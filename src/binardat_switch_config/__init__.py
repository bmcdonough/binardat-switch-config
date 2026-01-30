"""Binardat switch configuration library.

A Python library for configuring Binardat brand network switches.
"""

from pathlib import Path


def _get_version() -> str:
    """Read version from VERSION file.

    Returns:
        Version string in CalVer format (YYYY.MM.DD[.MICRO]).
    """
    version_file = Path(__file__).parent.parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"  # Fallback if VERSION file missing


__version__ = _get_version()

# Export main classes/functions for convenient imports
from .ssh_enabler import (  # noqa: E402
    SSHEnabler,
    load_config_from_env,
    verify_ssh_port,
)

__all__ = [
    "__version__",
    "SSHEnabler",
    "load_config_from_env",
    "verify_ssh_port",
]
