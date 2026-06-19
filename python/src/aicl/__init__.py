"""
AICL — Artificial Intelligence-Centered Language
Specification-first programming with mandatory Risk/Recovery syntax,
the AX Turing-complete sub-language, and cryptographic Proof of Origin.
Compiles to Python, Rust, JavaScript, and Go.

Version: 2.1.0
Author: Philippe-Antoine
"""

__version__ = "2.1.0"
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
    GeneratedArtifact, ArtifactType, ProofOfOrigin,
)
from .spec_verify import (
    SpecificationVerifier, VerificationReport, CheckResult, CheckStatus,
    verify_source, verify_file,
)
from .modules import (
    ModuleRegistry, ModuleResolver, CompiledModule,
    ModuleExport, ImportDeclaration, CrossFileProvenance,
    compile_multi_file, parse_imports, extract_exports,
)
from .crypto_signing import (
    ProofSigner, ProofSignature, ProofChainLink,
    create_signed_proof, verify_signed_proof,
)
from .runtime import (
    RuntimeEnvironment, RuntimeProvenance, RuntimeProvenanceEvent,
    RuntimeEventType, RecoveryExecutor, RiskRecoveryBinding,
)
from .ownership import (
    OwnershipAnalyzer, OwnershipReport, OwnershipRelation,
    OwnershipKind, Lifetime, generate_ownership_code,
)
from .auto_optimizer import (
    ArchitectureOptimizer, OptimizationResult, OptimizationAction,
    OptimizationStrategy,
)
from .autonomous import (
    AutonomousCompiler, AutonomousResult, LoopController,
    PatternLearner, SpecEvolver, TestRunner,
    LoopState, LoopIteration, format_evolve_report,
)
from .ai_generator import (
    AICLGenerator, AIDiagnoser, SelfWritingCompiler,
    AIGenerationResult, is_ai_available, format_create_report,
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
    "GeneratedArtifact", "ArtifactType", "ProofOfOrigin",
    # v0.9: Specification Verification
    "SpecificationVerifier", "VerificationReport", "CheckResult", "CheckStatus",
    "verify_source", "verify_file",
    # v0.10: Multi-file Programs
    "ModuleRegistry", "ModuleResolver", "CompiledModule",
    "ModuleExport", "ImportDeclaration", "CrossFileProvenance",
    "compile_multi_file", "parse_imports", "extract_exports",
    # v0.11: Cryptographic Proof Signing
    "ProofSigner", "ProofSignature", "ProofChainLink",
    "create_signed_proof", "verify_signed_proof",
    # v2.0: Self-healing Runtime
    "RuntimeEnvironment", "RuntimeProvenance", "RuntimeProvenanceEvent",
    "RuntimeEventType", "RecoveryExecutor", "RiskRecoveryBinding",
    # v2.5: Memory Management
    "OwnershipAnalyzer", "OwnershipReport", "OwnershipRelation",
    "OwnershipKind", "Lifetime", "generate_ownership_code",
    # v3.0: Autonomous Architecture Optimization
    "ArchitectureOptimizer", "OptimizationResult", "OptimizationAction",
    "OptimizationStrategy",
    # v1.1: Autonomous Self-Writing, Self-Validating Compilation
    "AutonomousCompiler", "AutonomousResult", "LoopController",
    "PatternLearner", "SpecEvolver", "TestRunner",
    "LoopState", "LoopIteration", "format_evolve_report",
    # v1.2: AI-Powered Self-Writing Compiler
    "AICLGenerator", "AIDiagnoser", "SelfWritingCompiler",
    "AIGenerationResult", "is_ai_available", "format_create_report",
]
