#!/bin/bash
# Changelog Helper Script
# Usage: ./scripts/check-changes.sh

set -e

echo "🔍 Git Batch Pull - Change Detection Helper"
echo "==========================================="

# Check if we have any commits
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

if [ "$COMMIT_COUNT" -eq "0" ]; then
    echo "📋 This is your initial commit. Here's what you're about to add:"
    echo ""
    echo "📁 Total files staged: $(git diff --cached --name-only | wc -l)"
    echo ""
    echo "📊 Breakdown by type:"
    echo "   Python files: $(git diff --cached --name-only | grep '\.py$' | wc -l)"
    echo "   Documentation: $(git diff --cached --name-only | grep '\.md$' | wc -l)"
    echo "   Configuration: $(git diff --cached --name-only | grep -E '\.(yml|yaml|toml|json)$' | wc -l)"
    echo "   Tests: $(git diff --cached --name-only | grep 'test_.*\.py$' | wc -l)"
    echo ""
    echo "🏗️  Key architecture components added:"
    git diff --cached --name-only | grep -E 'src/.*/(cli|core|services|security|models)/' | sort
    echo ""
    echo "📚 Documentation added:"
    git diff --cached --name-only | grep '\.md$' | grep -v README | sort
    echo ""
    echo "✅ This looks like a comprehensive initial release!"
    echo "   Your CHANGELOG.md should reflect this as version 1.0.0"
else
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

    if [ -z "$LAST_TAG" ]; then
        echo "📋 No tags found. Showing changes since first commit:"
        COMPARE_POINT=$(git rev-list --max-parents=0 HEAD)
    else
        echo "📋 Showing changes since last tag: $LAST_TAG"
        COMPARE_POINT=$LAST_TAG
    fi

    echo ""
    echo "📊 Files changed: $(git diff --name-only $COMPARE_POINT..HEAD | wc -l)"
    echo ""

    echo "🐍 Python modules modified:"
    git diff --name-only $COMPARE_POINT..HEAD | grep '\.py$' | head -10 || echo "   None"

    echo ""
    echo "📚 Documentation modified:"
    git diff --name-only $COMPARE_POINT..HEAD | grep '\.md$' | head -10 || echo "   None"

    echo ""
    echo "⚙️  Configuration modified:"
    git diff --name-only $COMPARE_POINT..HEAD | grep -E '\.(yml|yaml|toml|json)$' | head -10 || echo "   None"

    echo ""
    echo "📝 Recent commits:"
    git log $COMPARE_POINT..HEAD --oneline | head -10 || echo "   None"

    echo ""
    echo "🔄 Changes to review for changelog:"
    echo "   1. Check if any new features were added"
    echo "   2. Look for bug fixes"
    echo "   3. Note any breaking changes"
    echo "   4. Document security improvements"
fi

echo ""
echo "📖 Next steps:"
echo "   1. Review CHANGELOG.md"
echo "   2. Add entries under [Unreleased] section"
echo "   3. Commit your changes"
echo "   4. Tag release when ready"

# Check if changelog was recently modified
if git diff --cached --name-only | grep -q "CHANGELOG.md"; then
    echo "   ✅ CHANGELOG.md is staged for commit"
elif [ "$COMMIT_COUNT" -gt "0" ] && git diff --name-only HEAD~1..HEAD | grep -q "CHANGELOG.md"; then
    echo "   ✅ CHANGELOG.md was updated in last commit"
else
    echo "   ⚠️  Consider updating CHANGELOG.md"
fi
