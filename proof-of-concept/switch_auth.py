"""Session management and authentication for Binardat switches.

This module provides the SwitchSession class for managing HTTP sessions
with Binardat switches, including RC4-encrypted authentication and menu
structure extraction.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup, Tag
from rc4_crypto import encrypt_credentials


class SwitchAuthError(Exception):
    """Exception raised for authentication-related errors."""

    pass


class SwitchConnectionError(Exception):
    """Exception raised for connection-related errors."""

    pass


class SwitchSession:
    """Manages HTTP session with a Binardat switch.

    This class handles authentication, session management, and provides
    methods for navigating the switch web interface.

    Attributes:
        host: IP address or hostname of the switch.
        timeout: Request timeout in seconds.
        session: Requests session object for persistent connections.
        authenticated: Whether the session is authenticated.
        rc4_key: RC4 encryption key extracted from the switch.
    """

    def __init__(self, host: str, timeout: float = 30.0) -> None:
        """Initialize a switch session.

        Args:
            host: IP address or hostname of the switch.
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self.host = host
        self.timeout = timeout
        self.session = requests.Session()
        self.authenticated = False
        self.rc4_key: Optional[str] = None
        self.base_url = f"http://{host}"

    def _extract_rc4_key(self, html: str) -> Optional[str]:
        """Extract RC4 key from HTML/JavaScript.

        Args:
            html: HTML content from the switch.

        Returns:
            RC4 key if found, None otherwise.
        """
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string:
                patterns = [
                    # Match rc4("key", ...) or rc4('key', ...)
                    r'rc4\s*\(\s*["\']([^"\']+)["\']',
                    # Match key = "..." or key = '...'
                    r'key\s*=\s*["\']([^"\']+)["\']',
                    r'rc4[Kk]ey\s*=\s*["\']([^"\']+)["\']',
                    r'encryptionKey\s*=\s*["\']([^"\']+)["\']',
                    # Match var something = "hexstring"
                    r'var\s+\w+\s*=\s*["\']([0-9a-fA-F]{16,})["\']',
                ]

                for pattern in patterns:
                    match = re.search(pattern, script.string, re.IGNORECASE)
                    if match:
                        return match.group(1)

        return None

    def _get_login_page(self) -> str:
        """Fetch the login page and extract RC4 key.

        Returns:
            HTML content of the login page.

        Raises:
            SwitchConnectionError: If unable to connect to the switch.
        """
        url = f"{self.base_url}/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Extract RC4 key
            self.rc4_key = self._extract_rc4_key(response.text)

            return response.text
        except requests.RequestException as e:
            raise SwitchConnectionError(
                f"Failed to connect to {url}: {e}"
            ) from e

    def _find_login_form(self, html: str) -> Dict[str, str]:
        """Parse login form to find field names and action URL.

        Args:
            html: HTML content of the login page.

        Returns:
            Dictionary with form action and field names.

        Raises:
            SwitchAuthError: If login form cannot be found or parsed.
        """
        soup = BeautifulSoup(html, "html.parser")
        forms = soup.find_all("form")

        if not forms:
            raise SwitchAuthError("No login form found on the page")

        # Use the first form (typically the login form)
        form = forms[0]

        action = form.get("action", "")
        method = form.get("method", "GET")

        form_info = {
            "action": str(action) if action else "",
            "method": str(method).upper() if method else "GET",
        }

        # Find username and password fields
        inputs = form.find_all("input")
        for inp in inputs:
            name_attr = inp.get("name", "")
            name = str(name_attr).lower() if name_attr else ""
            type_attr = inp.get("type", "text")
            input_type = str(type_attr).lower() if type_attr else "text"

            # Try to identify username field
            if "user" in name or input_type == "text":
                if "username_field" not in form_info:
                    name_val = inp.get("name", "")
                    form_info["username_field"] = (
                        str(name_val) if name_val else ""
                    )

            # Try to identify password field
            if "pass" in name or input_type == "password":
                if "password_field" not in form_info:
                    name_val = inp.get("name", "")
                    form_info["password_field"] = (
                        str(name_val) if name_val else ""
                    )

            # Capture hidden fields
            if input_type == "hidden":
                hidden_name_attr = inp.get("name", "")
                hidden_name = str(hidden_name_attr) if hidden_name_attr else ""
                hidden_value_attr = inp.get("value", "")
                hidden_value = (
                    str(hidden_value_attr) if hidden_value_attr else ""
                )
                if hidden_name:
                    form_info[f"hidden_{hidden_name}"] = hidden_value

        # Validate that we found the required fields
        if "username_field" not in form_info:
            raise SwitchAuthError(
                "Could not identify username field in login form"
            )
        if "password_field" not in form_info:
            raise SwitchAuthError(
                "Could not identify password field in login form"
            )

        return form_info

    def login(self, username: str, password: str) -> bool:
        """Authenticate to the switch.

        Args:
            username: Switch username.
            password: Switch password.

        Returns:
            True if authentication successful.

        Raises:
            SwitchConnectionError: If unable to connect to the switch.
            SwitchAuthError: If authentication fails.
        """
        # Get login page and extract RC4 key
        self._get_login_page()

        if not self.rc4_key:
            raise SwitchAuthError(
                "Could not extract RC4 key from login page. "
                "Manual inspection of JavaScript may be required."
            )

        # Encrypt credentials
        enc_username, enc_password = encrypt_credentials(
            username, password, self.rc4_key
        )

        # Build POST data (format: name=<encrypted>&pwd=<encrypted>)
        form_data = {
            "name": enc_username,
            "pwd": enc_password,
        }

        # Submit login to /login.cgi
        login_url = f"{self.base_url}/login.cgi"

        try:
            response = self.session.post(
                login_url, data=form_data, timeout=self.timeout
            )
            response.raise_for_status()

            # Parse JSON response
            try:
                result = response.json()
                code = result.get("code", -1)

                if code == 0:
                    # Login successful
                    self.authenticated = True
                    return True
                elif code == 6:
                    # Insufficient permissions
                    username_field = result.get("data", {}).get(
                        "name", username
                    )
                    raise SwitchAuthError(
                        f'"{username_field}" does not have sufficient '
                        "permissions. User permissions must be >= 15."
                    )
                else:
                    # Authentication failed
                    raise SwitchAuthError(
                        "Authentication failed: incorrect username or password"
                    )
            except ValueError:
                # Response is not JSON, fall back to HTML check
                if self._check_authentication(response.text):
                    self.authenticated = True
                    return True
                else:
                    raise SwitchAuthError("Authentication failed")

        except requests.RequestException as e:
            raise SwitchConnectionError(
                f"Failed to submit login form: {e}"
            ) from e

    def _check_authentication(self, html: str) -> bool:
        """Check if authentication was successful.

        Args:
            html: HTML response after login attempt.

        Returns:
            True if authenticated, False otherwise.
        """
        # Check for common authentication failure indicators
        failure_indicators = [
            "invalid",
            "incorrect",
            "failed",
            "wrong password",
            "authentication failed",
            "login failed",
        ]

        html_lower = html.lower()
        for indicator in failure_indicators:
            if indicator in html_lower:
                return False

        # Check if login form is still present
        soup = BeautifulSoup(html, "html.parser")
        forms = soup.find_all("form")
        for form in forms:
            inputs = form.find_all("input", type="password")
            if inputs:
                # Password field still present, likely still on login page
                return False

        # If we made it here, authentication likely succeeded
        return True

    def logout(self) -> bool:
        """Log out from the switch.

        Returns:
            True if logout successful.

        Raises:
            SwitchConnectionError: If unable to connect to the switch.
        """
        if not self.authenticated:
            return True

        # Common logout URLs
        logout_urls = [
            f"{self.base_url}/logout",
            f"{self.base_url}/logout.html",
            f"{self.base_url}/logout.cgi",
            f"{self.base_url}/signout",
        ]

        for url in logout_urls:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    self.authenticated = False
                    return True
            except requests.RequestException:
                continue

        # If no logout URL worked, just clear the session
        self.session.cookies.clear()
        self.authenticated = False
        return True

    def get_page(self, path: str) -> str:
        """Fetch a page from the switch.

        Args:
            path: URL path relative to base URL.

        Returns:
            HTML content of the page.

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to fetch the page.
        """
        if not self.authenticated:
            raise SwitchAuthError("Not authenticated. Call login() first.")

        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise SwitchConnectionError(f"Failed to fetch {url}: {e}") from e

    def post_page(self, path: str, data: Dict[str, str]) -> str:
        """Submit a form to the switch.

        Args:
            path: URL path relative to base URL.
            data: Form data to submit.

        Returns:
            HTML content of the response.

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to submit the form.
        """
        if not self.authenticated:
            raise SwitchAuthError("Not authenticated. Call login() first.")

        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise SwitchConnectionError(f"Failed to post to {url}: {e}") from e

    def navigate_to_ip_config(
        self,
        menu_file: Optional[str] = None,
    ) -> str:
        """Navigate to the IP configuration page.

        Args:
            menu_file: Path to menu_structure.json file. If provided,
                uses menu structure for targeted navigation. If None or
                file doesn't exist, falls back to common URLs.

        Returns:
            HTML content of the IP configuration page.

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to reach the page.
        """
        # Try menu-aware navigation first
        if menu_file:
            menu_path = Path(menu_file)
            if menu_path.exists():
                try:
                    return self._navigate_using_menu(menu_path)
                except SwitchConnectionError:
                    # Fall through to common URLs
                    pass

        # Fall back to common IP configuration page URLs
        config_urls = [
            "network.html",
            "network.htm",
            "ip_config.html",
            "ip_config.htm",
            "ipconfig.html",
            "config/network.html",
            "system/network.html",
            "settings/network.html",
        ]

        for url in config_urls:
            try:
                html = self.get_page(url)
                # Check if this page contains IP configuration
                if "ip" in html.lower() and (
                    "address" in html.lower() or "netmask" in html.lower()
                ):
                    return html
            except SwitchConnectionError:
                continue

        raise SwitchConnectionError(
            "Could not find IP configuration page. "
            "Try running 03_menu_extraction.py first to discover pages, "
            "or manual navigation may be required."
        )

    def _navigate_using_menu(self, menu_path: Path) -> str:
        """Navigate to IP config using extracted menu structure.

        Args:
            menu_path: Path to menu_structure.json file.

        Returns:
            HTML content of the IP configuration page.

        Raises:
            SwitchConnectionError: If unable to find or navigate to page.
        """
        # Load menu structure
        with open(menu_path, "r", encoding="utf-8") as f:
            menu_data = json.load(f)

        # Search for IP configuration page
        candidates = []
        for page in menu_data.get("all_pages", []):
            url = page.get("url", "").lower()
            label = page.get("label", "").lower()

            # Score each page based on relevance
            score = 0
            if "ip" in url or "ip" in label:
                score += 10
            if "network" in url or "network" in label:
                score += 5
            if "config" in url or "config" in label:
                score += 3
            if "address" in label:
                score += 5
            if page.get("category") == "network":
                score += 5

            if score > 0:
                candidates.append((score, page))

        # Sort by score (highest first)
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Try each candidate
        for score, page in candidates:
            url = page.get("url", "")
            if not url:
                continue

            try:
                html = self.get_page(url)
                # Verify this is actually an IP configuration page
                html_lower = html.lower()
                if "ip" in html_lower and (
                    "address" in html_lower or "netmask" in html_lower
                ):
                    return html
            except SwitchConnectionError:
                continue

        raise SwitchConnectionError(
            "Could not find IP configuration page in menu structure. "
            "Try re-running 03_menu_extraction.py or check "
            "menu_structure.json."
        )

    def get_current_ip_config(
        self,
        menu_file: Optional[str] = None,
    ) -> Dict[str, str]:
        """Get current IP configuration from the switch.

        Args:
            menu_file: Path to menu_structure.json file for menu-aware
                navigation. Optional.

        Returns:
            Dictionary with current IP settings (ip, netmask, gateway).

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to fetch configuration.
        """
        html = self.navigate_to_ip_config(menu_file)
        soup = BeautifulSoup(html, "html.parser")

        config = {}

        # Look for input fields with common IP-related names
        inputs = soup.find_all("input")
        for inp in inputs:
            name_attr = inp.get("name", "")
            name = str(name_attr).lower() if name_attr else ""
            value_attr = inp.get("value", "")
            value = str(value_attr) if value_attr else ""

            if "ip" in name and "addr" in name:
                config["ip_address"] = value
            elif "netmask" in name or "subnet" in name:
                config["subnet_mask"] = value
            elif "gateway" in name or "gw" in name:
                config["gateway"] = value
            elif "dns" in name:
                if "dns1" not in config:
                    config["dns1"] = value
                else:
                    config["dns2"] = value

        return config

    def change_ip_address(
        self,
        new_ip: str,
        subnet_mask: str,
        gateway: Optional[str] = None,
        dns1: Optional[str] = None,
        dns2: Optional[str] = None,
        menu_file: Optional[str] = None,
    ) -> bool:
        """Change the switch IP address configuration.

        Args:
            new_ip: New IP address.
            subnet_mask: Subnet mask.
            gateway: Default gateway (optional).
            dns1: Primary DNS server (optional).
            dns2: Secondary DNS server (optional).
            menu_file: Path to menu_structure.json file for menu-aware
                navigation. Optional.

        Returns:
            True if configuration change submitted successfully.

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to submit configuration.

        Note:
            The switch may reboot or disconnect after applying changes.
            You will need to reconnect to the new IP address.
        """
        # Get the IP configuration page
        html = self.navigate_to_ip_config(menu_file)
        soup = BeautifulSoup(html, "html.parser")

        # Find the configuration form
        form = None
        for f in soup.find_all("form"):
            # Look for forms with IP-related inputs
            inputs = f.find_all("input")
            for inp in inputs:
                name_attr = inp.get("name", "")
                name = str(name_attr).lower() if name_attr else ""
                if "ip" in name or "netmask" in name:
                    form = f
                    break
            if form:
                break

        if not form:
            raise SwitchConnectionError("Could not find IP configuration form")

        # Build form data
        form_data = {}

        # Add all existing form fields
        for inp in form.find_all("input"):
            name_attr = inp.get("name", "")
            name = str(name_attr) if name_attr else ""
            if name:
                value_attr = inp.get("value", "")
                value = str(value_attr) if value_attr else ""
                form_data[name] = value

        # Update with new IP configuration
        for name in form_data.keys():
            name_lower = name.lower()
            if "ip" in name_lower and "addr" in name_lower:
                form_data[name] = new_ip
            elif "netmask" in name_lower or "subnet" in name_lower:
                form_data[name] = subnet_mask
            elif "gateway" in name_lower or "gw" in name_lower:
                if gateway:
                    form_data[name] = gateway
            elif "dns" in name_lower:
                if dns1 and "dns1" in name_lower:
                    form_data[name] = dns1
                elif dns2 and "dns2" in name_lower:
                    form_data[name] = dns2

        # Get form action
        action_attr = form.get("action", "")
        action = str(action_attr) if action_attr else ""
        if not action:
            # Form submits to same page
            action = "network.html"

        # Submit the form
        try:
            self.post_page(action, form_data)
            return True
        except SwitchConnectionError:
            # Connection may be lost due to IP change
            # This is expected behavior
            return True

    def get_main_page(self) -> str:
        """Fetch the main/index page after authentication.

        Returns:
            HTML content of the main page.

        Raises:
            SwitchAuthError: If not authenticated.
            SwitchConnectionError: If unable to fetch the page.
        """
        # Common main page URLs
        main_urls = [
            "index.html",
            "index.htm",
            "main.html",
            "main.htm",
            "home.html",
            "home.htm",
            "status.html",
            "status.htm",
        ]

        for url in main_urls:
            try:
                html = self.get_page(url)
                # Verify this is actually a page with navigation
                if len(html) > 1000:  # Reasonable page size
                    return html
            except SwitchConnectionError:
                continue

        # If no specific page worked, try root
        return self.get_page("/")

    def extract_navigation(self, html: str) -> List[Dict[str, Any]]:
        """Extract navigation menu items from HTML.

        Analyzes HTML structure to find navigation elements like nav, menu,
        ul/li structures, and extract menu items with their URLs.

        Args:
            html: HTML content to parse.

        Returns:
            List of menu items, each containing label and url keys.
        """
        soup = BeautifulSoup(html, "html.parser")
        menu_items: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()

        # Strategy 1: Find <nav> elements
        nav_elements = soup.find_all("nav")
        for nav in nav_elements:
            items = self._extract_links_from_element(nav)
            for item in items:
                if item["url"] not in seen_urls:
                    menu_items.append(item)
                    seen_urls.add(item["url"])

        # Strategy 2: Find elements with menu-related classes
        menu_classes = [
            "menu",
            "navigation",
            "nav",
            "sidebar",
            "sidemenu",
            "mainmenu",
        ]
        for class_name in menu_classes:
            elements = soup.find_all(
                class_=lambda c: c and class_name in c.lower()
            )
            for elem in elements:
                items = self._extract_links_from_element(elem)
                for item in items:
                    if item["url"] not in seen_urls:
                        menu_items.append(item)
                        seen_urls.add(item["url"])

        # Strategy 3: Find <ul> elements that might be menus
        ul_elements = soup.find_all("ul")
        for ul in ul_elements:
            # Check if this ul contains multiple links
            links = ul.find_all("a")
            if len(links) >= 3:  # At least 3 links suggests a menu
                items = self._extract_links_from_element(ul)
                for item in items:
                    if item["url"] not in seen_urls:
                        menu_items.append(item)
                        seen_urls.add(item["url"])

        # Strategy 4: Find frames/iframes (common in older switch interfaces)
        frames = soup.find_all(["frame", "iframe"])
        for frame in frames:
            src_attr = frame.get("src", "")
            src = str(src_attr) if src_attr else ""
            name_attr = frame.get("name", "") or frame.get("id", "")
            name = str(name_attr) if name_attr else "frame"
            if src and src not in seen_urls:
                menu_items.append(
                    {
                        "label": name,
                        "url": src,
                        "type": "frame",
                    }
                )
                seen_urls.add(src)

        return menu_items

    def _extract_links_from_element(
        self, element: Tag
    ) -> List[Dict[str, Any]]:
        """Extract links from a BeautifulSoup element.

        Args:
            element: BeautifulSoup Tag to extract links from.

        Returns:
            List of dictionaries with label and url keys.
        """
        links = []
        for link in element.find_all("a"):
            href_attr = link.get("href", "")
            href = str(href_attr) if href_attr else ""
            if (
                not href
                or href.startswith("#")
                or href.startswith("javascript:")
            ):
                continue

            # Get link text
            text = link.get_text(strip=True)
            if not text:
                # Try to get text from title or other attributes
                title_attr = link.get("title", "")
                alt_attr = link.get("alt", "")
                text = (
                    str(title_attr)
                    if title_attr
                    else str(alt_attr) if alt_attr else href
                )

            links.append(
                {
                    "label": text,
                    "url": href,
                }
            )

        return links

    def extract_menu_from_js(self, js_content: str) -> List[Dict[str, Any]]:
        """Extract menu structure from JavaScript code.

        Looks for common JavaScript patterns used to define menus:
        - Array definitions (var menu = [...])
        - Object definitions (var menuConfig = {...})
        - Function calls that build menus

        Args:
            js_content: JavaScript source code.

        Returns:
            List of menu items extracted from JavaScript.
        """
        menu_items: List[Dict[str, Any]] = []

        # Pattern 1: Array of menu items
        # Example: var menu = [{label:"Network",url:"network.html"}, ...]
        array_pattern = r"(?:var|let|const)\s+\w*[Mm]enu\w*\s*=\s*\[(.*?)\]"
        matches = re.finditer(array_pattern, js_content, re.DOTALL)

        for match in matches:
            array_content = match.group(1)
            # Try to parse as JSON-like structure
            # Extract {key:value} or {"key":"value"} patterns
            items = re.finditer(
                r"\{([^}]*?)\}",
                array_content,
            )
            for item_match in items:
                item_str = item_match.group(1)
                menu_item = self._parse_js_object(item_str)
                if menu_item and "url" in menu_item:
                    menu_items.append(menu_item)

        # Pattern 2: Direct assignments
        # Example: menu[0] = {label:"Network", url:"network.html"};
        assignment_pattern = r"\w+\[\d+\]\s*=\s*\{([^}]*?)\}"
        matches = re.finditer(assignment_pattern, js_content)

        for match in matches:
            item_str = match.group(1)
            menu_item = self._parse_js_object(item_str)
            if menu_item and "url" in menu_item:
                menu_items.append(menu_item)

        return menu_items

    def _parse_js_object(self, js_obj_str: str) -> Dict[str, Any]:
        """Parse a JavaScript object string into a Python dictionary.

        Args:
            js_obj_str: JavaScript object content (without braces).

        Returns:
            Dictionary with extracted key-value pairs.
        """
        result: Dict[str, Any] = {}

        # Extract key:value or "key":"value" pairs
        # Handle both quoted and unquoted keys/values
        pair_pattern = r'["\']?(\w+)["\']?\s*:\s*["\']?([^,"\']+)["\']?'
        matches = re.finditer(pair_pattern, js_obj_str)

        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result[key] = value

        return result

    def discover_pages(self, html: str) -> List[Dict[str, Any]]:
        """Discover all accessible pages from the main page.

        Combines HTML navigation extraction with JavaScript menu parsing
        to build a comprehensive list of available pages.

        Args:
            html: HTML content of the main page.

        Returns:
            List of discovered pages with metadata.
        """
        discovered: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()

        # Extract navigation from HTML
        nav_items = self.extract_navigation(html)
        for item in nav_items:
            if item["url"] not in seen_urls:
                discovered.append(item)
                seen_urls.add(item["url"])

        # Extract JavaScript content
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string:
                # Look for menu definitions
                js_items = self.extract_menu_from_js(script.string)
                for item in js_items:
                    if item["url"] not in seen_urls:
                        discovered.append(item)
                        seen_urls.add(item["url"])

            # Check for external JavaScript files
            src_attr = script.get("src", "")
            src = str(src_attr) if src_attr else ""
            if src:
                try:
                    # Fetch external JS file
                    js_content = self.get_page(src)
                    js_items = self.extract_menu_from_js(js_content)
                    for item in js_items:
                        if item["url"] not in seen_urls:
                            discovered.append(item)
                            seen_urls.add(item["url"])
                except Exception:
                    # Skip if unable to fetch
                    pass

        return discovered

    def build_menu_structure(
        self,
        pages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build a hierarchical menu structure from discovered pages.

        Analyzes page URLs and labels to infer parent-child relationships
        and organize pages into a tree structure.

        Args:
            pages: List of discovered pages.

        Returns:
            Dictionary representing menu hierarchy.
        """
        # Group pages by category based on URL patterns
        categories: Dict[str, List[Dict[str, Any]]] = {
            "network": [],
            "system": [],
            "security": [],
            "port": [],
            "vlan": [],
            "status": [],
            "monitoring": [],
            "config": [],
            "other": [],
        }

        for page in pages:
            url = page["url"].lower()
            categorized = False

            for category in categories.keys():
                if (
                    category in url
                    or category in page.get("label", "").lower()
                ):
                    categories[category].append(page)
                    categorized = True
                    break

            if not categorized:
                categories["other"].append(page)

        # Build menu structure
        menu: List[Dict[str, Any]] = []

        for category, items in categories.items():
            if items:
                menu.append(
                    {
                        "id": category,
                        "label": category.capitalize(),
                        "children": items,
                    }
                )

        return {"menu": menu, "total_pages": len(pages)}

    def close(self) -> None:
        """Close the session and clean up resources."""
        try:
            self.logout()
        except Exception:
            pass
        finally:
            self.session.close()

    def __enter__(self) -> "SwitchSession":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()
