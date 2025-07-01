"""Enhanced error handling and reporting."""

import logging
import traceback
from typing import Any, Dict, List, Optional

from ..exceptions import GitBatchPullError


class ErrorHandler:
    """
    Centralized error handling and reporting.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
        self.errors: List[Dict[str, Any]] = []

    def handle_error(
        self,
        error: Exception,
        context: Optional[str] = None,
        repository: Optional[str] = None,
        fatal: bool = False,
    ) -> None:
        """
        Handle an error with proper logging and tracking.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            repository: Repository name if error is repo-specific
            fatal: Whether this error should cause the program to exit
        """
        self.error_count += 1

        # Create error record
        error_record = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "repository": repository,
            "traceback": (
                traceback.format_exc() if not isinstance(error, GitBatchPullError) else None
            ),
            "fatal": fatal,
        }

        self.errors.append(error_record)

        # Log the error
        error_msg = self._format_error_message(error_record)

        if fatal:
            self.logger.critical(error_msg)
        else:
            self.logger.error(error_msg)

        # If fatal, we could raise or exit here
        if fatal:
            raise error

    def handle_repository_error(self, repository: str, error: Exception) -> None:
        """
        Handle repository-specific errors.

        Args:
            repository: Repository name
            error: The exception that occurred
        """
        self.handle_error(
            error=error, context="repository processing", repository=repository, fatal=False
        )

    def get_error_summary(self) -> str:
        """
        Get a summary of all errors encountered.

        Returns:
            Formatted error summary
        """
        if not self.errors:
            return "No errors encountered."

        summary_lines = [f"Error Summary ({self.error_count} errors):", "=" * 40]

        # Group errors by type
        error_by_type: Dict[str, int] = {}
        repo_errors: List[str] = []

        for error in self.errors:
            error_type = error["type"]
            error_by_type[error_type] = error_by_type.get(error_type, 0) + 1

            if error["repository"]:
                repo_errors.append(error["repository"])

        # Add type summary
        summary_lines.append("Error types:")
        for error_type, count in error_by_type.items():
            summary_lines.append(f"  - {error_type}: {count}")

        # Add repository summary
        if repo_errors:
            unique_repos = set(repo_errors)
            summary_lines.append(f"\nRepositories with errors ({len(unique_repos)}):")
            for repo in sorted(unique_repos):
                summary_lines.append(f"  - {repo}")

        return "\n".join(summary_lines)

    def write_detailed_error_log(self, file_path: str) -> None:
        """
        Write detailed error log to file.

        Args:
            file_path: Path to write the error log
        """
        if not self.errors:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Git Batch Pull - Detailed Error Log\n")
                f.write("=" * 50 + "\n\n")

                for i, error in enumerate(self.errors, 1):
                    f.write(f"Error #{i}\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Type: {error['type']}\n")
                    f.write(f"Message: {error['message']}\n")

                    if error["context"]:
                        f.write(f"Context: {error['context']}\n")

                    if error["repository"]:
                        f.write(f"Repository: {error['repository']}\n")

                    if error["traceback"]:
                        f.write(f"Traceback:\n{error['traceback']}\n")

                    f.write("\n")

            self.logger.info(f"Detailed error log written to: {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to write error log to {file_path}: {e}")

    def has_errors(self) -> bool:
        """Check if any errors have been recorded."""
        return len(self.errors) > 0

    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors have been recorded."""
        return any(error["fatal"] for error in self.errors)

    def clear_errors(self) -> None:
        """Clear all recorded errors."""
        self.errors.clear()
        self.error_count = 0

    def _format_error_message(self, error_record: Dict[str, Any]) -> str:
        """Format an error record into a readable message."""
        parts = []

        if error_record["repository"]:
            parts.append(f"[{error_record['repository']}]")

        if error_record["context"]:
            parts.append(f"({error_record['context']})")

        parts.append(f"{error_record['type']}: {error_record['message']}")

        return " ".join(parts)


# Global error handler instance
error_handler = ErrorHandler()
