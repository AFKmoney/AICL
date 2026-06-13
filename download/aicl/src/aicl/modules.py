"""
AICL Module System — Multi-File Programs with Cross-File Provenance

Enables AICL programs to import and reference other AICL modules,
creating multi-file programs with cross-file provenance tracking.

Usage in AICL source:
    Import GameEngine from engine.aicl
    Import NetworkLayer from network.aicl

Architecture:
    ModuleResolver — resolves import paths to AICL source files
    ModuleRegistry — tracks compiled modules and their exports
    CrossFileProvenance — links provenance chains across module boundaries
"""

import os
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any

from .parser import Parser, ParseError
from .ast import AICLProgram
from .ir import ArchitectureTree
from .compiler import Compiler, CompilationResult
from .provenance import (
    CompilationProvenance, ProvenanceType, ProvenanceRecord,
    GeneratedArtifact, ArtifactType, ProofOfOrigin,
)


@dataclass
class ModuleExport:
    """An exported symbol from a compiled AICL module."""
    name: str
    symbol_type: str  # "entity", "behavior", "layer", "validation"
    source_module: str  # Module path that defines this symbol
    description: str = ""


@dataclass
class CompiledModule:
    """A compiled AICL module with its exports and provenance."""
    module_path: str
    source_text: str
    program: AICLProgram
    compilation_result: CompilationResult
    exports: List[ModuleExport] = field(default_factory=list)
    source_hash: str = ""

    def __post_init__(self):
        if not self.source_hash:
            self.source_hash = hashlib.sha256(
                self.source_text.encode('utf-8')
            ).hexdigest()


@dataclass
class ImportDeclaration:
    """An import declaration parsed from AICL source."""
    symbols: List[str]  # What to import (empty = import all)
    module_path: str    # Path to the source module


class ModuleRegistry:
    """
    Registry of compiled AICL modules.

    Tracks which modules have been compiled, what they export,
    and maintains cross-file provenance links.
    """

    def __init__(self):
        self._modules: Dict[str, CompiledModule] = {}
        self._import_graph: Dict[str, Set[str]] = {}  # module → set of dependencies

    def register(self, module: CompiledModule) -> None:
        """Register a compiled module."""
        self._modules[module.module_path] = module
        if module.module_path not in self._import_graph:
            self._import_graph[module.module_path] = set()

    def get(self, module_path: str) -> Optional[CompiledModule]:
        """Get a compiled module by path."""
        return self._modules.get(module_path)

    def is_compiled(self, module_path: str) -> bool:
        """Check if a module has been compiled."""
        return module_path in self._modules

    def find_export(self, symbol_name: str) -> Optional[Tuple[str, ModuleExport]]:
        """Find which module exports a given symbol."""
        for path, module in self._modules.items():
            for export in module.exports:
                if export.name == symbol_name:
                    return (path, export)
        return None

    def add_import_dependency(self, importer: str, imported: str) -> None:
        """Record that one module imports from another."""
        if importer not in self._import_graph:
            self._import_graph[importer] = set()
        self._import_graph[importer].add(imported)

    def get_dependency_order(self) -> List[str]:
        """
        Return module paths in dependency order (topological sort).
        Modules with no dependencies come first.
        """
        order = []
        visited = set()
        visiting = set()

        def visit(path: str) -> None:
            if path in visited:
                return
            if path in visiting:
                return  # Cycle detected — skip (should have been caught earlier)
            visiting.add(path)
            for dep in self._import_graph.get(path, set()):
                visit(dep)
            visiting.discard(path)
            visited.add(path)
            order.append(path)

        for path in self._modules:
            visit(path)

        return order

    def get_all_modules(self) -> Dict[str, CompiledModule]:
        """Get all registered modules."""
        return dict(self._modules)


