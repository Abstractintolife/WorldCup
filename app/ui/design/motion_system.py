"""motion_system —— 统一动效系统（WorldCup 3.0）。

把**所有**过渡收敛到「一条曲线 + 一个标准时长 + 一个悬停手势 + 一道时长硬上限」，
让全应用的运动语言绝对一致：

* 缓动：``QEasingCurve.Type.OutCubic``（唯一曲线）。
* 标准时长：180 ms。
* 时长硬上限：500 ms（超过即视为违规，发布态夹紧）。
* 悬停：``translateY(-6px)``。

本模块构建在既有 :class:`AnimationManager`（生命周期登记 / 活跃计数）与
``tokens`` 之上 —— 它是控件获取 hover / enter / exit / 页面过渡动画的**唯一**
合法入口。

不变量（对应需求 19.1 / 19.2 / 19.3 / 19.4，设计 Property 1 / 2 / 3）：
经本模块创建的任意动画 ``A``，``easing(A) == OutCubic`` 且 ``duration(A) <= 500``。
"""
from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QTimer,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from app.config import LOW_PERF
from app.ui.design import tokens
from app.ui.design.animation_manager import AnimationManager

try:  # 用 sip 可靠判断底层 C++ 对象是否已析构
    from PyQt6 import sip  # type: ignore
except ImportError:  # pragma: no cover
    sip = None  # type: ignore

# ── 运动令牌 ────────────────────────────────
EASE_STANDARD = QEasingCurve.Type.OutCubic   # 唯一曲线
DUR_STANDARD = 180                           # 标准过渡时长（ms）
DUR_MAX = 500                                # 硬上限；> 500ms 被禁止
HOVER_LIFT_DY = -6                           # 悬停 translateY(-6px)
PAGE_SLIDE_DY = 22                           # 页面切入：自下而上轻微滑入像素

# ── 与 tokens 对齐（设计要求：retarget） ─────
# 把结构令牌中的「快速过渡」与「标准缓动」重定向到本系统的定义，
# 确保任何仍直接引用 tokens 的旧代码也得到统一的 180ms / OutCubic。
tokens.Duration.FAST = DUR_STANDARD
tokens.Easing.STANDARD = EASE_STANDARD

# 存放卡片「静息位置」的属性名（供 hover_lift 记忆 restY）
_REST_ATTR = "_hud_rest_pos"


def clamp_duration(duration: int) -> int:
    """把任意请求时长夹紧到 ``[0, DUR_MAX]``（保证 ≤ 500ms 上限）。"""
    d = int(duration)
    if d < 0:
        d = 0
    if d > DUR_MAX:
        d = DUR_MAX
    return d


def std_anim(
    target: QObject,
    prop: bytes,
    start,
    end,
    duration: int = DUR_STANDARD,
) -> QPropertyAnimation:
    """创建一条「标准过渡」动画。

    保证：缓动恒为 ``OutCubic``；有效时长被夹紧到 ``<= DUR_MAX``（500ms）。
    动画会登记进 :class:`AnimationManager`（统一计数 / 生命周期跟踪），但
    **不自动启动** —— 由调用方按需 ``start()``（``hover_lift`` 会替你启动）。

    时长策略（设计 "Motion Design System"）：调试态 ``assert`` 捕获越界请求以
    便在开发期暴露违规调用；发布态（``python -O``）断言被跳过，由 ``clamp_duration``
    把时长夹紧到 ``<= DUR_MAX``，保证不变量在任何构建下都成立。
    """
    assert duration <= DUR_MAX, "animation duration exceeds 500ms ceiling"
    eff_duration = clamp_duration(duration)
    anim = QPropertyAnimation(target, prop, target)
    anim.setDuration(eff_duration)
    anim.setEasingCurve(EASE_STANDARD)          # 永远 OutCubic
    anim.setStartValue(start)
    anim.setEndValue(end)
    AnimationManager.instance().track(anim)
    return anim


def hover_lift_target_y(rest_y: int, *, up: bool) -> int:
    """纯函数：给定静息 ``rest_y``，返回悬停目标 Y。

    * ``up=True``  → ``rest_y + HOVER_LIFT_DY``（即 ``rest_y - 6``，浮起）。
    * ``up=False`` → ``rest_y``（精确回到静息）。

    抽成纯函数便于在无 GUI 环境下做属性测试（Property 3 的目标数学）。
    """
    return rest_y + HOVER_LIFT_DY if up else rest_y


