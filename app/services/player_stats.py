"""球员五维能力值生成器（PAC/SHO/PAS/DEF/PHY）。

数据接口只提供进球/助攻等排行数据，没有 FIFA 那种能力面板。
这里用「person_id 的稳定哈希 + 真实进球/助攻数据」推导出一套**确定性**的
能力值：同一名球员每次进入都得到完全一致的结果，且与其真实表现相关
（射手射门高、组织者传球高、名次靠前整体强）。仅用于可视化展示。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.models.player import PlayerRanking, RankingType

# 五维（缩写, 中文, 强调色）
DIMENSIONS: list[tuple[str, str, str]] = [
    ("PAC", "速度", "#00e5ff"),
    ("SHO", "射门", "#ff0055"),
    ("PAS", "传球", "#00ff66"),
    ("DEF", "防守", "#0077ff"),
    ("PHY", "力量", "#ffd700"),
]


@dataclass
class PlayerStats:
    pac: int
    sho: int
    pas: int
    dfd: int
    phy: int
    ovr: int            # 综合
    position: str       # 推测位置
    tag_code: str       # 特色徽章代码
    tag_label: str      # 徽章文案
    tag_icon: str       # 徽章图标

    def as_pairs(self) -> list[tuple[str, str, int, str]]:
        """返回 [(缩写, 中文, 数值, 颜色), ...]，供雷达图渲染。"""
        vals = {"PAC": self.pac, "SHO": self.sho, "PAS": self.pas,
                "DEF": self.dfd, "PHY": self.phy}
        return [(code, zh, vals[code], color) for code, zh, color in DIMENSIONS]


def _seed(key: str) -> int:
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)


def _clamp(v: float) -> int:
    return int(max(48, min(99, round(v))))


# 特色徽章：(code, label, icon)
_TAGS = {
    "PAC": ("speed", "极速突击", "⚡"),
    "SHO": ("finisher", "终结杀手", "🎯"),
    "PAS": ("maestro", "传球大师", "🎼"),
    "DEF": ("wall", "钢铁后防", "🛡"),
    "PHY": ("tank", "力量怪兽", "💪"),
}


def player_stats(p: PlayerRanking | None) -> PlayerStats:
    """根据排行榜数据推导球员五维能力。"""
    if p is None:
        return PlayerStats(70, 70, 70, 70, 70, 70, "中场", "balance", "全能战士", "✨")

    rnd_key = p.person_id or p.person_name or "anon"
    seed = _seed(rnd_key)

    # 用哈希拆出五个 0..1 的稳定基数
    def frac(shift: int) -> float:
        return ((seed >> (shift * 5)) & 0x1F) / 31.0

    base = 60.0
    span = 24.0
    pac = base + span * frac(0)
    sho = base + span * frac(1)
    pas = base + span * frac(2)
    dfd = base + span * frac(3)
    phy = base + span * frac(4)

    goals = p.goal if p.goal is not None else (p.count if p.ranking_type == RankingType.GOALS else 0)
    assists = p.count if p.ranking_type == RankingType.ASSISTS else 0

    # 真实数据加成
    if p.ranking_type == RankingType.GOALS:
        sho += min(20.0, (p.count or 0) * 2.6)
        pac += min(10.0, (p.count or 0) * 1.2)
    else:
        pas += min(20.0, (p.count or 0) * 3.0)
        pac += min(8.0, (p.count or 0) * 1.0)

    # 名次靠前 → 整体提升
    rank_boost = max(0.0, 12.0 - (p.rank or 30) * 0.5)
    for _ in range(1):
        pass
    pac += rank_boost * 0.4
    sho += rank_boost * 0.5
    pas += rank_boost * 0.4
    phy += rank_boost * 0.3

    pac, sho, pas, dfd, phy = map(_clamp, (pac, sho, pas, dfd, phy))
    ovr = _clamp(0.18 * pac + 0.30 * sho + 0.24 * pas + 0.10 * dfd + 0.18 * phy + 6)

    # 特色徽章 = 最强维度
    dims = {"PAC": pac, "SHO": sho, "PAS": pas, "DEF": dfd, "PHY": phy}
    top = max(dims, key=dims.get)
    tag_code, tag_label, tag_icon = _TAGS[top]

    # 简单位置推测
    if p.ranking_type == RankingType.GOALS and goals >= 2:
        position = "前锋"
    elif p.ranking_type == RankingType.ASSISTS:
        position = "中场"
    elif dfd >= max(pac, sho, pas):
        position = "后卫"
    else:
        position = "中场"

    return PlayerStats(pac, sho, pas, dfd, phy, ovr, position,
                       tag_code, tag_label, tag_icon)


# ─── 用懂球帝真实能力值构建五维（优先于哈希推导） ───────────
def stats_from_ability(ability, fallback: "PlayerRanking | None" = None) -> "PlayerStats":
    """把懂球帝 sofifa 能力值（六维 redar）映射为本应用的五维 PlayerStats。

    映射：速度→PAC / 射门→SHO / 传球→PAS / 防守→DEF / 力量→PHY。
    OVR 直接取 average。若 ability 为空则退回基于排行榜的哈希推导。
    """
    if ability is None or not getattr(ability, "radar", None):
        return player_stats(fallback)

    name_map = {d.name: d.val for d in ability.radar}

    def pick(*keys: str) -> int:
        for k in keys:
            if k in name_map:
                return _clamp(name_map[k])
        return 70

    pac = pick("速度", "加速")
    sho = pick("射门")
    pas = pick("传球", "短传")
    dfd = pick("防守", "盯人")
    phy = pick("力量", "强壮")
    ovr = _clamp(ability.ovr) if ability.ovr else _clamp(
        0.2 * pac + 0.28 * sho + 0.24 * pas + 0.1 * dfd + 0.18 * phy + 4
    )

    dims = {"PAC": pac, "SHO": sho, "PAS": pas, "DEF": dfd, "PHY": phy}
    top = max(dims, key=dims.get)
    tag_code, tag_label, tag_icon = _TAGS[top]

    position = ability.position or "中场"
    return PlayerStats(pac, sho, pas, dfd, phy, ovr, position,
                       tag_code, tag_label, tag_icon)
