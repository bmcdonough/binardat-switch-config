"""RC4 encryption module for Binardat switch authentication.

This module implements RC4 encryption to match the JavaScript implementation
used by Binardat switches for credential encryption.

Warning:
    RC4 is cryptographically weak and should not be used for secure
    applications. This implementation exists solely to communicate with
    legacy switch firmware.
"""

from Crypto.Cipher import ARC4


def rc4_encrypt(plaintext: str, key: str, encoding: str = "utf-8") -> str:
    """Encrypt a string using RC4 encryption.

    Args:
        plaintext: The text to encrypt.
        key: The RC4 encryption key.
        encoding: Character encoding to use. Defaults to "utf-8".

    Returns:
        Hexadecimal string representation of the encrypted data.

    Example:
        >>> key = "mykey123"
        >>> encrypted = rc4_encrypt("password", key)
        >>> print(encrypted)
        'a1b2c3d4...'
    """
    # Convert strings to bytes
    plaintext_bytes = plaintext.encode(encoding)
    key_bytes = key.encode(encoding)

    # Create RC4 cipher
    cipher = ARC4.new(key_bytes)

    # Encrypt
    ciphertext_bytes = cipher.encrypt(plaintext_bytes)

    # Convert to hex string (common format for web interfaces)
    return ciphertext_bytes.hex()


def rc4_encrypt_binardat(plaintext: str, key: str) -> str:
    """Encrypt a string using RC4 with Binardat switch format.

    This matches the JavaScript implementation used by Binardat switches,
    which outputs decimal bytes separated by ',,' delimiters.

    Args:
        plaintext: The text to encrypt.
        key: The RC4 encryption key.

    Returns:
        Comma-delimited decimal string (e.g., "126,,103,,178,,").

    Example:
        >>> key = "iensuegdul27c90d"
        >>> encrypted = rc4_encrypt_binardat("admin", key)
        >>> print(encrypted)
        '126,,103,,178,,61,,175,,'
    """
    # Initialize S-box
    S = list(range(256))
    j = 0
    key_length = len(key)

    # KSA (Key Scheduling Algorithm)
    for i in range(256):
        j = (j + S[i] + ord(key[i % key_length])) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA (Pseudo-Random Generation Algorithm)
    result = ""
    i = 0
    j = 0

    for char in plaintext:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = (S[i] + S[j]) % 256
        # XOR character with keystream byte and append with delimiter
        result += str(ord(char) ^ S[t])
        result += ",,"

    return result


def rc4_decrypt(ciphertext_hex: str, key: str, encoding: str = "utf-8") -> str:
    """Decrypt an RC4-encrypted hex string.

    Args:
        ciphertext_hex: Hexadecimal string of encrypted data.
        key: The RC4 encryption key.
        encoding: Character encoding to use. Defaults to "utf-8".

    Returns:
        Decrypted plaintext string.

    Example:
        >>> key = "mykey123"
        >>> decrypted = rc4_decrypt("a1b2c3d4...", key)
        >>> print(decrypted)
        'password'
    """
    # Convert hex string to bytes
    ciphertext_bytes = bytes.fromhex(ciphertext_hex)
    key_bytes = key.encode(encoding)

    # Create RC4 cipher
    cipher = ARC4.new(key_bytes)

    # Decrypt
    plaintext_bytes = cipher.decrypt(ciphertext_bytes)

    # Convert to string
    return plaintext_bytes.decode(encoding)


def rc4_encrypt_base64(
    plaintext: str, key: str, encoding: str = "utf-8"
) -> str:
    """Encrypt a string using RC4 and return base64-encoded result.

    Some web interfaces use base64 encoding instead of hex. This function
    provides an alternative output format.

    Args:
        plaintext: The text to encrypt.
        key: The RC4 encryption key.
        encoding: Character encoding to use. Defaults to "utf-8".

    Returns:
        Base64 string representation of the encrypted data.

    Example:
        >>> key = "mykey123"
        >>> encrypted = rc4_encrypt_base64("password", key)
        >>> print(encrypted)
        'YWJjZGVm...'
    """
    import base64

    # Convert strings to bytes
    plaintext_bytes = plaintext.encode(encoding)
    key_bytes = key.encode(encoding)

    # Create RC4 cipher
    cipher = ARC4.new(key_bytes)

    # Encrypt
    ciphertext_bytes = cipher.encrypt(plaintext_bytes)

    # Convert to base64 string
    return base64.b64encode(ciphertext_bytes).decode("ascii")


def encrypt_credentials(
    username: str, password: str, key: str
) -> tuple[str, str]:
    """Encrypt both username and password for switch authentication.

    Args:
        username: Username to encrypt.
        password: Password to encrypt.
        key: The RC4 encryption key.

    Returns:
        Tuple of (encrypted_username, encrypted_password) in Binardat format.

    Example:
        >>> enc_user, enc_pass = encrypt_credentials("admin", "admin", "key")
        >>> print(f"User: {enc_user}, Pass: {enc_pass}")
        User: 126,,103,..., Pass: 126,,103...
    """
    encrypted_username = rc4_encrypt_binardat(username, key)
    encrypted_password = rc4_encrypt_binardat(password, key)
    return encrypted_username, encrypted_password


def verify_rc4_implementation(
    plaintext: str, key: str, expected_hex: str
) -> bool:
    """Verify RC4 implementation against known output.

    This is useful for testing that our RC4 implementation matches
    the JavaScript implementation on the switch.

    Args:
        plaintext: The plaintext to encrypt.
        key: The RC4 key.
        expected_hex: Expected hexadecimal output.

    Returns:
        True if implementation matches expected output, False otherwise.

    Example:
        >>> result = verify_rc4_implementation(
        ...     "test", "key123", "a1b2c3d4"
        ... )
        >>> print("Match!" if result else "Mismatch!")
    """
    actual_hex = rc4_encrypt(plaintext, key)
    return actual_hex.lower() == expected_hex.lower()


# Common utility functions
def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hexadecimal string.

    Args:
        data: Bytes to convert.

    Returns:
        Hexadecimal string representation.
    """
    return data.hex()


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hexadecimal string to bytes.

    Args:
        hex_string: Hexadecimal string.

    Returns:
        Bytes object.
    """
    return bytes.fromhex(hex_string)
