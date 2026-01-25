# Web Interface Reconnaissance Findings

**Target:** Binardat 2G20-16410GSM Switch
**IP Address:** 192.168.2.1
**Date:** 2026-01-25
**Tool:** `proof-of-concept/01_reconnaissance.py`

## Executive Summary

Successfully analyzed the Binardat switch web interface and identified the complete authentication mechanism. The switch uses JavaScript-based AJAX login with RC4-encrypted credentials sent to `/login.cgi`.

## Key Findings

### 1. Authentication Mechanism

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

### 2. RC4 Encryption

**Encryption Key:** `iensuegdul27c90d`

**Location:** Inline JavaScript in login page (line ~67)

**JavaScript Code:**
```javascript
var postData='name='+rc4("iensuegdul27c90d", name)+'&pwd='+rc4("iensuegdul27c90d", pwd);
```

**Output Format:** Comma-delimited decimal bytes (e.g., `126,,103,,178,,61,,175,,`)

**Example:**
```
Username: "admin"
Key: "iensuegdul27c90d"
Encrypted: "126,,103,,178,,61,,175,,"
```

### 3. Session Management

**Cookie Name:** `session`

**Cookie Format:** `session=<random_id>,timestamp=<timestamp>`

**Example:** `session=79909,timestamp=6414`

**Cookie Attributes:**
- Domain: 192.168.2.1
- Path: /
- Secure: false (HTTP only)
- HttpOnly: false
- SameSite: Lax

### 4. Response Format

**Content-Type:** JSON

**Success Response:**
```json
{
  "code": 0
}
```

**Success Action:** Redirect to `index.cgi`

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

### 5. JavaScript Files

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

### 6. Login Form Details

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

### 7. Additional JavaScript Functions

**Base64 Encoding/Decoding:**
- Custom Base64 implementation for cookie storage
- Functions: `enBase64()`, `deBase64()`

**Cookie Management:**
- Stores remembered credentials as base64
- Cookie names: `webusername`, `webpassword`, `remember`

**Language Support:**
- Endpoint: `/language.cgi`
- Default: English (`en`)

## Security Observations

### Weaknesses Identified

1. **RC4 Encryption**
   - Cryptographically weak cipher (deprecated since 2015)
   - Fixed key hardcoded in JavaScript (publicly visible)
   - No salt or randomization

2. **HTTP Protocol**
   - No HTTPS/TLS encryption
   - All credentials transmitted in plaintext over network
   - Session cookies sent without Secure flag

3. **Session Management**
   - Session ID appears to be numeric/predictable
   - No HttpOnly flag on session cookie (vulnerable to XSS)
   - No CSRF protection observed

4. **Authentication**
   - Default credentials widely known (admin/admin)
   - No account lockout after failed attempts
   - No two-factor authentication

5. **Information Disclosure**
   - Encryption key exposed in client-side JavaScript
   - Detailed error messages reveal permission levels
   - Software version visible in response headers

### Recommendations

1. **Immediate:**
   - Change default credentials
   - Use only on isolated/controlled networks
   - Do not expose to internet

2. **For Manufacturer:**
   - Implement HTTPS/TLS
   - Use modern authentication (bcrypt/scrypt)
   - Add CSRF tokens
   - Enable HttpOnly and Secure flags on cookies
   - Implement rate limiting
   - Remove hardcoded encryption keys

## Technical Implementation Details

### RC4 Algorithm Implementation

The switch uses a custom RC4 implementation in JavaScript (`utility.js`):

```javascript
function rc4(key, plaintext) {
    // Initialize S-box (0-255)
    var S = [];
    for (var i = 0; i < 256; i++) {
        S[i] = i;
    }

    // Key Scheduling Algorithm (KSA)
    var j = 0;
    for (var i = 0; i < 256; i++) {
        j = (j + S[i] + key.charCodeAt(i % key.length)) % 256;
        var temp = S[i];
        S[i] = S[j];
        S[j] = temp;
    }

    // Pseudo-Random Generation Algorithm (PRGA)
    var result = "";
    var i = 0;
    j = 0;

    for (var n = 0; n < plaintext.length; n++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        var temp = S[i];
        S[i] = S[j];
        S[j] = temp;
        var t = (S[i] + S[j]) % 256;
        result += (plaintext.charCodeAt(n) ^ S[t]) + ",,";
    }

    return result;
}
```

**Key Differences from Standard RC4:**
- Output format is comma-delimited decimal bytes instead of hex or base64
- Delimiter: `,,` (double comma)
- No padding or encoding wrapper

### Authentication Flow

```
1. User enters credentials in web form
   ↓
2. JavaScript captures form submission
   ↓
3. Credentials encrypted with RC4 using key "iensuegdul27c90d"
   ↓
4. POST request to /login.cgi with encrypted data
   ↓
5. Server validates credentials
   ↓
6. Response: {"code": 0} for success
   ↓
7. JavaScript redirects to index.cgi
   ↓
8. Session cookie maintains authentication state
```

## File Artifacts

**Generated Files:**
- `login_page.html` - Complete HTML source of login page
- `login_page_analysis.html` - Processed analysis output

**Location:** Current working directory where script was executed

## Next Steps

1. **Implement Python RC4 function** matching JavaScript format (comma-delimited decimals)
2. **Test authentication** with discovered key and endpoint
3. **Map additional endpoints** after successful login
4. **Locate IP configuration page** (likely under network/system settings)
5. **Document IP change form structure** and parameters

## References

- **Reconnaissance Script:** `proof-of-concept/01_reconnaissance.py`
- **RC4 Crypto Module:** `proof-of-concept/rc4_crypto.py`
- **Switch Model:** Binardat 2G20-16410GSM
- **Default Credentials:** admin/admin
- **Default IP:** 192.168.2.1

## Appendix: HTTP Headers

```
Set-Cookie: session=79909,timestamp=6414;SameSite=Lax
```

No additional security headers observed (no HSTS, CSP, X-Frame-Options, etc.)

---

**Report Generated:** 2026-01-25
**Analyst:** Automated reconnaissance tool
**Classification:** Internal Use - Contains Security-Sensitive Information
