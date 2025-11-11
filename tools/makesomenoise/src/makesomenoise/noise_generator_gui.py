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
                               QProgressBar, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QImage, QPixmap, QCursor
import noise
from opensimplex import OpenSimplex
from perlin_noise import PerlinNoise
import os
import random


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
            result = NoiseGenerator._perlin(width, height, params, seamless, blend_width)
        elif noise_type == "Simplex":
            result = NoiseGenerator._simplex(width, height, params, seamless, blend_width)
        elif noise_type == "FBM":
            result = NoiseGenerator._fbm(width, height, params, seamless, blend_width)
        elif noise_type == "Turbulence":
            result = NoiseGenerator._turbulence(width, height, params, seamless, blend_width)
        elif noise_type == "Ridged":
            result = NoiseGenerator._ridged(width, height, params, seamless, blend_width)
        elif noise_type == "Domain Warp":
            result = NoiseGenerator._domain_warp(width, height, params, seamless, blend_width)
        else:
            result = np.zeros((height, width))
        
        # Apply invert if requested
        if params.get('invert', False):
            result = 1.0 - result
        
        return result
    
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
        try:
            # Check if interrupted before starting
            if self.isInterruptionRequested():
                return
            
            # Generate layer A
            noise_a = NoiseGenerator.generate(self.noise_type_a, self.width, self.height, 
                                             self.params_a, self.seamless_tiling, self.blend_width)
            
            # Check if interrupted after layer A
            if self.isInterruptionRequested():
                return
            
            # If no layer B, return just A
            if self.noise_type_b == "None":
                self.finished.emit(noise_a)
                return
            
            # Generate layer B
            noise_b = NoiseGenerator.generate(self.noise_type_b, self.width, self.height, 
                                             self.params_b, self.seamless_tiling, self.blend_width)
            
            # Check if interrupted after layer B
            if self.isInterruptionRequested():
                return
            
            # Blend the layers
            result = self.blend_noise(noise_a, noise_b, self.mix_weight, self.blend_mode)
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in worker thread: {e}")
            import traceback
            traceback.print_exc()
            # Emit a black noise map on error to prevent UI freeze
            fallback = np.zeros((self.height, self.width), dtype=np.float32)
            self.finished.emit(fallback)
    
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
            'sensitivity': 0.1,
            'invert': False
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
            'sensitivity': 0.1,
            'invert': False
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
        
        # Set default save directory to Pictures folder
        import pathlib
        self.default_save_dir = str(pathlib.Path.home() / "Pictures" / "NoiseExports")
        os.makedirs(self.default_save_dir, exist_ok=True)
        
        # Animation state
        self.atlas_frames = []  # Store individual frames for animation
        self.current_frame = 0
        self.animation_timer = None
        
        self.init_ui()
        self.update_preview()
        
        # Sparkle animation for easter egg hint
        self.sparkle_timer = QTimer()
        self.sparkle_timer.timeout.connect(self.trigger_sparkle)
        self.sparkle_timer.start(random.randint(5000, 15000))  # First sparkle in 5-15 seconds
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu anywhere in the application."""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu()
        
        # Export options
        export_single_action = menu.addAction("🖼️ Export Single Frame")
        export_single_action.triggered.connect(self.export_single)
        
        export_atlas_action = menu.addAction("📊 Export Animation Atlas")
        export_atlas_action.triggered.connect(self.export_atlas)
        
        export_sequence_action = menu.addAction("🎞️ Export File Sequence")
        export_sequence_action.triggered.connect(self.export_sequence)
        
        menu.addSeparator()
        
        # Clipboard option
        copy_preview_action = menu.addAction("📋 Copy Preview to Clipboard")
        copy_preview_action.triggered.connect(self.copy_preview_to_clipboard)
        
        # Open location
        open_location_action = menu.addAction("📁 Open Save Location in Explorer")
        open_location_action.triggered.connect(self.open_save_location)
        
        menu.addSeparator()
        
        # Help
        help_action = menu.addAction("📚 A Guide To Noise")
        help_action.triggered.connect(self.show_help_dialog)
        
        # About
        about_action = menu.addAction("ℹ️ About MakeSomeNoise")
        about_action.triggered.connect(self.show_about_dialog)
        
        # Show menu at cursor position
        menu.exec_(event.globalPos())
    
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
                                     "Ridged", "Domain Warp"])
        self.noise_combo_a.setToolTip("")  # Prevent parent tooltip inheritance
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
        
        # Add invert checkbox
        from PySide6.QtWidgets import QCheckBox
        self.invert_checkbox_a = QCheckBox("Invert Output")
        self.invert_checkbox_a.setChecked(False)
        self.invert_checkbox_a.setToolTip("Invert the noise values (black ↔ white)")
        self.invert_checkbox_a.stateChanged.connect(lambda state: self.on_invert_changed('A', state))
        self.params_a_layout.addWidget(self.invert_checkbox_a)
        
        params_a_group.setLayout(self.params_a_layout)
        layout.addWidget(params_a_group)
        
        # Add spacing before mixing
        layout.addSpacing(15)
        
        # Mixing controls
        mix_group = QGroupBox("Layer Mixing")
        mix_layout = QVBoxLayout()
        
        # Blend mode
        blend_row = QHBoxLayout()
        blend_label = QLabel("Blend Mode:")
        blend_label.setToolTip("Select how to combine layers A and B")
        blend_row.addWidget(blend_label)
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(["Mix", "Add", "Multiply", "Screen", "Overlay", "Min", "Max"])
        self.blend_combo.setToolTip("")  # Prevent parent tooltip inheritance
        self.blend_combo.currentTextChanged.connect(self.on_blend_changed)
        blend_row.addWidget(self.blend_combo, 2)
        mix_layout.addLayout(blend_row)
        
        # Weight slider
        weight_container = QWidget()
        weight_layout = QHBoxLayout(weight_container)
        weight_layout.setContentsMargins(0, 0, 0, 0)
        weight_label = QLabel("A ← Weight → B:")
        weight_label.setToolTip("Balance between layer A (left) and layer B (right)")
        weight_layout.addWidget(weight_label)
        self.weight_slider = QSlider(Qt.Horizontal)
        self.weight_slider.setMinimum(0)
        self.weight_slider.setMaximum(100)
        self.weight_slider.setValue(50)
        self.weight_slider.setToolTip("")  # Prevent parent tooltip inheritance
        self.weight_slider.valueChanged.connect(self.on_weight_changed)
        weight_layout.addWidget(self.weight_slider, 2)
        self.weight_label = QLabel("0.50")
        self.weight_label.setMinimumWidth(40)
        self.weight_label.setToolTip("")  # Prevent parent tooltip inheritance
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
                                     "Ridged", "Domain Warp"])
        self.noise_combo_b.setToolTip("")  # Prevent parent tooltip inheritance
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
        
        # Add invert checkbox
        self.invert_checkbox_b = QCheckBox("Invert Output")
        self.invert_checkbox_b.setChecked(False)
        self.invert_checkbox_b.setToolTip("Invert the noise values (black ↔ white)")
        self.invert_checkbox_b.stateChanged.connect(lambda state: self.on_invert_changed('B', state))
        self.params_b_layout.addWidget(self.invert_checkbox_b)
        
        params_b_group.setLayout(self.params_b_layout)
        layout.addWidget(params_b_group)
        
        # Update visibility
        self.update_param_visibility()
        
        layout.addStretch()
        
        # Copyright and version info at bottom left (clickable easter egg)
        copyright_container = QWidget()
        copyright_container.setObjectName("copyright_container")
        copyright_layout = QVBoxLayout(copyright_container)
        copyright_layout.setContentsMargins(0, 0, 0, 0)
        copyright_layout.setSpacing(2)  # Minimal space between lines
        
        copyright_label = QLabel("Andy Moorer 2025")
        copyright_label.setProperty("easterEgg", True)
        copyright_label.setStyleSheet("color: #666; font-size: 9px; cursor: pointer;")
        copyright_label.setToolTip("Click here for A Guide To Noise")
        copyright_label.mousePressEvent = lambda event: self.show_help_dialog()
        copyright_layout.addWidget(copyright_label)
        
        version_label = QLabel("v1.1.2")
        version_label.setProperty("easterEgg", True)
        version_label.setStyleSheet("color: #666; font-size: 9px; cursor: pointer;")
        version_label.setToolTip("Click here for A Guide To Noise")
        version_label.mousePressEvent = lambda event: self.show_help_dialog()
        copyright_layout.addWidget(version_label)
        
        layout.addWidget(copyright_container)
        
        return panel
    
    def add_slider(self, layout, label, key, min_val, max_val, default, scale=1.0, layer='A'):
        """Add a parameter slider."""
        # Tooltips for each parameter
        tooltips = {
            'scale': 'Controls the size/frequency of noise features\nLower = larger features, Higher = smaller features',
            'octaves': 'Number of noise layers to combine\nMore octaves = more detail but slower generation',
            'persistence': 'How much each octave contributes\nHigher = more influence from smaller details',
            'lacunarity': 'Frequency multiplier between octaves\nHigher = more variation between detail levels',
            'seed': 'Random seed for noise generation\nSame seed = same noise pattern',
            'power': 'Exponential adjustment of noise values\nHigher = more contrast, sharper features',
            'warp': 'Domain warping strength\nHigher = more distortion',
            'z_slice': 'Position in 3D noise space\nUseful for static 3D noise sampling',
            'x_offset': 'Horizontal offset in noise space\nShift the noise pattern left/right',
            'y_offset': 'Vertical offset in noise space\nShift the noise pattern up/down',
            'z_offset': 'Depth offset in noise space\nUsed for animation progression',
            'sensitivity': 'Multiplier for X/Y/Z offset effects\nHigher = offsets have stronger effect'
        }
        
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(100)
        # Apply tooltip to label if available
        if key in tooltips:
            lbl.setToolTip(tooltips[key])
        h_layout.addWidget(lbl)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(int(default))
        slider.setToolTip("")  # Prevent parent tooltip inheritance
        slider.valueChanged.connect(lambda v: self.on_param_changed(layer, key, v * scale))
        h_layout.addWidget(slider)
        
        value_label = QLabel(f"{default * scale:.2f}" if scale != 1.0 else str(default))
        value_label.setFixedWidth(50)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value_label.setToolTip("")  # Prevent parent tooltip inheritance
        from PySide6.QtWidgets import QSizePolicy
        value_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        h_layout.addWidget(value_label, 0, Qt.AlignRight)
        
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
        self.status_label.setProperty("easterEgg", True)
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold; cursor: pointer;")
        self.status_label.setToolTip("Click here for A Guide To Noise")
        self.status_label.mousePressEvent = lambda event: self.show_help_dialog()
        preview_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(self.preview_size, self.preview_size)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        self.preview_label.setToolTip("")  # No tooltip on preview
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        # Preview controls at bottom left
        from PySide6.QtWidgets import QCheckBox
        preview_controls = QWidget()
        preview_controls_layout = QVBoxLayout(preview_controls)
        preview_controls_layout.setContentsMargins(0, 0, 0, 0)
        preview_controls_layout.setSpacing(2)
        
        self.tiling_checkbox = QCheckBox("Seamless Tiling")
        self.tiling_checkbox.setChecked(True)  # Default to enabled
        self.tiling_checkbox.setToolTip("Enable seamless edge blending for tileable textures")
        self.tiling_checkbox.stateChanged.connect(self.on_tiling_changed)
        preview_controls_layout.addWidget(self.tiling_checkbox)
        
        # Blend width slider
        blend_width_container = QWidget()
        blend_width_layout = QHBoxLayout(blend_width_container)
        blend_width_layout.setContentsMargins(0, 0, 0, 0)
        blend_width_label = QLabel("Blend Width:")
        blend_width_label.setToolTip("Width of edge blending for seamless tiling\nHigher values = smoother but more visible blend")
        blend_width_layout.addWidget(blend_width_label)
        self.blend_width_slider = QSlider(Qt.Horizontal)
        self.blend_width_slider.setMinimum(5)
        self.blend_width_slider.setMaximum(40)
        self.blend_width_slider.setValue(10)  # 10%
        self.blend_width_slider.setToolTip("")  # Prevent parent tooltip inheritance
        self.blend_width_slider.valueChanged.connect(self.on_blend_width_changed)
        blend_width_layout.addWidget(self.blend_width_slider)
        self.blend_width_label = QLabel("10%")
        self.blend_width_label.setMinimumWidth(40)
        self.blend_width_label.setToolTip("")  # Prevent parent tooltip inheritance
        blend_width_layout.addWidget(self.blend_width_label)
        preview_controls_layout.addWidget(blend_width_container)
        
        self.center_seams_checkbox = QCheckBox("Center Seams")
        self.center_seams_checkbox.setChecked(False)
        self.center_seams_checkbox.setToolTip("Offset seamless tiles by 50% to preview seam quality\nSeams will appear in center of preview")
        self.center_seams_checkbox.stateChanged.connect(self.on_center_seams_changed)
        preview_controls_layout.addWidget(self.center_seams_checkbox)
        
        preview_layout.addWidget(preview_controls, alignment=Qt.AlignLeft)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Export Preview
        export_preview_group = QGroupBox("Export Preview")
        export_preview_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        export_preview_layout = QVBoxLayout()
        
        # Preview mode selector
        preview_mode_row = QHBoxLayout()
        mode_label = QLabel("Preview Method:")
        mode_label.setToolTip("Select what type of export to preview")
        preview_mode_row.addWidget(mode_label)
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["Single Frame", "Atlas", "Anim Preview"])
        self.preview_mode_combo.setToolTip("")  # Prevent parent tooltip inheritance
        preview_mode_row.addWidget(self.preview_mode_combo, 2)
        
        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.setToolTip("Generate a preview of the selected export mode")
        self.preview_btn.clicked.connect(self.generate_preview)
        preview_mode_row.addWidget(self.preview_btn)
        export_preview_layout.addLayout(preview_mode_row)
        
        self.export_preview_label = QLabel("Click 'Generate Preview' to see output")
        self.export_preview_label.setFixedSize(256, 256)
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #222; color: #888;")
        self.export_preview_label.setAlignment(Qt.AlignCenter)
        self.export_preview_label.setToolTip("")  # Prevent parent tooltip inheritance
        export_preview_layout.addWidget(self.export_preview_label, alignment=Qt.AlignCenter)
        
        self.export_info_label = QLabel("")
        self.export_info_label.setProperty("easterEgg", True)
        self.export_info_label.setWordWrap(True)
        self.export_info_label.setMinimumHeight(200)
        self.export_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.export_info_label.setStyleSheet("cursor: pointer;")
        self.export_info_label.setToolTip("Click here for A Guide To Noise")
        self.export_info_label.mousePressEvent = lambda event: self.show_help_dialog()
        export_preview_layout.addWidget(self.export_info_label)
        
        # Playback FPS control in lower right
        fps_row = QHBoxLayout()
        fps_row.addStretch()
        fps_label = QLabel("Playback FPS:")
        fps_label.setToolTip("Preview animation playback speed (frames per second)")
        fps_row.addWidget(fps_label)
        self.playback_fps_spin = QSpinBox()
        self.playback_fps_spin.setMinimum(1)
        self.playback_fps_spin.setMaximum(60)
        self.playback_fps_spin.setValue(12)
        self.playback_fps_spin.setToolTip("")  # Prevent parent tooltip inheritance
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
        save_to_label = QLabel("Save to:")
        save_to_label.setToolTip("Full path where files will be saved\nAuto-updates with version numbers after export")
        path_row.addWidget(save_to_label)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Auto-generated filename")
        self.output_path.setToolTip("")  # Prevent parent tooltip inheritance
        self.update_suggested_filename()  # Set initial filename
        path_row.addWidget(self.output_path, 3)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setToolTip("Browse for a custom save location")
        browse_btn.clicked.connect(self.browse_output)
        path_row.addWidget(browse_btn)
        export_layout.addLayout(path_row)
        
        # Connect filename tracking
        self.output_path.textChanged.connect(self.on_manual_filename_change)
        
        # Atlas options
        atlas_row = QHBoxLayout()
        frames_label = QLabel("Frames:")
        frames_label.setToolTip("Number of animation frames to generate")
        atlas_row.addWidget(frames_label)
        self.frame_spin = QSpinBox()
        self.frame_spin.setMinimum(1)
        self.frame_spin.setMaximum(256)
        self.frame_spin.setValue(16)
        self.frame_spin.setToolTip("")  # Prevent parent tooltip inheritance
        atlas_row.addWidget(self.frame_spin)
        
        frame_size_label = QLabel("  Frame Size:")
        frame_size_label.setToolTip("Resolution of each exported frame")
        atlas_row.addWidget(frame_size_label)
        self.atlas_size_combo = QComboBox()
        self.atlas_size_combo.addItems(["64x64", "128x128", "256x256", "512x512"])
        self.atlas_size_combo.setCurrentText("256x256")
        self.atlas_size_combo.setToolTip("")  # Prevent parent tooltip inheritance
        atlas_row.addWidget(self.atlas_size_combo)
        
        # Add Noise Anim Rate to the right of Frame Size
        anim_rate_label = QLabel("  Noise Anim Rate:")
        anim_rate_label.setToolTip("Z-offset step between frames\nHigher values = faster animation speed")
        atlas_row.addWidget(anim_rate_label)
        self.anim_rate_spin = QSpinBox()
        self.anim_rate_spin.setMinimum(1)
        self.anim_rate_spin.setMaximum(100)
        self.anim_rate_spin.setValue(5)
        self.anim_rate_spin.setToolTip("")  # Prevent parent tooltip inheritance
        atlas_row.addWidget(self.anim_rate_spin)
        
        atlas_row.addStretch()
        export_layout.addLayout(atlas_row)
        
        # Connect for filename updates
        self.atlas_size_combo.currentTextChanged.connect(self.update_suggested_filename)
        self.frame_spin.valueChanged.connect(self.update_suggested_filename)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setToolTip("")  # Prevent parent tooltip inheritance
        export_layout.addWidget(self.progress_bar)
        
        # Export buttons
        btn_row = QHBoxLayout()
        export_single_btn = QPushButton("Export Single Frame")
        export_single_btn.setToolTip("Export a single noise texture\nRight-click for more options")
        export_single_btn.clicked.connect(self.export_single)
        export_single_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        export_single_btn.customContextMenuRequested.connect(self.show_export_context_menu)
        btn_row.addWidget(export_single_btn)
        
        export_atlas_btn = QPushButton("Export Animation Atlas")
        export_atlas_btn.setToolTip("Export animation frames in a grid layout\nRight-click for more options")
        export_atlas_btn.clicked.connect(self.export_atlas)
        export_atlas_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        export_atlas_btn.customContextMenuRequested.connect(self.show_export_context_menu)
        btn_row.addWidget(export_atlas_btn)
        
        export_sequence_btn = QPushButton("Export File Sequence")
        export_sequence_btn.setToolTip("Export animation frames as individual files\nRight-click for more options")
        export_sequence_btn.clicked.connect(self.export_sequence)
        export_sequence_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        export_sequence_btn.customContextMenuRequested.connect(self.show_export_context_menu)
        btn_row.addWidget(export_sequence_btn)
        
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
        
        # Create full path with default directory
        full_path = os.path.join(self.default_save_dir, filename)
        
        # Temporarily disable manual tracking
        old_manual = self.manual_filename
        self.output_path.setText(full_path)
        self.manual_filename = old_manual
    
    def on_blend_changed(self, text):
        """Handle blend mode change."""
        self.blend_mode = text
        # Debounce updates
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
    def on_weight_changed(self, value):
        """Handle weight slider change."""
        self.mix_weight = value / 100.0
        self.weight_label.setText(f"{self.mix_weight:.2f}")
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
    def on_tiling_changed(self, state):
        """Handle tiling checkbox change."""
        self.seamless_tiling = (state == 2)  # Qt.Checked = 2
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
    def on_center_seams_changed(self, state):
        """Handle center seams checkbox change."""
        self.center_seams = (state == 2)  # Qt.Checked = 2
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
    def on_blend_width_changed(self, value):
        """Handle blend width slider change."""
        self.seamless_blend_width = value / 100.0  # Convert to 0.05-0.40 range
        self.blend_width_label.setText(f"{value}%")
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
    def on_invert_changed(self, layer, state):
        """Handle invert checkbox change."""
        invert_value = (state == 2)  # Qt.Checked = 2
        if layer == 'A':
            self.params_a['invert'] = invert_value
        else:
            self.params_b['invert'] = invert_value
        
        # Debounce updates
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)
    
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
        self.update_timer.start(300)
    
    def update_preview(self):
        """Update noise preview using worker thread."""
        # If worker is currently running, stop it first
        if self.worker is not None and self.worker.isRunning():
            try:
                # Disconnect signals so old worker doesn't update UI
                self.worker.finished.disconnect()
                # Request interruption
                self.worker.requestInterruption()
                # Don't wait for it to finish, just disconnect
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
        try:
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
        except Exception as e:
            print(f"Error displaying preview: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText("Error")
            self.status_label.setStyleSheet("color: #f00; font-weight: bold;")
        finally:
            # Always restore cursor, even on error
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
    
    def show_export_context_menu(self, position):
        """Show context menu for export buttons."""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu()
        
        # Export options
        export_single_action = menu.addAction("Export Single Frame")
        export_single_action.triggered.connect(self.export_single)
        
        export_atlas_action = menu.addAction("Export Animation Atlas")
        export_atlas_action.triggered.connect(self.export_atlas)
        
        export_sequence_action = menu.addAction("Export File Sequence")
        export_sequence_action.triggered.connect(self.export_sequence)
        
        menu.addSeparator()
        
        # Open save location
        open_location_action = menu.addAction("Open Save Location in Explorer")
        open_location_action.triggered.connect(self.open_save_location)
        
        # Show menu at cursor position
        sender = self.sender()
        menu.exec_(sender.mapToGlobal(position))
    
    def copy_preview_to_clipboard(self):
        """Copy the current preview image to clipboard."""
        from PySide6.QtGui import QGuiApplication
        
        # Get the current preview pixmap
        pixmap = self.preview_label.pixmap()
        if pixmap and not pixmap.isNull():
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(pixmap)
            self.status_label.setText("Preview copied to clipboard!")
            self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        else:
            QMessageBox.warning(self, "No Preview", "No preview image available to copy.")
    
    def show_help_dialog(self):
        """Show comprehensive help dialog with noise type information."""
        from PySide6.QtWidgets import QDialog, QTabWidget, QTextBrowser, QVBoxLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("A Guide To Noise")
        dialog.resize(750, 650)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General usage tab
        usage_text = """
