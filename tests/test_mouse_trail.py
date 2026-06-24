"""Property + unit tests for MouseTrailOverlay (Task 5.4 / 5.5).

Covers Task 5.5 — Property 17: Mouse trail bound & fade.

The ring-buffer update (``push_sample``) and opacity ramp (``trail_opacities``)
are pure and run headless.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets.fx import mouse_trail as mt

_point = st.tuples(st.integers(-5000, 5000), st.integers(-5000, 5000))


# ════════════════════════════════════════════════════════════════════
#  Property 17: Mouse trail bound & fade
#  Feature: worldcup-ultimate-redesign, Property 17: Mouse trail bound & fade
#  — for any cursor path, at most 5 dots are rendered and their opacities are
#  strictly decreasing from head to tail.
#  Validates: Requirements 23.1, 23.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(path=st.lists(_point, min_size=0, max_size=200))
def test_property17_buffer_never_exceeds_max(path):
    samples: list = []
    for pos in path:
        samples = mt.push_sample(samples, pos, mt.MAX_DOTS)
        # (23.1) 任意时刻缓冲长度 <= 5。
        assert len(samples) <= mt.MAX_DOTS
    # 最新采样始终在头部。
    if path:
        assert samples[0] == path[-1]


@settings(max_examples=200)
@given(count=st.integers(min_value=0, max_value=20))
def test_property17_opacities_strictly_decreasing(count):
    ops = mt.trail_opacities(count)
    # (23.1) 渲染点数恒 <= MAX_DOTS。
    assert len(ops) <= mt.MAX_DOTS
    # (23.2) 头→尾严格递减，且全部为正。
    for a, b in zip(ops, ops[1:]):
        assert b < a
    for o in ops:
        assert o > 0.0


def test_push_sample_does_not_mutate_input():
    original = [(1, 1), (2, 2)]
    snapshot = list(original)
    _ = mt.push_sample(original, (9, 9), mt.MAX_DOTS)
    assert original == snapshot


def test_trail_opacity_examples():
    ops = mt.trail_opacities(5, head=1.0)
    assert ops == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert mt.trail_opacities(0) == []
