<div align="center">

# AICL

**Architecture Compilation Language**

*If the compiler cannot explain why it generated a line, it should not generate it.*

[![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-63%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Install](#install) · [Quick Start](#quick-start) · [Examples](#examples) · [Language Reference](#language-levels) · [Grammar](spec/grammar.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## Why AICL Exists

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

But there is a deeper problem. Modern compilers generate millions of lines of code without ever being able to answer a simple question: **why?** Why was this line generated? What architectural decision produced it? What risk does this recovery address? What validation does this test verify?

No mainstream compiler can answer these questions. The code exists, but the reasoning behind it is lost the moment compilation finishes.

AICL exists to change this.

## The Core Idea

AICL is an **Architecture Compilation System** — not just a language. It compiles architectural specifications into executable code where:

> **Risks, recoveries, and validations are mandatory syntactic elements, and every generated line carries full provenance.**

This means three things that no other system does together:

1. **Risk and Recovery are not optional.** You cannot write an AICL program without specifying what can fail and how to recover. The compiler enforces this the way other compilers enforce types.

2. **Validation compiles into tests.** Every `Validation:` section becomes executable test code — not a comment, not a wish, but a compiled test.

3. **Every line is explainable.** `aicl explain` tells you exactly why each line was generated, what pattern matched, what source it came from, and what confidence the compiler had. If the compiler cannot explain itself, it falls back to explicit sub-language syntax rather than guessing.

```aicl
Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries
```

This is not a comment. It is not a try/catch you might remember to write. It is a **first-class language construct** that the compiler transforms into executable recovery logic — and can later explain why it generated that specific clamping code.

## What Makes This Different

Several systems have tried "architecture to code." That is not the novelty here.

The novelty is **explicable compilation** — the principle that a compiler should never generate code it cannot justify:

| | Traditional Compilers | AI Code Generators | AICL |
|---|---|---|---|
| **Risks** | Optional try/catch | Not considered | Mandatory `Risk:` keyword |
| **Recovery** | Scattered error handlers | Not considered | Paired `Recovery:` per risk |
| **Validation** | Separate test files | Not generated | Compiled from `Validation:` sections |
| **Architecture** | Documentation only | Hallucinated | Executable `Layer:` definitions |
| **Provenance** | None | None | Full audit trail (`aicl explain`) |
| **Determinism** | Deterministic | Probabilistic | Deterministic by contract |
| **Explainability** | No | No | Every line traceable to source |

The key insight: **AICL does not use AI to write code.** AI is an optional plugin. The core compiler is 100% deterministic, using a library of 30+ behavior patterns. This is a deliberate design choice — you should never need to wonder whether your compiler made a creative decision.

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

The compiler generates:
- **`main.py`** — Complete Python application with error handling and recovery logic
- **`test_main.py`** — Test suite derived from `Validation:` sections
- **`architecture_tree.txt`** — Visual architecture representation

Then ask it why:

```bash
aicl explain examples/02_pong.aicl --behavior MovePaddle
```

The compiler will trace exactly which pattern matched, why, and with what confidence — because **every generated line must be explainable**.

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
aicl explain examples/02_pong.aicl --provenance             # Full provenance report
```

Every generated line of code has a provenance chain. The `aicl explain` command shows you exactly why the compiler generated each line, what pattern it matched, what AICL source it came from, and what confidence level it had.

### Run the tests

```bash
python -m pytest tests/ -v
```

---

## Examples

The `examples/` directory contains four programs of increasing complexity:

| Example | Levels Used | Description |
|---------|------------|-------------|
| [`01_blue_square.aicl`](examples/01_blue_square.aicl) | 1 | Simple graphics — display a blue square |
| [`02_pong.aicl`](examples/02_pong.aicl) | 1–6 | Pong game — entities, behaviors, conditions, events, parallelism |
| [`03_chat.aicl`](examples/03_chat.aicl) | 1–9 | Chat app — full feature set including security, learning, optimization |
| [`04_chess.aicl`](examples/04_chess.aicl) | 1–9 | Multiplayer chess — complex state, networking, adaptive graphics |

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
    │               │     + provenance per line
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Test         │  ──→ pytest suite from Validations
    │  Generation   │     + provenance linking
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Optimization │  ──→ Apply Optimize/Priority hints
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Final        │  ──→ main.py + test_main.py + tree
    │  Construction │     + explain report
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

### Compilation Provenance

Every compilation decision is tracked through the `ProvenanceType` enum:

| Type | Meaning |
|------|---------|
| `PATTERN_MATCH` | A behavior pattern matched with sufficient confidence |
| `SUB_LANGUAGE` | Explicit sub-language syntax was used |
| `FALLBACK` | No pattern matched; structured skeleton generated |
| `ARCHITECTURE_TEMPLATE` | Goal mapped to application structure |
| `DIRECT_MAPPING` | Keyword directly mapped to code |
| `RECOVERY_SYNTHESIS` | Recovery code synthesized from Risk/Recovery pair |
| `VALIDATION_SYNTHESIS` | Test code generated from Validation section |
| `CONDITION_SYNTHESIS` | Condition handler generated from When/Then |
| `EVENT_SYNTHESIS` | Event handler generated from On/Action |
| `ENTITY_GENERATION` | Dataclass generated from Entity definition |

The `aicl explain` command traverses this provenance chain and shows the full reasoning path for every generated line.

---

## Project Structure

```
AICL/
├── src/aicl/                    # Compiler source
│   ├── __init__.py              # Package exports (v0.4.0)
│   ├── cli.py                   # CLI: compile, parse, tree, check, explain
│   ├── parser.py                # Line-based parser → AST
│   ├── ast.py                   # 17 AST node dataclasses
│   ├── ir.py                    # Intermediate representation (Architecture Tree)
│   ├── compiler.py              # 9-stage compilation pipeline
│   ├── patterns.py              # 30+ deterministic behavior patterns
│   ├── provenance.py            # Compilation provenance tracker
│   └── lexer.py                 # Lexical analyzer (standalone)
├── examples/                    # Example programs
│   ├── 01_blue_square.aicl      # Level 1 — simple graphics
│   ├── 02_pong.aicl             # Levels 1–6 — game with behaviors
│   ├── 03_chat.aicl             # Levels 1–9 — full-featured app
│   └── 04_chess.aicl            # Levels 1–9 — complex state management
├── tests/                       # Test suite
│   └── test_aicl.py             # 63 tests (all passing)
├── spec/                        # Language specification
│   └── grammar.md               # Formal BNF grammar & keyword table
├── docs/                        # Documentation
│   └── whitepaper.pdf           # White paper
├── tools/                       # Build and utility scripts
│   └── generate_whitepaper.py   # White paper PDF generator
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

The white paper at [`docs/whitepaper.pdf`](docs/whitepaper.pdf) presents AICL as an Architecture Compilation System with **explicable compilation** as its central thesis:

- The provenance principle: a compiler that cannot explain why should not generate
- Formal BNF grammar with derivation rules
- Risk and Recovery as mandatory language elements
- Validation compiled automatically into tests
- Complete provenance of generation
- Deterministic compilation contract
- Strict separation between language and optional AI
- Comparative analysis against DSLs, ADLs, and AI code generators

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| **v0.1** | Parser, grammar, Python codegen, 38 tests | Done |
| **v0.2** | Deterministic patterns, zero-TODO compilation, provenance | Done |
| **v0.3** | Sub-language expansion, architecture templates | Done |
| **v0.4** | Explicable compilation thesis, provenance-first design, project reorganization | Current |
| **v0.5** | Architecture Tree IR improvements, multi-file programs, real dependency analysis | Planned |
| **v1.0** | Multi-language targets (Rust, JavaScript, Go), mature compiler | Future |
| **v2.0** | Self-healing runtime with automatic recovery execution | Future |
| **v3.0** | Autonomous architecture optimization, memory management system | Future |

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **New target languages** — Rust, TypeScript, Go code generation backends
- **New behavior patterns** — Expand the deterministic pattern library
- **Provenance visualization** — Tools to explore and visualize compilation provenance
- **IDE support** — Syntax highlighting, LSP server, VS Code extension
- **New examples** — Real-world programs showcasing different levels
- **Formal verification** — Proof that Risk/Recovery pairs are complete
- **Memory management** — Ultra-simple but effective ownership model

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Philippe-Antoine**

---

<div align="center">

*"If the compiler cannot explain why it generated a line of code, it should not generate it."*

</div>
