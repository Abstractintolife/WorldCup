"""glass_card —— 统一玻璃拟态卡片基类（WorldCup 3.0，取代 ``misc.Card``）。

全应用所有卡片共享同一玻璃材质（对应需求 20.1 / 20.2 / 20.3 / 19.4，
设计 Property 3）：

* 圆角 **24px**。
* 填充 ``rgba(255,255,255,0.05)``。
* 边框 ``rgba(255,255,255,0.08)``。
* 阴影 ``0 10px 40px rgba(0,0,0,0.4)`` —— **单个** ``QGraphicsDropShadowEffect``。
* 悬停：经 :func:`motion_system.hover_lift` 做 ``translateY(-6px)`` / 180ms
  （动画 ``pos``，**绝不**动画 ``blurRadius`` —— 沿用既有性能教训），
  且边框提亮到 ``glass_border_hi``。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QWidget

from app.ui.design import motion_system
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Shadow


class GlassCard(QFrame):
    """玻璃拟态卡片基类。

    参数
    ----
    glow:
        可选的辉光强调色（hex / rgba 字符串）；预留给子类做主题点缀，
        基类仅记录，不强制渲染。
    hover:
        是否启用悬停浮起 + 边框提亮（默认 ``True``）。作为滚动宿主等
        不需要悬停反馈的场景可传 ``False``。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        glow: str | None = None,
        hover: bool = True,
        palette: HudPalette = NIGHT_STADIUM,
        padding: int = 16,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("GlassCard")
        # 让 QSS 的 background / border-radius 生效（自定义 QFrame 必须开启）。
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(padding, padding, padding, padding)

        self._palette = palette
        self._glow = glow
        self._hover_enabled = hover
        self._hovered = False

        # 基础玻璃材质（即便全局 QSS 未应用也保证单卡可见）。
        self._apply_card_style(hovered=False)

        # 单个投影：0 10px 40px rgba(0,0,0,0.4)。
        blur, dy, base_rgba = Shadow.CARD
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setXOffset(0)
        shadow.setYOffset(dy)
        shadow.setColor(self._shadow_color(base_rgba))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

    # ── 样式 ────────────────────────────────
    def _apply_card_style(self, *, hovered: bool) -> None:
        p = self._palette
        border = p.glass_border_hi if hovered else p.glass_border
        self.setStyleSheet(
            f"QFrame#GlassCard {{"
            f" background: {p.glass_fill};"
            f" border: 1px solid {border};"
            f" border-radius: {Radius.CARD}px;"
            f" }}"
        )

    @staticmethod
    def _shadow_color(base_rgba: str) -> QColor:
        # base_rgba 形如 "rgba(0,0,0,0.40)" —— 解析成带 alpha 的 QColor。
        inner = base_rgba[base_rgba.index("(") + 1:base_rgba.index(")")]
        parts = [s.strip() for s in inner.split(",")]
        r, g, b = (int(float(parts[i])) for i in range(3))
        a = float(parts[3]) if len(parts) == 4 else 1.0
        col = QColor(r, g, b)
        col.setAlphaF(a)
        return col

    # ── 悬停反馈 ─────────────────────────────
    def enterEvent(self, ev) -> None:
        if self._hover_enabled and not self._hovered:
            self._hovered = True
            self._apply_card_style(hovered=True)     # 边框提亮到 glass_border_hi
            motion_system.hover_lift(self, up=True)   # translateY(-6px)
        super().enterEvent(ev)

    def leaveEvent(self, ev) -> None:
        if self._hover_enabled and self._hovered:
            self._hovered = False
            self._apply_card_style(hovered=False)    # 边框还原
            motion_system.hover_lift(self, up=False)  # 精确回到 restY
        super().leaveEvent(ev)

    # ── 便捷查询（供测试 / 子类） ─────────────
    @property
    def is_hovered(self) -> bool:
        return self._hovered
