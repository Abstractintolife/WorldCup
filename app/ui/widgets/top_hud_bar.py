"""top_hud_bar —— 顶部 HUD 栏（WorldCup 3.0 · 夜间球场 HUD），1:1 复刻设计稿。

在 ``hud_theme`` 令牌之上重建（取代旧 ``top_bar.TopBar``）。
对应需求 3.1 / 3.2 / 3.3：

* 左侧：页面标题「概览」+ 副标题「OVERVIEW」。
* 居中：搜索框，占位符「搜索球队 / 球员 / 比赛…」。
* 右侧：通知铃铛、区域地球（显示「CN」）、圆形头像。

颜色一律取自 :data:`NIGHT_STADIUM` 令牌（不硬编码 hex）。保留与旧
``TopBar`` 兼容的 :meth:`set_title` / :meth:`set_current_skin` 接口，
让 ``MainWindow`` 壳层无痛复用。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.config import TOPBAR_HEIGHT
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba
from app.ui.design.app_cursor import pointing_hand_cursor


# 中文标题 → 英文副标题（OVERLINE）映射；概览页副标题恒为「OVERVIEW」。
_EN_SUBTITLE: dict[str, str] = {
    "概览": "OVERVIEW",
    "赛程中心": "SCHEDULE CENTER",
    "实时比赛": "LIVE MATCH",
    "球队": "TEAMS",
    "球员": "PLAYERS",
    "数据分析": "DATA ANALYSIS",
    "积分榜": "STANDINGS",
    "射手榜": "TOP SCORERS",
    "场馆地图": "VENUE MAP",
    "新闻资讯": "NEWS",
    "收藏夹": "FAVORITES",
    "设置": "SETTINGS",
}


def _circle_icon_button(
    glyph: str, tooltip: str, palette: HudPalette, *, diameter: int = 40
) -> QPushButton:
    """圆形玻璃图标按钮（通知铃 / 区域球 等）。"""
    btn = QPushButton(glyph)
    btn.setObjectName("HudIconBtn")
    btn.setCursor(pointing_hand_cursor())
    btn.setFixedSize(diameter, diameter)
    if tooltip:
        btn.setToolTip(tooltip)
    p = palette
    btn.setStyleSheet(
        f"""
QPushButton#HudIconBtn {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: {diameter // 2}px;
    color: {p.text};
    font-size: {Type.H3}px;
}}
QPushButton#HudIconBtn:hover {{
    border: 1px solid {p.glass_border_hi};
    background: {rgba(p.primary, 0.12)};
}}
""".strip()
    )
    return btn


class TopHudBar(QFrame):
    """顶部 HUD 栏。"""

    search_submitted = pyqtSignal(str)
    notifications_clicked = pyqtSignal()
    region_clicked = pyqtSignal()
    profile_clicked = pyqtSignal()

    def __init__(self, palette: HudPalette = NIGHT_STADIUM) -> None:
        super().__init__()
        self.setObjectName("TopHudBar")
        self.setFixedHeight(TOPBAR_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._palette = palette
        p = palette

        outer = QHBoxLayout(self)
        outer.setContentsMargins(28, 10, 28, 10)
        outer.setSpacing(16)

        # ── 标题块 ──
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self._title = QLabel("概览")
        self._title.setObjectName("HudTitle")
        self._title_zh = "概览"
        self._title.setStyleSheet(
            f"QLabel#HudTitle {{ color: {p.text};"
            f" font-size: {Type.H2}px; font-weight: {Type.W_BLACK};"
            f" background: transparent; }}"
        )
        self._subtitle = QLabel("OVERVIEW")
        self._subtitle.setObjectName("HudSubtitle")
        self._subtitle.setStyleSheet(
            f"QLabel#HudSubtitle {{ color: {p.text_dim};"
            f" font-size: {Type.OVERLINE}px; font-weight: {Type.W_BOLD};"
            f" letter-spacing: 2px; background: transparent; }}"
        )
        title_box.addWidget(self._title)
        title_box.addWidget(self._subtitle)
        outer.addLayout(title_box)

        outer.addStretch(1)

        # ── 居中搜索框 ──
        self._search = QLineEdit()
        self._search.setObjectName("HudSearch")
        self._search.setPlaceholderText("搜索球队 / 球员 / 比赛…")
        self._search.setFixedHeight(40)
        self._search.setMinimumWidth(300)
        self._search.setMaximumWidth(420)
        self._search.setClearButtonEnabled(True)
        self._search.setStyleSheet(
            f"""
