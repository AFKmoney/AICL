# AICL — Architecture

This document explains how the repository is organised. For *what* AICL is
and *why* it exists, see [README.md](./README.md). For the formal grammar,
see [`python/spec/grammar.md`](./python/spec/grammar.md).

## Autonomous compilation loop

`python/src/aicl/autonomous.py` runs:

```
spec → compile → verify → test → diagnose → fix → recompile
```

Termination is hard: `max_iterations` (default 10) and a 30s test timeout.
`SpecEvolver` is rule-based. It may add a clause; it never deletes a Goal
or a Validation. The original file is not overwritten — the result is a
sibling `.evolved.aicl`.

Convergence is refused unless all of the following hold on the iteration:

1. `SpecificationVerifier` passed. This is the verifier report, not
   `tests_failed == 0 and audit_coverage >= 1.0`.
2. Audit coverage is 1.0.
3. Generated tests passed.
4. No fallback compilations remain.
5. Score delta is under the threshold.
6. Proof of Origin was verified **this iteration**. A missing or invalid
   proof blocks. It is not an end-of-run report.
7. No `SPEC_EVOLVED` padding is what closed a check. A generic
   `Handle … gracefully` recovery, a placeholder action, or the tautological
   validation "All generated code artifacts have traceable provenance"
   is tagged `[SPEC_EVOLVED]`, penalized in the score, and blocks
   convergence for the rest of the session.

The rest of this document is the repository layout. The loop gates above
are the contract `LoopController` enforces.
