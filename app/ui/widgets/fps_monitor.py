"""Performance Overlay —— 实时性能 HUD。

调试用半透明覆盖层，固定窗口右上角，由全局 :class:`FrameClock` 驱动。
它测量「帧时钟实际心跳间隔」：主线程被重绘 / 模糊压垮时 ``PreciseTimer``
无法按时触发、实测帧间隔变大、FPS 随之下降，因此读数能真实反映卡顿。

显示项
------
* **FPS**     —— 实测每秒帧数（指数平滑），按健康度染色（绿 / 琥珀 / 红）。
* **FRAME**   —— 平均帧耗时（ms） + 目标刷新率。
* **CPU**     —— 本进程 CPU 利用率近似（``process_time`` / 墙钟）。
* **MEM**     —— 常驻内存（MB）。
* **ANIM**    —— 当前活跃动画数（AnimationManager）。
* **PAINT**   —— 每秒重绘次数（QPaintEvent 计数）。

开关：环境变量 ``WC_FPS_OVERLAY=1`` 启动即显示；主窗口 ``Ctrl+Shift+F`` 切换。
"""
from __future__ import annotations

import time

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

from app.ui.design.animation_manager import anim as _anim
from app.ui.design.frame_clock import FrameClock
from app.ui.design.perf_stats import perf_stats


class FpsMonitor(QWidget):
    _WIDTH = 172
    _HEIGHT = 96

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFixedSize(self._WIDTH, self._HEIGHT)

        self._clock = FrameClock.instance()
        self._stats = perf_stats()
        self._subscribed = False

        self._fps = 0.0
        self._frame_ms = 0.0
        self._cpu = 0.0
        self._mem = 0.0
        self._anim_count = 0
        self._paint_per_s = 0.0

        self._accum_dt = 0.0
        self._accum_frames = 0
        self._last_sample_wall = time.perf_counter()
        self._last_cpu_time = time.process_time()
        self._last_paint_total = 0

    # ── 生命周期 ─────────────────────────────
    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._subscribed:
            self._stats.install(QApplication.instance())
            self._last_sample_wall = time.perf_counter()
            self._last_cpu_time = time.process_time()
            self._last_paint_total = self._stats.paint_total
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._stats.uninstall(QApplication.instance())
            self._subscribed = False

    # ── 采样 ─────────────────────────────────
    def _on_frame(self, _t: float, dt: float) -> None:
        self._accum_dt += dt
        self._accum_frames += 1
        now = time.perf_counter()
        elapsed = now - self._last_sample_wall
        if elapsed >= 0.4 and self._accum_frames > 0:
            avg_dt = self._accum_dt / self._accum_frames
            inst_fps = (1.0 / avg_dt) if avg_dt > 1e-6 else 0.0
            self._fps = inst_fps if self._fps == 0.0 else self._fps * 0.6 + inst_fps * 0.4
            self._frame_ms = avg_dt * 1000.0

            cpu_now = time.process_time()
            self._cpu = max(0.0, min(999.0, ((cpu_now - self._last_cpu_time) / elapsed) * 100.0))
            self._last_cpu_time = cpu_now

            paint_total = self._stats.paint_total
            self._paint_per_s = (paint_total - self._last_paint_total) / elapsed
            self._last_paint_total = paint_total

            self._mem = self._stats.memory_mb()
            self._anim_count = _anim().active_count()

            self._accum_dt = 0.0
            self._accum_frames = 0
            self._last_sample_wall = now
            self.update()

    # ── 绘制 ─────────────────────────────────
    def _fps_color(self) -> QColor:
        if self._fps >= 55:
            return QColor("#2ED877")
        if self._fps >= 30:
            return QColor("#FFC857")
        return QColor("#FF5470")

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(8, 13, 26, 212))
        p.drawRoundedRect(rect, 12, 12)
        p.setPen(QColor(0, 191, 255, 60))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 12, 12)

        mono = QFont("Consolas, Menlo, monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)

        # 大 FPS 数字
        col = self._fps_color()
        big = QFont(mono); big.setPointSize(22); big.setBold(True)
        p.setFont(big)
        p.setPen(col)
        p.drawText(QRectF(12, 4, 96, 32),
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                   f"{self._fps:4.0f}")
        lab = QFont(mono); lab.setPointSize(8); lab.setBold(True)
        p.setFont(lab)
        p.setPen(QColor(176, 190, 197))
        p.drawText(QRectF(96, 10, 70, 22),
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                   f"FPS / {self._clock.fps()}Hz")

        # 细节两列
        det = QFont(mono); det.setPointSize(8)
        p.setFont(det)
        p.setPen(QColor(176, 190, 197))
        line_h = 13
        y0 = 38
        rows_left = [
            f"FRAME {self._frame_ms:5.1f}ms",
            f"CPU   {self._cpu:5.1f}%",
            f"MEM   {self._mem:5.0f}MB",
        ]
        rows_right = [
            f"ANIM {self._anim_count:3d}",
            f"PAINT{self._paint_per_s:4.0f}/s",
            "",
        ]
        for i, txt in enumerate(rows_left):
            p.drawText(QRectF(12, y0 + i * line_h, 100, line_h),
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), txt)
        for i, txt in enumerate(rows_right):
            if txt:
                p.drawText(QRectF(108, y0 + i * line_h, 58, line_h),
                           int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), txt)
        p.end()
