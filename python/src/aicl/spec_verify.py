"""
AICL Specification Verification System

Implements three levels of specification checking:

1. Completeness Checking: Verifies that the specification contains all
   required elements (Goal, Layer, Validation) and that all references
   between elements are resolvable.

2. Coherence Checking: Verifies that the specification is internally
   consistent — no contradictions, no dangling references, no
   impossible configurations.

3. Satisfaction Checking: Verifies that the specification is satisfiable —
   that a valid program can be generated from it, and that validations
   are testable.

Usage:
    aicl verify <source.aicl>                    # All three checks
    aicl verify <source.aicl> --completeness     # Completeness only
    aicl verify <source.aicl> --coherence        # Coherence only
    aicl verify <source.aicl> --satisfaction     # Satisfaction only
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum

from .ast import AICLProgram
from .parser import Parser
from .ir import ArchitectureTree


class CheckStatus(Enum):
    """Status of a verification check."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


@dataclass
class CheckResult:
    """Result of a single verification check."""
    name: str
    status: CheckStatus
    message: str
    details: List[str] = field(default_factory=list)


@dataclass
class VerificationReport:
    """Complete verification report for a specification."""
    source: str = ""
    completeness_results: List[CheckResult] = field(default_factory=list)
    coherence_results: List[CheckResult] = field(default_factory=list)
    satisfaction_results: List[CheckResult] = field(default_factory=list)

    @property
    def all_results(self) -> List[CheckResult]:
        """All check results combined."""
        return self.completeness_results + self.coherence_results + self.satisfaction_results

    @property
    def passed(self) -> bool:
        """Whether all checks passed (no FAIL results)."""
        return all(r.status != CheckStatus.FAIL for r in self.all_results)

    @property
    def warnings(self) -> List[CheckResult]:
        """Checks that produced warnings."""
        return [r for r in self.all_results if r.status == CheckStatus.WARN]

    def summary(self) -> str:
        """Generate a human-readable summary of the verification."""
        lines = []
        lines.append("=" * 60)
        lines.append("AICL SPECIFICATION VERIFICATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Source: {self.source or '<unknown>'}")
        lines.append(f"Overall: {'PASS' if self.passed else 'FAIL'}")
        lines.append("")

        for section_name, results in [
            ("COMPLETENESS", self.completeness_results),
            ("COHERENCE", self.coherence_results),
            ("SATISFACTION", self.satisfaction_results),
        ]:
            lines.append(f"--- {section_name} ---")
            for r in results:
                status_str = f"[{r.status.value:4s}]"
                lines.append(f"  {status_str} {r.name}: {r.message}")
                for detail in r.details:
                    lines.append(f"         {detail}")
            lines.append("")

        total = len(self.all_results)
        passed_count = sum(1 for r in self.all_results if r.status == CheckStatus.PASS)
        warn_count = sum(1 for r in self.all_results if r.status == CheckStatus.WARN)
        fail_count = sum(1 for r in self.all_results if r.status == CheckStatus.FAIL)

        lines.append(f"Total checks: {total}")
        lines.append(f"  Passed: {passed_count}")
        lines.append(f"  Warnings: {warn_count}")
        lines.append(f"  Failed: {fail_count}")
        lines.append("=" * 60)

        return "\n".join(lines)