<h2>Getting Started with MakeSomeNoise</h2>

<h3>🎨 Basic Workflow</h3>
<ol>
<li><b>Select a Noise Type:</b> Choose from 6 different algorithms in the Noise Type A section</li>
<li><b>Adjust Parameters:</b> Fine-tune the noise using sliders (hover over labels for descriptions)</li>
<li><b>Preview in Real-Time:</b> See immediate results in the live preview window</li>
<li><b>Add Complexity:</b> Optionally enable Noise Type B and blend two layers together</li>
<li><b>Export Your Work:</b> Save as a single image, animation atlas, or frame sequence</li>
</ol>

<h3>⚙️ Key Features</h3>
<p><b>Seamless Tiling:</b> Enable to create textures that tile perfectly without visible seams. Use "Center Seams" to inspect seam quality.</p>
<p><b>Dual-Layer Blending:</b> Combine two noise types using various blend modes (Mix, Add, Multiply, Screen, Overlay, Min, Max) for complex patterns.</p>
<p><b>Animation:</b> Create animated noise by using Z-offset or exporting sequences with the Noise Anim Rate parameter.</p>
<p><b>Version Control:</b> Exports automatically increment version numbers (_v00, _v01, etc.) to prevent overwriting.</p>

<h3>💡 Tips & Tricks</h3>
<ul>
<li>Use <b>right-click</b> anywhere for quick access to export and clipboard options</li>
<li>Hover over any <b>label</b> to see detailed parameter descriptions</li>
<li>Start with <b>Perlin</b> or <b>Simplex</b> noise for natural-looking textures</li>
<li>Use <b>FBM</b> (Fractal Brownian Motion) for cloud-like patterns</li>
<li>Try <b>Domain Warp</b> for organic, flowing distortions</li>
<li>Combine <b>Ridged</b> noise with low power values for terrain-like features</li>
<li>Export <b>sequences</b> for use in game engines like PopcornFX</li>
</ul>

