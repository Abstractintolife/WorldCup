"""PerfStats —— 进程级性能采样（供 Performance Overlay 使用）。

采集
----
* **Paint Count**：在 ``QApplication`` 上装一个事件过滤器，统计每秒 ``QPaintEvent``
  的数量 —— 重绘越频繁，这个数越高，是定位「过度重绘 / 全窗口刷新」的关键指标。
  过滤器只做一次自增，开销可忽略。
* **Memory**：读取本进程常驻内存（RSS）。Linux 优先读 ``/proc/self/statm``，
  其余平台回退到 ``resource.getrusage``。
* **Animation Count**：转发 :class:`AnimationManager` 的活跃动画数。

所有读数都是「便宜的整数 / 浮点」，由 Overlay 每 ~0.4s 拉取一次。
"""
from __future__ import annotations

import os

from PyQt6.QtCore import QEvent, QObject


class _PaintCounter(QObject):
    """应用级事件过滤器：累计 QPaintEvent 次数。"""

    def __init__(self, stats: "PerfStats") -> None:
        super().__init__()
        self._stats = stats

    def eventFilter(self, _obj, ev) -> bool:  # noqa: N802
        if ev.type() == QEvent.Type.Paint:
            self._stats._paint_total += 1
        return False


class PerfStats:
    _instance: "PerfStats | None" = None

    def __init__(self) -> None:
        self._paint_total = 0
        self._filter: _PaintCounter | None = None
        self._page_size = 4096
        try:
            self._page_size = os.sysconf("SC_PAGE_SIZE")
        except (ValueError, AttributeError, OSError):
            pass

    @classmethod
    def instance(cls) -> "PerfStats":
        if cls._instance is None:
            cls._instance = PerfStats()
        return cls._instance

    def install(self, app) -> None:
        """在 QApplication 上安装重绘计数过滤器（仅当 Overlay 开启时调用）。"""
        if self._filter is None and app is not None:
            self._filter = _PaintCounter(self)
            app.installEventFilter(self._filter)

    def uninstall(self, app) -> None:
        if self._filter is not None and app is not None:
            app.removeEventFilter(self._filter)
            self._filter = None

    @property
    def paint_total(self) -> int:
        return self._paint_total

    def memory_mb(self) -> float:
        """本进程常驻内存（MB）。"""
        # Linux：/proc/self/statm 第 2 字段 = resident pages
        try:
            with open("/proc/self/statm", "r", encoding="ascii") as fh:
                resident = int(fh.read().split()[1])
            return resident * self._page_size / (1024 * 1024)
        except (OSError, IndexError, ValueError):
            pass
        try:
            import resource
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # Linux 单位 KB，macOS 单位字节
            import sys
            return rss / 1024.0 if sys.platform != "darwin" else rss / (1024 * 1024)
        except Exception:  # pragma: no cover
            return 0.0


def perf_stats() -> PerfStats:
    return PerfStats.instance()
