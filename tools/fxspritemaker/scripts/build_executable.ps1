# Build VFX Sprite Maker Executable
# Creates standalone .exe using PyInstaller

# Change to the project root directory (parent of scripts folder)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "VFX Sprite Maker - Build Executable" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: .\scripts\setup_env.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install PyInstaller if not present
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
pip show pyinstaller >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

# Clean previous builds
if (Test-Path "build") {
    Write-Host "Cleaning build directory..." -ForegroundColor Gray
    Remove-Item -Recurse -Force build
}
if (Test-Path "dist\FXSpriteMaker") {
    Write-Host "Cleaning dist directory..." -ForegroundColor Gray
    Remove-Item -Recurse -Force dist\FXSpriteMaker
}

# Build with PyInstaller
pyinstaller FXSpriteMaker.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  dist\FXSpriteMaker.exe" -ForegroundColor White
    Write-Host ""
    
    # Display file size
    $exePath = "dist\FXSpriteMaker.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    }
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Build failed with error code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
