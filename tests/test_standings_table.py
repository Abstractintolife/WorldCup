"""Property + unit tests for the Standings Panel v2 (Task 10).

Covers:
* Task 10.2 — Property 14: Form pills validity (Requirement 10.4).
* Task 10.2 — Property 15: Rank-change glyph correctness (Requirement 10.7).
* Task 10.2 — Property 16: Qualification bar proportionality (Requirement 10.5).
* Task 10.4 — Unit: group selector A active initially; selecting a tab marks it
  active and renders that group (Requirements 9.3, 9.4).

The glyph / form-normalisation / qual-fill maths are pure functions and run
headless. Qt-backed widget tests additionally exercise ``StandingsTable`` and
are skipped when Qt cannot be initialised offscreen.

Feature: worldcup-ultimate-redesign
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.ui.widgets.fx import standings_fx as sfx
from tests.conftest import QT_AVAILABLE

_EPS = 1e-9


# ════════════════════════════════════════════════════════════════════
#  Property 14 — Form pills validity (pure)
#  Feature: worldcup-ultimate-redesign, Property 14: Form pills validity —
#  at most 5 pills, each in {W, D, L}.
#  Validates: Requirements 10.4
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=200)
@given(
    results=st.lists(
        st.one_of(
            st.sampled_from(["W", "D", "L", "w", "d", "l", " W ", "x", "", "Z", "1"]),
            st.text(max_size=3),
        ),
        max_size=40,
    )
)
def test_property14_form_pills_validity(results):
    pills = sfx.normalize_form(results)
    # 至多 5 枚。
    assert len(pills) <= sfx.MAX_FORM_PILLS
    # 每枚 ∈ {W, D, L}。
    assert all(p in ("W", "D", "L") for p in pills)


@settings(max_examples=100)
@given(results=st.lists(st.sampled_from(["W", "D", "L"]), min_size=0, max_size=20))
def test_property14_keeps_last_five_in_order(results):
    pills = sfx.normalize_form(results)
    expected = [r.upper() for r in results][-5:]
    assert pills == expected


# ════════════════════════════════════════════════════════════════════
#  Property 15 — Rank-change glyph correctness (pure)
#  Feature: worldcup-ultimate-redesign, Property 15: Rank-change glyph
#  correctness — "↑n"/"↓n"/"—" matches sign of delta, n = |delta|.
#  Validates: Requirements 10.7
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(delta=st.integers(min_value=-500, max_value=500))
def test_property15_rank_delta_glyph(delta):
    glyph = sfx.rank_delta_glyph(delta)
    if delta > 0:
        assert glyph == f"↑{delta}"
    elif delta < 0:
        assert glyph == f"↓{abs(delta)}"
    else:
        assert glyph == "—"


def test_rank_delta_glyph_none_is_dash():
    assert sfx.rank_delta_glyph(None) == "—"


# ════════════════════════════════════════════════════════════════════
#  Property 16 — Qualification bar proportionality (pure)
#  Feature: worldcup-ultimate-redesign, Property 16: Qualification bar
#  proportionality — fill fraction equals clamp(p, 0, 1).
#  Validates: Requirements 10.5
# ════════════════════════════════════════════════════════════════════
@settings(max_examples=300)
@given(p=st.floats(min_value=-100.0, max_value=100.0,
                   allow_nan=False, allow_infinity=False))
def test_property16_qual_fill_is_clamp(p):
    frac = sfx.qual_fill_fraction(p)
    expected = max(0.0, min(1.0, p))
    assert abs(frac - expected) < _EPS
    assert 0.0 <= frac <= 1.0


def test_qual_fill_none_and_text():
    assert sfx.qual_fill_fraction(None) == 0.0
    assert sfx.qual_percent_text(None) == "—"
    assert sfx.qual_percent_text(0.92) == "92%"
    assert sfx.qual_percent_text(1.5) == "100%"
    assert sfx.qual_percent_text(-0.2) == "0%"


# ════════════════════════════════════════════════════════════════════
#  Pure mapping helpers
# ════════════════════════════════════════════════════════════════════
def test_estimate_qual_prob_monotone_and_bounded():
    from app.ui.widgets.standings_table import estimate_qual_prob

    probs = [estimate_qual_prob(r, 4) for r in (1, 2, 3, 4)]
    assert all(0.0 <= x <= 1.0 for x in probs)
    # 名次越靠前出线概率越高（非递增）。
    for a, b in zip(probs, probs[1:]):
        assert a >= b
    assert estimate_qual_prob(1, 0) == 0.0


def test_row_from_standing_derives_rank_delta():
    from app.models.standing import TeamStanding
    from app.ui.widgets.standings_table import row_from_standing

    ts = TeamStanding(
        rank=1, last_rank=3, team_id="t1", team_name="墨西哥", points=7,
        matches_total=3, matches_won=2, matches_draw=1, matches_lost=0,
        goals_pro=5, goals_against=1,
    )
    row = row_from_standing(ts, 4)
    assert row.rank_delta == 2          # last_rank(3) - rank(1)
    assert row.goal_diff == 4
    assert row.team_name == "墨西哥"
    assert 0.0 <= (row.qual_prob or 0) <= 1.0

    ts2 = TeamStanding(
        rank=2, team_id="t2", team_name="韩国", points=5,
        matches_total=3, matches_won=1, matches_draw=2, matches_lost=0,
        goals_pro=3, goals_against=2,
    )
    assert row_from_standing(ts2, 4).rank_delta is None  # no last_rank


# ════════════════════════════════════════════════════════════════════
#  Qt-backed widget tests (skipped if Qt is unavailable)
# ════════════════════════════════════════════════════════════════════
pytestmark_qt = pytest.mark.skipif(
    not QT_AVAILABLE, reason="Qt/QApplication unavailable in this environment"
)


@pytestmark_qt
def test_standings_tabs_are_a_through_l(qapp):
    from app.ui.widgets.standings_table import GROUP_LETTERS, StandingsTable

    table = StandingsTable()
    assert tuple(table._tab_btns.keys()) == GROUP_LETTERS
    assert [b.text() for b in table._tab_btns.values()] == list("ABCDEFGHIJKL")


@pytestmark_qt
def test_standings_group_a_active_by_default(qapp):
    """Req 9.3: group A is the active tab initially."""
    from app.ui.widgets.standings_table import StandingsTable

    table = StandingsTable()
    assert table.active_group == "A"
    assert table._tab_btns["A"].isChecked() is True
    assert all(not b.isChecked() for k, b in table._tab_btns.items() if k != "A")
    # 默认渲染设计稿样例（墨西哥 / 韩国 / 捷克 / 南非）。
    assert table._rows_box.count() == 4


@pytestmark_qt
def test_standings_selecting_tab_marks_active_and_renders_group(qapp):
    """Req 9.4: selecting a tab marks it active and renders that group.

    Inject distinct A/B groups via ``set_groups`` and assert that switching the
    active tab re-renders the standings so ``current_team_names()`` reflects the
    newly selected group (the table's rendered rows), while the previously
    active tab is deactivated.
    """
    from app.models.standing import GroupStanding, TeamStanding
    from app.ui.widgets.standings_table import StandingsTable

    def _team(rank, name, tid):
        return TeamStanding(
            rank=rank, team_id=tid, team_name=name, points=9 - rank,
            matches_total=3, matches_won=3 - rank, matches_draw=0,
            matches_lost=rank - 1, goals_pro=5, goals_against=rank,
        )

    group_a = GroupStanding(name="A组", teams=[
        _team(1, "墨西哥", "mx"), _team(2, "韩国", "kr"),
    ])
    group_b = GroupStanding(name="B组", teams=[
        _team(1, "巴西", "br"), _team(2, "塞尔维亚", "rs"), _team(3, "瑞士", "ch"),
    ])
    table = StandingsTable()
    table.set_groups([group_a, group_b])

    # A 组初始激活并渲染 A 组真实数据。
    assert table.active_group == "A"
    assert table.current_team_names() == ["墨西哥", "韩国"]

    # 触发 B 标签点击（公开点击路径）。
    table._tab_btns["B"].click()
    assert table.active_group == "B"
    assert table._tab_btns["B"].isChecked() is True
    assert table._tab_btns["A"].isChecked() is False
    # 重渲染为 B 组：current_team_names() 反映选中组的真实球队，且行数一致。
    assert table.current_team_names() == ["巴西", "塞尔维亚", "瑞士"]
    assert table._rows_box.count() == 3

    # 切回 A 组（点击 A 标签）：再次反映 A 组。
    table._tab_btns["A"].click()
    assert table.active_group == "A"
    assert table._tab_btns["A"].isChecked() is True
    assert table._tab_btns["B"].isChecked() is False
    assert table.current_team_names() == ["墨西哥", "韩国"]


@pytestmark_qt
def test_standings_team_click_emits_signal(qapp):
    from app.models.standing import GroupStanding, TeamStanding
    from app.ui.widgets.standings_table import StandingsTable

    captured: list[str] = []
    table = StandingsTable()
    table.team_clicked.connect(captured.append)
    grp = GroupStanding(name="C组", teams=[
        TeamStanding(rank=1, team_id="x9", team_name="法国", points=7,
                     matches_total=3, matches_won=2, matches_draw=1,
                     matches_lost=0, goals_pro=6, goals_against=2),
    ])
    table.set_groups([grp])
    table._select("C")
    # 找到该行并触发点击（行的 mousePressEvent 被重写为发信号，忽略事件参数）。
    row = table._rows_box.itemAt(0).widget()
    row.mousePressEvent(None)
    assert captured == ["x9"]
