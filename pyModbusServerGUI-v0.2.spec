# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

icon="./m.ico",

a = Analysis(
    ['pyModbusServerGUI-v0.2.py'],
    pathex=[],
    binaries=[],
    #添加所有的包到可执行文件中，包括字体文件
    datas=[('./pyModbusTCP/*.py', '.'),('./modbus_server.py','.'),('./Adobe Fangsong Std.otf', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pyModbusServerGUI-v0.2',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyModbusServerGUI-v0.2',
)
