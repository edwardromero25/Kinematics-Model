import os
import sys

block_cipher = None
project_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
ffmpeg_dir = os.path.join(project_dir, 'ffmpeg')
images_dir = os.path.join(project_dir, 'images')

a = Analysis(
    scripts=[os.path.join(project_dir, 'gui.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(images_dir, 'asterisk.png'), 'images'),
        (os.path.join(images_dir, 'favicon.ico'), 'images'),
        (os.path.join(images_dir, 'info.png'), 'images'),
        (os.path.join(images_dir, 'mssf_logo.png'), 'images'),
        (os.path.join(images_dir, 'nasa_logo.png'), 'images'),

        (os.path.join(project_dir, 'fibonacci_lattice.py'), '.'),
        (os.path.join(project_dir, 'math_model.py'), '.'),

        (os.path.join(ffmpeg_dir, 'avcodec-61.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'avdevice-61.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'avfilter-10.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'avformat-61.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'avutil-59.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'ffmpeg.exe'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'postproc-58.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'swresample-5.dll'), 'ffmpeg'),
        (os.path.join(ffmpeg_dir, 'swscale-8.dll'), 'ffmpeg'),
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
    name='Kinematics Model',
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
    icon=[os.path.join(images_dir, 'favicon.ico')],
)