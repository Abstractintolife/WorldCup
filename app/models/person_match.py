"""球员近期比赛模型 —— 对接懂球帝 ``person/matches/{person_id}`` 接口。

该接口返回某球员（含未参加本届世界杯者，如梅西）参加过的每一场比赛，
并附带**该球员在该场的个人数据**：进球、助攻、黄/红牌、出场分钟、
官方评分（``rating``）与懂球帝评分（``dqd_rating``）。

这正是「球员详情页 · 近期比赛为空」的数据来源 —— 旧版用的是「球员
所属国家队的本届世界杯赛程」，对绝大多数球员（尤其俱乐部球员）为空。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _s(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def _int(v: Any, default: int = 0) -> int:
    try:
        s = _s(v)
        return int(s) if s and s.lstrip("-").isdigit() else default
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class PersonMatch:
    """球员某一场比赛的概览 + 个人数据。"""

    person_id: str
    match_id: str
    competition_name: str
    match_title: str

    team_a_name: str
    team_a_logo: str
    team_b_name: str
    team_b_logo: str

    fs_a: str           # 全场比分 A
    fs_b: str           # 全场比分 B
    start_play: datetime | None

    goals: int          # 该球员本场进球
    assists: int        # 该球员本场助攻
    cards: str          # 黄/红牌（原样字符串）
    minute: str         # 出场分钟，如 "80'"
    rating: str         # 官方评分
    dqd_rating: str     # 懂球帝评分

    @property
    def played(self) -> bool:
        """是否已进行（有比分即视为已踢）。"""
        return bool(self.fs_a) and bool(self.fs_b)

    @property
    def score_text(self) -> str:
        if self.played:
            return f"{self.fs_a} - {self.fs_b}"
        return "VS"

    @property
    def best_rating(self) -> str:
        """优先官方评分，否则懂球帝评分。"""
        return self.rating or self.dqd_rating

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "PersonMatch":
        # start_play 形如 "2026-06-17 01:00:00"，按 UTC 处理（与 Match 一致）
        sp = _s(raw.get("start_play"))
        dt: datetime | None = None
        if sp and sp != "0000-00-00 00:00:00":
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(sp, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
        return cls(
            person_id=_s(raw.get("person_id")),
            match_id=_s(raw.get("match_id")),
            competition_name=_s(raw.get("competition_name")),
            match_title=_s(raw.get("match_title")),
            team_a_name=_s(raw.get("team_A_name")),
            team_a_logo=_s(raw.get("team_A_logo")),
            team_b_name=_s(raw.get("team_B_name")),
            team_b_logo=_s(raw.get("team_B_logo")),
            fs_a=_s(raw.get("fs_A")),
            fs_b=_s(raw.get("fs_B")),
            start_play=dt,
            goals=_int(raw.get("goals")),
            assists=_int(raw.get("assists")),
            cards=_s(raw.get("cards")),
            minute=_s(raw.get("minute")),
            rating=_s(raw.get("rating")),
            dqd_rating=_s(raw.get("dqd_rating")),
        )
