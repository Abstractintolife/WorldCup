"""平滑滚动 —— 让「操作界面」真正享受高帧率。

问题
-----
默认 ``QScrollArea`` / 表格的滚轮滚动是「一格一格」的离散跳变，即便
很快，观感也是「卡顿/生硬」的。这与动效帧率无关 —— 它是交互层的体验。

方案
-----
拦截滚轮事件，把目标滚动位置交给 **全局 FrameClock** 逐帧用指数缓动
（时间驱动，帧率无关）平滑逼近。于是：

* 在 120/240FPS 下，滚动是丝滑的连续插值，而不是跳变；
* 连续快滚会叠加目标位移 → 自然的「惯性/动量」手感；
* 只有在滚动进行中才订阅时钟，停下立即退订，零空转。

对 ``QAbstractItemView``（表格/列表）会自动切换为「按像素滚动」，
保证位移单位统一为像素，惯性手感一致。
"""
from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtWidgets import QAbstractItemView, QAbstractScrollArea

from app.ui.design.frame_clock import FrameClock
from app.ui.design.motion import approach, clamp

# 每「一格」滚轮（angleDelta=120）对应的像素位移
_PX_PER_NOTCH = 96.0
# 缓动收敛速度（越大越跟手；时间驱动，帧率无关）
_FOLLOW_SPEED = 17.0


class SmoothScroller(QObject):
    """挂在某个滚动区域上的平滑滚动控制器。"""

    def __init__(self, area: QAbstractScrollArea) -> None:
        super().__init__(area)
        self._area = area
        self._vbar = area.verticalScrollBar()
        self._clock = FrameClock.instance()
        self._target = float(self._vbar.value())
        self._pos = float(self._vbar.value())
        self._active = False
        self._setting = False  # 防止自身 setValue 触发 valueChanged 递归

        if isinstance(area, QAbstractItemView):
            area.setVerticalScrollMode(
                QAbstractItemView.ScrollMode.ScrollPerPixel
            )

        area.viewport().installEventFilter(self)
        self._vbar.valueChanged.connect(self._on_bar_changed)

    # ── 事件拦截 ────────────────────────────
    def eventFilter(self, obj, ev) -> bool:
        if ev.type() == QEvent.Type.Wheel:
            # 没有可滚动内容 / 横向滚动 → 交回默认处理
            if self._vbar.maximum() <= self._vbar.minimum():
                return False
            dy = ev.angleDelta().y()
            if dy == 0:
                return False
            # 高精度触控板（pixelDelta）直接用像素增量，更顺
            pd = ev.pixelDelta()
            if not pd.isNull():
                step = float(pd.y())
            else:
                step = (dy / 120.0) * _PX_PER_NOTCH
            self._target = clamp(
                self._target - step,
                float(self._vbar.minimum()),
                float(self._vbar.maximum()),
            )
            self._ensure_active()
            ev.accept()
            return True
        return False

    def _on_bar_changed(self, value: int) -> None:
        # 外部改动（拖动滑块 / 键盘 / 程序跳转）时同步内部目标，避免回弹
        if self._setting or self._active:
            return
        self._target = float(value)
        self._pos = float(value)

    # ── 时钟订阅 ────────────────────────────
    def _ensure_active(self) -> None:
        self._pos = float(self._vbar.value())
        if not self._active:
            self._active = True
            self._clock.subscribe(self._on_frame)

    def _deactivate(self) -> None:
        if self._active:
            self._active = False
            self._clock.unsubscribe(self._on_frame)

    def _set_value(self, v: int) -> None:
        self._setting = True
        self._vbar.setValue(v)
        self._setting = False

    def _on_frame(self, _t: float, dt: float) -> None:
        # 内容高度可能变化，目标随时夹紧到合法范围
        self._target = clamp(
            self._target,
            float(self._vbar.minimum()),
            float(self._vbar.maximum()),
        )
        self._pos = approach(self._pos, self._target, dt, speed=_FOLLOW_SPEED)
        if abs(self._pos - self._target) < 0.5:
            self._pos = self._target
            self._set_value(int(round(self._pos)))
            self._deactivate()
            return
        self._set_value(int(round(self._pos)))


def enable_smooth_scrolling(area: QAbstractScrollArea) -> None:
    """为某滚动区域启用平滑滚动（幂等：重复调用无副作用）。"""
    if area is None or area.property("_smoothScroll"):
        return
    area.setProperty("_smoothScroll", True)
    SmoothScroller(area)
