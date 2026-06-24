"""一次性生成器：抓取 Sports Mole 世界杯赛前预览页，解析每场的比分预测
（We say）、双方预测首发阵容、近期战绩（全部赛事 W/D/L），生成
app/services/sportsmole_data.py。

为什么只取结构化字段
--------------------
Sports Mole 的预览正文为受版权保护的英文长文，本软件界面为中文且不做逐字
转载，因此本生成器只提取**可结构化的事实型数据**：

  * ``We say`` 比分预测（如 "Paraguay 0-1 Australia"）；
  * 双方「possible starting lineup」预测首发名单；
  * 双方近期战绩（all competitions 的 W/D/L 序列）。

这些恰好是 forebet / kickform 两个来源所没有的（尤其是**预测首发阵容**），
能为预测页补充实质性的新信息。预测页会据此生成中文摘要并展示出处链接。

数据来源：sportsmole.co.uk（预览页服务端可直接抓取，返回 HTTP 200）。
运行：python scripts_gen_sportsmole.py
"""
from __future__ import annotations

import json
import re
import urllib.request

INDEX = "https://www.sportsmole.co.uk/football/preview/"
BASE = "https://www.sportsmole.co.uk"
HEAD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Sports Mole 英文队名 → 懂球帝中文名（与 geo_data.TEAM_COORDS 一致，含命名变体）
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
    "Netherlands": "荷兰", "Japan": "日本", "Sweden": "瑞典", "Turkey": "土耳其",
    "Turkiye": "土耳其", "Türkiye": "土耳其", "USA": "美国", "United States": "美国",
    "Paraguay": "巴拉圭", "Australia": "澳大利亚", "Uruguay": "乌拉圭", "Spain": "西班牙",
    "Cape Verde": "佛得角", "Cabo Verde": "佛得角", "Saudi Arabia": "沙特阿拉伯",
    "New Zealand": "新西兰", "Belgium": "比利时", "Egypt": "埃及", "Iran": "伊朗",
    "IR Iran": "伊朗",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def clean(s: str) -> str:
    """去 HTML 标签与多余空白，还原常见实体。"""
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&")
         .replace("&#039;", "'").replace("&rsquo;", "'")
         .replace("&quot;", '"'))
    return re.sub(r"\s+", " ", s).strip()


def paras(segment: str) -> list[str]:
    """从一段 HTML 中抽出干净的段落文本（剔除广告 / 博彩促销 / 阵容行 / 空段）。"""
    out = []
    skip_kw = ("akcelo", "slmadshb", "&pound;", "free bets",
               "New Customer offer", "Gamble Responsibly", "T&amp;Cs apply")
    for mm in re.finditer(r"<p[^>]*>(.*?)</p>", segment, re.S):
        raw = mm.group(1)
        if any(k in raw for k in skip_kw) or "possible starting lineup" in raw:
            continue
        txt = clean(raw)
        if not txt or len(txt) <= 1:
            continue
        if txt.endswith("form:") or "form (all competitions):" in txt \
                or "World Cup form:" in txt:  # 战绩小标题（W/D/L 另行结构化）
            continue
        out.append(txt)
    return out


def parse_form(html: str, team_en: str, scope: str) -> list[str]:
    """提取某队某口径（World Cup / all competitions）的 W/D/L 序列。"""
    label = re.escape(f"{team_en} {scope}:")
    m = re.search(label + r"</p>\s*<div[^>]*>\s*<ul[^>]*>(.*?)</ul>", html, re.S)
    if not m:
        return []
    return re.findall(r'<span class="wRd">([WDL])</span>', m.group(1))


