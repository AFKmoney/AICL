<div align="center">

# AICL

**Architecture Compilation Language**

*If the compiler cannot explain why it generated a line, it should not generate it.*

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-76%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Audit](https://img.shields.io/badge/audit%20coverage-100%25-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Install](#install) · [Quick Start](#quick-start) · [Examples](#examples) · [Audit System](#audit-system) · [Language Reference](#language-levels) · [Grammar](spec/grammar.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## Why AICL Exists

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

But there is a deeper problem. Modern compilers generate millions of lines of code without ever being able to answer a simple question: **why?** Why was this line generated? What architectural decision produced it? What risk does this recovery address? What validation does this test verify?

No mainstream compiler can answer these questions. The code exists, but the reasoning behind it is lost the moment compilation finishes.

AICL exists to change this — and to make that change **measurable**.

## The Core Idea

AICL is an **Architecture Compilation System** — not just a language. It compiles architectural specifications into executable code where:

> **Risks, recoveries, and validations are mandatory syntactic elements, every generated artifact carries full provenance, and audit coverage is a measurable property.**

This means four things that no other system does together:

1. **Risk and Recovery are not optional.** You cannot write an AICL program without specifying what can fail and how to recover. The compiler enforces this the way other compilers enforce types.

2. **Validation compiles into tests.** Every `Validation:` section becomes executable test code — not a comment, not a wish, but a compiled test.

3. **Every artifact is explainable.** `aicl explain` tells you exactly why each method was generated, what pattern matched, what source it came from, and what confidence the compiler had.

4. **Audit coverage is measurable.** `aicl audit` verifies that every generated artifact — every class, method, function, and test — has provenance. If an artifact has no provenance, it's an **orphan**. The target is always: **Audit Coverage = 100%**.

```aicl
Risk:
    Ball leaves play area

Recovery:
    Clamp ball position to boundaries
```

This is not a comment. It is not a try/catch you might remember to write. It is a **first-class language construct** that the compiler transforms into executable recovery logic — and can later audit to verify it has complete provenance.

## What Makes This Different

Several systems have tried "architecture to code." That is not the novelty here.

The novelty is **auditable compilation** — the principle that a compiler should never generate code it cannot justify, and that this property should be **measurable**:

| | Traditional Compilers | AI Code Generators | AICL |
|---|---|---|---|
| **Risks** | Optional try/catch | Not considered | Mandatory `Risk:` keyword |
| **Recovery** | Scattered error handlers | Not considered | Paired `Recovery:` per risk |
| **Validation** | Separate test files | Not generated | Compiled from `Validation:` sections |
| **Architecture** | Documentation only | Hallucinated | Executable `Layer:` definitions |
| **Provenance** | None | None | Full audit trail (`aicl explain`) |
| **Audit** | None | None | Measurable coverage (`aicl audit`) |
| **Determinism** | Deterministic | Probabilistic | Deterministic by contract |
| **Explainability** | No | No | Every artifact traceable to source |

The key insight: **AICL does not use AI to write code.** AI is an optional plugin. The core compiler is 100% deterministic, using a library of 30+ behavior patterns. This is a deliberate design choice — you should never need to wonder whether your compiler made a creative decision.

**Traditional compilers generate code. AICL generates code and its justification.**

---

## Audit System

The audit system is AICL's most original contribution. It introduces three concepts that no other compiler offers:

### Auditability

> A program is **auditable** if every generated artifact can be traced to its originating specification through a complete provenance chain.

### Audit Coverage

> **Audit Coverage = Auditable Artifacts / Generated Artifacts**
>
> Target: **Audit Coverage = 1.0** (100%)

### Orphan Artifacts

> An **orphan artifact** is a generated artifact (method, class, function, test) without provenance. It exists in the code, but the compiler cannot explain why.

### Using the Audit System

```bash
# Full audit report
aicl audit examples/02_pong.aicl

# Strict mode: fail if coverage < 100%
aicl audit examples/02_pong.aicl --strict
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
  dataclass        2/  2  100.00%  [VERIFIED]
  class            1/  1  100.00%  [VERIFIED]
  function         1/  1  100.00%  [VERIFIED]
  import_block     1/  1  100.00%  [VERIFIED]

======================================================================
AUDIT RESULT: PASSED
  Every generated artifact has provenance.
  Compilation is fully auditable.
======================================================================
```

### Explain vs. Audit

Two separate commands serve different purposes:

- **`aicl explain`** answers: *"Why was this specific artifact generated?"* (micro-level traceability)
- **`aicl audit`** answers: *"Is the entire compilation traceable?"* (macro-level verification)

You can think of it as:
- `explain` = debugging a single behavior
- `audit` = certifying the entire compilation

### Compilation Output

When you compile, the output now includes audit information:

```bash
aicl compile examples/02_pong.aicl

# Output:
Compilation successful
  Stages completed: Specification Parsing, Architecture Validation, ...
  TODOs remaining: 0
  Fully compiled: Yes
  Audit coverage: 100.0% (52/52 artifacts)
```

A traditional compiler says: `Compilation successful`.

AICL says: `Compilation successful. Audit coverage: 100%. Orphan artifacts: 0. Audit status: VERIFIED.`

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

Then audit it:

```bash
aicl audit examples/02_pong.aicl
```

Verify that every generated artifact has provenance — because **if you can't audit it, you can't trust it**.

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

### Audit the compilation

```bash
aicl audit examples/02_pong.aicl               # Full audit report
aicl audit examples/02_pong.aicl --strict       # Fail if coverage < 100%
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
```

Every generated artifact has a provenance chain. The `aicl explain` command shows you exactly why the compiler generated each method, what pattern it matched, what AICL source it came from, and what confidence level it had.

### Run the tests

```bash
python -m pytest tests/ -v
```

---

## Examples

The `examples/` directory contains four programs of increasing complexity — all achieving **100% audit coverage**:

| Example | Levels Used | Artifacts | Audit Coverage |
|---------|------------|-----------|----------------|
| [`01_blue_square.aicl`](examples/01_blue_square.aicl) | 1 | 35 | 100% |
| [`02_pong.aicl`](examples/02_pong.aicl) | 1–6 | 52 | 100% |
| [`03_chat.aicl`](examples/03_chat.aicl) | 1–9 | 58 | 100% |
| [`04_chess.aicl`](examples/04_chess.aicl) | 1–9 | 59 | 100% |

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
    │  Construction │     + audit report
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

Every compilation decision is tracked through the `ProvenanceType` enum (19 types):

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
| `LAYER_INITIALIZATION` | Layer initialization method generated |
| `HELPER_METHOD` | Helper method generated from template requirements |
| `SECURITY_METHOD` | Security enforcement method generated |
| `PARALLEL_EXECUTION` | Parallel execution code generated |
| `RUN_METHOD` | Main run method generated from architecture template |
| `IMPORT_GENERATION` | Import statements generated from program analysis |
| `ENTRY_POINT` | Main entry point function generated |
| `TEST_GENERATION` | Test functions generated from specifications |
| `CLASS_STRUCTURE` | Class structure (attributes, constructor) generated |

### Artifact Tracking

Every generated code unit is registered as an **artifact** with one of these types:

| ArtifactType | Description | Examples |
|---|---|---|
| `class` | Main application class | `PongGame` |
| `dataclass` | Entity dataclasses | `Player`, `Ball` |
| `method` | Instance methods | `_behavior_move_paddle`, `_validate_1`, `__init__` |
| `function` | Module-level functions | `main()` |
| `test_function` | Test functions | `test_validation_1`, `test_risk_handling_1` |
| `import_block` | Import section | All import statements |

The audit system verifies that every registered artifact has at least one provenance record explaining why it was generated.

---

## Project Structure

```
AICL/
├── src/aicl/                    # Compiler source
│   ├── __init__.py              # Package exports (v0.5.0)
│   ├── cli.py                   # CLI: compile, parse, tree, check, explain, audit
│   ├── parser.py                # Line-based parser → AST
│   ├── ast.py                   # 17 AST node dataclasses
│   ├── ir.py                    # Intermediate representation (Architecture Tree)
│   ├── compiler.py              # 9-stage compilation pipeline + artifact tracking
│   ├── patterns.py              # 30+ deterministic behavior patterns
│   ├── provenance.py            # Provenance tracker + audit system
│   └── lexer.py                 # Lexical analyzer (standalone)
├── examples/                    # Example programs
│   ├── 01_blue_square.aicl      # Level 1 — simple graphics (35 artifacts, 100% audit)
│   ├── 02_pong.aicl             # Levels 1–6 — game with behaviors (52 artifacts, 100% audit)
│   ├── 03_chat.aicl             # Levels 1–9 — full-featured app (58 artifacts, 100% audit)
│   └── 04_chess.aicl            # Levels 1–9 — complex state (59 artifacts, 100% audit)
├── tests/                       # Test suite
│   └── test_aicl.py             # 76 tests (all passing, including audit tests)
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
| **v0.4** | Explicable compilation thesis, provenance-first design, project reorganization | Done |
| **v0.5** | Audit system, artifact tracking, 100% audit coverage, orphan detection, `aicl audit` | **Current** |
| **v0.6** | Formal verification of audit coverage, external audit format, provenance visualization | Planned |
| **v1.0** | Multi-language targets (Rust, JavaScript, Go), mature compiler | Future |
| **v2.0** | Self-healing runtime with automatic recovery execution | Future |
| **v3.0** | Autonomous architecture optimization, memory management system | Future |

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **New target languages** — Rust, TypeScript, Go code generation backends
- **New behavior patterns** — Expand the deterministic pattern library
- **Provenance visualization** — Tools to explore and visualize compilation provenance
- **External audit format** — Standardized provenance reports for third-party verification
- **IDE support** — Syntax highlighting, LSP server, VS Code extension
- **New examples** — Real-world programs showcasing different levels
- **Formal verification** — Proof that no orphan artifacts can exist (Orphan Artifact Theorem)
- **Memory management** — Ultra-simple but effective ownership model

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Philippe-Antoine**

---

<div align="center">

*"Traditional compilers generate code. AICL generates code and its justification."*

</div>
