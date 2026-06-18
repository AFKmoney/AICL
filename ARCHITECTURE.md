# AICL — Architecture

This document explains how the repository is organised. For *what* AICL is
and *why* it exists, see [README.md](./README.md). For the formal grammar,
see [`python/spec/grammar.md`](./python/spec/grammar.md).

## Repository layout

AICL is a **single repository** with two cooperating stacks. The Python
language lives in `python/` and the web editor lives in `editor/`. They
share documentation in `docs/` and CI in `.github/workflows/`.

```
AICL/
├── python/                          The AICL language (Python package)
│   ├── src/aicl/                    Core implementation
│   │   ├── parser.py                  Parse AICL source → AST
│   │   ├── ast.py                     AST node definitions
│   │   ├── ir.py                      Architecture Tree IR (the "real program")
│   │   ├── compiler.py                9-stage compiler: spec → Python/Rust/JS/Go
│   │   ├── provenance.py              Per-artifact provenance + Proof of Origin
│   │   ├── crypto_signing.py          Cryptographic signing of proofs
│   │   ├── spec_verify.py             Specification completeness/coherence checks
│   │   ├── runtime.py                 Self-healing runtime (Risk → Recovery binding)
│   │   ├── ownership.py               Ownership / lifetime analysis
│   │   ├── auto_optimizer.py          Architecture-level optimisation passes
│   │   ├── autonomous.py              Self-writing, self-validating compilation loop
│   │   ├── ai_generator.py            LLM-backed program synthesis & repair
│   │   ├── modules.py                 Multi-file programs (imports / exports)
│   │   ├── patterns.py                Behaviour pattern library & sub-language parser
│   │   ├── cli.py                     `aicl` command-line interface
│   │   ├── tui/                       Textual-based terminal UI
│   │   └── cognet/                    Placeholder for CogNet integration (v2.2+)
│   ├── spec/grammar.md               Formal BNF-style grammar
│   ├── examples/                     91 AICL programs
│   │   ├── showcase/                   20 curated programs + 6 CogNet specs + websocket/
│   │   └── archive/                    65 additional programs (training data, reference)
│   ├── tests/                        Pytest suite (156 tests, all passing)
│   │   ├── test_aicl.py                Original 151 tests
│   │   └── test_property.py            5 Hypothesis property-based tests
│   ├── tools/                        Developer utilities
│   │   ├── generate_dataset.py         JSONL dataset generator (portable)
│   │   ├── generate_whitepaper.py      Whitepaper PDF generator
│   │   ├── generate_editor_manual_v2.py Editor manual PDF generator
│   │   ├── verify_proof.py             Standalone Proof of Origin verifier
│   │   ├── visualize_provenance.py     Provenance graph visualiser
│   │   └── ai_bridge.mjs               Node.js bridge for z-ai-web-dev-sdk
│   ├── scripts/aicl_helper.py        JSON-over-stdio bridge for the web editor
│   ├── datasets/                     JSONL training sets for LLM fine-tuning
│   ├── docs/                         Bridge protocol, CogNet integration plan
│   ├── pyproject.toml                Package metadata, ruff/black/mypy config
│   ├── MANIFEST.in                   Sdist packaging
│   └── README.md                     (link to top-level README)
│
├── editor/                          AICL Editor — the web IDE (Next.js 16)
│   ├── src/app/                     Next.js app routes (API + UI)
│   │   ├── api/                       11 API routes (compile, verify, evolve, …)
│   │   ├── page.tsx                   Main editor page
│   │   ├── layout.tsx                 Root layout
│   │   └── globals.css                Tailwind + global styles
│   ├── src/components/ui/            shadcn/ui components (45 files)
│   ├── src/hooks/                    React hooks (use-mobile, use-toast)
│   ├── src/lib/                      Shared TS utilities
│   │   ├── aicl-bridge.ts              Shared Python bridge client (DRY)
│   │   ├── db.ts                       Prisma client
│   │   └── utils.ts                    Tailwind helper
│   ├── prisma/schema.prisma          Database schema (SQLite via Prisma)
│   ├── public/                       Static assets (logo, robots.txt)
│   ├── package.json                  Editor metadata
│   ├── bun.lock                      Bun lockfile
│   ├── next.config.ts                Next.js config
│   ├── tsconfig.json                 TypeScript config
│   ├── eslint.config.mjs             ESLint config
│   ├── tailwind.config.ts            Tailwind config
│   ├── postcss.config.mjs            PostCSS config
│   ├── components.json               shadcn/ui config
│   └── Caddyfile                     Reverse-proxy config (optional, production)
│
├── docs/                            Cross-cutting documentation
│   ├── position_paper.md            Why AICL exists
│   ├── arxiv_paper.tex              Academic paper (LaTeX source)
│   ├── arxiv_paper.pdf              Academic paper (PDF)
│   ├── AICL_User_Manual.pdf         End-user manual
│   ├── AICL_CLI_TUI_Manual.pdf      CLI/TUI manual
│   ├── AICL_Editor_Manual.pdf       Web editor manual
│   ├── CORRIGENDUM.txt              Corrections to earlier docs
│   ├── demo.cast                    Asciinema demo (run with `asciinema play`)
│   └── screenshots/                 5 editor screenshots
│
├── .github/workflows/ci.yml         CI: Python 3.10/3.11/3.12 + editor build
├── .pre-commit-config.yaml          ruff + black + mypy + eslint + tsc hooks
├── .gitignore                       Comprehensive ignore rules
├── .env.example                     Template for required env vars
├── Makefile                         Common dev tasks (`make help`)
├── ARCHITECTURE.md                  This file
├── README.md                        Project README
├── CHANGELOG.md                     Keep-a-Changelog format
├── CONTRIBUTING.md                  How to contribute
├── SECURITY.md                      Vulnerability disclosure policy
├── CITATION.cff                     Academic citation metadata
└── LICENSE                          MIT
```

