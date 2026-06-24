"""Targeted unit tests for the Stage Compositor ambient layers (Task 2.3).

These are **deterministic, sampling-based unit tests** (not randomized PBT),
per the spec's Testing Strategy note that Properties 7 and 9 are validated via
targeted unit tests. They exercise the pure, GUI-free compositing logic in
``app.ui.widgets.stage_compositor`` and therefore run fully headless (no Qt /
no GL context required).

Property 7 — Ambient layer opacity bands: sample ``ambient_contributions``
across a dense grid of ``uv`` in [0,1]^2 and several ``t`` values; assert each
layer's weighted contribution stays within its design band
(floodlights ~8%, grass 3-5%, pitch ~2%, trophy ~2%).

Property 9 — Trophy silhouette is static: for fixed ``uv`` samples, assert the
L5 ``trophy_silhouette`` output (and the ``trophy`` contribution) is identical
across a wide range of varied ``t`` values (time-invariance).

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import math

from app.ui.widgets import stage_compositor as sc

_EPS = 1e-9


def _uv_grid(n: int = 21):
    """Dense deterministic grid of uv samples over [0,1]^2 (n*n points)."""
    step = 1.0 / (n - 1)
    return [(i * step, j * step) for i in range(n) for j in range(n)]


# A spread of times including 0, sub-second, multi-second, and large values to
# exercise any slow time-driven drift in the floodlight pools.
_T_SAMPLES = [0.0, 0.25, 0.5, 1.0, 2.5, 4.0, 7.999, 8.0, 13.37, 60.0,
              123.456, 1000.0, 9999.0]


# ════════════════════════════════════════════════════════════════════
#  Property 7: Ambient layer opacity bands
#  Feature: worldcup-ultimate-redesign, Property 7: Ambient layer opacity
#  bands — for all pixels/regions, each ambient layer's contribution stays
#  within its specified opacity band (floodlights ~8%, grass 3-5%, pitch ~2%,
#  trophy ~2%).
#  Validates: Requirements 16.3
# ════════════════════════════════════════════════════════════════════
def test_property7_ambient_layer_opacity_bands_grid_sampling():
    """Sample contributions across a 21x21 uv grid x 13 times (5733 samples);
    every layer's weighted contribution must stay within [0, band-ceiling]."""
    grid = _uv_grid(21)
    samples = 0
    for t in _T_SAMPLES:
        for uv in grid:
            c = sc.ambient_contributions(uv, t)
            samples += 1
            assert 0.0 <= c["floodlight"] <= sc.FLOODLIGHT_OPACITY + _EPS, (uv, t, c)
            assert 0.0 <= c["grass"] <= sc.GRASS_OPACITY + _EPS, (uv, t, c)
            assert 0.0 <= c["pitch"] <= sc.PITCH_OPACITY + _EPS, (uv, t, c)
            assert 0.0 <= c["trophy"] <= sc.TROPHY_OPACITY + _EPS, (uv, t, c)
    # Sanity: confirm we actually exercised the full grid x time matrix.
    assert samples == 21 * 21 * len(_T_SAMPLES)


def test_property7_grass_band_is_within_design_range():
    """The grass layer weight (4%) must sit inside the design band 3-5%, and
    the band itself must match the spec's 3-5% range."""
    lo, hi = sc.GRASS_OPACITY_BAND
    assert (lo, hi) == (0.03, 0.05)
    assert lo <= sc.GRASS_OPACITY <= hi


def test_property7_band_ceilings_match_design_constants():
    """The four band ceilings match the spec values (floodlight ~8%, grass ~4%,
    pitch ~2%, trophy ~2%)."""
    assert sc.FLOODLIGHT_OPACITY == 0.08
    assert sc.GRASS_OPACITY == 0.04
    assert sc.PITCH_OPACITY == 0.02
    assert sc.TROPHY_OPACITY == 0.02


