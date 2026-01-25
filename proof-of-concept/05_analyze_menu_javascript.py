"""Analyze JavaScript menu implementation in Binardat switch.

This script logs into the switch and analyzes the JavaScript code to understand
how the menu system is implemented, including event handlers, AJAX calls,
and page loading mechanisms.
"""

import argparse
import json
import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, List, Set

from bs4 import BeautifulSoup
from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


def extract_javascript_content(html: str, session: SwitchSession) -> Dict[str, str]:
    """Extract all JavaScript content from the page.

    Args:
        html: HTML content of the main page.
        session: Authenticated switch session.

    Returns:
        Dictionary mapping source identifiers to JavaScript content.
    """
    print("\n[1] Extracting JavaScript content...")
    soup = BeautifulSoup(html, "html.parser")
    javascript_sources = {}

    # Extract inline scripts
    inline_scripts = soup.find_all("script", src=False)
    for i, script in enumerate(inline_scripts):
        if script.string:
            javascript_sources[f"inline_script_{i}"] = script.string
            print(f"    ✓ Found inline script {i} ({len(script.string)} bytes)")

    # Extract external script URLs
    external_scripts = soup.find_all("script", src=True)
    for i, script in enumerate(external_scripts):
        src = script.get("src", "")
        if src:
            print(f"    • Fetching external script: {src}")
            try:
                js_content = session.get_page(src)
                javascript_sources[f"external_{src}"] = js_content
                print(f"      ✓ Downloaded ({len(js_content)} bytes)")
            except SwitchConnectionError as e:
                print(f"      ✗ Failed to download: {e}")

    print(f"\n    Total JavaScript sources: {len(javascript_sources)}")
    return javascript_sources


def analyze_menu_click_handlers(js_sources: Dict[str, str]) -> Dict[str, Any]:
    """Analyze JavaScript event handlers for menu clicks.

    Args:
        js_sources: Dictionary of JavaScript content.

    Returns:
        Dictionary with analysis results.
    """
    print("\n[2] Analyzing menu click handlers...")
    analysis = {
        "click_handlers": [],
        "event_listeners": [],
        "jquery_selectors": [],
    }

    for source_name, js_content in js_sources.items():
        # Find jQuery click handlers
        # Pattern: $('.selector').click(function() { ... })
        click_pattern = r'\$\(["\']([^"\']+)["\']\)\.click\s*\(\s*function\s*\([^)]*\)\s*\{([^}]+)\}'
        matches = re.finditer(click_pattern, js_content, re.DOTALL)

        for match in matches:
            selector = match.group(1)
            handler_body = match.group(2).strip()

            analysis["click_handlers"].append(
                {
                    "source": source_name,
                    "selector": selector,
                    "handler_snippet": handler_body[:200],
                }
            )
            print(f"    ✓ Found click handler for: {selector}")

        # Find addEventListener calls
        listener_pattern = (
            r'addEventListener\s*\(["\']([^"\']+)["\'],\s*([^,]+),'
        )
        matches = re.finditer(listener_pattern, js_content)

        for match in matches:
            event_type = match.group(1)
            handler_name = match.group(2).strip()

            analysis["event_listeners"].append(
                {
                    "source": source_name,
                    "event_type": event_type,
                    "handler": handler_name,
                }
            )
            print(f"    ✓ Found event listener: {event_type} -> {handler_name}")

        # Find jQuery selectors related to menu/sidebar
        menu_selectors = [
            "lsm-sidebar",
            "menu",
            "navigation",
            "sidebar-item",
            "datalink",
        ]
        for selector in menu_selectors:
            if selector in js_content:
                analysis["jquery_selectors"].append(
                    {"source": source_name, "selector": selector}
                )

    return analysis


