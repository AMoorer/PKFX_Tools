# Building MakeSomeNoise Executable

This guide explains how to create a standalone executable for the MakeSomeNoise noise generator.

## Quick Build

### Option 1: Using Build Script (Recommended)
```powershell
.\build_executable.ps1
```

### Option 2: Using Spec File
```powershell
.\venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller MakeSomeNoise.spec
```

### Option 3: Manual Command
```powershell
.\venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile --windowed --name "MakeSomeNoise" tools/noise_generator_gui.py
```

## Output

The executable will be created in:
```
dist\MakeSomeNoise.exe
```

## Build Options

### Single File (Recommended)
- **Option**: `--onefile`
- **Result**: One `.exe` file (~100-150 MB)
- **Startup**: Slower (extracts to temp folder)
- **Distribution**: Easy - just one file

### Directory Build (Faster Startup)
- **Option**: `--onedir`
- **Result**: Folder with `.exe` and dependencies
- **Startup**: Faster
- **Distribution**: Requires entire folder

## Advanced Options

### Add Icon
```powershell
pyinstaller --onefile --windowed --icon="path/to/icon.ico" tools/noise_generator_gui.py
```

### Reduce File Size
```powershell
pyinstaller --onefile --windowed --strip --upx-dir="path/to/upx" tools/noise_generator_gui.py
```

### Debug Console
```powershell
pyinstaller --onefile --console tools/noise_generator_gui.py
```

## Troubleshooting

### Missing Modules
If the executable crashes with import errors, add hidden imports:
```powershell
pyinstaller --onefile --windowed --hidden-import=MODULE_NAME tools/noise_generator_gui.py
```

### PySide6 Issues
Ensure PySide6 plugins are included:
```powershell
pyinstaller --onefile --windowed --add-data "venv/Lib/site-packages/PySide6/plugins;PySide6/plugins" tools/noise_generator_gui.py
```

### Antivirus False Positives
- Windows Defender may flag new executables
- First run will be slower due to scanning
- Consider code signing for distribution

## File Size Optimization

Typical executable size: **~150 MB**

To reduce size:
1. Use UPX compression: `--upx-dir`
2. Exclude unused libraries: `--exclude-module`
3. Use directory build instead: `--onedir`

## Distribution

### Single Executable
Simply distribute `dist\MakeSomeNoise.exe`

### With Resources
If you add external resources later:
```
MakeSomeNoise/
  ├── MakeSomeNoise.exe
  ├── resources/
  └── README.txt
```

## Clean Build

To rebuild from scratch:
```powershell
Remove-Item -Recurse -Force build, dist
pyinstaller MakeSomeNoise.spec
```

## Notes

- First build takes 2-5 minutes
- Subsequent builds are faster (uses cache)
- Test the executable on a clean system without Python installed
- Executable is platform-specific (Windows .exe won't run on macOS/Linux)
