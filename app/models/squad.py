"""国家队阵容模型（来自懂球帝 team/member_v2 接口）。

接口返回 ``data.list`` —— 一组分区（教练 / 门将 / 后卫 / 中场 / 前锋），
每个分区下是若干球员/教练。本模块把它解析为强类型对象供 UI 使用。
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


def _clean(v: Any) -> str | None:
    s = ("" if v is None else str(v)).strip()
    return s or None


class SquadMember(BaseModel):
    """阵容中的一名成员（球员或教练）。"""

    model_config = ConfigDict(extra="ignore")

    person_id: str
    name: str
    en_name: str | None = None
    logo: str | None = None
    shirt_number: str | None = None
    age: str | None = None
    position_type: str = ""        # 原始 type：attacker/midfielder/... 或 主教练
    role_title: str = ""           # 所属分区标题（前锋/中场/...）
    is_captain: bool = False
    nationality: str | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any], group_title: str = "") -> "SquadMember":
        return cls(
            person_id=str(raw.get("person_id") or ""),
            name=raw.get("person_name") or "",
            en_name=_clean(raw.get("person_en_name")),
            logo=_clean(raw.get("person_logo")),
            shirt_number=_clean(raw.get("shirtnumber")),
            age=_clean(raw.get("age")),
            position_type=raw.get("type") or "",
            role_title=group_title,
            is_captain=bool((raw.get("captain_logo") or "").strip()),
            nationality=_clean(raw.get("nationality_name")),
        )


class SquadGroup(BaseModel):
    """阵容分区（如「前锋」「门将」「教练」）。"""

    model_config = ConfigDict(extra="ignore")

    title: str
    is_coach: bool = False
    members: list[SquadMember] = []

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SquadGroup":
        title = raw.get("title") or ""
        members = [
            SquadMember.from_raw(p, title) for p in (raw.get("data") or [])
        ]
        return cls(title=title, is_coach=(title == "教练"), members=members)

    @property
    def count(self) -> int:
        return len(self.members)
