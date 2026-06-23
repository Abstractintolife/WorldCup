# 🏆 世界杯赛事终端 — World Cup Console

> 一款基于 **Python 3.12 + PyQt6** 打造的 2026 FIFA 世界杯桌面应用，UI 极致精美、功能机智实用。
> 数据来源：懂球帝公开数据接口（`season_id=26123` = 2026 World Cup）。

![](docs/preview.png)

## ✨ 特性总览

| 板块 | 功能 |
|------|------|
| 🏠 **仪表盘** | 焦点比赛 hero 横幅 / 4 项实时统计指标（总比赛 / 已结束 / 直播中 / 待开赛）/ 直播 + 即将开赛比赛卡片 / 射手助攻 TOP3 |
| 📅 **赛程大厅** | 全部 64 场比赛 · 按 **轮次 / 状态 / 日期** 三维筛选 · 关键字模糊搜索 · 日期分段陈列 |
| 🏆 **积分榜** | A-L **12 个小组** 的卡片视图 + 名次配色 + 出线图例 · 淘汰赛对阵图 |
| ⚽ **射手榜** | TOP 30 射手 · 头像 + 队徽 + 进球数 · 渐变进度条排名条 |
| 🅰️ **助攻榜** | TOP 助攻 · 同上交互 |
| 🛡 **国家队** | 全部参赛队伍卡片网格 · 关键字搜索 · 排名 / 积分 / 净胜球速览 |
| 🏟 **球场** | 内置 2026 世界杯 16 座主办球场（美 / 加 / 墨）· 容量 / 落成年 / 角色 / 简介 |
| 🛡 **球队详情** | 头部数据条 + 当家球星（射手 / 助攻）+ **完整阵容（门将/后卫/中场/前锋/教练，含球衣号、年龄、队长标识）** + 全部赛程 + 收藏 |
| 👤 **球员详情** | 个人头像 + 进球 / 助攻 / 点球 / 排名计数动画 + 所属队全部比赛 + 收藏 |
| ⚽ **比赛详情** | 渐变 hero · 双方 logo · 比分 · 完整元数据 · 收藏 |
| ⭐ **收藏夹** | 球队 / 球员 / 比赛 三列；本地 JSON 持久化 |
| 🔎 **全局搜索** | 顶栏输入回车 → 聚合命中（球队 / 球员 / 比赛 / 球场） |
| 🌗 **主题切换** | 暗色（极光紫黑 + 金色冠冕）/ 亮色（草坪绿白）一键切换 |
| 🔄 **自动刷新** | 仪表盘 / 赛程 / 比赛详情每 30 秒自动重拉一次实时数据 |
| 🚀 **极速体验** | `httpx` HTTP/2 + `diskcache` JSON 缓存（60s）+ 30 天图片磁盘缓存 + stale-while-revalidate |

## 📁 项目结构

