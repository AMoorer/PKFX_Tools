"""
Procedural Noise Library Examples
Demonstrates various noise algorithms for texture generation, terrain, and VFX.
"""

import numpy as np
from PIL import Image
import noise  # Perlin noise
from opensimplex import OpenSimplex
from perlin_noise import PerlinNoise


def generate_perlin_noise_2d(width=512, height=512, scale=100.0, octaves=6, 
                              persistence=0.5, lacunarity=2.0, seed=0):
    """
    Generate 2D Perlin noise texture.
    
    Args:
        width, height: Image dimensions
        scale: Zoom level (lower = more zoomed in)
        octaves: Number of noise layers (more = more detail)
        persistence: Amplitude multiplier per octave (0-1)
        lacunarity: Frequency multiplier per octave
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            # Generate Perlin noise value at this coordinate
            nx = x / scale
            ny = y / scale
            noise_val = noise.pnoise2(
                nx, ny,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=seed
            )
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
    return noise_map


def generate_simplex_noise_2d(width=512, height=512, scale=100.0, seed=0):
    """
    Generate 2D OpenSimplex noise texture.
    Simplex noise is faster and has fewer directional artifacts than Perlin.
    
    Args:
        width, height: Image dimensions
        scale: Zoom level
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    simplex = OpenSimplex(seed=seed)
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            noise_val = simplex.noise2(nx, ny)
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = (noise_map + 1) / 2  # OpenSimplex returns -1 to 1
    return noise_map


def generate_fbm_noise(width=512, height=512, octaves=6, scale=100.0, seed=0):
    """
    Generate Fractional Brownian Motion (FBM) noise using perlin-noise library.
    Great for natural-looking textures and terrain.
    
    Args:
        width, height: Image dimensions
        octaves: Number of octaves (detail levels)
        scale: Zoom level
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    perlin = PerlinNoise(octaves=octaves, seed=seed)
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            noise_val = perlin([nx, ny])
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
    return noise_map


def generate_turbulence(width=512, height=512, scale=100.0, power=2.0, seed=0):
    """
    Generate turbulence pattern (absolute value of Perlin noise).
    Great for marble, wood grain, fire effects.
    
    Args:
        width, height: Image dimensions
        scale: Zoom level
        power: Turbulence intensity
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    simplex = OpenSimplex(seed=seed)
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            # Take absolute value for turbulence effect
            noise_val = abs(simplex.noise2(nx, ny))
            noise_val = noise_val ** power  # Apply power for sharper edges
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = noise_map / noise_map.max()
    return noise_map


def generate_ridged_multifractal(width=512, height=512, octaves=6, scale=100.0, seed=0):
    """
    Generate ridged multifractal noise.
    Perfect for mountain ridges, veins, cracks.
    
    Args:
        width, height: Image dimensions
        octaves: Number of detail layers
        scale: Zoom level
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    simplex = OpenSimplex(seed=seed)
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            amplitude = 1.0
            frequency = 1.0
            result = 0.0
            
            for _ in range(octaves):
                nx = x / scale * frequency
                ny = y / scale * frequency
                
                # Ridge noise: 1 - abs(noise)
                signal = 1.0 - abs(simplex.noise2(nx, ny))
                signal = signal * signal  # Square for sharper ridges
                
                result += signal * amplitude
                
                amplitude *= 0.5
                frequency *= 2.0
            
            noise_map[y][x] = result
    
    # Normalize to 0-1 range
    noise_map = noise_map / noise_map.max()
    return noise_map


def generate_domain_warped(width=512, height=512, scale=100.0, warp_strength=50.0, seed=0):
    """
    Generate domain-warped noise.
    Creates swirly, organic patterns great for clouds, water, energy effects.
    
    Args:
        width, height: Image dimensions
        scale: Zoom level
        warp_strength: How much to distort the noise
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    simplex = OpenSimplex(seed=seed)
    simplex_warp = OpenSimplex(seed=seed + 1)
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            # Generate warp offsets
            nx = x / scale
            ny = y / scale
            
            warp_x = simplex_warp.noise2(nx, ny) * warp_strength
            warp_y = simplex_warp.noise2(nx + 5.2, ny + 1.3) * warp_strength
            
            # Sample noise at warped coordinates
            warped_nx = nx + warp_x / scale
            warped_ny = ny + warp_y / scale
            noise_val = simplex.noise2(warped_nx, warped_ny)
            
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = (noise_map + 1) / 2
    return noise_map


