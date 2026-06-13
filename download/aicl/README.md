<div align="center">

# AICL

**Architecture Compilation Language**

*If the compiler cannot explain why it generated a line, it should not generate it.*
*And this property must be independently verifiable without trusting the compiler.*

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/AFKmoney/AICL)
[![Status](https://img.shields.io/badge/status-beta-green.svg)](https://github.com/AFKmoney/AICL)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-129%20passing-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Audit](https://img.shields.io/badge/audit%20coverage-100%25-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Proof](https://img.shields.io/badge/proof%20of%20origin-verifiable-brightgreen.svg)](https://github.com/AFKmoney/AICL)
[![Targets](https://img.shields.io/badge/targets-Python%20%7C%20Rust%20%7C%20JS%20%7C%20Go-blue.svg)](https://github.com/AFKmoney/AICL)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](https://github.com/AFKmoney/AICL/blob/main/LICENSE)

[Install](#install) · [Quick Start](#quick-start) · [Proof of Origin](#proof-of-origin) · [Audit System](#audit-system) · [Multi-Language](#multi-language-targets) · [Language Reference](#language-levels) · [Grammar](spec/grammar.md) · [White Paper](docs/whitepaper.pdf)

</div>

---

## Why AICL Exists

Every production system needs error handling, failure recovery, and validation. Yet in every mainstream language, these are **optional afterthoughts** — scattered across try/catch blocks, buried in documentation, or forgotten entirely.

**3:00 AM pages happen because risks were documented in Confluence, not compiled into code.**

AICL makes risk and recovery **mandatory language elements**. Every Risk must have a Recovery. Every Validation must generate a test. Every generated line must have a traceable provenance chain. And every compilation produces a **Proof of Origin** that can be independently verified without trusting the compiler.

---

## Core Idea

AICL is built on five key properties:

1. **Mandatory Risk/Recovery** — Every `Risk` must have a `Recovery`. Error handling is not optional.
2. **Validation → Tests** — Every `Validation` section generates a test. Test coverage is structural.
3. **Explainable Artifacts** — Every generated line of code has a traceable provenance chain.
4. **Measurable Audit Coverage** — Audit coverage = auditable artifacts / total artifacts. Target: 100%.
5. **Independently Verifiable Proofs** — Proof of Origin files can be verified without the compiler.

---

## Proof of Origin

The **Proof of Origin** (`.aicl-proof`) is the central artifact of AICL compilation. It is a self-contained, cryptographically bound file that proves every generated artifact has traceable provenance.

```
AICL Source → Compiler → Proof of Origin
                         ├─ Code (Python, Rust, JS, Go)
                         ├─ Explain (provenance chains)
                         └─ Audit (coverage verification)
```

### Architecture Shift

In v0.7+, the **Proof of Origin** became the central artifact. Code, explanation, and audit are views on the proof:

- **aicl compile** → produces code AND proof
- **aicl explain --proof** → reads from proof (no compiler needed)
- **aicl audit --proof** → reads from proof (no compiler needed)
- **aicl proof --verify** → verifies proof integrity

### Independent Verification

The independent verifier (`tools/verify_proof.py`) is ~200 lines of Python using **only the standard library** — zero AICL dependencies. It performs 8 verification checks:

| # | Check | What it verifies |
|---|-------|-----------------|
| 1 | `format_version` | Proof format is supported |
| 2 | `source_hash_binding` | SHA-256(source_text) == source_hash |
| 3 | `program_hash_binding` | SHA-256(generated_source) == program_hash |
| 4 | `test_hash_binding` | SHA-256(generated_tests) == test_hash |
| 5 | `no_orphan_artifact_property` | Every artifact has a provenance chain |
| 6 | `complete_coverage_property` | Audit coverage = 1.0 |
| 7 | `record_artifact_linkage` | Provenance records reference valid artifacts |
| 8 | `artifact_consistency` | Orphan status matches provenance linkage |

```bash
python tools/verify_proof.py output/main.aicl-proof
# → VALID (exit 0) or INVALID (exit 1)
```

This eliminates the **"Trust me bro" problem**: AICL says AICL is correct. The independent verifier says the proof is valid — without using AICL.

### Proof Format v2.0

The proof file is self-contained JSON:

```json
{
  "format_version": "2.0",
  "compiler_version": "1.0.0",
  "timestamp": "2026-06-13T12:00:00Z",
  "source_hash": "sha256:...",
  "program_hash": "sha256:...",
  "test_hash": "sha256:...",
  "source_text": "Goal ...",
  "generated_source": "class Application ...",
  "generated_tests": "def test_ ...",
  "records": [...],
  "artifacts": [...],
  "formal_properties": {...},
  "audit_coverage": {...},
  "explicability_coverage": {...}
}
```

### Cryptographic Proof Signing (v0.11)

Proof files can be cryptographically signed with the compiler's key:

```python
from aicl.crypto_signing import create_signed_proof, verify_signed_proof

signed = create_signed_proof(proof_dict, key_seed="compiler-key")
result = verify_signed_proof(signed)
# result["signature_present"] == True
# result["proof_hash_valid"] == True
```

Cross-compilation proof chains link successive compilations, creating an auditable history.

---

## Audit System

### What is Auditability?

A program is **auditable** if every generated artifact can be traced to its originating specification through a complete provenance chain:

```
Audit Coverage = Auditable Artifacts / Generated Artifacts
Target: Audit Coverage = 1.0
```

### Three Formal Properties

1. **The No-Orphan Property**: Every generated artifact has at least one provenance record.
2. **The Complete Coverage Property**: Audit coverage equals 1.0 (100%).
3. **The Hash Binding Property**: SHA-256 hashes bind the proof to the generated code.

These properties are **verifiable properties of the compilation artifact**, not just features of the compiler. An independent verifier can check them without using AICL.

---

## Multi-Language Targets

AICL v1.0 supports **four target languages**:

| Target | Status | Features |
|--------|--------|----------|
| **Python** | Mature (default) | Full provenance, pytest tests, dataclasses |
| **Rust** | Beta | Structs, Result error types, Cargo.toml, #[test] |
| **JavaScript** | Beta | ES6 classes, Jest tests, package.json, async/await |
| **Go** | Beta | Structs, error types, go.mod, table-driven tests |

```bash
aicl compile pong.aicl --target rust
aicl compile pong.aicl --target javascript
aicl compile pong.aicl --target go
```

Each target generator produces idiomatic code with:
- Error handling from Risk/Recovery pairs
- Entity structures as language-appropriate types
- Behavior methods with deterministic patterns
- Test suites from Validation sections
- Project configuration files (Cargo.toml, package.json, go.mod)

---

## Specification Verification (v0.9)

The `aicl verify` command checks specifications at three levels:

1. **Completeness**: All required elements present (Goal, Layer, Validation)
2. **Coherence**: No contradictions or dangling references
3. **Satisfaction**: Specification is implementable and testable

```bash
aicl verify pong.aicl                    # All three checks
aicl verify pong.aicl --completeness     # Completeness only
aicl verify pong.aicl --coherence        # Coherence only
aicl verify pong.aicl --satisfaction     # Satisfaction only
```

---

## Self-Healing Runtime (v2.0)

AICL's self-healing runtime extends compile-time provenance into execution:

- **Risk monitoring**: Runtime checks detect when risks materialize
- **Automatic recovery**: Recovery actions execute with retry and backoff
- **Runtime provenance**: Every event is recorded in a provenance chain

```python
from aicl.runtime import RuntimeEnvironment

env = RuntimeEnvironment()
env.register_risk_recovery(
    "network_failure",
    risk_condition=lambda: not check_network(),
    recovery_action=lambda: reconnect(),
)
result = env.run(application_main)
```

---

## Install

```bash
pip install aicl
```

Or from source:

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL
pip install -e .
```

---

## Quick Start

### 1. Write an AICL program

```aicl
Goal Build a simple Pong game

Layer Game
    SubLayer Rendering
    SubLayer Physics

Entity Ball
    x: float
    y: float
    dx: float
    dy: float

Entity Paddle
    x: float
    y: float

Behavior MoveBall
    Input: Ball ball
    Action: Update ball position by velocity

Behavior MovePaddle
    Input: Player direction string
    Action: Update paddle position

Validation Ball bounces off walls
    Ball velocity reverses on boundary contact

Validation Paddle stays in bounds
    Paddle position clamped to screen width

Risk Ball goes off screen
    Recovery Clamp ball position to screen bounds

Risk Paddle moves too fast
    Recovery Clamp paddle speed to maximum
```

### 2. Compile with proof

```bash
aicl compile pong.aicl --output-dir output
```

Output:
```
Compilation successful
  Output directory: output
  Main file: output/main.py
  Test file: output/test_main.py
  Architecture tree: output/architecture_tree.txt
  Proof of Origin: output/main.aicl-proof
  TODOs remaining: 0
  Fully compiled: Yes
  Audit coverage: 100.0%
  Proof of Origin: VALID
```

### 3. Verify independently

```bash
python tools/verify_proof.py output/main.aicl-proof
# → VALID
```

### 4. Explore the proof

```bash
aicl explain --proof output/main.aicl-proof
aicl audit --proof output/main.aicl-proof
aicl proof output/main.aicl-proof --verify
```

### 5. Compile to other languages

```bash
aicl compile pong.aicl --target rust --output-dir rust_output
aicl compile pong.aicl --target javascript --output-dir js_output
aicl compile pong.aicl --target go --output-dir go_output
```

---

## Language Levels

AICL has 10 progressive levels, each adding a new architectural dimension:

| Level | Name | Keywords | Purpose |
|-------|------|----------|---------|
| 1 | Architecture | `Goal`, `Layer`, `Validation`, `Risk`, `Recovery` | System structure + risk management |
| 2 | Entities | `Entity`, `field: type` | Data structures |
| 3 | Behaviors | `Behavior`, `Input`, `Output`, `Action` | What entities do |
| 4 | Conditions | `When`, `Then` | Replace if/else with declarative rules |
| 5 | Events | `On`, `Do` | Event-driven architecture |
| 6 | Concurrency | `Parallel` | Concurrent layer execution |
| 7 | Optimization | `Optimize`, `Priority` | Performance targets |
| 8 | Learning | `Learn`, `Adapt` | Adaptive behavior |
| 9 | Security | `Encrypt`, `Protect` | Security requirements |
| 10 | Native Code | `Native` | Inline code in other languages |

27 reserved keywords across all levels.

---

## Compilation Pipeline

```
    ┌───────────────┐
    │  AICL Source   │
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Specification │  ──→ Parser → AST
    │  Parsing       │
    └────┬──────────┘
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
    │  Code         │  ──→ Target language source + error handling
    │  Generation   │     (30+ deterministic patterns)
    │               │     + artifact registration
    │               │     + provenance per artifact
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  Test         │  ──→ Test suite from Validations
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
    │               │     + cryptographic signature
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
│   ├── __init__.py              # Package exports (v1.0.0)
│   ├── cli.py                   # CLI: compile, parse, tree, check, explain, audit, proof, verify, optimize
│   ├── parser.py                # Line-based parser → AST
│   ├── ast.py                   # 17 AST node dataclasses
│   ├── ir.py                    # Intermediate representation (Architecture Tree)
│   ├── compiler.py              # 9-stage compilation pipeline + artifact tracking
│   ├── patterns.py              # 30+ deterministic behavior patterns
│   ├── provenance.py            # Provenance tracker + audit + Proof of Origin
│   ├── lexer.py                 # Lexical analyzer (standalone)
│   ├── spec_verify.py           # Specification verification (completeness, coherence, satisfaction)
│   ├── modules.py               # Multi-file module system + cross-file provenance
│   ├── crypto_signing.py        # Cryptographic proof signing + proof chains
│   ├── runtime.py               # Self-healing runtime with automatic recovery
│   ├── ownership.py             # Memory management: ownership model from Layer/Entity
│   ├── auto_optimizer.py        # Autonomous architecture optimization
│   └── targets/                 # Multi-language target generators
│       ├── __init__.py          # Target registry
│       ├── base.py              # Base class for target generators
│       ├── rust.py              # Rust target (structs, Result, Cargo.toml)
│       ├── javascript.py        # JavaScript target (ES6, Jest, package.json)
│       └── go.py                # Go target (structs, go.mod)
├── examples/                    # Example programs
│   ├── 01_blue_square.aicl      # Level 1 — simple graphics (35 artifacts, 100% audit)
│   ├── 02_pong.aicl             # Levels 1–6 — game with behaviors (52 artifacts, 100% audit)
│   ├── 03_chat.aicl             # Levels 1–9 — full-featured app (58 artifacts, 100% audit)
│   └── 04_chess.aicl            # Levels 1–9 — complex state (59 artifacts, 100% audit)
├── tests/                       # Test suite
│   └── test_aicl.py             # 129 tests (all passing, including new feature tests)
├── spec/                        # Language specification
│   └── grammar.md               # Formal BNF grammar & keyword table
├── docs/                        # Documentation
│   ├── whitepaper.pdf           # White paper (16+ sections, v1.0)
│   └── position_paper.md        # "The No-Orphan Property: Towards Auditable Code Generation"
├── tools/                       # Build and utility scripts
│   ├── generate_whitepaper.py   # White paper PDF generator
│   ├── verify_proof.py          # Independent proof verifier (~200 lines, zero AICL deps)
│   └── visualize_provenance.py  # Provenance graph visualization (D3.js interactive HTML)
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
- Self-healing runtime: extending provenance into execution
- Ownership model: memory management from architectural structure
- Multi-language compilation: one specification, four targets

---

## Position Paper

The position paper at [`docs/position_paper.md`](docs/position_paper.md) — "The No-Orphan Property: Towards Auditable Code Generation" — argues that the No-Orphan Property should be a fundamental requirement for any code generation system:

- The accountability gap in traditional compilers and AI code generators
- The "Trust me bro" problem: systems assert correctness without evidence
- The No-Orphan Property as a formally verifiable invariant
- Why independence matters: circular trust vs. mathematical trust
- Implications for AI code generation and software engineering
- Objections and responses (determinism, overhead, dynamic code, hash binding)

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| **v0.1** | Parser, grammar, Python codegen, 38 tests | ✅ Done |
| **v0.2** | Deterministic patterns, zero-TODO compilation, provenance | ✅ Done |
| **v0.3** | Sub-language expansion, architecture templates | ✅ Done |
| **v0.4** | Explicable compilation thesis, provenance-first design, project reorganization | ✅ Done |
| **v0.5** | Audit system, artifact tracking, 100% audit coverage, orphan detection, `aicl audit` | ✅ Done |
| **v0.6** | Proof of Origin v1.0, `aicl proof` command, explain/audit from proof file | ✅ Done |
| **v0.7** | Proof of Origin v2.0 (self-contained), independent verifier, 8 verification checks, No-Orphan as formal property | ✅ Done |
| **v0.8** | Position paper: "The No-Orphan Property: Towards Auditable Code Generation" | ✅ Done |
| **v0.9** | Specification compilation: completeness checking, coherence checking, satisfaction checking, `aicl verify` | ✅ Done |
| **v0.10** | Multi-file programs: import and module mechanisms, cross-file provenance | ✅ Done |
| **v0.11** | Cryptographic proof signing: proof files signed with compiler key, proof chain across compilations | ✅ Done |
| **v1.0** | Multi-language targets (Rust, JavaScript, Go), mature compiler, stable proof format | ✅ Done |
| **v1.5** | Provenance visualization: interactive D3.js exploration of compilation provenance graphs | ✅ Done |
| **v2.0** | Self-healing runtime with automatic recovery execution and runtime provenance | ✅ Done |
| **v2.5** | Memory management: ultra-simple ownership model derived from Layer/Entity structure | ✅ Done |
| **v3.0** | Autonomous architecture optimization, specification-driven refactoring | ✅ Done |

### The Conceptual Trajectory

The roadmap reflects a deepening understanding of what auditable compilation means:

```
v0.1–v0.3:  "I want a simpler language than C++"
v0.4–v0.5:  "I want the compiler to explain itself"     → Explicable Compilation
v0.5–v0.6:  "I want to measure that explanation"         → Auditable Compilation
v0.7:        "I want proof that doesn't require trust"    → Proof of Origin + Independent Verification
v0.8:        "This idea transcends AICL itself"           → The No-Orphan Property (Position Paper)
v0.9:        "I want to verify the specification"         → Specification Compilation
v0.10:       "I want multi-file programs"                 → Module System + Cross-File Provenance
v0.11:       "I want the proof to be tamper-proof"        → Cryptographic Proof Signing
v1.0:        "I want it in other languages"               → Multi-Language Targets
v1.5:        "I want to see the provenance"               → Provenance Visualization
v2.0:        "I want self-healing at runtime"             → Self-Healing Runtime
v2.5:        "I want safe memory management"              → Ownership Model
v3.0:        "I want the architecture to improve itself"  → Autonomous Optimization
```

Each stage discovered that the previous stage's endpoint was actually the beginning of a deeper problem. Explicable compilation raised the question of measurement. Measurement raised the question of trust. Trust raised the question of independent verification. Verification raised the question of specification quality. Specification raised the question of multi-file programs. Multi-file raised the question of proof integrity. Proof integrity raised the question of language independence. Language independence raised the question of visibility. Visibility raised the question of runtime behavior. Runtime raised the question of memory safety. Memory safety raised the question of architectural evolution.

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **New target languages** — TypeScript, C++, Java, Kotlin, Swift code generation backends
- **New behavior patterns** — Expand the deterministic pattern library
- **IDE support** — Syntax highlighting, LSP server, VS Code extension
- **New examples** — Real-world programs showcasing different levels
- **Performance optimization** — Large program compilation speed
- **Proof format standardization** — Interoperable proof files across tools
- **Runtime provenance** — Extending provenance to JIT and dynamic code generation

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Philippe-Antoine**

---

<div align="center">

*"Traditional compilers generate code. AI generates code without accountability.*
*AICL generates code with cryptographic proof of origin — and that proof can be verified by anyone.*
*Every risk has a recovery. Every artifact has provenance. Every proof is independently verifiable.*
*From specification to execution, the chain is unbroken."*

</div>
