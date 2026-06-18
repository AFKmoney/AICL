# AICL — Makefile
# Common dev tasks. Requires Python 3.10+ and (optionally) Bun/Node for the editor.
#
# Quick start:
#   make install      Install everything (Python pkg + editor deps + pre-commit)
#   make test         Run the AICL Python test suite
#   make editor       Run the web editor dev server (http://localhost:3000)
#   make lint         Run all linters (ruff, black --check, mypy, eslint, tsc)

PYTHON ?= python3
PIP    ?= pip3
NODE   ?= bun

.PHONY: help install install-python install-editor install-precommit test test-property lint lint-python lint-editor type-check format dev editor dev-editor build-editor build-python bump-version clean clean-all

help:
	@echo "AICL — common tasks"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install Python pkg + editor deps + pre-commit hooks"
	@echo "  make install-python       Install AICL Python package (editable) + dev extras"
	@echo "  make install-editor       Install web editor Node dependencies"
	@echo "  make install-precommit    Install pre-commit git hooks"
	@echo ""
	@echo "Quality:"
	@echo "  make test                 Run the AICL Python test suite (151 tests)"
	@echo "  make test-property        Run only the Hypothesis property tests"
	@echo "  make lint                 Run all linters (ruff, black --check, mypy, eslint, tsc)"
	@echo "  make format               Auto-format Python (black + ruff --fix)"
	@echo "  make type-check           Type-check Python (mypy) and TypeScript (tsc)"
	@echo ""
	@echo "Run:"
	@echo "  make dev                  Launch the AICL terminal UI"
	@echo "  make editor               Run web editor dev server (http://localhost:3000)"
	@echo ""
	@echo "Build:"
	@echo "  make build-python         Build Python sdist + wheel (for PyPI)"
	@echo "  make build-editor         Production build of the web editor"
	@echo "  make bump-version NEW_VERSION=X.Y.Z   Bump version in pyproject.toml + __init__.py"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove build/test artifacts"
	@echo "  make clean-all            clean + remove node_modules + .venv"

install: install-python install-editor install-precommit

install-python:
	cd python && $(PIP) install -e ".[tui,dev]"

install-editor:
	cd editor && $(NODE) install

install-precommit:
	pre-commit install
	@echo "pre-commit hooks installed. Run 'pre-commit run --all-files' to test."

test:
	cd python && $(PYTHON) -m pytest tests/ -v

test-property:
	cd python && $(PYTHON) -m pytest tests/test_property.py -v

lint: lint-python lint-editor

lint-python:
	cd python && ruff check src/ tests/ tools/ scripts/
	cd python && black --check src/ tests/ tools/ scripts/
	cd python && mypy

lint-editor:
	cd editor && $(NODE) run lint
	cd editor && $(NODE) run type-check

type-check:
	cd python && mypy
	cd editor && $(NODE) run type-check

format:
	cd python && black src/ tests/ tools/ scripts/
	cd python && ruff check --fix src/ tests/ tools/ scripts/

dev:
	cd python && $(PYTHON) -m aicl tui

editor:
	cd editor && $(NODE) run dev

dev-editor: editor

build-python:
	cd python && $(PYTHON) -m build

build-editor:
	cd editor && $(NODE) run build

bump-version:
	@if [ -z "$(NEW_VERSION)" ]; then \
		echo "Error: NEW_VERSION is required. Usage: make bump-version NEW_VERSION=X.Y.Z"; \
		exit 1; \
	fi
	@echo "Bumping version to $(NEW_VERSION)..."
	@# Update python/pyproject.toml
	sed -i.bak 's/^version = ".*"/version = "$(NEW_VERSION)"/' python/pyproject.toml && rm python/pyproject.toml.bak
	@# Update python/src/aicl/__init__.py
	sed -i.bak 's/^__version__ = .*/__version__ = "$(NEW_VERSION)"/' python/src/aicl/__init__.py && rm python/src/aicl/__init__.py.bak
	@echo ""
	@echo "Version bumped to $(NEW_VERSION) in:"
	@echo "  - python/pyproject.toml"
	@echo "  - python/src/aicl/__init__.py"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Update CHANGELOG.md (add a new section for v$(NEW_VERSION))"
	@echo "  2. make test && make lint"
	@echo "  3. make build-python"
	@echo "  4. twine check python/dist/*"
	@echo "  5. See RELEASING.md for the full release process"

clean:
	find python -type d -name __pycache__ -prune -exec rm -rf {} +
	find python -type d -name .pytest_cache -prune -exec rm -rf {} +
	find python -type d -name .mypy_cache -prune -exec rm -rf {} +
	find python -type d -name .ruff_cache -prune -exec rm -rf {} +
	rm -rf python/build python/dist python/src/*.egg-info
	rm -rf python/output
	rm -rf editor/.next editor/out

clean-all: clean
	rm -rf editor/node_modules
	rm -rf python/.venv .venv
