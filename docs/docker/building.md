# Building Custom Docker Images

Guide for building and customizing the Binardat SSH Enabler Docker image.

## Table of Contents

- [Building Locally](#building-locally)
- [Customizing the Dockerfile](#customizing-the-dockerfile)
- [Multi-Architecture Builds](#multi-architecture-builds)
- [Image Optimization](#image-optimization)
- [Publishing to Registries](#publishing-to-registries)

## Building Locally

### Prerequisites

- Docker installed (version 20.10+)
- Git (to clone the repository)
- 500MB+ free disk space

### Basic Build

Clone and build the image:

```bash
# Clone the repository
git clone https://github.com/bmcdonough/binardat-switch-config.git
cd binardat-switch-config

# Checkout develop branch (contains Docker support)
git checkout develop

# Build the image
docker build -t binardat-ssh-enabler:latest .

# Verify the build
docker images binardat-ssh-enabler:latest
```

### Build with Custom Tag

Use semantic versioning or custom tags:

```bash
# Version tag
docker build -t binardat-ssh-enabler:2025.01.27 .

# Environment tag
docker build -t binardat-ssh-enabler:production .

# Multiple tags
docker build \
  -t binardat-ssh-enabler:latest \
  -t binardat-ssh-enabler:v1.0.0 \
  .
```

### Using Build Scripts

The repository includes a helper script:

```bash
# Make script executable
chmod +x scripts/build-docker.sh

# Run the build script
./scripts/build-docker.sh
```

### Build Arguments

Customize the build with build arguments:

```bash
# Use a different Python version
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t binardat-ssh-enabler:python311 \
  .

# Set timezone
docker build \
  --build-arg TZ=America/New_York \
  -t binardat-ssh-enabler:latest \
  .
```

## Customizing the Dockerfile

### Understanding the Dockerfile

The Dockerfile has several key sections:

```dockerfile
# Base image selection
FROM python:3.12-slim

# System dependencies (Chromium)
RUN apt-get update && apt-get install -y ...

# Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Application code
COPY src/enable_ssh.py .
COPY src/rc4_crypto.py .

# Security (non-root user)
RUN useradd -m -u 1000 switchuser
USER switchuser

# Runtime configuration
ENV SWITCH_IP=192.168.2.1
ENTRYPOINT ["python", "enable_ssh.py"]
```

### Modifying Python Version

Edit the first line of the Dockerfile:

```dockerfile
# Use Python 3.11 instead
FROM python:3.11-slim

# Or use Alpine for smaller image
FROM python:3.12-alpine
```

**Note**: Alpine requires additional build dependencies for some Python packages.

### Adding Additional Tools

Install extra debugging or networking tools:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    iputils-ping \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*
```

### Modifying Default Configuration

Change default environment variables:

```dockerfile
ENV SWITCH_IP=10.0.0.1 \
    SWITCH_USERNAME=netadmin \
    SWITCH_PASSWORD=changeme \
    SWITCH_SSH_PORT=2222 \
    TIMEOUT=30
```

### Using a Different ChromeDriver

If you need a specific ChromeDriver version:

```dockerfile
# Download specific ChromeDriver version
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
```

### Adding Health Checks

Add a health check to monitor container status:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=1)" || exit 1
```

## Multi-Architecture Builds

### Building for ARM64

Build for Raspberry Pi, Apple Silicon, or other ARM devices:

```bash
# Enable buildx (if not already enabled)
docker buildx create --use

# Build for ARM64
docker buildx build \
  --platform linux/arm64 \
  -t binardat-ssh-enabler:arm64 \
  --load \
  .
```

### Building for Multiple Architectures

Create a multi-arch image:

```bash
# Build for both AMD64 and ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t binardat-ssh-enabler:multi-arch \
  --push \
  .
```

**Note**: `--push` is required for multi-arch builds (can't use `--load`).

### Testing ARM64 Images on AMD64

Use QEMU emulation:

```bash
# Install QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Build and test ARM64 image on AMD64 host
docker buildx build \
  --platform linux/arm64 \
  -t binardat-ssh-enabler:arm64-test \
  --load \
  .

docker run --network host binardat-ssh-enabler:arm64-test
```

## Image Optimization

### Reducing Image Size

The default image is ~400-500MB. To reduce size:

#### 1. Use Alpine Base

```dockerfile
FROM python:3.12-alpine

# Alpine requires additional build dependencies
RUN apk add --no-cache \
    chromium chromium-chromedriver \
    gcc musl-dev linux-headers
```

**Size**: ~200-300MB (50% smaller)

#### 2. Multi-Stage Build

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements-docker.txt .
RUN pip install --user --no-cache-dir -r requirements-docker.txt

# Stage 2: Runtime
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY src/ .
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT ["python", "enable_ssh.py"]
```

**Size**: ~350-400MB (25% smaller)

#### 3. Remove Unnecessary Dependencies

Review `requirements-docker.txt` and remove unused packages:

```txt
# Minimal requirements
selenium>=4.16.0
pycryptodome>=3.19.0

# Remove if not needed:
# beautifulsoup4>=4.12.0
# pyyaml>=6.0
# requests>=2.31.0
```

### Build Cache Optimization

Order Dockerfile commands to maximize cache hits:

```dockerfile
# Install system dependencies (changes rarely)
RUN apt-get update && apt-get install -y ...

# Install Python dependencies (changes occasionally)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code (changes frequently)
COPY src/ .
```

### Cleaning Up Build Artifacts

Remove unnecessary files after installation:

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium chromium-driver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
```

## Publishing to Registries

### Docker Hub

```bash
# Tag for Docker Hub
docker tag binardat-ssh-enabler:latest yourusername/binardat-ssh-enabler:latest

# Login
docker login

# Push
docker push yourusername/binardat-ssh-enabler:latest
```

### GitHub Container Registry (GHCR)

```bash
# Tag for GHCR
docker tag binardat-ssh-enabler:latest ghcr.io/yourusername/binardat-ssh-enabler:latest

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Push
docker push ghcr.io/yourusername/binardat-ssh-enabler:latest
```

### Private Registry

```bash
# Tag for private registry
docker tag binardat-ssh-enabler:latest registry.example.com/binardat-ssh-enabler:latest

# Login to private registry
docker login registry.example.com

# Push
docker push registry.example.com/binardat-ssh-enabler:latest
```

### Automated Builds with GitHub Actions

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build Docker Image

on:
  push:
    branches: [develop, main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          platforms: linux/amd64,linux/arm64
```

## Testing Custom Images

### Automated Testing

Use the test script:

```bash
# Make script executable
chmod +x scripts/test-docker.sh

# Run tests
./scripts/test-docker.sh
```

### Manual Testing

Test your custom image:

```bash
# Build
docker build -t binardat-ssh-enabler:test .

# Test help output
docker run --rm binardat-ssh-enabler:test --help

# Test with real switch (if available)
docker run --network host \
  -e SWITCH_IP=192.168.2.1 \
  binardat-ssh-enabler:test

# Check image size
docker images binardat-ssh-enabler:test
```

### Debugging Failed Builds

Run intermediate build steps:

```bash
# Build up to a specific stage
docker build --target builder -t debug-builder .

# Run intermediate image
docker run -it debug-builder /bin/bash

# Build with no cache
docker build --no-cache -t binardat-ssh-enabler:test .

# Verbose output
docker build --progress=plain -t binardat-ssh-enabler:test .
```

## Best Practices

1. **Use specific base image tags** (not `latest`):
   ```dockerfile
   FROM python:3.12.1-slim
   ```

2. **Pin dependency versions** in `requirements-docker.txt`:
   ```txt
   selenium==4.16.0
   pycryptodome==3.19.1
   ```

3. **Scan for vulnerabilities**:
   ```bash
   docker scan binardat-ssh-enabler:latest
   ```

4. **Use `.dockerignore`** to exclude unnecessary files

5. **Document custom builds** in your fork's README

6. **Test on target architecture** before deploying

7. **Use multi-stage builds** for production images

8. **Run as non-root user** (already implemented)

## Troubleshooting Build Issues

### "Failed to fetch" during apt-get

Update package lists:

```dockerfile
RUN apt-get update && apt-get install -y ...
```

### ChromeDriver version mismatch

Install matching versions:

```dockerfile
# Install specific Chrome and ChromeDriver versions
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb && \
    apt install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb
```

### Python package build failures

Install build dependencies:

```dockerfile
RUN apt-get install -y --no-install-recommends \
    gcc python3-dev
```

### Out of disk space

Clean up Docker:

```bash
docker system prune -a
docker volume prune
```

## Further Reading

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Quick Start Guide](quickstart.md)
- [Usage Guide](usage.md)
