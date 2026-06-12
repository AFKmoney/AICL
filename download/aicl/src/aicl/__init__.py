"""
AICL - Architecture Compilation Language
Auditable Compilation: if the compiler cannot explain why, it does not generate.

Version: 0.5.0
Author: Philippe-Antoine
"""

__version__ = "0.5.0"
__author__ = "Philippe-Antoine"

from .parser import Parser, ParseError
from .ast import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, AdaptSection, SecuritySection,
    NativeSection, EntityField, BehaviorInput, BehaviorOutput,
    SecurityAction,
)
from .ir import ArchitectureTree, ArchitectureNode
from .compiler import Compiler, CompilationResult
from .patterns import (
    BehaviorPatternLibrary, BehaviorCompiler,
    SubLanguageParser, ArchitectureTemplateMapper,
)
from .provenance import (
    CompilationProvenance, ProvenanceType, ProvenanceRecord,
    GeneratedArtifact, ArtifactType,
)

__all__ = [
    "Parser", "ParseError",
    "AICLProgram", "GoalSection", "ConstraintSection", "RiskSection",
    "RecoverySection", "LayerSection", "ValidationSection", "EntitySection",
    "BehaviorSection", "ConditionSection", "EventSection", "ParallelSection",
    "OptimizeSection", "LearnSection", "AdaptSection", "SecuritySection",
    "NativeSection", "EntityField", "BehaviorInput", "BehaviorOutput",
    "SecurityAction",
    "ArchitectureTree", "ArchitectureNode",
    "Compiler", "CompilationResult",
    "BehaviorPatternLibrary", "BehaviorCompiler",
    "SubLanguageParser", "ArchitectureTemplateMapper",
    "CompilationProvenance", "ProvenanceType", "ProvenanceRecord",
    "GeneratedArtifact", "ArtifactType",
]
