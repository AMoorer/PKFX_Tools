# MakeSomeNoise - Procedural Noise Generator

A powerful, user-friendly GUI tool for generating seamless procedural noise textures with real-time preview and animation support.

![Version](https://img.shields.io/badge/version-1.1.2-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-See%20LICENSE-green)

## ✨ Features

- **6 Noise Algorithms**: Perlin, Simplex, FBM, Turbulence, Ridged Multifractal, Domain Warp
- **Seamless Tiling**: Industry-standard offset-based blending for perfect texture tiling
- **Dual Layer Blending**: Mix two noise types with 7 blend modes (Mix, Add, Multiply, Screen, Overlay, Min, Max)
- **Real-Time Preview**: Live preview with adjustable parameters and smooth animation playback
- **Animation Support**: Generate animated texture atlases or frame sequences with Z-offset progression
- **Multiple Export Formats**: Single frame, animation atlas, or file sequence
- **3D Offset Controls**: Navigate through noise space with X/Y/Z offsets and adjustable sensitivity
- **Preview Verification**: Center Seams mode to inspect seamless tiling quality
- **Automatic Versioning**: Incremental version numbers (_v00, _v01...) prevent overwriting
- **Educational Guide**: Built-in comprehensive guide with detailed algorithm explanations and history

## 📥 Download

**For End Users:**
1. Go to [Releases](../../../../releases)
2. Download the latest `MakeSomeNoise.exe`
3. Double-click to run - no installation required!

**Requirements:** Windows 10/11 (64-bit)

## 🛠️ For Developers

### Setup Development Environment

```powershell
# From PKFX_Tools root
cd tools/makesomenoise

# Run setup script (creates venv and installs dependencies)
.\scripts\setup_env.ps1

# Launch the GUI
.\scripts\run_noise_gui.ps1
```

### Build Executable

```powershell
# Quick build
.\scripts\build_executable.ps1

# Or manually
.\venv\Scripts\Activate.ps1
pyinstaller VFXSpriteMaker.spec --clean
```

## 📖 Usage

### Basic Workflow

1. **Select Noise Type**: Choose from Layer A dropdown
2. **Adjust Parameters**: 
   - Scale: Base frequency of noise
   - Octaves: Level of detail (more = finer details)
   - Persistence: How much each octave contributes
   - Lacunarity: Frequency multiplier between octaves
3. **Enable Seamless Tiling**: Check the box and adjust Blend Width (10-30%)
4. **Preview Seams**: Toggle to visualize tiling with 50% offset
5. **Export**: Click "Export Noise" and choose resolution & format

### Advanced Features

**Layer Mixing:**
- Set Layer B to a different noise type
- Adjust Mix Weight slider (0=all A, 1=all B)
- Choose blend mode for creative effects

**Animation:**
- Enable "Animated Output"
- Set frame count and atlas layout
- Adjust "Noise Anim Rate" for speed
- Export creates an animated texture atlas

**3D Navigation:**
- Use X/Y/Z offset sliders to explore noise space
- Adjust sensitivity for fine/coarse control
- Perfect for finding interesting regions

## 🎯 Use Cases

- **Game Development**: Seamless terrain heightmaps, normal maps, detail textures
- **VFX**: Procedural textures for materials and effects
- **PopcornFX**: Custom texture inputs for particle effects
- **Prototyping**: Quick texture generation for mockups

## 📋 Noise Types

| Type | Description | Best For |
|------|-------------|----------|
| **Perlin** | Classic smooth noise | Natural terrain, clouds |
| **Simplex** | Improved Perlin, fewer artifacts | Modern terrain, organics |
| **FBM** | Fractional Brownian Motion | Realistic terrain, mountains |
| **Turbulence** | Absolute value FBM | Fire, smoke, energy effects |
| **Ridged** | Inverted ridges | Mountain ridges, veins |
| **Domain Warp** | Warped noise space | Twisted, organic patterns |

*All noise types support 3D offset animation for temporal continuity*

## 🐛 Troubleshooting

**Executable won't start:**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Check Windows Defender isn't blocking it

**Seams visible in tiled texture:**
- Increase "Blend Width" to 15-30%
- Use "Preview Seams" to verify
- Ensure "Seamless Tiling" is enabled

**Python script errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## 🏗️ Project Structure

```
makesomenoise/
├── src/
│   └── makesomenoise/
│       ├── __init__.py
│       ├── __main__.py
│       ├── noise_generator_gui.py   # Main application
│       └── version.py
├── scripts/
│   ├── build_executable.ps1         # Build script
│   ├── run_noise_gui.ps1           # Launch script
│   └── setup_env.ps1               # Environment setup
├── VFXSpriteMaker.spec             # PyInstaller config
└── README.md                        # This file
```

## 🙏 Credits

- **Author**: Andy Moorer
- **Built with**: PySide6, NumPy, noise, opensimplex, perlin-noise, Pillow
- **Algorithm References**: Ken Perlin, Stefan Gustavson

---

**Version**: 1.1.2  
**Last Updated**: October 24, 2025

[← Back to PKFX Tools](../../README.md)
