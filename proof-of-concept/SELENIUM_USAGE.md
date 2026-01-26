# Selenium Scripts - Usage Guide

## Overview

This directory contains browser automation scripts for configuring Binardat switches:

- **`selenium_ip_change.py`** - Changes switch IP address
- **`enable_ssh_selenium.py`** - Enables SSH access on the switch

Both scripts use Selenium WebDriver to simulate real user interaction, bypassing the HTTP API issues discovered during development.

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

---

# SSH Enablement Script

## Overview

`enable_ssh_selenium.py` enables SSH access on Binardat switches through the web interface. This is a **one-time setup** that unlocks SSH-based configuration for all future management tasks.

## Why Enable SSH?

**The Path to a Minimal Solution:**

1. ✅ **Use Selenium ONCE** - Run this script to enable SSH via web interface
2. ✅ **Switch to SSH** - Use lightweight paramiko/netmiko for all future configuration
3. ✅ **100x Smaller Footprint** - 2MB (paramiko) vs 200MB (Chrome/Selenium)
4. ✅ **30x Faster** - 1-2 seconds vs 60 seconds per operation

After SSH is enabled, you can:
- Configure switch settings via CLI commands
- Use standard SSH libraries (paramiko, netmiko)
- Deploy in minimal environments (Docker, embedded systems)
- Avoid browser automation overhead

## Basic Usage

### Default Configuration

Enable SSH on switch at 192.168.2.1 with defaults (admin/admin, port 22):

```bash
python enable_ssh_selenium.py
```

This uses:
- Switch IP: 192.168.2.1
- Username: admin
- Password: admin
- SSH Port: 22
- Headless mode (no browser window)
- Automatic port verification enabled

### Custom Switch IP

```bash
python enable_ssh_selenium.py --switch-ip 192.168.2.100
```

### Custom Credentials

```bash
python enable_ssh_selenium.py --username admin --password mypassword
```

### Full Configuration

```bash
python enable_ssh_selenium.py \
  --switch-ip 192.168.2.1 \
  --username admin \
  --password admin \
  --port 22 \
  --show-browser
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--switch-ip` | 192.168.2.1 | IP address of the switch |
| `-u, --username` | admin | Login username |
| `-p, --password` | admin | Login password |
| `--port` | 22 | SSH port number |
| `--show-browser` | False | Show browser window (for debugging) |
| `--no-verify` | False | Skip SSH port verification |
| `--timeout` | 10 | Timeout in seconds for page loads |

## How It Works

The script follows these steps:

### 1. Login
- Navigates to `http://<switch-ip>/`
- Fills username and password fields
- Clicks login button
- Waits for redirect to main page

### 2. Navigate to SSH Config
- Finds "Monitor Management" parent menu
- Clicks to expand submenu
- Clicks "SSH Config" (linked to `ssh_get.cgi`)
- Waits for configuration form to load via AJAX

### 3. Enable SSH Form
- Locates SSH enable field (checkbox/dropdown/radio)
- Enables SSH service
- Optionally configures SSH port (if field exists)
- Finds and clicks submit button

### 4. Save Configuration
- Executes JavaScript to call `syscmd.cgi` with `cmd=save`
- Ensures SSH remains enabled after reboot

### 5. Verification (unless `--no-verify`)
- Waits 5 seconds for SSH service to start
- Tests socket connection to SSH port
- Reports accessibility status

## Expected Output

```
Setting up Chrome WebDriver...
Navigating to http://192.168.2.1/...
Waiting for login form...
Logging in as 'admin'...
Waiting for main page to load...
✓ Login successful
Looking for Monitor Management menu...
Found 'Monitor Management' parent menu
Clicking 'Monitor Management' to expand submenu...
Looking for SSH Config submenu item...
Found SSH Config link (ssh_get.cgi)
Clicking SSH Config submenu item...
Waiting for SSH configuration form to load...
✓ Navigated to SSH configuration page
SSH config page saved to debug_ssh_config_loaded.html
Looking for SSH enable form fields...
Found enable field with selector: input[name="enable"]
Found checkbox for SSH enable
Enabling SSH (checking checkbox)...
Looking for submit button...
Found submit button with selector: input[type="button"][value="Apply"]
Submitting SSH configuration...
✓ Form submitted successfully
Saving configuration to switch...
✓ Configuration save command sent

✓ SSH enablement process completed successfully
SSH service should now be active...
Closing browser...

============================================================
Verifying SSH port 22 accessibility...
============================================================

Waiting for SSH service to start (5 seconds)...
✓ SSH port 22 is accessible

You can now connect via SSH:
  ssh admin@192.168.2.1

============================================================
SSH ENABLEMENT COMPLETED
Switch: 192.168.2.1
Port: 22
============================================================
```

## Verification Steps

After running the script, verify SSH access:

### 1. Test SSH Connection

```bash
ssh admin@192.168.2.1
```

If prompted about host key:
```
The authenticity of host '192.168.2.1 (192.168.2.1)' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)? yes
```

### 2. Check SSH Service Status

Once connected via SSH:
```bash
show ssh server status
# or
show running-config | include ssh
```

### 3. Test Configuration via SSH

Now you can configure the switch via CLI:
```bash
# Example: Change IP via SSH (no Selenium needed!)
ssh admin@192.168.2.1 <<EOF
configure terminal
interface vlan 1
ip address 192.168.2.100 255.255.255.0
exit
write memory
exit
EOF
```

