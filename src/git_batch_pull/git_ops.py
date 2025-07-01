import logging
import subprocess
from pathlib import Path
from typing import Dict

from git_batch_pull.exceptions import GitOperationError  # type: ignore[attr-defined]


class GitOperator:
    """
    Handles secure and robust git operations for repositories.
    """

    def __init__(self, base_folder: str):
        """
        Initialize the GitOperator.

        Args:
            base_folder: Path to the base folder for all repos.
        """
        self.base_folder = Path(base_folder)
        self.base_folder.mkdir(parents=True, exist_ok=True)

    def repo_path(self, repo_name: str) -> Path:
        """
        Return the local path for a given repo name.

        Args:
            repo_name: Name of the repository.
        Returns:
            Path to the local repository.
        """
        return self.base_folder / repo_name

    def has_uncommitted_changes(self, path: str) -> bool:
        """
        Check if a git repo has uncommitted changes.

        Args:
            path: Path to the local repository.
        Returns:
            True if there are uncommitted changes, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logging.error(f"Error checking uncommitted changes in {path}: {e}")
            return False

    def clone_or_pull(self, repo: Dict) -> None:
        """
        Clone the repo if not present, otherwise pull from default branch.
        Skips pull if uncommitted changes are detected.

        Args:
            repo: Repository metadata dict.
        Raises:
            GitOperationError: On git command failure.
        """
        path = self.repo_path(repo["name"])
        clone_url = repo["clone_url"]
        if not path.exists():
            logging.info(f"Cloning {repo['name']}...")
            logging.debug(f"Cloning {repo['name']} using URL: {clone_url}")
            try:
                subprocess.run(
                    ["git", "clone", clone_url, str(path)],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                logging.error(f"Clone failed for {repo['name']}: {e.stderr}")
                raise GitOperationError(f"Clone failed for {repo['name']}")
        # Check if repo is empty (no HEAD)
        git_dir = str(path)
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=git_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logging.info(f"Repo {repo['name']} is empty. Nothing to pull.")
                return
        except Exception:
            logging.info(f"Repo {repo['name']} is empty or not " f"initialized. Nothing to pull.")
            return
        if self.has_uncommitted_changes(str(path)):
            logging.warning(f"Repo {repo['name']} has uncommitted changes. " f"Skipping pull.")
            return
        logging.info(f"Pulling {repo['name']}...")
        try:
            subprocess.run(
                ["git", "checkout", repo["default_branch"]],
                cwd=path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "pull", "origin", repo["default_branch"]],
                cwd=path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Pull failed for {repo['name']}: {e.stderr}")
            raise GitOperationError(f"Pull failed for {repo['name']}")
        except Exception:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=git_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise Exception("Git command failed: " + result.stderr.strip())
