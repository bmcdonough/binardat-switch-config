"""Example test module demonstrating test structure."""

from binardat_switch_config import __version__


def test_version() -> None:
    """Test that version is defined and follows date format."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    # Date format: YYYY.MM.DD
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
