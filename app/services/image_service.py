"""异步图片加载 + 磁盘缓存（用于国旗、头像、队徽）。

UI 控件向 ``ImageService`` 订阅 URL，加载完成后通过 Qt 信号回调。
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap

from app.api.client import ApiClient
from app.config import IMAGE_CACHE_DIR

log = logging.getLogger(__name__)


def _cache_path(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    suffix = Path(url.split("?")[0]).suffix.lower()
    if suffix not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        suffix = ".img"
    return IMAGE_CACHE_DIR / f"{h}{suffix}"


class ImageService(QObject):
    """全局单例，所有需要图片的控件都通过它请求。"""

    image_ready = pyqtSignal(str, QPixmap)  # url, pixmap

    _instance: "ImageService | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._client = ApiClient.instance()
        self._inflight: dict[str, asyncio.Task] = {}
        self._mem: dict[str, QPixmap] = {}
        # 失败 URL 负缓存：被服务器 404/Wikimedia 重定向 404 的死链不再反复重试
        self._failed: set[str] = set()

    @classmethod
    def instance(cls) -> "ImageService":
        if cls._instance is None:
            cls._instance = ImageService()
        return cls._instance

    # ──────────────── 公共接口 ────────────────
    def get_cached(self, url: str | None) -> QPixmap | None:
        """返回内存或磁盘命中的 QPixmap，否则 None。"""
        if not url:
            return None
        if url in self._mem:
            return self._mem[url]
        # 本地文件路径（球员高清图存在仓库 app/assets/players/ 下）：直接加载
        if "://" not in url:
            lp = Path(url)
            if lp.exists():
                pm = QPixmap(str(lp))
                if not pm.isNull():
                    self._mem[url] = pm
                    return pm
            return None
        path = _cache_path(url)
        if path.exists():
            pm = QPixmap(str(path))
            if not pm.isNull():
                self._mem[url] = pm
                return pm
        return None

    def request(self, url: str | None) -> QPixmap | None:
        """请求图片：若已缓存立即返回；否则异步下载并稍后通过信号通知。"""
        if not url:
            return None
        # 死链短路 —— 避免每次启动都重试已知 404
        if url in self._failed:
            return None
        cached = self.get_cached(url)
        if cached is not None:
            return cached
        if url in self._inflight:
            return None
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._download(url))
        self._inflight[url] = task
        return None

    async def _download(self, url: str) -> None:
        try:
            content = await self._client.get_bytes(url)
            path = _cache_path(url)
            path.write_bytes(content)
            pm = QPixmap()
            if pm.loadFromData(content):
                self._mem[url] = pm
                self.image_ready.emit(url, pm)
        except Exception as exc:  # pragma: no cover - 网络
            log.warning("图片下载失败 %s: %s", url, exc)
            # 把失败 URL 记入负缓存，避免后续滚动 / 翻页反复重试
            self._failed.add(url)
        finally:
            self._inflight.pop(url, None)
