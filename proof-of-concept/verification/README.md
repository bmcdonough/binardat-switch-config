# Verification Test Suite

## Purpose

This test suite validates all documented behavior of the Binardat switch interface. It ensures that our implementation matches the actual switch behavior and catches any discrepancies early.

## Test Organization

The verification suite is organized into 5 test modules:

1. **test_01_rc4_crypto.py** - RC4 encryption validation
2. **test_02_authentication.py** - Login/logout flow validation
3. **test_03_menu_navigation.py** - Menu structure and page access
4. **test_04_form_submission.py** - Configuration form handling
5. **test_05_end_to_end.py** - Complete workflow validation

## Running Tests

### All Tests

Run all verification tests with the master runner:

```bash
cd proof-of-concept/verification
python run_all_verifications.py
```

This will:
- Execute all 5 test suites in order
- Generate a console summary (pass/fail counts)
- Create a JSON report for CI integration
- Create an HTML report for human review
- Exit with code 0 (all pass) or 1 (failures)

### Individual Test Suites

Run a specific test suite using pytest:

```bash
# RC4 encryption tests
pytest test_01_rc4_crypto.py -v

# Authentication tests
pytest test_02_authentication.py -v

# Menu navigation tests
pytest test_03_menu_navigation.py -v

# Form submission tests
pytest test_04_form_submission.py -v

# End-to-end workflow tests
pytest test_05_end_to_end.py -v
```

### With Coverage

Generate code coverage reports:

```bash
pytest --cov=.. --cov-report=html --cov-report=term
```

### Specific Test

Run a single test function:

```bash
pytest test_01_rc4_crypto.py::test_known_vectors -v
```

## Test Environment

### Requirements

- **Active Binardat switch** at 192.168.2.1 (or configure different IP)
- **Valid credentials** (default: admin/admin)
- **Network connectivity** to the switch
- **Python 3.9+** with dependencies from requirements.txt

### Configuration

Tests use the following default configuration:
- Switch IP: 192.168.2.1
- Username: admin
- Password: admin

To use different values, set environment variables:

```bash
export SWITCH_IP=192.168.1.100
export SWITCH_USER=myuser
export SWITCH_PASS=mypass
```

Or create a `test_config.yaml` file:

```yaml
switch:
  host: 192.168.1.100
  username: myuser
  password: mypass
```

### Safety

**All tests run in read-only mode.** No configuration changes are made to the switch.

Tests will:
- ✅ Read current configuration
- ✅ Parse forms and pages
- ✅ Validate data structures
- ❌ **NOT** submit configuration changes
- ❌ **NOT** reboot or reset the switch
- ❌ **NOT** modify any settings

## Test Coverage

### Module 1: RC4 Encryption

**File:** `test_01_rc4_crypto.py`

**Tests:**
- Known plaintext/ciphertext pairs from switch
- Binardat-specific format (comma-delimited decimals)
- Encryption/decryption round-trip
- Edge cases (empty strings, special characters, unicode)
- Cross-validation with JavaScript RC4

**Example:**
```python
def test_known_vectors():
    """Test RC4 encryption against known switch outputs."""
    assert rc4_encrypt_binardat("admin", "iensuegdul27c90d") == "126,,103,,178,,61,,175,,"
```

### Module 2: Authentication

**File:** `test_02_authentication.py`

**Tests:**
- RC4 key extraction from login page
- Successful login with valid credentials
- Failed login scenarios (invalid credentials, insufficient permissions)
- Session cookie creation and persistence
- Session reuse across requests
- Logout flow

**Example:**
```python
def test_login_success():
    """Test successful authentication and session creation."""
    session = SwitchSession("192.168.2.1")
    result = session.login("admin", "admin")
    assert result is True
    assert session.session_cookie is not None
```

### Module 3: Menu Navigation

**File:** `test_03_menu_navigation.py`

