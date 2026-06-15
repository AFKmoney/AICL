# Contributing to AICL

> **You make a critical error if you consider AICL to be simply a programming language.**
> AICL is a cognitive representation language. The generated code is a byproduct. The architecture is the real program.

Welcome to AICL. We're building a language that forces explicit architectural thinking — where risk, recovery, and validation are not optional afterthoughts but mandatory language elements. If that vision resonates with you, you're in the right place.

This project is open source because architectural clarity should not be proprietary. Every contribution, from a single example program to a new compiler backend, moves the needle toward a world where AI systems reason about structure rather than syntax.

---

## How to Contribute

### 1. Write AICL Example Programs

**This is the easiest way to contribute.** Just write a `.aicl` file.

AICL's power is demonstrated through its examples. Every spec in the `examples/` directory teaches the compiler — and any AI trained on it — how to think about a domain. A new example is a genuine contribution to the language's cognitive coverage.

See [AICL Example Program Guidelines](#aicl-example-program-guidelines) below for requirements.

### 2. Improve the Compiler

The compiler lives in `src/aicl/` and `tools/`. It's written in Python and handles lexing, parsing, IR generation, multi-target compilation, and Proof of Origin verification. Key areas:

- **Parser and AST** (`src/aicl/parser.py`, `src/aicl/ast.py`) — improve error messages, add structural validation
- **Compiler and IR** (`src/aicl/compiler.py`, `src/aicl/ir.py`) — optimization passes, better code generation
- **Provenance and Crypto** (`src/aicl/provenance.py`, `src/aicl/crypto_signing.py`) — strengthen the Proof of Origin chain
- **Autonomous Mode** (`src/aicl/autonomous.py`, `src/aicl/auto_optimizer.py`) — self-improving compilation

### 3. Add Target Language Support

AICL currently compiles to Python, Rust, Go, and JavaScript (see `src/aicl/targets/`). Adding a new target means:

1. Create a new module in `src/aicl/targets/` extending `base.py`
2. Implement the `TargetBackend` interface for your language
3. Add tests and example compilations
4. Update the CLI and documentation

### 4. Improve Documentation

- Language spec at `spec/grammar.md`
- White paper at `docs/whitepaper.pdf`
- User and CLI manuals in `docs/`
- Code comments and docstrings

Good documentation is not secondary to good code — it *is* good code.

### 5. Testing and Proof of Origin Verification

Every compilation must produce a valid, independently verifiable Proof of Origin. Contributions to testing infrastructure, verification tooling (`tools/verify_proof.py`), and provenance visualization (`tools/visualize_provenance.py`) are critical.

---

## AICL Example Program Guidelines

A good AICL example program is a complete, self-contained architectural specification. All example submissions must meet these requirements:

### Required Elements

- **Must use at least 3 AICL levels** — A program that doesn't exercise the language's layered structure isn't demonstrating AICL's purpose. Use `Goal`, `Constraint`, `Layer`, `Sublayer`, `Behavior`, `Condition`, `Event` as appropriate.
- **Must include Risk and Recovery** — This is non-negotiable. Every `Risk` must have a corresponding `Recovery`. This is the core of AICL's philosophy: resilience is not optional.
- **Must include Validation** — Every program must specify how correctness is verified. `Validation` blocks generate tests in compiled output.

### Compilation Requirements

Your example must compile successfully:

```bash
python tools/aicl_compiler.py compile examples/your_file.aicl
```

And it must produce a valid Proof of Origin:

```bash
python tools/verify_proof.py examples/your_file.aicl.proof
```

### Style

- Use descriptive names, not placeholders
- Include a comment header explaining the domain
- Look at existing examples in `examples/` for patterns
- Number your file following the existing convention (e.g., `89_your_domain.aicl`)

---

## Code Style

### Python

- **Python 3.10+** — use modern syntax (match statements, type unions, etc.)
- **Type hints everywhere** — if a function takes or returns something, annotate it
- **Docstrings** — every public function and class gets a docstring. Google style preferred.
- **No unused imports** — keep it clean
- **Line length** — 100 characters soft limit

Example:

```python
def compile_spec(source: str, target: str = "python") -> CompilationResult:
    """Compile an AICL specification to the target language.

    Args:
        source: The AICL source code to compile.
        target: Target language (python, rust, go, javascript).

    Returns:
        A CompilationResult containing generated code and proof of origin.

    Raises:
        AICLError: If the source fails parsing or compilation.
    """
    ...
```

---

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `spec`

**Examples:**
```
feat(compiler): add C# target backend
fix(parser): handle nested Sublayer inside Behavior blocks
spec(examples): add distributed ledger example with 4 levels
docs(grammar): clarify Risk/Recovery pairing rules
test(provenance): add edge cases for Proof of Origin verification
```

---

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`: `git checkout -b feat/your-feature`
3. **Make your changes** with clear, atomic commits
4. **Test your changes** — all existing tests must pass, new code needs new tests
5. **Open a Pull Request** against `main`
6. **Describe what and why** — a good PR description explains the motivation, not just the implementation

### PR Checklist

- [ ] Code compiles and tests pass
- [ ] New code follows the style guidelines
- [ ] Type hints and docstrings are present
- [ ] Commit messages follow conventional commits
- [ ] If adding an AICL example: at least 3 levels, Risk/Recovery, Validation, compiles successfully, valid Proof of Origin

---

## Language Specification

The authoritative AICL grammar is at [`spec/grammar.md`](spec/grammar.md). If your contribution touches the language itself — new keywords, changed semantics, structural rules — it must be reflected in the spec first.

---

## Zero Censorship Note

**AICL has no content restrictions.** Spec programs may describe any system. The only validation is technical: does it compile, is the proof valid.

AICL is a language, not a policy engine. It does not judge what you specify — it ensures that what you specify is structurally sound, resilient, and verifiable. Any attempt to add content-based filtering to the compiler will not be accepted.

---

## License

By contributing to AICL, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

## Questions?

Open an issue. Start a discussion. Write an AICL spec about what's confusing you and compile it — seriously, we'd find that delightful.

*The architecture is the program. Welcome aboard.*
