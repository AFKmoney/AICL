#!/usr/bin/env python3
"""
AICL Proof of Origin — Independent Verifier

This script verifies a .aicl-proof file WITHOUT any AICL dependency.
It uses only Python standard library modules (json, hashlib, sys).

Purpose:
    An independent third party should be able to verify that:
    1. The proof is self-contained (contains the generated code)
    2. SHA-256 hashes in the proof match the embedded code
    3. No artifact exists without provenance (No Orphan Property)
    4. Audit coverage = 1.0 (Complete Coverage Property)
    5. All provenance indices reference valid records
    6. Artifact orphan status is internally consistent

This eliminates the "Trust me bro" problem:
    Without independent verification, AICL says AICL is correct.
    With independent verification, ANYONE can verify AICL's claims.

Usage:
    python verify_proof.py <proof.aicl-proof>
    python verify_proof.py <proof.aicl-proof> --verbose

Exit codes:
    0 — Proof is VALID (all checks passed)
    1 — Proof is INVALID (one or more checks failed)
    2 — Error (file not found, invalid JSON, etc.)

Design Principles:
    - Zero dependencies beyond Python stdlib
    - No import from aicl or any project module
    - Can be run by anyone, anywhere, without installing AICL
    - Reads the .aicl-proof file as plain JSON
    - Applies deterministic, reproducible verification logic
    - Output is machine-parseable and human-readable

The No-Orphan Property is not a feature of the compiler.
It is a VERIFIABLE PROPERTY of an artifact produced by the compiler.
This distinction is critical.
"""

import json
import hashlib
import sys
import os


SUPPORTED_FORMAT_VERSIONS = ("1.0", "2.0")


