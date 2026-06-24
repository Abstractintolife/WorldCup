"""Property test for frame-rate independence (Task 3.5).

This module hosts a single, focused property — **Property 21: Frame-rate
independence** — kept in its own file so it does not collide with the sweep
periodicity property (Task 3.4) that lives in ``test_particles_sweep.py``.

All tests here are **pure-logic** and run headless (no Qt / no GL context):
they exercise the CPU ``ParticleEngine.step_particles`` advancement (frame-scale
``dt * REF_FPS`` with a linear + modulo-wrap integrator) and the pure
``sweep_positions`` function, both of which are the single source of truth that
the GPU shader mirrors.

Property 21 (design.md):
    For all frame rates supported by FrameClock (30–240 Hz), time-driven motion
    (particles, sweep, breathing) advances at the same real-time speed.

Operationalised here: advancing by the *same total elapsed real time* must
reach the *same state*, regardless of how that elapsed time is subdivided into
per-frame ``dt`` steps (i.e. regardless of the frame rate, which dictates the
``dt`` size: ``dt ≈ 1/rate`` for rate ∈ [30, 240] Hz).

Tolerance note — the integrator is ``y_{n+1} = (y_n - speed*dt*REF_FPS/h) % 1``.
Under *exact* real arithmetic the modulo-wrap accumulation is associative, so a
single big step and a many-small-step subdivision are identical. Under IEEE-754
float arithmetic, summing thousands of tiny ``dt`` values (up to ~120 s / (1/240
s) ≈ 28.8k steps) introduces rounding that accumulates to roughly 1e-12..1e-11.
We therefore assert *closeness* with ``abs_tol = 1e-6`` (comfortably above the
worst-case accumulated float error yet far tighter than any visible motion),
and we compare ``y`` / ``phase`` on the **circle** (mod 1.0) so a value of
0.9999999 and 0.0000001 — which are adjacent across the wrap boundary — are
correctly treated as close rather than ~1.0 apart.

Each property runs >= 100 Hypothesis iterations.

Feature: worldcup-ultimate-redesign, Property 21: Frame-rate independence
"""
from __future__ import annotations

import random

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.design.frame_clock import REF_FPS
from app.ui.widgets import stage_compositor as sc

# Chosen comparison tolerance for the modulo-wrap float-summation drift.
# See module docstring for the justification (worst case ~1e-11 << 1e-6).
_ABS_TOL = 1e-6

# Supported frame-rate band per Requirement 25.3 / design Property 21.
_RATE_MIN_HZ, _RATE_MAX_HZ = 30.0, 240.0


def _circular_close(a: float, b: float, abs_tol: float = _ABS_TOL) -> bool:
    """True if ``a`` and ``b`` are within ``abs_tol`` on the unit circle (mod 1).

    ``y`` and ``phase`` are wrapped into ``[0, 1)`` by the integrator, so values
    straddling the 0/1 seam (e.g. 0.999999 vs 1e-7) are genuinely adjacent.
    """
    d = abs(a - b) % 1.0
    return min(d, 1.0 - d) <= abs_tol


# A randomized sequence of frame rates (Hz) within the supported band. Each rate
# yields a per-frame dt = 1/rate, modelling a stream of frames at 30–240 Hz
# (mixed rates within one run model a variable refresh / jittery clock).
_rates = st.lists(
    st.floats(
        min_value=_RATE_MIN_HZ, max_value=_RATE_MAX_HZ,
        allow_nan=False, allow_infinity=False,
    ),
    min_size=1, max_size=400,
)


