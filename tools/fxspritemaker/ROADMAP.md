# VFX Sprite Maker - Roadmap

**Current Version**: 1.0.6  
**Last Updated**: November 10, 2025

This document outlines planned features and improvements for VFX Sprite Maker. Features are organized by priority and complexity.

---

## 🎯 Near-Term Features (v1.1.x - v1.2.x)

### Animation System Enhancements

#### Advanced Curve Types
**Priority**: High  
**Complexity**: Medium

Add parametric animation curve types beyond the current interpolation options:

- **Noise Curves**: Perlin/Simplex noise-driven parameter animation
  - Noise frequency and amplitude controls
  - Seed parameter for reproducibility
  - Use cases: organic motion, jitter effects
  
- **Spring Curves**: Physics-based spring motion
  - Stiffness and damping parameters
  - Natural overshoot and settling behavior
  - Use cases: elastic bounces, impact responses
  
- **Bounce Curves**: Gravity-based bounce animation
  - Bounce height decay
  - Number of bounces control
  - Use cases: falling particles, impact effects

#### Multi-Step Animation
**Priority**: Medium  
**Complexity**: Low

Extend "Stepped" curve to support N steps instead of single step:

- Step count parameter (2-16 steps)
- Even or custom step distribution
- Use cases: flipbook-style animation, retro effects

---

### Sprite Type Improvements

#### New Procedural Types
**Priority**: High  
**Complexity**: Medium-High

**Signed Distance Fields (SDFs)**:
- Crisp edges at any resolution
- Shape morphing capabilities
- Outline and glow effects
- SDF primitives: Circle, Box, Polygon, Star

**Pattern Generators**:
- Checkerboard, stripes, dots
- Radial and grid patterns
- Noise-based patterns (Voronoi, cellular)
- Tiling options

**Random Splatting**:
- Scatter N shapes (lines, circles, etc.) randomly
- Density, size variation, rotation controls
- Seed for reproducibility
- Use cases: debris, sparks, dust particles

#### Geometry Improvements
**Priority**: Medium  
**Complexity**: Medium

- **N-Gon & Star Refinement**: 
  - Move from polar plotting to proper Cartesian geometry
  - Better edge smoothing and anti-aliasing
  - Configurable corner rounding per vertex
  
- **General Sprite Polish**:
  - Improved gradient algorithms
  - Better softness/feathering quality
  - Optimized rendering performance
  - Additional types may include snowflake maker, runes, splash shapes

---

### Asset Import & Atlas Generation

#### Icon Atlas Generator
**Priority**: High  
**Complexity**: Medium

Import `.ico` files and generate sprite atlases:

- Parse multi-resolution .ico files
- Extract each icon size to separate atlas cell
- Automatic grid layout based on icon count
- Preserve transparency and color depth
- Batch import from folder

**Use Cases**: UI icon sheets, toolbar atlases, status indicator sprites

#### Font to Sprite Sheet
**Priority**: High  
**Complexity**: High

Convert font files to image atlases:

- Support TrueType (.ttf) and OpenType (.otf) fonts
- Generate cell per character (ASCII, Unicode ranges)
- Configurable: font size, antialiasing, padding
- Character set selection (ASCII, extended, custom)
- Outline and shadow effects
- Export character mapping data (JSON/CSV)

**Use Cases**: Bitmap fonts for retro games, custom text rendering, particle text effects

---

## 🍒 Low-Hanging Fruit Improvements (v1.0.7 - v1.0.9)

### 1. Parameter Presets System
**Priority**: High  
**Complexity**: Low

- Save current parameters as named preset
- Load presets from dropdown menu
- Export/import preset files (.json)
- Built-in preset library for common effects

### 2. Batch Export
**Priority**: Medium  
**Complexity**: Low

- Export multiple resolutions simultaneously
- Generate variants with parameter ranges
- Example: Export 64x64, 128x128, 256x256, 512x512 in one click

### 3. Keyboard Shortcuts
**Priority**: Medium  
**Complexity**: Low

Common shortcuts to improve workflow:
- `Ctrl+E`: Quick export
- `Ctrl+P`: Generate preview
- `Ctrl+R`: Reset parameters
- `Space`: Play/pause animation
- `Ctrl+C`: Copy current parameters to clipboard
- `Ctrl+V`: Paste parameters from clipboard

### 4. Enhanced Color Picker
**Priority**: Low  
**Complexity**: Low

- Recent colors palette (last 8-12 colors used)
- Hex color code input/display
- Eyedropper to pick color from preview
- Favorite colors list

### 5. Preview Enhancements
**Priority**: Medium  
**Complexity**: Low

- Grid overlay toggle (for alignment reference)
- Zoom controls (50%, 100%, 200%, 400%)
- Pan functionality for zoomed views
- Background pattern options (checkerboard, solid, custom)

### 6. Export Options Expansion
**Priority**: Low  
**Complexity**: Low

- Alpha premultiplication toggle
- PNG compression level control
- JPG quality slider (for non-transparent exports)
- Metadata embedding (tool version, parameters)

### 7. Post processing
**Priority**: Mid  
**Complexity**: Mid

- Convolution/filters (glow, blur, posterize, threshold)
- Edge handling (edge fade and alpha vignette)
- Color control and packing

---

## 🔮 Future Considerations (v1.3.x+)

### Advanced Features
- **3D Sprites**: Simple 3D primitives (sphere, cube) with lighting
- **6-way lighting**
- **Additional maps** Alpha remap, grads, normal, depth
- **Custom Shaders**: GLSL shader support for advanced users
- **Python Scripting**: Scriptable parameter automation

### Integration Features
- **Plugin System**: Community-contributed sprite types
- **API Mode**: Command-line batch processing
- AI support including CLI tools to Claude skills and MCP

---

## 🤝 Community Input

Feature requests and suggestions are welcome! Please open an issue on GitHub with:
- **Feature Description**: What you'd like to see
- **Use Case**: How you'd use it
- **Priority**: How important it is to your workflow

<img width="171" height="256" alt="AMcharHappy_Square256" src="https://github.com/user-attachments/assets/9b2b72de-2980-4cab-966d-cc8dbcda9a7e" />

---

## 📝 Notes

- Features may shift between versions based on complexity and user demand
- Breaking changes will be avoided in minor version updates
- Major version updates (v2.0+) may include architectural changes

**Roadmap Status**: Active Development  
**Next Milestone**: v1.0.7 (Low-hanging fruit improvements)

---

*This roadmap is subject to change based on development priorities, community feedback, technical feasibility and the entirely unpredictable whims of the author who needs to spend less time coding and more time hanging out with his rescue dogs.*
