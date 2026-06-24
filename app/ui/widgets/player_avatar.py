"""球员头像 —— 渐变光环 + 径向底光的电影感头像框。

在普通远程圆形头像的基础上，叠加：
* **径向渐变底光**：头像背后一圈柔和的品牌色辉光，弱化「证件照」生硬感。
* **双层渐变描边环**：外环品牌渐变 + 内侧细高光，呼应 FC25 球星卡风格。

仍复用 ``RemoteImage`` 的异步加载 / 缓存逻辑，仅重写绘制：照片绘制在
留出环宽的内圈，环与底光画在外圈余量里。API 与旧版保持一致
（``PlayerAvatar(url, parent, size=...)`` + ``set_url``）。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QConicalGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmapCache,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget

from app.ui.widgets.image_loader import RemoteImage


class PlayerAvatar(RemoteImage):
    """带渐变光环与底光的圆形球员头像。"""

    def __init__(
        self,
        url: str | None = None,
        parent: QWidget | None = None,
        *,
        size: int = 56,
        ring: bool = True,
        ring_from: str = "#00BFFF",
        ring_to: str = "#FFD700",
    ) -> None:
        super().__init__(parent, size=size, shape="circle")
        self._ring = ring
        # 环宽随尺寸自适应（小头像窄环、大头像宽环）
        self._ring_w = max(2.0, round(size * 0.045))
        self._ring_from = QColor(ring_from)
        self._ring_to = QColor(ring_to)
        self.set_url(url)

    def set_ring_colors(self, ring_from: str, ring_to: str) -> None:
        self._ring_from = QColor(ring_from)
        self._ring_to = QColor(ring_to)
        self.update()

    def paintEvent(self, _ev) -> None:  # noqa: D401
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        full = QRectF(self.rect())
        cx, cy = full.center().x(), full.center().y()

        if not self._ring:
            # 无环：退回基础圆形绘制
            super().paintEvent(_ev)
            return

        gap = 2.0                       # 环与照片之间的留白
        ring_w = self._ring_w
        inset = ring_w + gap            # 照片相对外框的内缩量

        # ① 径向底光（照片背后柔和辉光）
        glow = QRadialGradient(cx, cy, full.width() / 2)
        c0 = QColor(self._ring_from); c0.setAlpha(120)
        c1 = QColor(self._ring_from); c1.setAlpha(0)
        glow.setColorAt(0.55, c0)
        glow.setColorAt(1.0, c1)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(full)

        # ② 照片（内圈圆形裁剪）
        photo_rect = full.adjusted(inset, inset, -inset, -inset)
        path = QPainterPath()
        path.addEllipse(photo_rect)
        p.save()
        p.setClipPath(path)
        # 占位底
        p.fillRect(photo_rect, QColor(self._placeholder_color))
        pix = self._pixmap
        if pix is not None and not pix.isNull():
            # 共享缩放缓存（QPixmapCache）：同一 URL + 同一照片尺寸的头像在所有
            # 行 / 卡片间复用一张缩放结果，避免每次 paintEvent 重复
            # SmoothTransformation 缩放（射手榜 / 排行榜头像数量大 —— 性能需求
            # 25.2 / 26.1）。
            pw, ph = int(photo_rect.width()), int(photo_rect.height())
            scaled = self._scaled
            if scaled is None or scaled.isNull():
                key = (
                    f"wcavatar:{self._url}:{pw}x{ph}" if self._url else None
                )
                cached = QPixmapCache.find(key) if key else None
                if cached is not None and not cached.isNull():
                    scaled = cached
                else:
                    scaled = pix.scaled(
                        pw, ph,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    if key:
                        QPixmapCache.insert(key, scaled)
                self._scaled = scaled
            x = photo_rect.left() + (photo_rect.width() - scaled.width()) / 2
            y = photo_rect.top() + (photo_rect.height() - scaled.height()) / 2
            p.drawPixmap(int(x), int(y), scaled)
        else:
            p.setPen(QPen(QColor(255, 255, 255, 70)))
            f = p.font(); f.setBold(True)
            f.setPointSize(max(8, int(photo_rect.width() * 0.32)))
            p.setFont(f)
            p.drawText(photo_rect, Qt.AlignmentFlag.AlignCenter, "•")
        p.restore()

        # ③ 渐变描边环（圆锥渐变 → 旋转一圈的金属光泽）
        ring_rect = full.adjusted(ring_w / 2, ring_w / 2, -ring_w / 2, -ring_w / 2)
        cone = QConicalGradient(cx, cy, 90)
        cone.setColorAt(0.0, self._ring_from)
        cone.setColorAt(0.5, self._ring_to)
        cone.setColorAt(1.0, self._ring_from)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(cone, ring_w))
        p.drawEllipse(ring_rect)

        # ④ 内侧细高光线
        hi_rect = full.adjusted(inset - 0.5, inset - 0.5, -(inset - 0.5), -(inset - 0.5))
        p.setPen(QPen(QColor(255, 255, 255, 55), 1.0))
        p.drawEllipse(hi_rect)
