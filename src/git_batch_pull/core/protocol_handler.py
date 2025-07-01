"""Protocol handling and mismatch detection."""

import logging
from typing import Callable, List, Optional

from ..models import Repository, RepositoryBatch
from ..services import RepositoryService


class ProtocolHandler:
    """
    Handles protocol detection, mismatch resolution, and user prompts.
    """

    def __init__(self, repository_service: RepositoryService):
        """
        Initialize protocol handler.

        Args:
            repository_service: Repository service for protocol operations
        """
        self.repository_service = repository_service
        self.logger = logging.getLogger(__name__)

    def detect_and_handle_mismatches(
        self,
        batch: RepositoryBatch,
        intended_protocol: str,
        entity_name: str,
        dry_run: bool = False,
        prompt_callback: Optional[Callable[[List[tuple[str, str]], str], bool]] = None,
    ) -> bool:
        """
        Detect protocol mismatches and handle them.

        Args:
            batch: Repository batch to check
            intended_protocol: Intended protocol ('ssh' or 'https')
            entity_name: GitHub entity name
            dry_run: Whether this is a dry run
            prompt_callback: Optional callback for user prompts

        Returns:
            True if mismatches were handled, False if user declined
        """
        mismatches = self.repository_service.detect_protocol_mismatches(batch, intended_protocol)

        if not mismatches:
            self.logger.debug("No protocol mismatches detected")
            return True

        self.logger.warning(f"Detected {len(mismatches)} protocol mismatches")

        for repo_name, current_url in mismatches:
            self.logger.warning(f"  - {repo_name}: {current_url}")

        if dry_run:
            self.logger.info("[DRY RUN] Would fix protocol mismatches")
            return True

        # Ask user if they want to fix mismatches
        if prompt_callback:
            should_fix = prompt_callback(mismatches, intended_protocol)
        else:
            should_fix = self._default_prompt(mismatches, intended_protocol)

        if should_fix:
            self.logger.info(f"Fixing protocol mismatches to {intended_protocol.upper()}")
            self.repository_service.fix_protocol_mismatches(batch, intended_protocol, entity_name)
            return True
        else:
            self.logger.info("Continuing with existing protocols")
            return False

    def handle_protocol_mismatches(
        self,
        repositories: List[Repository],
        intended_protocol: str,
        entity_name: str,
        dry_run: bool = False,
        prompt_callback: Optional[Callable[[List[tuple[str, str]], str], bool]] = None,
    ) -> bool:
        """
        Handle protocol mismatches for a list of repositories.

        Args:
            repositories: List of repositories to check
            intended_protocol: Intended protocol ('ssh' or 'https')
            entity_name: GitHub entity name
            dry_run: Whether this is a dry run
            prompt_callback: Optional callback for user prompts

        Returns:
            True if mismatches were handled, False if user declined
        """
        # Create a temporary batch from the repository list
        from ..models import RepositoryBatch

        batch = RepositoryBatch(repositories=repositories, entity_type="mixed", entity_name="batch")
        return self.detect_and_handle_mismatches(
            batch, intended_protocol, entity_name, dry_run, prompt_callback
        )

    def _default_prompt(self, mismatches: List[tuple[str, str]], intended_protocol: str) -> bool:
        """
        Default prompt implementation for protocol mismatch handling.

        Args:
            mismatches: List of (repo_name, current_url) tuples
            intended_protocol: Intended protocol

        Returns:
            True if user wants to fix mismatches
        """
        print(f"\nProtocol mismatch detected in {len(mismatches)} repositories:")
        for repo_name, current_url in mismatches:
            print(f"  - {repo_name}: {current_url}")

        print("\nOptions:")
        print(f"1. Update all repositories to use {intended_protocol.upper()}")
        print("2. Continue with current protocols")

        while True:
            try:
                choice = input("Enter 1 or 2: ").strip()
                if choice == "1":
                    return True
                elif choice == "2":
                    return False
                else:
                    print("Please enter 1 or 2")
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled")
                return False

    def warn_about_protocol_mismatch(
        self, repo_path: str, intended_protocol: Optional[str] = None
    ) -> str:
        """
        Generate a warning message about protocol mismatch.

        Args:
            repo_path: Path to the repository
            intended_protocol: Intended protocol ('ssh', 'https', or None)

        Returns:
            Warning message or empty string if no mismatch
        """
        from ..protocol_utils import detect_protocol_mismatch

        return detect_protocol_mismatch(repo_path, intended_protocol)
