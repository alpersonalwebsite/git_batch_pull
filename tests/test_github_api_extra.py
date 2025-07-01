"""
Extra tests for GitHubAPIClient error and rate limit handling in git_batch_pull.github_api.
Covers API error raising and rate limit retry logic.
"""

from unittest.mock import patch

import pytest

from git_batch_pull.github_api import GitHubAPIClient


class DummyFailSession:
    """
    Mock session that always fails for API error tests.
    """

    def __init__(self):
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        raise Exception("API fail")


class DummyRateLimitSession:
    """
    Mock session that simulates GitHub API rate limiting, then fails after one retry.
    """

    def __init__(self):
        self.headers = {}
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1

        class Resp:
            def __init__(self, calls):
                self.calls = calls

            @property
            def status_code(self):
                return 403 if self.calls == 1 else 500

            @property
            def headers(self):
                return {"X-RateLimit-Remaining": "0"} if self.calls == 1 else {}

            def raise_for_status(self):
                raise Exception("rate limit exceeded" if self.calls == 1 else "fail")

            def json(self):
                return []

        return Resp(self.calls)


def test_github_api_error():
    """
    Test that GitHubAPIClient raises on API error.
    """
    client = GitHubAPIClient("token")
    client.session = DummyFailSession()
    with pytest.raises(Exception):
        client.get_repos("user", "foo")


def test_github_api_rate_limit():
    """
    Test that GitHubAPIClient handles API rate limiting and retries.
    """
    client = GitHubAPIClient("token", max_retries=1, backoff=0)
    client.session = DummyRateLimitSession()
    with patch("time.sleep", return_value=None), patch("time.time", return_value=0):
        with pytest.raises(Exception):
            client.get_repos("user", "foo")
