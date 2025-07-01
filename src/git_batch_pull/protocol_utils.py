from typing import Optional


def detect_protocol_mismatch(repo_path: str, intended_protocol: Optional[str] = None) -> str:
    """
    Detect if the remote URL protocol (SSH/HTTPS) mismatches the user's intended protocol.

    Args:
        repo_path: Path to the local git repository.
        intended_protocol: 'ssh', 'https', or None (just report protocol).
    Returns:
        str: Warning string if a mismatch is detected, otherwise an empty string.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()
    except Exception:
        return ""

    remote_url_lower = remote_url.lower()
    is_ssh = remote_url_lower.startswith("git@") or remote_url_lower.startswith("ssh://")
    is_https = remote_url_lower.startswith("https://")

    if intended_protocol == "ssh":
        if not is_ssh:
            return (
                "[WARNING] This repository is configured to use {} ({}). "
                "If you attempt to use SSH, authentication will fail. "
                "Use 'git remote set-url origin <ssh-url>' to switch to SSH if needed."
            ).format("HTTPS", remote_url)
        return ""
    elif intended_protocol == "https":
        if not is_https:
            return (
                "[WARNING] This repository is configured to use {} ({}). "
                "If you attempt to use HTTPS, authentication will fail. "
                "Use 'git remote set-url origin <https-url>' to switch to HTTPS if needed."
            ).format("SSH", remote_url)
        return ""
    # If no intended protocol, just report protocol
    if is_ssh:
        return (
            "[WARNING] This repository is configured to use SSH ({}). "
            "If you attempt to use HTTPS credentials or tokens, authentication will fail. "
            "Use 'git remote set-url origin <https-url>' to switch to HTTPS if needed."
        ).format(remote_url)
    elif is_https:
        return (
            "[WARNING] This repository is configured to use HTTPS ({}). "
            "If you attempt to use SSH keys, authentication will fail. "
            "Use 'git remote set-url origin <ssh-url>' to switch to SSH if needed."
        ).format(remote_url)
    return ""
