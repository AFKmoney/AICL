"""
AICL AST Node Definitions

Defines the Abstract Syntax Tree nodes that represent the structure
of an AICL program after parsing. Each node corresponds to a section
or element of the AICL language specification.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


# =============================================================================
# Level 1 - Architecture (Core)
# =============================================================================

@dataclass
class GoalSection(ASTNode):
    """Defines the intended outcome of the system."""
    description: str = ""


@dataclass
class ConstraintSection(ASTNode):
    """Defines a system limitation or requirement."""
    description: str = ""


@dataclass
class RiskSection(ASTNode):
    """Defines a known failure condition."""
    description: str = ""


@dataclass
class RecoverySection(ASTNode):
    """Defines a corrective action for a risk."""
    description: str = ""


@dataclass
class LayerSection(ASTNode):
    """Defines an architectural layer."""
    name: str = ""
    sublayers: List['LayerSection'] = field(default_factory=list)


@dataclass
class ValidationSection(ASTNode):
    """Defines a measurable success criterion."""
    description: str = ""


# =============================================================================
# Level 2 - Entities
# =============================================================================

@dataclass
class EntityField(ASTNode):
    """A field within an entity definition."""
    name: str = ""
    field_type: str = ""


@dataclass
class EntitySection(ASTNode):
    """Defines a data entity within the system."""
    name: str = ""
    fields: List[EntityField] = field(default_factory=list)


# =============================================================================
# Level 3 - Behaviors
# =============================================================================

@dataclass
class BehaviorInput(ASTNode):
    """Input parameter for a behavior."""
    name: str = ""
    param_type: str = ""


@dataclass
class BehaviorOutput(ASTNode):
    """Output specification for a behavior."""
    name: str = ""
    output_type: str = ""


@dataclass
class BehaviorSection(ASTNode):
    """Defines what an entity does."""
    name: str = ""
    inputs: List[BehaviorInput] = field(default_factory=list)
    output: Optional[BehaviorOutput] = None
    action: str = ""


# =============================================================================
# Level 4 - Conditions
# =============================================================================

@dataclass
class ConditionSection(ASTNode):
    """Replaces traditional if/else with When/Then."""
    when_clause: str = ""
    then_clause: str = ""


# =============================================================================
# Level 5 - Events
# =============================================================================

@dataclass
class EventSection(ASTNode):
    """Defines event-driven behavior."""
    on_clause: str = ""
    action: str = ""


# =============================================================================
# Level 6 - Concurrency
# =============================================================================

@dataclass
class ParallelSection(ASTNode):
    """Defines concurrent execution of layers."""
    layers: List[str] = field(default_factory=list)


# =============================================================================
# Level 7 - Optimization
# =============================================================================

@dataclass
class OptimizeSection(ASTNode):
    """Defines optimization targets."""
    target: str = ""
    priority: str = ""


# =============================================================================
# Level 8 - Learning
# =============================================================================

@dataclass
class LearnSection(ASTNode):
    """Defines what the system should learn."""
    subject: str = ""
    goal: str = ""


@dataclass
class AdaptSection(ASTNode):
    """Defines adaptive behavior."""
    subject: str = ""
    based_on: str = ""


# =============================================================================
# Level 9 - Security
# =============================================================================

@dataclass
class SecurityAction(ASTNode):
    """A security action (encrypt or protect)."""
    action_type: str = ""  # "encrypt" or "protect"
    target: str = ""


@dataclass
class SecuritySection(ASTNode):
    """Defines security requirements."""
    actions: List[SecurityAction] = field(default_factory=list)


# =============================================================================
# Level 10 - Native Code
# =============================================================================

@dataclass
class NativeSection(ASTNode):
    """Inline native code in another language."""
    language: str = ""
    code: str = ""


# =============================================================================
# Top-Level Program
# =============================================================================

@dataclass
class AICLProgram(ASTNode):
    """
    The root node of an AICL program.

    Contains all sections that define the complete specification
    of a software system.
    """
    goals: List[GoalSection] = field(default_factory=list)
    constraints: List[ConstraintSection] = field(default_factory=list)
    risks: List[RiskSection] = field(default_factory=list)
    recoveries: List[RecoverySection] = field(default_factory=list)
    layers: List[LayerSection] = field(default_factory=list)
    validations: List[ValidationSection] = field(default_factory=list)
    entities: List[EntitySection] = field(default_factory=list)
    behaviors: List[BehaviorSection] = field(default_factory=list)
    conditions: List[ConditionSection] = field(default_factory=list)
    events: List[EventSection] = field(default_factory=list)
    parallels: List[ParallelSection] = field(default_factory=list)
    optimizations: List[OptimizeSection] = field(default_factory=list)
    learns: List[LearnSection] = field(default_factory=list)
    adapts: List[AdaptSection] = field(default_factory=list)
    securities: List[SecuritySection] = field(default_factory=list)
    natives: List[NativeSection] = field(default_factory=list)

    def get_all_sections(self) -> List[ASTNode]:
        """Return a flat list of all sections in the program."""
        sections: List[ASTNode] = []
        sections.extend(self.goals)
        sections.extend(self.constraints)
        sections.extend(self.risks)
        sections.extend(self.recoveries)
        sections.extend(self.layers)
        sections.extend(self.validations)
        sections.extend(self.entities)
        sections.extend(self.behaviors)
        sections.extend(self.conditions)
        sections.extend(self.events)
        sections.extend(self.parallels)
        sections.extend(self.optimizations)
        sections.extend(self.learns)
        sections.extend(self.adapts)
        sections.extend(self.securities)
        sections.extend(self.natives)
        return sections

    def validate(self) -> List[str]:
        """
        Validate the program structure and return a list of warnings.

        A valid AICL program must have at least one Goal, one Layer,
        and one Validation section.
        """
        warnings = []

        if not self.goals:
            warnings.append("Program has no Goal section. At least one Goal is required.")
        if not self.layers:
            warnings.append("Program has no Layer section. At least one Layer is required.")
        if not self.validations:
            warnings.append("Program has no Validation section. At least one Validation is required.")

        # Check that every Risk has at least one Recovery
        if self.risks and not self.recoveries:
            warnings.append("Program defines Risks but no Recovery sections. "
                            "Consider adding recovery procedures for each risk.")

        # Check for orphaned Recoveries (no matching Risk)
        if self.recoveries and not self.risks:
            warnings.append("Program defines Recoveries but no Risk sections. "
                            "Recoveries should correspond to defined risks.")

        return warnings
