# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：社媒监测洞察系统 · Windows 桌面版（onedir）。

构建：在 packaging/ 目录下执行
    ..\\.venv\\Scripts\\pyinstaller.exe social-monitor.spec --noconfirm --clean
产物：dist\\社媒监测洞察系统\\  （内含同名 exe + 全部依赖 + 内嵌前端 web/）
"""
from pathlib import Path

ROOT = Path(SPECPATH).parent          # 项目根（数字能源社媒/）
BACKEND = ROOT / "backend"

a = Analysis(
    [str(BACKEND / "run_desktop.py")],
    pathex=[str(BACKEND)],
    binaries=[],
    # 前端构建产物内嵌到 _MEIPASS/web（config.FRONTEND_DIST 会找到它）
    datas=[(str(ROOT / "frontend" / "dist"), "web")],
    hiddenimports=[
        # uvicorn[standard] 按需加载的组件
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        # apscheduler 触发器按需导入
        "apscheduler.triggers.cron",
        "apscheduler.triggers.interval",
        "apscheduler.triggers.date",
        "apscheduler.triggers.combining",
        # SQLAlchemy SQLite 方言
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.dialects.sqlite.pysqlite",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest", "pytest_asyncio", "_pytest",
        "tkinter", "matplotlib", "numpy", "pandas", "PIL",
        "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # onedir 模式
    name="社媒监测洞察系统",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                       # 不开 UPX：避免误报/损坏
    console=True,                    # 保留控制台：测试者能看到日志与报错
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
    upx=False,
    upx_exclude=[],
    name="社媒监测洞察系统",
)
