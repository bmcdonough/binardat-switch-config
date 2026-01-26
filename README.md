# Binardat Switch Config

Network switch configuration management with netmiko. Automatically backup, version control, and rollback configurations for network switches.

## Features

**Phase 1 - Core Backup (MVP)** ✅ Implemented

- SSH connection to network switches using netmiko
- Configuration retrieval (running-config, startup-config)
- Configuration normalization (removes timestamps, uptime, dynamic content)
- Change detection (only commits when config actually changes)
- Git version control with automatic commits
- Push to remote git repository
- Support for multiple vendors (Cisco IOS/IOS-XE, Arista, Juniper, etc.)
- Multi-switch batch backups with filtering by tags
- CLI interface with comprehensive commands

**Coming Soon:**

- Phase 2: Advanced change detection with detailed diffs
- Phase 3: Multi-switch inventory management
- Phase 4: Rollback capability to restore previous configurations
- Phase 5: Production hardening with comprehensive tests

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/binardat-switch-config.git
cd binardat-switch-config

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize Configuration Repository

```bash
# Create a new config repository
binardat-config init /var/lib/switch-configs
cd /var/lib/switch-configs
```

This creates:
- Git repository for version control
- `inventory.yaml` file for switch definitions
- `switches/` directory for storing configs

### 2. Configure Inventory

Edit `inventory.yaml` to add your switches:

```yaml
defaults:
  username: admin
  password: ${SWITCH_PASSWORD}  # Environment variable
  port: 22
  timeout: 30.0
  device_type: cisco_ios
  auto_push: true  # Automatically push to remote

switches:
  - name: switch-office-01
    host: 192.168.1.10
    location: "Office Building A"
    enabled: true
    tags: [production, office]

  - name: switch-datacenter-01
    host: 10.0.0.20
    device_type: cisco_ios
    key_file: ~/.ssh/switch_key  # SSH key authentication
    location: "Datacenter Rack 42"
    enabled: true
    tags: [production, datacenter]
```

### 3. Set Credentials

```bash
# Set password via environment variable
export SWITCH_PASSWORD="your-secure-password"

# Or use SSH key authentication (configured in inventory)
```

### 4. Backup Switches

```bash
# Backup single switch
binardat-config backup switch-office-01

# Backup all enabled switches
binardat-config backup --all

# Backup switches with specific tags
binardat-config backup --all --tags production

# Dry run (don't save changes)
binardat-config backup --all --dry-run
```

## CLI Commands

### Initialize Repository

```bash
binardat-config init <path>
```

Creates a new configuration repository with git version control.

### Backup Switches

```bash
# Single switch
binardat-config backup <switch-name>

# All enabled switches
binardat-config backup --all

# Filter by tags
binardat-config backup --all --tags production,office

# Dry run mode
binardat-config backup switch-01 --dry-run

# Custom inventory file
binardat-config backup --all --inventory /path/to/inventory.yaml
```

### Validate Inventory

```bash
binardat-config validate-inventory
```

Checks `inventory.yaml` for syntax errors and missing required fields.

### Global Options

```bash
--config-repo PATH   # Path to config repository (default: current directory)
-v, --verbose        # Enable verbose logging
-q, --quiet          # Suppress all output except errors
```

## Configuration

### Inventory File Format

```yaml
defaults:
  # Default settings applied to all switches
  username: admin
  password: ${SWITCH_PASSWORD}
  port: 22
  timeout: 30.0
  device_type: cisco_ios
  auto_push: true

switches:
  - name: switch-01              # Required: unique identifier
    host: 192.168.1.10           # Required: IP or hostname
    device_type: cisco_ios       # Optional: override default
    username: admin2             # Optional: override default
    password: ${SWITCH_PASSWORD} # Optional: override default
    key_file: ~/.ssh/key         # Optional: SSH key auth
    port: 22                     # Optional: override default
    timeout: 30.0                # Optional: override default
    location: "Office"           # Optional: description
    enabled: true                # Optional: enable/disable (default: true)
    tags: [production, office]   # Optional: tags for filtering
    auto_push: false             # Optional: override auto-push
```

### Supported Device Types

- `cisco_ios` - Cisco IOS switches
- `cisco_xe` - Cisco IOS-XE switches
- `cisco_nxos` - Cisco Nexus switches
- `cisco_asa` - Cisco ASA firewalls
- `arista_eos` - Arista EOS switches
- `juniper_junos` - Juniper JunOS devices
- `hp_procurve` - HP ProCurve switches
- `generic` - Generic devices (uses standard commands)

See netmiko documentation for full list of supported device types.

## Architecture

### Directory Structure

