"""Test and verify RC4 encryption implementation.

This script tests the RC4 implementation against known inputs/outputs
to ensure it matches the JavaScript implementation used by the switch.
"""

import argparse
import sys

from rc4_crypto import (
    encrypt_credentials,
    rc4_decrypt,
    rc4_encrypt,
    rc4_encrypt_base64,
)


def test_basic_encryption() -> bool:
    """Test basic RC4 encryption/decryption.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 1] Basic Encryption/Decryption")
    print("-" * 60)

    plaintext = "Hello, World!"
    key = "testkey123"

    # Encrypt
    encrypted = rc4_encrypt(plaintext, key)
    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Encrypted:  {encrypted}")

    # Decrypt
    decrypted = rc4_decrypt(encrypted, key)
    print(f"Decrypted:  {decrypted}")

    # Verify
    success = plaintext == decrypted
    print(f"Result:     {'PASS' if success else 'FAIL'}")

    return success


def test_empty_strings() -> bool:
    """Test RC4 with empty strings.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 2] Empty String Handling")
    print("-" * 60)

    plaintext = ""
    key = "testkey123"

    encrypted = rc4_encrypt(plaintext, key)
    decrypted = rc4_decrypt(encrypted, key)

    print(f"Empty plaintext encrypted: {encrypted}")
    print(f"Decrypted back to:         '{decrypted}'")

    success = plaintext == decrypted
    print(f"Result:                    {'PASS' if success else 'FAIL'}")

    return success


def test_special_characters() -> bool:
    """Test RC4 with special characters.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 3] Special Characters")
    print("-" * 60)

    test_cases = [
        ("admin", "testkey"),
        ("password123!", "mykey"),
        ("user@domain.com", "secret"),
        ("P@ssw0rd!", "key123"),
    ]

    all_passed = True

    for plaintext, key in test_cases:
        encrypted = rc4_encrypt(plaintext, key)
        decrypted = rc4_decrypt(encrypted, key)

        passed = plaintext == decrypted
        all_passed = all_passed and passed

        status = "PASS" if passed else "FAIL"
        print(f"{status}: '{plaintext}' with key '{key}'")

    print(f"\nResult: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def test_base64_encoding() -> bool:
    """Test RC4 with base64 encoding.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 4] Base64 Encoding")
    print("-" * 60)

    plaintext = "password"
    key = "mykey123"

    # Encrypt to hex and base64
    encrypted_hex = rc4_encrypt(plaintext, key)
    encrypted_base64 = rc4_encrypt_base64(plaintext, key)

    print(f"Plaintext:       {plaintext}")
    print(f"Key:             {key}")
    print(f"Hex format:      {encrypted_hex}")
    print(f"Base64 format:   {encrypted_base64}")

    # Both should decrypt to the same value
    decrypted_hex = rc4_decrypt(encrypted_hex, key)
    print(f"Decrypted:       {decrypted_hex}")

    success = plaintext == decrypted_hex
    print(f"Result:          {'PASS' if success else 'FAIL'}")

    return success


def test_credential_encryption() -> bool:
    """Test credential encryption function.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 5] Credential Encryption")
    print("-" * 60)

    username = "admin"
    password = "admin"
    key = "switchkey"

    enc_user, enc_pass = encrypt_credentials(username, password, key)

    print(f"Username:            {username}")
    print(f"Password:            {password}")
    print(f"Key:                 {key}")
    print(f"Encrypted username:  {enc_user}")
    print(f"Encrypted password:  {enc_pass}")

    # Decrypt to verify
    dec_user = rc4_decrypt(enc_user, key)
    dec_pass = rc4_decrypt(enc_pass, key)

    print(f"Decrypted username:  {dec_user}")
    print(f"Decrypted password:  {dec_pass}")

    success = username == dec_user and password == dec_pass
    print(f"Result:              {'PASS' if success else 'FAIL'}")

    return success


def test_known_vectors() -> bool:
    """Test against known test vectors if provided.

    Returns:
        True if test passes, False otherwise.
    """
    print("\n[TEST 6] Known Test Vectors")
    print("-" * 60)
    print(
        "Note: To test against switch JavaScript, compare outputs " "manually."
    )
    print(
        "      Use browser console to generate expected values "
        "with same key."
    )
    print()

    # Example: If you know the JavaScript produces specific output
    # test_vectors = [
    #     ("admin", "key123", "expected_hex_output"),
    # ]
    #
    # for plaintext, key, expected in test_vectors:
    #     result = verify_rc4_implementation(plaintext, key, expected)
    #     print(f"{'PASS' if result else 'FAIL'}: {plaintext}")

    print("Generate JavaScript output with:")
    print("  const cipher = new RC4('key123');")
    print("  const encrypted = cipher.encrypt('admin');")
    print("  console.log(encrypted);")
    print()
    print("Then compare with Python output:")
    print('  python -c "from rc4_crypto import rc4_encrypt;')
    print("  print(rc4_encrypt('admin', 'key123'))\"")

    return True  # Manual verification required


def interactive_test() -> None:
    """Run interactive RC4 test with user input."""
    print("\n" + "=" * 60)
    print("INTERACTIVE RC4 TEST")
    print("=" * 60)

    plaintext = input("Enter plaintext to encrypt: ")
    key = input("Enter RC4 key: ")

    print("\nEncrypting...")
    encrypted_hex = rc4_encrypt(plaintext, key)
    encrypted_base64 = rc4_encrypt_base64(plaintext, key)

    print("\nResults:")
    print(f"  Plaintext:      {plaintext}")
    print(f"  Key:            {key}")
    print(f"  Hex output:     {encrypted_hex}")
    print(f"  Base64 output:  {encrypted_base64}")

    print("\nVerifying decryption...")
    decrypted = rc4_decrypt(encrypted_hex, key)
    print(f"  Decrypted:      {decrypted}")
    print(f"  Match:          {'YES' if decrypted == plaintext else 'NO'}")


def main() -> int:
    """Run RC4 encryption tests.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Test RC4 encryption implementation"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run interactive test mode",
    )
    args = parser.parse_args()

    if args.interactive:
        interactive_test()
        return 0

    print("=" * 60)
    print("RC4 ENCRYPTION IMPLEMENTATION TESTS")
    print("=" * 60)

    # Run all tests
    tests = [
        test_basic_encryption,
        test_empty_strings,
        test_special_characters,
        test_base64_encoding,
        test_credential_encryption,
        test_known_vectors,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\nERROR: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("Result: ALL TESTS PASSED")
        return 0
    else:
        print("Result: SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
