# Binardat Switch Authentication & Web Interface

**Target:** Binardat 2G20-16410GSM Switch
**IP Address:** 192.168.2.1
**Date:** 2026-01-25
**Status:** ✅ FULLY OPERATIONAL

## Executive Summary

Successfully analyzed and implemented authentication for the Binardat switch web interface. The switch uses JavaScript-based AJAX login with RC4-encrypted credentials. Authentication has been successfully tested with both valid and invalid credentials, and session management has been validated.

## Initial Discovery

### Authentication Mechanism

**Login Type:** JavaScript/AJAX-based (no HTML form submission)

**Endpoint:** `/login.cgi`

**Method:** POST

**Parameters:**
- `name` - RC4 encrypted username
- `pwd` - RC4 encrypted password

**Parameter Format:**
```
name=<encrypted_username>&pwd=<encrypted_password>
```

### JavaScript Files

The web interface loads three JavaScript files:

| File | Size | Purpose |
|------|------|---------|
| `/js/jquery-3.5.1.min.js` | 89,476 bytes | jQuery library |
| `/js/utility.js` | 33,754 bytes | **Main utilities** - Contains RC4 function and HTTP helpers |
| `/js/jquery.slimscroll.min.js` | 4,739 bytes | UI scrolling library |

**Critical File:** `utility.js` contains:
- RC4 encryption function
- HTTP POST/GET helper functions
- Authentication logic
- Cookie management
- Various utility functions

### Login Form Details

**Form Type:** JavaScript-dynamically populated (not static HTML form)

**Input Fields:**
```html
<input type="text" name="name" placeholder="Account" id="name" required="">
<input type="password" name="pwd" placeholder="Password" id="pwd" required="required">
```

**Additional Features:**
- "Remember password" checkbox (stores base64-encoded credentials in cookies)
- Language selector (default: English)
- CAPTCHA canvas (though not enforced for login)
- Show/hide password toggle

### Additional JavaScript Functions

**Base64 Encoding/Decoding:**
- Custom Base64 implementation for cookie storage
- Functions: `enBase64()`, `deBase64()`

**Cookie Management:**
- Stores remembered credentials as base64
- Cookie names: `webusername`, `webpassword`, `remember`

**Language Support:**
- Endpoint: `/language.cgi`
- Default: English (`en`)

## RC4 Encryption Implementation

### Encryption Key Discovery

The RC4 encryption key is hardcoded in the login page JavaScript at line ~57:

```javascript
var postData='name='+rc4("iensuegdul27c90d", name)+'&pwd='+rc4("iensuegdul27c90d", pwd);
```

**Extracted Key:** `iensuegdul27c90d`

### Custom RC4 Format

Credentials are encrypted using a **custom RC4 implementation** with non-standard output:

**Output Format:** Comma-delimited decimal bytes (e.g., `126,,103,,178,,61,,175,,`)

**NOT standard formats:**
- NOT hex encoding (e.g., `7e67b23daf`)
- NOT base64 encoding
- NOT binary output

**Example:**
```
Username: "admin"
Key: "iensuegdul27c90d"
Encrypted: "126,,103,,178,,61,,175,,"
```

### JavaScript Implementation

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

**Key Differences from Standard RC4:**
- Output format is comma-delimited decimal bytes instead of hex or base64
- Delimiter: `,,` (double comma)
- No padding or encoding wrapper
- Uses XOR swapping in KSA (functionally equivalent but different implementation)

### Python Implementation

Created matching implementation in `proof-of-concept/rc4_crypto.py`:

```python
def rc4_encrypt_binardat(plaintext: str, key: str) -> str:
    """Encrypt using RC4 with Binardat switch format.

    Args:
        plaintext: The text to encrypt
        key: The RC4 encryption key

    Returns:
        Comma-delimited decimal byte string (e.g., "126,,103,,178,,")
    """
    # Initialize S-box
    S = list(range(256))
    j = 0

    # KSA (Key Scheduling Algorithm)
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA (Pseudo-Random Generation Algorithm)
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

## Complete Authentication Flow

### Step-by-Step Process

```
1. Initial Connection
   GET http://192.168.2.1/
   └─> Response: HTML login page + session cookie

2. RC4 Key Extraction
   Parse HTML for hardcoded encryption key
   └─> Key: "iensuegdul27c90d"

