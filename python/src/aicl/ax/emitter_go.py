"""Go emitter for the AICL-Action (AX) sub-language.

Walks the same AX AST as the other emitters but renders Go. Go is statically
typed; like the Rust emitter this makes pragmatic choices:

  - Integer literals    -> int
  - Float literals      -> float64
  - Boolean expressions -> bool
  - List literals       -> []int
  - Bindings use        -> := on first assignment, = on reassignment

Translation rules for the non-obvious cases:
  - range(a, b)         -> for i := a; i < b; i++
  - range(a, b, c)      -> for i := a; i < b; i += c
  - a, b = b, a          -> capture rhs into temps first, then assign
                             (Go supports `a, b = b, a` natively for simple
                              names, but indexed swaps need temps)
  - True/False/None     -> true/false / 0  (Go has no generic nil for int)
  - and/or/not          -> &&/||/!
  - a // b              -> a / b  (int division truncates toward zero in Go)
  - a ** b              -> int(math.Pow(float64(a), float64(b)))
  - len(x)              -> len(x)
  - abs(x)              -> a math.Abs-based helper; for int, inline branch
  - array[j]            -> array[j]  (Go indexing needs int, AX int matches)

Note: Go does not allow unused variables or imports, so generated code must
be wrapped in a function that uses every declared name. The emitter does not
emit the wrapping func signature — callers provide it.
"""

from __future__ import annotations
from typing import List, Set

from . import ast as A
from .ast import (
    Assign, AugAssign, BinOp, BoolLit, Break, Call, Continue, ExprStmt,
    FloatLit, For, If, Index, Attr, IntLit, ListLit, MethodCall, Name,
    NoneLit, Pass, Return, StrLit, Stmt, Swap, SwapStmt, UnaryOp, While,
)


class _GoExprEmitter:
    def __init__(self):
        self.seen: Set[str] = set()
        self.swap_counter = 0

    def fresh_temp(self) -> str:
        self.swap_counter += 1
        return f"_axTmp{self.swap_counter}"

    def emit(self, e: A.Expr) -> str:
        if isinstance(e, IntLit):
            return str(e.value)
        if isinstance(e, FloatLit):
            return repr(e.value)
        if isinstance(e, BoolLit):
            return "true" if e.value else "false"
        if isinstance(e, NoneLit):
            # Go has no nil for int; represent absence as 0.
            return "0"
        if isinstance(e, StrLit):
            esc = e.value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{esc}"'
        if isinstance(e, Name):
            return e.name
        if isinstance(e, ListLit):
            inner = ", ".join(self.emit(x) for x in e.elements)
            return f"[]int{{{inner}}}"
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
            return self._call(e)
        if isinstance(e, MethodCall):
            args = ", ".join(self.emit(a) for a in e.args)
            return f"{self.emit(e.target)}.{e.method}({args})"
        raise TypeError(f"cannot emit Go expression node {type(e).__name__}")

    def _binop(self, e: BinOp) -> str:
        L = self.emit(e.left)
        R = self.emit(e.right)
        if e.op == "and":
            return f"({L} && {R})"
        if e.op == "or":
            return f"({L} || {R})"
        if e.op == "//":
            # Go int division truncates toward zero.
            return f"({L} / {R})"
        if e.op == "**":
            return f"int(math.Pow(float64({L}), float64({R})))"
        if e.op == "%":
            return f"({L} % {R})"
        return f"({L} {e.op} {R})"

    def _call(self, e: Call) -> str:
        args = [self.emit(a) for a in e.args]
        if e.func == "len" and len(args) == 1:
            return f"len({args[0]})"
        if e.func == "abs" and len(args) == 1:
            # no built-in abs for int in Go; inline.
            v = args[0]
            return f"(_absInt({v}))"
        if e.func in ("max", "min") and len(args) == 2:
            # Go 1.21+ has builtin max/min.
            return f"({e.func}({args[0]}, {args[1]}))"
        return f"{e.func}({', '.join(args)})"


def _emit_block(stmts: List[Stmt], indent: int, ex: _GoExprEmitter) -> List[str]:
    if not stmts:
        return ["    " * indent + "// no-op"]
    lines: List[str] = []
    for s in stmts:
        lines.extend(_emit_stmt(s, indent, ex))
    return lines


def _emit_stmt(s: Stmt, indent: int, ex: _GoExprEmitter) -> List[str]:
    pad = "    " * indent

    if isinstance(s, Pass):
        return [f"{pad}// pass"]
    if isinstance(s, Break):
        return [f"{pad}break"]
    if isinstance(s, Continue):
        return [f"{pad}continue"]
    if isinstance(s, Return):
        if s.value is None:
            return [f"{pad}return"]
        return [f"{pad}return {ex.emit(s.value)}"]
    if isinstance(s, ExprStmt):
        return [f"{pad}{ex.emit(s.expr)}"]
    if isinstance(s, SwapStmt):
        return _emit_swap(s, indent, ex)
    if isinstance(s, Assign):
        return _emit_assign(s, indent, ex)
    if isinstance(s, AugAssign):
        target = ex.emit(s.target)
        op = s.op[:-1]
        return [f"{pad}{target} {op}= {ex.emit(s.value)}"]
    if isinstance(s, If):
        return _emit_if(s, indent, ex)
    if isinstance(s, While):
        lines = [f"{pad}for {ex.emit(s.cond)} {{"]
        lines.extend(_emit_block(s.body, indent + 1, ex))
        lines.append(f"{pad}}}")
        return lines
    if isinstance(s, For):
        return _emit_for(s, indent, ex)
    raise TypeError(f"cannot emit Go statement node {type(s).__name__}")


