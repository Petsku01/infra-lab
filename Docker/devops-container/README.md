# DevOps Container

A comprehensive development and operations container with SSH access, development tools, and customizable shell environment for remote development workflows.

## Overview

This Docker container provides a full-featured Ubuntu-based development environment with SSH server, code-server (VS Code in browser), modern shell (zsh with oh-my-zsh), and a complete toolkit for DevOps workflows. Designed for remote development, CI/CD operations, and infrastructure management.

## Features

- **SSH Server**: Secure remote access with password or key-based authentication
- **Code Server**: VS Code in your browser (optional)
- **Modern Shell**: Zsh with oh-my-zsh and customizable themes
- **Development Tools**: Git, Python 3, Node.js, npm, AWS CLI
- **System Utilities**: curl, wget, nano, vim, htop, net-tools, jq
- **Security**: Non-root user execution with sudo privileges
- **Persistence**: Volume mounting for data and configuration

## Architecture

```
devops-container/
├── Dockerfile               # Multi-stage container build
├── docker-compose.yml       # Orchestration configuration
├── entrypoint.sh           # Container initialization
├── config/
│   ├── sshd_config         # SSH daemon configuration
│   ├── zshrc               # Zsh shell configuration
│   └── motd                # Message of the day
├── scripts/
│   ├── setup_user.sh       # User provisioning
│   ├── install_code_server.sh  # VS Code server installer
│   ├── example.sh          # Example script
│   └── help.sh             # Help documentation
├── data/                   # Persistent data directory
└── build.sh                # Build automation script
```

## Building the Container

### Using Docker Build

```bash
docker build -t devops-container:latest ./devops-container
```

### Using docker-compose

```bash
cd devops-container
docker-compose build
```

### Using Build Script

```bash
cd devops-container
chmod +x build.sh
./build.sh
```

## Usage

### Quick Start with docker-compose

```bash
cd devops-container
docker-compose up -d
```

This starts the container with:
- SSH on port 2222
- Code Server on port 8080 (if enabled)
- Persistent data volume

### Manual Docker Run

```bash
docker run -d \
  --name devops \
  -p 2222:22 \
  -p 8080:8080 \
  -v devops-data:/data \
  -e USER_NAME=devuser \
  -e USER_PASSWORD=secure_password \
  devops-container:latest
```

### Connect via SSH

```bash
ssh devuser@localhost -p 2222
```

Default credentials (change immediately):
- Username: devuser
- Password: changeme

### Access Code Server

Open browser and navigate to:
```
http://localhost:8080
```

## Environment Variables

### User Configuration

- `USER_NAME`: Username for SSH access (default: devuser)
- `USER_PASSWORD`: Password for user (default: changeme)
- `USER_UID`: User ID for filesystem permissions (default: 1000)
- `USER_GID`: Group ID for filesystem permissions (default: 1000)

### SSH Configuration

- `SSH_PORT`: SSH server port (default: 22, mapped to 2222 on host)
- `ENABLE_ROOT_LOGIN`: Allow root SSH login (default: no)

### Code Server Configuration

- `CODE_SERVER_PORT`: Code server port (default: 8080)
- `CODE_SERVER_PASSWORD`: Access password for code-server

## Pre-installed Tools

### Development Languages
- **Python 3**: Latest Python 3 with pip
- **Node.js**: JavaScript runtime with npm

### DevOps Tools
- **git**: Version control
- **awscli**: AWS command-line interface
- **docker**: Docker CLI (if docker socket mounted)
- **kubectl**: Kubernetes CLI (add via script)
- **terraform**: Infrastructure as code (add via script)

### System Utilities
- **curl/wget**: HTTP clients
- **nano/vim**: Text editors
- **htop**: Process monitor
- **net-tools**: Network diagnostics
- **jq**: JSON processor
- **sudo**: Privilege escalation

### Shell Environment
- **bash**: Default shell
- **zsh**: Modern shell with plugins
- **oh-my-zsh**: Zsh framework with themes

## Volume Mounts

### Persistent Data

```bash
docker run -d -v /host/path:/data devops-container:latest
```

### Mount Docker Socket

Enable Docker-in-Docker:

```bash
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  devops-container:latest
```

### Mount SSH Keys

```bash
docker run -d \
  -v ~/.ssh:/home/devuser/.ssh:ro \
  devops-container:latest
```

### Mount Project Directory

```bash
docker run -d \
  -v $(pwd)/project:/workspace \
  devops-container:latest
```

## SSH Configuration

### Password Authentication

Default enabled. Change password after first login:

```bash
passwd
```

### Key-Based Authentication

