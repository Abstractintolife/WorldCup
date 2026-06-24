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
import pathlib
import re

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




# ════════════════════════════════════════════════════════════════════
#  Property 13 — No main-thread network (static data-layer scan)
#  Feature: worldcup-ultimate-redesign, Property 13: No main-thread network
#  Validates: Requirements 26.1
#
#  Strengthened structural guarantee: the ENTIRE data layer (app/api +
#  app/services) must never reach for a synchronous/blocking network primitive
#  that would run on (and freeze) the GUI thread. All network I/O flows through
#  httpx.AsyncClient awaited off-thread via BasePage.run_async (qasync/asyncio).
# ════════════════════════════════════════════════════════════════════

# Blocking primitives that would issue a network request synchronously on the
# caller's (GUI) thread. httpx.AsyncClient is the ONLY sanctioned client.
_SYNC_NETWORK_PATTERNS = (
    re.compile(r"^\s*import\s+requests\b", re.MULTILINE),       # sync `requests`
    re.compile(r"^\s*from\s+requests\b", re.MULTILINE),
    re.compile(r"\brequests\.(get|post|put|delete|head|patch|request|Session)\b"),
    re.compile(r"\bhttpx\.Client\b"),                           # blocking httpx client
    re.compile(r"^\s*import\s+urllib\b", re.MULTILINE),         # urllib(.request) blocks
    re.compile(r"^\s*from\s+urllib\b", re.MULTILINE),
    re.compile(r"\burllib\.request\b"),
    re.compile(r"^\s*import\s+socket\b", re.MULTILINE),         # raw blocking socket
    re.compile(r"\bsocket\.socket\b"),
)


def _data_layer_files() -> list[pathlib.Path]:
    """All Python source files in the preserved data layer (api + services)."""
    import app.api as _api
    import app.services as _services

    files: list[pathlib.Path] = []
    for pkg in (_api, _services):
        pkg_dir = pathlib.Path(pkg.__file__).parent
        files.extend(sorted(pkg_dir.rglob("*.py")))
    assert files, "expected data-layer source files under app/api and app/services"
    return files


def test_property13_data_layer_has_no_synchronous_network():
    """Req 26.1 / Property 13: no blocking network primitive anywhere in the

    data layer — only httpx.AsyncClient (awaited off the GUI thread) is allowed.

    Feature: worldcup-ultimate-redesign, Property 13: No main-thread network.
    """
    offenders: list[str] = []
    for path in _data_layer_files():
        text = path.read_text(encoding="utf-8")
        for pat in _SYNC_NETWORK_PATTERNS:
            if pat.search(text):
                offenders.append(f"{path.name}: matched /{pat.pattern}/")
    assert offenders == [], (
        "synchronous/blocking network usage found in the data layer "
        f"(must use httpx.AsyncClient off-thread): {offenders}"
    )


def test_property13_data_layer_uses_async_httpx_client():
    """The sole HTTP client in the data layer is httpx.AsyncClient (non-blocking)."""
    from app.api.client import ApiClient

    src = inspect.getsource(ApiClient)
    assert "httpx.AsyncClient" in src, "ApiClient must use httpx.AsyncClient"


# ════════════════════════════════════════════════════════════════════
#  Req 25.4 — Timer audit (static allow-list scan)
#  Feature: worldcup-ultimate-redesign (Requirement 25.4)
#
#  Statically scan every app/ui/**/*.py source for *repeating* QTimer
#  instantiations (`QTimer(...)`). `QTimer.singleShot(...)` is a one-shot,
#  fire-and-forget deferral (no heartbeat) and is excluded as benign.
#
#  The ONLY modules permitted to instantiate a repeating QTimer are:
#    * frame_clock.py    — the single global Frame Clock animation heartbeat.
#    * hero_match_card.py— the single 1s Hero Match Card countdown (Req 6.4).
#    * main_window.py    — the app-level `_auto_timer` data-refresh scheduler.
#                          This is a data-refresh scheduler, NOT an animation /
#                          per-widget timer, and is therefore allowed (Req 28.2).
#  No OTHER module may own a repeating per-widget / heartbeat QTimer (Req 25.4).
# ════════════════════════════════════════════════════════════════════

# Allow-list of module basenames permitted to instantiate a repeating QTimer.
_TIMER_ALLOWLIST = {
    "frame_clock.py",      # FrameClock heartbeat
    "hero_match_card.py",  # Hero countdown (the single allowed per-widget timer)
    "main_window.py",      # _auto_timer data-refresh scheduler (not an animation timer)
}

# `QTimer(` = a constructed (repeating-capable) timer instance. We must NOT match
# `QTimer.singleShot(` (one-shot deferral) — note the `.` after QTimer there.
_QTIMER_CTOR = re.compile(r"\bQTimer\s*\(")


def _ui_source_files() -> list[pathlib.Path]:
    """Every Python source file under app/ui (recursively)."""
    import app.ui as _ui

    ui_dir = pathlib.Path(_ui.__file__).parent
    files = sorted(ui_dir.rglob("*.py"))
    assert files, "expected source files under app/ui"
    return files


def test_timer_audit_only_allowlisted_modules_create_repeating_timers():
    """Req 25.4: no live per-widget timers other than the Frame Clock and the

    single Hero Match Card countdown (plus the allowed data-refresh scheduler).

    Feature: worldcup-ultimate-redesign (Requirement 25.4).
    """
    offenders: list[str] = []
    saw_allowed: set[str] = set()
    for path in _ui_source_files():
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if not _QTIMER_CTOR.search(line):
                continue
            # `QTimer.singleShot(...)` is benign (one-shot) — exclude it.
            if "QTimer.singleShot" in line or "QTimer .singleShot" in line:
                continue
            if path.name in _TIMER_ALLOWLIST:
                saw_allowed.add(path.name)
            else:
                offenders.append(f"{path.name}: {line.strip()}")

    assert offenders == [], (
        "repeating QTimer instantiated outside the allow-list "
        f"{sorted(_TIMER_ALLOWLIST)}: {offenders}"
    )
    # Sanity: the two animation/countdown timers genuinely exist where expected.
    assert "frame_clock.py" in saw_allowed, "FrameClock heartbeat QTimer missing"
    assert "hero_match_card.py" in saw_allowed, "Hero countdown QTimer missing"


def test_timer_audit_singleshot_is_treated_as_benign():
    """Sanity check on the scanner: `QTimer.singleShot` must NOT be flagged.

    main_window.py uses `QTimer.singleShot(0, ...)` for a deferred backend swap;
    that one-shot deferral is not a live/heartbeat timer and must be excluded.
    """
    singleshot = "        QTimer.singleShot(0, self._swap_to_cpu_backdrop)"
    ctor = "        self._timer = QTimer(self)"
    # `QTimer.singleShot(` has a `.` after QTimer, so the constructor regex (which
    # requires `QTimer` immediately followed by `(`) does NOT match it...
    assert _QTIMER_CTOR.search(singleshot) is None
    # ...and the explicit guard would exclude it even if it did.
    assert "QTimer.singleShot" in singleshot
    # A genuine constructor call IS matched.
    assert _QTIMER_CTOR.search(ctor) is not None
