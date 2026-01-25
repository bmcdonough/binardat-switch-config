# Binardat Switch - JavaScript Menu System Analysis

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

**Key File:** `/js/utility.js` contains the `reCurrentWeb()` function and all menu navigation logic.

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

### Detected Click Handlers

Found 5 click handler(s):

**Handler 1:**
- **Source:** `inline_script_3`
- **Selector:** `#statusToggle`
- **Code snippet:**
  ```javascript
  HideAndShowPanle($(this));    changeAppMainHeight();...
  ```

**Handler 2:**
- **Source:** `inline_script_3`
- **Selector:** `#logout`
- **Code snippet:**
  ```javascript
  httpPostGet('POST', 'syscmd.cgi', 'cmd=logout', function(val){ 	   if(val.code==0){clearAuthInfo();refreshWeb();...
  ```

**Handler 3:**
- **Source:** `inline_script_3`
- **Selector:** `#save`
- **Code snippet:**
  ```javascript
  httpPostGet('POST', 'syscmd.cgi', 'cmd=save', function(val){ 	   showBg();if(val.code==0){closeBg();alert('Configuration saved successfully!');console.log('ä¿å­æå!');...
  ```

**Handler 4:**
- **Source:** `inline_script_3`
- **Selector:** `#reset`
- **Code snippet:**
  ```javascript
  myconfirm('Are you sure you want to restore the switch?', resetDevice);...
  ```

**Handler 5:**
- **Source:** `inline_script_3`
- **Selector:** `#reboot`
- **Code snippet:**
  ```javascript
  myconfirm('Are you sure you want to reboot the switch?', rebootDevice);...
  ```

### Menu-Related jQuery Selectors

The following menu-related selectors were found:
- `datalink`
- `lsm-sidebar`
- `menu`
- `sidebar-item`

## AJAX and Page Loading

### jQuery .load() Calls

Found 0 jQuery .load() call(s):

### jQuery $.ajax() Calls

Found 1 jQuery $.ajax() call(s).
These are typically used for form submissions or API calls.

## 'datalink' Attribute Handling

The Binardat switch uses a custom `datalink` attribute instead of standard `href` attributes.

### Datalink Reads

Found 3 location(s) where the `datalink` attribute is read:

- `$(this).attr('datalink')` in `external_/js/utility.js`
- `$(this).attr('datalink')` in `external_/js/utility.js`
- `that.attr('datalink')` in `external_/js/utility.js`

### Related Functions

The following functions reference the `datalink` attribute:

- `reCurrentWeb()` in `external_/js/utility.js`

### Key Implementation Detail

The menu system works as follows:

1. **Menu items with `datalink` attribute** are interactive pages
2. **jQuery event handler** in `utility.js` reads the `datalink` attribute when clicked
3. **AJAX request** fetches the page content from the URL specified in `datalink`
4. **Content injection** into the `#appMainInner` div displays the page
5. **URL doesn't change** - true single-page application behavior

**Critical Finding:** The menu JavaScript in `utility.js` handles the `datalink` attribute clicks,
but for programmatic access, we can bypass this and directly fetch the URLs via GET requests
using our authenticated session.

## Menu Interaction Patterns

### Expand/Collapse Mechanism

Found 7 expand/collapse pattern(s):

- `addClass('lsm-sidebar-show')` in `external_/js/utility.js`
- `removeClass('lsm-sidebar-show')` in `external_/js/utility.js`
- `removeClass('lsm-sidebar-show')` in `external_/js/utility.js`
- `removeClass('lsm-sidebar-show')` in `external_/js/utility.js`
- `removeClass('active')` in `external_/js/utility.js`
- `addClass('active')` in `external_/js/utility.js`
- `removeClass('lsm-sidebar-show')` in `external_/js/utility.js`

### Active State Management

The following CSS classes are used to indicate active menu items:

- `!=typeof v.data&&(v.data=S.param(v.data,v.traditional)),Bt(Rt,v,t,T),h)return T;for(i in(g=S.event&&v.global)&&0==S.active++&&S.event.trigger(`
- `)&&n.push(o)}return f}var be=/^key/,we=/^(?:mouse|pointer|contextmenu|drag|drop)|click/,Te=/^([^.]*)(?:\.(.+)|)/;function Ce(){return!0}function Ee(){return!1}function Se(e,t){return e===function(){try{return E.activeElement}catch(e){}}()==(`
- `),this},blur:function(){var a=this.__activeElement,b=arguments[0];return b!==!1&&this.__focus(a),this._autofocus=!1,this.__popup.removeClass(this.className+`
- `),this},focus:function(){var a=this.node,d=this.__popup,e=b.current,f=this.zIndex=b.zIndex++;if(e&&e!==this&&e.blur(!1),!c.contains(a,this.__getActive())){var g=d.find(`
- `);
        for (var i = 0; i < idArr.length; i++) {
			hideOrShow($(idArr[i]),val);
        }
    }
}

/*
函数功能：创建HTTP对象
参数含义：无
返回值：无
*/
function createHttpRequest() {
    var xmlHttp = false;
    if (window.XMLHttpRequest) {
        xmlHttp = new XMLHttpRequest()
    } else {
        xmlHttp = new ActiveXObject(`
