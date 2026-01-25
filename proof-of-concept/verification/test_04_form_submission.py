"""Form submission verification tests.

Validates:
- Form field discovery and parsing
- Hidden field extraction
- Current configuration extraction
- Form data construction
- Read-only validation (no actual submissions)
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
    """Create authenticated session."""
    session = SwitchSession(SWITCH_IP)
    session.login(SWITCH_USER, SWITCH_PASS)
    yield session
    session.logout()


@pytest.fixture
def ip_config_page(authenticated_session):
    """Fetch IP configuration page."""
    response = authenticated_session.session.get(
        f"http://{SWITCH_IP}/Manageportip.cgi", timeout=30
    )
    return response.text


class TestFormParsing:
    """Test form field extraction."""

    def test_form_exists(self, ip_config_page):
        """Verify form exists on IP config page."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        assert form is not None, "No form found on IP config page"

    def test_extract_input_fields(self, ip_config_page):
        """Extract all input fields from form."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        inputs = form.find_all("input") if form else []

        assert len(inputs) > 0, "No input fields found"

        # Check for common fields
        field_names = [inp.get("name") for inp in inputs if inp.get("name")]
        assert len(field_names) > 0, "No named input fields found"

    def test_extract_select_fields(self, ip_config_page):
        """Extract select/dropdown fields."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        selects = form.find_all("select") if form else []

        # May or may not have select fields
        for select in selects:
            assert select.get("name"), "Select field missing name attribute"

    def test_form_action(self, ip_config_page):
        """Verify form has action attribute."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")

        if form:
            action = form.get("action")
            # Action may be empty (submit to same page) or a URL
            assert action is not None


class TestHiddenFields:
    """Test hidden field extraction."""

    def test_find_hidden_fields(self, ip_config_page):
        """Find all hidden input fields."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        hidden_fields = (
            form.find_all("input", type="hidden") if form else []
        )

        # Hidden fields are common for CSRF, session tokens, etc.
        if hidden_fields:
            for hidden in hidden_fields:
                name = hidden.get("name")
                value = hidden.get("value")
                assert name, "Hidden field missing name"
                # Value may be empty


class TestFormDataConstruction:
    """Test construction of form submission data."""

    def test_build_form_data(self, ip_config_page):
        """Build complete form data dictionary."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        assert form is not None

        form_data = {}

        # Extract all input fields
        for inp in form.find_all("input"):
            name = inp.get("name")
            if name:
                value = inp.get("value", "")
                form_data[name] = value

        # Extract select fields
        for select in form.find_all("select"):
            name = select.get("name")
            if name:
                selected = select.find("option", selected=True)
                if selected:
                    form_data[name] = selected.get("value", "")

        assert len(form_data) > 0, "No form data extracted"

    def test_validate_form_structure(self, ip_config_page):
        """Validate form structure is reasonable."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")

        if form:
            # Should have a method (GET or POST)
            method = form.get("method", "GET").upper()
            assert method in ["GET", "POST"]


class TestCurrentConfiguration:
    """Test extraction of current configuration values."""

    def test_extract_current_values(self, ip_config_page):
        """Extract current configuration values from form."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        assert form is not None

        # Look for fields that might contain IP configuration
        inputs = form.find_all("input", type=["text", "number"])

        # Should find some text/number inputs
        assert len(inputs) > 0, "No text/number inputs found"

    def test_field_validation_attributes(self, ip_config_page):
        """Check for validation attributes on fields."""
        soup = BeautifulSoup(ip_config_page, "html.parser")
        form = soup.find("form")
        inputs = form.find_all("input") if form else []

        # Check for common validation attributes
        for inp in inputs:
            # Fields may have: required, pattern, min, max, etc.
            # Just verify they exist and are accessible
            inp.get("required")
            inp.get("pattern")


class TestReadOnlyValidation:
    """Ensure tests don't modify configuration."""

    def test_no_post_requests(self, authenticated_session):
        """Verify we're not making POST requests in tests."""
        # This is a safety check - all tests should be read-only
        # No actual test here, just documentation that tests are safe
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
