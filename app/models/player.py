"""球员排行榜模型（射手榜 / 助攻榜）。"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


class RankingType(str, Enum):
    GOALS = "goals"
    ASSISTS = "assists"
    YELLOW_CARDS = "yellow_cards"

    @property
    def label(self) -> str:
        return {
            "goals": "射手榜",
            "assists": "助攻榜",
            "yellow_cards": "黄牌榜",
        }[self.value]

    @property
    def emoji(self) -> str:
        return {
            "goals": "⚽",
            "assists": "🅰️",
            "yellow_cards": "🟨",
        }[self.value]

    @property
    def unit(self) -> str:
        """榜单计数单位文案。"""
        return {
            "goals": "进球",
            "assists": "助攻",
            "yellow_cards": "黄牌",
        }[self.value]


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
    count: int                     # 进球或助攻数
    goal: int | None = None        # 射手榜的进球
    penalty_goal: int | None = None
    ranking_type: RankingType = RankingType.GOALS

    @classmethod
    def from_raw(
        cls, raw: dict[str, Any], rtype: RankingType
    ) -> "PlayerRanking":
        return cls(
            rank=_to_int(raw.get("rank")),
            person_id=str(raw.get("person_id", "")),
            person_name=raw.get("person_name") or "",
            person_logo=raw.get("person_logo"),
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo"),
            count=_to_int(raw.get("count") or raw.get("goal")),
            goal=_to_int(raw.get("goal"), 0) if rtype == RankingType.GOALS else None,
            penalty_goal=_to_int(raw.get("penalty_goal"), 0)
            if rtype == RankingType.GOALS
            else None,
            ranking_type=rtype,
        )
