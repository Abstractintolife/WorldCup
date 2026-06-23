"""SkinBackdrop —— 全局动态背景层（皮肤引擎的视觉核心）。

V3.0「六层渲染系统」
=====================
一个铺满整窗的最底层控件，按当前皮肤的 ``scene`` 渲染对应的动态场景。
所有场景遵循设计文档的分层模型逐层叠加：

    Layer 1  背景渐变      —— 深蓝 / 焦黑 / 翠绿 / 梅紫 三段竖向渐变
    Layer 2  光晕层        —— 皇家紫 / 金 / 绿 / 粉 的大面积径向光晕（缓慢漂移）
    Layer 3  球场纹理层    —— 透视中线圈 + 边线（极低透明度，仅蓝/绿场景）
    Layer 4  聚光灯层      —— 顶部左右两束摆动光锥（模拟世界杯开幕式）
    Layer 5  粒子层        —— 漂浮光点 / 星星 / 花瓣（60FPS 上限、离屏低分渲染）
    Layer 6  动态光效层    —— 底部辉光呼吸

==========  =================================================================
scene       视觉
==========  =================================================================
``worldcup`` 深蓝世界杯 · 电光蓝渐变 + 紫色光晕 + 球场纹理 + 聚光灯 + 漂浮粒子
``gold``     黑金冠军   · 焦黑渐变 + 大力神杯金光晕 + 聚光灯 + 金色尘埃粒子
``field``    绿茵赛场   · 翠绿球场 + 滚动草纹 + 体育场灯柱光锥 + 漂浮草屑
``sakura``   樱花限定   · 暮色梅紫 + 柔粉光晕 + 缓缓飘落的樱花花瓣
==========  =================================================================

控件 **不接收鼠标事件**，且不会拦截子控件交互。
"""
from __future__ import annotations

import math
import random

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QRadialGradient,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from app.config import (
    BACKDROP_PARTICLE_SCALE,
    BACKDROP_RENDER_SCALE,
    LOW_PERF,
)
from app.ui.design.frame_clock import REF_FPS, FrameClock
from app.ui.theme import DARK, ThemePalette

TAU = math.tau


def _c(hexstr: str, alpha: int | None = None) -> QColor:
    col = QColor(hexstr)
    if alpha is not None:
        col.setAlpha(alpha)
    return col


