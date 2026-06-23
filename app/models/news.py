"""赛事新闻数据模型（懂球帝资讯接口）。

数据来源
---------
``https://api.dongqiudi.com/v2/article/relative/{seed_id}?from=msite_com``
返回 ``{"code":0,"relative":[{id,title,thumb,time,show_time,schema,type}, ...]}``，
即与某篇世界杯文章「相关」的最新资讯流。本模型把每条原始 JSON 规范化为
强类型的 :class:`NewsArticle`，供概览页「赛事新闻」面板与新闻资讯页消费。
"""
from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict

# 文章网页地址模板（由 article id 拼出，可在系统浏览器打开原文）
_ARTICLE_URL = "https://www.dongqiudi.com/articles/{id}.html"

# 评论正文中可能夹带 HTML（表情 <img>、链接等），展示前清洗为纯文本
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    text = _TAG_RE.sub("", text or "")
    return (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .strip()
    )


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


class HotComment(BaseModel):
    """单条「热评」（球迷热议）。

    数据来源：``https://api.dongqiudi.com/v2/article/{article_id}/hot``
    返回 ``data.comment_list[]``（评论正文/点赞/时间/user_id/回复数）与
    ``data.user_list[]``（按 ``id`` 提供昵称与头像）。本模型把两者按
    ``user_id`` 关联，规范化为带作者信息的强类型评论。
    """

    model_config = ConfigDict(extra="ignore")

    comment_id: str
    content: str
    up: int = 0                  # 点赞数
    reply_total: int = 0         # 回复数
    created_at: str = ""         # 形如 "2026-06-23 17:28:49"
    user_name: str = "球迷"
    avatar: str | None = None

    @classmethod
    def from_raw(
        cls, raw: dict[str, Any], users: dict[str, dict[str, Any]] | None = None
    ) -> "HotComment":
        users = users or {}
        uid = str(raw.get("user_id") or "")
        u = users.get(uid, {})

        def _int(v: Any) -> int:
            try:
                return int(v)
            except (TypeError, ValueError):
                return 0

        avatar = (u.get("avatar") or "").strip() or None
        return cls(
            comment_id=str(raw.get("id") or ""),
            content=_strip_html(raw.get("content") or ""),
            up=_int(raw.get("up")),
            reply_total=_int(raw.get("reply_total")),
            created_at=(raw.get("created_at") or "").strip(),
            user_name=(u.get("username") or "球迷").strip() or "球迷",
            avatar=avatar,
        )
