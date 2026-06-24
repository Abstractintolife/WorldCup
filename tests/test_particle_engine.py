"""Property tests for the World Cup Particle Engine bounds (Task 3.2).

These are **pure-logic** property tests (no Qt / no GL context): they exercise
the CPU ``ParticleEngine`` that backs the night-stadium particle field, the
single source of truth for particle count / speed / opacity invariants shared
with the GPU shader.

Each property uses Hypothesis with >= 100 examples and, crucially, drives the
engine through **randomized construction** (count incl. ``None``, negatives,
zero, and huge values) followed by **arbitrary sequences of**
``step_particles(dt)`` (dt incl. 0, negative, and large values), asserting the
design bounds hold for *any reachable compositor/engine state*.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import stage_compositor as sc

# Tiny tolerance to absorb float rounding when comparing against band edges.
_EPS = 1e-9

# ── Shared strategies ────────────────────────────────────────────────
# Requested particle count: None (use perf-derived default) plus a wide range
# of integers including negatives, zero, and absurdly large values. The engine
# must clamp every one of these into the [80,120] design band.
_count = st.one_of(
    st.none(),
    st.integers(min_value=-10_000, max_value=1_000_000),
)
_seed = st.integers(min_value=0, max_value=1_000_000)

# dt values fed to step_particles: includes negative, zero, sub-frame, normal,
# and very large steps. Negative / zero must be treated as no-op; large steps
# must still wrap (mod 1.0) and never push derived bounds out of range.
_dt = st.floats(
    min_value=-10.0, max_value=10_000.0,
    allow_nan=False, allow_infinity=False,
)
_dt_sequence = st.lists(_dt, min_size=0, max_size=25)


def _build_and_step(count, seed, dts):
    """Construct an engine for ``count``/``seed`` then apply the dt sequence."""
    eng = sc.ParticleEngine(count, seed=seed)
    for dt in dts:
        eng.step_particles(dt)
    return eng


# ════════════════════════════════════════════════════════════════════
#  Property 4: Particle count bound
#  Feature: worldcup-ultimate-redesign, Property 4: Particle count bound —
#  for any compositor state, active particle count ∈ [80,120].
#  Validates: Requirements 17.1
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200, deadline=None)
@given(count=_count, seed=_seed, dts=_dt_sequence)
def test_property4_particle_count_bound(count, seed, dts):
    eng = _build_and_step(count, seed, dts)
    n = eng.active_count()
    assert sc.PARTICLE_COUNT_MIN <= n <= sc.PARTICLE_COUNT_MAX
    # active_count() must always agree with the actual particle list length,
    # and stepping must never create or destroy particles.
    assert n == len(eng.particles)


# ════════════════════════════════════════════════════════════════════
#  Property 5: Particle speed bound
#  Feature: worldcup-ultimate-redesign, Property 5: Particle speed bound —
#  for any particle, per-frame speed ∈ [0.1,0.3] px/frame at the reference
#  frame rate.
#  Validates: Requirements 17.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200, deadline=None)
@given(count=_count, seed=_seed, dts=_dt_sequence)
def test_property5_particle_speed_bound(count, seed, dts):
    eng = _build_and_step(count, seed, dts)
    for p in eng.particles:
        assert sc.PARTICLE_SPEED_MIN - _EPS <= p.speed <= sc.PARTICLE_SPEED_MAX + _EPS
        # Every live particle must round-trip through the validated ParticleSpec
        # (construction raises if any band — count/kind/speed/opacity — is violated).
        spec = eng.spec_for(p)
        assert spec.kind in sc.PARTICLE_KINDS


# ════════════════════════════════════════════════════════════════════
#  Property 6: Particle opacity bound
#  Feature: worldcup-ultimate-redesign, Property 6: Particle opacity bound —
#  for any particle, rendered opacity ∈ [0.05,0.15].
#  Validates: Requirements 17.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200, deadline=None)
@given(count=_count, seed=_seed, dts=_dt_sequence)
def test_property6_particle_opacity_bound(count, seed, dts):
    eng = _build_and_step(count, seed, dts)
    for p in eng.particles:
        assert sc.PARTICLE_OPACITY_MIN - _EPS <= p.opacity <= sc.PARTICLE_OPACITY_MAX + _EPS
        # kind is restricted to dust/grass/glint — petals/sakura/snow/meteors
        # are explicitly banned (Requirements 17.4 / 17.5).
        assert p.kind in sc.PARTICLE_KINDS
        assert p.kind not in sc.BANNED_PARTICLE_KINDS
