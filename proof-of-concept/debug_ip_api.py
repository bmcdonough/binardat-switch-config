#!/usr/bin/env python3
"""Debug script to understand the IP configuration API."""

import json
import sys
from switch_auth import SwitchSession


def main():
    """Debug the IP configuration API."""
    print("Connecting to switch at 192.168.2.1...")
    session = SwitchSession("192.168.2.1", timeout=30.0)

    try:
        print("Logging in...")
        session.login("admin", "admin")
        print("Login successful!\n")

        # Try to get IP config via the CGI endpoint
        print("=" * 70)
        print("Testing Manageportip.cgi (GET request)...")
        print("=" * 70)
        try:
            response = session.get_page("Manageportip.cgi")
            print(f"Response length: {len(response)} bytes")
            print("\nResponse content:")
            print(response[:500])  # First 500 chars

            # Try to parse as JSON
            try:
                data = json.loads(response)
                print("\n\nParsed as JSON:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print("\n(Not valid JSON)")

        except Exception as e:
            print(f"Error: {e}")

        # Try GetInterfaceIpv4.cgi
        print("\n" + "=" * 70)
        print("Testing GetInterfaceIpv4.cgi...")
        print("=" * 70)
        for endpoint in ["GetInterfaceIpv4.cgi", "getInterfaceIpv4.cgi"]:
            try:
                response = session.get_page(endpoint)
                print(f"\n{endpoint}:")
                print(f"Response length: {len(response)} bytes")
                print(response[:500])

                try:
                    data = json.loads(response)
                    print("\nParsed as JSON:")
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    pass

            except Exception as e:
                print(f"Error with {endpoint}: {e}")

        # Try to get the main page and look for IP configuration
        print("\n" + "=" * 70)
        print("Checking main page menu structure...")
        print("=" * 70)
        try:
            main_html = session.get_page("index.cgi")
            print(f"Main page length: {len(main_html)} bytes")

            # Save for inspection
            with open("debug_main_page.html", "w", encoding="utf-8") as f:
                f.write(main_html)
            print("Main page saved to: debug_main_page.html")

            # Look for datalink attributes related to IP
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(main_html, "html.parser")
            ip_links = soup.find_all("a", attrs={"datalink": True})

            print(f"\nFound {len(ip_links)} menu items with datalink attribute")
            print("\nIP-related menu items:")
            for link in ip_links:
                datalink = link.get("datalink", "")
                label = link.get_text(strip=True)
                if "ip" in datalink.lower() or "ip" in label.lower():
                    print(f"  {label:30s} -> {datalink}")

        except Exception as e:
            print(f"Error: {e}")

    finally:
        session.close()
        print("\nSession closed.")


if __name__ == "__main__":
    sys.exit(main())
