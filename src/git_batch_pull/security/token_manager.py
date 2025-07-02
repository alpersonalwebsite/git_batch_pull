"""Secure token management utilities."""

import logging
import os
from typing import Optional

import keyring

from ..exceptions import AuthenticationError, SecurityError


class SecureTokenManager:
    """Manages GitHub tokens securely with keyring integration."""
    
    SERVICE_NAME = "git-batch-pull"
    
    def __init__(self, use_keyring: bool = False):
        self.use_keyring = use_keyring
        self.logger = logging.getLogger(__name__)
    
    def get_token(self) -> str:
        """Get GitHub token from environment or keyring."""
        # First try environment variable
        token = os.getenv("github_token")
        
        if not token and self.use_keyring:
            # Try keyring if enabled
            username = self._get_username()
            token = keyring.get_password(self.SERVICE_NAME, username)
            
            if not token:
                raise AuthenticationError(
                    "No token found in keyring. Please set github_token in environment first."
                )
        
        if not token:
            raise AuthenticationError(
                "GitHub token not found. Set github_token environment variable or use --use-keyring."
            )
        
        self._validate_token(token)
        return token
    
    def store_token(self, token: str) -> None:
        """Store token in keyring if enabled."""
        if not self.use_keyring:
            return
        
        self._validate_token(token)
        username = self._get_username()
        
        try:
            keyring.set_password(self.SERVICE_NAME, username, token)
            self.logger.info("Token stored securely in keyring")
        except Exception as e:
            raise SecurityError(f"Failed to store token in keyring: {e}")
    
    def _validate_token(self, token: str) -> None:
        """Validate token format and content."""
        if not token or token.strip() == "":
            raise AuthenticationError("GitHub token cannot be empty")
        
        if token.startswith("ghp_xxx") or token == "your_token_here":
            raise AuthenticationError("GitHub token appears to be a placeholder")
        
        # GitHub personal access tokens should start with ghp_, gho_, ghu_, ghs_, or ghr_
        if not any(token.startswith(prefix) for prefix in ["ghp_", "gho_", "ghu_", "ghs_", "ghr_"]):
            self.logger.warning("Token format may be invalid - expected GitHub token format")
    
    def _get_username(self) -> str:
        """Get username for keyring storage."""
        import getpass
        return os.getenv("USER") or getpass.getuser()
    
    def sanitize_token_for_logging(self, token: str) -> str:
        """Sanitize token for safe logging."""
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"
