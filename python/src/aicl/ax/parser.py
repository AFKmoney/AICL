"""Recursive-descent parser for the AICL-Action (AX) sub-language.

Consumes the token stream from ``lexer.tokenize`` and produces a list of
``ast.Stmt`` (the top-level body of an Action block).

Grammar (see docs/superpowers/specs/2026-06-18-aicl-turing-complete-design.md):

    action    ::= stmt+
    stmt      ::= 'if' expr block ('elif' expr block)* ('else' block)?
                | 'while' expr block
                | 'for' name 'in' expr block
                | 'return' expr?
                | 'break' | 'continue' | 'pass'
                | swap_or_assign | expr_stmt
    block     ::= NEWLINE INDENT stmt+ DEDENT
    expr      ::= or_expr
    or_expr   ::= and_expr ('or' and_expr)*
    and_expr  ::= not_expr ('and' not_expr)*
    not_expr  ::= 'not' not_expr | comparison
    comparison::= arith (comp_op arith)*
    arith     ::= term (('+' | '-') term)*
    term      ::= factor (('*' | '/' | '//' | '%') factor)*
    factor    ::= '-' factor | power
    power     ::= atom ('**' factor)?
    atom      ::= literal | name | '(' expr ')' | '[' list ']' | call | index | attr

A 'swap_or_assign' recognizes the special form ``a, b = b, a`` (parsed as a
SwapStmt). Plain ``target = expr`` is an Assign; ``target += expr`` an AugAssign.
"""

from __future__ import annotations
from typing import List, Optional

