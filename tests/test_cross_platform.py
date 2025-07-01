"""
Unit tests for cross-platform path handling in git-batch-pull.
Ensures correct path string formatting on Windows and Unix-like systems.
"""

import platform
from pathlib import Path


def test_cross_platform_paths():
    """
    Test that path string formatting is correct for the current platform.
    """
    if platform.system() == "Windows":
        p = Path("C:\\Users\\test\\repo")
        assert str(p).startswith("C:\\")
    else:
        p = Path("/tmp/repo")
        assert str(p).startswith("/tmp")
