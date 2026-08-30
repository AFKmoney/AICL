"""JavaScript emitter for the AICL-Action (AX) sub-language.

Walks the same AX AST as ``emitter_python`` but renders JavaScript (ES2015+).
AX is designed as a common subset, so most nodes map cleanly; the non-trivial
translations are:

  - ``range(a, b)`` / ``range(a, b, c)``  →  C-style ``for (let i = a; i < b; i += c)``
  - ``a, b = b, a`` (swap)                →  ``[a, b] = [b, a]`` (destructuring)
  - ``True / False / None``               →  ``true / false / null``
  - ``and / or / not``                    →  ``&& / || / !``
  - ``//`` (floor div)                    →  ``Math.trunc(a / b)``
  - ``**`` (power)                        →  ``Math.pow(a, b)``

Output is plain ES2015+ with no imports required, suitable for Node or browser.
Variables are declared with ``let`` on first assignment; AX has no declarations
so the emitter tracks which names have been seen in the current scope.
"""

from __future__ import annotations
from typing import List, Set

from . import ast as A
from .ast import (
    Assign, AugAssign, BinOp, BoolLit, Break, Call, Continue, ExprStmt,
    FloatLit, For, If, Index, Attr, IntLit, ListLit, DictLit, SetLit, Slice,
    MethodCall, Name, NoneLit, Pass, Return, StrLit, Stmt, Swap, SwapStmt,
    UnaryOp, While,
)

# Keywords in JS that must not be used as bare identifiers (we don't rename,
# but we avoid emitting them as `let` declarations conflicting with globals).
_JS_RESERVED = {"let", "const", "var", "function", "return", "if", "else",
                "for", "while", "break", "continue", "true", "false", "null",
                "undefined", "new", "delete", "typeof", "instanceof", "in",
                "of", "class", "extends", "super", "this", "switch", "case",
                "default", "try", "catch", "finally", "throw"}


