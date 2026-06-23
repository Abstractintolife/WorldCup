"""顶部栏：面包屑标题 + 圆角搜索框 + 通知 / 皮肤 / 刷新 / 设置 图标。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from app.config import TOPBAR_HEIGHT
from app.ui.theme import THEME_META, THEME_ORDER


class _GlowLineEdit(QLineEdit):
    """胶囊搜索框：聚焦时切换出粉红色径向光晕。"""

    def __init__(self) -> None:
        super().__init__()
        self._glow: QGraphicsDropShadowEffect | None = None

    def _install_glow(self) -> None:
        if self._glow is not None:
            return
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(20)
        eff.setOffset(0, 0)
        # spec: 0 0 20px 电光蓝光晕
        eff.setColor(QColor(0, 191, 255, 150))
        self.setGraphicsEffect(eff)
        self._glow = eff

    def _remove_glow(self) -> None:
        if self._glow is None:
            return
        self.setGraphicsEffect(None)
        self._glow = None

    def focusInEvent(self, ev) -> None:  # noqa: D401
        self._install_glow()
        super().focusInEvent(ev)

    def focusOutEvent(self, ev) -> None:  # noqa: D401
        self._remove_glow()
        super().focusOutEvent(ev)


def _icon_button(emoji: str, tooltip: str = "") -> QPushButton:
    btn = QPushButton(emoji)
    btn.setProperty("iconBtn", True)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if tooltip:
        btn.setToolTip(tooltip)
    return btn


# 皮肤菜单样式（深色玻璃 + 选中高亮）
_SKIN_MENU_QSS = """
QMenu {
    background: rgba(11,16,32,0.97);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px;
    padding: 8px;
    color: #FFFFFF;
}
QMenu::item {
    padding: 10px 20px 10px 16px;
    border-radius: 9px;
    margin: 2px 2px;
    font-size: 13px;
    font-weight: 600;
}
QMenu::item:selected {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(0,191,255,0.35), stop:1 rgba(106,90,205,0.10));
    color: #ffffff;
}
QMenu::item:checked {
    color: #ffffff;
    font-weight: 800;
}
QMenu::indicator { width: 0; height: 0; }
"""


class TopBar(QFrame):
    search_submitted = pyqtSignal(str)
    refresh_clicked = pyqtSignal()
    theme_toggled = pyqtSignal()
    skin_selected = pyqtSignal(str)  # 皮肤名（theme key）
    settings_clicked = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(TOPBAR_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(28, 12, 28, 12)
        outer.setSpacing(14)

        # 标题块
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self._title = QLabel("仪表盘")
        self._title.setStyleSheet(
            "font-size:19px; font-weight:900; color:#FFFFFF;"
        )
        self._subtitle = QLabel("DASHBOARD")
        self._subtitle.setStyleSheet(
            "color:#B0BEC5; font-size:11px; letter-spacing:1.6px; font-weight:700;"
        )
        title_box.addWidget(self._title)
        title_box.addWidget(self._subtitle)
        outer.addLayout(title_box)

        outer.addStretch(1)

        # 搜索框（圆角胶囊 —— 高 48px / 圆角 50px / 聚焦红色光晕）
        self._search = _GlowLineEdit()
        self._search.setPlaceholderText("🔍   搜索球队 / 球员 / 比赛 ID...")
        self._search.setFixedHeight(48)
        self._search.setMinimumWidth(280)
        self._search.setMaximumWidth(380)
        self._search.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        # 行内样式覆盖全局 QSS：彻底胶囊化（border-radius 24 = 高 48 的一半）
        self._search.setStyleSheet(
            "QLineEdit{background: rgba(255,255,255,0.05);"
            " border: 1px solid rgba(255,255,255,0.15);"
            " border-radius: 24px; padding: 0 22px; color: #FFFFFF;"
            " font-size: 12.5px; selection-background-color: #00BFFF;}"
            "QLineEdit:focus{border: 1px solid #00BFFF;"
            " background: rgba(0,191,255,0.10);}"
        )
        self._search.returnPressed.connect(
            lambda: self.search_submitted.emit(self._search.text().strip())
        )
        outer.addWidget(self._search)

        # 圆形图标按钮
        bell = _icon_button("🔔", "通知")
        outer.addWidget(bell)

        refresh_btn = _icon_button("⟳", "强制刷新当前页")
        refresh_btn.clicked.connect(self.refresh_clicked.emit)
        outer.addWidget(refresh_btn)

        # 皮肤切换 —— 弹出菜单，列出全部动态皮肤
        self._skin_btn = _icon_button("🎨", "切换皮肤主题")
        self._skin_menu = QMenu(self)
        self._skin_menu.setStyleSheet(_SKIN_MENU_QSS)
        self._skin_group = QActionGroup(self)
        self._skin_group.setExclusive(True)
        self._skin_actions: dict[str, QAction] = {}
        for name in THEME_ORDER:
            zh, emoji, desc = THEME_META.get(name, (name, "🎨", ""))
            act = QAction(f"{emoji}   {zh}    ·  {desc}", self)
            act.setCheckable(True)
            act.setData(name)
            act.triggered.connect(lambda _checked, n=name: self._on_skin_pick(n))
            self._skin_group.addAction(act)
            self._skin_menu.addAction(act)
            self._skin_actions[name] = act
        self._skin_btn.setMenu(self._skin_menu)
        outer.addWidget(self._skin_btn)

        gear = _icon_button("⚙", "设置")
        gear.clicked.connect(self.settings_clicked.emit)
        outer.addWidget(gear)

    # ── 皮肤 ──────────────────────────────────
    def _on_skin_pick(self, name: str) -> None:
        self.skin_selected.emit(name)

    def set_current_skin(self, name: str) -> None:
        act = self._skin_actions.get(name)
        if act is not None:
            act.setChecked(True)

    # ── 接口 ──────────────────────────────────
    def set_title(self, title: str, subtitle: str = "") -> None:
        self._title.setText(title)
        # 把中文子标题转为「英文化大写」样式：直接显示原 subtitle，若空显示路径式 hint
        self._subtitle.setText(subtitle if subtitle else self._derive_en(title))

    @staticmethod
    def _derive_en(title: str) -> str:
        m = {
            "仪表盘": "DASHBOARD",
            "地球仪": "GLOBE",
            "赛程大厅": "MATCH SCHEDULE",
            "积分榜": "STANDINGS",
            "射手榜": "TOP SCORERS",
            "助攻榜": "TOP ASSISTS",
            "国家队": "TEAMS",
            "球场": "STADIUMS",
            "收藏夹": "FAVORITES",
            "比赛详情": "MATCH DETAILS",
            "球员详情": "PLAYER PROFILE",
            "球队详情": "TEAM PROFILE",
            "搜索": "SEARCH",
        }
        return m.get(title, "")

    @property
    def search_text(self) -> str:
        return self._search.text().strip()

    def set_search_text(self, value: str) -> None:
        self._search.setText(value)
