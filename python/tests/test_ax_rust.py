"""Runtime validation of the AX Rust emitter against rustc.

Each test parses an AX program, emits Rust, wraps it in a compilable program,
compiles with `rustc`, runs it, and asserts the output is CORRECT.
Requires `rustc` on PATH.
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
from aicl.ax.emitter_rust import emit_rust

RUSTC = shutil.which("rustc")
pytestmark = pytest.mark.skipif(RUSTC is None, reason="rustc not installed")


def _run_rust(ax_source: str, program: str) -> str:
    """Emit AX as Rust, splice into program, compile + run via rustc, return stdout.

    ``program`` is a format string with one ``%s`` placeholder for the AX-emitted
    function body (already indented). The program is prefixed with an allow
    attribute to suppress style lints (unused parens / mut) that are inherent
    to mechanical codegen but irrelevant to correctness.
    """
    body = emit_rust(parse(textwrap.dedent(ax_source)), indent=2)
    src = "#![allow(unused_parens, unused_mut, dead_code, unused_assignments)]\n" + (program % body)
    with tempfile.TemporaryDirectory() as d:
        rs = os.path.join(d, "main.rs")
        with open(rs, "w", encoding="utf-8") as f:
            f.write(src)
        exe = os.path.join(d, "main.exe" if os.name == "nt" else "main")
        compile_proc = subprocess.run(
            [RUSTC, "-O", "-o", exe, rs],
            capture_output=True, text=True, timeout=60,
        )
        if compile_proc.returncode != 0:
            pytest.fail(f"rustc failed:\n{compile_proc.stderr[:1500]}")
        run_proc = subprocess.run([exe], capture_output=True, text=True, timeout=15)
        if run_proc.returncode != 0:
            pytest.fail(f"runtime panic:\n{run_proc.stderr[:500]}")
        return run_proc.stdout.strip()


def test_rust_quicksort():
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
fn partition(array: &mut [i64], low: i64, high: i64) -> i64 {
%s
}
fn quicksort(array: &mut [i64], low: i64, high: i64) {
    if low < high {
        let p = partition(array, low, high);
        quicksort(array, low, p - 1);
        quicksort(array, p + 1, high);
    }
}
fn main() {
    let mut arr = vec![3i64, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5];
    let n = arr.len() as i64;
    let expected = vec![1i64, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9];
    quicksort(&mut arr, 0, n - 1);
    if arr == expected { println!(\"CORRECT\"); } else { println!(\"WRONG\"); }
}
"""
    assert _run_rust(ax, program) == "CORRECT"


def test_rust_binary_search():
    ax = """\
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
        return -1"""
    program = """\
fn search(array: &[i64], target: i64) -> i64 {
%s
}
fn main() {
    let arr = vec![1i64, 3, 5, 7, 9, 11, 13, 15, 17, 19];
    let mut ok = true;
    for i in 0..arr.len() {
        if search(&arr, arr[i]) != (i as i64) { ok = false; }
    }
    if search(&arr, 0) != -1 { ok = false; }
    if search(&arr, 20) != -1 { ok = false; }
    if search(&arr, 8) != -1 { ok = false; }
    if ok { println!(\"CORRECT\"); } else { println!(\"WRONG\"); }
}
"""
    assert _run_rust(ax, program) == "CORRECT"


def test_rust_factorial_recursive():
    ax = """\
        if n <= 1:
            return 1
        return n * factorial(n - 1)"""
    program = """\
fn factorial(n: i64) -> i64 {
%s
}
fn main() {
    let expected = [1i64, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880];
    let mut ok = true;
    for n in 0..10 {
        if factorial(n) != expected[n as usize] { ok = false; }
    }
    if ok { println!(\"CORRECT\"); } else { println!(\"WRONG\"); }
}
"""
    assert _run_rust(ax, program) == "CORRECT"
