"""Repository management service combining GitHub API and local git operations."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from ..models import Repository, RepositoryBatch, RepositoryInfo
from .git_service import GitService
from .github_service import GitHubService


class RepositoryService:
    """
    High-level service for managing repositories with caching and filtering.
    """

    def __init__(self, store_path: Path, github_service: GitHubService, git_service: GitService):
        """
        Initialize the repository service.

        Args:
            store_path: Path to the repository metadata cache file
            github_service: GitHub API service
            git_service: Git operations service
        """
        self.store_path = store_path
        self.github_service = github_service
        self.git_service = git_service
        self.logger = logging.getLogger(__name__)

    def get_repositories(
        self,
        entity_type: str,
        entity_name: str,
        repo_visibility: str = "all",
        use_cache: bool = True,
        include_forks: bool = False,
        include_archived: bool = False,
        repo_names: Optional[List[str]] = None,
        repo_file: Optional[str] = None,
        local_folder: Optional[str] = None,
    ) -> RepositoryBatch:
        """
        Get repositories for a GitHub entity with optional filtering.

        Args:
            entity_type: Type of entity ('user' or 'org')
            entity_name: Name of the GitHub user or organization
            repo_visibility: Repository visibility ('all', 'public', 'private')
            use_cache: Whether to use cached data
            include_forks: Whether to include forked repositories
            include_archived: Whether to include archived repositories
            repo_names: Optional list of specific repository names to filter
            repo_file: Optional file containing repository names to filter
            local_folder: Optional local folder path for repositories

        Returns:
            RepositoryBatch containing filtered repositories
        """
        # Get repository info from GitHub API
        repo_infos = self._get_repository_infos(
            entity_type, entity_name, repo_visibility, use_cache
        )

        # Apply filters
        filtered_infos = self._apply_filters(
            repo_infos, include_forks, include_archived, repo_names, repo_file
        )

        # Convert to Repository objects
        repositories = []
        for info in filtered_infos:
            repo = Repository(
                info=info, local_path=Path(self._get_local_path(info.name, local_folder))
            )
            repositories.append(repo)

        return RepositoryBatch(
            repositories=repositories, entity_type=entity_type, entity_name=entity_name
        )

    def detect_protocol_mismatches(
        self, batch_or_repositories, intended_protocol: str
    ) -> List[tuple[str, str]]:
        """
        Detect protocol mismatches in a repository batch or list.

        Args:
            batch_or_repositories: Repository batch or list of repositories to check
            intended_protocol: Intended protocol ('ssh' or 'https')

        Returns:
            List of (repo_name, current_url) tuples for mismatched repositories
        """
        mismatches = []

        # Handle both RepositoryBatch and list of repositories
        if hasattr(batch_or_repositories, "repositories"):
            repositories = batch_or_repositories.repositories
        else:
            repositories = batch_or_repositories

        for repository in repositories:
            if not repository.exists_locally:
                continue

            current_protocol = self.git_service.detect_protocol(repository.local_path)
            if current_protocol and current_protocol != intended_protocol:
                current_url = self.git_service.get_remote_url(repository.local_path)
                if current_url:
                    mismatches.append((repository.name, current_url))

        return mismatches

    def fix_protocol_mismatches(
        self, batch: RepositoryBatch, intended_protocol: str, entity_name: str
    ) -> None:
        """
        Fix protocol mismatches by updating remote URLs.

        Args:
            batch: Repository batch to fix
            intended_protocol: Intended protocol ('ssh' or 'https')
            entity_name: GitHub entity name
        """
        mismatches = self.detect_protocol_mismatches(batch, intended_protocol)

        for repo_name, current_url in mismatches:
            # Find the repository in the batch
            repository = next((r for r in batch.repositories if r.name == repo_name), None)
            if repository:
                # Get the new URL based on intended protocol
                new_url = repository.get_clone_url(use_ssh=(intended_protocol == "ssh"))

                # Update the remote URL
                self.git_service.update_remote_url(repository.local_path, new_url)
                self.logger.info(f"Updated {repo_name} remote URL to {intended_protocol.upper()}")

    def _get_repository_infos(
        self, entity_type: str, entity_name: str, repo_visibility: str, use_cache: bool
    ) -> List[RepositoryInfo]:
        """Get repository information with caching support."""
        if use_cache:
            cached_repos = self._load_from_cache()
            if cached_repos:
                self.logger.debug(f"Using cached data for {entity_type}/{entity_name}")
                return cached_repos

        # Fetch from GitHub API
        self.logger.info(f"Fetching repositories for {entity_type}/{entity_name}")
        repo_dicts = self.github_service.get_repositories(entity_type, entity_name, repo_visibility)

        # Convert to RepositoryInfo objects
        repo_infos = [RepositoryInfo.from_github_api(repo_dict) for repo_dict in repo_dicts]

        # Save to cache
        self._save_to_cache(repo_infos)

        return repo_infos

    def _apply_filters(
        self,
        repo_infos: List[RepositoryInfo],
        include_forks: bool,
        include_archived: bool,
        repo_names: Optional[List[str]],
        repo_file: Optional[str],
    ) -> List[RepositoryInfo]:
        """Apply various filters to repository list."""
        filtered = repo_infos[:]

        # Filter by fork status
        if not include_forks:
            filtered = [r for r in filtered if not r.fork]

        # Filter by archived status
        if not include_archived:
            filtered = [r for r in filtered if not r.archived]

        # Filter by specific repository names
        if repo_names:
            filtered = [r for r in filtered if r.name in repo_names]
        elif repo_file:
            names_from_file = self._read_repo_names_from_file(repo_file)
            filtered = [r for r in filtered if r.name in names_from_file]

        return filtered

    def _get_local_path(self, repo_name: str, local_folder: Optional[str]) -> str:
        """Get the local path for a repository."""
        if local_folder:
            return str(Path(local_folder) / repo_name)
        return repo_name

    def _save_to_cache(self, repositories: List[RepositoryInfo]) -> None:
        """Save repositories to cache file."""
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dictionaries for JSON serialization
            repo_dicts = []
            for repo in repositories:
                repo_dict = {
                    "name": repo.name,
                    "default_branch": repo.default_branch,
                    "clone_url": repo.clone_url,
                    "ssh_url": repo.ssh_url,
                    "private": repo.private,
                    "archived": repo.archived,
                    "fork": repo.fork,
                }
                repo_dicts.append(repo_dict)

            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(repo_dicts, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved {len(repositories)} repositories to cache")

        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")

    def _load_from_cache(self) -> List[RepositoryInfo]:
        """Load repositories from cache file."""
        try:
            if not self.store_path.exists():
                return []

            with open(self.store_path, "r", encoding="utf-8") as f:
                repo_dicts = json.load(f)

            # Convert from dictionaries to RepositoryInfo objects
            repositories = []
            for repo_dict in repo_dicts:
                repo_info = RepositoryInfo(
                    name=repo_dict["name"],
                    default_branch=repo_dict["default_branch"],
                    clone_url=repo_dict["clone_url"],
                    ssh_url=repo_dict.get("ssh_url"),
                    private=repo_dict.get("private", False),
                    archived=repo_dict.get("archived", False),
                    fork=repo_dict.get("fork", False),
                )
                repositories.append(repo_info)

            self.logger.debug(f"Loaded {len(repositories)} repositories from cache")
            return repositories

        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return []

    def _read_repo_names_from_file(self, file_path: str) -> List[str]:
        """Read repository names from a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
            return names
        except Exception as e:
            self.logger.error(f"Failed to read repository names from {file_path}: {e}")
            return []
