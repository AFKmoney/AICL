#!/usr/bin/env python3
"""
Tests for the AX (AICL-Action) Turing-complete sub-language.

These tests go beyond syntax: they compile real AX programs via the full
AICL pipeline (parse -> compile -> codegen) and EXECUTE the generated Python
to verify the algorithm produces the correct result. A regression here means
the compiler stopped emitting executable algorithm code.

Covers three reference algorithms that exercise distinct language features:
  - quicksort partition : for loop + if + array swap + indexing
  - binary search       : while loop + if/elif/else + integer division
  - factorial (recursive) : base case + recursive call + multiplication
"""

import sys
import os
import ast as pyast
import importlib.util
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from aicl.compiler import Compiler
from aicl.ax import parse, emit_python, is_ax, AXSyntaxError


# ---------------------------------------------------------------------------
# Unit tests for the AX frontend (lexer/parser/emitter) in isolation
# ---------------------------------------------------------------------------

class TestAXFrontend:
    def test_is_ax_distinguishes_code_from_prose(self):
        assert is_ax("x = 5\ny = x + 1") is True
        assert is_ax("partition the array around a pivot") is False
        assert is_ax("for i in range(10):\n    total += i") is True
        assert is_ax("") is False

    def test_parse_arithmetic_precedence(self):
        stmts = parse("x = 1 + 2 * 3")
        code = emit_python(stmts, indent=0)
        assert "x = (1 + (2 * 3))" in code  # mul binds tighter than add

    def test_parse_if_elif_else(self):
        src = textwrap.dedent("""\
            if x < 0:
                return -1
            elif x == 0:
                return 0
            else:
                return 1""")
        stmts = parse(src)
        code = emit_python(stmts, indent=0)
        assert "if (x < 0):" in code
        assert "elif (x == 0):" in code
        assert "else:" in code

    def test_parse_while_break(self):
        src = textwrap.dedent("""\
            while i < n:
                if found:
                    break
                i = i + 1""")
        stmts = parse(src)
        assert len(stmts) == 1
        from aicl.ax.ast import While, If, Break, Assign
        w = stmts[0]
        assert isinstance(w, While)
        assert isinstance(w.body[0], If)
        # If stores branches as [(cond, body)]; first branch's body has the Break
        assert isinstance(w.body[0].branches[0][1][0], Break)
        assert isinstance(w.body[1], Assign)

    def test_parse_swap(self):
        stmts = parse("a, b = b, a")
        code = emit_python(stmts, indent=0)
        assert "a, b = b, a" in code

    def test_parse_method_call(self):
        stmts = parse("result.append(x * 2)")
        code = emit_python(stmts, indent=0)
        assert "result.append((x * 2))" in code

    def test_emit_produces_valid_python(self):
        src = textwrap.dedent("""\
            total = 0
            for i in range(1, 11):
                total += i
            return total""")
        code = emit_python(parse(src), indent=1)
        pyast.parse("def f():\n" + code)  # raises if invalid

    def test_invalid_syntax_raises(self):
        with pytest.raises(AXSyntaxError):
            parse("for in range(10):")  # missing loop var
        with pytest.raises(AXSyntaxError):
            parse("x = ")  # missing rhs


# ---------------------------------------------------------------------------
# End-to-end: compile a .aicl with an AX Action and EXECUTE the result
# ---------------------------------------------------------------------------

def _compile_and_load(source: str, module_name: str = "ax_test_module"):
    """Compile an AICL source string, load the generated main.py, return the module."""
    compiler = Compiler()
    result = compiler.compile(source)
    assert result.success, f"compilation failed: {getattr(result, 'errors', 'unknown')}"
    # The generated source must be syntactically valid Python.
    pyast.parse(result.source_code)
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(compile(result.source_code, "<ax-test>", "exec"), mod.__dict__)
    return mod


def _find_behavior_method(mod, prefix: str):
    """Find the generated behavior method whose name starts with ``prefix``.

    The codegen appends a numeric suffix (e.g. ``_behavior_search_2``), so we
    match by prefix rather than exact name.
    """
    cls = next(v for v in vars(mod).values()
               if isinstance(v, type) and any(m.startswith(prefix) for m in dir(v)))
    method_name = next(m for m in dir(cls) if m.startswith(prefix))
    inst = cls()
    return getattr(inst, method_name)


# Minimal AICL program shells that embed AX in their Action: section.
# We keep the Goal/Risk/Recovery/Validation scaffolding minimal so the test
# focuses on the AX Action itself.

QUICKSORT_AICL = """\
Goal:
Sort an array of integers in ascending order

Constraint:
Use the Lomuto partition scheme

Risk:
Empty input array

Recovery:
Return an empty array

Layer:
Partition

Validation:
Output array is sorted

Behavior Partition
    Input: array, low, high
    Output: pivot_index
    Action:
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1
"""

BINARY_SEARCH_AICL = """\
Goal:
Find the index of a target integer in a sorted array

Constraint:
Array must be sorted in ascending order

Risk:
Target not present

Recovery:
Return -1

Layer:
Search

Validation:
Returned index points to the target, or -1 if absent

Behavior Search
    Input: array, target
    Output: index
    Action:
        low = 0
        high = len(array) - 1
        while low <= high:
            mid = (low + high) // 2
            if array[mid] == target:
                return mid
            elif array[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1
"""

FACTORIAL_AICL = """\
Goal:
Compute the factorial of a non-negative integer

Constraint:
Factorial of 0 is 1

Risk:
Negative input

Recovery:
Return 1

Layer:
Computation

Validation:
Result equals the product 1 * 2 * ... * n

Behavior Compute
    Input: n
    Output: result
    Action:
        if n <= 1:
            return 1
        return n * compute(n - 1)
"""


class TestQuicksortAX:
    def test_compiles_and_executes(self):
        mod = _compile_and_load(QUICKSORT_AICL)
        partition = _find_behavior_method(mod, "_behavior_partition")

        def quicksort(a, lo, hi):
            if lo < hi:
                p = partition(a, lo, hi)
                quicksort(a, lo, p - 1)
                quicksort(a, p + 1, hi)

        cases = [
            [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
            [5, 4, 3, 2, 1],
            [1],
            [2, 2, 2, 2],
            [],
        ]
        for arr in cases:
            work = list(arr)
            if work:
                quicksort(work, 0, len(work) - 1)
            assert work == sorted(arr), f"quicksort({arr}) -> {work}"


class TestBinarySearchAX:
    def test_compiles_and_executes(self):
        mod = _compile_and_load(BINARY_SEARCH_AICL)
        search = _find_behavior_method(mod, "_behavior_search")

        arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        # Present targets
        for idx, val in enumerate(arr):
            assert search(arr, val) == idx, f"search({val}) should be {idx}"
        # Absent targets
        assert search(arr, 0) == -1
        assert search(arr, 20) == -1
        assert search(arr, 8) == -1
        # Edge cases
        assert search([42], 42) == 0
        assert search([42], 7) == -1


class TestFactorialAX:
    def test_compiles_and_executes(self):
        mod = _compile_and_load(FACTORIAL_AICL)
        compute = _find_behavior_method(mod, "_behavior_compute")

        # The generated method recurses via bare name `compute`; we expose it
        # in the method's globals so the recursive call resolves.
        compute.__globals__['compute'] = compute

        import math
        for n in [0, 1, 2, 5, 7, 10]:
            expected = math.factorial(n)
            got = compute(n)
            assert got == expected, f"factorial({n}) = {got}, expected {expected}"
