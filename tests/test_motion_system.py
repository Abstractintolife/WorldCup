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

import os
import pathlib
import subprocess
import sys
import textwrap

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.design import motion_system as m
from tests.conftest import QT_AVAILABLE

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


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


# Property names exercised against std_anim. Easing is set independently of
# whether the property is animatable, so randomizing across these still
# faithfully exercises "any animation created via the motion system".
_ANIM_PROPS = [b"pos", b"geometry", b"size", b"windowOpacity", b"objectName"]


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(
    prop=st.sampled_from(_ANIM_PROPS),
    duration=st.integers(min_value=-2000, max_value=500),
    start=st.integers(min_value=-500, max_value=500),
    end=st.integers(min_value=-500, max_value=500),
)
def test_std_anim_easing_is_always_outcubic(qapp, prop, duration, start, end):
    """Property 1: every animation from the motion system uses OutCubic.

    Feature: worldcup-ultimate-redesign, Property 1: Motion easing is uniform.

    For any animation created via ``std_anim`` (randomized target property,
    start/end values, and duration), the created ``QPropertyAnimation``'s
    easing curve type is ``OutCubic``.

    Validates: Requirements 19.1
    """
    from PyQt6.QtCore import QEasingCurve, QObject

    target = QObject()
    anim = m.std_anim(target, prop, start, end, duration=duration)
    assert anim.easingCurve().type() == QEasingCurve.Type.OutCubic


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(
    x=st.integers(min_value=-400, max_value=400),
    y=st.integers(min_value=-400, max_value=400),
    up=st.booleans(),
    duration=st.integers(min_value=0, max_value=500),
)
def test_hover_lift_easing_is_always_outcubic(qapp, x, y, up, duration):
    """Property 1 (hover gesture): hover_lift animations also use OutCubic.

    Feature: worldcup-ultimate-redesign, Property 1: Motion easing is uniform.

    ``hover_lift`` routes through ``std_anim``, so any hover animation it
    produces (entering or leaving, any position/duration) must also carry the
    uniform ``OutCubic`` easing curve.

    Validates: Requirements 19.1
    """
    from PyQt6.QtCore import QEasingCurve, QPoint
    from PyQt6.QtWidgets import QWidget

    w = QWidget()
    w.move(QPoint(x, y))

    anim = m.hover_lift(w, up=up, duration=duration)
    assert anim.easingCurve().type() == QEasingCurve.Type.OutCubic


@pytestmark_qt
@settings(max_examples=150, deadline=None)
@given(duration=st.integers(min_value=-5000, max_value=m.DUR_MAX))
def test_std_anim_duration_ceiling_in_range(qapp, duration):
    """Property 2: created animation's effective duration is in [0, 500] ms.

    Exercises ``std_anim`` directly across the in-bounds request domain
    (``duration <= DUR_MAX``, including negatives that must clamp up to 0).
    Requests above the ceiling are covered separately under release
    (``python -O``) semantics, because ``std_anim`` deliberately ``assert``s
    on > 500 ms requests in debug builds to surface violating callers.

    Feature: worldcup-ultimate-redesign, Property 2: Animation duration ceiling.
    Validates: Requirements 19.2
    """
    from PyQt6.QtCore import QObject

    target = QObject()
    anim = m.std_anim(target, b"objectName", 0, 1, duration=duration)
    eff = anim.duration()
    assert 0 <= eff <= m.DUR_MAX == 500
    assert eff == m.clamp_duration(duration)


