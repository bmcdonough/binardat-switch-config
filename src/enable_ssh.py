#!/usr/bin/env python3
"""Enable SSH on Binardat switch using Selenium browser automation.

This script automates enabling SSH through the web interface using Selenium
WebDriver. It logs in, navigates to the SSH configuration page under Monitor
Management, enables SSH, and saves the configuration.

Docker-optimized version with environment variable support.

Example:
    Basic usage with environment variables:
        $ docker run --network host -e SWITCH_IP=192.168.2.1 binardat-ssh-enabler

    With defaults (192.168.2.1, admin/admin):
        $ python enable_ssh.py

    Custom switch IP:
        $ python enable_ssh.py --switch-ip 192.168.2.100

    Show browser for debugging:
        $ python enable_ssh.py --show-browser
"""

import argparse
import os
import signal
import socket
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
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


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


def load_config_from_env():
    """Load configuration from environment variables.

    Returns:
        Dictionary with configuration values from environment.
    """
    return {
        'switch_ip': os.getenv('SWITCH_IP', '192.168.2.1'),
        'username': os.getenv('SWITCH_USERNAME', 'admin'),
        'password': os.getenv('SWITCH_PASSWORD', 'admin'),
        'port': int(os.getenv('SWITCH_SSH_PORT', '22')),
        'timeout': int(os.getenv('TIMEOUT', '10')),
    }


