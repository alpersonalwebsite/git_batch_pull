# API Reference

## Overview

Git Batch Pull provides a comprehensive Python API for programmatic access to GitHub repository batch processing functionality. The API is built with modern Python practices including type hints, dataclasses, async/await support, and comprehensive error handling.

### Design Philosophy

- **Type Safety**: Complete type annotations with runtime validation
- **Async Support**: Non-blocking operations for better performance
- **Error Handling**: Comprehensive exception hierarchy with recovery
- **Immutability**: Immutable data structures where possible
- **Composability**: Services and components designed for composition

## Quick Start

```python
import asyncio
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config

async def main():
    # Configure the application
    config = Config(
        github_token="ghp_your_token",
        local_folder="/path/to/repos",
        max_workers=4
    )

    # Initialize service container
    container = ServiceContainer(config)

    # Get repositories
    github_service = container.github_service
    repositories = await github_service.get_repositories(
        entity_type="org",
        entity_name="myorganization"
    )

    # Process repositories
    batch_processor = container.batch_processor
    result = await batch_processor.process_batch(repositories)

    print(f"Processed {len(result.successes)} repositories successfully")

# Run the async function
asyncio.run(main())
```

## Core Modules

### git_batch_pull.services

#### ServiceContainer

The main dependency injection container that manages all services and their dependencies.

```python
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config

# Initialize with configuration
config = Config(
    github_token="ghp_your_token",
    local_folder="/path/to/repos",
    max_workers=2,
    log_level="DEBUG"
)
container = ServiceContainer(config)

# Access services (automatically wired with dependencies)
github_service = container.github_service
git_service = container.git_service
repository_service = container.repository_service
batch_processor = container.batch_processor
```

**Constructor Parameters:**
- `config: Config` - Application configuration object

**Properties:**
- `github_service: GitHubService` - GitHub API service instance
- `git_service: GitService` - Git operations service instance
- `repository_service: RepositoryService` - Repository management service instance
- `batch_processor: BatchProcessor` - Batch processing engine instance

**Methods:**
- `configure_keyring(enabled: bool) -> None` - Enable/disable keyring token storage
- `get_health_checker() -> HealthChecker` - Get system health checker instance

#### GitHubService

Handles all GitHub API interactions with rate limiting and error handling.

```python
from git_batch_pull.services import GitHubService

service = GitHubService(token="ghp_token", use_keyring=False)

# Get repositories for an organization
repositories = await service.get_repositories(
    entity_type="org",
    entity_name="myorganization",
    visibility="all"
)

# Get repositories for a user
repositories = await service.get_repositories(
    entity_type="user",
    entity_name="username",
    visibility="public"
)
```

**Methods:**
- `get_repositories(entity_type: str, entity_name: str, visibility: str = "all") -> RepositoryBatch`
- `test_authentication() -> bool` - Test if token is valid
- `get_rate_limit_info() -> Dict[str, Any]` - Get current rate limit status

#### GitService

Provides secure Git operations with error handling and protocol management.

```python
from git_batch_pull.services import GitService

service = GitService()

# Clone or pull a repository
result = service.clone_or_pull(
    repository=repository,
    use_ssh=True
)

# Check if repository has uncommitted changes
has_changes = service.has_uncommitted_changes(repository.local_path)
```

**Methods:**
- `clone_or_pull(repository: Repository, use_ssh: bool = False) -> GitOperationResult`
- `has_uncommitted_changes(repo_path: Path) -> bool`
- `switch_remote_protocol(repo_path: Path, new_url: str) -> bool`

#### RepositoryService

Manages repository filtering, caching, and metadata operations.

```python
from git_batch_pull.services import RepositoryService

service = RepositoryService(github_service, config)

# Filter repositories
filtered = service.filter_repositories(
    batch=repository_batch,
    repo_names=["repo1", "repo2"],
    exclude_archived=True,
    exclude_forks=False
)

# Detect protocol mismatches
mismatches = service.detect_protocol_mismatches(
    batch=repository_batch,
    intended_protocol="ssh"
)
```

