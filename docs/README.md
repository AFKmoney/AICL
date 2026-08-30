# AICL Documentation

Welcome to the AICL documentation. AICL is a specification-first programming
language where software is defined through structured architectural intent.
The compiler transforms your specs into executable Python, Rust, JavaScript,
and Go — with a cryptographic Proof of Origin.

---

## Start here

| If you want to... | Read this |
|-------------------|-----------|
| **Write your first AICL program** | [How to Code in AICL](./how-to-code-in-aicl.md) |
| **Install and run the compiler** | [Getting Started](./getting-started.md) |
| **Understand the vision** | [Position Paper](./position_paper.md) |

---

## Reference

| Doc | What it covers |
|-----|----------------|
| [How to Code in AICL](./how-to-code-in-aicl.md) | Practical guide — the mental model, the skeleton, every feature with examples |
| [AX Language Reference](./ax-language-reference.md) | Full grammar of the AX sub-language (statements, expressions, operators, data structures) |
| [Standard Library Reference](./stdlib-reference.md) | Every builtin function with target mappings (Python/JS/Rust/Go) |
| [AICL Cookbook](./cookbook.md) | 40+ ready-to-run recipes (algorithms, data processing, CRUD, I/O) |
| [Compile Targets](./targets.md) | How AX translates to Python, Rust, JavaScript, and Go |
| [Formal Grammar](../python/spec/grammar.md) | BNF for the full AICL language |
| [Proof of Origin](./proof-of-origin.md) | Cryptographic provenance and verification |

---

## Deep dives

| Doc | What it covers |
|-----|----------------|
| [White Paper](./whitepaper.md) | Complete technical overview — the definitive reference |
| [CogNet Integration](./cognet-integration.md) | Corpus generation, fine-tuning CogNet 1B |
| [Position Paper](./position_paper.md) | Why AICL exists — the no-orphan property |
| [arXiv Paper (LaTeX)](./arxiv_paper.tex) | Full academic treatment |

---

## Quick links

- **Examples**: [`python/examples/showcase/`](../python/examples/showcase/) — 20+ runnable AICL programs
- **Dataset**: [`python/aicl_dataset/`](../python/aicl_dataset/) — 151 AX-powered algorithm scripts
- **Tests**: [`python/tests/`](../python/tests/) — 210 passing tests
- **Web editor**: [`editor/`](../editor/) — Next.js 16 web IDE

---

## Learning path

### Beginner

1. Read [How to Code in AICL](./how-to-code-in-aicl.md) sections 1–4
2. Try the [cookbook](./cookbook.md) recipes for word counting and CSV parsing
3. Load examples in the web editor and experiment

### Intermediate

1. Read the [AX Language Reference](./ax-language-reference.md) end-to-end
2. Study the [Standard Library Reference](./stdlib-reference.md)
3. Build a small CRUD app using the cookbook patterns

### Advanced

1. Read the [White Paper](./whitepaper.md)
2. Study the [Proof of Origin](./proof-of-origin.md) and the independent verifier
3. Explore the [CogNet integration](./cognet-integration.md) for AI training

---

*Think better, not bigger. The architecture is the program; the code is a byproduct.*
