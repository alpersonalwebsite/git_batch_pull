"""
Unit tests for protocol mismatch detection in git_batch_pull.protocol_utils.
Covers HTTPS, SSH, and no-remote scenarios.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import subprocess

from git_batch_pull.protocol_utils import detect_protocol_mismatch


def test_detect_protocol_mismatch_https(tmp_path):
    """
    Test detection of HTTPS protocol mismatch and warning message.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/user/repo.git"],
        cwd=repo_dir,
        check=True,
    )
    warning = detect_protocol_mismatch(str(repo_dir))
    assert "HTTPS" in warning
    assert "SSH keys" in warning


def test_detect_protocol_mismatch_ssh(tmp_path):
    """
    Test detection of SSH protocol mismatch and warning message.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:user/repo.git"],
        cwd=repo_dir,
        check=True,
    )
    warning = detect_protocol_mismatch(str(repo_dir))
    assert "SSH" in warning
    assert "HTTPS credentials" in warning


def test_detect_protocol_mismatch_none(tmp_path):
    """
    Test that no warning is returned when no remote is set.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    # No remote
    warning = detect_protocol_mismatch(str(repo_dir))
    assert warning == ""
