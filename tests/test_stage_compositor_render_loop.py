"""Tests for the Stage Compositor per-frame render loop / ~60 FPS throttle.

Task 2.4 — `on_frame(t, dt)` accumulates `dt` and throttles ambient redraws to
~60 FPS; the accumulated real `dt` is forwarded to `_advance` so time-driven
motion stays time-accurate (no time lost), and `paintGL` uploads exactly the
four per-frame uniforms and draws one full-screen triangle.

The throttle logic lives in ``_CompositorMixin._on_frame`` and depends only on
plain attributes (``_bg_accum``, ``_t``) plus ``_advance`` / ``update`` hooks,
so it can be exercised headless via a tiny stub — no Qt widget, QApplication,
or FrameClock required.

Validates: Requirements 25.1, 25.2
Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest

from app.ui.widgets import stage_compositor as sc

_BG_MIN_DT = sc._BG_MIN_DT  # 1/60 s


class _ClockStub:
    """Minimal stand-in exposing the attributes ``_on_frame`` touches.

    Records every accumulated ``step`` handed to ``_advance`` and counts
    ``update()`` (i.e. ambient-redraw) requests so we can assert throttle
    behaviour precisely.
    """

    def __init__(self) -> None:
        self._bg_accum = 0.0
        self._t = 0.0
        self.updates = 0
        self.advanced_steps: list[float] = []

    def _advance(self, step_dt: float) -> None:
        self.advanced_steps.append(step_dt)

    def update(self) -> None:
        self.updates += 1

    # Borrow the real throttle implementation under test.
    _on_frame = sc._CompositorMixin._on_frame

    # Convenience: drive a whole sequence of (dt) ticks at a fixed rate.
    def drive(self, dts) -> None:
        t = 0.0
        for dt in dts:
            t += dt
            self._on_frame(t, dt)


# ════════════════════════════════════════════════════════════════════
#  Req 25.2 — throttle ambient redraws to ~60 FPS
# ════════════════════════════════════════════════════════════════════
def test_sub_60fps_ticks_coalesce_into_one_update():
    """Four 240 Hz ticks (each < 1/60 s) coalesce into a single redraw."""
    stub = _ClockStub()
    dt = 1.0 / 240.0
    # First three ticks accumulate below the 1/60 threshold → no redraw.
    for _ in range(3):
        stub._on_frame(stub._t + dt, dt)
    assert stub.updates == 0
    assert stub.advanced_steps == []
    # Fourth tick crosses 1/60 → exactly one coalesced redraw.
    stub._on_frame(stub._t + dt, dt)
    assert stub.updates == 1
    assert len(stub.advanced_steps) == 1
    # The accumulated real dt (~4 * 1/240 == 1/60) is forwarded to _advance.
    assert stub.advanced_steps[0] == pytest.approx(4.0 * dt)


def test_high_rate_clock_throttled_to_about_60fps():
    """A 240 Hz clock over 1 real second yields ~60 ambient redraws."""
    stub = _ClockStub()
    dt = 1.0 / 240.0
    stub.drive([dt] * 240)          # exactly 1.0 s of ticks
    # 240 Hz throttled to ~60 FPS → about 60 redraws (allow ±1 boundary slack).
    assert 59 <= stub.updates <= 61
    # No real time is lost: flushed time + residual == elapsed time.
    flushed = sum(stub.advanced_steps)
    assert flushed + stub._bg_accum == pytest.approx(240 * dt)


# ════════════════════════════════════════════════════════════════════
#  Task 2.4 #4 — a single large dt (> 1/60) must still trigger an update
# ════════════════════════════════════════════════════════════════════
def test_single_large_dt_triggers_immediate_update():
    """A lone tick whose dt already exceeds 1/60 s redraws right away."""
    stub = _ClockStub()
    big = 0.05  # FrameClock's _MAX_DT clamp; well above 1/60
    stub._on_frame(big, big)
    assert stub.updates == 1
    assert stub.advanced_steps == [pytest.approx(big)]
    # Accumulator fully reset after the flush.
    assert stub._bg_accum == 0.0


def test_exact_threshold_triggers_update():
    """dt == 1/60 is not `< 1/60`, so it must flush (boundary correctness)."""
    stub = _ClockStub()
    stub._on_frame(_BG_MIN_DT, _BG_MIN_DT)
    assert stub.updates == 1
    assert stub.advanced_steps[0] == pytest.approx(_BG_MIN_DT)


# ════════════════════════════════════════════════════════════════════
#  Task 2.4 #4 — accumulated time is never lost across flushes
# ════════════════════════════════════════════════════════════════════
def test_residual_below_threshold_is_retained_not_dropped():
    """Time left over after a flush stays in the accumulator for next time."""
    stub = _ClockStub()
    # Two 0.01 s ticks → 0.02 s > 1/60 → one flush of 0.02 s, residual 0.
    stub._on_frame(0.01, 0.01)
    assert stub.updates == 0
    stub._on_frame(0.02, 0.01)
    assert stub.updates == 1
    assert stub.advanced_steps[0] == pytest.approx(0.02)
    # A further small tick is held (not advanced) until the threshold is met.
    stub._on_frame(0.025, 0.005)
    assert stub.updates == 1                       # still throttled
    assert stub._bg_accum == pytest.approx(0.005)  # retained, not dropped


def test_total_advanced_time_equals_elapsed_time_no_loss():
    """Across an irregular dt sequence, flushed + residual == elapsed."""
    stub = _ClockStub()
    dts = [0.004, 0.004, 0.004, 0.004, 0.004,   # five small ticks
           0.05,                                 # one big tick
           0.008, 0.008, 0.001]                  # trailing partial frame
    stub.drive(dts)
    flushed = sum(stub.advanced_steps)
    assert flushed + stub._bg_accum == pytest.approx(sum(dts))
    # Every value handed to _advance is itself >= the throttle threshold.
    for step in stub.advanced_steps:
        assert step >= _BG_MIN_DT - 1e-12


def test_negative_or_zero_dt_does_not_redraw():
    """Non-positive dt accumulates harmlessly without spurious redraws."""
    stub = _ClockStub()
    stub._on_frame(0.0, 0.0)
    assert stub.updates == 0
    assert stub._bg_accum == 0.0


# ════════════════════════════════════════════════════════════════════
#  Req 25.1 — subscribe-on-show / unsubscribe-on-hide gating
# ════════════════════════════════════════════════════════════════════
def test_should_run_gating_matches_observable_flags():
    """_should_run reflects enabled ∧ want_anim ∧ visible ∧ ¬LOW_PERF."""
    class _GateStub:
        _enabled = True
        _want_anim = True
        _visible = True

        def isVisible(self):
            return self._visible

        _should_run = sc._CompositorMixin._should_run

    g = _GateStub()
    # All gates open (LOW_PERF is False in the test config) → should run.
    assert sc.LOW_PERF is False
    assert g._should_run() is True
    for attr in ("_enabled", "_want_anim", "_visible"):
        setattr(g, attr, False)
        assert g._should_run() is False, f"{attr}=False must stop the clock"
        setattr(g, attr, True)
    assert g._should_run() is True
