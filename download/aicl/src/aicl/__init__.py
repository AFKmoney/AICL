"""
AICL - AI-Centric Language
Architecture is the program. Risks are syntax. Validations compile.

Version: 0.3.0
Author: Philippe-Antoine
"""

__version__ = "0.3.0"
__author__ = "Philippe-Antoine"

from .parser import Parser, ParseError
from .ast_nodes import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, AdaptSection, SecuritySection,
    NativeSection, EntityField, BehaviorInput, BehaviorOutput,
    SecurityAction,
)
from .architecture_tree import ArchitectureTree, ArchitectureNode
from .compiler import Compiler, CompilationResult
from .patterns import (
    BehaviorPatternLibrary, BehaviorCompiler,
    SubLanguageParser, ArchitectureTemplateMapper,
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
]
