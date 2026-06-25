"""国家队总览页：所有 48 支球队的卡片网格。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.team import Team
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.card_grid import CardGrid
from app.ui.widgets.misc import Card
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class _TeamCard(Card):
    clicked = pyqtSignal(str)

    def __init__(self, team: Team) -> None:
        super().__init__(padding=14)
        self._team = team
        self.setFixedSize(220, 156)
        self.setCursor(pointing_hand_cursor())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(TeamLogo(team.logo, size=44, shape="circle"))
        col = QVBoxLayout()
        col.setSpacing(2)
        name = QLabel(team.name)
        name.setStyleSheet("font-size: 14px; font-weight: 700;")
        col.addWidget(name)
        if team.group:
            grp = QLabel(team.group)
            grp.setStyleSheet(
                "background: rgba(106,90,205,0.20); color:#B7AEFF;"
                "font-size:11px; padding:2px 8px; border-radius:8px;"
            )
            grp.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            col.addWidget(grp)
        head.addLayout(col)
        head.addStretch(1)
        layout.addLayout(head)

        # stats
        stats = QHBoxLayout()
        stats.setSpacing(10)
        for label, value in (
            ("名次", f"#{team.rank or '—'}"),
            ("分", str(team.points if team.points is not None else "—")),
            ("净胜", _gd_text(team)),
        ):
            box = QVBoxLayout()
            box.setSpacing(2)
            v = QLabel(value)
            v.setStyleSheet("font-size:15px; font-weight:800; color:#FFD700;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l = QLabel(label)
            l.setStyleSheet("color:#B0BEC5; font-size:11px;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.addWidget(v)
            box.addWidget(l)
            wrap = QWidget(); wrap.setLayout(box)
            stats.addWidget(wrap)
        layout.addLayout(stats)
        layout.addStretch(1)

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._team.team_id)
        super().mousePressEvent(ev)


def _gd_text(team: Team) -> str:
    gd = team.goal_diff
    if gd is None:
        return "—"
    return f"+{gd}" if gd > 0 else str(gd)


class TeamsPage(BasePage):
    title = "国家队"
    subtitle = "本届杯赛全部参赛队伍 · 点击进入详情"

    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._all: list[Team] = []

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

        # 搜索栏
        head = Card(padding=12, shadow=False)
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(16, 8, 16, 8)
        title = QLabel("🛡️  国家队总览")
        title.setStyleSheet("font-size:16px; font-weight:800;")
        h_lay.addWidget(title)
        h_lay.addStretch(1)
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  搜索球队名（中文）...")
        self._search.setMinimumWidth(260)
        self._search.textChanged.connect(self._render)
        h_lay.addWidget(self._search)
        outer.addWidget(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        self._grid = CardGrid(220, 156, h_spacing=14, v_spacing=14)
        scroll.setWidget(self._grid)

    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            groups, _ko, _km = await self._service.fetch_standings(force=force)
            self._all = self._service.teams_from_standings(groups)
            self._render()

        self.run_async(runner)

    def _render(self) -> None:
        self._grid.clear()
        q = self._search.text().strip().lower()
        items = (
            [t for t in self._all if q in t.name.lower()] if q else list(self._all)
        )
        items.sort(key=lambda t: ((t.group or "Z"), t.rank or 99))
        cards = []
        for t in items:
            card = _TeamCard(t)
            card.clicked.connect(self.team_clicked.emit)
            cards.append(card)
        self._grid.add_cards(cards)
