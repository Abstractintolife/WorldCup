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

import math

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QColor, QCursor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget

from app.ui.design.frame_clock import FrameClock
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette

#: 拖尾点数上限（更长 → 更连续顺滑的彗尾）。适当减少以降低每帧绘制开销。
MAX_DOTS = 16
#: 头部（最新）点的基准透明度。整体调暗，避免过亮刺眼。
HEAD_OPACITY = 0.32
#: 头部光点核半径（像素）；越靠尾部越小。
DOT_RADIUS = 4
#: 光标静止多少帧后开始「消尾」。
_IDLE_FRAMES = 2
#: 插值采样的目标间距（像素）—— 快速移动时按此密度补点，得到连续顺滑的彗尾。
_STEP_PX = 3.5
#: 拖尾自身的目标刷新率（FPS）。即便全局 FrameClock 跑在 120/144Hz，拖尾也只
#: 按此频率推进与重绘 —— 显著降低 CPU/GPU 开销，肉眼仍然顺滑。
_TRAIL_FPS = 60
#: 紧贴光标的「留空」半径（像素）：此范围内的拖尾点不绘制，使彗尾跟在鼠标
#: 「身后」而非压在指针正下方（解决拖尾与鼠标重叠）。
_CURSOR_GAP_PX = 16.0

# ── 配色：与仓库上传的「光标.png」（青色发光球）一致 ──────────────
#: 彗尾辉光主色（青/teal，取自光标中心 ~#36CCD6，略提亮以增强发光感）。
_TRAIL_GLOW = "#39D7E6"
#: 光点核高光色（近白青，叠加后形成炽白核心）。
_TRAIL_CORE = "#E6FEFF"


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
        # 拖尾自身限频：累积 dt，达到目标间隔才推进一帧（见 _TRAIL_FPS）。
        self._accum: float = 0.0
        self._min_interval: float = 1.0 / float(_TRAIL_FPS)

    # ── FrameClock 订阅（显示订阅 / 隐藏退订） ──
    def showEvent(self, ev) -> None:
        self._clock.subscribe(self._on_frame)
        super().showEvent(ev)

    def hideEvent(self, ev) -> None:
        try:
            self._clock.unsubscribe(self._on_frame)
        except RuntimeError:  # pragma: no cover - 进程退出竞态（FrameClock 已析构）
            pass
        self._reset()
        super().hideEvent(ev)

    # ── 每帧推进 ─────────────────────────────
    def _on_frame(self, _t: float, _dt: float) -> None:
        # 限频：全局 FrameClock 可能以 120/144Hz 触发，但拖尾只需 ~60FPS。
        # 累积 dt，未达目标间隔则直接跳过本帧（不推进、不重绘），省开销。
        self._accum += float(_dt)
        if self._accum + 1e-9 < self._min_interval:
            return
        self._accum = 0.0

        cur = QPoint(self.mapFromGlobal(QCursor.pos()))
        if self._last_pos is None:
            self._samples = push_sample(self._samples, cur, MAX_DOTS)
            self._last_pos = cur
            self._idle = 0
        else:
            dx = cur.x() - self._last_pos.x()
            dy = cur.y() - self._last_pos.y()
            dist = math.hypot(dx, dy)
            if dist >= 1.0:
                # 在上一帧位置与当前位置之间插值补点：快速移动时也能形成
                # 连续、均匀的彗尾，而非相距很远的几个点（消除「卡顿感」）。
                steps = min(MAX_DOTS, max(1, int(dist / _STEP_PX)))
                for i in range(1, steps + 1):
                    f = i / steps
                    px = round(self._last_pos.x() + dx * f)
                    py = round(self._last_pos.y() + dy * f)
                    self._samples = push_sample(self._samples, QPoint(px, py), MAX_DOTS)
                self._idle = 0
            else:
                self._idle += 1
                if self._idle > _IDLE_FRAMES and self._samples:
                    # 静止：从尾部逐帧「消尾」。
                    self._samples = self._samples[:-1]
            self._last_pos = cur

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
        # 叠加（additive）合成：重叠的辉光相互增亮，形成发光彗尾，与「光标.png」
        # 那颗青色发光球的质感一致。透明度已整体调低，避免过亮刺眼。
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        p.setPen(Qt.PenStyle.NoPen)

        ops = self._opacities or trail_opacities(len(self._samples))
        n = len(self._samples)
        if n == 0:
            return

        glow = QColor(_TRAIL_GLOW)
        core = QColor(_TRAIL_CORE)
        cursor = self._last_pos
        gap2 = _CURSOR_GAP_PX * _CURSOR_GAP_PX

        def _too_close(pt: QPoint) -> bool:
            # 紧贴光标的点不绘制：让彗尾跟在鼠标身后，不压在指针正下方。
            if cursor is None:
                return False
            dx = pt.x() - cursor.x()
            dy = pt.y() - cursor.y()
            return (dx * dx + dy * dy) < gap2

        # 第一遍：柔和的青色辉光（径向渐变，半径与亮度向尾部递减）。
        for i, (pt, op) in enumerate(zip(self._samples, ops)):
            if _too_close(pt):
                continue
            f = (n - i) / n                       # 头部=1 → 尾部→0
            radius = DOT_RADIUS * 2.4 * f + 2.5
            grad = QRadialGradient(QPointF(pt), radius)
            inner = QColor(glow)
            inner.setAlphaF(max(0.0, min(1.0, op * 0.40)))
            mid = QColor(glow)
            mid.setAlphaF(max(0.0, min(1.0, op * 0.13)))
            edge = QColor(glow)
            edge.setAlphaF(0.0)
            grad.setColorAt(0.0, inner)
            grad.setColorAt(0.5, mid)
            grad.setColorAt(1.0, edge)
            p.setBrush(grad)
            p.drawEllipse(QPointF(pt), radius, radius)

        # 第二遍：高光核（更小、更亮），让头部像那颗发光球的核心。亮度已调低。
        for i, (pt, op) in enumerate(zip(self._samples, ops)):
            if _too_close(pt):
                continue
            f = (n - i) / n
            cr = max(0.8, DOT_RADIUS * f) * 1.5
            grad = QRadialGradient(QPointF(pt), cr)
            c0 = QColor(core)
            c0.setAlphaF(max(0.0, min(1.0, op * 0.55)))
            c1 = QColor(core)
            c1.setAlphaF(0.0)
            grad.setColorAt(0.0, c0)
            grad.setColorAt(1.0, c1)
            p.setBrush(grad)
            p.drawEllipse(QPointF(pt), cr, cr)
