# binardat-switch-config

A Python library for configuring Binardat brand network switches from default settings to custom configurations.

## About Binardat Switches

This project was developed for the **Binardat 2G20-16410GSM** 20-Port 2.5G Web Managed Switch.

![Binardat 2G20-16410GSM Switch](images/binardat-2G20-16410GSM.jpg)

### Hardware Specifications

- **Model:** 2G20-16410GSM
- **Ports:** 16x 2.5G Ethernet + 4x 10G SFP+
- **Management:** Web/CLI L3 Managed
- **Form Factor:** Desktop/Rackmount Metal

### Default Settings

When factory reset, the switch defaults to:

- **IP Address:** `192.168.2.1`
- **Username:** `admin`
- **Password:** `admin`

### Purchase Information

- **Purchased:** March 2025 from Amazon
- **Price:** $285.98
- **Links:**
  - [Amazon Product Page](https://www.amazon.com/dp/B0D97B1V5R)
  - [Binardat Product Page](https://www.binardat.com/products/20-port-25g-web-managed-switch,-16x25g-ethernet,-4x10-gigabit-sfp-ports,-web-cli-l3-managed,-metal-multi-gigabit-desktop-rackmount-network-switch-1)

## Docker Quick Start

The fastest way to enable SSH on your Binardat switch is using Docker:

### Default Configuration

The image comes pre-configured with common defaults:
- **Switch IP**: 192.168.2.1
- **Username**: admin
- **Password**: admin
- **SSH Port**: 22

```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Custom Credentials

If you've changed the default credentials:

```bash
docker run --network host \
  -e SWITCH_IP=192.168.1.100 \
  -e SWITCH_USERNAME=myadmin \
  -e SWITCH_PASSWORD=mypassword \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

## Documentation
- [Docker Quick Start](docs/docker/quickstart.md) - Get started in minutes
- [Docker Usage Guide](docs/docker/usage.md) - Comprehensive reference
- [Troubleshooting](docs/docker/troubleshooting.md) - Common issues and solutions

## Project Structure

```
binardat-switch-config/
├── src/
│   └── binardat_switch_config/  # Main package
├── tests/                        # Test suite
├── docs/                         # Documentation
└── pyproject.toml                # Project configuration
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please ensure:
- All code follows PEP 8 style guidelines
- Type hints are provided for all functions
- Google-style docstrings are included
- Tests are included for new functionality
- All pre-commit hooks pass

## Versioning

This project uses date-based versioning: `YYYY.MM.DD`