class _JSExprEmitter:
    """Renders AX expressions as JS expression strings.

    Tracks names seen so far so the statement emitter can decide between
    `let` (first assignment) and plain reassignment.
    """

    def __init__(self):
        self.seen: Set[str] = set()

    def emit(self, e: A.Expr) -> str:
        if isinstance(e, IntLit):
            return str(e.value)
        if isinstance(e, FloatLit):
            return repr(e.value)
        if isinstance(e, BoolLit):
            return "true" if e.value else "false"
        if isinstance(e, NoneLit):
            return "null"
        if isinstance(e, StrLit):
            return '"' + e.value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if isinstance(e, Name):
            return e.name
        if isinstance(e, ListLit):
            return "[" + ", ".join(self.emit(x) for x in e.elements) + "]"
        if isinstance(e, DictLit):
            # Use plain JS object for dict (supports [] indexing natively)
            pairs = ", ".join(f"[{self.emit(k)}, {self.emit(v)}]" for k, v in e.pairs)
            return "Object.fromEntries([" + pairs + "])"
        if isinstance(e, SetLit):
            inner = ", ".join(self.emit(x) for x in e.elements)
            return f"new Set([{inner}])"
        if isinstance(e, Slice):
            start = self.emit(e.start) if e.start is not None else "0"
            if e.stop is not None:
                stop = self.emit(e.stop)
            else:
                stop = "undefined"
            if e.step is not None:
                # JS doesn't natively support step; use a filter approach
                step = self.emit(e.step)
                return f"{self.emit(e.target)}.filter((_, _i) => _i >= {start} && (false || {stop} === undefined || _i < {stop}) && (_i - {start}) % {step} === 0)"
            return f"{self.emit(e.target)}.slice({start}, {stop})"
        if isinstance(e, BinOp):
            return self._binop(e)
        if isinstance(e, UnaryOp):
            if e.op == "not":
                return f"(!{self.emit(e.operand)})"
            return f"(-{self.emit(e.operand)})"
        if isinstance(e, Index):
            # For Map objects, use .get(); for arrays/strings, use []
            return f"{self.emit(e.target)}[{self.emit(e.index)}]"
        if isinstance(e, Attr):
            return f"{self.emit(e.target)}.{e.attr}"
        if isinstance(e, Call):
            return self.emit_call(e)
        if isinstance(e, MethodCall):
            return self._method_call(e)
        raise TypeError(f"cannot emit JS expression node {type(e).__name__}")

    def emit_call(self, e: Call) -> str:
        """Translate Python builtins to their JS equivalents."""
        args = [self.emit(a) for a in e.args]

        # I/O
        if e.func == "print":
            return f"console.log({', '.join(args)})"
        if e.func == "input":
            # Synchronous readline for Node.js
            if args:
                return f"(process.stdout.write({args[0]}), require('readline-sync').question(''))"
            return "require('readline-sync').question('')"
        if e.func == "read_file":
            return f"require('fs').readFileSync({args[0]}, 'utf8')"
        if e.func == "write_file":
            return f"require('fs').writeFileSync({args[0]}, {args[1]}, 'utf8')"

        # Type conversion
        if e.func == "int" and len(args) == 1:
            return f"parseInt({args[0]}, 10)"
        if e.func == "str" and len(args) == 1:
            return f"String({args[0]})"
        if e.func == "float" and len(args) == 1:
            return f"parseFloat({args[0]})"
        if e.func == "bool" and len(args) == 1:
            return f"Boolean({args[0]})"

        # Collections
        if e.func == "len" and len(args) == 1:
            return f"{args[0]}.length"
        if e.func == "abs" and len(args) == 1:
            return f"Math.abs({args[0]})"
        if e.func in ("max", "min") and len(args) >= 1:
            return f"Math.{e.func}({', '.join(args)})"
        if e.func == "sum" and len(args) == 1:
            return f"{args[0]}.reduce((a, b) => a + b, 0)"
        if e.func == "sorted" and len(args) == 1:
            return f"[...{args[0]}].sort((a, b) => a - b)"
        if e.func == "reversed" and len(args) == 1:
            return f"[...{args[0]}].reverse()"
        if e.func == "enumerate" and len(args) == 1:
            return f"{args[0]}.map((v, i) => [i, v])"
        if e.func == "zip" and len(args) == 2:
            return f"{args[0]}.map((v, i) => [v, {args[1]}[i]])"
        if e.func == "list" and len(args) == 1:
            return f"[...{args[0]}]"
        if e.func == "dict" and len(args) == 1:
            return f"new Map(Object.entries({args[0]}))"

        # String functions
        if e.func == "ord" and len(args) == 1:
            return f"{args[0]}.charCodeAt(0)"
        if e.func == "chr" and len(args) == 1:
            return f"String.fromCharCode({args[0]})"

        # Math
        if e.func == "sqrt" and len(args) == 1:
            return f"Math.sqrt({args[0]})"
        if e.func == "pow" and len(args) == 2:
            return f"Math.pow({args[0]}, {args[1]})"
        if e.func == "floor" and len(args) == 1:
            return f"Math.floor({args[0]})"
        if e.func == "ceil" and len(args) == 1:
            return f"Math.ceil({args[0]})"

        return f"{e.func}({', '.join(args)})"

    def _method_call(self, e: MethodCall) -> str:
        """Translate common Python methods to JS equivalents."""
        args = [self.emit(a) for a in e.args]
        target = self.emit(e.target)

        # String methods
        if e.method == "upper":
            return f"{target}.toUpperCase()"
        if e.method == "lower":
            return f"{target}.toLowerCase()"
        if e.method == "strip":
            return f"{target}.trim()"
        if e.method == "lstrip":
            return f"{target}.replace(/^\\s+/, '')"
        if e.method == "rstrip":
            return f"{target}.replace(/\\s+$/, '')"
        if e.method == "split":
            if args:
                return f"{target}.split({args[0]})"
            return f"{target}.split(/\\s+/)"
        if e.method == "join":
            return f"{args[0]}.join({target})"
        if e.method == "replace":
            return f"{target}.split({args[0]}).join({args[1]})"
        if e.method == "find":
            return f"{target}.indexOf({args[0]})"
        if e.method == "startswith":
            return f"{target}.startsWith({args[0]})"
        if e.method == "endswith":
            return f"{target}.endsWith({args[0]})"
        if e.method == "count":
            return f"{target}.split({args[0]}).length - 1"
        if e.method == "format":
            # Simple {0}, {1} format support
            return f"{target}.replace(/{{(\\d+)}}/g, (_, i) => args[parseInt(i)])"

        # List methods
        if e.method == "append":
            return f"{target}.push({args[0]})"
        if e.method == "pop":
            return f"{target}.pop()"
        if e.method == "insert":
            return f"{target}.splice({args[0]}, 0, {args[1]})"
        if e.method == "remove":
            return f"{target}.splice({target}.indexOf({args[0]}), 1)"
        if e.method == "sort":
            return f"{target}.sort((a, b) => a - b)"
        if e.method == "reverse":
            return f"{target}.reverse()"
        if e.method == "extend":
            return f"{target}.push(...{args[0]})"

        # Dict methods (for plain JS objects)
        if e.method == "get":
            if len(args) >= 2:
                return f"({target}[{args[0]}] !== undefined ? {target}[{args[0]}] : {args[1]})"
            return f"{target}[{args[0]}]"
        if e.method == "keys":
            return f"Object.keys({target})"
        if e.method == "values":
            return f"Object.values({target})"
        if e.method == "items":
            return f"Object.entries({target})"

        # Default: direct method call
        return f"{target}.{e.method}({', '.join(args)})"

    def _binop(self, e: BinOp) -> str:
        L = self.emit(e.left)
        R = self.emit(e.right)
        # boolean operators
        if e.op == "and":
            return f"({L} && {R})"
        if e.op == "or":
            return f"({L} || {R})"
        # membership operators
        if e.op == "in":
            return f"({R}.includes({L}))"
        if e.op == "not_in":
            return f"(!{R}.includes({L}))"
        # identity operators
        if e.op == "is":
            return f"({L} === {R})"
        if e.op == "is_not":
            return f"({L} !== {R})"
        # floor division → Math.trunc(a / b)
        if e.op == "//":
            return f"Math.trunc({L} / {R})"
        # power → Math.pow
        if e.op == "**":
            return f"Math.pow({L}, {R})"
        # modulo: JS % is fine for integers
        # equality/inequality/comparison map 1:1
        return f"({L} {e.op} {R})"


