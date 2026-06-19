"""Cross-target test: one AX spec compiled to all 4 targets.

This is the integration test that proves the Phase B goal: a single .aicl
spec written in AX produces real algorithm code in Python, JavaScript, Rust,
and Go — not stubs. For each target we verify:
  - the AX algorithm body is present (not a commented stub)
  - the behavior method has the right parameters
  - where a runtime is available, the generated code executes correctly

Runtimes used (auto-detected):
  - python: always (in-process exec)
  - javascript: `node --check` for syntax, always available here
  - rust: rustc compile + run (skipped if absent)
  - go: go build (skipped if absent)
"""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aicl.compiler import Compiler

NODE = shutil.which("node")
RUSTC = shutil.which("rustc")
GO = shutil.which("go")

# A single AX spec used across all targets. Lomuto quicksort partition.
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

# Markers proving the real algorithm survived into each target's output.
AX_PRESENT_MARKERS = {
    "python":     ["for j in range(low, high)", "pivot = array[high]", "return"],
    "javascript": ["for (let j = low; j < high", "let pivot = array[high]", "return"],
    "rust":       ["for j in (low)..(high)", "let mut pivot", "return"],
    "go":         ["for j := low; j < high", "pivot := array[high]", "return"],
}


@pytest.fixture(scope="module")
def compiled_targets():
    """Compile the quicksort spec to all 4 targets, return {target: result}."""
    out = {}
    for target in ("python", "javascript", "rust", "go"):
        out[target] = Compiler(target_language=target).compile(QUICKSORT_AICL)
    return out


