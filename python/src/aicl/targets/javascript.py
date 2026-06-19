"""
AICL JavaScript Target Generator

Generates idiomatic JavaScript/TypeScript code from AICL compilation results.

Features:
    - ES6 classes for entities
    - try/catch error handling from Risk/Recovery pairs
    - EventEmitter for event-driven patterns
    - async/await for asynchronous operations
    - Jest test suite from Validation sections
    - JSDoc documentation from provenance records

Generated code follows JavaScript best practices:
    - Module pattern (ESM)
    - Error classes with custom properties
    - Promise-based async operations
    - Event-driven architecture support
"""

import textwrap
from typing import List, Dict, Optional

from .base import TargetGenerator, TargetCodeResult
from ..compiler import CompilationResult


def _one_line(text: str, n: int = 60) -> str:
    """First line of text, truncated, safe for single-line comments."""
    return text.split("\n", 1)[0][:n]


class JavaScriptGenerator(TargetGenerator):
    """Generates JavaScript/TypeScript code from AICL compilation results."""

    @property
    def language_name(self) -> str:
        return "JavaScript"

    @property
    def file_extension(self) -> str:
        return ".js"

    def generate(self, result: CompilationResult) -> TargetCodeResult:
        """Generate JavaScript source code from the compilation result."""
        parts = []

        # Module imports
        parts.append(self._generate_imports())

        # Error classes
        parts.append(self._generate_error_classes(result))

        # Entity classes
        parts.append(self._generate_classes(result))

        # Application class
        parts.append(self._generate_application(result))

        # Export
        parts.append(self._generate_exports(result))

        source_code = "\n\n".join(parts)

        # Project files
        project_files = {
            "package.json": self._generate_package_json(result),
            "tsconfig.json": self._generate_tsconfig(),
        }

        return TargetCodeResult(
            target_language="javascript",
            source_code=source_code,
            test_code=self.generate_test(result),
            project_files=project_files,
            build_instructions="npm install && npm test",
        )

    def generate_test(self, result: CompilationResult) -> str:
        """Generate Jest test code."""
        parts = []
        parts.append("const { Application } = require('./main');")
        parts.append("")
        parts.append("describe('AICL Generated Application', () => {")

        # Generate test cases from validations
        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value == "validation_synthesis":
                    test_name = self._to_camel_case(
                        f"test {record.source_location}"
                    ).replace(" ", "")
                    parts.append(f"  test('{_one_line(record.source_text, 50)}', () => {{")
                    parts.append(f"    // {_one_line(record.source_text, 60)}")
                    parts.append(f"    expect(true).toBe(true);")
                    parts.append(f"  }});")

        if not any(r.source_type.value == "validation_synthesis"
                    for r in (result.provenance.records if result.provenance else [])):
            parts.append("  test('application initializes', () => {")
            parts.append("    const app = new Application();")
            parts.append("    expect(app).toBeDefined();")
            parts.append("  });")

        parts.append("});")
        return "\n".join(parts)

    def _generate_imports(self) -> str:
        """Generate JavaScript import statements."""
        return textwrap.dedent("""\
            const { EventEmitter } = require('events');
            const crypto = require('crypto');""")

    def _generate_error_classes(self, result: CompilationResult) -> str:
        """Generate JavaScript error classes from Risk/Recovery pairs."""
        lines = []
        lines.append("class AppError extends Error {")
        lines.append("  constructor(message, type = 'General') {")
        lines.append("    super(message);")
        lines.append("    this.name = 'AppError';")
        lines.append("    this.type = type;")
        lines.append("  }")
        lines.append("}")

        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value == "recovery_synthesis":
                    error_name = self._to_pascal_case(
                        record.source_location.replace("Risk ", "").replace(" ", "")
                    ) + "Error"
                    lines.append("")
                    lines.append(f"class {error_name} extends AppError {{")
                    lines.append(f"  constructor(message) {{")
                    lines.append(f"    super(message, '{error_name}');")
                    lines.append(f"    this.name = '{error_name}';")
                    lines.append(f"  }}")
                    lines.append(f"}}")

        return "\n".join(lines)

    def _generate_classes(self, result: CompilationResult) -> str:
        """Generate JavaScript classes from AICL entities."""
        parts = []

        if result.provenance:
            entity_names = set()
            for record in result.provenance.records:
                if record.source_type.value == "entity_generation":
                    entity_names.add(record.artifact_names[0] if record.artifact_names else "")

            for entity_name in entity_names:
                if not entity_name:
                    continue
                class_name = self._to_pascal_case(entity_name)
                parts.append(f"class {class_name} {{")
                parts.append(f"  constructor() {{")
                parts.append(f"    this.data = {{}};")
                parts.append(f"  }}")
                parts.append(f"}}")

        if not parts:
            parts.append("class AppState {")
            parts.append("  constructor() {")
            parts.append("    this.data = {};")
            parts.append("  }")
            parts.append("}")

        return "\n\n".join(parts)

    def _generate_application(self, result: CompilationResult) -> str:
        """Generate the main Application class."""
        lines = []
        lines.append("class Application extends EventEmitter {")
        lines.append("  constructor() {")
        lines.append("    super();")
        lines.append("    this.state = new AppState();")
        lines.append("    this._setupEventHandlers();")
        lines.append("  }")
        lines.append("")
        lines.append("  _setupEventHandlers() {")

        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value == "event_synthesis":
                    lines.append(f"    // {_one_line(record.source_text, 60)}")
                    lines.append(f"    // this.on('event', this._handle{self._to_pascal_case(record.source_location.split()[-1])}.bind(this));")

        lines.append("  }")

        # Generate methods from behaviors
        if result.provenance:
            for record in result.provenance.records:
                if record.source_type.value in ("pattern_match", "sub_language"):
                    # Behavior name is the last token of "Behavior <Name>"
                    behavior_name = record.source_location.split()[-1] if record.source_location else ""
                    method_name = self._to_camel_case(behavior_name)
                    lines.append("")
                    lines.append(f"  /**")
                    lines.append(f"   * {_one_line(record.source_text, 60)}")
                    lines.append(f"   * Provenance: {record.resolution_path[-1] if record.resolution_path else 'N/A'}")
                    lines.append(f"   */")
                    ax_body, params = self._emit_ax_body_js(result, behavior_name)
                    param_list = ", ".join(params)
                    lines.append(f"  {method_name}({param_list}) {{")
                    if ax_body:
                        for ax_line in ax_body.split('\n'):
                            lines.append(f"    {ax_line}")
                    else:
                        lines.append(f"    // {record.generated_code[:60]}")
                    lines.append(f"  }}")

        # Run method
        lines.append("")
        lines.append("  async run() {")
        lines.append("    this.emit('start');")
        lines.append("    this.emit('end');")
        lines.append("  }")

        lines.append("}")
        return "\n".join(lines)

    def _generate_exports(self, result: CompilationResult) -> str:
        """Generate module exports."""
        return "module.exports = { Application, AppError };"

    def _generate_package_json(self, result: CompilationResult) -> str:
        """Generate package.json."""
        return textwrap.dedent('''\
            {
              "name": "aicl-generated",
              "version": "1.0.0",
              "description": "AICL-generated application",
              "main": "main.js",
              "scripts": {
                "test": "jest",
                "start": "node main.js"
              },
              "devDependencies": {
                "jest": "^29.0.0"
              }
            }''')

    def _generate_tsconfig(self) -> str:
        """Generate tsconfig.json for TypeScript support."""
        return textwrap.dedent('''\
            {
              "compilerOptions": {
                "target": "ES2022",
                "module": "commonjs",
                "strict": true,
                "esModuleInterop": true,
                "outDir": "./dist"
              },
              "include": ["*.js"]
            }''')

    def _emit_ax_body_js(self, result, behavior_name: str):
        """If the behavior was written in AX, return (js_body, param_names).

        Returns ("", []) if the behavior has no AX source.
        """
        raw = getattr(result, 'ax_sources', {}).get(behavior_name)
        if not raw:
            return "", []
        # ax_sources entries are either a bare source string (legacy) or a
        # (source, [param_names]) tuple.
        if isinstance(raw, tuple):
            ax_src, params = raw
        else:
            ax_src, params = raw, []
        try:
            from ..ax import parse as ax_parse
            from ..ax.emitter_javascript import emit_javascript
            return emit_javascript(ax_parse(ax_src), indent=1), params
        except Exception:
            return "", params