def _emit_assign(s: Assign, indent: int, ex: _GoExprEmitter) -> List[str]:
    pad = "    " * indent
    if isinstance(s.target, Name):
        name = s.target.name
        rhs = ex.emit(s.value)
        if name not in ex.seen:
            ex.seen.add(name)
            return [f"{pad}{name} := {rhs}"]
        return [f"{pad}{name} = {rhs}"]
    if isinstance(s.target, Index):
        target = ex.emit(s.target.target)
        idx = ex.emit(s.target.index)
        return [f"{pad}{target}[{idx}] = {ex.emit(s.value)}"]
    target = ex.emit(s.target)
    return [f"{pad}{target} = {ex.emit(s.value)}"]


def _emit_swap(s: SwapStmt, indent: int, ex: _GoExprEmitter) -> List[str]:
    """Capture all rhs into temps first, then assign — correct for indexed swaps."""
    pad = "    " * indent
    lines: List[str] = []
    left = s.swap.left
    right = s.swap.right
    if len(left) != len(right):
        raise ValueError("swap sides must have equal length")
    # If every lvalue is a simple Name, Go's native swap is fine.
    if all(isinstance(lv, Name) and isinstance(rv, Name) for lv, rv in zip(left, right)):
        ls = ", ".join(ex.emit(lv) for lv in left)
        rs = ", ".join(ex.emit(rv) for rv in right)
        lines.append(f"{pad}{ls} = {rs}")
        return lines
    # Mixed/indexed: capture rhs, then assign.
    temps = [ex.fresh_temp() for _ in right]
    for t, rv in zip(temps, right):
        lines.append(f"{pad}{t} := {ex.emit(rv)}")
    for t, lv in zip(temps, left):
        lines.append(f"{pad}{_assign_target(lv, ex)} = {t}")
    return lines


def _assign_target(e: A.Expr, ex: _GoExprEmitter) -> str:
    if isinstance(e, Name):
        return e.name
    return ex.emit(e)


def _emit_if(s: If, indent: int, ex: _GoExprEmitter) -> List[str]:
    pad = "    " * indent
    lines: List[str] = []
    first = True
    for cond, body in s.branches:
        if first:
            lines.append(f"{pad}if {ex.emit(cond)} {{")
            first = False
        else:
            # Go requires `} else if {` on the SAME line — the `}` that closes
            # the previous block must be followed immediately by ` else if `.
            # So we rewrite the last `}` line we emitted.
            lines[-1] = f"{pad}}} else if {ex.emit(cond)} {{"
        lines.extend(_emit_block(body, indent + 1, ex))
        lines.append(f"{pad}}}")
    if s.orelse:
        lines[-1] = f"{pad}}} else {{"
        lines.extend(_emit_block(s.orelse, indent + 1, ex))
        lines.append(f"{pad}}}")
    return lines


def _emit_for(s: For, indent: int, ex: _GoExprEmitter) -> List[str]:
    pad = "    " * indent
    var = s.var

    if isinstance(s.iterable, Call) and s.iterable.func == "range":
        args = s.iterable.args
        if len(args) == 1:
            start, stop, step = "0", ex.emit(args[0]), None
        elif len(args) == 2:
            start, stop, step = ex.emit(args[0]), ex.emit(args[1]), None
        else:
            start = ex.emit(args[0])
            stop = ex.emit(args[1])
            step = ex.emit(args[2])

        if step is None:
            head = f"{pad}for {var} := {start}; {var} < {stop}; {var}++ {{"
        else:
            head = f"{pad}for {var} := {start}; {var} < {stop}; {var} += {step} {{"
        lines = [head]
        lines.extend(_emit_block(s.body, indent + 1, ex))
        lines.append(f"{pad}}}")
        return lines

    # generic range fallback
    it = ex.emit(s.iterable)
    lines = [f"{pad}for _, {var} := range {it} {{"]
    lines.extend(_emit_block(s.body, indent + 1, ex))
    lines.append(f"{pad}}}")
    return lines


def emit_go(stmts: List[Stmt], indent: int = 1) -> str:
    """Render an AX statement list as Go at the given indent level."""
    ex = _GoExprEmitter()
    return "\n".join(_emit_block(stmts, indent, ex))


# Helper that callers using abs() must include in their package.
ABS_HELPER = """
func _absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}
"""
