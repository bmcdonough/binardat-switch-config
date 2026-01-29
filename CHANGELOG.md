# Changelog

All notable changes to the Binardat Switch Configuration tool are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Pre-commit hooks for automated code quality checks (isort, black, flake8, mypy, pydocstyle)
- GitHub Actions CI/CD workflow with linting and testing across Python 3.9-3.12
- Enhanced tool configurations for flake8, coverage, mypy, pytest, and pydocstyle
- Type marker file (py.typed) for better mypy support

### Changed
- Updated minimum versions for dev dependencies to match tested versions
- Enhanced mypy configuration with stricter type checking rules
- Improved pytest configuration with additional test discovery patterns
- Enhanced isort and black configurations for better code formatting

### Fixed
- All flake8 errors: line length violations, unused imports, f-strings without placeholders, bare except
- All mypy errors: missing type annotations, optional attribute access
- Code now passes all pre-commit hooks without errors

## [2026.01.29] - 2026-01-29

### Added
- SSH disablement functionality via `--disable` CLI flag
- Ability to disable SSH on Binardat switches using the same Selenium-based automation
- Verification of SSH port closure after disablement (when verification is not disabled)

### Changed
- Docker image renamed from `binardat-ssh-enabler` to `binardat-switch-config` throughout all documentation and configuration files
- Updated `.dockerignore` to include `pyproject.toml` in Docker builds (previously excluded)
- Updated `.dockerignore` to explicitly include `README.md` in Docker builds
- Refactored SSH form interaction to support both enable and disable operations
- CLI description updated to reflect both enable and disable capabilities

## [2026.01.28] - 2026-01-28

Initial release of the Binardat Switch Configuration tool.

### Added
- Python package structure with proper src-layout following modern best practices
- CLI entry point via `binardat-config` command
- Version management system using VERSION file
- Modern Python packaging with `pyproject.toml`
- Selenium-based web automation for switch configuration
- SSH enablement functionality for Binardat switches
- Environment variable configuration support (`SWITCH_IP`, `SWITCH_USERNAME`, `SWITCH_PASSWORD`)
- CLI arguments: `--ip`, `--username`, `--password`, `--version`
- Default credentials support (192.168.2.1, admin/admin)
- Docker container support with Chrome headless browser
- Non-root user security in Docker (switchuser:1000)
- Comprehensive code quality tooling:
  - black (code formatting)
  - isort (import sorting)
  - flake8 (linting)
  - mypy (static type checking)
  - pydocstyle (docstring validation with Google style)
  - pre-commit hooks
- GitHub Actions CI/CD pipeline
  - Linting checks (isort, black, flake8, mypy)
  - Test suite across Python 3.9, 3.10, 3.11, and 3.12
  - Coverage reporting via Codecov

### Documentation
- Comprehensive README with installation and usage instructions
- CLAUDE.md with development guidelines and architecture overview
- Docker quick start guide
- Detailed usage guide
- Troubleshooting guide
- Versioning and release documentation
