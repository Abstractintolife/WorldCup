"""floating_flag —— 上下浮动的旗帜控件（WorldCup 3.0）。

包裹既有 :class:`~app.ui.widgets.flag_icon.FlagIcon`，让其在垂直方向以
**±3px / 4 秒** 的正弦节律持续轻微浮动（Hero 区的「活起来」氛围）。

实现：自定义 ``floatY`` 属性 + 单条循环 ``QPropertyAnimation``（4000ms、
``LoopCount = -1``）。为避免「关键帧 + 缓动曲线」的相互作用歧义，动画推进的是
一个 ``phase`` ∈ [0,1] 的线性相位，偏移量经纯函数 :func:`floating_offset_from_phase`
（``A·sin(2π·phase)``）求得 —— 这正是一个平滑的正弦往复（InOutSine 形态），
天然落在 ``[-3, +3]`` 内、周期精确 4 秒。

对应需求 22.1（偏移 ∈ [-3,+3]）/ 22.2（周期 4 秒）。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    pyqtProperty,
)
from PyQt6.QtWidgets import QWidget

from app.config import LOW_PERF
from app.ui.widgets.flag_icon import FlagIcon

#: 浮动幅度（像素）—— 偏移恒在 ``[-AMPLITUDE, +AMPLITUDE]``。
FLOAT_AMPLITUDE_PX = 3.0
#: 一个完整振荡周期（秒 / 毫秒）。
FLOAT_PERIOD_S = 4.0
FLOAT_PERIOD_MS = int(FLOAT_PERIOD_S * 1000)


def floating_offset_from_phase(phase: float, amplitude: float = FLOAT_AMPLITUDE_PX) -> float:
    """纯函数：给定相位 ``phase`` ∈ [0,1]，返回垂直偏移 ``A·sin(2π·phase)``。

    结果恒在 ``[-amplitude, +amplitude]`` 内；``phase`` 每 +1 即一个完整周期。
    """
    return amplitude * math.sin(2.0 * math.pi * phase)


def floating_offset(t: float, amplitude: float = FLOAT_AMPLITUDE_PX,
                    period: float = FLOAT_PERIOD_S) -> float:
    """纯函数：给定时间 ``t``（秒），返回浮动偏移。

    ``A·sin(2π·t/period)``，振幅 ``amplitude``、周期 ``period``，恒在
    ``[-amplitude, +amplitude]`` 内。
    """
    return amplitude * math.sin(2.0 * math.pi * (t / period))


class FloatingFlag(QWidget):
    """以 ±3px / 4s 正弦节律上下浮动的旗帜。

    控件固定尺寸为「旗面尺寸 + 上下各留 ``AMPLITUDE`` 余量」，因此旗面在
    整个振荡区间内都不会被裁切。
    """

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

        self._flag = FlagIcon(nationality, self, height=height, radius=radius)
        self._margin = int(math.ceil(FLOAT_AMPLITUDE_PX))
        fw = self._flag.width()
        fh = self._flag.height()
        # 预留上下浮动余量，避免裁切。
        self.setFixedSize(fw, fh + 2 * self._margin)

        self._phase = 0.0
        self._float_y = 0.0
        self._place_flag()

        self._anim = QPropertyAnimation(self, b"phase", self)
        self._anim.setDuration(FLOAT_PERIOD_MS)      # 4s 周期
        self._anim.setLoopCount(-1)                   # 持续循环（氛围动画）
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        # 线性推进相位；正弦由 floating_offset_from_phase 提供（即 InOutSine 往复）。
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

    # ── 旗面定位 ─────────────────────────────
    def _place_flag(self) -> None:
        x = (self.width() - self._flag.width()) // 2
        # 基线在中央余量处；偏移 float_y ∈ [-margin, +margin]。
        y = self._margin + int(round(self._float_y))
        self._flag.move(x, y)

    # ── 公共 API ─────────────────────────────
    def set_nationality(self, nationality: str | None) -> None:
        self._flag.set_nationality(nationality)

    def start_float(self) -> None:
        """开始浮动循环。``LOW_PERF`` 省电模式下保持静止（不启动定时驱动）。"""
        if LOW_PERF:
            self._set_phase(0.0)
            return
        if self._anim.state() != QAbstractAnimation.State.Running:
            self._anim.start()

    def stop_float(self) -> None:
        self._anim.stop()
        self._set_phase(0.0)

    @property
    def float_y(self) -> float:
        return self._float_y

    # ── phase 属性（动画驱动） ────────────────
    def _set_phase(self, value: float) -> None:
        self._phase = float(value)
        self._float_y = floating_offset_from_phase(self._phase)
        self._place_flag()

    def get_phase(self) -> float:
        return self._phase

    phase = pyqtProperty(float, fget=get_phase, fset=_set_phase)
