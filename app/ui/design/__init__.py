"""设计系统地基：统一帧时钟、缓动、设计令牌。

这是「商业级重构」的动效内核所在。所有动画都由 :class:`FrameClock`
单一高精度时钟驱动（时间驱动而非帧驱动），从而：

* 真正支持高刷新率（最高 240FPS），且运行时可切换目标帧率；
* 同一 dt 下运动速度恒定 —— 60fps 与 240fps 观感一致，只是更顺滑；
* 全应用只有一个定时器在跑，避免数十个 QTimer 各自为政带来的抖动与开销。
"""
from app.ui.design.frame_clock import FrameClock
from app.ui.design.motion import (
    DUR_FAST,
    DUR_NORMAL,
    DUR_SLOW,
    EASE_EMPHASIZED,
    EASE_STANDARD,
    clamp,
    ease_out_cubic,
    lerp,
)

__all__ = [
    "FrameClock",
    "DUR_FAST",
    "DUR_NORMAL",
    "DUR_SLOW",
    "EASE_EMPHASIZED",
    "EASE_STANDARD",
    "clamp",
    "ease_out_cubic",
    "lerp",
]
