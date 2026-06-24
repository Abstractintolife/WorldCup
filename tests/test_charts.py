"""Property + unit tests for the animated Chart System (Task 5.6 / 5.7).

Covers Task 5.7 — Property 20: Chart reveal settles at data.

The reveal/geometry value-math (``eased_reveal``, ``reveal_values`` and the
per-chart geometry helpers) is pure and runs headless.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import math

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets.charts import base as cb
from app.ui.widgets.charts import bar as cbar
from app.ui.widgets.charts import line as cline
from app.ui.widgets.charts import radar as cradar

_EPS = 1e-9

_values = st.lists(
    st.floats(min_value=0.0, max_value=10_000.0, allow_nan=False, allow_infinity=False),
    min_size=1, max_size=12,
)
_reveals = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


# ════════════════════════════════════════════════════════════════════
#  Property 20: Chart reveal settles at data
#  Feature: worldcup-ultimate-redesign, Property 20: Chart reveal settles at
#  data — for any dataset, reveal progress is monotonic 0→1 and settled
#  geometry equals the input values.
#  Validates: Requirements 24.1, 24.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(p=st.floats(min_value=0.0, max_value=1.0))
def test_property20_reveal_progress_monotonic_0_to_1(p):
    # 端点：eased(0)=0, eased(1)=1。
    assert cb.eased_reveal(0.0) == 0.0
    assert cb.eased_reveal(1.0) == 1.0
    # 单调非减：eased(p) <= eased(min(p+δ,1))。
    q = min(1.0, p + 0.05)
    assert cb.eased_reveal(q) >= cb.eased_reveal(p) - _EPS


@settings(max_examples=300)
@given(values=_values, r1=_reveals, r2=_reveals)
def test_property20_reveal_values_monotonic_and_settle(values, r1, r2):
    lo, hi = sorted((r1, r2))
    a = cb.reveal_values(values, lo)
    b = cb.reveal_values(values, hi)
    # 非负值：揭示比例增大 → 逐元素几何非递减（需求 24.1）。
    for av, bv in zip(a, b):
        assert bv >= av - _EPS
    # 落定 (reveal=1) 几何逐元素精确等于输入数据（需求 24.2）。
    settled = cb.reveal_values(values, 1.0)
    assert settled == [float(v) for v in values]


@settings(max_examples=200)
@given(values=_values)
def test_property20_radar_settles_at_fraction(values):
    max_value = max(values) + 1.0   # 保证 max_value > 0
    cx, cy, radius = 100.0, 100.0, 80.0
    verts = cradar.radar_vertices(values, max_value, 1.0, cx, cy, radius)
    # 落定时各顶点到圆心的半径 == radius · (value/max_value)。
    n = len(values)
    for i, (x, y) in enumerate(verts):
        r = math.hypot(x - cx, y - cy)
        expected = radius * cradar.radar_axis_fraction(values[i], max_value)
        assert math.isclose(r, expected, abs_tol=1e-6)
        # 角度按等分布置。
        _ = n


@settings(max_examples=200)
@given(values=_values)
def test_property20_bar_settles_at_data(values):
    max_value = max(values) + 1.0
    full_h = 120.0
    settled = cbar.bar_reveal_heights(values, max_value, full_h, 1.0)
    for v, h in zip(values, settled):
        assert math.isclose(h, full_h * (v / max_value), abs_tol=1e-6)


@settings(max_examples=200)
@given(values=_values, r1=_reveals, r2=_reveals)
def test_property20_bar_heights_monotonic_in_reveal(values, r1, r2):
    # 非负数据：揭示比例增大 → 每根柱高度非递减（需求 24.1）。
    max_value = max(values) + 1.0
    full_h = 120.0
    lo, hi = sorted((r1, r2))
    a = cbar.bar_reveal_heights(values, max_value, full_h, lo)
    b = cbar.bar_reveal_heights(values, max_value, full_h, hi)
    for av, bv in zip(a, b):
        assert bv >= av - _EPS


@settings(max_examples=200)
@given(values=_values, r1=_reveals, r2=_reveals)
def test_property20_radar_radii_monotonic_in_reveal(values, r1, r2):
    # 非负数据：揭示比例增大 → 每个顶点到圆心的半径非递减（需求 24.1）。
    max_value = max(values) + 1.0
    cx, cy, radius = 100.0, 100.0, 80.0
    lo, hi = sorted((r1, r2))
    va = cradar.radar_vertices(values, max_value, lo, cx, cy, radius)
    vb = cradar.radar_vertices(values, max_value, hi, cx, cy, radius)
    for (ax, ay), (bx, by) in zip(va, vb):
        ra = math.hypot(ax - cx, ay - cy)
        rb = math.hypot(bx - cx, by - cy)
        assert rb >= ra - 1e-6


@settings(max_examples=200)
@given(values=_values)
def test_property20_line_settles_at_all_points(values):
    # 用 (i, v) 作为折线顶点；落定时返回全部顶点且精确一致。
    pts = [(float(i), float(v)) for i, v in enumerate(values)]
    out = cline.line_reveal_points(pts, 1.0)
    assert out == pts


@settings(max_examples=200)
@given(values=st.lists(st.floats(0.0, 100.0, allow_nan=False, allow_infinity=False),
                       min_size=2, max_size=12),
       r1=_reveals, r2=_reveals)
def test_property20_line_reveal_coverage_monotonic(values, r1, r2):
    pts = [(float(i), float(v)) for i, v in enumerate(values)]
    lo, hi = sorted((r1, r2))
    a = cline.line_reveal_points(pts, lo)
    b = cline.line_reveal_points(pts, hi)
    # 揭示比例增大 → 可见折线覆盖范围（顶点数）不减。
    assert len(b) >= len(a)
    assert len(a) <= len(pts)
    assert len(b) <= len(pts)


def test_chart_constants():
    from PyQt6.QtCore import QEasingCurve

    assert cb.CHART_REFRESH_MS == 300
    assert cb.EASE == QEasingCurve.Type.OutCubic
