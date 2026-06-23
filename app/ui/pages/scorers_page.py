"""射手榜 / 助攻榜（FC25 风格大卡）。

修复
----
原版把行容器包在 ``Card`` 里再 ``QScrollArea.setWidget()``，导致 Qt
对带 ``QGraphicsDropShadowEffect`` 的 widget 整体渲染到 pixmap 时
子控件丢失，整片区域呈现为单色。本次重构改用普通 ``QWidget`` 作为
滚动宿主。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.player import PlayerRanking, RankingType
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.misc import Card
from app.ui.widgets.podium_card import PodiumCard
from app.ui.widgets.ranking_row import RankingRow

log = logging.getLogger(__name__)


class RankingPage(BasePage):
    """射手榜或助攻榜（取决于初始化时的 ranking_type）。"""

    player_clicked = pyqtSignal(PlayerRanking)
    team_clicked = pyqtSignal(str)

    def __init__(self, service: DataService, rtype: RankingType) -> None:
        super().__init__()
        self._service = service
        self._rtype = rtype
        self.title = rtype.label
        self.subtitle = rtype.en

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(14)

        # ── 滚动列表 —— 关键：用普通 QWidget，不要 Card ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        self._scroll = scroll
        self._list_layout: QVBoxLayout | None = None
        self._list_host: QWidget | None = None
        # 不在 __init__ 中提前 setWidget —— 等到 _render() 第一次被调用时
        # 再创建。否则在某些 Qt 平台 / offscreen 模式下，二次 setWidget
        # 会让 ScrollArea 的内部尺寸缓存与新 widget 的子 layout 不一致，
        # 出现「子行 geom = sizeHint，所有行堆叠在 (0,0)」的 bug。

    def _build_scroll_host(self) -> None:
        """每次刷新都重新创建 host —— 避免动态 mutate 导致 QScrollArea
        在 Qt 内部缓存的子布局尺寸不更新（行堆叠 bug 的核心成因）。

        关键顺序：先 ``setWidget`` 再创建 ``QVBoxLayout``。这样
        Qt 在 attach widget 时已经为 widget 设置了大小（跟随 viewport），
        随后建立 layout 时拓扑信息一致，避免 layout 缓存里残留 (0,0,
        sizeHint) 而忽略真实尺寸 —— 正是用户看到「行全部堆叠」的根因。
        """
        list_host = QWidget()
        self._scroll.setWidget(list_host)         # 先 attach
        self._list_layout = QVBoxLayout(list_host)  # 再建 layout
        self._list_layout.setContentsMargins(2, 4, 2, 16)
        self._list_layout.setSpacing(10)
        self._list_host = list_host

    # ─────────────────────────────────────────
    def set_rtype(self, rtype: RankingType, *, force: bool = False) -> None:
        """切换榜单类型并重新拉取数据。"""
        if rtype == self._rtype and self._content_ready and not force:
            return
        self._rtype = rtype
        self.title = rtype.label
        self.subtitle = rtype.en
        self.refresh(force=force)

    # ─────────────────────────────────────────
    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            data = await self._service.fetch_ranking(self._rtype, force=force)
            self._render(data)
        self.run_async(runner)

    def _render(self, data: list[PlayerRanking]) -> None:
        # 重新创建 host —— 强制 QScrollArea 重新布局新的子树
        self._build_scroll_host()

        if not data:
            empty = QLabel("暂无数据 ⚽")
            empty.setStyleSheet("color:#B0BEC5; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
            self._list_layout.addStretch(1)
            return

        max_count = max((p.value or 0) for p in data) or 1
        anim_targets: list[QWidget] = []

        # ── Top-3 领奖台（金/银/铜冠军卡）──────────────────
        # 数据不足 3 人时跳过，全部走扁平榜单。
        rest = data
        if len(data) >= 3:
            podium = self._build_podium(data[:3])
            self._list_layout.addWidget(podium)
            anim_targets.append(podium)
            rest = data[3:]

        # ── 其余名次（4+）：紧凑扁平榜单条 ──────────────────
        rows: list[QWidget] = []
        for p in rest:
            row = RankingRow(p, max_count)
            row.player_clicked.connect(self.player_clicked.emit)
            row.team_clicked.connect(self.team_clicked.emit)
            self._list_layout.addWidget(row)
            rows.append(row)
        anim_targets.extend(rows[:14])

        # 末尾留白
        self._list_layout.addStretch(1)

        # 入场动画：纯淡入（不再做逐行 geometry 位移 —— 那会与布局相互
        # 拉扯，在长榜单上明显卡顿）
        stagger_fade(anim_targets, step=32, dx=0, dy=0)

    def _build_podium(self, top3: list[PlayerRanking]) -> QWidget:
        """把前三名摆成领奖台：亚军(左) · 冠军(中, 更高) · 季军(右)。"""
        host = QWidget()
        row = QHBoxLayout(host)
        row.setContentsMargins(2, 4, 2, 8)
        row.setSpacing(14)
        row.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # 显示顺序：2 1 3（place 索引：1=银 0=金 2=铜）
        for place in (1, 0, 2):
            if place >= len(top3):
                continue
            card = PodiumCard(top3[place], place)
            card.player_clicked.connect(self.player_clicked.emit)
            card.team_clicked.connect(self.team_clicked.emit)
            row.addWidget(card, 1)
        return host
