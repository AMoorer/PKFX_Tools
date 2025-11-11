"""
VFX Sprite Generator GUI
Real-time sprite generation with parameter controls and atlas export.
"""

import sys
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton,
                               QSpinBox, QGroupBox, QFileDialog, QMessageBox, QLineEdit,
                               QCheckBox, QColorDialog, QSizePolicy, QMenu)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QImage, QPixmap, QColor, QAction
import os
from .sprite_generator import SpriteGenerator
from .version import VERSION


class SpriteGeneratorThread(QThread):
    """Background thread for sprite generation."""
    finished = Signal(np.ndarray)
    
    def __init__(self, sprite_type, width, height, params):
        super().__init__()
        self.sprite_type = sprite_type
        self.width = width
        self.height = height
        self.params = params
    
    def run(self):
        """Generate sprite in background."""
        try:
            sprite = SpriteGenerator.generate(
                self.sprite_type, 
                self.width, 
                self.height, 
                self.params
            )
            self.finished.emit(sprite)
        except Exception as e:
            print(f"Generation error: {e}")
            self.finished.emit(np.zeros((self.height, self.width, 4), dtype=np.uint8))


class SpriteGeneratorGUI(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle(f"VFX Sprite Maker v{VERSION}")
        self.setMinimumSize(1200, 800)
        
        # State
        self.current_sprite_type = "Circle"
        self.preview_size = 400
        self.current_sprite = None
        self.generation_thread = None
        self.pending_update = False
        
        # Initialize sprite parameters and definitions
        self._init_sprite_data()
        
        # Animation parameters
        self.animated_output = False
        self.frame_count = 16
        self.atlas_rows = 4
        self.atlas_cols = 4
        
        # Animation settings per parameter
        self.anim_enabled = {}  # param_key: bool
        self.anim_start = {}    # param_key: value
        self.anim_end = {}      # param_key: value
        self.anim_style = {}    # param_key: "linear"/"pingpong"/"random"
        self.anim_curve = {}    # param_key: "linear"/"ease_in"/"ease_out"/"ease_inout"/"stepped"
        
        # Preview mode and animation
        self.preview_mode = "Single"  # Single, Atlas, or Animation
        self.atlas_frames = []  # Store frames for animation preview
        self.current_frame = 0
        self.animation_timer = None
        self.playback_fps = 12
        
        # Store original pixmaps for re-scaling on resize
        self.original_preview_pixmap = None
        self.original_export_pixmap = None
        
        # Resize throttling
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.on_resize_complete)
        self.resize_timer.setInterval(50)  # 50ms debounce
        
        # Theme
        self.dark_mode = True
        
        # Setup UI
        self.init_ui()
        self.create_menu_bar()
        self.apply_theme()
        
        # Initialize atlas controls
        self.on_atlas_mode_changed("Auto (Square)")
        
        # Initial preview
        self.update_preview()
    
    def _init_sprite_data(self):
        """Initialize sprite parameters and definitions."""
        # Default parameters for each sprite type
        self.sprite_params = {
            'Circle': {
                'radius': 0.4, 'softness': 0.1, 'gradient': False,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Square': {
                'size': 0.6, 'softness': 0.1, 'rotation': 0, 'gradient': False,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Line': {
                'thickness': 0.1, 'softness': 0.2, 'angle': 0, 'length': 0.8, 'length_falloff': True,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'N-Gon': {
                'sides': 6, 'radius': 0.4, 'softness': 0.1, 'rotation': 0, 'gradient': False,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Star': {
                'points': 5, 'outer_radius': 0.4, 'inner_radius': 0.2, 'softness': 0.1, 
                'rotation': 0, 'gradient': False,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Glow': {
                'intensity': 1.0, 'falloff': 2.0, 'radius': 0.5, 'blur': 0.0,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Flame': {
                'height': 0.8, 'width': 0.5, 'turbulence': 0.3, 'falloff': 2.0, 
                'blur': 1.0, 'seed': 42,
                'color_r': 255, 'color_g': 128, 'color_b': 0, 'alpha': 1.0
            },
            'Sparkle': {
                'rays': 4, 'thickness': 0.05, 'length': 0.8, 'softness': 0.15, 'rotation': 0,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Noise': {
                'scale': 0.1, 'octaves': 3, 'seed': 42, 'contrast': 1.0, 'threshold': 0.0,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Gradient': {
                'gradient_type': 'radial', 'angle': 0, 'falloff': 1.0,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Ring': {
                'outer_radius': 0.4, 'inner_radius': 0.25, 'softness': 0.1, 'gradient': False,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            },
            'Cross': {
                'thickness': 0.1, 'softness': 0.1, 'rotation': 0,
                'color_r': 255, 'color_g': 255, 'color_b': 255, 'alpha': 1.0
            }
        }
        
        # Parameter definitions (label, key, min, max, default, scale, tooltip)
        self.param_definitions = {
            'Circle': [
                ('Radius', 'radius', 0, 100, 40, 0.01, 'Size of the circle'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness/falloff'),
            ],
            'Square': [
                ('Size', 'size', 0, 100, 60, 0.01, 'Size of the square'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness/falloff'),
                ('Rotation', 'rotation', 0, 360, 0, 1.0, 'Rotation angle in degrees'),
            ],
            'Line': [
                ('Thickness', 'thickness', 0, 100, 10, 0.01, 'Line thickness'),
                ('Softness', 'softness', 0, 100, 20, 0.01, 'Edge softness'),
                ('Angle', 'angle', 0, 360, 0, 1.0, 'Line angle in degrees'),
                ('Length', 'length', 0, 100, 80, 0.01, 'Line length'),
            ],
            'N-Gon': [
                ('Sides', 'sides', 3, 12, 6, 1.0, 'Number of sides'),
                ('Radius', 'radius', 0, 100, 40, 0.01, 'Polygon radius'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness'),
                ('Rotation', 'rotation', 0, 360, 0, 1.0, 'Rotation angle'),
            ],
            'Star': [
                ('Points', 'points', 3, 12, 5, 1.0, 'Number of star points'),
                ('Outer Radius', 'outer_radius', 0, 100, 40, 0.01, 'Outer point radius'),
                ('Inner Radius', 'inner_radius', 0, 100, 20, 0.01, 'Inner point radius'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness'),
                ('Rotation', 'rotation', 0, 360, 0, 1.0, 'Rotation angle'),
            ],
            'Glow': [
                ('Intensity', 'intensity', 0, 100, 100, 0.01, 'Overall brightness'),
                ('Falloff', 'falloff', 0, 50, 20, 0.1, 'Falloff curve power'),
                ('Radius', 'radius', 0, 100, 50, 0.01, 'Glow radius'),
                ('Blur', 'blur', 0, 100, 0, 0.01, 'Gaussian blur amount'),
            ],
            'Flame': [
                ('Height', 'height', 0, 100, 80, 0.01, 'Flame height'),
                ('Width', 'width', 0, 100, 50, 0.01, 'Flame base width'),
                ('Turbulence', 'turbulence', 0, 100, 30, 0.01, 'Edge turbulence'),
                ('Falloff', 'falloff', 0, 50, 20, 0.1, 'Intensity falloff'),
                ('Blur', 'blur', 0, 100, 10, 0.1, 'Smoothing blur'),
                ('Seed', 'seed', 0, 1000, 42, 1.0, 'Random seed'),
            ],
            'Sparkle': [
                ('Rays', 'rays', 2, 12, 4, 1.0, 'Number of rays'),
                ('Thickness', 'thickness', 0, 50, 5, 0.01, 'Ray thickness'),
                ('Length', 'length', 0, 100, 80, 0.01, 'Ray length'),
                ('Softness', 'softness', 0, 100, 15, 0.01, 'Edge softness'),
                ('Rotation', 'rotation', 0, 360, 0, 1.0, 'Rotation angle'),
            ],
            'Noise': [
                ('Scale', 'scale', 1, 100, 10, 0.01, 'Noise scale/frequency'),
                ('Octaves', 'octaves', 1, 8, 3, 1.0, 'Detail layers'),
                ('Seed', 'seed', 0, 1000, 42, 1.0, 'Random seed'),
                ('Contrast', 'contrast', 0, 300, 100, 0.01, 'Contrast adjustment'),
                ('Threshold', 'threshold', 0, 100, 0, 0.01, 'Cutoff threshold'),
            ],
            'Gradient': [
                ('Angle', 'angle', 0, 360, 0, 1.0, 'Linear gradient angle'),
                ('Falloff', 'falloff', 0, 50, 10, 0.1, 'Gradient falloff curve'),
            ],
            'Ring': [
                ('Outer Radius', 'outer_radius', 0, 100, 40, 0.01, 'Ring outer radius'),
                ('Inner Radius', 'inner_radius', 0, 100, 25, 0.01, 'Ring inner radius'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness'),
            ],
            'Cross': [
                ('Thickness', 'thickness', 0, 50, 10, 0.01, 'Cross bar thickness'),
                ('Softness', 'softness', 0, 100, 10, 0.01, 'Edge softness'),
                ('Rotation', 'rotation', 0, 360, 0, 1.0, 'Rotation angle'),
            ]
        }
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Preview and Export
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 2)
    
    def create_menu_bar(self):
        """Create menu bar with File and View menus."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Sprite...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_sprite)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        self.theme_action = QAction("Switch to Light Mode", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
    
    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.theme_action.setText("Switch to Light Mode" if self.dark_mode else "Switch to Dark Mode")
    
    def apply_theme(self):
        """Apply dark or light theme."""
        if self.dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QComboBox, QLineEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 3px;
                    color: #e0e0e0;
                }
                QSpinBox {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 3px 2px;
                    color: #e0e0e0;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: right;
                    width: 16px;
                    border-left: 1px solid #555;
                    background-color: #4a4a4a;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: left;
                    width: 16px;
                    border-right: 1px solid #555;
                    background-color: #4a4a4a;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #5a5a5a;
                }
                QSpinBox::up-arrow {
                    image: none;
                    border: none;
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 6px solid #e0e0e0;
                    margin: 0 auto;
                }
                QSpinBox::down-arrow {
                    image: none;
                    border: none;
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid #e0e0e0;
                    margin: 0 auto;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QSlider::groove:horizontal {
                    background: #3a3a3a;
                    height: 6px;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #5a9fd4;
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QCheckBox {
                    color: #e0e0e0;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #555;
                    border-radius: 3px;
                    background-color: #3a3a3a;
                }
                QCheckBox::indicator:checked {
                    background-color: #3a3a3a;
                    border: 1px solid #4CAF50;
                    background-image: radial-gradient(circle, #4CAF50 0%, #4CAF50 50%, transparent 50%);
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #6a9fd4;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected {
                    background-color: #3a3a3a;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #555;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f0f0f0;
                    color: #333;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #fff;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QComboBox, QLineEdit {
                    background-color: #fff;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    padding: 3px;
                    color: #333;
                }
                QSpinBox {
                    background-color: #fff;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    padding: 3px 2px;
                    color: #333;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: right;
                    width: 16px;
                    border-left: 1px solid #ccc;
                    background-color: #f5f5f5;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: left;
                    width: 16px;
                    border-right: 1px solid #ccc;
                    background-color: #f5f5f5;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #e0e0e0;
                }
                QSpinBox::up-arrow {
                    image: none;
                    border: none;
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 6px solid #333;
                    margin: 0 auto;
                }
                QSpinBox::down-arrow {
                    image: none;
                    border: none;
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid #333;
                    margin: 0 auto;
                }
                QLabel {
                    color: #333;
                }
                QSlider::groove:horizontal {
                    background: #ddd;
                    height: 6px;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #5a9fd4;
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QCheckBox {
                    color: #333;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background-color: #fff;
                }
                QCheckBox::indicator:checked {
                    background-color: #fff;
                    border: 1px solid #4CAF50;
                    background-image: radial-gradient(circle, #4CAF50 0%, #4CAF50 50%, transparent 50%);
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #6a9fd4;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #333;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                }
                QMenu::item:selected {
                    background-color: #e8e8e8;
                }
            """)
    
    def create_control_panel(self):
        """Create control panel with parameters."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Sprite Type Selection
        type_group = QGroupBox("Sprite Type")
        type_layout = QVBoxLayout()
        self.sprite_combo = QComboBox()
        self.sprite_combo.addItems([
            "Circle", "Square", "Line", "N-Gon", "Star", 
            "Glow", "Flame", "Sparkle", "Noise", "Gradient", "Ring", "Cross"
        ])
        self.sprite_combo.currentTextChanged.connect(self.on_sprite_type_changed)
        type_layout.addWidget(self.sprite_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Parameters Group
        params_group = QGroupBox("Parameters")
        self.params_layout = QVBoxLayout()
        self.sliders = {}
        
        # Add animation tip
        anim_tip = QLabel("💡 Tip: Check ☑️ next to any parameter to animate it")
        anim_tip.setStyleSheet("font-size: 10px; color: #888; font-style: italic; padding: 5px;")
        anim_tip.setWordWrap(True)
        self.params_layout.addWidget(anim_tip)
        
        # Note: Will be populated after all UI elements are created
        
        params_group.setLayout(self.params_layout)
        layout.addWidget(params_group)
        
        # Color and Alpha Controls
        color_group = QGroupBox("Color & Alpha")
        color_layout = QVBoxLayout()
        
        # Main color row with checkbox and button
        color_main_row = QHBoxLayout()
        
        # Color animation checkbox
        self.color_anim_checkbox = QCheckBox()
        self.color_anim_checkbox.setToolTip("Enable color animation")
        self.color_anim_checkbox.setFixedWidth(20)
        self.color_anim_checkbox.setChecked(False)
        self.color_anim_checkbox.toggled.connect(self.on_color_anim_changed)
        color_main_row.addWidget(self.color_anim_checkbox)
        
        color_label = QLabel("Color:")
        color_label.setMinimumWidth(80)
        color_main_row.addWidget(color_label)
        
        # Square color picker button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 50)  # Square shape like Photoshop
        self.update_color_button()
        self.color_button.clicked.connect(self.pick_color)
        color_main_row.addWidget(self.color_button)
        color_main_row.addStretch()
        color_layout.addLayout(color_main_row)
        
        # Color animation controls (start/end colors)
        self.color_anim_row = QWidget()
        color_anim_layout = QHBoxLayout(self.color_anim_row)
        color_anim_layout.setContentsMargins(25, 2, 0, 2)
        color_anim_layout.setSpacing(5)
        
        color_anim_layout.addWidget(QLabel("Start:"))
        self.color_start_button = QPushButton()
        self.color_start_button.setFixedSize(40, 40)
        self.color_start_button.clicked.connect(self.pick_color_start)
        color_anim_layout.addWidget(self.color_start_button)
        
        color_anim_layout.addWidget(QLabel("End:"))
        self.color_end_button = QPushButton()
        self.color_end_button.setFixedSize(40, 40)
        self.color_end_button.clicked.connect(self.pick_color_end)
        color_anim_layout.addWidget(self.color_end_button)
        color_anim_layout.addStretch()
        
        self.color_anim_row.setVisible(False)
        color_layout.addWidget(self.color_anim_row)
        
        # Initialize color animation
        self.color_anim_enabled = False
        self.color_start = (255, 255, 255)
        self.color_end = (255, 255, 255)
        self.update_color_anim_buttons()
        
        # Alpha slider
        self.add_slider(color_layout, "Alpha", 'alpha', 0, 100, 100, scale=0.01, 
                       tooltip='Sprite opacity')
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Checkboxes
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.gradient_checkbox = QCheckBox("Gradient Fill")
        self.gradient_checkbox.setChecked(False)
        self.gradient_checkbox.setToolTip("Apply gradient fill to shape")
        self.gradient_checkbox.stateChanged.connect(self.on_option_changed)
        options_layout.addWidget(self.gradient_checkbox)
        
        self.length_falloff_checkbox = QCheckBox("Length Falloff")
        self.length_falloff_checkbox.setChecked(True)
        self.length_falloff_checkbox.setToolTip("Apply length falloff to line")
        self.length_falloff_checkbox.stateChanged.connect(self.on_option_changed)
        options_layout.addWidget(self.length_falloff_checkbox)
        
        # Gradient type (for Gradient sprite)
        gradient_type_row = QHBoxLayout()
        gradient_type_label = QLabel("Gradient Type:")
        gradient_type_row.addWidget(gradient_type_label)
        self.gradient_type_combo = QComboBox()
        self.gradient_type_combo.addItems(["radial", "linear"])
        self.gradient_type_combo.currentTextChanged.connect(self.on_gradient_type_changed)
        gradient_type_row.addWidget(self.gradient_type_combo)
        options_layout.addLayout(gradient_type_row)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel(f"v{VERSION} - Andy Moorer 2025")
        version_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(version_label)
        
        # Now populate parameters after all UI elements exist
        self.populate_parameters()
        
        return panel
    
    def create_preview_panel(self):
        """Create preview and export panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Preview
        preview_group = QGroupBox("Preview (Live)")
        preview_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        preview_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(100, 100)
        self.preview_label.setMaximumSize(16777215, 16777215)  # Qt max size - allow full expansion
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #222;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_label, 1)  # Remove alignment to allow full expansion
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group, 1)  # Reduce space for live preview
        
        # Export Preview
        export_preview_group = QGroupBox("Export Preview")
        export_preview_layout = QVBoxLayout()
        
        # Preview mode selector
        preview_mode_row = QHBoxLayout()
        mode_label = QLabel("Preview Mode:")
        mode_label.setToolTip("Select what to preview")
        preview_mode_row.addWidget(mode_label)
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["Single", "Atlas", "Animation"])
        self.preview_mode_combo.currentTextChanged.connect(self.on_preview_mode_changed)
        preview_mode_row.addWidget(self.preview_mode_combo, 2)
        
        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.setToolTip("Generate a preview of the selected export mode")
        self.preview_btn.clicked.connect(self.generate_export_preview)
        preview_mode_row.addWidget(self.preview_btn)
        export_preview_layout.addLayout(preview_mode_row)
        
        self.export_preview_label = QLabel("Click 'Generate Preview'\nto see output")
        self.export_preview_label.setMinimumSize(100, 200)  # Increase minimum height
        self.export_preview_label.setMaximumSize(16777215, 16777215)  # Qt max size - allow full expansion
        self.export_preview_label.setStyleSheet("border: 1px solid #ccc; background: #222; color: #888; font-size: 11px;")
        self.export_preview_label.setAlignment(Qt.AlignCenter)
        self.export_preview_label.setWordWrap(True)
        self.export_preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        export_preview_layout.addWidget(self.export_preview_label, 1)  # Remove alignment to allow full expansion
        
        # Info label for dimensions
        self.export_info_label = QLabel("")
        self.export_info_label.setWordWrap(True)
        self.export_info_label.setMinimumHeight(60)
        self.export_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        export_preview_layout.addWidget(self.export_info_label)
        
        # Playback FPS control
        fps_row = QHBoxLayout()
        fps_row.addStretch()
        fps_label = QLabel("Playback FPS:")
        fps_label.setToolTip("Preview animation playback speed (frames per second)")
        fps_row.addWidget(fps_label)
        self.playback_fps_spin = QSpinBox()
        self.playback_fps_spin.setMinimum(1)
        self.playback_fps_spin.setMaximum(60)
        self.playback_fps_spin.setValue(12)
        self.playback_fps_spin.valueChanged.connect(self.on_fps_changed)
        fps_row.addWidget(self.playback_fps_spin)
        export_preview_layout.addLayout(fps_row)
        
        export_preview_group.setLayout(export_preview_layout)
        layout.addWidget(export_preview_group, 5)  # Give export preview maximum space
        
        # Export Settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()
        export_layout.setSpacing(8)  # More comfortable spacing
        
        # Resolution
        res_row = QHBoxLayout()
        res_label = QLabel("Resolution:")
        res_row.addWidget(res_label)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["64x64", "128x128", "256x256", "512x512", "1024x1024"])
        self.resolution_combo.setCurrentText("256x256")
        res_row.addWidget(self.resolution_combo)
        export_layout.addLayout(res_row)
        
        # Animation options
        self.animated_checkbox = QCheckBox("Animated Output (Atlas)")
        self.animated_checkbox.setChecked(False)
        self.animated_checkbox.setToolTip("Export as animated texture atlas")
        self.animated_checkbox.stateChanged.connect(self.on_animated_changed)
        export_layout.addWidget(self.animated_checkbox)
        
        # Frame count
        frame_row = QHBoxLayout()
        frame_label = QLabel("Frame Count:")
        frame_row.addWidget(frame_label)
        self.frame_spin = QSpinBox()
        self.frame_spin.setMinimum(2)
        self.frame_spin.setMaximum(64)
        self.frame_spin.setValue(16)
        self.frame_spin.valueChanged.connect(self.on_frame_count_changed)
        frame_row.addWidget(self.frame_spin)
        export_layout.addLayout(frame_row)
        
        # Atlas mode
        atlas_mode_row = QHBoxLayout()
        atlas_mode_label = QLabel("Atlas Mode:")
        atlas_mode_row.addWidget(atlas_mode_label)
        self.atlas_mode_combo = QComboBox()
        self.atlas_mode_combo.addItems(["Auto (Square)", "Row Only", "Column Only", "Manual"])
        self.atlas_mode_combo.currentTextChanged.connect(self.on_atlas_mode_changed)
        atlas_mode_row.addWidget(self.atlas_mode_combo)
        export_layout.addLayout(atlas_mode_row)
        
        # Atlas layout
        atlas_row = QHBoxLayout()
        atlas_label = QLabel("Atlas Layout:")
        atlas_row.addWidget(atlas_label)
        atlas_row.addWidget(QLabel("Cols:"))
        self.atlas_cols_spin = QSpinBox()
        self.atlas_cols_spin.setMinimum(1)
        self.atlas_cols_spin.setMaximum(16)
        self.atlas_cols_spin.setValue(4)
        self.atlas_cols_spin.valueChanged.connect(self.on_atlas_layout_changed)
        atlas_row.addWidget(self.atlas_cols_spin)
        atlas_row.addWidget(QLabel("Rows:"))
        self.atlas_rows_spin = QSpinBox()
        self.atlas_rows_spin.setMinimum(1)
        self.atlas_rows_spin.setMaximum(16)
        self.atlas_rows_spin.setValue(4)
        self.atlas_rows_spin.valueChanged.connect(self.on_atlas_layout_changed)
        atlas_row.addWidget(self.atlas_rows_spin)
        export_layout.addLayout(atlas_row)
        
        # Filename
        filename_row = QHBoxLayout()
        filename_label = QLabel("Filename:")
        filename_row.addWidget(filename_label)
        self.filename_edit = QLineEdit("sprite")
        filename_row.addWidget(self.filename_edit)
        export_layout.addLayout(filename_row)
        
        # Export button
        self.export_button = QPushButton("Export Sprite")
        self.export_button.setStyleSheet("font-weight: bold; padding: 10px;")
        self.export_button.clicked.connect(self.export_sprite)
        export_layout.addWidget(self.export_button)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group, 0)  # No stretch, just minimum space needed
        
        # Removed addStretch() - let preview areas use available space
        
        return panel
    
    def populate_parameters(self):
        """Populate parameter sliders for current sprite type."""
        # Clear existing sliders
        for key, slider_data in self.sliders.items():
            container = slider_data[0]
            self.params_layout.removeWidget(container)
            container.deleteLater()
        self.sliders.clear()
        
        # Clear animation settings for previous sprite type
        self.anim_enabled.clear()
        self.anim_start.clear()
        self.anim_end.clear()
        self.anim_style.clear()
        self.anim_curve.clear()
        
        # Add sliders for current sprite type
        if self.current_sprite_type in self.param_definitions:
            for label, key, min_val, max_val, default, scale, tooltip in self.param_definitions[self.current_sprite_type]:
                self.add_slider(self.params_layout, label, key, min_val, max_val, default, scale, tooltip)
        
        # Update checkbox visibility
        self.update_option_visibility()
    
    def add_slider(self, layout, label, key, min_val, max_val, default, scale=1.0, tooltip=''):
        """Add a parameter slider with animation controls."""
        # Main container
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 2, 0, 2)
        main_layout.setSpacing(2)
        
        # First row: Label, slider, value (wrap in widget for visibility control)
        top_row_widget = QWidget()
        top_row = QHBoxLayout(top_row_widget)
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(5)
        
        # Animation enable checkbox
        anim_checkbox = QCheckBox()
        anim_checkbox.setToolTip("Enable animation for this parameter")
        anim_checkbox.setFixedWidth(20)
        anim_checkbox.setChecked(False)
        anim_checkbox.toggled.connect(lambda checked, k=key: self.on_anim_enabled_changed(k, checked))
        top_row.addWidget(anim_checkbox)
        
        # Label
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(80)
        if tooltip:
            lbl.setToolTip(tooltip)
        top_row.addWidget(lbl)
        
        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(int(default))
        slider.valueChanged.connect(lambda v: self.on_param_changed(key, v * scale))
        top_row.addWidget(slider)
        
        # Value label - show as percentage if scale is 0.01 (normalized 0-1)
        if scale == 0.01:
            value_label = QLabel(f"{int(default)}%")
        elif scale != 1.0:
            value_label = QLabel(f"{default * scale:.2f}")
        else:
            value_label = QLabel(str(default))
        value_label.setFixedWidth(50)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_row.addWidget(value_label)
        
        main_layout.addWidget(top_row_widget)
        
        # Second row: Animation controls (initially hidden)
        anim_row = QWidget()
        anim_v_layout = QVBoxLayout(anim_row)
        anim_v_layout.setContentsMargins(25, 2, 0, 2)
        anim_v_layout.setSpacing(3)
        
        # First line: Start/End values
        values_row = QHBoxLayout()
        values_row.setSpacing(5)
        values_row.addWidget(QLabel("Start:"))
        start_spin = QSpinBox()
        start_spin.setMinimum(min_val)
        start_spin.setMaximum(max_val)
        start_spin.setValue(min_val)
        start_spin.setFixedWidth(65)
        start_spin.valueChanged.connect(lambda v: self.on_anim_start_changed(key, v * scale))
        values_row.addWidget(start_spin)
        
        values_row.addWidget(QLabel("End:"))
        end_spin = QSpinBox()
        end_spin.setMinimum(min_val)
        end_spin.setMaximum(max_val)
        end_spin.setValue(max_val)
        end_spin.setFixedWidth(65)
        end_spin.valueChanged.connect(lambda v: self.on_anim_end_changed(key, v * scale))
        values_row.addWidget(end_spin)
        values_row.addStretch()
        anim_v_layout.addLayout(values_row)
        
        # Second line: Style and Curve
        style_row = QHBoxLayout()
        style_row.setSpacing(5)
        style_row.addWidget(QLabel("Style:"))
        style_combo = QComboBox()
        style_combo.addItems(["Linear", "Ping Pong", "Random"])
        style_combo.setFixedWidth(100)
        style_combo.currentTextChanged.connect(lambda t: self.on_anim_style_changed(key, t))
        style_row.addWidget(style_combo)
        
        style_row.addWidget(QLabel("Curve:"))
        curve_combo = QComboBox()
        curve_combo.addItems(["Linear", "Ease In", "Ease Out", "Ease In/Out", "Stepped"])
        curve_combo.setFixedWidth(100)
        curve_combo.currentTextChanged.connect(lambda t: self.on_anim_curve_changed(key, t))
        style_row.addWidget(curve_combo)
        style_row.addStretch()
        anim_v_layout.addLayout(style_row)
        
        anim_row.setVisible(False)
        main_layout.addWidget(anim_row)
        
        # Initialize animation settings
        self.anim_enabled[key] = False
        self.anim_start[key] = min_val * scale
        self.anim_end[key] = max_val * scale
        self.anim_style[key] = "Linear"
        self.anim_curve[key] = "Linear"
        
        # Store references
        self.sliders[key] = (container, slider, value_label, scale, anim_checkbox, anim_row, start_spin, end_spin, style_combo, curve_combo, top_row_widget)
        layout.addWidget(container)
    
    def update_color_button(self):
        """Update color button appearance."""
        params = self.sprite_params[self.current_sprite_type]
        r = int(params['color_r'])
        g = int(params['color_g'])
        b = int(params['color_b'])
        self.color_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #999;")
    
    def pick_color(self):
        """Open color picker dialog."""
        params = self.sprite_params[self.current_sprite_type]
        current_color = QColor(int(params['color_r']), int(params['color_g']), int(params['color_b']))
        
        color = QColorDialog.getColor(current_color, self, "Select Sprite Color")
        if color.isValid():
            params['color_r'] = color.red()
            params['color_g'] = color.green()
            params['color_b'] = color.blue()
            self.update_color_button()
            self.update_preview()
    
    def pick_color_start(self):
        """Pick start color for animation."""
        current = QColor(*self.color_start)
        color = QColorDialog.getColor(current, self, "Select Start Color")
        if color.isValid():
            self.color_start = (color.red(), color.green(), color.blue())
            self.update_color_anim_buttons()
    
    def pick_color_end(self):
        """Pick end color for animation."""
        current = QColor(*self.color_end)
        color = QColorDialog.getColor(current, self, "Select End Color")
        if color.isValid():
            self.color_end = (color.red(), color.green(), color.blue())
            self.update_color_anim_buttons()
    
    def update_color_anim_buttons(self):
        """Update appearance of color animation buttons."""
        r, g, b = self.color_start
        self.color_start_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #999;")
        r, g, b = self.color_end
        self.color_end_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #999;")
    
    def on_color_anim_changed(self, enabled):
        """Handle color animation enable/disable."""
        self.color_anim_enabled = enabled
        self.color_anim_row.setVisible(enabled)
        self.color_button.setVisible(not enabled)
    
    def update_option_visibility(self):
        """Update visibility of option checkboxes based on sprite type."""
        # Gradient checkbox
        has_gradient = self.current_sprite_type in ['Circle', 'Square', 'N-Gon', 'Star', 'Ring']
        self.gradient_checkbox.setVisible(has_gradient)
        
        # Length falloff checkbox
        has_length_falloff = self.current_sprite_type == 'Line'
        self.length_falloff_checkbox.setVisible(has_length_falloff)
        
        # Gradient type combo
        is_gradient_sprite = self.current_sprite_type == 'Gradient'
        self.gradient_type_combo.setVisible(is_gradient_sprite)
        self.gradient_type_combo.parentWidget().setVisible(is_gradient_sprite)
    
    def on_sprite_type_changed(self, sprite_type):
        """Handle sprite type change."""
        self.current_sprite_type = sprite_type
        self.populate_parameters()
        self.update_color_button()
        self.update_preview()
    
    def on_param_changed(self, key, value):
        """Handle parameter change."""
        params = self.sprite_params[self.current_sprite_type]
        params[key] = value
        
        # Update value label
        if key in self.sliders:
            slider_data = self.sliders[key]
            value_label = slider_data[2]
            scale = slider_data[3]
            if scale == 0.01:
                # Normalized parameters - show as percentage
                value_label.setText(f"{int(value * 100)}%")
            elif scale != 1.0:
                value_label.setText(f"{value:.2f}")
            else:
                value_label.setText(str(int(value)))
        
        self.update_preview()
    
    def on_anim_enabled_changed(self, key, enabled):
        """Handle animation enable/disable for a parameter."""
        self.anim_enabled[key] = enabled
        
        # Show/hide animation controls and slider
        if key in self.sliders:
            anim_row = self.sliders[key][5]
            top_row_widget = self.sliders[key][10]
            anim_row.setVisible(enabled)
            # Hide main slider when animating, but keep checkbox visible
            # We need to hide slider and value label, but keep the checkbox and label
            slider = self.sliders[key][1]
            value_label = self.sliders[key][2]
            slider.setVisible(not enabled)
            value_label.setVisible(not enabled)
    
    def on_anim_start_changed(self, key, value):
        """Handle animation start value change."""
        self.anim_start[key] = value
    
    def on_anim_end_changed(self, key, value):
        """Handle animation end value change."""
        self.anim_end[key] = value
    
    def on_anim_style_changed(self, key, style):
        """Handle animation style change."""
        self.anim_style[key] = style
    
    def on_anim_curve_changed(self, key, curve):
        """Handle animation curve change."""
        self.anim_curve[key] = curve
    
    def on_option_changed(self):
        """Handle option checkbox change."""
        params = self.sprite_params[self.current_sprite_type]
        params['gradient'] = self.gradient_checkbox.isChecked()
        params['length_falloff'] = self.length_falloff_checkbox.isChecked()
        self.update_preview()
    
    def on_gradient_type_changed(self, gradient_type):
        """Handle gradient type change."""
        params = self.sprite_params[self.current_sprite_type]
        params['gradient_type'] = gradient_type
        self.update_preview()
    
    def on_animated_changed(self, state):
        """Handle animated checkbox change."""
        self.animated_output = (state == Qt.Checked)
    
    def on_frame_count_changed(self, value):
        """Handle frame count change."""
        self.frame_count = value
        # Auto-calculate optimal atlas layout
        self.auto_calculate_atlas_layout()
    
    def on_atlas_mode_changed(self, mode):
        """Handle atlas mode change."""
        # Enable/disable manual controls
        is_manual = mode == "Manual"
        self.atlas_cols_spin.setEnabled(is_manual)
        self.atlas_rows_spin.setEnabled(is_manual)
        
        # Auto-calculate if not manual
        if not is_manual:
            self.auto_calculate_atlas_layout()
    
    def auto_calculate_atlas_layout(self):
        """Automatically calculate atlas rows and columns based on frame count and mode."""
        import math
        
        mode = self.atlas_mode_combo.currentText()
        
        if mode == "Manual":
            # Don't auto-calculate in manual mode
            return
        elif mode == "Row Only":
            # Single row, all frames in columns
            cols = self.frame_count
            rows = 1
        elif mode == "Column Only":
            # Single column, all frames in rows
            cols = 1
            rows = self.frame_count
        else:  # Auto (Square)
            # Calculate square root and round up
            sqrt_frames = math.ceil(math.sqrt(self.frame_count))
            
            # Try to make it as square as possible
            cols = sqrt_frames
            rows = math.ceil(self.frame_count / cols)
        
        # Update spinners without triggering signals
        self.atlas_cols_spin.blockSignals(True)
        self.atlas_rows_spin.blockSignals(True)
        self.atlas_cols_spin.setValue(cols)
        self.atlas_rows_spin.setValue(rows)
        self.atlas_cols_spin.blockSignals(False)
        self.atlas_rows_spin.blockSignals(False)
        
        # Update state
        self.atlas_cols = cols
        self.atlas_rows = rows
    
    def on_atlas_layout_changed(self):
        """Handle atlas layout change."""
        self.atlas_rows = self.atlas_rows_spin.value()
        self.atlas_cols = self.atlas_cols_spin.value()
    
    def on_preview_mode_changed(self, mode):
        """Handle preview mode change."""
        self.preview_mode = mode
        # Stop animation if switching away from Animation mode
        if mode != "Animation" and self.animation_timer:
            self.animation_timer.stop()
    
    def on_fps_changed(self, fps):
        """Handle FPS change."""
        self.playback_fps = fps
        # Restart animation timer with new FPS if currently playing
        if self.animation_timer and self.animation_timer.isActive():
            self.animation_timer.stop()
            self.animation_timer.start(1000 // self.playback_fps)
    
    def generate_export_preview(self):
        """Generate preview based on selected mode."""
        try:
            params = self.sprite_params[self.current_sprite_type].copy()
            # Use actual export resolution for preview (will be scaled down if needed)
            export_res = int(self.resolution_combo.currentText().split('x')[0])
            # Cap at 1024 for preview performance, but show full res if <= 1024
            preview_size = min(export_res, 1024)
            
            if self.preview_mode == "Single":
                # Generate single sprite
                sprite = SpriteGenerator.generate(
                    self.current_sprite_type,
                    preview_size,
                    preview_size,
                    params
                )
                
                # Convert to QImage and display
                h, w = sprite.shape[:2]
                bytes_per_line = w * 4
                qimage = QImage(sprite.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)
                self.set_scaled_pixmap(self.export_preview_label, pixmap)
                
                # Update info - show actual export size
                self.export_info_label.setText(
                    f"Single Sprite\n"
                    f"Export Size: {export_res}x{export_res}px"
                )
                
            elif self.preview_mode == "Atlas":
                # Generate atlas preview using actual export resolution
                cols = self.atlas_cols
                rows = self.atlas_rows
                
                # Use actual cell size from export resolution, cap at 512 per cell for preview
                cell_size = min(export_res, 512)
                
                # Calculate atlas dimensions based on cell size and grid
                atlas_w = cell_size * cols
                atlas_h = cell_size * rows
                
                # Create atlas image with visible background (medium gray) and border
                # Background color clearly distinguishes atlas from label background
                atlas = Image.new('RGBA', (atlas_w, atlas_h), (60, 60, 60, 255))
                
                # Draw border to show atlas extent
                from PIL import ImageDraw
                draw = ImageDraw.Draw(atlas)
                draw.rectangle([0, 0, atlas_w-1, atlas_h-1], outline=(100, 150, 200, 255), width=2)
                
                total_frames = min(self.frame_count, cols * rows)
                for frame in range(total_frames):
                    # Get animated parameters for this frame
                    frame_params = self.get_animated_params(frame, total_frames)
                    
                    sprite = SpriteGenerator.generate(
                        self.current_sprite_type,
                        cell_size,
                        cell_size,
                        frame_params
                    )
                    
                    frame_image = Image.fromarray(sprite, mode='RGBA')
                    col = frame % cols
                    row = frame // cols
                    atlas.paste(frame_image, (col * cell_size, row * cell_size))
                
                # Convert to QPixmap
                atlas_array = np.array(atlas)
                h, w = atlas_array.shape[:2]
                bytes_per_line = w * 4
                qimage = QImage(atlas_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)
                self.set_scaled_pixmap(self.export_preview_label, pixmap)
                
                # Calculate actual export dimensions
                export_res = int(self.resolution_combo.currentText().split('x')[0])
                export_atlas_w = export_res * cols
                export_atlas_h = export_res * rows
                
                # Update info - show cell size and export atlas size
                self.export_info_label.setText(
                    f"Atlas: {cols}x{rows} = {total_frames} frames\n"
                    f"Cell Size: {export_res}x{export_res}px\n"
                    f"Export Size: {export_atlas_w}x{export_atlas_h}px"
                )
                
            elif self.preview_mode == "Animation":
                # Generate frames for animation
                self.atlas_frames = []
                frame_size = preview_size
                total_frames = min(self.frame_count, 16)
                
                for frame in range(total_frames):  # Limit preview frames
                    # Get animated parameters for this frame
                    frame_params = self.get_animated_params(frame, total_frames)
                    
                    sprite = SpriteGenerator.generate(
                        self.current_sprite_type,
                        frame_size,
                        frame_size,
                        frame_params
                    )
                    
                    # Convert to QPixmap
                    h, w = sprite.shape[:2]
                    bytes_per_line = w * 4
                    qimage = QImage(sprite.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(qimage)
                    self.atlas_frames.append(pixmap)
                
                # Start animation
                self.current_frame = 0
                self.play_animation()
                
                # Update info
                self.export_info_label.setText(
                    f"Animation Preview\n"
                    f"Frames: {len(self.atlas_frames)}\n"
                    f"Frame Size: {frame_size}x{frame_size}px\n"
                    f"FPS: {self.playback_fps}"
                )
        
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Failed to generate preview:\n{str(e)}")
    
    def play_animation(self):
        """Play animation preview."""
        if not self.atlas_frames:
            return
        
        # Stop existing timer
        if self.animation_timer:
            self.animation_timer.stop()
        
        # Create new timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_animation_frame)
        self.animation_timer.start(1000 // self.playback_fps)  # Convert FPS to ms
    
    def next_animation_frame(self):
        """Display next animation frame."""
        if not self.atlas_frames:
            return
        
        self.set_scaled_pixmap(self.export_preview_label, self.atlas_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.atlas_frames)
    
    def calculate_animated_value(self, key, frame, total_frames):
        """Calculate parameter value for a given frame based on animation settings."""
        if not self.anim_enabled.get(key, False):
            # Animation not enabled, return current value
            params = self.sprite_params[self.current_sprite_type]
            return params.get(key, 0)
        
        start = self.anim_start.get(key, 0)
        end = self.anim_end.get(key, 1)
        style = self.anim_style.get(key, "Linear")
        curve = self.anim_curve.get(key, "Linear")
        
        # Calculate progress (0.0 to 1.0)
        if total_frames <= 1:
            progress = 0.0
        else:
            progress = frame / (total_frames - 1)
        
        # Apply animation style
        if style == "Ping Pong":
            # Bounce back and forth
            if progress <= 0.5:
                progress = progress * 2  # 0 to 1
            else:
                progress = 2 - (progress * 2)  # 1 back to 0
        elif style == "Random":
            # Random value between start and end
            import random
            random.seed(frame)  # Use frame as seed for consistency
            return start + random.random() * (end - start)
        
        # Apply animation curve
        progress = self.apply_curve(progress, curve)
        
        # Interpolate between start and end
        value = start + (end - start) * progress
        return value
    
    def apply_curve(self, t, curve_type):
        """Apply easing curve to progress value (0 to 1)."""
        import math
        
        if curve_type == "Linear":
            return t
        elif curve_type == "Ease In":
            return t * t
        elif curve_type == "Ease Out":
            return 1 - (1 - t) * (1 - t)
        elif curve_type == "Ease In/Out":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - math.pow(-2 * t + 2, 2) / 2
        elif curve_type == "Stepped":
            # Snap to 0 or 1 based on threshold
            return 0.0 if t < 0.5 else 1.0
        else:
            return t
    
    def get_animated_params(self, frame, total_frames):
        """Get parameters with animation applied for a specific frame."""
        params = self.sprite_params[self.current_sprite_type].copy()
        
        # Apply animation to each parameter that has it enabled
        for key in self.anim_enabled:
            if self.anim_enabled[key]:
                params[key] = self.calculate_animated_value(key, frame, total_frames)
        
        # Apply color animation if enabled
        if self.color_anim_enabled:
            t = frame / max(total_frames - 1, 1)
            # Linear interpolation between start and end colors
            start_r, start_g, start_b = self.color_start
            end_r, end_g, end_b = self.color_end
            params['color_r'] = int(start_r + (end_r - start_r) * t)
            params['color_g'] = int(start_g + (end_g - start_g) * t)
            params['color_b'] = int(start_b + (end_b - start_b) * t)
        
        return params
    
    def update_preview(self):
        """Update preview with current parameters."""
        if self.generation_thread and self.generation_thread.isRunning():
            self.pending_update = True
            return
        
        self.status_label.setText("Generating...")
        self.status_label.setStyleSheet("color: #fa0; font-weight: bold;")
        
        params = self.sprite_params[self.current_sprite_type].copy()
        
        self.generation_thread = SpriteGeneratorThread(
            self.current_sprite_type,
            self.preview_size,
            self.preview_size,
            params
        )
        self.generation_thread.finished.connect(self.on_preview_ready)
        self.generation_thread.start()
    
    def set_scaled_pixmap(self, label, pixmap, store_original=True):
        """Set a pixmap on a label with proper scaling to fit while maintaining aspect ratio."""
        if pixmap.isNull():
            return
        
        # Clear any text in the label
        label.setText("")
        
        # Store original pixmap for re-scaling on resize
        if store_original:
            if label == self.preview_label:
                self.original_preview_pixmap = pixmap
            elif label == self.export_preview_label:
                self.original_export_pixmap = pixmap
        
        # Get label size
        label_size = label.size()
        
        # Only scale down, never up (max 100%)
        if pixmap.width() <= label_size.width() and pixmap.height() <= label_size.height():
            # Pixmap fits, don't scale up
            label.setPixmap(pixmap)
        else:
            # Scale down to fit
            scaled_pixmap = pixmap.scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """Handle window resize to re-scale preview images."""
        super().resizeEvent(event)
        
        # Restart the debounce timer - only re-scale after resize settles
        self.resize_timer.start()
    
    def on_resize_complete(self):
        """Called after resize completes (debounced)."""
        # Re-scale preview images with stored originals
        if self.original_preview_pixmap:
            self.set_scaled_pixmap(
                self.preview_label, 
                self.original_preview_pixmap,
                store_original=False
            )
        
        if self.original_export_pixmap:
            self.set_scaled_pixmap(
                self.export_preview_label,
                self.original_export_pixmap,
                store_original=False
            )
    
    def on_preview_ready(self, sprite):
        """Handle preview generation complete."""
        self.current_sprite = sprite
        
        # Convert to QImage
        h, w = sprite.shape[:2]
        bytes_per_line = w * 4
        qimage = QImage(sprite.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        
        self.set_scaled_pixmap(self.preview_label, pixmap)
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #0a0; font-weight: bold;")
        
        # Handle pending update
        if self.pending_update:
            self.pending_update = False
            QTimer.singleShot(50, self.update_preview)
    
    def export_sprite(self):
        """Export sprite to file."""
        try:
            # Get export resolution
            res_text = self.resolution_combo.currentText()
            resolution = int(res_text.split('x')[0])
            
            # Get filename
            base_filename = self.filename_edit.text() or "sprite"
            
            # Choose save location
            default_filename = f"{base_filename}.png"
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Save Sprite",
                default_filename,
                "PNG Files (*.png)"
            )
            
            if not filepath:
                return
            
            # Auto-version if file exists
            filepath = self.get_versioned_filename(filepath)
            
            if self.animated_output:
                self.export_animated_atlas(filepath, resolution)
            else:
                self.export_single_sprite(filepath, resolution)
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Sprite exported successfully to:\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export sprite:\n{str(e)}"
            )
    
    def export_single_sprite(self, filepath, resolution):
        """Export single sprite."""
        params = self.sprite_params[self.current_sprite_type].copy()
        
        sprite = SpriteGenerator.generate(
            self.current_sprite_type,
            resolution,
            resolution,
            params
        )
        
        # Save as PNG
        image = Image.fromarray(sprite, mode='RGBA')
        image.save(filepath, 'PNG')
    
    def export_animated_atlas(self, filepath, resolution):
        """Export animated sprite atlas."""
        # Calculate atlas dimensions
        atlas_width = resolution * self.atlas_cols
        atlas_height = resolution * self.atlas_rows
        
        # Create atlas image
        atlas = Image.new('RGBA', (atlas_width, atlas_height), (0, 0, 0, 0))
        
        # Generate frames
        total_frames = min(self.frame_count, self.atlas_rows * self.atlas_cols)
        for frame in range(total_frames):
            # Get animated parameters for this frame
            frame_params = self.get_animated_params(frame, total_frames)
            
            # Generate frame
            sprite = SpriteGenerator.generate(
                self.current_sprite_type,
                resolution,
                resolution,
                frame_params
            )
            
            # Convert to PIL Image
            frame_image = Image.fromarray(sprite, mode='RGBA')
            
            # Calculate position in atlas
            col = frame % self.atlas_cols
            row = frame // self.atlas_cols
            x = col * resolution
            y = row * resolution
            
            # Paste into atlas
            atlas.paste(frame_image, (x, y))
        
        # Save atlas
        atlas.save(filepath, 'PNG')
    
    def get_versioned_filename(self, filepath):
        """Get versioned filename if file exists."""
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filepath)
        version = 0
        
        while True:
            versioned_path = f"{base}_v{version:02d}{ext}"
            if not os.path.exists(versioned_path):
                return versioned_path
            version += 1
            if version > 99:
                return filepath


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = SpriteGeneratorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()