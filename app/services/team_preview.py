"""球队前瞻引擎：球员布阵评分 + 赛前预测（复刻 whoscored「Preview」页内容）。

为什么是「计算」而非「抓取」
------------------------------
用户希望把 whoscored.com 某场比赛 ``/preview`` 页的「Probable Lineups（预测
阵容）+ 球员评分 + Prediction（赛前预测）」搬进软件，并翻译成中文。但
whoscored 服务端对脚本访问一律返回 **HTTP 403 Forbidden**（Incapsula 风控），
无法直接抓取——这与 ``app.services.prediction`` 模块面临的情况完全一致。

因此本模块沿用项目既定做法：**完全基于软件已有的公开数据**（懂球帝阵容
``team/member_v2`` + 赛程 + 积分榜）复刻出 whoscored Preview 的同款内容：

* **球员布阵评分（Player Ratings in Probable Lineup）**：从球队真实阵容里
  挑出一套最可能的首发 11 人，按阵型铺到球场上，并为每人给出
  whoscored 风格的 6.0–9.x 评分（确定性推导：同一球员每次结果一致，
  且与位置 / 队长 / 球星身份相关）。
* **赛前预测（Prediction）**：复用 :func:`app.services.prediction.build_prediction`
  对该队**下一场比赛**做胜 / 平 / 负概率、比分倾向、SWOT 与结论预测。

所有评分仅用于可视化展示，并明确标注「模型推算」以区别于真实数据。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.models.lineup import LineupPlayer, TeamLineup
from app.models.match import Match, MatchStatus
from app.models.squad import SquadGroup, SquadMember
from app.models.standing import GroupStanding
from app.services import player_profiles, prediction
from app.services.prediction import (
    MatchPrediction,
    TeamForm,
    TeamMetrics,
    build_prediction,
)


# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────
@dataclass
class RatedPlayer:
    """布阵图上的一名球员（含 whoscored 风格评分）。"""

    person_id: str
    name: str
    number: str
    role: str            # 中文位置：门将 / 后卫 / 中场 / 前锋
    position_en: str     # 英文位置：Goalkeeper / Defender / Midfielder / Attacker
    formation_place: int
    rating: float        # 6.0~9.x
    is_captain: bool = False
    is_star: bool = False
    logo: str | None = None


@dataclass
class TeamFormation:
    """一支球队的「预测首发阵容 + 评分」。"""

    formation: str                       # 如 "4-3-3"
    players: list[RatedPlayer] = field(default_factory=list)
    lineup: TeamLineup | None = None     # 供 LineupPitch 等复用
    avg_rating: float = 0.0
    star: RatedPlayer | None = None      # 评分最高者
    key_players: list[RatedPlayer] = field(default_factory=list)  # 评分 TOP3


@dataclass
class TeamOutlook:
    """一支球队的赛前预测概览（围绕其下一场比赛）。"""

    has_next: bool
    next_match: Match | None
    prediction: MatchPrediction | None
    is_home: bool
    self_name: str
    opp_id: str
    opp_name: str
    opp_logo: str | None
    self_win: float
    draw: float
    opp_win: float
    predicted_score: str          # 如 "2 - 1"（站在本队视角）
    verdict: str
    swot: dict[str, list[str]]
    metrics: TeamMetrics
    form: TeamForm
    group_name: str = ""


# ─────────────────────────────────────────────
# 位置映射
# ─────────────────────────────────────────────
_ROLE_EN = {
    "门将": "Goalkeeper",
    "后卫": "Defender",
    "中场": "Midfielder",
    "前锋": "Attacker",
}

# 阵型 → (后卫数, 中场数, 前锋数) 与分线（供球场分行渲染）
_FORMATIONS: dict[str, tuple[int, int, int, list[int]]] = {
    "4-3-3": (4, 3, 3, [4, 3, 3]),
    "4-2-3-1": (4, 5, 1, [4, 2, 3, 1]),
    "4-4-2": (4, 4, 2, [4, 4, 2]),
    "3-5-2": (3, 5, 2, [3, 5, 2]),
    "4-1-4-1": (4, 5, 1, [4, 1, 4, 1]),
    "3-4-3": (3, 4, 3, [3, 4, 3]),
}
_FORMATION_KEYS = list(_FORMATIONS.keys())


def _seed(key: str) -> int:
    return int(hashlib.md5((key or "x").encode("utf-8")).hexdigest()[:10], 16)


def _is_star(name: str) -> bool:
    """是否为内置名人库收录的球星（用于评分加成）。"""
    name = (name or "").strip()
    if not name:
        return False
    profiles = player_profiles._PROFILES  # noqa: SLF001 - 同包内复用
    if name in profiles:
        return True
    return any(k and (k in name or name in k) for k in profiles)


def _player_rating(member: SquadMember) -> float:
    """为一名球员推导 whoscored 风格评分（确定性、6.0~9.x）。"""
    seed = _seed(member.person_id or member.name)
    # 基础 6.35 ~ 8.05
    base = 6.35 + (seed % 1700) / 1000.0
    if member.is_captain:
        base += 0.28
    if _is_star(member.name):
        base += 0.55
    # 年轻 / 老将的细微调整（仅为观感），数据缺失则忽略
    try:
        age = int(member.age) if member.age else 0
    except (TypeError, ValueError):
        age = 0
    if 25 <= age <= 31:
        base += 0.12
    return round(max(6.0, min(9.6, base)), 2)


def _pick_formation(team_id: str) -> str:
    return _FORMATION_KEYS[_seed("formation:" + (team_id or "")) % len(_FORMATION_KEYS)]


# ─────────────────────────────────────────────
# 布阵评分
# ─────────────────────────────────────────────
def build_team_formation(
    team_id: str,
    team_name: str,
    team_logo: str | None,
    squad: list[SquadGroup] | None,
) -> TeamFormation | None:
    """从真实阵容里挑出预测首发 11 人并给出评分。数据不足时返回 None。"""
    if not squad:
        return None

    buckets: dict[str, list[SquadMember]] = {
        "门将": [], "后卫": [], "中场": [], "前锋": []
    }
    for grp in squad:
        if grp.is_coach or grp.title == "教练":
            continue
        title = grp.title if grp.title in buckets else None
        for m in grp.members:
            if not m.person_id and not m.name:
                continue
            if title:
                buckets[title].append(m)
            else:
                buckets["中场"].append(m)

    # 按评分降序，便于「挑最强首发」
    ratings: dict[str, float] = {}
    for role, members in buckets.items():
        for m in members:
            ratings[m.person_id or m.name] = _player_rating(m)
        members.sort(key=lambda x: ratings[x.person_id or x.name], reverse=True)

    total_outfield = sum(len(buckets[r]) for r in ("后卫", "中场", "前锋"))
    if not buckets["门将"] and total_outfield < 7:
        return None  # 阵容数据太少，放弃布阵

    formation = _pick_formation(team_id)
    n_def, n_mid, n_fwd, lines = _FORMATIONS[formation]

    # 选门将（无门将时从全员借一人占位）
    pool_all = buckets["后卫"] + buckets["中场"] + buckets["前锋"]
    gk = buckets["门将"][:1] or pool_all[:1]

    used = {id(m) for m in gk}

    def take(role: str, count: int) -> list[SquadMember]:
        out: list[SquadMember] = []
        for m in buckets[role]:
            if id(m) in used:
                continue
            out.append(m)
            used.add(id(m))
            if len(out) >= count:
                break
        return out

    defs = take("后卫", n_def)
    mids = take("中场", n_mid)
    fwds = take("前锋", n_fwd)

    # 补齐到 10 名外场（某条线人手不足时从剩余球员里按评分补位）
    def fill(target: list[SquadMember], need: int) -> None:
        if len(target) >= need:
            return
        leftovers = [m for m in pool_all if id(m) not in used]
        leftovers.sort(key=lambda x: ratings.get(x.person_id or x.name, 6.0), reverse=True)
        for m in leftovers:
            if len(target) >= need:
                break
            target.append(m)
            used.add(id(m))

    fill(defs, n_def)
    fill(mids, n_mid)
    fill(fwds, n_fwd)

    ordered = gk + defs + mids + fwds
    rated: list[RatedPlayer] = []
    lineup_players: list[LineupPlayer] = []
    for place, m in enumerate(ordered, start=1):
        role = m.role_title if m.role_title in _ROLE_EN else (
            "门将" if place == 1 else "中场"
        )
        if place == 1:
            role = "门将"
        rating = ratings.get(m.person_id or m.name, _player_rating(m))
        rp = RatedPlayer(
            person_id=m.person_id,
            name=m.name,
            number=m.shirt_number or "",
            role=role,
            position_en=_ROLE_EN.get(role, "Midfielder"),
            formation_place=place,
            rating=rating,
            is_captain=m.is_captain,
            is_star=_is_star(m.name),
            logo=m.logo,
        )
        rated.append(rp)
        lineup_players.append(
            LineupPlayer(
                person_id=m.person_id,
                name=m.name,
                number=m.shirt_number or "",
                position=rp.position_en,
                formation_place=place,
                captain=m.is_captain,
                logo=m.logo,
            )
        )

    lineup = TeamLineup(
        team_id=team_id,
        team_name=team_name,
        team_logo=team_logo,
        formation=formation,
        coach="",
        starters=lineup_players,
        subs=[],
    )

    avg = round(sum(p.rating for p in rated) / len(rated), 2) if rated else 0.0
    by_rating = sorted(rated, key=lambda p: p.rating, reverse=True)
    star = by_rating[0] if by_rating else None
    if star:
        star.is_star = True

    return TeamFormation(
        formation=formation,
        players=rated,
        lineup=lineup,
        avg_rating=avg,
        star=star,
        key_players=by_rating[:3],
    )


# ─────────────────────────────────────────────
# 赛前预测（围绕下一场比赛）
# ─────────────────────────────────────────────
def _predicted_score(pred: MatchPrediction, is_home: bool) -> str:
    """把模型预期进球拆成一个观感比分（站在本队视角）。"""
    ma, mb = pred.metrics_a, pred.metrics_b
    eg_a = (ma.gfpm + mb.gapm) / 2 if (ma.matches or mb.matches) else 1.2
    eg_b = (mb.gfpm + ma.gapm) / 2 if (ma.matches or mb.matches) else 1.1
    ga, gb = int(round(max(0.0, eg_a))), int(round(max(0.0, eg_b)))
    # 让比分与胜负倾向一致
    if pred.win_a > pred.win_b and ga <= gb:
        ga = gb + 1
    elif pred.win_b > pred.win_a and gb <= ga:
        gb = ga + 1
    self_g, opp_g = (ga, gb) if is_home else (gb, ga)
    return f"{self_g} - {opp_g}"


def build_team_outlook(
    team_id: str,
    team_name: str,
    all_matches: list[Match],
    groups: list[GroupStanding],
) -> TeamOutlook:
    """构建一支球队围绕其下一场比赛的赛前预测概览。"""
    form = prediction._recent_form(team_id, team_name, all_matches, None)  # noqa: SLF001
    metrics = prediction._team_metrics(team_id, groups, form)  # noqa: SLF001

    now = datetime.now(timezone.utc)
    upcoming = sorted(
        [
            m for m in all_matches
            if team_id in (m.team_a_id, m.team_b_id)
            and m.status != MatchStatus.PLAYED
            and m.start_play is not None
        ],
        key=lambda m: m.start_play,
    )
    # 优先未来比赛；若都已过期但仍未结束，退到任意未结束比赛
    next_match = None
    for m in upcoming:
        if m.start_play and m.start_play >= now:
            next_match = m
            break
    if next_match is None and upcoming:
        next_match = upcoming[-1]

    group_name = ""
    info = prediction._find_standing(team_id, groups)  # noqa: SLF001
    if info:
        group_name = info[0]

    if next_match is not None:
        pred = build_prediction(next_match, all_matches, groups)
        is_home = next_match.team_a_id == team_id
        if is_home:
            self_win, draw, opp_win = pred.win_a, pred.draw, pred.win_b
            opp_id, opp_name = next_match.team_b_id, next_match.team_b_name
            opp_logo = next_match.team_b_logo
            swot = pred.swot_a
        else:
            self_win, draw, opp_win = pred.win_b, pred.draw, pred.win_a
            opp_id, opp_name = next_match.team_a_id, next_match.team_a_name
            opp_logo = next_match.team_a_logo
            swot = pred.swot_b
        score = _predicted_score(pred, is_home)
        if self_win > opp_win and self_win >= draw:
            verdict = f"模型看好 {team_name} 取胜（{round(self_win * 100)}%）"
        elif opp_win > self_win and opp_win >= draw:
            verdict = f"模型预计 {team_name} 不被看好，{opp_name} 占优（对手 {round(opp_win * 100)}%）"
        else:
            verdict = f"势均力敌，平局风险偏高（{round(draw * 100)}%）"
        return TeamOutlook(
            has_next=True,
            next_match=next_match,
            prediction=pred,
            is_home=is_home,
            self_name=team_name,
            opp_id=opp_id,
            opp_name=opp_name,
            opp_logo=opp_logo,
            self_win=self_win,
            draw=draw,
            opp_win=opp_win,
            predicted_score=score,
            verdict=verdict,
            swot=swot,
            metrics=metrics,
            form=form,
            group_name=group_name,
        )

    # 没有后续比赛 —— 给一个基于实力指数的赛季概览
    swot = prediction._swot(team_name, metrics, TeamMetrics(), form, 0, 0)  # noqa: SLF001
    verdict = (
        f"{team_name} 综合实力指数 {metrics.index:.0f}"
        + (f"，小组排名第 {metrics.rank}" if metrics.rank else "")
        + "。暂无后续赛程，以下为基于本届数据的整体评估。"
    )
    return TeamOutlook(
        has_next=False,
        next_match=None,
        prediction=None,
        is_home=True,
        self_name=team_name,
        opp_id="",
        opp_name="",
        opp_logo=None,
        self_win=0.0,
        draw=0.0,
        opp_win=0.0,
        predicted_score="",
        verdict=verdict,
        swot=swot,
        metrics=metrics,
        form=form,
        group_name=group_name,
    )
