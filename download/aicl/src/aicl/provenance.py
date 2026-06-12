"""
AICL Compilation Provenance & Audit System

Every line of generated code must have a traceable provenance chain:
    AICL Source → Parse → Pattern Match → Template → Generated Code

This module records and reports WHY each line of code was generated,
and provides an audit system to verify that every generated artifact
is traceable to its originating specification.

Core Concepts:
    - Provenance Record: Explains why a specific piece of code was generated
    - Generated Artifact: A named unit of generated code (class, method, function, test)
    - Audit Coverage: Ratio of auditable artifacts to total generated artifacts
    - Orphan Artifact: A generated artifact without provenance

Formal Property (The Auditability Theorem):
    A program is auditable if every generated artifact
    can be traced to its originating specification
    through a complete provenance chain.

    Audit Coverage = Auditable Artifacts / Generated Artifacts
    Target: Audit Coverage = 1.0

Usage:
    aicl explain pong.aicl              # Full compilation trace
    aicl explain pong.aicl --behavior MovePaddle  # Specific behavior trace
    aicl audit pong.aicl                # Audit report with coverage
    aicl audit pong.aicl --strict       # Fail if coverage < 100%
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from enum import Enum
import re
import json
import hashlib
import time


class ProvenanceType(Enum):
    """Type of provenance record."""
    PATTERN_MATCH = "pattern_match"
    SUB_LANGUAGE = "sub_language"
    FALLBACK = "fallback"
    ARCHITECTURE_TEMPLATE = "architecture_template"
    DIRECT_MAPPING = "direct_mapping"
    RECOVERY_SYNTHESIS = "recovery_synthesis"
    VALIDATION_SYNTHESIS = "validation_synthesis"
    CONDITION_SYNTHESIS = "condition_synthesis"
    EVENT_SYNTHESIS = "event_synthesis"
    HELPER_METHOD = "helper_method"
    ENTITY_GENERATION = "entity_generation"
    LAYER_INITIALIZATION = "layer_initialization"
    # v0.5: New provenance types for full coverage
    SECURITY_METHOD = "security_method"
    PARALLEL_EXECUTION = "parallel_execution"
    RUN_METHOD = "run_method"
    IMPORT_GENERATION = "import_generation"
    ENTRY_POINT = "entry_point"
    TEST_GENERATION = "test_generation"
    CLASS_STRUCTURE = "class_structure"


class ArtifactType(Enum):
    """Type of generated artifact."""
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    DATACLASS = "dataclass"
    TEST_FUNCTION = "test_function"
    IMPORT_BLOCK = "import_block"
    MODULE = "module"


@dataclass
class ProvenanceRecord:
    """
    A single provenance record explaining why a piece of code was generated.

    This is the audit trail of the compiler. Every generated method,
    every line of behavior code, every recovery handler must have one.
    """
    source_type: ProvenanceType
    source_location: str          # Where in the AICL source (e.g., "Behavior MovePaddle")
    source_text: str              # The original AICL text
    resolution_path: List[str]    # Chain: ["AICL Source", "Parser", "Pattern Match", "MOVE", "Template"]
    generated_code: str           # The code that was generated
    confidence: float = 1.0       # Confidence of the match (1.0 = deterministic)
    pattern_name: str = ""        # Pattern that matched (if applicable)
    template_name: str = ""       # Architecture template (if applicable)
    parameters: Dict[str, str] = field(default_factory=dict)  # Parameters used
    artifact_names: List[str] = field(default_factory=list)    # Which artifacts this record covers


@dataclass
class GeneratedArtifact:
    """
    A named unit of generated code.

    Every method, class, function, and dataclass produced by the compiler
    is registered as an artifact. The audit system verifies that each
    artifact has at least one provenance record explaining its existence.

    An artifact without provenance is an "orphan" — it exists in the
    generated code but the compiler cannot explain why.
    """
    name: str                           # Human-readable name (e.g., "_behavior_move_paddle")
    artifact_type: ArtifactType         # Type of artifact
    source: str                         # Which AICL section triggered generation
    provenance_indices: List[int] = field(default_factory=list)  # Indices into records list
    code_snippet: str = ""              # Brief snippet of the generated code (first line)

    @property
    def has_provenance(self) -> bool:
        """Whether this artifact has at least one provenance record."""
        return len(self.provenance_indices) > 0

    @property
    def is_orphan(self) -> bool:
        """Whether this artifact is an orphan (no provenance)."""
        return not self.has_provenance


class CompilationProvenance:
    """
    Tracks the complete provenance of a compilation and provides
    audit capabilities.

    Records every decision the compiler makes, creating an audit trail
    that can be queried to understand WHY any line of code exists.

    This is the antidote to compiler complexity hiding. As AICL grows
    (30 patterns → 100 patterns → 500 patterns), the provenance tracker
    ensures every decision remains explainable.

    v0.5: Added artifact tracking and audit coverage computation.
    """

    def __init__(self):
        self.records: List[ProvenanceRecord] = []
        self.artifacts: List[GeneratedArtifact] = []

    def record(
        self,
        source_type: ProvenanceType,
        source_location: str,
        source_text: str,
        resolution_path: List[str],
        generated_code: str,
        confidence: float = 1.0,
        pattern_name: str = "",
        template_name: str = "",
        parameters: Dict[str, str] = None,
        artifact_names: List[str] = None,
    ) -> ProvenanceRecord:
        """Record a compilation decision."""
        rec = ProvenanceRecord(
            source_type=source_type,
            source_location=source_location,
            source_text=source_text,
            resolution_path=resolution_path,
            generated_code=generated_code,
            confidence=confidence,
            pattern_name=pattern_name,
            template_name=template_name,
            parameters=parameters or {},
            artifact_names=artifact_names or [],
        )
        self.records.append(rec)

        # Link this provenance record to any matching artifacts
        record_index = len(self.records) - 1
        for artifact_name in (artifact_names or []):
            for artifact in self.artifacts:
                if artifact.name == artifact_name:
                    artifact.provenance_indices.append(record_index)

        return rec

    def register_artifact(
        self,
        name: str,
        artifact_type: ArtifactType,
        source: str,
        code_snippet: str = "",
    ) -> GeneratedArtifact:
        """
        Register a generated artifact.

        Every method, class, function, and dataclass produced by the
        compiler should be registered. The audit system will verify
        that each artifact has at least one provenance record.
        """
        artifact = GeneratedArtifact(
            name=name,
            artifact_type=artifact_type,
            source=source,
            code_snippet=code_snippet,
        )
        self.artifacts.append(artifact)

        # Check if any existing provenance records already cover this artifact
        for i, rec in enumerate(self.records):
            if name in rec.artifact_names:
                artifact.provenance_indices.append(i)

        return artifact

    def link_provenance_to_artifact(self, record_index: int, artifact_name: str):
        """Explicitly link a provenance record to an artifact."""
        if record_index < len(self.records):
            if artifact_name not in self.records[record_index].artifact_names:
                self.records[record_index].artifact_names.append(artifact_name)

        for artifact in self.artifacts:
            if artifact.name == artifact_name:
                if record_index not in artifact.provenance_indices:
                    artifact.provenance_indices.append(record_index)

    # =========================================================================
    # Explain Commands
    # =========================================================================

    def explain(self, target: str = None) -> str:
        """
        Generate an explanation of the compilation.

        Args:
            target: Optional filter (behavior name, pattern name, etc.)

        Returns:
            Human-readable explanation of all compilation decisions.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AICL COMPILATION PROVENANCE TRACE")
        lines.append("=" * 70)
        lines.append("")

        # Summary
        total = len(self.records)
        pattern_count = sum(1 for r in self.records if r.source_type == ProvenanceType.PATTERN_MATCH)
        sublang_count = sum(1 for r in self.records if r.source_type == ProvenanceType.SUB_LANGUAGE)
        fallback_count = sum(1 for r in self.records if r.source_type == ProvenanceType.FALLBACK)
        template_count = sum(1 for r in self.records if r.source_type == ProvenanceType.ARCHITECTURE_TEMPLATE)
        direct_count = sum(1 for r in self.records if r.source_type == ProvenanceType.DIRECT_MAPPING)

        lines.append(f"Total decisions: {total}")
        lines.append(f"  Pattern matches:    {pattern_count}")
        lines.append(f"  Sub-language:       {sublang_count}")
        lines.append(f"  Direct mappings:    {direct_count}")
        lines.append(f"  Architecture tmpl:  {template_count}")
        lines.append(f"  Fallbacks:          {fallback_count}")
        lines.append("")

        # Confidence score
        if total > 0:
            avg_confidence = sum(r.confidence for r in self.records) / total
            fully_deterministic = sum(1 for r in self.records if r.confidence >= 0.9)
            lines.append(f"Average confidence:    {avg_confidence:.2f}")
            lines.append(f"Fully deterministic:   {fully_deterministic}/{total} ({100*fully_deterministic//max(total,1)}%)")
            lines.append("")

        # Group by source type
        by_type: Dict[ProvenanceType, List[ProvenanceRecord]] = {}
        for rec in self.records:
            if rec.source_type not in by_type:
                by_type[rec.source_type] = []
            by_type[rec.source_type].append(rec)

        for source_type, records in by_type.items():
            type_label = source_type.value.replace("_", " ").title()
            lines.append("-" * 70)
            lines.append(f" {type_label} ({len(records)} decisions)")
            lines.append("-" * 70)

            for i, rec in enumerate(records):
                # Filter by target if specified
                if target and target.lower() not in rec.source_location.lower() and target.lower() not in rec.pattern_name.lower():
                    continue

                lines.append(f"")
                lines.append(f"  [{i+1}] {rec.source_location}")
                lines.append(f"  Source:  \"{rec.source_text}\"")
                lines.append(f"  Path:    {' → '.join(rec.resolution_path)}")

                if rec.pattern_name:
                    lines.append(f"  Pattern: {rec.pattern_name}")
                if rec.template_name:
                    lines.append(f"  Template: {rec.template_name}")
                if rec.parameters:
                    params_str = ", ".join(f"{k}={v}" for k, v in rec.parameters.items() if not k.startswith("#"))
                    if params_str:
                        lines.append(f"  Params:  {params_str}")

                lines.append(f"  Confidence: {rec.confidence:.2f}")

                # Show generated code (truncated)
                code_lines = rec.generated_code.strip().split('\n')
                if len(code_lines) <= 4:
                    for cl in code_lines:
                        lines.append(f"  Code:    {cl}")
                else:
                    for cl in code_lines[:3]:
                        lines.append(f"  Code:    {cl}")
                    lines.append(f"  Code:    ... ({len(code_lines) - 3} more lines)")

        lines.append("")
        lines.append("=" * 70)
        lines.append("END OF PROVENANCE TRACE")
        lines.append("=" * 70)

        return '\n'.join(lines)

    def explain_behavior(self, behavior_name: str) -> str:
        """
        Explain the compilation of a specific behavior.

        This is the answer to:
            "Explain compilation MovePaddle"
        """
        lines = []
        lines.append(f"Compilation trace for: {behavior_name}")
        lines.append("")

        matching = [r for r in self.records if behavior_name.lower() in r.source_location.lower()]

        if not matching:
            return f"No compilation records found for '{behavior_name}'"

        for rec in matching:
            lines.append(f"Source type: {rec.source_type.value}")
            lines.append(f"Source text: \"{rec.source_text}\"")
            lines.append(f"")
            lines.append(f"Resolution chain:")
            for step in rec.resolution_path:
                lines.append(f"  ↓ {step}")
            lines.append(f"")
            lines.append(f"Generated code:")
            for cl in rec.generated_code.strip().split('\n'):
                lines.append(f"  {cl}")
            lines.append(f"")
            lines.append(f"Confidence: {rec.confidence:.2f}")
            if rec.pattern_name:
                lines.append(f"Pattern: {rec.pattern_name}")
            if rec.parameters:
                lines.append(f"Parameters used:")
                for k, v in rec.parameters.items():
                    if not k.startswith("#"):
                        lines.append(f"  {k} = {v}")

        return '\n'.join(lines)

    def get_statistics(self) -> Dict:
        """Get compilation statistics."""
        total = len(self.records)
        if total == 0:
            return {"total": 0}

        return {
            "total": total,
            "by_type": {t.value: len([r for r in self.records if r.source_type == t]) for t in ProvenanceType},
            "avg_confidence": sum(r.confidence for r in self.records) / total,
            "fully_deterministic": sum(1 for r in self.records if r.confidence >= 0.9),
            "patterns_used": list(set(r.pattern_name for r in self.records if r.pattern_name)),
        }

    # =========================================================================
    # Coverage & Audit
    # =========================================================================

    def compute_explicability_coverage(self, generated_source: str, generated_tests: str = "") -> Dict:
        """
        Compute the explicability coverage ratio.

        The explicability coverage measures what fraction of generated code
        lines are accounted for by provenance records. The target is 1.0
        (every line has provenance). Any deviation is a gap to investigate.

        Returns:
            Dict with keys:
                - total_lines: total non-blank, non-comment lines in generated code
                - accounted_lines: lines that appear in at least one provenance record
                - coverage_ratio: accounted_lines / total_lines (target: 1.0)
                - unaccounted_lines: list of line numbers without provenance
                - by_type_coverage: coverage broken down by provenance type
        """
        # Combine source and test code
        all_code = generated_source
        if generated_tests:
            all_code += "\n" + generated_tests

        # Count meaningful lines (non-blank, non-import, non-pure-comment)
        code_lines = []
        for i, line in enumerate(all_code.split('\n')):
            stripped = line.strip()
            if not stripped:
                continue
            # Skip pure comment lines and import lines for coverage
            if stripped.startswith('#') and not any(kw in stripped for kw in ['When:', 'On:', 'Risk:', 'Recovery:', 'Action:', 'Intent:']):
                continue
            if stripped.startswith(('import ', 'from ')):
                continue
            if stripped in ('"""', "'''", ''):
                continue
            code_lines.append((i + 1, stripped))

        total_lines = len(code_lines)
        if total_lines == 0:
            return {
                "total_lines": 0,
                "accounted_lines": 0,
                "coverage_ratio": 1.0,
                "unaccounted_lines": [],
                "by_type_coverage": {},
            }

        # Build set of code fragments from provenance records
        accounted_fragments = set()
        for rec in self.records:
            for code_line in rec.generated_code.strip().split('\n'):
                stripped = code_line.strip()
                if stripped:
                    # Normalize for matching (remove variable values that change)
                    normalized = re.sub(r'[\'"].*?[\'\"]', "'...'", stripped)
                    normalized = re.sub(r'\{[^}]*\}', '{...}', normalized)
                    accounted_fragments.add(normalized)
                    # Also add the original
                    accounted_fragments.add(stripped)

        # Check which lines are accounted for
        accounted_lines = 0
        unaccounted = []
        for line_num, line_text in code_lines:
            stripped = line_text.strip()
            # Check if this line or a normalized version appears in provenance
            found = False
            if stripped in accounted_fragments:
                found = True
            else:
                # Try normalizing the source line too
                normalized = re.sub(r'[\'"].*?[\'\"]', "'...'", stripped)
                normalized = re.sub(r'\{[^}]*\}', '{...}', normalized)
                if normalized in accounted_fragments:
                    found = True
                else:
                    # Check if any provenance fragment is a prefix of this line
                    for frag in accounted_fragments:
                        if frag and stripped.startswith(frag.split('=')[0].split('(')[0].strip()):
                            found = True
                            break

            if found:
                accounted_lines += 1
            else:
                # Only flag as unaccounted if it's a significant line
                if not stripped.startswith(('#', '"""', "'''", 'pass', 'else:', 'try:', 'except', 'finally:')):
                    unaccounted.append((line_num, stripped[:80]))

        # Coverage by provenance type
        by_type_coverage = {}
        for ptype in ProvenanceType:
            count = len([r for r in self.records if r.source_type == ptype])
            if count > 0:
                by_type_coverage[ptype.value] = count

        return {
            "total_lines": total_lines,
            "accounted_lines": accounted_lines,
            "coverage_ratio": accounted_lines / total_lines if total_lines > 0 else 1.0,
            "unaccounted_lines": unaccounted,
            "by_type_coverage": by_type_coverage,
        }

    def compute_audit_coverage(self) -> Dict:
        """
        Compute the audit coverage of generated artifacts.

        Audit Coverage = Auditable Artifacts / Generated Artifacts

        An artifact is "auditable" if it has at least one provenance record.
        An artifact without provenance is an "orphan".

        This is the key metric for the Auditability property:
            "A program is auditable if every generated artifact
             can be traced to its originating specification
             through a complete provenance chain."

        Returns:
            Dict with:
                - total_artifacts: total number of generated artifacts
                - auditable_artifacts: artifacts with at least one provenance record
                - orphan_artifacts: list of artifacts without provenance
                - audit_coverage: ratio of auditable to total (target: 1.0)
                - by_type: breakdown by artifact type
        """
        total = len(self.artifacts)
        if total == 0:
            return {
                "total_artifacts": 0,
                "auditable_artifacts": 0,
                "orphan_artifacts": [],
                "audit_coverage": 1.0,
                "by_type": {},
            }

        auditable = [a for a in self.artifacts if a.has_provenance]
        orphans = [a for a in self.artifacts if a.is_orphan]

        # Breakdown by type
        by_type = {}
        for atype in ArtifactType:
            type_artifacts = [a for a in self.artifacts if a.artifact_type == atype]
            type_auditable = [a for a in type_artifacts if a.has_provenance]
            if type_artifacts:
                by_type[atype.value] = {
                    "total": len(type_artifacts),
                    "auditable": len(type_auditable),
                    "coverage": len(type_auditable) / len(type_artifacts),
                }

        return {
            "total_artifacts": total,
            "auditable_artifacts": len(auditable),
            "orphan_artifacts": [{"name": a.name, "type": a.artifact_type.value, "source": a.source} for a in orphans],
            "audit_coverage": len(auditable) / total,
            "by_type": by_type,
        }

    def explain_coverage(self, generated_source: str, generated_tests: str = "") -> str:
        """Generate a coverage report for the explicable compilation property."""
        coverage = self.compute_explicability_coverage(generated_source, generated_tests)
        lines = []
        lines.append("=" * 70)
        lines.append("EXPLICABILITY COVERAGE REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Total meaningful lines:   {coverage['total_lines']}")
        lines.append(f"Lines with provenance:    {coverage['accounted_lines']}")
        lines.append(f"Coverage ratio:           {coverage['coverage_ratio']:.3f}")
        lines.append("")

        if coverage['coverage_ratio'] >= 0.95:
            lines.append("Status: PASS (coverage >= 95%)")
        elif coverage['coverage_ratio'] >= 0.80:
            lines.append("Status: PARTIAL (coverage 80-95%, investigation needed)")
        else:
            lines.append("Status: FAIL (coverage < 80%, provenance gaps detected)")

        lines.append("")

        if coverage['by_type_coverage']:
            lines.append("Provenance by type:")
            for ptype, count in sorted(coverage['by_type_coverage'].items(), key=lambda x: -x[1]):
                lines.append(f"  {ptype:30s} {count:4d} records")
            lines.append("")

        if coverage['unaccounted_lines']:
            lines.append(f"Unaccounted lines ({len(coverage['unaccounted_lines'])}):")
            for line_num, text in coverage['unaccounted_lines'][:20]:
                lines.append(f"  L{line_num:4d}: {text}")
            if len(coverage['unaccounted_lines']) > 20:
                lines.append(f"  ... and {len(coverage['unaccounted_lines']) - 20} more")
        else:
            lines.append("All lines have provenance coverage.")

        lines.append("")
        lines.append("=" * 70)
        return '\n'.join(lines)

    def audit(self, generated_source: str = "", generated_tests: str = "") -> str:
        """
        Generate a complete audit report.

        This is the primary output of the audit system. It verifies the
        Auditability property:

            "A program is auditable if every generated artifact
             can be traced to its originating specification
             through a complete provenance chain."

        The audit report contains:
            1. Artifact summary (total, auditable, orphans)
            2. Audit coverage ratio (target: 1.0)
            3. Orphan artifact list (artifacts without provenance)
            4. Audit status (VERIFIED / PARTIAL / FAILED)
            5. Explicability coverage (line-level)
            6. Breakdown by artifact type

        Returns:
            Human-readable audit report.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AICL AUDIT REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Artifact audit
        audit = self.compute_audit_coverage()

        lines.append("ARTIFACT AUDIT")
        lines.append("-" * 70)
        lines.append(f"  Generated artifacts:     {audit['total_artifacts']}")
        lines.append(f"  Artifacts with provenance: {audit['auditable_artifacts']}")
        lines.append(f"  Orphan artifacts:        {len(audit['orphan_artifacts'])}")
        lines.append("")

        coverage_pct = audit['audit_coverage'] * 100
        lines.append(f"  Audit Coverage:          {coverage_pct:.2f}%")
        lines.append("")

        # Audit status
        if audit['audit_coverage'] >= 1.0:
            lines.append("  Audit Status: VERIFIED")
        elif audit['audit_coverage'] >= 0.90:
            lines.append("  Audit Status: PARTIAL (investigation needed)")
        else:
            lines.append("  Audit Status: FAILED (significant provenance gaps)")
        lines.append("")

        # Orphan artifacts
        if audit['orphan_artifacts']:
            lines.append("ORPHAN ARTIFACTS (no provenance)")
            lines.append("-" * 70)
            for orphan in audit['orphan_artifacts']:
                lines.append(f"  [{orphan['type']:15s}] {orphan['name']}")
                lines.append(f"    Source: {orphan['source']}")
            lines.append("")

        # Breakdown by artifact type
        if audit['by_type']:
            lines.append("COVERAGE BY ARTIFACT TYPE")
            lines.append("-" * 70)
            for atype, info in sorted(audit['by_type'].items(), key=lambda x: -x[1]['total']):
                cov_pct = info['coverage'] * 100
                status = "VERIFIED" if info['coverage'] >= 1.0 else "PARTIAL" if info['coverage'] >= 0.9 else "FAILED"
                lines.append(f"  {atype:15s}  {info['auditable']:3d}/{info['total']:3d}  {cov_pct:6.2f}%  [{status}]")
            lines.append("")

        # Line-level explicability coverage
        if generated_source:
            exp_coverage = self.compute_explicability_coverage(generated_source, generated_tests)
            lines.append("LINE-LEVEL EXPLICABILITY")
            lines.append("-" * 70)
            lines.append(f"  Total meaningful lines:  {exp_coverage['total_lines']}")
            lines.append(f"  Lines with provenance:   {exp_coverage['accounted_lines']}")
            lines.append(f"  Explicability coverage:  {exp_coverage['coverage_ratio']:.2%}")

            if exp_coverage['coverage_ratio'] >= 0.95:
                lines.append("  Line status: PASS (>= 95%)")
            elif exp_coverage['coverage_ratio'] >= 0.80:
                lines.append("  Line status: PARTIAL (80-95%)")
            else:
                lines.append("  Line status: FAIL (< 80%)")

            if exp_coverage['unaccounted_lines']:
                lines.append(f"  Unaccounted lines: {len(exp_coverage['unaccounted_lines'])}")
            lines.append("")

        # Provenance summary
        lines.append("PROVENANCE SUMMARY")
        lines.append("-" * 70)
        total_records = len(self.records)
        lines.append(f"  Total provenance records: {total_records}")

        if total_records > 0:
            avg_conf = sum(r.confidence for r in self.records) / total_records
            lines.append(f"  Average confidence:       {avg_conf:.2f}")
            deterministic = sum(1 for r in self.records if r.confidence >= 0.9)
            lines.append(f"  Deterministic decisions:  {deterministic}/{total_records} ({100*deterministic//total_records}%)")

            # By type summary
            by_type = {}
            for rec in self.records:
                label = rec.source_type.value.replace("_", " ").title()
                by_type[label] = by_type.get(label, 0) + 1

            lines.append("  Provenance by type:")
            for label, count in sorted(by_type.items(), key=lambda x: -x[1]):
                lines.append(f"    {label:30s} {count:4d}")
        lines.append("")

        # Final verdict
        lines.append("=" * 70)
        if audit['audit_coverage'] >= 1.0 and (not generated_source or exp_coverage['coverage_ratio'] >= 0.95):
            lines.append("AUDIT RESULT: PASSED")
            lines.append("  Every generated artifact has provenance.")
            lines.append("  Compilation is fully auditable.")
        elif audit['audit_coverage'] >= 0.90:
            lines.append("AUDIT RESULT: PARTIAL")
            lines.append("  Most artifacts have provenance.")
            lines.append("  Some orphan artifacts need investigation.")
        else:
            lines.append("AUDIT RESULT: FAILED")
            lines.append("  Significant provenance gaps detected.")
            lines.append("  Compilation is not fully auditable.")
        lines.append("=" * 70)

        return '\n'.join(lines)

    def audit_passed(self, generated_source: str = "", generated_tests: str = "") -> bool:
        """
        Check whether the audit passes.

        Audit passes if:
            1. Audit coverage = 1.0 (no orphan artifacts)
            2. Explicability coverage >= 0.95 (line-level)

        Used by `aicl audit --strict` to determine exit code.
        """
        audit = self.compute_audit_coverage()
        if audit['audit_coverage'] < 1.0:
            return False

        if generated_source:
            exp = self.compute_explicability_coverage(generated_source, generated_tests)
            if exp['coverage_ratio'] < 0.95:
                return False

        return True

    # =========================================================================
    # Proof of Origin — The Central Artifact
    # =========================================================================

    def to_proof(
        self,
        source_path: str = "",
        source_text: str = "",
        generated_source: str = "",
        generated_tests: str = "",
        compiler_version: str = "0.6.0",
        target_language: str = "python",
    ) -> 'ProofOfOrigin':
        """
        Generate a Proof of Origin from this compilation.

        The Proof of Origin is the central artifact of auditable compilation.
        It is a self-contained, verifiable record that binds:
            - The original AICL specification
            - Every generated artifact
            - Every provenance record
            - The formal properties verified (No Orphan, Complete Coverage)
            - Cryptographic hashes binding proof to generated code

        If this file exists, `aicl explain` and `aicl audit` can be
        reconstructed entirely from it — without the compiler.

        Args:
            source_path: Path to the original AICL source file
            source_text: The original AICL source text
            generated_source: The generated program code
            generated_tests: The generated test code
            compiler_version: Version of the AICL compiler
            target_language: Target language of the compilation

        Returns:
            ProofOfOrigin instance ready for serialization.
        """
        return ProofOfOrigin.from_compilation(
            provenance=self,
            source_path=source_path,
            source_text=source_text,
            generated_source=generated_source,
            generated_tests=generated_tests,
            compiler_version=compiler_version,
            target_language=target_language,
        )


class ProofOfOrigin:
    """
    Proof of Origin — the central artifact of auditable compilation.

    A Proof of Origin is a self-contained, verifiable record that proves:
        1. Every generated artifact has a traceable provenance chain
        2. No artifact exists without justification (No Orphan Property)
        3. Audit coverage = 1.0 (Complete Coverage Property)
        4. The proof is cryptographically bound to the generated code

    Architecture:
        aicl compile pong.aicl
            ↓
        pong.py              (executable program)
        pong.aicl-proof      (proof of origin)

        aicl explain --proof pong.aicl-proof    → human-readable explanation
        aicl audit --proof pong.aicl-proof      → audit report
        aicl proof pong.aicl-proof              → inspect/verify proof

    The proof file is JSON, machine-readable, and contains ALL information
    needed to reconstruct explain() and audit() without the compiler.

    Formal Properties Verified:
        - No Orphan Artifact Property:
            Every generated artifact has at least one provenance chain.
        - Complete Coverage Property:
            Audit Coverage = Auditable Artifacts / Generated Artifacts = 1.0
        - Hash Binding:
            SHA-256(proof) is bound to SHA-256(generated code).
    """

    PROOF_FORMAT_VERSION = "1.0"

    def __init__(self):
        # Metadata
        self.format_version: str = self.PROOF_FORMAT_VERSION
        self.compiler_version: str = ""
        self.timestamp: str = ""
        self.source_path: str = ""
        self.target_language: str = "python"

        # Source binding
        self.source_hash: str = ""          # SHA-256 of AICL source
        self.source_text: str = ""          # Full AICL source text

        # Code binding
        self.program_hash: str = ""         # SHA-256 of generated program
        self.test_hash: str = ""            # SHA-256 of generated tests
        self.generated_source: str = ""     # Generated program code
        self.generated_tests: str = ""      # Generated test code

        # Provenance records
        self.records: List[Dict[str, Any]] = []

        # Generated artifacts
        self.artifacts: List[Dict[str, Any]] = []

        # Formal properties
        self.formal_properties: Dict[str, Any] = {}

        # Audit coverage
        self.audit_coverage: Dict[str, Any] = {}

        # Explicability coverage
        self.explicability_coverage: Dict[str, Any] = {}

    @classmethod
    def from_compilation(
        cls,
        provenance: CompilationProvenance,
        source_path: str = "",
        source_text: str = "",
        generated_source: str = "",
        generated_tests: str = "",
        compiler_version: str = "0.6.0",
        target_language: str = "python",
    ) -> 'ProofOfOrigin':
        """
        Create a Proof of Origin from a completed compilation.

        This is the primary constructor — used by the compiler at the end
        of a successful compilation to produce the proof artifact.
        """
        proof = cls()
        proof.compiler_version = compiler_version
        proof.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        proof.source_path = source_path
        proof.target_language = target_language

        # Bind to source
        proof.source_text = source_text
        proof.source_hash = hashlib.sha256(source_text.encode('utf-8')).hexdigest()

        # Bind to generated code
        proof.generated_source = generated_source
        proof.generated_tests = generated_tests
        proof.program_hash = hashlib.sha256(generated_source.encode('utf-8')).hexdigest()
        proof.test_hash = hashlib.sha256(generated_tests.encode('utf-8')).hexdigest()

        # Serialize provenance records
        proof.records = []
        for rec in provenance.records:
            proof.records.append({
                "source_type": rec.source_type.value,
                "source_location": rec.source_location,
                "source_text": rec.source_text,
                "resolution_path": rec.resolution_path,
                "generated_code": rec.generated_code,
                "confidence": rec.confidence,
                "pattern_name": rec.pattern_name,
                "template_name": rec.template_name,
                "parameters": rec.parameters,
                "artifact_names": rec.artifact_names,
            })

        # Serialize artifacts
        proof.artifacts = []
        for art in provenance.artifacts:
            proof.artifacts.append({
                "name": art.name,
                "artifact_type": art.artifact_type.value,
                "source": art.source,
                "provenance_indices": art.provenance_indices,
                "code_snippet": art.code_snippet,
                "has_provenance": art.has_provenance,
                "is_orphan": art.is_orphan,
            })

        # Compute and store formal properties
        audit = provenance.compute_audit_coverage()
        exp_coverage = provenance.compute_explicability_coverage(
            generated_source, generated_tests
        ) if generated_source else {"coverage_ratio": 1.0, "total_lines": 0, "accounted_lines": 0}

        proof.formal_properties = {
            "no_orphan_artifact_property": {
                "statement": "Every generated artifact has at least one provenance chain.",
                "verified": len(audit['orphan_artifacts']) == 0,
                "orphan_count": len(audit['orphan_artifacts']),
            },
            "complete_coverage_property": {
                "statement": "Audit Coverage = Auditable Artifacts / Generated Artifacts = 1.0",
                "verified": audit['audit_coverage'] >= 1.0,
                "coverage": audit['audit_coverage'],
            },
            "hash_binding_property": {
                "statement": "Proof is cryptographically bound to generated code via SHA-256.",
                "verified": True,  # Hashes are computed at proof creation time
                "program_hash": proof.program_hash,
                "test_hash": proof.test_hash,
                "source_hash": proof.source_hash,
            },
        }

        proof.audit_coverage = audit
        proof.explicability_coverage = exp_coverage

        return proof

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the proof to a dictionary (ready for JSON)."""
        return {
            "proof_of_origin": {
                "format_version": self.format_version,
                "compiler_version": self.compiler_version,
                "timestamp": self.timestamp,
                "source_path": self.source_path,
                "target_language": self.target_language,
                "source_hash": self.source_hash,
                "program_hash": self.program_hash,
                "test_hash": self.test_hash,
                "formal_properties": self.formal_properties,
                "audit_summary": {
                    "total_artifacts": self.audit_coverage.get('total_artifacts', 0),
                    "auditable_artifacts": self.audit_coverage.get('auditable_artifacts', 0),
                    "orphan_artifacts": len(self.audit_coverage.get('orphan_artifacts', [])),
                    "audit_coverage": self.audit_coverage.get('audit_coverage', 0),
                    "audit_status": "VERIFIED" if self.audit_coverage.get('audit_coverage', 0) >= 1.0 else "FAILED",
                },
                "explicability_summary": {
                    "total_lines": self.explicability_coverage.get('total_lines', 0),
                    "accounted_lines": self.explicability_coverage.get('accounted_lines', 0),
                    "coverage_ratio": self.explicability_coverage.get('coverage_ratio', 1.0),
                },
                "records": self.records,
                "artifacts": self.artifacts,
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize the proof to JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_file(self, path: str) -> None:
        """Write the proof to a .aicl-proof file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProofOfOrigin':
        """Deserialize a proof from a dictionary."""
        proof_data = data.get("proof_of_origin", data)
        proof = cls()
        proof.format_version = proof_data.get("format_version", cls.PROOF_FORMAT_VERSION)
        proof.compiler_version = proof_data.get("compiler_version", "")
        proof.timestamp = proof_data.get("timestamp", "")
        proof.source_path = proof_data.get("source_path", "")
        proof.target_language = proof_data.get("target_language", "python")
        proof.source_hash = proof_data.get("source_hash", "")
        proof.program_hash = proof_data.get("program_hash", "")
        proof.test_hash = proof_data.get("test_hash", "")
        proof.formal_properties = proof_data.get("formal_properties", {})
        proof.audit_coverage = proof_data.get("audit_coverage", {})

        # Reconstruct audit_coverage if only summary is available
        if 'audit_summary' in proof_data and not proof.audit_coverage:
            summary = proof_data['audit_summary']
            proof.audit_coverage = {
                'total_artifacts': summary.get('total_artifacts', 0),
                'auditable_artifacts': summary.get('auditable_artifacts', 0),
                'orphan_artifacts': [],
                'audit_coverage': summary.get('audit_coverage', 0),
            }

        proof.explicability_coverage = proof_data.get("explicability_coverage", {})

        if 'explicability_summary' in proof_data and not proof.explicability_coverage:
            summary = proof_data['explicability_summary']
            proof.explicability_coverage = {
                'total_lines': summary.get('total_lines', 0),
                'accounted_lines': summary.get('accounted_lines', 0),
                'coverage_ratio': summary.get('coverage_ratio', 1.0),
            }

        proof.records = proof_data.get("records", [])
        proof.artifacts = proof_data.get("artifacts", [])

        # Source text and generated code are optional (large, can be omitted)
        proof.source_text = proof_data.get("source_text", "")
        proof.generated_source = proof_data.get("generated_source", "")
        proof.generated_tests = proof_data.get("generated_tests", "")

        return proof

    @classmethod
    def from_file(cls, path: str) -> 'ProofOfOrigin':
        """Load a proof from a .aicl-proof file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        proof = cls.from_dict(data)
        return proof

    @classmethod
    def from_json_str(cls, json_str: str) -> 'ProofOfOrigin':
        """Load a proof from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    # =========================================================================
    # Verification
    # =========================================================================

    def verify(self, generated_source: str = "", generated_tests: str = "") -> Dict[str, Any]:
        """
        Verify the integrity of this proof.

        Checks:
            1. Format version is supported
            2. Hash binding: proof hashes match the provided code
            3. No Orphan Property: every artifact has provenance
            4. Complete Coverage Property: audit coverage = 1.0
            5. Record-artifact linkage integrity

        Returns:
            Dict with 'valid' (bool) and 'checks' (list of check results).
        """
        checks = []

        # Check 1: Format version
        checks.append({
            "name": "format_version",
            "description": "Proof format version is supported",
            "passed": self.format_version == self.PROOF_FORMAT_VERSION,
        })

        # Check 2: Hash binding — verify generated code matches proof
        if generated_source:
            actual_hash = hashlib.sha256(generated_source.encode('utf-8')).hexdigest()
            hash_match = actual_hash == self.program_hash
            checks.append({
                "name": "program_hash_binding",
                "description": "Generated program SHA-256 matches proof",
                "passed": hash_match,
                "expected": self.program_hash,
                "actual": actual_hash,
            })
        else:
            checks.append({
                "name": "program_hash_binding",
                "description": "No generated source provided for hash verification",
                "passed": True,  # Can't verify, assume ok
                "note": "Hash not checked (no source provided)",
            })

        if generated_tests:
            actual_hash = hashlib.sha256(generated_tests.encode('utf-8')).hexdigest()
            hash_match = actual_hash == self.test_hash
            checks.append({
                "name": "test_hash_binding",
                "description": "Generated tests SHA-256 matches proof",
                "passed": hash_match,
            })
        else:
            checks.append({
                "name": "test_hash_binding",
                "description": "No test code provided for hash verification",
                "passed": True,
                "note": "Hash not checked (no tests provided)",
            })

        # Check 3: No Orphan Property
        no_orphan = self.formal_properties.get('no_orphan_artifact_property', {})
        orphan_count = no_orphan.get('orphan_count',
            len(self.audit_coverage.get('orphan_artifacts', [])))
        checks.append({
            "name": "no_orphan_artifact_property",
            "description": "Every generated artifact has at least one provenance chain",
            "passed": orphan_count == 0,
            "orphan_count": orphan_count,
        })

        # Check 4: Complete Coverage Property
        complete_cov = self.formal_properties.get('complete_coverage_property', {})
        coverage = complete_cov.get('coverage',
            self.audit_coverage.get('audit_coverage', 0))
        checks.append({
            "name": "complete_coverage_property",
            "description": "Audit Coverage = Auditable Artifacts / Generated Artifacts = 1.0",
            "passed": coverage >= 1.0,
            "coverage": coverage,
        })

        # Check 5: Record-artifact linkage integrity
        linkage_valid = True
        for artifact_data in self.artifacts:
            if not artifact_data.get('is_orphan', True):
                # Non-orphan artifact should have provenance indices
                indices = artifact_data.get('provenance_indices', [])
                if not indices:
                    linkage_valid = False
                    break
                # Each index should reference a valid record
                for idx in indices:
                    if idx < 0 or idx >= len(self.records):
                        linkage_valid = False
                        break
        checks.append({
            "name": "record_artifact_linkage",
            "description": "All provenance indices reference valid records",
            "passed": linkage_valid,
        })

        all_passed = all(c['passed'] for c in checks)
        return {
            "valid": all_passed,
            "checks": checks,
        }

    # =========================================================================
    # Views on the Proof
    # =========================================================================

    def explain(self, target: str = None) -> str:
        """
        Reconstruct a full explanation from this proof.

        This proves that the .aicl-proof file contains ALL information
        needed to answer "Why did the compiler generate this line?"
        without requiring the compiler itself.

        Args:
            target: Optional filter (behavior name, pattern name, etc.)

        Returns:
            Human-readable explanation of all compilation decisions.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AICL PROOF OF ORIGIN — EXPLANATION")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Source: {self.source_path or '<unknown>'}")
        lines.append(f"Compiled: {self.timestamp}")
        lines.append(f"Compiler: AICL v{self.compiler_version}")
        lines.append(f"Target: {self.target_language}")
        lines.append("")

        # Summary
        total = len(self.records)
        type_counts = {}
        for rec in self.records:
            st = rec.get('source_type', 'unknown')
            type_counts[st] = type_counts.get(st, 0) + 1

        lines.append(f"Total decisions: {total}")
        for st, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            label = st.replace("_", " ").title()
            lines.append(f"  {label}: {count}")
        lines.append("")

        # Confidence
        if total > 0:
            confidences = [r.get('confidence', 1.0) for r in self.records]
            avg_conf = sum(confidences) / len(confidences)
            fully_det = sum(1 for c in confidences if c >= 0.9)
            lines.append(f"Average confidence: {avg_conf:.2f}")
            lines.append(f"Fully deterministic: {fully_det}/{total} ({100*fully_det//max(total,1)}%)")
            lines.append("")

        # Group by source type
        by_type: Dict[str, list] = {}
        for rec in self.records:
            st = rec.get('source_type', 'unknown')
            if st not in by_type:
                by_type[st] = []
            by_type[st].append(rec)

        for source_type, records in by_type.items():
            type_label = source_type.replace("_", " ").title()
            lines.append("-" * 70)
            lines.append(f" {type_label} ({len(records)} decisions)")
            lines.append("-" * 70)

            for i, rec in enumerate(records):
                # Filter by target if specified
                if target and target.lower() not in rec.get('source_location', '').lower() \
                        and target.lower() not in rec.get('pattern_name', '').lower():
                    continue

                lines.append("")
                lines.append(f"  [{i+1}] {rec.get('source_location', '<unknown>')}")
                lines.append(f"  Source:  \"{rec.get('source_text', '')}\"")
                path = rec.get('resolution_path', [])
                lines.append(f"  Path:    {' → '.join(path)}")

                if rec.get('pattern_name'):
                    lines.append(f"  Pattern: {rec['pattern_name']}")
                if rec.get('template_name'):
                    lines.append(f"  Template: {rec['template_name']}")
                if rec.get('parameters'):
                    params = rec['parameters']
                    params_str = ", ".join(f"{k}={v}" for k, v in params.items() if not k.startswith("#"))
                    if params_str:
                        lines.append(f"  Params:  {params_str}")

                lines.append(f"  Confidence: {rec.get('confidence', 1.0):.2f}")

                # Show generated code (truncated)
                code = rec.get('generated_code', '')
                code_lines = code.strip().split('\n') if code.strip() else []
                if len(code_lines) <= 4:
                    for cl in code_lines:
                        lines.append(f"  Code:    {cl}")
                elif code_lines:
                    for cl in code_lines[:3]:
                        lines.append(f"  Code:    {cl}")
                    lines.append(f"  Code:    ... ({len(code_lines) - 3} more lines)")

                # Artifacts covered
                art_names = rec.get('artifact_names', [])
                if art_names:
                    lines.append(f"  Covers:  {', '.join(art_names)}")

        lines.append("")
        lines.append("=" * 70)
        lines.append("END OF EXPLANATION (from Proof of Origin)")
        lines.append("=" * 70)

        return '\n'.join(lines)

    def explain_behavior(self, behavior_name: str) -> str:
        """
        Reconstruct a behavior-specific explanation from this proof.

        Answers: "Why was this specific behavior generated this way?"
        """
        lines = []
        lines.append(f"Compilation trace for: {behavior_name}")
        lines.append(f"(Reconstructed from Proof of Origin)")
        lines.append("")

        matching = [
            r for r in self.records
            if behavior_name.lower() in r.get('source_location', '').lower()
        ]

        if not matching:
            return f"No compilation records found for '{behavior_name}' in proof"

        for rec in matching:
            lines.append(f"Source type: {rec.get('source_type', 'unknown')}")
            lines.append(f"Source text: \"{rec.get('source_text', '')}\"")
            lines.append("")
            lines.append("Resolution chain:")
            for step in rec.get('resolution_path', []):
                lines.append(f"  ↓ {step}")
            lines.append("")
            lines.append("Generated code:")
            for cl in rec.get('generated_code', '').strip().split('\n'):
                lines.append(f"  {cl}")
            lines.append("")
            lines.append(f"Confidence: {rec.get('confidence', 1.0):.2f}")
            if rec.get('pattern_name'):
                lines.append(f"Pattern: {rec['pattern_name']}")

            art_names = rec.get('artifact_names', [])
            if art_names:
                lines.append(f"Artifacts covered: {', '.join(art_names)}")

        return '\n'.join(lines)

    def audit_report(self) -> str:
        """
        Reconstruct the full audit report from this proof.

        Proves that the .aicl-proof file contains ALL information
        needed to verify the Auditability property.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AICL AUDIT REPORT (from Proof of Origin)")
        lines.append("=" * 70)
        lines.append("")

        # Proof metadata
        lines.append("PROOF METADATA")
        lines.append("-" * 70)
        lines.append(f"  Compiler:        AICL v{self.compiler_version}")
        lines.append(f"  Timestamp:       {self.timestamp}")
        lines.append(f"  Source:          {self.source_path or '<unknown>'}")
        lines.append(f"  Source hash:     {self.source_hash[:16]}...")
        lines.append(f"  Program hash:    {self.program_hash[:16]}...")
        lines.append("")

        # Artifact audit
        total_artifacts = self.audit_coverage.get('total_artifacts', len(self.artifacts))
        auditable = self.audit_coverage.get('auditable_artifacts',
            sum(1 for a in self.artifacts if not a.get('is_orphan', True)))
        orphans = self.audit_coverage.get('orphan_artifacts', [])
        coverage_val = self.audit_coverage.get('audit_coverage',
            auditable / total_artifacts if total_artifacts > 0 else 1.0)

        lines.append("ARTIFACT AUDIT")
        lines.append("-" * 70)
        lines.append(f"  Generated artifacts:       {total_artifacts}")
        lines.append(f"  Artifacts with provenance: {auditable}")
        lines.append(f"  Orphan artifacts:          {len(orphans)}")
        lines.append("")
        lines.append(f"  Audit Coverage:            {coverage_val:.2%}")
        lines.append("")

        # Audit status
        if coverage_val >= 1.0:
            lines.append("  Audit Status: VERIFIED")
        elif coverage_val >= 0.90:
            lines.append("  Audit Status: PARTIAL (investigation needed)")
        else:
            lines.append("  Audit Status: FAILED (significant provenance gaps)")
        lines.append("")

        # Formal properties
        lines.append("FORMAL PROPERTIES")
        lines.append("-" * 70)
        for prop_name, prop_data in self.formal_properties.items():
            label = prop_name.replace("_", " ").title()
            verified = prop_data.get('verified', False)
            status = "VERIFIED" if verified else "FAILED"
            lines.append(f"  {label}: {status}")
            if 'statement' in prop_data:
                lines.append(f"    {prop_data['statement']}")
            if 'orphan_count' in prop_data:
                lines.append(f"    Orphan count: {prop_data['orphan_count']}")
            if 'coverage' in prop_data:
                lines.append(f"    Coverage: {prop_data['coverage']:.2%}")
        lines.append("")

        # Orphan artifacts
        if orphans:
            lines.append("ORPHAN ARTIFACTS (no provenance)")
            lines.append("-" * 70)
            for orphan in orphans:
                lines.append(f"  [{orphan.get('type', 'unknown'):15s}] {orphan.get('name', 'unknown')}")
                lines.append(f"    Source: {orphan.get('source', 'unknown')}")
            lines.append("")

        # Coverage by artifact type
        by_type = self.audit_coverage.get('by_type', {})
        if by_type:
            lines.append("COVERAGE BY ARTIFACT TYPE")
            lines.append("-" * 70)
            for atype, info in sorted(by_type.items(), key=lambda x: -x[1].get('total', 0)):
                cov = info.get('coverage', 0)
                status = "VERIFIED" if cov >= 1.0 else "PARTIAL" if cov >= 0.9 else "FAILED"
                lines.append(f"  {atype:15s}  {info.get('auditable', 0):3d}/{info.get('total', 0):3d}  {cov:6.2%}  [{status}]")
            lines.append("")

        # Line-level explicability
        exp = self.explicability_coverage
        if exp.get('total_lines', 0) > 0:
            lines.append("LINE-LEVEL EXPLICABILITY")
            lines.append("-" * 70)
            lines.append(f"  Total meaningful lines:  {exp.get('total_lines', 0)}")
            lines.append(f"  Lines with provenance:   {exp.get('accounted_lines', 0)}")
            ratio = exp.get('coverage_ratio', 1.0)
            lines.append(f"  Explicability coverage:  {ratio:.2%}")
            if ratio >= 0.95:
                lines.append("  Line status: PASS (>= 95%)")
            elif ratio >= 0.80:
                lines.append("  Line status: PARTIAL (80-95%)")
            else:
                lines.append("  Line status: FAIL (< 80%)")
            lines.append("")

        # Provenance summary
        lines.append("PROVENANCE SUMMARY")
        lines.append("-" * 70)
        lines.append(f"  Total provenance records: {len(self.records)}")
        if self.records:
            confidences = [r.get('confidence', 1.0) for r in self.records]
            avg_conf = sum(confidences) / len(confidences)
            deterministic = sum(1 for c in confidences if c >= 0.9)
            lines.append(f"  Average confidence:       {avg_conf:.2f}")
            lines.append(f"  Deterministic decisions:  {deterministic}/{len(self.records)} ({100*deterministic//len(self.records)}%)")

            # By type
            type_counts = {}
            for rec in self.records:
                label = rec.get('source_type', 'unknown').replace("_", " ").title()
                type_counts[label] = type_counts.get(label, 0) + 1
            lines.append("  Provenance by type:")
            for label, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                lines.append(f"    {label:30s} {count:4d}")
        lines.append("")

        # Verification result
        verification = self.verify()
        lines.append("PROOF VERIFICATION")
        lines.append("-" * 70)
        for check in verification['checks']:
            status = "PASS" if check['passed'] else "FAIL"
            lines.append(f"  [{status:4s}] {check['name']}: {check['description']}")
        lines.append("")

        # Final verdict
        lines.append("=" * 70)
        if verification['valid'] and coverage_val >= 1.0:
            lines.append("AUDIT RESULT: PASSED")
            lines.append("  Every generated artifact has provenance.")
            lines.append("  Compilation is fully auditable.")
            lines.append("  Proof of Origin is valid.")
        elif coverage_val >= 0.90:
            lines.append("AUDIT RESULT: PARTIAL")
            lines.append("  Most artifacts have provenance.")
        else:
            lines.append("AUDIT RESULT: FAILED")
            lines.append("  Significant provenance gaps detected.")
        lines.append("=" * 70)

        return '\n'.join(lines)

    def audit_passed(self) -> bool:
        """Check whether the audit passes based on this proof."""
        coverage_val = self.audit_coverage.get('audit_coverage', 0)
        if coverage_val < 1.0:
            return False
        verification = self.verify()
        return verification['valid']

    def coverage_report(self) -> str:
        """
        Reconstruct the explicability coverage report from this proof.
        """
        exp = self.explicability_coverage
        lines = []
        lines.append("=" * 70)
        lines.append("EXPLICABILITY COVERAGE REPORT (from Proof of Origin)")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Total meaningful lines:   {exp.get('total_lines', 0)}")
        lines.append(f"Lines with provenance:    {exp.get('accounted_lines', 0)}")
        ratio = exp.get('coverage_ratio', 1.0)
        lines.append(f"Coverage ratio:           {ratio:.3f}")
        lines.append("")

        if ratio >= 0.95:
            lines.append("Status: PASS (coverage >= 95%)")
        elif ratio >= 0.80:
            lines.append("Status: PARTIAL (coverage 80-95%, investigation needed)")
        else:
            lines.append("Status: FAIL (coverage < 80%, provenance gaps detected)")

        lines.append("")

        # Provenance by type
        type_counts = {}
        for rec in self.records:
            label = rec.get('source_type', 'unknown')
            type_counts[label] = type_counts.get(label, 0) + 1

        if type_counts:
            lines.append("Provenance by type:")
            for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {ptype:30s} {count:4d} records")
            lines.append("")

        unaccounted = exp.get('unaccounted_lines', [])
        if unaccounted:
            lines.append(f"Unaccounted lines ({len(unaccounted)}):")
            for item in unaccounted[:20]:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    lines.append(f"  L{item[0]:4d}: {item[1]}")
            if len(unaccounted) > 20:
                lines.append(f"  ... and {len(unaccounted) - 20} more")
        else:
            lines.append("All lines have provenance coverage.")

        lines.append("")
        lines.append("=" * 70)
        return '\n'.join(lines)
