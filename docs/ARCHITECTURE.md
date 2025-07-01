# Architecture Deep Dive

## Overview

Git Batch Pull implements a sophisticated **7-layer architecture** with enterprise-grade patterns including dependency injection, service abstraction, comprehensive security, and advanced error handling.

## Architectural Principles

### SOLID Principles
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through plugins and configuration
- **Liskov Substitution**: All interfaces are properly implemented
- **Interface Segregation**: Focused, cohesive interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Clean Architecture
- **Independence**: Business logic independent of external concerns
- **Testability**: All components can be tested in isolation
- **Database Independence**: No hard coupling to specific storage
- **UI Independence**: Core logic independent of CLI interface
- **Framework Independence**: Not bound to specific frameworks

## Layer-by-Layer Analysis

### Layer 1: CLI Interface (Presentation)

**Purpose**: User interaction and command parsing
**Technology**: Typer with Rich for enhanced UX
**Components**: CLI commands, argument parsing, output formatting

```
src/git_batch_pull/cli/
├── __init__.py          # CLI module initialization
├── cli.py              # Main CLI application
├── commands.py         # Command definitions
└── formatters.py       # Output formatting utilities
```

#### Key Features
- **Rich Help System**: Contextual help with examples
- **Parameter Validation**: Type checking and bounds validation
- **Progress Indicators**: Real-time progress bars and status
- **Error Formatting**: User-friendly error messages

#### Implementation Details

```python
@app.command("main-command")
def main_command(
    entity_type: EntityType = typer.Argument(..., help="Type of GitHub entity"),
    entity_name: str = typer.Argument(..., help="Name of the entity"),
    # ... other parameters
) -> None:
    """Process repositories for a GitHub user or organization."""

    # Validate inputs at CLI layer
    validated_config = validate_cli_inputs(...)

    # Delegate to handler layer
    handler = MainCommandHandler(validated_config)
    result = handler.execute()

    # Format and display results
    formatter = ResultFormatter()
    formatter.display_results(result)
```

### Layer 2: Handler Layer (Application Services)

**Purpose**: Orchestrate business operations and handle cross-cutting concerns
**Components**: Command handlers, logging handlers, error handlers

```
src/git_batch_pull/handlers/
├── __init__.py              # Handler module initialization
├── main_command_handler.py  # Main command orchestration
├── logging_handler.py       # Structured logging management
├── error_handler.py         # Error processing and sanitization
└── callback_handlers.py    # Event callback handling
```

#### Command Handler Pattern

```python
class MainCommandHandler:
    """Orchestrates the main batch processing workflow."""

    def __init__(self, config: Config):
        self.config = config
        self.container = ServiceContainer(config)
        self.logger = LoggingHandler()
        self.error_handler = ErrorHandler()

    def execute(self) -> BatchResult:
        """Execute the complete batch processing workflow."""
        try:
            # 1. Health check
            health_result = self._perform_health_check()
            if not health_result.success:
                return BatchResult.from_health_failure(health_result)

            # 2. Repository discovery
            repositories = self._discover_repositories()

            # 3. Protocol handling
            repositories = self._handle_protocols(repositories)

            # 4. Batch processing
            result = self._process_batch(repositories)

            # 5. Post-processing
            self._post_process_results(result)

            return result

        except Exception as e:
            return self.error_handler.handle_critical_error(e)
```

### Layer 3: Core Business Logic (Domain Layer)

**Purpose**: Implement business rules and domain-specific operations
**Components**: Batch processor, protocol handler, health checker

```
src/git_batch_pull/core/
├── __init__.py              # Core module initialization
├── batch_processor.py      # Parallel batch processing engine
├── protocol_handler.py     # SSH/HTTPS protocol management
├── health_check.py         # System health diagnostics
└── plugin_manager.py      # Plugin discovery and management
```

#### Batch Processing Engine

```python
class BatchProcessor:
    """High-performance parallel repository processing."""

    def __init__(
        self,
        git_service: GitService,
        max_workers: int = 1,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.git_service = git_service
        self.max_workers = max_workers
        self.rate_limiter = rate_limiter or RateLimiter()
        self.metrics = ProcessingMetrics()

    async def process_batch(
        self,
        batch: RepositoryBatch,
        use_ssh: bool = False,
        error_callback: Optional[Callable] = None
    ) -> BatchResult:
        """Process repository batch with parallel execution."""

        # Initialize processing context
        context = ProcessingContext(
            batch=batch,
            use_ssh=use_ssh,
            error_callback=error_callback
        )

        # Execute parallel processing
        if self.max_workers == 1:
            return await self._sequential_processing(context)
        else:
            return await self._parallel_processing(context)

    async def _parallel_processing(self, context: ProcessingContext) -> BatchResult:
        """Execute parallel processing with worker management."""
        semaphore = asyncio.Semaphore(self.max_workers)
        tasks = []

        for repository in context.batch.repositories:
            task = self._process_single_repository(
                repository, context, semaphore
            )
            tasks.append(task)

        # Wait for all tasks with progress tracking
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return self._aggregate_results(results, context)
```

