"""积分榜数据模型：组别 + 球队行 + 淘汰赛对阵。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


class TeamStanding(BaseModel):
    """积分榜中的某一支球队行。"""

    model_config = ConfigDict(extra="ignore")

    rank: int
    last_rank: int | None = None
    team_id: str
    team_name: str
    team_logo: str | None = None
    points: int
    matches_total: int
    matches_won: int
    matches_draw: int
    matches_lost: int
    goals_pro: int
    goals_against: int
    desc: str | None = None        # 例如 "晋级 16 强"
    instruction: str | None = None
    color: str | None = None       # 由分组的 desc 解析得到
    qualify: str | None = None     # 晋级状态："direct"（前2直接晋级）/ "best3"（最佳第三）/ None

    @property
    def goal_diff(self) -> int:
        return self.goals_pro - self.goals_against

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "TeamStanding":
        return cls(
            rank=_to_int(raw.get("rank")),
            last_rank=_to_int(raw.get("last_rank"), default=0) or None,
            team_id=str(raw.get("team_id", "")),
            team_name=raw.get("team_name") or "",
            team_logo=raw.get("team_logo"),
            points=_to_int(raw.get("points")),
            matches_total=_to_int(raw.get("matches_total")),
            matches_won=_to_int(raw.get("matches_won")),
            matches_draw=_to_int(raw.get("matches_draw")),
            matches_lost=_to_int(raw.get("matches_lost")),
            goals_pro=_to_int(raw.get("goals_pro")),
            goals_against=_to_int(raw.get("goals_against")),
            desc=raw.get("desc"),
            instruction=raw.get("instruction"),
        )


class GroupStanding(BaseModel):
    """单个小组的积分榜。"""

    model_config = ConfigDict(extra="ignore")

    name: str = "—"                                 # 例如 "A组"
    teams: list[TeamStanding] = Field(default_factory=list)
    legend: list[dict[str, str]] = Field(default_factory=list)
    """legend 描述例如：[{"color":"#3b82f6","desc":"出线晋级 16 强"}]"""

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "GroupStanding":
        teams = [TeamStanding.from_raw(t) for t in raw.get("data") or []]

        # desc 中包含颜色 + 文案，用于积分榜的色块图例
        legend: list[dict[str, str]] = []
        for d in raw.get("desc") or []:
            if isinstance(d, dict):
                legend.append(
                    {
                        "color": d.get("color") or "#888888",
                        "desc": d.get("desc") or d.get("text") or "",
                        "rank": str(d.get("rank") or ""),
                    }
                )

        # 把图例颜色映射回每个名次
        rank_to_color: dict[str, str] = {}
        for item in legend:
            r = item.get("rank")
            if r:
                rank_to_color[r] = item["color"]
        for t in teams:
            t.color = rank_to_color.get(str(t.rank))

        return cls(
            name=str(raw.get("name") or "—"),
            teams=teams,
            legend=legend,
        )


class KnockoutTie(BaseModel):
    """淘汰赛单场对阵（含两回合或单场）。"""

    model_config = ConfigDict(extra="ignore")

    team_a_id: str
    team_a_name: str
    team_a_logo: str | None = None
    team_b_id: str
    team_b_name: str
    team_b_logo: str | None = None
    total_score: str = ""          # 如 "2 - 1" 或 "vs"
    total_penalty: str = ""        # 点球总比分
    winner: str = ""
    matches: list[dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "KnockoutTie":
        a = raw.get("TeamA") or {}
        b = raw.get("TeamB") or {}
        return cls(
            team_a_id=str(a.get("id", "")),
            team_a_name=a.get("name") or "",
            team_a_logo=a.get("logo"),
            team_b_id=str(b.get("id", "")),
            team_b_name=b.get("name") or "",
            team_b_logo=b.get("logo"),
            total_score=str(raw.get("total_score") or "").strip(),
            total_penalty=str(raw.get("total_penalty") or "").strip(),
            winner=str(raw.get("winner") or ""),
            matches=raw.get("matches") or [],
        )
