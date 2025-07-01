"""
Unit tests for the GitHubAPIClient and related GitHub API logic in git_batch_pull.github_api.
Covers API pagination, organization/user repo fetching, and error handling with mocks.
"""

import time

import pytest
import requests

from git_batch_pull import github_api


class DummySession:
    """Mock requests.Session for GitHub API tests."""

    def __init__(self):
        self.calls = []
        self.headers = {}

    def update(self, *args, **kwargs):
        self.headers.update(*args, **kwargs)

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        page = params["page"] if params and "page" in params else 1
        print(f"MOCK GET: url={url}, params={params}, page={page}")

        class Resp:
            headers = {}

            def raise_for_status(self):
                pass

            def json(self):
                if page > 1:
                    return []
                if "/orgs/" in url and "/repos" in url:
                    return [
                        {
                            "name": "org-repo",
                            "default_branch": "main",
                            "clone_url": "org-url",
                            "ssh_url": "org-ssh",
                        }
                    ]
                if "/user/repos" in url:
                    return [
                        {
                            "name": "user-repo",
                            "default_branch": "main",
                            "clone_url": "user-url",
                            "ssh_url": "user-ssh",
                        }
                    ]
                return []

            @property
            def status_code(self):
                return 200

            @property
            def text(self):
                import json

                return json.dumps(self.json())

        return Resp()

    def __getattr__(self, name):
        # Allow any other attribute access to not break
        return lambda *a, **kw: None


def test_get_repos_user(monkeypatch):
    """Test fetching user repos from the GitHub API client."""
    client = github_api.GitHubAPIClient("token")
    client.session = DummySession()
    repos = client.get_repos("user", "foo")
    assert repos[0]["name"] == "user-repo"


def test_get_repos_org(monkeypatch):
    """Test fetching org repos from the GitHub API client."""
    client = github_api.GitHubAPIClient("token")
    client.session = DummySession()
    repos = client.get_repos("org", "myorg")
    assert repos[0]["name"] == "org-repo"


def test_get_repos_handles_error(monkeypatch):
    """Test error handling when the GitHub API client fails."""

    class FailingSession:
        def get(self, url, params=None, timeout=None):
            raise Exception("API fail")

    client = github_api.GitHubAPIClient("token")
    client.session = FailingSession()
    with pytest.raises(Exception):
        client.get_repos("user", "foo")


def pytest_fixture_patch_sleep():
    import time as real_time

    orig_sleep = real_time.sleep
    real_time.sleep = lambda x: None
    yield
    real_time.sleep = orig_sleep


@pytest.fixture(autouse=True)
def patch_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda x: None)


@pytest.fixture(autouse=True)
def patch_requests_session(monkeypatch):
    monkeypatch.setattr(requests, "Session", DummySession)
