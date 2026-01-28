# Docker Versioning and Release Process

## Table of Contents
1. [Versioning Strategy](#versioning-strategy)
2. [Version Management](#version-management)
3. [Docker Image Tagging Strategy](#docker-image-tagging-strategy)
4. [Release Process](#release-process)
5. [CI/CD Automation (Future)](#cicd-automation-future)
6. [Rollback Procedures](#rollback-procedures)
7. [FAQ](#faq)
8. [Appendix A: Quick Reference Commands](#appendix-a-quick-reference-commands)
9. [Appendix B: Version History Template](#appendix-b-version-history-template)

## Versioning Strategy

### Chosen Versioning Scheme: Calendar Versioning (CalVer)

**Format**: `YYYY.MM.DD[.MICRO]`

**Examples**:
- `2026.01.28` - Release on January 28, 2026
- `2026.01.28.1` - Second release on same day
- `2026.02.15` - Release on February 15, 2026

**Rationale**:
- **Clarity**: Users immediately know when image was released
- **Simplicity**: No semantic meaning to decode (major/minor/patch)
- **Use case alignment**: This is a utility tool, not a library with API contracts
- **Industry precedent**: Ubuntu, certbot, pip, and many utilities use CalVer

### Version Semantics

- **Date component** (YYYY.MM.DD): Release date
- **Micro component** (optional): Multiple releases on same day
  - First release of day: No micro component (e.g., 2026.01.28)
  - Subsequent releases: Add .1, .2, etc. (e.g., 2026.01.28.1)

### When to Create New Versions

**New Release (YYYY.MM.DD)**:
- New features added
- Bug fixes
- Security updates
- Dependency updates
- Documentation improvements (if they affect user experience)

**Same-Day Update (YYYY.MM.DD.MICRO)**:
- Critical hotfixes
- Broken release fix
- Emergency security patch
- Build failures requiring rebuild

**No New Release**:
- README-only changes
- Non-code documentation updates (typos, clarifications)
- CI/CD workflow changes (unless affecting output)
- Internal refactoring with no functional changes

### Pre-release Versions

**Format**: `YYYY.MM.DD-rc.N` or `YYYY.MM.DD-beta.N` or `YYYY.MM.DD-dev`

**Examples**:
- `2026.01.28-rc.1` - Release candidate 1
- `2026.01.28-beta.2` - Beta version 2
- `2026.01.28-dev` - Development build

**Use cases**:
- Testing new features before production release
- User acceptance testing
- Breaking change validation
- Feature previews

## Version Management

### Version Storage Locations

Version numbers MUST be stored in multiple locations for consistency:

1. **Git tags** - Source of truth for releases
2. **VERSION file** - Single source of truth for current version
3. **Docker image labels** - For introspection and metadata
4. **README.md** - For documentation visibility
5. **CHANGELOG.md** - Historical record of all releases

### VERSION File Format

**Location**: `/VERSION` (repository root)

**Content**:
```
2026.01.28
```

**Requirements**:
- Plain text file
- Single line containing version number
- No 'v' prefix
- No leading/trailing whitespace
- UTF-8 encoding
- MUST match Git tag (minus 'v' prefix)

### Git Tagging Strategy

**Tag Format**: `v{VERSION}`

**Examples**:
- `v2026.01.28` - Production release
- `v2026.01.28.1` - Hotfix release
- `v2026.01.28-rc.1` - Release candidate

**Tag Requirements**:
- Use annotated tags (not lightweight)
- Include release notes in tag message
- Sign tags with GPG (optional but recommended)
- Push tags explicitly (not included in normal push)

**Creating annotated tags**:

```bash
# Create annotated tag with message
git tag -a v2026.01.28 -m "Release 2026.01.28

- Enable SSH via web interface
- Docker image optimization
- Documentation improvements
"

# Create signed tag (recommended)
git tag -s v2026.01.28 -m "Release 2026.01.28"

# Push tag to remote (required)
git push origin v2026.01.28
```

### Branch Strategy

**Main branches**:
- `main` - Production-ready code, source for tagged releases
- `develop` - Integration branch for features (optional)
- `feature/*` - Feature development branches
- `hotfix/*` - Emergency fixes for production

**Release workflow**:
1. Develop features on `feature/*` branches
2. Merge features into `develop` (or directly to `main`)
3. When ready to release, ensure `main` has all changes
4. Tag `main` with release version
5. Build and push Docker images from tagged commit
6. Merge any release changes back to `develop`

## Docker Image Tagging Strategy

### Tag Types

Each release creates MULTIPLE Docker image tags:

1. **Specific version tag** - `v2026.01.28`, `v2026.01.28.1`
2. **Date aliases** - `2026.01`, `2026`
3. **latest tag** - `latest`
4. **Pre-release tags** - `rc`, `beta`, `dev`

### Tag Examples

**For release v2026.01.28**:

```bash
ghcr.io/bmcdonough/binardat-ssh-enabler:v2026.01.28   # Specific version
ghcr.io/bmcdonough/binardat-ssh-enabler:2026.01       # Month alias
ghcr.io/bmcdonough/binardat-ssh-enabler:2026          # Year alias
ghcr.io/bmcdonough/binardat-ssh-enabler:latest        # Latest stable
```

**For pre-release v2026.01.28-rc.1**:

```bash
ghcr.io/bmcdonough/binardat-ssh-enabler:v2026.01.28-rc.1  # Specific RC
ghcr.io/bmcdonough/binardat-ssh-enabler:rc                # Latest RC
```

### Tag Stability Guarantees

| Tag Type | Stability | Use Case |
|----------|-----------|----------|
| `vYYYY.MM.DD` | Immutable | Pin to specific release for production |
| `YYYY.MM` | Updated monthly | Track monthly releases automatically |
| `YYYY` | Updated yearly | Track yearly releases |
| `latest` | Updated on each release | Always get newest stable version |
| `rc` | Pre-release | Test before production deployment |
| `dev` | Unstable | Development and testing only |

### Tag Usage Recommendations

**Production**: Always pin to specific version
```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:v2026.01.28
```

**Development/Testing**: Use latest or dev
```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

**Continuous updates**: Use month alias (updates automatically each month)
```bash
docker run --network host ghcr.io/bmcdonough/binardat-ssh-enabler:2026.01
```

## Release Process

### Pre-Release Checklist

Before creating a release, complete ALL items:

- [ ] All tests passing locally
- [ ] Code review completed (if applicable)
- [ ] Documentation updated (README, usage docs, etc.)
- [ ] CHANGELOG.md updated with changes
- [ ] VERSION file updated
- [ ] No uncommitted changes (`git status` clean)
- [ ] On correct branch (`main`)
- [ ] Remote repository up to date (`git pull`)

### Manual Release Process (Step-by-Step)

#### Step 1: Prepare Release

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Set version for this release
export VERSION="2026.01.28"

# Verify no uncommitted changes
git status
```

#### Step 2: Update VERSION File

```bash
# Update VERSION file
echo "$VERSION" > VERSION

# Commit version bump
git add VERSION
git commit -m "Bump version to $VERSION"
```

#### Step 3: Update CHANGELOG

Edit `CHANGELOG.md`:

```markdown
## [2026.01.28] - 2026-01-28

### Added
- New feature X
- Support for Y

### Fixed
- Bug in SSH enablement
- Documentation typos

### Changed
- Improved error handling
- Updated dependencies
```

Commit changes:

```bash
git add CHANGELOG.md
git commit -m "Update CHANGELOG for v$VERSION"
```

#### Step 4: Create Git Tag

```bash
# Create annotated tag with release notes
git tag -a v$VERSION -m "Release v$VERSION

$(git log --pretty=format:'- %s' --since='1 week ago' HEAD)
"

# Push commits and tag
git push origin main
git push origin v$VERSION
```

#### Step 5: Build Docker Image

```bash
# Build image with version information and multiple tags
docker build \
  --build-arg VERSION="v$VERSION" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse HEAD)" \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:latest \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:$(echo $VERSION | cut -d. -f1-2) \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:$(echo $VERSION | cut -d. -f1) \
  .
```

#### Step 6: Test Docker Image

```bash
# Test with default settings (use a test switch or dry-run mode)
docker run --rm --network host ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION

# Verify version labels
docker inspect ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION | \
  jq '.[0].Config.Labels'
```

#### Step 7: Push Docker Image

```bash
# Login to GitHub Container Registry (if not already logged in)
# Create token at: https://github.com/settings/tokens
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Push all tags
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:$(echo $VERSION | cut -d. -f1-2)
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:$(echo $VERSION | cut -d. -f1)
```

#### Step 8: Create GitHub Release

```bash
# Using gh CLI (install: https://cli.github.com/)
gh release create v$VERSION \
  --title "Release v$VERSION" \
  --notes "$(git tag -l --format='%(contents)' v$VERSION)" \
  --latest

# Or create release manually via GitHub web interface:
# https://github.com/bmcdonough/binardat-switch-config/releases/new
```

#### Step 9: Announce Release

- Update README.md if needed with latest version reference
- Post announcement in project discussions/forums
- Notify users via appropriate channels

### Hotfix Process (Emergency Releases)

For critical bugs in production:

```bash
# Start from main branch
git checkout main
git pull origin main

# Set hotfix version (increment micro version)
export VERSION="2026.01.28.1"

# Create hotfix branch (optional, for complex fixes)
git checkout -b hotfix/v$VERSION

# Make fixes and commit changes
# ... fix the bug ...
git add .
git commit -m "Fix critical issue in SSH enablement"

# Update VERSION and CHANGELOG
echo "$VERSION" > VERSION
# Edit CHANGELOG.md to add hotfix entry
git add VERSION CHANGELOG.md
git commit -m "Bump version to $VERSION (hotfix)"

# Merge to main (if using hotfix branch)
git checkout main
git merge --no-ff hotfix/v$VERSION

# Create tag
git tag -a v$VERSION -m "Hotfix v$VERSION - Critical bugfix"

# Push to remote
git push origin main
git push origin v$VERSION

# Build and push Docker image (same as Steps 5-7)
docker build \
  --build-arg VERSION="v$VERSION" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse HEAD)" \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION \
  --tag ghcr.io/bmcdonough/binardat-ssh-enabler:latest \
  .

docker push ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest

# Create GitHub release
gh release create v$VERSION \
  --title "Hotfix v$VERSION" \
  --notes "Critical bug fix" \
  --latest

# Clean up (if using hotfix branch)
git branch -d hotfix/v$VERSION
```

## CI/CD Automation (Future)

### Recommended GitHub Actions Workflow

Future implementation should include automated releases via GitHub Actions.

**Trigger**: When Git tag matching `v*` is pushed

**Actions**:
1. Checkout code at tag
2. Extract version from tag
3. Build Docker image with multi-arch support (amd64, arm64)
4. Tag image with version, latest, and date aliases
5. Push to GitHub Container Registry
6. Create GitHub Release with auto-generated notes
7. Send notification (optional)

**Benefits**:
- Consistent builds
- No manual Docker commands
- Multi-architecture support (amd64, arm64, arm/v7)
- Automatic release notes
- Faster release cycle
- Reduced human error

**Implementation**: See `.github/workflows/release.yml` (to be created in future phase)

## Rollback Procedures

### Scenario: New release has critical bug, need to revert users

#### Option 1: Re-tag Previous Version as Latest

```bash
# Identify last good version
export GOOD_VERSION="2026.01.27"

# Pull previous version
docker pull ghcr.io/bmcdonough/binardat-ssh-enabler:v$GOOD_VERSION

# Re-tag as latest
docker tag ghcr.io/bmcdonough/binardat-ssh-enabler:v$GOOD_VERSION \
  ghcr.io/bmcdonough/binardat-ssh-enabler:latest

# Push updated latest tag
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

**Note**: This doesn't remove the bad version, but prevents new users from getting it via `latest` tag.

#### Option 2: Delete Bad Tag and Create Hotfix

```bash
# Delete bad Git tag locally and remotely
export BAD_VERSION="2026.01.28"
git tag -d v$BAD_VERSION
git push origin :refs/tags/v$BAD_VERSION

# Delete bad Docker image tags (requires GitHub package admin access)
# Via GitHub UI: Packages → binardat-ssh-enabler → Select version → Delete

# Create hotfix release with fixes
export HOTFIX_VERSION="2026.01.28.1"
# ... follow hotfix process above ...
```

### Communicating Rollbacks

When rolling back:
1. Create GitHub issue documenting the problem and rollback
2. Post announcement in Releases section
3. Update README.md with warning if needed
4. Fast-track hotfix release
5. Update CHANGELOG.md with rollback entry

## FAQ

### Q: Why CalVer instead of SemVer?

**A**: This is a utility tool, not a library. Users care about "when was this released?" more than "is this API-compatible?". CalVer provides immediate chronological context. SemVer is designed for libraries with API contracts - major/minor/patch indicates breaking changes, new features, and bugfixes. For a standalone Docker image that enables SSH, CalVer is more appropriate and user-friendly.

### Q: Can I use both CalVer and SemVer?

**A**: Not recommended. Mixing versioning schemes creates confusion. Choose one and stick with it consistently. This project has chosen CalVer.

### Q: What if I need multiple releases in one day?

**A**: Use the micro component:
- First release: `2026.01.28`
- Second release: `2026.01.28.1`
- Third release: `2026.01.28.2`

### Q: Should I always use `latest` tag in production?

**A**: **NO**. Always pin to a specific version for production: `v2026.01.28`. The `latest` tag can change at any time, which may introduce breaking changes or bugs. Use `latest` only for development and testing.

### Q: How long are old versions supported?

**A**: No formal support policy currently. Users should upgrade to the latest version for bug fixes and security updates. If needed, old versions remain available via specific tags indefinitely.

### Q: Can I delete old Docker image tags?

**A**: Yes, but **NOT recommended**. Storage is cheap, and users may depend on specific versions. Only delete truly broken releases that should never be used.

### Q: What about ARM64/multi-architecture support?

**A**: Currently only AMD64 (x86_64) is built. Multi-architecture support (arm64, arm/v7) is planned for the CI/CD automation phase using Docker buildx.

### Q: How do I check which version I'm running?

**A**: Inspect the Docker image labels:

```bash
docker inspect ghcr.io/bmcdonough/binardat-ssh-enabler:latest | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.version"'
```

### Q: What's the difference between `v2026.01.28` and `2026.01` tags?

**A**:
- `v2026.01.28` - Immutable, always points to the same image
- `2026.01` - Mutable, updates to the latest release in January 2026

Use specific versions for production, use date aliases for development.

## Appendix A: Quick Reference Commands

### Check Current Version

```bash
# From VERSION file
cat VERSION

# From Git tags
git describe --tags --abbrev=0

# From Docker image labels
docker inspect ghcr.io/bmcdonough/binardat-ssh-enabler:latest | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.version"'
```

### Create Release

```bash
export VERSION="YYYY.MM.DD"
echo "$VERSION" > VERSION
git add VERSION
git commit -m "Bump version to $VERSION"
git tag -a v$VERSION -m "Release v$VERSION"
git push origin main v$VERSION
```

### Build Docker Image

```bash
docker build \
  --build-arg VERSION="v$VERSION" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse HEAD)" \
  -t ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION \
  -t ghcr.io/bmcdonough/binardat-ssh-enabler:latest \
  .
```

### Push Docker Image

```bash
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION
docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest
```

### Create GitHub Release

```bash
gh release create v$VERSION \
  --title "Release v$VERSION" \
  --notes "Release notes here" \
  --latest
```

## Appendix B: Version History Template

Keep this in `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [YYYY.MM.DD] - YYYY-MM-DD

### Added
- Feature A
- Feature B

### Fixed
- Bug X
- Bug Y

### Changed
- Improvement Z

### Documentation
- Updated guide A
- Added example B
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-28
**Maintainer**: bmcdonough
