# Binardat Switch Menu System - Implementation Guide

**Date:** 2026-01-25
**Switch Model:** Binardat 2G20-16410GSM
**Switch IP:** 192.168.2.1
**Scripts:** `proof-of-concept/03_menu_extraction.py`, `proof-of-concept/05_analyze_menu_javascript.py`

## Executive Summary

This document provides technical details of how the Binardat switch's menu system works, including HTML structure, JavaScript implementation, and programmatic access methods. The switch uses a jQuery-based Single Page Application (SPA) with custom `datalink` attributes for navigation.

## System Architecture

### Technology Stack

- **jQuery 3.5.1** - DOM manipulation and AJAX calls
- **Custom navigation system** - `datalink` attribute-based routing
- **Single Page Application (SPA)** - Pages loaded dynamically without full page refresh
- **AJAX content loading** - Pages injected into `#appMainInner` container

### JavaScript File Inventory

| File | Size | Purpose |
|------|------|---------|
| `/js/jquery-3.5.1.min.js` | 89 KB | jQuery library for DOM manipulation and AJAX |
| `/js/utility.js` | 34 KB | **Core menu navigation logic**, datalink handling, form utilities |
| `/js/jquery.dataTables.min.js` | 88 KB | Table rendering and pagination for monitoring pages |
| `/js/dialog-plus-min.js` | 13 KB | Modal dialog system for confirmations and alerts |
| `/js/jquery.slimscroll.min.js` | 5 KB | Custom scrollbar for menu sidebar |
| `/js/tooltip.js` | 2 KB | Tooltip display for UI elements |
| Inline scripts (4) | ~12 KB | Page-specific logic, event handlers, initialization |

**Key File:** `/js/utility.js` contains:
- `reCurrentWeb()` function - Core menu navigation handler
- Datalink click handlers
- HTTP POST/GET helper functions
- Form utilities
- RC4 encryption (for authentication)

## HTML Menu Structure

### Menu Hierarchy

The menu is structured as a hierarchical list using semantic HTML:

```html
<div class="lsm-sidebar">
  <ul class="sidebar-menu">
    <li class="sidebar-item">
      <a class="has-arrow">
        <span>Category Name</span>
      </a>
      <ul class="submenu">
        <li>
          <a datalink="page.cgi">
            <span>Page Name</span>
          </a>
        </li>
        <!-- More pages -->
      </ul>
    </li>
    <!-- More categories -->
  </ul>
</div>
```

### Key HTML Attributes

**`datalink` Attribute:**
- Custom attribute used instead of standard `href`
- Contains the URL of the page to load
- Read by JavaScript click handlers in `utility.js`
- Example: `<a datalink="Manageportip.cgi">`

**CSS Classes:**
- `lsm-sidebar` - Main sidebar container
- `sidebar-menu` - Top-level menu list
- `sidebar-item` - Menu category item
- `has-arrow` - Indicates expandable category
- `submenu` - Nested page list
- `active` - Currently selected menu item
- `lsm-sidebar-show` - Expanded category state

### Menu Categories

The switch organizes pages into ~10 categories:

| Category | Typical Pages |
|----------|---------------|
| Network | IP config, DHCP, routing, DNS |
| Port | Port settings, statistics, mirroring |
| VLAN | VLAN configuration, membership |
| System | Admin, firmware, backup, reboot |
| Status | Dashboard, port status, system info |
| Security | ACL, users, authentication |
| Monitoring | Logs, statistics, traffic analysis |
| QoS | Quality of Service settings |
| IGMP | Multicast configuration |
| Other | Miscellaneous features |

## JavaScript Navigation Implementation

### Core Navigation Flow

```
User clicks menu item
    ↓
jQuery click handler fires (in utility.js)
    ↓
Extract 'datalink' attribute value
    ↓
jQuery .load() or $.ajax() fetches page content
    ↓
Content injected into #appMainInner div
    ↓
Page displays without full refresh
    ↓
Menu item marked as 'active'
```

