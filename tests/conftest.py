"""
Pytest configuration and fixtures for git-batch-pull tests.
Automatically patches time.sleep to speed up tests.
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def patch_sleep():
    """
    Automatically patch time.sleep to a no-op for all tests.
    """
    with patch("time.sleep", return_value=None):
        yield