**Methods:**
- `get_repositories(...) -> RepositoryBatch` - Get repositories with caching
- `filter_repositories(...) -> RepositoryBatch` - Apply filtering criteria
- `detect_protocol_mismatches(...) -> List[Tuple[str, str]]` - Find protocol mismatches
- `fix_protocol_mismatches(...) -> int` - Fix protocol mismatches

### git_batch_pull.models

#### Repository

Represents a GitHub repository with local state information.

```python
from git_batch_pull.models import Repository
from pathlib import Path

repository = Repository(
    name="my-repo",
    url="https://github.com/user/my-repo.git",
    ssh_url="git@github.com:user/my-repo.git",
    local_path=Path("/local/path/my-repo"),
    is_private=False,
    is_archived=False,
    is_fork=False
)

# Get clone URL based on protocol preference
clone_url = repository.get_clone_url(use_ssh=True)
```

**Properties:**
- `name: str` - Repository name
- `url: str` - HTTPS clone URL
- `ssh_url: str` - SSH clone URL
- `local_path: Path` - Local filesystem path
- `is_private: bool` - Whether repository is private
- `is_archived: bool` - Whether repository is archived
- `is_fork: bool` - Whether repository is a fork
- `last_updated: Optional[datetime]` - Last update timestamp

**Methods:**
- `get_clone_url(use_ssh: bool = False) -> str` - Get appropriate clone URL
- `exists_locally() -> bool` - Check if repository exists locally
- `is_git_repository() -> bool` - Check if local path is a git repository

#### RepositoryBatch

Container for multiple repositories with metadata.

```python
from git_batch_pull.models import RepositoryBatch

batch = RepositoryBatch(
    repositories=[repo1, repo2, repo3],
    entity_type="org",
    entity_name="myorganization",
    total_count=3
)

# Access repositories
for repo in batch.repositories:
    print(f"Processing {repo.name}")
```

**Properties:**
- `repositories: List[Repository]` - List of repositories
- `entity_type: str` - "user" or "org"
- `entity_name: str` - GitHub username or organization name
- `total_count: int` - Total number of repositories
- `fetched_at: datetime` - When batch was fetched

#### Config

Application configuration with validation.

```python
from git_batch_pull.models import Config
from pathlib import Path

config = Config(
    github_token="ghp_your_token",
    local_folder=Path("/path/to/repos"),
    repo_visibility="all",
    max_workers=2,
    log_level="INFO"
)

# Configuration is automatically validated
```

**Properties:**
- `github_token: str` - GitHub personal access token
- `local_folder: Path` - Local repository storage path
- `repo_visibility: str` - "all", "public", or "private"
- `max_workers: int` - Maximum parallel workers
- `log_level: str` - Logging level
- `use_keyring: bool` - Whether to use keyring for token storage

### git_batch_pull.core

#### BatchProcessor

Handles parallel processing of repository operations.

```python
from git_batch_pull.core import BatchProcessor

processor = BatchProcessor(
    git_service=git_service,
    max_workers=4
)

# Process batch with error handling
def error_callback(repo_name: str, error: Exception):
    print(f"Error processing {repo_name}: {error}")

result = processor.process_batch(
    batch=repository_batch,
    use_ssh=True,
    error_callback=error_callback
)

print(f"Processed: {result.processed}, Failed: {result.failed}")
```

**Methods:**
- `process_batch(batch: RepositoryBatch, use_ssh: bool = False, error_callback: Optional[Callable] = None) -> BatchResult`

#### ProtocolHandler

Manages SSH/HTTPS protocol detection and switching.

```python
from git_batch_pull.core import ProtocolHandler

handler = ProtocolHandler(repository_service)

# Detect and handle protocol mismatches
handler.detect_and_handle_mismatches(
    batch=repository_batch,
    intended_protocol="ssh",
    entity_name="myorg",
    dry_run=False
)
```

**Methods:**
- `detect_and_handle_mismatches(batch: RepositoryBatch, intended_protocol: str, entity_name: str, dry_run: bool = False)`
- `prompt_for_protocol_switch(mismatches: List[Tuple[str, str]], target_protocol: str) -> bool`

