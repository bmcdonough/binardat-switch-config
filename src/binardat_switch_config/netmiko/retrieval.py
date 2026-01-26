"""Configuration retrieval and normalization for network switches."""

import logging
import re
from typing import Dict, Optional

from ..exceptions import ConfigRetrievalError
from .connection import SwitchConnection
from .device_profiles import (
    get_running_config_command,
    get_startup_config_command,
    get_version_command,
)

logger = logging.getLogger(__name__)


class ConfigRetriever:
    """Retrieves configurations from network switches.

    Example:
        >>> with SwitchConnection(...) as conn:
        ...     retriever = ConfigRetriever(conn)
        ...     config = retriever.retrieve_running_config()
    """

    def __init__(self, connection: SwitchConnection) -> None:
        """Initialize config retriever.

        Args:
            connection: Active SwitchConnection instance
        """
        self.connection = connection

    def retrieve_running_config(self) -> str:
        """Retrieve running configuration from switch.

        Returns:
            Running configuration as string

        Raises:
            ConfigRetrievalError: If retrieval fails
        """
        try:
            command = get_running_config_command(self.connection.device_type)
            logger.info(f"Retrieving running config from {self.connection.host}")
            config = self.connection.send_command(command)

            if not config or len(config.strip()) == 0:
                raise ConfigRetrievalError(
                    f"Empty running config retrieved from {self.connection.host}"
                )

            logger.debug(f"Retrieved {len(config)} bytes of running config")
            return config

        except ConfigRetrievalError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve running config from {self.connection.host}: {e}")
            raise ConfigRetrievalError(
                f"Failed to retrieve running config from {self.connection.host}: {e}"
            )

    def retrieve_startup_config(self) -> Optional[str]:
        """Retrieve startup configuration from switch.

        Returns:
            Startup configuration as string, or None if not available

        Raises:
            ConfigRetrievalError: If retrieval fails (but not if startup config doesn't exist)
        """
        try:
            command = get_startup_config_command(self.connection.device_type)
            logger.info(f"Retrieving startup config from {self.connection.host}")
            config = self.connection.send_command(command)

            # Some devices may not have a startup config
            if not config or "not found" in config.lower() or "does not exist" in config.lower():
                logger.info(f"No startup config found on {self.connection.host}")
                return None

            logger.debug(f"Retrieved {len(config)} bytes of startup config")
            return config

        except Exception as e:
            logger.warning(f"Could not retrieve startup config from {self.connection.host}: {e}")
            return None

    def retrieve_version_info(self) -> str:
        """Retrieve version information from switch.

        Returns:
            Version information as string

        Raises:
            ConfigRetrievalError: If retrieval fails
        """
        try:
            command = get_version_command(self.connection.device_type)
            logger.info(f"Retrieving version info from {self.connection.host}")
            version = self.connection.send_command(command)

            if not version:
                raise ConfigRetrievalError(
                    f"Empty version info retrieved from {self.connection.host}"
                )

            return version

        except ConfigRetrievalError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve version info from {self.connection.host}: {e}")
            raise ConfigRetrievalError(
                f"Failed to retrieve version info from {self.connection.host}: {e}"
            )

    def retrieve_full_backup(self) -> Dict[str, str]:
        """Retrieve all available configurations and info.

        Returns:
            Dictionary containing 'running', 'startup' (if available), and 'version'

        Raises:
            ConfigRetrievalError: If critical retrieval fails
        """
        backup: Dict[str, str] = {}

        # Running config is required
        backup["running"] = self.retrieve_running_config()

        # Startup config is optional
        startup = self.retrieve_startup_config()
        if startup:
            backup["startup"] = startup

        # Version info
        try:
            backup["version"] = self.retrieve_version_info()
        except ConfigRetrievalError:
            logger.warning("Could not retrieve version info, continuing without it")

        return backup


class ConfigNormalizer:
    """Normalizes configurations for change detection.

    Removes dynamic content like timestamps, uptime counters, and session IDs
    that change frequently but don't represent actual configuration changes.
    """

    # Patterns to remove from configs (device-agnostic)
    TIMESTAMP_PATTERNS = [
        r"^! Last configuration change at.*$",
        r"^! NVRAM config last updated at.*$",
        r"^! Configuration last modified by.*$",
        r"^!Time:.*$",
        r"^! Last Modified:.*$",
        r"^! Written:.*$",
        r"^! Generated.*$",
        r"^! Created:.*$",
    ]

    UPTIME_PATTERNS = [
        r"^.*uptime is.*$",
        r"^.*System uptime:.*$",
    ]

    DYNAMIC_PATTERNS = [
        r"^ntp clock-period \d+$",  # NTP clock period changes
        r"^! PID:.*$",  # Process IDs
        r"^! SN:.*$",  # Serial numbers in some contexts
    ]

    def normalize(self, config: str, device_type: str) -> str:
        """Normalize configuration for change detection.

        Args:
            config: Raw configuration string
            device_type: Netmiko device type (for device-specific normalization)

        Returns:
            Normalized configuration string
        """
        normalized = config

        # Apply generic normalization
        normalized = self.remove_timestamps(normalized)
        normalized = self.remove_dynamic_content(normalized)

        # Apply device-specific normalization
        if "cisco" in device_type.lower():
            normalized = self._normalize_cisco(normalized)
        elif "juniper" in device_type.lower():
            normalized = self._normalize_juniper(normalized)

        # Clean up extra blank lines
        normalized = self._clean_blank_lines(normalized)

        return normalized

    def remove_timestamps(self, config: str) -> str:
        """Remove timestamp lines from configuration.

        Args:
            config: Configuration string

        Returns:
            Configuration with timestamps removed
        """
        lines = config.splitlines()
        filtered_lines = []

        for line in lines:
            # Check if line matches any timestamp pattern
            is_timestamp = False
            for pattern in self.TIMESTAMP_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    is_timestamp = True
                    break

            if not is_timestamp:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def remove_dynamic_content(self, config: str) -> str:
        """Remove dynamic content that changes frequently.

        Args:
            config: Configuration string

        Returns:
            Configuration with dynamic content removed
        """
        lines = config.splitlines()
        filtered_lines = []

        all_patterns = self.UPTIME_PATTERNS + self.DYNAMIC_PATTERNS

        for line in lines:
            # Check if line matches any dynamic pattern
            is_dynamic = False
            for pattern in all_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_dynamic = True
                    break

            if not is_dynamic:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _normalize_cisco(self, config: str) -> str:
        """Apply Cisco-specific normalization.

        Args:
            config: Configuration string

        Returns:
            Normalized configuration
        """
        lines = config.splitlines()
        filtered_lines = []

        for line in lines:
            # Skip Cisco-specific dynamic lines
            if re.match(r"^Building configuration.*$", line):
                continue
            if re.match(r"^Current configuration :.*bytes$", line):
                continue

            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _normalize_juniper(self, config: str) -> str:
        """Apply Juniper-specific normalization.

        Args:
            config: Configuration string

        Returns:
            Normalized configuration
        """
        lines = config.splitlines()
        filtered_lines = []

        for line in lines:
            # Skip Juniper-specific dynamic lines
            if re.match(r"^## Last commit:.*$", line):
                continue

            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _clean_blank_lines(self, config: str) -> str:
        """Remove excessive blank lines.

        Reduces multiple consecutive blank lines to a single blank line.

        Args:
            config: Configuration string

        Returns:
            Configuration with cleaned blank lines
        """
        # Replace multiple consecutive blank lines with a single blank line
        cleaned = re.sub(r"\n\n+", "\n\n", config)

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned
