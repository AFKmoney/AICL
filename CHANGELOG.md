# Changelog

All notable changes to AICL are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Repository restructured into a `python/` + `editor/` workspace (single repo).
- All editor API routes now use a shared `aicl-bridge.ts` module instead of
  duplicating the Python path in each file.
- Python interpreter path is now configurable via `AICL_PYTHON` env var
  (default `python3`) instead of being hardcoded to `/usr/bin/python3.13`.
- Helper script path is now configurable via `AICL_HELPER_PATH` env var.

### Added
- `CHANGELOG.md` (this file).
- `python/docs/bridge_protocol.md` — formal spec of the editor↔compiler bridge.
- `.pre-commit-config.yaml` — ruff + black + mypy hooks.
- `[tool.ruff]` and `[tool.mypy]` sections in `python/pyproject.toml`.
- `python/tests/test_property.py` — property-based tests using Hypothesis.
- `python/src/aicl/cognet/` — placeholder module for the upcoming CogNet
  integration (see `python/docs/cognet_integration_plan.md`).
- `python/docs/cognet_integration_plan.md` — design doc for CogNet integration.
- `MANIFEST.in` for sdist packaging.
- `editor/src/lib/aicl-bridge.ts` — shared bridge module.
- GitHub Actions workflow runs on Python 3.10, 3.11, and 3.12.

### Removed
- `worklog.md`, `agent-ctx/`, `download/`, `aicl-repo/`, `.zscripts/`,
  `start-server.sh`, `watchdog.sh`, `push_to_github.sh` — workspace-specific
  clutter.
- `db/custom.db` — binary database (regenerable via `prisma db push`).
- `.env` — committed env file (replaced by `.env.example`).
- `mini-services/` — empty placeholder.
- 3 redundant PDFs in `docs/`.
- `datasets/aicl_mega_dataset.jsonl` — concatenation of others (per manifest).

## [2.1.0] — 2026-06-13

### Added
- CogNet-AICL integration bridge specification (examples 86–91).
- CogNet self-evolution examples (87, 88).
- CogNet training pipeline, evaluation, and autonomous deployment specs (89–91).
- `CONTRIBUTING.md`.
- Illustrated research paper PDF (35 pages, 10 diagrams).
- arXiv LaTeX paper (20 pages).
- Training pipeline, evaluation, and deployment specs.

### Changed
- README rewritten and expanded.
- SpecEvolver auto-fix improvements.
- Autonomous compilation loop (`Evolve` command).

## [2.0.0] — 2026-04-15

### Added
- Self-healing runtime (`runtime.py`): Risk → Recovery binding executed at runtime.
- Ownership analysis (`ownership.py`): lifetime and ownership model.
- Architecture optimiser (`auto_optimizer.py`): architecture-level optimisation passes.

## [1.2.0] — 2026-03-10

### Added
- AI-powered self-writing compiler (`ai_generator.py`).
- `aicl create` — natural-language → AICL program synthesis.
- `aicl ai-fix` — diagnose and repair broken specifications.

## [1.1.0] — 2026-02-20

### Added
- Autonomous compilation loop (`autonomous.py`).
- Pattern learning across compilation runs.
- SpecEvolver — autonomous specification repair.

## [1.0.0] — 2026-01-15

### Added
- Initial release of AICL.
- 9-stage compiler producing auditable Python code.
- Cryptographic Proof of Origin for every compilation.
- 27 keywords across 10 language levels.
- Multi-target support: Python, Rust, JavaScript, Go.
- Multi-file programs (`modules.py`).
- Cryptographic proof signing (`crypto_signing.py`).
- Specification verifier (`spec_verify.py`).
- 151-test pytest suite.
- Terminal UI based on Textual.
- 91 example programs.

[Unreleased]: https://github.com/AFKmoney/AICL/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/AFKmoney/AICL/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/AFKmoney/AICL/compare/v1.2.0...v2.0.0
[1.2.0]: https://github.com/AFKmoney/AICL/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/AFKmoney/AICL/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/AFKmoney/AICL/releases/tag/v1.0.0
