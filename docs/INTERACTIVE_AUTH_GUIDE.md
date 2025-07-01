# Interactive HTTPS Authentication Guide

## Overview

Git Batch Pull provides **interactive HTTPS authentication** that allows you to securely enter your GitHub credentials once and have them applied to all repositories during a sync operation. This feature is especially useful for:

- **Private repositories** that require authentication
- **Organizations with mixed visibility** (public/private repositories)
- **Users who prefer not to store tokens in environment variables**
- **Temporary or one-time operations** where you don't want to persist credentials

## How It Works

When you use the `--interactive-auth` flag with HTTPS:

1. **Single Prompt**: You'll be prompted once for your GitHub username and personal access token
2. **Secure Input**: Your token is hidden while typing (like password input)
3. **Credential Caching**: Credentials are cached in memory for the duration of the operation
4. **Automatic Application**: All repositories in the sync use the same credentials
5. **Memory Cleanup**: Credentials are automatically cleared when the operation completes

## Usage

### Basic Interactive Authentication

```bash
# Clone all repositories with interactive authentication
git-batch-pull sync org myorg --interactive-auth

# Clone only private repositories
git-batch-pull sync org myorg --interactive-auth --visibility private

# Clone specific repositories
git-batch-pull sync user myuser --interactive-auth --repos "repo1,repo2,repo3"
```

### Combined with Other Options

```bash
# Interactive auth with parallel processing
git-batch-pull sync org myorg --interactive-auth --max-workers 3

# Interactive auth with detailed logging
git-batch-pull sync org myorg --interactive-auth --log-level DEBUG

# Dry run to see what would be processed
git-batch-pull sync org myorg --interactive-auth --dry-run
```

## Example Session

```bash
$ git-batch-pull sync org mycompany --interactive-auth --visibility private

🔐 HTTPS Authentication Required
Enter your GitHub credentials for HTTPS access:
GitHub Username: myusername
GitHub Token/Password: [hidden input]

Fetching repositories for org 'mycompany'...
Found 15 repositories
Processing 15 repositories
Successfully processed: private-repo-1
Successfully processed: private-repo-2
Successfully processed: internal-tool
...
Summary: 15 processed, 0 failed
```

## Security Features

### ✅ Secure Input
- Token/password input is hidden (uses `getpass` module)
- No credentials are displayed in logs or terminal output
- Clone URLs in logs are truncated to prevent credential exposure

### ✅ Memory Management
- Credentials are cached only in memory during the operation
- Automatic cleanup when the operation completes or fails
- No persistent storage of credentials

### ✅ Error Handling
- Clear error messages for authentication failures
- Graceful handling of invalid credentials
- No credential leakage in error messages

## Authentication Requirements

### GitHub Personal Access Token (Recommended)
Create a GitHub Personal Access Token with appropriate permissions:

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens**
2. Click **Generate new token (classic)**
3. Select scopes based on your needs:
   - `repo` - Full repository access (for private repos)
   - `public_repo` - Public repository access only
   - `read:org` - Read organization membership (if needed)
4. Generate and copy the token

### Password Authentication (Legacy)
GitHub password authentication is deprecated and not recommended. Use personal access tokens instead.

## Comparison with Other Authentication Methods

| Method | Security | Convenience | Use Case |
|--------|----------|-------------|----------|
| **Interactive Auth** | ⭐⭐⭐⭐ | ⭐⭐⭐ | One-time operations, private repos |
| **Environment Variable** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Automated scripts, CI/CD |
| **Keyring Storage** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Regular use, persistent storage |
| **SSH Keys** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Power users, best security |

## Troubleshooting

### "Authentication failed" Error
- Verify your username is correct (case-sensitive)
- Ensure your token has the necessary permissions
- Check if your token has expired
- For organizations, verify you have access to the repositories

### "Username cannot be empty" Error
- Make sure to enter your GitHub username when prompted
- Don't leave the username field blank

### "Token/Password cannot be empty" Error
- Enter your personal access token when prompted
- Don't use your GitHub password (it's deprecated)

### Repository Access Issues
```bash
# Test access to a specific repository first
git-batch-pull sync org myorg --interactive-auth --repos "specific-repo" --dry-run
```

## Limitations

1. **HTTPS Only**: Interactive authentication only works with HTTPS URLs (not SSH)
2. **Manual Input**: Requires user interaction, not suitable for automated scripts
3. **Single Session**: Credentials are not persisted between different command runs
4. **Terminal Required**: Needs an interactive terminal for credential input

## Best Practices

### ✅ Do
- Use personal access tokens instead of passwords
- Grant minimal necessary permissions to tokens
- Test with `--dry-run` first for large operations
- Use `--repos` to limit scope for testing

### ❌ Don't
- Share or commit your personal access tokens
- Use expired or invalid tokens
- Use interactive auth in automated scripts
- Skip the dry-run for large repository sets

## Integration Examples

### Private Organization Repositories
```bash
# Clone all private repositories from your organization
git-batch-pull sync org myorg --interactive-auth --visibility private
```

### Mixed Repository Types
```bash
# Clone all repositories (public and private) with authentication
git-batch-pull sync org myorg --interactive-auth --visibility all
```

### Development Workflow
```bash
# Clone specific development repositories
git-batch-pull sync org mycompany \
  --interactive-auth \
  --repos "backend-api,frontend-app,mobile-app" \
  --max-workers 3
```

---

## Related Documentation

- [Command Reference](COMMAND_REFERENCE.md) - Complete CLI options
- [SSH Guide](SSH_GUIDE.md) - SSH key authentication setup
- [Quick Start](QUICK_START.md) - Getting started guide
- [Installation](INSTALLATION.md) - Installation instructions
