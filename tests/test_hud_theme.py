"""Unit + light property tests for the HUD theme token helpers.

Task 1.2 — validates Requirements 16.2 (night-stadium gradient ramp) and
20.1 (glass-card material tokens). These tests are pure (no Qt needed):
``rgba()`` / ``mix()`` are plain string/number helpers.
"""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.design.hud_theme import (
    NIGHT_STADIUM,
    Radius,
    Shadow,
    _parse_color,
    build_qss,
    mix,
    rgba,
)


# ─────────────────────────── gradient ramp ───────────────────────────
def test_night_stadium_gradient_ramp_values():
    """The base vertical ramp matches the spec's exact hex stops (Req 16.2)."""
    assert NIGHT_STADIUM.bg_top == "#06111A"
    assert NIGHT_STADIUM.bg_mid == "#0A1B28"
    assert NIGHT_STADIUM.bg_bottom == "#0F2A1F"


def test_glass_material_tokens():
    """Glass fill/border tokens match the spec (Req 20.1)."""
    assert NIGHT_STADIUM.glass_fill == "rgba(255,255,255,0.05)"
    assert NIGHT_STADIUM.glass_border == "rgba(255,255,255,0.08)"
    assert Radius.CARD == 24
    # Shadow CARD encodes 0 10px 40px rgba(0,0,0,.4)
    blur, dy, base = Shadow.CARD
    assert (blur, dy) == (40, 10)
    assert base == "rgba(0,0,0,0.40)"


# ─────────────────────────── rgba() ───────────────────────────
def test_rgba_from_hex_with_alpha():
    assert rgba("#19E3B5", 0.35) == "rgba(25,227,181,0.35)"


def test_rgba_passthrough_keeps_value():
    assert rgba("rgba(255,255,255,0.05)") == "rgba(255,255,255,0.05)"


def test_rgba_short_hex():
    assert rgba("#abc") == "rgba(170,187,204,1)"


def test_rgba_alpha_is_clamped():
    assert rgba("#000000", 5.0) == "rgba(0,0,0,1)"
    assert rgba("#000000", -2.0) == "rgba(0,0,0,0)"


@settings(max_examples=200)
@given(
    r=st.integers(min_value=0, max_value=255),
    g=st.integers(min_value=0, max_value=255),
    b=st.integers(min_value=0, max_value=255),
    a=st.floats(min_value=0.0, max_value=1.0),
)
def test_rgba_roundtrips_and_clamps(r, g, b, a):
    """rgba() output always re-parses to the same clamped components."""
    src = f"#{r:02X}{g:02X}{b:02X}"
    out = rgba(src, a)
    pr, pg, pb, pa = _parse_color(out)
    assert (pr, pg, pb) == (r, g, b)
    assert 0.0 <= pa <= 1.0
    assert abs(pa - round(a, 3)) <= 1e-6


# ─────────────────────────── mix() ───────────────────────────
def test_mix_endpoints_and_midpoint():
    assert mix("#000000", "#FFFFFF", 0.0) == "#000000"
    assert mix("#000000", "#FFFFFF", 1.0) == "#FFFFFF"
    assert mix("#000000", "#FFFFFF", 0.5) == "#808080"


def test_mix_clamps_t():
    assert mix("#000000", "#FFFFFF", -1.0) == "#000000"
    assert mix("#000000", "#FFFFFF", 2.0) == "#FFFFFF"


@settings(max_examples=200)
@given(t=st.floats(min_value=0.0, max_value=1.0))
def test_mix_output_is_valid_hex(t):
    out = mix("#06111A", "#0F2A1F", t)
    assert out.startswith("#") and len(out) == 7
    r, g, b, _ = _parse_color(out)
    for c in (r, g, b):
        assert 0 <= c <= 255


# ─────────────────────────── build_qss() ───────────────────────────
def test_build_qss_contains_ramp_and_glass():
    qss = build_qss(NIGHT_STADIUM)
    assert NIGHT_STADIUM.bg_top in qss
    assert NIGHT_STADIUM.bg_mid in qss
    assert NIGHT_STADIUM.bg_bottom in qss
    assert "GlassCard" in qss
    assert "border-radius: 24px" in qss
