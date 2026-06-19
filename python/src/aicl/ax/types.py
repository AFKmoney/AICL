"""Type inference for the AICL-Action (AX) sub-language.

AX is dynamically typed, but statically-typed targets (Rust, Go) need to know
each parameter's shape at codegen time. This module walks an AX AST and infers
a coarse type for a given set of names.

Inference rules (conservative — only types we can prove):
  - A name used as an index target (x[i]) or with a method like .append/.len
    is an ARRAY.
  - A name compared with / assigned from integer arithmetic is INT.
  - Otherwise ANY (emitter picks a default).

Usage:
    infer_param_types(stmts, param_names) -> Dict[str, str]
    # returns {"array": "ARRAY", "low": "INT", ...}
"""

from __future__ import annotations
from typing import Dict, List, Set

from . import ast as A


def _walk_expr(e: A.Expr, arrays: Set[str], ints: Set[str]) -> None:
    """Mark names as arrays/ints based on how they're used in ``e``."""
    if isinstance(e, A.Name):
        return  # bare name alone doesn't tell us the type
    if isinstance(e, A.Index):
        # e.target is indexed → it's an array (if it's a Name)
        if isinstance(e.target, A.Name):
            arrays.add(e.target.name)
        # the index expression itself is int-ish
        _walk_expr(e.index, arrays, ints)
        return
    if isinstance(e, A.Attr):
        # x.method or x.field — x is an object/array
        if isinstance(e.target, A.Name):
            # .append/.pop etc. strongly imply array; .length is JS-specific
            if e.attr in ("append", "pop", "extend", "insert", "remove", "sort"):
                arrays.add(e.target.name)
        _walk_expr(e.target, arrays, ints)
        return
    if isinstance(e, A.MethodCall):
        # target.method(args)
        if isinstance(e.target, A.Name) and e.method in ("append", "pop", "extend", "insert", "remove", "sort"):
            arrays.add(e.target.name)
        _walk_expr(e.target, arrays, ints)
        for a in e.args:
            _walk_expr(a, arrays, ints)
        return
    if isinstance(e, A.Call):
        # len(x) → x is array; abs(x), max(x,...) → x is int
        if e.func == "len" and e.args and isinstance(e.args[0], A.Name):
            arrays.add(e.args[0].name)
        for a in e.args:
            _walk_expr(a, arrays, ints)
        return
    if isinstance(e, A.BinOp):
        _walk_expr(e.left, arrays, ints)
        _walk_expr(e.right, arrays, ints)
        return
    if isinstance(e, A.UnaryOp):
        _walk_expr(e.operand, arrays, ints)
        return
    if isinstance(e, A.ListLit):
        for el in e.elements:
            _walk_expr(el, arrays, ints)
        return
    # literals (IntLit, FloatLit, StrLit, BoolLit, NoneLit) carry no name info


def _walk_stmts(stmts: List[A.Stmt], arrays: Set[str], ints: Set[str]) -> None:
    for s in stmts:
        _walk_stmt(s, arrays, ints)


def _walk_stmt(s: A.Stmt, arrays: Set[str], ints: Set[str]) -> None:
    if isinstance(s, A.Assign):
        # if assigning a ListLit to a name, that name is an array
        if isinstance(s.target, A.Name) and isinstance(s.value, A.ListLit):
            arrays.add(s.target.name)
        _walk_expr(s.target, arrays, ints)
        _walk_expr(s.value, arrays, ints)
        return
    if isinstance(s, A.AugAssign):
        if isinstance(s.target, A.Name):
            ints.add(s.target.name)  # += on a name implies numeric
        _walk_expr(s.target, arrays, ints)
        _walk_expr(s.value, arrays, ints)
        return
    if isinstance(s, A.ExprStmt):
        _walk_expr(s.expr, arrays, ints)
        return
    if isinstance(s, (A.Return,)):
        if s.value is not None:
            _walk_expr(s.value, arrays, ints)
        return
    if isinstance(s, A.SwapStmt):
        for e in s.swap.left + s.swap.right:
            _walk_expr(e, arrays, ints)
        return
    if isinstance(s, A.If):
        for cond, body in s.branches:
            _walk_expr(cond, arrays, ints)
            _walk_stmts(body, arrays, ints)
        _walk_stmts(s.orelse, arrays, ints)
        return
    if isinstance(s, A.While):
        _walk_expr(s.cond, arrays, ints)
        _walk_stmts(s.body, arrays, ints)
        return
    if isinstance(s, A.For):
        # loop variable is iterable element → often int for range loops
        _walk_expr(s.iterable, arrays, ints)
        _walk_stmts(s.body, arrays, ints)
        return
    # Pass, Break, Continue — nothing to infer


def infer_param_types(stmts: List[A.Stmt], param_names: List[str]) -> Dict[str, str]:
    """Infer a coarse type tag for each parameter name.

    Returns a dict mapping each name to one of:
        "ARRAY" — used with indexing, len(), or list methods
        "INT"   — used in arithmetic / augmented assignment
        "ANY"   — no evidence (emitter chooses a default)
    """
    arrays: Set[str] = set()
    ints: Set[str] = set()
    _walk_stmts(stmts, arrays, ints)
    result: Dict[str, str] = {}
    for name in param_names:
        if name in arrays:
            result[name] = "ARRAY"
        elif name in ints:
            result[name] = "INT"
        else:
            result[name] = "ANY"
    return result
