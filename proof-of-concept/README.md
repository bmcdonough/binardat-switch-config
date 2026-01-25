# Proof of Concept: Web-Based IP Configuration

This directory contains proof-of-concept scripts for automating IP address configuration on Binardat switches (model 2G20-16410GSM) via their web interface.

## Overview

These scripts demonstrate the feasibility of programmatically:
1. Authenticating to the switch web interface using RC4-encrypted credentials
2. Navigating to the network configuration pages
3. Changing the IP address, subnet mask, and gateway
4. Verifying the configuration change

## Security Warnings

⚠️ **Important Security Considerations:**
- The switch uses HTTP (not HTTPS), so all traffic is unencrypted
- RC4 encryption is cryptographically weak and considered insecure by modern standards
- Credentials transmitted over the network can be intercepted
- These scripts are for controlled networks only
- Never use default credentials (admin/admin) in production

## Prerequisites

- Python 3.9 or higher
- Binardat switch accessible on the network (default: 192.168.2.1)
- Network connectivity from your machine to the switch

## Installation

From the repository root:

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Install dependencies (already included in pyproject.toml)
pip install -e ".[dev]"
```

## Scripts

### Phase 2: Reconnaissance

**`01_reconnaissance.py`** - Web interface analysis
- Fetches the login page and analyzes its structure
- Extracts JavaScript files and identifies the RC4 key
- Documents form fields and session management
- Usage: `python proof-of-concept/01_reconnaissance.py`

**`analyze_login.py`** - Interactive login analysis
- Extracts RC4 encryption key from JavaScript
- Shows form field names and any CSRF tokens
- Tests basic connectivity
- Usage: `python proof-of-concept/analyze_login.py`

### Phase 3: Encryption

**`rc4_crypto.py`** - RC4 encryption module
- Implements RC4 encryption matching the switch's JavaScript
- Provides functions for encrypting credentials
- Can be imported by other scripts

**`test_rc4.py`** - RC4 verification
- Tests the RC4 implementation against known inputs/outputs
- Compares with JavaScript output from browser console
- Usage: `python proof-of-concept/test_rc4.py`

### Phase 4: Authentication

**`switch_auth.py`** - Session management module
- `SwitchSession` class for managing HTTP sessions
- Login, logout, and session validation
- Menu extraction and page discovery methods
- Menu-aware navigation with automatic fallback to common URLs
- Used by other scripts for authentication

**`02_test_login.py`** - Login testing
- Tests successful login with credentials
- Verifies session persistence
- Tests error handling for invalid credentials
- Usage: `python proof-of-concept/02_test_login.py --host 192.168.2.1 --username admin --password admin`

### Phase 5: Menu Discovery

**`03_menu_extraction.py`** - Menu structure extraction
- Discovers all available pages in the switch interface
- Extracts navigation from HTML and JavaScript
- Categorizes pages by function (network, system, security, etc.)
- Outputs JSON file with complete menu hierarchy
- Usage:
  ```bash
  # Basic extraction
  python proof-of-concept/03_menu_extraction.py --username admin --password admin

  # With tree display
  python proof-of-concept/03_menu_extraction.py --username admin --password admin --display-tree

  # Search for specific pages
  python proof-of-concept/03_menu_extraction.py --username admin --password admin --search "ip"
  ```
- Output: `menu_structure.json` - Complete menu hierarchy

### Phase 6: IP Configuration

**`04_test_ip_change.py`** - IP change testing (UPDATED for Phase 6)
- Reads current IP configuration
- Uses menu-aware navigation if menu_structure.json exists
- Automatic fallback to common URLs if menu not available
- Prompts for new IP settings with validation
- Submits configuration change
- Dry-run mode for testing without changes
- Usage:
  ```bash
  # Read current config (uses menu if available)
  python proof-of-concept/04_test_ip_change.py --host 192.168.2.1

  # Change IP (dry-run)
  python proof-of-concept/04_test_ip_change.py --change-ip \
    --new-ip 192.168.1.100 --subnet-mask 255.255.255.0 --dry-run

  # Change IP (live)
  python proof-of-concept/04_test_ip_change.py --change-ip \
    --new-ip 192.168.1.100 --subnet-mask 255.255.255.0 \
    --gateway 192.168.1.1
  ```

### Phase 7: Complete Tool

**`change_ip_address.py`** - Main CLI tool
- Complete end-to-end IP address change
- Connects to old IP, changes configuration, verifies on new IP
- Supports dry-run mode for testing
- Usage:
  ```bash
  python proof-of-concept/change_ip_address.py \
    --old-ip 192.168.2.1 \
    --new-ip 192.168.1.100 \
    --subnet 255.255.255.0 \
    --gateway 192.168.1.1 \
    --username admin \
    --password admin \
    --verify
  ```

**`config_example.yaml`** - Configuration template
- Example YAML configuration for batch operations
- Shows structure for multiple switch configurations
- Copy to `config.local.yaml` for actual use (gitignored)

## Typical Workflow

### Single Switch Configuration

1. **Test connectivity:**
   ```bash
   python proof-of-concept/01_reconnaissance.py
   ```

2. **Test authentication:**
   ```bash
   python proof-of-concept/02_test_login.py --host 192.168.2.1 --username admin --password admin
   ```

3. **Extract menu structure (recommended):**
   ```bash
   python proof-of-concept/03_menu_extraction.py --username admin --password admin --display-tree
   ```
   This discovers all available pages and helps locate the IP configuration page.

4. **Test IP change (dry-run):**
   ```bash
   python proof-of-concept/change_ip_address.py \
     --old-ip 192.168.2.1 \
     --new-ip 192.168.1.100 \
     --subnet 255.255.255.0 \
     --username admin \
     --password admin \
     --dry-run
   ```

5. **Perform IP change:**
   ```bash
   python proof-of-concept/change_ip_address.py \
     --old-ip 192.168.2.1 \
     --new-ip 192.168.1.100 \
     --subnet 255.255.255.0 \
     --username admin \
     --password admin \
     --verify
   ```

### Batch Configuration

1. Copy `config_example.yaml` to `config.local.yaml`
2. Edit `config.local.yaml` with your switch details
3. Run batch script (when implemented)

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to switch at 192.168.2.1

**Solutions:**
- Verify switch is powered on and connected
- Check your machine's network configuration
- Ensure you're on the same subnet (e.g., 192.168.2.x/24)
- Try pinging the switch: `ping 192.168.2.1`
- Verify no firewall is blocking HTTP traffic

### Authentication Issues

**Problem:** Login fails with correct credentials

**Solutions:**
- Verify the RC4 encryption key matches the switch firmware
- Check if the switch firmware version has changed
- Try logging in via web browser to confirm credentials
- Review the switch's JavaScript for any authentication changes

### IP Change Issues

**Problem:** IP change submitted but switch not responding on new IP

**Solutions:**
- Wait 30-60 seconds for switch to apply changes
- Verify the new IP is on a valid subnet
- Check if new IP conflicts with another device
- Ensure your machine can route to the new subnet
- Try accessing the switch via web browser at new IP

### Network Interruption

**Problem:** Lose connectivity during IP change

**Expected Behavior:** This is normal when changing subnets. The script should:
1. Submit the change
2. Wait for the switch to reboot/apply settings
3. Attempt reconnection on the new IP
4. Verify successful configuration

If verification fails, manually check the switch via web browser.

### Menu Discovery Issues

**Problem:** Menu extraction finds no or very few pages

**Solutions:**
- Check if the switch uses frames/framesets (older interface design)
- Examine the HTML source in a web browser to identify menu structure
- Look for AJAX-loaded menus (check browser's network tab)
- Try accessing `/main.html`, `/menu.html`, or `/status.html` directly
- Run with `--display-tree` to see what was discovered
- Review `menu_structure.json` for partial results

**Problem:** Cannot find IP configuration page in menu

**Solutions:**
- Search the menu structure: `python 03_menu_extraction.py --search "ip" -u admin -p admin`
- Try common URLs directly: `network.html`, `ip_config.html`, `system_network.html`
- Access the switch web interface manually and note the URL
- Check if IP config is under a different category (system, config, etc.)

## Known Limitations

1. **Single switch at a time:** Scripts are designed for one switch per execution
2. **HTTP only:** No HTTPS support (switch limitation)
3. **No rollback:** Failed IP changes require manual recovery via console cable
4. **Timing dependent:** Network interruption during change can cause issues
5. **Model specific:** Only tested with Binardat 2G20-16410GSM
6. **Firmware specific:** RC4 key may change with firmware updates

## Development Notes

All scripts follow the project's coding standards:
- **Type hints:** All functions use Python 3.9+ type hints
- **Docstrings:** Google-style docstrings for all public APIs
- **Formatting:** Black (79 chars) + isort
- **Linting:** flake8, mypy, pydocstyle
- **Error handling:** Custom exceptions from `binardat_switch_config.exceptions`

To check code quality:
```bash
black proof-of-concept/
isort proof-of-concept/
flake8 proof-of-concept/
mypy proof-of-concept/
pydocstyle proof-of-concept/
```

## Future Integration

After PoC validation, these scripts will be refactored into:
- `src/binardat_switch_config/http/` - HTTP communication module
- `src/binardat_switch_config/crypto/` - Encryption utilities
- `src/binardat_switch_config/cli.py` - Production CLI tool
- `tests/` - Proper unit tests with mocked HTTP responses

## Testing

See `TESTING.md` for detailed test procedures and verification steps.

## Support

This is proof-of-concept code for internal use. For issues:
- Review the troubleshooting section above
- Check the main project documentation
- Examine network captures with Wireshark if needed
- Refer to switch documentation for firmware-specific behavior

## License

This code is part of the binardat-switch-config project and follows the same MIT license.
