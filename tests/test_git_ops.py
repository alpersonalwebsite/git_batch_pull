"""
Unit tests for git_ops module in git-batch-pull.
Covers detection of uncommitted changes and error handling in clone/pull operations.
"""

import os
from unittest.mock import patch

import pytest

from git_batch_pull import git_ops


def test_has_uncommitted_changes(tmp_path):
    """
    Test detection of uncommitted changes in a git repository.
    """
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    os.system(f"git init {repo_path}")
    with open(repo_path / "file.txt", "w") as f:
        f.write("test")
    os.system(f"git -C {repo_path} add .")
    git_op = git_ops.GitOperator(str(tmp_path))
    assert git_op.has_uncommitted_changes(str(repo_path))


def test_clone_or_pull_handles_error(tmp_path):
    """
    Test that clone_or_pull handles subprocess errors gracefully and raises exceptions.
    """
    git_op = git_ops.GitOperator(str(tmp_path))
    repo = {
        "name": "failrepo",
        "default_branch": "main",
        "clone_url": "https://invalid.url/repo.git",
    }
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Mocked git failure")
        with pytest.raises(Exception):
            git_op.clone_or_pull(repo)
