"""外部来源赛事预测（媒体 / 模型）。

为什么是「人工整理」而非「实时抓取」
------------------------------------
用户希望把 Squawka 与 KickForm（ThePuntersPage）这类站点的赛前预测翻译成
中文，展示在软件的「AI 赛事预测」页里。但这两个来源服务端均不可直接抓取：

* ``squawka.com`` → 服务端请求一律返回 HTTP 403（反爬拦截）；
* ``thepunterspage.com`` 的比赛页 → 胜/平/负概率与比分由前端 JS 渲染，
  直接抓页面只能拿到空壳模板。**但其后端 JSON 接口可直接访问**，例如
  ``…/stats-front/dist/en_GB/api.php?stats/fixture?fixture_id=<id>&with_predictions=1``
  会返回 KickForm 的 1X2 概率、最可能比分、BTTS、大小球、最佳赔率与文字分析。
  本模块阿根廷 vs 奥地利的 KickForm 数据即取自该接口（fixture 199773）。
* ``forebet.com`` → 文字预测（1X2 + 比分）服务端可抓；但比赛页的
  「OVERALL STATISTICS」整体数据块由 JS 渲染，需按截图人工录入。
* ``sportsmole.co.uk`` → 预览页服务端可直接抓取（HTTP 200）。由
  ``scripts_gen_sportsmole.py`` 解析出比分预测（We say）、双方**预测首发阵容**
  与近期战绩等事实型字段，落成 ``sportsmole_data.py``（不含原文逐字转载）。

因此本模块以**人工整理 + 翻译**的方式，把从这些来源公开获取到的核心预测
（比分预测、盘口赔率、推荐玩法、文字分析等）落成结构化数据，按「参赛双方」
索引。预测页会自动为命中的比赛渲染一张「媒体 / 模型预测」卡片。

如何新增其它比赛
----------------
往 ``_EXTERNAL_DB`` 里按相同结构追加条目即可（键为两队中文名组成的
``frozenset``）。``get_external_predictions`` 会自动按双方名字（无视主客顺序）
匹配，命中则在预测页展示，未命中则该卡片自动隐藏。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.models.match import Match
from app.services.forebet_data import FOREBET_RAW
from app.services.kickform_data import KICKFORM_RAW
from app.services.sportsmole_data import SPORTSMOLE_RAW
from app.services.freesupertips_data import FREESUPERTIPS_RAW
from app.services.prediction_analysis_cn import SPORTSMOLE_CN, FREESUPERTIPS_CN
from app.services.theanalyst import get_match_preview


# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────
@dataclass
class ExternalPrediction:
    """来自某个外部来源（媒体 / 预测模型）的一份赛前预测。"""

    source: str                       # 来源名，如 "Squawka" / "KickForm"
    source_url: str                   # 原文链接（用于标注出处）
    summary: str                      # 中文综述（已翻译 / 转述）
    score_prediction: str = ""        # 比分预测，如 "阿根廷 2 - 1 奥地利"
    win_a: float | None = None        # 主队胜概率 0~1（无则留空）
    draw: float | None = None         # 平局概率 0~1
    win_b: float | None = None        # 客队胜概率 0~1
    odds_text: str = ""               # 盘口赔率说明（已转中文）
    tips: list[str] = field(default_factory=list)  # 推荐玩法 / 投注角度
    note: str = ""                    # 备注（数据获取限制等说明）
    analysis: list[tuple[str, str]] = field(default_factory=list)
    # ↑ 长篇赛前分析，[(小标题, 正文), ...]；正文可含多段（以换行分隔）。
    analysis_lang: str = "zh"         # "zh"=已译中文 / "en"=英文原文回退


@dataclass
class StatRow:
    """球队数据对比中的一行。"""

    label: str                # 指标名，如 "总射门"
    a_value: str              # 主队主数值，如 "108"
    b_value: str              # 客队主数值
    a_sub: str = ""           # 主队补充，如 "场均 12"
    b_sub: str = ""           # 客队补充


@dataclass
class TeamStats:
    """对应 Forebet「OVERALL STATISTICS」的球队整体数据对比。"""

    team_a: str
    team_b: str
    rows: list[StatRow]
    source: str = "Forebet"
    source_url: str = ""
    scope: str = ""           # 统计口径，如 "全场 · 全部赛事"
    note: str = ""


# ─────────────────────────────────────────────
# 人工整理的数据库（键 = 两队中文名 frozenset）
# ─────────────────────────────────────────────
_EXTERNAL_DB: dict[frozenset[str], list[ExternalPrediction]] = {
    frozenset({"阿根廷", "奥地利"}): [
        ExternalPrediction(
            source="Squawka",
            source_url=(
                "https://www.squawka.com/us/news/world-cup/"
                "match-preview-argentina-vs-austria-06-22-26-world-cup-2026/"
            ),
            summary=(
                "阿根廷首战凭借梅西的帽子戏法 3-0 完胜阿尔及利亚，奥地利也以 "
                "3-1 拿下约旦，两队均开门红。作为卫冕冠军，阿根廷状态正盛、"
                "整体实力明显占优，本场（达拉斯 AT&T 球场）被看好取胜；盘口的"
                "倾向同样反映了状态、阵容厚度与卫冕方的连胜势头。"
            ),
            score_prediction="阿根廷 2 - 1 奥地利（若比赛后段才被打开，3-1 同样很有可能）",
            odds_text=(
                "bet365 盘口：阿根廷取胜 -167（约合欧赔 1.60）、平局 +300"
                "（约 4.00）、奥地利取胜 +475（约 5.75）"
            ),
            tips=[
                "全场胜负：阿根廷主胜",
                "梅西任意时间进球",
                "稳一点可搭配「小于 2.5 球 / 双方进球：否」",
                "博高回报可选正确比分 2-0（阿根廷）",
            ],
            note="内容为根据 Squawka 公开预览整理并翻译；赔率为美式盘口，括号内为换算的欧赔参考。",
        ),
        ExternalPrediction(
            source="KickForm（ThePuntersPage）",
            source_url="https://www.thepunterspage.com/kickform/world-cup/argentina-vs-austria/851nE/",
            summary=(
                "KickForm 的「足球公式」看好阿根廷取胜。阿根廷小组首战 3-0 完胜阿尔及利亚、"
                "梅西上演帽子戏法，攻防两端都掌控得当；奥地利 3-1 击败约旦、状态不俗，逼抢"
                "积极、打法直接，开局阶段不容小觑。但综合大赛经验、近期连续零封与锋线终结"
                "能力，模型认为阿根廷主场获胜是更可信的走向。伤停方面，蒙铁尔右侧腿筋有"
                "轻伤、预计不首发，莫利纳有望顶替出任右后卫，阵容深度足以应对。"
            ),
            score_prediction="阿根廷 1 - 0 奥地利（最可能；2-0、2-1 同样接近）",
            win_a=0.682,
            draw=0.176,
            win_b=0.142,
            odds_text="最佳赔率（欧赔）：阿根廷取胜 1.45、平局 4.40、奥地利取胜 8.10",
            tips=[
                "胜负倾向：阿根廷主胜（胜 68% · 平 18% · 负 14%）",
                "最可能比分：1-0、2-0、2-1（首选 1:0）",
                "双方进球：否（55% > 是 45%）",
                "进球数：大于 1.5 球 76% · 大于 2.5 球 52% · 大于 3.5 球 29%",
                "场地：AT&T 球场　·　主裁：Amin Mohamed Omar",
            ],
            note=(
                "数据取自 KickForm / ThePuntersPage 后端统计接口（fixture 199773）并翻译整理，"
                "为该模型实测百分比。"
            ),
        ),
    ],
}


# ─────────────────────────────────────────────
# Forebet「OVERALL STATISTICS」球队数据对比
# ─────────────────────────────────────────────
# 说明：Forebet 比赛页的这块整体统计由网页 JS 渲染，服务端无法直接抓取，
# 因此按截图人工录入。新增比赛照相同结构补充即可。
_TEAM_STATS_DB: dict[frozenset[str], TeamStats] = {
    frozenset({"墨西哥", "韩国"}): TeamStats(
        team_a="墨西哥",
        team_b="韩国",
        source="Forebet",
        source_url="https://www.forebet.com/en/predictions-world/world-cup",
        scope="整体 · 全场 · 全部赛事",
        rows=[
            StatRow("已赛场次", "9", "6"),
            StatRow("总进球", "16", "11", "场均 1.78", "场均 1.83"),
            StatRow("总失球", "4", "4", "场均 0.44", "场均 0.67"),
            StatRow("近期连续进球率", "89%", "100%", "近 9 场 8 场", "近 6 场 6 场"),
            StatRow("总射门", "108", "95", "场均 12", "场均 15.83"),
            StatRow("被封堵射门", "16", "20", "场均 1.78", "场均 3.33"),
            StatRow("射正率", "40%", "35%"),
            StatRow("禁区内射门占比", "60%", "69%"),
            StatRow("总传球", "3219", "3828", "场均 357.67", "场均 638"),
            StatRow("传球成功率", "87%", "88%", "成功 2809 脚", "成功 3384 脚"),
            StatRow("控球率", "58%", "71%"),
            StatRow("大于 1.5 球（近况）", "78%", "100%", "近 9 场 7 场", "近 6 场 6 场"),
            StatRow("大于 2.5 球（近况）", "33%", "33%", "近 9 场 3 场", "近 6 场 2 场"),
            StatRow("平均首个进球时间", "14′", "—", "首个失球约 31′", ""),
        ],
        note=(
            "数据据用户提供的 Forebet「OVERALL STATISTICS」截图整理（墨西哥 vs 韩国）。"
            "该统计板块由网页 JS 渲染、无法服务端自动抓取，故依截图录入；"
            "「平均首个进球时间」按截图标记呈现，仅供参考。"
        ),
    ),
}


# ─────────────────────────────────────────────
# KickForm 自动生成数据（全部 32 场，按中文队名索引）
# ─────────────────────────────────────────────
_KICKFORM_DB: dict[frozenset[str], dict] = {
    frozenset({r["home_cn"], r["away_cn"]}): r for r in KICKFORM_RAW
}

_KF_SOURCE = "KickForm（ThePuntersPage）"


def _pct(x) -> str:
    return f"{round(x)}%" if isinstance(x, (int, float)) else "—"


def _fav_phrase(hcn: str, acn: str, ph, pd, pa) -> str:
    vals = [v for v in (ph, pd, pa) if isinstance(v, (int, float))]
    if not vals:
        return "胜负态势接近"
    top = max(vals)
    if pd == top and (ph is None or pd >= ph) and (pa is None or pd >= pa):
        return "双方势均力敌、平局机会不低"
    if (ph or 0) >= (pa or 0):
        return f"看好{hcn}取胜"
    return f"看好{acn}取胜"


def _raw_to_prediction(raw: dict, team_a_name: str) -> ExternalPrediction:
    """把一条 KickForm 原始数据转成按当前比赛主客顺序对齐的预测。"""
    flip = team_a_name == raw["away_cn"]
    hcn = raw["away_cn"] if flip else raw["home_cn"]
    acn = raw["home_cn"] if flip else raw["away_cn"]
    ph = raw["p_away"] if flip else raw["p_home"]
    pa = raw["p_home"] if flip else raw["p_away"]
    pd = raw["p_draw"]

    scores = []
    for h, a, pct in raw.get("top_scores", []):
        if flip:
            h, a = a, h
        scores.append((h, a, pct))

    # 比分预测文本
    score_pred = ""
    if scores:
        h0, a0, _ = scores[0]
        alt = "、".join(f"{h}-{a}" for h, a, _ in scores[1:])
        score_pred = f"{hcn} {h0} - {a0} {acn}（最可能"
        score_pred += f"；另 {alt}）" if alt else "）"

    # 赔率（按主客对齐）
    oh = raw["odds_away"] if flip else raw["odds_home"]
    oa = raw["odds_home"] if flip else raw["odds_away"]
    od = raw["odds_draw"]
    odds_text = ""
    if oh and od and oa:
        odds_text = f"最佳赔率（欧赔）：{hcn} {oh}、平 {od}、{acn} {oa}"

    fav = _fav_phrase(hcn, acn, ph, pd, pa)
    summary = (
        f"KickForm「足球公式」测算：{fav}。综合胜负概率为 {hcn} {_pct(ph)}、"
        f"平局 {_pct(pd)}、{acn} {_pct(pa)}"
    )
    if scores:
        summary += f"；模型给出的最可能比分为 {scores[0][0]}-{scores[0][1]}。"
    else:
        summary += "。"

    tips = [f"胜负倾向：{fav}（{hcn} {_pct(ph)} · 平 {_pct(pd)} · {acn} {_pct(pa)}）"]
    if scores:
        tips.append("最可能比分：" + "、".join(f"{h}-{a}" for h, a, _ in scores))
    by, bn = raw.get("btts_yes"), raw.get("btts_no")
    if isinstance(by, (int, float)) and isinstance(bn, (int, float)):
        verdict = "是" if by > bn else "否"
        tips.append(f"双方进球：{verdict}（是 {_pct(by)} / 否 {_pct(bn)}）")
    o15, o25, o35 = raw.get("over_1_5"), raw.get("over_2_5"), raw.get("over_3_5")
    if any(isinstance(v, (int, float)) for v in (o15, o25, o35)):
        tips.append(
            f"进球数：大于 1.5 球 {_pct(o15)} · 大于 2.5 球 {_pct(o25)} · "
            f"大于 3.5 球 {_pct(o35)}"
        )
    loc = []
    if raw.get("venue"):
        loc.append(f"场地：{raw['venue']}")
    if raw.get("referee"):
        loc.append(f"主裁：{raw['referee']}")
    if loc:
        tips.append("　·　".join(loc))

    return ExternalPrediction(
        source=_KF_SOURCE,
        source_url=raw.get("url", ""),
        summary=summary,
        score_prediction=score_pred,
        win_a=(ph / 100.0) if isinstance(ph, (int, float)) else None,
        draw=(pd / 100.0) if isinstance(pd, (int, float)) else None,
        win_b=(pa / 100.0) if isinstance(pa, (int, float)) else None,
        odds_text=odds_text,
        tips=tips,
        note=(
            f"数据取自 KickForm / ThePuntersPage 后端统计接口"
            f"（fixture {raw.get('fixture_id')}）并按结构化字段整理生成。"
        ),
    )


# ─────────────────────────────────────────────
# Forebet 自动生成数据（按中文队名索引）
# ─────────────────────────────────────────────
_FOREBET_DB: dict[frozenset[str], dict] = {
    frozenset({r["home_cn"], r["away_cn"]}): r for r in FOREBET_RAW
}

_FB_SOURCE = "Forebet"


def _american_to_decimal(s) -> float | None:
    try:
        v = int(s)
    except (TypeError, ValueError):
        return None
    if v == 0:
        return None
    return round(1 + (100 / abs(v) if v < 0 else v / 100), 2)


def _forebet_to_prediction(raw: dict, team_a_name: str) -> ExternalPrediction:
    """把一条 Forebet 原始数据转成按当前比赛主客顺序对齐的预测。"""
    flip = team_a_name == raw["away_cn"]
    hcn = raw["away_cn"] if flip else raw["home_cn"]
    acn = raw["home_cn"] if flip else raw["away_cn"]
    ph = raw["p_away"] if flip else raw["p_home"]
    pa = raw["p_home"] if flip else raw["p_away"]
    pd = raw["p_draw"]

    sh, sa = raw.get("score_home"), raw.get("score_away")
    if flip:
        sh, sa = sa, sh
    score_pred = ""
    if isinstance(sh, int) and isinstance(sa, int):
        score_pred = f"{hcn} {sh} - {sa} {acn}"

    oh = _american_to_decimal(raw["odds_away"] if flip else raw["odds_home"])
    oa = _american_to_decimal(raw["odds_home"] if flip else raw["odds_away"])
    od = _american_to_decimal(raw["odds_draw"])
    odds_text = ""
    if oh and od and oa:
        odds_text = f"最佳赔率（欧赔）：{hcn} {oh}、平 {od}、{acn} {oa}"

    fav = _fav_phrase(hcn, acn, ph, pd, pa)
    summary = (
        f"Forebet 数学模型测算：{fav}。胜负概率为 {hcn} {_pct(ph)}、平局 {_pct(pd)}、"
        f"{acn} {_pct(pa)}"
    )
    if score_pred:
        summary += f"；最可能比分 {hcn} {sh}-{sa} {acn}。"
    else:
        summary += "。"

    tips = [f"胜负倾向：{fav}（{hcn} {_pct(ph)} · 平 {_pct(pd)} · {acn} {_pct(pa)}）"]
    if score_pred:
        tips.append(f"最可能比分：{sh}-{sa}")
    if isinstance(raw.get("avg_goals"), (int, float)):
        tips.append(f"模型场均总进球：约 {raw['avg_goals']} 球")
    if raw.get("venue"):
        tips.append(f"场地：{raw['venue']}")

    return ExternalPrediction(
        source=_FB_SOURCE,
        source_url=raw.get("url", ""),
        summary=summary,
        score_prediction=score_pred,
        win_a=(ph / 100.0) if isinstance(ph, (int, float)) else None,
        draw=(pd / 100.0) if isinstance(pd, (int, float)) else None,
        win_b=(pa / 100.0) if isinstance(pa, (int, float)) else None,
        odds_text=odds_text,
        tips=tips,
        note="数据取自 forebet.com 列表页解析生成（1X2 概率 / 预测比分 / 场均进球 / 赔率）。",
    )


# ─────────────────────────────────────────────
# Sports Mole 自动生成数据（按中文队名索引）
# ─────────────────────────────────────────────
# 来源：sportsmole.co.uk 预览页。仅含事实型结构化字段（比分预测 / 预测首发 /
# 近期战绩），由 scripts_gen_sportsmole.py 生成。其独有价值是**预测首发阵容**，
# 这是 KickForm / Forebet 两个来源都没有的信息。
_SPORTSMOLE_DB: dict[frozenset[str], dict] = {
    frozenset({r["home_cn"], r["away_cn"]}): r for r in SPORTSMOLE_RAW
}

_SM_SOURCE = "Sports Mole"
_FST_SOURCE = "FreeSuperTips"
_TA_SOURCE = "The Analyst（Opta 超算）"

_FORM_CN = {"W": "胜", "D": "平", "L": "负"}

_EN_FALLBACK_NOTE = "（暂为英文原文，完整中文翻译可后续补充；点此查看出处原文。）"


def _form_str(seq) -> str:
    if not seq:
        return ""
    return " ".join(_FORM_CN.get(x, x) for x in seq)


def _sm_english_blocks(raw: dict, flip: bool) -> list[tuple[str, str]]:
    """无中文译文时，用英文原文段落拼出可读的分析块。"""
    blocks: list[tuple[str, str]] = []
    intro = raw.get("intro_en") or []
    preview = raw.get("preview_en") or []
    news = raw.get("team_news_en") or []
    if intro:
        blocks.append(("Match context", "\n".join(intro)))
    if preview:
        blocks.append(("Match preview", "\n".join(preview)))
    if news:
        blocks.append(("Team news", "\n".join(news)))
    return blocks


def _sportsmole_to_prediction(raw: dict, team_a_name: str) -> ExternalPrediction:
    """把一条 Sports Mole 数据转成按当前比赛主客顺序对齐的预测。"""
    flip = team_a_name == raw["away_cn"]
    hcn = raw["away_cn"] if flip else raw["home_cn"]
    acn = raw["home_cn"] if flip else raw["away_cn"]

    sh, sa = raw.get("score_home"), raw.get("score_away")
    if flip:
        sh, sa = sa, sh
    lineup_h = raw.get("lineup_away") if flip else raw.get("lineup_home")
    lineup_a = raw.get("lineup_home") if flip else raw.get("lineup_away")
    form_h = raw.get("form_away") if flip else raw.get("form_home")
    form_a = raw.get("form_home") if flip else raw.get("form_away")

    score_pred = ""
    if isinstance(sh, int) and isinstance(sa, int):
        score_pred = f"{hcn} {sh} - {sa} {acn}"

    # 由比分推导倾向
    if isinstance(sh, int) and isinstance(sa, int):
        if sh > sa:
            verdict = f"看好{hcn}取胜"
        elif sa > sh:
            verdict = f"看好{acn}取胜"
        else:
            verdict = "预计双方战平"
    else:
        verdict = "给出了赛前预测"

    # 分析正文：优先中文译文，否则英文原文回退
    key = frozenset({raw["home_cn"], raw["away_cn"]})
    cn = SPORTSMOLE_CN.get(key)
    if cn:
        analysis = list(cn.get("blocks", []))
        analysis_lang = "zh"
        summary = cn.get("summary", "")
    else:
        analysis = _sm_english_blocks(raw, flip)
        analysis_lang = "en"
        summary = (
            f"Sports Mole 编辑赛前研判：{verdict}"
            + (f"，预测比分 {hcn} {sh}-{sa} {acn}。" if score_pred else "。")
            + "下方为英文原文分析（含赛前形势、前瞻与球队动态）。"
        )

    tips: list[str] = []
    if score_pred:
        tips.append(f"编辑比分预测：{score_pred}")
    if lineup_h:
        tips.append(f"预测首发（{hcn}）：{lineup_h}")
    if lineup_a:
        tips.append(f"预测首发（{acn}）：{lineup_a}")
    fh, fa = _form_str(form_h), _form_str(form_a)
    if fh:
        tips.append(f"近期战绩（{hcn}，全部赛事，由近及远）：{fh}")
    if fa:
        tips.append(f"近期战绩（{acn}，全部赛事，由近及远）：{fa}")

    note = (
        "比分预测、预测首发与近期战绩取自 Sports Mole 英文赛前预览，整理为结构化中文数据；"
        "分析正文为人工翻译（已就中文表达润色）。"
        if analysis_lang == "zh" else
        "数据取自 Sports Mole 英文赛前预览。" + _EN_FALLBACK_NOTE
    )

    return ExternalPrediction(
        source=_SM_SOURCE,
        source_url=raw.get("url", ""),
        summary=summary,
        score_prediction=score_pred,
        tips=tips,
        analysis=analysis,
        analysis_lang=analysis_lang,
        note=note,
    )


# ─────────────────────────────────────────────
# FreeSuperTips 自动生成数据（按中文队名索引）
# ─────────────────────────────────────────────
# 来源：freesupertips.com 预测页。其价值是**完整的赛前文字分析**（JSON-LD
# articleBody），由 scripts_gen_freesupertips.py 抓取生成；中文翻译见
# prediction_analysis_cn.FREESUPERTIPS_CN。
_FREESUPERTIPS_DB: dict[frozenset[str], dict] = {
    frozenset({r["home_cn"], r["away_cn"]}): r for r in FREESUPERTIPS_RAW
}


def _freesupertips_to_prediction(raw: dict, team_a_name: str) -> ExternalPrediction:
    """把一条 FreeSuperTips 数据转成预测（含完整分析正文）。"""
    hcn, acn = raw["home_cn"], raw["away_cn"]
    bullets = raw.get("bullets_en") or []

    key = frozenset({hcn, acn})
    cn = FREESUPERTIPS_CN.get(key)
    if cn:
        analysis = list(cn.get("blocks", []))
        analysis_lang = "zh"
        summary = cn.get("summary", "")
        note = (
            "完整赛前分析取自 FreeSuperTips，正文为人工翻译（已就中文表达润色）；"
            "文中比分 / 玩法倾向仅供参考。"
        )
    else:
        # 英文原文回退：用文章自带小标题切分正文
        body = raw.get("body_en") or []
        blocks: list[tuple[str, str]] = []
        cur_head, cur_buf = raw.get("section_title_en", "") or "", []
        for p in body:
            # 小标题：较短且不以句末标点结尾
            if len(p) < 90 and not p.rstrip().endswith((".", "!", "?", "…")):
                if cur_buf:
                    blocks.append((cur_head, "\n".join(cur_buf)))
                    cur_buf = []
                cur_head = p
            else:
                cur_buf.append(p)
        if cur_buf:
            blocks.append((cur_head, "\n".join(cur_buf)))
        analysis = blocks
        analysis_lang = "en"
        summary = "FreeSuperTips 完整赛前分析（下方为英文原文）。"
        note = "数据取自 freesupertips.com。" + _EN_FALLBACK_NOTE

    tips = [f"分析要点：{b}" for b in bullets]

    return ExternalPrediction(
        source=_FST_SOURCE,
        source_url=raw.get("url", ""),
        summary=summary,
        tips=tips,
        analysis=analysis,
        analysis_lang=analysis_lang,
        note=note,
    )


# ─────────────────────────────────────────────
# The Analyst（Opta 超级计算机）赛前预测
# ─────────────────────────────────────────────
def _theanalyst_to_prediction(match: Match):
    """把 The Analyst（Opta 超算）赛前模拟转成一份 :class:`ExternalPrediction`。

    含 25,000 次赛前模拟的胜 / 平 / 负概率（齐全时渲染概率条）、关键事实
    （Key Insights）与预测正文（英文原文）。无命中返回 ``None``。
    """
    pv = get_match_preview(match)
    if pv is None:
        return None
    hcn, acn = pv.home_cn, pv.away_cn

    # 胜平负概率：三者齐全才传给概率条（避免误导），否则只在综述里点名热门胜率。
    if pv.home_pct is not None and pv.draw_pct is not None and pv.away_pct is not None:
        win_a = pv.home_pct / 100.0
        draw = pv.draw_pct / 100.0
        win_b = pv.away_pct / 100.0
    else:
        win_a = draw = win_b = None

    def _fav_phrase() -> str:
        pairs = [(hcn, pv.home_pct), (acn, pv.away_pct)]
        named = [(n, p) for n, p in pairs if p is not None]
        if not named:
            return "Opta 超算给出赛前模拟概率"
        top = max(named, key=lambda x: x[1])
        return f"Opta 超算看好{top[0]}（取胜概率 {top[1]:.1f}%）"

    bits = []
    if pv.home_pct is not None:
        bits.append(f"{hcn} {pv.home_pct:.1f}%")
    if pv.draw_pct is not None:
        bits.append(f"平 {pv.draw_pct:.1f}%")
    if pv.away_pct is not None:
        bits.append(f"{acn} {pv.away_pct:.1f}%")
    prob_line = "　胜平负模拟：" + " · ".join(bits) if bits else ""
    # 综述：优先用整篇分析的中文综述，回退到「热门 + 胜率」一句话。
    summary = (pv.summary_cn or f"{_fav_phrase()}。") + prob_line

    # 分析正文：整篇文章的中文译文（关键数据 / 深度分析 / 历史交锋 / 赛前预测）。
    analysis = [(title, body) for title, body in pv.analysis_cn if body]
    if not analysis and pv.prediction:
        analysis = [("Opta 超算赛前研判（英文原文）", pv.prediction)]
    has_zh = bool(pv.analysis_cn)
    tips = [] if has_zh else [f"关键事实：{s}" for s in pv.insights]

    return ExternalPrediction(
        source=_TA_SOURCE,
        source_url=pv.url,
        summary=summary,
        win_a=win_a,
        draw=draw,
        win_b=win_b,
        tips=tips,
        analysis=analysis,
        analysis_lang="zh" if has_zh else ("en" if pv.prediction else "zh"),
        note=(
            "数据取自 The Analyst（Opta 超级计算机），基于 25,000 次赛前模拟；"
            "胜平负概率与关键事实为模型实测，分析正文为官网英文原文的中文翻译"
            "（机器翻译，仅供参考）。"
        ),
    )


# ─────────────────────────────────────────────
# 查询入口
# ─────────────────────────────────────────────
def get_external_predictions(match: Match) -> list[ExternalPrediction]:
    """按参赛双方名字匹配外部来源预测（无视主客顺序）。

    合并五类来源：
      1. ``_EXTERNAL_DB`` —— 人工整理（Squawka / 精修版 KickForm）；
      2. ``_KICKFORM_DB`` —— 后端接口自动生成的 KickForm 预测（32 场）；
      3. ``_FOREBET_DB`` —— Forebet 列表页解析生成的预测（约 31 场）；
      4. ``_SPORTSMOLE_DB`` —— Sports Mole 预览页解析生成（比分预测 / 预测首发 /
         近期战绩 + 长篇分析，随赛程刷新）；
      5. ``_FREESUPERTIPS_DB`` —— FreeSuperTips 预测页解析生成（完整赛前分析）。
    按来源名去重；带长篇分析的来源（Sports Mole / FreeSuperTips）排在前面。
    所有自动来源都会按当前比赛主客顺序自动校正左右两栏。
    """
    key = frozenset({match.team_a_name, match.team_b_name})
    curated = list(_EXTERNAL_DB.get(key, []))
    present = {ep.source for ep in curated}
    result = list(curated)

    raw_kf = _KICKFORM_DB.get(key)
    if raw_kf is not None and _KF_SOURCE not in present:
        result.append(_raw_to_prediction(raw_kf, match.team_a_name))

    raw_fb = _FOREBET_DB.get(key)
    if raw_fb is not None and _FB_SOURCE not in present:
        result.append(_forebet_to_prediction(raw_fb, match.team_a_name))

    raw_sm = _SPORTSMOLE_DB.get(key)
    if raw_sm is not None and _SM_SOURCE not in present:
        result.append(_sportsmole_to_prediction(raw_sm, match.team_a_name))

    raw_fst = _FREESUPERTIPS_DB.get(key)
    if raw_fst is not None and _FST_SOURCE not in present:
        result.append(_freesupertips_to_prediction(raw_fst, match.team_a_name))

    # The Analyst（Opta 超级计算机）—— 实时同源的赛前模拟概率 + 关键事实
    if _TA_SOURCE not in present:
        ta = _theanalyst_to_prediction(match)
        if ta is not None:
            result.append(ta)

    # 排序：有长篇分析（Sports Mole / FreeSuperTips）的来源优先靠前展示
    _order = {_SM_SOURCE: 0, _FST_SOURCE: 1, _TA_SOURCE: 2}
    result.sort(key=lambda ep: _order.get(ep.source, 9))
    return result


def get_team_stats(match: Match) -> TeamStats | None:
    """按参赛双方名字匹配 Forebet 球队数据对比（无视主客顺序）。无则返回 None。

    若命中条目里的主客顺序与本场相反，会自动翻转左右两栏以对齐当前比赛。
    """
    key = frozenset({match.team_a_name, match.team_b_name})
    stats = _TEAM_STATS_DB.get(key)
    if stats is None:
        return None
    if stats.team_a == match.team_a_name:
        return stats
    # 顺序相反 → 翻转左右栏，保证主队始终在左
    return TeamStats(
        team_a=stats.team_b,
        team_b=stats.team_a,
        source=stats.source,
        source_url=stats.source_url,
        scope=stats.scope,
        note=stats.note,
        rows=[
            StatRow(r.label, r.b_value, r.a_value, r.b_sub, r.a_sub)
            for r in stats.rows
        ],
    )


def orient_to_match(pred: ExternalPrediction, match: Match) -> ExternalPrediction:
    """占位：若未来按主客顺序存储概率，可在此做翻转对齐。当前直接返回。"""
    return pred
