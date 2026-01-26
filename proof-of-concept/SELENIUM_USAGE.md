# Selenium IP Change Script - Usage Guide

## Overview

`selenium_ip_change.py` is a browser automation script that changes a Binardat switch's IP address through the web interface. It uses Selenium WebDriver to simulate real user interaction, bypassing the HTTP API issues discovered during development.

## Why Selenium?

The switch's HTTP CGI endpoints return error messages when accessed directly via Python requests, even with proper authentication. Browser automation guarantees success by simulating the exact same interaction a human user would perform.

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-selenium.txt
```

This will install:
- `selenium` - Browser automation framework (includes Selenium Manager for automatic ChromeDriver management)

### 2. Install Chrome/Chromium

The script requires Chrome or Chromium browser. Install if not already present:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download from https://www.google.com/chrome/

## Basic Usage

### Default Configuration

Change IP from 192.168.2.1 to 192.168.2.100 with defaults:

```bash
python selenium_ip_change.py
```

This uses:
- Current IP: 192.168.2.1
- New IP: 192.168.2.100
- Subnet: 255.255.255.0
- Username: admin
- Password: admin
- Headless mode (no browser window)
- Automatic verification enabled

### Custom IP Addresses

```bash
python selenium_ip_change.py --current-ip 192.168.2.1 --new-ip 192.168.2.50
```

### Full Configuration

```bash
python selenium_ip_change.py \
  --current-ip 192.168.2.1 \
  --new-ip 192.168.2.100 \
  --subnet 255.255.255.0 \
  --gateway 192.168.2.1 \
  --username admin \
  --password admin
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--current-ip` | 192.168.2.1 | Current IP address of the switch |
| `--new-ip` | 192.168.2.100 | New IP address to set |
| `--subnet` | 255.255.255.0 | Subnet mask |
| `--gateway` | None | Default gateway (optional) |
| `-u, --username` | admin | Login username |
| `-p, --password` | admin | Login password |
| `--show-browser` | False | Show browser window (for debugging) |
| `--no-verify` | False | Skip verification step |
| `--timeout` | 10 | Timeout in seconds for page loads |

## Debugging Mode

To see what the browser is doing, use `--show-browser`:

```bash
python selenium_ip_change.py --show-browser
```

This will:
- Open a visible Chrome window
- Let you watch the automation process
- Help diagnose any issues with form fields or navigation

## How It Works

The script follows these steps:

### 1. Login
- Navigates to `http://<current-ip>/`
- Fills username and password fields
- Clicks login button
- Waits for redirect to main page

### 2. Navigate to IP Config
- Finds "IPv4 Config" menu item (linked to `Manageportip.cgi`)
- Clicks the menu item
- Waits for configuration form to load via AJAX

### 3. Fill and Submit Form
- Locates IP address input field (tries multiple field name variations)
- Locates subnet mask field
- Optionally locates gateway field if provided
- Fills all fields with new values
- Finds and clicks submit button

### 4. Save Configuration
- Executes JavaScript to call `syscmd.cgi` with `cmd=save`
- Ensures changes are persistent across reboots

### 5. Verification (unless `--no-verify`)
- Waits 30 seconds for switch to apply changes
- Pings new IP address (up to 60 seconds)
- Attempts login at new IP
- Confirms switch is accessible

## Expected Output

```
Setting up Chrome WebDriver...
Navigating to http://192.168.2.1/...
Waiting for login form...
Logging in as 'admin'...
Waiting for main page to load...
✓ Login successful
Looking for IPv4 Config menu item...
Clicking IPv4 Config menu item...
Waiting for IP configuration form to load...
✓ Navigated to IP configuration page
Looking for IP address form fields...
Found IP field with selector: input[name="ip_address"]
Found subnet mask field with selector: input[name="netmask"]
Setting IP address to 192.168.2.100...
Setting subnet mask to 255.255.255.0...
Looking for submit button...
Found submit button with selector: button[type="submit"]
Submitting IP configuration...
✓ Form submitted successfully
Saving configuration to switch...
✓ Configuration save command sent

✓ IP change process completed successfully
Switch is applying changes and may reboot...
Closing browser...

============================================================
Verifying new IP address: 192.168.2.100
============================================================

Waiting for switch to apply changes (30 seconds)...
Waiting for 192.168.2.100 to respond to ping...
✓ 192.168.2.100 is responding to ping (attempt 2/12)

Attempting to log in to new IP (192.168.2.100)...
Setting up Chrome WebDriver...
Navigating to http://192.168.2.100/...
Waiting for login form...
Logging in as 'admin'...
Waiting for main page to load...
✓ Login successful

✓ Verification successful!
✓ Switch is accessible at 192.168.2.100
Closing browser...

============================================================
SUCCESS!
Switch IP successfully changed to: 192.168.2.100
============================================================
```

