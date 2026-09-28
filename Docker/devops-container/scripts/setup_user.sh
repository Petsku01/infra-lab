#!/bin/bash
# User setup verification script  
# Author: pk

set -e
# location should be: scripts/setup_user.sh
# chmod +x scripts/setup_user.sh

# Verify user exists (should be created in Dockerfile)
if ! id "user" &>/dev/null; then
  echo "Error: user not found. Should be created in Dockerfile."
  exit 1
fi

echo "User setup verified"
