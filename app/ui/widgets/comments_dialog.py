"""新闻「热评」弹窗 —— 展示某篇资讯下的球迷热议。

数据来自 ``DataService.fetch_hot_comments(article_id)``（懂球帝 article/hot 接口）。
弹窗顶部为文章标题 + 「查看原文」按钮，正文为按点赞降序排列的评论卡片
（头像 + 昵称 + 正文 + 👍 点赞数 + 时间 + 💬 回复数）。
"""
from __future__ import annotations

import asyncio
import logging

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.news import HotComment, NewsArticle
from app.services.data_service import DataService
from app.ui.widgets.image_loader import RemoteImage

log = logging.getLogger(__name__)

_PRIMARY = "#00BFFF"
_TEXT = "#FFFFFF"
_DIM = "#B0BEC5"
_FAINT = "#6B7689"
_GOLD = "#FFD700"


class HotCommentsDialog(QDialog):
    """某篇资讯的热评弹窗。"""

    def __init__(self, service: DataService, article: NewsArticle,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._article = article
        self.setWindowTitle("球迷热议")
        self.setMinimumSize(480, 600)
        self.setStyleSheet(
            "QDialog{background:#0B1020;}"
            f"QLabel{{color:{_TEXT};}}"
            "QPushButton{background: rgba(255,255,255,0.08); color:#fff;"
            " border:1px solid rgba(255,255,255,0.16); border-radius:9px;"
            " padding:7px 14px; font-size:12.5px; font-weight:700;}"
            "QPushButton:hover{background: rgba(255,255,255,0.16);}"
            "QScrollArea{border:none; background:transparent;}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        # ── 标题 + 查看原文 ──
        head = QVBoxLayout()
        head.setSpacing(8)
        title = QLabel(article.title or "资讯热评")
        title.setWordWrap(True)
        title.setStyleSheet(f"color:{_TEXT}; font-size:16px; font-weight:900;")
        head.addWidget(title)
        meta = QHBoxLayout()
        sub = QLabel(f"🔥 球迷热议 · {article.time_text}")
        sub.setStyleSheet(f"color:{_DIM}; font-size:11.5px; font-weight:700;")
        meta.addWidget(sub)
        meta.addStretch(1)
        if article.url:
            open_btn = QPushButton("查看原文 ↗")
            open_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(article.url)))
            meta.addWidget(open_btn)
        head.addLayout(meta)
        root.addLayout(head)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(255,255,255,0.08);")
        root.addWidget(line)

        # ── 评论滚动区 ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_host = QWidget()
        self._list = QVBoxLayout(self._list_host)
        self._list.setContentsMargins(0, 0, 4, 0)
        self._list.setSpacing(10)
        self._scroll.setWidget(self._list_host)
        root.addWidget(self._scroll, 1)

        self._status = QLabel("正在加载热评…")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(f"color:{_FAINT}; font-size:13px; padding:20px;")
        self._list.addWidget(self._status)
        self._list.addStretch(1)

        self._load()

    # ── 加载 ───────────────────────────────
    def _load(self) -> None:
        async def runner() -> None:
            try:
                comments = await self._service.fetch_hot_comments(
                    self._article.article_id)
            except Exception as exc:  # pragma: no cover - 网络
                log.warning("热评加载失败：%s", exc)
                comments = []
            self._populate(comments)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(runner())
                return
        except RuntimeError:
            pass
        # 无运行中的事件循环时同步兜底
        asyncio.ensure_future(runner())

    def _populate(self, comments: list[HotComment]) -> None:
        # 清空旧内容
        while self._list.count():
            it = self._list.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
        if not comments:
            empty = QLabel("暂无热评，点「查看原文」到原页面参与讨论 💬")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color:{_FAINT}; font-size:13px; padding:24px;")
            self._list.addWidget(empty)
            self._list.addStretch(1)
            return
        for c in comments:
            self._list.addWidget(self._comment_card(c))
        self._list.addStretch(1)

    def _comment_card(self, c: HotComment) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame{background: rgba(255,255,255,0.04); border-radius:12px;"
            " border:1px solid rgba(255,255,255,0.07);}")
        row = QHBoxLayout(card)
        row.setContentsMargins(12, 11, 12, 11)
        row.setSpacing(11)

        avatar = RemoteImage(size=38, shape="round", radius=19,
                             placeholder_color="#243049")
        avatar.setFixedSize(38, 38)
        if c.avatar:
            avatar.set_url(c.avatar)
        row.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(5)
        top = QHBoxLayout()
        name = QLabel(c.user_name)
        name.setStyleSheet(f"color:{_GOLD}; font-size:12.5px; font-weight:800;")
        top.addWidget(name)
        top.addStretch(1)
        when = QLabel(c.created_at)
        when.setStyleSheet(f"color:{_FAINT}; font-size:10px;")
        top.addWidget(when)
        col.addLayout(top)

        body = QLabel(c.content)
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{_TEXT}; font-size:13px; line-height:160%;")
        col.addWidget(body)

        foot = QHBoxLayout()
        likes = QLabel(f"👍 {c.up}")
        likes.setStyleSheet(f"color:{_PRIMARY}; font-size:11px; font-weight:700;")
        foot.addWidget(likes)
        if c.reply_total:
            replies = QLabel(f"💬 {c.reply_total}")
            replies.setStyleSheet(f"color:{_DIM}; font-size:11px; font-weight:700;")
            foot.addWidget(replies)
        foot.addStretch(1)
        col.addLayout(foot)

        row.addLayout(col, 1)
        return card
