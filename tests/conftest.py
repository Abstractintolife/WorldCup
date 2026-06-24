"""Shared pytest fixtures for the WorldCup 3.0 test-suite.

Many foundation modules create Qt objects (``QPropertyAnimation``,
``QWidget`` subclasses). Those require a single ``QApplication`` instance and a
usable Qt platform plugin. In headless CI / sandboxes we force the
``offscreen`` platform. If Qt cannot be initialised at all (no platform plugin,
missing system libs), GUI-dependent tests are skipped — while the pure-logic
property tests (easing constant, duration clamp, hover-lift target math) still
run, per the spec's testing strategy.
"""
from __future__ import annotations

import os

import pytest

# Force a headless Qt platform before any Qt import.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _try_make_qapp():
    """Return a (singleton) QApplication or ``None`` if Qt is unavailable."""
    try:
        from PyQt6.QtWidgets import QApplication
    except Exception:  # pragma: no cover - import/lib failure
        return None
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app
    except Exception:  # pragma: no cover - no platform plugin / missing libs
        return None


_QAPP = _try_make_qapp()
QT_AVAILABLE = _QAPP is not None


@pytest.fixture(scope="session")
def qapp():
    """Session-wide QApplication; skips the test if Qt is unavailable."""
    if _QAPP is None:
        pytest.skip("Qt/QApplication unavailable in this environment")
    return _QAPP
