"""Property + unit tests for win-probability split integrity (Task 8.5).

Feature: worldcup-ultimate-redesign, Property 12: Win-probability split
integrity — for valid triples summing to 100, segment widths are proportional;
invalid triples cause the bar to hide.
Validates: Requirements 7.3, 7.4

The win-probability maths in :mod:`app.ui.widgets.hero_match_card`
(:func:`win_prob_is_valid`, :func:`win_prob_widths`, :func:`win_prob_fractions`)
are pure (no Qt required), so those properties run fully headless. The
``WinProbBar`` widget behaviour (returns ``False`` and hides itself on invalid
input, Requirement 7.4) is exercised via the session ``qapp`` fixture and is
skipped when Qt cannot be initialised offscreen. Each property runs >= 100
Hypothesis examples.
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import hero_match_card as hmc
from tests.conftest import QT_AVAILABLE


# ════════════════════════════════════════════════════════════════════
#  Strategies
# ════════════════════════════════════════════════════════════════════
@st.composite
def valid_triples(draw):
    """Draw a valid (home, draw, away) triple summing to exactly 100.

    Each component is in [0, 100]; built so the constraint holds by
    construction (home + draw <= 100, away = 100 - home - draw).
    """
    h = draw(st.integers(min_value=0, max_value=100))
    d = draw(st.integers(min_value=0, max_value=100 - h))
    a = 100 - h - d
    return (h, d, a)


def _is_valid(triple) -> bool:
    return all(0 <= v <= 100 for v in triple) and sum(triple) == 100


# Triples drawn from a wide range, then filtered to the *invalid* ones
# (sum != 100, out-of-range, or negative components).
invalid_triples = st.tuples(
    st.integers(min_value=-80, max_value=240),
    st.integers(min_value=-80, max_value=240),
    st.integers(min_value=-80, max_value=240),
).filter(lambda t: not _is_valid(t))


# ════════════════════════════════════════════════════════════════════
#  Property 12 — valid triples: proportional, gap-free widths (Req 7.3)
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(triple=valid_triples(), total_width=st.integers(min_value=0, max_value=5_000))
def test_property12_valid_widths_are_proportional_and_fill(triple, total_width):
    """Feature: worldcup-ultimate-redesign, Property 12: Win-probability split
    integrity. Validates: Requirements 7.3, 7.4.

    For a valid triple, the three integer pixel widths are non-negative, sum
    EXACTLY to the total width (gap-free fill), and each segment is within
    +/-1 px of the ideal proportional width ``total_width * component / 100``.
    """
    assert hmc.win_prob_is_valid(triple) is True

    widths = hmc.win_prob_widths(triple, total_width)

    # Three non-negative integers.
    assert len(widths) == 3
    assert all(isinstance(w, int) and w >= 0 for w in widths)

    # Gap-free, no overflow: segments fill the bar exactly.
    assert sum(widths) == max(0, total_width)

    # Proportional within rounding tolerance (+/-1 px).
    for w_seg, component in zip(widths, triple):
        ideal = total_width * component / 100.0
        assert abs(w_seg - ideal) <= 1.0


@settings(max_examples=200)
@given(triple=valid_triples())
def test_property12_fractions_sum_to_one(triple):
    """Feature: worldcup-ultimate-redesign, Property 12. Validates: Req 7.3.

    For a valid triple, the proportional fractions equal component/100 and sum
    to exactly 1.0 (within float tolerance).
    """
    fractions = hmc.win_prob_fractions(triple)
    assert fractions == (triple[0] / 100.0, triple[1] / 100.0, triple[2] / 100.0)
    assert abs(sum(fractions) - 1.0) < 1e-9


# ════════════════════════════════════════════════════════════════════
#  Property 12 — invalid triples: validity False + helpers raise (Req 7.4)
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(triple=invalid_triples)
def test_property12_invalid_triples_are_rejected(triple):
    """Feature: worldcup-ultimate-redesign, Property 12. Validates: Req 7.4.

    For an invalid triple (sum != 100, out-of-range, or negative),
    ``win_prob_is_valid`` is False and the proportional helpers raise
    ``ValueError`` (so callers hide the bar entirely).
    """
    assert hmc.win_prob_is_valid(triple) is False
    with pytest.raises(ValueError):
        hmc.win_prob_fractions(triple)
    with pytest.raises(ValueError):
        hmc.win_prob_widths(triple, 1_000)


# ════════════════════════════════════════════════════════════════════
#  Targeted unit examples (edge cases)
# ════════════════════════════════════════════════════════════════════
def test_zero_width_yields_all_zero_segments():
    assert hmc.win_prob_widths((47, 26, 27), 0) == (0, 0, 0)


def test_extreme_single_segment_fills_bar():
    assert hmc.win_prob_widths((100, 0, 0), 500) == (500, 0, 0)
    assert hmc.win_prob_widths((0, 0, 100), 500) == (0, 0, 500)


def test_sample_fixture_triple_is_valid():
    # Sampled fixture from Requirement 7.2: 47% / 26% / 27%.
    assert hmc.win_prob_is_valid((47, 26, 27)) is True
    assert sum(hmc.win_prob_widths((47, 26, 27), 1_000)) == 1_000


def test_invalid_examples_rejected():
    assert hmc.win_prob_is_valid((40, 30, 40)) is False  # sums to 110
    assert hmc.win_prob_is_valid((50, 60, -10)) is False  # negative component
    assert hmc.win_prob_is_valid((33, 33, 33)) is False   # sums to 99
    assert hmc.win_prob_is_valid((101, 0, -1)) is False    # out of range


# ════════════════════════════════════════════════════════════════════
#  Qt-backed WinProbBar widget tests (skipped if Qt is unavailable)
#  Req 7.4: invalid input -> set_probabilities returns False and bar hides.
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


@pytestmark_qt
@settings(max_examples=100, deadline=None)
@given(triple=invalid_triples)
def test_property12_winprobbar_hides_on_invalid(qapp, triple):
    """Feature: worldcup-ultimate-redesign, Property 12. Validates: Req 7.4.

    For any invalid triple, ``WinProbBar.set_probabilities`` returns False and
    the bar hides itself (``isHidden()`` True).
    """
    from app.ui.widgets.hero_match_card import WinProbBar

    bar = WinProbBar()
    result = bar.set_probabilities(triple)
    assert result is False
    assert bar.is_valid is False
    assert bar.isHidden() is True


@pytestmark_qt
@settings(max_examples=100, deadline=None)
@given(triple=valid_triples())
def test_property12_winprobbar_shows_on_valid(qapp, triple):
    """Feature: worldcup-ultimate-redesign, Property 12. Validates: Req 7.3.

    For any valid triple, ``WinProbBar.set_probabilities`` returns True and the
    bar is not hidden.
    """
    from app.ui.widgets.hero_match_card import WinProbBar

    bar = WinProbBar()
    result = bar.set_probabilities(triple)
    assert result is True
    assert bar.is_valid is True
    assert bar.isHidden() is False
