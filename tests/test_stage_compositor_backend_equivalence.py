"""Integration test for Stage Compositor backend selection / equivalence.

Task 2.6 — **Property 22: Backend API equivalence**. The GPU
(:class:`StageCompositor`) and CPU (:class:`StageCompositorCPU`) backends share
the *exact* same public API (``set_palette`` / ``set_enabled`` / ``set_paused``)
via ``_CompositorMixin``. This integration test drives the *same* sequence of
public calls against *both* backends and asserts their observable state
(``is_enabled`` / ``is_paused`` / ``palette_name`` / ``particle_count`` and the
visibility-independent ``is_animating``) transitions identically after every
call. It also exercises the GPU-failure path: ``create_backdrop`` must fall back
to constructing the CPU backend (without crashing) and log a warning, and the
runtime ``gpu_failed`` signal must be connectable for hot-swap wiring.

Both backends are real Qt widgets, so the equivalence cases are skipped when Qt
cannot initialise headless. The GPU-failure→CPU fallback case is verified
without a GL context (it only needs the factory + a monkeypatched constructor).

In a headless ``offscreen`` environment the GPU ``QOpenGLWidget`` still
*constructs* fine (the GL context / shader link is deferred to first show), so
we drive the real GPU class directly; the KEY assertion is that the two
backends are API-equivalent at the observable-state level. ``is_animating`` is
driven purely by FrameClock subscription which is gated on widget visibility —
neither widget is shown here, so both report ``False`` throughout, which is
itself an equivalence we assert.

Feature: worldcup-ultimate-redesign, Property 22: Backend API equivalence
Validates: Requirements 27.1, 27.2, 27.3, 27.4
"""
from __future__ import annotations

import logging

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.ui.design.hud_theme import NIGHT_STADIUM
from app.ui.widgets import stage_compositor as sc
from tests.conftest import QT_AVAILABLE

_LOGGER_NAME = "app.ui.widgets.stage_compositor"

# The full observable-state surface shared by both backends (Property 22).
_OBSERVABLE = (
    "is_enabled",
    "is_paused",
    "palette_name",
    "particle_count",
    "is_animating",
)


def _observe(backend) -> tuple:
    """Snapshot every observable accessor into a comparable tuple."""
    return tuple(getattr(backend, name)() for name in _OBSERVABLE)


def _apply(backend, op) -> None:
    """Apply one ``(method, arg)`` public-API call to a backend."""
    method, arg = op
    getattr(backend, method)(arg)


def _drain(*widgets) -> None:
    """Schedule deletion and pump the event loop so widgets are reclaimed."""
    try:
        from PyQt6.QtWidgets import QApplication

        for w in widgets:
            w.deleteLater()
        app = QApplication.instance()
        if app is not None:
            app.processEvents()
    except Exception:  # pragma: no cover - teardown best-effort
        pass


# A "valid" alternate palette object that is duck-typed as a HudPalette so
# set_palette accepts it, plus invalid objects both backends must ignore
# identically. NIGHT_STADIUM is the canonical night-stadium theme.
_OPS = [
    ("set_enabled", True),
    ("set_enabled", False),
    ("set_paused", True),
    ("set_paused", False),
    ("set_palette", NIGHT_STADIUM),   # valid HudPalette → accepted
    ("set_palette", "not-a-palette"),  # invalid → ignored by BOTH backends
    ("set_palette", None),             # invalid → ignored by BOTH backends
]

_op_strategy = st.lists(st.sampled_from(_OPS), min_size=1, max_size=20)


# ════════════════════════════════════════════════════════════════════
#  GPU-failure path (no GL context needed) — Req 27.1 / 27.2
# ════════════════════════════════════════════════════════════════════
@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_gpu_failure_falls_back_to_cpu_and_logs_warning(qapp, monkeypatch, caplog):
    """When GPU construction raises, the factory builds the CPU backend and warns.

    Simulates "GPU context unavailable / shader link failed" by forcing
    ``_construct_gpu`` to raise, then asserts ``create_backdrop(prefer_gpu=True)``
    returns a ``StageCompositorCPU`` (no crash) and emits a WARNING log.
    """

    def _boom(palette, parent):
        raise RuntimeError("simulated OpenGL 3.3 context unavailable / link failure")

    monkeypatch.setattr(sc, "_construct_gpu", _boom)

    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        backdrop = sc.create_backdrop(NIGHT_STADIUM, prefer_gpu=True)

    assert backdrop is not None
    assert type(backdrop).__name__ == "StageCompositorCPU"
    # A warning about the GPU fallback must have been logged (Req 27.2).
    assert any(r.levelno == logging.WARNING for r in caplog.records)
    assert any("CPU" in r.getMessage() or "GPU" in r.getMessage()
               for r in caplog.records)
    # The fallback backend still honours the full public API.
    for name in ("set_palette", "set_enabled", "set_paused", *_OBSERVABLE):
        assert callable(getattr(backdrop, name))
    _drain(backdrop)