# Release-build (``python -O``) Hypothesis property: with assertions stripped,
# ``std_anim`` must still clamp ANY requested duration — including values far
# above the ceiling and negatives — so the created animation's effective
# duration stays within [0, 500] ms. Runs in a subprocess so the -O semantics
# (``assert`` removed) apply to ``std_anim``. >= 100 iterations.
_RELEASE_CEILING_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from hypothesis import given, settings
    from hypothesis import strategies as st
    from PyQt6.QtCore import QObject
    from PyQt6.QtWidgets import QApplication

    from app.ui.design import motion_system as m

    # Sanity: confirm assertions are actually disabled (running under -O).
    assert __debug__ is False, "expected to run under python -O"

    _app = QApplication.instance() or QApplication([])

    @settings(max_examples=150, deadline=None)
    @given(duration=st.integers(min_value=-10_000, max_value=50_000))
    def test_release_clamp(duration):
        anim = m.std_anim(QObject(), b"objectName", 0, 1, duration=duration)
        eff = anim.duration()
        assert 0 <= eff <= 500, (duration, eff)
        assert eff == m.clamp_duration(duration), (duration, eff)

    test_release_clamp()
    print("RELEASE_CEILING_OK")
    """
)


@pytestmark_qt
def test_std_anim_duration_ceiling_release_mode_clamps_over_500():
    """Property 2 (release semantics): std_anim clamps over-ceiling requests.

    Under ``python -O`` the debug assert is stripped, so ``std_anim`` must rely
    on ``clamp_duration`` to keep the effective duration <= 500 ms for the FULL
    input domain (including durations > 500 and negatives). This closes the gap
    left by the in-range test above, fully validating the property end-to-end.

    Feature: worldcup-ultimate-redesign, Property 2: Animation duration ceiling.
    Validates: Requirements 19.2
    """
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = os.pathsep.join(
        [str(_PROJECT_ROOT), env.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [sys.executable, "-O", "-c", _RELEASE_CEILING_SCRIPT],
        cwd=str(_PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"release-mode ceiling property failed\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "RELEASE_CEILING_OK" in result.stdout, result.stdout


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


@pytestmark_qt
@settings(max_examples=100, deadline=None)
@given(
    x=st.integers(min_value=-300, max_value=300),
    rest_y=st.integers(min_value=-300, max_value=300),
)
def test_glass_card_hover_lift_through_events(qapp, x, rest_y):
    """Property 3 (GlassCard events): hovering a glass card lifts -6, leaving returns exactly.

    Drives the real ``GlassCard.enterEvent`` / ``leaveEvent`` handlers (the
    production hover path) for a card resting at a randomized ``(x, rest_y)``.
    Entering must target ``rest_y - 6`` and leaving must return exactly to
    ``rest_y``. The animation created by each handler is identified as the new
    ``QPropertyAnimation`` child of the card, and its ``endValue`` is asserted.

    Feature: worldcup-ultimate-redesign, Property 3: Hover lift magnitude.
    Validates: Requirements 19.4, 20.3
    """
    from PyQt6.QtCore import QEvent, QPoint, QPointF, QPropertyAnimation
    from PyQt6.QtGui import QEnterEvent

    from app.ui.widgets.glass_card import GlassCard

    card = GlassCard()
    card.move(QPoint(x, rest_y))

    before = set(card.findChildren(QPropertyAnimation))

    # Enter hover: card lifts to rest_y - 6.
    pos_f = QPointF(float(x), float(rest_y))
    card.enterEvent(QEnterEvent(QPointF(0.0, 0.0), QPointF(0.0, 0.0), pos_f))
    after_enter = set(card.findChildren(QPropertyAnimation))
    enter_new = after_enter - before
    assert len(enter_new) == 1, "enterEvent must create exactly one hover animation"
    enter_anim = enter_new.pop()
    assert enter_anim.endValue() == QPoint(x, rest_y - 6)

    # Leave hover: card returns exactly to rest_y.
    card.leaveEvent(QEvent(QEvent.Type.Leave))
    after_leave = set(card.findChildren(QPropertyAnimation))
    leave_new = after_leave - after_enter
    assert len(leave_new) == 1, "leaveEvent must create exactly one return animation"
    leave_anim = leave_new.pop()
    assert leave_anim.endValue() == QPoint(x, rest_y)
