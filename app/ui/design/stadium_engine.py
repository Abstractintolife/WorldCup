"""StadiumEngine —— 广播级球场场景烘焙引擎。

把「世界杯赛事中心」的第一印象浓缩成一张**整体预渲染**的球场场景图：
夜空 + 看台人群辉光 + 体育场灯柱光锥 + 带透视割草纹的草坪 + 球场白线 +
四周暗角 + 顶部聚光。所有图层一次性合成进一张 ``QPixmap`` 并缓存
（key = 尺寸 + 皮肤名）——控件 ``paintEvent`` 只需 ``drawPixmap``，**逐帧零开销**，
因此既有电视转播包装的视觉冲击，又完全符合「禁止实时重绘 / 实时模糊」的性能铁律。

动态感由两部分提供且都不增加 Hero 的重绘成本：
* 顶部透出的全局 ``SkinBackdrop``（粒子 / 光束）。
* Hero 载入时由 ``AnimationManager`` 驱动的数字 count-up 与淡入。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QPolygonF,
    QRadialGradient,
)

from app.ui.theme import ThemePalette

_CACHE: dict[tuple, QPixmap] = {}
_MAX_ENTRIES = 8


def _lerp_color(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
    )


def stadium_pixmap(width: int, height: int, palette: ThemePalette,
                   *, radius: int = 22) -> QPixmap:
    """返回一张预渲染的球场场景贴图（带缓存）。"""
    width = max(1, int(width))
    height = max(1, int(height))
    key = (width, height, palette.name, radius)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached

    pm = QPixmap(width, height)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    rect = QRectF(0, 0, width, height)
    clip = QPainterPath()
    clip.addRoundedRect(rect, float(radius), float(radius))
    p.setClipPath(clip)

    _paint_sky(p, rect, palette)
    _paint_crowd(p, rect, palette)
    _paint_light_cones(p, rect, palette)
    _paint_pitch(p, rect, palette)
    _paint_vignette(p, rect)
    _paint_edge(p, rect, radius)

    p.end()

    if len(_CACHE) >= _MAX_ENTRIES:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = pm
    return pm


# ── 图层 ──────────────────────────────────────────────
def _paint_sky(p: QPainter, rect: QRectF, t: ThemePalette) -> None:
    """夜空：自上而下三段渐变（顶部最深 → 地平线偏亮）。"""
    g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    g.setColorAt(0.0, QColor(t.hero_grad_a))
    g.setColorAt(0.5, QColor(t.hero_grad_b))
    g.setColorAt(0.62, _lerp_color(QColor(t.hero_grad_b), QColor(t.primary), 0.18))
    g.setColorAt(1.0, QColor(t.hero_grad_c))
    p.fillRect(rect, QBrush(g))


def _paint_crowd(p: QPainter, rect: QRectF, t: ThemePalette) -> None:
    """看台人群辉光：地平线（约 58% 高度）上方一排柔和光斑。"""
    horizon = rect.height() * 0.58
    p.setPen(Qt.PenStyle.NoPen)
    band = QLinearGradient(QPointF(0, horizon - 70), QPointF(0, horizon))
    sc = QColor(t.secondary)
    band.setColorAt(0.0, QColor(sc.red(), sc.green(), sc.blue(), 0))
    band.setColorAt(1.0, QColor(sc.red(), sc.green(), sc.blue(), 46))
    p.setBrush(QBrush(band))
    p.drawRect(QRectF(0, horizon - 70, rect.width(), 70))

    # 离散人群光点（确定性，不随机，保证缓存稳定）
    cols = max(10, int(rect.width() // 46))
    for i in range(cols):
        fx = (i + 0.5) / cols
        x = fx * rect.width()
        amp = 0.5 + 0.5 * math.sin(i * 1.7)
        rr = 26 + amp * 16
        gl = QRadialGradient(QPointF(x, horizon - 22), rr)
        c = QColor(t.primary) if i % 3 else QColor(t.accent)
        gl.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), int(34 + amp * 28)))
        gl.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        p.setBrush(QBrush(gl))
        p.drawEllipse(QPointF(x, horizon - 22), rr, rr)


def _paint_light_cones(p: QPainter, rect: QRectF, t: ThemePalette) -> None:
    """四盏体育场灯柱光锥（自上方射向草坪）。"""
    p.setPen(Qt.PenStyle.NoPen)
    cone_specs = [
        (0.12, t.primary, 64),
        (0.40, t.secondary, 52),
        (0.62, t.secondary, 52),
        (0.88, t.primary, 64),
    ]
    for fx, col_hex, alpha in cone_specs:
        apex = QPointF(rect.width() * fx, -rect.height() * 0.08)
        spread = rect.width() * 0.10
        bottom_y = rect.height() * 0.92
        poly = QPolygonF([
            apex,
            QPointF(rect.width() * fx - spread, bottom_y),
            QPointF(rect.width() * fx + spread, bottom_y),
        ])
        lg = QLinearGradient(apex, QPointF(rect.width() * fx, bottom_y))
        c = QColor(col_hex)
        lg.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), alpha))
        lg.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        p.setBrush(QBrush(lg))
        p.drawPolygon(poly)


def _paint_pitch(p: QPainter, rect: QRectF, t: ThemePalette) -> None:
    """草坪：底部约 42% 高度，带透视割草条纹 + 中线 + 中圈弧。"""
    horizon = rect.height() * 0.58
    w = rect.width()
    h = rect.height()
    pitch_rect = QRectF(0, horizon, w, h - horizon)

    p.save()
    pclip = QPainterPath()
    pclip.addRect(pitch_rect)
    p.setClipPath(pclip)

    # 草地基础渐变（远端暗、近端亮）
    base = QLinearGradient(QPointF(0, horizon), QPointF(0, h))
    base.setColorAt(0.0, QColor(10, 46, 24))
    base.setColorAt(1.0, QColor(22, 94, 48))
    p.setPen(Qt.PenStyle.NoPen)
    p.fillRect(pitch_rect, QBrush(base))

    # 透视割草条纹：从地平线向下，条纹越来越高（近大远小）
    y = horizon
    idx = 0
    while y < h:
        frac = (y - horizon) / (h - horizon + 0.001)
        band_h = 8 + frac * 46
        if idx % 2 == 0:
            p.setBrush(QColor(255, 255, 255, 14))
            p.drawRect(QRectF(0, y, w, band_h))
        y += band_h
        idx += 1

    # 中线 + 中圈（白线，带轻微发光）
    cx = w / 2.0
    mid_y = horizon + (h - horizon) * 0.30
    pen_w = 2.4
    from PyQt6.QtGui import QPen
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(255, 255, 255, 70), pen_w))
    p.drawLine(QPointF(0, mid_y), QPointF(w, mid_y))
    ell_w = w * 0.16
    ell_h = (h - horizon) * 0.34
    p.drawEllipse(QPointF(cx, mid_y), ell_w, ell_h)
    p.setBrush(QColor(255, 255, 255, 70))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, mid_y), 3.0, 3.0)

    p.restore()


def _paint_vignette(p: QPainter, rect: QRectF) -> None:
    """四周暗角，聚焦视觉中心。"""
    p.setPen(Qt.PenStyle.NoPen)
    rg = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.62)
    rg.setColorAt(0.0, QColor(0, 0, 0, 0))
    rg.setColorAt(0.78, QColor(0, 0, 0, 0))
    rg.setColorAt(1.0, QColor(0, 0, 0, 120))
    p.setBrush(QBrush(rg))
    p.drawRect(rect)


def _paint_edge(p: QPainter, rect: QRectF, radius: int) -> None:
    """顶部高光描边。"""
    from PyQt6.QtGui import QPen
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(255, 255, 255, 30), 1.0))
    p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), float(radius), float(radius))


def clear_cache() -> None:
    _CACHE.clear()
