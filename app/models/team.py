"""国家队/俱乐部模型（轻量、由各处聚合产生）。"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Team(BaseModel):
    """聚合后的球队信息。"""

    model_config = ConfigDict(extra="ignore")

    team_id: str
    name: str
    short_name: str | None = None
    logo: str | None = None
    group: str | None = None
    rank: int | None = None
    points: int | None = None
    matches_total: int | None = None
    matches_won: int | None = None
    matches_draw: int | None = None
    matches_lost: int | None = None
    goals_pro: int | None = None
    goals_against: int | None = None

    @property
    def goal_diff(self) -> int | None:
        if self.goals_pro is None or self.goals_against is None:
            return None
        return self.goals_pro - self.goals_against
