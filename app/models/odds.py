"""比赛实时赔率模型（懂球帝 ``match/odds/index`` 接口）。

包含三类盘口，每条均含「初始(begin) → 即时(now)」两组数据，可据此显示升降：

* **欧赔(euro)**：主胜 / 平 / 客胜（1X2）。``avg`` 为各家平均值。
* **亚盘(asia)**：盘口(让球线) + 主队水位 / 客队水位。
* **大小球(size)**：盘口(总进球线) + 大球水位 / 小球水位。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _s(v: Any) -> str:
    if v is None:
        return "-"
    s = str(v).strip()
    return s if s else "-"


@dataclass
class EuroLine:
    """1X2 欧赔一行（某家博彩公司）。"""

    name: str
    home: str
    draw: str
    away: str
    begin_home: str
    begin_draw: str
    begin_away: str

    @staticmethod
    def _trend(now: str, begin: str) -> int:
        """1=升 -1=降 0=平/不可比。"""
        try:
            n, b = float(now), float(begin)
        except (TypeError, ValueError):
            return 0
        if b <= 0:
            return 0
        return 1 if n > b else (-1 if n < b else 0)

    @property
    def home_trend(self) -> int:
        return self._trend(self.home, self.begin_home)

    @property
    def away_trend(self) -> int:
        return self._trend(self.away, self.begin_away)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "EuroLine":
        now = raw.get("now") or {}
        begin = raw.get("begin") or {}
        return cls(
            name=_s(raw.get("name")),
            home=_s(now.get("homeWin")),
            draw=_s(now.get("draw")),
            away=_s(now.get("awayWin")),
            begin_home=_s(begin.get("homeWin")),
            begin_draw=_s(begin.get("draw")),
            begin_away=_s(begin.get("awayWin")),
        )


@dataclass
class HandicapLine:
    """亚盘 / 大小球一行。``a`` / ``b`` 为两侧水位。"""

    name: str
    line: str       # 盘口（让球线 / 总进球线）
    a: str          # 亚盘=主队水位；大小球=大球水位
    b: str          # 亚盘=客队水位；大小球=小球水位

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "HandicapLine":
        now = raw.get("now") or {}
        return cls(
            name=_s(raw.get("name")),
            line=_s(now.get("draw")),
            a=_s(now.get("homeWin")),
            b=_s(now.get("awayWin")),
        )


@dataclass
class MatchOdds:
    match_id: str
    has_odds: bool = False
    avg: EuroLine | None = None
    euro: list[EuroLine] = field(default_factory=list)
    asia: list[HandicapLine] = field(default_factory=list)
    size: list[HandicapLine] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "MatchOdds":
        raw = raw or {}
        avg_raw = raw.get("avg")
        avg = EuroLine.from_raw({**avg_raw, "name": "平均"}) if avg_raw else None
        return cls(
            match_id=str(raw.get("matchId", "")),
            has_odds=bool(raw.get("has_odds")),
            avg=avg,
            euro=[EuroLine.from_raw(x) for x in (raw.get("euro") or [])],
            asia=[HandicapLine.from_raw(x) for x in (raw.get("asia") or [])],
            size=[HandicapLine.from_raw(x) for x in (raw.get("size") or [])],
        )
