"""可换行的流式布局（与 ``QHBoxLayout`` 类似，但会自动折行）。

PyQt 文档示例的精简移植版。用于排队卡片、组别卡片等响应式布局。
"""
from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    def __init__(
        self,
        parent=None,
        margin: int = 0,
        h_spacing: int = 12,
        v_spacing: int = 12,
    ) -> None:
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._h = h_spacing
        self._v = v_spacing
        self._items: list = []

    # ── QLayout 必要重载 ───────────────────────
    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    # ── 内部 ──────────────────────────────────
    def _do_layout(self, rect, test_only: bool) -> int:
        m = self.contentsMargins()
        eff = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y = eff.x(), eff.y()
        line_h = 0
        for item in self._items:
            wid = item.widget()
            sp_x = self._h
            sp_y = self._v
            if wid is not None:
                style = wid.style()
                sp_x = max(
                    sp_x,
                    style.layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Horizontal,
                    ),
                )
                sp_y = max(
                    sp_y,
                    style.layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Vertical,
                    ),
                )
            next_x = x + item.sizeHint().width() + sp_x
            if next_x - sp_x > eff.right() and line_h > 0:
                x = eff.x()
                y = y + line_h + sp_y
                next_x = x + item.sizeHint().width() + sp_x
                line_h = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_h = max(line_h, item.sizeHint().height())
        return y + line_h - rect.y() + m.bottom()
