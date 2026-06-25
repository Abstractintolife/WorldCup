"""stat_strip —— 赛事大盘统计条（WorldCup 3.0，任务 11.1）。

对照设计稿 1:1 复刻「赛事大盘统计条」—— 一排 **恰好六张等宽** 玻璃统计卡
（继承 :class:`GlassCard`），自左至右依次为：

    总比赛场次 · 总进球数 · 进球球员 · 平均进球 · 参赛球队 · 主办城市

每张卡片包含：

* **标题数字**（headline）—— 进入页面时用 :class:`CountUpNumber` 从 0 滚动到
  目标值（``平均进球`` 用两位小数，需求 11.10）。
* **次级文本**（secondary）—— 卡片底部说明（如「已结束 48 场」）。
* **图标**（icon）—— emoji 字形；``总比赛场次`` 改用迷你折线
  （:class:`MiniSparkline`）取代图标。
* **涨跌幅**（delta）—— 仅部分卡片展示（如「↑8%」）。

数据来源
---------
:func:`compute_stats` 是**纯函数**：尽量从 :class:`DataService` 给出的真实数据
（``总比赛场次`` / ``已完赛`` / ``总进球`` / ``场均`` / ``进球球员数``）测算每张
卡片的标题值与次级文本；任一数据缺失时回退到设计稿样例值
（104 / 141 / 89 / 2.94 / 48 / 16）。``主办城市`` 无公开数据源，恒为样例 16。

对应需求 11.1–11.10。不修改 ``app/api`` / ``app/models`` / ``app/services``。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.fx.count_up import CountUpNumber
from app.ui.widgets.fx.standings_fx import MiniSparkline
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor


# ════════════════════════════════════════════════════════════════════
#  统计卡视图模型
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class StatSpec:
    """单张统计卡的展示数据。"""

    key: str                       # 稳定标识（matches / goals / ...）
    title: str                     # 中文标题（总比赛场次 ...）
    en: str                        # 英文副标题（overline）
    value: float                   # 标题数字（CountUpNumber 目标值）
    decimals: int = 0              # 小数位（平均进球 = 2）
    secondary: str = ""            # 次级说明文本
    delta: str | None = None       # 涨跌幅（如「↑8%」）；None → 不展示
    icon: str = ""                 # emoji 图标字形；空 → 不展示图标
    sparkline: bool = False        # 是否以迷你折线代替图标
    sparkline_series: tuple[float, ...] = field(default_factory=tuple)


#: 六张卡的规范顺序（自左至右，需求 11.2）。
STAT_ORDER: tuple[str, ...] = (
    "matches", "goals", "scorers", "avg", "teams", "cities",
)

#: 设计稿样例（真实数据缺失时回退；需求 11.4–11.9）。
SAMPLE_STATS: list[StatSpec] = [
    StatSpec(
        key="matches", title="总比赛场次", en="TOTAL MATCHES",
        value=104, decimals=0, secondary="已结束 48 场",
        sparkline=True, sparkline_series=(48, 56, 64, 80, 96, 104),
    ),
    StatSpec(
        key="goals", title="总进球数", en="TOTAL GOALS",
        value=141, decimals=0, secondary="场均2.94球", delta="↑8%", icon="⚽",
    ),
    StatSpec(
        key="scorers", title="进球球员", en="GOAL SCORERS",
        value=89, decimals=0, secondary="来自32个国家", delta="↑15%", icon="👤",
    ),
    StatSpec(
        key="avg", title="平均进球", en="AVG GOALS",
        value=2.94, decimals=2, secondary="每场比赛", delta="↑6%", icon="🎯",
    ),
    StatSpec(
        key="teams", title="参赛球队", en="TEAMS",
        value=48, decimals=0, secondary="12个小组", icon="🛡",
    ),
    StatSpec(
        key="cities", title="主办城市", en="HOST CITIES",
        value=16, decimals=0, secondary="美国/加拿大/墨西哥", icon="📍",
    ),
]


# ════════════════════════════════════════════════════════════════════
#  纯函数：从真实数据测算统计值（缺失则回退样例）
# ════════════════════════════════════════════════════════════════════
def _match_goals(m) -> tuple[int, int] | None:
    """解析一场比赛的双方进球；无法解析（如未开赛）返回 ``None``。"""
    def _pick(*vals):
        for v in vals:
            if v not in (None, ""):
                return v
        return None

    a_raw = _pick(getattr(m, "fs_a", None), getattr(m, "score_a", None))
    b_raw = _pick(getattr(m, "fs_b", None), getattr(m, "score_b", None))
    if a_raw is None or b_raw is None:
        return None
    try:
        return int(a_raw), int(b_raw)
    except (TypeError, ValueError):
        return None


def _is_played(m) -> bool:
    status = getattr(m, "status", None)
    # 用值比较，避免对 MatchStatus 的硬依赖（保持可无头测试）。
    return getattr(status, "value", status) == "Played"


def _distinct_teams(matches) -> int:
    ids: set[str] = set()
    for m in matches:
        a = getattr(m, "team_a_id", None)
        b = getattr(m, "team_b_id", None)
        if a:
            ids.add(str(a))
        if b:
            ids.add(str(b))
    return len(ids)


def compute_stats(matches=None, groups=None, scorers=None) -> list[StatSpec]:
    """纯函数：把真实数据测算成六张 :class:`StatSpec`（顺序见 :data:`STAT_ORDER`）。

    任一指标的真实数据缺失时，沿用 :data:`SAMPLE_STATS` 中对应的样例值与文案
    （需求 11.3 的优雅降级）。``主办城市`` 始终采用样例（无公开数据源）。
    """
    matches = list(matches or [])
    groups = list(groups or [])
    scorers = list(scorers or [])
    base = {s.key: s for s in SAMPLE_STATS}

    # ── 总比赛场次 / 已完赛 ──
    matches_spec = base["matches"]
    if matches:
        total = len(matches)
        played = sum(1 for m in matches if _is_played(m))
        matches_spec = StatSpec(
            **{**matches_spec.__dict__,
               "value": total, "secondary": f"已结束 {played} 场"}
        )
    else:
        played = 48  # 样例「已结束 48 场」

    # ── 总进球数 / 场均 ──
    goals_spec = base["goals"]
    avg_spec = base["avg"]
    scored = [g for m in matches if (g := _match_goals(m)) is not None]
    if scored:
        total_goals = sum(a + b for a, b in scored)
        played_n = sum(1 for m in matches if _is_played(m)) or len(scored)
        avg = (total_goals / played_n) if played_n else 0.0
        goals_spec = StatSpec(
            **{**goals_spec.__dict__,
               "value": total_goals, "secondary": f"场均{avg:.2f}球"}
        )
        avg_spec = StatSpec(**{**avg_spec.__dict__, "value": round(avg, 2)})

    # ── 进球球员（人数 + 来源国家数）──
    scorers_spec = base["scorers"]
    real_scorers = [s for s in scorers if (getattr(s, "count", 0) or 0) > 0]
    if real_scorers:
        countries = {getattr(s, "team_name", "") for s in real_scorers}
        countries.discard("")
        secondary = (f"来自{len(countries)}个国家"
                     if countries else scorers_spec.secondary)
        scorers_spec = StatSpec(
            **{**scorers_spec.__dict__,
               "value": len(real_scorers), "secondary": secondary}
        )

    # ── 参赛球队 / 小组数 ──
    teams_spec = base["teams"]
    n_teams = _distinct_teams(matches)
    if not n_teams and groups:
        n_teams = sum(len(getattr(g, "teams", []) or []) for g in groups)
    if n_teams:
        secondary = (f"{len(groups)}个小组" if groups else teams_spec.secondary)
        teams_spec = StatSpec(
            **{**teams_spec.__dict__, "value": n_teams, "secondary": secondary}
        )

    # ── 主办城市（恒样例）──
    cities_spec = base["cities"]

    by_key = {
        "matches": matches_spec,
        "goals": goals_spec,
        "scorers": scorers_spec,
        "avg": avg_spec,
        "teams": teams_spec,
        "cities": cities_spec,
    }
    return [by_key[k] for k in STAT_ORDER]


# ════════════════════════════════════════════════════════════════════
#  单张统计卡
# ════════════════════════════════════════════════════════════════════
class StatCard(GlassCard):
    """一张玻璃统计卡：图标/折线 · 标题数字（CountUp）· 涨跌幅 · 次级文本。

    可点击：点击后通过 :pyattr:`clicked` 发出该卡的 ``key``，供上层跳转到
    对应榜单（球队 / 球员 / 赛程等）。
    """

    #: 点击该卡 —— 携带 :pyattr:`StatSpec.key`（matches / goals / ...）。
    clicked = pyqtSignal(str)

    def __init__(
        self,
        spec: StatSpec,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent, padding=0, palette=palette)
        self._palette = palette
        self._spec = spec
        # 更紧凑：缩小卡片最小高度，并让纵向尺寸「按内容收缩」（不再向下撑出大片
        # 空白），底部强调条紧贴「已结束 48 场」次级文案。
        self.setMinimumHeight(72)
        self.setCursor(pointing_hand_cursor())
        self.setToolTip("点击查看对应榜单")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._build_ui()
        self.set_spec(spec)

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._spec.key)
        super().mousePressEvent(ev)

    # ── 骨架 ─────────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        col = QVBoxLayout(self)
        col.setContentsMargins(15, 11, 15, 10)
        col.setSpacing(3)

        # 顶栏：标题文字（左） + 图标 / 折线（右）。
        top = QHBoxLayout()
        top.setSpacing(8)
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        self._title = QLabel()
        self._title.setStyleSheet(
            f"color: {p.text_dim}; font-size: 11px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        title_box.addWidget(self._title)
        self._en = QLabel()
        self._en.setStyleSheet(
            f"color: {p.text_faint}; font-size: 8px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.2px; background: transparent;"
        )
        title_box.addWidget(self._en)
        top.addLayout(title_box)
        top.addStretch(1)

        # 图标字形（emoji）。
        self._icon = QLabel()
        self._icon.setFixedSize(28, 28)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet(
            f"font-size: 17px; border-radius: {Radius.CHIP}px;"
            f" background: {rgba(p.primary, 0.12)};"
        )
        top.addWidget(self._icon, alignment=Qt.AlignmentFlag.AlignTop)

        # 迷你折线（取代图标，仅「总比赛场次」用）。
        self._spark = MiniSparkline(palette=p, width=56, height=24)
        top.addWidget(self._spark, alignment=Qt.AlignmentFlag.AlignTop)
        col.addLayout(top)

        # 标题数字（CountUp） + 涨跌幅。
        value_row = QHBoxLayout()
        value_row.setSpacing(6)
        self._value = CountUpNumber(decimals=self._spec.decimals)
        self._value.setStyleSheet(
            f"color: {p.text}; font-size: 23px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        value_row.addWidget(self._value, 0, Qt.AlignmentFlag.AlignBottom)
        self._delta = QLabel()
        self._delta.setStyleSheet(
            f"color: {p.win}; font-size: 11px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        value_row.addWidget(self._delta, 0, Qt.AlignmentFlag.AlignBottom)
        value_row.addStretch(1)
        col.addLayout(value_row)

        # 次级说明。
        self._secondary = QLabel()
        self._secondary.setWordWrap(True)
        self._secondary.setStyleSheet(
            f"color: {p.text_faint}; font-size: 10px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        col.addWidget(self._secondary)

        # 底部强调色条（紧贴次级文案下方，不再用弹性空白把卡片撑高）。
        from PyQt6.QtWidgets import QFrame
        col.addSpacing(6)
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {p.primary},"
            f" stop:1 {rgba(p.primary, 0.0)}); border-radius: 2px;"
        )
        col.addWidget(bar)

    # ── 公共 API ─────────────────────────────
    def set_spec(self, spec: StatSpec) -> None:
        """应用一份 :class:`StatSpec`（更新文案/图标，并触发数字滚动）。"""
        self._spec = spec
        self._title.setText(spec.title)
        self._en.setText(spec.en)
        self._secondary.setText(spec.secondary)

        # 图标 vs 折线（互斥）。
        if spec.sparkline:
            self._icon.hide()
            self._spark.show()
            self._spark.set_series(list(spec.sparkline_series))
        else:
            self._spark.hide()
            self._icon.setText(spec.icon)
            self._icon.setVisible(bool(spec.icon))

        # 涨跌幅（仅部分卡片）；↑ 绿 / ↓ 红。
        if spec.delta:
            self._delta.setText(spec.delta)
            up = not spec.delta.lstrip().startswith("↓")
            col = self._palette.win if up else self._palette.loss
            self._delta.setStyleSheet(
                f"color: {col}; font-size: 12px; font-weight: {Type.W_BOLD};"
                " background: transparent;"
            )
            self._delta.show()
        else:
            self._delta.clear()
            self._delta.hide()

        # CountUpNumber 的小数位是构造期固定的；spec 变更后若小数位不同需重建。
        if self._value._decimals != spec.decimals:  # noqa: SLF001
            self._value.setParent(None)
            self._value.deleteLater()
            self._value = CountUpNumber(decimals=spec.decimals)
            self._value.setStyleSheet(
                f"color: {self._palette.text}; font-size: 23px;"
                f" font-weight: {Type.W_BLACK}; background: transparent;"
            )
            # 重新插入到数字行的最前。
            self.layout().itemAt(1).layout().insertWidget(
                0, self._value, 0, Qt.AlignmentFlag.AlignBottom
            )
        self.play_count_up()

    def play_count_up(self) -> None:
        """从 0 滚动到目标值（需求 11.10）。"""
        self._value.set_target(self._spec.value)

    # ── 便捷查询（供测试 / 上层） ─────────────
    @property
    def spec(self) -> StatSpec:
        return self._spec

    @property
    def title_text(self) -> str:
        return self._spec.title

    @property
    def value_target(self) -> float:
        return self._value.target

    @property
    def secondary_text(self) -> str:
        return self._spec.secondary

    @property
    def delta_text(self) -> str:
        return self._spec.delta or ""

    @property
    def icon_text(self) -> str:
        return self._spec.icon

    @property
    def has_sparkline(self) -> bool:
        return self._spec.sparkline


# ════════════════════════════════════════════════════════════════════
#  StatStrip —— 六卡横排
# ════════════════════════════════════════════════════════════════════
class StatStrip(QWidget):
    """一排恰好六张等宽统计卡（需求 11.1 / 11.2）。"""

    #: 点击某张卡 —— 携带其 ``key``（matches / goals / scorers / avg / teams / cities）。
    clicked = pyqtSignal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        specs: list[StatSpec] | None = None,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(16)

        self._cards: list[StatCard] = []
        for spec in (specs or SAMPLE_STATS):
            card = StatCard(spec, palette=palette)
            card.clicked.connect(self.clicked.emit)
            # 等宽：每张卡 stretch = 1（需求 11.1）。
            self._row.addWidget(card, 1)
            self._cards.append(card)

        self._played_once = False

    # ── 公共 API ─────────────────────────────
    def set_stats(self, specs: list[StatSpec]) -> None:
        """用一组（六张）:class:`StatSpec` 更新各卡并重新滚动数字。

        ``specs`` 数量应为 6；少于卡片数时仅更新前若干张。
        """
        for card, spec in zip(self._cards, specs):
            card.set_spec(spec)

    def play_count_up(self) -> None:
        """让所有卡片的标题数字从 0 重新滚动（需求 11.10）。"""
        for card in self._cards:
            card.play_count_up()

    # ── 进入页面即滚动（需求 11.10） ─────────
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._played_once:
            self._played_once = True
            self.play_count_up()

    # ── 便捷查询（供测试 / 上层） ─────────────
    @property
    def cards(self) -> list[StatCard]:
        return list(self._cards)

    @property
    def titles(self) -> list[str]:
        return [c.title_text for c in self._cards]