<h3>📁 Export Formats</h3>
<p><b>Single Frame:</b> Best for static textures and testing</p>
<p><b>Animation Atlas:</b> Grid layout of frames - efficient for sprite sheets</p>
<p><b>File Sequence:</b> Individual files per frame - maximum flexibility for compositing</p>

<h3>🔗 Common Use Cases</h3>
<ul>
<li>Game texture generation (clouds, terrain, marble, wood grain)</li>
<li>VFX elements (smoke, fire, water, energy effects)</li>
<li>Procedural backgrounds and environments</li>
<li>Displacement and bump maps</li>
<li>Motion graphics and abstract art</li>
</ul>
"""
        usage_browser = QTextBrowser()
        usage_browser.setHtml(usage_text)
        usage_browser.setOpenExternalLinks(True)
        tabs.addTab(usage_browser, "📖 Usage Guide")
        
        # Noise type tabs
        noise_types = {
            "Perlin": {
                "summary": "Classic gradient noise algorithm with smooth, natural-looking transitions.",
                "history": "Developed by Ken Perlin in 1983 for the movie Tron. Won an Academy Award for Technical Achievement in 1997.",
                "algorithm": "Works by interpolating random gradient vectors placed at integer grid points. Each point influences nearby coordinates through a polynomial fade function (6t⁵ - 15t⁴ + 10t³), creating smooth transitions. The dot product of gradient vectors with distance vectors determines the final value at each point.",
                "parameters": "<b>Scale:</b> Frequency of noise features<br><b>Octaves:</b> Layers of detail<br><b>Persistence:</b> Amplitude reduction per octave<br><b>Lacunarity:</b> Frequency increase per octave",
                "use_cases": "Ideal for natural textures like clouds, terrain, marble, and wood grain. Widely used in procedural generation and organic patterns.",
                "characteristics": "Smooth gradients, no directional bias, tileable when properly implemented. Good balance between randomness and coherence.",
                "pro_tip": "Start with a scale around 100 and 4-6 octaves for most natural textures. Increasing octaves adds fine detail but slows generation. For wood grain, try combining with turbulence."
            },
            "Simplex": {
                "summary": "Ken Perlin's improved noise algorithm with better visual quality and performance.",
                "history": "Created by Ken Perlin in 2001 as an improvement over classic Perlin noise. Features fewer directional artifacts and better computational efficiency.",
                "algorithm": "Uses a simplex grid (triangular in 2D, tetrahedral in 3D) instead of a square grid. Gradients are distributed more evenly, and fewer gradient evaluations are needed per point. The skewed coordinate system reduces directional bias and improves visual isotropy.",
                "parameters": "<b>Scale:</b> Controls feature size<br><b>Octaves:</b> Detail layers<br><b>Persistence:</b> Detail contribution<br><b>Lacunarity:</b> Detail frequency scaling",
                "use_cases": "Excellent for terrain generation, fluid simulations, and any application requiring smooth, organic randomness. Often preferred over Perlin for modern applications.",
                "characteristics": "Smoother than Perlin, less visible grid artifacts, computationally faster. Creates more visually pleasing organic patterns.",
                "pro_tip": "Simplex produces rounder, more organic 'blobs' than Perlin. Lower the scale (30-50) for cloud formations, or go very low (10-20) with high persistence for cellular-looking patterns."
            },
            "FBM": {
                "summary": "Fractal Brownian Motion - combines multiple octaves of noise for rich, detailed patterns.",
                "history": "Based on fractional Brownian motion concepts from fractal geometry. Popularized in computer graphics for creating natural-looking textures with self-similar detail at multiple scales.",
                "algorithm": "Sums multiple octaves of noise with increasing frequency and decreasing amplitude. Each octave's frequency is multiplied by lacunarity (typically 2.0) and amplitude by persistence (typically 0.5). The result is: Σ(amplitude × noise(frequency × point)) for each octave.",
                "parameters": "<b>Scale:</b> Base frequency<br><b>Octaves:</b> Number of detail layers (more = more complex)<br><b>Persistence:</b> How much each octave contributes<br><b>Lacunarity:</b> Frequency multiplier between octaves",
                "use_cases": "Perfect for clouds, mountains, planetary surfaces, and any surface requiring multiple scales of detail. Widely used in procedural terrain generation.",
                "characteristics": "Self-similar at different scales, highly detailed, computational cost increases with octaves. Creates fractal-like patterns found in nature.",
                "pro_tip": "For realistic clouds, use 6-8 octaves with persistence 0.5 and lacunarity 2.0. For mountains, try persistence 0.6-0.7. Higher lacunarity (2.5-3.0) creates more chaotic, varied detail."
            },
            "Turbulence": {
                "summary": "Uses absolute values of noise for chaotic, turbulent patterns with sharp contrasts.",
                "history": "Derived from fluid dynamics turbulence simulation. Introduced to computer graphics for creating marble, fire, and other flowing, chaotic patterns.",
                "algorithm": "Similar to FBM but takes the absolute value of each noise octave before summing: Σ(amplitude × |noise(frequency × point)|). This creates sharp 'folds' in the pattern where values cross zero, mimicking turbulent fluid behavior.",
                "parameters": "<b>Scale:</b> Turbulence scale<br><b>Octaves:</b> Complexity level<br><b>Persistence:</b> Contrast control<br><b>Power:</b> Sharpness of features",
                "use_cases": "Excellent for marble textures, fire effects, energy shields, magical effects, and flowing liquids. Creates more chaotic patterns than FBM.",
                "characteristics": "Sharp ridges and valleys, higher contrast than FBM, creates swirling, turbulent patterns. More dramatic and less smooth than standard noise.",
                "pro_tip": "For marble, use turbulence with power 2.0-3.0 and mix with Perlin. For fire, increase power to 3.5-4.5 and use high persistence (0.7+). The higher the power, the sharper and more intense the effect."
            },
            "Ridged": {
                "summary": "Creates sharp ridges and valleys, excellent for terrain and crystalline structures.",
                "history": "Developed for terrain generation where sharp mountain ridges are desired. Inverts and modifies standard noise to create ridge-like features.",
                "algorithm": "Inverts the absolute value operation: 1 - |noise(point)|, then combines octaves. This creates sharp ridges where the original noise would have zero crossings. Often applies a power function to sharpen peaks further: (1 - |noise|)^power.",
                "parameters": "<b>Scale:</b> Ridge frequency<br><b>Octaves:</b> Ridge detail<br><b>Power:</b> Ridge sharpness (lower = sharper)<br><b>Persistence:</b> Detail contribution",
                "use_cases": "Mountain ranges, canyon networks, crystalline structures, cracked surfaces, and sci-fi terrain. Essential for realistic terrain generation.",
                "characteristics": "Creates sharp peaks and valleys, inverse of turbulence in some ways. Lower power values create more dramatic, sharp ridges.",
                "pro_tip": "Counterintuitively, LOWER power values create SHARPER ridges. Try power 1.0-1.5 for dramatic mountain ranges. Use 4-6 octaves for natural terrain. Blend with Perlin (50/50 mix) for more realistic landscapes."
            },
            "Domain Warp": {
                "summary": "Warps the noise space itself, creating organic, flowing distortions and unique patterns.",
                "history": "Modern technique popularized by Inigo Quilez and procedural generation artists. Creates complex patterns by feeding noise output back into domain input.",
                "algorithm": "Uses noise to offset the sampling coordinates before evaluating final noise. Typically: offset_x = noise(x, y), offset_y = noise(x+seed, y+seed), final = noise(x+offset_x×warp, y+offset_y×warp). This recursive distortion creates complex, organic patterns impossible with direct noise.",
                "parameters": "<b>Warp Strength:</b> Amount of distortion<br><b>Scale:</b> Base pattern size<br><b>Octaves:</b> Warp complexity",
                "use_cases": "Abstract art, organic alien textures, flow fields, twisted metal, biological patterns, and unique VFX elements. Great for when standard noise is too regular.",
                "characteristics": "Highly organic and flowing, can create fingerprint-like patterns. No two warps look exactly alike. Computationally more expensive.",
                "pro_tip": "Start with warp strength 30-50 and increase slowly. Very high values (80+) create intense, almost psychedelic patterns. Try warping Ridged noise for alien landscapes, or warp FBM for biological cell-like structures."
            }
        }
        
        for noise_name, info in noise_types.items():
            noise_html = f"""
