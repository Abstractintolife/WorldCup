"""全局极致动效 / 材质工具集。

提供：
* ``stagger_fade``     —— 一组控件依次淡入（异步延迟层次感 Stagger）。
* ``fade_slide_in``    —— 单个控件淡入 + 轻微位移。
* ``BreathingGlow``    —— 给控件套上「呼吸灯」霓虹光晕（鼠标悬停环境光）。
* ``ShimmerSkeleton``  —— 骨架屏：自左向右循环划过的微光扫掠。

说明：一个 QWidget 同时只能挂一个 QGraphicsEffect，
因此「淡入(opacity)」与「发光(shadow)」不要作用在同一控件上。
"""
from __future__ import annotations

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPauseAnimation,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QWidget

from app.ui.design.animation_manager import anim as _anim
from app.ui.design.frame_clock import FrameClock

try:
    # 用 sip 判断底层 C++ 对象是否已被销毁（比 try/except 更可靠）
    from PyQt6 import sip  # type: ignore
except ImportError:  # pragma: no cover
    sip = None  # type: ignore


def _is_alive(obj) -> bool:
    """判断 QObject 的底层 C++ 对象是否仍然存活。"""
    if obj is None:
        return False
    if sip is not None:
        try:
            return not sip.isdeleted(obj)
        except (TypeError, RuntimeError):
            return False
    # 兜底：直接尝试访问一个属性，捕获 RuntimeError
    try:
        obj.objectName()
        return True
    except RuntimeError:
        return False

_CUBIC = QEasingCurve.Type.OutCubic
# 平滑减速曲线（贴近设计稿的 cubic-bezier(0.25,1,0.5,1)）
_EXPO = QEasingCurve.Type.OutQuint


def fade_slide_in(
    widget: QWidget,
    *,
    delay: int = 0,
    duration: int = 460,
    dx: int = 26,
    dy: int = 0,
) -> None:
    """让控件淡入并从 (dx, dy) 偏移滑入到原位。

    用 ``QSequentialAnimationGroup`` 内嵌 ``QPauseAnimation`` 实现延迟，
    全部动画都作为 ``widget`` 的子对象 —— 控件销毁时整棵动画树一并安全释放，
    不会留下悬空的定时器回调。
    """
    # widget 已被销毁则直接返回，避免后续访问抛 RuntimeError。
    if not _is_alive(widget):
        return

    # 停掉该控件上一轮淡入（避免「animation without target」告警）
    prev = getattr(widget, "_fade_anim_ref", None)
    if prev is not None:
        try:
            prev.stop()
        except RuntimeError:
            pass

    # 复用已有的不透明度 effect（否则替换会让旧动画失去目标）
    eff = widget.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
    eff.setOpacity(0.0)

    fade = QPropertyAnimation(eff, b"opacity", widget)
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(_CUBIC)

    parallel = QParallelAnimationGroup()
    parallel.addAnimation(fade)

    seq = QSequentialAnimationGroup(widget)
    if delay > 0:
        seq.addPause(delay)
    seq.addAnimation(parallel)
    setattr(widget, "_fade_anim_ref", seq)
    _anim().track(seq)

    # 动画结束后移除不透明度 effect：避免它常驻在「持续重绘」的页面上
    # （如地球仪）每帧都把整页重渲染到离屏 pixmap，既费性能又会与子控件绘制打架。
    def _cleanup() -> None:
        if not _is_alive(widget):
            return
        try:
            cur = widget.graphicsEffect()
            if isinstance(cur, QGraphicsOpacityEffect):
                widget.setGraphicsEffect(None)
        except RuntimeError:
            # widget 在动画结束的同一拍被销毁 —— 静默忽略
            pass

    seq.finished.connect(_cleanup)

    # ★ 关键修复：不要在「widget 还没拿到正确 geometry」时就用 setGeometry
    # 强行做位移 —— 否则父 layout 在下一轮活动时可能被锁住，所有兄弟节点
    # 都停留在 (0,0,sizeHint())，表现为「列表行全部堆叠」+「文字贴底」
    # （用户痛点：射手 / 助攻榜的 bug）。
    # 把位移动画推迟到事件循环下一轮：此时父 layout 已激活，再移动安全。
    if (dx or dy):
        def _slide_after_layout() -> None:
            # 延迟回调触发时，控件可能已经因为页面切换被销毁。
            if not _is_alive(widget):
                return
            try:
                geo = widget.geometry()
            except RuntimeError:
                return
            if geo.width() <= 0 or geo.height() <= 0:
                return  # geometry 还没下来 —— 跳过位移，仅淡入
            moved = QRect(geo)
            moved.translate(dx, dy)
            try:
                slide = QPropertyAnimation(widget, b"geometry", widget)
            except RuntimeError:
                return
            slide.setDuration(duration)
            slide.setStartValue(moved)
            slide.setEndValue(geo)
            slide.setEasingCurve(_EXPO)
            slide.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        QTimer.singleShot(max(1, delay), _slide_after_layout)

    seq.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)


