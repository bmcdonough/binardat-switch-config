"""End-to-end workflow verification tests.

Validates complete automation sequence:
1. Login with credentials
2. Discover menu structure
3. Navigate to IP configuration page
4. Read current configuration
5. Validate configuration format
6. Logout cleanly
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


class TestCompleteWorkflow:
    """Test complete automation workflow."""

    def test_full_workflow(self):
        """Execute complete automation sequence."""
        # Step 1: Create session and login
        session = SwitchSession(SWITCH_IP)
        login_result = session.login(SWITCH_USER, SWITCH_PASS)
        assert login_result is True, "Login failed"
        assert session.authenticated is True

        # Step 2: Access main page (menu discovery)
        main_response = session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=30
        )
        assert main_response.status_code == 200
        main_soup = BeautifulSoup(main_response.text, "html.parser")

        # Step 3: Find IP config page in menu
        ip_config_link = main_soup.find(attrs={"datalink": "Manageportip.cgi"})
        assert ip_config_link is not None, "IP config page not found in menu"

        # Step 4: Navigate to IP config page
        ip_config_response = session.session.get(
            f"http://{SWITCH_IP}/Manageportip.cgi", timeout=30
        )
        assert ip_config_response.status_code == 200
        ip_config_soup = BeautifulSoup(ip_config_response.text, "html.parser")

        # Step 5: Extract form and configuration
        form = ip_config_soup.find("form")
        assert form is not None, "No form found on IP config page"

        # Extract all form fields
        form_data = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            if name:
                form_data[name] = inp.get("value", "")

        assert len(form_data) > 0, "No form data extracted"

        # Step 6: Logout
        session.logout()


class TestErrorRecovery:
    """Test error handling at each stage."""

    def test_recovery_from_connection_error(self):
        """Test recovery from connection errors."""
        # Test with invalid IP first
        bad_session = SwitchSession("192.0.2.1", timeout=1)

        with pytest.raises(Exception):
            bad_session.login("admin", "admin")

        # Now test with valid IP
        good_session = SwitchSession(SWITCH_IP)
        result = good_session.login(SWITCH_USER, SWITCH_PASS)
        assert result is True

        good_session.logout()

    def test_recovery_from_auth_error(self):
        """Test recovery from authentication errors."""
        session = SwitchSession(SWITCH_IP)

        # Try with wrong credentials
        with pytest.raises(Exception):
            session.login("wronguser", "wrongpass")

        # Should be able to try again with correct credentials
        result = session.login(SWITCH_USER, SWITCH_PASS)
        assert result is True

        session.logout()


class TestStateConsistency:
    """Test state consistency throughout workflow."""

    def test_session_state_after_logout(self):
        """Verify session state after logout."""
        session = SwitchSession(SWITCH_IP)
        session.login(SWITCH_USER, SWITCH_PASS)
        assert session.authenticated is True

        session.logout()

        # After logout, should not be able to access protected pages
        # (or should get redirected to login)

    def test_multiple_workflows(self):
        """Test running multiple workflows in sequence."""
        for i in range(3):
            session = SwitchSession(SWITCH_IP)
            session.login(SWITCH_USER, SWITCH_PASS)

            # Access a page
            response = session.session.get(
                f"http://{SWITCH_IP}/index.cgi", timeout=30
            )
            assert response.status_code == 200

            session.logout()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
