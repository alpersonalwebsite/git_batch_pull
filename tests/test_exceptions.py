"""
Unit tests for custom exception raising in git_batch_pull.exceptions.
Covers raising and catching ConfigError, GitHubAPIError, and GitOperationError.
"""

import pytest

from git_batch_pull import exceptions


def test_config_error():
    """
    Test that ConfigError can be raised and caught.
    """
    with pytest.raises(exceptions.ConfigError):
        raise exceptions.ConfigError("config error")


def test_github_api_error():
    """
    Test that GitHubAPIError can be raised and caught.
    """
    with pytest.raises(exceptions.GitHubAPIError):
        raise exceptions.GitHubAPIError("api error")


def test_git_operation_error():
    """
    Test that GitOperationError can be raised and caught.
    """
    with pytest.raises(exceptions.GitOperationError):
        raise exceptions.GitOperationError("git error")
