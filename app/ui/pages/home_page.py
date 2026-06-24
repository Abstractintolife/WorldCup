"""概览仪表盘（OVERVIEW）—— 对照「想象中的样子」设计稿复刻，**全量真实数据**。

布局
-----
* 第一排：实时比赛核心看板（焦点比赛）  |  小组积分榜（A-L 切换）
* 第二排：赛事大盘 5 张统计卡（场次 / 进球 / 完赛进度 / 球队 / 金靴）
* 第三排：今日赛程  |  攻防雷达分析  |  射手榜 TOP5
* 第四排：夺冠热门  |  赛事新闻  |  快速操作

数据来源
---------
所有内容均通过既有数据层（``DataService`` → 懂球帝公开接口）实时拉取，
**不含任何写死的演示数据**：

* 实时比赛 / 今日赛程 / 赛事大盘统计 ← ``fetch_full_schedule``
* 小组积分榜 / 攻防雷达 / 夺冠热门（模型推算） ← ``fetch_standings``
* 射手榜 / 金靴 ← ``fetch_ranking(GOALS)``
* 赛事新闻 ← ``fetch_news``（懂球帝资讯流）

焦点比赛优先级：进行中 > 最近一场即将开赛 > 最近一场已结束。
"""
from __future__ import annotations

import logging
import math

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus, Round
from app.models.player import PlayerRanking, RankingType
from app.models.standing import GroupStanding, TeamStanding
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta, percentages_to_100
from app.ui.widgets.championship_panel import ChampionshipPanel
from app.ui.widgets.live_match_center import LiveMatchCenter
from app.ui.widgets.standings_table import StandingsTable
from app.ui.widgets.stat_strip import StatStrip, compute_stats
from app.ui.widgets.today_matches_panel import TodayMatchesPanel
from app.ui.widgets.top_scorers_panel import TopScorersPanel as TopScorersCard
from app.utils.time_utils import is_today, local_now

log = logging.getLogger(__name__)

# ── 设计稿配色 ─────────────────────────────────────────────
C_PRIMARY = "#00BFFF"
C_PURPLE = "#6A5ACD"
C_GOLD = "#FFD700"
C_LIVE = "#FF3057"
C_GREEN = "#2ED877"
C_YELLOW = "#FFC857"
C_RED = "#FF5470"
C_TEXT = "#FFFFFF"
C_DIM = "#B0BEC5"
C_FAINT = "#6B7689"


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    except ValueError:
        return "0,191,255"


# ════════════════════════════════════════════════════════════
#  概览页信息架构（IA）权重 —— 单一事实来源（供布局与单测共享）
# ════════════════════════════════════════════════════════════
#  设计稿 Hero:Overview:Standings:Schedule:Analysis:Other = 40:20:15:10:10:5
#  （需求 1.2）。这些常量是模块级的，便于无显示环境下的单元测试直接读取。
IA_WEIGHTS: dict[str, int] = {
    "hero": 40,
    "overview": 20,
    "standings": 15,
    "schedule": 10,
    "analysis": 10,
    "other": 5,
}
# 视觉权重的规范顺序（即 40:20:15:10:10:5 比值的排列顺序）。
IA_WEIGHT_ORDER: tuple[str, ...] = (
    "hero", "overview", "standings", "schedule", "analysis", "other",
)
# Hero 行横向列分配：焦点比赛 ~65%（左、宽）| 小组积分榜 ~35%（右、窄）（需求 1.4）。
HERO_COLUMN_WEIGHTS: tuple[int, int] = (65, 35)
# 底部多面板行（任务 12）横向列分配：今日赛程 | 实时比赛 | 射手榜 | 夺冠概率榜。
# 「今日赛程」与「实时比赛」为「正在发生」的主面板（更宽），射手榜 / 夺冠概率榜
# 为次级面板（略窄）；四列共同占用 IA 底部行纵向预算（schedule+analysis+other）。
BOTTOM_COLUMN_WEIGHTS: tuple[int, int, int, int] = (10, 10, 7, 7)


