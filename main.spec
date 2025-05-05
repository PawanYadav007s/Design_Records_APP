# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# Include all hidden imports (especially useful for Flask or PyWebView)
hiddenimports = collect_submodules('flask') + collect_submodules('jinja2')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('settings.json', '.'),
    ('templates', 'templates'),
    ('static', 'static'),
    ('design.db', '.')  # ← Include the SQLite DB
],
     hiddenimports=[
        'jinja2.ext',
        'pyvisa.resources.serial',
        'pyvisa_py',
        'zeroconf',
        'serial.tools.list_ports',
                # ✅ correct import name for backend
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon='icon.ico',
    name='Design_Record',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see logs in terminal for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
