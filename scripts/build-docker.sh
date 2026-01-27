#!/bin/bash
set -e

echo "========================================"
echo " Building Binardat SSH Enabler Docker  "
echo "========================================"
echo ""

# Get version from git tag or use 'dev'
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")
echo "Version: $VERSION"
echo ""

# Build the image
echo "Building Docker image..."
docker build -t binardat-ssh-enabler:latest .

# Tag with version
if [ "$VERSION" != "dev" ]; then
    echo "Tagging with version: $VERSION"
    docker build -t binardat-ssh-enabler:$VERSION .
fi

echo ""
echo "========================================"
echo " Build Complete!                       "
echo "========================================"
echo ""

# Show image details
echo "Image details:"
docker images binardat-ssh-enabler:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
echo ""

echo "Run with:"
echo "  docker run --network host binardat-ssh-enabler:latest"
echo ""
echo "Or with custom IP:"
echo "  docker run --network host -e SWITCH_IP=192.168.2.50 binardat-ssh-enabler:latest"
echo ""
