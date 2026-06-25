"""概率预测页（Opta 超级计算机赛事模拟）。

把 theanalyst.com「FIFA World Cup Predictions」的夺冠 / 出线概率榜搬进软件：

* 顶部两枚切换：**夺冠概率** / **进决赛概率**。
* 主榜：全部 48 队按所选概率降序，含名次、国旗、队名、小组、概率条与百分比。
* 「按小组」：12 个小组各自的夺冠概率小卡。

数据来自 :class:`app.services.theanalyst.TheAnalyst`（Opta 赛事模拟实时接口，
失败时自动回退离线快照）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.services.theanalyst import TeamProbability, TheAnalyst
from app.ui.pages.base import BasePage
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.design.app_cursor import pointing_hand_cursor

_GOLD = "#FFD700"
_CYAN = "#00BFFF"
_TEXT = "#FFFFFF"
_DIM = "#B0BEC5"
_FAINT = "#6B7689"


class ProbabilityPage(BasePage):
    title = "概率预测"
    subtitle = "OPTA 超级计算机赛事模拟"

    team_clicked = pyqtSignal(str)   # 预留：点击队伍（按中文名）

    def __init__(self, service=None) -> None:
        super().__init__()
        self._service = service
        self._mode = "win"  # win=夺冠概率 / final=进决赛概率

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(22, 18, 22, 18)
        outer.setSpacing(14)

        # 标题
        head = QHBoxLayout()
        head.setSpacing(12)
        title = QLabel("🔮  概率预测")
        title.setStyleSheet(f"font-size:20px; font-weight:900; color:{_TEXT};")
        head.addWidget(title)
        head.addStretch(1)
        self._live_tag = QLabel("数据加载中…")
        self._live_tag.setStyleSheet(
            f"color:{_DIM}; font-size:12px; font-weight:700;"
            "background:rgba(255,255,255,0.06); border-radius:11px; padding:4px 12px;"
        )
        head.addWidget(self._live_tag)
        outer.addLayout(head)

        sub = QLabel(
            "Opta 超级计算机对每场比赛进行数万次赛前模拟，推算各队夺冠 / 进入决赛的"
            "概率（数据来源：The Analyst / Opta）。"
        )
        sub.setStyleSheet(f"color:{_DIM}; font-size:12px;")
        sub.setWordWrap(True)
        outer.addWidget(sub)

        # 切换：夺冠概率 / 进决赛概率
        tabs = QHBoxLayout()
        tabs.setSpacing(10)
        self._btn_win = QPushButton("夺冠概率")
        self._btn_final = QPushButton("进决赛概率")
        for b, mode in ((self._btn_win, "win"), (self._btn_final, "final")):
            b.setCheckable(True)
            b.setCursor(pointing_hand_cursor())
            b.clicked.connect(lambda _c=False, m=mode: self._set_mode(m))
            tabs.addWidget(b)
        tabs.addStretch(1)
        outer.addLayout(tabs)

        # 正文滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll, 1)
        body = QWidget()
        body.setObjectName("OpaqueBody")
        scroll.setWidget(body)
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(16)

        self._apply_tab_style()

    # ── 切换 ─────────────────────────────────
    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        self._apply_tab_style()
        self._render()

    def _apply_tab_style(self) -> None:
        for b, mode in ((self._btn_win, "win"), (self._btn_final, "final")):
            active = self._mode == mode
            b.setChecked(active)
            if active:
                b.setStyleSheet(
                    f"QPushButton{{color:#0E1116; background:{_GOLD}; border:none;"
                    "border-radius:10px; padding:8px 20px; font-size:14px;"
                    "font-weight:900;}"
                )
            else:
                b.setStyleSheet(
                    "QPushButton{color:#C8D0E0; background:rgba(255,255,255,0.06);"
                    "border:1px solid rgba(255,255,255,0.12); border-radius:10px;"
                    "padding:8px 20px; font-size:14px; font-weight:700;}"
                    "QPushButton:hover{background:rgba(255,255,255,0.12);}"
                )

    # ── 数据 ─────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            ok = await TheAnalyst.instance().refresh(force=force)
            self._live_tag.setText("● 实时数据" if ok and TheAnalyst.instance().is_live
                                    else "离线快照")
            self._live_tag.setStyleSheet(
                f"color:{'#2ED877' if ok else _DIM}; font-size:12px; font-weight:700;"
                "background:rgba(255,255,255,0.06); border-radius:11px; padding:4px 12px;"
            )
            self._render()
        self.run_async(runner)

    # ── 渲染 ─────────────────────────────────
    def _clear_body(self) -> None:
        while self._body.count():
            it = self._body.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

    def _ranking(self) -> list[TeamProbability]:
        ta = TheAnalyst.instance()
        return ta.qualifying_ranking() if self._mode == "final" else ta.championship_ranking()

    def _render(self) -> None:
        self._clear_body()
        teams = self._ranking()
        if not teams:
            empty = QLabel("暂无概率数据")
            empty.setStyleSheet(f"color:{_DIM}; font-size:14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._body.addWidget(empty)
            self._body.addStretch(1)
            return

        self._body.addWidget(self._ranking_card(teams))
        self._body.addWidget(self._groups_card())
        self._body.addStretch(1)

    def _pct_of(self, t: TeamProbability) -> float:
        return t.final_pct if self._mode == "final" else t.win_pct

    def _card(self) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("ProbCard")
        card.setStyleSheet(
            "QFrame#ProbCard{background:rgba(255,255,255,0.04);"
            "border:1px solid rgba(255,255,255,0.08); border-radius:18px;}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 18)
        lay.setSpacing(10)
        return card, lay

    def _section(self, lay: QVBoxLayout, text: str) -> None:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{_TEXT}; font-size:15px; font-weight:900;")
        lay.addWidget(lbl)

    def _ranking_card(self, teams: list[TeamProbability]) -> QWidget:
        card, lay = self._card()
        head = "🏆  夺冠概率排行榜" if self._mode == "win" else "🎫  进入决赛概率排行榜"
        self._section(lay, head)
        max_pct = max((self._pct_of(t) for t in teams), default=1.0) or 1.0
        for i, t in enumerate(teams, start=1):
            lay.addWidget(self._team_row(i, t, max_pct))
        return card

    def _rank_color(self, rank: int) -> str:
        return {1: _GOLD, 2: "#CBD5E1", 3: "#FF9D5C"}.get(rank, _FAINT)

    def _team_row(self, rank: int, t: TeamProbability, max_pct: float) -> QWidget:
        pct = self._pct_of(t)
        w = QFrame()
        w.setObjectName("TRow")
        w.setFixedHeight(46)
        w.setStyleSheet(
            "QFrame#TRow{background:rgba(255,255,255,0.03); border-radius:12px;}"
            "QFrame#TRow:hover{background:rgba(255,255,255,0.08);}"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(14, 4, 16, 4)
        row.setSpacing(12)

        rk = QLabel(str(rank))
        rk.setFixedWidth(24)
        rk.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rk.setStyleSheet(
            f"color:{self._rank_color(rank)}; font-size:15px; font-weight:900;"
            "background:transparent;"
        )
        row.addWidget(rk)
        row.addWidget(FlagIcon(t.team_cn, height=22, radius=4))

        nm = QLabel(t.team_cn)
        nm.setFixedWidth(96)
        nm.setStyleSheet(f"color:{_TEXT}; font-size:13.5px; font-weight:800; background:transparent;")
        row.addWidget(nm)

        grp = QLabel(_group_cn(t.group))
        grp.setFixedWidth(58)
        grp.setStyleSheet(f"color:{_FAINT}; font-size:11px; font-weight:700; background:transparent;")
        row.addWidget(grp)

        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int(pct / max_pct * 1000))
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(
            "QProgressBar{background:rgba(255,255,255,0.08); border:none; border-radius:3px;}"
            f"QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {_GOLD}, stop:1 {_CYAN}); border-radius:3px;}}"
        )
        row.addWidget(bar, 1)

        val = QLabel(f"{pct:.1f}%")
        val.setFixedWidth(58)
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setStyleSheet(f"color:{_GOLD}; font-size:15px; font-weight:900; background:transparent;")
        row.addWidget(val)
        return w

    def _groups_card(self) -> QWidget:
        card, lay = self._card()
        self._section(lay, "🗂  按小组")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        groups = TheAnalyst.instance().groups()
        # 按小组名排序（Group A..L）
        names = sorted(groups.keys())
        for idx, gname in enumerate(names):
            r, c = divmod(idx, 3)
            grid.addWidget(self._group_block(gname, groups[gname]), r, c)
        holder = QWidget()
        holder.setLayout(grid)
        lay.addWidget(holder)
        return card

    def _group_block(self, gname: str, teams: list[TeamProbability]) -> QWidget:
        w = QFrame()
        w.setStyleSheet(
            "QFrame{background:rgba(255,255,255,0.03);"
            "border:1px solid rgba(255,255,255,0.07); border-radius:12px;}"
        )
        col = QVBoxLayout(w)
        col.setContentsMargins(12, 10, 12, 10)
        col.setSpacing(6)
        title = QLabel(_group_cn(gname))
        title.setStyleSheet(f"color:{_CYAN}; font-size:12.5px; font-weight:900; background:transparent;")
        col.addWidget(title)
        for t in teams:
            line = QHBoxLayout()
            line.setSpacing(8)
            line.addWidget(FlagIcon(t.team_cn, height=16, radius=3))
            nm = QLabel(t.team_cn)
            nm.setStyleSheet(f"color:{_DIM}; font-size:11.5px; font-weight:700; background:transparent;")
            line.addWidget(nm, 1)
            pc = QLabel(f"{self._pct_of(t):.1f}%")
            pc.setStyleSheet(f"color:{_TEXT}; font-size:11.5px; font-weight:800; background:transparent;")
            pc.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            line.addWidget(pc)
            col.addLayout(line)
        return w


def _group_cn(group_en: str) -> str:
    """'Group A' → '小组 A'。"""
    g = (group_en or "").replace("Group", "").strip()
    return f"小组 {g}" if g else "—"
