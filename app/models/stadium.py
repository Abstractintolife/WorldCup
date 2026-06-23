"""球场模型（用于 2026 世界杯 16 个主办城市）。"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Stadium(BaseModel):
    """主办城市的体育场信息。"""

    model_config = ConfigDict(extra="ignore")

    name_zh: str
    name_en: str
    city: str
    country: str
    capacity: int
    opened: int | None = None
    surface: str = "草皮"
    role: str = ""                  # 例如 "揭幕战 / 决赛"
    description: str = ""
    flag_emoji: str = ""           # 国家国旗 emoji
    image_url: str | None = None   # 球场远程实景图（用于卡片背景）
    accent: str = "#E5394E"        # 卡片主色

    @property
    def location(self) -> str:
        return f"{self.city}, {self.country}"