#### Protocol Management

```python
class ProtocolHandler:
    """Intelligent SSH/HTTPS protocol management."""

    def __init__(self, git_service: GitService):
        self.git_service = git_service
        self.protocol_detector = ProtocolDetector()

    def detect_and_handle_mismatches(
        self,
        batch: RepositoryBatch,
        intended_protocol: str,
        entity_name: str,
        dry_run: bool = False
    ) -> ProtocolHandlingResult:
        """Detect and resolve protocol mismatches."""

        mismatches = []

        for repository in batch.repositories:
            current_protocol = self.protocol_detector.detect_protocol(
                repository.local_path
            )

            if current_protocol != intended_protocol:
                mismatch = ProtocolMismatch(
                    repository=repository,
                    current_protocol=current_protocol,
                    intended_protocol=intended_protocol
                )
                mismatches.append(mismatch)

        if not mismatches:
            return ProtocolHandlingResult.no_action_needed()

        return self._handle_protocol_mismatches(mismatches, dry_run)
```

### Layer 4: Service Layer (Infrastructure Abstraction)

**Purpose**: Abstract external system interactions and provide clean APIs
**Components**: GitHub service, Git service, Repository service

```
src/git_batch_pull/services/
├── __init__.py              # Services module initialization
├── container.py            # Dependency injection container
├── github_service.py       # GitHub API client
├── git_service.py          # Git operations service
└── repository_service.py   # Repository management service
```

#### Service Container (Dependency Injection)

```python
class ServiceContainer:
    """Dependency injection container with lazy initialization."""

    def __init__(self, config: Config):
        self.config = config
        self._services = {}
        self._initializers = {
            'github_service': self._create_github_service,
            'git_service': self._create_git_service,
            'repository_service': self._create_repository_service,
            'batch_processor': self._create_batch_processor,
        }

    def __getattr__(self, name: str):
        """Lazy service initialization."""
        if name in self._initializers:
            if name not in self._services:
                self._services[name] = self._initializers[name]()
            return self._services[name]
        raise AttributeError(f"Service '{name}' not found")

    def _create_github_service(self) -> GitHubService:
        """Create GitHub service with proper configuration."""
        return GitHubService(
            token=self.config.github_token,
            use_keyring=self.config.use_keyring,
            rate_limiter=RateLimiter(),
            session_factory=self._create_secure_session
        )
```

#### GitHub Service Implementation

```python
class GitHubService:
    """GitHub API client with enterprise features."""

    def __init__(
        self,
        token: str,
        use_keyring: bool = False,
        rate_limiter: Optional[RateLimiter] = None,
        session_factory: Optional[Callable] = None
    ):
        self.token_manager = SecureTokenManager(use_keyring)
        self.token = self.token_manager.get_or_store_token("github", token)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = session_factory() if session_factory else self._create_session()
        self.cache = TTLCache(maxsize=100, ttl=3600)  # 1-hour cache

    async def get_repositories(
        self,
        entity_type: str,
        entity_name: str,
        visibility: str = "all"
    ) -> RepositoryBatch:
        """Fetch repositories with caching and error handling."""

        cache_key = f"{entity_type}:{entity_name}:{visibility}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            repositories = await self._fetch_repositories_paginated(
                entity_type, entity_name, visibility
            )

            batch = RepositoryBatch(
                repositories=repositories,
                entity_type=entity_type,
                entity_name=entity_name,
                fetched_at=datetime.utcnow()
            )

            self.cache[cache_key] = batch
            return batch

        except Exception as e:
            raise GitHubAPIError(f"Failed to fetch repositories: {e}") from e
```

### Layer 5: Security Layer (Cross-cutting Security)

**Purpose**: Implement comprehensive security controls
**Components**: Token manager, path validator, subprocess runner

```
src/git_batch_pull/security/
├── __init__.py              # Security module initialization
├── token_manager.py        # Secure token management
├── path_validator.py       # Path security validation
├── subprocess_runner.py    # Safe subprocess execution
└── input_validator.py      # Input validation utilities
```

#### Secure Token Management

