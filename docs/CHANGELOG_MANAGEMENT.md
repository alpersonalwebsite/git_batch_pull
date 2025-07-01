# CHANGELOG Management Guide

## 📋 Overview

This guide explains how the CHANGELOG is managed in the git-batch-pull project, including manual processes, automation tools, and CI/CD integration.

## � **CURRENT SITUATION - FIRST RELEASE**

You currently have **103 staged files** representing a complete project implementation. This is your **initial commit** for a brand new repository.

### **Recommended Action for Initial Release**

Since this represents a major implementation, consider this as your v2.0.0 release:

```bash
# 1. Update CHANGELOG.md to move "Unreleased" → "2.0.0" with today's date
# 2. Commit everything as initial release
git add .
git commit -m "feat: initial release v2.0.0 with complete modern architecture"
git tag v2.0.0
git push origin main --tags
```

## 🔄 Future CHANGELOG Process

### **Manual Process (Recommended)**

For future development, use this workflow:

1. **During Development**: Use conventional commits with changelog updates
2. **Before Release**: Run `python scripts/update_changelog.py` for suggestions
3. **At Release**: Use `bumpver` and CI/CD automation

### **File Structure**

```markdown
# CHANGELOG.md Structure

## [Unreleased]
### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features

### Security
- Security improvements

## [1.0.0] - 2025-06-30
### Added
- Initial release features
```

## 🛠️ Tools and Automation

### **1. bumpver (Version Management)**

**Configuration**: `bumpver.toml`
```toml
[bumpver.file_patterns]
"CHANGELOG.md" = [
    '## Unreleased',
    '## v{new_version} - {utc_now:%Y-%m-%d}'
]
```

**Usage**:
```bash
# Update patch version (1.0.0 -> 1.0.1)
bumpver update --patch

# Update minor version (1.0.0 -> 1.1.0)
bumpver update --minor

# Update major version (1.0.0 -> 2.0.0)
bumpver update --major
```

**What it does**:
- ✅ Updates version in `pyproject.toml`
- ✅ Updates version in `src/git_batch_pull/__init__.py`
- ✅ Converts `## Unreleased` to `## v{version} - {date}` in CHANGELOG.md

### **2. Release Drafter (Configured but Not Active)**

**Configuration**: `.github/release-drafter.yml`
- Generates draft release notes from PR labels
- Categories: 🚀 Features, 🐛 Bug Fixes, 🧰 Maintenance
- **Status**: Config exists but no workflow file to activate it

**To Activate** (Optional):
```yaml
# .github/workflows/release-drafter.yml
name: Release Drafter
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, reopened, synchronize]

jobs:
  update_release_draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🚀 CI/CD Integration

### **Current Workflows**

**1. CI Workflow (`.github/workflows/ci.yml`)**:
- ✅ Runs on: `push` to `main/develop`, `pull_request`
- ✅ Tests across multiple OS and Python versions
- ✅ Linting, type checking, security scans
- ❌ **No CHANGELOG validation**

**2. Release Workflow (`.github/workflows/release.yml`)**:
- ✅ Triggers on: `push` tags matching `v*`
- ✅ Runs tests, builds package, publishes to PyPI
- ✅ Creates GitHub release
- ❌ **No automatic CHANGELOG generation**

**3. Test Release Workflow (`.github/workflows/test-release.yml`)**:
- ✅ Manual trigger for TestPyPI publishing
- ✅ Safe testing before production release

### **What's Automated vs Manual**

| Task | Status | How |
|------|--------|-----|
| **Version Bumping** | 🔄 Semi-Auto | `bumpver update` (manual command) |
| **CHANGELOG Updates** | ✋ Manual | Developer updates during development |
| **Release Notes** | ✋ Manual | Created from CHANGELOG during release |
| **PyPI Publishing** | ✅ Automated | CI/CD on git tag push |
| **GitHub Releases** | ✅ Automated | CI/CD creates release from tag |

## 📝 Developer Workflow

### **Adding New Features**

1. **During Development**:
   ```bash
   # Make your changes
   git checkout -b feature/interactive-auth

   # Update CHANGELOG.md
   # Add entry under ## [Unreleased] section

   # Commit changes
   git commit -am "feat: add interactive HTTPS authentication

   Updates CHANGELOG.md with new feature description"
   ```

2. **Before PR**:
   - ✅ Ensure CHANGELOG.md is updated
   - ✅ Follow contributing guidelines checklist
   - ✅ Categorize changes (Added/Changed/Fixed/Security)

### **Creating a Release**

1. **Prepare Release**:
   ```bash
   # Ensure you're on main branch with latest changes
   git checkout main
   git pull origin main

   # Update version and CHANGELOG
   bumpver update --minor  # or --patch, --major

   # Review the changes
   git diff
   ```

2. **Publish Release**:
   ```bash
   # Commit version bump
   git commit -am "Release v1.1.0"

   # Create and push tag (triggers CI/CD)
   git tag v1.1.0
   git push origin main --tags
   ```

3. **CI/CD Takes Over**:
   - ✅ Runs full test suite
   - ✅ Builds distribution packages
   - ✅ Publishes to PyPI
   - ✅ Creates GitHub release

## 🔧 Potential Improvements

### **Option 1: Enhanced Automation with Release Drafter**

**Benefits**:
- ✅ Auto-generates release notes from PRs
- ✅ Consistent categorization with labels
- ✅ Reduces manual CHANGELOG maintenance

**Implementation**:
```bash
# Add workflow file
touch .github/workflows/release-drafter.yml

# Use PR labels: feature, bug, chore
# Release notes auto-generated on each PR merge
```

### **Option 2: Conventional Commits**

**Benefits**:
- ✅ Standardized commit messages
- ✅ Auto-generates CHANGELOG from commits
- ✅ Auto-determines version bumps

**Example**:
```bash
git commit -m "feat: add interactive authentication"
git commit -m "fix: resolve credential caching issue"
git commit -m "docs: update installation guide"
```

### **Option 3: CHANGELOG Validation in CI**

**Benefits**:
- ✅ Ensures CHANGELOG is updated for user-facing changes
- ✅ Prevents releases without proper documentation

**Implementation**:
```yaml
# Add to CI workflow
- name: Check CHANGELOG Updated
  run: |
    if git diff --name-only HEAD~1 | grep -E "(src/|docs/)" && ! git diff --name-only HEAD~1 | grep "CHANGELOG.md"; then
      echo "❌ User-facing changes detected but CHANGELOG.md not updated"
      exit 1
    fi
```

## 📋 Best Practices

### **✅ Do**
- Update CHANGELOG.md during development, not at release time
- Use clear, user-focused language in changelog entries
- Categorize changes appropriately (Added/Changed/Fixed/Security)
- Include breaking changes prominently
- Link to relevant issues/PRs when helpful

### **❌ Don't**
- Skip CHANGELOG updates for user-facing changes
- Use technical jargon that users won't understand
- Mix multiple unrelated changes in one entry
- Forget to update CHANGELOG before creating PR

## 🔗 Related Files

- **CHANGELOG.md**: Main changelog file
- **bumpver.toml**: Version bumping configuration
- **.github/release-drafter.yml**: Release notes automation config
- **CONTRIBUTING.md**: Developer guidelines including CHANGELOG requirements
- **Makefile**: Release process automation

## 📞 Questions?

For questions about the CHANGELOG process:
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
- Review [Makefile](../Makefile) for release commands
- See [.github/workflows/](../.github/workflows/) for CI/CD automation
