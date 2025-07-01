# 📋 Command Reference

Complete reference for all git-batch-pull commands, development tools, and utilities.

## 📋 Table of Contents

- [CLI Commands](#cli-commands)
- [Development Commands (Makefile)](#development-commands-makefile)
- [Poetry Commands](#poetry-commands)
- [Docker Commands](#docker-commands)
- [CI/CD Commands](#cicd-commands)
- [Manual Commands](#manual-commands)

---

## 🖥️ CLI Commands

### Main Commands

#### `git-batch-pull sync`
Synchronize repositories (clone if missing, pull if exists)

```bash
# Basic usage
git-batch-pull sync org|user <name>

# Options
--repos REPOS          # Comma-separated list of specific repos
--config CONFIG        # Path to configuration file
--use-ssh              # Use SSH URLs instead of HTTPS
--interactive-auth     # Prompt for username/token for HTTPS authentication
--visibility VISIBILITY # Repository visibility (all, public, private)
--max-workers N        # Number of parallel workers (default: 1)
--verbose              # Enable verbose output
--quiet                # Suppress non-error output
--dry-run              # Show what would be done without executing

# Examples
git-batch-pull sync org microsoft
git-batch-pull sync user octocat --repos "Hello-World,Spoon-Knife"
git-batch-pull sync org myorg --use-ssh --max-workers 4
git-batch-pull sync org myorg --interactive-auth --visibility private
git-batch-pull sync org myorg --config custom.toml --verbose
```

#### `git-batch-pull clone`
Clone repositories only (skip if already exists)

```bash
# Basic usage
git-batch-pull clone org|user <name>

# Same options as sync command
git-batch-pull clone org myorg --repos "repo1,repo2"
git-batch-pull clone user myuser --use-ssh
```

#### `git-batch-pull pull`
Pull updates for existing repositories

```bash
# Basic usage
git-batch-pull pull org|user <name>

# Examples
git-batch-pull pull org myorg
git-batch-pull pull user myuser --verbose
```

#### `git-batch-pull batch`
Run batch operations with configuration file

```bash
# Basic usage
git-batch-pull batch --config CONFIG_FILE

# Examples
git-batch-pull batch --config batch-config.toml
git-batch-pull batch --config configs/production.toml --verbose
```

### Utility Commands

#### Global Options
```bash
--help                 # Show help message
--version              # Show version information
--install-completion   # Install shell completion
--show-completion      # Show completion script
```

#### Environment Variables
```bash
GITHUB_TOKEN          # GitHub personal access token (required)
LOCAL_FOLDER          # Base directory for repositories (required)
REPO_VISIBILITY       # Default repository visibility (all, public, private)
```

---

## 🔨 Development Commands (Makefile)

### Setup and Installation
```bash
make help             # Show all available commands with descriptions
make install          # Complete development setup (poetry install + pre-commit)
make dev-install      # Install package in development mode with pip
make dev-uninstall    # Remove development installation
```

### Testing and Quality
```bash
make test             # Run full test suite with coverage reports
make test-fast        # Quick test run (fail on first error)
make test-all-python  # Test across all Python versions (requires pyenv)
make lint             # Run all linting checks (ruff, mypy)
make format           # Format code (black, isort, ruff)
make security         # Run security scans (bandit, safety)
make pre-commit       # Install and run all pre-commit hooks
```

### Build and Distribution
```bash
make build            # Build wheel and source distribution
make build-check      # Build package and verify with twine
make clean            # Remove all build artifacts and caches
make requirements     # Generate requirements.txt files for compatibility
```

### Performance and Benchmarking
```bash
make benchmark        # Run comprehensive performance benchmarks
```

### Docker Operations
```bash
make docker-build     # Build optimized Docker image
make docker-test      # Test Docker image functionality
```

### Maintenance and Updates
```bash
make update-deps      # Update all dependencies to latest versions
make verify-install   # End-to-end installation verification test
```

### Release Management
```bash
make release          # Complete release preparation (test + lint + security + build)
```

---

## 🎭 Poetry Commands

### Basic Operations
```bash
poetry install                 # Install all dependencies
poetry install --no-dev       # Install only production dependencies
poetry shell                   # Activate virtual environment
poetry run <command>           # Run command in virtual environment
```

### Development Commands
```bash
poetry run git-batch-pull --help      # Run CLI with poetry
poetry run pytest                     # Run tests
poetry run pytest --cov=src          # Run tests with coverage
poetry run black .                    # Format code
poetry run isort .                    # Sort imports
poetry run ruff check .               # Lint code
poetry run mypy src/                  # Type checking
poetry run bandit -r src/             # Security analysis
poetry run safety check               # Dependency vulnerability scan
```

### Build and Distribution
```bash
poetry build                   # Build wheel and source distribution
poetry publish                # Publish to PyPI (requires API token)
poetry publish --repository testpypi  # Publish to TestPyPI
poetry export -f requirements.txt --output requirements.txt  # Export requirements
```

### Environment Management
```bash
poetry env list               # List virtual environments
poetry env remove <env>       # Remove virtual environment
poetry env info               # Show environment information
poetry show                   # List installed packages
poetry show --tree            # Show dependency tree
poetry update                 # Update all dependencies
```

---

## 🐳 Docker Commands

### Basic Docker Operations
```bash
# Build images
docker build -t git-batch-pull .
docker build -f Dockerfile.dev -t git-batch-pull:dev .

# Run containers
docker run --rm git-batch-pull --help
docker run --rm git-batch-pull --version

# Interactive mode
docker run -it --rm git-batch-pull /bin/bash
docker run -it --rm git-batch-pull:dev /bin/bash
```

### Production Usage
```bash
# Run with environment variables
docker run --rm \
  -e GITHUB_TOKEN=your_token \
  -e LOCAL_FOLDER=/workspace \
  -v $(pwd):/workspace \
  git-batch-pull sync org myorg

# Background operation
docker run -d \
  --name git-batch-pull \
  -e GITHUB_TOKEN=your_token \
  -e LOCAL_FOLDER=/workspace \
  -v $(pwd):/workspace \
  git-batch-pull sync org myorg
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  git-batch-pull:
    build: .
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - LOCAL_FOLDER=/workspace
    volumes:
      - ./repos:/workspace
    command: sync org myorg
```

```bash
docker-compose up                # Run with compose
docker-compose run git-batch-pull sync org myorg  # One-off command
```

---

## 🚀 CI/CD Commands

### GitHub Actions (Automated)
```bash
# Triggered automatically on:
# - Push to main/develop branches
# - Pull requests
# - Tag creation (v*.*.*)
# - Manual workflow dispatch

# Available workflows:
# .github/workflows/ci.yml           - Continuous Integration
# .github/workflows/release.yml      - Production Release
# .github/workflows/test-release.yml - Test Release (TestPyPI)
```

### Manual CI Commands
```bash
# Run locally what CI runs
poetry install
poetry run pytest --cov=src --cov-report=xml
poetry run ruff check .
poetry run mypy src/
poetry run bandit -r src/
poetry run safety check
poetry build
poetry run twine check dist/*
```

### Release Process
```bash
# 1. Prepare release
make release

# 2. Update version
# Edit pyproject.toml version = "1.1.0"
# OR use automated tool:
bumpver update --patch  # 1.0.0 -> 1.0.1
bumpver update --minor  # 1.0.0 -> 1.1.0
bumpver update --major  # 1.0.0 -> 2.0.0

# 3. Commit and tag
git add .
git commit -m "Release v1.1.0"
git tag v1.1.0
git push origin main --tags  # Triggers release workflow
```

---

## 🔧 Manual Commands

### Testing Without Make/Poetry
```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest --cov=src --cov-report=html -v
pytest tests/test_specific.py -v
pytest -k "test_pattern" -v

# Code quality
black --check .
isort --check-only .
ruff check .
mypy src/

# Security
bandit -r src/ -f json -o bandit-report.json
safety check --json --output safety-report.json
```

### Building Without Poetry
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Install locally
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl

# Upload to PyPI
twine upload dist/*  # Production
twine upload --repository testpypi dist/*  # Test
```

### Performance Testing
```bash
# Basic benchmark
python benchmarks/performance_benchmarks.py

# Advanced benchmarks with profiling
python benchmarks/advanced_benchmarks.py

# Memory profiling (requires memory-profiler)
pip install memory-profiler
mprof run python benchmarks/advanced_benchmarks.py
mprof plot
```

---

## ⚙️ Configuration Files

### Configuration File Examples
```toml
# config.toml - Basic configuration
[general]
log_level = "INFO"
quiet = false
max_workers = 4

[github]
use_ssh = true
refetch_repos = false
entity_type = "org"
entity_name = "myorg"
repos = ["repo1", "repo2"]
```

### Environment Configuration
```bash
# .env file
GITHUB_TOKEN=ghp_your_token_here
LOCAL_FOLDER=/path/to/repos
REPO_VISIBILITY=all
LOG_LEVEL=INFO
```

---

## 🎯 Command Examples by Use Case

### For DevOps Teams
```bash
# Sync all organization repos with SSH
git-batch-pull sync org company --use-ssh --max-workers 8

# Batch operations with config
git-batch-pull batch --config devops-config.toml

# Docker deployment
docker run -d --name repo-sync \
  -e GITHUB_TOKEN=${GITHUB_TOKEN} \
  -v /repos:/workspace \
  git-batch-pull sync org company
```

### For Individual Developers
```bash
# Personal repos
git-batch-pull sync user myusername

# Specific projects
git-batch-pull clone org company --repos "project1,project2"

# Development with verbose output
git-batch-pull sync org company --verbose --dry-run
```

### For CI/CD Integration
```bash
# In CI pipeline
git-batch-pull sync org company --quiet --config ci-config.toml

# With error handling
if ! git-batch-pull sync org company; then
  echo "Repository sync failed"
  exit 1
fi
```

### For Automated Scripts
```bash
#!/bin/bash
# Daily repo sync script

export GITHUB_TOKEN=$(cat ~/.github-token)
export LOCAL_FOLDER="/backup/repos"

git-batch-pull sync org company1 --quiet
git-batch-pull sync org company2 --quiet
git-batch-pull sync user developer1 --quiet

echo "Repository sync completed at $(date)"
```

---

## 📚 Additional Resources

- **Main Documentation**: [README.md](../README.md)
- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Reference**: [API.md](API.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Examples**: [examples/](../examples/)
- **Benchmarks**: [benchmarks/](../benchmarks/)

---

**💡 Pro Tip**: Use `make help` to see all available development commands with descriptions, or `git-batch-pull --help` for CLI usage information.