<h2>🌊 {noise_name} Noise</h2>

<h3>Overview</h3>
<p>{info['summary']}</p>

<h3>📜 History & Background</h3>
<p>{info['history']}</p>

<h3>🔬 How The Algorithm Works</h3>
<p>{info['algorithm']}</p>

<h3>⚙️ Key Parameters</h3>
<p>{info['parameters']}</p>

<h3>🎯 Best Use Cases</h3>
<p>{info['use_cases']}</p>

<h3>✨ Characteristics</h3>
<p>{info['characteristics']}</p>

<h3>💡 Pro Tip</h3>
<p><i>{info['pro_tip']}</i></p>
"""
            noise_browser = QTextBrowser()
            noise_browser.setHtml(noise_html)
            tabs.addTab(noise_browser, noise_name)
        
        layout.addWidget(tabs)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.close)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_about_dialog(self):
        """Show About dialog with application information."""
        about_text = """
<h2>MakeSomeNoise v1.1.2</h2>
<p><b>Procedural Noise Generator</b></p>

<p>A professional tool for generating seamless noise textures with dual-layer blending and animation support.</p>

<h3>Features:</h3>
<ul>
<li>6 noise algorithms (Perlin, Simplex, FBM, Turbulence, Ridged, Domain Warp)</li>
<li>Dual-layer blending with 7 blend modes</li>
<li>Seamless tiling with adjustable edge blending</li>
<li>Animation support with atlas and sequence export</li>
<li>Real-time preview with animation playback</li>
<li>Automatic version management for exports</li>
</ul>

