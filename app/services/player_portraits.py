"""球员高清肖像 / 海报图映射。

懂球帝接口里的 ``person_logo`` 多为 200×200 的圆头像，放到球员详情页
当 hero 大图分辨率不够。本模块为 **本届世界杯热门球员** 维护一份
中文姓名 → Wikimedia Commons / 高清照片 URL 的映射表，把球员详情页
的 hero 区做出 3A 游戏般的电影级质感。

未命中映射的球员 fallback 到 ``person_logo``（仍可放大铺满 + 渐变，
不影响功能完整性）。
"""
from __future__ import annotations

from app.models.player import PlayerRanking


def _wm(name: str, width: int = 1200) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        f"{name}?width={width}"
    )


# 中文姓名 → 大图 URL（最常见的 2026 WC 入选球员）
PLAYER_PORTRAITS: dict[str, str] = {
    # 德国
    "哈弗茨": _wm("Kai-Havertz-August-2018.jpg"),
    "穆西亚拉": _wm("Jamal_Musiala_2021_%28cropped%29.jpg"),
    "维尔茨": _wm("Florian_Wirtz_2021.jpg"),
    "京多安": _wm("Ilkay_Gundogan_2018.jpg"),
    "诺伊尔": _wm("Manuel_Neuer_2018_%28cropped%29.jpg"),
    "基米希": _wm("Joshua_Kimmich_2018_%28cropped%29.jpg"),
    "菲尔克鲁格": _wm("Niclas_F%C3%BCllkrug_2023.jpg"),
    # 法国
    "姆巴佩": _wm("Kylian_Mbapp%C3%A9_2018.jpg"),
    "格列兹曼": _wm("Antoine_Griezmann_2018.jpg"),
    "登贝莱": _wm("Ousmane_Demb%C3%A9l%C3%A9_2018_%28cropped%29.jpg"),
    "图拉姆": _wm("Marcus_Thuram_2024_%28cropped%29.jpg"),
    "琼阿梅尼": _wm("Aur%C3%A9lien_Tchouameni_2022.jpg"),
    "卡马文加": _wm("Eduardo_Camavinga_2022_%28cropped%29.jpg"),
    "登德斯": _wm("Theo_Hernandez_2022.jpg"),
    # 阿根廷
    "梅西": _wm("Lionel_Messi_WC2022.jpg"),
    "迪马利亚": _wm("Angel_Di_Maria_2018.jpg"),
    "劳塔罗·马丁内斯": _wm("Lautaro_Mart%C3%ADnez_2022.jpg"),
    "马丁内斯": _wm("Lautaro_Mart%C3%ADnez_2022.jpg"),
    "恩佐·费尔南德斯": _wm("Enzo_Fern%C3%A1ndez_2022.jpg"),
    "阿尔瓦雷斯": _wm("Juli%C3%A1n_%C3%81lvarez_2024.jpg"),
    # 巴西
    "内马尔": _wm("Neymar_2018.jpg"),
    "维尼修斯": _wm("V%C3%ADnicius_J%C3%BAnior_2024.jpg"),
    "罗德里戈": _wm("Rodrygo_2022.jpg"),
    "卡塞米罗": _wm("Casemiro_2022.jpg"),
    "马尔基尼奥斯": _wm("Marquinhos_2018.jpg"),
    # 葡萄牙
    "C罗": _wm("Cristiano_Ronaldo_2018.jpg"),
    "C 罗": _wm("Cristiano_Ronaldo_2018.jpg"),
    "克里斯蒂亚诺·罗纳尔多": _wm("Cristiano_Ronaldo_2018.jpg"),
    "B费": _wm("Bruno_Fernandes_2022.jpg"),
    "B 费": _wm("Bruno_Fernandes_2022.jpg"),
    "莱奥": _wm("Rafael_Le%C3%A3o_2022.jpg"),
    "费利克斯": _wm("Joao_Felix_2021.jpg"),
    # 西班牙
    "亚马尔": _wm("Lamine_Yamal_2024_%28cropped%29.jpg"),
    "佩德里": _wm("Pedri_2021.jpg"),
    "罗德里": _wm("Rodri_2022.jpg"),
    "莫拉塔": _wm("Alvaro_Morata_2018.jpg"),
    "丹尼·奥尔莫": _wm("Dani_Olmo_2021.jpg"),
    # 英格兰
    "贝林厄姆": _wm("Jude_Bellingham_2024_%28cropped%29.jpg"),
    "凯恩": _wm("Harry_Kane_2018.jpg"),
    "福登": _wm("Phil_Foden_2022.jpg"),
    "萨卡": _wm("Bukayo_Saka_2024_%28cropped%29.jpg"),
    "赖斯": _wm("Declan_Rice_2022.jpg"),
    # 比利时
    "德布劳内": _wm("Kevin_De_Bruyne_2022.jpg"),
    "卢卡库": _wm("Romelu_Lukaku_2018.jpg"),
    # 荷兰
    "范戴克": _wm("Virgil_van_Dijk_2022.jpg"),
    "德容": _wm("Frenkie_de_Jong_2022.jpg"),
    "德佩": _wm("Memphis_Depay_2022.jpg"),
    # 克罗地亚
    "莫德里奇": _wm("Luka_Modri%C4%87_2022.jpg"),
    # 摩洛哥
    "齐耶赫": _wm("Hakim_Ziyech_2018.jpg"),
    "哈基米": _wm("Achraf_Hakimi_2018.jpg"),
    # 美国 / 加拿大 / 墨西哥（东道主）
    "普利西奇": _wm("Christian_Pulisic_2018.jpg"),
    "戴维斯": _wm("Alphonso_Davies_2022.jpg"),
}


def portrait_url(player: PlayerRanking) -> str | None:
    """优先返回名人映射，否则返回懂球帝的圆头像。"""
    if not player:
        return None
    name = (player.person_name or "").strip()
    if not name:
        return player.person_logo
    if name in PLAYER_PORTRAITS:
        return PLAYER_PORTRAITS[name]
    # 别名清理
    for k, v in PLAYER_PORTRAITS.items():
        if k in name or name in k:
            return v
    return player.person_logo


# ── 本地高清图（存仓库 app/assets/players/） ──────────────
from pathlib import Path  # noqa: E402

from app.config import ASSETS_DIR  # noqa: E402

PLAYERS_IMG_DIR = ASSETS_DIR / "players"
_LOCAL_EXTS = (".png", ".webp", ".jpg", ".jpeg")


def local_portrait(person_id: str | None, name_zh: str | None = None) -> str | None:
    """在 app/assets/players/ 下按 person_id 或中文名查找本地高清图。"""
    if not PLAYERS_IMG_DIR.exists():
        return None
    candidates: list[str] = []
    if person_id:
        candidates.append(str(person_id))
    if name_zh:
        candidates.append(name_zh.strip())
    for stem in candidates:
        for ext in _LOCAL_EXTS:
            f = PLAYERS_IMG_DIR / f"{stem}{ext}"
            if f.exists():
                return str(f)
    return None


def best_portrait(
    person_id: str | None,
    name_zh: str | None,
    fallback_logo: str | None,
) -> str | None:
    """统一取图优先级：本地高清图 > 名人 Wikimedia 大图 > 懂球帝头像。"""
    local = local_portrait(person_id, name_zh)
    if local:
        return local
    name = (name_zh or "").strip()
    if name and name in PLAYER_PORTRAITS:
        return PLAYER_PORTRAITS[name]
    if name:
        for k, v in PLAYER_PORTRAITS.items():
            if k in name or name in k:
                return v
    return fallback_logo
