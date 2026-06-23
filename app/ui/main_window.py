"""主窗口：把侧边栏 / 顶部栏 / 各页面装进 QStackedWidget。"""
from __future__ import annotations

import logging

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QGuiApplication, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    ANIM_FPS,
    APP_TITLE_ZH,
    LIVE_REFRESH_INTERVAL_MS,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from app.models.match import Match
from app.models.player import RankingType
from app.services.data_service import DataService
from app.services.favorites import Favorites, Settings
from app.ui.pages.favorites_page import FavoritesPage
from app.ui.pages.globe_page import GlobePage
from app.ui.pages.home_page import HomePage
from app.ui.pages.match_detail_page import MatchDetailPage
from app.ui.pages.player_detail_page import PlayerDetailPage
from app.ui.pages.prediction_page import PredictionPage
from app.ui.pages.schedule_page import SchedulePage
from app.ui.pages.scorers_page import RankingPage
from app.ui.pages.search_page import SearchPage
from app.ui.pages.stadiums_page import StadiumsPage
from app.ui.pages.standings_page import StandingsPage
from app.ui.pages.team_detail_page import TeamDetailPage
from app.ui.pages.teams_page import TeamsPage
from app.ui.theme import THEMES, ThemePalette, build_qss
from app.ui.design.frame_clock import FrameClock
from app.ui.widgets.effects import fade_slide_in
from app.ui.widgets.fps_monitor import FpsMonitor
from app.ui.widgets.nav_sidebar import NavSidebar
from app.ui.widgets.skin_backdrop import SkinBackdrop
from app.ui.widgets.top_bar import TopBar

log = logging.getLogger(__name__)


