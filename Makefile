# AICL — Makefile
# Common dev tasks. Requires Python 3.10+ and (optionally) Node/Bun for the editor.

PYTHON ?= python3
PIP    ?= pip3
NODE   ?= bun   # change to `npm` or `pnpm` if preferred

.PHONY: help install install-python install-editor test lint clean dev editor dev-editor build-editor

help:
	@echo "AICL — common tasks"
	@echo ""
	@echo "  make install          Install both Python package and web editor deps"
	@echo "  make install-python   Install AICL Python package (editable) + TUI extras"
	@echo "  make install-editor   Install web editor Node dependencies"
	@echo "  make test             Run the AICL Python test suite"
	@echo "  make lint             Lint Python (pyflakes) + editor (eslint)"
	@echo "  make dev              Run Python TUI"
	@echo "  make editor           Run web editor dev server (http://localhost:3000)"
	@echo "  make build-editor     Production build of the web editor"
	@echo "  make clean            Remove build/test artifacts"

install: install-python install-editor

install-python:
	$(PIP) install -e ".[tui]"
	$(PIP) install pytest

install-editor:
	$(NODE) install

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m pyflakes src/aicl/ scripts/ tools/ || true
	cd editor 2>/dev/null && $(NODE) run lint || $(NODE) run lint || true

dev:
	$(PYTHON) -m aicl tui

editor:
	$(NODE) run dev

dev-editor: editor

build-editor:
	$(NODE) run build

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf output/ .next/ out/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
