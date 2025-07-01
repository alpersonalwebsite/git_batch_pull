# Technical Architecture Overview

## System Architecture

Git Batch Pull implements a **layered architecture** with clear separation of concerns, following modern software engineering principles and enterprise patterns.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (Typer)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Main Command    │  │ Health Command  │  │   Global    │  │
│  │                 │  │                 │  │   Options   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   Handler Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Logging Handler │  │  Error Handler  │  │   Callback  │  │
│  │   - Structured  │  │   - Sanitized   │  │   Handlers  │  │
│  │   - Multi-level │  │   - Recovery    │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Core Business Logic                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Batch Processor │  │Protocol Handler │  │Plugin Mgr   │  │
│  │ - Parallel      │  │ - SSH/HTTPS     │  │- Discovery  │  │
│  │ - Rate Limiting │  │ - Mismatch      │  │- Loading    │  │
│  │ - Error Handling│  │ - Switching     │  │- Execution  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  GitHub Service │  │   Git Service   │  │ Repository  │  │
│  │  - API Client   │  │  - Clone/Pull   │  │  Service    │  │
│  │  - Auth/Token   │  │  - Validation   │  │ - Filtering │  │
│  │  - Rate Limits  │  │  - Security     │  │ - Caching   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Security Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Token Manager   │  │ Path Validator  │  │ Subprocess  │  │
│  │ - Keyring       │  │ - Traversal     │  │   Runner    │  │
│  │ - Encryption    │  │ - Symlinks      │  │ - Injection │  │
│  │ - Sanitization  │  │ - Permissions   │  │ - Timeout   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │     Models      │  │   Exceptions    │  │   Config    │  │
│  │ - Repository    │  │ - Hierarchy     │  │ - Loading   │  │
│  │ - Config        │  │ - Sanitization  │  │ - Validation│  │
│  │ - Results       │  │ - Recovery      │  │ - Precedence│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### 1. Dependency Injection
```python
class ServiceContainer:
    """Manages all service dependencies with proper injection."""

    def __init__(self, config: Config):
        self.config = config
        self._github_service = None
        self._git_service = None
        self._repository_service = None

    @property
    def github_service(self) -> GitHubService:
        """Lazy-loaded GitHub service with dependencies."""
        if self._github_service is None:
            self._github_service = GitHubService(
                token=self.config.github_token,
                use_keyring=self.config.use_keyring
            )
        return self._github_service
```

#### 2. Service Layer Pattern
```python
class RepositoryService:
    """Repository management with clear business logic separation."""

    def __init__(self, github_service: GitHubService, config: Config):
        self.github_service = github_service
        self.config = config
        self.cache = RepoCache()

    def get_repositories(self, entity_type: str, entity_name: str) -> RepositoryBatch:
        """Business logic for repository retrieval with caching."""
        # Check cache first
        cached = self.cache.get(entity_type, entity_name)
        if cached and not self._is_stale(cached):
            return cached

        # Fetch from GitHub API
        repositories = self.github_service.fetch_repositories(entity_type, entity_name)

        # Cache results
        self.cache.store(entity_type, entity_name, repositories)

        return repositories
```

#### 3. Strategy Pattern
```python
class ProtocolHandler:
    """Strategy pattern for different protocol handling approaches."""

    def __init__(self, repository_service: RepositoryService):
        self.repository_service = repository_service
        self.strategies = {
            "interactive": InteractiveProtocolStrategy(),
            "automatic": AutomaticProtocolStrategy(),
            "skip": SkipProtocolStrategy()
        }

    def handle_mismatches(self, strategy: str, **kwargs):
        """Apply selected strategy for protocol mismatch handling."""
        handler = self.strategies.get(strategy, self.strategies["interactive"])
        return handler.handle(self.repository_service, **kwargs)
```

## Core Components

### 1. Data Models

#### Repository Model
```python
@dataclass
class Repository:
    """Immutable repository representation with computed properties."""

    name: str
    url: str
    ssh_url: str
    local_path: Path
    is_private: bool
    is_archived: bool
    is_fork: bool
    last_updated: Optional[datetime] = None

    def get_clone_url(self, use_ssh: bool = False) -> str:
        """Strategy method for URL selection."""
        return self.ssh_url if use_ssh else self.url

    def exists_locally(self) -> bool:
        """Check local existence with proper validation."""
        return self.local_path.exists() and self.local_path.is_dir()

    def is_git_repository(self) -> bool:
        """Validate git repository structure."""
        git_dir = self.local_path / ".git"
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())
```

