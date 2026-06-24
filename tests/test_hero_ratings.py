"""Unit tests for Hero Match Card ranking placeholder fallback (Task 8.7).

Covers Requirement 8.2: each team's Elo / FIFA rank / world rank renders the
placeholder "—" when the underlying value is missing (``None``), and the raw
stringified value otherwise.

The placeholder logic lives in the pure function
:func:`app.ui.widgets.hero_match_card.fmt_rank`; the widget-level rendering is
driven through :meth:`HeroMatchCard.set_match` /
``HeroMatchCard._format_ratings``. ``HeroMatchCard`` is a ``QWidget`` so the
widget assertions use the session ``qapp`` fixture and are skipped when Qt
cannot be initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest

from app.ui.widgets import hero_match_card as hmc
from tests.conftest import QT_AVAILABLE

PLACEHOLDER = "—"


# ════════════════════════════════════════════════════════════════════
#  Task 8.7 — pure fmt_rank placeholder fallback (Requirement 8.2)
# ════════════════════════════════════════════════════════════════════
def test_fmt_rank_none_renders_placeholder():
    """Missing value (None) renders the em-dash placeholder. (Req 8.2)"""
    assert hmc.fmt_rank(None) == PLACEHOLDER


def test_fmt_rank_present_values_render_stringified():
    """Present values render as their plain string form. (Req 8.2)"""
    assert hmc.fmt_rank(5) == "5"
    assert hmc.fmt_rank(1800) == "1800"


# ════════════════════════════════════════════════════════════════════
#  Qt-backed widget rendering (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


@pytestmark_qt
def test_hero_card_renders_present_and_missing_ranks(qapp):
    """Present home ranks render their values; all-missing away ranks render '—'.

    Home has Elo 1800 / FIFA #5 / world #3 (all present); away has every value
    missing, so its ratings line shows the placeholder three times. (Req 8.2)
    """
    from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta

    card = HeroMatchCard()
    card.set_match(
        None,
        HeroMeta(
            home_elo=1800,
            home_fifa_rank=5,
            home_world_rank=3,
            # away_* default to None (missing).
        ),
    )

    home_text = card._home_ratings.text()
    assert "1800" in home_text
    assert "5" in home_text
    assert "3" in home_text
    # Home values are all present -> no placeholder.
    assert PLACEHOLDER not in home_text

    away_text = card._away_ratings.text()
    # Three missing values -> exactly three placeholders.
    assert away_text.count(PLACEHOLDER) == 3


@pytestmark_qt
def test_hero_card_all_missing_ranks_render_placeholder(qapp):
    """A fully-missing HeroMeta renders '—' for all six rating values. (Req 8.2)"""
    from app.ui.widgets.hero_match_card import HeroMatchCard, HeroMeta

    card = HeroMatchCard()
    card.set_match(None, HeroMeta())

    home_text = card._home_ratings.text()
    away_text = card._away_ratings.text()
    # Three placeholders per team (Elo / FIFA / world rank) -> six in total.
    assert home_text.count(PLACEHOLDER) == 3
    assert away_text.count(PLACEHOLDER) == 3
