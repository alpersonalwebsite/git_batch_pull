import json
import os
from typing import Dict, List


class RepoStore:
    """
    Handles secure storage and retrieval of repository metadata.
    """

    def __init__(self, path: str):
        """
        Initialize the RepoStore.

        Args:
            path: Path to the metadata file.
        """
        self.path = path

    def save(self, repos: List[Dict]) -> None:
        """
        Save repository metadata to disk.

        Args:
            repos: List of repository metadata dicts.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(repos, f, indent=2)

    def load(self) -> List[Dict]:
        """
        Load repository metadata from disk.

        Returns:
            List of repository metadata dicts.
        """
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def exists(self) -> bool:
        """
        Check if the metadata file exists.

        Returns:
            True if the file exists, False otherwise.
        """
        return os.path.exists(self.path)
