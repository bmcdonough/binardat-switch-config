# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning in the format `YYYY.MM.DD`.

## [Unreleased]

### Added
- Pulled latest changes from develop branch

## [2026.01.26] - 2026-01-26

### Added - Phase 1: Core Backup (MVP)

This release implements the complete Phase 1 functionality for the netmiko-based
switch configuration management system.

#### Core Infrastructure
- **pyproject.toml**: Complete project configuration with all dependencies
  - Python 3.9+ support
  - Click for CLI framework
  - Netmiko for SSH connection management
  - GitPython for version control
  - PyYAML for inventory management
  - Development dependencies: black, isort, flake8, mypy, pydocstyle, pytest
- **exceptions.py**: Custom exception classes for error handling
  - `BinardatSwitchConfigError`: Base exception class
  - `ConnectionError`: Connection-related errors
  - `RetrievalError`: Configuration retrieval errors
  - `StorageError`: Storage operation errors
  - `GitError`: Git operation errors
  - `InventoryError`: Inventory file errors

#### Netmiko Integration (`src/binardat_switch_config/netmiko/`)
- **connection.py**: `SwitchConnection` class with SSH connection management
  - Support for password and SSH key authentication
  - Automatic retry logic with exponential backoff (3 retries, 2s initial delay)
  - Context manager for automatic resource cleanup
  - Connection state validation
- **retrieval.py**: Configuration retrieval and normalization
  - `ConfigRetriever`: Retrieve running-config and startup-config from switches
  - `ConfigNormalizer`: Normalize configs by removing timestamps and dynamic content
  - Device-specific normalization for multiple vendors
- **device_profiles.py**: Device-specific command mappings
  - Support for Cisco IOS/IOS-XE, Arista EOS, Juniper JunOS, HP Comware, and more
  - Vendor-specific command templates for config retrieval

#### Storage Layer (`src/binardat_switch_config/storage/`)
- **filesystem.py**: `ConfigStorage` class for file operations
  - Save/load configurations to filesystem in organized directory structure
  - Metadata management (timestamps, device info, change detection)
  - Automatic directory creation and validation
- **git_manager.py**: `GitManager` class for version control
  - Initialize git repositories with proper configuration
  - Add, commit, and push changes with descriptive messages
  - Retrieve files from specific commits
  - List commit history with filtering options
  - Remote repository support (push to origin)

#### CLI Interface (`src/binardat_switch_config/cli/`)
- **main.py**: Main CLI entry point using Click framework
  - Global options: `--verbose`, `--quiet`, `--config-repo`
  - `init` command: Initialize new configuration repository
  - `validate-inventory` command: Validate inventory.yaml structure
- **backup.py**: Backup command implementation
  - Single switch backup: `binardat-config backup <hostname>`
  - Multi-switch batch backup: `binardat-config backup --all`
  - Tag-based filtering: `binardat-config backup --all --tags production,core`
  - Dry-run mode: `binardat-config backup --dry-run`
  - Environment variable substitution for credentials
  - Automatic change detection (only commits when config actually changes)
  - Progress indicators and detailed logging

#### Documentation
- **README.md**: Comprehensive documentation including:
  - Installation instructions
  - Quick start guide
  - Usage examples for all commands
  - Inventory file format and examples
  - Configuration options
  - Credential management
  - Project structure overview
  - Development setup instructions
- **CLAUDE.md**: Development guide for AI assistance
  - Project structure and architecture
  - Development environment setup
  - Code quality standards
  - Docstring requirements (Google style)
  - CI/CD pipeline information

#### CI/CD
- **.github/workflows/ci.yml**: GitHub Actions workflow
  - Linting job: isort, black, flake8, mypy
  - Testing job: pytest across Python 3.9, 3.10, 3.11, 3.12
  - Coverage reporting to Codecov
- **.pre-commit-config.yaml**: Pre-commit hooks for code quality
  - black (79 character line length)
  - isort (black-compatible profile)
  - flake8 (PEP8 compliance)
  - mypy (strict type checking)
  - pydocstyle (Google-style docstrings)

#### Configuration Files
- **.mypy.ini**: MyPy strict type checking configuration
- **pyproject.toml**: Centralized configuration for all tools
  - black, isort, flake8, mypy, pydocstyle, pytest settings
  - Consistent 79 character line length (PEP8)
  - Google-style docstring convention

### Features

- ✅ SSH connection to network switches using netmiko
- ✅ Configuration retrieval (running-config, startup-config)
- ✅ Configuration normalization (removes timestamps, uptime, dynamic content)
- ✅ Change detection (only commits when config actually changes)
- ✅ Git version control with automatic commits
- ✅ Push to remote git repository
- ✅ Support for multiple vendors (Cisco, Arista, Juniper, HP, etc.)
- ✅ Multi-switch batch backups with tag filtering
- ✅ CLI interface with comprehensive commands
- ✅ Error handling with retries and graceful failures
- ✅ Environment variable support for credentials
- ✅ Dry-run mode for testing without making changes

### Developer Experience

- Modern src-layout package structure
- Comprehensive type hints with strict mypy checking
- Google-style docstrings on all public APIs
- Pre-commit hooks for code quality
- CI/CD pipeline with multi-version Python testing
- Clear separation of concerns (connection, retrieval, storage, CLI)

## [1.0.0] - 2026-01-20

### Added
- Initial commit
- Project repository created

---

## Roadmap

### Phase 2: Advanced Change Detection
- Detailed diff reports showing exactly what changed
- Change categorization (VLANs, interfaces, routing, etc.)
- Notifications on specific types of changes

### Phase 3: Enhanced Inventory Management
- Dynamic inventory from external sources
- Inventory validation and health checks
- Device discovery and auto-registration

### Phase 4: Rollback Capability
- Restore configurations from git history
- Dry-run rollback testing
- Rollback scheduling and automation

### Phase 5: Production Hardening
- Comprehensive test suite with high coverage
- Integration tests with mock switches
- Security hardening (secret management, audit logging)
- Performance optimization for large deployments
- Documentation and deployment guides