### Click Handler Analysis

The switch uses jQuery event handlers attached to elements with `datalink` attributes:

**Primary Handler (in utility.js):**
```javascript
$('[datalink]').on('click', function() {
    var url = $(this).attr('datalink');
    reCurrentWeb(url);
});
```

**`reCurrentWeb()` Function:**
This is the core navigation function in `utility.js`:
```javascript
function reCurrentWeb(url) {
    // Remove active class from all menu items
    $('.sidebar-menu a').removeClass('active');

    // Add active class to clicked item
    $('[datalink="' + url + '"]').addClass('active');

    // Load page content via AJAX
    $('#appMainInner').load(url, function(response, status, xhr) {
        if (status == "error") {
            console.log("Error loading page: " + url);
        }
    });
}
```

### Additional Click Handlers

Found 5 specialized click handlers for system operations:

| Selector | Purpose | Endpoint |
|----------|---------|----------|
| `#statusToggle` | Show/hide status panel | N/A (UI only) |
| `#logout` | Logout user | `syscmd.cgi?cmd=logout` |
| `#save` | Save configuration | `syscmd.cgi?cmd=save` |
| `#reset` | Factory reset | Confirmation dialog → reset command |
| `#reboot` | Reboot switch | Confirmation dialog → reboot command |

### Menu Expand/Collapse Mechanism

The menu uses CSS classes to manage category expansion:

**Expand Category:**
```javascript
$('.sidebar-item').addClass('lsm-sidebar-show');
```

**Collapse Category:**
```javascript
$('.sidebar-item').removeClass('lsm-sidebar-show');
```

**Active State:**
```javascript
// Mark menu item as selected
$('.sidebar-menu a').removeClass('active');
$(clickedElement).addClass('active');
```

## Programmatic Access Methods

### Method 1: Direct Page Access (Recommended)

**Advantages:**
- Simpler implementation
- No need to simulate menu clicks
- Works with authenticated session
- Bypasses JavaScript entirely

**Python Implementation:**
```python
from switch_auth import SwitchSession

# Authenticate
session = SwitchSession("192.168.2.1")
session.login("admin", "admin")

# Navigate directly to any page using its datalink URL
page_html = session.get_page("Manageportip.cgi")

# No menu simulation required
```

**Critical Finding:** Since the switch loads pages via AJAX, all pages are accessible
via direct GET requests as long as we have an authenticated session cookie.

### Method 2: Menu Structure Discovery

**Use Case:** When you need to discover all available pages

**Python Implementation:**
```python
from bs4 import BeautifulSoup

# Get main page with menu structure
main_html = session.get_main_page()
soup = BeautifulSoup(main_html, "html.parser")

# Find all menu items with datalink attributes
menu_items = soup.find_all("a", attrs={"datalink": True})

# Build menu structure
menu_structure = {}
for item in menu_items:
    label = item.find("span")
    if label:
        label_text = label.get_text(strip=True)
        url = item.get("datalink")
        menu_structure[label_text] = url
        print(f"{label_text} → {url}")

# Access any discovered page
for label, url in menu_structure.items():
    if "ip" in label.lower():
        print(f"Found IP config: {url}")
        ip_page = session.get_page(url)
```

### Method 3: Form Interaction

**Use Case:** Submitting configuration changes

**Python Implementation:**
```python
# Get configuration page
page_html = session.get_page("Manageportip.cgi")
soup = BeautifulSoup(page_html, "html.parser")

# Find the form
form = soup.find("form")
if not form:
    raise ValueError("No form found on page")

# Extract form action (submission URL)
action = form.get("action", "Manageportip.cgi")

# Extract all form fields (including hidden fields)
form_data = {}
for input_field in form.find_all("input"):
    name = input_field.get("name")
    value = input_field.get("value", "")
    if name:
        form_data[name] = value

# Also get select/option values
for select in form.find_all("select"):
    name = select.get("name")
    selected = select.find("option", selected=True)
    if name and selected:
        form_data[name] = selected.get("value", "")

# Modify configuration values
form_data["ip_address"] = "192.168.100.50"
form_data["netmask"] = "255.255.255.0"
form_data["gateway"] = "192.168.100.1"

# Submit form via POST
response = session.post_page(action, form_data)

# Check response
if "success" in response.lower() or response.status_code == 200:
    print("Configuration updated successfully")
```

