"""主题系统：调色板 + 全局 QSS 样式表。

「2026 FIFA 世界杯 · 商业级设计语言」V3.0
=========================================
参考 EA Sports FC / OneFootball / 世界杯官方 App 的现代化桌面客户端风格：

* 主背景 ``#0B1020`` —— 深邃球场夜空（顶部 ``#08111E`` → 底部 ``#0F2745`` 渐变）。
* 卡片 —— 毛玻璃质感（``rgba(255,255,255,0.08)`` 底 + ``rgba(255,255,255,0.15)`` 白边）。
* 核心配色：
    - 主色 电光蓝 ``#00BFFF``（PRIMARY_BLUE，按钮 / 高亮 / 选中态）
    - 辅色 皇家紫 ``#6A5ACD``（SECONDARY_PURPLE，光晕 / 渐变）
    - 点缀 大力神杯金 ``#FFD700``（GOLD，荣誉 / 强调）
    - 绿茵翠绿 ``#1B5E20`` / ``#2ED877``（球场 / 胜势）

精简皮肤为三套（对应 StageCompositor 的夜间球场场景）：
    深蓝世界杯（默认）/ 黑金冠军 / 绿茵赛场。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtGui import QColor

from app.ui.design.hud_theme import NIGHT_STADIUM


# ─── 设计令牌（供模块外引用） ─────────────────────────────────
PRIMARY_BLUE = "#00BFFF"
SECONDARY_PURPLE = "#6A5ACD"
FIELD_GREEN = "#1B5E20"
GOLD = "#FFD700"
BACKGROUND = "#0B1020"


@dataclass(frozen=True)
class ThemePalette:
    """一套主题配色。"""

    name: str

    # 基础色
    bg: str
    bg_elevated: str        # 卡片背景
    bg_hover: str
    bg_sidebar: str
    bg_topbar: str
    surface: str            # 表面色（弹窗等）
    border: str
    divider: str

    # 文本
    text: str
    text_dim: str
    text_faint: str
    text_inverse: str

    # 强调色
    primary: str            # 主品牌色（按钮 / 高亮 / 选中态）
    primary_hover: str
    primary_press: str
    primary_soft: str       # primary 的低饱和柔光（透明）
    secondary: str          # 辅助色（紫 / 光晕）
    accent: str             # 大力神杯金

    # 语义色
    success: str            # 胜
    warning: str            # 平
    danger: str             # 负
    live: str               # 直播红

    # hero 渐变（人物海报背景）
    hero_grad_a: str
    hero_grad_b: str
    hero_grad_c: str

    # 玻璃材质（自定义绘制用）
    glass_top: str = "rgba(255,255,255,0.08)"
    glass_bottom: str = "rgba(255,255,255,0.02)"
    glass_border: str = "rgba(255,255,255,0.15)"
    glass_border_strong: str = "rgba(0,191,255,0.35)"

    # 该皮肤对应的「动态背景场景」标识（SkinBackdrop 据此渲染不同动效）
    scene: str = "worldcup"
    # 侧栏 / 顶栏的半透明玻璃底（让动态背景能透出来）
    chrome_glass: str = "rgba(8,14,28,0.66)"

    # 排名组别染色（A-L 共 12 组）
    group_colors: tuple[str, ...] = field(
        default_factory=lambda: (
            "#00BFFF",  # 电光蓝 A
            "#36D1FF",  # 浅蓝 B
            "#5BC8FF",  # 天蓝 C
            "#2ED877",  # 翠绿 D
            "#00D4A4",  # 青绿 E
            "#7CE0C0",  # 薄荷 F
            "#6A5ACD",  # 皇家紫 G
            "#8E7CFF",  # 浅紫 H
            "#B79BFF",  # 雾紫 I
            "#FFD700",  # 金 J
            "#FFC04D",  # 琥珀 K
            "#FF8FB1",  # 樱粉 L
        )
    )

    def color(self, attr: str) -> QColor:
        return QColor(getattr(self, attr))

    def group_color(self, name: str) -> QColor:
        """根据组名（"A组" / "I组"）返回该组的强调色。"""
        if not name:
            return QColor(self.primary)
        ch = name[0].upper()
        idx = ord(ch) - ord("A")
        if 0 <= idx < len(self.group_colors):
            return QColor(self.group_colors[idx])
        return QColor(self.primary)


# ════════════════════════════════════════════════════════════════════
#  🌃 深蓝世界杯（默认）—— 电光蓝 × 皇家紫 × 大力神杯金
# ════════════════════════════════════════════════════════════════════
DARK = ThemePalette(
    name="dark",
    bg="#0B1020",
    bg_elevated="#141B33",
    bg_hover="#1B2342",
    bg_sidebar="#080E1C",
    bg_topbar="#0B1020",
    surface="#141B33",
    border="rgba(255,255,255,0.15)",
    divider="rgba(255,255,255,0.06)",
    text="#FFFFFF",
    text_dim="#B0BEC5",
    text_faint="#6B7689",
    text_inverse="#0B1020",
    primary="#00BFFF",
    primary_hover="#46D2FF",
    primary_press="#0092C8",
    primary_soft="rgba(0,191,255,0.18)",
    secondary="#6A5ACD",
    accent="#FFD700",
    success="#2ED877",
    warning="#FFC857",
    danger="#FF5470",
    live="#FF3057",
    hero_grad_a="#08111E",
    hero_grad_b="#13294B",
    hero_grad_c="#0B1020",
    glass_top="rgba(255,255,255,0.08)",
    glass_bottom="rgba(255,255,255,0.02)",
    glass_border="rgba(255,255,255,0.15)",
    glass_border_strong="rgba(0,191,255,0.38)",
    scene="worldcup",
    chrome_glass="rgba(8,13,26,0.68)",
)

# ════════════════════════════════════════════════════════════════════
#  🏆 黑金冠军 —— 焦黑底 + 大力神杯金，至高荣誉
# ════════════════════════════════════════════════════════════════════
GOLD_THEME = ThemePalette(
    name="gold",
    bg="#0C0A06",
    bg_elevated="#1A150B",
    bg_hover="#241D0F",
    bg_sidebar="#080703",
    bg_topbar="#0C0A06",
    surface="#1A150B",
    border="rgba(255,215,0,0.18)",
    divider="rgba(255,215,0,0.08)",
    text="#FFF8E7",
    text_dim="#C9B891",
    text_faint="#897A56",
    text_inverse="#0C0A06",
    primary="#FFD700",
    primary_hover="#FFE680",
    primary_press="#C8A400",
    primary_soft="rgba(255,215,0,0.16)",
    secondary="#FF9D2E",
    accent="#FFE680",
    success="#9ED84D",
    warning="#FFC857",
    danger="#FF6B6B",
    live="#FF5A2E",
    hero_grad_a="#1A1206",
    hero_grad_b="#3A2A08",
    hero_grad_c="#0C0A06",
    glass_top="rgba(255,225,140,0.07)",
    glass_bottom="rgba(255,225,140,0.02)",
    glass_border="rgba(255,215,0,0.20)",
    glass_border_strong="rgba(255,215,0,0.42)",
    scene="gold",
    chrome_glass="rgba(10,8,4,0.70)",
)

# ════════════════════════════════════════════════════════════════════
#  🌱 绿茵赛场 —— 草地翠绿 + 体育场灯光
# ════════════════════════════════════════════════════════════════════
PITCH = ThemePalette(
    name="pitch",
    bg="#04140C",
    bg_elevated="#0B2417",
    bg_hover="#123320",
    bg_sidebar="#03100A",
    bg_topbar="#04140C",
    surface="#0B2417",
    border="rgba(120,255,170,0.16)",
    divider="rgba(120,255,170,0.07)",
    text="#EAFBEF",
    text_dim="#8FC4A4",
    text_faint="#5A856B",
    text_inverse="#04140C",
    primary="#2FE36B",
    primary_hover="#6BF59B",
    primary_press="#18A24A",
    primary_soft="rgba(47,227,107,0.18)",
    secondary="#00BFFF",
    accent="#FFD700",
    success="#2FE36B",
    warning="#FFD36E",
    danger="#FF6B6B",
    live="#FF5A5A",
    hero_grad_a="#04210F",
    hero_grad_b="#0B5A2C",
    hero_grad_c="#04140C",
    glass_top="rgba(120,255,170,0.07)",
    glass_bottom="rgba(120,255,170,0.02)",
    glass_border="rgba(120,255,170,0.18)",
    glass_border_strong="rgba(120,255,170,0.40)",
    scene="field",
    chrome_glass="rgba(4,18,11,0.68)",
)

THEMES: dict[str, ThemePalette] = {
    "dark": DARK,
    "gold": GOLD_THEME,
    "pitch": PITCH,
}

# 皮肤切换菜单的展示顺序与元信息：name -> (中文名, emoji, 一句话简介)
THEME_ORDER: tuple[str, ...] = ("dark", "gold", "pitch")
THEME_META: dict[str, tuple[str, str, str]] = {
    "dark": ("深蓝世界杯", "🌃", "电光蓝 · 聚光灯粒子"),
    "gold": ("黑金冠军", "🏆", "焦黑底 · 大力神杯金"),
    "pitch": ("绿茵赛场", "🌱", "翠绿草地 · 体育场灯光"),
}


def build_qss(t: ThemePalette) -> str:
    """根据当前主题生成全局 QSS。

    放在一起便于一次性 setStyleSheet，避免控件内零散硬编码颜色。
    毛玻璃用「微弱白边 + 极淡顶亮渐变」模拟（真正的背景模糊由
    SkinBackdrop 的动态场景 + 卡片半透明叠加承担）。
    """
    return f"""
    /* ────────── 全局 ────────── */
    QWidget {{
        color: {t.text};
        background-color: {t.bg};
        font-family: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC",
                     "Hiragino Sans GB", "Noto Sans CJK SC", "Source Han Sans SC",
                     "Segoe UI", "Inter", "Helvetica Neue", "Arial", sans-serif;
        font-size: 14px;
    }}

    /* QLabel 默认透明 —— 否则会继承上面 QWidget 的 background-color，
       在 hero 渐变 / 卡片彩色背景上显示为「丑陋的黑色方块」。
       需要底色的标签（状态徽章 / 胶囊）各自显式设置 background，
       其选择器更具体，不受此规则影响。 */
    QLabel {{
        background: transparent;
    }}

    QToolTip {{
        background-color: {t.surface};
        color: {t.text};
        border: 1px solid {t.glass_border_strong};
        padding: 6px 10px;
        border-radius: 8px;
    }}

    QStatusBar {{ background: {t.bg_topbar}; color: {t.text_dim}; }}
    QStatusBar::item {{ border: none; }}

    /* ────────── 滚动条 ────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 12px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(255,255,255,0.13);
        border-radius: 6px;
        min-height: 42px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {t.primary}, stop:1 {t.primary_hover});
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0; background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
    QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px 4px; }}
    QScrollBar::handle:horizontal {{
        background: rgba(255,255,255,0.13); border-radius: 6px; min-width: 42px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {t.primary}, stop:1 {t.primary_hover});
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0; background: none;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

    /* ────────── 文本输入 ────────── */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: rgba(255,255,255,0.05);
        border: 1px solid {t.glass_border};
        border-radius: 14px;
        padding: 9px 16px;
        color: {t.text};
        selection-background-color: {t.primary};
        selection-color: #ffffff;
    }}
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
        border: 1px solid {t.glass_border_strong};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {t.primary};
        background: rgba(255,255,255,0.07);
    }}

    /* ────────── 按钮 ────────── */
    QPushButton {{
        background-color: rgba(255,255,255,0.05);
        color: {t.text};
        border: 1px solid {t.glass_border};
        border-radius: 13px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: rgba(255,255,255,0.11);
        border: 1px solid {t.glass_border_strong};
        color: {t.text};
    }}
    QPushButton:pressed {{
        background-color: rgba(255,255,255,0.05);
        padding-top: 10px; padding-bottom: 8px;
    }}
    QPushButton:disabled {{ color: {t.text_faint}; border-color: {t.divider}; }}

    QPushButton[primary="true"] {{
        background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 {t.primary}, stop:1 {t.secondary});
        color: #ffffff;
        border: 1px solid {t.primary_hover};
        font-weight: 800;
        letter-spacing: 0.3px;
        padding: 10px 22px;
    }}
    QPushButton[primary="true"]:hover {{
        background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 {t.primary_hover}, stop:1 {t.secondary});
        border: 1px solid {t.primary_hover};
    }}
    QPushButton[primary="true"]:pressed {{
        background-color: {t.primary_press};
        padding-top: 11px; padding-bottom: 9px;
    }}

    QPushButton[ghost="true"] {{
        background: transparent;
        border: none;
        color: {t.text_dim};
        padding: 8px 15px;
        border-radius: 12px;
        font-weight: 600;
    }}
    QPushButton[ghost="true"]:hover {{
        color: {t.text};
        background: rgba(255,255,255,0.08);
    }}

    /* 顶部栏圆形图标按钮 */
    QPushButton[iconBtn="true"] {{
        background: rgba(255,255,255,0.05);
        border: 1px solid {t.glass_border};
        border-radius: 18px;
        padding: 0;
        font-size: 16px;
        min-width: 36px; min-height: 36px;
        max-width: 36px; max-height: 36px;
        color: {t.text_dim};
    }}
    QPushButton[iconBtn="true"]:hover {{
        background: rgba(255,255,255,0.10);
        color: {t.primary};
        border: 1px solid {t.primary};
    }}
    /* 隐藏带菜单的图标按钮（皮肤切换）右下角的下拉箭头 */
    QPushButton[iconBtn="true"]::menu-indicator {{
        image: none; width: 0; height: 0;
    }}

    /* ────────── 选择框 ────────── */
    QComboBox {{
        background: rgba(255,255,255,0.05);
        border: 1px solid {t.glass_border};
        border-radius: 13px;
        padding: 8px 16px;
        color: {t.text};
        min-width: 100px;
        font-weight: 600;
    }}
    QComboBox:hover {{ border: 1px solid {t.glass_border_strong}; background: rgba(255,255,255,0.08); }}
    QComboBox:focus {{ border: 1px solid {t.primary}; }}
    QComboBox::drop-down {{ width: 26px; border: none; }}
    QComboBox QAbstractItemView {{
        background: {t.surface};
        border: 1px solid {t.glass_border_strong};
        border-radius: 12px;
        selection-background-color: {t.primary};
        selection-color: #ffffff;
        outline: 0;
        padding: 6px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 30px; border-radius: 8px; padding: 2px 8px;
    }}

    /* ────────── 选项卡 ────────── */
    QTabWidget::pane {{ border: none; }}
    QTabBar::tab {{
        background: transparent;
        color: {t.text_dim};
        padding: 11px 22px;
        margin-right: 6px;
        border-bottom: 2px solid transparent;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
    QTabBar::tab:selected {{
        color: {t.text};
        border-bottom: 2px solid {t.primary};
        font-weight: 800;
    }}
    QTabBar::tab:hover {{ color: {t.text}; }}

    /* ────────── 通用「卡片」类 ────────── */
    QFrame#Card, QFrame#GlassCard {{
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {t.glass_top}, stop:1 {t.glass_bottom});
        border: 1px solid {t.glass_border};
        border-radius: 20px;
    }}
    QFrame#Card:hover, QFrame#GlassCard:hover {{
        border: 1px solid {t.glass_border_strong};
    }}

    /* 大标题/段落标题 —— 排版层级 */
    QLabel[h1="true"] {{ font-size: 32px; font-weight: 900; color: {t.text}; letter-spacing: 0.2px; }}
    QLabel[h2="true"] {{ font-size: 22px; font-weight: 800; color: {t.text}; letter-spacing: 0.2px; }}
    QLabel[h3="true"] {{ font-size: 16px; font-weight: 700; color: {t.text}; }}
    QLabel[overline="true"] {{
        font-size: 11px; font-weight: 800; color: {t.text_dim};
        letter-spacing: 1.6px;
    }}
    QLabel[muted="true"] {{ color: {t.text_dim}; }}
    QLabel[faint="true"] {{ color: {t.text_faint}; }}
    QLabel[accent="true"] {{ color: {t.accent}; font-weight: 700; }}
    QLabel[primary="true"] {{ color: {t.primary}; font-weight: 700; }}

    /* ────────── 侧边栏导航 ────────── */
    QFrame#Sidebar {{
        background: {t.chrome_glass};
        border-right: 1px solid {t.glass_border};
    }}
    /* 自定义导航行（NavRow）样式由 navItem QSS 接管 */
    QPushButton[navItem="true"] {{
        background: transparent;
        color: #b8c0d8;
        text-align: left;
        padding: 11px 18px 11px 22px;
        border: none;
        border-radius: 12px;
        font-size: 14px;
        margin: 3px 14px;
        font-weight: 600;
    }}
    QPushButton[navItem="true"]:hover {{
        background: rgba(255,255,255,0.07);
        color: #ffffff;
    }}
    QPushButton[navItem="true"][active="true"] {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {t.primary_soft}, stop:1 rgba(255,255,255,0.0));
        color: #ffffff;
        font-weight: 800;
        border-left: 3px solid {t.primary};
        padding-left: 19px;
    }}

    /* ────────── TopBar ────────── */
    QFrame#TopBar {{
        background: {t.chrome_glass};
        border-bottom: 1px solid {t.glass_border};
    }}
    /* 顶部胶囊搜索框 —— 高 48px / 圆角 50px / 聚焦蓝色光晕 */
    QFrame#TopBar QLineEdit {{
        background: rgba(255,255,255,0.05);
        border: 1px solid {t.glass_border};
        border-radius: 24px;
        padding: 10px 22px;
        min-height: 26px;
        max-height: 26px;
        font-size: 12.5px;
    }}
    QFrame#TopBar QLineEdit:focus {{
        border: 1px solid {t.primary};
        background: {t.primary_soft};
    }}

    /* ────────── 状态徽章 ────────── */
    QLabel[chip="live"] {{
        background: {t.live}; color: white;
        border-radius: 9px; padding: 2px 9px;
        font-size: 11px; font-weight: 800;
    }}
    QLabel[chip="finished"] {{
        background: rgba(255,255,255,0.10); color: {t.text_dim};
        border-radius: 9px; padding: 2px 9px;
        font-size: 11px; font-weight: 700;
    }}
    QLabel[chip="upcoming"] {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 {t.primary}, stop:1 {t.secondary});
        color: white;
        border-radius: 9px; padding: 2px 9px;
        font-size: 11px; font-weight: 800;
    }}

    /* 表格 */
    QTableWidget, QTableView {{
        background: transparent;
        gridline-color: {t.divider};
        selection-background-color: {t.primary_soft};
        selection-color: {t.text};
        border: none;
    }}
    QHeaderView::section {{
        background: transparent;
        color: {t.text_dim};
        border: none;
        border-bottom: 1px solid {t.glass_border};
        padding: 9px;
        font-weight: 700;
    }}
    QTableView::item {{ padding: 6px; }}

    /* 分隔线 */
    QFrame[hr="true"] {{
        background: {t.divider}; max-height: 1px; min-height: 1px; border: none;
    }}

    /* ────────── 动态背景透出层 ──────────
       性能权衡：动态背景（SkinBackdrop）若透过整页内容，会导致每一动效帧
       都要重新合成整棵内容树 —— 在长列表（如射手榜 60+ 行）上极其卡顿。
       因此页面正文（PageContent）改为「不透明实色底」：动效背景只在侧栏 /
       顶栏（半透明 chrome_glass）背后透出，正文滚动因而稳定流畅；卡片自身
       的半透明玻璃底叠在实色背景上，依旧是「悬浮玻璃」观感。 */
    QStackedWidget {{ background: transparent; }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollArea > QWidget#qt_scrollarea_viewport {{ background: transparent; }}
    QScrollArea > QWidget#qt_scrollarea_viewport > QWidget {{
        background: transparent;
    }}
    QWidget#PageRoot {{ background: transparent; }}
    QWidget#PageContent {{ background: {t.bg}; }}
    /* 新 HUD 页面（如概览页）滚动正文不透明底 —— 需求 16.5：避免 GPU 合成器
       每帧重合成整棵控件树；色值取 hud_theme 的 bg_opaque_body 令牌。 */
    QWidget#OpaqueBody {{ background: {NIGHT_STADIUM.bg_opaque_body}; }}
    QWidget#ContentHost {{ background: transparent; }}
    """
