# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None
project_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

a = Analysis(
    scripts=[os.path.join(project_dir, 'gui.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'images/favicon.ico'), 'images'),
        (os.path.join(project_dir, 'images/MSSF_logo.png'), 'images'),
        (os.path.join(project_dir, 'images/NASA_logo.png'), 'images'),
        (os.path.join(project_dir, 'images/info.png'), 'images'),
        (os.path.join(project_dir, 'images/asterisk.png'), 'images'),
        (os.path.join(project_dir, 'path_visualization.py'), '.'),
        (os.path.join(project_dir, 'math_model.py'), '.'),
        (os.path.join(project_dir, 'ffmpeg/avcodec-61.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/avdevice-61.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/avfilter-10.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/avformat-61.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/avutil-59.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/ffmpeg.exe'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/postproc-58.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/swresample-5.dll'), 'ffmpeg'),
        (os.path.join(project_dir, 'ffmpeg/swscale-8.dll'), 'ffmpeg')
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