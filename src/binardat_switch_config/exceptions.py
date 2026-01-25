"""Custom exceptions for binardat-switch-config.

This module defines all custom exceptions used throughout the package.
"""


class BinardatSwitchError(Exception):
    """Base exception for all binardat-switch-config errors."""

    pass


class ConnectionError(BinardatSwitchError):
    """Raised when connection to switch fails."""

    pass


class ConfigurationError(BinardatSwitchError):
    """Raised when configuration is invalid or cannot be applied."""

    pass


class TimeoutError(BinardatSwitchError):
    """Raised when an operation times out."""

    pass


class AuthenticationError(BinardatSwitchError):
    """Raised when authentication fails."""

    pass
