"""阵容球场控件 —— 还原懂球帝「阵容」页的横向球场布阵图。

布局
----
* 横向球场：A 队占左半场（球门在最左），B 队占右半场（球门在最右）。
* 每名球员一个圆形号码牌 + 下方姓名标签（A 队红、B 队白，与懂球帝一致）。
* 位置由 ``TeamLineup.formation``（如 ``4-2-3-1``）+ ``formation_place``
  推导：第 1 列为门将，其后由守到攻逐列展开，同一列内上下均布。
* 点击任一球员牌 → ``player_clicked(person_id, name)``（进入球员详情）。

接口不提供 ``position_x/y``，故所有坐标均由阵型字符串在本控件内计算。
"""
from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from app.models.lineup import LineupPlayer, TeamLineup
from app.ui.design.app_cursor import pointing_hand_cursor


class LineupPitch(QWidget):
    """横向布阵球场（自绘）。"""

    player_clicked = pyqtSignal(str, str)  # person_id, name

    def __init__(
        self,
        team_a: TeamLineup,
        team_b: TeamLineup,
        *,
        color_a: str = "#FF5470",
        color_b: str = "#FFFFFF",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._a = team_a
        self._b = team_b
        self._color_a = QColor(color_a)
        self._color_b = QColor(color_b)
        # 点击命中区：(圆心矩形, person_id, name)
        self._nodes: list[tuple[QRectF, str, str]] = []
        self.setMinimumHeight(480)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.setCursor(pointing_hand_cursor())

    # ── 阵型 → 列分组 ──────────────────────────
    @staticmethod
    def _columns(team: TeamLineup) -> list[list[LineupPlayer]]:
        players = list(team.starters)
        gk = [p for p in players if p.is_goalkeeper][:1]
        rest = [p for p in players if p not in gk]
        rest.sort(key=lambda p: (p.formation_place or 99))

        cols: list[list[LineupPlayer]] = []
        if gk:
            cols.append(gk)

        idx = 0
        lines = team.formation_lines
        if lines:
            for cnt in lines:
                col: list[LineupPlayer] = []
                for _ in range(cnt):
                    if idx < len(rest):
                        col.append(rest[idx])
                        idx += 1
                if col:
                    cols.append(col)
        # 阵型与实际人数不一致时，把剩余球员补到最后一列
        while idx < len(rest):
            if cols:
                cols[-1].append(rest[idx])
            else:
                cols.append([rest[idx]])
            idx += 1
        return cols

    # ── 半场布点 ──────────────────────────────
    @staticmethod
    def _layout_half(
        cols: list[list[LineupPlayer]], rect: QRectF, left_side: bool
    ) -> list[tuple[LineupPlayer, QPointF]]:
        out: list[tuple[LineupPlayer, QPointF]] = []
        ncol = max(1, len(cols))
        for ci, col in enumerate(cols):
            frac = (ci + 0.5) / ncol
            if left_side:
                x = rect.left() + frac * rect.width()
            else:
                x = rect.right() - frac * rect.width()
            n = max(1, len(col))
            for ri, pl in enumerate(col):
                yfrac = (ri + 0.5) / n
                y = rect.top() + yfrac * rect.height()
                out.append((pl, QPointF(x, y)))
        return out

    # ── 事件 ─────────────────────────────────
    def mousePressEvent(self, ev) -> None:
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        pos = ev.position()
        for rectf, pid, name in self._nodes:
            if rectf.contains(pos) and pid:
                self.player_clicked.emit(pid, name)
                return

    # ── 绘制 ─────────────────────────────────
    def paintEvent(self, _ev) -> None:
        self._nodes.clear()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = QRectF(self.rect())
        pitch = rect.adjusted(6, 6, -6, -6)
        self._draw_pitch(p, pitch)

        # 球员可布区域：左右各留白给门将，上下留白给姓名标签
        play = pitch.adjusted(
            pitch.width() * 0.015, 30, -pitch.width() * 0.015, -22
        )
        left_half = QRectF(play.left(), play.top(), play.width() / 2, play.height())
        right_half = QRectF(
            play.center().x(), play.top(), play.width() / 2, play.height()
        )

        cols_a = self._columns(self._a)
        cols_b = self._columns(self._b)

        # 自适应号码牌半径
        col_count = max(len(cols_a), len(cols_b), 1)
        max_rows = max(
            [len(c) for c in cols_a] + [len(c) for c in cols_b] + [1]
        )
        radius = min(
            (play.width() / 2) / col_count / 2.3,
            play.height() / max_rows / 2.7,
            23.0,
        )
        radius = max(13.0, radius)

        pos_a = self._layout_half(cols_a, left_half, left_side=True)
        pos_b = self._layout_half(cols_b, right_half, left_side=False)

        for pl, center in pos_a:
            self._draw_node(p, pl, center, radius, self._color_a, dark_text=False)
        for pl, center in pos_b:
            self._draw_node(p, pl, center, radius, self._color_b, dark_text=True)

    def _draw_pitch(self, p: QPainter, r: QRectF) -> None:
        # 圆角草地底
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.save()
        p.setClipPath(path)

        grad = QLinearGradient(r.topLeft(), r.bottomLeft())
        grad.setColorAt(0.0, QColor("#1F8A4C"))
        grad.setColorAt(1.0, QColor("#176B3B"))
        p.fillRect(r, grad)

        # 竖向修剪条纹（深浅相间）
        stripes = 12
        sw = r.width() / stripes
        for i in range(stripes):
            if i % 2 == 0:
                p.fillRect(
                    QRectF(r.left() + i * sw, r.top(), sw, r.height()),
                    QColor(255, 255, 255, 14),
                )

        # 白色场地标线
        line = QPen(QColor(255, 255, 255, 165), 2)
        p.setPen(line)
        p.setBrush(Qt.BrushStyle.NoBrush)
        inner = r.adjusted(10, 10, -10, -10)
        p.drawRoundedRect(inner, 4, 4)

        # 中线（竖直）+ 中圈
        cx = inner.center().x()
        p.drawLine(QPointF(cx, inner.top()), QPointF(cx, inner.bottom()))
        cr = min(inner.height(), inner.width()) * 0.12
        p.drawEllipse(QPointF(cx, inner.center().y()), cr, cr)
        p.setBrush(QColor(255, 255, 255, 165))
        p.drawEllipse(QPointF(cx, inner.center().y()), 3, 3)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # 左右禁区 + 球门区
        box_h = inner.height() * 0.52
        box_w = inner.width() * 0.10
        small_h = inner.height() * 0.28
        small_w = inner.width() * 0.045
        cy = inner.center().y()
        # 左
        p.drawRect(QRectF(inner.left(), cy - box_h / 2, box_w, box_h))
        p.drawRect(QRectF(inner.left(), cy - small_h / 2, small_w, small_h))
        # 右
        p.drawRect(QRectF(inner.right() - box_w, cy - box_h / 2, box_w, box_h))
        p.drawRect(
            QRectF(inner.right() - small_w, cy - small_h / 2, small_w, small_h)
        )
        p.restore()

    def _draw_node(
        self,
        p: QPainter,
        pl: LineupPlayer,
        center: QPointF,
        radius: float,
        base: QColor,
        *,
        dark_text: bool,
    ) -> None:
        cx, cy = center.x(), center.y()
        circle_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        # 圆牌阴影
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 70))
        p.drawEllipse(QRectF(cx - radius, cy - radius + 2, radius * 2, radius * 2))

        # 圆牌主体（渐变）
        grad = QLinearGradient(circle_rect.topLeft(), circle_rect.bottomLeft())
        grad.setColorAt(0.0, base.lighter(115))
        grad.setColorAt(1.0, base.darker(108))
        p.setBrush(grad)
        p.setPen(QPen(QColor(255, 255, 255, 220), 2))
        p.drawEllipse(circle_rect)

        # 号码
        num = pl.number or ""
        f = QFont(self.font())
        f.setPointSizeF(max(9.0, radius * 0.78))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#15213B") if dark_text else QColor("#FFFFFF"))
        p.drawText(circle_rect, int(Qt.AlignmentFlag.AlignCenter), num)

        # 队长 C 标
        if pl.captain:
            cap_r = radius * 0.42
            cap_rect = QRectF(
                cx + radius - cap_r, cy - radius - cap_r * 0.5, cap_r * 2, cap_r * 2
            )
            p.setPen(QPen(QColor(255, 255, 255, 220), 1.4))
            p.setBrush(QColor("#FFC53D"))
            p.drawEllipse(cap_rect)
            cf = QFont(self.font())
            cf.setPointSizeF(max(6.0, cap_r * 1.0))
            cf.setBold(True)
            p.setFont(cf)
            p.setPen(QColor("#5A3D00"))
            p.drawText(cap_rect, int(Qt.AlignmentFlag.AlignCenter), "C")

        # 姓名标签（半透明深色药丸）
        name = pl.name or ""
        nf = QFont(self.font())
        nf.setPointSizeF(max(8.0, radius * 0.52))
        nf.setBold(True)
        p.setFont(nf)
        fm = p.fontMetrics()
        max_w = radius * 4.4
        elided = fm.elidedText(name, Qt.TextElideMode.ElideRight, int(max_w))
        tw = fm.horizontalAdvance(elided)
        th = fm.height()
        pad_x, pad_y = 6.0, 2.0
        label_rect = QRectF(
            cx - tw / 2 - pad_x,
            cy + radius + 3,
            tw + pad_x * 2,
            th + pad_y * 2,
        )
        lp = QPainterPath()
        lp.addRoundedRect(label_rect, 6, 6)
        p.setPen(Qt.PenStyle.NoPen)
        p.fillPath(lp, QColor(8, 14, 24, 175))
        p.setPen(QColor("#F2F5FF"))
        p.drawText(label_rect, int(Qt.AlignmentFlag.AlignCenter), elided)

        # 记录命中区（圆 + 姓名整体）
        hit = QRectF(
            cx - radius, cy - radius, radius * 2, radius * 2 + th + 8
        )
        self._nodes.append((hit, pl.person_id, pl.name))
