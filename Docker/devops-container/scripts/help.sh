#!/bin/bash
# Container help information
# Author: pk

set -e

cat << EOF
========================================
Super Ubuntu Docker Container Usage
========================================

ENVIRONMENT VARIABLES:
  ENABLE_SSH=true         Start SSH server (port 22; key auth required)
  ENABLE_CODE_SERVER=true Start code-server (port 8080; password auth enabled)

VOLUMES:
  /home/user/data         Persistent data storage
  /home/user/.ssh         SSH keys (mount authorized_keys for pubkey auth)

PORTS:
  22    SSH server
  8080  Code-server (VS Code)

SECURITY NOTES:
  - Runs as non-root 'user'; no sudo access for security
  - SSH: Pubkey auth only; passwords disabled
  - Code-server: Password auth enabled by default

EXAMPLES:
  # Basic interactive shell
  docker run -it -v \$(pwd)/data:/home/user/data super-ubuntu:latest

  # With SSH enabled (mount keys)
  docker run -d -p 2222:22 -e ENABLE_SSH=true -v \$(pwd)/data:/home/user/data -v \$(pwd)/ssh_keys:/home/user/.ssh:ro super-ubuntu:latest

  # With code-server enabled
  docker run -d -p 8080:8080 -e ENABLE_CODE_SERVER=true -v \$(pwd)/data:/home/user/data super-ubuntu:latest

  # Full setup with both services (docker compose recommended)
  docker compose up -d

For issues: Check logs with 'docker logs <container>'. Update to latest image for fixes.
EOF
