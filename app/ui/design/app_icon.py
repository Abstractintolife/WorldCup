"""应用图标：程序化绘制的「世界杯大力神杯」徽章。

不依赖任何外部图片资源 —— 直接用 QPainter 在多档尺寸下绘制一枚
圆角徽章：深蓝渐变底 + 顶部紫光 + 金色奖杯 + 点缀星芒。
窗口左上角、任务栏、Alt-Tab 均会使用它。
"""
from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QRadialGradient,
)

# 在 256×256 的设计坐标系内绘制，再按目标尺寸缩放，保证各档清晰。
_BASE = 256.0

_GOLD_HI = QColor("#FFF0A8")
_GOLD = QColor("#FFD24D")
_GOLD_LO = QColor("#C8962A")
_GOLD_DEEP = QColor("#8A5A00")


def _draw_star(p: QPainter, cx: float, cy: float, r: float, color: QColor) -> None:
    p.save()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(color)
    pts = []
    import math
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.4
        pts.append(QPointF(cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    p.drawPolygon(QPolygonF(pts))
    p.restore()


def _paint(p: QPainter) -> None:
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # ── 圆角徽章底（深蓝竖向渐变） ──
    tile = QRectF(6, 6, _BASE - 12, _BASE - 12)
    radius = _BASE * 0.235
    clip = QPainterPath()
    clip.addRoundedRect(tile, radius, radius)
    p.setClipPath(clip)

    bg = QLinearGradient(tile.topLeft(), tile.bottomLeft())
    bg.setColorAt(0.0, QColor("#15264A"))
    bg.setColorAt(0.55, QColor("#0E1A33"))
    bg.setColorAt(1.0, QColor("#080F1E"))
    p.fillRect(tile, bg)

    # 顶部皇家紫光晕
    glow = QRadialGradient(QPointF(_BASE * 0.5, _BASE * 0.16), _BASE * 0.7)
    glow.setColorAt(0.0, QColor(106, 90, 205, 150))
    glow.setColorAt(1.0, QColor(106, 90, 205, 0))
    p.fillRect(tile, glow)
    # 左下电光蓝光晕
    glow2 = QRadialGradient(QPointF(_BASE * 0.2, _BASE * 0.92), _BASE * 0.6)
    glow2.setColorAt(0.0, QColor(0, 191, 255, 90))
    glow2.setColorAt(1.0, QColor(0, 191, 255, 0))
    p.fillRect(tile, glow2)

    # ── 奖杯 ──
    gold_grad = QLinearGradient(QPointF(_BASE * 0.5, 70), QPointF(_BASE * 0.5, 210))
    gold_grad.setColorAt(0.0, _GOLD_HI)
    gold_grad.setColorAt(0.45, _GOLD)
    gold_grad.setColorAt(1.0, _GOLD_LO)
    outline = QPen(QColor(90, 60, 0, 200), 3.0)
    outline.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    # 把手（两侧描边椭圆，先画，被杯身覆盖内半部）
    handle_pen = QPen(_GOLD_LO, 11.0)
    handle_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(handle_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(58, 86, 46, 60), int(-70 * 16), int(-150 * 16))
    p.drawArc(QRectF(152, 86, 46, 60), int(70 * 16), int(150 * 16))

    # 杯身
    bowl = QPainterPath()
    bowl.moveTo(82, 82)
    bowl.lineTo(174, 82)
    bowl.cubicTo(172, 120, 152, 152, 128, 152)
    bowl.cubicTo(104, 152, 84, 120, 82, 82)
    bowl.closeSubpath()
    p.setPen(outline)
    p.setBrush(QBrush(gold_grad))
    p.drawPath(bowl)

    # 杯口椭圆（高光描边）
    p.setBrush(QBrush(_GOLD_HI))
    p.setPen(QPen(QColor(90, 60, 0, 160), 2.5))
    p.drawEllipse(QRectF(80, 72, 96, 20))

    # 杯柄
    p.setPen(outline)
    stem = QPainterPath()
    stem.addRoundedRect(QRectF(120, 150, 16, 22), 4, 4)
    p.fillPath(stem, QBrush(gold_grad))
    p.drawPath(stem)

    # 底座（梯形 + 底板）
    base = QPainterPath()
    base.moveTo(104, 172)
    base.lineTo(152, 172)
    base.lineTo(160, 192)
    base.lineTo(96, 192)
    base.closeSubpath()
    p.fillPath(base, QBrush(gold_grad))
    p.drawPath(base)
    plinth = QPainterPath()
    plinth.addRoundedRect(QRectF(90, 190, 76, 16), 5, 5)
    p.fillPath(plinth, QBrush(gold_grad))
    p.drawPath(plinth)

    # 杯身高光（竖向亮条）
    p.setPen(Qt.PenStyle.NoPen)
    shine = QLinearGradient(QPointF(110, 84), QPointF(118, 150))
    shine.setColorAt(0.0, QColor(255, 255, 255, 150))
    shine.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.setBrush(shine)
    hl = QPainterPath()
    hl.moveTo(108, 86)
    hl.lineTo(120, 86)
    hl.cubicTo(116, 120, 112, 138, 116, 148)
    hl.cubicTo(108, 138, 106, 110, 108, 86)
    hl.closeSubpath()
    p.drawPath(hl)

    # 星芒点缀
    _draw_star(p, 196, 66, 12, QColor(255, 255, 255, 230))
    _draw_star(p, 210, 92, 7, QColor("#FFD24D"))
    _draw_star(p, 64, 70, 6, QColor(255, 255, 255, 180))


@lru_cache(maxsize=1)
def build_app_icon() -> QIcon:
    """生成多档尺寸的应用图标（带缓存，全应用复用）。"""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.scale(size / _BASE, size / _BASE)
        try:
            _paint(p)
        finally:
            p.end()
        icon.addPixmap(pm)
    return icon
