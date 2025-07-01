"""Health check command for git-batch-pull."""

import asyncio
from typing import Optional

import typer

from ..core.health_check import HealthChecker, format_health_report


def health_command(
    config_file: Optional[str] = typer.Option(None, "--config", help="Path to configuration file"),
) -> None:
    """
    Run system health checks.

    Checks system requirements, network connectivity, GitHub API access,
    and configuration validity.
    """
    # Load configuration if provided
    config_obj = None
    if config_file:
        from ..config import load_config

        try:
            config_obj = load_config(config_file)
        except Exception as e:
            typer.echo(f"Warning: Could not load config: {e}", err=True)

    # Run health checks
    checker = HealthChecker(config_obj)

    async def run_checks():
        return await checker.run_all_checks()

    try:
        results = asyncio.run(run_checks())
        report = format_health_report(results)
        typer.echo(report)

        # Exit with error code if there are any errors
        has_errors = any(result.status == "error" for result in results)
        if has_errors:
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Health check failed: {e}", err=True)
        raise typer.Exit(1)
