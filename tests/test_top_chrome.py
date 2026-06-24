"""Unit tests for the Top HUD Bar and Sub-Header chrome (Tasks 6.3 / 6.4).

Feature: worldcup-ultimate-redesign
Validates: Requirements 3.1, 3.2, 3.3 (Top HUD Bar) and 4.1, 4.2, 4.3 (Sub-Header).

Skipped automatically when Qt cannot be initialised headless.
"""
from __future__ import annotations

import pytest

from tests.conftest import QT_AVAILABLE

pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


# ── Top HUD Bar ────────────────────────────────────────────
def test_top_bar_default_title_and_subtitle(qapp):
    """Req 3.1: page title 概览 + subtitle OVERVIEW."""
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    assert bar._title.text() == "概览"
    assert bar._subtitle.text() == "OVERVIEW"


def test_top_bar_subtitle_mapping_for_overview(qapp):
    """Req 3.1: the overview subtitle is exactly OVERVIEW even when the
    page supplies a longer subtitle string."""
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    bar.set_title("概览", "OVERVIEW · 2026 FIFA 世界杯实时数据中心")
    assert bar._title.text() == "概览"
    assert bar._subtitle.text() == "OVERVIEW"


def test_top_bar_search_placeholder(qapp):
    """Req 3.2: centered search box placeholder."""
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    assert bar._search.placeholderText() == "搜索球队 / 球员 / 比赛…"


def test_top_bar_search_submits_trimmed_text(qapp):
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    received: list[str] = []
    bar.search_submitted.connect(received.append)
    bar._search.setText("  梅西  ")
    bar._search.returnPressed.emit()
    assert received == ["梅西"]


def test_top_bar_has_bell_region_and_avatar(qapp):
    """Req 3.3: notification bell, region globe showing CN, profile avatar."""
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    assert bar._bell.text() == "🔔"
    assert "CN" in bar._region.text()
    # avatar is a circular button present in the bar
    assert bar._avatar is not None


def test_top_bar_profile_click_signal(qapp):
    from app.ui.widgets.top_hud_bar import TopHudBar

    bar = TopHudBar()
    fired: list[bool] = []
    bar.profile_clicked.connect(lambda: fired.append(True))
    bar._avatar.click()
    assert fired == [True]


# ── Sub-Header ─────────────────────────────────────────────
def test_sub_header_text_lines(qapp):
    """Req 4.1 / 4.2: the two sub-header text lines."""
    from app.ui.widgets.sub_header import SubHeader

    sh = SubHeader()
    assert sh._line1.text() == "2026 美加墨世界杯 · 实时数据总览"
    assert sh._line2.text() == "OVERVIEW · 数据来源：懂球帝公开接口"


def test_sub_header_live_pill_connected_by_default(qapp):
    """Req 4.3: green 实时数据已连接 pill with a status dot."""
    from app.ui.widgets.sub_header import SubHeader

    sh = SubHeader()
    assert sh.pill.is_connected is True
    assert sh.pill.text == "实时数据已连接"


def test_sub_header_pill_disconnect_toggle(qapp):
    from app.ui.widgets.sub_header import SubHeader

    sh = SubHeader()
    sh.set_connected(False)
    assert sh.pill.is_connected is False
    sh.set_connected(True)
    assert sh.pill.is_connected is True
    assert sh.pill.text == "实时数据已连接"
