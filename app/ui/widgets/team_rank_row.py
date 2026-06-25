"""球队数据榜单行 —— 名次徽章 + 队徽 + 队名 + 进度条 + 数值。

与球员榜 :class:`RankingRow` 风格一致（复用其 ``_RankBadge`` / ``_Bar``），
但只展示球队信息（无头像 / 位置）。纯 ``QFrame`` + ``paintEvent`` 自绘背景，
规避 ``QScrollArea`` + 阴影特效的整列堆叠渲染 bug。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.models.player import TeamRanking
from app.ui.widgets.ranking_row import _Bar, _RankBadge, _GOLD, _GREEN
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class TeamRankRow(QFrame):
    """单行球队排行。"""

    team_clicked = pyqtSignal(str)

    def __init__(self, team: TeamRanking, max_count: float) -> None:
        super().__init__()
        self._team = team
        self._max = max(1.0, max_count)
        self._leader = (team.value or 0) >= self._max
        self._accent = QColor(_GOLD if self._leader else _GREEN)
        self._hover = False
        self.setObjectName("RankingRow")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(72)
        self.setCursor(pointing_hand_cursor())
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 24, 10)
        outer.setSpacing(16)

        outer.addWidget(_RankBadge(team.rank, self._leader))
        # 队徽（懂球帝官方图，已是该国家队徽/旗，无需再叠一面国旗）
        outer.addWidget(TeamLogo(team.team_logo, size=44, shape="circle"))

        name = QLabel(team.team_name)
        nf = QFont()
        nf.setPointSize(14)
        nf.setBold(True)
        name.setFont(nf)
        name.setStyleSheet("color:#FFFFFF;")
        name.setMinimumWidth(120)
        outer.addWidget(name)

        bar = _Bar(team.value, self._max, _GOLD if self._leader else _GREEN)
        outer.addWidget(bar, 1)

        count_box = QVBoxLayout()
        count_box.setSpacing(0)
        cnum = QLabel(team.display)
        cnum.setStyleSheet(
            f"color:{_GOLD if self._leader else '#FFFFFF'};"
            "font-size:24px; font-weight:900;"
        )
        cnum.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_box.addWidget(cnum)
        unit_txt = team.ranking_type.unit
        if unit_txt:
            unit = QLabel(unit_txt)
            unit.setStyleSheet("color:#B0BEC5; font-size:10.5px; font-weight:700;")
            unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_box.addWidget(unit)
        cnt_w = QWidget()
        cnt_w.setLayout(count_box)
        cnt_w.setFixedWidth(96)
        outer.addWidget(cnt_w)

    # ── 事件 ─────────────────────────────────
    def enterEvent(self, _ev) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, _ev) -> None:
        self._hover = False
        self.update()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton and self._team.team_id:
            self.team_clicked.emit(self._team.team_id)
        super().mousePressEvent(ev)

    # ── 绘制 ────────────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 16, 16)

        bg = QLinearGradient(r.topLeft(), r.bottomLeft())
        bg.setColorAt(0.0, QColor(255, 255, 255, 16))
        bg.setColorAt(1.0, QColor(255, 255, 255, 6))
        p.fillPath(path, bg)

        ac = self._accent
        warm = QLinearGradient(r.topLeft(), r.topRight())
        warm.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(),
                                    70 if self._leader else 26))
        warm.setColorAt(0.45, QColor(ac.red(), ac.green(), ac.blue(), 0))
        p.fillPath(path, warm)

        if self._hover:
            p.fillPath(path, QColor(255, 255, 255, 20))

        pen_col = (QColor(ac.red(), ac.green(), ac.blue(), 220)
                   if self._hover else QColor(255, 255, 255, 28))
        p.setPen(QPen(pen_col, 1.4))
        p.drawPath(path)
