"""桌面打包模式入口：单进程托管 前端静态页 + API，自动开浏览器。

开发环境请用 uvicorn 起 app.main:app；本入口仅供 PyInstaller 打包使用：
    python -m app.desktop            # 自动打开浏览器
    python -m app.desktop --no-browser
"""
from __future__ import annotations

import socket
import sys
import threading
import webbrowser

PREFERRED_PORT = 18765  # 避开常用端口（8000/5173 等），降低冲突概率


def _find_free_port(preferred: int) -> int:
    for p in [preferred, *range(preferred + 1, preferred + 20)]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return preferred


def main() -> None:
    import uvicorn

    from .main import app  # noqa: WPS433 延迟导入，保证日志/配置就绪

    port = _find_free_port(PREFERRED_PORT)
    url = f"http://127.0.0.1:{port}"

    if "--no-browser" not in sys.argv:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    banner = (
        "\n"
        "  ============================================\n"
        "   社媒监测洞察系统 · 桌面版\n"
        f"   访问地址: {url}\n"
        "   默认账号: Admin / Seek22626301（首次登录改密）\n"
        "   关闭本窗口即停止服务\n"
        "  ============================================\n"
    )
    print(banner, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
