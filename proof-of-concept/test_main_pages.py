#!/usr/bin/env python3
"""Test which main page URL works."""

from bs4 import BeautifulSoup
from switch_auth import SwitchSession

session = SwitchSession("192.168.2.1")
session.login("admin", "admin")

main_urls = [
    "",
    "/",
    "index.html",
    "index.htm",
    "main.html",
    "status.html",
    "index.cgi",
]

for url in main_urls:
    try:
        print(f"\nTrying: {url or '(root)'}")
        html = session.get_page(url) if url else session.session.get(session.base_url).text
        print(f"  Length: {len(html)} bytes")

        soup = BeautifulSoup(html, "html.parser")
        datalinks = soup.find_all("a", attrs={"datalink": True})
        print(f"  Datalinks found: {len(datalinks)}")

        if datalinks:
            print(f"  ✓ THIS ONE HAS THE MENU!")
            # Show first few
            for link in datalinks[:5]:
                label = link.get_text(strip=True)
                url_target = link.get("datalink")
                print(f"     - {label:30s} -> {url_target}")
            break

    except Exception as e:
        print(f"  Error: {e}")

session.close()