```
shijiebei/
├── main.py                    # 入口（asyncio + qasync + Qt 事件循环）
├── requirements.txt
└── app/
    ├── config.py              # API 端点 / 缓存路径 / UI 常量
    ├── api/
    │   └── client.py          # 异步 httpx 客户端 + diskcache + 重试
    ├── models/                # Pydantic v2 数据模型
    │   ├── match.py           # 比赛 + 状态枚举 + 轮次
    │   ├── standing.py        # 小组积分 + 球队行 + 淘汰赛对阵
    │   ├── player.py          # 球员排行（射手 / 助攻）
    │   ├── team.py            # 国家队
    │   └── stadium.py         # 球场
    ├── services/
    │   ├── data_service.py    # 聚合 4 个接口的高层服务
    │   ├── image_service.py   # 异步图片下载 + 磁盘缓存（QPixmap 信号）
    │   ├── stadiums_data.py   # 内置 2026 WC 16 座球场数据
    │   └── favorites.py       # 收藏夹 + 设置（JSON 持久化）
    ├── utils/time_utils.py    # 日期 / 相对时间格式化
    └── ui/
        ├── theme.py           # 暗 / 亮主题调色板 + QSS 全局样式
        ├── main_window.py     # 主窗口（侧边栏 / 顶部栏 / 页面栈）
        ├── widgets/           # 自绘组件库
        │   ├── hero_banner.py     # 渐变焦点比赛横幅
        │   ├── match_card.py      # 比赛卡片
        │   ├── group_card.py      # 单组积分榜卡片
        │   ├── ranking_row.py     # 射手榜 / 助攻榜的进度条行
        │   ├── team_logo.py       # 圆形队徽
        │   ├── player_avatar.py   # 球员圆形头像
        │   ├── image_loader.py    # 异步远程图片（圆 / 圆角 / 矩形）
        │   ├── flow_layout.py     # 自动换行的 FlowLayout
        │   ├── nav_sidebar.py     # 侧边导航（含品牌区）
        │   ├── top_bar.py         # 顶部栏（标题 / 搜索 / 主题 / 刷新）
        │   ├── favorite_button.py # ★ 收藏切换按钮
        │   └── misc.py            # Card / Spinner / StatusChip / CountUpLabel
        └── pages/             # 主要页面
            ├── home_page.py        # 仪表盘
            ├── schedule_page.py    # 赛程大厅
            ├── standings_page.py   # 积分榜（小组 / 淘汰赛）
            ├── scorers_page.py     # 射手 + 助攻共用同一 RankingPage
            ├── teams_page.py       # 国家队总览
            ├── stadiums_page.py    # 球场
            ├── team_detail_page.py
            ├── player_detail_page.py
            ├── match_detail_page.py
            ├── favorites_page.py
            ├── search_page.py
            └── base.py             # 统一空态 / 加载 / 错误态基类
```

## 🚀 安装与运行

```bash
# 1) 进入项目目录
cd shijiebei

# 2) （推荐）创建虚拟环境 —— 请使用 Python 3.13 或 3.12
python3.13 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3) 安装依赖
pip install -r requirements.txt

# 4) 运行
python main.py
```

> 系统要求：**Python 3.12 或 3.13**。
> ⚠️ 暂不支持 **Python 3.14**：底层异步库 `qasync` 官方支持范围为 `>=3.8, <3.14`，
> 在 3.14 上其内部定时器无法启动（报 `QObject::startTimer: Timers can only be used
> with threads started with QThread`），导致窗口无法打开。请改用 Python 3.13。
> macOS / Windows / Linux 均可。

## 🛠 数据接口

应用通过以下四个公开接口构建全部数据视图（`season_id=26123` 切换赛季即切换联赛）：

| 接口 | 用途 |
|------|------|
| `GET sport-data.dongqiudi.com/soccer/biz/data/schedule` | 完整赛程 + match_id + 实时比分 |
| `GET sport-data.dongqiudi.com/soccer/biz/data/standing` | 12 个小组积分榜 + 淘汰赛对阵 |
| `GET api.dongqiudi.com/data/v1/person_ranking/0?type=goals` | 射手榜 |
| `GET api.dongqiudi.com/data/v1/person_ranking/0?type=assists` | 助攻榜 |

接口返回 JSON 由 `app/api/client.py` 异步拉取，并以 60 秒为窗口缓存于本地磁盘；
图片资源（队徽 / 头像）则缓存 30 天。

## ⌨️ 交互速查

| 操作 | 触发 |
|------|------|
| 切换页面 | 左侧导航 |
| 查看比赛详情 | 单击任意比赛卡片 |
| 查看球队详情 | 单击国家队卡片 / 积分榜行 / 比赛 hero 上的队徽 |
| 查看球员详情 | 单击射手榜或助攻榜行 |
| 全局搜索 | 顶栏输入关键字后按回车 |
| 强制刷新 | 顶栏「⟳ 刷新」按钮 |
| 主题切换 | 顶栏「☾ 主题」按钮（自动持久化） |
| 添加 / 移除收藏 | 各详情页右上角 ★ |
| 查看完整阵容 | 进入任意球队详情页向下滚动 |
| 自动刷新 | 仪表盘 / 赛程 / 比赛详情每 30 秒静默更新 |

## 📝 鸣谢与免责

* 数据来源 © 懂球帝（dongqiudi.com）公开接口；本应用仅作学习展示之用。
* 球场资料整理自 FIFA 官方公告与各球场公开资料。

## 📄 许可

MIT
