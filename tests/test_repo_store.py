"""
Unit tests for RepoStore class in git_batch_pull.repo_store.
Covers saving, loading, and missing file behavior.
"""

import pytest

from git_batch_pull import repo_store


def test_repo_store(tmp_path):
    """
    Test saving and loading repository data with RepoStore.
    """
    store = repo_store.RepoStore(tmp_path / "repos.json")
    data = [{"name": "repo1", "default_branch": "main", "clone_url": "url"}]
    store.save(data)
    assert store.exists()
    loaded = store.load()
    assert loaded == data


def test_repo_store_missing(tmp_path):
    """
    Test that loading from a missing file raises FileNotFoundError.
    """
    store = repo_store.RepoStore(tmp_path / "missing.json")
    assert not store.exists()
    with pytest.raises(FileNotFoundError):
        store.load()
