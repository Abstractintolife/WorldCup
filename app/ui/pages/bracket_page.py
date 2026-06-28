"""淘汰赛对阵图页面（脑图 / Bracket）。

把 :class:`app.ui.widgets.knockout_bracket.KnockoutBracket` 放进可滚动容器，
顶部带标题与数据来源说明。对阵数据默认取自 Opta 预测（The Analyst bracket）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.ui.pages.base import BasePage
from app.ui.widgets.knockout_bracket import KnockoutBracket

_TEXT = "#E8EEF5"
_DIM = "#7C8CA1"


class BracketPage(BasePage):
    title = "对阵图"
    subtitle = "淘汰赛对阵树 · Opta 预测"

    def __init__(self, service=None) -> None:
        super().__init__()
        self._service = service

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
        wrap_lay.addWidget(KnockoutBracket())
        wrap_lay.addStretch(1)
        scroll.setWidget(canvas_wrap)

        outer.addWidget(scroll, 1)
