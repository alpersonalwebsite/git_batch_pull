# API Reference

## Module Overview

The `git_batch_pull` package provides a comprehensive API for GitHub repository batch processing. This reference covers all public APIs, classes, and functions.

## Core Modules

### CLI Module (`git_batch_pull.cli`)

The command-line interface built with Typer, providing rich interactive commands.

#### Commands
- `main-command` - Primary batch processing command
- `health` - System health diagnostics

### Core Module (`git_batch_pull.core`)

Business logic and processing engines.

#### Classes
- `BatchProcessor` - Parallel repository processing
- `ProtocolHandler` - SSH/HTTPS protocol management
- `HealthChecker` - System diagnostics

### Services Module (`git_batch_pull.services`)

Service layer providing clean API abstractions.

#### Classes
- `ServiceContainer` - Dependency injection container
- `GitHubService` - GitHub API integration
- `GitService` - Git operations
- `RepositoryService` - Repository management

### Models Module (`git_batch_pull.models`)

Data models and structures.

#### Classes
- `Repository` - Repository representation
- `RepositoryBatch` - Collection of repositories
- `Config` - Application configuration
- `GitOperationResult` - Git operation results

### Security Module (`git_batch_pull.security`)

Security components and utilities.

#### Classes
- `SecureTokenManager` - Token encryption and storage
- `PathValidator` - Path security validation
- `SafeSubprocessRunner` - Secure subprocess execution

### Handlers Module (`git_batch_pull.handlers`)

Event and error handling.

#### Classes
- `LoggingHandler` - Structured logging
- `ErrorHandler` - Error processing and sanitization

### Plugins Module (`git_batch_pull.plugins`)

Plugin system for extensibility.

#### Classes
- `BasePlugin` - Plugin base class
- `PluginManager` - Plugin discovery and loading

For detailed API documentation, see [API.md](../API.md).
