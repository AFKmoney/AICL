#!/usr/bin/env python3
"""
AICL Test Suite - Comprehensive Tests

Tests all components of the AICL system:
- Parser (syntactic analysis)
- Architecture Tree (IR)
- Compiler (code generation)
- End-to-end compilation

Run with: python -m pytest tests/ -v
"""

import sys
import os
import tempfile
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aicl.parser import Parser, ParseError
from aicl.ast_nodes import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, SecuritySection,
)
from aicl.architecture_tree import ArchitectureTree, ArchitectureNode
from aicl.compiler import Compiler, CompilationResult


# =============================================================================
# Parser Tests
# =============================================================================

class TestParser:
    """Test the AICL parser."""

    def test_parse_goal(self):
        """Test parsing a Goal section."""
        source = "Goal:\nBuild a game"
        parser = Parser(source)
        program = parser.parse()
        assert len(program.goals) == 1
        assert "Build a game" in program.goals[0].description

    def test_parse_goal_inline(self):
        """Test parsing a Goal on the same line."""
        source = "Goal: Build a game"
        parser = Parser(source)
        program = parser.parse()
        assert len(program.goals) == 1
        assert "Build a game" in program.goals[0].description

    def test_parse_risk_recovery(self):
        """Test parsing Risk and Recovery sections."""
        source = """Goal:
Test

Risk:
Server down

Recovery:
Reconnect
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.risks) == 1
        assert len(program.recoveries) == 1
        assert "Server down" in program.risks[0].description
        assert "Reconnect" in program.recoveries[0].description

    def test_parse_layer(self):
        """Test parsing Layer sections."""
        source = """Goal:
Test

Layer:
Renderer

Layer:
Input System
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.layers) == 2
        assert program.layers[0].name == "Renderer"
        assert program.layers[1].name == "Input System"

    def test_parse_layer_with_sublayers(self):
        """Test parsing Layer with Sublayer sections."""
        source = """Goal:
Test

Layer:
Renderer
    Sublayer:
    Device creation
    Sublayer:
    Shader system
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.layers) == 1
        assert program.layers[0].name == "Renderer"
        assert len(program.layers[0].sublayers) == 2

    def test_parse_entity(self):
        """Test parsing Entity sections with fields."""
        source = """Goal:
Test

Entity User
    name: string
    id: integer
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.entities) == 1
        assert program.entities[0].name == "User"
        assert len(program.entities[0].fields) == 2
        assert program.entities[0].fields[0].name == "name"
        assert program.entities[0].fields[0].field_type == "string"

    def test_parse_behavior(self):
        """Test parsing Behavior sections."""
        source = """Goal:
Test

Behavior SendMessage
    Input:
        User Message
    Action:
        transmit message
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.behaviors) == 1
        assert program.behaviors[0].name == "SendMessage"
        assert "transmit" in program.behaviors[0].action

    def test_parse_validation(self):
        """Test parsing Validation sections."""
        source = """Goal:
Test

Validation:
System works correctly
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.validations) == 1
        assert "System works correctly" in program.validations[0].description

    def test_parse_constraint(self):
        """Test parsing Constraint sections."""
        source = """Goal:
Test

Constraint:
Must run at 60 FPS
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.constraints) == 1
        assert "60 FPS" in program.constraints[0].description

    def test_parse_condition(self):
        """Test parsing Condition sections."""
        source = """Goal:
Test

Condition:
    When user disconnected
    Then reconnect
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.conditions) == 1
        assert "disconnected" in program.conditions[0].when_clause

    def test_parse_event(self):
        """Test parsing Event sections."""
        source = """Goal:
Test

Event:
    On click
    Action:
    open menu
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.events) == 1
        assert "click" in program.events[0].on_clause

    def test_parse_security(self):
        """Test parsing Security sections."""
        source = """Goal:
Test

Security:
    Encrypt:
        user data
    Protect:
        passwords
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.securities) == 1
        assert len(program.securities[0].actions) == 2

    def test_parse_parallel(self):
        """Test parsing Parallel sections."""
        source = """Goal:
Test

Parallel:
    UI
    Network
    Logic
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.parallels) == 1
        assert len(program.parallels[0].layers) >= 2

    def test_parse_optimize(self):
        """Test parsing Optimize sections."""
        source = """Goal:
Test

Optimize:
Memory usage
"""
        parser = Parser(source)
        program = parser.parse()
        assert len(program.optimizations) == 1

    def test_program_validation(self):
        """Test that program validation detects missing sections."""
        program = AICLProgram()
        warnings = program.validate()
        assert len(warnings) > 0

    def test_complete_program(self):
        """Test parsing a complete AICL program."""
        source = """Goal:
