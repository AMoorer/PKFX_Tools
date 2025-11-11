"""
Sprite Generator Core
Handles all procedural sprite generation algorithms.
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image


class SpriteGenerator:
    """Handles all sprite generation algorithms."""
    
    @staticmethod
    def generate(sprite_type, width, height, params):
        """
        Generate sprite based on type and parameters.
        Returns RGBA numpy array with shape (height, width, 4).
        """
        if sprite_type == "Circle":
            return SpriteGenerator._circle(width, height, params)
        elif sprite_type == "Square":
            return SpriteGenerator._square(width, height, params)
        elif sprite_type == "Line":
            return SpriteGenerator._line(width, height, params)
        elif sprite_type == "N-Gon":
            return SpriteGenerator._ngon(width, height, params)
        elif sprite_type == "Star":
            return SpriteGenerator._star(width, height, params)
        elif sprite_type == "Glow":
            return SpriteGenerator._glow(width, height, params)
        elif sprite_type == "Flame":
            return SpriteGenerator._flame(width, height, params)
        elif sprite_type == "Sparkle":
            return SpriteGenerator._sparkle(width, height, params)
        elif sprite_type == "Noise":
            return SpriteGenerator._noise(width, height, params)
        elif sprite_type == "Gradient":
            return SpriteGenerator._gradient(width, height, params)
        elif sprite_type == "Ring":
            return SpriteGenerator._ring(width, height, params)
        elif sprite_type == "Cross":
            return SpriteGenerator._cross(width, height, params)
        else:
            return np.zeros((height, width, 4), dtype=np.uint8)
    
    @staticmethod
    def _apply_color_and_alpha(intensity, params):
        """Apply color and alpha to intensity map."""
        h, w = intensity.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        
        r = int(params.get('color_r', 255))
        g = int(params.get('color_g', 255))
        b = int(params.get('color_b', 255))
        alpha_mult = params.get('alpha', 1.0)
        
        rgba[:, :, 0] = (intensity * r).astype(np.uint8)
        rgba[:, :, 1] = (intensity * g).astype(np.uint8)
        rgba[:, :, 2] = (intensity * b).astype(np.uint8)
        rgba[:, :, 3] = (intensity * alpha_mult * 255).astype(np.uint8)
        
        return rgba
    
    @staticmethod
    def _circle(w, h, p):
        """Generate a circle sprite."""
        center_x = w / 2
        center_y = h / 2
        radius = p.get('radius', 0.4) * min(w, h) / 2
        softness = p.get('softness', 0.1) * min(w, h) / 2
        
        y, x = np.ogrid[:h, :w]
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Soft circle with smooth falloff
        if softness > 0:
            intensity = np.clip(1.0 - (dist - radius) / softness, 0, 1)
        else:
            intensity = (dist <= radius).astype(float)
        
        # Apply gradient if enabled
        if p.get('gradient', False):
            gradient_intensity = 1.0 - np.clip(dist / radius, 0, 1)
            intensity = intensity * gradient_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _square(w, h, p):
        """Generate a square sprite."""
        center_x = w / 2
        center_y = h / 2
        size = p.get('size', 0.6) * min(w, h) / 2
        softness = p.get('softness', 0.1) * min(w, h) / 2
        rotation = np.radians(p.get('rotation', 0))
        
        y, x = np.ogrid[:h, :w]
        
        # Apply rotation
        dx = x - center_x
        dy = y - center_y
        if rotation != 0:
            x_rot = dx * np.cos(rotation) - dy * np.sin(rotation)
            y_rot = dx * np.sin(rotation) + dy * np.cos(rotation)
        else:
            x_rot = dx
            y_rot = dy
        
        # Distance from square edges
        dist_x = np.abs(x_rot)
        dist_y = np.abs(y_rot)
        dist = np.maximum(dist_x, dist_y)
        
        # Soft square with smooth falloff
        if softness > 0:
            intensity = np.clip(1.0 - (dist - size) / softness, 0, 1)
        else:
            intensity = (dist <= size).astype(float)
        
        # Apply gradient if enabled
        if p.get('gradient', False):
            max_dist = np.maximum(np.abs(x_rot), np.abs(y_rot))
            gradient_intensity = 1.0 - np.clip(max_dist / size, 0, 1)
            intensity = intensity * gradient_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _line(w, h, p):
        """Generate a line sprite."""
        thickness = p.get('thickness', 0.1) * min(w, h)
        softness = p.get('softness', 0.2) * min(w, h)
        angle = np.radians(p.get('angle', 0))
        length = p.get('length', 0.8) * np.sqrt(w**2 + h**2)
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        
        # Rotate coordinates
        dx = x - center_x
        dy = y - center_y
        x_rot = dx * np.cos(angle) - dy * np.sin(angle)
        y_rot = dx * np.sin(angle) + dy * np.cos(angle)
        
        # Distance from line
        dist_perp = np.abs(y_rot)
        dist_along = np.abs(x_rot)
        
        # Create line with length constraint
        intensity = np.ones_like(dist_perp)
        
        # Perpendicular falloff
        if softness > 0:
            intensity *= np.clip(1.0 - (dist_perp - thickness/2) / softness, 0, 1)
        else:
            intensity *= (dist_perp <= thickness/2).astype(float)
        
        # Length constraint with falloff
        if p.get('length_falloff', True):
            length_intensity = np.clip(1.0 - (dist_along - length/2) / (length * 0.1), 0, 1)
            intensity *= length_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _ngon(w, h, p):
        """Generate an n-gon (regular polygon) sprite."""
        sides = int(p.get('sides', 6))
        radius = p.get('radius', 0.4) * min(w, h) / 2
        softness = p.get('softness', 0.1) * min(w, h) / 2
        rotation = np.radians(p.get('rotation', 0))
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dx = x - center_x
        dy = y - center_y
        
        # Calculate angle for each pixel
        angle = np.arctan2(dy, dx) + rotation
        
        # Distance from center
        dist_center = np.sqrt(dx**2 + dy**2)
        
        # Calculate distance to polygon edge
        angle_step = 2 * np.pi / sides
        # Find the nearest edge
        edge_angles = np.arange(sides) * angle_step
        
        # Distance to polygon edge (using polar coordinates)
        dist_to_edge = np.zeros_like(dist_center)
        for i in range(sides):
            edge_angle = edge_angles[i]
            # Distance from center to edge at this angle
            edge_dist = radius / np.cos(np.pi / sides)
            # Project current point onto this edge direction
            angle_diff = np.mod(angle - edge_angle + np.pi, 2*np.pi) - np.pi
            if i == 0:
                dist_to_edge = np.abs(dist_center * np.cos(angle_diff) - radius / np.cos(np.pi / sides))
            else:
                dist_to_edge = np.minimum(dist_to_edge, 
                    np.abs(dist_center * np.cos(angle_diff) - radius / np.cos(np.pi / sides)))
        
        # Simpler approach: use angular modulation
        angular_mod = np.cos(angle * sides) * 0.5 + 0.5
        polygon_radius = radius * (0.8 + 0.2 * angular_mod)
        dist = dist_center - polygon_radius
        
        # Soft edges
        if softness > 0:
            intensity = np.clip(1.0 - dist / softness, 0, 1)
        else:
            intensity = (dist <= 0).astype(float)
        
        # Apply gradient if enabled
        if p.get('gradient', False):
            gradient_intensity = 1.0 - np.clip(dist_center / radius, 0, 1)
            intensity = intensity * gradient_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _star(w, h, p):
        """Generate a star sprite."""
        points = int(p.get('points', 5))
        outer_radius = p.get('outer_radius', 0.4) * min(w, h) / 2
        inner_radius = p.get('inner_radius', 0.2) * min(w, h) / 2
        softness = p.get('softness', 0.1) * min(w, h) / 2
        rotation = np.radians(p.get('rotation', 0))
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dx = x - center_x
        dy = y - center_y
        
        angle = np.arctan2(dy, dx) + rotation
        dist_center = np.sqrt(dx**2 + dy**2)
        
        # Create star shape using angular modulation
        angle_step = 2 * np.pi / points
        angle_mod = np.mod(angle, angle_step) - angle_step / 2
        angle_factor = np.cos(angle_mod * points) * 0.5 + 0.5
        
        # Interpolate between inner and outer radius
        star_radius = inner_radius + (outer_radius - inner_radius) * angle_factor
        dist = dist_center - star_radius
        
        # Soft edges
        if softness > 0:
            intensity = np.clip(1.0 - dist / softness, 0, 1)
        else:
            intensity = (dist <= 0).astype(float)
        
        # Apply gradient if enabled
        if p.get('gradient', False):
            gradient_intensity = 1.0 - np.clip(dist_center / outer_radius, 0, 1)
            intensity = intensity * gradient_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _glow(w, h, p):
        """Generate a glow/halo sprite."""
        intensity_val = p.get('intensity', 1.0)
        falloff = p.get('falloff', 2.0)
        radius = p.get('radius', 0.5)
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Normalized distance
        norm_dist = dist / (max_dist * radius)
        
        # Radial falloff
        intensity = np.power(1.0 - np.clip(norm_dist, 0, 1), falloff) * intensity_val
        
        # Apply gaussian blur for smoothness
        blur = p.get('blur', 0.0)
        if blur > 0:
            intensity = gaussian_filter(intensity, sigma=blur * min(w, h) / 10)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _flame(w, h, p):
        """Generate a flame-shaped sprite."""
        height_factor = p.get('height', 0.8)
        width_factor = p.get('width', 0.5)
        turbulence = p.get('turbulence', 0.3)
        seed = int(p.get('seed', 42))
        
        np.random.seed(seed)
        
        center_x = w / 2
        
        y, x = np.ogrid[:h, :w]
        
        # Normalize coordinates
        nx = (x - center_x) / (w / 2)
        ny = y / h
        
        # Base flame shape (narrowing upward)
        flame_width = width_factor * (1.0 - ny * 0.7)
        dist_x = np.abs(nx) / flame_width
        
        # Height mask
        height_mask = (ny < height_factor).astype(float)
        
        # Add turbulence
        if turbulence > 0:
            noise = np.random.rand(h, w) * 2 - 1
            noise = gaussian_filter(noise, sigma=min(w, h) * 0.05)
            dist_x += noise * turbulence
        
        # Create flame shape
        intensity = np.clip(1.0 - dist_x, 0, 1) * height_mask
        
        # Vertical gradient (brighter at bottom)
        vertical_grad = 1.0 - ny * 0.6
        intensity *= vertical_grad
        
        # Apply falloff
        falloff = p.get('falloff', 2.0)
        intensity = np.power(intensity, falloff)
        
        # Blur for smoothness
        blur = p.get('blur', 1.0)
        if blur > 0:
            intensity = gaussian_filter(intensity, sigma=blur * min(w, h) / 20)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _sparkle(w, h, p):
        """Generate a sparkle/twinkle sprite."""
        rays = int(p.get('rays', 4))
        thickness = p.get('thickness', 0.05) * min(w, h)
        length = p.get('length', 0.8) * min(w, h) / 2
        softness = p.get('softness', 0.15) * min(w, h)
        rotation = np.radians(p.get('rotation', 0))
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dx = x - center_x
        dy = y - center_y
        
        intensity = np.zeros((h, w))
        
        # Create rays
        for i in range(rays):
            angle = rotation + (i * np.pi / rays)
            
            # Rotate coordinates
            x_rot = dx * np.cos(angle) - dy * np.sin(angle)
            y_rot = dx * np.sin(angle) + dy * np.cos(angle)
            
            # Distance from ray axis
            dist_perp = np.abs(y_rot)
            dist_along = np.abs(x_rot)
            
            # Ray intensity
            ray_intensity = np.clip(1.0 - (dist_perp - thickness/2) / softness, 0, 1)
            ray_intensity *= np.clip(1.0 - (dist_along - length) / (length * 0.2), 0, 1)
            
            intensity = np.maximum(intensity, ray_intensity)
        
        # Add center glow
        dist_center = np.sqrt(dx**2 + dy**2)
        center_glow = np.exp(-(dist_center / (thickness * 3))**2)
        intensity = np.maximum(intensity, center_glow)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _noise(w, h, p):
        """Generate a noise texture sprite."""
        scale = p.get('scale', 0.1)
        octaves = int(p.get('octaves', 3))
        seed = int(p.get('seed', 42))
        
        np.random.seed(seed)
        
        intensity = np.zeros((h, w))
        
        # Multi-octave noise
        for octave in range(octaves):
            freq = 2 ** octave
            amp = 0.5 ** octave
            
            # Generate random noise at this frequency
            noise_h = int(h * scale * freq) + 1
            noise_w = int(w * scale * freq) + 1
            octave_noise = np.random.rand(noise_h, noise_w)
            
            # Upscale to full resolution
            from scipy.ndimage import zoom
            if noise_h > 1 and noise_w > 1:
                upscaled = zoom(octave_noise, (h / noise_h, w / noise_w), order=1)
                intensity += upscaled * amp
        
        # Normalize
        if intensity.max() > 0:
            intensity = intensity / intensity.max()
        
        # Apply contrast
        contrast = p.get('contrast', 1.0)
        intensity = np.clip((intensity - 0.5) * contrast + 0.5, 0, 1)
        
        # Apply threshold
        threshold = p.get('threshold', 0.0)
        if threshold > 0:
            intensity = np.where(intensity > threshold, intensity, 0)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _gradient(w, h, p):
        """Generate a gradient sprite."""
        gradient_type = p.get('gradient_type', 'radial')  # 'radial' or 'linear'
        angle = np.radians(p.get('angle', 0))
        falloff = p.get('falloff', 1.0)
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        
        if gradient_type == 'radial':
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            intensity = 1.0 - np.clip(dist / max_dist, 0, 1)
        else:  # linear
            dx = x - center_x
            dy = y - center_y
            # Project onto gradient direction
            proj = (dx * np.cos(angle) + dy * np.sin(angle))
            max_proj = np.sqrt(center_x**2 + center_y**2)
            intensity = 0.5 + proj / (2 * max_proj)
            intensity = np.clip(intensity, 0, 1)
        
        # Apply falloff curve
        intensity = np.power(intensity, falloff)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _ring(w, h, p):
        """Generate a ring/donut sprite."""
        outer_radius = p.get('outer_radius', 0.4) * min(w, h) / 2
        inner_radius = p.get('inner_radius', 0.25) * min(w, h) / 2
        softness = p.get('softness', 0.1) * min(w, h) / 2
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Ring shape (1 inside ring, 0 outside)
        outer_mask = np.clip(1.0 - (dist - outer_radius) / softness, 0, 1)
        inner_mask = np.clip((dist - inner_radius) / softness, 0, 1)
        intensity = outer_mask * inner_mask
        
        # Apply gradient if enabled
        if p.get('gradient', False):
            ring_center = (outer_radius + inner_radius) / 2
            ring_width = (outer_radius - inner_radius) / 2
            dist_from_center = np.abs(dist - ring_center)
            gradient_intensity = 1.0 - np.clip(dist_from_center / ring_width, 0, 1)
            intensity = intensity * gradient_intensity
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
    
    @staticmethod
    def _cross(w, h, p):
        """Generate a cross/plus sprite."""
        thickness = p.get('thickness', 0.1) * min(w, h)
        softness = p.get('softness', 0.1) * min(w, h)
        rotation = np.radians(p.get('rotation', 0))
        
        center_x = w / 2
        center_y = h / 2
        
        y, x = np.ogrid[:h, :w]
        dx = x - center_x
        dy = y - center_y
        
        # Rotate coordinates
        if rotation != 0:
            x_rot = dx * np.cos(rotation) - dy * np.sin(rotation)
            y_rot = dx * np.sin(rotation) + dy * np.cos(rotation)
        else:
            x_rot = dx
            y_rot = dy
        
        # Horizontal bar
        dist_h = np.abs(y_rot)
        intensity_h = np.clip(1.0 - (dist_h - thickness/2) / softness, 0, 1)
        
        # Vertical bar
        dist_v = np.abs(x_rot)
        intensity_v = np.clip(1.0 - (dist_v - thickness/2) / softness, 0, 1)
        
        # Combine
        intensity = np.maximum(intensity_h, intensity_v)
        
        return SpriteGenerator._apply_color_and_alpha(intensity, p)
