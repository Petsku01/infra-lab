#!/bin/bash
# Docker build script
# Author: pk

set -e

echo "Building Super Ubuntu Docker Image (Ubuntu 24.04 base, code-server v4.107.1)..."

# Lint (optional local tool)
command -v hadolint >/dev/null && hadolint Dockerfile || echo "Hadolint not found; skipping lint."

docker build -t super-ubuntu:latest . || { echo "Build failed!"; exit 1; }

echo ""
echo "Build complete! Run with:"
echo "  docker run -it super-ubuntu:latest"
echo "  docker compose up -d"
echo ""
echo "For help:"
echo "  docker run -it super-ubuntu:latest help"
