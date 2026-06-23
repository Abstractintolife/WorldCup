"""左侧导航栏 —— 对照 2026 FIFA WC 目标稿打造。

设计要点
---------
* 顶部「品牌行」：圆形大力神杯 logo + 中文主标题 + 英文副标题。
* 中部导航行：使用 ``NavRow`` 自绘控件 —— 图标 + 文案 + 选中态右侧
  红色发光指示条（呼应目标稿的「红色高亮条」）。
* 底部宣传卡：FIFA WORLD CUP 2026 赛事 logo + slogan，鼠标悬停时
  会有微微上浮 + 边框点亮的动效。
"""
from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_TITLE_ZH, SIDEBAR_WIDTH


# 默认调色（与 theme.DARK 同步；自绘控件不走 QSS）
ACCENT = QColor("#00BFFF")
ACCENT_LIGHT = QColor("#46D2FF")
TEXT = QColor("#FFFFFF")
TEXT_DIM = QColor("#B0BEC5")
TEXT_FAINT = QColor("#6B7689")


def apply_palette(palette) -> None:
    """根据当前皮肤更新侧栏自绘控件的强调色（NavRow / 品牌色）。

    NavRow 等自绘控件不走 QSS，颜色取自这些模块级 QColor。切换皮肤时
    调用本函数即可让选中高亮、图标色随皮肤联动。
    """
    global ACCENT, ACCENT_LIGHT, TEXT, TEXT_DIM, TEXT_FAINT
    ACCENT = QColor(palette.primary)
    ACCENT_LIGHT = QColor(palette.primary_hover)
    TEXT = QColor(palette.text)
    TEXT_DIM = QColor(palette.text_dim)
    TEXT_FAINT = QColor(palette.text_faint)


# ─────────────────────────────────────────────
class NavRow(QWidget):
    """单个导航行（自绘）。

    展示图标 + 文案。选中时背景出现红色弱光 + 左侧 3px 红色发光条 +
    文字加粗。鼠标悬停时背景变亮。
    """

    clicked = pyqtSignal(str)

    def __init__(self, key: str, icon: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._icon = icon
        self._label = label
        self._active = False
        self._hover = False
        self._t = 0.0  # 选中过渡进度（0..1）
        self.setFixedHeight(46)
        self.setMinimumWidth(SIDEBAR_WIDTH - 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._anim = QPropertyAnimation(self, b"_progress", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # 动画属性 —— 用 setProperty 驱动重绘
    def get_progress(self) -> float:  # noqa: D401
        return self._t

    def set_progress(self, v: float) -> None:
        self._t = float(v)
        self.update()

    from PyQt6.QtCore import pyqtProperty
    _progress = pyqtProperty(float, fget=get_progress, fset=set_progress)

    def set_active(self, active: bool) -> None:
        if active == self._active:
            return
        self._active = active
        self._anim.stop()
        self._anim.setStartValue(self._t)
        self._anim.setEndValue(1.0 if active else 0.0)
        self._anim.start()

    def enterEvent(self, _ev) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, _ev) -> None:
        self._hover = False
        self.update()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._key)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Hover 时整行视觉上向右平移 5px（active 状态保持原位 —— 已经有左侧高亮条）
        hover_offset = 5.0 if (self._hover and not self._active) else 0.0
        rect = QRectF(self.rect()).adjusted(14.0 + hover_offset, 2.0,
                                            -14.0 + hover_offset, -2.0)

        # 背景
        path = QPainterPath()
        path.addRoundedRect(rect, 12.0, 12.0)
        if self._active or self._t > 0.01:
            # 选中态：90deg 皮肤主色渐变（accent → transparent）
            grad = QLinearGradient(rect.topLeft(), rect.topRight())
            base = QColor(ACCENT)
            grad.setColorAt(0.0, QColor(base.red(), base.green(), base.blue(), int(90 * self._t)))
            grad.setColorAt(1.0, QColor(base.red(), base.green(), base.blue(), 0))
            p.fillPath(path, QBrush(grad))
        if self._hover and self._t < 0.5:
            p.fillPath(path, QColor(255, 255, 255, 14))

        # 左侧选中条 —— 3px 高亮发光竖条（皮肤主色）
        if self._t > 0.0:
            bar = QRectF(rect.left() + 4, rect.center().y() - 9, 3, 18)
            bar_path = QPainterPath()
            bar_path.addRoundedRect(bar, 1.6, 1.6)
            gc = QColor(ACCENT)
            glow = QColor(gc.red(), gc.green(), gc.blue(), int(255 * self._t))
            p.fillPath(bar_path, glow)

        # 图标 emoji
        f_icon = QFont(self.font())
        f_icon.setPointSize(15)
        p.setFont(f_icon)
        p.setPen(ACCENT_LIGHT if self._active else TEXT_DIM)
        icon_rect = QRectF(rect.left() + 14, rect.top(), 26, rect.height())
        p.drawText(icon_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                   self._icon)

        # 文案
        f_lbl = QFont(self.font())
        f_lbl.setPointSize(11)
        f_lbl.setBold(self._active)
        p.setFont(f_lbl)
        p.setPen(TEXT if (self._active or self._hover) else TEXT_DIM)
        text_rect = QRectF(rect.left() + 44, rect.top(),
                           rect.width() - 50, rect.height())
        p.drawText(text_rect,
                   int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                   self._label)


class _LogoOrb(QWidget):
    """侧栏顶部的「大力神杯」金色玻璃球 logo（自绘）。"""

    def __init__(self, size: int = 38, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        cx, cy = r.center().x(), r.center().y()

        # 外圈光晕
        glow = QRadialGradient(QPointF(cx, cy), self.width() * 0.7)
        glow.setColorAt(0.4, QColor(0, 191, 255, 220))
        glow.setColorAt(1.0, QColor(0, 191, 255, 0))
        p.setBrush(glow)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(r)

        # 主球（蓝紫渐变）
        inner = r.adjusted(3, 3, -3, -3)
        ball = QLinearGradient(QPointF(inner.topLeft()), QPointF(inner.bottomRight()))
        ball.setColorAt(0.0, QColor("#46D2FF"))
        ball.setColorAt(1.0, QColor("#3E2F8C"))
        p.setBrush(ball)
        p.drawEllipse(inner)

        # 高光
        spec = QRadialGradient(
            QPointF(cx - self.width() * 0.18, cy - self.height() * 0.22),
            self.width() * 0.45,
        )
        spec.setColorAt(0.0, QColor(255, 255, 255, 160))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.drawEllipse(inner)

        # 中央杯型符号 ⚽
        f = QFont(self.font())
        f.setPointSize(int(self.width() * 0.45))
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), "⚽")


