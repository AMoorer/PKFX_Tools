# Procedural Noise Examples

This directory contains comprehensive examples of procedural noise generation for technical art, VFX, and game development.

## Quick Start

### Run Examples

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run 2D noise examples
python examples\noise_examples.py

# Run 3D/animated noise examples
python examples\noise_3d_example.py
```

## Noise Types Included

### 1. **Perlin Noise** (`noise` library)
- Classic gradient noise algorithm
- Great for: Terrain, clouds, general-purpose textures
- Features: Octaves, persistence, lacunarity control

### 2. **Simplex Noise** (`opensimplex` library)
- Faster than Perlin, fewer directional artifacts
- Great for: Real-time generation, smooth gradients
- Better for: Higher dimensions (3D/4D)

### 3. **FBM (Fractional Brownian Motion)** (`perlin-noise` library)
- Layered noise for natural-looking results
- Great for: Terrain heightmaps, organic textures
- Easy octave control

### 4. **Turbulence**
- Absolute value of noise
- Great for: Fire, explosions, marble, wood grain
- Creates sharp, energetic patterns

### 5. **Ridged Multifractal**
- Inverted noise for sharp ridges
- Great for: Mountain ranges, veins, cracks, lightning
- Perfect for dramatic terrain

### 6. **Domain Warping**
- Noise sampled at distorted coordinates
- Great for: Clouds, water, swirls, organic patterns
- Creates flowing, natural distortions

### 7. **Curl Noise**
- Divergence-free vector field
- Great for: Fluid simulation, particle advection
- Makes particles flow naturally without clustering

### 8. **3D Animated Noise**
- Time-varying noise for motion
- Great for: Animated textures, volumetric effects
- Smooth temporal coherence

## Parameters Explained

### Scale
- Lower values = more zoomed in (larger features)
- Higher values = more zoomed out (smaller features)
- Typical range: 50-300

### Octaves
- Number of noise layers combined
- More octaves = more detail
- Typical range: 4-8
- Each octave adds computational cost

### Persistence
- How much each octave contributes
- Range: 0.0-1.0
- Lower = smoother, Higher = rougher
- Default: 0.5

### Lacunarity
- Frequency multiplier between octaves
- Range: 1.5-4.0
- Higher = more frequency variation
- Default: 2.0

## Use Cases by Industry

### **VFX / Technical Art**
- **Fire/Explosions**: Turbulence + hot colormap + animation
- **Smoke**: 3D animated simplex + curl noise advection
- **Clouds**: Domain warped simplex
- **Energy Fields**: Animated 3D noise + glow
- **Magic Effects**: Turbulence + color gradients

### **Game Development**
- **Terrain Generation**: FBM for heightmaps + terrain colormap
- **Procedural Textures**: Perlin/simplex for runtime generation
- **Particle Systems**: Curl noise for natural particle flow
- **Weather Effects**: 3D animated noise for rain/snow patterns
- **Procedural Materials**: Layered noise for variation

### **Level Design**
- **Cave Systems**: Ridged multifractal thresholding
- **Biome Blending**: Multiple noise layers with different scales
- **Resource Distribution**: Thresholded noise for placement
- **Path Generation**: Curl noise for natural winding paths

### **VR / Real-Time**
- **Procedural Skyboxes**: Animated clouds with domain warping
- **Dynamic Weather**: 3D noise slicing for volumetrics
- **Shader Effects**: GPU-based noise in HLSL/GLSL
- **Optimization**: Pre-bake textures vs. runtime generation

## Integration Tips

### **Export to Game Engines**

```python
# Save as texture
save_noise_as_image(noise_map, "terrain_heightmap.png")

# For Unity/Unreal: Export as 16-bit for better precision
img_16bit = (noise_map * 65535).astype(np.uint16)
Image.fromarray(img_16bit, mode='I;16').save("heightmap_16bit.png")
```

### **GPU Shader Implementation**

The noise algorithms can be ported to HLSL/GLSL:
- Use GPU for real-time generation
- Sample 3D noise in vertex/pixel shaders
- Animate with time parameter

### **PopcornFX Integration**

```python
# Export noise as texture atlas for particle systems
# Use curl noise for particle velocity fields
# Generate sprite sheet variations
```

## Performance Tips

1. **Pre-bake when possible**: Generate once, reuse many times
2. **Use Simplex over Perlin**: ~30% faster
3. **Reduce octaves**: Start with 4, add more only if needed
4. **Cache results**: Store noise maps for reuse
5. **GPU acceleration**: Port to shaders for real-time use

## Advanced Techniques

### **Multi-Octave Blending**
```python
base = generate_simplex_noise_2d(scale=200)
detail = generate_perlin_noise_2d(scale=50, octaves=8)
combined = base * 0.7 + detail * 0.3
```

### **Threshold Masking**
```python
noise = generate_fbm_noise()
mask = (noise > 0.6).astype(float)  # Create islands/continents
```

### **Color Mapping**
```python
# Use noise to drive color palettes
for y in range(height):
    for x in range(width):
        val = noise_map[y, x]
        color = interpolate_color(palette, val)
```

## Resources

- **Perlin Noise**: Ken Perlin's original paper
- **Simplex Noise**: Improvement over Perlin (fewer grid artifacts)
- **Book**: "Texturing & Modeling: A Procedural Approach"
- **GPU Gems**: Chapter on noise in shaders
- **shadertoy.com**: Real-time shader examples

## Next Steps

1. Run the example scripts to see output
2. Experiment with parameters
3. Combine multiple noise types
4. Export textures to your game engine
5. Port algorithms to HLSL/GLSL for real-time use

## Questions?

Check the inline documentation in:
- `noise_examples.py` - 2D noise types
- `noise_3d_example.py` - 3D and animated noise
