"""Git operations service with enhanced security and error handling."""

import logging
from pathlib import Path
from typing import Optional

from ..exceptions import GitOperationError
from ..models import Repository
from ..security import PathValidator, SafeSubprocessRunner
from ..security.credential_manager import InteractiveCredentialManager


class GitService:
    """
    Handles secure and robust git operations for repositories.
    """

    def __init__(
        self,
        base_folder: Path,
        subprocess_runner: SafeSubprocessRunner,
        path_validator: PathValidator,
    ):
        """
        Initialize the Git service.

        Args:
            base_folder: Base directory for all repositories
            subprocess_runner: Safe subprocess runner
            path_validator: Path validator for security
        """
        self.base_folder = path_validator.validate_absolute_path(base_folder)
        self.subprocess_runner = subprocess_runner
        self.path_validator = path_validator
        self.logger = logging.getLogger(__name__)
        self.credential_manager = InteractiveCredentialManager()

        # Ensure base directory exists
        self.path_validator.ensure_directory_exists(self.base_folder)

    def get_repository_path(self, repo_name: str) -> Path:
        """
        Get the local path for a repository.

        Args:
            repo_name: Repository name

        Returns:
            Path to the local repository

        Raises:
            PathValidationError: If repo_name is invalid
        """
        safe_name = self.path_validator.validate_filename(repo_name)
        return self.base_folder / safe_name

    def has_uncommitted_changes(self, repo_path: Path) -> bool:
        """
        Check if a repository has uncommitted changes.

        Args:
            repo_path: Path to the repository

        Returns:
            True if there are uncommitted changes

        Raises:
            GitOperationError: If git command fails
        """
        try:
            result = self.subprocess_runner.run_git_command(
                ["git", "status", "--porcelain"], cwd=repo_path, timeout=10
            )
            return bool(result.stdout.strip())
        except Exception as e:
            self.logger.error(f"Error checking uncommitted changes in {repo_path}: {e}")
            return False

    def is_repository_empty(self, repo_path: Path) -> bool:
        """
        Check if a repository is empty (no commits).

        Args:
            repo_path: Path to the repository

        Returns:
            True if repository is empty
        """
        try:
            self.subprocess_runner.run_git_command(
                ["git", "rev-parse", "--verify", "HEAD"], cwd=repo_path, timeout=5
            )
            return False  # HEAD exists, so not empty
        except GitOperationError:
            return True  # No HEAD, repository is empty

    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """
        Get the current branch name.

        Args:
            repo_path: Path to the repository

        Returns:
            Current branch name or None if detached HEAD
        """
        try:
            result = self.subprocess_runner.run_git_command(
                ["git", "branch", "--show-current"], cwd=repo_path, timeout=5
            )
            return result.stdout.strip() or None
        except GitOperationError:
            return None

    def get_remote_url(self, repo_path: Path, remote: str = "origin") -> Optional[str]:
        """
        Get the URL of a remote.

        Args:
            repo_path: Path to the repository
            remote: Remote name (default: origin)

        Returns:
            Remote URL or None if not found
        """
        try:
            result = self.subprocess_runner.run_git_command(
                ["git", "remote", "get-url", remote], cwd=repo_path, timeout=5
            )
            return result.stdout.strip()
        except GitOperationError:
            return None

    def detect_protocol(self, repo_path: Path) -> Optional[str]:
        """
        Detect the protocol (ssh/https) of the origin remote.

        Args:
            repo_path: Path to the repository

        Returns:
            'ssh', 'https', or None if cannot determine
        """
        remote_url = self.get_remote_url(repo_path)
        if not remote_url:
            return None

        remote_url_lower = remote_url.lower()
        if remote_url_lower.startswith("git@") or remote_url_lower.startswith("ssh://"):
            return "ssh"
        elif remote_url_lower.startswith("https://"):
            return "https"
        else:
            return None

    def clone_repository(
        self, repository: Repository, use_ssh: bool = False, interactive_auth: bool = False
    ) -> None:
        """
        Clone a repository.

        Args:
            repository: Repository to clone
            use_ssh: Whether to use SSH URL
            interactive_auth: Whether to prompt for HTTPS credentials interactively

        Raises:
            GitOperationError: If clone fails
        """
        clone_url = repository.get_clone_url(use_ssh)
        repo_path = repository.local_path

        self.logger.info(f"Cloning {repository.name}...")
        self.logger.debug(
            f"Clone URL: {clone_url[:50]}..." if len(clone_url) > 50 else f"Clone URL: {clone_url}"
        )

        # Handle interactive authentication for HTTPS
        if not use_ssh and interactive_auth:
            try:
                username, token = self.credential_manager.get_credentials()
                clone_url = self.credential_manager.create_authenticated_url(
                    clone_url, username, token
                )
                self.logger.debug("Applied interactive credentials to clone URL")
            except Exception as e:
                self.logger.error(f"Failed to get credentials: {e}")
                raise GitOperationError(f"Authentication failed: {e}")

        # Ensure parent directory exists
        self.path_validator.ensure_directory_exists(repo_path.parent)

        try:
            self.subprocess_runner.run_git_command(
                ["git", "clone", clone_url, str(repo_path)],
                cwd=repo_path.parent,
                timeout=300,  # 5 minutes for clone
            )
            self.logger.info(f"Successfully cloned {repository.name}")
        except GitOperationError as e:
            self.logger.error(f"Failed to clone {repository.name}: {e}")
            raise

    def pull_repository(self, repository: Repository) -> None:
        """
        Pull latest changes for a repository.

        Args:
            repository: Repository to pull

        Raises:
            GitOperationError: If pull fails
        """
        repo_path = repository.local_path
        default_branch = repository.info.default_branch

        if not repo_path.exists():
            raise GitOperationError(f"Repository path does not exist: {repo_path}")

        if self.is_repository_empty(repo_path):
            self.logger.info(f"Repository {repository.name} is empty, nothing to pull")
            return

        if self.has_uncommitted_changes(repo_path):
            self.logger.warning(
                f"Repository {repository.name} has uncommitted changes, skipping pull"
            )
            return

        self.logger.info(f"Pulling {repository.name}...")

        try:
            # Checkout default branch
            self.subprocess_runner.run_git_command(
                ["git", "checkout", default_branch], cwd=repo_path, timeout=30
            )

            # Pull from origin
            self.subprocess_runner.run_git_command(
                ["git", "pull", "origin", default_branch], cwd=repo_path, timeout=60
            )

            self.logger.info(f"Successfully pulled {repository.name}")

        except GitOperationError as e:
            self.logger.error(f"Failed to pull {repository.name}: {e}")
            raise

    def update_remote_url(self, repo_path: Path, new_url: str, remote: str = "origin") -> None:
        """
        Update the URL of a remote.

        Args:
            repo_path: Path to the repository
            new_url: New remote URL
            remote: Remote name (default: origin)

        Raises:
            GitOperationError: If update fails
        """
        try:
            self.subprocess_runner.run_git_command(
                ["git", "remote", "set-url", remote, new_url], cwd=repo_path, timeout=10
            )
            self.logger.info(f"Updated {remote} remote URL to {new_url}")
        except GitOperationError as e:
            self.logger.error(f"Failed to update remote URL: {e}")
            raise

    def clone_or_pull(
        self, repository: Repository, use_ssh: bool = False, interactive_auth: bool = False
    ) -> None:
        """
        Clone repository if not present, otherwise pull latest changes.

        Args:
            repository: Repository to process
            use_ssh: Whether to use SSH URLs
            interactive_auth: Whether to prompt for HTTPS credentials interactively

        Raises:
            GitOperationError: If operation fails
        """
        if not repository.exists_locally:
            self.clone_repository(repository, use_ssh, interactive_auth)
        else:
            self.pull_repository(repository)

    def clear_cached_credentials(self) -> None:
        """Clear any cached interactive credentials."""
        self.credential_manager.clear_credentials()
        self.logger.debug("Cleared cached credentials from git service")