# ════════════════════════════════════════════════════════════════════
#  通用浮点粒子：位置 / 速度 / 半径 / 透明度 / 相位 / 颜色 / 类型标记
# ════════════════════════════════════════════════════════════════════
class _Dot:
    __slots__ = ("x", "y", "vx", "vy", "r", "a", "phase", "color", "kind")

    def __init__(self, x, y, vx, vy, r, a, color, phase=0.0, kind=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.a = a
        self.phase = phase
        self.color = color
        self.kind = kind  # 0=光点 1=星星 2=花瓣


# ════════════════════════════════════════════════════════════════════
class SkinBackdrop(QWidget):
    """整窗动态背景。通过 :meth:`set_palette` 切换皮肤场景。"""

    def __init__(self, parent: QWidget | None = None, palette: ThemePalette | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lower()

        self._palette: ThemePalette = palette or DARK
        self._scene: str = self._palette.scene
        self._t: float = 0.0
        self._frame: int = 0
        self._fs: float = 1.0  # 帧缩放系数 = dt * REF_FPS（时间驱动）
        # 全窗背景是 CPU 软件栅格化，没必要跟到 240Hz —— 把它的重绘上限
        # 钳到 ~30fps（缓慢的氛围运动 30fps 足够），把主线程时间让给滚动/
        # 点击等交互（动效观感几乎无损，因为运动是时间驱动的，仍用累计 dt 推进）。
        self._bg_accum: float = 0.0
        self._bg_min_dt: float = 1.0 / 30.0

        self._dots: list[_Dot] = []
        self._spawned_for: tuple[str, int, int] | None = None
        # 预渲染的「柔光点」精灵缓存（按颜色）：避免每颗粒子每帧新建径向渐变，
        # 这是全窗背景最主要的逐帧开销来源。
        self._sprite_cache: dict[int, QPixmap] = {}

        # 离屏低分辨率渲染缓冲（大幅降低全窗背景的栅格化开销）
        self._buf: QPixmap | None = None

        # 全局帧时钟（240FPS 动效内核）—— 不再自持 QTimer
        self._clock = FrameClock.instance()
        self._enabled = True      # 用户设置：是否启用动态背景动画
        self._want_anim = True    # 页面级暂停（如地球仪页持续自绘时）
        self._subscribed = False
        self._sync_subscription()

    # ─── 公共接口 ────────────────────────────────
    def set_palette(self, palette: ThemePalette) -> None:
        self._palette = palette
        self._scene = palette.scene
        self._spawned_for = None  # 触发重新生成
        self.update()

    def set_paused(self, paused: bool) -> None:
        self._want_anim = not paused
        self._sync_subscription()

    def set_enabled(self, on: bool) -> None:
        """用户开关：关闭后背景静止（仅保留静态渐变），CPU 占用归零。"""
        self._enabled = bool(on)
        self._sync_subscription()
        self.update()

    def _sync_subscription(self) -> None:
        run = (
            self._enabled and self._want_anim
            and self.isVisible() and not LOW_PERF
        )
        if run and not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True
        elif not run and self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    # ─── 生命周期 ────────────────────────────────
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        self._sync_subscription()

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._spawned_for = None

    def _ensure_spawn(self) -> None:
        key = (self._scene, self.width(), self.height())
        if self._spawned_for == key:
            return
        self._spawned_for = key
        self._dots = []
        spawn = getattr(self, f"_spawn_{self._scene}", self._spawn_worldcup)
        spawn()
        if BACKDROP_PARTICLE_SCALE < 0.999 and self._dots:
            k = BACKDROP_PARTICLE_SCALE
            self._dots = self._dots[: max(6, int(len(self._dots) * k))]

    def _on_frame(self, t: float, dt: float) -> None:
        if self.width() <= 1 or self.height() <= 1:
            return
        # 背景重绘节流：累计 dt，达到 ~1/60s 才真正步进 + 重绘
        self._bg_accum += dt
        if self._bg_accum < self._bg_min_dt:
            return
        step_dt = self._bg_accum
        self._bg_accum = 0.0
        self._ensure_spawn()
        self._t = t
        # 帧缩放：把以 60fps 为基准写死的每帧增量换算为时间驱动（封顶防跳变）
        self._fs = min(6.0, step_dt * REF_FPS)
        self._frame += 1
        stepper = getattr(self, f"_step_{self._scene}", self._step_float)
        stepper()
        self.update()

    # ─── 绘制分发 ────────────────────────────────
    def paintEvent(self, _ev) -> None:
        w, h = self.width(), self.height()
        if w <= 1 or h <= 1:
            return
        self._ensure_spawn()
        painter_fn = getattr(self, f"_paint_{self._scene}", self._paint_worldcup)

        scale = BACKDROP_RENDER_SCALE
        if scale >= 0.99:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            try:
                painter_fn(p, QRectF(self.rect()))
            finally:
                p.end()
            return

        bw, bh = max(1, int(w * scale)), max(1, int(h * scale))
        if self._buf is None or self._buf.size() != QSize(bw, bh):
            self._buf = QPixmap(bw, bh)
        self._buf.fill(Qt.GlobalColor.transparent)
        bp = QPainter(self._buf)
        bp.setRenderHint(QPainter.RenderHint.Antialiasing)
        bp.scale(scale, scale)
        try:
            painter_fn(bp, QRectF(0, 0, w, h))
        finally:
            bp.end()

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.drawPixmap(self.rect(), self._buf)
        p.end()

    # ════════════════════════════════════════════════════════════════
    #  通用绘制原语（六层渲染共享）
    # ════════════════════════════════════════════════════════════════
    def _fill_base(self, p: QPainter, rect: QRectF, top: str, mid: str, bottom: str) -> None:
        """Layer 1：三段竖向渐变底色。"""
        g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        g.setColorAt(0.0, _c(top))
        g.setColorAt(0.55, _c(mid))
        g.setColorAt(1.0, _c(bottom))
        p.fillRect(rect, g)

    def _glow(self, p: QPainter, rect: QRectF, cx: float, cy: float,
              radius: float, color: QColor, alpha: int) -> None:
        """Layer 2 / 6：大面积径向光晕。"""
        g = QRadialGradient(QPointF(cx, cy), radius)
        g.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), alpha))
        g.setColorAt(0.55, QColor(color.red(), color.green(), color.blue(), alpha // 3))
        g.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        p.fillRect(rect, g)

    def _field_texture(self, p: QPainter, rect: QRectF, color: QColor) -> None:
        """Layer 3：透视球场纹理 —— 底部中线圈 + 边线（极低透明度）。"""
        w, h = rect.width(), rect.height()
        p.save()
        p.setBrush(Qt.BrushStyle.NoBrush)
        line = QColor(color.red(), color.green(), color.blue(), 26)
        p.setPen(QPen(line, 1.4))
        cx = w * 0.5
        base_y = h * 1.02
        # 中圈（被底边裁切的椭圆 → 透视半场）
        p.drawEllipse(QPointF(cx, base_y), w * 0.20, h * 0.13)
        p.drawEllipse(QPointF(cx, base_y), w * 0.07, h * 0.045)
        # 透视边线（自底部中心向上发散的几条线）
        for fx in (-0.42, -0.16, 0.16, 0.42):
            p.drawLine(QPointF(cx + w * fx, h), QPointF(cx + w * fx * 0.32, h * 0.52))
        p.restore()

    def _spotlights(self, p: QPainter, rect: QRectF, color: QColor,
                    *, alpha: int = 40, period: float = 10.0) -> None:
        """Layer 4：顶部左右两束摆动光锥。"""
        w, h = rect.width(), rect.height()
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        for k, base_fx in enumerate((0.26, 0.74)):
            sway = math.sin(self._t * (TAU / period) + k * math.pi) * w * 0.10
            apex = QPointF(w * base_fx, -h * 0.06)
            spread = w * 0.13
            poly = QPolygonF([
                apex,
                QPointF(w * base_fx - spread + sway, h * 1.02),
                QPointF(w * base_fx + spread + sway, h * 1.02),
            ])
            grad = QLinearGradient(apex, QPointF(w * base_fx + sway, h))
            grad.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), alpha))
            grad.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), alpha // 3))
            grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            p.setBrush(QBrush(grad))
            p.drawPolygon(poly)
        p.restore()

    def _glow_sprite(self, color: QColor) -> QPixmap:
        """返回某颜色的「柔光点」精灵（中心实 → 边缘透明），按颜色缓存。

        预渲染一次后用 :meth:`QPainter.drawPixmap` 绘制，避免每颗粒子每帧
        新建 ``QRadialGradient`` + 填充椭圆（软件栅格化下这是主要热点）。
        """
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

    def _draw_particles(self, p: QPainter) -> None:
        """Layer 5：漂浮光点 + 星星闪烁（光点使用缓存精灵，零逐帧渐变）。"""
        p.setPen(Qt.PenStyle.NoPen)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        for d in self._dots:
            tw = (math.sin(d.phase) * 0.5 + 0.5)
            a = max(0.0, min(1.0, tw * d.a))
            col = QColor(d.color)
            if d.kind == 1:
                # 星星：十字星芒
                self._draw_star(p, d, a)
                continue
            # 光点：缓存柔光精灵作为光晕 + 实心亮核
            r = d.r * 4.0
            sprite = self._glow_sprite(col)
            p.setOpacity(a * 0.5)
            p.drawPixmap(
                QRectF(d.x - r, d.y - r, r * 2, r * 2),
                sprite,
                QRectF(0, 0, sprite.width(), sprite.height()),
            )
            core = QColor(col); core.setAlpha(255)
            p.setOpacity(min(1.0, a + 0.18))
            p.setBrush(core)
            p.drawEllipse(QPointF(d.x, d.y), d.r, d.r)
        p.setOpacity(1.0)

    def _draw_star(self, p: QPainter, d: _Dot, a: float) -> None:
        col = QColor(d.color)
        col.setAlphaF(a)
        pen = QPen(col, 1.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        s = d.r * 2.6
        p.drawLine(QPointF(d.x - s, d.y), QPointF(d.x + s, d.y))
        p.drawLine(QPointF(d.x, d.y - s), QPointF(d.x, d.y + s))
        p.setPen(Qt.PenStyle.NoPen)
        core = QColor(d.color)
        core.setAlphaF(a)
        p.setBrush(core)
        p.drawEllipse(QPointF(d.x, d.y), d.r * 0.7, d.r * 0.7)

    # 通用「上浮 + 横向漂移 + 闪烁」步进（worldcup / gold 复用）
    def _step_float(self) -> None:
        w, h = self.width(), self.height()
        fs = self._fs
        for d in self._dots:
            d.phase += 0.012 * fs
            d.x += (d.vx + math.sin(d.phase) * 0.18) * fs
            d.y += d.vy * fs
            if d.y < -12 or d.x < -12 or d.x > w + 12:
                d.x = random.uniform(0, w)
                d.y = h + random.uniform(0, 30)

    def _spawn_floaters(self, palette_hex: list[str], *, star_ratio: float = 0.22) -> None:
        w, h = self.width(), self.height()
        n = max(40, min(150, w * h // 13000))
        for _ in range(n):
            is_star = random.random() < star_ratio
            self._dots.append(_Dot(
                random.uniform(0, w), random.uniform(0, h),
                random.uniform(-0.05, 0.05), random.uniform(-0.30, -0.06),
                random.uniform(0.7, 1.6) if is_star else random.uniform(0.9, 2.6),
                random.uniform(0.30, 0.85),
                _c(random.choice(palette_hex)), random.uniform(0, TAU),
                kind=1 if is_star else 0,
            ))

    # ════════════════════════════════════════════════════════════════
    #  场景 1：WORLDCUP（深蓝世界杯，默认）
    # ════════════════════════════════════════════════════════════════
    def _spawn_worldcup(self) -> None:
        self._spawn_floaters(
            ["#FFFFFF", "#FFFFFF", "#00BFFF", "#46D2FF", "#6A5ACD", "#FFD700"],
            star_ratio=0.26,
        )

    def _paint_worldcup(self, p: QPainter, rect: QRectF) -> None:
        t = self._palette
        w, h = rect.width(), rect.height()
        # L1 渐变（顶 #08111E → 底 #0F2745）
        self._fill_base(p, rect, "#08111E", "#10213C", "#0F2745")
        # L2 光晕：左上皇家紫 + 右下电光蓝（缓慢漂移）
        ox = math.sin(self._t * 0.18) * w * 0.05
        oy = math.cos(self._t * 0.15) * h * 0.05
        self._glow(p, rect, w * 0.24 + ox, h * 0.18 + oy, max(w, h) * 0.6,
                   _c(t.secondary), 70)
        self._glow(p, rect, w * 0.82 - ox, h * 0.30 + oy, max(w, h) * 0.5,
                   _c(t.primary), 52)
        # L3 球场纹理
        self._field_texture(p, rect, _c(t.primary))
        # L4 聚光灯（蓝白）
        self._spotlights(p, rect, _c("#9FE3FF"), alpha=34, period=11.0)
        # L5 粒子
        self._draw_particles(p)
        # L6 底部辉光呼吸
        breathe = 40 + int(22 * (0.5 + 0.5 * math.sin(self._t * 0.9)))
        self._glow(p, rect, w * 0.5, h * 1.06, max(w, h) * 0.55,
                   _c(t.primary), breathe)

    # ════════════════════════════════════════════════════════════════
    #  场景 2：GOLD（黑金冠军）
    # ════════════════════════════════════════════════════════════════
    def _spawn_gold(self) -> None:
        self._spawn_floaters(
            ["#FFD700", "#FFE680", "#FF9D2E", "#FFFFFF", "#FFC04D"],
            star_ratio=0.30,
        )

    _step_gold = _step_float

    def _paint_gold(self, p: QPainter, rect: QRectF) -> None:
        t = self._palette
        w, h = rect.width(), rect.height()
        self._fill_base(p, rect, "#13100A", "#241B0C", "#0C0A06")
        ox = math.sin(self._t * 0.16) * w * 0.05
        self._glow(p, rect, w * 0.5 + ox, h * 0.12, max(w, h) * 0.6,
                   _c("#FFB300"), 64)
        self._glow(p, rect, w * 0.20 - ox, h * 0.40, max(w, h) * 0.42,
                   _c("#FF7A1A"), 38)
        # 聚光灯（暖金）
        self._spotlights(p, rect, _c("#FFE6A0"), alpha=42, period=12.0)
        self._draw_particles(p)
        breathe = 44 + int(26 * (0.5 + 0.5 * math.sin(self._t * 0.8)))
        self._glow(p, rect, w * 0.5, h * 1.06, max(w, h) * 0.55,
                   _c(t.accent), breathe)

    # ════════════════════════════════════════════════════════════════
    #  场景 3：FIELD（绿茵赛场）
    # ════════════════════════════════════════════════════════════════
    def _spawn_field(self) -> None:
        w, h = self.width(), self.height()
        n = max(28, min(80, w * h // 24000))
        for _ in range(n):
            self._dots.append(_Dot(
                random.uniform(0, w), random.uniform(0, h),
                random.uniform(-0.3, 0.3), random.uniform(-0.5, -0.12),
                random.uniform(1.0, 3.0), random.uniform(0.30, 0.85),
                _c(random.choice(["#C8FF8A", "#7DFFB0", "#FFF0A0"])),
                random.uniform(0, TAU), kind=0,
            ))

    def _step_field(self) -> None:
        w, h = self.width(), self.height()
        fs = self._fs
        for d in self._dots:
            d.phase += 0.02 * fs
            d.x += (d.vx + math.sin(d.phase) * 0.25) * fs
            d.y += d.vy * fs
            if d.y < -10:
                d.x, d.y = random.uniform(0, w), h + random.uniform(0, 30)

    def _paint_field(self, p: QPainter, rect: QRectF) -> None:
        t = self._palette
        w, h = rect.width(), rect.height()
        self._fill_base(p, rect, "#04210F", "#0A3A1E", "#04140C")
        # 滚动球场条纹
        stripe_h = max(40.0, h / 9.0)
        scroll = (self._t * 14.0) % (stripe_h * 2)
        y = -stripe_h * 2 + scroll
        i = 0
        while y < h:
            if i % 2 == 0:
                p.fillRect(QRectF(0, y, w, stripe_h), QColor(255, 255, 255, 8))
            y += stripe_h
            i += 1
        # 体育场灯柱光锥（四束）
        p.setPen(Qt.PenStyle.NoPen)
        for k in range(4):
            base_x = w * (0.12 + 0.25 * k)
            sway = math.sin(self._t * 0.6 + k * 1.3) * w * 0.05
            apex = QPointF(base_x + sway, -h * 0.15)
            spread = w * 0.10
            poly = QPolygonF([
                apex,
                QPointF(base_x - spread + sway * 0.4, h),
                QPointF(base_x + spread + sway * 0.4, h),
            ])
            grad = QLinearGradient(apex, QPointF(base_x, h))
            grad.setColorAt(0.0, QColor(255, 247, 200, 46))
            grad.setColorAt(1.0, QColor(255, 247, 200, 0))
            p.setBrush(QBrush(grad))
            p.drawPolygon(poly)
        # 球场纹理 + 顶/底辉光
        self._field_texture(p, rect, _c("#EAFBEF"))
        self._glow(p, rect, w * 0.5, -h * 0.1, max(w, h) * 0.7, _c("#FFE696"), 40)
        self._glow(p, rect, w * 0.5, h * 1.05, max(w, h) * 0.6, _c(t.primary), 56)
        # 草屑
        self._draw_particles(p)

    # ════════════════════════════════════════════════════════════════
    #  场景 4：SAKURA（樱花限定）
    # ════════════════════════════════════════════════════════════════
    def _spawn_sakura(self) -> None:
        w, h = self.width(), self.height()
        # 花瓣
        n = max(30, min(110, w * h // 16000))
        petal_cols = ["#FFC8DE", "#FFB3CD", "#FF8FB1", "#FFE0EC"]
        for _ in range(n):
            self._dots.append(_Dot(
                random.uniform(0, w), random.uniform(-h, h),
                random.uniform(-0.5, 0.5), random.uniform(0.5, 1.6),
                random.uniform(3.0, 6.5), random.uniform(0.5, 0.95),
                _c(random.choice(petal_cols)), random.uniform(0, TAU), kind=2,
            ))
        # 远处柔光星点
        ns = max(16, min(60, w * h // 30000))
        for _ in range(ns):
            self._dots.append(_Dot(
                random.uniform(0, w), random.uniform(0, h * 0.6),
                0.0, 0.0, random.uniform(0.6, 1.4), random.uniform(0.3, 0.8),
                _c("#FFE0EC"), random.uniform(0, TAU), kind=1,
            ))

    def _step_sakura(self) -> None:
        w, h = self.width(), self.height()
        fs = self._fs
        for d in self._dots:
            if d.kind == 1:
                d.phase += 0.04 * fs
                continue
            d.phase += 0.03 * fs
            d.x += (d.vx + math.sin(d.phase) * 0.8) * fs
            d.y += d.vy * fs
            if d.y - d.r > h:
                d.y = -random.uniform(0, h * 0.3)
                d.x = random.uniform(0, w)

    def _paint_sakura(self, p: QPainter, rect: QRectF) -> None:
        t = self._palette
        w, h = rect.width(), rect.height()
        self._fill_base(p, rect, "#2A1020", "#3C1730", "#160A12")
        ox = math.sin(self._t * 0.15) * w * 0.05
        self._glow(p, rect, w * 0.30 + ox, h * 0.22, max(w, h) * 0.55,
                   _c(t.primary), 58)
        self._glow(p, rect, w * 0.78 - ox, h * 0.34, max(w, h) * 0.45,
                   _c(t.secondary), 44)
        # 柔光星点
        p.setPen(Qt.PenStyle.NoPen)
        for d in self._dots:
            if d.kind == 1:
                a = (math.sin(d.phase) * 0.5 + 0.5) * d.a
                col = QColor(d.color)
                col.setAlphaF(max(0.0, a))
                p.setBrush(col)
                p.drawEllipse(QPointF(d.x, d.y), d.r, d.r)
        # 花瓣
        self._draw_petals(p)
        # 底部柔粉辉光
        breathe = 40 + int(20 * (0.5 + 0.5 * math.sin(self._t * 0.7)))
        self._glow(p, rect, w * 0.5, h * 1.06, max(w, h) * 0.55,
                   _c(t.primary), breathe)

    def _draw_petals(self, p: QPainter) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        for d in self._dots:
            if d.kind != 2:
                continue
            col = QColor(d.color)
            col.setAlphaF(max(0.0, min(1.0, d.a)))
            p.save()
            p.translate(d.x, d.y)
            p.rotate(math.degrees(d.phase))
            # 花瓣随旋转「翻面」→ 宽度按 cos 收缩，模拟飘落翻转
            sx = abs(math.cos(d.phase * 0.7)) * 0.6 + 0.4
            p.setBrush(col)
            path = QPainterPath()
            r = d.r
            path.moveTo(0, -r)
            path.cubicTo(r * 0.8 * sx, -r * 0.5, r * 0.7 * sx, r * 0.6, 0, r)
            path.cubicTo(-r * 0.7 * sx, r * 0.6, -r * 0.8 * sx, -r * 0.5, 0, -r)
            p.drawPath(path)
            p.restore()
