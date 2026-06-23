"""左侧导航栏 —— 对照 2026 FIFA WC「想象中的样子」设计稿精准打造。

布局（自上而下）
-----------------
1. 品牌区：金色大力神杯 logo + 「世界杯 2026」主标题 + 「FIFA WORLD CUP」副标题。
2. 菜单：概览 / 实时比赛（红色 LIVE 徽章）/ 赛程中心 / 赛事日历 / 球队 /
   球员 / 数据分析 / 预测中心 / 新闻资讯 / 收藏夹 / 设置。
   —— 用自绘 ``NavRow`` 控件：图标 + 文案 + 选中态左侧发光竖条。
3. 倒计时卡：炫彩渐变卡，「距 FIFA 世界杯开幕 / 365 天」+ 开幕日期
   2026.06.11 + 举办地（美国 · 加拿大 · 墨西哥）。
4. 用户栏：圆形头像 + 昵称「WorldCup Fan」+ 等级「Lv.12」。
"""
from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
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
    QVBoxLayout,
    QWidget,
)

from app.config import SIDEBAR_WIDTH


# 默认调色（与 theme.DARK 同步；自绘控件不走 QSS）
ACCENT = QColor("#00BFFF")
ACCENT_LIGHT = QColor("#46D2FF")
GOLD = QColor("#FFD700")
LIVE = QColor("#FF3057")
TEXT = QColor("#FFFFFF")
TEXT_DIM = QColor("#B0BEC5")
TEXT_FAINT = QColor("#6B7689")


def apply_palette(palette) -> None:
    """根据当前皮肤更新侧栏自绘控件的强调色。"""
    global ACCENT, ACCENT_LIGHT, GOLD, LIVE, TEXT, TEXT_DIM, TEXT_FAINT
    ACCENT = QColor(palette.primary)
    ACCENT_LIGHT = QColor(palette.primary_hover)
    GOLD = QColor(palette.accent)
    LIVE = QColor(palette.live)
    TEXT = QColor(palette.text)
    TEXT_DIM = QColor(palette.text_dim)
    TEXT_FAINT = QColor(palette.text_faint)


