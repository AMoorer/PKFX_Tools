# PKFX Tools

A collection of tools and utilities for PKFX (PopcornFX) and general VFX development.

<img width="320" height="480" alt="AMcharThumbs_phonesize" src="https://github.com/user-attachments/assets/bcee49e6-79dd-473a-a804-58999e2ca527" />

## 🛠️ Available Tools

### 🎨 [MakeSomeNoise](tools/makesomenoise/) - Procedural Noise Generator

A powerful GUI tool for generating seamless procedural noise textures with real-time preview and animation support.

**Key Features:**
- 6 noise algorithms (Perlin, Simplex, FBM, Turbulence, Ridged, Domain Warp)
- Seamless tiling with adjustable blend width
- Dual-layer blending with 7 blend modes
- 3D offset controls and animation
- Atlas and sequence export

[Download Latest Release](../../releases) | [View Documentation](tools/makesomenoise/README.md)

---

### ✨ [VFX Sprite Maker](tools/fxspritemaker/) - Procedural Sprite Generator

Create high-quality VFX sprites with full animation and color control.

**Key Features:**
- 10+ sprite types (Circle, Star, Particle, Lightning, Smoke, etc.)
- Real-time parameter animation with multiple curves
- Color animation with RGB transitions
- Atlas export with flexible grid layouts
- Export from 64×64 to 1024×1024+

[Download Latest Release](../../releases) | [View Documentation](tools/fxspritemaker/README.md)

---

## 📥 Quick Start

### For End Users

1. Go to [Releases](../../releases)
2. Download the tool executable you need
3. Run directly - no installation required!

**Requirements:** Windows 10/11 (64-bit)

### For Developers

Each tool has its own development environment:

```powershell
# Clone repository
git clone https://github.com/AMoorer/PKFX_Tools.git
cd PKFX_Tools

# Choose a tool
cd tools/makesomenoise    # or tools/fxspritemaker

# Setup environment
.\scripts\setup_env.ps1

# Run the tool
.\scripts\run_noise_gui.ps1    # or run_sprite_gui.ps1
```

## 🏗️ Repository Structure

```
PKFX_Tools/
├── tools/
│   ├── makesomenoise/         # Noise texture generator
│   │   ├── src/
│   │   ├── scripts/
│   │   └── README.md
│   └── fxspritemaker/         # VFX sprite generator
│       ├── src/
│       ├── scripts/
│       └── README.md
├── docs/                      # Shared documentation
├── .github/                   # CI/CD workflows
├── LICENSE
└── README.md                  # This file
```

## 🤝 Contributing

Contributions are welcome! To add a new tool or improve existing ones:

1. Fork the repository
2. Create a feature branch
3. Add your tool under `tools/yourtool/`
4. Follow the existing structure (src/, scripts/, README.md)
5. Update this main README to list your tool
6. Submit a pull request

## 📚 Documentation

- **Tool-Specific Docs**: See each tool's README for detailed documentation
- **Build Instructions**: Check `docs/BUILD_README.md`
- **Troubleshooting**: See `docs/TROUBLESHOOT_EXE.md`
- **Version History**: View tool-specific changelogs

## 📜 License

See [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Author**: Andy Moorer
- **Built with**: PySide6, NumPy, Pillow, noise libraries
- **Purpose**: Tools for PKFX (PopcornFX) and VFX development

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**MakeSomeNoise**: v1.1.2  
**VFX Sprite Maker**: v1.0.6  
**Last Updated**: November 10, 2025

See individual tool READMEs for detailed version history and changelogs.
