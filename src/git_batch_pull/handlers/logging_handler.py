"""Enhanced logging configuration and management."""

import logging
import sys
from typing import Optional

from colorama import Fore, Style
from colorama import init as colorama_init


class LoggingHandler:
    """
    Manages logging configuration with color support and file output.
    """

    def __init__(self):
        self.color_enabled = True
        self.formatters = {}
        self._setup_formatters()

    def setup_logging(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        quiet: bool = False,
        plain: bool = False,
    ) -> None:
        """
        Configure logging with the specified parameters.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional file path for log output
            quiet: Whether to suppress console output
            plain: Whether to disable colored output
        """
        # Configure colorama
        self._setup_colors(plain)

        # Create handlers
        handlers = []

        if not quiet:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                self.formatters["color"] if self.color_enabled else self.formatters["plain"]
            )
            handlers.append(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(self.formatters["file"])
            handlers.append(file_handler)

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            handlers=handlers,
            force=True,  # Override any existing configuration
        )

        # Set up specific logger levels
        self._configure_library_loggers()

    def _setup_colors(self, plain: bool) -> None:
        """Setup color support."""
        if plain:
            self.color_enabled = False
            # Disable colorama
            from colorama import deinit as colorama_deinit

            colorama_deinit()
        else:
            self.color_enabled = True
            colorama_init(autoreset=True)

    def _setup_formatters(self) -> None:
        """Setup different formatters for various output types."""
        # Basic formatter for plain text
        plain_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        self.formatters["plain"] = logging.Formatter(plain_format)

        # File formatter with more details
        file_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        self.formatters["file"] = logging.Formatter(file_format)

        # Color formatter for console
        self.formatters["color"] = ColoredFormatter()

    def _configure_library_loggers(self) -> None:
        """Configure logging levels for third-party libraries."""
        # Reduce noise from libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("git").setLevel(logging.WARNING)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.

        Args:
            name: Logger name

        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages based on level.
    """

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def __init__(self):
        super().__init__()
        self.base_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get the color for this log level
        color = self.COLORS.get(record.levelno, "")

        # Create a temporary formatter with color
        if color:
            colored_format = f"{color}{self.base_format}{Style.RESET_ALL}"
        else:
            colored_format = self.base_format

        formatter = logging.Formatter(colored_format)
        return formatter.format(record)


# Global logging handler instance
logging_handler = LoggingHandler()
