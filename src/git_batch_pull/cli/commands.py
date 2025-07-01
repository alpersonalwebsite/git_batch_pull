"""CLI commands for git-batch-pull."""

import logging
import subprocess
from typing import Optional

import typer

from ..core import BatchProcessor, ProtocolHandler
from ..handlers.error_handler import error_handler
from ..handlers.logging_handler import logging_handler
from ..models import Config
from ..services import ServiceContainer


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
        typer.echo(f"git-batch-pull {get_version()}")
        raise typer.Exit()


def feedback_callback(value: bool) -> None:
    """Handle --feedback flag."""
    if value:
        typer.echo("Report issues or feedback at: https://github.com/your/repo/issues")
        raise typer.Exit()


def main_command(
    entity_type: str = typer.Argument(
        ..., help="GitHub entity type (org or user)", metavar="ENTITY_TYPE"
    ),
    entity_name: str = typer.Argument(..., help="GitHub org or user name", metavar="ENTITY_NAME"),
    # Global options
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version and exit", is_eager=True
    ),
    feedback: Optional[bool] = typer.Option(
        None,
        "--feedback",
        callback=feedback_callback,
        help="Show feedback link and exit",
        is_eager=True,
    ),
    # Protocol options
    use_ssh: bool = typer.Option(
        False, "--ssh/--https", help="Use SSH URLs for cloning (default: HTTPS)"
    ),
    # Repository filtering
    repos: Optional[str] = typer.Option(
        None, "--repos", help="Comma-separated list of repository names to process"
    ),
    repos_file: Optional[str] = typer.Option(
        None, "--repos-file", help="File containing repository names (one per line)"
    ),
    exclude_archived: bool = typer.Option(
        False, "--exclude-archived", help="Exclude archived repositories"
    ),
    exclude_forks: bool = typer.Option(
        False, "--exclude-forks", help="Exclude forked repositories"
    ),
    # Repository visibility
    visibility: str = typer.Option(
        "all", "--visibility", help="Repository visibility: 'all', 'public', or 'private'"
    ),
    # Cache options
    refetch_repos: bool = typer.Option(
        False, "--refetch", help="Force refetch repository list from GitHub"
    ),
    # Execution options
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview actions without making changes"),
    max_workers: int = typer.Option(
        1, "--max-workers", help="Maximum parallel operations (use with caution)"
    ),
    # Security options
    use_keyring: bool = typer.Option(
        False, "--use-keyring", help="Store/retrieve GitHub token securely using keyring"
    ),
    # Authentication options
    interactive_auth: bool = typer.Option(
        False, "--interactive-auth", help="Prompt for username/password for HTTPS authentication"
    ),
    # Output options
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output"),
    plain: bool = typer.Option(False, "--plain", help="Disable colored output"),
    log_level: str = typer.Option(
        "INFO", "--log-level", "-l", help="Set log level (DEBUG, INFO, WARNING, ERROR)"
    ),
    log_file: Optional[str] = typer.Option(None, "--log-file", help="Write logs to specified file"),
    error_log: Optional[str] = typer.Option(
        None, "--error-log", help="Write detailed error logs to specified file"
    ),
    # Configuration
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
):
    """
    Clone and pull GitHub repositories for a user or organization.

    ENTITY_TYPE must be either 'user' or 'org'.
    ENTITY_NAME is the GitHub username or organization name.

    Examples:

      # Clone all repositories for a user
      git-batch-pull user octocat

      # Clone specific repositories using SSH
      git-batch-pull org myorg --ssh --repos "repo1,repo2"

      # Clone only private repositories
      git-batch-pull org myorg --visibility private

      # Dry run to see what would be processed
      git-batch-pull user octocat --dry-run
    """
    # Validate entity type
    if entity_type not in ("org", "user"):
        typer.echo(
            f"Error: Invalid entity type '{entity_type}'. Must be 'org' or 'user'.", err=True
        )
        raise typer.Exit(1)

    # Setup logging first
    logging_handler.setup_logging(log_level, log_file, quiet, plain)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        logger.debug("Loading configuration...")
        config_obj = Config.from_env(config)

        # Override config with CLI arguments
        config_obj.use_ssh = use_ssh
        config_obj.repo_visibility = visibility
        config_obj.dry_run = dry_run
        config_obj.quiet = quiet
        config_obj.plain = plain
        config_obj.max_workers = max_workers
        config_obj.log_level = log_level

        # Create service container
        logger.debug("Initializing services...")
        container = ServiceContainer(config_obj)

        if use_keyring:
            container.configure_keyring(True)

        # Process repository names from CLI parameter
        repo_names = repos.split(",") if repos else None

        # Get repositories
        logger.info(f"Fetching repositories for {entity_type} '{entity_name}'...")
        repository_batch = container.repository_service.get_repositories(
            entity_type=entity_type,
            entity_name=entity_name,
            repo_visibility=config_obj.repo_visibility,
            use_cache=not refetch_repos,
            include_forks=not exclude_forks,
            include_archived=not exclude_archived,
            repo_names=repo_names,
            local_folder=str(config_obj.local_folder),
        )

        if not repository_batch.repositories:
            logger.warning("No repositories found")
            return

        logger.info(f"Found {len(repository_batch.repositories)} repositories")

        logger.info(f"Processing {len(repository_batch.repositories)} repositories")

        # Handle protocol mismatches
        protocol_handler = ProtocolHandler(container.repository_service)
        intended_protocol = "ssh" if use_ssh else "https"

        protocol_handler.detect_and_handle_mismatches(
            batch=repository_batch,
            intended_protocol=intended_protocol,
            entity_name=entity_name,
            dry_run=dry_run,
        )

        # Process repositories
        batch_processor = BatchProcessor(git_service=container.git_service, max_workers=max_workers)

        def error_callback(repo_name: str, error: Exception) -> None:
            error_handler.handle_repository_error(repo_name, error)

        result = batch_processor.process_batch(
            batch=repository_batch,
            use_ssh=use_ssh,
            dry_run=dry_run,
            quiet=quiet,
            interactive_auth=interactive_auth,
            error_callback=error_callback,
        )

        # Clear any cached credentials for security
        if interactive_auth and not use_ssh:
            container.git_service.clear_cached_credentials()

        # Print summary
        if not quiet:
            if dry_run:
                typer.echo(f"\n[DRY RUN] Would process {result.simulated} repositories")
            else:
                typer.echo(f"\nSummary: {result.processed} processed, {result.failed} failed")
                if result.success_rate < 100:
                    typer.echo(f"Success rate: {result.success_rate:.1f}%")

        # Write error logs if requested
        if error_log and error_handler.has_errors():
            error_handler.write_detailed_error_log(error_log)

        # Exit with error code if there were failures
        if result.failed > 0:
            logger.error(f"{result.failed} repositories failed to process")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        raise typer.Exit(130)

    except Exception as e:
        error_handler.handle_error(e, context="main command", fatal=False)

        if not quiet:
            typer.echo(f"Error: {e}", err=True)

        if error_log:
            error_handler.write_detailed_error_log(error_log)

        raise typer.Exit(1)