class SSHEnabler:
    """Automates SSH enablement on Binardat switches via web interface."""

    def __init__(self, headless: bool = True, timeout: int = 10):
        """Initialize the SSH enabler.

        Args:
            headless: Run browser in headless mode (no GUI).
            timeout: Default timeout in seconds for element waits.
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with Docker-compatible options.

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

        # Check if we're in Docker (CHROMEDRIVER_PATH env var set)
        chrome_driver_path = os.getenv('CHROMEDRIVER_PATH')

        if chrome_driver_path and os.path.exists(chrome_driver_path):
            # Use explicit ChromeDriver path for Docker
            print(f"Using ChromeDriver at: {chrome_driver_path}")
            service = Service(executable_path=chrome_driver_path)
            return webdriver.Chrome(service=service, options=options)
        else:
            # Use Selenium Manager for local development
            print("Using Selenium Manager to locate ChromeDriver...")
            return webdriver.Chrome(options=options)

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

    def _navigate_to_ssh_config(self) -> bool:
        """Navigate to the SSH Config page under Monitor Management.

        Returns:
            True if navigation successful, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, self.timeout)

            print("Looking for Monitor Management menu...")

            # Wait for page to be ready
            time.sleep(2)

            # The menu structure is hierarchical:
            # 1. Find and click "Monitor Management" parent menu
            # 2. Then click the submenu item with datalink="ssh_get.cgi"

            # Step 1: Find and click the "Monitor Management" parent menu
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            monitor_mgmt_parent = None

            for link in all_links:
                text = link.text.strip()
                if text == "Monitor Management":
                    monitor_mgmt_parent = link
                    print(f"Found 'Monitor Management' parent menu")
                    break

            if monitor_mgmt_parent is None:
                print("✗ Could not find 'Monitor Management' parent menu")
                return False

            # Click the parent menu to expand submenu
            print("Clicking 'Monitor Management' to expand submenu...")
            monitor_mgmt_parent.click()
            time.sleep(1)  # Wait for submenu to expand

            # Step 2: Find and click the SSH Config link
            print("Looking for SSH Config submenu item...")
            ssh_link = None

            try:
                ssh_link = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'a[datalink="ssh_get.cgi"]')
                    )
                )
                print("Found SSH Config link (ssh_get.cgi)")
            except TimeoutException:
                print("✗ Could not find link with datalink='ssh_get.cgi'")
                visible_links = [l for l in self.driver.find_elements(By.TAG_NAME, "a") if l.is_displayed()]
                print(f"Found {len(visible_links)} visible links after expanding menu")
                return False

            print("Clicking SSH Config submenu item...")
            ssh_link.click()

            # Wait for the SSH config form to load
            print("Waiting for SSH configuration form to load...")
            time.sleep(2)  # Give the page time to load via AJAX

            # Verify form loaded successfully
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#appMainInner")
                    )
                )
                print("✓ Navigated to SSH configuration page")
                return True
            except TimeoutException:
                print("✗ Could not load SSH configuration form")
                return False

        except TimeoutException:
            print("✗ Navigation failed: Timeout")
            return False
        except NoSuchElementException as e:
            print(f"✗ Navigation failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Navigation error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _enable_ssh_form(self, port: int = 22) -> bool:
        """Fill and submit the SSH enablement form.

        Args:
            port: SSH port number (default: 22).

        Returns:
            True if form submitted successfully, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, self.timeout)

            print("Looking for SSH enable form fields...")

            # Try multiple field name patterns for enable checkbox/select
            enable_selectors = [
                'input[name="enable"]',
                'input[name="ssh_enable"]',
                'input[name="status"]',
                'select[name="enable"]',
                'select[name="ssh_enable"]',
                'select[name="status"]',
                'input[id*="enable"]',
                'select[id*="enable"]',
            ]

            enable_field = None
            found_selector = None
            for selector in enable_selectors:
                try:
                    enable_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    found_selector = selector
                    print(f"Found enable field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if enable_field is None:
                # Fallback: find all input and select fields and display them for debugging
                print("Could not find enable field automatically. Inspecting form...")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                inputs.extend(self.driver.find_elements(By.TAG_NAME, "select"))
                print(f"Found {len(inputs)} input/select fields:")
                for inp in inputs:
                    name = inp.get_attribute("name") or "no-name"
                    id_attr = inp.get_attribute("id") or "no-id"
                    input_type = inp.get_attribute("type") or inp.tag_name
                    print(f"  - name='{name}', id='{id_attr}', type='{input_type}'")
                return False

            # Enable SSH based on field type
            if enable_field.tag_name == "input" and enable_field.get_attribute("type") == "checkbox":
                print("Found checkbox for SSH enable")
                if not enable_field.is_selected():
                    print("Enabling SSH (checking checkbox)...")
                    checkbox_id = enable_field.get_attribute("id")
                    if checkbox_id:
                        # Try to find and click the label for this checkbox
                        try:
                            label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                            print(f"Clicking label for checkbox (id={checkbox_id})")
                            label.click()
                        except NoSuchElementException:
                            # Fallback: use JavaScript to click the checkbox directly
                            print("Using JavaScript to check checkbox")
                            self.driver.execute_script("arguments[0].click();", enable_field)
                    else:
                        # No ID, use JavaScript to click
                        print("Using JavaScript to check checkbox")
                        self.driver.execute_script("arguments[0].click();", enable_field)
                else:
                    print("SSH already enabled (checkbox is checked)")
            elif enable_field.tag_name == "select":
                print("Found dropdown for SSH enable")
                select = Select(enable_field)
                # Try to select "Enabled", "Enable", "1", etc.
                try:
                    select.select_by_visible_text("Enabled")
                    print("Selected 'Enabled' from dropdown")
                except NoSuchElementException:
                    try:
                        select.select_by_visible_text("Enable")
                        print("Selected 'Enable' from dropdown")
                    except NoSuchElementException:
                        try:
                            select.select_by_value("1")
                            print("Selected value '1' from dropdown")
                        except NoSuchElementException:
                            print("Warning: Could not select enable option, trying first option")
                            select.select_by_index(0)
            elif enable_field.tag_name == "input" and enable_field.get_attribute("type") == "radio":
                print("Found radio button for SSH enable")
                # Radio buttons with value "1" or "enable" are typically "enable"
                radio_value = enable_field.get_attribute("value")
                if radio_value in ["1", "enable", "enabled", "on"]:
                    enable_field.click()
                    print(f"Selected radio button with value '{radio_value}'")
            else:
                print(f"Warning: Unknown field type for enable: {enable_field.tag_name}")

            # Note: The SSH checkbox has an onChange handler that submits immediately
            # No separate submit button is needed. The checkbox click triggers:
            # httpPostGet('POST', 'ssh_post.cgi', 'ssh_enable=on', ...)
            # Then the page reloads with reCurrentWeb()

            print("Waiting for SSH enable submission to complete...")
            # The JavaScript waits up to 60 seconds and then reloads the page
            # Wait for the page to potentially reload
            time.sleep(5)

            # Optional: Check if SSH config fields are now visible (indicates SSH is enabled)
            try:
                # These fields appear after SSH is enabled
                ssh_args = self.driver.find_elements(By.CSS_SELECTOR, '.ssh-args')
                if ssh_args and any(elem.is_displayed() for elem in ssh_args):
                    print("✓ SSH configuration fields are now visible (SSH enabled)")
                else:
                    print("Note: SSH config fields not visible (may need page refresh)")
            except:
                pass

            print("✓ Form submitted successfully")
            return True

        except Exception as e:
            print(f"✗ Error filling form: {e}")
            import traceback
            traceback.print_exc()
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

    def enable_ssh(
        self,
        switch_ip: str,
        username: str,
        password: str,
        port: int = 22
    ) -> bool:
        """Enable SSH on the switch.

        Args:
            switch_ip: IP address of the switch.
            username: Login username.
            password: Login password.
            port: SSH port number (default: 22).

        Returns:
            True if SSH enablement successful, False otherwise.
        """
        try:
            self.driver = self._setup_driver()

            print(f"\n{'='*60}")
            print(f"Enabling SSH on switch: {switch_ip}")
            print(f"{'='*60}\n")

            # Step 1: Login
            if not self._login(switch_ip, username, password):
                return False

            # Step 2: Navigate to SSH config
            if not self._navigate_to_ssh_config():
                return False

            # Step 3: Fill and submit form
            if not self._enable_ssh_form(port):
                return False

            # Step 4: Save configuration
            if not self._save_configuration():
                print("Warning: Configuration save may have failed")

            print("\n✓ SSH enablement process completed successfully")
            print("SSH service should now be active...")

            return True

        except Exception as e:
            print(f"\n✗ Error during SSH enablement: {e}")
            return False

        finally:
            if self.driver:
                print("Closing browser...")
                self.driver.quit()


def verify_ssh_port(host: str, port: int = 22, timeout: float = 5.0) -> bool:
    """Verify SSH port is accessible via socket connection.

    Args:
        host: IP address or hostname.
        port: SSH port number (default: 22).
        timeout: Connection timeout in seconds.

    Returns:
        True if port is accessible, False otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Socket error: {e}")
        return False


def main():
    """Main entry point for the script."""
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
  python enable_ssh.py

  # Custom switch IP (overrides SWITCH_IP env var)
  python enable_ssh.py --switch-ip 192.168.2.100

  # Custom credentials (overrides env vars)
  python enable_ssh.py --username admin --password mypass

  # Show browser for debugging
  python enable_ssh.py --show-browser

  # Full configuration
  python enable_ssh.py \\
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
