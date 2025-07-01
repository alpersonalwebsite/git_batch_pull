# 🚀 Quick Start Guide

Get up and running with git-batch-pull in under 5 minutes!

## 📋 Table of Contents

- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [First Run](#first-run)
- [Common Usage Patterns](#common-usage-patterns)
- [Development Quick Start](#development-quick-start)
- [Essential Commands](#essential-commands)

---

## 🔧 Installation

### Option 1: Install with pipx (Recommended)
```bash
# Install pipx (if not available)
brew install pipx  # macOS
# or: python3 -m pip install --user pipx

# Install git-batch-pull
pipx install git+https://github.com/alpersonalwebsite/git_batch_pull.git
git-batch-pull sync --help
```

### Option 2: Install from PyPI (When Available)
```bash
pip install git-batch-pull
git-batch-pull sync --help
```

### Option 3: Install from Source (Latest Features)
```bash
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull
make install  # Sets up everything automatically
```

---

## ⚙️ Basic Setup

### 1. Create Configuration
```bash
# Create .env file with your GitHub token
echo "GITHUB_TOKEN=your_personal_access_token_here" > .env
echo "LOCAL_FOLDER=/path/to/your/repos" >> .env
echo "REPO_VISIBILITY=all" >> .env
```

### 2. Verify Setup
```bash
git-batch-pull --help
git-batch-pull --version
```

---

## 🏃 First Run

### Sync All Repositories for an Organization
```bash
git-batch-pull sync org your-organization-name
```

### Clone Specific Repositories
```bash
git-batch-pull clone --repos repo1,repo2,repo3 org your-org
```

### Pull Updates for Existing Repositories
```bash
git-batch-pull pull org your-org
```

### Batch Operations
```bash
git-batch-pull batch --config config.toml
```

---

## 📖 Common Usage Patterns

### For Organizations
```bash
# Sync all public repos
git-batch-pull sync org microsoft

# Sync all repos (public + private)
git-batch-pull sync org your-private-org --visibility all

# Clone only specific repos
git-batch-pull clone --repos "repo1,repo2" org your-org

# Use SSH instead of HTTPS
git-batch-pull sync org your-org --use-ssh
```

### Interactive Authentication (No Token Setup Required)
```bash
# Prompts for GitHub username and token - perfect for one-time operations
git-batch-pull sync org your-org --interactive-auth

# Interactive auth for private repositories only
git-batch-pull sync org your-org --interactive-auth --visibility private

# Interactive auth with specific repositories
git-batch-pull sync user yourusername --interactive-auth --repos "repo1,repo2"

# Test first with dry run
git-batch-pull sync org your-org --interactive-auth --dry-run
```

> **🔐 Tip**: Interactive authentication is perfect when you don't want to set up environment variables or when working on shared/temporary systems.

### For Individual Users
```bash
# Sync your personal repositories
git-batch-pull sync user your-username

# Sync someone else's public repos
git-batch-pull sync user octocat
```

### Advanced Configuration
```bash
# Use custom config file
git-batch-pull sync org your-org --config custom-config.toml

# Verbose output for debugging
git-batch-pull sync org your-org --verbose

# Quiet mode (minimal output)
git-batch-pull sync org your-org --quiet
```

---

## 🛠️ Development Quick Start

### Complete Development Setup (One Command)
```bash
# Clone, install, and set up development environment
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull
make install  # This does everything for you!
```

What `make install` does:
- ✅ Installs Poetry dependencies
- ✅ Sets up pre-commit hooks
- ✅ Configures development environment
- ✅ Runs initial tests

### Start Developing
```bash
# Activate development environment
poetry shell

# Make your changes, then test
make test-fast

# Format and lint your code
make format
make lint

# Run security checks
make security

# Build and test package
make build-check
```

---

## ⚡ Essential Commands

### Quick Reference
```bash
# Development
make install         # Complete dev setup
make test           # Run all tests
make test-fast      # Quick test run
make format         # Format code
make lint           # Check code quality
make security       # Security scans

# Build & Release
make build          # Build package
make build-check    # Build and verify
make release        # Complete release check
make clean          # Clean build artifacts

# Performance
make benchmark      # Run performance tests

# Docker
make docker-build   # Build Docker image
make docker-test    # Test Docker functionality

# Maintenance
make update-deps    # Update dependencies
make help           # Show all available commands
```

### Individual Poetry Commands
```bash
# If you prefer using Poetry directly
poetry install                    # Install dependencies
poetry run git-batch-pull --help  # Run with Poetry
poetry run pytest                 # Run tests
poetry run black .                # Format code
poetry run ruff check .           # Lint code
poetry build                      # Build package
```

### Manual Commands (Without Make)
```bash
# Testing
pytest --cov=src --cov-report=html -v
pytest --maxfail=1 -x -v

# Code Quality
black .
isort .
ruff check .
mypy src/

# Security
bandit -r src/
safety check

# Build
poetry build
twine check dist/*

# Performance
python benchmarks/advanced_benchmarks.py
```

---

## 🎯 What's Next?

### For Users
1. **Read the Full Documentation**: [README.md](../README.md)
2. **Check Examples**: [examples/](../examples/)
3. **Configure Advanced Settings**: [Configuration Guide](../README.md#configuration)
4. **Join the Community**: GitHub Discussions

### For Contributors
1. **Read Contributing Guidelines**: [CONTRIBUTING.md](../CONTRIBUTING.md)
2. **Understand the Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
3. **Set up Development Environment**: `make install`
4. **Run Tests**: `make test`
5. **Check Performance**: `make benchmark`

---

## 🆘 Need Help?

### Quick Troubleshooting
```bash
# Installation issues
pip install --upgrade pip
pip install --user git-batch-pull

# Development issues
make clean && make install

# Import issues
pip install -e .
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Permission issues
chmod +x git-batch-pull
pip install --user -e .
```

### Get Support
- 📚 **Documentation**: Check `docs/` directory
- 🐛 **Issues**: [GitHub Issues](https://github.com/alpersonalwebsite/git_batch_pull/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/alpersonalwebsite/git_batch_pull/discussions)
- 📖 **Examples**: `examples/` directory

---

## 🏆 Pro Tips

### Performance Optimization
- Use `--max-workers 4` for faster operations
- Enable SSH for private repos: `--use-ssh`
- Use `--quiet` for scripting
- Check `benchmarks/` for performance data

### Security Best Practices
- Never commit tokens to git
- Use environment variables or `.env` files
- Enable 2FA on your GitHub account
- Use SSH keys for private repositories

### Advanced Usage
- Create custom plugins (see `src/git_batch_pull/plugins/`)
- Use configuration files for complex setups
- Monitor performance with built-in benchmarks
- Integrate with CI/CD pipelines

---

**🚀 Happy coding! You're now ready to manage hundreds of repositories with ease!**
