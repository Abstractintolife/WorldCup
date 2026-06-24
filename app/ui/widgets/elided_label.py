"""elided_label —— 自动省略号 QLabel（防止窄列中文字相互挤压 / 重叠）。

普通 :class:`QLabel` 在空间不足时会**裁切**文字（产生与相邻控件「文字冲突」
的观感）。:class:`ElidedLabel` 在每次尺寸变化时按当前宽度重新计算省略文本
（``…``），并将完整文本作为 tooltip，保证在任意窄列下都不会与邻接控件重叠。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget


class ElidedLabel(QLabel):
    """按可用宽度自动省略（``…``）的标签。"""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        mode: Qt.TextElideMode = Qt.TextElideMode.ElideRight,
    ) -> None:
        super().__init__(parent)
        self._full_text = text
        self._mode = mode
        # 横向可被压缩到 0：让布局按 stretch 分配空间，文字超出即省略而非撑破列宽。
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
        self._apply_elision()

    # ── 公共 API ─────────────────────────────
    def setText(self, text: str) -> None:  # noqa: N802 (Qt 命名)
        self._full_text = text or ""
        self._apply_elision()

    def fullText(self) -> str:  # noqa: N802 (Qt 命名)
        """返回未省略的完整文本。"""
        return self._full_text

    def setElideMode(self, mode: Qt.TextElideMode) -> None:  # noqa: N802
        self._mode = mode
        self._apply_elision()

    # ── 内部 ─────────────────────────────────
    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._apply_elision()

    def _apply_elision(self) -> None:
        fm = QFontMetrics(self.font())
        avail = max(0, self.width())
        elided = fm.elidedText(self._full_text, self._mode, avail)
        super().setText(elided)
        # 被省略时用 tooltip 兜底完整文本。
        self.setToolTip(self._full_text if elided != self._full_text else "")
