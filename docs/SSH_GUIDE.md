# 🔐 SSH Setup and Usage Guide

Complete guide for using git-batch-pull with SSH authentication for enhanced security and performance.

## 📋 Table of Contents

- [Why Use SSH?](#why-use-ssh)
- [SSH Prerequisites](#ssh-prerequisites)
- [SSH Key Setup](#ssh-key-setup)
- [Configuration for SSH](#configuration-for-ssh)
- [Command Usage](#command-usage)
- [Protocol Switching](#protocol-switching)
- [Troubleshooting](#troubleshooting)

---

## 🔒 Why Use SSH?

**Benefits of SSH over HTTPS:**
- ✅ **Better Security**: Public key authentication instead of tokens
- ✅ **No Token Management**: No need to manage GitHub Personal Access Tokens for git operations
- ✅ **Better Performance**: Faster authentication and connection reuse
- ✅ **No Rate Limits**: SSH doesn't have the same API rate limits as HTTPS

**When to Use SSH:**
- You have SSH keys set up with GitHub
- You're working with private repositories frequently
- You want to avoid Personal Access Token management for git operations
- You need better performance for large repository operations

---

## 🔧 SSH Prerequisites

### 1. SSH Key Generation
If you don't have SSH keys yet:

```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Or use RSA (if ed25519 not supported)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Start SSH agent and add your key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519  # or ~/.ssh/id_rsa
```

### 2. Add SSH Key to GitHub
```bash
# Copy your public key
cat ~/.ssh/id_ed25519.pub  # or ~/.ssh/id_rsa.pub

# Then add it to: GitHub → Settings → SSH and GPG keys → New SSH key
```

### 3. Test SSH Connection
```bash
# Test connection to GitHub
ssh -T git@github.com

# Should see: "Hi username! You've successfully authenticated..."
```

---

## ⚙️ Configuration for SSH

### Method 1: Command Line Flag
Use the `--ssh` flag with any command:

```bash
git-batch-pull sync org myorg --ssh
git-batch-pull clone org myorg --repos "repo1,repo2" --ssh
git-batch-pull pull user myuser --ssh
```

### Method 2: Configuration File
Set `use_ssh = true` in your config file:

**config.toml:**
```toml
[general]
log_level = "INFO"

[github]
use_ssh = true              # Use SSH URLs for all git operations
entity_type = "org"
entity_name = "myorg"
```

Then use with config:
```bash
git-batch-pull sync --config config.toml
```

### Method 3: Environment Variable
Set in your environment:

```bash
# In your .env file or environment
USE_SSH=true

git-batch-pull sync org myorg
```

---

## 🚀 Command Usage

### Basic SSH Commands

```bash
# Sync all repositories using SSH
git-batch-pull sync org myorg --ssh

# Clone specific repositories using SSH
git-batch-pull clone org myorg --repos "repo1,repo2,repo3" --ssh

# Pull updates for existing repositories using SSH
git-batch-pull pull user myuser --ssh

# Use SSH with batch processing
git-batch-pull batch --config config.toml  # (with use_ssh = true in config)
```

### Advanced SSH Usage

```bash
# Combine SSH with other options
git-batch-pull sync org myorg --ssh --quiet --verbose
git-batch-pull sync org myorg --ssh --visibility private
git-batch-pull sync org myorg --ssh --repos "core-repo,api-repo"

# Use SSH with custom local folder
LOCAL_FOLDER=/path/to/repos git-batch-pull sync org myorg --ssh

# SSH with specific visibility
git-batch-pull sync org myorg --ssh --visibility public
git-batch-pull sync org myorg --ssh --visibility private
git-batch-pull sync org myorg --ssh --visibility all
```

### Batch Operations with SSH

**config.toml:**
```toml
[general]
quiet = false
max_workers = 1

[github]
use_ssh = true
entity_type = "org"
entity_name = "myorg"
repos = ["repo1", "repo2", "repo3"]  # Optional: specific repos only
```

```bash
git-batch-pull batch --config config.toml
```

---

## 🔄 Protocol Switching

git-batch-pull automatically detects and handles protocol mismatches:

### Automatic Detection
```bash
# If repositories exist with HTTPS but you want SSH
git-batch-pull sync org myorg --ssh

# Tool will detect the mismatch and prompt:
# "Repository 'repo1' is currently using HTTPS but you specified SSH. Switch? [y/N]"
```

### Force Protocol Updates
```bash
# Switch existing HTTPS repositories to SSH
git-batch-pull switch-protocol ssh /path/to/repos

# Switch existing SSH repositories to HTTPS
git-batch-pull switch-protocol https /path/to/repos
```

### Mixed Protocol Handling
- **Existing HTTPS + --ssh flag**: Prompts to switch each repository
- **Existing SSH + no --ssh flag**: Prompts to switch to HTTPS
- **Same protocol**: No prompts, continues normally

---

## 🔍 Verification and Status

### Check Current Protocol
```bash
# Check what protocol repositories are using
git-batch-pull status /path/to/your/repos

# Output shows:
# ✅ repo1: SSH (git@github.com:org/repo1.git)
# ⚠️  repo2: HTTPS (https://github.com/org/repo2.git)
```

### Health Check
```bash
# Verify SSH connectivity and repository status
git-batch-pull health-check --ssh

# Checks:
# ✅ SSH key authentication
# ✅ GitHub connectivity
# ✅ Repository access
# ✅ Local directory permissions
```

---

## 🛠️ Troubleshooting

### Common SSH Issues

**1. SSH Key Not Found**
```bash
# Error: "Permission denied (publickey)"
# Solution: Check SSH key setup
ssh -T git@github.com
ssh-add -l  # List loaded keys
ssh-add ~/.ssh/id_ed25519  # Add key if missing
```

**2. SSH Agent Not Running**
```bash
# Error: "Could not open a connection to your authentication agent"
# Solution: Start SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**3. Repository Access Issues**
```bash
# Error: "Repository not found"
# Solution: Check repository permissions and SSH key access
ssh -T git@github.com  # Verify GitHub authentication
# Ensure SSH key has access to the repository
```

**4. Host Key Verification**
```bash
# Error: "Host key verification failed"
# Solution: Add GitHub to known hosts
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Debug Mode
```bash
# Run with verbose output to debug issues
git-batch-pull sync org myorg --ssh --verbose

# Check SSH connection with debug
ssh -vT git@github.com
```

### Configuration Troubleshooting
```bash
# Verify SSH is being used
git-batch-pull sync org myorg --ssh --dry-run

# Check configuration
git-batch-pull config-check --config config.toml
```

---

## 🎯 Best Practices

### Security
- ✅ Use SSH keys with passphrases
- ✅ Regularly rotate SSH keys
- ✅ Use different keys for different purposes
- ✅ Monitor SSH key usage in GitHub

### Performance
- ✅ Use SSH for large batch operations
- ✅ Configure SSH connection reuse:
  ```bash
  # Add to ~/.ssh/config
  Host github.com
    ControlMaster auto
    ControlPath ~/.ssh/master-%r@%h:%p
    ControlPersist 300
  ```

### Workflow
- ✅ Set up SSH once, use everywhere
- ✅ Use config files for consistent settings
- ✅ Test SSH connectivity before large operations

---

## 📚 Related Documentation

- [Installation Guide](INSTALLATION.md) - Complete setup instructions
- [Command Reference](COMMAND_REFERENCE.md) - All available commands
- [Configuration Guide](../config.toml.example) - Configuration options
- [Security Guide](SECURITY.md) - Security best practices

---

## ❓ Need Help?

- 🐛 **Issues**: [GitHub Issues](https://github.com/alpersonalwebsite/git_batch_pull/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/alpersonalwebsite/git_batch_pull/discussions)
- 📖 **Documentation**: [docs/](../docs/)
- 🔒 **Security**: [SECURITY.md](../SECURITY.md)
