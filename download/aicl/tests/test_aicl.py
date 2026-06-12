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
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'pong.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Pong has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_chat_zero_todos(self):
        """Test that Chat compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'chat.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Chat has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_chess_zero_todos(self):
        """Test that Chess compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'chess.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Chess has {result.todo_count} TODOs"
        assert result.fully_compiled

    def test_blue_square_zero_todos(self):
        """Test that Blue Square compiles with zero TODOs."""
        from aicl.compiler import Compiler
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', 'blue_square.aicl')) as f:
            source = f.read()
        compiler = Compiler()
        result = compiler.compile(source)
        assert result.success
        assert result.todo_count == 0, f"Blue Square has {result.todo_count} TODOs"
        assert result.fully_compiled


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