```python
class SecureTokenManager:
    """Enterprise-grade token management with encryption."""

    def __init__(self, use_keyring: bool = True):
        self.use_keyring = use_keyring
        self.keyring_service = "git_batch_pull"
        self.encryption_key = self._get_or_create_encryption_key()

    def store_token(self, service: str, token: str) -> None:
        """Store token with encryption."""
        if not self._validate_token_format(token):
            raise SecurityError("Invalid token format")

        if self.use_keyring:
            try:
                keyring.set_password(self.keyring_service, service, token)
                return
            except Exception as e:
                logger.warning(f"Keyring storage failed: {e}")

        # Fallback to encrypted file storage
        encrypted_token = self._encrypt_token(token)
        self._store_encrypted_token(service, encrypted_token)

    def get_token(self, service: str) -> Optional[str]:
        """Retrieve and decrypt token."""
        if self.use_keyring:
            try:
                token = keyring.get_password(self.keyring_service, service)
                if token:
                    return token
            except Exception as e:
                logger.warning(f"Keyring retrieval failed: {e}")

        # Fallback to encrypted file storage
        encrypted_token = self._load_encrypted_token(service)
        if encrypted_token:
            return self._decrypt_token(encrypted_token)

        return None
```

#### Path Security Validation

```python
class PathValidator:
    """Advanced path security with multiple validation layers."""

    DANGEROUS_PATHS = frozenset([
        "/etc", "/var", "/usr", "/bin", "/sbin", "/boot", "/dev", "/proc", "/sys"
    ])

    DANGEROUS_PATTERNS = [
        r"\.\.\/",  # Directory traversal
        r"^\/dev\/",  # Device files
        r"^\/proc\/",  # Process files
        r".*\$\{.*\}.*",  # Variable expansion
    ]

    @classmethod
    def validate_and_resolve(
        cls,
        path: str,
        base_path: Optional[str] = None
    ) -> Path:
        """Comprehensive path validation and resolution."""

        # Input validation
        if not path or not isinstance(path, str):
            raise PathValidationError("Path must be a non-empty string")

        # Pattern matching
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.match(pattern, path):
                raise PathValidationError(f"Path matches dangerous pattern: {pattern}")

        # Path resolution
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            raise PathValidationError(f"Path resolution failed: {e}")

        # Dangerous path check
        for dangerous in cls.DANGEROUS_PATHS:
            if str(resolved_path).startswith(dangerous):
                raise PathValidationError(f"Access to {dangerous} not allowed")

        # Base path validation
        if base_path:
            base_resolved = Path(base_path).resolve()
            try:
                resolved_path.relative_to(base_resolved)
            except ValueError:
                raise PathValidationError("Path outside allowed base directory")

        # Symlink validation
        cls._validate_symlinks(resolved_path)

        return resolved_path
```

### Layer 6: Data Layer (Models and Storage)

**Purpose**: Define data structures and manage persistence
**Components**: Data models, configuration, exceptions

```
src/git_batch_pull/models/
├── __init__.py              # Models module initialization
├── repository.py           # Repository data models
├── config.py              # Configuration model
├── results.py             # Result and status models
└── batch.py               # Batch processing models
```

#### Advanced Data Models

```python
@dataclass(frozen=True)
class Repository:
    """Immutable repository representation with validation."""

    name: str
    url: str
    ssh_url: str
    local_path: Path
    is_private: bool = False
    is_archived: bool = False
    is_fork: bool = False
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate repository data on creation."""
        if not self.name:
            raise ValueError("Repository name cannot be empty")

        if not self.url.startswith(("https://", "git@")):
            raise ValueError("Invalid repository URL format")

        # Validate local path
        try:
            PathValidator.validate_and_resolve(str(self.local_path))
        except PathValidationError as e:
            raise ValueError(f"Invalid local path: {e}")

    def get_clone_url(self, use_ssh: bool = False) -> str:
        """Get appropriate clone URL based on protocol preference."""
        return self.ssh_url if use_ssh else self.url

    def is_cloned(self) -> bool:
        """Check if repository is already cloned locally."""
        return (self.local_path / ".git").exists()

    def get_current_branch(self) -> Optional[str]:
        """Get current branch of local repository."""
        if not self.is_cloned():
            return None

        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.local_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
```

#### Configuration with Advanced Validation

