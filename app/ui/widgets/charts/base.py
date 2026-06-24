"""charts.base —— 动画图表共享基类与纯几何映射（WorldCup 3.0）。

广播风的雷达 / 折线 / 柱状图共享同一条「揭示进度」动画：``reveal`` 从 0→1
经 **300ms / OutCubic** 推进（``CHART_REFRESH_MS``），落定时几何精确等于输入
数据。

数值数学全部抽成无 GUI 依赖的纯函数（:func:`eased_reveal` /
:func:`reveal_value` / :func:`reveal_values`），三种图表共用，便于无头属性
测试（设计 Property 20）：

* 24.1 —— 收到数据后，揭示进度从 0 单调增长到 1。
* 24.2 —— 揭示完成时几何与输入数据值一致。
* 24.3 —— 刷新目标 300ms（OutCubic）。
"""
from __future__ import annotations

from PyQt6.QtCore import (
    QAbstractAnimation,
    QPropertyAnimation,
    pyqtProperty,
)
from PyQt6.QtWidgets import QWidget

from app.config import LOW_PERF
from app.ui.design.motion_system import EASE_STANDARD

#: 图表刷新 / 揭示时长（毫秒）。
CHART_REFRESH_MS = 300
#: 唯一缓动曲线 —— 复用统一动效系统的 ``EASE_STANDARD``（OutCubic），
#: 确保图表与全应用共享同一条运动曲线（设计 "Motion Design System"）。
EASE = EASE_STANDARD


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def eased_reveal(p: float) -> float:
    """OutCubic 揭示缓动：``1 - (1-p)^3``。

    ``p`` ∈ [0,1]，单调非减；``eased_reveal(0) == 0``，``eased_reveal(1) == 1``。
    """
    p = _clamp(p)
    return 1.0 - (1.0 - p) ** 3


def reveal_value(value: float, reveal: float) -> float:
    """纯函数：揭示进度 ``reveal`` ∈ [0,1] 处某个值的几何幅度 ``value * reveal``。

    * ``reveal >= 1`` → **精确返回** ``value``（落定即输入数据，需求 24.2）。
    * 对非负 ``value`` 随 ``reveal`` 单调非减（需求 24.1）。
    """
    r = _clamp(reveal)
    if r >= 1.0:
        return value
    return value * r


def reveal_values(values, reveal: float) -> list[float]:
    """纯函数：对一组值逐个施加 :func:`reveal_value`。

    ``reveal == 1`` 时返回的列表逐元素精确等于输入 ``values``。
    """
    return [reveal_value(v, reveal) for v in values]


class BaseChart(QWidget):
    """动画图表基类：统一持有 ``reveal`` 属性与 300ms/OutCubic 揭示动画。

    子类只需实现 :meth:`paintEvent`，读取 ``self.reveal`` 把几何按比例揭示；
    设置数据后调用 :meth:`_start_reveal` 触发 0→1 动画。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reveal = 0.0
        self._anim = QPropertyAnimation(self, b"reveal", self)
        self._anim.setDuration(CHART_REFRESH_MS)   # 300ms
        self._anim.setEasingCurve(EASE)            # OutCubic
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)

    # ── 揭示动画 ─────────────────────────────
    def _start_reveal(self) -> None:
        """从 0 重新揭示到 1。``LOW_PERF`` 省电模式下瞬时落定。"""
        self._anim.stop()
        if LOW_PERF:
            self._set_reveal(1.0)
            return
        self._set_reveal(0.0)
        self._anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)

    # ── reveal 属性（动画驱动） ───────────────
    def _set_reveal(self, value: float) -> None:
        self._reveal = _clamp(float(value))
        self.update()

    def get_reveal(self) -> float:
        return self._reveal

    reveal = pyqtProperty(float, fget=get_reveal, fset=_set_reveal)
