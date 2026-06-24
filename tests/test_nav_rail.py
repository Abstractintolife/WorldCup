"""Unit tests for the Navigation Rail (Task 6.2).

Feature: worldcup-ultimate-redesign
Validates: Requirements 2.2 (nav item labels/exact order),
           2.3 (only the active page's item is highlighted).

Skipped automatically when Qt cannot be initialised headless.
"""
from __future__ import annotations

import pytest

from tests.conftest import QT_AVAILABLE

pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


# 导航 13 项，严格顺序（中文标签）—— 在「数据分析」后新增「概率预测」。
EXPECTED_LABELS = [
    "概览",
    "赛程中心",
    "实时比赛",
    "球队",
    "球员",
    "数据分析",
    "概率预测",
    "积分榜",
    "射手榜",
    "场馆地图",
    "新闻资讯",
    "收藏夹",
    "设置",
]

EXPECTED_KEYS = [
    "home",
    "schedule",
    "live",
    "teams",
    "players",
    "analysis",
    "probability",
    "standings",
    "scorers",
    "venue",
    "news",
    "favorites",
    "settings",
]


def _make_rail(qapp):
    from app.ui.widgets.nav_rail import NAV_ITEMS, NavRail

    return NavRail(NAV_ITEMS)


def test_nav_rail_has_exactly_thirteen_items(qapp):
    rail = _make_rail(qapp)
    assert len(rail.nav_keys()) == 13
    assert len(rail.nav_labels()) == 13


def test_nav_rail_labels_match_spec_order(qapp):
    """Req 2.2: labels appear in the exact spec order."""
    rail = _make_rail(qapp)
    assert rail.nav_labels() == EXPECTED_LABELS


def test_nav_rail_keys_match_spec_order(qapp):
    rail = _make_rail(qapp)
    assert rail.nav_keys() == EXPECTED_KEYS


def test_overview_active_highlights_only_overview(qapp):
    """Req 2.3: while Overview is active, only 概览 is highlighted."""
    rail = _make_rail(qapp)
    rail.set_active("home")
    assert rail.active_key == "home"
    assert rail.active_items() == ["home"]
    assert rail.item("home").is_active is True
    # every other item is inactive
    for key in EXPECTED_KEYS:
        if key != "home":
            assert rail.item(key).is_active is False


def test_only_one_item_highlighted_after_switch(qapp):
    """Switching the active page leaves exactly one highlighted item."""
    rail = _make_rail(qapp)
    for key in EXPECTED_KEYS:
        rail.set_active(key)
        assert rail.active_items() == [key]
        assert sum(1 for k in EXPECTED_KEYS if rail.item(k).is_active) == 1


def test_set_active_unknown_key_is_noop(qapp):
    rail = _make_rail(qapp)
    rail.set_active("home")
    rail.set_active("does-not-exist")
    # highlight unchanged
    assert rail.active_items() == ["home"]


def test_clicking_item_emits_selected_and_highlights(qapp):
    """Clicking a row highlights it and emits the selected signal."""
    rail = _make_rail(qapp)
    received: list[str] = []
    rail.selected.connect(received.append)

    rail.item("standings").clicked.emit("standings")

    assert received == ["standings"]
    assert rail.active_items() == ["standings"]


def test_live_badge_toggles_on_live_entry(qapp):
    """LIVE badge lights only the live-match entry when a match is live."""
    rail = _make_rail(qapp)
    live_item = rail.item("live")

    rail.set_live(True)
    assert live_item._badge.isVisibleTo(rail) or not rail.isVisible()
    # badge is explicitly un-hidden
    assert not live_item._badge.isHidden()

    rail.set_live(False)
    assert live_item._badge.isHidden()
