# Binardat Switch Menu Structure - Analysis Findings

**Date:** 2026-01-25
**Switch Model:** Binardat 2G20-16410GSM
**Switch IP:** 192.168.2.1
**Firmware:** Unknown (to be determined)

## Executive Summary

The Binardat switch uses a custom menu structure with **168 configuration pages** organized into **10 main categories**. The menu is embedded directly in the HTML using a custom attribute system (`datalink`) rather than standard HTML navigation patterns.

**Key Finding:** The IPv4 configuration page is located at `Manageportip.cgi`.

## Menu Structure Overview

### HTML Architecture

The switch uses a modern single-page application (SPA) approach with:
- **jQuery 3.5.1** for DOM manipulation
- **Custom navigation system** using `datalink` attributes
- **No traditional `href` links** in the menu
- **Nested `<ul>/<li>` structure** for hierarchy

### Menu HTML Pattern

```html
<div class="lsm-sidebar">
  <ul>
    <li class="lsm-sidebar-item">
      <a>
        <i class="my-icon lsm-sidebar-icon icon-system"></i>
        <span>System Config</span>
        <i class="my-icon lsm-sidebar-more"></i>
      </a>
      <ul>
        <li><a datalink="homepage.cgi"><span>System Homepage</span></a></li>
        <li class="lsm-sidebar-item">
          <a><span>IP Config</span></a>
          <ul>
            <li><a datalink="Manageportip.cgi"><span>IPv4 Config</span></a></li>
            <li><a datalink="GetInterfaceIpv6.cgi"><span>IPv6 Config</span></a></li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</div>
```

### Key HTML Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `class="lsm-sidebar-item"` | Indicates category or submenu container | `<li class="lsm-sidebar-item">` |
| `datalink="..."` | Contains the URL for page loading | `datalink="Manageportip.cgi"` |
| `<span>` inside `<a>` | Contains the menu label text | `<span>IPv4 Config</span>` |
| `class="my-icon..."` | Icon styling for menu items | `icon-system`, `icon-vlan`, etc. |

### Page Loading Mechanism

Pages are loaded via AJAX into the `#appMainInner` div:

```javascript
$('.lsm-sidebar-item a').click(function() {
  var datalink = $(this).attr('datalink');
  if (datalink) {
    // Load page content via AJAX
    $('#appMainInner').load(datalink);
  }
});
```

## Complete Menu Hierarchy

### 1. System Config (30 pages)
- **System Homepage** → `homepage.cgi`
- **Device Info** → `devinfo.cgi`
- **IP Config** (Category)
  - **IPv4 Config** → `Manageportip.cgi` ⭐ **PRIMARY TARGET**
  - **IPv6 Config** → `GetInterfaceIpv6.cgi`
- **Web Config** (Category)
  - Web Timeout → `getWebLoginTimeout.cgi`
  - HTTP → `webHttpServerConfig.cgi`
  - HTTPS → `webSslConfig.cgi`
  - Security IP → `loginUserDSecIP.cgi`
  - ACL → `loginAclName.cgi`
- **User Management** (Category)
  - User Management → `usermanag.cgi`
  - Authentication Method → `usermanagprivacy.cgi`
- **Firmware Upgrade** (Category)
  - HTTP Upgrade → `uploadFiremare.cgi`
  - TFTP Service → `firwareupgradetftp.cgi`
  - FTP Service → `firwareupgradeftp.cgi`
- **Management Config** (Category)
  - TFTP → `ImportExportConfig.cgi`
  - HTTP → `getSysFileByHttp.cgi`
- **NTP** (Category)
  - NTP Config → `ntpserverconfig.cgi`
  - NTP Authentication Config → `NtpAthenConfig.cgi`
- **SNTP** (Category)
  - Server Config → `Sntpserverconfig.cgi`
  - Time Zone Config → `configTimeDiffer.cgi`
- **Device Management** (Category)
  - Device Reboot/Reset → `devicemanagement.cgi`
  - System Utilization → `Utilization.cgi`
  - View System Config → `showRunConfig.cgi`
  - View Logging Buffer → `LoggingBuffer.cgi`
  - View Logging Flash → `LoggingFlash.cgi`

### 2. Monitor Management (32 pages)
- **SSH Config** → `ssh_get.cgi`
- **Telnet Config** → `telnet_get.cgi`
- **Port Statistics** → `Mon_port.cgi`
- **DDMI Status** → `Mon_ddm.cgi`
- **Ping** → `ping.cgi`
- **Traceroute** → `traceroute.cgi`
- **Cable Diagnostics** → `virtualCable_get.cgi`
- **SNMP Config** (8 pages)
- **RMON Config** (4 pages)
- **Onvif Config** (2 pages)
- **Loopback Detection** (4 pages)
- **LLDP Config** (4 pages)

### 3. Switch Config (24 pages)
- **Port Config** (2 pages)
- **Port Mirror** → `getPortMonitor.cgi`
- **Port Isolate** → `getPortIso.cgi`
- **Port Channel** (2 pages)
- **Jumbo Frame** → `getMTU.cgi`
- **Port Rate** → `getPortRate.cgi`
- **Storm Control** → `getStormControl.cgi`
- **MAC Address Config** (4 pages)
- **AM** → `getAccessManage.cgi`
- **AAA** (4 pages)
- **DNS Config** → `DnsSeverConfig.cgi`

