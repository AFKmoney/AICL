"""Runtime validation of the AX JavaScript emitter against Node.

Each test parses an AX program, emits JavaScript, wraps it in a runnable
script, executes it via Node, and asserts the algorithm produced the correct
result. Requires `node` on PATH.
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
from aicl.ax.emitter_javascript import emit_javascript

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not installed")


def _run_js(ax_source: str, wrapper: str) -> str:
    """Emit AX as JS, splice into wrapper, run via Node, return stdout."""
    body = emit_javascript(parse(textwrap.dedent(ax_source)), indent=1)
    script = wrapper % body
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        path = f.name
    try:
        proc = subprocess.run([NODE, path], capture_output=True, text=True, timeout=15)
        if proc.returncode != 0:
            pytest.fail(f"node failed: {proc.stderr.strip()[:500]}")
        return proc.stdout.strip()
    finally:
        os.unlink(path)


def test_js_quicksort():
    ax = """\
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1"""
    wrapper = """\
function partition(array, low, high) {
%s
}
function quicksort(array, low, high) {
  if (low < high) {
    const p = partition(array, low, high);
    quicksort(array, low, p - 1);
    quicksort(array, p + 1, high);
  }
}
const arr = [3,1,4,1,5,9,2,6,5,3,5];
const orig = [...arr];
quicksort(arr, 0, arr.length - 1);
const expected = [...orig].sort((a,b) => a - b);
console.log(arr.every((v,i) => v === expected[i]) ? 'CORRECT' : 'WRONG');
"""
    assert _run_js(ax, wrapper) == "CORRECT"


def test_js_binary_search():
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
    wrapper = """\
function search(array, target) {
%s
}
const arr = [1,3,5,7,9,11,13,15,17,19];
let ok = true;
for (let i = 0; i < arr.length; i++) if (search(arr, arr[i]) !== i) ok = false;
if (search(arr,0) !== -1) ok = false;
if (search(arr,20) !== -1) ok = false;
if (search(arr,8) !== -1) ok = false;
console.log(ok ? 'CORRECT' : 'WRONG');
"""
    assert _run_js(ax, wrapper) == "CORRECT"


def test_js_factorial_recursive():
    ax = """\
        if n <= 1:
            return 1
        return n * factorial(n - 1)"""
    wrapper = """\
function factorial(n) {
%s
}
const expected = [1,1,2,6,24,120,720,5040,40320,362880];
let ok = true;
for (let n = 0; n <= 9; n++) if (factorial(n) !== expected[n]) ok = false;
console.log(ok ? 'CORRECT' : 'WRONG');
"""
    assert _run_js(ax, wrapper) == "CORRECT"


def test_js_truthy_logic_and_none():
    """Exercises boolean ops, not, None literal."""
    ax = """\
        found = none
        if not flag and value > 0:
            found = true
        else:
            found = false
        return found"""
    wrapper = """\
function decide(flag, value) {
%s
}
const out = decide(false, 5) === true && decide(true, 5) === false && decide(false, -1) === false;
console.log(out ? 'CORRECT' : 'WRONG');
"""
    assert _run_js(ax, wrapper) == "CORRECT"
