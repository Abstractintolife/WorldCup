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

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices
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

from app.models.match import Match, MatchStatus, Round
from app.models.news import NewsArticle
from app.models.player import PlayerRanking, RankingType
from app.models.standing import GroupStanding, TeamStanding
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.dashboard_charts import DualRadarChart, RingProgress, Sparkline
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.image_loader import RemoteImage
from app.ui.widgets.misc import Card
from app.utils.time_utils import fmt_time, is_today, local_now

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


def _clamp(v: float, lo: float = 5.0, hi: float = 99.0) -> int:
    return int(max(lo, min(hi, v)))


def _goals(m: Match) -> tuple[int, int] | None:
    """取一场已结束/进行中比赛的双方进球。无法解析返回 None。"""
    try:
        a = int(m.fs_a if m.fs_a not in (None, "") else (m.score_a or 0))
        b = int(m.fs_b if m.fs_b not in (None, "") else (m.score_b or 0))
    except (TypeError, ValueError):
        return None
    return a, b


def _clear_layout(layout) -> None:
    while layout.count():
        it = layout.takeAt(0)
        w = it.widget()
        if w is not None:
            w.deleteLater()
        else:
            sub = it.layout()
            if sub is not None:
                _clear_layout(sub)


# ════════════════════════════════════════════════════════════
#  可点击行容器
# ════════════════════════════════════════════════════════════
class _ClickRow(QFrame):
    """带 hover 高亮的可点击行。"""

    clicked = pyqtSignal()

    def __init__(self, *, height: int = 40, radius: int = 9,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ClickRow")
        self.setFixedHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"QFrame#ClickRow{{background: rgba(255,255,255,0.03);"
            f" border-radius:{radius}px;}}"
            "QFrame#ClickRow:hover{background: rgba(255,255,255,0.08);}"
        )

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(ev)


# ── 分区标题（卡片内）────────────────────────────────────────
def _panel_title(text: str, en: str, accent: str, hint: str = "") -> QWidget:
    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    bar = QFrame()
    bar.setFixedSize(4, 22)
    bar.setStyleSheet(
        f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        f" stop:0 {accent}, stop:1 rgba(255,255,255,0.05)); border-radius:2px;"
    )
    row.addWidget(bar)
    tb = QVBoxLayout()
    tb.setSpacing(0)
    t = QLabel(text)
    t.setStyleSheet(f"font-size:15.5px; font-weight:900; color:{C_TEXT}; background:transparent;")
    tb.addWidget(t)
    if en:
        e = QLabel(en)
        e.setStyleSheet(
            f"color:{accent}; font-size:8.5px; font-weight:800; letter-spacing:1.6px;"
            " background:transparent;"
        )
        tb.addWidget(e)
    row.addLayout(tb)
    row.addStretch(1)
    if hint:
        hl = QLabel(hint)
        hl.setObjectName("PanelHint")
        hl.setStyleSheet(f"color:{C_FAINT}; font-size:10.5px; font-weight:600; background:transparent;")
        row.addWidget(hl, alignment=Qt.AlignmentFlag.AlignVCenter)
    return w


def _chip(text: str, color: str, *, solid: bool = True, font_px: int = 10) -> QLabel:
    lbl = QLabel(text)
    if solid:
        lbl.setStyleSheet(
            f"background:{color}; color:#fff; border-radius:8px; padding:2px 9px;"
            f" font-size:{font_px}px; font-weight:800;"
        )
    else:
        lbl.setStyleSheet(
            f"background: rgba({_rgb(color)},0.16); color:{color}; border-radius:8px;"
            f" padding:2px 9px; font-size:{font_px}px; font-weight:800;"
            f" border:1px solid rgba({_rgb(color)},0.4);"
        )
    lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return lbl


