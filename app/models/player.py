"""球员 / 球队排行榜模型。

懂球帝数据榜接口：

* 球员榜 ``person_ranking``（射手 / 助攻 / 射门 / 传球 / 抢断 / 门将 / 评分…）
* 球队榜 ``team_ranking``（进球 / 失球 / 角球 / 越位 / 身价…）

用 :class:`RankingType` 统一描述每个榜单的「接口 type 值 + 中文名 +
图标 + 单位 + 所属分类 + 适用范围(球员/球队/两者)」。

数值解析
--------
* **评分（rating）**：``"9.6"`` 浮点字符串 —— 用 :func:`_to_float` 保留小数。
* **传球成功率（pass_accuracy）**：球员返回 ``"99"``、球队返回 ``"92%"``，
  统一补 ``%``。
* **身价（market_value）**：返回 ``"15.2亿"`` 这类带中文量词的字符串 ——
  ``display`` 原样展示，``value`` 解析出数值（亿/万）用于进度条排序。

模型同时保留：``value``（浮点，进度条/排序）、``display``（展示文本，
如 ``"9.6"`` / ``"99%"`` / ``"15.2亿"``）、``count``（向后兼容的整数）。
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(_to_float(v, float(default)))
    except (TypeError, ValueError):
        return default


def _to_float(v: Any, default: float = 0.0) -> float:
    """把接口的计数字段解析为浮点数。

    兼容百分号（``"92%"``）与中文量词（``"15.2亿"`` / ``"800万"``）。
    """
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    if not s:
        return default
    mult = 1.0
    if s.endswith("%"):
        s = s[:-1]
    elif s.endswith("亿"):
        s, mult = s[:-1], 1e8
    elif s.endswith("万"):
        s, mult = s[:-1], 1e4
    try:
        return float(s) * mult
    except ValueError:
        return default


# 适用范围
_PLAYER = "player"
_TEAM = "team"
_BOTH = "both"

# ── 榜单元信息：type 值 → (中文名, 图标, 单位文案, 分类, 英文副标题, 适用范围) ──
#   「单位文案」即展示在排行数值下方的标注（网站对应的项目名，替代笼统的「次」）。
#   定义顺序即各分类内的展示顺序。
_RANKING_META: dict[str, tuple[str, str, str, str, str, str]] = {
    # 进攻
    "goals":              ("射手榜", "⚽", "进球", "进攻", "TOP SCORERS", _BOTH),
    "penalty_goals":      ("点球", "🎯", "点球", "进攻", "PENALTY GOALS", _TEAM),
    "shots":              ("射门", "🎯", "射门", "进攻", "SHOTS", _BOTH),
    "shots_on_target":    ("射正", "🥅", "射正", "进攻", "SHOTS ON TARGET", _BOTH),
    "hit_woodwork":       ("击中门框", "🪵", "中框", "进攻", "WOODWORK", _TEAM),
    "offsides":           ("越位", "🚩", "越位", "进攻", "OFFSIDES", _TEAM),
    "corners":            ("角球", "🏁", "角球", "进攻", "CORNERS", _TEAM),
    "big_chance_missed":  ("错失绝佳机会", "😱", "错失", "进攻", "BIG CHANCES MISSED", _BOTH),
    # 创造
    "assists":            ("助攻榜", "🅰️", "助攻", "创造", "TOP ASSISTS", _BOTH),
    "key_passes":         ("关键传球", "🔑", "关键传球", "创造", "KEY PASSES", _BOTH),
    "big_chances":        ("创造进球机会", "🎯", "机会", "创造", "BIG CHANCES CREATED", _TEAM),
    # 传球
    "passes":             ("传球", "🔁", "传球", "传球", "PASSES", _BOTH),
    "pass_accuracy":      ("传球成功率", "🎯", "成功率", "传球", "PASS ACCURACY", _BOTH),
    "long_balls":         ("长传", "🚀", "长传", "传球", "LONG BALLS", _BOTH),
    "success_long_balls": ("成功长传", "🎯", "成功长传", "传球", "ACCURATE LONG BALLS", _BOTH),
    "crosses":            ("传中", "✈️", "传中", "传球", "CROSSES", _BOTH),
    "success_crosses":    ("成功传中", "🎯", "成功传中", "传球", "ACCURATE CROSSES", _BOTH),
    "touches":            ("触球", "👟", "触球", "传球", "TOUCHES", _BOTH),
    # 过人
    "dribbles_attempted": ("尝试过人", "🌀", "尝试过人", "过人", "DRIBBLES ATTEMPTED", _BOTH),
    "dribbles_won":       ("成功过人", "💫", "成功过人", "过人", "SUCCESSFUL DRIBBLES", _BOTH),
    "fouled":             ("被犯规", "🆘", "被犯规", "过人", "FOULS WON", _BOTH),
    "dispossessed":       ("丢失球权", "💨", "丢球权", "过人", "DISPOSSESSED", _BOTH),
    # 防守
    "goal_against":       ("失球", "🥅", "失球", "防守", "GOALS CONCEDED", _TEAM),
    "goal_own":           ("乌龙球", "🙈", "乌龙", "防守", "OWN GOALS", _TEAM),
    "tackles":            ("抢断", "🛡", "抢断", "防守", "TACKLES", _BOTH),
    "interceptions":      ("拦截", "🚧", "拦截", "防守", "INTERCEPTIONS", _BOTH),
    "clearances":         ("解围", "🧹", "解围", "防守", "CLEARANCES", _BOTH),
    "last_man_tackle":    ("防线最后一人抢断", "🚨", "最后一抢", "防守", "LAST MAN TACKLES", _BOTH),
    "was_dribbled":       ("被过", "🌀", "被过", "防守", "DRIBBLED PAST", _BOTH),
    # 对抗
    "aerials":            ("争顶总数", "🆙", "争顶", "对抗", "AERIAL DUELS", _BOTH),
    "aerials_won":        ("争顶成功", "🛫", "争顶成功", "对抗", "AERIAL DUELS WON", _BOTH),
    "ground_duels":       ("地面争抢", "🤼", "地面争抢", "对抗", "GROUND DUELS", _BOTH),
    "ground_duels_won":   ("地面争抢成功", "🤝", "争抢成功", "对抗", "GROUND DUELS WON", _BOTH),
    # 纪律 / 失误
    "yellow_cards":       ("黄牌榜", "🟨", "黄牌", "纪律", "MOST YELLOW CARDS", _BOTH),
    "red_cards":          ("红牌榜", "🟥", "红牌", "纪律", "MOST RED CARDS", _BOTH),
    "fouls":              ("犯规", "🚫", "犯规", "纪律", "FOULS", _BOTH),
    "error_lead_to_goal": ("失误导致丢球", "❌", "失误丢球", "纪律", "ERRORS LEADING TO GOAL", _BOTH),
    "error_lead_to_shot": ("失误导致射门", "⚠️", "失误送射", "纪律", "ERRORS LEADING TO SHOT", _BOTH),
    # 门将
    "saves":              ("扑救", "🧤", "扑救", "门将", "SAVES", _BOTH),
    "box_shot_saves":     ("禁区射门扑救", "🧤", "禁区扑救", "门将", "SAVES IN BOX", _BOTH),
    "runs_out":           ("出击成功", "🏃", "出击", "门将", "SUCCESSFUL RUNS OUT", _BOTH),
    "claims_high":        ("出击摘高球", "🙌", "摘高球", "门将", "HIGH CLAIMS", _BOTH),
    "punches":            ("拳击球", "🥊", "拳击", "门将", "PUNCHES", _BOTH),
    # 综合
    "rating":             ("评分", "⭐", "分", "综合", "AVERAGE RATING", _BOTH),
    "market_value":       ("身价", "💰", "", "综合", "MARKET VALUE", _TEAM),
}

# 分类展示顺序
RANKING_CATEGORY_ORDER: tuple[str, ...] = (
    "进攻", "创造", "传球", "过人", "防守", "对抗", "纪律", "门将", "综合",
)

# 以百分比展示的榜单（展示时补 "%"）
_PERCENT_TYPES = {"pass_accuracy"}


class RankingType(str, Enum):
    # 进攻
    GOALS = "goals"
    PENALTY_GOALS = "penalty_goals"
    SHOTS = "shots"
    SHOTS_ON_TARGET = "shots_on_target"
    HIT_WOODWORK = "hit_woodwork"
    OFFSIDES = "offsides"
    CORNERS = "corners"
    BIG_CHANCE_MISSED = "big_chance_missed"
    # 创造
    ASSISTS = "assists"
    KEY_PASSES = "key_passes"
    BIG_CHANCES = "big_chances"
    # 传球
    PASSES = "passes"
    PASS_ACCURACY = "pass_accuracy"
    LONG_BALLS = "long_balls"
    SUCCESS_LONG_BALLS = "success_long_balls"
    CROSSES = "crosses"
    SUCCESS_CROSSES = "success_crosses"
    TOUCHES = "touches"
    # 过人
    DRIBBLES_ATTEMPTED = "dribbles_attempted"
    DRIBBLES_WON = "dribbles_won"
    FOULED = "fouled"
    DISPOSSESSED = "dispossessed"
    # 防守
    GOAL_AGAINST = "goal_against"
    GOAL_OWN = "goal_own"
    TACKLES = "tackles"
    INTERCEPTIONS = "interceptions"
    CLEARANCES = "clearances"
    LAST_MAN_TACKLE = "last_man_tackle"
    WAS_DRIBBLED = "was_dribbled"
    # 对抗
    AERIALS = "aerials"
    AERIALS_WON = "aerials_won"
    GROUND_DUELS = "ground_duels"
    GROUND_DUELS_WON = "ground_duels_won"
    # 纪律 / 失误
    YELLOW_CARDS = "yellow_cards"
    RED_CARDS = "red_cards"
    FOULS = "fouls"
    ERROR_LEAD_TO_GOAL = "error_lead_to_goal"
    ERROR_LEAD_TO_SHOT = "error_lead_to_shot"
    # 门将
    SAVES = "saves"
    BOX_SHOT_SAVES = "box_shot_saves"
    RUNS_OUT = "runs_out"
    CLAIMS_HIGH = "claims_high"
    PUNCHES = "punches"
    # 综合
    RATING = "rating"
    MARKET_VALUE = "market_value"

    @property
    def _meta(self) -> tuple[str, str, str, str, str, str]:
        return _RANKING_META.get(
            self.value, (self.value, "📊", "次", "综合", "RANKING", _BOTH)
        )

    @property
    def label(self) -> str:
        return self._meta[0]

    @property
    def emoji(self) -> str:
        return self._meta[1]

    @property
    def unit(self) -> str:
        """排行数值下方的标注（网站对应的项目名，如「射门」「抢断」）。"""
        return self._meta[2]

    @property
    def category(self) -> str:
        return self._meta[3]

    @property
    def en(self) -> str:
        return self._meta[4]

    @property
    def scope(self) -> str:
        return self._meta[5]

    @property
    def is_discipline(self) -> bool:
        """纪律类榜单（黄/红牌）—— UI 用琥珀色调强调。"""
        return self in (RankingType.YELLOW_CARDS, RankingType.RED_CARDS)

    @classmethod
    def grouped(cls, scope: str = _PLAYER) -> list[tuple[str, list["RankingType"]]]:
        """按分类返回 ``[(分类名, [榜单, …]), …]``。

        ``scope`` 为 ``"player"`` / ``"team"``，分别筛选适用于球员 / 球队的榜单
        （``"both"`` 的类型两边都出现）。分类与组内顺序固定。
        """
        buckets: dict[str, list[RankingType]] = {c: [] for c in RANKING_CATEGORY_ORDER}
        for rt in cls:
            if rt.scope in (scope, _BOTH):
                buckets.setdefault(rt.category, []).append(rt)
        return [(c, buckets[c]) for c in RANKING_CATEGORY_ORDER if buckets.get(c)]


def _ranking_display(raw: dict[str, Any], rtype: RankingType) -> tuple[int, float, str]:
    """从原始条目解析出 (count, value, display)。"""
    raw_count = raw.get("count")
    if raw_count in (None, ""):
        raw_count = raw.get("goal")
    value = _to_float(raw_count)
    # 展示文本：优先用接口 row_2（已格式化），回退到 count
    disp_src = raw.get("row_2")
    if disp_src in (None, ""):
        disp_src = raw_count
    display = str(disp_src) if disp_src not in (None, "") else "0"
    if rtype.value in _PERCENT_TYPES and not display.endswith("%"):
        display = f"{display}%"
    return _to_int(raw_count), value, display


class PlayerRanking(BaseModel):
    """单条球员排行榜数据。"""

    model_config = ConfigDict(extra="ignore")

    rank: int
    person_id: str
    person_name: str
    person_logo: str | None = None
    team_id: str
    team_name: str
    team_logo: str | None = None
    count: int = 0                 # 向后兼容的整数计数（浮点榜会取整）
    value: float = 0.0             # 数值（进度条 / 排序用，保留小数）
    display: str = "0"             # 展示文本（如 "9.6" / "99%"）
    goal: int | None = None        # 射手榜的进球
    penalty_goal: int | None = None
    ranking_type: RankingType = RankingType.GOALS

    @classmethod
    def from_raw(
        cls, raw: dict[str, Any], rtype: RankingType
    ) -> "PlayerRanking":
        count, value, display = _ranking_display(raw, rtype)
        return cls(
            rank=_to_int(raw.get("rank")),
            person_id=str(raw.get("person_id", "")),
            person_name=raw.get("person_name") or "",
            person_logo=raw.get("person_logo"),
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo"),
            count=count,
            value=value,
            display=display,
            goal=_to_int(raw.get("goal"), 0) if rtype == RankingType.GOALS else None,
            penalty_goal=_to_int(raw.get("penalty_goal"), 0)
            if rtype == RankingType.GOALS
            else None,
            ranking_type=rtype,
        )


class TeamRanking(BaseModel):
    """单条球队数据榜数据。"""

    model_config = ConfigDict(extra="ignore")

    rank: int
    team_id: str
    team_name: str
    team_logo: str | None = None
    count: int = 0
    value: float = 0.0
    display: str = "0"
    ranking_type: RankingType = RankingType.GOALS

    @classmethod
    def from_raw(cls, raw: dict[str, Any], rtype: RankingType) -> "TeamRanking":
        count, value, display = _ranking_display(raw, rtype)
        return cls(
            rank=_to_int(raw.get("rank")),
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo"),
            count=count,
            value=value,
            display=display,
            ranking_type=rtype,
        )
