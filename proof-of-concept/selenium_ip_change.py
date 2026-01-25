#!/usr/bin/env python3
"""Change Binardat switch IP using Selenium browser automation.

This script automates changing a Binardat switch's IP address through the web
interface using Selenium WebDriver. It logs in, navigates to the IP configuration
page, fills the form, submits changes, and verifies the new IP is accessible.

Example:
    Basic usage with defaults (192.168.2.1 → 192.168.2.100):
        $ python selenium_ip_change.py

    Custom IP addresses:
        $ python selenium_ip_change.py --current-ip 192.168.2.1 \\
            --new-ip 192.168.2.100 --subnet 255.255.255.0

    Show browser for debugging:
        $ python selenium_ip_change.py --show-browser
"""

import argparse
import subprocess
import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SwitchIPChanger:
    """Automates IP address changes on Binardat switches via web interface."""

    def __init__(self, headless: bool = True, timeout: int = 10):
        """Initialize the switch IP changer.

        Args:
            headless: Run browser in headless mode (no GUI).
            timeout: Default timeout in seconds for element waits.
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with appropriate options.

        Returns:
            Configured Chrome WebDriver instance.

        Raises:
            WebDriverException: If driver initialization fails.
        """
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Disable logging
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        print("Setting up Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _login(
        self, host: str, username: str, password: str
    ) -> bool:
        """Log into the switch web interface.

        Args:
            host: Switch IP address or hostname.
            username: Login username.
            password: Login password.

        Returns:
            True if login successful, False otherwise.
        """
        try:
            url = f"http://{host}/"
            print(f"Navigating to {url}...")
            self.driver.get(url)

            # Wait for login page to load
            wait = WebDriverWait(self.driver, self.timeout)

            print("Waiting for login form...")
            name_field = wait.until(
                EC.presence_of_element_located((By.ID, "name"))
            )
            pwd_field = self.driver.find_element(By.ID, "pwd")

            print(f"Logging in as '{username}'...")
            name_field.clear()
            name_field.send_keys(username)
            pwd_field.clear()
            pwd_field.send_keys(password)

            # Find and click login button
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[onclick='loginSubmit()']"
            )
            login_button.click()

            # Wait for redirect to main page (index.cgi)
            print("Waiting for main page to load...")
            wait.until(
                lambda d: "index.cgi" in d.current_url or "index.html" in d.current_url
            )

            # Verify we're logged in by checking for main page elements
            wait.until(
                EC.presence_of_element_located((By.ID, "appMainInner"))
            )

            print("✓ Login successful")
            return True

        except TimeoutException:
            print("✗ Login failed: Timeout waiting for page elements")
            return False
        except NoSuchElementException as e:
            print(f"✗ Login failed: Could not find element: {e}")
            return False
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False

    def _navigate_to_ip_config(self) -> bool:
        """Navigate to the IPv4 configuration page.

        Returns:
            True if navigation successful, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, self.timeout)

            print("Looking for IPv4 Config menu item...")

            # Wait for menu to be ready
            wait.until(
                EC.presence_of_element_located((By.ID, "menu"))
            )

            # Find the IPv4 Config link by its datalink attribute
            # The menu uses <a> tags with datalink="Manageportip.cgi"
            ipv4_link = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'a[datalink="Manageportip.cgi"]')
                )
            )

            print("Clicking IPv4 Config menu item...")
            ipv4_link.click()

            # Wait for the IP config form to load in appMainInner
            print("Waiting for IP configuration form to load...")
            time.sleep(2)  # Give the page time to load via AJAX

            # Switch to the iframe if the content is loaded in one
            # Otherwise wait for form fields in the main page
            try:
                # Check if form loaded successfully
                # We'll look for typical IP config form elements
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#appMainInner")
                    )
                )
                print("✓ Navigated to IP configuration page")
                return True

            except TimeoutException:
                print("✗ Could not load IP configuration form")
                return False

        except TimeoutException:
            print("✗ Navigation failed: Could not find IPv4 Config menu item")
            return False
        except NoSuchElementException as e:
            print(f"✗ Navigation failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Navigation error: {e}")
            return False

    def _fill_and_submit_ip_form(
        self,
        new_ip: str,
        subnet_mask: str,
        gateway: Optional[str] = None
    ) -> bool:
        """Fill and submit the IP configuration form.

        Args:
            new_ip: New IP address for the switch.
            subnet_mask: Subnet mask (e.g., 255.255.255.0).
            gateway: Default gateway (optional).

        Returns:
            True if form submitted successfully, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, self.timeout)

            print("Looking for IP address form fields...")

            # Common field names for IP configuration forms
            # Try multiple possible field name variations
            ip_field_selectors = [
                'input[name="ip"]',
                'input[name="ip_address"]',
                'input[name="ipAddress"]',
                'input[name="ip_addr"]',
                'input[id*="ip"]',
            ]

            ip_field = None
            for selector in ip_field_selectors:
                try:
                    ip_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found IP field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if ip_field is None:
                # Fallback: find all input fields and display them for debugging
                print("Could not find IP field automatically. Inspecting form...")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"Found {len(inputs)} input fields:")
                for inp in inputs:
                    name = inp.get_attribute("name") or "no-name"
                    id_attr = inp.get_attribute("id") or "no-id"
                    input_type = inp.get_attribute("type") or "text"
                    print(f"  - name='{name}', id='{id_attr}', type='{input_type}'")
                return False

            # Find subnet mask field
            mask_field_selectors = [
                'input[name="netmask"]',
                'input[name="mask"]',
                'input[name="subnet_mask"]',
                'input[name="subnetMask"]',
                'input[id*="mask"]',
            ]

            mask_field = None
            for selector in mask_field_selectors:
                try:
                    mask_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found subnet mask field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if mask_field is None:
                print("✗ Could not find subnet mask field")
                return False

            # Fill in the IP address and subnet mask
            print(f"Setting IP address to {new_ip}...")
            ip_field.clear()
            ip_field.send_keys(new_ip)

            print(f"Setting subnet mask to {subnet_mask}...")
            mask_field.clear()
            mask_field.send_keys(subnet_mask)

            # Optionally fill in gateway if provided
            if gateway:
                gateway_field_selectors = [
                    'input[name="gateway"]',
                    'input[name="default_gateway"]',
                    'input[name="defaultGateway"]',
                    'input[id*="gateway"]',
                ]

                gateway_field = None
                for selector in gateway_field_selectors:
                    try:
                        gateway_field = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        print(f"Found gateway field with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue

                if gateway_field:
                    print(f"Setting gateway to {gateway}...")
                    gateway_field.clear()
                    gateway_field.send_keys(gateway)
                else:
                    print("Note: Could not find gateway field (may be optional)")

            # Find and click submit button
            print("Looking for submit button...")
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[onclick*="submit"]',
                'button.btn-primary',
                'button.submit',
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found submit button with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if submit_button is None:
                print("✗ Could not find submit button")
                return False

            print("Submitting IP configuration...")
            submit_button.click()

            # Wait a moment for the submission to process
            time.sleep(3)

            print("✓ Form submitted successfully")
            return True

        except Exception as e:
            print(f"✗ Error filling form: {e}")
            return False

    def _save_configuration(self) -> bool:
        """Save the switch configuration to make changes persistent.

        Returns:
            True if save successful, False otherwise.
        """
        try:
            print("Saving configuration to switch...")

            # Execute JavaScript to call the save command
            # Based on the documentation, switches use syscmd.cgi with cmd=save
            self.driver.execute_script("""
                httpPostGet('POST', 'syscmd.cgi', 'cmd=save', function(val) {
                    console.log('Configuration saved:', val);
                });
            """)

            time.sleep(2)

            print("✓ Configuration save command sent")
            return True

        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
            return False

    def change_ip(
        self,
        current_ip: str,
        username: str,
        password: str,
        new_ip: str,
        subnet_mask: str,
        gateway: Optional[str] = None
    ) -> bool:
        """Change the switch IP address.

        Args:
            current_ip: Current IP address of the switch.
            username: Login username.
            password: Login password.
            new_ip: Desired new IP address.
            subnet_mask: Subnet mask.
            gateway: Default gateway (optional).

        Returns:
            True if IP change successful, False otherwise.
        """
        try:
            self.driver = self._setup_driver()

            print(f"\n{'='*60}")
            print(f"Changing switch IP: {current_ip} → {new_ip}")
            print(f"{'='*60}\n")

            # Step 1: Login
            if not self._login(current_ip, username, password):
                return False

            # Step 2: Navigate to IP config
            if not self._navigate_to_ip_config():
                return False

            # Step 3: Fill and submit form
            if not self._fill_and_submit_ip_form(new_ip, subnet_mask, gateway):
                return False

            # Step 4: Save configuration
            if not self._save_configuration():
                print("Warning: Configuration save may have failed")

            print("\n✓ IP change process completed successfully")
            print("Switch is applying changes and may reboot...")

            return True

        except Exception as e:
            print(f"\n✗ Error during IP change: {e}")
            return False

        finally:
            if self.driver:
                print("Closing browser...")
                self.driver.quit()

    def verify_change(
        self,
        new_ip: str,
        username: str,
        password: str,
        max_wait: int = 60
    ) -> bool:
        """Verify the IP change by pinging and logging into the new IP.

        Args:
            new_ip: The new IP address to verify.
            username: Login username.
            password: Login password.
            max_wait: Maximum time to wait for switch to respond (seconds).

        Returns:
            True if verification successful, False otherwise.
        """
        print(f"\n{'='*60}")
        print(f"Verifying new IP address: {new_ip}")
        print(f"{'='*60}\n")

        # Wait for switch to apply changes
        print("Waiting for switch to apply changes (30 seconds)...")
        time.sleep(30)

        # Wait for ping response
        if not wait_for_ping(new_ip, max_attempts=max_wait // 5):
            print(f"✗ Verification failed: {new_ip} is not responding to ping")
            return False

        # Verify by logging in to new IP
        try:
            print(f"\nAttempting to log in to new IP ({new_ip})...")
            self.driver = self._setup_driver()

            if not self._login(new_ip, username, password):
                print(f"✗ Verification failed: Could not log in to {new_ip}")
                return False

            print(f"\n✓ Verification successful!")
            print(f"✓ Switch is accessible at {new_ip}")

            return True

        except Exception as e:
            print(f"✗ Verification error: {e}")
            return False

        finally:
            if self.driver:
                self.driver.quit()


def wait_for_ping(ip: str, max_attempts: int = 12) -> bool:
    """Wait for an IP address to respond to ping.

    Args:
        ip: IP address to ping.
        max_attempts: Maximum number of ping attempts.

    Returns:
        True if ping successful, False otherwise.
    """
    print(f"Waiting for {ip} to respond to ping...")

    for attempt in range(1, max_attempts + 1):
        try:
            # Use platform-specific ping command
            if sys.platform.startswith('win'):
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '2000', ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=3
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=3
                )

            if result.returncode == 0:
                print(f"✓ {ip} is responding to ping (attempt {attempt}/{max_attempts})")
                return True
            else:
                print(f"  Attempt {attempt}/{max_attempts}: No response")

        except subprocess.TimeoutExpired:
            print(f"  Attempt {attempt}/{max_attempts}: Timeout")
        except Exception as e:
            print(f"  Attempt {attempt}/{max_attempts}: Error - {e}")

        if attempt < max_attempts:
            time.sleep(5)

    return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Change Binardat switch IP address via web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults (192.168.2.1 → 192.168.2.100)
  python selenium_ip_change.py

  # Custom IP addresses
  python selenium_ip_change.py --current-ip 192.168.2.1 --new-ip 192.168.2.50

  # Show browser for debugging
  python selenium_ip_change.py --show-browser

  # Full configuration
  python selenium_ip_change.py \\
    --current-ip 192.168.2.1 \\
    --new-ip 192.168.2.100 \\
    --subnet 255.255.255.0 \\
    --gateway 192.168.2.1 \\
    --username admin \\
    --password admin
        """
    )

    parser.add_argument(
        '--current-ip',
        default='192.168.2.1',
        help='Current IP address of the switch (default: 192.168.2.1)'
    )
    parser.add_argument(
        '--new-ip',
        default='192.168.2.100',
        help='New IP address for the switch (default: 192.168.2.100)'
    )
    parser.add_argument(
        '--subnet',
        default='255.255.255.0',
        help='Subnet mask (default: 255.255.255.0)'
    )
    parser.add_argument(
        '--gateway',
        default=None,
        help='Default gateway (optional)'
    )
    parser.add_argument(
        '-u', '--username',
        default='admin',
        help='Login username (default: admin)'
    )
    parser.add_argument(
        '-p', '--password',
        default='admin',
        help='Login password (default: admin)'
    )
    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser window (default: headless mode)'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip verification step'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds for page loads (default: 10)'
    )

    args = parser.parse_args()

    # Validate IP addresses
    if args.current_ip == args.new_ip:
        print("Error: Current IP and new IP are the same")
        return 1

    # Create changer instance
    changer = SwitchIPChanger(
        headless=not args.show_browser,
        timeout=args.timeout
    )

    # Change IP
    success = changer.change_ip(
        current_ip=args.current_ip,
        username=args.username,
        password=args.password,
        new_ip=args.new_ip,
        subnet_mask=args.subnet,
        gateway=args.gateway
    )

    if not success:
        print("\n✗ IP change failed")
        return 1

    # Verify unless disabled
    if not args.no_verify:
        if not changer.verify_change(
            new_ip=args.new_ip,
            username=args.username,
            password=args.password
        ):
            print("\n✗ Verification failed")
            return 1
    else:
        print("\nSkipping verification (--no-verify)")

    print(f"\n{'='*60}")
    print("SUCCESS!")
    print(f"Switch IP successfully changed to: {args.new_ip}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
