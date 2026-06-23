"""ResourceManager —— 静态资源（阴影 / 渐变）预渲染缓存。

为什么需要它
-------------
``QGraphicsDropShadowEffect`` / ``QGraphicsBlurEffect`` 是 Qt Widgets 最大的
性能杀手：每当被作用控件重绘（甚至只是 hover 改变 blurRadius）时，Qt 都要把
整块区域**重新栅格化 + 高斯模糊**一遍。在长列表 / 多卡片场景下，几十个实时
模糊同时跑，CPU 直接打满 —— 这正是「只有 30FPS」的根因之一。

正确做法（本模块提供）
----------------------
* :func:`drop_shadow_pixmap` —— 把「圆角矩形投影」**预渲染**成一张 ``QPixmap``
  并按参数 key 缓存（底层用 Qt 全局 ``QPixmapCache``）。控件只需在 ``paintEvent``
  里 ``drawPixmap`` 这张现成贴图，零模糊开销、可被 GPU 直接合成。
* :func:`vertical_gradient` / :func:`linear_gradient` —— 缓存常用 ``QLinearGradient``
  对象，避免每帧重新构造（构造本身廉价，但缓存可避免重复分配 + 统一管理）。

所有缓存都以「不可变参数元组」为 key，命中即直接返回，未命中才渲染一次。
"""
from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPixmap,
    QPixmapCache,
)
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
)

# 提高 Qt 全局 pixmap 缓存上限（默认约 10MB），容纳预渲染阴影 / 渐变贴图。
QPixmapCache.setCacheLimit(40 * 1024)  # KB → 40MB


# ════════════════════════════════════════════════════════════════════
#  阴影预渲染（Shadow Cache）
# ════════════════════════════════════════════════════════════════════
def _bake_shadow(width: int, height: int, radius: int, blur: int,
                 col: QColor, dy: int) -> QPixmap:
    """用 Qt 原生（C++）高斯模糊把「圆角矩形投影」烘焙成一张贴图（仅执行一次）。

    做法：把一块不透明圆角矩形（caster）放进离屏 ``QGraphicsScene`` 并挂一个
    ``QGraphicsDropShadowEffect``，整体渲染到目标 ``QPixmap``；随后用
    ``CompositionMode_Clear`` 抠掉 caster 自身的不透明区域，只留下四周的模糊
    投影光晕。之后控件在 ``paintEvent`` 里 ``drawPixmap`` 这张静态贴图即可，
    运行期**零模糊开销**。
    """
    pad = blur + abs(dy) + 2
    total_w = max(1, width + pad * 2)
    total_h = max(1, height + pad * 2)

    # 1) 投影源：一块实心圆角矩形（DropShadow 只取其 alpha 形状）
    caster = QPixmap(width, height)
    caster.fill(Qt.GlobalColor.transparent)
    cp = QPainter(caster)
    cp.setRenderHint(QPainter.RenderHint.Antialiasing)
    cp.setPen(Qt.PenStyle.NoPen)
    cp.setBrush(QColor(0, 0, 0, 255))
    cp.drawRoundedRect(0, 0, width, height, radius, radius)
    cp.end()

    # 2) 离屏场景 + 原生 DropShadow，渲染到包含 blur 边距的目标贴图
    scene = QGraphicsScene()
    item = QGraphicsPixmapItem(caster)
    item.setPos(pad, pad)
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(col)
    item.setGraphicsEffect(eff)
    scene.addItem(item)
    scene.setSceneRect(0, 0, total_w, total_h)

    out = QPixmap(total_w, total_h)
    out.fill(Qt.GlobalColor.transparent)
    op = QPainter(out)
    op.setRenderHint(QPainter.RenderHint.Antialiasing)
    scene.render(op)

    # 3) 抠掉 caster 自身（只保留四周投影光晕）—— 否则不透明黑块会透过半透明卡片
    op.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    op.setPen(Qt.PenStyle.NoPen)
    op.setBrush(QColor(0, 0, 0, 255))
    op.drawRoundedRect(pad, pad, width, height, radius, radius)
    op.end()

    return out


def drop_shadow_pixmap(
    width: int,
    height: int,
    *,
    radius: int = 20,
    blur: int = 28,
    color: QColor | str = QColor(0, 0, 0, 110),
    dy: int = 6,
) -> QPixmap:
    """返回一张「圆角矩形投影」预渲染贴图（带缓存）。

    贴图尺寸 = 内容尺寸 + 四周 ``blur`` 边距；把它居中绘制在内容矩形后方
    （向下偏移 ``dy``）即得到与实时 DropShadow 几乎一致的投影，但**零模糊开销**。

    参数全部参与缓存 key，命中即直接返回同一对象。
    """
    col = QColor(color)
    key = (
        "wc_shadow",
        int(width), int(height), int(radius), int(blur),
        col.rgba(), int(dy),
    )
    cache_key = "|".join(str(k) for k in key)
    cached = QPixmapCache.find(cache_key)
    if cached is not None and not cached.isNull():
        return cached

    pix = _bake_shadow(int(width), int(height), int(radius), int(blur), col, int(dy))
    QPixmapCache.insert(cache_key, pix)
    return pix


def shadow_margins(blur: int, dy: int = 6) -> tuple[int, int, int, int]:
    """与 :func:`drop_shadow_pixmap` 配套：返回 (left, top, right, bottom) 外扩边距。

    与 :func:`_bake_shadow` 内部 ``pad`` 保持一致：四周均为 ``blur + |dy| + 2``。
    """
    pad = blur + abs(dy) + 2
    return pad, pad, pad, pad


# ════════════════════════════════════════════════════════════════════
#  渐变缓存（Gradient Cache）
# ════════════════════════════════════════════════════════════════════
_GRADIENT_CACHE: dict[tuple, QLinearGradient] = {}


def vertical_gradient(height: float, stops: tuple[tuple[float, str], ...]) -> QLinearGradient:
    """缓存一个「竖直方向」线性渐变（0→height）。

    ``stops`` 为 ((pos, color_hex), ...)，全部参与 key。
    """
    key = ("v", round(float(height), 1)) + stops
    g = _GRADIENT_CACHE.get(key)
    if g is None:
        g = QLinearGradient(0.0, 0.0, 0.0, float(height))
        for pos, col in stops:
            g.setColorAt(float(pos), QColor(col))
        _GRADIENT_CACHE[key] = g
    return g


def linear_gradient(
    p0: tuple[float, float],
    p1: tuple[float, float],
    stops: tuple[tuple[float, str], ...],
) -> QLinearGradient:
    """缓存任意方向线性渐变。"""
    key = ("l", round(p0[0], 1), round(p0[1], 1), round(p1[0], 1), round(p1[1], 1)) + stops
    g = _GRADIENT_CACHE.get(key)
    if g is None:
        g = QLinearGradient(QPointF(*p0), QPointF(*p1))
        for pos, col in stops:
            g.setColorAt(float(pos), QColor(col))
        _GRADIENT_CACHE[key] = g
    return g


def clear_caches() -> None:
    """清空所有缓存（主题切换时调用，避免旧主题渐变 / 阴影残留）。"""
    _GRADIENT_CACHE.clear()
    QPixmapCache.clear()
