import os
from typing import Optional, Tuple

import tomli
from dotenv import load_dotenv

from git_batch_pull.exceptions import ConfigError  # type: ignore[attr-defined]


def load_config(config_path: Optional[str] = None) -> Tuple[str, str, str, dict]:
    """
    Load configuration from environment variables, .env, and optional config.toml.

    Args:
        config_path: Optional path to a TOML config file.
    Returns:
        Tuple of (github_token, local_folder, repo_visibility, extra_config)
    Raises:
        ConfigError: If required variables are missing or insecure.
    """
    load_dotenv()
    github_token = os.getenv("github_token")
    local_folder = os.getenv("local_folder")
    repo_visibility = os.getenv("repo_visibility", "all")
    extra_config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, "rb") as f:
            extra_config = tomli.load(f)
    if not github_token or not local_folder:
        raise ConfigError(
            "Both 'github_token' and 'local_folder' must be set in .env or "
            "environment variables."
        )
    if github_token.startswith("ghp_xxx") or github_token.strip() == "":
        raise ConfigError("GitHub token appears to be a placeholder or empty.")
    if not os.path.isabs(local_folder):
        raise ConfigError("local_folder must be an absolute path.")
    return github_token, local_folder, repo_visibility, extra_config
