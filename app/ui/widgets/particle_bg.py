"""粒子 / 流星 / 光斑 沉浸式背景。

为整个应用提供「2026 FIFA WC 红黑霓虹」的电影级氛围层。
设计语言对照「EA FC25 Ultimate Team × Apple Vision Pro」：

* 30~50 颗漂浮粒子（柔和淡入淡出 + 缓慢上浮）。
* 偶发的流星（自右上向左下穿越，留下渐隐拖尾）。
* 视图边缘的径向光晕（红 / 金 / 蓝），制造景深感。
* 使用 `QGraphicsBlurEffect` 不现实（性能差），改为 alpha 渐变 +
  径向渐变模拟「景深模糊」。

控件本身是 **不接收鼠标事件** 的覆盖层（``WA_TransparentForMouseEvents``），
可作为页面 hero 区或整页的最底层装饰。
"""
from __future__ import annotations

import math
import random

from PyQt6.QtCore import (
    QPointF,
    QRectF,
    Qt,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from app.config import BACKDROP_PARTICLE_SCALE, LOW_PERF
from app.ui.design.frame_clock import FrameClock


class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "r", "alpha", "phase", "color")

    def __init__(self, w: float, h: float, palette: list[QColor]) -> None:
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-0.06, 0.06)
        self.vy = random.uniform(-0.25, -0.06)  # 缓慢上浮
        self.r = random.uniform(0.8, 2.6)
        self.alpha = random.uniform(0.12, 0.65)
        self.phase = random.uniform(0, math.tau)
        self.color = random.choice(palette)

    def step(self, w: float, h: float) -> None:
        self.x += self.vx
        self.y += self.vy
        self.phase += 0.013
        if self.y < -10 or self.x < -10 or self.x > w + 10:
            self.x = random.uniform(0, w)
            self.y = h + random.uniform(0, 30)


