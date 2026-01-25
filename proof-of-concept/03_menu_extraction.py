"""Extract and document menu structure from Binardat switch.

This script authenticates to the switch and systematically discovers
the menu structure by analyzing HTML navigation elements and JavaScript
menu definitions. Outputs a JSON file with the complete menu hierarchy.
"""

import argparse
import json
import sys
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


def parse_binardat_menu_recursive(
    ul_element: Any,
    level: int = 0,
) -> List[Dict[str, Any]]:
    """Recursively parse Binardat menu structure from <ul> element.

    The Binardat switch uses a custom menu system with 'datalink' attributes
    instead of standard 'href' attributes.

    Args:
        ul_element: BeautifulSoup <ul> element.
        level: Current nesting level.

    Returns:
        List of menu items with hierarchy.
    """
    from bs4 import Tag

    items = []

    for li in ul_element.find_all("li", class_="lsm-sidebar-item", recursive=False):
        # Get the direct <a> child
        a_tag = li.find("a", recursive=False)
        if not a_tag:
            continue

        # Get menu label from <span>
        span = a_tag.find("span")
        label = span.get_text(strip=True) if span else "Unknown"

        # Check for datalink attribute (Binardat-specific)
        datalink_attr = a_tag.get("datalink", "")
        datalink = str(datalink_attr) if datalink_attr else ""

        item: Dict[str, Any] = {
            "label": label,
            "level": level,
        }

        if datalink:
            item["url"] = datalink
            item["type"] = "page"
        else:
            item["type"] = "category"

        # Look for submenu
        sub_ul = li.find("ul", recursive=False)
        if sub_ul:
            # Parse both category items and leaf items
            children = []

            # Parse nested categories
            nested_categories = parse_binardat_menu_recursive(sub_ul, level + 1)
            children.extend(nested_categories)

            # Parse direct leaf items (non-category)
            for sub_li in sub_ul.find_all("li", recursive=False):
                # Skip if it's a category (has class lsm-sidebar-item)
                if "lsm-sidebar-item" in sub_li.get("class", []):
                    continue

                sub_a = sub_li.find("a")
                if sub_a:
                    sub_span = sub_a.find("span")
                    sub_label = (
                        sub_span.get_text(strip=True) if sub_span else "Unknown"
                    )
                    sub_datalink_attr = sub_a.get("datalink", "")
                    sub_datalink = (
                        str(sub_datalink_attr) if sub_datalink_attr else ""
                    )

                    if sub_datalink:
                        children.append(
                            {
                                "label": sub_label,
                                "url": sub_datalink,
                                "type": "page",
                                "level": level + 1,
                            }
                        )

            if children:
                item["children"] = children

        items.append(item)

    return items


