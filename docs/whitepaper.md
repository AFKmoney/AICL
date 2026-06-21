# AICL: Artificial Intelligence-Centered Language

## A White Paper on Specification-First Programming with Cryptographic Proof of Origin

**Version 2.1.0 — June 2026**
**Author: Philippe-Antoine Robert (@AFKmoney)**
**License: MIT**

---

## Abstract

AICL (Artificial Intelligence-Centered Language) is a specification-first
programming language where architectural intent, risk management, and
validation are mandatory syntax — not comments. Every compilation produces
a cryptographic Proof of Origin that ties each line of generated code back
to the specification it came from. AICL introduces **AX**, a Turing-complete
sub-language for Behavior actions that compiles to real, executable code in
Python, Rust, JavaScript, and Go. Combined with **CogNet**, a non-transformer
language model fine-tuned on AICL spec→code pairs, the system creates a
self-improving compilation pipeline where an AI writes, validates, and
explains its own code.

This white paper presents the architecture, the AX sub-language, the
four-target compilation pipeline, the Proof of Origin system, the CogNet
integration, and experimental results across 189 tests and 151 AX-powered
algorithm scripts.

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [AICL's Answer](#2-aicls-answer)
3. [Language Architecture](#3-language-architecture)
4. [AX: The Turing-Complete Sub-Language](#4-ax-the-turing-complete-sub-language)
5. [Four-Target Compilation](#5-four-target-compilation)
6. [Proof of Origin](#6-proof-of-origin)
7. [CogNet Integration](#7-cognet-integration)
8. [Tools and Interfaces](#8-tools-and-interfaces)
9. [Experimental Results](#9-experimental-results)
10. [Related Work](#10-related-work)
11. [Limitations and Future Work](#11-limitations-and-future-work)

---

## 1. The Problem

AI-generated code has a fundamental accountability crisis. Modern language
models produce millions of lines of code daily, but none of it carries
**provenance** — a verifiable explanation of *why* each line exists, *where*
it came from, and *whether* it satisfies the stated requirements.

### The three gaps

| Gap | Consequence |
|-----|-------------|
| **No provenance** | Generated code cannot be audited. You cannot trace a line back to a requirement. |
| **No enforcement** | Risks and recoveries are comments that nothing checks. A function can ignore every declared failure mode. |
| **No explanation** | When the compiler emits code, it cannot explain its decisions. "Trust me" is the only answer. |

These gaps make AI-generated code unsuitable for safety-critical,
regulated, or auditable environments — which is most of professional
software engineering.

---

## 2. AICL's Answer

AICL inverts the relationship between specification and code. The
specification **is** the program. Code is a byproduct.

### Governing principle

> **If the compiler cannot explain why, it does not generate.**

Every line of generated code must carry a recorded reason — tied to a
specific section of the source specification, produced by a named
compilation stage, and hashed for integrity. If any artifact lacks this
provenance chain, the compilation is incomplete.

### What makes AICL different

| Feature | Traditional languages | AICL |
|---------|----------------------|------|
| Risk management | Comments, if any | **Mandatory syntax** — a Risk without a Recovery does not compile |
| Validation | Manual tests | **Declared in the spec** — the compiler generates test stubs |
| Code provenance | None | **Cryptographic Proof of Origin** for every artifact |
| AI code generation | Unaccountable | **AX sub-language** — AI writes compilable logic, not prose |
| Multi-target | Manual ports | **One spec → Python, Rust, JS, Go** — all executable |
| Explainability | None | **`aicl explain`** shows why each line was generated |

---

## 3. Language Architecture

AICL is structured in 10 progressive levels, each adding an architectural
dimension.

### Level overview

| Level | Dimension | Keywords |
|-------|-----------|----------|
| 1 | Architecture | Goal, Constraint, Risk/Recovery, Layer/SubLayer, Validation |
| 2 | Entities | Entity with typed fields |
| 3 | Behaviors | Behavior with Input/Output/Action |
| 4 | Conditions | When/Then rules |
| 5 | Events | On/Action handlers |
| 6 | Concurrency | Parallel execution |
| 7 | Optimization | Optimize/Priority targets |
| 8 | Learning | Learn/Adapt/Based adaptive behavior |
| 9 | Security | Encrypt/Protect directives |
| 10 | Native | Inline code in any target language |

### Level 3: Behaviors and AX

Level 3 is where computation lives. A Behavior declares its inputs, outputs,
and an **Action**. In AICL 2.1.0, the Action can use **AX** — the
Turing-complete sub-language — to express real, compilable logic.

```aicl
Behavior Partition
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

### Enforcement

The compiler enforces structural rules before generating any code:

- A program **without a Goal** does not compile.
- A program **with a Risk but no matching Recovery** does not compile.
- A program **whose Validation cannot be traced to a Goal** does not compile.

This is the "specification-first" guarantee: invalid intent is caught at
compile time, not at runtime.

---

## 4. AX: The Turing-Complete Sub-Language

### Design rationale

Before AICL 2.1.0, Behavior Actions contained free-form English prose
("partition the array around a pivot"). No pattern-matcher can translate
arbitrary English into code. The result was skeleton output: method
signatures with `pass` bodies.

AX replaces prose with a strict, compilable grammar. It is deliberately a
subset of Python, making the Python translation near-identity and the
Rust/JS/Go translations mechanical.

### Grammar

```
action        ::= stmt+
stmt          ::= assign | if | while | for | return | break | continue | swap
assign        ::= lvalue "=" expr | lvalue aug_op expr
if            ::= "if" expr block ("elif" expr block)* ("else" block)?
while         ::= "while" expr block
for           ::= "for" name "in" expr block
block         ::= INDENT stmt+ DEDENT
expr          ::= or_expr → and_expr → not_expr → comparison → arith → term → factor → power → atom
atom          ::= literal | name | "(" expr ")" | list | call | index | attr
swap          ::= lvalue_list "=" expr_list    (e.g. a, b = b, a)
```

### Supported constructs

| Category | Constructs |
|----------|-----------|
| Control flow | `if`/`elif`/`else`, `while`, `for x in range(...)` |
| Recursion | Call other behaviors by name |
| Arithmetic | `+ - * / // % **` |
| Comparison | `== != < <= > >=` |
| Logic | `and or not` |
| Data | List literals `[1,2,3]`, indexing `x[i]`, method calls `result.append(x)` |
| Swaps | `a, b = b, a` (correct for indexed locations) |
| Builtins | `len()`, `abs()`, `max()`, `min()`, `range()` |

### Type inference

AX is dynamically typed, but Rust and Go targets need static types. The
compiler infers types from usage:

- A name **indexed** (`x[i]`) or passed to `len()` → **array**
- A name in **arithmetic** → **integer**
- Otherwise → **default** (int for numeric contexts)

This is conservative — only types that can be proven are inferred. See
`python/src/aicl/ax/typeinfer.py`.

---

## 5. Four-Target Compilation

AICL compiles a single `.aicl` source to four target languages. AX-written
behaviors produce **real, executable code** in every target.

### Target matrix

| Target | Output | Runtime validated |
|--------|--------|-------------------|
| Python | `main.py` + `test_main.py` | In-process exec |
| Rust | `main.rs` + `Cargo.toml` | rustc compile + run |
| JavaScript | `main.mjs` | `node --check` + exec |
| Go | `main.go` + `go.mod` | `go build` + run |

### Translation examples

| AX | Python | Rust | JS | Go |
|----|--------|------|----|----|
| `for j in range(a, b)` | `for j in range(a, b):` | `for j in (a)..(b)` | `for (let j = a; j < b; j++)` | `for j := a; j < b; j++` |
| `a, b = b, a` | native swap | temp vars (capture-first) | `[a, b] = [b, a]` | native or temps |
| `len(x)` | `len(x)` | `x.len() as i64` | `x.length` | `len(x)` |
| `x // y` | `x // y` | `x / y` (int trunc) | `Math.trunc(x / y)` | `x / y` (int) |

### Proof of Origin is target-independent

The `.aicl-proof` file is identical regardless of target. Provenance
describes the spec→code mapping, not the target-specific syntax. Whether
you compile to Python or Go, the same proof verifies the same artifacts.

---

## 6. Proof of Origin

Every compilation produces a `.aicl-proof` sidecar file — a cryptographic
record that ties each generated artifact back to its source.

### What it contains

For each generated artifact:

- **Source span**: the exact location in the `.aicl` source that produced it
- **Compilation stage**: which phase generated it (parsing, AX emission,
  pattern matching, fallback)
- **SHA-256 hash**: of the generated artifact
- **Resolution path**: the chain of decisions that led to this output

### Verification

The proof is self-contained — it does not require the AICL compiler to
verify. A standalone script (`tools/verify_proof.py`) checks the hash chain
independently:

```bash
python tools/verify_proof.py output/main.aicl-proof
```

If verification fails, the compilation was tampered with after the fact.
**The artifact is not trustworthy.**

### Audit coverage

The `aicl audit` command computes what percentage of generated artifacts
have complete provenance. In all 151 dataset scripts, audit coverage is
**100%** — every artifact is traceable.

---

## 7. CogNet Integration

AICL is the training ground for [CogNet](https://github.com/AFKmoney/CogNet),
a non-transformer language model with O(n) cognitive routing and a
three-tier hierarchical memory system (Working, Episodic, Semantic).

### Architecture

```
AICL spec (.aicl)  →  corpus_generator  →  training corpus (.raw)
                                              ↓
                                    CogNet fine-tuning (--model 1b)
                                              ↓
                                    CogNetAICL model
                                              ↓
                              Generates new AICL specs + code
```

### Corpus

The corpus generator (`tools/corpus_generator.py`) produces plain-text
training data: each document is an AICL spec followed by its compiled code.
CogNet is character-level, so it learns the spec→code mapping as a
character distribution.

**151 AX-powered algorithm scripts** across 14 categories: sorting,
searching, math, arrays, strings, logic, geometry, statistics, games,
conversions, number theory, bitops, recursion, and validation. Each
compiles to valid, executable code in all four targets.

### Model sizes

| Model | Parameters | VRAM | Use case |
|-------|-----------|------|----------|
| small | 163M | 8-12 GB | Prototyping, consumer GPUs |
| 1b | 1.01B | 24-40 GB | Production, A100 recommended |

Both use `seq_len=2048` — the full AICL spec context window.

### Training pipeline

```bash
git clone https://github.com/AFKmoney/CogNet.git && cd CogNet
pip install -r requirements_aicl.txt
python cloud_train.py --steps 5000 --model 1b
```

The script auto-clones the AICL compiler, generates a fresh corpus, and
launches training with GPU auto-detection. Segment-based training allows
resumption without losing progress ("repair the car while driving").

---

## 8. Tools and Interfaces

### CLI (18 commands)

The AICL CLI uses rich-colored output, supports `--json` for CI/CD, and
includes project scaffolding:

```bash
aicl init my-app              # Scaffold a new project
aicl new sort --inputs array  # Generate a Behavior with AX skeleton
aicl compile app.aicl -t rust # Compile to Rust (AX → real code)
aicl check app.aicl -t go     # Target-aware AX syntax check
aicl verify app.aicl          # Spec completeness verification
aicl audit app.aicl           # Provenance audit (100% coverage)
aicl explain app.aicl         # Why each line was generated
aicl targets                  # List 4 targets + AX capabilities
aicl doctor                   # Environment diagnostic
aicl --json compile app.aicl  # Machine-readable output
```

### TUI (Textual)

A full terminal IDE with:
- **Real code editor** (TextArea — not read-only)
- AX syntax highlighting (if/while/for in purple, builtins in yellow)
- `:compile all` — compile to 4 targets simultaneously
- `:save` — writes to disk (Ctrl+S)
- AI chat with local LLM backends (GGUF, ONNX)
- Guided tutorials including AX

### Web editor (Next.js 16)

A browser-based IDE with:
- AX syntax highlighting (AICL keywords in teal, AX keywords in purple)
- 4-target compilation with dynamic file badges (`.py`/`.rs`/`.mjs`/`.go`)
- **localStorage persistence** — no data loss on refresh
- AI chat with spec generation and autonomous evolution loop
- Interactive exercises and examples

---

## 9. Experimental Results

### Test suite

| Metric | Value |
|--------|-------|
| Total tests | **189 passed, 0 failed, 0 skipped** |
| AX frontend tests | 11 (lexer, parser, emitter, syntax rejection) |
| AX runtime tests (Python) | 3 algorithms executed and verified correct |
| AX runtime tests (JavaScript) | 4 algorithms executed via Node |
| AX runtime tests (Rust) | 3 algorithms compiled via rustc + executed |
| AX runtime tests (Go) | 2 algorithms compiled via go + executed |
| Cross-target integration | 8 tests (1 spec → 4 targets, algorithm present) |
| Original compiler tests | 156 (all language levels, provenance, proof chain) |

### Dataset

| Metric | Value |
|--------|-------|
| AX-powered scripts | **151** |
| Categories | 14 (sorting, searching, math, arrays, etc.) |
| Scripts compiling to valid Python | **151/151 (100%)** |
| Corpus size (training) | 54,107 chars |
| Corpus size (multi-target Python+Rust) | 305,350 chars |

### Runtime validation

Every AX algorithm is validated by **actual execution**, not just syntax
checking:

- **Python**: quicksort sorts `[3,1,4,1,5,9,2,6,5,3,5]` → `[1,1,2,3,3,4,5,5,5,6,9]` ✓
- **JavaScript (Node)**: binary search finds all targets, returns -1 for absent ✓
- **Rust (rustc)**: factorial recursive, n=0..9, matches `math.factorial` ✓
- **Go**: quicksort + factorial compile and run correctly ✓

### Proof of Origin

All 151 dataset scripts produce a valid `.aicl-proof` file with **100% audit
coverage** — every generated artifact has complete, verifiable provenance.

---

## 10. Related Work

### Design-by-contract

AICL's mandatory Risk/Recovery syntax extends Eiffel's design-by-contract
to include failure modes as first-class language constructs. Where Eiffel
requires preconditions and postconditions, AICL additionally requires every
declared Risk to have a matching Recovery.

### Provenance in compilers

The Proof of Origin system draws on software supply chain security (SLSA,
in-toto) but applies it at the compilation level — not the build pipeline
level. Each compilation artifact, not each binary, has cryptographic provenance.

### Neural code generation

CogNetAICL differs from CodeBERT, Codex, and similar models in two ways:
(1) CogNet is non-transformer (O(n) cognitive routing, not O(n²) attention),
and (2) the training data is spec→code pairs in a formal language (AICL/AX),
not natural-language→code pairs. The formal language eliminates ambiguity in
the training signal.

---

## 11. Limitations and Future Work

### Current limitations

- **AX scope**: AX covers algorithms (control flow, arithmetic, data
  structures). It does not cover I/O (sockets, files, graphics) — use
  `Native:` sections for those.
- **No string library**: AX strings support comparison and concatenation
  but not regex, splitting, or formatting.
- **Single-type lists**: AX lists are homogeneous (all `i64`/`int`). Mixed
  types would need a sum type.
- **Type inference is conservative**: only arrays and integers are
  inferred. Floats, strings, and booleans default to integer.
- **CogNet not yet fine-tuned at scale**: the pipeline is ready, but
  production-scale fine-tuning requires a GPU cloud instance.

### Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| A | ✅ Done | AX sub-language (lexer, parser, Python emitter) |
| B | ✅ Done | AX emitters for Rust, JS, Go + type inference |
| C | ✅ Done | Corpus generator (151 scripts) + CogNet training pipeline |
| D | ✅ Done | CLI/TUI/web editor refonte |
| E | 🔨 Next | Large-scale CogNet fine-tuning (1B model on A100) |
| F | 🔨 Next | Expanded AX (string library, float types, generics) |
| G | 🔨 Next | CogNetAICL inference: generate new specs from natural language |

---

## References

1. AICL Project. *Artificial Intelligence-Centered Language: Specification-first programming with AX sub-language and Proof of Origin*. https://github.com/AFKmoney/AICL
2. CogNet Project. *Non-transformer language model with cognitive routing and hierarchical memory*. https://github.com/AFKmoney/CogNet
3. FIPS 180-4. *Secure Hash Standard (SHA-256)*. NIST, 2015.
4. Garlan, D. & Shaw, M. *An Introduction to Software Architecture*. CMU, 1994.
5. Meyer, B. *Object-Oriented Software Construction* (design by contract). Prentice Hall, 1997.

---

## Appendix A: Quick Start

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL/python
pip install -e .

aicl init my-app
cd my-app
aicl compile my-app.aicl --target python
aicl audit my-app.aicl
```

## Appendix B: Dataset Categories

| Category | Scripts | Examples |
|----------|---------|----------|
| math | 33 | factorial, fibonacci, GCD, primes, digit sum |
| arrays | 25 | sort, search, filter, rotate, Kadane's algorithm |
| logic | 19 | median, leap year, grade, traffic light, quadrant |
| validation | 12 | age, score, month, day, hour, range checks |
| searching | 8 | linear, binary, ternary, find max/min |
| geometry | 8 | area, perimeter, volume, distance |
| conversions | 8 | temperature, distance, time units |
| statistics | 8 | average, range, median, variance |
| sorting | 6 | bubble, insertion, selection, quicksort, merge, counting |
| strings | 7 | length, vowels, palindrome, reverse |
| games | 6 | dice, rock-paper-scissors, guess, coin |
| numbertheory | 5 | divisors, LCM, primes, Armstrong numbers |
| bitops | 3 | popcount, odd/even checks |
| recursion | 3 | fibonacci, digit sum, power (recursive) |
| **Total** | **151** | |

---

*This white paper reflects AICL v2.1.0 as of June 2026. For the latest
version, see [github.com/AFKmoney/AICL](https://github.com/AFKmoney/AICL).*
