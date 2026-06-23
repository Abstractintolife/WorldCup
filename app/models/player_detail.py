"""球员个人主页模型 —— 对接懂球帝 person/detail + sofifa 能力值接口。

数据来源
--------
* ``person/detail/{person_id}``  → 真实档案（身高/体重/惯用脚/国籍/俱乐部/
  号码/身价/合同/奖杯），**对任意球员（含未参加本届世界杯的）都有效**。
* ``sofifa/v1/player_ability/{person_id}`` → FC26 风能力值（OVR + 六维雷达
  + 细项 + 国际声望/逆足/花式 + 注册位置）。

任何字段都做了空值容错；缺失时由调用方按 person_id 哈希兜底。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


def _s(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def _int(v: Any, default: int = 0) -> int:
    try:
        m = re.search(r"-?\d+", str(v))
        return int(m.group(0)) if m else default
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────
@dataclass(frozen=True)
class TrophyItem:
    """一项荣誉（某项赛事夺冠 N 次）。"""

    competition_name: str
    trophy_img: str
    times: int
    seasons: list[str] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "TrophyItem":
        lists = raw.get("lists") or []
        seasons = [
            f"{_s(x.get('season_name'))} {_s(x.get('team_name'))}".strip()
            for x in lists
            if isinstance(x, dict)
        ]
        return cls(
            competition_name=_s(raw.get("competition_name")),
            trophy_img=_s(raw.get("trophy_img")),
            times=_int(raw.get("times"), len(seasons)),
            seasons=seasons,
        )


@dataclass(frozen=True)
class AbilityDim:
    """一个雷达维度（速度/力量/防守/盘带/传球/射门）。"""

    name: str
    val: int


@dataclass(frozen=True)
class PlayerAbility:
    """FC26 风能力值面板。"""

    ovr: int
    radar: list[AbilityDim]
    position: str          # 注册位置（ST / CM / ...）
    foot: str              # R / L / B
    reputation: int        # 国际声望（1-5 星）
    weak_foot: int         # 逆足能力（1-5 星）
    skill_moves: int       # 花式技巧（1-5 星）
    version: str           # 「FC 26」
    bars: list[tuple[str, int]] = field(default_factory=list)  # (分类, total)

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "PlayerAbility | None":
        if not isinstance(data, dict):
            return None
        d = data.get("data") if "data" in data else data
        if not isinstance(d, dict) or not d:
            return None
        avg = d.get("average") or {}
        radar = [
            AbilityDim(_s(x.get("name")), _int(x.get("val")))
            for x in (d.get("redar") or [])
            if isinstance(x, dict)
        ]
        star = {
            _s(x.get("name")): _int(x.get("val"))
            for x in (d.get("star_bar") or [])
            if isinstance(x, dict)
        }
        bars = [
            (_s(b.get("title")), _int(b.get("total")))
            for b in (d.get("bar_info") or [])
            if isinstance(b, dict)
        ]
        return cls(
            ovr=_int(avg.get("val")),
            radar=radar,
            position=_s((d.get("good_pos") or {}).get("val")),
            foot=_s((d.get("foot_info") or {}).get("val")),
            reputation=star.get("国际声望", 0),
            weak_foot=star.get("逆足能力", 0),
            skill_moves=star.get("花式技巧", 0),
            version=_s(d.get("version")) or "FC",
            bars=bars,
        )


@dataclass(frozen=True)
class PlayerDetail:
    """球员个人主页完整档案。"""

    person_id: str
    name_zh: str
    name_en: str
    person_logo: str
    nationality: str
    nationality_logo: str
    date_of_birth: str
    age: int
    height_cm: int
    weight_kg: int
    foot: str
    position_type: str         # attacker/midfielder/...
    team_id: str
    team_name: str
    team_logo: str
    shirt_number: int
    role: str                  # 前锋/中场/...
    market_value: str          # 万欧（原样字符串）
    weekly_salary: str
    contract: str
    trophies: list[TrophyItem] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "PlayerDetail | None":
        if not isinstance(raw, dict):
            return None
        base = raw.get("base_info") or {}
        if not isinstance(base, dict) or not _s(base.get("person_id")):
            return None
        team = base.get("team_info") or {}
        trophies = [
            TrophyItem.from_raw(t)
            for t in (raw.get("trophy_info") or [])
            if isinstance(t, dict)
        ]
        return cls(
            person_id=_s(base.get("person_id")),
            name_zh=_s(base.get("person_name")),
            name_en=_s(base.get("person_en_name")),
            person_logo=_s(base.get("person_logo")),
            nationality=_s(base.get("nationality")),
            nationality_logo=_s(base.get("nationality_logo")),
            date_of_birth=_s(base.get("date_of_birth")),
            age=_int(base.get("age")),
            height_cm=_int(base.get("height")),
            weight_kg=_int(base.get("weight")),
            foot=_s(base.get("foot")) or "右脚",
            position_type=_s(base.get("position")),
            team_id=_s(team.get("team_id")),
            team_name=_s(team.get("team_name")),
            team_logo=_s(team.get("team_logo")),
            shirt_number=_int(team.get("shirtnumber")),
            role=_s(team.get("role")),
            market_value=_s(base.get("market_value")),
            weekly_salary=_s(base.get("weekly_salary")),
            contract=_s(base.get("contract")),
            trophies=trophies,
        )
