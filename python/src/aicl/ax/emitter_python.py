"""Python emitter for the AICL-Action (AX) sub-language.

Walks an AX AST (from ``parser.parse``) and renders it as Python source text.
AX is deliberately a subset of Python, so most nodes map almost 1:1; this
emitter's job is mostly indentation and string escaping. Because the output
is meant to be embedded inside a generated method body, callers pass the
starting indentation level.

The only AX construct with no direct Python equivalent is Swap (a, b = b, a),
which Python supports natively — so it maps to a tuple assignment.
"""

from __future__ import annotations
from typing import List

from . import ast as A
from .ast import (
    Assign, AugAssign, BinOp, BoolLit, Break, Call, Continue, ExprStmt,
    FloatLit, For, If, Index, Attr, IntLit, ListLit, MethodCall, Name,
    NoneLit, Pass, Return, StrLit, Stmt, Swap, SwapStmt, UnaryOp, While,
)


def _emit_expr(e: A.Expr) -> str:
    """Render a single AX expression as a Python expression string."""
    if isinstance(e, IntLit):
        return str(e.value)
    if isinstance(e, FloatLit):
        return repr(e.value)
    if isinstance(e, BoolLit):
        return "True" if e.value else "False"
    if isinstance(e, NoneLit):
        return "None"
    if isinstance(e, StrLit):
        return '"' + e.value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(e, Name):
        return e.name
    if isinstance(e, ListLit):
        return "[" + ", ".join(_emit_expr(x) for x in e.elements) + "]"
    if isinstance(e, BinOp):
        return f"({_emit_expr(e.left)} {e.op} {_emit_expr(e.right)})"
    if isinstance(e, UnaryOp):
        if e.op == "not":
            return f"(not {_emit_expr(e.operand)})"
        return f"(-{_emit_expr(e.operand)})"
    if isinstance(e, Index):
        return f"{_emit_expr(e.target)}[{_emit_expr(e.index)}]"
    if isinstance(e, Attr):
        return f"{_emit_expr(e.target)}.{e.attr}"
    if isinstance(e, Call):
        args = ", ".join(_emit_expr(a) for a in e.args)
        return f"{e.func}({args})"
    if isinstance(e, MethodCall):
        args = ", ".join(_emit_expr(a) for a in e.args)
        return f"{_emit_expr(e.target)}.{e.method}({args})"
    raise TypeError(f"cannot emit expression node {type(e).__name__}")


def _emit_stmt(s: Stmt, indent: int) -> List[str]:
    """Render one statement as a list of source lines (already indented)."""
    pad = "    " * indent

    if isinstance(s, Pass):
        return [f"{pad}pass"]
    if isinstance(s, Break):
        return [f"{pad}break"]
    if isinstance(s, Continue):
        return [f"{pad}continue"]
    if isinstance(s, Return):
        if s.value is None:
            return [f"{pad}return"]
        return [f"{pad}return {_emit_expr(s.value)}"]
    if isinstance(s, ExprStmt):
        return [f"{pad}{_emit_expr(s.expr)}"]
    if isinstance(s, Assign):
        return [f"{pad}{_emit_expr(s.target)} = {_emit_expr(s.value)}"]
    if isinstance(s, AugAssign):
        return [f"{pad}{_emit_expr(s.target)} {s.op} {_emit_expr(s.value)}"]
    if isinstance(s, SwapStmt):
        left = ", ".join(_emit_expr(x) for x in s.swap.left)
        right = ", ".join(_emit_expr(x) for x in s.swap.right)
        return [f"{pad}{left} = {right}"]
    if isinstance(s, If):
        lines: List[str] = []
        first = True
        for cond, body in s.branches:
            kw = "if" if first else "elif"
            lines.append(f"{pad}{kw} {_emit_expr(cond)}:")
            lines.extend(_emit_block(body, indent + 1))
            first = False
        if s.orelse:
            lines.append(f"{pad}else:")
            lines.extend(_emit_block(s.orelse, indent + 1))
        return lines
    if isinstance(s, While):
        lines = [f"{pad}while {_emit_expr(s.cond)}:"]
        lines.extend(_emit_block(s.body, indent + 1))
        return lines
    if isinstance(s, For):
        lines = [f"{pad}for {s.var} in {_emit_expr(s.iterable)}:"]
        lines.extend(_emit_block(s.body, indent + 1))
        return lines
    raise TypeError(f"cannot emit statement node {type(s).__name__}")


def _emit_block(stmts: List[Stmt], indent: int) -> List[str]:
    """Render a nested block. An empty block becomes a single 'pass' line."""
    if not stmts:
        return ["    " * indent + "pass"]
    lines: List[str] = []
    for s in stmts:
        lines.extend(_emit_stmt(s, indent))
    return lines


def emit_python(stmts: List[Stmt], indent: int = 1) -> str:
    """Render an AX statement list as Python source at the given indent level.

    ``indent=1`` means the code is emitted one level deep (4 spaces), which is
    the right default for code placed inside a method body.
    """
    return "\n".join(_emit_block(stmts, indent))
