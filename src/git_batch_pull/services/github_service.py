"""GitHub API service with enhanced error handling and security."""

import logging
import time
from typing import Dict, List

import requests

from ..exceptions import AuthenticationError, GitHubAPIError
from ..security import SafeSubprocessRunner


class GitHubService:
    """
    Enhanced GitHub API client with better error handling and security.
    """

    def __init__(
        self,
        token: str,
        subprocess_runner: SafeSubprocessRunner,
        max_retries: int = 3,
        backoff: float = 2.0,
    ):
        """
        Initialize the GitHub API service.

        Args:
            token: GitHub personal access token
            subprocess_runner: Safe subprocess runner instance
            max_retries: Number of retries for failed requests
            backoff: Backoff time (seconds) for retries
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "git-batch-pull/1.0.0",
            }
        )

        self.api_url = "https://api.github.com"
        self.max_retries = max_retries
        self.backoff = backoff
        self.subprocess_runner = subprocess_runner
        self.logger = logging.getLogger(__name__)

    def get_repositories(
        self, entity_type: str, entity_name: str, repo_visibility: str = "all"
    ) -> List[Dict]:
        """
        Fetch all repositories for a user or organization.

        Args:
            entity_type: 'user' or 'org'
            entity_name: Username or organization name
            repo_visibility: 'all', 'public', or 'private'

        Returns:
            List of repository metadata dictionaries

        Raises:
            GitHubAPIError: On API failure
            AuthenticationError: On authentication issues
        """
        self.logger.debug(
            f"Fetching {entity_type} repositories for {entity_name} (visibility: {repo_visibility})"
        )

        if entity_type == "user":
            url = f"{self.api_url}/user/repos"
            params = {"visibility": repo_visibility}
        elif entity_type == "org":
            url = f"{self.api_url}/orgs/{entity_name}/repos"
            params = {"type": "all"}
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'user' or 'org'")

        repositories: List[Dict] = []
        page = 1

        while True:
            current_params = {"per_page": 100, "page": page, **params}

            for attempt in range(self.max_retries):
                try:
                    self.logger.debug(f"API request: {url} (page {page}, attempt {attempt + 1})")

                    response = self.session.get(url, params=current_params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        if not data:  # No more pages
                            self.logger.debug(f"Fetched {len(repositories)} repositories total")
                            return repositories

                        repositories.extend(data)
                        self.logger.debug(f"Page {page}: received {len(data)} repositories")
                        break  # Success, continue to next page

                    elif response.status_code == 401:
                        raise AuthenticationError(
                            "Invalid GitHub token or insufficient permissions"
                        )

                    elif response.status_code == 403:
                        if self._is_rate_limited(response):
                            wait_time = self._get_rate_limit_wait_time(response)
                            self.logger.warning(f"Rate limit exceeded, waiting {wait_time} seconds")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise GitHubAPIError(
                                "Access forbidden - check token permissions",
                                status_code=403,
                                response_text=response.text,
                            )

                    elif response.status_code == 404:
                        raise GitHubAPIError(
                            f"Entity '{entity_name}' not found or not accessible", status_code=404
                        )

                    else:
                        raise GitHubAPIError(
                            f"GitHub API error: HTTP {response.status_code}",
                            status_code=response.status_code,
                            response_text=response.text,
                        )

                except requests.exceptions.Timeout:
                    self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        raise GitHubAPIError("Request timeout after maximum retries")
                    time.sleep(self.backoff)

                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    if attempt == self.max_retries - 1:
                        raise GitHubAPIError(
                            f"Request failed after {self.max_retries} attempts: {e}"
                        )
                    time.sleep(self.backoff)

            page += 1

    def test_authentication(self) -> bool:
        """
        Test if the current token is valid.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = self.session.get(f"{self.api_url}/user", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def _is_rate_limited(self, response: requests.Response) -> bool:
        """Check if response indicates rate limiting."""
        return (
            "X-RateLimit-Remaining" in response.headers
            and response.headers["X-RateLimit-Remaining"] == "0"
        )

    def _get_rate_limit_wait_time(self, response: requests.Response) -> int:
        """Calculate how long to wait for rate limit reset."""
        reset_time = int(response.headers.get("X-RateLimit-Reset", "0"))
        current_time = int(time.time())
        return max(reset_time - current_time, 1)
