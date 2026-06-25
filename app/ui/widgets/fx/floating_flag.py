"""floating_flag —— 随风飘扬的旗帜控件（WorldCup 3.0）。

旧版只是让旗面整体 **上下平移**（±3px / 4s 正弦），观感僵硬、不真实。本版改成
像真实旗帜一样 **迎风飘动**：把旗面沿水平方向切成许多细竖条，每一条按一条
**行进波**（traveling wave）做垂直位移，并叠加 **明暗褶皱**（朝向观众的折面更亮、
背离的更暗），从而呈现布料在风中起伏的立体感。

实现要点
--------
* 旗面位图加载方式与 :class:`~app.ui.widgets.flag_icon.FlagIcon` 一致
  （本地打包优先，``ImageService`` 异步回填），保证清晰、零延迟、可离线。
* 动画由 **唯一** 的全局 :class:`~app.ui.design.frame_clock.FrameClock` 心跳驱动
  （不新增 ``QTimer``），并节流到 ~60fps；旗帜显示时订阅、隐藏时退订。
* 飘动靠近 **旗杆一侧（左）几乎不动**，越靠 **自由端（右）摆幅越大**——符合真实
  旗帜的物理直觉。两条不同频率/相位的正弦叠加，使飘动不机械、更自然。
* ``LOW_PERF`` 省电模式下保持静止（不订阅心跳），:pyattr:`float_y` 恒为 ``0.0``。

为兼容历史调用，仍保留纯函数 :func:`floating_offset` 与
``FLOAT_AMPLITUDE_PX`` / ``FLOAT_PERIOD_S`` 等常量。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QPixmapCache,
    QTransform,
)
from PyQt6.QtWidgets import QWidget

from app.config import LOW_PERF
from app.services.image_service import ImageService
from app.services.player_profiles import flag_image_url
from app.ui.design.frame_clock import FrameClock

#: 历史兼容：旧「上下浮动」幅度（像素）与周期（秒）。
FLOAT_AMPLITUDE_PX = 3.0
FLOAT_PERIOD_S = 4.0
FLOAT_PERIOD_MS = int(FLOAT_PERIOD_S * 1000)

#: 旗帜飘动参数。
_WAVE_PERIOD_S = 2.0          # 一个主波周期（秒）—— 风的节律（略快、更有动感）
_WAVE_COUNT = 2.0             # 旗面上同时可见的波数（沿宽度方向，褶皱更丰富）
_WAVE_AMPLITUDE_RATIO = 0.17  # 自由端最大垂直摆幅 ≈ 旗高 * 该比值（加大、更震撼）
_WAVE_SWAY_RATIO = 0.08       # 自由端最大水平摆幅 ≈ 旗高 * 该比值
_STRIP_PX = 3                 # 竖条宽度（像素）—— 错切保证无缝，故可略宽以省开销
# 重绘节流：跟随全局帧时钟（最高 144FPS）—— 不再压到 120，飘动更顺滑、更高帧率。
_BG_MIN_DT = 1.0 / 144.0
# 动态高光「扫光」周期（秒）：一道亮带周期性掠过旗面，模拟布料反光，更炫酷。
_SHEEN_PERIOD_S = 3.4
_SHEEN_ALPHA = 46             # 高光峰值不透明度（0–255），克制以免发白


def floating_offset(t: float, amplitude: float = FLOAT_AMPLITUDE_PX,
                    period: float = FLOAT_PERIOD_S) -> float:
    """纯函数（历史兼容）：``A·sin(2π·t/period)``，恒在 ``[-amplitude, +amplitude]``。"""
    return amplitude * math.sin(2.0 * math.pi * (t / period))


def wave_offset(u: float, t: float, *, amplitude: float,
                period: float = _WAVE_PERIOD_S, waves: float = _WAVE_COUNT) -> float:
    """纯函数：旗面归一化横向位置 ``u`` ∈ [0,1]（0=旗杆，1=自由端）在时间 ``t``
    处的垂直位移。

    位移幅度随 ``u`` 增大（旗杆端固定、自由端摆幅最大），并由两条不同频率的
    正弦叠加，避免机械感。返回值绝对值 ≤ ``amplitude``（在叠加权重 0.7+0.3=1.0 下）。
    """
    env = u * u                      # 旗杆端≈0、自由端≈1 的摆幅包络（二次更柔和）
    w = 2.0 * math.pi / max(0.05, period)
    k = 2.0 * math.pi * waves
    primary = math.sin(k * u - w * t)
    secondary = math.sin(0.6 * k * u - 1.7 * w * t + 1.3)
    return amplitude * env * (0.7 * primary + 0.3 * secondary)


class FloatingFlag(QWidget):
    """随风飘扬的旗帜（取代旧的「上下平移」实现，保持同名 API）。"""

    def __init__(
        self,
        nationality: str | None = None,
        parent: QWidget | None = None,
        *,
        height: int = 26,
        radius: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._h = int(height)
        self._w = max(1, round(self._h * 3 / 2))      # 统一 3:2 旗面比例
        self._radius = radius
        # 飘动留白：自由端的垂直/水平摆幅都需要余量，避免被裁切。
        self._amp = max(2.0, self._h * _WAVE_AMPLITUDE_RATIO)
        self._sway = max(1.0, self._h * _WAVE_SWAY_RATIO)
        self._mx = int(math.ceil(self._sway)) + 2
        self._my = int(math.ceil(self._amp)) + 2
        self.setFixedSize(self._w + 2 * self._mx, self._h + 2 * self._my)

        self._pixmap: QPixmap | None = None
        self._scaled: QPixmap | None = None
        self._url: str | None = None
        self._service = ImageService.instance()
        self._listening = False

        self._clock = FrameClock.instance()
        self._subscribed = False
        self._accum = 0.0
        self._t = 0.0
        self._float_y = 0.0            # 历史兼容字段（恒 0.0；飘动为逐条位移）

        # 历史兼容：保留一个（停止状态的）属性动画对象。新版飘动由 FrameClock
        # 驱动逐竖条位移，本动画对象不参与渲染，仅供旧测试/调用读取 ``_anim.state()``。
        self._anim = QPropertyAnimation(self, b"floatY", self)
        self._anim.setDuration(FLOAT_PERIOD_MS)

        self.set_nationality(nationality)

    # ── 旗面位图加载（与 FlagIcon 一致：本地优先 + 异步回填）──
    def set_nationality(self, nationality: str | None) -> None:
        self._url = flag_image_url(nationality, height=max(120, self._h * 4))
        self._scaled = None
        if not self._url:
            self._pixmap = None
            self._stop_listening()
            self.update()
            return
        pm = self._service.request(self._url)
        if pm is not None and not pm.isNull():
            self._pixmap = pm
            self._stop_listening()
        else:
            self._pixmap = None
            self._start_listening()
        self.update()

    def _start_listening(self) -> None:
        if not self._listening:
            self._service.image_ready.connect(self._on_ready)
            self._listening = True

    def _stop_listening(self) -> None:
        if self._listening:
            try:
                self._service.image_ready.disconnect(self._on_ready)
            except (TypeError, RuntimeError):
                pass
            self._listening = False

    def _on_ready(self, url: str, pm: QPixmap) -> None:
        if url == self._url:
            self._pixmap = pm
            self._scaled = None
            self._stop_listening()
            self.update()

    def _build_scaled(self) -> None:
        if not (self._pixmap and not self._pixmap.isNull()):
            self._scaled = None
            return
        key = f"wcwaveflag:{self._url}:{self._w}x{self._h}"
        cached = QPixmapCache.find(key)
        if cached is not None and not cached.isNull():
            self._scaled = cached
            return
        scaled = self._pixmap.scaled(
            self._w, self._h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        # 居中裁剪到精确 w×h，保证所有旗面尺寸完全一致。
        if scaled.width() != self._w or scaled.height() != self._h:
            x = max(0, (scaled.width() - self._w) // 2)
            y = max(0, (scaled.height() - self._h) // 2)
            scaled = scaled.copy(x, y, self._w, self._h)
        self._scaled = scaled
        if self._url:
            QPixmapCache.insert(key, scaled)

    # ── 公共 API（保持与旧实现一致）──
    def start_float(self) -> None:
        """开始迎风飘动。``LOW_PERF`` 省电模式下保持静止（不订阅心跳）。"""
        if LOW_PERF:
            self._float_y = 0.0
            return
        if not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def stop_float(self) -> None:
        self._unsubscribe()
        self._t = 0.0
        self.update()

    def _unsubscribe(self) -> None:
        if self._subscribed:
            try:
                self._clock.unsubscribe(self._on_frame)
            except RuntimeError:  # pragma: no cover - 进程退出竞态
                pass
            self._subscribed = False

    # ── 帧时钟回调（节流到 ~60fps）──
    def _on_frame(self, t: float, dt: float) -> None:
        self._accum += dt
        if self._accum < _BG_MIN_DT:
            return
        self._accum = 0.0
        self._t = t
        self.update()

    # ── 生命周期：显示订阅 / 隐藏退订 ──
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not LOW_PERF and not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        self._unsubscribe()
        super().hideEvent(ev)

    # ── 绘制：逐竖条「错切」行进波 + 褶皱明暗（无缝、不割裂）──
    def paintEvent(self, _ev) -> None:
        if self._scaled is None:
            self._build_scaled()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        base_x = self._mx
        base_y = self._my

        if self._scaled is None or self._scaled.isNull():
            # 位图未就绪：画一个淡占位框（与 FlagIcon 一致的观感）。
            p.fillRect(QRectF(base_x, base_y, self._w, self._h),
                       QColor(255, 255, 255, 18))
            return

        fw, fh = self._w, self._h
        t = self._t
        amp = self._amp
        step = max(2, _STRIP_PX)

        # 竖条边界（含末端），在「边界」处取位移，使相邻竖条共享同一条边
        # —— 关键：每条竖条用 **垂直错切**（shear）让左缘对齐 dy(x0)、右缘对齐
        #    dy(x1)，相邻竖条因共享边界位移而严丝合缝，彻底消除「阶梯/割裂」。
        bounds = list(range(0, fw, step))
        if bounds[-1] != fw:
            bounds.append(fw)

        def off(x: float) -> float:
            return wave_offset(x / fw, t, amplitude=amp)

        for i in range(len(bounds) - 1):
            x0 = bounds[i]
            x1 = bounds[i + 1]
            sw = x1 - x0
            if sw <= 0:
                continue
            dy0 = off(x0)
            dy1 = off(x1)
            slope = (dy1 - dy0) / sw          # 该竖条内的垂直错切斜率

            # 源像素 (sx,sy) → 设备: x'=base_x+sx, y'=base_y+dy0+slope*(sx-x0)+sy
            tr = QTransform(1.0, slope, 0.0, 1.0,
                            float(base_x), float(base_y + dy0 - slope * x0))
            p.setTransform(tr)
            # 只绘制该竖条对应的源子区（比「画整图再裁剪」更省），错切后与相邻
            # 竖条共享边界、严丝合缝。
            p.drawPixmap(QPointF(float(x0), 0.0), self._scaled,
                         QRectF(x0, 0, sw, fh))

            # 褶皱明暗：用局部斜率近似折面朝向，连续变化（不产生硬边带）。
            u = (x0 + sw * 0.5) / fw
            env = u * u                         # 旗杆端≈0、自由端≈1
            shade = max(-1.0, min(1.0, slope * 3.5))
            if shade < 0:                       # 背光折面 → 压暗
                a = int(min(70, -shade * env * 70))
                if a > 0:
                    p.fillRect(QRectF(x0, 0, sw, fh), QColor(0, 0, 0, a))
            elif shade > 0:                     # 迎光折面 → 提亮
                a = int(min(42, shade * env * 42))
                if a > 0:
                    p.fillRect(QRectF(x0, 0, sw, fh), QColor(255, 255, 255, a))
        p.resetTransform()

        # ── 动态高光「扫光」：一道斜向亮带周期性掠过旗面（更炫酷的反光质感）──
        # 叠加在飘动旗面之上，裁剪到旗面圆角矩形内；用三段式线性渐变形成一道
        # 柔和的窄高光，中心随时间从左外侧扫到右外侧后循环。
        phase = (t % _SHEEN_PERIOD_S) / _SHEEN_PERIOD_S      # 0→1 循环
        sweep = -0.35 + phase * 1.70                          # 高光中心（归一化 x，含越界余量）
        cx = base_x + sweep * fw
        band = max(8.0, fw * 0.28)                            # 高光带宽度
        # 斜向：顶部略偏右、底部略偏左，呈自然的对角反光。
        grad = QLinearGradient(cx - band, base_y, cx + band, base_y + fh)
        grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        grad.setColorAt(0.5, QColor(255, 255, 255, _SHEEN_ALPHA))
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        clip = QPainterPath()
        flag_rect = QRectF(base_x + 0.5, base_y + 0.5, fw - 1, fh - 1)
        if self._radius > 0:
            clip.addRoundedRect(flag_rect, float(self._radius), float(self._radius))
        else:
            clip.addRect(flag_rect)
        p.setClipPath(clip)
        p.fillRect(QRectF(base_x, base_y, fw, fh), grad)
        p.setClipping(False)

    # ── 历史兼容属性 ──
    def _get_float_y(self) -> float:
        return self._float_y

    def _set_float_y(self, value: float) -> None:
        self._float_y = float(value)

    #: 历史兼容的 Qt 属性（供旧 QPropertyAnimation 绑定；新版飘动不使用）。
    floatY = pyqtProperty(float, fget=_get_float_y, fset=_set_float_y)

    @property
    def float_y(self) -> float:
        """历史兼容：整体垂直偏移恒为 0.0（飘动改由逐竖条位移实现）。"""
        return self._float_y
