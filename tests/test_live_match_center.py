"""Property + unit tests for LiveMatchCenter (Task 12.2 / 12.3).

Covers Task 12.3:
* Property 18: LIVE badge opacity bound — badge opacity stays within [0.7, 1.0].
* Property 19: Live event row creation — each pushed event creates exactly one
  new row.

The breathing-opacity math (``breathing_opacity``) is a pure function and runs
headless. The ``push_event`` row-count behaviour requires a Qt widget and is
skipped when Qt cannot be initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import live_match_center as lmc
from tests.conftest import QT_AVAILABLE


# ════════════════════════════════════════════════════════════════════
#  Property 18: LIVE badge opacity bound
#  Feature: worldcup-ultimate-redesign, Property 18: LIVE badge opacity bound
#  — the breathing badge opacity stays within [0.7, 1.0] for any time t.
#  Validates: Requirements 13.5, 13.7
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(t=st.floats(min_value=-1_000_000.0, max_value=1_000_000.0,
                   allow_nan=False, allow_infinity=False))
def test_property18_breathing_opacity_within_bounds(t):
    # t is randomized over a wide range incl. negative & large magnitudes —
    # the breathing opacity must always stay within [0.7, 1.0].
    op = lmc.breathing_opacity(t)
    assert lmc.LIVE_OPACITY_MIN <= op <= lmc.LIVE_OPACITY_MAX


@settings(max_examples=200)
@given(
    t=st.floats(min_value=-10_000.0, max_value=10_000.0,
                allow_nan=False, allow_infinity=False),
    period=st.floats(min_value=0.2, max_value=8.0,
                     allow_nan=False, allow_infinity=False),
)
def test_property18_within_bounds_any_period(t, period):
    op = lmc.breathing_opacity(t, period=period)
    assert 0.7 <= op <= 1.0


def test_breathing_opacity_endpoints_and_range():
    # t=0 → 上限 1.0（呼吸从最亮开始）。
    assert lmc.breathing_opacity(0.0) == pytest.approx(1.0)
    # 半周期 → 下限 0.7（最暗）。
    half = lmc.LIVE_BREATH_PERIOD_S / 2.0
    assert lmc.breathing_opacity(half) == pytest.approx(0.7, abs=1e-9)
    # 一个整周期回到上限。
    assert lmc.breathing_opacity(lmc.LIVE_BREATH_PERIOD_S) == pytest.approx(1.0)
    # 非正周期兜底返回上限。
    assert lmc.breathing_opacity(3.0, period=0.0) == 1.0


# ════════════════════════════════════════════════════════════════════
#  Property 19: Live event row creation (unit)
#  Feature: worldcup-ultimate-redesign, Property 19: Live event row creation
#  — each pushed event creates exactly one new event row.
#  Validates: Requirements 13.5, 13.7
# ════════════════════════════════════════════════════════════════════
@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt unavailable")
def test_property19_each_push_adds_exactly_one_row(qapp):
    panel = lmc.LiveMatchCenter()
    panel.set_events([])  # 清空（含默认样例事件）。
    assert panel.event_row_count == 0

    events = [
        lmc.MatchEvent(kind="GOAL", minute=12, team_side="home", text="A"),
        lmc.MatchEvent(kind="YELLOW", minute=30, team_side="away", text="B"),
        lmc.MatchEvent(kind="VAR", minute=44, team_side="home", text="C"),
        lmc.MatchEvent(kind="SUB", minute=60, team_side="away", text="D"),
        lmc.MatchEvent(kind="RED", minute=78, team_side="home", text="E"),
        lmc.MatchEvent(kind="GOAL", minute=90, team_side="away", text="F"),
    ]
    for i, ev in enumerate(events, start=1):
        before = panel.event_row_count
        panel.push_event(ev)
        after = panel.event_row_count
        # 每次推送恰好新增一行（需求 13.5，Property 19）。
        assert after == before + 1
        assert after == i


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt unavailable")
def test_live_badge_opacity_stays_in_bounds_when_driven(qapp):
    badge = lmc.LiveBadge()
    for t in (0.0, 0.4, 0.8, 1.6, 2.4, 3.3, 7.7, 12.5, 100.25):
        badge._on_frame(t, 0.016)  # noqa: SLF001
        assert 0.7 <= badge.current_opacity <= 1.0


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt unavailable")
def test_default_is_empty_state(qapp):
    panel = lmc.LiveMatchCenter()
    # 默认空态：无进行中比赛时留空，不展示任何虚构样例比赛。
    assert panel.event_row_count == 0
    assert panel._scoreline_w.isVisibleTo(panel) is False  # noqa: SLF001
    assert panel._clock_lbl.text() == ""  # noqa: SLF001


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt unavailable")
def test_set_live_none_renders_empty(qapp):
    panel = lmc.LiveMatchCenter()
    panel._render_sample()  # noqa: SLF001 - 先填充样例
    assert panel.event_row_count == len(lmc.SAMPLE_EVENTS)
    panel.set_live(None)
    # 回到空态。
    assert panel.event_row_count == 0
    assert panel._scoreline_w.isVisibleTo(panel) is False  # noqa: SLF001
