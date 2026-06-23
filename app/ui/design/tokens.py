"""Design Tokens —— 全局统一的「设计原子」常量。

为什么需要它
-------------
商业级设计系统的核心是「**禁止魔法数字**」：所有间距 / 圆角 / 字号 / 动画时长
都来自一套有限的、命名的令牌（token），而不是散落在各处的 ``16`` / ``20`` /
``300``。改一处令牌，全局节奏统一变化。

本模块只放「与主题无关」的结构性令牌（间距 / 圆角 / 字号 / 时长 / 缓动）。
**颜色令牌**仍由 :mod:`app.ui.theme` 的 ``ThemePalette`` 负责（随皮肤切换），
两者职责互补。

约定（8pt 栅格）
----------------
间距以 4 / 8 为基数，符合主流 8pt grid 设计规范，保证视觉节奏一致。
"""
from __future__ import annotations

from PyQt6.QtCore import QEasingCurve


# ════════════════════════════════════════════════════════════════════
#  间距令牌（Spacing）—— 8pt 栅格
# ════════════════════════════════════════════════════════════════════
class Space:
    XXS = 2
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


# ════════════════════════════════════════════════════════════════════
#  圆角令牌（Radius）
# ════════════════════════════════════════════════════════════════════
class Radius:
    XS = 6
    SM = 10
    MD = 14
    LG = 20      # 卡片默认
    XL = 28
    PILL = 999   # 胶囊 / 全圆


# ════════════════════════════════════════════════════════════════════
#  字号令牌（Typography）
# ════════════════════════════════════════════════════════════════════
class FontSize:
    OVERLINE = 11
    CAPTION = 12
    BODY = 14
    SUBTITLE = 16
    H3 = 20
    H2 = 22
    H1 = 32
    DISPLAY = 48


class FontWeight:
    REGULAR = 400
    MEDIUM = 600
    BOLD = 700
    HEAVY = 800
    BLACK = 900


# ════════════════════════════════════════════════════════════════════
#  动画令牌（Animation）—— 与 motion.py 对齐
# ════════════════════════════════════════════════════════════════════
class Duration:
    INSTANT = 90
    FAST = 180
    NORMAL = 300
    SLOW = 460
    SLOWER = 640


class Easing:
    STANDARD = QEasingCurve.Type.OutCubic       # 标准过渡
    EMPHASIZED = QEasingCurve.Type.OutQuint      # 强调（弹性减速）
    INOUT = QEasingCurve.Type.InOutSine          # 往复（呼吸 / 循环）
    DECELERATE = QEasingCurve.Type.OutQuart      # 进入
    ACCELERATE = QEasingCurve.Type.InQuart       # 退出


# ════════════════════════════════════════════════════════════════════
#  交互手势令牌（统一的「微反馈」幅度）
# ════════════════════════════════════════════════════════════════════
class Motion:
    HOVER_SCALE = 1.03       # 卡片悬停放大
    PRESS_SCALE = 0.97       # 按下回弹
    LIFT_DY = 8              # 悬停「浮起」位移
    PAGE_SLIDE_DX = 26       # 页面进入滑动


# ════════════════════════════════════════════════════════════════════
#  阴影令牌（与 resource_cache.drop_shadow_pixmap 配合的标准参数）
# ════════════════════════════════════════════════════════════════════
class Shadow:
    # (blur, dy, alpha)
    CARD = (28, 6, 100)
    CARD_HOVER = (40, 14, 150)
    ELEVATED = (48, 12, 130)
    SUBTLE = (16, 3, 80)
