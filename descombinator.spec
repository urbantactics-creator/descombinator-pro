# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Descombinator Pro.

Build with:
    pyinstaller descombinator.spec
"""

import sys
from pathlib import Path

block_cipher = None
root = Path(SPECPATH)

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / "app" / "resources"), "app/resources"),
        (str(root / "assets"), "assets"),
    ],
    hiddenimports=[
        "torch",
        "torch._C",
        "torch.cuda",
        "torch.backends",
        "torch.backends.mkldnn",
        "demucs",
        "demucs.api",
        "demucs.pretrained",
        "demucs.separate",
        "demucs.audio",
        "openunmix",
        "openunmix.ui_model",
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtMultimedia",
        "pyqtgraph",
        "onnxruntime",
        "librosa",
        "soundfile",
        "resampy",
        "mutagen",
        "psutil",
        "numpy",
        "scipy",
        "numpy.core",
        "numpy.core._methods",
        "numpy.lib",
        "numpy.lib.format",
        "numpy.random",
        "scipy.signal",
        "scipy.special",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "IPython",
        "jupyter",
        "notebook",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "win32":
    icon_path = root / "assets/icons/icon.ico"
elif sys.platform == "darwin":
    icon_path = root / "assets/icons/icon.icns"
else:
    icon_path = root / "assets/icons/icon.png"

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="descombinator",
    icon=str(icon_path),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
