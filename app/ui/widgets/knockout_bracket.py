"""淘汰赛对阵图（脑图 / Bracket 树状视图）。

布局参照 The Analyst「FIFA World Cup Predictions · Bracket」：
左右各 16 队（8 组 R32 对阵）向中间收拢 —— 16强 → 八强 → 半决赛 →
中央「决赛 / 冠军」。每个队格显示真实国旗 + 中文队名；轮次格在尚未
产生胜者的位置显示「16强 / 八强 / 半决赛 / 决赛」标签。

实现：固定尺寸画布（由列宽与队数推导），队格 / 轮次格用 ``QFrame`` 按
绝对几何摆放，连接线在 ``paintEvent`` 中按各格几何用 ``QPainter`` 绘制。
外层用 ``QScrollArea`` 包裹，面板较窄时可滚动查看完整对阵图。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.flag_icon import FlagIcon

# ── 配色（配合 app 深色「夜战球场」主题）──────────────────────
_CELL_BG = "rgba(15, 29, 46, 0.92)"
_CELL_BORDER = "#1f3b54"
_LABEL_BORDER = "#33597a"
_TEXT = "#E8EEF5"
_DIM = "#7C8CA1"
_GOLD = "#FFD700"
_LINE = QColor("#33597a")
_LINE_GOLD = QColor("#FFD700")

# ── 默认对阵数据（Opta 预测，左右各 8 组 R32）──────────────────
# 顺序与 The Analyst bracket 一致；可按需替换为实时数据。
LEFT_PAIRS: list[tuple[str, str]] = [
    ("德国", "巴拉圭"), ("法国", "瑞典"),
    ("南非", "加拿大"), ("荷兰", "摩洛哥"),
    ("葡萄牙", "克罗地亚"), ("西班牙", "奥地利"),
    ("美国", "波黑"), ("比利时", "塞内加尔"),
]
RIGHT_PAIRS: list[tuple[str, str]] = [
    ("巴西", "日本"), ("科特迪瓦", "挪威"),
    ("墨西哥", "厄瓜多尔"), ("英格兰", "刚果民主共和国"),
    ("阿根廷", "佛得角"), ("澳大利亚", "埃及"),
    ("瑞士", "阿尔及利亚"), ("哥伦比亚", "加纳"),
]

# ── 几何常量 ──────────────────────────────────────────────
_TEAM_W = 168
_TEAM_H = 74
_GAP = 34          # 相邻 R32 队格间距
_TOP = 56
_LBL_W = 120       # 轮次标签格宽
_LBL_H = 54
_FINAL_W = 168
_FINAL_H = 70
_COL_GAP = 56      # 列间水平间距
_MARGIN_X = 24


class _Cell(QFrame):
    """一个 R32 对阵队格：上下两行（国旗 + 中文队名）。点击发出 ``clicked``。"""

    #: 点击信号 —— 携带 (主队中文名, 客队中文名)，供页面解析为 Match 跳转。
    clicked = pyqtSignal(str, str)

    def __init__(self, top_team: str, bottom_team: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._home = top_team
        self._away = bottom_team
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # 悬停高亮边框 —— 提示「可点击进入比赛详情」。
        self.setStyleSheet(
            f"QFrame{{background:{_CELL_BG}; border:1px solid {_CELL_BORDER};"
            "border-radius:8px;}"
            f"QFrame:hover{{border:1px solid #00BFFF;}}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)
        for name in (top_team, bottom_team):
            row = QHBoxLayout()
            row.setSpacing(9)
            row.addWidget(FlagIcon(name, height=18, radius=3))
            lbl = QLabel(name)
            lbl.setStyleSheet(
                f"color:{_TEXT}; font-size:13px; font-weight:700; border:none;"
                "background:transparent;"
            )
            row.addWidget(lbl)
            row.addStretch(1)
            lay.addLayout(row)

    def mousePressEvent(self, ev) -> None:  # noqa: D401
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._home, self._away)
        super().mousePressEvent(ev)


class _LabelBox(QFrame):
    """轮次标签格（16强 / 八强 / 半决赛 / 决赛）。"""

    def __init__(self, text: str, parent: QWidget, *, gold: bool = False) -> None:
        super().__init__(parent)
        border = _GOLD if gold else _LABEL_BORDER
        self.setStyleSheet(
            f"QFrame{{background:{_CELL_BG}; border:1px solid {border};"
            "border-radius:8px;}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        color = _GOLD if gold else _DIM
        weight = 900 if gold else 700
        size = 15 if gold else 13
        lbl.setStyleSheet(
            f"color:{color}; font-size:{size}px; font-weight:{weight};"
            "border:none; background:transparent;"
        )
        lay.addWidget(lbl)


class KnockoutBracket(QWidget):
    """淘汰赛对阵图画布（固定尺寸，放入 QScrollArea 使用）。"""

    #: 点击某个 R32 对阵格 —— 携带 (主队中文名, 客队中文名)。
    match_clicked = pyqtSignal(str, str)

    def __init__(
        self,
        left_pairs: list[tuple[str, str]] | None = None,
        right_pairs: list[tuple[str, str]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._left = left_pairs or LEFT_PAIRS
        self._right = right_pairs or RIGHT_PAIRS
        # 连接线段缓存：[(x1, y1, x2, y2, gold?), ...]
        self._segments: list[tuple[float, float, float, float, bool]] = []
        self._build()

    # ── 几何辅助 ──────────────────────────────────────────
    @staticmethod
    def _centers(n: int) -> list[float]:
        return [_TOP + i * (_TEAM_H + _GAP) + _TEAM_H / 2 for i in range(n)]

    @staticmethod
    def _merge(centers: list[float]) -> list[float]:
        return [(centers[2 * j] + centers[2 * j + 1]) / 2 for j in range(len(centers) // 2)]

    def _build(self) -> None:
        team_cy = self._centers(8)
        l16_cy = self._merge(team_cy)
        qf_cy = self._merge(l16_cy)
        sf_cy = self._merge(qf_cy)[0]

        total_h = int(_TOP + 8 * _TEAM_H + 7 * _GAP + _TOP)
        # 列 x（左半）：队格 / 16强 / 八强 / 半决赛
        lx_team = _MARGIN_X
        lx_l16 = lx_team + _TEAM_W + _COL_GAP
        lx_qf = lx_l16 + _LBL_W + _COL_GAP
        lx_sf = lx_qf + _LBL_W + _COL_GAP
        # 中央决赛
        final_x_left = lx_sf + _LBL_W + _COL_GAP
        total_w = int((final_x_left + _FINAL_W + _COL_GAP) + _LBL_W + _COL_GAP
                      + _LBL_W + _COL_GAP + _LBL_W + _COL_GAP + _TEAM_W + _MARGIN_X)
        # 右半镜像列 x（以右边缘对齐）
        rx_team = total_w - _MARGIN_X - _TEAM_W
        rx_l16 = rx_team - _COL_GAP - _LBL_W
        rx_qf = rx_l16 - _COL_GAP - _LBL_W
        rx_sf = rx_qf - _COL_GAP - _LBL_W

        self.setFixedSize(total_w, total_h)
        segs: list[tuple[float, float, float, float, bool]] = []

        def place(widget: QWidget, x: float, cy: float, w: float, h: float) -> tuple[float, float]:
            widget.setGeometry(int(x), int(cy - h / 2), int(w), int(h))
            widget.show()
            return x, cy  # 返回左上参考

        # —— 左半 ——
        for i, (a, b) in enumerate(self._left):
            c = _Cell(a, b, self)
            c.clicked.connect(self.match_clicked.emit)
            place(c, lx_team, team_cy[i], _TEAM_W, _TEAM_H)
        for j, cy in enumerate(l16_cy):
            place(_LabelBox("16强", self), lx_l16, cy, _LBL_W, _LBL_H)
            # 连接两个队格 → 16强
            segs += self._connect(lx_team + _TEAM_W,
                                  [team_cy[2 * j], team_cy[2 * j + 1]],
                                  lx_l16, cy, right=True)
        for j, cy in enumerate(qf_cy):
            place(_LabelBox("八强", self), lx_qf, cy, _LBL_W, _LBL_H)
            segs += self._connect(lx_l16 + _LBL_W,
                                  [l16_cy[2 * j], l16_cy[2 * j + 1]],
                                  lx_qf, cy, right=True)
        place(_LabelBox("半决赛", self), lx_sf, sf_cy, _LBL_W, _LBL_H)
        segs += self._connect(lx_qf + _LBL_W, [qf_cy[0], qf_cy[1]], lx_sf, sf_cy, right=True)

        # —— 右半 ——
        for i, (a, b) in enumerate(self._right):
            c = _Cell(a, b, self)
            c.clicked.connect(self.match_clicked.emit)
            place(c, rx_team, team_cy[i], _TEAM_W, _TEAM_H)
        for j, cy in enumerate(l16_cy):
            place(_LabelBox("16强", self), rx_l16, cy, _LBL_W, _LBL_H)
            segs += self._connect(rx_team,
                                  [team_cy[2 * j], team_cy[2 * j + 1]],
                                  rx_l16 + _LBL_W, cy, right=False)
        for j, cy in enumerate(qf_cy):
            place(_LabelBox("八强", self), rx_qf, cy, _LBL_W, _LBL_H)
            segs += self._connect(rx_l16,
                                  [l16_cy[2 * j], l16_cy[2 * j + 1]],
                                  rx_qf + _LBL_W, cy, right=False)
        place(_LabelBox("半决赛", self), rx_sf, sf_cy, _LBL_W, _LBL_H)
        segs += self._connect(rx_qf, [qf_cy[0], qf_cy[1]], rx_sf + _LBL_W, sf_cy, right=False)

        # —— 中央：决赛 + 冠军 ——
        final_cy = sf_cy
        fb = _LabelBox("决赛", self, gold=True)
        place(fb, final_x_left, final_cy, _FINAL_W, _FINAL_H)
        champ = QLabel("🏆 冠军", self)
        champ.setAlignment(Qt.AlignmentFlag.AlignCenter)
        champ.setStyleSheet(
            f"color:{_GOLD}; font-size:17px; font-weight:900;"
            "border:none; background:transparent;"
        )
        champ.setGeometry(int(final_x_left), int(final_cy - _FINAL_H / 2 - 40),
                          int(_FINAL_W), 30)
        champ.show()
        # 半决赛 → 决赛（左右各一段，金色）
        segs.append((lx_sf + _LBL_W, sf_cy, final_x_left, final_cy, True))
        segs.append((final_x_left + _FINAL_W, final_cy, rx_sf, sf_cy, True))

        self._segments = segs

    @staticmethod
    def _connect(x_from: float, src_ys: list[float], x_to: float, y_to: float,
                 *, right: bool) -> list[tuple[float, float, float, float, bool]]:
        """生成两源 → 一目标的肘形连接线段。

        right=True：源在左、目标在右（左半）；right=False：镜像（右半）。
        """
        stub = x_from + (16 if right else -16)
        segs: list[tuple[float, float, float, float, bool]] = []
        for y in src_ys:
            segs.append((x_from, y, stub, y, False))
        segs.append((stub, min(src_ys), stub, max(src_ys), False))
        segs.append((stub, y_to, x_to, y_to, False))
        return segs

    # ── 绘制连接线 ────────────────────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for x1, y1, x2, y2, gold in self._segments:
            pen = QPen(_LINE_GOLD if gold else _LINE, 1.6 if gold else 1.3)
            p.setPen(pen)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))
        p.end()
