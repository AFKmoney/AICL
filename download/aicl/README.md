<div align="center">

# AICL

**Architecture Compilation Language**

*If the compiler cannot explain why it generated a line, it should not generate it.*
*And this property must be independently verifiable without trusting the compiler.*

[![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-95%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Audit](https://img.shields.io/badge/audit%20coverage-100%25-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Proof](https://img.shields.io/badge/proof%20of%20origin-verifiable-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Install](#install) · [Quick Start](#quick-start) · [Proof of Origin](#proof-of-origin) · [Audit System](#audit-system) · [Language Reference](#language-levels) · [Grammar](spec/grammar.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## Why AICL Exists

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

But there is a deeper problem. Modern compilers and AI code generators produce millions of lines of code without ever being able to answer a simple question: **why?** Why was this line generated? What architectural decision produced it? What risk does this recovery address? And — critically — **can you verify this without trusting the compiler itself?**

No mainstream system can answer these questions. The code exists, but the reasoning behind it is lost the moment compilation finishes. And when the only entity that can vouch for the code's correctness is the same entity that generated it, you have a problem:

> **Trust me bro → AICL says AICL is correct**

AICL exists to solve this — and to make that solution **measurable and independently verifiable**.

## The Core Idea

AICL is an **Architecture Compilation System** that produces not just code, but a **Proof of Origin**: a self-contained, cryptographically bound artifact that proves every generated line has traceable provenance, and that this proof can be verified by anyone without installing AICL.

This means five things that no other system does together:

1. **Risk and Recovery are not optional.** You cannot write an AICL program without specifying what can fail and how to recover. The compiler enforces this the way other compilers enforce types.

2. **Validation compiles into tests.** Every `Validation:` section becomes executable test code — not a comment, not a wish, but a compiled test.

3. **Every artifact is explainable.** `aicl explain` tells you exactly why each method was generated, what pattern matched, and what source it came from.

4. **Audit coverage is measurable.** `aicl audit` verifies that every generated artifact has provenance. The target is always: **Audit Coverage = 100%**.

5. **Proofs are independently verifiable.** `verify_proof.py` (200 lines, zero AICL dependencies) verifies that the No-Orphan Property holds — without the compiler, without the parser, without trusting AICL at all.

```aicl
Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries
```

This is not a comment. It is not a try/catch you might remember to write. It is a **first-class language construct** that the compiler transforms into executable recovery logic — and produces a cryptographic proof that this transformation is traceable.

## What Makes This Different

Several systems have tried "architecture to code." That is not the novelty here.

The novelty is **auditable compilation with independently verifiable proof of origin**:

| | Traditional Compilers | AI Code Generators | AICL |
|---|---|---|---|
| **Risks** | Optional try/catch | Not considered | Mandatory `Risk:` keyword |
| **Recovery** | Scattered error handlers | Not considered | Paired `Recovery:` per risk |
| **Validation** | Separate test files | Not generated | Compiled from `Validation:` sections |
| **Architecture** | Documentation only | Hallucinated | Executable `Layer:` definitions |
| **Provenance** | None | None | Full audit trail (`aicl explain`) |
| **Audit** | None | None | Measurable coverage (`aicl audit`) |
| **Proof of Origin** | None | None | Self-contained `.aicl-proof` file |
| **Independent Verification** | None | None | `verify_proof.py` (zero AICL deps) |
| **Determinism** | Deterministic | Probabilistic | Deterministic by contract |

The key insight: **AICL does not use AI to write code.** AI is an optional plugin. The core compiler is 100% deterministic, using a library of 30+ behavior patterns. This is a deliberate design choice — you should never need to wonder whether your compiler made a creative decision.

**Traditional compilers generate code. AI generates code without accountability. AICL generates code with cryptographic proof of origin.**

---

## Proof of Origin

The Proof of Origin is AICL's central artifact. When you compile:

```
aicl compile pong.aicl --output-dir ./output
```

You get:

```
output/
├── main.py              # Executable program
├── test_main.py         # Generated test suite
├── architecture_tree.txt # Architecture visualization
└── main.aicl-proof      # Proof of Origin — the central artifact
```

### The Architectural Shift

```
Before:    AICL source → Compiler → Code
Then:      AICL source → Compiler → Code + Explain
Then:      AICL source → Compiler → Code + Audit
Now:       AICL source → Compiler → Proof of Origin
                                        ├── Code
                                        ├── Explain
                                        └── Audit
```

The proof is the central artifact. Code, explain, and audit are all **views on the proof**.

### Independent Verification

The critical test: **can a third party verify the proof without using AICL?**

```bash
# This uses ZERO AICL dependencies — only Python stdlib
python tools/verify_proof.py output/main.aicl-proof

# Output:
======================================================================
AICL PROOF OF ORIGIN — INDEPENDENT VERIFICATION
======================================================================

  [PASS] format_version
  [PASS] source_hash_binding
  [PASS] program_hash_binding
  [PASS] test_hash_binding
  [PASS] no_orphan_artifact_property
  [PASS] complete_coverage_property
  [PASS] record_artifact_linkage
  [PASS] artifact_consistency

======================================================================
VERDICT: VALID

  This Proof of Origin is independently verifiable.
  No AICL compiler, parser, or project dependency was used.
  The No-Orphan Property is verified as a property of the artifact,
  not as a claim of the compiler.
======================================================================
```

**The No-Orphan Property is not a feature of the compiler. It is a verifiable property of an artifact produced by the compiler.** This distinction is critical.

### Proof Format v2.0

The `.aicl-proof` file (JSON) contains:

| Field | Purpose |
|-------|---------|
| `source_text` | Original AICL source |
| `generated_source` | Generated program code |
| `generated_tests` | Generated test code |
| `source_hash` | SHA-256 of source text |
| `program_hash` | SHA-256 of generated program |
| `test_hash` | SHA-256 of generated tests |
| `formal_properties` | No Orphan, Complete Coverage, Hash Binding |
| `records` | All provenance records (19 types) |
| `artifacts` | All generated artifacts with provenance linkage |

The proof is self-contained: an independent verifier recomputes hashes from the embedded code and compares them to the stored values. Any tampering is detected.

### Working with Proofs

```bash
# Inspect a proof
aicl proof output/main.aicl-proof

# Verify a proof
aicl proof output/main.aicl-proof --verify

# Explain from proof (no compiler needed)
aicl explain --proof output/main.aicl-proof
aicl explain --proof output/main.aicl-proof --behavior MovePaddle

# Audit from proof (no compiler needed)
aicl audit --proof output/main.aicl-proof
aicl audit --proof output/main.aicl-proof --strict

# Independent verification (no AICL needed at all)
python tools/verify_proof.py output/main.aicl-proof
```

---

## Audit System

The audit system is AICL's most original contribution. It introduces concepts that no other compiler offers:

### Auditability

> A program is **auditable** if every generated artifact can be traced to its originating specification through a complete provenance chain.

### Audit Coverage

> **Audit Coverage = Auditable Artifacts / Generated Artifacts**
>
> Target: **Audit Coverage = 1.0** (100%)

### Orphan Artifacts

> An **orphan artifact** is a generated artifact (method, class, function, test) without provenance. It exists in the code, but the compiler cannot explain why.

### Formal Properties

The audit system verifies three formal properties:

| Property | Statement | Verification |
|----------|-----------|-------------|
| **No Orphan Artifact** | Every generated artifact has at least one provenance chain | Orphan count = 0 |
| **Complete Coverage** | Audit Coverage = 1.0 | All artifacts have provenance |
| **Hash Binding** | Proof is cryptographically bound to generated code | SHA-256 hashes match |

### Using the Audit System

```bash
# Full audit report
aicl audit examples/02_pong.aicl

# Strict mode: fail if coverage < 100%
aicl audit examples/02_pong.aicl --strict

# Audit from proof file (no compiler needed)
aicl audit --proof output/main.aicl-proof --strict
```

Example output:

```
======================================================================
AICL AUDIT REPORT
======================================================================

ARTIFACT AUDIT
----------------------------------------------------------------------
  Generated artifacts:       52
  Artifacts with provenance: 52
  Orphan artifacts:          0

  Audit Coverage:            100.00%

  Audit Status: VERIFIED

COVERAGE BY ARTIFACT TYPE
----------------------------------------------------------------------
  method          35/ 35  100.00%  [VERIFIED]
  test_function   12/ 12  100.00%  [VERIFIED]
  dataclass        2/ 2  100.00%  [VERIFIED]
  class            1/ 1  100.00%  [VERIFIED]
  function         1/ 1  100.00%  [VERIFIED]
  import_block     1/ 1  100.00%  [VERIFIED]

======================================================================
AUDIT RESULT: PASSED
  Every generated artifact has provenance.
  Compilation is fully auditable.
======================================================================
```

---

## What It Looks Like

A complete Pong game in AICL:

```aicl
Goal:
    Build a Pong game

Constraint:
    Must run at 60 FPS minimum

Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries

Risk:
    Input lag detected

Recovery:
    Enable input buffering

Layer:
    Window Manager

Layer:
    Rendering System
        Sublayer: Sprite rendering
        Sublayer: Text rendering
        Sublayer: Background rendering

Layer:
    Input System

Layer:
    Physics Engine
        Sublayer: Ball movement
        Sublayer: Collision detection
        Sublayer: Paddle movement

Layer:
    Game Logic
        Sublayer: Score tracking
        Sublayer: Game state management

Entity Player
    name: string
    score: integer
    paddle_position: float

Entity Ball
    x: float
    y: float
    velocity_x: float
    velocity_y: float

Behavior MovePaddle
    Input: Player direction string
    Action: Update paddle position based on direction

Behavior UpdateBall
    Input: Ball
    Action: Update ball position and handle collisions

Condition:
    When ball hits paddle
    Then reflect ball velocity

Condition:
    When score reaches 10
    Then end match

Event:
    On key press
    Action: move corresponding paddle

Parallel:
    Rendering System
    Input System
    Physics Engine

Validation:
    Complete one playable match

Validation:
    Maintain 60 FPS during gameplay
```

Compile it:

```bash
aicl compile examples/02_pong.aicl --output-dir ./output
```

Then verify the proof independently:

```bash
python tools/verify_proof.py output/main.aicl-proof
# → VALID
```

Verify that every generated artifact has provenance — because **if you can't audit it, you can't trust it, and if you can't verify the audit independently, you're still just trusting the compiler**.

---

## Install

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL
pip install -e .
```

## Quick Start

### Compile an AICL program

```bash
aicl compile examples/02_pong.aicl --output-dir ./output
```

### Verify the proof independently

```bash
python tools/verify_proof.py output/main.aicl-proof
```

### Audit the compilation

```bash
aicl audit examples/02_pong.aicl               # Full audit report
aicl audit examples/02_pong.aicl --strict       # Fail if coverage < 100%
aicl audit --proof output/main.aicl-proof       # Audit from proof (no compiler)
```

### Inspect the architecture

```bash
aicl tree examples/04_chess.aicl       # Visualize the architecture tree
aicl parse examples/03_chat.aicl       # Dump the AST
aicl check examples/01_blue_square.aicl # Validate without compiling
```

### Understand the compilation

```bash
aicl explain examples/02_pong.aicl                          # Full compilation trace
aicl explain examples/02_pong.aicl --behavior MovePaddle    # Specific behavior trace
aicl explain examples/02_pong.aicl --coverage               # Explicability coverage report
aicl explain --proof output/main.aicl-proof                  # Explain from proof (no compiler)
```

### Inspect and verify a proof

```bash
aicl proof output/main.aicl-proof                # Inspect proof
aicl proof output/main.aicl-proof --verify       # Verify proof integrity
aicl proof output/main.aicl-proof --explain      # Full explanation from proof
aicl proof output/main.aicl-proof --audit        # Audit report from proof
```

### Run the tests

```bash
python -m pytest tests/ -v
```

---

## Examples

The `examples/` directory contains four programs of increasing complexity — all achieving **100% audit coverage** and **independently verifiable Proofs of Origin**:

| Example | Levels Used | Artifacts | Audit Coverage | Proof Verified |
|---------|------------|-----------|----------------|----------------|
| [`01_blue_square.aicl`](examples/01_blue_square.aicl) | 1 | 35 | 100% | VALID |
| [`02_pong.aicl`](examples/02_pong.aicl) | 1–6 | 52 | 100% | VALID |
| [`03_chat.aicl`](examples/03_chat.aicl) | 1–9 | 58 | 100% | VALID |
| [`04_chess.aicl`](examples/04_chess.aicl) | 1–9 | 59 | 100% | VALID |

---

## Language Levels

AICL is organized in 10 progressive levels. Every program must include **Level 1**; higher levels are used as needed.

| Level | Feature | Keywords | Example |
|:-----:|---------|----------|---------|
| **1** | **Architecture** *(mandatory)* | `Goal` `Constraint` `Risk` `Recovery` `Layer` `Sublayer` `Validation` | Every AICL program |
| **2** | **Entities** | `Entity` + typed fields | Data models |
| **3** | **Behaviors** | `Behavior` `Input` `Output` `Action` | Entity operations |
| **4** | **Conditions** | `Condition` `When` `Then` | Replace if/else |
| **5** | **Events** | `Event` `On` `Action` | Event-driven logic |
| **6** | **Concurrency** | `Parallel` | Concurrent layer execution |
| **7** | **Optimization** | `Optimize` `Priority` | Performance targets |
| **8** | **Learning** | `Learn` `Adapt` `Based` | ML integration |
| **9** | **Security** | `Security` `Encrypt` `Protect` | Security directives |
| **10** | **Native Code** | `Native` | Escape hatch for low-level code |

### Minimal Valid Program

A Level 1 program needs just three things — a goal, a layer, and a validation:

```aicl
Goal:
    Hello World

Layer:
    Core

Validation:
    Output is produced
```

---

## Compilation Pipeline

The AICL compiler does not just translate — it **reasons** about your architecture through a 9-stage pipeline, recording provenance at every step:

```
  ┌─────────────┐
  │  AICL Source │
  └──────┬──────┘
         │
    ┌────▼────┐
    │  Parse  │  ──→ AST (17 node types)
    └────┬────┘
         │
    ┌────▼──────────┐
    │  Architecture  │  ──→ Structural completeness check
    │  Validation    │     (Goal, Layer, Validation present)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Dependency   │  ──→ Layer dependency graph
    │  Analysis     │
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Risk         │  ──→ Risk/Recovery pairing
    │  Analysis     │     (every Risk needs a Recovery)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Recovery     │  ──→ Recovery logic synthesis
    │  Synthesis    │     + provenance recording
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Code         │  ──→ Python source + error handling
    │  Generation   │     (30+ deterministic patterns)
    │               │     + artifact registration
    │               │     + provenance per artifact
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Test         │  ──→ pytest suite from Validations
    │  Generation   │     + artifact registration
    │               │     + provenance linking
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Optimization │  ──→ Apply Optimize/Priority hints
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Final        │  ──→ main.py + test_main.py + tree
    │  Construction │     + main.aicl-proof (Proof of Origin)
    └──────────────┘
```

### Deterministic Behavior Compilation

The **Behavior Pattern Library** maps action descriptions to concrete code through 30+ deterministic patterns:

| Category | Patterns | Example |
|----------|----------|---------|
| Movement | MOVE, MOVE_BALL, REFLECT_VELOCITY, CLAMP_POSITION | "Update paddle position" → MOVE pattern |
| Creation | CREATE, INIT_LAYER, CREATE_WINDOW | "Create new game" → CREATE pattern |
| Communication | BROADCAST, SEND_MESSAGE | "Transmit message" → BROADCAST pattern |
| Update | UPDATE, INCREMENT_SCORE, UPDATE_STATE | "Clamp ball position" → CLAMP pattern |
| Display | DISPLAY, RENDER_FRAME, HIGHLIGHT | "Draw game frame" → RENDER pattern |
| Validation | VALIDATE, CHECK_COLLISION | "Validate move" → VALIDATE pattern |
| Networking | CONNECT, RECONNECT, DISCONNECT | "Connect to server" → CONNECT pattern |
| Persistence | STORE, LOAD | "Save game state" → STORE pattern |
| Security | ENCRYPT_DATA, PROTECT_ACCESS | "Encrypt message" → ENCRYPT pattern |

When no pattern matches, the **sub-language parser** handles explicit action specifications:

```aicl
Behavior MovePaddle
    Input: Player direction string
    Action: assign paddle_position += direction * speed
            clamp paddle_position between 0 and screen_width
```

This means **zero TODOs** in compiled output. Every behavior compiles to real, executable code — and every compilation decision is recorded in the provenance chain.

---

## Project Structure

```
AICL/
├── src/aicl/                    # Compiler source
│   ├── __init__.py              # Package exports (v0.7.0)
│   ├── cli.py                   # CLI: compile, parse, tree, check, explain, audit, proof
│   ├── parser.py                # Line-based parser → AST
│   ├── ast.py                   # 17 AST node dataclasses
│   ├── ir.py                    # Intermediate representation (Architecture Tree)
│   ├── compiler.py              # 9-stage compilation pipeline + artifact tracking
│   ├── patterns.py              # 30+ deterministic behavior patterns
│   ├── provenance.py            # Provenance tracker + audit + Proof of Origin
│   └── lexer.py                 # Lexical analyzer (standalone)
├── examples/                    # Example programs
│   ├── 01_blue_square.aicl      # Level 1 — simple graphics (35 artifacts, 100% audit)
│   ├── 02_pong.aicl             # Levels 1–6 — game with behaviors (52 artifacts, 100% audit)
│   ├── 03_chat.aicl             # Levels 1–9 — full-featured app (58 artifacts, 100% audit)
│   └── 04_chess.aicl            # Levels 1–9 — complex state (59 artifacts, 100% audit)
├── tests/                       # Test suite
│   └── test_aicl.py             # 95 tests (all passing, including proof + verifier tests)
├── spec/                        # Language specification
│   └── grammar.md               # Formal BNF grammar & keyword table
├── docs/                        # Documentation
│   └── whitepaper.pdf           # White paper (16 sections, v0.7)
├── tools/                       # Build and utility scripts
│   ├── generate_whitepaper.py   # White paper PDF generator
│   └── verify_proof.py          # Independent proof verifier (~200 lines, zero AICL deps)
├── pyproject.toml               # Python package configuration
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## Formal Specification

The complete language specification is in [`spec/grammar.md`](spec/grammar.md), including:

- Full BNF grammar for all 10 language levels
- 27 reserved keywords with level and purpose
- Type system (`string`, `integer`, `float`, `boolean`, `datetime`, `list`, `dict`, `set`, `any`, `void`, `bytes`)
- Comment syntax (lines starting with `#`)
- File extension (`.aicl`)

---

## White Paper

The white paper at [`docs/whitepaper.pdf`](docs/whitepaper.pdf) presents AICL as an Architecture Compilation System with **auditable provenance** as its central thesis:

- The provenance principle: a compiler that cannot explain why should not generate
- The No-Orphan Property: every artifact must have traceable provenance
- The Complete Coverage Property: audit coverage must equal 1.0
- Proof of Origin: self-contained, cryptographically bound compilation artifact
- Independent verification: proof verifiable without trusting the compiler
- The "Trust me bro" problem and how independent verification solves it
- Formal BNF grammar with derivation rules
- Risk and Recovery as mandatory language elements
- 19 provenance types covering all compilation zones
- Deterministic compilation contract
- Comparative analysis against DSLs, ADLs, and AI code generators

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| **v0.1** | Parser, grammar, Python codegen, 38 tests | Done |
| **v0.2** | Deterministic patterns, zero-TODO compilation, provenance | Done |
| **v0.3** | Sub-language expansion, architecture templates | Done |
| **v0.4** | Explicable compilation thesis, provenance-first design, project reorganization | Done |
| **v0.5** | Audit system, artifact tracking, 100% audit coverage, orphan detection, `aicl audit` | Done |
| **v0.6** | Proof of Origin v1.0, `aicl proof` command, explain/audit from proof file | Done |
| **v0.7** | Proof of Origin v2.0 (self-contained), independent verifier, 8 verification checks, No-Orphan as formal property | **Current** |
| **v0.8** | Position paper: "The No-Orphan Property: Towards Auditable Code Generation" | Planned |
| **v0.9** | Specification compilation: completeness checking, coherence checking, satisfaction checking, `aicl verify` | Planned |
| **v0.10** | Multi-file programs: import and module mechanisms, cross-file provenance | Planned |
| **v0.11** | Cryptographic proof signing: proof files signed with compiler key, proof chain across compilations | Planned |
| **v1.0** | Multi-language targets (Rust, JavaScript, Go), mature compiler, stable proof format | Future |
| **v1.5** | Provenance visualization: interactive exploration of compilation provenance graphs | Future |
| **v2.0** | Self-healing runtime with automatic recovery execution and runtime provenance | Future |
| **v2.5** | Memory management: ultra-simple ownership model derived from Layer/Entity structure | Future |
| **v3.0** | Autonomous architecture optimization, specification-driven refactoring | Future |

### The Conceptual Trajectory

The roadmap reflects a deepening understanding of what auditable compilation means:

```
v0.1–v0.3:  "I want a simpler language than C++"
v0.4–v0.5:  "I want the compiler to explain itself"     → Explicable Compilation
v0.5–v0.6:  "I want to measure that explanation"         → Auditable Compilation
v0.7:        "I want proof that doesn't require trust"    → Proof of Origin + Independent Verification
v0.8:        "This idea transcends AICL itself"           → The No-Orphan Property (Position Paper)
v0.9:        "I want to verify the specification"         → Specification Compilation
v0.11:       "I want the proof to be tamper-proof"        → Cryptographic Proof Signing
```

Each stage discovered that the previous stage's endpoint was actually the beginning of a deeper problem. Explicable compilation raised the question of measurement. Measurement raised the question of trust. Trust raised the question of independent verification.

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **The No-Orphan Position Paper** — Help formalize the argument that every code-generating system should demonstrate 100% provenance coverage
- **Specification compilation** — Implement completeness, coherence, and satisfaction checking for AICL specifications
- **Cryptographic proof signing** — Sign proof files with compiler keys, create proof chains across compilations
- **New target languages** — Rust, TypeScript, Go code generation backends
- **New behavior patterns** — Expand the deterministic pattern library
- **Provenance visualization** — Tools to explore and visualize compilation provenance
- **IDE support** — Syntax highlighting, LSP server, VS Code extension
- **New examples** — Real-world programs showcasing different levels

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Philippe-Antoine**

---

<div align="center">

*"Traditional compilers generate code. AI generates code without accountability.*
*AICL generates code with cryptographic proof of origin — and that proof can be verified by anyone."*

</div>
