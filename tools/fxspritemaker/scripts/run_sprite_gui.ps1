# Run VFX Sprite Maker GUI
# Launches the application in development mode

# Change to the project root directory (parent of scripts folder)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "VFX Sprite Maker - Starting GUI..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: .\scripts\setup_env.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Run the application
python -m src.fxspritemaker

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Application exited with error code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
