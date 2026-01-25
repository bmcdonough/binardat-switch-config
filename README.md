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

## Features

- Automated switch configuration from YAML or JSON templates
- Support for SSH, Telnet, and HTTP API connections
- Validation of switch configurations before applying
- Backup and restore capabilities
- CLI interface for interactive configuration

## Installation

### For Users

```bash
pip install binardat-switch-config
```

### For Development

```bash
# Clone the repository
git clone https://github.com/bmcdonough/binardat-switch-config.git
cd binardat-switch-config

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

```python
from binardat_switch_config import SwitchConfig, connect_to_switch

# Connect to a switch (using default IP and credentials)
conn = connect_to_switch("192.168.2.1", username="admin", password="admin")

# Load and apply configuration
config = SwitchConfig.from_file("switch_config.yaml")
conn.apply_config(config)
```

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

### Running Tests

```bash
pytest                  # Run all tests
pytest --cov           # Run with coverage report
```

### Code Quality

```bash
black .                 # Format code
isort .                 # Sort imports
flake8 .                # Lint code
mypy .                  # Type check
pydocstyle .            # Check docstrings
pre-commit run --all-files  # Run all checks
```

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
