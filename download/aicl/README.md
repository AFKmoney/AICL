# AICL - AI-Centric Language

<p align="center">
  <strong>Architecture-Driven, AI-Native Software Development</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/status-alpha-orange" alt="Status">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="License">
</p>

---

## What is AICL?

AICL (AI-Centric Language) is a **specification-first programming language** where you describe **what** a system should achieve, not **how** it should implement it. Instead of writing code directly, you specify:

- **Goals** — What the system must accomplish
- **Risks** — What can go wrong
- **Recoveries** — How to handle failures
- **Layers** — How the system is organized
- **Validations** — How to measure success

The AICL compiler transforms your architectural specification into executable code.

## The Key Insight

> **Risks, recoveries, and validations are not documentation — they are mandatory syntactic elements of the language.**

This is what distinguishes AICL from a simple "natural language compiled by AI." The grammar is strict and deterministic, while AI fills in implementation details.

## Quick Example

```aicl
Goal:
Build a Pong game

Constraint:
60 FPS minimum

Risk:
Ball leaves play area

Recovery:
Clamp ball position

Layer:
Window Manager

Layer:
Game Logic

Layer:
Rendering System

Entity Player
    name: string
    score: integer

Entity Ball
    x: float
    y: float

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
- `main.py` — Complete Python application with error handling
- `test_main.py` — Test suite from validation specifications
- `architecture_tree.txt` — Visual architecture representation

## Installation

```bash
git clone https://github.com/username/aicl.git
cd aicl
pip install -e .
```

## Usage

### Compile
```bash
aicl compile source.aicl --output-dir ./output
```

### Parse & Inspect
```bash
aicl parse source.aicl    # Show AST
aicl tree source.aicl     # Show Architecture Tree
aicl check source.aicl    # Check for errors
```

### Version
```bash
aicl version
```

## Language Levels

AICL is organized in 10 progressive levels:

| Level | Feature | Keywords |
|-------|---------|----------|
| 1 | Architecture | Goal, Constraint, Risk, Recovery, Layer, Validation |
| 2 | Entities | Entity, fields |
| 3 | Behaviors | Behavior, Input, Output, Action |
| 4 | Conditions | Condition, When, Then |
| 5 | Events | Event, On, Action |
| 6 | Concurrency | Parallel |
| 7 | Optimization | Optimize, Priority |
| 8 | Learning | Learn, Adapt, Based |
| 9 | Security | Security, Encrypt, Protect |
| 10 | Native Code | Native |

## Compilation Pipeline

```
Source → Parse → Validate → Analyze → Generate → Optimize → Output
         ↓         ↓          ↓          ↓
         AST    Warnings   Dep Tree   Python Code
                                         + Tests
```

9 compilation stages:
1. Specification Parsing
2. Architecture Validation
3. Dependency Analysis
4. Risk Analysis
5. Recovery Synthesis
6. Code Generation
7. Test Generation
8. Optimization
9. Final Construction

## Project Structure

```
aicl/
├── src/
│   └── aicl/
│       ├── __init__.py        # Package exports
│       ├── parser.py          # Line-based parser
│       ├── ast_nodes.py       # AST node definitions
│       ├── architecture_tree.py # Intermediate representation
│       ├── compiler.py        # Multi-stage compiler
│       └── cli.py             # Command-line interface
├── examples/
│   ├── blue_square.aicl       # Simple graphics example
│   ├── pong.aicl              # Pong game
│   ├── chat.aicl              # Chat application
│   └── chess.aicl             # Multiplayer chess
├── tests/
│   └── test_aicl.py           # Comprehensive test suite
├── spec/
│   └── SPECIFICATION.md       # Language specification
├── docs/
│   └── whitepaper.pdf         # Technical white paper
└── README.md
```

## Running Tests

```bash
cd aicl
python -m pytest tests/ -v
```

## Roadmap

- **v0.1** — Parser, grammar, Python backend ✅
- **v0.5** — Architecture Tree IR, automatic test generation
- **v1.0** — Multi-language targets, AI-assisted compiler
- **v2.0** — Self-healing runtime
- **v3.0** — Autonomous architecture optimization

## License

MIT License

## Author

Philippe-Antoine

---

*"The architecture is no longer documentation. The architecture is the program."*
