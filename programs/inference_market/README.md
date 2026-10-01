# inference-market

Solana-facing husk of the AICL Inference Market.

- Spec: `python/examples/showcase/90_inference_market.aicl`
- Class v0: `python/examples/showcase/91_tiny_inference_class.aicl`
- Reference machine: `python/src/aicl/market/`

```bash
cd programs/inference_market && cargo test
cd python && pytest tests/test_inference_market.py -q
```

Do not add a mint instruction until one job has taken the `Settle` path in this crate and in the Python engine.
