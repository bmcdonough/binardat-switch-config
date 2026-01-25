"""Main CLI tool for changing Binardat switch IP addresses.

This script provides an end-to-end solution for changing switch IP
addresses, including connection to the old IP, authentication,
configuration change, and verification on the new IP.
"""

import argparse
import re
import sys
import time
from getpass import getpass
from typing import Optional

from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


class IPChangeError(Exception):
    """Exception raised for IP change operation errors."""

    pass


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

    octets = ip.split(".")
    for octet in octets:
        if int(octet) > 255:
            return False

    return True


def validate_subnet_mask(mask: str) -> bool:
    """Validate subnet mask format.

    Args:
        mask: Subnet mask string.

    Returns:
        True if valid subnet mask, False otherwise.
    """
    if not validate_ip(mask):
        return False

    # Convert to binary and check it's a valid mask
    # (all 1s followed by all 0s)
    octets = mask.split(".")
    binary = "".join(format(int(octet), "08b") for octet in octets)

    # Check pattern: 1+ followed by 0*
    if not re.match(r"^1*0*$", binary):
        return False

    # At least some 1s
    if "1" not in binary:
        return False

    return True


def test_connectivity(host: str, timeout: float = 5.0) -> bool:
    """Test if switch is reachable.

    Args:
        host: Switch IP address or hostname.
        timeout: Connection timeout. Defaults to 5.0.

    Returns:
        True if reachable, False otherwise.
    """
    import socket

    try:
        socket.create_connection((host, 80), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


def connect_and_change_ip(
    old_ip: str,
    username: str,
    password: str,
    new_ip: str,
    subnet_mask: str,
    gateway: Optional[str] = None,
    timeout: float = 30.0,
    verbose: bool = False,
) -> bool:
    """Connect to switch and change IP address.

    Args:
        old_ip: Current switch IP address.
        username: Switch username.
        password: Switch password.
        new_ip: New IP address.
        subnet_mask: Subnet mask.
        gateway: Default gateway (optional).
        timeout: Request timeout. Defaults to 30.0.
        verbose: Enable verbose output. Defaults to False.

    Returns:
        True if successful, False otherwise.

    Raises:
        IPChangeError: If operation fails.
    """
    if verbose:
        print("\n[STEP 1] Connecting to switch at old IP...")
        print(f"          Old IP: {old_ip}")

    # Test connectivity
    if not test_connectivity(old_ip, timeout=5.0):
        raise IPChangeError(f"Switch not reachable at {old_ip}")

    if verbose:
        print("          Switch is reachable")

    # Create session
    session = SwitchSession(old_ip, timeout)

    try:
        # Authenticate
        if verbose:
            print("\n[STEP 2] Authenticating...")
        session.login(username, password)
        if verbose:
            print("          Authentication successful")

        # Read current configuration
        if verbose:
            print("\n[STEP 3] Reading current configuration...")
        current_config = session.get_current_ip_config()
        if verbose:
            print("          Current configuration:")
            for key, value in current_config.items():
                print(f"            {key:15s}: {value}")

        # Display new configuration
        if verbose:
            print("\n[STEP 4] Preparing new configuration...")
            print(f"          New IP      : {new_ip}")
            print(f"          Subnet Mask : {subnet_mask}")
            print(f"          Gateway     : {gateway or '(unchanged)'}")

        # Submit configuration change
        if verbose:
            print("\n[STEP 5] Submitting configuration change...")
        session.change_ip_address(new_ip, subnet_mask, gateway)

        if verbose:
            print("          Configuration submitted")
            print(
                "          Note: Switch may disconnect "
                "while applying changes"
            )

        return True

    except SwitchAuthError as e:
        raise IPChangeError(f"Authentication failed: {e}") from e

    except SwitchConnectionError:
        # Connection loss during IP change is expected
        if verbose:
            print("          Connection lost (expected during IP change)")
        return True

    finally:
        session.close()


def verify_new_ip(
    new_ip: str,
    username: str,
    password: str,
    timeout: float = 30.0,
    wait_time: float = 60.0,
    verbose: bool = False,
) -> bool:
    """Verify switch is accessible at new IP.

    Args:
        new_ip: New IP address to verify.
        username: Switch username.
        password: Switch password.
        timeout: Request timeout. Defaults to 30.0.
        wait_time: Time to wait before verification. Defaults to 60.0.
        verbose: Enable verbose output. Defaults to False.

    Returns:
        True if verification successful, False otherwise.
    """
    if verbose:
        print(
            f"\n[VERIFICATION] Waiting {wait_time}s for switch to "
            "apply changes..."
        )

    # Wait for switch to apply changes
    for i in range(int(wait_time)):
        if verbose and (i + 1) % 10 == 0:
            print(f"               {i + 1}/{int(wait_time)}s elapsed...")
        time.sleep(1)

    if verbose:
        print("\n[VERIFICATION] Testing connectivity to new IP...")
        print(f"               New IP: {new_ip}")

    # Test connectivity
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        if verbose:
            print(f"               Attempt {attempt}/{max_attempts}...")

        if test_connectivity(new_ip, timeout=5.0):
            if verbose:
                print("               Switch is reachable!")
            break

        if attempt < max_attempts:
            time.sleep(5)
    else:
        if verbose:
            print("               WARNING: Switch not reachable")
        return False

    # Try to authenticate
    if verbose:
        print("\n[VERIFICATION] Attempting authentication...")

    session = SwitchSession(new_ip, timeout)

    try:
        session.login(username, password)
        if verbose:
            print("               Authentication successful!")

        # Read configuration to confirm
        config = session.get_current_ip_config()
        if verbose:
            print("\n[VERIFICATION] Current configuration:")
            for key, value in config.items():
                print(f"               {key:15s}: {value}")

        # Verify IP matches
        current_ip = config.get("ip_address", "")
        if current_ip == new_ip:
            if verbose:
                print(f"\n[VERIFICATION] IP address confirmed: {new_ip}")
            return True
        else:
            if verbose:
                print(
                    f"\n[VERIFICATION] WARNING: IP mismatch! "
                    f"Expected {new_ip}, got {current_ip}"
                )
            return False

    except (SwitchAuthError, SwitchConnectionError) as e:
        if verbose:
            print(f"               Verification failed: {e}")
        return False

    finally:
        session.close()


def main() -> int:
    """Run IP address change operation.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Change IP address on Binardat switch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Change IP with verification
  python change_ip_address.py \\
    --old-ip 192.168.2.1 \\
    --new-ip 192.168.1.100 \\
    --subnet 255.255.255.0 \\
    --gateway 192.168.1.1 \\
    --username admin \\
    --password admin \\
    --verify

  # Dry run to test without changing
  python change_ip_address.py \\
    --old-ip 192.168.2.1 \\
    --new-ip 192.168.1.100 \\
    --subnet 255.255.255.0 \\
    --username admin \\
    --dry-run

  # Quiet mode (minimal output)
  python change_ip_address.py \\
    --old-ip 192.168.2.1 \\
    --new-ip 192.168.1.100 \\
    --subnet 255.255.255.0 \\
    --username admin \\
    --quiet
        """,
    )

    # Connection parameters
    parser.add_argument(
        "--old-ip",
        required=True,
        help="Current switch IP address",
    )
    parser.add_argument(
        "--new-ip",
        required=True,
        help="New IP address to set",
    )
    parser.add_argument(
        "--subnet",
        required=True,
        help="Subnet mask (e.g., 255.255.255.0)",
    )
    parser.add_argument(
        "--gateway",
        help="Default gateway (optional)",
    )

    # Authentication
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

    # Options
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify switch is accessible at new IP after change",
    )
    parser.add_argument(
        "--wait-time",
        type=float,
        default=60.0,
        help="Time to wait before verification (default: 60.0s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without actually changing IP",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output (errors only)",
    )

    args = parser.parse_args()

    # Adjust verbosity
    verbose = args.verbose and not args.quiet

    # Print header
    if not args.quiet:
        print("=" * 70)
        print("BINARDAT SWITCH IP ADDRESS CHANGE TOOL")
        print("=" * 70)
        if args.dry_run:
            print("MODE: DRY RUN (no changes will be made)")
            print("=" * 70)

    # Validate IP addresses
    if not validate_ip(args.old_ip):
        print(f"Error: Invalid old IP address: {args.old_ip}")
        return 1

    if not validate_ip(args.new_ip):
        print(f"Error: Invalid new IP address: {args.new_ip}")
        return 1

    if not validate_subnet_mask(args.subnet):
        print(f"Error: Invalid subnet mask: {args.subnet}")
        return 1

    if args.gateway and not validate_ip(args.gateway):
        print(f"Error: Invalid gateway: {args.gateway}")
        return 1

    # Get credentials
    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    if args.dry_run:
        if not args.quiet:
            print("\nDRY RUN MODE - Configuration:")
            print(f"  Old IP      : {args.old_ip}")
            print(f"  New IP      : {args.new_ip}")
            print(f"  Subnet Mask : {args.subnet}")
            print(f"  Gateway     : {args.gateway or '(not set)'}")
            print("\nNo changes will be made.")
        return 0

    # Perform IP change
    try:
        success = connect_and_change_ip(
            args.old_ip,
            username,
            password,
            args.new_ip,
            args.subnet,
            args.gateway,
            args.timeout,
            verbose,
        )

        if not success:
            if not args.quiet:
                print("\nIP change failed.")
            return 1

        if not args.quiet:
            print("\nIP change submitted successfully!")

        # Verify if requested
        if args.verify:
            verified = verify_new_ip(
                args.new_ip,
                username,
                password,
                args.timeout,
                args.wait_time,
                verbose,
            )

            if verified:
                if not args.quiet:
                    print("\n" + "=" * 70)
                    print("RESULT: IP CHANGE VERIFIED - SUCCESS")
                    print("=" * 70)
                return 0
            else:
                if not args.quiet:
                    print("\n" + "=" * 70)
                    print("RESULT: VERIFICATION FAILED")
                    print("=" * 70)
                    print(
                        "\nThe IP change was submitted, "
                        "but verification failed."
                    )
                    print("Please check the switch manually.")
                return 1
        else:
            if not args.quiet:
                print("\n" + "=" * 70)
                print("RESULT: IP CHANGE SUBMITTED")
                print("=" * 70)
                print(
                    f"\nThe switch should now be accessible at: {args.new_ip}"
                )
                print("Wait 30-60 seconds before attempting to connect.")
            return 0

    except IPChangeError as e:
        print(f"\nError: {e}")
        return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