def analyze_ajax_calls(js_sources: Dict[str, str]) -> Dict[str, Any]:
    """Analyze AJAX calls and page loading mechanisms.

    Args:
        js_sources: Dictionary of JavaScript content.

    Returns:
        Dictionary with AJAX analysis results.
    """
    print("\n[3] Analyzing AJAX calls and page loading...")
    analysis = {
        "jquery_load_calls": [],
        "jquery_ajax_calls": [],
        "fetch_calls": [],
        "xhr_requests": [],
    }

    for source_name, js_content in js_sources.items():
        # jQuery .load() calls
        # Pattern: $('#selector').load(url)
        load_pattern = r'\$\(["\']([^"\']+)["\']\)\.load\s*\(([^)]+)\)'
        matches = re.finditer(load_pattern, js_content)

        for match in matches:
            target_selector = match.group(1)
            url_expression = match.group(2).strip()

            analysis["jquery_load_calls"].append(
                {
                    "source": source_name,
                    "target": target_selector,
                    "url_expression": url_expression,
                }
            )
            print(f"    ✓ jQuery .load() found: {target_selector} ← {url_expression}")

        # jQuery $.ajax() calls
        ajax_pattern = r'\$\.ajax\s*\(\s*\{([^}]+)\}'
        matches = re.finditer(ajax_pattern, js_content, re.DOTALL)

        for match in matches:
            ajax_config = match.group(1)

            analysis["jquery_ajax_calls"].append(
                {"source": source_name, "config_snippet": ajax_config[:200]}
            )
            print(f"    ✓ jQuery $.ajax() found in {source_name}")

        # Fetch API calls
        fetch_pattern = r'fetch\s*\(["\']([^"\']+)["\']'
        matches = re.finditer(fetch_pattern, js_content)

        for match in matches:
            url = match.group(1)

            analysis["fetch_calls"].append({"source": source_name, "url": url})
            print(f"    ✓ Fetch API call found: {url}")

        # XMLHttpRequest usage
        if "XMLHttpRequest" in js_content:
            analysis["xhr_requests"].append(
                {"source": source_name, "uses_xhr": True}
            )
            print(f"    ✓ XMLHttpRequest usage detected in {source_name}")

    return analysis


def analyze_datalink_handling(js_sources: Dict[str, str]) -> Dict[str, Any]:
    """Analyze how the datalink attribute is used.

    Args:
        js_sources: Dictionary of JavaScript content.

    Returns:
        Dictionary with datalink handling analysis.
    """
    print("\n[4] Analyzing 'datalink' attribute handling...")
    analysis = {
        "datalink_reads": [],
        "datalink_usage_patterns": [],
        "related_functions": [],
    }

    for source_name, js_content in js_sources.items():
        # Pattern: $(this).attr('datalink') or similar
        datalink_read_pattern = (
            r'(\$\([^)]+\)|\w+)\.attr\s*\(["\']datalink["\']\s*\)'
        )
        matches = re.finditer(datalink_read_pattern, js_content)

        for match in matches:
            element_expr = match.group(1)

            analysis["datalink_reads"].append(
                {"source": source_name, "element": element_expr}
            )
            print(f"    ✓ datalink read: {element_expr}")

        # Pattern: getAttribute('datalink')
        get_attr_pattern = r'\.getAttribute\s*\(["\']datalink["\']\)'
        if re.search(get_attr_pattern, js_content):
            analysis["datalink_reads"].append(
                {"source": source_name, "method": "getAttribute"}
            )
            print(f"    ✓ datalink read via getAttribute in {source_name}")

        # Look for functions that handle datalink
        function_pattern = (
            r'function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*datalink[^}]*\}'
        )
        matches = re.finditer(function_pattern, js_content, re.DOTALL)

        for match in matches:
            function_name = match.group(1)

            analysis["related_functions"].append(
                {"source": source_name, "function": function_name}
            )
            print(f"    ✓ Function using datalink: {function_name}()")

    return analysis


