# Testing Guide for Binardat Switch PoC

This document provides detailed testing procedures for the proof-of-concept scripts.

## Prerequisites

Before testing, ensure you have:

1. **Hardware:**
   - Binardat switch (model 2G20-16410GSM)
   - Network cable
   - Computer with Ethernet port

2. **Network Setup:**
   - Connect your computer directly to the switch, or
   - Connect both to the same network segment
   - Configure your computer's network interface to be on the same subnet as the switch

3. **Software:**
   - Python 3.9 or higher
   - Virtual environment activated
   - All dependencies installed (`pip install -e ".[dev]"`)

4. **Credentials:**
   - Default: admin/admin
   - Or custom credentials if switch has been configured

## Initial Network Configuration

### Option 1: Direct Connection (Recommended for Initial Testing)

1. **Connect directly to switch:**
   ```bash
   # On Linux, assuming eth0 is your interface
   sudo ip addr add 192.168.2.100/24 dev eth0
   sudo ip link set eth0 up

   # Verify connectivity
   ping -c 4 192.168.2.1
   ```

2. **On Windows:**
   - Open Network Connections
   - Right-click Ethernet adapter
   - Properties → Internet Protocol Version 4 (TCP/IPv4)
   - Set IP: 192.168.2.100
   - Set Subnet: 255.255.255.0
   - Click OK

### Option 2: Through Existing Network

If the switch is already on your network at a known IP, use that IP for testing.

## Test Sequence

### Phase 1: Basic Connectivity

**Test 1.1: Ping the switch**

```bash
ping 192.168.2.1
```

Expected: Successful ping responses

**Test 1.2: Access web interface manually**

```bash
# Open in browser
firefox http://192.168.2.1
# or
chrome http://192.168.2.1
```

Expected: Login page appears

### Phase 2: Reconnaissance Scripts

**Test 2.1: Run reconnaissance script**

```bash
cd proof-of-concept
python 01_reconnaissance.py --host 192.168.2.1
```

Expected output:
- HTTP headers displayed
- Cookies (if any) listed
- Login form structure identified
- JavaScript files found and analyzed
- HTML saved to `login_page.html`

Verify:
- [ ] Script completes without errors
- [ ] login_page.html created
- [ ] Login form fields identified
- [ ] No Python tracebacks

**Test 2.2: Run login analysis script**

```bash
python analyze_login.py --host 192.168.2.1
```

Expected output:
- Connectivity test: OK
- RC4 encryption key found
- Login form structure displayed
- HTML saved to `login_page_analysis.html`

Verify:
- [ ] RC4 key extracted successfully
- [ ] Form field names identified
- [ ] No errors or warnings

**Troubleshooting:**
- If RC4 key not found, manually inspect the HTML and JavaScript
- Look for encryption-related functions in browser developer tools
- Check if switch firmware version differs from expected

### Phase 3: RC4 Encryption

**Test 3.1: Run RC4 unit tests**

```bash
python test_rc4.py
```

Expected output:
```
==============================================================
RC4 ENCRYPTION IMPLEMENTATION TESTS
==============================================================

[TEST 1] Basic Encryption/Decryption
------------------------------------------------------------
...
Result:     PASS

[TEST 2] Empty String Handling
------------------------------------------------------------
...
Result:     PASS

...

==============================================================
TEST SUMMARY
==============================================================
Passed: 6/6
Result: ALL TESTS PASSED
```

Verify:
- [ ] All 6 tests pass
- [ ] No exceptions or errors

**Test 3.2: Interactive RC4 test**

```bash
python test_rc4.py --interactive
```

Example interaction:
```
Enter plaintext to encrypt: admin
Enter RC4 key: testkey123

Results:
  Plaintext:      admin
  Key:            testkey123
  Hex output:     <hex string>
  Base64 output:  <base64 string>

Verifying decryption...
  Decrypted:      admin
  Match:          YES
```

Verify:
- [ ] Encryption produces consistent output
- [ ] Decryption returns original plaintext
- [ ] No errors

**Test 3.3: Compare with JavaScript (Manual)**

