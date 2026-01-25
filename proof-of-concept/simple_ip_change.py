#!/usr/bin/env python3
"""Simple script to change Binardat switch IP address.

This script provides a straightforward way to:
1. Connect to a switch at its current IP
2. Authenticate and change the IP address
3. Verify the change by pinging and logging in to the new IP
"""

import argparse
import subprocess
import sys
import time

from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


def ping_host(host: str, timeout: int = 5) -> bool:
    """Test if a host is reachable via ping.

    Args:
        host: IP address or hostname to ping.
        timeout: Timeout in seconds. Defaults to 5.

    Returns:
        True if ping successful, False otherwise.
    """
    try:
        # Use -c 1 for one ping, -W for timeout
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def wait_for_ping(host: str, max_attempts: int = 12, interval: int = 5) -> bool:
    """Wait for a host to respond to ping.

    Args:
        host: IP address to ping.
        max_attempts: Maximum number of ping attempts. Defaults to 12.
        interval: Seconds between attempts. Defaults to 5.

    Returns:
        True if host responds, False if max attempts reached.
    """
    print(f"\n[VERIFY] Waiting for {host} to respond to ping...")

    for attempt in range(1, max_attempts + 1):
        print(f"[VERIFY] Ping attempt {attempt}/{max_attempts}...", end=" ")

        if ping_host(host, timeout=2):
            print("SUCCESS!")
            return True

        print("no response")

        if attempt < max_attempts:
            time.sleep(interval)

    return False


def change_switch_ip(
    current_ip: str,
    username: str,
    password: str,
    new_ip: str,
    subnet_mask: str = "255.255.255.0",
    gateway: str = None,
) -> bool:
    """Change switch IP address and verify the change.

    Args:
        current_ip: Current IP address of the switch.
        username: Switch username.
        password: Switch password.
        new_ip: New IP address to set.
        subnet_mask: Subnet mask. Defaults to "255.255.255.0".
        gateway: Default gateway (optional).

    Returns:
        True if successful, False otherwise.
    """
    print("=" * 70)
    print("BINARDAT SWITCH IP CHANGE")
    print("=" * 70)
    print(f"Current IP  : {current_ip}")
    print(f"New IP      : {new_ip}")
    print(f"Subnet Mask : {subnet_mask}")
    print(f"Gateway     : {gateway or '(not set)'}")
    print("=" * 70)

    # Step 1: Connect to current IP
    print(f"\n[STEP 1] Connecting to switch at {current_ip}...")
    session = SwitchSession(current_ip, timeout=30.0)

    try:
        # Step 2: Login
        print(f"[STEP 2] Authenticating as '{username}'...")
        session.login(username, password)
        print("[STEP 2] Authentication successful!")

        # Step 3: Read current config
        print("\n[STEP 3] Reading current configuration...")
        current_config = session.get_current_ip_config()
        print("[STEP 3] Current configuration:")
        for key, value in current_config.items():
            print(f"         {key:15s}: {value}")

        # Step 4: Change IP
        print(f"\n[STEP 4] Changing IP address to {new_ip}...")
        session.change_ip_address(new_ip, subnet_mask, gateway)
        print("[STEP 4] IP change request submitted!")
        print("[STEP 4] Switch may disconnect while applying changes...")

    except SwitchAuthError as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        return False

    except SwitchConnectionError as e:
        # Connection loss during IP change is expected
        print("[STEP 4] Connection lost (expected during IP change)")

    finally:
        session.close()

    # Step 5: Wait and verify
    print(f"\n[STEP 5] Waiting 10 seconds for switch to apply changes...")
    time.sleep(10)

    # Step 6: Ping verification
    print("\n[STEP 6] Verifying new IP address...")
    if not wait_for_ping(new_ip, max_attempts=12, interval=5):
        print(f"\n[ERROR] Switch not responding at {new_ip}")
        print("[ERROR] The IP change may have failed or the switch needs more time")
        return False

    # Step 7: Login verification
    print(f"\n[STEP 7] Verifying login at new IP {new_ip}...")
    new_session = SwitchSession(new_ip, timeout=30.0)

    try:
        new_session.login(username, password)
        print("[STEP 7] Login successful!")

        # Read config to confirm
        print("\n[STEP 7] Confirming IP configuration...")
        new_config = new_session.get_current_ip_config()
        print("[STEP 7] New configuration:")
        for key, value in new_config.items():
            print(f"         {key:15s}: {value}")

        # Verify IP matches
        actual_ip = new_config.get("ip_address", "")
        if actual_ip == new_ip:
            print(f"\n[SUCCESS] IP address successfully changed to {new_ip}")
            print("=" * 70)
            return True
        else:
            print(f"\n[WARNING] IP mismatch! Expected {new_ip}, got {actual_ip}")
            return False

    except (SwitchAuthError, SwitchConnectionError) as e:
        print(f"\n[ERROR] Verification failed: {e}")
        return False

    finally:
        new_session.close()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = argparse.ArgumentParser(
        description="Simple tool to change Binardat switch IP address",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use all defaults (192.168.2.1 -> 192.168.2.100)
  python simple_ip_change.py

  # Specify different IPs
  python simple_ip_change.py \\
    --current-ip 192.168.1.1 \\
    --new-ip 192.168.1.100

  # Full configuration
  python simple_ip_change.py \\
    --current-ip 192.168.2.1 \\
    --username admin \\
    --password admin \\
    --new-ip 192.168.2.100 \\
    --subnet 255.255.255.0 \\
    --gateway 192.168.2.1
        """,
    )

    parser.add_argument(
        "--current-ip",
        default="192.168.2.1",
        help="Current IP address of the switch (default: 192.168.2.1)",
    )
    parser.add_argument(
        "--username",
        "-u",
        default="admin",
        help="Switch username (default: admin)",
    )
    parser.add_argument(
        "--password",
        "-p",
        default="admin",
        help="Switch password (default: admin)",
    )
    parser.add_argument(
        "--new-ip",
        default="192.168.2.100",
        help="New IP address to set (default: 192.168.2.100)",
    )
    parser.add_argument(
        "--subnet",
        default="255.255.255.0",
        help="Subnet mask (default: 255.255.255.0)",
    )
    parser.add_argument(
        "--gateway",
        help="Default gateway (optional)",
    )

    args = parser.parse_args()

    try:
        success = change_switch_ip(
            current_ip=args.current_ip,
            username=args.username,
            password=args.password,
            new_ip=args.new_ip,
            subnet_mask=args.subnet,
            gateway=args.gateway,
        )

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Operation cancelled by user")
        return 130

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
