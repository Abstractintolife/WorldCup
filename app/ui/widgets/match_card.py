"""比赛卡片：在赛程页 / 首页 / 球队页都会用。

特点
-----
* 大字比分居中，两侧球队居中。
* 顶部状态徽章（直播 / 已结束 / 未开赛）+ 日期。
* 底部时间居左 + match_id 居右。
* 直播态的卡片自带红色 glow，显眼。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.misc import Card, StatusChip
from app.utils.time_utils import fmt_short_date, fmt_time
from app.ui.design.app_cursor import pointing_hand_cursor


class MatchCard(Card):
    """单场比赛卡片，点击可发出 ``clicked`` 信号。"""

    clicked = pyqtSignal(Match)

    def __init__(self, match: Match, parent: QWidget | None = None) -> None:
        if match.status in (MatchStatus.LIVE, MatchStatus.HALF_TIME):
            _glow = "#FF3057"
        elif match.status == MatchStatus.PLAYED:
            _glow = "#2ED883"
        else:
            _glow = "#00BFFF"
        super().__init__(parent, padding=14, glow_color=_glow)
        self._match = match
        self.setCursor(pointing_hand_cursor())
        self.setMinimumWidth(330)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        # ── 顶部：日期 + 状态徽章 ───────────────
        top = QHBoxLayout()
        top.setSpacing(8)
        date_lbl = QLabel(self._date_text())
        date_lbl.setStyleSheet("color: #B0BEC5; font-size: 11.5px; font-weight: 700;")
        top.addWidget(date_lbl)
        top.addStretch(1)
        chip_status, chip_text = _chip_for(match)
        self._chip = StatusChip(chip_status, chip_text)
        top.addWidget(self._chip)
        outer.addLayout(top)

        # ── 中部：A 队 logo + 名字 + 比分 + 名字 + B 队 logo ──
        body = QHBoxLayout()
        body.setSpacing(10)

        a_box = self._team_box(
            match.team_a_name, match.team_a_short or match.team_a_name, align="left"
        )
        body.addLayout(a_box, 4)

        score = QLabel(match.display_score)
        score_font = QFont()
        score_font.setPointSize(20)
        score_font.setBold(True)
        score.setFont(score_font)
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score.setStyleSheet(
            "color: #FFD700;" if match.status == MatchStatus.PLAYED
            else "color: #46D2FF;"
        )
        body.addWidget(score, 3)

        b_box = self._team_box(
            match.team_b_name, match.team_b_short or match.team_b_name, align="right"
        )
        body.addLayout(b_box, 4)
        outer.addLayout(body)

        # ── 底部：时间 / 比赛 ID ───────────────
        bottom = QHBoxLayout()
        time_lbl = QLabel("⏱  " + fmt_time(match.start_play))
        time_lbl.setStyleSheet("color: #B0BEC5; font-size: 11.5px; font-weight: 600;")
        bottom.addWidget(time_lbl)
        bottom.addStretch(1)
        id_lbl = QLabel(f"#{match.match_id}")
        id_lbl.setStyleSheet("color: #56607D; font-size: 10.5px; font-weight: 700;")
        bottom.addWidget(id_lbl)
        outer.addLayout(bottom)

    # ─────────────────────────────────────────
    def _date_text(self) -> str:
        if self._match.start_play:
            return fmt_short_date(self._match.start_play)
        return self._match.date_utc or "—"

    def _team_box(
        self, team_name: str | None, name: str, *, align: str
    ) -> QVBoxLayout:
        wrap = QVBoxLayout()
        wrap.setSpacing(6)
        wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 完整国旗（不裁剪 / 不圆角），代替原先被圆形裁掉边缘的队徽；
        # 旗面右下角紧贴国际足联世界排名标注（如「#12」）。
        flag_row = QHBoxLayout()
        flag_row.setSpacing(4)
        flag_row.setContentsMargins(0, 0, 0, 0)
        flag_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_row.addWidget(
            FlagIcon(team_name, height=30), alignment=Qt.AlignmentFlag.AlignVCenter)
        rank_lbl = self._rank_lbl(team_name)
        if rank_lbl is not None:
            flag_row.addWidget(rank_lbl, alignment=Qt.AlignmentFlag.AlignBottom)
        wrap.addLayout(flag_row)
        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet("font-weight: 700; font-size:12.5px;")
        wrap.addWidget(name_lbl)
        return wrap

    @staticmethod
    def _rank_lbl(team_name: str | None) -> QLabel | None:
        """国际足联世界排名小标注（如「#12」）；无排名则不展示。"""
        from app.services.fifa_rankings import FifaRankings
        txt = FifaRankings.instance().rank_text(team_name)
        if not txt:
            return None
        lbl = QLabel(txt)
        lbl.setToolTip("国际足联世界排名")
        lbl.setStyleSheet(
            "color:#FFD166; font-size:10px; font-weight:900; background:transparent;")
        return lbl

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._match)
        super().mousePressEvent(ev)


def _chip_for(match: Match) -> tuple[str, str]:
    if match.status == MatchStatus.LIVE:
        minute = match.minute or "·"
        extra = f"+{match.minute_extra}" if match.minute_extra and match.minute_extra != "0" else ""
        return "live", f"直播 {minute}'{extra}"
    if match.status == MatchStatus.HALF_TIME:
        return "live", "中场"
    if match.status == MatchStatus.PLAYED:
        return "finished", "已结束"
    if match.status == MatchStatus.POSTPONED:
        return "finished", "推迟"
    if match.status == MatchStatus.CANCELED:
        return "finished", "取消"
    return "upcoming", "未开赛"
