"""射手 / 助攻榜单行 —— 对齐目标设计稿的「扁平榜单条」。

布局（自左至右）
----------------
* 名次徽章：扁平圆角方块（并列名次直接显示相同数字，如 1 1 1 … 6 6）。
  冠军组（值=最高）用金色，其余用中性玻璃底。
* 球员头像：圆形描边。
* 姓名（粗体）+ 第二行「真实国旗图 + 所属球队」。
* 位置胶囊：草绿描边胶囊（中场 / 前锋 / 边锋…）。
* 长进度条：冠军组金色，其余草绿。
* 右侧大数字 + 单位（进球 / 助攻）。

相比旧版的改动
----------------
* 去掉了会呼吸发光的大奖牌（观感杂乱、与设计稿不符、且耗 CPU），
  改为干净的扁平名次徽章。
* 国旗由 emoji 改为 ``FlagIcon`` 真实位图（emoji 国旗在 Windows /
  部分 Linux 无法完整渲染）。
* 仍用纯 ``QFrame`` + ``paintEvent`` 自绘背景，规避 ``QScrollArea`` +
  阴影特效导致的「整列堆叠」渲染 bug。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
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
from app.ui.widgets.team_logo import TeamLogo
from app.ui.design.app_cursor import pointing_hand_cursor

# 冠军组（最高值）金色，其余草绿；黄牌榜用琥珀黄
_GOLD = "#FFC53D"
_GREEN = "#2ED883"
_AMBER = "#FFC93C"


class _RankBadge(QWidget):
    """扁平圆角名次徽章。"""

    def __init__(self, rank: int, leader: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rank = rank
        self._leader = leader
        self.setFixedSize(40, 40)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r, 11, 11)

        if self._leader:
            grad = QLinearGradient(r.topLeft(), r.bottomRight())
            grad.setColorAt(0.0, QColor("#FFE08A"))
            grad.setColorAt(1.0, QColor("#F5B524"))
            p.fillPath(path, grad)
            p.setPen(QPen(QColor(255, 255, 255, 150), 1))
            p.drawPath(path)
            txt = QColor("#5A3D00")
        else:
            p.fillPath(path, QColor(255, 255, 255, 20))
            p.setPen(QPen(QColor(255, 255, 255, 36), 1))
            p.drawPath(path)
            txt = QColor("#C9D2EC")

        f = QFont(self.font())
        f.setPointSize(14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(txt)
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), str(self._rank))


class _Bar(QWidget):
    """渐变水平进度条。"""

    def __init__(self, value: int, maximum: int, accent: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._v = value
        self._max = max(1, maximum)
        self._accent = QColor(accent)
        self.setFixedHeight(12)
        self.setMinimumWidth(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        bg = QPainterPath()
        bg.addRoundedRect(r, 6, 6)
        p.fillPath(bg, QColor(255, 255, 255, 22))

        ratio = max(0.05, min(1.0, self._v / self._max))
        fr = QRectF(r.x(), r.y(), r.width() * ratio, r.height())
        fp = QPainterPath()
        fp.addRoundedRect(fr, 6, 6)
        ac = self._accent
        grad = QLinearGradient(fr.topLeft(), fr.topRight())
        c1 = QColor(ac)
        c1.setAlpha(235)
        c2 = QColor(ac.lighter(125))
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        p.fillPath(fp, grad)


class RankingRow(QFrame):
    """单行排行榜（对齐设计稿）。

    Parameters
    ----------
    player : PlayerRanking
    max_count : int
        当前列表最大值，用于计算进度条比例与判断「冠军组」。
    """

    player_clicked = pyqtSignal(PlayerRanking)
    team_clicked = pyqtSignal(str)

    def __init__(self, player: PlayerRanking, max_count: int) -> None:
        super().__init__()
        self._player = player
        self._max = max(1, max_count)
        self._leader = (player.value or 0) >= self._max
        _rest_color = _AMBER if player.ranking_type.is_discipline else _GREEN
        self._rest_color = _rest_color
        self._accent = QColor(_GOLD if self._leader else _rest_color)
        self._hover = False
        self.setObjectName("RankingRow")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(80)
        self.setCursor(pointing_hand_cursor())
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 12, 24, 12)
        outer.setSpacing(16)

        # 1. 名次徽章
        outer.addWidget(_RankBadge(player.rank, self._leader))

        # 2. 头像
        outer.addWidget(PlayerAvatar(player.person_logo, size=52))

        # 3. 姓名 + 国旗 + 球队
        prof = profile_for(player)
        info = QVBoxLayout()
        info.setSpacing(3)
        info.setContentsMargins(0, 0, 0, 0)
        name = QLabel(player.person_name)
        nf = QFont()
        nf.setPointSize(13)
        nf.setBold(True)
        name.setFont(nf)
        name.setStyleSheet("color:#FFFFFF;")
        info.addWidget(name)

        team_row = QHBoxLayout()
        team_row.setSpacing(7)
        team_row.setContentsMargins(0, 0, 0, 0)
        team_row.addWidget(FlagIcon(player.team_name, height=22))
        team_lbl = QLabel(player.team_name)
        team_lbl.setStyleSheet("color:#9AA3BE; font-size:11.5px; font-weight:600;")
        team_row.addWidget(team_lbl)
        team_row.addStretch(1)
        team_w = QWidget()
        team_w.setLayout(team_row)
        team_w.setCursor(pointing_hand_cursor())
        team_w.mousePressEvent = self._team_click  # type: ignore[assignment]
        info.addWidget(team_w)

        info_w = QWidget()
        info_w.setLayout(info)
        info_w.setFixedWidth(210)
        outer.addWidget(info_w, 0)

        # 4. 位置胶囊（草绿描边）
        pos_chip = QLabel(prof.position)
        pos_chip.setStyleSheet(
            "color:#9DF5C4; font-size:11px; font-weight:800;"
            "background: rgba(46,216,131,0.12);"
            "border:1px solid rgba(46,216,131,0.45);"
            "border-radius:11px; padding:4px 13px;"
        )
        pos_chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        outer.addWidget(pos_chip)

        # 5. 进度条
        bar = _Bar(player.value, self._max, _GOLD if self._leader else _rest_color)
        outer.addWidget(bar, 1)

        # 6. 大数字 + 单位
        count_box = QVBoxLayout()
        count_box.setSpacing(0)
        cnum = QLabel(player.display)
        cnum.setStyleSheet(
            f"color:{_GOLD if self._leader else '#FFFFFF'};"
            "font-size:26px; font-weight:900;"
        )
        cnum.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_box.addWidget(cnum)
        unit_txt = player.ranking_type.unit
        unit = QLabel(unit_txt)
        unit.setStyleSheet("color:#B0BEC5; font-size: 10.5px; font-weight:700;")
        unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_box.addWidget(unit)
        cnt_w = QWidget()
        cnt_w.setLayout(count_box)
        cnt_w.setFixedWidth(82)
        outer.addWidget(cnt_w)

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
        path.addRoundedRect(r, 16, 16)

        # 背景 —— 顶亮玻璃
        bg = QLinearGradient(r.topLeft(), r.bottomLeft())
        bg.setColorAt(0.0, QColor(255, 255, 255, 16))
        bg.setColorAt(1.0, QColor(255, 255, 255, 6))
        p.fillPath(path, bg)

        ac = self._accent
        # 左侧 accent 暖光（冠军组更明显）
        warm = QLinearGradient(r.topLeft(), r.topRight())
        warm.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(),
                                    70 if self._leader else 26))
        warm.setColorAt(0.45, QColor(ac.red(), ac.green(), ac.blue(), 0))
        p.fillPath(path, warm)

        if self._hover:
            p.fillPath(path, QColor(255, 255, 255, 20))

        pen_col = (QColor(ac.red(), ac.green(), ac.blue(), 220)
                   if self._hover else QColor(255, 255, 255, 28))
        p.setPen(QPen(pen_col, 1.4))
        p.drawPath(path)
