# MakeSomeNoise - Development Roadmap

**Current Version**: 1.1.2  
**Last Updated**: October 24, 2025  
**Status**: Actively Developed

---

## Version History & Future Releases

### ✅ v1.0.0 - Foundation (October 2025)
**Status**: Released

Core functionality and noise algorithms established.

### ✅ v1.1.2 - Enhancement & Education (October 2025)
**Status**: Released

Major UI/UX improvements, educational guide, and export workflow enhancements.

---

## Planned Releases

### 🎯 v1.2.0 - Advanced Features (Q4 2025 / Q1 2026)
**Focus**: Power user features and expanded functionality.

#### Immediate Plans

- [ ] **Noise Types**
  - Add more noise types
     - Worley
     - Manhattan
     - White Noise
     - Alligator
     - Gabor noise
     - Curl noise
     - Billow noise
     - Swiss Noise

- [ ] **Procedural shapes and patterns with SDF control**
     - Hex Grid
     - Fracture
     - Spots
     - Star
     - Square
     - Circle
     - N-gon
     - Ring
     - Capsule
     - Brick/tile
     - Grid
     - Trigrid
 
- [ ] **Explore SDF Operations**
     - Union
     - Intersection
     - Difference
     - Shell

- [ ] **Explore SDF Modifiers**
     - Bilateral and Radial Symmetry
     - Twist/Bend

- [ ] **Alpha Channel and Transparency support**
     - Output transparent .png files
     - Transparency previewing

- [ ] **Post processing**
     - Normal map generation

- [ ] **Resolution Increase**
     - 1024x1024
     - 2048x2048
     - 4096x4096
     - Consider custom resolutions and non-square output.

#### Medium Priority Features

- [ ] **Color Mapping**
  - Apply gradient maps to noise
  - Preset gradient library
  - Custom gradient editor
  - Export colored textures

- [ ] **Layer System**
  - More than 2 layers
  - Layer visibility toggles
  - Layer reordering
  - Per-layer opacity controls

- [ ] **History/Undo System**
  - Parameter history stack
  - Undo/redo functionality
  - History browser with thumbnails
  - "Compare with previous" feature

#### Wishlist Items

- [ ] **Color Mapping**
  - Apply gradient maps to noise
  - Preset gradient library
  - Custom gradient editor
  - Export colored textures

- [ ] **Layer System**
  - More than 2 layers
  - RGBA Channel Packing

#### Possible v3.0 Features

- [ ] **Preset System**
  - Save/load parameter presets
  - Include community preset library
  - Import/export preset files (.msn format)
  - Preset categories and tags

- [ ] **Batch Export**
  - Export multiple resolutions simultaneously
  - Export multiple file formats at once
  - Queue multiple exports with different parameters
  - Background export with notifications

- [ ] **Enhanced Animation**
  - Looping animation support (seamless temporal wrapping)
  - Custom animation curves for Z-offset
  - Keyframe system for parameter animation
  - Export video formats (MP4, GIF)

- [ ] **Additional Export Formats**
  - TIFF support (8-bit, 16-bit)
  - OpenEXR for VFX workflows

---

## Implementation Notes

### Noise Type Implementation Guide

#### Voronoi/Worley Noise
**Implementation**:
```python
@staticmethod
def _voronoi(w, h, p, seamless=False, blend_width=0.1):
    noise_map = np.zeros((h, w), dtype=np.float32)
    scale = p['scale']
    seed = int(p['seed'])
    distance_metric = p.get('metric', 'euclidean')  # euclidean, manhattan, chebyshev
    
    # Generate random feature points
    np.random.seed(seed)
    num_points = int((w * h) / (scale * scale))
    
    for y in range(h):
        for x in range(w):
            min_dist = float('inf')
            # Check distances to all feature points
            for point in feature_points:
                dist = calculate_distance(x, y, point, distance_metric)
                min_dist = min(min_dist, dist)
            noise_map[y][x] = min_dist
    
    # Normalize to 0-1
    result = noise_map / noise_map.max()
    if seamless:
        result = NoiseGenerator.make_seamless_blend(result, blend_width)
    return result
```
**Parameters**: scale, seed, metric (euclidean/manhattan/chebyshev), invert
**Use Cases**: Cells, stone, caustics, cracked surfaces

