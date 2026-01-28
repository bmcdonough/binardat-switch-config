# Docker Usage Guide

Comprehensive guide for using the Binardat SSH Enabler Docker image.

## Table of Contents

- [Version Management](#version-management)
- [Configuration Methods](#configuration-methods)
- [Runtime Configuration](#runtime-configuration)
- [Docker Networking](#docker-networking)
- [Security Considerations](#security-considerations)
- [Multi-Switch Workflows](#multi-switch-workflows)
- [Docker Compose](#docker-compose)
- [Advanced Usage](#advanced-usage)

## Version Management

### Docker Image Tags

The `binardat-switch-config` image is published with multiple tags to support different use cases:

| Tag | Description | Stability | Use Case |
|-----|-------------|-----------|----------|
| `v2026.01.28` | Specific version | Immutable | Production (recommended) |
| `2026.01` | Month alias | Updates monthly | Track monthly releases |
| `2026` | Year alias | Updates yearly | Track yearly releases |
| `latest` | Latest stable | Updates on release | Development and testing |
| `rc` | Release candidate | Pre-release | Testing new features |

### Production Best Practices

**Always pin to specific versions in production**:

```bash
# Good - Specific version (reproducible)
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:v2026.01.28

# Avoid - Latest tag (can change unexpectedly)
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest
```

**Docker Compose with specific version**:

```yaml
version: '3.8'
services:
  ssh-enabler:
    image: ghcr.io/bmcdonough/binardat-switch-config:v2026.01.28  # Pinned version
    environment:
      - SWITCH_IP=192.168.2.1
    network_mode: host
```

### Development Workflows

For development and testing, using `latest` is acceptable:

```bash
# Development - Use latest tag
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest
```

### Version Verification

Check which version is currently running:

```bash
# Check image version label
docker inspect ghcr.io/bmcdonough/binardat-switch-config:latest | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.version"'

# Check image creation date
docker inspect ghcr.io/bmcdonough/binardat-switch-config:latest | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.created"'

# View all image labels
docker inspect ghcr.io/bmcdonough/binardat-switch-config:latest | \
  jq '.[0].Config.Labels'
```

### Upgrading Versions

To upgrade to a newer version:

```bash
# Pull the new version
docker pull ghcr.io/bmcdonough/binardat-switch-config:v2026.02.15

# Update your docker-compose.yml or run command with new version
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:v2026.02.15
```

**Note**: The `:latest` tag updates automatically on pull, so always specify versions explicitly if reproducibility is important.

For complete versioning documentation, see [Versioning and Release Process](versioning-and-releases.md).

## Configuration Methods

The Docker image supports three configuration methods (in priority order):

### 1. Command-Line Arguments (Highest Priority)

Arguments passed to the container override all other configuration:

```bash
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest \
  --switch-ip 192.168.2.100 \
  --username admin \
  --password mypassword \
  --port 2222 \
  --timeout 15
```

Available arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--switch-ip` | Switch IP address | `192.168.2.1` |
| `--username`, `-u` | Login username | `admin` |
| `--password`, `-p` | Login password | `admin` |
| `--port` | SSH port number | `22` |
| `--timeout` | Timeout in seconds | `10` |
| `--show-browser` | Show browser (for debugging) | Headless mode |
| `--no-verify` | Skip SSH port verification | Verify enabled |
| `--help`, `-h` | Show help message | - |

### 2. Environment Variables (Medium Priority)

Set via `-e` flag or `--env-file`:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.100 \
  -e SWITCH_USERNAME=admin \
  -e SWITCH_PASSWORD=mypassword \
  -e SWITCH_SSH_PORT=2222 \
  -e TIMEOUT=15 \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SWITCH_IP` | Switch IP address | `192.168.2.1` |
| `SWITCH_USERNAME` | Login username | `admin` |
| `SWITCH_PASSWORD` | Login password | `admin` |
| `SWITCH_SSH_PORT` | SSH port number | `22` |
| `TIMEOUT` | Operation timeout | `10` |
| `CHROMEDRIVER_PATH` | ChromeDriver location | `/usr/bin/chromedriver` |

### 3. Default Values (Lowest Priority)

If no configuration is provided, the image uses these defaults:

- Switch IP: `192.168.2.1`
- Username: `admin`
- Password: `admin`
- SSH Port: `22`
- Timeout: `10` seconds

## Runtime Configuration

### Using Environment Files

Create a `.env` file for reusable configuration:

```env
# Switch connection settings
SWITCH_IP=192.168.2.50
SWITCH_USERNAME=admin
SWITCH_PASSWORD=SecurePassword123

# SSH configuration
SWITCH_SSH_PORT=22

# Operation settings
TIMEOUT=15
```

Run with the environment file:

```bash
docker run --network host --env-file .env ghcr.io/bmcdonough/binardat-switch-config:latest
```

**Security tip**: Always restrict environment file permissions:

```bash
chmod 600 .env
echo ".env" >> .gitignore  # Never commit to git
```

### Using Docker Secrets (Recommended for Production)

Docker secrets provide secure credential storage:

```bash
# Create secrets
echo "admin" | docker secret create switch_username -
echo "mypassword" | docker secret create switch_password -

# Run with secrets (requires Docker Swarm)
docker service create \
  --name ssh-enabler \
  --secret switch_username \
  --secret switch_password \
  --network host \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

### Interactive Configuration

Get help on available options:

```bash
docker run --rm ghcr.io/bmcdonough/binardat-switch-config:latest --help
```

## Docker Networking

### Why `--network host` is Required

The container must access switches on your local network. Docker's default bridge network isolates containers from the host's network interfaces.

**Required**:
```bash
docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest
```

**Will NOT work** (default bridge network):
```bash
docker run ghcr.io/bmcdonough/binardat-switch-config:latest
# Error: Connection refused
```

### Network Modes Explained

| Mode | Access to Local Network | Use Case |
|------|------------------------|----------|
| `host` | ✓ Yes | **Required** for switch access |
| `bridge` | ✗ No | Won't work for this use case |
| `none` | ✗ No | Won't work for this use case |

### Accessing Switches on Different Subnets

If your switches are on a different subnet than your Docker host:

1. **Add a route** to the switch network:
   ```bash
   sudo ip route add 192.168.2.0/24 via 192.168.1.1
   ```

2. **Use a VPN container** as a network intermediary
3. **Run on a host** in the same subnet as the switches

## Security Considerations

### Credential Management

**DON'T** hardcode passwords in scripts:
```bash
# Bad practice
docker run --network host \
  -e SWITCH_PASSWORD=SuperSecret123 \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

**DO** use environment files with restricted permissions:
```bash
# Good practice
chmod 600 .env
docker run --network host --env-file .env ghcr.io/bmcdonough/binardat-switch-config:latest
```

**BEST** use Docker secrets in production:
```bash
echo "mypassword" | docker secret create switch_password -
```

### Container Security

The image follows security best practices:

- **Non-root user**: Runs as `switchuser` (uid 1000)
- **Minimal base**: Uses `python:3.12-slim`
- **No SSH keys stored**: Credentials are runtime-only
- **Read-only filesystem** compatible:
  ```bash
  docker run --network host --read-only ghcr.io/bmcdonough/binardat-switch-config:latest
  ```

### Network Security

- **Temporary access**: Container only runs during enablement
- **No persistent connections**: Exits after SSH is enabled
- **Audit logs**: All output is logged to stdout/stderr

## Multi-Switch Workflows

### Enabling SSH on Multiple Switches

Create a switch inventory file (`switches.txt`):

```
192.168.2.1
192.168.2.2
192.168.2.3
192.168.2.4
```

Use a bash loop:

```bash
#!/bin/bash
while IFS= read -r switch_ip; do
  echo "Enabling SSH on $switch_ip..."
  docker run --network host \
    -e SWITCH_IP="$switch_ip" \
    -e SWITCH_USERNAME=admin \
    -e SWITCH_PASSWORD=admin \
    ghcr.io/bmcdonough/binardat-switch-config:latest

  echo "Completed: $switch_ip"
  echo "---"
done < switches.txt
```

### Parallel Execution

Enable SSH on multiple switches simultaneously:

```bash
#!/bin/bash
switches=("192.168.2.1" "192.168.2.2" "192.168.2.3")

for switch in "${switches[@]}"; do
  docker run --network host \
    -e SWITCH_IP="$switch" \
    --env-file .env \
    ghcr.io/bmcdonough/binardat-switch-config:latest &
done

# Wait for all background jobs to complete
wait
echo "All switches processed"
```

### CSV Input with Different Credentials

Process a CSV file with per-switch credentials (`switches.csv`):

```csv
ip,username,password,port
192.168.2.1,admin,password1,22
192.168.2.2,admin,password2,22
192.168.2.3,netadmin,password3,2222
```

Processing script:

```bash
#!/bin/bash
# Skip header line
tail -n +2 switches.csv | while IFS=, read -r ip username password port; do
  echo "Enabling SSH on $ip..."
  docker run --network host \
    -e SWITCH_IP="$ip" \
    -e SWITCH_USERNAME="$username" \
    -e SWITCH_PASSWORD="$password" \
    -e SWITCH_SSH_PORT="$port" \
    ghcr.io/bmcdonough/binardat-switch-config:latest
done
```

## Docker Compose

### Basic Configuration

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  ssh-enabler:
    image: ghcr.io/bmcdonough/binardat-switch-config:latest
    environment:
      - SWITCH_IP=192.168.2.1
      - SWITCH_USERNAME=admin
      - SWITCH_PASSWORD=admin
      - SWITCH_SSH_PORT=22
    network_mode: host
```

Run:

```bash
docker-compose up
```

### Using Environment Files

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  ssh-enabler:
    image: ghcr.io/bmcdonough/binardat-switch-config:latest
    env_file:
      - .env
    network_mode: host
```

`.env`:

```env
SWITCH_IP=192.168.2.1
SWITCH_USERNAME=admin
SWITCH_PASSWORD=admin
```

### Multiple Switches

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  switch-1:
    image: ghcr.io/bmcdonough/binardat-switch-config:latest
    environment:
      - SWITCH_IP=192.168.2.1
      - SWITCH_USERNAME=admin
      - SWITCH_PASSWORD=admin
    network_mode: host

  switch-2:
    image: ghcr.io/bmcdonough/binardat-switch-config:latest
    environment:
      - SWITCH_IP=192.168.2.2
      - SWITCH_USERNAME=admin
      - SWITCH_PASSWORD=admin
    network_mode: host

  switch-3:
    image: ghcr.io/bmcdonough/binardat-switch-config:latest
    environment:
      - SWITCH_IP=192.168.2.3
      - SWITCH_USERNAME=admin
      - SWITCH_PASSWORD=admin
    network_mode: host
```

Run all:

```bash
docker-compose up
```

## Advanced Usage

### Debugging with Visible Browser

For troubleshooting, show the browser window:

```bash
docker run --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/bmcdonough/binardat-switch-config:latest \
  --show-browser
```

**Note**: Requires X11 forwarding setup on your host.

### Custom ChromeDriver Path

Override the default ChromeDriver location:

```bash
docker run --network host \
  -e CHROMEDRIVER_PATH=/custom/path/chromedriver \
  -v /path/to/chromedriver:/custom/path/chromedriver \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

### Increased Timeout for Slow Networks

For switches on slow or unreliable networks:

```bash
docker run --network host \
  -e TIMEOUT=30 \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

### Skip SSH Verification

If you don't want to verify SSH port accessibility after enablement:

```bash
docker run --network host \
  ghcr.io/bmcdonough/binardat-switch-config:latest \
  --no-verify
```

### Capture Logs

Save container output to a file:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.1 \
  ghcr.io/bmcdonough/binardat-switch-config:latest \
  2>&1 | tee ssh-enable.log
```

### Run as One-Liner

For quick operations:

```bash
docker run --rm --network host -e SWITCH_IP=192.168.2.50 ghcr.io/bmcdonough/binardat-switch-config:latest
```

The `--rm` flag automatically removes the container after it exits.

## Container Lifecycle

### Automatic Cleanup

Containers automatically exit after SSH enablement:

```bash
docker run --rm --network host ghcr.io/bmcdonough/binardat-switch-config:latest
```

The `--rm` flag ensures the container is removed after exit.

### Manual Cleanup

List and remove old containers:

```bash
# List all containers
docker ps -a

# Remove specific container
docker rm <container_id>

# Remove all stopped containers
docker container prune
```

### Image Updates

Pull the latest image:

```bash
docker pull ghcr.io/bmcdonough/binardat-switch-config:latest
```

## Exit Codes

The container returns standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | SSH enablement failed |
| `130` | Interrupted (Ctrl+C) |
| `143` | Terminated (SIGTERM) |

Use in scripts:

```bash
if docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest; then
  echo "SSH enabled successfully"
else
  echo "Failed to enable SSH"
  exit 1
fi
```

## Troubleshooting

For common issues and solutions, see the [Troubleshooting Guide](troubleshooting.md).

## Further Reading

- [Quick Start Guide](quickstart.md) - Get started quickly
- [Building Custom Images](building.md) - Customize the Docker image
- [Troubleshooting Guide](troubleshooting.md) - Solve common problems
- [GitHub Repository](https://github.com/bmcdonough/binardat-switch-config) - Source code and issues