## Automated Menu Extraction

### Extraction Script Usage

The `03_menu_extraction.py` script automates menu discovery:

**Basic Extraction:**
```bash
cd proof-of-concept
python 03_menu_extraction.py -u admin -p admin
```

**With Tree Display:**
```bash
python 03_menu_extraction.py -u admin -p admin --display-tree
```

**Search for Specific Pages:**
```bash
python 03_menu_extraction.py -u admin -p admin --search "ip"
```

**Custom Output Location:**
```bash
python 03_menu_extraction.py -u admin -p admin -o ../docs/menu_structure.json
```

### JSON Output Format

The script generates `menu_structure.json`:

```json
{
  "metadata": {
    "switch_host": "192.168.2.1",
    "extraction_method": "html_and_javascript",
    "extraction_date": "2026-01-25",
    "total_items": 168,
    "categories": {
      "network": 15,
      "system": 20,
      "port": 25,
      "vlan": 12,
      "status": 10,
      "security": 18,
      "monitoring": 22,
      "qos": 14,
      "igmp": 8,
      "other": 24
    }
  },
  "menu": [
    {
      "id": "network",
      "label": "Network Configuration",
      "children": [
        {
          "label": "Port IP Configuration",
          "url": "Manageportip.cgi",
          "category": "network"
        }
        // ... more pages
      ]
    }
    // ... more categories
  ],
  "all_pages": [
    {
      "label": "Port IP Configuration",
      "url": "Manageportip.cgi",
      "category": "network",
      "type": "link"
    }
    // ... all 168 pages sorted by URL
  ]
}
```

### Categorization Logic

Pages are automatically categorized based on URL patterns and labels:

```python
def categorize_page(url: str, label: str) -> str:
    """Categorize a page based on URL and label keywords."""
    text = (url + " " + label).lower()

    if any(kw in text for kw in ["ip", "dhcp", "routing", "dns", "ntp"]):
        return "network"
    elif any(kw in text for kw in ["port", "interface", "ethernet"]):
        return "port"
    elif any(kw in text for kw in ["vlan", "virtual"]):
        return "vlan"
    elif any(kw in text for kw in ["system", "admin", "firmware"]):
        return "system"
    elif any(kw in text for kw in ["status", "info", "dashboard"]):
        return "status"
    elif any(kw in text for kw in ["security", "user", "access", "auth"]):
        return "security"
    elif any(kw in text for kw in ["monitor", "statistics", "traffic"]):
        return "monitoring"
    elif any(kw in text for kw in ["qos", "quality"]):
        return "qos"
    elif any(kw in text for kw in ["igmp", "multicast"]):
        return "igmp"
    else:
        return "other"
```

## Complete Code Examples

### Example 1: Find and Access IP Configuration Page

```python
#!/usr/bin/env python3
"""Find and access the IP configuration page."""

from switch_auth import SwitchSession
from bs4 import BeautifulSoup

def find_ip_config_page(session: SwitchSession) -> tuple[str, str]:
    """Find the IP configuration page in the menu.

    Returns:
        Tuple of (label, url) for the IP config page
    """
    # Get main page
    main_html = session.get_main_page()
    soup = BeautifulSoup(main_html, "html.parser")

    # Search for IP-related pages
    for link in soup.find_all("a", attrs={"datalink": True}):
        label = link.get_text(strip=True)
        url = link.get("datalink")

        if "ip" in label.lower() and "config" in label.lower():
            return label, url

    return None, None

def main():
    # Authenticate
    session = SwitchSession("192.168.2.1")
    session.login("admin", "admin")

    # Find IP config page
    label, url = find_ip_config_page(session)
    print(f"Found: {label} → {url}")

    # Access the page
    page_html = session.get_page(url)
    print(f"Page size: {len(page_html)} bytes")

    # Logout
    session.logout()

if __name__ == "__main__":
    main()
```

