"""Dependency injection container for services."""

from ..models import Config
from ..security import PathValidator, SafeSubprocessRunner, SecureTokenManager
from .git_service import GitService
from .github_service import GitHubService
from .repository_service import RepositoryService


class ServiceContainer:
    """Dependency injection container for all services."""

    def __init__(self, config: Config):
        self.config = config

        # Security components
        self.token_manager = SecureTokenManager(use_keyring=False)  # Can be configured
        self.subprocess_runner = SafeSubprocessRunner()
        self.path_validator = PathValidator()

        # Core services
        self._github_service = None
        self._git_service = None
        self._repository_service = None

    @property
    def github_service(self) -> GitHubService:
        """Get GitHub service instance."""
        if self._github_service is None:
            token = self.token_manager.get_token()
            self._github_service = GitHubService(token, self.subprocess_runner)
        return self._github_service

    @property
    def git_service(self) -> GitService:
        """Get Git service instance."""
        if self._git_service is None:
            self._git_service = GitService(
                base_folder=self.config.local_folder,
                subprocess_runner=self.subprocess_runner,
                path_validator=self.path_validator,
            )
        return self._git_service

    @property
    def repository_service(self) -> RepositoryService:
        """Get Repository service instance."""
        if self._repository_service is None:
            repo_store_path = (
                self.config.local_folder / f".repos_{hash(self.config.local_folder)}.json"
            )
            self._repository_service = RepositoryService(
                store_path=repo_store_path,
                github_service=self.github_service,
                git_service=self.git_service,
            )
        return self._repository_service

    def configure_keyring(self, use_keyring: bool) -> None:
        """Configure keyring usage for token management."""
        self.token_manager = SecureTokenManager(use_keyring=use_keyring)
