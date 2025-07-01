"""Interactive credential management for HTTPS authentication."""

import getpass
import logging
import urllib.parse
from typing import Optional, Tuple

from ..exceptions import AuthenticationError


class InteractiveCredentialManager:
    """Manages interactive credential prompting for HTTPS git operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cached_credentials: Optional[Tuple[str, str]] = None

    def get_credentials(self, force_prompt: bool = False) -> Tuple[str, str]:
        """
        Get username and token/password for HTTPS authentication.

        Args:
            force_prompt: Force prompting even if credentials are cached

        Returns:
            Tuple of (username, token/password)
        """
        if self._cached_credentials and not force_prompt:
            return self._cached_credentials

        print("\n🔐 HTTPS Authentication Required")
        print("Enter your GitHub credentials for HTTPS access:")

        username = input("GitHub Username: ").strip()
        if not username:
            raise AuthenticationError("Username cannot be empty")

        # Use getpass to hide token input
        token = getpass.getpass("GitHub Token/Password: ").strip()
        if not token:
            raise AuthenticationError("Token/Password cannot be empty")

        self._cached_credentials = (username, token)
        self.logger.info(f"Credentials cached for user: {username}")

        return self._cached_credentials

    def create_authenticated_url(self, https_url: str, username: str, token: str) -> str:
        """
        Create an authenticated HTTPS URL.

        Args:
            https_url: Original HTTPS URL
            username: GitHub username
            token: GitHub token/password

        Returns:
            Authenticated HTTPS URL
        """
        # Parse the URL
        parsed = urllib.parse.urlparse(https_url)

        # URL encode credentials to handle special characters
        encoded_username = urllib.parse.quote(username, safe="")
        encoded_token = urllib.parse.quote(token, safe="")

        # Create authenticated URL
        netloc = f"{encoded_username}:{encoded_token}@{parsed.netloc}"
        authenticated_url = urllib.parse.urlunparse(
            (parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
        )

        return authenticated_url

    def clear_credentials(self) -> None:
        """Clear cached credentials."""
        self._cached_credentials = None
        self.logger.debug("Cleared cached credentials")