### Example 2: Extract All Form Fields from a Page

```python
#!/usr/bin/env python3
"""Extract all form fields from a configuration page."""

from switch_auth import SwitchSession
from bs4 import BeautifulSoup
from typing import Dict

def extract_form_fields(html: str) -> Dict[str, str]:
    """Extract all form fields and their current values.

    Args:
        html: HTML content of the page

    Returns:
        Dictionary of field names to current values
    """
    soup = BeautifulSoup(html, "html.parser")
    form_data = {}

    # Find form
    form = soup.find("form")
    if not form:
        return form_data

    # Extract input fields
    for input_field in form.find_all("input"):
        name = input_field.get("name")
        if not name:
            continue

        field_type = input_field.get("type", "text")
        value = input_field.get("value", "")

        if field_type == "checkbox":
            value = input_field.has_attr("checked")
        elif field_type == "radio":
            if input_field.has_attr("checked"):
                form_data[name] = value
            continue

        form_data[name] = value

    # Extract select fields
    for select in form.find_all("select"):
        name = select.get("name")
        if not name:
            continue

        selected = select.find("option", selected=True)
        if selected:
            form_data[name] = selected.get("value", "")
        else:
            # Use first option as default
            first_option = select.find("option")
            if first_option:
                form_data[name] = first_option.get("value", "")

    # Extract textarea fields
    for textarea in form.find_all("textarea"):
        name = textarea.get("name")
        if name:
            form_data[name] = textarea.get_text(strip=True)

    return form_data

def main():
    # Authenticate
    session = SwitchSession("192.168.2.1")
    session.login("admin", "admin")

    # Get IP config page
    page_html = session.get_page("Manageportip.cgi")

    # Extract form fields
    fields = extract_form_fields(page_html)

    print("Form fields and current values:")
    for name, value in fields.items():
        print(f"  {name}: {value}")

    session.logout()

if __name__ == "__main__":
    main()
```

### Example 3: Update Configuration with Validation

```python
#!/usr/bin/env python3
"""Update switch IP configuration with validation."""

from switch_auth import SwitchSession
from bs4 import BeautifulSoup
import ipaddress

def validate_ip_config(ip: str, netmask: str, gateway: str) -> bool:
    """Validate IP configuration parameters.

    Args:
        ip: IP address
        netmask: Subnet mask
        gateway: Gateway address

    Returns:
        True if valid, raises ValueError if invalid
    """
    # Validate IP address
    try:
        ip_obj = ipaddress.IPv4Address(ip)
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {e}")

    # Validate netmask
    try:
        netmask_obj = ipaddress.IPv4Address(netmask)
    except ValueError as e:
        raise ValueError(f"Invalid netmask: {e}")

    # Validate gateway
    try:
        gateway_obj = ipaddress.IPv4Address(gateway)
    except ValueError as e:
        raise ValueError(f"Invalid gateway: {e}")

    # Check that IP and gateway are in same subnet
    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
    if gateway_obj not in network:
        raise ValueError(f"Gateway {gateway} not in subnet {network}")

    return True

def update_ip_config(
    session: SwitchSession,
    new_ip: str,
    netmask: str,
    gateway: str
) -> bool:
    """Update switch IP configuration.

    Args:
        session: Authenticated switch session
        new_ip: New IP address
        netmask: Subnet mask
        gateway: Gateway address

    Returns:
        True if successful, False otherwise
    """
    # Validate configuration
    validate_ip_config(new_ip, netmask, gateway)

    # Get current configuration
    page_html = session.get_page("Manageportip.cgi")
    soup = BeautifulSoup(page_html, "html.parser")

    form = soup.find("form")
    if not form:
        raise ValueError("No form found on IP config page")

    # Extract current form data (including hidden fields)
    form_data = {}
    for input_field in form.find_all("input"):
        name = input_field.get("name")
        value = input_field.get("value", "")
        if name:
            form_data[name] = value

    # Update with new values
    form_data["ip_address"] = new_ip
    form_data["netmask"] = netmask
    form_data["gateway"] = gateway

    # Submit form
    action = form.get("action", "Manageportip.cgi")
    response = session.post_page(action, form_data)

    # Check response (implementation depends on actual response format)
    return response.status_code == 200

def main():
    session = SwitchSession("192.168.2.1")
    session.login("admin", "admin")

    try:
        success = update_ip_config(
            session,
            new_ip="192.168.100.50",
            netmask="255.255.255.0",
            gateway="192.168.100.1"
        )

        if success:
            print("✅ IP configuration updated successfully")
            print("⚠️  Note: You may lose connection if the IP changed")
        else:
            print("❌ IP configuration update failed")

    except ValueError as e:
        print(f"❌ Validation error: {e}")
    finally:
        session.logout()

if __name__ == "__main__":
    main()
```