class _Meteor:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color")

    def __init__(self, w: float, h: float) -> None:
        # 从右上角随机出来，斜向左下
        self.x = random.uniform(w * 0.4, w * 1.05)
        self.y = random.uniform(-30, h * 0.45)
        speed = random.uniform(7.0, 11.0)
        ang = math.radians(random.uniform(190, 220))
        self.vx = math.cos(ang) * speed
        self.vy = -math.sin(ang) * speed  # 左下
        self.life = 0
        self.max_life = random.randint(30, 55)
        c = random.choice([
            QColor(255, 255, 255),
            QColor(255, 200, 90),
            QColor(255, 110, 130),
            QColor(120, 200, 255),
        ])
        self.color = c

    def step(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.life += 1
        return self.life < self.max_life and self.y < 9999 and self.x > -200


class ParticleBackground(QWidget):
    """粒子 / 流星 / 光晕 背景层。

    Parameters
    ----------
    parent : QWidget
        父控件。
    n_particles : int
        粒子数量（默认 42，区间约 30~50）。
    accent : str
        主点缀色，影响光晕与粒子色彩偏向。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        n_particles: int = 110,
        accent: str = "#00BFFF",
        secondary: str = "#FFD700",
        meteor_chance: float = 0.012,
        base_color: str = "#040812",
        beams: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._accent = QColor(accent)
        self._secondary = QColor(secondary)
        self._base_color = QColor(base_color)
        self._beams = beams
        self._meteor_chance = meteor_chance
        # 对角光束周期（用 _tick 驱动），8 秒扫一次
        self._beam_phase = 0.0

        # 颗粒色板（红粉为主 + 少量金 + 少量蓝白点缀）
        ac = self._accent
        sec = self._secondary
        self._palette: list[QColor] = [
            QColor(255, 255, 255),
            QColor(255, 255, 255),
            QColor(ac.red(), ac.green(), ac.blue()),
            QColor(ac.red(), ac.green(), ac.blue()),
            QColor(255, 126, 179),       # 浅粉
            QColor(sec.red(), sec.green(), sec.blue()),
            QColor(120, 200, 255),
        ]
        self._n_particles = max(8, int(n_particles * BACKDROP_PARTICLE_SCALE))
        self._particles: list[_Particle] = []
        self._meteors: list[_Meteor] = []
        self._tick = 0
        # 柔光点精灵缓存（按颜色）：避免每帧每颗粒子新建径向渐变
        self._sprite_cache: dict[int, QPixmap] = {}

        # 动画由全局唯一的 FrameClock 驱动（单一帧调度器）；省电模式下完全静止，
        # 仅画一帧静态光晕。可见时订阅、隐藏时退订 —— 与其它动效共用一个心跳，
        # 不再各自持有 QTimer。
        self._clock = FrameClock.instance()
        self._subscribed = False

    # ─── 生命周期：不可见时退订，零占用 ──────
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not LOW_PERF and not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    # ─── 几何 ────────────────────────────────
    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        if not self._particles:
            self._spawn_particles()

    def _spawn_particles(self) -> None:
        w, h = max(1, self.width()), max(1, self.height())
        self._particles = [_Particle(w, h, self._palette) for _ in range(self._n_particles)]

    def _on_frame(self, _t: float, _dt: float) -> None:
        if self.width() <= 1 or self.height() <= 1:
            return
        if not self._particles:
            self._spawn_particles()
        w, h = self.width(), self.height()
        for p in self._particles:
            p.step(w, h)
        # 流星
        if random.random() < self._meteor_chance:
            self._meteors.append(_Meteor(w, h))
        self._meteors = [m for m in self._meteors if m.step()]
        self._tick += 1
        # 8 秒一次的对角光束扫过：1/(30fps*8) ≈ 0.00417/帧
        self._beam_phase = (self._beam_phase + 0.0042) % 1.0
        self.update()

    # ─── 绘制 ────────────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        ac = self._accent
        sec = self._secondary
        rad = max(rect.width(), rect.height())

        # ① 第一层：深蓝底色（仅当 base_color 非透明时绘制）
        if self._base_color.alpha() > 0:
            p.fillRect(rect, self._base_color)

        # ② 第二层：红紫渐变（rgba(255,0,100,.25)，左下偏强）
        glow1 = QRadialGradient(rect.bottomLeft(), rad * 0.95)
        glow1.setColorAt(0.0, QColor(255, 0, 100, 64))
        glow1.setColorAt(0.55, QColor(ac.red(), ac.green(), ac.blue(), 30))
        glow1.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(rect, glow1)

        # ③ 第三层：对角光束 —— 45° 方向缓慢扫过（8 秒一周期）
        if self._beams:
            self._draw_diagonal_beams(p, rect)

        # 右上角金色辅光（增加冷暖对比）
        glow2 = QRadialGradient(rect.topRight(), rad * 0.7)
        glow2.setColorAt(0.0, QColor(sec.red(), sec.green(), sec.blue(), 60))
        glow2.setColorAt(0.55, QColor(sec.red(), sec.green(), sec.blue(), 0))
        p.fillRect(rect, glow2)

        # 中下偏冷蓝光（增加纵深）
        glow3 = QRadialGradient(QPointF(rect.center().x(), rect.bottom()), rad * 0.55)
        glow3.setColorAt(0.0, QColor(80, 120, 255, 26))
        glow3.setColorAt(1.0, QColor(80, 120, 255, 0))
        p.fillRect(rect, glow3)

        # ④ 第四层：粒子（缓存柔光精灵 → drawPixmap，避免逐帧径向渐变）
        p.setPen(Qt.PenStyle.NoPen)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        for prt in self._particles:
            a = (math.sin(prt.phase) * 0.5 + 0.5) * prt.alpha
            col = QColor(prt.color)
            r = prt.r * 4.0
            sprite = self._glow_sprite(col)
            p.setOpacity(max(0.0, min(1.0, a)))
            p.drawPixmap(
                QRectF(prt.x - r, prt.y - r, r * 2, r * 2),
                sprite,
                QRectF(0, 0, sprite.width(), sprite.height()),
            )
            core = QColor(col); core.setAlpha(255)
            p.setOpacity(min(1.0, a + 0.2))
            p.setBrush(core)
            p.drawEllipse(QPointF(prt.x, prt.y), prt.r, prt.r)
        p.setOpacity(1.0)

        # 流星
        for m in self._meteors:
            t = m.life / max(1, m.max_life)
            length = 110.0 * (1.0 - t)
            tail_x = m.x - m.vx * 4.0
            tail_y = m.y - m.vy * 4.0
            grad = QLinearGradient(QPointF(m.x, m.y), QPointF(tail_x, tail_y))
            head = QColor(m.color); head.setAlpha(int(220 * (1 - t)))
            tail = QColor(m.color); tail.setAlpha(0)
            grad.setColorAt(0.0, head)
            grad.setColorAt(1.0, tail)
            pen = QPen(QBrush(grad), 2.4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(
                QPointF(m.x, m.y),
                QPointF(m.x - m.vx * length / 10.0, m.y - m.vy * length / 10.0),
            )
        p.end()

    # ──────────────────────────────────────────
    # ──────────────────────────────────────────
    def _glow_sprite(self, color: QColor) -> QPixmap:
        """按颜色缓存的「柔光点」精灵（中心实 → 边缘透明）。"""
        key = color.rgb()
        pm = self._sprite_cache.get(key)
        if pm is not None:
            return pm
        size = 64
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        pp = QPainter(pm)
        pp.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QRadialGradient(QPointF(size / 2, size / 2), size / 2)
        c0 = QColor(color); c0.setAlpha(255)
        c1 = QColor(color); c1.setAlpha(0)
        grad.setColorAt(0.0, c0)
        grad.setColorAt(1.0, c1)
        pp.setPen(Qt.PenStyle.NoPen)
        pp.setBrush(QBrush(grad))
        pp.drawEllipse(QRectF(0, 0, size, size))
        pp.end()
        self._sprite_cache[key] = pm
        return pm

    def _draw_diagonal_beams(self, p: QPainter, rect: QRectF) -> None:
        """画 45° 对角光束（半透明红色斜条），按 _beam_phase 缓慢平移。"""
        ac = self._accent
        w = rect.width()
        h = rect.height()
        # 把对角线坐标系（沿 45° 轴的位置 t）映射到屏幕：
        # 任一点 (x, y) 在 45° 轴上的投影 = (x + y) / sqrt(2)
        # 屏幕对角线长度 = (w + h) / sqrt(2)，再加上 padding 让光带能完整扫过
        diag = (w + h)
        # 两道平行光束，相位错开
        for offset, alpha in ((0.0, 22), (0.5, 14)):
            phase = (self._beam_phase + offset) % 1.0
            # 光束中心沿 45° 轴的位置（屏幕坐标的 x+y 投影）
            t = -diag * 0.3 + phase * (diag * 1.6)
            band = max(80.0, min(w, h) * 0.18)
            # 用 QLinearGradient 沿 45°（x+y 方向）画一条带状光
            # 起点在左上角偏向 t-band，终点在 t+band
            # 沿 (1, 1) 单位向量取等距点
            from math import sqrt
            ux, uy = 1 / sqrt(2), 1 / sqrt(2)
            # 把投影点 t 还原到屏幕坐标 (cx, cy)
            cx, cy = ux * t, uy * t
            sx, sy = cx - ux * band, cy - uy * band
            ex, ey = cx + ux * band, cy + uy * band
            grad = QLinearGradient(QPointF(sx, sy), QPointF(ex, ey))
            grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.5, QColor(255, 0, 80, alpha))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(rect, grad)
