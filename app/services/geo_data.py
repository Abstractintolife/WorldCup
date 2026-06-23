"""地理数据：国家队经纬度 + 世界陆地掩膜（供 3D 地球仪使用）。

* ``TEAM_COORDS`` —— 中文国名 → (纬度 lat, 经度 lon)。
* ``land_points()`` —— 烤好的低分辨率陆地点阵，用于在地球上绘制大陆轮廓。

陆地掩膜来源：Natural Earth ``ne_110m_land``（公有领域），离线栅格化为
90×180（每格 2°）的位图，base64 打包存放于同目录 ``land_mask.b64``。
"""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

# ─── 国家队坐标（首都 / 国土质心的近似值）──────────────────────
# key 使用懂球帝接口返回的中文队名（已去除首尾空格后匹配）。
TEAM_COORDS: dict[str, tuple[float, float]] = {
    "墨西哥": (23.6, -102.5),
    "韩国": (36.5, 127.8),
    "捷克": (49.8, 15.5),
    "南非": (-29.0, 24.0),
    "瑞士": (46.8, 8.2),
    "加拿大": (56.1, -106.3),
    "卡塔尔": (25.3, 51.2),
    "波黑": (43.9, 17.7),
    "苏格兰": (56.5, -4.2),
    "摩洛哥": (31.8, -7.1),
    "巴西": (-10.0, -52.0),
    "海地": (19.0, -72.3),
    "美国": (39.5, -98.4),
    "澳大利亚": (-25.3, 133.8),
    "土耳其": (39.0, 35.2),
    "巴拉圭": (-23.4, -58.4),
    "德国": (51.2, 10.4),
    "科特迪瓦": (7.5, -5.5),
    "厄瓜多尔": (-1.5, -78.4),
    "库拉索": (12.2, -69.0),
    "瑞典": (62.0, 15.0),
    "日本": (36.2, 138.3),
    "荷兰": (52.1, 5.3),
    "突尼斯": (34.0, 9.5),
    "比利时": (50.6, 4.5),
    "伊朗": (32.4, 53.7),
    "埃及": (26.8, 30.8),
    "新西兰": (-41.0, 174.0),
    "西班牙": (40.2, -3.7),
    "乌拉圭": (-32.5, -55.8),
    "沙特阿拉伯": (23.9, 45.1),
    "佛得角": (16.0, -24.0),
    "法国": (46.6, 2.4),
    "塞内加尔": (14.5, -14.5),
    "挪威": (64.0, 11.0),
    "伊拉克": (33.2, 43.7),
    "阿根廷": (-38.4, -63.6),
    "奥地利": (47.6, 14.1),
    "阿尔及利亚": (28.0, 1.7),
    "约旦": (31.2, 36.5),
    "葡萄牙": (39.5, -8.0),
    "哥伦比亚": (4.6, -74.3),
    "乌兹别克斯坦": (41.4, 64.6),
    "刚果民主共和国": (-2.9, 23.7),
    "英格兰": (52.5, -1.5),
    "克罗地亚": (45.1, 15.5),
    "巴拿马": (8.5, -80.0),
    "加纳": (7.9, -1.0),
    # ── 常见别名 / 后备坐标 ──────────────────────────
    "美利坚": (39.5, -98.4),
    "英国": (54.0, -2.5),
    "威尔士": (52.3, -3.7),
    "北爱尔兰": (54.7, -6.5),
    "意大利": (42.8, 12.6),
    "中国": (35.0, 104.0),
    "尼日利亚": (9.1, 8.7),
    "喀麦隆": (5.7, 12.4),
    "丹麦": (56.0, 9.5),
    "波兰": (52.1, 19.4),
    "塞尔维亚": (44.0, 21.0),
    "俄罗斯": (61.5, 90.0),
    "智利": (-35.7, -71.5),
    "秘鲁": (-9.2, -75.0),
    "委内瑞拉": (6.4, -66.6),
    "刚果": (-0.7, 15.8),
}


def team_coord(name: str | None) -> tuple[float, float] | None:
    """按中文队名查经纬度；找不到返回 None。"""
    if not name:
        return None
    return TEAM_COORDS.get(name.strip())


# ─── 陆地掩膜 ───────────────────────────────────────────────
_MASK_STEP = 2.0
_MASK_ROWS = 90
_MASK_COLS = 180
_DATA_FILE = Path(__file__).resolve().parent / "land_mask.b64"


@lru_cache(maxsize=1)
def _mask_bytes() -> bytes:
    try:
        return base64.b64decode(_DATA_FILE.read_text().strip())
    except Exception:
        return b""


def _bit(idx: int) -> bool:
    data = _mask_bytes()
    byte_i = idx >> 3
    if byte_i >= len(data):
        return False
    return bool(data[byte_i] & (1 << (7 - (idx & 7))))


def is_land(lat: float, lon: float) -> bool:
    """该经纬度是否落在陆地上。"""
    col = int((lon + 180.0) / _MASK_STEP)
    row = int((90.0 - lat) / _MASK_STEP)
    col = max(0, min(_MASK_COLS - 1, col))
    row = max(0, min(_MASK_ROWS - 1, row))
    return _bit(row * _MASK_COLS + col)


@lru_cache(maxsize=1)
def land_points() -> list[tuple[float, float]]:
    """返回所有陆地格子中心点 (lat, lon)，用于绘制大陆点阵。"""
    pts: list[tuple[float, float]] = []
    for row in range(_MASK_ROWS):
        lat = 90.0 - _MASK_STEP * (row + 0.5)
        base = row * _MASK_COLS
        for col in range(_MASK_COLS):
            if _bit(base + col):
                lon = -180.0 + _MASK_STEP * (col + 0.5)
                pts.append((lat, lon))
    return pts