def extract_menu_interaction_patterns(
    js_sources: Dict[str, str],
) -> Dict[str, Any]:
    """Extract patterns for menu interaction.

    Args:
        js_sources: Dictionary of JavaScript content.

    Returns:
        Dictionary with menu interaction patterns.
    """
    print("\n[5] Extracting menu interaction patterns...")
    patterns = {
        "expand_collapse": [],
        "active_state": [],
        "navigation_flow": [],
    }

    for source_name, js_content in js_sources.items():
        # Look for expand/collapse patterns (toggleClass, addClass, removeClass)
        expand_pattern = r'(toggleClass|addClass|removeClass)\s*\(["\']([^"\']+)["\']\)'
        matches = re.finditer(expand_pattern, js_content)

        for match in matches:
            method = match.group(1)
            class_name = match.group(2)

            # Filter for menu-related classes
            if any(
                keyword in class_name.lower()
                for keyword in ["open", "active", "expand", "show", "collapsed"]
            ):
                patterns["expand_collapse"].append(
                    {
                        "source": source_name,
                        "method": method,
                        "class": class_name,
                    }
                )
                print(f"    ✓ Expand/collapse: {method}('{class_name}')")

        # Look for active state management
        if "active" in js_content.lower():
            active_patterns = re.finditer(
                r'["\']([^"\']*active[^"\']*)["\']', js_content, re.IGNORECASE
            )
            for match in active_patterns:
                class_name = match.group(1)
                if class_name not in [
                    p["class"] for p in patterns["active_state"]
                ]:
                    patterns["active_state"].append(
                        {"source": source_name, "class": class_name}
                    )

    return patterns


