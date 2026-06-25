"""today_matches_panel —— 今日赛程面板（WorldCup 3.0，任务 12.1）。

对照设计稿 1:1 复刻「今日赛程 / TODAY'S MATCHES」底部面板（继承
:class:`GlassCard`）：

* 头部标题「今日赛程 / TODAY'S MATCHES」+ 反映当日真实赛事数量的计数
  （如「4场比赛」，需求 12.1）。
* 带时间戳的对阵行：左右双方国旗 + 比分 / 状态（需求 12.2）。
* 设计稿样例行（无真实数据时回退，需求 12.3）：
    - 01:00 葡萄牙 5-0 乌兹别克斯坦（赔率标签）
    - 04:00 英格兰 0-0 加纳（已结束）
    - 07:00 巴西 VS 塞尔维亚（直播）
    - 10:00 法国 VS 沙特阿拉伯（将开赛）
* 底部按钮「查看完整赛程」（需求 12.4）。

不修改 ``app/api`` / ``app/models`` / ``app/services``。
"""
from __future__ import annotations

from dataclasses import dataclass

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

from app.models.match import Match, MatchStatus
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.elided_label import ElidedLabel
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor


# ════════════════════════════════════════════════════════════════════
#  样例对阵视图模型（无真实数据时回退）
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class SampleFixture:
    """设计稿样例对阵行。"""

    time_text: str
    home: str
    away: str
    score: str          # "5-0" / "0-0" / "VS"
    status: str         # "odds" / "played" / "live" / "upcoming"


SAMPLE_FIXTURES: list[SampleFixture] = [
    SampleFixture("01:00", "葡萄牙", "乌兹别克斯坦", "5-0", "odds"),
    SampleFixture("04:00", "英格兰", "加纳", "0-0", "played"),
    SampleFixture("07:00", "巴西", "塞尔维亚", "VS", "live"),
    SampleFixture("10:00", "法国", "沙特阿拉伯", "VS", "upcoming"),
]


