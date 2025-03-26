# PowerShell setup script for HNCLI

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Setting up Hacker News CLI..."

# Check if Python 3 is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ./venv/Scripts/Activate.ps1

# Install requirements
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Make CLI script executable (only needed for Linux/WSL)
if ($IsLinux -or $IsMacOS) {
    chmod +x hncli
}

Write-Host "Setup complete!"
Write-Host ""
Write-Host "To use the Hacker News CLI:"
Write-Host "1. Activate the virtual environment: ./venv/Scripts/Activate.ps1"
Write-Host "2. Run commands like: python hncli.py top"
Write-Host ""
Write-Host "You can add this directory to your PATH for easier access." 