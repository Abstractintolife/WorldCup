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

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.ui.design.app_cursor import pointing_hand_cursor


# 窗口控制按钮（最小化 / 最大化 / 关闭）—— 圆形玻璃风，与右上角 HUD 按钮一体化。
# 玻璃底由 QSS 负责（含悬停态），按钮图标改为 QPainter 矢量描线绘制
# （见 _WinCtrlButton），彻底解决「用 Unicode 字形显示不出来 / 看不见」的问题。
_BTN_QSS = (
    "QPushButton{background:rgba(255,255,255,0.06); border:none;"
    " border-radius:14px;}"
    "QPushButton:hover{background:rgba(255,255,255,0.16);}"
)
# 关闭按钮：常态同样的玻璃圆，悬停转品牌红
_CLOSE_QSS = (
    "QPushButton{background:rgba(255,255,255,0.06); border:none;"
    " border-radius:14px;}"
    "QPushButton:hover{background:#E5484D;}"
)


class _WinCtrlButton(QPushButton):
    """窗口控制按钮：玻璃底（QSS）+ QPainter 矢量描线图标。

    ``kind`` ∈ {"min", "max", "restore", "close"}。图标用 1.6px 圆头线条
    绘制，常态浅灰、悬停纯白（关闭键悬停时底色转红、图标转白），保证在
    任意背景 / 缩放下都清晰可见（取代渲染不稳定的 Unicode 字形）。
    """

    def __init__(self, kind: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._kind = kind
        self.setCursor(pointing_hand_cursor())
        self.setFixedSize(28, 28)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(_CLOSE_QSS if kind == "close" else _BTN_QSS)

    def set_kind(self, kind: str) -> None:
        self._kind = kind
        self.update()

    def paintEvent(self, ev) -> None:  # noqa: D401
        # 先让 QPushButton 画出玻璃底 / 悬停态，再在其上描出矢量图标。
        super().paintEvent(ev)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#FFFFFF") if self.underMouse() else QColor("#C8D0E0")
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        # 以按钮中心为基准的 10×10 图标区。
        cx, cy = self.width() / 2.0, self.height() / 2.0
        d = 9.0  # 图标边长
        l, t, r, b = cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2
        k = self._kind
        if k == "min":
            p.drawLine(int(l), int(cy), int(r), int(cy))
        elif k == "max":
            p.drawRect(QRectF(l, t, d, d))
        elif k == "restore":
            # 两个错位方框（还原图标）。
            off = 2.4
            p.drawRect(QRectF(l, t + off, d - off, d - off))
            p.drawLine(int(l + off), int(t + off), int(l + off), int(t))
            p.drawLine(int(l + off), int(t), int(r), int(t))
            p.drawLine(int(r), int(t), int(r), int(b - off))
            p.drawLine(int(r), int(b - off), int(r - off), int(b - off))
        elif k == "close":
            p.drawLine(int(l), int(t), int(r), int(b))
            p.drawLine(int(l), int(b), int(r), int(t))
        p.end()


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

        self._min_btn = _WinCtrlButton("min")
        self._max_btn = _WinCtrlButton("max")
        self._close_btn = _WinCtrlButton("close")
        for b in (self._min_btn, self._max_btn, self._close_btn):
            b.setFixedSize(28, 28)
        self._min_btn.setToolTip("最小化")
        self._max_btn.setToolTip("最大化 / 还原")
        self._close_btn.setToolTip("关闭")
        row.addWidget(self._min_btn)
        row.addWidget(self._max_btn)
        row.addWidget(self._close_btn)

        self._min_btn.clicked.connect(self._on_min)
        self._max_btn.clicked.connect(self._toggle_max)
        self._close_btn.clicked.connect(self._on_close)

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_language(self, lang: str) -> None:
        """切换标题栏语言（应用名 + 窗口控制按钮提示）。"""
        from app.i18n import tr
        from app.config import APP_TITLE_ZH
        self._title.setText(tr(APP_TITLE_ZH))
        self._min_btn.setToolTip(tr("最小化"))
        self._max_btn.setToolTip(tr("最大化 / 还原"))
        self._close_btn.setToolTip(tr("关闭"))

    # ── 窗口控制 ──────────────────────────────
    def _on_min(self) -> None:
        self.window().showMinimized()

    def _on_close(self) -> None:
        self.window().close()

    def _toggle_max(self) -> None:
        win = self.window()
        if win.isMaximized():
            win.showNormal()
            self._max_btn.set_kind("max")
        else:
            win.showMaximized()
            self._max_btn.set_kind("restore")

    def sync_max_glyph(self) -> None:
        self._max_btn.set_kind("restore" if self.window().isMaximized() else "max")

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