class ModuleResolver:
    """
    Resolves module paths to AICL source files.

    Resolution strategy:
        1. Absolute path: /path/to/module.aicl
        2. Relative path: ./sibling.aicl or ../parent.aicl
        3. Search path: look in configured search directories
    """

    def __init__(self, search_paths: Optional[List[str]] = None):
        self.search_paths = search_paths or ['.']

    def resolve(self, module_path: str, referencing_file: Optional[str] = None) -> Optional[str]:
        """
        Resolve a module path to an absolute file path.

        Args:
            module_path: The module path from the Import statement
            referencing_file: The file that contains the Import (for relative resolution)

        Returns:
            Absolute path to the .aicl file, or None if not found
        """
        # Add .aicl extension if missing
        if not module_path.endswith('.aicl'):
            module_path = module_path + '.aicl'

        # Absolute path
        if os.path.isabs(module_path):
            if os.path.exists(module_path):
                return module_path
            return None

        # Relative to referencing file
        if referencing_file:
            ref_dir = os.path.dirname(os.path.abspath(referencing_file))
            candidate = os.path.join(ref_dir, module_path)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        # Search paths
        for search_path in self.search_paths:
            candidate = os.path.join(search_path, module_path)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        return None


class CrossFileProvenance:
    """
    Links provenance chains across module boundaries.

    When module A imports from module B, the provenance chain for
    A's generated code that uses B's exports should reference B's
    provenance records. This creates a cross-file provenance chain.

    The cross-file provenance is recorded as additional records in
    the importing module's provenance, with a special provenance type
    and reference to the exporting module's proof file.
    """

    def __init__(self, registry: ModuleRegistry):
        self.registry = registry

    def create_import_provenance(
        self,
        import_declaration: ImportDeclaration,
        importer_module: str,
    ) -> List[ProvenanceRecord]:
        """
        Create provenance records for an import declaration.

        These records document that certain code was generated
        because of symbols imported from another module.
        """
        records = []
        source_module = self.registry.get(import_declaration.module_path)

        if not source_module:
            return records

        for symbol_name in import_declaration.symbols:
            export = None
            for exp in source_module.exports:
                if exp.name == symbol_name:
                    export = exp
                    break

            if export:
                record = ProvenanceRecord(
                    source_type=ProvenanceType.IMPORT_GENERATION,
                    source_location=f"Import {symbol_name} from {import_declaration.module_path}",
                    source_text=f"Import {symbol_name} from {import_declaration.module_path}",
                    resolution_path=[
                        "AICL Source",
                        "Import Declaration",
                        f"Module: {import_declaration.module_path}",
                        f"Symbol: {symbol_name}",
                    ],
                    generated_code=f"# Imported from {import_declaration.module_path}: {symbol_name}",
                    confidence=1.0,
                    parameters={
                        "imported_module": import_declaration.module_path,
                        "imported_symbol": symbol_name,
                        "source_module_hash": source_module.source_hash[:16],
                    },
                )
                records.append(record)

        return records

    def generate_cross_file_proof_chain(
        self,
        main_module_path: str,
    ) -> Dict[str, Any]:
        """
        Generate a proof chain that links all modules in the program.

        Returns a dictionary mapping module paths to their proof hashes,
        creating a chain of trust across the module graph.
        """
        chain = {}
        dep_order = self.registry.get_dependency_order()

        for module_path in dep_order:
            module = self.registry.get(module_path)
            if module and module.compilation_result.proof:
                proof = module.compilation_result.proof
                chain[module_path] = {
                    "source_hash": proof.source_hash,
                    "program_hash": proof.program_hash,
                    "test_hash": proof.test_hash,
                    "dependencies": list(self.registry._import_graph.get(module_path, set())),
                }

        return chain


