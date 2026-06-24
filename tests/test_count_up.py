"""Property + unit tests for CountUpNumber (Task 5.1 / 5.2).

Covers Task 5.2 — Property 11: Count-up reaches exact target.

The value-math (``count_up_value`` / ``count_up_display``) is pure and runs
headless. A Qt-backed test additionally exercises the ``CountUpNumber`` widget
and is skipped when Qt cannot be initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets.fx import count_up as cu
from tests.conftest import QT_AVAILABLE

_EPS = 1e-9


# ════════════════════════════════════════════════════════════════════
#  Property 11: Count-up reaches exact target
#  Feature: worldcup-ultimate-redesign, Property 11: Count-up reaches exact
#  target — for any non-negative target, the final rendered value equals the
#  target exactly and intermediate values are non-decreasing.
#  Validates: Requirements 21.2, 21.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(
    target=st.floats(min_value=0.0, max_value=1_000_000.0,
                     allow_nan=False, allow_infinity=False),
    steps=st.integers(min_value=2, max_value=64),
)
def test_property11_exact_settle_and_non_decreasing(target, steps):
    # 等分的单调递增进度序列 0 → 1。
    progresses = [i / (steps - 1) for i in range(steps)]
    vals = [cu.count_up_value(target, p) for p in progresses]

    # (21.3) 朝非负 target 增长，中间值非递减。
    for a, b in zip(vals, vals[1:]):
        assert b >= a - _EPS

    # (21.2) 终值精确等于 target。
    assert cu.count_up_value(target, 1.0) == target
    assert vals[-1] == target


@settings(max_examples=200)
@given(
    target=st.integers(min_value=0, max_value=1_000_000),
    steps=st.integers(min_value=2, max_value=48),
)
def test_property11_display_integer_non_decreasing_and_exact(target, steps):
    progresses = [i / (steps - 1) for i in range(steps)]
    shown = [cu.count_up_display(target, p, decimals=0) for p in progresses]
    for a, b in zip(shown, shown[1:]):
        assert b >= a
    # 终点精确命中整数 target。
    assert cu.count_up_display(target, 1.0, decimals=0) == float(target)


def test_eased_out_cubic_endpoints_and_monotonic():
    assert cu.ease_out_cubic(0.0) == 0.0
    assert cu.ease_out_cubic(1.0) == 1.0
    xs = [i / 50 for i in range(51)]
    ys = [cu.ease_out_cubic(x) for x in xs]
    for a, b in zip(ys, ys[1:]):
        assert b >= a


def test_count_up_constants():
    from PyQt6.QtCore import QEasingCurve

    assert cu.DURATION_MS == 800
    assert cu.EASE == QEasingCurve.Type.OutCubic


# ════════════════════════════════════════════════════════════════════
#  Qt-backed widget test (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt unavailable")
def test_count_up_widget_settles_exactly(qapp):
    w = cu.CountUpNumber(decimals=0)
    w.set_target(141)
    # 直接调用终帧回调，验证落定文本精确等于 target。
    w._on_finished()
    assert w.text() == "141"
    assert w.target == 141.0
