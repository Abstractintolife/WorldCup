"""portrait_lineup_pitch —— 球员「大头照」布阵图（用于概览页实时比赛面板）。

在一块横向迷你球场上还原对阵双方的首发阵容：

* 左半场主队、右半场客队（球门各在最外侧），按 ``formation`` + ``formation_place``
  推导每名球员的列（防线→锋线）与行（同列内上下均布）。
* 每名球员用**圆形大头照**（经 :class:`ImageService` 异步加载，未到位时回退为
  带球衣号的纯色圆牌），照片下方标注**姓名简写**。
* 队长加金色「C」标；点击球员牌 → ``player_clicked(person_id, name)``。

照片优先级见 :func:`app.services.player_portraits.best_portrait`
（本地高清图 > 名人 Wikimedia 大图 > 懂球帝头像）。
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
    QPixmap,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from app.models.lineup import LineupPlayer, TeamLineup
from app.services.image_service import ImageService
from app.services.player_portraits import best_portrait
from app.ui.design.app_cursor import pointing_hand_cursor


def short_player_name(name: str) -> str:
    """姓名简写：取「·」后的姓氏段，并截断到 4 个字符，紧凑显示。"""
    n = (name or "").strip()
    if not n:
        return ""
    if "·" in n:
        n = n.split("·")[-1]
    elif " " in n:
        n = n.split(" ")[-1]
    return n[:4]


class PortraitLineupPitch(QWidget):
    """双队「大头照」布阵球场（自绘）。"""

    player_clicked = pyqtSignal(str, str)  # person_id, name

    def __init__(
        self,
        team_a: TeamLineup,
        team_b: TeamLineup,
        *,
        color_a: str = "#FF5470",
        color_b: str = "#36D6E6",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._a = team_a
        self._b = team_b
        self._color_a = QColor(color_a)
        self._color_b = QColor(color_b)
        self._nodes: list[tuple[QRectF, str, str]] = []
        self._img = ImageService.instance()
        # 球员 person_id/name → 头像 URL（首发构建时解析一次）。
        self._urls: dict[str, str] = {}
        self._collect_urls()
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(pointing_hand_cursor())

    # ── 头像 URL 收集 + 异步加载订阅 ──────────────
    def _collect_urls(self) -> None:
        # 已改用球衣号码圆牌渲染，不再加载球员照片（省去网络请求与裁剪开销）。
        return

    def showEvent(self, ev) -> None:
        super().showEvent(ev)

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)

    # ── 阵型 → 列分组（与 LineupPitch 一致）──────────
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
        for cnt in team.formation_lines:
            col: list[LineupPlayer] = []
            for _ in range(cnt):
                if idx < len(rest):
                    col.append(rest[idx])
                    idx += 1
            if col:
                cols.append(col)
        while idx < len(rest):
            (cols[-1] if cols else cols.append([]) or cols[-1]).append(rest[idx])
            idx += 1
        return cols

    @staticmethod
    def _layout_half(cols, rect: QRectF, left_side: bool):
        out = []
        ncol = max(1, len(cols))
        for ci, col in enumerate(cols):
            frac = (ci + 0.5) / ncol
            x = (rect.left() + frac * rect.width()) if left_side \
                else (rect.right() - frac * rect.width())
            n = max(1, len(col))
            for ri, pl in enumerate(col):
                y = rect.top() + (ri + 0.5) / n * rect.height()
                out.append((pl, QPointF(x, y)))
        return out

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
        pitch = rect.adjusted(4, 4, -4, -4)
        self._draw_pitch(p, pitch)

        play = pitch.adjusted(pitch.width() * 0.01, 18,
                              -pitch.width() * 0.01, -16)
        left = QRectF(play.left(), play.top(), play.width() / 2, play.height())
        right = QRectF(play.center().x(), play.top(), play.width() / 2, play.height())
        cols_a = self._columns(self._a)
        cols_b = self._columns(self._b)
        col_count = max(len(cols_a), len(cols_b), 1)
        max_rows = max([len(c) for c in cols_a] + [len(c) for c in cols_b] + [1])
        # 缩小球衣号圆牌，避免相邻列 / 行的圆与姓名标签互相重叠（更大的除数 +
        # 更低的上限 / 下限），让 11 人也能在小面板里互不挤压地铺开。
        radius = min((play.width() / 2) / col_count / 2.8,
                     play.height() / max_rows / 3.0, 15.0)
        radius = max(8.5, radius)
        for pl, c in self._layout_half(cols_a, left, True):
            self._draw_player(p, pl, c, radius, self._color_a)
        for pl, c in self._layout_half(cols_b, right, False):
            self._draw_player(p, pl, c, radius, self._color_b)

    def _draw_pitch(self, p: QPainter, r: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(r, 12, 12)
        p.save()
        p.setClipPath(path)
        grad = QLinearGradient(r.topLeft(), r.bottomLeft())
        grad.setColorAt(0.0, QColor("#1F8A4C"))
        grad.setColorAt(1.0, QColor("#176B3B"))
        p.fillRect(r, grad)
        stripes = 10
        sw = r.width() / stripes
        for i in range(stripes):
            if i % 2 == 0:
                p.fillRect(QRectF(r.left() + i * sw, r.top(), sw, r.height()),
                           QColor(255, 255, 255, 13))
        p.setPen(QPen(QColor(255, 255, 255, 150), 1.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        inner = r.adjusted(8, 8, -8, -8)
        p.drawRoundedRect(inner, 4, 4)
        cx = inner.center().x()
        p.drawLine(QPointF(cx, inner.top()), QPointF(cx, inner.bottom()))
        cr = min(inner.height(), inner.width()) * 0.12
        p.drawEllipse(QPointF(cx, inner.center().y()), cr, cr)
        p.restore()

    def _circular_portrait(self, pm: QPixmap, d: int) -> QPixmap:
        """把任意图裁成居中正方形再缩放为直径 d 的圆形头像。"""
        side = min(pm.width(), pm.height())
        if side <= 0:
            return QPixmap()
        sq = pm.copy((pm.width() - side) // 2, (pm.height() - side) // 2, side, side)
        sq = sq.scaled(d, d, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                       Qt.TransformationMode.SmoothTransformation)
        out = QPixmap(d, d)
        out.fill(Qt.GlobalColor.transparent)
        pp = QPainter(out)
        pp.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(QRectF(0, 0, d, d))
        pp.setClipPath(clip)
        pp.drawPixmap(0, 0, sq)
        pp.end()
        return out

    def _draw_player(self, p: QPainter, pl: LineupPlayer, center: QPointF,
                     radius: float, base: QColor) -> None:
        cx, cy = center.x(), center.y()
        circle = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        # 阴影
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 80))
        p.drawEllipse(QRectF(cx - radius, cy - radius + 2, radius * 2, radius * 2))

        # 纯色圆牌 + 球衣号（按需求：用球衣号码替代球员照片，圆圈更小、互不重叠）。
        grad = QLinearGradient(circle.topLeft(), circle.bottomLeft())
        grad.setColorAt(0.0, base.lighter(118))
        grad.setColorAt(1.0, base.darker(110))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(circle)
        num = (pl.number or "").strip()
        if num:
            f = QFont(self.font())
            f.setPointSizeF(max(8.0, radius * 0.95))
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor("#FFFFFF"))
            p.drawText(circle, int(Qt.AlignmentFlag.AlignCenter), num)
        # 描边（队伍色）
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(base.lighter(125), 2))
        p.drawEllipse(circle)

        # 队长 C 标
        if pl.captain:
            cap_r = radius * 0.4
            cap_rect = QRectF(cx + radius - cap_r, cy - radius - cap_r * 0.4,
                              cap_r * 2, cap_r * 2)
            p.setPen(QPen(QColor(255, 255, 255, 220), 1.2))
            p.setBrush(QColor("#FFC53D"))
            p.drawEllipse(cap_rect)
            cf = QFont(self.font())
            cf.setPointSizeF(max(5.5, cap_r * 1.0))
            cf.setBold(True)
            p.setFont(cf)
            p.setPen(QColor("#5A3D00"))
            p.drawText(cap_rect, int(Qt.AlignmentFlag.AlignCenter), "C")

        # 姓名简写标签
        name = short_player_name(pl.name)
        nf = QFont(self.font())
        nf.setPointSizeF(max(7.0, radius * 0.5))
        nf.setBold(True)
        p.setFont(nf)
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(name)
        th = fm.height()
        label = QRectF(cx - tw / 2 - 5, cy + radius + 2, tw + 10, th + 3)
        lp = QPainterPath()
        lp.addRoundedRect(label, 5, 5)
        p.setPen(Qt.PenStyle.NoPen)
        p.fillPath(lp, QColor(8, 14, 24, 185))
        p.setPen(QColor("#F2F5FF"))
        p.drawText(label, int(Qt.AlignmentFlag.AlignCenter), name)

        self._nodes.append((QRectF(cx - radius, cy - radius, radius * 2,
                                   radius * 2 + th + 6), pl.person_id, pl.name))
