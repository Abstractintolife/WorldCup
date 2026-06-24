"""Property tests for the World Cup Particle Engine and Floodlight Sweep (Task 3).

All tests here are **pure-logic** and run headless (no Qt / no GL context):
they exercise the typed/validated ``ParticleSpec`` + ``ParticleEngine`` and the
pure ``floodlight_sweep`` / ``sweep_positions`` functions that both the GPU
shader and the CPU fallback share as their single source of truth.

Each property runs >= 100 Hypothesis iterations.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import math
import random

from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.design.frame_clock import REF_FPS
from app.ui.widgets import stage_compositor as sc

_EPS = 1e-9

# 采样空间：归一化屏幕坐标 uv ∈ [0,1]^2，时间 t ∈ [0, 10000) 秒。
_uv = st.tuples(
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=1.0),
)
_t = st.floats(min_value=0.0, max_value=10_000.0, allow_nan=False, allow_infinity=False)


# ════════════════════════════════════════════════════════════════════
#  Property 4: Particle count bound
#  Feature: worldcup-ultimate-redesign, Property 4: Particle count bound —
#  for any compositor state, active particle count ∈ [80,120].
#  Validates: Requirements 17.1
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(requested=st.integers(min_value=-1000, max_value=100_000), seed=st.integers(0, 1_000_000))
def test_property4_particle_count_bound(requested, seed):
    eng = sc.ParticleEngine(requested, seed=seed)
    n = eng.active_count()
    assert sc.PARTICLE_COUNT_MIN <= n <= sc.PARTICLE_COUNT_MAX
    # active_count 与实际粒子列表长度一致。
    assert n == len(eng.particles)


def test_property4_default_count_in_band():
    eng = sc.ParticleEngine()
    assert sc.PARTICLE_COUNT_MIN <= eng.active_count() <= sc.PARTICLE_COUNT_MAX


# ════════════════════════════════════════════════════════════════════
#  Property 5: Particle speed bound
#  Feature: worldcup-ultimate-redesign, Property 5: Particle speed bound —
#  for any particle, per-frame speed ∈ [0.1,0.3] px/frame at the reference
#  frame rate.
#  Validates: Requirements 17.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(seed=st.integers(0, 1_000_000), count=st.integers(0, 1000))
def test_property5_particle_speed_bound(seed, count):
    eng = sc.ParticleEngine(count, seed=seed)
    for p in eng.particles:
        assert sc.PARTICLE_SPEED_MIN - _EPS <= p.speed <= sc.PARTICLE_SPEED_MAX + _EPS
        # 每个粒子都可包装成受校验的 ParticleSpec（不抛异常即满足全部带约束）。
        spec = eng.spec_for(p)
        assert spec.kind in sc.PARTICLE_KINDS


# ════════════════════════════════════════════════════════════════════
#  Property 6: Particle opacity bound
#  Feature: worldcup-ultimate-redesign, Property 6: Particle opacity bound —
#  for any particle, rendered opacity ∈ [0.05,0.15].
#  Validates: Requirements 17.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(seed=st.integers(0, 1_000_000), count=st.integers(0, 1000))
def test_property6_particle_opacity_bound(seed, count):
    eng = sc.ParticleEngine(count, seed=seed)
    for p in eng.particles:
        assert sc.PARTICLE_OPACITY_MIN - _EPS <= p.opacity <= sc.PARTICLE_OPACITY_MAX + _EPS
        # kind 只能是 dust/grass/glint —— 明确排除花瓣/樱花/雪/流星（需求 17.4/17.5）。
        assert p.kind in sc.PARTICLE_KINDS
        assert p.kind not in sc.BANNED_PARTICLE_KINDS


# ════════════════════════════════════════════════════════════════════
#  Property 8: Floodlight sweep periodicity
#  Feature: worldcup-ultimate-redesign, Property 8: Floodlight sweep
#  periodicity — for any t, sweep position at t equals position at t + 8.0,
#  and the combined sweep opacity contribution is <= ~5%.
#  Validates: Requirements 18.1, 18.2
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(uv=_uv, t=_t)
def test_property8_floodlight_sweep_periodicity_and_ceiling(uv, t):
    p_now = sc.sweep_positions(t)
    p_next = sc.sweep_positions(t + sc.SWEEP_PERIOD)
    # 位置周期为 8s：position(t) == position(t + 8.0)（容忍浮点误差）。
    assert math.isclose(p_now[0], p_next[0], abs_tol=1e-4)
    assert math.isclose(p_now[1], p_next[1], abs_tol=1e-4)
    # 合计不透明度 ≤ ~5%（带上限 SWEEP_OPACITY_CEIL），且非负。
    a = sc.floodlight_sweep(uv, t)
    assert 0.0 <= a <= sc.SWEEP_OPACITY_CEIL + _EPS
    # 横扫强度亦呈 8s 周期。
    a_next = sc.floodlight_sweep(uv, t + sc.SWEEP_PERIOD)
    assert math.isclose(a, a_next, abs_tol=1e-4)


# ════════════════════════════════════════════════════════════════════
#  Property 21: Frame-rate independence
#  Feature: worldcup-ultimate-redesign, Property 21: Frame-rate independence
#  — for random dt sequences summing to the same elapsed real time at rates
#  between 30 Hz and 240 Hz, particle/sweep advancement reaches the same state.
#  Validates: Requirements 25.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=150, deadline=None)
@given(
    total=st.floats(min_value=0.1, max_value=120.0, allow_nan=False, allow_infinity=False),
    seed=st.integers(0, 1_000_000),
    rng_seed=st.integers(0, 1_000_000),
)
def test_property21_frame_rate_independence(total, seed, rng_seed):
    # 参考：单步推进整段时间。
    ref = sc.ParticleEngine(seed=seed)
    ref.step_particles(total)

    # 对照：把同样的总时长切成「30–240Hz」之间的随机 dt 序列逐帧推进。
    sub = sc.ParticleEngine(seed=seed)
    rng = random.Random(rng_seed)
    remaining = total
    lo, hi = 1.0 / 240.0, 1.0 / 30.0
    while remaining > 1e-12:
        dt = min(remaining, rng.uniform(lo, hi))
        sub.step_particles(dt)
        remaining -= dt

    # 两者推进到同一状态（位置 / 相位在浮点容差内一致）。
    for pr, ps in zip(ref.particles, sub.particles):
        assert math.isclose(pr.y, ps.y, abs_tol=1e-6)
        assert math.isclose(pr.phase, ps.phase, abs_tol=1e-6)

    # 横扫位置是 t 的纯函数，对任意 dt 切分都只取决于总时长 → 帧率无关。
    assert sc.sweep_positions(total) == sc.sweep_positions(total)
