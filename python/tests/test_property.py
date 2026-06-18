"""
Property-based tests for the AICL compiler using Hypothesis.

These tests generate randomised but well-formed AICL programs and verify
that the compiler upholds its core invariants:

  1. Round-trip:  parse(program) succeeds for well-formed minimal programs
  2. Audit coverage:  every compiled artifact has provenance (100%)
  3. Proof of Origin:  every successful compilation produces a valid proof
  4. Idempotent verification:  verify(program) returns the same overall
     verdict regardless of how many times it is called
  5. Determinism:  compiling the same program twice yields identical output

The generators are intentionally conservative — they produce programs that
*should* compile, then check that the compiler agrees. Failure of a property
test indicates a real bug in the compiler.
"""

from __future__ import annotations

import string

from hypothesis import HealthCheck, given, settings, strategies as st

from aicl import Compiler, Parser, verify_source


# --------------------------------------------------------------------------
# Generators
# --------------------------------------------------------------------------

# Identifiers used in entities/behaviours — kept simple to avoid parser edge
# cases that are not the subject of these tests.
identifiers = st.text(
    alphabet=string.ascii_letters + string.digits + "_",
    min_size=3,
    max_size=20,
).filter(lambda s: s[0].isalpha() and s.isidentifier())


@st.composite
def valid_minimal_program(draw):
    """Generate a minimal but always-valid AICL program.

    A minimal valid program has:
      - exactly one Goal
      - at least one Layer
      - exactly one Validation
      - one Risk with one matching Recovery (so the spec is complete)
    """
    goal_text = draw(
        st.text(alphabet=string.ascii_letters + " ", min_size=10, max_size=80)
    )
    layer_name = draw(identifiers)
    validation_text = draw(
        st.text(alphabet=string.ascii_letters + " ", min_size=5, max_size=60)
    )
    risk_text = draw(
        st.text(alphabet=string.ascii_letters + " ", min_size=5, max_size=60)
    )
    recovery_text = draw(
        st.text(alphabet=string.ascii_letters + " ", min_size=5, max_size=60)
    )

    return f"""Goal:
{goal_text}

Constraint:
System must be deterministic

Risk:
{risk_text}

Recovery:
{recovery_text}

Layer:
{layer_name}

Validation:
{validation_text}
"""


# --------------------------------------------------------------------------
# Properties
# --------------------------------------------------------------------------


@given(program_source=valid_minimal_program())
@settings(
    max_examples=50,
    deadline=2000,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_property_parse_succeeds_for_valid_minimal_programs(program_source: str) -> None:
    """Property 1: a minimal valid program always parses successfully."""
    parser = Parser(source=program_source)
    ast = parser.parse()
    assert ast is not None
    assert len(ast.goals) >= 1
    assert len(ast.layers) >= 1
    assert len(ast.validations) >= 1


@given(program_source=valid_minimal_program())
@settings(
    max_examples=30,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_property_compile_produces_100pct_audit_coverage(program_source: str) -> None:
    """Property 2: a valid program compiles with 100% audit coverage."""
    compiler = Compiler(target_language="python")
    result = compiler.compile(program_source)
    assert result.success, f"Compile failed: {result.errors}"
    # audit_coverage is a dict with an "audit_coverage" float inside
    audit = result.proof.audit_coverage
    coverage_value = audit["audit_coverage"] if isinstance(audit, dict) else audit
    assert coverage_value == 1.0, f"Audit coverage was {coverage_value}, expected 1.0"
    assert result.todo_count == 0, f"Unresolved TODOs: {result.todo_count}"
    assert result.fully_compiled, "Program did not fully compile"


@given(program_source=valid_minimal_program())
@settings(
    max_examples=30,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_property_compile_produces_valid_proof_of_origin(program_source: str) -> None:
    """Property 3: every successful compilation produces a valid proof chain."""
    compiler = Compiler(target_language="python")
    result = compiler.compile(program_source)
    assert result.success

    proof = result.proof
    assert proof is not None, "No Proof of Origin generated"
    assert proof.verify(), "Proof of Origin failed verification"
    assert len(proof.records) > 0, "Proof chain has no records"


@given(program_source=valid_minimal_program())
@settings(
    max_examples=30,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_property_verifier_is_idempotent(program_source: str) -> None:
    """Property 4: verify_source() returns the same verdict across calls."""
    report1 = verify_source(program_source)
    report2 = verify_source(program_source)
    assert report1.passed == report2.passed, (
        f"Verifier returned different verdicts: passed={report1.passed} vs {report2.passed}"
    )
    assert len(report1.all_results) == len(report2.all_results)


@given(program_source=valid_minimal_program())
@settings(
    max_examples=20,
    deadline=8000,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_property_compilation_is_deterministic(program_source: str) -> None:
    """Property 5: compiling the same program twice yields identical output."""
    r1 = Compiler(target_language="python").compile(program_source)
    r2 = Compiler(target_language="python").compile(program_source)
    assert r1.success and r2.success
    assert r1.source_code == r2.source_code, "Compilation is non-deterministic"
    assert r1.test_code == r2.test_code
