"""RC4 encryption verification tests.

This module validates the RC4 encryption implementation against the
Binardat switch's JavaScript implementation. It tests known vectors,
format validation, round-trip encryption/decryption, and edge cases.

Test Categories:
1. Known test vectors from switch
2. Binardat-specific format validation
3. Encryption/decryption round-trip
4. Edge cases (empty strings, special characters, unicode)
5. Cross-validation with JavaScript RC4
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rc4_crypto import (
    encrypt_credentials,
    rc4_decrypt,
    rc4_encrypt,
    rc4_encrypt_base64,
    rc4_encrypt_binardat,
    verify_rc4_implementation,
)


class TestKnownVectors:
    """Test RC4 encryption against known switch outputs."""

    def test_admin_admin_credentials(self):
        """Test encryption of 'admin' with known key."""
        key = "iensuegdul27c90d"
        username = "admin"
        password = "admin"

        # Known output from JavaScript implementation
        expected = "126,,103,,178,,61,,175,,"

        # Test username encryption
        encrypted_user = rc4_encrypt_binardat(username, key)
        assert (
            encrypted_user == expected
        ), f"Expected {expected}, got {encrypted_user}"

        # Test password encryption (same input/key = same output)
        encrypted_pass = rc4_encrypt_binardat(password, key)
        assert (
            encrypted_pass == expected
        ), f"Expected {expected}, got {encrypted_pass}"

    def test_encrypt_credentials_function(self):
        """Test the combined credential encryption function."""
        key = "iensuegdul27c90d"
        username = "admin"
        password = "admin"
        expected = "126,,103,,178,,61,,175,,"

        enc_user, enc_pass = encrypt_credentials(username, password, key)

        assert enc_user == expected, f"Username: expected {expected}, got {enc_user}"
        assert enc_pass == expected, f"Password: expected {expected}, got {enc_pass}"

    def test_different_inputs_different_outputs(self):
        """Verify that different inputs produce different outputs."""
        key = "iensuegdul27c90d"

        encrypted_admin = rc4_encrypt_binardat("admin", key)
        encrypted_user = rc4_encrypt_binardat("user", key)
        encrypted_test = rc4_encrypt_binardat("test", key)

        # All should be different
        assert encrypted_admin != encrypted_user
        assert encrypted_admin != encrypted_test
        assert encrypted_user != encrypted_test


class TestBinardatFormat:
    """Test Binardat-specific output format."""

    def test_delimiter_format(self):
        """Verify output uses double-comma delimiter."""
        result = rc4_encrypt_binardat("test", "key")

        # Should end with double comma
        assert result.endswith(
            ",,"
        ), f"Output should end with ',,', got: {result[-10:]}"

        # Should contain only digits and commas
        for char in result:
            assert char.isdigit() or char == ",", f"Invalid character: {char}"

    def test_decimal_format(self):
        """Verify output is decimal bytes, not hex."""
        result = rc4_encrypt_binardat("test", "key")

        # Remove delimiters and split into numbers
        numbers = [n for n in result.split(",,") if n]

        # All should be valid decimal numbers
        for num_str in numbers:
            num = int(num_str)
            assert 0 <= num <= 255, f"Byte value {num} out of range (0-255)"

    def test_no_padding(self):
        """Verify no padding is added to output."""
        plaintext = "test"
        result = rc4_encrypt_binardat(plaintext, "key")

        # Count number of byte values (split by delimiter)
        byte_count = len([b for b in result.split(",,") if b])

        # Should match plaintext length
        assert (
            byte_count == len(plaintext)
        ), f"Expected {len(plaintext)} bytes, got {byte_count}"

    def test_consistent_format(self):
        """Verify format is consistent across different inputs."""
        test_cases = ["a", "ab", "abc", "test", "admin", "password123"]
        key = "testkey"

        for plaintext in test_cases:
            result = rc4_encrypt_binardat(plaintext, key)

            # Verify format: numbers separated by ,,
            parts = result.split(",,")

            # Last part should be empty (ends with ,,)
            assert parts[-1] == "", f"Output should end with ,, for '{plaintext}'"

            # All other parts should be numbers
            for part in parts[:-1]:
                assert part.isdigit(), f"Invalid part '{part}' in output"


class TestRoundTrip:
    """Test encryption/decryption round-trip."""

    def test_basic_roundtrip_hex(self):
        """Test encrypt → decrypt returns original (hex format)."""
        plaintext = "Hello, World!"
        key = "testkey123"

        encrypted = rc4_encrypt(plaintext, key)
        decrypted = rc4_decrypt(encrypted, key)

        assert (
            decrypted == plaintext
        ), f"Round-trip failed: '{plaintext}' → '{decrypted}'"

    def test_multiple_plaintexts(self):
        """Test round-trip with various plaintext strings."""
        test_cases = [
            "admin",
            "password",
            "user123",
            "P@ssw0rd!",
            "test@example.com",
            "192.168.1.1",
        ]
        key = "testkey"

        for plaintext in test_cases:
            encrypted = rc4_encrypt(plaintext, key)
            decrypted = rc4_decrypt(encrypted, key)

            assert decrypted == plaintext, f"Round-trip failed for '{plaintext}'"

    def test_multiple_keys(self):
        """Test round-trip with various encryption keys."""
        plaintext = "test"
        keys = ["key1", "key2", "longkey123456", "short", "iensuegdul27c90d"]

        for key in keys:
            encrypted = rc4_encrypt(plaintext, key)
            decrypted = rc4_decrypt(encrypted, key)

            assert (
                decrypted == plaintext
            ), f"Round-trip failed with key '{key}'"

    def test_wrong_key_fails_decryption(self):
        """Verify that wrong key produces incorrect decryption."""
        plaintext = "secret"
        correct_key = "key1"
        wrong_key = "key2"

        encrypted = rc4_encrypt(plaintext, correct_key)
        decrypted_wrong = rc4_decrypt(encrypted, wrong_key)

        # Should NOT match original
        assert (
            decrypted_wrong != plaintext
        ), "Decryption with wrong key should fail"


class TestEdgeCases:
    """Test edge cases and special inputs."""

    def test_empty_string(self):
        """Test encryption of empty string."""
        result = rc4_encrypt_binardat("", "key")

        # Empty input should produce empty output (just delimiter)
        assert result == "", f"Empty string should produce empty output, got: {result}"

    def test_single_character(self):
        """Test encryption of single character."""
        result = rc4_encrypt_binardat("a", "key")

        # Should produce single byte value
        parts = [p for p in result.split(",,") if p]
        assert len(parts) == 1, f"Single char should produce one byte, got {len(parts)}"

    def test_special_characters(self):
        """Test encryption of special characters."""
        test_cases = [
            "!@#$%^&*()",
            "username@domain.com",
            "P@ssw0rd!",
            "192.168.1.1",
            "path/to/file",
        ]
        key = "testkey"

        for plaintext in test_cases:
            result = rc4_encrypt_binardat(plaintext, key)

            # Should produce output with correct length
            byte_count = len([b for b in result.split(",,") if b])
            assert (
                byte_count == len(plaintext)
            ), f"Length mismatch for '{plaintext}'"

    def test_numeric_strings(self):
        """Test encryption of numeric strings."""
        test_cases = ["123", "456789", "0", "192.168.1.1"]
        key = "key"

        for plaintext in test_cases:
            result = rc4_encrypt_binardat(plaintext, key)

            # Verify output format
            assert result.endswith(",,") or result == ""
            parts = [p for p in result.split(",,") if p]
            assert len(parts) == len(plaintext)

    def test_unicode_characters(self):
        """Test encryption of unicode characters."""
        # Note: May not work correctly with switch (ASCII only)
        test_cases = ["café", "naïve", "Zürich"]
        key = "key"

        for plaintext in test_cases:
            try:
                result = rc4_encrypt_binardat(plaintext, key)
                # Should produce output (even if switch doesn't support it)
                assert isinstance(result, str)
            except UnicodeEncodeError:
                # Expected for non-ASCII characters
                pass

    def test_very_long_plaintext(self):
        """Test encryption of long strings."""
        plaintext = "a" * 1000
        key = "key"

        result = rc4_encrypt_binardat(plaintext, key)

        # Verify correct length
        byte_count = len([b for b in result.split(",,") if b])
        assert byte_count == 1000, f"Expected 1000 bytes, got {byte_count}"

    def test_very_long_key(self):
        """Test with very long encryption key."""
        plaintext = "test"
        key = "k" * 1000

        result = rc4_encrypt_binardat(plaintext, key)

        # Should still work
        byte_count = len([b for b in result.split(",,") if b])
        assert byte_count == len(plaintext)


class TestBase64Encoding:
    """Test base64 encoding variant."""

    def test_base64_format(self):
        """Test RC4 encryption with base64 output."""
        plaintext = "password"
        key = "key123"

        result = rc4_encrypt_base64(plaintext, key)

        # Base64 should only contain valid base64 characters
        import string

        valid_chars = string.ascii_letters + string.digits + "+/="
        for char in result:
            assert char in valid_chars, f"Invalid base64 character: {char}"

    def test_base64_vs_hex(self):
        """Verify base64 and hex formats encode the same data."""
        plaintext = "test"
        key = "key"

        hex_result = rc4_encrypt(plaintext, key)
        base64_result = rc4_encrypt_base64(plaintext, key)

        # Decode both and verify they're different formats of same data
        import base64

        # Convert base64 to hex for comparison
        base64_bytes = base64.b64decode(base64_result)
        base64_as_hex = base64_bytes.hex()

        assert (
            hex_result == base64_as_hex
        ), "Base64 and hex should encode same ciphertext"


class TestCrossValidation:
    """Cross-validation tests (require manual JavaScript comparison)."""

    def test_javascript_comparison_vectors(self):
        """Test vectors for manual JavaScript validation.

        To validate against JavaScript:
        1. Open switch login page in browser
        2. Open browser console
        3. Run: rc4("iensuegdul27c90d", "admin")
        4. Compare output with Python output below
        """
        key = "iensuegdul27c90d"
        test_cases = [
            ("admin", "126,,103,,178,,61,,175,,"),
            # Add more known vectors as discovered
        ]

        for plaintext, expected in test_cases:
            result = rc4_encrypt_binardat(plaintext, key)
            assert result == expected, (
                f"JavaScript mismatch:\n"
                f"  Input: '{plaintext}'\n"
                f"  Expected: {expected}\n"
                f"  Got:      {result}"
            )


class TestVerifyFunction:
    """Test the verify_rc4_implementation helper function."""

    def test_verify_function_pass(self):
        """Test verify function with matching output."""
        plaintext = "test"
        key = "key123"

        # Get actual output
        expected = rc4_encrypt(plaintext, key)

        # Verify should return True
        result = verify_rc4_implementation(plaintext, key, expected)
        assert result is True, "Verify should return True for matching output"

    def test_verify_function_fail(self):
        """Test verify function with non-matching output."""
        plaintext = "test"
        key = "key123"

        # Use wrong expected output
        wrong_expected = "0000000000"

        # Verify should return False
        result = verify_rc4_implementation(plaintext, key, wrong_expected)
        assert result is False, "Verify should return False for non-matching output"

    def test_verify_case_insensitive(self):
        """Test that verify function is case-insensitive for hex."""
        plaintext = "test"
        key = "key123"

        hex_output = rc4_encrypt(plaintext, key)
        hex_upper = hex_output.upper()
        hex_lower = hex_output.lower()

        # Both should verify
        assert verify_rc4_implementation(plaintext, key, hex_upper)
        assert verify_rc4_implementation(plaintext, key, hex_lower)


# Pytest fixtures
@pytest.fixture
def switch_key():
    """Provide the switch RC4 key."""
    return "iensuegdul27c90d"


@pytest.fixture
def test_credentials():
    """Provide test credentials."""
    return {"username": "admin", "password": "admin"}


# Integration test using fixtures
def test_full_credential_encryption(switch_key, test_credentials):
    """Test complete credential encryption flow."""
    enc_user, enc_pass = encrypt_credentials(
        test_credentials["username"], test_credentials["password"], switch_key
    )

    # Both should match known output
    expected = "126,,103,,178,,61,,175,,"
    assert enc_user == expected
    assert enc_pass == expected

    # Format validation
    assert enc_user.endswith(",,")
    assert enc_pass.endswith(",,")


if __name__ == "__main__":
    # Run pytest if executed directly
    pytest.main([__file__, "-v"])
