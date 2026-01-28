# For Development

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
