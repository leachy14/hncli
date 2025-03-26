#!/bin/bash

# WSL-specific wrapper for Hacker News CLI
# This script activates the virtual environment and runs the command in one step

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate the virtual environment and run the command
source venv/bin/activate
./hncli "$@" 