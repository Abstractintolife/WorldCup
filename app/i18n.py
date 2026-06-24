"""轻量国际化（i18n）—— 中文 / 英文界面语言切换。

设计
----
* 单例 :class:`_I18N`（``QObject``）持有当前语言（``"zh"`` / ``"en"``）并在切换时
  发出 :pyattr:`language_changed` 信号，供各界面元件即时重译（retranslate）。
* :func:`tr` 把界面文案从中文翻成英文（语言为 ``en`` 时）：优先用调用方显式
  传入的 ``en`` 译文，否则查内置词表 :data:`_UI_TEXT`，再否则原样返回中文。
* 语言由设置持久化（见 ``MainWindow``），下次启动沿用。

范围
----
本模块只负责**界面文案**（导航 / 标题栏 / 顶栏 / 子标题 / 设置 / 按钮等）。
赛事**数据本身**（球队 / 球员 / 新闻等中文名）来自中文数据源，不在翻译范围内。
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

#: 界面文案词表（中文 → 英文）。仅收录常见的持久化 chrome 文案。
_UI_TEXT: dict[str, str] = {
    # 导航
    "概览": "Overview",
    "赛程中心": "Schedule",
    "实时比赛": "Live Match",
    "球队": "Teams",
    "球员": "Players",
    "数据分析": "Analytics",
    "积分榜": "Standings",
    "射手榜": "Top Scorers",
    "场馆地图": "Venue Map",
    "新闻资讯": "News",
    "收藏夹": "Favorites",
    "设置": "Settings",
    # 标题栏 / 应用
    "世界杯赛事终端": "FIFA World Cup Console 2026",
    "最小化": "Minimize",
    "最大化 / 还原": "Maximize / Restore",
    "关闭": "Close",
    # 顶栏
    "搜索球队 / 球员 / 比赛…": "Search teams / players / matches…",
    "通知 · 查看最新资讯": "Notifications · latest news",
    "个人中心": "Profile",
    # 子标题栏
    "2026 美加墨世界杯 · 实时数据总览": "2026 FIFA World Cup · Live Data Overview",
    "OVERVIEW · 数据来源：懂球帝公开接口": "OVERVIEW · Source: Dongqiudi public API",
    "实时数据已连接": "Live data connected",
    "实时数据已断开": "Live data disconnected",
    # 设置面板
    "完成": "Done",
    "国际足联世界排名": "FIFA World Ranking",
    "点击查看对应榜单": "Click to open the related ranking",
    # 语言切换提示
    "已切换为英文界面（赛事数据仍为中文数据源）": (
        "Switched to English UI (match data stays from the Chinese source)"
    ),
    "已切换为中文界面": "Switched to Chinese UI",
}


class _I18N(QObject):
    """界面语言单例。"""

    #: 语言切换信号（载荷为 ``"zh"`` / ``"en"``）。
    language_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._lang = "zh"

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> None:
        norm = "en" if str(lang).lower().startswith("en") else "zh"
        if norm == self._lang:
            return
        self._lang = norm
        self.language_changed.emit(norm)

    def tr(self, zh: str, en: str | None = None) -> str:
        if self._lang == "en":
            if en is not None:
                return en
            return _UI_TEXT.get(zh, zh)
        return zh


_INSTANCE = _I18N()


def i18n() -> _I18N:
    """返回 i18n 单例（用于 ``connect(language_changed)``）。"""
    return _INSTANCE


def tr(zh: str, en: str | None = None) -> str:
    """翻译界面文案：英文模式下返回英文，否则返回中文原文。"""
    return _INSTANCE.tr(zh, en)


def set_language(lang: str) -> None:
    _INSTANCE.set_language(lang)


def current_language() -> str:
    return _INSTANCE.language


def is_english() -> bool:
    return _INSTANCE.language == "en"
