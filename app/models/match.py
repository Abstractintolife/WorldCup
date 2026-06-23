"""比赛与轮次数据模型。"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.time_utils import parse_utc, to_local


class MatchStatus(str, Enum):
    """统一规范化后的比赛状态。"""

    FIXTURE = "Fixture"      # 未开赛
    LIVE = "Playing"         # 进行中
    HALF_TIME = "HalfTime"
    PLAYED = "Played"        # 已结束
    POSTPONED = "Postponed"
    CANCELED = "Canceled"
    UNKNOWN = "Unknown"

    @classmethod
    def from_raw(cls, raw: str | None) -> "MatchStatus":
        if not raw:
            return cls.UNKNOWN
        m = {
            "Fixture": cls.FIXTURE,
            "Playing": cls.LIVE,
            "Live": cls.LIVE,
            "InPlay": cls.LIVE,
            "HalfTime": cls.HALF_TIME,
            "Played": cls.PLAYED,
            "Finished": cls.PLAYED,
            "Postponed": cls.POSTPONED,
            "Canceled": cls.CANCELED,
            "Cancelled": cls.CANCELED,
        }
        return m.get(raw, cls.UNKNOWN)

    @property
    def label(self) -> str:
        return {
            MatchStatus.FIXTURE: "未开赛",
            MatchStatus.LIVE: "进行中",
            MatchStatus.HALF_TIME: "中场",
            MatchStatus.PLAYED: "已结束",
            MatchStatus.POSTPONED: "推迟",
            MatchStatus.CANCELED: "取消",
            MatchStatus.UNKNOWN: "—",
        }[self]


class Round(BaseModel):
    """轮次（赛程头部分组）。"""

    model_config = ConfigDict(extra="ignore")

    name: str = "—"
    current: bool = False
    season_id: int | None = None
    round_id: int | None = None
    gameweek: int | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "Round":
        params = raw.get("params") or {}
        return cls(
            name=raw.get("name", "—"),
            current=bool(raw.get("current")),
            season_id=params.get("season_id"),
            round_id=params.get("round_id"),
            gameweek=params.get("gameweek"),
        )


class Match(BaseModel):
    """单场比赛。

    时间字段约定
    -------------
    * ``start_play`` —— 始终是 **带 UTC 时区** 的 datetime。
      渲染时由 ``app.utils.time_utils.to_local`` 自动转为本地时间。
      解析逻辑优先使用接口里明确标 UTC 的 ``date_utc + time_utc``，
      若无再回退到 ``start_play`` 字符串（按 UTC 处理）。
    """

    model_config = ConfigDict(extra="ignore")

    match_id: str
    competition_id: int | None = None
    round_id: str | None = None

    team_a_id: str
    team_a_name: str
    team_a_short: str | None = None
    team_a_logo: str | None = None

    team_b_id: str
    team_b_name: str
    team_b_short: str | None = None
    team_b_logo: str | None = None

    score_a: str | None = None
    score_b: str | None = None
    fs_a: str | None = None  # 全场比分（finish score）
    fs_b: str | None = None
    ps_a: str | None = None  # 点球比分
    ps_b: str | None = None

    start_play: datetime | None = None
    end_play: datetime | None = None
    date_utc: str | None = None
    time_utc: str | None = None
    status: MatchStatus = MatchStatus.UNKNOWN
    suretime: bool = False
    minute: str | None = None
    minute_extra: str | None = None
    scheme: str | None = None

    # ─── 派生字段 ──────────────────────────────
    @property
    def display_score(self) -> str:
        """以 ``2 - 0`` 这种形式返回比分；未开赛返回 ``vs``。"""
        if self.status in (MatchStatus.FIXTURE, MatchStatus.UNKNOWN):
            return "VS"
        a = self.fs_a or self.score_a or "0"
        b = self.fs_b or self.score_b or "0"
        if self.ps_a or self.ps_b:
            return f"{a} ({self.ps_a or '0'}) - ({self.ps_b or '0'}) {b}"
        return f"{a} - {b}"

    @property
    def is_live(self) -> bool:
        return self.status in (MatchStatus.LIVE, MatchStatus.HALF_TIME)

    @property
    def local_start(self) -> datetime | None:
        return to_local(self.start_play)

    @property
    def winner_id(self) -> str | None:
        if self.status != MatchStatus.PLAYED:
            return None
        try:
            a = int(self.fs_a or self.score_a or 0)
            b = int(self.fs_b or self.score_b or 0)
        except ValueError:
            return None
        if a > b:
            return self.team_a_id
        if b > a:
            return self.team_b_id
        # 平局，看点球
        try:
            pa = int(self.ps_a or 0)
            pb = int(self.ps_b or 0)
            if pa > pb:
                return self.team_a_id
            if pb > pa:
                return self.team_b_id
        except ValueError:
            pass
        return None

    # ─── 解析 ─────────────────────────────────
    @field_validator("start_play", "end_play", mode="before")
    @classmethod
    def _parse_dt(cls, v: Any) -> Any:
        if v in (None, "", "0000-00-00 00:00:00"):
            return None
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if isinstance(v, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        return None

    @field_validator("status", mode="before")
    @classmethod
    def _parse_status(cls, v: Any) -> Any:
        if isinstance(v, MatchStatus):
            return v
        return MatchStatus.from_raw(v)

    @field_validator("suretime", mode="before")
    @classmethod
    def _parse_bool(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        return str(v) in ("1", "true", "True")

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "Match":
        # 优先使用明确标 UTC 的 date_utc / time_utc 拼出权威开赛时间。
        # 若缺失，再退到 start_play 字段（同样按 UTC 处理）。
        date_utc = raw.get("date_utc")
        time_utc = raw.get("time_utc")
        utc_dt = parse_utc(date_utc, time_utc)
        start_play = utc_dt or raw.get("start_play")

        return cls(
            match_id=str(raw.get("match_id", "")),
            competition_id=raw.get("competition_id"),
            round_id=raw.get("round_id"),
            team_a_id=str(raw.get("team_A_id", "")),
            team_a_name=raw.get("team_A_name") or "",
            team_a_short=raw.get("team_A_short_name"),
            team_a_logo=raw.get("team_A_logo"),
            team_b_id=str(raw.get("team_B_id", "")),
            team_b_name=raw.get("team_B_name") or "",
            team_b_short=raw.get("team_B_short_name"),
            team_b_logo=raw.get("team_B_logo"),
            score_a=raw.get("score_A"),
            score_b=raw.get("score_B"),
            fs_a=raw.get("fs_A"),
            fs_b=raw.get("fs_B"),
            ps_a=raw.get("ps_A"),
            ps_b=raw.get("ps_B"),
            start_play=start_play,
            end_play=raw.get("end_play"),
            date_utc=raw.get("date_utc"),
            time_utc=raw.get("time_utc"),
            status=raw.get("status"),
            suretime=raw.get("suretime"),
            minute=raw.get("minute"),
            minute_extra=raw.get("minute_extra"),
            scheme=raw.get("scheme"),
        )
