"""standings_table —— 小组积分榜面板 v2（WorldCup 3.0，任务 10.3）。

对照设计稿 1:1 复刻「小组积分榜 / GROUP STANDINGS」卡（继承 :class:`GlassCard`）：

* 头部标题「小组积分榜 / GROUP STANDINGS」。
* 分组选择器（Group Selector）标签 ``A B C D E F G H I J K L``，默认 A 激活。
* 列序：``# / 球队 / 场次 / 胜平负 / 净胜球 / 积分 / 出线概率(条+%) / 最近5场(胶囊)``。
* 默认（无真实数据时）渲染设计稿样例行：墨西哥 92% / 韩国 56% / 捷克 48% / 南非 4%。
* 底部按钮「查看完整积分榜」。
* 点击某标签 → 重渲染该组并标记其为激活态。

对应需求 9.1–9.5 / 10.1 / 10.2 / 10.6。

数据映射保持**优雅降级**：把既有 :class:`GroupStanding` / :class:`TeamStanding`
（可能缺少出线概率 / 排名变化 / 近 5 场战绩）映射成展示行 ——
* 排名变化由 ``last_rank - rank`` 派生（无 ``last_rank`` → 持平「—」）；
* 出线概率由组内名次启发式估计（:func:`estimate_qual_prob`）；
* 近 5 场战绩既有模型无该字段 → 留空（仅渲染已有数据）。

不修改 ``app/api`` / ``app/models`` / ``app/services``。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.standing import GroupStanding, TeamStanding
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.fx.standings_fx import (
    FormPills,
    MiniSparkline,
    QualBar,
    rank_delta_glyph,
)
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor

#: 分组选择器固定标签 A–L（共 12 组，需求 9.2）。
GROUP_LETTERS: tuple[str, ...] = tuple("ABCDEFGHIJKL")


# ════════════════════════════════════════════════════════════════════
#  展示行视图模型
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class StandingRow:
    """积分榜单行的展示数据（适配既有 :class:`TeamStanding`）。"""

    rank: int
    team_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goal_diff: int
    points: int
    team_id: str = ""
    qual_prob: float | None = None          # 出线概率 [0,1]；None → 隐藏 %
    rank_delta: int | None = None           # 名次变化（正=上升）；None → 「—」
    form: list[str] = field(default_factory=list)   # 近 5 场（W/D/L）
    gd_series: list[int] = field(default_factory=list)  # 净胜球趋势


# ── 设计稿样例：A 组（墨西哥 92% / 韩国 56% / 捷克 48% / 南非 4%）（需求 10.6）──
SAMPLE_GROUP_A: list[StandingRow] = [
    StandingRow(rank=1, team_name="墨西哥", played=3, won=2, drawn=1, lost=0,
                goal_diff=4, points=7, qual_prob=0.92, rank_delta=1,
                form=["W", "W", "D", "W", "L"], gd_series=[1, 2, 1, 4]),
    StandingRow(rank=2, team_name="韩国", played=3, won=1, drawn=2, lost=0,
                goal_diff=1, points=5, qual_prob=0.56, rank_delta=-1,
                form=["D", "W", "D", "L", "W"], gd_series=[0, 1, 0, 1]),
    StandingRow(rank=3, team_name="捷克", played=3, won=1, drawn=1, lost=1,
                goal_diff=0, points=4, qual_prob=0.48, rank_delta=0,
                form=["L", "D", "W", "D", "L"], gd_series=[-1, 0, 1, 0]),
    StandingRow(rank=4, team_name="南非", played=3, won=0, drawn=1, lost=2,
                goal_diff=-5, points=1, qual_prob=0.04, rank_delta=0,
                form=["L", "L", "D", "L", "L"], gd_series=[-2, -3, -4, -5]),
]


# ════════════════════════════════════════════════════════════════════
#  纯映射辅助
# ════════════════════════════════════════════════════════════════════
def estimate_qual_prob(rank: int, group_size: int) -> float:
    """纯函数：由组内名次启发式估计「出线（前 2）概率」 ∈ [0,1]。

    既有模型无显式出线概率字段，此处给出与名次单调相关的温和估计（名次越靠
    前概率越高），并夹紧到 ``[0,1]``。仅作展示，非博彩报价。
    """
    if group_size <= 0:
        return 0.0
    # 名次 1 最高，逐名次衰减；前 2 名显著高于后段。
    table = {1: 0.92, 2: 0.58, 3: 0.30, 4: 0.06}
    if rank in table:
        return table[rank]
    # 兜底：线性衰减到 ~0.02。
    frac = max(0.0, 1.0 - (rank - 1) / float(group_size))
    return max(0.02, min(1.0, frac))


def row_from_standing(ts: TeamStanding, group_size: int) -> StandingRow:
    """纯函数：把一支 :class:`TeamStanding` 映射为展示用 :class:`StandingRow`。

    * 名次变化 ``rank_delta = last_rank - rank``（``last_rank`` 缺失 → ``None``）。
    * 出线概率由 :func:`estimate_qual_prob` 估计。
    * 近 5 场战绩既有模型无该字段，留空。
    """
    delta: int | None = None
    if ts.last_rank:
        delta = int(ts.last_rank) - int(ts.rank)
    return StandingRow(
        rank=ts.rank,
        team_name=ts.team_name,
        played=ts.matches_total,
        won=ts.matches_won,
        drawn=ts.matches_draw,
        lost=ts.matches_lost,
        goal_diff=ts.goal_diff,
        points=ts.points,
        team_id=ts.team_id,
        qual_prob=estimate_qual_prob(ts.rank, group_size),
        rank_delta=delta,
        form=[],
        gd_series=[],
    )


def rows_from_group(group: GroupStanding) -> list[StandingRow]:
    """纯函数：把一个 :class:`GroupStanding` 映射为按名次排序的展示行列表。"""
    teams = sorted(group.teams, key=lambda t: t.rank)
    size = len(teams)
    return [row_from_standing(t, size) for t in teams]


# ════════════════════════════════════════════════════════════════════
#  StandingsTable 面板
# ════════════════════════════════════════════════════════════════════
class StandingsTable(GlassCard):
    """小组积分榜面板 v2（继承 :class:`GlassCard`）。"""

    #: 点击某行球队（携带 team_id）—— 供上层接通既有 ``team_clicked``。
    team_clicked = pyqtSignal(str)
    #: 点击「查看完整积分榜」底部按钮。
    view_all_clicked = pyqtSignal()

    # 列宽预算（像素）—— 与表头一致，保证对齐。
    # 概览页小组积分榜面板较窄（~360–380px），列宽需足够紧凑：非「球队」列
    # 的固定宽度之和 + 间距要给伸缩的「球队」列留出 ≥ 其内容最小宽度的余量，
    # 否则「球队」列在表头（仅文字）与数据行（旗+名）会被压到不同的最小宽度，
    # 导致后续所有列错位。「最近5场」列因过宽（在此窄面板放不下）已移除。
    _W_RANK = 24
    _W_PLAYED = 28
    _W_WDL = 44
    _W_GD = 34
    _W_PTS = 26
    _W_QUAL = 70

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        # 真实小组数据（按组字母索引）；空 → 渲染设计稿样例。
        self._groups_by_letter: dict[str, GroupStanding] = {}
        # 出线概率覆盖表（中文队名 → 分数 [0,1]）：来自 Opta 赛事模拟，优先于
        # 组内名次启发式估计（estimate_qual_prob）。
        self._qualify_override: dict[str, float] = {}
        self._tab_btns: dict[str, QPushButton] = {}
        self._active: str = "A"          # 默认 A 激活（需求 9.3）
        self.setMinimumWidth(360)
        self.setMinimumHeight(360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._build_ui()
        self._select("A")

    # ── 构建骨架 ─────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        root.addWidget(self._header())
        root.addLayout(self._group_selector())
        root.addWidget(self._column_header())
        root.addWidget(self._hr())

        self._rows_box = QVBoxLayout()
        self._rows_box.setSpacing(6)
        # 让积分行区占满卡片剩余高度：4 支球队的行随面板等比拉伸填满，
        # 不再在底部留出大片空白（需求：加大行高、四队铺满小组件）。
        root.addLayout(self._rows_box, 1)

        # 底部「查看完整积分榜」。
        self._footer_btn = QPushButton("查看完整积分榜")
        self._footer_btn.setCursor(pointing_hand_cursor())
        self._footer_btn.setMinimumHeight(36)
        self._footer_btn.setStyleSheet(
            "QPushButton {"
            f" background: {p.glass_fill}; color: {p.text_dim};"
            f" border: 1px solid {p.glass_border};"
            f" border-radius: {Radius.PILL}px; padding: 6px 16px;"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD}; }}"
            "QPushButton:hover {"
            f" border: 1px solid {p.glass_border_hi}; color: {p.text}; }}"
        )
        self._footer_btn.clicked.connect(self.view_all_clicked.emit)
        root.addWidget(self._footer_btn)

    def _header(self) -> QWidget:
        p = self._palette
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        bar = QFrame()
        bar.setFixedSize(4, 24)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f" stop:0 {p.primary}, stop:1 {rgba(p.primary, 0.05)}); border-radius:2px;"
        )
        row.addWidget(bar)
        col = QVBoxLayout()
        col.setSpacing(0)
        zh = QLabel("小组积分榜")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("GROUP STANDINGS")
        en.setStyleSheet(
            f"color: {p.primary}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        col.addWidget(en)
        row.addLayout(col)
        row.addStretch(1)
        return w

    def _group_selector(self) -> QHBoxLayout:
        self._tabs = QHBoxLayout()
        self._tabs.setSpacing(4)
        for letter in GROUP_LETTERS:
            b = QPushButton(letter)
            b.setCheckable(True)
            b.setCursor(pointing_hand_cursor())
            b.setFixedHeight(28)
            # 字母不省略：12 个标签挤在窄面板时，给一个能容下单字母的最小宽度，
            # 避免被压到比文字还窄而触发 QPushButton 的「…」省略（看起来像乱码）。
            b.setMinimumWidth(22)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.clicked.connect(lambda _c=False, key=letter: self._select(key))
            self._tab_btns[letter] = b
            self._tabs.addWidget(b)
        return self._tabs

    def _column_header(self) -> QWidget:
        p = self._palette
        w = QWidget()
        row = QHBoxLayout(w)
        # 数据行（QFrame#StandingRow）有 3px 左侧色条边框，会把行内内容整体右移 3px；
        # 表头无该边框，故左内边距补足 3px（8+3），使表头与数据列严格对齐。
        row.setContentsMargins(11, 0, 8, 0)
        row.setSpacing(5)

        def lbl(text: str, width: int | None, align) -> QLabel:
            l = QLabel(text)
            l.setStyleSheet(
                f"color: {p.text_faint}; font-size: 10px;"
                f" font-weight: {Type.W_BOLD}; background: transparent;"
            )
            if width is not None:
                l.setFixedWidth(width)
            l.setAlignment(align)
            return l

        row.addWidget(lbl("#", self._W_RANK, Qt.AlignmentFlag.AlignLeft))
        row.addWidget(lbl("球队", None, Qt.AlignmentFlag.AlignLeft), 1)
        row.addWidget(lbl("场次", self._W_PLAYED, Qt.AlignmentFlag.AlignCenter))
        row.addWidget(lbl("胜平负", self._W_WDL, Qt.AlignmentFlag.AlignCenter))
        row.addWidget(lbl("净胜球", self._W_GD, Qt.AlignmentFlag.AlignCenter))
        row.addWidget(lbl("积分", self._W_PTS, Qt.AlignmentFlag.AlignCenter))
        row.addWidget(lbl("出线概率", self._W_QUAL, Qt.AlignmentFlag.AlignCenter))
        return w

    def _hr(self) -> QFrame:
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {self._palette.glass_border};")
        return line

    # ── 公共 API ─────────────────────────────
    def set_groups(self, groups: list[GroupStanding]) -> None:
        """注入真实小组数据（按组名首字母索引）；随后重渲染当前激活组。

        若某字母无真实数据，则该标签仍可点击，但渲染为空态。A 组若有真实数据
        则覆盖设计稿样例。
        """
        self._groups_by_letter = {}
        for g in groups or []:
            if not g.teams:
                continue
            letter = (g.name or "?").strip()[:1].upper()
            if letter:
                self._groups_by_letter[letter] = g
        self._select(self._active)

    def set_qualify_probs(self, mapping: dict[str, float]) -> None:
        """注入真实出线概率（中文队名 → 分数 ``[0,1]``，来自 Opta 赛事模拟）。

        提供后，概率栏优先展示该真实值（与「概率预测」页 / theanalyst 同源）；
        未覆盖到的球队仍回退组内名次启发式估计。
        """
        self._qualify_override = dict(mapping or {})
        self._render_active()

    @property
    def active_group(self) -> str:
        """当前激活的小组字母（默认 ``"A"``，需求 9.3）。"""
        return self._active

    @property
    def tab_letters(self) -> list[str]:
        """分组选择器标签字母列表（顺序 A–L，需求 9.2）。"""
        return list(self._tab_btns.keys())

    def current_team_names(self) -> list[str]:
        """当前激活组实际渲染的球队名（按行序）—— 供分组选择器单测断言。"""
        return [r.team_name for r in self._rows_for_active()]

    # ── 标签选择 + 重渲染 ────────────────────
    def _select(self, letter: str) -> None:
        if letter not in self._tab_btns:
            return
        self._active = letter
        self._restyle_tabs()
        self._render_active()

    def _restyle_tabs(self) -> None:
        p = self._palette
        for letter, b in self._tab_btns.items():
            active = letter == self._active
            b.setChecked(active)
            if active:
                b.setStyleSheet(
                    "QPushButton {"
                    f" background: {p.primary}; color: #04121A; border: none;"
                    " padding: 0px;"
                    f" border-radius: 8px; font-size: 12px; font-weight: {Type.W_BLACK}; }}"
                )
            else:
                b.setStyleSheet(
                    "QPushButton {"
                    f" background: {p.glass_fill}; color: {p.text_dim};"
                    f" border: 1px solid {p.glass_border};"
                    " padding: 0px;"
                    f" border-radius: 8px; font-size: 12px; font-weight: {Type.W_BOLD}; }}"
                    "QPushButton:hover {"
                    f" background: {rgba(p.primary, 0.12)}; color: {p.text}; }}"
                )

    def _rows_for_active(self) -> list[StandingRow]:
        grp = self._groups_by_letter.get(self._active)
        if grp is not None:
            return rows_from_group(grp)
        # 无真实数据：A 组渲染设计稿样例；其余组为空态。
        if self._active == "A":
            return list(SAMPLE_GROUP_A)
        return []

    def _clear_rows(self) -> None:
        while self._rows_box.count():
            it = self._rows_box.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
            else:
                sub = it.layout()
                if sub is not None:
                    while sub.count():
                        c = sub.takeAt(0).widget()
                        if c is not None:
                            c.deleteLater()

    def _render_active(self) -> None:
        self._clear_rows()
        rows = self._rows_for_active()
        if not rows:
            empty = QLabel("暂无积分榜数据")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color: {self._palette.text_faint}; font-size: {Type.CAPTION}px;"
                " padding: 24px; background: transparent;"
            )
            self._rows_box.addWidget(empty)
            return
        for r in rows:
            self._rows_box.addWidget(self._build_row(r), 1)

    # ── 单行构建 ─────────────────────────────
    def _build_row(self, r: StandingRow) -> QWidget:
        p = self._palette
        qual = r.rank <= 2
        accent = p.win if qual else "rgba(255,255,255,0.08)"
        w = QFrame()
        w.setObjectName("StandingRow")
        # 行高随面板拉伸（最小 52），四支球队铺满整张卡，视觉更饱满。
        w.setMinimumHeight(52)
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        w.setCursor(pointing_hand_cursor())
        w.setStyleSheet(
            f"QFrame#StandingRow {{ background: {rgba('#FFFFFF', 0.03)};"
            f" border-radius: 9px; border-left: 3px solid {accent}; }}"
            f"QFrame#StandingRow:hover {{ background: {rgba('#FFFFFF', 0.08)}; }}"
        )
        if r.team_id:
            w.mousePressEvent = (  # type: ignore[assignment]
                lambda _e, tid=r.team_id: self.team_clicked.emit(tid)
            )

        row = QHBoxLayout(w)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(5)

        # # 名次 + 排名变化字形。
        rank_box = QVBoxLayout()
        rank_box.setSpacing(0)
        rk = QLabel(str(r.rank))
        rk.setStyleSheet(
            f"color: {p.win if qual else p.text_dim}; font-size: 15px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        rank_box.addWidget(rk)
        glyph = rank_delta_glyph(r.rank_delta)
        delta_col = (p.win if (r.rank_delta or 0) > 0
                     else p.loss if (r.rank_delta or 0) < 0 else p.text_faint)
        dl = QLabel(glyph)
        dl.setStyleSheet(
            f"color: {delta_col}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        rank_box.addWidget(dl)
        rank_host = QWidget()
        rank_host.setFixedWidth(self._W_RANK)
        rank_host.setLayout(rank_box)
        row.addWidget(rank_host)

        # 球队：旗 + 名。名称用可省略标签（ElidedLabel），其最小宽度很小，
        # 保证「球队」伸缩列在窄面板下仍能取得与表头一致的分配宽度（不被内容
        # 撑大到不同的最小值），从而所有数据列与表头严格对齐。
        team_box = QHBoxLayout()
        team_box.setContentsMargins(0, 0, 0, 0)
        team_box.setSpacing(7)
        team_box.addWidget(FlagIcon(r.team_name, height=24, radius=4))
        from app.utils.text_utils import short_country_name
        from app.ui.widgets.elided_label import ElidedLabel
        nm = ElidedLabel(short_country_name(r.team_name),
                         mode=Qt.TextElideMode.ElideRight)
        nm.setMinimumWidth(0)
        nm.setStyleSheet(
            f"color: {p.text}; font-size: 14px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        team_box.addWidget(nm, 1)
        team_host = QWidget()
        team_host.setLayout(team_box)
        row.addWidget(team_host, 1)

        # 场次。
        row.addWidget(self._cell(str(r.played), self._W_PLAYED, p.text_dim))
        # 胜平负。
        row.addWidget(self._cell(f"{r.won}-{r.drawn}-{r.lost}", self._W_WDL, p.text_dim))
        # 净胜球。
        gd_text = f"+{r.goal_diff}" if r.goal_diff > 0 else str(r.goal_diff)
        gd_col = p.win if r.goal_diff > 0 else p.loss if r.goal_diff < 0 else p.text_dim
        row.addWidget(self._cell(gd_text, self._W_GD, gd_col))
        # 积分。
        row.addWidget(self._cell(str(r.points), self._W_PTS, p.accent, bold=True))

        # 出线概率（条 + %）—— 末列。优先用 Opta 真实出线概率（覆盖表），
        # 未覆盖到的球队回退组内名次启发式估计（StandingRow.qual_prob）。
        prob = self._qualify_override.get(r.team_name, r.qual_prob)
        qual_bar = QualBar(prob, palette=p)
        qual_host = QWidget()
        qh = QHBoxLayout(qual_host)
        qh.setContentsMargins(0, 0, 0, 0)
        qh.addWidget(qual_bar)
        qual_host.setFixedWidth(self._W_QUAL)
        row.addWidget(qual_host)

        return w

    def _cell(self, text: str, width: int, color: str, *, bold: bool = False) -> QLabel:
        weight = Type.W_BLACK if bold else Type.W_MEDIUM
        l = QLabel(text)
        l.setFixedWidth(width)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: {weight};"
            " background: transparent;"
        )
        return l
