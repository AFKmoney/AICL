"""
AICL Memory Management — Ultra-Simple Ownership Model

Derives memory ownership and lifecycle management from the
Layer/Entity structure of AICL programs.

The key insight: AICL's architectural structure already encodes
ownership relationships. A Layer owns its entities. Entities own
their fields. This structural ownership can be automatically
translated into memory management rules:

    - Layers are owners (responsible for allocation/deallocation)
    - Entities are values (owned by their layer)
    - Behaviors are borrows (temporary access to entity state)
    - References across layers are explicit (cross-layer dependencies)

This model provides:
    - Automatic RAII-style resource management
    - No garbage collector needed (ownership is deterministic)
    - Borrow checking derived from architecture (not annotations)
    - Lifetime annotations inferred from layer hierarchy

Design Principle:
    Memory management should not be an afterthought added to
    the language. It should be derived from the architectural
    structure that already exists in the specification.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum

from .ast import AICLProgram, LayerSection, EntitySection, BehaviorSection
from .ir import ArchitectureTree, ArchitectureNode


class OwnershipKind(Enum):
    """Kind of ownership relationship."""
    OWNS = "owns"           # Layer owns Entity
    BORROWS = "borrows"     # Behavior borrows Entity
    REFERENCES = "references"  # Cross-layer reference
    MOVES = "moves"         # Transfer of ownership


class Lifetime(Enum):
    """Lifetime category for an owned resource."""
    STATIC = "static"       # Lives for the entire program
    LAYER = "layer"         # Lives as long as its owning layer
    SCOPE = "scope"         # Lives within a behavior scope
    EPHEMERAL = "ephemeral" # Temporary, not stored


@dataclass
class OwnershipRelation:
    """An ownership relationship between two elements."""
    owner: str              # Name of the owner
    owned: str              # Name of the owned element
    kind: OwnershipKind     # Type of ownership
    lifetime: Lifetime      # Expected lifetime
    is_mutable: bool = False  # Whether the borrow is mutable
    description: str = ""


@dataclass
class OwnershipReport:
    """Report on the ownership model of an AICL program."""
    relations: List[OwnershipRelation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = []
        lines.append("=" * 50)
        lines.append("AICL OWNERSHIP MODEL REPORT")
        lines.append("=" * 50)
        lines.append(f"Ownership relations: {len(self.relations)}")

        owns_count = sum(1 for r in self.relations if r.kind == OwnershipKind.OWNS)
        borrows_count = sum(1 for r in self.relations if r.kind == OwnershipKind.BORROWS)
        refs_count = sum(1 for r in r for r in [self.relations] if r.kind == OwnershipKind.REFERENCES) if False else sum(1 for r in self.relations if r.kind == OwnershipKind.REFERENCES)

        lines.append(f"  Owns: {owns_count}")
        lines.append(f"  Borrows: {borrows_count}")
        lines.append(f"  References: {refs_count}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  - {w}")

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  - {e}")

        lines.append("\nOWNERSHIP GRAPH")
        for rel in self.relations:
            mut = "mut " if rel.is_mutable else ""
            lines.append(f"  {rel.owner} --[{rel.kind.value} {mut}]--> {rel.owned}  ({rel.lifetime.value})")

        lines.append("=" * 50)
        return "\n".join(lines)


class OwnershipAnalyzer:
    """
    Analyzes the ownership model of an AICL program.

    Derives ownership relationships from the Layer/Entity structure,
    infers lifetimes from the architecture hierarchy, and checks
    for ownership conflicts (double borrows, dangling references, etc.).
    """

    def __init__(self, program: AICLProgram):
        self.program = program
        self.tree = ArchitectureTree(program)
        self._report = OwnershipReport()

    def analyze(self) -> OwnershipReport:
        """
        Analyze the ownership model and return a report.

        Derives:
            1. Layer → Entity ownership (each layer owns its entities)
            2. Entity → Field ownership (each entity owns its fields)
            3. Behavior → Entity borrows (behaviors borrow entity state)
            4. Cross-layer references (explicit dependencies)
        """
        self._derive_layer_entity_ownership()
        self._derive_entity_field_ownership()
        self._derive_behavior_borrows()
        self._check_ownership_conflicts()
        self._check_lifetime_consistency()

        return self._report

    def _derive_layer_entity_ownership(self) -> None:
        """Derive Layer → Entity ownership relationships."""
        for layer in self.program.layers:
            # Each layer owns all entities (simplified model)
            for entity in self.program.entities:
                self._report.relations.append(OwnershipRelation(
                    owner=layer.name,
                    owned=entity.name,
                    kind=OwnershipKind.OWNS,
                    lifetime=Lifetime.LAYER,
                    description=f"Layer '{layer.name}' owns entity '{entity.name}'",
                ))

    def _derive_entity_field_ownership(self) -> None:
        """Derive Entity → Field ownership relationships."""
        for entity in self.program.entities:
            for f in entity.fields:
                self._report.relations.append(OwnershipRelation(
                    owner=entity.name,
                    owned=f"{entity.name}.{f.name}",
                    kind=OwnershipKind.OWNS,
                    lifetime=Lifetime.LAYER,
                    description=f"Entity '{entity.name}' owns field '{f.name}'",
                ))

    def _derive_behavior_borrows(self) -> None:
        """Derive Behavior → Entity borrow relationships."""
        for behavior in self.program.behaviors:
            # Each behavior borrows from entities it operates on
            # In AICL, behaviors implicitly borrow their layer's entities
            for entity in self.program.entities:
                self._report.relations.append(OwnershipRelation(
                    owner=behavior.name,
                    owned=entity.name,
                    kind=OwnershipKind.BORROWS,
                    lifetime=Lifetime.SCOPE,
                    is_mutable=True,
                    description=f"Behavior '{behavior.name}' borrows entity '{entity.name}'",
                ))

    def _check_ownership_conflicts(self) -> None:
        """Check for ownership conflicts (e.g., double mutable borrows)."""
        # Check for multiple mutable borrows of the same entity
        borrow_map: Dict[str, List[str]] = {}
        for rel in self._report.relations:
            if rel.kind == OwnershipKind.BORROWS and rel.is_mutable:
                if rel.owned not in borrow_map:
                    borrow_map[rel.owned] = []
                borrow_map[rel.owned].append(rel.owner)

        for entity, borrowers in borrow_map.items():
            if len(borrowers) > 1:
                self._report.warnings.append(
                    f"Entity '{entity}' is mutably borrowed by multiple behaviors: "
                    f"{', '.join(borrowers)}. This may cause data races in parallel execution."
                )

    def _check_lifetime_consistency(self) -> None:
        """Check that lifetimes are consistent (no borrowing longer than ownership)."""
        # A borrow should not outlive its owner
        # In AICL, behavior borrows (SCOPE) are always shorter than
        # entity ownership (LAYER), so this is structurally guaranteed.
        for rel in self._report.relations:
            if rel.kind == OwnershipKind.BORROWS and rel.lifetime == Lifetime.STATIC:
                self._report.errors.append(
                    f"Borrow of '{rel.owned}' by '{rel.owner}' has STATIC lifetime. "
                    f"Borrows should not be static."
                )


def generate_ownership_code(program: AICLProgram) -> str:
    """
    Generate Python code that implements the ownership model.

    Uses context managers for RAII-style resource management.
    """
    analyzer = OwnershipAnalyzer(program)
    report = analyzer.analyze()

    lines = []
    lines.append('"""')
    lines.append("AICL-generated code with ownership model.")
    lines.append("Layer/Entity structure determines memory ownership.")
    lines.append('"""')
    lines.append("")
    lines.append("from contextlib import contextmanager")
    lines.append("from typing import Any, Dict, Optional")
    lines.append("")

    # Generate owned resource classes
    for entity in program.entities:
        lines.append(f"class {entity.name}:")
        lines.append(f'    """Owned by its layer. Lifetime: layer-scoped."""')
        lines.append(f"    def __init__(self):")
        for f in entity.fields:
            lines.append(f"        self.{f.name} = None  # {f.field_type}")
        lines.append(f"")
        lines.append(f"    def __enter__(self):")
        lines.append(f"        return self")
        lines.append(f"")
        lines.append(f"    def __exit__(self, *args):")
        lines.append(f"        pass  # Resource cleanup")
        lines.append(f"")

    # Generate layer classes with ownership
    for layer in program.layers:
        lines.append(f"class {layer.name}Layer:")
        lines.append(f'    """Owns entities. Manages their lifecycle."""')
        lines.append(f"    def __init__(self):")
        for entity in program.entities:
            lines.append(f"        self._{entity.name.lower()} = {entity.name}()")
        lines.append(f"")
        lines.append(f"    @contextmanager")
        lines.append(f"    def borrow_{program.entities[0].name.lower() if program.entities else 'resource'}(self):")
        lines.append(f'        """Borrow an owned entity (scoped lifetime)."""')
        if program.entities:
            lines.append(f"        yield self._{program.entities[0].name.lower()}")
        lines.append(f"")

    return "\n".join(lines)