- `)}function $t(e,t){var n,r,i=S.ajaxSettings.flatOptions||{};for(n in t)void 0!==t[n]&&((i[n]?e:r||(r={}))[n]=t[n]);return r&&S.extend(!0,e,r),e}Wt.href=Tt.href,S.extend({active:0,lastModified:{},etag:{},ajaxSettings:{url:Tt.href,type:`
- `)}while((e=e.parentNode)&&1===e.nodeType);return!1}}),target:function(e){var t=n.location&&n.location.hash;return t&&t.slice(1)===e.id},root:function(e){return e===a},focus:function(e){return e===C.activeElement&&(!C.hasFocus||C.hasFocus())&&!!(e.type||e.href||~e.tabIndex)},enabled:ge(!1),disabled:ge(!0),checked:function(e){var t=e.nodeName.toLowerCase();return`
- `+a]();for(var c=0;c<b.length;c++)b[c].call(this)},__focus:function(a){try{this.autofocus&&!/^iframe$/i.test(a.nodeName)&&a.focus()}catch(b){}},__getActive:function(){try{var a=document.activeElement,b=a.contentDocument,c=b&&b.activeElement||a;return c}catch(d){}},__center:function(){var a=this.__popup,b=c(window),d=c(document),e=this.fixed,f=e?0:d.scrollLeft(),g=e?0:d.scrollTop(),h=b.width(),i=b.height(),j=a.width(),k=a.height(),l=(h-j)/2+f,m=382*(i-k)/1e3+g,n=a[0].style;n.left=Math.max(parseInt(l),f)+`
- `+n:null}).html(p).appendTo(t),{action:n},r))}}var p,g,n,b=u.oClasses,m=u.oLanguage.oPaginate,S=u.oLanguage.oAria.paginate||{};try{n=P(t).find(v.activeElement).data(`
- `,[T,v]),--S.active||S.event.trigger(`
- `,function(t,e){if(n===e)try{u[0]!==v.activeElement&&u.val(o.sSearch)}catch(t){}}),l[0]}function Rt(t,e,n){function a(t){o.sSearch=t.sSearch,o.bRegex=t.bRegex,o.bSmart=t.bSmart,o.bCaseInsensitive=t.bCaseInsensitive,o.return=t.return}function r(t){return t.bEscapeRegex!==H?!t.bEscapeRegex:t.bRegex}var o=t.oPreviousSearch,i=t.aoPreSearchCols;if(lt(t),`
- `,sPageButtonActive:`
- `,show:function(a){if(this.destroyed)return this;var d=this.__popup,g=this.__backdrop;if(this.__activeElement=this.__getActive(),this.open=!0,this.follow=a||this.follow,!this.__ready){if(d.addClass(this.className).attr(`
- `:g===b.sPageButtonActive?`
- `:p=m.sLast,0!==d&&f!==d-1||(s=!0);break;default:p=u.fnFormatNumber(n+1),g=f===n?b.sPageButtonActive:`
- `active`

## Implementation Recommendations

### 1. Programmatic Navigation

To programmatically navigate to a page:

```python
def navigate_to_page(session: SwitchSession, page_url: str) -> str:
    """Navigate to a specific page using direct URL access.

    Args:
        session: Authenticated switch session.
        page_url: The page URL (e.g., 'Manageportip.cgi').

    Returns:
        HTML content of the page.
    """
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

## Practical Menu Navigation Examples

### Example 1: Direct Page Access (Recommended)

```python
from switch_auth import SwitchSession

# Authenticate
session = SwitchSession("192.168.2.1")
session.login("admin", "admin")

# Navigate directly to IPv4 configuration page
# No need to simulate menu clicks - just GET the page
ip_config_html = session.get_page("Manageportip.cgi")

# Parse the page
from bs4 import BeautifulSoup
soup = BeautifulSoup(ip_config_html, "html.parser")

# Extract form and current IP settings
# ... (form handling code)
```

### Example 2: Menu Traversal (If Needed)

```python
# Get main page with menu structure
main_html = session.get_main_page()
soup = BeautifulSoup(main_html, "html.parser")

# Find all menu items with datalink attributes
menu_items = soup.find_all("a", attrs={"datalink": True})

for item in menu_items:
    label = item.find("span").get_text(strip=True)
    url = item.get("datalink")
    print(f"{label} → {url}")

# Access any discovered page
page_html = session.get_page(url)
```

### Example 3: Working with Forms

```python
# Get IP configuration page
page_html = session.get_page("Manageportip.cgi")
soup = BeautifulSoup(page_html, "html.parser")

# Find the configuration form
form = soup.find("form")

# Extract all form fields
form_data = {}
for input_field in form.find_all("input"):
    name = input_field.get("name")
    value = input_field.get("value", "")
    if name:
        form_data[name] = value

# Modify IP settings
form_data["ip_address"] = "192.168.100.50"
form_data["netmask"] = "255.255.255.0"

# Submit form
action = form.get("action", "Manageportip.cgi")
response = session.post_page(action, form_data)
```

## Key Findings Summary

1. **Navigation Method:** jQuery-based SPA with AJAX for page content injection (via `utility.js`)
2. **Custom Attribute:** Uses `datalink` instead of `href` for menu items
3. **AJAX Pattern:** Content loaded into `#appMainInner` container dynamically
4. **Direct Access:** Pages can be accessed directly via GET requests (no need to simulate clicks)
5. **Session Management:** Authentication session persists across AJAX requests
6. **Primary JavaScript:** `utility.js` contains the core menu navigation logic
7. **Function Name:** `reCurrentWeb()` handles page loading via datalink attributes

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
