"""球场页：2026 世界杯 16 个主办城市球场 —— 网络实景图大卡片。"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.stadium import Stadium
from app.services.stadiums_data import all_stadiums, find_stadium
from app.ui.pages.base import BasePage
from app.ui.widgets.card_grid import CardGrid
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.image_loader import RemoteCover
from app.ui.widgets.misc import Card
from app.ui.design.app_cursor import pointing_hand_cursor


class _StadiumCard(QWidget):
    """单个球场卡片：实景图 + 城市名 + 容量 + 角色徽章。"""

    clicked = pyqtSignal(Stadium)
    CARD_W = 332
    CARD_H = 244

    def __init__(self, stadium: Stadium) -> None:
        super().__init__()
        self._stadium = stadium
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setCursor(pointing_hand_cursor())
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._hover = False

        # 背景实景图（自动占满）
        self._cover = RemoteCover(self, accent=stadium.accent,
                                   overlay_top=0.18, overlay_bottom=0.86)
        self._cover.set_url(stadium.image_url)

        # 内容布局
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(0)

        # 顶行：国旗 + 角色徽章
        top = QHBoxLayout()
        top.setSpacing(8)
        flag = FlagIcon(stadium.country, height=28)
        top.addWidget(flag)
        ctry = QLabel(stadium.country)
        ctry.setStyleSheet(
            "color:#ffffff; font-weight:700; font-size:12px;"
            "background: rgba(0,0,0,0.45); border-radius:9px; padding:3px 9px;"
        )
        top.addWidget(ctry)
        top.addStretch(1)
        if stadium.role:
            role = QLabel(self._role_short(stadium.role))
            role.setStyleSheet(
                f"color:#ffffff; font-weight:800; font-size:11px;"
                f"background: {stadium.accent}; border-radius:9px; padding:3px 10px;"
            )
            top.addWidget(role)
        outer.addLayout(top)
        outer.addStretch(1)

        # 名字（中文 + 英文）
        title_zh = QLabel(stadium.name_zh)
        title_zh.setStyleSheet(
            "color:#ffffff; font-size:18px; font-weight:900; letter-spacing:0.5px;"
        )
        outer.addWidget(title_zh)
        title_en = QLabel(stadium.name_en.upper())
        title_en.setStyleSheet(
            "color:#FFD700; font-size:10px; font-weight:800; letter-spacing:1.6px;"
        )
        outer.addWidget(title_en)

        outer.addSpacing(8)

        # 信息行
        info = QHBoxLayout()
        info.setSpacing(14)
        info.addLayout(self._info_box("📍 城市", stadium.city))
        info.addLayout(self._info_box("🪑 容量", f"{stadium.capacity:,}"))
        if stadium.opened:
            info.addLayout(self._info_box("🏗 落成", str(stadium.opened)))
        info.addStretch(1)
        outer.addLayout(info)

    @staticmethod
    def _role_short(role: str) -> str:
        if "决赛" in role:
            return "决赛"
        if "揭幕" in role:
            return "揭幕战"
        if "半决赛" in role:
            return "半决赛"
        if "季军" in role:
            return "季军战"
        if "8 强" in role:
            return "8 强"
        if "16 强" in role:
            return "16 强"
        return "小组赛"

    @staticmethod
    def _info_box(label: str, value: str) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(0)
        l = QLabel(label)
        l.setStyleSheet("color:rgba(255,255,255,0.7); font-size:9.5px; font-weight:700; letter-spacing:0.6px;")
        col.addWidget(l)
        v = QLabel(value)
        v.setStyleSheet("color:#ffffff; font-weight:800; font-size:13px;")
        col.addWidget(v)
        return col

    # ── 几何与悬停 ──────────────────────────
    def resizeEvent(self, ev) -> None:
        self._cover.setGeometry(0, 0, self.width(), self.height())
        self._cover.lower()
        super().resizeEvent(ev)

    def enterEvent(self, _ev) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, _ev) -> None:
        self._hover = False
        self.update()

    def paintEvent(self, _ev) -> None:
        # 描边（hover 时点亮 accent 色）
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 18.0, 18.0)
        col = QColor(self._stadium.accent)
        from PyQt6.QtGui import QPen
        p.setPen(QPen(col if self._hover else QColor(255, 255, 255, 28), 1.5))
        p.drawPath(path)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._stadium)
        super().mousePressEvent(ev)


class StadiumsPage(BasePage):
    title = "球场"
    subtitle = "2026 世界杯 · 美 加 墨 16 座主办球场"

    stadium_clicked = pyqtSignal(Stadium)

    def __init__(self) -> None:
        super().__init__()

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(16)

        head = Card(padding=18)
        h_lay = QVBoxLayout(head)
        h_lay.setContentsMargins(20, 14, 20, 14)
        h_lay.setSpacing(8)
        title = QLabel("🌎  16 座主办球场")
        title.setStyleSheet("font-size: 18px; font-weight: 900;")
        h_lay.addWidget(title)
        sub = QLabel(
            "2026 年世界杯首次扩军至 48 队，由美国、加拿大、墨西哥三国联合举办。"
        )
        sub.setStyleSheet("color:#B0BEC5; font-size: 12px;")
        sub.setWordWrap(True)
        h_lay.addWidget(sub)

        # 搜索
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍   搜索球场名 / 城市 / 国家...")
        self._search.textChanged.connect(self._render)
        h_lay.addWidget(self._search)
        outer.addWidget(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        self._grid = CardGrid(_StadiumCard.CARD_W, _StadiumCard.CARD_H,
                              h_spacing=16, v_spacing=16)
        scroll.setWidget(self._grid)

    def refresh(self, force: bool = False) -> None:
        self._render()
        self.show_content()

    def _render(self) -> None:
        self._grid.clear()
        text = self._search.text().strip()
        cards: list[QWidget] = []
        for s in (find_stadium(text) if text else all_stadiums()):
            card = _StadiumCard(s)
            card.clicked.connect(self.stadium_clicked.emit)
            cards.append(card)
        self._grid.add_cards(cards)
        stagger_fade(cards, step=35, dx=0, dy=0)