**Tests:**
- Datalink attribute extraction from HTML
- Menu hierarchy parsing (10 categories, 168 pages)
- Direct page access (bypass JavaScript simulation)
- Page categorization accuracy
- Primary target discovery (Manageportip.cgi)
- All documented pages are accessible

**Example:**
```python
def test_datalink_extraction():
    """Test extraction of datalink attributes from menu HTML."""
    menu_items = extract_menu_items(main_page_html)
    assert len(menu_items) >= 150  # Expect ~168 pages
    assert any("Manageportip.cgi" in item["url"] for item in menu_items)
```

### Module 4: Form Submission

**File:** `test_04_form_submission.py`

**Tests:**
- Form field discovery and parsing
- Hidden field extraction
- Current configuration value extraction
- Form data construction for POST
- Response validation (success/error codes)
- Error handling and recovery

**Example:**
```python
def test_form_parsing():
    """Test extraction of form fields from IP config page."""
    form_fields = extract_form_fields(ip_config_html)
    assert "ip_address" in form_fields
    assert "netmask" in form_fields
    assert "gateway" in form_fields
```

### Module 5: End-to-End Workflow

**File:** `test_05_end_to_end.py`

**Tests:**
- Complete automation sequence
- Login → discover menu → navigate to page → read config → logout
- Error recovery at each stage
- State consistency verification

**Example:**
```python
def test_complete_workflow():
    """Test the complete automation workflow."""
    # 1. Login
    session = SwitchSession("192.168.2.1")
    session.login("admin", "admin")

    # 2. Discover menu
    menu = discover_menu_structure(session)
    assert len(menu["all_pages"]) >= 150

    # 3. Navigate to IP config
    ip_page = session.get_page("Manageportip.cgi")
    assert "ip" in ip_page.lower()

    # 4. Read configuration
    config = extract_form_fields(ip_page)
    assert "ip_address" in config

    # 5. Logout
    session.logout()
```

## Continuous Integration

The verification suite is designed for CI/CD integration:

### GitHub Actions Example

```yaml
name: Verification Tests
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python verification/run_all_verifications.py
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: verification-reports
          path: |
            verification-report.html
            verification-report.json
```

### Jenkins Example

```groovy
pipeline {
    agent any
    stages {
        stage('Verify') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python verification/run_all_verifications.py'
            }
        }
    }
    post {
        always {
            publishHTML([
                reportDir: 'proof-of-concept/verification',
                reportFiles: 'verification-report.html',
                reportName: 'Verification Report'
            ])
        }
    }
}
```

## Troubleshooting

### Connection Refused

**Problem:** Tests fail with "Connection refused" error

**Solutions:**
- Verify switch is powered on and accessible
- Check IP address configuration
- Ensure network connectivity: `ping 192.168.2.1`
- Check firewall rules

### Authentication Failed

**Problem:** Tests fail during login

**Solutions:**
- Verify credentials are correct
- Check that user has sufficient permissions (≥15)
- Ensure switch is not already at max sessions

### Timeouts

**Problem:** Tests timeout waiting for responses

**Solutions:**
- Increase timeout values in test configuration
- Check network latency: `ping -c 10 192.168.2.1`
- Verify switch is not overloaded

### Page Not Found

**Problem:** Specific pages return 404 errors

**Solutions:**
- Verify switch firmware version matches expectations
- Check if page requires specific permissions
- Confirm page URL is correct for your switch model

## Contributing

When adding new tests:

1. **Follow naming convention:** `test_XX_category.py`
2. **Add docstrings:** Explain what each test validates
3. **Use descriptive names:** Test function names should be self-documenting
4. **Add to master runner:** Update `run_all_verifications.py`
5. **Update this README:** Document new test coverage

## References

- [Authentication & Web Interface](../../docs/authentication-and-web-interface.md)
- [Menu Implementation Guide](../../docs/menu-implementation-guide.md)
- [Menu Quick Reference](../../docs/menu-interaction-guide.md)
- [Menu Structure Catalog](../../docs/menu-structure-findings.md)

---

**Last Updated:** 2026-01-25
