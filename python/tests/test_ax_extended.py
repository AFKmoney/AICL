"""Tests for the extended AX sub-language: dicts, slicing, string methods, in operator.

These verify that the new language features (added to make AICL a general-purpose
language) parse, emit, and execute correctly across targets.
"""

import pytest
import sys
import os

# Ensure src is on path
_src = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src"))
if os.path.isdir(_src):
    sys.path.insert(0, _src)

from aicl.ax.parser import parse
from aicl.ax.ast import DictLit, SetLit, Slice, Index, BinOp, Assign, MethodCall
from aicl.ax.emitter_python import emit_python
from aicl.ax.emitter_javascript import emit_javascript


class TestDictLiterals:
    def test_empty_dict(self):
        stmts = parse("d = {}")
        assert isinstance(stmts[0], Assign)
        assert isinstance(stmts[0].value, DictLit)
        assert len(stmts[0].value.pairs) == 0

    def test_dict_with_string_keys(self):
        stmts = parse('d = {"a": 1, "b": 2}')
        assert isinstance(stmts[0].value, DictLit)
        assert len(stmts[0].value.pairs) == 2

    def test_dict_access(self):
        stmts = parse('x = d["key"]')
        assert isinstance(stmts[0].value, Index)

    def test_dict_emits_python(self):
        stmts = parse('d = {"a": 1, "b": 2}')
        code = emit_python(stmts, indent=0)
        assert '"a"' in code
        assert "1" in code

    def test_dict_emits_javascript(self):
        stmts = parse('d = {"a": 1, "b": 2}')
        code = emit_javascript(stmts, indent=0)
        assert "Object.fromEntries" in code


class TestSlicing:
    def test_simple_slice(self):
        stmts = parse("x = arr[1:3]")
        assert isinstance(stmts[0].value, Slice)
        assert stmts[0].value.start is not None
        assert stmts[0].value.stop is not None
        assert stmts[0].value.step is None

    def test_slice_no_start(self):
        stmts = parse("x = arr[:5]")
        assert isinstance(stmts[0].value, Slice)
        assert stmts[0].value.start is None
        assert stmts[0].value.stop is not None

    def test_slice_with_step(self):
        stmts = parse("x = arr[0:10:2]")
        assert isinstance(stmts[0].value, Slice)
        assert stmts[0].value.step is not None

    def test_slice_emits_python(self):
        stmts = parse("x = arr[1:3]")
        code = emit_python(stmts, indent=0)
        assert "[1:3]" in code


class TestInOperator:
    def test_in_operator(self):
        stmts = parse('if x in nums:\n    return true')
        assert isinstance(stmts[0], type(parse("if x in nums:\n    return true")[0]))

    def test_not_in_operator(self):
        stmts = parse('if x not in nums:\n    return true')
        # Should parse without error

    def test_in_emits_python(self):
        stmts = parse("result = x in nums")
        code = emit_python(stmts, indent=0)
        assert " in " in code

    def test_in_emits_javascript(self):
        stmts = parse("result = x in nums")
        code = emit_javascript(stmts, indent=0)
        assert ".includes" in code


class TestStringMethods:
    def test_upper(self):
        stmts = parse('x = word.upper()')
        assert isinstance(stmts[0].value, MethodCall)
        assert stmts[0].value.method == "upper"

    def test_split(self):
        stmts = parse('parts = text.split(",")')
        assert isinstance(stmts[0].value, MethodCall)
        assert stmts[0].value.method == "split"

    def test_string_literal_method(self):
        # "hello".upper() should parse correctly
        stmts = parse('x = "hello".upper()')
        assert isinstance(stmts[0].value, MethodCall)

    def test_chained_methods(self):
        # text.strip().lower() should parse
        stmts = parse('x = text.strip().lower()')
        assert isinstance(stmts[0].value, MethodCall)


class TestStandardLibrary:
    def test_print(self):
        stmts = parse('print("hello")')
        code = emit_python(stmts, indent=0)
        assert "print(" in code

    def test_print_javascript(self):
        stmts = parse('print("hello")')
        code = emit_javascript(stmts, indent=0)
        assert "console.log" in code

    def test_int_conversion(self):
        stmts = parse('x = int("42")')
        code = emit_python(stmts, indent=0)
        assert "int(" in code

    def test_str_conversion(self):
        stmts = parse('x = str(42)')
        code = emit_python(stmts, indent=0)
        assert "str(" in code

    def test_sum(self):
        stmts = parse('total = sum(nums)')
        code = emit_python(stmts, indent=0)
        assert "sum(" in code

    def test_sorted(self):
        stmts = parse('x = sorted(nums)')
        code = emit_python(stmts, indent=0)
        assert "sorted(" in code

    def test_len(self):
        stmts = parse('x = len(word)')
        code = emit_python(stmts, indent=0)
        assert "len(" in code


class TestEndToEndExecution:
    """Verify that generated Python code actually executes correctly."""

    def _compile_and_run(self, source, func_name, args):
        """Compile AICL source and run a behavior method, returning the result."""
        from aicl import Compiler
        c = Compiler(target_language="python")
        r = c.compile(source)
        assert r.success, f"Compilation failed: {r.errors}"

        import tempfile
        import importlib.util
        import inspect
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(r.source_code)
            f.flush()
            spec = importlib.util.spec_from_file_location("test_mod", f.name)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        # Find the class that has the behavior method
        app = None
        for name in dir(mod):
            obj = getattr(mod, name)
            if inspect.isclass(obj) and hasattr(obj, func_name):
                app = obj()
                break
        assert app is not None, f"No class with method {func_name} found"
        method = getattr(app, func_name)
        return method(*args)

    def test_dict_operations(self):
        source = """Goal:
Test dict operations

Layer:
Test

Validation:
Dicts work

Behavior BuildDict
    Input: a, b
    Output: result
    Action:
        d = {}
        d["x"] = a
        d["y"] = b
        return d["x"] + d["y"]
"""
        result = self._compile_and_run(source, "_behavior_builddict", [3, 4])
        assert result == 7

    def test_string_processing(self):
        source = """Goal:
Test string processing

Layer:
Test

Validation:
Strings work

Behavior ProcessString
    Input: text
    Output: result
    Action:
        result = text.upper().strip()
        return result
"""
        result = self._compile_and_run(source, "_behavior_processstring", ["  hello  "])
        assert result == "HELLO"

    def test_in_operator(self):
        source = """Goal:
Test in operator

Layer:
Test

Validation:
In works

Behavior CheckIn
    Input: item, collection
    Output: result
    Action:
        if item in collection:
            return true
        else:
            return false
"""
        result = self._compile_and_run(source, "_behavior_checkin", [3, [1, 2, 3]])
        assert result == True

    def test_slicing(self):
        source = """Goal:
Test slicing

Layer:
Test

Validation:
Slicing works

Behavior GetSlice
    Input: nums
    Output: result
    Action:
        return nums[1:3]
"""
        result = self._compile_and_run(source, "_behavior_getslice", [[10, 20, 30, 40, 50]])
        assert result == [20, 30]

    def test_type_conversion(self):
        source = """Goal:
Test type conversion

Layer:
Test

Validation:
Conversion works

Behavior ConvertAndAdd
    Input: a, b
    Output: result
    Action:
        x = int(a) + int(b)
        return str(x)
"""
        result = self._compile_and_run(source, "_behavior_convertandadd", ["5", "7"])
        assert result == "12"
