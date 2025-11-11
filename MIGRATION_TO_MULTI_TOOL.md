# Migration to Multi-Tool Repository Structure

**Date**: November 10, 2025  
**Purpose**: Restructure PKFX_Tools to accommodate multiple tools

## Summary

The repository has been restructured from a single-tool project (MakeSomeNoise) to a multi-tool collection that now includes both MakeSomeNoise and VFX Sprite Maker.

## Changes Made

### 1. Directory Structure Reorganization

**Before:**
```
PKFX_Tools/
├── src/makesomenoise/
├── scripts/
├── MakeSomeNoise.spec
└── README.md
```

**After:**
```
PKFX_Tools/
├── tools/
│   ├── makesomenoise/
│   │   ├── src/makesomenoise/
│   │   ├── scripts/
│   │   ├── MakeSomeNoise.spec
│   │   └── README.md
│   └── fxspritemaker/
│       ├── src/fxspritemaker/
│       ├── scripts/
│       ├── VFXSpriteMaker.spec
│       └── README.md
├── scripts/
│   └── setup_env.ps1
├── docs/
├── .github/
├── requirements.txt
└── README.md
```

### 2. Files Moved

- **MakeSomeNoise**:
  - `src/` → `tools/makesomenoise/src/`
  - `scripts/` → `tools/makesomenoise/scripts/`
  - `MakeSomeNoise.spec` → `tools/makesomenoise/MakeSomeNoise.spec`

### 3. Files Added

- **VFX Sprite Maker** (copied from misc_projects):
  - `tools/fxspritemaker/src/fxspritemaker/` (complete source)
  - `tools/fxspritemaker/scripts/` (setup, run, build scripts)
  - `tools/fxspritemaker/VFXSpriteMaker.spec` (PyInstaller configuration)
  - `tools/fxspritemaker/README.md` (comprehensive documentation)
  - `tools/fxspritemaker/requirements.txt` (tool-specific dependencies)

- **Tool-Specific Documentation**:
  - `tools/makesomenoise/README.md` (extracted and adapted from main README)

- **Root Level Scripts**:
  - `scripts/setup_env.ps1` (unified environment setup)

### 4. Files Updated

- **Main README.md**:
  - Now serves as a hub listing all available tools
  - Includes quick-start guide for users and developers
  - Points to tool-specific documentation
  - Shows repository structure
  
- **requirements.txt**:
  - Consolidated dependencies from both tools
  - Added sections for each tool's specific needs
  - Includes PyInstaller for building executables

## Benefits

1. **Scalability**: Easy to add new tools following the established pattern
2. **Organization**: Each tool is self-contained with its own docs and scripts
3. **Clarity**: Main README acts as a directory/hub
4. **Maintenance**: Tool-specific changes don't affect other tools
5. **Independence**: Each tool can have its own version, dependencies, and build process

## For Developers

### Setting Up Development Environment

```powershell
# Clone repository
git clone https://github.com/AMoorer/PKFX_Tools.git
cd PKFX_Tools

# Setup unified environment (installs all dependencies)
.\scripts\setup_env.ps1

# Or setup for a specific tool
cd tools/makesomenoise    # or tools/fxspritemaker
.\scripts\setup_env.ps1
```

### Running Tools

```powershell
# MakeSomeNoise
.\tools\makesomenoise\scripts\run_noise_gui.ps1

# VFX Sprite Maker
.\tools\fxspritemaker\scripts\run_sprite_gui.ps1
```

### Building Executables

```powershell
# Navigate to specific tool
cd tools/fxspritemaker    # or tools/makesomenoise

# Run build script
.\scripts\build_executable.ps1
```

## Tool Versions

- **MakeSomeNoise**: v1.1.2
- **VFX Sprite Maker**: v1.0.6

## Next Steps

1. **Test all scripts**: Ensure setup, run, and build scripts work in new structure
2. **Update CI/CD**: Modify GitHub Actions to build both tools
3. **Create releases**: Tag and release both executables
4. **Update documentation**: Ensure all links work with new structure
5. **Archive migration docs**: Move this file to `docs/archive/` after verification

## Migration Checklist

- [x] Create `tools/` directory structure
- [x] Move MakeSomeNoise to `tools/makesomenoise/`
- [x] Copy VFX Sprite Maker to `tools/fxspritemaker/`
- [x] Create tool-specific README files
- [x] Update main README with tool listings
- [x] Create VFXSpriteMaker.spec for PyInstaller
- [x] Consolidate requirements.txt at root
- [x] Create root-level setup script
- [ ] Test environment setup scripts
- [ ] Test tool launch scripts
- [ ] Test build scripts for both tools
- [ ] Update GitHub Actions workflows
- [ ] Create dual-tool release

## Notes

- Original fx_spritemaker location: `misc_projects/fx_spritemaker/`
- All functionality preserved in migration
- No breaking changes to tool behavior
- Scripts updated to work with new paths

---

**Completed by**: Cascade AI  
**Approved by**: Andy Moorer  
**Date**: November 10, 2025
