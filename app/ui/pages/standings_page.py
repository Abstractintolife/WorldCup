"""积分榜页：A-L 12 个组别卡片 + 淘汰赛对阵 —— 精致玻璃化版本。"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.data_service import DataService
from app.models.standing import GroupStanding, TeamStanding
from app.ui.pages.base import BasePage
from app.ui.theme import THEMES, ThemePalette
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.group_card import GroupCard
from app.ui.widgets.misc import Card
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor

log = logging.getLogger(__name__)


class StandingsPage(BasePage):
    title = "积分榜"
    subtitle = "STANDINGS"

    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._theme: ThemePalette = THEMES["dark"]

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(12)

        # 头部介绍
        head = Card(padding=18, glow_color="#FFD700")
        h_lay = QVBoxLayout(head)
        h_lay.setContentsMargins(22, 14, 22, 14)
        h_lay.setSpacing(6)
        title = QLabel("🏆  小组赛积分榜")
        title.setStyleSheet("font-size: 18px; font-weight: 900;")
        h_lay.addWidget(title)
        sub = QLabel(
            "48 队分 12 组 · 各组前 2 名直接晋级 + 8 个最佳第 3 名 = 32 强淘汰赛 · "
            "点击任一队进入球队详情"
        )
        sub.setStyleSheet("color:#B0BEC5; font-size: 12px; font-weight: 600;")
        h_lay.addWidget(sub)

        # 晋级图例
        legend = QLabel(
            "🟢 直接晋级（小组前 2）　　🔵 最佳第三名晋级　　"
            "排序：积分 › 净胜球 › 进球数 › 公平竞赛分 › FIFA 排名"
        )
        legend.setStyleSheet("color:#8A96A8; font-size: 11px; font-weight: 600;")
        h_lay.addWidget(legend)
        outer.addWidget(head)

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs)

        # tab 1：小组赛
        self._groups_scroll = QScrollArea()
        self._groups_scroll.setWidgetResizable(True)
        self._groups_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._groups_widget = QWidget()
        self._groups_scroll.setWidget(self._groups_widget)
        # 一排三个：固定 3 列等宽栅格
        self._groups_cols = 3
        self._groups_grid = QGridLayout(self._groups_widget)
        self._groups_grid.setContentsMargins(4, 4, 4, 4)
        self._groups_grid.setHorizontalSpacing(14)
        self._groups_grid.setVerticalSpacing(14)
        for c in range(self._groups_cols):
            self._groups_grid.setColumnStretch(c, 1)
        self._tabs.addTab(self._groups_scroll, "🏆 小组赛")

        # tab 2：淘汰赛对阵
        self._knockout_scroll = QScrollArea()
        self._knockout_scroll.setWidgetResizable(True)
        self._knockout_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._knockout_widget = QWidget()
        self._knockout_scroll.setWidget(self._knockout_widget)
        self._knockout_layout = QVBoxLayout(self._knockout_widget)
        self._knockout_layout.setContentsMargins(0, 8, 0, 8)
        self._knockout_layout.setSpacing(12)
        self._tabs.addTab(self._knockout_scroll, "⚔️ 淘汰赛对阵")

    def set_theme(self, palette: ThemePalette) -> None:
        self._theme = palette

    # ─────────────────────────────────────────
    @staticmethod
    def _mark_qualifiers(groups: list[GroupStanding]) -> None:
        """按 2026 世界杯新赛制标注晋级球队。

        规则
        ----
        * 每组前 2 名直接晋级（共 24 队）→ ``qualify="direct"``。
        * 12 个小组的第 3 名再按以下优先级排序，取前 8 名晋级
          （共 8 队）→ ``qualify="best3"``：
          总积分 › 总净胜球 › 总进球数 ›（公平竞赛分 / FIFA 排名暂无数据）。
        合计 32 队进入淘汰赛。
        """
        thirds: list[TeamStanding] = []
        for g in groups:
            for t in g.teams:
                t.qualify = None
            for t in g.teams:
                if t.rank in (1, 2):
                    t.qualify = "direct"
                elif t.rank == 3:
                    thirds.append(t)
        # 最佳第三名排序：积分 → 净胜球 → 进球数（降序）
        thirds.sort(
            key=lambda t: (t.points, t.goal_diff, t.goals_pro),
            reverse=True,
        )
        for t in thirds[:8]:
            t.qualify = "best3"

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            groups, knockouts, _km = await self._service.fetch_standings(force=force)
            self._mark_qualifiers(groups)

            while self._groups_grid.count():
                item = self._groups_grid.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            cards: list[QWidget] = []
            for idx, g in enumerate(groups):
                gc = GroupCard(g, self._theme)
                gc.team_clicked.connect(self.team_clicked.emit)
                gc.setMinimumWidth(300)
                gc.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                self._groups_grid.addWidget(
                    gc, idx // self._groups_cols, idx % self._groups_cols
                )
                cards.append(gc)
            stagger_fade(cards, step=30, dx=0, dy=0)

            # knockouts
            while self._knockout_layout.count():
                item = self._knockout_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            if not knockouts:
                empty = QLabel("淘汰赛对阵尚未公布 🤔")
                empty.setStyleSheet("color:#B0BEC5; padding: 40px;")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._knockout_layout.addWidget(empty)
            else:
                for tie in knockouts:
                    self._knockout_layout.addWidget(self._knockout_card(tie))
                self._knockout_layout.addStretch(1)

        self.run_async(runner)

    def _knockout_card(self, tie) -> Card:
        card = Card(padding=18, glow_color="#46D2FF")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 14, 22, 14)
        layout.setSpacing(14)

        a = QHBoxLayout()
        a.setSpacing(10)
        a.addWidget(TeamLogo(tie.team_a_logo, size=42, shape="circle"))
        a_lbl = QLabel(tie.team_a_name)
        a_lbl.setStyleSheet("font-weight: 800; font-size: 14px;")
        a.addWidget(a_lbl)
        a.addStretch(1)
        a_w = QWidget(); a_w.setLayout(a)
        a_w.setCursor(pointing_hand_cursor())
        a_w.mousePressEvent = lambda _e, t=tie.team_a_id: self.team_clicked.emit(t)  # type: ignore[assignment]
        layout.addWidget(a_w, 4)

        score = QLabel(tie.total_score or "vs")
        score.setStyleSheet("font-size: 20px; font-weight: 900; color: #FFD700;")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(score, 2)

        b = QHBoxLayout()
        b.setSpacing(10)
        b.addStretch(1)
        b_lbl = QLabel(tie.team_b_name)
        b_lbl.setStyleSheet("font-weight: 800; font-size: 14px;")
        b.addWidget(b_lbl)
        b.addWidget(TeamLogo(tie.team_b_logo, size=42, shape="circle"))
        b_w = QWidget(); b_w.setLayout(b)
        b_w.setCursor(pointing_hand_cursor())
        b_w.mousePressEvent = lambda _e, t=tie.team_b_id: self.team_clicked.emit(t)  # type: ignore[assignment]
        layout.addWidget(b_w, 4)

        return card
