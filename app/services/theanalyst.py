"""The Analyst（Opta 超级计算机）数据服务。

提供两类数据：

1. **夺冠 / 出线概率**（``TournamentProbabilities``）——
   优先从 Opta「赛事模拟」实时接口拉取（与 theanalyst.com 的预测页同源），
   失败时回退到 :mod:`app.services.theanalyst_data` 里的离线快照。每支球队含
   「夺冠概率」「进决赛概率」，并附小组、积分等信息。

2. **逐场赛前预测**（``MatchPreview``）——
   取自 :mod:`app.services.theanalyst_data` 中由预览文章生成的快照：Opta 超算
   25,000 次赛前模拟的胜 / 平 / 负概率、关键事实（Key Insights）与预测正文。
   按参赛双方（无视主客顺序）匹配，用于「即将开赛的球队信息」展示。

数据来源：theanalyst.com / Opta（api.performfeeds.com）。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.api.client import ApiClient
from app.models.match import Match
from app.services.theanalyst_data import THEANALYST_MATCHES, THEANALYST_TOURNAMENT

log = logging.getLogger(__name__)

# ── Opta 赛事模拟实时接口（与 theanalyst.com 预测页同源）──
_OUTLET = "1mjq6w6ezkxe611ykkj8rgz7f1"
_TMCL = "873cbl9cd9butm4air0mugxzo"
_SIM_URL = (
    f"https://api.performfeeds.com/soccerdata/seasonandtournamentsimulations/{_OUTLET}"
)
_REFERER = {"Referer": "https://theanalyst.com/", "Accept": "application/json"}
#: 模拟概率更新不频繁（每场比赛后）—— 缓存 30 分钟。
_CACHE_TTL = 60 * 30

#: 英文队名 → 中文（与项目内既有中文名一致；实时接口用英文名）。
_EN_TO_CN = {
    "Argentina": "阿根廷", "Austria": "奥地利", "France": "法国", "Iraq": "伊拉克",
    "Spain": "西班牙", "Saudi Arabia": "沙特阿拉伯", "England": "英格兰",
    "Croatia": "克罗地亚", "Ghana": "加纳", "Panama": "巴拿马", "Portugal": "葡萄牙",
    "Uzbekistan": "乌兹别克斯坦", "DR Congo": "刚果民主共和国",
    "Congo DR": "刚果民主共和国", "Germany": "德国", "Ivory Coast": "科特迪瓦",
    "Norway": "挪威", "Senegal": "塞内加尔", "Brazil": "巴西", "Haiti": "海地",
    "Morocco": "摩洛哥", "Scotland": "苏格兰", "Netherlands": "荷兰", "Sweden": "瑞典",
    "Japan": "日本", "Tunisia": "突尼斯", "Belgium": "比利时", "Iran": "伊朗",
    "Switzerland": "瑞士", "Canada": "加拿大", "Bosnia-Herzegovina": "波黑",
    "Qatar": "卡塔尔", "Mexico": "墨西哥", "South Korea": "韩国",
    "Korea Republic": "韩国", "Czechia": "捷克", "Czech Republic": "捷克",
    "South Africa": "南非", "USA": "美国", "United States": "美国",
    "Australia": "澳大利亚", "Colombia": "哥伦比亚", "Uruguay": "乌拉圭",
    "Cape Verde": "佛得角", "Jordan": "约旦", "Algeria": "阿尔及利亚",
    "New Zealand": "新西兰", "Egypt": "埃及", "Ecuador": "厄瓜多尔",
    "Curacao": "库拉索", "Curaçao": "库拉索", "Turkiye": "土耳其",
    "Türkiye": "土耳其", "Turkey": "土耳其", "Paraguay": "巴拉圭",
}


def _cn(en: str) -> str:
    en = (en or "").strip()
    if en in _EN_TO_CN:
        return _EN_TO_CN[en]
    for k, v in _EN_TO_CN.items():
        if k.lower() == en.lower():
            return v
    return en


# ════════════════════════════════════════════════════════════════════
#  数据结构
# ════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class TeamProbability:
    """一支球队的赛事模拟概率。"""

    team_cn: str
    team_en: str
    code: str
    group: str
    win_pct: float          # 夺冠概率（%）
    final_pct: float        # 进决赛概率（%）
    points: int = 0
    played: int = 0
    qualify_pct: float = 0.0   # 小组出线 / 晋级淘汰赛概率（%）；0 视为无数据


@dataclass(frozen=True)
class MatchPreview:
    """一场比赛的 Opta 赛前预测（25,000 次模拟）。"""

    home_cn: str
    away_cn: str
    home_pct: float | None  # 主胜概率（%）
    draw_pct: float | None  # 平局概率（%）
    away_pct: float | None  # 客胜概率（%）
    insights: list[str] = field(default_factory=list)
    prediction: str = ""
    url: str = ""
    summary_cn: str = ""                       # 中文综述
    analysis_cn: list[tuple[str, str]] = field(default_factory=list)  # [(小标题, 正文)]

    @property
    def has_probabilities(self) -> bool:
        return self.home_pct is not None or self.away_pct is not None


# ════════════════════════════════════════════════════════════════════
#  解析实时接口
# ════════════════════════════════════════════════════════════════════
def parse_simulations(data: dict) -> list[TeamProbability]:
    """纯函数：把 Opta 赛事模拟响应解析为按夺冠概率降序的球队列表。

    决赛阶段 contestant 的 typeId 2 = 夺冠概率、typeId 1 = 进决赛概率；
    小组赛 division 的 ranking 提供小组 / 积分 / 已赛场次。响应结构异常时返回
    空列表（调用方据此回退离线快照）。
    """
    if not isinstance(data, dict):
        return []
    stages = data.get("stages", {}).get("stage")
    if not isinstance(stages, list):
        return []
    by_name = {s.get("name"): s for s in stages if isinstance(s, dict)}

    # 决赛阶段：夺冠 / 进决赛概率
    win_final: dict[str, tuple[float, float]] = {}
    final = by_name.get("Final", {})
    contestants = (final.get("contestants") or {}).get("contestant") or []
    for c in contestants:
        preds = {}
        try:
            for x in c["predictions"][0]["predicted"]:
                preds[x["typeId"]] = x["value"]
        except (KeyError, IndexError, TypeError):
            continue
        win_final[c.get("name", "")] = (
            _to_pct(preds.get("2")),
            _to_pct(preds.get("1")),
        )

    # 小组赛 division：小组 / 积分 / 场次
    out: dict[str, TeamProbability] = {}
    gs = by_name.get("Group Stage", {})
    divisions = gs.get("division") or []
    for grp in divisions:
        gname = grp.get("groupName", "")
        for r in grp.get("ranking", []):
            name = r.get("contestantName", "")
            if not name:
                continue
            win, fin = win_final.get(name, (0.0, 0.0))
            tp = TeamProbability(
                team_cn=_cn(name),
                team_en=name,
                code=r.get("contestantCode", ""),
                group=gname,
                win_pct=round(win, 2),
                final_pct=round(fin, 2),
                points=int(r.get("points", 0) or 0),
                played=int(r.get("matchesPlayed", 0) or 0),
                qualify_pct=_qualify_from_ranking(r),
            )
            # 去重：同队若多次出现取夺冠概率更高者
            prev = out.get(tp.team_en)
            if prev is None or tp.win_pct >= prev.win_pct:
                out[tp.team_en] = tp

    teams = list(out.values())
    teams.sort(key=lambda t: -t.win_pct)
    return teams


def _to_pct(value) -> float:
    if value is None:
        return 0.0
    try:
        return float(str(value).rstrip("%"))
    except (TypeError, ValueError):
        return 0.0


def _qualify_from_ranking(entry: dict) -> float:
    """从小组排名条目的 ``overallPredictions`` 求「出线 / 晋级淘汰赛概率」(%)。

    Opta 在每支小组球队的 ``overallPredictions[0].rankPrediction`` 列出其各种最终
    名次的概率，其中 ``rankStatus`` 含「16th Finals」的项即「晋级 1/16 决赛（淘汰
    赛）」——直接出线 + 凭最佳第三名出线（「Possible 16th Finals」）相加即总出线
    概率（与 theanalyst.com 预测页一致）。解析失败返回 0。
    """
    try:
        op = entry.get("overallPredictions") or []
        if not op:
            return 0.0
        rp = op[0].get("rankPrediction") or []
    except (AttributeError, IndexError, TypeError):
        return 0.0
    total = 0.0
    for x in rp:
        if not isinstance(x, dict):
            continue
        status = str(x.get("rankStatus") or "")
        if "16th Finals" in status:   # 含「16th Finals」与「Possible 16th Finals」
            total += _to_pct(x.get("value"))
    return min(100.0, round(total, 2))


def _snapshot_teams() -> list[TeamProbability]:
    """离线快照 → 球队概率列表（去重并按夺冠概率降序）。"""
    out: dict[str, TeamProbability] = {}
    for r in THEANALYST_TOURNAMENT:
        tp = TeamProbability(
            team_cn=r.get("team_cn", ""),
            team_en=r.get("team_en", ""),
            code=r.get("code", ""),
            group=r.get("group", ""),
            win_pct=float(r.get("win_pct", 0.0) or 0.0),
            final_pct=float(r.get("final_pct", 0.0) or 0.0),
            points=int(r.get("points", 0) or 0),
            played=int(r.get("played", 0) or 0),
            qualify_pct=float(r.get("qualify_pct", 0.0) or 0.0),
        )
        prev = out.get(tp.team_en)
        if prev is None or tp.win_pct >= prev.win_pct:
            out[tp.team_en] = tp
    teams = list(out.values())
    teams.sort(key=lambda t: -t.win_pct)
    return teams


# ════════════════════════════════════════════════════════════════════
#  服务单例
# ════════════════════════════════════════════════════════════════════
class TheAnalyst:
    """The Analyst（Opta）数据服务（单例）。"""

    _instance: "TheAnalyst | None" = None

    def __init__(self) -> None:
        self._teams: list[TeamProbability] = []
        self._loaded_live = False

    @classmethod
    def instance(cls) -> "TheAnalyst":
        if cls._instance is None:
            cls._instance = TheAnalyst()
        return cls._instance

    async def refresh(self, *, force: bool = False) -> bool:
        """异步拉取最新赛事模拟概率；成功返回 ``True``，失败保留上一份。"""
        try:
            data = await ApiClient.instance().get_json(
                _SIM_URL,
                params={"tmcl": _TMCL, "_fmt": "json", "_rt": "c"},
                headers=_REFERER,
                use_common_params=False,
                cache_ttl=_CACHE_TTL,
                force=force,
            )
        except Exception as exc:  # pragma: no cover - 网络异常
            log.warning("The Analyst 赛事模拟拉取失败：%s", exc)
            return False
        teams = parse_simulations(data)
        if teams:
            self._teams = teams
            self._loaded_live = True
            return True
        return False

    def championship_ranking(self, top: int | None = None) -> list[TeamProbability]:
        """夺冠概率排行榜（降序）。实时数据缺失时回退离线快照。"""
        teams = self._teams if self._teams else _snapshot_teams()
        return teams[:top] if top else list(teams)

    def qualifying_ranking(self, top: int | None = None) -> list[TeamProbability]:
        """进决赛概率排行榜（降序）。"""
        teams = self.championship_ranking()
        ranked = sorted(teams, key=lambda t: -t.final_pct)
        return ranked[:top] if top else ranked

    def groups(self) -> dict[str, list[TeamProbability]]:
        """按小组分组（组内按夺冠概率降序）。"""
        out: dict[str, list[TeamProbability]] = {}
        for t in self.championship_ranking():
            out.setdefault(t.group or "—", []).append(t)
        return out

    def qualification_map(self) -> dict[str, float]:
        """中文队名 → 出线 / 晋级概率（分数 ``[0,1]``）。

        仅收录有明确出线概率（``qualify_pct > 0``）的球队；供首页小组积分榜 /
        预测页「晋级概率」直接取用（与 theanalyst.com 同源）。
        """
        out: dict[str, float] = {}
        for t in self.championship_ranking():
            if t.qualify_pct and t.qualify_pct > 0:
                out[t.team_cn] = max(0.0, min(1.0, t.qualify_pct / 100.0))
        return out

    @property
    def is_live(self) -> bool:
        return self._loaded_live


# ════════════════════════════════════════════════════════════════════
#  逐场赛前预测（离线快照，按队名匹配）
# ════════════════════════════════════════════════════════════════════
_PREVIEW_DB: dict[frozenset[str], dict] = {
    frozenset({r["home_cn"], r["away_cn"]}): r for r in THEANALYST_MATCHES
}


def get_match_preview(match: Match) -> MatchPreview | None:
    """按参赛双方（无视主客顺序）匹配 Opta 赛前预测；无则返回 ``None``。

    若快照里的主客顺序与本场相反，会自动翻转左右概率以对齐当前比赛。
    """
    key = frozenset({match.team_a_name, match.team_b_name})
    raw = _PREVIEW_DB.get(key)
    if raw is None:
        return None
    flip = match.team_a_name == raw["away_cn"]
    home_cn = raw["away_cn"] if flip else raw["home_cn"]
    away_cn = raw["home_cn"] if flip else raw["away_cn"]
    hp = raw["away_pct"] if flip else raw["home_pct"]
    ap = raw["home_pct"] if flip else raw["away_pct"]
    return MatchPreview(
        home_cn=home_cn,
        away_cn=away_cn,
        home_pct=hp,
        draw_pct=raw.get("draw_pct"),
        away_pct=ap,
        insights=list(raw.get("insights") or []),
        prediction=raw.get("prediction", ""),
        url=raw.get("url", ""),
        summary_cn=raw.get("summary_cn", ""),
        analysis_cn=[tuple(b) for b in (raw.get("analysis_cn") or [])
                     if isinstance(b, (list, tuple)) and len(b) == 2],
    )
