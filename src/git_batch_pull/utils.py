"""Utility functions for git-batch-pull - enhanced version."""

import logging
from pathlib import Path
from typing import List, Optional

from colorama import Fore, Style


def write_error_log(error_log_path: Optional[str], error_log_lines: List[str]) -> None:
    """
    Write detailed error logs to a file if error_log_path is specified.

    Args:
        error_log_path: Path to write error log (None to skip)
        error_log_lines: List of error log lines to write
    """
    if not error_log_path or not error_log_lines:
        return

    try:
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.writelines(error_log_lines)
        print(f"{Fore.YELLOW}Detailed error log written to {error_log_path}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"Failed to write error log to {error_log_path}: {e}")


def print_summary(processed: int, failed: int, quiet: bool = False) -> None:
    """
    Print a summary of processed and failed repositories.

    Args:
        processed: Number of successfully processed repositories
        failed: Number of failed repositories
        quiet: Whether to suppress output
    """
    if quiet:
        return

    total = processed + failed
    if total == 0:
        print(f"{Fore.YELLOW}No repositories were processed{Style.RESET_ALL}")
        return

    success_rate = (processed / total) * 100 if total > 0 else 0

    print(f"\n{Fore.GREEN}Summary: {processed} processed, {failed} failed{Style.RESET_ALL}")

    if failed > 0:
        print(f"{Fore.YELLOW}Success rate: {success_rate:.1f}%{Style.RESET_ALL}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for use in file system.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    sanitized = filename

    for char in unsafe_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "unnamed"

    return sanitized


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The path (for chaining)

    Raises:
        OSError: If directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise OSError(f"Failed to create directory {path}: {e}")


def format_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_value: float = size_bytes

    while size_value >= 1024 and i < len(size_names) - 1:
        size_value /= 1024.0
        i += 1

    return f"{size_value:.1f} {size_names[i]}"
