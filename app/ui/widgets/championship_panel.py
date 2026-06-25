"""championship_panel —— 夺冠概率榜面板（替换概览页右下角「主办城市」面板）。

对照 Opta 超级计算机的「夺冠概率」（theanalyst.com 预测页同源数据），在概览页
右下角以广播级排行榜呈现夺冠热门前几名：名次 + 国旗 + 队名 + 夺冠概率 + 概率条。

数据由 :class:`app.services.theanalyst.TheAnalyst` 提供（实时接口，失败回退离线
快照）。继承 :class:`GlassCard`，与射手榜 / 主办城市等底部面板风格一致。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.services.theanalyst import TeamProbability
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor


class ChampionshipPanel(GlassCard):
    """夺冠概率榜面板（继承 :class:`GlassCard`）。"""

    #: 点击底部「查看完整概率预测」。
    view_all_clicked = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
        top: int = 6,
    ) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        self._top = top
        self.setMinimumHeight(300)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    # ── 骨架 ─────────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(10)
        root.addWidget(self._header())

        self._rows_box = QVBoxLayout()
        self._rows_box.setSpacing(7)
        root.addLayout(self._rows_box)
        root.addStretch(1)

        self._footer_btn = QPushButton("查看完整概率预测")
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
        zh = QLabel("夺冠概率榜")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("OPTA TITLE ODDS")
        en.setStyleSheet(
            f"color: {p.accent}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        col.addWidget(en)
        row.addLayout(col)
        row.addStretch(1)
        tag = QLabel("超算模拟")
        tag.setStyleSheet(
            f"color: {p.accent}; font-size: 10px; font-weight: {Type.W_BOLD};"
            f" background: {rgba(p.accent, 0.12)}; border-radius: {Radius.PILL}px;"
            " padding: 3px 10px;"
        )
        row.addWidget(tag, alignment=Qt.AlignmentFlag.AlignVCenter)
        return w

    # ── 公共 API ─────────────────────────────
    def set_ranking(self, teams: list[TeamProbability]) -> None:
        """注入夺冠概率排行榜（取前 ``top`` 名）。"""
        self._clear_rows()
        top = [t for t in teams if t.win_pct > 0][: self._top] or teams[: self._top]
        max_pct = max((t.win_pct for t in top), default=1.0) or 1.0
        for i, t in enumerate(top, start=1):
            self._rows_box.addWidget(self._team_row(i, t, max_pct))

    # ── 名次配色 ─────────────────────────────
    def _rank_color(self, rank: int) -> str:
        p = self._palette
        return {1: p.accent, 2: "#CBD5E1", 3: "#FF9D5C"}.get(rank, p.text_faint)

    def _team_row(self, rank: int, t: TeamProbability, max_pct: float) -> QWidget:
        p = self._palette
        w = QFrame()
        w.setObjectName("TitleRow")
        w.setFixedHeight(46)
        w.setStyleSheet(
            f"QFrame#TitleRow {{ background: {rgba('#FFFFFF', 0.03)};"
            f" border-radius: {Radius.CHIP}px; }}"
            f"QFrame#TitleRow:hover {{ background: {rgba('#FFFFFF', 0.08)}; }}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 4, 14, 4)
        row.setSpacing(10)

        rk = QLabel(str(rank))
        rk.setFixedWidth(16)
        rk.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rk.setStyleSheet(
            f"color: {self._rank_color(rank)}; font-size: 15px;"
            f" font-weight: {Type.W_BLACK}; background: transparent;"
        )
        row.addWidget(rk)
        row.addWidget(FlagIcon(t.team_cn, height=20, radius=4))

        # 队名 + 概率条
        col = QVBoxLayout()
        col.setSpacing(3)
        nm = QLabel(t.team_cn)
        nm.setStyleSheet(
            f"color: {p.text}; font-size: 12.5px; font-weight: {Type.W_BOLD};"
            " background: transparent;"
        )
        col.addWidget(nm)
        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int(t.win_pct / max_pct * 1000))
        bar.setTextVisible(False)
        bar.setFixedHeight(5)
        bar.setStyleSheet(
            f"QProgressBar {{ background: {rgba(p.text, 0.08)}; border: none;"
            " border-radius: 2px; }"
            f"QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {p.accent}, stop:1 {p.primary_hi}); border-radius: 2px; }}"
        )
        col.addWidget(bar)
        row.addLayout(col, 1)

        pct = QLabel(f"{t.win_pct:.1f}%")
        pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pct.setStyleSheet(
            f"color: {p.accent}; font-size: 15px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        pct.setFixedWidth(54)
        row.addWidget(pct)
        return w

    def _clear_rows(self) -> None:
        while self._rows_box.count():
            it = self._rows_box.takeAt(0)
            wdg = it.widget()
            if wdg is not None:
                wdg.deleteLater()