## The two stacks

### 1. AICL — the language (Python)
- Package: `aicl` (v2.1.0), installed via `cd python && pip install -e .`
- Entry point: `aicl` CLI (`python -m aicl.cli`)
- 9-stage compiler producing auditable Python / Rust / JavaScript / Go
- 100% audit coverage — every generated artifact carries provenance
- Cryptographic Proof of Origin for every compilation
- Self-healing runtime that executes user-declared Recoveries on user-declared Risks
- 156-test pytest suite (151 functional + 5 Hypothesis property-based)

### 2. AICL Editor — the web IDE (Next.js)
- A Next.js 16 + React 19 + Prisma + shadcn/ui application
- Calls into the Python `aicl` package via
  [`python/scripts/aicl_helper.py`](./python/scripts/aicl_helper.py) (a
  JSON-over-stdio bridge — protocol in
  [`python/docs/bridge_protocol.md`](./python/docs/bridge_protocol.md))
- 11 API routes share a single bridge client (`editor/src/lib/aicl-bridge.ts`)
- Provides: spec editing, live compilation, architecture tree visualisation,
  proof inspection, AI-powered program synthesis, autonomous compilation
  loop, interactive exercises
- Has its own SQLite database (Prisma) — independent of AICL itself

The web editor is **optional**. The AICL language is fully usable from the
CLI and TUI without ever installing Node.

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

## Editor ↔ compiler data flow

```
Browser
   │  HTTP POST { source, target }
   ▼
Next.js API route (editor/src/app/api/<cmd>/route.ts)
   │  callAicl(subcommand, args, stdin)
   ▼
aicl-bridge.ts (editor/src/lib/aicl-bridge.ts)
   │  execFileSync(python, [helper, cmd, ...args], {input: source})
   ▼
aicl_helper.py (python/scripts/aicl_helper.py)
   │  JSON-over-stdio protocol (see bridge_protocol.md)
   ▼
aicl package (python/src/aicl/)
   │  Parser → AST → IR → 9-stage Compiler
   ▼
JSON response → HTTP response → Browser
```

## CogNet integration (planned)

```
                  ┌────────────────────────────┐
                  │   AICL spec (.aicl file)   │
                  └─────────────┬──────────────┘
                                │
                       spec_to_graph()
                                ▼
                  ┌────────────────────────────┐
                  │    CogNet cognitive graph  │
                  │  (hierarchical memory,     │
                  │   cognitive routing,       │
                  │   compositional inference) │
                  └─────────────┬──────────────┘
                                │
                       graph_to_spec()
                                ▼
                  ┌────────────────────────────┐
                  │  Evolved AICL spec         │
                  └────────────────────────────┘
```

The bridge is specced in
[`python/examples/showcase/cognet/`](./python/examples/showcase/cognet/)
and the rollout plan is in
[`python/docs/cognet_integration_plan.md`](./python/docs/cognet_integration_plan.md).
The `python/src/aicl/cognet/` subpackage is reserved as a placeholder so the
import path is stable across the integration rollout.

## Versioning

AICL follows semver `<major>.<minor>.<patch>` in
`python/pyproject.toml` and `python/src/aicl/__init__.py`. The web editor has
its own independent version in `editor/package.json`. The two are versioned
separately because the editor depends on the language, not the other way
around. Release history is in [`CHANGELOG.md`](./CHANGELOG.md).
