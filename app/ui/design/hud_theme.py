"""hud_theme —— "Night Stadium Futuristic HUD" 设计令牌系统（WorldCup 3.0）。

这是整套「夜间球场 HUD」视觉语言的**单一事实来源**（single source of truth）：
颜色渐变、HUD 强调色、语义色、文字层级、玻璃材质、圆角、阴影、字体规格。
它取代旧的 sakura/pink/purple 多皮肤调色板（``theme.py`` palette）与
``tokens.py`` 中的颜色相关令牌；结构性令牌（8pt 间距、时长、缓动）仍由
``tokens.py`` 负责，两者互补。

设计要点
--------
* 控件**永不硬编码 hex** —— 一律经 :func:`rgba` / :func:`mix` 派生颜色，
  或直接引用 :data:`NIGHT_STADIUM` 上的命名令牌。
* :func:`build_qss` 产出全局 QSS，统一 HUD 外观。

对应需求：16.2（夜间渐变底色）、20.1（玻璃卡材质）。
"""
from __future__ import annotations

from dataclasses import dataclass


# ════════════════════════════════════════════════════════════════════
#  调色板 —— Night Stadium HUD
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class HudPalette:
    """不可变的「夜间球场」调色板。

    所有字段都是命名令牌；颜色以 ``#RRGGBB`` 或 ``rgba(r,g,b,a)`` 字符串表达，
    便于直接拼进 QSS 或经 :func:`rgba` / :func:`mix` 派生。
    """

    name: str = "night-stadium"

    # ── 背景渐变（垂直「球场之夜」渐变） ──
    bg_top: str = "#06111A"          # 夜空
    bg_mid: str = "#0A1B28"          # 中场雾霭
    bg_bottom: str = "#0F2A1F"       # 草皮墨绿
    bg_opaque_body: str = "#081420"  # 滚动正文不透明底（性能用）

    # ── HUD 强调色 ──
    primary: str = "#19E3B5"         # HUD 薄荷青（选中 / 焦点 / 实时数据）
    primary_hi: str = "#5FF4D0"
    secondary: str = "#2D7DF6"       # 转播蓝（链接 / 次级）
    accent: str = "#FFC23D"          # 奖杯金（荣誉 / 强调）
    floodlight: str = "#EAF6FF"      # 冷白泛光灯色调

    # ── 语义色 ──
    win: str = "#2ED877"
    draw: str = "#FFC857"
    loss: str = "#FF5470"
    live: str = "#FF2D55"            # 转播直播红

    # ── 文字层级 ──
    text: str = "#F2F7FA"
    text_dim: str = "#9FB2C0"
    text_faint: str = "#5C7180"

    # ── 玻璃材质 ──
    glass_fill: str = "rgba(255,255,255,0.05)"
    glass_border: str = "rgba(255,255,255,0.08)"
    glass_border_hi: str = "rgba(25,227,181,0.35)"


# 全局唯一的调色板实例（整个应用引用它）
NIGHT_STADIUM = HudPalette()


# ════════════════════════════════════════════════════════════════════
#  结构令牌
# ════════════════════════════════════════════════════════════════════
class Radius:
    """玻璃卡片系统圆角。"""

    CARD = 24
    PILL = 999
    CHIP = 12
    INNER = 16


class Shadow:
    """阴影令牌 —— ``(blur_px, dy_px, base_rgba)``。

    ``CARD`` 对应设计稿 ``0 10px 40px rgba(0,0,0,.4)``。
    """

    CARD = (40, 10, "rgba(0,0,0,0.40)")
    CARD_HOVER = (48, 16, "rgba(0,0,0,0.50)")


class Type:
    """字体规格（pt 与字重）。"""

    DISPLAY = 40
    H1 = 30
    H2 = 22
    H3 = 18
    BODY = 14
    CAPTION = 12
    OVERLINE = 11

    W_REGULAR = 400
    W_MEDIUM = 600
    W_BOLD = 800
    W_BLACK = 900


# ════════════════════════════════════════════════════════════════════
#  颜色工具 —— rgba() / mix()
# ════════════════════════════════════════════════════════════════════
def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def _parse_color(color: str) -> tuple[int, int, int, float]:
    """把 ``#RGB`` / ``#RRGGBB`` / ``rgb(...)`` / ``rgba(...)`` 解析为 (r,g,b,a)。

    ``r/g/b`` 是 ``0..255`` 的整数，``a`` 是 ``0.0..1.0`` 的浮点 alpha。
    """
    s = color.strip()
    if s.startswith("#"):
        hexpart = s[1:]
        if len(hexpart) == 3:                       # #RGB 简写
            hexpart = "".join(ch * 2 for ch in hexpart)
        if len(hexpart) != 6:
            raise ValueError(f"invalid hex color: {color!r}")
        r = int(hexpart[0:2], 16)
        g = int(hexpart[2:4], 16)
        b = int(hexpart[4:6], 16)
        return r, g, b, 1.0
    if s.lower().startswith("rgb"):
        inner = s[s.index("(") + 1:s.index(")")]
        parts = [p.strip() for p in inner.split(",")]
        if len(parts) not in (3, 4):
            raise ValueError(f"invalid rgb/rgba color: {color!r}")
        r, g, b = (int(round(float(parts[i]))) for i in range(3))
        a = float(parts[3]) if len(parts) == 4 else 1.0
        return r, g, b, a
    raise ValueError(f"unsupported color format: {color!r}")


