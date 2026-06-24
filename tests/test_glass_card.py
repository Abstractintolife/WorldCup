"""GUI tests for GlassCard hover-lift integration (Task 1.7 support).

Feature: worldcup-ultimate-redesign, Property 3: Hover lift magnitude.
Validates: Requirements 19.4, 20.2, 20.3

Skipped automatically when Qt cannot be initialised headless.
"""
from __future__ import annotations

import pytest

from tests.conftest import QT_AVAILABLE

pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


def test_glass_card_has_single_dropshadow(qapp):
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect

    from app.ui.widgets.glass_card import GlassCard

    card = GlassCard()
    eff = card.graphicsEffect()
    assert isinstance(eff, QGraphicsDropShadowEffect)
    # 0 10px 40px rgba(0,0,0,0.4)
    assert eff.blurRadius() == 40
    assert eff.xOffset() == 0
    assert eff.yOffset() == 10
    assert round(eff.color().alphaF(), 2) == 0.40


def _enter_event():
    from PyQt6.QtCore import QPointF
    from PyQt6.QtGui import QEnterEvent

    p = QPointF(0.0, 0.0)
    return QEnterEvent(p, p, p)


def _leave_event():
    from PyQt6.QtCore import QEvent

    return QEvent(QEvent.Type.Leave)


def test_glass_card_hover_lifts_and_returns(qapp):
    from PyQt6.QtCore import QPoint

    from app.ui.widgets.glass_card import GlassCard

    card = GlassCard()
    card.move(QPoint(120, 80))
    rest = card.pos()

    # enter -> memorises rest, border brightens
    card.enterEvent(_enter_event())
    assert card.is_hovered is True
    assert getattr(card, "_hud_rest_pos", None) == rest

    # leave -> returns exactly to rest
    card.leaveEvent(_leave_event())
    assert card.is_hovered is False


def test_glass_card_hover_never_animates_blur_radius(qapp):
    """Req 20.3: hover animates pos, never the shadow blur radius."""
    from app.ui.widgets.glass_card import GlassCard

    card = GlassCard()
    before = card.graphicsEffect().blurRadius()
    card.enterEvent(_enter_event())
    card.leaveEvent(_leave_event())
    after = card.graphicsEffect().blurRadius()
    assert before == after == 40
