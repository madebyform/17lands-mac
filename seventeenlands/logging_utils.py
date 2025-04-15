"""
Logging utilities for the 17Lands log parser.

This module provides a centralized logging configuration with:
- File logging with daily rotation
- Colored console output
- Consistent formatting across the application
"""

import logging
import logging.handlers
import os
from typing import Dict, Optional


# Configure log storage location in user's home directory
_LOG_FOLDER = os.path.join(os.path.expanduser("~"), ".seventeenlands")
if not os.path.exists(_LOG_FOLDER):
    os.makedirs(_LOG_FOLDER)
_LOG_FILENAME = os.path.join(_LOG_FOLDER, "seventeenlands.log")

# Define standard log format for file logging
_LOG_FORMATTER = logging.Formatter(
    "%(asctime)s.%(msecs)03d,%(levelname)s,%(name)s,%(message)s",
    datefmt="%Y%m%d %H%M%S",
)

# ANSI color codes for terminal output
_COLORS = {
    "RESET": "\033[0m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BOLD": "\033[1m",
}

# Allow disabling colors via environment variable
_USE_COLORS = os.environ.get("SEVENTEENLANDS_COLOR_LOGS", "true").lower() != "false"


class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to console logs based on log level."""

    LEVEL_COLORS = {
        logging.DEBUG: _COLORS["BLUE"],
        logging.INFO: _COLORS["GREEN"],
        logging.WARNING: _COLORS["YELLOW"],
        logging.ERROR: _COLORS["RED"],
        logging.CRITICAL: _COLORS["BOLD"] + _COLORS["RED"],
    }

    def format(self, record):
        """Format log record with appropriate colors for level and logger name."""
        levelno = getattr(record, "levelno", logging.INFO)

        # Add color if enabled
        if _USE_COLORS and levelno in self.LEVEL_COLORS:
            color = self.LEVEL_COLORS[levelno]
            record.levelname = f"{color}{record.levelname}{_COLORS['RESET']}"
            record.name = f"{_COLORS['CYAN']}{record.name}{_COLORS['RESET']}"

        return super().format(record)


# Define formatters
_CONSOLE_FORMATTER = ColoredFormatter("%(levelname)s [%(name)s] %(message)s")

# Set up file handler with daily rotation and 7-day retention
_file_handler = logging.handlers.TimedRotatingFileHandler(
    _LOG_FILENAME,
    when="D",
    interval=1,
    backupCount=7,
    utc=True,
)
_file_handler.setFormatter(_LOG_FORMATTER)

# Set up console handler with colored output
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_CONSOLE_FORMATTER)

# Combined handlers for both file and console output
_HANDLERS = [_file_handler, _console_handler]

# Cache for created loggers to avoid duplicate initialization
_loggers: Dict[str, logging.Logger] = {}
_log_location_logged = False


def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: Logger name
        log_level: Optional log level (uses INFO if not specified)

    Returns:
        Configured logger instance
    """
    global _log_location_logged

    # Return cached logger if already created
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    # Clear any existing handlers
    logger.handlers = []

    # Add both file and console handlers
    for handler in _HANDLERS:
        logger.addHandler(handler)

    logger.setLevel(log_level if log_level is not None else logging.INFO)
    logger.propagate = False  # Prevent duplicate logs

    # Log file location only once during application lifetime
    if not _log_location_logged:
        logger.info(f"Saving logs to {_LOG_FILENAME}")
        _log_location_logged = True

    # Cache the logger for future use
    _loggers[name] = logger

    return logger
