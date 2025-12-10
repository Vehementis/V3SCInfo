# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for V3SCInfo - Star Citizen Stats Reader
# By V3h3m3ntis for the Hiv3mind Community
# This creates a single executable file that's antivirus-friendly

import sys
import os
from pathlib import Path

# Get the script directory
script_dir = Path.cwd()

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(script_dir)],
    binaries=[],
    datas=[
        # Include any data files if needed
        # ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'customtkinter',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused modules to reduce size
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'pytest',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='V3SCInfo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression to reduce file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon file - you can add an .ico file here
    # icon='icon.ico',
    
    # Version information for Windows
    version_info={
        'version': (1, 0, 0, 0),
        'file_version': (1, 0, 0, 0),
        'product_version': (1, 0, 0, 0),
        'file_description': 'V3SCInfo - Star Citizen Stats Reader by V3h3m3ntis',
        'product_name': 'V3SCInfo',
        'company_name': 'V3h3m3ntis',
        'copyright': 'V3h3m3ntis',
        'original_filename': 'V3SCInfo.exe',
    }
)
