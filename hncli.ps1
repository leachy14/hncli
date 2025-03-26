# PowerShell wrapper for HNCLI

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if virtual environment exists
if (-not (Test-Path "$ScriptDir\venv")) {
    Write-Host "Virtual environment not found. Please run .\setup.ps1 first."
    exit 1
}

# Use the Python from virtual environment
$Python = "$ScriptDir\venv\Scripts\python.exe"

# Execute the Python script with the provided arguments
& $Python "$ScriptDir\hncli.py" $args 