# Menu Structure Analysis

**Date:** 2026-01-25
**Switch Model:** Binardat 2G20-16410GSM
**Switch IP:** 192.168.2.1
**Script:** `proof-of-concept/03_menu_extraction.py`

## Overview

This document describes the menu structure discovery process for the Binardat switch web interface. The goal is to systematically identify all available pages and configuration options to enable programmatic navigation.

## Extraction Methodology

### 1. HTML Navigation Analysis

The extraction script analyzes the authenticated web interface using multiple strategies:

**Strategy A: Semantic HTML Elements**
- `<nav>` tags
- Elements with menu-related classes (`menu`, `navigation`, `sidebar`, etc.)
- `<ul>/<li>` structures with multiple links (3+ items)
- `<frame>` and `<iframe>` elements (common in older interfaces)

**Strategy B: Link Analysis**
- Extract all `<a>` tags with `href` attributes
- Filter out JavaScript pseudo-links (`javascript:`, `#`)
- Capture link text, title attributes, and URLs

### 2. JavaScript Menu Parsing

Many switch interfaces define menus dynamically in JavaScript. The script searches for:

**Pattern 1: Array Definitions**
```javascript
var menu = [
    {label: "Network", url: "network.html"},
    {label: "System", url: "system.html"},
    // ...
];
```

**Pattern 2: Direct Assignments**
```javascript
menu[0] = {label: "Network", url: "network.html"};
menu[1] = {label: "System", url: "system.html"};
```

**Pattern 3: Configuration Objects**
```javascript
var menuConfig = {
    network: {label: "Network Configuration", url: "network.html"},
    // ...
};
```

### 3. External JavaScript Files

The script follows `<script src="...">` tags to fetch and analyze external JavaScript files, particularly:
- `/js/utility.js` - Common location for menu definitions
- `/js/menu.js` - Dedicated menu configuration
- `/js/common.js` - Shared utilities

### 4. Categorization

Discovered pages are automatically categorized based on URL patterns and labels:

| Category    | Patterns                                      |
|-------------|-----------------------------------------------|
| Network     | `network`, `ip`, `dhcp`, `routing`           |
| System      | `system`, `admin`, `management`              |
| Port        | `port`, `interface`, `ethernet`              |
| VLAN        | `vlan`, `virtual`                            |
| Status      | `status`, `info`, `dashboard`                |
| Security    | `security`, `user`, `access`, `auth`         |
| Monitoring  | `monitor`, `statistics`, `stats`, `traffic`  |
| Config      | `config`, `setting`, `setup`                 |
| Other       | Everything else                              |

## Output Format

The script generates a JSON file (`menu_structure.json`) with the following structure:

```json
{
  "metadata": {
    "switch_host": "192.168.2.1",
    "extraction_method": "html_and_javascript",
    "total_items": 25,
    "categories": {
      "network": 5,
      "system": 8,
      "status": 3,
      // ...
    }
  },
  "menu": [
    {
      "id": "network",
      "label": "Network",
      "children": [
        {
          "label": "IP Configuration",
          "url": "ip_config.html",
          "category": "network"
        },
        // ...
      ]
    },
    // ...
  ],
  "all_pages": [
    {
      "label": "IP Configuration",
      "url": "ip_config.html",
      "category": "network",
      "type": "link"
    },
    // ... (sorted by URL)
  ]
}
```

## Usage

### Basic Extraction
```bash
cd proof-of-concept
python 03_menu_extraction.py -u admin -p admin
```

### With Tree Display
```bash
python 03_menu_extraction.py -u admin -p admin --display-tree
```

### Search for Specific Pages
```bash
python 03_menu_extraction.py -u admin -p admin --search "ip"
```

### Custom Output Location
```bash
python 03_menu_extraction.py -u admin -p admin -o ../docs/discovered_menu.json
```

## Expected Findings

Based on typical managed switch web interfaces, we expect to find:

### Network Configuration Pages
- IP address configuration (static/DHCP)
- VLAN configuration
- Routing settings
- DNS configuration
- NTP time synchronization

### Port Configuration Pages
- Port settings (speed, duplex, auto-negotiation)
- Port statistics
- Port mirroring
- Link aggregation (LAG/trunk)

### System Pages
- System information
- Firmware upgrade
- Configuration backup/restore
- Reboot/reset
- User management

### Monitoring Pages
- Port status and statistics
- System logs
- Traffic monitoring
- Error counters

### Security Pages
- Access control lists (ACL)
- User authentication
- SNMP configuration
- SSH/Telnet settings

## Integration with IP Configuration

The primary goal of menu extraction is to locate the IP configuration page. Once identified, the URL will be used in Phase 6 to implement targeted navigation:

```python
# Example from switch_auth.py (enhanced version)
def navigate_to_ip_config(self) -> str:
    """Navigate to IP configuration using discovered menu."""
    # Load menu structure
    with open("menu_structure.json") as f:
        menu = json.load(f)

    # Search for IP config page
    for page in menu["all_pages"]:
        if "ip" in page["url"].lower() or "network" in page["url"].lower():
            return self.get_page(page["url"])

    # Fallback to common URLs
    # ...
```

## Troubleshooting

### No Navigation Items Found

**Causes:**
- Interface uses frameset layout (check for `<frameset>` tags)
- Menu generated by AJAX after page load
- Non-standard navigation structure

**Solutions:**
1. Check browser developer tools for AJAX requests
2. Look for `XMLHttpRequest` or `fetch()` calls in JavaScript
3. Try accessing `/main.html`, `/menu.html`, or similar pages directly

### JavaScript Parsing Fails

**Causes:**
- Obfuscated JavaScript
- Menu data loaded from external API
- Complex JavaScript frameworks (unlikely in switches)

**Solutions:**
1. Use browser to manually identify menu structure
2. Check network tab for JSON responses
3. Look for data attributes (`data-url`, `data-page`) in HTML

### Incomplete Menu Discovery

**Causes:**
- Some pages only accessible after specific actions
- Multi-level menus with dynamic loading
- Pages hidden by permissions

**Solutions:**
1. Run extraction with admin-level account
2. Follow links recursively (future enhancement)
3. Check for submenu expansion JavaScript

## Future Enhancements

1. **Recursive Page Discovery**
   - Follow discovered links to find additional pages
   - Build complete site map
   - Detect circular references

2. **AJAX Endpoint Detection**
   - Monitor network requests during extraction
   - Identify API endpoints
   - Map form submission URLs

3. **Form Field Discovery**
   - For each page, extract form fields
   - Document expected input types
   - Build configuration templates

4. **Page Content Analysis**
   - Extract current settings from each page
   - Build complete switch state snapshot
   - Enable configuration comparison

## References

- `proof-of-concept/switch_auth.py` - Session management and menu extraction methods
- `proof-of-concept/03_menu_extraction.py` - Main extraction script
- `proof-of-concept/menu_structure.json` - Output file (generated)
- `docs/reconnaissance-findings.md` - Initial reconnaissance results

## Changelog

- **2026-01-25**: Initial menu extraction implementation (Phase 5)
