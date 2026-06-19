<div align="center">

# AICL

**Artificial Intelligence-Centered Language**

*Auditable compilation with Proof of Origin.*
*If the compiler cannot explain why, it does not generate.*

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-189%20passing-brightgreen.svg)](#tests)
[![Audit](https://img.shields.io/badge/audit%20coverage-100%25-brightgreen.svg)](#proof-of-origin)
[![Targets](https://img.shields.io/badge/targets-Python%20%7C%20Rust%20%7C%20JS%20%7C%20Go-blue.svg)](#targets)
[![AX](https://img.shields.io/badge/AX-Turing--complete%20sub--language-ff69b4.svg)](#ax-sub-language)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](./LICENSE)
[![CI](https://github.com/AFKmoney/AICL/actions/workflows/ci.yml/badge.svg)](https://github.com/AFKmoney/AICL/actions/workflows/ci.yml)

</div>

<p align="center">
  <a href="https://github.com/AFKmoney/AICL/releases/download/v2.1.0-pitch-v2/aicl_pitch_v2.mp4">
    <img src="https://img.shields.io/badge/▶_Watch-4_min_pitch_(2026)-FF0000?logo=youtube&logoColor=white" alt="Watch the 4-minute pitch video" />
  </a>
  <a href="https://github.com/AFKmoney/AICL/releases/download/v2.1.0-pitch/aicl_pitch.mp4">
    <img src="https://img.shields.io/badge/▶_Original_pitch-original-555.svg" alt="Original pitch video" />
  </a><br/>
  <sub>Updated pitch: AX sub-language, 4-target compilation, CogNet 1B. <a href="https://github.com/AFKmoney/AICL/releases/tag/v2.1.0-pitch-v2">Download MP4</a> (~8 MB).</sub>
</p>

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

## AX sub-language

AX (AICL-Action) is a **Turing-complete sub-language** for `Action:` sections.
Instead of free-form English prose that the compiler can only skeleton, AX
gives Behaviors a strict, compilable grammar: `if`/`elif`/`else`, `while`,
`for`, recursion via calls, arithmetic, comparisons, list literals, indexing,
method calls, and tuple swaps. The compiler translates any valid AX program
to **executable code in all four targets** — no stubs, no `pass`-empty bodies.

```aicl
Behavior Quicksort
    Input: array, low, high
    Output: pivot_index
    Action:
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1
```

This compiles to **real, runnable code** that sorts correctly — in Python,
JavaScript (Node), Rust (rustc), and Go. The AX module lives in
[`python/src/aicl/ax/`](./python/src/aicl/ax/) (lexer, parser, AST, four
emitters, type inference). Grammar and design:
[`docs/superpowers/specs/2026-06-18-aicl-turing-complete-design.md`](./docs/superpowers/specs/2026-06-18-aicl-turing-complete-design.md).

## Why

Traditional languages mix objective, implementation, risk, recovery, and
validation in the same syntactic space, maximising learning noise for both
humans and AI. AICL forces these dimensions apart and makes each one a
first-class, machine-checkable element of the program.

The result is three properties no conventional language gives you for free:

1. **Auditability** — every generated line has a recorded reason.
2. **Verifiability** — every spec is checked for completeness and coherence
   before any code is emitted.
3. **Self-healing** — declared Risks are bound to declared Recoveries at
   compile time and executed by the runtime when the risk fires.

## Demo

[![asciicast](https://asciinema.org/a/0/demo.svg)](https://asciinema.org/a/0/demo)

(Or open [`docs/demo.cast`](./docs/demo.cast) directly in
[asciinema](https://asciinema.org/) — `asciinema play docs/demo.cast`.)

## Install

**From PyPI (recommended for users):**

```bash
pip install aicl              # core package
pip install "aicl[tui]"       # core + terminal UI (textual + rich)
```

**From source (recommended for contributors):**

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL
make install-python   # or: cd python && pip install -e ".[tui,dev]"
```

Requires Python 3.10+. The optional `tui` extras pull in
[`textual`](https://textual.textualize.io/) and
[`rich`](https://rich.readthedocs.io/). The `dev` extras add `ruff`,
`black`, `mypy`, `pytest`, `hypothesis`, `pre-commit`, `build`, and
`twine`.

See [`python/docs/upgrading.md`](./python/docs/upgrading.md) for how to
upgrade, downgrade, and migrate between versions.

## Quick start

```bash
# Compile a program
aicl compile python/examples/showcase/01_blue_square.aicl

# Inspect the architecture tree
aicl tree python/examples/showcase/01_blue_square.aicl

# Verify spec completeness
aicl verify python/examples/showcase/01_blue_square.aicl

# Audit a compilation
aicl audit output/main.py --proof output/main.aicl-proof

# Explain why each line was generated
aicl explain python/examples/showcase/01_blue_square.aicl

# Launch the interactive terminal UI
aicl tui
```

`aicl --help` lists all 13 subcommands.

## The language in one minute

AICL has 27 keywords organised across 10 language levels. The full BNF is in
[`python/spec/grammar.md`](./python/spec/grammar.md).

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
`python/tools/verify_proof.py`. A proof that does not verify means the
compilation was tampered with after the fact — **the artifact is not
trustworthy**.

## Autonomous compilation

AICL can write itself. The `evolve` subcommand runs a self-writing,
self-validating loop:

```
spec → compile → run tests → diagnose failures → patch spec → repeat
```

The loop terminates when the spec compiles, tests pass, and audit coverage
hits 100%. Patterns learned across runs are persisted to a pattern library
and reused on subsequent invocations. See `python/src/aicl/autonomous.py` and
`python/src/aicl/ai_generator.py`.

## CogNet integration

AICL is the cognitive representation layer for the
[CogNet](https://github.com/AFKmoney/CogNet) non-transformer language model.
CogNet is fine-tuned on a corpus of **AICL spec → generated code** pairs so
it learns to write AICL/Python/Rust code from a specification.

**Corpus generator**: [`python/tools/corpus_generator.py`](./python/tools/corpus_generator.py)
produces the training data — 30 algorithm templates (sorts, searches, math,
string ops, primes, collatz, etc.) written in AX, each compiled to real code.
Output: `corpus/aicl_corpus.raw` (Python, 258k chars) or
`corpus/aicl_corpus_multitarget.raw` (Python + Rust, 305k chars).

**Training**: see the [CogNet repo](https://github.com/AFKmoney/CogNet) for
`cloud_train.py` (one-shot GPU training script) and `CLOUD_TRAINING.md`
(GPU recommendations, timing, checkpoint usage).

```bash
# Generate the corpus
python tools/corpus_generator.py --out corpus/aicl_corpus.raw --targets python

# Fine-tune CogNet (on a GPU instance)
python cloud_train.py --steps 5000
```

## Web editor (optional)

The repo ships a Next.js 16 web editor that exposes the compiler through a
browser UI: live compilation, architecture-tree visualisation, proof
inspection, AI-assisted spec authoring, and interactive exercises.

```bash
cp .env.example .env
cd editor && bun install
bun run db:push     # initialise the SQLite database
bun run dev         # http://localhost:3000
```

The editor talks to the Python `aicl` package through
[`python/scripts/aicl_helper.py`](./python/scripts/aicl_helper.py) via the
JSON-over-stdio protocol documented in
[`python/docs/bridge_protocol.md`](./python/docs/bridge_protocol.md). The web
editor is **optional** — the language is fully usable from the CLI and TUI
without Node.

## Tests

```bash
make test
# or: cd python && pytest tests/ -v
```

**156 tests** cover parsing, all 10 language levels, every backend, the
autonomous loop, the spec verifier, the ownership analyser, the optimiser,
the Proof of Origin chain, and **5 Hypothesis property-based tests** that
generate randomised valid programs and verify compiler invariants
(determinism, 100% audit coverage, valid proof chains, idempotent
verification). All pass on Python 3.10, 3.11, and 3.12.

## Examples

The curated showcase is in [`python/examples/showcase/`](./python/examples/showcase/)
(20 programs + 6 CogNet integration specs). The full set of 91 examples is in
[`python/examples/archive/`](./python/examples/archive/). See
[`python/examples/showcase/README.md`](./python/examples/showcase/README.md)
for the gallery index.

## Repository layout

The repo is a single workspace with two cooperating stacks. See
[`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full map.

```
python/           AICL — the language (Python package — the core artifact)
├── src/aicl/       Compiler, runtime, CLI, TUI, cognet/ placeholder
├── spec/           Formal BNF grammar
├── examples/       91 AICL programs (showcase/ + archive/)
├── tests/          156 pytest tests (incl. 5 property-based)
├── tools/          Developer utilities (dataset gen, proof verifier, AI bridge)
├── scripts/        aicl_helper.py — JSON bridge used by the web editor
├── datasets/       JSONL training sets for fine-tuning LLMs on AICL
├── docs/           Bridge protocol, CogNet integration plan
└── pyproject.toml  Package metadata, ruff/black/mypy config

editor/            AICL Editor — the web IDE (Next.js 16, optional)
├── src/app/        Next.js API routes + page
├── src/components/ shadcn/ui components
├── src/lib/        aicl-bridge.ts — shared Python bridge client
├── prisma/         Database schema (SQLite)
├── public/         Static assets
└── package.json    Editor metadata

docs/              Cross-cutting docs (papers, screenshots, asciinema demo)
.github/workflows/  CI (Python 3.10/3.11/3.12 + editor build)
```

## Documentation

- [Formal grammar](./python/spec/grammar.md)
- [Architecture overview](./ARCHITECTURE.md)
- [Bridge protocol (editor ↔ compiler)](./python/docs/bridge_protocol.md)
- [CogNet integration plan](./python/docs/cognet_integration_plan.md)
- [Upgrading AICL (user guide)](./python/docs/upgrading.md)
- [Releasing AICL (maintainer guide)](./RELEASING.md)
- [Position paper](./docs/position_paper.md) — why AICL exists
- [arXiv paper (LaTeX source)](./docs/arxiv_paper.tex) — full academic treatment
- [arXiv paper (PDF)](./docs/arxiv_paper.pdf)
- [User manual (PDF)](./docs/AICL_User_Manual.pdf)
- [CLI / TUI manual (PDF)](./docs/AICL_CLI_TUI_Manual.pdf)
- [Editor manual (PDF)](./docs/AICL_Editor_Manual.pdf)
- [Changelog](./CHANGELOG.md)
- [Contributing](./CONTRIBUTING.md)
- [Security policy](./SECURITY.md)
- [Citation](./CITATION.cff)

## Contributing

Pull requests welcome. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) first.
Install pre-commit hooks with `make install-precommit` — ruff, black, mypy,
and eslint will run automatically on every commit.

Please open an issue before starting work on a large change.

## License

MIT — see [`LICENSE`](./LICENSE).

## Author

**Philippe-Antoine Robert** — [GitHub @AFKmoney](https://github.com/AFKmoney)

> *Think better, not bigger.*
