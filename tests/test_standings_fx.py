"""Property tests for standings_fx pure helpers (Task 10.2).

Covers the three standings Correctness Properties whose math lives in pure,
GUI-free helpers in :mod:`app.ui.widgets.fx.standings_fx`:

* Property 14 — Form pills validity (``normalize_form`` → ≤5 items, each ∈ {W,D,L}).
* Property 15 — Rank-change glyph correctness (``rank_delta_glyph``).
* Property 16 — Qualification bar proportionality (``qual_fill_fraction`` → clamp(p,0,1)).

The helpers are pure and run headless. Where useful we additionally drive the
real Qt widgets (``FormPills`` / ``QualBar``) under the session ``qapp`` fixture
to assert their observable state mirrors the pure functions.

Each property runs ≥ 100 Hypothesis examples.

Feature: worldcup-ultimate-redesign
Validates: Requirements 10.4, 10.7, 10.5
"""
from __future__ import annotations

import math

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.ui.widgets.fx import (
    normalize_form,
    qual_fill_fraction,
    rank_delta_glyph,
)
from app.ui.widgets.fx.standings_fx import FORM_RESULTS, MAX_FORM_PILLS

_VALID = set(FORM_RESULTS)  # {"W", "D", "L"}


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


# ════════════════════════════════════════════════════════════════════
#  Property 14: Form pills validity
#  Feature: worldcup-ultimate-redesign, Property 14: Form pills validity
#  — for ANY input sequence, normalize_form returns a list of length ≤ 5 where
#  every element ∈ {W, D, L}.
#  Validates: Requirements 10.4
# ════════════════════════════════════════════════════════════════════

# A deliberately messy generator: valid letters (any case, padded), invalid
# letters/strings, digits, None, empty strings — to stress the normaliser.
_form_item = st.one_of(
    st.sampled_from(["W", "D", "L", "w", "d", "l", " W ", "L\n", "\td"]),
    st.text(max_size=4),
    st.sampled_from(["X", "Z", "win", "", "WW", "1", "draw"]),
    st.none(),
    st.integers(min_value=-10, max_value=10),
)


@settings(max_examples=300)
@given(seq=st.lists(_form_item, min_size=0, max_size=40))
def test_property14_form_pills_validity(seq):
    out = normalize_form(seq)
    # (10.4) at most MAX_FORM_PILLS (5) pills.
    assert isinstance(out, list)
    assert len(out) <= MAX_FORM_PILLS
    # (10.4) every rendered pill is one of {W, D, L}.
    for ch in out:
        assert ch in _VALID


@settings(max_examples=150)
@given(seq=st.lists(st.sampled_from(["W", "D", "L"]), min_size=0, max_size=40))
def test_property14_keeps_last_five_valid(seq):
    out = normalize_form(seq)
    expected = seq[-MAX_FORM_PILLS:]
    # For already-valid input the normaliser keeps the most recent ≤5 verbatim.
    assert out == expected


@settings(max_examples=120, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seq=st.lists(_form_item, min_size=0, max_size=30))
def test_property14_widget_results(qapp, seq):
    """Drive the real FormPills widget; .results must satisfy Property 14."""
    from app.ui.widgets.fx import FormPills

    pills = FormPills(seq)
    try:
        results = pills.results
        assert len(results) <= MAX_FORM_PILLS
        for ch in results:
            assert ch in _VALID
        # Observable state matches the pure helper exactly.
        assert results == normalize_form(seq)
    finally:
        pills.deleteLater()


# ════════════════════════════════════════════════════════════════════
#  Property 15: Rank-change glyph correctness
#  Feature: worldcup-ultimate-redesign, Property 15: Rank-change glyph correctness
#  — ↑n / ↓n / — matches the sign of delta, with n = |delta|.
#  Validates: Requirements 10.7
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(delta=st.integers(min_value=-10_000, max_value=10_000))
def test_property15_rank_delta_glyph(delta):
    glyph = rank_delta_glyph(delta)
    if delta > 0:
        assert glyph == f"↑{delta}"
        assert glyph[0] == "↑"
        # n equals |delta|.
        assert int(glyph[1:]) == abs(delta)
    elif delta < 0:
        assert glyph == f"↓{-delta}"
        assert glyph[0] == "↓"
        assert int(glyph[1:]) == abs(delta)
    else:
        assert glyph == "—"


@settings(max_examples=100)
@given(delta=st.integers(min_value=-1000, max_value=1000))
def test_property15_magnitude_is_abs(delta):
    glyph = rank_delta_glyph(delta)
    if delta == 0:
        assert glyph == "—"
    else:
        # Strip the leading arrow; remaining digits == |delta|.
        assert int(glyph[1:]) == abs(delta)


def test_property15_none_and_zero():
    assert rank_delta_glyph(None) == "—"
    assert rank_delta_glyph(0) == "—"


# ════════════════════════════════════════════════════════════════════
#  Property 16: Qualification bar proportionality
#  Feature: worldcup-ultimate-redesign, Property 16: Qualification bar proportionality
#  — fill fraction equals clamp(p, 0, 1); None → 0.0.
#  Validates: Requirements 10.5
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(p=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_property16_qual_fill_fraction(p):
    frac = qual_fill_fraction(p)
    # (10.5) result is always within [0, 1].
    assert 0.0 <= frac <= 1.0
    # (10.5) result equals clamp(p, 0, 1).
    assert math.isclose(frac, _clamp01(p), rel_tol=0, abs_tol=1e-12)


@settings(max_examples=120)
@given(p=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_property16_in_range_is_identity(p):
    # Inside [0,1] the fraction is the value itself.
    assert math.isclose(qual_fill_fraction(p), p, abs_tol=1e-12)


def test_property16_none_is_zero():
    assert qual_fill_fraction(None) == 0.0


@settings(max_examples=120, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(p=st.one_of(
    st.none(),
    st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
))
def test_property16_widget_fraction(qapp, p):
    """Drive the real QualBar widget; .fraction must equal clamp(p,0,1)."""
    from app.ui.widgets.fx import QualBar

    bar = QualBar(p)
    try:
        frac = bar.fraction
        assert 0.0 <= frac <= 1.0
        expected = 0.0 if p is None else _clamp01(p)
        assert math.isclose(frac, expected, abs_tol=1e-12)
    finally:
        bar.deleteLater()
