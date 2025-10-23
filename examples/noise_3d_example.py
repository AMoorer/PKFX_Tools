"""
3D Noise Examples for Volumetric Effects and Animation
"""

import numpy as np
from PIL import Image
import noise
from opensimplex import OpenSimplex


def generate_3d_noise_slice(width=512, height=512, z_slice=0.0, scale=100.0, 
                            octaves=4, seed=0):
    """
    Generate a 2D slice of 3D Perlin noise.
    Useful for animated noise by changing z_slice over time.
    
    Args:
        width, height: Image dimensions
        z_slice: Z-coordinate (animate this for motion)
        scale: Zoom level
        octaves: Detail levels
        seed: Random seed
    
    Returns:
        numpy array normalized to 0-1
    """
    noise_map = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            nz = z_slice / scale
            
            noise_val = noise.pnoise3(
                nx, ny, nz,
                octaves=octaves,
                persistence=0.5,
                lacunarity=2.0,
                base=seed
            )
            noise_map[y][x] = noise_val
    
    # Normalize to 0-1 range
    noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
    return noise_map


def generate_animated_noise_sequence(num_frames=60, width=256, height=256, 
                                     z_speed=5.0, output_dir="animated_noise"):
    """
    Generate a sequence of noise textures for animation.
    Perfect for animated fire, smoke, clouds, energy fields.
    
    Args:
        num_frames: Number of frames to generate
        width, height: Frame dimensions
        z_speed: How fast noise evolves
        output_dir: Output directory
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating {num_frames} frame animation...")
    
    for frame in range(num_frames):
        z_slice = frame * z_speed
        noise_map = generate_3d_noise_slice(
            width=width, 
            height=height, 
            z_slice=z_slice, 
            scale=100.0,
            octaves=6,
            seed=42
        )
        
        # Convert to image
        img_data = (noise_map * 255).astype(np.uint8)
        img = Image.fromarray(img_data, mode='L')
        img.save(f"{output_dir}/frame_{frame:04d}.png")
        
        if (frame + 1) % 10 == 0:
            print(f"  Generated {frame + 1}/{num_frames} frames")
    
    print(f"\nAnimation frames saved to '{output_dir}'")
    print("Create video with ffmpeg:")
    print(f"  ffmpeg -framerate 30 -i {output_dir}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p noise_animation.mp4")


def generate_curl_noise_2d(width=512, height=512, scale=100.0, seed=0):
    """
    Generate 2D curl noise (divergence-free vector field).
    Perfect for fluid simulations, smoke, fire particle advection.
    
    Returns:
        Tuple of (vector_x, vector_y) numpy arrays
    """
    simplex = OpenSimplex(seed=seed)
    
    # Create potential field
    potential = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            potential[y, x] = simplex.noise3(nx, ny, 0.0)
    
    # Calculate curl (gradient rotated 90 degrees)
    # curl = (∂potential/∂y, -∂potential/∂x)
    grad_y, grad_x = np.gradient(potential)
    
    # Curl is perpendicular to gradient
    curl_x = grad_y
    curl_y = -grad_x
    
    # Normalize vectors
    magnitude = np.sqrt(curl_x**2 + curl_y**2)
    magnitude[magnitude == 0] = 1  # Avoid division by zero
    
    curl_x = curl_x / magnitude
    curl_y = curl_y / magnitude
    
    return curl_x, curl_y


def visualize_curl_noise(curl_x, curl_y, filename="curl_noise.png", 
                        arrow_spacing=16, arrow_scale=8):
    """
    Visualize curl noise vector field as arrows on an image.
    
    Args:
        curl_x, curl_y: Vector field components
        filename: Output filename
        arrow_spacing: Pixels between arrows
        arrow_scale: Length of arrows
    """
    from PIL import ImageDraw
    
    height, width = curl_x.shape
    
    # Create base image showing vector magnitude
    magnitude = np.sqrt(curl_x**2 + curl_y**2)
    img_data = ((magnitude / magnitude.max()) * 255).astype(np.uint8)
    img = Image.fromarray(img_data, mode='L').convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # Draw arrows
    for y in range(0, height, arrow_spacing):
        for x in range(0, width, arrow_spacing):
            vx = curl_x[y, x] * arrow_scale
            vy = curl_y[y, x] * arrow_scale
            
            x1, y1 = x, y
            x2, y2 = x + vx, y + vy
            
            # Draw arrow line
            draw.line([(x1, y1), (x2, y2)], fill=(255, 100, 100), width=1)
            
            # Draw arrow head (simple)
            draw.ellipse([(x2-1, y2-1), (x2+1, y2+1)], fill=(255, 100, 100))
    
    img.save(filename)
    print(f"Saved: {filename}")


def main():
    """Generate 3D and animated noise examples."""
    import os
    
    output_dir = "noise_output_3d"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating 3D noise examples...")
    
    # Generate multiple slices to show 3D evolution
    print("\n1. 3D noise slices...")
    for i, z in enumerate([0, 20, 40, 60, 80]):
        noise_slice = generate_3d_noise_slice(z_slice=z, scale=150.0, octaves=6, seed=42)
        img_data = (noise_slice * 255).astype(np.uint8)
        img = Image.fromarray(img_data, mode='L')
        img.save(f"{output_dir}/3d_slice_z{z:03d}.png")
        print(f"  Slice {i+1}/5 (z={z})")
    
    # Generate curl noise for particle advection
    print("\n2. Curl noise (for fluid simulation)...")
    curl_x, curl_y = generate_curl_noise_2d(scale=80.0, seed=42)
    visualize_curl_noise(curl_x, curl_y, f"{output_dir}/curl_noise_vectors.png")
    
    # Optional: Generate short animation sequence
    # Uncomment below to generate animation frames
    # print("\n3. Animated noise sequence...")
    # generate_animated_noise_sequence(
    #     num_frames=30, 
    #     width=256, 
    #     height=256,
    #     z_speed=3.0,
    #     output_dir=f"{output_dir}/animation"
    # )
    
    print(f"\nAll 3D noise examples saved to '{output_dir}'!")
    print("\nUse cases:")
    print("- 3D Noise Slices: Animated textures, volumetric effects")
    print("- Curl Noise: Fluid simulation, smoke/fire particles, natural motion")


if __name__ == "__main__":
    main()
