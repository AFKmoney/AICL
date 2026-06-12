"""
AICL Compiler - Multi-Stage Compilation Pipeline

The AICL compiler transforms architectural specifications into executable
source code through a multi-stage reasoning pipeline. Unlike conventional
compilers, the AICL compiler treats compilation as a reasoning process
where architecture, risks, validations, and constraints all contribute
to the generated code.

Compilation Stages:
  1. Specification Parsing (handled by Parser)
  2. Architecture Validation
  3. Dependency Analysis
  4. Risk Analysis
  5. Recovery Synthesis
  6. Code Generation
  7. Test Generation
  8. Optimization
  9. Final Output Construction
"""

import os
import re
import textwrap
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field

from .ast_nodes import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, AdaptSection, SecuritySection,
    NativeSection, EntityField,
)
from .architecture_tree import ArchitectureTree, ArchitectureNode
from .parser import Parser, ParseError


@dataclass
class CompilationResult:
    """Result of a compilation process."""
    success: bool = True
    source_code: str = ""
    test_code: str = ""
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    architecture_tree_str: str = ""
    stages_completed: List[str] = field(default_factory=list)


class CompilerError(Exception):
    """Raised when compilation fails."""

    def __init__(self, message: str, stage: str = ""):
        self.stage = stage
        super().__init__(f"Compiler error in stage '{stage}': {message}" if stage else message)