```
binardat-switch-config/
├── src/binardat_switch_config/
│   ├── netmiko/              # SSH connection & config retrieval
│   │   ├── connection.py     # SwitchConnection class
│   │   ├── retrieval.py      # ConfigRetriever & ConfigNormalizer
│   │   └── device_profiles.py # Device-specific commands
│   │
│   ├── storage/              # Storage & version control
│   │   ├── filesystem.py     # ConfigStorage class
│   │   └── git_manager.py    # GitManager class
│   │
│   ├── cli/                  # Command-line interface
│   │   ├── main.py          # CLI entry point
│   │   └── backup.py        # Backup command
│   │
│   └── exceptions.py         # Custom exceptions
│
├── tests/                    # Test suite
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Configuration Storage

```
/var/lib/switch-configs/      # Config repository root
├── .git/                     # Git repository
├── inventory.yaml            # Switch inventory
├── switches/                 # Switch configurations
│   ├── switch-office-01/
│   │   ├── running-config.txt
│   │   ├── startup-config.txt
│   │   └── metadata.yaml
│   └── switch-datacenter-01/
│       └── ...
```

## How It Works

### Backup Workflow

1. **Connect** - Establish SSH connection using netmiko
2. **Retrieve** - Get running-config (and startup-config if available)
3. **Normalize** - Remove timestamps, uptime, and dynamic content
4. **Detect Changes** - Compare with previous config
5. **Save** - Write to filesystem if changes detected
6. **Commit** - Create git commit with descriptive message
7. **Push** - Push to remote repository (if configured)

### Change Detection

The system normalizes configurations before comparison to avoid false positives:

- Removes timestamp lines (`Last configuration change at ...`)
- Removes uptime counters
- Removes dynamic NTP clock periods
- Removes process IDs and session IDs
- Device-specific normalization (Cisco, Juniper, etc.)

This ensures commits only happen for real configuration changes, not dynamic content.

## Scheduled Backups

Use cron to schedule automatic backups:

```bash
# Create backup script
cat > /usr/local/bin/backup-switches.sh << 'EOF'
#!/bin/bash
set -e
export SWITCH_PASSWORD=$(cat /etc/switch-configs/.password)
cd /var/lib/switch-configs
binardat-config backup --all --quiet
EOF

chmod +x /usr/local/bin/backup-switches.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-switches.sh >> /var/log/switch-backup.log 2>&1" | crontab -
```

## Git Integration

### Setup Remote Repository

```bash
cd /var/lib/switch-configs

# Add remote
git remote add origin https://github.com/yourorg/switch-configs.git

# Push initial commit
git push -u origin main
```

After setup, backups will automatically push to the remote repository (if `auto_push: true`).

### Manual Git Operations

```bash
cd /var/lib/switch-configs

# View commit history
git log --oneline

# View changes in specific file
git log -p switches/switch-01/running-config.txt

# Compare two versions
git diff <old-commit> <new-commit> switches/switch-01/running-config.txt
```

## Error Handling

The tool handles various failure scenarios:

- **Connection failures** - Retries with exponential backoff (3 attempts)
- **Authentication errors** - Reports immediately without retry
- **Retrieval failures** - Continues with other switches in batch mode
- **Git errors** - Reports but doesn't stop backup process
- **Push failures** - Logs warning but marks backup as successful

## Development

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/binardat_switch_config

# Run specific test
pytest tests/test_connection.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Run all checks
black src/ tests/ && isort src/ tests/ && mypy src/
```

## Troubleshooting

### Connection Issues

```bash
# Test with verbose logging
binardat-config -v backup switch-01

# Check inventory configuration
binardat-config validate-inventory

# Test SSH connection manually
ssh admin@192.168.1.10
```

### Permission Issues

Ensure the user running backups has:
- Write access to config repository
- SSH access to switches
- Git credentials configured

### Git Push Failures

```bash
# Check git remote
cd /var/lib/switch-configs
git remote -v

# Test manual push
git push origin main

# Configure git credentials
git config user.name "Switch Backup Bot"
git config user.email "backup@example.com"
```

## Security Considerations

- **Credentials** - Use environment variables, never hardcode passwords
- **SSH Keys** - Prefer key-based authentication over passwords
- **File Permissions** - Restrict access to config repository (chmod 700)
- **Git Repository** - Use private repository for sensitive configs
- **Audit Trail** - Git history provides complete audit trail

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Run code quality checks
5. Submit pull request

## Roadmap

- [x] Phase 1: Core backup functionality
- [ ] Phase 2: Advanced change detection with detailed diffs
- [ ] Phase 3: Enhanced inventory management
- [ ] Phase 4: Rollback capability
- [ ] Phase 5: Production hardening
- [ ] Future: Web UI for configuration management
- [ ] Future: Compliance checking
- [ ] Future: Configuration templates
