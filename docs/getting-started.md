# Getting Started with AICL

AICL (Artificial Intelligence-Centered Language) is a specification-first
programming language where risks, recoveries, and validations are mandatory
syntax — not comments. Every compilation produces a cryptographic Proof of
Origin that ties each line of generated code back to the spec it came from.

## Install

```bash
git clone https://github.com/AFKmoney/AICL.git
cd AICL/python
pip install -e .
```

Requires Python 3.10–3.13. The CLI works on 3.14 too (fixed in 2.1.0).

## Your first AICL program

Create `hello.aicl`:

```aicl
Goal:
Greet the user by name

Risk:
Name is empty

Recovery:
Use a default greeting

Validation:
A greeting is produced

Behavior Greet
    Input: name
    Output: message
    Action:
        if len(name) == 0:
            return "Hello, world!"
        return "Hello, " + name + "!"
```

Compile it:

```bash
aicl compile hello.aicl --target python -o ./output
```

This produces `output/main.py` — executable Python — plus `output/main.aicl-proof`,
the cryptographic Proof of Origin.

## The AX sub-language

The `Action:` section above uses **AX**, AICL's Turing-complete sub-language.
AX gives Behaviors real, compilable logic instead of English prose:

| Feature | AX syntax |
|---------|-----------|
| Conditionals | `if` / `elif` / `else` |
| Loops | `while`, `for x in range(a, b)` |
| Recursion | Call other behaviors by name |
| Arithmetic | `+`, `-`, `*`, `/`, `//`, `%`, `**` |
| Comparisons | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Logic | `and`, `or`, `not` |
| Lists | `[1, 2, 3]`, `result.append(x)` |
| Swaps | `a, b = b, a` |

AX compiles to **real, executable code** in all four targets. See the
[AX reference](./ax-reference.md) for the full grammar.

## Compile targets

```bash
aicl compile hello.aicl --target python      # → main.py
aicl compile hello.aicl --target rust        # → main.rs
aicl compile hello.aicl --target javascript  # → main.mjs
aicl compile hello.aicl --target go          # → main.go
```

Every target ships an identical `.aicl-proof` file — the Proof of Origin is
target-independent. See [Targets](./targets.md) for details.

## Verify and audit

```bash
aicl verify hello.aicl       # Check spec completeness (Goal/Risk/Recovery/Validation)
aicl compile hello.aicl      # Compile + generate Proof of Origin
aicl audit hello.aicl        # Verify every artifact has provenance
aicl explain hello.aicl      # Show why each line was generated
aicl check hello.aicl        # Check errors, warnings, and AX syntax (--target aware)
```

## Scaffold a new project

```bash
aicl init my-app             # Creates my-app/my-app.aicl + README
aicl new sort --inputs array # Generates a Behavior template with AX skeleton
aicl targets                 # List 4 compile targets + AX capabilities
aicl doctor                  # Diagnose your environment (Python, node, rustc, go)
```

## Machine-readable output (CI/CD)

```bash
aicl --json compile hello.aicl --target rust   # JSON output for pipelines
aicl --json audit hello.aicl                    # JSON audit report
```

## Interactive TUI

```bash
aicl tui
```

A full terminal IDE with a real code editor (TextArea), AX syntax
highlighting, 4-target compilation (`:compile all`), and an AI assistant.

Key TUI commands:
- `:compile all` — compile to Python + Rust + JS + Go simultaneously
- `:save <file>` — save editor content to disk (Ctrl+S works too)
- `:tutorial` — guided AICL tutorials
- `:chat` — chat with a local LLM assistant

Requires `pip install textual` (rich is now a core dependency).

## Web editor

```bash
cd editor
bun install
bun dev
```

A Next.js web IDE with AX syntax highlighting, localStorage persistence
(no data loss on refresh), 4-target compilation, AI chat, and autonomous
evolution. The editor auto-saves your files between sessions.

A Next.js web IDE with file tabs, live compilation, architecture tree
visualization, and an AI assistant. See `editor/README.md`.

## What's next

- [AX reference](./ax-reference.md) — full grammar and examples
- [Compile targets](./targets.md) — Python, Rust, JavaScript, Go
- [CogNet integration](./cognet-integration.md) — fine-tune CogNet on AICL
- [Proof of Origin](./proof-of-origin.md) — cryptographic provenance
