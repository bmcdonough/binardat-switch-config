"""Analyze the Binardat switch menu structure.

This script examines the actual HTML structure used by the switch
and extracts the menu hierarchy with datalink attributes.
"""

import json
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from switch_auth import SwitchSession


def parse_menu_recursive(
    ul_element: Any,
    level: int = 0,
) -> List[Dict[str, Any]]:
    """Recursively parse menu structure from <ul> element.

    Args:
        ul_element: BeautifulSoup <ul> element.
        level: Current nesting level.

    Returns:
        List of menu items with hierarchy.
    """
    items = []

    for li in ul_element.find_all("li", class_="lsm-sidebar-item", recursive=False):
        # Get the direct <a> child
        a_tag = li.find("a", recursive=False)
        if not a_tag:
            continue

        # Get menu label from <span>
        span = a_tag.find("span")
        label = span.get_text(strip=True) if span else "Unknown"

        # Check for datalink attribute (leaf menu item)
        datalink = a_tag.get("datalink", "")

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
            nested_categories = parse_menu_recursive(sub_ul, level + 1)
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
                    sub_datalink = sub_a.get("datalink", "")

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


def analyze_menu_structure() -> None:
    """Analyze and display the Binardat switch menu structure."""
    print("\n" + "=" * 70)
    print("BINARDAT SWITCH MENU STRUCTURE ANALYSIS")
    print("=" * 70)

    # Connect to switch
    session = SwitchSession("192.168.2.1")
    session.login("admin", "admin")
    print("✓ Connected to switch\n")

    # Get main page
    main_html = session.get_main_page()
    soup = BeautifulSoup(main_html, "html.parser")

    # Find the sidebar menu
    sidebar = soup.find("div", class_="lsm-sidebar")
    if not sidebar:
        print("✗ Could not find sidebar menu!")
        return

    # Find the root <ul>
    root_ul = sidebar.find("ul", recursive=False)
    if not root_ul:
        print("✗ Could not find root menu list!")
        return

    # Parse menu structure
    menu_items = parse_menu_recursive(root_ul)

    # Display menu tree
    print("=" * 70)
    print("MENU STRUCTURE")
    print("=" * 70)

    def print_item(item: Dict[str, Any], indent: int = 0) -> None:
        """Print menu item with indentation."""
        prefix = "  " * indent
        if item["type"] == "category":
            print(f"{prefix}📁 {item['label']}")
        else:
            print(f"{prefix}📄 {item['label']} → {item.get('url', 'N/A')}")

        if "children" in item:
            for child in item["children"]:
                print_item(child, indent + 1)

    for item in menu_items:
        print_item(item)

    # Find IP configuration pages
    print("\n" + "=" * 70)
    print("IP CONFIGURATION PAGES")
    print("=" * 70)

    def find_ip_pages(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find all IP-related pages."""
        results = []
        for item in items:
            label_lower = item["label"].lower()
            if "ip" in label_lower or "network" in label_lower:
                results.append(item)
            if "children" in item:
                results.extend(find_ip_pages(item["children"]))
        return results

    ip_pages = find_ip_pages(menu_items)
    for page in ip_pages:
        if page.get("url"):
            print(f"  • {page['label']:30} → {page['url']}")
        else:
            print(f"  • {page['label']:30} [Category]")

    # Save to JSON
    output = {
        "menu_structure": menu_items,
        "ip_pages": ip_pages,
        "total_categories": sum(
            1 for item in menu_items if item["type"] == "category"
        ),
    }

    # Count total pages
    def count_pages(items: List[Dict[str, Any]]) -> int:
        """Count total number of pages."""
        count = sum(1 for item in items if item.get("url"))
        for item in items:
            if "children" in item:
                count += count_pages(item["children"])
        return count

    output["total_pages"] = count_pages(menu_items)

    with open("menu_structure.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total categories:     {output['total_categories']}")
    print(f"Total pages:          {output['total_pages']}")
    print(f"IP-related pages:     {len(ip_pages)}")
    print(f"\nMenu structure saved to: menu_structure.json")
    print("\n✓ Analysis complete!")

    session.close()


if __name__ == "__main__":
    analyze_menu_structure()