#### HealthChecker

System health monitoring and diagnostics.

```python
from git_batch_pull.core.health_check import HealthChecker, format_health_report
import asyncio

checker = HealthChecker(config)

# Run all health checks
async def check_health():
    results = await checker.run_all_checks()
    report = format_health_report(results)
    print(report)

asyncio.run(check_health())
```

**Methods:**
- `run_all_checks() -> List[HealthCheckResult]` - Run comprehensive health checks
- Individual check methods for specific components

### git_batch_pull.security

#### SecureTokenManager

Secure token storage and management.

```python
from git_batch_pull.security import SecureTokenManager

manager = SecureTokenManager()

# Store token securely
manager.store_token("github", "ghp_your_token")

# Retrieve token
token = manager.get_token("github")

# Delete token
manager.delete_token("github")
```

**Methods:**
- `store_token(service: str, token: str)` - Store token securely
- `get_token(service: str) -> Optional[str]` - Retrieve stored token
- `delete_token(service: str)` - Delete stored token
- `token_exists(service: str) -> bool` - Check if token exists

#### PathValidator

Path validation and security.

```python
from git_batch_pull.security import PathValidator

# Validate and resolve path
safe_path = PathValidator.validate_and_resolve("/user/input/path")

# Check if path is safe
is_safe = PathValidator.is_safe_path("/some/path", "/base/directory")
```

**Methods:**
- `validate_and_resolve(path: str) -> Path` - Validate and resolve path
- `is_safe_path(path: str, base_path: str) -> bool` - Check path safety
- `ensure_directory_exists(path: Path)` - Create directory safely

#### SafeSubprocessRunner

Secure subprocess execution.

```python
from git_batch_pull.security import SafeSubprocessRunner

runner = SafeSubprocessRunner()

# Run git command safely
result = runner.run_git_command(
    ["git", "clone", repo_url, local_path],
    cwd=workspace_dir,
    timeout=300
)
```

**Methods:**
- `run_git_command(args: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> subprocess.CompletedProcess`
- `run_command(args: List[str], **kwargs) -> subprocess.CompletedProcess` - Generic command execution

### git_batch_pull.exceptions

#### Exception Hierarchy

```python
from git_batch_pull.exceptions import (
    GitBatchPullError,
    ConfigError,
    ValidationError,
    AuthenticationError,
    GitHubAPIError,
    GitOperationError,
    SecurityError,
    PathValidationError
)

try:
    # Some operation
    pass
except GitHubAPIError as e:
    print(f"GitHub API error: {e}")
except GitOperationError as e:
    print(f"Git operation failed: {e}")
except GitBatchPullError as e:
    print(f"General error: {e}")
```

**Exception Classes:**
- `GitBatchPullError` - Base exception for all errors
- `ConfigError` - Configuration and validation errors
- `ValidationError` - Input validation errors
- `AuthenticationError` - Authentication and authorization errors
- `GitHubAPIError` - GitHub API communication errors
- `GitOperationError` - Git command execution errors
- `SecurityError` - Security-related errors
- `PathValidationError` - Path validation and security errors

## Usage Examples

### Basic Repository Processing

```python
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config
from git_batch_pull.core import BatchProcessor
from pathlib import Path

# Setup configuration
config = Config(
    github_token="ghp_your_token",
    local_folder=Path("/local/repos"),
    max_workers=2
)

# Initialize services
container = ServiceContainer(config)

# Get repositories
repository_batch = container.repository_service.get_repositories(
    entity_type="org",
    entity_name="myorganization"
)

# Process repositories
processor = BatchProcessor(container.git_service, max_workers=2)
result = processor.process_batch(repository_batch, use_ssh=True)

print(f"Successfully processed {result.processed} repositories")
```

### Custom Error Handling

```python
def custom_error_handler(repo_name: str, error: Exception):
    """Custom error handling for repository processing."""
    if isinstance(error, GitHubAPIError):
        print(f"GitHub API error for {repo_name}: {error}")
    elif isinstance(error, GitOperationError):
        print(f"Git operation failed for {repo_name}: {error}")
    else:
        print(f"Unexpected error for {repo_name}: {error}")

# Use custom error handler
result = processor.process_batch(
    batch=repository_batch,
    error_callback=custom_error_handler
)
```

