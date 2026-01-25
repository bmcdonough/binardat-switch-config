# Dependency Management

This document explains how dependencies are managed in this project.

## Overview

This project uses a **two-tier dependency management system**:

1. **`pyproject.toml`** - Source of truth (human-edited)
2. **`requirements.txt` / `requirements-dev.txt`** - Auto-generated (machine-created)

## Why Two Files?

**pyproject.toml (Modern)**
- Modern Python standard (PEP 621)
- Flexible version constraints (`requests>=2.31.0`)
- Only lists direct dependencies
- Human-friendly and maintainable
- Works with pip, poetry, PDM, and other modern tools

**requirements.txt (Compatibility)**
- Older format, but universally supported
- Exact version pins (`requests==2.32.5`)
- Includes ALL dependencies (direct + transitive)
- Reproducible builds across environments
- Works with legacy tools and CI systems

## The pip-compile Tool

We use `pip-compile` from the `pip-tools` package to bridge these formats:

```bash
pip install pip-tools
```

### What pip-compile Does

1. **Reads** `pyproject.toml` to find direct dependencies
2. **Resolves** the full dependency tree (including transitive dependencies)
3. **Pins** exact versions for every package
4. **Writes** the result to `requirements.txt` with helpful comments

### Example

**Input (pyproject.toml):**
```toml
dependencies = [
    "requests>=2.31.0",
]
```

**Output (requirements.txt):**
```
requests==2.32.5
    # via binardat-switch-config (pyproject.toml)
certifi==2026.1.4
    # via requests
charset-normalizer==3.4.4
    # via requests
urllib3==2.6.3
    # via requests
```

Notice:
- `requests>=2.31.0` became `requests==2.32.5` (exact pin)
- Three transitive dependencies were added automatically
- Comments show the dependency chain

## Workflows

### Adding a New Dependency

```bash
# 1. Edit pyproject.toml
#    Add to [project.dependencies] or [project.optional-dependencies.dev]

# 2. Regenerate requirements files
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# 3. Install the new dependencies
pip install -e ".[dev]"

# 4. Test that everything works
pytest --cov

# 5. Commit all three files
git add pyproject.toml requirements.txt requirements-dev.txt
git commit -m "Add <package-name> dependency"
```

### Updating Dependencies

**Update all dependencies:**
```bash
# Regenerate with latest compatible versions
pip-compile --upgrade pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --upgrade --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras

# Reinstall
pip install -e ".[dev]"

# Test
pytest --cov

# Review and commit if tests pass
git diff requirements.txt requirements-dev.txt
git add requirements.txt requirements-dev.txt
git commit -m "Update dependencies"
```

**Update a specific package:**
```bash
# Update just requests and its dependencies
pip-compile --upgrade-package requests pyproject.toml --output-file=requirements.txt --strip-extras

# Or update the version constraint in pyproject.toml first
# Change: requests>=2.31.0 to requests>=2.32.0
# Then regenerate:
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
```

### During Development

You don't need to regenerate requirements files after every change. Only regenerate when:

1. **Adding/removing a dependency** in `pyproject.toml`
2. **Before a release** (to ensure latest compatible versions)
3. **After updating version constraints** in `pyproject.toml`
4. **When security updates** are needed

For day-to-day development, just work with `pyproject.toml`:
```bash
# This installs from pyproject.toml, not requirements.txt
pip install -e ".[dev]"
```

### Before Every Release

**REQUIRED:** Regenerate requirements files to ensure they're up-to-date:

```bash
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras
git add requirements.txt requirements-dev.txt
git commit -m "Update requirements files for release"
```

See [releases.md](releases.md) for the full release process.

## Installation Methods

### For Development
```bash
# Install from pyproject.toml (editable, with dev dependencies)
pip install -e ".[dev]"
```

### For End Users
```bash
# Option 1: Install from PyPI (when published)
pip install binardat-switch-config

# Option 2: Install from source using pyproject.toml
pip install .

# Option 3: Install from requirements.txt (exact versions)
pip install -r requirements.txt
```

## File Responsibilities

| File | Who Edits | When | Purpose |
|------|-----------|------|---------|
| `pyproject.toml` | Humans | When adding/changing dependencies | Source of truth |
| `requirements.txt` | pip-compile | Before releases, after dependency changes | Reproducible builds |
| `requirements-dev.txt` | pip-compile | Before releases, after dependency changes | Reproducible dev environments |

## Common Questions

### Why not just use requirements.txt?

`requirements.txt` can't specify metadata like:
- Package description
- Author information
- License
- Python version requirements
- Entry points (CLI commands)

Modern tools expect `pyproject.toml`.

### Why not just use pyproject.toml?

Some tools and CI systems don't support `pyproject.toml` yet. Also, `requirements.txt` provides:
- Exact reproducibility (pinned transitive dependencies)
- Faster dependency resolution
- Compatibility with legacy tooling

### Can I edit requirements.txt directly?

**No!** It's auto-generated. Your changes will be overwritten next time `pip-compile` runs.

Always edit `pyproject.toml`, then regenerate:
```bash
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
```

### What is --strip-extras?

The `--strip-extras` flag tells pip-compile to not include extra specifiers in the output. This is becoming the default in pip-tools 8.0.0. It makes the output cleaner and is recommended for most projects.

### How do I see what changed?

After running pip-compile:
```bash
# See what versions changed
git diff requirements.txt

# See a summary
git diff requirements.txt | grep '^[+-][a-z]'
```

## Troubleshooting

### Version conflicts

If pip-compile fails with conflicts:
```
Could not find a version that matches requests>=2.32,<2.31
```

1. Check version constraints in `pyproject.toml`
2. Ensure constraints don't conflict
3. Try upgrading the conflicting package:
   ```bash
   pip-compile --upgrade-package requests pyproject.toml --output-file=requirements.txt --strip-extras
   ```

### Out of sync

If requirements files are out of sync with `pyproject.toml`:
```bash
# Nuclear option: regenerate both files
pip-compile pyproject.toml --output-file=requirements.txt --strip-extras
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.txt --strip-extras
```

### Can't resolve dependencies

If pip-compile can't resolve dependencies, you may have incompatible version constraints:

```bash
# Try upgrading everything
pip-compile --upgrade pyproject.toml --output-file=requirements.txt --strip-extras

# If that fails, check for conflicting constraints in pyproject.toml
# Example problem:
#   package-a>=2.0
#   package-b<2.0  # conflicts with package-a
```

## References

- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Python Packaging User Guide](https://packaging.python.org/)
