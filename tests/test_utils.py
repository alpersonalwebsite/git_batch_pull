"""Tests for utility functions."""

from git_batch_pull.utils import format_size, sanitize_filename


def test_format_size():
    """Test file size formatting."""
    assert format_size(0) == "0 B"
    assert format_size(512) == "512.0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1536) == "1.5 KB"
    assert format_size(1048576) == "1.0 MB"
    assert format_size(1073741824) == "1.0 GB"


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("normal_file.txt") == "normal_file.txt"
    assert sanitize_filename("file/with\\slashes") == "file_with_slashes"
    assert sanitize_filename("file:with*forbidden?chars") == "file_with_forbidden_chars"
    assert sanitize_filename("file<with>pipe|chars") == "file_with_pipe_chars"
    assert sanitize_filename('file"with"quotes') == "file_with_quotes"


def test_sanitize_filename_empty():
    """Test sanitizing empty filename."""
    assert sanitize_filename("") == "unnamed"
    assert sanitize_filename("   ") == "unnamed"


def test_sanitize_filename_dots_only():
    """Test sanitizing filename with only dots."""
    assert sanitize_filename("...") == "unnamed"
    assert sanitize_filename(".") == "unnamed"
    assert sanitize_filename("..") == "unnamed"
