"""所有页面的基类：异步加载、统一空态/错误态。

设计要点
---------
* **不再使用 ``QStackedWidget``**：之前的设计在某些 Qt 平台 + 嵌套
  ``QScrollArea`` 时会触发子布局延迟激活的 bug，表现为「所有行堆叠
  在 (0,0)」（用户原始反馈：射手 / 助攻榜全部堆在一起）。改为：
  * 单一 ``content`` 容器（QWidget）作为页面正文，由子类填充。
  * 加载态 / 错误态作为 **半透明覆盖层**（QFrame, raise_）出现在
    页面之上 —— 几何独立，不会影响子布局。
* 默认 **「增量刷新」**：``run_async`` 不会切到 loading 覆盖层 —— 仅
  在顶部出现红色霓虹同步条；首屏（``_content_ready=False``）才显示
  完整加载态。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QAbstractScrollArea,
    QFrame,
    QHBoxLayout,
    QLabel,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.ui.design.frame_clock import FrameClock
from app.ui.widgets.misc import Spinner

log = logging.getLogger(__name__)


class _LoadingBar(QWidget):
    """页面顶部的霓虹同步光带（refreshing 时出现，由 FrameClock 驱动）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(2)
        self._pos = -0.4
        self._clock = FrameClock.instance()
        self._subscribed = False
        self.hide()

    def start(self) -> None:
        self.show()
        self.raise_()
        if not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def stop(self) -> None:
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False
        self.hide()

    def _on_frame(self, _t: float, dt: float) -> None:
        self._pos += dt * 1.3
        if self._pos > 1.4:
            self._pos = -0.4
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        rect = self.rect()
        w = rect.width()
        g = QLinearGradient(self._pos * w - 80, 0, self._pos * w + 80, 0)
        g.setColorAt(0.0, QColor(0, 191, 255, 0))
        g.setColorAt(0.5, QColor(70, 210, 255, 230))
        g.setColorAt(1.0, QColor(0, 191, 255, 0))
        p.fillRect(rect, g)


class _Overlay(QFrame):
    """半透明遮罩覆盖层（加载 / 错误用）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "background: rgba(11,16,32,0.82);"
            "border: none;"
        )
        self.hide()

    def show_over(self, parent: QWidget) -> None:
        self.setParent(parent)
        self.setGeometry(parent.rect())
        self.raise_()
        self.show()


class BasePage(QWidget):
    """提供 ``run_async``、``show_error``、``show_loading`` 的基类。"""

    title: str = ""
    subtitle: str = ""

    def __init__(self) -> None:
        super().__init__()
        # 页面根透明，让全局动态背景（SkinBackdrop）透出来
        self.setObjectName("PageRoot")
        # 唯一的内容容器
        self._content = QWidget(self)
        self._content.setObjectName("PageContent")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._content)

        # 加载态覆盖层
        self._loading_overlay = _Overlay(self)
        v_load = QVBoxLayout(self._loading_overlay)
        v_load.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(Spinner(diameter=42))
        msg = QLabel("正在加载数据……")
        msg.setStyleSheet("color: #B0BEC5; padding-left:12px; font-size:13px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(msg)
        row.addStretch(1)
        v_load.addLayout(row)
        v_load.addStretch(1)

        # 错误态覆盖层
        self._error_overlay = _Overlay(self)
        v_err = QVBoxLayout(self._error_overlay)
        v_err.addStretch(1)
        big = QLabel("⚠️")
        big.setStyleSheet("font-size: 48px;")
        big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_err.addWidget(big)
        self._error_label = QLabel("发生错误")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.setStyleSheet("color: #FF4E5E; font-size: 14px;")
        v_err.addWidget(self._error_label)
        v_err.addStretch(1)

        # 顶部霓虹光带（增量刷新）
        self._loading_bar = _LoadingBar(self)

        # 是否已经至少完成过一次内容渲染
        self._content_ready: bool = False
        # 平滑滚动只安装一次
        self._smooth_installed: bool = False

    # ── 平滑滚动（让操作界面享受高帧率） ──────
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._smooth_installed:
            self._smooth_installed = True
            from app.ui.design.smooth_scroll import enable_smooth_scrolling
            for area in self.findChildren(QAbstractScrollArea):
                enable_smooth_scrolling(area)

    # ── 子类调用 ──────────────────────────────
    def content_widget(self) -> QWidget:
        return self._content

    def show_content(self) -> None:
        self._content_ready = True
        self._loading_overlay.hide()
        self._error_overlay.hide()

    def show_loading(self) -> None:
        self._error_overlay.hide()
        self._loading_overlay.setGeometry(self.rect())
        self._loading_overlay.raise_()
        self._loading_overlay.show()

    def show_error(self, message: str) -> None:
        self._error_label.setText(f"加载失败：{message}")
        # 已有内容时，错误以浮层形式提示一下，不替换页面
        if self._content_ready:
            log.warning("刷新失败：%s", message)
            return
        self._loading_overlay.hide()
        self._error_overlay.setGeometry(self.rect())
        self._error_overlay.raise_()
        self._error_overlay.show()

    def run_async(
        self,
        coro_factory: Callable[[], Awaitable[None]],
        *,
        show_loader: bool | None = None,
    ) -> None:
        """运行异步任务。

        默认行为是 **增量刷新**：
        * 首屏（``self._content_ready == False``）—— 显示加载态遮罩。
        * 已有内容 —— 顶部霓虹光带，原 UI 一直可见。
        显式传 ``show_loader=True/False`` 可强制覆盖。
        """
        if show_loader is None:
            show_loader = not self._content_ready
        if show_loader:
            self.show_loading()
        else:
            self._loading_bar.setGeometry(0, 0, max(1, self.width()), 2)
            self._loading_bar.raise_()
            self._loading_bar.start()

        async def _runner() -> None:
            try:
                await coro_factory()
                self.show_content()
            except Exception as exc:  # pragma: no cover - 网络
                log.exception("页面加载失败")
                self.show_error(str(exc))
            finally:
                self._loading_bar.stop()

        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_runner())
        else:
            QTimer.singleShot(0, lambda: asyncio.ensure_future(_runner()))

    # ── 几何同步 ──────────────────────────────
    def resizeEvent(self, ev) -> None:  # noqa: D401
        super().resizeEvent(ev)
        self._loading_bar.setGeometry(0, 0, self.width(), 2)
        if self._loading_overlay.isVisible():
            self._loading_overlay.setGeometry(self.rect())
        if self._error_overlay.isVisible():
            self._error_overlay.setGeometry(self.rect())
