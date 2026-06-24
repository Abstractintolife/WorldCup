"""charts.bar —— 动画柱状图（WorldCup 3.0）。

柱子高度随 ``reveal`` 0→1「生长」（300ms/OutCubic）。落定时各柱高度比例
精确等于 ``value / max_value``。

高度映射抽成纯函数 :func:`bar_reveal_heights`，便于无头属性测试
（设计 Property 20）。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette
from app.ui.widgets.charts.base import BaseChart, reveal_value


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def bar_reveal_heights(values, max_value: float, full_height: float,
                       reveal: float) -> list[float]:
    """纯函数：各柱在揭示进度 ``reveal`` 处的像素高度。

    第 ``i`` 柱满量程高度为 ``full_height · clamp(value/max_value, 0, 1)``，
    再乘以揭示比例：``reveal == 1`` 时精确等于满量程高度（落定几何 == 输入
    数据，需求 24.2）；对非负值随 ``reveal`` 单调非减（需求 24.1）。
    """
    mx = max_value if max_value > 0 else 1.0
    out = []
    for v in values:
        full = full_height * _clamp(v / mx)
        out.append(reveal_value(full, reveal))
    return out


class BarChart(BaseChart):
    """高度生长式柱状图。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent)
        self.setMinimumSize(220, 160)
        self._palette = palette
        self._values: list[float] = []
        self._max_value: float = 1.0
        self._accent = QColor(palette.primary)

    def set_bars(self, values, *, max_value: float | None = None,
                 accent: str | None = None) -> None:
        self._values = [float(v) for v in values]
        self._max_value = float(max_value) if max_value else (
            max(self._values) if self._values else 1.0)
        if accent:
            self._accent = QColor(accent)
        self._start_reveal()

    def paintEvent(self, _ev) -> None:
        if not self._values:
            return
        n = len(self._values)
        pad = 12.0
        w = max(1.0, self.width() - 2 * pad)
        h = max(1.0, self.height() - 2 * pad)
        base_y = pad + h
        heights = bar_reveal_heights(self._values, self._max_value, h, self.get_reveal())

        gap = 8.0
        bar_w = max(1.0, (w - gap * (n - 1)) / n) if n else w

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._accent)
        for i, bh in enumerate(heights):
            x = pad + i * (bar_w + gap)
            rect = QRectF(x, base_y - bh, bar_w, bh)
            p.drawRoundedRect(rect, 4.0, 4.0)