# 主导航定义 —— 对照「想象中的样子」设计稿的菜单（含 LIVE 徽章）。
# 每项 = (key, emoji, 中文标签[, 徽章])；key 映射到 _key_to_page 的页面。
_PRIMARY_NAV: list[tuple] = [
    ("home", "📊", "概览"),
    ("live", "🔴", "实时比赛", "LIVE"),
    ("schedule", "📅", "赛程中心"),
    ("globe", "🗓", "赛事日历"),
    ("teams", "🛡", "球队"),
    ("scorers", "⚽", "球员"),
    ("standings", "📈", "数据分析"),
    ("prediction", "🔮", "预测中心"),
    ("stadiums", "📰", "新闻资讯"),
    ("favorites", "⭐", "收藏夹"),
    ("settings", "⚙️", "设置"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE_ZH)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._service = DataService()
        self._favorites = Favorites()
        self._settings = Settings()
        self._theme_name: str = str(self._settings.get("theme", "dark"))
        if self._theme_name not in THEMES:
            self._theme_name = "dark"

        # 动画帧率（240FPS 动效内核）—— 从设置载入并即时应用到全局帧时钟
        try:
            self._fps = int(self._settings.get("fps", ANIM_FPS) or ANIM_FPS)
        except (TypeError, ValueError):
            self._fps = ANIM_FPS
        FrameClock.instance().set_fps(self._fps)
        self._fps = FrameClock.instance().fps()

        # 动态背景动画开关（默认开；卡顿时可在设置中关闭以提升流畅度）
        self._bg_anim = bool(self._settings.get("bg_anim", True))

        # 窗口图标（大力神杯徽章）
        from app.ui.design.app_icon import build_app_icon
        self.setWindowIcon(build_app_icon())

        # ── 控件 ──
        self._sidebar = NavSidebar(_PRIMARY_NAV)
        self._topbar = TopBar()
        self._stack = QStackedWidget()

        # 主页面
        self._home = HomePage(self._service)
        self._globe = GlobePage(self._service)
        self._schedule = SchedulePage(self._service)
        self._prediction = PredictionPage(self._service)
        self._standings = StandingsPage(self._service)
        self._scorers = RankingPage(self._service, RankingType.GOALS)
        self._assists = RankingPage(self._service, RankingType.ASSISTS)
        self._yellows = RankingPage(self._service, RankingType.YELLOW_CARDS)
        self._teams = TeamsPage(self._service)
        self._stadiums = StadiumsPage()
        self._favorites_page = FavoritesPage(self._service, self._favorites)
        # 详情页
        self._match_detail = MatchDetailPage(self._service, self._favorites)
        self._player_detail = PlayerDetailPage(self._service, self._favorites)
        self._team_detail = TeamDetailPage(self._service, self._favorites)
        # 搜索页
        self._search = SearchPage(self._service)

        # ── 索引映射 ──
        self._key_to_page: dict[str, QWidget] = {
            "home": self._home,
            "live": self._schedule,
            "globe": self._globe,
            "schedule": self._schedule,
            "prediction": self._prediction,
            "standings": self._standings,
            "scorers": self._scorers,
            "assists": self._assists,
            "yellows": self._yellows,
            "teams": self._teams,
            "stadiums": self._stadiums,
            "favorites": self._favorites_page,
            "match_detail": self._match_detail,
            "player_detail": self._player_detail,
            "team_detail": self._team_detail,
            "search": self._search,
        }
        for w in self._key_to_page.values():
            self._stack.addWidget(w)

        # ── 布局 ──
        central = QWidget()
        self.setCentralWidget(central)
        self._central = central

        # 全局动态背景层（皮肤引擎核心）—— 铺满整窗、位于最底层
        self._backdrop = SkinBackdrop(central, palette=THEMES.get(self._theme_name))
        self._backdrop.setGeometry(central.rect())
        self._backdrop.set_enabled(self._bg_anim)
        self._backdrop.lower()

        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        right.addWidget(self._topbar)
        right.addWidget(self._stack, 1)
        right_w = QWidget()
        right_w.setLayout(right)
        outer.addWidget(right_w, 1)

        # 让动态背景透出来：内容区容器全部透明（侧栏/顶栏走 chrome_glass 半透明）
        central.setStyleSheet("background: transparent;")
        right_w.setStyleSheet("background: transparent;")
        self._stack.setStyleSheet("background: transparent;")

        # 状态栏
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("已就绪 · 数据来源：懂球帝公开接口")

        # ── 信号 ──
        self._sidebar.selected.connect(self._on_nav_selected)
        self._topbar.search_submitted.connect(self._on_search)
        self._topbar.refresh_clicked.connect(self._refresh_current)
        self._topbar.skin_selected.connect(self._set_skin)
        self._topbar.settings_clicked.connect(self._open_settings)

        self._home.match_clicked.connect(self._open_match)
        self._home.team_clicked.connect(self._open_team)
        self._home.player_clicked.connect(self._open_player)
        self._home.prediction_clicked.connect(self._open_prediction)
        self._home.navigate.connect(self._on_home_navigate)

        self._globe.team_clicked.connect(self._open_team)

        self._schedule.match_clicked.connect(self._open_match)

        self._prediction.team_clicked.connect(self._open_team)
        self._prediction.match_clicked.connect(self._open_match)

        self._standings.team_clicked.connect(self._open_team)

        self._scorers.player_clicked.connect(
            lambda p: self._open_player(p.person_id, p.person_name)
        )
        self._scorers.team_clicked.connect(self._open_team)
        self._assists.player_clicked.connect(
            lambda p: self._open_player(p.person_id, p.person_name)
        )
        self._assists.team_clicked.connect(self._open_team)
        self._yellows.player_clicked.connect(
            lambda p: self._open_player(p.person_id, p.person_name)
        )
        self._yellows.team_clicked.connect(self._open_team)

        self._teams.team_clicked.connect(self._open_team)

        self._match_detail.team_clicked.connect(self._open_team)
        self._match_detail.player_clicked.connect(self._open_player)
        self._match_detail.back_clicked.connect(self._go_back)
        self._match_detail.prediction_clicked.connect(self._open_prediction)
        self._player_detail.team_clicked.connect(self._open_team)
        self._player_detail.match_clicked.connect(self._open_match)
        self._player_detail.back_clicked.connect(self._go_back)
        self._team_detail.match_clicked.connect(self._open_match)
        self._team_detail.player_clicked.connect(self._open_player)
        self._team_detail.back_clicked.connect(self._go_back)

        self._favorites_page.match_clicked.connect(self._open_match)
        self._favorites_page.team_clicked.connect(self._open_team)
        self._favorites_page.player_clicked.connect(self._open_player)

        self._search.match_clicked.connect(self._open_match)
        self._search.team_clicked.connect(self._open_team)
        self._search.player_clicked.connect(self._open_player)

        # 历史栈（用于「← 返回」）
        self._history: list[str] = []

        # 初始主题 + 初始页
        self._apply_theme()
        self._sidebar.set_active("home")
        self._navigate("home")

        # 自动刷新（仅当当前页是仪表盘 / 赛程 / 直播页时才会真正请求）
        self._auto_timer = QTimer(self)
        self._auto_timer.timeout.connect(self._auto_refresh)
        self._auto_timer.start(LIVE_REFRESH_INTERVAL_MS)

        # ── 性能 HUD（FPS / 帧耗时 / CPU）──
        # 右上角浮层；默认隐藏，Ctrl+Shift+F 切换，或 WC_FPS_OVERLAY=1 启动即显示。
        import os
        self._fps_monitor = FpsMonitor(central)
        self._fps_monitor.hide()
        self._fps_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        self._fps_shortcut.activated.connect(self._toggle_fps_monitor)
        if os.environ.get("WC_FPS_OVERLAY", "0").strip().lower() in ("1", "true", "yes"):
            self._fps_monitor.show()
            self._fps_monitor.raise_()
            self._position_fps_monitor()

        # 居中窗口
        screen = QGuiApplication.primaryScreen().availableGeometry()
        w = min(int(screen.width() * 0.92), 1600)
        h = min(int(screen.height() * 0.92), 1000)
        self.resize(w, h)
        self.move(
            screen.left() + (screen.width() - w) // 2,
            screen.top() + (screen.height() - h) // 2,
        )

    # ─── 主题 / 皮肤 ──────────────────────────
    def _apply_theme(self) -> None:
        palette: ThemePalette = THEMES.get(self._theme_name, THEMES["dark"])
        # 切主题前清空阴影 / 渐变 / 球场场景缓存，避免旧皮肤的预渲染贴图残留
        from app.ui.design.resource_cache import clear_caches
        from app.ui.design.stadium_engine import clear_cache as clear_stadium
        clear_caches()
        clear_stadium()
        QApplication.instance().setStyleSheet(build_qss(palette))
        # 动态背景场景 + 侧栏强调色 + 积分榜配色 随皮肤联动
        self._backdrop.set_palette(palette)
        self._sidebar.apply_palette(palette)
        self._standings.set_theme(palette)
        self._home.apply_palette(palette)
        self._topbar.set_current_skin(self._theme_name)
        self._settings.set("theme", self._theme_name)

    def _set_skin(self, name: str) -> None:
        if name not in THEMES or name == self._theme_name:
            # 仍同步勾选态
            self._topbar.set_current_skin(self._theme_name)
            return
        self._theme_name = name
        self._apply_theme()
        # 触发当前页重新绘制（部分自定义控件颜色和主题色相关）
        cur = self._stack.currentWidget()
        if hasattr(cur, "refresh"):
            cur.refresh(force=False)
        else:
            cur.update()

    def _toggle_theme(self) -> None:
        # 兼容旧入口：在「深蓝世界杯」与「黑金冠军」之间切换
        self._set_skin("gold" if self._theme_name != "gold" else "dark")

    def _open_settings(self) -> None:
        """打开设置对话框（主题 / 帧率 / 缓存 / 关于）。"""
        from app.ui.widgets.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._theme_name, self._fps, self,
                             current_bg_anim=self._bg_anim)
        dlg.theme_selected.connect(self._set_skin)
        dlg.fps_selected.connect(self._set_fps)
        dlg.bg_anim_toggled.connect(self._set_bg_anim)
        dlg.cache_cleared.connect(self._on_cache_cleared)
        dlg.exec()

    def _set_bg_anim(self, on: bool) -> None:
        """实时开关动态背景动画并持久化。"""
        self._bg_anim = bool(on)
        self._backdrop.set_enabled(self._bg_anim)
        self._settings.set("bg_anim", self._bg_anim)
        msg = "动态背景已开启 ✨" if self._bg_anim else "动态背景已关闭 · 性能优先 ⚡"
        self.statusBar().showMessage(msg, 3000)

    def _set_fps(self, fps: int) -> None:
        """实时切换全局动画帧率并持久化。"""
        FrameClock.instance().set_fps(int(fps))
        self._fps = FrameClock.instance().fps()
        self._settings.set("fps", self._fps)
        self.statusBar().showMessage(f"动画帧率已设为 {self._fps} FPS ⚡", 3000)

    def _on_cache_cleared(self) -> None:
        """清空接口缓存并强制刷新当前页。"""
        try:
            self._service._client.clear_cache()
        except Exception:  # pragma: no cover
            pass
        self._refresh_current()
        self.statusBar().showMessage("已清空缓存并刷新 ✅", 3000)

    # ─── 导航 ──────────────────────────────
    def _on_home_navigate(self, key: str) -> None:
        """概览页「快速操作」跳转到对应主页面，并同步侧栏高亮。"""
        if key not in self._key_to_page:
            return
        if key in {item[0] for item in _PRIMARY_NAV}:
            self._sidebar.set_active(key)
        self._navigate(key, push_history=True)

    def _on_nav_selected(self, key: str) -> None:
        # 「设置」是动作型条目：打开设置对话框，不切换页面。
        if key == "settings":
            self._open_settings()
            # 高亮回退到当前页对应的导航项
            cur = self._current_key()
            if cur:
                self._sidebar.set_active(cur)
            return
        self._navigate(key, push_history=False)

    def _navigate(self, key: str, *, push_history: bool = True) -> None:
        page = self._key_to_page.get(key)
        if page is None:
            return
        if push_history:
            cur_key = self._current_key()
            if cur_key and cur_key != key:
                self._history.append(cur_key)
        self._stack.setCurrentWidget(page)
        # 全局动态背景：地球仪页持续自绘较重，切到该页时暂停背景动画省 CPU
        self._backdrop.set_paused(page is self._globe)
        # 页面切入：淡入 + 自下而上轻微滑入（地球仪页持续自绘，跳过以免离屏重渲染冲突）
        if page is not self._globe:
            fade_slide_in(page, duration=360, dx=0, dy=22)
        title, subtitle = self._title_for(key, page)
        self._topbar.set_title(title, subtitle)
        # 触发数据刷新
        if hasattr(page, "refresh"):
            page.refresh(force=False)

    def _current_key(self) -> str | None:
        cur = self._stack.currentWidget()
        for k, w in self._key_to_page.items():
            if w is cur:
                return k
        return None

    def _title_for(self, key: str, page) -> tuple[str, str]:
        title = getattr(page, "title", APP_TITLE_ZH)
        subtitle = getattr(page, "subtitle", "")
        # 强制使用导航条目里的中文标题（详情页 / 搜索页保持页面自带 title）
        nav_titles = {item[0]: item[2] for item in _PRIMARY_NAV}
        if key in nav_titles:
            title = nav_titles[key]
        return title, subtitle

    def _go_back(self) -> None:
        if self._history:
            key = self._history.pop()
            self._sidebar.set_active(key) if key in {item[0] for item in _PRIMARY_NAV} else None
            self._stack.setCurrentWidget(self._key_to_page[key])
            page = self._key_to_page[key]
            self._topbar.set_title(*self._title_for(key, page))
            if hasattr(page, "refresh"):
                page.refresh(force=False)
        else:
            self._sidebar.set_active("home")
            self._navigate("home", push_history=False)

    # ─── 跳转 ──────────────────────────────
    def _open_match(self, match: Match) -> None:
        self._match_detail.open_match(match)
        self._navigate("match_detail")

    def _open_prediction(self, match: Match) -> None:
        """从比赛详情跳转到该场的完整 AI 预测页。"""
        self._prediction.open_match(match)
        self._sidebar.set_active("prediction")
        self._navigate("prediction")

    def _open_team(self, team_id: str) -> None:
        self._team_detail.open_team(team_id)
        self._navigate("team_detail")

    def _open_player(self, person_id: str, person_name: str = "") -> None:
        self._player_detail.open_player(person_id, person_name)
        self._navigate("player_detail")

    def _on_search(self, text: str) -> None:
        if not text:
            return
        self._search.search(text)
        self._navigate("search")

    # ─── 自动刷新 ───────────────────────────
    def _auto_refresh(self) -> None:
        cur = self._stack.currentWidget()
        if cur in (self._home, self._schedule, self._match_detail):
            if hasattr(cur, "refresh"):
                cur.refresh(force=True)

    def _refresh_current(self) -> None:
        cur = self._stack.currentWidget()
        if hasattr(cur, "refresh"):
            cur.refresh(force=True)
            self.statusBar().showMessage("已强制刷新当前页面 ✅", 3000)

    # ─── 性能 HUD ───────────────────────────
    def _toggle_fps_monitor(self) -> None:
        if self._fps_monitor.isVisible():
            self._fps_monitor.hide()
            self.statusBar().showMessage("性能 HUD 已关闭", 2000)
        else:
            self._fps_monitor.show()
            self._fps_monitor.raise_()
            self._position_fps_monitor()
            self.statusBar().showMessage("性能 HUD 已开启 · FPS / 帧耗时 / CPU", 2000)

    def _position_fps_monitor(self) -> None:
        if not hasattr(self, "_fps_monitor") or not hasattr(self, "_central"):
            return
        m = 16
        x = self._central.width() - self._fps_monitor.width() - m
        self._fps_monitor.move(max(0, x), m)

    # ─── 几何 ──────────────────────────────
    def resizeEvent(self, ev) -> None:  # noqa: D401
        super().resizeEvent(ev)
        if hasattr(self, "_backdrop") and hasattr(self, "_central"):
            self._backdrop.setGeometry(self._central.rect())
            self._backdrop.lower()
        if hasattr(self, "_fps_monitor") and self._fps_monitor.isVisible():
            self._position_fps_monitor()
            self._fps_monitor.raise_()
