"""Core batch processing logic for repositories."""

import concurrent.futures
import logging
from typing import Callable, List, Optional

from tqdm import tqdm

from ..exceptions import GitOperationError
from ..models import Repository, RepositoryBatch
from ..services import GitService


class BatchProcessor:
    """
    Processes repositories in batches with parallel execution and error handling.
    """

    def __init__(self, git_service: GitService, max_workers: int = 1):
        """
        Initialize the batch processor.

        Args:
            git_service: Git service for repository operations
            max_workers: Maximum number of parallel workers
        """
        self.git_service = git_service
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    def process_repositories(
        self,
        repositories: List[Repository],
        use_ssh: bool = False,
        dry_run: bool = False,
        quiet: bool = False,
        interactive_auth: bool = False,
        error_callback: Optional[Callable[[str, Exception], None]] = None,
    ) -> "ProcessingResult":
        """
        Process a list of repositories directly.

        Args:
            repositories: List of repositories to process
            use_ssh: Whether to use SSH URLs
            dry_run: Whether to simulate operations without executing
            quiet: Whether to suppress progress output
            interactive_auth: Whether to prompt for HTTPS credentials interactively
            error_callback: Optional callback for handling errors

        Returns:
            ProcessingResult with statistics
        """
        # Create a temporary batch from the repository list
        from ..models import RepositoryBatch

        batch = RepositoryBatch(repositories=repositories, entity_type="mixed", entity_name="batch")
        return self.process_batch(batch, use_ssh, dry_run, quiet, interactive_auth, error_callback)

    def process_batch(
        self,
        batch: RepositoryBatch,
        use_ssh: bool = False,
        dry_run: bool = False,
        quiet: bool = False,
        interactive_auth: bool = False,
        error_callback: Optional[Callable[[str, Exception], None]] = None,
    ) -> "ProcessingResult":
        """
        Process a batch of repositories.

        Args:
            batch: Repository batch to process
            use_ssh: Whether to use SSH URLs
            dry_run: Whether to simulate operations without executing
            quiet: Whether to suppress progress output
            interactive_auth: Whether to prompt for HTTPS credentials interactively
            error_callback: Optional callback for handling errors

        Returns:
            ProcessingResult with statistics
        """
        result = ProcessingResult()

        def process_single_repository(repository: Repository) -> None:
            """Process a single repository."""
            try:
                if dry_run:
                    if not quiet:
                        self.logger.info(f"[DRY RUN] Would process: {repository.name}")
                    result.simulated += 1
                    return

                self.logger.debug(f"Processing repository: {repository.name}")
                self.git_service.clone_or_pull(repository, use_ssh, interactive_auth)
                result.processed += 1
                self.logger.info(f"Successfully processed: {repository.name}")

            except GitOperationError as e:
                self.logger.error(f"Git operation failed for {repository.name}: {e}")
                result.failed += 1
                result.errors.append((repository.name, str(e)))

                if error_callback:
                    error_callback(repository.name, e)

            except Exception as e:
                self.logger.error(f"Unexpected error for {repository.name}: {e}")
                result.failed += 1
                result.errors.append((repository.name, f"Unexpected error: {e}"))

                if error_callback:
                    error_callback(repository.name, e)

        # Process repositories
        if self.max_workers > 1 and not dry_run:
            # Parallel processing
            self._process_parallel(batch.repositories, process_single_repository, quiet)
        else:
            # Sequential processing
            self._process_sequential(batch.repositories, process_single_repository, quiet)

        return result

    def _process_parallel(
        self,
        repositories: List[Repository],
        processor_func: Callable[[Repository], None],
        quiet: bool,
    ) -> None:
        """Process repositories in parallel."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {executor.submit(processor_func, repo): repo for repo in repositories}

            # Process with progress bar
            if not quiet:
                for future in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(repositories),
                    desc="Processing repositories",
                ):
                    try:
                        future.result()  # This will raise any exception that occurred
                    except Exception:
                        # Exception already handled in processor_func
                        pass  # nosec
            else:
                # Wait for all futures to complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        pass  # nosec

    def _process_sequential(
        self,
        repositories: List[Repository],
        processor_func: Callable[[Repository], None],
        quiet: bool,
    ) -> None:
        """Process repositories sequentially."""
        if not quiet:
            repositories = tqdm(repositories, desc="Processing repositories")

        for repository in repositories:
            processor_func(repository)


class ProcessingResult:
    """
    Result of batch processing operation.
    """

    def __init__(self):
        self.processed = 0
        self.failed = 0
        self.simulated = 0
        self.errors: List[tuple[str, str]] = []

    @property
    def total(self) -> int:
        """Total number of repositories processed."""
        return self.processed + self.failed + self.simulated

    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.processed / self.total) * 100

    def has_errors(self) -> bool:
        """Check if there were any errors."""
        return len(self.errors) > 0

    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.errors:
            return "No errors"

        summary_lines = [f"Errors occurred in {len(self.errors)} repositories:"]
        for repo_name, error_msg in self.errors:
            summary_lines.append(f"  - {repo_name}: {error_msg}")

        return "\n".join(summary_lines)

    def write_error_log(self, file_path: str) -> None:
        """Write detailed error log to file."""
        if not self.errors:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Git Batch Pull Error Log\n")
                f.write("========================\n\n")
                f.write(f"Total repositories processed: {self.total}\n")
                f.write(f"Failed: {self.failed}\n")
                f.write(f"Success rate: {self.success_rate:.1f}%\n\n")

                for repo_name, error_msg in self.errors:
                    f.write(f"Repository: {repo_name}\n")
                    f.write(f"Error: {error_msg}\n")
                    f.write("-" * 50 + "\n")

            self.logger.info(f"Error log written to: {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")

    def __str__(self) -> str:
        """String representation of processing result."""
        if self.simulated > 0:
            return f"Simulation: {self.simulated} repositories would be processed"
        else:
            return (
                f"Processed: {self.processed}, Failed: {self.failed}, "
                f"Success rate: {self.success_rate:.1f}%"
            )