@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_prefer_gpu_false_constructs_cpu_directly(qapp):
    """``prefer_gpu=False`` skips the GPU path entirely and builds CPU."""
    backdrop = sc.create_backdrop(NIGHT_STADIUM, prefer_gpu=False)
    assert type(backdrop).__name__ == "StageCompositorCPU"
    _drain(backdrop)


@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_gpu_failed_signal_is_connectable_for_hot_swap(qapp):
    """The runtime ``gpu_failed`` signal can be wired (drives the 27.4 hot-swap).

    A real shader-link failure only surfaces inside ``initializeGL`` once a GL
    context exists, which the headless offscreen platform cannot provide. We
    therefore verify the *contract*: the signal exists, accepts a connection,
    and invokes the connected slot when emitted — exactly what MainWindow relies
    on to hot-swap to the CPU backend on detected GPU failure.
    """
    gpu = sc._construct_gpu(NIGHT_STADIUM, None)
    fired = []
    gpu.gpu_failed.connect(lambda: fired.append(True))
    gpu.gpu_failed.emit()
    assert fired == [True]
    _drain(gpu)


# ════════════════════════════════════════════════════════════════════
#  Observable-state equivalence — Req 27.3 (Property 22)
# ════════════════════════════════════════════════════════════════════
@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_initial_observable_state_is_identical(qapp):
    """Freshly-constructed GPU and CPU backends share identical initial state."""
    gpu = sc._construct_gpu(NIGHT_STADIUM, None)
    cpu = sc._construct_cpu(NIGHT_STADIUM, None)
    try:
        assert _observe(gpu) == _observe(cpu)
        # Sanity: defaults match the documented contract.
        assert gpu.is_enabled() is True and gpu.is_paused() is False
        assert 80 <= gpu.particle_count() <= 120
    finally:
        _drain(gpu, cpu)


@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_deterministic_call_sequence_state_equivalence(qapp):
    """A thorough deterministic call sequence keeps both backends in lock-step."""
    gpu = sc._construct_gpu(NIGHT_STADIUM, None)
    cpu = sc._construct_cpu(NIGHT_STADIUM, None)
    try:
        sequence = [
            ("set_enabled", False),
            ("set_paused", True),
            ("set_palette", "ignored"),     # invalid → no-op on both
            ("set_enabled", True),
            ("set_palette", NIGHT_STADIUM),
            ("set_paused", False),
            ("set_enabled", False),
            ("set_paused", True),
            ("set_palette", None),          # invalid → no-op on both
            ("set_enabled", True),
            ("set_paused", False),
        ]
        assert _observe(gpu) == _observe(cpu)
        for op in sequence:
            _apply(gpu, op)
            _apply(cpu, op)
            assert _observe(gpu) == _observe(cpu), f"divergence after {op}"
    finally:
        _drain(gpu, cpu)


@settings(
    max_examples=120,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(ops=_op_strategy)
@pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)
def test_random_call_sequences_state_equivalence(qapp, ops):
    """Property 22: for ANY sequence of public calls, GPU and CPU observable
    state transitions are identical after every call (≥100 randomized examples).
    """
    gpu = sc._construct_gpu(NIGHT_STADIUM, None)
    cpu = sc._construct_cpu(NIGHT_STADIUM, None)
    try:
        assert _observe(gpu) == _observe(cpu)
        for op in ops:
            _apply(gpu, op)
            _apply(cpu, op)
            assert _observe(gpu) == _observe(cpu), f"divergence after {op}"
    finally:
        _drain(gpu, cpu)
