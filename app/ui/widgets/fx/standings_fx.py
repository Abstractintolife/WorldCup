"""standings_fx —— 积分榜专属「特效」控件与纯辅助函数（WorldCup 3.0，任务 10.1）。

对照设计稿复刻积分榜行内的四件「微件」：

* :func:`rank_delta_glyph` —— 排名变化字形：``"↑n"`` / ``"↓n"`` / ``"—"``。
* :class:`FormPills`       —— 近 5 场战绩胶囊（胜=绿 / 平=琥珀 / 负=红，≤5 枚）。
* :class:`QualBar`         —— 出线概率进度条（填充 = ``clamp(p,0,1)`` + 百分比标签）。
* :class:`MiniSparkline`   —— 净胜球（GD）趋势迷你折线。

对应需求 10.3（排名变化）/ 10.5（出线概率条）/ 10.7（近 5 场胶囊），
设计 Property 14 / 15 / 16。

**纯函数优先**：字形、胶囊归一化、填充比例三处数学全部抽成无 GUI 依赖的纯
函数（:func:`rank_delta_glyph` / :func:`normalize_form` / :func:`qual_fill_fraction`），
可在无头环境（``QT_QPA_PLATFORM=offscreen`` 或根本无 Qt）直接做属性测试。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette, Radius, Type, rgba

# ── 战绩字母 → 语义槽位 ─────────────────────────
#: 合法的近 5 场战绩字母（大写）。
FORM_RESULTS = ("W", "D", "L")
#: 最多展示的战绩胶囊数。
MAX_FORM_PILLS = 5


# ════════════════════════════════════════════════════════════════════
#  纯函数：排名变化字形（Property 15 / 需求 10.7）
# ════════════════════════════════════════════════════════════════════
def rank_delta_glyph(delta: int | None) -> str:
    """纯函数：把排名变化量 ``delta`` 渲染成字形。

    * ``delta > 0`` → ``"↑{n}"``（名次上升，``n = delta``）。
    * ``delta < 0`` → ``"↓{n}"``（名次下降，``n = |delta|``）。
    * ``delta == 0`` 或 ``None`` → ``"—"``（持平 / 无数据）。

    其中 ``n`` 恒为 ``|delta|`` 的绝对值（需求 10.7，Property 15）。约定
    «正 = 上升»：调用方应以 ``last_rank - rank`` 计算 ``delta``（名次数字变小 =
    上升 = 正向）。
    """
    if delta is None:
        return "—"
    d = int(delta)
    if d > 0:
        return f"↑{d}"
    if d < 0:
        return f"↓{-d}"
    return "—"


# ════════════════════════════════════════════════════════════════════
#  纯函数：近 5 场战绩归一化（Property 14 / 需求 10.4）
# ════════════════════════════════════════════════════════════════════
def normalize_form(results) -> list[str]:
    """纯函数：把任意战绩序列归一化为「**最近 5 场**、每项 ∈ {W,D,L}」的列表。

    处理流程：
    1. 逐项大写并去除首尾空白；
    2. 丢弃任何不在 ``{W, D, L}`` 中的项（容错脏数据）；
    3. 只保留**最后** :data:`MAX_FORM_PILLS`（5）项（最近的战绩）。

    返回列表长度恒 ``<= 5``，且每项恒 ∈ ``{W, D, L}``（需求 10.4，Property 14）。
    """
    if not results:
        return []
    cleaned: list[str] = []
    for item in results:
        if item is None:
            continue
        ch = str(item).strip().upper()
        if ch in FORM_RESULTS:
            cleaned.append(ch)
    return cleaned[-MAX_FORM_PILLS:]


# ════════════════════════════════════════════════════════════════════
#  纯函数：出线概率填充比例（Property 16 / 需求 10.5）
# ════════════════════════════════════════════════════════════════════
def qual_fill_fraction(p: float | None) -> float:
    """纯函数：出线概率 ``p`` → 进度条填充比例 ``clamp(p, 0, 1)``。

    * ``None`` → ``0.0``（无数据，空条）。
    * 其余一律夹紧到 ``[0.0, 1.0]``（需求 10.5，Property 16）。
    """
    if p is None:
        return 0.0
    v = float(p)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def qual_percent_text(p: float | None) -> str:
    """纯函数：出线概率 → 百分比标签文本（``None`` → ``"—"``）。"""
    if p is None:
        return "—"
    return f"{round(qual_fill_fraction(p) * 100)}%"


# ════════════════════════════════════════════════════════════════════
#  FormPills —— 近 5 场战绩胶囊
# ════════════════════════════════════════════════════════════════════
class FormPills(QWidget):
    """把近 5 场战绩渲染为一排小色块胶囊（胜=绿 / 平=琥珀 / 负=红）。

    至多 5 枚（:data:`MAX_FORM_PILLS`），每枚对应 ``{W, D, L}`` 之一
    （需求 10.3 / 10.4，Property 14）。
    """

    def __init__(
        self,
        results=None,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
        pill_size: int = 16,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self._size = int(pill_size)
        self._results: list[str] = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(4)
        self._row.addStretch(1)
        self.set_results(results or [])

    def _color_for(self, result: str) -> str:
        return {
            "W": self._palette.win,
            "D": self._palette.draw,
            "L": self._palette.loss,
        }.get(result, self._palette.text_faint)

    def _clear(self) -> None:
        while self._row.count():
            it = self._row.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()

    def set_results(self, results) -> None:
        """设置战绩序列（自动归一化为最近 ≤5 场、每项 ∈ {W,D,L}）。"""
        self._results = normalize_form(results)
        self._clear()
        for r in self._results:
            color = self._color_for(r)
            pill = QLabel(r)
            pill.setFixedSize(self._size, self._size)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setStyleSheet(
                f"background: {rgba(color, 0.9)}; color: #04121A;"
                f" border-radius: {self._size // 2}px;"
                f" font-size: {max(8, self._size - 6)}px; font-weight: {Type.W_BOLD};"
            )
            self._row.addWidget(pill)
        self._row.addStretch(1)

    @property
    def results(self) -> list[str]:
        return list(self._results)


# ════════════════════════════════════════════════════════════════════
#  QualBar —— 出线概率进度条
# ════════════════════════════════════════════════════════════════════
class QualBar(QWidget):
    """出线概率进度条：填充宽度 = ``clamp(p,0,1)``，右侧附百分比标签。

    ``p`` 为 ``None`` 时隐藏百分比文本（渲染「—」），填充为空（需求 10.5 /
    10.2，Property 16）。
    """

    def __init__(
        self,
        prob: float | None = None,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
        show_label: bool = True,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self._prob: float | None = None
        self._show_label = show_label
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(14)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        self._track = _QualTrack(palette, self)
        row.addWidget(self._track, 1)
        self._label = QLabel("—")
        self._label.setMinimumWidth(30)
        self._label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._label.setStyleSheet(
            f"color: {palette.text}; font-size: {Type.CAPTION}px;"
            f" font-weight: {Type.W_BOLD}; background: transparent;"
        )
        self._label.setVisible(show_label)
        row.addWidget(self._label, 0)
        self.set_probability(prob)

    def set_probability(self, prob: float | None) -> None:
        """设置出线概率（``[0,1]``，夹紧）；``None`` → 空条 + 「—」。"""
        self._prob = prob
        self._track.set_fraction(qual_fill_fraction(prob))
        self._label.setText(qual_percent_text(prob))

    @property
    def fraction(self) -> float:
        return qual_fill_fraction(self._prob)


class _QualTrack(QWidget):
    """QualBar 的实际绘制轨道（背景槽 + 渐变填充）。"""

    def __init__(self, palette: HudPalette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._fraction = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumWidth(24)
        self.setFixedHeight(8)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_fraction(self, fraction: float) -> None:
        self._fraction = qual_fill_fraction(fraction)
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        radius = h / 2.0

        # 背景槽。
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
        p.fillPath(track, QColor(255, 255, 255, 22))

        # 填充：颜色随概率从 loss(红) → draw(琥珀) → win(绿) 过渡。
        fill_w = w * self._fraction
        if fill_w > 0:
            clip = QPainterPath()
            clip.addRoundedRect(QRectF(0, 0, fill_w, h), radius, radius)
            p.setClipPath(clip)
            col = self._fill_color(self._fraction)
            p.fillRect(QRectF(0, 0, fill_w, h), col)
            p.setClipping(False)

    def _fill_color(self, frac: float) -> QColor:
        pal = self._palette
        if frac >= 0.6:
            return QColor(pal.win)
        if frac >= 0.35:
            return QColor(pal.draw)
        return QColor(pal.loss)


# ════════════════════════════════════════════════════════════════════
#  MiniSparkline —— 净胜球（GD）趋势迷你折线
# ════════════════════════════════════════════════════════════════════
class MiniSparkline(QWidget):
    """把净胜球（goal difference）随轮次的走势画成一条迷你折线。

    无数据 / 单点时不画线（仅留空白），不抛错（需求 10.3 优雅降级）。
    """

    def __init__(
        self,
        series=None,
        parent: QWidget | None = None,
        *,
        palette: HudPalette = NIGHT_STADIUM,
        width: int = 56,
        height: int = 20,
    ) -> None:
        super().__init__(parent)
        self._palette = palette
        self._series: list[float] = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(int(width), int(height))
        self.set_series(series or [])

    def set_series(self, series) -> None:
        self._series = [float(v) for v in (series or [])]
        self.update()

    @property
    def series(self) -> list[float]:
        return list(self._series)

    def paintEvent(self, _ev) -> None:
        if len(self._series) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        pad = 2.0
        lo = min(self._series)
        hi = max(self._series)
        span = (hi - lo) or 1.0
        n = len(self._series)
        step = (w - 2 * pad) / (n - 1)

        path = QPainterPath()
        for i, v in enumerate(self._series):
            x = pad + i * step
            # 值越大越靠上（y 轴翻转）。
            y = pad + (1.0 - (v - lo) / span) * (h - 2 * pad)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # 末值非负 → 上升趋势用 win 色，否则 loss 色。
        trend_up = self._series[-1] >= self._series[0]
        col = QColor(self._palette.win if trend_up else self._palette.loss)
        pen = QPen(col, 1.6)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawPath(path)
