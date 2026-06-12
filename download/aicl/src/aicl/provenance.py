"""
AICL Compilation Provenance Tracker

Every line of generated code must have a traceable provenance chain:
    AICL Source → Parse → Pattern Match → Template → Generated Code

This module records and reports WHY each line of code was generated,
addressing the fundamental risk of compiler complexity hiding.

Design Principle:
    The compiler must always know exactly why it generated a line of code.
    If it can't explain it, it shouldn't generate it.

Usage:
    aicl explain pong.aicl              # Full compilation trace
    aicl explain pong.aicl --behavior MovePaddle  # Specific behavior trace
    aicl explain pong.aicl --provenance           # Show provenance for each line
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
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


class CompilationProvenance:
    """
    Tracks the complete provenance of a compilation.

    Records every decision the compiler makes, creating an audit trail
    that can be queried to understand WHY any line of code exists.

    This is the antidote to compiler complexity hiding. As AICL grows
    (30 patterns → 100 patterns → 500 patterns), the provenance tracker
    ensures every decision remains explainable.
    """

    def __init__(self):
        self.records: List[ProvenanceRecord] = []

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
        )
        self.records.append(rec)
        return rec

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
