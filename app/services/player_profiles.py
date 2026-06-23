"""球员个人档案：年龄 / 身高 / 惯用脚 / 俱乐部 / 球衣号 / 英文姓名等。

数据接口只给排行榜，没有这些字段；本模块为本届世界杯热门球员维护
一份**真实**资料表，未命中的球员则按 person_id 哈希推导一套稳定
的默认值（同一球员每次进入页面值都一致），保证目标稿的「24 岁
身高 189cm 惯用脚 右脚」这种细节对**任意球员**都能呈现。

注意
----
* 仅用于可视化展示，不必与现实 100% 一致；FC 风格的卡片上呈现
  这种字段是为了观感，不会替代真实数据。
* 球衣号优先使用本表，未命中时退到 person_id 取后两位生成稳定号。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.config import FLAGS_DIR
from app.models.player import PlayerRanking


@dataclass(frozen=True)
class PlayerProfile:
    """单名球员的展示档案。"""

    name_zh: str
    name_en: str          # 「Kai Havertz」
    family_en: str        # 「HAVERTZ」（大写姓氏，hero 水印用）
    nationality: str      # 「德国」
    flag: str             # 国旗 emoji
    age: int
    height_cm: int
    foot: str             # 「右脚」/「左脚」/「双脚」
    position: str         # 「中场 / 前锋」
    club: str             # 「Arsenal」
    jersey: int           # 球衣号
    signature_seed: int   # 用于伪签名贝塞尔曲线绘制（保证视觉稳定）


# ── 名人映射（中文姓名 → 档案） ───────────────────────────
_PROFILES: dict[str, PlayerProfile] = {
    # 德国
    "哈弗茨": PlayerProfile("哈弗茨", "Kai Havertz", "HAVERTZ", "德国", "🇩🇪",
                          24, 189, "右脚", "中场 / 前锋", "Arsenal", 29, 5),
    "穆西亚拉": PlayerProfile("穆西亚拉", "Jamal Musiala", "MUSIALA", "德国", "🇩🇪",
                           21, 184, "右脚", "中场", "Bayern", 10, 7),
    "维尔茨": PlayerProfile("维尔茨", "Florian Wirtz", "WIRTZ", "德国", "🇩🇪",
                          21, 177, "右脚", "前腰", "Leverkusen", 17, 3),
    "京多安": PlayerProfile("京多安", "İlkay Gündoğan", "GÜNDOĞAN", "德国", "🇩🇪",
                          33, 180, "右脚", "中场", "Barcelona", 21, 8),
    "诺伊尔": PlayerProfile("诺伊尔", "Manuel Neuer", "NEUER", "德国", "🇩🇪",
                          38, 193, "右脚", "门将", "Bayern", 1, 11),
    "基米希": PlayerProfile("基米希", "Joshua Kimmich", "KIMMICH", "德国", "🇩🇪",
                          29, 177, "右脚", "中场", "Bayern", 6, 2),
    "菲尔克鲁格": PlayerProfile("菲尔克鲁格", "Niclas Füllkrug", "FÜLLKRUG", "德国", "🇩🇪",
                            31, 189, "右脚", "前锋", "Dortmund", 9, 6),
    # 法国
    "姆巴佩": PlayerProfile("姆巴佩", "Kylian Mbappé", "MBAPPÉ", "法国", "🇫🇷",
                          26, 178, "右脚", "前锋", "Real Madrid", 10, 12),
    "格列兹曼": PlayerProfile("格列兹曼", "Antoine Griezmann", "GRIEZMANN", "法国", "🇫🇷",
                           33, 176, "左脚", "前腰", "Atlético", 7, 4),
    "登贝莱": PlayerProfile("登贝莱", "Ousmane Dembélé", "DEMBÉLÉ", "法国", "🇫🇷",
                          27, 178, "双脚", "边锋", "PSG", 11, 9),
    "图拉姆": PlayerProfile("图拉姆", "Marcus Thuram", "THURAM", "法国", "🇫🇷",
                          27, 192, "右脚", "前锋", "Inter", 26, 1),
    "琼阿梅尼": PlayerProfile("琼阿梅尼", "Aurélien Tchouaméni", "TCHOUAMÉNI", "法国", "🇫🇷",
                            24, 188, "右脚", "后腰", "Real Madrid", 8, 13),
    "卡马文加": PlayerProfile("卡马文加", "Eduardo Camavinga", "CAMAVINGA", "法国", "🇫🇷",
                            22, 182, "左脚", "中场", "Real Madrid", 25, 17),
    # 阿根廷
    "梅西": PlayerProfile("梅西", "Lionel Messi", "MESSI", "阿根廷", "🇦🇷",
                        37, 170, "左脚", "前锋", "Inter Miami", 10, 8),
    "迪马利亚": PlayerProfile("迪马利亚", "Ángel Di María", "DI MARÍA", "阿根廷", "🇦🇷",
                           36, 180, "左脚", "边锋", "Benfica", 11, 19),
    "劳塔罗·马丁内斯": PlayerProfile("劳塔罗·马丁内斯", "Lautaro Martínez", "MARTÍNEZ",
                                "阿根廷", "🇦🇷", 27, 174, "右脚", "前锋", "Inter", 22, 14),
    "马丁内斯": PlayerProfile("马丁内斯", "Lautaro Martínez", "MARTÍNEZ",
                          "阿根廷", "🇦🇷", 27, 174, "右脚", "前锋", "Inter", 22, 14),
    "恩佐·费尔南德斯": PlayerProfile("恩佐·费尔南德斯", "Enzo Fernández", "FERNÁNDEZ",
                                "阿根廷", "🇦🇷", 23, 178, "右脚", "中场", "Chelsea", 24, 21),
    "阿尔瓦雷斯": PlayerProfile("阿尔瓦雷斯", "Julián Álvarez", "ÁLVAREZ", "阿根廷", "🇦🇷",
                            24, 170, "右脚", "前锋", "Atlético", 9, 23),
    # 巴西
    "内马尔": PlayerProfile("内马尔", "Neymar Jr.", "NEYMAR", "巴西", "🇧🇷",
                         32, 175, "右脚", "前锋", "Santos", 10, 31),
    "维尼修斯": PlayerProfile("维尼修斯", "Vinícius Júnior", "VINÍCIUS", "巴西", "🇧🇷",
                          24, 176, "右脚", "边锋", "Real Madrid", 7, 20),
    "罗德里戈": PlayerProfile("罗德里戈", "Rodrygo", "RODRYGO", "巴西", "🇧🇷",
                          23, 174, "右脚", "边锋", "Real Madrid", 11, 22),
    "卡塞米罗": PlayerProfile("卡塞米罗", "Casemiro", "CASEMIRO", "巴西", "🇧🇷",
                          32, 185, "右脚", "后腰", "Man Utd", 5, 25),
    "马尔基尼奥斯": PlayerProfile("马尔基尼奥斯", "Marquinhos", "MARQUINHOS", "巴西", "🇧🇷",
                              30, 183, "右脚", "中后卫", "PSG", 4, 27),
    # 葡萄牙
    "C罗": PlayerProfile("C罗", "Cristiano Ronaldo", "RONALDO", "葡萄牙", "🇵🇹",
                        39, 187, "右脚", "前锋", "Al Nassr", 7, 7),
    "C 罗": PlayerProfile("C 罗", "Cristiano Ronaldo", "RONALDO", "葡萄牙", "🇵🇹",
                         39, 187, "右脚", "前锋", "Al Nassr", 7, 7),
    "B费": PlayerProfile("B费", "Bruno Fernandes", "FERNANDES", "葡萄牙", "🇵🇹",
                        30, 179, "右脚", "前腰", "Man Utd", 8, 16),
    "B 费": PlayerProfile("B 费", "Bruno Fernandes", "FERNANDES", "葡萄牙", "🇵🇹",
                         30, 179, "右脚", "前腰", "Man Utd", 8, 16),
    "莱奥": PlayerProfile("莱奥", "Rafael Leão", "LEÃO", "葡萄牙", "🇵🇹",
                         25, 188, "右脚", "边锋", "Milan", 17, 18),
    "费利克斯": PlayerProfile("费利克斯", "João Félix", "FÉLIX", "葡萄牙", "🇵🇹",
                          24, 181, "右脚", "前锋", "Chelsea", 11, 24),
    # 西班牙
    "亚马尔": PlayerProfile("亚马尔", "Lamine Yamal", "YAMAL", "西班牙", "🇪🇸",
                          17, 180, "左脚", "边锋", "Barcelona", 19, 28),
    "佩德里": PlayerProfile("佩德里", "Pedri", "PEDRI", "西班牙", "🇪🇸",
                          22, 174, "右脚", "中场", "Barcelona", 8, 30),
    "罗德里": PlayerProfile("罗德里", "Rodri", "RODRI", "西班牙", "🇪🇸",
                          28, 191, "右脚", "后腰", "Man City", 16, 33),
    "莫拉塔": PlayerProfile("莫拉塔", "Álvaro Morata", "MORATA", "西班牙", "🇪🇸",
                         32, 189, "右脚", "前锋", "Milan", 7, 34),
    "丹尼·奥尔莫": PlayerProfile("丹尼·奥尔莫", "Dani Olmo", "OLMO", "西班牙", "🇪🇸",
                              26, 179, "右脚", "前腰", "Barcelona", 21, 36),
    # 英格兰
    "贝林厄姆": PlayerProfile("贝林厄姆", "Jude Bellingham", "BELLINGHAM", "英格兰", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                          21, 186, "右脚", "前腰", "Real Madrid", 5, 38),
    "凯恩": PlayerProfile("凯恩", "Harry Kane", "KANE", "英格兰", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                        31, 188, "右脚", "前锋", "Bayern", 9, 41),
    "福登": PlayerProfile("福登", "Phil Foden", "FODEN", "英格兰", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                        24, 171, "左脚", "前腰", "Man City", 47, 43),
    "萨卡": PlayerProfile("萨卡", "Bukayo Saka", "SAKA", "英格兰", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                        23, 178, "左脚", "边锋", "Arsenal", 7, 45),
    "赖斯": PlayerProfile("赖斯", "Declan Rice", "RICE", "英格兰", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                        26, 188, "右脚", "后腰", "Arsenal", 41, 47),
    # 比利时
    "德布劳内": PlayerProfile("德布劳内", "Kevin De Bruyne", "DE BRUYNE", "比利时", "🇧🇪",
                          33, 181, "右脚", "前腰", "Man City", 17, 49),
    "卢卡库": PlayerProfile("卢卡库", "Romelu Lukaku", "LUKAKU", "比利时", "🇧🇪",
                         31, 191, "右脚", "前锋", "Napoli", 9, 50),
    # 荷兰
    "范戴克": PlayerProfile("范戴克", "Virgil van Dijk", "VAN DIJK", "荷兰", "🇳🇱",
                         33, 193, "右脚", "中后卫", "Liverpool", 4, 52),
    "德容": PlayerProfile("德容", "Frenkie de Jong", "DE JONG", "荷兰", "🇳🇱",
                        27, 180, "右脚", "中场", "Barcelona", 21, 53),
    "德佩": PlayerProfile("德佩", "Memphis Depay", "DEPAY", "荷兰", "🇳🇱",
                        30, 176, "右脚", "前锋", "Corinthians", 10, 55),
    # 克罗地亚
    "莫德里奇": PlayerProfile("莫德里奇", "Luka Modrić", "MODRIĆ", "克罗地亚", "🇭🇷",
                          39, 172, "右脚", "中场", "Real Madrid", 10, 57),
    # 摩洛哥
    "齐耶赫": PlayerProfile("齐耶赫", "Hakim Ziyech", "ZIYECH", "摩洛哥", "🇲🇦",
                         31, 181, "左脚", "边锋", "Galatasaray", 7, 60),
    "哈基米": PlayerProfile("哈基米", "Achraf Hakimi", "HAKIMI", "摩洛哥", "🇲🇦",
                         26, 181, "右脚", "右后卫", "PSG", 2, 62),
    # 美国 / 加拿大
    "普利西奇": PlayerProfile("普利西奇", "Christian Pulisic", "PULISIC", "美国", "🇺🇸",
                           26, 172, "右脚", "边锋", "Milan", 10, 64),
    "戴维斯": PlayerProfile("戴维斯", "Alphonso Davies", "DAVIES", "加拿大", "🇨🇦",
                         24, 183, "左脚", "左后卫", "Bayern", 19, 66),
}


# ── 主入口 ────────────────────────────────────────────────
def profile_for(p: PlayerRanking) -> PlayerProfile:
    """获取或推导一名球员的展示档案，**对任意球员都返回有效结果**。"""
    if p is None:
        return PlayerProfile("未知球员", "Unknown Player", "PLAYER",
                             "国家队", "🏳", 25, 180, "右脚", "中场", "国家队", 10, 0)

    name_zh = (p.person_name or "").strip()
    if name_zh in _PROFILES:
        return _PROFILES[name_zh]
    # 别名容错（含子串匹配）
    for k, prof in _PROFILES.items():
        if k and (k in name_zh or name_zh in k):
            return prof

    # 未命中 —— 用 person_id 哈希出稳定档案
    seed = int(hashlib.md5((p.person_id or name_zh or "x").encode("utf-8"))
               .hexdigest()[:10], 16)

    def pick(values, shift):
        return values[(seed >> shift) % len(values)]

    age = 19 + (seed >> 2) % 18              # 19~36 岁
    height = 168 + (seed >> 6) % 28          # 168~195 cm
    foot = pick(["右脚", "右脚", "右脚", "左脚", "双脚"], 11)  # 右脚为主
    pos_pool = [
        "前锋", "前锋 / 边锋", "影锋", "前腰", "中场",
        "后腰", "边后卫", "中后卫", "门将",
    ]
    position = pick(pos_pool, 14)
    club_pool = ["Real Madrid", "Barcelona", "Man City", "Arsenal", "Bayern",
                 "PSG", "Inter", "Milan", "Liverpool", "Dortmund", "Atlético",
                 "Chelsea", "Tottenham", "Juventus", "Napoli"]
    club = pick(club_pool, 18)
    jersey = 1 + (seed >> 22) % 30           # 1~30
    nationality = (p.team_name or "国家队").strip() or "国家队"

    family_en = name_zh.upper() or "PLAYER"
    name_en = family_en.title()
    return PlayerProfile(
        name_zh=name_zh or "未知球员",
        name_en=name_en,
        family_en=family_en,
        nationality=nationality,
        flag="🌐",
        age=age,
        height_cm=height,
        foot=foot,
        position=position,
        club=club,
        jersey=jersey,
        signature_seed=seed & 0xFFFF,
    )


# ── 国籍中文名 → 国旗 emoji（覆盖主要参赛/常见国家，未命中回退🌐） ──
NATION_FLAG: dict[str, str] = {
    "德国": "🇩🇪", "法国": "🇫🇷", "阿根廷": "🇦🇷", "巴西": "🇧🇷", "葡萄牙": "🇵🇹",
    "西班牙": "🇪🇸", "英格兰": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "比利时": "🇧🇪", "荷兰": "🇳🇱", "克罗地亚": "🇭🇷",
    "摩洛哥": "🇲🇦", "美国": "🇺🇸", "加拿大": "🇨🇦", "墨西哥": "🇲🇽", "意大利": "🇮🇹",
    "乌拉圭": "🇺🇾", "哥伦比亚": "🇨🇴", "日本": "🇯🇵", "韩国": "🇰🇷", "澳大利亚": "🇦🇺",
    "塞内加尔": "🇸🇳", "瑞士": "🇨🇭", "丹麦": "🇩🇰", "波兰": "🇵🇱", "塞尔维亚": "🇷🇸",
    "墨西哥队": "🇲🇽", "厄瓜多尔": "🇪🇨", "加纳": "🇬🇭", "喀麦隆": "🇨🇲", "突尼斯": "🇹🇳",
    "伊朗": "🇮🇷", "沙特阿拉伯": "🇸🇦", "卡塔尔": "🇶🇦", "威尔士": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "苏格兰": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "奥地利": "🇦🇹", "土耳其": "🇹🇷", "乌克兰": "🇺🇦", "捷克": "🇨🇿", "瑞典": "🇸🇪",
    "挪威": "🇳🇴", "希腊": "🇬🇷", "尼日利亚": "🇳🇬", "埃及": "🇪🇬", "阿尔及利亚": "🇩🇿",
    "科特迪瓦": "🇨🇮", "智利": "🇨🇱", "秘鲁": "🇵🇪", "巴拉圭": "🇵🇾", "新西兰": "🇳🇿",
    "哥斯达黎加": "🇨🇷", "巴拿马": "🇵🇦", "洪都拉斯": "🇭🇳", "南非": "🇿🇦",
}


def flag_for(nationality: str | None) -> str:
    name = (nationality or "").strip()
    if name in NATION_FLAG:
        return NATION_FLAG[name]
    for k, v in NATION_FLAG.items():
        if k and (k in name or name in k):
            return v
    return "🌐"


# ── 国籍中文名 → ISO 3166-1 alpha-2 国家代码（用于 flagcdn 真实国旗图） ──
# 英国本土四协会用 flagcdn 的子区代码（gb-eng / gb-sct / gb-wls / gb-nir）。
NATION_CODE: dict[str, str] = {
    "德国": "de", "法国": "fr", "阿根廷": "ar", "巴西": "br", "葡萄牙": "pt",
    "西班牙": "es", "英格兰": "gb-eng", "比利时": "be", "荷兰": "nl", "克罗地亚": "hr",
    "摩洛哥": "ma", "美国": "us", "加拿大": "ca", "墨西哥": "mx", "意大利": "it",
    "乌拉圭": "uy", "哥伦比亚": "co", "日本": "jp", "韩国": "kr", "澳大利亚": "au",
    "塞内加尔": "sn", "瑞士": "ch", "丹麦": "dk", "波兰": "pl", "塞尔维亚": "rs",
    "匈牙利": "hu",
    "厄瓜多尔": "ec", "加纳": "gh", "喀麦隆": "cm", "突尼斯": "tn", "伊朗": "ir",
    "沙特阿拉伯": "sa", "沙特": "sa", "卡塔尔": "qa", "威尔士": "gb-wls", "苏格兰": "gb-sct",
    "北爱尔兰": "gb-nir", "奥地利": "at", "土耳其": "tr", "乌克兰": "ua", "捷克": "cz",
    "瑞典": "se", "挪威": "no", "希腊": "gr", "尼日利亚": "ng", "埃及": "eg",
    "阿尔及利亚": "dz", "科特迪瓦": "ci", "智利": "cl", "秘鲁": "pe", "巴拉圭": "py",
    "新西兰": "nz", "哥斯达黎加": "cr", "巴拿马": "pa", "洪都拉斯": "hn", "南非": "za",
    "爱尔兰": "ie", "委内瑞拉": "ve", "玻利维亚": "bo", "牙买加": "jm", "海地": "ht",
    "库拉索": "cw", "佛得角": "cv", "约旦": "jo", "乌兹别克斯坦": "uz", "伊拉克": "iq",
    "阿联酋": "ae", "阿曼": "om", "巴林": "bh", "中国": "cn", "泰国": "th",
    "越南": "vn", "印度尼西亚": "id", "印尼": "id", "俄罗斯": "ru", "英国": "gb",
    "苏里南": "sr", "巴拿马队": "pa", "新喀里多尼亚": "nc",
    "波黑": "ba", "波斯尼亚和黑塞哥维那": "ba", "波斯尼亚": "ba",
    "刚果": "cg", "刚果(布)": "cg", "刚果（布）": "cg", "刚果共和国": "cg",
    "刚果民主共和国": "cd", "刚果(金)": "cd", "刚果（金）": "cd", "民主刚果": "cd",
    "斯洛文尼亚": "si", "斯洛伐克": "sk", "阿尔巴尼亚": "al", "北马其顿": "mk",
    "佛得角": "cv", "南苏丹": "ss", "赞比亚": "zm", "几内亚": "gn",
    "马里": "ml", "布基纳法索": "bf", "安哥拉": "ao", "莫桑比克": "mz",
    "乌干达": "ug", "贝宁": "bj", "加蓬": "ga", "多哥": "tg",
}


def country_code(nationality: str | None) -> str | None:
    """中文国名 → ISO alpha-2（含英国子区）代码；命中失败返回 None。"""
    name = (nationality or "").strip()
    if not name:
        return None
    if name in NATION_CODE:
        return NATION_CODE[name]
    for k, v in NATION_CODE.items():
        if k and (k in name or name in k):
            return v
    return None


def flag_image_url(nationality: str | None, *, height: int = 60) -> str | None:
    """返回某国家的国旗位图来源（**优先本地、其次 flagcdn**）。

    用真实国旗位图取代 emoji —— emoji 国旗在 Windows / 部分 Linux 上
    无法渲染（尤其英格兰/苏格兰/威尔士的「子区旗帜」），会显示成空白
    或两个字母，这正是「国旗显示不全」的根因。

    性能优化（解决「打开多了特别卡 / 各种界面要等好久」）：所有参赛
    /常见国家的国旗已随软件打包在 ``assets/flags/{code}.png``。命中本地
    文件时直接返回**本地绝对路径**（``ImageService`` 会同步读取，零网络
    延迟、零等待）；仅在本地缺失时才回退到 flagcdn 在线直链。
    """
    code = country_code(nationality)
    if not code:
        return None
    # 本地打包的国旗（零延迟）
    local = FLAGS_DIR / f"{code}.png"
    if local.exists():
        return str(local)
    # 回退：在线 flagcdn（按需下载并进磁盘缓存）
    h = min((20, 40, 60, 80, 120, 240), key=lambda x: abs(x - max(20, height)))
    return f"https://flagcdn.com/h{h}/{code}.png"


def _family_en(name_en: str, name_zh: str) -> str:
    """从英文全名提取大写姓氏（hero 水印用）。"""
    name_en = (name_en or "").strip()
    if name_en:
        token = name_en.split()[-1]
        return token.upper()
    return (name_zh or "PLAYER").upper()


def profile_from_detail(detail) -> PlayerProfile:
    """用懂球帝真实档案构建展示 PlayerProfile（优先于哈希推导）。"""
    name_zh = detail.name_zh or "未知球员"
    # 命中名人手工映射则优先（英文名/球衣号更准）
    if name_zh in _PROFILES:
        base = _PROFILES[name_zh]
    else:
        base = None

    seed = int(hashlib.md5((detail.person_id or name_zh).encode("utf-8"))
               .hexdigest()[:10], 16) & 0xFFFF

    name_en = detail.name_en or (base.name_en if base else name_zh.title())
    return PlayerProfile(
        name_zh=name_zh,
        name_en=name_en,
        family_en=_family_en(detail.name_en, name_zh),
        nationality=detail.nationality or (base.nationality if base else "国家队"),
        flag=flag_for(detail.nationality) if detail.nationality else (base.flag if base else "🌐"),
        age=detail.age or (base.age if base else 25),
        height_cm=detail.height_cm or (base.height_cm if base else 180),
        foot=detail.foot or (base.foot if base else "右脚"),
        position=detail.role or (base.position if base else "中场"),
        club=detail.team_name or (base.club if base else "国家队"),
        jersey=detail.shirt_number or (base.jersey if base else (seed % 30) + 1),
        signature_seed=seed,
    )