## Troubleshooting

### Issue: SSH port not responding after script completes

**Symptoms:**
```
⚠ SSH port 22 is not responding
```

**Solutions:**

1. **Switch may require reboot** - Many switches only start SSH after reboot:
   ```bash
   # Log in to web interface and reboot switch
   # Or wait for scheduled reboot
   ```

2. **Verify SSH is enabled in web interface:**
   - Log in to `http://192.168.2.1/`
   - Navigate to Monitor Management → SSH Config
   - Confirm SSH is enabled

3. **Check firewall/network:**
   - Try from another machine
   - Check switch firewall settings
   - Verify no ACLs blocking SSH

4. **SSH may be on different port:**
   ```bash
   nmap -p 22,23,2222 192.168.2.1
   ```

### Issue: Form fields not found

**Symptoms:**
```
Could not find enable field automatically. Inspecting form...
Found 3 input/select fields:
  - name='status', id='ssh_status', type='select'
  ...
```

**Solutions:**

1. **Use `--show-browser`** to see the form:
   ```bash
   python enable_ssh_selenium.py --show-browser
   ```

2. **Check debug output:**
   - Script saves page HTML to `debug_ssh_config_loaded.html`
   - Inspect to find actual field names
   - Report issue if firmware uses different fields

3. **Firmware variation:**
   - Different switch models may have different forms
   - Script tries multiple field name patterns
   - May need customization for specific firmware

### Issue: SSH disabled after reboot

**Possible causes:**
1. Configuration not saved properly
2. Factory reset performed
3. Configuration restored from backup without SSH enabled

**Debug steps:**
1. Re-run script to re-enable SSH
2. Verify save command succeeds
3. Backup configuration after enabling SSH

## Post-SSH Configuration Examples

Once SSH is enabled, you can use lightweight Python scripts:

### Example 1: Configure IP via SSH (No Selenium!)

```python
import paramiko

def configure_switch_ip(host, username, password, new_ip, netmask):
    """Configure switch IP via SSH - 2MB dependency, 2 seconds execution."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)

    commands = [
        "configure terminal",
        "interface vlan 1",
        f"ip address {new_ip} {netmask}",
        "exit",
        "write memory",
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())

    ssh.close()

# Usage
configure_switch_ip(
    host="192.168.2.1",
    username="admin",
    password="admin",
    new_ip="192.168.2.100",
    netmask="255.255.255.0"
)
```

### Example 2: Using Netmiko (Even Simpler)

```python
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',  # Or appropriate type for switch
    'host': '192.168.2.1',
    'username': 'admin',
    'password': 'admin',
}

with ConnectHandler(**device) as net_connect:
    output = net_connect.send_config_set([
        'interface vlan 1',
        'ip address 192.168.2.100 255.255.255.0',
    ])
    output += net_connect.save_config()
    print(output)
```

### Example 3: Batch Configuration

```bash
#!/bin/bash
# Configure multiple switches via SSH - FAST!

SWITCHES=(
  "192.168.2.1"
  "192.168.2.2"
  "192.168.2.3"
)

for switch in "${SWITCHES[@]}"; do
  echo "Configuring $switch..."

  sshpass -p admin ssh -o StrictHostKeyChecking=no admin@$switch <<EOF
    configure terminal
    snmp-server community public RO
    snmp-server community private RW
    write memory
    exit
EOF

  echo "✓ Configured $switch"
done
```

## Dependencies Comparison

| Solution | Install Size | Execution Time | Use Case |
|----------|-------------|----------------|----------|
| **Selenium (this script)** | ~200MB | 30-60s | One-time SSH enablement |
| **Paramiko (SSH)** | ~2MB | 1-2s | All config after SSH enabled |
| **Netmiko (SSH)** | ~3MB | 1-2s | Network device automation |
| **HTTP API** | ~500KB | N/A | ❌ Doesn't work (HTTP 201) |

## Security Notes

### SSH Key Authentication (Recommended)

After enabling SSH, configure key-based authentication:

1. **Generate SSH key:**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/binardat_switch
   ```

2. **Copy public key to switch:**
   ```bash
   ssh-copy-id -i ~/.ssh/binardat_switch.pub admin@192.168.2.1
   ```

3. **Connect without password:**
   ```bash
   ssh -i ~/.ssh/binardat_switch admin@192.168.2.1
   ```

### Password Security

Avoid hardcoding passwords:

```python
import getpass
import paramiko

password = getpass.getpass("Switch password: ")
# Use password in SSH connection
```

## Comparison with Other Approaches

| Method | Script | Status | Pros | Cons |
|--------|--------|--------|------|------|
| **Selenium Web Automation** | `selenium_ip_change.py`, `enable_ssh_selenium.py` | ✅ Working | Guaranteed to work, handles JavaScript, one-time setup for SSH | Requires Chrome (~200MB), slower (30-60s) |
| **SSH/Paramiko CLI** | Custom scripts | ✅ After SSH enabled | Fast (1-2s), lightweight (2MB), standard network management | Requires SSH to be enabled first via web |
| **Direct HTTP API** | `switch_auth.py` | ❌ Fails | Fast, pure Python, small footprint | CGI endpoints return error 201, firmware rejects non-browser requests |

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