Build a Pong game

Constraint:
60 FPS minimum

Risk:
Ball leaves play area

Recovery:
Clamp ball position

Layer:
Window Manager

Layer:
Game Logic

Validation:
Complete one playable match
"""
        parser = Parser(source)
        program = parser.parse()

        assert len(program.goals) == 1
        assert len(program.constraints) == 1
        assert len(program.risks) == 1
        assert len(program.recoveries) == 1
        assert len(program.layers) == 2
        assert len(program.validations) == 1

        warnings = program.validate()
        assert len(warnings) == 0


# =============================================================================
# Architecture Tree Tests
# =============================================================================

class TestArchitectureTree:
    """Test the Architecture Tree IR."""

    def test_tree_construction(self):
        """Test building an Architecture Tree from a program."""
        source = """Goal:
Build a game

Risk:
Server down

Recovery:
Reconnect

Layer:
Renderer

Layer:
Input System

Validation:
Game runs correctly
"""
        parser = Parser(source)
        program = parser.parse()
        tree = ArchitectureTree(program)

        assert tree.root.name == "System"
        assert "Build a game" in tree.root.goal
        assert len(tree.root.risks) == 1
        assert len(tree.root.recoveries) == 1
        assert len(tree.root.children) >= 2

    def test_tree_to_string(self):
        """Test the tree string representation."""
        source = """Goal:
Build a game

Layer:
Renderer

Validation:
Game works
"""
        parser = Parser(source)
        program = parser.parse()
        tree = ArchitectureTree(program)

        tree_str = tree.to_string()
        assert "System" in tree_str
        assert "Renderer" in tree_str

    def test_tree_to_dict(self):
        """Test the tree dictionary representation."""
        source = """Goal:
Test

Layer:
Network

Validation:
Works
"""
        parser = Parser(source)
        program = parser.parse()
        tree = ArchitectureTree(program)

        d = tree.to_dict()
        assert "name" in d
        assert d["name"] == "System"

    def test_dependency_order(self):
        """Test that dependency order is returned correctly."""
        source = """Goal:
Test

Layer:
UI

Layer:
Logic

Layer:
Data

Validation:
Works
"""
        parser = Parser(source)
        program = parser.parse()
        tree = ArchitectureTree(program)

        order = tree.get_dependency_order()
        assert len(order) >= 3


# =============================================================================
# Compiler Tests
# =============================================================================

class TestCompiler:
    """Test the AICL compiler."""

    def test_compile_simple_program(self):
        """Test compiling a simple AICL program."""
        source = """Goal:
Build a game

Risk:
Server down

Recovery:
Reconnect

Layer:
Renderer

Layer:
Game Logic

Validation:
Game runs correctly
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success, f"Compilation failed: {result.errors}"
        assert len(result.source_code) > 0
        assert "class" in result.source_code
        assert "def run" in result.source_code

    def test_compile_with_entities(self):
        """Test compiling a program with Entity sections."""
        source = """Goal:
Chat app

Layer:
Network

Entity User
    name: string
    id: integer

Entity Message
    content: string
    timestamp: datetime

Validation:
Messages sent correctly
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success, f"Compilation failed: {result.errors}"
        assert "class User" in result.source_code
        assert "class Message" in result.source_code

    def test_compile_generates_tests(self):
        """Test that the compiler generates test code."""
        source = """Goal:
Test app

Layer:
Core

Validation:
System works

Validation:
No errors
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success
        assert len(result.test_code) > 0
        assert "pytest" in result.test_code
        assert "test_validation" in result.test_code

    def test_compile_generates_architecture_tree(self):
        """Test that the compiler generates architecture tree string."""
        source = """Goal:
Game

Layer:
Renderer

Validation:
Works
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success
        assert len(result.architecture_tree_str) > 0
        assert "System" in result.architecture_tree_str

    def test_compile_to_file(self):
        """Test compiling to output files."""
        source = """Goal:
File output test

Layer:
Core

Validation:
Files created
"""
        compiler = Compiler()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "output")
            result = compiler.compile_to_file(source, output_dir)

            assert result.success
            assert os.path.exists(os.path.join(output_dir, "main.py"))
            assert os.path.exists(os.path.join(output_dir, "test_main.py"))
            assert os.path.exists(os.path.join(output_dir, "architecture_tree.txt"))

    def test_compile_multiple_risks(self):
        """Test compiling a program with multiple risks and recoveries."""
        source = """Goal:
Robust app

Risk:
Network failure

