"""一次性生成器：抓取 FreeSuperTips 世界杯赛事预测页，解析每场的赛前分析
全文（JSON-LD articleBody）、分析标题与领先要点，生成
app/services/freesupertips_data.py。

FreeSuperTips 的预测页把完整分析以结构化的 JSON-LD ``articleBody`` 暴露在
页面里（服务端可直接抓取，HTTP 200），因此可以稳定地取到**完整的分析正文**
（而非省略版）。本生成器只取事实型/分析型文本字段，供翻译层译成中文后在
软件「媒体 / 模型预测」卡片中以大段篇幅展示，并标注出处链接。

数据来源：freesupertips.com。
运行：python scripts_gen_freesupertips.py
"""
from __future__ import annotations

import json
import re
import urllib.request

INDEX = "https://www.freesupertips.com/predictions/"
HEAD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# FreeSuperTips 英文队名 → 中文名（含其命名变体）
EN2CN = {
    "Argentina": "阿根廷", "Austria": "奥地利", "France": "法国", "Iraq": "伊拉克",
    "Norway": "挪威", "Senegal": "塞内加尔", "Jordan": "约旦", "Algeria": "阿尔及利亚",
    "Portugal": "葡萄牙", "Uzbekistan": "乌兹别克斯坦", "England": "英格兰", "Ghana": "加纳",
    "Panama": "巴拿马", "Croatia": "克罗地亚", "Colombia": "哥伦比亚",
    "Congo DR": "刚果民主共和国", "DR Congo": "刚果民主共和国", "Congo": "刚果民主共和国",
    "Switzerland": "瑞士", "Canada": "加拿大", "Qatar": "卡塔尔",
    "Bosnia And Herzegovina": "波黑", "Bosnia and Herzegovina": "波黑",
    "Scotland": "苏格兰", "Brazil": "巴西", "Morocco": "摩洛哥", "Haiti": "海地",
    "Czechia": "捷克", "Czech Republic": "捷克", "Mexico": "墨西哥",
    "South Africa": "南非", "South Korea": "韩国", "Ecuador": "厄瓜多尔", "Germany": "德国",
    "Curacao": "库拉索", "Ivory Coast": "科特迪瓦", "Tunisia": "突尼斯", "Netherlands": "荷兰",
    "Japan": "日本", "Sweden": "瑞典", "Turkiye": "土耳其", "Turkey": "土耳其", "USA": "美国",
    "Usa": "美国", "Congo Dr": "刚果民主共和国",
    "Paraguay": "巴拉圭", "Australia": "澳大利亚", "Uruguay": "乌拉圭", "Spain": "西班牙",
    "Cape Verde Islands": "佛得角", "Cape Verde": "佛得角",
    "Saudi Arabia": "沙特阿拉伯", "New Zealand": "新西兰", "Belgium": "比利时",
    "Egypt": "埃及", "Iran": "伊朗",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#039;", "'")
         .replace("&#8211;", "-").replace("&#8217;", "'").replace("&rsquo;", "'")
         .replace("&#8216;", "'").replace("&quot;", '"').replace("&#8230;", "…"))
    return re.sub(r"[ \t]+", " ", s).strip()


def slug_to_teams(slug: str) -> tuple[str, str] | None:
    m = re.match(r"([a-z0-9-]+?)-vs-([a-z0-9-]+?)-predictions", slug)
    if not m:
        return None

    def norm(s):
        return " ".join(w.capitalize() for w in s.split("-"))
    return norm(m.group(1)), norm(m.group(2))


def parse_page(url: str, home_en: str, away_en: str) -> dict | None:
    html = fetch(url)

    m = re.search(r'"articleBody"\s*:\s*"(.*?)"\s*[,}]', html, re.S)
    if not m:
        return None
    body = m.group(1).encode().decode("unicode_escape", "ignore")
    body = (body.replace("&#8211;", "-").replace("&#8217;", "'")
            .replace("&#8216;", "'").replace("&#8230;", "…").replace("&amp;", "&"))
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    if not lines:
        return None

    # 领先要点（开头若干条短句）+ 分析标题 + 正文段落
    # 经验：开头几行是要点统计，随后一行是分析小标题，其余是正文。
    headline = re.search(r'"headline"\s*:\s*"([^"]+)"', html)
    title = clean(headline.group(1)) if headline else ""

    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", html, re.S)
    section_title = clean(h2.group(1)) if h2 else ""

    bullets, body_paras = [], []
    for ln in lines:
        if section_title and ln == section_title:
            continue
        # 短句且不含句末标点的，归为要点
        if len(ln) < 90 and not re.search(r"[.!?]$", ln) and not body_paras:
            bullets.append(ln)
        else:
            body_paras.append(ln)

    pub = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)

    return {
        "home_en": home_en, "away_en": away_en,
        "home_cn": EN2CN[home_en], "away_cn": EN2CN[away_en],
        "url": url,
        "date": pub.group(1) if pub else "",
        "title_en": title,
        "section_title_en": section_title,
        "bullets_en": bullets,
        "body_en": body_paras,
    }


def main():
    idx = fetch(INDEX)
    slugs = sorted(set(re.findall(
        r'/predictions/([a-z0-9-]+-vs-[a-z0-9-]+-predictions[a-z0-9-]*)/', idx)))
    print(f"found {len(slugs)} match prediction pages")

    entries, skipped = [], []
    for slug in slugs:
        url = f"https://www.freesupertips.com/predictions/{slug}/"
        teams = slug_to_teams(slug)
        if not teams:
            skipped.append((slug, "slug parse"))
            continue
        home_en, away_en = teams
        if home_en not in EN2CN or away_en not in EN2CN:
            skipped.append((slug, f"unmapped {home_en} / {away_en}"))
            continue
        try:
            res = parse_page(url, home_en, away_en)
        except Exception as e:
            skipped.append((slug, f"{type(e).__name__}: {e}"))
            continue
        if res is None:
            skipped.append((slug, "no articleBody"))
        else:
            entries.append(res)

    entries.sort(key=lambda e: (e["home_cn"], e["away_cn"]))

    header = (
        '"""自动生成：FreeSuperTips 各场赛前分析的结构化文本数据。\n\n'
        "请勿手工编辑。由 scripts_gen_freesupertips.py 抓取 freesupertips.com\n"
        "预测页的 JSON-LD articleBody 解析生成（完整分析正文，未省略）。\n"
        "中文翻译见 prediction_analysis_cn.py。\n"
        '数据来源：freesupertips.com。\n"""\n\n'
        "FREESUPERTIPS_RAW = "
    )
    with open("app/services/freesupertips_data.py", "w", encoding="utf-8") as f:
        f.write(header)
        f.write(json.dumps(entries, ensure_ascii=False, indent=4))
        f.write("\n")

    print(f"generated {len(entries)} entries")
    for e in entries:
        print(f"  {e['home_cn']} vs {e['away_cn']}  "
              f"bullets={len(e['bullets_en'])} paras={len(e['body_en'])}")
    for slug, why in skipped:
        print("  skipped", slug, why)


if __name__ == "__main__":
    main()