# ════════════════════════════════════════════════════════════
#  实时比赛核心看板
# ════════════════════════════════════════════════════════════
class _LiveBadge(QLabel):
    """闪烁的 ★ LIVE 徽章。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("★ LIVE", parent)
        self.setStyleSheet(
            f"background:{C_LIVE}; color:#fff; border-radius:9px; padding:3px 11px;"
            " font-size:11px; font-weight:900; letter-spacing:1px;"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        from app.ui.design.frame_clock import FrameClock
        self._clock = FrameClock.instance()

    def showEvent(self, ev):
        super().showEvent(ev)
        self._clock.subscribe(self._tick)

    def hideEvent(self, ev):
        super().hideEvent(ev)
        try:
            self._clock.unsubscribe(self._tick)
        except Exception:
            pass

    def _tick(self, t: float, _dt: float):
        a = 0.55 + 0.45 * (1.0 - math.cos(t * 3.0)) * 0.5
        self.setStyleSheet(
            f"background: rgba({_rgb(C_LIVE)},{a:.2f}); color:#fff; border-radius:9px;"
            " padding:3px 11px; font-size:11px; font-weight:900; letter-spacing:1px;"
        )


class LiveMatchPanel(Card):
    """焦点比赛核心看板（进行中 / 即将开赛 / 最近结束）。"""

    def __init__(self, *, on_open=None, on_predict=None, on_watch=None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_LIVE)
        self._on_open = on_open
        self._on_predict = on_predict
        self._on_watch = on_watch
        self._match: Match | None = None
        self.setMinimumWidth(540)
        self.setMinimumHeight(372)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        # 顶栏：LIVE/状态 + 阶段 + 时间
        top = QHBoxLayout()
        top.setSpacing(10)
        self._badge = _LiveBadge()
        top.addWidget(self._badge)
        self._stage = QLabel("—")
        self._stage.setStyleSheet(
            f"color:{C_DIM}; font-size:12px; font-weight:700; background:transparent;")
        top.addWidget(self._stage)
        top.addStretch(1)
        self._clock = QLabel("")
        self._clock.setStyleSheet(
            f"color:{C_LIVE}; font-size:14px; font-weight:900; background:transparent;")
        top.addWidget(self._clock)
        root.addLayout(top)

        # 比分行
        score = QHBoxLayout()
        score.setSpacing(8)
        self._home_block = QWidget()
        self._away_block = QWidget()
        score.addWidget(self._home_block, 1)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        self._big = QLabel("—")
        self._big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._big.setStyleSheet(
            "font-size:52px; font-weight:900; color:#FFFFFF; background:transparent;"
            " letter-spacing:2px;")
        mid.addWidget(self._big)
        self._status_txt = QLabel("")
        self._status_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_txt.setStyleSheet(
            f"color:{C_LIVE}; font-size:11px; font-weight:800; background:transparent;")
        mid.addWidget(self._status_txt)
        mid_w = QWidget()
        mid_w.setLayout(mid)
        mid_w.setFixedWidth(120)
        score.addWidget(mid_w)
        score.addWidget(self._away_block, 1)
        root.addLayout(score)

        # 副信息行（开赛时间 / 日期）
        self._meta = QLabel("")
        self._meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._meta.setStyleSheet(
            f"color:{C_DIM}; font-size:12px; font-weight:600; background:transparent;")
        root.addWidget(self._meta)

        root.addStretch(1)

        # 操作按钮：观看直播（主）+ 详情/预测（次）
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self._watch_btn = QPushButton("📺  观看直播")
        self._watch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._watch_btn.setMinimumHeight(42)
        self._watch_btn.setStyleSheet(
            "QPushButton{background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {C_PRIMARY}, stop:1 #2D8CFF); color:#fff; border:none;"
            " border-radius:13px; font-size:14px; font-weight:800; letter-spacing:1px;}"
            "QPushButton:hover{background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 #46D2FF, stop:1 {C_PRIMARY});}}")
        self._watch_btn.clicked.connect(self._fire_watch)
        btn_row.addWidget(self._watch_btn, 1)

        self._action = QPushButton("查看详情")
        self._action.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action.setMinimumHeight(42)
        self._action.setStyleSheet(
            "QPushButton{background: rgba(255,255,255,0.08); color:#fff;"
            " border:1px solid rgba(255,255,255,0.18); border-radius:13px;"
            " font-size:13px; font-weight:800; padding:0 16px;}"
            "QPushButton:hover{background: rgba(255,255,255,0.16);}")
        self._action.clicked.connect(self._fire_action)
        btn_row.addWidget(self._action)
        root.addLayout(btn_row)

        # 底部来源
        self._venue = QLabel("数据来源 · 懂球帝实时数据")
        self._venue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._venue.setStyleSheet(
            f"color:{C_FAINT}; font-size:11px; font-weight:600; background:transparent;")
        root.addWidget(self._venue)

        self._empty()

    def _fire_action(self) -> None:
        if self._match is None:
            return
        if self._match.status in (MatchStatus.FIXTURE, MatchStatus.UNKNOWN) and self._on_predict:
            self._on_predict(self._match)
        elif self._on_open:
            self._on_open(self._match)

    def _fire_watch(self) -> None:
        # 观看直播 / 导入 M3U8 源 —— 即使当前无进行中比赛也允许打开（手动导入源）。
        if self._on_watch:
            self._on_watch(self._match)

    def _team_block(self, name: str, *, home: bool = True) -> QWidget:
        """单侧队伍块：国旗 + 队名横向排列，国旗紧贴中线 VS。

        主队（左）：``… 美国 🇺🇸``　客队（右）：``🇰🇷 韩国 …``
        左右拼起来即「美国 🇺🇸  VS  🇰🇷 韩国」的对阵横幅。
        """
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        flag = FlagIcon(name, height=60, radius=12)
        n = QLabel(name)
        n.setStyleSheet(
            f"color:{C_TEXT}; font-size:19px; font-weight:900;"
            " letter-spacing:0.5px; background:transparent;")

        if home:
            n.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addStretch(1)
            row.addWidget(n)
            row.addWidget(flag)
        else:
            n.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(flag)
            row.addWidget(n)
            row.addStretch(1)
        return w

    def _swap(self, attr: str, new: QWidget, stretch: int) -> None:
        old = getattr(self, attr)
        lay = old.parentWidget().layout()
        idx = lay.indexOf(old)
        lay.takeAt(idx)
        old.deleteLater()
        lay.insertWidget(idx, new, stretch)
        setattr(self, attr, new)

    def _empty(self) -> None:
        self._badge.hide()
        self._stage.setText("暂无焦点比赛")
        self._clock.setText("")
        self._big.setText("—")
        self._status_txt.setText("")
        self._meta.setText("赛事数据加载中…")
        self._action.setText("查看赛程")

    def set_match(self, match: Match | None) -> None:
        self._match = match
        if match is None:
            self._empty()
            return

        self._swap("_home_block", self._team_block(match.team_a_name, home=True), 1)
        self._swap("_away_block", self._team_block(match.team_b_name, home=False), 1)

        is_live = match.is_live
        self._badge.setVisible(is_live)
        self._big.setText(match.display_score)

        if is_live:
            minute = (match.minute or "").strip()
            self._clock.setText(f"⏱  {minute}'" if minute else "⏱  进行中")
            self._status_txt.setStyleSheet(
                f"color:{C_LIVE}; font-size:11px; font-weight:800; background:transparent;")
            self._status_txt.setText("进行中")
            self._action.setText("查看比赛详情")
        elif match.status == MatchStatus.PLAYED:
            self._clock.setText("已结束")
            self._clock.setStyleSheet(
                f"color:{C_FAINT}; font-size:13px; font-weight:800; background:transparent;")
            self._status_txt.setStyleSheet(
                f"color:{C_GREEN}; font-size:11px; font-weight:800; background:transparent;")
            self._status_txt.setText("全场结束")
            self._action.setText("查看比赛详情")
        else:
            self._clock.setText("即将开赛")
            self._clock.setStyleSheet(
                f"color:{C_PRIMARY}; font-size:13px; font-weight:800; background:transparent;")
            self._status_txt.setStyleSheet(
                f"color:{C_PRIMARY}; font-size:11px; font-weight:800; background:transparent;")
            self._status_txt.setText("VS")
            self._action.setText("查看赛前预测")

        self._stage.setText(getattr(match, "_stage_name", "") or "世界杯")
        ls = match.local_start
        if ls is not None:
            self._meta.setText(ls.strftime("%m月%d日  %H:%M  开球"))
        else:
            self._meta.setText(match.status.label)


# ════════════════════════════════════════════════════════════
#  小组积分榜（A-L 动态切换）
# ════════════════════════════════════════════════════════════
class GroupStandingsPanel(Card):
    def __init__(self, *, on_team=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self._on_team = on_team
        self._groups: list[GroupStanding] = []
        self._tab_btns: dict[str, QPushButton] = {}
        self._active: str | None = None
        self.setMinimumWidth(360)
        self.setMinimumHeight(330)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)
        root.addWidget(_panel_title("小组积分榜", "GROUP STANDINGS", C_PRIMARY))

        self._tabs = QHBoxLayout()
        self._tabs.setSpacing(4)
        root.addLayout(self._tabs)

        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        for txt, w, al in (("# 球队", 0, Qt.AlignmentFlag.AlignLeft),
                           ("场", 30, Qt.AlignmentFlag.AlignCenter),
                           ("净", 38, Qt.AlignmentFlag.AlignCenter),
                           ("积", 36, Qt.AlignmentFlag.AlignCenter)):
            l = QLabel(txt)
            l.setStyleSheet(f"color:{C_FAINT}; font-size:10.5px; font-weight:800; background:transparent;")
            if w:
                l.setFixedWidth(w)
                l.setAlignment(al)
            header.addWidget(l, 0 if w else 1)
        root.addLayout(header)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(255,255,255,0.08);")
        root.addWidget(line)

        self._rows_box = QVBoxLayout()
        self._rows_box.setSpacing(2)
        root.addLayout(self._rows_box)
        root.addStretch(1)

    def set_groups(self, groups: list[GroupStanding]) -> None:
        self._groups = [g for g in groups if g.teams]
        # 重建标签
        _clear_layout(self._tabs)
        self._tab_btns.clear()
        for g in self._groups:
            letter = (g.name or "?")[0]
            b = QPushButton(letter)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(30)
            # 横向均分铺满整行（顶满格）—— 等宽分段按钮，告别小方块
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.clicked.connect(lambda _c=False, key=g.name: self._select(key))
            self._tab_btns[g.name] = b
            self._tabs.addWidget(b)

        if not self._groups:
            _clear_layout(self._rows_box)
            empty = QLabel("暂无积分榜数据")
            empty.setStyleSheet(f"color:{C_FAINT}; padding:24px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rows_box.addWidget(empty)
            return
        target = self._active if self._active in self._tab_btns else self._groups[0].name
        self._select(target)

    def _select(self, group_name: str) -> None:
        self._active = group_name
        for name, b in self._tab_btns.items():
            active = name == group_name
            b.setStyleSheet(
                "QPushButton{border-radius:8px; font-size:13px; font-weight:900;"
                " padding:0 2px;"
                + (f" background:{C_PRIMARY}; color:#fff; border:none;"
                   if active else
                   " background: rgba(255,255,255,0.05); color:#B0BEC5;"
                   " border:1px solid rgba(255,255,255,0.10);")
                + "}"
                "QPushButton:hover{"
                + ("" if active else " background: rgba(255,255,255,0.10); color:#fff;")
                + "}")
            b.setChecked(active)
        grp = next((g for g in self._groups if g.name == group_name), None)
        _clear_layout(self._rows_box)
        if grp is None:
            return
        for ts in sorted(grp.teams, key=lambda t: t.rank):
            self._rows_box.addWidget(self._row(ts))

    def _row(self, ts: TeamStanding) -> QWidget:
        qual = ts.rank <= 2
        accent = C_GREEN if qual else "rgba(255,255,255,0.10)"
        w = _ClickRow(height=40)
        w.setStyleSheet(
            f"QFrame#ClickRow{{background: rgba(255,255,255,0.03); border-radius:9px;"
            f" border-left:3px solid {accent};}}"
            "QFrame#ClickRow:hover{background: rgba(255,255,255,0.08);}")
        if self._on_team and ts.team_id:
            w.clicked.connect(lambda tid=ts.team_id: self._on_team(tid))
        row = QHBoxLayout(w)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(8)
        rk = QLabel(str(ts.rank))
        rk.setFixedWidth(16)
        rk.setStyleSheet(
            f"color:{C_GREEN if qual else C_FAINT}; font-size:13px; font-weight:900;"
            " background:transparent;")
        row.addWidget(rk)
        row.addWidget(FlagIcon(ts.team_name, height=18, radius=3))
        nm = QLabel(ts.team_name)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        row.addWidget(nm, 1)
        gd = ts.goal_diff
        for val, w_, color in ((str(ts.matches_total), 30, C_DIM),
                               (f"+{gd}" if gd > 0 else str(gd), 38, C_DIM),
                               (str(ts.points), 36, C_GOLD)):
            l = QLabel(val)
            l.setFixedWidth(w_)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weight = 900 if color == C_GOLD else 700
            l.setStyleSheet(
                f"color:{color}; font-size:12.5px; font-weight:{weight}; background:transparent;")
            row.addWidget(l)
        return w


# ════════════════════════════════════════════════════════════
#  赛事大盘统计卡
# ════════════════════════════════════════════════════════════
class StatCard(Card):
    def __init__(self, title: str, en: str, value: str, sub: str, color: str,
                 chart: QWidget | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=color)
        self.setMinimumHeight(118)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        col = QVBoxLayout(self)
        col.setContentsMargins(16, 14, 16, 12)
        col.setSpacing(4)

        top = QHBoxLayout()
        t = QLabel(title)
        t.setStyleSheet(f"color:{C_DIM}; font-size:12px; font-weight:800; background:transparent;")
        top.addWidget(t)
        top.addStretch(1)
        if chart is not None:
            top.addWidget(chart, alignment=Qt.AlignmentFlag.AlignRight)
        col.addLayout(top)

        v = QLabel(value)
        v.setStyleSheet(f"color:{color}; font-size:30px; font-weight:900; background:transparent;")
        col.addWidget(v)

        s = QLabel(sub)
        s.setWordWrap(True)
        s.setStyleSheet(f"color:{C_FAINT}; font-size:10.5px; font-weight:600; background:transparent;")
        col.addWidget(s)

        col.addStretch(1)
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {color},"
            " stop:1 rgba(255,255,255,0.0)); border-radius:2px;")
        col.addWidget(bar)


# ════════════════════════════════════════════════════════════
#  今日赛程
# ════════════════════════════════════════════════════════════
class TodaySchedulePanel(Card):
    def __init__(self, *, on_match=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self._on_match = on_match
        self.setMinimumHeight(280)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(20, 16, 20, 16)
        self._root.setSpacing(10)
        self._title = _panel_title("今日赛程", "TODAY", C_PRIMARY, "0 场")
        self._root.addWidget(self._title)
        self._rows = QVBoxLayout()
        self._rows.setSpacing(8)
        self._root.addLayout(self._rows)
        self._root.addStretch(1)

    def set_matches(self, matches: list[Match]) -> None:
        _clear_layout(self._rows)
        hint = self.findChild(QLabel, "PanelHint")
        if hint:
            hint.setText(f"{len(matches)} 场")
        if not matches:
            empty = QLabel("今日暂无赛事 ⚽")
            empty.setStyleSheet(f"color:{C_FAINT}; padding:18px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rows.addWidget(empty)
            return
        for m in matches[:4]:
            self._rows.addWidget(self._match_row(m))

    def _match_row(self, m: Match) -> QWidget:
        w = _ClickRow(height=56, radius=11)
        if self._on_match:
            w.clicked.connect(lambda mm=m: self._on_match(mm))
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(8)
        t = QLabel(fmt_time(m.start_play))
        t.setFixedWidth(42)
        t.setStyleSheet(f"color:{C_DIM}; font-size:12px; font-weight:800; background:transparent;")
        row.addWidget(t)

        row.addWidget(FlagIcon(m.team_a_name, height=18, radius=3))
        h = QLabel(m.team_a_name)
        h.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:700; background:transparent;")
        row.addWidget(h, 1)

        if m.status in (MatchStatus.FIXTURE, MatchStatus.UNKNOWN):
            mid = QLabel("VS")
            mid.setStyleSheet(f"color:{C_FAINT}; font-size:11px; font-weight:800; background:transparent;")
        else:
            mid = QLabel(m.display_score)
            color = C_LIVE if m.is_live else C_TEXT
            mid.setStyleSheet(f"color:{color}; font-size:14px; font-weight:900; background:transparent;")
        mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mid.setFixedWidth(54)
        row.addWidget(mid)

        a = QLabel(m.team_b_name)
        a.setAlignment(Qt.AlignmentFlag.AlignRight)
        a.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:700; background:transparent;")
        row.addWidget(a, 1)
        row.addWidget(FlagIcon(m.team_b_name, height=18, radius=3))

        if m.is_live:
            row.addWidget(_chip("LIVE", C_LIVE, font_px=9))
        elif m.status == MatchStatus.PLAYED:
            row.addWidget(_chip("完场", C_GREEN, solid=False, font_px=9))
        else:
            row.addWidget(_chip("未开始", C_FAINT, solid=False, font_px=9))
        return w


# ════════════════════════════════════════════════════════════
#  攻防雷达分析
# ════════════════════════════════════════════════════════════
class RadarPanel(Card):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PURPLE)
        self.setMinimumHeight(280)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 12)
        col.setSpacing(8)
        col.addWidget(_panel_title("攻防数据分析", "MATCH ANALYSIS", C_PURPLE))
        self._radar = DualRadarChart()
        col.addWidget(self._radar, 1)
        self._legend = QHBoxLayout()
        col.addLayout(self._legend)

    @staticmethod
    def _radar_vector(ts: TeamStanding | None) -> list[int]:
        if ts is None or ts.matches_total == 0:
            return [50, 50, 50, 50, 50]
        m = ts.matches_total
        gfpm = ts.goals_pro / m
        gapm = ts.goals_against / m
        ppm = ts.points / m
        winr = ts.matches_won / m
        gdp = ts.goal_diff / m
        return [
            _clamp(gfpm / 2.5 * 99),                    # 进攻
            _clamp((1 - min(1.0, gapm / 2.5)) * 99),    # 防守
            _clamp(ppm / 3.0 * 99),                     # 积分
            _clamp(winr * 99),                          # 胜率
            _clamp((gdp + 2.5) / 5.0 * 99),             # 净胜
        ]

    def set_teams(self, name_a: str, vec_a: list[int],
                  name_b: str, vec_b: list[int]) -> None:
        self._radar.set_data(
            dims=[("进攻", "ATK"), ("防守", "DEF"), ("积分", "PTS"),
                  ("胜率", "WIN"), ("净胜", "GD")],
            series=[(name_a, vec_a, C_PRIMARY), (name_b, vec_b, C_GREEN)],
        )
        _clear_layout(self._legend)
        self._legend.addStretch(1)
        self._legend.addWidget(self._dot(C_PRIMARY, name_a))
        self._legend.addSpacing(16)
        self._legend.addWidget(self._dot(C_GREEN, name_b))
        self._legend.addStretch(1)

    def _dot(self, color: str, name: str) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background:{color}; border-radius:5px;")
        row.addWidget(dot)
        l = QLabel(name)
        l.setStyleSheet(f"color:{C_DIM}; font-size:11px; font-weight:700; background:transparent;")
        row.addWidget(l)
        return w


# ════════════════════════════════════════════════════════════
#  射手榜
# ════════════════════════════════════════════════════════════
class TopScorersPanel(Card):
    def __init__(self, *, on_player=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_GOLD)
        self._on_player = on_player
        self.setMinimumHeight(280)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(20, 16, 20, 16)
        self._root.setSpacing(6)
        self._root.addWidget(_panel_title("射手榜", "TOP SCORERS", C_GOLD))
        self._rows = QVBoxLayout()
        self._rows.setSpacing(4)
        self._root.addLayout(self._rows)
        self._root.addStretch(1)

    @staticmethod
    def _rank_color(r: int) -> str:
        return {1: C_GOLD, 2: "#CBD5E1", 3: "#FF9D5C"}.get(r, C_FAINT)

    def set_scorers(self, scorers: list[PlayerRanking]) -> None:
        _clear_layout(self._rows)
        if not scorers:
            empty = QLabel("暂无射手榜数据")
            empty.setStyleSheet(f"color:{C_FAINT}; padding:18px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rows.addWidget(empty)
            return
        for p in scorers[:5]:
            self._rows.addWidget(self._row(p))

    def _row(self, p: PlayerRanking) -> QWidget:
        w = _ClickRow(height=40)
        if self._on_player and p.person_id:
            w.clicked.connect(lambda pp=p: self._on_player(pp.person_id, pp.person_name))
        row = QHBoxLayout(w)
        row.setContentsMargins(10, 0, 12, 0)
        row.setSpacing(9)
        rk = QLabel(str(p.rank))
        rk.setFixedWidth(16)
        rk.setStyleSheet(
            f"color:{self._rank_color(p.rank)}; font-size:14px; font-weight:900;"
            " background:transparent;")
        row.addWidget(rk)
        row.addWidget(FlagIcon(p.team_name, height=18, radius=3))
        nm = QLabel(p.person_name)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        row.addWidget(nm, 1)
        g = QLabel(f"{p.count} 球")
        g.setStyleSheet(f"color:{C_PRIMARY}; font-size:13px; font-weight:900; background:transparent;")
        row.addWidget(g)
        return w


# ════════════════════════════════════════════════════════════
#  夺冠热门（模型推算）
# ════════════════════════════════════════════════════════════
class FavoritesPanel(Card):
    def __init__(self, *, on_team=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_GOLD)
        self._on_team = on_team
        self.setMinimumHeight(270)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(20, 16, 20, 16)
        self._root.setSpacing(10)
        self._root.addWidget(_panel_title("夺冠热门", "CHAMPIONS", C_GOLD, "模型推算"))
        self._rows = QVBoxLayout()
        self._rows.setSpacing(8)
        self._root.addLayout(self._rows)
        self._root.addStretch(1)

    def set_favorites(self, favs: list[tuple[str, str, float]]) -> None:
        """favs: [(team_name, team_id, probability 0~1), ...]（已按概率降序）。"""
        _clear_layout(self._rows)
        if not favs:
            empty = QLabel("暂无预测数据")
            empty.setStyleSheet(f"color:{C_FAINT}; padding:18px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rows.addWidget(empty)
            return
        peak = max(p for _, _, p in favs) or 1.0
        for name, tid, prob in favs:
            self._rows.addWidget(self._row(name, tid, prob, prob / peak))

    def _row(self, name: str, team_id: str, prob: float, frac: float) -> QWidget:
        w = QWidget()
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(FlagIcon(name, height=18, radius=3))
        nm = QLabel(name)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        if self._on_team and team_id:
            nm.setCursor(Qt.CursorShape.PointingHandCursor)
        head.addWidget(nm, 1)
        val = QLabel(f"{prob * 100:.1f}%")
        val.setStyleSheet(f"color:{C_GOLD}; font-size:13px; font-weight:900; background:transparent;")
        head.addWidget(val)
        col.addLayout(head)
        col.addWidget(_ProgressBar(frac))
        return w


class _ProgressBar(QWidget):
    def __init__(self, frac: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(7)
        self._frac = max(0.04, min(1.0, frac))

    def paintEvent(self, _ev):
        from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        track = QPainterPath()
        track.addRoundedRect(r, 3.5, 3.5)
        p.fillPath(track, QColor(255, 255, 255, 26))
        fill = QPainterPath()
        fill.addRoundedRect(QRectF(0, 0, r.width() * self._frac, r.height()), 3.5, 3.5)
        grad = QLinearGradient(0, 0, r.width(), 0)
        grad.setColorAt(0.0, QColor(C_GOLD))
        grad.setColorAt(1.0, QColor("#FF9D2E"))
        p.fillPath(fill, grad)


# ════════════════════════════════════════════════════════════
#  赛事新闻
# ════════════════════════════════════════════════════════════
class NewsPanel(Card):
    def __init__(self, *, on_open=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self._on_open = on_open
        self.setMinimumHeight(270)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(20, 16, 20, 16)
        self._root.setSpacing(8)
        self._root.addWidget(_panel_title("赛事新闻", "TOURNAMENT NEWS", C_PRIMARY, "懂球帝"))
        self._rows = QVBoxLayout()
        self._rows.setSpacing(8)
        self._root.addLayout(self._rows)
        self._root.addStretch(1)

    def set_news(self, articles: list[NewsArticle]) -> None:
        _clear_layout(self._rows)
        if not articles:
            empty = QLabel("暂无资讯")
            empty.setStyleSheet(f"color:{C_FAINT}; padding:18px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._rows.addWidget(empty)
            return
        for a in articles[:4]:
            self._rows.addWidget(self._row(a))

    def _row(self, a: NewsArticle) -> QWidget:
        w = _ClickRow(height=52, radius=10)
        if self._on_open is not None:
            w.clicked.connect(lambda art=a: self._on_open(art))
        elif a.url:
            w.clicked.connect(lambda url=a.url: QDesktopServices.openUrl(QUrl(url)))
        row = QHBoxLayout(w)
        row.setContentsMargins(10, 6, 12, 6)
        row.setSpacing(10)
        thumb = RemoteImage(size=40, shape="round", radius=8,
                            placeholder_color="#1d2436")
        thumb.setFixedSize(44, 40)
        if a.thumb:
            thumb.set_url(a.thumb)
        row.addWidget(thumb)
        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel(a.title)
        ttl.setStyleSheet(f"color:{C_TEXT}; font-size:11.5px; font-weight:700; background:transparent;")
        ttl.setWordWrap(True)
        col.addWidget(ttl)
        tl = QLabel(a.time_text)
        tl.setStyleSheet(f"color:{C_FAINT}; font-size:9.5px; background:transparent;")
        col.addWidget(tl)
        row.addLayout(col, 1)
        return w


# ════════════════════════════════════════════════════════════
#  快速操作
# ════════════════════════════════════════════════════════════
_QUICK = [
    ("📅", "赛程中心", "schedule", C_PRIMARY),
    ("🛡", "球队", "teams", C_PURPLE),
    ("📈", "数据分析", "standings", C_GREEN),
    ("🔮", "预测中心", "prediction", C_GOLD),
    ("⭐", "收藏夹", "favorites", C_LIVE),
    ("📰", "新闻资讯", "stadiums", "#36D1FF"),
]


class QuickActionsPanel(Card):
    def __init__(self, *, on_navigate=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PURPLE)
        self._on_navigate = on_navigate
        self.setMinimumHeight(270)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)
        col.addWidget(_panel_title("快速操作", "QUICK ACTIONS", C_PURPLE))
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (icon, label, key, color) in enumerate(_QUICK):
            grid.addWidget(self._btn(icon, label, key, color), i // 2, i % 2)
        col.addLayout(grid)
        col.addStretch(1)

    def _btn(self, icon: str, label: str, key: str, color: str) -> QWidget:
        w = _ClickRow(height=64, radius=13)
        w.setStyleSheet(
            "QFrame#ClickRow{background: rgba(255,255,255,0.04); border-radius:13px;"
            f" border:1px solid rgba({_rgb(color)},0.22);}}"
            f"QFrame#ClickRow:hover{{background: rgba({_rgb(color)},0.14);"
            f" border:1px solid {color};}}")
        if self._on_navigate:
            w.clicked.connect(lambda k=key: self._on_navigate(k))
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 0, 10, 0)
        row.setSpacing(10)
        badge = QLabel(icon)
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"font-size:17px; border-radius:11px; background: rgba({_rgb(color)},0.18);"
            f" border:1px solid rgba({_rgb(color)},0.4);")
        row.addWidget(badge)
        l = QLabel(label)
        l.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        row.addWidget(l, 1)
        return w


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
        v = QVBoxLayout(body)
        v.setContentsMargins(24, 22, 24, 26)
        v.setSpacing(18)

        v.addLayout(self._welcome_bar())

        # 第 1 排
        self._live = LiveMatchPanel(
            on_open=self.match_clicked.emit,
            on_predict=self.prediction_clicked.emit,
            on_watch=self._open_live_stream,
        )
        self._standings_panel = GroupStandingsPanel(on_team=self.team_clicked.emit)
        row1 = QHBoxLayout()
        row1.setSpacing(18)
        row1.addWidget(self._live, 3)
        row1.addWidget(self._standings_panel, 2)
        v.addLayout(row1)

        # 第 2 排：统计卡（动态填充）
        self._stats_host = QWidget()
        self._stats_layout = QHBoxLayout(self._stats_host)
        self._stats_layout.setContentsMargins(0, 0, 0, 0)
        self._stats_layout.setSpacing(16)
        v.addWidget(self._stats_host)

        # 第 3 排
        self._today = TodaySchedulePanel(on_match=self.match_clicked.emit)
        self._radar = RadarPanel()
        self._scorers = TopScorersPanel(on_player=self.player_clicked.emit)
        row3 = QHBoxLayout()
        row3.setSpacing(18)
        row3.addWidget(self._today, 1)
        row3.addWidget(self._radar, 1)
        row3.addWidget(self._scorers, 1)
        v.addLayout(row3)

        # 第 4 排
        self._favorites = FavoritesPanel(on_team=self.team_clicked.emit)
        self._news = NewsPanel(on_open=self._open_news_comments)
        self._quick = QuickActionsPanel(on_navigate=self.navigate.emit)
        row4 = QHBoxLayout()
        row4.setSpacing(18)
        row4.addWidget(self._favorites, 1)
        row4.addWidget(self._news, 1)
        row4.addWidget(self._quick, 1)
        v.addLayout(row4)

        v.addStretch(1)

        # 占位统计卡（数据到达前）
        self._render_stats(total=0, played=0, goals=0, teams=0, scorer=None)

    # ── 顶部欢迎条 ──────────────────────────
    def _welcome_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        hi = QLabel("2026 美加墨世界杯 · 实时数据总览")
        hi.setStyleSheet(f"color:{C_TEXT}; font-size:22px; font-weight:900; background:transparent;")
        col.addWidget(hi)
        sub = QLabel("OVERVIEW · 数据来源：懂球帝公开接口")
        sub.setStyleSheet(f"color:{C_DIM}; font-size:12.5px; font-weight:600; background:transparent;")
        col.addWidget(sub)
        row.addLayout(col)
        row.addStretch(1)
        self._conn_badge = QLabel("● 数据加载中…")
        self._conn_badge.setStyleSheet(
            f"color:{C_DIM}; font-size:11.5px; font-weight:800;"
            f" background: rgba(255,255,255,0.06); border-radius:11px; padding:6px 14px;")
        row.addWidget(self._conn_badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        return row

    def _set_connected(self, ok: bool) -> None:
        if ok:
            self._conn_badge.setText("● 实时数据已连接")
            self._conn_badge.setStyleSheet(
                f"color:{C_GREEN}; font-size:11.5px; font-weight:800;"
                f" background: rgba({_rgb(C_GREEN)},0.12); border-radius:11px; padding:6px 14px;")
        else:
            self._conn_badge.setText("● 数据获取失败")
            self._conn_badge.setStyleSheet(
                f"color:{C_LIVE}; font-size:11.5px; font-weight:800;"
                f" background: rgba({_rgb(C_LIVE)},0.12); border-radius:11px; padding:6px 14px;")

    # ── 统计卡 ──────────────────────────────
    def _render_stats(self, *, total: int, played: int, goals: int,
                      teams: int, scorer: PlayerRanking | None,
                      recent_goals: list[float] | None = None) -> None:
        _clear_layout(self._stats_layout)
        avg = (goals / played) if played else 0.0
        progress = (played / total * 100) if total else 0.0

        spark = Sparkline(recent_goals or [1, 1, 1, 1, 1], C_PRIMARY)
        spark.setFixedSize(70, 32)
        self._stats_layout.addWidget(
            StatCard("总比赛场次", "TOTAL MATCHES", str(total),
                     f"已结束 {played} 场", C_PRIMARY, chart=spark), 1)

        ball = QLabel("⚽")
        ball.setFixedSize(34, 34)
        ball.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ball.setStyleSheet("font-size:24px; background:transparent;")
        self._stats_layout.addWidget(
            StatCard("总进球数", "TOTAL GOALS", str(goals),
                     f"场均 {avg:.2f} 球", C_GREEN, chart=ball), 1)

        ring = RingProgress(progress, "#36D1FF")
        self._stats_layout.addWidget(
            StatCard("完赛进度", "PROGRESS", f"{progress:.0f}%",
                     f"{played} / {total} 场", "#36D1FF", chart=ring), 1)

        teams_glyph = QLabel("🌍")
        teams_glyph.setFixedSize(34, 34)
        teams_glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        teams_glyph.setStyleSheet("font-size:22px; background:transparent;")
        self._stats_layout.addWidget(
            StatCard("参赛球队", "TEAMS", str(teams),
                     "12 个小组", C_YELLOW, chart=teams_glyph), 1)

        if scorer is not None:
            golden = StatCard("当前金靴", "GOLDEN BOOT", f"{scorer.count}",
                              f"{scorer.person_name} · {scorer.team_name}",
                              C_GOLD,
                              chart=FlagIcon(scorer.team_name, height=26, radius=4))
        else:
            golden = StatCard("当前金靴", "GOLDEN BOOT", "—", "等待数据", C_GOLD)
        self._stats_layout.addWidget(golden, 1)

    # ── 数据加载 ────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            import asyncio
            results = await asyncio.gather(
                self._service.fetch_full_schedule(force=force),
                self._service.fetch_standings(force=force),
                self._service.fetch_ranking(RankingType.GOALS, force=force),
                self._service.fetch_news(force=force),
                return_exceptions=True,
            )
            self._apply(results)
        self.run_async(runner)

    def _apply(self, results) -> None:
        sched, standings, scorers, news = results

        rounds: list[Round] = []
        matches: list[Match] = []
        if isinstance(sched, tuple):
            rounds, matches = sched
        groups: list[GroupStanding] = []
        if isinstance(standings, tuple):
            groups = standings[0]
        scorer_list: list[PlayerRanking] = scorers if isinstance(scorers, list) else []
        news_list: list[NewsArticle] = news if isinstance(news, list) else []

        ok = bool(matches or groups or scorer_list)
        self._set_connected(ok)

        # 是否有正在进行的比赛 —— 驱动侧栏 LIVE 徽章「仅进行中时显示」
        self.live_state_changed.emit(any(m.is_live for m in matches))

        # 标注每场比赛所属阶段名（供焦点比赛展示）
        round_name = {
            str(r.round_id): r.name for r in rounds if r.round_id is not None
        }
        for m in matches:
            try:
                m._stage_name = round_name.get(str(m.round_id), "")
            except Exception:
                pass

        # ── 焦点比赛 ──
        self._live.set_match(self._pick_featured(matches))

        # ── 积分榜 ──
        self._standings_panel.set_groups(groups)

        # ── 今日赛程 ──
        today = sorted(
            (m for m in matches if is_today(m.start_play)),
            key=lambda x: x.start_play or x.team_a_name,
        )
        self._today.set_matches(today)

        # ── 攻防雷达（焦点比赛双方）──
        featured = self._pick_featured(matches)
        lookup = self._team_lookup(groups)
        if featured is not None:
            self._radar.set_teams(
                featured.team_a_name,
                RadarPanel._radar_vector(lookup.get(featured.team_a_id)),
                featured.team_b_name,
                RadarPanel._radar_vector(lookup.get(featured.team_b_id)),
            )
        elif groups and len(groups[0].teams) >= 2:
            a, b = groups[0].teams[0], groups[0].teams[1]
            self._radar.set_teams(
                a.team_name, RadarPanel._radar_vector(a),
                b.team_name, RadarPanel._radar_vector(b),
            )

        # ── 射手榜 ──
        self._scorers.set_scorers(scorer_list)

        # ── 夺冠热门 ──
        self._favorites.set_favorites(self._championship_odds(groups))

        # ── 赛事新闻 ──
        self._news.set_news(news_list)

        # ── 赛事大盘统计 ──
        played = [m for m in matches if m.status == MatchStatus.PLAYED]
        total_goals = 0
        recent: list[float] = []
        for m in sorted(played, key=lambda x: x.start_play.timestamp() if x.start_play else 0.0):
            g = _goals(m)
            if g is not None:
                total_goals += g[0] + g[1]
                recent.append(float(g[0] + g[1]))
        team_count = sum(len(g.teams) for g in groups)
        self._render_stats(
            total=len(matches),
            played=len(played),
            goals=total_goals,
            teams=team_count,
            scorer=scorer_list[0] if scorer_list else None,
            recent_goals=recent[-12:] if len(recent) >= 2 else None,
        )

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

    # ── 观看直播 / 导入 M3U8 源 ──────────────
    def _open_live_stream(self, match: Match | None) -> None:
        """打开应用内播放器观看直播，并支持粘贴/导入 M3U8 等源地址。"""
        from app.ui.widgets.video_player import VideoPlayerDialog
        title = "直播间"
        if match is not None:
            title = f"直播 · {match.team_a_name} vs {match.team_b_name}"
        dlg = VideoPlayerDialog(url="", title=title, parent=self.window())
        dlg.exec()

    def _open_news_comments(self, article: NewsArticle) -> None:
        """打开新闻热评弹窗（球迷热议）。"""
        from app.ui.widgets.comments_dialog import HotCommentsDialog
        dlg = HotCommentsDialog(self._service, article, parent=self.window())
        dlg.exec()

    # ── 兼容 MainWindow 接口 ────────────────
    def apply_palette(self, palette) -> None:  # noqa: D401
        # 概览页采用固定的设计稿配色（深蓝世界杯）。
        return
