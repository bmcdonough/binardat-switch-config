# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based tool for configuring Binardat brand network switches from default settings to custom configurations.

## Versioning

This project uses calendar versioning (CalVer) in the format `YYYY.MM.DD[.MICRO]`.

### Version Management

- **VERSION file**: Single source of truth for the current version (located at repository root)
- **Git tags**: Tagged with `v` prefix (e.g., `v2026.01.28`)
- **CHANGELOG.md**: All changes MUST be documented in `/CHANGELOG.md` at the repository root
  - Follow [Keep a Changelog](https://keepachangelog.com/) format
  - Add entries under `[Unreleased]` during development
  - Move to version section when releasing

### Documenting Changes

**IMPORTANT**: All code changes, features, bug fixes, and breaking changes MUST be documented in `/CHANGELOG.md`.

When making changes:
1. Add entry under `[Unreleased]` section in appropriate category:
   - `### Added` - New features
   - `### Changed` - Changes to existing functionality
   - `### Deprecated` - Soon-to-be removed features
   - `### Removed` - Removed features
   - `### Fixed` - Bug fixes
   - `### Security` - Security improvements

2. Use clear, user-facing language describing the change
3. When creating a release, move `[Unreleased]` entries to a new version section

For complete versioning documentation, see [docs/docker/versioning-and-releases.md](docs/docker/versioning-and-releases.md).

## Project Structure

This project follows the **src-layout** structure for Python packages:

```
binardat-switch-config/
├── src/
│   └── binardat_switch_config/    # Main package
│       └── __init__.py
├── tests/                          # Test suite
│   └── __init__.py
├── docs/                           # Documentation
├── pyproject.toml                  # Project configuration and dependencies
├── .pre-commit-config.yaml         # Pre-commit hooks
├── .github/                        # GitHub workflows
└── README.md
```

**Why src-layout?**
- Prevents accidentally importing from the wrong location during development
- Forces proper installation of the package for testing
- Standard modern Python practice

## Current Package Structure

The package currently implements SSH enablement functionality:

```
src/binardat_switch_config/
├── __init__.py           # Package initialization, version management
├── cli.py                # CLI entry point and argument parsing
└── ssh_enabler.py        # SSHEnabler class and utilities
```

**Version Management:**
- Version is read from `/VERSION` file at runtime
- Exposed as `binardat_switch_config.__version__`
- Also specified in `pyproject.toml` (keep in sync during releases)

**CLI Entry Point:**
- Command: `binardat-config` (installed via console_scripts)
- Entry point: `binardat_switch_config.cli:main`
- Maintains same CLI arguments as original script

**Modules:**
- `__init__.py` - Package initialization with version loading and public API exports
- `cli.py` - Command-line interface using argparse, signal handling, and environment variable support
- `ssh_enabler.py` - Core SSHEnabler class using Selenium for web automation

**Future modules** will be added to `src/binardat_switch_config/` as needed.

## Expected Future Architecture

Based on the project goals, additional modules may include:

- **Switch Communication Layer** (`src/binardat_switch_config/connection/`) - Direct SSH/Telnet/HTTP API communication
- **Configuration Management** (`src/binardat_switch_config/config/`) - Parsing and applying switch configuration settings

## Development Environment

**Python Version:** 3.9+

**Setup:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"    # Install package in editable mode with dev dependencies
pre-commit install
```

**Dependency Management:**
- `pyproject.toml` is the **source of truth** for all dependencies
- `requirements.txt` and `requirements-dev.txt` are maintained for compatibility but should not be edited directly
- Add runtime dependencies to `[project.dependencies]` in `pyproject.toml`
- Add development dependencies to `[project.optional-dependencies.dev]` in `pyproject.toml`

**Code Quality Tools:**
- **black** - Code formatter (79 character line length, PEP8)
- **isort** - Import sorting (black-compatible profile)
- **flake8** - Linting (configured to defer to black on conflicts via E203, W503 ignores)
- **mypy** - Static type checking (strict mode)
- **pydocstyle** - Docstring style checking (Google style convention)
- **pre-commit** - Git hooks to catch issues before commit

**Common Commands:**
- `black .` - Format code
- `isort .` - Sort imports
- `flake8 .` - Run linting
- `mypy .` - Run type checking
- `pydocstyle .` - Check docstring style
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage
- `pre-commit run --all-files` - Run all pre-commit hooks

## Docstring Requirements

**All public modules, classes, functions, and methods MUST have docstrings.**

This project uses **Google-style docstrings** enforced by `pydocstyle`:

**Module docstring example:**
```python
"""Module for switch connection management.

This module provides classes and functions for establishing and managing
connections to Binardat network switches via SSH, Telnet, or HTTP.
"""
```

**Function/method docstring example:**
```python
def connect_to_switch(
    host: str, port: int = 22, timeout: float = 30.0
) -> SwitchConnection:
    """Connect to a Binardat switch via SSH.

    Args:
        host: The IP address or hostname of the switch.
        port: The SSH port to connect to. Defaults to 22.
        timeout: Connection timeout in seconds. Defaults to 30.0.

    Returns:
        An active SwitchConnection instance.

    Raises:
        ConnectionError: If the connection cannot be established.
        TimeoutError: If the connection times out.

    Example:
        >>> conn = connect_to_switch("192.168.1.1")
        >>> conn.send_command("show version")
    """
```

**Class docstring example:**
```python
class SwitchConfig:
    """Configuration container for Binardat switches.

    This class represents a complete switch configuration including VLANs,
    ports, routing, and security settings.

    Attributes:
        hostname: The switch hostname.
        vlans: Dictionary of VLAN configurations.
        ports: List of port configurations.
    """

    def __init__(self, hostname: str) -> None:
        """Initialize a new switch configuration.

        Args:
            hostname: The desired hostname for the switch.
        """
```

**Docstring Configuration:**
- Convention: Google style
- Ignored errors: D100 (missing module docstring in __init__.py), D104 (missing docstring in public package)
- Tests are excluded from docstring requirements

**CI/CD:**
- GitHub Actions runs linting and tests on push/PR to main and develop branches
- Linting job checks isort, black, flake8, and mypy
- Test job runs pytest across Python 3.9, 3.10, 3.11, and 3.12
- Coverage reports uploaded to Codecov
