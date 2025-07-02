"""
git_batch_pull - Clone and pull GitHub repositories in batch.

A secure and robust tool for cloning and pulling one, several,
or all GitHub repositories for a user or organization.
"""

from .cli import app
from .exceptions import (
    AuthenticationError,
    ConfigError,
    GitBatchPullError,
    GitHubAPIError,
    GitOperationError,
    PathValidationError,
    SecurityError,
    ValidationError,
)
from .models import Config, Repository, RepositoryBatch, RepositoryInfo

__version__ = "2.0.1"
__author__ = "Al Diaz"
__email__ = "aldiazcode@gmail.com"
__license__ = "MIT"

__all__ = [
    # CLI
    "app",
    # Models
    "Config",
    "Repository",
    "RepositoryInfo",
    "RepositoryBatch",
    # Exceptions
    "GitBatchPullError",
    "ConfigError",
    "GitHubAPIError",
    "GitOperationError",
    "ValidationError",
    "AuthenticationError",
    "SecurityError",
    "PathValidationError",
    # Version
    "__version__",
]
