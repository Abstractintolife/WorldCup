"""收藏夹：球队 / 球员 / 比赛分别一栏。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match
from app.models.player import RankingType
from app.services.data_service import DataService
from app.services.favorites import Favorites
from app.ui.pages.base import BasePage
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.match_card import MatchCard
from app.ui.widgets.misc import Card
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class FavoritesPage(BasePage):
    title = "收藏夹"
    subtitle = "我的关注 · 球队 / 球员 / 比赛"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)

    def __init__(self, service: DataService, favorites: Favorites) -> None:
        super().__init__()
        self._service = service
        self._fav = favorites

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(12)

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs)

        self._team_layout = self._tab_with_grid("球队")
        self._player_layout = self._tab_with_grid("球员")
        self._match_layout = self._tab_with_grid("比赛")

    def _tab_with_grid(self, title: str) -> FlowLayout:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        scroll.setWidget(body)
        flow = FlowLayout(margin=10, h_spacing=12, v_spacing=12)
        body.setLayout(flow)
        self._tabs.addTab(scroll, title)
        return flow

    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            groups, _ko, _km = await self._service.fetch_standings(force=force)
            _rounds, matches = await self._service.fetch_full_schedule(force=force)
            scorers = await self._service.fetch_ranking(RankingType.GOALS, force=force)
            assists = await self._service.fetch_ranking(RankingType.ASSISTS, force=force)
            all_players = {p.person_id: p for p in scorers + assists}
            teams_map = {
                t.team_id: t
                for g in groups
                for t in g.teams
            }
            self._render(matches, teams_map, all_players)

        self.run_async(runner)

    def _render(self, matches, teams_map, all_players) -> None:
        # 清空各 tab
        for layout in (self._team_layout, self._player_layout, self._match_layout):
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

        # 球队
        team_ids = self._fav.list("team")
        if not team_ids:
            self._team_layout.addWidget(self._empty("尚未收藏任何球队"))
        else:
            for tid in team_ids:
                t = teams_map.get(tid)
                if not t:
                    continue
                w = _FavTeamChip(tid, t.team_name, t.team_logo)
                w.clicked.connect(self.team_clicked.emit)
                self._team_layout.addWidget(w)

        # 球员
        pids = self._fav.list("player")
        if not pids:
            self._player_layout.addWidget(self._empty("尚未收藏任何球员"))
        else:
            for pid in pids:
                p = all_players.get(pid)
                if not p:
                    continue
                w = _FavPlayerChip(pid, p.person_name, p.person_logo, p.team_name)
                w.clicked.connect(self.player_clicked.emit)
                self._player_layout.addWidget(w)

        # 比赛
        mids = set(self._fav.list("match"))
        match_objs = [m for m in matches if m.match_id in mids]
        if not match_objs:
            self._match_layout.addWidget(self._empty("尚未收藏任何比赛"))
        else:
            for m in match_objs:
                card = MatchCard(m)
                card.clicked.connect(self.match_clicked.emit)
                self._match_layout.addWidget(card)

    def _empty(self, msg: str) -> QLabel:
        l = QLabel(msg + " 💛")
        l.setStyleSheet("color:#B0BEC5; padding: 40px;")
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return l


class _FavTeamChip(Card):
    clicked = pyqtSignal(str)

    def __init__(self, team_id: str, name: str, logo: str | None) -> None:
        super().__init__(padding=10)
        self._tid = team_id
        self.setFixedSize(180, 70)
        self.setCursor(pointing_hand_cursor())
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(10)
        h.addWidget(TeamLogo(logo, size=42, shape="circle"))
        n = QLabel(name)
        n.setStyleSheet("font-weight:700;")
        h.addWidget(n)
        h.addStretch(1)

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._tid)
        super().mousePressEvent(ev)


class _FavPlayerChip(Card):
    clicked = pyqtSignal(str, str)

    def __init__(
        self, person_id: str, name: str, logo: str | None, team: str
    ) -> None:
        super().__init__(padding=10)
        self._pid = person_id
        self._name = name
        self.setFixedSize(220, 70)
        self.setCursor(pointing_hand_cursor())
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(10)
        h.addWidget(PlayerAvatar(logo, size=42))
        col = QVBoxLayout()
        col.setSpacing(2)
        n = QLabel(name)
        n.setStyleSheet("font-weight:700;")
        col.addWidget(n)
        t = QLabel(team)
        t.setStyleSheet("color:#B0BEC5; font-size:11px;")
        col.addWidget(t)
        h.addLayout(col)
        h.addStretch(1)

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._pid, self._name)
        super().mousePressEvent(ev)
