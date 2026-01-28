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

### Standard Installation

```bash
# Clone repository
git clone https://github.com/yourusername/binardat-switch-config.git
cd binardat-switch-config

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Docker Installation

See [Docker Guide](docs/DOCKER.md) for building, running, and managing Docker images.

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

## License

[LICENSE.md](LICENSE.md)

## Roadmap

- [x] Phase 1: Core backup functionality
- [ ] Phase 2: Advanced change detection with detailed diffs
- [ ] Phase 3: Enhanced inventory management
- [ ] Phase 4: Rollback capability
- [ ] Phase 5: Production hardening
- [ ] Future: Web UI for configuration management
- [ ] Future: Compliance checking
- [ ] Future: Configuration templates
