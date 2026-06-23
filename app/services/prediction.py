"""赛前预测引擎（纯计算，无 UI / 无网络）。

为什么是「计算」而非「抓取」
------------------------------
用户希望把 leisu.com（swot / 数据分析页）与 oddsportal 的「AI 赛事预测」
信息搬进软件。但这三个站点均为服务端不可抓取：

* ``leisu.com/guide/swot-*`` → 阿里云 WAF，服务端请求一律返回 HTTP 405；
* ``live.leisu.com/shujufenxi-*`` → 返回 403「访问过于频繁」拦截页；
* ``oddsportal.com`` → 数据由前端 JS 渲染，服务端只能拿到空壳标题。

因此本模块**完全基于软件已有的公开数据**（懂球帝赛程 + 积分榜）复刻出同款
内容：比赛结果倾向、进球大小（Over/Under 2.5）、双方是否进球（BTTS）、
近 5 场走势、历史交锋、SWOT（优势 / 劣势 / 机会 / 威胁）以及模型推算赔率。
所有数字皆由真实数据测算，赔率标注为「模型推算」以区别于博彩公司报价。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.models.match import Match, MatchStatus
from app.models.standing import GroupStanding, TeamStanding


# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────
@dataclass
class FormGame:
    """近期一场比赛的精简结果（站在目标球队视角）。"""

    result: str            # "W" / "D" / "L"
    score: str             # "2 - 0"
    opponent: str          # 对手名
    total_goals: int       # 全场总进球
    both_scored: bool      # 双方是否都破门
    is_home: bool


@dataclass
class TeamForm:
    team_id: str = ""
    team_name: str = ""
    games: list[FormGame] = field(default_factory=list)

    @property
    def wins(self) -> int:
        return sum(1 for g in self.games if g.result == "W")

    @property
    def draws(self) -> int:
        return sum(1 for g in self.games if g.result == "D")

    @property
    def losses(self) -> int:
        return sum(1 for g in self.games if g.result == "L")

    @property
    def over25(self) -> int:
        return sum(1 for g in self.games if g.total_goals >= 3)

    @property
    def btts(self) -> int:
        return sum(1 for g in self.games if g.both_scored)

    @property
    def count(self) -> int:
        return len(self.games)


@dataclass
class TeamMetrics:
    rank: int | None = None
    matches: int = 0
    ppm: float = 0.0          # 场均积分
    gfpm: float = 0.0         # 场均进球
    gapm: float = 0.0         # 场均失球
    form_n: float = 0.5       # 近期状态分 0~1
    index: float = 50.0       # 综合指数 0~100


@dataclass
class Trend:
    """一条「AI 预测趋势」（对应截图里的每个区块）。"""

    category: str             # "比赛结果" / "进球数" / "双方进球"
    headline: str             # "阿根廷 胜" / "进球数 大于 2.5" / "双方进球 否"
    probability: float        # 0~1
    narrative: str            # 一段中文分析
    stat_a: str               # "阿根廷：近 5 场 3 场取胜"
    stat_b: str               # "奥地利：近 5 场 3 场告负"
    market: str               # "1X2 · 主胜"
    odds: float               # 模型推算赔率（小数）


@dataclass
class MatchPrediction:
    match: Match
    metrics_a: TeamMetrics
    metrics_b: TeamMetrics
    form_a: TeamForm
    form_b: TeamForm
    win_a: float
    draw: float
    win_b: float
    expected_goals: float
    over25_prob: float
    btts_prob: float
    trends: list[Trend]
    swot_a: dict[str, list[str]]
    swot_b: dict[str, list[str]]
    h2h_total: int
    h2h_a_win: int
    h2h_draw: int
    h2h_b_win: int
    verdict: str
    group_name: str = ""
    exp_goals_a: float = 0.0
    exp_goals_b: float = 0.0


# ─────────────────────────────────────────────
# 工具
# ─────────────────────────────────────────────
def _match_goals(m: Match) -> tuple[int, int] | None:
    """取一场已结束比赛的双方进球（A, B）。无法解析返回 None。"""
    try:
        a = int(m.fs_a if m.fs_a not in (None, "") else (m.score_a or 0))
        b = int(m.fs_b if m.fs_b not in (None, "") else (m.score_b or 0))
    except (TypeError, ValueError):
        return None
    return a, b


def _find_standing(
    team_id: str, groups: list[GroupStanding]
) -> tuple[str, TeamStanding] | None:
    for g in groups:
        for ts in g.teams:
            if ts.team_id == team_id:
                return g.name, ts
    return None


def _recent_form(
    team_id: str,
    team_name: str,
    all_matches: list[Match],
    exclude_match_id: str | None,
    limit: int = 5,
) -> TeamForm:
    played = [
        m for m in all_matches
        if m.status == MatchStatus.PLAYED
        and team_id in (m.team_a_id, m.team_b_id)
        and (exclude_match_id is None or m.match_id != exclude_match_id)
    ]
    played.sort(key=lambda x: x.start_play or x.date_utc or "", reverse=True)

    form = TeamForm(team_id=team_id, team_name=team_name)
    for m in played[:limit]:
        goals = _match_goals(m)
        if goals is None:
            continue
        ga, gb = goals
        is_home = m.team_a_id == team_id
        my, opp = (ga, gb) if is_home else (gb, ga)
        if my > opp:
            res = "W"
        elif my < opp:
            res = "L"
        else:
            res = "D"
        opp_name = m.team_b_name if is_home else m.team_a_name
        form.games.append(
            FormGame(
                result=res,
                score=f"{my} - {opp}",
                opponent=opp_name,
                total_goals=ga + gb,
                both_scored=ga > 0 and gb > 0,
                is_home=is_home,
            )
        )
    return form


def _team_metrics(
    team_id: str,
    groups: list[GroupStanding],
    form: TeamForm,
) -> TeamMetrics:
    info = _find_standing(team_id, groups)
    met = TeamMetrics()
    mt = points = gp = ga = 0
    gd = 0
    if info is not None:
        ts = info[1]
        mt, points, gp, ga, gd = (
            ts.matches_total, ts.points, ts.goals_pro,
            ts.goals_against, ts.goal_diff,
        )
        met.rank = ts.rank
    met.matches = mt
    met.ppm = points / mt if mt else 0.0
    met.gfpm = gp / mt if mt else 0.0
    met.gapm = ga / mt if mt else 0.0

    # 近期状态分（W=3 / D=1 / L=0）→ 0~1
    if form.games:
        fp = sum(3 if g.result == "W" else 1 if g.result == "D" else 0
                 for g in form.games)
        met.form_n = fp / (len(form.games) * 3)
    else:
        met.form_n = 0.5

    ppm_n = met.ppm / 3.0
    gd_per = (gd / mt) if mt else 0.0
    gd_n = max(0.0, min(1.0, (gd_per + 3.0) / 6.0))
    met.index = 100.0 * (0.45 * ppm_n + 0.30 * met.form_n + 0.25 * gd_n)
    return met


def _win_probabilities(ia: float, ib: float) -> tuple[float, float, float]:
    """由综合指数估算 胜 / 平 / 负 概率（Elo 式 + 接近度决定平局）。"""
    diff = ia - ib
    pa_core = 1.0 / (1.0 + 10 ** (-diff / 40.0))
    draw = 0.30 * (1.0 - min(1.0, abs(diff) / 60.0))
    draw = max(0.10, min(0.32, draw))
    win_a = pa_core * (1.0 - draw)
    win_b = (1.0 - pa_core) * (1.0 - draw)
    return win_a, draw, win_b


def _implied_odds(prob: float) -> float:
    """概率 → 小数赔率，加约 6% 的庄家利润（更贴近真实盘口观感）。"""
    p = max(0.02, min(0.97, prob))
    raw = 1.0 / p
    return round(max(1.01, raw * 0.94), 2)


# ─────────────────────────────────────────────
# 叙述文本（中文，全部由数据驱动）
# ─────────────────────────────────────────────
def _fmt_form(form: TeamForm) -> str:
    if not form.games:
        return "暂无近期战绩"
    seq = "".join({"W": "胜", "D": "平", "L": "负"}[g.result] for g in form.games)
    return f"近 {form.count} 场 {seq}"


def _result_narrative(
    m: Match, ma: TeamMetrics, mb: TeamMetrics,
    fa: TeamForm, fb: TeamForm, win_a: float, draw: float, win_b: float,
) -> tuple[str, str, float]:
    """返回（标题，分析段落，概率）。"""
    if win_a >= win_b and win_a >= draw:
        fav, foe = m.team_a_name, m.team_b_name
        fav_m, foe_m = ma, mb
        fav_f = fa
        headline = f"{m.team_a_name} 胜"
        prob = win_a
    elif win_b >= win_a and win_b >= draw:
        fav, foe = m.team_b_name, m.team_a_name
        fav_m, foe_m = mb, ma
        fav_f = fb
        headline = f"{m.team_b_name} 胜"
        prob = win_b
    else:
        headline = "平局"
        prob = draw
        txt = (
            f"{m.team_a_name} 与 {m.team_b_name} 综合实力接近"
            f"（指数 {ma.index:.0f} vs {mb.index:.0f}），"
            f"近期状态亦无明显高下，本场胜负难料，平局是值得重点考虑的结果。"
        )
        return headline, txt, prob

    rank_txt = ""
    if fav_m.rank:
        rank_txt = f"小组排名第 {fav_m.rank}、"
    parts = [
        f"{fav} 综合实力指数 {fav_m.index:.0f}，高于 {foe} 的 {foe_m.index:.0f}，"
        f"{rank_txt}场均拿分 {fav_m.ppm:.1f}。"
    ]
    if fav_m.gfpm >= 1.6:
        parts.append(f"其进攻端火力充沛（场均 {fav_m.gfpm:.1f} 球），")
    if foe_m.gapm >= 1.3:
        parts.append(f"而 {foe} 防线场均失 {foe_m.gapm:.1f} 球、存在隐患，")
    parts.append(
        f"结合 {fav} {_fmt_form(fav_f)} 的走势，本场更被看好取胜。"
    )
    return headline, "".join(parts), prob


def _goals_narrative(
    m: Match, ma: TeamMetrics, mb: TeamMetrics,
    fa: TeamForm, fb: TeamForm, expected: float, over_prob: float,
) -> tuple[str, str, float]:
    over = expected >= 2.5
    headline = "进球数 大于 2.5" if over else "进球数 小于 2.5"
    prob = over_prob if over else (1.0 - over_prob)
    oa = fa.over25
    ob = fb.over25
    if over:
        txt = (
            f"两队近期攻防均偏开放：{m.team_a_name} 场均进 {ma.gfpm:.1f} / 失 "
            f"{ma.gapm:.1f}，{m.team_b_name} 场均进 {mb.gfpm:.1f} / 失 {mb.gapm:.1f}，"
            f"模型预计本场总进球约 {expected:.1f} 个。"
            f"近 5 场打出大球（≥3 球）的比例分别为 {oa}/{fa.count} 与 "
            f"{ob}/{fb.count}，本场倾向于打出 3 球或以上。"
        )
    else:
        txt = (
            f"两队整体攻防偏谨慎：{m.team_a_name} 场均进 {ma.gfpm:.1f} / 失 "
            f"{ma.gapm:.1f}，{m.team_b_name} 场均进 {mb.gfpm:.1f} / 失 {mb.gapm:.1f}，"
            f"模型预计本场总进球约 {expected:.1f} 个。"
            f"近 5 场大球比例为 {oa}/{fa.count} 与 {ob}/{fb.count}，"
            f"本场更可能是一场小比分较量。"
        )
    return headline, txt, prob


def _btts_narrative(
    m: Match, ma: TeamMetrics, mb: TeamMetrics,
    fa: TeamForm, fb: TeamForm, btts_prob: float,
) -> tuple[str, str, float]:
    yes = btts_prob >= 0.5
    headline = "双方进球 是" if yes else "双方进球 否"
    prob = btts_prob if yes else (1.0 - btts_prob)
    ba, bb = fa.btts, fb.btts
    if yes:
        txt = (
            f"双方均具备稳定的破门能力，且后防并非滴水不漏："
            f"{m.team_a_name} 场均进 {ma.gfpm:.1f} 球，{m.team_b_name} 场均进 "
            f"{mb.gfpm:.1f} 球。近 5 场「双方都进球」分别出现 {ba}/{fa.count} 与 "
            f"{bb}/{fb.count} 次，本场两队同时破门的可能性较高。"
        )
    else:
        weaker = m.team_a_name if ma.gfpm <= mb.gfpm else m.team_b_name
        txt = (
            f"至少一方进攻效率有限或对手防守稳固，"
            f"{weaker} 的进球把握存疑。近 5 场「双方都进球」仅出现 {ba}/{fa.count} "
            f"与 {bb}/{fb.count} 次，本场更可能有一方挂零。"
        )
    return headline, txt, prob


def _swot(
    name: str, met: TeamMetrics, foe: TeamMetrics, form: TeamForm,
    h2h_self_win: int, h2h_foe_win: int,
) -> dict[str, list[str]]:
    """生成一支球队的 SWOT（优势 / 劣势 / 机会 / 威胁）。"""
    S: list[str] = []
    W: list[str] = []
    O: list[str] = []
    T: list[str] = []

    if met.gfpm >= 1.6:
        S.append(f"进攻火力强（场均 {met.gfpm:.1f} 球）")
    if met.gapm <= 0.8 and met.matches:
        S.append(f"防守稳固（场均失 {met.gapm:.1f} 球）")
    if met.ppm >= 2.0:
        S.append(f"赢球能力突出（场均 {met.ppm:.1f} 分）")
    if form.wins >= max(3, form.count - 1) and form.count:
        S.append(f"近期状态火热（{form.wins} 胜）")
    if met.rank and met.rank == 1:
        S.append("小组头名领跑")

    if met.gapm >= 1.5 and met.matches:
        W.append(f"防线偏松（场均失 {met.gapm:.1f} 球）")
    if met.gfpm <= 0.8 and met.matches:
        W.append(f"进攻乏力（场均 {met.gfpm:.1f} 球）")
    if form.losses >= max(2, form.count - 1) and form.count:
        W.append(f"近期低迷（{form.losses} 负）")
    if met.matches == 0:
        W.append("缺乏小组赛数据样本")

    if foe.gapm >= 1.3 and foe.matches:
        O.append(f"对手防线场均失 {foe.gapm:.1f} 球，可加以利用")
    if foe.gfpm <= 0.9 and foe.matches:
        O.append("对手进攻效率有限，利于稳守反击")
    if h2h_self_win > h2h_foe_win:
        O.append(f"历史交锋占优（{h2h_self_win}-{h2h_foe_win}）")
    if met.index >= foe.index + 8:
        O.append("整体实力占据上风")

    if foe.gfpm >= 1.6:
        T.append(f"对手进攻犀利（场均 {foe.gfpm:.1f} 球）")
    if foe.index >= met.index + 8:
        T.append("对手综合实力更强")
    if h2h_foe_win > h2h_self_win:
        T.append(f"历史交锋落于下风（{h2h_self_win}-{h2h_foe_win}）")
    if met.gapm >= 1.3 and foe.gfpm >= 1.3:
        T.append("后防需警惕对手反扑")

    return {
        "优势": S or ["整体表现均衡"],
        "劣势": W or ["暂无明显短板"],
        "机会": O or ["需在比赛中把握细节"],
        "威胁": T or ["对手不构成明显威胁"],
    }


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────
def build_prediction(
    match: Match,
    all_matches: list[Match],
    groups: list[GroupStanding],
) -> MatchPrediction:
    """聚合一场比赛的完整赛前预测。"""
    fa = _recent_form(match.team_a_id, match.team_a_name, all_matches, match.match_id)
    fb = _recent_form(match.team_b_id, match.team_b_name, all_matches, match.match_id)
    ma = _team_metrics(match.team_a_id, groups, fa)
    mb = _team_metrics(match.team_b_id, groups, fb)

    win_a, draw, win_b = _win_probabilities(ma.index, mb.index)

    # 预期进球：本队进攻强度与对手防守弱点的折中
    eg_a = (ma.gfpm + mb.gapm) / 2 if (ma.matches or mb.matches) else 1.2
    eg_b = (mb.gfpm + ma.gapm) / 2 if (ma.matches or mb.matches) else 1.1
    expected = max(0.4, eg_a) + max(0.4, eg_b)
    # Over 2.5 概率：以预期进球围绕 2.5 做平滑映射
    over25_prob = max(0.05, min(0.95, 0.5 + (expected - 2.5) * 0.22))
    # BTTS：两队各自「至少进 1 球」的概率近似后取交集
    p_a_scores = max(0.1, min(0.95, 0.45 + (eg_a - 1.0) * 0.30))
    p_b_scores = max(0.1, min(0.95, 0.45 + (eg_b - 1.0) * 0.30))
    btts_prob = p_a_scores * p_b_scores

    # 历史交锋
    pair = {match.team_a_id, match.team_b_id}
    h2h = [
        x for x in all_matches
        if x.status == MatchStatus.PLAYED
        and {x.team_a_id, x.team_b_id} == pair
        and x.match_id != match.match_id
    ]
    a_win = b_win = drawn = 0
    for x in h2h:
        w = x.winner_id
        if w is None:
            drawn += 1
        elif w == match.team_a_id:
            a_win += 1
        elif w == match.team_b_id:
            b_win += 1

    # 三条趋势（对应截图）
    r_head, r_txt, r_prob = _result_narrative(match, ma, mb, fa, fb, win_a, draw, win_b)
    if r_head.endswith("胜") and match.team_a_name in r_head:
        market = "1X2 · 主胜"
    elif r_head.endswith("胜"):
        market = "1X2 · 客胜"
    else:
        market = "1X2 · 平局"
    g_head, g_txt, g_prob = _goals_narrative(match, ma, mb, fa, fb, expected, over25_prob)
    b_head, b_txt, b_prob = _btts_narrative(match, ma, mb, fa, fb, btts_prob)

    trends = [
        Trend(
            category="比赛结果",
            headline=r_head,
            probability=r_prob,
            narrative=r_txt,
            stat_a=f"{match.team_a_name}：{_fmt_form(fa)}",
            stat_b=f"{match.team_b_name}：{_fmt_form(fb)}",
            market=market,
            odds=_implied_odds(r_prob),
        ),
        Trend(
            category="进球数",
            headline=g_head,
            probability=g_prob,
            narrative=g_txt,
            stat_a=f"{match.team_a_name}：近 {fa.count} 场 {fa.over25} 场大球",
            stat_b=f"{match.team_b_name}：近 {fb.count} 场 {fb.over25} 场大球",
            market="进球数 " + ("大 2.5" if "大于" in g_head else "小 2.5"),
            odds=_implied_odds(g_prob),
        ),
        Trend(
            category="双方进球",
            headline=b_head,
            probability=b_prob,
            narrative=b_txt,
            stat_a=f"{match.team_a_name}：近 {fa.count} 场 {fa.btts} 场双方进球",
            stat_b=f"{match.team_b_name}：近 {fb.count} 场 {fb.btts} 场双方进球",
            market="双方进球 " + ("是" if "是" in b_head else "否"),
            odds=_implied_odds(b_prob),
        ),
    ]

    swot_a = _swot(match.team_a_name, ma, mb, fa, a_win, b_win)
    swot_b = _swot(match.team_b_name, mb, ma, fb, b_win, a_win)

    if win_a > win_b and win_a >= draw:
        verdict = f"模型看好 {match.team_a_name} 取胜（{round(win_a * 100)}%）"
    elif win_b > win_a and win_b >= draw:
        verdict = f"模型看好 {match.team_b_name} 取胜（{round(win_b * 100)}%）"
    else:
        verdict = f"势均力敌，平局风险偏高（{round(draw * 100)}%）"

    info = _find_standing(match.team_a_id, groups) or _find_standing(match.team_b_id, groups)
    group_name = info[0] if info else ""

    return MatchPrediction(
        match=match,
        metrics_a=ma,
        metrics_b=mb,
        form_a=fa,
        form_b=fb,
        win_a=win_a,
        draw=draw,
        win_b=win_b,
        expected_goals=expected,
        over25_prob=over25_prob,
        btts_prob=btts_prob,
        trends=trends,
        swot_a=swot_a,
        swot_b=swot_b,
        h2h_total=len(h2h),
        h2h_a_win=a_win,
        h2h_draw=drawn,
        h2h_b_win=b_win,
        verdict=verdict,
        group_name=group_name,
        exp_goals_a=max(0.4, eg_a),
        exp_goals_b=max(0.4, eg_b),
    )
