<div align="center">

# AICL

**Architecture Compilation Language**

*Auditable compilation with Proof of Origin.*
*If the compiler cannot explain why, it does not generate.*

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-151%20passing-brightgreen.svg)](#tests)
[![Audit](https://img.shields.io/badge/audit%20coverage-100%25-brightgreen.svg)](#proof-of-origin)
[![Targets](https://img.shields.io/badge/targets-Python%20%7C%20Rust%20%7C%20JS%20%7C%20Go-blue.svg)](#targets)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](./LICENSE)

</div>

---

## What AICL is

AICL is a **specification-first programming language**. Risks, recoveries, and
validations are not comments — they are mandatory syntactic elements. Every
generated artifact carries provenance; every compilation produces a
cryptographic **Proof of Origin**; every risk declared in source has a matching
recovery executed by the runtime.

You write **architecture**. The compiler writes **code**. The proof chain
explains **why**.

```aicl
Goal:
Render a blue square in a window for 60 seconds

Constraint:
Window must close on ESC key

Risk:
Windowing subsystem unavailable

Recovery:
Fall back to headless framebuffer capture

Layer:
Renderer

Validation:
At least one frame is produced

Behavior RenderFrame
    Input: Frame
    Output: Pixels
    Action: clear screen to blue and present
```

Compiles to verified Python / Rust / JavaScript / Go, with a sidecar
`*.aicl-proof` file that cryptographically ties each generated line back to
the spec.

## Why

Traditional languages mix objective, implementation, risk, recovery, and
validation in the same syntactic space, maximising learning noise for both
humans and AI. AICL forces these dimensions apart and makes each one a
first-class, machine-checkable element of the program.

The result is three properties that no conventional language gives you for
free:

1. **Auditability** — every generated line has a recorded reason.
2. **Verifiability** — every spec is checked for completeness and coherence
   before any code is emitted.
3. **Self-healing** — declared Risks are bound to declared Recoveries at
   compile time and executed by the runtime when the risk fires.

## Install

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL
pip install -e ".[tui]"        # core package + terminal UI
```

Requires Python 3.10+. The optional TUI extras pull in
[`textual`](https://textual.textualize.io/) and
[`rich`](https://rich.readthedocs.io/).

## Quick start

```bash
# Compile a program
aicl compile examples/01_blue_square.aicl

# Inspect the architecture tree
aicl tree examples/01_blue_square.aicl

# Verify spec completeness
aicl verify examples/01_blue_square.aicl

# Audit a compilation
aicl audit output/main.py --proof output/main.aicl-proof

# Explain why each line was generated
aicl explain examples/01_blue_square.aicl

# Launch the interactive terminal UI
aicl tui
```

`aicl --help` lists all 13 subcommands.

## The language in one minute

AICL has 27 keywords organised across 10 language levels. The full BNF is in
[`spec/grammar.md`](./spec/grammar.md).

| Level | Mandatory? | Keywords |
|-------|-----------|----------|
| 1. Architecture | **Yes** | `Goal`, `Constraint`, `Layer`, `Validation` |
| 2. Risk management | **Yes** | `Risk`, `Recovery` |
| 3. Data | No | `Entity`, `Field` |
| 4. Behaviour | No | `Behavior`, `Input`, `Output`, `Action` |
| 5. Reactivity | No | `When`, `Then`, `Event`, `On` |
| 6. Concurrency | No | `Parallel`, `Sequence` |
| 7. Optimisation | No | `Optimize`, `Learn`, `Adapt` |
| 8. Security | No | `Security`, `Native` |
| 9. Modules | No | `import`, `export` |
| 10. AI autonomy | No | `Evolve`, `SpecEvolver` |

A program without a `Goal` does not compile. A program with a `Risk` but no
matching `Recovery` does not compile. A program whose `Validation` cannot be
traced back to a `Goal` does not compile. The compiler enforces intent.

## Targets

The compiler emits code for four backends, all from the same `.aicl` source:

| Target | Flag | Output |
|--------|------|--------|
| Python | `--target python` (default) | `main.py` + `test_main.py` |
| Rust   | `--target rust`   | `main.rs` + tests |
| JavaScript | `--target javascript` | `main.mjs` |
| Go     | `--target go`     | `main.go` |

Each backend produces an identical `.aicl-proof` file — the Proof of Origin is
target-independent.

## Proof of Origin

Every compilation emits a `.aicl-proof` JSON file that records, for each
generated artifact:

- the source span it was derived from
- the compilation stage that produced it
- a SHA-256 hash of the artifact
- (optionally) an Ed25519 signature over the proof chain

Proofs can be inspected with `aicl proof` and verified out-of-band with
`tools/verify_proof.py`. A proof that does not verify means the compilation
was tampered with after the fact — **the artifact is not trustworthy**.

## Autonomous compilation

AICL can write itself. The `evolve` subcommand runs a self-writing,
self-validating loop:

```
spec → compile → run tests → diagnose failures → patch spec → repeat
```

The loop terminates when the spec compiles, tests pass, and audit coverage
hits 100%. Patterns learned across runs are persisted to a pattern library
and reused on subsequent invocations. See `src/aicl/autonomous.py` and
`src/aicl/ai_generator.py`.

## Web editor (optional)

The repo also ships a Next.js 16 web editor that exposes the compiler through
a browser UI: live compilation, architecture-tree visualisation, proof
inspection, AI-assisted spec authoring, and interactive exercises.

```bash
cp .env.example .env
bun install            # or npm / pnpm install
bun run db:push        # initialise the SQLite database
bun run dev            # http://localhost:3000
```

The editor talks to the Python `aicl` package through
[`scripts/aicl_helper.py`](./scripts/aicl_helper.py), a small JSON-over-stdio
bridge. The web editor is **optional** — the language is fully usable from
the CLI and TUI without Node.

## Tests

```bash
pytest tests/ -v
```

151 tests cover parsing, all 10 language levels, every backend, the
autonomous loop, the spec verifier, the ownership analyser, the optimiser,
and the Proof of Origin chain. All pass on Python 3.10, 3.11, and 3.12.

## Examples

91 example programs live in [`examples/`](./examples):

- `01_blue_square.aicl` … `04_chess.aicl` — the original four reference programs
- `05_banking.aicl` … `85_rideshare.aicl` — domain gallery (fintech, blockchain,
  ML pipelines, IoT, gaming, healthcare, energy, transport…)
- `86_cognet_aicl_bridge.aicl` … `91_cognet_autonomous_deployment.aicl` —
  integration with the CogNet cognitive engine

## Project layout

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for a detailed map of the
repository. The short version:

```
src/aicl/     the language (Python package — the core artifact)
spec/         formal grammar
examples/     91 AICL programs
tests/        151 pytest tests
tools/        developer utilities
scripts/      bridge used by the web editor
datasets/     JSONL training sets for fine-tuning LLMs on AICL
docs/         papers, manuals, screenshots
src/app/      Next.js 16 web editor (optional)
prisma/       editor database schema
```

## Documentation

- [Formal grammar](./spec/grammar.md)
- [Position paper](./docs/position_paper.md) — why AICL exists
- [arXiv paper (LaTeX source)](./docs/arxiv_paper.tex) — full academic treatment
- [arXiv paper (PDF)](./docs/arxiv_paper.pdf)
- [User manual (PDF)](./docs/AICL_User_Manual.pdf)
- [CLI / TUI manual (PDF)](./docs/AICL_CLI_TUI_Manual.pdf)
- [Editor manual (PDF)](./docs/AICL_Editor_Manual.pdf)
- [Contributing](./CONTRIBUTING.md)
- [Security policy](./SECURITY.md)
- [Citation](./CITATION.cff)

## Contributing

Pull requests welcome. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) first.
Please open an issue before starting work on a large change.

## License

MIT — see [`LICENSE`](./LICENSE).

## Author

**Philippe-Antoine Robert** — [GitHub @AFKmoney](https://github.com/AFKmoney)

> *Think better, not bigger.*
