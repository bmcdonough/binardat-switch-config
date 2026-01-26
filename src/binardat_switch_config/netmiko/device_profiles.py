"""Device-specific command profiles for different switch vendors."""

from typing import Dict, List

# Device-specific commands for retrieving configurations
DEVICE_COMMANDS: Dict[str, Dict[str, str]] = {
    "cisco_ios": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
    "cisco_xe": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
    "cisco_nxos": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
    "cisco_asa": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
    "arista_eos": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
    "juniper_junos": {
        "running_config": "show configuration",
        "startup_config": "show configuration",
        "version": "show version",
    },
    "hp_procurve": {
        "running_config": "show running-config",
        "startup_config": "show config",
        "version": "show version",
    },
    "generic": {
        "running_config": "show running-config",
        "startup_config": "show startup-config",
        "version": "show version",
    },
}


def get_commands(device_type: str) -> Dict[str, str]:
    """Get command set for a device type.

    Args:
        device_type: Netmiko device type string

    Returns:
        Dictionary of command names to command strings

    Example:
        >>> commands = get_commands("cisco_ios")
        >>> print(commands["running_config"])
        show running-config
    """
    return DEVICE_COMMANDS.get(device_type, DEVICE_COMMANDS["generic"])


def get_running_config_command(device_type: str) -> str:
    """Get the command to retrieve running configuration.

    Args:
        device_type: Netmiko device type string

    Returns:
        Command string for retrieving running config
    """
    commands = get_commands(device_type)
    return commands["running_config"]


def get_startup_config_command(device_type: str) -> str:
    """Get the command to retrieve startup configuration.

    Args:
        device_type: Netmiko device type string

    Returns:
        Command string for retrieving startup config
    """
    commands = get_commands(device_type)
    return commands["startup_config"]


def get_version_command(device_type: str) -> str:
    """Get the command to retrieve version information.

    Args:
        device_type: Netmiko device type string

    Returns:
        Command string for retrieving version info
    """
    commands = get_commands(device_type)
    return commands["version"]
