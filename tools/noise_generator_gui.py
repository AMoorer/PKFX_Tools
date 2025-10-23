"""
Interactive Noise Generator GUI
Real-time noise generation with parameter controls and atlas export.
"""

import sys
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton,
                               QSpinBox, QGroupBox, QFileDialog, QMessageBox, QLineEdit,
                               QProgressBar)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QCursor
import noise
from opensimplex import OpenSimplex
from perlin_noise import PerlinNoise
import os


class NoiseGenerator:
    """Handles all noise generation algorithms."""
    
    @staticmethod
    def make_seamless_blend(noise_map, blend_width=0.1):
        """Apply boundary blending with proper 2D corner handling for seamless tiling."""
        h, w = noise_map.shape
        result = noise_map.copy()
        
        # Calculate blend zone size
        blend_h = max(2, int(h * blend_width))
        blend_w = max(2, int(w * blend_width))
        
        # Process each pixel in the blend zones with proper 2D blending
        for y in range(h):
            for x in range(w):
                # Determine if pixel is in blend zone and calculate weights
                blend_y = 0.0
                blend_x = 0.0
                
                # Vertical blend weight
                if y < blend_h:
                    blend_y = 1.0 - (y / float(blend_h))
                elif y >= h - blend_h:
                    blend_y = 1.0 - ((h - 1 - y) / float(blend_h))
                
                # Horizontal blend weight
                if x < blend_w:
                    blend_x = 1.0 - (x / float(blend_w))
                elif x >= w - blend_w:
                    blend_x = 1.0 - ((w - 1 - x) / float(blend_w))
                
                # Skip if not in any blend zone
                if blend_y == 0.0 and blend_x == 0.0:
                    continue
                
                # Get the 4 corresponding pixels (current + 3 wraps)
                p00 = noise_map[y, x]
                p01 = noise_map[y, (x + w // 2) % w]  # Horizontal wrap
                p10 = noise_map[(y + h // 2) % h, x]  # Vertical wrap
                p11 = noise_map[(y + h // 2) % h, (x + w // 2) % w]  # Both wraps
                
                # Blend in 2D
                top_blend = (1 - blend_x) * p00 + blend_x * p01
                bottom_blend = (1 - blend_x) * p10 + blend_x * p11
                result[y, x] = (1 - blend_y) * top_blend + blend_y * bottom_blend
        
        return result
    
    @staticmethod
    def generate(noise_type, width, height, params, seamless=False, blend_width=0.1):
        """Generate noise based on type and parameters."""
        if noise_type == "Perlin":
            return NoiseGenerator._perlin(width, height, params, seamless, blend_width)
        elif noise_type == "Simplex":
            return NoiseGenerator._simplex(width, height, params, seamless, blend_width)
        elif noise_type == "FBM":
            return NoiseGenerator._fbm(width, height, params, seamless, blend_width)
        elif noise_type == "Turbulence":
            return NoiseGenerator._turbulence(width, height, params, seamless, blend_width)
        elif noise_type == "Ridged":
            return NoiseGenerator._ridged(width, height, params, seamless, blend_width)
        elif noise_type == "Domain Warp":
            return NoiseGenerator._domain_warp(width, height, params, seamless, blend_width)
        elif noise_type == "3D Slice":
            return NoiseGenerator._3d_slice(width, height, params, seamless, blend_width)
        else:
            return np.zeros((height, width))
    
    @staticmethod
    def _perlin(w, h, p, seamless=False, blend_width=0.1):
        """Optimized Perlin noise generation with 3D offsets."""
        noise_map = np.zeros((h, w))
        scale = p['scale']
        octaves = int(min(p['octaves'], 10))
        seed = int(p['seed']) % 256
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        # Generate noise (seamless tiling will be applied via boundary blending)
        for y in range(h):
            for x in range(w):
                nx = (float(x) + x_off) / scale
                ny = (float(y) + y_off) / scale
                nz = z_off / scale
                
                val = noise.pnoise3(nx, ny, nz, octaves=octaves, 
                                   persistence=p['persistence'], lacunarity=p['lacunarity'], 
                                   base=seed)
                noise_map[y][x] = val
        
        # Normalize
        min_val, max_val = noise_map.min(), noise_map.max()
        if max_val - min_val > 1e-10:
            result = (noise_map - min_val) / (max_val - min_val)
        else:
            result = noise_map
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _simplex(w, h, p, seamless=False, blend_width=0.1):
        """Optimized Simplex noise generation with 3D offsets."""
        simplex = OpenSimplex(seed=int(p['seed']) % 256)
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        # Generate noise
        for y in range(h):
            for x in range(w):
                nx = (x + x_off) / scale
                ny = (y + y_off) / scale
                nz = z_off / scale
                noise_map[y][x] = simplex.noise3(nx, ny, nz)
        
        # Normalize to 0-1
        result = (noise_map + 1.0) * 0.5
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _fbm(w, h, p, seamless=False, blend_width=0.1):
        """Optimized FBM noise generation with 3D offsets."""
        octaves = int(min(p['octaves'], 10))
        perlin = PerlinNoise(octaves=octaves, seed=int(p['seed']) % 256)
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        for y in range(h):
            for x in range(w):
                noise_map[y][x] = perlin([(x + x_off)/scale, (y + y_off)/scale, z_off/scale])
        
        # Normalize
        min_val, max_val = noise_map.min(), noise_map.max()
        if max_val - min_val > 1e-10:
            result = (noise_map - min_val) / (max_val - min_val)
        else:
            result = noise_map
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _turbulence(w, h, p, seamless=False, blend_width=0.1):
        """Optimized turbulence noise generation with 3D offsets."""
        simplex = OpenSimplex(seed=int(p['seed']) % 256)
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        power = p.get('power', 2.0)
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        for y in range(h):
            for x in range(w):
                val = abs(simplex.noise3((x + x_off)/scale, (y + y_off)/scale, z_off/scale))
                noise_map[y][x] = val ** power
        
        max_val = noise_map.max()
        result = noise_map / (max_val + 1e-10) if max_val > 1e-10 else noise_map
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _ridged(w, h, p, seamless=False, blend_width=0.1):
        """Optimized ridged multifractal noise generation with 3D offsets."""
        simplex = OpenSimplex(seed=int(p['seed']) % 256)
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        octaves = int(min(p['octaves'], 10))
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        for y in range(h):
            for x in range(w):
                result = 0.0
                amp, freq = 1.0, 1.0
                for _ in range(octaves):
                    signal = 1.0 - abs(simplex.noise3((x + x_off)/scale*freq, (y + y_off)/scale*freq, z_off/scale*freq))
                    signal *= signal  # Square for sharper ridges
                    result += signal * amp
                    amp *= 0.5
                    freq *= 2.0
                noise_map[y][x] = result
        
        max_val = noise_map.max()
        result = noise_map / (max_val + 1e-10) if max_val > 1e-10 else noise_map
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _domain_warp(w, h, p, seamless=False, blend_width=0.1):
        """Optimized domain warp noise generation with 3D offsets."""
        seed = int(p['seed']) % 256
        simplex = OpenSimplex(seed=seed)
        simplex_warp = OpenSimplex(seed=seed + 1)
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        warp = p.get('warp', 50.0)
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        for y in range(h):
            for x in range(w):
                wx = simplex_warp.noise3((x + x_off)/scale, (y + y_off)/scale, z_off/scale) * warp
                wy = simplex_warp.noise3((x + x_off)/scale + 5.2, (y + y_off)/scale + 1.3, z_off/scale) * warp
                val = simplex.noise3((x+wx)/scale, (y+wy)/scale, z_off/scale)
                noise_map[y][x] = val
        
        result = (noise_map + 1.0) * 0.5
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result
    
    @staticmethod
    def _3d_slice(w, h, p, seamless=False, blend_width=0.1):
        """Optimized 3D slice noise generation with offsets."""
        noise_map = np.zeros((h, w), dtype=np.float32)
        scale = p['scale']
        z = p.get('z_slice', 0.0)
        octaves = int(min(p['octaves'], 10))
        seed = int(p['seed']) % 256
        
        # Apply 3D offsets with sensitivity
        sensitivity = p.get('sensitivity', 1.0)
        x_off = p.get('x_offset', 0.0) * sensitivity
        y_off = p.get('y_offset', 0.0) * sensitivity
        z_off = p.get('z_offset', 0.0) * sensitivity
        
        for y in range(h):
            for x in range(w):
                val = noise.pnoise3((x + x_off)/scale, (y + y_off)/scale, (z + z_off)/scale, 
                                   octaves=octaves, base=seed)
                noise_map[y][x] = val
        
        # Normalize
        min_val, max_val = noise_map.min(), noise_map.max()
        if max_val - min_val > 1e-10:
            result = (noise_map - min_val) / (max_val - min_val)
        else:
            result = noise_map
        
        # Apply seamless blending if requested
        if seamless:
            result = NoiseGenerator.make_seamless_blend(result, blend_width)
        
        return result


class NoiseWorker(QThread):
    """Worker thread for generating composite noise without blocking UI."""
    finished = Signal(np.ndarray)
    
    def __init__(self, noise_type_a, noise_type_b, width, height, params_a, params_b, 
                 mix_weight, blend_mode, seamless_tiling=False, blend_width=0.1):
        super().__init__()
        self.noise_type_a = noise_type_a
        self.noise_type_b = noise_type_b
        self.width = width
        self.height = height
        self.params_a = params_a
        self.params_b = params_b
        self.mix_weight = mix_weight
        self.blend_mode = blend_mode
        self.seamless_tiling = seamless_tiling
        self.blend_width = blend_width
    
    def run(self):
        # Generate layer A
        noise_a = NoiseGenerator.generate(self.noise_type_a, self.width, self.height, 
                                         self.params_a, self.seamless_tiling, self.blend_width)
        
        # If no layer B, return just A
        if self.noise_type_b == "None":
            self.finished.emit(noise_a)
            return
        
        # Generate layer B
        noise_b = NoiseGenerator.generate(self.noise_type_b, self.width, self.height, 
                                         self.params_b, self.seamless_tiling, self.blend_width)
        
        # Blend the layers
        result = self.blend_noise(noise_a, noise_b, self.mix_weight, self.blend_mode)
        self.finished.emit(result)
    
    def blend_noise(self, noise_a, noise_b, weight, mode):
        """Blend two noise maps using specified mode."""
        if mode == "Mix":
            return noise_a * (1 - weight) + noise_b * weight
        elif mode == "Add":
            result = noise_a + noise_b * weight
            return np.clip(result, 0, 1)
        elif mode == "Multiply":
            return noise_a * (noise_b * weight + (1 - weight))
        elif mode == "Screen":
            return 1 - (1 - noise_a) * (1 - noise_b * weight)
        elif mode == "Overlay":
            mask = noise_a < 0.5
            result = np.zeros_like(noise_a)
            result[mask] = 2 * noise_a[mask] * noise_b[mask]
            result[~mask] = 1 - 2 * (1 - noise_a[~mask]) * (1 - noise_b[~mask])
            return noise_a * (1 - weight) + result * weight
        elif mode == "Min":
            return np.minimum(noise_a, noise_b * weight + noise_a * (1 - weight))
        elif mode == "Max":
            return np.maximum(noise_a, noise_b * weight + noise_a * (1 - weight))
        else:
            return noise_a


class NoiseGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MakeSomeNoise")
        self.setGeometry(100, 100, 1400, 850)
        
        # Set size constraints to prevent elongation
        self.setMinimumSize(1200, 850)
        self.setMaximumSize(1920, 900)
        
        # Parameter visibility mapping - all noises now support 3D offsets
        self.param_visibility = {
            'Perlin': ['scale', 'octaves', 'persistence', 'lacunarity', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'Simplex': ['scale', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'FBM': ['scale', 'octaves', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'Turbulence': ['scale', 'power', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'Ridged': ['scale', 'octaves', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'Domain Warp': ['scale', 'warp', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            '3D Slice': ['scale', 'octaves', 'z_slice', 'seed', 'x_offset', 'y_offset', 'z_offset', 'sensitivity'],
            'None': []
        }
        
        # Default parameters for layer A
        self.params_a = {
            'scale': 100.0,
            'octaves': 6,
            'persistence': 0.5,
            'lacunarity': 2.0,
            'seed': 42,
            'power': 2.0,
            'warp': 50.0,
            'z_slice': 0.0,
            'x_offset': 0.0,
            'y_offset': 0.0,
            'z_offset': 0.0,
            'sensitivity': 0.1
        }
        
        # Default parameters for layer B (ensure different seed)
        self.params_b = {
            'scale': 50.0,
            'octaves': 4,
            'persistence': 0.5,
            'lacunarity': 2.0,
            'seed': 500,  # Different from A to ensure variation
            'power': 2.0,
            'warp': 30.0,
            'z_slice': 0.0,
            'x_offset': 0.0,
            'y_offset': 0.0,
            'z_offset': 0.0,
            'sensitivity': 0.1
        }
        
        # Mixing parameters
        self.mix_weight = 0.5  # 0=all A, 1=all B
        self.blend_mode = "Mix"
        self.seamless_tiling = True  # Seamless tiling option (default enabled)
        self.seamless_blend_width = 0.1  # Blend width for seamless tiling (10%)
        self.center_seams = False  # Center seams visualization (default disabled)
        
        self.preview_size = 256
        self.noise_type_a = "Perlin"
        self.noise_type_b = "None"
        self.worker = None
        self.manual_filename = False  # Track if user manually edited filename
        
        # Animation state
        self.atlas_frames = []  # Store individual frames for animation
        self.current_frame = 0
        self.animation_timer = None
        
        self.init_ui()
        self.update_preview()
    
    def init_ui(self):
        """Initialize UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Preview and Export
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 2)
    
    def create_control_panel(self):
        """Create control panel with parameters."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Noise Type A Selection
        type_a_group = QGroupBox("Noise Type A")
        type_a_layout = QVBoxLayout()
        self.noise_combo_a = QComboBox()
        self.noise_combo_a.addItems(["Perlin", "Simplex", "FBM", "Turbulence", 
                                     "Ridged", "Domain Warp", "3D Slice"])
        self.noise_combo_a.currentTextChanged.connect(lambda t: self.on_noise_type_changed('A', t))
        type_a_layout.addWidget(self.noise_combo_a)
        type_a_group.setLayout(type_a_layout)
        layout.addWidget(type_a_group)
        
        # Parameters A
        params_a_group = QGroupBox("Parameters A")
        self.params_a_layout = QVBoxLayout()
        
        self.sliders_a = {}
        self.add_slider(self.params_a_layout, "Scale", 'scale', 10, 500, 100, layer='A')
        self.add_slider(self.params_a_layout, "Octaves", 'octaves', 1, 10, 6, layer='A')
        self.add_slider(self.params_a_layout, "Persistence", 'persistence', 0, 100, 50, scale=0.01, layer='A')
        self.add_slider(self.params_a_layout, "Lacunarity", 'lacunarity', 15, 40, 20, scale=0.1, layer='A')
        self.add_slider(self.params_a_layout, "Seed", 'seed', 0, 1000, 42, layer='A')
        self.add_slider(self.params_a_layout, "Power", 'power', 10, 50, 20, scale=0.1, layer='A')
        self.add_slider(self.params_a_layout, "Warp Strength", 'warp', 10, 100, 50, layer='A')
        self.add_slider(self.params_a_layout, "Z Slice", 'z_slice', 0, 200, 0, layer='A')
        self.add_slider(self.params_a_layout, "X Offset", 'x_offset', -500, 500, 0, layer='A')
        self.add_slider(self.params_a_layout, "Y Offset", 'y_offset', -500, 500, 0, layer='A')
        self.add_slider(self.params_a_layout, "Z Offset", 'z_offset', -500, 500, 0, layer='A')
        self.add_slider(self.params_a_layout, "Sensitivity", 'sensitivity', 1, 300, 10, scale=0.01, layer='A')
        
        params_a_group.setLayout(self.params_a_layout)
        layout.addWidget(params_a_group)
        
        # Add spacing before mixing
        layout.addSpacing(15)
        
        # Mixing controls
        mix_group = QGroupBox("Layer Mixing")
        mix_layout = QVBoxLayout()
        
        # Blend mode
        blend_row = QHBoxLayout()
        blend_row.addWidget(QLabel("Blend Mode:"))
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(["Mix", "Add", "Multiply", "Screen", "Overlay", "Min", "Max"])
        self.blend_combo.currentTextChanged.connect(self.on_blend_changed)
        blend_row.addWidget(self.blend_combo, 2)
        mix_layout.addLayout(blend_row)
        
        # Weight slider
        weight_container = QWidget()
        weight_layout = QHBoxLayout(weight_container)
        weight_layout.setContentsMargins(0, 0, 0, 0)
        weight_layout.addWidget(QLabel("A ← Weight → B:"))
        self.weight_slider = QSlider(Qt.Horizontal)
        self.weight_slider.setMinimum(0)
        self.weight_slider.setMaximum(100)
        self.weight_slider.setValue(50)
        self.weight_slider.valueChanged.connect(self.on_weight_changed)
        weight_layout.addWidget(self.weight_slider, 2)
        self.weight_label = QLabel("0.50")
        self.weight_label.setMinimumWidth(40)
        weight_layout.addWidget(self.weight_label)
        mix_layout.addWidget(weight_container)
        
        mix_group.setLayout(mix_layout)
        layout.addWidget(mix_group)
        
        # Add spacing after mixing
        layout.addSpacing(15)
        
        # Noise Type B Selection
        type_b_group = QGroupBox("Noise Type B")
        type_b_layout = QVBoxLayout()
        self.noise_combo_b = QComboBox()
        self.noise_combo_b.addItems(["None", "Perlin", "Simplex", "FBM", "Turbulence", 
                                     "Ridged", "Domain Warp", "3D Slice"])
        self.noise_combo_b.currentTextChanged.connect(lambda t: self.on_noise_type_changed('B', t))
        type_b_layout.addWidget(self.noise_combo_b)
        type_b_group.setLayout(type_b_layout)
        layout.addWidget(type_b_group)
        
        # Parameters B
        params_b_group = QGroupBox("Parameters B")
        self.params_b_layout = QVBoxLayout()
        
        self.sliders_b = {}
        self.add_slider(self.params_b_layout, "Scale", 'scale', 10, 500, 50, layer='B')
        self.add_slider(self.params_b_layout, "Octaves", 'octaves', 1, 10, 4, layer='B')
        self.add_slider(self.params_b_layout, "Persistence", 'persistence', 0, 100, 50, scale=0.01, layer='B')
        self.add_slider(self.params_b_layout, "Lacunarity", 'lacunarity', 15, 40, 20, scale=0.1, layer='B')
        self.add_slider(self.params_b_layout, "Seed", 'seed', 0, 1000, 500, layer='B')
        self.add_slider(self.params_b_layout, "Power", 'power', 10, 50, 20, scale=0.1, layer='B')
        self.add_slider(self.params_b_layout, "Warp Strength", 'warp', 10, 100, 30, layer='B')
        self.add_slider(self.params_b_layout, "Z Slice", 'z_slice', 0, 200, 0, layer='B')
        self.add_slider(self.params_b_layout, "X Offset", 'x_offset', -500, 500, 0, layer='B')
        self.add_slider(self.params_b_layout, "Y Offset", 'y_offset', -500, 500, 0, layer='B')
        self.add_slider(self.params_b_layout, "Z Offset", 'z_offset', -500, 500, 0, layer='B')
        self.add_slider(self.params_b_layout, "Sensitivity", 'sensitivity', 1, 300, 10, scale=0.01, layer='B')
        
        params_b_group.setLayout(self.params_b_layout)
        layout.addWidget(params_b_group)
        
        # Update visibility
        self.update_param_visibility()
        
        layout.addStretch()
        
        # Copyright and version info at bottom left
        copyright_container = QWidget()
        copyright_layout = QVBoxLayout(copyright_container)
        copyright_layout.setContentsMargins(0, 0, 0, 0)
        copyright_layout.setSpacing(2)  # Minimal space between lines
        
        copyright_label = QLabel("Andy Moorer 2025")
        copyright_label.setStyleSheet("color: #666; font-size: 9px;")
        copyright_layout.addWidget(copyright_label)
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #666; font-size: 9px;")
        copyright_layout.addWidget(version_label)
        
        layout.addWidget(copyright_container)
        
        return panel
    
    def add_slider(self, layout, label, key, min_val, max_val, default, scale=1.0, layer='A'):
        """Add a parameter slider."""
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(100)
        h_layout.addWidget(lbl)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(int(default / scale) if scale != 1.0 else default)
        slider.valueChanged.connect(lambda v: self.on_param_changed(layer, key, v * scale))
        h_layout.addWidget(slider, 2)
        
        value_label = QLabel(f"{default * scale:.2f}" if scale != 1.0 else str(default))
        value_label.setMinimumWidth(50)
        h_layout.addWidget(value_label)
        
        sliders_dict = self.sliders_a if layer == 'A' else self.sliders_b
        sliders_dict[key] = (container, slider, value_label, scale)
        layout.addWidget(container)
    
    def create_preview_panel(self):
        """Create preview and export panel."""
        from PySide6.QtWidgets import QSizePolicy
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)  # Consistent spacing between groups
        
        # Preview
        preview_group = QGroupBox("Preview (Live)")
        preview_layout = QVBoxLayout()
        preview_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Status indicator at top
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        preview_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(self.preview_size, self.preview_size)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        # Preview controls at bottom left
        from PySide6.QtWidgets import QCheckBox
        preview_controls = QWidget()
        preview_controls_layout = QVBoxLayout(preview_controls)
        preview_controls_layout.setContentsMargins(0, 0, 0, 0)
        preview_controls_layout.setSpacing(2)
        
        self.tiling_checkbox = QCheckBox("Seamless Tiling")
        self.tiling_checkbox.setChecked(True)  # Default to enabled
        self.tiling_checkbox.stateChanged.connect(self.on_tiling_changed)
        preview_controls_layout.addWidget(self.tiling_checkbox)
        
        # Blend width slider
        blend_width_container = QWidget()
        blend_width_layout = QHBoxLayout(blend_width_container)
        blend_width_layout.setContentsMargins(0, 0, 0, 0)
        blend_width_layout.addWidget(QLabel("Blend Width:"))
        self.blend_width_slider = QSlider(Qt.Horizontal)
        self.blend_width_slider.setMinimum(5)
        self.blend_width_slider.setMaximum(40)
        self.blend_width_slider.setValue(10)  # 10%
        self.blend_width_slider.valueChanged.connect(self.on_blend_width_changed)
        blend_width_layout.addWidget(self.blend_width_slider)
        self.blend_width_label = QLabel("10%")
        self.blend_width_label.setMinimumWidth(40)
        blend_width_layout.addWidget(self.blend_width_label)
        preview_controls_layout.addWidget(blend_width_container)
        
        self.center_seams_checkbox = QCheckBox("Preview Seams")
        self.center_seams_checkbox.setChecked(False)
        self.center_seams_checkbox.stateChanged.connect(self.on_center_seams_changed)
        preview_controls_layout.addWidget(self.center_seams_checkbox)
        
        preview_layout.addWidget(preview_controls, alignment=Qt.AlignLeft)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Export Preview
        export_preview_group = QGroupBox("Export Preview")
        export_preview_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        export_preview_layout = QVBoxLayout()
        
        # Preview mode selector
        preview_mode_row = QHBoxLayout()
        preview_mode_row.addWidget(QLabel("Mode:"))
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["Single Frame", "Atlas", "Anim Preview"])
        preview_mode_row.addWidget(self.preview_mode_combo, 2)
        
        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        preview_mode_row.addWidget(self.preview_btn)
        export_preview_layout.addLayout(preview_mode_row)
        
        self.export_preview_label = QLabel("Click 'Generate Preview' to see output")
        self.export_preview_label.setFixedSize(256, 256)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #222; color: #888;")
        self.export_preview_label.setAlignment(Qt.AlignCenter)
        export_preview_layout.addWidget(self.export_preview_label, alignment=Qt.AlignCenter)
        
        self.export_info_label = QLabel("")
        self.export_info_label.setWordWrap(True)
        export_preview_layout.addWidget(self.export_info_label)
        
        # Playback FPS control in lower right
        fps_row = QHBoxLayout()
        fps_row.addStretch()
        fps_row.addWidget(QLabel("Playback FPS:"))
        self.playback_fps_spin = QSpinBox()
        self.playback_fps_spin.setMinimum(1)
        self.playback_fps_spin.setMaximum(60)
        self.playback_fps_spin.setValue(12)
        self.playback_fps_spin.setToolTip("Preview animation speed")
        fps_row.addWidget(self.playback_fps_spin)
        export_preview_layout.addLayout(fps_row)
        
        export_preview_group.setLayout(export_preview_layout)
        layout.addWidget(export_preview_group)
        
        # Export Options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()
        export_layout.setSpacing(5)  # Tighten vertical spacing
        export_layout.setContentsMargins(9, 9, 9, 9)  # Standard margins
        
        # Output path
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Save to:"))
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Auto-generated filename")
        self.update_suggested_filename()  # Set initial filename
        path_row.addWidget(self.output_path, 3)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        path_row.addWidget(browse_btn)
        export_layout.addLayout(path_row)
        
        # Connect filename tracking
        self.output_path.textChanged.connect(self.on_manual_filename_change)
        
        # Atlas options
        atlas_row = QHBoxLayout()
        atlas_row.addWidget(QLabel("Frames:"))
        self.frame_spin = QSpinBox()
        self.frame_spin.setMinimum(1)
        self.frame_spin.setMaximum(256)
        self.frame_spin.setValue(16)
        atlas_row.addWidget(self.frame_spin)
        
        atlas_row.addWidget(QLabel("  Frame Size:"))
        self.atlas_size_combo = QComboBox()
        self.atlas_size_combo.addItems(["64x64", "128x128", "256x256", "512x512"])
        self.atlas_size_combo.setCurrentText("256x256")
        atlas_row.addWidget(self.atlas_size_combo)
        
        # Add Noise Anim Rate to the right of Frame Size
        atlas_row.addWidget(QLabel("  Noise Anim Rate:"))
        self.anim_rate_spin = QSpinBox()
        self.anim_rate_spin.setMinimum(1)
        self.anim_rate_spin.setMaximum(100)
        self.anim_rate_spin.setValue(5)
        self.anim_rate_spin.setToolTip("Offset step between frames")
        atlas_row.addWidget(self.anim_rate_spin)
        
        atlas_row.addStretch()
        export_layout.addLayout(atlas_row)
        
        # Connect for filename updates
        self.atlas_size_combo.currentTextChanged.connect(self.update_suggested_filename)
        self.frame_spin.valueChanged.connect(self.update_suggested_filename)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        export_layout.addWidget(self.progress_bar)
        
        # Export buttons
        btn_row = QHBoxLayout()
        export_single_btn = QPushButton("Export Single Frame")
        export_single_btn.clicked.connect(self.export_single)
        btn_row.addWidget(export_single_btn)
        
        export_atlas_btn = QPushButton("Export Animation Atlas")
        export_atlas_btn.clicked.connect(self.export_atlas)
        btn_row.addWidget(export_atlas_btn)
        export_layout.addLayout(btn_row)
        
        export_group.setLayout(export_layout)
        
        # Set size policy to prevent vertical expansion
        export_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        layout.addWidget(export_group)
        
        # Add stretch at bottom to prevent expansion
        layout.addStretch()
        
        return panel
    
    def on_noise_type_changed(self, layer, text):
        """Handle noise type change."""
        if layer == 'A':
            self.noise_type_a = text
        else:
            self.noise_type_b = text
        self.update_param_visibility()
        self.update_suggested_filename()
        self.update_preview()
    
    def on_manual_filename_change(self):
        """Track if user manually edited filename."""
        self.manual_filename = True
    
    def update_suggested_filename(self):
        """Generate smart filename based on current settings."""
        if self.manual_filename:
            return  # Don't override manual edits
        
        # Build filename
        name_parts = [self.noise_type_a.replace(' ', '')]
        
        if self.noise_type_b != "None":
            name_parts.append(self.noise_type_b.replace(' ', ''))
        
        # Add size
        size = self.atlas_size_combo.currentText().split('x')[0] if hasattr(self, 'atlas_size_combo') else "256"
        name_parts.append(size)
        
        # Check if atlas export (more than 1 frame)
        if hasattr(self, 'frame_spin'):
            num_frames = self.frame_spin.value()
            if num_frames > 1:
                # Calculate grid
                cols = int(np.ceil(np.sqrt(num_frames)))
                rows = int(np.ceil(num_frames / cols))
                name_parts.append(f"{cols}x{rows}")
        
        filename = "_".join(name_parts) + ".png"
        
        # Temporarily disable manual tracking
        old_manual = self.manual_filename
        self.output_path.setText(filename)
        self.manual_filename = old_manual
    
    def on_blend_changed(self, text):
        """Handle blend mode change."""
        self.blend_mode = text
        # Debounce updates
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def on_weight_changed(self, value):
        """Handle weight slider change."""
        self.mix_weight = value / 100.0
        self.weight_label.setText(f"{self.mix_weight:.2f}")
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def on_tiling_changed(self, state):
        """Handle tiling checkbox change."""
        self.seamless_tiling = (state == 2)  # Qt.Checked = 2
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def on_center_seams_changed(self, state):
        """Handle center seams checkbox change."""
        self.center_seams = (state == 2)  # Qt.Checked = 2
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def on_blend_width_changed(self, value):
        """Handle blend width slider change."""
        self.seamless_blend_width = value / 100.0  # Convert to 0.05-0.40 range
        self.blend_width_label.setText(f"{value}%")
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def update_param_visibility(self):
        """Update parameter visibility based on selected noise types."""
        # Update layer A visibility
        visible_params_a = self.param_visibility.get(self.noise_type_a, [])
        for key, widgets in self.sliders_a.items():
            container = widgets[0]
            container.setVisible(key in visible_params_a)
        
        # Update layer B visibility
        visible_params_b = self.param_visibility.get(self.noise_type_b, [])
        for key, widgets in self.sliders_b.items():
            container = widgets[0]
            container.setVisible(key in visible_params_b)
    
    def on_param_changed(self, layer, key, value):
        """Handle parameter change."""
        params = self.params_a if layer == 'A' else self.params_b
        params[key] = value
        
        sliders_dict = self.sliders_a if layer == 'A' else self.sliders_b
        container, slider, label, scale = sliders_dict[key]
        
        if scale != 1.0:
            label.setText(f"{value:.2f}")
        else:
            label.setText(str(int(value)))
        
        # Debounce updates
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(200)
    
    def update_preview(self):
        """Update noise preview using worker thread."""
        # Disconnect old worker if it exists (let it finish in background)
        if self.worker is not None:
            try:
                # Disconnect signals so old worker doesn't update UI
                self.worker.finished.disconnect()
            except (RuntimeError, TypeError):
                pass  # Worker already deleted or signals already disconnected
        
        # Update UI status
        self.status_label.setText("Rendering...")
        self.status_label.setStyleSheet("color: #fa0; font-weight: bold;")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        
        # Create new worker thread for composite noise
        self.worker = NoiseWorker(
            self.noise_type_a, self.noise_type_b,
            self.preview_size, self.preview_size,
            self.params_a.copy(), self.params_b.copy(),
            self.mix_weight, self.blend_mode, self.seamless_tiling, self.seamless_blend_width
        )
        self.worker.finished.connect(self.on_preview_finished)
        self.worker.start()
    
    def generate_composite_noise(self, width, height):
        """Generate composite noise from layers A and B."""
        # Generate layer A
        noise_a = NoiseGenerator.generate(self.noise_type_a, width, height, self.params_a, self.seamless_tiling, self.seamless_blend_width)
        
        # If no layer B, return just A
        if self.noise_type_b == "None":
            return noise_a
        
        # Generate layer B
        noise_b = NoiseGenerator.generate(self.noise_type_b, width, height, self.params_b, self.seamless_tiling, self.seamless_blend_width)
        
        # Blend the layers
        return self.blend_noise(noise_a, noise_b, self.mix_weight, self.blend_mode)
    
    def blend_noise(self, noise_a, noise_b, weight, mode):
        """Blend two noise maps using specified mode."""
        if mode == "Mix":
            return noise_a * (1 - weight) + noise_b * weight
        elif mode == "Add":
            result = noise_a + noise_b * weight
            return np.clip(result, 0, 1)
        elif mode == "Multiply":
            return noise_a * (noise_b * weight + (1 - weight))
        elif mode == "Screen":
            return 1 - (1 - noise_a) * (1 - noise_b * weight)
        elif mode == "Overlay":
            mask = noise_a < 0.5
            result = np.zeros_like(noise_a)
            result[mask] = 2 * noise_a[mask] * noise_b[mask]
            result[~mask] = 1 - 2 * (1 - noise_a[~mask]) * (1 - noise_b[~mask])
            return noise_a * (1 - weight) + result * weight
        elif mode == "Min":
            return np.minimum(noise_a, noise_b * weight + noise_a * (1 - weight))
        elif mode == "Max":
            return np.maximum(noise_a, noise_b * weight + noise_a * (1 - weight))
        else:
            return noise_a
    
    def on_preview_finished(self, noise_map):
        """Handle preview generation completion."""
        img_data = (noise_map * 255).astype(np.uint8)
        
        # Apply 50% offset with wrapping if center seams is enabled
        if self.center_seams:
            height, width = img_data.shape
            offset_y = height // 2
            offset_x = width // 2
            
            # Create wrapped/rolled image
            img_data = np.roll(img_data, offset_y, axis=0)
            img_data = np.roll(img_data, offset_x, axis=1)
        
        height, width = img_data.shape
        qimg = QImage(img_data.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(pixmap)
        
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        QApplication.restoreOverrideCursor()
    
    def generate_preview(self):
        """Generate preview based on selected mode without saving."""
        mode = self.preview_mode_combo.currentText()
        
        self.status_label.setText("Generating Preview...")
        self.status_label.setStyleSheet("color: #fa0; font-weight: bold;")
        QApplication.processEvents()
        
        try:
            if mode == "Single Frame":
                self.preview_single_frame()
            elif mode == "Atlas":
                self.preview_atlas()
            elif mode == "Anim Preview":
                self.preview_animation()
            
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Preview failed: {str(e)}")
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
    
    def preview_single_frame(self):
        """Preview single frame at export resolution."""
        res_text = self.atlas_size_combo.currentText()
        size = int(res_text.split('x')[0])
        
        # Generate noise at export resolution
        noise_map = self.generate_composite_noise(size, size)
        img_data = (noise_map * 255).astype(np.uint8)
        
        # Display in preview
        height, width = img_data.shape
        qimg = QImage(img_data.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.export_preview_label.setPixmap(scaled_pixmap)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        
        info = f"Single Frame Preview\nResolution: {size}x{size}\n\nNot saved - click 'Export Single Frame' to save"
        self.export_info_label.setText(info)
        
        # Stop any running animation
        if self.animation_timer is not None:
            self.animation_timer.stop()
    
    def preview_atlas(self):
        """Preview complete atlas layout."""
        num_frames = self.frame_spin.value()
        frame_size = int(self.atlas_size_combo.currentText().split('x')[0])
        anim_rate = self.anim_rate_spin.value()
        
        # Calculate grid layout
        cols = int(np.ceil(np.sqrt(num_frames)))
        rows = int(np.ceil(num_frames / cols))
        atlas_width = cols * frame_size
        atlas_height = rows * frame_size
        
        atlas = np.zeros((atlas_height, atlas_width), dtype=np.uint8)
        
        # Generate frames
        for i in range(num_frames):
            progress = int((i / num_frames) * 100)
            self.status_label.setText(f"Generating Preview... {progress}%")
            QApplication.processEvents()
            
            # Animate using z_offset
            params_a_copy = self.params_a.copy()
            params_b_copy = self.params_b.copy()
            
            params_a_copy['z_offset'] = self.params_a.get('z_offset', 0.0) + (i * anim_rate)
            if self.noise_type_b != "None":
                params_b_copy['z_offset'] = self.params_b.get('z_offset', 0.0) + (i * anim_rate)
            
            # Temporarily set params
            old_params_a = self.params_a
            old_params_b = self.params_b
            self.params_a = params_a_copy
            self.params_b = params_b_copy
            
            noise_map = self.generate_composite_noise(frame_size, frame_size)
            
            # Restore params
            self.params_a = old_params_a
            self.params_b = old_params_b
            
            img_data = (noise_map * 255).astype(np.uint8)
            
            row = i // cols
            col = i % cols
            y = row * frame_size
            x = col * frame_size
            atlas[y:y+frame_size, x:x+frame_size] = img_data
        
        # Display atlas preview
        height, width = atlas.shape
        qimg = QImage(atlas.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.export_preview_label.setPixmap(scaled_pixmap)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        
        info = f"Atlas Preview\n{num_frames} frames in {cols}x{rows} grid\nFrame: {frame_size}x{frame_size}\nTotal: {atlas_width}x{atlas_height}\nAnimation Rate: {anim_rate}\n\nNot saved - click 'Export Animation Atlas' to save"
        self.export_info_label.setText(info)
        
        # Stop any running animation
        if self.animation_timer is not None:
            self.animation_timer.stop()
    
    def preview_animation(self):
        """Preview animation sequence."""
        num_frames = self.frame_spin.value()
        frame_size = int(self.atlas_size_combo.currentText().split('x')[0])
        anim_rate = self.anim_rate_spin.value()
        
        # Clear and generate frames
        self.atlas_frames = []
        
        for i in range(num_frames):
            progress = int((i / num_frames) * 100)
            self.status_label.setText(f"Generating Animation... {progress}%")
            QApplication.processEvents()
            
            # Animate using z_offset
            params_a_copy = self.params_a.copy()
            params_b_copy = self.params_b.copy()
            
            params_a_copy['z_offset'] = self.params_a.get('z_offset', 0.0) + (i * anim_rate)
            if self.noise_type_b != "None":
                params_b_copy['z_offset'] = self.params_b.get('z_offset', 0.0) + (i * anim_rate)
            
            # Temporarily set params
            old_params_a = self.params_a
            old_params_b = self.params_b
            self.params_a = params_a_copy
            self.params_b = params_b_copy
            
            noise_map = self.generate_composite_noise(frame_size, frame_size)
            
            # Restore params
            self.params_a = old_params_a
            self.params_b = old_params_b
            
            img_data = (noise_map * 255).astype(np.uint8)
            self.atlas_frames.append(img_data.copy())
        
        # Start animation
        self.current_frame = 0
        fps = self.playback_fps_spin.value()
        info = f"Animation Preview\n{num_frames} frames at {fps} FPS\nFrame: {frame_size}x{frame_size}\nAnimation Rate: {anim_rate}\n\nLooping...\n\nNot saved - click 'Export Animation Atlas' to save"
        self.export_info_label.setText(info)
        self.start_animation()
    
    def browse_output(self):
        """Browse for output file location."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Noise", 
                                                  self.output_path.text(), 
                                                  "PNG Files (*.png)")
        if filename:
            self.output_path.setText(filename)
    
    def get_versioned_filename(self, base_path):
        """Get filename with version number, incrementing if file exists."""
        if not base_path.lower().endswith('.png'):
            base_path += '.png'
        
        # Split into base and extension
        base = base_path[:-4]
        ext = '.png'
        
        # Check if file exists
        version = 0
        versioned_path = f"{base}_v{version:02d}{ext}"
        
        while os.path.exists(versioned_path):
            version += 1
            versioned_path = f"{base}_v{version:02d}{ext}"
        
        return versioned_path
    
    def export_single(self):
        """Export single frame of noise."""
        output_path = self.output_path.text()
        if not output_path:
            output_path = "noise_output.png"
        
        # Get versioned filename
        output_path = self.get_versioned_filename(output_path)
        
        self.status_label.setText("Exporting...")
        self.status_label.setStyleSheet("color: #fa0; font-weight: bold;")
        QApplication.processEvents()
        
        # Get selected resolution
        res_text = self.atlas_size_combo.currentText()
        size = int(res_text.split('x')[0])
        
        # Generate noise at export resolution
        noise_map = self.generate_composite_noise(size, size)
        img_data = (noise_map * 255).astype(np.uint8)
        img = Image.fromarray(img_data, mode='L')
        img.save(output_path)
        
        # Show preview
        self.show_export_preview(img, f"Single Frame: {size}x{size}\n{os.path.basename(output_path)}")
        
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        QMessageBox.information(self, "Success", f"Saved: {output_path}")
    
    def export_atlas(self):
        """Export animation atlas."""
        filename = self.output_path.text()
        if not filename:
            QMessageBox.warning(self, "Error", "Please specify output filename")
            return
        
        # Ensure .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        # Add _atlas suffix if not present
        if '_atlas' not in filename.lower():
            name, ext = os.path.splitext(filename)
            filename = f"{name}_atlas{ext}"
        
        # Get versioned filename
        filename = self.get_versioned_filename(filename)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(100)
        
        try:
            num_frames = self.frame_spin.value()
            frame_size = int(self.atlas_size_combo.currentText().split('x')[0])
            
            # Calculate grid layout
            cols = int(np.ceil(np.sqrt(num_frames)))
            rows = int(np.ceil(num_frames / cols))
            atlas_width = cols * frame_size
            atlas_height = rows * frame_size
            
            atlas = np.zeros((atlas_height, atlas_width), dtype=np.uint8)
            
            # Clear previous frames and prepare for new animation
            self.atlas_frames = []
            anim_rate = self.anim_rate_spin.value()
            
            # Generate frames
            for i in range(num_frames):
                # Update progress
                progress = int((i / num_frames) * 100)
                self.progress_bar.setValue(progress)
                QApplication.processEvents()
                
                # Animate using z_offset with animation rate
                params_a_copy = self.params_a.copy()
                params_b_copy = self.params_b.copy()
                
                # Use z_offset for animation (works for all noise types now)
                params_a_copy['z_offset'] = self.params_a.get('z_offset', 0.0) + (i * anim_rate)
                if self.noise_type_b != "None":
                    params_b_copy['z_offset'] = self.params_b.get('z_offset', 0.0) + (i * anim_rate)
                
                # Temporarily set animated params
                old_params_a = self.params_a
                old_params_b = self.params_b
                self.params_a = params_a_copy
                self.params_b = params_b_copy
                
                noise_map = self.generate_composite_noise(frame_size, frame_size)
                
                # Restore params
                self.params_a = old_params_a
                self.params_b = old_params_b
                img_data = (noise_map * 255).astype(np.uint8)
                
                # Store frame for animation
                self.atlas_frames.append(img_data.copy())
                
                row = i // cols
                col = i % cols
                y = row * frame_size
                x = col * frame_size
                atlas[y:y+frame_size, x:x+frame_size] = img_data
            
            img = Image.fromarray(atlas, mode='L')
            img.save(filename)
            
            # Start animated preview
            self.current_frame = 0
            info = f"Atlas: {num_frames} frames\nGrid: {cols}x{rows}\nFrame: {frame_size}x{frame_size}\nTotal: {atlas_width}x{atlas_height}\n{os.path.basename(filename)}\n\nPlaying at {self.playback_fps_spin.value()} FPS"
            self.export_info_label.setText(info)
            self.start_animation()
            
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", f"Saved atlas: {filename}\n{num_frames} frames, {cols}x{rows} grid\n\nAnimation preview playing!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export atlas: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def show_export_preview(self, pil_image, info_text):
        """Show preview of exported image."""
        # Resize for preview (max 256x256)
        preview_img = pil_image.copy()
        preview_img.thumbnail((256, 256), Image.Resampling.LANCZOS)
        
        # Convert to QPixmap
        img_array = np.array(preview_img)
        if len(img_array.shape) == 2:  # Grayscale
            height, width = img_array.shape
            qimg = QImage(img_array.data, width, height, width, QImage.Format_Grayscale8)
        else:  # RGB
            height, width, channels = img_array.shape
            qimg = QImage(img_array.data, width, height, width * channels, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimg)
        self.export_preview_label.setPixmap(pixmap)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        self.export_info_label.setText(info_text)
    
    def start_animation(self):
        """Start animation playback of atlas frames."""
        if not self.atlas_frames:
            return
        
        # Stop existing animation if running
        if self.animation_timer is not None:
            self.animation_timer.stop()
        
        # Create new timer
        fps = self.playback_fps_spin.value()
        interval_ms = int(1000 / fps)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation_frame)
        self.animation_timer.start(interval_ms)
        
        # Show first frame immediately
        self.update_animation_frame()
    
    def update_animation_frame(self):
        """Update the export preview with the next animation frame."""
        if not self.atlas_frames:
            return
        
        # Get current frame
        frame_data = self.atlas_frames[self.current_frame]
        height, width = frame_data.shape
        
        # Convert to QImage and display
        qimg = QImage(frame_data.data, width, height, width, QImage.Format_Grayscale8)
        
        # Scale to preview size (256x256) maintaining aspect ratio
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.export_preview_label.setPixmap(scaled_pixmap)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        
        # Advance to next frame (loop)
        self.current_frame = (self.current_frame + 1) % len(self.atlas_frames)


def main():
    app = QApplication(sys.argv)
    window = NoiseGeneratorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
