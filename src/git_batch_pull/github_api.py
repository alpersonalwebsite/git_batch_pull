import logging
import time
from typing import Dict, List

import requests

from git_batch_pull.exceptions import GitHubAPIError  # type: ignore[attr-defined]


class GitHubAPIClient:
    """
    Client for interacting with the GitHub API securely.
    Handles authentication, pagination, and error handling.
    """

    def __init__(self, token: str, max_retries: int = 3, backoff: float = 2.0):
        """
        Initialize the GitHubAPIClient.

        Args:
            token: GitHub personal access token.
            max_retries: Number of retries for failed requests.
            backoff: Backoff time (seconds) for retries.
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            }  # type: ignore
        )
        self.api_url = "https://api.github.com"
        self.max_retries = max_retries
        self.backoff = backoff

    def get_repos(
        self, entity_type: str, entity_name: str, repo_visibility: str = "all"
    ) -> List[Dict]:
        """
        Fetch all repositories for a user or org.

        Args:
            entity_type: 'user' or 'org'.
            entity_name: username or org name.
            repo_visibility: 'all', 'public', or 'private'.
        Returns:
            List of repository metadata dicts.
        Raises:
            GitHubAPIError: On API failure.
        """
        logging.debug(
            f"get_repos called with entity_type={entity_type}, "
            f"entity_name={entity_name}, repo_visibility={repo_visibility}"
        )
        if entity_type == "user":
            url = self.api_url + "/user/repos"
            extra_params = {"visibility": repo_visibility}
        else:
            url = f"{self.api_url}/orgs/{entity_name}/repos"
            extra_params = {"type": "all"}
        logging.debug(f"API request URL: {url}")
        logging.debug(f"API params: {extra_params}")
        repos: List[Dict] = []
        page = 1
        done = False
        while not done:
            params = {"per_page": 100, "page": page}
            params.update(extra_params)  # type: ignore[arg-type]
            for attempt in range(self.max_retries):
                try:
                    logging.debug(f"Requesting URL: {url}")
                    logging.debug(
                        "Request headers: %s",
                        {k: v for k, v in self.session.headers.items() if k != "Authorization"},
                    )
                    logging.debug("Request params: %s", params)
                    resp = self.session.get(url, params=params, timeout=10)
                    logging.debug(f"Response status: {resp.status_code}")
                    logging.debug(f"Response headers: {resp.headers}")
                    if page == 1:
                        try:
                            logging.debug("Raw JSON response (first page): %s", resp.text[:2000])
                        except Exception as e:
                            logging.debug("Could not print raw response: %s", e)
                    if resp.status_code == 200:
                        data = resp.json()
                        logging.debug(f"Page {page} received {len(data)} repos")
                        if not data:
                            logging.debug(f"No more data on page {page}, " "breaking outer loop.")
                            done = True
                            break
                        repos.extend(data)
                        if page == 1:
                            for i, repo in enumerate(data[:3]):
                                logging.debug(
                                    f"Repo {i}: name={repo.get('name')}, "
                                    f"private={repo.get('private')}, "
                                    f"ssh_url={repo.get('ssh_url')}, "
                                    f"clone_url={repo.get('clone_url')}"
                                )
                        break  # Success, break out of retry loop
                    elif (
                        resp.status_code == 403
                        and "X-RateLimit-Remaining" in resp.headers
                        and resp.headers["X-RateLimit-Remaining"] == "0"
                    ):
                        reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
                        now = int(time.time())
                        wait = max(reset - now, 1)
                        logging.warning(f"Rate limit exceeded, sleeping for {wait} seconds")
                        time.sleep(wait)
                        continue
                    else:
                        try:
                            err = resp.json()
                        except Exception:
                            err = resp.text
                        raise GitHubAPIError(f"GitHub API error: {resp.status_code} {err}")
                except Exception as e:
                    logging.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    if attempt == self.max_retries - 1:
                        raise GitHubAPIError(
                            f"GitHub API error after {self.max_retries} attempts: {e}"
                        )
                    time.sleep(self.backoff)
            page += 1
        return repos
