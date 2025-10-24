# Launch Noise Generator GUI
Write-Host "Starting Noise Generator GUI..." -ForegroundColor Cyan

# Change to root directory
Set-Location $PSScriptRoot\..

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the GUI
python -m makesomenoise.noise_generator_gui
