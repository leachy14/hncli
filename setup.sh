#!/bin/bash
# Consolidated setup script for Hacker News CLI

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╭───────────────────────────────────────────╮"
echo "│       Setting up Hacker News CLI           │"
echo "│            All-in-one Setup                │"
echo "╰───────────────────────────────────────────╯"
echo ""

# STEP 1: Verify prerequisites
echo "Checking prerequisites..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
else
    echo "✅ Python 3 is installed"
fi

# Check if Python venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "❌ Python venv module is not available. Installing it may require admin privileges."
    echo "You may need to run: sudo apt-get install python3-venv (on Ubuntu/Debian)"
    echo "Or: sudo yum install python3-venv (on CentOS/RHEL)"
    exit 1
else
    echo "✅ Python venv module is available"
fi

# STEP 2: Create virtual environment
echo ""
echo "Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# STEP 3: Install dependencies
echo ""
echo "Installing dependencies..."

# Activate virtual environment
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# STEP 4: Ensure script is executable
chmod +x "$SCRIPT_DIR/hncli"
chmod +x "$SCRIPT_DIR/run-hncli.sh"
echo "✅ Made scripts executable"

# STEP 5: Shell integration
echo ""
echo "Setting up shell integration..."

# Detect shell type
if [ -n "$ZSH_VERSION" ]; then
    SHELL_TYPE="zsh"
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_TYPE="bash"
    # Check which bash init file to use
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.bash_profile"
    fi
else
    SHELL_TYPE="unknown"
    SHELL_RC=""
fi

# Define the content to add to shell configuration
SHORTCUT_CONTENT="
# Hacker News CLI shortcut
HNCLI_PATH=\"$SCRIPT_DIR\"
function hn() {
  \$HNCLI_PATH/run-hncli.sh \"\$@\"
}
"

# Ask user if they want to set up the shell shortcut
if [ -n "$SHELL_RC" ]; then
    echo "Would you like to set up the 'hn' command for your shell? (y/n)"
    read -r SETUP_SHORTCUT
    
    if [[ "$SETUP_SHORTCUT" =~ ^[Yy] ]]; then
        echo "$SHORTCUT_CONTENT" >> "$SHELL_RC"
        echo "✅ Added 'hn' command to $SHELL_RC"
        echo ""
        echo "To start using the 'hn' command right away, run:"
        echo "  source $SHELL_RC"
    else
        echo "Skipping shell integration."
        echo "You can still use the CLI with ./run-hncli.sh"
    fi
else
    echo "❓ Unable to detect your shell configuration file."
    echo "To add the 'hn' shortcut manually, add the following to your shell config file:"
    echo "$SHORTCUT_CONTENT"
fi

# STEP 6: Completion
echo ""
echo "╭───────────────────────────────────────────╮"
echo "│         Setup Complete!                    │"
echo "╰───────────────────────────────────────────╯"
echo ""
echo "You can now use Hacker News CLI in the following ways:"
echo ""
echo "1. With the 'hn' command (if you added the shortcut):"
echo "   hn top         # Show top stories"
echo "   hn new         # Show new stories"
echo "   hn best        # Show best stories"
echo "   hn search ai   # Search for AI stories"
echo ""
echo "2. Using the run script directly:"
echo "   ./run-hncli.sh top"
echo "   ./run-hncli.sh new"
echo ""
echo "3. Activate the virtual environment manually:"
echo "   source venv/bin/activate"
echo "   ./hncli top"
echo ""
echo "Enjoy browsing Hacker News from your terminal!" 