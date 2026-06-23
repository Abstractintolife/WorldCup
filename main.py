"""世界杯赛事终端 — 应用入口。

运行：
    python -m pip install -r requirements.txt
    python main.py
"""
from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys

import qasync
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from app import __app_name__, __version__
from app.api.client import ApiClient
from app.config import ASSETS_DIR
from app.ui.main_window import MainWindow


def configure_logging() -> None:
    level = os.environ.get("WC_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def load_bundled_fonts() -> str | None:
    """注册仓库内置字体（assets/fonts/*.ttf）。

    内置 Inter 作为拉丁文 / 数字主字体 —— 比分、能力值、英文榜单标题
    等大量拉丁字形会更锐利统一；中文则由系统字体（雅黑 / 苹方 /
    思源黑体）自动回退补字。返回首个成功注册的字体族名。
    """
    fonts_dir = ASSETS_DIR / "fonts"
    if not fonts_dir.exists():
        return None
    family: str | None = None
    for ttf in sorted(fonts_dir.glob("*.ttf")):
        fid = QFontDatabase.addApplicationFont(str(ttf))
        if fid < 0:
            continue
        fams = QFontDatabase.applicationFontFamilies(fid)
        if fams and family is None:
            family = fams[0]
    return family


def main() -> int:
    configure_logging()
    log = logging.getLogger("main")
    log.info("启动 %s v%s", __app_name__, __version__)

    # 高 DPI 屏幕缩放
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setOrganizationName("kiro")

    # 应用图标（窗口左上角 / 任务栏 / Alt-Tab）—— 程序化绘制的大力神杯徽章
    from app.ui.design.app_icon import build_app_icon
    app.setWindowIcon(build_app_icon())

    # 全局字体：内置 Inter（拉丁/数字）+ 系统中文字体自动回退。
    # 解决「字体太难看」：统一锐利的拉丁字形 + 抗锯齿 + 轻度 hinting。
    family = load_bundled_fonts()
    font = QFont(family or "Inter")
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    font.setHintingPreference(QFont.HintingPreference.PreferVerticalHinting)
    font.setPointSize(10)
    app.setFont(font)

    # 把 asyncio 与 Qt 事件循环合并
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 应用退出信号：窗口关闭 / 收到系统信号时置位，结束事件循环
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    # 优雅退出
    def _shutdown(*_a) -> None:
        log.info("收到退出信号，正在关闭...")
        QApplication.instance().quit()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _shutdown)
        except (ValueError, AttributeError):
            pass

    async def _bootstrap() -> None:
        # 关键：在事件循环“已经运行”之后再创建窗口。
        # MainWindow 构造期间会触发首页刷新、图片下载等 asyncio 任务
        # （loop.create_task / ensure_future）。如果此时循环尚未运行，
        # qasync 内部定时器 startTimer 会失败返回 0，并因 id 冲突触发
        # AssertionError（“Timers can only be used with threads started
        # with QThread”）。把窗口创建放进 run_until_complete 驱动的协程里，
        # 可确保所有任务调度都在循环运行状态下进行。
        window = MainWindow()
        window.show()
        try:
            await app_close_event.wait()
        finally:
            # 退出前关闭 HTTP 客户端
            try:
                await ApiClient.instance().close()
            except Exception:  # pragma: no cover
                pass

    with loop:
        loop.run_until_complete(_bootstrap())
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
