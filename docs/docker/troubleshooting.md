# Docker Troubleshooting Guide

Solutions for common issues when using the Binardat SSH Enabler Docker image.

## Table of Contents

- [Version Issues](#version-issues)
- [Connection Issues](#connection-issues)
- [Authentication Problems](#authentication-problems)
- [Docker-Specific Issues](#docker-specific-issues)
- [Chromium/Selenium Errors](#chromiumselenium-errors)
- [SSH Port Issues](#ssh-port-issues)
- [Network Problems](#network-problems)
- [Debugging Techniques](#debugging-techniques)

## Version Issues

### Wrong Version Running

**Symptom**:
You expected a newer version but an older version is running.

**Solutions**:

1. **Check current version**:
   ```bash
   docker inspect ghcr.io/bmcdonough/binardat-switch-config:latest | \
     jq -r '.[0].Config.Labels."org.opencontainers.image.version"'
   ```

2. **Force pull latest image**:
   ```bash
   docker pull ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Remove old images and pull fresh**:
   ```bash
   # Remove all binardat-switch-config images
   docker images | grep binardat-switch-config | awk '{print $3}' | xargs docker rmi -f

   # Pull fresh image
   docker pull ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

4. **Use specific version tag** (recommended for production):
   ```bash
   docker run --network host ghcr.io/bmcdonough/binardat-switch-config:v2026.01.28
   ```

### Docker Image Cache Issues

**Symptom**:
Changes not reflected even after pulling new image.

**Solutions**:

1. **Check image ID and creation date**:
   ```bash
   docker images ghcr.io/bmcdonough/binardat-switch-config
   ```

2. **Prune Docker cache**:
   ```bash
   docker system prune -a
   docker pull ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Run with `--pull always`**:
   ```bash
   docker run --pull always --network host \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

### Version Mismatch Between Documentation and Image

**Symptom**:
Documentation references features not available in your image version.

**Solutions**:

1. **Check image creation date**:
   ```bash
   docker inspect ghcr.io/bmcdonough/binardat-switch-config:latest | \
     jq -r '.[0].Config.Labels."org.opencontainers.image.created"'
   ```

2. **Check repository for version compatibility**:
   - Visit [CHANGELOG](CHANGELOG.md) to see when features were added
   - Ensure you're using a version that includes the desired features

3. **Pull specific version matching documentation**:
   ```bash
   # Example: Pull version 2026.01.28
   docker pull ghcr.io/bmcdonough/binardat-switch-config:v2026.01.28
   ```

### Unexpected Behavior After Upgrade

**Symptom**:
Container behavior changed after pulling `:latest` tag.

**Solutions**:

1. **Identify what changed**:
   ```bash
   # Check CHANGELOG for recent changes
   curl https://raw.githubusercontent.com/bmcdonough/binardat-switch-config/main/CHANGELOG.md
   ```

2. **Rollback to previous version**:
   ```bash
   # Use a specific older version
   docker run --network host ghcr.io/bmcdonough/binardat-switch-config:v2026.01.27
   ```

3. **Pin to specific version** (prevent future auto-updates):
   ```yaml
   # In docker-compose.yml
   services:
     ssh-enabler:
       image: ghcr.io/bmcdonough/binardat-switch-config:v2026.01.28  # Pinned
   ```

For more on version management, see [Versioning and Release Process](versioning-and-releases.md).

## Connection Issues

### "Connection refused" Error

**Symptom**:
```
Error: Connection refused
✗ Login failed: Timeout waiting for page elements
```

**Solutions**:

1. **Verify network mode**:
   ```bash
   # Must use --network host
   docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Check switch IP**:
   ```bash
   # Ping the switch
   ping 192.168.2.1

   # Verify switch is on correct IP
   docker run --network host \
     -e SWITCH_IP=192.168.2.100 \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Verify switch web interface is accessible**:
   ```bash
   curl http://192.168.2.1
   # Should return HTML content
   ```

### "Network unreachable" Error

**Symptom**:
```
✗ Login failed: Network unreachable
```

**Solutions**:

1. **Check host routing**:
   ```bash
   ip route
   # Ensure route to 192.168.2.0/24 exists
   ```

2. **Add route if needed**:
   ```bash
   sudo ip route add 192.168.2.0/24 via 192.168.1.1
   ```

3. **Check firewall rules**:
   ```bash
   sudo iptables -L
   # Ensure HTTP traffic to switches is allowed
   ```

### Timeout Waiting for Page Elements

**Symptom**:
```
✗ Login failed: Timeout waiting for page elements
```

**Solutions**:

1. **Increase timeout**:
   ```bash
   docker run --network host \
     -e TIMEOUT=30 \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Check switch is responding**:
   ```bash
   curl -v http://192.168.2.1
   # Should connect and return HTTP 200
   ```

3. **Verify correct switch model**:
   - This tool is designed for Binardat switches
   - Other brands may have different web interfaces

## Authentication Problems

### Login Failed - Wrong Credentials

**Symptom**:
```
✗ Login failed: Could not find element
```

**Solutions**:

1. **Verify credentials in browser**:
   - Open http://192.168.2.1 in a browser
   - Try logging in manually with your credentials

2. **Check for special characters**:
   ```bash
   # Escape special characters in passwords
   docker run --network host \
     -e SWITCH_PASSWORD='my$ecure!pass' \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Try default credentials**:
   ```bash
   docker run --network host \
     -e SWITCH_USERNAME=admin \
     -e SWITCH_PASSWORD=admin \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

### Password with Special Characters

**Symptom**:
Password not accepted, bash interpretation issues

**Solutions**:

1. **Use environment file**:
   ```env
   # .env file
   SWITCH_PASSWORD=my$pecial!pass@123
   ```
   ```bash
   docker run --network host --env-file .env ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Use single quotes** in command line:
   ```bash
   docker run --network host \
     -e SWITCH_PASSWORD='my$pecial!pass@123' \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Use command-line arguments**:
   ```bash
   docker run --network host ghcr.io/bmcdonough/binardat-switch-config:latest \
     --password 'my$pecial!pass@123'
   ```

## Docker-Specific Issues

### Permission Denied Errors

**Symptom**:
```
docker: Got permission denied while trying to connect to the Docker daemon socket
```

**Solutions**:

1. **Add user to docker group**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Use sudo** (temporary):
   ```bash
   sudo docker run --network host ...
   ```

3. **Fix Docker socket permissions**:
   ```bash
   sudo chmod 666 /var/run/docker.sock
   ```

### Container Exits Immediately

**Symptom**:
Container starts and exits without output

**Solutions**:

1. **Check container logs**:
   ```bash
   docker ps -a  # Find container ID
   docker logs <container_id>
   ```

2. **Run with --rm for automatic cleanup**:
   ```bash
   docker run --rm --network host ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Check for conflicting containers**:
   ```bash
   docker ps
   # Stop conflicting containers if any
   ```

### "No space left on device"

**Symptom**:
```
Error: No space left on device
```

**Solutions**:

1. **Clean up Docker**:
   ```bash
   docker system prune -a
   docker volume prune
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Remove unused images**:
   ```bash
   docker image prune -a
   ```

## Chromium/Selenium Errors

### ChromeDriver Not Found

**Symptom**:
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solutions**:

This should not happen with the official image. If you see this:

1. **Use official image**:
   ```bash
   docker pull ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Check CHROMEDRIVER_PATH**:
   ```bash
   docker run --network host \
     -e CHROMEDRIVER_PATH=/usr/bin/chromedriver \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

3. **Verify ChromeDriver in image**:
   ```bash
   docker run --rm ghcr.io/bmcdonough/binardat-switch-config:latest \
     /bin/bash -c "which chromedriver"
   ```

### Chrome Crashed on Startup

**Symptom**:
```
WebDriverException: chrome not reachable
session deleted because of page crash
```

**Solutions**:

1. **Increase shared memory** (if not using --network host):
   ```bash
   docker run --network host --shm-size=2g ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Verify --no-sandbox flag** (already included in image)

3. **Check system resources**:
   ```bash
   free -h
   # Ensure sufficient RAM available
   ```

### Selenium Timeout Errors

**Symptom**:
```
TimeoutException: Message:
```

**Solutions**:

1. **Increase timeout**:
   ```bash
   docker run --network host \
     -e TIMEOUT=30 \
     ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

2. **Check switch responsiveness**:
   ```bash
   time curl http://192.168.2.1
   # Should respond in < 2 seconds
   ```

3. **Run with visible browser for debugging**:
   ```bash
   docker run --network host \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix \
     ghcr.io/bmcdonough/binardat-switch-config:latest \
     --show-browser
   ```

## SSH Port Issues

### SSH Port Not Accessible After Enablement

**Symptom**:
```
✓ SSH enablement process completed successfully
⚠ SSH port 22 is not responding
```

**Solutions**:

1. **Reboot the switch**:
   - Some switches require reboot for SSH to start
   - Reboot via web interface or power cycle

2. **Wait longer**:
   ```bash
   # Try connecting after 30 seconds
   sleep 30
   ssh admin@192.168.2.1
   ```

3. **Check switch firewall settings**:
   - Log into web interface
   - Navigate to firewall/security settings
   - Ensure SSH is allowed

4. **Verify SSH is on correct port**:
   ```bash
   # Scan for SSH port
   nmap 192.168.2.1 -p 22,2222,22222
   ```

### Different SSH Port Than Expected

**Symptom**:
SSH not on port 22

**Solutions**:

1. **Check switch documentation** for default SSH port

2. **Scan all ports**:
   ```bash
   nmap 192.168.2.1
   ```

3. **Try common SSH ports**:
   ```bash
   ssh -p 2222 admin@192.168.2.1
   ssh -p 22222 admin@192.168.2.1
   ```

## Network Problems

### Switch on Different Subnet

**Symptom**:
Can't reach switch from Docker container

**Solutions**:

1. **Verify host can reach switch**:
   ```bash
   ping 192.168.2.1
   ```

2. **Add routing**:
   ```bash
   sudo ip route add 192.168.2.0/24 via <gateway_ip>
   ```

3. **Use intermediate host**:
   - SSH to host on same subnet as switch
   - Run Docker container from there

### VPN or Complex Networking

**Symptom**:
Switch behind VPN or complex network topology

**Solutions**:

1. **Ensure VPN is active on host**:
   ```bash
   ip addr show
   # Verify VPN interface is present
   ```

2. **Use host network mode** (required):
   ```bash
   docker run --network host ...
   ```

3. **Test connectivity from host**:
   ```bash
   curl http://192.168.2.1
   ```

## Debugging Techniques

### Enable Verbose Output

Currently, the script outputs detailed progress. For even more detail:

1. **Check container logs**:
   ```bash
   docker logs <container_id>
   ```

2. **Run with TTY**:
   ```bash
   docker run -it --network host ghcr.io/bmcdonough/binardat-switch-config:latest
   ```

### Show Browser for Visual Debugging

Requires X11 forwarding:

```bash
# Allow X11 connections
xhost +local:docker

# Run with display
docker run --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/bmcdonough/binardat-switch-config:latest \
  --show-browser

# Revoke X11 access after
xhost -local:docker
```

### Save Page Source for Inspection

If you've modified the code to save page source:

```bash
docker run --network host \
  -v $(pwd)/debug:/debug \
  ghcr.io/bmcdonough/binardat-switch-config:latest
```

### Interactive Shell in Container

For advanced debugging:

```bash
# Start container with shell
docker run -it --network host \
  --entrypoint /bin/bash \
  ghcr.io/bmcdonough/binardat-switch-config:latest

# Inside container
python enable_ssh.py --help
python enable_ssh.py --switch-ip 192.168.2.1
```

### Test Network Connectivity from Container

```bash
docker run -it --network host --entrypoint /bin/bash ghcr.io/bmcdonough/binardat-switch-config:latest

# Inside container
apt-get update && apt-get install -y iputils-ping curl
ping 192.168.2.1
curl http://192.168.2.1
```

### Check Docker Network Configuration

```bash
# List Docker networks
docker network ls

# Inspect host network
docker network inspect host

# Verify container is using host network
docker inspect <container_id> | grep NetworkMode
```

## Common Error Messages

### "Could not find 'Monitor Management' parent menu"

**Cause**: Switch web interface differs from expected layout

**Solutions**:
1. Verify switch model is supported
2. Check switch firmware version
3. Log into web interface manually to verify menu structure

### "Could not find enable field automatically"

**Cause**: SSH configuration form layout differs

**Solutions**:
1. Enable debug output to see form fields
2. Report issue on GitHub with switch model info
3. May require code modification for your switch model

### "Configuration save may have failed"

**Cause**: JavaScript save command didn't execute

**Solutions**:
1. Usually non-critical - SSH is still enabled
2. Log into web interface and manually save configuration
3. Configuration may auto-save on most switches

## Getting Help

If you're still experiencing issues:

1. **Check existing issues**:
   - [GitHub Issues](https://github.com/bmcdonough/binardat-switch-config/issues)

2. **Gather information**:
   ```bash
   # Docker version
   docker --version

   # System info
   uname -a

   # Network info
   ip addr show

   # Container logs
   docker logs <container_id>
   ```

3. **Create a bug report**:
   - Include error messages
   - Include switch model and firmware version
   - Include Docker version and host OS
   - Include network topology (if relevant)

4. **Workarounds**:
   - Try the proof-of-concept Python script directly
   - Enable SSH manually via web interface
   - Use the original proof-of-concept script (non-Docker)

## Related Documentation

- [Quick Start Guide](quickstart.md) - Basic usage
- [Usage Guide](usage.md) - Advanced configuration
- [Building Guide](building.md) - Custom images
- [GitHub Repository](https://github.com/bmcdonough/binardat-switch-config) - Source code and issues
