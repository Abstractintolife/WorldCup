"""盘口分析模块（纯计算）。

由「赛前预测引擎」给出的两队预期进球（exp_goals_a / exp_goals_b）出发，
构建 **泊松比分概率矩阵**，再从同一个矩阵一致地推导出各类盘口结果：

* 全场让球结果（亚洲让球 / Asian Handicap）
* 全场大小结果（Over / Under 总进球）
* 全场独赢结果（1X2 胜平负）
* 全场总进球数（0-1 / 2-3 / 4-6 / 7+ 区间）
* 全场比分单双（总进球数为单 / 为双）
* 半场 / 全场结果（HT/FT 九宫格）
* 正确比分（最可能的若干个准确比分）

为保证与预测页其它卡片（胜负概率、预期进球）**口径一致**，本模块会先用
一维搜索微调两队 λ，使泊松模型推出的 1X2 尽量贴合引擎给出的 win_a / win_b，
同时维持引擎预计的总进球数。所有结果对每一场比赛都可计算，无需外部数据。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.services.prediction import MatchPrediction

# 全场进球上限（矩阵规模）与半场首/次比例
_MAXG = 10
_HALF_FRAC = 0.45  # 上半场进球占比的常用经验值


# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────
@dataclass
class MarketLine:
    label: str
    prob: float
    highlight: bool = False


@dataclass
class MarketGroup:
    title: str
    pick: str
    lines: list[MarketLine] = field(default_factory=list)
    note: str = ""


@dataclass
class MatchMarkets:
    exp_a: float
    exp_b: float
    handicap_line: float
    groups: list[MarketGroup] = field(default_factory=list)


# ─────────────────────────────────────────────
# 泊松工具
# ─────────────────────────────────────────────
def _pois(k: int, lam: float) -> float:
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def _pmf(lam: float, n: int) -> list[float]:
    return [_pois(k, lam) for k in range(n + 1)]


def _score_matrix(la: float, lb: float, n: int) -> list[list[float]]:
    pa, pb = _pmf(la, n), _pmf(lb, n)
    return [[pa[i] * pb[j] for j in range(n + 1)] for i in range(n + 1)]


def _wdl(mat: list[list[float]]) -> tuple[float, float, float]:
    """由比分矩阵得 (主胜, 平, 客胜)。"""
    n = len(mat)
    home = sum(mat[i][j] for i in range(n) for j in range(n) if i > j)
    draw = sum(mat[i][i] for i in range(n))
    away = sum(mat[i][j] for i in range(n) for j in range(n) if i < j)
    return home, draw, away


def _calibrate_lambdas(pred: MatchPrediction) -> tuple[float, float]:
    """微调 λ：保持引擎预计总进球，使泊松 1X2 贴合 win_a/win_b。"""
    total = max(0.6, pred.exp_goals_a + pred.exp_goals_b)
    target_home, target_away = pred.win_a, pred.win_b
    best_d, best_err = 0.0, 1e9
    # d 为「主队净 λ 优势」的一半，搜索 -total/2..total/2
    steps = 120
    lo, hi = -total / 2 + 0.05, total / 2 - 0.05
    for s in range(steps + 1):
        d = lo + (hi - lo) * s / steps
        la, lb = total / 2 + d, total / 2 - d
        if la <= 0.05 or lb <= 0.05:
            continue
        h, _, a = _wdl(_score_matrix(la, lb, _MAXG))
        err = abs(h - target_home) + abs(a - target_away)
        if err < best_err:
            best_err, best_d = err, d
    return total / 2 + best_d, total / 2 - best_d


# ─────────────────────────────────────────────
# 各盘口
# ─────────────────────────────────────────────
def _g_result(a: str, b: str, mat) -> MarketGroup:
    h, d, aw = _wdl(mat)
    opts = [(f"{a} 胜", h), ("平局", d), (f"{b} 胜", aw)]
    top = max(opts, key=lambda x: x[1])
    return MarketGroup(
        title="全场独赢结果（胜平负）",
        pick=top[0],
        lines=[MarketLine(lbl, p, lbl == top[0]) for lbl, p in opts],
    )


def _g_overunder(mat) -> MarketGroup:
    n = len(mat)
    totals = [0.0] * (2 * n)
    for i in range(n):
        for j in range(n):
            totals[i + j] += mat[i][j]
    lines: list[MarketLine] = []
    best_lbl, best_gap = "", 1.0
    for line in (1.5, 2.5, 3.5, 4.5):
        over = sum(totals[k] for k in range(len(totals)) if k > line)
        lines.append(MarketLine(f"大于 {line}", over))
        lines.append(MarketLine(f"小于 {line}", 1 - over))
        gap = abs(over - 0.5)
        if gap < best_gap:
            best_gap, best_lbl = gap, (f"大于 {line}" if over >= 0.5 else f"小于 {line}")
    for ln in lines:
        ln.highlight = ln.label == best_lbl
    return MarketGroup(title="全场大小结果（总进球）", pick=best_lbl, lines=lines)


def _g_handicap(a: str, b: str, la: float, lb: float, mat) -> tuple[MarketGroup, float]:
    n = len(mat)
    fav_is_a = la >= lb
    fav, dog = (a, b) if fav_is_a else (b, a)
    # 让球净胜分布（让方视角）：margin = fav_goals - dog_goals
    margin: dict[int, float] = {}
    for i in range(n):
        for j in range(n):
            m = (i - j) if fav_is_a else (j - i)
            margin[m] = margin.get(m, 0.0) + mat[i][j]
    exp_margin = abs(la - lb)
    line = max(0.5, round(exp_margin - 0.5) + 0.5)  # 最接近期望净胜的 .5 让球线

    lines: list[MarketLine] = []
    pick_lbl = ""
    for h in sorted({0.5, line, line + 1.0}):
        need = math.ceil(h)  # 让 -h，需净胜 >= need
        cover = sum(p for m, p in margin.items() if m >= need)
        lbl = f"{fav} -{h} / {dog} +{h}"
        ln = MarketLine(f"{lbl}：{fav}赢盘", cover)
        lines.append(ln)
        if abs(h - line) < 1e-6:
            pick_lbl = f"{fav} -{h} / {dog} +{h}"
            ln.highlight = True
    grp = MarketGroup(
        title="全场让球结果（亚洲盘）",
        pick=pick_lbl,
        lines=lines,
        note=f"主让盘口以模型期望净胜（约 {exp_margin:.1f} 球）取最接近的 .5 线。",
    )
    return grp, line


def _g_bands(mat) -> MarketGroup:
    n = len(mat)
    totals = [0.0] * (2 * n)
    for i in range(n):
        for j in range(n):
            totals[i + j] += mat[i][j]
    bands = [
        ("0-1 球", sum(totals[k] for k in range(0, 2))),
        ("2-3 球", sum(totals[k] for k in range(2, 4))),
        ("4-6 球", sum(totals[k] for k in range(4, 7))),
        ("7 球或更多", sum(totals[k] for k in range(7, len(totals)))),
    ]
    top = max(bands, key=lambda x: x[1])
    return MarketGroup(
        title="全场总进球数（区间）",
        pick=top[0],
        lines=[MarketLine(lbl, p, lbl == top[0]) for lbl, p in bands],
    )


def _g_oddeven(mat) -> MarketGroup:
    n = len(mat)
    odd = sum(mat[i][j] for i in range(n) for j in range(n) if (i + j) % 2 == 1)
    even = 1 - odd
    pick = "比分为单" if odd >= even else "比分为双"
    return MarketGroup(
        title="全场比分单双",
        pick=pick,
        lines=[
            MarketLine("比分为单（总进球为奇数）", odd, pick.endswith("单")),
            MarketLine("比分为双（总进球为偶数，含 0）", even, pick.endswith("双")),
        ],
    )


def _g_htft(a: str, b: str, la: float, lb: float) -> MarketGroup:
    """半场/全场九宫格：上下半场各自独立泊松，合成联合分布。"""
    nh = 8
    la1, lb1 = la * _HALF_FRAC, lb * _HALF_FRAC
    la2, lb2 = la * (1 - _HALF_FRAC), lb * (1 - _HALF_FRAC)
    h1 = _score_matrix(la1, lb1, nh)
    h2 = _score_matrix(la2, lb2, nh)

    def res(i: int, j: int) -> str:
        return a if i > j else (b if i < j else "和")

    joint: dict[tuple[str, str], float] = {}
    for i1 in range(nh + 1):
        for j1 in range(nh + 1):
            p1 = h1[i1][j1]
            if p1 < 1e-9:
                continue
            ht = res(i1, j1)
            for i2 in range(nh + 1):
                for j2 in range(nh + 1):
                    p2 = h2[i2][j2]
                    if p2 < 1e-9:
                        continue
                    ft = res(i1 + i2, j1 + j2)
                    joint[(ht, ft)] = joint.get((ht, ft), 0.0) + p1 * p2

    order = [a, "和", b]
    lines = [
        MarketLine(f"{ht} / {ft}", joint.get((ht, ft), 0.0))
        for ht in order for ft in order
    ]
    top = max(lines, key=lambda x: x.prob)
    top.highlight = True
    return MarketGroup(
        title="半场 / 全场结果",
        pick=top.label,
        lines=lines,
        note="顺序为「半场结果 / 全场结果」，「和」表示半场或全场打平。",
    )


def _g_correct_score(a: str, b: str, mat, top_n: int = 10) -> MarketGroup:
    n = len(mat)
    scores = [((i, j), mat[i][j]) for i in range(n) for j in range(n)]
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_n]
    best = top[0][0]
    lines = [
        MarketLine(f"{i} - {j}", p, (i, j) == best)
        for (i, j), p in top
    ]
    return MarketGroup(
        title="正确比分（最可能）",
        pick=f"{best[0]} - {best[1]}",
        lines=lines,
        note=f"比分以 {a}（左）- {b}（右）为序，列出概率最高的 {top_n} 个。",
    )


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────
def build_markets(pred: MatchPrediction) -> MatchMarkets:
    a, b = pred.match.team_a_name, pred.match.team_b_name
    la, lb = _calibrate_lambdas(pred)
    mat = _score_matrix(la, lb, _MAXG)

    handicap_grp, line = _g_handicap(a, b, la, lb, mat)
    groups = [
        handicap_grp,
        _g_overunder(mat),
        _g_result(a, b, mat),
        _g_bands(mat),
        _g_oddeven(mat),
        _g_htft(a, b, la, lb),
        _g_correct_score(a, b, mat),
    ]
    return MatchMarkets(exp_a=la, exp_b=lb, handicap_line=line, groups=groups)
