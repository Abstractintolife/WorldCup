"""新闻资讯页：懂球帝世界杯资讯流。

把原概览页「赛事新闻」小面板的内容整合到独立页面，展示更多条目，
点击任一条打开「球迷热评」弹窗。数据来源：懂球帝 ``article/relative`` 接口。
"""
from __future__ import annotations

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.news import NewsArticle
from app.services.data_service import DataService
from app.ui.pages.base import BasePage
from app.ui.widgets.effects import stagger_fade
from app.ui.widgets.image_loader import RemoteImage
from app.ui.widgets.misc import Card
from app.ui.design.app_cursor import pointing_hand_cursor


class _NewsRow(QFrame):
    """单条资讯卡：缩略图 + 标题 + 时间。"""

    def __init__(self, article: NewsArticle, on_open) -> None:
        super().__init__()
        self._article = article
        self._on_open = on_open
        self.setObjectName("NewsRow")
        self.setCursor(pointing_hand_cursor())
        self.setFixedHeight(96)
        self.setStyleSheet(
            "QFrame#NewsRow{background: rgba(255,255,255,0.04);"
            " border:1px solid rgba(255,255,255,0.08); border-radius:14px;}"
            "QFrame#NewsRow:hover{background: rgba(255,255,255,0.09);"
            " border:1px solid rgba(0,191,255,0.40);}"
        )
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 16, 10)
        row.setSpacing(14)

        thumb = RemoteImage(size=120, shape="round", radius=10,
                            placeholder_color="#1d2436")
        thumb.setFixedSize(124, 74)
        if article.thumb:
            thumb.set_url(article.thumb)
        row.addWidget(thumb)

        col = QVBoxLayout()
        col.setSpacing(6)
        ttl = QLabel(article.title)
        ttl.setWordWrap(True)
        ttl.setStyleSheet("color:#FFFFFF; font-size:14px; font-weight:700; background:transparent;")
        col.addWidget(ttl, 1)
        meta = QLabel(f"🕒 {article.time_text}   ·   懂球帝")
        meta.setStyleSheet("color:#6B7689; font-size:11px; font-weight:600; background:transparent;")
        col.addWidget(meta)
        row.addLayout(col, 1)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton and self._on_open:
            self._on_open(self._article)
        super().mousePressEvent(ev)


class NewsPage(BasePage):
    title = "新闻资讯"
    subtitle = "TOURNAMENT NEWS · 懂球帝资讯流"

    _PAGE = 12   # 每次渲染/追加的条数

    def __init__(self, service: DataService) -> None:
        super().__init__()
        self._service = service
        self._articles: list[NewsArticle] = []
        self._shown = 0
        self._auto_refreshing = False

        host = self.content_widget()
        outer = QVBoxLayout(host)
        outer.setContentsMargins(24, 20, 24, 16)
        outer.setSpacing(14)

        head = Card(padding=16)
        h_lay = QVBoxLayout(head)
        h_lay.setContentsMargins(20, 12, 20, 12)
        h_lay.setSpacing(4)
        title = QLabel("📰  赛事资讯")
        title.setStyleSheet("font-size:18px; font-weight:900;")
        h_lay.addWidget(title)
        sub = QLabel("2026 世界杯实时新闻 · 向下滚动自动加载更多 / 到底刷新 · 点击查看球迷热评")
        sub.setStyleSheet("color:#B0BEC5; font-size:12px; font-weight:600;")
        h_lay.addWidget(sub)
        outer.addWidget(head)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)
        outer.addWidget(self._scroll, 1)
        self._list_layout: QVBoxLayout | None = None
        self._footer: QLabel | None = None

    def _build_host(self) -> None:
        host = QWidget()
        self._scroll.setWidget(host)
        self._list_layout = QVBoxLayout(host)
        self._list_layout.setContentsMargins(2, 2, 2, 16)
        self._list_layout.setSpacing(10)
        # 底部状态/加载提示（始终位于列表末尾）
        self._footer = QLabel("")
        self._footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer.setStyleSheet("color:#6B7689; font-size:12px; padding:10px;")
        self._list_layout.addWidget(self._footer)
        self._list_layout.addStretch(1)

    def refresh(self, force: bool = False) -> None:
        async def runner() -> None:
            articles = await self._service.fetch_news(force=force)
            self._auto_refreshing = False
            self._render(articles)
        self.run_async(runner)

    def _render(self, articles: list[NewsArticle]) -> None:
        self._articles = articles
        self._shown = 0
        self._build_host()
        if not articles:
            self._footer.setText("暂无资讯")
            return
        self._append_more()

    def _append_more(self) -> None:
        """把后续若干条插入到列表（footer 之前）。"""
        if self._list_layout is None:
            return
        start, end = self._shown, min(self._shown + self._PAGE, len(self._articles))
        if start >= end:
            return
        # footer 与 stretch 固定在末尾两项，插入位置 = 现有条数
        insert_at = self._shown
        rows: list[QWidget] = []
        for a in self._articles[start:end]:
            row = _NewsRow(a, self._open_comments)
            self._list_layout.insertWidget(insert_at, row)
            insert_at += 1
            rows.append(row)
        self._shown = end
        stagger_fade(rows, step=24, dx=0, dy=0)
        remaining = len(self._articles) - self._shown
        if remaining > 0:
            self._footer.setText(f"向下滚动加载更多 · 还有 {remaining} 条")
        else:
            self._footer.setText(f"已展示全部 {self._shown} 条 · 继续下滑可刷新最新")

    def _on_scroll(self, value: int) -> None:
        bar = self._scroll.verticalScrollBar()
        if bar.maximum() <= 0 or value < bar.maximum() - 8:
            return
        # 到达底部
        if self._shown < len(self._articles):
            self._append_more()
        elif not self._auto_refreshing and self._articles:
            # 已全部展示 → 触底刷新拉取最新
            self._auto_refreshing = True
            if self._footer is not None:
                self._footer.setText("正在刷新最新资讯…")
            self.refresh(force=True)

    def _open_comments(self, article: NewsArticle) -> None:
        try:
            from app.ui.widgets.comments_dialog import HotCommentsDialog
            dlg = HotCommentsDialog(self._service, article, parent=self.window())
            dlg.exec()
        except Exception:
            if article.url:
                QDesktopServices.openUrl(QUrl(article.url))
