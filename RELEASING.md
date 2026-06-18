# Releasing AICL

**Audience:** Maintainers with PyPI upload credentials.
**Purpose:** Step-by-step guide for cutting a new AICL release, from version
bump to PyPI upload to GitHub release.

> If you only want to **use** AICL, see
> [`python/docs/upgrading.md`](./python/docs/upgrading.md) instead.

---

## Prerequisites (one-time setup)

You need:

1. **Push access** to [`AFKmoney/AICL`](https://github.com/AFKmoney/AICL).
2. **A PyPI account** with maintainer/owner rights on the `aicl` package
   (request from [@AFKmoney](https://github.com/AFKmoney) if not yet set up).
3. **A PyPI API token** scoped to the `aicl` project:
   - Create at <https://pypi.org/manage/account/token/>
   - Scope: "Project: aicl"
   - Save it in `~/.pypirc` or your password manager.

4. **Local tooling** — install the `dev` extras:

   ```bash
   cd python && pip install -e ".[dev]"
   ```

   This gives you `build`, `twine`, `ruff`, `black`, `mypy`, `pytest`,
   `hypothesis`, and `pre-commit`.

5. **Pre-commit hooks installed**:

   ```bash
   pre-commit install
   ```

---

## Release checklist

A release has **8 steps**. Steps 1–6 are mechanical; step 7 publishes to
PyPI (irreversible); step 8 announces.

### Step 1 — Pick the new version number

AICL follows [Semantic Versioning](https://semver.org/):

| Change | Bump | Example |
|--------|------|---------|
| Breaking API change (compiler output format, CLI flags, public Python API) | **MAJOR** | `2.1.0` → `3.0.0` |
| New feature, new keyword, new target backend (backward-compatible) | **MINOR** | `2.1.0` → `2.2.0` |
| Bug fix, docs, perf, dependency bump (backward-compatible) | **PATCH** | `2.1.0` → `2.1.1` |
| Pre-release of an upcoming version | **pre** | `2.2.0a1`, `2.2.0b1`, `2.2.0rc1` |

**Rules:**
- A new keyword in the grammar is **MINOR** (old programs still compile).
- A removed keyword is **MAJOR**.
- A change to the compiled output format is **MAJOR** (breaks downstream
  build pipelines).
- A change to the `.aicl-proof` file format is **MAJOR**.
- CogNet integration (when it lands) will be **MINOR** (additive).

### Step 2 — Make sure `main` is green

```bash
git checkout main
git pull origin main
make test           # 156 tests must pass
make lint           # ruff + black --check + mypy + eslint + tsc
```

If anything fails, **stop**. Fix it on a PR, merge, then come back.

Also check that GitHub Actions CI is green on `main`:
<https://github.com/AFKmoney/AICL/actions>

### Step 3 — Bump the version in three places

The version is duplicated in three files. **All three must match**:

1. `python/pyproject.toml`:
   ```toml
   version = "X.Y.Z"
   ```
2. `python/src/aicl/__init__.py`:
   ```python
   __version__ = "X.Y.Z"
   ```
3. `editor/package.json` (only if the editor also needs a bump — see
   "Editor versioning" below):
   ```json
   "version": "X.Y.Z"
   ```

> The version is also referenced in `python/src/aicl/cli.py`'s `version`
> subcommand, but it reads from `__init__.py`, so no manual edit needed.

Use `make bump-version` (a helper that updates all three atomically):

```bash
make bump-version NEW_VERSION=X.Y.Z
```

Verify:

```bash
grep '^version' python/pyproject.toml
grep '__version__' python/src/aicl/__init__.py
```

### Step 4 — Update the CHANGELOG

Open [`CHANGELOG.md`](./CHANGELOG.md) and:

1. Add a new section at the top (under `## [Unreleased]`):

   ```markdown
   ## [X.Y.Z] — YYYY-MM-DD

   ### Added
   - New feature ...

   ### Changed
   - ...

   ### Fixed
   - ...

   ### Removed
   - ...
   ```

2. Move the contents of the old `## [Unreleased]` section into the new
   versioned section. Leave `## [Unreleased]` empty (just the heading).

3. Add a link at the bottom of the file:

   ```markdown
   [X.Y.Z]: https://github.com/AFKmoney/AICL/compare/vPREV...vX.Y.Z
   ```

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions.
Each entry should be a single sentence with a verb at the start.

### Step 5 — Build the package

```bash
make build-python
```

This runs `python -m build` in `python/`, producing two artifacts in
`python/dist/`:

```
python/dist/
├── aicl-X.Y.Z-py3-none-any.whl   # wheel (binary distribution)
└── aicl-X.Y.Z.tar.gz             # sdist (source distribution)
```

### Step 6 — Validate the build

```bash
# Validate PyPI metadata
twine check python/dist/*

# Inspect wheel contents (optional sanity check)
python -m zipfile -l python/dist/aicl-X.Y.Z-py3-none-any.whl | head -30

# Test-install in a clean venv
rm -rf /tmp/aicl-release-test
python -m venv /tmp/aicl-release-test
source /tmp/aicl-release-test/bin/activate
pip install python/dist/aicl-X.Y.Z-py3-none-any.whl
aicl version
python -c "import aicl; print(aicl.__version__)"
deactivate
rm -rf /tmp/aicl-release-test
```

If `twine check` fails, fix the metadata in `python/pyproject.toml` and
rebuild. Do **not** upload a build that fails validation.

### Step 7 — Publish to PyPI

This step is **irreversible**. Once a version is on PyPI it cannot be
reused or overwritten — you can only yank it (hide from default install)
or delete it (within 24h, if no dependencies depend on it).

#### 7a. Test on TestPyPI first (recommended for non-trivial releases)

```bash
twine upload --repository testpypi python/dist/*
```

Install from TestPyPI to verify:

```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            aicl==X.Y.Z
```

If TestPyPI works, proceed to 7b. If not, fix and rebuild — you'll need
to bump to a new version number (TestPyPI also doesn't allow re-uploads).

#### 7b. Upload to real PyPI

```bash
twine upload python/dist/*
```

You'll be prompted for your PyPI username and password. Use:
- **Username:** `__token__`
- **Password:** your PyPI API token (starts with `pypi-`)

Or save credentials in `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Verify the upload at <https://pypi.org/project/aicl/>

### Step 8 — Tag and release on GitHub

```bash
git add python/pyproject.toml python/src/aicl/__init__.py CHANGELOG.md
git commit -m "release: vX.Y.Z"
git tag -a vX.Y.Z -m "AICL vX.Y.Z — short summary of headline changes"
git push origin main
git push origin vX.Y.Z
```

Then create a GitHub Release:

```bash
# Either via the web UI (recommended — you can paste the CHANGELOG section):
# https://github.com/AFKmoney/AICL/releases/new?tag=vX.Y.Z

# Or via the API:
gh release create vX.Y.Z \
  --title "AICL vX.Y.Z — <headline>" \
  --notes-file <(awk '/^## \[X.Y.Z\]/{flag=1} /^## \[/{if(flag && !start){start=1;next} else if(start){exit}} flag' CHANGELOG.md)
```

Attach the built wheel and sdist to the release as well:

```bash
gh release upload vX.Y.Z python/dist/aicl-X.Y.Z-*
```

### Step 9 — Announce

- Update the `version` badge in [`README.md`](./README.md) if needed
  (currently a static badge — consider making it dynamic).
- Post to your channels: "AICL vX.Y.Z released — <headline>".
- If you maintain a Discord/Mastodon/X account for the project, post there.

---

## Editor versioning

The web editor (`editor/package.json`) is versioned **independently** from
the Python package. Bump it only when the editor changes:

| Python pkg | Editor | When to bump editor |
|------------|--------|---------------------|
| Patch (X.Y.Z → X.Y.Z+1) | Usually no bump | Only if editor also fixed a bug |
| Minor (X.Y.Z → X.(Y+1).0) | Optional bump | If editor gained a feature that needs the new Python API |
| Major (X.Y.Z → (X+1).0.0) | Required bump | Editor must be updated to work with the new Python API |

The editor does **not** get published to npm — it's bundled in the repo
for users to `bun install` themselves. So editor version bumps are
documentation-only (visible in the `package.json` and the editor's
About dialog if one exists).

---

## Rollback / yank

If a release has a critical bug:

1. **Yank it from PyPI** (hides from default `pip install` but keeps it
   available to anyone who pins the exact version):
   ```bash
   pip install yanker
   yanker aicl X.Y.Z
   # or via the web UI: https://pypi.org/manage/project/aicl/releases/
   ```

2. **Cut a patch release** following the steps above with version
   `X.Y.(Z+1)` (e.g. `2.1.0` → `2.1.1`).

3. **Update the CHANGELOG** with a note in the broken version's section:
   ```markdown
   ## [2.1.0] — 2026-06-13
   ⚠ **Yanked** — see [2.1.1] for the fix. Install with `pip install aicl!=2.1.0`.
   ```

4. **Do not delete the tag** — it's part of history. Add a note to the
   GitHub release description instead.

You **cannot** delete a version from PyPI once anyone has installed it
(unless within 24h of upload and no downloads yet).

---

## Pre-releases (alpha / beta / release candidates)

For testing a major release before it goes live:

```bash
# Bump to e.g. 3.0.0a1
make bump-version NEW_VERSION=3.0.0a1
# Update CHANGELOG: "## [3.0.0a1] — YYYY-MM-DD (pre-release)"
make build-python
twine upload python/dist/*

# Tag
git tag -a v3.0.0a1 -m "AICL v3.0.0a1 — pre-release"
git push origin v3.0.0a1
```

Users install pre-releases explicitly:

```bash
pip install --pre aicl            # any pre-release
pip install aicl==3.0.0a1         # specific pre-release
```

Pre-releases are **not** picked up by `pip install aicl` (which respects
semver precedence). They are picked up by `pip install --pre aicl`.

---

## Automation (future work)

The manual process above is intentionally explicit — it's safer for a
project with one maintainer. As the project grows, consider automating:

1. **GitHub Actions release workflow** — trigger on tag push, build the
   wheel + sdist, upload to PyPI, create GitHub Release with changelog
   excerpt. Example: `.github/workflows/release.yml`.

2. **Automated CHANGELOG from commits** — use
   [conventional commits](https://www.conventionalcommits.org/) +
   [release-please](https://github.com/googleapis/release-please) to
   auto-bump versions and generate changelog entries.

3. **Trusted publishing** — replace the long-lived PyPI API token with
   [OIDC-based trusted publishing](https://docs.pypi.org/trusted-publishers/)
   so GitHub Actions can upload without secrets.

These are tracked as future improvements and are **not** required for
the current single-maintainer workflow.

---

## Troubleshooting

### `twine upload` fails with "File already exists"

The version `X.Y.Z` is already on PyPI. PyPI does not allow re-uploads.
You must bump to a new version (e.g. `X.Y.(Z+1)`).

### Wheel installs but `aicl` command is missing

The `[project.scripts]` entry in `python/pyproject.toml` is wrong or
missing. Verify:

```toml
[project.scripts]
aicl = "aicl.cli:main"
```

Rebuild and re-upload with a new version number.

### `pip install aicl` installs the wrong version

PyPI caches aggressively. Force a refresh:

```bash
pip install --no-cache-dir aicl==X.Y.Z
```

Or check what's actually on PyPI:

```bash
pip index versions aicl
```

### Build fails with "No module named 'build'"

Install the dev extras:

```bash
cd python && pip install -e ".[dev]"
```

### `make bump-version` doesn't exist yet

The Makefile target is a planned convenience. Until it lands, bump the
version manually in the three files listed in Step 3.

---

## Quick reference

```bash
# One-shot release (after Step 1-4 done):
make test
make lint
make build-python
twine check python/dist/*
twine upload python/dist/*
git add -A
git commit -m "release: vX.Y.Z"
git tag -a vX.Y.Z -m "AICL vX.Y.Z"
git push origin main
git push origin vX.Y.Z
# Then create the GitHub Release via the web UI.
```

See also:
- [User-facing upgrade guide](./python/docs/upgrading.md)
- [CHANGELOG](./CHANGELOG.md)
- [PyPI project page](https://pypi.org/project/aicl/)
- [GitHub Releases](https://github.com/AFKmoney/AICL/releases)
