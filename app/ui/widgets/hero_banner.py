"""Hero Section —— 世界杯赛事中心首屏（广播级）。

WORLD CUP CONSOLE 5.0
=====================
首屏即「赛事指挥中心」：整块由 :mod:`app.ui.design.stadium_engine` 预渲染的
夜空球场场景作背景（看台辉光 / 灯柱光锥 / 透视草坪 / 中线中圈 / 暗角），其上叠加：

* 左侧：赛事标识 + 巨型标题 + 标语 + 一排 **count-up 数据瓷砖**（球队 / 球场 /
  场次 / 主办国），数字在载入时由 :class:`AnimationManager` 平滑上扬。
* 右侧：焦点比赛面板（双方国旗 + VS / 比分）+ 实时倒计时（天 / 时 / 分 / 秒）。

性能：背景是缓存贴图，``paintEvent`` 只 ``drawPixmap``，逐帧零开销。
"""
from __future__ import annotations

from datetime import datetime, timezone

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match
from app.ui.design.animation_manager import anim as _anim
from app.ui.design.stadium_engine import stadium_pixmap
from app.ui.theme import DARK, ThemePalette
from app.ui.widgets.flag_icon import FlagIcon
from app.utils.time_utils import fmt_datetime, fmt_relative


class _StatTile(QWidget):
    """数据瓷砖：大号 count-up 数字 + 中/英标签。"""

    def __init__(self, target: int, zh: str, en: str, accent: str,
                 suffix: str = "") -> None:
        super().__init__()
        self._target = target
        self._suffix = suffix
        self.setMinimumWidth(96)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)

        self._num = QLabel("0" + suffix)
        nf = QFont()
        nf.setPointSize(30)
        nf.setBold(True)
        self._num.setFont(nf)
        self._num.setStyleSheet(f"color:{accent}; background:transparent;")
        lay.addWidget(self._num)

        zh_lbl = QLabel(zh)
        zh_lbl.setStyleSheet(
            "color:#FFFFFF; font-size:12.5px; font-weight:800; background:transparent;")
        lay.addWidget(zh_lbl)
        en_lbl = QLabel(en)
        en_lbl.setStyleSheet(
            "color:rgba(255,255,255,0.55); font-size:9.5px; font-weight:800;"
            " letter-spacing:1.4px; background:transparent;")
        lay.addWidget(en_lbl)

    def set_accent(self, accent: str) -> None:
        self._num.setStyleSheet(f"color:{accent}; background:transparent;")

    def play(self) -> None:
        suffix = self._suffix
        _anim().count_up(
            lambda s: self._num.setText(s + suffix),
            0, self._target, duration=1100, fmt="{:.0f}", parent=self,
        )


class _CountdownCell(QWidget):
    """单个倒计时格子：大号数字 + 下方单位标签。"""

    def __init__(self, unit: str, accent: str) -> None:
        super().__init__()
        self.setFixedSize(60, 66)
        self._accent = accent
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        self._num = QLabel("00")
        self._num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._num.setStyleSheet(
            "color:#FFFFFF; font-size:26px; font-weight:900;"
            " background: rgba(255,255,255,0.07); border-radius:13px;"
            " border:1px solid rgba(255,255,255,0.16);")
        self._num.setFixedHeight(46)
        lay.addWidget(self._num)
        self._u = QLabel(unit)
        self._u.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._u.setStyleSheet(
            f"color:{accent}; font-size:10px; font-weight:800;"
            " letter-spacing:1px; background:transparent;")
        lay.addWidget(self._u)

    def set_value(self, v: int) -> None:
        self._num.setText(f"{max(0, v):02d}")

    def set_accent(self, accent: str) -> None:
        self._accent = accent
        self._u.setStyleSheet(
            f"color:{accent}; font-size:10px; font-weight:800;"
            " letter-spacing:1px; background:transparent;")


