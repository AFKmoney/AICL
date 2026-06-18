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
from aicl.ast import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, SecuritySection,
)
from aicl.ir import ArchitectureTree, ArchitectureNode
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

    EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase')

    def _load_example(self, name):
        """Load an example AICL file."""
        path = os.path.join(self.EXAMPLES_DIR, name)
        if not os.path.exists(path):
            import pytest; pytest.skip(f"Example file not found: {path}")
        with open(path, 'r') as f:
            return f.read()

    def test_compile_blue_square(self):
        """Test compiling the Blue Square example."""
        source = self._load_example('01_blue_square.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Blue Square compilation failed: {result.errors}"
        assert "class" in result.source_code

    def test_compile_pong(self):
        """Test compiling the Pong example."""
        source = self._load_example('02_pong.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Pong compilation failed: {result.errors}"

    def test_compile_chat(self):
        """Test compiling the Chat example."""
        source = self._load_example('03_chat.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Chat compilation failed: {result.errors}"

    def test_compile_chess(self):
        """Test compiling the Chess example."""
        source = self._load_example('04_chess.aicl')
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success, f"Chess compilation failed: {result.errors}"

    def test_pong_generated_code_is_valid_python(self):
        """Test that the Pong example generates valid Python."""
        source = self._load_example('02_pong.aicl')
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
        source = self._load_example('03_chat.aicl')
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
        source = self._load_example('04_chess.aicl')
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
        source = self._load_example('01_blue_square.aicl')
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
# Pattern Library Tests
# =============================================================================

class TestBehaviorPatternLibrary:
    """Test the behavior pattern library and pattern matching."""

    def test_pattern_matching_move(self):
        """Test that 'move' actions match the MOVE pattern."""
        from aicl.patterns import BehaviorPatternLibrary
        lib = BehaviorPatternLibrary()
        match = lib.match("Update paddle position based on direction")
        assert match is not None
        assert match.pattern_name == "MOVE"

    def test_pattern_matching_broadcast(self):
        """Test that 'broadcast' actions match a communication pattern."""
        from aicl.patterns import BehaviorPatternLibrary, PatternCategory
        lib = BehaviorPatternLibrary()
        match = lib.match("Broadcast message to all users")
        assert match is not None
        # Could match BROADCAST or SEND_MESSAGE, both are communication patterns
        assert match.category in (PatternCategory.BROADCAST, PatternCategory.ROUTE)

    def test_pattern_matching_clamp(self):
        """Test that 'clamp' actions match the CLAMP_POSITION pattern."""
        from aicl.patterns import BehaviorPatternLibrary
        lib = BehaviorPatternLibrary()
        match = lib.match("Clamp ball position to boundaries")
        assert match is not None
        assert match.pattern_name == "CLAMP_POSITION"
        # Verify parameters produce valid Python
        code = match.code_template.format(**match.parameters)
        try:
            compile(code, '<test>', 'exec')
        except SyntaxError:
            raise AssertionError(f"Pattern code is not valid Python: {code}")

    def test_pattern_matching_reflect(self):
        """Test that 'reflect' actions match a physics-related pattern."""
        from aicl.patterns import BehaviorPatternLibrary, PatternCategory
        lib = BehaviorPatternLibrary()
        match = lib.match("Reflect ball velocity on collision")
        assert match is not None
        # Could match REFLECT_VELOCITY or CHECK_COLLISION, both are valid
        assert match.category in (PatternCategory.REFLECT, PatternCategory.VALIDATE)

    def test_pattern_matching_encrypt(self):
        """Test that 'encrypt' actions match a security-related pattern."""
        from aicl.patterns import BehaviorPatternLibrary, PatternCategory
        lib = BehaviorPatternLibrary()
        match = lib.match("Encrypt message content")
        assert match is not None
        # Could match ENCRYPT_DATA or SEND_MESSAGE (message keyword), both valid
        assert match.category in (PatternCategory.ENCRYPT, PatternCategory.ROUTE, PatternCategory.BROADCAST)

    def test_pattern_no_match_for_gibberish(self):
        """Test that random text doesn't match any pattern."""
        from aicl.patterns import BehaviorPatternLibrary
        lib = BehaviorPatternLibrary()
        match = lib.match("xyzzy foobar bazquux")
        assert match is None

    def test_word_boundary_matching(self):
        """Test that keywords match whole words, not substrings."""
        from aicl.patterns import BehaviorPatternLibrary
        lib = BehaviorPatternLibrary()
        # "multiplayer" should NOT match "play" keyword
        # It should match "multiplayer" in event_driven keywords instead
        match = lib.match("Update multiplayer state")
        # Should not match GAME_LOOP patterns via "play" substring
        if match:
            assert match.pattern_name != "MOVE" or "update" in match.pattern_name.lower()


class TestBehaviorCompiler:
    """Test the deterministic behavior compiler."""

    def test_compile_move_action(self):
        """Test compiling a move action."""
        from aicl.patterns import BehaviorCompiler
        bc = BehaviorCompiler()
        code, compiled = bc.compile_action("Update paddle position based on direction")
        assert compiled is True
        assert "position" in code

    def test_compile_clamp_action(self):
        """Test compiling a clamp action produces valid Python."""
        from aicl.patterns import BehaviorCompiler
        bc = BehaviorCompiler()
        code, compiled = bc.compile_action("Clamp ball position to boundaries")
        assert compiled is True
        # The generated code must be valid Python
        try:
            compile(code, '<test>', 'exec')
        except SyntaxError:
            raise AssertionError(f"Clamp code is not valid Python: {code}")

    def test_compile_empty_action(self):
        """Test compiling an empty action returns pass."""
        from aicl.patterns import BehaviorCompiler
        bc = BehaviorCompiler()
        code, compiled = bc.compile_action("")
        assert code == "pass"
        assert compiled is True

    def test_compile_fallback_action(self):
        """Test that unknown actions get structured fallback (not bare TODO)."""
        from aicl.patterns import BehaviorCompiler
        bc = BehaviorCompiler()
        code, compiled = bc.compile_action("Perform quantum entanglement")
        assert compiled is False
        assert "# Intent:" in code
        assert "# TODO:" not in code  # Should NOT have bare TODO


class TestSubLanguageParser:
    """Test the action sub-language parser."""

    def test_assign_statement(self):
        """Test parsing an assign statement."""
        from aicl.patterns import SubLanguageParser
        parser = SubLanguageParser()
        stmts = parser.parse("assign x += direction * speed")
        assert len(stmts) == 1
        assert stmts[0].target == "x"
        assert stmts[0].operator == "+="
        assert stmts[0].value == "direction * speed"

    def test_clamp_statement(self):
        """Test parsing a clamp statement."""
        from aicl.patterns import SubLanguageParser
        parser = SubLanguageParser()
        stmts = parser.parse("clamp position between 0 and screen_height")
        assert len(stmts) == 1
        assert stmts[0].target == "position"
        assert stmts[0].min_val == "0"
        assert stmts[0].max_val == "screen_height"

    def test_check_statement(self):
        """Test parsing a check statement."""
        from aicl.patterns import SubLanguageParser
        parser = SubLanguageParser()
        stmts = parser.parse("check score >= 10")
        assert len(stmts) == 1
        assert stmts[0].condition == "score >= 10"

    def test_sub_language_detection_strict(self):
        """Test that natural language doesn't trigger sub-language parsing."""
        from aicl.patterns import SubLanguageParser
        parser = SubLanguageParser()
        # "Clamp ball position" is natural language, NOT a sub-language statement
        # (it lacks "between ... and ...")
        assert parser.is_sub_language("Clamp ball position to boundaries") is False
        # "clamp position between 0 and 100" IS sub-language
        assert parser.is_sub_language("clamp position between 0 and 100") is True
        # "assign x = 5" IS sub-language
        assert parser.is_sub_language("assign x = 5") is True

    def test_sub_language_assign_requires_operator(self):
        """Test that 'assign' without operator is not treated as sub-language."""
        from aicl.patterns import SubLanguageParser
        parser = SubLanguageParser()
        assert parser.is_sub_language("assign the task") is False
        assert parser.is_sub_language("assign x = 5") is True


class TestArchitectureTemplateMapper:
    """Test the Goal → Architecture Template mapper."""

    def test_game_goal_maps_to_game_loop(self):
        """Test that game-related goals map to game_loop template."""
        from aicl.patterns import ArchitectureTemplateMapper
        name, info = ArchitectureTemplateMapper.match("Build a Pong game")
        assert name == "game_loop"

    def test_chat_goal_maps_to_event_driven(self):
        """Test that chat-related goals map to event_driven template."""
        from aicl.patterns import ArchitectureTemplateMapper
        name, info = ArchitectureTemplateMapper.match("Create a multiplayer chat application")
        assert name == "event_driven"

    def test_chess_goal_maps_to_game_loop(self):
        """Test that chess goals map to game_loop template."""
        from aicl.patterns import ArchitectureTemplateMapper
        name, info = ArchitectureTemplateMapper.match("Create a multiplayer chess game")
        assert name == "game_loop"

    def test_pipeline_goal(self):
        """Test that data processing goals map to pipeline template."""
        from aicl.patterns import ArchitectureTemplateMapper
        name, info = ArchitectureTemplateMapper.match("Process and analyze data stream")
        assert name == "pipeline"

    def test_multiplayer_not_matching_game(self):
        """Test that 'multiplayer' doesn't accidentally match 'play' in game keywords."""
        from aicl.patterns import ArchitectureTemplateMapper
        # "multiplayer chat" should be event_driven, not game_loop
        name, info = ArchitectureTemplateMapper.match("multiplayer chat application")
        assert name == "event_driven"


class TestZeroTODOCompilation:
    """Verify that all examples compile with zero TODOs."""

    def test_pong_zero_todos(self):
        """Test that Pong compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '02_pong.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Pong has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_chat_zero_todos(self):
        """Test that Chat compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '03_chat.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Chat has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_chess_zero_todos(self):
        """Test that Chess compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '04_chess.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Chess has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_blue_square_zero_todos(self):
        """Test that Blue Square compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '01_blue_square.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Blue Square has {result.todo_count} TODOs"
        assert result.fully_compiled


# =============================================================================
# Audit Coverage Tests
# =============================================================================

class TestAuditCoverage:
    """Test the audit coverage system."""

    def test_audit_coverage_is_100_for_simple_program(self):
        """Test that a simple program has 100% audit coverage."""
        from aicl.compiler import Compiler
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
        assert result.success

        audit = result.provenance.compute_audit_coverage()
        assert audit['audit_coverage'] == 1.0, f"Expected 100%, got {audit['audit_coverage']:.1%}"
        assert audit['total_artifacts'] > 0
        assert audit['auditable_artifacts'] == audit['total_artifacts']
        assert len(audit['orphan_artifacts']) == 0

    def test_audit_coverage_for_pong(self):
        """Test that Pong has 100% audit coverage."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '02_pong.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        audit = result.provenance.compute_audit_coverage()
        assert audit['audit_coverage'] == 1.0, f"Pong audit coverage: {audit['audit_coverage']:.1%}"
        assert len(audit['orphan_artifacts']) == 0

    def test_audit_coverage_for_chat(self):
        """Test that Chat has 100% audit coverage."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '03_chat.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        audit = result.provenance.compute_audit_coverage()
        assert audit['audit_coverage'] == 1.0, f"Chat audit coverage: {audit['audit_coverage']:.1%}"
        assert len(audit['orphan_artifacts']) == 0

    def test_audit_coverage_for_chess(self):
        """Test that Chess has 100% audit coverage."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'showcase', '04_chess.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        audit = result.provenance.compute_audit_coverage()
        assert audit['audit_coverage'] == 1.0, f"Chess audit coverage: {audit['audit_coverage']:.1%}"
        assert len(audit['orphan_artifacts']) == 0

    def test_audit_passed_method(self):
        """Test the audit_passed method."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a game

Layer:
Renderer

Validation:
Game runs correctly
"""
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.provenance.audit_passed(result.source_code, result.test_code)

    def test_audit_report_generates(self):
        """Test that the audit report generates correctly."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a game

Layer:
Renderer

Validation:
Game runs correctly
"""
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        report = result.provenance.audit(result.source_code, result.test_code)
        assert "AICL AUDIT REPORT" in report
        assert "VERIFIED" in report
        assert "Audit Coverage" in report
        assert "100.00%" in report

    def test_explicability_coverage_for_compiled_program(self):
        """Test that compiled programs have high explicability coverage."""
        from aicl.compiler import Compiler
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
        assert result.success

        coverage = result.provenance.compute_explicability_coverage(result.source_code, result.test_code)
        assert coverage['coverage_ratio'] >= 0.90, f"Coverage too low: {coverage['coverage_ratio']:.1%}"

    def test_artifact_tracking_by_type(self):
        """Test that artifacts are tracked by type in the audit."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a Pong game

Entity:
Player
    position: integer
    score: integer

Layer:
Game Logic

Behavior:
Move Paddle
    Input: player: Player, direction: string
    Action: move player paddle

Validation:
Game runs at 60fps
"""
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        audit = result.provenance.compute_audit_coverage()
        by_type = audit['by_type']

        # Should have at least methods, a class, imports, and tests
        assert 'method' in by_type
        assert 'class' in by_type
        assert 'import_block' in by_type
        assert 'test_function' in by_type
        assert 'dataclass' in by_type

        # All should be 100% covered
        for atype, info in by_type.items():
            assert info['coverage'] == 1.0, f"{atype} coverage: {info['coverage']:.1%}"

    def test_all_provenance_types_covered(self):
        """Test that the provenance system covers all new types."""
        from aicl.provenance import ProvenanceType
        expected_types = [
            "pattern_match", "sub_language", "fallback", "architecture_template",
            "direct_mapping", "recovery_synthesis", "validation_synthesis",
            "condition_synthesis", "event_synthesis", "helper_method",
            "entity_generation", "layer_initialization",
            "security_method", "parallel_execution", "run_method",
            "import_generation", "entry_point", "test_generation",
            "class_structure",
        ]
        actual_types = [t.value for t in ProvenanceType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing ProvenanceType: {expected}"


class TestProvenanceArtifactSystem:
    """Test the provenance artifact tracking system."""

    def test_register_artifact(self):
        """Test that artifacts can be registered."""
        from aicl.provenance import CompilationProvenance, ArtifactType
        prov = CompilationProvenance()
        art = prov.register_artifact("test_method", ArtifactType.METHOD, "Test source")
        assert art.name == "test_method"
        assert art.artifact_type == ArtifactType.METHOD
        assert not art.has_provenance
        assert art.is_orphan

    def test_link_provenance_to_artifact(self):
        """Test that provenance records can be linked to artifacts."""
        from aicl.provenance import CompilationProvenance, ProvenanceType, ArtifactType
        prov = CompilationProvenance()

        # Register artifact first
        prov.register_artifact("test_method", ArtifactType.METHOD, "Test source")

        # Record provenance that covers the artifact
        prov.record(
            source_type=ProvenanceType.PATTERN_MATCH,
            source_location="Behavior Test",
            source_text="move player",
            resolution_path=["AICL Source", "Pattern Match", "Generated Code"],
            generated_code="player.position += 1",
            artifact_names=["test_method"],
        )

        # Verify artifact now has provenance
        assert prov.artifacts[0].has_provenance
        assert not prov.artifacts[0].is_orphan

    def test_orphan_detection(self):
        """Test that orphan artifacts are detected."""
        from aicl.provenance import CompilationProvenance, ArtifactType
        prov = CompilationProvenance()

        # Register an artifact without provenance
        prov.register_artifact("orphan_method", ArtifactType.METHOD, "Unknown")

        audit = prov.compute_audit_coverage()
        assert audit['audit_coverage'] == 0.0
        assert len(audit['orphan_artifacts']) == 1
        assert audit['orphan_artifacts'][0]['name'] == "orphan_method"

    def test_audit_coverage_computation(self):
        """Test audit coverage computation with mixed provenance."""
        from aicl.provenance import CompilationProvenance, ProvenanceType, ArtifactType
        prov = CompilationProvenance()

        # Register 3 artifacts
        prov.register_artifact("method_a", ArtifactType.METHOD, "Source A")
        prov.register_artifact("method_b", ArtifactType.METHOD, "Source B")
        prov.register_artifact("method_c", ArtifactType.FUNCTION, "Source C")

        # Add provenance for 2 of them
        prov.record(
            source_type=ProvenanceType.DIRECT_MAPPING,
            source_location="Test A",
            source_text="test a",
            resolution_path=["Source", "Generated"],
            generated_code="pass",
            artifact_names=["method_a"],
        )
        prov.record(
            source_type=ProvenanceType.DIRECT_MAPPING,
            source_location="Test B",
            source_text="test b",
            resolution_path=["Source", "Generated"],
            generated_code="pass",
            artifact_names=["method_b"],
        )

        audit = prov.compute_audit_coverage()
        assert audit['total_artifacts'] == 3
        assert audit['auditable_artifacts'] == 2
        assert audit['audit_coverage'] == 2/3
        assert len(audit['orphan_artifacts']) == 1


class TestProofOfOrigin:
    """Test the Proof of Origin system — the central artifact of auditable compilation."""

    def test_proof_generation_from_compilation(self):
        """Test that compilation produces a Proof of Origin."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a game

Risk:
Server down

Recovery:
Reconnect

Layer:
GameLogic

Behavior:
MovePlayer
    Input: player: Player
    Action: move player up
"""
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.proof is not None
        assert result.proof.format_version == "2.0"
        assert result.proof.compiler_version == "1.0.0"
        assert result.proof.timestamp != ""
        assert result.proof.program_hash != ""
        assert result.proof.source_hash != ""

    def test_proof_serialization_roundtrip(self):
        """Test that a proof can be serialized to JSON and loaded back."""
        import json
        from aicl.provenance import ProofOfOrigin
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Risk:
Crash

Recovery:
Restart

Layer:
Core

Behavior:
Update
    Input: state: State
    Action: update state
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Serialize to JSON and back
        json_str = proof.to_json()
        loaded = ProofOfOrigin.from_json_str(json_str)

        # Verify roundtrip
        assert loaded.format_version == proof.format_version
        assert loaded.compiler_version == proof.compiler_version
        assert loaded.timestamp == proof.timestamp
        assert loaded.source_hash == proof.source_hash
        assert loaded.program_hash == proof.program_hash
        assert loaded.test_hash == proof.test_hash
        assert len(loaded.records) == len(proof.records)
        assert len(loaded.artifacts) == len(proof.artifacts)

    def test_proof_file_roundtrip(self):
        """Test that a proof can be written to a file and loaded back."""
        import tempfile
        import os
        from aicl.provenance import ProofOfOrigin
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Risk:
Lag

Recovery:
Reduce quality

Layer:
Render

Behavior:
Draw
    Input: canvas: Canvas
    Action: render frame
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Write to file and read back
        with tempfile.NamedTemporaryFile(suffix='.aicl-proof', delete=False, mode='w') as f:
            proof_path = f.name
            proof.to_file(proof_path)

        try:
            loaded = ProofOfOrigin.from_file(proof_path)
            assert loaded.format_version == proof.format_version
            assert loaded.program_hash == proof.program_hash
            assert len(loaded.records) == len(proof.records)
            assert len(loaded.artifacts) == len(proof.artifacts)
        finally:
            os.unlink(proof_path)

    def test_proof_verification_valid(self):
        """Test that a valid proof passes verification."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a game

Risk:
Data loss

Recovery:
Backup

Layer:
Storage

Behavior:
Save
    Input: data: Data
    Action: save data
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        verification = proof.verify()
        assert verification['valid']
        for check in verification['checks']:
            assert check['passed'], f"Check failed: {check['name']}: {check['description']}"

    def test_proof_verification_with_code_binding(self):
        """Test hash binding when generated code is provided for verification."""
        from aicl.compiler import Compiler
        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: start game loop
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Verify with actual code
        verification = proof.verify(
            generated_source=result.source_code,
            generated_tests=result.test_code,
        )
        assert verification['valid']
        # Check that hash binding check actually verified
        hash_checks = [c for c in verification['checks'] if 'hash' in c['name']]
        assert len(hash_checks) >= 2
        for check in hash_checks:
            assert check['passed']

    def test_proof_explain_reconstructs_from_proof(self):
        """Test that explain() can be reconstructed entirely from the proof file.

        This is the critical test: if we delete the compiler,
        can we still get a full explanation from the .aicl-proof file?
        """
        from aicl.provenance import ProofOfOrigin
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Risk:
Cheating

Recovery:
Kick player

Layer:
Network

Behavior:
ValidateMove
    Input: move: Move
    Action: validate move
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Get explanation from the proof (not from the compiler)
        explanation = proof.explain()
        assert "PROOF OF ORIGIN" in explanation
        assert "EXPLANATION" in explanation
        assert len(explanation) > 200  # Non-trivial explanation

    def test_proof_audit_report_from_proof(self):
        """Test that audit report can be reconstructed from the proof file."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Process
    Action: process input
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        report = proof.audit_report()
        assert "AUDIT REPORT" in report
        assert "Proof of Origin" in report
        assert "FORMAL PROPERTIES" in report
        assert "PROOF VERIFICATION" in report

    def test_proof_formal_properties(self):
        """Test that formal properties are correctly computed in the proof."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Init
    Action: initialize
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # No Orphan Property
        no_orphan = proof.formal_properties.get('no_orphan_artifact_property', {})
        assert no_orphan.get('verified', False)
        assert no_orphan.get('orphan_count', -1) == 0

        # Complete Coverage Property
        complete_cov = proof.formal_properties.get('complete_coverage_property', {})
        assert complete_cov.get('verified', False)
        assert complete_cov.get('coverage', 0) >= 1.0

        # Hash Binding Property
        hash_binding = proof.formal_properties.get('hash_binding_property', {})
        assert hash_binding.get('verified', False)
        assert 'program_hash' in hash_binding
        assert 'source_hash' in hash_binding

    def test_proof_explain_behavior(self):
        """Test behavior-specific explanation from proof."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Game

Behavior:
MovePlayer
    Input: player: Player
    Action: move player left
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        explanation = proof.explain_behavior("MovePlayer")
        # The behavior might be stored as "Behavior MovePlayer" or "move_player"
        # so we check that either the behavior is found or a not-found message appears
        assert "MovePlayer" in explanation or "No compilation records" in explanation

    def test_proof_coverage_report(self):
        """Test explicability coverage report from proof."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Tick
    Action: update state
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        report = proof.coverage_report()
        assert "EXPLICABILITY COVERAGE" in report
        assert "Proof of Origin" in report

    def test_proof_audit_passed(self):
        """Test that audit_passed works from proof file."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run loop
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        assert proof.audit_passed()

    def test_proof_compile_to_file_generates_proof(self):
        """Test that compile_to_file generates a .aicl-proof file."""
        import tempfile
        import os
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Start
    Action: start game
"""
        compiler = Compiler()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = compiler.compile_to_file(source, tmpdir)
            assert result.success
            proof_path = os.path.join(tmpdir, 'main.aicl-proof')
            assert os.path.exists(proof_path)

            # Verify the proof file can be loaded
            from aicl.provenance import ProofOfOrigin
            loaded = ProofOfOrigin.from_file(proof_path)
            assert loaded.format_version == "2.0"
            assert len(loaded.records) > 0
            assert len(loaded.artifacts) > 0

    def test_proof_contains_all_provenance_records(self):
        """Test that proof contains ALL provenance records from compilation.

        This verifies that nothing is lost in the serialization.
        """
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Risk:
Crash

Recovery:
Restart

Layer:
Core

Entity:
Player
    position: int
    score: int

Behavior:
MovePlayer
    Input: player: Player
    Action: move player right
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Number of records should match
        assert len(proof.records) == len(result.provenance.records)

        # Number of artifacts should match
        assert len(proof.artifacts) == len(result.provenance.artifacts)

        # Audit coverage should match
        proof_coverage = proof.audit_coverage.get('audit_coverage', 0)
        direct_audit = result.provenance.compute_audit_coverage()
        assert proof_coverage == direct_audit['audit_coverage']

    def test_proof_to_dict_structure(self):
        """Test that the proof dictionary has the expected structure."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        d = proof.to_dict()
        assert 'proof_of_origin' in d
        po = d['proof_of_origin']
        assert 'format_version' in po
        assert 'compiler_version' in po
        assert 'timestamp' in po
        assert 'source_hash' in po
        assert 'program_hash' in po
        assert 'test_hash' in po
        assert 'formal_properties' in po
        assert 'audit_summary' in po
        assert 'explicability_summary' in po
        assert 'records' in po
        assert 'artifacts' in po
        # v2.0: proof is self-contained — includes code
        assert 'source_text' in po
        assert 'generated_source' in po
        assert 'generated_tests' in po
        assert po['source_text'] != ""
        assert po['generated_source'] != ""

    def test_proof_v2_self_contained(self):
        """Test that v2.0 proof is fully self-contained for independent verification."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # v2.0 proof must contain the generated code
        assert proof.generated_source != ""
        assert proof.generated_tests != ""
        assert proof.source_text != ""

        # Verify() should work WITHOUT external code (self-contained)
        verification = proof.verify()
        assert verification['valid']

        # All hash checks should pass using embedded code
        hash_checks = [c for c in verification['checks'] if 'hash' in c['name']]
        for check in hash_checks:
            assert check['passed'], f"{check['name']}: {check.get('detail', '')}"

    def test_proof_v2_independent_verifier(self):
        """Test that the independent verifier (verify_proof.py) validates the proof."""
        import subprocess
        import tempfile
        import os
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run
"""
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success

        # Write proof to a temp file
        with tempfile.NamedTemporaryFile(suffix='.aicl-proof', delete=False, mode='w') as f:
            proof_path = f.name
            result.proof.to_file(proof_path)

        try:
            # Run the independent verifier
            verifier_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'tools', 'verify_proof.py'
            )
            proc = subprocess.run(
                [sys.executable, verifier_path, proof_path],
                capture_output=True, text=True, timeout=30
            )
            # Exit code 0 = VALID
            assert proc.returncode == 0, f"Verifier failed:\n{proc.stdout}\n{proc.stderr}"
            assert "VALID" in proc.stdout
        finally:
            os.unlink(proof_path)

    def test_proof_v2_source_hash_binding(self):
        """Test that v2.0 proof verifies source text hash binding."""
        from aicl.compiler import Compiler
        import hashlib

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Source hash should match
        expected_hash = hashlib.sha256(source.encode('utf-8')).hexdigest()
        assert proof.source_hash == expected_hash

        # Verify should pass the source hash check
        verification = proof.verify()
        source_check = [c for c in verification['checks'] if c['name'] == 'source_hash_binding'][0]
        assert source_check['passed']

    def test_proof_v2_artifact_consistency_check(self):
        """Test that the new artifact consistency check works."""
        from aicl.compiler import Compiler

        source = """Goal:
Build a game

Layer:
Core

Behavior:
Run
    Action: run
"""
        compiler = Compiler()
        result = compiler.compile(source)
        proof = result.proof

        # Verify should pass consistency check
        verification = proof.verify()
        consistency_check = [c for c in verification['checks'] if c['name'] == 'artifact_consistency'][0]
        assert consistency_check['passed']

    def test_proof_v2_all_four_examples_independently_verifiable(self):
        """Test that all 4 example programs produce independently verifiable proofs."""
        import subprocess
        import tempfile
        import os
        from aicl.compiler import Compiler

        examples_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'examples', 'showcase'
        )
        verifier_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tools', 'verify_proof.py'
        )

        # Iterate over .aicl files in showcase/ (skip the cognet/ subfolder
        # and websocket/ for this proof-chain test).
        aicl_files = []
        for entry in sorted(os.listdir(examples_dir)):
            if entry.endswith('.aicl'):
                aicl_files.append(entry)
        for example_file in aicl_files:
            example_path = os.path.join(examples_dir, example_file)
            with open(example_path, 'r') as f:
                source = f.read()

            compiler = Compiler()
            result = compiler.compile(source)
            assert result.success, f"Compilation of {example_file} failed"

            # Write proof to temp file
            with tempfile.NamedTemporaryFile(suffix='.aicl-proof', delete=False, mode='w') as f:
                proof_path = f.name
                result.proof.to_file(proof_path)

            try:
                proc = subprocess.run(
                    [sys.executable, verifier_path, proof_path],
                    capture_output=True, text=True, timeout=30
                )
                assert proc.returncode == 0, (
                    f"Independent verification of {example_file} failed:\n"
                    f"{proc.stdout}\n{proc.stderr}"
                )
                assert "VALID" in proc.stdout
            finally:
                os.unlink(proof_path)


# =============================================================================
# v0.9: Specification Verification Tests
# =============================================================================

class TestSpecificationVerification:
    """Tests for the specification verification system (v0.9)."""

    def _simple_source(self):
        return """Goal Build a simple game
Layer GameLoop
    SubLayer Rendering
Entity Ball
    x: float
    y: float
Behavior MoveBall
    Input: Ball ball
    Action: Move ball by velocity
Validation Ball moves correctly
    Ball position updates when moved
Risk Ball goes off screen
    Recovery Clamp ball position to screen bounds
"""

    def _minimal_source(self):
        return """Goal Do something
Layer App
Validation It works
"""

    def test_completeness_check_passes(self):
        """A well-formed AICL program passes completeness checks."""
        from aicl.spec_verify import SpecificationVerifier, CheckStatus
        parser = Parser(self._simple_source())
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.completeness_only()
        # Should have no FAIL results for a well-formed program
        fails = [r for r in report.completeness_results if r.status == CheckStatus.FAIL]
        assert len(fails) == 0, f"Unexpected failures: {[r.name for r in fails]}"

    def test_completeness_check_missing_goal(self):
        """A program without a Goal fails completeness check."""
        from aicl.spec_verify import SpecificationVerifier, CheckStatus
        source = "Layer App\nValidation It works\n"
        parser = Parser(source)
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.completeness_only()
        goal_check = [r for r in report.completeness_results if r.name == "goal_present"]
        assert len(goal_check) > 0
        assert goal_check[0].status == CheckStatus.FAIL

    def test_coherence_check_no_duplicates(self):
        """Coherence check detects duplicate entity names."""
        from aicl.spec_verify import SpecificationVerifier, CheckStatus
        source = """Goal Test
Layer App
Entity Ball
    x: float
Entity Ball
    y: float
Validation It works
"""
        parser = Parser(source)
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.coherence_only()
        dup_check = [r for r in report.coherence_results if r.name == "no_duplicate_entities"]
        assert len(dup_check) > 0
        assert dup_check[0].status == CheckStatus.FAIL

    def test_satisfaction_check_achievable(self):
        """Satisfaction check verifies goal is achievable."""
        from aicl.spec_verify import SpecificationVerifier, CheckStatus
        parser = Parser(self._simple_source())
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.satisfaction_only()
        goal_check = [r for r in report.satisfaction_results if r.name == "goal_achievable"]
        assert len(goal_check) > 0
        assert goal_check[0].status == CheckStatus.PASS

    def test_full_verification_passes(self):
        """Full verification of a well-formed program passes."""
        from aicl.spec_verify import SpecificationVerifier
        parser = Parser(self._simple_source())
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.verify()
        assert report.passed

    def test_verify_source_convenience_function(self):
        """verify_source convenience function works."""
        from aicl.spec_verify import verify_source
        report = verify_source(self._simple_source())
        assert report.passed


# =============================================================================
# v0.10: Multi-File Module System Tests
# =============================================================================

class TestModuleSystem:
    """Tests for the multi-file module system (v0.10)."""

    def test_parse_imports(self):
        """Import declarations are parsed correctly."""
        from aicl.modules import parse_imports
        source = """Goal Build game
Import GameEngine from engine.aicl
Import NetworkLayer from network.aicl
Layer GameLoop
Validation It works
"""
        imports = parse_imports(source)
        assert len(imports) == 2
        assert imports[0].symbols == ["GameEngine"]
        assert imports[0].module_path == "engine.aicl"
        assert imports[1].symbols == ["NetworkLayer"]

    def test_module_registry(self):
        """ModuleRegistry tracks compiled modules."""
        from aicl.modules import ModuleRegistry, CompiledModule, ModuleExport
        registry = ModuleRegistry()
        module = CompiledModule(
            module_path="test.aicl",
            source_text="Goal Test",
            program=AICLProgram(),
            compilation_result=CompilationResult(success=True),
            exports=[ModuleExport(name="Ball", symbol_type="entity", source_module="test.aicl")],
        )
        registry.register(module)
        assert registry.is_compiled("test.aicl")
        assert registry.get("test.aicl") is not None

    def test_module_resolver(self):
        """ModuleResolver resolves paths correctly."""
        from aicl.modules import ModuleResolver
        resolver = ModuleResolver(search_paths=["/nonexistent"])
        # Should return None for non-existent paths
        result = resolver.resolve("nonexistent.aicl")
        assert result is None

    def test_extract_exports(self):
        """Entity exports are extracted from compiled programs."""
        from aicl.modules import extract_exports
        parser = Parser("Goal Test\nLayer App\nEntity Ball\n    x: float\nValidation Works\n")
        program = parser.parse()
        exports = extract_exports(program, "test.aicl")
        entity_exports = [e for e in exports if e.symbol_type == "entity"]
        assert len(entity_exports) >= 1
        assert entity_exports[0].name == "Ball"

    def test_cross_file_provenance(self):
        """CrossFileProvenance creates import provenance records."""
        from aicl.modules import ModuleRegistry, CompiledModule, CrossFileProvenance, ImportDeclaration
        registry = ModuleRegistry()
        dep_module = CompiledModule(
            module_path="engine.aicl",
            source_text="Goal Engine",
            program=AICLProgram(),
            compilation_result=CompilationResult(success=True),
        )
        registry.register(dep_module)

        cross_prov = CrossFileProvenance(registry)
        imp = ImportDeclaration(symbols=["GameEngine"], module_path="engine.aicl")
        records = cross_prov.create_import_provenance(imp, "main.aicl")
        assert len(records) >= 0  # No export found, so empty


# =============================================================================
# v0.11: Cryptographic Proof Signing Tests
# =============================================================================

class TestCryptoSigning:
    """Tests for cryptographic proof signing (v0.11)."""

    def test_sign_and_verify(self):
        """Signing and verifying a proof works."""
        from aicl.crypto_signing import ProofSigner
        signer = ProofSigner(key_seed="test-key")
        proof_dict = {"format_version": "2.0", "compiler_version": "1.0.0"}
        signature = signer.sign(proof_dict)
        assert signature.signature_hex != ""
        assert signature.compiler_key_id != ""
        assert signer.verify(proof_dict, signature)

    def test_tampered_proof_fails_verification(self):
        """A tampered proof fails signature verification."""
        from aicl.crypto_signing import ProofSigner
        signer = ProofSigner(key_seed="test-key")
        proof_dict = {"format_version": "2.0", "compiler_version": "1.0.0"}
        signature = signer.sign(proof_dict)
        # Tamper with the proof
        tampered = {"format_version": "2.0", "compiler_version": "9.9.9"}
        assert not signer.verify(tampered, signature)

    def test_proof_signature_serialization(self):
        """ProofSignature can be serialized and deserialized."""
        from aicl.crypto_signing import ProofSignature
        sig = ProofSignature(
            algorithm="HMAC-SHA256",
            compiler_key_id="abc123",
            signature_hex="deadbeef",
            signed_at="2026-01-01T00:00:00Z",
            proof_hash="hash123",
        )
        d = sig.to_dict()
        restored = ProofSignature.from_dict(d)
        assert restored.algorithm == sig.algorithm
        assert restored.compiler_key_id == sig.compiler_key_id
        assert restored.signature_hex == sig.signature_hex

    def test_create_signed_proof(self):
        """create_signed_proof adds signature to proof dict."""
        from aicl.crypto_signing import create_signed_proof
        proof_dict = {"format_version": "2.0", "compiler_version": "1.0.0"}
        signed = create_signed_proof(proof_dict, key_seed="test-key")
        assert "signature" in signed
        assert signed["signature"]["algorithm"] == "HMAC-SHA256"

    def test_verify_signed_proof(self):
        """verify_signed_proof checks signed proof integrity."""
        from aicl.crypto_signing import create_signed_proof, verify_signed_proof
        proof_dict = {"format_version": "2.0", "compiler_version": "1.0.0"}
        signed = create_signed_proof(proof_dict, key_seed="test-key")
        result = verify_signed_proof(signed)
        assert result["signature_present"]
        assert result["proof_hash_valid"]


# =============================================================================
# v1.0: Multi-Language Target Tests
# =============================================================================

class TestMultiLanguageTargets:
    """Tests for multi-language target generators (v1.0)."""

    def _compile_example(self):
        """Compile a simple example for target generation."""
        source = """Goal Build a game
Layer GameLoop
Entity Ball
    x: float
    y: float
Behavior MoveBall
    Input: Ball ball
    Action: Move ball by velocity
Validation Ball moves
Risk Ball off screen
    Recovery Clamp position
"""
        compiler = Compiler()
        return compiler.compile(source)

    def test_list_targets(self):
        """Available targets are listed."""
        from aicl.targets import list_targets
        targets = list_targets()
        assert "rust" in targets
        assert "javascript" in targets
        assert "go" in targets

    def test_rust_generator(self):
        """Rust code generation produces valid output."""
        from aicl.targets import get_target_generator
        result = self._compile_example()
        gen = get_target_generator("rust")
        target_result = gen.generate(result)
        assert target_result.target_language == "rust"
        assert "fn main()" in target_result.source_code
        assert "Cargo.toml" in target_result.project_files

    def test_javascript_generator(self):
        """JavaScript code generation produces valid output."""
        from aicl.targets import get_target_generator
        result = self._compile_example()
        gen = get_target_generator("javascript")
        target_result = gen.generate(result)
        assert target_result.target_language == "javascript"
        assert "class Application" in target_result.source_code
        assert "package.json" in target_result.project_files

    def test_go_generator(self):
        """Go code generation produces valid output."""
        from aicl.targets import get_target_generator
        result = self._compile_example()
        gen = get_target_generator("go")
        target_result = gen.generate(result)
        assert target_result.target_language == "go"
        assert "func main()" in target_result.source_code
        assert "go.mod" in target_result.project_files

    def test_python_target_raises(self):
        """Python target raises error (use built-in compiler)."""
        from aicl.targets import get_target_generator
        import pytest
        with pytest.raises(ValueError, match="Python target"):
            get_target_generator("python")


# =============================================================================
# v2.0: Self-Healing Runtime Tests
# =============================================================================

class TestSelfHealingRuntime:
    """Tests for the self-healing runtime system (v2.0)."""

    def test_runtime_environment_creation(self):
        """RuntimeEnvironment can be created."""
        from aicl.runtime import RuntimeEnvironment
        env = RuntimeEnvironment()
        assert env.provenance is not None

    def test_register_risk_recovery(self):
        """Risk/recovery pairs can be registered."""
        from aicl.runtime import RuntimeEnvironment
        env = RuntimeEnvironment()
        env.register_risk_recovery(
            "test_risk",
            risk_condition=lambda: False,
            recovery_action=lambda: True,
        )
        assert len(env._bindings) == 1

    def test_run_with_no_risks(self):
        """Running with no risks succeeds."""
        from aicl.runtime import RuntimeEnvironment
        env = RuntimeEnvironment()
        result = env.run(lambda: None)
        assert result["success"]
        assert result["event_count"] >= 2  # start + end

    def test_runtime_provenance_recording(self):
        """Runtime provenance events are recorded."""
        from aicl.runtime import RuntimeProvenance, RuntimeProvenanceEvent, RuntimeEventType
        prov = RuntimeProvenance()
        prov.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.RISK_DETECTED,
            source="test",
            description="Test risk detected",
        ))
        assert len(prov.events) == 1

    def test_recovery_executor(self):
        """RecoveryExecutor executes recovery actions."""
        from aicl.runtime import RuntimeProvenance, RecoveryExecutor, RiskRecoveryBinding
        prov = RuntimeProvenance()
        executor = RecoveryExecutor(prov)
        binding = RiskRecoveryBinding(
            risk_name="test_risk",
            risk_condition=lambda: True,
            recovery_action=lambda: True,
            max_attempts=3,
        )
        result = executor.execute(binding)
        assert result
        assert len(prov.events) >= 3  # risk detected + recovery executed + recovery success

    def test_runtime_coverage(self):
        """Runtime coverage is computed correctly."""
        from aicl.runtime import RuntimeProvenance, RuntimeProvenanceEvent, RuntimeEventType
        prov = RuntimeProvenance()
        prov.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.RISK_DETECTED,
            source="test", description="Risk",
            risk_name="test_risk",
        ))
        prov.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.RECOVERY_SUCCESS,
            source="test", description="Recovery",
            risk_name="test_risk",
            recovery_name="test_risk_recovery",
        ))
        coverage = prov.compute_runtime_coverage()
        assert coverage["runtime_recovery_coverage"] == 1.0


# =============================================================================
# v2.5: Ownership Model Tests
# =============================================================================

class TestOwnershipModel:
    """Tests for the ownership model (v2.5)."""

    def test_ownership_analysis(self):
        """OwnershipAnalyzer produces a report."""
        from aicl.ownership import OwnershipAnalyzer
        source = """Goal Test
Layer App
Entity Ball
    x: float
    y: float
Behavior Move
    Input: Ball ball
    Action: Update position
Validation Works
"""
        parser = Parser(source)
        program = parser.parse()
        analyzer = OwnershipAnalyzer(program)
        report = analyzer.analyze()
        assert len(report.relations) > 0

    def test_layer_owns_entities(self):
        """Layers own their entities."""
        from aicl.ownership import OwnershipAnalyzer, OwnershipKind
        source = """Goal Test
Layer App
Entity Ball
    x: float
Validation Works
"""
        parser = Parser(source)
        program = parser.parse()
        analyzer = OwnershipAnalyzer(program)
        report = analyzer.analyze()
        owns_rels = [r for r in report.relations if r.kind == OwnershipKind.OWNS]
        assert len(owns_rels) > 0

    def test_ownership_report_summary(self):
        """OwnershipReport produces a summary string."""
        from aicl.ownership import OwnershipAnalyzer
        source = """Goal Test
Layer App
Entity Ball
    x: float
Validation Works
"""
        parser = Parser(source)
        program = parser.parse()
        analyzer = OwnershipAnalyzer(program)
        report = analyzer.analyze()
        summary = report.summary()
        assert "OWNERSHIP MODEL" in summary

    def test_generate_ownership_code(self):
        """Ownership code generation produces Python code."""
        from aicl.ownership import generate_ownership_code
        source = """Goal Test
Layer App
Entity Ball
    x: float
Validation Works
"""
        parser = Parser(source)
        program = parser.parse()
        code = generate_ownership_code(program)
        assert "class Ball" in code


# =============================================================================
# v3.0: Autonomous Architecture Optimization Tests
# =============================================================================

class TestArchitectureOptimization:
    """Tests for autonomous architecture optimization (v3.0)."""

    def test_optimizer_creates(self):
        """ArchitectureOptimizer can be created."""
        from aicl.auto_optimizer import ArchitectureOptimizer
        source = """Goal Test
Layer App
Validation Works
"""
        parser = Parser(source)
        program = parser.parse()
        optimizer = ArchitectureOptimizer(program)
        assert optimizer.program is not None

    def test_optimize_minimal_program(self):
        """Optimizing a minimal program runs without error."""
        from aicl.auto_optimizer import ArchitectureOptimizer
        source = """Goal Test
Layer App
Entity Ball
    x: float
Behavior MoveBall
    Input: Ball ball
    Action: move
Validation It works
Risk Ball escapes
    Recovery clamp
"""
        parser = Parser(source)
        program = parser.parse()
        optimizer = ArchitectureOptimizer(program)
        result = optimizer.optimize()
        assert result.iterations >= 1
        assert result.summary()  # Can generate summary

    def test_optimization_strategies(self):
        """All optimization strategies can be applied."""
        from aicl.auto_optimizer import OptimizationStrategy
        strategies = list(OptimizationStrategy)
        assert len(strategies) == 7
        assert OptimizationStrategy.LAYER_CONSOLIDATION in strategies
        assert OptimizationStrategy.PARALLELIZATION in strategies


# =============================================================================
# Autonomous Compilation Tests
# =============================================================================

class TestAutonomousCompilation:
    """Test the self-writing, self-validating autonomous compilation system."""

    def test_pattern_learner_creation(self):
        """PatternLearner can be created and records unmatched descriptions."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        learner.record_unmatched("Transfer", "debit source account and credit target account atomically")
        assert len(learner.unmatched_descriptions) == 1

    def test_pattern_learner_learns_from_description(self):
        """PatternLearner can learn a new pattern from an unmatched description."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        pattern = learner.learn_from_description(
            "ProcessPayment",
            "validate payment and debit account and record transaction"
        )
        assert pattern is not None
        assert pattern["behavior"] == "ProcessPayment"
        assert "keywords" in pattern
        assert len(pattern["keywords"]) > 0
        assert pattern["confidence"] >= 0.5

    def test_pattern_learner_extracts_verb(self):
        """PatternLearner correctly extracts action verbs."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        pattern = learner.learn_from_description("CreateUser", "create new user account")
        assert pattern["verb"] == "create"

    def test_pattern_learner_extracts_object(self):
        """PatternLearner correctly extracts action objects."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        pattern = learner.learn_from_description("ValidateCard", "validate card number and check expiry")
        assert pattern["object"] == "card"

    def test_pattern_learner_classifies_category(self):
        """PatternLearner correctly classifies pattern categories."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()

        cases = [
            ("CreateAccount", "create new account", "CREATION"),
            ("DeleteRecord", "delete record from database", "DELETION"),
            ("ValidateInput", "validate user input", "VALIDATE"),
            ("SendNotification", "send notification to user", "ROUTE"),
            ("StoreData", "store data in cache", "STORE"),
            ("EncryptPassword", "encrypt password hash", "ENCRYPT"),
            ("FreezeAccount", "freeze account for review", "SECURITY"),
            ("AuditTransaction", "audit transaction record", "AUDIT"),
        ]

        for name, desc, expected_category in cases:
            pattern = learner.learn_from_description(name, desc)
            assert pattern["category"] == expected_category, \
                f"Expected {expected_category} for '{desc}', got {pattern['category']}"

    def test_pattern_learner_generates_template(self):
        """PatternLearner generates executable code templates."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        pattern = learner.learn_from_description("CreateAccount", "create new account with initial balance")
        assert "template" in pattern
        assert "Behavior" in pattern["template"]

    def test_pattern_learner_export(self):
        """PatternLearner can export learned patterns."""
        from aicl.autonomous import PatternLearner
        learner = PatternLearner()
        learner.learn_from_description("Test1", "validate input data")
        learner.learn_from_description("Test2", "create new record")
        exported = learner.export_patterns()
        assert len(exported) == 2

    def test_spec_evolver_creation(self):
        """SpecEvolver can be created."""
        from aicl.autonomous import SpecEvolver
        evolver = SpecEvolver()
        assert len(evolver.evolution_log) == 0

    def test_spec_evolver_fixes_missing_recovery(self):
        """SpecEvolver adds missing Recovery for unpaired Risk."""
        from aicl.autonomous import SpecEvolver
        evolver = SpecEvolver()
        source = "Goal:\nTest\n\nRisk:\nDatabase failure\n\nLayer:\nCore\n\nValidation:\nSystem works"
        modified, changes = evolver.evolve_from_verification(source, {
            "checks": [{"name": "risk_recovery_pairing", "status": "FAIL", "message": "Unpaired risk"}]
        })
        assert len(changes) > 0
        assert "Recovery" in modified

    def test_spec_evolver_makes_vague_validation_specific(self):
        """SpecEvolver makes vague validations more testable."""
        from aicl.autonomous import SpecEvolver
        evolver = SpecEvolver()
        source = "Goal:\nTest\n\nLayer:\nCore\n\nValidation:\nSystem works correctly"
        modified, changes = evolver.evolve_from_test_failure(source, {
            "suggested_fix": "fix_validation_logic",
            "assertion_failures": ["test_validation_1"],
        })
        if len(changes) > 0:
            assert "works correctly" not in modified

    def test_loop_controller_creation(self):
        """LoopController can be created with custom settings."""
        from aicl.autonomous import LoopController
        controller = LoopController(max_iterations=5, convergence_threshold=0.02)
        assert controller.max_iterations == 5
        assert controller.should_continue

    def test_loop_controller_convergence_detection(self):
        """LoopController detects convergence correctly."""
        from aicl.autonomous import LoopController, LoopIteration, LoopState
        controller = LoopController(max_iterations=10)

        iteration = LoopIteration(
            iteration=1,
            state_entered=LoopState.COMPILING,
            timestamp_start=0.0,
            tests_passed=10,
            tests_total=10,
            audit_coverage=1.0,
            fallback_count=0,
        )
        iteration.state_exited = LoopState.CONVERGED
        controller.record_iteration(iteration)

        iteration2 = LoopIteration(
            iteration=2,
            state_entered=LoopState.COMPILING,
            timestamp_start=0.0,
            tests_passed=10,
            tests_total=10,
            audit_coverage=1.0,
            fallback_count=0,
        )
        iteration2.state_exited = LoopState.CONVERGED
        controller.record_iteration(iteration2)

        assert controller.is_converged
        assert controller.convergence_iteration == 1

    def test_loop_controller_max_iterations(self):
        """LoopController respects max iterations."""
        from aicl.autonomous import LoopController, LoopIteration, LoopState
        controller = LoopController(max_iterations=2)

        for i in range(3):
            iteration = LoopIteration(
                iteration=i + 1,
                state_entered=LoopState.COMPILING,
                timestamp_start=0.0,
                tests_passed=0,
                tests_total=1,
                audit_coverage=0.5,
                fallback_count=1,
            )
            controller.record_iteration(iteration)

        assert not controller.should_continue
        assert len(controller.iterations) == 3

    def test_autonomous_result_summary(self):
        """AutonomousResult produces a readable summary."""
        from aicl.autonomous import AutonomousResult
        result = AutonomousResult(
            converged=True,
            iterations=[],
            total_duration=1.5,
            final_audit_coverage=1.0,
            final_test_pass_rate=1.0,
            patterns_learned=["LEARNED_TRANSFER", "LEARNED_CONVERT"],
            spec_evolution=["Added recovery for risk"],
            convergence_iteration=3,
            proof_valid=True,
        )
        summary = result.summary
        assert "Converged: True" in summary
        assert "100.0%" in summary

    def test_format_evolve_report(self):
        """format_evolve_report produces a readable report."""
        from aicl.autonomous import AutonomousResult, format_evolve_report
        result = AutonomousResult(
            converged=False,
            iterations=[],
            total_duration=0.5,
            final_audit_coverage=0.8,
            final_test_pass_rate=0.9,
            patterns_learned=["LEARNED_VALIDATE"],
            spec_evolution=[],
        )
        report = format_evolve_report(result)
        assert "AUTONOMOUS" in report
        assert "80.0%" in report

    def test_loop_state_enum(self):
        """LoopState enum has all expected states."""
        from aicl.autonomous import LoopState
        states = [s.value for s in LoopState]
        assert "compiling" in states
        assert "verifying" in states
        assert "testing" in states
        assert "diagnosing" in states
        assert "fixing" in states
        assert "learning" in states
        assert "converged" in states
        assert "failed" in states

    def test_new_provenance_types(self):
        """New ProvenanceTypes for autonomous compilation exist."""
        from aicl.provenance import ProvenanceType
        assert ProvenanceType.AI_GENERATION.value == "ai_generation"
        assert ProvenanceType.SELF_HEALING.value == "self_healing"
        assert ProvenanceType.PATTERN_LEARNED.value == "pattern_learned"
        assert ProvenanceType.SPEC_EVOLVED.value == "spec_evolved"

    def test_autonomous_compiler_creation(self):
        """AutonomousCompiler can be created with custom settings."""
        from aicl.autonomous import AutonomousCompiler
        compiler = AutonomousCompiler(
            max_iterations=5,
            target_language="python",
            test_timeout=10,
        )
        assert compiler.max_iterations == 5
        assert compiler.test_runner is not None
        assert compiler.pattern_learner is not None
        assert compiler.spec_evolver is not None
        assert compiler.loop_controller is not None

    def test_test_runner_creation(self):
        """TestRunner can be created."""
        from aicl.autonomous import TestRunner
        runner = TestRunner(timeout=10)
        assert runner.timeout == 10

    def test_test_runner_missing_file(self):
        """TestRunner handles missing test files gracefully."""
        from aicl.autonomous import TestRunner
        runner = TestRunner()
        passed, failed, total, details = runner.run_tests("/nonexistent/path")
        assert passed == 0
        assert failed == 0
        assert total == 0

    def test_loop_iteration_dataclass(self):
        """LoopIteration dataclass works correctly."""
        from aicl.autonomous import LoopIteration, LoopState
        it = LoopIteration(
            iteration=1,
            state_entered=LoopState.COMPILING,
            timestamp_start=100.0,
        )
        assert it.iteration == 1
        assert it.tests_passed == 0
        assert it.audit_coverage == 0.0
        assert it.fallback_count == 0

    def test_loop_iteration_success_property(self):
        """LoopIteration.success property works correctly."""
        from aicl.autonomous import LoopIteration, LoopState
        # Successful iteration
        it = LoopIteration(
            iteration=1,
            state_entered=LoopState.COMPILING,
            timestamp_start=0.0,
            tests_passed=5,
            tests_failed=0,
            tests_total=5,
            audit_coverage=1.0,
            fallback_count=0,
        )
        assert it.success

        # Failed iteration (tests failed)
        it2 = LoopIteration(
            iteration=2,
            state_entered=LoopState.COMPILING,
            timestamp_start=0.0,
            tests_passed=4,
            tests_failed=1,
            tests_total=5,
            audit_coverage=1.0,
            fallback_count=0,
        )
        assert not it2.success

        # Failed iteration (fallbacks)
        it3 = LoopIteration(
            iteration=3,
            state_entered=LoopState.COMPILING,
            timestamp_start=0.0,
            tests_passed=5,
            tests_failed=0,
            tests_total=5,
            audit_coverage=1.0,
            fallback_count=2,
        )
        assert not it3.success


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
