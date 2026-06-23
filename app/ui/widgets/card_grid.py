"""确定性的响应式卡片网格。

为什么不用 ``FlowLayout`` ？
---------------------------
``FlowLayout`` 依赖 Qt 的 *height-for-width* 协商；当它被放进
``QScrollArea(setWidgetResizable(True))`` 中、且在控件尚未获得正确宽度时
触发布局，在部分平台（如 Windows + High-DPI）上会出现所有卡片堆叠到
左上角的问题。

``CardGrid`` 改为「按当前宽度直接计算列数并用 setGeometry 摆放」，
完全不依赖布局协商，因此在任何平台 / 任何时机都能正确排布。
"""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QSizePolicy, QWidget


class CardGrid(QWidget):
    """把一组固定尺寸的卡片自动按行列排布的容器。"""

    def __init__(
        self,
        card_w: int,
        card_h: int,
        *,
        h_spacing: int = 14,
        v_spacing: int = 14,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cw = card_w
        self._ch = card_h
        self._hs = h_spacing
        self._vs = v_spacing
        self._cards: list[QWidget] = []
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    # ── 增删 ──────────────────────────────
    def add_card(self, w: QWidget) -> None:
        w.setParent(self)
        w.show()
        self._cards.append(w)
        self._relayout()

    def add_cards(self, widgets: list[QWidget]) -> None:
        for w in widgets:
            w.setParent(self)
            w.show()
            self._cards.append(w)
        self._relayout()

    def clear(self) -> None:
        for c in self._cards:
            c.setParent(None)
            c.deleteLater()
        self._cards = []
        self.setMinimumHeight(0)
        self.updateGeometry()

    def cards(self) -> list[QWidget]:
        return list(self._cards)

    # ── 计算 ──────────────────────────────
    def _columns(self, width: int) -> int:
        if width <= 0:
            width = max(self.width(), self._cw)
        return max(1, (width + self._hs) // (self._cw + self._hs))

    def _rows_for_width(self, width: int) -> int:
        if not self._cards:
            return 0
        cols = self._columns(width)
        return (len(self._cards) + cols - 1) // cols

    def _relayout(self) -> None:
        width = self.width()
        cols = self._columns(width)
        # 居中：计算左侧留白，让整体网格水平居中
        grid_w = cols * self._cw + (cols - 1) * self._hs
        left = max(0, (width - grid_w) // 2)
        for i, c in enumerate(self._cards):
            r, col = divmod(i, cols)
            x = left + col * (self._cw + self._hs)
            y = r * (self._ch + self._vs)
            c.setGeometry(x, y, self._cw, self._ch)
        rows = self._rows_for_width(width)
        h = rows * self._ch + max(0, rows - 1) * self._vs
        self.setMinimumHeight(h)
        self.updateGeometry()

    # ── Qt 钩子 ───────────────────────────
    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._relayout()

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        rows = self._rows_for_width(width)
        return rows * self._ch + max(0, rows - 1) * self._vs

    def sizeHint(self) -> QSize:
        rows = self._rows_for_width(self.width())
        h = rows * self._ch + max(0, rows - 1) * self._vs
        return QSize(self._cw * 4, h)

    def minimumSizeHint(self) -> QSize:
        return QSize(self._cw, self._ch)
