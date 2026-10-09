"""Convergence must not be padded, and spec_verified must be the verifier."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aicl.autonomous import LoopController, LoopIteration, SpecEvolver
from aicl.provenance import ProvenanceType


def _iteration(**overrides):
    base = dict(
        iteration=1,
        state_entered=__import__("aicl.autonomous", fromlist=["LoopState"]).LoopState.COMPILING,
        timestamp_start=0.0,
        timestamp_end=1.0,
        tests_passed=4,
        tests_failed=0,
        tests_total=4,
        audit_coverage=1.0,
        fallback_count=0,
        spec_verified=True,
        proof_valid=True,
        padding_blocked=False,
        spec_evolved_count=0,
    )
    base.update(overrides)
    return LoopIteration(**base)


def test_record_iteration_does_not_infer_spec_from_tests():
    controller = LoopController()
    # Tests green and coverage full, but the verifier failed.
    controller.record_iteration(_iteration(spec_verified=False))
    assert controller.history[-1]["spec_verified"] is False
    assert controller.history[-1]["spec_verified"] != (
        controller.iterations[-1].tests_failed == 0
        and controller.iterations[-1].audit_coverage >= 1.0
    )


def test_padding_and_missing_proof_block_convergence():
    controller = LoopController()
    controller.record_iteration(_iteration(iteration=1, padding_blocked=True, spec_evolved_count=1))
    controller.record_iteration(_iteration(iteration=2, padding_blocked=True, spec_evolved_count=1))
    assert controller.is_converged is False

    clean = LoopController()
    clean.record_iteration(_iteration(iteration=1, proof_valid=False))
    clean.record_iteration(_iteration(iteration=2, proof_valid=False))
    assert clean.is_converged is False

    ok = LoopController()
    ok.record_iteration(_iteration(iteration=1))
    ok.record_iteration(_iteration(iteration=2))
    assert ok.is_converged is True


def test_spec_evolved_padding_is_marked_and_penalized():
    evolver = SpecEvolver()
    source = "Risk: account overdraft\nValidation:\nBalance stays non-negative\n"
    _patched, changes = evolver.evolve_from_verification(
        source,
        {"checks": [{"name": "risk_recovery_pairing", "status": "FAIL", "message": "no recovery"}]},
    )
    assert evolver.padding_closures
    assert any(c.startswith("SPEC_EVOLVED") for c in changes)
    assert "[SPEC_EVOLVED]" in _patched
    assert any(entry.get("provenance") == ProvenanceType.SPEC_EVOLVED.value for entry in evolver.evolution_log)

    _covered, cov_changes = evolver.evolve_from_audit_gap(
        source,
        {"audit_coverage": 0.4, "orphan_artifacts": ["main.py"]},
    )
    assert any("tautolog" in c for c in cov_changes)
    assert any(item.startswith("audit_coverage:") for item in evolver.padding_closures)

    padded = _iteration(padding_blocked=True, spec_evolved_count=2)
    honest = _iteration()
    controller = LoopController()
    assert controller._compute_score(padded) < controller._compute_score(honest)
