"""一次性生成器：抓取 ThePuntersPage/KickForm 后端接口，生成
app/services/kickform_data.py（KickForm 各场预测的结构化原始数据）。

世界杯带预测的 fixture_id 区间：199773–199804（共 32 场）。
运行：python scripts_gen_kickform.py
"""
import json
import urllib.request
import time

BASE = ("https://www.thepunterspage.com/app/plugins/wis-stats-integration-wp/"
        "stats-front/dist/en_GB/api.php?stats/fixture?fixture_id={fid}"
        "&with_predictions=1&ws=tpp&tzo=-480&uc=pl")
HEAD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# 英文队名（API name）→ 懂球帝中文队名（与 geo_data.TEAM_COORDS 一致）
EN2CN = {
    "Argentina": "阿根廷", "Austria": "奥地利", "France": "法国", "Iraq": "伊拉克",
    "Norway": "挪威", "Senegal": "塞内加尔", "Jordan": "约旦", "Algeria": "阿尔及利亚",
    "Portugal": "葡萄牙", "Uzbekistan": "乌兹别克斯坦", "England": "英格兰", "Ghana": "加纳",
    "Panama": "巴拿马", "Croatia": "克罗地亚", "Colombia": "哥伦比亚",
    "Democratic Republic of the Congo": "刚果民主共和国", "Switzerland": "瑞士",
    "Canada": "加拿大", "Bosnia and Herzegovina": "波黑", "Qatar": "卡塔尔",
    "Scotland": "苏格兰", "Brazil": "巴西", "Morocco": "摩洛哥", "Haiti": "海地",
    "Czechia": "捷克", "Mexico": "墨西哥", "South Africa": "南非", "South Korea": "韩国",
    "Ecuador": "厄瓜多尔", "Germany": "德国", "Curacao": "库拉索",
    "Cote d'Ivoire": "科特迪瓦", "Tunisia": "突尼斯", "Netherlands": "荷兰",
    "Japan": "日本", "Sweden": "瑞典", "Turkiye": "土耳其", "USA": "美国",
    "Paraguay": "巴拉圭", "Australia": "澳大利亚", "Uruguay": "乌拉圭", "Spain": "西班牙",
    "Cabo Verde": "佛得角", "Saudi Arabia": "沙特阿拉伯", "New Zealand": "新西兰",
    "Belgium": "比利时", "Egypt": "埃及", "IR Iran": "伊朗",
}

TPP_URL = "https://www.thepunterspage.com/kickform/world-cup/{hs}-vs-{as_}/{hash}/"


def fetch(fid):
    req = urllib.request.Request(BASE.format(fid=fid), headers=HEAD)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def num(x):
    try:
        return round(float(x), 1)
    except (TypeError, ValueError):
        return None


def odd(best, k):
    try:
        return round(float((best.get(k) or {}).get("decimal_odd")), 2)
    except (TypeError, ValueError):
        return None


entries = []
skipped = []
for fid in range(199773, 199805):
    try:
        d = fetch(fid)
    except Exception as e:
        skipped.append((fid, f"fetch {type(e).__name__}"))
        continue
    pred = d.get("predictions") or {}
    if not pred:
        skipped.append((fid, "no predictions"))
        continue
    he = (d.get("home_team") or {}).get("name")
    ae = (d.get("away_team") or {}).get("name")
    hcn, acn = EN2CN.get(he), EN2CN.get(ae)
    if not hcn or not acn:
        skipped.append((fid, f"unmapped {he} / {ae}"))
        continue

    trend = pred.get("trend") or {}
    res = pred.get("result") or {}
    btts = pred.get("btts") or {}
    ou = pred.get("over-under_goals") or {}
    best = d.get("best_odds") or {}
    tip = pred.get("tip") or {}

    top_scores = []
    for k in ("result1", "result2", "result3"):
        r = res.get(k)
        if r:
            top_scores.append([r.get("home_goals"), r.get("away_goals"),
                               num(r.get("percent"))])

    entries.append({
        "fixture_id": fid,
        "home_en": he, "away_en": ae,
        "home_cn": hcn, "away_cn": acn,
        "round": d.get("round"), "date": d.get("date"),
        "venue": d.get("venue") or "", "referee": d.get("referee") or "",
        "url": TPP_URL.format(hs=(d.get("home_team") or {}).get("slug"),
                              as_=(d.get("away_team") or {}).get("slug"),
                              hash=d.get("hash_id")),
        "p_home": num(trend.get("1")), "p_draw": num(trend.get("X")),
        "p_away": num(trend.get("2")),
        "top_scores": top_scores,
        "top_prediction": (tip.get("top_prediction") or "").strip(),
        "btts_yes": num(btts.get("btts_yes")), "btts_no": num(btts.get("btts_no")),
        "over_1_5": num(ou.get("over_1_5")), "over_2_5": num(ou.get("over_2_5")),
        "over_3_5": num(ou.get("over_3_5")),
        "odds_home": odd(best, "1"), "odds_draw": odd(best, "X"),
        "odds_away": odd(best, "2"),
    })
    time.sleep(0.2)

header = ('"""自动生成：KickForm（ThePuntersPage）各场赛前预测原始数据。\n\n'
          '请勿手工编辑。由 scripts_gen_kickform.py 抓取后端接口生成，\n'
          '数据来源：thepunterspage.com / KickForm（wis-stats 接口）。\n'
          '世界杯 fixture_id 区间 199773–199804。\n"""\n\n'
          "null = None  # 兼容 JSON 字面量中的 null（缺失值）\n\n"
          "KICKFORM_RAW = ")

with open("app/services/kickform_data.py", "w", encoding="utf-8") as f:
    f.write(header)
    f.write(json.dumps(entries, ensure_ascii=False, indent=4))
    f.write("\n")

print(f"generated {len(entries)} entries")
for fid, why in skipped:
    print("  skipped", fid, why)
