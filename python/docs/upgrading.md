# Upgrading AICL

**Audience:** Users of the AICL Python package (installed via `pip` or from
source).
**Purpose:** How to check your current version, upgrade to a new version,
downgrade in an emergency, and migrate when there are breaking changes.

> If you are a **maintainer** cutting a new release, see
> [`RELEASING.md`](../../RELEASING.md) instead.

---

## TL;DR

```bash
# Check what you have
pip show aicl
# or: python -c "import aicl; print(aicl.__version__)"

# Upgrade to the latest
pip install --upgrade aicl

# Upgrade to a specific version
pip install aicl==2.2.0

# Install pre-release versions
pip install --pre aicl
```

---

## Where versions come from

AICL is published to [PyPI](https://pypi.org/project/aicl/) as both a
**wheel** (pre-built binary distribution, fast install) and an **sdist**
(source distribution, used as a fallback).

The version numbering follows [Semantic Versioning](https://semver.org/):

| Bump type | When it happens | Impact on you |
|-----------|-----------------|---------------|
| **PATCH** (X.Y.Z → X.Y.Z+1) | Bug fixes, docs, perf | Safe to upgrade blindly. No code changes needed. |
| **MINOR** (X.Y.Z → X.(Y+1).0) | New features, new keywords, new targets | Safe to upgrade. Old code keeps working. New features are opt-in. |
| **MAJOR** (X.Y.Z → (X+1).0.0) | Breaking changes | **Read the migration guide below.** Compiled output may change. |

Pre-release versions (`2.2.0a1`, `2.2.0b1`, `2.2.0rc1`) are **not**
installed by default. Use `pip install --pre aicl` to opt in.

---

## Checking your current version

Three equivalent ways:

```bash
# 1. From pip
pip show aicl | grep -i version

# 2. From the Python interpreter
python -c "import aicl; print(aicl.__version__)"

# 3. From the CLI
aicl version
```

The CLI output also tells you which target languages are enabled:

```
AICL v2.1.0
Artificial Intelligence-Centered Language
  AX sub-language: Turing-complete (if/while/for/recursion)
  Targets: Python, Rust, JavaScript, Go
  Proof of Origin: cryptographic, sidecar .aicl-proof
  CogNet integration: fine-tuning corpus generator ready
```

---

## What's new in 2.1.0

- **AX sub-language**: Turing-complete `Action:` sections that compile to real
  executable code in all 4 targets (no more skeleton `pass` stubs)
- **Type inference**: arrays and ints correctly typed for Rust/Go targets
- **CLI overhaul**: rich colored output, `--json`, `init`, `new`, `targets`,
  `doctor`, `--model` flag, `set_defaults` dispatch
- **TUI overhaul**: real TextArea editor (was read-only), fixed `:save`,
  `:compile all` (4 targets simultaneously)
- **Web editor**: AX syntax highlighting, localStorage persistence
- **151 AX-powered dataset scripts** replacing all old prose-style examples
- **CogNet 1B training pipeline**: `cloud_train.py` with `--model small|1b`

## Upgrading

### Basic upgrade

```bash
pip install --upgrade aicl
```

This fetches the latest compatible version. If you have the `[tui]` extra
installed, preserve it:

```bash
pip install --upgrade "aicl[tui]"
```

Same for `[dev]`:

```bash
pip install --upgrade "aicl[tui,dev]"
```

### Pinning a specific version

For reproducible builds, pin in your `requirements.txt`:

```text
aicl==2.1.0
```

Or in `pyproject.toml`:

```toml
[project]
dependencies = ["aicl>=2.1,<3.0"]
```

The `<3.0` upper bound protects you from a future breaking major release
auto-installing.

### Upgrading from a Git checkout

If you installed from source (development install):

```bash
cd /path/to/AICL
git fetch --tags
git checkout v2.2.0    # or: git checkout main && git pull
pip install --force-reinstall -e python/
```

Verify:

```bash
aicl version
```

---

## What to do after upgrading

### 1. Re-run your test suite

```bash
pytest tests/
```

If anything breaks, check the [CHANGELOG](../../CHANGELOG.md) for the
version you upgraded to. Breaking changes are always listed under a
`### Removed` or `### Changed` heading.

### 2. Re-compile any cached AICL output

If you have `.aicl-proof` files from an older version of the compiler
that you need to re-verify, the proof chain should still verify
(backward-compatible by design). If it doesn't, the proof was generated
by a version with a known bug — see the CHANGELOG for the fix version.

```bash
aicl proof path/to/old.aicl-proof
```

### 3. Check for new optional features

Minor releases sometimes add new optional dependencies. Check the
CHANGELOG for the `[tui]`, `[dev]`, or future `[cognet]` extras.

---

## Downgrading

If a new version breaks your workflow and you need to revert:

```bash
pip install aicl==2.1.0
```

PyPI keeps every version ever published. You can list available versions:

```bash
pip index versions aicl
```

Or:

```bash
pip install aicl==    # tab-completes with available versions
```

### Why a version might be unavailable

- It was **yanked** (hidden from default install but still installable
  with explicit version pin). Install with `pip install aicl==X.Y.Z`
  still works.
- It was **deleted** (within 24h of upload, if no one downloaded it).
  This is rare.

If a version is yanked, the CHANGELOG will say so.

---

## Migration guides

This section is updated when a MAJOR release happens. For MINOR and PATCH
releases, no migration is needed.

### v2.x → v3.0 (not yet released — placeholder)

> **Status:** Not scheduled. Will be added when v3.0 is planned.

Expected scope (subject to change):
- CogNet runtime integration stabilises and becomes a default-on feature
  (currently opt-in placeholder).
- `.aicl-proof` file format may gain a new field for CogNet signature
  chains. Old proofs still verify; new proofs are not backward-readable
  by old tools.

Migration steps will be published here when v3.0 is released.

### v1.x → v2.0

> **Status:** Already happened (v2.0.0 released 2026-04-15).

Breaking changes in v2.0:

- **Self-healing runtime** added (`runtime.py`). Risks declared in source
  are now bound to Recoveries at compile time and executed by the
  runtime when the risk fires. Old v1.x programs that declared Risks
  without matching Recoveries will now fail to compile — add a
  `Recovery:` section.
- **Ownership analysis** added (`ownership.py`). Generated code now
  includes ownership hints. Old generated code still runs but does not
  benefit from ownership checking.
- **Architecture optimiser** added (`auto_optimizer.py`). Opt-in via
  `aicl optimize`. Does not change default compilation output.

To migrate from v1.x to v2.0:

1. `pip install aicl==2.0.0`
2. Run `aicl verify` on all your `.aicl` files. Any file with an
   unmatched `Risk:` will fail — add a `Recovery:` section.
3. Re-compile all programs with `aicl compile`. The new output includes
   ownership hints and is fully backward-compatible at runtime.

---

## Staying informed

Three ways to hear about new releases:

1. **Watch the GitHub repo.** Go to
   <https://github.com/AFKmoney/AICL> → "Watch" → "Custom" → "Releases".
   You'll get an email for every release.

2. **Subscribe to PyPI RSS.** Add
   <https://pypi.org/rss/project/aicl/releases.xml> to your feed reader.

3. **Check the CHANGELOG.** <https://github.com/AFKmoney/AICL/blob/main/CHANGELOG.md>
   is updated before every release.

---

## Frequently asked questions

### "I upgraded and now my generated Python code is different"

This happens on MINOR releases when the compiler output format is
improved. The new output is always backward-compatible at runtime — your
old tests still pass — but the diff is non-empty.

If you need bit-exact reproducibility (e.g. for regulatory reasons), pin
the AICL version and don't upgrade without re-running your full
validation suite.

### "I upgraded and now my `.aicl-proof` files don't verify"

This should never happen on a non-MAJOR release — it's a bug. File an
issue at <https://github.com/AFKmoney/AICL/issues> with:

- The AICL version that generated the proof
- The AICL version that's failing to verify it
- The proof file (or a minimal reproduction)

### "Should I install from PyPI or from Git?"

**PyPI**, unless you need an unreleased feature or fix. The PyPI package
is tested, has passed `twine check`, and is what 99% of users should use.

Install from Git only if:
- You need a fix that's merged to `main` but not yet released.
- You're contributing to AICL itself.
- You need to debug something against a specific commit.

```bash
# From Git (latest main)
pip install git+https://github.com/AFKmoney/AICL.git#subdirectory=python

# From Git (specific tag)
pip install git+https://github.com/AFKmoney/AICL.git@v2.1.0#subdirectory=python
```

### "Can I have multiple versions installed at once?"

No — Python packages can only have one version installed per
environment. Use separate virtualenvs:

```bash
python -m venv venv-2.1
python -m venv venv-2.2
venv-2.1/bin/pip install aicl==2.1.0
venv-2.2/bin/pip install aicl==2.2.0
```

### "What Python versions are supported?"

Python 3.10, 3.11, and 3.12. CI runs on all three:
<https://github.com/AFKmoney/AICL/actions/workflows/ci.yml>

Python 3.13 will be added when its stable release lands and our
dependencies (`textual`, `rich`) support it.

### "Does the package include type hints?"

Yes. The `py.typed` marker (PEP 561) is shipped in the wheel, so
`mypy`/`pyright` will pick up type hints when you `import aicl`.

The codebase is not yet fully type-annotated, but the public API surface
is. Missing annotations are tracked as a long-term cleanup.

---

## Getting help

- **Bug reports:** <https://github.com/AFKmoney/AICL/issues>
- **Questions:** Open a Discussion at
  <https://github.com/AFKmoney/AICL/discussions> (if enabled) or just
  open an issue labelled `question`.
- **Security issues:** See [`SECURITY.md`](../../SECURITY.md) — do **not**
  open a public issue for security problems.

---

## See also

- [CHANGELOG](../../CHANGELOG.md) — what changed in each version
- [RELEASING.md](../../RELEASING.md) — maintainer's release guide
- [PyPI project page](https://pypi.org/project/aicl/)
- [GitHub Releases](https://github.com/AFKmoney/AICL/releases)
- [Install instructions](../../README.md#install) — for first-time install
