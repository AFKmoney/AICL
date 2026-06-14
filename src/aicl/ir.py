"""
AICL Architecture Tree - Intermediate Representation

The Architecture Tree is the central IR of the AICL compiler.
It transforms the flat list of AST sections into a hierarchical
tree structure that represents the system's architecture, with
risk/recovery pairs and validation criteria attached.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .ast import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, AdaptSection, SecuritySection,
    NativeSection,
)


@dataclass
class ArchitectureNode:
    """
    A node in the Architecture Tree.

    Each node represents an architectural layer with associated
    risks, recoveries, validations, behaviors, conditions, events,
    and sublayers.
    """
    name: str
    node_type: str = "layer"  # layer, entity, behavior, root
    goal: str = ""
    risks: List[str] = field(default_factory=list)
    recoveries: List[str] = field(default_factory=list)
    validations: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    optimization_targets: List[str] = field(default_factory=list)
    security_actions: List[str] = field(default_factory=list)
    children: List['ArchitectureNode'] = field(default_factory=list)
    parent: Optional['ArchitectureNode'] = None

    def add_child(self, child: 'ArchitectureNode') -> None:
        """Add a child node and set its parent reference."""
        child.parent = self
        self.children.append(child)

    def find_node(self, name: str) -> Optional['ArchitectureNode']:
        """Find a node by name in the subtree."""
        if self.name == name:
            return self
        for child in self.children:
            result = child.find_node(name)
            if result:
                return result
        return None

    def depth(self) -> int:
        """Return the depth of this node in the tree."""
        depth = 0
        node = self
        while node.parent:
            depth += 1
            node = node.parent
        return depth

    def to_dict(self) -> Dict:
        """Convert the tree to a dictionary representation."""
        return {
            "name": self.name,
            "type": self.node_type,
            "goal": self.goal,
            "risks": self.risks,
            "recoveries": self.recoveries,
            "validations": self.validations,
            "constraints": self.constraints,
            "behaviors": self.behaviors,
            "conditions": self.conditions,
            "events": self.events,
            "optimization_targets": self.optimization_targets,
            "security_actions": self.security_actions,
            "children": [child.to_dict() for child in self.children],
        }

    def to_tree_string(self, indent: int = 0) -> str:
        """Render the tree as a human-readable string with indentation."""
        prefix = "  " * indent
        connector = "├── " if indent > 0 else ""
        lines = [f"{prefix}{connector}{self.name}"]

        if self.risks:
            for risk in self.risks:
                lines.append(f"{prefix}  │ ⚠ Risk: {risk}")
        if self.recoveries:
            for rec in self.recoveries:
                lines.append(f"{prefix}  │ ↻ Recovery: {rec}")
        if self.validations:
            for val in self.validations:
                lines.append(f"{prefix}  │ ✓ Validation: {val}")
        if self.constraints:
            for con in self.constraints:
                lines.append(f"{prefix}  │ ⊘ Constraint: {con}")

        for i, child in enumerate(self.children):
            if i == len(self.children) - 1:
                lines.append(f"{prefix}  └── {child.to_tree_string(indent + 2).strip()}")
            else:
                lines.append(f"{prefix}  ├── {child.to_tree_string(indent + 2).strip()}")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        return f"ArchitectureNode({self.name!r}, type={self.node_type!r}, children={len(self.children)})"


class ArchitectureTree:
    """
    The Architecture Tree is the Intermediate Representation (IR) of the AICL compiler.

    It is constructed from an AICLProgram AST and provides a hierarchical
    view of the system architecture with associated risks, recoveries,
    validations, and constraints.

    The Architecture Tree serves as the primary data structure for:
    - Dependency analysis
    - Risk propagation
    - Code generation
    - Test generation
    """

    def __init__(self, program: AICLProgram):
        self.program = program
        self.root = ArchitectureNode(name="System", node_type="root")
        self._build()

    def _build(self) -> None:
        """Build the Architecture Tree from the program AST."""
        # Set root goal
        if self.program.goals:
            self.root.goal = self.program.goals[0].description

        # Add global risks and recoveries to root
        for risk in self.program.risks:
            self.root.risks.append(risk.description)
        for recovery in self.program.recoveries:
            self.root.recoveries.append(recovery.description)
        for validation in self.program.validations:
            self.root.validations.append(validation.description)
        for constraint in self.program.constraints:
            self.root.constraints.append(constraint.description)

        # Build layer hierarchy
        for layer in self.program.layers:
            layer_node = ArchitectureNode(
                name=layer.name, node_type="layer"
            )
            # Add sublayers
            for sublayer in layer.sublayers:
                sublayer_node = ArchitectureNode(
                    name=sublayer.name, node_type="layer"
                )
                layer_node.add_child(sublayer_node)
            self.root.add_child(layer_node)

        # Add entity nodes
        for entity in self.program.entities:
            entity_node = ArchitectureNode(
                name=entity.name, node_type="entity"
            )
            self.root.add_child(entity_node)

        # Add behavior nodes
        for behavior in self.program.behaviors:
            behavior_node = ArchitectureNode(
                name=behavior.name, node_type="behavior",
                behaviors=[behavior.action] if behavior.action else []
            )
            self.root.add_child(behavior_node)

        # Propagate conditions to relevant layers
        for condition in self.program.conditions:
            # Conditions apply globally; compiler will distribute
            self.root.conditions.append(
                f"WHEN {condition.when_clause} THEN {condition.then_clause}"
            )

        # Propagate events to relevant layers
        for event in self.program.events:
            self.root.events.append(
                f"ON {event.on_clause} DO {event.action}"
            )

        # Add optimization targets
        for opt in self.program.optimizations:
            self.root.optimization_targets.append(opt.target)

        # Add security actions
        for sec in self.program.securities:
            for action in sec.actions:
                self.root.security_actions.append(
                    f"{action.action_type}: {action.target}"
                )

        # Distribute risks and recoveries to layers if possible
        self._distribute_risks()

    def _distribute_risks(self) -> None:
        """
        Attempt to distribute global risks and recoveries to specific layers
        based on keyword matching.
        """
        for risk in self.program.risks:
            risk_words = set(risk.description.lower().split())
            best_layer = None
            best_score = 0

            for child in self.root.children:
                layer_words = set(child.name.lower().split())
                score = len(risk_words & layer_words)
                if score > best_score:
                    best_score = score
                    best_layer = child

            # Only distribute if there's a meaningful match
            # (score >= 1 means at least one word overlaps)

    def find_layer(self, name: str) -> Optional[ArchitectureNode]:
        """Find a layer node by name."""
        return self.root.find_node(name)

    def get_all_layers(self) -> List[ArchitectureNode]:
        """Get all layer nodes in the tree (depth-first)."""
        layers = []
        for child in self.root.children:
            if child.node_type == "layer":
                layers.append(child)
                self._collect_layers(child, layers)
        return layers

    def _collect_layers(self, node: ArchitectureNode, result: List[ArchitectureNode]) -> None:
        """Recursively collect all layer nodes."""
        for child in node.children:
            if child.node_type == "layer":
                result.append(child)
                self._collect_layers(child, result)

    def get_dependency_order(self) -> List[ArchitectureNode]:
        """
        Return layers in dependency order (topological sort).

        Layers at the top of the architecture (closest to root) come first,
        as they typically depend on layers below them.
        """
        order = []
        visited = set()

        def visit(node: ArchitectureNode) -> None:
            if node.name in visited:
                return
            visited.add(node.name)
            for child in node.children:
                visit(child)
            order.append(node)

        for child in self.root.children:
            visit(child)

        return order

    def to_dict(self) -> Dict:
        """Convert the entire tree to a dictionary."""
        return self.root.to_dict()

    def to_string(self) -> str:
        """Render the tree as a human-readable string."""
        return self.root.to_tree_string()

    def __repr__(self) -> str:
        return f"ArchitectureTree(root={self.root})"
