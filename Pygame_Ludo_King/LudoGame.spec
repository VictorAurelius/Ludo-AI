# -*- mode: python ; coding: utf-8 -*-


# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Ludo Game Master/game_controller.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('mapfinal', 'mapfinal'),
        ('assets_ver1', 'assets_ver1'),
        ('assets_ver1/assets_nhat', 'assets_ver1/assets_nhat'),
        ('assets_ver1/assets_nhat/Red', 'assets_ver1/assets_nhat/Red'),
        ('assets_ver1/assets_nhat/Blue', 'assets_ver1/assets_nhat/Blue'),
        ('assets_ver1/assets_nhat/Yellow', 'assets_ver1/assets_nhat/Yellow'),
        ('assets_ver1/assets_nhat/Purple', 'assets_ver1/assets_nhat/Purple'),
        ('img', 'img')
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

# Thêm dòng này vào đây
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # Thêm dòng này
    a.zipfiles,       # Thêm dòng này
    a.datas,          # Thêm dòng này
    [],
    name='LudoGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # Thêm dòng này để tạm thời giải nén vào RAM
    console=True,         # Đặt False để ẩn console khi phát hành
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
