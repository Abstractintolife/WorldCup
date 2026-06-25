"""预测页（AI 赛事预测）。

对应用户诉求：把 leisu「SWOT / 数据分析」与 oddsportal「AI Match Predictions」
里的全部信息搬进软件。由于三个来源服务端均不可抓取（详见
``app.services.prediction`` 模块说明），本页用软件自有数据**复刻**出同款内容：

* 顶部比赛选择器（默认定位到最近一场未开赛比赛）。
* 比赛 Hero（双方队旗 + 比分 / VS + 小组 + 开球时间）。
* 胜 / 平 / 负 概率条 + 结论。
* 「AI 赛事预测」三张趋势卡：比赛结果、进球数(Over/Under 2.5)、双方进球(BTTS)，
  每张含分析段落 + 双方近 5 场命中率 + 模型推算赔率（对照截图布局）。
* 「SWOT 分析」：两队各自的 优势 / 劣势 / 机会 / 威胁。
* 「数据分析」：综合指标对比、近期战绩走势、历史交锋、预期进球。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.models.standing import GroupStanding
from app.ui.design.app_cursor import pointing_hand_cursor
from app.services.data_service import DataService
from app.services.external_predictions import (
    ExternalPrediction,
    TeamStats,
    get_external_predictions,
    get_team_stats,
)
from app.services.match_markets import MarketGroup, MatchMarkets, build_markets
from app.services.prediction import MatchPrediction, Trend, build_prediction
from app.services.theanalyst import TeamProbability, TheAnalyst
from app.ui.pages.base import BasePage
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.misc import Card, HLine
from app.ui.widgets.standings_table import estimate_qual_prob
from app.ui.widgets.team_logo import TeamLogo
from app.utils.time_utils import fmt_datetime, fmt_relative


# 配色（与赛前分析卡一致）
_A = "#FF5470"      # 队 A（主）
_DRAW = "#B0BEC5"   # 平
_B = "#00BFFF"      # 队 B（客）
_GOLD = "#FFD700"

_SWOT_STYLE = {
    "优势": ("#2ED883", "💪"),
    "劣势": ("#FF6B6B", "⚠️"),
    "机会": ("#4FC3F7", "🎯"),
    "威胁": ("#FFB74D", "🛡"),
}

_RESULT_PILL = {"W": ("#2ED883", "胜"), "D": ("#FFD700", "平"), "L": ("#FF4E5E", "负")}

# 各来源短名（按钮上显示），与配色
_SRC_SHORT = {
    "Sports Mole": "Sports Mole",
    "FreeSuperTips": "FreeSuperTips",
    "Squawka": "Squawka",
    "KickForm（ThePuntersPage）": "KickForm",
    "Forebet": "Forebet",
    "The Analyst（Opta 超算）": "The Analyst",
}


class _SourceTabs(QWidget):
    """媒体 / 模型预测的来源切换器：顶部一排来源按钮，点击切换下方完整内容。"""

    def __init__(self, preds: list[ExternalPrediction], build_page) -> None:
        super().__init__()
        self._btns: list[QPushButton] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # ── 来源按钮行（可自动换行）──
        btn_host = QWidget()
        flow = FlowLayout(btn_host, margin=0, h_spacing=10, v_spacing=10)
        for i, ep in enumerate(preds):
            label = _SRC_SHORT.get(ep.source, ep.source)
            if ep.analysis_lang == "en" and ep.analysis:
                label += "  ·  EN"
            b = QPushButton(label)
            b.setCheckable(True)
            b.setCursor(pointing_hand_cursor())
            b.clicked.connect(lambda _checked=False, idx=i: self._select(idx))
            self._btns.append(b)
            flow.addWidget(b)
        root.addWidget(btn_host)

        # ── 内容堆叠区 ──
        self._stack = QStackedWidget()
        for ep in preds:
            self._stack.addWidget(build_page(ep))
        root.addWidget(self._stack)

        self._select(0)

    def _select(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)
        for i, b in enumerate(self._btns):
            b.setChecked(i == idx)
            if i == idx:
                b.setStyleSheet(
                    f"QPushButton{{color:#0E1116; background:{_GOLD};"
                    "border:none; border-radius:10px; padding:9px 18px;"
                    "font-size:14.5px; font-weight:900;}"
                )
            else:
                b.setStyleSheet(
                    "QPushButton{color:#C8D0E0; background:rgba(255,255,255,0.06);"
                    "border:1px solid rgba(255,255,255,0.12); border-radius:10px;"
                    "padding:9px 18px; font-size:14.5px; font-weight:700;}"
                    "QPushButton:hover{background:rgba(255,255,255,0.12);}"
                )


class _ProbBar(QWidget):
    """胜 / 平 / 负 三段式概率条。"""

    def __init__(self, pa: float, pd: float, pb: float) -> None:
        super().__init__()
        self._pa, self._pd, self._pb = max(0.0, pa), max(0.0, pd), max(0.0, pb)
        self.setFixedHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        total = self._pa + self._pd + self._pb or 1.0
        segs = [
            (self._pa / total, QColor(_A)),
            (self._pd / total, QColor(_DRAW)),
            (self._pb / total, QColor(_B)),
        ]
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(w), float(h), 9.0, 9.0)
        p.setClipPath(path)
        x = 0.0
        p.setPen(Qt.PenStyle.NoPen)
        for frac, col in segs:
            seg_w = frac * w
            if seg_w <= 0:
                continue
            p.fillRect(QRectF(x, 0, seg_w + 1, h), col)
            if seg_w > 36:
                p.setPen(QColor("#0B0E16"))
                font = p.font(); font.setBold(True); font.setPointSize(10)
                p.setFont(font)
                p.drawText(QRectF(x, 0, seg_w, h), Qt.AlignmentFlag.AlignCenter,
                           f"{round(frac * 100)}%")
                p.setPen(Qt.PenStyle.NoPen)
            x += seg_w


class _DonutProb(QWidget):
    """趋势卡右侧：概率甜甜圈 + 模型推算赔率。"""

    def __init__(self, prob: float, odds: float, market: str) -> None:
        super().__init__()
        self._prob = max(0.0, min(1.0, prob))
        self._odds = odds
        self._market = market
        self.setFixedSize(150, 96)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 背景圆角盒
        box = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        path = QPainterPath(); path.addRoundedRect(box, 12.0, 12.0)
        p.fillPath(path, QColor(13, 16, 24, 235))

        # 甜甜圈
        d = 60.0
        ring = QRectF(12, (self.height() - d) / 2, d, d)
        p.setPen(Qt.PenStyle.NoPen)
        # 底环
        from PyQt6.QtGui import QPen
        pen_bg = QPen(QColor(255, 255, 255, 38), 7)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_bg)
        p.drawArc(ring, 0, 360 * 16)
        # 进度环
        pen_fg = QPen(QColor(_GOLD), 7)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_fg)
        p.drawArc(ring, 90 * 16, -int(360 * 16 * self._prob))
        # 中心百分比
        p.setPen(QColor("#FFFFFF"))
        f = p.font(); f.setBold(True); f.setPointSize(13); p.setFont(f)
        p.drawText(ring, Qt.AlignmentFlag.AlignCenter, f"{round(self._prob * 100)}%")

        # 右侧赔率
        rx = 12 + d + 8
        rrect = QRectF(rx, 14, self.width() - rx - 8, self.height() - 28)
        p.setPen(QColor("#B0BEC5"))
        f2 = p.font(); f2.setBold(False); f2.setPointSize(8); p.setFont(f2)
        p.drawText(QRectF(rx, 14, rrect.width(), 14),
                   Qt.AlignmentFlag.AlignLeft, "模型推算赔率")
        p.setPen(QColor(_GOLD))
        f3 = p.font(); f3.setBold(True); f3.setPointSize(20); p.setFont(f3)
        p.drawText(QRectF(rx, 28, rrect.width(), 30),
                   Qt.AlignmentFlag.AlignLeft, f"{self._odds:.2f}")
        p.setPen(QColor("#9AA3BE"))
        f4 = p.font(); f4.setBold(True); f4.setPointSize(8); p.setFont(f4)
        p.drawText(QRectF(rx, 60, rrect.width(), 16),
                   Qt.AlignmentFlag.AlignLeft, self._market)


class PredictionPage(BasePage):
    title = "AI 赛事预测"
    subtitle = "智能赛前分析"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._matches: list[Match] = []
        self._groups: list[GroupStanding] = []
        self._selected_id: str | None = None
        self._pending_match: Match | None = None

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(14)

        # 标题 + 选择器
        head = QHBoxLayout()
        head.setSpacing(12)
        title = QLabel("🔮  AI 赛事预测")
        title.setStyleSheet("font-size:20px; font-weight:900; color:#FFFFFF;")
        head.addWidget(title)
        head.addStretch(1)
        pick_lbl = QLabel("选择比赛")
        pick_lbl.setStyleSheet("color:#B0BEC5; font-size:12px; font-weight:700;")
        head.addWidget(pick_lbl)
        self._combo = QComboBox()
        self._combo.setMinimumWidth(480)
        self._combo.setMinimumHeight(34)
        self._combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._combo.setMinimumContentsLength(36)
        self._combo.setStyleSheet(
            "QComboBox{font-size:13.5px; font-weight:700; padding:4px 14px;}"
            "QComboBox QAbstractItemView{font-size:13px; min-width:520px;}"
        )
        self._combo.setCursor(pointing_hand_cursor())
        self._combo.currentIndexChanged.connect(self._on_pick)
        head.addWidget(self._combo)
        outer.addLayout(head)

        sub = QLabel(
            "基于小组积分、近期战绩与历史交锋的智能测算 · "
            "复刻 SWOT / 数据分析 / AI 预测三类内容（数据来源：懂球帝公开接口）"
        )
        sub.setStyleSheet("color:#B0BEC5; font-size:12px;")
        sub.setWordWrap(True)
        outer.addWidget(sub)

        # 正文滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll, 1)
        body = QWidget()
        scroll.setWidget(body)
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(16)

    # ── 对外入口 ──────────────────────────────
    def open_match(self, match: Match) -> None:
        """从外部（如比赛卡）跳转到某场比赛的预测。"""
        self._pending_match = match
        self._selected_id = match.match_id
        self.refresh(force=False)

    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            _r, matches = await self._service.fetch_full_schedule(force=force)
            self._matches = matches
            try:
                groups, _ko, _km = await self._service.fetch_standings(force=force)
                self._groups = groups
            except Exception:  # pragma: no cover - 网络
                self._groups = []
            # 晋级概率：拉取 Opta 赛事模拟（夺冠 / 进决赛概率）；失败自动回退离线快照。
            try:
                await TheAnalyst.instance().refresh(force=force)
            except Exception:  # pragma: no cover - 网络
                pass
            self._populate_combo()
            self._render()

        self.run_async(runner)

    # ── 选择器 ────────────────────────────────
    def _ordered_matches(self) -> list[Match]:
        """未开赛 / 进行中在前（按开球时间升序），已结束在后（最近在前）。"""
        def key(m: Match):
            ts = m.start_play or m.date_utc or ""
            played = m.status == MatchStatus.PLAYED
            return (1 if played else 0, ts if not played else "")
        upcoming = [m for m in self._matches if m.status != MatchStatus.PLAYED]
        played = [m for m in self._matches if m.status == MatchStatus.PLAYED]
        upcoming.sort(key=lambda m: m.start_play or m.date_utc or "")
        played.sort(key=lambda m: m.start_play or m.date_utc or "", reverse=True)
        return upcoming + played

    def _populate_combo(self) -> None:
        ordered = self._ordered_matches()
        self._combo.blockSignals(True)
        self._combo.clear()
        default_index = 0
        for i, m in enumerate(ordered):
            when = ""
            if m.local_start:
                when = m.local_start.strftime("%m-%d %H:%M")
            tag = "🔴 " if m.is_live else ("✓ " if m.status == MatchStatus.PLAYED else "")
            label = f"{tag}{m.team_a_name} vs {m.team_b_name}"
            if when:
                label += f"  ·  {when}"
            self._combo.addItem(label, m.match_id)
            if self._selected_id and m.match_id == self._selected_id:
                default_index = i
        # 未指定时：默认选最近一场未开赛/进行中的比赛
        if not self._selected_id and ordered:
            for i, m in enumerate(ordered):
                if m.status != MatchStatus.PLAYED:
                    default_index = i
                    break
            self._selected_id = ordered[default_index].match_id
        self._combo.setCurrentIndex(default_index)
        self._combo.blockSignals(False)

    def _on_pick(self, _idx: int) -> None:
        mid = self._combo.currentData()
        if mid:
            self._selected_id = mid
            self._pending_match = None
            self._render()

    def _current_match(self) -> Match | None:
        if self._pending_match is not None:
            return self._pending_match
        for m in self._matches:
            if m.match_id == self._selected_id:
                return m
        return self._matches[0] if self._matches else None

    # ── 渲染 ─────────────────────────────────
    def _clear_body(self) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render(self) -> None:
        self._clear_body()
        m = self._current_match()
        if m is None:
            empty = QLabel("暂无可预测的比赛数据")
            empty.setStyleSheet("color:#B0BEC5; font-size:14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._body.addWidget(empty)
            self._body.addStretch(1)
            return

        pred = build_prediction(m, self._matches, self._groups)

        self._body.addWidget(self._hero_card(pred))
        self._body.addWidget(self._prob_card(pred))
        self._body.addWidget(self._advance_card(pred))
        self._body.addWidget(self._trends_card(pred))
        ext = get_external_predictions(m)
        if ext:
            self._body.addWidget(self._external_card(ext))
        stats = get_team_stats(m)
        if stats:
            self._body.addWidget(self._stats_card(stats))
        self._body.addWidget(self._swot_card(pred))
        self._body.addWidget(self._data_card(pred))
        self._body.addWidget(self._markets_card(pred))
        self._body.addStretch(1)

    # ── 各区块 ────────────────────────────────
    def _hero_card(self, pred: MatchPrediction) -> QWidget:
        m = pred.match
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(14)
        row.addLayout(self._team_col(m.team_a_id, m.team_a_logo, m.team_a_name), 4)

        center = QVBoxLayout()
        center.setSpacing(4)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score = QLabel(m.display_score)
        f = QFont(); f.setPointSize(30); f.setBold(True)
        score.setFont(f)
        score.setStyleSheet(f"color:{_GOLD};")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(score)
        status_txt = m.status.label
        if m.status == MatchStatus.FIXTURE and m.start_play:
            status_txt = fmt_relative(m.start_play)
        st = QLabel(status_txt)
        st.setStyleSheet("color:#9AA3BE; font-size:12px; font-weight:700;")
        st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(st)
        row.addLayout(center, 3)

        row.addLayout(self._team_col(m.team_b_id, m.team_b_logo, m.team_b_name), 4)
        lay.addLayout(row)

        meta_bits = []
        if pred.group_name:
            meta_bits.append(f"🏆 {pred.group_name}")
        if m.start_play:
            meta_bits.append(f"🕐 {fmt_datetime(m.start_play)}")
        if meta_bits:
            meta = QLabel("　·　".join(meta_bits))
            meta.setStyleSheet("color:#B0BEC5; font-size:12px;")
            meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(meta)
        return card

    def _team_col(self, team_id: str, logo: str | None, name: str) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(8)
        col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(TeamLogo(logo, size=64, shape="circle"),
                      alignment=Qt.AlignmentFlag.AlignCenter)
        n = QLabel(name)
        f = QFont(); f.setPointSize(13); f.setBold(True)
        n.setFont(f)
        n.setStyleSheet("color:#FFFFFF;")
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        n.setWordWrap(True)
        col.addWidget(n)
        wrap = QWidget(); wrap.setLayout(col)
        wrap.setCursor(pointing_hand_cursor())
        wrap.mousePressEvent = lambda _e, t=team_id: self.team_clicked.emit(t)  # type: ignore[assignment]
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(wrap, alignment=Qt.AlignmentFlag.AlignCenter)
        return outer

    def _prob_card(self, pred: MatchPrediction) -> QWidget:
        m = pred.match
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(10)
        self._section(lay, "📊  胜负概率")

        headr = QHBoxLayout()
        la = QLabel(f"{m.team_a_name} 胜")
        la.setStyleSheet(f"color:{_A}; font-size:12px; font-weight:800;")
        ld = QLabel("平")
        ld.setStyleSheet(f"color:{_DRAW}; font-size:12px; font-weight:800;")
        ld.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb = QLabel(f"{m.team_b_name} 胜")
        lb.setStyleSheet(f"color:{_B}; font-size:12px; font-weight:800;")
        lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        headr.addWidget(la, 1); headr.addWidget(ld, 1); headr.addWidget(lb, 1)
        lay.addLayout(headr)
        lay.addWidget(_ProbBar(pred.win_a, pred.draw, pred.win_b))

        pct = QHBoxLayout()
        for val, color, align in (
            (pred.win_a, _A, Qt.AlignmentFlag.AlignLeft),
            (pred.draw, _DRAW, Qt.AlignmentFlag.AlignCenter),
            (pred.win_b, _B, Qt.AlignmentFlag.AlignRight),
        ):
            pl = QLabel(f"{round(val * 100)}%")
            pl.setStyleSheet(f"color:{color}; font-size:13px; font-weight:900;")
            pl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            pct.addWidget(pl, 1)
        lay.addLayout(pct)

        verdict = QLabel(f"📌  {pred.verdict}")
        verdict.setStyleSheet(
            f"color:{_GOLD}; font-size:13px; font-weight:800;"
            "background:rgba(255,197,61,0.10); border-radius:10px; padding:8px 12px;"
        )
        verdict.setWordWrap(True)
        lay.addWidget(verdict)
        return card

    # ── 晋级概率（出线 + Opta 夺冠 / 进决赛）────────────────────
    def _team_group_rank(self, team_id: str, team_name: str) -> tuple[int | None, int]:
        """在小组积分榜里定位某队的组内名次与小组规模（找不到 → (None, 0)）。"""
        for g in self._groups:
            for ts in g.teams:
                if (team_id and ts.team_id == team_id) or ts.team_name == team_name:
                    return ts.rank, len(g.teams)
        return None, 0

    def _qual_prob_for(self, team_id: str, team_name: str) -> float | None:
        """小组出线（晋级淘汰赛）概率。

        优先取 Opta 赛事模拟的真实出线概率（``qualify_pct``，与「概率预测」页 /
        theanalyst.com 同源）；无该数据时回退组内名次启发式估计（与首页小组
        积分榜同源），保证离线 / 旧数据下仍有合理展示。
        """
        tp = self._opta_for(team_name)
        if tp is not None and tp.qualify_pct and tp.qualify_pct > 0:
            return max(0.0, min(1.0, tp.qualify_pct / 100.0))
        rank, size = self._team_group_rank(team_id, team_name)
        if rank is None or size <= 0:
            return None
        return estimate_qual_prob(rank, size)

    @staticmethod
    def _opta_for(team_name: str) -> TeamProbability | None:
        """Opta 赛事模拟里某队的夺冠 / 进决赛概率（按中文 / 英文名匹配）。"""
        for tp in TheAnalyst.instance().championship_ranking():
            if tp.team_cn == team_name or tp.team_en == team_name:
                return tp
        return None

    def _advance_card(self, pred: MatchPrediction) -> QWidget:
        m = pred.match
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 16)
        lay.setSpacing(10)
        self._section(lay, "🎫  晋级概率")
        hint = QLabel(
            "出线（晋级淘汰赛）概率取自 Opta 超级计算机赛事模拟（与「概率预测」页、"
            "首页「小组积分榜」概率栏同源），并附 Opta 推算的夺冠 / 进决赛概率"
        )
        hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        lay.addWidget(self._advance_row(m.team_a_id, m.team_a_name, _A))
        lay.addWidget(self._advance_row(m.team_b_id, m.team_b_name, _B))
        return card

    def _advance_row(self, team_id: str, team_name: str, color: str) -> QWidget:
        qual = self._qual_prob_for(team_id, team_name)
        tp = self._opta_for(team_name)

        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 4, 0, 4)
        col.setSpacing(6)

        # 队名 + 出线概率条 + 百分比
        top = QHBoxLayout()
        top.setSpacing(10)
        nm = QLabel(team_name)
        nm.setStyleSheet(f"color:{color}; font-size:14px; font-weight:900;")
        nm.setMinimumWidth(96)
        top.addWidget(nm)

        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int((qual or 0.0) * 1000))
        bar.setTextVisible(False)
        bar.setFixedHeight(10)
        bar.setStyleSheet(
            "QProgressBar{background:rgba(255,255,255,0.08); border:none; border-radius:5px;}"
            f"QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {color}, stop:1 {_GOLD}); border-radius:5px;}}"
        )
        top.addWidget(bar, 1)

        qpct = QLabel(f"{round(qual * 100)}%" if qual is not None else "—")
        qpct.setFixedWidth(52)
        qpct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        qpct.setStyleSheet(f"color:{_GOLD}; font-size:15px; font-weight:900;")
        top.addWidget(qpct)
        col.addLayout(top)

        # 标签行：出线概率 + Opta 夺冠 / 进决赛
        tags = QHBoxLayout()
        tags.setSpacing(8)
        tags.addWidget(self._adv_chip("小组出线",
                                      f"{round(qual * 100)}%" if qual is not None else "—",
                                      "#2ED883"))
        if tp is not None:
            tags.addWidget(self._adv_chip("进决赛", f"{tp.final_pct:.1f}%", _B))
            tags.addWidget(self._adv_chip("夺冠", f"{tp.win_pct:.1f}%", _GOLD))
        tags.addStretch(1)
        col.addLayout(tags)
        return wrap

    @staticmethod
    def _adv_chip(label: str, value: str, color: str) -> QWidget:
        chip = QLabel(f"{label} {value}")
        chip.setStyleSheet(
            f"color:{color}; font-size:11.5px; font-weight:800;"
            "background:rgba(255,255,255,0.06); border-radius:8px; padding:3px 9px;"
        )
        chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return chip

    def _trends_card(self, pred: MatchPrediction) -> QWidget:
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "🤖  AI 赛事预测")
        hint = QLabel("综合近期趋势，给出本场三大核心市场的倾向预测")
        hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
        lay.addWidget(hint)

        for i, t in enumerate(pred.trends):
            if i > 0:
                lay.addWidget(HLine())
            lay.addWidget(self._trend_block(pred, t))
        return card

    def _trend_block(self, pred: MatchPrediction, t: Trend) -> QWidget:
        wrap = QWidget()
        row = QHBoxLayout(wrap)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(7)
        cat = QLabel(t.category)
        cat.setStyleSheet(
            f"color:{_B}; font-size:11px; font-weight:800;"
            "background:rgba(61,139,255,0.14); border-radius:8px; padding:2px 9px;"
        )
        cat.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        cat_row = QHBoxLayout(); cat_row.addWidget(cat); cat_row.addStretch(1)
        left.addLayout(cat_row)

        head = QLabel(t.headline)
        head.setStyleSheet("color:#FFFFFF; font-size:16px; font-weight:900;")
        left.addWidget(head)

        narr = QLabel(t.narrative)
        narr.setStyleSheet("color:#B7BFD8; font-size:12.5px; line-height:150%;")
        narr.setWordWrap(True)
        left.addWidget(narr)

        # 双方近期命中率
        for stat, color in ((t.stat_a, _A), (t.stat_b, _B)):
            srow = QHBoxLayout()
            srow.setSpacing(8)
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:10px;")
            dot.setFixedWidth(14)
            srow.addWidget(dot)
            sl = QLabel(stat)
            sl.setStyleSheet("color:#9AA3BE; font-size:12px; font-weight:600;")
            srow.addWidget(sl)
            srow.addStretch(1)
            left.addLayout(srow)

        row.addLayout(left, 1)
        row.addWidget(_DonutProb(t.probability, t.odds, t.market), 0,
                      Qt.AlignmentFlag.AlignTop)
        return wrap

    def _external_card(self, preds: list[ExternalPrediction]) -> QWidget:
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "📰  媒体 / 模型预测")
        names = "、".join(_SRC_SHORT.get(ep.source, ep.source) for ep in preds)
        hint = QLabel(
            f"点击下方来源按钮切换查看（共 {len(preds)} 家：{names}）。"
            "各家完整赛前分析已翻译为中文（暂未翻译的以英文原文呈现）。"
        )
        hint.setStyleSheet("color:#B0BEC5; font-size:13px;")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        lay.addWidget(_SourceTabs(preds, self._external_block))
        return card

    def _external_block(self, ep: ExternalPrediction) -> QWidget:
        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(2, 4, 2, 4)
        col.setSpacing(12)

        # 比分预测（醒目）
        if ep.score_prediction:
            sp = QLabel(f"🎯  比分预测：{ep.score_prediction}")
            sp.setStyleSheet(
                f"color:{_GOLD}; font-size:16px; font-weight:900;"
                "background:rgba(255,197,61,0.10); border-radius:10px; padding:9px 14px;"
            )
            sp.setWordWrap(True)
            col.addWidget(sp)

        # 胜 / 平 / 负概率（若来源提供）
        if ep.win_a is not None and ep.draw is not None and ep.win_b is not None:
            col.addWidget(_ProbBar(ep.win_a, ep.draw, ep.win_b))
            prob_txt = QLabel(
                f"主胜 {round(ep.win_a * 100)}%　·　平 {round(ep.draw * 100)}%"
                f"　·　客胜 {round(ep.win_b * 100)}%"
            )
            prob_txt.setStyleSheet("color:#9AA3BE; font-size:13px; font-weight:700;")
            col.addWidget(prob_txt)

        # 综述（导语）
        if ep.summary:
            summ = QLabel(ep.summary)
            summ.setStyleSheet(
                "color:#E6EAF4; font-size:15px; font-weight:600; line-height:175%;"
            )
            summ.setWordWrap(True)
            col.addWidget(summ)

        # ── 完整分析正文（大段、不省略）──
        if ep.analysis:
            col.addWidget(HLine())
            for heading, body in ep.analysis:
                if heading:
                    h = QLabel(heading)
                    h.setStyleSheet(
                        f"color:{_GOLD}; font-size:15.5px; font-weight:900;"
                    )
                    h.setWordWrap(True)
                    col.addWidget(h)
                for para in str(body).split("\n"):
                    para = para.strip()
                    if not para:
                        continue
                    pl = QLabel(para)
                    pl.setStyleSheet(
                        "color:#CDD4E4; font-size:14.5px; line-height:185%;"
                    )
                    pl.setWordWrap(True)
                    pl.setTextInteractionFlags(
                        Qt.TextInteractionFlag.TextSelectableByMouse)
                    col.addWidget(pl)

        # 盘口赔率
        if ep.odds_text:
            odds = QLabel(f"💱  {ep.odds_text}")
            odds.setStyleSheet("color:#9AA3BE; font-size:13px;")
            odds.setWordWrap(True)
            col.addWidget(odds)

        # 推荐玩法 / 分析要点
        if ep.tips:
            col.addWidget(HLine())
            tips_head = QLabel("推荐玩法 / 分析要点")
            tips_head.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:800;")
            col.addWidget(tips_head)
            for t in ep.tips:
                tl = QLabel(f"·  {t}")
                tl.setStyleSheet("color:#AEB6CC; font-size:13.5px; line-height:165%;")
                tl.setWordWrap(True)
                tl.setContentsMargins(8, 0, 0, 0)
                col.addWidget(tl)

        # 备注 + 出处
        foot_bits = []
        if ep.note:
            foot_bits.append(ep.note)
        if ep.source_url:
            foot_bits.append(f"出处：{ep.source_url}")
        if foot_bits:
            foot = QLabel("　".join(foot_bits))
            foot.setStyleSheet("color:#6A7388; font-size:11.5px; line-height:160%;")
            foot.setWordWrap(True)
            foot.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            col.addWidget(foot)
        return wrap

    def _stats_card(self, stats: TeamStats) -> QWidget:
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "📊  球队数据对比")
        bits = ["球队整体统计"]
        if stats.scope:
            bits.append(stats.scope)
        bits.append(f"来源：{stats.source}")
        hint = QLabel("　·　".join(bits))
        hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        h0 = QLabel(stats.team_a)
        h0.setStyleSheet(f"color:{_A}; font-size:13px; font-weight:800;")
        grid.addWidget(h0, 0, 0)
        hm = QLabel("指标")
        hm.setStyleSheet("color:#B0BEC5; font-size:12px;")
        hm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(hm, 0, 1)
        h2 = QLabel(stats.team_b)
        h2.setStyleSheet(f"color:{_B}; font-size:13px; font-weight:800;")
        h2.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(h2, 0, 2)

        for r, row in enumerate(stats.rows, start=1):
            grid.addWidget(
                self._stat_cell(row.a_value, row.a_sub,
                                Qt.AlignmentFlag.AlignLeft), r, 0)
            ml = QLabel(row.label)
            ml.setStyleSheet("color:#B0BEC5; font-size:12px;")
            ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ml.setWordWrap(True)
            grid.addWidget(ml, r, 1)
            grid.addWidget(
                self._stat_cell(row.b_value, row.b_sub,
                                Qt.AlignmentFlag.AlignRight), r, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        lay.addWidget(self._wrap_layout(grid))

        foot_bits = []
        if stats.note:
            foot_bits.append(stats.note)
        if stats.source_url:
            foot_bits.append(f"出处：{stats.source_url}")
        if foot_bits:
            foot = QLabel("　".join(foot_bits))
            foot.setStyleSheet("color:#56607D; font-size:10.5px;")
            foot.setWordWrap(True)
            lay.addWidget(foot)
        return card

    def _stat_cell(self, value: str, sub: str, align) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(1)
        val = QLabel(value)
        val.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:800;")
        val.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
        v.addWidget(val)
        if sub:
            s = QLabel(sub)
            s.setStyleSheet("color:#6E7790; font-size:11px;")
            s.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            s.setWordWrap(True)
            v.addWidget(s)
        return w

    def _markets_card(self, pred: MatchPrediction) -> QWidget:
        mk = build_markets(pred)
        m = pred.match
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "🎲  盘口分析")
        hint = QLabel(
            f"由泊松比分模型测算（{m.team_a_name} 预期 {mk.exp_a:.2f} 球 · "
            f"{m.team_b_name} 预期 {mk.exp_b:.2f} 球），涵盖让球 / 大小 / 独赢 / "
            "总进球 / 单双 / 半全场 / 正确比分"
        )
        hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        for i, g in enumerate(mk.groups):
            if i > 0:
                lay.addWidget(HLine())
            lay.addWidget(self._market_group_block(g))
        return card

    def _market_group_block(self, g: MarketGroup) -> QWidget:
        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 4, 0, 4)
        col.setSpacing(8)

        title = QLabel(g.title)
        title.setStyleSheet("color:#FFFFFF; font-size:13.5px; font-weight:800;")
        col.addWidget(title)

        pick = QLabel(f"✅ 推荐：{g.pick}")
        pick.setStyleSheet(
            f"color:{_GOLD}; font-size:12.5px; font-weight:800;"
            "background:rgba(255,197,61,0.10); border-radius:8px; padding:4px 10px;"
        )
        pick.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        pick.setWordWrap(True)
        prow = QHBoxLayout(); prow.addWidget(pick); prow.addStretch(1)
        col.addLayout(prow)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(5)
        for idx, ln in enumerate(g.lines):
            r, c = divmod(idx, 2)
            grid.addWidget(self._market_line_cell(ln), r, c)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        col.addWidget(self._wrap_layout(grid))

        if g.note:
            note = QLabel(g.note)
            note.setStyleSheet("color:#56607D; font-size:10.5px;")
            note.setWordWrap(True)
            col.addWidget(note)
        return wrap

    def _market_line_cell(self, ln: MarketLine) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        lbl = QLabel(("● " if ln.highlight else "") + ln.label)
        lbl.setStyleSheet(
            f"color:{'#FFFFFF' if ln.highlight else '#9AA3BE'}; font-size:12px;"
            f"{'font-weight:800;' if ln.highlight else ''}"
        )
        lbl.setWordWrap(True)
        row.addWidget(lbl, 1)
        pct = QLabel(f"{round(ln.prob * 100)}%")
        pct.setStyleSheet(
            f"color:{_GOLD if ln.highlight else '#C7CEE0'}; font-size:12.5px; "
            "font-weight:900;"
        )
        pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pct.setFixedWidth(46)
        row.addWidget(pct, 0)
        return w

    def _swot_card(self, pred: MatchPrediction) -> QWidget:
        m = pred.match
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "🧭  SWOT 分析")
        hint = QLabel("优势 / 劣势 / 机会 / 威胁 —— 由两队攻防、状态与交锋数据生成")
        hint.setStyleSheet("color:#B0BEC5; font-size:12px;")
        lay.addWidget(hint)

        cols = QHBoxLayout()
        cols.setSpacing(16)
        cols.addLayout(self._swot_col(m.team_a_name, pred.swot_a, _A), 1)
        cols.addLayout(self._swot_col(m.team_b_name, pred.swot_b, _B), 1)
        lay.addLayout(cols)
        return card

    def _swot_col(self, name: str, swot: dict[str, list[str]], color: str) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(10)
        head = QLabel(name)
        head.setStyleSheet(f"color:{color}; font-size:14px; font-weight:900;")
        col.addWidget(head)
        for key in ("优势", "劣势", "机会", "威胁"):
            c, icon = _SWOT_STYLE[key]
            block = QLabel(f"{icon}  {key}")
            block.setStyleSheet(f"color:{c}; font-size:12.5px; font-weight:800;")
            col.addWidget(block)
            for item in swot.get(key, []):
                il = QLabel(f"· {item}")
                il.setStyleSheet("color:#9AA3BE; font-size:12px;")
                il.setWordWrap(True)
                il.setContentsMargins(10, 0, 0, 0)
                col.addWidget(il)
        col.addStretch(1)
        return col

    def _data_card(self, pred: MatchPrediction) -> QWidget:
        m = pred.match
        ma, mb = pred.metrics_a, pred.metrics_b
        card = Card(padding=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 18)
        lay.setSpacing(12)
        self._section(lay, "📈  数据分析")

        # 指标对比网格
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(9)
        h0 = QLabel(m.team_a_name)
        h0.setStyleSheet(f"color:{_A}; font-size:13px; font-weight:800;")
        grid.addWidget(h0, 0, 0)
        hm = QLabel("指标"); hm.setStyleSheet("color:#B0BEC5; font-size:12px;")
        hm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(hm, 0, 1)
        h2 = QLabel(m.team_b_name)
        h2.setStyleSheet(f"color:{_B}; font-size:13px; font-weight:800;")
        h2.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(h2, 0, 2)

        def rowm(r: int, label: str, va: str, vb: str, a_better: bool | None) -> None:
            ac = _GOLD if a_better is True else "#FFFFFF"
            bc = _GOLD if a_better is False else "#FFFFFF"
            al = QLabel(va)
            al.setStyleSheet(f"color:{ac}; font-size:14px; font-weight:800;")
            grid.addWidget(al, r, 0)
            ml = QLabel(label); ml.setStyleSheet("color:#B0BEC5; font-size:12px;")
            ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(ml, r, 1)
            bl = QLabel(vb)
            bl.setStyleSheet(f"color:{bc}; font-size:14px; font-weight:800;")
            bl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(bl, r, 2)

        rowm(1, "综合指数", f"{ma.index:.0f}", f"{mb.index:.0f}",
             ma.index > mb.index if ma.index != mb.index else None)
        rowm(2, "小组排名",
             f"第 {ma.rank}" if ma.rank else "—",
             f"第 {mb.rank}" if mb.rank else "—",
             (ma.rank or 99) < (mb.rank or 99) if (ma.rank or mb.rank) else None)
        rowm(3, "场均积分", f"{ma.ppm:.1f}", f"{mb.ppm:.1f}",
             ma.ppm > mb.ppm if ma.ppm != mb.ppm else None)
        rowm(4, "场均进球", f"{ma.gfpm:.1f}", f"{mb.gfpm:.1f}",
             ma.gfpm > mb.gfpm if ma.gfpm != mb.gfpm else None)
        rowm(5, "场均失球", f"{ma.gapm:.1f}", f"{mb.gapm:.1f}",
             ma.gapm < mb.gapm if ma.gapm != mb.gapm else None)
        lay.addWidget(self._wrap_layout(grid))

        lay.addWidget(HLine())

        # 近期战绩走势
        form_head = QLabel("近期战绩")
        form_head.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:800;")
        lay.addWidget(form_head)
        lay.addLayout(self._form_row(m.team_a_name, pred.form_a, _A))
        lay.addLayout(self._form_row(m.team_b_name, pred.form_b, _B))

        # 历史交锋
        if pred.h2h_total:
            lay.addWidget(HLine())
            h2h = QLabel(
                f"⚔️  历史交锋 {pred.h2h_total} 场："
                f"{m.team_a_name} {pred.h2h_a_win} 胜 · {pred.h2h_draw} 平 · "
                f"{pred.h2h_b_win} 胜 {m.team_b_name}"
            )
            h2h.setStyleSheet("color:#9AA3BE; font-size:12.5px;")
            h2h.setWordWrap(True)
            lay.addWidget(h2h)

        # 预期进球
        eg = QLabel(
            f"🎯  模型预期总进球：约 {pred.expected_goals:.1f} 球　·　"
            f"大 2.5 概率 {round(pred.over25_prob * 100)}%　·　"
            f"双方进球概率 {round(pred.btts_prob * 100)}%"
        )
        eg.setStyleSheet("color:#9AA3BE; font-size:12.5px;")
        eg.setWordWrap(True)
        lay.addWidget(eg)
        return card

    def _form_row(self, name, form, color: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        nm = QLabel(name)
        nm.setStyleSheet(f"color:{color}; font-size:12.5px; font-weight:800;")
        nm.setFixedWidth(96)
        nm.setWordWrap(True)
        row.addWidget(nm)
        if not form.games:
            na = QLabel("暂无近期战绩")
            na.setStyleSheet("color:#56607D; font-size:12px;")
            row.addWidget(na)
            row.addStretch(1)
            return row
        for g in form.games:
            c, ch = _RESULT_PILL.get(g.result, ("#B0BEC5", "—"))
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

    # ── 工具 ─────────────────────────────────
    def _section(self, layout: QVBoxLayout, text: str) -> None:
        t = QLabel(text)
        t.setStyleSheet("font-size:15px; font-weight:800; color:#FFFFFF;")
        layout.addWidget(t)

    @staticmethod
    def _wrap_layout(inner) -> QWidget:
        w = QWidget()
        w.setLayout(inner)
        return w
