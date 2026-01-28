FROM python:3.12-slim

# Build arguments for version information
ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

# OCI image labels
LABEL org.opencontainers.image.title="Binardat SSH Enabler"
LABEL org.opencontainers.image.description="Enable SSH on Binardat switches via web interface automation"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.source="https://github.com/bmcdonough/binardat-switch-config"
LABEL org.opencontainers.image.url="https://github.com/bmcdonough/binardat-switch-config"
LABEL org.opencontainers.image.vendor="bmcdonough"
LABEL org.opencontainers.image.licenses="MIT"

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome paths
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install package
WORKDIR /app
COPY src/ /app/src/
COPY pyproject.toml VERSION README.md LICENSE /app/
RUN pip install --no-cache-dir /app

# Create non-root user
RUN useradd -m -u 1000 switchuser && \
    chown -R switchuser:switchuser /app
USER switchuser

# Default configuration
ENV SWITCH_IP=192.168.2.1 \
    SWITCH_USERNAME=admin \
    SWITCH_PASSWORD=admin \
    SWITCH_SSH_PORT=22 \
    TIMEOUT=10

ENTRYPOINT ["binardat-config"]
