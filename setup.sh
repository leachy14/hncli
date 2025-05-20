#!/bin/bash
# Setup script for Hacker News CLI in Codex environment

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Setting up Hacker News CLI..."

# Configure pip to use the proxy if available
if [ -n "$http_proxy" ]; then
    pip config set global.proxy "$http_proxy"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov mypy flake8 black

# Install project dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .

echo "Setup complete. You can now use the 'hn' command."
echo "Development tools installed: pytest, mypy, flake8, black" 