#### White Noise
**Implementation**:
```python
@staticmethod
def _white_noise(w, h, p, seamless=False, blend_width=0.1):
    seed = int(p['seed'])
    np.random.seed(seed)
    noise_map = np.random.rand(h, w).astype(np.float32)
    # Note: White noise is not naturally seamless
    return noise_map
```
**Parameters**: seed only
**Use Cases**: Dithering, grain, random seeds for other effects

#### Billowed Noise
**Implementation**:
```python
@staticmethod
def _billow(w, h, p, seamless=False, blend_width=0.1):
    # Similar to FBM but with absolute values
    noise_map = np.zeros((h, w), dtype=np.float32)
    scale = p['scale']
    octaves = int(p['octaves'])
    persistence = p['persistence']
    lacunarity = p['lacunarity']
    seed = int(p['seed'])
    
    amplitude = 1.0
    frequency = 1.0
    
    for octave in range(octaves):
        for y in range(h):
            for x in range(w):
                val = noise.pnoise2(x/scale * frequency, y/scale * frequency, 
                                   octaves=1, base=seed)
                noise_map[y][x] += abs(val) * amplitude  # abs() creates billow effect
        
        amplitude *= persistence
        frequency *= lacunarity
    
    # Normalize
    result = noise_map / noise_map.max()
    if seamless:
        result = NoiseGenerator.make_seamless_blend(result, blend_width)
    return result
```
**Parameters**: scale, octaves, persistence, lacunarity, seed
**Use Cases**: Puffy clouds, cotton, soft organic surfaces

#### Curl Noise
**Implementation**:
```python
@staticmethod
def _curl_noise(w, h, p, seamless=False, blend_width=0.1):
    # Curl noise requires computing derivatives
    scale = p['scale']
    seed = int(p['seed'])
    epsilon = 0.01
    
    noise_map = np.zeros((h, w), dtype=np.float32)
    
    for y in range(h):
        for x in range(w):
            # Compute gradients using central differences
            dx = noise.pnoise2((x+epsilon)/scale, y/scale, base=seed) - \
                 noise.pnoise2((x-epsilon)/scale, y/scale, base=seed)
            dy = noise.pnoise2(x/scale, (y+epsilon)/scale, base=seed) - \
                 noise.pnoise2(x/scale, (y-epsilon)/scale, base=seed)
            
            # Curl is perpendicular gradient (swirl effect)
            curl = np.sqrt(dx*dx + dy*dy)
            noise_map[y][x] = curl
    
    # Normalize
    result = noise_map / noise_map.max()
    if seamless:
        result = NoiseGenerator.make_seamless_blend(result, blend_width)
    return result
```
**Parameters**: scale, seed
**Use Cases**: Fluid flow, swirls, turbulent patterns

### SDF Implementation Guide

#### Basic Circle SDF
**Implementation**:
```python
@staticmethod
def _sdf_circle(w, h, p, seamless=False, blend_width=0.1):
    cx, cy = w/2, h/2  # Center
    radius = p.get('radius', min(w, h) / 4)
    softness = p.get('softness', 2.0)  # Edge feathering
    
    noise_map = np.zeros((h, w), dtype=np.float32)
    
    for y in range(h):
        for x in range(w):
            # Distance from center
            dx = x - cx
            dy = y - cy
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Signed distance (negative inside, positive outside)
            sdf = dist - radius
            
            # Convert to 0-1 with soft edge
            value = 1.0 / (1.0 + np.exp(sdf / softness))
            noise_map[y][x] = value
    
    return noise_map
```
**Parameters**: radius, softness, center_x, center_y
**Use Cases**: Radial masks, vignettes, circular patterns

#### Hexagonal Grid SDF
**Implementation**:
```python
@staticmethod
def _sdf_hexgrid(w, h, p, seamless=False, blend_width=0.1):
    scale = p['scale']
    thickness = p.get('thickness', 0.1)
    
    noise_map = np.zeros((h, w), dtype=np.float32)
    
    # Hexagonal grid constants
    hex_size = scale
    
    for y in range(h):
        for x in range(w):
            # Convert to hexagonal coordinates
            q = (x * np.sqrt(3)/3 - y/3) / hex_size
            r = (y * 2/3) / hex_size
            
            # Find nearest hex center
            # ... hexagonal rounding logic ...
            
            # Calculate distance to hex edges
            dist = calculate_hex_distance(q, r)
            
            # Threshold at thickness
            value = 1.0 if dist < thickness else 0.0
            noise_map[y][x] = value
    
    if seamless:
        result = NoiseGenerator.make_seamless_blend(noise_map, blend_width)
        return result
    return noise_map
```
**Parameters**: scale, thickness, softness
**Use Cases**: Honeycomb patterns, cellular grids, mesh overlays

