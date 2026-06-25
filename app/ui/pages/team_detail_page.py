"""球队详情页：阵容（射手榜中本队球员）+ 全部赛程 + 小组位置。

修复点
-------
* 「本队进球 / 助攻贡献者」由 **单一 FlowLayout 合并卡片** 改为
  **左右两列「贡献者排行行」**。
  - 左列 ⚽ 进球贡献者（按本届进球数倒序）
  - 右列 🅰️ 助攻贡献者（按本届助攻数倒序）
  即便只有一个人也不再「卡在一起」—— 行卡片本身就是定宽满列布局。
"""
from __future__ import annotations

import asyncio
import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match
from app.models.player import PlayerRanking, RankingType
from app.models.squad import SquadGroup
from app.models.standing import GroupStanding, TeamStanding
from app.services.data_service import DataService
from app.services.favorites import Favorites
from app.ui.design.app_cursor import pointing_hand_cursor
from app.services.team_preview import (
    TeamFormation,
    TeamOutlook,
    build_team_formation,
    build_team_outlook,
)
from app.ui.pages.base import BasePage
from app.ui.widgets.card_grid import CardGrid
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.favorite_button import FavoriteButton
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.formation_pitch import FormationPitch, rating_color
from app.ui.widgets.match_card import MatchCard
from app.ui.widgets.misc import Card, HLine
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.widgets.squad_card import ROLE_COLOR, SquadPlayerCard
from app.ui.widgets.team_logo import TeamLogo
from app.utils.time_utils import fmt_datetime, fmt_relative

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
class _ContributorRow(QWidget):
    """单条贡献者行：名次 + 头像 + 姓名 + 数值（进球/助攻）。"""

    clicked = pyqtSignal(str, str)  # person_id, person_name

    def __init__(self, p: PlayerRanking, value: int, kind: str) -> None:
        super().__init__()
        self._p = p
        self.setCursor(pointing_hand_cursor())
        self.setFixedHeight(60)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        accent = "#46D2FF" if kind == "goals" else "#FFD700"
        self.setStyleSheet(
            "_ContributorRow{background: rgba(255,255,255,0.04);"
            " border-radius: 14px; border: 1px solid rgba(255,255,255,0.06);}"
            "_ContributorRow:hover{background: rgba(255,255,255,0.08);"
            f" border: 1px solid {accent};}}"
        )

        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 8, 14, 8)
        outer.setSpacing(12)

        # 名次徽章
        rank_lbl = QLabel(f"#{p.rank}")
        rank_lbl.setStyleSheet(
            f"color:{accent}; font-size:13px; font-weight:900;"
            "background: rgba(255,255,255,0.06); border-radius:9px; padding:3px 8px;"
        )
        rank_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        outer.addWidget(rank_lbl)

        outer.addWidget(PlayerAvatar(p.person_logo, size=42))

        col = QVBoxLayout()
        col.setSpacing(2)
        n = QLabel(p.person_name)
        n.setStyleSheet("font-weight: 800; font-size: 13.5px;")
        col.addWidget(n)
        meta = QLabel(f"本届世界杯  ·  {kind == 'goals' and '进球' or '助攻'} 排行")
        meta.setStyleSheet("color:#B0BEC5; font-size:10.5px;")
        col.addWidget(meta)
        outer.addLayout(col, 1)

        # 数值大字
        v = QLabel(str(value))
        v.setStyleSheet(f"color:{accent}; font-size:24px; font-weight:900;")
        outer.addWidget(v)
        unit = QLabel("⚽" if kind == "goals" else "🅰️")
        unit.setStyleSheet("font-size:14px;")
        outer.addWidget(unit)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._p.person_id, self._p.person_name)


