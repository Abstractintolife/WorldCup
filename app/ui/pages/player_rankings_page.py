"""球员榜单页：懂球帝全量球员数据榜单（射手 / 助攻 / 射门 / 传球 /
抢断 / 门将 / 评分 …）。

布局
-----
* 顶部「分类」分段按钮：进攻 / 创造 / 传球 / 过人 / 防守 / 对抗 / 纪律 /
  门将 / 综合。
* 第二行「榜单」按钮：随所选分类动态切换（如「进攻」下含 射手榜 / 射门 /
  射正 / 错失绝佳机会）。
* 正文复用单个 :class:`RankingPage`，点击榜单按钮即 ``set_rtype`` 切换并
  拉取数据（数据层有缓存，切换近乎秒回）。

数据来源：懂球帝 ``person_ranking`` 接口（``type`` 取各榜单枚举值）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.player import PlayerRanking, RankingType
from app.services.data_service import DataService
from app.ui.pages.scorers_page import RankingPage
from app.ui.design.app_cursor import pointing_hand_cursor

_PRIMARY = "#00BFFF"
_DIM = "#B0BEC5"


def _cat_button_qss(active: bool) -> str:
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


def _stat_button_qss(active: bool) -> str:
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


class PlayerRankingsPage(QWidget):
    """球员全量数据榜单（分类 + 榜单二级切换）。"""

    title = "球员榜单"
    subtitle = "PLAYER RANKINGS · 懂球帝数据"

    player_clicked = pyqtSignal(PlayerRanking)
    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        self._service = service
        self._grouped = RankingType.grouped()
        self._active_cat = self._grouped[0][0] if self._grouped else ""
        self._active_rtype = RankingType.GOALS
        self._loaded = False

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 18, 24, 0)
        root.setSpacing(12)

        # ── 一级：分类分段按钮 ──────────────────
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

        # ── 二级：榜单按钮（横向可滚动，避免溢出）──
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

        # ── 正文：单个可切换的榜单页 ──────────────
        self._page = RankingPage(service, RankingType.GOALS)
        self._page.player_clicked.connect(self.player_clicked.emit)
        self._page.team_clicked.connect(self.team_clicked.emit)
        root.addWidget(self._page, 1)

        # 初始化分类按钮高亮 + 榜单按钮
        self._select_category(self._active_cat, load=False)

    # ─────────────────────────────────────────
    def _select_category(self, cat: str, *, load: bool = True) -> None:
        self._active_cat = cat
        for name, b in self._cat_btns.items():
            b.setChecked(name == cat)
            b.setStyleSheet(_cat_button_qss(name == cat))

        # 重建该分类下的榜单按钮
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

        # 选中该分类的第一个榜单（若当前榜单不在此分类）
        if types:
            target = self._active_rtype if self._active_rtype in types else types[0]
            self._select_rtype(target, load=load)

    def _select_rtype(self, rtype: RankingType, *, load: bool = True) -> None:
        self._active_rtype = rtype
        for rt, b in self._stat_btns.items():
            b.setChecked(rt == rtype)
            b.setStyleSheet(_stat_button_qss(rt == rtype))
        if load:
            self._page.set_rtype(rtype)
            self._loaded = True

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        """首次进入时加载当前榜单；强制刷新时重拉当前榜单。"""
        if not self._loaded or force:
            self._page.set_rtype(self._active_rtype, force=force)
            self._loaded = True
