"""淘汰赛对阵图页面（脑图 / Bracket）。

把 :class:`app.ui.widgets.knockout_bracket.KnockoutBracket` 放进可滚动容器，
顶部带标题与数据来源说明。对阵数据默认取自 Opta 预测（The Analyst bracket）。

点击某个对阵格会按双方中文队名在赛程中查找对应 :class:`Match`，命中则发出
``match_clicked`` 进入比赛详情；未命中（对阵尚未在赛程中产生）则回退为
``team_clicked``（主队），仍给出有意义的跳转。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.models.match import Match
from app.ui.pages.base import BasePage
from app.ui.widgets.knockout_bracket import KnockoutBracket

_TEXT = "#E8EEF5"
_DIM = "#7C8CA1"


class BracketPage(BasePage):
    title = "对阵图"
    subtitle = "淘汰赛对阵树 · Opta 预测"

    match_clicked = pyqtSignal(Match)   # 命中赛程 → 进入比赛详情
    team_clicked = pyqtSignal(str)      # 回退：按球队中文名进入球队详情

    def __init__(self, service=None) -> None:
        super().__init__()
        self._service = service
        self._matches: list[Match] = []
        self._loaded = False

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(22, 18, 22, 14)
        outer.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(12)
        title = QLabel("🧩  淘汰赛对阵图")
        title.setStyleSheet(f"font-size:20px; font-weight:900; color:{_TEXT};")
        head.addWidget(title)
        head.addStretch(1)
        outer.addLayout(head)

        sub = QLabel(
            "32 强淘汰赛对阵树：左右各 16 队向中间收拢 —— 16强 → 八强 → "
            "半决赛 → 决赛 / 冠军（数据来源：The Analyst / Opta 超级计算机预测）。"
            "点击任一对阵格可进入对应比赛详情。"
        )
        sub.setStyleSheet(f"color:{_DIM}; font-size:12px;")
        sub.setWordWrap(True)
        outer.addWidget(sub)

        # 可滚动画布
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea{background:transparent; border:none;}")

        canvas_wrap = QWidget()
        wrap_lay = QHBoxLayout(canvas_wrap)
        wrap_lay.setContentsMargins(0, 0, 0, 0)
        self._bracket = KnockoutBracket()
        self._bracket.match_clicked.connect(self._on_pair_clicked)
        wrap_lay.addWidget(self._bracket)
        wrap_lay.addStretch(1)
        scroll.setWidget(canvas_wrap)

        outer.addWidget(scroll, 1)

    # ── 数据加载 ──────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        """加载赛程，用于把对阵格解析为可跳转的 Match（仅首屏 / force 时）。"""
        if self._service is None or (self._loaded and not force):
            self.show_content()
            return

        async def runner() -> None:
            _r, matches = await self._service.fetch_full_schedule(force=force)
            self._matches = matches
            self._loaded = True

        self.run_async(runner, show_loader=False)

    # ── 点击解析 ──────────────────────────────────────────
    def _on_pair_clicked(self, home_cn: str, away_cn: str) -> None:
        key = frozenset({home_cn, away_cn})
        for m in self._matches:
            if frozenset({m.team_a_name, m.team_b_name}) == key:
                self.match_clicked.emit(m)
                return
        # 赛程中暂无该对阵（预测对阵尚未在真实赛程产生）→ 回退到主队详情
        self.team_clicked.emit(home_cn)
