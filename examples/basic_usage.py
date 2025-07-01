#!/usr/bin/env python3
"""
Basic Usage Examples for git-batch-pull

This script demonstrates common usage patterns for git-batch-pull.
Run each example individually to see how the tool works.
"""


def run_command(cmd: str, description: str) -> None:
    """Run a command and show the output."""
    print(f"\n🔹 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)

    # In real usage, you would run:
    # subprocess.run(cmd.split(), check=True)

    # For demo purposes, just show what would be executed
    print(f"[DEMO] Would execute: {cmd}")
    print("[DEMO] This would clone/pull the specified repositories")


def main():
    """Demonstrate common git-batch-pull usage patterns."""

    print("🚀 git-batch-pull Usage Examples")
    print("=" * 50)

    # Basic examples
    run_command(
        "git-batch-pull sync user octocat", "Clone all public repositories for user 'octocat'"
    )

    run_command(
        "git-batch-pull sync org github --ssh", "Clone all repositories for GitHub org using SSH"
    )

    # Filtering examples
    run_command(
        "git-batch-pull sync user octocat --repos 'repo1,repo2,repo3'",
        "Clone only specific repositories",
    )

    run_command(
        "git-batch-pull sync org myorg --exclude-archived --exclude-forks",
        "Clone org repos, excluding archived and forked repositories",
    )

    # Advanced examples
    run_command(
        "git-batch-pull sync user username --ssh --dry-run",
        "Preview what would be cloned with SSH (dry run)",
    )

    run_command(
        "git-batch-pull sync org myorg --max-workers 3 --quiet",
        "Clone with 3 parallel workers, minimal output",
    )

    print("\n✅ Examples completed!")
    print("\n📚 For more information:")
    print("   git-batch-pull --help")
    print("   git-batch-pull sync --help")
    print("   git-batch-pull health")


if __name__ == "__main__":
    main()
