#!/usr/bin/env python3
"""
Changelog update helper script for git-batch-pull.
Helps detect changes and suggests changelog updates.
"""

import subprocess
import sys
from pathlib import Path


def run_git_command(cmd):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_changed_files():
    """Get list of changed files since last commit."""
    # Try different git commands to get changes
    commands = [
        ["git", "diff", "--name-only", "HEAD"],  # Changes since last commit
        ["git", "diff", "--cached", "--name-only"],  # Staged changes
        ["git", "status", "--porcelain"],  # All changes
    ]

    for cmd in commands:
        output = run_git_command(cmd)
        if output:
            if cmd[1] == "status":
                # Parse porcelain output
                files = []
                for line in output.split("\n"):
                    if line.strip():
                        files.append(line[3:])  # Remove status prefix
                return files
            else:
                return output.split("\n") if output else []

    return []


def analyze_changes(files):
    """Analyze changed files and suggest changelog categories."""
    suggestions = {
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Security": [],
        "Technical": [],
        "Documentation": [],
        "Breaking Changes": [],
    }

    for file in files:
        if not file.strip():
            continue

        # Documentation changes
        if file.startswith("docs/") or file.endswith(".md"):
            if "security" in file.lower():
                suggestions["Security"].append(f"Updated {file}")
            else:
                suggestions["Documentation"].append(f"Updated {file}")

        # Source code changes
        elif file.startswith("src/"):
            if "security" in file:
                suggestions["Security"].append(f"Enhanced {file}")
            elif "cli" in file:
                suggestions["Changed"].append(f"Updated CLI in {file}")
            elif "test" in file:
                suggestions["Technical"].append(f"Updated tests in {file}")
            else:
                suggestions["Changed"].append(f"Modified {file}")

        # Test changes
        elif file.startswith("tests/"):
            suggestions["Technical"].append(f"Updated tests in {file}")

        # Configuration changes
        elif file.endswith((".yml", ".yaml", ".toml", ".cfg", ".ini")):
            suggestions["Technical"].append(f"Updated configuration in {file}")

        # CI/CD changes
        elif ".github" in file:
            suggestions["Technical"].append(f"Updated CI/CD in {file}")

        # Docker changes
        elif "docker" in file.lower() or file == "Dockerfile":
            suggestions["Technical"].append("Updated Docker configuration")

        # Dependencies
        elif "requirements" in file or file == "pyproject.toml":
            suggestions["Technical"].append(f"Updated dependencies in {file}")

    return suggestions


def format_suggestions(suggestions):
    """Format suggestions for changelog."""
    output = []
    output.append("# Suggested Changelog Updates")
    output.append("")
    output.append("Based on the changed files, here are suggested changelog entries:")
    output.append("")

    for category, items in suggestions.items():
        if items:
            output.append(f"### {category}")
            for item in items:
                output.append(f"- {item}")
            output.append("")

    return "\n".join(output)


def main():
    """Main function."""
    print("🔍 Analyzing changes for changelog updates...")

    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    # Get changed files
    changed_files = get_changed_files()

    if not changed_files:
        print("✅ No changes detected")
        return

    print(f"📁 Found {len(changed_files)} changed files")

    # Analyze changes
    suggestions = analyze_changes(changed_files)

    # Format and display suggestions
    formatted = format_suggestions(suggestions)
    print("\n" + formatted)

    # Save to file
    output_file = Path("changelog_suggestions.md")
    output_file.write_text(formatted)
    print(f"\n💾 Suggestions saved to {output_file}")

    print("\n📝 Next steps:")
    print("1. Review the suggestions above")
    print("2. Update CHANGELOG.md manually with appropriate entries")
    print("3. Use semantic commit messages for future changes")
    print("4. Run this script before major releases")


if __name__ == "__main__":
    main()
