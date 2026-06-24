"""charts —— 动画图表系统（WorldCup 3.0）。

广播风的雷达 / 折线 / 柱状图，共享同一条「揭示进度」0→1 动画
（``CHART_REFRESH_MS = 300`` / OutCubic）；落定时几何精确等于输入数据。

* :class:`RadarChart` —— 顶点从中心生长到数值。
* :class:`LineChart`  —— 折线从左到右渐进绘出。
* :class:`BarChart`   —— 柱子高度生长。

数值数学（揭示插值 / 各图几何映射）均为无 GUI 依赖的纯函数，见各模块及
:mod:`app.ui.widgets.charts.base`（设计 Property 20）。
"""
from __future__ import annotations

from app.ui.widgets.charts.bar import BarChart
from app.ui.widgets.charts.base import BaseChart, CHART_REFRESH_MS
from app.ui.widgets.charts.line import LineChart
from app.ui.widgets.charts.radar import RadarChart

__all__ = [
    "BaseChart",
    "CHART_REFRESH_MS",
    "RadarChart",
    "LineChart",
    "BarChart",
]
