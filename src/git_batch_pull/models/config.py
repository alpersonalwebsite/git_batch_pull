"""Configuration data model."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..exceptions import ConfigError, ValidationError


@dataclass
class Config:
    """Configuration settings for git-batch-pull."""

    github_token: str
    local_folder: Path
    repo_visibility: str = "all"
    max_workers: int = 1
    log_level: str = "INFO"
    use_ssh: bool = False
    dry_run: bool = False
    quiet: bool = False
    plain: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        if not self.github_token or self.github_token.strip() == "":
            raise ConfigError("GitHub token cannot be empty")

        if self.github_token.startswith("ghp_xxx"):
            raise ConfigError("GitHub token appears to be a placeholder")

        if not self.local_folder.is_absolute():
            raise ConfigError("local_folder must be an absolute path")

        if self.repo_visibility not in ("all", "public", "private"):
            raise ValidationError(f"Invalid repo_visibility: {self.repo_visibility}")

        if self.max_workers < 1:
            raise ValidationError("max_workers must be at least 1")

        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
            raise ValidationError(f"Invalid log_level: {self.log_level}")

    @classmethod
    def from_env(cls, config_path: Optional[str] = None) -> "Config":
        """Create configuration from environment variables and optional config file."""
        import tomli
        from dotenv import load_dotenv

        load_dotenv()

        # Load from environment
        github_token = os.getenv("github_token")
        local_folder_str = os.getenv("local_folder")
        repo_visibility = os.getenv("repo_visibility", "all")

        if not github_token:
            raise ConfigError("github_token must be set in environment or .env file")

        if not local_folder_str:
            raise ConfigError("local_folder must be set in environment or .env file")

        local_folder = Path(local_folder_str)

        # Load additional config from TOML file if provided
        extra_config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, "rb") as f:
                extra_config = tomli.load(f)

        return cls(
            github_token=github_token,
            local_folder=local_folder,
            repo_visibility=repo_visibility,
            max_workers=extra_config.get("max_workers", 1),
            log_level=extra_config.get("log_level", "INFO"),
            use_ssh=extra_config.get("use_ssh", False),
            dry_run=extra_config.get("dry_run", False),
            quiet=extra_config.get("quiet", False),
            plain=extra_config.get("plain", False),
        )
