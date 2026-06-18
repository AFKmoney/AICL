"""
AICL Target Code Generators — Multi-Language Compilation

Provides code generation backends for multiple target languages:
    - Python (default, mature)
    - Rust (systems-level safety)
    - JavaScript (web/NPM ecosystem)
    - Go (cloud/infrastructure)

Each target implements the TargetGenerator interface, producing
idiomatic code in the target language while preserving the
provenance chain from the AICL source.

The generated code includes:
    - Error handling derived from Risk/Recovery pairs
    - Validation functions from Validation sections
    - Entity structures as language-appropriate types
    - Behavior methods with deterministic patterns
    - Import statements for the target language's ecosystem

Usage:
    from aicl.targets import get_target_generator, list_targets

    generator = get_target_generator("rust")
    code = generator.generate(compilation_result)
"""

from .base import TargetGenerator, TargetCodeResult
from .rust import RustGenerator
from .javascript import JavaScriptGenerator
from .go import GoGenerator


def get_target_generator(target: str) -> TargetGenerator:
    """Get a target code generator by language name."""
    generators = {
        "rust": RustGenerator,
        "javascript": JavaScriptGenerator,
        "js": JavaScriptGenerator,
        "go": GoGenerator,
        "python": None,  # Python uses the built-in compiler
    }

    gen_class = generators.get(target.lower())
    if gen_class is None:
        if target.lower() == "python":
            raise ValueError("Python target uses the built-in compiler. Use Compiler() directly.")
        raise ValueError(f"Unknown target language: {target}. Available: {list_targets()}")

    return gen_class()


def list_targets() -> list:
    """List available target languages."""
    return ["rust", "javascript", "go"]


__all__ = [
    "TargetGenerator", "TargetCodeResult",
    "RustGenerator", "JavaScriptGenerator", "GoGenerator",
    "get_target_generator", "list_targets",
]
