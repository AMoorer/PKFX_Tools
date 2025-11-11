# VFX Sprite Maker - Procedural Sprite Generator

A powerful tool for generating procedural VFX sprites with real-time preview and advanced animation support. Create circles, stars, rings, particles, and more with full parameter control and color animation.

![Version](https://img.shields.io/badge/version-1.0.6-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-See%20LICENSE-green)

## ✨ Features

- **10+ Sprite Types**: Circle, Square, N-Gon, Star, Ring, Particle, Line, Lightning, Smoke, Spark
- **Real-Time Preview**: Live preview with instant parameter updates
- **Animation System**: Animate any parameter with multiple interpolation curves
- **Color Animation**: Smooth RGB transitions between start and end colors
- **Atlas Export**: Generate sprite sheets with customizable grid layouts
- **Multiple Resolutions**: Export from 64×64 to 1024×1024 (or higher)
- **Export Modes**: Single sprite, animation atlas, or frame sequence
- **Gradient Support**: Radial gradients for enhanced visual depth
- **Professional UI**: Dark/Light themes with intuitive parameter controls
- **Export Preview**: See exactly what you'll export before saving

## 📥 Download

**For End Users:**
1. Go to [Releases](../../../../releases)
2. Download the latest `VFXSpriteMaker.exe`
3. Double-click to run - no installation required!

**Requirements:** Windows 10/11 (64-bit)

## 🛠️ For Developers

### Setup Development Environment

```powershell
# From PKFX_Tools root
cd tools/fxspritemaker

# Run setup script (creates venv and installs dependencies)
.\scripts\setup_env.ps1

# Launch the GUI
.\scripts\run_sprite_gui.ps1
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

1. **Select Sprite Type**: Choose from dropdown (Circle, Star, Particle, etc.)
2. **Adjust Parameters**:
   - Radius/Size: Overall sprite size
   - Softness: Edge feathering
   - Color: RGB color selection
   - Alpha: Opacity (0-100%)
3. **Preview**: Watch real-time updates in the Preview (Live) panel
4. **Export**: 
   - Choose resolution
   - Select export mode (Single, Atlas, Animation)
   - Click "Export Sprite"

### Animation System

**Animate Any Parameter:**
1. Click the checkbox next to any parameter (Radius, Rotation, etc.)
2. Set Start and End values
3. Choose animation Style: Linear, Ping Pong, or Random
4. Select interpolation Curve: Linear, Ease In/Out, Stepped
5. Generate preview to see animation

**Color Animation:**
1. Check the box next to "Color"
2. Click "Start" to pick starting color
3. Click "End" to pick ending color
4. Export atlas or animation to see smooth color transition

### Export Modes

**Single Sprite:**
- One high-quality sprite at chosen resolution
- Perfect for static effects

**Atlas:**
- Multiple frames in a texture atlas
- Grid layout: Row Only, Column Only, Auto (Square), or Manual
- Cell size and export dimensions clearly displayed

**Animation Preview:**
- Real-time playback of animated sprites
- Adjustable FPS (1-60)
- Preview before exporting

## 🎨 Sprite Types

| Type | Description | Key Parameters |
|------|-------------|----------------|
| **Circle** | Perfect circular gradient | Radius, Softness, Gradient |
| **Square** | Rounded square shapes | Size, Corner Radius, Rotation |
| **N-Gon** | Polygon with N sides | Sides (3-12), Rotation |
| **Star** | Multi-pointed star | Points (3-12), Inner Ratio |
| **Ring** | Hollow ring/donut | Outer/Inner Radius, Thickness |
| **Particle** | Soft particle glow | Radius, Softness, Intensity |
| **Line** | Straight line segment | Length, Thickness, Rotation |
| **Lightning** | Electric arc effect | Segments, Chaos, Thickness |
| **Smoke** | Wispy smoke puff | Size, Turbulence, Blur |
| **Spark** | Energy spark trail | Length, Intensity, Falloff |

## 🎯 Use Cases

- **Game Development**: VFX sprite sheets for particle systems
- **PopcornFX**: Custom sprites for particle effects
- **Motion Graphics**: Animated sprite sequences
- **UI Effects**: Glows, highlights, and indicators
- **Prototyping**: Quick sprite generation for effects testing

## 💡 Pro Tips

**Creating Smooth Animations:**
- Use "Ease In/Out" curve for natural motion
- "Ping Pong" style creates looping effects
- Combine parameter and color animation for richer effects

**Atlas Optimization:**
- Use "Row Only" for horizontal strips (common in engines)
- "Column Only" for vertical strips
- "Auto (Square)" for balanced atlases

**Performance:**
- Export preview shows actual resolution up to 1024px per cell
- Large atlases (4×4 at 1024) will be scaled down in preview
- Final export always uses exact resolution specified

## 🐛 Troubleshooting

**Preview appears small:**
- Check if animation is enabled on parameters
- Ensure resolution is set correctly (256+ recommended)
- Maximize window for larger preview area

**Atlas shows wrong grid:**
- Verify Atlas Mode matches desired layout
- Check Cols/Rows values in Manual mode
- Frame Count must be ≤ (Cols × Rows)

**Export looks different from preview:**
- Export preview shows close approximation (up to 1024px per cell)
- Increase export resolution if preview seems low quality
- Check info label for exact cell size and export dimensions

## 🏗️ Project Structure

```
fxspritemaker/
├── src/
│   └── fxspritemaker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── sprite_generator.py       # Core generation engine
│       ├── sprite_generator_gui.py   # Main GUI application
│       └── version.py
├── scripts/
│   ├── build_executable.ps1         # Build script
│   ├── run_sprite_gui.ps1           # Launch script
│   └── setup_env.ps1               # Environment setup
├── VFXSpriteMaker.spec             # PyInstaller config
└── README.md                        # This file
```

## 📋 Version History

**v1.0.6** (Current)
- Full resolution export preview (up to 1024px per cell)
- Enhanced checkbox visibility with larger indicators
- Optimized space distribution for better preview display
- Improved atlas information labels
- Refined UI spacing and layout proportions

**v1.0.0**
- Initial release
- 10+ sprite types
- Animation system
- Color animation
- Atlas export

## 🙏 Credits

- **Author**: Andy Moorer
- **Built with**: PySide6, NumPy, Pillow (PIL)
- **Inspired by**: PopcornFX particle system needs

---

**Version**: 1.0.6  
**Last Updated**: November 10, 2025

[← Back to PKFX Tools](../../README.md)
