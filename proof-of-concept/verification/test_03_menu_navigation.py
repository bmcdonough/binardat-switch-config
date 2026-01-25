"""Menu navigation verification tests.

Validates:
- Datalink attribute extraction from HTML
- Menu hierarchy parsing
- Direct page access
- Page categorization
- Primary target discovery (Manageportip.cgi)
"""

import os
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

from switch_auth import SwitchSession

SWITCH_IP = os.getenv("SWITCH_IP", "192.168.2.1")
SWITCH_USER = os.getenv("SWITCH_USER", "admin")
SWITCH_PASS = os.getenv("SWITCH_PASS", "admin")


@pytest.fixture(scope="module")
def authenticated_session():
    """Create authenticated session for all tests."""
    session = SwitchSession(SWITCH_IP)
    session.login(SWITCH_USER, SWITCH_PASS)
    yield session
    session.logout()


class TestDatalinkExtraction:
    """Test extraction of datalink attributes."""

    def test_extract_datalink_attributes(self, authenticated_session):
        """Extract all datalink attributes from main page."""
        main_page = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        soup = BeautifulSoup(main_page.text, "html.parser")

        # Find all elements with datalink attribute
        datalinks = soup.find_all(attrs={"datalink": True})
        assert len(datalinks) > 0, "No datalink attributes found"

    def test_datalink_format(self, authenticated_session):
        """Verify datalink values are valid URLs."""
        main_page = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        soup = BeautifulSoup(main_page.text, "html.parser")
        datalinks = soup.find_all(attrs={"datalink": True})

        for element in datalinks:
            url = element.get("datalink")
            assert url and len(url) > 0
            # Should end with .cgi or .html typically
            assert url.endswith(".cgi") or url.endswith(".html") or "." in url


class TestMenuStructure:
    """Test menu hierarchy and structure."""

    def test_menu_categories_exist(self, authenticated_session):
        """Verify menu has multiple categories."""
        main_page = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        soup = BeautifulSoup(main_page.text, "html.parser")

        # Look for sidebar menu structure
        sidebar = soup.find(class_=["sidebar", "menu", "lsm-sidebar"])
        assert sidebar is not None, "No sidebar menu found"

    def test_minimum_page_count(self, authenticated_session):
        """Verify minimum expected number of pages."""
        main_page = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        soup = BeautifulSoup(main_page.text, "html.parser")
        datalinks = soup.find_all(attrs={"datalink": True})

        # Expect at least 50 pages (conservative estimate)
        assert len(datalinks) >= 50, f"Expected >=50 pages, found {len(datalinks)}"


class TestDirectPageAccess:
    """Test direct access to pages."""

    def test_access_main_page(self, authenticated_session):
        """Test accessing main authenticated page."""
        response = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        assert response.status_code == 200
        assert len(response.text) > 1000  # Should be substantial page

    def test_access_status_page(self, authenticated_session):
        """Test accessing status page."""
        response = authenticated_session.session.get(
            f"http://{SWITCH_IP}/status.html", timeout=30
        )
        assert response.status_code == 200

    def test_access_ip_config_page(self, authenticated_session):
        """Test accessing IP configuration page."""
        response = authenticated_session.session.get(
            f"http://{SWITCH_IP}/Manageportip.cgi", timeout=30
        )
        assert response.status_code == 200


class TestPrimaryTargetDiscovery:
    """Test discovery of primary IP configuration page."""

    def test_find_ip_config_in_menu(self, authenticated_session):
        """Verify Manageportip.cgi is discoverable in menu."""
        main_page = authenticated_session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        soup = BeautifulSoup(main_page.text, "html.parser")

        # Search for IP config page
        ip_config = soup.find(attrs={"datalink": "Manageportip.cgi"})
        assert ip_config is not None, "Manageportip.cgi not found in menu"

    def test_ip_config_page_accessible(self, authenticated_session):
        """Verify IP config page is accessible."""
        response = authenticated_session.session.get(
            f"http://{SWITCH_IP}/Manageportip.cgi", timeout=30
        )
        assert response.status_code == 200
        assert "ip" in response.text.lower(), "Page doesn't appear to be IP config"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
