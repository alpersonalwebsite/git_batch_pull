"""Enhanced exception hierarchy for git-batch-pull with better error handling."""

from typing import Optional


class GitBatchPullError(Exception):
    """Base exception for all git-batch-pull errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ConfigError(GitBatchPullError):
    """Exception raised for configuration errors."""

    pass


class ValidationError(GitBatchPullError):
    """Exception raised for input validation errors."""

    pass


class AuthenticationError(GitBatchPullError):
    """Exception raised for authentication/authorization errors."""

    pass


class GitHubAPIError(GitBatchPullError):
    """Exception raised for GitHub API errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        base_msg = self.message
        if self.status_code:
            base_msg += f" (HTTP {self.status_code})"
        if self.response_text:
            base_msg += f"\nResponse: {self.response_text}"
        return base_msg


class GitOperationError(GitBatchPullError):
    """Exception raised for git operation errors."""

    def __init__(self, message: str, command: Optional[str] = None, stderr: Optional[str] = None):
        super().__init__(message)
        self.command = command
        self.stderr = stderr

    def __str__(self) -> str:
        base_msg = self.message
        if self.command:
            base_msg += f"\nCommand: {self.command}"
        if self.stderr:
            base_msg += f"\nError output: {self.stderr}"
        return base_msg


class SecurityError(GitBatchPullError):
    """Exception raised for security-related errors."""

    pass


class PathValidationError(ValidationError):
    """Exception raised for path validation errors."""

    pass


__all__ = [
    "GitBatchPullError",
    "ConfigError",
    "ValidationError",
    "AuthenticationError",
    "GitHubAPIError",
    "GitOperationError",
    "SecurityError",
    "PathValidationError",
]
