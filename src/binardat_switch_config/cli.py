"""Command-line interface for Binardat switch configuration.

This module provides the CLI entry point for enabling SSH on Binardat switches.
"""

import argparse
import signal
import sys
import time

from binardat_switch_config import __version__
from binardat_switch_config.ssh_enabler import (
    SSHEnabler,
    load_config_from_env,
    verify_ssh_port,
)


# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully.

    Args:
        signum: Signal number.
        frame: Current stack frame.
    """
    global shutdown_requested
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_requested = True
    sys.exit(0)


def main():
    """Main entry point for the CLI."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Load configuration from environment variables
    env_config = load_config_from_env()

    parser = argparse.ArgumentParser(
        description="Enable SSH on Binardat switch via web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults from environment variables or fallback to 192.168.2.1, admin/admin
  binardat-config

  # Custom switch IP (overrides SWITCH_IP env var)
  binardat-config --switch-ip 192.168.2.100

  # Custom credentials (overrides env vars)
  binardat-config --username admin --password mypass

  # Show browser for debugging
  binardat-config --show-browser

  # Full configuration
  binardat-config \\
    --switch-ip 192.168.2.1 \\
    --username admin \\
    --password admin \\
    --port 22 \\
    --show-browser

Environment Variables:
  SWITCH_IP         - Switch IP address (default: 192.168.2.1)
  SWITCH_USERNAME   - Login username (default: admin)
  SWITCH_PASSWORD   - Login password (default: admin)
  SWITCH_SSH_PORT   - SSH port number (default: 22)
  TIMEOUT           - Timeout in seconds (default: 10)
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='Show version and exit'
    )
    parser.add_argument(
        '--switch-ip',
        default=env_config['switch_ip'],
        help=f"IP address of the switch (default from env: {env_config['switch_ip']})"
    )
    parser.add_argument(
        '-u', '--username',
        default=env_config['username'],
        help=f"Login username (default from env: {env_config['username']})"
    )
    parser.add_argument(
        '-p', '--password',
        default=env_config['password'],
        help='Login password (default from env or --password)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=env_config['port'],
        help=f"SSH port number (default from env: {env_config['port']})"
    )
    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser window (default: headless mode)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=env_config['timeout'],
        help=f"Timeout in seconds for page loads (default from env: {env_config['timeout']})"
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip SSH port verification'
    )

    args = parser.parse_args()

    # Create enabler instance
    enabler = SSHEnabler(
        headless=not args.show_browser,
        timeout=args.timeout
    )

    # Enable SSH
    success = enabler.enable_ssh(
        switch_ip=args.switch_ip,
        username=args.username,
        password=args.password,
        port=args.port
    )

    if not success:
        print("\n✗ SSH enablement failed")
        return 1

    # Verify SSH port accessibility unless disabled
    if not args.no_verify:
        print(f"\n{'='*60}")
        print(f"Verifying SSH port {args.port} accessibility...")
        print(f"{'='*60}\n")

        print("Waiting for SSH service to start (5 seconds)...")
        time.sleep(5)

        if verify_ssh_port(args.switch_ip, args.port):
            print(f"✓ SSH port {args.port} is accessible")
            print(f"\nYou can now connect via SSH:")
            print(f"  ssh {args.username}@{args.switch_ip}")
        else:
            print(f"⚠ SSH port {args.port} is not responding")
            print("\nPossible reasons:")
            print("  - SSH service requires switch reboot to start")
            print("  - SSH is enabled but on a different port")
            print("  - Firewall blocking SSH connections")
            print("\nTry:")
            print(f"  1. Reboot the switch")
            print(f"  2. Verify SSH is enabled in web interface")
            print(f"  3. Check switch firewall settings")
    else:
        print("\nSkipping verification (--no-verify)")

    print(f"\n{'='*60}")
    print("SSH ENABLEMENT COMPLETED")
    print(f"Switch: {args.switch_ip}")
    print(f"Port: {args.port}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
