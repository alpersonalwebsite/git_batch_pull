"""Safe subprocess execution utilities."""

import logging
import subprocess  # nosec
from pathlib import Path
from typing import List, Optional, Union

from ..exceptions import GitOperationError, SecurityError


class SafeSubprocessRunner:
    """Safely executes subprocess commands with proper error handling and timeouts."""

    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.logger = logging.getLogger(__name__)

    def run_git_command(
        self,
        command: List[str],
        cwd: Union[str, Path],
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Safely run a git command with proper error handling.

        Args:
            command: Git command as list of strings
            cwd: Working directory
            timeout: Timeout in seconds (uses default if None)
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit

        Returns:
            CompletedProcess result

        Raises:
            GitOperationError: If command fails
            SecurityError: If command is unsafe
        """
        if not command or not isinstance(command, list):
            raise SecurityError("Command must be a non-empty list")

        # Validate that first command is git
        if command[0] != "git":
            raise SecurityError("Only git commands are allowed")

        # Sanitize command arguments
        safe_command = self._sanitize_command(command)

        timeout_val = timeout or self.default_timeout

        self.logger.debug(f"Running git command: {' '.join(safe_command)}")

        try:
            result = subprocess.run(
                safe_command,
                cwd=str(cwd),
                capture_output=capture_output,
                text=True,
                timeout=timeout_val,
                check=check,
            )

            if result.returncode != 0:
                self.logger.warning(f"Git command failed with code {result.returncode}")
                if result.stderr:
                    self.logger.warning(f"Error output: {result.stderr}")

            return result

        except subprocess.TimeoutExpired:
            raise GitOperationError(
                f"Git command timed out after {timeout_val} seconds", command=" ".join(safe_command)
            )
        except subprocess.CalledProcessError as e:
            raise GitOperationError(
                f"Git command failed with exit code {e.returncode}",
                command=" ".join(safe_command),
                stderr=e.stderr,
            )
        except Exception as e:
            raise GitOperationError(
                f"Unexpected error running git command: {e}", command=" ".join(safe_command)
            )

    def run_safe_command(
        self,
        command: List[str],
        cwd: Union[str, Path],
        allowed_commands: List[str],
        timeout: Optional[int] = None,
    ) -> subprocess.CompletedProcess:
        """
        Run a command from an allowed list with safety checks.

        Args:
            command: Command as list of strings
            cwd: Working directory
            allowed_commands: List of allowed command names
            timeout: Timeout in seconds

        Returns:
            CompletedProcess result

        Raises:
            SecurityError: If command is not allowed
        """
        if not command or command[0] not in allowed_commands:
            raise SecurityError(
                f"Command '{command[0] if command else 'None'}' not in allowed list"
            )

        timeout_val = timeout or self.default_timeout

        try:
            return subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout_val,
                check=True,
            )
        except subprocess.TimeoutExpired:
            raise SecurityError(f"Command timed out after {timeout_val} seconds")
        except subprocess.CalledProcessError as e:
            raise SecurityError(f"Command failed: {e}")

    def _sanitize_command(self, command: List[str]) -> List[str]:
        """
        Sanitize command arguments to prevent injection.

        Args:
            command: Command arguments

        Returns:
            Sanitized command arguments
        """
        sanitized = []

        for arg in command:
            # Basic sanitization - remove dangerous characters
            if isinstance(arg, str):
                # Remove null bytes and control characters
                clean_arg = "".join(char for char in arg if ord(char) >= 32 or char in "\t\n")
                sanitized.append(clean_arg)
            else:
                sanitized.append(str(arg))

        return sanitized
