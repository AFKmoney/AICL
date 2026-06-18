# AICL — Python package

This directory contains the AICL language implementation. See the
[top-level README](../README.md) for project overview, install instructions,
and feature list.

## What's here

- [`src/aicl/`](./src/aicl/) — Core implementation (parser, compiler, runtime, CLI, TUI)
- [`spec/grammar.md`](./spec/grammar.md) — Formal BNF grammar
- [`examples/`](./examples/) — 91 AICL programs (`showcase/` + `archive/`)
- [`tests/`](./tests/) — 156 pytest tests (incl. 5 Hypothesis property tests)
- [`tools/`](./tools/) — Developer utilities (dataset gen, proof verifier, AI bridge)
- [`scripts/aicl_helper.py`](./scripts/aicl_helper.py) — JSON-over-stdio bridge for the web editor
- [`datasets/`](./datasets/) — JSONL training sets for LLM fine-tuning
- [`docs/`](./docs/) — Bridge protocol, CogNet integration plan
- [`pyproject.toml`](./pyproject.toml) — Package metadata, ruff/black/mypy config
- [`MANIFEST.in`](./MANIFEST.in) — Sdist packaging manifest

## Install

```bash
pip install -e ".[tui,dev]"
```

See [top-level Makefile](../Makefile) for the full set of `make` targets.

## Test

```bash
pytest tests/ -v
```

## Use

```bash
aicl --help
aicl compile examples/showcase/01_blue_square.aicl
aicl tui   # interactive terminal UI
```
