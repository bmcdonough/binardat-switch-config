# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning in the format YYYY.MM.DD.

## [Unreleased]

### Added
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

### Fixed
- CI workflow dependency and configuration issues ([`0b02295`](https://github.com/bmcdonough/binardat-switch-config/commit/0b02295))
  - Fixed bump-my-version version from 0.18.0 (non-existent) to >=0.25.0
  - Updated CI to use modern `pip install -e ".[dev]"` instead of requirements files
  - Fixed coverage path from `--cov=.` to `--cov=src` for src-layout
  - Added pydocstyle check to lint job
  - Scoped linting tools to src/ and tests/ directories only

### Changed
- Updated README from minimal description to comprehensive documentation
- Reorganized .gitignore with trailing whitespace fixes

### Commits
- [`1d52005`](https://github.com/bmcdonough/binardat-switch-config/commit/1d52005) - Initial commit
- [`d6a85f3`](https://github.com/bmcdonough/binardat-switch-config/commit/d6a85f3) - Organize repository into standard Python library structure
- [`0b02295`](https://github.com/bmcdonough/binardat-switch-config/commit/0b02295) - Fix CI workflow and dependency issues

[Unreleased]: https://github.com/bmcdonough/binardat-switch-config/compare/1d52005...HEAD