class _PromoCard(QFrame):
    """侧栏底部的赛事宣传卡（鼠标悬停轻微上移）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PromoCard")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setFixedHeight(74)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        self._orb = _LogoOrb(size=44)
        layout.addWidget(self._orb)
        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel("FIFA WORLD CUP 2026")
        title.setStyleSheet(
            "color:#FFD700; font-size:10.5px; font-weight:900; letter-spacing:1.4px;"
        )
        col.addWidget(title)
        slogan = QLabel("激情 · 荣耀 · 梦想")
        slogan.setStyleSheet("color:#B0BEC5; font-size:11px; font-weight:600;")
        col.addWidget(slogan)
        layout.addLayout(col)
        layout.addStretch(1)

        # 阴影 + 主题边框
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(28)
        eff.setOffset(0, 6)
        eff.setColor(QColor(0, 191, 255, 80))
        self.setGraphicsEffect(eff)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 14.0, 14.0)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor(0, 191, 255, 40))
        grad.setColorAt(1.0, QColor(106, 90, 205, 24))
        p.fillPath(path, grad)
        p.setPen(QPen(QColor(0, 191, 255, 90), 1.0))
        p.drawPath(path)


class NavSidebar(QFrame):
    """侧边导航。每个 item = (key, icon-emoji, label)。"""

    selected = pyqtSignal(str)

    def __init__(self, items: Iterable[tuple[str, str, str]]) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 22, 0, 16)
        layout.setSpacing(2)

        # ── 品牌区 ──────────────────────────
        brand = QHBoxLayout()
        brand.setContentsMargins(20, 0, 20, 16)
        brand.setSpacing(10)
        brand.addWidget(_LogoOrb(size=36))
        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel(APP_TITLE_ZH)
        title.setStyleSheet(
            "color:#ffffff; font-size:14.5px; font-weight:900; letter-spacing:0.5px;"
        )
        col.addWidget(title)
        sub = QLabel("FIFA WORLD CUP 2026")
        sub.setStyleSheet(
            "color:#FFD700; font-size:9.5px; font-weight:800; letter-spacing:1.6px;"
        )
        col.addWidget(sub)
        brand.addLayout(col)
        brand.addStretch(1)
        brand_w = QWidget()
        brand_w.setLayout(brand)
        layout.addWidget(brand_w)

        # 分隔细线
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.06);")
        sep_wrap_lay = QVBoxLayout()
        sep_wrap_lay.setContentsMargins(20, 0, 20, 12)
        sep_wrap_lay.addWidget(sep)
        sep_wrap = QWidget(); sep_wrap.setLayout(sep_wrap_lay)
        layout.addWidget(sep_wrap)

        # ── 导航行 ──────────────────────────
        self._rows: dict[str, NavRow] = {}
        for key, emoji, label in items:
            row = NavRow(key, emoji, label)
            row.clicked.connect(self.set_active)
            layout.addWidget(row)
            self._rows[key] = row

        layout.addStretch(1)

        # ── 底部 promo 卡 ────────────────────
        promo_lay = QVBoxLayout()
        promo_lay.setContentsMargins(14, 8, 14, 0)
        promo_lay.addWidget(_PromoCard())
        promo_w = QWidget(); promo_w.setLayout(promo_lay)
        layout.addWidget(promo_w)

        footer = QLabel("数据来源 · 懂球帝公开接口")
        footer.setStyleSheet(
            "color:#525c7a; font-size:9.5px; padding: 10px 22px 0 22px;"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(footer)

    def set_active(self, key: str) -> None:
        for k, row in self._rows.items():
            row.set_active(k == key)
        self.selected.emit(key)

    def apply_palette(self, palette) -> None:
        """皮肤切换：刷新自绘导航行的强调色。"""
        apply_palette(palette)
        for row in self._rows.values():
            row.update()
        self.update()
