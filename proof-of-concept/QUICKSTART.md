# Quick Start Guide: Change Switch IP Address

## TL;DR

```bash
cd proof-of-concept
pip install -r requirements-selenium.txt
python selenium_ip_change.py
```

This changes the switch IP from **192.168.2.1** to **192.168.2.100** (defaults).

---

## Installation (One Time)

```bash
# From the proof-of-concept directory
pip install -r requirements-selenium.txt

# Verify setup
python test_selenium_setup.py
```

**Expected output:** "✓ ALL TESTS PASSED"

---

## Basic Usage

### Use Default IPs (192.168.2.1 → 192.168.2.100)

```bash
python selenium_ip_change.py
```

### Specify Custom IPs

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

---

## What Happens?

1. **Login** - Connects to current IP and authenticates
2. **Navigate** - Opens IP configuration page
3. **Change** - Fills form and submits new IP settings
4. **Save** - Persists configuration to switch
5. **Wait** - Gives switch 30 seconds to apply changes
6. **Verify** - Pings new IP and logs in to confirm

**Total time:** ~60 seconds

---

## Debugging

### See What's Happening

```bash
python selenium_ip_change.py --show-browser
```

This opens a visible Chrome window so you can watch the automation.

### Skip Verification

```bash
python selenium_ip_change.py --no-verify
```

Useful if you want to verify manually or if the switch takes longer than expected.

### Increase Timeout

```bash
python selenium_ip_change.py --timeout 20
```

If elements are taking longer to load.

---

## Common Issues

### "ChromeDriver not found"

**Solution:** The script downloads it automatically on first run. Ensure internet access.

### "Timeout waiting for elements"

**Solutions:**
- Increase timeout: `--timeout 20`
- Check switch IP is correct: `ping 192.168.2.1`
- Use debug mode: `--show-browser`

### "Verification failed"

**Reasons:**
- Switch is still applying changes (wait longer and try ping manually)
- IP conflict with another device
- Network routing issue

**Verify manually:**
```bash
ping 192.168.2.100
# Open browser to http://192.168.2.100
```

---

## Command-Line Options

```bash
python selenium_ip_change.py [OPTIONS]

Options:
  --current-ip IP       Current switch IP (default: 192.168.2.1)
  --new-ip IP          New switch IP (default: 192.168.2.100)
  --subnet MASK        Subnet mask (default: 255.255.255.0)
  --gateway IP         Gateway IP (optional)
  -u, --username USER  Login username (default: admin)
  -p, --password PASS  Login password (default: admin)
  --show-browser       Show browser window (for debugging)
  --no-verify          Skip verification step
  --timeout SECS       Page load timeout (default: 10)
```

---

## Examples

### Example 1: Basic IP Change

```bash
python selenium_ip_change.py
```

**Output:**
```
============================================================
Changing switch IP: 192.168.2.1 → 192.168.2.100
============================================================

Setting up Chrome WebDriver...
Navigating to http://192.168.2.1/...
Logging in as 'admin'...
✓ Login successful
Looking for IPv4 Config menu item...
✓ Navigated to IP configuration page
Setting IP address to 192.168.2.100...
Setting subnet mask to 255.255.255.0...
Submitting IP configuration...
✓ Form submitted successfully
✓ Configuration save command sent
✓ IP change process completed successfully

============================================================
Verifying new IP address: 192.168.2.100
============================================================

Waiting for switch to apply changes (30 seconds)...
Waiting for 192.168.2.100 to respond to ping...
✓ 192.168.2.100 is responding to ping (attempt 2/12)
✓ Login successful
✓ Verification successful!

============================================================
SUCCESS!
Switch IP successfully changed to: 192.168.2.100
============================================================
```

### Example 2: Change to Different Subnet

```bash
python selenium_ip_change.py \
  --current-ip 192.168.2.1 \
  --new-ip 10.0.0.50 \
  --subnet 255.255.255.0 \
  --gateway 10.0.0.1
```

### Example 3: Debug Mode

```bash
python selenium_ip_change.py --show-browser --no-verify
```

Watch the browser perform each step, then verify manually.

---

## After IP Change

### Verify Manually

```bash
# Ping new IP
ping 192.168.2.100

# Test login
python 02_test_login.py --host 192.168.2.100 -u admin -p admin

# Open in browser
firefox http://192.168.2.100
```

### Change Back (if needed)

```bash
python selenium_ip_change.py \
  --current-ip 192.168.2.100 \
  --new-ip 192.168.2.1
```

---

## Multiple Switches

```bash
# Switch 1
python selenium_ip_change.py --current-ip 192.168.2.1 --new-ip 192.168.2.101

# Switch 2
python selenium_ip_change.py --current-ip 192.168.2.2 --new-ip 192.168.2.102

# Switch 3
python selenium_ip_change.py --current-ip 192.168.2.3 --new-ip 192.168.2.103
```

Or use a bash script:

```bash
#!/bin/bash
for i in {1..10}; do
  current="192.168.2.$i"
  new="192.168.2.$((i+100))"
  python selenium_ip_change.py --current-ip "$current" --new-ip "$new"
done
```

---

## Getting Help

### Full Documentation

- **Usage Guide:** `SELENIUM_USAGE.md` - Comprehensive documentation
- **Implementation:** `IMPLEMENTATION_SUMMARY.md` - Technical details
- **Main README:** `README.md` - All proof-of-concept scripts

### Test Your Setup

```bash
python test_selenium_setup.py
```

### Check Script Help

```bash
python selenium_ip_change.py --help
```

---

## Security Note

⚠️ **Avoid passing passwords on command line in production:**

```bash
# Set environment variable instead
export SWITCH_PASSWORD="your-password"
python selenium_ip_change.py -p "$SWITCH_PASSWORD"
```

Or modify the script to prompt for password:
```python
import getpass
password = getpass.getpass("Switch password: ")
```

---

## That's It!

The script is designed to be simple and reliable. For most cases, just run:

```bash
python selenium_ip_change.py
```

And it handles everything automatically.
