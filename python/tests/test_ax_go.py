"""Validation of the AX Go emitter.

If `go` is on PATH, these tests compile + run the emitted Go and assert
algorithm correctness, just like the Python/JS/Rust runtime tests. If `go`
is absent, the runtime tests skip but a structural check still runs to catch
emitter regressions (valid AST -> well-formed Go output).
"""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aicl.ax import parse
from aicl.ax.emitter_go import emit_go

GO = shutil.which("go")


# ---------------------------------------------------------------------------
# Structural tests (always run, no toolchain required)
# ---------------------------------------------------------------------------

def test_go_quicksort_structure():
    ax = """\
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1"""
    out = emit_go(parse(textwrap.dedent(ax)), indent=1)
    assert "for j := low; j < high; j++ {" in out
    assert "pivot := array[high]" in out
    # swap should use temps for indexed swap
    assert "_axTmp" in out
    # braces balanced
    assert out.count("{") == out.count("}")


def test_go_if_elif_else_chain():
    ax = """\
        if x == 1:
            return 1
        elif x == 2:
            return 2
        else:
            return 3"""
    out = emit_go(parse(textwrap.dedent(ax)), indent=1)
    # Go requires `} else if {` on the same line
    assert "} else if " in out
    assert "} else {" in out


def test_go_brace_balance_on_all_constructs():
    """Every emitted construct must produce balanced braces."""
    cases = [
        "x = 1",
        "if x > 0:\n    return 1\nelse:\n    return 0",
        "while i < 10:\n    i += 1",
        "for j in range(0, 5):\n    total += j",
        "a, b = b, a",
    ]
    for src in cases:
        out = emit_go(parse(textwrap.dedent(src)), indent=1)
        assert out.count("{") == out.count("}"), f"unbalanced braces in: {src}\n{out}"


# ---------------------------------------------------------------------------
# Runtime tests (require `go` on PATH)
# ---------------------------------------------------------------------------

pytestmark_runtime = pytest.mark.skipif(GO is None, reason="go not installed")


def _run_go(ax_source: str, program: str) -> str:
    body = emit_go(parse(textwrap.dedent(ax_source)), indent=1)
    src = program % body
    with tempfile.TemporaryDirectory() as d:
        go_file = os.path.join(d, "main.go")
        with open(go_file, "w", encoding="utf-8") as f:
            f.write(src)
        exe = os.path.join(d, "main.exe" if os.name == "nt" else "main")
        build = subprocess.run([GO, "build", "-o", exe, go_file],
                               capture_output=True, text=True, timeout=60)
        if build.returncode != 0:
            pytest.fail(f"go build failed:\n{build.stderr[:1500]}")
        run = subprocess.run([exe], capture_output=True, text=True, timeout=15)
        if run.returncode != 0:
            pytest.fail(f"go runtime panic:\n{run.stderr[:500]}")
        return run.stdout.strip()


@pytestmark_runtime
def test_go_quicksort_runtime():
    ax = """\
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1"""
    program = """\
package main

func partition(array []int, low int, high int) int {
%s
}
func quicksort(array []int, low int, high int) {
    if low < high {
        p := partition(array, low, high)
        quicksort(array, low, p-1)
        quicksort(array, p+1, high)
    }
}
func main() {
    arr := []int{3,1,4,1,5,9,2,6,5,3,5}
    expected := []int{1,1,2,3,3,4,5,5,5,6,9}
    quicksort(arr, 0, len(arr)-1)
    ok := true
    for i := range arr { if arr[i] != expected[i] { ok = false } }
    if ok { println("CORRECT") } else { println("WRONG") }
}
"""
    assert _run_go(ax, program) == "CORRECT"


@pytestmark_runtime
def test_go_factorial_runtime():
    ax = """\
        if n <= 1:
            return 1
        return n * factorial(n - 1)"""
    program = """\
package main

func factorial(n int) int {
%s
}
func main() {
    expected := []int{1,1,2,6,24,120,720,5040,40320,362880}
    ok := true
    for n := 0; n < 10; n++ { if factorial(n) != expected[n] { ok = false } }
    if ok { println("CORRECT") } else { println("WRONG") }
}
"""
    assert _run_go(ax, program) == "CORRECT"
