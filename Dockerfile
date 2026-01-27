FROM python:3.12-slim

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome paths
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install Python dependencies
WORKDIR /app
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY src/enable_ssh.py .
COPY src/rc4_crypto.py .

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

ENTRYPOINT ["python", "enable_ssh.py"]
