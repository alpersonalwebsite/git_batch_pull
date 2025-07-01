"""
Extra unit tests for GitOperator in git_batch_pull.git_ops.
Covers already cloned and dirty repository scenarios with mocks.
"""

import os
from unittest.mock import patch

from git_batch_pull import git_ops


class DummyResult:
    """
    Dummy result object for simulating subprocess.run return values.
    """

    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_clone_or_pull_already_cloned(tmp_path):
    """
    Test clone_or_pull when the repository is already cloned and clean.
    """
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    # Simulate a repo already cloned, no uncommitted changes
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = DummyResult(returncode=0, stdout="", stderr="")
        git_op = git_ops.GitOperator(str(tmp_path))
        repo = {"name": "repo", "default_branch": "main", "clone_url": "url"}
        git_op.clone_or_pull(repo)


def test_clone_or_pull_dirty_repo(tmp_path):
    """
    Test clone_or_pull when the repository has uncommitted changes.
    """
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    # Simulate a repo with uncommitted changes
    with patch("subprocess.run") as mock_run:
        # First call: git status (dirty)
        mock_run.return_value = DummyResult(returncode=0, stdout="dirty", stderr="")
        git_op = git_ops.GitOperator(str(tmp_path))
        repo = {"name": "repo", "default_branch": "main", "clone_url": "url"}
        git_op.clone_or_pull(repo)
