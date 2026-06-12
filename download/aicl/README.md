<div align="center">

# AICL

**AI-Centric Language**

*Architecture is the program. Risks are syntax. Validations compile.*

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Install](#install) · [Quick Start](#quick-start) · [Examples](#examples) · [Language Reference](#language-levels) · [Grammar](spec/grammar.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## The Problem

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

The gap between what we *intend* to build and what we *actually* build is where most production failures live. Architecture documents describe risk scenarios and recovery strategies, but nothing enforces their implementation. Code reviews miss edge cases. Tests skip failure paths. The result: systems that work on the happy path and crumble on every other one.

## The Idea

AICL is a **specification-first programming language** where you describe *what* a system must achieve — not *how*. The core insight:

> **Risks, recoveries, and validations are not documentation — they are mandatory syntactic elements of the language.**

You cannot write an AICL program without specifying what can fail and how to recover. The compiler enforces this the way other compilers enforce types. This isn't a linting rule you can suppress or a best practice you can skip — it's a compile-time requirement built into the grammar itself.

```aicl
Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries
```

This isn't a comment. It's not a try/catch you might remember to write. It's a **first-class language construct** that the compiler transforms into executable recovery logic. Every Risk must have a paired Recovery. Every Validation must be testable. Every Layer must be accounted for in the generated architecture.

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

---

## How It's Different

| | Traditional Code | AICL |
|---|---|---|
| **Risks** | Optional try/catch, if you remember | Mandatory `Risk:` keyword |
| **Recovery** | Scattered error handlers | Paired `Recovery:` per risk |
| **Validation** | Separate test files, best effort | Compiled from `Validation:` sections |
| **Architecture** | Documentation / diagrams | Executable `Layer:` definitions |
| **Behavior** | Free-form function bodies | Deterministic pattern compilation |
| **Compiler** | Translates syntax | Reasons about architecture |
| **Provenance** | None | Every generated line is traceable (`aicl explain`) |

This is not "natural language programming." AICL has a **strict, deterministic grammar** with 27 reserved keywords and a formal BNF specification. The compiler uses a library of 30+ behavior patterns to generate concrete, deterministic code — no AI guessing required. AI-assisted code filling (`--ai-fill`) is a separate, optional mode.

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
```

Every generated line of code has a provenance chain. The `aicl explain` command shows you exactly why the compiler generated each line, what pattern it matched, and what AICL source it came from.

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

The AICL compiler doesn't just translate — it **reasons** about your architecture through a 9-stage pipeline:

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
    │  Synthesis    │
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Code         │  ──→ Python source + error handling
    │  Generation   │     (30+ deterministic behavior patterns)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Test         │  ──→ pytest suite from Validations
    │  Generation   │
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Optimization │  ──→ Apply Optimize/Priority hints
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Final        │  ──→ main.py + test_main.py + tree
    │  Construction │
    └──────────────┘
```

### Deterministic Behavior Compilation

The key innovation in v0.3 is the **Behavior Pattern Library** — a set of 30+ deterministic patterns that map action descriptions to concrete code:

| Category | Patterns | Example |
|----------|----------|---------|
| Movement | MOVE, BOUNCE, ORBIT | "Update paddle position" → MOVE pattern |
| Creation | CREATE, INITIALIZE, SPAWN | "Create new game" → CREATE pattern |
| Update | UPDATE, ASSIGN, CLAMP | "Clamp ball position" → CLAMP pattern |
| Communication | BROADCAST, SEND, RECEIVE | "Transmit message" → BROADCAST pattern |
| Validation | VALIDATE, CHECK, VERIFY | "Validate move" → VALIDATE pattern |
| Transform | TRANSFORM, CONVERT, PARSE | "Parse input" → TRANSFORM pattern |
| Storage | STORE, LOAD, PERSIST | "Save game state" → STORE pattern |
| Security | ENCRYPT, HASH, PROTECT | "Encrypt message" → ENCRYPT pattern |

When no pattern matches, the **sub-language parser** handles explicit action specifications:

```aicl
Behavior MovePaddle
    Input: Player direction string
    Action: assign paddle_position += direction * speed
            clamp paddle_position between 0 and screen_width
```

This means **zero TODOs** in compiled output. Every behavior compiles to real, executable code.

---

## Project Structure

```
AICL/
├── src/aicl/                    # Compiler source
│   ├── __init__.py              # Package exports (v0.3.0)
│   ├── cli.py                   # CLI: compile, parse, tree, check, explain
│   ├── parser.py                # Line-based parser → AST
│   ├── ast_nodes.py             # 17 AST node dataclasses
│   ├── architecture_tree.py     # Intermediate representation (IR)
│   ├── compiler.py              # 9-stage compilation pipeline
│   ├── patterns.py              # 30+ deterministic behavior patterns
│   ├── provenance.py            # Compilation provenance tracker
│   └── tokenizer.py             # Lexical analyzer (standalone)
├── examples/                    # Example programs
│   ├── 01_blue_square.aicl      # Level 1 — simple graphics
│   ├── 02_pong.aicl             # Levels 1–6 — game with behaviors
│   ├── 03_chat.aicl             # Levels 1–9 — full-featured app
│   └── 04_chess.aicl            # Levels 1–9 — complex state management
├── tests/                       # Test suite
│   └── test_aicl.py             # 38 tests (all passing)
├── spec/                        # Language specification
│   └── grammar.md               # Formal BNF grammar & keyword table
├── docs/                        # Documentation
│   └── whitepaper.pdf           # Academic white paper
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

A comprehensive white paper is available at [`docs/whitepaper.pdf`](docs/whitepaper.pdf), covering:

- Formal operational semantics
- Full BNF grammar with derivation rules
- Comparative analysis against DSLs, architecture description languages, and AI code generation tools
- The Architecture Tree intermediate representation
- Deterministic behavior pattern compilation
- Compilation provenance and explainability
- All 10 language levels with examples

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| **v0.1** | Parser, grammar, Python codegen, 38 tests | Done |
| **v0.2** | Deterministic patterns, zero-TODO compilation, provenance | Done |
| **v0.3** | Reorganized project, new white paper, sub-language expansion | Current |
| **v0.5** | Architecture Tree IR improvements, multi-file programs | Planned |
| **v1.0** | Multi-language targets (Rust, JavaScript, Go), mature compiler | Future |
| **v2.0** | Self-healing runtime with automatic recovery execution | Future |
| **v3.0** | Autonomous architecture optimization | Future |

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **New target languages** — Rust, TypeScript, Go code generation backends
- **New behavior patterns** — Expand the deterministic pattern library
- **IDE support** — Syntax highlighting, LSP server, VS Code extension
- **New examples** — Real-world programs showcasing different levels
- **Formal verification** — Proof that Risk/Recovery pairs are complete

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Philippe-Antoine**

---

<div align="center">

*"The architecture is no longer documentation. The architecture is the program."*

</div>
