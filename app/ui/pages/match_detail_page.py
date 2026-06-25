"""比赛详情页：双方队伍 + 比分 + 元数据 + 赛前前瞻。

针对「未开赛比赛信息太空」的问题，本页对所有比赛（尤其 Fixture 未开赛）
基于公开接口已有的数据，补齐了一套**真实可得**的赛前前瞻信息：

* 开赛倒计时 + 本地开球时间。
* 双方小组排名（名次 / 积分 / 胜平负 / 净胜球）。
* 两队近期战绩（最近 5 场 W/D/L 走势 + 比分）。
* 历史交锋（本数据集内两队过往对阵的胜平负与比分列表）。

这些数据全部由 ``schedule`` 与 ``standing`` 两个接口聚合计算，不臆造。
（懂球帝并未公开「赛前预测阵容 / 事件流」接口，故不展示这两项。）
"""
from __future__ import annotations

import math

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.models.lineup import MatchLineup, TeamLineup
from app.models.odds import MatchOdds
from app.ui.design.app_cursor import pointing_hand_cursor
from app.models.standing import GroupStanding, TeamStanding
from app.services.data_service import DataService
from app.services.favorites import Favorites
from app.ui.pages.base import BasePage
from app.ui.widgets.favorite_button import FavoriteButton
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.lineup_pitch import LineupPitch
from app.ui.widgets.misc import Card
from app.ui.widgets.team_logo import TeamLogo
from app.utils.time_utils import fmt_datetime, fmt_relative, fmt_short_date


class _MatchHero(QWidget):
    """比赛详情顶部：自绘渐变背景 + 双方队伍 + 比分。"""

    team_clicked = pyqtSignal(str)

    def __init__(self, match: Match) -> None:
        super().__init__()
        self._match = match
        self.setMinimumHeight(220)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        outer = QHBoxLayout(self)
        outer.setContentsMargins(36, 28, 36, 28)
        outer.setSpacing(16)

        # 队 A
        outer.addLayout(self._team_col(match.team_a_id, match.team_a_logo, match.team_a_name), 4)

        # 比分
        center = QVBoxLayout()
        center.setSpacing(6)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score = QLabel(match.display_score)
        f = QFont(); f.setPointSize(44); f.setBold(True)
        score.setFont(f)
        score.setStyleSheet("color: #FFD700;")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(score)

        if match.is_live:
            status_lbl = QLabel(f"🔴 直播  {match.minute or '·'}'")
            status_lbl.setStyleSheet(
                "background: #ff3057; color: white;"
                "border-radius: 12px; padding: 4px 16px;"
                "font-weight:800; font-size: 12px;"
            )
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            center.addWidget(status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            status_lbl = QLabel(match.status.label)
            status_lbl.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-weight:700;"
            )
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            center.addWidget(status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addLayout(center, 3)

        # 队 B
        outer.addLayout(self._team_col(match.team_b_id, match.team_b_logo, match.team_b_name), 4)

    def _team_col(self, team_id: str, logo: str | None, name: str) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(10)
        col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(TeamLogo(logo, size=96, shape="circle"), alignment=Qt.AlignmentFlag.AlignCenter)
        n = QLabel(name)
        f = QFont(); f.setPointSize(16); f.setBold(True)
        n.setFont(f)
        n.setStyleSheet("color: white;")
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        n.setWordWrap(True)
        col.addWidget(n)
        # 包裹一个透明可点击层，让整列点击=进入球队详情
        w = QWidget()
        w.setLayout(col)
        w.setCursor(pointing_hand_cursor())
        w.mousePressEvent = lambda _e, t=team_id: self.team_clicked.emit(t)  # type: ignore[assignment]
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(w, alignment=Qt.AlignmentFlag.AlignCenter)
        return outer

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(
            float(rect.x()),
            float(rect.y()),
            float(rect.width()),
            float(rect.height()),
            18.0,
            18.0,
        )
        from PyQt6.QtGui import QLinearGradient
        from PyQt6.QtCore import QPointF
        grad = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        grad.setColorAt(0.0, QColor("#0A1426"))
        grad.setColorAt(0.55, QColor("#16294A"))
        grad.setColorAt(1.0, QColor("#0B1020"))
        p.fillPath(path, grad)


# ── 走势小药丸（W/D/L） ───────────────────────────────────
_RESULT_STYLE = {
    "W": ("#2ED883", "胜"),
    "D": ("#FFD700", "平"),
    "L": ("#FF4E5E", "负"),
}


def _form_pill(result: str) -> QLabel:
    color, ch = _RESULT_STYLE.get(result, ("#B0BEC5", "—"))
    lbl = QLabel(ch)
    lbl.setFixedSize(22, 22)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background:{color}; color:#0B0E16; border-radius:11px;"
        "font-size:11px; font-weight:900;"
    )
    return lbl


# ── 赛前分析配色 ───────────────────────────────────────────
_ANALYSIS_A = "#FF5470"     # 主队（队 A）
_ANALYSIS_DRAW = "#B0BEC5"  # 平局
_ANALYSIS_B = "#00BFFF"     # 客队（队 B）


