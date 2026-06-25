"""球队数据榜页：懂球帝全量球队数据（进球 / 失球 / 角球 / 越位 / 身价 …）。

布局与球员榜一致：顶部「分类」分段按钮 + 第二行「榜单」按钮 + 正文榜单列表。
点击任一球队行进入球队详情。数据来源：懂球帝 ``team_ranking`` 接口。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.player import RankingType, TeamRanking
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.team_rank_row import TeamRankRow
from app.ui.design.app_cursor import pointing_hand_cursor

log = logging.getLogger(__name__)

_PRIMARY = "#00BFFF"
_DIM = "#B0BEC5"


def _cat_qss(active: bool) -> str:
    if active:
        return (
            "QPushButton{background:" + _PRIMARY + "; color:#fff; border:none;"
            " border-radius:11px; font-size:13px; font-weight:900; padding:7px 16px;}"
        )
    return (
        "QPushButton{background: rgba(255,255,255,0.05); color:" + _DIM + ";"
        " border:1px solid rgba(255,255,255,0.10); border-radius:11px;"
        " font-size:13px; font-weight:700; padding:7px 16px;}"
        "QPushButton:hover{background: rgba(255,255,255,0.10); color:#fff;}"
    )


def _stat_qss(active: bool) -> str:
    if active:
        return (
            "QPushButton{background: rgba(0,191,255,0.18); color:#fff;"
            " border:1px solid " + _PRIMARY + "; border-radius:10px;"
            " font-size:12.5px; font-weight:800; padding:6px 14px;}"
        )
    return (
        "QPushButton{background: transparent; color:" + _DIM + ";"
        " border:1px solid rgba(255,255,255,0.10); border-radius:10px;"
        " font-size:12.5px; font-weight:600; padding:6px 14px;}"
        "QPushButton:hover{background: rgba(255,255,255,0.07); color:#fff;}"
    )


class TeamRankingsPage(BasePage):
    """球队全量数据榜（分类 + 榜单二级切换）。"""

    title = "球队数据榜"
    subtitle = "TEAM RANKINGS · 懂球帝数据"

    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._grouped = RankingType.grouped(scope="team")
        self._active_cat = self._grouped[0][0] if self._grouped else ""
        self._active_rtype = RankingType.GOALS

        host = self.content_widget()
        root = QVBoxLayout(host)
        root.setContentsMargins(24, 18, 24, 0)
        root.setSpacing(12)

        # 一级：分类
        cat_bar = QHBoxLayout()
        cat_bar.setSpacing(8)
        self._cat_btns: dict[str, QPushButton] = {}
        for cat, _types in self._grouped:
            b = QPushButton(cat)
            b.setCheckable(True)
            b.setCursor(pointing_hand_cursor())
            b.clicked.connect(lambda _c=False, c=cat: self._select_category(c))
            self._cat_btns[cat] = b
            cat_bar.addWidget(b)
        cat_bar.addStretch(1)
        root.addLayout(cat_bar)

        # 二级：榜单（横向可滚动）
        self._stat_bar_host = QWidget()
        self._stat_bar = QHBoxLayout(self._stat_bar_host)
        self._stat_bar.setContentsMargins(0, 0, 0, 0)
        self._stat_bar.setSpacing(8)
        stat_scroll = QScrollArea()
        stat_scroll.setWidgetResizable(True)
        stat_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        stat_scroll.setFixedHeight(46)
        stat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        stat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        stat_scroll.setWidget(self._stat_bar_host)
        root.addWidget(stat_scroll)
        self._stat_btns: dict[RankingType, QPushButton] = {}

        # 正文：榜单滚动列表
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root.addWidget(self._scroll, 1)
        self._list_layout: QVBoxLayout | None = None

        self._select_category(self._active_cat, load=False)

    # ─────────────────────────────────────────
    def _select_category(self, cat: str, *, load: bool = True) -> None:
        self._active_cat = cat
        for name, b in self._cat_btns.items():
            b.setChecked(name == cat)
            b.setStyleSheet(_cat_qss(name == cat))

        while self._stat_bar.count():
            it = self._stat_bar.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
        self._stat_btns.clear()

        types = next((t for c, t in self._grouped if c == cat), [])
        for rt in types:
            b = QPushButton(f"{rt.emoji} {rt.label}")
            b.setCheckable(True)
            b.setCursor(pointing_hand_cursor())
            b.clicked.connect(lambda _c=False, r=rt: self._select_rtype(r))
            self._stat_btns[rt] = b
            self._stat_bar.addWidget(b)
        self._stat_bar.addStretch(1)

        if types:
            target = self._active_rtype if self._active_rtype in types else types[0]
            self._select_rtype(target, load=load)

    def _select_rtype(self, rtype: RankingType, *, load: bool = True) -> None:
        self._active_rtype = rtype
        for rt, b in self._stat_btns.items():
            b.setChecked(rt == rtype)
            b.setStyleSheet(_stat_qss(rt == rtype))
        if load:
            self.refresh(force=False)

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        rtype = self._active_rtype

        async def runner() -> None:
            data = await self._service.fetch_team_ranking(rtype, force=force)
            self._render(data)

        self.run_async(runner)

    def _build_host(self) -> None:
        host = QWidget()
        self._scroll.setWidget(host)
        self._list_layout = QVBoxLayout(host)
        self._list_layout.setContentsMargins(2, 4, 2, 16)
        self._list_layout.setSpacing(10)

    def _render(self, data: list[TeamRanking]) -> None:
        self._build_host()
        if not data:
            empty = QLabel("暂无数据 ⚽")
            empty.setStyleSheet("color:#B0BEC5; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
            self._list_layout.addStretch(1)
            return
        max_count = max((t.value or 0) for t in data) or 1.0
        rows: list[QWidget] = []
        for t in data:
            row = TeamRankRow(t, max_count)
            row.team_clicked.connect(self.team_clicked.emit)
            self._list_layout.addWidget(row)
            rows.append(row)
        self._list_layout.addStretch(1)
        stagger_fade(rows[:16], step=30, dx=0, dy=0)
