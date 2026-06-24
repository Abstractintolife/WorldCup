"""Integration tests for LOW_PERF degradation & fetch-failure recovery (Task 15.2).

Feature: worldcup-ultimate-redesign
Validates: Requirements 28.1, 28.2, 28.3

This is an *integration* test that exercises the real widgets / page wiring
(not just the pure helper math), complementing the focused checks in
``test_error_degradation.py``.

It covers two graceful-degradation guarantees:

* **Req 28.3 — LOW_PERF static backdrop + instant transitions.** Under
  ``WC_LITE=1`` / ``LOW_PERF`` the Stage Compositor must still paint a *static*
  gradient (the UI stays visually intact, just animation-free), the Motion
  System must make page transitions instant, and the count-up / floating-flag /
  chart-reveal effects must settle to their final state immediately.
* **Req 28.1 / 28.2 — last-good-data retention + retry on next tick.** A
  simulated ``DataService`` fetch failure must keep the previously-rendered
  ("last good") data and flip the connection badge to the error state, while the
  refresh path keeps re-issuing the (force) fetches so a later tick can recover.

LOW_PERF design note
--------------------
``LOW_PERF`` is parsed from the ``WC_LITE`` env var **once at import time** and
bound as a module-level constant inside every consumer module (``app.config``
plus each module that did ``from app.config import LOW_PERF`` — the compositor,
motion system, count-up, floating-flag, chart base). Re-reading ``os.environ``
at runtime would therefore *not* change behaviour. So these tests
``monkeypatch.setattr`` the module-local ``LOW_PERF`` name in *each* relevant
module. Using the ``monkeypatch`` fixture guarantees the flags are restored on
teardown, so neighbouring tests are never polluted.

retry-on-next-tick design note
-------------------------------
``HomePage.refresh`` hands an async coroutine to ``BasePage.run_async``, which
schedules it on the event loop (Qt + asyncio integration). Driving that full
loop in a unit test is brittle, so for the most robust assertion we intercept
``run_async`` to capture the coroutine factory, then run that coroutine directly
with ``asyncio`` and assert the injected service's fetch methods were invoked
with ``force=True``. This proves a refresh tick re-issues all three fetches
(i.e. a failed source is retried on the next scheduled tick — Req 28.2). A
structural check on ``MainWindow._auto_refresh`` confirms the timer is wired to
force-refresh the dashboard pages.
"""
from __future__ import annotations

import asyncio
import inspect

import pytest

from tests.conftest import QT_AVAILABLE

pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