class _ProbBar(QWidget):
    """胜/平/负三段式概率条（队 A 胜 · 平 · 队 B 胜）。"""

    def __init__(self, pa: float, pd: float, pb: float) -> None:
        super().__init__()
        self._pa = max(0.0, pa)
        self._pd = max(0.0, pd)
        self._pb = max(0.0, pb)
        self.setFixedHeight(26)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        total = self._pa + self._pd + self._pb or 1.0
        segs = [
            (self._pa / total, QColor(_ANALYSIS_A)),
            (self._pd / total, QColor(_ANALYSIS_DRAW)),
            (self._pb / total, QColor(_ANALYSIS_B)),
        ]
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(w), float(h), 8.0, 8.0)
        p.setClipPath(path)
        x = 0.0
        p.setPen(Qt.PenStyle.NoPen)
        for frac, col in segs:
            seg_w = frac * w
            if seg_w <= 0:
                continue
            p.fillRect(QRectF(x, 0, seg_w + 1, h), col)
            # 段内百分比（够宽才画）
            if seg_w > 34:
                p.setPen(QColor("#0B0E16"))
                font = p.font(); font.setBold(True); font.setPointSize(9)
                p.setFont(font)
                p.drawText(QRectF(x, 0, seg_w, h),
                           Qt.AlignmentFlag.AlignCenter, f"{round(frac * 100)}%")
                p.setPen(Qt.PenStyle.NoPen)
            x += seg_w