```python
@dataclass
class Config:
    """Application configuration with comprehensive validation."""

    github_token: str
    local_folder: Path
    repo_visibility: str = "all"
    max_workers: int = 1
    log_level: str = "INFO"
    use_keyring: bool = False
    exclude_archived: bool = False
    exclude_forks: bool = False

    # Advanced configuration
    timeout_seconds: int = 300
    retry_attempts: int = 3
    rate_limit_per_hour: int = 5000
    cache_ttl_seconds: int = 3600

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """Comprehensive configuration validation."""
        # Token validation
        if not self.github_token:
            raise ConfigError("GitHub token is required")

        if not validate_github_token(self.github_token):
            raise ConfigError("Invalid GitHub token format")

        # Path validation
        try:
            self.local_folder = PathValidator.validate_and_resolve(
                str(self.local_folder)
            )
        except PathValidationError as e:
            raise ConfigError(f"Invalid local folder: {e}")

        # Numeric validations
        if self.max_workers < 1 or self.max_workers > 20:
            raise ConfigError("max_workers must be between 1 and 20")

        if self.timeout_seconds < 60 or self.timeout_seconds > 3600:
            raise ConfigError("timeout_seconds must be between 60 and 3600")

        # Enum validations
        valid_visibility = {"all", "public", "private"}
        if self.repo_visibility not in valid_visibility:
            raise ConfigError(f"repo_visibility must be one of: {valid_visibility}")

        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.log_level not in valid_log_levels:
            raise ConfigError(f"log_level must be one of: {valid_log_levels}")
```

## Advanced Patterns and Features

### Event-Driven Architecture

```python
class EventBus:
    """Simple event bus for decoupled communication."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, data: Any):
        """Publish an event to all subscribers."""
        for handler in self._handlers[event_type]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

# Usage in batch processor
class BatchProcessor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def process_repository(self, repo: Repository):
        self.event_bus.publish("repository.processing.started", repo)

        try:
            result = await self._do_processing(repo)
            self.event_bus.publish("repository.processing.completed", result)
        except Exception as e:
            self.event_bus.publish("repository.processing.failed", {
                "repository": repo,
                "error": e
            })
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
```

### Metrics and Observability

```python
class MetricsCollector:
    """Comprehensive metrics collection."""

    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.gauges: Dict[str, float] = {}
        self.start_time = time.time()

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] += value

    def record_histogram(self, name: str, value: float):
        """Record a histogram value."""
        self.histograms[name].append(value)

    def set_gauge(self, name: str, value: float):
        """Set a gauge value."""
        self.gauges[name] = value

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        uptime = time.time() - self.start_time

        summary = {
            "uptime_seconds": uptime,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {}
        }

        # Calculate histogram statistics
        for name, values in self.histograms.items():
            if values:
                summary["histograms"][name] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p50": self._percentile(values, 0.5),
                    "p95": self._percentile(values, 0.95),
                    "p99": self._percentile(values, 0.99)
                }

        return summary
```

## Performance Optimizations

### Async/Await Patterns

```python
class AsyncBatchProcessor:
    """High-performance async batch processing."""

    async def process_batch_optimized(
        self,
        repositories: List[Repository]
    ) -> BatchResult:
        """Optimized batch processing with async patterns."""

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_workers)

        # Create tasks with semaphore
        async def bounded_task(repo: Repository):
            async with semaphore:
                return await self.process_single_repository(repo)

        # Execute all tasks concurrently
        tasks = [bounded_task(repo) for repo in repositories]

        # Use asyncio.as_completed for real-time results
        results = []
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                self.emit_progress(len(results), len(repositories))
            except Exception as e:
                results.append(RepositoryResult.from_error(e))

        return BatchResult(results)
```

### Memory Management

```python
class MemoryEfficientProcessor:
    """Memory-efficient processing for large repository sets."""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.memory_monitor = MemoryMonitor()

    async def process_large_batch(
        self,
        repositories: AsyncIterable[Repository]
    ) -> AsyncGenerator[RepositoryResult, None]:
        """Process large batches with memory management."""

        batch = []

        async for repository in repositories:
            batch.append(repository)

            if len(batch) >= self.batch_size:
                # Process batch and yield results
                async for result in self._process_batch_chunk(batch):
                    yield result

                # Clear batch and check memory
                batch.clear()
                await self._check_memory_pressure()

        # Process remaining repositories
        if batch:
            async for result in self._process_batch_chunk(batch):
                yield result

    async def _check_memory_pressure(self):
        """Check and handle memory pressure."""
        usage = self.memory_monitor.get_memory_usage()

        if usage > 0.8:  # 80% memory usage
            await asyncio.sleep(0.1)  # Brief pause
            gc.collect()  # Force garbage collection
```

This comprehensive architecture documentation provides deep technical insights into the design patterns, implementation details, and advanced features of Git Batch Pull. The system demonstrates enterprise-grade software engineering practices with a focus on security, performance, maintainability, and extensibility.
