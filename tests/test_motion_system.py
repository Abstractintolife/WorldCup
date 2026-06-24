"""Property + unit tests for the unified Motion System.

Covers:
* Task 1.4 — Property 1: Motion easing is uniform (Requirement 19.1)
* Task 1.5 — Property 2: Animation duration ceiling (Requirement 19.2)
* Task 1.7 — Property 3: Hover lift magnitude (Requirements 19.4, 20.3)

Pure-logic properties (``clamp_duration``, ``hover_lift_target_y``) run
everywhere. Qt-object properties additionally exercise ``std_anim`` /
``hover_lift`` and are skipped when Qt cannot be initialised headless.
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.design import motion_system as m
from tests.conftest import QT_AVAILABLE


# ════════════════════════════════════════════════════════════════════
#  Property 2 — Animation duration ceiling (pure)
#  Feature: worldcup-ultimate-redesign, Property 2: Animation duration
#  ceiling — for any requested duration, the effective duration is <= 500ms.
#  Validates: Requirements 19.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(d=st.integers(min_value=-10_000, max_value=10_000))
def test_clamp_duration_never_exceeds_ceiling(d):
    out = m.clamp_duration(d)
    assert 0 <= out <= m.DUR_MAX == 500


def test_clamp_duration_examples():
    assert m.clamp_duration(180) == 180
    assert m.clamp_duration(9999) == 500
    assert m.clamp_duration(-5) == 0


# ════════════════════════════════════════════════════════════════════
#  Property 3 — Hover lift magnitude (pure target math)
#  Feature: worldcup-ultimate-redesign, Property 3: Hover lift magnitude —
#  entering hover targets restY - 6 and leaving returns exactly to restY.
#  Validates: Requirements 19.4, 20.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(rest_y=st.integers(min_value=-5000, max_value=5000))
def test_hover_lift_target_math(rest_y):
    assert m.hover_lift_target_y(rest_y, up=True) == rest_y - 6
    assert m.hover_lift_target_y(rest_y, up=False) == rest_y
    # leaving always returns exactly to rest
    up = m.hover_lift_target_y(rest_y, up=True)
    assert m.hover_lift_target_y(up, up=False) == up  # idempotent on rest input


def test_motion_tokens_constants():
    from PyQt6.QtCore import QEasingCurve

    assert m.DUR_STANDARD == 180
    assert m.DUR_MAX == 500
    assert m.HOVER_LIFT_DY == -6
    assert m.EASE_STANDARD == QEasingCurve.Type.OutCubic


# ════════════════════════════════════════════════════════════════════
#  Qt-backed properties (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(
    duration=st.integers(min_value=-2000, max_value=5000),
    start=st.integers(min_value=-500, max_value=500),
    end=st.integers(min_value=-500, max_value=500),
)
def test_std_anim_easing_is_always_outcubic(qapp, duration, start, end):
    """Property 1: every animation from the motion system uses OutCubic.

    Feature: worldcup-ultimate-redesign, Property 1: Motion easing is uniform.
    Validates: Requirements 19.1
    """
    from PyQt6.QtCore import QEasingCurve, QObject

    target = QObject()
    anim = m.std_anim(target, b"objectName", start, end, duration=duration)
    assert anim.easingCurve().type() == QEasingCurve.Type.OutCubic


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(duration=st.integers(min_value=-2000, max_value=20_000))
def test_std_anim_duration_ceiling(qapp, duration):
    """Property 2: created animation's effective duration <= 500ms.

    Feature: worldcup-ultimate-redesign, Property 2: Animation duration ceiling.
    Validates: Requirements 19.2
    """
    from PyQt6.QtCore import QObject

    target = QObject()
    anim = m.std_anim(target, b"objectName", 0, 1, duration=duration)
    assert anim.duration() <= 500


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(
    x=st.integers(min_value=-300, max_value=300),
    y=st.integers(min_value=-300, max_value=300),
)
def test_hover_lift_widget_targets(qapp, x, y):
    """Property 3 (GUI): hover_lift targets restY-6 up, restY exactly down.

    Feature: worldcup-ultimate-redesign, Property 3: Hover lift magnitude.
    Validates: Requirements 19.4, 20.3
    """
    from PyQt6.QtCore import QPoint
    from PyQt6.QtWidgets import QWidget

    w = QWidget()
    w.move(QPoint(x, y))

    up_anim = m.hover_lift(w, up=True)
    assert up_anim.endValue() == QPoint(x, y - 6)

    down_anim = m.hover_lift(w, up=False)
    assert down_anim.endValue() == QPoint(x, y)