QLineEdit#HudSearch {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: 20px;
    padding: 0 20px;
    color: {p.text};
    font-size: {Type.BODY}px;
    selection-background-color: {rgba(p.primary, 0.35)};
}}
QLineEdit#HudSearch:focus {{
    border: 1px solid {rgba(p.primary, 0.6)};
    background: {rgba(p.primary, 0.08)};
}}
""".strip()
        )
        self._search.returnPressed.connect(
            lambda: self.search_submitted.emit(self._search.text().strip())
        )
        outer.addWidget(self._search, 2)

        outer.addStretch(1)

        # ── 右侧控件：通知铃 / 区域球(CN) / 头像 ──
        self._bell = _circle_icon_button("🔔", "通知 · 查看最新资讯", p)
        self._bell.clicked.connect(self.notifications_clicked.emit)
        # 未读提醒红点徽标（叠在铃铛右上角）。
        self._bell_badge = QLabel(self._bell)
        self._bell_badge.setObjectName("HudBellBadge")
        self._bell_badge.setFixedSize(9, 9)
        self._bell_badge.move(26, 6)
        self._bell_badge.setStyleSheet(
            f"QLabel#HudBellBadge {{ background: {p.live};"
            f" border: 1.5px solid {p.bg_mid}; border-radius: 4px; }}"
        )
        self._bell_badge.show()
        outer.addWidget(self._bell)

        # 区域地球：地球图标 + 「CN」标签
        self._region = QPushButton("🌐 CN")
        self._region.setObjectName("HudRegion")
        self._region.setCursor(pointing_hand_cursor())
        self._region.setFixedHeight(40)
        self._region.setToolTip("区域 / 语言：中国")
        self._region.setStyleSheet(
            f"""
QPushButton#HudRegion {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: 20px;
    padding: 0 14px;
    color: {p.text};
    font-size: {Type.CAPTION}px;
    font-weight: {Type.W_BOLD};
    letter-spacing: 1px;
}}
QPushButton#HudRegion:hover {{
    border: 1px solid {p.glass_border_hi};
    background: {rgba(p.primary, 0.12)};
}}
""".strip()
        )
        self._region.clicked.connect(self.region_clicked.emit)
        outer.addWidget(self._region)

        # 圆形「设置」按钮（齿轮图标，点击打开设置对话框）
        self._avatar = QPushButton("⚙")
        self._avatar.setObjectName("HudAvatar")
        self._avatar.setCursor(pointing_hand_cursor())
        self._avatar.setFixedSize(40, 40)
        self._avatar.setToolTip("设置")
        self._avatar.setStyleSheet(
            f"""
QPushButton#HudAvatar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {rgba(p.primary, 0.85)}, stop:1 {rgba(p.secondary, 0.85)});
    border: 2px solid {rgba(p.primary_hi, 0.6)};
    border-radius: 20px;
    font-size: {Type.H3}px;
    color: {p.text};
}}
QPushButton#HudAvatar:hover {{
    border: 2px solid {p.primary_hi};
}}
""".strip()
        )
        self._avatar.clicked.connect(self.profile_clicked.emit)
        outer.addWidget(self._avatar)

    # ── 接口（与旧 TopBar 兼容） ──────────────
    def set_title(self, title: str, subtitle: str = "") -> None:
        """设置页面标题与副标题。

        副标题优先用中文标题映射出的英文 OVERLINE（如 概览→OVERVIEW）；
        映射缺失时回退到传入 ``subtitle`` 的首段（按 ``·`` 切分），保证概览页
        恒显示「OVERVIEW」（需求 3.1）。标题本身按当前界面语言翻译。
        """
        from app.i18n import tr
        self._title_zh = title
        self._title.setText(tr(title))
        en = _EN_SUBTITLE.get(title)
        if en is None:
            en = subtitle.split("·")[0].strip() if subtitle else ""
        self._subtitle.setText(en)

    def set_language(self, lang: str) -> None:
        """切换顶栏语言：区域按钮、搜索占位、提示，并按语言重译当前标题。"""
        from app.i18n import tr
        self._region.setText("🌐 EN" if lang == "en" else "🌐 CN")
        self._region.setToolTip(
            "Language: English (click to switch)" if lang == "en"
            else "区域 / 语言：中文（点击切换）")
        self._search.setPlaceholderText(tr("搜索球队 / 球员 / 比赛…"))
        self._bell.setToolTip(tr("通知 · 查看最新资讯"))
        self._avatar.setToolTip(tr("设置"))
        # 以当前标题按新语言重译。
        if getattr(self, "_title_zh", None):
            self.set_title(self._title_zh)

    def set_current_skin(self, name: str) -> None:  # noqa: D401
        """兼容旧壳层调用 —— HUD 色板固定，无操作。"""
        return None

    @property
    def search_text(self) -> str:
        return self._search.text().strip()

    def set_search_text(self, value: str) -> None:
        self._search.setText(value)