3. Credential Encryption
   username_encrypted = rc4_encrypt_binardat("admin", key)
   password_encrypted = rc4_encrypt_binardat("admin", key)
   └─> Both: "126,,103,,178,,61,,175,,"

4. Authentication Request
   POST http://192.168.2.1/login.cgi
   Content-Type: application/x-www-form-urlencoded
   Body: name=126,,103,,178,,61,,175,,&pwd=126,,103,,178,,61,,175,,
   └─> Response: {"code": 0}

5. Session Established
   JavaScript redirects to index.cgi
   Session cookie maintains authentication state
```

### Session Management

**Cookie Name:** `session`

**Cookie Format:** `session=<random_id>,timestamp=<timestamp>`

**Example:** `session=79909,timestamp=6414`

**Cookie Attributes:**
- Domain: 192.168.2.1
- Path: /
- Secure: false (HTTP only)
- HttpOnly: false
- SameSite: Lax

**Session Persistence:**
- Session cookie remains valid after authentication
- No explicit expiration time
- Can access authenticated pages (e.g., `status.html`, `index.cgi`)
- No additional authentication headers required

### Response Format

**Content-Type:** JSON

**Success Response:**
```json
{
  "code": 0
}
```

**Success Action:** Redirect to `index.cgi`

**Error Response Codes:**
- `0` - Authentication successful
- `1` - Authentication failed (incorrect credentials)
- `6` - Insufficient permissions (user permissions must be ≥ 15)

**Error Response (Insufficient Permissions):**
```json
{
  "code": 6,
  "data": {
    "name": "<username>"
  }
}
```
Error message: User needs permissions >= 15

**Error Response (Invalid Credentials):**
```json
{
  "code": <non-zero>
}
```
Error message: "The account and password are incorrect!"

## Testing and Validation

### Test Environment
- **Switch:** Binardat 2G20-16410GSM at 192.168.2.1
- **Test Script:** `proof-of-concept/02_test_login.py`
- **Test Date:** 2026-01-25

### Test Case 1: Valid Credentials

```bash
python 02_test_login.py --username admin --password admin
```

**Results:**
- ✅ Session created successfully
- ✅ RC4 key extracted: `iensuegdul27c90d`
- ✅ Credentials encrypted correctly
- ✅ Authentication successful (response code: 0)
- ✅ Session persistent (accessed `status.html`, 40,022 bytes)
- ✅ Logout successful

### Test Case 2: Invalid Credentials

**Expected Behavior:**
- Server returns `{"code": 1}`
- Python raises `SwitchAuthError` exception
- Error message: "Authentication failed: incorrect username or password"

**Actual Behavior:** ✅ As expected

### Debugging Journey

#### Problem 1: RC4 Key Extraction

**Initial Failure:**
```
Authentication error: Could not extract RC4 key from login page.
```

**Root Cause:** Regex pattern didn't match `rc4("key", ...)` format in JavaScript.

**Fix:** Added pattern `r'rc4\s*\(\s*["\']([^"\']+)["\']'` to extract key from function calls.

#### Problem 2: Credential Format

**Initial Failure:**
```
Authentication error: Authentication failed: incorrect username or password
Server response: {"code": 1}
```

**Root Cause:** Used standard hex encoding (`7e67b23daf`) instead of Binardat's custom format (`126,,103,,178,,61,,175,,`).

**Fix:** Implemented custom `rc4_encrypt_binardat()` function matching JavaScript output format exactly.

#### Problem 3: Output Format Validation

**Test Cases:**
```python
# Test known vectors
assert rc4_encrypt_binardat("admin", "iensuegdul27c90d") == "126,,103,,178,,61,,175,,"

# Test delimiter format
assert all(output.endswith(",,") for output in test_outputs)

