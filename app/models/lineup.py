"""比赛阵容数据模型（懂球帝 match/lineup 接口）。

接口字段约定
-------------
* ``base`` —— 场地 / 裁判 / 天气 / 是否预测阵容（``forecast_lineup``）。
* ``persons.team_A/B`` —— **首发实际阵容**（比赛开始后才有，未开赛时
  ``lineups`` 为 null）。
* ``forecasts.team_A/B`` —— **赛前预测阵容**（赛前 1 小时左右公布）。

每名球员的 ``formation_place`` 是关键定位字段：

* ``1`` 恒为门将；
* 之后从后防线开始、由守到攻**逐行递增**编号。

结合 ``formation``（如 ``"4-2-3-1"``）即可在球场上还原每名球员的
列（防线/中场/锋线）与行（同一线内的上下位置）。接口未给
``position_x / position_y``，故位置完全由本模型 + 阵型字符串推导。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# 英文位置 → 中文（懂球帝 position 字段）
_POSITION_ZH = {
    "Goalkeeper": "门将",
    "Defender": "后卫",
    "Midfielder": "中场",
    "Attacker": "前锋",
    "Forward": "前锋",
}


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


@dataclass
class LineupPlayer:
    """阵容中的一名球员。"""

    person_id: str
    name: str
    number: str
    position: str            # 英文：Goalkeeper / Defender / Midfielder / Attacker
    formation_place: int     # 1=门将，其后由守到攻递增
    captain: bool
    logo: str | None = None

    @property
    def position_zh(self) -> str:
        return _POSITION_ZH.get(self.position, "球员")

    @property
    def is_goalkeeper(self) -> bool:
        return self.position == "Goalkeeper" or self.formation_place == 1

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "LineupPlayer":
        return cls(
            person_id=str(raw.get("person_id", "")),
            name=raw.get("person") or raw.get("person_name") or "",
            number=str(raw.get("shirtnumber") or raw.get("number") or "").strip(),
            position=raw.get("position") or "",
            formation_place=_to_int(raw.get("formation_place"), 0),
            captain=bool(_to_int(raw.get("captain"), 0)),
            logo=raw.get("logo") or None,
        )


@dataclass
class TeamLineup:
    """单支球队的阵容（首发 + 替补 + 阵型）。"""

    team_id: str
    team_name: str
    team_logo: str | None
    formation: str
    coach: str
    starters: list[LineupPlayer] = field(default_factory=list)
    subs: list[LineupPlayer] = field(default_factory=list)

    @property
    def formation_lines(self) -> list[int]:
        """把阵型字符串拆成各线人数，如 ``"4-2-3-1"`` → ``[4, 2, 3, 1]``。"""
        nums = [int(x) for x in re.findall(r"\d+", self.formation or "")]
        return nums

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "TeamLineup":
        starters = [
            LineupPlayer.from_raw(p) for p in (raw.get("lineups") or [])
        ]
        subs = [LineupPlayer.from_raw(p) for p in (raw.get("sub") or [])]
        return cls(
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo") or None,
            formation=raw.get("formation") or "",
            coach=raw.get("team_coach") or "",
            starters=starters,
            subs=subs,
        )

    @property
    def has_starters(self) -> bool:
        return len(self.starters) > 0


@dataclass
class MatchLineup:
    """一场比赛的完整阵容信息。"""

    is_forecast: bool
    field_name: str
    referee: str
    weather: str
    team_a: TeamLineup
    team_b: TeamLineup

    @property
    def available(self) -> bool:
        return self.team_a.has_starters or self.team_b.has_starters

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "MatchLineup | None":
        if not data:
            return None
        base = data.get("base") or {}
        persons = data.get("persons") or {}
        forecasts = data.get("forecasts") or {}

        # 优先使用实际首发；若没有（未开赛）则退到预测阵容。
        def _pick(side: str) -> tuple[TeamLineup, bool]:
            actual_raw = persons.get(side) or {}
            actual = TeamLineup.from_raw(actual_raw)
            if actual.has_starters:
                return actual, False
            forecast_raw = forecasts.get(side) or {}
            forecast = TeamLineup.from_raw(forecast_raw)
            return forecast, True

        team_a, fa = _pick("team_A")
        team_b, fb = _pick("team_B")

        # 任一侧用到了预测阵容，就标记整体为「预测阵容」。
        is_forecast = fa or fb or bool(_to_int(base.get("forecast_lineup"), 0))

        ml = cls(
            is_forecast=is_forecast,
            field_name=base.get("field") or "",
            referee=base.get("referee") or "",
            weather=base.get("weather") or "",
            team_a=team_a,
            team_b=team_b,
        )
        if not ml.available:
            return None
        return ml
