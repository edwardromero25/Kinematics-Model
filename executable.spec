# -*- mode: python ; coding: utf-8 -*-

import os
import sys
block_cipher = None

project_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

a = Analysis(
    [os.path.join(project_dir, 'gui.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'images/favicon.ico'), 'images'),
        (os.path.join(project_dir, 'images/MSSF_logo.png'), 'images'),
        (os.path.join(project_dir, 'images/NASA_logo.png'), 'images'),
        (os.path.join(project_dir, 'spherical_coordinates.py'), '.')
        (os.path.join(project_dir, 'rigid_body.py'), '.')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Computer Model',
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
    icon=[os.path.join(project_dir, 'images/favicon.ico')],
)
