# -*- mode: python ; coding: utf-8 -*-
# 一键配置程序打包配置（onefile + windowed）。exe 中文名在这里（Python 文件，UTF-8 安全），
# rebuild.bat 只引用本 spec 文件名（纯 ASCII），避免 .bat 编码问题。

a = Analysis(
    ['oneclick_config.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='社媒监测一键配置',
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
