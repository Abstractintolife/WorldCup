"""Tests for error handling & graceful degradation (Task 15).

Covers:
* Task 15.1 / Req 28.3 — under WC_LITE=1 / LOW_PERF the Stage Compositor renders
  a static backdrop (never subscribes to the Frame Clock) and the Motion System
  makes page transitions instant, while the UI stays fully functional.
* Task 15.1 / Req 28.1, 28.2 — on a simulated DataService fetch failure the
  Overview Page retains the last-good data (does not clear populated widgets)
  and the MainWindow auto-refresh timer retries on the next scheduled tick.

LOW_PERF is read into module namespaces at import time, so these tests
monkeypatch the module-level flag rather than the process environment. Qt-backed
checks are skipped automatically when Qt cannot initialise offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest

from app.ui.widgets import stage_compositor as sc
from tests.conftest import QT_AVAILABLE

pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


# ════════════════════════════════════════════════════════════════════
#  Req 28.3 — LOW_PERF: static backdrop (no Frame Clock subscription)
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_low_perf_backdrop_is_static(qapp, monkeypatch):
    """Under LOW_PERF the compositor never subscribes to the Frame Clock."""
    monkeypatch.setattr(sc, "LOW_PERF", True)
    bd = sc._construct_cpu(sc.NIGHT_STADIUM, None)
    bd.set_enabled(True)
    bd.set_paused(False)
    bd.show()
    qapp.processEvents()
    # 静态渐变：未订阅帧时钟 → 不推进动画（需求 28.3）。
    assert bd.is_animating() is False
    # 但 UI 仍可用：公共 API 正常、可观察状态如实反映。
    assert bd.is_enabled() is True
    assert bd.is_paused() is False
    bd.deleteLater()


@pytestmark_qt
def test_normal_perf_backdrop_animates(qapp, monkeypatch):
    """Sanity counterpart: with LOW_PERF off the visible backdrop animates."""
    monkeypatch.setattr(sc, "LOW_PERF", False)
    bd = sc._construct_cpu(sc.NIGHT_STADIUM, None)
    bd.set_enabled(True)
    bd.show()
    qapp.processEvents()
    assert bd.is_animating() is True
    bd.set_enabled(False)
    bd.deleteLater()


# ════════════════════════════════════════════════════════════════════
#  Req 28.3 — LOW_PERF: Motion System makes transitions instant
# ════════════════════════════════════════════════════════════════════
@pytestmark_qt
def test_low_perf_page_transition_is_instant(qapp, monkeypatch):
    """page_transition is a no-op (instant) under LOW_PERF."""
    from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

    from app.ui.design import motion_system as ms

    monkeypatch.setattr(ms, "LOW_PERF", True)
    w = QWidget()
    w.resize(200, 120)
    w.show()
    anim = ms.page_transition(w, dy=22)
    # 瞬时：不创建动画，且不残留不透明度 effect（控件立即完全可见）。
    assert anim is None
    assert not isinstance(w.graphicsEffect(), QGraphicsOpacityEffect)
    w.deleteLater()


@pytestmark_qt
def test_normal_page_transition_is_180ms_outcubic(qapp, monkeypatch):
    """Counterpart: normal mode produces a 180ms OutCubic fade (Req 29.2)."""
    from PyQt6.QtCore import QEasingCurve
    from PyQt6.QtWidgets import QWidget

    from app.ui.design import motion_system as ms

    monkeypatch.setattr(ms, "LOW_PERF", False)
    w = QWidget()
    w.resize(200, 120)
    w.show()
    anim = ms.page_transition(w, dy=22)
    assert anim is not None
    assert anim.duration() == 180
    assert anim.duration() <= ms.DUR_MAX
    assert anim.easingCurve().type() == QEasingCurve.Type.OutCubic
    w.deleteLater()


# ════════════════════════════════════════════════════════════════════
#  Req 28.1 / 28.2 — last-good-data retention + retry on next tick
# ════════════════════════════════════════════════════════════════════
def _match():
    from app.models.match import Match

    return Match(
        match_id="1",
        team_a_id="a", team_a_name="瑞士",
        team_b_id="b", team_b_name="加拿大",
    )


def _group():
    from app.models.standing import GroupStanding, TeamStanding

    team = TeamStanding(
        rank=1, team_id="a", team_name="瑞士", points=9, matches_total=3,
        matches_won=3, matches_draw=0, matches_lost=0,
        goals_pro=6, goals_against=1,
    )
    return GroupStanding(name="A组", teams=[team])


def _scorer():
    from app.models.player import PlayerRanking

    return PlayerRanking(
        rank=1, person_id="p1", person_name="梅西",
        team_id="arg", team_name="阿根廷", count=5,
    )


@pytestmark_qt
def test_homepage_retains_last_good_data_on_fetch_failure(qapp):
    """Req 28.1: a fetch failure keeps the last-good data instead of clearing."""
    from app.services.data_service import DataService
    from app.ui.pages.home_page import HomePage

    home = HomePage(DataService())

    # 连接态现经 connection_changed 信号广播（正文连接徽标已移除）。
    conn_states: list[bool] = []
    home.connection_changed.connect(conn_states.append)

    good_matches = [_match()]
    good_groups = [_group()]
    good_scorers = [_scorer()]
    # 成功一拍：sched=(rounds, matches), standings=(groups, ...), scorers=list。
    home._apply((([], good_matches), (good_groups, {}), good_scorers))

    assert home._last_matches == good_matches
    assert home._last_groups == good_groups
    assert home._last_scorers == good_scorers
    assert home._had_good_data is True

    # 下一拍三个数据源全部抛错（模拟网络 / 超时失败）。
    home._apply((RuntimeError("net"), TimeoutError("t"), RuntimeError("net")))

    # 数据被**保留**（对象同一），而非被清空（需求 28.1）。
    assert home._last_matches == good_matches
    assert home._last_groups == good_groups
    assert home._last_scorers == good_scorers
    # 连接态切换到错误（False），但控件仍持有上一份完好数据。
    assert conn_states[-1] is False


@pytestmark_qt
def test_homepage_partial_failure_updates_only_succeeding_source(qapp):
    """A source that succeeds updates; a source that fails retains last-good."""
    from app.services.data_service import DataService
    from app.ui.pages.home_page import HomePage

    home = HomePage(DataService())
    first_groups = [_group()]
    home._apply((([], [_match()]), (first_groups, {}), [_scorer()]))

    new_matches = [_match(), _match()]
    # standings 失败、sched 成功、scorers 成功。
    home._apply(((["r"], new_matches), RuntimeError("standings down"), [_scorer()]))

    assert home._last_matches == new_matches        # 成功源已更新
    assert home._last_groups == first_groups         # 失败源保留上一份


def test_mainwindow_auto_refresh_retries_on_tick():
    """Req 28.2: the auto-refresh timer re-fetches home/schedule each tick.

    Structural assertion (no network): the auto-refresh handler force-refreshes
    the current dashboard page, so a failed load is retried on the next tick.
    """
    import inspect

    from app.ui import main_window as mw

    src = inspect.getsource(mw.MainWindow._auto_refresh)
    # 当前页为概览 / 赛程 / 比赛详情时强制刷新 → 失败后下一拍自动重试。
    assert "refresh(force=True)" in src
    assert "_home" in src
