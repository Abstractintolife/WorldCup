"""Property test for floodlight-sweep periodicity (Task 3.4 / design Property 8).

These tests are **pure-logic** and run fully headless (no Qt / no GL context):
they exercise the pure ``sweep_positions(t)`` / ``floodlight_sweep(uv, t)``
functions in :mod:`app.ui.widgets.stage_compositor`, which are the single source
of truth shared by both the GPU fragment shader and the CPU fallback renderer.

Property 8 — Floodlight sweep periodicity:
  * For any time ``t`` the beam positions repeat with period ``SWEEP_PERIOD``
    (8 s), i.e. ``sweep_positions(t) ≈ sweep_positions(t + 8.0)`` and likewise
    the combined sweep intensity ``floodlight_sweep(uv, t)`` repeats every 8 s.
  * For any screen coordinate ``uv ∈ [0,1]^2`` and any ``t`` the combined
    opacity contribution is bounded by ``SWEEP_OPACITY_CEIL`` (~5%).

Each property runs >= 100 Hypothesis iterations over a wide range of ``t`` that
includes negative and large magnitudes.

Feature: worldcup-ultimate-redesign, Property 8: Floodlight sweep periodicity
Validates: Requirements 18.1, 18.2
"""
from __future__ import annotations

import math

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from app.ui.widgets import stage_compositor as sc

# Position equality is mathematically exact across the sampled range; a tiny
# absolute tolerance guards against any incidental floating-point noise.
_POS_ABS_TOL = 1e-9
_OPACITY_EPS = 1e-9

# Sampling space: normalised screen coords uv ∈ [0,1]^2 and time t over a wide
# band that intentionally spans negatives and large magnitudes.
_uv = st.tuples(
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
_t_wide = st.floats(
    min_value=-1_000_000.0,
    max_value=1_000_000.0,
    allow_nan=False,
    allow_infinity=False,
)


def _assume_not_at_wrap_boundary(t: float) -> None:
    """Skip the measure-zero sawtooth wrap point for periodicity comparisons.

    The beam sweep is a sawtooth: it eases LEFT→RIGHT across a cycle and snaps
    back at the period boundary. ``sweep_positions`` is therefore discontinuous
    at phase 0 ≡ 1. For an infinitesimal negative ``t`` (e.g. ``-1e-300``),
    ``t % 8.0`` rounds up to exactly ``8.0`` (phase 1.0, beam at RIGHT) while
    ``(t + 8.0) % 8.0`` yields ``0.0`` (phase 0.0, beam at LEFT) — a pure
    floating-point artifact that never arises with a monotonic FrameClock.
    Excluding only this boundary keeps the periodicity claim meaningful.
    """
    phase = (t % sc.SWEEP_PERIOD) / sc.SWEEP_PERIOD
    assume(1e-9 < phase < 1.0 - 1e-9)


# ════════════════════════════════════════════════════════════════════
#  Property 8: Floodlight sweep periodicity — beam positions
#  Feature: worldcup-ultimate-redesign, Property 8: Floodlight sweep periodicity
#  Validates: Requirements 18.1
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(t=_t_wide)
def test_floodlight_sweep_position_periodicity(t):
    """sweep_positions(t) repeats with period SWEEP_PERIOD (8 s)."""
    _assume_not_at_wrap_boundary(t)
    assert sc.SWEEP_PERIOD == 8.0
    x1_now, x2_now = sc.sweep_positions(t)
    x1_next, x2_next = sc.sweep_positions(t + sc.SWEEP_PERIOD)
    assert math.isclose(x1_now, x1_next, abs_tol=_POS_ABS_TOL)
    assert math.isclose(x2_now, x2_next, abs_tol=_POS_ABS_TOL)
    # Positions stay within the configured sweep span [LEFT, RIGHT].
    lo, hi = sc.SWEEP_LEFT, sc.SWEEP_RIGHT
    assert lo - _OPACITY_EPS <= x1_now <= hi + _OPACITY_EPS
    assert lo - _OPACITY_EPS <= x2_now <= hi + _OPACITY_EPS


# ════════════════════════════════════════════════════════════════════
#  Property 8: Floodlight sweep periodicity — combined intensity
#  Feature: worldcup-ultimate-redesign, Property 8: Floodlight sweep periodicity
#  Validates: Requirements 18.1
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(uv=_uv, t=_t_wide)
def test_floodlight_sweep_intensity_periodicity(uv, t):
    """floodlight_sweep(uv, t) repeats with period SWEEP_PERIOD (8 s)."""
    _assume_not_at_wrap_boundary(t)
    a_now = sc.floodlight_sweep(uv, t)
    a_next = sc.floodlight_sweep(uv, t + sc.SWEEP_PERIOD)
    assert math.isclose(a_now, a_next, abs_tol=_POS_ABS_TOL)


# ════════════════════════════════════════════════════════════════════
#  Property 8: Floodlight sweep periodicity — opacity ceiling
#  Feature: worldcup-ultimate-redesign, Property 8: Floodlight sweep periodicity
#  Validates: Requirements 18.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(uv=_uv, t=_t_wide)
def test_floodlight_sweep_opacity_ceiling(uv, t):
    """Combined sweep opacity is non-negative and <= SWEEP_OPACITY_CEIL (~5%)."""
    a = sc.floodlight_sweep(uv, t)
    assert 0.0 <= a <= sc.SWEEP_OPACITY_CEIL + _OPACITY_EPS