# Test decimal-only output
assert all(char.isdigit() or char == ',' for char in output)
```

**Results:** ✅ All tests passed

## Security Analysis

### Weaknesses Identified

#### 1. RC4 Encryption
- **Status:** Cryptographically broken since 2013
- **Issue:** RC4 is deprecated and vulnerable to plaintext recovery attacks
- **Impact:** Credentials can potentially be decrypted by network observers
- **Note:** RC4 declared insecure by RFC 7465 (2015)

#### 2. Hardcoded Encryption Key
- **Status:** Critical vulnerability
- **Issue:** RC4 key `iensuegdul27c90d` is embedded in client-side JavaScript
- **Impact:** Visible to anyone who views page source
- **Cannot be rotated:** Requires firmware update to change

#### 3. HTTP Protocol (No TLS)
- **Status:** No encryption in transit
- **Issue:** All data transmitted over unencrypted HTTP
- **Impact:** Credentials and session cookies vulnerable to interception
- **Missing:** No HTTPS/TLS support

#### 4. Session Management
- **Issue:** Session ID appears to be numeric/predictable
- **Missing:** No HttpOnly flag on session cookie (vulnerable to XSS)
- **Missing:** No CSRF protection observed
- **Missing:** No explicit session timeout mechanism
- **Missing:** No secure flag on cookies

#### 5. Authentication Weaknesses
- **Default credentials:** Widely known (admin/admin)
- **No account lockout:** After failed attempts
- **No rate limiting:** Brute force attacks possible
- **No two-factor authentication:** Single-factor only

#### 6. Information Disclosure
- **Encryption key exposed:** In client-side JavaScript
- **Detailed error messages:** Reveal permission levels
- **Software version visible:** In response headers
- **No security headers:** No HSTS, CSP, X-Frame-Options, etc.

### Recommendations

#### Immediate Actions
1. **Change default credentials** on all switches
2. **Use only on isolated networks** with no external access
3. **Do not expose to internet** or untrusted networks
4. **Implement network segmentation** for management interfaces

#### For Manufacturer (Future Firmware)
1. **Implement HTTPS/TLS** for all communications
2. **Replace RC4** with modern authentication (OAuth2, JWT with bcrypt/scrypt)
3. **Add CSRF tokens** for state-changing operations
4. **Enable security flags** on cookies (HttpOnly, Secure, SameSite=Strict)
5. **Implement rate limiting** and account lockout
6. **Remove hardcoded keys** and use per-device unique keys
7. **Add security headers** (HSTS, CSP, X-Frame-Options)
8. **Implement session timeout** and proper session management

## Implementation Files

### Created Modules

**`proof-of-concept/rc4_crypto.py`**
- RC4 encryption implementation matching Binardat format
- Functions: `rc4_encrypt_binardat()`, `encrypt_credentials()`
- Test vectors for validation

**`proof-of-concept/switch_auth.py`**
- Session and authentication management
- `SwitchSession` class for managing connections
- Key extraction from HTML pages
- Login/logout operations

**`proof-of-concept/02_test_login.py`**
- Authentication test script
- Command-line interface for testing
- Validation of authentication flow

**`proof-of-concept/debug_login.py`**
- Debug script for troubleshooting
- Detailed logging of authentication steps

### Key Functions

```python
# RC4 encryption with Binardat format
rc4_encrypt_binardat(plaintext: str, key: str) -> str

# Encrypt both username and password
encrypt_credentials(username: str, password: str, key: str) -> tuple

# Session management
SwitchSession.login(username: str, password: str) -> bool
SwitchSession._extract_rc4_key(html: str) -> str
SwitchSession.logout() -> None
```

## Next Steps

With successful authentication, the following operations are now possible:

### Configuration Management
- Access network configuration pages
- Modify IP address settings
- Update VLAN configurations
- Change port settings

### Information Gathering
- Retrieve switch status
- Read port configurations
- Export current settings
- Monitor system health

### Automation Opportunities
- Batch configuration of multiple switches
- Automated backup of configurations
- Scripted firmware updates
- Configuration drift detection

## Related Documentation

- [Menu Structure Catalog](./menu-structure-findings.md) - Complete list of 168 configuration pages
- [Menu Implementation Guide](./menu-implementation-guide.md) - Technical details of menu system
- [Menu Quick Reference](./menu-interaction-guide.md) - Fast lookup for common tasks
- [CHANGELOG](../CHANGELOG.md) - Project version history

## Archived Documentation

Original research documents preserved in:
- `docs/archive/reconnaissance-findings.md` - Initial discovery phase
- `docs/archive/authentication-findings.md` - Authentication implementation phase

## References

- **JavaScript RC4 implementation:** `http://192.168.2.1/js/utility.js`
- **Login endpoint:** `http://192.168.2.1/login.cgi`
- **Login page:** `http://192.168.2.1/`
- **Switch model:** Binardat 2G20-16410GSM
- **Default IP:** 192.168.2.1
- **Test script:** `proof-of-concept/02_test_login.py`

---

**Document Created:** 2026-01-25
**Status:** Complete and Validated
**Classification:** Internal Use - Contains Security-Sensitive Information
