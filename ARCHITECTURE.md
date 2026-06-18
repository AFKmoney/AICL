# AICL — Architecture

This document explains how the repository is organised. For *what* AICL is and
*why* it exists, see [README.md](./README.md). For the formal grammar, see
[spec/grammar.md](./spec/grammar.md).

## High-level layout

```
AICL/
├── src/aicl/            The AICL language — Python package (the core artifact)
│   ├── parser.py          Parse AICL source → AST
│   ├── ast.py             AST node definitions
│   ├── ir.py              Architecture Tree IR (the "real program")
│   ├── compiler.py        9-stage compiler: spec → Python/Rust/JS/Go
│   ├── provenance.py      Per-artifact provenance + Proof of Origin
│   ├── crypto_signing.py  Cryptographic signing of proofs
│   ├── spec_verify.py     Specification completeness/coherence checks
│   ├── runtime.py         Self-healing runtime (Risk → Recovery binding)
│   ├── ownership.py       Ownership / lifetime analysis
│   ├── auto_optimizer.py  Architecture-level optimisation passes
│   ├── autonomous.py      Self-writing, self-validating compilation loop
│   ├── ai_generator.py    LLM-backed program synthesis & repair
│   ├── modules.py         Multi-file programs (imports / exports)
│   ├── patterns.py        Behaviour pattern library & sub-language parser
│   ├── cli.py             `aicl` command-line interface
│   └── tui/               Textual-based terminal UI
├── spec/grammar.md      Formal BNF-style grammar
├── examples/            91 AICL programs (01–04 = core, 05–91 = domain gallery)
│   └── websocket/        Example frontend + server for reactive AICL programs
├── tests/               Pytest suite (151 tests, all passing)
├── tools/               Developer utilities (dataset gen, proof verifier, …)
├── scripts/             `aicl_helper.py` — JSON bridge used by the web editor
├── datasets/            JSONL training sets for fine-tuning LLMs on AICL
├── docs/                Papers, manuals, screenshots
├── prisma/              Prisma schema for the web editor
├── src/app/             Next.js 16 app routes (the web editor — API + UI)
├── src/components/      shadcn/ui components
├── src/hooks/           React hooks
├── src/lib/             Shared TS utilities
├── public/              Static assets served by the editor
├── pyproject.toml       Python package metadata
├── package.json         Web editor metadata
├── Caddyfile            Reverse-proxy config (optional, production)
├── CONTRIBUTING.md      How to contribute
├── SECURITY.md          Vulnerability disclosure policy
├── CITATION.cff         Academic citation
└── Makefile             Common dev tasks
```

## The two stacks

The repository contains **two independent but cooperating stacks**:

### 1. AICL — the language (Python)
- Package: `aicl` (v2.1.0), installed via `pip install -e .`
- Entry point: `aicl` CLI (`python -m aicl.cli`)
- 9-stage compiler producing auditable Python / Rust / JavaScript / Go
- 100% audit coverage — every generated artifact carries provenance
- Cryptographic Proof of Origin for every compilation
- Self-healing runtime that executes user-declared Recoveries on user-declared Risks

### 2. AICL Editor — the web IDE (Next.js)
- A Next.js 16 + React 19 + Prisma + shadcn/ui application
- Calls into the Python `aicl` package via `scripts/aicl_helper.py` (a JSON-over-stdio bridge)
- Provides a browser-based editor with: spec editing, live compilation, architecture tree visualisation, proof inspection, AI-powered program synthesis, autonomous compilation loop, interactive exercises
- Has its own SQLite database (Prisma) for users / posts / sessions — independent of AICL itself

The web editor is **optional**. The AICL language is fully usable from the CLI
and TUI without ever installing Node.

## Data flow

```
.aicl source
     │
     ▼
  Parser ──► AST ──► Architecture Tree (IR)
                              │
                              ▼
                    9-stage Compiler
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Python code      Rust code        JS / Go code
              │               │               │
              └───────┬───────┴───────┬───────┘
                      ▼               ▼
              test_main.py     *.aicl-proof
                      │       (cryptographic
                      │        Proof of Origin)
                      ▼
              Self-healing runtime
              (Risk → Recovery binding)
```

## Versioning

AICL follows the pattern `<major>.<minor>.<patch>` in `pyproject.toml` and
`src/aicl/__init__.py`. The web editor has its own independent version in
`package.json`. The two are versioned separately because the editor depends on
the language, not the other way around.
