"""单队布阵评分球场 —— 竖向球场 + 每名球员的 whoscored 风格评分牌。

与 :class:`app.ui.widgets.lineup_pitch.LineupPitch`（横向、双队）不同，本控件
专为**球队详情页**设计：

* 竖向球场：门将在最下、前锋在最上，按阵型分线自下而上铺开。
* 每名球员一个圆形号码牌 + 姓名标签 + 右上角**评分徽章**（按分值着色：
  ≥8.0 深绿 / ≥7.0 草绿 / ≥6.5 琥珀 / 其余 灰）。
* 队长加金色「C」标，球星号码牌描金。
* 点击任一球员 → ``player_clicked(person_id, name)``。

坐标完全由阵型字符串（如 ``4-3-3``）+ ``formation_place`` 推导。
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

from app.services.team_preview import RatedPlayer
from app.ui.design.app_cursor import pointing_hand_cursor


def rating_color(rating: float) -> str:
    """whoscored 风格的评分着色。"""
    if rating >= 8.0:
        return "#1FA363"
    if rating >= 7.5:
        return "#2ED883"
    if rating >= 7.0:
        return "#8BC34A"
    if rating >= 6.5:
        return "#F2B33D"
    return "#9AA3BE"


class FormationPitch(QWidget):
    """竖向单队布阵评分球场（自绘）。"""

    player_clicked = pyqtSignal(str, str)  # person_id, name

    def __init__(
        self,
        players: list[RatedPlayer],
        formation: str,
        *,
        accent: str = "#00BFFF",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._players = list(players)
        self._formation = formation or ""
        self._accent = QColor(accent)
        self._nodes: list[tuple[QRectF, str, str]] = []
        self.setMinimumHeight(560)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.setCursor(pointing_hand_cursor())

    # ── 阵型 → 由下到上的行分组 ──────────────────
    def _rows(self) -> list[list[RatedPlayer]]:
        players = sorted(self._players, key=lambda p: p.formation_place)
        if not players:
            return []
        gk = [players[0]]
        rest = players[1:]
        lines = [int(x) for x in self._formation.replace("：", "-").split("-")
                 if x.strip().isdigit()]
        rows: list[list[RatedPlayer]] = [gk]
        idx = 0
        if lines:
            for cnt in lines:
                row: list[RatedPlayer] = []
                for _ in range(cnt):
                    if idx < len(rest):
                        row.append(rest[idx])
                        idx += 1
                if row:
                    rows.append(row)
        while idx < len(rest):
            rows[-1].append(rest[idx])
            idx += 1
        return rows

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

        rows = self._rows()  # rows[0] = 门将（最下方）
        if not rows:
            return

        play = pitch.adjusted(18, 26, -18, -30)
        n_rows = len(rows)
        radius = min(play.width() / 6.2, play.height() / (n_rows * 2.6), 26.0)
        radius = max(15.0, radius)

        for ri, row in enumerate(rows):
            # ri=0 门将 → 底部；最后一行 → 顶部
            yfrac = 1.0 - (ri + 0.5) / n_rows
            y = play.top() + yfrac * play.height()
            n = max(1, len(row))
            for ci, rp in enumerate(row):
                xfrac = (ci + 0.5) / n
                x = play.left() + xfrac * play.width()
                self._draw_node(p, rp, QPointF(x, y), radius)

    def _draw_pitch(self, p: QPainter, r: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.save()
        p.setClipPath(path)

        grad = QLinearGradient(r.topLeft(), r.bottomLeft())
        grad.setColorAt(0.0, QColor("#1F8A4C"))
        grad.setColorAt(1.0, QColor("#176B3B"))
        p.fillRect(r, grad)

        # 横向修剪条纹
        stripes = 11
        sh = r.height() / stripes
        for i in range(stripes):
            if i % 2 == 0:
                p.fillRect(
                    QRectF(r.left(), r.top() + i * sh, r.width(), sh),
                    QColor(255, 255, 255, 13),
                )

        line = QPen(QColor(255, 255, 255, 150), 2)
        p.setPen(line)
        p.setBrush(Qt.BrushStyle.NoBrush)
        inner = r.adjusted(10, 10, -10, -10)
        p.drawRoundedRect(inner, 4, 4)

        cy = inner.center().y()
        # 中线（水平）+ 中圈
        p.drawLine(QPointF(inner.left(), cy), QPointF(inner.right(), cy))
        cr = min(inner.height(), inner.width()) * 0.12
        p.drawEllipse(inner.center(), cr, cr)
        p.setBrush(QColor(255, 255, 255, 150))
        p.drawEllipse(inner.center(), 3, 3)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # 上 / 下禁区
        box_w = inner.width() * 0.5
        box_h = inner.height() * 0.10
        small_w = inner.width() * 0.26
        small_h = inner.height() * 0.045
        cx = inner.center().x()
        p.drawRect(QRectF(cx - box_w / 2, inner.bottom() - box_h, box_w, box_h))
        p.drawRect(QRectF(cx - small_w / 2, inner.bottom() - small_h, small_w, small_h))
        p.drawRect(QRectF(cx - box_w / 2, inner.top(), box_w, box_h))
        p.drawRect(QRectF(cx - small_w / 2, inner.top(), small_w, small_h))
        p.restore()

    def _draw_node(
        self, p: QPainter, rp: RatedPlayer, center: QPointF, radius: float
    ) -> None:
        cx, cy = center.x(), center.y()
        circle_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        # 阴影
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 70))
        p.drawEllipse(QRectF(cx - radius, cy - radius + 2, radius * 2, radius * 2))

        # 号码牌主体
        base = QColor(self._accent)
        grad = QLinearGradient(circle_rect.topLeft(), circle_rect.bottomLeft())
        grad.setColorAt(0.0, base.lighter(120))
        grad.setColorAt(1.0, base.darker(112))
        p.setBrush(grad)
        border = QColor("#FFD700") if rp.is_star else QColor(255, 255, 255, 220)
        p.setPen(QPen(border, 3 if rp.is_star else 2))
        p.drawEllipse(circle_rect)

        # 号码
        num = rp.number or ""
        f = QFont(self.font())
        f.setPointSizeF(max(9.0, radius * 0.74))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(circle_rect, int(Qt.AlignmentFlag.AlignCenter), num)

        # 队长 C 标（左上）
        if rp.is_captain:
            cap_r = radius * 0.42
            cap_rect = QRectF(
                cx - radius - cap_r * 0.5, cy - radius - cap_r * 0.5,
                cap_r * 2, cap_r * 2,
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

        # 评分徽章（右上）
        rcol = QColor(rating_color(rp.rating))
        badge_w = radius * 1.5
        badge_h = radius * 0.78
        badge_rect = QRectF(
            cx + radius - badge_w * 0.55, cy - radius - badge_h * 0.45,
            badge_w, badge_h,
        )
        bp = QPainterPath()
        bp.addRoundedRect(badge_rect, badge_h * 0.45, badge_h * 0.45)
        p.setPen(QPen(QColor(0, 0, 0, 90), 1))
        p.fillPath(bp, rcol)
        p.drawPath(bp)
        rf = QFont(self.font())
        rf.setPointSizeF(max(7.5, radius * 0.46))
        rf.setBold(True)
        p.setFont(rf)
        p.setPen(QColor("#0B0E16"))
        p.drawText(badge_rect, int(Qt.AlignmentFlag.AlignCenter), f"{rp.rating:.1f}")

        # 姓名标签
        name = rp.name or ""
        nf = QFont(self.font())
        nf.setPointSizeF(max(8.0, radius * 0.5))
        nf.setBold(True)
        p.setFont(nf)
        fm = p.fontMetrics()
        max_w = radius * 4.6
        elided = fm.elidedText(name, Qt.TextElideMode.ElideRight, int(max_w))
        tw = fm.horizontalAdvance(elided)
        th = fm.height()
        pad_x, pad_y = 6.0, 2.0
        label_rect = QRectF(
            cx - tw / 2 - pad_x, cy + radius + 3, tw + pad_x * 2, th + pad_y * 2
        )
        lp = QPainterPath()
        lp.addRoundedRect(label_rect, 6, 6)
        p.setPen(Qt.PenStyle.NoPen)
        p.fillPath(lp, QColor(8, 14, 24, 180))
        p.setPen(QColor("#F2F5FF"))
        p.drawText(label_rect, int(Qt.AlignmentFlag.AlignCenter), elided)

        hit = QRectF(cx - radius, cy - radius, radius * 2, radius * 2 + th + 8)
        self._nodes.append((hit, rp.person_id, rp.name))