1. Generate key pair on your machine:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/devops_key
```

2. Copy public key to container:
```bash
docker cp ~/.ssh/devops_key.pub devops:/home/devuser/.ssh/authorized_keys
docker exec devops chown devuser:devuser /home/devuser/.ssh/authorized_keys
docker exec devops chmod 600 /home/devuser/.ssh/authorized_keys
```

3. Connect with key:
```bash
ssh -i ~/.ssh/devops_key devuser@localhost -p 2222
```

### Disable Password Authentication

Edit `config/sshd_config`:
```
PasswordAuthentication no
PubkeyAuthentication yes
```

Rebuild container.

## Security Hardening

### Change Default Credentials

```bash
docker exec -it devops passwd devuser
```

### Restrict SSH Access

Update `config/sshd_config`:
```
PermitRootLogin no
MaxAuthTries 3
AllowUsers devuser
```

### Enable Firewall

```bash
docker exec -it devops bash
apt-get install ufw
ufw allow 22/tcp
ufw enable
```

### Use Key-Based Auth Only

Disable password authentication (see SSH Configuration above).

## Example Workflows

### CI/CD Pipeline Runner

```yaml
# .gitlab-ci.yml
deploy:
  image: devops-container:latest
  script:
    - aws s3 sync ./dist s3://my-bucket
    - ssh -i $DEPLOY_KEY user@server "systemctl restart app"
```

### Remote Development

```bash
# Start container
docker-compose up -d

# Connect and work
ssh devuser@localhost -p 2222

# Or use code-server in browser
open http://localhost:8080
```

### Infrastructure Management

```bash
# Enter container
docker exec -it devops zsh

# Manage cloud resources
aws ec2 describe-instances
kubectl get pods
terraform plan
```

## Customization

### Add Custom Scripts

Place scripts in `scripts/` directory before building:

```bash
echo '#!/bin/bash' > devops-container/scripts/deploy.sh
echo 'echo "Deploying..."' >> devops-container/scripts/deploy.sh
chmod +x devops-container/scripts/deploy.sh
docker build -t devops-container:latest ./devops-container
```

### Customize Zsh Theme

Edit `config/zshrc`:
```bash
ZSH_THEME="agnoster"  # or "robbyrussell", "powerlevel10k", etc.
```

### Add System Packages

Edit `Dockerfile` and add to apt-get install:
```dockerfile
RUN apt-get update && apt-get install -y \
    your-package-here \
    && apt-get clean
```

## Monitoring and Logs

### View Container Logs

```bash
docker logs devops
```

### Follow Logs in Real-Time

```bash
docker logs -f devops
```

### SSH Access Logs

```bash
docker exec devops tail -f /var/log/auth.log
```

### System Resource Usage

```bash
docker exec devops htop
```

## Troubleshooting

### Issue: Cannot connect via SSH

**Solution 1**: Check if SSH service is running
```bash
docker exec devops service ssh status
```

**Solution 2**: Restart SSH service
```bash
docker exec devops service ssh restart
```

**Solution 3**: Verify port mapping
```bash
docker port devops
```

### Issue: Code server not accessible

**Solution**: Check if code-server is running and port is exposed:
```bash
docker exec devops ps aux | grep code-server
docker port devops | grep 8080
```

### Issue: Permission denied on mounted volumes

**Solution**: Match container user UID with host UID:
```bash
docker run -d \
  -e USER_UID=$(id -u) \
  -e USER_GID=$(id -g) \
  -v $(pwd)/data:/data \
  devops-container:latest
```

### Issue: Slow container startup

**Solution**: Pre-build image with all tools instead of installing at runtime:
```bash
docker build --no-cache -t devops-container:latest ./devops-container
```

## Docker Compose Reference

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### Rebuild and Restart

```bash
docker-compose up -d --build
```

### View Logs

```bash
docker-compose logs -f
```

### Scale Services

```bash
docker-compose up -d --scale devops=3
```

## Performance Optimization

- **Build Cache**: Use multi-stage builds to leverage layer caching
- **Image Size**: Currently optimized but can be reduced further with Alpine base
- **Startup Time**: ~2-3 seconds for SSH ready
- **Memory**: Base usage ~100-150 MB

## Health Checks

### SSH Health Check

```bash
docker exec devops service ssh status
```

### System Health

```bash
docker exec devops bash -c "uptime && free -h && df -h"
```

## Container Specifications

- **Base Image**: ubuntu:24.04
- **Size**: Varies (estimated 800 MB - 1.5 GB with all tools)
- **User**: devuser (non-root with sudo)
- **Exposed Ports**: 22 (SSH), 8080 (code-server)

## Version

Current version: 1.2

## Exit Codes

- **0**: Successful operation
- **1**: General error
- **137**: Container killed (OOM or manual stop)

## License

See project root for license information.

## Contributing

Contributions welcome. When adding new features, ensure backward compatibility and update documentation accordingly.

## Support

For issues or questions:
1. Check logs: `docker logs devops`
2. Verify configuration files
3. Review Dockerfile and entrypoint.sh
4. Check GitHub issues for similar problems
