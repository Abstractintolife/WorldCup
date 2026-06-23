"""赛事新闻数据模型（懂球帝资讯接口）。

数据来源
---------
``https://api.dongqiudi.com/v2/article/relative/{seed_id}?from=msite_com``
返回 ``{"code":0,"relative":[{id,title,thumb,time,show_time,schema,type}, ...]}``，
即与某篇世界杯文章「相关」的最新资讯流。本模型把每条原始 JSON 规范化为
强类型的 :class:`NewsArticle`，供概览页「赛事新闻」面板与新闻资讯页消费。
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

# 文章网页地址模板（由 article id 拼出，可在系统浏览器打开原文）
_ARTICLE_URL = "https://www.dongqiudi.com/articles/{id}.html"


class NewsArticle(BaseModel):
    """单条赛事资讯。"""

    model_config = ConfigDict(extra="ignore")

    article_id: str
    title: str
    thumb: str | None = None          # 缩略图 URL（可能为空字符串 → None）
    time_text: str = ""               # 形如 "06-23 17:27"
    show_time: int | None = None      # Unix 时间戳（秒），用于排序
    url: str = ""                     # 原文网页地址
    article_type: str = "article"

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "NewsArticle":
        aid = str(raw.get("id") or "")
        thumb = (raw.get("thumb") or "").strip() or None
        show_time = raw.get("show_time")
        try:
            show_time = int(show_time) if show_time is not None else None
        except (TypeError, ValueError):
            show_time = None
        return cls(
            article_id=aid,
            title=(raw.get("title") or "").strip(),
            thumb=thumb,
            time_text=(raw.get("time") or "").strip(),
            show_time=show_time,
            url=_ARTICLE_URL.format(id=aid) if aid else "",
            article_type=str(raw.get("type") or "article"),
        )
