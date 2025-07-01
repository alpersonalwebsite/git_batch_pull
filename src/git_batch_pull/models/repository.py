"""Repository data models."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RepositoryInfo:
    """Information about a GitHub repository."""

    name: str
    default_branch: str
    clone_url: str
    ssh_url: Optional[str] = None
    private: bool = False
    archived: bool = False
    fork: bool = False

    @classmethod
    def from_github_api(cls, repo_data: Dict) -> "RepositoryInfo":
        """Create RepositoryInfo from GitHub API response."""
        return cls(
            name=repo_data["name"],
            default_branch=repo_data.get("default_branch", "main"),
            clone_url=repo_data["clone_url"],
            ssh_url=repo_data.get("ssh_url"),
            private=repo_data.get("private", False),
            archived=repo_data.get("archived", False),
            fork=repo_data.get("fork", False),
        )


@dataclass
class Repository:
    """Local repository with associated metadata."""

    info: RepositoryInfo
    local_path: Path

    @property
    def name(self) -> str:
        """Get repository name."""
        return self.info.name

    @property
    def exists_locally(self) -> bool:
        """Check if repository exists locally."""
        return self.local_path.exists() and (self.local_path / ".git").exists()

    def get_clone_url(self, use_ssh: bool = False) -> str:
        """Get the appropriate clone URL based on protocol preference."""
        if use_ssh and self.info.ssh_url:
            return self.info.ssh_url
        return self.info.clone_url


@dataclass
class RepositoryBatch:
    """A batch of repositories to process."""

    repositories: List[Repository]
    entity_type: str  # "user" or "org"
    entity_name: str

    def filter_by_names(self, names: List[str]) -> "RepositoryBatch":
        """Filter repositories by name."""
        filtered_repos = [repo for repo in self.repositories if repo.name in names]
        return RepositoryBatch(
            repositories=filtered_repos,
            entity_type=self.entity_type,
            entity_name=self.entity_name,
        )

    def exclude_archived(self) -> "RepositoryBatch":
        """Exclude archived repositories."""
        active_repos = [repo for repo in self.repositories if not repo.info.archived]
        return RepositoryBatch(
            repositories=active_repos,
            entity_type=self.entity_type,
            entity_name=self.entity_name,
        )

    def exclude_forks(self) -> "RepositoryBatch":
        """Exclude forked repositories."""
        non_fork_repos = [repo for repo in self.repositories if not repo.info.fork]
        return RepositoryBatch(
            repositories=non_fork_repos,
            entity_type=self.entity_type,
            entity_name=self.entity_name,
        )
