#!/usr/bin/env python3
"""Test accessing IP config page after accessing main page."""

import json
from bs4 import BeautifulSoup
from switch_auth import SwitchSession

print("=" * 70)
print("Testing IP Configuration Page Access Sequence")
print("=" * 70)

session = SwitchSession("192.168.2.1")
session.login("admin", "admin")
print("\n[1] Logged in successfully\n")

# Step 1: Access main page first
print("[2] Accessing main page (index.html)...")
main_html = session.get_page("index.html")
print(f"    Main page loaded: {len(main_html)} bytes\n")

# Step 2: Now try to access Manageportip.cgi
print("[3] Accessing Manageportip.cgi...")
ip_page = session.get_page("Manageportip.cgi")
print(f"    Page loaded: {len(ip_page)} bytes")
print(f"    Content preview:\n{ip_page[:500]}\n")

# Try to parse as JSON
try:
    data = json.loads(ip_page)
    print("[4] Successfully parsed as JSON:")
    print(json.dumps(data, indent=2))
except json.JSONDecodeError:
    print("[4] Not JSON, analyzing HTML...")
    soup = BeautifulSoup(ip_page, "html.parser")

    # Look for forms
    forms = soup.find_all("form")
    print(f"    Forms found: {len(forms)}")

    # Look for inputs
    inputs = soup.find_all("input")
    print(f"    Input fields found: {len(inputs)}\n")

    if inputs:
        print("    Input fields:")
        for inp in inputs[:10]:
            name = inp.get("name", "(no name)")
            inp_type = inp.get("type", "text")
            value = inp.get("value", "")
            print(f"      - {name:30s} type={inp_type:10s} value='{value}'")

session.close()
