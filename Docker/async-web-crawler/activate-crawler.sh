#!/bin/bash
# Crawler activation script
# Author: pk

set -e

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose not found"
    echo "Install: sudo apt install docker-compose-plugin (Linux) or brew install docker-compose (Mac)"
    exit 1
fi

mkdir -p output
chmod 755 output
docker-compose up --build
