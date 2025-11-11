# Setup Development Environment for VFX Sprite Maker
# Creates virtual environment and installs dependencies

# Change to the project root directory (parent of scripts folder)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "VFX Sprite Maker - Environment Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Project Directory: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Check if Python is installed
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Display Python version
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Cyan
    Write-Host "  .\scripts\run_sprite_gui.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "To build executable:" -ForegroundColor Cyan
    Write-Host "  .\scripts\build_executable.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