### Health Monitoring

```python
import asyncio
from git_batch_pull.core.health_check import HealthChecker

async def monitor_system_health():
    """Monitor system health and report issues."""
    checker = HealthChecker()
    results = await checker.run_all_checks()

    # Check for errors
    errors = [r for r in results if r.status == "error"]
    warnings = [r for r in results if r.status == "warning"]

    if errors:
        print(f"Found {len(errors)} system errors:")
        for error in errors:
            print(f"  - {error.name}: {error.message}")

    if warnings:
        print(f"Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  - {warning.name}: {warning.message}")

    return len(errors) == 0

# Run health check
healthy = asyncio.run(monitor_system_health())
```

## Advanced Examples

### Enterprise Integration

```python
import asyncio
import logging
from pathlib import Path
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config
from git_batch_pull.security import SecureTokenManager
from git_batch_pull.handlers import LoggingHandler

async def enterprise_batch_processing():
    """Enterprise-grade batch processing with full monitoring."""

    # Configure structured logging
    logging_handler = LoggingHandler()
    logging_handler.configure_structured_logging(
        log_file=Path("operations.log"),
        log_level="INFO"
    )

    # Secure token management
    token_manager = SecureTokenManager()
    github_token = token_manager.get_token("github")

    # Enterprise configuration
    config = Config(
        github_token=github_token,
        local_folder=Path("/enterprise/repositories"),
        max_workers=8,
        use_keyring=True,
        log_level="INFO",
        exclude_archived=True,
        exclude_forks=True
    )

    # Initialize services
    container = ServiceContainer(config)

    try:
        # Health check before processing
        health_checker = container.get_health_checker()
        health_results = await health_checker.run_all_checks()

        if not all(r.status == "ok" for r in health_results):
            logging.error("Health check failed, aborting operation")
            return False

        # Get repositories
        github_service = container.github_service
        repositories = await github_service.get_repositories(
            entity_type="org",
            entity_name="enterprise-org",
            visibility="all"
        )

        # Filter and process
        repository_service = container.repository_service
        filtered_repos = repository_service.filter_repositories(
            repositories,
            exclude_archived=True,
            exclude_forks=True
        )

        # Process with monitoring
        batch_processor = container.batch_processor
        result = await batch_processor.process_batch(
            filtered_repos,
            use_ssh=True,
            error_callback=enterprise_error_handler
        )

        # Report results
        logging.info(f"Enterprise batch processing completed")
        logging.info(f"Successful: {len(result.successes)}")
        logging.info(f"Failed: {len(result.failures)}")

        return len(result.failures) == 0

    except Exception as e:
        logging.error(f"Critical error in batch processing: {e}")
        return False

def enterprise_error_handler(repo_name: str, error: Exception):
    """Enterprise error handling with alerting."""
    logging.error(f"Repository {repo_name} failed: {error}")
    # Integration with enterprise monitoring/alerting
    # send_alert(f"Git batch pull failed for {repo_name}: {error}")

# Run enterprise processing
if __name__ == "__main__":
    success = asyncio.run(enterprise_batch_processing())
    exit(0 if success else 1)
```

### Custom Plugin Development

