"""3A 游戏级「球星特色卡片」。

* 毛玻璃卡片 + 顶部「出框」球员头像（鼠标悬停时上浮放大、突破卡片上边界）。
* 悬停：环境呼吸光晕 + 头像放大 105%。
* 金色「特色徽章」（速度型 ⚡ / 终结杀手 🎯 等），悬停时有金属流光划过。
* 综合评分 OVR + 位置 + Top3 能力迷你条。
"""
from __future__ import annotations

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.models.player import PlayerRanking
from app.services.player_stats import player_stats
from app.ui.design.frame_clock import FrameClock
from app.ui.widgets.effects import BreathingGlow
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.design.app_cursor import pointing_hand_cursor



class _StatBar(QWidget):
    """单条能力迷你进度条。"""

    def __init__(self, code: str, value: int, color: str) -> None:
        super().__init__()
        self._code = code
        self._value = value
        self._color = QColor(color)
        self.setFixedHeight(15)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(QColor("#B0BEC5"))
        f = QFont(self.font()); f.setPointSize(8); f.setBold(True)
        p.setFont(f)
        p.drawText(0, 0, 30, h, int(Qt.AlignmentFlag.AlignVCenter), self._code)
        p.drawText(w - 24, 0, 24, h,
                   int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                   str(self._value))
        tx, tw = 32, w - 32 - 28
        ty, th = h / 2 - 2.5, 5
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 22))
        p.drawRoundedRect(int(tx), int(ty), int(tw), int(th), 2, 2)
        fillw = int(tw * self._value / 99.0)
        p.setBrush(self._color)
        p.drawRoundedRect(int(tx), int(ty), fillw, int(th), 2, 2)



class _ShineBadge(QLabel):
    """金色特色徽章，悬停时金属流光划过。"""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setFixedHeight(22)
        self.setStyleSheet(
            "color:#1a1304; font-weight:800; font-size:11px;"
            "padding:0 10px; border-radius:11px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #ffe680, stop:0.5 #ffd700, stop:1 #d4a017);"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._shine = -0.4
        self._clock = FrameClock.instance()
        self._shining = False

    def _on_frame(self, _t: float, dt: float) -> None:
        # 帧率无关：每秒推进约 2.1（≈ 旧版 0.06/帧 @ 35fps）
        self._shine += dt * 2.1
        if self._shine > 1.4:
            self._shine = -0.4
            self._stop_shine()
        self.update()

    def _stop_shine(self) -> None:
        if self._shining:
            self._clock.unsubscribe(self._on_frame)
            self._shining = False

    def shine(self) -> None:
        self._shine = -0.4
        if not self._shining:
            self._clock.subscribe(self._on_frame)
            self._shining = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        self._stop_shine()

    def paintEvent(self, ev) -> None:
        super().paintEvent(ev)
        if not self._shining:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        g = QLinearGradient(self._shine * w - 24, 0, self._shine * w + 24, 0)
        g.setColorAt(0.0, QColor(255, 255, 255, 0))
        g.setColorAt(0.5, QColor(255, 255, 255, 170))
        g.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(g)
        p.drawRoundedRect(self.rect(), 11, 11)



_TAG_COLOR = {
    "speed": "#00e5ff", "finisher": "#ff0055", "maestro": "#00ff66",
    "wall": "#00BFFF", "tank": "#ffd700", "balance": "#00BFFF",
}


class PlayerStarCard(QWidget):
    """球星卡片容器（顶部留白用于头像出框）。"""

    clicked = pyqtSignal(str, str)        # person_id, person_name

    CARD_W = 196
    CARD_H = 292

    def __init__(self, ranking: PlayerRanking, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._p = ranking
        self._stats = player_stats(ranking)
        self._accent = _TAG_COLOR.get(self._stats.tag_code, "#00BFFF")
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setMouseTracking(True)
        self.setCursor(pointing_hand_cursor())

        # 毛玻璃主体
        self._glass = QFrame(self)
        self._glass.setObjectName("GlassCard")
        self._glass.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        gl = QVBoxLayout(self._glass)
        gl.setContentsMargins(14, 54, 14, 14)
        gl.setSpacing(6)

        name = QLabel(ranking.person_name or "—")
        name.setStyleSheet("font-size:15px; font-weight:800;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(name)

        team = QLabel(ranking.team_name or "")
        team.setStyleSheet("color:#B0BEC5; font-size:11px;")
        team.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(team)


        # OVR + 位置
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addStretch(1)
        ovr = QLabel(f"{self._stats.ovr}")
        ovr.setStyleSheet(
            "color:#ffd700; font-size:22px; font-weight:900;")
        row.addWidget(ovr)
        ovr_lab = QLabel("OVR")
        ovr_lab.setStyleSheet("color:#B0BEC5; font-size:10px; font-weight:700;")
        row.addWidget(ovr_lab)
        sep = QLabel("·"); sep.setStyleSheet("color:#525c7a;")
        row.addWidget(sep)
        pos = QLabel(self._stats.position)
        pos.setStyleSheet(
            f"color:{self._accent}; font-size:12px; font-weight:800;"
            "background: rgba(255,255,255,0.06); border-radius:8px; padding:2px 8px;")
        row.addWidget(pos)
        row.addStretch(1)
        gl.addLayout(row)

        # 特色徽章
        badge_row = QHBoxLayout()
        badge_row.addStretch(1)
        self._badge = _ShineBadge(f"{self._stats.tag_icon}  {self._stats.tag_label}")
        badge_row.addWidget(self._badge)
        badge_row.addStretch(1)
        gl.addLayout(badge_row)

        gl.addSpacing(2)
        # Top3 能力条
        pairs = sorted(self._stats.as_pairs(), key=lambda x: x[2], reverse=True)[:3]
        for code, _zh, val, color in pairs:
            gl.addWidget(_StatBar(code, val, color))
        gl.addStretch(1)

        # 出框头像
        self._avatar = PlayerAvatar(ranking.person_logo, self, size=88)
        self._glow = BreathingGlow(self._glass, self._accent, base=10, peak=40)
        self._glow.stop()
        self._hovering = False
        self._av_anim: QPropertyAnimation | None = None


    # ── 几何 ──────────────────────────────
    def _avatar_geo(self, hover: bool) -> QRect:
        size = 96 if hover else 88
        x = (self.CARD_W - size) // 2
        y = 2 if hover else 12
        return QRect(x, y, size, size)

    def resizeEvent(self, ev) -> None:
        self._glass.setGeometry(0, 56, self.CARD_W, self.CARD_H - 56)
        self._avatar.setGeometry(self._avatar_geo(self._hovering))
        self._avatar.raise_()
        super().resizeEvent(ev)

    def _animate_avatar(self, hover: bool) -> None:
        target = self._avatar_geo(hover)
        anim = QPropertyAnimation(self._avatar, b"geometry", self)
        anim.setDuration(220)
        anim.setStartValue(self._avatar.geometry())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        self._av_anim = anim

    # ── 悬停 ──────────────────────────────
    def enterEvent(self, _ev) -> None:
        self._hovering = True
        self._animate_avatar(True)
        self._glow.start()
        self._badge.shine()

    def leaveEvent(self, _ev) -> None:
        self._hovering = False
        self._animate_avatar(False)
        self._glow.stop()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._p.person_id, self._p.person_name)
