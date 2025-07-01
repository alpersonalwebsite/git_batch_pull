#!/usr/bin/env python3
"""
Script to check changes for changelog updates.

This script helps identify what has changed locally compared to what's on GitHub,
making it easier to update the changelog with accurate information.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def run_git_command(command: List[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return ""


def get_git_status() -> Dict[str, List[str]]:
    """Get current git status categorized by change type."""
    status_output = run_git_command(["git", "status", "--porcelain"])

    changes = {"modified": [], "added": [], "deleted": [], "renamed": [], "untracked": []}

    for line in status_output.split("\n"):
        if not line.strip():
            continue

        status_code = line[:2]
        file_path = line[3:]

        if status_code[0] == "M" or status_code[1] == "M":
            changes["modified"].append(file_path)
        elif status_code[0] == "A" or status_code[1] == "A":
            changes["added"].append(file_path)
        elif status_code[0] == "D" or status_code[1] == "D":
            changes["deleted"].append(file_path)
        elif status_code[0] == "R":
            changes["renamed"].append(file_path)
        elif status_code == "??":
            changes["untracked"].append(file_path)

    return changes


def get_commit_history(since: str = "HEAD~10") -> List[str]:
    """Get recent commit messages."""
    log_output = run_git_command(["git", "log", f"{since}..HEAD", "--oneline", "--no-merges"])

    if not log_output:
        return []

    return [line.strip() for line in log_output.split("\n") if line.strip()]


def analyze_file_changes(file_path: str) -> str:
    """Analyze what changed in a specific file."""
    if not Path(file_path).exists():
        return "File was deleted"

    diff_output = run_git_command(["git", "diff", "HEAD", "--", file_path])
    if not diff_output:
        # Try staged changes
        diff_output = run_git_command(["git", "diff", "--cached", "--", file_path])

    if not diff_output:
        return "New file"

    # Count additions and deletions
    lines = diff_output.split("\n")
    additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))

    return f"+{additions} -{deletions} lines"


def categorize_changes(changes: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Categorize changes by type for changelog."""
    categories = {
        "features": [],
        "bugfixes": [],
        "documentation": [],
        "tests": [],
        "config": [],
        "security": [],
        "other": [],
    }

    all_files = []
    for change_type, files in changes.items():
        all_files.extend(files)

    for file_path in all_files:
        if file_path.startswith(("docs/", "README", "*.md")):
            categories["documentation"].append(file_path)
        elif file_path.startswith("tests/"):
            categories["tests"].append(file_path)
        elif file_path.endswith((".yml", ".yaml", ".toml", ".cfg", ".ini")):
            categories["config"].append(file_path)
        elif "security" in file_path.lower() or "auth" in file_path.lower():
            categories["security"].append(file_path)
        elif file_path.startswith("src/"):
            # Could be features or bugfixes - would need commit analysis
            categories["features"].append(file_path)
        else:
            categories["other"].append(file_path)

    return categories


def generate_changelog_suggestions(changes: Dict[str, List[str]]) -> str:
    """Generate changelog suggestions based on changes."""
    categories = categorize_changes(changes)

    suggestions = []
    suggestions.append("## Suggested Changelog Updates")
    suggestions.append("")

    if categories["features"]:
        suggestions.append("### Added")
        for file_path in categories["features"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    if categories["documentation"]:
        suggestions.append("### Documentation")
        for file_path in categories["documentation"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    if categories["security"]:
        suggestions.append("### Security")
        for file_path in categories["security"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    if categories["tests"]:
        suggestions.append("### Testing")
        for file_path in categories["tests"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    if categories["config"]:
        suggestions.append("### Configuration")
        for file_path in categories["config"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    if categories["other"]:
        suggestions.append("### Other")
        for file_path in categories["other"]:
            change_info = analyze_file_changes(file_path)
            suggestions.append(f"- Updated `{file_path}` ({change_info})")
        suggestions.append("")

    return "\n".join(suggestions)


def main():
    """Main function to analyze changes and provide changelog suggestions."""
    print("🔍 Analyzing local changes for changelog updates...")
    print("=" * 60)

    # Check if we're in a git repository
    try:
        run_git_command(["git", "rev-parse", "--git-dir"])
    except:
        print("❌ Not in a git repository!")
        sys.exit(1)

    # Get current changes
    changes = get_git_status()

    print("\n📊 Current Changes Summary:")
    print("-" * 30)

    total_changes = sum(len(files) for files in changes.values())
    if total_changes == 0:
        print("✅ No local changes detected")
        print("\n💡 If you haven't committed yet, your changes are all in the working directory.")
        print("   Consider what you've added/modified since your last commit or tag.")
    else:
        for change_type, files in changes.items():
            if files:
                print(f"{change_type.title()}: {len(files)} files")
                for file_path in files[:5]:  # Show first 5
                    print(f"  - {file_path}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")

    # Get recent commits
    print("\n📝 Recent Commits:")
    print("-" * 20)
    recent_commits = get_commit_history()
    if recent_commits:
        for commit in recent_commits:
            print(f"  {commit}")
    else:
        print("  No recent commits found")

    # Generate suggestions
    if total_changes > 0:
        print("\n" + generate_changelog_suggestions(changes))

    print("\n" + "=" * 60)
    print("💡 Tips for updating your changelog:")
    print("1. Focus on user-facing changes (features, fixes, breaking changes)")
    print("2. Group changes by category (Added, Changed, Fixed, Security, etc.)")
    print("3. Use action verbs and be specific about what changed")
    print("4. Include any breaking changes prominently")
    print("5. Don't include internal refactoring unless it affects users")

    print("\n📖 Your current changelog is in: CHANGELOG.md")
    print("🔗 Follow keepachangelog.com format for consistency")


if __name__ == "__main__":
    main()
