"""SSH connection management for network switches using netmiko."""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    SSHException,
)

from ..exceptions import NetmikoConnectionError

logger = logging.getLogger(__name__)


class SwitchConnection:
    """Context manager for netmiko SSH connections.

    Supports:
    - Username/password authentication
    - SSH key-based authentication
    - Connection retry logic
    - Automatic cleanup

    Example:
        >>> with SwitchConnection("192.168.1.1", "cisco_ios", "admin", password="secret") as conn:
        ...     config = conn.send_command("show running-config")
    """

    def __init__(
        self,
        host: str,
        device_type: str,
        username: str,
        password: Optional[str] = None,
        key_file: Optional[Path] = None,
        port: int = 22,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        """Initialize switch connection parameters.

        Args:
            host: IP address or hostname of the switch
            device_type: Netmiko device type (e.g., 'cisco_ios', 'cisco_xe')
            username: SSH username
            password: SSH password (optional if using key_file)
            key_file: Path to SSH private key file (optional)
            port: SSH port (default: 22)
            timeout: Connection timeout in seconds (default: 30.0)
            max_retries: Maximum connection attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 2.0)

        Raises:
            ValueError: If neither password nor key_file is provided
        """
        if not password and not key_file:
            raise ValueError("Either password or key_file must be provided")

        self.host = host
        self.device_type = device_type
        self.username = username
        self.password = password
        self.key_file = Path(key_file) if key_file else None
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._connection: Optional[Any] = None
        self._is_connected = False

    def connect(self) -> None:
        """Establish SSH connection to the switch.

        Attempts connection with exponential backoff retry logic.

        Raises:
            NetmikoConnectionError: If connection fails after all retry attempts
        """
        device_params: Dict[str, Any] = {
            "device_type": self.device_type,
            "host": self.host,
            "username": self.username,
            "port": self.port,
            "timeout": self.timeout,
        }

        if self.password:
            device_params["password"] = self.password
        if self.key_file:
            device_params["use_keys"] = True
            device_params["key_file"] = str(self.key_file)

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Connecting to {self.host} (attempt {attempt}/{self.max_retries})..."
                )
                self._connection = ConnectHandler(**device_params)
                self._is_connected = True
                logger.info(f"Successfully connected to {self.host}")
                return

            except NetmikoAuthenticationException as e:
                last_error = e
                logger.error(f"Authentication failed for {self.host}: {e}")
                # Don't retry authentication failures
                break

            except NetmikoTimeoutException as e:
                last_error = e
                logger.warning(f"Connection timeout to {self.host} (attempt {attempt}): {e}")

            except SSHException as e:
                last_error = e
                logger.warning(f"SSH error connecting to {self.host} (attempt {attempt}): {e}")

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error connecting to {self.host}: {e}")
                break

            # Exponential backoff before retry
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.debug(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)

        # All attempts failed
        error_msg = f"Failed to connect to {self.host} after {self.max_retries} attempts"
        if last_error:
            error_msg += f": {last_error}"
        raise NetmikoConnectionError(error_msg)

    def disconnect(self) -> None:
        """Close SSH connection to the switch."""
        if self._connection and self._is_connected:
            try:
                self._connection.disconnect()
                logger.debug(f"Disconnected from {self.host}")
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.host}: {e}")
            finally:
                self._is_connected = False
                self._connection = None

    def send_command(self, command: str, **kwargs: Any) -> str:
        """Send a single command to the switch.

        Args:
            command: Command to execute
            **kwargs: Additional arguments passed to netmiko send_command

        Returns:
            Command output as string

        Raises:
            NetmikoConnectionError: If not connected or command fails
        """
        if not self._is_connected or not self._connection:
            raise NetmikoConnectionError(f"Not connected to {self.host}")

        try:
            logger.debug(f"Sending command to {self.host}: {command}")
            output = self._connection.send_command(command, **kwargs)
            return output
        except Exception as e:
            logger.error(f"Error sending command to {self.host}: {e}")
            raise NetmikoConnectionError(f"Command failed on {self.host}: {e}")

    def send_config_commands(self, commands: List[str], **kwargs: Any) -> str:
        """Send configuration commands to the switch.

        Args:
            commands: List of configuration commands
            **kwargs: Additional arguments passed to netmiko send_config_set

        Returns:
            Configuration output as string

        Raises:
            NetmikoConnectionError: If not connected or commands fail
        """
        if not self._is_connected or not self._connection:
            raise NetmikoConnectionError(f"Not connected to {self.host}")

        try:
            logger.info(f"Sending {len(commands)} config commands to {self.host}")
            logger.debug(f"Commands: {commands[:5]}...")  # Log first 5 commands
            output = self._connection.send_config_set(commands, **kwargs)
            return output
        except Exception as e:
            logger.error(f"Error sending config commands to {self.host}: {e}")
            raise NetmikoConnectionError(f"Config commands failed on {self.host}: {e}")

    def is_alive(self) -> bool:
        """Check if connection is still alive.

        Returns:
            True if connected and alive, False otherwise
        """
        if not self._is_connected or not self._connection:
            return False

        try:
            return self._connection.is_alive()
        except Exception:
            return False

    def __enter__(self) -> "SwitchConnection":
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close connection."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation of connection."""
        status = "connected" if self._is_connected else "disconnected"
        return f"<SwitchConnection {self.username}@{self.host}:{self.port} ({status})>"
