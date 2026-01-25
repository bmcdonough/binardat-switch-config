"""Interactive login analysis tool for Binardat switches.

This script provides an interactive way to analyze the switch's
login mechanism, extract the RC4 key, and test connectivity.
"""

import argparse
import re
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup


def fetch_login_page(host: str, timeout: float = 10.0) -> Optional[str]:
    """Fetch the login page HTML.

    Args:
        host: Switch IP address or hostname.
        timeout: Request timeout in seconds. Defaults to 10.0.

    Returns:
        HTML content if successful, None otherwise.
    """
    url = f"http://{host}/"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error: Could not connect to {url}")
        print(f"Details: {e}")
        return None


def extract_rc4_key_from_html(html: str) -> Optional[str]:
    """Extract RC4 encryption key from HTML/JavaScript.

    Args:
        html: HTML content from the login page.

    Returns:
        RC4 key if found, None otherwise.
    """
    # Parse HTML and look for inline JavaScript
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")

    for script in scripts:
        if script.string:
            # Look for RC4 key patterns
            patterns = [
                r'key\s*=\s*["\']([^"\']+)["\']',
                r'rc4[Kk]ey\s*=\s*["\']([^"\']+)["\']',
                r'encryptionKey\s*=\s*["\']([^"\']+)["\']',
                r'var\s+\w+\s*=\s*["\']([0-9a-fA-F]{16,})["\']',
            ]

            for pattern in patterns:
                match = re.search(pattern, script.string, re.IGNORECASE)
                if match:
                    return match.group(1)

    return None


def extract_form_fields(html: str) -> dict:
    """Extract form field names from the login page.

    Args:
        html: HTML content from the login page.

    Returns:
        Dictionary with form information.
    """
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")

    form_info = {"forms": []}

    for form in forms:
        form_data = {
            "action": form.get("action", ""),
            "method": form.get("method", "GET"),
            "fields": [],
        }

        inputs = form.find_all("input")
        for inp in inputs:
            field = {
                "name": inp.get("name", ""),
                "type": inp.get("type", "text"),
                "value": inp.get("value", ""),
            }
            form_data["fields"].append(field)

        form_info["forms"].append(form_data)

    return form_info


def test_connectivity(host: str, timeout: float = 10.0) -> bool:
    """Test basic connectivity to the switch.

    Args:
        host: Switch IP address or hostname.
        timeout: Request timeout in seconds. Defaults to 10.0.

    Returns:
        True if switch is reachable, False otherwise.
    """
    url = f"http://{host}/"
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def display_analysis(host: str, html: str) -> None:
    """Display analysis results in a formatted way.

    Args:
        host: Switch IP address or hostname.
        html: HTML content from the login page.
    """
    print("\n" + "=" * 70)
    print(f"SWITCH LOGIN ANALYSIS: {host}")
    print("=" * 70)

    # Test connectivity
    print("\n[1] CONNECTIVITY TEST")
    if test_connectivity(host):
        print("    Status: OK (switch is reachable)")
    else:
        print("    Status: FAILED (switch is not reachable)")

    # Extract RC4 key
    print("\n[2] RC4 ENCRYPTION KEY")
    rc4_key = extract_rc4_key_from_html(html)
    if rc4_key:
        print(f"    Key found: {rc4_key}")
        print(f"    Length: {len(rc4_key)} characters")
    else:
        print("    Key not found (may need manual inspection)")

    # Extract form fields
    print("\n[3] LOGIN FORM STRUCTURE")
    form_info = extract_form_fields(html)

    if not form_info["forms"]:
        print("    No forms found on the page")
    else:
        for i, form in enumerate(form_info["forms"], 1):
            print(f"\n    Form #{i}:")
            print(f"      Action: {form['action'] or '(same page)'}")
            print(f"      Method: {form['method'].upper()}")
            print("      Fields:")
            for field in form["fields"]:
                name = field["name"] or "(no name)"
                field_type = field["type"]
                value = field["value"]
                if value:
                    print(f"        - {name} ({field_type}) = {value}")
                else:
                    print(f"        - {name} ({field_type})")

    # JavaScript analysis
    print("\n[4] JAVASCRIPT ANALYSIS")
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")

    inline_scripts = [s for s in scripts if s.string and len(s.string) > 50]
    external_scripts = [s for s in scripts if s.get("src")]

    print(f"    Inline scripts: {len(inline_scripts)}")
    print(f"    External scripts: {len(external_scripts)}")

    if external_scripts:
        print("    External script URLs:")
        for script in external_scripts:
            print(f"      - {script.get('src')}")

    # Save HTML for manual inspection
    output_file = "login_page_analysis.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print("\n[5] OUTPUT")
    print(f"    HTML saved to: {output_file}")

    print("\n" + "=" * 70)


def main() -> int:
    """Run interactive login analysis.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Interactive analysis of switch login mechanism"
    )
    parser.add_argument(
        "--host",
        default="192.168.2.1",
        help="Switch IP address (default: 192.168.2.1)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10.0)",
    )
    args = parser.parse_args()

    print("Binardat Switch Login Analyzer")
    print(f"Target: {args.host}\n")

    # Fetch login page
    print("Fetching login page...")
    html = fetch_login_page(args.host, args.timeout)

    if not html:
        print("\nFailed to fetch login page. Please check:")
        print("  - Switch is powered on and connected")
        print("  - IP address is correct")
        print("  - Your machine is on the same network")
        print(f"  - You can ping {args.host}")
        return 1

    # Display analysis
    display_analysis(args.host, html)

    print("\nNext steps:")
    print("  1. Review the output above")
    print("  2. Check login_page_analysis.html for details")
    print("  3. If RC4 key not found, manually inspect JavaScript")
    print("  4. Note the form field names for authentication")
    print("  5. Run 02_test_login.py to test authentication")

    return 0


if __name__ == "__main__":
    sys.exit(main())
