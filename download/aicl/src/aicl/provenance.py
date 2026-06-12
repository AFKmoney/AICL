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
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import re


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
