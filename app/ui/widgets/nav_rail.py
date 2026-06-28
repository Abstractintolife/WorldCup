"""nav_rail —— 左侧导航栏（WorldCup 3.0 · 夜间球场 HUD），1:1 复刻设计稿。

在 :class:`GlassCard` + ``hud_theme`` 令牌之上重建（取代旧 ``nav_sidebar``）：

布局（自上而下，对应需求 2.1 / 2.2 / 2.3 / 2.4）
------------------------------------------------
1. **品牌区**：发光大力神杯徽标 + 「WORLD CUP」主标题 + 「FIFA WORLD CUP」副标题。
2. **导航项**：固定 12 项，顺序严格为——
   概览 / 赛程中心 / 实时比赛 / 球队 / 球员 / 数据分析 / 积分榜 / 射手榜 /
   场馆地图 / 新闻资讯 / 收藏夹 / 设置。
   当前页对应项渲染为高亮（active）态，其余为非激活态。
3. **页脚**：「数据同步中… 98%」同步进度 + 「v3.0.0 / WORLD CUP 2026」版本标签。

所有颜色一律取自 :data:`NIGHT_STADIUM` 令牌（不硬编码 hex）。
对外暴露 :pyattr:`selected` 信号（与旧 ``NavSidebar`` 同名），并保留
:meth:`set_active` / :meth:`set_live` / :meth:`apply_palette` 以便 ``MainWindow``
壳层无痛复用。
"""
from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.config import SIDEBAR_WIDTH
from app.ui.design.hud_theme import (
    NIGHT_STADIUM,
    HudPalette,
    Radius,
    Type,
    rgba,
)
from app.ui.widgets.glass_card import GlassCard
from app.ui.design.app_cursor import pointing_hand_cursor


# ════════════════════════════════════════════════════════════════════
#  导航项定义 —— (key, 中文标签, 英文名, 图标)，顺序即设计稿顺序
# ════════════════════════════════════════════════════════════════════
NAV_ITEMS: list[tuple[str, str, str, str]] = [
    ("home",       "概览",     "Overview",       "📊"),
    ("schedule",   "赛程中心", "Schedule Center", "📅"),
    ("live",       "实时比赛", "Live Match",     "📡"),
    ("teams",      "球队",     "Teams",          "🛡"),
    ("players",    "球员",     "Players",        "👤"),
    ("analysis",   "数据分析", "Data Analysis",  "📈"),
    ("probability", "概率预测", "Predictions",    "🔮"),
    ("bracket",     "对阵图",   "Bracket",        "🧩"),
    ("standings",  "积分榜",   "Standings",      "🏆"),
    ("scorers",    "射手榜",   "Top Scorers",    "⚽"),
    ("venue",      "场馆地图", "Venue Map",      "🗺"),
    ("news",       "新闻资讯", "News",           "📰"),
    ("favorites",  "收藏夹",   "Favorites",      "⭐"),
    ("settings",   "设置",     "Settings",       "⚙"),
]

# 哪些条目是「直播」入口（LIVE 徽章动态点亮）
_LIVE_KEYS = ("live",)


