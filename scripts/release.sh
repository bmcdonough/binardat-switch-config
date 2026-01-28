#!/bin/bash
# Automated release helper script for binardat-switch-config Docker image
# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 2026.01.28

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if version argument provided
VERSION=$1
if [ -z "$VERSION" ]; then
    print_error "Version number required"
    echo "Usage: $0 <version>"
    echo "Example: $0 2026.01.28"
    exit 1
fi

# Validate version format (YYYY.MM.DD or YYYY.MM.DD.MICRO)
if ! [[ "$VERSION" =~ ^[0-9]{4}\.[0-9]{2}\.[0-9]{2}(\.[0-9]+)?$ ]]; then
    print_error "Invalid version format: $VERSION"
    echo "Expected format: YYYY.MM.DD or YYYY.MM.DD.MICRO"
    echo "Examples: 2026.01.28 or 2026.01.28.1"
    exit 1
fi

# Check if git repository
if [ ! -d ".git" ]; then
    print_error "Not a git repository. Run this script from the repository root."
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warn "You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Aborted by user"
        exit 1
    fi
fi

# Confirmation
print_info "Creating release v$VERSION"
echo ""
echo "This will:"
echo "  1. Update VERSION file to $VERSION"
echo "  2. Create git tag v$VERSION"
echo "  3. Build Docker image with multiple tags"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Aborted by user"
    exit 1
fi

# Update VERSION file
print_info "Updating VERSION file..."
echo "$VERSION" > VERSION

# Extract date components for alias tags
YEAR=$(echo "$VERSION" | cut -d. -f1)
MONTH=$(echo "$VERSION" | cut -d. -f2)
YEAR_MONTH="${YEAR}.${MONTH}"

# Build Docker image with multiple tags
print_info "Building Docker image..."
docker build \
  --build-arg VERSION="v$VERSION" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse HEAD)" \
  --tag "ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION" \
  --tag "ghcr.io/bmcdonough/binardat-ssh-enabler:latest" \
  --tag "ghcr.io/bmcdonough/binardat-ssh-enabler:$YEAR_MONTH" \
  --tag "ghcr.io/bmcdonough/binardat-ssh-enabler:$YEAR" \
  .

# Verify image labels
print_info "Verifying image labels..."
IMAGE_VERSION=$(docker inspect ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION | \
  jq -r '.[0].Config.Labels."org.opencontainers.image.version"')

if [ "$IMAGE_VERSION" = "v$VERSION" ]; then
    print_info "Image version label verified: $IMAGE_VERSION"
else
    print_warn "Image version label mismatch: expected v$VERSION, got $IMAGE_VERSION"
fi

echo ""
print_info "Release v$VERSION created successfully!"
echo ""
echo "Next steps:"
echo ""
echo "1. Review the CHANGELOG:"
echo "   ${YELLOW}vim CHANGELOG.md${NC}"
echo ""
echo "2. Commit VERSION file (if modified):"
echo "   ${YELLOW}git add VERSION${NC}"
echo "   ${YELLOW}git commit -m \"Bump version to $VERSION\"${NC}"
echo ""
echo "3. Create and push git tag:"
echo "   ${YELLOW}git tag -a v$VERSION -m \"Release v$VERSION\"${NC}"
echo "   ${YELLOW}git push origin main${NC}"
echo "   ${YELLOW}git push origin v$VERSION${NC}"
echo ""
echo "4. Push Docker images to registry:"
echo "   ${YELLOW}docker push ghcr.io/bmcdonough/binardat-ssh-enabler:v$VERSION${NC}"
echo "   ${YELLOW}docker push ghcr.io/bmcdonough/binardat-ssh-enabler:latest${NC}"
echo "   ${YELLOW}docker push ghcr.io/bmcdonough/binardat-ssh-enabler:$YEAR_MONTH${NC}"
echo "   ${YELLOW}docker push ghcr.io/bmcdonough/binardat-ssh-enabler:$YEAR${NC}"
echo ""
echo "5. Create GitHub release:"
echo "   ${YELLOW}gh release create v$VERSION --title \"Release v$VERSION\" --latest${NC}"
echo ""
echo "Or push all tags at once:"
echo "   ${YELLOW}docker push ghcr.io/bmcdonough/binardat-ssh-enabler --all-tags${NC}"
