# -*- mode: python ; coding: utf-8 -*-


# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['game_controller.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('mapfinal', 'mapfinal'),        # Thêm thư mục chứa file TMX
        ('assets_ver1', 'assets_ver1'),  # Thêm thư mục tài nguyên, điều chỉnh nếu cần
        # Thêm các thư mục tài nguyên khác nếu cần
    ],
    hiddenimports=[
        'main', 'Players', 'Pawns', 'States', 'Stars',
        'alert_manager', 'main_board', 'pytmx'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LudoGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LudoGame',
)
