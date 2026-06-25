"""球员详情页 —— 懂球帝风格完整资料页（对任意球员有效，含未参加本届世界杯者）。

数据来源
---------
* ``DataService.fetch_player_detail``  → 真实档案（身高/体重/惯用脚/国籍/俱乐部/
  号码/身价/合同/奖杯）。
* ``DataService.fetch_player_ability`` → FC26 风能力值（OVR + 真实六维雷达）。
* 射手榜 / 助攻榜 → 本届世界杯进球 / 助攻 / 点球 / 排名（未参赛则为 0）。

布局
----
* 顶部 Hero：球员实景图（靠右）+ 红色光晕 + 姓名 + 国旗 + 位置/俱乐部 chip +
  年龄/身高/惯用脚 + 球衣号水印 + 红色伪签名。
* 4 KPI（进球 / 助攻 / 点球 / 排名）。
* 三栏：能力雷达（紫色 FC 风）· 综合能力（真实 OVR）· 近期比赛。
* 两栏：个人资料（生日/身高体重/身价/合同/注册位置/星级）· 荣誉奖杯。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import (
    QPointF,
    QRectF,
    QSize,
    Qt,
    pyqtSignal,
)
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
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match, MatchStatus
from app.models.person_match import PersonMatch
from app.models.player import PlayerRanking, RankingType
from app.models.player_detail import PlayerAbility, PlayerDetail
from app.services.data_service import DataService
from app.services.favorites import Favorites
from app.services.player_portraits import best_portrait
from app.services.player_profiles import PlayerProfile, profile_for, profile_from_detail
from app.services.player_stats import player_stats, stats_from_ability
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.favorite_button import FavoriteButton
from app.ui.widgets.flag_icon import FlagIcon
from app.ui.widgets.image_loader import RemoteCover, RemoteImage
from app.ui.widgets.misc import Card
from app.ui.widgets.radar import RadarChart
from app.ui.widgets.team_logo import TeamLogo
from app.utils.time_utils import fmt_time
from app.ui.design.app_cursor import pointing_hand_cursor

log = logging.getLogger(__name__)

# 雷达紫色（目标稿风格）
RADAR_COLOR = "#8B7DFF"
RADAR_GLOW = "#6C5CE7"


# ─────────────────────────────────────────────
class _PlayerHero(QWidget):
    """顶部 hero：球员大图 + 粒子 + 资料 + 球衣号水印 + 签名。"""

    team_clicked = pyqtSignal(str)
    back_clicked = pyqtSignal()

    HERO_HEIGHT = 360

    def __init__(
        self,
        profile: PlayerProfile,
        portrait: str | None,
        team_id: str,
        on_team_click=None,
        on_back=None,
    ) -> None:
        super().__init__()
        self._profile = profile
        self.setMinimumHeight(self.HERO_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 底层：球员实景图（靠右悬浮）
        self._cover = RemoteCover(self, accent="#00BFFF",
                                  overlay_top=0.32, overlay_bottom=0.18,
                                  anchor="right")
        self._cover.set_url(portrait)
        cover_glow = QGraphicsDropShadowEffect(self._cover)
        cover_glow.setBlurRadius(80)
        cover_glow.setOffset(0, 0)
        cover_glow.setColor(QColor(255, 0, 80, 180))
        self._cover.setGraphicsEffect(cover_glow)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(36, 22, 36, 28)
        outer.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(6)

        if on_back:
            back = QPushButton("←  返回")
            back.setProperty("ghost", True)
            back.setCursor(pointing_hand_cursor())
            back.clicked.connect(on_back)
            back.setStyleSheet(
                "QPushButton{background: rgba(0,0,0,0.45); color:#FFFFFF;"
                "border: 1px solid rgba(255,255,255,0.18); border-radius: 14px;"
                "padding: 6px 16px; font-weight:700; font-size:11.5px;}"
                "QPushButton:hover{background: rgba(0,191,255,0.32); color:#ffffff;"
                "border: 1px solid #00BFFF;}"
            )
            back.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            back_row = QHBoxLayout()
            back_row.addWidget(back)
            back_row.addStretch(1)
            left.addLayout(back_row)
            left.addSpacing(10)

        zh = QLabel(self._profile.name_zh)
        zh.setStyleSheet(
            "color:#ffffff; font-size:42px; font-weight:900; letter-spacing:1px;"
        )
        left.addWidget(zh)

        en = QLabel(self._profile.name_en)
        en.setStyleSheet(
            "color:rgba(255,255,255,0.78); font-size:15px; font-weight:600;"
            "letter-spacing:1px;"
        )
        left.addWidget(en)
        left.addSpacing(4)

        flag_row = QHBoxLayout()
        flag_row.setSpacing(10)
        flag_icon = FlagIcon(self._profile.nationality, height=36)
        flag_row.addWidget(flag_icon)
        country = QLabel(self._profile.nationality)
        country.setStyleSheet("color:#ffffff; font-size:14px; font-weight:800;")
        flag_row.addWidget(country)
        flag_row.addStretch(1)
        flag_w = QWidget(); flag_w.setLayout(flag_row)
        flag_w.setCursor(pointing_hand_cursor())
        if on_team_click and team_id:
            flag_w.mousePressEvent = (  # type: ignore[assignment]
                lambda _e, tid=team_id: on_team_click(tid)
            )
        left.addWidget(flag_w)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        for chip in (self._profile.position, self._profile.club):
            if not chip:
                continue
            l = QLabel(chip)
            l.setStyleSheet(
                "color:rgba(255,255,255,0.94); font-size:11.5px; font-weight:700;"
                "background: rgba(0,0,0,0.42); border:1px solid rgba(255,255,255,0.18);"
                "border-radius: 9px; padding: 3px 12px;"
            )
            l.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            meta_row.addWidget(l)
        meta_row.addStretch(1)
        left.addLayout(meta_row)
        left.addSpacing(2)

        details = QLabel(
            f"{self._profile.age}岁    ·    "
            f"身高 {self._profile.height_cm}cm    ·    "
            f"惯用脚 {self._profile.foot}"
        )
        details.setStyleSheet(
            "color:rgba(255,255,255,0.76); font-size:12.5px; font-weight:600;"
        )
        left.addWidget(details)
        left.addStretch(1)

        outer.addLayout(left, 5)
        outer.addStretch(1)

        right_spacer = QWidget()
        right_spacer.setMinimumWidth(260)
        outer.addWidget(right_spacer, 4)

    def resizeEvent(self, ev) -> None:
        self._cover.setGeometry(0, 0, self.width(), self.height())
        self._cover.lower()
        super().resizeEvent(ev)

    def paintEvent(self, ev) -> None:
        super().paintEvent(ev)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        spot_cx = rect.center().x() + rect.width() * 0.18
        spot_cy = rect.center().y() + rect.height() * 0.10
        spot_r = rect.height() * 1.2
        spot = QRadialGradient(QPointF(spot_cx, spot_cy), spot_r)
        spot.setColorAt(0.0, QColor(255, 0, 80, 70))
        spot.setColorAt(0.35, QColor(255, 0, 80, 30))
        spot.setColorAt(1.0, QColor(255, 0, 80, 0))
        p.fillRect(rect, spot)

        anchor_x = rect.right() - 36
        anchor_y = rect.top() + 28

        f = QFont(self.font())
        f.setPointSize(160)
        f.setBold(True)
        p.setFont(f)
        col = QColor(255, 255, 255, 38)
        p.setPen(col)
        fm = p.fontMetrics()
        num_text = str(self._profile.jersey)
        nw = fm.horizontalAdvance(num_text)
        p.drawText(anchor_x - nw, anchor_y + fm.ascent(), num_text)

        f2 = QFont(self.font())
        f2.setPointSize(24)
        f2.setBold(True)
        p.setFont(f2)
        family = self._profile.family_en
        f2_metrics = p.fontMetrics()
        fw = f2_metrics.horizontalAdvance(family)
        p.setPen(QColor(255, 79, 121, 245))
        family_y = anchor_y + fm.ascent() + 30
        p.drawText(anchor_x - fw, family_y, family)

        seed = self._profile.signature_seed
        p.setPen(QPen(QColor(255, 79, 121, 220), 2.6))
        bx = anchor_x - 130
        by = family_y + 28
        path = QPainterPath()
        path.moveTo(bx, by)
        c1x = bx + 24 + (seed % 16) - 8
        c1y = by - 14 - (seed >> 2 & 0x7)
        c2x = bx + 60 + (seed >> 4 & 0xF) - 8
        c2y = by + 18 + (seed >> 6 & 0x7)
        c3x = bx + 100 + (seed >> 8 & 0xF) - 8
        path.cubicTo(c1x, c1y, c2x, c2y, c3x, by - 6)
        path.cubicTo(c3x + 18, by - 16, bx + 130, by + 4, bx + 116, by + 14)
        p.drawPath(path)


# ─────────────────────────────────────────────
class _SmallMatchRow(QFrame):
    """近期比赛单行（FC 风格时间轴）。"""

    clicked = pyqtSignal(Match)

    def __init__(self, match: Match, focus_team_id: str) -> None:
        super().__init__()
        self._match = match
        self._hover = False
        self.setCursor(pointing_hand_cursor())
        self.setFixedHeight(80)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(22, 12, 14, 12)
        outer.setSpacing(12)

        d_box = QVBoxLayout(); d_box.setSpacing(0)
        date_top = QLabel(self._date_md(match))
        date_top.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:900;")
        date_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        d_box.addWidget(date_top)
        date_dow = QLabel(self._dow(match))
        date_dow.setStyleSheet("color:#B0BEC5; font-size:10.5px; font-weight:700;")
        date_dow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        d_box.addWidget(date_dow)
        d_w = QWidget(); d_w.setLayout(d_box); d_w.setFixedWidth(54)
        outer.addWidget(d_w)

        outer.addWidget(TeamLogo(match.team_a_logo, size=32, shape="circle"))

        if match.status == MatchStatus.PLAYED:
            score_text = match.display_score
        elif match.status == MatchStatus.FIXTURE:
            score_text = "-"
        else:
            score_text = match.display_score
        score = QLabel(score_text)
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if match.status == MatchStatus.PLAYED:
            score.setStyleSheet("color:#ffffff; font-size:17px; font-weight:900;")
        else:
            score.setStyleSheet("color:#B0BEC5; font-size:15px; font-weight:800;")
        score.setMinimumWidth(60)
        outer.addWidget(score, 1)

        outer.addWidget(TeamLogo(match.team_b_logo, size=32, shape="circle"))
        outer.addSpacing(6)

        time = QLabel(fmt_time(match.start_play))
        time.setStyleSheet("color:#B0BEC5; font-size:11.5px; font-weight:700;")
        time.setFixedWidth(46)
        time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(time)

        play = QLabel("▶")
        play.setFixedSize(32, 32)
        play.setAlignment(Qt.AlignmentFlag.AlignCenter)
        play.setStyleSheet(
            "background: rgba(0,191,255,0.18); color:#46D2FF;"
            "border: 1px solid rgba(0,191,255,0.5); border-radius: 16px;"
            "font-size: 11px; font-weight: 800;"
        )
        outer.addWidget(play)

    @staticmethod
    def _date_md(m: Match) -> str:
        from app.utils.time_utils import to_local
        local = to_local(m.start_play)
        return local.strftime("%m.%d") if local else "—"

    @staticmethod
    def _dow(m: Match) -> str:
        from app.utils.time_utils import to_local, WEEKDAYS_ZH
        local = to_local(m.start_play)
        return WEEKDAYS_ZH[local.weekday()] if local else ""

    def enterEvent(self, _ev): self._hover = True; self.update()
    def leaveEvent(self, _ev): self._hover = False; self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        offset = 8.0 if self._hover else 0.0
        rect = QRectF(self.rect()).adjusted(0.5 + offset, 0.5,
                                            -0.5 + offset, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 14.0, 14.0)

        if self._hover:
            p.fillPath(path, QColor(255, 79, 121, 30))
            p.setPen(QPen(QColor(255, 79, 121, 200), 1.3))
        else:
            p.fillPath(path, QColor(255, 255, 255, 8))
            p.setPen(QPen(QColor(255, 255, 255, 24), 1.0))
        p.drawPath(path)

        center_x = rect.left() + 12
        center_y = rect.center().y()
        line_pen = QPen(QColor(255, 79, 121, 60), 1.0)
        line_pen.setStyle(Qt.PenStyle.SolidLine)
        p.setPen(line_pen)
        p.drawLine(QPointF(center_x, rect.top()), QPointF(center_x, center_y - 6))
        p.drawLine(QPointF(center_x, center_y + 6), QPointF(center_x, rect.bottom()))

        glow = QRadialGradient(QPointF(center_x, center_y), 14)
        glow.setColorAt(0.0, QColor(255, 79, 121, 220))
        glow.setColorAt(1.0, QColor(255, 79, 121, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(QPointF(center_x, center_y), 14, 14)
        p.setBrush(QColor("#00BFFF"))
        p.drawEllipse(QPointF(center_x, center_y), 3.0, 3.0)
        p.setBrush(QColor(255, 255, 255, 220))
        p.drawEllipse(QPointF(center_x - 1.0, center_y - 1.0), 1.0, 1.0)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._match)


class _PersonMatchRow(QFrame):
    """球员近期比赛单行（真实数据：对阵 + 比分 + 个人进球/助攻/评分）。"""

    def __init__(self, pm: PersonMatch) -> None:
        super().__init__()
        self._pm = pm
        self.setFixedHeight(66)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 8, 14, 8)
        outer.setSpacing(10)

        # 日期 + 赛事
        d_box = QVBoxLayout(); d_box.setSpacing(1)
        date_top = QLabel(self._date_md(pm))
        date_top.setStyleSheet("color:#FFFFFF; font-size:13px; font-weight:900;")
        d_box.addWidget(date_top)
        comp = QLabel(pm.competition_name or "—")
        comp.setStyleSheet("color:#B0BEC5; font-size:9.5px; font-weight:700;")
        d_box.addWidget(comp)
        d_w = QWidget(); d_w.setLayout(d_box); d_w.setFixedWidth(64)
        outer.addWidget(d_w)

        # 主队 logo
        outer.addWidget(TeamLogo(pm.team_a_logo, size=26, shape="circle"))

        # 比分
        score = QLabel(pm.score_text)
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if pm.played:
            score.setStyleSheet("color:#ffffff; font-size:15px; font-weight:900;")
        else:
            score.setStyleSheet("color:#B0BEC5; font-size:13px; font-weight:800;")
        score.setMinimumWidth(48)
        outer.addWidget(score, 1)

        # 客队 logo
        outer.addWidget(TeamLogo(pm.team_b_logo, size=26, shape="circle"))

        outer.addSpacing(4)

        # 个人数据：进球 / 助攻 / 评分（各固定 40，与列头对齐）
        outer.addWidget(self._stat(str(pm.goals), "#00BFFF"))
        outer.addWidget(self._stat(str(pm.assists), "#FF9F43"))
        outer.addWidget(self._rating_chip(pm.best_rating))

    @staticmethod
    def _stat(value: str, color: str) -> QWidget:
        lab = QLabel(value if value else "-")
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lab.setFixedWidth(40)
        active = bool(value) and value not in ("0", "-")
        lab.setStyleSheet(
            f"color:{color if active else '#56607D'};"
            "font-size:15px; font-weight:900;"
        )
        return lab

    @staticmethod
    def _rating_chip(rating: str) -> QWidget:
        if not rating:
            lab = QLabel("-")
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lab.setFixedWidth(40)
            lab.setStyleSheet("color:#56607D; font-size:13px; font-weight:800;")
            return lab
        try:
            val = float(rating)
        except ValueError:
            val = 0.0
        if val >= 8.0:
            bg = "#2ED883"
        elif val >= 7.0:
            bg = "#4FACFE"
        elif val >= 6.0:
            bg = "#FF9F43"
        else:
            bg = "#B0BEC5"
        chip = QLabel(rating)
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setFixedWidth(40)
        chip.setStyleSheet(
            f"color:#0c0f18; background:{bg}; border-radius:8px;"
            "padding:3px 0; font-size:12.5px; font-weight:900;"
        )
        return chip

    @staticmethod
    def _date_md(pm: PersonMatch) -> str:
        from app.utils.time_utils import to_local
        local = to_local(pm.start_play)
        return local.strftime("%m.%d") if local else "—"

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 13.0, 13.0)
        p.fillPath(path, QColor(255, 255, 255, 8))
        p.setPen(QPen(QColor(255, 255, 255, 22), 1.0))
        p.drawPath(path)


class _KpiCard(QFrame):
    """单个 KPI 卡（FC26 风）。"""

    def __init__(self, label_zh: str, label_en: str, value: int,
                 color: str, icon: str) -> None:
        super().__init__()
        from app.ui.widgets.misc import GoldNumber
        self._color = QColor(color)
        self._hover = False
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 14, 22, 14)
        outer.setSpacing(2)

        is_gold = color in ("#FFD700", "#FFD700", "#FFE680")
        self._num = GoldNumber(font_size=46,
                                primary="#FFE680" if is_gold else "#FFFFFF",
                                secondary=color,
                                deep="#82430C" if is_gold else color)
        if not is_gold:
            self._num.set_colors("#ffffff", color, color)
        self._num.set_target(int(value))
        outer.addWidget(self._num)

        bot = QHBoxLayout()
        bot.setSpacing(10)
        ic = QLabel(icon)
        ic.setStyleSheet(
            f"color:{color}; font-weight:900; font-size:14px;"
            "background: rgba(255,255,255,0.06); border-radius:7px;"
            "padding: 2px 8px; min-width: 18px;"
        )
        ic.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        bot.addWidget(ic)

        col = QVBoxLayout(); col.setSpacing(0)
        zh = QLabel(label_zh)
        zh.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:800;")
        col.addWidget(zh)
        en = QLabel(label_en)
        en.setStyleSheet(
            "color:#B0BEC5; font-size:9.5px; font-weight:800; letter-spacing:1.6px;"
        )
        col.addWidget(en)
        bot.addLayout(col)
        bot.addStretch(1)
        outer.addLayout(bot)

    def enterEvent(self, _ev): self._hover = True; self.update()
    def leaveEvent(self, _ev): self._hover = False; self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, 24.0, 24.0)
        p.fillPath(path, QColor(20, 20, 30, 115))

        ac = self._color
        warm = QLinearGradient(r.topLeft(), r.topRight())
        warm.setColorAt(0.0, QColor(ac.red(), ac.green(), ac.blue(), 50))
        warm.setColorAt(0.7, QColor(ac.red(), ac.green(), ac.blue(), 0))
        p.fillPath(path, warm)

        if self._hover:
            p.fillPath(path, QColor(255, 255, 255, 14))
            p.setPen(QPen(ac, 1.6))
        else:
            p.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        p.drawPath(path)


# ─────────────────────────────────────────────
class PlayerDetailPage(BasePage):
    title = "球员详情"
    subtitle = "PLAYER PROFILE"

    match_clicked = pyqtSignal(Match)
    team_clicked = pyqtSignal(str)
    back_clicked = pyqtSignal()

    def __init__(self, service: DataService, favorites: Favorites) -> None:
        super().__init__()
        self._service = service
        self._favorites = favorites
        self._person_id: str | None = None
        self._person_name: str | None = None

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 8, 20, 0)
        top_bar.addStretch(1)
        self._fav_btn = FavoriteButton(favorites, "player", "")
        top_bar.addWidget(self._fav_btn)
        top_bar_w = QWidget(); top_bar_w.setLayout(top_bar)
        top_bar_w.setFixedHeight(40)
        outer.addWidget(top_bar_w)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(20, 10, 20, 20)
        self._body.setSpacing(16)

    # ── 数据 ──────────────────────────────
    def open_player(self, person_id: str, person_name: str = "") -> None:
        self._person_id = person_id
        self._person_name = person_name
        self._fav_btn.set_entity("player", person_id)
        self.refresh(force=False)

    def refresh(self, force: bool = False) -> None:
        if not self._person_id:
            return
        pid = self._person_id

        async def runner() -> None:
            import asyncio
            detail_t = self._service.fetch_player_detail(pid, force=force)
            ability_t = self._service.fetch_player_ability(pid, force=force)
            scorers_t = self._service.fetch_ranking(RankingType.GOALS, force=force)
            assists_t = self._service.fetch_ranking(RankingType.ASSISTS, force=force)
            sched_t = self._service.fetch_full_schedule(force=force)
            matches_t = self._service.fetch_person_matches(pid, force=force)
            detail, ability, scorers, assists, (_rounds, matches), person_matches = (
                await asyncio.gather(
                    detail_t, ability_t, scorers_t, assists_t, sched_t, matches_t,
                    return_exceptions=False,
                )
            )
            scorer = next((p for p in scorers if p.person_id == pid), None)
            assist = next((p for p in assists if p.person_id == pid), None)
            base = scorer or assist
            team_id = (detail.team_id if detail and detail.team_id
                       else (base.team_id if base else ""))
            team_matches = (
                [m for m in matches if team_id in (m.team_a_id, m.team_b_id)]
                if team_id else []
            )
            self._render(detail, ability, scorer, assist, team_id,
                         team_matches, person_matches)

        self.run_async(runner)

    # ── 渲染 ──────────────────────────────
    def _render(
        self,
        detail: PlayerDetail | None,
        ability: PlayerAbility | None,
        scorer: PlayerRanking | None,
        assist: PlayerRanking | None,
        team_id: str,
        team_matches: list[Match],
        person_matches: list[PersonMatch] | None = None,
    ) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        base = scorer or assist

        # 档案：优先真实 detail，其次排行榜，最后用 person_id 兜底
        if detail is not None:
            profile = profile_from_detail(detail)
        elif base is not None:
            profile = profile_for(base)
        else:
            stub = PlayerRanking(
                rank=0, person_id=self._person_id or "x",
                person_name=self._person_name or "未知球员",
                team_id=team_id, team_name="", count=0,
            )
            profile = profile_for(stub)

        # 能力值：优先真实 ability，否则哈希推导
        stats = stats_from_ability(ability, base)

        # 取图：本地高清 > Wikimedia > 懂球帝头像
        logo = (detail.person_logo if detail else None) or (
            base.person_logo if base else None)
        portrait = best_portrait(self._person_id, profile.name_zh, logo)

        # ── Hero ─────────────────────────────
        hero = _PlayerHero(profile, portrait, team_id,
                           on_team_click=self.team_clicked.emit,
                           on_back=self.back_clicked.emit)
        self._body.addWidget(hero)

        # ── 4 KPI 卡 ───────────────────────
        goals = scorer.count if scorer else 0
        assists_n = assist.count if assist else 0
        penalties = (scorer.penalty_goal
                     if (scorer and scorer.penalty_goal is not None) else 0)
        rank = base.rank if base else 0
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        kpi_widgets: list[QWidget] = []
        for label_zh, label_en, value, color, icon in (
            ("进球", "GOALS", goals, "#00BFFF", "⚽"),
            ("助攻", "ASSISTS", assists_n, "#FF9F43", "A"),
            ("点球", "PENALTIES", penalties, "#00D2FF", "P"),
            ("排名", "RANKING", rank, "#4FACFE", "#"),
        ):
            kpi = _KpiCard(label_zh, label_en, int(value), color, icon)
            stats_row.addWidget(kpi, 1)
            kpi_widgets.append(kpi)
        wrap = QWidget(); wrap.setLayout(stats_row)
        self._body.addWidget(wrap)

        # ── 三栏：雷达 · 综合能力 · 近期比赛 ─────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)
        bottom_row.addWidget(self._build_radar_card(stats), 3)
        bottom_row.addWidget(self._build_overall_card(stats, ability), 3)
        bottom_row.addWidget(
            self._build_recent_matches_card(person_matches or [], team_matches), 4)
        bottom_w = QWidget(); bottom_w.setLayout(bottom_row)
        self._body.addWidget(bottom_w)

        # ── 两栏：个人资料 · 荣誉奖杯 ───────────
        info_row = QHBoxLayout()
        info_row.setSpacing(14)
        info_row.addWidget(self._build_info_card(detail, profile, ability), 1)
        info_row.addWidget(self._build_trophies_card(detail), 1)
        info_w = QWidget(); info_w.setLayout(info_row)
        self._body.addWidget(info_w)

        self._body.addStretch(1)

        stagger_fade(kpi_widgets, step=70, dx=0, dy=14)

    # ── 雷达卡 ────────────────────────────
    def _build_radar_card(self, stats) -> Card:
        card = Card(padding=18, glow_color=RADAR_COLOR, shadow=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)
        title = QLabel("能力值总览")
        title.setStyleSheet(f"font-size:14px; font-weight:900; color:{RADAR_COLOR};")
        lay.addWidget(title)

        radar = RadarChart()
        radar.setMinimumSize(QSize(240, 240))
        radar.set_data(stats.as_pairs(), RADAR_COLOR)
        radar.set_breathing_glow(True, color=RADAR_GLOW)
        lay.addWidget(radar, 1)
        return card

    # ── 综合能力卡 ────────────────────────
    def _build_overall_card(self, stats, ability: PlayerAbility | None) -> Card:
        card = Card(padding=20, glow_color="#FFD700", shadow=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(10)
        t = QLabel("综合能力")
        t.setStyleSheet("font-size:14px; font-weight:900; color:#FFD700;")
        lay.addWidget(t)

        ovr_row = QHBoxLayout()
        ovr_row.setSpacing(12)
        ovr = QLabel(str(stats.ovr))
        ovr.setStyleSheet("color:#FFD700; font-size:80px; font-weight:900;")
        ovr_glow = QGraphicsDropShadowEffect(ovr)
        ovr_glow.setBlurRadius(20)
        ovr_glow.setOffset(0, 0)
        ovr_glow.setColor(QColor(255, 140, 0, 220))
        ovr.setGraphicsEffect(ovr_glow)
        ovr_row.addWidget(ovr)

        ob = QVBoxLayout(); ob.setSpacing(2)
        ob.addStretch(1)
        ver = (ability.version if ability and ability.version else "FC")
        rk = QLabel(f"{self._tier(stats.ovr)}  ·  {ver}")
        rk.setStyleSheet(
            "color:#1a1304; font-size:12px; font-weight:900;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #FFE680, stop:1 #FFD700); border-radius:11px; padding:4px 12px;"
        )
        rk.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ob.addWidget(rk)
        ob.addStretch(1)
        ovr_row.addLayout(ob)
        ovr_row.addStretch(1)
        lay.addLayout(ovr_row)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(6)
        for chip_text, chip_color in self._tier_chips(stats.ovr):
            chip = QLabel(chip_text)
            chip.setStyleSheet(
                f"color:#1a1304; font-weight:900; font-size:11px;"
                f"padding:4px 12px; border-radius:11px;"
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 #FFE680, stop:1 {chip_color});"
            )
            chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            chip_row.addWidget(chip)
        chip_row.addStretch(1)
        lay.addLayout(chip_row)

        for code, zh, val, color in stats.as_pairs():
            r = QHBoxLayout(); r.setSpacing(8)
            zh_l = QLabel(zh)
            zh_l.setStyleSheet("color:#B0BEC5; font-size:11.5px;")
            zh_l.setFixedWidth(38)
            r.addWidget(zh_l)
            code_l = QLabel(code)
            code_l.setStyleSheet("color:#FFFFFF; font-size:11.5px; font-weight:700;")
            code_l.setFixedWidth(36)
            r.addWidget(code_l)
            r.addStretch(1)
            v = QLabel(str(val))
            v.setStyleSheet(f"color:{color}; font-size:13.5px; font-weight:900;")
            r.addWidget(v)
            lay.addLayout(r)

        lay.addStretch(1)
        return card

    @staticmethod
    def _tier(ovr: int) -> str:
        if ovr >= 90:
            return "史诗"
        if ovr >= 85:
            return "传奇"
        if ovr >= 80:
            return "金卡"
        if ovr >= 75:
            return "稀有"
        return "普通"

    @staticmethod
    def _tier_chips(ovr: int) -> list[tuple[str, str]]:
        if ovr >= 90:
            return [("⭐  传奇", "#FFD700"), ("👑  核心", "#6A5ACD"), ("✨  超级球星", "#00BFFF")]
        if ovr >= 85:
            return [("👑  核心", "#6A5ACD"), ("✨  超级球星", "#00BFFF")]
        if ovr >= 80:
            return [("✨  超级球星", "#00BFFF")]
        if ovr >= 75:
            return [("🔥  核心球员", "#FF9F43")]
        return [("🌱  潜力新星", "#00D2FF")]

    # ── 个人资料卡（懂球帝风格） ──────────────
    def _build_info_card(
        self, detail: PlayerDetail | None, profile, ability: PlayerAbility | None
    ) -> Card:
        card = Card(padding=18, glow_color="#2ED877", shadow=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(10)
        head = QLabel("📋  个人资料")
        head.setStyleSheet("font-size:14px; font-weight:900; color:#2ED877;")
        lay.addWidget(head)

        rows: list[tuple[str, str]] = []
        if detail:
            if detail.date_of_birth:
                rows.append(("出生日期", detail.date_of_birth))
            hw = []
            if detail.height_cm:
                hw.append(f"{detail.height_cm}cm")
            if detail.weight_kg:
                hw.append(f"{detail.weight_kg}kg")
            if hw:
                rows.append(("身高 / 体重", "  /  ".join(hw)))
            if detail.foot:
                rows.append(("惯用脚", detail.foot))
            if detail.role or profile.position:
                rows.append(("场上位置", detail.role or profile.position))
            if ability and ability.position:
                rows.append(("注册位置", ability.position))
            if detail.team_name:
                rows.append(("所属俱乐部", detail.team_name))
            if detail.shirt_number:
                rows.append(("球衣号码", str(detail.shirt_number)))
            if detail.market_value:
                rows.append(("身价", f"{detail.market_value} 万欧"))
            if detail.weekly_salary:
                rows.append(("周薪", f"{detail.weekly_salary} 万欧"))
            if detail.contract:
                rows.append(("合同到期", detail.contract))
            if detail.nationality:
                rows.append(("国籍", detail.nationality))
        else:
            rows = [
                ("年龄", f"{profile.age} 岁"),
                ("身高", f"{profile.height_cm} cm"),
                ("惯用脚", profile.foot),
                ("场上位置", profile.position),
                ("所属俱乐部", profile.club),
                ("球衣号码", str(profile.jersey)),
                ("国籍", profile.nationality),
            ]

        for k, v in rows:
            r = QHBoxLayout(); r.setSpacing(8)
            kl = QLabel(k)
            kl.setStyleSheet("color:#B0BEC5; font-size:12px;")
            r.addWidget(kl)
            r.addStretch(1)
            vl = QLabel(v)
            vl.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:700;")
            vl.setAlignment(Qt.AlignmentFlag.AlignRight)
            r.addWidget(vl)
            lay.addLayout(r)

        # 星级（国际声望 / 逆足 / 花式）
        if ability and (ability.reputation or ability.weak_foot or ability.skill_moves):
            lay.addSpacing(4)
            for name, val in (
                ("国际声望", ability.reputation),
                ("逆足能力", ability.weak_foot),
                ("花式技巧", ability.skill_moves),
            ):
                if not val:
                    continue
                r = QHBoxLayout(); r.setSpacing(8)
                kl = QLabel(name)
                kl.setStyleSheet("color:#B0BEC5; font-size:12px;")
                r.addWidget(kl)
                r.addStretch(1)
                stars = QLabel("★" * int(val) + "☆" * max(0, 5 - int(val)))
                stars.setStyleSheet("color:#FFD700; font-size:13px; font-weight:900;")
                r.addWidget(stars)
                lay.addLayout(r)

        lay.addStretch(1)
        return card

    # ── 荣誉奖杯卡 ────────────────────────
    def _build_trophies_card(self, detail: PlayerDetail | None) -> Card:
        card = Card(padding=18, glow_color="#FFD700", shadow=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(10)
        head = QLabel("🏆  荣誉殿堂")
        head.setStyleSheet("font-size:14px; font-weight:900; color:#FFD700;")
        lay.addWidget(head)

        trophies = detail.trophies if detail else []
        if not trophies:
            empty = QLabel("暂无荣誉数据")
            empty.setStyleSheet("color:#56607D; font-size:12px; padding: 24px 0;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(empty)
            lay.addStretch(1)
            return card

        for tr in trophies[:12]:
            r = QHBoxLayout(); r.setSpacing(10)
            if tr.trophy_img:
                img = RemoteImage(size=28, shape="rect", radius=4)
                img.set_url(tr.trophy_img)
                r.addWidget(img)
            name = QLabel(tr.competition_name or "—")
            name.setStyleSheet("color:#FFFFFF; font-size:12.5px; font-weight:700;")
            r.addWidget(name, 1)
            times = QLabel(f"× {tr.times}")
            times.setStyleSheet("color:#FFD700; font-size:13px; font-weight:900;")
            r.addWidget(times)
            lay.addLayout(r)

        lay.addStretch(1)
        return card

    # ── 近期比赛 ──────────────────────────
    def _build_recent_matches_card(
        self,
        person_matches: list[PersonMatch],
        team_matches: list[Match] | None = None,
    ) -> Card:
        """渲染球员真实近期比赛（含每场进球/助攻/评分）。

        数据优先用 ``person/matches`` 接口（对任意球员有效）；若该接口为空，
        再退回到「所属国家队的本届世界杯赛程」作为兜底。
        """
        card = Card(padding=18, glow_color="#4FACFE", shadow=False)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 14, 20, 12)
        lay.setSpacing(8)
        head = QHBoxLayout()
        head.setSpacing(8)
        ic = QLabel("📅")
        ic.setStyleSheet("font-size:14px;")
        head.addWidget(ic)
        t = QLabel("近期比赛")
        t.setStyleSheet("font-size:14px; font-weight:900;")
        head.addWidget(t)
        en = QLabel("RECENT MATCHES")
        en.setStyleSheet(
            "color:#B0BEC5; font-size:9.5px; font-weight:800; letter-spacing:1.6px;"
        )
        head.addWidget(en)
        head.addStretch(1)
        lay.addLayout(head)

        # 列头：进球 / 助攻 / 评分（与每行右侧三栏对齐）
        legend = QHBoxLayout()
        legend.setContentsMargins(0, 0, 6, 0)
        legend.addStretch(1)
        for txt in ("进球", "助攻", "评分"):
            lab = QLabel(txt)
            lab.setStyleSheet("color:#56607D; font-size:9.5px; font-weight:800;")
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lab.setFixedWidth(40)
            legend.addWidget(lab)
        legend_w = QWidget(); legend_w.setLayout(legend)

        # 已踢的优先、按时间倒序
        sorted_pm = sorted(
            person_matches,
            key=lambda m: (not m.played,
                           -(m.start_play.timestamp() if m.start_play else 0)),
        )

        if sorted_pm:
            lay.addWidget(legend_w)
            for pm in sorted_pm[:6]:
                lay.addWidget(_PersonMatchRow(pm))
            lay.addStretch(1)
            return card

        # ── 兜底：用国家队赛程 ────────────────
        sorted_m = sorted(
            team_matches or [],
            key=lambda m: (m.status != MatchStatus.PLAYED,
                           -(m.start_play.timestamp() if m.start_play else 0)),
        )
        for m in sorted_m[:5]:
            row = _SmallMatchRow(m, "")
            row.clicked.connect(self.match_clicked.emit)
            lay.addWidget(row)

        if not sorted_m:
            empty = QLabel("暂无比赛数据")
            empty.setStyleSheet("color:#B0BEC5; padding: 40px 0;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(empty)

        lay.addStretch(1)
        return card