#### Box SDF
**Implementation**:
```python
@staticmethod
def _sdf_box(w, h, p, seamless=False, blend_width=0.1):
    box_w = p.get('box_width', w/3)
    box_h = p.get('box_height', h/3)
    roundness = p.get('roundness', 0.0)  # 0 = sharp, >0 = rounded
    softness = p.get('softness', 2.0)
    
    cx, cy = w/2, h/2
    noise_map = np.zeros((h, w), dtype=np.float32)
    
    for y in range(h):
        for x in range(w):
            # Distance from center
            dx = abs(x - cx) - box_w/2
            dy = abs(y - cy) - box_h/2
            
            # Box SDF with optional rounding
            outside_dist = np.sqrt(max(dx, 0)**2 + max(dy, 0)**2)
            inside_dist = min(max(dx, dy), 0)
            sdf = outside_dist + inside_dist - roundness
            
            # Soft threshold
            value = 1.0 / (1.0 + np.exp(sdf / softness))
            noise_map[y][x] = value
    
    return noise_map
```
**Parameters**: box_width, box_height, roundness, softness
**Use Cases**: Frames, tiles, rectangular masks, UI elements

### SDF Operations Implementation

#### Union (Combine Shapes)
```python
def sdf_union(sdf_a, sdf_b):
    """Combine two SDFs - shows both shapes"""
    return np.minimum(sdf_a, sdf_b)
```

#### Intersection (Overlap Only)
```python
def sdf_intersection(sdf_a, sdf_b):
    """Only show where both SDFs overlap"""
    return np.maximum(sdf_a, sdf_b)
```

#### Subtraction (Cut Out)
```python
def sdf_subtraction(sdf_a, sdf_b):
    """Cut sdf_b out of sdf_a"""
    return np.maximum(sdf_a, -sdf_b)
```

#### Smooth Union (Organic Blend)
```python
def sdf_smooth_union(sdf_a, sdf_b, k=0.1):
    """Smoothly blend two SDFs"""
    h = np.clip(0.5 + 0.5 * (sdf_b - sdf_a) / k, 0.0, 1.0)
    return sdf_b * (1 - h) + sdf_a * h - k * h * (1 - h)
```

### Architecture Recommendations

#### 1. Extend NoiseGenerator Class
Add new noise types as static methods following existing pattern:
```python
@staticmethod
def _voronoi(w, h, p, seamless=False, blend_width=0.1):
    # Implementation
    pass
```

#### 2. Create Separate SDFGenerator Class
```python
class SDFGenerator:
    """Handles all SDF shape generation."""
    
    @staticmethod
    def circle(w, h, params):
        pass
    
    @staticmethod
    def box(w, h, params):
        pass
    
    # Operations
    @staticmethod
    def union(sdf_a, sdf_b):
        return np.minimum(sdf_a, sdf_b)
```

#### 3. Update UI Structure
Add dropdown for shape/pattern selection:
```python
self.shape_combo = QComboBox()
self.shape_combo.addItems([
    'Circle', 'Box', 'Ring', 'Star', 'N-gon',
    'Hex Grid', 'Brick', 'Line'
])
```

#### 4. Parameter Visibility System
Extend existing param_visibility dict:
```python
self.sdf_param_visibility = {
    'Circle': ['radius', 'softness', 'center_x', 'center_y'],
    'Box': ['box_width', 'box_height', 'roundness', 'softness'],
    'Hex Grid': ['scale', 'thickness', 'softness'],
    # etc.
}
```

### Alpha Channel Implementation

#### Modify Export Functions
```python
def export_with_alpha(noise_map, alpha_map, filename):
    """Export RGBA PNG with alpha channel"""
    # Convert grayscale to RGB
    rgb = np.stack([noise_map, noise_map, noise_map], axis=2)
    
    # Add alpha channel
    rgba = np.dstack([rgb, alpha_map])
    
    # Convert to uint8
    rgba_uint8 = (rgba * 255).astype(np.uint8)
    
    # Save with PIL
    img = Image.fromarray(rgba_uint8, mode='RGBA')
    img.save(filename, 'PNG')
```

