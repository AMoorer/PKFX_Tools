# Build script for MakeSomeNoise executable
# This creates a single-file executable using PyInstaller

Write-Host "Building MakeSomeNoise executable..." -ForegroundColor Green

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install PyInstaller if not already installed
Write-Host "Checking PyInstaller installation..." -ForegroundColor Cyan
pip install pyinstaller

# Clean previous builds
Write-Host "Cleaning previous build..." -ForegroundColor Cyan
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the executable using spec file
Write-Host "Creating executable..." -ForegroundColor Cyan
pyinstaller MakeSomeNoise.spec --clean

Write-Host ""
if (Test-Path "dist\MakeSomeNoise.exe") {
    Write-Host "Build complete!" -ForegroundColor Green
    Write-Host "Executable location: dist\MakeSomeNoise.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Testing executable..." -ForegroundColor Cyan
    Write-Host "Note: First run may take longer as Windows Defender scans the new executable." -ForegroundColor Gray
} else {
    Write-Host "Build failed! Check errors above." -ForegroundColor Red
}
