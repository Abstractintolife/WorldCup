"""mouse_trail —— 透明的鼠标拖尾叠层（WorldCup 3.0）。

跟随光标的极简拖尾点（z3 顶层、对鼠标事件透明），刻意「克制」—— 不是网页
小游戏那种夸张拖尾。由**单一** ``FrameClock`` 心跳驱动（**不**新增定时器）；
位置为最近若干个光标采样的环形缓冲（``<= MAX_DOTS``），透明度从头到尾
**严格递减**。光标静止且拖尾耗尽后，重置已存透明度。

对应需求 23.1 / 23.2 / 23.3 / 23.4（设计 Property 17）：

* 23.1 —— 任意时刻渲染 ``<= 5`` 个点。
* 23.2 —— 点透明度从头（最新）到尾（最旧）严格递减。
* 23.3 —— 叠层对鼠标输入透明（``WA_TransparentForMouseEvents``）。
* 23.4 —— 光标静止且无点可见时，重置已存透明度。

环形缓冲更新与透明度斜坡抽成纯函数（:func:`push_sample` /
:func:`trail_opacities`），可无头属性测试。
"""
from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QCursor, QPainter
from PyQt6.QtWidgets import QWidget

from app.ui.design.frame_clock import FrameClock
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette

#: 拖尾点数上限。
MAX_DOTS = 5
#: 头部（最新）点的基准透明度（克制、低调）。
HEAD_OPACITY = 0.45
#: 点半径（像素）。
DOT_RADIUS = 3
#: 光标静止多少帧后开始「消尾」。
_IDLE_FRAMES = 2


def push_sample(samples: list, pos, max_dots: int = MAX_DOTS) -> list:
    """纯函数：把最新光标位置压入环形缓冲，保留最近 ``max_dots`` 个（最新在头）。

    返回**新列表**（不就地修改入参），长度恒 ``<= max_dots``。
    """
    if max_dots <= 0:
        return []
    return [pos] + list(samples)[: max_dots - 1]


def trail_opacities(count: int, head: float = HEAD_OPACITY,
                    max_dots: int = MAX_DOTS) -> list[float]:
    """纯函数：``count`` 个点的透明度斜坡，从头到尾**严格递减**且全部为正。

    第 ``i`` 个点（``i=0`` 为头/最新）透明度为 ``head * (count - i) / count``：
    例如 ``count=5`` → ``head * [1.0, 0.8, 0.6, 0.4, 0.2]``。``count`` 会被夹紧
    到 ``[0, max_dots]``。
    """
    n = max(0, min(int(count), max_dots))
    if n == 0:
        return []
    return [head * (n - i) / n for i in range(n)]


class MouseTrailOverlay(QWidget):
    """光标拖尾叠层（z3，透明、FrameClock 驱动）。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._samples: list[QPoint] = []
        self._opacities: list[float] = []
        self._last_pos: QPoint | None = None
        self._idle: int = 0
        self._clock = FrameClock.instance()

    # ── FrameClock 订阅（显示订阅 / 隐藏退订） ──
    def showEvent(self, ev) -> None:
        self._clock.subscribe(self._on_frame)
        super().showEvent(ev)

    def hideEvent(self, ev) -> None:
        self._clock.unsubscribe(self._on_frame)
        self._reset()
        super().hideEvent(ev)

    # ── 每帧推进 ─────────────────────────────
    def _on_frame(self, _t: float, _dt: float) -> None:
        cur = self.mapFromGlobal(QCursor.pos())
        moved = self._last_pos is None or cur != self._last_pos
        if moved:
            self._samples = push_sample(self._samples, QPoint(cur), MAX_DOTS)
            self._idle = 0
        else:
            self._idle += 1
            if self._idle > _IDLE_FRAMES and self._samples:
                # 静止：从尾部逐帧「消尾」。
                self._samples = self._samples[:-1]
        self._last_pos = QPoint(cur)

        if self._samples:
            self._opacities = trail_opacities(len(self._samples))
        elif self._opacities:
            # 拖尾耗尽且光标静止：重置已存透明度（需求 23.4）。
            self._reset_opacities()

        self.update()

    def _reset_opacities(self) -> None:
        self._opacities = []

    def _reset(self) -> None:
        self._samples = []
        self._opacities = []
        self._last_pos = None
        self._idle = 0

    # ── 绘制 ─────────────────────────────────
    def paintEvent(self, _ev) -> None:
        if not self._samples:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        base = QColor(self._palette.primary_hi)
        ops = self._opacities or trail_opacities(len(self._samples))
        for pt, op in zip(self._samples, ops):
            c = QColor(base)
            c.setAlphaF(max(0.0, min(1.0, op)))
            p.setBrush(c)
            p.drawEllipse(pt, DOT_RADIUS, DOT_RADIUS)
