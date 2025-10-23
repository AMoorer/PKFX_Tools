# PKFX_Tools

Tools and utilities for PKFX (PopcornFX) development.

## 🎨 MakeSomeNoise - Procedural Noise Generator

A powerful, user-friendly GUI tool for generating seamless procedural noise textures with real-time preview and animation support.

### ✨ Features

- **7 Noise Types**: Perlin, Simplex, FBM, Turbulence, Ridged Multifractal, Domain Warp, 3D Slice
- **Seamless Tiling**: Industry-standard offset-based blending for perfect texture tiling
- **Dual Layer Mixing**: Blend two noise types with multiple blend modes (Mix, Add, Multiply, Screen, Overlay)
- **Real-Time Preview**: Live 256×256 preview with adjustable parameters
- **Animation Support**: Generate animated texture atlases with customizable frame counts and layouts
- **Batch Export**: Export at any resolution (up to 4096×4096) in PNG or TIFF format
- **3D Offset Controls**: Navigate through noise space with X/Y/Z offsets and adjustable sensitivity
- **Preview Seams**: Visual verification tool to ensure seamless tiling

### 📥 Download

**For End Users:**
1. Go to [Releases](../../releases)
2. Download the latest `MakeSomeNoise.exe`
3. Double-click to run - no installation required!

**Requirements:** Windows 10/11 (64-bit)

### 🛠️ For Developers

#### Setup Development Environment

```powershell
# Clone the repository
git clone https://github.com/AMoorer/PKFX_Tools.git
cd PKFX_Tools

# Run setup script (creates venv and installs dependencies)
.\setup_env.ps1

# Launch the GUI
.\run_noise_gui.ps1
```

#### Build Executable

```powershell
# Quick build
.\build_executable.ps1

# Or manually
.\venv\Scripts\Activate.ps1
pyinstaller MakeSomeNoise.spec --clean
```

See [BUILD_README.md](BUILD_README.md) for detailed build instructions and troubleshooting.

### 📖 Usage

#### Basic Workflow

1. **Select Noise Type**: Choose from Layer A dropdown
2. **Adjust Parameters**: 
   - Scale: Base frequency of noise
   - Octaves: Level of detail (more = finer details)
   - Persistence: How much each octave contributes
   - Lacunarity: Frequency multiplier between octaves
3. **Enable Seamless Tiling**: Check the box and adjust Blend Width (10-30%)
4. **Preview Seams**: Toggle to visualize tiling with 50% offset
5. **Export**: Click "Export Noise" and choose resolution & format

#### Advanced Features

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

### 🎯 Use Cases

- **Game Development**: Seamless terrain heightmaps, normal maps, detail textures
- **VFX**: Procedural textures for materials and effects
- **PopcornFX**: Custom texture inputs for particle effects
- **Prototyping**: Quick texture generation for mockups

### 📋 Noise Types

| Type | Description | Best For |
|------|-------------|----------|
| **Perlin** | Classic smooth noise | Natural terrain, clouds |
| **Simplex** | Improved Perlin, fewer artifacts | Modern terrain, organics |
| **FBM** | Fractional Brownian Motion | Realistic terrain, mountains |
| **Turbulence** | Absolute value FBM | Fire, smoke, energy effects |
| **Ridged** | Inverted ridges | Mountain ridges, veins |
| **Domain Warp** | Warped noise space | Twisted, organic patterns |
| **3D Slice** | Slice through 3D noise | Animated flowing textures |

### 🐛 Troubleshooting

**Executable won't start:**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Check Windows Defender isn't blocking it
- See [TROUBLESHOOT_EXE.md](TROUBLESHOOT_EXE.md)

**Seams visible in tiled texture:**
- Increase "Blend Width" to 15-30%
- Use "Preview Seams" to verify
- Ensure "Seamless Tiling" is enabled

**Python script errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### 🏗️ Project Structure

```
PKFX_Tools/
├── tools/
│   └── noise_generator_gui.py    # Main application
├── build_executable.ps1           # Build script
├── MakeSomeNoise.spec            # PyInstaller config
├── BUILD_README.md               # Build documentation
├── TROUBLESHOOT_EXE.md          # Troubleshooting guide
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### 📜 License

See [LICENSE](LICENSE) file for details.

### 🙏 Credits

- **Author**: Andy Moorer
- **Built with**: PySide6, NumPy, noise, opensimplex, perlin-noise, Pillow
- **Algorithm References**: Ken Perlin, Stefan Gustavson

### 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**Version**: 1.0.0  
**Last Updated**: October 2025
