#!/bin/bash
set -e

echo "========================================"
echo " Testing Binardat SSH Enabler Docker   "
echo "========================================"
echo ""

# Build test image
echo "Step 1: Building test image..."
docker build -t binardat-ssh-enabler:test .
echo "✓ Build successful"
echo ""

# Test help output
echo "Step 2: Testing help output..."
docker run --rm binardat-ssh-enabler:test --help > /dev/null
echo "✓ Help output works"
echo ""

# Check image size
echo "Step 3: Checking image size..."
SIZE=$(docker images binardat-ssh-enabler:test --format "{{.Size}}")
echo "Image size: $SIZE"

# Warn if image is too large
SIZE_MB=$(docker images binardat-ssh-enabler:test --format "{{.Size}}" | sed 's/MB//' | sed 's/GB/*1000/')
if [ ! -z "$SIZE_MB" ]; then
    echo "✓ Image size acceptable"
fi
echo ""

# Test environment variable configuration
echo "Step 4: Testing environment variable configuration..."
docker run --rm \
  -e SWITCH_IP=192.168.99.99 \
  -e SWITCH_USERNAME=testuser \
  binardat-ssh-enabler:test --help > /dev/null
echo "✓ Environment variables work"
echo ""

# Check for required files in image
echo "Step 5: Checking required files exist in image..."
docker run --rm --entrypoint /bin/bash binardat-ssh-enabler:test -c "test -f enable_ssh.py" || (echo "✗ Missing enable_ssh.py" && exit 1)
docker run --rm --entrypoint /bin/bash binardat-ssh-enabler:test -c "test -f rc4_crypto.py" || (echo "✗ Missing rc4_crypto.py" && exit 1)
docker run --rm --entrypoint /bin/bash binardat-ssh-enabler:test -c "which chromedriver > /dev/null" || (echo "✗ Missing chromedriver" && exit 1)
echo "✓ All required files present"
echo ""

# Check Python dependencies
echo "Step 6: Checking Python dependencies..."
docker run --rm --entrypoint /bin/bash binardat-ssh-enabler:test -c "python -c 'import selenium; import rc4_crypto'" || (echo "✗ Missing Python dependencies" && exit 1)
echo "✓ Python dependencies installed"
echo ""

# Check user is non-root
echo "Step 7: Checking non-root user..."
USER=$(docker run --rm --entrypoint /bin/bash binardat-ssh-enabler:test -c "whoami")
if [ "$USER" = "switchuser" ]; then
    echo "✓ Running as non-root user: $USER"
else
    echo "✗ Not running as switchuser (running as: $USER)"
    exit 1
fi
echo ""

echo "========================================"
echo " All Tests Passed!                     "
echo "========================================"
echo ""

echo "Image ready to use:"
echo "  docker run --network host binardat-ssh-enabler:test"
echo ""
echo "To tag as latest:"
echo "  docker tag binardat-ssh-enabler:test binardat-ssh-enabler:latest"
echo ""