def generate_javascript_documentation(
    click_handlers: Dict[str, Any],
    ajax_calls: Dict[str, Any],
    datalink_handling: Dict[str, Any],
    interaction_patterns: Dict[str, Any],
    output_file: Path,
) -> None:
    """Generate documentation file for JavaScript findings.

    Args:
        click_handlers: Click handler analysis results.
        ajax_calls: AJAX call analysis results.
        datalink_handling: Datalink handling analysis.
        interaction_patterns: Menu interaction patterns.
        output_file: Path to output documentation file.
    """
    print(f"\n[6] Generating documentation: {output_file}")

    content = """# Binardat Switch - JavaScript Menu System Analysis

**Date:** 2026-01-25
**Script:** `proof-of-concept/05_analyze_menu_javascript.py`

## Executive Summary

This document analyzes the JavaScript implementation of the Binardat switch's menu system,
documenting how menu clicks are handled, pages are loaded, and navigation is implemented.

## Menu System Architecture

### Technology Stack

- **jQuery 3.5.1** - DOM manipulation and AJAX calls
- **Custom navigation system** - `datalink` attribute-based routing
- **Single Page Application (SPA)** - Pages loaded dynamically without full page refresh

### Core Navigation Flow

```
User clicks menu item
    ↓
jQuery click handler fires
    ↓
Extract 'datalink' attribute value
    ↓
jQuery .load() fetches page content
    ↓
Content injected into #appMainInner div
    ↓
Page displays without full refresh
```

## Click Handler Analysis

"""

    # Document click handlers
    if click_handlers["click_handlers"]:
        content += f"""### Detected Click Handlers

Found {len(click_handlers['click_handlers'])} click handler(s):

"""
        for i, handler in enumerate(click_handlers["click_handlers"], 1):
            content += f"""**Handler {i}:**
- **Source:** `{handler['source']}`
- **Selector:** `{handler['selector']}`
- **Code snippet:**
  ```javascript
  {handler['handler_snippet']}...
  ```

"""

    # Document jQuery selectors
    if click_handlers["jquery_selectors"]:
        unique_selectors = {
            s["selector"] for s in click_handlers["jquery_selectors"]
        }
        content += f"""### Menu-Related jQuery Selectors

The following menu-related selectors were found:
{chr(10).join(f'- `{s}`' for s in sorted(unique_selectors))}

"""

    # Document AJAX patterns
    content += f"""## AJAX and Page Loading

### jQuery .load() Calls

Found {len(ajax_calls['jquery_load_calls'])} jQuery .load() call(s):

"""
    if ajax_calls["jquery_load_calls"]:
        for i, call in enumerate(ajax_calls["jquery_load_calls"], 1):
            content += f"""**Load Call {i}:**
- **Source:** `{call['source']}`
- **Target element:** `{call['target']}`
- **URL expression:** `{call['url_expression']}`

"""

    if ajax_calls["jquery_ajax_calls"]:
        content += f"""### jQuery $.ajax() Calls

Found {len(ajax_calls['jquery_ajax_calls'])} jQuery $.ajax() call(s).
These are typically used for form submissions or API calls.

"""

    if ajax_calls["fetch_calls"]:
        content += f"""### Fetch API Calls

Found {len(ajax_calls['fetch_calls'])} Fetch API call(s):

"""
        for call in ajax_calls["fetch_calls"]:
            content += f"- **{call['url']}** (in `{call['source']}`)\n"

    # Document datalink handling
    content += f"""## 'datalink' Attribute Handling

The Binardat switch uses a custom `datalink` attribute instead of standard `href` attributes.

### Datalink Reads

Found {len(datalink_handling['datalink_reads'])} location(s) where the `datalink` attribute is read:

"""
    for read in datalink_handling["datalink_reads"]:
        if "element" in read:
            content += f"- `{read['element']}.attr('datalink')` in `{read['source']}`\n"
        else:
            content += f"- `getAttribute('datalink')` in `{read['source']}`\n"

    if datalink_handling["related_functions"]:
        content += f"""
### Related Functions

The following functions reference the `datalink` attribute:

"""
        for func in datalink_handling["related_functions"]:
            content += f"- `{func['function']}()` in `{func['source']}`\n"

    # Document interaction patterns
    content += """
## Menu Interaction Patterns

### Expand/Collapse Mechanism

"""
    if interaction_patterns["expand_collapse"]:
        content += f"Found {len(interaction_patterns['expand_collapse'])} expand/collapse pattern(s):\n\n"
        for pattern in interaction_patterns["expand_collapse"]:
            content += f"- `{pattern['method']}('{pattern['class']}')` in `{pattern['source']}`\n"
    else:
        content += "No explicit expand/collapse patterns detected.\n"

    if interaction_patterns["active_state"]:
        content += f"""
### Active State Management

The following CSS classes are used to indicate active menu items:

"""
        unique_classes = {p["class"] for p in interaction_patterns["active_state"]}
        for class_name in sorted(unique_classes):
            content += f"- `{class_name}`\n"

    # Add implementation recommendations
    content += """
## Implementation Recommendations

### 1. Programmatic Navigation

To programmatically navigate to a page:

```python
def navigate_to_page(session: SwitchSession, page_url: str) -> str:
    \"\"\"Navigate to a specific page using direct URL access.

    Args:
        session: Authenticated switch session.
        page_url: The page URL (e.g., 'Manageportip.cgi').

    Returns:
        HTML content of the page.
    \"\"\"
    return session.get_page(page_url)
```

**Note:** Since pages are loaded via AJAX in the browser, we can access them
directly via GET requests when using the session.

### 2. Menu Simulation

If we need to simulate the full menu interaction:

```python
# 1. Get the main page to establish session
main_html = session.get_main_page()

# 2. Direct page access (simpler, recommended)
page_html = session.get_page("Manageportip.cgi")

# 3. Parse and interact with the page content
soup = BeautifulSoup(page_html, "html.parser")
# ... work with the page
```

### 3. CSRF Token Handling

Check if pages require CSRF tokens:

```python
# Look for hidden input fields with CSRF tokens
csrf_token = soup.find("input", {"name": "csrf_token"})
if csrf_token:
    token_value = csrf_token.get("value")
    # Include in form submissions
```

## Key Findings Summary

1. **Navigation Method:** jQuery-based SPA with `.load()` for page content injection
2. **Custom Attribute:** Uses `datalink` instead of `href` for menu items
3. **AJAX Pattern:** Content loaded into `#appMainInner` container
4. **Direct Access:** Pages can be accessed directly via GET requests (no need to simulate clicks)
5. **Session Management:** Authentication session persists across AJAX requests

## Next Steps

1. **Form Analysis:** Analyze the IP configuration form structure in `Manageportip.cgi`
2. **Submission Testing:** Test form submissions and identify required fields
3. **Response Handling:** Document success/error response formats
4. **Verification:** Implement post-change verification methods

## References

- `proof-of-concept/switch_auth.py` - Session management
- `docs/menu-structure-findings.md` - HTML menu structure documentation
- `proof-of-concept/02_test_login.py` - Authentication testing

## Changelog

- **2026-01-25**: Initial JavaScript menu system analysis
"""

    output_file.write_text(content, encoding="utf-8")
    print(f"    ✓ Documentation written")