# ─────────────────────────────────────────────
class NavRow(QWidget):
    """单个导航行（自绘）：图标 + 文案 + 选中态左侧发光竖条 + 可选 LIVE 徽章。"""

    clicked = pyqtSignal(str)

    def __init__(
        self,
        key: str,
        icon: str,
        label: str,
        badge: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._key = key
        self._icon = icon
        self._label = label
        self._badge = badge          # 例如 "LIVE"
        self._active = False
        self._hover = False
        self._t = 0.0
        self._blink = 0.0            # LIVE 徽章呼吸（0..1）
        self.setFixedHeight(42)
        self.setMinimumWidth(SIDEBAR_WIDTH - 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._anim = QPropertyAnimation(self, b"_progress", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # LIVE 徽章呼吸动画（订阅全局帧时钟，避免每行各起一个 QTimer）
        self._clock = None
        if self._badge:
            from app.ui.design.frame_clock import FrameClock
            self._clock = FrameClock.instance()

    # 选中过渡属性
    def get_progress(self) -> float:
        return self._t

    def set_progress(self, v: float) -> None:
        self._t = float(v)
        self.update()

    _progress = pyqtProperty(float, fget=get_progress, fset=set_progress)

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if self._clock is not None:
            self._clock.subscribe(self._on_frame)

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._clock is not None:
            try:
                self._clock.unsubscribe(self._on_frame)
            except Exception:
                pass

    def _on_frame(self, t: float, _dt: float) -> None:
        import math
        self._blink = (1.0 - math.cos(t * 2.6)) * 0.5
        self.update()

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
        hover_offset = 4.0 if (self._hover and not self._active) else 0.0
        rect = QRectF(self.rect()).adjusted(12.0 + hover_offset, 1.0,
                                            -12.0 + hover_offset, -1.0)

        path = QPainterPath()
        path.addRoundedRect(rect, 11.0, 11.0)
        if self._active or self._t > 0.01:
            grad = QLinearGradient(rect.topLeft(), rect.topRight())
            base = QColor(ACCENT)
            grad.setColorAt(0.0, QColor(base.red(), base.green(), base.blue(), int(95 * self._t)))
            grad.setColorAt(1.0, QColor(base.red(), base.green(), base.blue(), 0))
            p.fillPath(path, QBrush(grad))
        if self._hover and self._t < 0.5:
            p.fillPath(path, QColor(255, 255, 255, 14))

        # 左侧选中条
        if self._t > 0.0:
            bar = QRectF(rect.left() + 3, rect.center().y() - 8, 3, 16)
            bp = QPainterPath()
            bp.addRoundedRect(bar, 1.6, 1.6)
            gc = QColor(ACCENT)
            p.fillPath(bp, QColor(gc.red(), gc.green(), gc.blue(), int(255 * self._t)))

        # 图标
        f_icon = QFont(self.font())
        f_icon.setPointSize(13)
        p.setFont(f_icon)
        p.setPen(ACCENT_LIGHT if self._active else TEXT_DIM)
        icon_rect = QRectF(rect.left() + 12, rect.top(), 24, rect.height())
        p.drawText(icon_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                   self._icon)

        # 文案
        f_lbl = QFont(self.font())
        f_lbl.setPointSize(11)
        f_lbl.setBold(self._active)
        p.setFont(f_lbl)
        p.setPen(TEXT if (self._active or self._hover) else TEXT_DIM)
        text_rect = QRectF(rect.left() + 42, rect.top(),
                           rect.width() - 90, rect.height())
        p.drawText(text_rect,
                   int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                   self._label)

        # LIVE 徽章（右侧红色呼吸胶囊）
        if self._badge:
            f_b = QFont(self.font())
            f_b.setPointSize(8)
            f_b.setBold(True)
            p.setFont(f_b)
            bw = 40.0
            bh = 17.0
            bx = rect.right() - bw - 2
            by = rect.center().y() - bh / 2
            brect = QRectF(bx, by, bw, bh)
            bpath = QPainterPath()
            bpath.addRoundedRect(brect, bh / 2, bh / 2)
            lc = QColor(LIVE)
            lc.setAlpha(int(180 + 75 * self._blink))
            # 外发光
            glow = QRadialGradient(brect.center(), bw)
            glow.setColorAt(0.0, QColor(LIVE.red(), LIVE.green(), LIVE.blue(), int(70 + 60 * self._blink)))
            glow.setColorAt(1.0, QColor(LIVE.red(), LIVE.green(), LIVE.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(glow)
            p.drawRoundedRect(brect.adjusted(-6, -6, 6, 6), bh, bh)
            p.fillPath(bpath, lc)
            # 小白点 + 文字
            p.setPen(QColor("#FFFFFF"))
            p.drawText(brect, int(Qt.AlignmentFlag.AlignCenter), self._badge)


class _TrophyOrb(QWidget):
    """品牌区金色大力神杯 logo（自绘）。"""

    def __init__(self, size: int = 38, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        cx, cy = r.center().x(), r.center().y()

        # 外圈金色光晕
        glow = QRadialGradient(QPointF(cx, cy), self.width() * 0.72)
        glow.setColorAt(0.42, QColor(255, 215, 0, 210))
        glow.setColorAt(1.0, QColor(255, 215, 0, 0))
        p.setBrush(glow)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(r)

        # 主圆盘（金渐变）
        inner = r.adjusted(3, 3, -3, -3)
        ball = QLinearGradient(QPointF(inner.topLeft()), QPointF(inner.bottomRight()))
        ball.setColorAt(0.0, QColor("#FFE680"))
        ball.setColorAt(0.55, QColor("#FFC04D"))
        ball.setColorAt(1.0, QColor("#A8730E"))
        p.setBrush(ball)
        p.drawEllipse(inner)

        # 高光
        spec = QRadialGradient(
            QPointF(cx - self.width() * 0.18, cy - self.height() * 0.22),
            self.width() * 0.45,
        )
        spec.setColorAt(0.0, QColor(255, 255, 255, 170))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.drawEllipse(inner)

        # 中央奖杯符号
        f = QFont(self.font())
        f.setPointSize(int(self.width() * 0.42))
        p.setFont(f)
        p.setPen(QColor("#5A3B00"))
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), "🏆")


class _CountdownCard(QFrame):
    """炫彩渐变倒计时卡：距开幕 365 天 + 日期 + 举办地。"""

    def __init__(self, days: int = 365, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CountdownCard")
        self.setFixedHeight(118)
        self._days = days

        col = QVBoxLayout(self)
        col.setContentsMargins(16, 13, 16, 13)
        col.setSpacing(2)

        cap = QLabel("距 FIFA 世界杯开幕")
        cap.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size:10.5px; font-weight:800;"
            " letter-spacing:0.5px; background:transparent;"
        )
        col.addWidget(cap)

        days_row = QHBoxLayout()
        days_row.setSpacing(6)
        days_row.setContentsMargins(0, 0, 0, 0)
        num = QLabel(str(days))
        num.setStyleSheet(
            "color:#FFFFFF; font-size:36px; font-weight:900; background:transparent;"
        )
        days_row.addWidget(num)
        unit = QLabel("天")
        unit.setStyleSheet(
            "color:rgba(255,255,255,0.92); font-size:14px; font-weight:800;"
            " background:transparent; padding-bottom:6px;"
        )
        days_row.addWidget(unit, alignment=Qt.AlignmentFlag.AlignBottom)
        days_row.addStretch(1)
        col.addLayout(days_row)

        date_lbl = QLabel("2026.06.11 开幕")
        date_lbl.setStyleSheet(
            "color:#FFFFFF; font-size:11px; font-weight:800; background:transparent;"
        )
        col.addWidget(date_lbl)
        host = QLabel("美国 · 加拿大 · 墨西哥")
        host.setStyleSheet(
            "color:rgba(255,255,255,0.85); font-size:10px; font-weight:600;"
            " background:transparent;"
        )
        col.addWidget(host)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(30)
        eff.setOffset(0, 8)
        eff.setColor(QColor(106, 90, 205, 120))
        self.setGraphicsEffect(eff)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 16.0, 16.0)
        # 炫彩斜向渐变：电光蓝 → 皇家紫 → 樱粉
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor("#1FA2FF"))
        grad.setColorAt(0.55, QColor("#6A5ACD"))
        grad.setColorAt(1.0, QColor("#B14FCB"))
        p.fillPath(path, grad)
        # 顶部高光叠层
        sheen = QLinearGradient(r.topLeft(), r.bottomLeft())
        sheen.setColorAt(0.0, QColor(255, 255, 255, 46))
        sheen.setColorAt(0.5, QColor(255, 255, 255, 0))
        p.fillPath(path, sheen)
        p.setPen(QPen(QColor(255, 255, 255, 60), 1.0))
        p.drawPath(path)


class _UserBar(QFrame):
    """底部用户栏：圆形头像 + 昵称 + 等级。"""

    def __init__(self, name: str = "WorldCup Fan", level: str = "Lv.12",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("UserBar")
        self.setFixedHeight(58)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._name = name
        self._level = level

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(10)
        row.addWidget(_Avatar(38, "WF"))
        col = QVBoxLayout()
        col.setSpacing(1)
        n = QLabel(name)
        n.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:800; background:transparent;")
        col.addWidget(n)
        lv = QLabel(f"⭐ {level}  精英球迷")
        lv.setStyleSheet("color:#FFD700; font-size:10px; font-weight:700; background:transparent;")
        col.addWidget(lv)
        row.addLayout(col)
        row.addStretch(1)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 14.0, 14.0)
        p.fillPath(path, QColor(255, 255, 255, 12))
        p.setPen(QPen(QColor(255, 255, 255, 26), 1.0))
        p.drawPath(path)


class _Avatar(QWidget):
    """圆形头像（渐变底 + 首字母）。"""

    def __init__(self, size: int = 38, initials: str = "WF",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._initials = initials

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor("#46D2FF"))
        grad.setColorAt(1.0, QColor("#6A5ACD"))
        p.setBrush(grad)
        p.setPen(QPen(QColor(255, 255, 255, 90), 1.5))
        p.drawEllipse(r)
        f = QFont(self.font())
        f.setPointSize(int(self.width() * 0.32))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), self._initials)


