"""
Base class for AICL target code generators.

Defines the interface that all target generators must implement,
and provides common utilities for code generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from ..compiler import CompilationResult


@dataclass
class TargetCodeResult:
    """Result of generating code for a specific target language."""
    target_language: str = ""
    source_code: str = ""
    test_code: str = ""
    project_files: Dict[str, str] = field(default_factory=dict)
    build_instructions: str = ""
    warnings: List[str] = field(default_factory=list)


class TargetGenerator(ABC):
    """
    Abstract base class for target code generators.

    Each target language implements this interface to produce
    idiomatic code from AICL compilation results.

    Design Principle:
        Target generators translate the COMPILATION RESULT, not the
        AICL source directly. The compilation result already contains
        the structured data (entities, behaviors, risk/recovery pairs)
        that the target generator maps to language-specific constructs.

        The provenance chain from the original compilation is preserved
        in the proof file — the target generator does not modify it.
    """

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Name of the target language."""
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for source files (e.g., '.rs', '.js', '.go')."""
        ...

    @abstractmethod
    def generate(self, result: CompilationResult) -> TargetCodeResult:
        """
        Generate target language code from a compilation result.

        Args:
            result: The AICL compilation result

        Returns:
            TargetCodeResult with generated code and project files
        """
        ...

    @abstractmethod
    def generate_test(self, result: CompilationResult) -> str:
        """
        Generate test code for the target language.

        Args:
            result: The AICL compilation result

        Returns:
            Test code as a string
        """
        ...

    def _indent(self, code: str, indent: int = 4) -> str:
        """Indent code by the given number of spaces."""
        prefix = " " * indent
        return "\n".join(prefix + line if line.strip() else line
                         for line in code.split("\n"))

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to CamelCase."""
        return "".join(part.capitalize() for part in name.split("_"))

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return "".join(part.capitalize() for part in name.split("_"))
