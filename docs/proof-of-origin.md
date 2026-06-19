# Proof of Origin

Every AICL compilation produces a `.aicl-proof` file — a cryptographic sidecar
that ties each generated line of code back to the exact spec it came from.

## What it contains

For each generated artifact, the proof records:

- **Source span** — the exact location in the `.aicl` source that produced it
- **Compilation stage** — which compiler phase generated it (parsing, pattern
  matching, sub-language, AX emission, fallback)
- **SHA-256 hash** — of the generated artifact
- **Resolution path** — the chain of decisions that led to this output

## Verify a proof

```bash
# Compile (generates the proof)
aicl compile myapp.aicl --target python -o ./output

# Audit: verify every artifact has provenance
aicl audit myapp.aicl

# Explain: show why each line was generated
aicl explain myapp.aicl

# Inspect the proof file directly
aicl proof output/main.aicl-proof
```

## Out-of-band verification

The proof file is self-contained — you don't need the AICL compiler to verify
it. The `verify_proof.py` tool checks the hash chain independently:

```bash
python tools/verify_proof.py output/main.aicl-proof
```

If verification fails, the compilation was tampered with after the fact. **The
artifact is not trustworthy.**

## Target independence

The proof is identical across all four compile targets. Whether you compile to
Python, Rust, JavaScript, or Go, the same `.aicl-proof` file is produced. The
provenance chain describes the spec→code mapping, not the target-specific
syntax.
