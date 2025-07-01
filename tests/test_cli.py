"""
Integration tests for the git-batch-pull CLI interface.
Covers help and version output for CLI entry point.
"""

import subprocess
from pathlib import Path

# Use the installed CLI command
CLI_COMMAND = str(Path(__file__).parent.parent / ".venv" / "bin" / "git-batch-pull")


def test_cli_help():
    """
    Test that the CLI help command runs successfully and displays usage info.
    """
    result = subprocess.run([CLI_COMMAND, "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "commands" in result.stdout.lower()


def test_cli_version():
    """
    Test that the CLI version command runs successfully and displays version info.
    """
    result = subprocess.run([CLI_COMMAND, "sync", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "git-batch-pull" in result.stdout.lower()
