"""motion —— 缓动曲线、时长令牌与时间驱动插值小工具。

统一所有过渡的「时间曲线」与「时长」，对齐设计文档：
* 标准过渡 300ms / OutCubic；强调过渡用 OutQuint 更有「弹性减速」感。
* 时间驱动插值 :func:`approach` 用于按 dt 平滑逼近目标值（与帧率无关）。
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve

# ── 时长令牌（毫秒） ─────────────────────────
DUR_FAST = 180
DUR_NORMAL = 300
DUR_SLOW = 460

# ── 缓动曲线 ────────────────────────────────
EASE_STANDARD = QEasingCurve.Type.OutCubic
EASE_EMPHASIZED = QEasingCurve.Type.OutQuint
EASE_INOUT = QEasingCurve.Type.InOutSine


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(x: float) -> float:
    return 1.0 - (1.0 - x) ** 3


def ease_in_out_sine(x: float) -> float:
    return -(math.cos(math.pi * x) - 1.0) / 2.0


def approach(current: float, target: float, dt: float, speed: float = 12.0) -> float:
    """按 dt 以指数方式平滑逼近 target（帧率无关）。

    ``speed`` 越大收敛越快。常用于悬停高亮、数值滚动等需要「跟手」的插值。
    """
    k = 1.0 - math.exp(-speed * max(0.0, dt))
    return current + (target - current) * k
