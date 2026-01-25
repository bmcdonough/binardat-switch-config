# Binardat Switch - Menu Interaction Quick Reference

**Date:** 2026-01-25
**Purpose:** Quick reference for interacting with the Binardat switch menu system

## Summary

The Binardat switch uses a jQuery-based single-page application (SPA) with custom `datalink` attributes for navigation. Pages can be accessed directly via GET requests without simulating JavaScript clicks.

## Menu Structure at a Glance

```
10 main categories
168 total pages
Custom datalink attribute system
jQuery 3.5.1 + utility.js for navigation
Content loaded into #appMainInner div
```

## Quick Navigation Examples

### Access IP Configuration Page

```python
from switch_auth import SwitchSession

session = SwitchSession("192.168.2.1")
session.login("admin", "admin")

# Direct access - no menu simulation needed!
ip_page = session.get_page("Manageportip.cgi")
```

### Get All Menu Items

```python
from bs4 import BeautifulSoup

main_html = session.get_main_page()
soup = BeautifulSoup(main_html, "html.parser")

# Find all pages with datalink attribute
menu_items = soup.find_all("a", attrs={"datalink": True})

for item in menu_items:
    label = item.find("span").get_text(strip=True)
    url = item.get("datalink")
    print(f"{label:40} → {url}")
```

## Key Menu Categories

| Category | Page Count | Example Pages |
|----------|------------|---------------|
| System Config | 30 | `Manageportip.cgi`, `devinfo.cgi`, `homepage.cgi` |
| Monitor Management | 32 | `Mon_port.cgi`, `ssh_get.cgi`, `ping.cgi` |
| Switch Config | 24 | `getPortCfg.cgi`, `getPortMonitor.cgi` |
| VLAN Config | 16 | `getVlanConfig.cgi`, `getVlanManage.cgi` |
| DHCP Config | 16 | `getDhcpsGlobal.cgi`, `getDhcpsPool.cgi` |
| ACL Config | 10 | `getTimeRange.cgi`, `getIpAclConfig.cgi` |
| Ring Network | 9 | `getStpGlobal.cgi`, `getStpPort.cgi` |
| Route Config | 20 | `getStaticRoute.cgi`, `getRouteTable.cgi` |
| Multicast Manage | 10 | `getIGMPSnooping.cgi` |
| QoS Config | 12 | `getPortQos.cgi`, `getClassMap.cgi` |

## Important IP-Related Pages

| Page Name | URL | Purpose |
|-----------|-----|---------|
| **IPv4 Config** | `Manageportip.cgi` | **Primary target for IP changes** |
| IPv6 Config | `GetInterfaceIpv6.cgi` | IPv6 configuration |
| DNS Config | `DnsSeverConfig.cgi` | DNS servers |
| DHCP Server | `getDhcpsGlobal.cgi` | DHCP server settings |

## Menu HTML Structure

```html
<!-- Category (non-clickable container) -->
<li class="lsm-sidebar-item">
  <a>
    <span>System Config</span>
  </a>
  <ul>
    <!-- Clickable page -->
    <li>
      <a datalink="Manageportip.cgi">
        <span>IPv4 Config</span>
      </a>
    </li>
  </ul>
</li>
```

## JavaScript Menu Logic

**File:** `/js/utility.js`
**Function:** `reCurrentWeb()`
**Pattern:**
1. User clicks menu item with `datalink` attribute
2. jQuery reads `$(this).attr('datalink')`
3. AJAX GET request fetches page content
4. Content injected into `#appMainInner` div
5. Page displays without URL change

## Interaction Methods

### Method 1: Direct Access (Recommended)

```python
# Simplest and most reliable
page_html = session.get_page("Manageportip.cgi")
```

**Pros:**
- Simple and fast
- No JavaScript simulation needed
- Works with existing session
- Direct and predictable

**Cons:**
- None for our use case

### Method 2: Menu Discovery

```python
# When you don't know the exact URL
menu_structure = session.discover_pages(main_html)
target_page = [p for p in menu_structure if "ip" in p["label"].lower()][0]
page_html = session.get_page(target_page["url"])
```

**Pros:**
- Works even if URLs change
- Documents available pages
- Helpful for exploration

**Cons:**
- More complex
- Slower (extra request for main page)

## CSS Classes for Menu States

| Class | Purpose |
|-------|---------|
| `lsm-sidebar-item` | Category container (has submenu) |
| `lsm-sidebar-show` | Menu is expanded/visible |
| `active` | Currently selected menu item |
| `lsm-sidebar-icon` | Icon styling |

## Common Operations

### Save Configuration

```python
# POST to syscmd.cgi with cmd=save parameter
response = session.post_page("syscmd.cgi", {"cmd": "save"})
```

### Reboot Switch

```python
# POST to syscmd.cgi with cmd=reboot parameter
response = session.post_page("syscmd.cgi", {"cmd": "reboot"})
```

### Logout

```python
# POST to syscmd.cgi with cmd=logout parameter
response = session.post_page("syscmd.cgi", {"cmd": "logout"})
# Or use session.logout()
```

## Troubleshooting

### Issue: Page returns "unauthorized"

**Solution:** Ensure session is authenticated:
```python
if not session.authenticated:
    session.login(username, password)
```

### Issue: Form submission fails

**Solution:** Check for hidden fields and CSRF tokens:
```python
hidden_fields = soup.find_all("input", type="hidden")
for field in hidden_fields:
    form_data[field.get("name")] = field.get("value")
```

### Issue: Can't find a page

**Solution:** Run menu extraction to discover all pages:
```bash
cd proof-of-concept
python 03_menu_extraction.py -u admin -p admin --search "keyword"
```

## Related Documentation

- **HTML Structure:** [`docs/menu-structure-findings.md`](menu-structure-findings.md)
- **JavaScript Details:** [`docs/javascript-menu-analysis.md`](javascript-menu-analysis.md)
- **Authentication:** [`docs/authentication-findings.md`](authentication-findings.md)
- **Reconnaissance:** [`docs/reconnaissance-findings.md`](reconnaissance-findings.md)

## Scripts

- **`02_test_login.py`** - Test authentication
- **`03_menu_extraction.py`** - Extract complete menu structure
- **`05_analyze_menu_javascript.py`** - Analyze JavaScript implementation
- **`analyze_menu_structure.py`** - Parse menu HTML structure
- **`switch_auth.py`** - Session management library

## Next Phase: IP Configuration

With the menu system fully documented, the next steps are:

1. **Fetch `Manageportip.cgi`** and analyze the form structure
2. **Identify form fields** for IP, netmask, gateway
3. **Test form submission** with known values
4. **Verify changes** by reconnecting or checking response
5. **Implement IP change function** in `switch_auth.py`

## Changelog

- **2026-01-25**: Initial quick reference guide created