def save_analysis_json(
    click_handlers: Dict[str, Any],
    ajax_calls: Dict[str, Any],
    datalink_handling: Dict[str, Any],
    interaction_patterns: Dict[str, Any],
    output_file: Path,
) -> None:
    """Save analysis results to JSON file.

    Args:
        click_handlers: Click handler analysis results.
        ajax_calls: AJAX call analysis results.
        datalink_handling: Datalink handling analysis.
        interaction_patterns: Menu interaction patterns.
        output_file: Path to output JSON file.
    """
    print(f"\n[7] Saving analysis JSON: {output_file}")

    analysis = {
        "click_handlers": click_handlers,
        "ajax_calls": ajax_calls,
        "datalink_handling": datalink_handling,
        "interaction_patterns": interaction_patterns,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print("    ✓ JSON analysis saved")


def main() -> int:
    """Run JavaScript menu analysis.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Analyze JavaScript menu implementation in Binardat switch"
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
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--output-doc",
        default="../docs/javascript-menu-analysis.md",
        help="Output documentation file (default: ../docs/javascript-menu-analysis.md)",
    )
    parser.add_argument(
        "--output-json",
        default="menu_javascript_analysis.json",
        help="Output JSON file (default: menu_javascript_analysis.json)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("BINARDAT SWITCH - JAVASCRIPT MENU ANALYSIS")
    print("=" * 70)

    # Prompt for credentials if not provided
    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    try:
        # Create and authenticate session
        print(f"\nConnecting to {args.host}...")
        with SwitchSession(args.host, args.timeout) as session:
            session.login(username, password)
            print(f"✓ Authenticated (RC4 key: {session.rc4_key})")

            # Fetch main page
            print("\nFetching main page...")
            main_html = session.get_main_page()
            print(f"✓ Main page fetched ({len(main_html)} bytes)")

            # Extract all JavaScript content
            js_sources = extract_javascript_content(main_html, session)

            # Analyze click handlers
            click_handlers = analyze_menu_click_handlers(js_sources)

            # Analyze AJAX calls
            ajax_calls = analyze_ajax_calls(js_sources)

            # Analyze datalink handling
            datalink_handling = analyze_datalink_handling(js_sources)

            # Extract interaction patterns
            interaction_patterns = extract_menu_interaction_patterns(js_sources)

            # Generate documentation
            doc_path = Path(args.output_doc)
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            generate_javascript_documentation(
                click_handlers,
                ajax_calls,
                datalink_handling,
                interaction_patterns,
                doc_path,
            )

            # Save JSON analysis
            json_path = Path(args.output_json)
            save_analysis_json(
                click_handlers,
                ajax_calls,
                datalink_handling,
                interaction_patterns,
                json_path,
            )

            # Display summary
            print("\n" + "=" * 70)
            print("ANALYSIS COMPLETE")
            print("=" * 70)
            print(f"Click handlers found:    {len(click_handlers['click_handlers'])}")
            print(f"AJAX load calls found:   {len(ajax_calls['jquery_load_calls'])}")
            print(f"Datalink reads found:    {len(datalink_handling['datalink_reads'])}")
            print(f"Documentation saved to:  {doc_path.absolute()}")
            print(f"JSON analysis saved to:  {json_path.absolute()}")

            return 0

    except SwitchAuthError as e:
        print(f"\n✗ Authentication error: {e}")
        return 1

    except SwitchConnectionError as e:
        print(f"\n✗ Connection error: {e}")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
