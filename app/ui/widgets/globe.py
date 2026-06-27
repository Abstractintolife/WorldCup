"""交互式 3D 地球仪控件。

* 鼠标拖动 → 360° 自由旋转（左右改变经度 yaw，上下改变纬度 pitch）。
* 松手后自动缓慢自转。
* 发光经纬网格 + 大陆点阵（来自 ne_110m_land 烤出的低分辨率掩膜）。
* 国家队以霓虹标记点 + 圆形国旗呈现；悬停高亮、点击进入球队。
* ``spin_to(lat, lon)`` 平滑地把某个坐标转到正面中央。

纯 QPainter 实现（正交投影），无需 OpenGL，跨平台稳定。
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget

from app.services.geo_data import land_points
from app.services.image_service import ImageService
from app.ui.design.frame_clock import FrameClock
from app.ui.design.app_cursor import pointing_hand_cursor


def _to_vec(lat: float, lon: float) -> tuple[float, float, float]:
    la = math.radians(lat)
    lo = math.radians(lon)
    cla = math.cos(la)
    return (cla * math.sin(lo), math.sin(la), cla * math.cos(lo))


@dataclass
class GlobeMarker:
    team_id: str
    name: str
    lat: float
    lon: float
    color: QColor
    logo: str | None = None
    group: str | None = None
    vec: tuple[float, float, float] = field(default=(0.0, 0.0, 0.0))
    # 每帧更新的屏幕坐标缓存
    _sx: float = 0.0
    _sy: float = 0.0
    _front: bool = False


class GlobeWidget(QWidget):
    """可旋转的发光地球仪。"""

    team_clicked = pyqtSignal(str)        # team_id
    team_hovered = pyqtSignal(str)        # team_id（"" 表示无）

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(420, 420)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        # 旋转状态（度）
        self._yaw = -20.0
        self._pitch = 18.0
        self._auto = True
        self._auto_speed = 0.18

        # 平滑转场目标
        self._target_yaw: float | None = None
        self._target_pitch: float | None = None

        # 交互状态
        self._dragging = False
        self._moved = False
        self._last_pos = QPointF()
        self._hover_idx = -1
        self._selected_id: str | None = None

        # 数据
        self._markers: list[GlobeMarker] = []
        self._land = [(_to_vec(lat, lon)) for (lat, lon) in land_points()]
        self._graticule = self._build_graticule()
        self._stars = self._build_stars(150)
        self._img = ImageService.instance()
        self._img.image_ready.connect(lambda *_: self.update())

        # 颜色主题（可由外部覆盖）
        self.ocean_a = QColor("#0b3a66")
        self.ocean_b = QColor("#04101f")
        self.land_color = QColor("#1fd1ff")
        self.grid_color = QColor(0, 119, 255)
        self.glow_color = QColor(0, 180, 255)

        # 动画由全局唯一 FrameClock 驱动（单一帧调度器）。可见时订阅、
        # 隐藏时退订 —— 地球仪页不在前台时彻底零开销。
        self._clock = FrameClock.instance()
        self._subscribed = False

        # 逐帧渲染缓存（运行时性能优化）：
        # 1) 静态背景（星点 + 大气辉光 + 海洋球体）对固定尺寸/配色完全不变，
        #    缓存成一张 pixmap，仅在尺寸或配色变化时重建，每帧只做一次 blit。
        self._bg_cache = None
        self._bg_key = None
        # 2) 队标圆形头像按 (logo, 直径) 缓存平滑缩放结果，避免每帧对每个
        #    marker 重复跑 SmoothTransformation。
        self._scaled_cache: dict = {}

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._subscribed:
            self._clock.subscribe(self._tick)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._tick)
            self._subscribed = False

    # ── 公共 API ──────────────────────────────
    def set_markers(self, markers: list[GlobeMarker]) -> None:
        for m in markers:
            m.vec = _to_vec(m.lat, m.lon)
        self._markers = markers
        self.update()

    def set_selected(self, team_id: str | None) -> None:
        self._selected_id = team_id
        self.update()

    def spin_to(self, lat: float, lon: float) -> None:
        """平滑地把 (lat, lon) 转到正面中心。"""
        self._target_yaw = -lon
        self._target_pitch = max(-80.0, min(80.0, lat))
        self._auto = False

    def set_auto_rotate(self, enabled: bool) -> None:
        self._auto = enabled

    # ── 几何辅助 ──────────────────────────────
    @staticmethod
    def _build_graticule() -> list[list[tuple[float, float, float]]]:
        lines: list[list[tuple[float, float, float]]] = []
        # 纬线（每 30°）
        for lat in range(-60, 90, 30):
            line = [_to_vec(lat, lon) for lon in range(-180, 181, 6)]
            lines.append(line)
        # 经线（每 30°）
        for lon in range(-180, 180, 30):
            line = [_to_vec(lat, lon) for lat in range(-90, 91, 6)]
            lines.append(line)
        return lines

    @staticmethod
    def _build_stars(n: int) -> list[tuple[float, float, float]]:
        rnd = random.Random(2026)
        return [(rnd.random(), rnd.random(), rnd.random()) for _ in range(n)]

    def _rot(self, v: tuple[float, float, float]) -> tuple[float, float, float]:
        ay = math.radians(self._yaw)
        ap = math.radians(self._pitch)
        cy, sy = math.cos(ay), math.sin(ay)
        cp, sp = math.cos(ap), math.sin(ap)
        x, y, z = v
        # 绕 Y
        x1 = x * cy + z * sy
        z1 = -x * sy + z * cy
        y1 = y
        # 绕 X
        y2 = y1 * cp - z1 * sp
        z2 = y1 * sp + z1 * cp
        return (x1, y2, z2)

    # ── 动画 ─────────────────────────────────
    def _tick(self, _t: float = 0.0, _dt: float = 0.0) -> None:
        changed = False
        if self._target_yaw is not None or self._target_pitch is not None:
            if self._target_yaw is not None:
                # 走最短角差
                diff = (self._target_yaw - self._yaw + 180) % 360 - 180
                if abs(diff) < 0.4:
                    self._yaw = self._target_yaw
                    self._target_yaw = None
                else:
                    self._yaw += diff * 0.12
                changed = True
            if self._target_pitch is not None:
                d = self._target_pitch - self._pitch
                if abs(d) < 0.3:
                    self._pitch = self._target_pitch
                    self._target_pitch = None
                else:
                    self._pitch += d * 0.12
                changed = True
        elif self._auto and not self._dragging:
            self._yaw = (self._yaw + self._auto_speed) % 360
            changed = True
        if changed:
            self.update()

    # ── 绘制 ─────────────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        R = min(w, h) * 0.42

        # 静态背景层（星点/大气/海洋）一次性缓存，逐帧仅 blit。
        self._blit_static_bg(p, w, h, cx, cy, R)

        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), R, R)
        p.setClipPath(clip)

        # 预算旋转三角函数（一次）
        ay = math.radians(self._yaw)
        ap = math.radians(self._pitch)
        cyaw, syaw = math.cos(ay), math.sin(ay)
        cp, sp = math.cos(ap), math.sin(ap)

        def project(v):
            x, y, z = v
            x1 = x * cyaw + z * syaw
            z1 = -x * syaw + z * cyaw
            y2 = y * cp - z1 * sp
            z2 = y * sp + z1 * cp
            return (cx + x1 * R, cy - y2 * R, z2)

        # 大陆点阵
        p.setPen(Qt.PenStyle.NoPen)
        lc = self.land_color
        for v in self._land:
            sx, sy, z = project(v)
            if z <= 0.02:
                continue
            shade = 0.35 + 0.65 * z
            a = int(235 * shade)
            p.setBrush(QColor(lc.red(), lc.green(), lc.blue(), a))
            rr = 1.5 + 1.7 * z
            p.drawEllipse(QPointF(sx, sy), rr, rr)

        # 经纬网格
        grid = self.grid_color
        for line in self._graticule:
            pen = QPen(QColor(grid.red(), grid.green(), grid.blue(), 60), 1.0)
            p.setPen(pen)
            prev = None
            for v in line:
                sx, sy, z = project(v)
                if z <= 0:
                    prev = None
                    continue
                if prev is not None:
                    p.drawLine(QPointF(prev[0], prev[1]), QPointF(sx, sy))
                prev = (sx, sy)

        p.setClipping(False)

        # 标记点（国家队）
        hover_marker: GlobeMarker | None = None
        for i, m in enumerate(self._markers):
            sx, sy, z = project(m.vec)
            m._sx, m._sy, m._front = sx, sy, z > 0.02
            if not m._front:
                continue
            self._draw_marker(p, m, sx, sy, z, selected=(m.team_id == self._selected_id))
            if i == self._hover_idx:
                hover_marker = m

        # 悬停标签放最后画（不被遮挡）
        if hover_marker is not None and hover_marker._front:
            self._draw_label(p, hover_marker)

    def _blit_static_bg(self, p, w, h, cx, cy, R) -> None:
        """绘制（并缓存）静态背景：星点 + 大气辉光 + 海洋球体。

        这些图元对固定的窗口尺寸与配色完全不变，烘焙到一张 ARGB pixmap，
        仅当尺寸/配色变化时重建；逐帧只需一次 drawPixmap。
        """
        from PyQt6.QtGui import QPixmap
        key = (w, h, self.glow_color.rgba(), self.ocean_a.rgba(), self.ocean_b.rgba())
        if self._bg_cache is None or self._bg_key != key:
            pm = QPixmap(w, h)
            pm.fill(Qt.GlobalColor.transparent)
            bp = QPainter(pm)
            bp.setRenderHint(QPainter.RenderHint.Antialiasing)
            # 背景星点
            bp.setPen(Qt.PenStyle.NoPen)
            for sx, sy, sb in self._stars:
                a = int(40 + sb * 120)
                bp.setBrush(QColor(150, 190, 255, a))
                rr = 0.6 + sb * 1.4
                bp.drawEllipse(QPointF(sx * w, sy * h), rr, rr)
            # 大气辉光
            atmo = QRadialGradient(cx, cy, R * 1.35)
            gc = QColor(self.glow_color)
            atmo.setColorAt(0.72, QColor(gc.red(), gc.green(), gc.blue(), 0))
            atmo.setColorAt(0.88, QColor(gc.red(), gc.green(), gc.blue(), 70))
            atmo.setColorAt(1.0, QColor(gc.red(), gc.green(), gc.blue(), 0))
            bp.setBrush(QBrush(atmo))
            bp.drawEllipse(QPointF(cx, cy), R * 1.35, R * 1.35)
            # 海洋球体（带高光偏移）
            ocean = QRadialGradient(cx - R * 0.32, cy - R * 0.34, R * 1.5)
            ocean.setColorAt(0.0, self.ocean_a)
            ocean.setColorAt(1.0, self.ocean_b)
            bp.setBrush(QBrush(ocean))
            bp.setPen(QPen(QColor(self.glow_color.red(), self.glow_color.green(),
                                  self.glow_color.blue(), 160), 1.4))
            bp.drawEllipse(QPointF(cx, cy), R, R)
            bp.end()
            self._bg_cache = pm
            self._bg_key = key
        p.drawPixmap(0, 0, self._bg_cache)

    def _draw_marker(self, p: QPainter, m: GlobeMarker, sx: float, sy: float,
                     z: float, *, selected: bool) -> None:
        # 调大尺寸：基础半径 9~14（旧版 4~7），充分占据屏幕，更易点击 / 看清
        col = QColor(m.color)
        base = 9.0 + 5.0 * z
        if selected:
            base += 3.0
        # 外发光（更明显）
        glow = QRadialGradient(sx, sy, base * 3.4)
        glow.setColorAt(0.0, QColor(col.red(), col.green(), col.blue(), 200))
        glow.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QPointF(sx, sy), base * 3.4, base * 3.4)

        # 圆形国旗（若已缓存）
        pm = self._img.request(m.logo) if m.logo else None
        rr = base + 4.0
        if pm is not None and not pm.isNull():
            path = QPainterPath()
            path.addEllipse(QPointF(sx, sy), rr, rr)
            p.save()
            p.setClipPath(path)
            target = QRectF(sx - rr, sy - rr, rr * 2, rr * 2)
            sz = int(rr * 2)
            ck = (pm.cacheKey(), sz)  # cacheKey 随 pixmap 内容变化，避免缓存陈旧
            scaled = self._scaled_cache.get(ck)
            if scaled is None:
                scaled = pm.scaled(sz, sz,
                                   Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                   Qt.TransformationMode.SmoothTransformation)
                if len(self._scaled_cache) > 512:
                    self._scaled_cache.clear()
                self._scaled_cache[ck] = scaled
            p.drawPixmap(target, scaled, QRectF(scaled.rect()))
            p.restore()
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 240) if selected else col, 2.4))
            p.drawEllipse(QPointF(sx, sy), rr, rr)
        else:
            p.setBrush(col)
            p.setPen(QPen(QColor(255, 255, 255, 230), 2.0))
            p.drawEllipse(QPointF(sx, sy), base, base)

        if selected:
            ring = QPen(QColor(255, 255, 255, 220), 2.0)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(ring)
            p.drawEllipse(QPointF(sx, sy), rr + 5, rr + 5)

    def _draw_label(self, p: QPainter, m: GlobeMarker) -> None:
        text = m.name
        p.setFont(self.font())
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text) + 18
        th = fm.height() + 8
        bx = m._sx + 12
        by = m._sy - th - 8
        if bx + tw > self.width():
            bx = m._sx - tw - 12
        if by < 0:
            by = m._sy + 12
        rect = QRectF(bx, by, tw, th)
        p.setBrush(QColor(7, 11, 20, 230))
        p.setPen(QPen(QColor(m.color), 1.3))
        p.drawRoundedRect(rect, 9, 9)
        p.setPen(QColor("#eaf0ff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    # ── 交互 ─────────────────────────────────
    def _hit_test(self, pos: QPointF) -> int:
        best = -1
        best_d = 22.0 ** 2  # 命中区扩大到 22px（与新的 marker 半径匹配）
        for i, m in enumerate(self._markers):
            if not m._front:
                continue
            d = (m._sx - pos.x()) ** 2 + (m._sy - pos.y()) ** 2
            if d < best_d:
                best_d = d
                best = i
        return best

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._moved = False
            self._last_pos = ev.position()
            # 用户开始手动操作 —— 关闭自动自转，松手后地球停在原地（不再「停不下来」）
            self._auto = False
            self._target_yaw = self._target_pitch = None
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, ev) -> None:
        pos = ev.position()
        if self._dragging:
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            if abs(dx) + abs(dy) > 2:
                self._moved = True
            self._last_pos = pos
            self._target_yaw = self._target_pitch = None
            self._yaw = (self._yaw + dx * 0.35) % 360
            # 上下方向跟手（向下拖 → 视角向下），修正此前的反向
            self._pitch = max(-85.0, min(85.0, self._pitch + dy * 0.35))
            self.update()
        else:
            idx = self._hit_test(pos)
            if idx != self._hover_idx:
                self._hover_idx = idx
                self.setCursor(pointing_hand_cursor() if idx >= 0
                               else Qt.CursorShape.OpenHandCursor)
                self.team_hovered.emit(self._markers[idx].team_id if idx >= 0 else "")
                self.update()

    def mouseReleaseEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if not self._moved:
                idx = self._hit_test(ev.position())
                if idx >= 0:
                    m = self._markers[idx]
                    self.team_clicked.emit(m.team_id)

    def leaveEvent(self, _ev) -> None:
        if self._hover_idx != -1:
            self._hover_idx = -1
            self.team_hovered.emit("")
            self.update()

    def wheelEvent(self, ev) -> None:
        # 滚轮控制自转：上滚 = 恢复并加快自转，下滚 = 减速直至停止
        delta = ev.angleDelta().y()
        if delta > 0:
            self._auto_speed = min(1.2, self._auto_speed + 0.06)
            self._auto = True
        else:
            self._auto_speed = max(0.0, self._auto_speed - 0.06)
            if self._auto_speed <= 0.0:
                self._auto = False
        ev.accept()