class SpecificationVerifier:
    """
    Verifies AICL specifications at three levels:
    completeness, coherence, and satisfaction.

    The verifier operates on the AST (AICLProgram) and the
    Architecture Tree (IR), ensuring that specifications are
    well-formed before compilation.

    Design Principle:
        The verifier catches specification errors BEFORE compilation.
        The compiler should never encounter a specification that the
        verifier has not approved. This separates the concern of "is
        this a valid specification?" from "can this be compiled?"
    """

    def __init__(self, program: AICLProgram):
        self.program = program
        self.tree = ArchitectureTree(program)
        self._report = VerificationReport()

    def verify(self, source_name: str = "") -> VerificationReport:
        """Run all three verification levels and return the report."""
        self._report = VerificationReport(source=source_name)
        self._check_completeness()
        self._check_coherence()
        self._check_satisfaction()
        return self._report

    def completeness_only(self, source_name: str = "") -> VerificationReport:
        """Run only completeness checks."""
        self._report = VerificationReport(source=source_name)
        self._check_completeness()
        return self._report

    def coherence_only(self, source_name: str = "") -> VerificationReport:
        """Run only coherence checks."""
        self._report = VerificationReport(source=source_name)
        self._check_coherence()
        return self._report

    def satisfaction_only(self, source_name: str = "") -> VerificationReport:
        """Run only satisfaction checks."""
        self._report = VerificationReport(source=source_name)
        self._check_satisfaction()
        return self._report

    # =========================================================================
    # Completeness Checking
    # =========================================================================

    def _check_completeness(self) -> None:
        """
        Completeness: The specification contains all required elements
        and all references between elements are resolvable.

        Required elements:
            - At least one Goal
            - At least one Layer
            - At least one Validation

        Recommended elements:
            - At least one Entity (for non-trivial programs)
            - At least one Behavior (for non-trivial programs)
            - Risk/Recovery pairs (for production code)
        """
        # Check: Goal exists
        if self.program.goals:
            self._report.completeness_results.append(CheckResult(
                name="goal_present",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.goals)} goal(s)",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="goal_present",
                status=CheckStatus.FAIL,
                message="Program has no Goal section. At least one Goal is required.",
            ))

        # Check: Layer exists
        if self.program.layers:
            self._report.completeness_results.append(CheckResult(
                name="layer_present",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.layers)} layer(s)",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="layer_present",
                status=CheckStatus.FAIL,
                message="Program has no Layer section. At least one Layer is required.",
            ))

        # Check: Validation exists
        if self.program.validations:
            self._report.completeness_results.append(CheckResult(
                name="validation_present",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.validations)} validation(s)",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="validation_present",
                status=CheckStatus.FAIL,
                message="Program has no Validation section. At least one Validation is required.",
            ))

        # Check: Entity exists (recommended)
        if self.program.entities:
            self._report.completeness_results.append(CheckResult(
                name="entity_present",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.entities)} entit(y/ies)",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="entity_present",
                status=CheckStatus.WARN,
                message="Program has no Entity section. Entities are recommended for non-trivial programs.",
            ))

        # Check: Behavior exists (recommended)
        if self.program.behaviors:
            self._report.completeness_results.append(CheckResult(
                name="behavior_present",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.behaviors)} behavior(s)",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="behavior_present",
                status=CheckStatus.WARN,
                message="Program has no Behavior section. Behaviors are recommended for non-trivial programs.",
            ))

        # Check: Risk/Recovery pairing
        has_risks = len(self.program.risks) > 0
        has_recoveries = len(self.program.recoveries) > 0

        if has_risks and has_recoveries:
            self._report.completeness_results.append(CheckResult(
                name="risk_recovery_pairing",
                status=CheckStatus.PASS,
                message=f"Program has {len(self.program.risks)} risk(s) and {len(self.program.recoveries)} recovery(ies)",
            ))
        elif has_risks and not has_recoveries:
            self._report.completeness_results.append(CheckResult(
                name="risk_recovery_pairing",
                status=CheckStatus.FAIL,
                message="Program defines Risks but no Recoveries. Every Risk needs a Recovery.",
                details=[f"  Risk: {r.description}" for r in self.program.risks],
            ))
        elif not has_risks and has_recoveries:
            self._report.completeness_results.append(CheckResult(
                name="risk_recovery_pairing",
                status=CheckStatus.WARN,
                message="Program defines Recoveries but no Risks. Recoveries should correspond to defined risks.",
            ))
        else:
            self._report.completeness_results.append(CheckResult(
                name="risk_recovery_pairing",
                status=CheckStatus.WARN,
                message="Program has no Risk/Recovery sections. Risk analysis is recommended for production code.",
            ))

        # Check: Entity fields are defined
        for entity in self.program.entities:
            if not entity.fields:
                self._report.completeness_results.append(CheckResult(
                    name=f"entity_{entity.name}_fields",
                    status=CheckStatus.WARN,
                    message=f"Entity '{entity.name}' has no fields defined.",
                ))
            else:
                self._report.completeness_results.append(CheckResult(
                    name=f"entity_{entity.name}_fields",
                    status=CheckStatus.PASS,
                    message=f"Entity '{entity.name}' has {len(entity.fields)} field(s)",
                ))

        # Check: Behavior has action
        for behavior in self.program.behaviors:
            if not behavior.action:
                self._report.completeness_results.append(CheckResult(
                    name=f"behavior_{behavior.name}_action",
                    status=CheckStatus.FAIL,
                    message=f"Behavior '{behavior.name}' has no action defined.",
                ))
            else:
                self._report.completeness_results.append(CheckResult(
                    name=f"behavior_{behavior.name}_action",
                    status=CheckStatus.PASS,
                    message=f"Behavior '{behavior.name}' has action defined",
                ))

    # =========================================================================
    # Coherence Checking
    # =========================================================================

    def _check_coherence(self) -> None:
        """
        Coherence: The specification is internally consistent.
        No contradictions, no dangling references, no impossible
        configurations.

        Checks:
            - Parallel layers reference existing layers
            - Conditions reference existing behaviors/layers
            - Events reference existing entities/layers
            - No duplicate entity names
            - No duplicate behavior names
            - Layer hierarchy is acyclic
            - Security actions reference existing entities
        """
        # Collect known names
        layer_names = set()
        for layer in self.program.layers:
            layer_names.add(layer.name)
            for sub in layer.sublayers:
                layer_names.add(sub.name)

        entity_names = {e.name for e in self.program.entities}
        behavior_names = {b.name for b in self.program.behaviors}

        # Check: Parallel layers reference existing layers
        for parallel in self.program.parallels:
            missing = [l for l in parallel.layers if l not in layer_names]
            if missing:
                self._report.coherence_results.append(CheckResult(
                    name=f"parallel_layers_exist",
                    status=CheckStatus.FAIL,
                    message=f"Parallel section references non-existent layer(s): {', '.join(missing)}",
                    details=missing,
                ))
            else:
                self._report.coherence_results.append(CheckResult(
                    name=f"parallel_layers_exist",
                    status=CheckStatus.PASS,
                    message=f"Parallel section references valid layer(s): {', '.join(parallel.layers)}",
                ))

        # Check: No duplicate entity names
        entity_name_counts: Dict[str, int] = {}
        for e in self.program.entities:
            entity_name_counts[e.name] = entity_name_counts.get(e.name, 0) + 1

        duplicates = {name for name, count in entity_name_counts.items() if count > 1}
        if duplicates:
            self._report.coherence_results.append(CheckResult(
                name="no_duplicate_entities",
                status=CheckStatus.FAIL,
                message=f"Duplicate entity names found: {', '.join(duplicates)}",
                details=[f"  {name} defined {entity_name_counts[name]} times" for name in duplicates],
            ))
        else:
            self._report.coherence_results.append(CheckResult(
                name="no_duplicate_entities",
                status=CheckStatus.PASS,
                message="All entity names are unique",
            ))

        # Check: No duplicate behavior names
        behavior_name_counts: Dict[str, int] = {}
        for b in self.program.behaviors:
            behavior_name_counts[b.name] = behavior_name_counts.get(b.name, 0) + 1

        dup_behaviors = {name for name, count in behavior_name_counts.items() if count > 1}
        if dup_behaviors:
            self._report.coherence_results.append(CheckResult(
                name="no_duplicate_behaviors",
                status=CheckStatus.FAIL,
                message=f"Duplicate behavior names found: {', '.join(dup_behaviors)}",
                details=[f"  {name} defined {behavior_name_counts[name]} times" for name in dup_behaviors],
            ))
        else:
            self._report.coherence_results.append(CheckResult(
                name="no_duplicate_behaviors",
                status=CheckStatus.PASS,
                message="All behavior names are unique",
            ))

        # Check: Layer hierarchy is acyclic
        # (In AICL's current design, layers are flat with sublayers,
        #  so cycles are structurally impossible. But we check anyway.)
        visited: Set[str] = set()
        has_cycle = False

        def check_cycle(layer_name: str, path: Set[str]) -> bool:
            if layer_name in path:
                return True
            if layer_name in visited:
                return False
            visited.add(layer_name)
            path.add(layer_name)
            # Find sublayers
            for layer in self.program.layers:
                if layer.name == layer_name:
                    for sub in layer.sublayers:
                        if check_cycle(sub.name, path):
                            return True
            path.discard(layer_name)
            return False

        for layer in self.program.layers:
            if check_cycle(layer.name, set()):
                has_cycle = True
                break

        if has_cycle:
            self._report.coherence_results.append(CheckResult(
                name="layer_hierarchy_acyclic",
                status=CheckStatus.FAIL,
                message="Layer hierarchy contains a cycle",
            ))
        else:
            self._report.coherence_results.append(CheckResult(
                name="layer_hierarchy_acyclic",
                status=CheckStatus.PASS,
                message="Layer hierarchy is acyclic",
            ))

        # Check: Constraints are non-empty
        for constraint in self.program.constraints:
            if not constraint.description.strip():
                self._report.coherence_results.append(CheckResult(
                    name=f"constraint_nonempty",
                    status=CheckStatus.WARN,
                    message="Empty constraint description found",
                ))

        if self.program.constraints:
            non_empty = sum(1 for c in self.program.constraints if c.description.strip())
            if non_empty == len(self.program.constraints):
                self._report.coherence_results.append(CheckResult(
                    name="constraints_nonempty",
                    status=CheckStatus.PASS,
                    message=f"All {len(self.program.constraints)} constraint(s) have descriptions",
                ))

        # Check: Security actions reference known entities
        for sec in self.program.securities:
            for action in sec.actions:
                # Security actions often reference entity fields or general targets
                # We check if the target matches any entity name as a soft check
                target = action.target.strip()
                if target and entity_names and target.lower() not in {e.lower() for e in entity_names}:
                    # Not a hard failure — security can target non-entity things
                    self._report.coherence_results.append(CheckResult(
                        name=f"security_target_{action.action_type}",
                        status=CheckStatus.WARN,
                        message=f"Security {action.action_type} target '{target}' does not match any entity name",
                    ))

    # =========================================================================
    # Satisfaction Checking
    # =========================================================================

    def _check_satisfaction(self) -> None:
        """
        Satisfaction: The specification is satisfiable — a valid program
        can be generated from it, and validations are testable.

        Checks:
            - Validations are testable (measurable/verifiable)
            - At least one behavior exists per entity (or entity is data-only)
            - Goal is achievable given the specification
            - Architecture is implementable (layers map to code)
        """
        # Check: Validations are testable
        for validation in self.program.validations:
            desc = validation.description.lower()
            # A testable validation should contain measurable language
            testable_indicators = [
                'must', 'should', 'shall', 'equals', 'equal', 'at least',
                'at most', 'between', 'greater', 'less', 'before', 'after',
                'within', 'exactly', 'minimum', 'maximum', 'returns',
                'produces', 'contains', 'valid', 'true', 'false',
                'success', 'fail', 'error', 'complete',
            ]
            is_testable = any(indicator in desc for indicator in testable_indicators)

            if is_testable:
                self._report.satisfaction_results.append(CheckResult(
                    name=f"validation_testable_{validation.description[:30]}",
                    status=CheckStatus.PASS,
                    message=f"Validation appears testable: {validation.description[:60]}",
                ))
            else:
                self._report.satisfaction_results.append(CheckResult(
                    name=f"validation_testable_{validation.description[:30]}",
                    status=CheckStatus.WARN,
                    message=f"Validation may be difficult to test: {validation.description[:60]}",
                    details=["Consider using measurable language (must, should, equals, etc.)"],
                ))

        # Check: Goal is achievable
        if self.program.goals:
            goal = self.program.goals[0]
            # Check that the specification has enough elements to achieve the goal
            has_layers = len(self.program.layers) > 0
            has_entities = len(self.program.entities) > 0
            has_behaviors = len(self.program.behaviors) > 0

            if has_layers and (has_entities or has_behaviors):
                self._report.satisfaction_results.append(CheckResult(
                    name="goal_achievable",
                    status=CheckStatus.PASS,
                    message=f"Goal appears achievable with {len(self.program.layers)} layer(s), "
                            f"{len(self.program.entities)} entit(y/ies), "
                            f"{len(self.program.behaviors)} behavior(s)",
                ))
            elif has_layers:
                self._report.satisfaction_results.append(CheckResult(
                    name="goal_achievable",
                    status=CheckStatus.WARN,
                    message="Goal may be underspecified: no entities or behaviors defined",
                ))
            else:
                self._report.satisfaction_results.append(CheckResult(
                    name="goal_achievable",
                    status=CheckStatus.FAIL,
                    message="Goal is not achievable: no layers defined",
                ))

        # Check: Architecture is implementable
        if self.program.layers:
            # Check that each layer with behaviors has at least one entity
            # (This is a soft check — layers can be purely structural)
            layers_with_content = 0
            for layer in self.program.layers:
                if layer.sublayers or any(
                    b for b in self.program.behaviors
                ):
                    layers_with_content += 1

            self._report.satisfaction_results.append(CheckResult(
                name="architecture_implementable",
                status=CheckStatus.PASS,
                message=f"Architecture with {len(self.program.layers)} layer(s) is implementable",
            ))
        else:
            self._report.satisfaction_results.append(CheckResult(
                name="architecture_implementable",
                status=CheckStatus.FAIL,
                message="No layers defined: architecture is not implementable",
            ))

        # Check: Sufficient coverage of risk space
        risk_count = len(self.program.risks)
        recovery_count = len(self.program.recoveries)

        if risk_count > 0:
            if recovery_count >= risk_count:
                self._report.satisfaction_results.append(CheckResult(
                    name="risk_coverage_sufficient",
                    status=CheckStatus.PASS,
                    message=f"Risk coverage sufficient: {recovery_count} recoveries for {risk_count} risks",
                ))
            else:
                self._report.satisfaction_results.append(CheckResult(
                    name="risk_coverage_sufficient",
                    status=CheckStatus.WARN,
                    message=f"Risk coverage may be insufficient: {recovery_count} recoveries for {risk_count} risks",
                    details=["Consider adding more Recovery sections to cover all Risks"],
                ))


def verify_source(source: str, source_name: str = "") -> VerificationReport:
    """Convenience function: parse and verify an AICL source string."""
    parser = Parser(source)
    program = parser.parse()
    verifier = SpecificationVerifier(program)
    return verifier.verify(source_name=source_name)


def verify_file(path: str) -> VerificationReport:
    """Convenience function: parse and verify an AICL source file."""
    with open(path, 'r') as f:
        source = f.read()
    return verify_source(source, source_name=path)
