"""FrameClock —— 全应用唯一的高精度帧时钟（动效内核）。

为什么需要它
-------------
要「适配 240 帧率」，正确的做法不是让每个动画控件各自跑一个 240Hz 的
``QTimer``（几十个高频定时器会互相抖动、抢 CPU、且无法统一调速），而是：

* 维护 **一个** ``Qt.TimerType.PreciseTimer`` 定时器，按目标帧率触发；
* 每拍用 ``time.perf_counter()`` 计算真实经过时间 ``dt``，广播 ``tick(t, dt)``；
* 所有动画订阅这一个信号，并 **基于 dt 做时间驱动运动** —— 因此 60fps 与
  240fps 下物体速度完全一致，只是后者更顺滑；
* 用「订阅引用计数」自动启停：没有任何可见动画时定时器停转，零空转开销。

运行时调速
-----------
``set_fps(n)`` 可在 60 / 120 / 144 / 240 之间即时切换（设置面板调用），
无需重启。``LOW_PERF`` 省电模式下时钟不启动（动效呈静态）。
"""
from __future__ import annotations

import time
from typing import Callable

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal

from app.config import ANIM_FPS, LOW_PERF

# 帧率允许范围。上限定在 144（「真实电竞帧」）：CPU 软件栅格化的动态背景
# 无法稳定喂满 240Hz，硬开 240 反而因定时器过冲 / 帧积压而「假高帧、真卡顿」。
# 144Hz（间隔 ~7ms）是单线程 QPainter 能稳定达成、肉眼顺滑的真实上限；保存过
# 240 的旧设置在 set_fps 时会被夹到 144。
FPS_MIN = 30
FPS_MAX = 144
# 单帧 dt 的安全上限（窗口被挂起/拖动后恢复时，避免一次性巨大跳变）
_MAX_DT = 0.05

# 「参考帧率」：旧代码的每帧位移增量是以 60fps 为基准写死的，
# 时间驱动改造后用 dt * REF_FPS 作为「帧缩放系数」，保持原有观感速度。
REF_FPS = 60.0


class FrameClock(QObject):
    """单例全局帧时钟。"""

    tick = pyqtSignal(float, float)   # (t_seconds, dt_seconds)
    fps_changed = pyqtSignal(int)

    _instance: "FrameClock | None" = None

    @classmethod
    def instance(cls) -> "FrameClock":
        if cls._instance is None:
            cls._instance = FrameClock()
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self._fps = max(FPS_MIN, min(FPS_MAX, int(ANIM_FPS)))
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.setInterval(self._interval_ms())
        self._timer.timeout.connect(self._on_timeout)
        self._t: float = 0.0
        self._last: float | None = None
        self._subs: int = 0  # 订阅引用计数

    # ── 帧率 ─────────────────────────────────
    def _interval_ms(self) -> int:
        return max(1, round(1000.0 / self._fps))

    def fps(self) -> int:
        return self._fps

    def set_fps(self, fps: int) -> None:
        fps = int(max(FPS_MIN, min(FPS_MAX, fps)))
        if fps == self._fps:
            return
        self._fps = fps
        self._timer.setInterval(self._interval_ms())
        self.fps_changed.emit(fps)

    @property
    def time(self) -> float:
        return self._t

    # ── 订阅（自动启停） ─────────────────────
    def subscribe(self, cb: Callable[[float, float], None]) -> None:
        """订阅每帧回调 ``cb(t, dt)``。可见动画在 showEvent 调用。"""
        self.tick.connect(cb)
        self._subs += 1
        if not LOW_PERF and not self._timer.isActive():
            self._last = time.perf_counter()
            self._timer.start()

    def unsubscribe(self, cb: Callable[[float, float], None]) -> None:
        """取消订阅。隐藏/销毁动画在 hideEvent 调用。"""
        try:
            self.tick.disconnect(cb)
        except TypeError:
            return
        self._subs = max(0, self._subs - 1)
        if self._subs == 0:
            self._timer.stop()
            self._last = None

    # ── 心跳 ─────────────────────────────────
    def _on_timeout(self) -> None:
        now = time.perf_counter()
        if self._last is None:
            self._last = now
        dt = now - self._last
        self._last = now
        if dt < 0.0:
            dt = 0.0
        elif dt > _MAX_DT:
            dt = _MAX_DT
        self._t += dt
        self.tick.emit(self._t, dt)