#### UI Addition
Add checkbox for alpha mode:
```python
self.alpha_checkbox = QCheckBox("Enable Alpha Channel")
self.alpha_source_combo = QComboBox()
self.alpha_source_combo.addItems([
    'Layer A', 'Layer B', 'Blended Result', 'Inverted'
])
```

### Normal Map Generation

```python
@staticmethod
def generate_normal_map(heightmap, strength=1.0):
    """Convert heightmap to normal map"""
    h, w = heightmap.shape
    
    # Sobel filters for gradients
    dx = np.zeros_like(heightmap)
    dy = np.zeros_like(heightmap)
    
    dx[1:-1, 1:-1] = (heightmap[1:-1, 2:] - heightmap[1:-1, :-2]) / 2.0
    dy[1:-1, 1:-1] = (heightmap[2:, 1:-1] - heightmap[:-2, 1:-1]) / 2.0
    
    # Apply strength
    dx *= strength
    dy *= strength
    
    # Calculate normals
    normal_map = np.zeros((h, w, 3), dtype=np.float32)
    normal_map[:,:,0] = -dx  # X (red)
    normal_map[:,:,1] = -dy  # Y (green)
    normal_map[:,:,2] = 1.0  # Z (blue)
    
    # Normalize
    length = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
    normal_map /= length
    
    # Convert to 0-1 range for image export
    normal_map = (normal_map + 1.0) * 0.5
    
    return normal_map
```

### Performance Considerations

1. **Vectorization**: Use NumPy broadcasting instead of nested loops where possible
2. **Caching**: Cache computed SDFs for reuse
3. **Progressive Rendering**: For large resolutions, render in tiles
4. **GPU Option**: Consider CuPy for GPU acceleration in future versions

### Testing Checklist

- [ ] Verify all noise types produce expected patterns
- [ ] Test seamless tiling for each type
- [ ] Validate parameter ranges prevent crashes
- [ ] Check memory usage with large resolutions
- [ ] Test SDF operations combinations
- [ ] Verify alpha channel export works correctly
- [ ] Test normal map generation quality

---

## Platform Expansion

### Current Platform
- Windows 10/11 (64-bit)

### Future Platforms
- [ ] macOS (M1/M2 and Intel)
- [ ] Web version (WebAssembly)
- [ ] Mobile (iOS/Android)

---

## Known Limitations

### Current Constraints
1. **Maximum Resolution**: 4096×4096 (memory constrained)
2. **Color Depth**: 8-bit grayscale only
3. **File Formats**: PNG only
4. **Platforms**: Windows only
5. **Processing**: CPU-only (no GPU acceleration)

### Planned Solutions
- Tiled generation for larger images (v1.2.0)
- 16-bit and float support (v1.2.0)
- Additional formats (v1.2.0)
- Cross-platform support (v1.3.0)
- GPU acceleration (v1.3.0)

---

## Versioning

MakeSomeNoise follows semantic versioning:
- **Major versions** (2.0.0): May include breaking changes
- **Minor versions** (1.X.0): New features, backwards compatible
- **Patch versions** (1.1.X): Bug fixes, no breaking changes

---

## Contributing

I welcome contributions! (I mean code collaboration but money is nice too...)

### Areas Needing Help
- Algorithm implementations
- Testing and quality assurance
- Documentation and tutorials
- Translation and localization

---

## Success Metrics

### Current
- ✅ Stable release (1.1.2)
- ✅ Core features complete
- ✅ Educational guide implemented
- ✅ Zero crash testing

---

## Resources & Dependencies

### Current Tech Stack
- **GUI**: PySide6 (Qt 6)
- **Computation**: NumPy
- **Noise**: noise, opensimplex, perlin-noise
- **Image**: Pillow (PIL)
- **Build**: PyInstaller

### Future Considerations
- **GPU**: CuPy, PyOpenCL
- **Web**: Emscripten, WebAssembly
- **Database**: SQLite (for presets)
- **Cloud**: AWS S3, Cloudflare Workers

---

## Questions & Discussion

**Have ideas or feedback?**
- Open a [GitHub Discussion](../../discussions)
- Submit a [Feature Request](../../issues/new?template=feature_request.md)
- Email: [andymoorer@gmail.com]

---

**Roadmap Version**: 1.0
**Maintainer**: Andy Moorer
