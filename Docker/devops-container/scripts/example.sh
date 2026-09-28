#!/bin/bash
# Example script demonstrating container capabilities
# Author: pk

set -e

echo "====================================="
echo "Running example initialization script"
echo "====================================="
echo "User: $(whoami)"
echo "Home: $HOME"
echo "Shell: $SHELL"
echo ""
echo "Installed versions:"
node --version 2>/dev/null && echo "Node: $(node --version)"
python3 --version 2>/dev/null
git --version 2>/dev/null
echo ""
echo "Creating test file in data directory..."
echo "Initialized at $(date)" > /home/user/data/initialized.txt
echo "Done! Check /home/user/data/initialized.txt"