Recovery:
Retry connection

Risk:
Disk full

Recovery:
Clean cache

Layer:
Core

Validation:
App runs
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success
        assert "Network failure" in result.source_code
        assert "Disk full" in result.source_code

    def test_compile_with_conditions(self):
        """Test compiling a program with Condition sections."""
        source = """Goal:
Interactive app

Layer:
UI

Condition:
    When user disconnected
    Then reconnect

Validation:
Works
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success
        assert "handle_condition" in result.source_code

    def test_compile_with_events(self):
        """Test compiling a program with Event sections."""
        source = """Goal:
Event-driven app

Layer:
Core

Event:
    On click
    Action:
    open menu

Validation:
Works
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success, f"Compilation failed: {result.errors}"
        assert "handle_event" in result.source_code

    def test_compilation_stages(self):
        """Test that all compilation stages are completed."""
        source = """Goal:
Test

Layer:
Core

Validation:
Works
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success
        expected_stages = [
            "Specification Parsing",
            "Architecture Validation",
            "Dependency Analysis",
            "Risk Analysis",
            "Recovery Synthesis",
            "Code Generation",
            "Test Generation",
            "Optimization",
            "Final Construction",
        ]
        for stage in expected_stages:
            assert stage in result.stages_completed, f"Stage '{stage}' not completed"

    def test_generated_python_is_syntactically_valid(self):
        """Test that generated Python code is syntactically valid."""
        source = """Goal:
Syntax test

Constraint:
Must be valid Python

Risk:
Import error

Recovery:
Use fallback

Layer:
Initialization

Layer:
Runtime

Entity Player
    name: string
    score: integer

Validation:
Code is valid

Validation:
Runs correctly
"""
        compiler = Compiler()
        result = compiler.compile(source)

        assert result.success, f"Compilation failed: {result.errors}"

        try:
            compile(result.source_code, '<generated>', 'exec')
        except SyntaxError as e:
            print("Generated code:")
            print(result.source_code)
            raise AssertionError(f"Generated Python code has syntax error: {e}")


# =============================================================================
# End-to-End Tests with Example Programs
# =============================================================================

class TestEndToEnd:
    """End-to-end tests using example AICL programs."""

    EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')

    def _load_example(self, name):
        """Load an example AICL file."""
        path = os.path.join(self.EXAMPLES_DIR, name)
        if not os.path.exists(path):
            self.skipTest(f"Example file not found: {path}")
        with open(path, 'r') as f:
            return f.read()

    def test_compile_blue_square(self):
        """Test compiling the Blue Square example."""
        source = self._load_example('blue_square.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Blue Square compilation failed: {result.errors}"
        assert "class" in result.source_code

    def test_compile_pong(self):
        """Test compiling the Pong example."""
        source = self._load_example('pong.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Pong compilation failed: {result.errors}"

    def test_compile_chat(self):
        """Test compiling the Chat example."""
        source = self._load_example('chat.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Chat compilation failed: {result.errors}"

    def test_compile_chess(self):
        """Test compiling the Chess example."""
        source = self._load_example('chess.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Chess compilation failed: {result.errors}"

    def test_pong_generated_code_is_valid_python(self):
        """Test that the Pong example generates valid Python."""
        source = self._load_example('pong.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        try:
            compile(result.source_code, '<pong>', 'exec')
        except SyntaxError as e:
            print("Generated Pong code:")
            print(result.source_code)
            raise AssertionError(f"Pong generated code has syntax error: {e}")

    def test_chat_generated_code_is_valid_python(self):
        """Test that the Chat example generates valid Python."""
        source = self._load_example('chat.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        try:
            compile(result.source_code, '<chat>', 'exec')
        except SyntaxError as e:
            print("Generated Chat code:")
            print(result.source_code)
            raise AssertionError(f"Chat generated code has syntax error: {e}")

    def test_chess_generated_code_is_valid_python(self):
        """Test that the Chess example generates valid Python."""
        source = self._load_example('chess.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        try:
            compile(result.source_code, '<chess>', 'exec')
        except SyntaxError as e:
            print("Generated Chess code:")
            print(result.source_code)
            raise AssertionError(f"Chess generated code has syntax error: {e}")

    def test_blue_square_generated_code_is_valid_python(self):
        """Test that the Blue Square example generates valid Python."""
        source = self._load_example('blue_square.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        try:
            compile(result.source_code, '<blue_square>', 'exec')
        except SyntaxError as e:
            print("Generated Blue Square code:")
            print(result.source_code)
            raise AssertionError(f"Blue Square generated code has syntax error: {e}")


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
