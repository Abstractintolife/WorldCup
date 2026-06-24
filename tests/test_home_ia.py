"""Unit tests for the Overview Page weighted IA grid (Task 7.2).

Feature: worldcup-ultimate-redesign
Validates: Requirements 1.2 (Hero:Overview:Standings:Schedule:Analysis:Other =
           40:20:15:10:10:5 visual-weight ratio), 1.3 (ratios preserved on
           window resize), 1.4 (Hero ~65% / Standings ~35% column split).

The IA weights are exposed as module-level constants/helpers so the canonical
ratio can be asserted without a display. The HomePage instantiation /
resize checks are skipped automatically when Qt cannot be initialised headless.
"""
from __future__ import annotations

import pytest

from app.ui.pages.home_page import (
    HERO_COLUMN_WEIGHTS,
    IA_WEIGHTS,
    ia_row_stretches,
    ia_weight_ratio,
)
from tests.conftest import QT_AVAILABLE

# 设计稿规定的 6 区视觉权重比（需求 1.2）。
EXPECTED_RATIO = [40, 20, 15, 10, 10, 5]


# ── 纯常量校验（无需显示） ───────────────────────────────────
def test_ia_weight_ratio_matches_spec() -> None:
    """Req 1.2: configured stretch factors equal 40/20/15/10/10/5."""
    assert ia_weight_ratio() == EXPECTED_RATIO
    assert IA_WEIGHTS["hero"] == 40
    assert IA_WEIGHTS["overview"] == 20
    assert IA_WEIGHTS["standings"] == 15
    assert IA_WEIGHTS["schedule"] == 10
    assert IA_WEIGHTS["analysis"] == 10
    assert IA_WEIGHTS["other"] == 5


def test_ia_row_stretches_sum_partitions_weights() -> None:
    """The three vertical rows budget hero / overview / (schedule+analysis+other)."""
    hero, overview, bottom = ia_row_stretches()
    assert hero == 40
    assert overview == 20
    assert bottom == IA_WEIGHTS["schedule"] + IA_WEIGHTS["analysis"] + IA_WEIGHTS["other"]
    assert bottom == 25


def test_hero_column_split_is_65_35() -> None:
    """Req 1.4: Hero occupies the wider (~65%) left column, Standings ~35% right."""
    assert HERO_COLUMN_WEIGHTS == (65, 35)
    assert HERO_COLUMN_WEIGHTS[0] > HERO_COLUMN_WEIGHTS[1]


# ── 实际布局配置 + 缩放保持（需要 Qt 才能实例化页面） ─────────
pytestmark_gui = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


def _make_home(qapp):
    from app.services.data_service import DataService
    from app.ui.pages.home_page import HomePage

    return HomePage(DataService())


@pytestmark_gui
def test_homepage_configures_spec_stretches(qapp):
    """The page exposes the canonical 40:20:15:10:10:5 ratio and applies it."""
    home = _make_home(qapp)
    assert home.region_weights() == EXPECTED_RATIO
    # Vertical rows: Hero(40) / Stat Strip(20) / bottom multi-panel(25).
    assert home.row_stretches() == (40, 20, 25)
    # Hero row columns: Hero ~65% left, Standings ~35% right.
    assert home.hero_column_stretches() == (65, 35)
    # Bottom row columns (Task 12): Today / Live / Top Scorers / Host Cities.
    assert home.bottom_column_stretches() == (10, 10, 7, 7)


@pytestmark_gui
def test_homepage_preserves_ratios_after_resize(qapp):
    """Req 1.3: configured stretch ratios are preserved across window resizes."""
    home = _make_home(qapp)
    before_rows = home.row_stretches()
    before_hero = home.hero_column_stretches()
    before_bottom = home.bottom_column_stretches()

    for w, h in ((1600, 1000), (640, 480), (1920, 1080), (800, 600)):
        home.resize(w, h)
        qapp.processEvents()
        assert home.row_stretches() == before_rows
        assert home.hero_column_stretches() == before_hero == (65, 35)
        assert home.bottom_column_stretches() == before_bottom