def stagger_fade(
    widgets: list[QWidget],
    *,
    step: int = 70,
    duration: int = 440,
    start: int = 40,
    dx: int = 20,
    dy: int = 0,
) -> None:
    """一组控件按 step 毫秒的时间差依次淡入（Stagger Effect）。"""
    for i, w in enumerate(widgets):
        if not _is_alive(w):
            continue
        fade_slide_in(w, delay=start + i * step, duration=duration, dx=dx, dy=dy)


def pulse_pop(widget: QWidget, *, grow: int = 6, duration: int = 260) -> None:
    """一次性「弹动」反馈：控件几何短暂放大再回弹（点击/激活时调用）。

    用于按钮、徽章等小控件的点击微反馈。通过 geometry 动画在原位
    略微膨胀再恢复 —— 全程作为 widget 子动画，控件销毁时安全释放。
    动画结束自动还原，避免与父布局长期冲突。
    """
    if not _is_alive(widget):
        return
    try:
        geo = widget.geometry()
    except RuntimeError:
        return
    if geo.width() <= 0 or geo.height() <= 0:
        return
    grown = QRect(geo).adjusted(-grow, -grow, grow, grow)

    anim = QPropertyAnimation(widget, b"geometry", widget)
    anim.setDuration(duration)
    anim.setKeyValueAt(0.0, geo)
    anim.setKeyValueAt(0.45, grown)
    anim.setKeyValueAt(1.0, geo)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    _anim().track(anim)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


class BreathingGlow(QGraphicsDropShadowEffect):
    """呼吸灯式霓虹光晕（用于卡片悬停 / 主按钮）。

    性能说明
    --------
    早期实现循环动画 ``blurRadius``，每帧都触发 Qt 对整块光晕重新高斯模糊 ——
    在多卡片页面是明显的「卡顿」来源。现改为 **固定 blurRadius + 只动画颜色
    alpha**（``glowAlpha`` 自定义属性）：重新「染色」远比重新「模糊」便宜，
    呼吸观感几乎一致，CPU 占用大幅下降。
    """

    def __init__(self, widget: QWidget, color: str = "#00BFFF",
                 base: int = 18, peak: int = 46) -> None:
        super().__init__(widget)
        self._c = QColor(color)
        # 固定模糊半径取 base/peak 的中间偏大值 —— 全程不再改变，杜绝重模糊。
        self._fixed_blur = int(round((base + peak) / 2))
        self._base_alpha = 90    # 静息亮度
        self._peak_alpha = 235   # 呼吸峰值亮度
        self._alpha = self._base_alpha
        self.setOffset(0, 0)
        self.setBlurRadius(self._fixed_blur)
        self._apply_alpha(self._base_alpha)
        widget.setGraphicsEffect(self)

        self._anim = QPropertyAnimation(self, b"glowAlpha", self)
        self._anim.setDuration(1400)
        self._anim.setStartValue(self._base_alpha)
        self._anim.setEndValue(self._peak_alpha)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)
        _anim().track(self._anim)

    # ── 自定义动画属性：只改颜色 alpha（廉价 re-tint，不触发重模糊） ──
    def _apply_alpha(self, a: int) -> None:
        c = QColor(self._c)
        c.setAlpha(int(max(0, min(255, a))))
        self.setColor(c)

    def get_glow_alpha(self) -> int:
        return self._alpha

    def set_glow_alpha(self, a: int) -> None:
        self._alpha = int(a)
        self._apply_alpha(self._alpha)

    glowAlpha = pyqtProperty(int, fget=get_glow_alpha, fset=set_glow_alpha)

    def set_color(self, color: str) -> None:
        self._c = QColor(color)
        self._apply_alpha(self._alpha)

    def start(self) -> None:
        # 来回呼吸
        self._anim.setDirection(QAbstractAnimation.Direction.Forward)
        self._anim.start()

    def pulse_once(self) -> None:
        self._anim.stop()
        self.set_glow_alpha(self._peak_alpha)

    def stop(self) -> None:
        self._anim.stop()
        self.set_glow_alpha(self._base_alpha)


class ShimmerSkeleton(QWidget):
    """骨架屏占位块：圆角灰块 + 自左向右循环的浅白极光扫掠（FrameClock 驱动）。"""

    def __init__(self, parent: QWidget | None = None, *,
                 width: int = 200, height: int = 16, radius: int = 8) -> None:
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._radius = radius
        self._pos = -0.4
        self._clock = FrameClock.instance()
        self._subscribed = False

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        self.stop()

    def _on_frame(self, _t: float, dt: float) -> None:
        self._pos += dt * 2.2
        if self._pos > 1.4:
            self._pos = -0.4
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 16))
        p.drawRoundedRect(rect, self._radius, self._radius)

        # 扫掠高光
        w = rect.width()
        g = QLinearGradient(self._pos * w - 60, 0, self._pos * w + 60, 0)
        g.setColorAt(0.0, QColor(255, 255, 255, 0))
        g.setColorAt(0.5, QColor(255, 255, 255, 60))
        g.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(g)
        p.drawRoundedRect(rect, self._radius, self._radius)

    def stop(self) -> None:
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False