#### Configuration Model
```python
@dataclass
class Config:
    """Configuration with validation and type safety."""

    github_token: str
    local_folder: Path
    repo_visibility: str = "all"
    max_workers: int = 1
    log_level: str = "INFO"
    use_keyring: bool = False

    def __post_init__(self):
        """Post-initialization validation."""
        self.validate()
        self.local_folder = Path(self.local_folder).resolve()

    def validate(self):
        """Comprehensive configuration validation."""
        if not self.github_token:
            raise ConfigError("GitHub token is required")

        if self.repo_visibility not in ["all", "public", "private"]:
            raise ConfigError("Invalid repo_visibility")

        if not 1 <= self.max_workers <= 20:
            raise ConfigError("max_workers must be between 1 and 20")
```

### 2. Service Architecture

#### GitHub Service
```python
class GitHubService:
    """GitHub API integration with enterprise features."""

    def __init__(self, token: str, use_keyring: bool = False):
        self.token_manager = SecureTokenManager()
        self.rate_limiter = RateLimiter()
        self.session = self._create_secure_session()

        if use_keyring:
            self.token = self.token_manager.get_token("github")
        else:
            self.token = token

    async def get_repositories(
        self,
        entity_type: str,
        entity_name: str,
        visibility: str = "all"
    ) -> RepositoryBatch:
        """Async repository fetching with pagination and error handling."""
        repositories = []

        async for page in self._paginate_repositories(entity_type, entity_name, visibility):
            repositories.extend(page)

        return RepositoryBatch(
            repositories=repositories,
            entity_type=entity_type,
            entity_name=entity_name,
            total_count=len(repositories)
        )

    async def _paginate_repositories(self, entity_type: str, entity_name: str, visibility: str):
        """Handle GitHub API pagination with rate limiting."""
        page = 1
        per_page = 100

        while True:
            await self.rate_limiter.wait_if_needed()

            response = await self.session.get(
                f"https://api.github.com/{entity_type}s/{entity_name}/repos",
                params={"page": page, "per_page": per_page, "visibility": visibility}
            )

            response.raise_for_status()
            data = response.json()

            if not data:
                break

            yield [Repository.from_github_data(repo) for repo in data]
            page += 1
```

### 3. Security Architecture

#### Token Security
```python
class SecureTokenManager:
    """Enterprise-grade token management."""

    def __init__(self):
        self.keyring_service = "git_batch_pull"

    def store_token(self, service: str, token: str):
        """Store token with encryption and validation."""
        # Validate token format
        if not self._is_valid_github_token(token):
            raise ValidationError("Invalid GitHub token format")

        # Store encrypted
        keyring.set_password(self.keyring_service, service, token)

        # Log security event (sanitized)
        logger.info(f"Token stored for service: {service}")

    def get_token(self, service: str) -> Optional[str]:
        """Retrieve and validate stored token."""
        token = keyring.get_password(self.keyring_service, service)

        if token and self._is_valid_github_token(token):
            return token

        return None

    def _is_valid_github_token(self, token: str) -> bool:
        """Validate GitHub token format."""
        return (
            token.startswith(('ghp_', 'github_pat_')) and
            len(token) >= 40 and
            token.replace('_', '').replace('-', '').isalnum()
        )
```

#### Path Security
```python
class PathValidator:
    """Comprehensive path validation and security."""

    @staticmethod
    def validate_and_resolve(path: str, base_path: Optional[str] = None) -> Path:
        """Validate path against security threats."""
        # Convert to Path and resolve
        path_obj = Path(path).resolve()

        # Check for directory traversal
        if base_path:
            base = Path(base_path).resolve()
            try:
                path_obj.relative_to(base)
            except ValueError:
                raise PathValidationError(f"Path outside base directory: {path}")

        # Check for dangerous system paths
        dangerous_prefixes = ["/etc", "/var", "/usr", "/bin", "/sbin", "/sys", "/proc"]
        str_path = str(path_obj)

        for prefix in dangerous_prefixes:
            if str_path.startswith(prefix):
                raise PathValidationError(f"Access to system path not allowed: {path}")

        # Check for symlink attacks
        if path_obj.is_symlink():
            target = path_obj.readlink()
            if target.is_absolute():
                raise PathValidationError(f"Absolute symlink not allowed: {path}")

        return path_obj
```

### 4. Error Handling Architecture

#### Exception Hierarchy
```python
class GitBatchPullError(Exception):
    """Base exception with enhanced error context."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize exception for logging/monitoring."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class ConfigError(GitBatchPullError):
    """Configuration and validation errors."""
    pass

class SecurityError(GitBatchPullError):
    """Security-related errors with audit logging."""

    def __init__(self, message: str, security_context: Optional[Dict[str, Any]] = None):
        super().__init__(message, security_context)
        self._audit_security_event()

    def _audit_security_event(self):
        """Log security event for monitoring."""
        audit_logger.warning(f"Security error: {self}", extra=self.context)
```

