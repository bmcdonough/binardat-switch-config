"""Test IP configuration change on Binardat switch.

This script tests the ability to read and change IP configuration
on the switch through the web interface. It uses menu-aware navigation
if menu_structure.json is available from 03_menu_extraction.py.
"""

import argparse
import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional

from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


def find_menu_file() -> Optional[str]:
    """Find menu_structure.json file if it exists.

    Searches in current directory and proof-of-concept directory.

    Returns:
        Path to menu_structure.json if found, None otherwise.
    """
    # Check current directory
    menu_path = Path("menu_structure.json")
    if menu_path.exists():
        return str(menu_path)

    # Check proof-of-concept directory
    poc_menu_path = Path(__file__).parent / "menu_structure.json"
    if poc_menu_path.exists():
        return str(poc_menu_path)

    return None


def validate_ip(ip: str) -> bool:
    """Validate IP address format.

    Args:
        ip: IP address string.

    Returns:
        True if valid IP address, False otherwise.
    """
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False

    # Check each octet is 0-255
    octets = ip.split(".")
    for octet in octets:
        if int(octet) > 255:
            return False

    return True


def test_read_ip_config(
    host: str,
    username: str,
    password: str,
    timeout: float = 30.0,
) -> bool:
    """Test reading current IP configuration.

    Args:
        host: Switch IP address or hostname.
        username: Switch username.
        password: Switch password.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 70)
    print("READ IP CONFIGURATION TEST")
    print("=" * 70)

    # Check for menu structure file
    menu_file = find_menu_file()
    if menu_file:
        print(f"Using menu structure: {menu_file}")
        print("(This enables targeted navigation to IP config page)")
    else:
        print("Menu structure not found - using common URLs")
        print("Run: python 03_menu_extraction.py to discover menu structure")

    session = SwitchSession(host, timeout)

    try:
        # Login
        print("\n[1] Authenticating...")
        session.login(username, password)
        print("    Authentication successful")

        # Read IP configuration
        print("\n[2] Reading current IP configuration...")
        config = session.get_current_ip_config(menu_file)

        if not config:
            print("    No configuration found")
            return False

        print("    Current configuration:")
        for key, value in config.items():
            print(f"      {key:15s}: {value}")

        print("\n" + "=" * 70)
        print("RESULT: READ TEST PASSED")
        print("=" * 70)
        return True

    except SwitchAuthError as e:
        print(f"    Authentication error: {e}")
        return False

    except SwitchConnectionError as e:
        print(f"    Connection error: {e}")
        return False

    except Exception as e:
        print(f"    Unexpected error: {e}")
        return False

    finally:
        session.close()


def test_change_ip(
    host: str,
    username: str,
    password: str,
    new_ip: str,
    subnet_mask: str,
    gateway: Optional[str] = None,
    dry_run: bool = False,
    timeout: float = 30.0,
) -> bool:
    """Test changing IP configuration.

    Args:
        host: Switch IP address or hostname.
        username: Switch username.
        password: Switch password.
        new_ip: New IP address.
        subnet_mask: Subnet mask.
        gateway: Default gateway (optional).
        dry_run: If True, don't actually submit the change.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 70)
    print("CHANGE IP CONFIGURATION TEST")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    # Validate IP addresses
    if not validate_ip(new_ip):
        print(f"Error: Invalid IP address: {new_ip}")
        return False

    if not validate_ip(subnet_mask):
        print(f"Error: Invalid subnet mask: {subnet_mask}")
        return False

    if gateway and not validate_ip(gateway):
        print(f"Error: Invalid gateway: {gateway}")
        return False

    # Check for menu structure file
    menu_file = find_menu_file()
    if menu_file:
        print(f"Using menu structure: {menu_file}")
    else:
        print("Menu structure not found - using common URLs")

    session = SwitchSession(host, timeout)

    try:
        # Login
        print("\n[1] Authenticating...")
        session.login(username, password)
        print("    Authentication successful")

        # Read current configuration
        print("\n[2] Reading current configuration...")
        current_config = session.get_current_ip_config(menu_file)

        print("    Current configuration:")
        for key, value in current_config.items():
            print(f"      {key:15s}: {value}")

        # Display new configuration
        print("\n[3] New configuration:")
        print(f"      IP Address     : {new_ip}")
        print(f"      Subnet Mask    : {subnet_mask}")
        print(f"      Gateway        : {gateway or '(not changed)'}")

        if dry_run:
            print("\n[4] DRY RUN MODE - Not submitting changes")
            print("\n" + "=" * 70)
            print("RESULT: DRY RUN COMPLETED")
            print("=" * 70)
            return True

        # Confirm with user
        print("\n[4] Ready to submit configuration change")
        print("    WARNING: This will change the switch IP address!")
        print(
            "    You will need to reconnect to the new IP " "after the change."
        )

        confirm = input("\n    Proceed? (yes/no): ")
        if confirm.lower() != "yes":
            print("    Change cancelled by user")
            return False

        # Submit change
        print("\n[5] Submitting configuration change...")
        session.change_ip_address(
            new_ip, subnet_mask, gateway, menu_file=menu_file
        )

        print("    Configuration change submitted")
        print(
            "    Note: Switch may reboot or disconnect. " "Wait 30-60 seconds."
        )

        print("\n" + "=" * 70)
        print("RESULT: CHANGE SUBMITTED")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Wait 30-60 seconds for switch to apply changes")
        print(f"  2. Try to access switch at new IP: {new_ip}")
        print(
            f"  3. Run: python 02_test_login.py --host {new_ip} "
            f"--username {username}"
        )

        return True

    except SwitchAuthError as e:
        print(f"    Authentication error: {e}")
        return False

    except SwitchConnectionError as e:
        print(f"    Connection error: {e}")
        print("    Note: Connection loss may be expected if IP changed")
        return False

    except Exception as e:
        print(f"    Unexpected error: {e}")
        return False

    finally:
        session.close()


def main() -> int:
    """Run IP configuration tests.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Test IP configuration changes on Binardat switch"
    )
    parser.add_argument(
        "--host",
        default="192.168.2.1",
        help="Switch IP address (default: 192.168.2.1)",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Switch username (will prompt if not provided)",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Switch password (will prompt if not provided)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--read-only",
        action="store_true",
        help="Only read current IP configuration",
    )
    mode_group.add_argument(
        "--change-ip",
        action="store_true",
        help="Change IP configuration",
    )

    # IP configuration options
    parser.add_argument(
        "--new-ip",
        help="New IP address",
    )
    parser.add_argument(
        "--subnet-mask",
        help="Subnet mask (e.g., 255.255.255.0)",
    )
    parser.add_argument(
        "--gateway",
        help="Default gateway (optional)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without actually submitting changes",
    )

    args = parser.parse_args()

    # Prompt for credentials if not provided
    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    # Read-only mode
    if args.read_only or not args.change_ip:
        success = test_read_ip_config(
            args.host, username, password, args.timeout
        )
        return 0 if success else 1

    # Change IP mode
    if args.change_ip:
        if not args.new_ip:
            print("Error: --new-ip is required for --change-ip mode")
            return 1

        if not args.subnet_mask:
            print("Error: --subnet-mask is required for --change-ip mode")
            return 1

        success = test_change_ip(
            args.host,
            username,
            password,
            args.new_ip,
            args.subnet_mask,
            args.gateway,
            args.dry_run,
            args.timeout,
        )
        return 0 if success else 1

    # Default: read-only mode
    success = test_read_ip_config(args.host, username, password, args.timeout)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