class TodayMatchesPanel(GlassCard):
    """今日赛程面板（继承 :class:`GlassCard`）。"""

    #: 点击某场对阵（携带 :class:`Match`）。
    match_clicked = pyqtSignal(Match)
    #: 点击底部「查看完整赛程」。
    view_all_clicked = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
    ) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        self.setMinimumHeight(300)
        self.setMinimumWidth(210)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._render_sample()

    # ── 骨架 ─────────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        # 头部：标题 + 计数。
        head = QWidget()
        hrow = QHBoxLayout(head)
        hrow.setContentsMargins(0, 0, 0, 0)
        hrow.setSpacing(10)
        bar = QFrame()
        bar.setFixedSize(4, 24)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f" stop:0 {p.primary}, stop:1 {rgba(p.primary, 0.05)}); border-radius:2px;"
        )
        hrow.addWidget(bar)
        tcol = QVBoxLayout()
        tcol.setSpacing(0)
        zh = QLabel("今日赛程")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        tcol.addWidget(zh)
        en = QLabel("TODAY'S MATCHES")
        en.setStyleSheet(
            f"color: {p.primary}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        tcol.addWidget(en)
        hrow.addLayout(tcol)
        hrow.addStretch(1)
        self._count_lbl = QLabel("0场比赛")
        self._count_lbl.setStyleSheet(
            f"color: {p.primary}; font-size: 11px; font-weight: {Type.W_BOLD};"
            f" background: {rgba(p.primary, 0.12)}; border-radius: {Radius.PILL}px;"
            " padding: 4px 12px;"
        )
        hrow.addWidget(self._count_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(head)

        # 对阵行容器。
        self._rows_box = QVBoxLayout()
        self._rows_box.setSpacing(8)
        root.addLayout(self._rows_box)
        root.addStretch(1)

        # 底部「查看完整赛程」。
        self._footer_btn = QPushButton("查看完整赛程")
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

    # ── 公共 API ─────────────────────────────
    def set_matches(self, matches: list[Match]) -> None:
        """注入真实今日赛事（无则回退设计稿样例）。计数反映真实数量（需求 12.1）。"""
        self._clear_rows()
        if not matches:
            self._render_sample()
            return
        self._count_lbl.setText(f"{len(matches)}场比赛")
        for m in matches[:4]:
            self._rows_box.addWidget(self._match_row(m))

    @property
    def count_text(self) -> str:
        return self._count_lbl.text()

    # ── 样例渲染 ─────────────────────────────
    def _render_sample(self) -> None:
        self._clear_rows()
        self._count_lbl.setText(f"{len(SAMPLE_FIXTURES)}场比赛")
        for fx in SAMPLE_FIXTURES:
            self._rows_box.addWidget(self._sample_row(fx))

    # ── 行构建 ───────────────────────────────
    def _row_frame(self) -> tuple[QFrame, QHBoxLayout]:
        p = self._palette
        w = QFrame()
        w.setObjectName("FixtureRow")
        w.setFixedHeight(54)
        w.setCursor(pointing_hand_cursor())
        w.setStyleSheet(
            f"QFrame#FixtureRow {{ background: {rgba('#FFFFFF', 0.03)};"
            f" border-radius: {Radius.CHIP}px; }}"
            f"QFrame#FixtureRow:hover {{ background: {rgba('#FFFFFF', 0.08)}; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(8)
        return w, row

    def _time_lbl(self, text: str) -> QLabel:
        p = self._palette
        t = QLabel(text)
        t.setFixedWidth(42)
        t.setStyleSheet(
            f"color: {p.text_dim}; font-size: 12px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        return t

    def _rank_lbl(self, nationality: str) -> QLabel | None:
        """国际足联世界排名小标注（如「#12」），紧贴国旗显示；无排名则不展示。"""
        from app.services.fifa_rankings import FifaRankings
        txt = FifaRankings.instance().rank_text(nationality)
        if not txt:
            return None
        p = self._palette
        lbl = QLabel(txt)
        lbl.setToolTip("国际足联世界排名")
        lbl.setStyleSheet(
            f"color: {p.accent}; font-size: 9.5px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        return lbl

    def _name_lbl(self, text: str, *, align_right: bool = False) -> QLabel:
        from app.utils.text_utils import short_country_name
        p = self._palette
        l = ElidedLabel(short_country_name(text), mode=Qt.TextElideMode.ElideRight)
        l.setStyleSheet(
            f"color: {p.text}; font-size: 12px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        if align_right:
            l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            l.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _score_lbl(self, text: str, color: str) -> QLabel:
        l = QLabel(text)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setFixedWidth(54)
        weight = Type.W_BLACK if text != "VS" else Type.W_BOLD
        l.setStyleSheet(
            f"color: {color}; font-size: 14px; font-weight: {weight};"
            " background: transparent;"
        )
        return l

    def _chip(self, text: str, color: str, *, solid: bool = False) -> QLabel:
        if solid:
            style = (
                f"background: {color}; color: #04121A;"
                f" border-radius: {Radius.PILL}px; padding: 2px 9px;"
                f" font-size: 9px; font-weight: {Type.W_BLACK};"
            )
        else:
            style = (
                f"background: {rgba(color, 0.16)}; color: {color};"
                f" border: 1px solid {rgba(color, 0.4)};"
                f" border-radius: {Radius.PILL}px; padding: 2px 9px;"
                f" font-size: 9px; font-weight: {Type.W_BOLD};"
            )
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return lbl

    def _sample_row(self, fx: SampleFixture) -> QWidget:
        p = self._palette
        w, row = self._row_frame()
        row.addWidget(self._time_lbl(fx.time_text))
        row.addWidget(FlagIcon(fx.home, height=18, radius=3))
        rk_h = self._rank_lbl(fx.home)
        if rk_h is not None:
            row.addWidget(rk_h)
        row.addWidget(self._name_lbl(fx.home), 1)

        score_color = p.live if fx.status == "live" else (
            p.text_faint if fx.score == "VS" else p.text)
        row.addWidget(self._score_lbl(fx.score, score_color))

        row.addWidget(self._name_lbl(fx.away, align_right=True), 1)
        rk_a = self._rank_lbl(fx.away)
        if rk_a is not None:
            row.addWidget(rk_a)
        row.addWidget(FlagIcon(fx.away, height=18, radius=3))

        if fx.status == "odds":
            row.addWidget(self._chip("赔率", p.accent))
        elif fx.status == "played":
            row.addWidget(self._chip("已结束", p.win))
        elif fx.status == "live":
            row.addWidget(self._chip("直播", p.live, solid=True))
        else:
            row.addWidget(self._chip("将开赛", p.primary))
        return w

    def _match_row(self, m: Match) -> QWidget:
        from app.utils.time_utils import fmt_time
        p = self._palette
        w, row = self._row_frame()
        w.mousePressEvent = (  # type: ignore[assignment]
            lambda _e, mm=m: self.match_clicked.emit(mm)
        )
        row.addWidget(self._time_lbl(fmt_time(m.start_play)))
        row.addWidget(FlagIcon(m.team_a_name, height=18, radius=3))
        rk_h = self._rank_lbl(m.team_a_name)
        if rk_h is not None:
            row.addWidget(rk_h)
        row.addWidget(self._name_lbl(m.team_a_name), 1)

        if m.status in (MatchStatus.FIXTURE, MatchStatus.UNKNOWN):
            row.addWidget(self._score_lbl("VS", p.text_faint))
        else:
            color = p.live if m.is_live else p.text
            row.addWidget(self._score_lbl(m.display_score, color))

        row.addWidget(self._name_lbl(m.team_b_name, align_right=True), 1)
        rk_a = self._rank_lbl(m.team_b_name)
        if rk_a is not None:
            row.addWidget(rk_a)
        row.addWidget(FlagIcon(m.team_b_name, height=18, radius=3))

        if m.is_live:
            row.addWidget(self._chip("直播", p.live, solid=True))
        elif m.status == MatchStatus.PLAYED:
            row.addWidget(self._chip("已结束", p.win))
        else:
            row.addWidget(self._chip("将开赛", p.primary))
        return w

    def _clear_rows(self) -> None:
        while self._rows_box.count():
            it = self._rows_box.takeAt(0)
            wdg = it.widget()
            if wdg is not None:
                wdg.deleteLater()
