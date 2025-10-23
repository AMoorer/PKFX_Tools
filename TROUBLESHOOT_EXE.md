# Troubleshooting MakeSomeNoise Executable

## Common Issues and Solutions

### 1. "Ordinal X could not be located" Error

**Problem:** Missing Qt/PySide6 DLLs or plugins

**Solution:**
```powershell
# Clean rebuild with updated spec file
.\build_executable.ps1
```

The updated spec file now includes:
- Platform plugins (required for Qt window creation)
- Style plugins (for UI rendering)
- All required hidden imports

### 2. "Failed to execute script" Error

**Problem:** Missing Python dependencies

**Solution:** Add to `hiddenimports` in `MakeSomeNoise.spec`:
```python
hiddenimports=[
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'numpy',
    'noise',
    'opensimplex',
    'perlin_noise',
    'PIL',
    # Add any other imports that fail
],
```

### 3. Executable Won't Start (No Error)

**Problem:** Console window disabled, can't see errors

**Solution:** Build with console to see errors:
```powershell
# In MakeSomeNoise.spec, change:
console=True  # Instead of False

# Rebuild
pyinstaller MakeSomeNoise.spec --clean
```

### 4. "Cannot find Qt platform plugin" Error

**Problem:** Qt platform plugins not bundled correctly

**Solution:** Already fixed in updated spec file. The plugins are now explicitly included in `datas`.

### 5. Missing VCRUNTIME140.dll

**Problem:** Microsoft Visual C++ Redistributable not installed

**Solution:** 
1. Download and install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Or bundle the DLL with the executable

### 6. Slow Startup

**Problem:** Windows Defender scanning new executable

**Solution:**
- First run is always slower (~10-30 seconds)
- Subsequent runs are faster
- Add to Windows Defender exclusions if needed

## Debug Build

To see detailed errors:

1. Enable console in spec file:
```python
console=True
```

2. Rebuild:
```powershell
pyinstaller MakeSomeNoise.spec --clean
```

3. Run from command prompt to see full error output

## Manual Build Steps

If automated build fails:

```powershell
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Upgrade PyInstaller
pip install --upgrade pyinstaller

# 3. Clean build
Remove-Item -Recurse -Force build, dist
pyinstaller MakeSomeNoise.spec --clean

# 4. Test
.\dist\MakeSomeNoise.exe
```

## Check Dependencies

Verify all dependencies are in venv:
```powershell
.\venv\Scripts\Activate.ps1
pip list
```

Required packages:
- PySide6
- numpy
- noise
- opensimplex
- perlin-noise
- Pillow

## Size Reduction

If executable is too large (>200 MB):

1. Use directory build instead of onefile
2. Exclude unused packages in spec file
3. Use UPX compression (already enabled)

## Alternative: Directory Build

For faster startup and easier debugging:

```python
# In spec file, change to:
exe = EXE(
    pyz,
    a.scripts,
    # Remove these for directory build:
    # a.binaries,
    # a.datas,
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='MakeSomeNoise',
)
```

This creates a folder with the executable and all dependencies.

## Still Having Issues?

1. Check PyInstaller warnings during build
2. Look for "WARNING" messages in build output
3. Try running the Python script directly first:
   ```powershell
   .\venv\Scripts\python.exe tools\noise_generator_gui.py
   ```
4. If script works but executable doesn't, it's a packaging issue
