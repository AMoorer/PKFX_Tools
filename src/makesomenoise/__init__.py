"""
MakeSomeNoise - Procedural Noise Generator
A powerful, user-friendly GUI tool for generating seamless procedural noise textures.
"""

__version__ = "1.1.2"
__author__ = "Samuel A. Moorer"
__license__ = "CC BY-NC-ND 4.0 with Commercial Use Exception"

from .noise_generator_gui import NoiseGeneratorGUI, NoiseGenerator

__all__ = ['NoiseGeneratorGUI', 'NoiseGenerator', '__version__']
