"""未来战术版「五维雷达图」。

* 极细发光网格线（同心多边形 + 辐条），科幻战术扫描仪质感。
* 数据区域高饱和霓虹半透明渐变填充。
* 打开时从中心点「生长」到真实数值（QPropertyAnimation 驱动 progress）。
* 可选「外圈红色发光呼吸」—— ``set_breathing_glow(True)`` 开启 4 秒
  周期的外发光呼吸（FC26 / FUT 风格）。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
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


class RadarChart(QWidget):
    """五维能力雷达图。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(260, 240)
        # [(code, zh, value0-99, colorhex), ...]
        self._data: list[tuple[str, str, int, str]] = []
        self._accent = QColor("#00BFFF")
        self._progress = 0.0
        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(1100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 呼吸光晕
        self._breath_enabled = False
        self._breath_color = QColor("#FF0050")
        self._breath_t = 0.0
        self._breath_anim = QPropertyAnimation(self, b"breath", self)
        self._breath_anim.setDuration(4000)   # 4s 周期
        self._breath_anim.setLoopCount(-1)
        self._breath_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath_anim.setStartValue(0.0)
        self._breath_anim.setEndValue(1.0)
        self._breath_anim.setDirection(QAbstractAnimation.Direction.Forward)

    def set_data(self, data: list[tuple[str, str, int, str]],
                 accent: str = "#00BFFF") -> None:
        self._data = data
        self._accent = QColor(accent)
        self.start_animation()

    def set_breathing_glow(self, enabled: bool, color: str = "#FF0050") -> None:
        """开关外圈红色发光呼吸（4 秒周期）。"""
        self._breath_color = QColor(color)
        self._breath_enabled = bool(enabled)
        if enabled:
            if self._breath_anim.state() != QAbstractAnimation.State.Running:
                self._breath_anim.start()
        else:
            self._breath_anim.stop()
            self._breath_t = 0.0
        self.update()

    def start_animation(self) -> None:
        self._anim.stop()
        self._progress = 0.0
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    # progress 属性（动画驱动）
    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, v: float) -> None:
        self._progress = float(v)
        self.update()

    progress = pyqtProperty(float, fget=get_progress, fset=set_progress)

    # 呼吸 0..1（PingPong 一遍 = 2s 上 + 2s 下，但我们用 LoopCount=-1 + InOutSine
    # 来回循环）
    def get_breath(self) -> float:
        return self._breath_t

    def set_breath(self, v: float) -> None:
        # 把单调 0..1 折成正弦：0→1→0
        import math as _math
        x = float(v)
        self._breath_t = (1.0 - _math.cos(2 * _math.pi * x)) * 0.5
        self.update()

    breath = pyqtProperty(float, fget=get_breath, fset=set_breath)

    # ── 绘制 ─────────────────────────────────
    def paintEvent(self, _ev) -> None:
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._data)
        cx, cy = self.width() / 2.0, self.height() / 2.0 + 6
        radius = min(self.width(), self.height()) * 0.34

        # ★ 外圈红色发光呼吸（0 0 40px rgba(255,0,80,.3)，4s 循环）
        if self._breath_enabled:
            t = self._breath_t   # 0..1
            blur = 28.0 + 24.0 * t
            alpha_outer = int(60 + 70 * t)        # ~60..130
            alpha_inner = int(120 + 80 * t)       # ~120..200
            glow = QRadialGradient(QPointF(cx, cy), radius + blur)
            bc = self._breath_color
            glow.setColorAt(0.55, QColor(bc.red(), bc.green(), bc.blue(), alpha_inner))
            glow.setColorAt(0.85, QColor(bc.red(), bc.green(), bc.blue(), alpha_outer))
            glow.setColorAt(1.0, QColor(bc.red(), bc.green(), bc.blue(), 0))
            p.setBrush(glow)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), radius + blur, radius + blur)

        def vertex(i: int, r: float) -> QPointF:
            ang = -math.pi / 2 + 2 * math.pi * i / n
            return QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang))

        # 同心网格（4 圈）
        rings = 4
        for k in range(1, rings + 1):
            rr = radius * k / rings
            poly = QPolygonF([vertex(i, rr) for i in range(n)])
            alpha = 26 if k < rings else 55
            p.setPen(QPen(QColor(120, 150, 200, alpha), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(poly)

        # 辐条
        for i in range(n):
            p.setPen(QPen(QColor(120, 150, 200, 40), 1.0))
            p.drawLine(QPointF(cx, cy), vertex(i, radius))

        # 数据多边形（受 progress 控制）
        ac = self._accent
        pts = []
        for i, (_code, _zh, val, _c) in enumerate(self._data):
            r = radius * (val / 99.0) * self._progress
            pts.append(vertex(i, r))
        poly = QPolygonF(pts)

        # 填充：从 #ff4f79 渐变到 #ff7eb3 的径向渐变（alpha ~0.25 = 64）
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 72))
        grad.setColorAt(0.7, QColor(ac.red(), ac.green(), ac.blue(), 54))
        grad.setColorAt(1.0, QColor(ac.red(), ac.green(), ac.blue(), 26))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(ac, 2.2))
        p.drawPolygon(poly)

        # 顶点光点
        p.setPen(Qt.PenStyle.NoPen)
        for pt in pts:
            glow = QRadialGradient(pt, 7)
            glow.setColorAt(0.0, QColor(255, 255, 255, 230))
            glow.setColorAt(1.0, QColor(ac.red(), ac.green(), ac.blue(), 0))
            p.setBrush(QBrush(glow))
            p.drawEllipse(pt, 6, 6)
            p.setBrush(QColor("#ffffff"))
            p.drawEllipse(pt, 2.2, 2.2)

        # 标签 + 数值
        f = QFont(self.font())
        f.setPointSize(9)
        f.setBold(True)
        p.setFont(f)
        for i, (code, _zh, val, color) in enumerate(self._data):
            lp = vertex(i, radius + 20)
            # 数值（带颜色）
            p.setPen(QColor(color))
            shown = int(round(val * self._progress))
            rect_w = 56
            p.drawText(
                int(lp.x() - rect_w / 2), int(lp.y() - 9), rect_w, 14,
                int(Qt.AlignmentFlag.AlignCenter), str(shown),
            )
            # 维度名
            p.setPen(QColor("#B0BEC5"))
            p.drawText(
                int(lp.x() - rect_w / 2), int(lp.y() + 5), rect_w, 14,
                int(Qt.AlignmentFlag.AlignCenter), code,
            )
