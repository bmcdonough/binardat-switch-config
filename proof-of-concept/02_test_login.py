"""Test authentication to Binardat switch.

This script tests the authentication mechanism by attempting to log in
to the switch and verifying session persistence.
"""

import argparse
import sys
from getpass import getpass

from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


def test_login(
    host: str,
    username: str,
    password: str,
    timeout: float = 30.0,
) -> bool:
    """Test login to the switch.

    Args:
        host: Switch IP address or hostname.
        username: Switch username.
        password: Switch password.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        True if login successful, False otherwise.
    """
    print("\n" + "=" * 70)
    print("BINARDAT SWITCH LOGIN TEST")
    print("=" * 70)
    print(f"Host:     {host}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print(f"Timeout:  {timeout}s")

    # Create session
    print("\n[1] Creating session...")
    session = SwitchSession(host, timeout)
    print("    Session created")

    # Attempt login
    print("\n[2] Attempting authentication...")
    try:
        success = session.login(username, password)

        if success:
            print("    Authentication: SUCCESS")
            print(f"    RC4 Key: {session.rc4_key}")
            print(f"    Authenticated: {session.authenticated}")

            # Test session persistence
            print("\n[3] Testing session persistence...")
            try:
                # Try to fetch a page (common pages: status, config, etc.)
                test_pages = [
                    "status.html",
                    "status.htm",
                    "index.html",
                    "main.html",
                    "home.html",
                ]

                page_found = False
                for page in test_pages:
                    try:
                        html = session.get_page(page)
                        print(f"    Successfully fetched: {page}")
                        print(f"    Page size: {len(html)} bytes")
                        page_found = True
                        break
                    except SwitchConnectionError:
                        continue

                if not page_found:
                    print("    Could not fetch any test pages")
                    print("    Session may still be valid")

            except Exception as e:
                print(f"    Session test failed: {e}")

            # Display session cookies
            print("\n[4] Session information:")
            cookies = session.session.cookies
            if cookies:
                print("    Cookies:")
                for cookie in cookies:
                    print(f"      {cookie.name} = {cookie.value}")
            else:
                print("    No cookies set")

            # Test logout
            print("\n[5] Testing logout...")
            try:
                session.logout()
                print("    Logout: SUCCESS")
            except Exception as e:
                print(f"    Logout failed: {e}")

            print("\n" + "=" * 70)
            print("RESULT: LOGIN TEST PASSED")
            print("=" * 70)
            return True

        else:
            print("    Authentication: FAILED")
            print("\n" + "=" * 70)
            print("RESULT: LOGIN TEST FAILED")
            print("=" * 70)
            return False

    except SwitchAuthError as e:
        print(f"    Authentication error: {e}")
        print("\n" + "=" * 70)
        print("RESULT: AUTHENTICATION ERROR")
        print("=" * 70)
        print("\nPossible causes:")
        print("  - Incorrect username or password")
        print("  - RC4 key extraction failed")
        print("  - Form field names have changed")
        print("  - Switch firmware version incompatible")
        return False

    except SwitchConnectionError as e:
        print(f"    Connection error: {e}")
        print("\n" + "=" * 70)
        print("RESULT: CONNECTION ERROR")
        print("=" * 70)
        print("\nPossible causes:")
        print("  - Switch is not reachable")
        print("  - Incorrect IP address")
        print("  - Network connectivity issues")
        print("  - Firewall blocking connection")
        return False

    except Exception as e:
        print(f"    Unexpected error: {e}")
        print("\n" + "=" * 70)
        print("RESULT: UNEXPECTED ERROR")
        print("=" * 70)
        return False

    finally:
        session.close()


def test_invalid_credentials(host: str, timeout: float = 30.0) -> bool:
    """Test that invalid credentials are rejected.

    Args:
        host: Switch IP address or hostname.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        True if invalid credentials properly rejected, False otherwise.
    """
    print("\n" + "=" * 70)
    print("INVALID CREDENTIALS TEST")
    print("=" * 70)

    invalid_username = "invalid_user_12345"
    invalid_password = "invalid_pass_12345"

    session = SwitchSession(host, timeout)

    try:
        print("Attempting login with invalid credentials...")
        session.login(invalid_username, invalid_password)

        # If we get here, authentication succeeded when it shouldn't
        print("ERROR: Invalid credentials were accepted!")
        return False

    except SwitchAuthError:
        print("Invalid credentials correctly rejected")
        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    finally:
        session.close()


def main() -> int:
    """Run login tests.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Test authentication to Binardat switch"
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
    parser.add_argument(
        "--test-invalid",
        action="store_true",
        help="Also test that invalid credentials are rejected",
    )
    args = parser.parse_args()

    # Prompt for credentials if not provided
    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    # Test valid login
    success = test_login(args.host, username, password, args.timeout)

    # Optionally test invalid credentials
    if args.test_invalid:
        print("\n")
        invalid_test = test_invalid_credentials(args.host, args.timeout)
        if not invalid_test:
            print("\nWARNING: Invalid credential test failed")

    # Return appropriate exit code
    if success:
        return 0
    else:
        print("\nLogin test failed. Please check:")
        print("  1. Switch is reachable (try: ping " + args.host + ")")
        print("  2. Credentials are correct")
        print("  3. Switch is not already logged in from another session")
        print("  4. Run analyze_login.py to inspect the login mechanism")
        return 1


if __name__ == "__main__":
    sys.exit(main())