def save_noise_as_image(noise_map, filename, colormap='grayscale'):
    """
    Save noise map as image.
    
    Args:
        noise_map: 2D numpy array (0-1 range)
        filename: Output filename
        colormap: 'grayscale', 'hot', 'cool', or 'terrain'
    """
    # Convert to 8-bit
    img_data = (noise_map * 255).astype(np.uint8)
    
    if colormap == 'grayscale':
        img = Image.fromarray(img_data, mode='L')
    elif colormap == 'hot':
        # Fire/lava colormap
        colored = np.zeros((img_data.shape[0], img_data.shape[1], 3), dtype=np.uint8)
        colored[:, :, 0] = img_data  # Red
        colored[:, :, 1] = np.clip(img_data - 85, 0, 255)  # Green
        colored[:, :, 2] = np.clip(img_data - 170, 0, 255)  # Blue
        img = Image.fromarray(colored, mode='RGB')
    elif colormap == 'cool':
        # Ice/water colormap
        colored = np.zeros((img_data.shape[0], img_data.shape[1], 3), dtype=np.uint8)
        colored[:, :, 0] = np.clip(img_data - 170, 0, 255)  # Red
        colored[:, :, 1] = np.clip(img_data - 85, 0, 255)  # Green
        colored[:, :, 2] = img_data  # Blue
        img = Image.fromarray(colored, mode='RGB')
    elif colormap == 'terrain':
        # Terrain colormap (water -> sand -> grass -> rock -> snow)
        colored = np.zeros((img_data.shape[0], img_data.shape[1], 3), dtype=np.uint8)
        for y in range(img_data.shape[0]):
            for x in range(img_data.shape[1]):
                val = img_data[y, x]
                if val < 51:  # Water
                    colored[y, x] = [30, 60, 120]
                elif val < 76:  # Sand
                    colored[y, x] = [210, 180, 140]
                elif val < 153:  # Grass
                    colored[y, x] = [50, 120, 40]
                elif val < 204:  # Rock
                    colored[y, x] = [100, 100, 100]
                else:  # Snow
                    colored[y, x] = [240, 240, 255]
        img = Image.fromarray(colored, mode='RGB')
    else:
        img = Image.fromarray(img_data, mode='L')
    
    img.save(filename)
    print(f"Saved: {filename}")


def main():
    """Generate example noise textures."""
    import os
    
    # Create output directory
    output_dir = "noise_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating noise textures...")
    
    # Basic Perlin noise
    print("1. Perlin noise...")
    perlin = generate_perlin_noise_2d(scale=150.0, octaves=6, seed=42)
    save_noise_as_image(perlin, f"{output_dir}/01_perlin.png")
    
    # Simplex noise
    print("2. Simplex noise...")
    simplex = generate_simplex_noise_2d(scale=150.0, seed=42)
    save_noise_as_image(simplex, f"{output_dir}/02_simplex.png")
    
    # FBM noise
    print("3. FBM noise...")
    fbm = generate_fbm_noise(octaves=8, scale=150.0, seed=42)
    save_noise_as_image(fbm, f"{output_dir}/03_fbm.png")
    
    # Turbulence
    print("4. Turbulence...")
    turbulence = generate_turbulence(scale=100.0, power=2.0, seed=42)
    save_noise_as_image(turbulence, f"{output_dir}/04_turbulence_fire.png", colormap='hot')
    
    # Ridged multifractal
    print("5. Ridged multifractal...")
    ridged = generate_ridged_multifractal(octaves=6, scale=150.0, seed=42)
    save_noise_as_image(ridged, f"{output_dir}/05_ridged_mountains.png")
    
    # Domain warped
    print("6. Domain warped...")
    warped = generate_domain_warped(scale=150.0, warp_strength=30.0, seed=42)
    save_noise_as_image(warped, f"{output_dir}/06_domain_warped_clouds.png", colormap='cool')
    
    # Terrain example
    print("7. Terrain map...")
    terrain = generate_perlin_noise_2d(scale=200.0, octaves=6, seed=123)
    save_noise_as_image(terrain, f"{output_dir}/07_terrain_map.png", colormap='terrain')
    
    print(f"\nAll textures saved to '{output_dir}' directory!")
    print("\nUse cases:")
    print("- Perlin/Simplex: General purpose noise, clouds, terrain")
    print("- FBM: Natural textures, wood, marble")
    print("- Turbulence: Fire, explosions, energy effects")
    print("- Ridged: Mountain ridges, veins, cracks")
    print("- Domain Warped: Swirly clouds, water, organic patterns")


if __name__ == "__main__":
    main()
