# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Get PySide6 location
import PySide6
pyside6_path = Path(PySide6.__file__).parent

a = Analysis(
    ['src\\makesomenoise\\noise_generator_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(pyside6_path / 'plugins' / 'platforms'), 'PySide6/plugins/platforms'),
        (str(pyside6_path / 'plugins' / 'styles'), 'PySide6/plugins/styles'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'numpy',
        'noise',
        'opensimplex',
        'perlin_noise',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MakeSomeNoise',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