```python
from git_batch_pull.plugins import BasePlugin
from git_batch_pull.models import Repository
import json
from pathlib import Path

class CompliancePlugin(BasePlugin):
    """Plugin for compliance scanning and reporting."""

    def __init__(self):
        super().__init__()
        self.compliance_results = []

    def process_repository(self, repository: Repository) -> None:
        """Scan repository for compliance issues."""
        compliance_result = self._scan_compliance(repository)
        self.compliance_results.append(compliance_result)

        if not compliance_result["compliant"]:
            self.logger.warning(
                f"Compliance issues found in {repository.name}: "
                f"{compliance_result['issues']}"
            )

    def _scan_compliance(self, repository: Repository) -> dict:
        """Perform compliance scanning."""
        issues = []

        # Check for required files
        required_files = ["LICENSE", "README.md", "SECURITY.md"]
        for required_file in required_files:
            if not (repository.local_path / required_file).exists():
                issues.append(f"Missing {required_file}")

        # Check for sensitive files
        sensitive_patterns = [".env", "*.key", "*.pem", "config.json"]
        for pattern in sensitive_patterns:
            if list(repository.local_path.glob(pattern)):
                issues.append(f"Sensitive files found: {pattern}")

        return {
            "repository": repository.name,
            "compliant": len(issues) == 0,
            "issues": issues,
            "scan_timestamp": self._get_current_timestamp()
        }

    def finalize(self) -> None:
        """Generate compliance report."""
        report_path = Path("compliance_report.json")
        with open(report_path, "w") as f:
            json.dump(self.compliance_results, f, indent=2)

        self.logger.info(f"Compliance report saved to {report_path}")

# Register plugin in pyproject.toml:
# [project.entry-points.git_batch_pull_plugins]
# compliance = "your_package.plugins:CompliancePlugin"
```

### Monitoring and Observability

```python
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config, Repository

@dataclass
class ProcessingMetrics:
    """Metrics for monitoring batch processing."""
    total_repositories: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration: float = 0.0
    avg_operation_time: float = 0.0
    api_calls_made: int = 0
    bytes_processed: int = 0

class MonitoringService:
    """Service for collecting and reporting metrics."""

    def __init__(self):
        self.metrics = ProcessingMetrics()
        self.start_time: float = 0.0
        self.operation_times: List[float] = []

    def start_monitoring(self):
        """Start monitoring session."""
        self.start_time = time.time()

    def record_operation(self, duration: float, success: bool):
        """Record individual operation metrics."""
        self.operation_times.append(duration)
        if success:
            self.metrics.successful_operations += 1
        else:
            self.metrics.failed_operations += 1

    def finalize_metrics(self):
        """Calculate final metrics."""
        self.metrics.total_duration = time.time() - self.start_time
        self.metrics.total_repositories = len(self.operation_times)

        if self.operation_times:
            self.metrics.avg_operation_time = sum(self.operation_times) / len(self.operation_times)

    def export_metrics(self) -> Dict:
        """Export metrics in Prometheus format."""
        return {
            "git_batch_pull_total_repositories": self.metrics.total_repositories,
            "git_batch_pull_successful_operations": self.metrics.successful_operations,
            "git_batch_pull_failed_operations": self.metrics.failed_operations,
            "git_batch_pull_total_duration_seconds": self.metrics.total_duration,
            "git_batch_pull_avg_operation_duration_seconds": self.metrics.avg_operation_time,
            "git_batch_pull_success_rate": (
                self.metrics.successful_operations / max(self.metrics.total_repositories, 1)
            )
        }

async def monitored_batch_processing():
    """Batch processing with comprehensive monitoring."""
    monitor = MonitoringService()
    monitor.start_monitoring()

    # Configure application
    config = Config(
        github_token="ghp_your_token",
        local_folder="/monitored/repos",
        max_workers=4
    )

    container = ServiceContainer(config)

    try:
        # Get repositories
        github_service = container.github_service
        repositories = await github_service.get_repositories("org", "myorg")

        # Process with monitoring
        git_service = container.git_service

        for repo in repositories.repositories:
            start_time = time.time()
            try:
                result = git_service.clone_or_pull(repo)
                duration = time.time() - start_time
                monitor.record_operation(duration, result.success)

            except Exception as e:
                duration = time.time() - start_time
                monitor.record_operation(duration, False)
                print(f"Failed to process {repo.name}: {e}")

        # Generate final metrics
        monitor.finalize_metrics()
        metrics = monitor.export_metrics()

        # Export metrics (e.g., to Prometheus, CloudWatch, etc.)
        print("Processing Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

        return metrics

    except Exception as e:
        print(f"Monitoring failed: {e}")
        return None

# Run monitored processing
if __name__ == "__main__":
    asyncio.run(monitored_batch_processing())
```

### Security-First Implementation

