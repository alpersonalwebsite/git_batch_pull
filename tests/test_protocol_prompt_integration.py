"""
Integration tests for protocol mismatch prompt behavior in the git-batch-pull CLI.
Covers detection and user prompt logic for SSH/HTTPS protocol mismatches.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the CLI script
CLI_PATH = str(Path(__file__).parent.parent / "src/git_batch_pull/cli.py")


@pytest.mark.skip(
    reason="Integration test needs rework after refactoring. Protocol tested in unit tests."
)
@pytest.mark.parametrize(
    "remote_url,args_use_ssh,should_prompt",
    [
        ("git@github.com:user/repo.git", True, False),  # SSH matches --use-ssh
        ("https://github.com/user/repo.git", False, False),  # HTTPS matches default
        (
            "https://github.com/user/repo.git",
            True,
            True,
        ),  # HTTPS with --use-ssh (should prompt)
        (
            "git@github.com:user/repo.git",
            False,
            True,
        ),  # SSH with default (should prompt)
    ],
)
def test_protocol_prompt_behavior(remote_url, args_use_ssh, should_prompt, tmp_path):
    """
    Test protocol mismatch prompt logic in CLI for various remote/protocol combinations.
    Ensures prompt appears only when protocol mismatch is detected.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_dir, check=True)

    # Patch the repo discovery to only include our test repo
    # Simulate CLI args
    args = [
        sys.executable,
        CLI_PATH,
        "org",
        "user",
        "--repos",
        "repo",
        "--log-level",
        "ERROR",
    ]
    if args_use_ssh:
        args.append("--ssh")

    # Use env var to point to our test repo location if needed
    env = os.environ.copy()
    env["GIT_BATCH_PULL_TEST_REPO_PATH"] = str(repo_dir)

    # Run the CLI and capture output
    proc = subprocess.run(args, capture_output=True, text=True, env=env, input="2\n", timeout=10)
    output = proc.stdout + proc.stderr

    if should_prompt:
        assert "Protocol mismatch detected" in output or "protocol mismatch" in output
    else:
        assert "Protocol mismatch detected" not in output and "protocol mismatch" not in output
