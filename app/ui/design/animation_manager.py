"""AnimationManager —— 全局统一动画系统（5.0 动效内核）。

设计目标
---------
* **统一入口**：Fade / Slide / Scale / Glow / Move / CountUp / Transition 全部经此
  创建，组件不再各自散落地 ``new QPropertyAnimation``。
* **生命周期安全**：每条动画都被登记，``stateChanged`` 驱动「活跃计数」增减；
  动画结束自动解除引用，杜绝悬空回调。
* **可观测**：``active_count()`` 暴露当前活跃动画数，供 Performance Overlay 显示
  （“Animation Count”）。
* **令牌化**：默认时长 / 缓动取自 :mod:`app.ui.design.tokens`，禁止魔法数字。

与底层 ``FrameClock`` 的关系
---------------------------
``FrameClock`` 是「单一帧调度器」（时间心跳）。本管理器创建的是 Qt
``QAbstractAnimation``（由 Qt 自己的动画驱动器推进），两者互补：逐帧自绘的
控件订阅 FrameClock，属性过渡动画走 AnimationManager。两条路径都被统一计数。
"""
from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QVariantAnimation,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

from app.ui.design.tokens import Duration, Easing


class AnimationManager(QObject):
    """进程级单例。统一创建 / 跟踪所有属性动画。"""

    _instance: AnimationManager | None = None

    def __init__(self) -> None:
        super().__init__()
        self._active: set[QAbstractAnimation] = set()
        self._started_total = 0

    @classmethod
    def instance(cls) -> AnimationManager:
        if cls._instance is None:
            cls._instance = AnimationManager()
        return cls._instance

    # ── 观测指标 ─────────────────────────────
    def active_count(self) -> int:
        return len(self._active)

    def started_total(self) -> int:
        return self._started_total

    # ── 核心：登记一条动画，按运行态维护活跃计数 ──
    def track(self, anim: QAbstractAnimation) -> QAbstractAnimation:
        def _on_state(new_state, _old) -> None:
            if new_state == QAbstractAnimation.State.Running:
                if anim not in self._active:
                    self._active.add(anim)
                    self._started_total += 1
            else:
                self._active.discard(anim)

        anim.stateChanged.connect(_on_state)
        anim.finished.connect(lambda: self._active.discard(anim))
        return anim

    # ════════════════════════════════════════════════
    #  统一动画工厂
    # ════════════════════════════════════════════════
    def fade(self, widget: QWidget, *, to: float = 1.0, frm: float | None = None,
             duration: int = Duration.NORMAL,
             easing: QEasingCurve.Type = Easing.STANDARD,
             on_done: Callable[[], None] | None = None) -> QPropertyAnimation:
        """淡入 / 淡出（通过 QGraphicsOpacityEffect 的 opacity 属性）。"""
        eff = widget.graphicsEffect()
        if not isinstance(eff, QGraphicsOpacityEffect):
            eff = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(eff)
        if frm is not None:
            eff.setOpacity(frm)
        anim = QPropertyAnimation(eff, b"opacity", widget)
        anim.setDuration(duration)
        if frm is not None:
            anim.setStartValue(frm)
        anim.setEndValue(to)
        anim.setEasingCurve(easing)
        if on_done is not None:
            anim.finished.connect(on_done)
        self.track(anim)
        anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)
        return anim

    def move(self, widget: QWidget, start, end, *,
             duration: int = Duration.NORMAL,
             easing: QEasingCurve.Type = Easing.EMPHASIZED) -> QPropertyAnimation:
        """几何 / 位置过渡（用于滑入、抬升）。start/end 为 QRect 或 QPoint。"""
        prop = b"geometry" if hasattr(start, "width") else b"pos"
        anim = QPropertyAnimation(widget, prop, widget)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(easing)
        self.track(anim)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim

    def animate_property(self, target: QObject, prop: bytes, start, end, *,
                         duration: int = Duration.NORMAL,
                         easing: QEasingCurve.Type = Easing.STANDARD,
                         loop: int = 1) -> QPropertyAnimation:
        """通用属性动画（Scale / Glow alpha / 自定义 pyqtProperty 等）。"""
        anim = QPropertyAnimation(target, prop, target)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(easing)
        anim.setLoopCount(loop)
        self.track(anim)
        anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)
        return anim

    def count_up(self, setter: Callable[[str], None], start: float, end: float, *,
                 duration: int = Duration.SLOW, fmt: str = "{:.0f}",
                 easing: QEasingCurve.Type = Easing.DECELERATE,
                 parent: QObject | None = None) -> QVariantAnimation:
        """数字滚动（CountUp）：从 ``start`` 平滑增长到 ``end``，每帧回调
        ``setter(text)`` 更新标签。用于统计数字 / 比分等「数据上扬」反馈。"""
        anim = QVariantAnimation(parent or self)
        anim.setStartValue(float(start))
        anim.setEndValue(float(end))
        anim.setDuration(duration)
        anim.setEasingCurve(easing)

        def _apply(v) -> None:
            try:
                setter(fmt.format(float(v)))
            except RuntimeError:
                anim.stop()

        anim.valueChanged.connect(_apply)
        self.track(anim)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim

    def stop_all(self) -> None:
        """停止所有活跃动画（页面大切换 / 退出时的兜底清理）。"""
        for anim in list(self._active):
            try:
                anim.stop()
            except RuntimeError:
                pass
        self._active.clear()


def anim() -> AnimationManager:
    """便捷取单例。"""
    return AnimationManager.instance()
