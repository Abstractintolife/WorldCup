"""无边框窗口的自绘窗体外壳：标题栏（含最小化 / 最大化 / 关闭）+ 边缘缩放手柄。

为什么需要它
------------
默认 ``QMainWindow`` 会带上操作系统的原生标题栏（那条「黑框框」），与软件
深色玻璃风格割裂。这里把窗口设为无边框（``FramelessWindowHint``），改用与
主体融合的自绘标题栏，并通过 Qt 的 ``QWindow.startSystemMove`` /
``startSystemResize`` 复刻拖动与边缘缩放（原生体验、跨平台）。

组件
----
* :class:`TitleBar` —— 顶部条：应用图标 + 标题 + 窗口控制按钮；可拖动、可双击
  最大化/还原。
* :class:`ResizeGripManager` —— 在窗口四边 / 四角铺 8 个透明手柄，按下时调用
  ``startSystemResize`` 实现缩放（无边框窗口默认丢失原生缩放能力）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


# 窗口控制按钮（最小化 / 最大化）——圆形玻璃风，与右上角 HUD 按钮一体化
_BTN_QSS = (
    "QPushButton{{background:rgba(255,255,255,0.06); color:#C8D0E0; border:none;"
    " border-radius:14px; font-size:{fs}px; font-weight:700;}}"
    "QPushButton:hover{{background:rgba(255,255,255,0.16); color:#FFFFFF;}}"
)
# 关闭按钮：常态同样的玻璃圆，悬停转品牌红
_CLOSE_QSS = (
    "QPushButton{background:rgba(255,255,255,0.06); color:#C8D0E0; border:none;"
    " border-radius:14px; font-size:14px; font-weight:700;}"
    "QPushButton:hover{background:#E5484D; color:#FFFFFF;}"
)


class TitleBar(QFrame):
    """与主体融合的自绘标题栏（无独立底色 / 无分隔线，浑然一体）。"""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(40)
        # 透明底、无边框：标题栏与下方内容、动态背景连成一体（一体化）。
        self.setStyleSheet("QFrame#TitleBar{background: transparent; border: none;}")

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 10, 0)
        row.setSpacing(8)

        # 应用徽标（程序化大力神杯）+ 标题
        try:
            from app.ui.design.app_icon import build_app_icon
            ico = QLabel()
            ico.setPixmap(build_app_icon().pixmap(20, 20))
            row.addWidget(ico)
        except Exception:
            pass
        self._title = QLabel(title)
        self._title.setStyleSheet(
            "color:#E6EAF4; font-size:12.5px; font-weight:800;"
            " letter-spacing:0.5px; background:transparent;")
        row.addWidget(self._title)
        row.addStretch(1)

        self._min_btn = QPushButton("\u2014")        # —
        self._max_btn = QPushButton("\u2610")         # ▢
        self._close_btn = QPushButton("\u2715")       # ✕
        for b in (self._min_btn, self._max_btn, self._close_btn):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedSize(28, 28)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._min_btn.setStyleSheet(_BTN_QSS.format(fs=14))
        self._max_btn.setStyleSheet(_BTN_QSS.format(fs=12))
        self._close_btn.setStyleSheet(_CLOSE_QSS)
        row.addWidget(self._min_btn)
        row.addWidget(self._max_btn)
        row.addWidget(self._close_btn)

        self._min_btn.clicked.connect(self._on_min)
        self._max_btn.clicked.connect(self._toggle_max)
        self._close_btn.clicked.connect(self._on_close)

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    # ── 窗口控制 ──────────────────────────────
    def _on_min(self) -> None:
        self.window().showMinimized()

    def _on_close(self) -> None:
        self.window().close()

    def _toggle_max(self) -> None:
        win = self.window()
        if win.isMaximized():
            win.showNormal()
            self._max_btn.setText("\u2610")        # ▢
        else:
            win.showMaximized()
            self._max_btn.setText("\u2750")        # ❐ 还原符号

    def sync_max_glyph(self) -> None:
        self._max_btn.setText("\u2750" if self.window().isMaximized() else "\u2610")

    # ── 拖动 / 双击最大化 ─────────────────────
    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()
            if handle is not None:
                handle.startSystemMove()
        super().mousePressEvent(ev)

    def mouseDoubleClickEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self._toggle_max()
        super().mouseDoubleClickEvent(ev)


class _Grip(QWidget):
    """单个边缘 / 角落缩放手柄。"""

    def __init__(self, parent: QWidget, edges: Qt.Edge, cursor: Qt.CursorShape) -> None:
        super().__init__(parent)
        self._edges = edges
        self.setCursor(cursor)
        # 透明，但能接收鼠标事件
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()
            if handle is not None and not self.window().isMaximized():
                handle.startSystemResize(self._edges)
        super().mousePressEvent(ev)


class ResizeGripManager:
    """在容器四边 / 四角维护 8 个缩放手柄，随容器尺寸自动重排。"""

    THICK = 6

    def __init__(self, container: QWidget) -> None:
        self._c = container
        E = Qt.Edge
        C = Qt.CursorShape
        self._grips: list[tuple[_Grip, str]] = [
            (_Grip(container, E.LeftEdge, C.SizeHorCursor), "l"),
            (_Grip(container, E.RightEdge, C.SizeHorCursor), "r"),
            (_Grip(container, E.TopEdge, C.SizeVerCursor), "t"),
            (_Grip(container, E.BottomEdge, C.SizeVerCursor), "b"),
            (_Grip(container, E.TopEdge | E.LeftEdge, C.SizeFDiagCursor), "tl"),
            (_Grip(container, E.TopEdge | E.RightEdge, C.SizeBDiagCursor), "tr"),
            (_Grip(container, E.BottomEdge | E.LeftEdge, C.SizeBDiagCursor), "bl"),
            (_Grip(container, E.BottomEdge | E.RightEdge, C.SizeFDiagCursor), "br"),
        ]

    def reposition(self) -> None:
        w = self._c.width()
        h = self._c.height()
        t = self.THICK
        geos = {
            "l": (0, t, t, h - 2 * t),
            "r": (w - t, t, t, h - 2 * t),
            "t": (t, 0, w - 2 * t, t),
            "b": (t, h - t, w - 2 * t, t),
            "tl": (0, 0, t, t),
            "tr": (w - t, 0, t, t),
            "bl": (0, h - t, t, t),
            "br": (w - t, h - t, t, t),
        }
        for grip, key in self._grips:
            x, y, gw, gh = geos[key]
            grip.setGeometry(x, y, max(0, gw), max(0, gh))
            grip.raise_()

    def set_visible(self, visible: bool) -> None:
        for grip, _ in self._grips:
            grip.setVisible(visible)

    def raise_all(self) -> None:
        for grip, _ in self._grips:
            grip.raise_()
