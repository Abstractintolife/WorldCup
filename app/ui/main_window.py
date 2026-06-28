"""主窗口：把侧边栏 / 顶部栏 / 各页面装进 QStackedWidget。"""
from __future__ import annotations

import logging

from PyQt6.QtCore import QRectF, QTimer, Qt
from PyQt6.QtGui import (
    QGuiApplication,
    QIcon,
    QKeySequence,
    QPainterPath,
    QRegion,
    QShortcut,
)
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
    GPU_BACKDROP,
    LIVE_REFRESH_INTERVAL_MS,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from app.models.match import Match
from app.services.data_service import DataService
from app.services.favorites import Favorites, Settings
from app.ui.pages.favorites_page import FavoritesPage
from app.ui.pages.globe_page import GlobePage
from app.ui.pages.home_page import HomePage
from app.ui.pages.match_detail_page import MatchDetailPage
from app.ui.pages.news_page import NewsPage
from app.ui.pages.player_detail_page import PlayerDetailPage
from app.ui.pages.player_rankings_page import PlayerRankingsPage
from app.ui.pages.prediction_page import PredictionPage
from app.ui.pages.probability_page import ProbabilityPage
from app.ui.pages.bracket_page import BracketPage
from app.ui.pages.schedule_page import SchedulePage
from app.ui.pages.search_page import SearchPage
from app.ui.pages.stadiums_page import StadiumsPage
from app.ui.pages.standings_page import StandingsPage
from app.ui.pages.team_detail_page import TeamDetailPage
from app.ui.pages.team_rankings_page import TeamRankingsPage
from app.ui.theme import THEMES, ThemePalette, build_qss
from app.ui.design.frame_clock import FrameClock
from app.ui.design.hud_theme import NIGHT_STADIUM
from app.ui.design import motion_system
from app.ui.widgets.fps_monitor import FpsMonitor
from app.ui.widgets.fx.mouse_trail import MouseTrailOverlay
from app.ui.widgets.nav_rail import NAV_ITEMS, NavRail
from app.ui.widgets.stage_compositor import create_backdrop
from app.ui.widgets.sub_header import SubHeader
from app.ui.widgets.top_hud_bar import TopHudBar
from app.ui.widgets.window_chrome import ResizeGripManager, TitleBar

log = logging.getLogger(__name__)


