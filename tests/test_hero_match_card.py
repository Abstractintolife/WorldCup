"""Property + unit tests for the Hero Match Card (Task 8).

Covers:
* Task 8.3 — Property 10: Countdown monotonicity (Requirement 6.2).
* Task 8.5 — Property 12: Win-probability split integrity (Requirements 7.3, 7.4).
* Task 8.7 — Unit: missing rating/rank renders "—" (Requirement 8.2).

The numeric maths (remaining-time decomposition, win-probability widths,
ranking placeholder) are pure functions and run headless. Qt-backed widget
tests additionally exercise ``HeroMatchCard`` and are skipped when Qt cannot be
initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import hero_match_card as hmc
from tests.conftest import QT_AVAILABLE

_BASE = datetime(2026, 6, 25, 3, 0, 0, tzinfo=timezone.utc)


# ════════════════════════════════════════════════════════════════════
#  Property 10 — Countdown monotonicity (pure)
#  Feature: worldcup-ultimate-redesign, Property 10: Countdown monotonicity —
#  for consecutive ticks before kickoff, displayed remaining time is
#  non-increasing and never negative.
#  Validates: Requirements 6.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(
    kickoff_offset=st.integers(min_value=-100_000, max_value=2_000_000),
    now_offsets=st.lists(
        st.integers(min_value=0, max_value=3_000_000),
        min_size=2, max_size=40,
    ),
)
def test_property10_remaining_non_increasing_and_non_negative(kickoff_offset, now_offsets):
    kickoff = _BASE + timedelta(seconds=kickoff_offset)
    # 时间向前推进 → now 单调不减。
    nows = sorted(_BASE + timedelta(seconds=o) for o in now_offsets)
    rems = [hmc.remaining_seconds(kickoff, n) for n in nows]

    # 绝不为负。
    for r in rems:
        assert r >= 0
    # 连续两次采样非递增。
    for a, b in zip(rems, rems[1:]):
        assert b <= a


@settings(max_examples=200)
@given(s=st.integers(min_value=-10, max_value=10_000_000))
def test_decompose_recombines_and_bounds(s):
    days, hours, minutes, seconds = hmc.decompose_remaining(s)
    expected = max(0, s)
    assert days * 86_400 + hours * 3_600 + minutes * 60 + seconds == expected
    assert 0 <= hours < 24
    assert 0 <= minutes < 60
    assert 0 <= seconds < 60
    # 时 / 分 / 秒 三栏：天折算进小时。
    H, M, S = hmc.countdown_fields(s)
    assert H == days * 24 + hours
    assert (M, S) == (minutes, seconds)


def test_remaining_seconds_clamps_past_and_none():
    assert hmc.remaining_seconds(None, _BASE) == 0
    past = _BASE - timedelta(hours=1)
    assert hmc.remaining_seconds(past, _BASE) == 0
    fut = _BASE + timedelta(seconds=90)
    assert hmc.remaining_seconds(fut, _BASE) == 90


# ════════════════════════════════════════════════════════════════════
#  Property 12 — Win-probability split integrity (pure)
#  Feature: worldcup-ultimate-redesign, Property 12: Win-probability split
#  integrity — for valid triples summing to 100, segment widths are
#  proportional; invalid triples cause the bar to hide.
#  Validates: Requirements 7.3, 7.4
# ════════════════════════════════════════════════════════════════════
@st.composite
def _valid_triple(draw):
    h = draw(st.integers(min_value=0, max_value=100))
    d = draw(st.integers(min_value=0, max_value=100 - h))
    a = 100 - h - d
    return (h, d, a)


@settings(max_examples=200)
@given(triple=_valid_triple(), width=st.integers(min_value=0, max_value=4000))
def test_property12_valid_widths_proportional(triple, width):
    assert hmc.win_prob_is_valid(triple)

    widths = hmc.win_prob_widths(triple, width)
    # 铺满、无缝。
    assert sum(widths) == max(0, width)

    fr = hmc.win_prob_fractions(triple)
    assert abs(sum(fr) - 1.0) < 1e-9
    assert fr == (triple[0] / 100.0, triple[1] / 100.0, triple[2] / 100.0)

    # 每段宽度正比于占比（像素取整精度内）。
    for wi, fi in zip(widths, fr):
        assert abs(wi - fi * max(0, width)) <= 1.0


@settings(max_examples=300)
@given(triple=st.tuples(
    st.integers(min_value=-60, max_value=220),
    st.integers(min_value=-60, max_value=220),
    st.integers(min_value=-60, max_value=220),
))
def test_property12_validity_matches_definition(triple):
    expected = all(0 <= v <= 100 for v in triple) and sum(triple) == 100
    assert hmc.win_prob_is_valid(triple) is expected
    if not expected:
        # 非法 → 占比 / 宽度计算抛错（调用方据此隐藏整条，需求 7.4）。
        with pytest.raises(ValueError):
            hmc.win_prob_fractions(triple)
        with pytest.raises(ValueError):
            hmc.win_prob_widths(triple, 100)


@settings(max_examples=200)
@given(probs=st.tuples(
    st.floats(min_value=0.0, max_value=1_000.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1_000.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1_000.0, allow_nan=False, allow_infinity=False),
))
def test_percentages_to_100_normalises_to_valid_triple(probs):
    triple = hmc.percentages_to_100(probs)
    assert sum(triple) == 100
    assert all(v >= 0 for v in triple)
    assert hmc.win_prob_is_valid(triple)


# ════════════════════════════════════════════════════════════════════
#  Task 8.7 — Unit: missing rating/rank renders "—" (Requirement 8.2)
# ════════════════════════════════════════════════════════════════════
def test_fmt_rank_placeholder_for_missing():
    assert hmc.fmt_rank(None) == "—"
    assert hmc.fmt_rank(0) == "0"
    assert hmc.fmt_rank(13) == "13"


def test_hero_meta_win_prob_validation():
    assert hmc.HeroMeta(win_prob=(47, 26, 27)).win_prob_valid is True
    assert hmc.HeroMeta(win_prob=(50, 26, 27)).win_prob_valid is False
    assert hmc.HeroMeta().win_prob_valid is False  # default (0,0,0)


# ════════════════════════════════════════════════════════════════════
#  Qt-backed widget tests (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


def _make_match():
    from app.models.match import Match

    return Match(
        match_id="1",
        team_a_id="a", team_a_name="瑞士",
        team_b_id="b", team_b_name="加拿大",
    )


@pytestmark_qt
def test_hero_card_renders_dash_for_missing_ratings(qapp):
    """Req 8.2: missing Elo / FIFA / world rank render '—'."""
    from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta

    card = HeroMatchCard()
    card.set_match(_make_match(), HeroMeta(win_prob=(47, 26, 27)))
    assert "—" in card._home_ratings.text()
    assert "—" in card._away_ratings.text()


@pytestmark_qt
def test_hero_card_hides_bar_for_invalid_win_prob(qapp):
    """Req 7.4: invalid win_prob hides the split bar (and its labels)."""
    from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta

    card = HeroMatchCard()
    card.set_match(_make_match(), HeroMeta(win_prob=(40, 30, 40)))  # sums to 110
    assert card._prob_bar.is_valid is False
    assert card._prob_bar.isVisibleTo(card) is False
    assert card._prob_labels_host.isVisibleTo(card) is False

    # Valid triple -> bar + labels shown, labels driven by data.
    card.set_match(_make_match(), HeroMeta(win_prob=(47, 26, 27)))
    assert card._prob_bar.is_valid is True
    assert card._prob_bar.isVisibleTo(card) is True
    assert card._lbl_home.text() == "47% 瑞士胜"
    assert card._lbl_draw.text() == "26% 平局"
    assert card._lbl_away.text() == "27% 加拿大胜"


@pytestmark_qt
def test_hero_card_single_countdown_timer(qapp):
    """Req 6.4: exactly one per-second QTimer owned by the card."""
    from PyQt6.QtCore import QTimer

    from app.ui.widgets.hero_match_card import HeroMatchCard

    card = HeroMatchCard()
    timers = card.findChildren(QTimer)
    assert len(timers) == 1
    assert timers[0].interval() == 1000


@pytestmark_qt
def test_hero_card_countdown_runs_then_stops_at_kickoff(qapp):
    """Req 6.1/6.3: timer runs before kickoff; stops + shows LIVE at kickoff."""
    from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta

    card = HeroMatchCard()

    future = datetime.now(timezone.utc) + timedelta(hours=2, minutes=5, seconds=30)
    card.set_match(_make_match(), HeroMeta(kickoff_utc=future, win_prob=(47, 26, 27)))
    assert card._cd_timer.isActive() is True

    past = datetime.now(timezone.utc) - timedelta(seconds=5)
    card.set_match(_make_match(), HeroMeta(kickoff_utc=past, win_prob=(47, 26, 27)))
    assert card._cd_timer.isActive() is False
    assert card._clock._live.isVisibleTo(card._clock) is True
