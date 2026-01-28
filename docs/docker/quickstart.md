# Docker Quick Start

Enable SSH on your Binardat switch in seconds using Docker.

## TL;DR

```bash
# Run with default settings (192.168.2.1, admin/admin)
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest

# Or with custom IP
docker run --network host \
  -e SWITCH_IP=192.168.2.50 \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## Prerequisites

- Docker installed and running
- Network access to your Binardat switch
- Switch at default IP (192.168.2.1) or known IP address

## Version Selection

### Choosing a Docker Tag

Multiple image tags are available for different use cases:

- **`:latest`** - Always the newest stable release (good for testing and development)
- **`:v2026.01.28`** - Specific version (recommended for production)
- **`:2026.01`** - Latest release in January 2026 (auto-updates monthly)
- **`:2026`** - Latest release in 2026 (auto-updates yearly)

**Production Recommendation**: Pin to a specific version for reproducibility:

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:v2026.01.28
```

**Development/Testing**: Use `latest` for automatic updates:

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Checking Image Version

To verify which version you're running:

```bash
docker inspect ghcr.io/bmcdonough/binardat-ssh-enabler:latest | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.version"'
```

For more details on versioning, see [Versioning and Release Process](versioning-and-releases.md).

## Basic Usage

### Default Configuration

The image comes pre-configured with common defaults:
- **Switch IP**: 192.168.2.1
- **Username**: admin
- **Password**: admin
- **SSH Port**: 22

Simply run:

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Custom Switch IP

If your switch is at a different IP address:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.100 \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Custom Credentials

If you've changed the default credentials:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.50 \
  -e SWITCH_USERNAME=myadmin \
  -e SWITCH_PASSWORD=mypassword \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Custom SSH Port

To enable SSH on a non-standard port:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.50 \
  -e SWITCH_SSH_PORT=2222 \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## Building Locally

If you prefer to build the image yourself:

```bash
# Clone the repository
git clone https://github.com/bmcdonough/binardat-switch-config.git
cd binardat-switch-config

# Checkout develop branch
git checkout develop

# Build the image
docker build -t binardat-ssh-enabler:latest .

# Run it
docker run --network host binardat-ssh-enabler:latest
```

## Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  ssh-enabler:
    image: ghcr.io/bmcdonough/binardat-ssh-enabler:latest
    environment:
      - SWITCH_IP=192.168.2.1
      - SWITCH_USERNAME=admin
      - SWITCH_PASSWORD=admin
    network_mode: host
```

Then run:

```bash
docker-compose up
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SWITCH_IP` | Switch IP address | `192.168.2.1` |
| `SWITCH_USERNAME` | Login username | `admin` |
| `SWITCH_PASSWORD` | Login password | `admin` |
| `SWITCH_SSH_PORT` | SSH port number | `22` |
| `TIMEOUT` | Operation timeout (seconds) | `10` |

## Using Environment Files

Create a `.env` file:

```env
SWITCH_IP=192.168.2.50
SWITCH_USERNAME=admin
SWITCH_PASSWORD=mypassword
SWITCH_SSH_PORT=22
```

Run with the environment file:

```bash
docker run --network host --env-file .env ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## Command-Line Arguments

You can also pass arguments directly (these override environment variables):

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest \
  --switch-ip 192.168.2.100 \
  --username admin \
  --password mypass
```

View all available options:

```bash
docker run --rm ghcr.io/bmcdonough/binardat-ssh-enabler:latest --help
```

## Verification

After running the container, you should see output similar to:

```
============================================================
Enabling SSH on switch: 192.168.2.1
============================================================

Setting up Chrome WebDriver...
Navigating to http://192.168.2.1/...
Waiting for login form...
Logging in as 'admin'...
✓ Login successful
Looking for Monitor Management menu...
✓ Navigated to SSH configuration page
✓ Form submitted successfully
✓ Configuration save command sent

✓ SSH enablement process completed successfully
SSH service should now be active...

============================================================
Verifying SSH port 22 accessibility...
============================================================

✓ SSH port 22 is accessible

You can now connect via SSH:
  ssh admin@192.168.2.1

============================================================
SSH ENABLEMENT COMPLETED
Switch: 192.168.2.1
Port: 22
============================================================
```

## Next Steps

Once SSH is enabled, connect to your switch:

```bash
ssh admin@192.168.2.1
```

## Troubleshooting

### "Connection refused" or "Timeout"

Make sure you're using `--network host` so Docker can access your local network:

```bash
docker run --network host ...
```

### "Login failed"

Verify your credentials are correct:

```bash
docker run --network host \
  -e SWITCH_USERNAME=yourusername \
  -e SWITCH_PASSWORD=yourpassword \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### SSH port not accessible after enablement

The switch may require a reboot. Check the switch web interface or try rebooting it.

### Need more help?

See the [full usage documentation](usage.md) or [troubleshooting guide](troubleshooting.md).

## Security Best Practices

1. **Don't hardcode passwords**: Use environment files or Docker secrets
2. **Restrict .env file permissions**:
   ```bash
   chmod 600 .env
   ```
3. **Use Docker secrets for production**:
   ```bash
   echo "mypassword" | docker secret create switch_password -
   ```
4. **Change default credentials** on your switches immediately after setup

## Links

- [Full Usage Documentation](usage.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Building Custom Images](building.md)
- [GitHub Repository](https://github.com/bmcdonough/binardat-switch-config)
