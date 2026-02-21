.PHONY: help install dev test test-cov lint format check build clean run demo doc

help:
	@echo "Pfn - Pure Functional Native"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install     Install production dependencies"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run all tests"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  lint        Run linting (ruff)"
	@echo "  format      Format code (ruff format)"
	@echo "  check       Run all checks (lint + typecheck + test)"
	@echo "  build       Build the package"
	@echo "  clean       Clean build artifacts"
	@echo "  run         Run Hello World example"
	@echo "  demo        Run full demo"
	@echo "  doc         Serve documentation locally"

PYTHON := .venv/bin/python3.13
PYTEST := .venv/bin/pytest
PIP := .venv/bin/pip

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"

PYTHON := .venv/bin/python3.13
PYTEST := .venv/bin/pytest

test:
	PYTHONPATH=src $(PYTEST) tests/unit -v

test-cov:
	PYTHONPATH=src $(PYTEST) tests/unit -v --cov=src/pfn --cov-report=term-missing

test-all:
	PYTHONPATH=src $(PYTEST) tests/ -v --cov=src/pfn --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests

format-check:
	$(PYTHON) -m ruff format --check src tests

typecheck:
	PYTHONPATH=src $(PYTHON) -m mypy src/pfn

check: lint format-check typecheck test
	@echo "All checks passed!"

build:
	$(PYTHON) -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	PYTHONPATH=src $(PYTHON) -c "from pfn.cli import main; main(['run', 'examples/hello.pfn'])"

demo:
	@echo "=== Pfn Language Demo ==="
	@echo ""
	@echo "1. Hello World:"
	PYTHONPATH=src $(PYTHON) -c "from pfn.cli import main; main(['run', 'examples/hello.pfn'])"
	@echo ""
	@echo "2. Type Checking:"
	PYTHONPATH=src $(PYTHON) -c "from pfn.cli import main; main(['check', 'examples/typed.pfn'])"
	@echo ""
	@echo "3. Generated Python:"
	PYTHONPATH=src $(PYTHON) -c "from pfn.cli import main; main(['compile', 'examples/typed.pfn'])"

doc:
	@echo "Serving docs at http://localhost:8000"
	cd docs && $(PYTHON) -m http.server 8000

ci: check
	@echo "CI passed!"
