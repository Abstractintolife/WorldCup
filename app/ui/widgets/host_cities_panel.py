"""host_cities_panel —— 主办城市面板（WorldCup 3.0，任务 12.5）。

对照设计稿 1:1 复刻「主办城市 / HOST CITIES」底部面板（继承 :class:`GlassCard`）：

* 头部标题「主办城市 / HOST CITIES」（需求 15.1）。
* 风格化北美地图（美国 / 加拿大 / 墨西哥）+ 发光城市点（需求 15.2）。
* 标注 16 座 2026 主办城市（需求 15.3）：温哥华 / 多伦多 / 西雅图 / 旧金山 /
  洛杉矶 / 达拉斯 / 休斯顿 / 堪萨斯城 / 亚特兰大 / 纽约·新泽西 / 波士顿 /
  费城 / 迈阿密 / 墨西哥城 / 瓜达拉哈拉 / 蒙特雷。
* 底部按钮「查看全部城市」（需求 15.4）。

主办城市为**静态数据集**（无公开数据源），以风格化地图渲染。不修改
``app/api`` / ``app/models`` / ``app/services``。
"""
from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor


# ════════════════════════════════════════════════════════════════════
#  静态主办城市数据集
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class HostCity:
    """一座主办城市：名称 + 归一化地图坐标（x 由西到东 0→1，y 由北到南 0→1）+ 国别。"""

    name: str
    x: float
    y: float
    country: str  # "USA" / "CAN" / "MEX"


#: 2026 美加墨世界杯 16 座主办城市（需求 15.3，坐标为风格化近似）。
HOST_CITIES: list[HostCity] = [
    HostCity("温哥华", 0.09, 0.16, "CAN"),
    HostCity("西雅图", 0.11, 0.23, "USA"),
    HostCity("多伦多", 0.71, 0.28, "CAN"),
    HostCity("波士顿", 0.88, 0.31, "USA"),
    HostCity("纽约·新泽西", 0.84, 0.37, "USA"),
    HostCity("费城", 0.82, 0.42, "USA"),
    HostCity("旧金山", 0.07, 0.45, "USA"),
    HostCity("堪萨斯城", 0.51, 0.43, "USA"),
    HostCity("洛杉矶", 0.13, 0.53, "USA"),
    HostCity("亚特兰大", 0.69, 0.55, "USA"),
    HostCity("达拉斯", 0.46, 0.59, "USA"),
    HostCity("休斯顿", 0.49, 0.65, "USA"),
    HostCity("迈阿密", 0.75, 0.75, "USA"),
    HostCity("蒙特雷", 0.43, 0.75, "MEX"),
    HostCity("瓜达拉哈拉", 0.36, 0.83, "MEX"),
    HostCity("墨西哥城", 0.45, 0.87, "MEX"),
]


# ════════════════════════════════════════════════════════════════════
#  风格化北美地图
# ════════════════════════════════════════════════════════════════════
class _NorthAmericaMap(QWidget):
    """风格化北美地图（加拿大 / 美国 / 墨西哥三块色域）+ 发光城市点 + 标签。"""

    def __init__(
        self,
        cities: list[HostCity],
        palette: HudPalette = NIGHT_STADIUM,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self._cities = cities
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _country_color(self, country: str) -> QColor:
        p = self._palette
        return {
            "CAN": QColor(p.secondary),
            "USA": QColor(p.primary),
            "MEX": QColor(p.accent),
        }.get(country, QColor(p.text_dim))

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        pal = self._palette

        # 整体地图区域（留出内边距）。
        pad_x = w * 0.04
        pad_y = h * 0.04
        mx, my = pad_x, pad_y
        mw, mh = w - 2 * pad_x, h - 2 * pad_y

        def to_px(cx: float, cy: float) -> QPointF:
            return QPointF(mx + cx * mw, my + cy * mh)

        # ── 三块风格化色域（圆角矩形「大陆轮廓」近似） ──
        def blob(x0, y0, x1, y1, color: QColor, alpha: int) -> None:
            r = QRectF(mx + x0 * mw, my + y0 * mh,
                       (x1 - x0) * mw, (y1 - y0) * mh)
            path = QPainterPath()
            path.addRoundedRect(r, 22, 22)
            c = QColor(color)
            c.setAlpha(alpha)
            p.fillPath(path, c)
            p.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 90), 1.2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        # 加拿大（北部宽带）。
        blob(0.02, 0.06, 0.96, 0.30, self._country_color("CAN"), 26)
        # 美国（中部主体）。
        blob(0.03, 0.28, 0.94, 0.66, self._country_color("USA"), 30)
        # 墨西哥（南部收窄）。
        blob(0.30, 0.64, 0.62, 0.94, self._country_color("MEX"), 30)

        # ── 城市发光点 + 标签 ──
        for city in self._cities:
            pt = to_px(city.x, city.y)
            base = self._country_color(city.country)

            # 径向辉光。
            glow = QRadialGradient(pt, 13)
            g0 = QColor(base); g0.setAlpha(150)
            g1 = QColor(base); g1.setAlpha(0)
            glow.setColorAt(0.0, g0)
            glow.setColorAt(1.0, g1)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(glow)
            p.drawEllipse(pt, 13, 13)

            # 实心点 + 白描边。
            dot = QColor(pal.floodlight)
            p.setBrush(dot)
            p.setPen(QPen(QColor(base), 1.5))
            p.drawEllipse(pt, 3.0, 3.0)

            # 标签（点右侧；过于靠右的城市标签改置左侧避免出界）。
            label = city.name
            metrics = p.fontMetrics()
            tw = metrics.horizontalAdvance(label)
            p.setPen(QColor(pal.text))
            f = p.font()
            f.setPointSizeF(7.5)
            f.setBold(True)
            p.setFont(f)
            if city.x > 0.7:
                tx = pt.x() - 6 - tw
            else:
                tx = pt.x() + 6
            ty = pt.y() + 3
            p.drawText(QPointF(tx, ty), label)