# ════════════════════════════════════════════════════════════════════
#  Property 21: Frame-rate independence
#  Feature: worldcup-ultimate-redesign, Property 21: Frame-rate independence —
#  for random dt sequences summing to the same elapsed real time at rates
#  between 30 Hz and 240 Hz, particle/sweep advancement reaches the same state.
#  Validates: Requirements 25.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200, deadline=None)
@given(rates=_rates, seed=st.integers(min_value=0, max_value=1_000_000))
def test_property21_frame_rate_independence_particles(rates, seed):
    """Same total elapsed time → same particle state, independent of dt split.

    Engine A advances with ONE big ``step_particles(T)``; engine B advances with
    the full per-frame ``dt = 1/rate`` sequence (rates ∈ [30,240] Hz) that sums
    to the same ``T``. Both engines share the same seed/count, so they start
    identical and must end identical (within ``_ABS_TOL`` on the wrap circle).
    """
    dts = [1.0 / r for r in rates]
    total = sum(dts)

    # A: single big step over the whole elapsed time.
    big = sc.ParticleEngine(seed=seed)
    big.step_particles(total)

    # B: many small per-frame steps at 30–240 Hz summing to the same total.
    framed = sc.ParticleEngine(seed=seed)
    for dt in dts:
        framed.step_particles(dt)

    assert len(big.particles) == len(framed.particles)
    for pa, pb in zip(big.particles, framed.particles):
        assert _circular_close(pa.y, pb.y), (
            f"y diverged beyond {_ABS_TOL}: big={pa.y!r} framed={pb.y!r} (T={total})"
        )
        assert _circular_close(pa.phase, pb.phase), (
            f"phase diverged beyond {_ABS_TOL}: big={pa.phase!r} framed={pb.phase!r} (T={total})"
        )


@settings(max_examples=150, deadline=None)
@given(
    total=st.floats(min_value=0.0, max_value=120.0, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=1_000_000),
    rng_seed=st.integers(min_value=0, max_value=1_000_000),
)
def test_property21_frame_rate_independence_random_subdivision(total, seed, rng_seed):
    """Same total elapsed time → same state for a *random* 30–240 Hz dt split.

    Complements the rate-list variant: here we fix the total elapsed time ``T``
    and chop it into random ``dt`` values drawn from ``[1/240, 1/30]`` s (i.e.
    instantaneous rates in 30–240 Hz), with the final partial frame clamped so
    the subdivision sums *exactly* to ``T``. A single ``step_particles(T)`` must
    reach the same state as the random subdivision.
    """
    ref = sc.ParticleEngine(seed=seed)
    ref.step_particles(total)

    sub = sc.ParticleEngine(seed=seed)
    rng = random.Random(rng_seed)
    lo, hi = 1.0 / _RATE_MAX_HZ, 1.0 / _RATE_MIN_HZ  # dt for 240 Hz .. 30 Hz
    remaining = total
    while remaining > 1e-12:
        dt = min(remaining, rng.uniform(lo, hi))
        sub.step_particles(dt)
        remaining -= dt

    for pr, ps in zip(ref.particles, sub.particles):
        assert _circular_close(pr.y, ps.y), (
            f"y diverged beyond {_ABS_TOL}: ref={pr.y!r} sub={ps.y!r} (T={total})"
        )
        assert _circular_close(pr.phase, ps.phase), (
            f"phase diverged beyond {_ABS_TOL}: ref={pr.phase!r} sub={ps.phase!r} (T={total})"
        )


@settings(max_examples=200, deadline=None)
@given(rates=_rates)
def test_property21_frame_rate_independence_sweep(rates):
    """Sweep position depends only on total elapsed ``t``, not the dt split.

    ``sweep_positions(t)`` is a pure function of absolute time, so accumulating
    the elapsed time as a sum of per-frame ``dt = 1/rate`` steps must land on the
    same beam centres as evaluating it at the total elapsed time directly. This
    is the sweep half of frame-rate independence (Requirement 25.3 / 18.3).
    """
    dts = [1.0 / r for r in rates]

    # Accumulate elapsed time one frame at a time (as the Frame Clock would).
    t_acc = 0.0
    for dt in dts:
        t_acc += dt

    total = sum(dts)
    x1_acc, x2_acc = sc.sweep_positions(t_acc)
    x1_tot, x2_tot = sc.sweep_positions(total)

    # Same scalar t → identical result (pure function); the only possible delta
    # is the float-summation difference between t_acc and total, which is tiny.
    assert _circular_close(x1_acc, x1_tot)
    assert _circular_close(x2_acc, x2_tot)