## Key Findings Summary

1. **Navigation Method:** jQuery-based SPA with AJAX for page content injection
2. **Custom Attribute:** Uses `datalink` instead of standard `href` for menu items
3. **Core Function:** `reCurrentWeb()` in `utility.js` handles page loading
4. **AJAX Pattern:** Content loaded into `#appMainInner` container dynamically
5. **Direct Access:** Pages can be accessed directly via GET requests (recommended approach)
6. **Session Persistence:** Authentication session persists across all AJAX requests
7. **Menu Structure:** ~168 pages organized into ~10 categories
8. **Primary Target:** `Manageportip.cgi` for IP configuration
9. **Form Handling:** Standard HTML forms with POST submissions
10. **No CSRF Protection:** Forms do not require CSRF tokens (security weakness)

## Implementation Recommendations

### For Python Automation

1. **Use Direct Page Access** - Don't simulate menu clicks, just GET the page URL
2. **Extract Form Fields First** - Always read current configuration before modifying
3. **Preserve Hidden Fields** - Include all hidden form fields in submissions
4. **Validate Inputs** - Check IP addresses, ranges, etc. before submitting
5. **Handle Errors Gracefully** - Check response codes and content for errors
6. **Test in Dry-Run Mode** - Validate form data before actual submission

### For Menu Discovery

1. **Parse HTML for `datalink` Attributes** - Most reliable method
2. **Build Complete Menu Structure** - Cache for multiple operations
3. **Categorize Pages** - Helps with organization and search
4. **Use JSON Output** - Easy to parse and integrate with other tools

## Related Documentation

- [Authentication & Web Interface](./authentication-and-web-interface.md) - Login, RC4, session management
- [Menu Quick Reference](./menu-interaction-guide.md) - Fast lookup for common tasks
- [Menu Structure Catalog](./menu-structure-findings.md) - Complete list of all 168 pages

## Archived Documentation

Original research documents preserved in:
- `docs/archive/menu-analysis.md` - Initial menu extraction methodology
- `docs/archive/javascript-menu-analysis.md` - JavaScript implementation analysis

## References

- **Core JavaScript:** `http://192.168.2.1/js/utility.js`
- **Main Page:** `http://192.168.2.1/index.cgi`
- **jQuery Library:** `http://192.168.2.1/js/jquery-3.5.1.min.js`
- **Menu Extraction Script:** `proof-of-concept/03_menu_extraction.py`
- **JavaScript Analysis Script:** `proof-of-concept/05_analyze_menu_javascript.py`

---

**Document Created:** 2026-01-25
**Status:** Complete and Validated
**Classification:** Internal Use - Technical Documentation
