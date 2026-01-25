#!/usr/bin/env python3
"""Debug script to investigate IP configuration page structure."""

import sys
from bs4 import BeautifulSoup
from switch_auth import SwitchSession


def main():
    """Debug the IP configuration page."""
    # Connect and login
    print("Connecting to switch at 192.168.2.1...")
    session = SwitchSession("192.168.2.1", timeout=30.0)

    try:
        print("Logging in...")
        session.login("admin", "admin")
        print("Login successful!\n")

        # Try the documented IP config page directly
        print("=" * 70)
        print("Fetching Manageportip.cgi (documented IP config page)...")
        print("=" * 70)
        try:
            html = session.get_page("Manageportip.cgi")
            print(f"\nPage fetched successfully! Length: {len(html)} bytes\n")

            # Parse and display forms
            soup = BeautifulSoup(html, "html.parser")
            forms = soup.find_all("form")
            print(f"Found {len(forms)} form(s) on the page\n")

            for idx, form in enumerate(forms, 1):
                print(f"Form {idx}:")
                print(f"  Action: {form.get('action', '(none)')}")
                print(f"  Method: {form.get('method', 'GET')}")
                print(f"  Inputs:")

                inputs = form.find_all("input")
                for inp in inputs:
                    name = inp.get("name", "(no name)")
                    inp_type = inp.get("type", "text")
                    value = inp.get("value", "")
                    print(f"    - {name:25s} type={inp_type:10s} value='{value}'")
                print()

            # Look for any text containing "ip"
            print("=" * 70)
            print("Searching for IP-related fields...")
            print("=" * 70)

            all_inputs = soup.find_all("input")
            ip_related = [
                inp for inp in all_inputs
                if "ip" in inp.get("name", "").lower()
                or "mask" in inp.get("name", "").lower()
                or "gateway" in inp.get("name", "").lower()
            ]

            if ip_related:
                print(f"\nFound {len(ip_related)} IP-related input fields:")
                for inp in ip_related:
                    name = inp.get("name", "(no name)")
                    inp_type = inp.get("type", "text")
                    value = inp.get("value", "")
                    print(f"  {name:30s} = '{value}' (type: {inp_type})")
            else:
                print("\nNo IP-related input fields found!")

            # Save HTML for manual inspection
            output_file = "debug_ip_config_page.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n[SAVED] Full HTML saved to: {output_file}")

        except Exception as e:
            print(f"Error fetching Manageportip.cgi: {e}")

        # Try the navigation method
        print("\n" + "=" * 70)
        print("Testing navigate_to_ip_config() method...")
        print("=" * 70)
        try:
            html = session.navigate_to_ip_config()
            print(f"Success! Length: {len(html)} bytes")
        except Exception as e:
            print(f"Failed: {e}")

    finally:
        session.close()
        print("\nSession closed.")


if __name__ == "__main__":
    sys.exit(main())
