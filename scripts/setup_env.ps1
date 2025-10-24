# Setup Python virtual environment for PKFX_Tools
Write-Host "Creating virtual environment..." -ForegroundColor Cyan

# Change to root directory
Set-Location $PSScriptRoot\..

python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`nSetup complete! Virtual environment is ready." -ForegroundColor Green
Write-Host "To activate in future sessions, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
