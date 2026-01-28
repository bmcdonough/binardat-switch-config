# Changelog

All notable changes to binardat-ssh-enabler Docker image are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Python package structure with proper src-layout
- CLI entry point via `binardat-config` command
- Version management from VERSION file in `__init__.py`
- `pyproject.toml` for modern Python packaging
- `--version` flag to display package version

### Changed
- **BREAKING**: Standalone `enable_ssh.py` script replaced with proper Python package
- **BREAKING**: Direct script execution `python enable_ssh.py` no longer supported - install package first
- Refactored code into modular structure: `cli.py`, `ssh_enabler.py`, `__init__.py`
- Docker image now installs package instead of copying scripts
- Docker entry point uses `binardat-config` CLI command
- CLI interface remains backward compatible (same arguments and behavior)

### Removed
- Standalone `src/enable_ssh.py` script (replaced by package modules)
- Reference to non-existent `rc4_crypto.py` from Dockerfile

### Fixed
- Dockerfile now correctly installs all dependencies via package instead of requirements file

## [2026.01.28] - 2026-01-28

### Added
- Initial Docker image for SSH enablement on Binardat switches
- Selenium-based web automation for switch configuration
- Environment variable configuration support
- Default credentials support (192.168.2.1, admin/admin)
- Chrome headless browser automation
- Non-root user security (switchuser:1000)

### Documentation
- Docker quick start guide
- Comprehensive usage guide
- Troubleshooting guide
- Development setup documentation