class NavSidebar(QFrame):
    """侧边导航。每个 item = (key, icon, label[, badge])。"""

    selected = pyqtSignal(str)

    def __init__(self, items: Iterable[tuple]) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 18, 0, 12)
        layout.setSpacing(1)

        # ── 品牌区 ──────────────────────────
        brand = QHBoxLayout()
        brand.setContentsMargins(18, 0, 18, 12)
        brand.setSpacing(10)
        brand.addWidget(_TrophyOrb(size=38))
        col = QVBoxLayout()
        col.setSpacing(1)
        title = QLabel("世界杯 2026")
        title.setStyleSheet(
            "color:#ffffff; font-size:15px; font-weight:900; letter-spacing:0.5px;"
            " background:transparent;"
        )
        col.addWidget(title)
        sub = QLabel("FIFA WORLD CUP")
        sub.setStyleSheet(
            "color:#FFD700; font-size:9px; font-weight:800; letter-spacing:2px;"
            " background:transparent;"
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
        sep_lay = QVBoxLayout()
        sep_lay.setContentsMargins(18, 0, 18, 8)
        sep_lay.addWidget(sep)
        sep_wrap = QWidget(); sep_wrap.setLayout(sep_lay)
        layout.addWidget(sep_wrap)

        # ── 导航行 ──────────────────────────
        self._rows: dict[str, NavRow] = {}
        for item in items:
            key, emoji, label = item[0], item[1], item[2]
            badge = item[3] if len(item) > 3 else None
            row = NavRow(key, emoji, label, badge)
            row.clicked.connect(self.set_active)
            layout.addWidget(row)
            self._rows[key] = row

        layout.addStretch(1)

        # ── 倒计时卡 ─────────────────────────
        cd_lay = QVBoxLayout()
        cd_lay.setContentsMargins(12, 4, 12, 8)
        cd_lay.addWidget(_CountdownCard(days=365))
        cd_wrap = QWidget(); cd_wrap.setLayout(cd_lay)
        layout.addWidget(cd_wrap)

        # ── 底部用户栏 ───────────────────────
        user_lay = QVBoxLayout()
        user_lay.setContentsMargins(12, 0, 12, 0)
        user_lay.addWidget(_UserBar("WorldCup Fan", "Lv.12"))
        user_wrap = QWidget(); user_wrap.setLayout(user_lay)
        layout.addWidget(user_wrap)

    def set_active(self, key: str) -> None:
        # settings 等「动作型」条目可能没有持久高亮需求，但这里统一处理高亮，
        # 真正的「打开设置」由 MainWindow 在 selected 槽里判断 key 决定。
        if key in self._rows:
            for k, row in self._rows.items():
                row.set_active(k == key)
        self.selected.emit(key)

    def apply_palette(self, palette) -> None:
        apply_palette(palette)
        for row in self._rows.values():
            row.update()
        self.update()
