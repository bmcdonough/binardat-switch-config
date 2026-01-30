# Changelog

All notable changes to the Binardat Switch Configuration tool are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **Pre-commit hooks** (`.pre-commit-config.yaml`) with 8 automated quality checks:
  - `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`
  - `check-json`, `check-toml`, `check-merge-conflict`, `debug-statements`
  - `isort`, `black`, `flake8`, `pydocstyle`, `mypy`
- **GitHub Actions CI/CD workflow** (`.github/workflows/ci.yml`):
  - Lint job: runs isort, black, flake8, mypy, pydocstyle on Python 3.11
  - Test job: runs pytest with coverage across Python 3.9, 3.10, 3.11, 3.12
  - Codecov integration for coverage reporting
  - Triggers on push/PR to main and develop branches
- **Tool configurations** in `pyproject.toml`:
  - `[tool.flake8]`: Line length 79, black-compatible ignore rules (E203, W503)
  - `[tool.coverage.run]` and `[tool.coverage.report]`: Coverage tracking configuration
  - `[tool.mypy]`: Stricter type checking with 11 additional rules
  - `[[tool.mypy.overrides]]`: Relaxed rules for test files
  - `[tool.pytest.ini_options]`: Enhanced test discovery patterns
- **Type marker file** (`src/binardat_switch_config/py.typed`) for PEP 561 compliance
- **Placeholder test** (`tests/test_placeholder.py`) to prevent pytest "no tests collected" failure

### Changed
- **Code formatting**: Applied isort and black formatting across entire codebase
- **Dev dependencies** upgraded to tested versions:
  - `pytest>=7.4.4` (was >=7.4.0)
  - `black>=24.8.0,<25.0.0` (was >=23.7.0) - pinned for Python 3.9 compatibility
  - `isort>=5.13.0` (was >=5.12.0)
  - `flake8>=7.0.0` (was >=6.1.0)
  - `mypy>=1.8.0` (was >=1.4.0)
  - `pre-commit>=3.6.0` (was >=3.3.0)
- **Black configuration**: Updated to support Python 3.9-3.12 (`target-version`), added `include` pattern
- **isort configuration**: Enhanced with `multi_line_output`, `include_trailing_comma`, and 4 additional settings
- **mypy configuration**: Added 8 stricter type checking rules (`disallow_incomplete_defs`, `check_untyped_defs`, `no_implicit_optional`, `warn_redundant_casts`, `warn_unused_ignores`, `warn_no_return`, `strict_equality`, plus test file overrides)
- **pytest configuration**: Added `python_classes`, `python_functions`, `--strict-config`, `--showlocals`
- **pydocstyle configuration**: Added `match` and `match-dir` patterns to exclude test files

### Fixed
- **All flake8 errors (21 total)**:
  - Line length violations (E501): Wrapped 14 long lines to fit 79 character limit
  - Unused imports (F401): Removed unused `WebDriverException` import
  - f-strings without placeholders (F541): Converted 6 f-strings to regular strings
  - Ambiguous variable name (E741): Renamed `l` → `link`
  - Bare except clause (E722): Changed `except:` → `except Exception:`
  - Unused local variables (F841): Removed `wait` and `found_selector`
- **All mypy errors (17 total)**:
  - Missing function type annotations: Added return types to `signal_handler()`, `main()`, `load_config_from_env()`
  - Optional attribute access: Added `assert self.driver is not None` in 4 methods
  - Lambda type inference: Replaced lambda with typed `check_main_page_loaded()` helper function
- **CI/CD workflow failures**:
  - Black version mismatch: Pre-commit used 24.1.1, CI installed 26.x → standardized on 24.10.0
  - Python 3.9 compatibility: Black 25.12.0+ requires Python 3.10+ → downgraded to 24.x series
  - Pytest "no tests collected": Added placeholder test file
  - Black formatting inconsistency: Applied black 24.10.0 formatting consistently
- **Code quality**: All code now passes pre-commit hooks and CI/CD checks without errors

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
