# Installation and Development Guide

## 📋 Table of Contents

- [Quick Installation](#quick-installation)
- [Development Setup](#development-setup)
- [Build from Source](#build-from-source)
- [Docker Installation](#docker-installation)
- [Development Commands](#development-commands)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Installation

### Method 1: Using pipx (Recommended for Users)

```bash
# Install pipx if not available (macOS)
brew install pipx

# Install git-batch-pull system-wide
pipx install git+https://github.com/alpersonalwebsite/git_batch_pull.git

# Verify installation
git-batch-pull sync --help
git-batch-pull sync --version
```

### Method 2: From PyPI (When Published)

```bash
# Install the latest stable version
pip install git-batch-pull

# Verify installation
git-batch-pull --help
git-batch-pull sync --version
```

### Method 3: From GitHub Releases

```bash
# Download and install specific version
pip install https://github.com/alpersonalwebsite/git_batch_pull/releases/download/v1.0.0/git_batch_pull-1.0.0-py3-none-any.whl
```

### Method 4: Using Virtual Environment (Avoiding System Package Conflicts)

```bash
# Create isolated environment
python3 -m venv git-batch-pull-env
source git-batch-pull-env/bin/activate  # On Windows: git-batch-pull-env\Scripts\activate

# Install from GitHub
pip install git+https://github.com/alpersonalwebsite/git_batch_pull.git

# Test installation
git-batch-pull sync --help

# Create alias for easy access (optional)
echo 'alias git-batch-pull="$HOME/git-batch-pull-env/bin/git-batch-pull"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+ (3.9, 3.10, 3.11, 3.12 supported)
- Git
- Poetry (recommended) or pip

### Method 1: Poetry Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull

# 2. Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install all dependencies and setup development environment
make install
# OR manually:
poetry install --no-interaction
poetry run pre-commit install

# 4. Test the installation
poetry run git-batch-pull sync --version

# 5. Use the command during development
poetry run git-batch-pull sync user alpersonalwebsite --dry-run

# 6. Activate virtual environment (optional)
poetry shell
# Now you can use git-batch-pull directly without 'poetry run'
git-batch-pull sync --help
```

### Method 2: Traditional pip Setup

```bash
# 1. Clone and create virtual environment
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Install in development mode
pip install -e .

# 4. Verify installation
git-batch-pull sync --help
git-batch-pull sync --version
```

### Method 3: Using pipx for Development

```bash
# Clone repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull

# Install in development mode with pipx
pipx install -e .

# Test installation
git-batch-pull sync --help
```

> **📝 Note for macOS Users**: If you encounter "externally-managed-environment" errors, use pipx or virtual environments instead of system pip. This is a safety feature in newer Python installations.

---

## 🔨 Build from Source

### Using Poetry (Recommended)

```bash
# Build both wheel and source distribution
poetry build

# Check build quality
poetry run twine check dist/*

# Install locally
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl
```

### Using Standard Build Tools

```bash
# Install build dependencies
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*
```

---

## 🐳 Docker Installation

### Quick Start with Docker

```bash
# Pull and run latest image
docker pull ghcr.io/alpersonalwebsite/git-batch-pull:latest
docker run --rm git-batch-pull --help

# With environment variables
docker run --rm \
  -e GITHUB_TOKEN=your_token \
  -e LOCAL_FOLDER=/workspace \
  -v $(pwd):/workspace \
  git-batch-pull sync org myorg
```

### Build Docker Image Locally

```bash
# Build optimized production image
docker build -t git-batch-pull .

# Build development image with all tools
docker build -f Dockerfile.dev -t git-batch-pull:dev .

# Run with interactive shell
docker run -it --rm git-batch-pull:dev bash
```

---

## ⚡ Development Commands

We provide a comprehensive Makefile with 20+ commands for common development tasks:

### Setup and Installation
```bash
make install          # Full development setup with pre-commit hooks
make dev-install      # Install in development mode with pip
make dev-uninstall    # Remove development installation
```

### Testing and Quality Assurance
```bash
make test            # Run full test suite with coverage
make test-fast       # Quick test run (fail on first error)
make test-all-python # Test across all Python versions (requires pyenv)
make lint            # Run all linting checks (ruff, mypy)
make format          # Format code (black, isort, ruff)
make security        # Run security scans (bandit, safety)
make pre-commit      # Run all pre-commit hooks
```

### Build and Distribution
```bash
make build           # Build wheel and source distribution
make build-check     # Build and verify package quality
make clean           # Remove all build artifacts and caches
make requirements    # Generate requirements.txt files
```

### Performance and Benchmarking
```bash
make benchmark       # Run performance benchmarks
```

### Docker Operations
```bash
make docker-build    # Build Docker image
make docker-test     # Test Docker image functionality
```

### Maintenance
```bash
make update-deps     # Update all dependencies
make verify-install  # Test package installation end-to-end
```

### Testing Interactive Authentication

After installation, test the interactive authentication feature:

```bash
# Test with a dry run first (safe - no actual cloning)
git-batch-pull sync user yourusername --interactive-auth --dry-run

# Test with a single public repository
git-batch-pull sync user yourusername --interactive-auth --repos "repository-name"

# Test with private repositories
git-batch-pull sync org yourorg --interactive-auth --visibility private

# Test the help system to see all options
git-batch-pull sync --help
```

> **🔐 Security Note**: The interactive authentication feature securely prompts for your GitHub username and personal access token, caches them in memory during the operation, and clears them when complete. Your credentials are never stored persistently.

### Release Preparation
```bash
make release         # Complete release check (test, lint, security, build)
```

### Individual Commands
If you prefer to run commands individually:

```bash
# Testing
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing -v
poetry run pytest --maxfail=1 -x -v  # Fast testing

# Linting and Formatting
poetry run ruff check .
poetry run mypy src/
poetry run black .
poetry run isort .

# Security
poetry run bandit -r src/ -f json -o bandit-report.json
poetry run safety check --json --output safety-report.json

# Build
poetry build
poetry run twine check dist/*

# Performance
poetry run python benchmarks/advanced_benchmarks.py
```

---

## 🧪 Testing

### Test Categories

```bash
# Unit tests (fast, isolated)
pytest tests/test_*service*.py -v

# Integration tests (slower, real operations)
pytest tests/test_*integration*.py -v

# All tests with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing -v

# Performance benchmarks
python benchmarks/advanced_benchmarks.py
```

### Test Configuration

Tests are configured in `pyproject.toml`:
- Minimum coverage: 50%
- Parallel execution supported
- HTML and XML coverage reports
- Integration with CI/CD

---

## 🔧 Troubleshooting

### Common Issues

#### Poetry Installation Issues
```bash
# If Poetry is not found
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# If Poetry environment issues
poetry env remove python  # Remove existing environment
poetry install             # Recreate environment
```

#### Python Version Issues
```bash
# Check Python version
python --version

# If using pyenv
pyenv install 3.11.9
pyenv local 3.11.9
poetry env use python3.11
```

#### Import/Module Issues
```bash
# Ensure proper installation
pip install -e .
# OR
poetry install

# Check PYTHONPATH
echo $PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

#### Permission Issues
```bash
# Install to user directory
pip install --user -e .

# Fix file permissions
chmod +x scripts/*
```

#### Test Discovery Issues
```bash
# Run tests with explicit path
pytest tests/ -v

# Check test discovery
pytest --collect-only
```

#### Build Issues
```bash
# Clean and rebuild
make clean
poetry install
poetry build

# Check for conflicting dependencies
poetry show --tree
```

#### Docker Issues
```bash
# Build with no cache
docker build --no-cache -t git-batch-pull .

# Check container logs
docker run --rm git-batch-pull --version

# Interactive debugging
docker run -it --rm --entrypoint=/bin/bash git-batch-pull
```

### Getting Help

- **Documentation**: Check docs/ directory for detailed guides
- **Issues**: Create an issue on GitHub with full error logs
- **Discussions**: Use GitHub Discussions for questions
- **Debugging**: Enable debug logging with `--verbose` flag

---

## 🎯 Next Steps

After installation:

1. **Configure Environment**: Set up `.env` file with GitHub token
2. **Read Documentation**: Check `README.md` and `docs/` directory
3. **Try Examples**: Run examples from `examples/` directory
4. **Run Tests**: Ensure everything works with `make test`
5. **Performance Check**: Run `make benchmark` to verify performance

For development:
1. **Setup Pre-commit**: `make pre-commit` for code quality
2. **Read Contributing**: Check `CONTRIBUTING.md` for guidelines
3. **Architecture Overview**: See `docs/ARCHITECTURE.md`

---

## 📚 Additional Resources

- [README.md](../README.md) - Main project documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [API.md](API.md) - API reference
- [Examples](../examples/) - Usage examples
- [Benchmarks](../benchmarks/) - Performance testing
# - git_batch_pull-1.0.0-py3-none-any.whl (wheel package)
# - git_batch_pull-1.0.0.tar.gz (source distribution)

# Install the wheel package (recommended)
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl

# Or install the source distribution
pip install dist/git_batch_pull-1.0.0.tar.gz

# Use directly (available in system PATH)
git-batch-pull health
git-batch-pull main-command org myorganization
```

**Advantages:**
- ✅ System-wide installation
- ✅ No virtual environment needed
- ✅ Distributable package files
- ✅ Standard Python packaging

### 3. Direct pip Install from Source

Quick installation directly from source code:

```bash
# Clone repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git_batch_pull

# Install directly from source
pip install .

# Or install in development mode (editable)
pip install -e .

# Use the script
git-batch-pull health
```

**Advantages:**
- ✅ Quick and simple
- ✅ No build step required
- ✅ Development mode available with -e flag

### 4. Production Installation from PyPI

For production environments (when published to PyPI):

```bash
# Install from PyPI
pip install git-batch-pull

# Or install specific version
pip install git-batch-pull==1.0.0

# Verify installation
git-batch-pull --help
git-batch-pull health
```

**Advantages:**
- ✅ Official distribution
- ✅ Version management
- ✅ Dependency resolution
- ✅ Easy updates

### 5. Docker Installation

For containerized deployment and isolated environments:

```bash
# Build Docker image
docker build -t git-batch-pull .

# Run with environment variables
docker run --rm \
  -e GITHUB_TOKEN=your_token \
  git-batch-pull health

# Run with volume mount for local repositories
docker run --rm \
  -v "$PWD:/workspace" \
  -e GITHUB_TOKEN=your_token \
  git-batch-pull main-command org myorganization

# Interactive mode
docker run --rm -it \
  -v "$PWD:/workspace" \
  -e GITHUB_TOKEN=your_token \
  git-batch-pull bash
```

**Advantages:**
- ✅ Complete isolation
- ✅ Reproducible environment
- ✅ No local dependencies
- ✅ Easy CI/CD integration

## Verification and Testing

After any installation method, verify the installation:

### Health Check
```bash
git-batch-pull health
```

Expected output:
```
🏥 Git Batch Pull Health Check
========================================
✅ python_version: Python 3.10.13
✅ git_installation: Git installed: git version 2.39.5
✅ network_connectivity: Network connectivity available
✅ github_api_access: GitHub API accessible
✅ disk_space: Sufficient disk space: 286.8GB free
✅ permissions: File system permissions OK

🟢 Overall Status: ALL SYSTEMS GO
```

### Command Help
```bash
git-batch-pull --help
git-batch-pull main-command --help
```

### Test Run (Dry Mode)
```bash
# Test with a public organization (no token needed for public repos)
git-batch-pull main-command org microsoft --dry-run
```

## Build Process Details

### Using Poetry Build

Poetry uses the modern Python packaging standards:

```bash
# Build both wheel and source distribution
poetry build

# Build only wheel
poetry build --format=wheel

# Build only source distribution
poetry build --format=sdist
```

**Generated Files:**
- `dist/git_batch_pull-1.0.0-py3-none-any.whl` - Universal wheel package
- `dist/git_batch_pull-1.0.0.tar.gz` - Source distribution

### Build Configuration

The build is configured in `pyproject.toml`:

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
git-batch-pull = "git_batch_pull.cli:app"
```

### Entry Points

The package provides a console script entry point:
- Command: `git-batch-pull`
- Module: `git_batch_pull.cli:app`
- Type: Typer CLI application

## Development Build Workflow

For developers working on the codebase:

```bash
# 1. Set up development environment
poetry install --with dev

# 2. Make code changes

# 3. Test changes in development mode
poetry run git-batch-pull health

# 4. Run tests
poetry run pytest

# 5. Build and test package
poetry build
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl --force-reinstall

# 6. Final verification
git-batch-pull health

# 7. Clean up (optional)
pip uninstall git-batch-pull
```

## Troubleshooting

### Common Issues

#### Command Not Found Error

**Problem**: `zsh: command not found: git-batch-pull` or `bash: git-batch-pull: command not found`

**Cause**: The package is not installed globally or not in your system PATH.

**Solutions**:

```bash
# Option 1: Install globally (recommended)
cd /path/to/git_batch_pull
pip install .

# Option 2: Use Poetry from project directory
cd /path/to/git_batch_pull
poetry run git-batch-pull health

# Option 3: Activate Poetry shell
cd /path/to/git_batch_pull
poetry shell
git-batch-pull health
```

**Verification**:
```bash
# Check if command is available
which git-batch-pull

# Should show something like:
# /Users/username/Library/Python/3.9/bin/git-batch-pull

# Test from any directory
cd /tmp
git-batch-pull health
```

#### Missing Dependencies
```bash
# If you get import errors, reinstall with all dependencies
pip install --force-reinstall git-batch-pull
```

#### Permission Issues
```bash
# Install to user directory if system install fails
pip install --user dist/git_batch_pull-1.0.0-py3-none-any.whl
```

#### Path Issues
```bash
# Ensure the script is in your PATH
which git-batch-pull

# If not found, check Python's script directory
python -m site --user-base
```

#### Virtual Environment Issues
```bash
# Ensure you're in the correct virtual environment
which python
which pip

# Activate Poetry environment
poetry shell
```

### Verification Commands

```bash
# Check installed package
pip show git-batch-pull

# Check entry points
pip show -f git-batch-pull | grep console_scripts

# Check import
python -c "import git_batch_pull; print('Import successful')"

# Check CLI availability
which git-batch-pull
git-batch-pull --version
```

## Distribution

### Publishing to PyPI

```bash
# Build the package
poetry build

# Publish to PyPI (requires credentials)
poetry publish

# Or publish to test PyPI first
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi
```

### Creating Releases

```bash
# Tag the release
git tag v1.0.0
git push --tags

# Create GitHub release
gh release create v1.0.0 \
  --title "Version 1.0.0" \
  --notes "Initial release" \
  dist/git_batch_pull-1.0.0-py3-none-any.whl \
  dist/git_batch_pull-1.0.0.tar.gz
```

## Understanding Usage Patterns

### Poetry vs Global Installation

| Installation Method | Command Usage | Availability | Use Case |
|-------------------|---------------|--------------|----------|
| **Poetry Development** | `poetry run git-batch-pull` | Only in project directory | Development, testing |
| **Poetry Shell** | `poetry shell` then `git-batch-pull` | While shell is active | Development sessions |
| **Global pip Install** | `git-batch-pull` | ✅ **Available everywhere** | Daily usage, production |

### When to Use Each Method

#### Use Poetry (`poetry run git-batch-pull`)
- ✅ **Development and testing**
- ✅ **Working on the codebase**
- ✅ **Isolated environment**
- ❌ **Only works in project directory**

#### Use Global Installation (`pip install .`)
- ✅ **Daily usage from any directory**
- ✅ **Production environments**
- ✅ **CI/CD pipelines**
- ✅ **Available system-wide**

### Quick Setup for Daily Use

```bash
# 1. Clone repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git_batch_pull

# 2. Install globally
pip install .

# 3. Use from anywhere
cd ~/your-project
git-batch-pull health
git-batch-pull main-command org your-organization
```