# ════════════════════════════════════════════════════════════════════
#  HostCitiesPanel
# ════════════════════════════════════════════════════════════════════
class HostCitiesPanel(GlassCard):
    """主办城市面板（继承 :class:`GlassCard`）。"""

    #: 点击底部「查看全部城市」。
    view_all_clicked = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
        cities: list[HostCity] | None = None,
    ) -> None:
        super().__init__(parent, padding=0, hover=False, palette=palette)
        self._palette = palette
        self._cities = list(cities) if cities else list(HOST_CITIES)
        self.setMinimumHeight(300)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    @property
    def cities(self) -> list[HostCity]:
        return list(self._cities)

    # ── 骨架 ─────────────────────────────────
    def _build_ui(self) -> None:
        p = self._palette
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        # 头部 + 城市计数。
        head = QWidget()
        hrow = QHBoxLayout(head)
        hrow.setContentsMargins(0, 0, 0, 0)
        hrow.setSpacing(10)
        bar = QFrame()
        bar.setFixedSize(4, 24)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f" stop:0 {p.accent}, stop:1 {rgba(p.accent, 0.05)}); border-radius:2px;"
        )
        hrow.addWidget(bar)
        col = QVBoxLayout()
        col.setSpacing(0)
        zh = QLabel("主办城市")
        zh.setStyleSheet(
            f"color: {p.text}; font-size: 16px; font-weight: {Type.W_BLACK};"
            " background: transparent;"
        )
        col.addWidget(zh)
        en = QLabel("HOST CITIES")
        en.setStyleSheet(
            f"color: {p.accent}; font-size: 9px; font-weight: {Type.W_BOLD};"
            " letter-spacing: 1.8px; background: transparent;"
        )
        col.addWidget(en)
        hrow.addLayout(col)
        hrow.addStretch(1)
        count = QLabel(f"{len(self._cities)}座城市")
        count.setStyleSheet(
            f"color: {p.accent}; font-size: 11px; font-weight: {Type.W_BOLD};"
            f" background: {rgba(p.accent, 0.12)}; border-radius: {Radius.PILL}px;"
            " padding: 4px 12px;"
        )
        hrow.addWidget(count, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(head)

        # 风格化地图。
        self._map = _NorthAmericaMap(self._cities, p)
        root.addWidget(self._map, 1)

        # 三国图例。
        legend = QHBoxLayout()
        legend.setSpacing(14)
        legend.addStretch(1)
        for label, country in (("美国", "USA"), ("加拿大", "CAN"), ("墨西哥", "MEX")):
            legend.addWidget(self._legend_dot(label, country))
        legend.addStretch(1)
        root.addLayout(legend)

        # 底部「查看全部城市」。
        self._footer_btn = QPushButton("查看全部城市")
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

    def _legend_color(self, country: str) -> str:
        p = self._palette
        return {"USA": p.primary, "CAN": p.secondary, "MEX": p.accent}.get(
            country, p.text_dim)

    def _legend_dot(self, label: str, country: str) -> QWidget:
        p = self._palette
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(9, 9)
        dot.setStyleSheet(
            f"background: {self._legend_color(country)}; border-radius: 4px;"
        )
        row.addWidget(dot)
        l = QLabel(label)
        l.setStyleSheet(
            f"color: {p.text_dim}; font-size: 10.5px; font-weight: {Type.W_MEDIUM};"
            " background: transparent;"
        )
        row.addWidget(l)
        return w
