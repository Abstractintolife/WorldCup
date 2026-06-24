"""自动生成：The Analyst（Opta）夺冠概率 + 逐场赛前预测快照。

请勿手工编辑。由 scripts_gen_theanalyst.py 抓取 theanalyst.com / Opta
（api.performfeeds.com 赛事模拟接口 + 预览文章）生成。
数据来源：theanalyst.com（Opta 超级计算机，25,000 次赛前模拟）。
"""

null = None  # 兼容缺失值

THEANALYST_TOURNAMENT = [
    {
        "team_en": "Argentina",
        "team_cn": "阿根廷",
        "code": "ARG",
        "group": "Group J",
        "win_pct": 15.46,
        "final_pct": 26.73,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "France",
        "team_cn": "法国",
        "code": "FRA",
        "group": "Group I",
        "win_pct": 15.06,
        "final_pct": 24.06,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Spain",
        "team_cn": "西班牙",
        "code": "ESP",
        "group": "Group H",
        "win_pct": 12.48,
        "final_pct": 21.22,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "England",
        "team_cn": "英格兰",
        "code": "ENG",
        "group": "Group L",
        "win_pct": 9.48,
        "final_pct": 17.04,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Portugal",
        "team_cn": "葡萄牙",
        "code": "POR",
        "group": "Group K",
        "win_pct": 6.71,
        "final_pct": 12.81,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Germany",
        "team_cn": "德国",
        "code": "GER",
        "group": "Group E",
        "win_pct": 6.6,
        "final_pct": 12.69,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Norway",
        "team_cn": "挪威",
        "code": "NOR",
        "group": "Group I",
        "win_pct": 5.42,
        "final_pct": 11.5,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Brazil",
        "team_cn": "巴西",
        "code": "BRA",
        "group": "Group C",
        "win_pct": 4.56,
        "final_pct": 9.58,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Netherlands",
        "team_cn": "荷兰",
        "code": "NED",
        "group": "Group F",
        "win_pct": 4.26,
        "final_pct": 8.54,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "United States",
        "team_cn": "美国",
        "code": "USA",
        "group": "Group D",
        "win_pct": 4.07,
        "final_pct": 9.14,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Colombia",
        "team_cn": "哥伦比亚",
        "code": "COL",
        "group": "Group K",
        "win_pct": 2.56,
        "final_pct": 6.4,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Switzerland",
        "team_cn": "瑞士",
        "code": "SUI",
        "group": "Group B",
        "win_pct": 1.74,
        "final_pct": 4.32,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Morocco",
        "team_cn": "摩洛哥",
        "code": "MAR",
        "group": "Group C",
        "win_pct": 1.73,
        "final_pct": 4.39,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Japan",
        "team_cn": "日本",
        "code": "JPN",
        "group": "Group F",
        "win_pct": 1.64,
        "final_pct": 4.12,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Mexico",
        "team_cn": "墨西哥",
        "code": "MEX",
        "group": "Group A",
        "win_pct": 1.57,
        "final_pct": 4.36,
        "points": 6,
        "played": 2
    },
    {
        "team_en": "Belgium",
        "team_cn": "比利时",
        "code": "BEL",
        "group": "Group G",
        "win_pct": 1.22,
        "final_pct": 3.65,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Belgium",
        "team_cn": "比利时",
        "code": "BEL",
        "group": "3rd Place Ranking",
        "win_pct": 1.22,
        "final_pct": 3.65,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Croatia",
        "team_cn": "克罗地亚",
        "code": "CRO",
        "group": "Group L",
        "win_pct": 0.88,
        "final_pct": 2.52,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Croatia",
        "team_cn": "克罗地亚",
        "code": "CRO",
        "group": "3rd Place Ranking",
        "win_pct": 0.88,
        "final_pct": 2.52,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Canada",
        "team_cn": "加拿大",
        "code": "CAN",
        "group": "Group B",
        "win_pct": 0.64,
        "final_pct": 2.45,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Egypt",
        "team_cn": "埃及",
        "code": "EGY",
        "group": "Group G",
        "win_pct": 0.5,
        "final_pct": 1.92,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Uruguay",
        "team_cn": "乌拉圭",
        "code": "URU",
        "group": "Group H",
        "win_pct": 0.42,
        "final_pct": 1.12,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Austria",
        "team_cn": "奥地利",
        "code": "AUT",
        "group": "Group J",
        "win_pct": 0.42,
        "final_pct": 1.37,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Sweden",
        "team_cn": "瑞典",
        "code": "SWE",
        "group": "Group F",
        "win_pct": 0.38,
        "final_pct": 1.24,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Sweden",
        "team_cn": "瑞典",
        "code": "SWE",
        "group": "3rd Place Ranking",
        "win_pct": 0.38,
        "final_pct": 1.24,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Ghana",
        "team_cn": "加纳",
        "code": "GHA",
        "group": "Group L",
        "win_pct": 0.31,
        "final_pct": 1.23,
        "points": 4,
        "played": 2
    },
    {
        "team_en": "Australia",
        "team_cn": "澳大利亚",
        "code": "AUS",
        "group": "Group D",
        "win_pct": 0.27,
        "final_pct": 0.94,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Senegal",
        "team_cn": "塞内加尔",
        "code": "SEN",
        "group": "Group I",
        "win_pct": 0.23,
        "final_pct": 0.9,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Senegal",
        "team_cn": "塞内加尔",
        "code": "SEN",
        "group": "3rd Place Ranking",
        "win_pct": 0.23,
        "final_pct": 0.9,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Paraguay",
        "team_cn": "巴拉圭",
        "code": "PAR",
        "group": "Group D",
        "win_pct": 0.22,
        "final_pct": 0.9,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Paraguay",
        "team_cn": "巴拉圭",
        "code": "PAR",
        "group": "3rd Place Ranking",
        "win_pct": 0.22,
        "final_pct": 0.9,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "IR Iran",
        "team_cn": "IR Iran",
        "code": "IRN",
        "group": "Group G",
        "win_pct": 0.21,
        "final_pct": 0.64,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Korea Republic",
        "team_cn": "韩国",
        "code": "KOR",
        "group": "Group A",
        "win_pct": 0.2,
        "final_pct": 0.78,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Côte d'Ivoire",
        "team_cn": "Côte d'Ivoire",
        "code": "CIV",
        "group": "Group E",
        "win_pct": 0.18,
        "final_pct": 0.63,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Algeria",
        "team_cn": "阿尔及利亚",
        "code": "ALG",
        "group": "Group J",
        "win_pct": 0.16,
        "final_pct": 0.72,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Algeria",
        "team_cn": "阿尔及利亚",
        "code": "ALG",
        "group": "3rd Place Ranking",
        "win_pct": 0.16,
        "final_pct": 0.72,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Scotland",
        "team_cn": "苏格兰",
        "code": "SCO",
        "group": "Group C",
        "win_pct": 0.14,
        "final_pct": 0.54,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Scotland",
        "team_cn": "苏格兰",
        "code": "SCO",
        "group": "3rd Place Ranking",
        "win_pct": 0.14,
        "final_pct": 0.54,
        "points": 3,
        "played": 2
    },
    {
        "team_en": "Ecuador",
        "team_cn": "厄瓜多尔",
        "code": "ECU",
        "group": "Group E",
        "win_pct": 0.13,
        "final_pct": 0.41,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Ecuador",
        "team_cn": "厄瓜多尔",
        "code": "ECU",
        "group": "3rd Place Ranking",
        "win_pct": 0.13,
        "final_pct": 0.41,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Bosnia-Herzegovina",
        "team_cn": "波黑",
        "code": "BIH",
        "group": "Group B",
        "win_pct": 0.07,
        "final_pct": 0.36,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Bosnia-Herzegovina",
        "team_cn": "波黑",
        "code": "BIH",
        "group": "3rd Place Ranking",
        "win_pct": 0.07,
        "final_pct": 0.36,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Cabo Verde",
        "team_cn": "Cabo Verde",
        "code": "CPV",
        "group": "Group H",
        "win_pct": 0.04,
        "final_pct": 0.18,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Cabo Verde",
        "team_cn": "Cabo Verde",
        "code": "CPV",
        "group": "3rd Place Ranking",
        "win_pct": 0.04,
        "final_pct": 0.18,
        "points": 2,
        "played": 2
    },
    {
        "team_en": "Congo DR",
        "team_cn": "Congo DR",
        "code": "COD",
        "group": "Group K",
        "win_pct": 0.02,
        "final_pct": 0.13,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Congo DR",
        "team_cn": "Congo DR",
        "code": "COD",
        "group": "3rd Place Ranking",
        "win_pct": 0.02,
        "final_pct": 0.13,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Czechia",
        "team_cn": "捷克",
        "code": "CZE",
        "group": "Group A",
        "win_pct": 0.01,
        "final_pct": 0.18,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Qatar",
        "team_cn": "卡塔尔",
        "code": "QAT",
        "group": "Group B",
        "win_pct": 0.01,
        "final_pct": 0.02,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Saudi Arabia",
        "team_cn": "沙特阿拉伯",
        "code": "KSA",
        "group": "Group H",
        "win_pct": 0.01,
        "final_pct": 0.14,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Czechia",
        "team_cn": "捷克",
        "code": "CZE",
        "group": "3rd Place Ranking",
        "win_pct": 0.01,
        "final_pct": 0.18,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "South Africa",
        "team_cn": "南非",
        "code": "RSA",
        "group": "Group A",
        "win_pct": 0.0,
        "final_pct": 0.06,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Haiti",
        "team_cn": "海地",
        "code": "HAI",
        "group": "Group C",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Türkiye",
        "team_cn": "土耳其",
        "code": "TUR",
        "group": "Group D",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Curaçao",
        "team_cn": "库拉索",
        "code": "CUW",
        "group": "Group E",
        "win_pct": 0.0,
        "final_pct": 0.01,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Tunisia",
        "team_cn": "突尼斯",
        "code": "TUN",
        "group": "Group F",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "New Zealand",
        "team_cn": "新西兰",
        "code": "NZL",
        "group": "Group G",
        "win_pct": 0.0,
        "final_pct": 0.02,
        "points": 1,
        "played": 2
    },
    {
        "team_en": "Iraq",
        "team_cn": "伊拉克",
        "code": "IRQ",
        "group": "Group I",
        "win_pct": 0.0,
        "final_pct": 0.01,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Jordan",
        "team_cn": "约旦",
        "code": "JOR",
        "group": "Group J",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Uzbekistan",
        "team_cn": "乌兹别克斯坦",
        "code": "UZB",
        "group": "Group K",
        "win_pct": 0.0,
        "final_pct": 0.01,
        "points": 0,
        "played": 2
    },
    {
        "team_en": "Panama",
        "team_cn": "巴拿马",
        "code": "PAN",
        "group": "Group L",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 2
    }
]

