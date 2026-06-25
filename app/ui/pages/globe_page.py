"""地球仪页：360° 旋转地球找国家队，点击进入阵容。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.team import Team
from app.services.data_service import DataService
from app.services.geo_data import team_coord
from app.ui.pages.base import BasePage
from app.ui.theme import DARK
from app.ui.widgets.globe import GlobeMarker, GlobeWidget
from app.ui.widgets.misc import Card
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor


class _TeamRow(QWidget):
    """侧栏中的一支球队（队徽 + 名称 + 组别）。"""

    clicked = pyqtSignal(str)
    hovered = pyqtSignal(str)

    def __init__(self, team: Team, color: QColor) -> None:
        super().__init__()
        self._team = team
        self.setFixedHeight(52)
        self.setCursor(pointing_hand_cursor())
        self.setProperty("teamRow", True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._base_qss = (
            "QWidget[teamRow=\"true\"] { background: rgba(255,255,255,0.03);"
            " border-radius: 12px; }"
            "QWidget[teamRow=\"true\"]:hover { background: rgba(255,255,255,0.09); }"
        )
        self.setStyleSheet(self._base_qss)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 12, 6)
        lay.setSpacing(10)
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{color.name()}; font-size:13px;")
        lay.addWidget(dot)
        lay.addWidget(TeamLogo(team.logo, size=30, shape="circle"))
        name = QLabel(team.name)
        name.setStyleSheet("font-size:14px; font-weight:700;")
        lay.addWidget(name)
        lay.addStretch(1)
        if team.group:
            grp = QLabel(team.group)
            grp.setStyleSheet(
                f"color:{color.name()}; background: rgba(255,255,255,0.06);"
                "font-size:11px; padding:2px 8px; border-radius:8px; font-weight:700;"
            )
            lay.addWidget(grp)

    def set_active(self, active: bool) -> None:
        if active:
            self.setStyleSheet(
                "QWidget[teamRow=\"true\"] { background: rgba(0,119,255,0.22);"
                " border: 1px solid rgba(0,119,255,0.6); border-radius: 12px; }"
            )
        else:
            self.setStyleSheet(self._base_qss)

    def enterEvent(self, _ev) -> None:
        self.hovered.emit(self._team.team_id)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._team.team_id)


class GlobePage(BasePage):
    title = "地球仪"
    subtitle = "转动地球 · 寻找你的国家队 · 点击查看阵容"

    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._teams: list[Team] = []
        self._rows: dict[str, _TeamRow] = {}

        host = self.content_widget()
        outer = QHBoxLayout(host)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(16)

        # ── 左：地球 ──
        globe_card = Card(padding=0)
        gl = QVBoxLayout(globe_card)
        gl.setContentsMargins(8, 8, 8, 8)
        gl.setSpacing(0)
        self._globe = GlobeWidget()
        gl.addWidget(self._globe, 1)
        hint = QLabel("🖱  拖动旋转（松手即停）　·　滚轮上滚恢复自转 / 下滚减速　·　点击发光标记进入球队")
        hint.setStyleSheet("color:#B0BEC5; font-size:12px; padding:8px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(hint)
        outer.addWidget(globe_card, 1)

        # ── 右：球队列表 ──
        side = Card(padding=0)
        side.setFixedWidth(312)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(14, 16, 10, 14)
        sl.setSpacing(10)
        head = QLabel("🌍  参赛国家队")
        head.setStyleSheet("font-size:16px; font-weight:800;")
        sl.addWidget(head)
        self._count = QLabel("")
        self._count.setStyleSheet("color:#B0BEC5; font-size:12px;")
        sl.addWidget(self._count)
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  搜索球队…")
        self._search.textChanged.connect(self._render_list)
        sl.addWidget(self._search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        sl.addWidget(scroll, 1)
        self._list_host = QWidget()
        scroll.setWidget(self._list_host)
        self._list_lay = QVBoxLayout(self._list_host)
        self._list_lay.setContentsMargins(0, 0, 6, 0)
        self._list_lay.setSpacing(5)
        self._list_lay.addStretch(1)
        outer.addWidget(side)

        # 信号
        self._globe.team_clicked.connect(self._on_pick)
        self._globe.team_hovered.connect(self._on_globe_hover)

    # ── 数据 ──────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            groups, _ko, _km = await self._service.fetch_standings(force=force)
            self._teams = self._service.teams_from_standings(groups)
            self._build_markers()
            self._render_list()

        if self._teams and not force:
            return
        self.run_async(runner)

    def _color_for(self, group: str | None) -> QColor:
        return DARK.group_color(group or "")

    def _build_markers(self) -> None:
        markers: list[GlobeMarker] = []
        for t in self._teams:
            coord = team_coord(t.name)
            if not coord:
                continue
            lat, lon = coord
            markers.append(
                GlobeMarker(
                    team_id=t.team_id,
                    name=t.name,
                    lat=lat,
                    lon=lon,
                    color=self._color_for(t.group),
                    logo=t.logo,
                    group=t.group,
                )
            )
        self._globe.set_markers(markers)
        self._count.setText(f"共 {len(self._teams)} 支 · 已定位 {len(markers)} 支")

    def _render_list(self) -> None:
        # 清空（保留末尾 stretch）
        while self._list_lay.count() > 1:
            item = self._list_lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._rows.clear()
        q = self._search.text().strip().lower()
        items = [t for t in self._teams if (not q or q in t.name.lower())]
        items.sort(key=lambda t: ((t.group or "Z"), t.rank or 99))
        for t in items:
            row = _TeamRow(t, self._color_for(t.group))
            row.clicked.connect(self._on_pick)
            row.hovered.connect(self._on_row_hover)
            self._rows[t.team_id] = row
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)

    # ── 交互 ──────────────────────────────────
    def _on_row_hover(self, team_id: str) -> None:
        self._globe.set_selected(team_id)
        coord = self._coord_of(team_id)
        if coord:
            self._globe.spin_to(*coord)

    def _on_globe_hover(self, team_id: str) -> None:
        for tid, row in self._rows.items():
            row.set_active(tid == team_id and bool(team_id))

    def _on_pick(self, team_id: str) -> None:
        self._globe.set_selected(team_id)
        coord = self._coord_of(team_id)
        if coord:
            self._globe.spin_to(*coord)
        self.team_clicked.emit(team_id)

    def _coord_of(self, team_id: str) -> tuple[float, float] | None:
        for t in self._teams:
            if t.team_id == team_id:
                return team_coord(t.name)
        return None