class TestAXPresentInAllTargets:
    """The real algorithm must appear in every target's generated output."""

    def test_ax_sources_populated(self, compiled_targets):
        for target, result in compiled_targets.items():
            assert result.ax_sources, f"{target}: ax_sources empty"

    @pytest.mark.parametrize("target", ["python", "javascript", "rust", "go"])
    def test_algorithm_body_present(self, compiled_targets, target):
        src = compiled_targets[target].source_code
        for marker in AX_PRESENT_MARKERS[target]:
            assert marker in src, (
                f"{target}: expected AX marker {marker!r} in output\n"
                f"got (first 500 chars):\n{src[:500]}"
            )

    def test_python_executes_correctly(self, compiled_targets):
        """Import the Python output and run quicksort on a real array."""
        import ast as pyast
        import importlib.util
        result = compiled_targets["python"]
        pyast.parse(result.source_code)  # must be valid Python
        mod = importlib.util.module_from_spec(
            importlib.util.spec_from_loader("ax_cross", loader=None))
        exec(compile(result.source_code, "<cross>", "exec"), mod.__dict__)
        # find the class with the partition method
        cls = next(v for v in vars(mod).values()
                   if isinstance(v, type)
                   and any(m.startswith("_behavior_partition") for m in dir(v)))
        mname = next(m for m in dir(cls) if m.startswith("_behavior_partition"))
        partition = getattr(cls(), mname)

        def qs(a, lo, hi):
            if lo < hi:
                p = partition(a, lo, hi)
                qs(a, lo, p - 1)
                qs(a, p + 1, hi)

        for arr in [[3,1,4,1,5,9,2,6,5,3,5], [5,4,3,2,1], [1], []]:
            work = list(arr)
            if work:
                qs(work, 0, len(work) - 1)
            assert work == sorted(arr)

    @pytest.mark.skipif(NODE is None, reason="node not installed")
    def test_javascript_syntax_valid(self, compiled_targets):
        """node --check confirms the JS output parses."""
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8") as f:
            f.write(compiled_targets["javascript"].source_code)
            path = f.name
        try:
            proc = subprocess.run([NODE, "--check", path],
                                  capture_output=True, text=True, timeout=15)
            assert proc.returncode == 0, f"node --check failed:\n{proc.stderr[:500]}"
        finally:
            os.unlink(path)

    @pytest.mark.skipif(RUSTC is None, reason="rustc not installed")
    def test_rust_full_program_compiles(self, compiled_targets):
        """The FULL generated Rust program (scaffolding + AX behaviors) must
        compile cleanly with rustc. This validates that the scaffolding
        (AppError enum, Application struct, main()) is consistent with the
        AX-generated behavior methods."""
        with tempfile.TemporaryDirectory() as d:
            rs = os.path.join(d, "main.rs")
            # suppress style lints inherent to mechanical codegen
            src = "#![allow(unused_parens, unused_mut, dead_code, unused_imports)]\n" \
                  + compiled_targets["rust"].source_code
            with open(rs, "w", encoding="utf-8") as f:
                f.write(src)
            exe = os.path.join(d, "main.exe" if os.name == "nt" else "main")
            proc = subprocess.run([RUSTC, "-O", "-o", exe, rs],
                                  capture_output=True, text=True, timeout=60)
            assert proc.returncode == 0, (
                f"rustc failed to compile the full program:\n{proc.stderr[:1000]}"
            )
            # And the binary should run without panicking.
            run = subprocess.run([exe], capture_output=True, text=True, timeout=15)
            assert run.returncode == 0, f"runtime panic:\n{run.stderr[:300]}"

    @pytest.mark.skipif(RUSTC is None, reason="rustc not installed")
    def test_rust_partition_compiles_and_runs(self, compiled_targets):
        """Extract the partition fn, wrap it with a real quicksort driver,
        and verify it sorts correctly. This proves the AX-generated algorithm
        is executable and correct in Rust."""
        src = compiled_targets["rust"].source_code
        # Extract the partition fn body using brace-matching.
        lines = src.splitlines()
        capture = False
        depth = 0
        fn_body = []
        for ln in lines:
            if "fn partition" in ln:
                capture = True
            if capture:
                fn_body.append(ln)
                depth += ln.count("{") - ln.count("}")
                if depth <= 0 and len(fn_body) > 1:
                    break
        assert fn_body, "partition function not found in Rust output"
        partition_fn = "\n".join(fn_body).replace("    pub fn partition(&mut self, ",
                                                   "fn partition(")

        program = f"""#![allow(unused_parens, unused_mut, dead_code)]
{partition_fn}

fn quicksort(array: &mut [i64], low: i64, high: i64) {{
    if low < high {{
        let p = partition(array, low, high);
        quicksort(array, low, p - 1);
        quicksort(array, p + 1, high);
    }}
}}

fn main() {{
    let mut arr = vec![3i64, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5];
    let n = arr.len() as i64;
    quicksort(&mut arr, 0, n - 1);
    let expected = vec![1i64, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9];
    if arr == expected {{ println!("CORRECT"); }} else {{ println!("WRONG"); }}
}}
"""
        with tempfile.TemporaryDirectory() as d:
            rs = os.path.join(d, "main.rs")
            with open(rs, "w", encoding="utf-8") as f:
                f.write(program)
            exe = os.path.join(d, "main.exe" if os.name == "nt" else "main")
            proc = subprocess.run([RUSTC, "-O", "-o", exe, rs],
                                  capture_output=True, text=True, timeout=60)
            assert proc.returncode == 0, f"rustc failed:\n{proc.stderr[:800]}"
            run = subprocess.run([exe], capture_output=True, text=True, timeout=15)
            assert "CORRECT" in run.stdout, f"runtime: {run.stdout} {run.stderr[:300]}"

    @pytest.mark.skipif(GO is None, reason="go not installed")
    def test_go_builds(self, compiled_targets):
        """go build must accept the generated Go."""
        with tempfile.TemporaryDirectory() as d:
            gof = os.path.join(d, "main.go")
            with open(gof, "w", encoding="utf-8") as f:
                f.write(compiled_targets["go"].source_code)
            exe = os.path.join(d, "main.exe" if os.name == "nt" else "main")
            proc = subprocess.run([GO, "build", "-o", exe, gof],
                                  capture_output=True, text=True, timeout=60)
            assert proc.returncode == 0, f"go build failed:\n{proc.stderr[:800]}"
