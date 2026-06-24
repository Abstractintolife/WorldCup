"""Unit tests for the Stat Strip (Task 11).

Covers:
* Task 11.2 — Stat Strip composition: exactly six equal-width cards in the
  specified order with the sampled headline / secondary / icon content
  (Requirements 11.1, 11.2, and the per-card samples 11.4–11.9).
* compute_stats pure-function behaviour: real data overrides the sampled
  values where available, and falls back to the design samples when data is
  missing (Requirement 11.3).

The compute_stats maths is a pure function and runs headless. The Qt-backed
StatStrip widget tests are skipped when Qt cannot be initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest

from app.ui.widgets.stat_strip import (
    SAMPLE_STATS,
    STAT_ORDER,
    StatSpec,
    compute_stats,
)
from tests.conftest import QT_AVAILABLE

# 设计稿规定的六张卡（自左至右，需求 11.2）。
EXPECTED_TITLES = ["总比赛场次", "总进球数", "进球球员", "平均进球", "参赛球队", "主办城市"]


# ════════════════════════════════════════════════════════════════════
#  纯函数：compute_stats 顺序 + 样例回退（需求 11.2 / 11.3）
# ════════════════════════════════════════════════════════════════════
def test_sample_stats_canonical_order():
    """六张样例卡的顺序与标识固定（需求 11.2）。"""
    assert [s.key for s in SAMPLE_STATS] == list(STAT_ORDER)
    assert [s.title for s in SAMPLE_STATS] == EXPECTED_TITLES


def test_compute_stats_falls_back_to_samples_when_empty():
    """无数据时回退设计稿样例值 104/141/89/2.94/48/16（需求 11.3 降级）。"""
    specs = compute_stats(matches=[], groups=[], scorers=[])
    assert [s.title for s in specs] == EXPECTED_TITLES
    by_key = {s.key: s for s in specs}
    assert by_key["matches"].value == 104
    assert by_key["matches"].secondary == "已结束 48 场"
    assert by_key["goals"].value == 141
    assert by_key["scorers"].value == 89
    assert by_key["avg"].value == 2.94
    assert by_key["avg"].decimals == 2
    assert by_key["teams"].value == 48
    assert by_key["cities"].value == 16


def test_compute_stats_per_card_sample_content():
    """每张样例卡的次级文案 / 涨跌幅 / 图标对齐设计稿（需求 11.4–11.9）。"""
    by_key = {s.key: s for s in compute_stats()}
    # 11.4 总比赛场次 — 迷你折线、无图标。
    assert by_key["matches"].sparkline is True
    assert by_key["matches"].icon == ""
    # 11.5 总进球数 — ↑8% / 场均2.94球 / ⚽。
    assert by_key["goals"].delta == "↑8%"
    assert by_key["goals"].secondary == "场均2.94球"
    assert by_key["goals"].icon == "⚽"
    # 11.6 进球球员 — ↑15% / 来自32个国家。
    assert by_key["scorers"].delta == "↑15%"
    assert by_key["scorers"].secondary == "来自32个国家"
    # 11.7 平均进球 — ↑6% / 每场比赛 / 两位小数。
    assert by_key["avg"].delta == "↑6%"
    assert by_key["avg"].secondary == "每场比赛"
    # 11.8 参赛球队 — 12个小组、无 delta。
    assert by_key["teams"].secondary == "12个小组"
    assert by_key["teams"].delta is None
    # 11.9 主办城市 — 美国/加拿大/墨西哥、无 delta。
    assert by_key["cities"].secondary == "美国/加拿大/墨西哥"
    assert by_key["cities"].delta is None


def test_compute_stats_uses_real_match_data():
    """有真实比赛数据时覆盖样例：总场次 / 已完赛 / 总进球 / 场均（需求 11.3）。"""
    class _M:
        def __init__(self, status, a_id, b_id, fa=None, fb=None):
            self.status = status
            self.team_a_id, self.team_b_id = a_id, b_id
            self.fs_a, self.fs_b = fa, fb
            self.score_a = self.score_b = None

    matches = [
        _M("Played", "t1", "t2", "2", "1"),   # 3 球
        _M("Played", "t3", "t4", "0", "0"),   # 0 球
        _M("Played", "t1", "t3", "1", "2"),   # 3 球
        _M("Fixture", "t2", "t4"),            # 未开赛，不计进球
    ]
    specs = {s.key: s for s in compute_stats(matches=matches)}
    assert specs["matches"].value == 4
    assert specs["matches"].secondary == "已结束 3 场"
    assert specs["goals"].value == 6          # 3 + 0 + 3
    assert specs["avg"].value == 2.0          # 6 / 3 played
    assert specs["teams"].value == 4          # t1..t4 distinct


def test_compute_stats_uses_real_scorer_data():
    """有真实射手榜时：进球球员数 = 计数>0 的球员数；国家数取自队名。"""
    class _S:
        def __init__(self, name, team, count):
            self.person_name, self.team_name, self.count = name, team, count

    scorers = [
        _S("梅西", "阿根廷", 5),
        _S("姆巴佩", "法国", 4),
        _S("哈兰德", "挪威", 4),
        _S("替补", "法国", 0),       # 0 球不计入
    ]
    specs = {s.key: s for s in compute_stats(scorers=scorers)}
    assert specs["scorers"].value == 3        # 三名有进球
    assert specs["scorers"].secondary == "来自3个国家"   # 阿根廷/法国/挪威


# ════════════════════════════════════════════════════════════════════
#  Qt-backed widget tests (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


@pytestmark_qt
def test_stat_strip_has_exactly_six_cards(qapp):
    """需求 11.1：恰好六张等宽卡，且横向排布。"""
    from app.ui.widgets.stat_strip import StatStrip

    strip = StatStrip()
    assert len(strip.cards) == 6
    # 每张卡 stretch 相等（=1）→ 等宽。
    stretches = [strip._row.stretch(i) for i in range(strip._row.count())]
    assert stretches == [1, 1, 1, 1, 1, 1]


@pytestmark_qt
def test_stat_strip_card_order_and_sampled_content(qapp):
    """需求 11.2/11.4–11.9：六卡顺序 + 标题数字 / 次级 / 图标取自设计稿样例。"""
    from app.ui.widgets.stat_strip import StatStrip

    strip = StatStrip()
    assert strip.titles == EXPECTED_TITLES

    cards = strip.cards
    # 标题数字（CountUpNumber 目标值）精确等于样例。
    assert [c.value_target for c in cards] == [104, 141, 89, 2.94, 48, 16]
    # 次级文本。
    assert [c.secondary_text for c in cards] == [
        "已结束 48 场", "场均2.94球", "来自32个国家",
        "每场比赛", "12个小组", "美国/加拿大/墨西哥",
    ]
    # 图标：首卡用折线（无图标字形），其余为对应 emoji。
    assert cards[0].has_sparkline is True
    assert cards[0].icon_text == ""
    assert [c.icon_text for c in cards[1:]] == ["⚽", "👤", "🎯", "🛡", "📍"]
    # 涨跌幅：仅总进球/进球球员/平均进球三张展示。
    assert [c.delta_text for c in cards] == ["", "↑8%", "↑15%", "↑6%", "", ""]


@pytestmark_qt
def test_stat_strip_set_stats_updates_cards(qapp):
    """set_stats 用新的 StatSpec 覆盖卡片标题数字与文案。"""
    from app.ui.widgets.stat_strip import StatStrip, compute_stats

    class _M:
        def __init__(self, status, a_id, b_id, fa=None, fb=None):
            self.status = status
            self.team_a_id, self.team_b_id = a_id, b_id
            self.fs_a, self.fs_b = fa, fb
            self.score_a = self.score_b = None

    strip = StatStrip()
    matches = [_M("Played", "t1", "t2", "3", "0"), _M("Played", "t3", "t4", "1", "1")]
    strip.set_stats(compute_stats(matches=matches))
    cards = strip.cards
    assert cards[0].value_target == 2            # 两场
    assert cards[0].secondary_text == "已结束 2 场"
    assert cards[1].value_target == 5            # 3 + 0 + 1 + 1
