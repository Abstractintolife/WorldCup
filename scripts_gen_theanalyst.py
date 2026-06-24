"""自动抓取 The Analyst（Opta）数据并生成 ``app/services/theanalyst_data.py``。

两类数据
--------
1. **夺冠 / 出线概率**（Opta 超级计算机赛事模拟）——
   取自 performfeeds「seasonandtournamentsimulations」接口（与
   theanalyst.com/competition/fifa-world-cup/predictions 同源）。
   字段：每支球队的「夺冠概率」「进决赛概率」「出线（晋级淘汰赛）概率」。

2. **逐场赛前预测**（Opta 超级计算机 25,000 次赛前模拟）——
   取自各场 ``*-prediction-world-cup-2026-match-preview`` 预览文章，解析出
   1X2（主胜 / 平 / 客胜）概率、关键事实（Key Insights）、预测正文与预测首发。

请勿手工编辑生成结果。重新运行本脚本即可刷新快照。
数据来源：theanalyst.com / Opta（api.performfeeds.com）。
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request

OUTLET = "1mjq6w6ezkxe611ykkj8rgz7f1"
TMCL = "873cbl9cd9butm4air0mugxzo"
SIM_URL = (
    f"https://api.performfeeds.com/soccerdata/seasonandtournamentsimulations/"
    f"{OUTLET}?tmcl={TMCL}&_fmt=json&_rt=c"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://theanalyst.com/",
}

# ── 英文队名 → 中文（与项目内既有中文名保持一致）────────────────
EN_TO_CN = {
    "Argentina": "阿根廷", "Austria": "奥地利", "France": "法国", "Iraq": "伊拉克",
    "Spain": "西班牙", "Saudi Arabia": "沙特阿拉伯", "England": "英格兰",
    "Croatia": "克罗地亚", "Ghana": "加纳", "Panama": "巴拿马", "Portugal": "葡萄牙",
    "Uzbekistan": "乌兹别克斯坦", "DR Congo": "刚果民主共和国", "Germany": "德国",
    "Ivory Coast": "科特迪瓦", "Norway": "挪威", "Senegal": "塞内加尔",
    "Brazil": "巴西", "Haiti": "海地", "Morocco": "摩洛哥", "Scotland": "苏格兰",
    "Netherlands": "荷兰", "Sweden": "瑞典", "Japan": "日本", "Tunisia": "突尼斯",
    "Belgium": "比利时", "Iran": "伊朗", "Switzerland": "瑞士", "Canada": "加拿大",
    "Bosnia-Herzegovina": "波黑", "Qatar": "卡塔尔", "Mexico": "墨西哥",
    "South Korea": "韩国", "Korea Republic": "韩国", "Czechia": "捷克",
    "Czech Republic": "捷克", "South Africa": "南非", "USA": "美国",
    "United States": "美国", "Australia": "澳大利亚", "Colombia": "哥伦比亚",
    "Uruguay": "乌拉圭", "Cape Verde": "佛得角", "Jordan": "约旦",
    "Algeria": "阿尔及利亚", "New Zealand": "新西兰", "Egypt": "埃及",
    "Ecuador": "厄瓜多尔", "Curacao": "库拉索", "Curaçao": "库拉索",
    "Turkiye": "土耳其", "Türkiye": "土耳其", "Turkey": "土耳其",
    "Paraguay": "巴拉圭",
}


def _cn(en: str) -> str:
    en = en.strip()
    if en in EN_TO_CN:
        return EN_TO_CN[en]
    # 容错：去掉重音 / 部分匹配
    for k, v in EN_TO_CN.items():
        if k.lower() == en.lower():
            return v
    return en


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def _strip(htmltext: str) -> str:
    import html as _h
    t = re.sub(r"<[^>]+>", " ", htmltext)
    return re.sub(r"\s+", " ", _h.unescape(t)).strip()


# ════════════════════════════════════════════════════════════════════
#  机器翻译（英文 → 中文）—— 用于把整篇分析正文译为中文
# ════════════════════════════════════════════════════════════════════
#: 译文缓存（去重相同句子，跨场复用，显著减少请求数）。
_TR_CACHE: dict[str, str] = {}
_GT_URL = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=en&tl=zh-CN&dt=t&q=")


def _gt_once(text: str) -> str:
    req = urllib.request.Request(
        _GT_URL + urllib.parse.quote(text),
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return "".join(seg[0] for seg in data[0] if seg and seg[0])


def _translate(text: str) -> str:
    """把一段英文译为中文（带缓存 + 重试）；失败时回退英文原文。"""
    text = (text or "").strip()
    if not text:
        return ""
    if text in _TR_CACHE:
        return _TR_CACHE[text]
    last = ""
    for attempt in range(4):
        try:
            out = _gt_once(text).strip()
            if out:
                _TR_CACHE[text] = out
                time.sleep(0.05)
                return out
        except Exception as exc:  # pragma: no cover - 网络/限流
            last = str(exc)
            time.sleep(0.6 * (attempt + 1))
    print(f"    ! translate fail ({last}); 回退英文", file=sys.stderr)
    _TR_CACHE[text] = text
    return text


def _translate_paras(paras: list[str]) -> list[str]:
    """逐段翻译（按 ~1200 字符分块合并请求，换行可被保留），返回等长中文列表。"""
    paras = [p for p in (paras or []) if p and p.strip()]
    if not paras:
        return []
    out: list[str] = []
    chunk: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal chunk, size
        if not chunk:
            return
        joined = "\n".join(chunk)
        zh = _translate(joined)
        parts = zh.split("\n")
        if len(parts) == len(chunk):
            out.extend(p.strip() for p in parts)
        else:
            # 行数对不上：逐段单独翻译兜底，保证一一对应。
            out.extend(_translate(p) for p in chunk)
        chunk = []
        size = 0

    for p in paras:
        if size + len(p) > 1200 and chunk:
            flush()
        chunk.append(p)
        size += len(p) + 1
    flush()
    return out


# ════════════════════════════════════════════════════════════════════
#  1) 夺冠 / 出线概率
# ════════════════════════════════════════════════════════════════════
def fetch_tournament() -> list[dict]:
    data = json.loads(_get(SIM_URL))
    stages = {s["name"]: s for s in data["stages"]["stage"]}

    # 决赛阶段：typeId 2 = 夺冠概率，typeId 1 = 进决赛概率
    win_final = {}
    for c in stages["Final"]["contestants"]["contestant"]:
        p = {x["typeId"]: x["value"] for x in c["predictions"][0]["predicted"]}
        win_final[c["name"]] = (
            float(p.get("2", "0").rstrip("%")),
            float(p.get("1", "0").rstrip("%")),
        )

    # 出线（晋级淘汰赛，16th Finals）概率 + 小组信息：取自小组赛 division
    out: list[dict] = []
    for grp in stages["Group Stage"]["division"]:
        gname = grp.get("groupName", "")
        for r in grp["ranking"]:
            name = r["contestantName"]
            win, fin = win_final.get(name, (0.0, 0.0))
            out.append({
                "team_en": name,
                "team_cn": _cn(name),
                "code": r.get("contestantCode", ""),
                "group": gname,
                "win_pct": round(win, 2),
                "final_pct": round(fin, 2),
                "points": r.get("points", 0),
                "played": r.get("matchesPlayed", 0),
            })
    out.sort(key=lambda x: -x["win_pct"])
    return out


# ════════════════════════════════════════════════════════════════════
#  2) 逐场赛前预测（解析预览文章）
# ════════════════════════════════════════════════════════════════════
def list_preview_slugs() -> list[str]:
    slugs: list[str] = []
    for page in (1, 2):
        url = (
            "https://theanalyst.com/wp-json/wp/v2/posts?search="
            "match%20preview%20world%20cup%202026&per_page=100&_fields=slug"
            f"&page={page}"
        )
        try:
            arr = json.loads(_get(url))
        except Exception:
            break
        for p in arr:
            s = p.get("slug", "")
            if "match-preview" in s and "world-cup-2026" in s and "-vs-" in s:
                if s not in slugs:
                    slugs.append(s)
        if len(arr) < 100:
            break
    return slugs


#: 多词队名的「区分词」（用于在正文里定位某队的概率，避免 South Korea / South
#  Africa 之类前缀撞车）。未列出的取首词。
_DISTINCT_TOKEN = {
    "South Korea": "korea", "South Africa": "africa", "New Zealand": "zealand",
    "Cape Verde": "verde", "Saudi Arabia": "saudi", "DR Congo": "congo",
    "Bosnia-Herzegovina": "bosnia", "Ivory Coast": "ivory",
    "Czech Republic": "czech", "Czechia": "czechia", "United States": "states",
    "Korea Republic": "korea",
}


def _token(name: str) -> str:
    if name in _DISTINCT_TOKEN:
        return _DISTINCT_TOKEN[name]
    return name.replace("-", " ").split()[0].lower()


def _prediction_paras(article_html: str) -> str:
    """定位真正的「赛前模拟概率」段落（围绕 “pre-match simulations” 锚点），
    取该段 + 紧随其后的一段（常承载另一队胜率与平局率），避免把历史数据类
    段落里的百分比（如「在 74% 的比赛中取得进球」）误当成胜负概率。"""
    import html as _h
    paras = [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", _h.unescape(p))).strip()
        for p in re.findall(r"<p[^>]*>(.*?)</p>", article_html, re.S)
    ]
    anchor_re = re.compile(
        r"pre-match simulations|25,000|supercomputer (?:favours|leant|expects|"
        r"predicts|gives)|emerged victorious|triumphed in|came out on top",
        re.I,
    )
    for i, p in enumerate(paras):
        if "%" in p and anchor_re.search(p):
            chunk = p
            # 紧随其后的一段若仍是概率描述（含 % 且含胜/平措辞），并入
            if i + 1 < len(paras):
                nxt = paras[i + 1]
                if "%" in nxt and re.search(
                    r"rated at|chance of winning|draw|victory|winning|simulations",
                    nxt, re.I,
                ):
                    chunk += " " + nxt
            return chunk[:1400]
    return ""


def _split_1x2(pred_text: str, home: str, away: str
               ) -> tuple[float | None, float | None, float | None]:
    """从预测正文解析主胜 / 平 / 客胜百分比。

    先按「平局」「主队区分词」「客队区分词」就近归类，未归类的概率再回填空缺
    的主 / 客槽位（处理用绰号指代夺冠热门、未直接点名的句式）。
    """
    home_tok = _token(home)
    away_tok = _token(away)
    h = d = a = None
    leftovers: list[float] = []
    for m in re.finditer(r"([\d.]+)\s*%", pred_text):
        val = float(m.group(1))
        if val > 100:
            continue
        ctx = pred_text[max(0, m.start() - 75):m.start()].lower()
        if "draw" in ctx or "stalemate" in ctx:
            if d is None:
                d = val
        elif home_tok in ctx and h is None:
            h = val
        elif away_tok in ctx and a is None:
            a = val
        else:
            leftovers.append(val)
    # 回填：未归类概率补到空缺的主 / 客槽位（夺冠热门常以绰号出现，未直接点名）
    for val in leftovers:
        if h is None:
            h = val
        elif a is None:
            a = val
    return h, d, a


def _valid_triple(h, d, a) -> bool:
    if h is None or d is None or a is None:
        return False
    return 92.0 <= (h + d + a) <= 108.0


def _fav_from_insight(bullet: str, home: str, away: str
                      ) -> tuple[float | None, float | None]:
    """从首条 Key Insight（通常含夺冠热门 + 胜率）解析 (主胜%, 客胜%)。

    Opta 预览的首条要点几乎总是「超算给 X 队 Y% 的取胜概率」。需处理胜 / 负语义：
    「A lost to B in 90.7%」表示 B（胜者）90.7%，而非 A。"""
    home_tok = _token(home)
    away_tok = _token(away)

    def side(tok_pos_text: str) -> str | None:
        low = tok_pos_text.lower()
        if home_tok in low:
            return "home"
        if away_tok in low:
            return "away"
        return None

    pcts = [float(x) for x in re.findall(r"([\d.]+)\s*%", bullet) if float(x) <= 100]
    if not pcts:
        return None, None

    # 「负于」句式：A lost to B in X% → 胜者 B 获得该百分比
    m = re.search(r"(.+?)\s+lost to\s+(.+?)\s+in\b", bullet, re.I)
    if m:
        winner_side = side(m.group(2))
        if winner_side == "home":
            return pcts[0], None
        if winner_side == "away":
            return None, pcts[0]

    # 「仅 X% 取胜机会」弱队句式：该队为劣势方，百分比归其名下
    mu = re.search(r"(.+?)\s+just a\s+([\d.]+)%", bullet, re.I)
    if mu:
        und_side = side(mu.group(1)[-40:])
        if und_side == "home":
            return float(mu.group(2)), None
        if und_side == "away":
            return None, float(mu.group(2))

    # 通用：先出现的队为热门、对应首个百分比；次个百分比归对手
    low = bullet.lower()
    hi = low.find(home_tok)
    ai = low.find(away_tok)
    hi = hi if hi >= 0 else 10 ** 9
    ai = ai if ai >= 0 else 10 ** 9
    fav_pct = pcts[0]
    other_pct = pcts[1] if len(pcts) >= 2 else None
    if hi <= ai:
        return fav_pct, other_pct
    return other_pct, fav_pct


def _clean_para(seg: str) -> str:
    import html as _h
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", _h.unescape(seg))).strip()


#: 抓取正文时过滤掉的导航 / 页脚 / 促销类噪声段。
_JUNK_KW = (
    "Search", "World Cup 2026", "Subscribe", "newsletter", "Sign up", "Gamble",
    "cookie", "All rights", "Follow", "Opta Analyst", "Read more", "READ MORE",
    "Premier League", "Download", "App Store", "Google Play",
)


def _good_para(t: str) -> bool:
    return len(t) >= 35 and not any(k in t for k in _JUNK_KW)


def extract_analysis(article_html: str) -> list[tuple[str, list[str], bool]]:
    """把预览文章正文切成有序分析块。

    返回 ``[(中文小标题, 英文段落列表, 是否要点列表), ...]``，覆盖文章的**全部**
    分析内容：关键数据速览（Key Insights 要点）、深度分析（叙述段落）、历史交锋
    （Head-to-Head）、赛前预测（Prediction）。剔除导航 / 阵容 / 订阅等非分析区。
    """
    h = article_html
    h2 = [(m.start(), m.end(), _clean_para(m.group(1)))
          for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", h, re.S)]

    def find(kw: str):
        for s, e, t in h2:
            if kw.lower() in t.lower():
                return (s, e, t)
        return None

    ki = find("Key Insights")
    h2h = find("Head-to-Head")
    pred = find("Prediction")
    end = len(h)
    for kw in ("Squads", "Predicted Lineups", "Subscribe"):
        f = find(kw)
        if f and pred and f[0] > pred[0]:
            end = f[0]
            break

    def paras(seg: str) -> list[str]:
        return [t for t in (_clean_para(p)
                for p in re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S)) if _good_para(t)]

    def bullets(seg: str) -> list[str]:
        return [t for t in (_clean_para(p)
                for p in re.findall(r"<li[^>]*>(.*?)</li>", seg, re.S)) if _good_para(t)]

    blocks: list[tuple[str, list[str], bool]] = []
    if ki and h2h:
        kb = bullets(h[ki[1]:h2h[0]])
        if kb:
            blocks.append(("关键数据速览", kb, True))
        ana = paras(h[ki[1]:h2h[0]])
        if ana:
            blocks.append(("深度分析", ana, False))
        hp = paras(h[h2h[1]:pred[0]]) if pred else paras(h[h2h[1]:end])
        if hp:
            blocks.append(("历史交锋", hp, False))
    if pred:
        pp = paras(h[pred[1]:end])
        if pp:
            blocks.append(("赛前预测（Opta 超算）", pp, False))
    return blocks


def parse_article(slug: str) -> dict | None:
    url = f"https://theanalyst.com/articles/{slug}"
    try:
        h = _get(url)
    except Exception as exc:
        print(f"  ! fetch fail {slug}: {exc}", file=sys.stderr)
        return None

    title = re.search(r"<title>(.*?)</title>", h)
    title_txt = _strip(title.group(1)) if title else ""
    mt = re.match(r"(.+?)\s+vs\s+(.+?)\s+Prediction", title_txt)
    if not mt:
        return None
    home_en, away_en = mt.group(1).strip(), mt.group(2).strip()

    # Key Insights 列表
    ki = h.find("The Key Insights")
    insights: list[str] = []
    if ki != -1:
        seg = h[ki:ki + 4000]
        for li in re.findall(r"<li[^>]*>(.*?)</li>", seg, re.S):
            txt = _strip(li)
            if txt and len(txt) > 8:
                insights.append(txt)
            if len(insights) >= 6:
                break

    # Prediction 段落（按「赛前模拟概率」锚点定位，避免历史数据百分比干扰）
    pred_text = _prediction_paras(h)
    hp, dp, ap = _split_1x2(pred_text, home_en, away_en)
    # 首条 Key Insight 几乎总会**点名**夺冠热门 + 胜率，据此校正主客归属。
    fav_h, fav_a = _fav_from_insight(insights[0] if insights else "",
                                     home_en, away_en)
    if not _valid_triple(hp, dp, ap):
        # 三元组不可靠：直接采用首条要点的解析结果（无平局率）。
        hp, ap = fav_h, fav_a
        dp = None
    else:
        # 三元组可靠，但主客可能被绰号句式搞反：用要点里的「热门方」校正。
        ins_fav = ("home" if (fav_h or 0) >= (fav_a or 0) else "away") \
            if (fav_h is not None or fav_a is not None) else None
        if ins_fav and hp is not None and ap is not None and hp != ap:
            tri_fav = "home" if hp >= ap else "away"
            if tri_fav != ins_fav:
                hp, ap = ap, hp

    # ── 全文分析（中文译文）：覆盖关键数据 / 深度分析 / 历史交锋 / 赛前预测 ──
    analysis_cn: list[list[str]] = []
    for title, items, is_bullets in extract_analysis(h):
        zh_items = _translate_paras(items)
        if not zh_items:
            continue
        if is_bullets:
            body = "\n".join(f"· {x}" for x in zh_items)
        else:
            body = "\n".join(zh_items)
        analysis_cn.append([title, body])

    # 中文综述：取「赛前预测」首段译文，回退「深度分析」首段。
    summary_cn = ""
    for title, body in analysis_cn:
        if title.startswith("赛前预测"):
            summary_cn = body.split("\n")[0]
            break
    if not summary_cn and analysis_cn:
        summary_cn = analysis_cn[0][1].split("\n")[0].lstrip("· ")

    return {
        "slug": slug,
        "url": url,
        "home_en": home_en,
        "away_en": away_en,
        "home_cn": _cn(home_en),
        "away_cn": _cn(away_en),
        "home_pct": hp,
        "draw_pct": dp,
        "away_pct": ap,
        "insights": insights,
        "prediction": pred_text,
        "summary_cn": summary_cn,
        "analysis_cn": analysis_cn,
    }


# ════════════════════════════════════════════════════════════════════
#  生成
# ════════════════════════════════════════════════════════════════════
def main() -> None:
    print("Fetching tournament simulations ...", file=sys.stderr)
    tournament = fetch_tournament()
    print(f"  {len(tournament)} teams", file=sys.stderr)

    print("Listing preview articles ...", file=sys.stderr)
    slugs = list_preview_slugs()
    print(f"  {len(slugs)} articles", file=sys.stderr)

    matches: list[dict] = []
    for s in slugs:
        rec = parse_article(s)
        if rec is not None:
            matches.append(rec)
            print(f"  ok {rec['home_cn']} vs {rec['away_cn']} "
                  f"({rec['home_pct']}/{rec['draw_pct']}/{rec['away_pct']}) "
                  f"· {len(rec['analysis_cn'])} 块分析译文",
                  file=sys.stderr)

    header = (
        '"""自动生成：The Analyst（Opta）夺冠概率 + 逐场赛前预测快照。\n\n'
        "请勿手工编辑。由 scripts_gen_theanalyst.py 抓取 theanalyst.com / Opta\n"
        "（api.performfeeds.com 赛事模拟接口 + 预览文章）生成。\n"
        '数据来源：theanalyst.com（Opta 超级计算机，25,000 次赛前模拟）。\n"""\n\n'
        "null = None  # 兼容缺失值\n\n"
    )
    body = (
        "THEANALYST_TOURNAMENT = "
        + json.dumps(tournament, ensure_ascii=False, indent=4)
        + "\n\nTHEANALYST_MATCHES = "
        + json.dumps(matches, ensure_ascii=False, indent=4)
        + "\n"
    )
    out_path = "app/services/theanalyst_data.py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + body)
    print(f"Wrote {out_path}: {len(tournament)} teams, {len(matches)} matches",
          file=sys.stderr)


if __name__ == "__main__":
    main()
