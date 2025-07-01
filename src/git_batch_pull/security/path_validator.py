"""Path validation utilities for security."""

from pathlib import Path
from typing import Union

from ..exceptions import PathValidationError, SecurityError


class PathValidator:
    """Validates paths to prevent security issues like path traversal."""

    @staticmethod
    def validate_safe_path(path: Union[str, Path], base_path: Union[str, Path]) -> Path:
        """
        Validate that a path is safe and within the expected base directory.

        Args:
            path: Path to validate
            base_path: Base directory that path should be within

        Returns:
            Resolved safe path

        Raises:
            PathValidationError: If path is unsafe
        """
        path_obj = Path(path).resolve()
        base_obj = Path(base_path).resolve()

        try:
            # Check if path is within base directory
            path_obj.relative_to(base_obj)
        except ValueError:
            raise PathValidationError(
                f"Path '{path}' is outside of allowed base directory '{base_path}'"
            )

        return path_obj

    @staticmethod
    def validate_absolute_path(path: Union[str, Path]) -> Path:
        """
        Validate that a path is absolute.

        Args:
            path: Path to validate

        Returns:
            Path object

        Raises:
            PathValidationError: If path is not absolute
        """
        path_obj = Path(path)

        if not path_obj.is_absolute():
            raise PathValidationError(f"Path must be absolute: {path}")

        return path_obj

    @staticmethod
    def ensure_directory_exists(path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if necessary.

        Args:
            path: Directory path

        Returns:
            Path object

        Raises:
            SecurityError: If directory cannot be created safely
        """
        path_obj = Path(path)

        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise SecurityError(f"Permission denied creating directory: {path}")
        except OSError as e:
            raise SecurityError(f"Failed to create directory '{path}': {e}")

        return path_obj

    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate filename for security (no path traversal, reserved names, etc.).

        Args:
            filename: Filename to validate

        Returns:
            Validated filename

        Raises:
            PathValidationError: If filename is unsafe
        """
        if not filename or filename.strip() == "":
            raise PathValidationError("Filename cannot be empty")

        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            raise PathValidationError(f"Filename contains invalid characters: {filename}")

        # Check for reserved names on Windows
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        if filename.upper() in reserved_names:
            raise PathValidationError(f"Filename is a reserved name: {filename}")

        return filename
