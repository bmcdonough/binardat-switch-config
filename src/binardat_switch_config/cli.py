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
        description="Enable or disable SSH on Binardat switch via web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable SSH (default action)
  binardat-config

  # Disable SSH
  binardat-config --disable

  # Custom switch IP (overrides SWITCH_IP env var)
  binardat-config --switch-ip 192.168.2.100

  # Custom credentials (overrides env vars)
  binardat-config --username admin --password mypass

  # Show browser for debugging
  binardat-config --show-browser

  # Full configuration for enabling SSH
  binardat-config \\
    --switch-ip 192.168.2.1 \\
    --username admin \\
    --password admin \\
    --port 22 \\
    --show-browser

  # Disable SSH with custom IP
  binardat-config --disable --switch-ip 192.168.2.100

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
        '--disable',
        action='store_true',
        help='Disable SSH instead of enabling it (default: enable SSH)'
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

    # Enable or disable SSH based on flag
    if args.disable:
        success = enabler.disable_ssh(
            switch_ip=args.switch_ip,
            username=args.username,
            password=args.password,
            port=args.port
        )
        action = "disablement"
    else:
        success = enabler.enable_ssh(
            switch_ip=args.switch_ip,
            username=args.username,
            password=args.password,
            port=args.port
        )
        action = "enablement"

    if not success:
        print(f"\n✗ SSH {action} failed")
        return 1

    # Verify SSH port accessibility unless disabled or we're disabling SSH
    if not args.no_verify and not args.disable:
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
    elif args.disable and not args.no_verify:
        print(f"\n{'='*60}")
        print(f"Verifying SSH port {args.port} is closed...")
        print(f"{'='*60}\n")

        print("Waiting for SSH service to stop (5 seconds)...")
        time.sleep(5)

        if not verify_ssh_port(args.switch_ip, args.port):
            print(f"✓ SSH port {args.port} is no longer accessible")
            print("\nSSH has been successfully disabled")
        else:
            print(f"⚠ SSH port {args.port} is still responding")
            print("\nPossible reasons:")
            print("  - SSH service requires switch reboot to stop")
            print("  - Configuration change hasn't taken effect yet")
            print("\nTry:")
            print(f"  1. Reboot the switch")
            print(f"  2. Verify SSH is disabled in web interface")
    else:
        print("\nSkipping verification (--no-verify)")

    print(f"\n{'='*60}")
    operation = "DISABLEMENT" if args.disable else "ENABLEMENT"
    print(f"SSH {operation} COMPLETED")
    print(f"Switch: {args.switch_ip}")
    print(f"Port: {args.port}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
