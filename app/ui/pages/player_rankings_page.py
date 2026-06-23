"""球员榜单页：射手榜 / 助攻榜 / 黄牌榜 三榜合一（顶部选项卡切换）。

把原先分散在 MainWindow 中的三个 ``RankingPage`` 收纳进一个带选项卡的
容器页，让「球员」导航入口一次性提供进球、助攻、黄牌三类榜单。各选项卡
**懒加载**：只有首次切到该榜时才发起网络请求，避免一次性拉三份数据。
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from app.models.player import PlayerRanking, RankingType
from app.services.data_service import DataService
from app.ui.pages.scorers_page import RankingPage


class PlayerRankingsPage(QWidget):
    """球员榜单总览：射手榜 / 助攻榜 / 黄牌榜。"""

    title = "球员榜单"
    subtitle = "PLAYER RANKINGS"

    player_clicked = pyqtSignal(PlayerRanking)
    team_clicked = pyqtSignal(str)

    # 选项卡顺序：进球 → 助攻 → 黄牌
    _RTYPES: tuple[RankingType, ...] = (
        RankingType.GOALS,
        RankingType.ASSISTS,
        RankingType.YELLOW_CARDS,
    )

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._pages: dict[int, RankingPage] = {}
        self._loaded: set[int] = set()
        for rtype in self._RTYPES:
            page = RankingPage(service, rtype)
            page.player_clicked.connect(self.player_clicked.emit)
            page.team_clicked.connect(self.team_clicked.emit)
            idx = self._tabs.addTab(page, f"{rtype.emoji}  {rtype.label}")
            self._pages[idx] = page

        self._tabs.currentChanged.connect(self._on_tab_changed)

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        """刷新当前选项卡（首次进入或强制刷新时拉取数据）。"""
        idx = self._tabs.currentIndex()
        page = self._pages.get(idx)
        if page is None:
            return
        if force or idx not in self._loaded:
            page.refresh(force=force)
            self._loaded.add(idx)

    def _on_tab_changed(self, idx: int) -> None:
        page = self._pages.get(idx)
        if page is None:
            return
        if idx not in self._loaded:
            page.refresh(force=False)
            self._loaded.add(idx)
