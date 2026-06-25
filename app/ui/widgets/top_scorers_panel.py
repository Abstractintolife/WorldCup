"""top_scorers_panel —— 射手榜面板（WorldCup 3.0，任务 12.4）。

对照设计稿 1:1 复刻「射手榜 / TOP SCORERS」底部面板（继承 :class:`GlassCard`）：

* 头部标题「射手榜 / TOP SCORERS」（需求 14.1）。
* 排名行：圆形球员头像、名次、球员 + 国家、进球数（需求 14.2）。
* 设计稿样例行（无真实数据时回退，需求 14.3）：
    - 1 梅西（阿根廷） 5
    - 2 姆巴佩（法国） 4
    - 2 哈兰德（挪威） 4
    - 4 Á. Morata（西班牙） 3
* 底部按钮「查看完整射手榜」（需求 14.4）。

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

from app.models.player import PlayerRanking
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.elided_label import ElidedLabel
from app.ui.widgets.glass_card import GlassCard
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.design.app_cursor import pointing_hand_cursor


@dataclass(frozen=True)
class SampleScorer:
    """设计稿样例射手行。"""

    rank: int
    name: str
    country: str
    goals: int


SAMPLE_SCORERS: list[SampleScorer] = [
    SampleScorer(1, "梅西", "阿根廷", 5),
    SampleScorer(2, "姆巴佩", "法国", 4),
    SampleScorer(2, "哈兰德", "挪威", 4),
    SampleScorer(4, "Á. Morata", "西班牙", 3),
]


class TopScorersPanel(GlassCard):
    """射手榜面板（继承 :class:`GlassCard`）。"""

    #: 点击某球员（携带 person_id, person_name）。
    player_clicked = pyqtSignal(str, str)
    #: 点击底部「查看完整射手榜」。
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
        self.setMinimumWidth(185)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._render_sample()

    # ── 骨架 ─────────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(10)
        root.addWidget(self._header())

        self._rows_box = QVBoxLayout()
        self._rows_box.setSpacing(6)
        root.addLayout(self._rows_box)
        root.addStretch(1)

        self._footer_btn = QPushButton("查看完整射手榜")
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
            f" stop:0 {p.accent}, stop:1 {rgba(p.accent, 0.05)}); border-radius:2px;"
        )
        row.addWidget(bar)
        col = QVBoxLayout()
        col.setSpacing(0)
        zh = QLabel("射手榜")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("TOP SCORERS")
        en.setStyleSheet(
            f"color: {p.accent}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        col.addWidget(en)
        row.addLayout(col)
        row.addStretch(1)
        return w

    # ── 公共 API ─────────────────────────────
    def set_scorers(self, scorers: list[PlayerRanking]) -> None:
        """注入真实射手榜（无则回退设计稿样例，需求 14.3）。"""
        self._clear_rows()
        if not scorers:
            self._render_sample()
            return
        for pr in scorers[:5]:
            self._rows_box.addWidget(self._scorer_row(pr))

    # ── 样例渲染 ─────────────────────────────
    def _render_sample(self) -> None:
        self._clear_rows()
        for s in SAMPLE_SCORERS:
            self._rows_box.addWidget(self._sample_row(s))

    # ── 名次配色 ─────────────────────────────
    def _rank_color(self, rank: int) -> str:
        p = self._palette
        return {1: p.accent, 2: "#CBD5E1", 3: "#FF9D5C"}.get(rank, p.text_faint)

    # ── 行构建 ───────────────────────────────
    def _row_frame(self) -> tuple[QFrame, QHBoxLayout]:
        p = self._palette
        w = QFrame()
        w.setObjectName("ScorerRow")
        w.setFixedHeight(48)
        w.setStyleSheet(
            f"QFrame#ScorerRow {{ background: {rgba('#FFFFFF', 0.03)};"
            f" border-radius: {Radius.CHIP}px; }}"
            f"QFrame#ScorerRow:hover {{ background: {rgba('#FFFFFF', 0.08)}; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 4, 14, 4)
        row.setSpacing(10)
        return w, row

    def _rank_lbl(self, rank: int) -> QLabel:
        rk = QLabel(str(rank))
        rk.setFixedWidth(18)
        rk.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rk.setStyleSheet(
            f"color: {self._rank_color(rank)}; font-size: 15px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        return rk

    def _name_block(self, name: str, country: str) -> QWidget:
        p = self._palette
        w = QWidget()
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        nm = ElidedLabel(name, mode=Qt.TextElideMode.ElideRight)
        nm.setStyleSheet(
            f"color: {p.text}; font-size: 12.5px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        col.addWidget(nm)
        ct = ElidedLabel(country, mode=Qt.TextElideMode.ElideRight)
        ct.setStyleSheet(
            f"color: {p.text_faint}; font-size: 10px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        col.addWidget(ct)
        return w

    def _goals_lbl(self, goals: int) -> QLabel:
        p = self._palette
        g = QLabel(f"{goals}")
        g.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        g.setStyleSheet(
            f"color: {p.accent}; font-size: 18px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        unit = QLabel("球")
        unit.setStyleSheet(
            f"color: {p.text_faint}; font-size: 10px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        host = QWidget()
        hl = QHBoxLayout(host)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(3)
        hl.addStretch(1)
        hl.addWidget(g, 0, Qt.AlignmentFlag.AlignBottom)
        hl.addWidget(unit, 0, Qt.AlignmentFlag.AlignBottom)
        return host  # type: ignore[return-value]

    def _sample_row(self, s: SampleScorer) -> QWidget:
        w, row = self._row_frame()
        row.addWidget(self._rank_lbl(s.rank))
        row.addWidget(PlayerAvatar(None, size=32, ring=False))
        row.addWidget(self._name_block(s.name, s.country), 1)
        row.addWidget(self._goals_lbl(s.goals))
        return w

    def _scorer_row(self, pr: PlayerRanking) -> QWidget:
        w, row = self._row_frame()
        if pr.person_id:
            w.setCursor(pointing_hand_cursor())
            w.mousePressEvent = (  # type: ignore[assignment]
                lambda _e, p=pr: self.player_clicked.emit(p.person_id, p.person_name)
            )
        row.addWidget(self._rank_lbl(pr.rank))
        row.addWidget(PlayerAvatar(pr.person_logo, size=32, ring=False))
        row.addWidget(self._name_block(pr.person_name, pr.team_name), 1)
        row.addWidget(self._goals_lbl(pr.count))
        return w

    def _clear_rows(self) -> None:
        while self._rows_box.count():
            it = self._rows_box.takeAt(0)
            wdg = it.widget()
            if wdg is not None:
                wdg.deleteLater()
