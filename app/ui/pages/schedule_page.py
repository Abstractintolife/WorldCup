"""赛程页：按轮次 / 日期 / 状态过滤所有比赛 —— 精致卡片网格。"""
from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus, Round
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.match_card import MatchCard
from app.ui.widgets.misc import Card
from app.utils.time_utils import to_local

log = logging.getLogger(__name__)

_STATUS_OPTIONS: list[tuple[str, str]] = [
    ("all", "全部状态"),
    ("live", "🔴 进行中"),
    ("upcoming", "⏳ 未开赛"),
    ("played", "✅ 已结束"),
]


class SchedulePage(BasePage):
    title = "赛程大厅"
    subtitle = "MATCH SCHEDULE"

    match_clicked = pyqtSignal(Match)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._all_matches: list[Match] = []
        self._rounds: list[Round] = []

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(14)

        # 过滤栏
        filters = Card(padding=12, shadow=False)
        flayout = QHBoxLayout(filters)
        flayout.setContentsMargins(16, 8, 16, 8)
        flayout.setSpacing(12)

        title = QLabel("📅  赛程大厅")
        title.setStyleSheet("font-size:15px; font-weight:900;")
        flayout.addWidget(title)

        flayout.addSpacing(14)

        self._round_combo = QComboBox()
        self._round_combo.addItem("所有轮次", None)
        flayout.addWidget(self._round_combo)

        self._status_combo = QComboBox()
        for k, v in _STATUS_OPTIONS:
            self._status_combo.addItem(v, k)
        # 默认聚焦「未开赛」—— 进入赛程中心即展示即将到来的比赛
        for i in range(self._status_combo.count()):
            if self._status_combo.itemData(i) == "upcoming":
                self._status_combo.setCurrentIndex(i)
                break
        flayout.addWidget(self._status_combo)

        self._date_combo = QComboBox()
        self._date_combo.addItem("所有日期", None)
        flayout.addWidget(self._date_combo)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍   搜索球队 / match_id ...")
        self._search.setMinimumWidth(220)
        flayout.addWidget(self._search)
        flayout.addStretch(1)

        self._summary = QLabel("0 场")
        self._summary.setStyleSheet(
            "color:#46D2FF; font-size:12px; font-weight:800;"
            "background: rgba(0,191,255,0.14); border-radius:9px; padding:4px 10px;"
        )
        flayout.addWidget(self._summary)
        outer.addWidget(filters)

        # 比赛列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        self._body_layout = QVBoxLayout(body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(20)

        # 信号
        self._round_combo.currentIndexChanged.connect(self._reapply)
        self._status_combo.currentIndexChanged.connect(self._reapply)
        self._date_combo.currentIndexChanged.connect(self._reapply)
        self._search.textChanged.connect(self._reapply)

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            import asyncio
            from app.services.fifa_rankings import FifaRankings
            rounds, matches = await self._service.fetch_full_schedule(force=force)
            # 同步拉取国际足联世界排名（供对阵卡国旗旁标注名次）；失败不影响赛程渲染。
            try:
                await FifaRankings.instance().refresh(force=force)
            except Exception:  # pragma: no cover
                pass
            self._rounds = rounds
            self._all_matches = matches
            self._populate_round_combo()
            self._populate_date_combo()
            self._render()
        self.run_async(runner)

    def _populate_round_combo(self) -> None:
        self._round_combo.blockSignals(True)
        current = self._round_combo.currentData()
        self._round_combo.clear()
        self._round_combo.addItem("所有轮次", None)
        for r in self._rounds:
            label = r.name + (" ★" if r.current else "")
            self._round_combo.addItem(label, (r.round_id, r.gameweek))
        for i in range(self._round_combo.count()):
            if self._round_combo.itemData(i) == current:
                self._round_combo.setCurrentIndex(i)
                break
        self._round_combo.blockSignals(False)

    def _populate_date_combo(self) -> None:
        self._date_combo.blockSignals(True)
        current = self._date_combo.currentData()
        self._date_combo.clear()
        self._date_combo.addItem("所有日期", None)
        # 用本地日期做唯一键，确保用户看到的「日期分组」与显示一致
        seen: set[str] = set()
        for m in self._all_matches:
            local = to_local(m.start_play)
            if local is None:
                continue
            key = local.strftime("%Y-%m-%d")
            if key in seen:
                continue
            seen.add(key)
        for d in sorted(seen):
            self._date_combo.addItem(d, d)
        for i in range(self._date_combo.count()):
            if self._date_combo.itemData(i) == current:
                self._date_combo.setCurrentIndex(i)
                break
        self._date_combo.blockSignals(False)

    # ─────────────────────────────────────────
    def _reapply(self, *_args) -> None:
        self._render()

    def _filtered(self) -> list[Match]:
        out = list(self._all_matches)
        rd = self._round_combo.currentData()
        if rd:
            round_id, _ = rd
            out = [m for m in out if str(m.round_id) == str(round_id)]
        st = self._status_combo.currentData()
        if st == "live":
            out = [m for m in out if m.is_live]
        elif st == "upcoming":
            out = [m for m in out if m.status == MatchStatus.FIXTURE]
        elif st == "played":
            out = [m for m in out if m.status == MatchStatus.PLAYED]
        date = self._date_combo.currentData()
        if date:
            out = [
                m for m in out
                if to_local(m.start_play)
                and to_local(m.start_play).strftime("%Y-%m-%d") == date
            ]
        q = self._search.text().strip().lower()
        if q:
            out = [
                m
                for m in out
                if q in m.team_a_name.lower()
                or q in m.team_b_name.lower()
                or q in m.match_id.lower()
            ]
        return out

    def _render(self) -> None:
        # 清空
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        matches = self._filtered()
        self._summary.setText(f"共 {len(matches)} 场")
        if not matches:
            empty = QLabel("没有符合条件的比赛 🤔")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color:#B0BEC5; padding: 40px;")
            self._body_layout.addWidget(empty)
            self._body_layout.addStretch(1)
            return

        # 按本地日期分组（与时区同步）
        groups: dict[str, list[Match]] = OrderedDict()
        # 按时间排序
        for m in sorted(matches, key=lambda x: x.start_play or datetime.max.replace(
                tzinfo=__import__("datetime").timezone.utc)):
            local = to_local(m.start_play)
            key = local.strftime("%Y-%m-%d") if local else "—"
            groups.setdefault(key, []).append(m)

        all_cards: list[QWidget] = []
        for date_key, items in groups.items():
            section = Card(padding=18, glow_color="#00BFFF")
            sec_lay = QVBoxLayout(section)
            sec_lay.setContentsMargins(20, 14, 20, 18)
            sec_lay.setSpacing(12)

            try:
                dt = datetime.strptime(date_key, "%Y-%m-%d")
                from app.utils.time_utils import WEEKDAYS_ZH
                date_text = dt.strftime("%m月%d日") + " " + WEEKDAYS_ZH[dt.weekday()]
            except (ValueError, TypeError):
                date_text = date_key
            title = QLabel(f"📅  {date_text}    ·    {len(items)} 场")
            title.setStyleSheet("font-size: 15px; font-weight: 900; color:#46D2FF;")
            sec_lay.addWidget(title)

            grid = FlowLayout()
            for m in items:
                card = MatchCard(m)
                card.clicked.connect(self.match_clicked.emit)
                grid.addWidget(card)
                all_cards.append(card)
            sec_lay.addLayout(grid)

            self._body_layout.addWidget(section)

        self._body_layout.addStretch(1)
        # 入场动画（纯淡入，避免长列表逐行位移造成的卡顿）
        stagger_fade(all_cards[:24], step=22, dx=0, dy=0)
