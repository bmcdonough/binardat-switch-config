# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning (`YYYY.MM.DD`).

## [Unreleased]

### Added

- **Docker Support** - Complete Docker packaging for SSH enablement functionality
  - Dockerfile with Python 3.12-slim base and Chromium/ChromeDriver
  - Docker Compose support for easy deployment
  - Runtime configuration via environment variables (SWITCH_IP, SWITCH_USERNAME, etc.)
  - Non-root container execution for security (switchuser, uid 1000)
  - Host network mode support for switch access
  - Comprehensive Docker documentation:
    - Quick Start guide (`docs/docker/quickstart.md`)
    - Usage guide (`docs/docker/usage.md`)
    - Building guide (`docs/docker/building.md`)
    - Troubleshooting guide (`docs/docker/troubleshooting.md`)
  - Helper scripts for building and testing Docker images (`scripts/build-docker.sh`, `scripts/test-docker.sh`)
  - Configuration examples (`examples/env.example`, `examples/docker-compose.example.yml`)
- **Refactored SSH Enabler** - Docker-compatible version of the Selenium-based SSH enabler
  - Environment variable support with fallback to CLI arguments
  - Signal handlers for graceful shutdown (SIGTERM, SIGINT)
  - Automatic ChromeDriver detection (Docker vs local development)
  - Enhanced logging for container environments
  - Removed debug HTML file saving (Docker-friendly)
- **Source Code Organization**
  - New `src/` directory with production-ready code
  - `src/enable_ssh.py` - Refactored SSH enabler with Docker support
  - `src/rc4_crypto.py` - RC4 encryption module (copied from proof-of-concept)
- **Proof-of-concept implementation for web-based IP configuration**
  - Complete PoC scripts in proof-of-concept/ directory
  - Web interface reconnaissance tools (01_reconnaissance.py, analyze_login.py)
  - RC4 encryption module (rc4_crypto.py) matching switch JavaScript implementation
  - Session management and authentication (switch_auth.py)
  - **Menu structure extraction and discovery (Phase 5)**
    - 03_menu_extraction.py - Automated menu discovery script
    - HTML navigation parsing (nav elements, menus, frames)
    - JavaScript menu pattern detection
    - Automatic page categorization (network, system, security, etc.)
    - JSON output format (menu_structure.json)
    - Search functionality for finding specific pages
    - Menu extraction methods in switch_auth.py (get_main_page, extract_navigation, etc.)
  - **Menu-aware IP configuration navigation (Phase 6)**
    - Enhanced navigate_to_ip_config() with menu structure support
    - _navigate_using_menu() method with scoring and ranking
    - Automatic fallback to common URLs if menu unavailable
    - Updated get_current_ip_config() and change_ip_address() methods
    - 04_test_ip_change.py (renamed from 03_test_ip_change.py)
    - Automatic menu discovery with find_menu_file() helper
    - User-friendly messages about menu usage
  - IP configuration reading and modification capabilities
  - End-to-end CLI tool for changing switch IP addresses (change_ip_address.py)
  - Comprehensive testing scripts (02_test_login.py, 04_test_ip_change.py, test_rc4.py)
  - Example configuration file (config_example.yaml)
  - Detailed testing guide (TESTING.md)
  - PoC-specific documentation (README.md in proof-of-concept/)
  - Menu analysis documentation (docs/menu-analysis.md)
- **Runtime dependencies**
  - requests (>=2.31.0) - HTTP client with session management
  - beautifulsoup4 (>=4.12.0) - HTML parsing
  - pycryptodome (>=3.19.0) - RC4 encryption
  - pyyaml (>=6.0) - YAML configuration file support
  - selenium (>=4.16.0) - Browser automation for SSH enablement
- **Security considerations documentation**
  - HTTP (unencrypted) communication warnings
  - RC4 cryptographic weakness documentation
  - Credential handling best practices
  - Local configuration file gitignore patterns
- Initial repository setup ([`1d52005`](https://github.com/bmcdonough/binardat-switch-config/commit/1d52005))
  - README.md
  - LICENSE (MIT)
  - .gitignore (Python)
- Standard Python library structure with src-layout ([`d6a85f3`](https://github.com/bmcdonough/binardat-switch-config/commit/d6a85f3))
  - src/binardat_switch_config/ package directory
  - tests/ directory with example test
  - py.typed marker for type hint support
- Project documentation (CLAUDE.md, CHANGELOG.md)
  - Google-style docstring requirements and examples
  - Detailed development guidelines
  - Project structure documentation
- Developer documentation in docs/ directory
  - Merging workflow with issue-first approach (docs/merging.md)
  - Release process with CalVer support (docs/releases.md)
- CI/CD pipeline with GitHub Actions (linting and testing workflows)
  - Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
  - Automated linting (isort, black, flake8, mypy, pydocstyle)
  - Test coverage reporting with pytest-cov
- Code quality tooling
  - black (>=24.3.0) - Code formatter
  - isort (5.13.2) - Import sorting
  - flake8 (7.0.0) - Linting
  - mypy (1.8.0) - Type checking
  - pydocstyle (6.3.0) - Docstring validation (Google style)
- Pre-commit hooks configuration
  - All code quality tools integrated
  - Automatic checks before commit
- Project configuration via pyproject.toml
  - Single source of truth for dependencies
  - Modern Python packaging with setuptools
  - Tool configurations (black, isort, flake8, mypy, pydocstyle, pytest, coverage)
- Development dependencies management
  - pyproject.toml as primary source
  - requirements-dev.txt for compatibility
- PEP8 line length (79 characters) enforced across all tools
- Black-compatible flake8 configuration (E203, W503 ignored)
- Version management with bump-my-version (>=0.25.0)
  - CalVer configuration (YYYY.MM.DD format)
  - Support for micro releases (same-day releases)
  - Support for development builds (.devN suffix)
  - Automatic version updates in __init__.py and pyproject.toml
- Example code and tests
  - Custom exception classes (exceptions.py)
  - Example test with version validation
  - 100% test coverage
- Hardware documentation in README.md
  - Binardat 2G20-16410GSM switch specifications
  - Default switch settings (192.168.2.1, admin/admin)
  - Purchase information and product links
  - Product image in images/ directory
- Comprehensive README with installation and usage examples

### Changed

- Updated README.md with Docker quick start section and links to Docker documentation
- Project now supports both traditional Python library usage and containerized SSH enablement
- Updated README from minimal description to comprehensive documentation
- Reorganized .gitignore with trailing whitespace fixes

### Fixed

- CI workflow dependency and configuration issues ([`0b02295`](https://github.com/bmcdonough/binardat-switch-config/commit/0b02295))
  - Fixed bump-my-version version from 0.18.0 (non-existent) to >=0.25.0
  - Updated CI to use modern `pip install -e ".[dev]"` instead of requirements files
  - Fixed coverage path from `--cov=.` to `--cov=src` for src-layout
  - Added pydocstyle check to lint job
  - Scoped linting tools to src/ and tests/ directories only

### Commits

- [`1d52005`](https://github.com/bmcdonough/binardat-switch-config/commit/1d52005) - Initial commit
- [`d6a85f3`](https://github.com/bmcdonough/binardat-switch-config/commit/d6a85f3) - Organize repository into standard Python library structure
- [`0b02295`](https://github.com/bmcdonough/binardat-switch-config/commit/0b02295) - Fix CI workflow and dependency issues

[Unreleased]: https://github.com/bmcdonough/binardat-switch-config/compare/1d52005...HEAD
