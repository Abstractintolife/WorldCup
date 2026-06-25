"""count_up —— 数字「滚动上扬」控件（WorldCup 3.0）。

所有数据数字在页面进入时从 0 平滑增长到目标值（默认 **800ms / OutCubic**），
由 ``QVariantAnimation`` 驱动；动画结束帧把显示值精确设为 ``target``（无舍入
漂移）。

对应需求 21.1 / 21.2 / 21.3（设计 Property 11）：

* 21.1 —— 收到 target 后，显示值在 800ms 内从 0 逼近 target。
* 21.2 —— 动画完成时显示值**精确等于** target。
* 21.3 —— 朝非负 target 增长过程中，中间值**非递减**。

数值数学抽成纯函数（:func:`count_up_value` / :func:`count_up_display`），
不依赖 Qt，可在无头环境直接做属性测试。
"""
from __future__ import annotations

from PyQt6.QtCore import (
    QAbstractAnimation,
    QVariantAnimation,
    Qt,
)
from PyQt6.QtWidgets import QLabel, QWidget

from app.config import LOW_PERF
from app.ui.design.motion_system import EASE_STANDARD

#: 标准计数时长（毫秒）。
DURATION_MS = 800
#: 唯一缓动曲线 —— 复用统一动效系统的标准曲线（OutCubic），保证全应用运动语言一致。
EASE = EASE_STANDARD


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def ease_out_cubic(p: float) -> float:
    """OutCubic 缓动：``1 - (1-p)^3``，``p`` ∈ [0,1]，单调非减。"""
    p = _clamp(p)
    return 1.0 - (1.0 - p) ** 3


def count_up_value(target: float, progress: float) -> float:
    """纯函数：归一化进度 ``progress`` ∈ [0,1] 处应显示的（未舍入）数值。

    * ``progress >= 1`` → **精确返回** ``target``（保证终值无漂移，需求 21.2）。
    * 否则返回 ``target * ease_out_cubic(progress)``。

    由于 :func:`ease_out_cubic` 单调非减，对**非负** ``target`` 该函数随
    ``progress`` 单调非减（需求 21.3）。
    """
    p = _clamp(progress)
    if p >= 1.0:
        return target
    return target * ease_out_cubic(p)


def count_up_display(target: float, progress: float, decimals: int = 0) -> float:
    """纯函数：进度 ``progress`` 处**实际渲染**的数值（按 ``decimals`` 舍入）。

    终点（``progress >= 1``）精确等于 ``target``。``decimals <= 0`` 时返回
    整数值（以 ``float`` 表达，便于比较）。
    """
    raw = count_up_value(target, progress)
    if progress >= 1.0:
        # 终值不参与舍入，确保精确等于 target。
        return float(target)
    if decimals <= 0:
        return float(round(raw))
    return round(raw, decimals)


class CountUpNumber(QLabel):
    """从 0 滚动到 target 的数字标签。

    参数
    ----
    decimals:
        小数位数（``总进球数`` 用 0；``平均进球 2.94`` 用 2）。
    prefix / suffix:
        数字前后缀（如 ``"+"`` / ``"%"``）。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        decimals: int = 0,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        super().__init__(parent)
        self._decimals = max(0, int(decimals))
        self._prefix = prefix
        self._suffix = suffix
        self._target: float = 0.0
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(DURATION_MS)
        self._anim.setEasingCurve(EASE)
        self._anim.valueChanged.connect(self._on_value)
        self._anim.finished.connect(self._on_finished)

        self._render(0.0)

    # ── 文本格式化 ───────────────────────────
    def _format(self, value: float) -> str:
        text = f"{value:.{self._decimals}f}"
        return f"{self._prefix}{text}{self._suffix}"

    def _render(self, value: float) -> None:
        self.setText(self._format(value))

    def _reserve_width_for(self, target: float) -> None:
        """为「终值」预留固定宽度，避免计数过程中位数增长（0→1→2→3 位）改变
        标签宽度、把相邻控件（如「↑8%」涨跌幅）来回挤动 —— 即数字「乱动」的根因。

        标签左对齐，终值宽度一次性预留后，中间值在该宽度内左对齐增长，兄弟控件
        位置恒定。字号经 QSS 设定，``ensurePolished`` 后 ``fontMetrics`` 已反映实际
        字体；多给 2px 容差以防细微度量误差。
        """
        self.ensurePolished()
        final_text = self._format(float(target))
        try:
            w = self.fontMetrics().horizontalAdvance(final_text)
        except Exception:  # pragma: no cover - 极端无字体环境兜底
            return
        self.setMinimumWidth(w + 2)

    @property
    def target(self) -> float:
        return self._target

    # ── 公共 API ─────────────────────────────
    def set_target(self, target: float) -> None:
        """设定目标值并启动 0→target 的滚动动画。

        ``LOW_PERF`` 省电模式下直接显示终值（过渡瞬时完成）。
        """
        self._target = float(target)
        self._reserve_width_for(target)
        self._anim.stop()
        if LOW_PERF:
            # 低性能模式：瞬时落定到精确终值。
            self._render(float(target))
            return
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(target))
        self._render(0.0)
        self._anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)

    # ── 动画回调 ─────────────────────────────
    def _on_value(self, value) -> None:
        # 动画过程中按 decimals 舍入显示（非负 target 下非递减）。
        v = float(value)
        if self._decimals <= 0:
            v = float(round(v))
        else:
            v = round(v, self._decimals)
        self._render(v)

    def _on_finished(self) -> None:
        # 终帧：精确落到 target（需求 21.2，杜绝舍入漂移）。
        self._render(self._target)
