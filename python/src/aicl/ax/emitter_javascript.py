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
    FloatLit, For, If, Index, Attr, IntLit, ListLit, MethodCall, Name,
    NoneLit, Pass, Return, StrLit, Stmt, Swap, SwapStmt, UnaryOp, While,
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
        if isinstance(e, BinOp):
            return self._binop(e)
        if isinstance(e, UnaryOp):
            if e.op == "not":
                return f"(!{self.emit(e.operand)})"
            return f"(-{self.emit(e.operand)})"
        if isinstance(e, Index):
            return f"{self.emit(e.target)}[{self.emit(e.index)}]"
        if isinstance(e, Attr):
            return f"{self.emit(e.target)}.{e.attr}"
        if isinstance(e, Call):
            return self.emit_call(e)
        if isinstance(e, MethodCall):
            args = ", ".join(self.emit(a) for a in e.args)
            return f"{self.emit(e.target)}.{e.method}({args})"
        raise TypeError(f"cannot emit JS expression node {type(e).__name__}")

    def emit_call(self, e: Call) -> str:
        """Translate Python builtins to their JS equivalents.

        ``len(x)`` → ``x.length``; ``abs(x)`` → ``Math.abs(x)``; ``max/min``
        stay as ``Math.max/min``. User-defined functions pass through unchanged.
        """
        args = [self.emit(a) for a in e.args]
        if e.func == "len" and len(args) == 1:
            return f"{args[0]}.length"
        if e.func == "abs" and len(args) == 1:
            return f"Math.abs({args[0]})"
        if e.func in ("max", "min") and len(args) >= 1:
            return f"Math.{e.func}({', '.join(args)})"
        return f"{e.func}({', '.join(args)})"

    def _binop(self, e: BinOp) -> str:
        L = self.emit(e.left)
        R = self.emit(e.right)
        # boolean operators
        if e.op == "and":
            return f"({L} && {R})"
        if e.op == "or":
            return f"({L} || {R})"
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