def parse_imports(source: str) -> List[ImportDeclaration]:
    """
    Parse Import declarations from AICL source text.

    Syntax:
        Import SymbolName from module_path
        Import Symbol1, Symbol2 from module_path

    This is a lightweight parser that only handles Import lines,
    without requiring a full parse of the source.
    """
    imports = []
    for line in source.split('\n'):
        line = line.strip()
        if not line.startswith('Import '):
            continue

        # Parse: Import Symbol1, Symbol2 from module_path
        rest = line[len('Import '):].strip()
        if ' from ' not in rest:
            continue

        symbols_part, module_path = rest.split(' from ', 1)
        symbols = [s.strip() for s in symbols_part.split(',')]
        module_path = module_path.strip()

        imports.append(ImportDeclaration(
            symbols=symbols,
            module_path=module_path,
        ))

    return imports


def extract_exports(program: AICLProgram, module_path: str) -> List[ModuleExport]:
    """
    Extract exportable symbols from a compiled AICL program.

    By default, all entities, behaviors, and layers are exportable.
    """
    exports = []

    for entity in program.entities:
        exports.append(ModuleExport(
            name=entity.name,
            symbol_type="entity",
            source_module=module_path,
            description=f"Entity with {len(entity.fields)} field(s)",
        ))

    for behavior in program.behaviors:
        exports.append(ModuleExport(
            name=behavior.name,
            symbol_type="behavior",
            source_module=module_path,
            description=f"Behavior: {behavior.action[:50]}",
        ))

    for layer in program.layers:
        exports.append(ModuleExport(
            name=layer.name,
            symbol_type="layer",
            source_module=module_path,
        ))

    for validation in program.validations:
        exports.append(ModuleExport(
            name=validation.description[:40].replace(' ', '_'),
            symbol_type="validation",
            source_module=module_path,
            description=validation.description,
        ))

    return exports


def compile_multi_file(
    main_source: str,
    main_path: str = "",
    resolver: Optional[ModuleResolver] = None,
    registry: Optional[ModuleRegistry] = None,
) -> Tuple[CompilationResult, ModuleRegistry]:
    """
    Compile a multi-file AICL program.

    Resolves imports, compiles dependencies first, then compiles
    the main module with cross-file provenance links.

    Args:
        main_source: The main AICL source text
        main_path: Path to the main source file (for relative imports)
        resolver: Module resolver (creates default if None)
        registry: Module registry (creates new if None)

    Returns:
        Tuple of (compilation_result, registry_with_all_modules)
    """
    if resolver is None:
        search_paths = ['.']
        if main_path:
            search_paths.append(os.path.dirname(os.path.abspath(main_path)))
        resolver = ModuleResolver(search_paths=search_paths)

    if registry is None:
        registry = ModuleRegistry()

    # Parse imports from main source
    imports = parse_imports(main_source)

    # Compile dependencies first
    for imp in imports:
        resolved_path = resolver.resolve(imp.module_path, referencing_file=main_path)

        if resolved_path is None:
            continue  # Skip unresolvable imports

        if registry.is_compiled(resolved_path):
            registry.add_import_dependency(main_path or "<main>", resolved_path)
            continue

        # Read and compile the dependency
        with open(resolved_path, 'r') as f:
            dep_source = f.read()

        dep_result = compile_multi_file(
            dep_source, resolved_path, resolver, registry
        )

        registry.add_import_dependency(main_path or "<main>", resolved_path)

    # Compile main module
    compiler = Compiler()
    result = compiler.compile(main_source)

    # Parse program for export extraction
    try:
        parser = Parser(main_source)
        program = parser.parse()
    except ParseError:
        program = AICLProgram()

    # Create compiled module
    exports = extract_exports(program, main_path or "<main>")
    compiled = CompiledModule(
        module_path=main_path or "<main>",
        source_text=main_source,
        program=program,
        compilation_result=result,
        exports=exports,
    )
    registry.register(compiled)

    # Add cross-file provenance records for imports
    if result.provenance:
        cross_prov = CrossFileProvenance(registry)
        for imp in imports:
            imp_records = cross_prov.create_import_provenance(imp, main_path or "<main>")
            for record in imp_records:
                result.provenance.record(record)

    return result, registry