def parse_preview(url: str) -> dict | None:
    html = fetch(url)

    # 标题 → 两队英文名
    t = re.search(r'itemprop="headline">\s*Preview:\s*(.*?)\s*-\s*prediction',
                  html, re.S)
    if not t:
        return None
    title = clean(t.group(1))
    mt = re.match(r"(.+?)\s+vs\.?\s+(.+)", title)
    if not mt:
        return None
    home_en, away_en = mt.group(1).strip(), mt.group(2).strip()
    home_cn, away_cn = EN2CN.get(home_en), EN2CN.get(away_en)
    if not home_cn or not away_cn:
        return ("UNMAPPED", home_en, away_en)

    # We say 比分预测
    we = re.search(r'<h2[^>]*>\s*We say:\s*([^<]+)</h2>', html)
    sh = sa = None
    if we:
        sc = re.search(r"(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)", clean(we.group(1)))
        if sc:
            n1, g1, g2, n2 = (sc.group(1).strip(), int(sc.group(2)),
                              int(sc.group(3)), sc.group(4).strip())
            # 按主客对齐（We say 通常主队在前，但仍按名字校验）
            if n1 == away_en or n2 == home_en:
                sh, sa = g2, g1
            else:
                sh, sa = g1, g2

    # 预测首发
    lineups = {}
    for mm in re.finditer(
        r'<p><strong>([^<]+?) possible starting lineup:</strong></p>\s*<p>([^<]+)</p>',
        html,
    ):
        lineups[mm.group(1).strip()] = clean(mm.group(2))

    # 发布时间
    pub = re.search(r'article:published_time"[^>]*content="([^"]+)"', html)

    # ── 全文 prose（用于翻译）：intro / Match preview / Team News ──
    body_start = html.find('itemprop="articleBody"')
    body_end = html.find("People mentioned in this article")
    if body_end == -1:
        body_end = len(html)
    body = html[body_start:body_end] if body_start != -1 else html

    p_prev = body.find("<h2>Match preview</h2>")
    p_news = body.find("<h2>Team News</h2>")
    p_say = body.find("We say:")
    p_lineup = body.find("possible starting lineup")
    # team news 在「预测首发」之前结束（避免把阵容名单/促销并入正文）
    news_end_candidates = [x for x in (p_lineup, p_say) if x != -1] or [len(body)]
    cut_news_end = min(news_end_candidates)

    intro = paras(body[:p_prev]) if p_prev != -1 else []
    preview = paras(body[p_prev:p_news]) if p_prev != -1 and p_news != -1 else []
    team_news = paras(body[p_news:cut_news_end]) if p_news != -1 else []

    return {
        "article_id": int(re.search(r"_(\d+)\.html", url).group(1)),
        "home_en": home_en, "away_en": away_en,
        "home_cn": home_cn, "away_cn": away_cn,
        "url": url,
        "date": pub.group(1) if pub else "",
        "score_home": sh, "score_away": sa,
        "lineup_home": lineups.get(home_en, ""),
        "lineup_away": lineups.get(away_en, ""),
        "form_home": parse_form(html, home_en, "form (all competitions)"),
        "form_away": parse_form(html, away_en, "form (all competitions)"),
        "intro_en": intro,
        "preview_en": preview,
        "team_news_en": team_news,
    }


def main():
    idx = fetch(INDEX)
    links = sorted(set(re.findall(
        r'href="(/football/[^"]*?/preview/[^"]*?_\d+\.html)"', idx)))
    print(f"found {len(links)} preview links")

    entries, skipped = [], []
    for path in links:
        url = BASE + path
        try:
            res = parse_preview(url)
        except Exception as e:
            skipped.append((path, f"{type(e).__name__}: {e}"))
            continue
        if res is None:
            skipped.append((path, "no headline / score"))
        elif isinstance(res, tuple):  # UNMAPPED
            skipped.append((path, f"unmapped {res[1]} / {res[2]}"))
        else:
            entries.append(res)

    entries.sort(key=lambda e: e["article_id"])

    header = (
        '"""自动生成：Sports Mole 各场赛前预览的结构化数据。\n\n'
        "请勿手工编辑。由 scripts_gen_sportsmole.py 抓取 sportsmole.co.uk 预览页\n"
        "解析生成。仅含事实型字段：比分预测（We say）、双方预测首发、近期战绩，\n"
        "不含原文逐字转载。\n"
        '数据来源：sportsmole.co.uk。\n"""\n\n'
        "null = None  # 兼容 JSON 字面量中的 null（缺失值）\n\n"
        "SPORTSMOLE_RAW = "
    )
    with open("app/services/sportsmole_data.py", "w", encoding="utf-8") as f:
        f.write(header)
        f.write(json.dumps(entries, ensure_ascii=False, indent=4))
        f.write("\n")

    print(f"generated {len(entries)} entries")
    for e in entries:
        sc = (f"{e['score_home']}-{e['score_away']}"
              if e["score_home"] is not None else "—")
        print(f"  {e['home_cn']} {sc} {e['away_cn']}  "
              f"lineups={'Y' if e['lineup_home'] and e['lineup_away'] else 'N'}")
    for path, why in skipped:
        print("  skipped", path, why)


if __name__ == "__main__":
    main()
