"""charts.line —— 动画折线图（WorldCup 3.0）。

折线随 ``reveal`` 0→1 从左到右**渐进绘出**（progressive path reveal，
300ms/OutCubic）。落定时折线顶点与输入数据精确一致。

渐进揭示的纯几何抽成 :func:`line_reveal_points`，便于无头属性测试
（设计 Property 20）。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette
from app.ui.widgets.charts.base import BaseChart


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def line_reveal_points(points, reveal: float) -> list[tuple[float, float]]:
    """纯函数：折线沿 X 方向渐进揭示后的可见顶点序列。

    ``reveal`` 表示沿折线（按顶点索引等分）已绘出的比例：
    * ``reveal >= 1`` → **精确返回**全部顶点（落定几何 == 输入数据，需求 24.2）。
    * 否则返回前若干完整顶点，并在当前段上插入一个插值端点。

    对单调增大的 ``reveal``，返回序列的覆盖范围单调扩张（需求 24.1）。
    """
    pts = [(float(x), float(y)) for (x, y) in points]
    n = len(pts)
    if n == 0:
        return []
    r = _clamp(reveal)
    if r >= 1.0 or n == 1:
        return list(pts)
    span = (n - 1) * r              # 已揭示的「段进度」
    full = int(math.floor(span))    # 完整可见的最后一个顶点索引
    out = list(pts[: full + 1])
    frac = span - full
    if frac > 0.0 and full < n - 1:
        x0, y0 = pts[full]
        x1, y1 = pts[full + 1]
        out.append((x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac))
    return out


class LineChart(BaseChart):
    """从左到右渐进绘出的折线图。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent)
        self.setMinimumSize(240, 160)
        self._palette = palette
        self._values: list[float] = []
        self._max_value: float = 1.0
        self._accent = QColor(palette.primary)

    def set_series(self, values, *, max_value: float | None = None,
                   accent: str | None = None) -> None:
        self._values = [float(v) for v in values]
        self._max_value = float(max_value) if max_value else (
            max(self._values) if self._values else 1.0)
        if accent:
            self._accent = QColor(accent)
        self._start_reveal()

    def _layout_points(self) -> list[tuple[float, float]]:
        """把数据序列映射到控件像素坐标（满量程，不含揭示）。"""
        n = len(self._values)
        if n == 0:
            return []
        pad = 12.0
        w = max(1.0, self.width() - 2 * pad)
        h = max(1.0, self.height() - 2 * pad)
        mx = self._max_value if self._max_value > 0 else 1.0
        out = []
        for i, v in enumerate(self._values):
            x = pad + (w * i / (n - 1) if n > 1 else 0.0)
            y = pad + h * (1.0 - _clamp(v / mx))
            out.append((x, y))
        return out

    def paintEvent(self, _ev) -> None:
        if not self._values:
            return
        full = self._layout_points()
        vis = line_reveal_points(full, self.get_reveal())
        if len(vis) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(self._accent, 2.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(QPolygonF([QPointF(x, y) for (x, y) in vis]))
