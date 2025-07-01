"""CLI interface for git-batch-pull."""

import subprocess
from typing import Optional

import typer

from .commands import main_command
from .health import health_command


def get_version() -> str:
    """Get the current version with git commit hash."""
    try:
        git_hash = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        return f"2.0.0 (git {git_hash})"
    except Exception:
        return "2.0.0"


def version_callback(value: bool) -> None:
    """Handle --version flag."""
    if value:
        print(f"git-batch-pull {get_version()}")
        raise typer.Exit()


def feedback_callback(value: bool) -> None:
    """Handle --feedback flag."""
    if value:
        print(
            "Report issues or feedback at: https://github.com/alpersonalwebsite/git_batch_pull/issues"
        )
        raise typer.Exit()


# Create the Typer app
app = typer.Typer()

# Add commands with intuitive names
app.command("sync")(main_command)  # Primary command - sync repositories
app.command("clone")(main_command)  # Alias for sync (more familiar to git users)
app.command("pull")(main_command)  # Alias for sync (git pull terminology)
app.command("batch")(main_command)  # Alias for sync (batch processing)
app.command("health")(health_command)  # Health diagnostics

__all__ = ["app"]