def _emit_block(stmts: List[Stmt], indent: int, expr_emit: _JSExprEmitter) -> List[str]:
    """Render a block of statements; empty block becomes a single comment."""
    if not stmts:
        return ["    " * indent + "/* no-op */"]
    lines: List[str] = []
    for s in stmts:
        lines.extend(_emit_stmt(s, indent, expr_emit))
    return lines


def _emit_stmt(s: Stmt, indent: int, expr_emit: _JSExprEmitter) -> List[str]:
    pad = "    " * indent

    if isinstance(s, Pass):
        return [f"{pad}/* pass */"]
    if isinstance(s, Break):
        return [f"{pad}break;"]
    if isinstance(s, Continue):
        return [f"{pad}continue;"]
    if isinstance(s, Return):
        if s.value is None:
            return [f"{pad}return;"]
        return [f"{pad}return {expr_emit.emit(s.value)};"]
    if isinstance(s, ExprStmt):
        return [f"{pad}{expr_emit.emit(s.expr)};"]
    if isinstance(s, SwapStmt):
        left = ", ".join(expr_emit.emit(x) for x in s.swap.left)
        right = ", ".join(expr_emit.emit(x) for x in s.swap.right)
        return [f"{pad}[{left}] = [{right}];"]
    if isinstance(s, Assign):
        return _emit_assign(s, indent, expr_emit)
    if isinstance(s, AugAssign):
        target = expr_emit.emit(s.target)
        return [f"{pad}{target} {s.op} {expr_emit.emit(s.value)};"]
    if isinstance(s, If):
        return _emit_if(s, indent, expr_emit)
    if isinstance(s, While):
        lines = [f"{pad}while ({expr_emit.emit(s.cond)}) {{"]
        lines.extend(_emit_block(s.body, indent + 1, expr_emit))
        lines.append(f"{pad}}}")
        return lines
    if isinstance(s, For):
        return _emit_for(s, indent, expr_emit)
    raise TypeError(f"cannot emit JS statement node {type(s).__name__}")


