"""PyInstaller 打包用启动脚本（绝对导入，避免包内相对导入问题）。"""
from app.desktop import main

if __name__ == "__main__":
    main()
