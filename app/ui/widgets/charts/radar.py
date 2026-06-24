"""charts.radar —— 动画雷达图（WorldCup 3.0）。

顶点从中心向各自数值「生长」（受共享 ``reveal`` 0→1 驱动，300ms/OutCubic）。
落定时各轴半径比例精确等于 ``value / max_value``。

几何映射抽成纯函数 :func:`radar_axis_fraction` / :func:`radar_vertices`，便于
无头属性测试（设计 Property 20）。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QRadialGradient
from PyQt6.QtWidgets import QWidget

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette
from app.ui.widgets.charts.base import BaseChart, reveal_value


def radar_axis_fraction(value: float, max_value: float) -> float:
    """纯函数：某轴在「满量程」下的半径比例 ``clamp(value/max_value, 0, 1)``。"""
    if max_value <= 0:
        return 0.0
    f = value / max_value
    return 0.0 if f < 0.0 else 1.0 if f > 1.0 else f


def radar_vertices(values, max_value: float, reveal: float,
                   cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    """纯函数：雷达多边形顶点坐标列表（受 ``reveal`` 揭示）。

    第 ``i`` 个顶点的半径为 ``radius · fraction_i · reveal``；``reveal == 1`` 时
    半径精确为 ``radius · fraction_i`` —— 即落定几何与输入数据一致。
    第 0 轴指向正上方，其余按顺时针等分。
    """
    n = len(values)
    out: list[tuple[float, float]] = []
    for i, v in enumerate(values):
        frac = radar_axis_fraction(v, max_value)
        r = reveal_value(radius * frac, reveal)
        ang = -math.pi / 2 + 2 * math.pi * i / n if n else 0.0
        out.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return out


class RadarChart(BaseChart):
    """五维（或 N 维）能力雷达图。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent)
        self.setMinimumSize(240, 220)
        self._palette = palette
        self._values: list[float] = []
        self._labels: list[str] = []
        self._max_value: float = 100.0
        self._accent = QColor(palette.primary)

    def set_data(self, values, *, max_value: float = 100.0,
                 labels: list[str] | None = None, accent: str | None = None) -> None:
        self._values = list(values)
        self._max_value = float(max_value)
        self._labels = list(labels) if labels else []
        if accent:
            self._accent = QColor(accent)
        self._start_reveal()

    def paintEvent(self, _ev) -> None:
        if not self._values:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._values)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        radius = min(self.width(), self.height()) * 0.36

        def vtx(i: int, r: float) -> QPointF:
            ang = -math.pi / 2 + 2 * math.pi * i / n
            return QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang))

        # 同心网格 + 辐条。
        for k in range(1, 5):
            rr = radius * k / 4
            poly = QPolygonF([vtx(i, rr) for i in range(n)])
            p.setPen(QPen(QColor(120, 150, 200, 30 if k < 4 else 60), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(poly)
        for i in range(n):
            p.setPen(QPen(QColor(120, 150, 200, 40), 1.0))
            p.drawLine(QPointF(cx, cy), vtx(i, radius))

        # 数据多边形（受 reveal 揭示）。
        pts = [QPointF(x, y) for (x, y) in
               radar_vertices(self._values, self._max_value, self.get_reveal(),
                              cx, cy, radius)]
        ac = self._accent
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 80))
        grad.setColorAt(1.0, QColor(ac.red(), ac.green(), ac.blue(), 26))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(ac, 2.0))
        p.drawPolygon(QPolygonF(pts))
