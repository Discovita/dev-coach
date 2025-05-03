"""
Logger module with custom log levels and formatting.

This module provides colored console output with automatic context information,
optional file logging, and custom log levels (FINE, SUCCESS, STEP) in addition 
to standard Python logging levels.
"""

from .logger import (
    configure_logging,
    FINE_LEVEL,
    STEP_LEVEL,
    SUCCESS_LEVEL,
    CONTEXT_DISPLAY,
    ConsoleFormatter,
    LogFileFormatter,
)

__all__ = [
    "configure_logging",
    "FINE_LEVEL",
    "STEP_LEVEL",
    "SUCCESS_LEVEL",
    "CONTEXT_DISPLAY",
    "ConsoleFormatter",
    "LogFileFormatter",
]