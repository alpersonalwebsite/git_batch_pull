"""Compatibility module for backward compatibility with tests."""

# Re-export from new CLI for backward compatibility
from .cli import app


def prompt_protocol_switch(repos_with_mismatch, target_protocol):
    """Prompt the user to switch protocols for mismatched repositories.

    Args:
        repos_with_mismatch: List of (repo_name, remote_url) tuples.
        target_protocol: The protocol to switch to ("ssh" or "https").

    Returns:
        bool: True if user chooses to update, False otherwise.
    """
    # User-facing info: keep as print
    print("\nProtocol mismatch detected in the following repositories:")
    for repo_name, remote_url in repos_with_mismatch:
        print(f"  - {repo_name}: {remote_url}")
    print("\nOptions:")
    print(f"1. Update all these repositories to use {target_protocol.upper()}")
    print("2. Continue using the current protocol for these repositories")
    choice = input("Enter 1 or 2 and press Enter: ").strip()
    return choice == "1"


__all__ = ["prompt_protocol_switch", "app"]
