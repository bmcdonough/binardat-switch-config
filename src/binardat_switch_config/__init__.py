"""Binardat Switch Configuration Tool.

A Python library for configuring Binardat brand network switches from
default settings to custom configurations.
"""

from binardat_switch_config.exceptions import (
    AuthenticationError,
    BinardatSwitchError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
)

__version__ = "2026.01.25"
__author__ = "bmcdonough"
__all__ = [
    "__version__",
    "BinardatSwitchError",
    "ConnectionError",
    "ConfigurationError",
    "TimeoutError",
    "AuthenticationError",
]