### 5. Plugin Architecture

#### Plugin System
```python
class PluginManager:
    """Dynamic plugin discovery and execution."""

    def __init__(self):
        self.plugins = {}
        self.discover_plugins()

    def discover_plugins(self):
        """Discover plugins via entry points."""
        for entry_point in pkg_resources.iter_entry_points('git_batch_pull_plugins'):
            try:
                plugin_class = entry_point.load()
                plugin_instance = plugin_class()
                self.plugins[entry_point.name] = plugin_instance
                logger.info(f"Loaded plugin: {entry_point.name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {entry_point.name}: {e}")

    def execute_plugins(self, event: str, context: Dict[str, Any]):
        """Execute all plugins for a specific event."""
        for name, plugin in self.plugins.items():
            try:
                if hasattr(plugin, event):
                    method = getattr(plugin, event)
                    method(context)
            except Exception as e:
                logger.error(f"Plugin {name} failed on {event}: {e}")

class BasePlugin:
    """Base class for all plugins."""

    def before_batch_processing(self, context: Dict[str, Any]):
        """Called before batch processing starts."""
        pass

    def after_repository_processed(self, context: Dict[str, Any]):
        """Called after each repository is processed."""
        pass

    def after_batch_processing(self, context: Dict[str, Any]):
        """Called after batch processing completes."""
        pass
```

## Performance & Scalability

### Parallel Processing
```python
class BatchProcessor:
    """High-performance parallel repository processing."""

    def __init__(self, git_service: GitService, max_workers: int = 1):
        self.git_service = git_service
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_batch(self, batch: RepositoryBatch, **kwargs) -> BatchResult:
        """Process repositories with intelligent parallelization."""
        results = []
        errors = []

        # Create futures for all repositories
        futures = {
            self.executor.submit(self._process_repository, repo, **kwargs): repo
            for repo in batch.repositories
        }

        # Process completed futures with progress tracking
        with tqdm(total=len(futures), desc="Processing repositories") as pbar:
            for future in as_completed(futures):
                repo = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result.success:
                        pbar.set_postfix({"status": "success", "repo": repo.name})
                    else:
                        pbar.set_postfix({"status": "failed", "repo": repo.name})
                except Exception as e:
                    errors.append((repo.name, e))
                    pbar.set_postfix({"status": "error", "repo": repo.name})
                finally:
                    pbar.update(1)

        return BatchResult(
            processed=len(results),
            failed=len(errors),
            total=len(batch.repositories),
            errors=errors
        )
```

### Caching Strategy
```python
class RepositoryCache:
    """Intelligent repository metadata caching."""

    def __init__(self, cache_dir: Path, ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # Time to live in seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, entity_type: str, entity_name: str) -> Optional[RepositoryBatch]:
        """Get cached repository batch if valid."""
        cache_file = self._get_cache_file(entity_type, entity_name)

        if not cache_file.exists():
            return None

        # Check if cache is stale
        if self._is_stale(cache_file):
            cache_file.unlink()  # Remove stale cache
            return None

        try:
            with cache_file.open('r') as f:
                data = json.load(f)
                return RepositoryBatch.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Invalid cache file {cache_file}: {e}")
            cache_file.unlink()  # Remove corrupted cache
            return None

    def store(self, entity_type: str, entity_name: str, batch: RepositoryBatch):
        """Store repository batch in cache."""
        cache_file = self._get_cache_file(entity_type, entity_name)

        with cache_file.open('w') as f:
            json.dump(batch.to_dict(), f, indent=2, default=str)

        logger.debug(f"Cached {len(batch.repositories)} repositories for {entity_name}")
```

This technical overview demonstrates the sophisticated architecture that makes Git Batch Pull suitable for enterprise environments while maintaining simplicity for individual developers.
  class MyPlugin(PluginBase):
      def run(self, *args, **kwargs):
          print("Hello from plugin!")
  ```
- See `src/example_plugin.py` for a template.

## Security Model
- Never logs secrets or sensitive data
- All subprocesses use `shell=False` and validate input
- Custom exception hierarchy for robust error handling
- Responsible disclosure: see `SECURITY.md`

## Testing & Coverage
- Run `pytest --cov=src` for coverage
- Property-based and cross-platform tests included
- Integration test placeholder for real-world scenarios

---
See the main `README.md` for more details and full CLI usage.
