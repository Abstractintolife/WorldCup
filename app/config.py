"""全局配置：API 端点、缓存路径、UI 常量。

把所有「魔法字符串」集中在此，改一次到处生效。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_cache_dir, user_data_dir

# ─── 应用元信息 ──────────────────────────────────────────────
APP_VENDOR = "kiro"
APP_NAME = "WorldCupConsole"
APP_TITLE_ZH = "世界杯赛事终端"
APP_TITLE_EN = "FIFA World Cup Console 2026"

# ─── 路径 ───────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
# 随软件打包的国旗位图目录（assets/flags/{code}.png）—— 本地直读，免下载、零延迟
FLAGS_DIR = ASSETS_DIR / "flags"

CACHE_DIR = Path(user_cache_dir(APP_NAME, APP_VENDOR))
DATA_DIR = Path(user_data_dir(APP_NAME, APP_VENDOR))
IMAGE_CACHE_DIR = CACHE_DIR / "images"
JSON_CACHE_DIR = CACHE_DIR / "json"
FAVORITES_FILE = DATA_DIR / "favorites.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

for _d in (CACHE_DIR, DATA_DIR, IMAGE_CACHE_DIR, JSON_CACHE_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# ─── 接口 ───────────────────────────────────────────────────
@dataclass(frozen=True)
class Endpoints:
    """懂球帝（dongqiudi）公开数据接口集合。"""

    # 默认赛季 ID — 2026 FIFA World Cup
    default_season_id: int = 26123

    schedule: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/data/schedule"
    )
    standing: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/data/standing"
    )
    person_ranking: str = (
        "https://api.dongqiudi.com/data/v1/person_ranking/0"
    )
    # 国家队阵容（按 /{team_id} 追加）—— 教练 / 门将 / 后卫 / 中场 / 前锋
    team_member: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/dqd/v1/team/member_v2"
    )
    # 球员个人主页档案（按 /{person_id} 追加）—— 身高/体重/惯用脚/国籍/俱乐部/奖杯
    person_detail: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/dqd/v1/person/detail"
    )
    # 球员 FC26 风能力值（按 /{person_id} 追加）—— OVR + 六维雷达 + 细项
    player_ability: str = (
        "https://sport-data.dongqiudi.com/soccer/data/sofifa/v1/player_ability"
    )
    # 比赛阵容（按 /{match_id} 追加）—— 首发/预测阵容 + 阵型 + 替补 + 场地/裁判
    match_lineup: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/dqd/v1/match/lineup"
    )
    # 球员近期比赛（按 /{person_id} 追加）—— 含每场进球/助攻/评分/出场分钟，
    # 对任意球员（含未参加本届世界杯者）都有效。
    person_matches: str = (
        "https://sport-data.dongqiudi.com/soccer/biz/dqd/person/matches"
    )
    # 赛事资讯流（按 /{seed_id} 追加）—— 返回与该篇世界杯文章相关的最新资讯，
    # 每条含 标题 / 缩略图 / 时间 / 文章 id。用于概览页「赛事新闻」与资讯页。
    news_relative: str = (
        "https://api.dongqiudi.com/v2/article/relative"
    )
    # 资讯流的「种子」文章 id（世界杯专题文章），相关流会持续滚动最新内容。
    news_seed_id: int = 5960042
    # 文章「热评」基址（按 /{article_id}/hot 追加）—— 返回某篇文章下的
    # 球迷热议（评论正文/点赞/时间 + 作者昵称头像）。用于新闻热评弹窗。
    article_hot_base: str = "https://api.dongqiudi.com/v2/article"

    # 默认查询参数
    common_params: dict = field(
        default_factory=lambda: {
            "app": "dqd",
            "version": "830",
            "platform": "miniprogram",
            "language": "zh-cn",
            "from": "msite_com",
        }
    )


ENDPOINTS = Endpoints()


# ─── HTTP 配置 ──────────────────────────────────────────────
HTTP_TIMEOUT_SECONDS = 12.0
HTTP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HTTP_RETRIES = 2
HTTP_BACKOFF = 0.4

# JSON 缓存有效期（秒）—— 实时数据短缓存，方便手动刷新
JSON_CACHE_TTL = 60
SQUAD_CACHE_TTL = 60 * 60 * 6     # 阵容变化较少 —— 缓存 6 小时
LINEUP_CACHE_TTL = 60 * 5         # 比赛阵容（赛前预测 → 首发）—— 缓存 5 分钟
NEWS_CACHE_TTL = 60 * 3           # 赛事资讯滚动较快 —— 缓存 3 分钟
IMAGE_CACHE_TTL = 60 * 60 * 24 * 30  # 图片缓存 30 天


# ─── UI 常量 ────────────────────────────────────────────────
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 800
SIDEBAR_WIDTH = 232
TOPBAR_HEIGHT = 64

# 自动轮询（毫秒），仅用于直播中的页面
LIVE_REFRESH_INTERVAL_MS = 30 * 1000

# 默认主题
DEFAULT_THEME = "dark"


# ─── 性能 / 动画 ─────────────────────────────────────────────
# 这些参数共同决定「动效流畅度 vs CPU 占用」的平衡，全部可用环境变量覆盖。
def _clampf(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# 动画目标帧率（动态背景 / 粒子 / 加载圈等）。默认 60；想要更顺滑可设
# ``WC_FPS=144``，省电可设更低。注意：动态背景是 CPU 软件栅格化，过高的
# 帧率会增加占用 —— 真正消除「卡顿」的是下方的离屏缩放与粒子系数。
ANIM_FPS = int(_clampf(_env_int("WC_FPS", 60), 20, 240))
ANIM_INTERVAL_MS = max(4, round(1000 / ANIM_FPS))

# 动态背景离屏渲染缩放（0.3~1.0）。<1 时背景先画到低分辨率位图再放大，
# 全窗背景的栅格化开销随之平方级下降（0.6 ≈ 只有原来 36% 的像素工作量）。
BACKDROP_RENDER_SCALE = _clampf(_env_float("WC_BACKDROP_SCALE", 0.6), 0.3, 1.0)

# 背景粒子数量系数（0.1~1.0）。调低可进一步降负载。
BACKDROP_PARTICLE_SCALE = _clampf(_env_float("WC_PARTICLE_SCALE", 0.65), 0.1, 1.0)

# 省电 / 低性能模式：禁用所有动态背景动画（仅保留静态渐变），WC_LITE=1 开启。
LOW_PERF = os.environ.get("WC_LITE", "0").strip().lower() in ("1", "true", "yes")
