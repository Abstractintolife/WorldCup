"""2026 FIFA 世界杯 16 个主办城市球场。

数据源
-------
* 文字资料 —— FIFA 官方公告 + 各球场公开维基资料整理。
* 实景图   —— Wikimedia Commons（自由许可），通过其
  ``Special:FilePath`` 接口直接拉取压缩缩略图。
"""
from __future__ import annotations

from app.models.stadium import Stadium


# Wikimedia Commons 图片直链工具
def _wm(name: str, width: int = 1200) -> str:
    """根据文件名返回 Wikimedia 缩略图直链。"""
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        f"{name}?width={width}"
    )


WC2026_STADIUMS: list[Stadium] = [
    # ── 美国 11 座 ─────────────────────────
    Stadium(
        name_zh="大都会人寿体育场",
        name_en="MetLife Stadium",
        city="纽约 / 新泽西",
        country="美国",
        capacity=82500,
        opened=2010,
        role="决赛举办场地（2026 年 7 月 19 日）",
        description="位于东卢瑟福，为 NFL 巨人队与喷气机队主场，是本届赛事承办决赛的旗舰球场。",
        flag_emoji="🇺🇸",
        image_url=_wm("Metlife_stadium_%28Aerial_view%29.jpg"),
        accent="#E5394E",
    ),
    Stadium(
        name_zh="索菲体育场",
        name_en="SoFi Stadium",
        city="洛杉矶 / 英格尔伍德",
        country="美国",
        capacity=70240,
        opened=2020,
        role="揭幕周 / 淘汰赛",
        description="一座极具未来感的可容纳 7 万人的多功能场馆，半透明 ETFE 屋顶夜间灯光秀震撼。",
        flag_emoji="🇺🇸",
        image_url=_wm("SoFi_Stadium_2023.jpg"),
        accent="#FF6B7E",
    ),
    Stadium(
        name_zh="AT&T 体育场",
        name_en="AT&T Stadium",
        city="达拉斯 / 阿灵顿",
        country="美国",
        capacity=80000,
        opened=2009,
        role="半决赛之一",
        description="室内空调球场，可开合屋顶；牛仔队主场，电子大屏世界级。",
        flag_emoji="🇺🇸",
        image_url=_wm("Arlington_June_2020_4_%28AT%26T_Stadium%29.jpg"),
        accent="#3a8dff",
    ),
    Stadium(
        name_zh="梅赛德斯-奔驰体育场",
        name_en="Mercedes-Benz Stadium",
        city="亚特兰大",
        country="美国",
        capacity=71000,
        opened=2017,
        role="淘汰赛阶段",
        description="标志性「相机光圈」可开合屋顶，被誉为 21 世纪最具设计感的体育馆之一。",
        flag_emoji="🇺🇸",
        image_url=_wm("Mercedes_Benz_Stadium_time_lapse_capture_2017-08-13.jpg"),
        accent="#FFB957",
    ),
    Stadium(
        name_zh="林肯金融球场",
        name_en="Lincoln Financial Field",
        city="费城",
        country="美国",
        capacity=69596,
        opened=2003,
        role="小组赛 + 16 强",
        description="老鹰队主场，场地草皮在比赛季由专业团队空运。",
        flag_emoji="🇺🇸",
        image_url=_wm("Lincoln_Financial_Field_%28Aerial_view%29.jpg"),
        accent="#2ED883",
    ),
    Stadium(
        name_zh="阿罗黑德体育场",
        name_en="Arrowhead Stadium",
        city="堪萨斯城",
        country="美国",
        capacity=76416,
        opened=1972,
        role="小组赛 + 8 强",
        description="酋长队主场，曾创下吉尼斯认证最响球迷分贝纪录 142.2 dB。",
        flag_emoji="🇺🇸",
        image_url=_wm("Aerial_view_of_Arrowhead_Stadium_08-31-2013.jpg"),
        accent="#E5394E",
    ),
    Stadium(
        name_zh="NRG 体育场",
        name_en="NRG Stadium",
        city="休斯顿",
        country="美国",
        capacity=72220,
        opened=2002,
        role="小组赛",
        description="德州人队主场，全美第一座可开合屋顶的 NFL 场馆。",
        flag_emoji="🇺🇸",
        image_url=_wm("Nrg_stadium.jpg"),
        accent="#FF6B7E",
    ),
    Stadium(
        name_zh="哈德罗克体育场",
        name_en="Hard Rock Stadium",
        city="迈阿密",
        country="美国",
        capacity=65326,
        opened=1987,
        role="季军争夺战",
        description="海豚队主场，毗邻一级方程式迈阿密大奖赛赛道。",
        flag_emoji="🇺🇸",
        image_url=_wm("Hard_Rock_Stadium_for_Super_Bowl_LIV_%2849606710103%29.jpg"),
        accent="#FFB957",
    ),
    Stadium(
        name_zh="吉列体育场",
        name_en="Gillette Stadium",
        city="波士顿 / 福克斯堡",
        country="美国",
        capacity=64628,
        opened=2002,
        role="小组赛 + 8 强",
        description="爱国者队主场，为本届世界杯特别铺设天然草皮。",
        flag_emoji="🇺🇸",
        image_url=_wm("Gillette_Stadium_%28Top_View%29.jpg"),
        accent="#3a8dff",
    ),
    Stadium(
        name_zh="李维斯体育场",
        name_en="Levi's Stadium",
        city="旧金山湾区 / 圣克拉拉",
        country="美国",
        capacity=68500,
        opened=2014,
        role="小组赛 + 16 强",
        description="49 人队主场，曾被评为全美最环保的体育场之一。",
        flag_emoji="🇺🇸",
        image_url=_wm("Levi%27s_Stadium_in_February_2016_prior_to_Super_Bowl_50_%2824398261729%29.jpg"),
        accent="#2ED883",
    ),
    Stadium(
        name_zh="卢门球场",
        name_en="Lumen Field",
        city="西雅图",
        country="美国",
        capacity=68740,
        opened=2002,
        role="小组赛",
        description="海鹰队主场（Lumen Field），最深的足球氛围之一。",
        flag_emoji="🇺🇸",
        image_url=_wm("2026_FIFA_World_Cup_-_Belgium_v._Egypt_in_Seattle_-_04.jpg"),
        accent="#9b6bff",
    ),
    # ── 加拿大 2 座 ─────────────────────────
    Stadium(
        name_zh="卑诗体育馆",
        name_en="BC Place",
        city="温哥华",
        country="加拿大",
        capacity=54500,
        opened=1983,
        role="小组赛 + 16 强",
        description="加拿大唯一一座承办本届世界杯的西海岸球场，位于温哥华市中心。",
        flag_emoji="🇨🇦",
        image_url=_wm("BC_Place_2015_Women%27s_FIFA_World_Cup.jpg"),
        accent="#E5394E",
    ),
    Stadium(
        name_zh="BMO 体育场",
        name_en="BMO Field",
        city="多伦多",
        country="加拿大",
        capacity=45736,
        opened=2007,
        role="小组赛",
        description="多伦多 FC 主场，为承办世界杯特别扩建至 4.5 万座位。",
        flag_emoji="🇨🇦",
        image_url=_wm("Toronto_BMO_Field_in_2024.jpg"),
        accent="#FF6B7E",
    ),
    # ── 墨西哥 3 座 ─────────────────────────
    Stadium(
        name_zh="阿兹特克体育场",
        name_en="Estadio Azteca",
        city="墨西哥城",
        country="墨西哥",
        capacity=87523,
        opened=1966,
        role="揭幕战（2026 年 6 月 11 日）",
        description="历史唯一三度承办世界杯（1970/1986/2026）的传奇球场，承办本届揭幕战。",
        flag_emoji="🇲🇽",
        image_url=_wm("Vista_a%C3%A9rea_del_Estadio_Azteca_-_2026_-_02.jpg"),
        accent="#FFB957",
    ),
    Stadium(
        name_zh="蒙特雷体育场",
        name_en="Estadio BBVA",
        city="蒙特雷",
        country="墨西哥",
        capacity=53500,
        opened=2015,
        role="小组赛 + 16 强",
        description="也叫做 El Gigante de Acero（钢铁巨人），坐落于群山之中。",
        flag_emoji="🇲🇽",
        image_url=_wm("Mexico_Guadalupe_Monterrey_Estadio_BBVA_Bancomer_fifa_world_cup_2026_6.JPG"),
        accent="#2ED883",
    ),
    Stadium(
        name_zh="阿克隆体育场",
        name_en="Estadio Akron",
        city="瓜达拉哈拉",
        country="墨西哥",
        capacity=49850,
        opened=2010,
        role="小组赛",
        description="美洲狮主场，毗邻 Bosque Los Colomos 自然保护区。",
        flag_emoji="🇲🇽",
        image_url=_wm("Estadio_Akron_02-07-2022_cabecera_sur_lado_derecho_%283%29.jpg"),
        accent="#3a8dff",
    ),
]


def all_stadiums() -> list[Stadium]:
    return list(WC2026_STADIUMS)


def find_stadium(query: str) -> list[Stadium]:
    q = query.strip().lower()
    if not q:
        return all_stadiums()
    return [
        s
        for s in WC2026_STADIUMS
        if q in s.name_zh.lower()
        or q in s.name_en.lower()
        or q in s.city.lower()
        or q in s.country.lower()
    ]
