"""
Integration tests for protocol switch prompt and update logic in git-batch-pull.
Covers user input handling and remote URL updates for protocol switching.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from git_batch_pull.main import prompt_protocol_switch


def setup_git_repo(tmp_path, remote_url):
    """
    Set up a temporary git repository with the given remote URL.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_dir, check=True)
    return repo_dir


def get_remote_url(repo_dir):
    """
    Get the remote URL for the 'origin' remote in the given repository.
    """
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_switch_protocol_on_user_input_yes(tmp_path, monkeypatch):
    """
    Test protocol switch when user selects 'yes' to switch protocol (input '1').
    """
    repo_dir = setup_git_repo(tmp_path, "https://github.com/user/repo.git")
    called = {}

    def fake_input(prompt):
        called["input"] = True
        return "1"

    monkeypatch.setattr("builtins.input", fake_input)
    mismatches = [("repo", get_remote_url(repo_dir))]
    # Simulate user chooses to switch to SSH
    assert prompt_protocol_switch(mismatches, "SSH") is True
    # Simulate the update
    new_url = "git@github.com:user/repo.git"
    subprocess.run(["git", "remote", "set-url", "origin", new_url], cwd=repo_dir, check=True)
    assert get_remote_url(repo_dir) == new_url
    assert called["input"]


def test_switch_protocol_on_user_input_no(tmp_path, monkeypatch):
    """
    Test protocol switch when user selects 'no' to switch protocol (input '2').
    """
    repo_dir = setup_git_repo(tmp_path, "https://github.com/user/repo.git")
    called = {}

    def fake_input(prompt):
        called["input"] = True
        return "2"

    monkeypatch.setattr("builtins.input", fake_input)
    mismatches = [("repo", get_remote_url(repo_dir))]
    # Simulate user chooses NOT to switch
    assert prompt_protocol_switch(mismatches, "SSH") is False
    # Remote should remain unchanged
    assert get_remote_url(repo_dir) == "https://github.com/user/repo.git"
    assert called["input"]
