"""CLI interface creation and configuration."""

import subprocess

import typer

from .commands import main_command


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
        return f"1.0.0 (git {git_hash})"
    except Exception:
        return "1.0.0"


def version_callback(value: bool) -> None:
    """Handle --version flag."""
    if value:
        print(f"git-batch-pull {get_version()}")
        raise typer.Exit()


def feedback_callback(value: bool) -> None:
    """Handle --feedback flag."""
    if value:
        print("Report issues or feedback at: https://github.com/your/repo/issues")
        raise typer.Exit()


def create_cli_app() -> typer.Typer:
    """
    Create and configure the main CLI application.

    Returns:
        Configured Typer application
    """
    # Create a simple app that directly uses our main command
    return typer.Typer(
        name="git-batch-pull",
        help="Clone and pull GitHub repos for a user/org, securely and robustly.",
        no_args_is_help=True,
        add_completion=True,
        callback=main_command,  # Use main_command as the app callback
    )