<h3>Export Formats:</h3>
<ul>
<li>Single Frame - Individual noise texture</li>
<li>Animation Atlas - Grid of animation frames</li>
<li>File Sequence - Separate files per frame</li>
</ul>

<p style="margin-top: 20px;">
<b>Created by:</b> Andy Moorer<br>
<b>Year:</b> 2025<br>
<b>Version:</b> 1.1.2
</p>

<p style="margin-top: 10px; font-size: 10px; color: #666;">
Right-click anywhere for quick access to export options and tools.
</p>
"""
        QMessageBox.about(self, "About MakeSomeNoise", about_text)
    
    def open_save_location(self):
        """Open the save directory in Windows Explorer."""
        import subprocess
        
        # Get the directory from current output path or use default
        output_path = self.output_path.text()
        if output_path:
            # If it's a file, get its directory; if it's a folder, use it directly
            if os.path.isdir(output_path):
                directory = output_path
            else:
                directory = os.path.dirname(output_path)
                # If no directory part, use default
                if not directory:
                    directory = self.default_save_dir
        else:
            directory = self.default_save_dir
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Open in Explorer
        try:
            subprocess.Popen(f'explorer "{directory}"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open Explorer: {str(e)}")
    
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
    
    def get_versioned_folder_name(self, base_folder):
        """Get folder name with version number, incrementing if folder exists."""
        # Check if folder exists
        version = 0
        versioned_folder = f"{base_folder}_v{version:02d}"
        
        while os.path.exists(versioned_folder):
            version += 1
            versioned_folder = f"{base_folder}_v{version:02d}"
        
        return versioned_folder
    
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
        
        # Update output path to show versioned filename
        old_manual = self.manual_filename
        self.output_path.setText(output_path)
        self.manual_filename = old_manual
        
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
            
            # Update output path to show versioned filename
            old_manual = self.manual_filename
            self.output_path.setText(filename)
            self.manual_filename = old_manual
            
            QMessageBox.information(self, "Success", f"Saved atlas: {filename}\n{num_frames} frames, {cols}x{rows} grid\n\nAnimation preview playing!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export atlas: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def export_sequence(self):
        """Export animation as individual frames in a folder."""
        # Build descriptive folder name
        num_frames = self.frame_spin.value()
        frame_size = int(self.atlas_size_combo.currentText().split('x')[0])
        
        # Get base name from user input or generate one
        user_name = self.output_path.text()
        if user_name and not user_name.lower().endswith('.png'):
            base_name = user_name
        elif user_name and user_name.lower().endswith('.png'):
            base_name = user_name[:-4]
        else:
            # Generate smart name: noisetype_size__Nframe_seq
            name_parts = [self.noise_type_a.replace(' ', '').lower()]
            if self.noise_type_b != "None":
                name_parts.append(self.noise_type_b.replace(' ', '').lower())
            base_name = "_".join(name_parts) + f"_{frame_size}__{num_frames}frame_seq"
        
        # Get versioned folder name (adds _v00, _v01, etc.)
        folder_path = self.get_versioned_folder_name(base_name)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(100)
        
        try:
            # Create the folder
            os.makedirs(folder_path, exist_ok=True)
            
            anim_rate = self.anim_rate_spin.value()
            
            # Clear previous frames and prepare for new animation
            self.atlas_frames = []
            
            # Calculate padding width (e.g., 16 frames = 2 digits, 100 frames = 3 digits)
            padding_width = len(str(num_frames))
            
            # Extract version number from folder path (e.g., "folder_v00" -> "v00")
            folder_basename = os.path.basename(folder_path)
            version_suffix = folder_basename.split('_')[-1]  # Gets "v00", "v01", etc.
            
            # Build frame filename prefix: noisetype_version
            noise_prefix_parts = [self.noise_type_a.replace(' ', '').lower()]
            if self.noise_type_b != "None":
                noise_prefix_parts.append(self.noise_type_b.replace(' ', '').lower())
            frame_prefix = "_".join(noise_prefix_parts) + f"_{version_suffix}"
            
            # Generate and save frames
            for i in range(num_frames):
                # Update progress
                progress = int((i / num_frames) * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Exporting frame {i+1}/{num_frames}...")
                self.status_label.setStyleSheet("color: #fa0; font-weight: bold;")
                QApplication.processEvents()
                
                # Animate using z_offset with animation rate
                params_a_copy = self.params_a.copy()
                params_b_copy = self.params_b.copy()
                
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
                
                # Store frame for animation preview
                self.atlas_frames.append(img_data.copy())
                
                # Save individual frame with noise type and version prefix
                frame_filename = f"{frame_prefix}_frame_{i:0{padding_width}d}.png"
                frame_path = os.path.join(folder_path, frame_filename)
                
                img = Image.fromarray(img_data, mode='L')
                img.save(frame_path)
            
            # Start animated preview of the sequence
            self.current_frame = 0
            info = f"File Sequence: {num_frames} frames\nFrame: {frame_size}x{frame_size}\nFolder: {os.path.basename(folder_path)}\n\nPlaying at {self.playback_fps_spin.value()} FPS"
            self.export_info_label.setText(info)
            
            # Update preview mode dropdown to reflect animation state
            self.preview_mode_combo.setCurrentText("Anim Preview")
            
            self.start_animation()
            
            self.progress_bar.setValue(100)
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
            
            # Update output path to show versioned folder path
            old_manual = self.manual_filename
            self.output_path.setText(folder_path)
            self.manual_filename = old_manual
            
            QMessageBox.information(self, "Success", f"Saved sequence: {folder_path}\n{num_frames} frames\n\nAnimation preview playing!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export sequence: {str(e)}")
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
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
    
    def trigger_sparkle(self):
        """Create sparkle animation with small pixel dots over copyright text."""
        # Get copyright container position
        copyright_container = self.findChild(QWidget, "copyright_container")
        if not copyright_container:
            return
        
        # Create 5-15 small pixel dots
        num_pixels = random.randint(5, 15)
        self._sparkle_pixels = []
        
        for i in range(num_pixels):
            # Create small pixel dot
            pixel = QLabel(self)
            pixel.setFixedSize(2, 2)
            pixel.setStyleSheet("background-color: #aaa; border-radius: 1px;")
            
            # Random position near copyright text
            container_pos = copyright_container.mapTo(self, QPoint(0, 0))
            x_offset = random.randint(-15, 80)
            y_offset = random.randint(-10, 30)
            pixel.move(container_pos.x() + x_offset, container_pos.y() + y_offset)
            
            # Stagger appearance: random delay 0-700ms
            appear_delay = random.randint(0, 700)
            
            # Stagger disappearance: show for 200-400ms after appearing
            disappear_delay = appear_delay + random.randint(200, 400)
            
            # Schedule appearance
            QTimer.singleShot(appear_delay, lambda p=pixel: p.show())
            
            # Schedule disappearance
            QTimer.singleShot(disappear_delay, lambda p=pixel: p.deleteLater())
            
            self._sparkle_pixels.append(pixel)
        
        # Schedule next sparkle
        next_delay = random.randint(8000, 15000)
        self.sparkle_timer.start(next_delay)


def main():
    app = QApplication(sys.argv)
    
    # Set global stylesheet for tooltips - subtle dark style
    app.setStyleSheet("""
        QToolTip {
            color: #888888 !important;
            background-color: #1e1e1e !important;
            border: 1px solid #3a3a3a !important;
            padding: 4px 8px;
            font-size: 9px;
            font-weight: normal;
        }
    """)
    
    window = NoiseGeneratorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
