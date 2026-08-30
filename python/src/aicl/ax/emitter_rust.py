"""Rust emitter for the AICL-Action (AX) sub-language.

Walks the same AX AST as the other emitters but renders Rust. Rust is
statically typed, so this emitter makes pragmatic typing decisions:

  - Integer literals    -> i64
  - Float literals      -> f64
  - Boolean expressions -> bool
  - List literals       -> Vec<i64>  (AX lists are homogeneous in practice for
                                      the algorithms we target; mixed-type
                                      lists would need an enum, out of scope)
  - All bindings are    -> let mut (AX has no const/mut distinction)

Translation rules for the non-obvious cases:
  - range(a, b)         -> (a..b)
  - range(a, b, c)      -> (a..b).step_by(c as usize)
  - a, b = b, a         -> let (_a, _b) = (a, b); a = _b; b = _a;
                           (Rust tuple-destructure swap is verbose)
  - True/False/None     -> true/false/None::<i64>
  - and/or/not          -> &&/||/!
  - a // b              -> (a / b)  (i64 division truncates toward zero)
  - a ** b              -> i64::pow(a, b as u32)
  - len(x)              -> x.len() as i64
  - abs(x)              -> i64::abs(a)
  - array[j]            -> *array.get(j as usize).unwrap()  (panic-safe indexing
                                                            would be .clone())

Output is valid Rust 2021. The generated code lives inside a function body;
callers wrap it with the function signature.
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


class _RustExprEmitter:
    """Renders AX expressions as Rust expression strings."""

    def __init__(self):
        self.seen: Set[str] = set()
        self.swap_counter = 0

    def fresh_temp(self) -> str:
        self.swap_counter += 1
        return f"_ax_tmp_{self.swap_counter}"

    def emit(self, e: A.Expr) -> str:
        if isinstance(e, IntLit):
            return f"{e.value}i64"
        if isinstance(e, FloatLit):
            return f"{e.value}f64"
        if isinstance(e, BoolLit):
            return "true" if e.value else "false"
        if isinstance(e, NoneLit):
            return "None::<i64>"
        if isinstance(e, StrLit):
            esc = e.value.replace("\\", "\\\\").replace('"', '\\"')
            return f'String::from("{esc}")'
        if isinstance(e, Name):
            return e.name
        if isinstance(e, ListLit):
            inner = ", ".join(self.emit(x) for x in e.elements)
            return f"vec![{inner}]"
        if isinstance(e, DictLit):
            # Rust HashMap from entries
            pairs = ", ".join(f"({self.emit(k)}, {self.emit(v)})" for k, v in e.pairs)
            return f"_ax_dict!({pairs})"
        if isinstance(e, SetLit):
            inner = ", ".join(self.emit(x) for x in e.elements)
            return f"_ax_set!({inner})"
        if isinstance(e, Slice):
            start = self.emit(e.start) if e.start is not None else "0"
            stop = self.emit(e.stop) if e.stop is not None else "None"
            if e.step is not None:
                # Rust doesn't support step natively; use iterators
                step = self.emit(e.step)
                return f"{self.emit(e.target)}.iter().step_by({step} as usize).cloned().collect::<Vec<_>>()"
            if e.stop is not None:
                return f"{self.emit(e.target)}[{start}..{stop} as usize].to_vec()"
            return f"{self.emit(e.target)}[{start}..].to_vec()"
        if isinstance(e, BinOp):
            return self._binop(e)
        if isinstance(e, UnaryOp):
            if e.op == "not":
                return f"(!{self.emit(e.operand)})"
            return f"(-{self.emit(e.operand)})"
        if isinstance(e, Index):
            return f"{self.emit(e.target)}[{self.emit(e.index)} as usize]"
        if isinstance(e, Attr):
            return f"{self.emit(e.target)}.{e.attr}"
        if isinstance(e, Call):
            return self._call(e)
        if isinstance(e, MethodCall):
            return self._method_call(e)
        raise TypeError(f"cannot emit Rust expression node {type(e).__name__}")

    def _binop(self, e: BinOp) -> str:
        L = self.emit(e.left)
        R = self.emit(e.right)
        if e.op == "and":
            return f"({L} && {R})"
        if e.op == "or":
            return f"({L} || {R})"
        # membership operators
        if e.op == "in":
            return f"({R}.contains(&{L}))"
        if e.op == "not_in":
            return f"(!{R}.contains(&{L}))"
        # identity operators
        if e.op == "is":
            return f"({L} == {R})"
        if e.op == "is_not":
            return f"({L} != {R})"
        if e.op == "//":
            return f"({L} / {R})"
        if e.op == "**":
            return f"i64::pow({L}, {R} as u32)"
        if e.op == "%":
            return f"({L} % {R})"
        return f"({L} {e.op} {R})"

    def _call(self, e: Call) -> str:
        args = [self.emit(a) for a in e.args]

        # I/O
        if e.func == "print":
            # Rust print! with multiple args
            fmt = ", ".join("{:?}" for _ in args)
            return f'println!("{{}}", {", ".join(args)})'
        if e.func == "read_file":
            return f"std::fs::read_to_string({args[0]}).unwrap()"
        if e.func == "write_file":
            return f"std::fs::write({args[0]}, {args[1]}).unwrap()"

        # Type conversion
        if e.func == "int" and len(args) == 1:
            return f"({args[0]} as i64)"
        if e.func == "str" and len(args) == 1:
            return f"format!(\"{{}}\", {args[0]})"
        if e.func == "float" and len(args) == 1:
            return f"({args[0]} as f64)"
        if e.func == "bool" and len(args) == 1:
            return f"({args[0]} != 0)"

        # Collections
        if e.func == "len" and len(args) == 1:
            return f"({args[0]}.len() as i64)"
        if e.func == "abs" and len(args) == 1:
            return f"i64::abs({args[0]})"
        if e.func in ("max", "min") and len(args) >= 1:
            return f"i64::{e.func}({', '.join(args)})"
        if e.func == "sum" and len(args) == 1:
            return f"{args[0]}.iter().sum::<i64>()"
        if e.func == "sorted" and len(args) == 1:
            return f"{{ let mut v = {args[0]}.clone(); v.sort(); v }}"
        if e.func == "reversed" and len(args) == 1:
            return f"{{ let mut v = {args[0]}.clone(); v.reverse(); v }}"

        # String functions
        if e.func == "ord" and len(args) == 1:
            return f"({args[0]}.chars().next().unwrap() as i64)"
        if e.func == "chr" and len(args) == 1:
            return f"char::from_u32({args[0]} as u32).unwrap().to_string()"

        # Math
        if e.func == "sqrt" and len(args) == 1:
            return f"({args[0]} as f64).sqrt()"
        if e.func == "pow" and len(args) == 2:
            return f"i64::pow({args[0]}, {args[1]} as u32)"
        if e.func == "floor" and len(args) == 1:
            return f"({args[0]} as f64).floor() as i64"
        if e.func == "ceil" and len(args) == 1:
            return f"({args[0]} as f64).ceil() as i64"

        if e.func == "range":
            if len(args) == 1:
                return f"(0..{args[0]}).collect::<Vec<_>>()"
            elif len(args) == 2:
                return f"({args[0]}..{args[1]}).collect::<Vec<_>>()"
            else:
                start, stop, step = args[0], args[1], args[2]
                return f"({start}..{stop}).step_by({step} as usize).collect::<Vec<_>>()"
        return f"{e.func}({', '.join(args)})"

    def _method_call(self, e: MethodCall) -> str:
        """Translate common Python methods to Rust equivalents."""
        args = [self.emit(a) for a in e.args]
        target = self.emit(e.target)

        # String methods
        if e.method == "upper":
            return f"{target}.to_uppercase()"
        if e.method == "lower":
            return f"{target}.to_lowercase()"
        if e.method == "strip":
            return f"{target}.trim().to_string()"
        if e.method == "split":
            if args:
                return f"{target}.split({args[0]}).map(|s| s.to_string()).collect::<Vec<_>>()"
            return f"{target}.split_whitespace().map(|s| s.to_string()).collect::<Vec<_>>()"
        if e.method == "replace":
            return f"{target}.replace({args[0]}, {args[1]})"
        if e.method == "find":
            return f"({target}.find({args[0]}).map(|i| i as i64).unwrap_or(-1))"
        if e.method == "startswith":
            return f"{target}.starts_with({args[0]})"
        if e.method == "endswith":
            return f"{target}.ends_with({args[0]})"
        if e.method == "contains":
            return f"{target}.contains({args[0]})"

        # List methods
        if e.method == "append":
            return f"{target}.push({args[0]})"
        if e.method == "pop":
            return f"{target}.pop().unwrap()"
        if e.method == "insert":
            return f"{target}.insert({args[0]} as usize, {args[1]})"
        if e.method == "remove":
            return f"{target}.remove({args[0]} as usize)"
        if e.method == "sort":
            return f"{target}.sort()"
        if e.method == "reverse":
            return f"{target}.reverse()"
        if e.method == "extend":
            return f"{target}.extend({args[0]})"

        # Default: direct method call
        return f"{target}.{e.method}({', '.join(args)})"


def _emit_block(stmts: List[Stmt], indent: int, ex: _RustExprEmitter) -> List[str]:
    if not stmts:
        return ["    " * indent + "// no-op"]
    lines: List[str] = []
    for s in stmts:
        lines.extend(_emit_stmt(s, indent, ex))
    return lines


def _emit_stmt(s: Stmt, indent: int, ex: _RustExprEmitter) -> List[str]:
    pad = "    " * indent

    if isinstance(s, Pass):
        return [f"{pad}// pass"]
    if isinstance(s, Break):
        return [f"{pad}break;"]
    if isinstance(s, Continue):
        return [f"{pad}continue;"]
    if isinstance(s, Return):
        if s.value is None:
            return [f"{pad}return;"]
        return [f"{pad}return {ex.emit(s.value)};"]
    if isinstance(s, ExprStmt):
        return [f"{pad}{ex.emit(s.expr)};"]
    if isinstance(s, SwapStmt):
        return _emit_swap(s, indent, ex)
    if isinstance(s, Assign):
        return _emit_assign(s, indent, ex)
    if isinstance(s, AugAssign):
        target = ex.emit(s.target)
        op = s.op[:-1]  # strip '=' from += etc.
        return [f"{pad}{target} {op}= {ex.emit(s.value)};"]
    if isinstance(s, If):
        return _emit_if(s, indent, ex)
    if isinstance(s, While):
        lines = [f"{pad}while {ex.emit(s.cond)} {{"]
        lines.extend(_emit_block(s.body, indent + 1, ex))
        lines.append(f"{pad}}}")
        return lines
    if isinstance(s, For):
        return _emit_for(s, indent, ex)
    raise TypeError(f"cannot emit Rust statement node {type(s).__name__}")


def _emit_assign(s: Assign, indent: int, ex: _RustExprEmitter) -> List[str]:
    pad = "    " * indent
    if isinstance(s.target, Name):
        name = s.target.name
        rhs = ex.emit(s.value)
        if name not in ex.seen:
            ex.seen.add(name)
            return [f"{pad}let mut {name} = {rhs};"]
        return [f"{pad}{name} = {rhs};"]
    # Index assignment: array[i] = x  — Rust needs * indexing for i64
    if isinstance(s.target, Index):
        target = ex.emit(s.target.target)
        idx = ex.emit(s.target.index)
        return [f"{pad}{target}[{idx} as usize] = {ex.emit(s.value)};"]
    # Attribute assignment
    target = ex.emit(s.target)
    return [f"{pad}{target} = {ex.emit(s.value)};"]


def _emit_swap(s: SwapStmt, indent: int, ex: _RustExprEmitter) -> List[str]:
    """Emit a tuple swap. AX swaps like a, b = b, a become, in Rust:

        let _ax_tmp_1 = <rhs-0>;
        let _ax_tmp_2 = <rhs-1>;
        <lhs-0> = _ax_tmp_1;
        <lhs-1> = _ax_tmp_2;

    All right-hand values are captured into temporaries BEFORE any assignment,
    so swapping indexed locations like array[i], array[j] = array[j], array[i]
    is correct (the second assignment does not see the first mutation).
    """
    pad = "    " * indent
    lines: List[str] = []
    left = s.swap.left
    right = s.swap.right
    if len(left) != len(right):
        raise ValueError("swap sides must have equal length")
    temps = [ex.fresh_temp() for _ in right]
    # capture all right-hand values first
    for t, rv in zip(temps, right):
        lines.append(f"{pad}let {t} = {ex.emit(rv)};")
    # assign temps into left targets
    for t, lv in zip(temps, left):
        lines.append(f"{pad}{_assign_target(lv, ex)} = {t};")
    return lines


def _assign_target(e: A.Expr, ex: _RustExprEmitter) -> str:
    """Render an lvalue for assignment (no value emission)."""
    if isinstance(e, Name):
        return e.name
    if isinstance(e, Index):
        target = ex.emit(e.target)
        return f"{target}[{ex.emit(e.index)} as usize]"
    return ex.emit(e)


def _emit_if(s: If, indent: int, ex: _RustExprEmitter) -> List[str]:
    pad = "    " * indent
    lines: List[str] = []
    first = True
    for cond, body in s.branches:
        kw = "if" if first else "else if"
        lines.append(f"{pad}{kw} {ex.emit(cond)} {{")
        lines.extend(_emit_block(body, indent + 1, ex))
        lines.append(f"{pad}}}")
        first = False
    if s.orelse:
        lines[-1] = f"{pad}}} else {{"
        lines.extend(_emit_block(s.orelse, indent + 1, ex))
        lines.append(f"{pad}}}")
    return lines


def _emit_for(s: For, indent: int, ex: _RustExprEmitter) -> List[str]:
    """Render for x in iterable. AX range maps to Rust ranges natively."""
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

        # Rust ranges need matching integer types; cast bounds to i64 then var as i64.
        if step is None:
            head = f"{pad}for {var} in ({start})..({stop}) {{"
        else:
            head = f"{pad}for {var} in ({start})..({stop}).step_by(({step}) as usize) {{"
        lines = [head]
        lines.extend(_emit_block(s.body, indent + 1, ex))
        lines.append(f"{pad}}}")
        return lines

    # generic iterator fallback
    it = ex.emit(s.iterable)
    lines = [f"{pad}for {var} in {it} {{"]
    lines.extend(_emit_block(s.body, indent + 1, ex))
    lines.append(f"{pad}}}")
    return lines


def emit_rust(stmts: List[Stmt], indent: int = 1) -> str:
    """Render an AX statement list as Rust at the given indent level.

    ``indent=1`` produces code one level deep (4 spaces), matching the body of
    a generated fn. Each call gets a fresh expression emitter so declaration
    tracking starts clean.
    """
    ex = _RustExprEmitter()
    return "\n".join(_emit_block(stmts, indent, ex))
