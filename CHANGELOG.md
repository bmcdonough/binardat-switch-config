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
- Project documentation (CLAUDE.md, CHANGELOG.md)
- Developer documentation in docs/ directory
  - Merging workflow with issue-first approach (docs/merging.md)
  - Release process with CalVer support (docs/releases.md)
- CI/CD pipeline with GitHub Actions (linting and testing workflows)
- Code quality tooling: black, isort, flake8, mypy
- Pre-commit hooks configuration
- Project configuration via pyproject.toml
- Development dependencies (requirements-dev.txt)
- PEP8 line length (79 characters) enforced across all tools
- Black-compatible flake8 configuration (E203, W503 ignored)
- Test coverage reporting with pytest-cov
- Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
- Version management with bump-my-version
  - CalVer configuration (YYYY.MM.DD format)
  - Support for micro releases (same-day releases)
  - Support for development builds (.devN suffix)
- Package structure with src-layout
  - src/binardat_switch_config/ package directory
  - tests/ directory for test suite
  - __version__ string in package __init__.py

### Commits
- [`1d52005`](https://github.com/bmcdonough/binardat-switch-config/commit/1d52005) - Initial commit

[Unreleased]: https://github.com/bmcdonough/binardat-switch-config/compare/1d52005...HEAD
