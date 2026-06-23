"""日期 / 时间工具。

API 端的时间字段约定
---------------------
* ``start_play`` —— 由懂球帝 schedule 返回的开赛时间字段。
  实际抓包发现该值在不同栏位之间并不一致（部分接口返回 UTC，
  部分接口返回北京时间）。直接把它当本地时间显示就会偏 8 小时
  —— 这正是用户反馈「赛事时间不对」的根因。
* ``date_utc`` + ``time_utc`` —— **明确的 UTC** 字段，可用作权威源。

本模块把所有比赛时间统一规范化为「带时区的 datetime（UTC）」，
显示时再转到「本地时区」，彻底消除 8 小时偏差。

时区配置
---------
默认本地时区为 ``Asia/Shanghai``。如需自定义，设置环境变量
``WC_LOCAL_TZ`` 即可（如 ``Europe/London`` / ``America/New_York``）。
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Optional

_TZ_NAME = os.environ.get("WC_LOCAL_TZ", "Asia/Shanghai")

try:  # Python 3.9+ 自带；3.13 可用
    from zoneinfo import ZoneInfo
    _LOCAL_TZ: tzinfo = ZoneInfo(_TZ_NAME)
except Exception:  # pragma: no cover - 兜底
    _LOCAL_TZ = timezone(timedelta(hours=8))

UTC = timezone.utc

WEEKDAYS_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# ─── 解析 ──────────────────────────────────────────────────
def parse_utc(date_str: str | None, time_str: str | None) -> datetime | None:
    """把 ``date_utc + time_utc`` 解析为带 UTC 时区的 datetime。"""
    if not date_str:
        return None
    raw = f"{date_str.strip()} {(time_str or '00:00:00').strip()}"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def to_local(dt: datetime | None) -> datetime | None:
    """把任意 datetime 转换为本地时区。

    若 dt 是 naive（没有 tzinfo），按 UTC 处理 —— 这是后端最常见的情况。
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(_LOCAL_TZ)


# ─── 格式化 ────────────────────────────────────────────────
def fmt_date(dt: datetime | None) -> str:
    dt = to_local(dt)
    if dt is None:
        return "—"
    return dt.strftime("%m月%d日") + " " + WEEKDAYS_ZH[dt.weekday()]


def fmt_short_date(dt: datetime | None) -> str:
    """``06.14 周日`` —— 卡片角标用。"""
    dt = to_local(dt)
    if dt is None:
        return "—"
    return dt.strftime("%m.%d") + " " + WEEKDAYS_ZH[dt.weekday()]


def fmt_time(dt: datetime | None) -> str:
    dt = to_local(dt)
    if dt is None:
        return "—"
    return dt.strftime("%H:%M")


def fmt_datetime(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return f"{fmt_date(dt)} {fmt_time(dt)}"


def is_today(dt: datetime | None) -> bool:
    dt = to_local(dt)
    if dt is None:
        return False
    now = datetime.now(_LOCAL_TZ)
    return dt.date() == now.date()


def fmt_relative(dt: datetime | None) -> str:
    """返回相对时间描述：``还有 3 小时``、``2 天前`` 等。"""
    dt = to_local(dt)
    if dt is None:
        return "—"
    now = datetime.now(_LOCAL_TZ)
    delta = dt - now
    seconds = int(delta.total_seconds())
    if seconds == 0:
        return "现在"
    future = seconds > 0
    seconds = abs(seconds)
    if seconds < 60:
        amount, unit = seconds, "秒"
    elif seconds < 3600:
        amount, unit = seconds // 60, "分钟"
    elif seconds < 86400:
        amount, unit = seconds // 3600, "小时"
    elif seconds < 86400 * 30:
        amount, unit = seconds // 86400, "天"
    elif seconds < 86400 * 365:
        amount, unit = seconds // (86400 * 30), "个月"
    else:
        amount, unit = seconds // (86400 * 365), "年"
    return f"还有 {amount} {unit}" if future else f"{amount} {unit}前"


def days_until(dt: datetime | None) -> Optional[int]:
    dt = to_local(dt)
    if dt is None:
        return None
    now = datetime.now(_LOCAL_TZ)
    return (dt.date() - now.date()).days


def floor_minute(td: timedelta) -> int:
    return int(td.total_seconds() // 60)


def local_now() -> datetime:
    """带时区的「本地当前时间」。"""
    return datetime.now(_LOCAL_TZ)
