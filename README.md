[![CI](https://github.com/alpersonalwebsite/git_batch_pull/actions/workflows/ci.yml/badge.svg)](https://github.com/alpersonalwebsite/git_batch_pull/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/alpersonalwebsite/git_batch_pull/branch/main/graph/badge.svg)](https://codecov.io/gh/alpersonalwebsite/git_batch_pull)
[![PyPI version](https://badge.fury.io/py/git-batch-pull.svg)](https://badge.fury.io/py/git-batch-pull)
[![Python Version](https://img.shields.io/pypi/pyversions/git-batch-pull)](https://pypi.org/project/git-batch-pull/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/git-batch-pull)](https://pepy.tech/project/git-batch-pull)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Semantic Versioning](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versioning-e10079.svg)](https://semver.org/)

# Git Batch Pull

**Enterprise-grade GitHub repository batch processing tool with modern architecture, comprehensive security, and advanced automation capabilities.**

A professional Python CLI application designed for DevOps teams, developers, and organizations managing multiple GitHub repositories. Built with modern software engineering practices, comprehensive security measures, and scalable architecture.

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [🚀 Quick Start](docs/QUICK_START.md) | Get started in under 5 minutes |
| [📋 Installation Guide](docs/INSTALLATION.md) | Complete installation and setup instructions |
| [� SSH Guide](docs/SSH_GUIDE.md) | Complete SSH setup and usage guide |
| [�📖 Command Reference](docs/COMMAND_REFERENCE.md) | Complete command reference and examples |
| [🏗️ Architecture Guide](docs/ARCHITECTURE.md) | Technical architecture and design |
| [🔌 API Reference](docs/API.md) | Complete API documentation |
| [🤝 Contributing Guide](CONTRIBUTING.md) | Development and contribution guidelines |
| [🔒 Security Guide](SECURITY.md) | Security features and best practices |
| [📦 Migration Guide](MIGRATION.md) | Upgrading from older versions |

---

## Table of Contents

- [Key Features](#key-features)
- [Quick Installation](#quick-installation)
- [Basic Usage](#basic-usage)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Development](#development)
- [Performance & Monitoring](#performance--monitoring)
- [Docker Support](#docker-support)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture Overview

Git Batch Pull follows a **layered architecture** with clear separation of concerns, dependency injection, and modern Python best practices.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (Typer)                       │
├─────────────────────────────────────────────────────────────┤
│                   Handler Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Logging Handler │  │  Error Handler  │  │   Health    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Core Business Logic                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Batch Processor │  │Protocol Handler │  │ Plugin Mgr  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  GitHub Service │  │   Git Service   │  │   Repo      │  │
│  │                 │  │                 │  │  Service    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Security Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Token Manager   │  │ Path Validator  │  │ Subprocess  │  │
│  │                 │  │                 │  │   Runner    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │     Models      │  │   Exceptions    │  │   Config    │  │
│  │  (Dataclasses)  │  │   Hierarchy     │  │   System    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

- **Dependency Injection**: ServiceContainer manages all dependencies
- **Service Layer**: Clean separation of business logic from external APIs
- **Repository Pattern**: Abstracted data access and storage
- **Strategy Pattern**: Pluggable protocol handling and processing strategies
- **Factory Pattern**: Dynamic service and handler creation
- **Command Pattern**: CLI commands with validation and error handling

---

## Key Features

### 🏗️ **Enterprise Architecture**
- **Modular Design**: 7-layer architecture with clear boundaries
- **Type Safety**: Complete type annotations with runtime validation
- **Dependency Injection**: Testable, maintainable, and extensible
- **Service Layer**: Clean abstraction of external integrations

### 🔒 **Security First**
- **Secure Token Management**: Keyring integration with automatic encryption
- **Path Validation**: Prevention of directory traversal attacks
- **Safe Subprocess Execution**: Sandboxed git operations
- **Input Sanitization**: Comprehensive validation throughout

### ⚡ **Performance & Reliability**
- **Parallel Processing**: Concurrent repository operations with rate limiting
- **Health Monitoring**: Built-in system diagnostics and health checks
- **Error Recovery**: Graceful failure handling with detailed reporting
- **Caching**: Intelligent repository metadata caching

### 🔧 **Developer Experience**
- **Modern CLI**: Typer-based interface with rich help and autocompletion
- **Comprehensive Logging**: Structured logging with multiple output formats
- **Plugin System**: Extensible architecture with Python entry points
- **Configuration Management**: TOML, environment, and CLI configuration

---

## 🚀 Quick Installation

### Install with pipx (Recommended)
```bash
# Install pipx (if not available)
brew install pipx  # macOS
# or: python3 -m pip install --user pipx

# Install git-batch-pull
pipx install git+https://github.com/alpersonalwebsite/git_batch_pull.git
git-batch-pull sync --help
```

### Install from PyPI (When Available)
```bash
pip install git-batch-pull
git-batch-pull sync --help
```

### Development Installation
```bash
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git-batch-pull
make install  # Complete development setup
```

**📚 [Complete Installation Guide →](docs/INSTALLATION.md)**

---

## ⚡ Basic Usage

### 1. Configure Environment
```bash
# Set up your GitHub token
export GITHUB_TOKEN="your_personal_access_token"
export LOCAL_FOLDER="/path/to/your/repos"
```

### 2. Sync Organization Repositories
```bash
# Sync all repositories for an organization
git-batch-pull sync org microsoft

# Sync specific repositories
git-batch-pull sync org myorg --repos "repo1,repo2,repo3"

# Use SSH instead of HTTPS
git-batch-pull sync org myorg --use-ssh
```

### 3. Advanced Operations
```bash
# Batch operations with configuration
git-batch-pull batch --config config.toml

# Clone only (skip existing)
git-batch-pull clone org myorg

# Pull updates only
git-batch-pull pull org myorg
```

**📖 [Complete Command Reference →](docs/COMMAND_REFERENCE.md)**

---

## 🔐 SSH Usage

Git Batch Pull supports **SSH authentication** for enhanced security and performance. SSH is recommended for:
- **Private repositories**
- **Large batch operations**
- **Better security** (no token management for git operations)
- **Faster authentication**

### Quick SSH Setup
```bash
# 1. Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output and add to: GitHub → Settings → SSH and GPG keys

# 4. Test connection
ssh -T git@github.com
```

### Using SSH with git-batch-pull
```bash
# Use SSH flag with any command
git-batch-pull sync org myorg --ssh
git-batch-pull clone org myorg --repos "repo1,repo2" --ssh

# Or configure in config.toml
echo 'use_ssh = true' >> config.toml
git-batch-pull sync org myorg --config config.toml
```

**📖 Complete SSH Guide:** [docs/SSH_GUIDE.md](docs/SSH_GUIDE.md)

---

## 🛠️ Development

### Quick Development Setup
```bash
# Complete development environment setup
make install

# Run tests
make test

# Code quality checks
make lint format security

# Build package
make build

# Performance benchmarks
make benchmark
```

### Available Make Commands
```bash
make help           # Show all available commands
make install        # Complete development setup
make test          # Run test suite with coverage
make test-fast     # Quick test run
make lint          # Code quality checks
make format        # Code formatting
make security      # Security scans
make build         # Build package
make benchmark     # Performance tests
make docker-build  # Build Docker image
make release       # Complete release preparation
```

**🤝 [Contributing Guide →](CONTRIBUTING.md)**

### Method 2: Build and Install with pip

For system-wide installation or distribution:

```bash
# Clone and build
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git_batch_pull

# Build the package
poetry build

# Install the built wheel
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl

# Or install the source distribution
pip install dist/git_batch_pull-1.0.0.tar.gz

# Use directly (available in PATH)
git-batch-pull health
```

### Method 3: Direct pip Install from Source

Quick installation from source:

```bash
# Clone repository
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git_batch_pull

# Install directly
pip install .

# Use the script
git-batch-pull health
```

### Method 4: Production Installation from PyPI

```bash
# Install from PyPI (when published)
pip install git-batch-pull

# Verify installation
git-batch-pull --help
git-batch-pull health
```

### Method 5: Docker Installation

For containerized deployment:

```bash
# Build container
docker build -t git-batch-pull .

# Run with volume mount
docker run --rm -v "$PWD:/workspace" \
  -e GITHUB_TOKEN=your_token \
  git-batch-pull sync org myorg
```

### Verification

After installation, verify everything works:

```bash
# Run health check
git-batch-pull health

# Check available commands
git-batch-pull --help

# Test with dry run
git-batch-pull sync org microsoft --dry-run
```

### 📋 **Usage Summary**

| Installation Method | Command | Available From |
|-------------------|---------|----------------|
| **Poetry Development** | `poetry run git-batch-pull` | Project directory only |
| **Global Installation** | `git-batch-pull` | ✅ **Any directory** |
| **Poetry Shell** | `poetry shell` → `git-batch-pull` | While shell active |

**💡 Tip**: For daily use, choose **Method 2 or 3** (global installation) so you can run `git-batch-pull` from any directory without the `poetry run` prefix.

---

## Quick Start

### 1. **System Health Check**
```bash
# Verify all dependencies and configuration
git-batch-pull health
```

### 2. **Configure Authentication**
```bash
# Method 1: Environment variable
export GITHUB_TOKEN=ghp_your_personal_access_token

# Method 2: Secure keyring storage
git-batch-pull sync org myorg --use-keyring

# Method 3: Interactive authentication (prompts for credentials)
git-batch-pull sync org myorg --interactive-auth

# Method 4: Configuration file
echo 'github_token = "ghp_your_token"' > config.toml
```

> **🔐 Interactive Authentication**: When using `--interactive-auth` with HTTPS, you'll be prompted once for your GitHub username and personal access token. These credentials will be used for all repositories in the sync operation and cleared from memory when complete.

### 3. **Basic Usage**
```bash
# Clone all repositories for an organization
git-batch-pull sync org myorganization

# Clone all repositories for a user
git-batch-pull sync user username

# Use SSH URLs with specific repositories
git-batch-pull sync org myorg --ssh --repos "repo1,repo2,repo3"

# Alternative commands (all do the same thing)
git-batch-pull clone org myorg     # Git-familiar naming
git-batch-pull pull org myorg      # Git-familiar naming
git-batch-pull batch org myorg     # Descriptive naming
```

### 4. **Advanced Usage**
```bash
# Dry run with detailed logging
git-batch-pull sync org myorg --dry-run --log-level DEBUG

# Interactive HTTPS authentication for private repositories
git-batch-pull sync org myorg --interactive-auth --visibility private

# Parallel processing with error logging
git-batch-pull sync org myorg \
  --max-workers 4 \
  --error-log errors.log \
  --log-file batch.log

# Exclude archived and forked repositories
git-batch-pull sync org myorg \
  --exclude-archived \
  --exclude-forks \
  --refetch
```

---

## CLI Reference

### Repository Sync Commands

All commands perform the same function with different names for familiarity:

```bash
git-batch-pull sync [OPTIONS] ENTITY_TYPE ENTITY_NAME     # Primary command
git-batch-pull clone [OPTIONS] ENTITY_TYPE ENTITY_NAME    # Git-familiar
git-batch-pull pull [OPTIONS] ENTITY_TYPE ENTITY_NAME     # Git-familiar
git-batch-pull batch [OPTIONS] ENTITY_TYPE ENTITY_NAME    # Descriptive
```

#### Arguments
- `ENTITY_TYPE`: Either 'user' or 'org'
- `ENTITY_NAME`: GitHub username or organization name

#### Examples
```bash
# Basic usage with different command names
git-batch-pull sync org mycompany
git-batch-pull clone user username
git-batch-pull pull org mycompany --ssh
git-batch-pull batch user username --dry-run
```

#### Options
| Option | Description | Default |
|--------|-------------|---------|
| `--ssh/--https` | Use SSH URLs for cloning | HTTPS |
| `--repos TEXT` | Comma-separated list of specific repositories | All repos |
| `--repos-file PATH` | File containing repository names (one per line) | None |
| `--exclude-archived` | Skip archived repositories | Include all |
| `--exclude-forks` | Skip forked repositories | Include all |
| `--refetch` | Force refresh of repository list from GitHub | Use cache |
| `--dry-run` | Preview actions without making changes | Execute |
| `--max-workers INT` | Maximum parallel operations | 1 |
| `--use-keyring` | Store/retrieve token securely using keyring | Environment |
| `-c, --config PATH` | Path to configuration file | Auto-detect |
| `-l, --log-level LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `--log-file PATH` | Write logs to specified file | Console only |
| `--error-log PATH` | Write detailed error logs | None |
| `-q, --quiet` | Suppress non-error output | Verbose |
| `--plain` | Disable colored output | Colored |

### Health Command
```bash
git-batch-pull health [OPTIONS]
```

Performs comprehensive system diagnostics:
- Python version compatibility
- Git installation and version
- Network connectivity
- GitHub API accessibility
- Disk space availability
- File system permissions
- Configuration validation

### Global Options
| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version information |
| `--install-completion` | Install shell completion |
| `--show-completion` | Show completion script |

---
## Configuration

Git Batch Pull supports multiple configuration methods with a clear precedence hierarchy:

### Configuration Precedence
1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **Configuration file** (TOML format)
4. **Default values** (lowest priority)

### Environment Variables

#### Required
```bash
export GITHUB_TOKEN=ghp_your_personal_access_token
export LOCAL_FOLDER=/absolute/path/to/repositories
```

#### Optional
```bash
export REPO_VISIBILITY=all           # all, public, private
export LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
export MAX_WORKERS=1                 # Parallel processing limit
export USE_KEYRING=false             # Secure token storage
```

### Configuration File

Create a `config.toml` file for persistent settings:

```toml
# GitHub Configuration
github_token = "ghp_your_token_here"
repo_visibility = "all"  # all, public, private

# Local Storage
local_folder = "/Users/username/repositories"

# Processing Options
max_workers = 2
use_ssh_default = false
exclude_archived = true
exclude_forks = false

# Logging
log_level = "INFO"
log_file = "git_batch_pull.log"
enable_colors = true

# Security
use_keyring = true
validate_ssl = true
```

### GitHub Token Configuration

#### Token Scopes Required

| Repository Access | Required Scopes |
|-------------------|-----------------|
| Public repositories only | No scopes required |
| Private user repositories | `repo` |
| Private organization repositories | `repo` + `read:org` |
| SSO-enabled organizations | Enable SSO for the token |

#### Secure Token Storage

```bash
# Store token securely using keyring
git-batch-pull main-command org myorg --use-keyring
# Token will be prompted and stored encrypted

# Or set via environment
export GITHUB_TOKEN=ghp_your_token
```

---

## Security Features

Git Batch Pull implements enterprise-grade security measures throughout the application.

### Token Security

#### SecureTokenManager
- **Keyring Integration**: Secure storage using system keyring
- **Token Sanitization**: Automatic removal from logs and error messages
- **Encryption**: OS-level encryption for stored tokens
- **Scope Validation**: Verification of required GitHub permissions

```python
# Token is automatically sanitized in all log outputs
logger.info(f"Using token: {sanitize_token(token)}")  # Output: "Using token: ghp_****"
```

### Path Security

#### PathValidator
- **Directory Traversal Prevention**: Validates all file paths
- **Symlink Protection**: Prevents malicious symlink attacks
- **Permission Checking**: Ensures appropriate file system access

```python
# All paths are validated before use
validated_path = PathValidator.validate_and_resolve(user_input_path)
```

### Process Security

#### SafeSubprocessRunner
- **Command Injection Prevention**: Parameterized command execution
- **Resource Limits**: Timeout and memory constraints
- **Error Handling**: Secure error message sanitization

```python
# Git commands are executed safely
result = SafeSubprocessRunner.run_git_command(
    ["git", "clone", repo_url, local_path],
    timeout=300,
    cwd=workspace_dir
)
```

### Input Validation

- **Type Checking**: Runtime validation of all inputs
- **Sanitization**: Cleaning of user-provided data
- **Bounds Checking**: Validation of numeric inputs
- **Format Validation**: URL, path, and token format checking

---

## Development

### Architecture Details

#### Service Container (Dependency Injection)
```python
from git_batch_pull.services import ServiceContainer

# Initialize container with configuration
container = ServiceContainer(config)

# Services are automatically wired with dependencies
github_service = container.github_service
git_service = container.git_service
repository_service = container.repository_service
```

#### Core Services

##### GitHubService
```python
class GitHubService:
    """GitHub API integration with rate limiting and error handling."""

    async def get_repositories(
        self,
        entity_type: str,
        entity_name: str,
        visibility: str = "all"
    ) -> RepositoryBatch:
        """Fetch repositories with pagination and caching."""
```

##### GitService
```python
class GitService:
    """Git operations with security and error handling."""

    def clone_or_pull(
        self,
        repository: Repository,
        use_ssh: bool = False
    ) -> GitOperationResult:
        """Safe clone or pull with protocol handling."""
```

##### RepositoryService
```python
class RepositoryService:
    """Repository management and filtering."""

    def filter_repositories(
        self,
        batch: RepositoryBatch,
        repo_names: Optional[List[str]] = None,
        exclude_archived: bool = False,
        exclude_forks: bool = False
    ) -> RepositoryBatch:
        """Apply filtering criteria to repository batch."""
```

### Data Models

#### Repository Model
```python
@dataclass
class Repository:
    """Represents a GitHub repository with local state."""

    name: str
    url: str
    ssh_url: str
    local_path: Path
    is_private: bool
    is_archived: bool
    is_fork: bool
    last_updated: Optional[datetime]

    def get_clone_url(self, use_ssh: bool = False) -> str:
        """Get appropriate clone URL based on protocol preference."""
        return self.ssh_url if use_ssh else self.url
```

#### Configuration Model
```python
@dataclass
class Config:
    """Application configuration with validation."""

    github_token: str
    local_folder: Path
    repo_visibility: str = "all"
    max_workers: int = 1
    log_level: str = "INFO"
    use_keyring: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
```

### Exception Hierarchy

```python
class GitBatchPullError(Exception):
    """Base exception for all git-batch-pull errors."""

class ConfigError(GitBatchPullError):
    """Configuration-related errors."""

class ValidationError(GitBatchPullError):
    """Input validation errors."""

class AuthenticationError(GitBatchPullError):
    """GitHub authentication errors."""

class GitHubAPIError(GitBatchPullError):
    """GitHub API communication errors."""

class GitOperationError(GitBatchPullError):
    """Git command execution errors."""

class SecurityError(GitBatchPullError):
    """Security-related errors."""

class PathValidationError(SecurityError):
    """Path validation and security errors."""
```

### Plugin System

#### Creating Plugins

1. **Create Plugin Class**:
```python
from git_batch_pull.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    """Custom processing plugin."""

    def process_repository(self, repository: Repository) -> None:
        """Custom repository processing logic."""
        print(f"Processing {repository.name} with custom logic")
```

2. **Register in pyproject.toml**:
```toml
[project.entry-points.git_batch_pull_plugins]
custom = "mypackage.plugins:CustomPlugin"
```

3. **Plugin Discovery**:
```python
# Plugins are automatically discovered and loaded
from git_batch_pull.plugins import discover_plugins

plugins = discover_plugins()
for plugin in plugins:
    plugin.process_repository(repository)
```

### Testing

#### Test Structure
```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_cli.py                 # CLI interface tests
├── test_cli_integration.py     # CLI integration tests
├── test_config.py              # Configuration system tests
├── test_exceptions.py          # Exception handling tests
├── test_git_ops.py             # Git operations tests
├── test_github_api.py          # GitHub API tests
├── test_plugins.py             # Plugin system tests
├── test_protocol_*.py          # Protocol handling tests
├── test_repo_store.py          # Repository storage tests
└── test_security.py            # Security feature tests
```

#### Running Tests
```bash
# Run all tests with coverage
poetry run pytest --cov=git_batch_pull --cov-report=html

# Run specific test categories
poetry run pytest tests/test_security.py -v
poetry run pytest tests/test_cli* -v

# Run with different Python versions
poetry run tox
```

#### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **Security Tests**: Security feature validation
- **Performance Tests**: Load and stress testing
- **CLI Tests**: Command-line interface testing

---

## API Documentation

### Core Classes

#### BatchProcessor
```python
class BatchProcessor:
    """Handles parallel processing of repository batches."""

    def __init__(self, git_service: GitService, max_workers: int = 1):
        """Initialize with git service and worker limit."""

    def process_batch(
        self,
        batch: RepositoryBatch,
        use_ssh: bool = False,
        error_callback: Optional[Callable] = None
    ) -> BatchResult:
        """Process repository batch with parallel execution."""
```

#### ProtocolHandler
```python
class ProtocolHandler:
    """Manages SSH/HTTPS protocol detection and switching."""

    def detect_and_handle_mismatches(
        self,
        batch: RepositoryBatch,
        intended_protocol: str,
        entity_name: str,
        dry_run: bool = False
    ) -> None:
        """Detect and handle protocol mismatches."""
```

#### HealthChecker
```python
class HealthChecker:
    """System health monitoring and diagnostics."""

    async def run_all_checks(self) -> List[HealthCheckResult]:
        """Run comprehensive system health checks."""

    def _check_python_version(self) -> HealthCheckResult:
        """Verify Python version compatibility."""

    def _check_git_installation(self) -> HealthCheckResult:
        """Verify Git installation and version."""

    async def _check_github_api_access(self) -> HealthCheckResult:
        """Test GitHub API connectivity and authentication."""
```

### Utility Functions

#### Token Management
```python
def sanitize_token(token: str) -> str:
    """Sanitize token for safe logging."""
    if not token or len(token) < 8:
        return "****"
    return f"{token[:4]}****"

def validate_github_token(token: str) -> bool:
    """Validate GitHub token format."""
    return token.startswith(('ghp_', 'github_pat_')) and len(token) >= 40
```

#### Path Utilities
```python
def validate_path(path: str) -> Path:
    """Validate and resolve file system path."""
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise PathValidationError(f"Path does not exist: {path}")
    return resolved

def ensure_directory(path: Path) -> None:
    """Ensure directory exists with proper permissions."""
    path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise PermissionError(f"Directory not writable: {path}")
```

---

## Performance & Monitoring

### Performance Features

#### Parallel Processing
- **Configurable Workers**: Adjust based on system resources and API limits
- **Rate Limiting**: Respect GitHub API rate limits automatically
- **Resource Management**: Proper cleanup and resource disposal

#### Caching Strategy
- **Repository Metadata**: Cache GitHub API responses to reduce API calls
- **Local State**: Track repository state to avoid unnecessary operations
- **Cache Invalidation**: Smart cache refresh based on staleness

#### Memory Management
- **Streaming Processing**: Process large repository lists without loading all into memory
- **Garbage Collection**: Proper cleanup of temporary resources
- **Memory Profiling**: Built-in memory usage monitoring

### Monitoring & Observability

#### Health Checks
```bash
# Comprehensive system diagnostics
git-batch-pull health

# Output example:
🏥 Git Batch Pull Health Check
========================================
✅ python_version: Python 3.10.13
✅ git_installation: Git installed: git version 2.39.5
✅ network_connectivity: Network connectivity available
✅ github_api_access: GitHub API accessible
✅ disk_space: Sufficient disk space: 294.1GB free
✅ permissions: File system permissions OK

🟢 Overall Status: ALL SYSTEMS GO
```

#### Logging & Metrics
- **Structured Logging**: JSON-formatted logs for parsing and analysis
- **Performance Metrics**: Execution time, API calls, success/failure rates
- **Error Tracking**: Detailed error logs with stack traces
- **Audit Trail**: Complete operation history and changes

#### Integration Points
- **Prometheus Metrics**: Export metrics for monitoring systems
- **Webhook Support**: Notifications for completion and errors
- **CI/CD Integration**: Exit codes and structured output for automation

---

## Contributing

### Development Setup

1. **Clone and Setup**:
```bash
git clone https://github.com/alpersonalwebsite/git_batch_pull.git
cd git_batch_pull
poetry install --with dev
poetry shell
```

2. **Install Pre-commit Hooks**:
```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

3. **Run Tests**:
```bash
poetry run pytest -v --cov=git_batch_pull
```

4. **Build and Test Package**:
```bash
# Build the package
poetry build

# Test the built package
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl --force-reinstall

# Verify the installation
git-batch-pull health
```

### Development Workflow

```bash
# 1. Make your changes to the code

# 2. Test your changes
poetry run git-batch-pull health
poetry run git-batch-pull sync --help

# 3. Run tests
poetry run pytest

# 4. Check code quality
poetry run ruff check src/ tests/
poetry run mypy src/git_batch_pull

# 5. Build and test package
poetry build
pip install dist/git_batch_pull-1.0.0-py3-none-any.whl --force-reinstall

# 6. Final verification
git-batch-pull health
```

### Code Quality Standards

#### Type Checking
```bash
# Run mypy for type checking
poetry run mypy src/git_batch_pull

# All code must have type hints
def process_repository(repo: Repository) -> ProcessResult:
    """Process a repository with full type safety."""
```

#### Code Formatting
```bash
# Format code with Black
poetry run black src/ tests/

# Sort imports with isort
poetry run isort src/ tests/

# Lint with Ruff
poetry run ruff check src/ tests/
```

#### Security Scanning
```bash
# Scan for security issues
poetry run bandit -r src/

# Check dependencies for vulnerabilities
poetry run safety check
```

### Contribution Guidelines

1. **Fork Repository**: Create your own fork for development
2. **Feature Branch**: Create branches for new features or fixes
3. **Write Tests**: All new code must include comprehensive tests
4. **Documentation**: Update documentation for new features
5. **Code Review**: Submit pull requests for review
6. **CI/CD**: Ensure all automated checks pass

### Architecture Principles

- **Single Responsibility**: Each class/function has one clear purpose
- **Dependency Injection**: Use container for dependency management
- **Type Safety**: Complete type annotations throughout
- **Error Handling**: Comprehensive exception handling with recovery
- **Security First**: Security considerations in all development
- **Performance**: Efficient algorithms and resource usage

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

**Git Batch Pull** is developed and maintained by the open source community. Contributions are welcome and encouraged.

For questions, issues, or feature requests, please open an issue on [GitHub](https://github.com/alpersonalwebsite/git_batch_pull).

---

### 🚨 **Troubleshooting**

#### "command not found: git-batch-pull"

**Problem**: The command isn't available from your current directory.

**Quick Fix**:
```bash
# Go to the project directory and install globally
cd /path/to/git_batch_pull
pip install .

# Now works from any directory
git-batch-pull health
```

**Alternative**: Use Poetry from the project directory:
```bash
cd /path/to/git_batch_pull
poetry run git-batch-pull sync
```

For complete troubleshooting, see: [Installation Guide](docs/INSTALLATION.md#troubleshooting)

---
