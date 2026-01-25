# Binardat Switch Authentication Findings

**Date:** 2026-01-25
**Test Script:** `proof-of-concept/02_test_login.py`
**Status:** ✅ SUCCESSFUL

## Executive Summary

Successfully authenticated to the Binardat 2G20-16410GSM switch web interface by implementing a custom RC4 encryption module that matches the switch's JavaScript authentication mechanism. The authentication uses RC4 encryption with a hardcoded key embedded in the login page JavaScript.

## Authentication Flow

### 1. Session Establishment

```
GET http://192.168.2.1/
```

**Response:**
- Cookie: `session=<random>,timestamp=<value>;SameSite=Lax`
- HTML page with embedded JavaScript

### 2. RC4 Key Extraction

The RC4 encryption key is hardcoded in the login page JavaScript at line 57:

```javascript
var postData='name='+rc4("iensuegdul27c90d", name)+'&pwd='+rc4("iensuegdul27c90d", pwd);
```

**Extracted Key:** `iensuegdul27c90d`

### 3. Credential Encryption

Credentials are encrypted using a **custom RC4 implementation** before transmission:

**JavaScript Implementation Details:**
- Standard RC4 Key Scheduling Algorithm (KSA)
- Standard RC4 Pseudo-Random Generation Algorithm (PRGA)
- **Non-standard output format:** Decimal bytes separated by `,,` delimiters
  - Example: `126,,103,,178,,61,,175,,`
  - NOT hex encoding (e.g., `7e67b23daf`)

**Test Case:**
```python
Username: "admin"
Password: "admin"
RC4 Key: "iensuegdul27c90d"

Encrypted username: "126,,103,,178,,61,,175,,"
Encrypted password: "126,,103,,178,,61,,175,,"
```

### 4. Authentication Request

```
POST http://192.168.2.1/login.cgi
Content-Type: application/x-www-form-urlencoded

name=126,,103,,178,,61,,175,,&pwd=126,,103,,178,,61,,175,,
```

**Response Format:** JSON

```json
{
  "code": 0
}
```

**Response Codes:**
- `0` - Authentication successful
- `1` - Authentication failed (incorrect credentials)
- `6` - Insufficient permissions (user permissions must be ≥ 15)

### 5. Session Persistence

After successful authentication:
- Session cookie remains valid
- Can access authenticated pages (e.g., `status.html`, `index.cgi`)
- No additional authentication headers required

## Technical Deep Dive

### JavaScript RC4 Implementation

The switch uses a custom RC4 function in `/js/utility.js`:

```javascript
function rc4(key, text) {
    var S = [];
    var j = 0, i = 0, t = 0;
    var result = '';

    // KSA (Key Scheduling Algorithm)
    for (i=0; i<256; i++) {
        S[i] = i;
    }
    for (i=0; i<256; i++) {
        j = (j + S[i] + key.charCodeAt(i % key.length)) % 256;
        // Swap using XOR
        S[i] = S[i] ^ S[j];
        S[j] = S[i] ^ S[j];
        S[i] = S[i] ^ S[j];
    }

    // PRGA (Pseudo-Random Generation Algorithm)
    j = 0; i = 0;
    for (var y=0; y<text.length; y++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        // Swap using XOR
        S[i] = S[i] ^ S[j];
        S[j] = S[i] ^ S[j];
        S[i] = S[i] ^ S[j];
        t = (S[i] + (S[j] % 256)) % 256;

        // Output format: decimal byte + delimiter
        result += text.charCodeAt(y) ^ S[t];
        result += ',,';
    }
    return result;
}
```

### Python Implementation

Created matching implementation in `rc4_crypto.py`:

```python
def rc4_encrypt_binardat(plaintext: str, key: str) -> str:
    """Encrypt using RC4 with Binardat switch format."""
    # Initialize S-box
    S = list(range(256))
    j = 0

    # KSA
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA
    result = ""
    i = j = 0
    for char in plaintext:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = (S[i] + S[j]) % 256
        result += str(ord(char) ^ S[t])
        result += ",,"

    return result
```

## Testing Results

### Test: Valid Credentials

```bash
python 02_test_login.py --username admin --password admin
```

**Results:**
- ✅ Session created successfully
- ✅ RC4 key extracted: `iensuegdul27c90d`
- ✅ Authentication successful
- ✅ Session persistent (accessed `status.html`, 40,022 bytes)
- ✅ Logout successful

### Test: Invalid Credentials

**Expected Behavior:**
- Server returns `{"code": 1}`
- Python raises `SwitchAuthError` exception
- Error message: "Authentication failed: incorrect username or password"

## Debugging Journey

### Initial Problem

The first implementation attempt failed with:
```
Authentication error: Could not extract RC4 key from login page.
```

**Root Cause:** Regex pattern didn't match `rc4("key", ...)` format in JavaScript.

**Fix:** Added pattern `r'rc4\s*\(\s*["\']([^"\']+)["\']'` to extract key from function calls.

### Second Problem

After fixing RC4 key extraction:
```
Authentication error: Authentication failed: incorrect username or password
```

Server response: `{"code": 1}`

**Root Cause:** Used standard hex encoding (`7e67b23daf`) instead of Binardat's custom format (`126,,103,,178,,61,,175,,`).

**Fix:** Implemented custom `rc4_encrypt_binardat()` function matching JavaScript output format.

## Security Considerations

⚠️ **WARNING:** This authentication mechanism has significant security weaknesses:

1. **Hardcoded Encryption Key**
   - RC4 key is embedded in client-side JavaScript
   - Visible to anyone who views page source
   - Cannot be rotated without firmware update

2. **RC4 Algorithm**
   - RC4 is cryptographically broken (2013)
   - Vulnerable to plaintext recovery attacks
   - Not recommended for any security-critical applications

3. **No Transport Security**
   - HTTP (not HTTPS)
   - Credentials sent over unencrypted network
   - Vulnerable to man-in-the-middle attacks

4. **Weak Session Management**
   - Simple session cookie with timestamp
   - No apparent session timeout mechanism
   - No CSRF protection

**Recommendation:** This authentication should only be used on isolated management networks with no external access.

## Files Modified/Created

### Created Files
- `proof-of-concept/rc4_crypto.py` - RC4 encryption implementation
- `proof-of-concept/switch_auth.py` - Session and authentication management
- `proof-of-concept/02_test_login.py` - Authentication test script
- `proof-of-concept/debug_login.py` - Debug script for troubleshooting

### Key Functions
- `rc4_encrypt_binardat()` - Custom RC4 with Binardat output format
- `encrypt_credentials()` - Encrypt both username and password
- `SwitchSession.login()` - Authenticate and establish session
- `SwitchSession._extract_rc4_key()` - Extract encryption key from HTML

## Next Steps

With successful authentication, the following operations are now possible:

1. **Configuration Changes**
   - Access network configuration pages
   - Modify IP address settings
   - Update VLAN configurations

2. **Information Gathering**
   - Retrieve switch status
   - Read port configurations
   - Export current settings

3. **Automation**
   - Batch configuration of multiple switches
   - Automated backup of configurations
   - Scripted firmware updates

## Related Documentation

- [Reconnaissance Findings](./reconnaissance-findings.md) - Initial switch discovery
- [Hardware Documentation](../hardware/binardat-2g20-16410gsm.md) - Switch specifications
- [CHANGELOG](../CHANGELOG.md) - Project version history

## References

- JavaScript RC4 implementation: `http://192.168.2.1/js/utility.js`
- Login endpoint: `http://192.168.2.1/login.cgi`
- Login page: `http://192.168.2.1/`
