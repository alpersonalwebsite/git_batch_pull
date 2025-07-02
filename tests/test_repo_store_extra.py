"""
Unit tests for RepoStore class in git_batch_pull.repo_store.
Covers handling of corrupt JSON and multiple instance access.
"""

import json

import pytest

from git_batch_pull import repo_store


def test_repo_store_corrupt_json(tmp_path):
    """
    Test that RepoStore raises JSONDecodeError on corrupt JSON file.
    """
    path = tmp_path / "repos.json"
    with open(path, "w") as f:
        f.write("not a json")
    store = repo_store.RepoStore(str(path))
    with pytest.raises(json.JSONDecodeError):
        store.load()


# Note: True concurrent access would require threading/multiprocessing
# and is not typical for this class.
# Here we just simulate two instances reading/writing the same file.
def test_repo_store_multiple_instances(tmp_path):
    """
    Test that multiple RepoStore instances see consistent data when reading/writing the same file.
    """
    path = tmp_path / "repos.json"
    store1 = repo_store.RepoStore(str(path))
    store2 = repo_store.RepoStore(str(path))
    data = [{"name": "repo1"}]
    store1.save(data)
    assert store2.exists()
    assert store2.load() == data
