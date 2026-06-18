# Contributing to AICL

> **You make a critical error if you consider AICL to be simply a programming language.**
> AICL is a cognitive representation language. The generated code is a byproduct. The architecture is the real program.

Welcome to AICL. We're building a language that forces explicit architectural thinking — where risk, recovery, and validation are not optional afterthoughts but mandatory language elements. If that vision resonates with you, you're in the right place.

This project is open source because architectural clarity should not be proprietary. Every contribution, from a single example program to a new compiler backend, moves the needle toward a world where AI systems reason about structure rather than syntax.

---

## How to Contribute

### 1. Write AICL Example Programs

**This is the easiest way to contribute.** Just write a `.aicl` file.

AICL's power is demonstrated through its examples. Every spec in the `python/examples/` directory teaches the compiler — and any AI trained on it — how to think about a domain. A new example is a genuine contribution to the language's cognitive coverage.

See [AICL Example Program Guidelines](#aicl-example-program-guidelines) below for requirements.

### 2. Improve the Compiler

The compiler lives in `python/src/aicl/` and `python/tools/`. It's written in Python and handles lexing, parsing, IR generation, multi-target compilation, and Proof of Origin verification. Key areas:

- **Parser and AST** (`python/src/aicl/parser.py`, `python/src/aicl/ast.py`) — improve error messages, add structural validation
- **Compiler and IR** (`python/src/aicl/compiler.py`, `python/src/aicl/ir.py`) — optimization passes, better code generation
- **Provenance and Crypto** (`python/src/aicl/provenance.py`, `python/src/aicl/crypto_signing.py`) — strengthen the Proof of Origin chain
- **Autonomous Mode** (`python/src/aicl/autonomous.py`, `python/src/aicl/auto_optimizer.py`) — self-improving compilation

### 3. Add Target Language Support

AICL currently compiles to Python, Rust, Go, and JavaScript (see `python/src/aicl/targets/`). Adding a new target means:

1. Create a new module in `python/src/aicl/targets/` extending `base.py`
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

Every compilation must produce a valid, independently verifiable Proof of Origin. Contributions to testing infrastructure, verification tooling (`python/tools/verify_proof.py`), and provenance visualization (`python/tools/visualize_provenance.py`) are critical.

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
aicl compile python/examples/showcase/your_file.aicl
```

And it must produce a valid Proof of Origin:

```bash
python python/tools/verify_proof.py output/your_file.aicl-proof
```

### Style

- Use descriptive names, not placeholders
- Include a comment header explaining the domain
- Look at existing examples in `python/examples/showcase/` for patterns
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

The authoritative AICL grammar is at [`python/spec/grammar.md`](python/spec/grammar.md). If your contribution touches the language itself — new keywords, changed semantics, structural rules — it must be reflected in the spec first.

---

## Tooling

### Python (required for the language)

- Install: `make install-python` (or `cd python && pip install -e ".[tui,dev]"`)
- Test: `make test`
- Lint: `make lint-python` (ruff + black --check + mypy)
- Format: `make format` (black + ruff --fix)

The Python toolchain is **ruff** (lint), **black** (format), and **mypy**
(types). Configuration lives in `python/pyproject.toml`. The codebase is
not yet fully type-annotated — `disallow_untyped_defs` is currently
`false` so existing code won't break, but new code should include type
hints.

### Editor (optional, for the web IDE)

- Install: `make install-editor` (uses [Bun](https://bun.sh/) by default)
- Dev: `make editor` → http://localhost:3000
- Build: `make build-editor`

**Bun vs npm vs pnpm:** Bun is the default because it's faster, but the
editor works with any of them. If you prefer npm:

```bash
cd editor && npm install && npm run dev
```

If you want to switch the lockfile permanently, delete `bun.lock` and run
`npm install` (or `pnpm install`) — the `package.json` is tool-agnostic.

### Pre-commit hooks (recommended)

Install the git hooks once after cloning:

```bash
make install-precommit
# or: pre-commit install
```

This runs ruff, black, mypy, eslint, and tsc on every commit. To run
manually across the whole repo:

```bash
pre-commit run --all-files
```

The config is in [`.pre-commit-config.yaml`](./.pre-commit-config.yaml).

### CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and PR:
- Python 3.10, 3.11, 3.12 — install + test + CLI smoke test + lint
- Editor — install + lint + type-check + production build

A green CI is required for merge to `main`.

### Releasing

Releases are cut by maintainers only. The full process (version bump →
build → PyPI upload → GitHub release) is documented in
[`RELEASING.md`](./RELEASING.md). The quick reference:

```bash
make bump-version NEW_VERSION=X.Y.Z
# edit CHANGELOG.md
make test && make lint
make build-python
twine check python/dist/*
twine upload python/dist/*
git tag -a vX.Y.Z -m "AICL vX.Y.Z"
git push origin main && git push origin vX.Y.Z
```

Users install releases from
[PyPI](https://pypi.org/project/aicl/) — see
[`python/docs/upgrading.md`](./python/docs/upgrading.md) for the
user-facing upgrade guide.

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