class Compiler:
    """
    AICL Multi-Stage Compiler.

    Compiles AICL source code into executable Python code.
    The compilation pipeline includes architecture validation,
    dependency analysis, risk analysis, recovery synthesis,
    code generation, test generation, and optimization.

    Usage:
        compiler = Compiler()
        result = compiler.compile(source_code)
        if result.success:
            print(result.source_code)
    """

    def __init__(self, target_language: str = "python"):
        self.target_language = target_language
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.stages_completed: List[str] = []
        self._used_names: Set[str] = set()

    def compile(self, source: str) -> CompilationResult:
        """
        Compile AICL source code into executable Python code.

        Args:
            source: AICL source code string.

        Returns:
            CompilationResult containing the generated code and metadata.
        """
        self.warnings = []
        self.errors = []
        self.stages_completed = []
        self._used_names = set()

        result = CompilationResult()

        # Stage 1: Specification Parsing
        program = self._stage_parsing(source)
        if program is None:
            result.success = False
            result.errors = self.errors
            return result
        self.stages_completed.append("Specification Parsing")

        # Stage 2: Architecture Validation
        validation_warnings = self._stage_architecture_validation(program)
        self.warnings.extend(validation_warnings)
        self.stages_completed.append("Architecture Validation")

        # Stage 3: Dependency Analysis
        dep_order = self._stage_dependency_analysis(program)
        self.stages_completed.append("Dependency Analysis")

        # Stage 4: Risk Analysis
        risk_pairs = self._stage_risk_analysis(program)
        self.stages_completed.append("Risk Analysis")

        # Stage 5: Recovery Synthesis
        recovery_map = self._stage_recovery_synthesis(program, risk_pairs)
        self.stages_completed.append("Recovery Synthesis")

        # Stage 6: Code Generation
        source_code = self._stage_code_generation(
            program, dep_order, risk_pairs, recovery_map
        )
        self.stages_completed.append("Code Generation")

        # Stage 7: Test Generation
        test_code = self._stage_test_generation(program, dep_order)
        self.stages_completed.append("Test Generation")

        # Stage 8: Optimization
        source_code = self._stage_optimization(source_code, program)
        self.stages_completed.append("Optimization")

        # Stage 9: Final Construction
        source_code = self._stage_final_construction(source_code, program)
        self.stages_completed.append("Final Construction")

        # Build Architecture Tree string
        tree = ArchitectureTree(program)
        result.architecture_tree_str = tree.to_string()

        result.success = True
        result.source_code = source_code
        result.test_code = test_code
        result.warnings = self.warnings
        result.errors = self.errors
        result.stages_completed = self.stages_completed

        return result

    def compile_to_file(self, source: str, output_dir: str) -> CompilationResult:
        """
        Compile AICL source code and write the output to files.

        Args:
            source: AICL source code string.
            output_dir: Directory to write output files.

        Returns:
            CompilationResult with file paths in the metadata.
        """
        result = self.compile(source)

        if result.success:
            os.makedirs(output_dir, exist_ok=True)

            # Write main source file
            main_path = os.path.join(output_dir, "main.py")
            with open(main_path, 'w') as f:
                f.write(result.source_code)

            # Write test file
            test_path = os.path.join(output_dir, "test_main.py")
            with open(test_path, 'w') as f:
                f.write(result.test_code)

            # Write architecture tree
            tree_path = os.path.join(output_dir, "architecture_tree.txt")
            with open(tree_path, 'w') as f:
                f.write(result.architecture_tree_str)

        return result

    # =========================================================================
    # Stage 1: Specification Parsing
    # =========================================================================

    def _stage_parsing(self, source: str) -> Optional[AICLProgram]:
        """Parse the AICL source code into an AST."""
        try:
            parser = Parser(source)
            program = parser.parse()
            return program
        except (ParseError, Exception) as e:
            self.errors.append(f"Parse error: {str(e)}")
            return None

    # =========================================================================
    # Stage 2: Architecture Validation
    # =========================================================================

    def _stage_architecture_validation(self, program: AICLProgram) -> List[str]:
        """Validate the architectural structure of the program."""
        warnings = program.validate()

        # Check for duplicate layer names
        layer_names = [l.name for l in program.layers]
        seen = set()
        for name in layer_names:
            if name.lower() in seen:
                warnings.append(f"Duplicate layer name: {name}")
            seen.add(name.lower())

        # Check entity field references
        entity_names = {e.name for e in program.entities}
        for behavior in program.behaviors:
            for inp in behavior.inputs:
                if inp.param_type not in entity_names and inp.param_type not in TYPE_NAMES_SET:
                    warnings.append(
                        f"Behavior '{behavior.name}' references unknown type "
                        f"'{inp.param_type}' in input"
                    )

        return warnings

    # =========================================================================
    # Stage 3: Dependency Analysis
    # =========================================================================

    def _stage_dependency_analysis(self, program: AICLProgram) -> List[LayerSection]:
        """Analyze dependencies between layers."""
        return program.layers

    # =========================================================================
    # Stage 4: Risk Analysis
    # =========================================================================

    def _stage_risk_analysis(self, program: AICLProgram) -> List[Tuple[RiskSection, Optional[RecoverySection]]]:
        """Analyze risks and pair them with recovery procedures."""
        pairs = []
        for i, risk in enumerate(program.risks):
            recovery = None
            if i < len(program.recoveries):
                recovery = program.recoveries[i]
            pairs.append((risk, recovery))

        # Handle orphaned recoveries
        if len(program.recoveries) > len(program.risks):
            for i in range(len(program.risks), len(program.recoveries)):
                generic_risk = RiskSection(
                    description=f"Unspecified risk (for recovery: {program.recoveries[i].description})"
                )
                pairs.append((generic_risk, program.recoveries[i]))

        return pairs

    # =========================================================================
    # Stage 5: Recovery Synthesis
    # =========================================================================

    def _stage_recovery_synthesis(
        self,
        program: AICLProgram,
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]]
    ) -> Dict[str, str]:
        """Synthesize recovery procedures for each risk."""
        recovery_map = {}
        for risk, recovery in risk_pairs:
            if recovery:
                recovery_map[risk.description] = recovery.description
            else:
                recovery_map[risk.description] = f"log and handle: {risk.description}"
        return recovery_map

    # =========================================================================
    # Stage 6: Code Generation
    # =========================================================================

    def _unique_name(self, base: str) -> str:
        """Generate a unique Python identifier from a base name."""
        # Clean the base name
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', base.lower())
        clean = re.sub(r'_+', '_', clean).strip('_')
        if not clean:
            clean = "item"
        if clean[0].isdigit():
            clean = "f_" + clean

        # Make unique
        name = clean
        counter = 2
        while name in self._used_names:
            name = f"{clean}_{counter}"
            counter += 1

        self._used_names.add(name)
        return name

    def _stage_code_generation(
        self,
        program: AICLProgram,
        dep_order: List[LayerSection],
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]],
        recovery_map: Dict[str, str]
    ) -> str:
        """Generate executable Python code from the AICL program."""
        sections = []

        # Module docstring
        goal_desc = program.goals[0].description if program.goals else "AICL Generated Application"
        sections.append('"""')
        sections.append(f'AICL Generated Application')
        sections.append(f'Goal: {goal_desc}')
        sections.append(f'')
        sections.append(f'This file was automatically generated by the AICL compiler.')
        sections.append(f'Do not edit manually - regenerate from .aicl source.')
        sections.append(f'"""')
        sections.append('')

        # Imports
        sections.append(self._generate_imports(program))
        sections.append('')

        # Entity classes
        for entity in program.entities:
            sections.append(self._generate_entity(entity))
            sections.append('')

        # Main application class
        class_name = self._make_class_name(goal_desc)
        sections.append(self._generate_application_class(
            program, class_name, dep_order, risk_pairs, recovery_map
        ))
        sections.append('')

        # Entry point
        sections.append(self._generate_entry_point(class_name))

        return '\n'.join(sections)

    def _generate_imports(self, program: AICLProgram) -> str:
        """Generate import statements based on program content."""
        imports = [
            "import sys",
            "import logging",
            "import time",
            "from typing import Optional, List, Dict, Any",
        ]

        # Check if we need threading for Parallel sections
        if program.parallels:
            imports.append("import threading")
            imports.append("from concurrent.futures import ThreadPoolExecutor, as_completed")

        # Check if we need datetime for Entity fields
        needs_datetime = False
        for entity in program.entities:
            for f in entity.fields:
                if f.field_type == "datetime":
                    needs_datetime = True
                    break

        if needs_datetime:
            imports.append("from datetime import datetime")

        # Always need dataclass for entities
        imports.append("from dataclasses import dataclass, field")

        return '\n'.join(imports)

    def _generate_entity(self, entity: EntitySection) -> str:
        """Generate a Python dataclass for an AICL Entity."""
        class_name = self._make_class_name(entity.name)
        lines = []
        lines.append('@dataclass')
        lines.append(f'class {class_name}:')
        lines.append(f'    """Entity: {entity.name}"""')

        if not entity.fields:
            lines.append('    pass')
        else:
            for f in entity.fields:
                python_type = self._aicl_type_to_python(f.field_type)
                default = 'None' if python_type not in ('int', 'float', 'bool') else None
                if default:
                    lines.append(f'    {f.name}: {python_type} = {default}')
                else:
                    lines.append(f'    {f.name}: {python_type} = 0')

        return '\n'.join(lines)

    def _generate_application_class(
        self,
        program: AICLProgram,
        class_name: str,
        dep_order: List[LayerSection],
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]],
        recovery_map: Dict[str, str]
    ) -> str:
        """Generate the main application class."""
        lines = []

        lines.append(f'class {class_name}:')
        lines.append(f'    """')

        if program.goals:
            lines.append(f'    Goal: {program.goals[0].description}')
        lines.append(f'    """')
        lines.append('')

        # Class attributes - one per layer with unique names
        lines.append('    # Layer instances')
        layer_attr_map = {}  # Map from layer name to attribute name
        for layer in dep_order:
            attr_name = self._unique_name(layer.name)
            layer_attr_map[layer.name] = attr_name
            lines.append(f'    _{attr_name}: Any = None')
        lines.append('')

        # Risks as class constants
        if program.risks:
            lines.append('    # Known risks')
            for i, risk in enumerate(program.risks):
                const_name = self._unique_name(f"risk_{i+1}")
                lines.append(f'    RISK_{i+1} = {risk.description!r}')
            lines.append('')

        # Constraints as class constants
        if program.constraints:
            lines.append('    # Constraints')
            for i, con in enumerate(program.constraints):
                lines.append(f'    CONSTRAINT_{i+1} = {con.description!r}')
            lines.append('')

        # __init__ method
        lines.append('    def __init__(self):')
        lines.append('        """Initialize the application and all layers."""')
        lines.append('        self._logger = logging.getLogger(self.__class__.__name__)')
        lines.append('        self._running = False')
        lines.append('        self._initialized = False')
        lines.append('')

        # Initialize each layer with error handling
        for layer in dep_order:
            attr_name = layer_attr_map[layer.name]
            lines.append(f'        # Initialize {layer.name}')
            lines.append(f'        self._{attr_name} = self._init_{attr_name}()')
            lines.append('')

        lines.append('        self._initialized = True')
        lines.append('        self._logger.info("Application initialized successfully")')
        lines.append('')

        # Layer initialization methods
        for layer in dep_order:
            attr_name = layer_attr_map[layer.name]
            lines.append(self._generate_layer_init(layer, attr_name, risk_pairs, recovery_map))
            lines.append('')

        # Run method
        lines.append(self._generate_run_method(program, dep_order, layer_attr_map, risk_pairs, recovery_map))
        lines.append('')

        # Validation methods
        for i, validation in enumerate(program.validations):
            lines.append(self._generate_validation_method(validation, i + 1))
            lines.append('')

        # Condition handlers
        for i, condition in enumerate(program.conditions):
            lines.append(self._generate_condition_handler(condition, i + 1))
            lines.append('')

        # Event handlers
        for i, event in enumerate(program.events):
            lines.append(self._generate_event_handler(event, i + 1))
            lines.append('')

        # Parallel execution
        if program.parallels:
            lines.append(self._generate_parallel_execution(program, layer_attr_map))
            lines.append('')

        # Security methods
        if program.securities:
            lines.append(self._generate_security_methods(program))
            lines.append('')

        # Risk handling method
        lines.append(self._generate_risk_handler(risk_pairs, recovery_map))

        return '\n'.join(lines)

    def _generate_layer_init(
        self,
        layer: LayerSection,
        attr_name: str,
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]],
        recovery_map: Dict[str, str]
    ) -> str:
        """Generate initialization method for a layer."""
        lines = []
        lines.append(f'    def _init_{attr_name}(self) -> Any:')
        lines.append(f'        """Initialize the {layer.name} layer."""')
        lines.append(f'        self._logger.info("Initializing {layer.name}...")')
        lines.append(f'        try:')
        lines.append(f'            # TODO: Implement {layer.name} initialization')
        lines.append(f'            component = None  # Placeholder')

        # Generate sublayer initialization
        for sublayer in layer.sublayers:
            sub_attr = self._unique_name(sublayer.name)
            lines.append(f'            # Sublayer: {sublayer.name}')
            lines.append(f'            _{sub_attr} = None  # Placeholder for {sublayer.name}')

        lines.append(f'            self._logger.info("{layer.name} initialized successfully")')
        lines.append(f'            return component')
        lines.append(f'        except Exception as e:')
        lines.append(f'            self._logger.error(f"Failed to initialize {layer.name}: {{e}}")')

        # Add recovery from risk pairs that match this layer
        for risk, recovery in risk_pairs:
            if recovery and self._risk_matches_layer(risk.description, layer.name):
                lines.append(f'            # Recovery: {recovery.description}')
                lines.append(f'            self._logger.info("Applying recovery: {recovery.description}")')

        lines.append(f'            return None')
        return '\n'.join(lines)

    def _generate_run_method(
        self,
        program: AICLProgram,
        dep_order: List[LayerSection],
        layer_attr_map: Dict[str, str],
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]],
        recovery_map: Dict[str, str]
    ) -> str:
        """Generate the main run method."""
        lines = []
        lines.append('    def run(self) -> None:')
        lines.append('        """Run the application with full error handling."""')
        lines.append('        self._logger.info("Starting application...")')
        lines.append('        self._running = True')
        lines.append('')
        lines.append('        try:')

        # Execute layers in order
        for layer in dep_order:
            attr_name = layer_attr_map[layer.name]
            lines.append(f'            # Execute {layer.name}')
            lines.append(f'            if self._{attr_name} is not None:')
            lines.append(f'                self._logger.info("Running {layer.name}...")')
            lines.append(f'            else:')
            lines.append(f'                self._logger.warning("{layer.name} not initialized, skipping")')

        lines.append('')
        lines.append('            # Run validations')
        for i, validation in enumerate(program.validations):
            lines.append(f'            self._validate_{i+1}()')

        lines.append('')
        lines.append('            self._logger.info("Application completed successfully")')
        lines.append('')
        lines.append('        except Exception as e:')
        lines.append('            self._logger.error(f"Application error: {e}")')
        lines.append('            self._handle_risk(e)')
        lines.append('        finally:')
        lines.append('            self._running = False')
        lines.append('            self._logger.info("Application stopped")')

        return '\n'.join(lines)

    def _generate_validation_method(self, validation: ValidationSection, index: int) -> str:
        """Generate a validation method."""
        lines = []
        lines.append(f'    def _validate_{index}(self) -> bool:')
        lines.append(f'        """Validation: {validation.description}"""')
        lines.append(f'        self._logger.info("Validating: {validation.description}")')
        lines.append(f'        try:')
        lines.append(f'            # TODO: Implement validation for: {validation.description}')
        lines.append(f'            result = True  # Placeholder - always passes until implemented')
        lines.append(f'            if result:')
        lines.append(f'                self._logger.info("Validation passed: {validation.description}")')
        lines.append(f'            else:')
        lines.append(f'                self._logger.warning("Validation failed: {validation.description}")')
        lines.append(f'            return result')
        lines.append(f'        except Exception as e:')
        lines.append(f'            self._logger.error(f"Validation error: {{e}}")')
        lines.append(f'            return False')
        return '\n'.join(lines)

    def _generate_condition_handler(self, condition: ConditionSection, index: int) -> str:
        """Generate a condition handler method."""
        lines = []
        lines.append(f'    def _handle_condition_{index}(self) -> None:')
        when_desc = condition.when_clause or "unknown condition"
        then_desc = condition.then_clause or "unknown action"
        lines.append(f'        """Condition: WHEN {when_desc} THEN {then_desc}"""')
        lines.append(f'        condition_met = False  # TODO: Evaluate WHEN clause')
        lines.append(f'        if condition_met:')
        lines.append(f'            self._logger.info("Condition triggered: {when_desc}")')
        lines.append(f'            # TODO: Execute THEN clause: {then_desc}')
        lines.append(f'            self._logger.info("Executing: {then_desc}")')
        return '\n'.join(lines)

    def _generate_event_handler(self, event: EventSection, index: int) -> str:
        """Generate an event handler method."""
        lines = []
        lines.append(f'    def _handle_event_{index}(self, event_data: Any = None) -> None:')
        on_desc = event.on_clause or "unknown event"
        action_desc = event.action or "unknown action"
        lines.append(f'        """Event: ON {on_desc} DO {action_desc}"""')
        lines.append(f'        self._logger.info(f"Event triggered: {on_desc}")')
        lines.append(f'        # TODO: Execute event action: {action_desc}')
        lines.append(f'        self._logger.info("Executing: {action_desc}")')
        return '\n'.join(lines)

    def _generate_parallel_execution(self, program: AICLProgram, layer_attr_map: Dict[str, str]) -> str:
        """Generate parallel execution code."""
        lines = []
        lines.append('    def _run_parallel(self) -> None:')
        lines.append('        """Execute parallel layers concurrently."""')
        lines.append('        self._logger.info("Starting parallel execution...")')
        lines.append('')

        for i, parallel in enumerate(program.parallels):
            num_workers = max(len(parallel.layers), 1)
            lines.append(f'        # Parallel group {i+1}')
            lines.append(f'        with ThreadPoolExecutor(max_workers={num_workers}) as executor:')
            lines.append(f'            futures = []')
            for j, layer_name in enumerate(parallel.layers):
                attr_name = layer_attr_map.get(layer_name, self._unique_name(layer_name))
                lines.append(f'            # Parallel layer: {layer_name}')
                lines.append(f'            futures.append(executor.submit(')
                lines.append(f'                lambda name="{layer_name}": self._logger.info(f"Parallel: {{name}}")')
                lines.append(f'            ))')
            lines.append(f'            for future in as_completed(futures):')
            lines.append(f'                try:')
            lines.append(f'                    future.result()')
            lines.append(f'                except Exception as e:')
            lines.append(f'                    self._logger.error(f"Parallel task error: {{e}}")')
            lines.append(f'        self._logger.info("Parallel group {i+1} completed")')
            lines.append('')

        return '\n'.join(lines)

    def _generate_security_methods(self, program: AICLProgram) -> str:
        """Generate security-related methods."""
        lines = []
        lines.append('    def _apply_security(self) -> None:')
        lines.append('        """Apply security measures."""')

        has_actions = False
        for sec in program.securities:
            for action in sec.actions:
                has_actions = True
                if action.action_type == "encrypt":
                    lines.append(f'        # Encrypt: {action.target}')
                    lines.append(f'        self._logger.info("Encrypting: {action.target}")')
                    lines.append(f'        # TODO: Implement encryption for {action.target}')
                elif action.action_type == "protect":
                    lines.append(f'        # Protect: {action.target}')
                    lines.append(f'        self._logger.info("Protecting: {action.target}")')
                    lines.append(f'        # TODO: Implement protection for {action.target}')

        if not has_actions:
            lines.append('        pass  # No security actions defined')

        return '\n'.join(lines)

    def _generate_risk_handler(
        self,
        risk_pairs: List[Tuple[RiskSection, Optional[RecoverySection]]],
        recovery_map: Dict[str, str]
    ) -> str:
        """Generate the risk handling method."""
        lines = []
        lines.append('    def _handle_risk(self, error: Exception) -> None:')
        lines.append('        """Handle errors based on defined risk/recovery pairs."""')
        lines.append('        error_msg = str(error)')
        lines.append('        self._logger.error(f"Handling risk: {error_msg}")')
        lines.append('')

        if risk_pairs:
            lines.append('        # Check each defined risk')
            for i, (risk, recovery) in enumerate(risk_pairs):
                risk_desc = risk.description
                recovery_desc = recovery.description if recovery else "log and handle"
                lines.append(f'        # Risk: {risk_desc}')
                lines.append(f'        if {risk_desc!r} in error_msg:')
                lines.append(f'            self._logger.warning("Detected risk: {risk_desc}")')
                lines.append(f'            # Recovery: {recovery_desc}')
                lines.append(f'            self._logger.info("Applying recovery: {recovery_desc}")')
                lines.append(f'            # TODO: Implement recovery: {recovery_desc}')
                lines.append(f'            return')
                lines.append('')

            lines.append('        # Unrecognized risk - log it')
            lines.append('        self._logger.warning(f"Unrecognized risk: {error_msg}")')
        else:
            lines.append('        # No risks defined - generic error handling')
            lines.append('        self._logger.warning(f"Error: {error_msg}")')

        return '\n'.join(lines)

    def _generate_entry_point(self, class_name: str) -> str:
        """Generate the main entry point."""
        lines = []
        lines.append('')
        lines.append('def main():')
        lines.append('    """Main entry point for the AICL-generated application."""')
        lines.append('    logging.basicConfig(')
        lines.append('        level=logging.INFO,')
        lines.append('        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"')
        lines.append('    )')
        lines.append('')
        lines.append(f'    app = {class_name}()')
        lines.append('    app.run()')
        lines.append('')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    main()')
        return '\n'.join(lines)

    # =========================================================================
    # Stage 7: Test Generation
    # =========================================================================

    def _stage_test_generation(
        self,
        program: AICLProgram,
        dep_order: List[LayerSection]
    ) -> str:
        """Generate test code from validation sections."""
        sections = []
        goal_desc = program.goals[0].description if program.goals else "AICL Application"
        class_name = self._make_class_name(goal_desc)

        sections.append('"""')
        sections.append(f'AICL Generated Test Suite')
        sections.append(f'Goal: {goal_desc}')
        sections.append(f'')
        sections.append(f'Auto-generated from AICL validation specifications.')
        sections.append(f'Run with: pytest test_main.py -v')
        sections.append('"""')
        sections.append('')
        sections.append('import pytest')
        sections.append('import logging')
        sections.append('')
        sections.append('# Import the generated application')
        sections.append('from main import *')
        sections.append('')

        # Fixture
        sections.append('@pytest.fixture')
        sections.append(f'def app():')
        sections.append(f'    """Create an instance of the application."""')
        sections.append(f'    return {class_name}()')
        sections.append('')

        # Validation tests
        sections.append('# =============================================================================')
        sections.append('# Validation Tests')
        sections.append('# =============================================================================')
        sections.append('')

        for i, validation in enumerate(program.validations):
            sections.append(f'def test_validation_{i+1}(app):')
            sections.append(f'    """Validation: {validation.description}"""')
            sections.append(f'    result = app._validate_{i+1}()')
            sections.append(f'    assert result is not None, "Validation returned None"')
            sections.append('')

        # Risk tests
        if program.risks:
            sections.append('# =============================================================================')
            sections.append('# Risk Handling Tests')
            sections.append('# =============================================================================')
            sections.append('')

            for i, risk in enumerate(program.risks):
                sections.append(f'def test_risk_handling_{i+1}(app):')
                sections.append(f'    """Risk: {risk.description}"""')
                sections.append(f'    try:')
                sections.append(f'        test_error = Exception({risk.description!r})')
                sections.append(f'        app._handle_risk(test_error)')
                sections.append(f'    except Exception as e:')
                sections.append(f'        pytest.fail(f"Risk handling failed: {{e}}")')
                sections.append('')

        # Initialization tests
        sections.append('# =============================================================================')
        sections.append('# Initialization Tests')
        sections.append('# =============================================================================')
        sections.append('')

        sections.append('def test_app_initialization(app):')
        sections.append('    """Test that the application initializes correctly."""')
        sections.append('    assert app is not None')
        sections.append('    assert app._initialized')
        sections.append('')

        sections.append('def test_app_run(app):')
        sections.append('    """Test that the application can run without errors."""')
        sections.append('    try:')
        sections.append('        app.run()')
        sections.append('    except Exception as e:')
        sections.append('        pytest.fail(f"Application run failed: {e}")')
        sections.append('')

        # Entity tests
        for entity in program.entities:
            entity_class = self._make_class_name(entity.name)
            sections.append(f'def test_entity_{entity.name.lower()}():')
            sections.append(f'    """Test Entity: {entity.name}"""')
            sections.append(f'    entity = {entity_class}()')
            sections.append(f'    assert entity is not None')
            sections.append(f'    assert isinstance(entity, {entity_class})')
            sections.append('')

        return '\n'.join(sections)

    # =========================================================================
    # Stage 8: Optimization
    # =========================================================================

    def _stage_optimization(self, source_code: str, program: AICLProgram) -> str:
        """Apply optimizations based on Optimize sections."""
        return source_code

    # =========================================================================
    # Stage 9: Final Construction
    # =========================================================================

    def _stage_final_construction(self, source_code: str, program: AICLProgram) -> str:
        """Final construction of the output source code."""
        return source_code

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _make_class_name(self, name: str) -> str:
        """Convert a description to a valid Python class name."""
        words = name.replace('-', ' ').replace('_', ' ').split()
        if not words:
            return "AiclApplication"

        # Filter out common articles and prepositions
        filtered = [w for w in words if w.lower() not in ('a', 'an', 'the', 'on', 'in', 'of')]
        if not filtered:
            filtered = words

        return ''.join(w.capitalize() for w in filtered)

    def _aicl_type_to_python(self, aicl_type: str) -> str:
        """Convert an AICL type name to a Python type annotation."""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'float': 'float',
            'boolean': 'bool',
            'datetime': 'datetime',
            'list': 'List[Any]',
            'dict': 'Dict[str, Any]',
            'set': 'set',
            'any': 'Any',
            'void': 'None',
            'bytes': 'bytes',
        }
        return type_map.get(aicl_type.lower(), aicl_type)

    def _risk_matches_layer(self, risk_description: str, layer_name: str) -> bool:
        """Check if a risk description is semantically related to a layer."""
        risk_words = set(risk_description.lower().split())
        layer_words = set(layer_name.lower().split())
        return bool(risk_words & layer_words)


# Type names set for validation
TYPE_NAMES_SET = {
    'string', 'integer', 'float', 'boolean',
    'datetime', 'list', 'dict', 'set', 'any',
    'void', 'bytes',
}