1. Open switch login page in browser
2. Open browser developer console (F12)
3. Find the RC4 implementation in JavaScript
4. Run in console:
   ```javascript
   // Assuming RC4 function exists
   var key = "extracted_key_from_script";
   var plaintext = "admin";
   var encrypted = rc4Encrypt(plaintext, key);
   console.log(encrypted);
   ```
5. Run in Python:
   ```bash
   python -c "from rc4_crypto import rc4_encrypt; print(rc4_encrypt('admin', 'extracted_key'))"
   ```
6. Compare outputs - they should match

### Phase 4: Authentication

**Test 4.1: Test successful login**

```bash
python 02_test_login.py --host 192.168.2.1 --username admin --password admin
```

Expected output:
```
======================================================================
BINARDAT SWITCH LOGIN TEST
======================================================================
Host:     192.168.2.1
Username: admin
Password: *****
Timeout:  30.0s

[1] Creating session...
    Session created

[2] Attempting authentication...
    Authentication: SUCCESS
    RC4 Key: <key>
    Authenticated: True

[3] Testing session persistence...
    Successfully fetched: status.html
    Page size: XXXX bytes

[4] Session information:
    Cookies:
      SESSIONID = <value>

[5] Testing logout...
    Logout: SUCCESS

======================================================================
RESULT: LOGIN TEST PASSED
======================================================================
```

Verify:
- [ ] Authentication succeeds
- [ ] RC4 key extracted
- [ ] Session cookies present
- [ ] Can fetch pages while authenticated
- [ ] Logout succeeds

**Test 4.2: Test invalid credentials**

```bash
python 02_test_login.py --host 192.168.2.1 --username wrong --password wrong --test-invalid
```

Expected:
- Invalid credentials should be rejected
- Script should report authentication error

Verify:
- [ ] Invalid login properly rejected
- [ ] Error message is clear

**Troubleshooting:**
- If authentication fails with correct credentials:
  - Verify credentials by logging in via browser
  - Check if RC4 key extraction worked
  - Run reconnaissance scripts again
  - Check switch firmware version

### Phase 5: IP Configuration Reading

**Test 5.1: Read current IP configuration**

```bash
python 03_test_ip_change.py --host 192.168.2.1 --username admin --password admin --read-only
```

Expected output:
```
======================================================================
READ IP CONFIGURATION TEST
======================================================================

[1] Authenticating...
    Authentication successful

[2] Reading current IP configuration...
    Current configuration:
      ip_address     : 192.168.2.1
      subnet_mask    : 255.255.255.0
      gateway        : 192.168.2.1

======================================================================
RESULT: READ TEST PASSED
======================================================================
```

Verify:
- [ ] Current IP configuration displayed
- [ ] All network parameters shown
- [ ] No errors

**Troubleshooting:**
- If IP config page not found:
  - Log in via browser
  - Navigate to network settings manually
  - Note the exact URL
  - Update `navigate_to_ip_config()` in switch_auth.py

### Phase 6: IP Configuration Change (Dry Run)

**Test 6.1: Dry run IP change**

```bash
python change_ip_address.py \
  --old-ip 192.168.2.1 \
  --new-ip 192.168.1.100 \
  --subnet 255.255.255.0 \
  --gateway 192.168.1.1 \
  --username admin \
  --password admin \
  --dry-run \
  --verbose
```

Expected:
- Script validates all parameters
- Shows what would be changed
- Does NOT actually submit changes
- Exits successfully

Verify:
- [ ] All validation passes
- [ ] Configuration preview shown
- [ ] No actual changes made (verify via browser)

### Phase 7: Actual IP Change (CAUTION!)

⚠️ **WARNING: This will change the switch IP address!**

**Preparation:**
1. Ensure you have physical access to the switch
2. Have a console cable ready (if available)
3. Document the current configuration
4. Ensure the new IP doesn't conflict with other devices
5. Make sure you can access the new subnet

**Test 7.1: Change IP to different subnet**

```bash
# Change from 192.168.2.1 to 192.168.1.100
python change_ip_address.py \
  --old-ip 192.168.2.1 \
  --new-ip 192.168.1.100 \
  --subnet 255.255.255.0 \
  --gateway 192.168.1.1 \
  --username admin \
  --password admin \
  --verify \
  --verbose
```