def sha256(text: str) -> str:
    """Compute SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_proof(proof_path: str, verbose: bool = False) -> dict:
    """
    Verify a .aicl-proof file.

    Returns a dict with:
        - valid: bool — whether ALL checks passed
        - checks: list of check result dicts
        - summary: human-readable summary string
    """
    # ── Load proof ──────────────────────────────────────────────────────
    if not os.path.exists(proof_path):
        return {
            "valid": False,
            "checks": [],
            "summary": f"ERROR: File not found: {proof_path}",
        }

    try:
        with open(proof_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "checks": [],
            "summary": f"ERROR: Invalid JSON: {e}",
        }

    # Unwrap the proof_of_origin envelope
    proof = data.get("proof_of_origin", data)

    checks = []

    # ── Check 1: Format version ─────────────────────────────────────────
    fmt_ver = proof.get("format_version", "")
    checks.append({
        "name": "format_version",
        "description": "Proof format version is supported",
        "passed": fmt_ver in SUPPORTED_FORMAT_VERSIONS,
        "detail": f"Found: {fmt_ver}, Supported: {SUPPORTED_FORMAT_VERSIONS}",
    })

    # ── Check 2: Source hash binding ────────────────────────────────────
    source_text = proof.get("source_text", "")
    source_hash = proof.get("source_hash", "")
    if source_text and source_hash:
        actual = sha256(source_text)
        checks.append({
            "name": "source_hash_binding",
            "description": "SHA-256(source_text) matches source_hash",
            "passed": actual == source_hash,
            "detail": f"Expected: {source_hash[:16]}... Actual: {actual[:16]}...",
        })
    else:
        checks.append({
            "name": "source_hash_binding",
            "description": "Source text not embedded — cannot verify source hash",
            "passed": True,
            "detail": "Skipped (v1.0 format or source omitted)",
        })

    # ── Check 3: Program hash binding ──────────────────────────────────
    generated_source = proof.get("generated_source", "")
    program_hash = proof.get("program_hash", "")
    if generated_source and program_hash:
        actual = sha256(generated_source)
        checks.append({
            "name": "program_hash_binding",
            "description": "SHA-256(generated_source) matches program_hash",
            "passed": actual == program_hash,
            "detail": f"Expected: {program_hash[:16]}... Actual: {actual[:16]}...",
        })
    else:
        checks.append({
            "name": "program_hash_binding",
            "description": "Generated source not embedded — proof is NOT self-contained",
            "passed": False,
            "detail": "Cannot verify hash binding. Proof is not independently verifiable.",
        })

    # ── Check 4: Test hash binding ─────────────────────────────────────
    generated_tests = proof.get("generated_tests", "")
    test_hash = proof.get("test_hash", "")
    if generated_tests and test_hash:
        actual = sha256(generated_tests)
        checks.append({
            "name": "test_hash_binding",
            "description": "SHA-256(generated_tests) matches test_hash",
            "passed": actual == test_hash,
            "detail": f"Expected: {test_hash[:16]}... Actual: {actual[:16]}...",
        })
    else:
        checks.append({
            "name": "test_hash_binding",
            "description": "Test code not embedded — proof is NOT self-contained",
            "passed": False,
            "detail": "Cannot verify hash binding. Proof is not independently verifiable.",
        })

    # ── Check 5: No Orphan Artifact Property ───────────────────────────
    artifacts = proof.get("artifacts", [])
    records = proof.get("records", [])
    formal_props = proof.get("formal_properties", {})

    no_orphan_prop = formal_props.get("no_orphan_artifact_property", {})
    declared_orphan_count = no_orphan_prop.get("orphan_count", None)

    # Independently count orphans
    actual_orphan_count = sum(
        1 for a in artifacts if a.get("is_orphan", not bool(a.get("provenance_indices", [])))
    )
    # Also check: are there artifacts with no provenance indices that claim non-orphan?
    inconsistent_orphans = sum(
        1 for a in artifacts
        if not a.get("provenance_indices", []) and not a.get("is_orphan", True)
    )

    orphan_check_passed = (
        actual_orphan_count == 0
        and inconsistent_orphans == 0
        and (declared_orphan_count is None or declared_orphan_count == 0)
    )

    checks.append({
        "name": "no_orphan_artifact_property",
        "description": "Every generated artifact has at least one provenance chain",
        "passed": orphan_check_passed,
        "detail": (
            f"Orphans found: {actual_orphan_count}, "
            f"Inconsistent claims: {inconsistent_orphans}, "
            f"Declared: {declared_orphan_count}"
        ),
    })

    # ── Check 6: Complete Coverage Property ────────────────────────────
    audit_summary = proof.get("audit_summary", {})
    declared_coverage = audit_summary.get("audit_coverage", None)
    complete_cov_prop = formal_props.get("complete_coverage_property", {})
    prop_coverage = complete_cov_prop.get("coverage", None)

    # Independently compute coverage
    total_artifacts = len(artifacts)
    auditable_artifacts = sum(
        1 for a in artifacts
        if a.get("provenance_indices", []) and not a.get("is_orphan", True)
    )
    computed_coverage = auditable_artifacts / total_artifacts if total_artifacts > 0 else 1.0

    coverage_passed = computed_coverage >= 1.0
    if declared_coverage is not None:
        coverage_passed = coverage_passed and declared_coverage >= 1.0
    if prop_coverage is not None:
        coverage_passed = coverage_passed and prop_coverage >= 1.0

    checks.append({
        "name": "complete_coverage_property",
        "description": "Audit Coverage = Auditable / Total = 1.0",
        "passed": coverage_passed,
        "detail": (
            f"Computed: {computed_coverage:.2%} ({auditable_artifacts}/{total_artifacts}), "
            f"Declared: {declared_coverage}, "
            f"Formal property: {prop_coverage}"
        ),
    })

    # ── Check 7: Record-artifact linkage integrity ─────────────────────
    linkage_valid = True
    linkage_errors = []
    for i, artifact in enumerate(artifacts):
        if not artifact.get("is_orphan", True):
            indices = artifact.get("provenance_indices", [])
            if not indices:
                linkage_valid = False
                linkage_errors.append(f"Artifact '{artifact.get('name', '?')}' has no indices but claims non-orphan")
            for idx in indices:
                if idx < 0 or idx >= len(records):
                    linkage_valid = False
                    linkage_errors.append(f"Artifact '{artifact.get('name', '?')}' references invalid record index {idx}")

    checks.append({
        "name": "record_artifact_linkage",
        "description": "All provenance indices reference valid records",
        "passed": linkage_valid,
        "detail": f"Linkage errors: {len(linkage_errors)}" + (
            f" — {'; '.join(linkage_errors[:3])}" if linkage_errors else ""
        ),
    })

    # ── Check 8: Artifact consistency ──────────────────────────────────
    consistency_valid = True
    for artifact in artifacts:
        has_indices = bool(artifact.get("provenance_indices", []))
        claims_orphan = artifact.get("is_orphan", not has_indices)
        # has_indices=True + claims_orphan=True → inconsistent
        # has_indices=False + claims_orphan=False → inconsistent
        if has_indices == claims_orphan:
            consistency_valid = False
            break

    checks.append({
        "name": "artifact_consistency",
        "description": "Artifact orphan status is consistent with provenance linkage",
        "passed": consistency_valid,
    })

    # ── Final result ────────────────────────────────────────────────────
    all_passed = all(c["passed"] for c in checks)

    # Build summary
    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count

    if all_passed:
        summary = (
            f"VALID — All {len(checks)} checks passed. "
            f"Proof of Origin is independently verifiable."
        )
    else:
        failed_names = [c["name"] for c in checks if not c["passed"]]
        summary = (
            f"INVALID — {failed_count}/{len(checks)} checks failed: "
            f"{', '.join(failed_names)}"
        )

    return {
        "valid": all_passed,
        "checks": checks,
        "summary": summary,
    }


def main():
    """CLI entry point for the independent verifier."""
    if len(sys.argv) < 2:
        print("Usage: python verify_proof.py <proof.aicl-proof> [--verbose]")
        print()
        print("Independent verifier for AICL Proof of Origin files.")
        print("Uses ONLY Python stdlib. No AICL installation required.")
        print()
        print("Exit codes: 0=VALID, 1=INVALID, 2=ERROR")
        sys.exit(2)

    proof_path = sys.argv[1]
    verbose = "--verbose" in sys.argv

    result = verify_proof(proof_path, verbose=verbose)

    # Print results
    print("=" * 70)
    print("AICL PROOF OF ORIGIN — INDEPENDENT VERIFICATION")
    print("=" * 70)
    print()
    print(f"File: {proof_path}")
    print()

    # Print each check
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status:4s}] {check['name']}")
        print(f"         {check['description']}")
        if verbose and "detail" in check:
            print(f"         {check['detail']}")
        if not check["passed"] and "detail" in check:
            print(f"         >> {check['detail']}")
        print()

    # Final verdict
    print("=" * 70)
    if result["valid"]:
        print("VERDICT: VALID")
        print()
        print("  This Proof of Origin is independently verifiable.")
        print("  No AICL compiler, parser, or project dependency was used.")
        print("  The No-Orphan Property is verified as a property of the artifact,")
        print("  not as a claim of the compiler.")
    else:
        print("VERDICT: INVALID")
        print()
        print("  One or more verification checks failed.")
        print("  This proof cannot be independently verified.")
    print("=" * 70)

    # Exit code
    if "ERROR" in result.get("summary", ""):
        sys.exit(2)
    elif result["valid"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
