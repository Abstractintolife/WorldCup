"""Performance & off-thread data audit (Task 16).

Covers:
* Property 13 (Req 26.1) — No main-thread network: a structural assertion that
  every DataService fetch (and the underlying ApiClient HTTP entry points) is an
  ``async`` coroutine backed by ``httpx.AsyncClient`` (non-blocking, driven by
  the qasync event loop), and that the services issue no synchronous/blocking
  ``requests`` calls.
* Req 25.4 — Timer audit: the only live per-widget timers are the single Frame
  Clock heartbeat and the single Hero Match Card 1s countdown. The animated
  widgets (compositor, fx, charts, panels, glass card) own zero ``QTimer``s.
* Req 20.3 / 25.4 — Hover/elevation never animates ``blurRadius`` (a source scan
  asserts no QPropertyAnimation targets the ``blurRadius`` property).

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import inspect

import pytest

from tests.conftest import QT_AVAILABLE

pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


# ════════════════════════════════════════════════════════════════════
#  Property 13 — No main-thread (synchronous) network
#  Feature: worldcup-ultimate-redesign, Property 13: No main-thread network —
#  network requests never originate synchronously on the GUI thread.
#  Validates: Requirements 26.1
# ════════════════════════════════════════════════════════════════════
def test_property13_data_service_fetches_are_async():
    """Every DataService.fetch_* is a coroutine (awaited off the GUI thread)."""
    from app.services.data_service import DataService

    fetchers = [
        name for name in dir(DataService)
        if name.startswith("fetch_") and callable(getattr(DataService, name))
    ]
    assert fetchers, "expected DataService.fetch_* methods"
    for name in fetchers:
        assert inspect.iscoroutinefunction(getattr(DataService, name)), (
            f"DataService.{name} must be async (non-blocking network)"
        )


def test_property13_api_client_entrypoints_are_async():
    """ApiClient HTTP entry points are async and use httpx.AsyncClient."""
    from app.api.client import ApiClient

    assert inspect.iscoroutinefunction(ApiClient.get_json)
    assert inspect.iscoroutinefunction(ApiClient.get_bytes)
    assert inspect.iscoroutinefunction(ApiClient.close)

    src = inspect.getsource(ApiClient)
    assert "httpx.AsyncClient" in src      # 非阻塞异步客户端
    # 不得使用同步阻塞的 requests 库（那会卡住 GUI 线程）。
    assert "import requests" not in src
    assert "requests.get(" not in src


def test_property13_image_service_downloads_off_thread():
    """ImageService downloads via the async client (no blocking GUI-thread I/O)."""
    from app.services.image_service import ImageService

    assert inspect.iscoroutinefunction(ImageService._download)
    src = inspect.getsource(ImageService)
    assert "await" in src and "get_bytes" in src


def test_overview_page_routes_data_through_data_service():
    """Req 26.2: the Overview Page requests data only via the DataService."""
    from app.ui.pages import home_page

    src = inspect.getsource(home_page.HomePage)
    # 全部经注入的 self._service（DataService），无直接 httpx / requests 调用。
    assert "self._service.fetch" in src
    assert "httpx" not in src
    assert "requests.get" not in src


# ════════════════════════════════════════════════════════════════════
#  Req 25.4 — Single FrameClock + single hero countdown; no stray timers
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_frame_clock_owns_single_timer(qapp):
    """The global Frame Clock heartbeat is exactly one QTimer."""
    from PyQt6.QtCore import QTimer

    from app.ui.design.frame_clock import FrameClock

    fc = FrameClock.instance()
    timers = fc.findChildren(QTimer)
    assert len(timers) == 1


@pytestmark_qt
def test_hero_card_owns_single_countdown_timer(qapp):
    """The Hero Match Card owns exactly one 1s countdown QTimer (Req 6.4)."""
    from PyQt6.QtCore import QTimer

    from app.ui.widgets.hero_match_card import HeroMatchCard

    hero = HeroMatchCard()
    timers = hero.findChildren(QTimer)
    assert len(timers) == 1
    assert timers[0].interval() == 1000


@pytestmark_qt
def test_animated_widgets_own_no_private_timers(qapp):
    """Animated widgets drive motion via FrameClock / property animations,

    never a private per-widget QTimer (Req 25.4).
    """
    from PyQt6.QtCore import QTimer

    from app.ui.widgets import stage_compositor as sc
    from app.ui.widgets.charts import BarChart, LineChart, RadarChart
    from app.ui.widgets.fx.count_up import CountUpNumber
    from app.ui.widgets.fx.mouse_trail import MouseTrailOverlay
    from app.ui.widgets.glass_card import GlassCard
    from app.ui.widgets.live_match_center import LiveMatchCenter
    from app.ui.widgets.standings_table import StandingsTable
    from app.ui.widgets.stat_strip import StatStrip
    from app.ui.widgets.today_matches_panel import TodayMatchesPanel

    widgets = {
        "cpu_backdrop": sc._construct_cpu(sc.NIGHT_STADIUM, None),
        "mouse_trail": MouseTrailOverlay(),
        "count_up": CountUpNumber(),
        "radar": RadarChart(),
        "line": LineChart(),
        "bar": BarChart(),
        "standings": StandingsTable(),
        "stat_strip": StatStrip(),
        "live_center": LiveMatchCenter(),
        "today": TodayMatchesPanel(),
        "glass_card": GlassCard(),
    }
    for name, w in widgets.items():
        assert w.findChildren(QTimer) == [], f"{name} must own no private QTimer"


# ════════════════════════════════════════════════════════════════════
#  Req 20.3 / 25.4 — Hover/elevation never animates blurRadius
# ════════════════════════════════════════════════════════════════════
def test_no_animation_targets_blur_radius():
    """No QPropertyAnimation drives the expensive ``blurRadius`` property.

    Hover elevation animates the cheap ``pos`` property; ``blurRadius`` is only
    ever set discretely (never per-frame), per the performance lesson.
    """
    import pathlib

    import app.ui as _ui

    ui_dir = pathlib.Path(_ui.__file__).parent
    offenders: list[str] = []
    for path in ui_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if 'b"blurRadius"' in text or "b'blurRadius'" in text:
            offenders.append(str(path))
    assert offenders == [], f"blurRadius must never be animated: {offenders}"


def test_glass_card_hover_uses_motion_system_pos():
    """GlassCard hover lift is routed through motion_system (animates `pos`)."""
    from app.ui.widgets import glass_card

    src = inspect.getsource(glass_card.GlassCard)
    assert "motion_system.hover_lift" in src
    # hover_lift 动画 pos（见 motion_system），绝不触碰 blurRadius。
    hover_src = inspect.getsource(
        __import__("app.ui.design.motion_system", fromlist=["hover_lift"]).hover_lift
    )
    assert 'b"pos"' in hover_src
    # hover_lift 仅创建 b"pos" 动画；不存在 b"blurRadius" 动画目标。
    assert 'b"blurRadius"' not in hover_src