# 主导航定义 —— 对照「想象中的样子」设计稿的菜单（12 项，严格顺序）。
# 复用 NavRail 的 NAV_ITEMS（key, 中文, 英文, 图标）；这里转成壳层既有
# 辅助函数期望的 (key, emoji, 中文标签) 形态。key 映射到 _key_to_page。
_PRIMARY_NAV: list[tuple] = [(key, icon, zh) for key, zh, _en, icon in NAV_ITEMS]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE_ZH)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        # 无边框：去掉操作系统原生「黑框」标题栏，改用与主体融合的自绘标题栏
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self._service = DataService()
        self._favorites = Favorites()
        self._settings = Settings()
        self._theme_name: str = str(self._settings.get("theme", "dark"))
        if self._theme_name not in THEMES:
            self._theme_name = "dark"

        # 界面语言（中文 / 英文）—— 从设置载入并应用到全局 i18n 单例。
        from app.i18n import set_language as _set_language
        self._language: str = str(self._settings.get("language", "zh"))
        if self._language not in ("zh", "en"):
            self._language = "zh"
        _set_language(self._language)

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

        # 项目自定义鼠标光标（assets/cursor.png）。设在窗口根上，所有未单独
        # 指定光标的子控件会自动继承；而按钮 / 可点卡片等显式 setCursor 的
        # 元件仍保留各自的「小手」等 hover 光标。缺图时静默回退系统箭头。
        from app.ui.design.app_cursor import apply_app_cursor
        apply_app_cursor(self)

        # ── 控件 ──
        self._sidebar = NavRail(NAV_ITEMS)
        self._topbar = TopHudBar()
        self._subheader = SubHeader()
        self._stack = QStackedWidget()

        # 主页面
        self._home = HomePage(self._service)
        self._globe = GlobePage(self._service)
        self._schedule = SchedulePage(self._service)
        self._prediction = PredictionPage(self._service)
        self._probability = ProbabilityPage(self._service)
        self._bracket = BracketPage(self._service)
        self._standings = StandingsPage(self._service)
        self._rankings = PlayerRankingsPage(self._service)
        self._teams = TeamRankingsPage(self._service)
        self._stadiums = StadiumsPage()
        self._news = NewsPage(self._service)
        self._favorites_page = FavoritesPage(self._service, self._favorites)
        # 详情页
        self._match_detail = MatchDetailPage(self._service, self._favorites)
        self._player_detail = PlayerDetailPage(self._service, self._favorites)
        self._team_detail = TeamDetailPage(self._service, self._favorites)
        # 搜索页
        self._search = SearchPage(self._service)

        # ── 索引映射 ──
        # 设计稿 12 项导航 → 实际页面。部分概念无独立页面，映射到最贴近的现有页：
        #   live(实时比赛)→赛程中心  players(球员)/scorers(射手榜)→球员榜
        #   analysis(数据分析)→预测中心  venue(场馆地图)→球场
        self._key_to_page: dict[str, QWidget] = {
            "home": self._home,
            "globe": self._globe,
            "schedule": self._schedule,
            "live": self._schedule,
            "prediction": self._prediction,
            "analysis": self._prediction,
            "probability": self._probability,
            "bracket": self._bracket,
            "standings": self._standings,
            "scorers": self._rankings,
            "players": self._rankings,
            "teams": self._teams,
            "stadiums": self._stadiums,
            "venue": self._stadiums,
            "news": self._news,
            "favorites": self._favorites_page,
            "match_detail": self._match_detail,
            "player_detail": self._player_detail,
            "team_detail": self._team_detail,
            "search": self._search,
        }
        # 仅把「真实页面」对象加进 stack（去重，避免同一页面被多 key 重复 add）。
        for w in dict.fromkeys(self._key_to_page.values()):
            self._stack.addWidget(w)

        # ── 布局 ──
        central = QWidget()
        self.setCentralWidget(central)
        self._central = central

        # 全局动态背景层（皮肤引擎核心）—— 铺满整窗、位于最底层
        # 渲染后端可选 CPU(QPainter) / GPU(GLSL)，见 _make_backdrop。
        self._gpu_bg = bool(self._settings.get("gpu_bg", GPU_BACKDROP))
        self._backdrop = self._make_backdrop(central)
        self._backdrop.setGeometry(central.rect())
        self._backdrop.set_enabled(self._bg_anim)
        self._backdrop.lower()

        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        right.addWidget(self._topbar)
        right.addWidget(self._subheader)
        right.addWidget(self._stack, 1)
        right_w = QWidget()
        right_w.setLayout(right)
        outer.addWidget(right_w, 1)

        # 自绘标题栏（窗口控制 + 拖动）置于最顶部，整窗一栏横贯
        self._titlebar = TitleBar(APP_TITLE_ZH)
        body_w = QWidget()
        body_w.setLayout(outer)
        shell = QVBoxLayout()
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        shell.addWidget(self._titlebar)
        shell.addWidget(body_w, 1)
        central.setLayout(shell)
        self._titlebar.setStyleSheet(self._titlebar.styleSheet())  # noqa: ensure styled

        # 无边框窗口的边缘缩放手柄（铺在四边/四角，置于最上层）
        self._grips = ResizeGripManager(central)
        self._grips.reposition()

        # 让 z0 舞台合成器透出：按设计 Z 序把内容宿主 + chrome 设为半透明。
        # central（RootSurface）持有铺满整窗的背景子控件，自身保持透明即可。
        central.setStyleSheet("background: transparent;")
        self._setup_compositing_layers(
            content_hosts=(body_w, right_w, self._stack),
            chrome=(self._sidebar, self._topbar, self._subheader),
        )

        # 状态栏
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("已就绪 · 数据来源：懂球帝公开接口")

        # ── 信号 ──
        self._sidebar.selected.connect(self._on_nav_selected)
        self._topbar.search_submitted.connect(self._on_search)
        self._topbar.profile_clicked.connect(self._open_settings)
        # 通知铃 → 跳转最新资讯；区域球 → 在中文 / 英文界面之间切换。
        self._topbar.notifications_clicked.connect(lambda: self._on_home_navigate("news"))
        self._topbar.region_clicked.connect(self._toggle_language)

        self._home.match_clicked.connect(self._open_match)
        self._home.team_clicked.connect(self._open_team)
        self._home.player_clicked.connect(self._open_player)
        self._home.prediction_clicked.connect(self._open_prediction)
        self._home.navigate.connect(self._on_home_navigate)
        # LIVE 徽章仅在有比赛进行中时点亮
        self._home.live_state_changed.connect(self._sidebar.set_live)
        # 侧栏页脚实时数据状态随连接态联动（绿色已连接 / 红色中断）
        self._home.connection_changed.connect(self._sidebar.set_realtime)
        # 子标题栏右侧实时连接胶囊也随连接态联动（取代已移除的正文连接徽标）
        self._home.connection_changed.connect(self._subheader.set_connected)

        self._globe.team_clicked.connect(self._open_team)

        self._schedule.match_clicked.connect(self._open_match)

        self._prediction.team_clicked.connect(self._open_team)
        self._prediction.match_clicked.connect(self._open_match)

        self._probability.team_clicked.connect(self._open_team)

        self._bracket.match_clicked.connect(self._open_match)
        self._bracket.team_clicked.connect(self._open_team)

        self._standings.team_clicked.connect(self._open_team)

        self._rankings.player_clicked.connect(
            lambda p: self._open_player(p.person_id, p.person_name)
        )
        self._rankings.team_clicked.connect(self._open_team)

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

        # ── 鼠标拖尾叠层（任务 5）──
        # 顶层、对鼠标事件透明的克制拖尾，铺满整个中央区域；由唯一 FrameClock
        # 驱动（不新增定时器）。置于最上层，但 WA_TransparentForMouseEvents 保证
        # 不拦截任何点击 / 拖拽（含无边框缩放手柄）。需求 23.x / 首开广播场景 29.1。
        self._mouse_trail = MouseTrailOverlay(central, palette=NIGHT_STADIUM)
        self._mouse_trail.setGeometry(central.rect())
        self._mouse_trail.raise_()
        self._mouse_trail.show()

        # 应用已保存的界面语言（默认中文；英文则即时重译所有 chrome）。
        self._apply_language(self._language)

        # 居中窗口
        screen = QGuiApplication.primaryScreen().availableGeometry()
        w = min(int(screen.width() * 0.92), 1600)
        h = min(int(screen.height() * 0.92), 1000)
        self.resize(w, h)
        self.move(
            screen.left() + (screen.width() - w) // 2,
            screen.top() + (screen.height() - h) // 2,
        )

    # ─── 语言（中文 / 英文界面切换）──────────────
    def _toggle_language(self) -> None:
        from app.i18n import current_language, set_language, tr
        new = "en" if current_language() == "zh" else "zh"
        set_language(new)
        self._language = new
        self._settings.set("language", new)
        self._apply_language(new)
        msg = (tr("已切换为英文界面（赛事数据仍为中文数据源）") if new == "en"
               else "已切换为中文界面")
        self.statusBar().showMessage(msg, 4000)

    def _apply_language(self, lang: str) -> None:
        """把界面语言应用到所有持久化 chrome（标题栏 / 顶栏 / 侧栏 / 子标题）。"""
        from app.i18n import tr
        from app.config import APP_TITLE_ZH
        self.setWindowTitle(tr(APP_TITLE_ZH))
        if hasattr(self, "_titlebar"):
            self._titlebar.set_language(lang)
        if hasattr(self, "_topbar"):
            self._topbar.set_language(lang)
        if hasattr(self, "_sidebar"):
            self._sidebar.set_language(lang)
        if hasattr(self, "_subheader"):
            self._subheader.set_language(lang)
        # 以当前页标题按新语言重译。
        cur = self._current_key()
        if cur:
            page = self._key_to_page.get(cur)
            if page is not None:
                self._topbar.set_title(*self._title_for(cur, page))

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
                             current_bg_anim=self._bg_anim,
                             current_gpu_bg=self._gpu_bg)
        dlg.theme_selected.connect(self._set_skin)
        dlg.fps_selected.connect(self._set_fps)
        dlg.bg_anim_toggled.connect(self._set_bg_anim)
        dlg.backend_selected.connect(self._set_gpu_bg)
        dlg.cache_cleared.connect(self._on_cache_cleared)
        dlg.exec()

    def _set_bg_anim(self, on: bool) -> None:
        """实时开关动态背景动画并持久化。"""
        self._bg_anim = bool(on)
        self._backdrop.set_enabled(self._bg_anim)
        self._settings.set("bg_anim", self._bg_anim)
        msg = "动态背景已开启 ✨" if self._bg_anim else "动态背景已关闭 · 性能优先 ⚡"
        self.statusBar().showMessage(msg, 3000)

    # ─── 合成层 / Z 序（让 z0 舞台合成器透出 chrome + 内容宿主）───────────
    def _setup_compositing_layers(self, *, content_hosts, chrome) -> None:
        """按设计 Z 序把内容宿主与 chrome 设为半透明，露出 z0「夜间球场」合成器。

        对应需求 16.5（概览页用半透明 chrome/hero + 不透明滚动正文渲染于背景之上）
        与设计「Compositing / Z-order」：

        * **内容宿主**（包裹容器 / ``QStackedWidget``，设计 Z1）开启
          ``WA_TranslucentBackground`` 并清空基底；各页面只让「滚动正文」走不透明底
          （``#OpaqueBody`` / ``#PageContent`` QSS，见 ``hud_theme`` / ``theme``），
          使长列表滚动时 GPU 合成器无需每帧重合成整棵控件树（性能权衡，沿用旧
          ``theme.py`` 的「动态背景透出层」教训）。
        * **chrome**（导航栏 / 顶栏 / 子标题，设计 Z2「半透明玻璃」）同样开启
          ``WA_TranslucentBackground``，根框基底透明以透出背景；其内部玻璃元件
          （nav 行高亮、搜索胶囊等）各自的样式不受影响。
        """
        for host in content_hosts:
            host.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            host.setStyleSheet("background: transparent;")
        for w in chrome:
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            # 仅把 chrome 根框基底设为透明（按 objectName 精确匹配），不波及子级。
            name = w.objectName() or type(w).__name__
            w.setStyleSheet(f"QFrame#{name} {{ background: transparent; }}")

    # ─── 动态背景渲染后端（CPU / GPU 可热切换）───────────
    def _make_backdrop(self, parent: QWidget):
        """创建「夜间球场」舞台合成器背景；GPU 不可用时工厂自动降级回 CPU 版。

        统一由 :func:`create_backdrop` 工厂选择后端（取代旧的
        ``SkinBackdrop`` / ``GLBackdrop``），并连接 GPU 运行期失败信号以便
        热切换到 CPU 后端（需求 27.1–27.4）。
        """
        from app.ui.widgets.stage_compositor import has_background_image
        # 存在自定义背景图时强制用 CPU 后端渲染（GPU 着色器路径不绘制该照片）。
        prefer_gpu = self._gpu_bg and not has_background_image()
        bd = create_backdrop(NIGHT_STADIUM, parent=parent, prefer_gpu=prefer_gpu)
        # 反映工厂实际选定的后端（GPU 构造失败时会回退为 CPU）。
        self._gpu_bg = type(bd).__name__ == "StageCompositor"
        if hasattr(bd, "gpu_failed"):
            bd.gpu_failed.connect(self._on_gpu_backdrop_failed)
        backend = "GPU (GLSL)" if self._gpu_bg else "CPU (QPainter)"
        log.info("舞台合成器后端：%s", backend)
        return bd

    def _on_gpu_backdrop_failed(self) -> None:
        """GPU 后端在 initializeGL 期检测到着色器编译/链接失败 → 热切到 CPU。"""
        if not self._gpu_bg:
            return
        self._gpu_bg = False
        log.warning("检测到 GPU 舞台合成器运行期失败，准备热切换到 CPU 后端")
        # 延后到事件循环空闲时重建，避免在 paint/initializeGL 内销毁自身。
        QTimer.singleShot(0, self._swap_to_cpu_backdrop)

    def _swap_to_cpu_backdrop(self) -> None:
        old = self._backdrop
        if old is not None:
            old.set_enabled(False)  # 取消帧时钟订阅
            old.setParent(None)
            old.deleteLater()
        self._gpu_bg = False
        self._backdrop = create_backdrop(NIGHT_STADIUM, parent=self._central, prefer_gpu=False)
        self._backdrop.setGeometry(self._central.rect())
        self._backdrop.set_enabled(self._bg_anim)
        self._backdrop.set_paused(self._stack.currentWidget() is self._globe)
        self._backdrop.lower()
        self._backdrop.show()
        self._settings.set("gpu_bg", False)
        self.statusBar().showMessage("GPU 后端异常，已热切换到 CPU 渲染 ⚙️", 3500)

    def _set_gpu_bg(self, on: bool) -> None:
        """运行时切换 CPU/GPU 背景后端（销毁旧实例、重建新实例）并持久化。"""
        on = bool(on)
        if on == self._gpu_bg and self._backdrop is not None:
            return
        self._gpu_bg = on
        # 销毁旧背景
        old = self._backdrop
        if old is not None:
            old.set_enabled(False)  # 取消帧时钟订阅
            old.setParent(None)
            old.deleteLater()
        # 重建（_make_backdrop 可能因 GPU 不可用把 _gpu_bg 复位为 False）
        self._backdrop = self._make_backdrop(self._central)
        self._backdrop.setGeometry(self._central.rect())
        self._backdrop.set_enabled(self._bg_anim)
        self._backdrop.set_paused(self._stack.currentWidget() is self._globe)
        self._backdrop.lower()
        self._backdrop.show()
        self._settings.set("gpu_bg", self._gpu_bg)
        if self._gpu_bg:
            msg = "渲染后端：GPU (GLSL) · 主线程已解放 🚀"
        elif on:
            msg = "GPU 后端不可用，已回退到 CPU 渲染"
        else:
            msg = "渲染后端：CPU (QPainter)"
        self.statusBar().showMessage(msg, 3500)

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
        # 兼容中文标签 → 页面 key（部分面板历史上发出中文名）。
        _ZH_ALIAS = {
            "概览": "home", "赛程中心": "schedule", "实时比赛": "live",
            "球队": "teams", "球员": "players", "数据分析": "analysis",
            "积分榜": "standings", "射手榜": "scorers", "场馆地图": "venue",
            "新闻资讯": "news", "收藏夹": "favorites",
        }
        key = _ZH_ALIAS.get(key, key)
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
        # 子标题栏双行文案已按需求移除（信息与顶栏标题重复）；连接状态改由侧栏
        # 页脚的实时状态指示承担，故概览页不再展示子标题栏，正文整体上移。
        self._subheader.setVisible(False)
        # 全局动态背景：地球仪页持续自绘较重，切到该页时暂停背景动画省 CPU
        self._backdrop.set_paused(page is self._globe)
        # 页面切入：180ms 淡入 + 自下而上轻微滑入（经统一动效系统 motion_system，
        # 缓动恒 OutCubic、时长 ≤ 500ms；LOW_PERF 下瞬时完成 —— 需求 29.2 / 28.3）。
        # 地球仪页持续自绘，跳过以免离屏重渲染冲突。
        if page is not self._globe:
            motion_system.page_transition(page, dy=22)
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
        self._sidebar.set_active("analysis")
        self._navigate("analysis")

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
    def _apply_round_mask(self) -> None:
        """给无边框窗口加圆角遮罩，让边框 / 标题栏 / 内容浑然一体。

        最大化 / 全屏时清除遮罩（铺满屏幕、直角）。
        """
        if self.isMaximized() or self.isFullScreen():
            self.clearMask()
            return
        radius = 14.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), radius, radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def showEvent(self, ev) -> None:  # noqa: D401
        super().showEvent(ev)
        self._apply_round_mask()

    def resizeEvent(self, ev) -> None:  # noqa: D401
        super().resizeEvent(ev)
        self._apply_round_mask()
        if hasattr(self, "_backdrop") and hasattr(self, "_central"):
            self._backdrop.setGeometry(self._central.rect())
            self._backdrop.lower()
        if hasattr(self, "_grips"):
            self._grips.reposition()
        if hasattr(self, "_mouse_trail") and hasattr(self, "_central"):
            self._mouse_trail.setGeometry(self._central.rect())
            self._mouse_trail.raise_()
        if hasattr(self, "_titlebar"):
            self._titlebar.sync_max_glyph()
        if hasattr(self, "_fps_monitor") and self._fps_monitor.isVisible():
            self._position_fps_monitor()
            self._fps_monitor.raise_()