# ════════════════════════════════════════════════════════════════════
#  Req 28.3 — LOW_PERF: Stage Compositor paints a *static* gradient
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_low_perf_backdrop_paints_static_gradient(qapp, monkeypatch):
    """Under LOW_PERF the compositor never animates, yet still paints a
    (static) night-stadium gradient — top vs bottom pixels must differ."""
    from app.ui.widgets import stage_compositor as sc

    monkeypatch.setattr(sc, "LOW_PERF", True)

    bd = sc.create_backdrop(sc.NIGHT_STADIUM, parent=None, prefer_gpu=False)
    bd.setFixedSize(240, 320)
    bd.set_enabled(True)
    bd.set_paused(False)
    bd.show()
    qapp.processEvents()

    # Static: the frame-clock subscription is never taken under LOW_PERF.
    assert bd._should_run() is False
    assert bd.is_animating() is False

    # ...but a backdrop is still painted (not blank): grab the widget and
    # confirm the vertical gradient produced visibly different top/bottom pixels.
    pm = bd.grab()
    assert not pm.isNull()
    img = pm.toImage()
    top = img.pixelColor(img.width() // 2, 2)
    bottom = img.pixelColor(img.width() // 2, img.height() - 3)
    # The night-stadium ramp goes #06111A (top) → #0F2A1F (bottom); the painted
    # pixels must differ, proving a static gradient (not an empty/blank fill).
    assert (top.red(), top.green(), top.blue()) != (
        bottom.red(), bottom.green(), bottom.blue()
    )

    bd.set_enabled(False)
    bd.deleteLater()
    qapp.processEvents()


# ════════════════════════════════════════════════════════════════════
#  Req 28.3 — LOW_PERF: Motion System page transition is instant
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_low_perf_page_transition_instant(qapp, monkeypatch):
    """``page_transition`` returns None (instant, no animation) under LOW_PERF."""
    from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

    from app.ui.design import motion_system as ms

    monkeypatch.setattr(ms, "LOW_PERF", True)

    w = QWidget()
    w.resize(200, 120)
    w.show()
    qapp.processEvents()

    anim = ms.page_transition(w, dy=22)
    assert anim is None
    # No leftover opacity effect → widget is immediately fully visible.
    assert not isinstance(w.graphicsEffect(), QGraphicsOpacityEffect)

    w.deleteLater()
    qapp.processEvents()


# ════════════════════════════════════════════════════════════════════
#  Req 28.3 — LOW_PERF: count-up / floating flag / chart settle instantly
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_low_perf_count_up_settles_immediately(qapp, monkeypatch):
    """``CountUpNumber.set_target`` displays the exact final value at once."""
    from app.ui.widgets.fx import count_up as cu

    monkeypatch.setattr(cu, "LOW_PERF", True)

    num = cu.CountUpNumber(decimals=0)
    num.set_target(141)
    # Instant settle: exact final text, no running animation.
    assert num.text() == "141"
    assert num._anim.state().name != "Running"

    num.deleteLater()
    qapp.processEvents()


@pytestmark_qt
def test_low_perf_floating_flag_stays_static(qapp, monkeypatch):
    """``FloatingFlag.start_float`` keeps the flag static under LOW_PERF."""
    from PyQt6.QtCore import QAbstractAnimation

    from app.ui.widgets.fx import floating_flag as ff

    monkeypatch.setattr(ff, "LOW_PERF", True)

    flag = ff.FloatingFlag("巴西")
    flag.start_float()
    # No oscillation: vertical offset pinned at 0, loop animation not running.
    assert flag.float_y == 0.0
    assert flag._anim.state() != QAbstractAnimation.State.Running

    flag.deleteLater()
    qapp.processEvents()


@pytestmark_qt
def test_low_perf_chart_reveal_settles_immediately(qapp, monkeypatch):
    """``BaseChart._start_reveal`` jumps the reveal to 1.0 under LOW_PERF."""
    from app.ui.widgets.charts import base as chart_base

    monkeypatch.setattr(chart_base, "LOW_PERF", True)

    chart = chart_base.BaseChart()
    chart._start_reveal()
    # Geometry fully revealed instantly (reveal == 1.0), animation not running.
    assert chart.get_reveal() == 1.0
    assert chart._anim.state().name != "Running"

    chart.deleteLater()
    qapp.processEvents()


# ════════════════════════════════════════════════════════════════════
#  Req 28.1 / 28.2 — fetch-failure recovery on the real HomePage
# ════════════════════════════════════════════════════════════════════
def _match():
    from app.models.match import Match

    return Match(
        match_id="42",
        team_a_id="a", team_a_name="阿根廷",
        team_b_id="b", team_b_name="法国",
    )


def _group():
    from app.models.standing import GroupStanding, TeamStanding

    team = TeamStanding(
        rank=1, team_id="a", team_name="阿根廷", points=9, matches_total=3,
        matches_won=3, matches_draw=0, matches_lost=0,
        goals_pro=7, goals_against=2,
    )
    return GroupStanding(name="A组", teams=[team])


def _scorer():
    from app.models.player import PlayerRanking

    return PlayerRanking(
        rank=1, person_id="p1", person_name="姆巴佩",
        team_id="fra", team_name="法国", count=8,
    )


@pytestmark_qt
def test_homepage_retains_last_good_data_and_flags_error(qapp):
    """Req 28.1: feed one good tick, then an all-failure tick → caches retained,
    badge flips to the error state."""
    from app.services.data_service import DataService
    from app.ui.pages.home_page import HomePage

    home = HomePage(DataService())

    # 连接态现经 connection_changed 信号广播（正文连接徽标已移除）。
    conn_states: list[bool] = []
    home.connection_changed.connect(conn_states.append)

    good_rounds: list = []
    good_matches = [_match()]
    good_groups = [_group()]
    good_scorers = [_scorer()]

    # Successful tick — lightweight stub results matching _apply's contract:
    #   sched = (rounds, matches), standings = (groups, ...), scorers = list.
    home._apply(((good_rounds, good_matches), (good_groups, {}), good_scorers))

    assert home._last_matches == good_matches
    assert home._last_groups == good_groups
    assert home._last_scorers == good_scorers
    assert home._had_good_data is True
    assert conn_states[-1] is True

    # All-failure tick — every source raises (asyncio.gather returns Exceptions).
    home._apply((RuntimeError("net"), TimeoutError("t/o"), RuntimeError("net")))

    # Last-good data is RETAINED (identical objects), not cleared (Req 28.1).
    assert home._last_matches == good_matches
    assert home._last_groups == good_groups
    assert home._last_scorers == good_scorers
    # Connection state reflects the failure (Req 28.1).
    assert conn_states[-1] is False


@pytestmark_qt
def test_homepage_refresh_reissues_all_fetches_with_force(qapp, monkeypatch):
    """Req 28.2: a refresh(force=True) tick re-issues *all three* fetches with
    ``force=True`` — so a previously-failed source is retried on the next tick.

    Robust unit-level approach (documented in the module docstring): intercept
    ``run_async`` to capture the coroutine factory, then run it directly under
    asyncio and assert the injected fake service recorded all three forced calls.
    """
    from app.models.player import RankingType
    from app.ui.pages.home_page import HomePage

    class FakeService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, bool]] = []

        async def fetch_full_schedule(self, force: bool = False):
            self.calls.append(("schedule", force))
            return ([], [_match()])

        async def fetch_standings(self, force: bool = False):
            self.calls.append(("standings", force))
            return ([_group()], [], [])

        async def fetch_ranking(self, rtype, force: bool = False):
            assert rtype == RankingType.GOALS
            self.calls.append(("ranking", force))
            return [_scorer()]

    fake = FakeService()
    home = HomePage(fake)  # type: ignore[arg-type]

    captured: dict = {}
    monkeypatch.setattr(
        home, "run_async", lambda factory, **kw: captured.__setitem__("f", factory)
    )

    home.refresh(force=True)
    assert "f" in captured, "refresh() should hand a coroutine to run_async"

    # Drive the captured coroutine directly (no Qt/asyncio loop integration).
    asyncio.run(captured["f"]())

    names = {name for name, _ in fake.calls}
    assert names == {"schedule", "standings", "ranking"}
    # Every fetch was forced (Req 28.2: bypass cache to recover on next tick).
    assert all(force is True for _, force in fake.calls)

    home.deleteLater()
    qapp.processEvents()


def test_mainwindow_auto_refresh_retries_dashboard_on_tick():
    """Req 28.2: the auto-refresh timer force-refreshes the active dashboard
    page, so a failed load is retried on the next scheduled tick.

    Structural assertion (no network / no Qt): inspect the handler source.
    """
    from app.ui import main_window as mw

    src = inspect.getsource(mw.MainWindow._auto_refresh)
    assert "refresh(force=True)" in src
    assert "_home" in src
