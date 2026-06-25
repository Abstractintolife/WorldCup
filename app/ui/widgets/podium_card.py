"""Top-3 领奖台「冠军卡片」—— 射手 / 助攻榜头三名的高光呈现。

设计目标（对齐 FIFA / ESPN / Apple Sports 的数据大屏语言）
--------------------------------------------------------------
* 把榜单最重要的「前三名」从单调的扁平长条里抽出来，做成
  **金 / 银 / 铜** 三张悬浮玻璃冠军卡。
* 视觉层级：冠军（金）卡更高、更亮、奖牌带皇冠光晕；亚军（银）、
  季军（铜）略矮，构成经典「领奖台」错落。
* 复用项目既有材质：玻璃顶亮渐变 + 微弱白边（与 ``RankingRow`` /
  ``Card`` 一致），头像沿用异步加载的 ``PlayerAvatar``，国旗用真实
  位图 ``FlagIcon``，位置胶囊沿用草绿描边风格。
* 纯 ``QFrame`` + ``paintEvent`` 自绘背景（规避 ``QScrollArea`` +
  阴影特效的整列堆叠渲染 bug，与 ``RankingRow`` 同策略）。

奖牌配色
--------
======  ========  ========================================
名次     主色       语义
======  ========  ========================================
1（金）  #FFC53D   冠军 · 大力神杯金
2（银）  #C9D4E6   亚军 · 月银
3（铜）  #E0894B   季军 · 古铜
======  ========  ========================================
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
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.player import PlayerRanking, RankingType
from app.services.player_profiles import profile_for
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.player_avatar import PlayerAvatar
from app.ui.design.app_cursor import pointing_hand_cursor

# 金 / 银 / 铜 主色（与名次 1/2/3 对应）
_MEDALS: tuple[tuple[str, str, str], ...] = (
    ("#FFC53D", "#FFE08A", "#8A5A00"),   # 金：主色 / 高光 / 暗描边
    ("#C9D4E6", "#EEF3FB", "#5C6678"),   # 银
    ("#E0894B", "#FFC089", "#6E3A12"),   # 铜
)


class _RingAvatar(QWidget):
    """带金/银/铜渐变光环的圆形头像容器。

    ``PlayerAvatar``（异步远程图）居中托管为子控件；本控件在
    ``paintEvent`` 中绘制其外侧的渐变光环 + 柔光，光环半径大于头像，
    因此始终可见（父控件 paintEvent 先于子控件绘制）。
    """

    def __init__(self, url: str | None, accent: str, hi: str,
                 *, box: int = 96, avatar: int = 74,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._accent = QColor(accent)
        self._hi = QColor(hi)
        self._box = box
        self.setFixedSize(box, box)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(PlayerAvatar(url, size=avatar),
                      0, Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(3, 3, -3, -3)
        c = r.center()
        rad = r.width() / 2

        # 外侧柔光
        glow = QRadialGradient(c, rad)
        g0 = QColor(self._accent)
        g0.setAlpha(120)
        g1 = QColor(self._accent)
        g1.setAlpha(0)
        glow.setColorAt(0.62, g1)
        glow.setColorAt(0.86, g0)
        glow.setColorAt(1.0, g1)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(c, rad, rad)

        # 渐变光环
        ring = QLinearGradient(r.topLeft(), r.bottomRight())
        ring.setColorAt(0.0, self._hi)
        ring.setColorAt(0.5, self._accent)
        ring.setColorAt(1.0, self._hi)
        pen = QPen(ring, 3.4)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        ring_rect = r.adjusted(7, 7, -7, -7)
        p.drawEllipse(ring_rect)


class PodiumCard(QFrame):
    """单张领奖台冠军卡（金/银/铜由 ``place`` 决定，0=冠军）。

    Parameters
    ----------
    player : PlayerRanking
    place : int
        0 / 1 / 2 → 金 / 银 / 铜。
    """

    player_clicked = pyqtSignal(PlayerRanking)
    team_clicked = pyqtSignal(str)

    def __init__(self, player: PlayerRanking, place: int) -> None:
        super().__init__()
        self._player = player
        self._place = max(0, min(2, place))
        self._champion = self._place == 0
        accent, hi, deep = _MEDALS[self._place]
        self._accent = QColor(accent)
        self._hi = QColor(hi)
        self._hover = False

        self.setObjectName("PodiumCard")
        self.setCursor(pointing_hand_cursor())
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # 冠军卡更高，构成领奖台错落。
        # 高度需容纳：名次徽章 + 光环头像 + 姓名 + 国旗/球队 + 位置胶囊 +
        # 大数字 + 单位（含间距与内边距）。旧版固定 286/262 偏矮，导致
        # 头像/姓名/国旗与底部大数字相互重叠 —— 这里给足高度彻底修复。
        self.setFixedHeight(392 if self._champion else 360)

        col = QVBoxLayout(self)
        col.setContentsMargins(18, 16 if self._champion else 30, 18, 18)
        col.setSpacing(8)
        col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # 1. 奖牌名次徽章
        badge = QLabel(str(player.rank))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(34, 34)
        badge.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {hi}, stop:1 {accent});"
            f"color:{deep}; font-size:16px; font-weight:900;"
            f"border-radius:17px; border:1px solid rgba(255,255,255,0.55);"
        )
        col.addWidget(badge, 0, Qt.AlignmentFlag.AlignHCenter)

        # 2. 光环头像
        col.addWidget(
            _RingAvatar(player.person_logo, accent, hi,
                        box=104 if self._champion else 92,
                        avatar=80 if self._champion else 70),
            0, Qt.AlignmentFlag.AlignHCenter,
        )

        # 3. 姓名
        prof = profile_for(player)
        name = QLabel(player.person_name)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nf = QFont()
        nf.setPointSize(15 if self._champion else 13)
        nf.setBold(True)
        name.setFont(nf)
        name.setStyleSheet("color:#FFFFFF;")
        col.addWidget(name)

        # 4. 国旗 + 球队
        team_row = QHBoxLayout()
        team_row.setSpacing(7)
        team_row.setContentsMargins(0, 0, 0, 0)
        team_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        team_row.addWidget(FlagIcon(player.team_name, height=20))
        team_lbl = QLabel(player.team_name)
        team_lbl.setStyleSheet(
            "color:#9AA3BE; font-size:11.5px; font-weight:600;")
        team_row.addWidget(team_lbl)
        team_w = QWidget()
        team_w.setLayout(team_row)
        team_w.setCursor(pointing_hand_cursor())
        team_w.mousePressEvent = self._team_click  # type: ignore[assignment]
        col.addWidget(team_w, 0, Qt.AlignmentFlag.AlignHCenter)

        # 5. 位置胶囊（草绿描边）
        pos_chip = QLabel(prof.position)
        pos_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_chip.setStyleSheet(
            "color:#9DF5C4; font-size:10.5px; font-weight:800;"
            "background: rgba(46,216,131,0.12);"
            "border:1px solid rgba(46,216,131,0.45);"
            "border-radius:10px; padding:3px 12px;"
        )
        pos_chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        col.addWidget(pos_chip, 0, Qt.AlignmentFlag.AlignHCenter)

        col.addStretch(1)

        # 6. 大数字 + 单位
        big = QLabel(player.display)
        big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        big.setStyleSheet(
            f"color:{accent}; font-size:{40 if self._champion else 32}px;"
            "font-weight:900;"
        )
        col.addWidget(big)
        unit_txt = player.ranking_type.unit
        if unit_txt:
            unit = QLabel(unit_txt)
            unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            unit.setStyleSheet("color:#B0BEC5; font-size:11px; font-weight:700;")
            col.addWidget(unit)

    # ── 事件 ─────────────────────────────────
    def enterEvent(self, _ev) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, _ev) -> None:
        self._hover = False
        self.update()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.player_clicked.emit(self._player)
        super().mousePressEvent(ev)

    def _team_click(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.team_clicked.emit(self._player.team_id)

    # ── 绘制 ────────────────────────────────
    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 20, 20)

        # 玻璃底（顶亮渐变）
        bg = QLinearGradient(r.topLeft(), r.bottomLeft())
        bg.setColorAt(0.0, QColor(255, 255, 255, 20))
        bg.setColorAt(1.0, QColor(255, 255, 255, 7))
        p.fillPath(path, bg)

        ac = self._accent
        # 顶部奖牌色辉光（冠军更强）
        top = QRadialGradient(QPointF(r.center().x(), r.top()), r.width())
        a0 = 120 if self._champion else 80
        top.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), a0))
        top.setColorAt(0.55, QColor(ac.red(), ac.green(), ac.blue(), 0))
        p.fillPath(path, top)

        if self._hover:
            p.fillPath(path, QColor(255, 255, 255, 18))

        # 边框：常态用奖牌色低透明，悬停加亮
        border = QColor(ac.red(), ac.green(), ac.blue(),
                        230 if self._hover else 130)
        p.setPen(QPen(border, 1.6 if self._champion else 1.3))
        p.drawPath(path)