from . import ast as A
from .ast import (
    Assign, AugAssign, BoolLit, Break, Call, Continue, ExprStmt, FloatLit,
    For, If, Index, Attr, IntLit, ListLit, DictLit, SetLit, Slice, MethodCall,
    Name, NoneLit, Pass, Return, StrLit, Stmt, Swap, SwapStmt, UnaryOp, BinOp,
    While, ARITH_OPS, COMPARE_OPS, LOGIC_OPS, AUG_OPS,
)
from .lexer import tokenize, Token, AXSyntaxError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.pos = 0

    # -- token helpers -------------------------------------------------------

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        return self.toks[idx] if idx < len(self.toks) else self.toks[-1]

    def advance(self) -> Token:
        t = self.peek()
        if self.pos < len(self.toks) - 1:
            self.pos += 1
        return t

    def at_end(self) -> bool:
        return self.peek().kind == "EOF"

    def check(self, kind: str, value: Optional[str] = None) -> bool:
        t = self.peek()
        if t.kind != kind:
            return False
        return value is None or t.value == value

    def check_op(self, *values: str) -> bool:
        t = self.peek()
        return t.kind == "OP" and t.value in values

    def check_name(self, *values: str) -> bool:
        t = self.peek()
        return t.kind == "NAME" and t.value in values

    def expect(self, kind: str, value: Optional[str] = None) -> Token:
        t = self.peek()
        if t.kind != kind or (value is not None and t.value != value):
            expected = f"{kind} {value!r}" if value else kind
            raise AXSyntaxError(
                f"line {t.line}: expected {expected} but got {t.kind} {t.value!r}"
            )
        return self.advance()

    def eat_newlines(self) -> None:
        while self.check("NEWLINE"):
            self.advance()

    # -- entry point ---------------------------------------------------------

    def parse_program(self) -> List[Stmt]:
        """Parse the whole Action body into a statement list."""
        self.eat_newlines()
        stmts: List[Stmt] = []
        while not self.at_end():
            stmts.append(self.parse_stmt())
            self.eat_newlines()
        return stmts

    # -- statements ----------------------------------------------------------

    def parse_block(self) -> List[Stmt]:
        """Parse an indented block: NEWLINE INDENT stmt+ DEDENT."""
        self.expect("NEWLINE")
        self.expect("INDENT")
        stmts: List[Stmt] = []
        self.eat_newlines()
        while not self.check("DEDENT") and not self.at_end():
            stmts.append(self.parse_stmt())
            self.eat_newlines()
        if not self.check("DEDENT"):
            raise AXSyntaxError(f"line {self.peek().line}: expected DEDENT at end of block")
        self.expect("DEDENT")
        return stmts

    def parse_stmt(self) -> Stmt:
        t = self.peek()

        if t.kind == "NAME":
            v = t.value
            if v == "if":
                return self.parse_if()
            if v == "while":
                return self.parse_while()
            if v == "for":
                return self.parse_for()
            if v == "return":
                self.advance()
                if self.check("NEWLINE"):
                    self.advance()
                    return Return(None)
                val = self.parse_expr()
                self.expect("NEWLINE")
                return Return(val)
            if v == "break":
                self.advance(); self.expect("NEWLINE"); return Break()
            if v == "continue":
                self.advance(); self.expect("NEWLINE"); return Continue()
            if v == "pass":
                self.advance(); self.expect("NEWLINE"); return Pass()

        # assignment / augmented assignment / swap / expression statement
        return self.parse_simple_stmt()

    def parse_if(self) -> If:
        self.expect("NAME", "if")
        cond = self.parse_expr()
        self.expect("OP", ":")
        body = self.parse_block()
        branches = [(cond, body)]
        orelse: List[Stmt] = []

        while self.check_name("elif"):
            self.advance()
            c = self.parse_expr()
            self.expect("OP", ":")
            b = self.parse_block()
            branches.append((c, b))

        if self.check_name("else"):
            self.advance()
            self.expect("OP", ":")
            orelse = self.parse_block()

        return If(branches=branches, orelse=orelse)

    def parse_while(self) -> While:
        self.expect("NAME", "while")
        cond = self.parse_expr()
        self.expect("OP", ":")
        body = self.parse_block()
        return While(cond=cond, body=body)

    def parse_for(self) -> For:
        self.expect("NAME", "for")
        var_tok = self.expect("NAME")
        if var_tok.value in {"in", "if", "while", "for", "return"}:
            raise AXSyntaxError(f"line {var_tok.line}: '{var_tok.value}' is a keyword, not a loop variable")
        self.expect("NAME", "in")
        iterable = self.parse_expr()
        self.expect("OP", ":")
        body = self.parse_block()
        return For(var=var_tok.value, iterable=iterable, body=body)

    def parse_simple_stmt(self) -> Stmt:
        """Parse an assignment / swap / augmented-assign / expression statement."""
        # First, try to detect a swap: target_list '=' target_list where both
        # sides have commas (e.g. a, b = b, a). We do this by looking ahead:
        # parse a primary expr; if followed by ',', we may have a target list.
        start_pos = self.pos
        first = self.parse_expr()

        if self.check_op(","):
            # potential swap: collect left-hand targets
            left = [first]
            while self.check_op(","):
                self.advance()
                if self.check_op("="):
                    # trailing comma like "a, = ..." — treat as single
                    break
                left.append(self.parse_expr())
            if self.check_op("="):
                self.advance()
                # right side: also comma-separated
                right = [self.parse_expr()]
                while self.check_op(","):
                    self.advance()
                    right.append(self.parse_expr())
                self.expect("NEWLINE")
                return SwapStmt(Swap(left=left, right=right))
            else:
                # was not an assignment; we consumed commas for nothing.
                # Reset and fall through to expression statement handling.
                self.pos = start_pos
                first = self.parse_expr()

        if self.check_op("="):
            self.advance()
            value = self.parse_expr()
            self.expect("NEWLINE")
            return Assign(target=first, value=value)

        for op in AUG_OPS:
            if self.check_op(op):
                self.advance()
                value = self.parse_expr()
                self.expect("NEWLINE")
                return AugAssign(target=first, op=op, value=value)

        # bare expression (e.g. a function call as a statement)
        self.expect("NEWLINE")
        return ExprStmt(first)

    # -- expressions ---------------------------------------------------------

    def parse_expr(self) -> A.Expr:
        return self.parse_or()

    def parse_or(self) -> A.Expr:
        left = self.parse_and()
        while self.check_name("or"):
            self.advance()
            right = self.parse_and()
            left = BinOp(op="or", left=left, right=right)
        return left

    def parse_and(self) -> A.Expr:
        left = self.parse_not()
        while self.check_name("and"):
            self.advance()
            right = self.parse_not()
            left = BinOp(op="and", left=left, right=right)
        return left

    def parse_not(self) -> A.Expr:
        if self.check_name("not"):
            self.advance()
            return UnaryOp(op="not", operand=self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> A.Expr:
        left = self.parse_arith()
        while True:
            # Check for "in", "not in", "is", "is not" keyword operators
            if self.check_name("in"):
                self.advance()
                right = self.parse_arith()
                left = BinOp(op="in", left=left, right=right)
                continue
            if self.check_name("not") and self.peek(1).kind == "NAME" and self.peek(1).value == "in":
                self.advance()  # not
                self.advance()  # in
                right = self.parse_arith()
                left = BinOp(op="not_in", left=left, right=right)
                continue
            if self.check_name("is"):
                self.advance()
                if self.check_name("not"):
                    self.advance()
                    right = self.parse_arith()
                    left = BinOp(op="is_not", left=left, right=right)
                else:
                    right = self.parse_arith()
                    left = BinOp(op="is", left=left, right=right)
                continue
            # Check for symbolic comparison operators
            matched = None
            for op in ("==", "!=", "<=", ">=", "<", ">"):
                if self.check_op(op):
                    matched = op
                    break
            if matched is None:
                break
            self.advance()
            right = self.parse_arith()
            left = BinOp(op=matched, left=left, right=right)
        return left

    def parse_arith(self) -> A.Expr:
        left = self.parse_term()
        while self.check_op("+", "-"):
            op = self.advance().value
            right = self.parse_term()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_term(self) -> A.Expr:
        left = self.parse_factor()
        while self.check_op("*", "/", "//", "%"):
            op = self.advance().value
            right = self.parse_factor()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_factor(self) -> A.Expr:
        if self.check_op("-"):
            self.advance()
            return UnaryOp(op="-", operand=self.parse_factor())
        return self.parse_power()

    def parse_power(self) -> A.Expr:
        base = self.parse_atom()
        if self.check_op("**"):
            self.advance()
            exp = self.parse_factor()  # right-assoc
            return BinOp(op="**", left=base, right=exp)
        return base

    def parse_atom(self) -> A.Expr:
        t = self.peek()

        if t.kind == "INT":
            self.advance()
            return self.parse_postfix(IntLit(int(t.value)))
        if t.kind == "FLOAT":
            self.advance()
            return self.parse_postfix(FloatLit(float(t.value)))
        if t.kind == "STRING":
            self.advance()
            return self.parse_postfix(StrLit(t.value))

        if t.kind == "NAME":
            v = t.value
            if v == "true":
                self.advance(); return self.parse_postfix(BoolLit(True))
            if v == "false":
                self.advance(); return self.parse_postfix(BoolLit(False))
            if v == "none":
                self.advance(); return self.parse_postfix(NoneLit())
            # name, possibly followed by call / index / attr
            self.advance()
            expr: A.Expr = Name(name=v)
            return self.parse_postfix(expr)

        if self.check_op("("):
            self.advance()
            inner = self.parse_expr()
            self.expect("OP", ")")
            return self.parse_postfix(inner)

        if self.check_op("["):
            self.advance()
            elements: List[A.Expr] = []
            if not self.check_op("]"):
                elements.append(self.parse_expr())
                while self.check_op(","):
                    self.advance()
                    if self.check_op("]"):
                        break
                    elements.append(self.parse_expr())
            self.expect("OP", "]")
            return self.parse_postfix(ListLit(elements=elements))

        # Dict literal {key: value, ...} or Set literal {a, b, ...}
        if self.check_op("{"):
            self.advance()
            # Empty braces → empty dict
            if self.check_op("}"):
                self.advance()
                return self.parse_postfix(DictLit(pairs=[]))
            # Parse first element to decide dict vs set
            first = self.parse_expr()
            if self.check_op(":"):
                # Dict literal
                self.advance()
                val = self.parse_expr()
                pairs: List[tuple] = [(first, val)]
                while self.check_op(","):
                    self.advance()
                    if self.check_op("}"):
                        break
                    k = self.parse_expr()
                    self.expect("OP", ":")
                    v = self.parse_expr()
                    pairs.append((k, v))
                self.expect("OP", "}")
                return self.parse_postfix(DictLit(pairs=pairs))
            else:
                # Set literal (or just a braced expression)
                elems = [first]
                while self.check_op(","):
                    self.advance()
                    if self.check_op("}"):
                        break
                    elems.append(self.parse_expr())
                self.expect("OP", "}")
                return self.parse_postfix(SetLit(elements=elems))

        raise AXSyntaxError(f"line {t.line}: unexpected token {t.kind} {t.value!r}")

    def parse_postfix(self, base: A.Expr) -> A.Expr:
        """Parse trailing [index], [start:stop:step] slice, .attr, and (call) suffixes."""
        expr = base
        while True:
            if self.check_op("["):
                self.advance()
                # Check for slice syntax: [start:stop] or [start:stop:step] or [:stop] etc.
                start: Optional[A.Expr] = None
                stop: Optional[A.Expr] = None
                step: Optional[A.Expr] = None
                is_slice = False

                if not self.check_op(":"):
                    start = self.parse_expr()
                # Check if this is a slice (has colon)
                if self.check_op(":"):
                    is_slice = True
                    self.advance()  # consume ':'
                    if not self.check_op(":") and not self.check_op("]"):
                        stop = self.parse_expr()
                    if self.check_op(":"):
                        self.advance()  # consume second ':'
                        if not self.check_op("]"):
                            step = self.parse_expr()
                self.expect("OP", "]")
                if is_slice:
                    expr = Slice(target=expr, start=start, stop=stop, step=step)
                else:
                    expr = Index(target=expr, index=start if start is not None else IntLit(0))
            elif self.check_op("."):
                self.advance()
                attr_tok = self.expect("NAME")
                expr = Attr(target=expr, attr=attr_tok.value)
            elif self.check_op("("):
                # function call (base is a Name) or method call (base is an Attr)
                self.advance()  # consume '('
                args: List[A.Expr] = []
                if not self.check_op(")"):
                    args.append(self.parse_expr())
                    while self.check_op(","):
                        self.advance()
                        args.append(self.parse_expr())
                self.expect("OP", ")")
                if isinstance(expr, Name):
                    expr = Call(func=expr.name, args=args)
                elif isinstance(expr, Attr):
                    expr = MethodCall(target=expr.target, method=expr.attr, args=args)
                else:
                    raise AXSyntaxError(
                        f"line {self.peek().line}: cannot call a non-function expression"
                    )
            else:
                break
        return expr


def parse(source: str) -> List[Stmt]:
    """Tokenize + parse an AX source string into a list of statements.

    Raises AXSyntaxError on any lexical or grammatical error.
    """
    tokens = tokenize(source)
    return Parser(tokens).parse_program()