class MatchDetailPage(BasePage):
    title = "比赛详情"
    subtitle = ""

    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)
    back_clicked = pyqtSignal()
    prediction_clicked = pyqtSignal(Match)

    def __init__(self, service: DataService, favorites: Favorites) -> None:
        super().__init__()
        self._service = service
        self._favorites = favorites
        self._match: Match | None = None
        self._all_matches: list[Match] = []
        self._groups: list[GroupStanding] = []
        self._lineup: MatchLineup | None = None
        self._odds: "MatchOdds | None" = None

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

        top_row = QHBoxLayout()
        back = QPushButton("← 返回")
        back.setProperty("ghost", True)
        back.setCursor(pointing_hand_cursor())
        back.setFixedWidth(80)
        back.clicked.connect(self.back_clicked.emit)
        top_row.addWidget(back)
        top_row.addStretch(1)
        self._predict_btn = QPushButton("🔮 完整预测")
        self._predict_btn.setCursor(pointing_hand_cursor())
        self._predict_btn.setStyleSheet(
            "QPushButton{background:rgba(61,139,255,0.16); color:#9CC4FF;"
            "border:1px solid rgba(61,139,255,0.45); border-radius:12px;"
            "padding:6px 16px; font-weight:800; font-size:12px;}"
            "QPushButton:hover{background:rgba(61,139,255,0.28); color:#FFFFFF;}"
        )
        self._predict_btn.clicked.connect(
            lambda: self._match and self.prediction_clicked.emit(self._match)
        )
        top_row.addWidget(self._predict_btn)
        self._fav_btn = FavoriteButton(favorites, "match", "")
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

    # ── 对外入口 ──────────────────────────────
    def open_match(self, match: Match) -> None:
        self._match = match
        self._lineup = None
        self._odds = None
        self._fav_btn.set_entity("match", match.match_id)
        self._render()
        self.show_content()
        # 异步补齐前瞻上下文（赛程 + 积分榜 + 阵容）
        self.refresh(force=False)

    def refresh(self, force: bool = False) -> None:
        if not self._match:
            return

        async def runner() -> None:
            _rounds, matches = await self._service.fetch_full_schedule(force=force)
            self._all_matches = matches
            for m in matches:
                if m.match_id == self._match.match_id:  # type: ignore[union-attr]
                    self._match = m
                    break
            try:
                groups, _ko, _km = await self._service.fetch_standings(force=force)
                self._groups = groups
            except Exception:  # pragma: no cover - 网络
                self._groups = []
            try:
                self._lineup = await self._service.fetch_match_lineup(
                    self._match.match_id, force=force  # type: ignore[union-attr]
                )
            except Exception:  # pragma: no cover - 网络
                self._lineup = None
            try:
                self._odds = await self._service.fetch_match_odds(
                    self._match.match_id, force=force  # type: ignore[union-attr]
                )
            except Exception:  # pragma: no cover - 网络
                self._odds = None
            self._render()

        self.run_async(runner)

    # ── 数据计算 ──────────────────────────────
    def _find_standing(self, team_id: str) -> tuple[str, TeamStanding] | None:
        for g in self._groups:
            for ts in g.teams:
                if ts.team_id == team_id:
                    return g.name, ts
        return None

    def _recent_form(self, team_id: str, limit: int = 5) -> list[tuple[Match, str]]:
        """返回某队最近 ``limit`` 场已结束比赛及其 W/D/L。"""
        played = [
            m for m in self._all_matches
            if m.status == MatchStatus.PLAYED
            and team_id in (m.team_a_id, m.team_b_id)
            and (self._match is None or m.match_id != self._match.match_id)
        ]
        played.sort(key=lambda x: x.start_play or x.date_utc or "", reverse=True)
        out: list[tuple[Match, str]] = []
        for m in played[:limit]:
            win = m.winner_id
            if win is None:
                res = "D"
            elif win == team_id:
                res = "W"
            else:
                res = "L"
            out.append((m, res))
        return out

    def _head_to_head(self) -> list[Match]:
        m = self._match
        if m is None:
            return []
        pair = {m.team_a_id, m.team_b_id}
        h2h = [
            x for x in self._all_matches
            if x.status == MatchStatus.PLAYED
            and {x.team_a_id, x.team_b_id} == pair
            and x.match_id != m.match_id
        ]
        h2h.sort(key=lambda x: x.start_play or x.date_utc or "", reverse=True)
        return h2h

    # ── 渲染 ─────────────────────────────────
    def _render(self) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        m = self._match
        if m is None:
            return

        hero = _MatchHero(m)
        hero.team_clicked.connect(self.team_clicked.emit)
        self._body.addWidget(hero)

        # 未开赛：醒目倒计时条
        if m.status == MatchStatus.FIXTURE and m.start_play:
            self._body.addWidget(self._countdown_card(m))

        # 赛前综合分析（胜负概率 / 实力对比 / 攻防 / 看点）—— 本页核心
        analysis_card = self._analysis_card(m)
        if analysis_card is not None:
            self._body.addWidget(analysis_card)

        # 实时赔率（欧赔 / 亚盘 / 大小球）—— 懂球帝实时数据
        odds_card = self._odds_card()
        if odds_card is not None:
            self._body.addWidget(odds_card)

        # 阵容布阵图（首发 / 赛前预测）—— 本页核心
        lineup_card = self._lineup_card()
        if lineup_card is not None:
            self._body.addWidget(lineup_card)

        # 赛前前瞻：双方小组排名对比
        standings_card = self._standings_card(m)
        if standings_card is not None:
            self._body.addWidget(standings_card)

        # 近期战绩
        form_card = self._form_card(m)
        if form_card is not None:
            self._body.addWidget(form_card)

        # 历史交锋
        h2h_card = self._h2h_card(m)
        if h2h_card is not None:
            self._body.addWidget(h2h_card)

        # 元数据卡
        self._body.addWidget(self._meta_card(m))

        self._body.addStretch(1)

    def _section_title(self, layout: QVBoxLayout, text: str) -> None:
        t = QLabel(text)
        t.setStyleSheet("font-size:15px; font-weight:800;")
        layout.addWidget(t)

    # ── 实时赔率 ──────────────────────────────
    def _odds_card(self) -> QWidget | None:
        odds = self._odds
        m = self._match
        if odds is None or m is None or not odds.has_odds:
            return None
        if not (odds.euro or odds.asia or odds.size or odds.avg):
            return None

        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 18)
        lay.setSpacing(12)
        self._section_title(lay, "💹  实时赔率")
        sub = QLabel("欧赔 · 亚盘 · 大小球 · 懂球帝实时（初盘 → 即时）")
        sub.setStyleSheet("color:#B0BEC5; font-size:11.5px; font-weight:600;")
        lay.addWidget(sub)

        a_name, b_name = m.team_a_name, m.team_b_name

        # 平均欧赔大屏：主胜 / 平 / 客胜
        if odds.avg is not None:
            avg = odds.avg
            big = QHBoxLayout()
            big.setSpacing(10)
            for label, val in ((f"{a_name} 胜", avg.home), ("平局", avg.draw),
                               (f"{b_name} 胜", avg.away)):
                cell = QVBoxLayout()
                cell.setSpacing(2)
                v = QLabel(val)
                v.setAlignment(Qt.AlignmentFlag.AlignCenter)
                v.setStyleSheet("color:#FFD700; font-size:26px; font-weight:900;")
                cell.addWidget(v)
                lab = QLabel(label)
                lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lab.setStyleSheet("color:#B0BEC5; font-size:11px; font-weight:700;")
                cell.addWidget(lab)
                cw = QWidget()
                cw.setLayout(cell)
                cw.setStyleSheet(
                    "background: rgba(255,255,255,0.04); border-radius:12px;"
                    "border:1px solid rgba(255,215,0,0.25);")
                big.addWidget(cw, 1)
            lay.addLayout(big)
            tip = QLabel("以上为各机构平均欧赔（1X2）")
            tip.setStyleSheet("color:#6B7689; font-size:10.5px;")
            lay.addWidget(tip)

        # 欧赔明细
        if odds.euro:
            lay.addWidget(self._odds_table(
                "欧赔 · 1X2（主 / 平 / 客）",
                ["机构", "主胜", "平", "客胜"],
                [[e.name, (e.home, e.home_trend), e.draw, (e.away, e.away_trend)]
                 for e in odds.euro[:8]],
            ))
        # 亚盘
        if odds.asia:
            lay.addWidget(self._odds_table(
                "亚盘 · 让球（盘口 / 主水 / 客水）",
                ["机构", "盘口", "主", "客"],
                [[h.name, h.line, h.a, h.b] for h in odds.asia[:6]],
            ))
        # 大小球
        if odds.size:
            lay.addWidget(self._odds_table(
                "大小球（盘口 / 大球 / 小球）",
                ["机构", "盘口", "大", "小"],
                [[h.name, h.line, h.a, h.b] for h in odds.size[:6]],
            ))
        return card

    def _odds_table(self, title: str, headers: list[str], rows: list[list]) -> QWidget:
        """构建一个紧凑赔率表。单元格可为 str 或 (值, 升降) 元组。"""
        box = QVBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(6)
        t = QLabel(title)
        t.setStyleSheet("color:#E3E9F3; font-size:12.5px; font-weight:800;")
        box.addWidget(t)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(5)
        # 表头
        for c, h in enumerate(headers):
            hl = QLabel(h)
            hl.setStyleSheet("color:#6B7689; font-size:10.5px; font-weight:800;")
            if c == 0:
                hl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            else:
                hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(hl, 0, c)
        grid.setColumnStretch(0, 1)
        # 数据行
        _TREND = {1: ("▲", "#FF5470"), -1: ("▼", "#2ED877")}
        for r, row in enumerate(rows, start=1):
            for c, cell in enumerate(row):
                if isinstance(cell, tuple):
                    val, trend = cell
                    arrow, color = _TREND.get(trend, ("", "#FFFFFF"))
                    txt = f"{val} {arrow}".strip()
                else:
                    val = cell
                    color = "#FFFFFF" if c > 0 else "#B0BEC5"
                    txt = str(val)
                lbl = QLabel(txt)
                if c == 0:
                    lbl.setStyleSheet("color:#B0BEC5; font-size:11.5px; font-weight:700;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                else:
                    lbl.setStyleSheet(f"color:{color}; font-size:12px; font-weight:800;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(lbl, r, c)
        host = QWidget()
        host.setLayout(grid)
        host.setStyleSheet(
            "background: rgba(255,255,255,0.03); border-radius:12px;")
        box.addWidget(host)
        container = QWidget()
        container.setLayout(box)
        return container

    def _countdown_card(self, m: Match) -> QWidget:
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(6)
        row = QHBoxLayout()
        row.setSpacing(12)
        big = QLabel(fmt_relative(m.start_play).replace("还有 ", "").strip() or "即将开始")
        big.setStyleSheet("color:#FFD700; font-size:24px; font-weight:900;")
        row.addWidget(QLabel("⏳"))
        lead = QLabel("距开赛")
        lead.setStyleSheet("color:#B0BEC5; font-size:13px; font-weight:700;")
        row.addWidget(lead)
        row.addWidget(big)
        row.addStretch(1)
        when = QLabel(fmt_datetime(m.start_play))
        when.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:700;")
        row.addWidget(when)
        lay.addLayout(row)
        return card

    # ── 赛前综合分析 ──────────────────────────
    def _team_metrics(self, team_id: str) -> dict | None:
        """聚合一支球队的赛前指标：场均积分 / 攻防 / 状态 / 综合指数。

        数据全部来自积分榜 + 赛程近期战绩，无任何臆造；数据不足时返回 None。
        """
        info = self._find_standing(team_id)
        form = self._recent_form(team_id)

        mt = points = gp = ga = 0
        gd = 0
        rank = None
        if info is not None:
            ts = info[1]
            mt = ts.matches_total
            points = ts.points
            gp = ts.goals_pro
            ga = ts.goals_against
            gd = ts.goal_diff
            rank = ts.rank

        if mt == 0 and not form:
            return None

        ppm = points / mt if mt else 0.0           # 场均积分 0~3
        gfpm = gp / mt if mt else 0.0              # 场均进球
        gapm = ga / mt if mt else 0.0              # 场均失球

        # 近期状态分（W=3 / D=1 / L=0），归一化到 0~1
        if form:
            fp = sum(3 if r == "W" else 1 if r == "D" else 0 for _m, r in form)
            form_n = fp / (len(form) * 3)
        else:
            form_n = 0.5  # 无近期数据 → 中性

        ppm_n = ppm / 3.0
        gd_per = (gd / mt) if mt else 0.0
        gd_n = max(0.0, min(1.0, (gd_per + 3.0) / 6.0))  # [-3,3] → [0,1]

        # 综合指数 0~100（积分权重最高，其次状态，再到净胜球）
        index = 100.0 * (0.45 * ppm_n + 0.30 * form_n + 0.25 * gd_n)

        return {
            "rank": rank,
            "mt": mt,
            "ppm": ppm,
            "gfpm": gfpm,
            "gapm": gapm,
            "form": form,
            "form_n": form_n,
            "index": index,
        }

    @staticmethod
    def _win_probabilities(ia: float, ib: float) -> tuple[float, float, float]:
        """由两队综合指数估算 胜 / 平 / 负 概率（Elo 式 + 接近度决定平局）。"""
        diff = ia - ib
        pa_core = 1.0 / (1.0 + 10 ** (-diff / 40.0))   # A 不计平局时的胜率
        draw = 0.30 * (1.0 - min(1.0, abs(diff) / 60.0))
        draw = max(0.10, min(0.32, draw))
        win_a = pa_core * (1.0 - draw)
        win_b = (1.0 - pa_core) * (1.0 - draw)
        return win_a, draw, win_b

    def _key_points(self, name: str, met: dict | None) -> list[str]:
        """根据指标自动生成一支球队的「看点」短句。"""
        if met is None:
            return ["暂无足够数据"]
        pts: list[str] = []
        if met["rank"]:
            pts.append(f"小组排名第 {met['rank']}")
        gfpm, gapm = met["gfpm"], met["gapm"]
        if met["mt"]:
            if gfpm >= 2.0:
                pts.append(f"进攻火力强劲（场均 {gfpm:.1f} 球）")
            elif gfpm <= 0.8:
                pts.append(f"进攻乏力（场均 {gfpm:.1f} 球）")
            if gapm <= 0.7:
                pts.append(f"防守稳固（场均失 {gapm:.1f} 球）")
            elif gapm >= 1.8:
                pts.append(f"防线漏洞较多（场均失 {gapm:.1f} 球）")
        form = met["form"]
        if form:
            wins = sum(1 for _m, r in form if r == "W")
            losses = sum(1 for _m, r in form if r == "L")
            if wins >= max(3, len(form) - 1):
                pts.append(f"状态火热（近 {len(form)} 场 {wins} 胜）")
            elif losses >= max(3, len(form) - 1):
                pts.append(f"状态低迷（近 {len(form)} 场 {losses} 负）")
        if not pts:
            pts.append("整体表现均衡")
        return pts

    def _analysis_card(self, m: Match) -> QWidget | None:
        ma = self._team_metrics(m.team_a_id)
        mb = self._team_metrics(m.team_b_id)
        h2h = self._head_to_head()
        if ma is None and mb is None and not h2h:
            return None

        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section_title(lay, "🔍  赛前综合分析")
        sub = QLabel("基于小组积分、近期战绩与历史交锋自动测算")
        sub.setStyleSheet("color:#B0BEC5; font-size:12px;")
        lay.addWidget(sub)

        ia = ma["index"] if ma else 50.0
        ib = mb["index"] if mb else 50.0
        win_a, draw, win_b = self._win_probabilities(ia, ib)

        # ── 胜负概率条 ──
        prob_head = QHBoxLayout()
        la = QLabel(f"{m.team_a_name} 胜")
        la.setStyleSheet(f"color:{_ANALYSIS_A}; font-size:12px; font-weight:800;")
        ld = QLabel("平")
        ld.setStyleSheet(f"color:{_ANALYSIS_DRAW}; font-size:12px; font-weight:800;")
        ld.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb = QLabel(f"{m.team_b_name} 胜")
        lb.setStyleSheet(f"color:{_ANALYSIS_B}; font-size:12px; font-weight:800;")
        lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prob_head.addWidget(la, 1)
        prob_head.addWidget(ld, 1)
        prob_head.addWidget(lb, 1)
        lay.addLayout(prob_head)
        lay.addWidget(_ProbBar(win_a, draw, win_b))

        # ── 实力对比（综合指数 + 攻防）──
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        def head(c: int, text: str, color: str, align) -> None:
            l = QLabel(text)
            l.setStyleSheet(f"color:{color}; font-size:13px; font-weight:800;")
            l.setAlignment(align)
            grid.addWidget(l, 0, c)

        head(0, m.team_a_name, _ANALYSIS_A, Qt.AlignmentFlag.AlignLeft)
        mid = QLabel("指标"); mid.setStyleSheet("color:#B0BEC5; font-size:12px;")
        mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(mid, 0, 1)
        head(2, m.team_b_name, _ANALYSIS_B, Qt.AlignmentFlag.AlignRight)

        def metric_row(r: int, label: str, va: str, vb: str,
                       a_better: bool | None) -> None:
            a_col = "#FFD700" if a_better is True else "#FFFFFF"
            b_col = "#FFD700" if a_better is False else "#FFFFFF"
            al = QLabel(va)
            al.setStyleSheet(f"color:{a_col}; font-size:14px; font-weight:800;")
            grid.addWidget(al, r, 0)
            ml = QLabel(label)
            ml.setStyleSheet("color:#B0BEC5; font-size:12px;")
            ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(ml, r, 1)
            bl = QLabel(vb)
            bl.setStyleSheet(f"color:{b_col}; font-size:14px; font-weight:800;")
            bl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(bl, r, 2)

        def fmt(v, suffix=""):
            return f"{v:.1f}{suffix}" if isinstance(v, float) else f"{v}{suffix}"

        metric_row(1, "综合指数", f"{ia:.0f}", f"{ib:.0f}",
                   ia > ib if ia != ib else None)
        if ma and mb:
            metric_row(2, "场均积分", fmt(ma["ppm"]), fmt(mb["ppm"]),
                       ma["ppm"] > mb["ppm"] if ma["ppm"] != mb["ppm"] else None)
            metric_row(3, "场均进球", fmt(ma["gfpm"]), fmt(mb["gfpm"]),
                       ma["gfpm"] > mb["gfpm"] if ma["gfpm"] != mb["gfpm"] else None)
            metric_row(4, "场均失球", fmt(ma["gapm"]), fmt(mb["gapm"]),
                       ma["gapm"] < mb["gapm"] if ma["gapm"] != mb["gapm"] else None)
        lay.addLayout(grid)

        # ── 历史交锋倾向 ──
        if h2h:
            a_win = b_win = drawn = 0
            for x in h2h:
                w = x.winner_id
                if w is None:
                    drawn += 1
                elif w == m.team_a_id:
                    a_win += 1
                elif w == m.team_b_id:
                    b_win += 1
            h2h_lbl = QLabel(
                f"⚔️  历史交锋 {len(h2h)} 场：{m.team_a_name} {a_win} 胜 · "
                f"{drawn} 平 · {b_win} 胜 {m.team_b_name}"
            )
            h2h_lbl.setStyleSheet("color:#9AA3BE; font-size:12px;")
            h2h_lbl.setWordWrap(True)
            lay.addWidget(h2h_lbl)

        # ── 双方看点 ──
        points_row = QHBoxLayout()
        points_row.setSpacing(14)
        points_row.addLayout(self._points_col(m.team_a_name, ma, _ANALYSIS_A), 1)
        points_row.addLayout(self._points_col(m.team_b_name, mb, _ANALYSIS_B), 1)
        lay.addLayout(points_row)

        # ── 结论 ──
        if win_a > win_b and win_a >= draw:
            verdict = f"略占上风：{m.team_a_name}"
        elif win_b > win_a and win_b >= draw:
            verdict = f"略占上风：{m.team_b_name}"
        else:
            verdict = "势均力敌，平局风险较高"
        vl = QLabel(f"📌  分析结论：{verdict}")
        vl.setStyleSheet(
            "color:#FFD700; font-size:13px; font-weight:800;"
            "background:rgba(255,197,61,0.10); border-radius:10px; padding:8px 12px;"
        )
        vl.setWordWrap(True)
        lay.addWidget(vl)
        return card

    def _points_col(self, name: str, met: dict | None, color: str) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        head = QLabel(name)
        head.setStyleSheet(f"color:{color}; font-size:13px; font-weight:800;")
        col.addWidget(head)
        for s in self._key_points(name, met):
            l = QLabel(f"· {s}")
            l.setStyleSheet("color:#9AA3BE; font-size:12px;")
            l.setWordWrap(True)
            col.addWidget(l)
        col.addStretch(1)
        return col

    # ── 阵容布阵图 ────────────────────────────
    _TEAM_A_COLOR = "#FF5470"
    _TEAM_B_COLOR = "#F4F6FB"

    def _lineup_card(self) -> QWidget | None:
        lu = self._lineup
        if lu is None:
            return None
        card = Card(padding=0, hover=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)

        # 标题行
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        badge = QLabel("预测阵容" if lu.is_forecast else "首发阵容")
        badge.setStyleSheet(
            "background: rgba(46,216,131,0.16); color:#9DF5C4;"
            "border:1px solid rgba(46,216,131,0.45);"
            "border-radius:11px; padding:3px 12px;"
            "font-size:12px; font-weight:900;"
        )
        title_row.addWidget(badge)
        if lu.is_forecast:
            hint = QLabel("赛前预测，最终首发以官方公布为准")
            hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
            title_row.addWidget(hint)
        title_row.addStretch(1)
        lay.addLayout(title_row)

        # 队伍 + 阵型行
        head = QHBoxLayout()
        head.setSpacing(10)
        head.addLayout(
            self._lineup_team_head(lu.team_a, self._TEAM_A_COLOR, left=True), 1
        )
        center = QVBoxLayout()
        center.setSpacing(2)
        formations = QLabel(
            f"{lu.team_a.formation or '—'}　vs　{lu.team_b.formation or '—'}"
        )
        formations.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formations.setStyleSheet(
            "color:#FFD700; font-size:15px; font-weight:900;"
        )
        center.addWidget(formations)
        head.addLayout(center, 0)
        head.addLayout(
            self._lineup_team_head(lu.team_b, self._TEAM_B_COLOR, left=False), 1
        )
        lay.addLayout(head)

        # 球场布阵图
        pitch = LineupPitch(
            lu.team_a,
            lu.team_b,
            color_a=self._TEAM_A_COLOR,
            color_b=self._TEAM_B_COLOR,
        )
        pitch.player_clicked.connect(self.player_clicked.emit)
        lay.addWidget(pitch)

        # 场地 / 裁判 / 天气
        bits = [b for b in (
            (f"🏟 {lu.field_name}" if lu.field_name else ""),
            (f"🧑‍⚖️ 裁判 {lu.referee}" if lu.referee else ""),
            (f"🌤 {lu.weather}" if lu.weather else ""),
        ) if b]
        if bits:
            meta = QLabel("　·　".join(bits))
            meta.setStyleSheet("color:#B0BEC5; font-size:12px;")
            meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
            meta.setWordWrap(True)
            lay.addWidget(meta)

        # 替补席
        subs = self._subs_block(lu)
        if subs is not None:
            lay.addWidget(subs)

        return card

    def _lineup_team_head(self, team: TeamLineup, color: str, *, left: bool):
        row = QHBoxLayout()
        row.setSpacing(9)
        flag = FlagIcon(team.team_name, height=22)
        name = QLabel(team.team_name)
        name.setStyleSheet("color:#FFFFFF; font-size:15px; font-weight:800;")
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{color}; font-size:12px;")
        if left:
            row.addWidget(flag)
            row.addWidget(name)
            row.addWidget(dot)
            row.addStretch(1)
        else:
            row.addStretch(1)
            row.addWidget(dot)
            row.addWidget(name)
            row.addWidget(flag)
        wrap = QWidget()
        wrap.setLayout(row)
        wrap.setCursor(pointing_hand_cursor())
        wrap.mousePressEvent = (  # type: ignore[assignment]
            lambda _e, tid=team.team_id: self.team_clicked.emit(tid)
        )
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(wrap)
        return outer

    def _subs_block(self, lu: MatchLineup) -> QWidget | None:
        if not lu.team_a.subs and not lu.team_b.subs:
            return None
        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 4, 0, 0)
        col.setSpacing(8)
        head = QLabel("替补席")
        head.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
        col.addWidget(head)

        def team_subs(team: TeamLineup, color: str) -> QLabel:
            names = "  ".join(
                f"{(p.number + ' ') if p.number else ''}{p.name}"
                for p in team.subs
            ) or "无"
            lbl = QLabel(f"{team.team_name}：{names}")
            lbl.setStyleSheet(
                f"color:#9AA3BE; font-size:12px;"
                f"border-left:3px solid {color}; padding-left:9px;"
            )
            lbl.setWordWrap(True)
            return lbl

        col.addWidget(team_subs(lu.team_a, self._TEAM_A_COLOR))
        col.addWidget(team_subs(lu.team_b, self._TEAM_B_COLOR))
        return wrap

    def _standings_card(self, m: Match) -> QWidget | None:
        sa = self._find_standing(m.team_a_id)
        sb = self._find_standing(m.team_b_id)
        if not sa and not sb:
            return None
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(12)
        grp = (sa or sb)[0] if (sa or sb) else ""
        self._section_title(lay, f"📊  小组排名{('  ·  ' + grp) if grp else ''}")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        headers = ["球队", "排名", "积分", "胜", "平", "负", "净胜"]
        for c, h in enumerate(headers):
            hl = QLabel(h)
            hl.setStyleSheet("color:#B0BEC5; font-size:11px; font-weight:700;")
            if c > 0:
                hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(hl, 0, c)

        def add_team_row(r: int, info: tuple[str, TeamStanding] | None,
                         team_name: str, team_id: str) -> None:
            name_w = QWidget()
            nrow = QHBoxLayout(name_w)
            nrow.setContentsMargins(0, 0, 0, 0)
            nrow.setSpacing(9)
            nrow.addWidget(FlagIcon(team_name, height=24))
            nl = QLabel(team_name)
            nl.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
            nrow.addWidget(nl)
            nrow.addStretch(1)
            name_w.setCursor(pointing_hand_cursor())
            name_w.mousePressEvent = (  # type: ignore[assignment]
                lambda _e, tid=team_id: self.team_clicked.emit(tid)
            )
            grid.addWidget(name_w, r, 0)
            if info is None:
                na = QLabel("未进入积分榜")
                na.setStyleSheet("color:#56607D; font-size:12px;")
                grid.addWidget(na, r, 1, 1, 6)
                return
            ts = info[1]
            vals = [
                str(ts.rank), str(ts.points), str(ts.matches_won),
                str(ts.matches_draw), str(ts.matches_lost),
                f"{ts.goal_diff:+d}",
            ]
            for c, v in enumerate(vals, start=1):
                vl = QLabel(v)
                vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                strong = c in (1, 2)
                vl.setStyleSheet(
                    f"color:{'#FFD700' if c == 2 else '#FFFFFF'};"
                    f"font-size:13px; font-weight:{'900' if strong else '600'};"
                )
                grid.addWidget(vl, r, c)

        add_team_row(1, sa, m.team_a_name, m.team_a_id)
        add_team_row(2, sb, m.team_b_name, m.team_b_id)
        lay.addLayout(grid)
        return card

    def _form_card(self, m: Match) -> QWidget | None:
        fa = self._recent_form(m.team_a_id)
        fb = self._recent_form(m.team_b_id)
        if not fa and not fb:
            return None
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(12)
        self._section_title(lay, "📈  近期战绩（近 5 场）")

        cols = QHBoxLayout()
        cols.setSpacing(18)
        cols.addLayout(self._team_form_col(m.team_a_name, m.team_a_id, fa), 1)
        cols.addLayout(self._team_form_col(m.team_b_name, m.team_b_id, fb), 1)
        lay.addLayout(cols)
        return card

    def _team_form_col(self, team_name: str, team_id: str,
                       form: list[tuple[Match, str]]) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(8)
        head = QHBoxLayout()
        head.setSpacing(9)
        head.addWidget(FlagIcon(team_name, height=24))
        nl = QLabel(team_name)
        nl.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
        head.addWidget(nl)
        head.addStretch(1)
        pills = QHBoxLayout()
        pills.setSpacing(4)
        for _m, res in form:
            pills.addWidget(_form_pill(res))
        head.addLayout(pills)
        col.addLayout(head)

        if not form:
            none = QLabel("暂无已结束的比赛记录")
            none.setStyleSheet("color:#56607D; font-size:12px;")
            col.addWidget(none)
            return col

        for mt, res in form:
            line = QLabel(self._form_line(mt, team_id))
            color = _RESULT_STYLE.get(res, ("#B0BEC5", ""))[0]
            line.setStyleSheet(f"color:#9AA3BE; font-size:12px; border-left:3px solid {color}; padding-left:8px;")
            col.addWidget(line)
        return col

    @staticmethod
    def _form_line(mt: Match, team_id: str) -> str:
        if team_id == mt.team_a_id:
            opp = mt.team_b_name
            sc = f"{mt.fs_a or mt.score_a or 0} - {mt.fs_b or mt.score_b or 0}"
        else:
            opp = mt.team_a_name
            sc = f"{mt.fs_b or mt.score_b or 0} - {mt.fs_a or mt.score_a or 0}"
        return f"{fmt_short_date(mt.start_play)}   {sc}   vs {opp}"

    def _h2h_card(self, m: Match) -> QWidget | None:
        h2h = self._head_to_head()
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(10)
        self._section_title(lay, "⚔️  历史交锋")
        if not h2h:
            note = QLabel("本数据集内暂无两队的过往交锋记录。")
            note.setStyleSheet("color:#B0BEC5; font-size:12px;")
            note.setWordWrap(True)
            lay.addWidget(note)
            return card

        a_win = b_win = draw = 0
        for x in h2h:
            w = x.winner_id
            if w is None:
                draw += 1
            elif w == m.team_a_id:
                a_win += 1
            elif w == m.team_b_id:
                b_win += 1
        tally = QLabel(
            f"{m.team_a_name}  {a_win}　胜  ·  {draw} 平  ·  "
            f"{b_win}　{m.team_b_name}胜"
        )
        tally.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:700;")
        tally.setWordWrap(True)
        lay.addWidget(tally)
        for x in h2h[:6]:
            row = QLabel(
                f"{fmt_short_date(x.start_play)}   "
                f"{x.team_a_name}  {x.fs_a or x.score_a or 0} - "
                f"{x.fs_b or x.score_b or 0}  {x.team_b_name}"
            )
            row.setStyleSheet("color:#9AA3BE; font-size:12px;")
            lay.addWidget(row)
        return card

    def _meta_card(self, m: Match) -> QWidget:
        meta = Card(padding=18)
        ml = QVBoxLayout(meta)
        ml.setContentsMargins(20, 14, 20, 14)
        ml.setSpacing(10)
        self._section_title(ml, "ℹ️  比赛信息")

        def info_row(label: str, value: str) -> QHBoxLayout:
            r = QHBoxLayout()
            l = QLabel(label)
            l.setFixedWidth(80)
            l.setStyleSheet("color:#B0BEC5; font-size:12px;")
            r.addWidget(l)
            v = QLabel(value)
            v.setStyleSheet("font-weight:600;")
            v.setWordWrap(True)
            r.addWidget(v, 1)
            return r

        ml.addLayout(info_row("比赛 ID", f"#{m.match_id}"))
        ml.addLayout(info_row("开赛时间", fmt_datetime(m.start_play)))
        if m.start_play and m.status == MatchStatus.FIXTURE:
            ml.addLayout(info_row("距开赛", fmt_relative(m.start_play)))
        if m.end_play:
            ml.addLayout(info_row("结束时间", fmt_datetime(m.end_play)))
        ml.addLayout(info_row("当前状态", m.status.label))
        if m.minute:
            ml.addLayout(info_row("比赛分钟", f"{m.minute}'+{m.minute_extra or 0}"))
        if m.fs_a or m.fs_b:
            ml.addLayout(info_row("最终比分", f"{m.fs_a} - {m.fs_b}"))
        if m.ps_a or m.ps_b:
            ml.addLayout(info_row("点球大战", f"{m.ps_a} - {m.ps_b}"))
        ml.addLayout(info_row("赛事 ID", str(m.competition_id)))
        ml.addLayout(info_row("轮次 ID", str(m.round_id or "—")))
        return meta
