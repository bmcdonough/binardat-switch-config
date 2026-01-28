# For Development

```bash
# Clone the repository
git clone https://github.com/bmcdonough/binardat-switch-config.git
cd binardat-switch-config

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

### Running Tests

```bash
pytest                  # Run all tests
pytest --cov           # Run with coverage report
```

### Code Quality

```bash
black .                 # Format code
isort .                 # Sort imports
flake8 .                # Lint code
mypy .                  # Type check
pydocstyle .            # Check docstrings
pre-commit run --all-files  # Run all checks
```

## Project Structure

```
binardat-switch-config/
├── src/
│   └── binardat_switch_config/  # Main package
│       ├── __init__.py           # Package init with version management
│       ├── cli.py                # CLI entry point
│       └── ssh_enabler.py        # Core SSH enabler class
├── tests/                        # Test suite
├── docs/                         # Documentation
├── scripts/
│   └── release.sh                # Release automation script
├── VERSION                       # Current version number
└── pyproject.toml                # Project configuration
```

## Version Management in Code

The package version is stored in `/VERSION` file and read at runtime by `__init__.py`:

```python
from binardat_switch_config import __version__
print(__version__)  # Outputs: 2026.01.28
```

When releasing:
1. Update `/VERSION` file
2. Update `version` in `pyproject.toml` to match
3. Build and test package
4. Create git tag

The CLI also supports showing the version:

```bash
binardat-config --version
```

See [Versioning and Release Process](docker/versioning-and-releases.md) for complete release workflow.

## Creating Releases

This project uses calendar versioning (CalVer): `YYYY.MM.DD[.MICRO]`

### Quick Release Process

For maintainers creating new releases, use the release script:

```bash
# Create a new release
./scripts/release.sh 2026.01.28
```

This will:
1. Validate version format
2. Update the VERSION file
3. Build Docker image with proper labels and tags
4. Display next steps for git tagging and Docker push

### Manual Release Steps

If you need to create a release manually:

1. **Update VERSION file**:
   ```bash
   echo "2026.01.28" > VERSION
   ```

2. **Update pyproject.toml version**:
   ```bash
   # Edit pyproject.toml and update the version field to match VERSION file
   # [project]
   # version = "2026.01.28"
   ```

3. **Update CHANGELOG.md**:
   - Add new version section with changes
   - Document new features, fixes, and breaking changes

4. **Commit changes**:
   ```bash
   git add VERSION pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 2026.01.28"
   ```

5. **Create Git tag**:
   ```bash
   git tag -a v2026.01.28 -m "Release v2026.01.28"
   git push origin main v2026.01.28
   ```

6. **Build and push Docker image**:
   ```bash
   export VERSION="2026.01.28"
   docker build \
     --build-arg VERSION="v$VERSION" \
     --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
     --build-arg VCS_REF="$(git rev-parse HEAD)" \
     -t ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION \
     -t ghcr.io/bmcdonough/binardat-ssh-enabler:latest \
     .

   docker push ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION
   docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest
   ```

7. **Create GitHub release**:
   ```bash
   gh release create v$VERSION --title "Release v$VERSION" --latest
   ```

### Pre-Release Checklist

Before creating a release:

- [ ] All tests passing (`pytest`)
- [ ] Code quality checks pass (`pre-commit run --all-files`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with changes
- [ ] VERSION file updated
- [ ] pyproject.toml version updated to match VERSION file
- [ ] Package installs locally (`pip install -e .`)
- [ ] CLI command works (`binardat-config --version`)
- [ ] Docker image builds successfully
- [ ] Docker image tested on real switch (if possible)

### Version Management

- **VERSION file**: Single source of truth for current version
- **Git tags**: Tagged with `v` prefix (e.g., `v2026.01.28`)
- **Docker tags**: Multiple tags per release:
  - Specific: `v2026.01.28`
  - Month alias: `2026.01`
  - Year alias: `2026`
  - Latest: `latest`

### Hotfix Releases

For critical bugfixes:

```bash
# Create hotfix version (add micro version)
./scripts/release.sh 2026.01.28.1

# Follow same process as regular release
```

For complete release documentation, see [Versioning and Release Process](docker/versioning-and-releases.md).
