"""仪表盘专用的轻量自绘图表组件（静态展示用）。

为「想象中的样子」概览页提供：
* :class:`DualRadarChart` —— 双队五维攻防雷达（蓝队 vs 绿队叠加）。
* :class:`Sparkline` —— 迷你折线图（总比赛趋势）。
* :class:`RingProgress` —— 圆环进度（场均控球率）。
* :class:`MiniBars` —— 迷你柱状图。

这些控件只负责「好看 + 稳定渲染」，不依赖网络数据。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QPolygonF,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget


class DualRadarChart(QWidget):
    """双队五维雷达图（攻防对比）。

    数据格式::

        set_data(
            dims=[("进攻","ATK"), ...],         # 维度（中文, 英文缩写）
            series=[("美国", [78,...], "#00BFFF"),
                    ("澳大利亚", [70,...], "#2ED877")],
        )
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self._dims: list[tuple[str, str]] = []
        self._series: list[tuple[str, list[int], str]] = []
        self._progress = 0.0
        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(1100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_data(self, dims, series) -> None:
        self._dims = list(dims)
        self._series = list(series)
        self._anim.stop()
        self._progress = 0.0
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, v: float) -> None:
        self._progress = float(v)
        self.update()

    progress = pyqtProperty(float, fget=get_progress, fset=set_progress)

    def paintEvent(self, _ev) -> None:
        if not self._dims or not self._series:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._dims)
        cx, cy = self.width() / 2.0, self.height() / 2.0 + 4
        radius = min(self.width(), self.height()) * 0.32

        def vertex(i: int, r: float) -> QPointF:
            ang = -math.pi / 2 + 2 * math.pi * i / n
            return QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang))

        # 同心网格
        rings = 4
        for k in range(1, rings + 1):
            rr = radius * k / rings
            poly = QPolygonF([vertex(i, rr) for i in range(n)])
            alpha = 24 if k < rings else 52
            p.setPen(QPen(QColor(120, 150, 200, alpha), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(poly)
        for i in range(n):
            p.setPen(QPen(QColor(120, 150, 200, 38), 1.0))
            p.drawLine(QPointF(cx, cy), vertex(i, radius))

        # 各队多边形
        for _name, values, color in self._series:
            ac = QColor(color)
            pts = []
            for i, val in enumerate(values[:n]):
                r = radius * (max(0, min(99, val)) / 99.0) * self._progress
                pts.append(vertex(i, r))
            poly = QPolygonF(pts)
            grad = QRadialGradient(cx, cy, radius)
            grad.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 70))
            grad.setColorAt(1.0, QColor(ac.red(), ac.green(), ac.blue(), 18))
            p.setBrush(QBrush(grad))
            p.setPen(QPen(ac, 2.2))
            p.drawPolygon(poly)
            p.setPen(Qt.PenStyle.NoPen)
            for pt in pts:
                p.setBrush(QColor("#ffffff"))
                p.drawEllipse(pt, 2.4, 2.4)
                p.setBrush(ac)
                p.drawEllipse(pt, 1.4, 1.4)

        # 维度标签
        f = QFont(self.font())
        f.setPointSize(9)
        f.setBold(True)
        p.setFont(f)
        for i, (zh, _en) in enumerate(self._dims):
            lp = vertex(i, radius + 18)
            p.setPen(QColor("#B0BEC5"))
            p.drawText(int(lp.x() - 30), int(lp.y() - 7), 60, 14,
                       int(Qt.AlignmentFlag.AlignCenter), zh)


class Sparkline(QWidget):
    """迷你折线图（带渐变填充）。"""

    def __init__(self, values: list[float], color: str = "#00BFFF",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._values = values or [1, 2, 1.5, 3, 2.4, 3.6, 3.1, 4.2]
        self._color = QColor(color)
        self.setMinimumSize(72, 34)

    def set_values(self, values: list[float], color: str | None = None) -> None:
        self._values = values
        if color:
            self._color = QColor(color)
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        vals = self._values
        if len(vals) < 2:
            return
        w, h = self.width(), self.height()
        lo, hi = min(vals), max(vals)
        rng = (hi - lo) or 1.0
        pad = 3
        pts = []
        for i, v in enumerate(vals):
            x = pad + (w - 2 * pad) * i / (len(vals) - 1)
            y = h - pad - (h - 2 * pad) * (v - lo) / rng
            pts.append(QPointF(x, y))
        # 渐变填充
        poly = QPolygonF([QPointF(pts[0].x(), h)] + pts + [QPointF(pts[-1].x(), h)])
        grad = QLinearGradient(0, 0, 0, h)
        c = self._color
        grad.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), 90))
        grad.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly)
        # 折线
        pen = QPen(c, 2.0)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(QPolygonF(pts))
        # 末端点
        p.setBrush(QColor("#ffffff"))
        p.setPen(QPen(c, 1.5))
        p.drawEllipse(pts[-1], 2.4, 2.4)


class RingProgress(QWidget):
    """圆环进度（百分比）。"""

    def __init__(self, percent: float = 53.0, color: str = "#00D4A4",
                 label: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target = percent
        self._percent = 0.0
        self._color = QColor(color)
        self._label = label
        self.setFixedSize(58, 58)
        self._anim = QPropertyAnimation(self, b"percent", self)
        self._anim.setDuration(1100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(percent))
        self._anim.start()

    def get_percent(self) -> float:
        return self._percent

    def set_percent(self, v: float) -> None:
        self._percent = float(v)
        self.update()

    percent = pyqtProperty(float, fget=get_percent, fset=set_percent)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(5, 5, -5, -5)
        # 底环
        p.setPen(QPen(QColor(255, 255, 255, 30), 5))
        p.drawArc(rect, 0, 360 * 16)
        # 进度环
        pen = QPen(self._color, 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        span = int(-self._percent / 100.0 * 360 * 16)
        p.drawArc(rect, 90 * 16, span)
        # 中央百分比
        f = QFont(self.font())
        f.setPointSize(11)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter),
                   f"{round(self._percent)}%")