def ia_weight_ratio(weights: dict[str, int] = IA_WEIGHTS) -> list[int]:
    """返回 40:20:15:10:10:5 视觉权重比（按 :data:`IA_WEIGHT_ORDER` 排列）。"""
    return [weights[k] for k in IA_WEIGHT_ORDER]


def ia_row_stretches(weights: dict[str, int] = IA_WEIGHTS) -> tuple[int, int, int]:
    """概览页三排（自上而下）的纵向 stretch 预算。

    * 第 1 排（Hero 行）承载 ``hero`` 权重；小组积分榜以右侧列的形式同处此排
      （列分配见 :data:`HERO_COLUMN_WEIGHTS`），故本排纵向预算取主导的 hero 权重。
    * 第 2 排（Stat Strip）取 ``overview`` 权重。
    * 第 3 排（底部多面板）取 ``schedule + analysis + other`` 之和。

    无论窗口如何缩放，这些 stretch 比值都被 Qt 布局保持不变（需求 1.3）。
    """
    return (
        weights["hero"],
        weights["overview"],
        weights["schedule"] + weights["analysis"] + weights["other"],
    )


# ════════════════════════════════════════════════════════════
#  HomePage（概览仪表盘）
# ════════════════════════════════════════════════════════════
class HomePage(BasePage):
    title = "概览"
    subtitle = "OVERVIEW · 2026 FIFA 世界杯实时数据中心"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)
    prediction_clicked = pyqtSignal(Match)
    navigate = pyqtSignal(str)
    live_state_changed = pyqtSignal(bool)   # 是否有比赛正在进行（驱动侧栏 LIVE 徽章）
    connection_changed = pyqtSignal(bool)   # 实时数据连接态（驱动侧栏页脚实时状态）

    # 视觉权重（公开，供单测无显示读取）。
    WEIGHTS: dict[str, int] = dict(IA_WEIGHTS)

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
        # 滚动正文走不透明底（性能：避免整树随滚动重新合成；hud_theme #OpaqueBody）。
        body.setObjectName("OpaqueBody")
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(24, 22, 24, 26)
        v.setSpacing(18)
        self._root_layout = v

        # 注：顶部「2026 美加墨世界杯 · 实时数据总览」双行欢迎条已移除 ——
        # 该信息与子标题栏（SubHeader）完全重复，正文不再二次展示（更精炼）。
        # 连接状态改由子标题栏右侧的实时连接胶囊呈现（见 MainWindow 接线）。

        # ── 第 1 排：Hero 行（焦点比赛 ~65% | 小组积分榜 ~35%）──
        # 焦点比赛核心看板（任务 8：HeroMatchCard）；小组积分榜占位待任务 10。
        self._hero_card = HeroMatchCard()
        self._hero_card.setProperty("ia_region", "hero")
        self._hero_card.watch_clicked.connect(self._open_live_stream)
        self._hero_card.analysis_clicked.connect(self._on_hero_analysis)
        self._hero_card.h2h_clicked.connect(self._on_hero_h2h)
        # 小组积分榜（任务 10：StandingsTable，取代占位）。
        self._standings_card = StandingsTable()
        self._standings_card.setProperty("ia_region", "standings")
        self._standings_card.setMinimumHeight(360)
        self._standings_card.team_clicked.connect(self.team_clicked.emit)
        self._standings_card.view_all_clicked.connect(lambda: self.navigate.emit("standings"))
        self._hero_row = QHBoxLayout()
        self._hero_row.setSpacing(18)
        self._hero_row.addWidget(self._hero_card, HERO_COLUMN_WEIGHTS[0])
        self._hero_row.addWidget(self._standings_card, HERO_COLUMN_WEIGHTS[1])
        hero_row_host = QWidget()
        hero_row_host.setLayout(self._hero_row)

        # ── 第 2 排：Stat Strip（赛事大盘统计条）──
        # 六张等宽玻璃统计卡（任务 11：StatStrip，取代占位）。默认展示设计稿
        # 样例值，真实数据到达后经 _apply → compute_stats 覆盖。
        self._stat_card = StatStrip()
        self._stat_card.setProperty("ia_region", "overview")
        self._stat_card.setMinimumHeight(78)
        # 六张统计卡点击跳转到对应榜单（球队 / 球员 / 赛程 / 场馆）。
        self._stat_card.clicked.connect(self._on_stat_clicked)

        # ── 第 3 排：底部多面板行（今日赛程 / 实时比赛 / 射手榜 / 夺冠概率榜）──
        # 任务 12：四块广播级面板，全部由注入的 DataService 喂数据（需求 1.1 / 26.2）。
        self._today_card = TodayMatchesPanel()
        self._today_card.setProperty("ia_region", "schedule")
        self._today_card.match_clicked.connect(self.match_clicked.emit)
        self._today_card.view_all_clicked.connect(lambda: self.navigate.emit("schedule"))

        self._live_card = LiveMatchCenter()
        self._live_card.setProperty("ia_region", "live")
        self._live_card.match_clicked.connect(self._on_live_match_clicked)
        self._live_card.player_clicked.connect(self.player_clicked.emit)
        self._live_card.enter_clicked.connect(lambda: self.navigate.emit("live"))

        self._scorers_card = TopScorersCard()
        self._scorers_card.setProperty("ia_region", "scorers")
        self._scorers_card.player_clicked.connect(self.player_clicked.emit)
        self._scorers_card.view_all_clicked.connect(lambda: self.navigate.emit("scorers"))

        self._cities_card = ChampionshipPanel(top=6)
        self._cities_card.setProperty("ia_region", "championship")
        self._cities_card.view_all_clicked.connect(lambda: self.navigate.emit("probability"))

        self._bottom_row = QHBoxLayout()
        self._bottom_row.setSpacing(18)
        self._bottom_row.addWidget(self._today_card, BOTTOM_COLUMN_WEIGHTS[0])
        self._bottom_row.addWidget(self._live_card, BOTTOM_COLUMN_WEIGHTS[1])
        self._bottom_row.addWidget(self._scorers_card, BOTTOM_COLUMN_WEIGHTS[2])
        self._bottom_row.addWidget(self._cities_card, BOTTOM_COLUMN_WEIGHTS[3])
        bottom_row_host = QWidget()
        bottom_row_host.setLayout(self._bottom_row)

        # 三排按 IA 视觉权重设置纵向 stretch（40 / 20 / 25）。比值随缩放保持不变（需求 1.3）。
        hero_s, stat_s, bottom_s = ia_row_stretches(self.WEIGHTS)
        v.addWidget(hero_row_host, hero_s)
        v.addWidget(self._stat_card, stat_s)
        v.addWidget(bottom_row_host, bottom_s)

        # ── 「上一份完好数据」缓存（需求 28.1：拉取失败时保留最近一次成功的数据）──
        # 自动刷新（MainWindow 定时器）会在下一拍重试失败的拉取（需求 28.2）。
        self._last_rounds: list[Round] = []
        self._last_matches: list[Match] = []
        self._last_groups: list[GroupStanding] = []
        self._last_scorers: list[PlayerRanking] = []
        self._had_good_data: bool = False

        self._set_connected(False)

    # ── IA 权重访问器（供单测无显示读取、并校验实际布局配置） ──
    def region_weights(self) -> list[int]:
        """40:20:15:10:10:5 视觉权重比（hero/overview/standings/schedule/analysis/other）。"""
        return ia_weight_ratio(self.WEIGHTS)

    def row_stretches(self) -> tuple[int, int, int]:
        """三排（Hero / Stat Strip / 底部多面板）实际配置的纵向 stretch。"""
        lay = self._root_layout
        # 欢迎条已移除：三个权重排现在分别位于 index 0 / 1 / 2。
        return (lay.stretch(0), lay.stretch(1), lay.stretch(2))

    def hero_column_stretches(self) -> tuple[int, int]:
        """Hero 行内 [焦点比赛, 小组积分榜] 的横向 stretch（~65 / ~35）。"""
        return (self._hero_row.stretch(0), self._hero_row.stretch(1))

    def bottom_column_stretches(self) -> tuple[int, int, int, int]:
        """底部行内 [今日赛程, 实时比赛, 射手榜, 夺冠概率榜] 的横向 stretch（10/10/7/7）。"""
        return (self._bottom_row.stretch(0), self._bottom_row.stretch(1),
                self._bottom_row.stretch(2), self._bottom_row.stretch(3))

    # ── 顶部欢迎条（已移除，连接态改由 SubHeader 胶囊呈现） ──
    def _set_connected(self, ok: bool) -> None:
        # 仅广播连接态：MainWindow 据此驱动侧栏页脚与子标题栏的实时连接胶囊。
        self.connection_changed.emit(bool(ok))

    # ── 数据加载 ────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            import asyncio
            from app.services.fifa_rankings import FifaRankings
            from app.services.theanalyst import TheAnalyst
            results = await asyncio.gather(
                self._service.fetch_full_schedule(force=force),
                self._service.fetch_standings(force=force),
                self._service.fetch_ranking(RankingType.GOALS, force=force),
                FifaRankings.instance().refresh(force=force),
                TheAnalyst.instance().refresh(force=force),
                return_exceptions=True,
            )
            # FIFA 世界排名仅用于在对阵国旗旁标注名次，不计入主数据成功判定。
            self._apply(results[:3])
            # 夺冠概率榜（Opta 超算）—— 实时接口失败时服务内部自动回退离线快照。
            self._cities_card.set_ranking(
                TheAnalyst.instance().championship_ranking())
            # 小组积分榜「出线概率」栏同步真实 Opta 出线概率（与概率预测页同源）。
            self._standings_card.set_qualify_probs(
                TheAnalyst.instance().qualification_map())
            # 实时比赛阵容（大头照布阵图）：仅当有正在进行的比赛时拉取并展示。
            live = next((m for m in self._last_matches
                         if getattr(m, "is_live", False)), None)
            if live is not None:
                try:
                    ml = await self._service.fetch_match_lineup(
                        live.match_id, force=force)
                except Exception:
                    ml = None
                self._live_card.set_lineup(ml)
            else:
                self._live_card.set_lineup(None)
        self.run_async(runner)

    def _apply(self, results) -> None:
        # 所有数据均来自注入的 DataService（无任何直接网络访问，需求 26.2）。
        sched, standings, scorers = results

        # ── 逐数据源判定成功 / 失败 ──────────────────────────
        # asyncio.gather(return_exceptions=True) 下，失败项为 Exception 实例。
        # 成功项更新「上一份完好数据」缓存；失败项**保留**上一份（需求 28.1），
        # 由 MainWindow 自动刷新定时器在下一拍重试（需求 28.2）。
        sched_ok = isinstance(sched, tuple)
        standings_ok = isinstance(standings, tuple)
        scorers_ok = isinstance(scorers, list)

        if sched_ok:
            self._last_rounds, self._last_matches = sched
        if standings_ok:
            self._last_groups = standings[0]
        if scorers_ok:
            self._last_scorers = scorers

        # 渲染统一使用「最近完好」数据（成功项为新值，失败项为保留值）。
        matches: list[Match] = self._last_matches
        groups: list[GroupStanding] = self._last_groups
        scorer_list: list[PlayerRanking] = self._last_scorers

        # 连接状态：本拍至少一个数据源成功即视为已连接；全部失败显示错误态，
        # 但各控件仍展示上一份完好数据（或首拉失败时的设计稿样例 / 空态）。
        any_ok = sched_ok or standings_ok or scorers_ok
        if any_ok:
            self._had_good_data = True
        self._set_connected(any_ok)

        # 是否有正在进行的比赛 —— 驱动侧栏 LIVE 徽章「仅进行中时显示」。
        self.live_state_changed.emit(any(getattr(m, "is_live", False) for m in matches))

        featured = self._pick_featured(matches)
        self._render_hero(featured, matches, groups)

        # 小组积分榜：注入数据（无数据时面板回退设计稿样例，需求 10.6）。
        self._standings_card.set_groups(groups)

        # 赛事大盘统计条：数据测算（缺失则回退设计稿样例，需求 11.3）。
        self._stat_card.set_stats(
            compute_stats(matches=matches, groups=groups, scorers=scorer_list))

        # ── 第 3 排：底部四面板（任务 12，全部经 DataService 喂数据，需求 1.1 / 26.2）──
        # 今日赛程：当日赛事（无则回退设计稿样例）。
        today = [m for m in matches if is_today(m.start_play)]
        self._today_card.set_matches(today)

        # 实时比赛中心：仅展示真实「正在进行」的比赛；无进行中则留空（不再回退虚构样例）。
        live_now = next((m for m in matches if getattr(m, "is_live", False)), None)
        if live_now is not None:
            self._live_card.set_live(live_now)
        else:
            # 没有正在进行的比赛 → 留空（需求：没有就留空，不展示假的实时比赛）。
            self._live_card.set_live(None)

        # 射手榜：射手榜数据（无则回退设计稿样例，需求 14.3）。
        self._scorers_card.set_scorers(scorer_list)

        # 夺冠概率榜由 refresh() 经 TheAnalyst 注入（实时接口失败时回退离线快照）。

    # ── Hero 卡渲染（任务 8：HeroMatchCard + HeroMeta）──────
    def _render_hero(self, featured: Match | None,
                     matches: list[Match], groups: list[GroupStanding]) -> None:
        """用焦点比赛与模型推算填充 HeroMatchCard。

        胜平负来自既有纯计算预测引擎（``app.services.prediction``，无网络），
        归一化为和恰为 100 的整数百分比；Elo / FIFA / 世界排名暂无公开数据源，
        统一以 ``None`` 传入并渲染「—」（需求 8.2）。
        """
        if featured is None:
            self._hero_card.set_match(None, HeroMeta())
            return

        win_prob = (0, 0, 0)
        try:
            from app.services.prediction import build_prediction
            pred = build_prediction(featured, matches, groups)
            win_prob = percentages_to_100((pred.win_a, pred.draw, pred.win_b))
        except Exception:  # pragma: no cover - 预测失败则隐藏概率条
            log.debug("hero win-prob 计算失败", exc_info=True)

        meta = HeroMeta(
            stage_label=getattr(featured, "_stage_name", "") or "世界杯",
            status_label=self._hero_status_label(featured),
            kickoff_utc=featured.start_play,
            venue="",
            win_prob=win_prob,
            home_fifa_rank=self._fifa_rank(featured.team_a_name),
            away_fifa_rank=self._fifa_rank(featured.team_b_name),
        )
        self._hero_card.set_match(featured, meta)

    @staticmethod
    def _fifa_rank(name: str | None) -> int | None:
        """查国际足联世界排名（供 Hero 卡 FIFA 名次显示）。"""
        from app.services.fifa_rankings import FifaRankings
        return FifaRankings.instance().rank(name)

    @staticmethod
    def _hero_status_label(match: Match) -> str:
        if match.is_live:
            return "直播中"
        if match.status == MatchStatus.PLAYED:
            return "已结束"
        return "即将开始"

    # ── 工具：焦点比赛 ──────────────────────
    @staticmethod
    def _pick_featured(matches: list[Match]) -> Match | None:
        if not matches:
            return None
        live = [m for m in matches if m.is_live]
        if live:
            return live[0]
        now = local_now()
        upcoming = [
            m for m in matches
            if m.status in (MatchStatus.FIXTURE, MatchStatus.UNKNOWN)
            and m.local_start is not None and m.local_start >= now
        ]
        if upcoming:
            return min(upcoming, key=lambda x: x.local_start)
        played = [m for m in matches if m.status == MatchStatus.PLAYED and m.local_start]
        if played:
            return max(played, key=lambda x: x.local_start)
        return matches[0]

    @staticmethod
    def _team_lookup(groups: list[GroupStanding]) -> dict[str, TeamStanding]:
        out: dict[str, TeamStanding] = {}
        for g in groups:
            for ts in g.teams:
                if ts.team_id:
                    out[ts.team_id] = ts
        return out

    @staticmethod
    def _championship_odds(groups: list[GroupStanding]) -> list[tuple[str, str, float]]:
        """基于积分榜（场均积分 / 净胜球 / 进攻）的简易夺冠指数 → 归一化概率。

        这是「模型推算」：完全由真实积分榜数据测算，非博彩报价。
        """
        teams: list[tuple[str, str, float]] = []  # (name, id, index)
        for g in groups:
            for ts in g.teams:
                m = ts.matches_total
                if m == 0:
                    idx = 0.25
                else:
                    ppm = ts.points / m / 3.0
                    gdp = max(0.0, min(1.0, (ts.goal_diff / m + 3.0) / 6.0))
                    gfpm = max(0.0, min(1.0, (ts.goals_pro / m) / 3.0))
                    idx = 0.5 * ppm + 0.3 * gdp + 0.2 * gfpm
                teams.append((ts.team_name, ts.team_id, idx))
        if not teams:
            return []
        # softmax 放大头部差距
        k = 6.0
        exps = [math.exp(k * idx) for _, _, idx in teams]
        total = sum(exps) or 1.0
        probs = [
            (name, tid, e / total)
            for (name, tid, _), e in zip(teams, exps)
        ]
        probs.sort(key=lambda x: x[2], reverse=True)
        return probs[:5]

    # ── Hero 卡操作回调（保持既有信号 match_clicked / prediction_clicked 接通）──
    def _on_hero_analysis(self, match: Match | None) -> None:
        """赛前分析 → 复用既有 prediction_clicked 信号。"""
        if match is not None:
            self.prediction_clicked.emit(match)

    def _on_hero_h2h(self, match: Match | None) -> None:
        """历史交锋 → 复用既有 match_clicked 信号（进入比赛详情）。"""
        if match is not None:
            self.match_clicked.emit(match)

    def _on_live_match_clicked(self, match) -> None:
        """实时比赛中心比分行 → 复用既有 match_clicked 信号（进入比赛详情）。"""
        if isinstance(match, Match):
            self.match_clicked.emit(match)

    # ── 赛事大盘统计卡点击 → 跳转对应榜单 ────────
    #: 六张统计卡 key → 目标页面（球员相关统计跳球员榜，球队跳球队榜）。
    _STAT_NAV = {
        "matches": "schedule",   # 总比赛场次 → 赛程中心
        "goals": "scorers",      # 总进球数 → 射手榜（球员）
        "scorers": "scorers",    # 进球球员 → 射手榜（球员）
        "avg": "scorers",        # 平均进球 → 射手榜（球员）
        "teams": "teams",        # 参赛球队 → 球队榜
        "cities": "venue",       # 主办城市 → 场馆地图
    }

    def _on_stat_clicked(self, key: str) -> None:
        target = self._STAT_NAV.get(key)
        if target:
            self.navigate.emit(target)

    # ── 观看直播 / 导入 M3U8 源 ──────────────
    def _open_live_stream(self, match: Match | None) -> None:
        """打开应用内播放器观看直播，并支持粘贴/导入 M3U8 等源地址。"""
        from app.ui.widgets.video_player import VideoPlayerDialog
        title = "直播间"
        if match is not None:
            title = f"直播 · {match.team_a_name} vs {match.team_b_name}"
        dlg = VideoPlayerDialog(url="", title=title, parent=self.window())
        dlg.exec()

    # ── 兼容 MainWindow 接口 ────────────────
    def apply_palette(self, palette) -> None:  # noqa: D401
        # 概览页采用固定的设计稿配色（深蓝世界杯）。
        return
