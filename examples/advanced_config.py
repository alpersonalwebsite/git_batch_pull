#!/usr/bin/env python3
"""
Advanced Configuration Examples for git-batch-pull

Demonstrates how to use configuration files, environment variables,
and advanced features for enterprise or power user scenarios.
"""

import tempfile


def create_example_config():
    """Create an example configuration file."""

    config_content = """
# git-batch-pull Configuration File
# Save as ~/.config/git-batch-pull/config.toml

[github]
# GitHub API token (recommended to use environment variable or keyring)
# token = "ghp_your_token_here"

# API base URL (for GitHub Enterprise)
# api_base_url = "https://api.github.com"

[storage]
# Base directory for cloned repositories
base_folder = "~/repos"

# Cache file for repository metadata
cache_file = "~/.cache/git-batch-pull/repos.json"

[behavior]
# Default protocol for cloning
default_protocol = "https"  # or "ssh"

# Default number of parallel workers
max_workers = 1

# Exclude archived repositories by default
exclude_archived = false

# Exclude forked repositories by default
exclude_forks = false

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR
level = "INFO"

# Log file path (optional)
# file = "~/.logs/git-batch-pull.log"

# Error log file (optional)
# error_file = "~/.logs/git-batch-pull-errors.log"

[security]
# Use keyring for secure token storage
use_keyring = true

# Timeout for git operations (seconds)
git_timeout = 300

# Timeout for API requests (seconds)
api_timeout = 30
"""

    # Write to temporary file for demonstration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(config_content.strip())
        print(f"📝 Example config created at: {f.name}")
        print("\n📋 Config file contents:")
        print(config_content.strip())
        return f.name


def show_environment_variables():
    """Show environment variable examples."""

    print("\n🌍 Environment Variables")
    print("=" * 30)

    env_vars = {
        "GITHUB_TOKEN": "Your GitHub personal access token",
        "GIT_BATCH_PULL_BASE_FOLDER": "Override default repository folder",
        "GIT_BATCH_PULL_LOG_LEVEL": "Override log level (DEBUG, INFO, WARNING, ERROR)",
        "GIT_BATCH_PULL_MAX_WORKERS": "Override parallel workers count",
        "GIT_BATCH_PULL_USE_SSH": "Default to SSH protocol (true/false)",
    }

    for var, description in env_vars.items():
        print(f"  {var}={description}")

    print("\n💡 Example usage:")
    print("  export GITHUB_TOKEN='ghp_your_token_here'")
    print("  export GIT_BATCH_PULL_BASE_FOLDER='~/work/repos'")
    print("  git-batch-pull sync user octocat")


def show_advanced_examples():
    """Show advanced usage examples."""

    print("\n🔧 Advanced Examples")
    print("=" * 25)

    examples = [
        {
            "title": "Enterprise GitHub with custom config",
            "command": "git-batch-pull sync org myorg --config /path/to/enterprise-config.toml",
            "description": "Use custom configuration for GitHub Enterprise",
        },
        {
            "title": "Batch processing with repository list file",
            "command": "git-batch-pull sync user username --repos-file repos.txt",
            "description": "Process repositories listed in a file (one per line)",
        },
        {
            "title": "Secure token with keyring",
            "command": "git-batch-pull sync org myorg --use-keyring",
            "description": "Store and retrieve GitHub token securely using system keyring",
        },
        {
            "title": "Custom logging and debugging",
            "command": "git-batch-pull sync user username --log-level DEBUG --log-file debug.log",
            "description": "Enable detailed logging for troubleshooting",
        },
        {
            "title": "Force refresh repository cache",
            "command": "git-batch-pull sync org myorg --refetch",
            "description": "Force re-fetch repository list from GitHub API",
        },
        {
            "title": "Protocol switching workflow",
            "command": "git-batch-pull sync user username --ssh  # Run after using HTTPS",
            "description": "Automatically detect protocol mismatches and prompt for updates",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   Command: {example['command']}")
        print(f"   Description: {example['description']}")


def show_integration_examples():
    """Show integration examples for CI/CD and scripts."""

    print("\n🔗 Integration Examples")
    print("=" * 28)

    # GitHub Actions example
    print("\n📄 GitHub Actions (.github/workflows/sync-repos.yml):")
    print(
        """
name: Sync Repositories
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install git-batch-pull
        run: pip install git-batch-pull
      - name: Sync repositories
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git-batch-pull sync org myorg --exclude-archived --quiet
"""
    )

    # Shell script example
    print("\n📄 Shell Script (sync-all-repos.sh):")
    print(
        """
#!/bin/bash
set -euo pipefail

# Configuration
ORG_NAME="myorg"
REPOS_DIR="$HOME/repos"
LOG_FILE="$HOME/logs/repo-sync.log"

# Ensure directories exist
mkdir -p "$REPOS_DIR" "$(dirname "$LOG_FILE")"

# Run sync with logging
echo "$(date): Starting repository sync for $ORG_NAME" >> "$LOG_FILE"

git-batch-pull sync org "$ORG_NAME" \\
    --exclude-archived \\
    --exclude-forks \\
    --log-file "$LOG_FILE" \\
    --quiet

echo "$(date): Repository sync completed" >> "$LOG_FILE"
"""
    )

    # Python script example
    print("\n📄 Python Integration (repo_manager.py):")
    print(
        """
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def sync_repositories(org_name, use_ssh=False, dry_run=False):
    \"\"\"Sync repositories for an organization.\"\"\"

    cmd = [
        "git-batch-pull", "sync", "org", org_name,
        "--exclude-archived", "--exclude-forks"
    ]

    if use_ssh:
        cmd.append("--ssh")
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully synced {org_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to sync {org_name}: {e}")
        return False

if __name__ == "__main__":
    orgs = ["myorg1", "myorg2", "myorg3"]
    for org in orgs:
        sync_repositories(org, use_ssh=True)
"""
    )


def main():
    """Run all advanced configuration examples."""

    print("🚀 git-batch-pull Advanced Configuration Examples")
    print("=" * 55)

    # Create example config
    config_file = create_example_config()

    # Show environment variables
    show_environment_variables()

    # Show advanced examples
    show_advanced_examples()

    # Show integration examples
    show_integration_examples()

    print("\n🧹 Cleanup: Remember to delete the example config file:")
    print(f"   rm {config_file}")

    print("\n✅ Advanced examples completed!")
    print("\n📚 For more information:")
    print("   git-batch-pull health  # Check system configuration")
    print("   git-batch-pull --help  # Full command reference")


if __name__ == "__main__":
    main()
