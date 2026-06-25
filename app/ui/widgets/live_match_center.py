"""live_match_center —— 实时比赛中心面板（WorldCup 3.0，任务 12.2）。

对照设计稿 1:1 复刻「实时比赛 / LIVE MATCH」底部面板（继承 :class:`GlassCard`）：

* 头部标题「实时比赛 / LIVE MATCH」。
* 红色「直播中」:class:`LiveBadge`（**呼吸**动画，透明度 1.0→0.7→1.0）+ 实时
  比赛时钟（如「75:24」）。
* 带双方国旗的比分行（如「巴西 2 - 1 塞尔维亚」）。
* 迷你球场之上的事件时间线（样例「23' 维尼修斯」「45' 内马尔」「63' 米特罗维奇」）。
* 底部按钮「进入比赛中心」。

**关键不变量 / 行为**
----------------------
* :class:`LiveBadge` 的透明度由**单一** ``FrameClock`` 心跳驱动（**不**新增任何
  ``QTimer``），并恒落在 ``[0.7, 1.0]``（需求 13.7，设计 Property 18）。呼吸数学
  抽成无 GUI 依赖的纯函数 :func:`breathing_opacity`，便于无头属性测试。
* :meth:`LiveMatchCenter.push_event` —— 每次推送**恰好**新增一行事件
  （需求 13.5，设计 Property 19）。
* 进球（``GOAL``）事件经 :mod:`motion_system` 从顶部**滑入**（180ms / OutCubic，
  需求 13.6）。
* 黄/红牌触发卡片**闪光**；``VAR`` 触发**扫描线**动画。

不修改 ``app/api`` / ``app/models`` / ``app/services``。:class:`MatchEvent` 是本
模块内的轻量展示视图模型（非持久化数据模型）。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from PyQt6.QtCore import QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.models.lineup import MatchLineup
from app.ui.design import motion_system
from app.ui.design.app_cursor import pointing_hand_cursor
from app.ui.design.frame_clock import FrameClock
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.elided_label import ElidedLabel
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.glass_card import GlassCard

# ════════════════════════════════════════════════════════════════════
#  纯函数：LIVE 徽章呼吸透明度（Property 18 / 需求 13.7）
# ════════════════════════════════════════════════════════════════════
#: 呼吸透明度下限 / 上限（恒夹紧在此区间内）。
LIVE_OPACITY_MIN = 0.7
LIVE_OPACITY_MAX = 1.0
#: 一个完整呼吸周期（秒）。
LIVE_BREATH_PERIOD_S = 1.6


def breathing_opacity(
    t: float,
    *,
    period: float = LIVE_BREATH_PERIOD_S,
    lo: float = LIVE_OPACITY_MIN,
    hi: float = LIVE_OPACITY_MAX,
) -> float:
    """纯函数：给定时间 ``t``（秒），返回 LIVE 徽章在 ``t`` 处的呼吸透明度。

    取 ``mid ± amp·cos(2π·t/period)``，其中 ``mid=(lo+hi)/2``、``amp=(hi-lo)/2`` ——
    余弦天然落在 ``[lo, hi]``；再夹紧到 ``[lo, hi]`` 兜底浮点误差，**保证**返回值
    恒在 ``[0.7, 1.0]`` 内（需求 13.7，Property 18）。在 ``t=0`` 取上限 ``hi``，
    随后平滑下探到 ``lo`` 再回升，形成「1.0→0.7→1.0」的呼吸节律（需求 13.7）。
    """
    if period <= 0:
        return hi
    mid = (lo + hi) / 2.0
    amp = (hi - lo) / 2.0
    raw = mid + amp * math.cos(2.0 * math.pi * (t / period))
    if raw < lo:
        return lo
    if raw > hi:
        return hi
    return raw


# ════════════════════════════════════════════════════════════════════
#  事件视图模型
# ════════════════════════════════════════════════════════════════════
EventKind = Literal["GOAL", "YELLOW", "RED", "VAR", "SUB"]
TeamSide = Literal["home", "away"]


@dataclass(frozen=True)
class MatchEvent:
    """单条实时比赛事件（展示用视图模型）。"""

    kind: str            # GOAL / YELLOW / RED / VAR / SUB
    minute: int          # 发生分钟（如 23 → 「23'」）
    team_side: str       # "home" / "away"
    text: str            # 事件文本（如球员名「维尼修斯」）


#: 设计稿样例：巴西 2 - 1 塞尔维亚 + 三条事件（需求 13.3 / 13.4）。
SAMPLE_HOME = "巴西"
SAMPLE_AWAY = "塞尔维亚"
SAMPLE_SCORE = (2, 1)
SAMPLE_CLOCK = "75:24"
SAMPLE_EVENTS: list[MatchEvent] = [
    MatchEvent(kind="GOAL", minute=23, team_side="home", text="维尼修斯"),
    MatchEvent(kind="GOAL", minute=45, team_side="home", text="内马尔"),
    MatchEvent(kind="GOAL", minute=63, team_side="away", text="米特罗维奇"),
]


# ════════════════════════════════════════════════════════════════════
#  LiveBadge —— 红色「直播中」呼吸徽章（FrameClock 驱动）
# ════════════════════════════════════════════════════════════════════
class LiveBadge(QFrame):
    """红色「直播中」胶囊徽章，透明度随 ``FrameClock`` 呼吸（1.0→0.7→1.0）。

    透明度恒落在 ``[0.7, 1.0]``（需求 13.7，Property 18）；由**单一**全局
    ``FrameClock`` 心跳驱动，显示时订阅、隐藏时退订（不新增 ``QTimer``）。
    """

    def __init__(
        self,
        palette: HudPalette = NIGHT_STADIUM,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setObjectName("LiveBadge")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f"QFrame#LiveBadge {{ background: {palette.live};"
            f" border-radius: {Radius.PILL}px; }}"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(11, 4, 12, 4)
        row.setSpacing(6)
        self._dot = QLabel("●")
        self._dot.setStyleSheet(
            "color: #FFFFFF; font-size: 9px; background: transparent;"
        )
        row.addWidget(self._dot)
        self._txt = QLabel("直播中")
        self._txt.setStyleSheet(
            f"color: #FFFFFF; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BLACK}; letter-spacing: 1px; background: transparent;"
        )
        row.addWidget(self._txt)

        # 用图形透明度效果承载「呼吸」（只动 opacity，不动 blurRadius）。
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(LIVE_OPACITY_MAX)
        self.setGraphicsEffect(self._effect)
        self._opacity = LIVE_OPACITY_MAX

        self._clock = FrameClock.instance()

    # ── FrameClock 订阅（显示订阅 / 隐藏退订） ──
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        self._clock.subscribe(self._on_frame)

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        try:
            self._clock.unsubscribe(self._on_frame)
        except Exception:
            pass

    def _on_frame(self, t: float, _dt: float) -> None:
        self._opacity = breathing_opacity(t)
        self._effect.setOpacity(self._opacity)

    @property
    def current_opacity(self) -> float:
        """当前呼吸透明度（恒 ∈ ``[0.7, 1.0]``）。"""
        return self._opacity


# ════════════════════════════════════════════════════════════════════
#  迷你球场（事件时间线宿主）
# ════════════════════════════════════════════════════════════════════
class _MiniPitch(QFrame):
    """绘制一块「迷你球场」（草绿底 + 中线 + 中圈），其上承载事件行布局。"""

    def __init__(self, palette: HudPalette = NIGHT_STADIUM,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._events_box = QVBoxLayout(self)
        self._events_box.setContentsMargins(14, 12, 14, 12)
        self._events_box.setSpacing(6)
        self._events_box.addStretch(1)

        # 空态占位（无进行中比赛时居中显示，覆盖事件区）。
        self._placeholder = QLabel("", self)
        self._placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setWordWrap(True)
        self._placeholder.setStyleSheet(
            f"color: {rgba(palette.text, 0.45)}; font-size: 13px;"
            f" font-weight: {Type.W_MEDIUM}; background: transparent;"
        )
        self._placeholder.hide()

    @property
    def events_box(self) -> QVBoxLayout:
        return self._events_box

    def show_placeholder(self, text: str) -> None:
        """显示居中空态文案（覆盖整块迷你球场）。"""
        self._placeholder.setText(text)
        self._placeholder.setGeometry(self.rect())
        self._placeholder.raise_()
        self._placeholder.show()

    def hide_placeholder(self) -> None:
        self._placeholder.hide()

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._placeholder.setGeometry(self.rect())

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        r = QRectF(1, 1, w - 2, h - 2)

        # 草绿底（极暗，呼应夜场草皮）。
        path = QPainterPath()
        path.addRoundedRect(r, Radius.INNER, Radius.INNER)
        p.fillPath(path, QColor(self._palette.bg_bottom))
        p.setClipPath(path)

        # 中线 + 中圈（淡白）。
        pen = QPen(QColor(255, 255, 255, 26), 1.4)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        cx = w / 2.0
        p.drawLine(int(cx), 2, int(cx), h - 2)
        cr = min(w, h) * 0.16
        p.drawEllipse(QRectF(cx - cr, h / 2.0 - cr, cr * 2, cr * 2))
        p.setClipping(False)

        # 细描边。
        p.setPen(QPen(QColor(self._palette.glass_border), 1))
        p.drawPath(path)


# ════════════════════════════════════════════════════════════════════
#  闪光 / 扫描线叠层
# ════════════════════════════════════════════════════════════════════
class _Overlay(QWidget):
    """覆盖整张卡的透明叠层基类（对鼠标透明，自带不透明度效果）。"""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)
        self.hide()


class _FlashOverlay(_Overlay):
    """黄/红牌闪光叠层：整卡铺一层语义色，不透明度由 0.55 衰减到 0。"""

    def __init__(self, parent: QWidget, palette: HudPalette) -> None:
        super().__init__(parent)
        self._palette = palette
        self._color = QColor(palette.draw)

    def flash(self, color: QColor) -> None:
        self._color = color
        self.raise_()
        self.show()
        self._effect.setOpacity(0.55)
        anim = motion_system.std_anim(self._effect, b"opacity", 0.55, 0.0, duration=380)
        anim.finished.connect(self.hide)
        anim.start()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), Radius.CARD, Radius.CARD)
        col = QColor(self._color)
        col.setAlpha(120)
        p.fillPath(path, col)


class _ScanlineOverlay(_Overlay):
    """VAR 复核扫描线：一条横向高亮线从顶部扫到底部。"""

    def __init__(self, parent: QWidget, palette: HudPalette) -> None:
        super().__init__(parent)
        self._palette = palette
        self._y = 0.0

    def get_scan_y(self) -> float:
        return self._y

    def set_scan_y(self, value: float) -> None:
        self._y = float(value)
        self.update()

    from PyQt6.QtCore import pyqtProperty as _pyqtProperty

    scan_y = _pyqtProperty(float, fget=get_scan_y, fset=set_scan_y)

    def play(self) -> None:
        self.raise_()
        self.show()
        self._effect.setOpacity(0.9)
        anim = motion_system.std_anim(
            self, b"scan_y", 0.0, float(max(1, self.height())), duration=460
        )
        anim.finished.connect(self.hide)
        anim.start()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        col = QColor(self._palette.primary_hi)
        col.setAlpha(150)
        p.setPen(QPen(col, 2))
        p.drawLine(0, int(self._y), w, int(self._y))


# ════════════════════════════════════════════════════════════════════
#  LiveMatchCenter 面板
# ════════════════════════════════════════════════════════════════════
class LiveMatchCenter(GlassCard):
    """实时比赛中心面板（继承 :class:`GlassCard`）。"""

    #: 点击比分行（携带当前 :class:`Match` 或 ``None``）。
    match_clicked = pyqtSignal(object)
    #: 点击底部「进入比赛中心」。
    enter_clicked = pyqtSignal()
    #: 点击布阵图中的球员（person_id, name）。
    player_clicked = pyqtSignal(str, str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        self._match: Match | None = None
        self.setMinimumHeight(300)
        self.setMinimumWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._build_ui()

        # 叠层（闪光 / 扫描线）—— 覆盖整卡，随 resize 同步尺寸。
        self._flash = _FlashOverlay(self, palette)
        self._scanline = _ScanlineOverlay(self, palette)

        # 默认空态：无真实进行中比赛时留空（不展示任何虚构样例比赛）。
        self._render_empty()

    # ── 构建骨架 ─────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        root.addWidget(self._header())
        self._scoreline_w = self._scoreline()
        root.addWidget(self._scoreline_w)

        self._pitch = _MiniPitch(p)
        root.addWidget(self._pitch, 1)
        self._root = root
        # 实时阵容「大头照」布阵图（懒加载，set_lineup 时插入并替换事件迷你球场）。
        self._formation = None

        self._footer_btn = QPushButton("进入比赛中心")
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
        self._footer_btn.clicked.connect(self.enter_clicked.emit)
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
            f" stop:0 {p.live}, stop:1 {rgba(p.live, 0.05)}); border-radius:2px;"
        )
        row.addWidget(bar)

        col = QVBoxLayout()
        col.setSpacing(0)
        zh = QLabel("实时比赛")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("LIVE MATCH")
        en.setStyleSheet(
            f"color: {p.live}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        col.addWidget(en)
        row.addLayout(col)
        row.addStretch(1)

        self._badge = LiveBadge(p)
        row.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._clock_lbl = QLabel(SAMPLE_CLOCK)
        self._clock_lbl.setStyleSheet(
            f"color: {p.live}; font-size: 15px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        row.addWidget(self._clock_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        return w

    def _scoreline(self) -> QWidget:
        p = self._palette
        w = QFrame()
        w.setObjectName("ScoreLine")
        w.setCursor(pointing_hand_cursor())
        w.setStyleSheet(
            f"QFrame#ScoreLine {{ background: {rgba('#FFFFFF', 0.03)};"
            f" border-radius: {Radius.CHIP}px; }}"
            f"QFrame#ScoreLine:hover {{ background: {rgba('#FFFFFF', 0.07)}; }}"
        )
        w.mousePressEvent = (  # type: ignore[assignment]
            lambda _e: self.match_clicked.emit(self._match)
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)

        # 主队（旗 + 名）。
        self._home_flag = FlagIcon(SAMPLE_HOME, height=26, radius=4)
        row.addWidget(self._home_flag)
        self._home_name = ElidedLabel(SAMPLE_HOME, mode=Qt.TextElideMode.ElideRight)
        self._home_name.setStyleSheet(
            f"color: {p.text}; font-size: 14px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        row.addWidget(self._home_name, 1)

        # 比分（大号）。
        self._score_lbl = QLabel(f"{SAMPLE_SCORE[0]} - {SAMPLE_SCORE[1]}")
        self._score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_lbl.setStyleSheet(
            f"color: {p.live}; font-size: 26px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        row.addWidget(self._score_lbl)

        # 客队（名 + 旗）。
        self._away_name = ElidedLabel(SAMPLE_AWAY, mode=Qt.TextElideMode.ElideLeft)
        self._away_name.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._away_name.setStyleSheet(
            f"color: {p.text}; font-size: 14px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        row.addWidget(self._away_name, 1)
        self._away_flag = FlagIcon(SAMPLE_AWAY, height=26, radius=4)
        row.addWidget(self._away_flag)
        return w

    # ── 公共 API ─────────────────────────────
    def set_live(self, match: Match | None) -> None:
        """注入一场真实（理想为进行中）比赛，刷新比分行与时钟。

        事件不随比分自动生成（既有数据层无事件流）；调用方可用
        :meth:`push_event` 逐条推送。``match`` 为 ``None`` 时回退设计稿样例。
        """
        self._match = match
        if match is None:
            self._render_empty()
            return

        # 进入真实比赛态：隐藏空态、恢复比分行。
        self._pitch.hide_placeholder()
        self._scoreline_w.setVisible(True)
        self._set_flag(self._home_flag_slot(), match.team_a_name)
        self._home_name.setText(match.team_a_name)
        self._away_name.setText(match.team_b_name)
        self._set_flag(self._away_flag_slot(), match.team_b_name)

        ga, gb = self._match_goals(match)
        self._score_lbl.setText(f"{ga} - {gb}")
        if match.is_live:
            self._clock_lbl.setText(self._format_live_minute(match))
            self._badge.setVisible(True)
        elif match.status == MatchStatus.PLAYED:
            self._clock_lbl.setText("已结束")
            self._badge.setVisible(False)
        else:
            self._clock_lbl.setText("即将开赛")
            self._badge.setVisible(False)

    @staticmethod
    def _format_live_minute(match: Match) -> str:
        """正在进行的比赛：返回带「分钟符号」的比赛时间，如 ``67'`` / ``45+2'``。

        无具体分钟数据时回退「进行中」。
        """
        minute = (getattr(match, "minute", "") or "").strip().rstrip("'")
        extra = (getattr(match, "minute_extra", "") or "").strip().rstrip("'").lstrip("+")
        if not minute:
            return "进行中"
        if extra and extra not in ("0", ""):
            return f"{minute}+{extra}'"
        return f"{minute}'"

    def push_event(self, ev: MatchEvent) -> QWidget:
        """推送一条事件 —— **恰好**新增一行（需求 13.5，Property 19）。

        进球（``GOAL``）从顶部滑入（需求 13.6）；黄/红牌触发闪光；``VAR`` 触发
        扫描线。返回新建的事件行控件。
        """
        row = self._make_event_row(ev)
        # 插到顶部（stretch 在末尾，所以索引 0 即最上方）。
        self._pitch.events_box.insertWidget(0, row)

        kind = (ev.kind or "").upper()
        if kind == "GOAL":
            self._slide_in_from_top(row)
        elif kind in ("YELLOW", "RED"):
            self._flash_card(kind)
        elif kind == "VAR":
            self._scanline.setGeometry(self.rect())
            self._scanline.play()
        return row

    def set_events(self, events: list[MatchEvent]) -> None:
        """整体重置事件时间线为 ``events``（清空后逐条 :meth:`push_event`）。"""
        self._clear_events()
        for ev in events:
            self.push_event(ev)

    def set_lineup(self, lineup: "MatchLineup | None") -> None:
        """注入实时比赛的双方阵容 → 在球场上以「大头照」布阵图展示。

        有可用阵容（实际首发或赛前预测）时，用 :class:`PortraitLineupPitch`
        替换事件迷你球场；否则移除布阵图、回到事件时间线。
        """
        # 先移除旧布阵图。
        if self._formation is not None:
            self._formation.hide()
            self._formation.setParent(None)
            self._formation.deleteLater()
            self._formation = None

        if lineup is None or not getattr(lineup, "available", False):
            self._pitch.show()
            return

        from app.ui.widgets.portrait_lineup_pitch import PortraitLineupPitch
        self._formation = PortraitLineupPitch(lineup.team_a, lineup.team_b,
                                              color_a=self._palette.loss,
                                              color_b=self._palette.primary_hi)
        self._formation.player_clicked.connect(self.player_clicked.emit)
        idx = self._root.indexOf(self._pitch)
        self._root.insertWidget(idx + 1, self._formation, 1)
        self._pitch.hide()
        self._formation.show()

    @property
    def event_row_count(self) -> int:
        """当前事件行数（不含末尾的伸缩项）。"""
        box = self._pitch.events_box
        count = 0
        for i in range(box.count()):
            if box.itemAt(i).widget() is not None:
                count += 1
        return count

    # ── 内部：渲染样例 ───────────────────────
    def _render_empty(self) -> None:
        """空态：无进行中比赛时留空，仅显示一行居中提示（需求：没有就留空）。"""
        self._match = None
        self.set_lineup(None)
        self._clear_events()
        self._scoreline_w.setVisible(False)
        self._badge.setVisible(False)
        self._clock_lbl.setText("")
        self._pitch.show_placeholder("当前没有正在进行的比赛")

    def _render_sample(self) -> None:
        p = self._palette
        self._pitch.hide_placeholder()
        self._scoreline_w.setVisible(True)
        self._home_name.setText(SAMPLE_HOME)
        self._away_name.setText(SAMPLE_AWAY)
        self._score_lbl.setText(f"{SAMPLE_SCORE[0]} - {SAMPLE_SCORE[1]}")
        self._clock_lbl.setText(SAMPLE_CLOCK)
        self._badge.setVisible(True)
        self._set_flag(self._home_flag_slot(), SAMPLE_HOME)
        self._set_flag(self._away_flag_slot(), SAMPLE_AWAY)
        self._clear_events()
        for ev in SAMPLE_EVENTS:
            row = self._make_event_row(ev)
            self._pitch.events_box.insertWidget(0, row)

    # ── 内部：事件行构建 ─────────────────────
    def _event_color(self, kind: str) -> str:
        p = self._palette
        return {
            "GOAL": p.win,
            "YELLOW": p.draw,
            "RED": p.loss,
            "VAR": p.primary,
            "SUB": p.secondary,
        }.get((kind or "").upper(), p.text_dim)

    def _event_glyph(self, kind: str) -> str:
        return {
            "GOAL": "⚽",
            "YELLOW": "🟨",
            "RED": "🟥",
            "VAR": "📺",
            "SUB": "🔁",
        }.get((kind or "").upper(), "•")

    def _make_event_row(self, ev: MatchEvent) -> QWidget:
        p = self._palette
        color = self._event_color(ev.kind)
        w = QFrame()
        w.setObjectName("EventRow")
        w.setStyleSheet(
            f"QFrame#EventRow {{ background: {rgba('#000000', 0.28)};"
            f" border-radius: {Radius.CHIP}px;"
            f" border-left: 3px solid {color}; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(10, 6, 12, 6)
        row.setSpacing(9)

        minute = QLabel(f"{int(ev.minute)}'")
        minute.setFixedWidth(34)
        minute.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        row.addWidget(minute)

        glyph = QLabel(self._event_glyph(ev.kind))
        glyph.setStyleSheet("font-size: 13px; background: transparent;")
        row.addWidget(glyph)

        text = QLabel(ev.text)
        text.setStyleSheet(
            f"color: {p.text}; font-size: 12.5px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        align = (Qt.AlignmentFlag.AlignRight if (ev.team_side or "") == "away"
                 else Qt.AlignmentFlag.AlignLeft)
        text.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(text, 1)
        return w

    def _clear_events(self) -> None:
        box = self._pitch.events_box
        # 保留末尾伸缩项，仅删除事件行控件。
        for i in reversed(range(box.count())):
            it = box.itemAt(i)
            wdg = it.widget()
            if wdg is not None:
                box.takeAt(i)
                wdg.deleteLater()

    # ── 内部：动效 ───────────────────────────
    def _slide_in_from_top(self, row: QWidget) -> None:
        """进球事件行从顶部滑入（180ms / OutCubic，经 motion_system，需求 13.6）。"""
        row.show()
        rest = QPoint(row.x(), row.y())
        start = QPoint(rest.x(), rest.y() - (row.height() or 28) - 8)
        anim = motion_system.std_anim(row, b"pos", start, rest, duration=180)
        anim.start()

    def _flash_card(self, kind: str) -> None:
        color = QColor(self._palette.draw if kind.upper() == "YELLOW"
                       else self._palette.loss)
        self._flash.setGeometry(self.rect())
        self._flash.flash(color)

    # ── 内部：杂项 ───────────────────────────
    @staticmethod
    def _match_goals(match: Match) -> tuple[int, int]:
        def _i(v) -> int:
            try:
                return int(v) if v not in (None, "") else 0
            except (TypeError, ValueError):
                return 0
        a = _i(match.fs_a if match.fs_a not in (None, "") else match.score_a)
        b = _i(match.fs_b if match.fs_b not in (None, "") else match.score_b)
        return a, b

    def _home_flag_slot(self) -> str:
        return "home"

    def _away_flag_slot(self) -> str:
        return "away"

    def _set_flag(self, slot: str, nationality: str) -> None:
        # FlagIcon 无 set_nationality 链路问题：直接调用其方法刷新旗面。
        flag = self._home_flag if slot == "home" else self._away_flag
        flag.set_nationality(nationality)

    # ── 叠层随卡尺寸同步 ─────────────────────
    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        rect = self.rect()
        if hasattr(self, "_flash"):
            self._flash.setGeometry(rect)
        if hasattr(self, "_scanline"):
            self._scanline.setGeometry(rect)
