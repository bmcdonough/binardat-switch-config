"""Web interface reconnaissance script for Binardat switches.

This script analyzes the switch's web interface to understand:
- Login page structure and form fields
- JavaScript files containing RC4 encryption logic
- Session management (cookies, tokens)
- Authentication flow
"""

import argparse
import re
import sys
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch_page(url: str, timeout: float = 10.0) -> Optional[requests.Response]:
    """Fetch a web page from the switch.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds. Defaults to 10.0.

    Returns:
        Response object if successful, None if failed.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def analyze_login_form(soup: BeautifulSoup, base_url: str) -> None:
    """Analyze the login form structure.

    Args:
        soup: BeautifulSoup object of the login page.
        base_url: Base URL for resolving relative paths.
    """
    print("\n" + "=" * 70)
    print("LOGIN FORM ANALYSIS")
    print("=" * 70)

    forms = soup.find_all("form")
    if not forms:
        print("No forms found on the page.")
        return

    for i, form in enumerate(forms, 1):
        print(f"\nForm #{i}:")
        print(f"  Action: {form.get('action', 'N/A')}")
        print(f"  Method: {form.get('method', 'GET').upper()}")

        # Find all input fields
        inputs = form.find_all("input")
        if inputs:
            print(f"  Input fields ({len(inputs)}):")
            for inp in inputs:
                name = inp.get("name", "N/A")
                input_type = inp.get("type", "text")
                value = inp.get("value", "")
                print(f"    - {name} (type={input_type}, value={value})")

        # Find select fields
        selects = form.find_all("select")
        if selects:
            print(f"  Select fields ({len(selects)}):")
            for select in selects:
                name = select.get("name", "N/A")
                print(f"    - {name}")


def extract_javascript_files(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract JavaScript file URLs from the page.

    Args:
        soup: BeautifulSoup object of the page.
        base_url: Base URL for resolving relative paths.

    Returns:
        List of absolute JavaScript URLs.
    """
    js_files = []
    scripts = soup.find_all("script", src=True)

    for script in scripts:
        src = script.get("src", "")
        if src:
            absolute_url = urljoin(base_url, src)
            js_files.append(absolute_url)

    return js_files


def search_for_rc4_key(
    js_content: str,
) -> Optional[str]:
    """Search for RC4 encryption key in JavaScript content.

    Args:
        js_content: JavaScript source code.

    Returns:
        RC4 key if found, None otherwise.
    """
    # Common patterns for RC4 keys in JavaScript
    patterns = [
        r'key\s*=\s*["\']([^"\']+)["\']',
        r'rc4[Kk]ey\s*=\s*["\']([^"\']+)["\']',
        r'encryptionKey\s*=\s*["\']([^"\']+)["\']',
        r'password[Kk]ey\s*=\s*["\']([^"\']+)["\']',
        r'secret\s*=\s*["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, js_content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def analyze_javascript_files(
    js_urls: List[str], timeout: float = 10.0
) -> None:
    """Analyze JavaScript files for RC4 encryption logic.

    Args:
        js_urls: List of JavaScript URLs to analyze.
        timeout: Request timeout in seconds. Defaults to 10.0.
    """
    print("\n" + "=" * 70)
    print("JAVASCRIPT ANALYSIS")
    print("=" * 70)

    if not js_urls:
        print("No JavaScript files found.")
        return

    for url in js_urls:
        print(f"\nAnalyzing: {url}")
        response = fetch_page(url, timeout)

        if not response:
            print("  Failed to fetch file.")
            continue

        content = response.text

        # Search for RC4 encryption functions
        if "rc4" in content.lower() or "encrypt" in content.lower():
            print("  Contains encryption-related code")

            # Look for RC4 key
            key = search_for_rc4_key(content)
            if key:
                print(f"  Potential RC4 key found: {key}")

        # Look for authentication-related code
        if "login" in content.lower() or "auth" in content.lower():
            print("  Contains authentication-related code")

        # Show file size
        print(f"  Size: {len(content)} bytes")


def analyze_cookies(response: requests.Response) -> None:
    """Analyze cookies set by the switch.

    Args:
        response: HTTP response from the switch.
    """
    print("\n" + "=" * 70)
    print("COOKIE ANALYSIS")
    print("=" * 70)

    cookies = response.cookies
    if not cookies:
        print("No cookies set by the server.")
        return

    for cookie in cookies:
        print(f"\nCookie: {cookie.name}")
        print(f"  Value: {cookie.value}")
        print(f"  Domain: {cookie.domain}")
        print(f"  Path: {cookie.path}")
        print(f"  Secure: {cookie.secure}")
        print(f"  HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")


def analyze_headers(response: requests.Response) -> None:
    """Analyze HTTP headers from the switch.

    Args:
        response: HTTP response from the switch.
    """
    print("\n" + "=" * 70)
    print("HTTP HEADERS")
    print("=" * 70)

    important_headers = [
        "Server",
        "Set-Cookie",
        "X-Frame-Options",
        "Content-Security-Policy",
        "X-Content-Type-Options",
    ]

    for header in important_headers:
        value = response.headers.get(header)
        if value:
            print(f"{header}: {value}")


def main() -> int:
    """Run reconnaissance on the switch web interface.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Analyze Binardat switch web interface"
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

    base_url = f"http://{args.host}"
    login_url = f"{base_url}/"

    print("=" * 70)
    print("BINARDAT SWITCH WEB INTERFACE RECONNAISSANCE")
    print("=" * 70)
    print(f"Target: {base_url}")
    print(f"Timeout: {args.timeout}s")

    # Fetch the login page
    print(f"\nFetching login page from {login_url}...")
    response = fetch_page(login_url, args.timeout)

    if not response:
        print("Failed to fetch login page. Exiting.")
        return 1

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Analyze different aspects
    analyze_headers(response)
    analyze_cookies(response)
    analyze_login_form(soup, base_url)

    # Extract and analyze JavaScript files
    js_files = extract_javascript_files(soup, base_url)
    if js_files:
        print(f"\nFound {len(js_files)} JavaScript file(s):")
        for js_file in js_files:
            print(f"  - {js_file}")

        analyze_javascript_files(js_files, args.timeout)

    # Save HTML for manual inspection
    output_file = "login_page.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"\nLogin page HTML saved to: {output_file}")

    print("\n" + "=" * 70)
    print("RECONNAISSANCE COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
