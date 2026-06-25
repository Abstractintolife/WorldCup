"""单组小型积分榜卡片（A 组 - L 组用同一控件）。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.standing import GroupStanding, TeamStanding
from app.ui.theme import ThemePalette
from app.ui.widgets.misc import Card
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class _RankRow(QFrame):
    """单行：名次徽章 + 队徽 + 队名 + 战绩 + 净胜 + 积分。"""

    clicked = pyqtSignal(str)

    def __init__(self, team: TeamStanding, leader_color: QColor) -> None:
        super().__init__()
        self._team_id = team.team_id
        self.setCursor(pointing_hand_cursor())
        self.setFixedHeight(46)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._base_qss = (
            "_RankRow{background: rgba(255,255,255,0.025); border-radius: 10px;"
            " border: 1px solid rgba(255,255,255,0.04);}"
            "_RankRow:hover{background: rgba(255,255,255,0.07);"
            f" border: 1px solid {leader_color.name()};}}"
        )
        self.setStyleSheet(self._base_qss)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 12, 4)
        layout.setSpacing(10)

        # 晋级状态配色（覆盖 API 图例色，让晋级一目了然）
        qualify = getattr(team, "qualify", None)
        _QUALIFY_COLORS = {"direct": "#2ED877", "best3": "#36A8FF"}
        if qualify in _QUALIFY_COLORS:
            rank_color = _QUALIFY_COLORS[qualify]
        else:
            rank_color = team.color or leader_color.name()

        # 名次徽章（带「晋级条」颜色）
        rank = QLabel(str(team.rank))
        rank.setFixedSize(24, 24)
        rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank.setStyleSheet(
            f"background:{rank_color}; color:white; font-weight:900;"
            f"border-radius:6px; font-size:12px;"
        )
        layout.addWidget(rank)

        layout.addWidget(TeamLogo(team.team_logo, size=26, shape="circle"))

        name = QLabel(team.team_name)
        name.setStyleSheet("font-size: 13px; font-weight: 700;")
        layout.addWidget(name)

        # 晋级胶囊：直接晋级（绿）/ 最佳第三（蓝）
        if qualify == "direct":
            chip = QLabel("晋级")
            chip.setStyleSheet(
                "color:#9DF5C4; font-size:10px; font-weight:800;"
                "background: rgba(46,216,131,0.16);"
                "border:1px solid rgba(46,216,131,0.45);"
                "border-radius:8px; padding:1px 8px;"
            )
            layout.addWidget(chip)
        elif qualify == "best3":
            chip = QLabel("最佳第三")
            chip.setStyleSheet(
                "color:#A9D8FF; font-size:10px; font-weight:800;"
                "background: rgba(54,168,255,0.16);"
                "border:1px solid rgba(54,168,255,0.45);"
                "border-radius:8px; padding:1px 8px;"
            )
            layout.addWidget(chip)

        layout.addStretch(1)

        record = QLabel(
            f"{team.matches_won}-{team.matches_draw}-{team.matches_lost}"
        )
        record.setStyleSheet("color: #B0BEC5; font-size: 11.5px; font-weight: 600;")
        record.setFixedWidth(56)
        record.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(record)

        gd = team.goal_diff
        gd_text = f"+{gd}" if gd > 0 else str(gd)
        gd_lbl = QLabel(gd_text)
        gd_lbl.setStyleSheet("color: #B0BEC5; font-size: 11.5px; font-weight: 600;")
        gd_lbl.setFixedWidth(36)
        gd_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(gd_lbl)

        pts = QLabel(str(team.points))
        pts.setStyleSheet(
            f"color:{leader_color.name()}; font-weight: 900; font-size: 16px;"
        )
        pts.setFixedWidth(32)
        pts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pts)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._team_id)
        super().mousePressEvent(ev)


class GroupCard(Card):
    """单组卡片。点击单行 → 球队详情。"""

    team_clicked = pyqtSignal(str)

    def __init__(self, group: GroupStanding, theme: ThemePalette) -> None:
        leader_color = theme.group_color(group.name)
        super().__init__(padding=14, glow_color=leader_color.name())
        self._group = group
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(8)

        # 头部
        head = QHBoxLayout()
        head.setSpacing(8)
        badge = QLabel(group.name)
        badge.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {leader_color.name()}, stop:1 rgba(255,255,255,0.05));"
            f" color: white; font-weight:900; padding:4px 14px; border-radius:9px;"
            f" font-size:13px; letter-spacing:1px;"
        )
        head.addWidget(badge)
        head.addStretch(1)
        teams_count = QLabel(f"{len(group.teams)} 队")
        teams_count.setStyleSheet("color:#B0BEC5; font-size:11.5px; font-weight:700;")
        head.addWidget(teams_count)
        layout.addLayout(head)

        # 表头
        col = QHBoxLayout()
        col.setContentsMargins(34, 0, 12, 0)
        col.setSpacing(10)
        for text, w, align in (
            ("球队", -1, Qt.AlignmentFlag.AlignLeft),
            ("胜平负", 56, Qt.AlignmentFlag.AlignCenter),
            ("净胜", 36, Qt.AlignmentFlag.AlignCenter),
            ("分", 32, Qt.AlignmentFlag.AlignCenter),
        ):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "color:#56607D; font-size:10.5px; font-weight:800; letter-spacing:0.6px;"
            )
            if w >= 0:
                lbl.setFixedWidth(w)
            else:
                lbl.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
            lbl.setAlignment(align)
            col.addWidget(lbl)
        layout.addLayout(col)

        # 行
        for t in group.teams:
            row = _RankRow(t, leader_color)
            row.clicked.connect(self.team_clicked.emit)
            layout.addWidget(row)

        # 图例
        if group.legend:
            legend = QHBoxLayout()
            legend.setSpacing(10)
            for item in group.legend[:3]:
                dot = QLabel("●")
                dot.setStyleSheet(f"color:{item.get('color')}; font-size:12px;")
                txt = QLabel(item.get("desc") or "")
                txt.setStyleSheet("color:#B0BEC5; font-size:10.5px; font-weight:600;")
                legend.addWidget(dot)
                legend.addWidget(txt)
            legend.addStretch(1)
            layout.addLayout(legend)
