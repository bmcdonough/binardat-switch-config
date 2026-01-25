# Release Process

This document describes how to create and publish releases for this project.

## Overview

This project uses **Calendar Versioning (CalVer)** with the format `YYYY.MM.DD[.MICRO][.devN]`:

- **YYYY.MM.DD** - Regular release (e.g., `2026.01.25`)
- **YYYY.MM.DD.1** - Second release on the same day (micro version)
- **YYYY.MM.DD.dev0** - Development/pre-release build

We use [bump-my-version](https://callowayproject.github.io/bump-my-version/) to automate version bumping.

## Setup

### Install Required Tools

```bash
# Install bump-my-version for version management
pip install bump-my-version

# Install pip-tools for requirements file generation
pip install pip-tools
```

### Configuration

The CalVer configuration is in `pyproject.toml`:

```toml
[tool.bumpversion]
current_version = "2026.01.25"
parse = """(?x)
    (?P<release>
        (?:[1-9][0-9]{3})\\.
        (?:1[0-2]|0?[1-9])\\.
        (?:3[0-1]|[1-2][0-9]|0?[1-9])
    )
    (?:\\.(?P<micro>\\d+))?
    (?:\\.(?P<dev>dev\\d+))?
"""
serialize = [
    "{release}.{micro}.{dev}",
    "{release}.{micro}",
    "{release}.{dev}",
    "{release}"
]

[tool.bumpversion.parts.release]
calver_format = "{YYYY}.{MM}.{DD}"

[tool.bumpversion.parts.micro]
first_value = "1"

[tool.bumpversion.parts.dev]
first_value = "dev0"
independent = false

[[tool.bumpversion.files]]
filename = "src/binardat_switch_config/__init__.py"
search = "__version__ = \"{current_version}\""
replace = "__version__ = \"{new_version}\""

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = "version = \"{current_version}\""
replace = "version = \"{new_version}\""
```

## Release Types

### 1. Regular Release (Date-based)

**When to use:** First release of the day

**Command:**
```bash
bump-my-version bump release
```

**Result:**
- If today is different from the current version date, creates a new `YYYY.MM.DD` version
- If today matches the current version date, no change (use micro instead)

### 2. Multiple Releases Same Day (Micro)

**When to use:** Second, third, etc. release on the same day

**Command:**
```bash
bump-my-version bump micro
```

**Result:**
- `2026.01.25` → `2026.01.25.1` (first micro release)
- `2026.01.25.1` → `2026.01.25.2` (second micro release)

### 3. Development Build (Pre-release)

**When to use:** Testing, CI builds, or work-in-progress versions

**Command:**
```bash
bump-my-version bump dev
```

**Result:**
- `2026.01.25` → `2026.01.25.dev0`
- `2026.01.25.dev0` → `2026.01.25.dev1`

To create a dev version of the next date:
```bash
bump-my-version bump release --new-version="2026.01.26.dev0"
```

## Step-by-Step Release Process

### 1. Ensure Clean Working Directory

```bash
git status
# Should show no uncommitted changes
```

### 2. Update CHANGELOG.md

Move items from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

## [2026.01.25] - 2026-01-25

### Added
- Feature A
- Feature B

### Fixed
- Bug fix C

### Commits
- [`abc1234`](https://github.com/bmcdonough/binardat-switch-config/commit/abc1234) - Add feature A
- [`def5678`](https://github.com/bmcdonough/binardat-switch-config/commit/def5678) - Add feature B
- [`ghi9012`](https://github.com/bmcdonough/binardat-switch-config/commit/ghi9012) - Fix bug C
```

Update the comparison link at the bottom:
```markdown
[Unreleased]: https://github.com/bmcdonough/binardat-switch-config/compare/abc1234...HEAD
[2026.01.25]: https://github.com/bmcdonough/binardat-switch-config/commit/abc1234
```

### 3. Generate Updated Requirements Files

**Important:** `pyproject.toml` is the source of truth for dependencies. The `requirements.txt` and `requirements-dev.txt` files must be regenerated before each release using `pip-compile`.

```bash
# Install pip-tools if not already installed
pip install pip-tools

# Generate requirements.txt from pyproject.toml
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras

# Generate requirements-dev.txt from pyproject.toml (includes dev dependencies)
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# Commit the updated requirements files
git add requirements.txt requirements-dev.txt
git commit -m "Update requirements files for release"
```

**What pip-compile does:**
- **Resolves the full dependency tree** - Finds all transitive dependencies (dependencies of dependencies)
- **Pins exact versions** - Converts `requests>=2.31.0` to `requests==2.32.5` for reproducibility
- **Documents the tree** - Adds comments showing which package requires each dependency
- **Auto-generates header** - Shows the exact command used to create the file

**Example output:**
```
beautifulsoup4==4.14.3      # Direct dependency from pyproject.toml
certifi==2026.1.4           # Transitive dependency (required by requests)
requests==2.32.5            # Direct dependency from pyproject.toml
urllib3==2.6.3              # Transitive dependency (required by requests)
```

**Why this is necessary:**
- `pyproject.toml` contains abstract specifications (e.g., `requests>=2.31.0`)
- `requirements.txt` contains exact pins for **reproducible builds**
- Ensures all developers and CI use identical dependency versions
- Makes it easy to audit security vulnerabilities in specific versions
- Provides compatibility with tools that don't support `pyproject.toml`

### 4. Run Tests and Linting

```bash
# Run all quality checks
black .
isort .
flake8 .
mypy .
pydocstyle .
pytest --cov

# Or use pre-commit
pre-commit run --all-files
```

### 5. Bump the Version

For a regular release:
```bash
bump-my-version bump release
```

For a same-day release:
```bash
bump-my-version bump micro
```

This will:
- Update `src/binardat_switch_config/__init__.py`
- Update `pyproject.toml`
- Create a git commit
- Create a git tag

### 6. Review the Changes

```bash
# Check the version was updated
git show HEAD

# Check the tag
git tag -l
```

### 7. Push to GitHub

```bash
# Push commits and tags
git push origin main
git push origin --tags
```

### 8. Create GitHub Release

1. Go to https://github.com/bmcdonough/binardat-switch-config/releases
2. Click **Draft a new release**
3. Select the tag you just pushed
4. **Release title:** Version YYYY.MM.DD[.MICRO]
5. **Description:** Copy the relevant section from CHANGELOG.md
6. Click **Publish release**

### 9. Publish to PyPI (Optional)

If you want to publish to PyPI:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution
twine check dist/*

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Quick Example

Here's a complete release workflow:

```bash
# 1. Clean working directory
git status  # Should be clean

# 2. Update CHANGELOG.md manually
# ... edit CHANGELOG.md ...

# 3. Generate updated requirements files
pip install pip-tools
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras
git add requirements.txt requirements-dev.txt
git commit -m "Update requirements files for release"

# 4. Commit changelog
git add CHANGELOG.md
git commit -m "Update CHANGELOG for 2026.01.25 release"

# 5. Run tests
pytest --cov
pre-commit run --all-files

# 6. Bump version (first release of the day)
bump-my-version bump release

# This creates:
# - Updates __version__ in src/binardat_switch_config/__init__.py
# - Updates version in pyproject.toml
# - Git commit: "Bump version: 2026.01.24 → 2026.01.25"
# - Git tag: 2026.01.25

# 7. Push to GitHub
git push origin main
git push origin --tags

# 8. Create GitHub release via web interface
# 9. (Optional) Publish to PyPI
python -m build
twine upload dist/*
```

## Handling Multiple Releases in One Day

**Scenario:** You released `2026.01.25` but need to release a hotfix later the same day.

```bash
# First release of the day
bump-my-version bump release
# Result: 2026.01.25

# ... later that day, hotfix needed ...

# Second release of the day
bump-my-version bump micro
# Result: 2026.01.25.1

# Third release if needed
bump-my-version bump micro
# Result: 2026.01.25.2
```

**CHANGELOG.md format:**
```markdown
## [2026.01.25.2] - 2026-01-25

### Fixed
- Critical security fix

### Commits
- [`xyz7890`](https://github.com/bmcdonough/binardat-switch-config/commit/xyz7890) - Fix security issue

## [2026.01.25.1] - 2026-01-25

### Fixed
- Hotfix for connection timeout

### Commits
- [`mno3456`](https://github.com/bmcdonough/binardat-switch-config/commit/mno3456) - Fix timeout

## [2026.01.25] - 2026-01-25

### Added
- Initial release

### Commits
- [`abc1234`](https://github.com/bmcdonough/binardat-switch-config/commit/abc1234) - Add features
```

## Managing Dependencies

### Adding a New Dependency

When adding a new runtime or development dependency:

```bash
# 1. Edit pyproject.toml and add the dependency
# For runtime: add to [project.dependencies]
# For dev: add to [project.optional-dependencies.dev]

# 2. Regenerate the requirements files
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# 3. Install the new dependencies
pip install -e ".[dev]"

# 4. Commit all changes together
git add pyproject.toml requirements.txt requirements-dev.txt
git commit -m "Add <package-name> dependency"
```

### Updating Dependencies

To get security updates or new features:

```bash
# Update all dependencies to latest compatible versions
pip-compile --upgrade pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --upgrade --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# Update a specific package only
pip-compile --upgrade-package requests pyproject.toml --output-file=requirements.txt --strip-extras

# Review changes
git diff requirements.txt requirements-dev.txt

# Reinstall to get new versions
pip install -e ".[dev]"

# Run tests to ensure compatibility
pytest --cov

# Commit if all tests pass
git add requirements.txt requirements-dev.txt
git commit -m "Update dependencies"
```

### Understanding the Files

**pyproject.toml** - Source of truth
```toml
dependencies = [
    "requests>=2.31.0",  # Accept any version >= 2.31.0
]
```

**requirements.txt** - Auto-generated pinned versions
```
requests==2.32.5          # Exact version pip-compile resolved
certifi==2026.1.4         # Transitive dependency (required by requests)
charset-normalizer==3.4.4 # Transitive dependency (required by requests)
urllib3==2.6.3            # Transitive dependency (required by requests)
```

**Key differences:**
- `pyproject.toml`: Lists only direct dependencies with flexible version constraints
- `requirements.txt`: Lists ALL dependencies (direct + transitive) with exact versions
- `pyproject.toml`: Human-edited
- `requirements.txt`: Auto-generated by pip-compile, never hand-edited

## Development Builds

Development builds are useful for testing unreleased changes:

```bash
# Create a dev build
bump-my-version bump dev
# 2026.01.25 → 2026.01.25.dev0

# Increment dev version
bump-my-version bump dev
# 2026.01.25.dev0 → 2026.01.25.dev1

# When ready for release, bump to next regular version
bump-my-version bump release
# 2026.01.25.dev1 → 2026.01.26 (if it's a new day)
```

**Note:** Development versions should not be pushed to PyPI. Use Test PyPI for testing:
```bash
twine upload --repository testpypi dist/*
```

## Troubleshooting

### Wrong version bumped

```bash
# Undo the last commit and tag
git reset --hard HEAD~1
git tag -d <tag-name>

# Try again with correct bump command
```

### Version out of sync

```bash
# Check current version in all files
grep -r "2026.01.25" src/ pyproject.toml

# Manually fix if needed, then:
bump-my-version bump --current-version 2026.01.25 release
```

### Need to skip CI

```bash
# Bump version without triggering CI
bump-my-version bump release --commit-args="[skip ci]"
```

### Requirements files out of sync

If `requirements.txt` or `requirements-dev.txt` are out of sync with `pyproject.toml`:

```bash
# Regenerate from pyproject.toml (source of truth)
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# Commit the updates
git add requirements.txt requirements-dev.txt
git commit -m "Sync requirements files with pyproject.toml"
```

**Remember:** Always edit dependencies in `pyproject.toml` first, then regenerate the requirements files. Never edit `requirements.txt` or `requirements-dev.txt` directly - they are auto-generated.

### Updating a specific dependency

If you need to update a specific dependency to get a newer version:

```bash
# Option 1: Update the constraint in pyproject.toml, then regenerate
# Edit pyproject.toml: change requests>=2.31.0 to requests>=2.32.0
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras

# Option 2: Use pip-compile's upgrade flag for a specific package
pip-compile --upgrade-package requests pyproject.toml --output-file=requirements.txt --strip-extras

# Option 3: Upgrade all packages to latest compatible versions
pip-compile --upgrade pyproject.toml --output-file=requirements.txt --strip-extras
```

## References

- [bump-my-version Documentation](https://callowayproject.github.io/bump-my-version/)
- [CalVer Specification](https://calver.org/)
- [bump-my-version CalVer Guide](https://callowayproject.github.io/bump-my-version/howtos/calver/)
- [Calendar Versioning Reference](https://callowayproject.github.io/bump-my-version/reference/calver_reference/)
- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
