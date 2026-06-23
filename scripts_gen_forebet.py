"""一次性生成器：抓取 Forebet 世界杯列表页，解析每场的 1X2 概率、预测比分、
场均进球、赔率，生成 app/services/forebet_data.py。

数据来源：forebet.com（文字版预测，服务端可抓）。
运行：python scripts_gen_forebet.py
"""
import json
import re
import urllib.request

URL = "https://www.forebet.com/en/predictions-world/world-cup"
HEAD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Forebet 英文队名 → 懂球帝中文名（含 Forebet 的命名变体）
EN2CN = {
    "Argentina": "阿根廷", "Austria": "奥地利", "France": "法国", "Iraq": "伊拉克",
    "Norway": "挪威", "Senegal": "塞内加尔", "Jordan": "约旦", "Algeria": "阿尔及利亚",
    "Portugal": "葡萄牙", "Uzbekistan": "乌兹别克斯坦", "England": "英格兰", "Ghana": "加纳",
    "Panama": "巴拿马", "Croatia": "克罗地亚", "Colombia": "哥伦比亚",
    "DR Congo": "刚果民主共和国", "Democratic Republic of the Congo": "刚果民主共和国",
    "Switzerland": "瑞士", "Canada": "加拿大", "Bosnia-Herzegovina": "波黑",
    "Bosnia and Herzegovina": "波黑", "Qatar": "卡塔尔", "Scotland": "苏格兰",
    "Brazil": "巴西", "Morocco": "摩洛哥", "Haiti": "海地", "Czech Republic": "捷克",
    "Czechia": "捷克", "Mexico": "墨西哥", "South Africa": "南非", "South Korea": "韩国",
    "Ecuador": "厄瓜多尔", "Germany": "德国", "Curacao": "库拉索", "Curaçao": "库拉索",
    "Ivory Coast": "科特迪瓦", "Cote d'Ivoire": "科特迪瓦", "Tunisia": "突尼斯",
    "Netherlands": "荷兰", "Japan": "日本", "Sweden": "瑞典", "Turkiye": "土耳其",
    "Türkiye": "土耳其", "USA": "美国", "Paraguay": "巴拉圭", "Australia": "澳大利亚",
    "Uruguay": "乌拉圭", "Spain": "西班牙", "Cape Verde": "佛得角", "Cabo Verde": "佛得角",
    "Saudi Arabia": "沙特阿拉伯", "New Zealand": "新西兰", "Belgium": "比利时",
    "Egypt": "埃及", "Iran": "伊朗", "IR Iran": "伊朗",
}

req = urllib.request.Request(URL, headers=HEAD)
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

# 按 SportsEvent 切块
blocks = html.split('itemtype="http://schema.org/SportsEvent"')[1:]
print(f"SportsEvent blocks: {len(blocks)}")

entries = []
skipped = []
by_id = {}
for b in blocks:
    names = re.findall(r'<span itemprop="name">([^<]+)</span>', b)
    href = re.search(r'href="/en/football/matches/([a-z0-9-]+)-(\d+)"', b)
    if len(names) < 2 or not href:
        skipped.append("structure")
        continue
    he, ae = names[0].strip(), names[1].strip()
    mid = int(href.group(2))

    prob = re.search(r"class='fprc'>\s*<span[^>]*>(\d+)</span>\s*<span>(\d+)</span>\s*<span>(\d+)</span>", b)
    if not prob:
        # 该 block 无概率（页面里同一场会出现多次），不占用去重，等带概率那份
        continue
    ph, pd, pa = int(prob.group(1)), int(prob.group(2)), int(prob.group(3))

    hcn, acn = EN2CN.get(he), EN2CN.get(ae)
    if not hcn or not acn:
        skipped.append(f"unmapped {he}/{ae}")
        continue
    if mid in by_id:
        continue

    sign = re.search(r'class="forepr"><span>([^<]+)</span>', b)
    score = re.search(r'class="ex_sc tabonly">\s*([0-9]+)\s*-\s*([0-9]+)', b)
    avg = re.search(r'class="avg_sc tabonly">([0-9.]+)', b)
    venue = re.search(r'itemprop="name address" content="([^"]+)"', b)
    date = re.search(r'class="date_bah">([^<]+)<', b)
    haodd = re.search(r'class="haodd">(.*?)</div>', b, re.S)
    odds = re.findall(r'<span>([+\-]?\d+)</span>', haodd.group(1)) if haodd else []

    by_id[mid] = {
        "match_id": mid,
        "home_en": he, "away_en": ae, "home_cn": hcn, "away_cn": acn,
        "url": f"https://www.forebet.com/en/football/matches/{href.group(1)}-{mid}",
        "p_home": ph, "p_draw": pd, "p_away": pa,
        "pred_sign": sign.group(1).strip() if sign else "",
        "score_home": int(score.group(1)) if score else None,
        "score_away": int(score.group(2)) if score else None,
        "avg_goals": float(avg.group(1)) if avg else None,
        "venue": venue.group(1).strip() if venue else "",
        "date": date.group(1).strip() if date else "",
        "odds_home": odds[0] if len(odds) > 0 else "",
        "odds_draw": odds[1] if len(odds) > 1 else "",
        "odds_away": odds[2] if len(odds) > 2 else "",
    }

entries = list(by_id.values())

header = ('"""自动生成：Forebet 各场赛前预测（1X2 概率 / 预测比分 / 场均进球 / 赔率）。\n\n'
          "请勿手工编辑。由 scripts_gen_forebet.py 抓取 forebet.com 列表页解析生成。\n"
          '数据来源：forebet.com。\n"""\n\n'
          "null = None  # 兼容 JSON 字面量中的 null（缺失值）\n\n"
          "FOREBET_RAW = ")
with open("app/services/forebet_data.py", "w", encoding="utf-8") as f:
    f.write(header)
    f.write(json.dumps(entries, ensure_ascii=False, indent=4))
    f.write("\n")

print(f"generated {len(entries)} entries")
from collections import Counter
print("skip reasons:", Counter(skipped))
for e in entries[:3]:
    print("  sample:", e["home_cn"], e["p_home"], e["p_draw"], e["p_away"],
          f"{e['score_home']}-{e['score_away']}", e["away_cn"], e["avg_goals"])