# ════════════════════════════════════════════════════════════════════
#  单个导航项
# ════════════════════════════════════════════════════════════════════
class NavRailItem(QFrame):
    """单个导航行：左侧高亮竖条 + 图标 + 中文标签 + 可选 LIVE 徽章。

    激活态由 :meth:`set_active` 驱动（``active`` 动态属性 + QSS 重抛光），
    便于无 GUI 渲染断言（测试只需读 :pyattr:`is_active`）。
    """

    clicked = pyqtSignal(str)

    def __init__(
        self,
        key: str,
        label_zh: str,
        label_en: str,
        icon: str,
        palette: HudPalette = NIGHT_STADIUM,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._key = key
        self._label_zh = label_zh
        self._label_en = label_en
        self._palette = palette
        self._active = False

        self.setObjectName("NavRailItem")
        self.setProperty("active", False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(pointing_hand_cursor())
        self.setFixedHeight(44)
        self.setToolTip(f"{label_zh} · {label_en}")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 14, 0)
        lay.setSpacing(12)

        self._icon = QLabel(icon)
        self._icon.setObjectName("NavIcon")
        self._icon.setFixedWidth(20)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._icon)

        self._text = QLabel(label_zh)
        self._text.setObjectName("NavLabel")
        lay.addWidget(self._text, 1)

        # LIVE 徽章（仅「实时比赛」等入口在确有直播时点亮）
        self._badge = QLabel("LIVE")
        self._badge.setObjectName("NavLiveBadge")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.hide()
        lay.addWidget(self._badge)

        self._apply_style()

    # ── 样式 ───────────────────────────────
    def _apply_style(self) -> None:
        p = self._palette
        active = self._active
        bg = rgba(p.primary, 0.16) if active else "transparent"
        bar = p.primary if active else "transparent"
        txt = p.text if active else p.text_dim
        icon_col = p.primary_hi if active else p.text_dim
        weight = Type.W_BOLD if active else Type.W_MEDIUM
        self.setStyleSheet(
            f"""
QFrame#NavRailItem {{
    background: {bg};
    border: none;
    border-left: 3px solid {bar};
    border-top-right-radius: {Radius.CHIP}px;
    border-bottom-right-radius: {Radius.CHIP}px;
}}
QFrame#NavRailItem:hover {{
    background: {rgba(p.primary, 0.16) if active else rgba(p.text, 0.06)};
}}
QLabel#NavLabel {{
    color: {txt};
    font-size: {Type.BODY}px;
    font-weight: {weight};
    background: transparent;
}}
QLabel#NavIcon {{
    color: {icon_col};
    font-size: {Type.H3}px;
    background: transparent;
}}
QLabel#NavLiveBadge {{
    color: {p.text};
    background: {rgba(p.live, 0.9)};
    border-radius: 8px;
    padding: 1px 7px;
    font-size: {Type.OVERLINE}px;
    font-weight: {Type.W_BOLD};
}}
""".strip()
        )

    # ── 激活态 ──────────────────────────────
    def set_active(self, active: bool) -> None:
        active = bool(active)
        if active == self._active:
            return
        self._active = active
        self.setProperty("active", active)
        self._apply_style()
        self.update()

    def set_badge_visible(self, on: bool) -> None:
        self._badge.setVisible(bool(on))

    def apply_palette(self, palette: HudPalette) -> None:
        self._palette = palette
        self._apply_style()

    def set_language(self, lang: str) -> None:
        """切换导航项语言（中文 / 英文）。"""
        self._text.setText(self._label_en if lang == "en" else self._label_zh)
        self.setToolTip(f"{self._label_zh} · {self._label_en}")

    # ── 查询 ────────────────────────────────
    @property
    def key(self) -> str:
        return self._key

    @property
    def label(self) -> str:
        return self._label_zh

    @property
    def is_active(self) -> bool:
        return self._active

    # ── 交互 ────────────────────────────────
    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._key)
        super().mousePressEvent(ev)


# ════════════════════════════════════════════════════════════════════
#  品牌区徽标
# ════════════════════════════════════════════════════════════════════
class _BrandLogo(QWidget):
    """发光大力神杯徽标 + 「WORLD CUP / FIFA WORLD CUP」标题。"""

    def __init__(
        self, palette: HudPalette = NIGHT_STADIUM, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("BrandLogo")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        p = palette

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 4, 16, 4)
        lay.setSpacing(12)

        # 奖杯标记（发光）
        trophy = QLabel("🏆")
        trophy.setObjectName("BrandTrophy")
        trophy.setFixedSize(40, 40)
        trophy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trophy.setStyleSheet(
            f"QLabel#BrandTrophy {{"
            f" font-size: 24px;"
            f" background: {rgba(p.accent, 0.14)};"
            f" border: 1px solid {rgba(p.accent, 0.45)};"
            f" border-radius: {Radius.CHIP}px;"
            f" }}"
        )
        glow = QGraphicsDropShadowEffect(trophy)
        glow.setBlurRadius(24)
        glow.setOffset(0, 0)
        gc = QColor(p.accent)
        gc.setAlphaF(0.8)
        glow.setColor(gc)
        trophy.setGraphicsEffect(glow)
        lay.addWidget(trophy)

        col = QVBoxLayout()
        col.setSpacing(1)
        title = QLabel("WORLD CUP")
        title.setObjectName("BrandTitle")
        title.setStyleSheet(
            f"QLabel#BrandTitle {{ color: {p.text};"
            f" font-size: {Type.H3}px; font-weight: {Type.W_BLACK};"
            f" letter-spacing: 1px; background: transparent; }}"
        )
        # 主标题发光（HUD 薄荷青）
        tglow = QGraphicsDropShadowEffect(title)
        tglow.setBlurRadius(18)
        tglow.setOffset(0, 0)
        pc = QColor(p.primary)
        pc.setAlphaF(0.7)
        tglow.setColor(pc)
        title.setGraphicsEffect(tglow)
        col.addWidget(title)

        sub = QLabel("FIFA WORLD CUP")
        sub.setObjectName("BrandSub")
        sub.setStyleSheet(
            f"QLabel#BrandSub {{ color: {p.accent};"
            f" font-size: {Type.OVERLINE}px; font-weight: {Type.W_BOLD};"
            f" letter-spacing: 2px; background: transparent; }}"
        )
        col.addWidget(sub)
        lay.addLayout(col)
        lay.addStretch(1)