# ─────────────────────────────────────────────
class TeamDetailPage(BasePage):
    title = "球队详情"
    subtitle = ""

    match_clicked = pyqtSignal(Match)
    player_clicked = pyqtSignal(str, str)
    back_clicked = pyqtSignal()

    def __init__(self, service: DataService, favorites: Favorites) -> None:
        super().__init__()
        self._service = service
        self._favorites = favorites
        self._team_id: str | None = None

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(14)

        # 顶部：返回 + 收藏
        top_row = QHBoxLayout()
        back = QPushButton("←  返回")
        back.setProperty("ghost", True)
        back.setCursor(pointing_hand_cursor())
        back.clicked.connect(self.back_clicked.emit)
        back.setFixedWidth(96)
        top_row.addWidget(back)
        top_row.addStretch(1)
        self._fav_btn = FavoriteButton(favorites, "team", "")
        top_row.addWidget(self._fav_btn)
        outer.addLayout(top_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(16)

    def open_team(self, team_id: str) -> None:
        self._team_id = team_id
        self._fav_btn.set_entity("team", team_id)
        self.refresh(force=False)

    def refresh(self, force: bool = False) -> None:
        if not self._team_id:
            return
        tid = self._team_id

        async def runner() -> None:
            standings_t = self._service.fetch_standings(force=force)
            schedule_t = self._service.fetch_full_schedule(force=force)
            scorers_t = self._service.fetch_ranking(RankingType.GOALS, force=force)
            assists_t = self._service.fetch_ranking(RankingType.ASSISTS, force=force)
            squad_t = self._service.fetch_team_squad(tid, force=force)

            (groups, _ko, _km), (_rounds, matches), scorers, assists, squad = (
                await asyncio.gather(
                    standings_t, schedule_t, scorers_t, assists_t, squad_t,
                    return_exceptions=False,
                )
            )

            team_standing: TeamStanding | None = None
            group_obj: GroupStanding | None = None
            for g in groups:
                for t in g.teams:
                    if t.team_id == tid:
                        team_standing = t
                        group_obj = g
                        break
                if team_standing:
                    break

            team_matches = [m for m in matches if tid in (m.team_a_id, m.team_b_id)]
            team_scorers = sorted(
                [p for p in scorers if p.team_id == tid],
                key=lambda x: (-(x.count or 0), x.rank),
            )
            team_assists = sorted(
                [p for p in assists if p.team_id == tid],
                key=lambda x: (-(x.count or 0), x.rank),
            )

            # 球队名 / 队徽（积分榜缺失时从比赛里兜底）
            team_name = team_standing.team_name if team_standing else ""
            team_logo = team_standing.team_logo if team_standing else None
            if not team_name:
                for m in team_matches:
                    if m.team_a_id == tid:
                        team_name, team_logo = m.team_a_name, m.team_a_logo
                        break
                    if m.team_b_id == tid:
                        team_name, team_logo = m.team_b_name, m.team_b_logo
                        break

            # whoscored 风格：球员布阵评分 + 赛前预测（基于公开数据复刻）
            formation = build_team_formation(tid, team_name, team_logo, squad)
            outlook = build_team_outlook(tid, team_name, matches, groups)

            self._render(team_standing, group_obj, team_matches,
                         team_scorers, team_assists, squad,
                         formation, outlook)

        self.run_async(runner)

    def _render(
        self,
        team: TeamStanding | None,
        group: GroupStanding | None,
        matches: list[Match],
        scorers: list[PlayerRanking],
        assists: list[PlayerRanking],
        squad: list[SquadGroup] | None = None,
        formation: TeamFormation | None = None,
        outlook: TeamOutlook | None = None,
    ) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not team:
            empty = QLabel("未找到该球队的数据")
            empty.setStyleSheet("color:#B0BEC5; padding:40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._body.addWidget(empty)
            return

        # ── 头部 ────────────────────────────
        head = Card(padding=20, glow_color="#00BFFF")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(20, 14, 20, 14)
        h_lay.setSpacing(20)
        h_lay.addWidget(TeamLogo(team.team_logo, size=86, shape="circle"))

        info = QVBoxLayout()
        info.setSpacing(6)
        name = QLabel(team.team_name)
        f = QFont(); f.setPointSize(22); f.setBold(True)
        name.setFont(f)
        info.addWidget(name)
        if group:
            sub = QLabel(f"{group.name}  ·  排名 #{team.rank}")
            sub.setStyleSheet("color:#B0BEC5; font-size:13px; font-weight:600;")
            info.addWidget(sub)
        if team.desc:
            desc = QLabel(team.desc)
            desc.setStyleSheet("color:#2ED883; font-size:12px; font-weight:700;")
            info.addWidget(desc)
        h_lay.addLayout(info, 1)

        stats = QHBoxLayout()
        stats.setSpacing(20)
        for k, v, color in (
            ("积分", str(team.points), "#FFD700"),
            ("胜", str(team.matches_won), "#2ED883"),
            ("平", str(team.matches_draw), "#B0BEC5"),
            ("负", str(team.matches_lost), "#FF4E5E"),
            ("进", str(team.goals_pro), "#46D2FF"),
            ("失", str(team.goals_against), "#B0BEC5"),
            ("净", f"+{team.goal_diff}" if team.goal_diff > 0 else str(team.goal_diff),
             "#FFD700"),
        ):
            sb = QVBoxLayout(); sb.setSpacing(2)
            vl = QLabel(v)
            vl.setStyleSheet(f"font-size:18px; font-weight:900; color:{color};")
            vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            kl = QLabel(k)
            kl.setStyleSheet("color:#B0BEC5; font-size:11px;")
            kl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sb.addWidget(vl); sb.addWidget(kl)
            ww = QWidget(); ww.setLayout(sb)
            stats.addWidget(ww)
        h_lay.addLayout(stats)
        self._body.addWidget(head)

        # ── 贡献者：左右两栏（修复 bug！） ──────
        contrib_row = QHBoxLayout()
        contrib_row.setSpacing(14)

        contrib_row.addWidget(
            self._contributor_card(
                "⚽", "进球贡献者", scorers, kind="goals", accent="#46D2FF"
            ),
            1,
        )
        contrib_row.addWidget(
            self._contributor_card(
                "🅰️", "助攻贡献者", assists, kind="assists", accent="#FFD700"
            ),
            1,
        )
        contrib_w = QWidget(); contrib_w.setLayout(contrib_row)
        self._body.addWidget(contrib_w)

        # ── 赛前预测（whoscored「Prediction」复刻，下一场） ──
        if outlook is not None:
            self._body.addWidget(self._outlook_card(outlook))

        # ── 球员布阵评分（whoscored「Probable Lineup + Ratings」复刻） ──
        if formation is not None:
            self._body.addWidget(self._formation_card(formation))

        # ── 完整阵容 ───────────────────────
        if squad:
            squad_card = Card(padding=18, glow_color="#00BFFF")
            ql = QVBoxLayout(squad_card)
            ql.setContentsMargins(20, 14, 20, 16)
            ql.setSpacing(12)
            total = sum(g.count for g in squad if not g.is_coach)
            head_t = QLabel(f"👥  球队阵容  ·  {total} 名球员")
            head_t.setStyleSheet("font-size:16px; font-weight:900;")
            ql.addWidget(head_t)

            all_cards: list[QWidget] = []
            for grp in squad:
                if not grp.members:
                    continue
                accent = ROLE_COLOR.get(grp.title, "#00BFFF")
                sec = QLabel(f"{grp.title}  ·  {grp.count}")
                sec.setStyleSheet(
                    f"color:{accent}; font-size:13px; font-weight:900;"
                    " letter-spacing:0.5px; padding-top:4px;"
                )
                ql.addWidget(sec)
                grid = CardGrid(
                    SquadPlayerCard.CARD_W, SquadPlayerCard.CARD_H,
                    h_spacing=14, v_spacing=14,
                )
                cards = []
                for member in grp.members:
                    pc = SquadPlayerCard(member)
                    pc.clicked.connect(self.player_clicked.emit)
                    cards.append(pc)
                    all_cards.append(pc)
                grid.add_cards(cards)
                ql.addWidget(grid)

            self._body.addWidget(squad_card)
            stagger_fade(all_cards, step=18, dx=0, dy=0)

        # ── 全部比赛 ───────────────────────
        m_card = Card(padding=18, glow_color="#2ED883")
        m_lay = QVBoxLayout(m_card)
        m_lay.setContentsMargins(20, 14, 20, 14)
        m_lay.setSpacing(10)
        m_title = QLabel(f"📅  全部比赛  ·  {len(matches)} 场")
        m_title.setStyleSheet("font-size:16px; font-weight:900;")
        m_lay.addWidget(m_title)
        grid = FlowLayout()
        for m in matches:
            mc = MatchCard(m)
            mc.clicked.connect(self.match_clicked.emit)
            grid.addWidget(mc)
        m_lay.addLayout(grid)
        if not matches:
            m_lay.addWidget(QLabel("暂无该队比赛数据"))
        self._body.addWidget(m_card)

        self._body.addStretch(1)

    def _contributor_card(
        self,
        icon: str,
        title: str,
        players: list[PlayerRanking],
        *,
        kind: str,
        accent: str,
    ) -> Card:
        card = Card(padding=18, glow_color=accent)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        ic = QLabel(icon); ic.setStyleSheet("font-size:16px;")
        head.addWidget(ic)
        t = QLabel(title)
        t.setStyleSheet(f"color:{accent}; font-size:14.5px; font-weight:900;")
        head.addWidget(t)
        head.addStretch(1)
        cnt = QLabel(f"{len(players)} 人")
        cnt.setStyleSheet("color:#B0BEC5; font-size:11.5px; font-weight:700;")
        head.addWidget(cnt)
        lay.addLayout(head)

        if not players:
            empty_card = QFrame()
            empty_card.setMinimumHeight(80)
            empty_card.setStyleSheet(
                "background: rgba(255,255,255,0.03); border-radius:12px;"
                "border: 1px dashed rgba(255,255,255,0.08);"
            )
            ev = QVBoxLayout(empty_card)
            ev.addStretch(1)
            l = QLabel(f"暂无{kind == 'goals' and '进球' or '助攻'}记录")
            l.setStyleSheet("color:#56607D; font-size:12px;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ev.addWidget(l)
            ev.addStretch(1)
            lay.addWidget(empty_card)
            lay.addStretch(1)
            return card

        for p in players[:10]:
            row = _ContributorRow(p, p.count or 0, kind)
            row.clicked.connect(self.player_clicked.emit)
            lay.addWidget(row)
        lay.addStretch(1)
        return card


    # ─────────────────────────────────────────
    # 赛前预测卡（whoscored「Prediction」复刻）
    # ─────────────────────────────────────────
    _RESULT_PILL = {"W": ("#2ED883", "胜"), "D": ("#FFD700", "平"), "L": ("#FF4E5E", "负")}
    _SWOT_STYLE = {
        "优势": ("#2ED883", "💪"),
        "劣势": ("#FF6B6B", "⚠️"),
        "机会": ("#4FC3F7", "🎯"),
        "威胁": ("#FFB74D", "🛡"),
    }

    def _outlook_card(self, outlook: TeamOutlook) -> Card:
        card = Card(padding=18, glow_color="#6A5ACD")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(8)
        t = QLabel("🔮  赛前预测")
        t.setStyleSheet("font-size:16px; font-weight:900;")
        head.addWidget(t)
        head.addStretch(1)
        src = QLabel("AI 模型推算 · 复刻 WhoScored 前瞻")
        src.setStyleSheet("color:#8B93A7; font-size:11px; font-weight:700;")
        head.addWidget(src)
        lay.addLayout(head)

        if not outlook.has_next or outlook.prediction is None:
            # 无后续赛程 —— 仅展示结论 + SWOT + 近期战绩
            v = QLabel(f"📌  {outlook.verdict}")
            v.setStyleSheet(
                "color:#FFD700; font-size:13px; font-weight:800;"
                "background:rgba(255,197,61,0.10); border-radius:10px; padding:8px 12px;"
            )
            v.setWordWrap(True)
            lay.addWidget(v)
            lay.addLayout(self._form_row("近期战绩", outlook.form))
            lay.addWidget(self._swot_block(outlook.swot))
            return card

        pred = outlook.prediction
        m = outlook.next_match

        # 对阵行
        opp_row = QHBoxLayout()
        opp_row.setSpacing(10)
        lead = QLabel("下一场对阵")
        lead.setStyleSheet("color:#B0BEC5; font-size:12px; font-weight:700;")
        opp_row.addWidget(lead)
        opp_row.addWidget(TeamLogo(outlook.opp_logo, size=26, shape="circle"))
        opp_w = QWidget()
        opp_inner = QHBoxLayout(opp_w)
        opp_inner.setContentsMargins(0, 0, 0, 0)
        opp_inner.setSpacing(6)
        opp_name = QLabel(outlook.opp_name)
        opp_name.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:800;")
        opp_inner.addWidget(opp_name)
        opp_w.setCursor(pointing_hand_cursor())
        # 点击对手 → 进入下一场比赛详情
        opp_w.mousePressEvent = (  # type: ignore[assignment]
            lambda _e: self.match_clicked.emit(m)
        )
        opp_row.addWidget(opp_w)
        opp_row.addStretch(1)
        where = "主场" if outlook.is_home else "客场"
        bits = [where]
        if outlook.group_name:
            bits.append(outlook.group_name)
        if m and m.start_play:
            bits.append(fmt_relative(m.start_play))
        meta = QLabel("　·　".join(bits))
        meta.setStyleSheet("color:#8B93A7; font-size:11.5px;")
        opp_row.addWidget(meta)
        lay.addLayout(opp_row)

        # 胜 / 平 / 负 概率条
        head_r = QHBoxLayout()
        la = QLabel(f"{outlook.self_name} 胜")
        la.setStyleSheet("color:#2ED883; font-size:12px; font-weight:800;")
        ld = QLabel("平")
        ld.setStyleSheet("color:#B0BEC5; font-size:12px; font-weight:800;")
        ld.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb = QLabel(f"{outlook.opp_name} 胜")
        lb.setStyleSheet("color:#FF5470; font-size:12px; font-weight:800;")
        lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        head_r.addWidget(la, 1); head_r.addWidget(ld, 1); head_r.addWidget(lb, 1)
        lay.addLayout(head_r)
        lay.addWidget(self._prob_bar(outlook.self_win, outlook.draw, outlook.opp_win))

        pct = QHBoxLayout()
        for val, color, align in (
            (outlook.self_win, "#2ED883", Qt.AlignmentFlag.AlignLeft),
            (outlook.draw, "#B0BEC5", Qt.AlignmentFlag.AlignCenter),
            (outlook.opp_win, "#FF5470", Qt.AlignmentFlag.AlignRight),
        ):
            pl = QLabel(f"{round(val * 100)}%")
            pl.setStyleSheet(f"color:{color}; font-size:13px; font-weight:900;")
            pl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            pct.addWidget(pl, 1)
        lay.addLayout(pct)

        # 预测比分 + 结论
        score_row = QHBoxLayout()
        score_row.setSpacing(10)
        sc = QLabel(f"预测比分  {outlook.predicted_score}")
        sc.setStyleSheet(
            "color:#46D2FF; font-size:13px; font-weight:900;"
            "background:rgba(70,210,255,0.10); border-radius:10px; padding:6px 12px;"
        )
        score_row.addWidget(sc)
        eg = QLabel(
            f"预期总进球 {pred.expected_goals:.1f}　·　大 2.5 概率 "
            f"{round(pred.over25_prob * 100)}%　·　双方进球 {round(pred.btts_prob * 100)}%"
        )
        eg.setStyleSheet("color:#9AA3BE; font-size:11.5px;")
        eg.setWordWrap(True)
        score_row.addWidget(eg, 1)
        lay.addLayout(score_row)

        verdict = QLabel(f"📌  {outlook.verdict}")
        verdict.setStyleSheet(
            "color:#FFD700; font-size:13px; font-weight:800;"
            "background:rgba(255,197,61,0.10); border-radius:10px; padding:8px 12px;"
        )
        verdict.setWordWrap(True)
        lay.addWidget(verdict)

        # 三大市场倾向
        lay.addWidget(HLine())
        trends_lbl = QLabel("🤖  核心市场倾向")
        trends_lbl.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
        lay.addWidget(trends_lbl)
        chips = QHBoxLayout()
        chips.setSpacing(10)
        for tr in pred.trends:
            chips.addWidget(self._trend_chip(tr.category, tr.headline, tr.probability), 1)
        lay.addLayout(chips)

        # 近期战绩
        lay.addLayout(self._form_row("近期战绩", outlook.form))

        # SWOT
        lay.addWidget(self._swot_block(outlook.swot))
        return card

    def _trend_chip(self, category: str, headline: str, prob: float) -> QWidget:
        w = QFrame()
        w.setStyleSheet(
            "QFrame{background: rgba(255,255,255,0.04); border-radius:12px;"
            " border:1px solid rgba(255,255,255,0.07);}"
        )
        col = QVBoxLayout(w)
        col.setContentsMargins(12, 9, 12, 9)
        col.setSpacing(3)
        cat = QLabel(category)
        cat.setStyleSheet("color:#8B93A7; font-size:10.5px; font-weight:800;")
        col.addWidget(cat)
        hl = QLabel(headline)
        hl.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:900;")
        hl.setWordWrap(True)
        col.addWidget(hl)
        pr = QLabel(f"命中概率 {round(prob * 100)}%")
        pr.setStyleSheet("color:#46D2FF; font-size:11px; font-weight:700;")
        col.addWidget(pr)
        return w

    def _prob_bar(self, pa: float, pd: float, pb: float) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(3)
        total = (pa + pd + pb) or 1.0
        for val, color, r in (
            (pa, "#2ED883", "left"),
            (pd, "#B0BEC5", "mid"),
            (pb, "#FF5470", "right"),
        ):
            seg = QFrame()
            radius = (
                "border-top-left-radius:8px;border-bottom-left-radius:8px;"
                if r == "left" else
                "border-top-right-radius:8px;border-bottom-right-radius:8px;"
                if r == "right" else ""
            )
            seg.setStyleSheet(f"background:{color}; border-radius:3px; {radius}")
            row.addWidget(seg, max(1, int(val / total * 1000)))
        return bar

    def _form_row(self, title: str, form) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        nm = QLabel(title)
        nm.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:800;")
        nm.setFixedWidth(80)
        row.addWidget(nm)
        games = getattr(form, "games", []) or []
        if not games:
            na = QLabel("暂无近期战绩")
            na.setStyleSheet("color:#56607D; font-size:12px;")
            row.addWidget(na)
            row.addStretch(1)
            return row
        for g in games:
            c, ch = self._RESULT_PILL.get(g.result, ("#B0BEC5", "—"))
            pill = QLabel(ch)
            pill.setFixedSize(22, 22)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setStyleSheet(
                f"background:{c}; color:#0B0E16; border-radius:11px;"
                "font-size:11px; font-weight:900;"
            )
            pill.setToolTip(f"{g.opponent}  {g.score}")
            row.addWidget(pill)
        row.addStretch(1)
        return row

    def _swot_block(self, swot: dict) -> QWidget:
        w = QWidget()
        grid = QGridLayout(w)
        grid.setContentsMargins(0, 4, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        keys = ["优势", "劣势", "机会", "威胁"]
        for i, key in enumerate(keys):
            color, icon = self._SWOT_STYLE[key]
            cell = QVBoxLayout()
            cell.setSpacing(3)
            h = QLabel(f"{icon}  {key}")
            h.setStyleSheet(f"color:{color}; font-size:12.5px; font-weight:800;")
            cell.addWidget(h)
            for item in (swot.get(key) or [])[:3]:
                il = QLabel(f"· {item}")
                il.setStyleSheet("color:#9AA3BE; font-size:11.5px;")
                il.setWordWrap(True)
                cell.addWidget(il)
            holder = QWidget(); holder.setLayout(cell)
            grid.addWidget(holder, i // 2, i % 2)
        return w

    # ─────────────────────────────────────────
    # 球员布阵评分卡（whoscored「Probable Lineup + Ratings」复刻）
    # ─────────────────────────────────────────
    def _formation_card(self, formation: TeamFormation) -> Card:
        card = Card(padding=18, glow_color="#2ED883")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(10)
        t = QLabel("📋  球员布阵评分")
        t.setStyleSheet("font-size:16px; font-weight:900;")
        head.addWidget(t)
        fm = QLabel(formation.formation)
        fm.setStyleSheet(
            "color:#FFD700; font-size:13px; font-weight:900;"
            "background:rgba(255,215,0,0.12); border-radius:9px; padding:3px 10px;"
        )
        head.addWidget(fm)
        head.addStretch(1)
        avg = QLabel(f"全队均分 {formation.avg_rating:.2f}")
        avg.setStyleSheet(
            f"color:{rating_color(formation.avg_rating)}; font-size:13px; font-weight:900;"
        )
        head.addWidget(avg)
        lay.addLayout(head)

        hint = QLabel("预测首发 11 人 + 评分（基于真实阵容由模型推算，仅供参考）")
        hint.setStyleSheet("color:#8B93A7; font-size:11.5px;")
        lay.addWidget(hint)

        # 球星亮点
        if formation.star is not None:
            star = formation.star
            star_row = QFrame()
            star_row.setStyleSheet(
                "QFrame{background:rgba(255,215,0,0.08); border-radius:12px;"
                " border:1px solid rgba(255,215,0,0.30);}"
            )
            sr = QHBoxLayout(star_row)
            sr.setContentsMargins(14, 8, 14, 8)
            sr.setSpacing(10)
            sr.addWidget(PlayerAvatar(star.logo, size=40))
            sb = QVBoxLayout(); sb.setSpacing(1)
            sn = QLabel(f"⭐  {star.name}")
            sn.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:900;")
            sb.addWidget(sn)
            smeta = QLabel(f"{star.role}  ·  预期全队最高分")
            smeta.setStyleSheet("color:#9AA3BE; font-size:11px;")
            sb.addWidget(smeta)
            sr.addLayout(sb, 1)
            srate = QLabel(f"{star.rating:.2f}")
            srate.setStyleSheet(
                f"color:{rating_color(star.rating)}; font-size:22px; font-weight:900;"
            )
            sr.addWidget(srate)
            star_wrap = star_row
            star_wrap.setCursor(pointing_hand_cursor())
            star_wrap.mousePressEvent = (  # type: ignore[assignment]
                lambda _e, pid=star.person_id, nm=star.name: self.player_clicked.emit(pid, nm)
            )
            lay.addWidget(star_wrap)

        # 布阵球场
        pitch = FormationPitch(formation.players, formation.formation, accent="#2ED883")
        pitch.player_clicked.connect(self.player_clicked.emit)
        lay.addWidget(pitch)

        # 评分 TOP3
        if formation.key_players:
            lay.addWidget(HLine())
            kp_lbl = QLabel("评分预期 TOP 3")
            kp_lbl.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
            lay.addWidget(kp_lbl)
            kp_row = QHBoxLayout()
            kp_row.setSpacing(10)
            for rp in formation.key_players:
                kp_row.addWidget(self._rated_chip(rp), 1)
            lay.addLayout(kp_row)
        return card

    def _rated_chip(self, rp) -> QWidget:
        w = QFrame()
        w.setStyleSheet(
            "QFrame{background: rgba(255,255,255,0.04); border-radius:12px;"
            " border:1px solid rgba(255,255,255,0.07);}"
            "QFrame:hover{border:1px solid #2ED883;}"
        )
        w.setCursor(pointing_hand_cursor())
        w.mousePressEvent = (  # type: ignore[assignment]
            lambda _e, pid=rp.person_id, nm=rp.name: self.player_clicked.emit(pid, nm)
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(10)
        row.addWidget(PlayerAvatar(rp.logo, size=36))
        col = QVBoxLayout(); col.setSpacing(1)
        n = QLabel(rp.name)
        n.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:800;")
        col.addWidget(n)
        rl = QLabel(rp.role)
        rl.setStyleSheet("color:#9AA3BE; font-size:10.5px;")
        col.addWidget(rl)
        row.addLayout(col, 1)
        rate = QLabel(f"{rp.rating:.1f}")
        rate.setStyleSheet(
            f"color:{rating_color(rp.rating)}; font-size:18px; font-weight:900;"
        )
        row.addWidget(rate)
        return w
