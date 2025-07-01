# Contributing to git-batch-pull

Thank you for considering contributing to git-batch-pull! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.9+
- Git
- GitHub account

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull

# Set up development environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Verify setup
pytest
git-batch-pull --health
```

## 🔄 Development Workflow

### 1. **Before You Start**
- Check existing [issues](https://github.com/alpersonalwebsite/git_batch_pull/issues) and [discussions](https://github.com/alpersonalwebsite/git_batch_pull/discussions)
- Open an issue to discuss your idea before submitting a large PR
- Fork the repository and create a feature branch

### 2. **Branch Naming**
```bash
# Feature branches
git checkout -b feature/your-feature-name

# Bug fixes
git checkout -b fix/bug-description

# Documentation
git checkout -b docs/improvement-description
```

### 3. **Development Process**
- Write clear, modular, and well-documented code
- Follow the existing code style and architecture
- Add or update tests for your changes
- Update documentation as needed

### 4. **Pre-submission Checklist**
Run these commands before submitting your PR:

```bash
# Code formatting and linting
ruff check .
ruff format .

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Tests with coverage
pytest --cov=src --cov-report=term --cov-report=html

# Build verification
python -m build

# Distribution check
twine check dist/*
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interaction
├── end_to_end/     # End-to-end workflow tests
└── fixtures/       # Shared test fixtures and data
```

### Writing Tests
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Property-Based Tests**: Use Hypothesis for edge case discovery

### Test Coverage Targets
- **Minimum**: 80% overall coverage
- **New Code**: 90% coverage for new features
- **Critical Paths**: 95% coverage for security and core logic

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_git_service.py

# With coverage
pytest --cov=src --cov-report=html

# Performance benchmarks
python benchmarks/performance_benchmarks.py

# Integration tests only
pytest tests/integration/

# Parallel execution
pytest -n auto
```

## 📝 Code Style Guidelines

### Python Style
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type hints everywhere
- **Docstrings**: Google-style docstrings for all public APIs
- **Error Handling**: Explicit exception handling with custom exceptions

### Code Organization
```python
# File structure example
"""Module docstring explaining purpose."""

import standard_library
import third_party_packages

from .local_modules import LocalClass

# Constants
CONSTANT_VALUE = "value"

class ExampleClass:
    """Class docstring."""

    def __init__(self, param: str) -> None:
        """Initialize with parameter."""
        self.param = param

    def public_method(self) -> str:
        """Public method with docstring."""
        return self._private_method()

    def _private_method(self) -> str:
        """Private method with docstring."""
        return f"processed: {self.param}"
```

### Documentation Style
```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        GitOperationError: When git operation fails

    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
    """
```

## 🏗️ Architecture Guidelines

### Service Layer Pattern
- **Services**: Business logic and external integrations
- **Models**: Data structures and domain objects
- **Handlers**: Cross-cutting concerns (logging, errors)
- **Security**: Input validation and safe operations

### Dependency Injection
```python
# Use the service container for dependency management
from git_batch_pull.services import ServiceContainer

container = ServiceContainer()
git_service = container.get_git_service()
```

### Error Handling
```python
# Use custom exceptions
from git_batch_pull.exceptions import GitOperationError

try:
    git_service.clone_repository(repo)
except GitOperationError as e:
    logger.error(f"Failed to clone {repo.name}: {e}")
    raise
```

## 🔌 Plugin Development

### Creating a Plugin
```python
# src/my_plugin.py
from git_batch_pull.plugins import PluginBase

class MyPlugin(PluginBase):
    """Custom plugin for special repository handling."""

    name = "my-plugin"
    version = "1.0.0"

    def process_repository(self, repo: Repository) -> bool:
        """Process repository with custom logic."""
        # Your custom logic here
        return True
```

### Registering a Plugin
```toml
# pyproject.toml
[project.entry-points.git_batch_pull_plugins]
my-plugin = "my_plugin:MyPlugin"
```

## 📖 Documentation

### Types of Documentation
- **README.md**: Main project documentation
- **API Documentation**: Inline docstrings
- **Architecture Documentation**: Design decisions and patterns
- **User Guides**: Step-by-step instructions
- **Migration Guides**: Version upgrade instructions

### Documentation Standards
- Clear, concise language
- Code examples for all features
- Screenshots for CLI tools
- Keep documentation up-to-date with code changes

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Run `git-batch-pull --health` to gather diagnostics
3. Try with `--verbose` for detailed output
4. Test with minimal reproduction case

### Bug Report Template
```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.7]
- git-batch-pull: [e.g., 1.0.0]
- Git: [e.g., 2.34.1]

**Additional Context**
- Health check output: `git-batch-pull --health`
- Verbose logs: `git-batch-pull --verbose ...`
```

## 🚀 Feature Requests

### Before Requesting
- Check existing feature requests
- Consider if it fits the project scope
- Think about implementation complexity

### Feature Request Template
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other ways to solve this problem

**Additional Context**
Examples, mockups, related issues
```

## 📋 Pull Request Process

### PR Checklist
- [ ] Branch is up-to-date with main
- [ ] All tests pass
- [ ] Code coverage meets requirements
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Security scan passes
- [ ] Performance impact considered

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

## 🏆 Recognition

### Contributors
All contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- GitHub releases
- Project documentation

### Types of Contributions
- Code contributions
- Documentation improvements
- Bug reports and testing
- Feature suggestions
- Community support

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: For security issues or private concerns

### Response Times
- **Bug Reports**: 48 hours
- **Feature Requests**: 1 week
- **Pull Requests**: 72 hours for initial review

## 📄 License

By contributing to git-batch-pull, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to git-batch-pull! 🎉

## Branching Model
- Use feature branches for all changes (e.g., `feature/xyz`, `bugfix/abc`).
- Submit pull requests to `main`.

## Code of Conduct
- See `CODE_OF_CONDUCT.md` for community standards.

## Security
- Never commit secrets or sensitive data.
- Report vulnerabilities as described in `SECURITY.md`.
