#!/usr/bin/env python3
"""Test Selenium setup and ChromeDriver installation.

This script verifies that:
1. Selenium is installed correctly
2. ChromeDriver can be downloaded/configured
3. Chrome browser is available
4. Basic browser automation works

Run this before using selenium_ip_change.py to ensure everything is set up.
"""

import sys


def test_imports():
    """Test if required packages can be imported."""
    print("Testing imports...")

    try:
        import selenium
        print(f"  ✓ selenium {selenium.__version__}")

        # Check if Selenium version supports Selenium Manager (4.6+)
        version_parts = selenium.__version__.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major < 4 or (major == 4 and minor < 6):
            print(f"  ⚠ Warning: Selenium {selenium.__version__} may not fully support Selenium Manager")
            print("    Consider upgrading: pip install --upgrade selenium")
        else:
            print(f"  ✓ Selenium Manager available (built-in)")

    except ImportError as e:
        print(f"  ✗ selenium not found: {e}")
        print("    Install: pip install selenium")
        return False

    return True


def test_chrome_driver():
    """Test if ChromeDriver can be set up."""
    print("\nTesting ChromeDriver setup...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        print("  Using Selenium Manager to configure ChromeDriver...")
        # Selenium Manager will automatically download the correct ChromeDriver version
        # No need for Service or webdriver-manager
        print("  Starting Chrome browser...")
        driver = webdriver.Chrome(options=options)

        print("  Testing navigation...")
        driver.get("data:text/html,<h1>Test Page</h1>")

        title = driver.title
        print(f"  ✓ Browser working (page title: '{title}')")

        driver.quit()
        return True

    except Exception as e:
        print(f"  ✗ ChromeDriver test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Install Chrome/Chromium browser")
        print("  2. Ensure you have internet access (Selenium Manager downloads ChromeDriver)")
        print("  3. Check for firewall/proxy issues")
        print("  4. Try manually: sudo apt update && sudo apt install chromium-browser")
        return False


def test_basic_automation():
    """Test basic browser automation features."""
    print("\nTesting browser automation...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Selenium Manager handles driver setup automatically
        driver = webdriver.Chrome(options=options)

        # Load a test page with a form
        test_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Form</title></head>
        <body>
            <form>
                <input type="text" id="test-input" name="test" />
                <button type="submit" id="test-button">Submit</button>
            </form>
        </body>
        </html>
        """
        driver.get(f"data:text/html,{test_html}")

        # Test element finding
        wait = WebDriverWait(driver, 5)
        input_field = wait.until(
            EC.presence_of_element_located((By.ID, "test-input"))
        )
        print("  ✓ Element location works")

        # Test input filling
        input_field.send_keys("test value")
        print("  ✓ Form input works")

        # Test button clicking
        button = driver.find_element(By.ID, "test-button")
        button.click()
        print("  ✓ Button clicking works")

        driver.quit()
        return True

    except Exception as e:
        print(f"  ✗ Automation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Selenium Setup Test")
    print("="*60 + "\n")

    all_passed = True

    # Test 1: Imports
    if not test_imports():
        all_passed = False
        print("\n❌ Setup incomplete - install missing packages")
        return 1

    # Test 2: ChromeDriver
    if not test_chrome_driver():
        all_passed = False

    # Test 3: Basic automation
    if all_passed and not test_basic_automation():
        all_passed = False

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nYour environment is ready!")
        print("You can now run: python selenium_ip_change.py")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running selenium_ip_change.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
