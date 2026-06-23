"""仪表盘首页：英雄横幅 + 关键指标 + 直播 / 焦点比赛 + 当家球星。

V3 旗舰版
----------
* 统一用 :class:`SectionHeader` 划分区块，建立清晰的排版层级与节奏。
* 指标卡片改为「彩色图标徽章 + 大号 count-up 数字 + 中英双标签 + 底部
  细色条」的高级样式，悬停时整卡发光浮起（Card 自带）。
* 全局动效由 ``FrameClock`` 统一驱动（最高 240FPS），动态背景透出毛玻璃卡片。

增量刷新设计
-------------
home_page 走 ``BasePage`` 的增量刷新模型：首屏显示加载态，之后每 30 秒
自动刷新或手动刷新时仅顶部出现霓虹同步条，卡片数值用 count-up 平滑滚动。
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.models.player import RankingType
from app.models.standing import GroupStanding
from app.services.data_service import DataService
from app.services.prediction import build_prediction
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.hero_banner import HeroBanner
from app.ui.widgets.match_card import MatchCard
from app.ui.widgets.misc import Card, CountUpLabel, SectionHeader
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.widgets.team_logo import TeamLogo

log = logging.getLogger(__name__)


class HomePage(BasePage):
    """仪表盘首页。"""

    title = "仪表盘"
    subtitle = "DASHBOARD · 实时聚合赛程 / 积分 / 射手 / 球队 / 球场"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)  # person_id, person_name
    prediction_clicked = pyqtSignal(Match)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 28)
        body_layout.setSpacing(20)

        # ── 英雄横幅 ──────────
        self._hero = HeroBanner()
        body_layout.addWidget(self._hero)

        # ── 赛事概览 ──────────
        body_layout.addWidget(
            SectionHeader(
                "赛事概览", "TOURNAMENT PULSE",
                accent="#00BFFF", hint="数据每 30 秒自动同步",
            )
        )
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self._stat_total = self._make_stat("总比赛", "TOTAL", "🗓", "#00BFFF")
        self._stat_done = self._make_stat("已结束", "PLAYED", "✅", "#2ED877")
        self._stat_live = self._make_stat("直播中", "LIVE", "🔴", "#FF3057")
        self._stat_upcoming = self._make_stat("待开赛", "UPCOMING", "⏳", "#FFD700")
        for s in (
            self._stat_total,
            self._stat_done,
            self._stat_live,
            self._stat_upcoming,
        ):
            stats_row.addWidget(s, 1)
        body_layout.addLayout(stats_row)

        # ── 进球风暴（数据速览） ──────────
        storm_row = QHBoxLayout()
        storm_row.setSpacing(16)
        self._stat_goals = self._make_mini_stat("总进球", "GOALS", "⚽", "#FF8A3D")
        self._stat_avg = self._make_mini_stat("场均进球", "AVG / GAME", "📈", "#2ED877")
        self._stat_big = self._make_mini_stat("大球率 ≥3", "OVER 2.5", "🔥", "#FF3057")
        self._stat_btts = self._make_mini_stat("双方进球率", "BTTS", "🤝", "#00BFFF")
        for s in (self._stat_goals, self._stat_avg, self._stat_big, self._stat_btts):
            storm_row.addWidget(s, 1)
        body_layout.addLayout(storm_row)

        # ── 现在的赛场 ──────────
        body_layout.addWidget(
            SectionHeader("现在的赛场", "LIVE NOW", accent="#FF3057")
        )
        live_card = Card(padding=18, glow_color="#FF3057")
        live_lay = QVBoxLayout(live_card)
        live_lay.setContentsMargins(18, 14, 18, 14)
        live_lay.setSpacing(10)
        self._live_grid = FlowLayout()
        live_lay.addLayout(self._live_grid)
        self._live_empty = QLabel("当前没有正在进行的比赛 —— 下方为下一场即将开赛的对决 👇")
        self._live_empty.setStyleSheet("color:#B0BEC5; font-size:13px;")
        self._live_empty.setVisible(False)
        live_lay.addWidget(self._live_empty)
        body_layout.addWidget(live_card)

        # ── 当家球星：射手榜 / 助攻榜 ──────────
        body_layout.addWidget(
            SectionHeader("当家球星", "TOP PERFORMERS", accent="#FFD700")
        )
        leaders_row = QHBoxLayout()
        leaders_row.setSpacing(16)
        self._scorers_card, self._scorers_box = self._make_leaders_card(
            "⚽  射手榜 TOP 3", "#00BFFF"
        )
        self._assists_card, self._assists_box = self._make_leaders_card(
            "🅰️  助攻榜 TOP 3", "#FFD700"
        )
        leaders_row.addWidget(self._scorers_card, 1)
        leaders_row.addWidget(self._assists_card, 1)
        body_layout.addLayout(leaders_row)

        # ── 夺冠热门 · 实力榜 ──────────
        body_layout.addWidget(
            SectionHeader(
                "夺冠热门 · 实力榜", "POWER RANKINGS",
                accent="#FFD700", hint="按积分 / 净胜球综合排序",
            )
        )
        power_card = Card(padding=18, glow_color="#FFD700")
        power_lay = QVBoxLayout(power_card)
        power_lay.setContentsMargins(18, 14, 18, 14)
        power_lay.setSpacing(10)
        self._power_grid = FlowLayout()
        power_lay.addLayout(self._power_grid)
        self._power_empty = QLabel("积分榜数据加载中…")
        self._power_empty.setStyleSheet("color:#B0BEC5; font-size:13px;")
        self._power_empty.setVisible(False)
        power_lay.addWidget(self._power_empty)
        body_layout.addWidget(power_card)

        # ── AI 预测精选 ──────────
        body_layout.addWidget(
            SectionHeader(
                "AI 预测精选", "MATCH OF THE DAY",
                accent="#6A5ACD", hint="点击查看完整赛前预测",
            )
        )
        self._featured_card = Card(padding=18, glow_color="#6A5ACD")
        self._featured_lay = QVBoxLayout(self._featured_card)
        self._featured_lay.setContentsMargins(20, 16, 20, 16)
        self._featured_lay.setSpacing(10)
        body_layout.addWidget(self._featured_card)

        # ── 即将开赛 ──────────
        body_layout.addWidget(
            SectionHeader("即将开赛", "UP NEXT", accent="#6A5ACD")
        )
        upcoming_card = Card(padding=18, glow_color="#6A5ACD")
        up_lay = QVBoxLayout(upcoming_card)
        up_lay.setContentsMargins(18, 14, 18, 14)
        up_lay.setSpacing(10)
        self._upcoming_grid = FlowLayout()
        up_lay.addLayout(self._upcoming_grid)
        self._upcoming_empty = QLabel("暂无后续赛程")
        self._upcoming_empty.setStyleSheet("color:#B0BEC5; font-size:13px;")
        self._upcoming_empty.setVisible(False)
        up_lay.addWidget(self._upcoming_empty)
        body_layout.addWidget(upcoming_card)

        body_layout.addStretch(1)

    # ─────────────────────────────────────────
    def apply_palette(self, palette) -> None:
        """皮肤切换：让英雄横幅渐变 / 倒计时强调色随主题联动。"""
        self._hero.apply_palette(palette)

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            (rounds, matches), scorers, assists = await asyncio.gather(
                self._service.fetch_full_schedule(force=force),
                self._service.fetch_ranking(RankingType.GOALS, force=force),
                self._service.fetch_ranking(RankingType.ASSISTS, force=force),
            )
            try:
                groups, _ko, _km = await self._service.fetch_standings(force=force)
            except Exception:  # pragma: no cover - 网络
                groups = []

            now = datetime.now(timezone.utc)
            live = [m for m in matches if m.is_live]
            upcoming = sorted(
                [m for m in matches if m.start_play and m.start_play >= now],
                key=lambda m: m.start_play,
            )
            recent_done = sorted(
                [m for m in matches if m.status == MatchStatus.PLAYED],
                key=lambda m: m.start_play or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )

            focus = (live[:1] or upcoming[:1] or recent_done[:1])
            self._hero.set_focus_match(focus[0] if focus else None)

            # 指标
            self._stat_total.value.set_target(len(matches))
            self._stat_done.value.set_target(
                sum(1 for m in matches if m.status == MatchStatus.PLAYED)
            )
            self._stat_live.value.set_target(len(live))
            self._stat_upcoming.value.set_target(len(upcoming))

            # 进球风暴（数据速览）
            self._fill_goal_storm(recent_done)

            # 直播 / 即将开赛 6 场
            self._fill_grid(self._live_grid, live[:6] or upcoming[:6])
            self._live_empty.setVisible(not live)

            # 即将开赛
            self._fill_grid(self._upcoming_grid, upcoming[:6])
            self._upcoming_empty.setVisible(not upcoming)

            # 排行榜 TOP3
            self._fill_leaders(self._scorers_box, scorers[:3])
            self._fill_leaders(self._assists_box, assists[:3])

            # 夺冠热门 · 实力榜
            self._fill_power(groups)

            # AI 预测精选（焦点比赛：直播 > 即将开赛 > 最近一场）
            feat = (upcoming[:1] or live[:1] or recent_done[:1])
            self._fill_featured(feat[0] if feat else None, matches, groups)

        self.run_async(runner)

    # ─────────────────────────────────────────
    def _make_stat(self, label: str, label_en: str, icon: str, color: str) -> Card:
        """高级指标卡：彩色图标徽章 + 大号 count-up + 中英标签 + 底部色条。"""
        card = Card(padding=0, glow_color=color)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(104)

        col = QVBoxLayout(card)
        col.setContentsMargins(18, 16, 18, 0)
        col.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(12)
        # 图标徽章（半透明主色底 + 圆角）
        badge = QLabel(icon)
        badge.setFixedSize(46, 46)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"font-size:22px; border-radius:14px;"
            f" background: rgba({_rgb(color)},0.16);"
            f" border:1px solid rgba({_rgb(color)},0.34);"
        )
        top.addWidget(badge)

        text_box = QVBoxLayout()
        text_box.setSpacing(0)
        value = CountUpLabel()
        value.setStyleSheet(f"font-size:30px; font-weight:900; color:{color};")
        text_box.addWidget(value)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:800;")
        text_box.addWidget(lbl)
        top.addLayout(text_box)
        top.addStretch(1)

        en = QLabel(label_en)
        en.setAlignment(Qt.AlignmentFlag.AlignTop)
        en.setStyleSheet(
            "color:#6B7689; font-size:9px; letter-spacing:1.8px; font-weight:800;"
        )
        top.addWidget(en, alignment=Qt.AlignmentFlag.AlignTop)
        col.addLayout(top)

        # 底部细色条
        underline = QFrame()
        underline.setFixedHeight(3)
        underline.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {color}, stop:1 rgba(255,255,255,0.0));"
            f" border-bottom-left-radius:18px;"
        )
        col.addWidget(underline)

        card.value = value  # type: ignore[attr-defined]
        return card

    def _make_mini_stat(self, label: str, label_en: str, icon: str, color: str) -> Card:
        """数据速览小卡：图标 + 大号数值（文本由 refresh 填）+ 中英标签。"""
        card = Card(padding=0, glow_color=color)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(86)
        col = QVBoxLayout(card)
        col.setContentsMargins(18, 14, 18, 12)
        col.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(10)
        badge = QLabel(icon)
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"font-size:18px; border-radius:12px;"
            f" background: rgba({_rgb(color)},0.16);"
            f" border:1px solid rgba({_rgb(color)},0.34);"
        )
        top.addWidget(badge)
        tb = QVBoxLayout(); tb.setSpacing(0)
        value = QLabel("—")
        value.setStyleSheet(f"font-size:24px; font-weight:900; color:{color};")
        tb.addWidget(value)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#FFFFFF; font-size:11.5px; font-weight:800;")
        tb.addWidget(lbl)
        top.addLayout(tb)
        top.addStretch(1)
        en = QLabel(label_en)
        en.setStyleSheet(
            "color:#6B7689; font-size:9px; letter-spacing:1.6px; font-weight:800;"
        )
        top.addWidget(en, alignment=Qt.AlignmentFlag.AlignTop)
        col.addLayout(top)
        card.value = value  # type: ignore[attr-defined]
        return card

    def _make_leaders_card(self, title: str, accent: str) -> tuple[Card, QVBoxLayout]:
        card = Card(padding=18, glow_color=accent)
        outer = QVBoxLayout(card)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(10)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 15px; font-weight: 900; color:{accent};")
        outer.addWidget(t)
        rows = QVBoxLayout()
        rows.setSpacing(10)
        outer.addLayout(rows)
        return card, rows

    def _fill_grid(self, layout, matches: list[Match]) -> None:
        # 清空 & 填充
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        cards: list[QWidget] = []
        for m in matches:
            card = MatchCard(m)
            card.clicked.connect(self.match_clicked.emit)
            layout.addWidget(card)
            cards.append(card)
        stagger_fade(cards, step=40, dx=0, dy=0)

    def _fill_leaders(self, layout: QVBoxLayout, players) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        widgets: list[QWidget] = []
        for i, p in enumerate(players):
            row = QHBoxLayout()
            row.setSpacing(12)

            rank_lbl = QLabel(str(p.rank))
            rank_lbl.setFixedWidth(28)
            rank_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_lbl.setStyleSheet(
                f"font-size: 18px; font-weight: 900;"
                f"color: {self._top_color(p.rank)};"
            )
            row.addWidget(rank_lbl)
            row.addWidget(PlayerAvatar(p.person_logo, size=42))

            text = QVBoxLayout()
            text.setSpacing(2)
            name = QLabel(p.person_name)
            name.setStyleSheet("font-weight:800; font-size:14px;")
            text.addWidget(name)
            tt = QHBoxLayout()
            tt.setSpacing(6)
            tt.addWidget(TeamLogo(p.team_logo, size=16, shape="circle"))
            team_lbl = QLabel(p.team_name)
            team_lbl.setStyleSheet("color:#B0BEC5; font-size:11px;")
            tt.addWidget(team_lbl)
            tt.addStretch(1)
            row_w = QWidget()
            row_w.setLayout(tt)
            text.addWidget(row_w)
            row.addLayout(text, 1)

            count = QLabel(str(p.count))
            count.setStyleSheet("font-size: 22px; font-weight: 900; color:#00BFFF;")
            row.addWidget(count)

            wrap = QWidget()
            wrap.setLayout(row)
            wrap.setCursor(Qt.CursorShape.PointingHandCursor)

            def _emit(_ev, pl=p) -> None:
                self.player_clicked.emit(pl.person_id, pl.person_name)

            wrap.mousePressEvent = _emit  # type: ignore[assignment]
            layout.addWidget(wrap)
            widgets.append(wrap)
        stagger_fade(widgets, step=70, dx=0, dy=0)

    @staticmethod
    def _top_color(r: int) -> str:
        return {1: "#FFD700", 2: "#CBD5E1", 3: "#FF9D5C"}.get(r, "#B0BEC5")

    # ─────────────────────────────────────────
    @staticmethod
    def _match_goals(m: Match):
        try:
            a = int(m.fs_a if m.fs_a not in (None, "") else (m.score_a or 0))
            b = int(m.fs_b if m.fs_b not in (None, "") else (m.score_b or 0))
        except (TypeError, ValueError):
            return None
        return a, b

    def _fill_goal_storm(self, played: list[Match]) -> None:
        games = [g for g in (self._match_goals(m) for m in played) if g is not None]
        n = len(games)
        total = sum(a + b for a, b in games)
        over = sum(1 for a, b in games if a + b >= 3)
        btts = sum(1 for a, b in games if a > 0 and b > 0)
        self._stat_goals.value.setText(str(total))
        self._stat_avg.value.setText(f"{(total / n):.2f}" if n else "—")
        self._stat_big.value.setText(f"{round(over / n * 100)}%" if n else "—")
        self._stat_btts.value.setText(f"{round(btts / n * 100)}%" if n else "—")

    def _fill_power(self, groups: list[GroupStanding]) -> None:
        while self._power_grid.count():
            item = self._power_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        teams = [t for g in groups for t in g.teams]
        teams.sort(key=lambda t: (t.points, t.goal_diff, t.goals_pro), reverse=True)
        top = teams[:8]
        self._power_empty.setVisible(not top)
        cards: list[QWidget] = []
        for i, ts in enumerate(top, start=1):
            cards.append(self._power_card(i, ts))
        for c in cards:
            self._power_grid.addWidget(c)
        stagger_fade(cards, step=40, dx=0, dy=0)

    def _power_card(self, rank: int, ts) -> QWidget:
        card = QFrame()
        card.setObjectName("PowerCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setFixedSize(248, 92)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        rc = self._top_color(rank)
        card.setStyleSheet(
            "QFrame#PowerCard{background: rgba(255,255,255,0.04);"
            " border-radius:16px; border:1px solid rgba(255,255,255,0.07);}"
            f"QFrame#PowerCard:hover{{border:1px solid {rc};"
            " background: rgba(255,255,255,0.08);}"
        )
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)
        rk = QLabel(str(rank))
        rk.setFixedWidth(26)
        rk.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rk.setStyleSheet(f"font-size:22px; font-weight:900; color:{rc};")
        row.addWidget(rk)
        row.addWidget(TeamLogo(ts.team_logo, size=40, shape="circle"))
        col = QVBoxLayout(); col.setSpacing(2)
        name = QLabel(ts.team_name)
        name.setStyleSheet("font-size:14px; font-weight:800; color:#FFFFFF;")
        col.addWidget(name)
        gd = f"+{ts.goal_diff}" if ts.goal_diff > 0 else str(ts.goal_diff)
        meta = QLabel(f"{ts.points} 分  ·  净胜 {gd}  ·  进 {ts.goals_pro}")
        meta.setStyleSheet("color:#B0BEC5; font-size:11px;")
        col.addWidget(meta)
        row.addLayout(col, 1)
        card.mousePressEvent = (  # type: ignore[assignment]
            lambda _e, tid=ts.team_id: self.team_clicked.emit(tid)
        )
        return card

    def _clear_featured(self) -> None:
        while self._featured_lay.count():
            item = self._featured_lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            else:
                inner = item.layout()
                if inner:
                    self._drop_layout(inner)

    def _drop_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._drop_layout(item.layout())

    def _fill_featured(
        self, match: Match | None, matches: list[Match], groups: list[GroupStanding]
    ) -> None:
        self._clear_featured()
        if match is None:
            empty = QLabel("暂无可预测的比赛")
            empty.setStyleSheet("color:#B0BEC5; font-size:13px;")
            self._featured_lay.addWidget(empty)
            return
        try:
            pred = build_prediction(match, matches, groups)
        except Exception:  # pragma: no cover
            pred = None
        if pred is None:
            empty = QLabel("预测数据暂不可用")
            empty.setStyleSheet("color:#B0BEC5; font-size:13px;")
            self._featured_lay.addWidget(empty)
            return

        # 对阵行
        vs = QHBoxLayout()
        vs.setSpacing(12)
        vs.addWidget(TeamLogo(match.team_a_logo, size=44, shape="circle"))
        na = QLabel(match.team_a_name)
        na.setStyleSheet("font-size:15px; font-weight:900; color:#FFFFFF;")
        vs.addWidget(na)
        vs.addStretch(1)
        mid = QLabel(pred.group_name or "VS")
        mid.setStyleSheet("color:#FFD700; font-size:13px; font-weight:900;")
        vs.addWidget(mid)
        vs.addStretch(1)
        nb = QLabel(match.team_b_name)
        nb.setStyleSheet("font-size:15px; font-weight:900; color:#FFFFFF;")
        nb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        vs.addWidget(nb)
        vs.addWidget(TeamLogo(match.team_b_logo, size=44, shape="circle"))
        self._featured_lay.addLayout(vs)

        # 概率条
        hr = QHBoxLayout()
        for txt, color, align in (
            (f"{match.team_a_name} 胜", "#FF5470", Qt.AlignmentFlag.AlignLeft),
            ("平", "#B0BEC5", Qt.AlignmentFlag.AlignCenter),
            (f"{match.team_b_name} 胜", "#00BFFF", Qt.AlignmentFlag.AlignRight),
        ):
            l = QLabel(txt)
            l.setStyleSheet(f"color:{color}; font-size:11.5px; font-weight:800;")
            l.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            hr.addWidget(l, 1)
        self._featured_lay.addLayout(hr)
        self._featured_lay.addWidget(
            self._prob_bar(pred.win_a, pred.draw, pred.win_b)
        )
        pr = QHBoxLayout()
        for val, color, align in (
            (pred.win_a, "#FF5470", Qt.AlignmentFlag.AlignLeft),
            (pred.draw, "#B0BEC5", Qt.AlignmentFlag.AlignCenter),
            (pred.win_b, "#00BFFF", Qt.AlignmentFlag.AlignRight),
        ):
            l = QLabel(f"{round(val * 100)}%")
            l.setStyleSheet(f"color:{color}; font-size:13px; font-weight:900;")
            l.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            pr.addWidget(l, 1)
        self._featured_lay.addLayout(pr)

        verdict = QLabel(f"📌  {pred.verdict}")
        verdict.setStyleSheet(
            "color:#FFD700; font-size:13px; font-weight:800;"
            "background:rgba(255,197,61,0.10); border-radius:10px; padding:8px 12px;"
        )
        verdict.setWordWrap(True)
        self._featured_lay.addWidget(verdict)

        cta = QLabel("查看完整 AI 赛事预测  →")
        cta.setStyleSheet("color:#9CC4FF; font-size:12.5px; font-weight:800;")
        cta.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._featured_lay.addWidget(cta)

        self._featured_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self._featured_card.mousePressEvent = (  # type: ignore[assignment]
            lambda _e, mt=match: self.prediction_clicked.emit(mt)
        )

    @staticmethod
    def _prob_bar(pa: float, pd: float, pb: float) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(3)
        total = (pa + pd + pb) or 1.0
        for val, color, side in (
            (pa, "#FF5470", "left"),
            (pd, "#B0BEC5", "mid"),
            (pb, "#00BFFF", "right"),
        ):
            seg = QFrame()
            radius = (
                "border-top-left-radius:8px;border-bottom-left-radius:8px;"
                if side == "left" else
                "border-top-right-radius:8px;border-bottom-right-radius:8px;"
                if side == "right" else ""
            )
            seg.setStyleSheet(f"background:{color}; border-radius:3px; {radius}")
            row.addWidget(seg, max(1, int(val / total * 1000)))
        return bar


def _rgb(hex_color: str) -> str:
    """'#RRGGBB' -> 'r,g,b'，用于 rgba() 内联样式。"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return "0,191,255"
    return f"{r},{g},{b}"