# ════════════════════════════════════════════════════════════════════
#  页脚（同步进度 + 版本）
# ════════════════════════════════════════════════════════════════════
class _RailFooter(QWidget):
    """页脚：同步进度条 + 「数据同步中… NN%」+ 版本标签。"""

    def __init__(
        self, palette: HudPalette = NIGHT_STADIUM, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("RailFooter")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        p = palette
        self._palette = p
        self._connected = True

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 10, 18, 6)
        lay.setSpacing(6)

        # 实时数据状态行：脉冲圆点 + 文案（取代旧的「数据同步中… 98%」假进度）。
        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(7)
        self._dot = QLabel("●")
        self._dot.setObjectName("SyncDot")
        self._dot.setStyleSheet(
            f"QLabel#SyncDot {{ color: {p.win};"
            f" font-size: {Type.CAPTION}px; background: transparent; }}"
        )
        status_row.addWidget(self._dot)
        self._sync_label = QLabel("实时数据 · 已连接")
        self._sync_label.setObjectName("SyncLabel")
        self._sync_label.setStyleSheet(
            f"QLabel#SyncLabel {{ color: {p.win};"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD};"
            f" background: transparent; }}"
        )
        status_row.addWidget(self._sync_label)
        status_row.addStretch(1)
        lay.addLayout(status_row)

        self._bar = QProgressBar()
        self._bar.setObjectName("SyncBar")
        self._bar.setRange(0, 100)
        self._bar.setValue(100)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(4)
        self._bar.setStyleSheet(
            f"""
QProgressBar#SyncBar {{
    background: {rgba(p.text, 0.08)};
    border: none;
    border-radius: 2px;
}}
QProgressBar#SyncBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {p.win}, stop:1 {p.primary_hi});
    border-radius: 2px;
}}
""".strip()
        )
        lay.addWidget(self._bar)

        self._version = QLabel("v3.0.0 / WORLD CUP 2026")
        self._version.setObjectName("VersionLabel")
        self._version.setStyleSheet(
            f"QLabel#VersionLabel {{ color: {p.text_faint};"
            f" font-size: {Type.OVERLINE}px; font-weight: {Type.W_MEDIUM};"
            f" letter-spacing: 1px; background: transparent; }}"
        )
        lay.addWidget(self._version)

    def set_sync_progress(self, percent: int) -> None:
        """历史兼容：仍接受同步百分比（更新进度条），文案改为实时状态语义。"""
        percent = max(0, min(100, int(percent)))
        self._bar.setValue(percent)

    def set_realtime(self, connected: bool) -> None:
        """切换实时数据连接态：绿色「实时数据 · 已连接」/ 红色「实时数据 · 连接中断」。"""
        self._connected = bool(connected)
        from app.i18n import tr
        p = self._palette
        col = p.win if connected else p.loss
        text = (tr("实时数据 · 已连接", "Live data · connected") if connected
                else tr("实时数据 · 连接中断", "Live data · disconnected"))
        self._dot.setStyleSheet(
            f"QLabel#SyncDot {{ color: {col};"
            f" font-size: {Type.CAPTION}px; background: transparent; }}"
        )
        self._sync_label.setText(text)
        self._sync_label.setStyleSheet(
            f"QLabel#SyncLabel {{ color: {col};"
            f" font-size: {Type.CAPTION}px; font-weight: {Type.W_BOLD};"
            f" background: transparent; }}"
        )
        self._bar.setValue(100 if connected else 30)
        self._bar.setStyleSheet(
            f"""
QProgressBar#SyncBar {{
    background: {rgba(p.text, 0.08)};
    border: none;
    border-radius: 2px;
}}
QProgressBar#SyncBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {col}, stop:1 {p.primary_hi if connected else col});
    border-radius: 2px;
}}
""".strip()
        )

    def set_language(self, lang: str) -> None:
        """语言切换：以当前连接态重新渲染本地化文案。"""
        self.set_realtime(getattr(self, "_connected", True))


