# Launch Noise Generator GUI
Write-Host "Starting Noise Generator GUI..." -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the GUI
python tools\noise_generator_gui.py
