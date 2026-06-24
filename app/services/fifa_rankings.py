"""国际足联（FIFA/Coca-Cola）世界排名 —— 实时拉取并按国别索引。

数据源
------
官方接口：``https://api.fifa.com/api/v3/fifarankings/rankings/live``
（``gender=1`` 男足、``sportType=0`` 足球、``language=en``）。返回 211 支国家队，
每项含 ``Rank``（排名）、``IdCountry``（FIFA 三字代码，如 ARG/FRA/ENG）、
``TeamName``（英文队名）。

用途
----
把「世界排名」标注到主页 / 赛程页的对阵国旗旁（如「#1」「#12」）。本模块负责：

1. 异步拉取并缓存排名（懂球帝接口同款 :class:`ApiClient`，带 stale-while-revalidate）。
2. 把 FIFA 三字代码映射成应用内使用的 ISO alpha-2 代码（与
   :func:`app.services.player_profiles.country_code` 输出一致，含英国子区
   ``gb-eng`` / ``gb-sct`` / ``gb-wls`` / ``gb-nir``）。
3. 提供按**中文队名**查询排名的同步接口 :meth:`FifaRankings.rank` /
   :meth:`FifaRankings.rank_text`，供各对阵控件渲染时直接调用。

设计为单例：任意页面调用 :meth:`refresh` 都共享同一份缓存（``ApiClient`` 还会
对同一 URL 去重），拉取成功后填充内存表；失败则保留上一份（不清空）。
"""
from __future__ import annotations

import logging

from app.api.client import ApiClient
from app.services.player_profiles import country_code

log = logging.getLogger(__name__)

#: FIFA 实时排名接口。
FIFA_RANKINGS_URL = (
    "https://api.fifa.com/api/v3/fifarankings/rankings/live"
)
#: 排名变化不频繁（每月一次左右）—— 缓存 6 小时。
_CACHE_TTL = 60 * 60 * 6


# ── FIFA 三字代码 → ISO alpha-2（与 player_profiles.NATION_CODE 取值一致）──
# 覆盖本届世界杯参赛队 + 常见国家队；未列出的代码（应用内不会展示）直接忽略。
# 英国本土四协会用 flagcdn 子区代码（gb-eng / gb-sct / gb-wls / gb-nir）。
_FIFA3_TO_ALPHA2: dict[str, str] = {
    "ARG": "ar", "FRA": "fr", "ESP": "es", "ENG": "gb-eng", "BRA": "br",
    "MAR": "ma", "POR": "pt", "NED": "nl", "GER": "de", "BEL": "be",
    "COL": "co", "MEX": "mx", "CRO": "hr", "USA": "us", "ITA": "it",
    "JPN": "jp", "SUI": "ch", "URU": "uy", "SEN": "sn", "DEN": "dk",
    "IRN": "ir", "NOR": "no", "AUT": "at", "KOR": "kr", "NGA": "ng",
    "AUS": "au", "EGY": "eg", "ALG": "dz", "CAN": "ca", "ECU": "ec",
    "CIV": "ci", "TUR": "tr", "UKR": "ua", "RUS": "ru", "POL": "pl",
    "SWE": "se", "PAR": "py", "WAL": "gb-wls", "HUN": "hu", "SCO": "gb-sct",
    "SRB": "rs", "PAN": "pa", "CZE": "cz", "CMR": "cm", "SVK": "sk",
    "GRE": "gr", "COD": "cd", "VEN": "ve", "CHI": "cl", "PER": "pe",
    "CRC": "cr", "ROU": "ro", "MLI": "ml", "IRL": "ie", "SVN": "si",
    "QAT": "qa", "TUN": "tn", "UZB": "uz", "KSA": "sa", "IRQ": "iq",
    "RSA": "za", "BFA": "bf", "CPV": "cv", "GHA": "gh", "BIH": "ba",
    "HON": "hn", "ALB": "al", "UAE": "ae", "MKD": "mk", "NIR": "gb-nir",
    "JAM": "jm", "JOR": "jo", "NZL": "nz", "CUW": "cw", "GUI": "gn",
    "ANG": "ao", "ZAM": "zm", "CHN": "cn", "BHR": "bh", "BEN": "bj",
    "THA": "th", "VIE": "vn", "IDN": "id", "SUR": "sr", "TOG": "tg",
    "GAB": "ga", "UGA": "ug", "MOZ": "mz", "SSD": "ss", "CGO": "cg",
    "NCL": "nc", "HAI": "ht", "BOL": "bo", "OMA": "om",
}


class FifaRankings:
    """国际足联世界排名（单例）。"""

    _instance: "FifaRankings | None" = None

    def __init__(self) -> None:
        # 内存表：ISO alpha-2 代码 → 排名（如 "ar" → 1）。
        self._ranks: dict[str, int] = {}
        self._loaded = False

    @classmethod
    def instance(cls) -> "FifaRankings":
        if cls._instance is None:
            cls._instance = FifaRankings()
        return cls._instance

    @property
    def loaded(self) -> bool:
        """是否已成功载入过一次排名（用于判断是否需要等待 / 重试）。"""
        return self._loaded

    # ── 拉取 ─────────────────────────────────
    async def refresh(self, *, force: bool = False) -> bool:
        """异步拉取最新世界排名并填充内存表；成功返回 ``True``。

        失败（网络 / 解析异常）时保留上一份排名（不清空），返回 ``False``。
        """
        try:
            data = await ApiClient.instance().get_json(
                FIFA_RANKINGS_URL,
                params={"gender": 1, "sportType": 0, "language": "en"},
                cache_ttl=_CACHE_TTL,
                force=force,
            )
        except Exception as exc:  # pragma: no cover - 网络异常
            log.warning("FIFA 世界排名拉取失败：%s", exc)
            return False

        ranks = parse_rankings(data)
        if ranks:
            self._ranks = ranks
            self._loaded = True
            return True
        return False

    # ── 查询 ─────────────────────────────────
    def rank(self, nationality_zh: str | None) -> int | None:
        """按**中文队名**查世界排名；未命中返回 ``None``。"""
        code = country_code(nationality_zh)
        if not code:
            return None
        return self._ranks.get(code)

    def rank_text(self, nationality_zh: str | None) -> str:
        """返回形如 ``"#12"`` 的排名标注；未命中返回空串。"""
        r = self.rank(nationality_zh)
        return f"#{r}" if r else ""


def parse_rankings(data: dict) -> dict[str, int]:
    """纯函数：把 FIFA 接口响应解析成 ``{alpha-2 代码: 排名}``。

    只保留能映射到应用内 ISO alpha-2 代码的国家队（其余忽略）。响应结构异常
    时返回空字典（调用方据此保留上一份数据）。
    """
    out: dict[str, int] = {}
    if not isinstance(data, dict):
        return out
    results = data.get("Results")
    if not isinstance(results, list):
        return out
    for item in results:
        if not isinstance(item, dict):
            continue
        fifa_code = str(item.get("IdCountry") or "").strip().upper()
        alpha2 = _FIFA3_TO_ALPHA2.get(fifa_code)
        if not alpha2:
            continue
        try:
            rank = int(item.get("Rank"))
        except (TypeError, ValueError):
            continue
        if rank > 0:
            out[alpha2] = rank
    return out
