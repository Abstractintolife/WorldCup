"""数据服务：把原始 JSON 解析为强类型对象，并提供聚合查询。"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.api.client import ApiClient
from app.config import ENDPOINTS, LINEUP_CACHE_TTL, NEWS_CACHE_TTL, SQUAD_CACHE_TTL
from app.models.lineup import MatchLineup
from app.models.match import Match, Round
from app.models.news import HotComment, NewsArticle
from app.models.odds import MatchOdds
from app.models.player import PlayerRanking, RankingType, TeamRanking
from app.models.player_detail import PlayerAbility, PlayerDetail
from app.models.person_match import PersonMatch
from app.models.squad import SquadGroup
from app.models.standing import GroupStanding, KnockoutTie
from app.models.team import Team

log = logging.getLogger(__name__)


class DataService:
    """组合所有 API 调用，并产出可直接喂给 UI 的对象。"""

    def __init__(
        self,
        client: ApiClient | None = None,
        season_id: int = ENDPOINTS.default_season_id,
    ) -> None:
        self._client = client or ApiClient.instance()
        self.season_id = season_id

    # ─── 赛程 ─────────────────────────────────
    async def fetch_schedule(
        self,
        round_id: int | None = None,
        gameweek: int | None = None,
        force: bool = False,
    ) -> tuple[list[Round], list[Match]]:
        params: dict[str, Any] = {"season_id": self.season_id}
        if round_id is not None:
            params["round_id"] = round_id
        if gameweek is not None:
            params["gameweek"] = gameweek

        data = await self._client.get_json(
            ENDPOINTS.schedule, params=params, force=force
        )
        content = data.get("content") or {}
        rounds = [Round.from_raw(r) for r in content.get("rounds") or []]
        matches = [Match.from_raw(m) for m in content.get("matches") or []]
        return rounds, matches

    async def fetch_full_schedule(self, force: bool = False) -> tuple[list[Round], list[Match]]:
        """拉取完整赛程：先获取轮次列表，再合并所有轮次的比赛。

        各轮次的请求**并发**发出（``asyncio.gather``）而非逐轮串行等待，
        把赛程页的首屏时间从「N×单次延迟」压缩到「≈单次延迟」。
        """
        rounds, base_matches = await self.fetch_schedule(force=force)
        all_matches: dict[str, Match] = {m.match_id: m for m in base_matches}

        targets = [
            (r.round_id, r.gameweek)
            for r in rounds
            if r.round_id is not None and r.gameweek is not None
        ]

        async def _one(round_id: int, gameweek: int):
            try:
                _, ms = await self.fetch_schedule(
                    round_id=round_id, gameweek=gameweek, force=force
                )
                return ms
            except Exception as exc:  # pragma: no cover - 网络
                log.warning("拉取第 %s 轮比赛失败：%s", gameweek, exc)
                return []

        results = await asyncio.gather(
            *(_one(rid, gw) for rid, gw in targets)
        )
        for ms in results:
            for m in ms:
                all_matches[m.match_id] = m

        return rounds, sorted(
            all_matches.values(),
            key=lambda x: (x.start_play or x.date_utc or "", x.match_id),
        )

    # ─── 积分榜 ───────────────────────────────
    async def fetch_standings(
        self, force: bool = False
    ) -> tuple[list[GroupStanding], list[KnockoutTie], list[Match]]:
        params = {"season_id": self.season_id}
        data = await self._client.get_json(
            ENDPOINTS.standing, params=params, force=force
        )
        content = data.get("content") or {}
        groups: list[GroupStanding] = []
        knockouts: list[KnockoutTie] = []
        knockout_matches: list[Match] = []

        for block in content.get("rounds") or []:
            template = block.get("template")
            block_content = block.get("content") or {}
            block_data = block_content.get("data") or []
            if template == "team_point_ranking_group":
                for grp in block_data:
                    if isinstance(grp, dict):
                        groups.append(GroupStanding.from_raw(grp))
            elif template == "team_point_ranking_knockout":
                for tie in block_data:
                    if isinstance(tie, dict):
                        ko = KnockoutTie.from_raw(tie)
                        knockouts.append(ko)
                        for sub in ko.matches:
                            knockout_matches.append(Match.from_raw(sub))
            elif template == "team_point_ranking_match":
                for m in block_data:
                    if isinstance(m, dict):
                        knockout_matches.append(Match.from_raw(m))
        return groups, knockouts, knockout_matches

    # ─── 排行榜 ───────────────────────────────
    async def fetch_ranking(
        self, rtype: RankingType, force: bool = False
    ) -> list[PlayerRanking]:
        params = {
            "season_id": self.season_id,
            "type": rtype.value,
            "version": 0,
            "refer": "person_ranking",
        }
        data = await self._client.get_json(
            ENDPOINTS.person_ranking, params=params, force=force
        )
        content = data.get("content") or {}
        return [
            PlayerRanking.from_raw(item, rtype) for item in content.get("data") or []
        ]

    # ─── 球队数据榜 ───────────────────────────
    async def fetch_team_ranking(
        self, rtype: RankingType, force: bool = False
    ) -> list[TeamRanking]:
        """拉取某项球队数据榜（进球 / 失球 / 角球 / 身价 …）。"""
        params = {
            "season_id": self.season_id,
            "type": rtype.value,
            "refer": "team_ranking",
        }
        data = await self._client.get_json(
            ENDPOINTS.team_ranking, params=params, force=force
        )
        content = data.get("content") or {}
        return [
            TeamRanking.from_raw(item, rtype) for item in content.get("data") or []
        ]

    # ─── 比赛实时赔率 ─────────────────────────
    async def fetch_match_odds(
        self, match_id: str, force: bool = False
    ) -> MatchOdds | None:
        """拉取某场比赛的实时赔率（欧赔 / 亚盘 / 大小球）。"""
        if not match_id:
            return None
        url = f"{ENDPOINTS.match_odds}/{match_id}"
        params = {"cmp_type": "soccer", "app": "dqd", "lang": "zh-cn", "platform": "android"}
        try:
            data = await self._client.get_json(url, params=params, force=force)
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取比赛赔率失败 %s：%s", match_id, exc)
            return None
        return MatchOdds.from_raw(data or {})

    # ─── 阵容 ─────────────────────────────────
    async def fetch_team_squad(
        self, team_id: str, force: bool = False
    ) -> list[SquadGroup]:
        """拉取某国家队的完整阵容（按位置分区）。"""
        url = f"{ENDPOINTS.team_member}/{team_id}"
        data = await self._client.get_json(
            url, params={"app": "dqd"}, cache_ttl=SQUAD_CACHE_TTL, force=force
        )
        content = data.get("data") or {}
        groups = [SquadGroup.from_raw(g) for g in (content.get("list") or [])]
        # 调整展示顺序：门将 → 后卫 → 中场 → 前锋 → 教练
        order = {"门将": 0, "后卫": 1, "中场": 2, "前锋": 3, "教练": 9}
        groups.sort(key=lambda g: order.get(g.title, 5))
        return groups

    # ─── 比赛阵容 ─────────────────────────────
    async def fetch_match_lineup(
        self, match_id: str, force: bool = False
    ) -> MatchLineup | None:
        """拉取某场比赛的阵容（首发 / 赛前预测 + 阵型 + 替补）。"""
        if not match_id:
            return None
        url = f"{ENDPOINTS.match_lineup}/{match_id}"
        try:
            data = await self._client.get_json(
                url, cache_ttl=LINEUP_CACHE_TTL, force=force
            )
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取比赛阵容失败 %s：%s", match_id, exc)
            return None
        return MatchLineup.from_raw(data or {})

    # ─── 球员个人档案 ──────────────────
    async def fetch_player_detail(
        self, person_id: str, force: bool = False
    ) -> PlayerDetail | None:
        """拉取任意球员的个人档案（含未参加本届世界杯的球员）。"""
        if not person_id:
            return None
        url = f"{ENDPOINTS.person_detail}/{person_id}"
        try:
            data = await self._client.get_json(
                url, cache_ttl=SQUAD_CACHE_TTL, force=force
            )
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取球员档案失败 %s：%s", person_id, exc)
            return None
        return PlayerDetail.from_raw(data or {})

    async def fetch_player_ability(
        self, person_id: str, force: bool = False
    ) -> PlayerAbility | None:
        """拉取球员 FC26 风能力值（OVR + 六维雷达）。"""
        if not person_id:
            return None
        url = f"{ENDPOINTS.player_ability}/{person_id}"
        try:
            data = await self._client.get_json(
                url, cache_ttl=SQUAD_CACHE_TTL, force=force
            )
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取球员能力值失败 %s：%s", person_id, exc)
            return None
        return PlayerAbility.from_raw(data or {})

    async def fetch_person_matches(
        self, person_id: str, force: bool = False
    ) -> list[PersonMatch]:
        """拉取球员近期比赛（含每场进球/助攻/评分/出场分钟）。

        对任意球员都有效（含未参加本届世界杯者）。失败时返回空列表，
        由调用方决定如何兜底（而非抛错导致整页渲染失败）。
        """
        if not person_id:
            return []
        url = f"{ENDPOINTS.person_matches}/{person_id}"
        try:
            data = await self._client.get_json(
                url, cache_ttl=SQUAD_CACHE_TTL, force=force
            )
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取球员近期比赛失败 %s：%s", person_id, exc)
            return []
        content = data or {}
        return [
            PersonMatch.from_raw(m)
            for m in (content.get("matches") or [])
            if isinstance(m, dict)
        ]

    # ─── 赛事资讯 ─────────────────────────────
    async def fetch_news(
        self, force: bool = False, *, target: int = 30, max_calls: int = 24
    ) -> list[NewsArticle]:
        """拉取最新世界杯资讯流（标题 / 缩略图 / 时间 / 原文链接）。

        懂球帝 ``article/relative`` 接口每次只返回 ~3 条「相关」资讯，单一种子
        远不够铺满资讯页。这里以种子文章为起点做**广度优先扩展**：把已返回文章
        的 id 继续作为新的种子拉取其相关流，去重累积，直到收集到 ``target`` 条
        或调用次数达到 ``max_calls`` 上限。接口结果有缓存，重复种子几乎零成本。

        失败时返回已收集到的部分（不让整页因资讯接口抖动而崩）。
        """
        from collections import deque

        seed = str(ENDPOINTS.news_seed_id)
        seen: dict[str, dict] = {}
        queue: deque[str] = deque([seed])
        visited: set[str] = {seed}
        calls = 0
        while queue and len(seen) < target and calls < max_calls:
            aid = queue.popleft()
            calls += 1
            url = f"{ENDPOINTS.news_relative}/{aid}"
            try:
                data = await self._client.get_json(
                    url, cache_ttl=NEWS_CACHE_TTL, force=force
                )
            except Exception as exc:  # pragma: no cover - 网络
                log.warning("拉取赛事资讯失败（seed=%s）：%s", aid, exc)
                continue
            for x in (data or {}).get("relative") or []:
                if (not isinstance(x, dict) or x.get("type") != "article"
                        or not x.get("title")):
                    continue
                xid = str(x.get("id") or "")
                if not xid:
                    continue
                seen.setdefault(xid, x)
                if xid not in visited:
                    visited.add(xid)
                    queue.append(xid)
        articles = [NewsArticle.from_raw(x) for x in seen.values()]
        # 按展示时间倒序（最新在前）
        articles.sort(key=lambda a: a.show_time or 0, reverse=True)
        return articles

    async def fetch_hot_comments(
        self, article_id: str, force: bool = False
    ) -> list[HotComment]:
        """拉取某篇文章的「热评」（球迷热议），按点赞数降序。

        失败时返回空列表，由调用方兜底。
        """
        if not article_id:
            return []
        url = (
            f"{ENDPOINTS.article_hot_base}/{article_id}/hot"
            "?size=30&version=576"
        )
        try:
            data = await self._client.get_json(
                url, cache_ttl=NEWS_CACHE_TTL, force=force
            )
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("拉取热评失败（article=%s）：%s", article_id, exc)
            return []
        content = (data or {}).get("data") or {}
        users = {
            str(u.get("id")): u
            for u in (content.get("user_list") or [])
            if isinstance(u, dict)
        }
        comments = [
            HotComment.from_raw(c, users)
            for c in (content.get("comment_list") or [])
            if isinstance(c, dict) and (c.get("content") or "").strip()
        ]
        comments.sort(key=lambda c: c.up, reverse=True)
        return comments

    # ─── 聚合：球队列表 ────────────────────────
    @staticmethod
    def teams_from_standings(
        groups: list[GroupStanding],
    ) -> list[Team]:
        out: list[Team] = []
        for g in groups:
            for ts in g.teams:
                out.append(
                    Team(
                        team_id=ts.team_id,
                        name=ts.team_name,
                        logo=ts.team_logo,
                        group=g.name,
                        rank=ts.rank,
                        points=ts.points,
                        matches_total=ts.matches_total,
                        matches_won=ts.matches_won,
                        matches_draw=ts.matches_draw,
                        matches_lost=ts.matches_lost,
                        goals_pro=ts.goals_pro,
                        goals_against=ts.goals_against,
                    )
                )
        return out

    @staticmethod
    def find_team_matches(team_id: str, matches: list[Match]) -> list[Match]:
        return [m for m in matches if m.team_a_id == team_id or m.team_b_id == team_id]

    @staticmethod
    def players_in_team(
        team_id: str, rankings: list[PlayerRanking]
    ) -> list[PlayerRanking]:
        return [p for p in rankings if p.team_id == team_id]
