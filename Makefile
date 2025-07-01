# Makefile for git-batch-pull development

.PHONY: help install test lint format security build clean docs pre-commit release

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies and project"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  security    - Run security checks"
	@echo "  build       - Build the package"
	@echo "  clean       - Clean build artifacts"
	@echo "  docs        - Build documentation"
	@echo "  pre-commit  - Install pre-commit hooks"
	@echo "  release     - Prepare for release (test, build, check)"
	@echo "  benchmark   - Run performance benchmarks"
	@echo "  changes     - Check what has changed for changelog"
	@echo "  changelog   - Open changelog workflow documentation"

# Development setup
install:
	poetry install --no-interaction
	poetry run pre-commit install

# Testing
test:
	poetry run pytest --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml -v

test-fast:
	poetry run pytest --maxfail=1 -x -v

# Code quality
lint:
	poetry run ruff check .
	poetry run mypy src/

format:
	poetry run black .
	poetry run isort .
	poetry run ruff format .

# Security
security:
	poetry run bandit -r src/ -f json -o bandit-report.json
	poetry run safety check --json --output safety-report.json

# Build and packaging
build:
	poetry build

build-check:
	poetry build
	poetry run twine check dist/*

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	mkdocs build
	mkdocs serve

# Pre-commit
pre-commit:
	poetry run pre-commit install
	poetry run pre-commit run --all-files

# Release preparation
release: clean test lint security build-check
	@echo "✅ All checks passed! Ready for release."
	@echo "Next steps:"
	@echo "1. Update version in pyproject.toml"
	@echo "2. Update CHANGELOG.md"
	@echo "3. Commit changes: git commit -am 'Release vX.Y.Z'"
	@echo "4. Create tag: git tag vX.Y.Z"
	@echo "5. Push: git push origin main --tags"

# Performance benchmarks
benchmark:
	poetry run python benchmarks/performance_benchmarks.py

# Development utilities
dev-install:
	pip install -e .

dev-uninstall:
	pip uninstall -y git-batch-pull

# Test different Python versions (requires pyenv)
test-all-python:
	@echo "Testing with Python 3.9..."
	pyenv local 3.9.18 && poetry run pytest --maxfail=1 -x
	@echo "Testing with Python 3.10..."
	pyenv local 3.10.14 && poetry run pytest --maxfail=1 -x
	@echo "Testing with Python 3.11..."
	pyenv local 3.11.9 && poetry run pytest --maxfail=1 -x
	@echo "Testing with Python 3.12..."
	pyenv local 3.12.4 && poetry run pytest --maxfail=1 -x

# Generate requirements.txt for compatibility
requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Docker builds
docker-build:
	docker build -t git-batch-pull .

docker-test:
	docker run --rm git-batch-pull --help

# Maintenance
update-deps:
	poetry update
	poetry run pre-commit autoupdate

# Package verification
verify-install:
	pip install dist/*.whl
	git-batch-pull --help
	git-batch-pull --version
	pip uninstall -y git-batch-pull

# Check what has changed for changelog
changes:
	@echo "🔍 Analyzing changes for changelog updates..."
	@python3 scripts/update_changelog.py
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. Review changelog_suggestions.md"
	@echo "  2. Update CHANGELOG.md manually"
	@echo "  3. Commit changelog updates"

# Open changelog workflow documentation
changelog:
	@echo "📖 Opening changelog documentation..."
	@echo "CHANGELOG.md: Current changelog"
	@echo "docs/CHANGELOG_MANAGEMENT.md: Workflow guide"
	@echo "changelog_suggestions.md: Latest suggestions (if available)"
	@echo ""
	@echo "💡 Quick commands:"
	@echo "  make changes     - Analyze changes and get suggestions"
	@echo "  make release     - Full release preparation"
