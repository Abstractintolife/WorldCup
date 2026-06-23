"""球员排行榜模型。

懂球帝 ``person_ranking`` 接口支持一大批球员数据榜单（射手 / 助攻 / 黄牌 /
射门 / 传球 / 抢断 / 门将 / 评分 …）。这里用 :class:`RankingType` 枚举把
每个榜单的「接口 type 值 + 中文名 + 图标 + 单位 + 所属分类」集中描述，
UI 据此动态生成全部榜单标签。

数值解析
--------
多数榜单计数为整数（进球 / 抢断 …），但有两类特殊：

* **评分（rating）**：形如 ``"9.6"`` 的浮点字符串 —— 不能按 int 解析
  （否则全部变 0）。用 :func:`_to_float` 保留小数，``display`` 原样展示。
* **传球成功率（pass_accuracy）**：接口返回 ``"99"``，展示需补 ``%``。

因此模型同时保留：``value``（浮点数值，用于进度条/排序）、``display``
（最终展示文本，如 ``"9.6"`` / ``"99%"``）、``count``（向后兼容的整数）。
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ── 榜单元信息：type 值 → (中文名, 图标, 单位, 分类, 英文副标题) ──────────
#   分类用于 UI 二级分组；定义顺序即各分类内的展示顺序。
_RANKING_META: dict[str, tuple[str, str, str, str, str]] = {
    # 进攻
    "goals":              ("射手榜", "⚽", "球", "进攻", "TOP SCORERS"),
    "shots":              ("射门", "🎯", "次", "进攻", "SHOTS"),
    "shots_on_target":    ("射正", "🥅", "次", "进攻", "SHOTS ON TARGET"),
    "big_chance_missed":  ("错失绝佳机会", "😱", "次", "进攻", "BIG CHANCES MISSED"),
    # 创造
    "assists":            ("助攻榜", "🅰️", "助攻", "创造", "TOP ASSISTS"),
    "key_passes":         ("关键传球", "🔑", "次", "创造", "KEY PASSES"),
    # 传球
    "passes":             ("传球", "🔁", "次", "传球", "PASSES"),
    "pass_accuracy":      ("传球成功率", "🎯", "", "传球", "PASS ACCURACY"),
    "long_balls":         ("长传", "🚀", "次", "传球", "LONG BALLS"),
    "crosses":            ("传中", "✈️", "次", "传球", "CROSSES"),
    "touches":            ("触球", "👟", "次", "传球", "TOUCHES"),
    # 过人
    "dribbles_attempted": ("尝试过人", "🌀", "次", "过人", "DRIBBLES ATTEMPTED"),
    "dribbles_won":       ("成功过人", "💫", "次", "过人", "SUCCESSFUL DRIBBLES"),
    "fouled":             ("被犯规", "🆘", "次", "过人", "FOULS WON"),
    "dispossessed":       ("丢失球权", "💨", "次", "过人", "DISPOSSESSED"),
    # 防守
    "tackles":            ("抢断", "🛡", "次", "防守", "TACKLES"),
    "interceptions":      ("拦截", "🚧", "次", "防守", "INTERCEPTIONS"),
    "clearances":         ("解围", "🧹", "次", "防守", "CLEARANCES"),
    "last_man_tackle":    ("防线最后一人抢断", "🚨", "次", "防守", "LAST MAN TACKLES"),
    "was_dribbled":       ("被过", "🌀", "次", "防守", "DRIBBLED PAST"),
    # 对抗
    "aerials":            ("争顶总数", "🆙", "次", "对抗", "AERIAL DUELS"),
    "aerials_won":        ("争顶成功", "🛫", "次", "对抗", "AERIAL DUELS WON"),
    "ground_duels":       ("地面争抢", "🤼", "次", "对抗", "GROUND DUELS"),
    "ground_duels_won":   ("地面争抢成功", "🤝", "次", "对抗", "GROUND DUELS WON"),
    # 纪律 / 失误
    "yellow_cards":       ("黄牌榜", "🟨", "张", "纪律", "MOST YELLOW CARDS"),
    "red_cards":          ("红牌榜", "🟥", "张", "纪律", "MOST RED CARDS"),
    "fouls":              ("犯规", "🚫", "次", "纪律", "FOULS"),
    "error_lead_to_goal": ("失误导致丢球", "❌", "次", "纪律", "ERRORS LEADING TO GOAL"),
    "error_lead_to_shot": ("失误导致射门", "⚠️", "次", "纪律", "ERRORS LEADING TO SHOT"),
    # 门将
    "saves":              ("扑救", "🧤", "次", "门将", "SAVES"),
    "runs_out":           ("出击成功", "🏃", "次", "门将", "SUCCESSFUL RUNS OUT"),
    "claims_high":        ("出击摘高球", "🙌", "次", "门将", "HIGH CLAIMS"),
    "punches":            ("拳击球", "🥊", "次", "门将", "PUNCHES"),
    # 综合
    "rating":             ("评分", "⭐", "分", "综合", "AVERAGE RATING"),
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
    SHOTS = "shots"
    SHOTS_ON_TARGET = "shots_on_target"
    BIG_CHANCE_MISSED = "big_chance_missed"
    # 创造
    ASSISTS = "assists"
    KEY_PASSES = "key_passes"
    # 传球
    PASSES = "passes"
    PASS_ACCURACY = "pass_accuracy"
    LONG_BALLS = "long_balls"
    CROSSES = "crosses"
    TOUCHES = "touches"
    # 过人
    DRIBBLES_ATTEMPTED = "dribbles_attempted"
    DRIBBLES_WON = "dribbles_won"
    FOULED = "fouled"
    DISPOSSESSED = "dispossessed"
    # 防守
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
    RUNS_OUT = "runs_out"
    CLAIMS_HIGH = "claims_high"
    PUNCHES = "punches"
    # 综合
    RATING = "rating"

    @property
    def _meta(self) -> tuple[str, str, str, str, str]:
        return _RANKING_META.get(
            self.value, (self.value, "📊", "次", "综合", "RANKING")
        )

    @property
    def label(self) -> str:
        return self._meta[0]

    @property
    def emoji(self) -> str:
        return self._meta[1]

    @property
    def unit(self) -> str:
        """榜单计数单位文案（如 进球 / 次 / 张 / 分）。"""
        return self._meta[2]

    @property
    def category(self) -> str:
        return self._meta[3]

    @property
    def en(self) -> str:
        return self._meta[4]

    @property
    def is_discipline(self) -> bool:
        """纪律类榜单（黄/红牌）—— UI 用琥珀色调强调。"""
        return self in (RankingType.YELLOW_CARDS, RankingType.RED_CARDS)

    @classmethod
    def grouped(cls) -> list[tuple[str, list["RankingType"]]]:
        """按分类返回 ``[(分类名, [榜单, …]), …]``，分类与组内顺序固定。"""
        buckets: dict[str, list[RankingType]] = {c: [] for c in RANKING_CATEGORY_ORDER}
        for rt in cls:
            buckets.setdefault(rt.category, []).append(rt)
        return [(c, buckets[c]) for c in RANKING_CATEGORY_ORDER if buckets.get(c)]


class PlayerRanking(BaseModel):
    """单条排行榜数据。"""

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
        raw_count = raw.get("count")
        if raw_count in (None, ""):
            raw_count = raw.get("goal")
        value = _to_float(raw_count)

        # 展示文本：优先用接口的 row_2（已是格式化好的字符串），回退到 count
        disp_src = raw.get("row_2")
        if disp_src in (None, ""):
            disp_src = raw_count
        display = str(disp_src) if disp_src not in (None, "") else "0"
        if rtype.value in _PERCENT_TYPES and not display.endswith("%"):
            display = f"{display}%"

        return cls(
            rank=_to_int(raw.get("rank")),
            person_id=str(raw.get("person_id", "")),
            person_name=raw.get("person_name") or "",
            person_logo=raw.get("person_logo"),
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo"),
            count=_to_int(raw_count),
            value=value,
            display=display,
            goal=_to_int(raw.get("goal"), 0) if rtype == RankingType.GOALS else None,
            penalty_goal=_to_int(raw.get("penalty_goal"), 0)
            if rtype == RankingType.GOALS
            else None,
            ranking_type=rtype,
        )
