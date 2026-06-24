"""真实国旗图标控件。

用国旗位图取代 emoji 国旗 —— emoji 国旗在 Windows / 部分 Linux 系统上
无法完整渲染（区域指示符组合字符常显示为两个字母，英格兰/苏格兰/威
尔士的「子区旗帜」更是几乎全平台失效），这正是「国旗显示不全」的根因。

设计修订（v5）—— 真·统一大小 + 高性能
-----------------------------------------
v4 改成「固定外框 + letterbox 居中」后，外框大小确实统一了，但**旗面
本身**仍按各国真实比例缩放居中：瑞士（接近正方形）、卡塔尔（超宽）等
旗面在框里一会儿窄一会儿宽，视觉上仍「参差不齐」。

本版做两件事：

1. **真·统一大小**：旗面用 ``KeepAspectRatioByExpanding`` 缩放后**填满**
   固定的 3:2 外框（多出的极小边缘裁掉）。于是相同 ``height`` 下，所有
   国旗呈现为**完全一致**的实心矩形，不再有大小/留白差异。
2. **高性能**（解决「打开多了特别卡」）：
   * 缩放结果缓存为 ``_scaled``，仅在位图或尺寸变化时重算，不再每帧重缩放。
   * **不**在构造时就订阅全局 ``image_ready`` 信号；仅当图片尚未就绪时
     才临时订阅，拿到后立即断开。配合本地打包的国旗（``assets/flags``），
     绝大多数 ``FlagIcon`` 都能**同步命中**、根本不触发信号，避免了
     「N 个国旗 × 每张图片加载都广播一次」的 O(N²) 开销。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap, QPixmapCache
from PyQt6.QtWidgets import QWidget

from app.services.image_service import ImageService
from app.services.player_profiles import flag_image_url


class FlagIcon(QWidget):
    """一面国旗（固定外框、填满外框、所有国旗大小完全一致）。

    Parameters
    ----------
    nationality : str | None
        国家中文名（如「德国」「英格兰」）。
    height : int
        旗帜外框高度（像素）；宽度固定为 ``height * 3 / 2``，**与国别无关**，
        保证所有国旗大小统一。
    radius : int
        圆角半径，默认 0（直角，不要圆角）。
    """

    #: 统一外框宽高比（标准 3:2 旗帜比例）
    ASPECT = 3 / 2

    def __init__(
        self,
        nationality: str | None = None,
        parent: QWidget | None = None,
        *,
        height: int = 26,
        radius: int = 0,
    ) -> None:
        super().__init__(parent)
        self._h = height
        self._w = max(1, round(height * self.ASPECT))
        self._radius = radius
        self._pixmap: QPixmap | None = None
        self._scaled: QPixmap | None = None
        self._url: str | None = None
        self._service = ImageService.instance()
        self._listening = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # 固定外框尺寸 —— 一次设定后不再随国旗位图变化（统一大小）
        self.setFixedSize(QSize(self._w, self._h))
        self.set_nationality(nationality)

    # ── public ──
    def set_nationality(self, nationality: str | None) -> None:
        # 本地打包优先；本地缺失才回退在线（请求更高分辨率以保证清晰度）
        self._url = flag_image_url(nationality, height=max(120, self._h * 4))
        self._scaled = None
        if not self._url:
            self._pixmap = None
            self._stop_listening()
            self.update()
            return
        # 同步命中（本地文件 / 已缓存）—— 无需订阅信号
        pm = self._service.request(self._url)
        if pm is not None and not pm.isNull():
            self._pixmap = pm
            self._stop_listening()
        else:
            # 仍在下载：临时订阅一次，拿到即断开
            self._pixmap = None
            self._start_listening()
        self.update()

    # ── internals ──
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

    def _build_scaled(self) -> None:
        if not (self._pixmap and not self._pixmap.isNull()):
            self._scaled = None
            return
        # 共享缩放缓存（QPixmapCache）：同一国别 + 同一尺寸的旗面在所有卡片 / 行
        # 之间复用同一张缩放结果，避免每个 FlagIcon 各自重复 SmoothTransformation
        # 缩放（概览页国旗数量大，省去大量重复栅格化 —— 性能需求 25.2 / 26.1）。
        key = f"wcflag:{self._url}:{self._w}x{self._h}"
        cached = QPixmapCache.find(key)
        if cached is not None and not cached.isNull():
            self._scaled = cached
            return
        # 真·统一：填满外框（ByExpanding），多出的极小边缘由裁剪去掉
        scaled = self._pixmap.scaled(
            self._w, self._h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._scaled = scaled
        if self._url:
            QPixmapCache.insert(key, scaled)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rectf = QRectF(0.5, 0.5, self._w - 1, self._h - 1)
        path = QPainterPath()
        if self._radius > 0:
            path.addRoundedRect(rectf, float(self._radius), float(self._radius))
        else:
            path.addRect(rectf)

        p.setClipPath(path)
        # 外框底色（图未就绪时的占位） —— 极淡，避免空白方块感
        p.fillPath(path, QColor(255, 255, 255, 18))

        if self._scaled is None:
            self._build_scaled()
        if self._scaled is not None and not self._scaled.isNull():
            # 填满外框后居中（多余部分被裁剪），所有国旗大小完全一致
            x = (self._w - self._scaled.width()) // 2
            y = (self._h - self._scaled.height()) // 2
            p.drawPixmap(x, y, self._scaled)
        p.setClipping(False)

        # 细描边，提升与背景的分离度
        p.setPen(QPen(QColor(0, 0, 0, 90), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