def rgba(color: str, alpha: float | None = None) -> str:
    """规范化为 ``rgba(r,g,b,a)`` 字符串，可选覆盖 alpha。

    * ``rgba("#19E3B5", 0.35)`` → ``"rgba(25,227,181,0.35)"``
    * ``rgba("rgba(255,255,255,0.05)")`` → ``"rgba(255,255,255,0.05)"``

    所有分量都被夹紧到合法区间（``r/g/b ∈ [0,255]``、``a ∈ [0,1]``）。
    """
    r, g, b, a = _parse_color(color)
    if alpha is not None:
        a = alpha
    r = int(_clamp(r, 0, 255))
    g = int(_clamp(g, 0, 255))
    b = int(_clamp(b, 0, 255))
    a = _clamp(float(a), 0.0, 1.0)
    # 去掉无意义的尾随 0，保持紧凑（0.35 而非 0.350000）
    a_str = f"{a:.3f}".rstrip("0").rstrip(".")
    if a_str == "":
        a_str = "0"
    return f"rgba({r},{g},{b},{a_str})"


def mix(c1: str, c2: str, t: float) -> str:
    """按比例 ``t`` 线性混合两个颜色，返回 ``#RRGGBB``。

    ``t=0`` 返回 ``c1``，``t=1`` 返回 ``c2``；``t`` 会被夹紧到 ``[0,1]``。
    alpha 不参与（混合结果总是不透明 hex），用于派生中间色调。
    """
    t = _clamp(float(t), 0.0, 1.0)
    r1, g1, b1, _ = _parse_color(c1)
    r2, g2, b2, _ = _parse_color(c2)
    r = int(round(r1 + (r2 - r1) * t))
    g = int(round(g1 + (g2 - g1) * t))
    b = int(round(b1 + (b2 - b1) * t))
    r = int(_clamp(r, 0, 255))
    g = int(_clamp(g, 0, 255))
    b = int(_clamp(b, 0, 255))
    return f"#{r:02X}{g:02X}{b:02X}"


# ════════════════════════════════════════════════════════════════════
#  全局样式表
# ════════════════════════════════════════════════════════════════════
def build_qss(palette: HudPalette = NIGHT_STADIUM) -> str:
    """产出全局 HUD 样式表。

    只依赖传入 ``palette`` 的命名令牌（不含任何散落 hex），切换调色板即可
    整体改观。覆盖：根背景渐变、文字默认色、玻璃卡（``#GlassCard``）、
    胶囊按钮、滚动条、输入框、分隔线等基础语汇。
    """
    p = palette
    return f"""
/* ── 根背景：垂直「球场之夜」渐变（L1 底色） ── */
QMainWindow, QWidget#RootSurface {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {p.bg_top}, stop:0.5 {p.bg_mid}, stop:1 {p.bg_bottom});
}}

/* ── 全局文字默认色 ── */
QWidget {{
    color: {p.text};
    font-size: {Type.BODY}px;
}}

/* ── 滚动正文不透明底（性能：避免整树重新合成） ── */
QWidget#OpaqueBody {{
    background: {p.bg_opaque_body};
}}

/* ── 玻璃卡片基类 ── */
QFrame#GlassCard {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: {Radius.CARD}px;
}}
QFrame#GlassCard[hovered="true"] {{
    border: 1px solid {p.glass_border_hi};
}}

/* ── 次级文字 ── */
QLabel[role="dim"]    {{ color: {p.text_dim}; }}
QLabel[role="faint"]  {{ color: {p.text_faint}; }}
QLabel[role="overline"] {{
    color: {p.text_dim};
    font-size: {Type.OVERLINE}px;
    font-weight: {Type.W_BOLD};
    letter-spacing: 2px;
}}

/* ── 胶囊按钮 ── */
QPushButton[pill="true"] {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: {Radius.PILL}px;
    padding: 8px 18px;
    color: {p.text};
    font-weight: {Type.W_MEDIUM};
}}
QPushButton[pill="true"]:hover {{
    border: 1px solid {p.glass_border_hi};
}}
QPushButton[pill="primary"] {{
    background: {rgba(p.primary, 0.18)};
    border: 1px solid {rgba(p.primary, 0.55)};
    border-radius: {Radius.PILL}px;
    padding: 8px 18px;
    color: {p.primary_hi};
    font-weight: {Type.W_BOLD};
}}

/* ── 输入框 ── */
QLineEdit {{
    background: {p.glass_fill};
    border: 1px solid {p.glass_border};
    border-radius: {Radius.INNER}px;
    padding: 8px 14px;
    color: {p.text};
    selection-background-color: {rgba(p.primary, 0.35)};
}}
QLineEdit:focus {{
    border: 1px solid {rgba(p.primary, 0.6)};
}}

/* ── 分隔线 ── */
QFrame[hr="true"] {{
    background: {p.glass_border};
    border: none;
    max-height: 1px;
}}

/* ── 滚动条（细、半透明，HUD 风） ── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {rgba(p.text_faint, 0.5)};
    border-radius: 4px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {rgba(p.primary, 0.5)};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
""".strip()
