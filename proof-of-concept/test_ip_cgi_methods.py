#!/usr/bin/env python3
"""Test different methods to access Manageportip.cgi."""

import json
from switch_auth import SwitchSession

session = SwitchSession("192.168.2.1")
session.login("admin", "admin")

# Access main page first
session.get_page("index.html")
print("[1] Main page accessed\n")

# Try GET with various query strings
test_urls = [
    ("GET", "Manageportip.cgi", None),
    ("GET", "Manageportip.cgi?action=get", None),
    ("GET", "Manageportip.cgi?cmd=get", None),
    ("GET", "Manageportip.cgi?op=query", None),
    ("POST", "Manageportip.cgi", {"action": "get"}),
    ("POST", "Manageportip.cgi", {"cmd": "query"}),
    ("POST", "Manageportip.cgi", {}),
]

for method, url, data in test_urls:
    print(f"[TEST] {method} {url}" + (f" data={data}" if data else ""))
    try:
        if method == "GET":
            response = session.get_page(url)
        else:
            response = session.post_page(url, data or {})

        print(f"  Length: {len(response)} bytes")

        # Try parse as JSON
        try:
            json_data = json.loads(response)
            print(f"  ✓ JSON response:")
            print(f"    {json.dumps(json_data, indent=4)[:200]}...")
        except:
            # Show first line of HTML
            first_line = response.split('\n')[0][:80]
            print(f"  HTML: {first_line}...")

            # Check if it's the error message
            if "password or web privileges" in response:
                print(f"  ✗ Got error message")
            elif len(response) > 1000:
                print(f"  ✓ Substantial content (might be valid!)")

    except Exception as e:
        print(f"  Error: {e}")

    print()

session.close()