# ════════════════════════════════════════════════════════════════════
#  导航栏
# ════════════════════════════════════════════════════════════════════
class NavRail(GlassCard):
    """夜间球场 HUD 左侧导航栏（玻璃面板）。"""

    selected = pyqtSignal(str)

    def __init__(
        self,
        items: Iterable[tuple[str, str, str, str]] | None = None,
        palette: HudPalette = NIGHT_STADIUM,
        parent: QWidget | None = None,
    ) -> None:
        # 整条导航栏是一块玻璃面板：禁用悬停浮起、零内边距（内部自管）。
        super().__init__(parent, hover=False, palette=palette, padding=0)
        self.setObjectName("NavRail")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self._palette = palette

        items = list(items) if items is not None else list(NAV_ITEMS)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 16, 8, 8)
        root.setSpacing(4)

        # ── 品牌区 ──
        root.addWidget(_BrandLogo(palette))

        # 分隔线
        sep = QFrame()
        sep.setProperty("hr", True)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {rgba(palette.text, 0.08)}; border: none;")
        root.addSpacing(8)
        root.addWidget(sep)
        root.addSpacing(8)

        # ── 导航项 ──
        self._rows: dict[str, NavRailItem] = {}
        self._order: list[str] = []
        self._live_keys: list[str] = []
        for key, zh, en, icon in items:
            row = NavRailItem(key, zh, en, icon, palette=palette)
            row.clicked.connect(self._on_row_clicked)
            root.addWidget(row)
            self._rows[key] = row
            self._order.append(key)
            if key in _LIVE_KEYS:
                self._live_keys.append(key)

        root.addStretch(1)

        # 页脚分隔
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {rgba(palette.text, 0.08)}; border: none;")
        root.addWidget(sep2)

        # ── 页脚 ──
        self._footer = _RailFooter(palette)
        root.addWidget(self._footer)

        self._active_key: str | None = None

    # ── 交互 ────────────────────────────────
    def _on_row_clicked(self, key: str) -> None:
        # 统一处理高亮；真正的页面切换由 MainWindow 在 selected 槽里决定。
        self.set_active(key)
        self.selected.emit(key)

    def set_active(self, key: str) -> None:
        """高亮 ``key`` 对应导航项，其余置为非激活（需求 2.3）。"""
        if key not in self._rows:
            return
        for k, row in self._rows.items():
            row.set_active(k == key)
        self._active_key = key

    # ── 直播徽章 ─────────────────────────────
    def set_live(self, on: bool) -> None:
        """有比赛进行中时点亮「实时比赛」入口的 LIVE 徽章。"""
        for key in self._live_keys:
            row = self._rows.get(key)
            if row is not None:
                row.set_badge_visible(bool(on))

    # ── 同步进度 ─────────────────────────────
    def set_sync_progress(self, percent: int) -> None:
        self._footer.set_sync_progress(percent)

    def set_realtime(self, connected: bool) -> None:
        """更新页脚实时数据连接状态（绿色已连接 / 红色中断）。"""
        self._footer.set_realtime(connected)

    def set_language(self, lang: str) -> None:
        """切换整条导航栏的语言（导航项 + 页脚状态文案）。"""
        for row in self._rows.values():
            row.set_language(lang)
        self._footer.set_language(lang)

    # ── 主题（HUD 固定 NIGHT_STADIUM；保留接口以兼容壳层调用） ──
    def apply_palette(self, palette=None) -> None:  # noqa: D401
        """兼容 ``MainWindow`` 旧调用。HUD 色板固定，旧主题色板被忽略。"""
        for row in self._rows.values():
            row.apply_palette(self._palette)
        self.update()

    # ── 查询（供测试 / 壳层） ─────────────────
    @property
    def active_key(self) -> str | None:
        return self._active_key

    def nav_keys(self) -> list[str]:
        return list(self._order)

    def nav_labels(self) -> list[str]:
        return [self._rows[k].label for k in self._order]

    def item(self, key: str) -> NavRailItem | None:
        return self._rows.get(key)

    def active_items(self) -> list[str]:
        """当前处于高亮态的所有项 key（正常情况下至多一个）。"""
        return [k for k, row in self._rows.items() if row.is_active]
