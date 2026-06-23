"""离屏渲染主窗口截图，便于在无显示器环境下审视 UI 美观度。

用法：
    QT_QPA_PLATFORM=offscreen python tools/screenshot.py <theme> <page> <out.png>
可一次多页： python tools/screenshot.py dark home:/tmp/a.png pred:/tmp/b.png
"""
from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qasync
from PyQt6.QtWidgets import QApplication


async def _run(theme: str, shots: list[tuple[str, str]]) -> None:
    import main as app_main
    try:
        app_main.load_bundled_fonts()
    except Exception:
        pass
    from app.ui.main_window import MainWindow

    w = MainWindow()
    w.resize(1440, 900)
    w._set_skin(theme)
    w.show()
    await asyncio.sleep(0.4)

    for page, out in shots:
        w._sidebar.set_active(page)
        await asyncio.sleep(2.2)        # 等异步数据 + 动画推进
        pm = w.grab()
        pm.save(out, "PNG")
        print(f"saved {out} ({pm.width()}x{pm.height()}) theme={theme} page={page}")


def main() -> None:
    theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
    shots: list[tuple[str, str]] = []
    for arg in sys.argv[2:]:
        if ":" in arg:
            page, out = arg.split(":", 1)
            shots.append((page, out))
    if not shots:
        shots = [("home", "/tmp/shot.png")]

    app = QApplication.instance() or QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_until_complete(_run(theme, shots))


if __name__ == "__main__":
    main()
