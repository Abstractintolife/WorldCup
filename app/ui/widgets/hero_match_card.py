"""hero_match_card —— 焦点比赛核心看板（WorldCup 3.0，取代 ``hero_banner`` +
home ``LiveMatchPanel``）。

像转播图形一样呈现一场焦点比赛（对应需求 5.1–5.7 / 6.1–6.4 / 7.1–7.4 /
8.1–8.2，设计 Property 10 / 12）：

* 左上角阶段标签「小组赛 第3轮」、右上角「即将开始」状态胶囊。
* 主队旗 — VS — 客队旗，队名「瑞士 / SWITZERLAND」「加拿大 / CANADA」（数据驱动）。
* 中央「距离开赛」+ 时 / 分 / 秒 翻牌式倒计时。
* 开球时间「06月25日 03:00」+ 场馆「BC Place Stadium, Vancouver」。
* 三枚胶囊按钮：观看直播（主，播放图标）/ 赛前分析 / 历史交锋。
* 左右轮播切换的 chevron 箭头。
* 胜平负概率分段条（红 → 中性 → 蓝），按 ``win_prob`` 比例分配宽度，
  分量不和为 100 时整条隐藏。
* 每队 Elo / FIFA 排名 / 世界排名，缺失渲染「—」。

**关键不变量**
--------------
* 倒计时：**唯一**的每秒 ``QTimer``（全应用除 FrameClock 外仅此一个定时器，
  需求 6.4），剩余时间非递增、绝不为负（Property 10）；到达开球即停表并显示
  「LIVE / KICK-OFF」。
* 胜平负：三段宽度正比于 ``win_prob``（和为 100，Property 12）。

数值数学全部抽成无 GUI 依赖的**纯函数**（:func:`remaining_seconds` /
:func:`decompose_remaining` / :func:`countdown_fields` / :func:`win_prob_is_valid`
/ :func:`win_prob_fractions` / :func:`win_prob_widths` / :func:`percentages_to_100`
/ :func:`fmt_rank`），便于无头属性测试（任务 8.3 / 8.5 / 8.7）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from PyQt6.QtCore import QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.fx.floating_flag import FloatingFlag
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor

# ════════════════════════════════════════════════════════════════════
#  纯函数：倒计时分解（任务 8.2 / Property 10）
# ════════════════════════════════════════════════════════════════════
SECONDS_PER_DAY = 86_400
SECONDS_PER_HOUR = 3_600
SECONDS_PER_MINUTE = 60


def remaining_seconds(kickoff_utc: datetime | None, now_utc: datetime) -> int:
    """纯函数：距开球的剩余秒数，**夹紧到非负整数**。

    * ``kickoff_utc is None`` → 返回 0。
    * 已到 / 已过开球 → 返回 0（绝不为负，需求 6.2）。

    由于该函数对「更晚的 ``now``」给出「更小（或相等）」的结果，连续每秒
    采样得到的剩余时间**非递增**（Property 10）。
    """
    if kickoff_utc is None:
        return 0
    if kickoff_utc.tzinfo is None:
        kickoff_utc = kickoff_utc.replace(tzinfo=timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    delta = (kickoff_utc - now_utc).total_seconds()
    if delta <= 0:
        return 0
    return int(delta)


def decompose_remaining(total_seconds: int) -> tuple[int, int, int, int]:
    """纯函数：把剩余秒数分解为 ``(天, 时, 分, 秒)``。

    负值被夹紧为 0；分解满足
    ``天*86400 + 时*3600 + 分*60 + 秒 == max(0, total_seconds)``，
    且 ``0 <= 时 < 24``、``0 <= 分 < 60``、``0 <= 秒 < 60``。
    """
    s = int(total_seconds)
    if s < 0:
        s = 0
    days = s // SECONDS_PER_DAY
    rem = s % SECONDS_PER_DAY
    hours = rem // SECONDS_PER_HOUR
    rem %= SECONDS_PER_HOUR
    minutes = rem // SECONDS_PER_MINUTE
    seconds = rem % SECONDS_PER_MINUTE
    return days, hours, minutes, seconds


def countdown_fields(total_seconds: int) -> tuple[int, int, int]:
    """纯函数：为「时 / 分 / 秒」三栏倒计时计算字段。

    把「天」折算进小时（``时 = 天*24 + 时``），返回 ``(总小时, 分, 秒)``，
    便于在没有「天」栏的翻牌钟里完整呈现剩余时间。
    """
    days, hours, minutes, seconds = decompose_remaining(total_seconds)
    return days * 24 + hours, minutes, seconds


# ════════════════════════════════════════════════════════════════════
#  纯函数：胜平负分段（任务 8.4 / Property 12）
# ════════════════════════════════════════════════════════════════════
def win_prob_is_valid(triple: tuple[int, int, int]) -> bool:
    """纯函数：胜平负三元组是否合法 —— 各分量 ∈ [0,100] 且和恰为 100。"""
    if triple is None or len(triple) != 3:
        return False
    try:
        h, d, a = (int(x) for x in triple)
    except (TypeError, ValueError):
        return False
    if not all(0 <= v <= 100 for v in (h, d, a)):
        return False
    return h + d + a == 100


def win_prob_fractions(triple: tuple[int, int, int]) -> tuple[float, float, float]:
    """纯函数：合法三元组 → 各段占比（``p/100``），三者和为 1.0。

    非法三元组抛 ``ValueError``（调用方应先用 :func:`win_prob_is_valid` 判断
    并在非法时隐藏整条，需求 7.4）。
    """
    if not win_prob_is_valid(triple):
        raise ValueError(f"invalid win_prob (must sum to 100): {triple!r}")
    h, d, a = (int(x) for x in triple)
    return h / 100.0, d / 100.0, a / 100.0


def win_prob_widths(triple: tuple[int, int, int], total_width: int) -> tuple[int, int, int]:
    """纯函数：合法三元组 → 三段**整数像素宽度**，三者和恰为 ``total_width``。

    主、平两段按比例四舍五入，末段（客胜）吸收舍入余量，保证铺满且无缝。
    宽度严格正比于 ``win_prob``（在像素取整精度内）。
    """
    if not win_prob_is_valid(triple):
        raise ValueError(f"invalid win_prob (must sum to 100): {triple!r}")
    w = max(0, int(total_width))
    h, d, a = (int(x) for x in triple)
    w_home = round(w * h / 100.0)
    w_draw = round(w * d / 100.0)
    w_away = w - w_home - w_draw
    if w_away < 0:  # 极端舍入兜底
        w_away = 0
        w_draw = w - w_home
    return int(w_home), int(w_draw), int(w_away)


def percentages_to_100(probs: tuple[float, float, float]) -> tuple[int, int, int]:
    """纯函数：把三个（任意非负）概率/权重归一化为**和恰为 100** 的整数百分比。

    采用「最大余数法」分配余数，保证 ``a + b + c == 100``（输入全 0 时回退
    为均分近似）。用于把模型给出的 ``win_a/draw/win_b`` 转成可供分段条使用的
    合法三元组。
    """
    vals = [max(0.0, float(x)) for x in probs]
    total = sum(vals)
    if total <= 0:
        return 34, 33, 33
    scaled = [v / total * 100.0 for v in vals]
    floors = [int(x) for x in scaled]
    remainder = 100 - sum(floors)
    # 按小数部分从大到小补足剩余的名额。
    order = sorted(range(3), key=lambda i: scaled[i] - floors[i], reverse=True)
    for i in range(remainder):
        floors[order[i % 3]] += 1
    return floors[0], floors[1], floors[2]


def fmt_rank(value: int | None) -> str:
    """纯函数：排名 / 评分缺失（``None``）渲染占位「—」，否则原样字符串化（需求 8.2）。"""
    if value is None:
        return "—"
    return str(value)


# ════════════════════════════════════════════════════════════════════
#  视图模型
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class HeroMeta:
    """焦点比赛的展示元数据（适配既有 :class:`Match` 模型）。

    ``win_prob`` 是 ``(主胜, 平, 客胜)`` 的整数百分比，合法时和恰为 100；
    非法（不和 100）时分段条整条隐藏（需求 7.4）。Elo / FIFA / 世界排名
    缺失用 ``None`` 表达，渲染为「—」（需求 8.2）。
    """

    stage_label: str = "小组赛 第3轮"
    status_label: str = "即将开始"
    kickoff_utc: datetime | None = None
    venue: str = ""
    home_name_en: str = ""
    away_name_en: str = ""
    win_prob: tuple[int, int, int] = (0, 0, 0)
    home_elo: int | None = None
    away_elo: int | None = None
    home_fifa_rank: int | None = None
    away_fifa_rank: int | None = None
    home_world_rank: int | None = None
    away_world_rank: int | None = None

    @property
    def win_prob_valid(self) -> bool:
        """``win_prob`` 是否为合法三元组（各 ∈ [0,100] 且和为 100）。"""
        return win_prob_is_valid(self.win_prob)


# ════════════════════════════════════════════════════════════════════
#  翻牌式倒计时钟（时 / 分 / 秒）
# ════════════════════════════════════════════════════════════════════
class _FlipDigit(QWidget):
    """单个「翻牌」数字格：深色圆角盒 + 大号数字 + 下方单位标签。"""

    def __init__(self, unit: str, palette: HudPalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        # 固定整格尺寸（数字盒 + 下方单位标签），为单位文字预留独立行高，
        # 杜绝「时/分/秒 小字与上方数字重叠」（需求：修正时分秒与具体时间重叠）。
        self.setFixedSize(58, 80)
        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)

        self._num = QLabel("00")
        self._num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._num.setFixedSize(58, 56)
        self._num.setStyleSheet(
            f"background: {rgba('#000000', 0.35)};"
            f" border: 1px solid {palette.glass_border};"
            f" border-radius: {Radius.CHIP}px;"
            f" color: {palette.text};"
            f" font-size: 30px; font-weight: {Type.W_BLACK};"
            " letter-spacing: 1px;"
        )
        col.addWidget(self._num, alignment=Qt.AlignmentFlag.AlignCenter)

        self._unit = QLabel(unit)
        self._unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unit.setFixedHeight(16)
        self._unit.setStyleSheet(
            f"color: {palette.text_dim}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BOLD}; background: transparent;"
        )
        col.addWidget(self._unit, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_value(self, value: int) -> None:
        self._num.setText(f"{int(value):02d}")

    def set_text(self, text: str) -> None:
        self._num.setText(text)


class CountdownClock(QWidget):
    """时 / 分 / 秒 翻牌式倒计时显示（由 HeroMatchCard 的单一 QTimer 驱动）。"""

    def __init__(self, palette: HudPalette = NIGHT_STADIUM, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        self._h = _FlipDigit("时", palette)
        self._m = _FlipDigit("分", palette)
        self._s = _FlipDigit("秒", palette)

        self._live = QLabel("")
        self._live.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._live.setStyleSheet(
            f"color: {palette.live}; font-size: {Type.H2}px;"
            f" font-weight: {Type.W_BLACK}; letter-spacing: 2px; background: transparent;"
        )
        self._live.hide()

        row.addStretch(1)
        row.addWidget(self._h)
        row.addWidget(self._sep())
        row.addWidget(self._m)
        row.addWidget(self._sep())
        row.addWidget(self._s)
        row.addWidget(self._live)
        row.addStretch(1)

    def _sep(self) -> QLabel:
        c = QLabel(":")
        c.setStyleSheet(
            f"color: {self._palette.text_faint}; font-size: 28px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        return c

    def set_time(self, hours: int, minutes: int, seconds: int) -> None:
        self._set_digits_visible(True)
        self._h.set_value(hours)
        self._m.set_value(minutes)
        self._s.set_value(seconds)

    def show_live(self) -> None:
        """到达开球：隐藏翻牌、显示「LIVE / KICK-OFF」（需求 6.3）。"""
        self._set_digits_visible(False)
        self._live.setText("LIVE · KICK-OFF")
        self._live.show()

    def show_status(self, text: str, *, color: str | None = None) -> None:
        """显示任意状态文案（如「进行中」「全场结束」），替代翻牌数字。"""
        self._set_digits_visible(False)
        self._live.setStyleSheet(
            f"color: {color or self._palette.live}; font-size: {Type.H2}px;"
            f" font-weight: {Type.W_BLACK}; letter-spacing: 2px; background: transparent;"
        )
        self._live.setText(text)
        self._live.show()

    def _set_digits_visible(self, visible: bool) -> None:
        for w in (self._h, self._m, self._s):
            w.setVisible(visible)
        if visible:
            self._live.hide()


# ════════════════════════════════════════════════════════════════════
#  胜平负分段条（红 → 中性 → 蓝）
# ════════════════════════════════════════════════════════════════════
class WinProbBar(QWidget):
    """三段（主胜 / 平 / 客胜）从左到右的胜平负概率条。

    宽度正比于 ``win_prob``（Property 12）；分量不和为 100 时整条隐藏（需求 7.4）。
    """

    def __init__(self, palette: HudPalette = NIGHT_STADIUM, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._triple: tuple[int, int, int] = (0, 0, 0)
        self._valid = False
        self.setFixedHeight(14)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_probabilities(self, triple: tuple[int, int, int]) -> bool:
        """设置三元组；返回是否合法。非法 → 隐藏整条（需求 7.4）。"""
        self._triple = tuple(int(x) for x in triple)  # type: ignore[assignment]
        self._valid = win_prob_is_valid(self._triple)
        self.setVisible(self._valid)
        self.update()
        return self._valid

    @property
    def is_valid(self) -> bool:
        return self._valid

    def paintEvent(self, _ev) -> None:
        if not self._valid:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        radius = h / 2.0

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
        p.setClipPath(clip)

        w_home, w_draw, w_away = win_prob_widths(self._triple, w)
        # 红（主胜）→ 中性（平）→ 蓝（客胜）。
        home_col = QColor(self._palette.loss)        # 红
        draw_col = QColor(self._palette.text_faint)   # 中性
        away_col = QColor(self._palette.secondary)    # 蓝

        x = 0
        for width, base in (
            (w_home, home_col),
            (w_draw, draw_col),
            (w_away, away_col),
        ):
            if width <= 0:
                continue
            grad = QLinearGradient(x, 0, x + width, 0)
            top = QColor(base)
            bottom = QColor(base)
            top.setAlphaF(0.95)
            bottom.setAlphaF(0.70)
            grad.setColorAt(0.0, top)
            grad.setColorAt(1.0, bottom)
            p.fillRect(QRectF(x, 0, width, h), grad)
            x += width


# ════════════════════════════════════════════════════════════════════
#  Hero Match Card
# ════════════════════════════════════════════════════════════════════
class HeroMatchCard(GlassCard):
    """焦点比赛核心看板（继承 :class:`GlassCard`）。"""

    #: 观看直播（主操作）。
    watch_clicked = pyqtSignal(object)
    #: 赛前分析。
    analysis_clicked = pyqtSignal(object)
    #: 历史交锋。
    h2h_clicked = pyqtSignal(object)
    #: 轮播：上一场 / 下一场。
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, *,
                 palette: HudPalette = NIGHT_STADIUM) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        self._match: Match | None = None
        self._meta: HeroMeta = HeroMeta()
        self.setMinimumHeight(360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 唯一的每秒倒计时定时器（全应用除 FrameClock 外的唯一定时器，需求 6.4）。
        self._cd_timer = QTimer(self)
        self._cd_timer.setInterval(1000)
        self._cd_timer.timeout.connect(self._tick_countdown)

        self._build_ui()
        self.set_match(None, HeroMeta())

    # ── 构建静态骨架 ─────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(16)

        # 顶栏：阶段标签（左） + 状态胶囊（右）
        top = QHBoxLayout()
        top.setSpacing(8)
        self._stage = QLabel("小组赛 第3轮")
        self._stage.setStyleSheet(
            f"color: {p.text_dim}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BOLD}; letter-spacing: 1px; background: transparent;"
        )
        top.addWidget(self._stage)
        top.addStretch(1)
        self._status_pill = QLabel("即将开始")
        self._status_pill.setStyleSheet(self._pill_style(p.primary))
        top.addWidget(self._status_pill)
        root.addLayout(top)

        # 中部：chevron | 主队 | 中央(VS + 距离开赛 + 倒计时) | 客队 | chevron
        mid = QHBoxLayout()
        mid.setSpacing(14)

        self._chev_l = self._chevron("‹")
        self._chev_l.clicked.connect(self.prev_clicked.emit)
        mid.addWidget(self._chev_l, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._home_flag = FloatingFlag(None, height=82, radius=10)
        self._away_flag = FloatingFlag(None, height=82, radius=10)
        self._home_zh, self._home_en, home_col = self._team_col(self._home_flag)
        mid.addWidget(home_col, 1)

        center = QVBoxLayout()
        center.setSpacing(8)
        self._vs = QLabel("VS")
        self._vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._vs.setStyleSheet(
            f"color: {p.text_faint}; font-size: {Type.H1}px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        center.addWidget(self._vs)
        cap = QLabel("距离开赛")
        cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cap.setStyleSheet(
            f"color: {p.text_dim}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BOLD}; letter-spacing: 2px; background: transparent;"
        )
        center.addWidget(cap)
        self._clock = CountdownClock(p)
        center.addWidget(self._clock)
        center_host = QWidget()
        center_host.setLayout(center)
        mid.addWidget(center_host, 0)

        self._away_zh, self._away_en, away_col = self._team_col(self._away_flag)
        mid.addWidget(away_col, 1)

        self._chev_r = self._chevron("›")
        self._chev_r.clicked.connect(self.next_clicked.emit)
        mid.addWidget(self._chev_r, alignment=Qt.AlignmentFlag.AlignVCenter)

        root.addLayout(mid)

        # 开球时间 + 场馆
        self._meta_lbl = QLabel("")
        self._meta_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._meta_lbl.setStyleSheet(
            f"color: {p.text_dim}; font-size: {Type.BODY}px;"
            f" font-weight: {Type.W_MEDIUM}; background: transparent;"
        )
        root.addWidget(self._meta_lbl)

        # 每队 Elo / FIFA / 世界排名
        ratings = QHBoxLayout()
        ratings.setSpacing(10)
        self._home_ratings = QLabel("")
        self._home_ratings.setStyleSheet(self._ratings_style())
        self._away_ratings = QLabel("")
        self._away_ratings.setStyleSheet(self._ratings_style())
        self._away_ratings.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ratings.addWidget(self._home_ratings, 1)
        ratings.addWidget(self._away_ratings, 1)
        root.addLayout(ratings)

        # 胜平负分段条 + 三个标签
        self._prob_bar = WinProbBar(p)
        root.addWidget(self._prob_bar)
        prob_labels = QHBoxLayout()
        prob_labels.setSpacing(6)
        self._lbl_home = QLabel("")
        self._lbl_draw = QLabel("")
        self._lbl_away = QLabel("")
        self._lbl_home.setStyleSheet(self._prob_label_style(p.loss))
        self._lbl_draw.setStyleSheet(self._prob_label_style(p.text_dim))
        self._lbl_draw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_away.setStyleSheet(self._prob_label_style(p.secondary))
        self._lbl_away.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prob_labels.addWidget(self._lbl_home, 1)
        prob_labels.addWidget(self._lbl_draw, 1)
        prob_labels.addWidget(self._lbl_away, 1)
        self._prob_labels_host = QWidget()
        self._prob_labels_host.setLayout(prob_labels)
        root.addWidget(self._prob_labels_host)

        # 三枚操作胶囊
        actions = QHBoxLayout()
        actions.setSpacing(10)
        self._btn_watch = QPushButton("▶  观看直播")
        self._btn_watch.setProperty("pill", "primary")
        self._btn_watch.setCursor(pointing_hand_cursor())
        self._btn_watch.setMinimumHeight(40)
        self._btn_watch.setStyleSheet(self._primary_btn_style())
        self._btn_watch.clicked.connect(lambda: self.watch_clicked.emit(self._match))

        self._btn_analysis = QPushButton("赛前分析")
        self._btn_h2h = QPushButton("历史交锋")
        for b, slot in ((self._btn_analysis, self.analysis_clicked),
                        (self._btn_h2h, self.h2h_clicked)):
            b.setCursor(pointing_hand_cursor())
            b.setMinimumHeight(40)
            b.setStyleSheet(self._ghost_btn_style())
            b.clicked.connect(lambda _c=False, s=slot: s.emit(self._match))

        actions.addWidget(self._btn_watch, 2)
        actions.addWidget(self._btn_analysis, 1)
        actions.addWidget(self._btn_h2h, 1)
        root.addLayout(actions)

    # ── 子构件工厂 ───────────────────────────
    def _team_col(self, flag: FloatingFlag) -> tuple[QLabel, QLabel, QWidget]:
        p = self._palette
        host = QWidget()
        col = QVBoxLayout(host)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)
        col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(flag, alignment=Qt.AlignmentFlag.AlignCenter)
        zh = QLabel("—")
        zh.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zh.setStyleSheet(
            f"color: {p.text}; font-size: {Type.H3}px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("")
        en.setAlignment(Qt.AlignmentFlag.AlignCenter)
        en.setStyleSheet(
            f"color: {p.text_faint}; font-size: {Type.OVERLINE}px;"
            f" font-weight: {Type.W_BOLD}; letter-spacing: 2px; background: transparent;"
        )
        col.addWidget(en)
        return zh, en, host

    def _chevron(self, glyph: str) -> QPushButton:
        b = QPushButton(glyph)
        b.setCursor(pointing_hand_cursor())
        b.setFixedSize(34, 34)
        p = self._palette
        b.setStyleSheet(
            "QPushButton {"
            f" background: {p.glass_fill};"
            f" border: 1px solid {p.glass_border};"
            f" border-radius: 17px; color: {p.text_dim};"
            f" font-size: 20px; font-weight: {Type.W_BLACK}; }}"
            "QPushButton:hover {"
            f" border: 1px solid {p.glass_border_hi}; color: {p.text}; }}"
        )
        return b

    def _pill_style(self, color: str) -> str:
        return (
            f"background: {rgba(color, 0.16)}; color: {color};"
            f" border: 1px solid {rgba(color, 0.45)}; border-radius: {Radius.PILL}px;"
            f" padding: 4px 14px; font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD};"
        )

    def _ratings_style(self) -> str:
        p = self._palette
        return (
            f"color: {p.text_dim}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_MEDIUM}; background: transparent;"
        )

    def _prob_label_style(self, color: str) -> str:
        return (
            f"color: {color}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BOLD}; background: transparent;"
        )

    def _primary_btn_style(self) -> str:
        p = self._palette
        return (
            "QPushButton {"
            f" background: {rgba(p.primary, 0.20)}; color: {p.primary_hi};"
            f" border: 1px solid {rgba(p.primary, 0.55)};"
            f" border-radius: {Radius.PILL}px; padding: 8px 18px;"
            f" font-size: {Type.BODY}px; font-weight: {Type.W_BOLD}; }}"
            "QPushButton:hover {"
            f" background: {rgba(p.primary, 0.30)};"
            f" border: 1px solid {rgba(p.primary, 0.75)}; }}"
        )

    def _ghost_btn_style(self) -> str:
        p = self._palette
        return (
            "QPushButton {"
            f" background: {p.glass_fill}; color: {p.text};"
            f" border: 1px solid {p.glass_border};"
            f" border-radius: {Radius.PILL}px; padding: 8px 16px;"
            f" font-size: {Type.BODY}px; font-weight: {Type.W_MEDIUM}; }}"
            "QPushButton:hover {"
            f" border: 1px solid {p.glass_border_hi}; }}"
        )

    # ── 公共 API ─────────────────────────────
    def set_match(self, match: Match | None, meta: HeroMeta) -> None:
        """设置焦点比赛 + 展示元数据，刷新整张卡并（重）启动倒计时。"""
        self._match = match
        self._meta = meta

        self._stage.setText(meta.stage_label or "—")
        self._status_pill.setText(meta.status_label or "—")

        home_zh = match.team_a_name if match is not None else "—"
        away_zh = match.team_b_name if match is not None else "—"
        # 队名做显示用简写（最多 4 个汉字），紧凑且更美观（不影响底层数据）。
        from app.utils.text_utils import short_country_name
        self._home_zh.setText(short_country_name(home_zh) or "—")
        self._away_zh.setText(short_country_name(away_zh) or "—")
        self._home_en.setText((meta.home_name_en or "").upper())
        self._away_en.setText((meta.away_name_en or "").upper())

        self._home_flag.set_nationality(home_zh if match is not None else None)
        self._away_flag.set_nationality(away_zh if match is not None else None)
        self._home_flag.start_float()
        self._away_flag.start_float()

        # 开球时间 + 场馆
        self._meta_lbl.setText(self._format_meta(meta))

        # 焦点比赛若正在进行 / 已结束：中央用大比分替代「VS」，并在倒计时位置
        # 显示比赛状态（进行中 / 全场结束），不再倒数（需求：正在踢的比赛加比分）。
        self._render_center_score(match)

        # 每队 Elo / FIFA / 世界排名（缺失 → 「—」）
        self._home_ratings.setText(self._format_ratings(
            meta.home_elo, meta.home_fifa_rank, meta.home_world_rank))
        self._away_ratings.setText(self._format_ratings(
            meta.away_elo, meta.away_fifa_rank, meta.away_world_rank))

        # 胜平负分段条 + 标签
        self._render_win_prob(match, meta)

    def _render_center_score(self, match: Match | None) -> None:
        """中央区按比赛状态切换：进行中 / 已结束 → 大比分 + 状态；否则 VS + 倒计时。"""
        p = self._palette
        is_live = bool(match is not None and getattr(match, "is_live", False))
        is_played = bool(match is not None
                         and getattr(match, "status", None) == MatchStatus.PLAYED)
        if match is not None and (is_live or is_played):
            ga, gb = self._match_goals(match)
            color = p.live if is_live else p.text
            self._vs.setText(f"{ga} - {gb}")
            self._vs.setStyleSheet(
                f"color: {color}; font-size: 46px;"
                f" font-weight: {Type.W_BLACK}; background: transparent;"
            )
            self._cd_timer.stop()
            if is_live:
                minute = (getattr(match, "minute", "") or "").strip()
                self._clock.show_status(f"{minute}'" if minute else "进行中",
                                        color=p.live)
            else:
                self._clock.show_status("全场结束", color=p.text_dim)
            return
        # 即将开赛（或无比赛）：恢复「VS」并起动倒计时。
        self._vs.setText("VS")
        self._vs.setStyleSheet(
            f"color: {p.text_faint}; font-size: {Type.H1}px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        self._restart_countdown()

    @staticmethod
    def _match_goals(match: Match) -> tuple[int, int]:
        """从 Match 取主客进球数（优先全场比分 fs_*，回退 score_*）。"""
        def _i(v) -> int:
            try:
                return int(v) if v not in (None, "") else 0
            except (TypeError, ValueError):
                return 0
        a = _i(getattr(match, "fs_a", None) if getattr(match, "fs_a", None) not in (None, "")
               else getattr(match, "score_a", None))
        b = _i(getattr(match, "fs_b", None) if getattr(match, "fs_b", None) not in (None, "")
               else getattr(match, "score_b", None))
        return a, b

    # ── 内部：格式化 ─────────────────────────
    def _format_meta(self, meta: HeroMeta) -> str:
        from app.utils.time_utils import to_local
        dt = to_local(meta.kickoff_utc)
        when = dt.strftime("%m月%d日 %H:%M") if dt is not None else "—"
        if meta.venue:
            return f"{when}  ·  {meta.venue}"
        return when

    def _format_ratings(self, elo: int | None, fifa: int | None,
                        world: int | None) -> str:
        """仅展示国际足联（FIFA）世界排名（已按需求移除 Elo / 世界排名两项）。"""
        return f"FIFA 世界排名 #{fmt_rank(fifa)}"

    def _render_win_prob(self, match: Match | None, meta: HeroMeta) -> None:
        valid = self._prob_bar.set_probabilities(meta.win_prob)
        self._prob_labels_host.setVisible(valid)
        if not valid:
            return
        h, d, a = (int(x) for x in meta.win_prob)
        from app.utils.text_utils import short_country_name
        home_zh = short_country_name(match.team_a_name) if match is not None else "主队"
        away_zh = short_country_name(match.team_b_name) if match is not None else "客队"
        self._lbl_home.setText(f"{h}% {home_zh}胜")
        self._lbl_draw.setText(f"{d}% 平局")
        self._lbl_away.setText(f"{a}% {away_zh}胜")

    # ── 内部：倒计时（唯一定时器，需求 6.x / Property 10） ──
    def _restart_countdown(self) -> None:
        self._cd_timer.stop()
        meta = self._meta
        if meta.kickoff_utc is None:
            # 无开球时间：显示静态 00:00:00（不起表）。
            self._clock.set_time(0, 0, 0)
            return
        # 先渲染一帧，再按需起表。
        if self._tick_countdown():
            self._cd_timer.start()

    def _tick_countdown(self) -> bool:
        """推进一帧倒计时；返回是否仍需继续（开球前 ``True``）。"""
        remaining = remaining_seconds(self._meta.kickoff_utc, datetime.now(timezone.utc))
        if remaining <= 0:
            self._clock.show_live()
            self._cd_timer.stop()
            return False
        hours, minutes, seconds = countdown_fields(remaining)
        self._clock.set_time(hours, minutes, seconds)
        return True

    # ── 生命周期：隐藏时停表，避免后台空转 ──────
    def hideEvent(self, ev) -> None:
        self._cd_timer.stop()
        super().hideEvent(ev)

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        # 重新进入视图时，按当前比赛状态恢复中央显示（比分 / 倒计时）。
        self._render_center_score(self._match)