class HeroBanner(QWidget):
    """广播级首屏 Hero。"""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(404)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        self._pal: ThemePalette = DARK
        self._match: Match | None = None
        self._intro_played = False

        outer = QHBoxLayout(self)
        outer.setContentsMargins(42, 34, 42, 30)
        outer.setSpacing(28)

        # ── 左：标识 + 标题 + 数据瓷砖 ──────────
        left = QVBoxLayout()
        left.setSpacing(10)
        self._tag = QLabel("FIFA WORLD CUP · 2026")
        self._tag.setStyleSheet(
            "color:#FFD700; font-size:12px; font-weight:900;"
            " letter-spacing:3px; background:transparent;")
        left.addWidget(self._tag)

        title = QLabel("WORLD CUP CONSOLE")
        tf = QFont()
        tf.setPointSize(38)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color:white; letter-spacing:1px; background:transparent;")
        left.addWidget(title)

        self._slogan = QLabel("世界杯赛事指挥中心 · 实时聚合全球绿茵盛宴")
        self._slogan.setStyleSheet(
            "color:rgba(255,255,255,0.90); font-size:15px;"
            " font-weight:600; background:transparent;")
        left.addWidget(self._slogan)

        left.addStretch(1)

        tiles = QHBoxLayout()
        tiles.setSpacing(26)
        self._tiles = [
            _StatTile(48, "支球队", "TEAMS", "#00BFFF"),
            _StatTile(16, "座球场", "STADIUMS", "#2ED877"),
            _StatTile(104, "场对决", "MATCHES", "#FFD700"),
            _StatTile(3, "主办国", "HOSTS", "#FF8A3D"),
        ]
        for tile in self._tiles:
            tiles.addWidget(tile)
        tiles.addStretch(1)
        left.addLayout(tiles)
        outer.addLayout(left, 6)

        # ── 右：焦点比赛 + 倒计时 ──────────
        right = QVBoxLayout()
        right.setSpacing(10)
        self._focus_tag = QLabel("📌  焦点比赛 · FEATURED")
        self._focus_tag.setStyleSheet(
            "color:rgba(255,255,255,0.82); font-size:12px;"
            " font-weight:800; letter-spacing:1.6px; background:transparent;")
        right.addWidget(self._focus_tag, alignment=Qt.AlignmentFlag.AlignRight)

        self._teams_row = QHBoxLayout()
        self._teams_row.setSpacing(14)
        self._teams_row.addStretch(1)
        right.addLayout(self._teams_row)

        self._meta_label = QLabel("—")
        self._meta_label.setStyleSheet(
            "color:rgba(255,255,255,0.85); font-size:13px;"
            " font-weight:600; background:transparent;")
        self._meta_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self._meta_label)

        self._cd_caption = QLabel("距离开赛 · KICK-OFF IN")
        self._cd_caption.setStyleSheet(
            "color:rgba(255,255,255,0.66); font-size:10.5px;"
            " font-weight:800; letter-spacing:1.6px; background:transparent;")
        self._cd_caption.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self._cd_caption)

        cd_row = QHBoxLayout()
        cd_row.setSpacing(9)
        cd_row.addStretch(1)
        self._cd_cells = {
            "days": _CountdownCell("天 DAYS", "#FFD700"),
            "hours": _CountdownCell("时 HRS", "#00BFFF"),
            "mins": _CountdownCell("分 MIN", "#00BFFF"),
            "secs": _CountdownCell("秒 SEC", "#00BFFF"),
        }
        for cell in self._cd_cells.values():
            cd_row.addWidget(cell)
        self._cd_widget = QWidget()
        self._cd_widget.setLayout(cd_row)
        right.addWidget(self._cd_widget)
        right.addStretch(1)
        outer.addLayout(right, 4)

        # 倒计时定时器（每秒刷新）
        self._cd_timer = QTimer(self)
        self._cd_timer.setInterval(1000)
        self._cd_timer.timeout.connect(self._tick_countdown)

    # ─── 入场动画（count-up 数据瓷砖，仅首次显示触发） ───
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._intro_played:
            self._intro_played = True
            for tile in self._tiles:
                tile.play()

    # ─── 主题联动 ────────────────────────────
    def apply_palette(self, pal: ThemePalette) -> None:
        self._pal = pal
        self._tag.setStyleSheet(
            f"color:{pal.accent}; font-size:12px; font-weight:900;"
            " letter-spacing:3px; background:transparent;")
        accents = [pal.primary, pal.success, pal.accent, "#FF8A3D"]
        for tile, ac in zip(self._tiles, accents):
            tile.set_accent(ac)
        for key, cell in self._cd_cells.items():
            cell.set_accent(pal.accent if key == "days" else pal.primary)
        self.update()

    # ─── public ─────────────────────────────
    def set_focus_match(self, match: Match | None) -> None:
        while self._teams_row.count() > 1:
            item = self._teams_row.takeAt(self._teams_row.count() - 1)
            w = item.widget()
            if w:
                w.deleteLater()

        if match is None:
            self._match = None
            self._cd_timer.stop()
            self._cd_widget.setVisible(False)
            self._cd_caption.setVisible(False)
            empty = QLabel("暂无焦点比赛")
            empty.setStyleSheet("color:rgba(255,255,255,0.7); background:transparent;")
            self._teams_row.addWidget(empty)
            self._meta_label.setText("")
            return

        self._match = match
        a_logo = FlagIcon(match.team_a_name, height=40)
        b_logo = FlagIcon(match.team_b_name, height=40)
        a_lbl = QLabel(match.team_a_short or match.team_a_name)
        a_lbl.setStyleSheet("color:white; font-weight:800; background:transparent;")
        a_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_lbl = QLabel(match.team_b_short or match.team_b_name)
        b_lbl.setStyleSheet("color:white; font-weight:800; background:transparent;")
        b_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_lbl = QLabel(match.display_score)
        f = QFont()
        f.setPointSize(24)
        f.setBold(True)
        score_lbl.setFont(f)
        score_lbl.setStyleSheet(
            f"color:{self._pal.accent}; background:transparent;")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col_a = QVBoxLayout()
        col_a.addWidget(a_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        col_a.addWidget(a_lbl)
        col_b = QVBoxLayout()
        col_b.addWidget(b_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        col_b.addWidget(b_lbl)
        wa, wb = QWidget(), QWidget()
        wa.setLayout(col_a)
        wb.setLayout(col_b)
        self._teams_row.addWidget(wa)
        self._teams_row.addWidget(score_lbl)
        self._teams_row.addWidget(wb)

        if match.is_live:
            meta = "🔴  直播中  ·  " + (match.minute or "·") + "'"
        elif match.start_play:
            meta = (
                f"开赛  {fmt_datetime(match.start_play)}   ·   "
                f"{fmt_relative(match.start_play)}"
            )
        else:
            meta = match.status.label
        self._meta_label.setText(meta)

        upcoming = (
            not match.is_live
            and match.start_play is not None
            and match.start_play > datetime.now(timezone.utc)
        )
        self._cd_widget.setVisible(upcoming)
        self._cd_caption.setVisible(upcoming)
        if upcoming:
            self._tick_countdown()
            if not self._cd_timer.isActive():
                self._cd_timer.start()
        else:
            self._cd_timer.stop()

    # ─── 倒计时刷新 ─────────────────────────
    def _tick_countdown(self) -> None:
        m = self._match
        if m is None or m.start_play is None:
            self._cd_timer.stop()
            return
        delta = m.start_play - datetime.now(timezone.utc)
        secs = int(delta.total_seconds())
        if secs <= 0:
            for cell in self._cd_cells.values():
                cell.set_value(0)
            self._cd_caption.setText("即将开赛")
            self._cd_timer.stop()
            return
        days, rem = divmod(secs, 86400)
        hours, rem = divmod(rem, 3600)
        mins, s = divmod(rem, 60)
        self._cd_cells["days"].set_value(days)
        self._cd_cells["hours"].set_value(hours)
        self._cd_cells["mins"].set_value(mins)
        self._cd_cells["secs"].set_value(s)

    # ─── 缓存球场场景背景 ─────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = stadium_pixmap(self.width(), self.height(), self._pal, radius=22)
        p.drawPixmap(0, 0, pm)
