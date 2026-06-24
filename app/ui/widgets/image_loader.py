"""异步远程图片控件：传 URL 进来，自动加载并显示，支持圆角/圆形裁剪。"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPixmap, QPixmapCache
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget

from app.services.image_service import ImageService


class RemoteImage(QLabel):
    """从远程 URL 加载并缓存图片的 QLabel（固定尺寸）。

    形态：``rect`` / ``round`` / ``circle``
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        size: int = 48,
        shape: str = "round",
        radius: int = 12,
        placeholder_color: str = "#1d2030",
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(size, size))
        self._size = size
        self._shape = shape
        self._radius = radius
        self._placeholder_color = QColor(placeholder_color)
        self._url: str | None = None
        self._pixmap: QPixmap | None = None
        self._scaled: QPixmap | None = None
        self._service = ImageService.instance()
        self._listening = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    # ─── public API ───
    def set_url(self, url: str | None) -> None:
        self._url = url
        self._scaled = None
        if not url:
            self._pixmap = None
            self._stop_listening()
            self.update()
            return
        cached = self._service.request(url)
        self._pixmap = cached
        if cached is not None and not cached.isNull():
            self._stop_listening()
        else:
            self._start_listening()
        self.update()

    def set_pixmap(self, pm: QPixmap | None) -> None:
        self._pixmap = pm
        self._scaled = None
        self._stop_listening()
        self.update()

    # ─── internals ───
    def _start_listening(self) -> None:
        if not self._listening:
            self._service.image_ready.connect(self._on_ready)
            self._listening = True

    def _stop_listening(self) -> None:
        if self._listening:
            try:
                self._service.image_ready.disconnect(self._on_ready)
            except (TypeError, RuntimeError):
                pass
            self._listening = False

    def _on_ready(self, url: str, pm: QPixmap) -> None:
        if url == self._url:
            self._pixmap = pm
            self._scaled = None
            self._stop_listening()
            self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        rectf = QRectF(rect)
        path = QPainterPath()
        if self._shape == "circle":
            path.addEllipse(rectf)
        elif self._shape == "round":
            path.addRoundedRect(rectf, float(self._radius), float(self._radius))
        else:
            path.addRect(rectf)

        # 背景占位
        p.setClipPath(path)
        p.fillRect(rect, QBrush(self._placeholder_color))

        if self._pixmap and not self._pixmap.isNull():
            if self._scaled is None:
                # 共享缩放缓存（QPixmapCache）：同一 URL + 同一尺寸的队徽 / 头像
                # 在所有行 / 卡片间复用一张缩放结果（性能需求 25.2 / 26.1）。
                key = f"wcimg:{self._url}:{self._size}" if self._url else None
                cached = QPixmapCache.find(key) if key else None
                if cached is not None and not cached.isNull():
                    self._scaled = cached
                else:
                    self._scaled = self._pixmap.scaled(
                        self._size,
                        self._size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    if key:
                        QPixmapCache.insert(key, self._scaled)
            scaled = self._scaled
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            p.drawPixmap(x, y, scaled)
        else:
            p.setPen(QPen(QColor(255, 255, 255, 60)))
            font = p.font()
            font.setPointSize(max(8, int(self._size * 0.32)))
            font.setBold(True)
            p.setFont(font)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "•")


class RemoteCover(QWidget):
    """**自适应宽高** 的远程封面（如球场/球员 hero）。

    使用 ``KeepAspectRatioByExpanding`` 把图片裁剪到当前控件大小，
    并在顶部叠加可配置的多段渐变遮罩（dim/colorize/vignette）。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        radius: int = 18,
        accent: str = "#00BFFF",
        overlay_top: float = 0.25,
        overlay_bottom: float = 0.75,
        placeholder_color: str = "#181B27",
        anchor: str = "center",
    ) -> None:
        super().__init__(parent)
        self._radius = radius
        self._anchor = anchor
        self._accent = QColor(accent)
        self._top = overlay_top
        self._bottom = overlay_bottom
        self._placeholder = QColor(placeholder_color)
        self._url: str | None = None
        self._pixmap: QPixmap | None = None
        self._service = ImageService.instance()
        self._listening = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_url(self, url: str | None) -> None:
        self._url = url
        if not url:
            self._pixmap = None
            self._stop_listening()
            self.update()
            return
        self._pixmap = self._service.request(url)
        if self._pixmap is not None and not self._pixmap.isNull():
            self._stop_listening()
        else:
            self._start_listening()
        self.update()

    def set_accent(self, color: str) -> None:
        self._accent = QColor(color)
        self.update()

    def _start_listening(self) -> None:
        if not self._listening:
            self._service.image_ready.connect(self._on_ready)
            self._listening = True

    def _stop_listening(self) -> None:
        if self._listening:
            try:
                self._service.image_ready.disconnect(self._on_ready)
            except (TypeError, RuntimeError):
                pass
            self._listening = False

    def _on_ready(self, url: str, pm: QPixmap) -> None:
        if url == self._url:
            self._pixmap = pm
            self._stop_listening()
            self.update()

    def paintEvent(self, _ev) -> None:
        from PyQt6.QtGui import QLinearGradient

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, float(self._radius), float(self._radius))
        p.setClipPath(path)

        # 占位底
        p.fillRect(rect, self._placeholder)

        # 图片 —— 中心裁剪铺满
        if self._pixmap and not self._pixmap.isNull():
            if self._anchor == "right":
                # 球员靠右悬浮：按高度等比缩放（略微出血），贴右下角
                target_h = int(rect.height() * 1.06)
                scaled = self._pixmap.scaledToHeight(
                    target_h, Qt.TransformationMode.SmoothTransformation
                )
                # 限制过宽
                max_w = int(rect.width() * 0.62)
                if scaled.width() > max_w:
                    scaled = self._pixmap.scaledToWidth(
                        max_w, Qt.TransformationMode.SmoothTransformation
                    )
                x = int(self.width() - scaled.width() - rect.width() * 0.04)
                y = int(self.height() - scaled.height() + rect.height() * 0.02)
                p.drawPixmap(x, y, scaled)
            else:
                scaled = self._pixmap.scaled(
                    int(rect.width()), int(rect.height()),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = (self.width() - scaled.width()) // 2
                y = (self.height() - scaled.height()) // 2
                p.drawPixmap(x, y, scaled)
        else:
            # 无图：画 accent 渐变背景占位
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            ac = self._accent
            grad.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 110))
            grad.setColorAt(1.0, self._placeholder)
            p.fillRect(rect, grad)

        # 顶部 dim 遮罩（让叠加文字更清晰）
        if self._top > 0:
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, QColor(0, 0, 0, int(255 * self._top)))
            grad.setColorAt(0.5, QColor(0, 0, 0, 0))
            p.fillRect(rect, grad)

        # 底部 dim 遮罩
        if self._bottom > 0:
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.55, QColor(0, 0, 0, 0))
            grad.setColorAt(1.0, QColor(0, 0, 0, int(255 * self._bottom)))
            p.fillRect(rect, grad)

        # accent 暖光（左下）
        ac = self._accent
        grad = QLinearGradient(rect.bottomLeft(), rect.topRight())
        grad.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 120))
        grad.setColorAt(0.65, QColor(ac.red(), ac.green(), ac.blue(), 0))
        p.fillRect(rect, grad)
