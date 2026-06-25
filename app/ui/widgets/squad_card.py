"""国家队阵容卡片 —— 单个球员 / 教练。

设计目标：干净、专业、稳健。
* 全部用标准布局（QVBoxLayout），不做手动 setGeometry，避免跨平台错位。
* 顶行：左侧球衣号徽，右侧队长「C」金牌。
* 居中圆形头像，外圈用位置色描边。
* 姓名（粗体）+「位置 · 年龄」。
* 悬停：边框点亮 + 阴影加深（轻微浮起感）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.models.squad import SquadMember
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.design.app_cursor import pointing_hand_cursor


# 位置 → 强调色
ROLE_COLOR = {
    "门将": "#FFD700",
    "后卫": "#00BFFF",
    "中场": "#2ED877",
    "前锋": "#FF5470",
    "教练": "#6A5ACD",
}
ROLE_COLOR_DEFAULT = "#00BFFF"


class SquadPlayerCard(QFrame):
    """单名球员 / 教练卡片。"""

    clicked = pyqtSignal(str, str)  # person_id, name

    CARD_W = 168
    CARD_H = 208

    def __init__(self, member: SquadMember, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._m = member
        accent = ROLE_COLOR.get(member.role_title, ROLE_COLOR_DEFAULT)
        self._accent = accent

        self.setObjectName("SquadCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setCursor(pointing_hand_cursor())
        self.setStyleSheet(
            "QFrame#SquadCard {"
            "  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "      stop:0 rgba(255,255,255,0.07), stop:1 rgba(255,255,255,0.025));"
            "  border: 1px solid rgba(255,255,255,0.10);"
            "  border-radius: 16px;"
            "}"
            "QFrame#SquadCard:hover {"
            f"  border: 1px solid {accent};"
            "  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "      stop:0 rgba(255,255,255,0.11), stop:1 rgba(255,255,255,0.04));"
            "}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 14)
        root.setSpacing(6)

        # 顶行：号码 + 队长
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        num = member.shirt_number
        num_text = num if num else ("教练" if member.role_title == "教练" else "·")
        badge = QLabel(num_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(22)
        badge.setMinimumWidth(28)
        badge.setStyleSheet(
            f"color:{accent}; font-weight:800; font-size:12px;"
            "background: rgba(255,255,255,0.07); border-radius:11px; padding:0 8px;"
        )
        top.addWidget(badge)
        top.addStretch(1)
        if member.is_captain:
            cap = QLabel("C")
            cap.setFixedSize(22, 22)
            cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cap.setStyleSheet(
                "color:#1a1304; font-weight:900; font-size:12px; border-radius:11px;"
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #ffe680, stop:1 #d4a017);"
            )
            top.addWidget(cap)
        root.addLayout(top)

        # 头像（带位置色外圈）
        av_wrap = QWidget()
        av_l = QHBoxLayout(av_wrap)
        av_l.setContentsMargins(0, 0, 0, 0)
        av_l.addStretch(1)
        ring = QFrame()
        ring.setFixedSize(78, 78)
        ring.setStyleSheet(
            f"background: rgba(255,255,255,0.04); border:2px solid {accent};"
            " border-radius:39px;"
        )
        ring_l = QHBoxLayout(ring)
        ring_l.setContentsMargins(5, 5, 5, 5)
        ring_l.addWidget(PlayerAvatar(member.logo, size=66))
        av_l.addWidget(ring)
        av_l.addStretch(1)
        root.addWidget(av_wrap)

        # 姓名
        name = QLabel(member.name or "—")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(False)
        name.setStyleSheet("font-size:14px; font-weight:800; color:#f2f4fb;")
        root.addWidget(name)

        # 位置 · 年龄
        bits = [member.role_title or "球员"]
        if member.age:
            bits.append(member.age)
        meta = QLabel("  ·  ".join(bits))
        meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meta.setStyleSheet("color:#B0BEC5; font-size:11px;")
        root.addWidget(meta)
        root.addStretch(1)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton and self._m.person_id:
            self.clicked.emit(self._m.person_id, self._m.name)
        super().mousePressEvent(ev)
