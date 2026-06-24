"""Property + unit tests for the Hero Match Card countdown maths (Task 8.3).

Feature: worldcup-ultimate-redesign, Property 10: Countdown monotonicity —
for consecutive ticks before kickoff, displayed remaining time is
non-increasing and never negative.
Validates: Requirements 6.2

The countdown numeric maths in :mod:`app.ui.widgets.hero_match_card`
(:func:`remaining_seconds`, :func:`decompose_remaining`,
:func:`countdown_fields`) are pure (no Qt required), so these tests run fully
headless. Each property runs >= 100 Hypothesis examples.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import hero_match_card as hmc

# A fixed reference kickoff instant used to anchor relative offsets.
_BASE = datetime(2026, 6, 25, 3, 0, 0, tzinfo=timezone.utc)


# ════════════════════════════════════════════════════════════════════
#  Property 10 — Countdown monotonicity (remaining_seconds)
#  Feature: worldcup-ultimate-redesign, Property 10: Countdown monotonicity
#  Validates: Requirements 6.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(
    kickoff_offset=st.integers(min_value=-100_000, max_value=2_000_000),
    now_offsets=st.lists(
        st.integers(min_value=-50_000, max_value=3_000_000),
        min_size=2, max_size=50,
    ),
)
def test_property10_remaining_non_increasing_and_non_negative(kickoff_offset, now_offsets):
    """For an increasing sequence of `now`, remaining time is non-increasing
    across the sequence and always >= 0 (never negative)."""
    kickoff = _BASE + timedelta(seconds=kickoff_offset)
    # Advancing wall-clock time -> `now` is monotonically non-decreasing.
    nows = sorted(_BASE + timedelta(seconds=o) for o in now_offsets)
    rems = [hmc.remaining_seconds(kickoff, n) for n in nows]

    # Never negative (Requirement 6.2).
    for r in rems:
        assert r >= 0

    # Consecutive ticks: displayed remaining time is non-increasing.
    for earlier, later in zip(rems, rems[1:]):
        assert later <= earlier


@settings(max_examples=200)
@given(
    kickoff_offset=st.integers(min_value=-100_000, max_value=2_000_000),
    after_offset=st.integers(min_value=0, max_value=5_000_000),
)
def test_property10_zero_at_or_after_kickoff(kickoff_offset, after_offset):
    """At or after kickoff, remaining_seconds is exactly 0 (never negative)."""
    kickoff = _BASE + timedelta(seconds=kickoff_offset)
    # Any `now` at-or-after kickoff.
    now = kickoff + timedelta(seconds=after_offset)
    assert hmc.remaining_seconds(kickoff, now) == 0


@settings(max_examples=200)
@given(seconds_before=st.integers(min_value=1, max_value=5_000_000))
def test_property10_strictly_before_kickoff_is_positive_and_floored(seconds_before):
    """Strictly before kickoff, remaining time is positive and equals the
    integer floor of the second-delta (matching per-second display)."""
    kickoff = _BASE
    now = kickoff - timedelta(seconds=seconds_before)
    rem = hmc.remaining_seconds(kickoff, now)
    assert rem >= 1
    assert rem == seconds_before


# ════════════════════════════════════════════════════════════════════
#  decompose_remaining — sum invariant + field ranges (incl. negatives)
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(total=st.integers(min_value=-1_000_000, max_value=10_000_000))
def test_decompose_remaining_invariant_and_bounds(total):
    """For any integer seconds (including negatives), the decomposition is
    non-negative, recombines to max(0, total), and respects field ranges."""
    days, hours, minutes, seconds = hmc.decompose_remaining(total)

    # All fields non-negative.
    assert days >= 0
    assert hours >= 0
    assert minutes >= 0
    assert seconds >= 0

    # Sum invariant: negatives clamp to 0.
    expected = max(0, total)
    assert days * 86_400 + hours * 3_600 + minutes * 60 + seconds == expected

    # Field ranges.
    assert 0 <= hours < 24
    assert 0 <= minutes < 60
    assert 0 <= seconds < 60


# ════════════════════════════════════════════════════════════════════
#  countdown_fields — total_hours folds days, matches decompose
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(total=st.integers(min_value=-1_000_000, max_value=10_000_000))
def test_countdown_fields_matches_decompose(total):
    """countdown_fields rolls days into hours (total_hours = days*24 + hours)
    and keeps minutes/seconds identical to decompose_remaining."""
    days, hours, minutes, seconds = hmc.decompose_remaining(total)
    total_hours, m, s = hmc.countdown_fields(total)

    assert total_hours == days * 24 + hours
    assert (m, s) == (minutes, seconds)
    # Recombining the folded form also satisfies the sum invariant.
    assert total_hours * 3_600 + m * 60 + s == max(0, total)


# ════════════════════════════════════════════════════════════════════
#  Targeted unit examples (edge cases)
# ════════════════════════════════════════════════════════════════════
def test_remaining_seconds_none_kickoff_is_zero():
    assert hmc.remaining_seconds(None, _BASE) == 0


def test_remaining_seconds_past_kickoff_is_zero():
    past = _BASE - timedelta(hours=3)
    assert hmc.remaining_seconds(past, _BASE) == 0


def test_remaining_seconds_exact_kickoff_is_zero():
    assert hmc.remaining_seconds(_BASE, _BASE) == 0


def test_remaining_seconds_future_floors_fractional_second():
    # 90.9s before kickoff -> floored to 90 displayed seconds.
    now = _BASE - timedelta(seconds=90, milliseconds=900)
    assert hmc.remaining_seconds(_BASE, now) == 90


def test_remaining_seconds_naive_datetime_treated_as_utc():
    naive_kickoff = datetime(2026, 6, 25, 3, 0, 0)  # no tzinfo
    naive_now = datetime(2026, 6, 25, 2, 0, 0)
    assert hmc.remaining_seconds(naive_kickoff, naive_now) == 3_600


def test_decompose_negative_clamps_to_zero():
    assert hmc.decompose_remaining(-12_345) == (0, 0, 0, 0)


def test_decompose_known_value():
    # 1 day, 2 hours, 3 minutes, 4 seconds.
    total = 1 * 86_400 + 2 * 3_600 + 3 * 60 + 4
    assert hmc.decompose_remaining(total) == (1, 2, 3, 4)
    assert hmc.countdown_fields(total) == (26, 3, 4)


def test_per_second_decrement_is_monotone_to_kickoff():
    """A simulated per-second tick stream is strictly decreasing then pins
    at 0 from kickoff onward (the observable countdown behaviour)."""
    kickoff = _BASE
    rems = [
        hmc.remaining_seconds(kickoff, kickoff - timedelta(seconds=5) + timedelta(seconds=i))
        for i in range(10)
    ]
    assert rems == [5, 4, 3, 2, 1, 0, 0, 0, 0, 0]
