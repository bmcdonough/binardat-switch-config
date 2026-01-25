# Release Process

This document describes how to create and publish releases for this project.

## Overview

This project uses **Calendar Versioning (CalVer)** with the format `YYYY.MM.DD[.MICRO][.devN]`:

- **YYYY.MM.DD** - Regular release (e.g., `2026.01.25`)
- **YYYY.MM.DD.1** - Second release on the same day (micro version)
- **YYYY.MM.DD.dev0** - Development/pre-release build

We use [bump-my-version](https://callowayproject.github.io/bump-my-version/) to automate version bumping.

## Setup

### Install bump-my-version

```bash
pip install bump-my-version
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

### 3. Run Tests and Linting

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

### 4. Bump the Version

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

### 5. Review the Changes

```bash
# Check the version was updated
git show HEAD

# Check the tag
git tag -l
```

### 6. Push to GitHub

```bash
# Push commits and tags
git push origin main
git push origin --tags
```

### 7. Create GitHub Release

1. Go to https://github.com/bmcdonough/binardat-switch-config/releases
2. Click **Draft a new release**
3. Select the tag you just pushed
4. **Release title:** Version YYYY.MM.DD[.MICRO]
5. **Description:** Copy the relevant section from CHANGELOG.md
6. Click **Publish release**

### 8. Publish to PyPI (Optional)

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

# 3. Commit changelog
git add CHANGELOG.md
git commit -m "Update CHANGELOG for 2026.01.25 release"

# 4. Run tests
pytest --cov
pre-commit run --all-files

# 5. Bump version (first release of the day)
bump-my-version bump release

# This creates:
# - Updates __version__ in src/binardat_switch_config/__init__.py
# - Updates version in pyproject.toml
# - Git commit: "Bump version: 2026.01.24 → 2026.01.25"
# - Git tag: 2026.01.25

# 6. Push to GitHub
git push origin main
git push origin --tags

# 7. Create GitHub release via web interface
# 8. (Optional) Publish to PyPI
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

## References

- [bump-my-version Documentation](https://callowayproject.github.io/bump-my-version/)
- [CalVer Specification](https://calver.org/)
- [bump-my-version CalVer Guide](https://callowayproject.github.io/bump-my-version/howtos/calver/)
- [Calendar Versioning Reference](https://callowayproject.github.io/bump-my-version/reference/calver_reference/)
