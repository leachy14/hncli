#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Setting up Hacker News CLI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if virtualenv is installed
if ! command -v python3 -m venv &> /dev/null; then
    echo "Python venv module is not available. Installing it may require admin privileges."
    echo "You may need to run: sudo apt-get install python3-venv (on Ubuntu/Debian)"
    echo "Or: sudo yum install python3-venv (on CentOS/RHEL)"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Make CLI script executable
chmod +x hncli

echo "Setup complete!"
echo ""
echo "To use the Hacker News CLI:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run commands like: ./hncli top"
echo ""
echo "You can add this directory to your PATH or create an alias for easier access." 