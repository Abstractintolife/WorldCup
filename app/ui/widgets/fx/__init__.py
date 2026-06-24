"""fx —— 可复用「特效」控件包（WorldCup 3.0）。

收纳 Overview 页与各卡片共享的轻量动效控件，全部由**单一** ``FrameClock``
心跳或 ``AnimationManager`` 跟踪的属性动画驱动（除 Hero 倒计时外，**不**新增
任何 ``QTimer``）：

* :class:`CountUpNumber`  —— 数字 0→target 滚动（800ms / OutCubic）。
* :class:`FloatingFlag`   —— 包裹 :class:`FlagIcon` 的上下浮动旗帜（±3px / 4s）。
* :class:`MouseTrailOverlay` —— 透明的鼠标拖尾叠层（≤5 点、透明度递减）。

每个模块都把**数值数学**抽成无 GUI 依赖的纯函数（计数插值 / 拖尾透明度斜坡 /
浮动偏移），便于无头属性测试。
"""
from __future__ import annotations

from app.ui.widgets.fx.count_up import CountUpNumber
from app.ui.widgets.fx.floating_flag import FloatingFlag
from app.ui.widgets.fx.mouse_trail import MouseTrailOverlay
from app.ui.widgets.fx.standings_fx import (
    FormPills,
    MiniSparkline,
    QualBar,
    normalize_form,
    qual_fill_fraction,
    qual_percent_text,
    rank_delta_glyph,
)

__all__ = [
    "CountUpNumber",
    "FloatingFlag",
    "MouseTrailOverlay",
    "FormPills",
    "QualBar",
    "MiniSparkline",
    "rank_delta_glyph",
    "normalize_form",
    "qual_fill_fraction",
    "qual_percent_text",
]
