"""sub_header —— 概览页子标题栏 + 实时连接胶囊（WorldCup 3.0）。

对应需求 4.1 / 4.2 / 4.3：

* 一行主文案「2026 美加墨世界杯 · 实时数据总览」。
* 次行「OVERVIEW · 数据来源：懂球帝公开接口」。
* 右对齐绿色「实时数据已连接」胶囊（带状态圆点）。

颜色一律取自 :data:`NIGHT_STADIUM` 令牌（不硬编码 hex）。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba


class LiveConnectionPill(QFrame):
    """右对齐绿色「实时数据已连接」状态胶囊（状态圆点 + 文案）。"""

    def __init__(
        self,
        text: str = "实时数据已连接",
        palette: HudPalette = NIGHT_STADIUM,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("LiveConnectionPill")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._palette = palette
        self._connected = True
        p = palette

        self.setStyleSheet(
            f"""
QFrame#LiveConnectionPill {{
    background: {rgba(p.win, 0.14)};
    border: 1px solid {rgba(p.win, 0.45)};
    border-radius: {Radius.PILL}px;
}}
""".strip()
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 6, 16, 6)
        lay.setSpacing(8)

        self._dot = QLabel("●")
        self._dot.setObjectName("LivePillDot")
        self._dot.setStyleSheet(
            f"QLabel#LivePillDot {{ color: {p.win};"
            f" font-size: {Type.CAPTION}px; background: transparent; }}"
        )
        lay.addWidget(self._dot)

        self._label = QLabel(text)
        self._label.setObjectName("LivePillText")
        self._label.setStyleSheet(
            f"QLabel#LivePillText {{ color: {p.win};"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD};"
            f" background: transparent; }}"
        )
        lay.addWidget(self._label)

    def set_connected(self, on: bool, *, text: str | None = None) -> None:
        """切换连接态配色（连接=绿色 win，断开=红色 loss）。"""
        self._connected = bool(on)
        p = self._palette
        col = p.win if self._connected else p.loss
        self.setStyleSheet(
            f"QFrame#LiveConnectionPill {{"
            f" background: {rgba(col, 0.14)};"
            f" border: 1px solid {rgba(col, 0.45)};"
            f" border-radius: {Radius.PILL}px; }}"
        )
        self._dot.setStyleSheet(
            f"QLabel#LivePillDot {{ color: {col};"
            f" font-size: {Type.CAPTION}px; background: transparent; }}"
        )
        self._label.setStyleSheet(
            f"QLabel#LivePillText {{ color: {col};"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD};"
            f" background: transparent; }}"
        )
        if text is not None:
            self._label.setText(text)
        else:
            from app.i18n import tr
            self._label.setText(
                tr("实时数据已连接") if self._connected
                else tr("实时数据已断开"))

    def set_language(self, lang: str) -> None:
        """语言切换：以当前连接态重新本地化胶囊文案。"""
        self.set_connected(self._connected)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def text(self) -> str:
        return self._label.text()


class SubHeader(QFrame):
    """概览页子标题栏：双行文案 + 右对齐实时连接胶囊。"""

    def __init__(self, palette: HudPalette = NIGHT_STADIUM) -> None:
        super().__init__()
        self.setObjectName("SubHeader")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QFrame#SubHeader { background: transparent; }")
        self._palette = palette
        p = palette

        outer = QHBoxLayout(self)
        outer.setContentsMargins(28, 6, 28, 10)
        outer.setSpacing(16)

        col = QVBoxLayout()
        col.setSpacing(2)

        self._line1 = QLabel("2026 美加墨世界杯 · 实时数据总览")
        self._line1.setObjectName("SubHeaderLine1")
        self._line1.setStyleSheet(
            f"QLabel#SubHeaderLine1 {{ color: {p.text};"
            f" font-size: {Type.H3}px; font-weight: {Type.W_BOLD};"
            f" background: transparent; }}"
        )
        col.addWidget(self._line1)

        self._line2 = QLabel("OVERVIEW · 数据来源：懂球帝公开接口")
        self._line2.setObjectName("SubHeaderLine2")
        self._line2.setStyleSheet(
            f"QLabel#SubHeaderLine2 {{ color: {p.text_dim};"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_MEDIUM};"
            f" letter-spacing: 1px; background: transparent; }}"
        )
        col.addWidget(self._line2)
        outer.addLayout(col)

        outer.addStretch(1)

        self._pill = LiveConnectionPill(palette=palette)
        outer.addWidget(self._pill, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    # ── 接口 ────────────────────────────────
    def set_connected(self, on: bool) -> None:
        self._pill.set_connected(on)

    def set_language(self, lang: str) -> None:
        """切换子标题栏语言（双行文案 + 实时连接胶囊）。"""
        from app.i18n import tr
        self._line1.setText(tr("2026 美加墨世界杯 · 实时数据总览"))
        self._line2.setText(tr("OVERVIEW · 数据来源：懂球帝公开接口"))
        self._pill.set_language(lang)

    @property
    def pill(self) -> LiveConnectionPill:
        return self._pill
