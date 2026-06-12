<div align="center">

# AICL

**AI-Centric Language**

*Architecture is the program. Risks are syntax. Validations compile.*

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Getting Started](#getting-started) · [Examples](#examples) · [Language Reference](#language-levels) · [Specification](spec/SPECIFICATION.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## The Problem

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

## The Idea

AICL is a **specification-first programming language** where you describe *what* a system must achieve — not *how*. The key insight:

> **Risks, recoveries, and validations are not documentation — they are mandatory syntactic elements of the language.**

You cannot write an AICL program without specifying what can fail and how to recover. The compiler enforces this the way other compilers enforce types.

```aicl
Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries
```

This isn't a comment. It's not a try/catch you might remember to write. It's a **first-class language construct** that the compiler transforms into executable recovery logic.

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
aicl compile pong.aicl --output-dir ./output
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
| **AI role** | Copilot autocomplete | Compiler reasons about architecture |

This is not "natural language programming." AICL has a **strict, deterministic grammar** with 27 reserved keywords. AI fills in implementation details, but the architectural intent is always explicit and machine-verifiable.

---

## Getting Started

### Install

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL
pip install -e .
```

### Compile an AICL program

```bash
aicl compile examples/pong.aicl --output-dir ./output
```

### Inspect the architecture

```bash
aicl tree examples/chess.aicl       # Visualize the architecture tree
aicl parse examples/chat.aicl       # Dump the AST
aicl check examples/blue_square.aicl # Validate without compiling
```

### Run the tests

```bash
python -m pytest tests/ -v
```

---

## Examples

The `examples/` directory contains four programs of increasing complexity:

| Example | Levels Used | Description |
|---------|------------|-------------|
| [`blue_square.aicl`](examples/blue_square.aicl) | 1 | Simple graphics — display a blue square |
| [`pong.aicl`](examples/pong.aicl) | 1–6 | Pong game — entities, behaviors, conditions, events, parallelism |
| [`chat.aicl`](examples/chat.aicl) | 1–9 | Chat app — full feature set including security, learning, optimization |
| [`chess.aicl`](examples/chess.aicl) | 1–9 | Multiplayer chess — complex state, networking, adaptive graphics |

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
    │  Parse  │  ──→ AST
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
    │  Generation   │
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

---

## Project Structure

```
AICL/
├── src/aicl/
│   ├── __init__.py            # Package exports
│   ├── parser.py              # Line-based parser (no tokenizer)
│   ├── ast_nodes.py           # 17 AST node dataclasses
│   ├── architecture_tree.py   # Intermediate representation (IR)
│   ├── compiler.py            # 9-stage compilation pipeline
│   └── cli.py                 # CLI: compile, parse, tree, check
├── examples/
│   ├── blue_square.aicl       # Level 1 — simple graphics
│   ├── pong.aicl              # Levels 1–6 — game with behaviors
│   ├── chat.aicl              # Levels 1–9 — full-featured app
│   └── chess.aicl             # Levels 1–9 — complex state management
├── tests/
│   └── test_aicl.py           # 38 tests (all passing)
├── spec/
│   └── SPECIFICATION.md       # Formal BNF grammar & keyword table
├── docs/
│   └── whitepaper.pdf         # 49-page academic white paper
└── README.md
```

---

## Formal Specification

The complete language specification is in [`spec/SPECIFICATION.md`](spec/SPECIFICATION.md), including:

- Full BNF grammar for all 10 language levels
- 27 reserved keywords with level and purpose
- Type system (`string`, `integer`, `float`, `boolean`, `datetime`, `list`, `dict`, `set`, `any`, `void`, `bytes`)
- Comment syntax (lines starting with `#`)
- File extension (`.aicl`)

---

## White Paper

A 49-page academic white paper is available at [`docs/whitepaper.pdf`](docs/whitepaper.pdf), covering:

- Formal operational semantics
- Full BNF grammar with derivation rules
- Comparative analysis against DSLs, architecture description languages, and AI code generation tools
- The Architecture Tree intermediate representation
- Detailed compilation pipeline semantics
- All 10 language levels with examples

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| **v0.1** | Parser, grammar, Python codegen, 38 tests | ✅ Done |
| **v0.5** | Architecture Tree IR improvements, AI-assisted compilation | 🔜 Planned |
| **v1.0** | Multi-language targets (Rust, JavaScript), mature compiler | 🔮 Future |
| **v2.0** | Self-healing runtime with automatic recovery execution | 🔮 Future |
| **v3.0** | Autonomous architecture optimization | 🔮 Future |

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **New target languages** — Rust, TypeScript, Go code generation backends
- **AI-assisted compilation** — Connect LLMs to fill in `TODO` placeholders in generated code
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
