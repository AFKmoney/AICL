"""AST node definitions for the AICL-Action (AX) sub-language.

AX is a deliberately small, strictly-typed-by-grammar subset of Python-like
syntax used inside Behavior ``Action:`` sections. It is Turing-complete:
if/elif/else, while, for-in, recursion (via function calls), arithmetic &
boolean expressions, list literals, indexing, and attribute access.

Every node is a plain dataclass so the emitters (python/rust/js/go) can walk
the tree with isinstance checks or a small visitor.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Union


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class Expr:
    """Base class for all expressions."""


@dataclass
class IntLit(Expr):
    value: int


@dataclass
class FloatLit(Expr):
    value: float


@dataclass
class StrLit(Expr):
    value: str


@dataclass
class BoolLit(Expr):
    value: bool


@dataclass
class NoneLit(Expr):
    pass


@dataclass
class Name(Expr):
    name: str


@dataclass
class ListLit(Expr):
    elements: List[Expr]


@dataclass
class BinOp(Expr):
    op: str          # one of: + - * / // % ** == != < <= > >= and or
    left: Expr
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str          # one of: - not
    operand: Expr


@dataclass
class Index(Expr):
    target: Expr
    index: Expr


@dataclass
class Attr(Expr):
    target: Expr
    attr: str


@dataclass
class Call(Expr):
    func: str
    args: List[Expr]


@dataclass
class MethodCall(Expr):
    """Method call on an object: obj.method(args)."""
    target: Expr
    method: str
    args: List[Expr]


@dataclass
class Swap(Expr):
    """Tuple swap: a, b = b, a  — represented at statement level too."""
    left: List[Expr]
    right: List[Expr]


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class Stmt:
    """Base class for all statements."""


@dataclass
class Assign(Stmt):
    target: Expr       # Name, Index, or Attr
    value: Expr


@dataclass
class AugAssign(Stmt):
    target: Expr
    op: str            # += -= *= /= //= %= **=
    value: Expr


@dataclass
class SwapStmt(Stmt):
    swap: Swap


@dataclass
class If(Stmt):
    branches: List[tuple]   # list of (condition: Expr, body: List[Stmt])
    orelse: List[Stmt]      # else body (may be empty)


@dataclass
class While(Stmt):
    cond: Expr
    body: List[Stmt]


@dataclass
class For(Stmt):
    var: str
    iterable: Expr
    body: List[Stmt]


@dataclass
class Return(Stmt):
    value: Optional[Expr]


@dataclass
class ExprStmt(Stmt):
    """A bare expression used as a statement (e.g. a function call)."""
    expr: Expr


@dataclass
class Break(Stmt):
    pass


@dataclass
class Continue(Stmt):
    pass


@dataclass
class Pass(Stmt):
    pass


# Convenience: the supported binary operators, grouped so emitters and the
# checker can validate them.
ARITH_OPS = {"+", "-", "*", "/", "//", "%", "**"}
COMPARE_OPS = {"==", "!=", "<", "<=", ">", ">="}
LOGIC_OPS = {"and", "or"}
AUG_OPS = {"+=", "-=", "*=", "/=", "//=", "%=", "**="}
