# Changelog

All notable changes to MakeSomeNoise will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-10-24

### Added
- **Built-in Educational Guide**: Comprehensive "A Guide To Noise" with detailed explanations for each algorithm
  - Historical background for each noise type
  - Technical algorithm explanations
  - Key parameter descriptions
  - Use cases and characteristics
  - Pro tips for each noise type
  - General usage guide with workflow and best practices
- **Comprehensive Tooltips**: Hover help for all controls and parameters
- **Right-Click Context Menu**: Quick access to export options and guide from anywhere in the app
- **Copy Preview to Clipboard**: Right-click menu option to copy current preview
- **Open Save Location**: Quick access to export directory from context menu
- **Export Preview Modes**: Preview single frames, atlases, or animations before exporting
- **Animation Playback**: Real-time animation preview with adjustable FPS (1-60 FPS)
- **Export Info Display**: Detailed information about preview/export parameters
- **Automatic Version Management**: Files automatically increment version numbers (_v00, _v01, etc.)
- **Full Path Display**: "Save to" field now shows complete file paths
- **Default Export Location**: Pictures/NoiseExports directory auto-created
- **About Dialog**: Application information and feature list

### Changed
- **Removed 3D Slice Noise Type**: Redundant with universal 3D offset support (now 6 noise types)
- All noise algorithms now support X/Y/Z offset animation with sensitivity control
- **Export Format Options**: Three distinct modes - Single Frame, Animation Atlas, File Sequence
- **Improved File Naming**: More descriptive folder names for sequence exports
- **Enhanced UI Layout**: Better spacing and organization of controls
- **Tooltip Styling**: Consistent dark theme tooltips across all UI elements
- **Center Seams Labeling**: Renamed from "Preview Seams" for clarity
- **Preview Method Label**: Renamed from "Mode" to "Preview Method" for clarity
- Debounce timers standardized to 300ms for improved stability

### Fixed
- **Worker Thread Management**: Robust interruption handling prevents crashes on rapid parameter changes
- **Animation Preview Text**: Increased display area to prevent text cutoff
- **Tooltip Inheritance**: Prevents color/style bleeding from parent elements
- **Preview State Sync**: Preview dropdown now properly reflects current mode after sequence export
- **Memory Management**: Proper cleanup of animation frames and worker threads
- **UI Responsiveness**: Non-blocking operations with proper status feedback

### Technical Improvements
- Optimized noise generation with proper thread interruption points
- Better memory management for animation frame storage
- Cleaner separation of UI and computation logic
- Consistent error handling across all export modes
- Improved code documentation and structure

## [1.0.0] - 2025-10-XX

### Initial Release
- **6 Noise Algorithms**: Perlin, Simplex, FBM, Turbulence, Ridged, Domain Warp
- **Dual-Layer Blending**: 7 blend modes (Mix, Add, Multiply, Screen, Overlay, Min, Max)
- **Seamless Tiling**: Industry-standard boundary blending
- **Real-Time Preview**: Live 256×256 preview
- **Animation Support**: Atlas and sequence export
- **3D Offset Controls**: Navigate noise space with X/Y/Z offsets
- **Parameter Controls**: Full control over scale, octaves, persistence, lacunarity, seed, power, warp strength
- **Multiple Export Formats**: PNG support up to 4096×4096
- **Preview Seam Mode**: Verify seamless tiling quality

---

## Version Numbering

MakeSomeNoise follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes or major feature overhauls
- **MINOR** version: New functionality in a backwards compatible manner
- **PATCH** version: Bug fixes and minor improvements

## Categories

Changes are grouped into these categories:
- **Added**: New features
- **Changed**: Changes to existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
- **Technical Improvements**: Under-the-hood enhancements
