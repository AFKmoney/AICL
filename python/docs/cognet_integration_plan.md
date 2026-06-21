# CogNet Integration Plan

**Status:** Implemented — corpus generator, training pipeline, and 1B model
support are all functional. See [docs/cognet-integration.md](../../docs/cognet-integration.md)
for the user-facing guide.
**Last updated:** 2026-06-20
**Owner:** Philippe-Antoine Robert (@AFKmoney)

This document explains how the CogNet ↔ AICL integration works. The corpus
generator produces spec→code pairs (using AX sub-language behaviors), and
CogNet is fine-tuned on them via the `cloud_train.py` pipeline.

## Goal

Bidirectional bridge between AICL specifications and the CogNet cognitive
engine (a non-transformer language model with hierarchical memory and
cognitive routing). The bridge lets CogNet reason over AICL programs as
first-class cognitive representations, and lets AICL programs invoke
CogNet as a reasoning backend.

The full design is specced in AICL itself in
[`examples/86_cognet_aicl_bridge.aicl`](../examples/86_cognet_aicl_bridge.aicl)
through
[`examples/91_cognet_autonomous_deployment.aicl`](../examples/91_cognet_autonomous_deployment.aicl).
Those six example programs collectively form the integration specification.

## What is in place today

```
python/src/aicl/cognet/
├── __init__.py        Public API surface (currently empty — see below)
└── README.md          This file's shorter sibling, viewable from the package
```

The `cognet/` subpackage is reserved. Importing `aicl.cognet` today succeeds
but exposes no symbols. This lets us:

1. Add the import path in `__init__.py` without breaking existing code.
2. Land type stubs and protocol definitions incrementally.
3. Keep the public API stable across the integration rollout.

## What is NOT in place yet

- The actual bridge implementation (translation layer between AICL AST and
  CogNet cognitive graph).
- CogNet model loading / inference glue.
- Round-trip fidelity tests.
- A `cognet` subcommand on the `aicl` CLI.

## Planned rollout

### Phase 1 — Bridge protocol (target: v2.2)
- Implement `aicl.cognet.bridge.AICLCognetBridge` with two methods:
  - `spec_to_graph(source: str) -> CognetGraph`
  - `graph_to_spec(graph: CognetGraph) -> str`
- Property-based round-trip test: `graph_to_spec(spec_to_graph(p)) ~ p`
- Add `aicl cognet translate <file>` subcommand

### Phase 2 — CogNet as reasoning backend (target: v2.3)
- New `Native:` section handler in the compiler that delegates to CogNet
  for runtime reasoning (cognitive routing decisions).
- Wire `runtime.py` Risk → Recovery selection through CogNet when a
  `Native: CogNet` section is present.

### Phase 3 — Autonomous CogNet self-evolution (target: v2.4)
- Implement the spec from example 87 (`87_cognet_self_evolution.aicl`).
- The autonomous compilation loop (`aicl evolve`) gains a CogNet mode
  where the LLM-backed `ai_generator.py` is replaced by a local CogNet
  model for fully offline self-modification.

### Phase 4 — Full AGI loop (target: v3.0)
- Bidirectional AICL ↔ CogNet loop where AICL specs drive CogNet training
  data, and CogNet reasoning drives AICL spec evolution.
- Examples 89–91 (training pipeline, evaluation, autonomous deployment)
  become executable end-to-end.

## How to integrate when ready

When the CogNet runtime is published:

1. Add `cognet-runtime` as an optional dependency in `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   cognet = ["cognet-runtime>=1.0"]
   ```
2. Implement `bridge.py` in this folder.
3. Re-export public symbols from `__init__.py`.
4. Add the `cognet` subcommand in `cli.py`.
5. Land property-based round-trip tests in `tests/test_cognet_bridge.py`.

Until then, this folder is a deliberate placeholder. Do not remove it.