THEANALYST_MATCHES = [
    {
        "slug": "turkiye-vs-usa-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/turkiye-vs-usa-prediction-world-cup-2026-match-preview",
        "home_en": "Türkiye",
        "away_en": "USA",
        "home_cn": "土耳其",
        "away_cn": "美国",
        "home_pct": 47.7,
        "draw_pct": 23.0,
        "away_pct": 29.3,
        "insights": [
            "The Opta supercomputer expects the USA to finish their Group D campaign on the front foot, with Mauricio Pochettino’s side winning 47.7% of the pre-match simulations.",
            "USA have won back-to-back World Cup matches for the first time since the very first pair of games they played in the competition (against Belgium and Paraguay) in 1930. They have never won three in a row at the tournament.",
            "Türkiye have two losses from two at this World Cup, yet have never lost three games in a row in the competition. They were also kept goalless by both Australia and Paraguay, having only failed to score in one of their previous 10 World Cup matches."
        ],
        "prediction": "From 25,000 match simulations, Pochettino’s charges are given a healthy win probability of 47.7%. Despite their dismal showing so far, a Türkiye victory isn’t seen as too big of a stretch, with Montella’s side given a 29.3% win rating, just ahead of a draw at exactly 23.0% probability."
    },
    {
        "slug": "paraguay-vs-australia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/paraguay-vs-australia-prediction-world-cup-2026-match-preview",
        "home_en": "Paraguay",
        "away_en": "Australia",
        "home_cn": "巴拉圭",
        "away_cn": "澳大利亚",
        "home_pct": 38.0,
        "draw_pct": 38.6,
        "away_pct": 23.4,
        "insights": [
            "Paraguay are unbeaten in their previous six FIFA World Cup group games played on matchday three (W3 D3), and are Opta’s favourites to extend that streak with victory here at 38.0%.",
            "Australia are unbeaten in their five meetings with Paraguay in all competitions (W2 D3).",
            "However, the Socceroos have never beaten a CONMEBOL nation at the World Cup (D1 L4)."
        ],
        "prediction": "The Opta supercomputer marginally favours a Paraguay victory, with Alfaro’s side having won 38.0% of the 25,000 pre-match simulations. Australia’s chances of claiming three points are rated at 23.4%, with a draw – which would also secure second place in Group D – at 38.6%."
    },
    {
        "slug": "tunisia-vs-netherlands-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/tunisia-vs-netherlands-prediction-world-cup-2026-match-preview",
        "home_en": "Tunisia",
        "away_en": "Netherlands",
        "home_cn": "突尼斯",
        "away_cn": "荷兰",
        "home_pct": 5.2,
        "draw_pct": 11.8,
        "away_pct": 83.0,
        "insights": [
            "After swatting aside Sweden, the Netherlands have an 83.0% chance of posting consecutive wins according to the Opta Supercomputer.",
            "Following 25,000 pre-match simulations, Tunisia emerged with just a 5.2% chance of success in Kansas City.",
            "Outside penalty shootouts, Oranje are unbeaten across 14 World Cup games since losing to Spain in the 2010 final (W9 D5) – that’s the longest streak in the tournament’s history."
        ],
        "prediction": "The Opta supercomputer’s 25,000 pre-match simulations calculated an 83% chance of success for the Netherlands. Tunisia have a mere 5.2% chance of leaving this World Cup with a win, while the draw is rated at 11.8%."
    },
    {
        "slug": "ecuador-vs-germany-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/ecuador-vs-germany-prediction-world-cup-2026-match-preview",
        "home_en": "Ecuador",
        "away_en": "Germany",
        "home_cn": "厄瓜多尔",
        "away_cn": "德国",
        "home_pct": 28.2,
        "draw_pct": null,
        "away_pct": 48.8,
        "insights": [
            "Germany are considered favourites by the Opta supercomputer for this fixture, with a win probability of 48.8% to Ecuador’s 28.2%.",
            "Deniz Undav is averaging a goal or assist every 11 minutes at this World Cup.",
            "Ecuador had 16 shots on target without scoring in their opening two games of the tournament."
        ],
        "prediction": ""
    },
    {
        "slug": "japan-vs-sweden-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/japan-vs-sweden-prediction-world-cup-2026-match-preview",
        "home_en": "Japan",
        "away_en": "Sweden",
        "home_cn": "日本",
        "away_cn": "瑞典",
        "home_pct": 51.9,
        "draw_pct": null,
        "away_pct": 22.2,
        "insights": [
            "Japan go into this clash as favourites, according to the Opta supercomputer, winning 51.9% of simulations compared to Sweden ‘s 22.2%.",
            "Friday’s contest in Dallas will be Japan and Sweden’s first meeting at the World Cup.",
            "Following a draw with the Netherlands and a win over Tunisia, Japan have a chance to go through the group stage of a World Cup unbeaten for only the second time, after first doing so as co-hosts in 2002."
        ],
        "prediction": "The Opta supercomputer gives both Japan and the Netherlands a 100% chance of progressing to the round of 32, while Sweden are assigned a 91.9% probability as Group F’s top three sides look set to advance."
    },
    {
        "slug": "curacao-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/curacao-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "home_en": "Curaçao",
        "away_en": "Ivory Coast",
        "home_cn": "库拉索",
        "away_cn": "科特迪瓦",
        "home_pct": 7.6,
        "draw_pct": 10.1,
        "away_pct": 82.2,
        "insights": [
            "Ivory Coast overcame Curaçao in a huge 82.2% of 25,000 pre-match simulations by the Opta supercomputer.",
            "Curaçao could become the lowest-ranked side in history to reach the knockout stages at the World Cup.",
            "Ivory Coast are hoping to reach the World Cup knockout stages for the first time ever."
        ],
        "prediction": "The Opta supercomputer struggled to see anything other than a win for Ivory Coast, who came out on top in a massive 82.2% of 25,000 pre-match simulations. Curaçao were afforded just a 7.6% chance of victory, with the draw accounting for 10.1% of the data-led simulations."
    },
    {
        "slug": "scotland-vs-brazil-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/scotland-vs-brazil-prediction-world-cup-2026-match-preview",
        "home_en": "Scotland",
        "away_en": "Brazil",
        "home_cn": "苏格兰",
        "away_cn": "巴西",
        "home_pct": 12.2,
        "draw_pct": 18.2,
        "away_pct": 69.6,
        "insights": [
            "According to the Opta supercomputer, Brazil will stride through to the knockout phase – they have a 69.6% chance of victory.",
            "With just a 12.2% chance of finally beating the Brazilians, Scotland can assume their preferred role as underdogs.",
            "Brazil are the team Scotland have faced most without ever winning (P10 D2 L8)."
        ],
        "prediction": "The Opta supercomputer’s 25,000 pre-match simulations established Brazil as clear favourites, with a 69.6% chance of success. Scotland only have a modest 12.2% chance of claiming victory, with the draw rated at 18.2%."
    },
    {
        "slug": "morocco-vs-haiti-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/morocco-vs-haiti-prediction-world-cup-2026-match-preview",
        "home_en": "Morocco",
        "away_en": "Haiti",
        "home_cn": "摩洛哥",
        "away_cn": "海地",
        "home_pct": 81.0,
        "draw_pct": 12.3,
        "away_pct": 6.8,
        "insights": [
            "The Opta supercomputer views Morocco as massive favourites to win this game, with Mohamed Ouahbi’s side coming out on top in 81.0% of the 25,000 pre-match simulations.",
            "Morocco have won three of their last four group games at the World Cup, more than they’d managed across their first 16 attempts in this phase of the tournament (two wins).",
            "Haiti have lost all five games they’ve played in their two World Cup appearances, conceding 18 goals and scoring just twice. Only El Salvador (six) have played more games at the tournament and maintained a 100% loss rate."
        ],
        "prediction": "From 25,000 pre-match simulations, Morocco emerged victorious in 81.0% of the outcomes, suggesting they will be comfortable favourites in Atlanta. Haiti are given little margin for error with a mere 6.8% chance of victory, but with a draw standing at 12.3% likelihood, Les Grenadiers will do all they can to create history and avoid a sixth straight World Cup defeat."
    },
    {
        "slug": "bosnia-herzegovina-vs-qatar-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/bosnia-herzegovina-vs-qatar-prediction-world-cup-2026-match-preview",
        "home_en": "Bosnia-Herzegovina",
        "away_en": "Qatar",
        "home_cn": "波黑",
        "away_cn": "卡塔尔",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 14.0,
        "insights": [
            "Qatar’s FIFA World Cup campaign looks set to come to an end, with the Opta supercomputer giving them just a 14.0% chance of victory.",
            "Bosnia-Herzegovina have recorded 3+ shots on target in 13 of their last 15 competitive internationals, while also averaging 25 touches in the opposition’s penalty area per game across that time.",
            "Qatar have failed to win any of their eight internationals since a 2-1 victory over the United Arab Emirates in October 2025 (D3 L5)."
        ],
        "prediction": "The Opta supercomputer makes Bosnia heavy favourites for this match after they came out on top in 67.8% of the 25,000 pre-match simulations."
    },
    {
        "slug": "switzerland-vs-canada-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/switzerland-vs-canada-prediction-world-cup-2026-match-preview",
        "home_en": "Switzerland",
        "away_en": "Canada",
        "home_cn": "瑞士",
        "away_cn": "加拿大",
        "home_pct": 43.5,
        "draw_pct": 28.3,
        "away_pct": 28.1,
        "insights": [
            "Switzerland are unbeaten against CONCACAF opposition at the World Cup (W2 D3), and are the Opta supercomputer’s favourites to extend that streak with victory here, at 43.5%.",
            "Against Qatar, Jonathan David became only the second player from a CONCACAF nation to score a hat-trick at the finals, after USA’s Bert Patenaude against Paraguay in 1930.",
            "Switzerland have lost just one of their last nine World Cup group games (W5 D3), going down 1-0 against Brazil in 2022."
        ],
        "prediction": "The Opta supercomputer favours a Switzerland victory, with Yakin’s side winning 43.5% of the 25,000 pre-match simulations. Canada’s chances of claiming three points – and subsequently top spot in Group B – are rated at 28.1%, with a draw at 28.3%."
    },
    {
        "slug": "panama-vs-croatia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/panama-vs-croatia-prediction-world-cup-2026-match-preview",
        "home_en": "Panama",
        "away_en": "Croatia",
        "home_cn": "巴拿马",
        "away_cn": "克罗地亚",
        "home_pct": 14.9,
        "draw_pct": 22.2,
        "away_pct": 63.0,
        "insights": [
            "The Opta supercomputer expects Croatia to win; they overcame Panama in a convincing 63.0% of pre-match simulations.",
            "Panama have lost each of their four World Cup matches, scoring just two goals.",
            "Croatia could lose back-to-back World Cup matches for just the second time."
        ],
        "prediction": "The Opta supercomputer ran 25,000 pre-match simulations, with Croatia getting back on track and winning 63.0% of those. Panama are afforded just a 14.9% chance of a first World Cup victory, while the draw accounted for 22.2% of the data-led simulations."
    },
    {
        "slug": "colombia-vs-dr-congo-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/colombia-vs-dr-congo-prediction-world-cup-2026-match-preview",
        "home_en": "Colombia",
        "away_en": "DR Congo",
        "home_cn": "哥伦比亚",
        "away_cn": "刚果民主共和国",
        "home_pct": 58.0,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Ahead of kick-off in Guadalajara, Colombia won in 58.0% of the Opta supercomputer’s simulations.",
            "Wednesday’s meeting will mark the first encounter between these two sides in men’s international football.",
            "DR Congo are fresh off earning their first point and scoring their first goal at the World Cup after their 1-1 opening draw with Portugal."
        ],
        "prediction": "The Opta supercomputer could not look past a Colombia win in Guadalajara, with Lorenzo’s side taking three points in 58% of the 25,000 pre-match simulations. Meanwhile, the chances of DR Congo pulling off another upset, and a draw are rated exactly the same at 21%."
    },
    {
        "slug": "norway-vs-senegal-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/norway-vs-senegal-prediction-world-cup-2026-match-preview",
        "home_en": "Norway",
        "away_en": "Senegal",
        "home_cn": "挪威",
        "away_cn": "塞内加尔",
        "home_pct": 44.7,
        "draw_pct": 24.9,
        "away_pct": 30.5,
        "insights": [
            "After an emphatic 4-1 opening win over Iraq, Norway walk into this contest as favourites with the Opta supercomputer handing them a 44.7% win probability to Senegal’s 30.5%.",
            "Monday’s clash will mark the first time Norway and Senegal meet in the World Cup.",
            "After losing just one of their first five World Cup matches against European opponents (W3 D1), Senegal have now lost each of their last three."
        ],
        "prediction": "The Opta supercomputer predicts a close contest in New Jersey, with marginal favourites Norway winning 44.7% of its 25,000 pre-match simulations. Senegal triumphed 30.5% of the time, while a draw was shown a 24.9% chance."
    },
    {
        "slug": "jordan-vs-algeria-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/jordan-vs-algeria-prediction-world-cup-2026-match-preview",
        "home_en": "Jordan",
        "away_en": "Algeria",
        "home_cn": "约旦",
        "away_cn": "阿尔及利亚",
        "home_pct": 17.6,
        "draw_pct": 21.7,
        "away_pct": 60.7,
        "insights": [
            "Algeria have won just one of their last 11 World Cup matches (D3 L7), but are the Opta supercomputer’s favourites for victory here at 60.7%.",
            "Jordan are without a win in their last six matches in all competitions (D2 L4), suffering as many defeats as in their previous 13 games (W7 D2).",
            "Algeria have never previously lost their opening two matches at a World Cup finals."
        ],
        "prediction": "The Opta supercomputer favours an Algeria victory, with Petković’s side winning 60.7% of the 25,000 pre-match simulations. Jordan’s chances of claiming a first World Cup win are rated at 17.6%, with a draw at 21.7%."
    },
    {
        "slug": "argentina-vs-austria-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/argentina-vs-austria-prediction-world-cup-2026-match-preview",
        "home_en": "Argentina",
        "away_en": "Austria",
        "home_cn": "阿根廷",
        "away_cn": "奥地利",
        "home_pct": 65.4,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "The Opta supercomputer gives Argentina a 65.4% win probability based on 25,000 pre-match simulations.",
            "Argentina could become just the seventh nation to score at least three goals in four consecutive World Cup matches, and the first since Spain between 1998 and 2002.",
            "Seven of Austria’s last 10 World Cup goals have been scored from set-pieces (3 corners, 2 penalties, 1 free-kick, 1 direct free-kick)."
        ],
        "prediction": ""
    },
    {
        "slug": "france-vs-iraq-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/france-vs-iraq-prediction-world-cup-2026-match-preview",
        "home_en": "France",
        "away_en": "Iraq",
        "home_cn": "法国",
        "away_cn": "伊拉克",
        "home_pct": 88.8,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "France are regarded as heavy favourites to win this match, coming out on top in 88.8% of the Opta supercomputer’s 25,000 simulations.",
            "Iraq have lost all four of their previous FIFA World Cup matches and could become the very first Asian nation to suffer defeat in each of their opening five games across the tournament’s history.",
            "France are seeking to win both of their opening two matches at a World Cup for the fourth successive edition – having done so in just one of their previous 13 appearances in the competition (1998)."
        ],
        "prediction": "The Opta supercomputer understandably regards France as heavy favourites to win this match, and any other result would be a huge shock. Deschamps’ side were triumphant in 88.8% of the 25,000 pre-match simulations. The next most likely result is a draw, at 7.9%, while Iraq earned a famous victory in 3.4% of simulations."
    },
    {
        "slug": "new-zealand-vs-egypt-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/new-zealand-vs-egypt-prediction-world-cup-2026-match-preview",
        "home_en": "New Zealand",
        "away_en": "Egypt",
        "home_cn": "新西兰",
        "away_cn": "埃及",
        "home_pct": 17.7,
        "draw_pct": 22.7,
        "away_pct": 59.6,
        "insights": [
            "Following 25,000 pre-match simulations by the Opta supercomputer, Egypt have been assigned a 59.6% chance of posting their first World Cup win.",
            "Ranked 56 places below their next opponents by FIFA – and with just an 17.7% chance of victory – New Zealand will assume their familiar position as underdogs.",
            "While the All Whites have yet to taste success after seven games at this level, only Honduras (nine) have played more often at the World Cup without winning than Egypt (eight)."
        ],
        "prediction": "The Opta Supercomputer’s 25,000 pre-match simulations established Egypt as clear favourites, with a 59.6% chance of success. New Zealand came out on top in just 17.7% of those simulations, with a draw rated at 22.7%."
    },
    {
        "slug": "uruguay-vs-cape-verde-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/uruguay-vs-cape-verde-prediction-world-cup-2026-match-preview",
        "home_en": "Uruguay",
        "away_en": "Cape Verde",
        "home_cn": "乌拉圭",
        "away_cn": "佛得角",
        "home_pct": 67.2,
        "draw_pct": 20.6,
        "away_pct": 12.2,
        "insights": [
            "The Opta supercomputer expects Uruguay to win this one after they came out on top in 67.2% of pre-match simulations.",
            "Cape Verde have never faced Uruguay but have suffered defeat in their only two encounters with CONMEBOL opposition.",
            "Uruguay have lost only one of their last nine group games at the World Cup."
        ],
        "prediction": "The Opta supercomputer struggled to see past a win for Uruguay, who claimed all three points in a massive 67.2% of 25,000 pre-match simulations. Cape Verde are afforded just a 12.2% chance of victory in the same data-led sims, while the draw accounted for 20.6% of scenarios."
    },
    {
        "slug": "belgium-vs-iran-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/belgium-vs-iran-prediction-world-cup-2026-match-preview",
        "home_en": "Belgium",
        "away_en": "Iran",
        "home_cn": "比利时",
        "away_cn": "伊朗",
        "home_pct": 67.5,
        "draw_pct": 19.3,
        "away_pct": 13.2,
        "insights": [
            "The Opta supercomputer predicts Belgium as favourites for this clash against Iran, with a strong win probability of 67.5%.",
            "Sunday’s clash will mark the first ever encounter between Belgium and Iran in men’s international football.",
            "Iran have won just one of their 10 World Cup matches against European opposition (D2 L7) ."
        ],
        "prediction": "The Red Devils triumphed in 67.5% of the 25,000 pre-match simulations, while Iran’s chances of victory are rated at just 13.2%. The probability of a draw, then, is left at 19.3%."
    },
    {
        "slug": "spain-vs-saudi-arabia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/spain-vs-saudi-arabia-prediction-world-cup-2026-match-preview",
        "home_en": "Spain",
        "away_en": "Saudi Arabia",
        "home_cn": "西班牙",
        "away_cn": "沙特阿拉伯",
        "home_pct": 87.4,
        "draw_pct": null,
        "away_pct": 3.8,
        "insights": [
            "Spain are considered the overwhelming favourites by the Opta supercomputer for this fixture, with a win probability of 87.4% to Saudi Arabia’s 3.8%.",
            "Spain have now completed exactly 2,500 passes and taken 49 shots since scoring their last World Cup goal.",
            "Mohammed Al Owais made nine saves for Saudi Arabia against Uruguay on Matchday 1."
        ],
        "prediction": ""
    },
    {
        "slug": "turkiye-vs-paraguay-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/turkiye-vs-paraguay-prediction-world-cup-2026-match-preview",
        "home_en": "Türkiye",
        "away_en": "Paraguay",
        "home_cn": "土耳其",
        "away_cn": "巴拉圭",
        "home_pct": 48.4,
        "draw_pct": 26.0,
        "away_pct": 25.5,
        "insights": [
            "Though they failed to produce on Matchday 1, Türkiye have a 48.4% chance of winning their second group game against Paraguay, according to the Opta Supercomputer.",
            "With just a 25.5% chance of victory, Paraguay aren’t expected to end their four-match winless streak at the World Cup.",
            "Türkiye took 30 shots in their opener, the most by any team without scoring in a World Cup match since 2006 (Portugal vs England, 31) and most without extra-time since Uruguay vs Sweden in 1974 (30)."
        ],
        "prediction": "The Opta supercomputer produced 25,000 pre-match simulations, and Türkiye came out as winners in 48.4% of the simulations. Paraguay only prevailed in 25.5%, with a draw rated at 26.0% – given the circumstances, the latter result would suit neither side."
    },
    {
        "slug": "brazil-vs-haiti-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/brazil-vs-haiti-prediction-world-cup-2026-match-preview",
        "home_en": "Brazil",
        "away_en": "Haiti",
        "home_cn": "巴西",
        "away_cn": "海地",
        "home_pct": 87.3,
        "draw_pct": null,
        "away_pct": 4.3,
        "insights": [
            "Brazil are considered the overwhelming favourites by the Opta supercomputer for this fixture, with a win probability of 87.3% to Haiti’s 4.3%.",
            "Vinícius Júnior has been involved in four goals in five appearances at the World Cup.",
            "Haiti had more shots than any other Group C side on MD1 (15)."
        ],
        "prediction": ""
    },
    {
        "slug": "tunisia-vs-japan-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/tunisia-vs-japan-prediction-world-cup-2026-match-preview",
        "home_en": "Tunisia",
        "away_en": "Japan",
        "home_cn": "突尼斯",
        "away_cn": "日本",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 60.7,
        "insights": [
            "Japan are regarded as clear favourites to win this match, coming out on top in 60.7% of the Opta supercomputer’s 25,000 simulations.",
            "Tunisia’s 5-1 defeat to Sweden on MD1 was their heaviest defeat in their FIFA World Cup history.",
            "Despite conceding in each of their seven FIFA World Cup group games since 2018, Japan have only lost two of those matches (W3 D2), while they’ve only lost one of their previous four matches at the tournament in which they’ve conceded first (W2 D1)."
        ],
        "prediction": "Tunisia’s decision to replace Lamouchi with Renard after just one game offers an interesting dynamic to this match, but the Opta supercomputer is still confident Japan will come out on top, winning the World Cup’s 1,000 th match in 60.7% of its 25,000 simulations. The next most likely result is a draw, at 22.9%. Meanwhile, Tunisia have a 16.4% of earning a surprising win."
    },
    {
        "slug": "ecuador-vs-curacao-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/ecuador-vs-curacao-prediction-world-cup-2026-match-preview",
        "home_en": "Ecuador",
        "away_en": "Curaçao",
        "home_cn": "厄瓜多尔",
        "away_cn": "库拉索",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 5.3,
        "insights": [
            "After their heavy opening game defeat, the Opta supercomputer gives Curaçao just a 5.3% win probability against Ecuador.",
            "Ecuador are winless in three games at the World Cup (D1 L2) since their 2-0 victory over Qatar in 2022.",
            "This is Curaçao’s second World Cup match – only three CONCACAF nations have ever recorded a victory in one of their opening two matches in the competition (USA in 1930, Cuba in 1938, Costa Rica in 1990)."
        ],
        "prediction": "Across the 25,000 pre-match simulations, Ecuador came on top in a whopping 84.5% of them. The probability of a draw is 10.2%, with Curaçao taking all three points in just 5.3% of projections."
    },
    {
        "slug": "germany-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/germany-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "home_en": "Germany",
        "away_en": "Ivory Coast",
        "home_cn": "德国",
        "away_cn": "科特迪瓦",
        "home_pct": 44.2,
        "draw_pct": 25.7,
        "away_pct": 30.1,
        "insights": [
            "Germany have won their last 10 matches in all competitions and are the Opta supercomputer’s favourites here, extending that streak with a win over Ivory Coast in 44.2% of the simulations.",
            "Ivory Coast have never won multiple games in a single edition of the World Cup.",
            "Germany have failed to register a clean sheet in any of their last seven World Cup matches."
        ],
        "prediction": "The Opta supercomputer favours an 11th straight Germany victory in all competitions, with Nagelsmann’s side winning 44.2% of the 25,000 pre-match simulations. Ivory Coast’s chances of claiming three points are rated at 30.1%, with a draw at 25.7%."
    },
    {
        "slug": "netherlands-vs-sweden-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/netherlands-vs-sweden-prediction-world-cup-2026-match-preview",
        "home_en": "Netherlands",
        "away_en": "Sweden",
        "home_cn": "荷兰",
        "away_cn": "瑞典",
        "home_pct": 55.8,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "The Opta supercomputer makes the Netherlands favourites for this game against Sweden, winning 55.8% of its 25,000 pre-match simulations.",
            "The Dutch have avoided defeat (in normal time) in their last 13 World Cup games, since losing 1–0 to Spain in the 2010 final – that’s the joint-longest unbeaten run by any team in the tournament’s history, along with Brazil between 1958 and 1966.",
            "Sweden’s five goals against Tunisia in their opener has already equalled their tally from the entire group stage at the 2018 World Cup, and they’ve only netted more group-stage goals in one of their previous six editions of the tournament (six in 1994)."
        ],
        "prediction": "Over 25,000 pre-match simulations, the Oranje came out on top in 55.8% of the outcomes, suggesting that Koeman’s charges look likely to bounce back and claim their first win at the 2026 World Cup. A Swedish victory stands at just 21.9% probability, but a single point – with a 22.3% likelihood of a draw – should still be enough for Potter’s side to seal their place in the last 32."
    },
    {
        "slug": "scotland-vs-morocco-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/scotland-vs-morocco-prediction-world-cup-2026-match-preview",
        "home_en": "Scotland",
        "away_en": "Morocco",
        "home_cn": "苏格兰",
        "away_cn": "摩洛哥",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 54.9,
        "insights": [
            "After opening their World Cup campaign with a draw against Brazil, the Opta supercomputer backs Morocco to triumph with a dominant win probability of 54.9%.",
            "The only previous encounter between these two sides came in the group stages of the 1998 World Cup, where Morocco picked up a comfortable 3-0 win.",
            "Following their 1-0 win over Haiti, Scotland are aiming to win back-to-back matches at a major tournament for the very first time."
        ],
        "prediction": "The Opta supercomputer gives Morocco a 91.6% chance of progressing to the knockout stage, while Scotland are assigned an 80.6% probability, making Friday’s result potentially decisive in the battle for qualification."
    },
    {
        "slug": "usa-vs-australia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/usa-vs-australia-prediction-world-cup-2026-match-preview",
        "home_en": "USA",
        "away_en": "Australia",
        "home_cn": "美国",
        "away_cn": "澳大利亚",
        "home_pct": 20.6,
        "draw_pct": 20.9,
        "away_pct": 58.5,
        "insights": [
            "The Opta supercomputer has given the United States a sizeable chance of victory ahead of this game, with Mauricio Pochettino’s side winning 58.5% of pre-match simulations.",
            "USA have won each of their last seven matches in Seattle .",
            "Australia have won three of their last four games at the World Cup, having managed just two victories across their first 17 tournament matches."
        ],
        "prediction": "From 25,000 pre-match simulations, Pochettino’s team came out on top in 58.5% of the outcomes, suggesting there is a growing weight of expectation behind this USA side. Australia’s chances of victory stand at just 20.6% by comparison, and with a draw given a 20.9% probability, the Socceroos will be keen to upset those pre-match presumptions."
    },
    {
        "slug": "mexico-vs-south-korea-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/mexico-vs-south-korea-prediction-world-cup-2026-match-preview",
        "home_en": "Mexico",
        "away_en": "South Korea",
        "home_cn": "墨西哥",
        "away_cn": "韩国",
        "home_pct": 48.8,
        "draw_pct": 26.4,
        "away_pct": 24.8,
        "insights": [
            "The Opta supercomputer expects Mexico to make it back-to-back wins as they overcame South Korea in a convincing 48.8% of pre-match simulations.",
            "South Korea could win their opening two matches at a World Cup for the first time in history.",
            "Raúl Jiménez has scored in his last two matches against South Korea."
        ],
        "prediction": "But the Opta supercomputer leant towards a Mexico victory in this encounter as Aguirre’s side came out on top in 48.8% of 25,000 pre-match simulations. South Korea were afforded a 24.8% chance of winning in the same data-led simulations, while the draw accounted for 26.4% of scenarios."
    },
    {
        "slug": "canada-vs-qatar-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/canada-vs-qatar-prediction-world-cup-2026-match-preview",
        "home_en": "Canada",
        "away_en": "Qatar",
        "home_cn": "加拿大",
        "away_cn": "卡塔尔",
        "home_pct": 72.9,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Canada are clear favourites to win this match, coming out on top in 72.9% of the Opta supercomputer’s 25,000 simulations.",
            "Canada have won their last four matches played in Vancouver, scoring 17 goals and conceding only two. The last team to beat them in the British Columbia city were Mexico in a March 2016 World Cup qualifier (3-0).",
            "Qatar ranked bottom of sides in Group B at the 2026 FIFA World Cup for shots (6), average possession (32%), forward passes (118), touches in the opposition box (8) and successful final-third passes (24) on MD1."
        ],
        "prediction": "The Opta supercomputer is supremely confident that it will be Canada who pick up their first World Cup win in this match, with Marsch’s side earning all three points in 72.9% of its 25,000 simulations. The next most likely result is a draw, at 16.5%. Meanwhile, Qatar have just a 10.6% chance of upsetting the odds with an unlikely victory."
    },
    {
        "slug": "switzerland-vs-bosnia-herzegovina-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/switzerland-vs-bosnia-herzegovina-prediction-world-cup-2026-match-preview",
        "home_en": "Switzerland",
        "away_en": "Bosnia-Herzegovina",
        "home_cn": "瑞士",
        "away_cn": "波黑",
        "home_pct": 61.8,
        "draw_pct": 21.1,
        "away_pct": 17.2,
        "insights": [
            "Despite making an uncertain start, Switzerland have a 61.8% chance of winning their second group game, according to the Opta supercomputer.",
            "So, with just a 17.2% chance of victory, Bosnia-Herzegovina are not expected to set a new national record of 10 matches unbeaten.",
            "Switzerland have lost just two of their last 17 group games at either the World Cup or UEFA European Championship (W7 D8)."
        ],
        "prediction": "Of 25,000 pre-match simulations produced by the Opta supercomputer, Switzerland came out as strong favourites for victory: they have a 61.8% chance of success. Bosnia-Herzegovina only prevailed in 17.2% of those simulations, with a draw rated at 21.1%."
    },
    {
        "slug": "czechia-vs-south-africa-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/czechia-vs-south-africa-prediction-world-cup-2026-match-preview",
        "home_en": "Czechia",
        "away_en": "South Africa",
        "home_cn": "捷克",
        "away_cn": "南非",
        "home_pct": 52.9,
        "draw_pct": null,
        "away_pct": 23.3,
        "insights": [
            "The Opta supercomputer makes Czechia the favourites with a 52.9% win probability, compared to South Africa’s 23.3%.",
            "In Czechia’s Miroslav Koubek (74 years, 290 days) and South Africa’s Hugo Broos (74y 69d), this will be the first match in World Cup history to see both head coaches aged over 70.",
            "Teboho Mokoena completed 92.9% of his passes (39/42) against Mexico, the highest ratio by a South Africa player to attempt 40+ passes in a World Cup match."
        ],
        "prediction": ""
    },
    {
        "slug": "uzbekistan-vs-colombia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/uzbekistan-vs-colombia-prediction-world-cup-2026-match-preview",
        "home_en": "Uzbekistan",
        "away_en": "Colombia",
        "home_cn": "乌兹别克斯坦",
        "away_cn": "哥伦比亚",
        "home_pct": 11.7,
        "draw_pct": 20.6,
        "away_pct": 67.7,
        "insights": [
            "Colombia have won five of their last six World Cup group matches (L1), and are Opta’s favourites for victory here at 67.7%.",
            "Uzbekistan are aiming to become the first World Cup debutants since Slovakia in 2010 to reach the knockout stages.",
            "Fabio Cannavaro (2006) and Néstor Lorenzo (1990) are two of the three head coaches at the 2026 tournament to have played in a World Cup final, along with France boss Didier Deschamps (1998)."
        ],
        "prediction": "The Opta supercomputer favours a Colombia victory, winning 67.7% of the 25,000 pre-match simulations. Uzbekistan’s chances of marking their World Cup bow with a win are rated at 11.7%, with a draw at 20.6%."
    },
    {
        "slug": "ghana-vs-panama-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/ghana-vs-panama-prediction-world-cup-2026-match-preview",
        "home_en": "Ghana",
        "away_en": "Panama",
        "home_cn": "加纳",
        "away_cn": "巴拿马",
        "home_pct": 45.1,
        "draw_pct": 26.8,
        "away_pct": 28.1,
        "insights": [
            "The Opta supercomputer makes Ghana favourites, winning 45.1% of the pre-match simulations.",
            "Panama claimed their maiden World Cup win in 28.1% of the supercomputer’s 25,000 pre-match simulations.",
            "At the age of 73, Black Stars boss Carlos Queiroz will become just the third head coach to manage at five World Cups."
        ],
        "prediction": "After sifting through 25,000 pre-match simulations, the Opta supercomputer predicts victory for Ghana, winning 45.1% of those sims. This game surely represents their best chance of claiming points in Group L, but Panama only won 28.1% of the supercomputer simulations, leaving a draw rated at 26.8%."
    },
    {
        "slug": "england-vs-croatia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/england-vs-croatia-prediction-world-cup-2026-match-preview",
        "home_en": "England",
        "away_en": "Croatia",
        "home_cn": "英格兰",
        "away_cn": "克罗地亚",
        "home_pct": 55.9,
        "draw_pct": null,
        "away_pct": 20.8,
        "insights": [
            "The Opta supercomputer expects England to start their 2026 World Cup campaign strongly, with a win probability of 55.9% to Croatia’s 20.8%.",
            "This will be the second meeting between England and Croatia in the World Cup, following the 2018 semi-final, where Croatia triumphed 2-1 after extra time.",
            "England have lost only one of their last eight opening matches at the World Cup (W4 D3) – a 2-1 defeat to Italy in 2014."
        ],
        "prediction": "The Opta supercomputer gives Croatia a 77.2% chance of progressing from Group L, second only to England’s 95.6%."
    },
    {
        "slug": "portugal-vs-dr-congo-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/portugal-vs-dr-congo-prediction-world-cup-2026-match-preview",
        "home_en": "Portugal",
        "away_en": "DR Congo",
        "home_cn": "葡萄牙",
        "away_cn": "刚果民主共和国",
        "home_pct": 54.5,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "The Opta supercomputer pits Portugal as big favourites to get their 2026 World Cup campaign underway with a victory. They beat DR Congo in 54.5% of the pre-match simulations.",
            "Portugal have won only one of their last four opening World Cup matches, beating Ghana 3–2 in 2022. Their last three openers at the tournament have produced an average of five goals per game.",
            "This is only DR Congo’s second World Cup appearance, and first since 1974 when they competed as Zaire. Only Wales (64 years), Egypt and Norway (both 56) have had longer gaps than the Leopards’ 52 years between tournaments."
        ],
        "prediction": "Across 25,000 pre-match simulations, Portugal dispatched DR Congo in a sizeable 54.5% of the outcomes, with a 22.3% likelihood that this Group K opener will finish level. The Leopards’ chances of victory stand at a reasonable 23.2%, but Sébastien Desabre’s side certainly couldn’t have asked for a much tougher test on their World Cup return."
    },
    {
        "slug": "austria-vs-jordan-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/austria-vs-jordan-prediction-world-cup-2026-match-preview",
        "home_en": "Austria",
        "away_en": "Jordan",
        "home_cn": "奥地利",
        "away_cn": "约旦",
        "home_pct": 69.6,
        "draw_pct": null,
        "away_pct": 13.5,
        "insights": [
            "Austria are considered the overwhelming favourites by the Opta supercomputer for this clash, with a win probability of 69.6% to Jordan’s 13.5%.",
            "Austria have won only one of their last nine World Cup matches.",
            "Jordan scored 32 goals in the 2026 FIFA World Cup qualifiers, their highest tally in a single qualifying campaign."
        ],
        "prediction": ""
    },
    {
        "slug": "argentina-vs-algeria-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/argentina-vs-algeria-prediction-world-cup-2026-match-preview",
        "home_en": "Argentina",
        "away_en": "Algeria",
        "home_cn": "阿根廷",
        "away_cn": "阿尔及利亚",
        "home_pct": 67.8,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Argentina overcame Algeria in a convincing 67.8% of pre-match simulations by the Opta supercomputer.",
            "No team has won back-to-back World Cup titles since Brazil retained their crown in 1962.",
            "Lionel Messi could become the first player in history to feature at six different editions of this competition."
        ],
        "prediction": "Regardless, Amoura’s prowess in front of goal has set Algeria up for their fifth appearance at the World Cup, and their first since 2014. That edition in Brazil was the only time they have progressed past the first round, but the Opta supercomputer gives them a 57.4% chance of making the knockout stages here."
    },
    {
        "slug": "iraq-vs-norway-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/iraq-vs-norway-prediction-world-cup-2026-match-preview",
        "home_en": "Iraq",
        "away_en": "Norway",
        "home_cn": "伊拉克",
        "away_cn": "挪威",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 75.9,
        "insights": [
            "Norway are regarded as clear favourites to win this match, coming out on top in 75.9% of the Opta supercomputer’s 25,000 simulations.",
            "Norway were one of two teams to win 100% of their qualifiers in the UEFA section (8/8), alongside England. They also scored 4.6 goals per game (37 goals in 8 matches), the best average ever for any European nation in a single FIFA World Cup qualifying campaign with 4+ matches.",
            "Iraq were the 48th and final team to qualify for the 2026 FIFA World Cup, playing 21 qualifying matches to reach the tournament, more than any other side. They secured their place via the inter-confederation play-offs, beating Bolivia 2-1 in Mexico."
        ],
        "prediction": "The Opta supercomputer is confident of a Norway win here, with Solbakken’s side starting the tournament with a win in 75.9% of its 25,000 simulations. The next-most likely result is a draw at 14.2%. Meanwhile, Iraq are regarded as having a 9.9% chance of earning a shock win."
    },
    {
        "slug": "france-vs-senegal-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/france-vs-senegal-prediction-world-cup-2026-match-preview",
        "home_en": "France",
        "away_en": "Senegal",
        "home_cn": "法国",
        "away_cn": "塞内加尔",
        "home_pct": 65.6,
        "draw_pct": 19.5,
        "away_pct": 14.9,
        "insights": [
            "France are the clear favourites with the Opta supercomputer for this clash, given a win probability of 65.6% to Senegal’s 14.9%.",
            "Kylian Mbappé has scored more goals than any other player across the last two World Cups.",
            "Senegal have kept only one clean sheet in their 12 World Cup matches ."
        ],
        "prediction": "Still, though, the Opta supercomputer expects Les Bleus to emerge triumphant at New York New Jersey Stadium, with a win probability of 65.6%. By contrast, Senegal are rated as a mere 14.9% chance to get off to a winning start, while the draw is a 19.5% shot."
    },
    {
        "slug": "iran-vs-new-zealand-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/iran-vs-new-zealand-prediction-world-cup-2026-match-preview",
        "home_en": "Iran",
        "away_en": "New Zealand",
        "home_cn": "伊朗",
        "away_cn": "新西兰",
        "home_pct": 51.4,
        "draw_pct": 26.7,
        "away_pct": 21.9,
        "insights": [
            "Only Scotland (8) have made more World Cup appearances without making it past the first round than Iran (6), but they are Opta’s favourites for victory here, given a 51.4% chance of victory.",
            "Only Honduras (9) and Egypt (7) have played more World Cup matches than New Zealand (6) without ever recording a win.",
            "Iran’s last eight goals at the finals have all been scored in the second half, including five in stoppage time."
        ],
        "prediction": "The Opta supercomputer favours an Iran victory, with Ghalenoei’s side winning 51.4% of the 25,000 pre-match simulations. New Zealand’s chances of claiming that first ever World Cup win are rated at 21.9%, with a draw at 26.7%."
    },
    {
        "slug": "saudi-arabia-vs-uruguay-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/saudi-arabia-vs-uruguay-prediction-world-cup-2026-match-preview",
        "home_en": "Saudi Arabia",
        "away_en": "Uruguay",
        "home_cn": "沙特阿拉伯",
        "away_cn": "乌拉圭",
        "home_pct": 14.8,
        "draw_pct": 22.0,
        "away_pct": 63.2,
        "insights": [
            "Favourites by a significant margin, the Opta supercomputer has given Uruguay a 63.2% chance of winning their group opener.",
            "With a modest 14.8% chance of success, Saudi Arabia aren’t fancied to repeat their shock result against Argentina in the opening round of Qatar 2022.",
            "Only three men have managed more teams at the World Cup than Uruguay boss Marcelo Bielsa (3), but his sides have never scored more than once in a game."
        ],
        "prediction": "After 25,000 pre-match simulations, the Opta supercomputer predicted success for Uruguay, with the South American side having a 63.2% chance of victory. Saudi Arabia start as long shots: only prevailing in 14.8% of those simulations, leaving a draw rated at 22.0%."
    },
    {
        "slug": "belgium-vs-egypt-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/belgium-vs-egypt-prediction-world-cup-2026-match-preview",
        "home_en": "Belgium",
        "away_en": "Egypt",
        "home_cn": "比利时",
        "away_cn": "埃及",
        "home_pct": 60.2,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "The Opta supercomputer has Belgium as favourites (60.2%).",
            "Belgium are making their 15th World Cup appearance; no European team has qualified for as many tournaments without ever winning the trophy.",
            "Only Honduras (9) have played more World Cup games than Egypt (7) without ever registering a victory."
        ],
        "prediction": "Belgium came out on top in 60.2% of simulations, with Egypt winning in just 17.8%."
    },
    {
        "slug": "spain-vs-cape-verde-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/spain-vs-cape-verde-prediction-world-cup-2026-match-preview",
        "home_en": "Spain",
        "away_en": "Cape Verde",
        "home_cn": "西班牙",
        "away_cn": "佛得角",
        "home_pct": 87.2,
        "draw_pct": 8.1,
        "away_pct": 4.8,
        "insights": [
            "The Opta supercomputer is very much expecting Spain to start their World Cup campaign on the front foot, with 87.2% of the pre-match simulations ending in victory for the UEFA Euro 2024 winners.",
            "Spain are appearing in their 17th World Cup and a 13th in a row, which is the second-longest current run of consecutive participations for a European nation after Germany’s 19.",
            "Cape Verde are the 14th African team to participate at the tournament, and will be aiming to become the first CAF side since Ghana in 2006 to reach the knockout stages on their World Cup debut."
        ],
        "prediction": "From 25,000 pre-match simulations, De la Fuente’s side came out on top in 87.2% of the outcomes, suggesting that Spain could make a significant statement right from the off. A draw stands at an 8.1% probability with a Cape Verde victory even lower at just 4.8%, but having already shocked the world just by reaching this tournament, Bubista’s Blue Sharks may have another upset in their arsenal."
    },
    {
        "slug": "sweden-vs-tunisia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/sweden-vs-tunisia-prediction-world-cup-2026-match-preview",
        "home_en": "Sweden",
        "away_en": "Tunisia",
        "home_cn": "瑞典",
        "away_cn": "突尼斯",
        "home_pct": 51.1,
        "draw_pct": 25.7,
        "away_pct": 23.2,
        "insights": [
            "The Opta supercomputer pegs Graham Potter’s Sweden as favourites ahead of kick-off, with a win probability of 51.1% to Tunisia’s 23.2%.",
            "Sunday’s clash marks the first ever meeting between these two sides in the World Cup, with all four previous encounters coming in friendlies.",
            "Sweden have lost just two of their 12 World Cup openers (W5 D5) and are unbeaten across each of their last four (W1 D3)."
        ],
        "prediction": "Sweden enter this Group F opener as favourites according to the Opta supercomputer, with Potter’s side coming out on top in 51.1% of the 10,000 pre-match simulations. Tunisia managed victory in a slim 23.2% of the supercomputer’s simulations, while a draw is rated at a 25.7% shot."
    },
    {
        "slug": "ivory-coast-vs-ecuador-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/ivory-coast-vs-ecuador-prediction-world-cup-2026-match-preview",
        "home_en": "Ivory Coast",
        "away_en": "Ecuador",
        "home_cn": "科特迪瓦",
        "away_cn": "厄瓜多尔",
        "home_pct": 37.5,
        "draw_pct": 27.3,
        "away_pct": 35.2,
        "insights": [
            "Ivory Coast are regarded as slight favourites to win this match against Ecuador, coming out on top in 37.5% of the Opta supercomputer’s 25,000 simulations.",
            "Ecuador boasted the strongest defence in the CONMEBOL qualifiers, conceding just five goals across 18 matches. They also lost the fewest matches (2).",
            "Ivory Coast won eight of their 10 matches in the qualifiers for the 2026 FIFA World Cup (D2) and were one of only two teams in the CAF section not to concede a single goal."
        ],
        "prediction": "Ivory Coast are slight favourites, winning this match in 37.5% of the supercomputer’s 25,000 pre-match simulations, while Ecuador came out on top in 35.2% of sims. The chance of a draw sits at 27.3%."
    },
    {
        "slug": "netherlands-vs-japan-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/netherlands-vs-japan-prediction-world-cup-2026-match-preview",
        "home_en": "Netherlands",
        "away_en": "Japan",
        "home_cn": "荷兰",
        "away_cn": "日本",
        "home_pct": 49.0,
        "draw_pct": null,
        "away_pct": 26.0,
        "insights": [
            "Netherlands are considered favourites for this game by Opta’s supercomputer with a 49.0% win probability to Japan’s 26.0%.",
            "The Oranje are unbeaten in their last 16 group matches at the FIFA World Cup (W12 D4), the longest current unbeaten run.",
            "Japan have won their first match in their last two FIFA World Cup appearances."
        ],
        "prediction": ""
    },
    {
        "slug": "germany-vs-curacao-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/germany-vs-curacao-prediction-world-cup-2026-match-preview",
        "home_en": "Germany",
        "away_en": "Curaçao",
        "home_cn": "德国",
        "away_cn": "库拉索",
        "home_pct": 90.7,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Curaçao lost to Germany in a massive 90.7% of pre-match simulations by the Opta supercomputer.",
            "Germany are making their 21st World Cup appearance, more than any other European nation and second only to Brazil overall (23).",
            "Curaçao’s Dick Advocaat will become the oldest head coach in the history of the competition."
        ],
        "prediction": "Owing to the expanded 48-team competition, the Opta supercomputer’s pre-tournament predictions gave Curaçao a 19% chance of reaching the round of 32. Germany topped Group E , in which they also face Ecuador and Ivory Coast , in 59.9% of 25,000 simulations."
    },
    {
        "slug": "united-states-vs-paraguay-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/united-states-vs-paraguay-prediction-world-cup-2026-match-preview",
        "home_en": "United States",
        "away_en": "Paraguay",
        "home_cn": "美国",
        "away_cn": "巴拉圭",
        "home_pct": 39.6,
        "draw_pct": 26.6,
        "away_pct": 33.8,
        "insights": [
            "Predicting victory for the co-hosts, the Opta supercomputer gives the United States a 39.6% chance of winning their opener.",
            "With a 33.8% probability of success, Paraguay aren’t fancied to reverse the result from one previous World Cup meeting – a 3-0 win for USA.",
            "That encounter came at the inaugural finals in 1930, when Bert Patenaude scored the first World Cup hat-trick – it’s still the USA’s joint-largest win at the tournament."
        ],
        "prediction": "Following 10,000 pre-match simulations, the Opta supercomputer predicts success for the United States, with a 39.6% chance of victory. Paraguay prevailed in 33.8% of those simulations, leaving a draw rated at 26.6%."
    },
    {
        "slug": "canada-vs-bosnia-herzegovina-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/canada-vs-bosnia-herzegovina-prediction-world-cup-2026-match-preview",
        "home_en": "Canada",
        "away_en": "Bosnia-Herzegovina",
        "home_cn": "加拿大",
        "away_cn": "波黑",
        "home_pct": 52.7,
        "draw_pct": 25.3,
        "away_pct": 22.0,
        "insights": [
            "The Opta supercomputer favours a Canada win ahead of kick-off, with the co-hosts triumphing in a dominant 52.7% of the pre-match simulations.",
            "Canada are still looking for their first ever win in a men’s FIFA World Cup match, having lost all six of their previous games.",
            "Friday’s Group B opener will mark the first ever encounter between Canada and Bosnia-Herzegovina."
        ],
        "prediction": "The Opta supercomputer could not look past a victory for Canada, who came out on top in 52.7% of the 10,000 pre-match simulations. Bosnia-Herzegovina triumphed in just 22.0% of the supercomputer’s simulations, with a draw accounting for the remaining 25.3%."
    },
    {
        "slug": "haiti-vs-scotland-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/haiti-vs-scotland-prediction-world-cup-2026-match-preview",
        "home_en": "Haiti",
        "away_en": "Scotland",
        "home_cn": "海地",
        "away_cn": "苏格兰",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 59.0,
        "insights": [
            "The Opta supercomputer is expecting Scotland to pick up a victory in their first World Cup match since 1998, with Steve Clarke’s side beating Haiti in 59.0% of the pre-match simulations.",
            "Haiti conceded 14 goals across their three group games at the 1974 FIFA World Cup – that’s the second most at this stage of the tournament, after South Korea shipped 16 at the 1954 edition.",
            "Scotland have lost their last three opening matches at the World Cup and last kicked off a tournament with victory back in 1982, beating New Zealand 5–2 at La Rosadela in Malaga, Spain."
        ],
        "prediction": "The Opta supercomputer sees Scotland as the overwhelming favourites to win their opener, with 59.0% of the 25,000 pre-match simulations ending in victory for the Tartan Army. Haiti’s chances of winning stand at a not-insurmountable 19.2%, although that’s the least likely result of the pre-match predictions, with a 21.8% likelihood of the game ending level."
    },
    {
        "slug": "australia-vs-turkiye-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/australia-vs-turkiye-prediction-world-cup-2026-match-preview",
        "home_en": "Australia",
        "away_en": "Türkiye",
        "home_cn": "澳大利亚",
        "away_cn": "土耳其",
        "home_pct": 20.5,
        "draw_pct": 24.1,
        "away_pct": 55.3,
        "insights": [
            "Türkiye have won all four of their World Cup matches against teams from the AFC confederation, and are the Opta supercomputer’s favourites for victory here (55.3% ).",
            "Australia have lost more matches than any other nation across the last five World Cups (ten of 17) .",
            "The Socceroos have also lost their opening game in five of their six World Cup appearances."
        ],
        "prediction": "The Opta supercomputer favours a Türkiye victory, with Montella’s side having won 55.3% of the 10,000 pre-match simulations. Australia’s chances of winning are rated at 20.5%, with a draw at 24.1%."
    },
    {
        "slug": "qatar-vs-switzerland-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/qatar-vs-switzerland-prediction-world-cup-2026-match-preview",
        "home_en": "Qatar",
        "away_en": "Switzerland",
        "home_cn": "卡塔尔",
        "away_cn": "瑞士",
        "home_pct": 9.1,
        "draw_pct": null,
        "away_pct": 76.0,
        "insights": [
            "The Opta supercomputer sees Switzerland as heavy favourites to kick off their World Cup campaign with a victory, winning 76.0% of the pre-match simulations compared to Qatar’s mere 9.1%.",
            "This is only Qatar’s second appearance at the FIFA World Cup, although it’s the first time they’ve ever qualified for the tournament after hosting in 2022.",
            "Switzerland are one of only two European teams to have reached the knockout stages in each of the last six major international tournaments (World Cup/Euros), alongside France."
        ],
        "prediction": "Across 25,000 pre-match simulations of this Group B clash, Switzerland came out on top 76.0% of the time, suggesting they are highly likely to pick up an early three points. Qatar’s chances of victory stand at just 9.1% by comparison, and with 14.9% of the simulations ending level, Julen Lopetegui’s side would likely be more than happy with a solitary point from this game."
    },
    {
        "slug": "brazil-vs-morocco-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/brazil-vs-morocco-prediction-world-cup-2026-match-preview",
        "home_en": "Brazil",
        "away_en": "Morocco",
        "home_cn": "巴西",
        "away_cn": "摩洛哥",
        "home_pct": 58.6,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Brazil have a 58.6% chance of getting their World Cup campaign off to a winning start against Morocco, according to the Opta supercomputer.",
            "This is the only group-stage fixture to feature two teams inside the top 10 of the FIFA World Rankings (Brazil 6th, Morocco 8th).",
            "Carlo Ancelotti is bidding to become the third coach to win both the World Cup and UEFA Champions League/European Cup after Marcello Lippi and Vicente del Bosque."
        ],
        "prediction": "Brazil have the upper hand in this Group C curtain-raiser, having come out on top in 57.7% of the Opta supercomputer ‘s 25,000 pre-match simulations."
    },
    {
        "slug": "south-korea-vs-czechia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/south-korea-vs-czechia-prediction-world-cup-2026-match-preview",
        "home_en": "South Korea",
        "away_en": "Czechia",
        "home_cn": "韩国",
        "away_cn": "捷克",
        "home_pct": 42.9,
        "draw_pct": null,
        "away_pct": 31.1,
        "insights": [
            "The Opta supercomputer rates South Korea as favourites for this Group A clash, with a win probability of 42.9% to Czechia’s 31.1%.",
            "This will be South Korea’s 12th World Cup tournament, the most of any Asian nation.",
            "Czechia scored more set-piece goals than any other team in the UEFA section of qualifying (11)."
        ],
        "prediction": ""
    },
    {
        "slug": "mexico-vs-south-africa-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/mexico-vs-south-africa-prediction-world-cup-2026-match-preview",
        "home_en": "Mexico",
        "away_en": "South Africa",
        "home_cn": "墨西哥",
        "away_cn": "南非",
        "home_pct": 67.1,
        "draw_pct": 19.4,
        "away_pct": 13.5,
        "insights": [
            "The Opta supercomputer’s pre-match simulations saw co-hosts Mexico secure victory over South Africa in a massive 67.1% of pre-match simulations.",
            "Mexico are unbeaten in their last seven opening matches at a men’s World Cup.",
            "None of South Africa’s nine games in the men’s FIFA World Cup have ended goalless."
        ],
        "prediction": "The Opta supercomputer could not look past a victory for Mexico, who came out on top in a convincing 67.1% of 10,000 pre-match simulations. South Africa finished as winners across 13.5% of supercomputer simulations, with the draw rated as more likely in 19.4% of the same data-led sims."
    }
]
