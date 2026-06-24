"""Tests for the Stage Compositor (Task 2).

Pure-logic property tests for the five-layer night-stadium backdrop run
headless and unconditionally (no Qt needed): they exercise the pure
``composite_ambient`` / ``ambient_contributions`` logic.

The backend API-equivalence integration test (Property 22) instantiates Qt
widgets and is skipped automatically when Qt cannot initialise headless, but
the GPU-failure→CPU fallback path is verified without a GL context.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets import stage_compositor as sc
from tests.conftest import QT_AVAILABLE

# ── 采样空间：归一化屏幕坐标 uv ∈ [0,1]^2，时间 t ∈ [0, 10000) 秒 ──
_uv = st.tuples(
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=1.0),
)
_t = st.floats(min_value=0.0, max_value=10_000.0, allow_nan=False, allow_infinity=False)

_EPS = 1e-9


# ════════════════════════════════════════════════════════════════════
#  Property 7: Ambient layer opacity bands
#  Feature: worldcup-ultimate-redesign, Property 7: Ambient layer opacity
#  bands — each ambient layer's contribution stays within its band
#  (floodlights ~8%, grass 3-5%, pitch ~2%, trophy ~2%).
#  Validates: Requirements 16.3
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(uv=_uv, t=_t)
def test_property7_ambient_layer_opacity_bands(uv, t):
    c = sc.ambient_contributions(uv, t)
    # 每层贡献都非负，且不超过其透明度带上限。
    assert 0.0 <= c["floodlight"] <= sc.FLOODLIGHT_OPACITY + _EPS
    assert 0.0 <= c["grass"] <= sc.GRASS_OPACITY + _EPS
    assert 0.0 <= c["pitch"] <= sc.PITCH_OPACITY + _EPS
    assert 0.0 <= c["trophy"] <= sc.TROPHY_OPACITY + _EPS


def test_property7_grass_weight_within_design_band():
    """草皮层权重必须落在设计带 3–5% 内。"""
    lo, hi = sc.GRASS_OPACITY_BAND
    assert lo <= sc.GRASS_OPACITY <= hi


@settings(max_examples=200)
@given(uv=_uv, t=_t)
def test_composite_ambient_returns_valid_color(uv, t):
    """合成颜色分量恒在 [0,1]（不溢出 / 不为负）。"""
    col = sc.composite_ambient(uv, t)
    assert len(col) == 3
    for ch in col:
        assert 0.0 <= ch <= 1.0


# ════════════════════════════════════════════════════════════════════
#  Property 9: Trophy silhouette is static
#  Feature: worldcup-ultimate-redesign, Property 9: Trophy silhouette is
#  static — L5 output for fixed uv is identical across varied t.
#  Validates: Requirements 16.4
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(
    uv=_uv,
    t1=_t,
    t2=_t,
)
def test_property9_trophy_silhouette_static_in_t(uv, t1, t2):
    a = sc.ambient_contributions(uv, t1)["trophy"]
    b = sc.ambient_contributions(uv, t2)["trophy"]
    # 奖杯层贡献对任意时间完全一致（设计 Property 9）。
    assert a == b
    # 贡献 = 层强度 × 固定权重，因此贡献恰为 trophy_silhouette(uv) 的线性缩放。
    assert a == sc.trophy_silhouette(uv) * sc.TROPHY_OPACITY


@settings(max_examples=100)
@given(uv=_uv)
def test_trophy_silhouette_bounded(uv):
    assert 0.0 <= sc.trophy_silhouette(uv) <= 1.0


# ════════════════════════════════════════════════════════════════════
#  Property 22: Backend API equivalence (integration)
#  Feature: worldcup-ultimate-redesign, Property 22: Backend API
#  equivalence — identical set_palette/set_enabled/set_paused call sequences
#  on both backends produce identical observable state transitions, and the
#  GPU-failure path constructs the CPU backend without crashing.
#  Validates: Requirements 27.1, 27.2, 27.3, 27.4
# ════════════════════════════════════════════════════════════════════
def test_property22_gpu_failure_falls_back_to_cpu(monkeypatch):
    """GPU 构造失败时，工厂应无异常地构造 CPU 后端。（无需 GL 上下文）"""

    def _boom(palette, parent):
        raise RuntimeError("simulated GL 3.3 unavailable / shader link failure")

    monkeypatch.setattr(sc, "_construct_gpu", _boom)
    bd = sc.create_backdrop(sc.NIGHT_STADIUM, prefer_gpu=True)
    assert bd is not None
    assert type(bd).__name__ == "StageCompositorCPU"


@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_property22_backend_observable_state_equivalence(qapp):
    """对两后端施加同一组调用序列，断言可观察状态转移完全一致。"""
    from app.ui.design.hud_theme import NIGHT_STADIUM

    gpu = sc._construct_gpu(NIGHT_STADIUM, None)
    cpu = sc._construct_cpu(NIGHT_STADIUM, None)

    # 同一组公共 API 调用序列。
    seq = [
        ("set_enabled", False),
        ("set_paused", True),
        ("set_enabled", True),
        ("set_paused", False),
        ("set_enabled", False),
    ]

    def observe(b):
        return (b.is_enabled(), b.is_paused(), b.palette_name())

    # 初始可观察状态一致。
    assert observe(gpu) == observe(cpu)

    for method, arg in seq:
        getattr(gpu, method)(arg)
        getattr(cpu, method)(arg)
        assert observe(gpu) == observe(cpu), f"divergence after {method}({arg})"

    # set_palette 也接受相同调用并产生相同可观察状态。
    gpu.set_palette(NIGHT_STADIUM)
    cpu.set_palette(NIGHT_STADIUM)
    assert observe(gpu) == observe(cpu)

    gpu.deleteLater()
    cpu.deleteLater()


@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_cpu_backend_shares_public_api(qapp):
    """CPU 后端暴露与 GPU 后端一致的公共 API 方法集。"""
    from app.ui.design.hud_theme import NIGHT_STADIUM

    cpu = sc._construct_cpu(NIGHT_STADIUM, None)
    for name in ("set_palette", "set_enabled", "set_paused",
                 "is_enabled", "is_paused", "palette_name", "is_animating"):
        assert callable(getattr(cpu, name))
    cpu.deleteLater()