## Troubleshooting

### Issue: ChromeDriver not found

**Solution:** The script uses Selenium Manager (built into Selenium 4.6+) to automatically download the correct ChromeDriver version for your installed browser. Ensure you have internet access on first run. If issues persist, try updating Selenium: `pip install --upgrade selenium`

### Issue: Timeout waiting for elements

**Symptoms:**
```
✗ Login failed: Timeout waiting for page elements
```

**Solutions:**
1. Increase timeout: `--timeout 20`
2. Check network connectivity to switch
3. Verify switch IP address is correct
4. Use `--show-browser` to see what's happening

### Issue: Could not find form fields

**Symptoms:**
```
Could not find IP field automatically. Inspecting form...
Found 5 input fields:
  - name='ip', id='ip_addr', type='text'
  ...
```

**Solution:** The script tries multiple field name variations. If it fails, the output shows all available fields. This may indicate:
1. Switch firmware uses different field names
2. Form loaded in an iframe (script needs adjustment)
3. JavaScript hasn't finished loading (increase timeout)

Use `--show-browser` to manually inspect the page.

### Issue: Form submits but IP doesn't change

**Possible causes:**
1. Save configuration step failed
2. Switch requires reboot (manual)
3. Network configuration conflict

**Debug steps:**
1. Manually log in to switch at old IP
2. Check if configuration was applied
3. Save configuration manually
4. Reboot switch if needed

### Issue: Verification fails

**Symptoms:**
```
✗ Verification failed: 192.168.2.100 is not responding to ping
```

**Solutions:**
1. Switch may take longer to apply changes - wait and try manual ping
2. Check if new IP conflicts with another device
3. Verify subnet mask and gateway are correct
4. Use `--no-verify` to skip verification, then test manually

## Security Considerations

### Passwords on Command Line

Avoid passing passwords on the command line in production environments, as they appear in shell history and process lists.

**Better approach:**
```python
# Modify script to prompt for password
import getpass
password = getpass.getpass("Switch password: ")
```

Or use environment variables:
```bash
export SWITCH_PASSWORD=admin
python selenium_ip_change.py -p "$SWITCH_PASSWORD"
```

### Headless Mode

By default, the script runs in headless mode (no visible browser). This is more secure as it doesn't display credentials on screen.

## Performance Notes

- **Typical execution time:** 30-60 seconds
  - 10s: Login and navigation
  - 5s: Form submission
  - 30s: Wait for switch to apply changes
  - 10s: Verification ping and login

- **Network requirements:**
  - Switch must be accessible on current IP
  - Computer must be able to reach both old and new IP addresses
  - No proxy or firewall blocking HTTP traffic

## Comparison with Other Approaches

| Method | Status | Pros | Cons |
|--------|--------|------|------|
| **Selenium (this script)** | ✅ Working | Guaranteed to work, handles JavaScript | Requires Chrome, slower |
| **Direct HTTP API** | ❌ Fails | Fast, pure Python | CGI endpoints return error 201 |
| **SSH/Telnet CLI** | ❓ Unknown | Standard network management | May not be enabled on switch |

## Future Improvements

Potential enhancements if needed:

1. **Screenshot capture** on errors for debugging
2. **Retry logic** for transient failures
3. **Multiple switch support** (batch processing)
4. **Config file** support instead of CLI args
5. **Firefox support** as alternative to Chrome
6. **Read current config** before changing (validation)
7. **Backup config** before changes
8. **Rollback capability** if verification fails

## Integration Example

Use this script in automation workflows:

```bash
#!/bin/bash
# Batch configure multiple switches

SWITCHES=(
  "192.168.2.1:192.168.2.101"
  "192.168.2.2:192.168.2.102"
  "192.168.2.3:192.168.2.103"
)

for switch_pair in "${SWITCHES[@]}"; do
  IFS=':' read -r current new <<< "$switch_pair"
  echo "Configuring switch: $current -> $new"

  python selenium_ip_change.py \
    --current-ip "$current" \
    --new-ip "$new" \
    --username admin \
    --password "$SWITCH_PASSWORD"

  if [ $? -eq 0 ]; then
    echo "✓ Success: $new"
  else
    echo "✗ Failed: $current"
  fi
done
```

## Support

For issues or questions:
1. Check this documentation
2. Run with `--show-browser` to debug visually
3. Review the plan document in `plans/` directory
4. Check existing proof-of-concept scripts for reference