Expected flow:
1. Connects to 192.168.2.1
2. Authenticates
3. Reads current configuration
4. Submits new configuration
5. Waits 60 seconds
6. Attempts connection to 192.168.1.100
7. Verifies new configuration

Verify:
- [ ] Script completes all steps
- [ ] Connection to old IP succeeds
- [ ] Configuration submitted
- [ ] Connection to new IP succeeds (if verification enabled)
- [ ] New IP configuration confirmed

**Test 7.2: Verify manually via browser**

```bash
# Update your computer's IP to be on the new subnet
# For example: 192.168.1.50/24

# Then access via browser:
firefox http://192.168.1.100
```

Log in and verify:
- [ ] Switch responds at new IP
- [ ] Login works
- [ ] Network settings show new configuration

**Test 7.3: Change back to default (Optional)**

If needed, change back to factory default IP:

```bash
python change_ip_address.py \
  --old-ip 192.168.1.100 \
  --new-ip 192.168.2.1 \
  --subnet 255.255.255.0 \
  --gateway 192.168.2.1 \
  --username admin \
  --password admin \
  --verify \
  --verbose
```

## Error Recovery

### If switch becomes unreachable after IP change:

1. **Wait longer:** Give it 2-3 minutes to fully apply changes

2. **Check your network configuration:**
   ```bash
   # Ensure your computer is on the right subnet
   ip addr show

   # Try pinging the new IP
   ping <new_ip>
   ```

3. **Factory reset via hardware:**
   - Locate the reset button on the switch
   - Hold for 10 seconds while powered on
   - Switch will reset to 192.168.2.1

4. **Console cable access:**
   - If available, connect via serial console
   - Access switch CLI to check/fix configuration

### If authentication fails:

1. **Verify credentials via browser**
2. **Check for firmware updates that changed authentication**
3. **Re-run reconnaissance scripts**
4. **Check if RC4 key changed**

## Performance Testing

### Timing Tests

Run multiple operations to verify consistency:

```bash
# Test login speed
time python 02_test_login.py --host 192.168.2.1 -u admin -p admin

# Test IP change speed (dry run)
time python change_ip_address.py --old-ip 192.168.2.1 --new-ip 192.168.1.100 --subnet 255.255.255.0 -u admin -p admin --dry-run
```

Expected times:
- Login: < 5 seconds
- IP change (dry run): < 10 seconds
- Full IP change with verification: 60-90 seconds

## Code Quality Checks

Before considering the PoC complete, run all code quality checks:

```bash
cd proof-of-concept

# Format check
black --check .

# Import sorting
isort --check .

# Linting
flake8 .

# Type checking
mypy .

# Docstring style
pydocstyle .
```

All checks should pass with no errors.

## Test Completion Checklist

- [ ] All reconnaissance scripts work
- [ ] RC4 tests pass
- [ ] Authentication succeeds
- [ ] Can read IP configuration
- [ ] Dry run IP change works
- [ ] Actual IP change succeeds
- [ ] Verification confirms new IP
- [ ] Can change back to original IP
- [ ] All code quality checks pass
- [ ] Documentation is accurate

## Known Issues and Limitations

1. **Single switch at a time:** Scripts don't handle multiple switches in parallel
2. **Timing sensitive:** Network interruption during change can cause issues
3. **No rollback:** Failed changes require manual recovery
4. **HTTP only:** All communication is unencrypted
5. **RC4 weakness:** Encryption is cryptographically weak
6. **Model specific:** Only tested with 2G20-16410GSM

## Next Steps After Testing

Once testing is complete:

1. Document any issues encountered
2. Note any firmware-specific behavior
3. Update scripts if needed for your environment
4. Consider integration into main library
5. Add proper unit tests with mocked responses
6. Implement batch configuration script
7. Add support for other switch operations

## Support

For issues during testing:
- Review troubleshooting sections above
- Check network configuration with Wireshark if needed
- Consult switch documentation
- Review JavaScript in browser developer tools
- Check system logs for network issues