### 4. VLAN Config (16 pages)
- **VLAN Config** (3 pages)
- **GVRP Config** (2 pages)
- **QINQ** (2 pages)
- **Voice VLAN** (2 pages)
- **MAC VLAN** (3 pages)
- **Protocol VLAN** → `getProtoVlanConfig.cgi`

### 5. DHCP Config (16 pages)
- **DHCP Server** (9 pages)
- **DHCP Relay Config** (1 page)
- **DHCP Snooping** (6 pages)

### 6. ACL Config (10 pages)
- **Time Range Config** → `getTimeRange.cgi`
- **IP ACL** (2 pages)
- **MAC ACL** (2 pages)
- **MAC-IP Extended ACL** → `getExtendedMACIP.cgi`
- **ACL Binding** (2 pages)

### 7. Ring Network (9 pages)
- **Spanning-tree** (6 pages)
- **ERPS** (3 pages)

### 8. Route Config (20 pages)
- **Static Route** → `getStaticRoute.cgi`
- **RIP Route** (8 pages)
- **OSPF Route** (9 pages)
- **BGP Route** (8 pages)
- **Routing Table** → `getRouteTable.cgi`

### 9. Multicast Manage (10 pages)
- **IGMP Snooping Config** (5 pages)
- **MLD Snooping Config** (5 pages)

### 10. QoS Config (12 pages)
- **Port Config** (5 pages)
- **Class-Map Config** (2 pages)
- **Policy-Map Config** (5 pages)

## IP Configuration Details

### Primary Target: IPv4 Configuration

**URL:** `Manageportip.cgi`
**Menu Path:** System Config → IP Config → IPv4 Config
**Purpose:** Configure switch management IP address, subnet mask, gateway

### Related IP Pages

| Page Name | URL | Purpose |
|-----------|-----|---------|
| IPv6 Config | `GetInterfaceIpv6.cgi` | IPv6 configuration |
| Security IP (Web) | `loginUserDSecIP.cgi` | Web interface IP restrictions |
| Security IP (SNMP) | `snmp_secutiryip_get.cgi` | SNMP access IP restrictions |
| DNS Config | `DnsSeverConfig.cgi` | DNS server configuration |
| DHCP Server | `getDhcpsGlobal.cgi` | DHCP server settings |

## Navigation Implementation

### Current State

Our initial extraction methods failed because:
1. We searched for standard `href` attributes
2. The switch uses custom `datalink` attributes
3. No traditional HTML navigation patterns used

### Corrected Approach

```python
def extract_binardat_menu(html: str) -> List[Dict[str, Any]]:
    """Extract menu from Binardat switch HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the sidebar menu
    sidebar = soup.find("div", class_="lsm-sidebar")
    root_ul = sidebar.find("ul", recursive=False)

    # Parse recursively, looking for 'datalink' attributes
    return parse_menu_recursive(root_ul)
```

### Key Parsing Rules

1. **Categories:** `<li class="lsm-sidebar-item">` without `datalink`
2. **Pages:** `<a>` tags with `datalink="xxx.cgi"` attribute
3. **Labels:** Text inside `<span>` within the `<a>` tag
4. **Hierarchy:** Nested `<ul>` elements indicate submenus

## Statistics

| Metric | Count |
|--------|-------|
| **Total Pages** | 168 |
| **Main Categories** | 10 |
| **Subcategories** | ~40 |
| **IP-Related Pages** | 15 |
| **Configuration Pages** | ~140 |
| **Monitoring Pages** | ~28 |

## Implementation Recommendations

### 1. Update Menu Extraction Script

Replace the generic extraction with Binardat-specific parsing:

```python
# Look for datalink attribute instead of href
datalink = a_tag.get("datalink", "")
if datalink:
    items.append({
        "label": label,
        "url": datalink,
        "type": "page"
    })
```

### 2. Direct Navigation to IP Config

Since we know the exact URL, we can navigate directly:

```python
def navigate_to_ip_config(session: SwitchSession) -> str:
    """Navigate directly to IPv4 configuration page."""
    return session.get_page("Manageportip.cgi")
```

### 3. Form Parsing

After loading `Manageportip.cgi`, we need to:
1. Parse the form structure
2. Identify input fields for IP, netmask, gateway
3. Extract current values
4. Determine the form submission endpoint

## Next Steps

1. **Load `Manageportip.cgi`** and analyze the form structure
2. **Identify form fields** for IP configuration
3. **Determine submission method** (POST endpoint, field names)
4. **Test configuration change** with known values
5. **Verify change** by reconnecting or checking response

## References

- `proof-of-concept/analyze_menu_structure.py` - Menu analysis script
- `menu_structure.json` - Complete extracted menu data
- `main_page.html` - Full HTML source of switch interface
- `docs/reconnaissance-findings.md` - Initial reconnaissance results

## Appendix: Common URL Patterns

Observed naming conventions for CGI endpoints:

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `get*.cgi` | Retrieve/display data | `getVlanConfig.cgi`, `getPortCfg.cgi` |
| `*Config.cgi` | Configuration pages | `RadiusConfigForm.cgi`, `DnsSeverConfig.cgi` |
| `Mon_*.cgi` | Monitoring pages | `Mon_port.cgi`, `Mon_ddm.cgi` |
| `*Info.cgi` | Information display | `getLLDPPortInfo.cgi`, `devinfo.cgi` |

## Changelog

- **2026-01-25**: Initial menu structure analysis completed
- Identified 168 pages across 10 main categories
- Located IPv4 configuration page at `Manageportip.cgi`
- Documented custom `datalink` attribute system
