"""
AICL - AI-Centric Language
A specification-first programming language for AI-native software development.

Version: 0.2.0
Author: Philippe-Antoine
"""

__version__ = "0.2.0"
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
