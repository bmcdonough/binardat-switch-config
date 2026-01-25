# binardat-switch-config

A Python library for configuring Binardat brand network switches from default settings to custom configurations.

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

# Connect to a switch
conn = connect_to_switch("192.168.1.1", username="admin", password="secret")

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
