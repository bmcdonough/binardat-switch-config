# Binardat Switch SSH Enabler (Docker)

Docker image to enable SSH on Binardat 2G20-16410GSM network switches.

## Quick Start

Enable SSH on your Binardat switch with default settings:

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## With Custom IP

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.50 \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## With Custom Credentials

```bash
docker run --network host \
  -e SWITCH_IP=192.168.2.50 \
  -e SWITCH_USERNAME=admin \
  -e SWITCH_PASSWORD=mypassword \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## Default Settings

- **Switch IP**: 192.168.2.1
- **Username**: admin
- **Password**: admin
- **SSH Port**: 22

## Building Locally

```bash
# Clone this branch
git clone -b enable-ssh https://github.com/bmcdonough/binardat-switch-config.git
cd binardat-switch-config

# Build the image
docker build -t binardat-ssh-enabler:latest .

# Run it
docker run --network host binardat-ssh-enabler:latest
```

## Documentation

- [Quick Start Guide](docs/docker/quickstart.md) - Detailed usage instructions
- [Usage Guide](docs/docker/usage.md) - Comprehensive reference
- [Troubleshooting](docs/docker/troubleshooting.md) - Common issues and solutions

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SWITCH_IP` | Switch IP address | `192.168.2.1` |
| `SWITCH_USERNAME` | Login username | `admin` |
| `SWITCH_PASSWORD` | Login password | `admin` |
| `SWITCH_SSH_PORT` | SSH port number | `22` |
| `TIMEOUT` | Operation timeout | `10` |

## Docker Compose

Create a `docker-compose.yml`:

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

Run with:

```bash
docker-compose up
```

## About This Branch

This is a minimal branch containing only the Docker image for enabling SSH on Binardat switches.

For the complete project with additional functionality, see the [main branch](https://github.com/bmcdonough/binardat-switch-config).

## Supported Switch Models

- Binardat 2G20-16410GSM (20-Port 2.5G Web Managed Switch)
- Other Binardat switches with similar web interfaces

## Requirements

- Docker installed and running
- Network access to your Binardat switch
- Switch must be accessible via HTTP (web interface)

## Security Note

This tool requires access to the switch web interface. Ensure you:
- Use strong passwords
- Change default credentials after setup
- Restrict network access to switch management interfaces
- Use environment files with restricted permissions (`chmod 600 .env`)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Found a bug or have a suggestion? Please open an issue on the [main project](https://github.com/bmcdonough/binardat-switch-config/issues).
