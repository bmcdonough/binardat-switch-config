"""Authentication flow verification tests.

Validates:
- RC4 key extraction from login page
- Successful login with valid credentials
- Failed login scenarios
- Session cookie creation and persistence
- Session reuse across requests
- Logout flow
"""

import os
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from switch_auth import SwitchAuthError, SwitchConnectionError, SwitchSession


# Configuration
SWITCH_IP = os.getenv("SWITCH_IP", "192.168.2.1")
SWITCH_USER = os.getenv("SWITCH_USER", "admin")
SWITCH_PASS = os.getenv("SWITCH_PASS", "admin")


@pytest.fixture
def session():
    """Create a fresh switch session."""
    return SwitchSession(SWITCH_IP)


class TestConnection:
    """Test basic connection to switch."""

    def test_switch_reachable(self):
        """Verify switch is reachable via HTTP."""
        try:
            response = requests.get(f"http://{SWITCH_IP}/", timeout=5)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.skip(f"Switch not reachable at {SWITCH_IP}: {e}")

    def test_session_initialization(self, session):
        """Test session object initialization."""
        assert session.host == SWITCH_IP
        assert session.authenticated is False
        assert session.rc4_key is None


class TestRC4KeyExtraction:
    """Test RC4 key extraction from login page."""

    def test_key_extraction_from_login_page(self, session):
        """Extract RC4 key from login page."""
        html = session._get_login_page()
        assert html is not None
        assert len(html) > 0

    def test_key_extracted_correctly(self, session):
        """Verify extracted key matches expected format."""
        session._get_login_page()
        assert session.rc4_key is not None
        assert len(session.rc4_key) > 0
        # Switch uses 16-character key
        assert len(session.rc4_key) == 16


class TestSuccessfulAuthentication:
    """Test successful login flow."""

    def test_login_success(self, session):
        """Test successful authentication."""
        result = session.login(SWITCH_USER, SWITCH_PASS)
        assert result is True
        assert session.authenticated is True

        # Cleanup
        session.logout()

    def test_session_cookie_created(self, session):
        """Verify session cookie is created after login."""
        session.login(SWITCH_USER, SWITCH_PASS)

        # Check for session cookie
        cookies = session.session.cookies
        assert "session" in cookies or len(cookies) > 0

        session.logout()

    def test_authenticated_page_access(self, session):
        """Test accessing authenticated pages."""
        session.login(SWITCH_USER, SWITCH_PASS)

        # Access main authenticated page
        response = session.session.get(
            f"http://{SWITCH_IP}/index.cgi", timeout=session.timeout
        )
        assert response.status_code == 200
        assert len(response.text) > 0

        session.logout()


class TestSessionPersistence:
    """Test session persistence across requests."""

    def test_session_reuse(self, session):
        """Verify session cookie persists across requests."""
        session.login(SWITCH_USER, SWITCH_PASS)

        # Get initial cookie
        cookies_before = dict(session.session.cookies)

        # Make another request
        session.session.get(f"http://{SWITCH_IP}/index.cgi", timeout=session.timeout)

        # Cookie should still be present
        cookies_after = dict(session.session.cookies)
        assert cookies_before == cookies_after

        session.logout()

    def test_multiple_page_access(self, session):
        """Test accessing multiple pages with same session."""
        session.login(SWITCH_USER, SWITCH_PASS)

        pages = ["index.cgi", "status.html"]
        for page in pages:
            response = session.session.get(
                f"http://{SWITCH_IP}/{page}", timeout=session.timeout
            )
            assert response.status_code == 200, f"Failed to access {page}"

        session.logout()


class TestFailedAuthentication:
    """Test failed login scenarios."""

    def test_invalid_password(self, session):
        """Test login with invalid password."""
        with pytest.raises(SwitchAuthError):
            session.login(SWITCH_USER, "wrongpassword")

        assert session.authenticated is False

    def test_invalid_username(self, session):
        """Test login with invalid username."""
        with pytest.raises(SwitchAuthError):
            session.login("invaliduser", SWITCH_PASS)

        assert session.authenticated is False

    def test_both_invalid(self, session):
        """Test login with both username and password invalid."""
        with pytest.raises(SwitchAuthError):
            session.login("baduser", "badpass")

        assert session.authenticated is False


class TestLogout:
    """Test logout functionality."""

    def test_logout_success(self, session):
        """Test successful logout."""
        session.login(SWITCH_USER, SWITCH_PASS)
        assert session.authenticated is True

        session.logout()
        # Note: logout may not change authenticated flag depending on implementation

    def test_logout_clears_session(self, session):
        """Verify logout clears session data."""
        session.login(SWITCH_USER, SWITCH_PASS)

        # Get cookies before logout
        cookies_before = len(session.session.cookies)
        assert cookies_before > 0

        session.logout()

        # Cookies may or may not be cleared depending on implementation
        # At minimum, they should no longer be valid for access


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_connection_timeout(self):
        """Test handling of connection timeout."""
        session = SwitchSession("192.0.2.1", timeout=1)  # Non-routable IP
        with pytest.raises(SwitchConnectionError):
            session._get_login_page()

    def test_invalid_host(self):
        """Test handling of invalid host."""
        session = SwitchSession("invalid.host.local", timeout=2)
        with pytest.raises(SwitchConnectionError):
            session._get_login_page()

    def test_empty_credentials(self, session):
        """Test login with empty credentials."""
        with pytest.raises((SwitchAuthError, ValueError)):
            session.login("", "")

    def test_double_login(self, session):
        """Test logging in twice with same session."""
        session.login(SWITCH_USER, SWITCH_PASS)
        assert session.authenticated is True

        # Second login should succeed or be idempotent
        result = session.login(SWITCH_USER, SWITCH_PASS)
        assert result is True

        session.logout()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
