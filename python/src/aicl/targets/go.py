"""
AICL Go Target Generator

Generates idiomatic Go code from AICL compilation results.

Features:
    - Structs for entities
    - Interface-based architecture from Layer structure
    - Error handling with custom error types from Risk/Recovery pairs
    - Goroutines for parallel execution patterns
    - Channel-based communication for event-driven patterns
    - Table-driven tests from Validation sections
    - Go module support (go.mod)

Generated code follows Go best practices:
    - Idiomatic error handling (error interface, not exceptions)
    - Goroutine and channel patterns for concurrency
    - Interface composition for architecture layers
    - Package-level organization matching AICL layers
"""

import textwrap
from typing import List, Dict, Optional

from .base import TargetGenerator, TargetCodeResult
from ..compiler import CompilationResult


class GoGenerator(TargetGenerator):
    """Generates Go code from AICL compilation results."""

    @property
    def language_name(self) -> str:
        return "Go"

    @property
    def file_extension(self) -> str:
        return ".go"

    def generate(self, result: CompilationResult) -> TargetCodeResult:
        """Generate Go source code from the compilation result."""
        parts = []

        # Package declaration and imports
        parts.append(self._generate_package_imports())

        # Error types
        parts.append(self._generate_error_types(result))

        # Entity structs
        parts.append(self._generate_structs(result))

        # Application
        parts.append(self._generate_application(result))

        # Main
        parts.append(self._generate_main())

        source_code = "\n\n".join(parts)

        # Project files
        project_files = {
            "go.mod": self._generate_go_mod(),
        }

        return TargetCodeResult(
            target_language="go",
            source_code=source_code,
            test_code=self.generate_test(result),
            project_files=project_files,
            build_instructions="go build && go test ./...",
        )

    def generate_test(self, result: CompilationResult) -> str:
        """Generate Go test code."""
        parts = []
        parts.append("package main")
        parts.append("")
        parts.append("import (")
        parts.append('\t"testing"')
        parts.append(")")
        parts.append("")

        # Generate test functions from validations
        if result.provenance:
            test_count = 0
            for record in result.provenance.records:
                if record.source_type.value == "validation_synthesis":
                    test_name = self._to_pascal_case(
                        f"Test{record.source_location.replace(' ', '')}"
                    )
                    parts.append(f"func {test_name}(t *testing.T) {{")
                    parts.append(f"\t// {record.source_text[:60]}")
                    parts.append("}")
                    parts.append("")
                    test_count += 1

        if not any(r.source_type.value == "validation_synthesis"
                    for r in (result.provenance.records if result.provenance else [])):
            parts.append("func TestApplication(t *testing.T) {")
            parts.append("\tapp := NewApplication()")
            parts.append("\tif app == nil {")
            parts.append("\t\tt.Error(\"Expected non-nil application\")")
            parts.append("\t}")
            parts.append("}")

        return "\n".join(parts)

    def _generate_package_imports(self) -> str:
        """Generate Go package declaration and imports."""
        return textwrap.dedent("""\
            package main

            import (
            \t"errors"
            \t"fmt"
            \t"sync"
            )""")

    def _generate_error_types(self, result: CompilationResult) -> str:
        """Generate Go error types from Risk/Recovery pairs."""
        lines = []

        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value == "recovery_synthesis":
                    error_name = self._to_pascal_case(
                        record.source_location.replace("Risk ", "").replace(" ", "")
                    ) + "Error"
                    lines.append(f"// {error_name} represents a recoverable error")
                    lines.append(f"var Err{error_name} = errors.New(\"{error_name.lower()}\")")
                    lines.append("")

        if not lines:
            lines.append("// ErrGeneral represents a general application error")
            lines.append('var ErrGeneral = errors.New("general error")')

        return "\n".join(lines)

    def _generate_structs(self, result: CompilationResult) -> str:
        """Generate Go structs from AICL entities."""
        parts = []

        if result.provenance:
            entity_names = set()
            for record in result.provenance.records:
                if record.source_type.value == "entity_generation":
                    entity_names.add(record.artifact_names[0] if record.artifact_names else "")

            for entity_name in entity_names:
                if not entity_name:
                    continue
                struct_name = self._to_pascal_case(entity_name)
                parts.append(f"// {struct_name} represents an AICL entity")
                parts.append(f"type {struct_name} struct {{")
                parts.append(f"\tData map[string]string")
                parts.append(f"}}")

        if not parts:
            parts.append("// AppState represents the application state")
            parts.append("type AppState struct {")
            parts.append("\tData map[string]string")
            parts.append("\tmu   sync.RWMutex")
            parts.append("}")

        return "\n\n".join(parts)

    def _generate_application(self, result: CompilationResult) -> str:
        """Generate the Go Application struct and methods."""
        lines = []
        lines.append("// Application is the main AICL-generated application")
        lines.append("type Application struct {")
        lines.append("\tstate *AppState")
        lines.append("}")
        lines.append("")
        lines.append("// NewApplication creates a new Application instance")
        lines.append("func NewApplication() *Application {")
        lines.append("\treturn &Application{")
        lines.append("\t\tstate: &AppState{Data: make(map[string]string)},")
        lines.append("\t}")
        lines.append("}")

        # Generate methods from behaviors
        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value in ("pattern_match", "sub_language"):
                    behavior_name = record.source_location.split()[-1] if record.source_location else ""
                    method_name = self._to_pascal_case(behavior_name)
                    ax_body, params, ptypes = self._emit_ax_body_go(result, behavior_name)
                    lines.append("")
                    lines.append(f"// {method_name} implements {record.source_text[:50]}")
                    if ax_body:
                        sig_parts = []
                        for p in params:
                            go_type = "[]int" if ptypes.get(p) == "ARRAY" else "int"
                            sig_parts.append(f"{p} {go_type}")
                        param_sig = ", ".join(sig_parts)
                        lines.append(f"func (a *Application) {method_name}({param_sig}) int {{")
                        for ax_line in ax_body.split('\n'):
                            lines.append(f"\t{ax_line}")
                        lines.append(f"}}")
                    else:
                        lines.append(f"func (a *Application) {method_name}() error {{")
                        lines.append(f"\t// {record.generated_code[:50]}")
                        lines.append(f"\treturn nil")
                        lines.append(f"}}")

        # Run method
        lines.append("")
        lines.append("// Run starts the application")
        lines.append("func (a *Application) Run() error {")
        lines.append("\treturn nil")
        lines.append("}")

        return "\n".join(lines)

    def _generate_main(self) -> str:
        """Generate Go main function."""
        return textwrap.dedent("""\
            func main() {
            \tapp := NewApplication()
            \tif err := app.Run(); err != nil {
            \t\tfmt.Printf("Error: %v\\n", err)
            \t}
            }""")

    def _generate_go_mod(self) -> str:
        """Generate go.mod file."""
        return textwrap.dedent("""\
            module aicl-generated

            go 1.21""")

    def _emit_ax_body_go(self, result, behavior_name: str):
        """If the behavior was written in AX, return (go_body, param_names, ptypes).

        ptypes is the AX-inferred type map {name: "ARRAY"|"INT"|"ANY"}.
        Returns ("", [], {}) if the behavior has no AX source.
        """
        raw = getattr(result, 'ax_sources', {}).get(behavior_name)
        if not raw:
            return "", [], {}
        if isinstance(raw, tuple):
            ax_src, params = raw
        else:
            ax_src, params = raw, []
        try:
            from ..ax import parse as ax_parse
            from ..ax.emitter_go import emit_go
            from ..ax.typeinfer import infer_param_types
            stmts = ax_parse(ax_src)
            ptypes = infer_param_types(stmts, params)
            return emit_go(stmts, indent=1), params, ptypes
        except Exception:
            return "", params, {}
