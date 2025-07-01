"""
Unit tests for custom exceptions in git_batch_pull.exceptions.
Covers inheritance and string representation of exception classes.
"""

from git_batch_pull import exceptions


def test_exception_inheritance():
    """
    Test that custom exceptions inherit from Exception.
    """
    assert issubclass(exceptions.ConfigError, Exception)
    assert issubclass(exceptions.GitHubAPIError, Exception)
    assert issubclass(exceptions.GitOperationError, Exception)


def test_exception_messages():
    """
    Test that custom exceptions return correct string messages.
    """
    e = exceptions.ConfigError("foo")
    assert str(e) == "foo"
    e = exceptions.GitHubAPIError("bar")
    assert str(e) == "bar"
    e = exceptions.GitOperationError("baz")
    assert str(e) == "baz"