def extract_menu_structure(
    host: str,
    username: str,
    password: str,
    output_file: str = "menu_structure.json",
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Extract menu structure from the switch.

    Args:
        host: Switch IP address or hostname.
        username: Switch username.
        password: Switch password.
        output_file: Path to output JSON file.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        Dictionary with menu structure.

    Raises:
        SwitchAuthError: If authentication fails.
        SwitchConnectionError: If unable to connect.
    """
    print("\n" + "=" * 70)
    print("BINARDAT SWITCH MENU EXTRACTION")
    print("=" * 70)
    print(f"Host:     {host}")
    print(f"Username: {username}")
    print(f"Output:   {output_file}")

    # Create session
    print("\n[1] Creating session and authenticating...")
    with SwitchSession(host, timeout) as session:
        session.login(username, password)
        print(f"    ✓ Authenticated (RC4 key: {session.rc4_key})")

        # Fetch main page
        print("\n[2] Fetching main page...")
        try:
            main_html = session.get_main_page()
            print("    ✓ Main page fetched ({} bytes)".format(len(main_html)))
        except SwitchConnectionError as e:
            print("    ✗ Failed to fetch main page: {}".format(e))
            raise

        # Extract navigation using Binardat-specific parser
        print("\n[3] Analyzing HTML navigation structure...")
        print("    Using Binardat-specific parser (datalink attributes)")

        soup = BeautifulSoup(main_html, "html.parser")

        # Find the Binardat sidebar menu
        sidebar = soup.find("div", class_="lsm-sidebar")
        if not sidebar:
            print("    ✗ Could not find lsm-sidebar div")
            print("    Falling back to generic extraction...")
            nav_items = session.extract_navigation(main_html)
        else:
            root_ul = sidebar.find("ul", recursive=False)
            if not root_ul:
                print("    ✗ Could not find root menu list")
                nav_items = []
            else:
                # Parse the Binardat menu structure
                menu_items = parse_binardat_menu_recursive(root_ul)

                # Flatten to get all pages
                def flatten_menu(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                    """Flatten menu structure to list of pages."""
                    result = []
                    for item in items:
                        if item.get("url"):
                            result.append(item)
                        if "children" in item:
                            result.extend(flatten_menu(item["children"]))
                    return result

                nav_items = flatten_menu(menu_items)
                print(f"    ✓ Found {len(nav_items)} navigation items")

                if nav_items:
                    print("\n    Sample navigation items:")
                    for item in nav_items[:10]:  # Show first 10
                        label = item.get("label", "")
                        url = item.get("url", "")
                        level = item.get("level", 0)
                        indent = "  " * level
                        print(f"      {indent}- {label:30} → {url}")
                    if len(nav_items) > 10:
                        print(f"      ... and {len(nav_items) - 10} more")

        # Store as all_pages for compatibility
        all_pages = nav_items
        print("\n[4] Total pages discovered: {}".format(len(all_pages)))

        # Categorize discovered pages
        print("\n[5] Categorizing pages...")
        categories: Dict[str, int] = {}
        for page in all_pages:
            url = page["url"].lower()
            label = page.get("label", "").lower()

            # Determine category
            category = "other"
            if "network" in url or "network" in label or "ip" in url:
                category = "network"
            elif "system" in url or "system" in label:
                category = "system"
            elif "port" in url or "port" in label:
                category = "port"
            elif "vlan" in url or "vlan" in label:
                category = "vlan"
            elif "status" in url or "status" in label or "info" in url:
                category = "status"
            elif "security" in url or "security" in label or "user" in url:
                category = "security"
            elif (
                "monitor" in url
                or "monitor" in label
                or "statistics" in url
                or "stats" in url
            ):
                category = "monitoring"
            elif "config" in url or "config" in label or "setting" in url:
                category = "config"

            page["category"] = category
            categories[category] = categories.get(category, 0) + 1

        print("    Categories found:")
        for cat, count in sorted(categories.items()):
            print(f"      - {cat:20} : {count:3} pages")

        # Build hierarchical menu structure
        print("\n[6] Building menu hierarchy...")
        menu_structure = session.build_menu_structure(all_pages)
        print("    ✓ Menu structure built")

        # Add metadata
        menu_structure["metadata"] = {
            "switch_host": host,
            "extraction_method": "html_and_javascript",
            "total_items": len(all_pages),
            "categories": categories,
        }

        # Flatten list of all pages for reference
        menu_structure["all_pages"] = sorted(
            all_pages, key=lambda x: x.get("url", "")
        )

        # Save to JSON file
        print(f"\n[7] Saving to {output_file}...")
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(menu_structure, f, indent=2, ensure_ascii=False)
        print("    ✓ Menu structure saved")

        # Display summary
        print("\n" + "=" * 70)
        print("EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"Total pages discovered: {len(all_pages)}")
        print(f"Menu categories:        {len(menu_structure['menu'])}")
        print(f"Output file:            {output_path.absolute()}")

        return menu_structure


def display_menu_tree(menu_structure: Dict[str, Any]) -> None:
    """Display menu structure as a tree.

    Args:
        menu_structure: Menu structure dictionary.
    """
    print("\n" + "=" * 70)
    print("MENU TREE")
    print("=" * 70)

    for category in menu_structure.get("menu", []):
        cat_label = category.get("label", "Unknown")
        children = category.get("children", [])

        print(f"\n{cat_label} ({len(children)} items)")
        print("-" * 70)

        for child in children:
            label = child.get("label", "")
            url = child.get("url", "")
            item_type = child.get("type", "link")

            print(f"  ├─ {label:30} → {url:35} [{item_type}]")


def search_menu(
    menu_structure: Dict[str, Any],
    search_term: str,
) -> None:
    """Search menu structure for specific terms.

    Args:
        menu_structure: Menu structure dictionary.
        search_term: Term to search for.
    """
    print("\n" + "=" * 70)
    print(f"SEARCH RESULTS: '{search_term}'")
    print("=" * 70)

    search_lower = search_term.lower()
    results = []

    for page in menu_structure.get("all_pages", []):
        label = page.get("label", "").lower()
        url = page.get("url", "").lower()

        if search_lower in label or search_lower in url:
            results.append(page)

    if results:
        print(f"\nFound {len(results)} matching pages:\n")
        for page in results:
            label = page.get("label", "")
            url = page.get("url", "")
            category = page.get("category", "unknown")
            print(f"  [{category:10}] {label:30} → {url}")
    else:
        print("\nNo pages found matching search term.")


def main() -> int:
    """Run menu extraction.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Extract menu structure from Binardat switch"
    )
    parser.add_argument(
        "--host",
        default="192.168.2.1",
        help="Switch IP address (default: 192.168.2.1)",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Switch username (will prompt if not provided)",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Switch password (will prompt if not provided)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="menu_structure.json",
        help="Output JSON file (default: menu_structure.json)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--display-tree",
        action="store_true",
        help="Display menu tree after extraction",
    )
    parser.add_argument(
        "--search",
        help="Search for specific term in menu (after extraction)",
    )
    args = parser.parse_args()

    # Prompt for credentials if not provided
    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    try:
        # Extract menu structure
        menu_structure = extract_menu_structure(
            args.host,
            username,
            password,
            args.output,
            args.timeout,
        )

        # Optional: Display menu tree
        if args.display_tree:
            display_menu_tree(menu_structure)

        # Optional: Search menu
        if args.search:
            search_menu(menu_structure, args.search)

        return 0

    except SwitchAuthError as e:
        print(f"\n✗ Authentication error: {e}")
        print("\nPossible causes:")
        print("  - Incorrect username or password")
        print("  - Insufficient permissions")
        return 1

    except SwitchConnectionError as e:
        print(f"\n✗ Connection error: {e}")
        print("\nPossible causes:")
        print("  - Switch is not reachable")
        print("  - Incorrect IP address")
        print("  - Network connectivity issues")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
