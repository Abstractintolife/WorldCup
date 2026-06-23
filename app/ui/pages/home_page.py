"""概览仪表盘（OVERVIEW）—— 对照「想象中的样子」设计稿精准复刻。

布局
-----
* 第一排：实时比赛核心看板（USA 2-1 AUS）  |  小组积分榜（A-H 切换）
* 第二排：赛事大盘 5 张统计卡（场次 / 进球 / 控球 / 黄牌 / 红牌）
* 第三排：今日赛程  |  攻防雷达分析  |  射手榜 TOP5
* 第四排：夺冠热门  |  赛事新闻  |  快速操作

这是一个**静态展示版**仪表盘：所有内容为内置演示数据（演示 / 售卖用），
不依赖实时接口。保留 ``HomePage`` 的对外信号与 ``refresh`` / ``apply_palette``
接口，以兼容 ``MainWindow`` 的既有连接。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
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
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.dashboard_charts import DualRadarChart, RingProgress, Sparkline
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.misc import Card

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
#  演示数据
# ════════════════════════════════════════════════════════════
# 小组积分榜：A-H 各组（队名, 场, 净胜球, 积分）
_GROUPS: dict[str, list[tuple[str, int, int, int]]] = {
    "A组": [("德国", 2, 4, 6), ("瑞士", 2, 2, 4), ("匈牙利", 2, -1, 1), ("苏格兰", 2, -5, 0)],
    "B组": [("美国", 2, 3, 4), ("荷兰", 2, 2, 4), ("澳大利亚", 2, -1, 3), ("摩洛哥", 2, -4, 0)],
    "C组": [("阿根廷", 2, 5, 6), ("墨西哥", 2, 1, 3), ("波兰", 2, -2, 1), ("沙特阿拉伯", 2, -4, 1)],
    "D组": [("法国", 2, 6, 6), ("丹麦", 2, 1, 4), ("突尼斯", 2, -2, 1), ("加拿大", 2, -5, 0)],
    "E组": [("西班牙", 2, 4, 6), ("日本", 2, 2, 4), ("加纳", 2, -2, 1), ("哥斯达黎加", 2, -4, 0)],
    "F组": [("比利时", 2, 3, 4), ("克罗地亚", 2, 2, 4), ("韩国", 2, 0, 3), ("喀麦隆", 2, -5, 0)],
    "G组": [("巴西", 2, 6, 6), ("塞尔维亚", 2, 1, 3), ("瑞士", 2, -1, 3), ("喀麦隆", 2, -6, 0)],
    "H组": [("葡萄牙", 2, 5, 6), ("乌拉圭", 2, 2, 4), ("加纳", 2, -2, 1), ("韩国", 2, -5, 0)],
}

# 今日赛程：(时间, 主队, 客队, 状态, 比分或None)
_TODAY = [
    ("03:00", "美国", "澳大利亚", "live", "2 - 1"),
    ("06:00", "苏格兰", "摩洛哥", "upcoming", None),
    ("08:30", "巴西", "塞尔维亚", "upcoming", None),
]

# 射手榜：(排名, 名字, 国家, 进球)
_SCORERS = [
    (1, "哈里·凯恩", "英格兰", 5),
    (2, "姆巴佩", "法国", 4),
    (3, "梅西", "阿根廷", 3),
    (4, "拉什福德", "英格兰", 3),
    (5, "吉鲁", "法国", 2),
]

# 夺冠热门：(国家, 概率%)
_FAVORITES = [
    ("巴西", 18.7),
    ("法国", 16.3),
    ("英格兰", 13.8),
    ("阿根廷", 12.5),
    ("德国", 9.2),
]

# 赛事新闻：(标签, 标签色, 标题, 时间)
_NEWS = [
    ("战报", C_LIVE, "美国队 2-1 力克澳大利亚，普利西奇梅开二度", "12 分钟前"),
    ("焦点", C_PRIMARY, "姆巴佩梅开二度，法国队 4-1 大胜对手", "1 小时前"),
    ("伤情", C_YELLOW, "德国队核心中场训练中轻伤，出战成疑", "3 小时前"),
    ("数据", C_GREEN, "本届世界杯场均进球 2.57，创近三届新高", "5 小时前"),
]

# 快速操作：(图标, 文案, 颜色)
_QUICK = [
    ("🗓", "赛程日历", C_PRIMARY),
    ("⚔️", "球队对比", C_PURPLE),
    ("📊", "数据统计", C_GREEN),
    ("⭐", "收藏夹", C_GOLD),
    ("🔔", "设置提醒", C_LIVE),
    ("📤", "分享应用", "#36D1FF"),
]


# ════════════════════════════════════════════════════════════
#  小工具：分区标题（卡片内）
# ════════════════════════════════════════════════════════════
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
class LiveMatchPanel(Card):
    def __init__(self, on_watch=None, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_LIVE)
        self._on_watch = on_watch
        self.setMinimumWidth(560)
        self.setMinimumHeight(330)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        # 顶栏：LIVE + 阶段 + 时间
        top = QHBoxLayout()
        top.setSpacing(10)
        self._live_badge = _LiveBadge()
        top.addWidget(self._live_badge)
        stage = QLabel("小组赛 · 第 2 轮 · B组")
        stage.setStyleSheet(f"color:{C_DIM}; font-size:12px; font-weight:700; background:transparent;")
        top.addWidget(stage)
        top.addStretch(1)
        clock = QLabel("⏱  78:36")
        clock.setStyleSheet(
            f"color:{C_LIVE}; font-size:14px; font-weight:900; background:transparent;"
        )
        top.addWidget(clock)
        root.addLayout(top)

        # 比分行
        score = QHBoxLayout()
        score.setSpacing(8)
        score.addWidget(self._team_block("美国", "美国", align_right=False), 1)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        big = QLabel("2 - 1")
        big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        big.setStyleSheet(
            "font-size:46px; font-weight:900; color:#FFFFFF; background:transparent;"
            " letter-spacing:2px;"
        )
        mid.addWidget(big)
        live_txt = QLabel("进行中")
        live_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        live_txt.setStyleSheet(
            f"color:{C_LIVE}; font-size:11px; font-weight:800; background:transparent;"
        )
        mid.addWidget(live_txt)
        mid_w = QWidget()
        mid_w.setLayout(mid)
        mid_w.setFixedWidth(150)
        score.addWidget(mid_w)

        score.addWidget(self._team_block("澳大利亚", "澳大利亚", align_right=True), 1)
        root.addLayout(score)

        # 进球信息
        goals = QHBoxLayout()
        goals.setSpacing(8)
        left_g = QVBoxLayout()
        left_g.setSpacing(3)
        for s in ("⚽ 普利西奇  23'", "⚽ 雷纳  45+2'"):
            l = QLabel(s)
            l.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:600; background:transparent;")
            left_g.addWidget(l)
        left_g.addStretch(1)
        goals.addLayout(left_g, 1)
        right_g = QVBoxLayout()
        right_g.setSpacing(3)
        for s in ("古德温  52' ⚽",):
            l = QLabel(s)
            l.setAlignment(Qt.AlignmentFlag.AlignRight)
            l.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:600; background:transparent;")
            right_g.addWidget(l)
        right_g.addStretch(1)
        goals.addLayout(right_g, 1)
        root.addLayout(goals)

        root.addStretch(1)

        # 观看直播按钮
        watch = QPushButton("▶   观看直播")
        watch.setProperty("primary", True)
        watch.setCursor(Qt.CursorShape.PointingHandCursor)
        watch.setMinimumHeight(42)
        watch.setStyleSheet(
            "QPushButton{background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {C_PRIMARY}, stop:1 #2D8CFF); color:#fff; border:none;"
            " border-radius:13px; font-size:14px; font-weight:800; letter-spacing:1px;}"
            "QPushButton:hover{background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 #46D2FF, stop:1 {C_PRIMARY});}}"
        )
        if self._on_watch:
            watch.clicked.connect(self._on_watch)
        root.addWidget(watch)

        # 场地信息
        venue = QLabel("📍  AT&T Stadium  ·  94,073 人")
        venue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        venue.setStyleSheet(f"color:{C_FAINT}; font-size:11px; font-weight:600; background:transparent;")
        root.addWidget(venue)

    def _team_block(self, name: str, flag_nat: str, *, align_right: bool) -> QWidget:
        w = QWidget()
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(8)
        col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag = FlagIcon(flag_nat, height=46, radius=8)
        col.addWidget(flag, alignment=Qt.AlignmentFlag.AlignCenter)
        n = QLabel(name)
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        n.setStyleSheet(f"color:{C_TEXT}; font-size:16px; font-weight:800; background:transparent;")
        col.addWidget(n)
        return w


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
        import math
        a = 0.55 + 0.45 * (1.0 - math.cos(t * 3.0)) * 0.5
        self.setStyleSheet(
            f"background: rgba({_rgb(C_LIVE)},{a:.2f}); color:#fff; border-radius:9px;"
            " padding:3px 11px; font-size:11px; font-weight:900; letter-spacing:1px;"
        )


# ════════════════════════════════════════════════════════════
#  小组积分榜
# ════════════════════════════════════════════════════════════
class GroupStandingsPanel(Card):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self.setMinimumWidth(360)
        self.setMinimumHeight(330)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)
        root.addWidget(_panel_title("小组积分榜", "GROUP STANDINGS", C_PRIMARY))

        # A-H 切换标签
        tabs = QHBoxLayout()
        tabs.setSpacing(5)
        self._tab_btns: dict[str, QPushButton] = {}
        for g in _GROUPS.keys():
            letter = g[0]
            b = QPushButton(letter)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedSize(30, 28)
            b.clicked.connect(lambda _c=False, key=g: self._select(key))
            self._tab_btns[g] = b
            tabs.addWidget(b)
        tabs.addStretch(1)
        root.addLayout(tabs)

        # 表头
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        for txt, w, al in (("# 球队", 0, Qt.AlignmentFlag.AlignLeft),
                           ("场", 34, Qt.AlignmentFlag.AlignCenter),
                           ("净", 40, Qt.AlignmentFlag.AlignCenter),
                           ("积", 40, Qt.AlignmentFlag.AlignCenter)):
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

        self._select("A组")

    def _select(self, group: str) -> None:
        for g, b in self._tab_btns.items():
            active = g == group
            b.setChecked(active)
            b.setStyleSheet(
                ("QPushButton{border-radius:8px; font-size:12px; font-weight:800;"
                 + (f" background:{C_PRIMARY}; color:#fff; border:none;"
                    if active else
                    " background: rgba(255,255,255,0.05); color:#B0BEC5;"
                    " border:1px solid rgba(255,255,255,0.10);")
                 + "}")
            )
        # 重填行
        while self._rows_box.count():
            it = self._rows_box.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i, (team, played, gd, pts) in enumerate(_GROUPS[group], start=1):
            self._rows_box.addWidget(self._row(i, team, played, gd, pts))

    def _row(self, rank: int, team: str, played: int, gd: int, pts: int) -> QWidget:
        w = QFrame()
        w.setObjectName("StRow")
        w.setFixedHeight(40)
        qual = rank <= 2  # 前两名出线（绿色）
        w.setStyleSheet(
            "QFrame#StRow{background: rgba(255,255,255,0.03); border-radius:9px;"
            f" border-left:3px solid {C_GREEN if qual else 'rgba(255,255,255,0.10)'};}}"
            "QFrame#StRow:hover{background: rgba(255,255,255,0.07);}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(8)
        rk = QLabel(str(rank))
        rk.setFixedWidth(16)
        rk.setStyleSheet(
            f"color:{C_GREEN if qual else C_FAINT}; font-size:13px; font-weight:900;"
            " background:transparent;"
        )
        row.addWidget(rk)
        row.addWidget(FlagIcon(team, height=18, radius=3))
        nm = QLabel(team)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        row.addWidget(nm, 1)
        for val, w_, color in ((str(played), 34, C_DIM),
                               (f"+{gd}" if gd > 0 else str(gd), 40, C_DIM),
                               (str(pts), 40, C_GOLD)):
            l = QLabel(val)
            l.setFixedWidth(w_)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weight = 900 if color == C_GOLD else 700
            l.setStyleSheet(
                f"color:{color}; font-size:12.5px; font-weight:{weight}; background:transparent;"
            )
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
        s.setStyleSheet(f"color:{C_FAINT}; font-size:10.5px; font-weight:600; background:transparent;")
        col.addWidget(s)

        col.addStretch(1)
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {color},"
            " stop:1 rgba(255,255,255,0.0)); border-radius:2px;"
        )
        col.addWidget(bar)


class _CardGlyph(QLabel):
    """黄牌 / 红牌发光小卡牌图标。"""

    def __init__(self, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(26, 34)
        self.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 {color}, stop:1 rgba({_rgb(color)},0.7));"
            f" border-radius:5px; border:1px solid rgba(255,255,255,0.3);"
        )


# ════════════════════════════════════════════════════════════
#  今日赛程
# ════════════════════════════════════════════════════════════
class TodaySchedulePanel(Card):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self.setMinimumHeight(280)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)
        col.addWidget(_panel_title("今日赛程", "TODAY", C_PRIMARY, "3 场"))
        for tm, home, away, status, score in _TODAY:
            col.addWidget(self._match_row(tm, home, away, status, score))
        col.addStretch(1)

    def _match_row(self, tm, home, away, status, score) -> QWidget:
        w = QFrame()
        w.setObjectName("SchRow")
        w.setFixedHeight(56)
        w.setStyleSheet(
            "QFrame#SchRow{background: rgba(255,255,255,0.03); border-radius:11px;}"
            "QFrame#SchRow:hover{background: rgba(255,255,255,0.07);}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(8)
        t = QLabel(tm)
        t.setFixedWidth(42)
        t.setStyleSheet(f"color:{C_DIM}; font-size:12px; font-weight:800; background:transparent;")
        row.addWidget(t)

        # 主队
        row.addWidget(FlagIcon(home, height=18, radius=3))
        h = QLabel(home)
        h.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:700; background:transparent;")
        row.addWidget(h, 1)

        # 中间比分 / VS
        if score:
            mid = QLabel(score)
            mid.setStyleSheet(f"color:{C_LIVE}; font-size:14px; font-weight:900; background:transparent;")
        else:
            mid = QLabel("VS")
            mid.setStyleSheet(f"color:{C_FAINT}; font-size:11px; font-weight:800; background:transparent;")
        mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mid.setFixedWidth(48)
        row.addWidget(mid)

        # 客队
        a = QLabel(away)
        a.setAlignment(Qt.AlignmentFlag.AlignRight)
        a.setStyleSheet(f"color:{C_TEXT}; font-size:12px; font-weight:700; background:transparent;")
        row.addWidget(a, 1)
        row.addWidget(FlagIcon(away, height=18, radius=3))

        if status == "live":
            row.addWidget(_chip("LIVE", C_LIVE, font_px=9))
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
        col.addWidget(_panel_title("赛事数据分析", "MATCH ANALYSIS", C_PURPLE))

        radar = DualRadarChart()
        radar.set_data(
            dims=[("进攻", "ATK"), ("防守", "DEF"), ("传球", "PAS"),
                  ("射门", "SHO"), ("抢断", "TKL")],
            series=[("美国", [78, 65, 72, 84, 58], C_PRIMARY),
                    ("澳大利亚", [70, 72, 64, 62, 68], C_GREEN)],
        )
        col.addWidget(radar, 1)

        # 图例
        legend = QHBoxLayout()
        legend.addStretch(1)
        legend.addWidget(self._legend_dot(C_PRIMARY, "美国"))
        legend.addSpacing(16)
        legend.addWidget(self._legend_dot(C_GREEN, "澳大利亚"))
        legend.addStretch(1)
        col.addLayout(legend)

    def _legend_dot(self, color: str, name: str) -> QWidget:
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
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_GOLD)
        self.setMinimumHeight(280)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(6)
        col.addWidget(_panel_title("射手榜", "TOP SCORERS", C_GOLD))
        for rank, name, nat, goals in _SCORERS:
            col.addWidget(self._row(rank, name, nat, goals))
        col.addStretch(1)

    @staticmethod
    def _rank_color(r: int) -> str:
        return {1: C_GOLD, 2: "#CBD5E1", 3: "#FF9D5C"}.get(r, C_FAINT)

    def _row(self, rank, name, nat, goals) -> QWidget:
        w = QFrame()
        w.setObjectName("ScRow")
        w.setFixedHeight(40)
        w.setStyleSheet(
            "QFrame#ScRow{background: rgba(255,255,255,0.03); border-radius:9px;}"
            "QFrame#ScRow:hover{background: rgba(255,255,255,0.07);}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(10, 0, 12, 0)
        row.setSpacing(9)
        rk = QLabel(str(rank))
        rk.setFixedWidth(16)
        rk.setStyleSheet(
            f"color:{self._rank_color(rank)}; font-size:14px; font-weight:900;"
            " background:transparent;"
        )
        row.addWidget(rk)
        row.addWidget(FlagIcon(nat, height=18, radius=3))
        nm = QLabel(name)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        row.addWidget(nm, 1)
        g = QLabel(f"{goals} 球")
        g.setStyleSheet(f"color:{C_PRIMARY}; font-size:13px; font-weight:900; background:transparent;")
        row.addWidget(g)
        return w


# ════════════════════════════════════════════════════════════
#  夺冠热门
# ════════════════════════════════════════════════════════════
class FavoritesPanel(Card):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_GOLD)
        self.setMinimumHeight(270)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)
        col.addWidget(_panel_title("夺冠热门", "CHAMPIONS", C_GOLD, "超算预测"))
        peak = max(p for _, p in _FAVORITES) or 1.0
        for nat, pct in _FAVORITES:
            col.addWidget(self._row(nat, pct, pct / peak))
        col.addStretch(1)

    def _row(self, nat: str, pct: float, frac: float) -> QWidget:
        w = QWidget()
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(FlagIcon(nat, height=18, radius=3))
        nm = QLabel(nat)
        nm.setStyleSheet(f"color:{C_TEXT}; font-size:12.5px; font-weight:700; background:transparent;")
        head.addWidget(nm, 1)
        val = QLabel(f"{pct:.1f}%")
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
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        from PyQt6.QtCore import QRectF
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
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PRIMARY)
        self.setMinimumHeight(270)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(8)
        col.addWidget(_panel_title("赛事新闻", "TOURNAMENT NEWS", C_PRIMARY))
        for tag, tag_color, title, tm in _NEWS:
            col.addWidget(self._row(tag, tag_color, title, tm))
        col.addStretch(1)

    def _row(self, tag, tag_color, title, tm) -> QWidget:
        w = QFrame()
        w.setObjectName("NwRow")
        w.setFixedHeight(50)
        w.setStyleSheet(
            "QFrame#NwRow{background: rgba(255,255,255,0.03); border-radius:10px;}"
            "QFrame#NwRow:hover{background: rgba(255,255,255,0.07);}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(10, 6, 12, 6)
        row.setSpacing(10)
        # 缩略图（渐变块）
        thumb = QLabel()
        thumb.setFixedSize(40, 38)
        thumb.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 {tag_color}, stop:1 rgba({_rgb(tag_color)},0.5)); border-radius:8px;"
        )
        row.addWidget(thumb)
        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel(title)
        ttl.setStyleSheet(f"color:{C_TEXT}; font-size:11.5px; font-weight:700; background:transparent;")
        ttl.setWordWrap(True)
        col.addWidget(ttl)
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.addWidget(_chip(tag, tag_color, solid=False, font_px=8))
        tl = QLabel(tm)
        tl.setStyleSheet(f"color:{C_FAINT}; font-size:9.5px; background:transparent;")
        meta.addWidget(tl)
        meta.addStretch(1)
        mw = QWidget(); mw.setLayout(meta)
        col.addWidget(mw)
        row.addLayout(col, 1)
        return w


# ════════════════════════════════════════════════════════════
#  快速操作
# ════════════════════════════════════════════════════════════
class QuickActionsPanel(Card):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=0, glow_color=C_PURPLE)
        self.setMinimumHeight(270)
        col = QVBoxLayout(self)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)
        col.addWidget(_panel_title("快速操作", "QUICK ACTIONS", C_PURPLE))
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (icon, label, color) in enumerate(_QUICK):
            grid.addWidget(self._btn(icon, label, color), i // 2, i % 2)
        col.addLayout(grid)
        col.addStretch(1)

    def _btn(self, icon: str, label: str, color: str) -> QWidget:
        w = QFrame()
        w.setObjectName("QaBtn")
        w.setFixedHeight(64)
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        w.setStyleSheet(
            "QFrame#QaBtn{background: rgba(255,255,255,0.04); border-radius:13px;"
            f" border:1px solid rgba({_rgb(color)},0.22);}}"
            f"QFrame#QaBtn:hover{{background: rgba({_rgb(color)},0.14);"
            f" border:1px solid {color};}}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 0, 10, 0)
        row.setSpacing(10)
        badge = QLabel(icon)
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"font-size:17px; border-radius:11px; background: rgba({_rgb(color)},0.18);"
            f" border:1px solid rgba({_rgb(color)},0.4);"
        )
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

    # 兼容 MainWindow 的既有连接（静态页一般不发射）
    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    player_clicked = pyqtSignal(str, str)
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
        v = QVBoxLayout(body)
        v.setContentsMargins(24, 22, 24, 26)
        v.setSpacing(18)

        # 顶部欢迎条
        v.addLayout(self._welcome_bar())

        # 第 1 排：实时比赛 | 积分榜
        row1 = QHBoxLayout()
        row1.setSpacing(18)
        row1.addWidget(LiveMatchPanel(on_watch=self._noop), 3)
        row1.addWidget(GroupStandingsPanel(), 2)
        v.addLayout(row1)

        # 第 2 排：5 张统计卡
        v.addLayout(self._stats_row())

        # 第 3 排：今日赛程 | 雷达 | 射手榜
        row3 = QHBoxLayout()
        row3.setSpacing(18)
        row3.addWidget(TodaySchedulePanel(), 1)
        row3.addWidget(RadarPanel(), 1)
        row3.addWidget(TopScorersPanel(), 1)
        v.addLayout(row3)

        # 第 4 排：夺冠热门 | 新闻 | 快速操作
        row4 = QHBoxLayout()
        row4.setSpacing(18)
        row4.addWidget(FavoritesPanel(), 1)
        row4.addWidget(NewsPanel(), 1)
        row4.addWidget(QuickActionsPanel(), 1)
        v.addLayout(row4)

        v.addStretch(1)

    # ── 顶部欢迎条 ──────────────────────────
    def _welcome_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        hi = QLabel("欢迎回来，WorldCup Fan 👋")
        hi.setStyleSheet(f"color:{C_TEXT}; font-size:22px; font-weight:900; background:transparent;")
        col.addWidget(hi)
        sub = QLabel("2026 美加墨世界杯 · 实时数据总览")
        sub.setStyleSheet(f"color:{C_DIM}; font-size:12.5px; font-weight:600; background:transparent;")
        col.addWidget(sub)
        row.addLayout(col)
        row.addStretch(1)
        # 右侧实时小徽章
        live = QLabel("● 实时数据已连接")
        live.setStyleSheet(
            f"color:{C_GREEN}; font-size:11.5px; font-weight:800;"
            f" background: rgba({_rgb(C_GREEN)},0.12); border-radius:11px; padding:6px 14px;"
        )
        row.addWidget(live, alignment=Qt.AlignmentFlag.AlignVCenter)
        return row

    # ── 统计卡排 ────────────────────────────
    def _stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)

        spark = Sparkline([8, 12, 10, 16, 14, 20, 18, 24, 22, 28], C_PRIMARY)
        spark.setFixedSize(70, 32)
        row.addWidget(StatCard("总比赛场次", "TOTAL MATCHES", "104", "已进行 28 场",
                               C_PRIMARY, chart=spark), 1)

        ball = QLabel("⚽")
        ball.setFixedSize(34, 34)
        ball.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ball.setStyleSheet("font-size:24px; background:transparent;")
        row.addWidget(StatCard("总进球数", "TOTAL GOALS", "72", "场均 2.57 球",
                               C_GREEN, chart=ball), 1)

        ring = RingProgress(53.0, C_PRIMARY)
        row.addWidget(StatCard("场均控球率", "POSSESSION", "53%", "本届世界杯新高",
                               "#36D1FF", chart=ring), 1)

        ycard = _CardGlyph(C_YELLOW)
        row.addWidget(StatCard("黄牌总数", "YELLOW CARDS", "48", "场均 1.71 张",
                               C_YELLOW, chart=ycard), 1)

        rcard = _CardGlyph(C_LIVE)
        row.addWidget(StatCard("红牌总数", "RED CARDS", "3", "场均 0.11 张",
                               C_LIVE, chart=rcard), 1)
        return row

    def _noop(self) -> None:
        log.info("观看直播（演示按钮）")

    # ── 兼容 MainWindow 接口 ────────────────
    def apply_palette(self, palette) -> None:  # noqa: D401
        # 概览页采用固定的设计稿配色（深蓝世界杯），不随皮肤大改。
        return

    def refresh(self, force: bool = False) -> None:  # noqa: D401
        # 静态展示页：直接标记内容就绪（隐藏加载遮罩）。
        self.show_content()
