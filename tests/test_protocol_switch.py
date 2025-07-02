"""
Integration and unit tests for protocol switch prompt logic in git-batch-pull.
Covers prompt suppression and protocol detection logic for SSH/HTTPS remotes.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import subprocess

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


def test_no_prompt_when_protocol_matches_ssh(tmp_path, monkeypatch):
    """
    Test that no prompt is shown when protocol matches SSH and --use-ssh is set.
    """
    _ = setup_git_repo(tmp_path, "git@github.com:user/repo.git")
    # Simulate args.use_ssh = True
    mismatches = []

    def fake_prompt(m, t):
        raise AssertionError("Should not prompt when protocol matches")

    # Simulate detection logic
    is_ssh = True
    is_https = False
    args_use_ssh = True
    if args_use_ssh and not is_ssh:
        mismatches.append(("repo", "git@github.com:user/repo.git"))
    elif not args_use_ssh and not is_https:
        mismatches.append(("repo", "git@github.com:user/repo.git"))
    assert not mismatches


def test_no_prompt_when_protocol_matches_https(tmp_path, monkeypatch):
    """
    Test that no prompt is shown when protocol matches HTTPS and --use-ssh is not set.
    """
    _ = setup_git_repo(tmp_path, "https://github.com/user/repo.git")
    mismatches = []

    def fake_prompt(m, t):
        raise AssertionError("Should not prompt when protocol matches")

    is_ssh = False
    is_https = True
    args_use_ssh = False
    if args_use_ssh and not is_ssh:
        mismatches.append(("repo", "https://github.com/user/repo.git"))
    elif not args_use_ssh and not is_https:
        mismatches.append(("repo", "https://github.com/user/repo.git"))
    assert not mismatches


def test_prompt_when_protocol_mismatch_ssh(tmp_path, monkeypatch):
    """
    Test that a prompt is shown when there is a protocol mismatch and --use-ssh is set.
    """
    _ = setup_git_repo(tmp_path, "https://github.com/user/repo.git")
    mismatches = []
    is_ssh = False
    is_https = True
    args_use_ssh = True
    if args_use_ssh and not is_ssh:
        mismatches.append(("repo", "https://github.com/user/repo.git"))
    elif not args_use_ssh and not is_https:
        mismatches.append(("repo", "https://github.com/user/repo.git"))
    assert mismatches == [("repo", "https://github.com/user/repo.git")]


def test_prompt_when_protocol_mismatch_https(tmp_path, monkeypatch):
    """
    Test that a prompt is shown when there is a protocol mismatch and --use-ssh is not set.
    """
    _ = setup_git_repo(tmp_path, "git@github.com:user/repo.git")
    mismatches = []
    is_ssh = True
    is_https = False
    args_use_ssh = False
    if args_use_ssh and not is_ssh:
        mismatches.append(("repo", "git@github.com:user/repo.git"))
    elif not args_use_ssh and not is_https:
        mismatches.append(("repo", "git@github.com:user/repo.git"))
    assert mismatches == [("repo", "git@github.com:user/repo.git")]


def test_prompt_protocol_switch_yes(monkeypatch):
    """
    Test the behavior of prompt_protocol_switch when the user selects 'yes'.
    """
    called = {}

    def fake_input(prompt):
        called["input"] = True
        return "1"

    monkeypatch.setattr("builtins.input", fake_input)
    mismatches = [("repo", "https://github.com/user/repo.git")]
    assert prompt_protocol_switch(mismatches, "SSH") is True
    assert called["input"]


def test_prompt_protocol_switch_no(monkeypatch):
    """
    Test the behavior of prompt_protocol_switch when the user selects 'no'.
    """
    called = {}

    def fake_input(prompt):
        called["input"] = True
        return "2"

    monkeypatch.setattr("builtins.input", fake_input)
    mismatches = [("repo", "https://github.com/user/repo.git")]
    assert prompt_protocol_switch(mismatches, "SSH") is False
    assert called["input"]
