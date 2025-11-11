# Setup Development Environment for PKFX Tools
# Creates virtual environment and installs all dependencies

Write-Host "PKFX Tools - Development Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.12 or later." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "`n✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`n✓ Setup complete!" -ForegroundColor Green
Write-Host "`nYou can now:" -ForegroundColor Cyan
Write-Host "  - Run MakeSomeNoise:    .\tools\makesomenoise\scripts\run_noise_gui.ps1" -ForegroundColor White
Write-Host "  - Run VFX Sprite Maker: .\tools\fxspritemaker\scripts\run_sprite_gui.ps1" -ForegroundColor White
Write-Host "`nOr navigate to individual tool directories for more options." -ForegroundColor Cyan