def _emit_assign(s: Assign, indent: int, expr_emit: _JSExprEmitter) -> List[str]:
    pad = "    " * indent
    # Track name introduction for `let` vs reassignment.
    if isinstance(s.target, Name):
        name = s.target.name
        rhs = expr_emit.emit(s.value)
        if name not in expr_emit.seen:
            expr_emit.seen.add(name)
            return [f"{pad}let {name} = {rhs};"]
        return [f"{pad}{name} = {rhs};"]
    # index / attribute assignment: no declaration needed
    target = expr_emit.emit(s.target)
    rhs = expr_emit.emit(s.value)
    return [f"{pad}{target} = {rhs};"]


def _emit_if(s: If, indent: int, expr_emit: _JSExprEmitter) -> List[str]:
    pad = "    " * indent
    lines: List[str] = []
    first = True
    for cond, body in s.branches:
        kw = "if" if first else "else if"
        lines.append(f"{pad}{kw} ({expr_emit.emit(cond)}) {{")
        lines.extend(_emit_block(body, indent + 1, expr_emit))
        lines.append(f"{pad}}}")
        first = False
    if s.orelse:
        # collapse trailing brace + else into one line for readability
        lines[-1] = f"{pad}}} else {{"
        lines.extend(_emit_block(s.orelse, indent + 1, expr_emit))
        lines.append(f"{pad}}}")
    return lines


def _emit_for(s: For, indent: int, expr_emit: _JSExprEmitter) -> List[str]:
    """Render an AX ``for x in iterable`` loop.

    AX iterables are almost always ``range(start, stop)`` or
    ``range(start, stop, step)``; those compile to C-style for loops. Any other
    iterable falls back to ``for...of``.
    """
    pad = "    " * indent
    var = s.var

    # Detect range(...) call
    if (isinstance(s.iterable, Call) and s.iterable.func == "range"):
        args = s.iterable.args
        if len(args) == 1:
            start, stop, step = "0", expr_emit.emit(args[0]), "1"
        elif len(args) == 2:
            start, stop, step = expr_emit.emit(args[0]), expr_emit.emit(args[1]), "1"
        else:
            start = expr_emit.emit(args[0])
            stop = expr_emit.emit(args[1])
            step = expr_emit.emit(args[2])
        lines = [f"{pad}for (let {var} = {start}; {var} < {stop}; {var} += {step}) {{"]
        lines.extend(_emit_block(s.body, indent + 1, expr_emit))
        lines.append(f"{pad}}}")
        return lines

    # Generic for...of fallback
    it = expr_emit.emit(s.iterable)
    lines = [f"{pad}for (let {var} of {it}) {{"]
    lines.extend(_emit_block(s.body, indent + 1, expr_emit))
    lines.append(f"{pad}}}")
    return lines


def emit_javascript(stmts: List[Stmt], indent: int = 1) -> str:
    """Render an AX statement list as JavaScript at the given indent level.

    ``indent=1`` produces code one level deep (4 spaces), matching the body of
    a generated method. Each call gets a fresh expression emitter so variable
    declaration tracking starts clean.
    """
    expr_emit = _JSExprEmitter()
    return "\n".join(_emit_block(stmts, indent, expr_emit))
