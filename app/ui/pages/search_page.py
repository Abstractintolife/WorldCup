"""全局搜索结果页：聚合显示队伍 / 球员 / 比赛 / 球场命中。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match
from app.models.player import RankingType
from app.services.data_service import DataService
from app.services.stadiums_data import find_stadium
from app.ui.pages.base import BasePage
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.match_card import MatchCard
from app.ui.widgets.misc import Card
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class SearchPage(BasePage):
    title = "搜索"
    subtitle = "搜全部 · 球队 / 球员 / 比赛 / 球场"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._query: str = ""

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(14)

    def search(self, query: str) -> None:
        self._query = query.strip()
        self.refresh(force=False)

    def refresh(self, force: bool = False) -> None:
        if not self._query:
            return

        async def runner() -> None:
            groups, _ko, _km = await self._service.fetch_standings(force=force)
            _rounds, matches = await self._service.fetch_full_schedule(force=force)
            scorers = await self._service.fetch_ranking(RankingType.GOALS, force=force)
            assists = await self._service.fetch_ranking(RankingType.ASSISTS, force=force)
            stadiums = find_stadium(self._query)
            self._render(groups, matches, scorers, assists, stadiums)

        self.run_async(runner)

    def _render(self, groups, matches, scorers, assists, stadiums) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        q = self._query.lower()

        # 球队
        team_hits = []
        for g in groups:
            for t in g.teams:
                if q in t.team_name.lower() or q in t.team_id:
                    team_hits.append((g.name, t))

        # 球员
        player_pool = {p.person_id: p for p in scorers + assists}
        player_hits = [
            p for p in player_pool.values()
            if q in p.person_name.lower() or q in p.person_id
        ]

        # 比赛
        match_hits = [
            m
            for m in matches
            if q in m.team_a_name.lower()
            or q in m.team_b_name.lower()
            or q in m.match_id
        ][:18]

        # 头部摘要
        head = Card(padding=18)
        h_lay = QVBoxLayout(head)
        h_lay.setContentsMargins(20, 14, 20, 14)
        title = QLabel(f"🔎  搜索：「{self._query}」")
        title.setStyleSheet("font-size:18px; font-weight:800;")
        h_lay.addWidget(title)
        sub = QLabel(
            f"球队 {len(team_hits)} · 球员 {len(player_hits)} · "
            f"比赛 {len(match_hits)} · 球场 {len(stadiums)}"
        )
        sub.setStyleSheet("color:#B0BEC5; font-size:12px;")
        h_lay.addWidget(sub)
        self._body.addWidget(head)

        # 球队结果
        if team_hits:
            self._body.addWidget(_SectionTitle("🛡  球队"))
            grid = FlowLayout(margin=0, h_spacing=10, v_spacing=10)
            wrap = QWidget(); wrap.setLayout(grid)
            for grp_name, t in team_hits[:24]:
                chip = _ClickableChip(
                    f"{t.team_name}  ·  {grp_name}",
                    TeamLogo(t.team_logo, size=28, shape="circle"),
                )
                chip.clicked.connect(lambda _e=None, tid=t.team_id: self.team_clicked.emit(tid))
                grid.addWidget(chip)
            self._body.addWidget(wrap)

        # 球员结果
        if player_hits:
            self._body.addWidget(_SectionTitle("⚽  球员"))
            grid = FlowLayout(margin=0, h_spacing=10, v_spacing=10)
            wrap = QWidget(); wrap.setLayout(grid)
            for p in player_hits[:24]:
                chip = _ClickableChip(
                    f"{p.person_name}  ·  {p.team_name}",
                    PlayerAvatar(p.person_logo, size=28),
                )
                chip.clicked.connect(
                    lambda _e=None, pid=p.person_id, name=p.person_name: self.player_clicked.emit(pid, name)
                )
                grid.addWidget(chip)
            self._body.addWidget(wrap)

        # 比赛结果
        if match_hits:
            self._body.addWidget(_SectionTitle("📅  比赛"))
            grid = FlowLayout()
            wrap = QWidget(); wrap.setLayout(grid)
            for m in match_hits:
                card = MatchCard(m)
                card.clicked.connect(self.match_clicked.emit)
                grid.addWidget(card)
            self._body.addWidget(wrap)

        # 球场结果（仅文字提示）
        if stadiums:
            self._body.addWidget(_SectionTitle("🏟  球场"))
            for s in stadiums[:8]:
                lbl = QLabel(
                    f"<b>{s.name_zh}</b> "
                    f"<span style='color:#B0BEC5'> · {s.city} · {s.country} · "
                    f"{s.capacity:,} 人</span>"
                )
                lbl.setWordWrap(True)
                self._body.addWidget(lbl)

        if not (team_hits or player_hits or match_hits or stadiums):
            empty = QLabel("没有找到匹配结果。")
            empty.setStyleSheet("color:#B0BEC5; padding: 24px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._body.addWidget(empty)

        self._body.addStretch(1)


class _SectionTitle(QLabel):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setStyleSheet("font-size:15px; font-weight:800; padding-top:8px;")


class _ClickableChip(QWidget):
    clicked = pyqtSignal()

    def __init__(self, text: str, icon: QWidget) -> None:
        super().__init__()
        self.setCursor(pointing_hand_cursor())
        h = QHBoxLayout(self)
        h.setContentsMargins(10, 6, 14, 6)
        h.setSpacing(10)
        h.addWidget(icon)
        l = QLabel(text)
        l.setStyleSheet("font-weight:600;")
        h.addWidget(l)
        self.setStyleSheet(
            "background: rgba(255,255,255,0.05); border-radius: 18px;"
        )

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(ev)