```python
import asyncio
from pathlib import Path
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config
from git_batch_pull.security import SecureTokenManager, PathValidator
from git_batch_pull.exceptions import SecurityError

async def secure_batch_processing():
    """Security-focused batch processing implementation."""

    try:
        # Secure token management
        token_manager = SecureTokenManager()

        # Store token securely (prompts user)
        print("Please enter your GitHub token:")
        token = input().strip()
        token_manager.store_token("github", token)

        # Retrieve token securely
        github_token = token_manager.get_token("github")

        # Validate and secure path handling
        user_folder = input("Enter repository folder path: ").strip()
        try:
            validated_folder = PathValidator.validate_and_resolve(user_folder)
        except SecurityError as e:
            print(f"Path validation failed: {e}")
            return False

        # Security configuration
        config = Config(
            github_token=github_token,
            local_folder=validated_folder,
            max_workers=2,  # Conservative for security
            use_keyring=True,
            validate_ssl=True
        )

        # Initialize with security checks
        container = ServiceContainer(config)

        # Health check with security focus
        health_checker = container.get_health_checker()
        health_results = await health_checker.run_all_checks()

        security_checks = [
            r for r in health_results
            if "security" in r.name.lower() or "permission" in r.name.lower()
        ]

        if any(r.status != "ok" for r in security_checks):
            print("Security health checks failed")
            return False

        # Process repositories with security validation
        github_service = container.github_service
        repositories = await github_service.get_repositories("org", "secure-org")

        # Additional security filtering
        secure_repos = []
        for repo in repositories.repositories:
            # Validate repository URLs
            if not repo.url.startswith(("https://github.com/", "git@github.com:")):
                print(f"Skipping repository with suspicious URL: {repo.url}")
                continue

            # Validate local paths
            try:
                PathValidator.validate_and_resolve(str(repo.local_path))
                secure_repos.append(repo)
            except SecurityError:
                print(f"Skipping repository with invalid path: {repo.local_path}")

        print(f"Processing {len(secure_repos)} repositories after security filtering")

        # Process with secure operations
        batch_processor = container.batch_processor
        from git_batch_pull.models import RepositoryBatch
        secure_batch = RepositoryBatch(repositories=secure_repos)

        result = await batch_processor.process_batch(secure_batch)

        print(f"Secure processing completed: {len(result.successes)} successful")
        return True

    except Exception as e:
        print(f"Security error in batch processing: {e}")
        return False

# Run secure processing
if __name__ == "__main__":
    success = asyncio.run(secure_batch_processing())
    if success:
        print("Secure batch processing completed successfully")
    else:
        print("Secure batch processing failed")
        exit(1)
```

## Integration Patterns

### CI/CD Integration

```python
# ci_integration.py
import os
import sys
import asyncio
from git_batch_pull.services import ServiceContainer
from git_batch_pull.models import Config

async def ci_batch_processing():
    """CI/CD pipeline integration."""

    # Get configuration from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("ERROR: GITHUB_TOKEN environment variable required")
        return False

    workspace = os.getenv("GITHUB_WORKSPACE", "/workspace")
    org_name = os.getenv("GITHUB_REPOSITORY_OWNER")

    config = Config(
        github_token=github_token,
        local_folder=workspace,
        max_workers=int(os.getenv("MAX_WORKERS", "4")),
        log_level="INFO"
    )

    container = ServiceContainer(config)

    try:
        # Process repositories
        github_service = container.github_service
        repositories = await github_service.get_repositories("org", org_name)

        batch_processor = container.batch_processor
        result = await batch_processor.process_batch(repositories)

        # Set output for GitHub Actions
        if os.getenv("GITHUB_ACTIONS"):
            with open(os.getenv("GITHUB_OUTPUT", "/dev/null"), "a") as f:
                f.write(f"successful_repos={len(result.successes)}\n")
                f.write(f"failed_repos={len(result.failures)}\n")

        # Exit with appropriate code
        return len(result.failures) == 0

    except Exception as e:
        print(f"CI processing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(ci_batch_processing())
    sys.exit(0 if success else 1)
```

---

For more examples and use cases, see the [examples directory](../examples/) in the repository.