def hover_lift(
    widget,
    *,
    up: bool,
    duration: int = DUR_STANDARD,
) -> QPropertyAnimation:
    """对控件做悬停浮起 / 回落动画（只动 ``pos``，绝不动 ``blurRadius``）。

    第一次调用时记忆控件当前位置为「静息位置」；之后：
    * ``up=True``  → 动画到 ``restY - 6``。
    * ``up=False`` → 精确动画回 ``restY``。
    """
    current = widget.pos()
    rest: QPoint | None = getattr(widget, _REST_ATTR, None)
    if rest is None:
        # 首次（通常是 enter）：当前位置即静息位置。
        rest = QPoint(current)
        setattr(widget, _REST_ATTR, rest)

    target_y = hover_lift_target_y(rest.y(), up=up)
    target = QPoint(rest.x(), target_y)

    anim = std_anim(widget, b"pos", current, target, duration=duration)
    anim.start()
    return anim


def _is_alive(obj) -> bool:
    """底层 C++ 对象是否仍存活（避免页面切换销毁后访问抛 RuntimeError）。"""
    if obj is None:
        return False
    if sip is not None:
        try:
            return not sip.isdeleted(obj)
        except (TypeError, RuntimeError):
            return False
    try:  # pragma: no cover - sip 缺失兜底
        obj.objectName()
        return True
    except RuntimeError:
        return False


def page_transition(
    widget,
    *,
    duration: int = DUR_STANDARD,
    dy: int = PAGE_SLIDE_DY,
):
    """页面切入过渡：180ms「淡入 + 自下而上滑入」（需求 29.2）。

    这是页面级过渡的**唯一**合法入口（经本系统 → ``std_anim``，故缓动恒为
    OutCubic、时长被夹紧到 ≤ 500ms，满足 Property 1 / 2）。

    低性能模式（``WC_LITE=1`` / ``LOW_PERF``）下过渡**瞬时完成**（需求 28.3）：
    清除可能残留的不透明度 effect、不创建任何动画，UI 立即可用。

    返回淡入动画（``None`` 表示瞬时 / 控件不可用）。
    """
    if not _is_alive(widget):
        return None

    # LOW_PERF：瞬时过渡 —— 移除残留 effect，确保控件完全可见，不建动画。
    if LOW_PERF:
        try:
            eff = widget.graphicsEffect()
            if isinstance(eff, QGraphicsOpacityEffect):
                widget.setGraphicsEffect(None)
        except RuntimeError:  # pragma: no cover
            pass
        return None

    # 停掉该控件上一轮页面淡入（避免「animation without target」告警）。
    prev = getattr(widget, "_page_fade_ref", None)
    if prev is not None:
        try:
            prev.stop()
        except RuntimeError:  # pragma: no cover
            pass

    # 淡入：复用 / 创建不透明度 effect。
    eff = widget.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
    eff.setOpacity(0.0)

    fade = std_anim(eff, b"opacity", 0.0, 1.0, duration=duration)
    setattr(widget, "_page_fade_ref", fade)

    def _cleanup() -> None:
        # 动画结束移除 effect：避免常驻在持续重绘的页面上拖累性能。
        if not _is_alive(widget):
            return
        try:
            cur = widget.graphicsEffect()
            if isinstance(cur, QGraphicsOpacityEffect):
                widget.setGraphicsEffect(None)
        except RuntimeError:  # pragma: no cover
            pass

    fade.finished.connect(_cleanup)
    fade.start()

    # 滑入：推迟到事件循环下一轮，待父 layout 给出有效 geometry 再做位移
    # （否则会与布局争用，导致兄弟节点堆叠 —— 见 effects.fade_slide_in 注释）。
    if dy:
        def _slide_after_layout() -> None:
            if not _is_alive(widget):
                return
            try:
                geo = widget.geometry()
            except RuntimeError:
                return
            if geo.width() <= 0 or geo.height() <= 0:
                return
            start = QRect(geo)
            start.translate(0, dy)
            slide = std_anim(widget, b"geometry", start, geo, duration=duration)
            slide.start()

        QTimer.singleShot(1, _slide_after_layout)

    return fade
