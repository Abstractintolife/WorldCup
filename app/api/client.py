"""异步 HTTP 客户端 + 智能 JSON 缓存。

特性
----
* 使用 ``httpx.AsyncClient`` 并启用连接池
* 失败自动重试（指数退避）
* 同时维护内存 LRU 与磁盘缓存（``diskcache``）
* 提供 ``stale-while-revalidate`` 行为：网络错误时仍可返回旧缓存
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import diskcache
import httpx

from app.config import (
    ENDPOINTS,
    HTTP_BACKOFF,
    HTTP_RETRIES,
    HTTP_TIMEOUT_SECONDS,
    HTTP_USER_AGENT,
    JSON_CACHE_DIR,
    JSON_CACHE_TTL,
)

log = logging.getLogger(__name__)

# 过期数据在磁盘上的保留时长（秒）。条目「新鲜期」由 ``cache_ttl`` 决定，
# 但磁盘上会保留得更久，以支持「stale-while-revalidate」：哪怕过了新鲜期，
# 也先把旧数据**瞬间**返回给页面（零等待），同时在后台静默刷新。
# 这是消除「打开各种界面要等好久」的关键 —— 任何访问过的页面都秒开。
STALE_RETENTION_SECONDS = 60 * 60 * 24 * 7  # 7 天


class ApiClient:
    """单例式异步客户端。"""

    _instance: "ApiClient | None" = None

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_SECONDS,
            headers={"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
            http2=True,
        )
        self._cache = diskcache.Cache(str(JSON_CACHE_DIR), size_limit=64 * 1024 * 1024)
        self._mem: dict[str, tuple[float, Any]] = {}
        # 同一个 (url, params) 正在飞的协程任务 —— 多页面同时刷新时共享一次实际网络请求，
        # 解决日志里同一个接口重复打 N 次的问题（每条日志都翻倍）。
        self._inflight: dict[str, asyncio.Task[dict[str, Any]]] = {}

    # ───────────────── 单例 ─────────────────
    @classmethod
    def instance(cls) -> "ApiClient":
        if cls._instance is None:
            cls._instance = ApiClient()
        return cls._instance

    async def close(self) -> None:
        await self._client.aclose()
        self._cache.close()

    # ──────────────── 公共底层 ────────────────
    async def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        cache_ttl: int = JSON_CACHE_TTL,
        force: bool = False,
    ) -> dict[str, Any]:
        """请求一个 JSON 端点（带 stale-while-revalidate 缓存 + 同请求去重）。

        行为
        ----
        * **命中且新鲜** —— 直接返回，零网络。
        * **命中但已过新鲜期** —— **立即**返回旧数据（零等待），并在后台
          静默发起刷新；下次进入页面即是最新数据。这样任何访问过的页面
          都能秒开，彻底消除「打开各种界面要等好久」。
        * **未命中** —— await 真正的网络请求（仅首次访问该接口时发生）。
        """
        params = {**ENDPOINTS.common_params, **(params or {})}
        cache_key = self._key(url, params)

        if not force:
            entry = self._cache.get(cache_key)
            data, fresh_until = self._unwrap(entry)
            if data is not None:
                if time.time() < fresh_until:
                    return data           # 新鲜 → 秒回
                # 过期 → 先秒回旧数据，再后台刷新
                self._revalidate_in_background(url, params, cache_key, cache_ttl)
                return data

        # in-flight 去重：同 key 已有协程在飞，直接 await 它的结果，
        # 否则起一个新协程并把它登记为「飞行中」。
        existing = self._inflight.get(cache_key)
        if existing is not None and not existing.done():
            return await existing

        task = asyncio.ensure_future(
            self._fetch_with_retry(url, params, cache_key, cache_ttl)
        )
        self._inflight[cache_key] = task
        try:
            return await task
        finally:
            # 仅当当前任务仍是登记的 task 时才清除（避免 race）
            if self._inflight.get(cache_key) is task:
                self._inflight.pop(cache_key, None)

    def _revalidate_in_background(
        self,
        url: str,
        params: dict[str, Any],
        cache_key: str,
        cache_ttl: int,
    ) -> None:
        """后台静默刷新一个过期条目（不阻塞调用方，错误仅记录日志）。"""
        existing = self._inflight.get(cache_key)
        if existing is not None and not existing.done():
            return  # 已有刷新在飞，避免重复
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return
        if not loop.is_running():
            return
        task = asyncio.ensure_future(
            self._fetch_with_retry(url, params, cache_key, cache_ttl)
        )
        self._inflight[cache_key] = task

        def _done(t: asyncio.Task) -> None:
            if self._inflight.get(cache_key) is t:
                self._inflight.pop(cache_key, None)
            exc = t.exception() if not t.cancelled() else None
            if exc is not None:
                log.debug("后台刷新失败 %s：%s", cache_key, exc)

        task.add_done_callback(_done)

    @staticmethod
    def _unwrap(entry: Any) -> tuple[Any, float]:
        """把缓存条目拆成 (data, fresh_until)。

        兼容旧格式（直接存裸数据）—— 视为已过期，返回 fresh_until=0，
        从而立即复用旧数据并触发一次后台刷新。
        """
        if entry is None:
            return None, 0.0
        if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[1], (int, float)):
            return entry[0], float(entry[1])
        return entry, 0.0

    async def _fetch_with_retry(
        self,
        url: str,
        params: dict[str, Any],
        cache_key: str,
        cache_ttl: int,
    ) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(HTTP_RETRIES + 1):
            try:
                resp = await self._client.get(url, params=params)
                resp.raise_for_status()
                # 服务端某些响应不带正确 content-type，需要手动解析
                data = json.loads(resp.text) if resp.text else {}
                # 存 (数据, 新鲜截止时间)；磁盘保留更久以支持过期复用。
                fresh_until = time.time() + max(0, cache_ttl)
                self._cache.set(
                    cache_key,
                    (data, fresh_until),
                    expire=max(cache_ttl, STALE_RETENTION_SECONDS),
                )
                return data
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_exc = exc
                log.warning(
                    "GET %s 第 %d 次失败：%s", url, attempt + 1, exc
                )
                await asyncio.sleep(HTTP_BACKOFF * (2**attempt))

        # 全部重试失败 → 尝试返回过期缓存（stale-while-revalidate）
        stale = self._cache.get(cache_key, default=None, retry=True)
        if stale is not None:
            data, _ = self._unwrap(stale)
            if data is not None:
                log.warning("使用过期缓存：%s", cache_key)
                return data
        raise RuntimeError(f"接口请求失败：{url} ({last_exc})")

    async def get_bytes(
        self,
        url: str,
        *,
        timeout: float | None = None,
    ) -> bytes:
        """直接拉取二进制（用于图片）。"""
        resp = await self._client.get(url, timeout=timeout or HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.content

    # ──────────────── 工具 ────────────────
    @staticmethod
    def _key(url: str, params: dict[str, Any]) -> str:
        sorted_kv = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{url}?{sorted_kv}"

    def clear_cache(self) -> None:
        """清空 JSON 缓存（不会清空图片缓存）。"""
        self._cache.clear()
        self._mem.clear()