def test_property7_each_layer_reaches_near_its_ceiling_somewhere():
    """Sampling check that the bands are tight (not vacuously satisfied): each
    layer attains a contribution close to its ceiling somewhere on the grid."""
    grid = _uv_grid(41)
    peak = {"floodlight": 0.0, "grass": 0.0, "pitch": 0.0, "trophy": 0.0}
    for uv in grid:
        c = sc.ambient_contributions(uv, 0.0)
        for k in peak:
            if c[k] > peak[k]:
                peak[k] = c[k]
    # Floodlight pools are broad and easily near their ceiling.
    assert peak["floodlight"] >= 0.5 * sc.FLOODLIGHT_OPACITY
    # Pitch markings and trophy have well-defined bright cores on the grid.
    assert peak["pitch"] >= 0.5 * sc.PITCH_OPACITY
    assert peak["trophy"] >= 0.5 * sc.TROPHY_OPACITY


def test_property7_composite_color_stays_in_unit_cube():
    """Final composited color components remain within [0,1] across the grid."""
    for t in (0.0, 4.0, 100.0):
        for uv in _uv_grid(21):
            col = sc.composite_ambient(uv, t)
            assert len(col) == 3
            for ch in col:
                assert 0.0 <= ch <= 1.0, (uv, t, col)


# ════════════════════════════════════════════════════════════════════
#  Property 9: Trophy silhouette is static
#  Feature: worldcup-ultimate-redesign, Property 9: Trophy silhouette is
#  static — for all times t, the trophy-silhouette layer output depends only
#  on position (uv), not on t.
#  Validates: Requirements 16.4
# ════════════════════════════════════════════════════════════════════
# Wide spread of varied t (incl. negatives, sub-second, large) for invariance.
_T_INVARIANCE = [-1000.0, -8.0, -0.5, 0.0, 0.1, 0.5, 1.0, 3.14159, 8.0,
                 42.0, 360.0, 1000.0, 86400.0, 1e6]


def test_property9_trophy_silhouette_is_time_invariant():
    """For fixed uv, trophy_silhouette(uv) and the 'trophy' contribution from
    ambient_contributions are IDENTICAL across a wide range of varied t."""
    grid = _uv_grid(21)
    for uv in grid:
        baseline = sc.trophy_silhouette(uv)
        contrib_baseline = sc.ambient_contributions(uv, _T_INVARIANCE[0])["trophy"]
        for t in _T_INVARIANCE:
            # Pure position function: no dependence on t whatsoever.
            assert sc.trophy_silhouette(uv) == baseline, (uv, t)
            # The weighted trophy contribution is likewise t-invariant.
            assert sc.ambient_contributions(uv, t)["trophy"] == contrib_baseline, (uv, t)
        # Contribution is exactly the silhouette intensity scaled by the band.
        assert math.isclose(
            contrib_baseline, baseline * sc.TROPHY_OPACITY, rel_tol=0.0, abs_tol=_EPS
        )


def test_property9_trophy_silhouette_bounded_on_grid():
    """The L5 intensity stays within [0,1] everywhere on the grid."""
    for uv in _uv_grid(41):
        v = sc.trophy_silhouette(uv)
        assert 0.0 <= v <= 1.0, uv


def test_property9_only_trophy_layer_is_time_invariant_sanity():
    """Sanity guard: the floodlight layer DOES vary with t at some pixel, so the
    invariance asserted above is specific to the trophy layer, not trivially
    true for every layer."""
    # Scan the grid for ANY pixel on the floodlight-pool slope (i.e. not
    # clamped to the band ceiling) whose contribution changes between two
    # times; the pools drift slowly with t, so such a pixel must exist.
    varies = False
    for uv in _uv_grid(41):
        a = sc.ambient_contributions(uv, 0.0)["floodlight"]
        b = sc.ambient_contributions(uv, 4.0)["floodlight"]
        if a != b:
            varies = True
            break
    assert varies, "expected at least one pixel where the floodlight layer varies with t"
