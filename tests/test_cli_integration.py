"""
Integration tests for CLI argument handling and feedback in git-batch-pull.
Covers missing arguments, invalid entity types, and feedback option.
"""

import subprocess
from pathlib import Path

# Use the installed CLI command
CLI_COMMAND = str(Path(__file__).parent.parent / ".venv" / "bin" / "git-batch-pull")


def run_cli(args):
    """
    Run the CLI with the given arguments and return the completed process.
    """
    return subprocess.run([CLI_COMMAND] + args, capture_output=True, text=True)


def test_cli_missing_args():
    """
    Test that running the CLI with missing arguments returns an error and usage info.
    """
    result = run_cli([])
    assert result.returncode != 0
    assert (
        "usage" in result.stderr.lower()
        or "usage" in result.stdout.lower()
        or "missing command" in result.stderr.lower()
    )


def test_cli_invalid_entity_type():
    """
    Test that running the CLI with an invalid entity type returns an error.
    """
    result = run_cli(["sync", "invalid", "foo"])
    assert result.returncode != 0
    assert (
        "invalid choice" in result.stderr.lower()
        or "invalid choice" in result.stdout.lower()
        or "must be one of: org, user" in result.stderr.lower()
        or "must be one of: org, user" in result.stdout.lower()
        or "invalid entity type" in result.stderr.lower()
        or "invalid entity type" in result.stdout.lower()
        or "invalid value" in result.stderr.lower()
        or "invalid value" in result.stdout.lower()
    )


def test_cli_feedback():
    """
    Test that the CLI feedback option displays feedback or report information.
    """
    result = run_cli(["sync", "org", "foo", "--feedback"])
    assert result.returncode == 0
    assert "feedback" in result.stdout.lower() or "report" in result.stdout.lower()
