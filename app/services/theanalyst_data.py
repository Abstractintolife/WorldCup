"""自动生成：The Analyst（Opta）夺冠概率 + 逐场赛前预测快照。

请勿手工编辑。由 scripts_gen_theanalyst.py 抓取 theanalyst.com / Opta
（api.performfeeds.com 赛事模拟接口 + 预览文章）生成。
数据来源：theanalyst.com（Opta 超级计算机，25,000 次赛前模拟）。
"""

null = None  # 兼容缺失值

THEANALYST_TOURNAMENT = [
    {
        "team_en": "France",
        "team_cn": "法国",
        "code": "FRA",
        "group": "Group I",
        "win_pct": 18.66,
        "final_pct": 28.37,
        "points": 9,
        "played": 3
    },
    {
        "team_en": "Argentina",
        "team_cn": "阿根廷",
        "code": "ARG",
        "group": "Group J",
        "win_pct": 16.26,
        "final_pct": 30.04,
        "points": 9,
        "played": 3
    },
    {
        "team_en": "Spain",
        "team_cn": "西班牙",
        "code": "ESP",
        "group": "Group H",
        "win_pct": 13.47,
        "final_pct": 22.66,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "England",
        "team_cn": "英格兰",
        "code": "ENG",
        "group": "Group L",
        "win_pct": 9.68,
        "final_pct": 18.63,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Brazil",
        "team_cn": "巴西",
        "code": "BRA",
        "group": "Group C",
        "win_pct": 6.47,
        "final_pct": 13.68,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Netherlands",
        "team_cn": "荷兰",
        "code": "NED",
        "group": "Group F",
        "win_pct": 5.11,
        "final_pct": 10.13,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Portugal",
        "team_cn": "葡萄牙",
        "code": "POR",
        "group": "Group K",
        "win_pct": 4.74,
        "final_pct": 9.46,
        "points": 5,
        "played": 3
    },
    {
        "team_en": "Germany",
        "team_cn": "德国",
        "code": "GER",
        "group": "Group E",
        "win_pct": 4.36,
        "final_pct": 8.71,
        "points": 6,
        "played": 3
    },
    {
        "team_en": "Colombia",
        "team_cn": "哥伦比亚",
        "code": "COL",
        "group": "Group K",
        "win_pct": 3.19,
        "final_pct": 7.99,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Norway",
        "team_cn": "挪威",
        "code": "NOR",
        "group": "Group I",
        "win_pct": 2.95,
        "final_pct": 7.21,
        "points": 6,
        "played": 3
    },
    {
        "team_en": "United States",
        "team_cn": "美国",
        "code": "USA",
        "group": "Group D",
        "win_pct": 2.45,
        "final_pct": 5.68,
        "points": 6,
        "played": 3
    },
    {
        "team_en": "Switzerland",
        "team_cn": "瑞士",
        "code": "SUI",
        "group": "Group B",
        "win_pct": 2.17,
        "final_pct": 5.84,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Mexico",
        "team_cn": "墨西哥",
        "code": "MEX",
        "group": "Group A",
        "win_pct": 1.81,
        "final_pct": 5.02,
        "points": 9,
        "played": 3
    },
    {
        "team_en": "Morocco",
        "team_cn": "摩洛哥",
        "code": "MAR",
        "group": "Group C",
        "win_pct": 1.63,
        "final_pct": 3.8,
        "points": 7,
        "played": 3
    },
    {
        "team_en": "Belgium",
        "team_cn": "比利时",
        "code": "BEL",
        "group": "Group G",
        "win_pct": 1.58,
        "final_pct": 3.96,
        "points": 5,
        "played": 3
    },
    {
        "team_en": "Japan",
        "team_cn": "日本",
        "code": "JPN",
        "group": "Group F",
        "win_pct": 1.02,
        "final_pct": 2.94,
        "points": 5,
        "played": 3
    },
    {
        "team_en": "Ecuador",
        "team_cn": "厄瓜多尔",
        "code": "ECU",
        "group": "Group E",
        "win_pct": 0.61,
        "final_pct": 1.93,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Ecuador",
        "team_cn": "厄瓜多尔",
        "code": "ECU",
        "group": "3rd Place Ranking",
        "win_pct": 0.61,
        "final_pct": 1.93,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Croatia",
        "team_cn": "克罗地亚",
        "code": "CRO",
        "group": "Group L",
        "win_pct": 0.58,
        "final_pct": 1.55,
        "points": 6,
        "played": 3
    },
    {
        "team_en": "Senegal",
        "team_cn": "塞内加尔",
        "code": "SEN",
        "group": "Group I",
        "win_pct": 0.54,
        "final_pct": 1.62,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Senegal",
        "team_cn": "塞内加尔",
        "code": "SEN",
        "group": "3rd Place Ranking",
        "win_pct": 0.54,
        "final_pct": 1.62,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Canada",
        "team_cn": "加拿大",
        "code": "CAN",
        "group": "Group B",
        "win_pct": 0.47,
        "final_pct": 1.68,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Egypt",
        "team_cn": "埃及",
        "code": "EGY",
        "group": "Group G",
        "win_pct": 0.44,
        "final_pct": 1.82,
        "points": 5,
        "played": 3
    },
    {
        "team_en": "Australia",
        "team_cn": "澳大利亚",
        "code": "AUS",
        "group": "Group D",
        "win_pct": 0.34,
        "final_pct": 1.33,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Sweden",
        "team_cn": "瑞典",
        "code": "SWE",
        "group": "Group F",
        "win_pct": 0.29,
        "final_pct": 0.86,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Sweden",
        "team_cn": "瑞典",
        "code": "SWE",
        "group": "3rd Place Ranking",
        "win_pct": 0.29,
        "final_pct": 0.86,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Ghana",
        "team_cn": "加纳",
        "code": "GHA",
        "group": "Group L",
        "win_pct": 0.28,
        "final_pct": 1.06,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Ghana",
        "team_cn": "加纳",
        "code": "GHA",
        "group": "3rd Place Ranking",
        "win_pct": 0.28,
        "final_pct": 1.06,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Côte d'Ivoire",
        "team_cn": "Côte d'Ivoire",
        "code": "CIV",
        "group": "Group E",
        "win_pct": 0.24,
        "final_pct": 1.06,
        "points": 6,
        "played": 3
    },
    {
        "team_en": "Algeria",
        "team_cn": "阿尔及利亚",
        "code": "ALG",
        "group": "Group J",
        "win_pct": 0.21,
        "final_pct": 0.94,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Algeria",
        "team_cn": "阿尔及利亚",
        "code": "ALG",
        "group": "3rd Place Ranking",
        "win_pct": 0.21,
        "final_pct": 0.94,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Paraguay",
        "team_cn": "巴拉圭",
        "code": "PAR",
        "group": "Group D",
        "win_pct": 0.11,
        "final_pct": 0.47,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Paraguay",
        "team_cn": "巴拉圭",
        "code": "PAR",
        "group": "3rd Place Ranking",
        "win_pct": 0.11,
        "final_pct": 0.47,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Bosnia-Herzegovina",
        "team_cn": "波黑",
        "code": "BIH",
        "group": "Group B",
        "win_pct": 0.1,
        "final_pct": 0.4,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Austria",
        "team_cn": "奥地利",
        "code": "AUT",
        "group": "Group J",
        "win_pct": 0.1,
        "final_pct": 0.42,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Bosnia-Herzegovina",
        "team_cn": "波黑",
        "code": "BIH",
        "group": "3rd Place Ranking",
        "win_pct": 0.1,
        "final_pct": 0.4,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "South Africa",
        "team_cn": "南非",
        "code": "RSA",
        "group": "Group A",
        "win_pct": 0.05,
        "final_pct": 0.22,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Congo DR",
        "team_cn": "Congo DR",
        "code": "COD",
        "group": "Group K",
        "win_pct": 0.04,
        "final_pct": 0.28,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Congo DR",
        "team_cn": "Congo DR",
        "code": "COD",
        "group": "3rd Place Ranking",
        "win_pct": 0.04,
        "final_pct": 0.28,
        "points": 4,
        "played": 3
    },
    {
        "team_en": "Cabo Verde",
        "team_cn": "Cabo Verde",
        "code": "CPV",
        "group": "Group H",
        "win_pct": 0.03,
        "final_pct": 0.22,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Korea Republic",
        "team_cn": "韩国",
        "code": "KOR",
        "group": "Group A",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Czechia",
        "team_cn": "捷克",
        "code": "CZE",
        "group": "Group A",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 1,
        "played": 3
    },
    {
        "team_en": "Qatar",
        "team_cn": "卡塔尔",
        "code": "QAT",
        "group": "Group B",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 1,
        "played": 3
    },
    {
        "team_en": "Scotland",
        "team_cn": "苏格兰",
        "code": "SCO",
        "group": "Group C",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Haiti",
        "team_cn": "海地",
        "code": "HAI",
        "group": "Group C",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "Türkiye",
        "team_cn": "土耳其",
        "code": "TUR",
        "group": "Group D",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Curaçao",
        "team_cn": "库拉索",
        "code": "CUW",
        "group": "Group E",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 1,
        "played": 3
    },
    {
        "team_en": "Tunisia",
        "team_cn": "突尼斯",
        "code": "TUN",
        "group": "Group F",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "IR Iran",
        "team_cn": "IR Iran",
        "code": "IRN",
        "group": "Group G",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "New Zealand",
        "team_cn": "新西兰",
        "code": "NZL",
        "group": "Group G",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 1,
        "played": 3
    },
    {
        "team_en": "Uruguay",
        "team_cn": "乌拉圭",
        "code": "URU",
        "group": "Group H",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 2,
        "played": 3
    },
    {
        "team_en": "Saudi Arabia",
        "team_cn": "沙特阿拉伯",
        "code": "KSA",
        "group": "Group H",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 2,
        "played": 3
    },
    {
        "team_en": "Iraq",
        "team_cn": "伊拉克",
        "code": "IRQ",
        "group": "Group I",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "Jordan",
        "team_cn": "约旦",
        "code": "JOR",
        "group": "Group J",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "Uzbekistan",
        "team_cn": "乌兹别克斯坦",
        "code": "UZB",
        "group": "Group K",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "Panama",
        "team_cn": "巴拿马",
        "code": "PAN",
        "group": "Group L",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 0,
        "played": 3
    },
    {
        "team_en": "IR Iran",
        "team_cn": "IR Iran",
        "code": "IRN",
        "group": "3rd Place Ranking",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Korea Republic",
        "team_cn": "韩国",
        "code": "KOR",
        "group": "3rd Place Ranking",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Scotland",
        "team_cn": "苏格兰",
        "code": "SCO",
        "group": "3rd Place Ranking",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 3,
        "played": 3
    },
    {
        "team_en": "Uruguay",
        "team_cn": "乌拉圭",
        "code": "URU",
        "group": "3rd Place Ranking",
        "win_pct": 0.0,
        "final_pct": 0.0,
        "points": 2,
        "played": 3
    }
]

THEANALYST_MATCHES = [
    {
        "slug": "south-africa-vs-canada-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/south-africa-vs-canada-prediction-world-cup-2026-match-preview",
        "home_en": "South Africa",
        "away_en": "Canada",
        "home_cn": "南非",
        "away_cn": "加拿大",
        "home_pct": 19.7,
        "draw_pct": 24.1,
        "away_pct": 56.2,
        "insights": [
            "Canada are the narrow favourites, winning 56.2% of the Opta supercomputer’s pre-match simulations compared to South Africa’s 19.7% chance of victory.",
            "South Africa boss Hugo Broos will be the oldest head coach to take charge of a World Cup knockout match.",
            "This will be the first knockout-stage appearance at the finals for both teams."
        ],
        "prediction": "The Opta supercomputer swayed towards a Canada win inside 90 minutes: that happened in 56.2% of 25,000 pre-match simulations. South Africa still hold a 19.7% chance of winning in normal time, while the draw – which would mean extra-time and possibly penalties – accounted for 24.1% of scenarios.",
        "summary_cn": "Opta 超级计算机在 90 分钟内就倾向于加拿大获胜：在 25,000 次赛前模拟中，有 56.2% 发生了这种情况。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 加拿大队以微弱优势获胜，在 Opta 超级计算机的赛前模拟中获胜率为 56.2%，而南非队的获胜率为 19.7%。\n· 南非主帅雨果·布罗斯将成为执掌世界杯淘汰赛最年长的主教练。\n· 这将是两支球队首次进入决赛淘汰赛阶段。"
            ],
            [
                "深度分析",
                "南非和加拿大将在洛杉矶进行 32 强比赛，开启世界杯淘汰赛阶段。\n周日的比赛对于这对组合来说是未知的领域，因为在 2026 年版之前，两人都从未在 FIFA 旗舰赛事的小组赛中出线。\n这将是自 2002 年锦标赛以来两支球队首次在此类比赛中交锋。土耳其队在那场比赛中以1-0击败了东道主日本队，这对于南非队来说可能是一个积极的预兆，因为南非队将在这里面对共同东道主加拿大队。\n没有多少人预料到巴法纳能够以 A 组亚军的身份晋级，击败韩国和捷克队，落后于墨西哥。事实上，南非队是小组中在对方禁区内触球次数最少的球队（35 次），创造的绝佳机会也是最少的（2 次）。\n但雨果·布鲁斯可能喜欢扮演失败者的角色。南非目前世界排名第 61 位，将成为世界杯淘汰赛阶段排名倒数第三的球队，仅次于尼日利亚（1998 年第 74 位）和俄罗斯（2018 年第 70 位），并与日本（2018 年第 61 位）持平。\n对于 74 岁的布罗斯来说，这也将是一次历史性的出游。这位南非主教练将成为历史上执教世界杯淘汰赛阶段球队最年长的主教练。\n南非队的亚军出线很大程度上要归功于萨佩洛·马塞科，他在 MD3 比赛中以 1-0 战胜韩国队，取得了至关重要的进球。\n尽管在 270 分钟的出场时间中只打了 159 分钟，但他在小组赛阶段的射门次数比任何其他南非球员都多（8 次）。其中只有一项努力达到了目标——他上次的致胜进球。\n布罗斯不会关心谁在这里交付。南非队过去 11 个世界杯进球是由 11 名不同的球员打进的——那么接下来谁会站出来呢？\n杰西·马什可能知道加拿大队的进球威胁来自哪里。迄今为止，内森·萨利巴在代表加拿大参加的两届世界杯中已经贡献了三个进球（1个进球，2次助攻），而在他的前15场国际比赛中只打进了两个进球。\n马什似乎确实提高了他的球队在门前的表现。加拿大队在小组赛阶段共射正 21 次，几乎是他们前两届世界杯参赛次数总和的两倍（1986 年 6 次，2022 年 5 次）。\n这也转化为目标。加拿大队在前四场世界杯比赛中未能进球，但此后在过去五场比赛中每场至少进球一次。然而，他们在本届赛事（6/10）中的 60% 进球都来自于本届 MD2 比赛中 6-0 战胜九人卡塔尔队的比赛。\n加拿大队也以失败告终，进入淘汰赛。事实证明，在MD3 1-2负于瑞士队的比赛中，诺言大卫的进球只是一个安慰，因为东道主队被挤到B组头名位置。\n尽管这场失利，加拿大队仍以 4 分晋级淘汰赛，这是自 1994 年美国队（同为 4 分）以来世界杯小组赛出线最少的国家。\n不过，美国队在该届淘汰赛第一轮就被巴西队淘汰，马什知道加拿大队不能在这场他们以微弱优势晋级的比赛中失利。"
            ],
            [
                "历史交锋",
                "这只是南非和加拿大之间的第二次会议。\n巴法纳 巴法纳在 2007 年德班的一场友谊赛中以 2-0 获胜。\n令马什担心的是，加拿大在与非洲国家的两场比赛中都输了。\n他们在2001年联合会杯上0-2负于喀麦隆，在2022年卡塔尔世界杯上1-2负于摩洛哥。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机在 90 分钟内就倾向于加拿大获胜：在 25,000 次赛前模拟中，有 56.2% 发生了这种情况。\n南非队在正常比赛中仍有 19.7% 的获胜机会，而平局——这意味着加时赛和可能的点球——占了 24.1% 的情况。\n加拿大晋级的机会为 68.3%，这意味着南非晋级的机会为 31.7%。"
            ]
        ]
    },
    {
        "slug": "brazil-vs-japan-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/brazil-vs-japan-prediction-world-cup-2026-match-preview",
        "home_en": "Brazil",
        "away_en": "Japan",
        "home_cn": "巴西",
        "away_cn": "日本",
        "home_pct": 57.7,
        "draw_pct": null,
        "away_pct": 24.3,
        "insights": [
            "According to the Opta supercomputer, Brazil have a 57.7% probability of winning within 90 minutes; there is also a 24.3% chance this tie goes to extra-time.",
            "Japan have a modest 18% chance of victory inside regulation.",
            "Still seeking their first World Cup knockout win, Japan have only beaten Brazil once across 14 prior meetings (D2 L11), though it was the most recent."
        ],
        "prediction": "Brazil are clear favourites to progress, as the Opta supercomputer’s 25,000 pre-match simulations gave them a 57.3% chance of winning within 90 minutes. Japan’s hopes are rated at just 19.7%; the probability of going to extra-time – or potentially penalties – is 23.0%.",
        "summary_cn": "巴西队显然是晋级的热门球队，Opta 超级计算机的 25,000 次赛前模拟让他们在 90 分钟内获胜的几率为 57.3%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据Opta超级计算机的计算，巴西队在90分钟内获胜的概率为57.7%；这场比赛还有 24.3% 的机会进入加时赛。\n· 日本队在常规赛中获胜的可能性只有 18%。\n· 日本仍在寻求首次世界杯淘汰赛胜利，在之前的 14 场比赛中仅击败过巴西一次（平 2 负 11），尽管这是最近的一次。"
            ],
            [
                "深度分析",
                "巴西队和日本队将在 16 强赛中对阵挪威队和科特迪瓦队，他们将在休斯敦体育场进行一场高风险的德州对决。\n这支南美球队在 C 组中以 1-1 战平摩洛哥、3-0 战胜海地和苏格兰，以小组头名身份进入本阶段。\n卡洛·安切洛蒂的桑巴明星似乎找到了一些节奏，自从第一比赛日早些时候落后以来，他们已经连续七个进球没有回复。\n值得注意的是，巴西上一次在世界杯上连续较长时间连续参赛还要追溯到 2002 年，当时他们最后一次捧起了足坛最令人垂涎的奖杯。\n甚至还有机会重新引进内马尔，这位受伤的前锋981天以来首次身披黄衫出场，并成为第四位参加四届世界杯的巴西人。\n值得注意的是，自 1982 年以来，桑巴军团在每个小组赛阶段都取得了第一名，但在最近的几次比赛中，深入的表现经常被证明超越了他们。\n巴西队在过去六场世界杯淘汰赛中有四场被淘汰——比之前的 17 场比赛更频繁——并且通常会被欧洲对手淘汰。\n然而，自1990年输给宿敌阿根廷以来，他们还没有在首轮淘汰赛中被淘汰。\n这种关系将把两个具有深厚历史和文化联系的国家结合在一起，而不是激烈的竞争对手：世界上最大的日本侨民居住在巴西境内。\n从前桑巴军团球星济科推广新生的 J 联赛，到他的巴西同胞入籍并代表日本国家队，肯定存在着相互尊重。\n然而，这支南美豪门是五届世界冠军，而这只是日本在世界杯上第五次淘汰赛，他们还没有赢过一场。\n运气不好的日本队又遭遇了一场艰难的抽签：他们之前的四个征服者中的三个最终获得了第三名——2002 年的土耳其、2018 年的比利时、2022 年的克罗地亚。\n在此之前，球队在战平荷兰和瑞典的同时又以 4-0 击败突尼斯，守安肇的球队在 F 组获得第二名。\n对阵瑞典，39岁的长友佑都成为首位五次闯入决赛的亚洲选手；现在，守康将备战他的第八场世界杯比赛，这将创下亚洲教练的新纪录。\n在克服了队长远藤渡和球星三兔薰的伤病困扰后，日本队在 10 场比赛中保持不败，其中包括友谊赛战胜巴西队。\n即使久保建英周一仍无法出战，他们也肯定会构成威胁。七个进球已经是他们在世界杯上进球最多的了。\n在本届世界杯上，日本队总共有 10 名球员进球或助攻，这又是一项全国纪录，而 Livewire 前锋上田绫濑（Ayase Ueda）（3 名）已经成为单届世界杯上进球数最多的日本球员。\n但巴西可以以毒攻毒。\n马修斯·库尼亚 (Matheus Cunha) 仅 4 次射门就打入 3 个进球；维尼修斯·儒尼奥尔打进了四粒进球，这是小组赛阶段进球最多的巴西人，与罗纳尔多（2002年）、内马尔（2014年）和雅伊尔津霍（1970年）并列。\n年仅 19 岁零 325 天的拉扬在对阵苏格兰的比赛中无缝替补受伤的拉芬哈，成为为桑巴军团提供世界杯助攻的最年轻球员（自 1966 年有此记录以来）。"
            ],
            [
                "历史交锋",
                "巴西只输给过日本一次（11胜2平），其中包括20年前两人在世界杯上的唯一一场比赛中以4-1获胜。\n然而，日本队唯一的成功发生在最近的一场比赛中，即去年 10 月以 3-2 获胜：巴西队在东京以两球领先，上田为东道主队打进致胜球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "巴西队显然是晋级的热门球队，Opta 超级计算机的 25,000 次赛前模拟让他们在 90 分钟内获胜的几率为 57.3%。\n日本的希望仅为19.7%；进入加时赛或可能受到处罚的概率为 23.0%。"
            ]
        ]
    },
    {
        "slug": "jordan-vs-argentina-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/jordan-vs-argentina-prediction-world-cup-2026-match-preview",
        "home_en": "Jordan",
        "away_en": "Argentina",
        "home_cn": "约旦",
        "away_cn": "阿根廷",
        "home_pct": 8.7,
        "draw_pct": null,
        "away_pct": null,
        "insights": [
            "Jordan have just an 8.7% chance of pulling off an upset, according to the Opta supercomputer’s pre-match simulations.",
            "Along with scoring all of Argentina’s goals at this World Cup (5), Lionel Messi also leads his team for chances created (4), through balls (4), line-breaking passes in the final third (11), completed dribbles (3) and progressive carries (22).",
            "After two games at this World Cup, Argentina (50%) rank third out of the four teams in Group J for average possession, behind Algeria (61%) and Austria (54.4%)."
        ],
        "prediction": "Even if Messi is left out, it is hard to look past Argentina in this match-up. They came out on top in 78.1% of the Opta supercomputer’s 25,000 pre-match simulations. The result was a draw in 13.2% of projections, leaving Jordan with just a 8.7% chance of making history with their first World Cup win.",
        "summary_cn": "即使梅西被排除在外，这场比赛也很难超越阿根廷队。在 Opta 超级计算机的 25,000 次赛前模拟中，他们以 78.1% 的成绩名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的赛前模拟，乔丹爆冷的几率只有 8.7%。\n· 除了打进阿根廷队在本届世界杯上的所有进球（5 球）外，梅西在创造机会（4 球）、直塞球（4 球）、最后三区的突破传球（11 球）、完成带球（3 球）和进步带球（22 球）方面也领先全队。\n· 本届世界杯两场比赛过后，阿根廷队的平均控球率（50%）在J组四支球队中排名第三，落后于阿尔及利亚（61%）和奥地利（54.4%）。"
            ],
            [
                "深度分析",
                "阿根廷可能会选择在达拉斯举行的世界杯 J 组最后一场对阵约旦的比赛中让状态良好的梅西休息。\n2-0战胜奥地利，加上阿尔及利亚2-1战胜约旦，阿根廷锁定J组头名。\n这是卫冕冠军在本届赛事中第二场0比0获胜，他们在首场比赛中还以3-0击败了阿尔及利亚队。他们上一次在世界杯上取得三场胜利并且每次都保持不失球是在1998年。\n梅西在北美的表现非常出色，他打进了阿根廷队的全部 5 粒进球，以 18 粒进球超越米洛斯拉夫·克洛泽，成为世界杯历史上进球最多的球员，尽管凯利安·姆巴佩仅落后他 2 个。\n这位阿尔比塞莱斯特队队长承认他在奥地利比赛后感到疲劳，因此他可能会在对阵已经被淘汰的约旦队时得到休息。\n“我们的想法是给大多数球员一个上场的机会。我认为他们应得的，只要比赛允许，我们就会这样做，”主教练莱昂内尔·斯卡罗尼周四告诉记者。\n梅西周三庆祝了自己的 39 岁生日，如果他出场的话，他将成为同年龄段第二位代表阿根廷队参加世界杯的球员，继 1958 年的安赫尔·拉布鲁纳之后。\n对阵乔丹的进球也使他成为第一位连续七场世界杯比赛进球的球员，超过了贾斯特·方丹（Just Fontaine，1958年）和雅伊尔津霍（Jairzinho，1970年）连续六场比赛进球的纪录。\n即使梅西继续坐在替补席上，阿根廷队仍然有信心能够击败约旦队，因为他们目前在同一主教练的带领下，在世界杯上八场比赛保持不败，是全国最好的成绩。\n克服膝伤的尼科·帕斯被认为是梅西的潜在替代者，而朱利安·阿尔瓦雷斯则有望在劳塔罗·马丁内斯之前获得认可。\n克里斯蒂安·罗梅罗在战胜奥地利一小时后右膝伤势加重，因此没有与球队其他球员一起训练，因此很可能缺席。\n阿尔及利亚队阿明·古里最后时刻的进球让约旦队在上次比赛中被淘汰，但他们渴望以优异的成绩结束他们的首次世界杯决赛。\n贾迈勒·塞拉米的球队在本届世界杯上排名第68位，他们的目标是成为世界杯上击败卫冕冠军的排名最低的球队，超越韩国队在2018年小组赛中以2-0击败德国队时取得的成绩（第57位）。\n“现在，对我们来说，面对阿根廷是一个机会。这是我们表现出色并留下与约旦足球相称的伟大印记的机会，”塞拉米说道。\n乔丹在过去的五场比赛中可能没有赢过任何一场，但他们一直面临着强劲的对手，并且在之前的两场小组赛中进球表明他们仍然可以成为进攻威胁。\n塞拉米拥有完整的阵容，而且两支球队都没有停赛的情况。\n不过，无论谁为阿根廷队首发，毫无疑问都会寻求在淘汰赛阶段获得更多的上场时间。"
            ],
            [
                "历史交锋",
                "这将是约旦和阿根廷在任何比赛中的首次交锋。\n然而，约旦在过去五场对阵南美足联对手的比赛中输掉了四场，最近一次是在 2025 年 10 月对阵玻利维亚的友谊赛中（1-0）。他们对阵南美球队的唯一一场胜利是2004年10月在利比亚举行的友谊赛中以3-0战胜厄瓜多尔。"
            ],
            [
                "赛前预测（Opta 超算）",
                "即使梅西被排除在外，这场比赛也很难超越阿根廷队。在 Opta 超级计算机的 25,000 次赛前模拟中，他们以 78.1% 的成绩名列前茅。\n结果是 13.2% 的预测结果为平局，这使得约旦队创造历史并首次赢得世界杯的机会只有 8.7%。"
            ]
        ]
    },
    {
        "slug": "algeria-vs-austria-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/algeria-vs-austria-prediction-world-cup-2026-match-preview",
        "home_en": "Algeria",
        "away_en": "Austria",
        "home_cn": "阿尔及利亚",
        "away_cn": "奥地利",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 42.1,
        "insights": [
            "Austria only require a point to progress to the World Cup knockout stages for the first time since 1954, and the Opta supercomputer predicts a draw in this one, with a 42.1% likelihood.",
            "Algeria are aiming to win back-to-back matches at the finals for the first time.",
            "However, the Fennecs are without a World Cup win against European opposition in eight attempts (D3 L5)."
        ],
        "prediction": "The Opta supercomputer is leaning towards a draw, which occurred in 42.1% of the 25,000 pre-match simulations. It would be a rare draw as far as Austria are concerned. Among nations to play 15 or more games at the finals, only Hungary (9%) have drawn a lower share of their matches than them (13% – 4/31). Meanwhile, they have played the most World Cup matches without any of them ending in a goalless draw (31).",
        "summary_cn": "Opta 超级计算机倾向于平局，在 25,000 次赛前模拟中，有 42.1% 出现平局。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 奥地利队自 1954 年以来首次晋级世界杯淘汰赛只需要一分，Opta 超级计算机预测本次比赛为平局，可能性为 42.1%。\n· 阿尔及利亚队的目标是首次在决赛中连续两场比赛获胜。\n· 然而，狐狸队在世界杯上八次尝试战胜欧洲对手（D3 L5），但从未取得过胜利。"
            ],
            [
                "深度分析",
                "阿尔及利亚队将在堪萨斯城体育场与奥地利队直接点球大战，争夺 J 组第二名，并有机会在世界杯 32 强赛中对阵西班牙队。\n到目前为止，两支球队几乎经历了平行的战役——都击败了首次亮相的乔丹，但在对阵梅西启发的阿根廷队时表现不佳，后者在还剩一场比赛的情况下锁定了榜首位置。\n奥地利队目前以净胜球优势占据优势，一场平局就足以进入前两名。 1982年，当两支球队在同一小组中垫底时，他们以颇具争议的方式晋级，那一年也是小组最后一场比赛不同时进行的一年，这绝非巧合。\n当时首次亮相的阿尔及利亚队在第二组中积四分，与奥地利和西德队持平，但在最后一场比赛中，西德队以互惠互利的比分 1-0 战胜了西德队，但因净胜球之差而出局。\n这几乎肯定会成为阿尔及利亚队的心头之念，因为他们正在努力第二次进入淘汰赛阶段，而这距离他们在巴西取得这一壮举已经过去了 12 年。\n在第一轮比赛中梅西的帽子戏法之后，弗拉基米尔·佩特科维奇的球队在圣克拉拉以 2-1 逆转战胜了乔丹。这只是他们在决赛中的第四场胜利，也是在之前 10 次尝试失败（平 3 负 7）后丢掉首个进球后的第一场胜利。\n纳迪尔·本布阿利和阿明·古里的进球为阿尔及利亚队完成了逆转，后者成为历史上第一支在同一场世界杯比赛中通过角球攻入两球的非洲球队。\n35岁零121天的里亚德·马赫雷斯成为阿尔及利亚世界杯上最年长的首发球员，这场比赛从很多方面来说对狐狸队来说都是一场具有里程碑意义的比赛，他们在单场比赛中取得了最好的控球总数（72%）、传球尝试次数（641次）和对方禁区触球次数（30次）。他们还追平了单场比赛中射正次数最多的球员（8 次），巧合的是，他们在 44 年前对阵奥地利时创下了这一纪录。\n尽管阿尔及利亚在对阵约旦的比赛中表现出色，但现在他们将面对世界杯上不失角球次数最多的国家——奥地利（19场）。\n奥地利队自1954年以来首次有机会进入比赛的淘汰赛阶段，当时他们在决赛中获得了铜牌，创下了他们的最好成绩。\n不过，要做到这一点，拉尔夫·朗尼克的球队必须在0-2逆转阿根廷队的比赛中做出积极回应——梅西梅开二度，也罚丢了一个点球，而他们自己只能射中一脚球。\n更光明的一面是，这对马塞尔·萨比策来说是历史性的一天，他成为继马尔科·阿诺托维奇（135 场）、大卫·阿拉巴（116 场）、安迪·赫尔佐格（103 场）和亚历山大·德拉戈维奇（100 场）之后第五位代表国家队出场 100 场的奥地利球员，也是第一位在重大赛事（世界杯和欧洲锦标赛）中首发 12 场比赛的球员。\n自朗尼克2022年4月上任以来，萨比策在奥地利各项赛事中参与进球数最多（26个）、射门最多（112次）、创造机会最多（62次）以及首发次数第三多（34场）。这位有影响力的中场球员的经验对于他的国家队寻求延长世界杯赛程至关重要。"
            ],
            [
                "历史交锋",
                "这将是两国之间的第二次交锋，另一次交锋也是在 1982 年世界杯小组赛阶段。\n在那场比赛中，奥地利队以2-0获胜。自11场比赛未尝胜绩以来，他们最近一次在决赛中保持不失球。\n在上一场比赛中，阿尔及利亚队以 2-1 击败西德队，取得了他们在世界杯上对阵欧洲对手的唯一一场胜利，而自那以后，耳廓狐队在八次尝试中都未能取得这样的胜利（平 3 负 5）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机倾向于平局，在 25,000 次赛前模拟中，有 42.1% 出现平局。\n对于奥地利来说，这将是一次罕见的平局。在决赛中打 15 场或以上比赛的国家中，只有匈牙利队 (9%) 的平局比例低于他们 (13% – 4/31)。与此同时，他们参加的世界杯比赛中没有一场以互交白卷告终（31场）。\n奥地利队是两队中稍微更受青睐的球队，他们拿下三分的几率为31.2%。\n阿尔及利亚队从未在世界杯决赛圈连续获胜，而他们在世界杯决赛圈中首次获得连胜的概率为26.7%。"
            ]
        ]
    },
    {
        "slug": "colombia-vs-portugal-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/colombia-vs-portugal-prediction-world-cup-2026-match-preview",
        "home_en": "Colombia",
        "away_en": "Portugal",
        "home_cn": "哥伦比亚",
        "away_cn": "葡萄牙",
        "home_pct": 26.0,
        "draw_pct": 25.1,
        "away_pct": 48.9,
        "insights": [
            "Portugal overcame Colombia and topped Group K in a convincing 48.9% of 25,000 pre-match simulations by the Opta supercomputer.",
            "Colombia could win all three group games at a single World Cup edition for just the second time.",
            "This will be the first meeting between the pair."
        ],
        "prediction": "The Opta supercomputer backed Portugal as the favourites; they won 48.9% of 25,000 pre-match simulations. Colombia boast a 26% chance of victory, though the draw – which would be enough for them to top Group K – accounted for 25.1% of data-led simulations.",
        "summary_cn": "Opta 超级计算机支持葡萄牙队成为夺冠热门；他们在 25,000 次赛前模拟中获胜了 48.9%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在 Opta 超级计算机进行的 25,000 次赛前模拟中，葡萄牙队以 48.9% 的正确率击败了哥伦比亚，夺得 K 组冠军。\n· 哥伦比亚第二次在世界杯上赢得全部三场小组赛胜利。\n· 这将是两人的第一次会面。"
            ],
            [
                "深度分析",
                "葡萄牙和哥伦比亚将于周日在迈阿密交锋，争夺世界杯 K 组头名的位置。\n哥伦比亚队在多场比赛中都取得了两场胜利——分别战胜了乌兹别克斯坦和刚果民主共和国——只需避免失利即可在小组中名列前茅。葡萄牙必须获胜才能获得第一名，尽管无论如何他们的四分很可能足以让他们进入淘汰赛阶段。\n有明显的动机来避免这成为死橡胶。无论谁获得本组第一名，都将面对最好的第三名之一，而第二名将遇到 L 组亚军，即英格兰、加纳或克罗地亚之一。\n尽管罗伯托·马丁内斯的球队在首场比赛中被刚果民主共和国1-1逼平，但在周三鼓舞士气的5-0战胜乌兹别克斯坦后，他们希望占据榜首位置。\n克里斯蒂亚诺·罗纳尔多 (Cristiano Ronaldo) 在 2026 年世界杯的首场比赛中表现不佳，但在上一场比赛中以两个进球做出了有力回应。他在世界杯上的 10 粒进球是葡萄牙历史上进球最多的球员，同时他也是世界上第一个在六次不同的 FIFA 决赛中进球的球员。\n这位 41 岁的球员现在的目标是自 2018 年俄罗斯世界杯第一和第二比赛日以来首次在世界杯连续比赛中进球。考虑到前两场比赛后只有埃尔林·哈兰德（2.7）和乔纳森·大卫（2.4）的非点球预期进球比罗纳尔多的 2.1 更高，机会应该会再次出现。\n马丁内斯可能很高兴看到他的两名关键球员联手，布鲁诺·费尔南德斯助攻罗纳尔多在 MD2 上攻入第一个进球。前两场比赛后，只有西班牙球员罗德里（9次）的突破防线传球次数比费尔南德斯（7次）多，而只有费利克斯·恩梅查和迈克尔·奥利塞（3次）的突破防线传球次数比他的两人多。\n不出所料，费尔南德斯、若奥·内维斯和维蒂尼亚对于马丁内斯想要如何踢球和控制中场战斗至关重要。在前两个比赛日中，只有西班牙（55 次）在开放比赛中至少 10 次传球的次数多于葡萄牙（49 次）。\n这支中场三人组也有助于推动球队的防守——葡萄牙在前两个比赛日的每次防守动作允许传球率 (PPDA) 最低 (6.8)。这表明马丁内斯在他的球队试图以高强度的压力从前场施压的过程中得到了调整，尽管面对的是乌兹别克斯坦和刚果民主共和国的低质量对手。\n内斯托尔·洛伦佐将坚持要求他的哥伦比亚队以类似的意图进行高位逼抢。他们的 11 次高失误中有 4 次导致射门（36.4%），在前两场比赛中，失误率排名第三，仅次于海地（5/9 - 55.6%）和乔丹（3/8 - 37.5%）。\n葡萄牙还必须留意丹尼尔·穆尼奥斯，他在首场比赛中以3-1战胜乌兹别克斯坦，并在1-0战胜刚果民主共和国的比赛中攻入制胜球。詹姆斯·罗德里格斯是唯一一位在世界杯小组赛三场比赛中都取得进球的哥伦比亚人，12 年前在巴西就曾取得过这样的成绩。\n罗德里格斯继续为国家队做出贡献。这位34岁的球员在上一场比赛中创造了5次机会，这是自1998年卡洛斯·巴尔德拉马（Carlos Valderrama）在对阵英格兰队时创造了5次机会以来，哥伦比亚球员在世界杯比赛中创造的最多机会。\n如果哥伦比亚想要第二次在单一赛事中赢得世界杯小组赛的全部三场比赛，穆尼奥斯、罗德里格斯和路易斯·迪亚斯可能会再次发挥关键作用。此前，他们在 2014 年闯入八强的过程中也曾这样做过。\n但葡萄牙将是一个严峻的考验。他们在世界杯之前的 17 场小组赛中只输了两场（9 胜 6 平）——2014 年 MD1 比赛中 4-0 输给德国队，四年前 MD3 比赛中 2-1 输给韩国队。"
            ],
            [
                "历史交锋",
                "这将是哥伦比亚和葡萄牙之间的首次交锋。\n哥伦比亚在过去三场世界杯对阵欧足联球队的比赛中保持不败（W2 D1），不包括点球大战。\n然而，葡萄牙队在小组赛对阵南美洲球队的三场比赛中也保持不败（2胜1平）。\n哥伦比亚将是继巴西和乌拉圭之后葡萄牙在世界杯上遇到的第三个不同的南美对手。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持葡萄牙队成为夺冠热门；他们在 25,000 次赛前模拟中获胜了 48.9%。\n哥伦比亚拥有 26% 的获胜机会，尽管平局（这足以让他们在 K 组中名列前茅）占数据主导模拟的 25.1%。"
            ]
        ]
    },
    {
        "slug": "croatia-vs-ghana-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/croatia-vs-ghana-prediction-world-cup-2026-match-preview",
        "home_en": "Croatia",
        "away_en": "Ghana",
        "home_cn": "克罗地亚",
        "away_cn": "加纳",
        "home_pct": 56.3,
        "draw_pct": 26.2,
        "away_pct": 17.6,
        "insights": [
            "The Opta supercomputer expects Croatia to have a significant impact on the final standings in Group L, with Zlatko Dalic’s side winning an overwhelming 56.3% of the pre-match simulations.",
            "Croatia have only lost one of their last eight group-stage games at the World Cup – a 4–2 defeat by England in their 2026 opener – keeping five clean sheets during this run.",
            "After only keeping two clean sheets in 15 World Cup games prior to 2026, Ghana have two from two so far at this year’s finals. In World Cup history, no African nation has ever kept three clean sheets at this stage of a tournament."
        ],
        "prediction": "From 25,000 pre-match simulations, Dalić’s side came out on top in 56.3% of the outcomes, implying Croatia are highly likely to finish their group stage campaign on the front foot. Ghana’s win rating stands at just 17.6% by comparison, and with a draw seen as even likelier at 26.2%, victory against the 2018 finalists could prove to be a tall order for Quieroz’s charges.",
        "summary_cn": "根据 Opta 超级计算机的数据，尽管落后加纳一分，并且为被黑星队成功淘汰的英格兰队打进了四个进球，但克罗地亚仍然是这场比赛的压倒性获胜热门。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计克罗地亚将对 L 组的最终排名产生重大影响，Zlatko Dalic 的球队在赛前模拟中以 56.3% 的压倒性优势获胜。\n· 克罗地亚在过去八场世界杯小组赛中只输掉了一场——2026 年揭幕战中以 4-2 负于英格兰——在这轮比赛中保持了 5 场不失球。\n· 加纳在 2026 年之前的 15 场世界杯比赛中只保持了 2 场不失球，而今年的决赛迄今为止，加纳已经取得了两场零失球的成绩。在世界杯历史上，还没有任何非洲国家在本届赛事中保持过三场不失球。"
            ],
            [
                "深度分析",
                "克罗地亚和加纳在最近几届世界杯上的表现都远远超出了他们的实力，随着 2026 年世界杯的淘汰赛阶段的到来，这场 L 组的决胜局有很多利害关系。\n英格兰队在首场比赛中以 4-2 战胜克罗地亚队，在 L 组中领先，但瓦特雷尼队在上一场对阵巴拿马队的比赛中反弹，凭借安特·布迪米尔第 54 分钟的进球取得了本届赛事的首场胜利。\n在马丁·巴图林纳和佩塔尔·穆萨对阵三狮军团的扳平球被证明是徒劳之后，克罗地亚重回正轨，在L组排名第三，落后于在波士顿0-0战平的英格兰和加纳。\n半场替补出场的布迪米尔以34岁零336天的年纪，成为克罗地亚队历史上年龄最大的世界杯进球者，打破了伊维察·奥利奇在2014年对阵喀麦隆队时创下的纪录。\n克罗地亚队长卢卡·莫德里奇也第 21 次参加世界杯。自 2006 年首次亮相锦标赛以来，只有克里斯蒂亚诺·罗纳尔多（24 岁）和莱昂内尔·梅西（28 岁）比这位 40 岁的球员出场次数更多，后者第 200 次代表国家队出场。\n如果本场比赛首发，莫德里奇和佩里西奇将成为首位在世界杯上首发20场的克罗地亚人；此前只有三个国家曾有多名球员在世界杯上首发超过 20 场比赛——德国（5 名）、阿根廷（3 名）和波兰（2 名）。\n然而，在战胜巴拿马的比赛中，克罗地亚队只射门六次，只有两次射正——这是他们在世界杯比赛中射门次数（总数和射正次数）最少的球队，但他们仍然赢得了胜利。\n这对加纳队来说将是美妙的音乐，他们在上一场0-0战平英格兰队的比赛中处处挫败英格兰队，并在首场比赛1-0击败巴拿马队后连续第二次不失球。\n因此，卡洛斯·基耶罗斯的球队以四分的成绩与英格兰队并列 L 组榜首，如果他们能够在对阵巴拿马的比赛中取得更好的成绩，那么他们将获得小组第一，并在最后 32 场比赛中取得有利的平局。\n马文·塞纳亚 (Marvin Senaya) 在对阵英格兰队的比赛中以 7 次铲球领先，这是加纳球员在单场世界杯比赛中铲断次数最多的球员，而门将本杰明·阿萨雷 (Benjamin Asare) 仅被迫做出了 3 次扑救。\n自2002年小组赛对阵尼日利亚时，英格兰队尝试了25次射门，但没有成功，因此英格兰队在世界杯比赛中射门19次，但没有进球。\n加纳队对阵巴拿马队的进球球员凯莱布·伊伦基 (Caleb Yirenkyi) 尽管早早收到黄牌，但还是踢了 90 分钟，而乔丹·阿尤 (Jordan Ayew) 则施加了 71 次高强度施压，这是本届世界杯单场比赛中第二多的球员。\n在执教葡萄牙、伊朗和现在的加纳期间，奎罗兹在 15 场世界杯比赛中只打进 29 球（进球 15 球，失球 14 球），平均每场进球 1.93 个。这是在赛事中出场 10 场以上的主教练中第二低的比率，仅次于斯文-戈兰·埃里克森（1.85 - 13 场比赛中 24 场）。\n就目前情况而言，克罗地亚队的三分足以确保作为最好的第三名球队之一进入最后32强，尽管达利奇的球队将在下一轮面对K组领头羊哥伦比亚。\n加纳只需要一场平局就能锁定L组第二名，但考虑到他们目前正在为32强对阵葡萄牙的比赛做好准备，黑星队不想让自己的命运听天由命。"
            ],
            [
                "历史交锋",
                "这将是这两个国家之间的首次交锋，加纳目前在国际足联全球排名中排名第 65 位，成为世界杯上对阵克罗地亚排名第二低的球队，仅次于 2018 年的俄罗斯（第 70 位）。\n克罗地亚队从未在世界杯比赛中输给过排名第40位或更低的球队，并且在世界杯对阵非洲球队的四场比赛中也保持不败——赢了3场，打进8球，只丢1球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "根据 Opta 超级计算机的数据，尽管落后加纳一分，并且为被黑星队成功淘汰的英格兰队打进了四个进球，但克罗地亚仍然是这场比赛的压倒性获胜热门。\n在 25,000 次赛前模拟中，达利奇的球队在 ​​56.3% 的结果中名列前茅，这意味着克罗地亚很有可能以领先优势结束小组赛阶段的比赛。\n相比之下，加纳队的胜率仅为 17.6%，而平局的可能性甚至高达 26.2%，对奎罗兹的指控来说，战胜 2018 年决赛选手可能是一项艰巨的任务。"
            ]
        ]
    },
    {
        "slug": "panama-vs-england-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/panama-vs-england-prediction-world-cup-2026-match-preview",
        "home_en": "Panama",
        "away_en": "England",
        "home_cn": "巴拿马",
        "away_cn": "英格兰",
        "home_pct": 84.1,
        "draw_pct": null,
        "away_pct": 81.0,
        "insights": [
            "England have an 81.0% chance of victory according to the Opta supercomputer, and an 84.1% chance of finishing first in Group L.",
            "After 25,000 pre-match simulations, Panama emerged with just a 8.9% probability of claiming their first World Cup win.",
            "England have only lost the third group game in one of their last 14 World Cup appearances (W8 D5) – to Belgium in 2018."
        ],
        "prediction": "England are huge favourites to leave New Jersey with maximum points, as the Opta Supercomputer’s 25,000 pre-match simulations suggest they have a 81.0% chance of success.",
        "summary_cn": "英格兰队是以最高分离开新泽西队的大热门，因为 Opta 超级计算机的 25,000 次赛前模拟表明他们有 81.0% 的成功机会。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，英格兰队获胜的几率为 81.0%，获得 L 组第一名的几率为 84.1%。\n· 经过 25,000 次赛前模拟，巴拿马队赢得世界杯首场胜利的概率仅为 8.9%。\n· 英格兰队在过去 14 场世界杯比赛中只输过一场小组赛第三场比赛（8 胜 5 平）——2018 年输给了比利时。"
            ],
            [
                "深度分析",
                "L组领头羊英格兰队的目标是在新泽西迎战已经被淘汰的巴拿马队时夺得头名。\n三狮军团在周二0比0战平加纳的比赛中表现并不令人信服，但仍然是小组冠军的热门球队。\n如果他们获胜并且黑星队没有通过击败克罗地亚来扭转一球的差距，那么托马斯·图赫尔的奖杯猎人将完成他们任务的第一部分。\n然而，如果他们出现失误，英格兰可能会失去通过淘汰赛阶段的一条更友好的路线。\n在 4-2 战胜克罗地亚的下半场比赛中，图赫尔的球队无法将统治地位转化为更多进球，在第二轮比赛中，人们熟悉的沮丧故事上演了。\n直到第 86 分钟，尼科·奥莱利 (Nico O’Reilly) 击中横梁，队长哈里·凯恩 (Harry Kane) 一反常态地抢到了篮板。\n英格兰队的19次射门是24年来世界杯上最多的一次没有进球；与此同时，加纳的两场比赛是三狮军团自 1966 年有此类记录以来所面对的最少的。\n英格兰队的控球率也高达 78.9%，这是世界杯历史上（也是自 1966 年以来）最终未能进球的球队中最高的控球率。\n不过，我们几乎没有时间反思或沉思——一场潜在的马拉松式竞选活动必须继续下去。\n尽管英格兰队在世界杯上唯一输给中北美洲及加勒比海地区对手的那场比赛仍然是臭名昭著的1950年输给美国业余队的比赛，但巴拿马队甚至还没有拿到一分。\n因此，可以公平地说，本周末历史将向中美洲不利。\n洛斯卡纳莱罗斯队第二次参加国际足联顶级赛事；他们在 2018 年小组垫底，三场比赛全部失利，丢了 11 个球，其中对阵英格兰队时丢了 6 个球。\n今年夏天，人们的希望更大了，托马斯·克里斯蒂安森带领他们打进了 2023 年金杯决赛，然后是美洲杯淘汰赛，然后进入了去年的中北美洲及加勒比海国家联赛决胜局。\n然而，在多伦多的连续失利已经终结了任何进步的希望。\n巴拿马队以0比1输给加纳队和克罗地亚队，成为第六个在世界杯前五场比赛中失利的国家。\n尽管接受过巴塞罗那青训学院的训练，克里斯蒂安森还是一位实用主义者——在前两个比赛日中，没有一支球队的比赛射门次数少于（32次）——他的球队将在周六再次形成顽固的低挡。\n巴拿马几乎没有什么武器可以突破英格兰的防线，但阿米尔·穆里略在中北美洲及加勒比海地区预选赛中的助攻数排名第四，并在对阵克罗地亚的比赛中尝试了全队最高的三脚射门。\n到目前为止，他们已经在老将前锋塞西利奥·沃特曼和何塞·法哈多之间切换。对于英格兰队来说，轮换凯恩是一个大胆的举动，凯恩曾在2018年对阵巴拿马队的比赛中上演帽子戏法。\n然而，随着淘汰赛的临近，这可能是最后的可行机会。奥利·沃特金斯和伊万·托尼都是能干的副手。\n图赫尔可能会再次调整，因为他在周二选秀了杰德·斯彭斯和马克·盖伊，但在让定位球专家德克兰·赖斯休息之前，他会三思而后行，后者已经创造了10次机会——是前两场比赛中创造机会最多的人。里斯·詹姆斯在右后卫位置上也存在疑问。"
            ],
            [
                "历史交锋",
                "两人此前唯一一次交锋是在 2018 年俄罗斯世界杯上，当时英格兰队以 6-1 取得了世界杯迄今为止最大的胜利。\n凯恩不仅上演了帽子戏法，成为继杰夫·赫斯特（1966 年决赛）和加里·莱因克尔（1986 年）之后唯一在世界杯上上演帽子戏法的英国人，而且约翰·斯通斯也帮助自己梅开二度。"
            ],
            [
                "赛前预测（Opta 超算）",
                "英格兰队是以最高分离开新泽西队的大热门，因为 Opta 超级计算机的 25,000 次赛前模拟表明他们有 81.0% 的成功机会。\n与此同时，巴拿马队最终获得世界杯首胜的机会为 6.9%；首次得分的概率仅为 12.1%。"
            ]
        ]
    },
    {
        "slug": "new-zealand-vs-belgium-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/new-zealand-vs-belgium-prediction-world-cup-2026-match-preview",
        "home_en": "New Zealand",
        "away_en": "Belgium",
        "home_cn": "新西兰",
        "away_cn": "比利时",
        "home_pct": 6.9,
        "draw_pct": 12.1,
        "away_pct": 81.0,
        "insights": [
            "The Opta supercomputer expects Belgium to win this one; they came out on top in a convincing 81.0% of 25,000 pre-match simulations.",
            "Belgian players have had 69 shots at the World Cup since last scoring in 2022.",
            "New Zealand are yet to win at the finals in eight attempts."
        ],
        "prediction": "The Opta supercomputer ran 25,000 pre-match simulations of this clash, and Belgium won a massive 81.0% of them. New Zealand achieved a first World Cup victory in only 6.9% of data-led simulations, while the draw accounted for 12.1% of scenarios.",
        "summary_cn": "Opta 超级计算机对这场比赛进行了 25,000 次赛前模拟，比利时队赢得了其中 81.0% 的胜利。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计比利时将赢得这场比赛；在 25,000 次赛前模拟中，他们以 81.0% 的准确率名列前茅。\n· 自2022年上次进球以来，比利时球员在世界杯上已经射门69次。\n· 新西兰队在八次尝试决赛中尚未获胜。"
            ],
            [
                "深度分析",
                "比利时队周六在温哥华迎战新西兰队，无法再承受世界杯上的再次失误。\n鲁迪·加西亚的球队在 ​​G 组的多场比赛中只得到两分，使他们排名第三，但晋级权掌握在自己手中。在 BC Place 取得胜利将确保进入前两名。\n尽管连续与埃及和伊朗战平，Opta 的现场锦标赛预测仍然认为他们进入淘汰赛阶段的机会为 92.2%。\n尽管内森·恩戈伊下半场被红牌罚下，但在周日0-0战平伊朗的比赛中，10人的比利时队仍有23次射门不成功。这是自 1994 年对阵沙特阿拉伯队（28 场）以来，他们在世界杯比赛中最多没有进球的一次，而且这种挥霍的趋势已经变得普遍。\n在本届世界杯和四年前的上一届世界杯上，比利时在五场比赛中仅进了两个进球。其中之一是埃及队的穆罕默德·哈尼在首场1-1战平的比赛中打进的乌龙球。\n比利时球员在这两项赛事中总共射门 73 次，其中只有米奇·巴舒亚伊在 2022 年对阵加拿大的比赛中进球。自上次进球以来，他们已经有 69 次射门，其中凯文·德布劳内参与了其中的 40%（16 次射门，创造了 12 次机会）。\n对于加西亚的球队来说，这也不全是坏消息，他们在各项赛事15场比赛中保持不败（9胜6平）。比利时队仅在2016年9月至2018年7月期间连续24场比赛保持不败，之后在俄罗斯世界杯上输给了法国队。\n蒂博·库尔图瓦也可能打破比利时队第 18 次闯入决赛的记录，超越恩佐·西福 (Enzo Scifo) 的 17 次闯入决赛。只有彼得·希尔顿和法比安·巴特兹（各 10 场）比库尔图瓦的 8 场不失球次数还要多。\n新西兰队1-3不敌小组头名埃及队，仅积1分。芬·苏尔曼 (Finn Surman) 的头球破门为达伦·贝兹利 (Darren Bazeley) 的球队带来了良好的开局，但穆罕默德·萨拉赫 (Mohamed Salah) 和穆斯塔法·济科 (Mostafa Zico) 很快就抢尽了风头，让全白队有了一种非常熟悉的感觉。\n他们在八场世界杯比赛中取得了三场领先，但没有一场获胜。 （D2 L1）。新西兰队是第二支在他们领先的前三场世界杯比赛中未能获胜的球队，另外保加利亚队在前六场此类比赛中均未能获胜。\n根据Opta超级计算机的数据，再一次翻盘失利使得新西兰队进入32强的机会只有7.0%，贝泽利迫切需要他的球队在全球舞台上取得第一场胜利。\n他们在世界杯前八场比赛（平4负4）后仍然没有取得胜利，只有洪都拉斯队（9平3平6）在决赛中打了更多场比赛但没有取得胜利，但任何不太可能获胜的希望都可能建立在后防线的改进上。\n新西兰队在 8 场世界杯比赛中，有 5 场至少丢了 2 个球（62.5%），1982 年的全部三场小组赛和 2026 年的两场小组赛都丢了两个球。在参加至少 8 场比赛的国家中，只有科特迪瓦在比赛中丢球数更高（7/11，63.6%）。"
            ],
            [
                "历史交锋",
                "这将是两人之间的第一次会面。\n然而，新西兰在最近两场世界杯对阵欧洲对手的比赛中保持不败。\n2010年在南非举行的锦标赛上，他们分别1-1战平斯洛伐克和意大利。\n与此同时，比利时可能成为自1998年以来第一支在世界杯小组赛三场比赛中全部打平的欧洲球队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机对这场比赛进行了 25,000 次赛前模拟，比利时队赢得了其中 81.0% 的胜利。\n在以数据为主导的模拟中，新西兰队取得世界杯首胜的比例仅为 6.9%，而平局则占 12.1%。"
            ]
        ]
    },
    {
        "slug": "uruguay-vs-spain-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/uruguay-vs-spain-prediction-world-cup-2026-match-preview",
        "home_en": "Uruguay",
        "away_en": "Spain",
        "home_cn": "乌拉圭",
        "away_cn": "西班牙",
        "home_pct": 15.7,
        "draw_pct": 21.9,
        "away_pct": 62.4,
        "insights": [
            "Spain are heavy favourites to win this one, with the Opta supercomputer giving Luis de la Fuente’s side a dominant 62.4% chance of winning to Uruguay’s 15.7%.",
            "Saturday’s contest will mark the third World Cup meeting between Uruguay and Spain, and their first since a goalless draw in Udine in the group stages of Italia ‘90.",
            "La Celeste have won just one of their last nine World Cup matches played in Mexico (D3 L5) – a 1-0 extra-time win over the USSR in the quarter-finals in 1970."
        ],
        "prediction": "The Opta supercomputer could not look past a Spain win, with the reigning European champions coming out on top in a whopping 62.4% of the 25,000 pre-match simulations. Uruguay took three points just 15.7% of the time, while the match ended in a draw in 21.9% of the simulations.",
        "summary_cn": "Opta 超级计算机无法忽视西班牙队的胜利，在 25,000 次赛前模拟中，卫冕欧洲冠军队以 62.4% 的准确率名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 西班牙队是这场比赛的最大热门，Opta 超级计算机让路易斯·德拉富恩特的球队获胜的几率为 62.4%，而乌拉圭队的获胜几率为 15.7%。\n· 周六的比赛将是乌拉圭和西班牙之间的第三次世界杯交锋，也是自90年意大利小组赛乌迪内0-0战平之后的第一次交锋。\n· 拉塞莱斯特队过去九场在墨西哥举行的世界杯比赛中只赢了一场（平3负5）——1970年四分之一决赛中加时赛1-0战胜苏联。"
            ],
            [
                "深度分析",
                "在今年世界杯的第一场比赛之前，很少有人会预料到 H 组的比赛会如此展开，乌拉圭队将于周五在瓜达拉哈拉迎战西班牙队，这是该组的重量级比赛。\n马塞洛·贝尔萨的球队在今年夏天的比赛中被沙特阿拉伯和佛得角逼平，他们本可以赢，而且很有可能赢。\n他们的首场比赛与沙特阿拉伯的平局似乎是一个短暂的短暂事件，但拉塞莱斯特队随后在第二场比赛中被首次亮相的佛得角队令人震惊地逼平，凯文·皮纳的精彩任意球抢尽了头条，随后赫利奥·巴雷拉取消了阿古斯丁·卡诺比奥的进球。\n乌拉圭队将竭力避免再次出现类似的结果，在2002年至2010年的世界杯上，乌拉圭队连续三场战平之前只有一次。\n虽然他们在2022年的小组赛中被淘汰，但他们连续几届世界杯都未能进入淘汰赛，这让贝尔萨的球队还有很多工作要做。\nOpta超级计算机目前给他们晋级下一轮的概率为36.4%，这与已经获得出线资格并获得H组冠军的概率为84.7%的西班牙形成鲜明对比。\n让乌拉圭的处境变得更加艰难的是他们在墨西哥的战绩。他们在过去的九场世界杯比赛中只赢了一场（平3负5）——1970年四分之一决赛中通过加时赛以1-0战胜苏联。\n与此同时，西班牙在 4-0 战胜沙特阿拉伯的比赛中以某种方式消除了锈迹。\n拉明·亚马尔首开纪录，米克尔·奥亚扎瓦尔快速打进两球，随后哈桑·阿尔坦巴克蒂的乌龙球锁定胜局。\n因此，路易斯·德拉富恩特对他的球队在瓜达拉哈拉取得好成绩充满信心，西班牙队在 1986 年至 2014 年间的每届世界杯小组赛最后一场比赛中都取得了胜利。\n然而，西班牙队在过去两届比赛中都未能做到这一点，2018年2-2战平摩洛哥，2022年1-2负于日本。\n西班牙队在过去三场世界杯比赛中均保持零失球，如果他们能够将乌拉圭队排除在外，那么他们可以不失球地进入整个小组赛阶段。\n事实上，他们在 21 世纪的世界杯比赛中有 48% 保持不失球（14/29）。在此期间参加过不止一场比赛的球队中，没有哪支球队的比率更高。\n他们在过去四场世界杯比赛中仅遭遇 21 次射门，其中对阵沙特阿拉伯时射门 3 次，对阵佛得角、摩洛哥和日本时各射门 6 次。\n自 1966 年以来，唯一一支在连续五场世界杯比赛中遭遇 6 次或更少射门的球队是卫冕冠军阿根廷队，他们在赢得 2022 年世界杯的前五场比赛中都做到了这一点。\n这种防守的稳固性可能会让乌拉圭时好时坏的进攻陷入困境。\n在对阵沙特阿拉伯的比赛中，贝尔萨的球队10次射正只有1次进球，而对阵佛得角的比赛中，贝尔萨的球队两次射正均取得进球，他们需要同样的效率才能击败西班牙。\n不过，他们要警惕的最大威胁之一是亚马尔，他在对阵沙特阿拉伯的比赛中攻入一球，以 18 岁零 343 天成为世界杯历史上第八年轻的进球者。\n如果这位巴塞罗那球员在瓜达拉哈拉进球，他将成为 1958 年继贝利之后唯一一位连续参加世界杯进球的青少年球员。"
            ],
            [
                "历史交锋",
                "乌拉圭和西班牙将于周六在世界杯上第三次相遇，他们上一次在大舞台上相遇已经是三十多年前了。\n他们最近一次交锋是在 1990 年意大利乌迪内世界杯小组赛阶段，双方互交白卷。\n两国之间唯一的另一场比赛是 1950 年世界杯最后一轮，他们在圣保罗以 2-2 战平。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机无法忽视西班牙队的胜利，在 25,000 次赛前模拟中，卫冕欧洲冠军队以 62.4% 的准确率名列前茅。\n乌拉圭获得三分的概率仅为 15.7%，而比赛以平局结束的概率为 21.9%。"
            ]
        ]
    },
    {
        "slug": "cape-verde-vs-saudi-arabia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/cape-verde-vs-saudi-arabia-prediction-world-cup-2026-match-preview",
        "home_en": "Cape Verde",
        "away_en": "Saudi Arabia",
        "home_cn": "佛得角",
        "away_cn": "沙特阿拉伯",
        "home_pct": 38.0,
        "draw_pct": null,
        "away_pct": 35.8,
        "insights": [
            "Cape Verde are considered slight favourites by the Opta supercomputer for this fixture, with a win probability of 38.0% to Saudi Arabia’s 35.8%.",
            "Cape Verde faced 44 shots across their opening two games at the World Cup, but just nine of those were on target.",
            "Saudi Arabia have conceded 49 goals in 21 World Cup games."
        ],
        "prediction": "",
        "summary_cn": "由于两支球队仍然有很大的机会进入下一轮，因此根据 Opta 超级计算机的数据，两支球队几乎没有什么区别也就不足为奇了。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为佛得角在这场比赛中稍有优势，获胜概率为 38.0%，沙特阿拉伯为 35.8%。\n· 佛得角在世界杯的前两场比赛中遭遇了 44 次射门，但其中只有 9 次射正。\n· 沙特阿拉伯队在 21 场世界杯比赛中丢了 49 个球。"
            ],
            [
                "深度分析",
                "人口约 53 万的佛得角迄今为止在世界杯上的表现非常出色，首场比赛是与重量级球队西班牙队互交白卷。\n布比斯塔的球队随后以2-2战平乌拉圭，凯文·皮纳(Kevin Pina)为球队取得领先，在马克西米利亚诺·阿劳霍(Maximiliano Araújo)和阿古斯丁·卡诺比奥(Agustín Canobbio)帮助乌拉圭2-1领先后，赫利奥·巴雷拉(Hélio Varela)替补出场扳平比分。\n巴雷拉在替补出场后仅 136 秒就进球了，这是当时世界杯历史上非洲球员替补进球第二快的进球，仅次于 1994 年对阵俄罗斯队的罗杰·米拉（84 秒）。\n佛得角在世界杯的前两场比赛中遭遇了 44 次射门，但其中只有 9 次射正。他们在MD1对阵西班牙的比赛中保持不失球，同时面临7次射门机会，但在MD2对阵乌拉圭的比赛中，他们两次射正都失球。\n蓝鲨队可能成为继喀麦隆（1982年3胜）和塞内加尔（2002年1胜2平）之后第三个首次参加世界杯就在小组赛中保持不败的非洲国家队。\n此外，如果他们与沙特阿拉伯再次陷入僵局，他们可能会加入威尔士（1958年）、喀麦隆（1982年）和爱尔兰共和国（1990年）的行列，成为仅有的前三场比赛均战平的国家。\n沙特阿拉伯也盯上了32强。他们在首场比赛中1-1战平乌拉圭，但在MD2中0-4被复兴的西班牙队击败。\n拉明·亚马尔第 10 分钟的首开纪录奠定了基调，米克尔·奥亚扎瓦尔的梅开二度让西班牙队控制住了局面，随后哈桑·阿尔坦巴克蒂的乌龙球完成了一场悲惨的比赛。\n沙特阿拉伯在 1994 年世界杯前三场比赛中赢得了两场（L1），但在随后的 18 场比赛中只赢了两场（D3 L13）。\n绿猎鹰队在参加的 21 场世界杯比赛中打进了 49 个进球，并且在过去 18 场比赛中未能保持不失球。世界杯历史上仅有的在 22 场或更少的比赛中丢掉 50 个球的球队是墨西哥（21 场）、韩国（22 场）和瑞士（22 场）。\n自 1966 年（Opta 记录开始）以来，沙特阿拉伯在世界杯上的射门次数（221 次）和面对射门次数（423 次）之间的差距最大（-202）。在 2026 年世界杯上，他们的射门次数为 49 次，而回击球只有 10 次。\n塞勒姆·阿尔·道萨里 (Salem Al Dawsari) 有望在这场比赛中第九次参加世界杯，这将是沙特阿拉伯队在本届世界杯上并列第二多的球员，仅次于穆罕默德·阿尔·德亚 (Mohammed Al-Deayea)（10 次）。"
            ],
            [
                "历史交锋",
                "这场H组比赛实际上标志着佛得角和沙特阿拉伯队首次交锋。\n沙特阿拉伯在此前五场世界杯对阵非洲对手的比赛中只输了一场，两胜两平，其中唯一的一场失利是在2002年0-1不敌喀麦隆的比赛中。\n佛得角将是沙特阿拉伯在世界杯上遇到的第六个非洲足联对手。\n他们此前曾在非洲足联对阵过摩洛哥、南非、喀麦隆、突尼斯和埃及。"
            ],
            [
                "赛前预测（Opta 超算）",
                "由于两支球队仍然有很大的机会进入下一轮，因此根据 Opta 超级计算机的数据，两支球队几乎没有什么区别也就不足为奇了。\n佛得角以微弱优势获胜，获胜概率为 38.0%。然而，沙特阿拉伯获胜的概率为 35.8%，而平局的概率为 26.1%。\n就整体比赛而言，佛得角实际上仍有小组出线的希望（尽管微乎其微）（2.7%）。人们认为这支小鱼队能够进入淘汰赛阶段的可能性为 63.9%，而赢得锦标赛的可能性微乎其微，只有 0.04%。\n沙特阿拉伯队上次输给西班牙队意味着他们无法小组第一，但他们确实有34.6%的机会进入32强。他们夺冠的希望比佛得角更渺茫，为0.03%。"
            ]
        ]
    },
    {
        "slug": "norway-vs-france-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/norway-vs-france-prediction-world-cup-2026-match-preview",
        "home_en": "Norway",
        "away_en": "France",
        "home_cn": "挪威",
        "away_cn": "法国",
        "home_pct": null,
        "draw_pct": null,
        "away_pct": 59.4,
        "insights": [
            "France have a win probability of 59.4% against Norway, making them the Opta supercomputer’s favourites.",
            "Norway have created 10 big chances at this World Cup, the most of any team in Group I and already one more than they managed in their previous participation (nine in 1998).",
            "This will be the first men’s World Cup meeting between Norway and France."
        ],
        "prediction": "Les Bleus won 59.4% of the 25,000 pre-match simulations, while 20.6% of them ended in a draw – a result that would be enough for France to top the group.",
        "summary_cn": "由于挪威可能会做出一些改变，因此 Opta 超级计算机选择法国作为最爱也就不足为奇了。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 法国队对挪威队的获胜概率为 59.4%，这使他们成为 Opta 超级计算机的最爱。\n· 挪威队在本届世界杯上创造了 10 次绝佳机会，是第一组中最多的球队，并且比上届世界杯​​（1998 年 9 次）多了 1 次。\n· 这将是挪威和法国之间的首次男子世界杯交锋。"
            ],
            [
                "深度分析",
                "周五，埃尔林·哈兰德和基利安·姆巴佩将在波士顿进行国际足联世界杯第一组的争夺，挪威队和法国队将展开对决。\n哈兰德和姆巴佩很快就与莱昂内尔·梅西一起成为世界杯历史上最伟大的金靴争夺战之一的中心人物。\n继上届3-2战胜塞内加尔的比赛中，挪威球星哈兰德在对阵伊拉克的比赛中攻入两球后，挪威球星哈兰德可能成为世界杯历史上第三位在前三场比赛中每场都攻入两球或以上的球员。仅有的其他实现这一壮举的球员是 1930 年的阿根廷选手吉列尔莫·斯塔比尔 (Guillermo Stabile) 和 1954 年的匈牙利选手桑多尔·科奇斯 (Sándor Kocsis)。\n姆巴佩还在上一场比赛中梅开二度——3-0战胜伊拉克，其中包括因暴风雨而休息130分钟——在16场世界杯比赛中打进了令人难以置信的16球，追平了米罗斯拉夫·克洛泽在世界杯历史进球榜上的纪录。\n克洛泽在本赛季保持着全胜纪录，但梅西在两场代表阿根廷队出场的比赛中打入 5 粒进球，使他超越了这位前德国前锋，达到了 18 粒进球——这是姆巴佩的新目标。\n这一切都意味着，尽管法国和挪威已经晋级32强，但这场比赛——天气预报显示这场比赛也可能受到暴风雨的影响——还远未结束。\n除了哈兰德和姆巴佩等人的个人奖项之外，各队在进入比赛时都知道胜利者将在32强赛中与第三名球队会面。亚军将获得E组第二名的球队，这支球队很可能是科特迪瓦或厄瓜多尔。\n不过，法国队主教练迪迪埃·德尚将缺席，法国足协确认，在他母亲去世后，他已被允许回国参加葬礼。在他缺席期间，助理教练盖伊·史蒂芬将带领球队。\n如果斯蒂芬能够带领法国队战胜挪威队，这将是法国队在世界杯历史上第二次赢得全部三场小组赛比赛。他们上一次夺冠是在 1998 年，当时他们在家乡捧起了奖杯。\n与此同时，挪威队在本届决赛中获胜的场次已经与他们之前三届决赛的胜场数相同（1938年0胜，1994年1胜，1998年1胜）。\n在使用了所有替补球员后，挪威队在战胜塞内加尔队的最后阶段发现，由于几名球员出现抽筋，挪威队一度只剩下九名球员。\n主教练索尔巴肯因此表示他将在与法国队的比赛中做出一系列改变。\n“会有一些变化。并不是我们不想赢，而是比赛之间的间隔较短以及比赛结束时球员的状态意味着其他一些人将有机会，”索尔巴肯说\n“只能这样了，我们还有两个航班在等，下次你就更难猜到队伍了。”\n在对阵塞内加尔的比赛中，朱利安·瑞尔森在第 13 分钟一瘸一拐地下场，挪威将密切关注他的健康状况，尽管他的替补马库斯·佩德森随后首开纪录。\n马洛·古斯托从脚伤中恢复过来，这是他在对阵伊拉克的比赛中首次亮相，因此他将力争挑战儒勒·孔代的右后卫位置。"
            ],
            [
                "历史交锋",
                "这将是挪威和法国之间的第 16 次交锋，也是自 2014 年 5 月法国队在巴黎友谊赛以 4-0 获胜以来的首次交锋。\n两队此前10场正式比赛中，挪威队只赢了2场，上一次胜利是在1987年6月于奥斯陆举行的欧洲杯预选赛中以2-0获胜。\n然而，挪威从未在世界杯上击败过欧洲同胞（P5 D2 L3），而法国在过去五场对阵欧洲对手的比赛中全部获胜——其中包括英格兰、克罗地亚和比利时的胜利。"
            ],
            [
                "赛前预测（Opta 超算）",
                "由于挪威可能会做出一些改变，因此 Opta 超级计算机选择法国作为最爱也就不足为奇了。\n在 25,000 场赛前模拟比赛中，高卢雄鸡队获胜率为 59.4%，而其中 20.6% 以平局告终 — 这一结果足以让法国队以小组头名身份出线。\n挪威队获胜的概率为 20.0%，因此他们有五分之一的机会全取三分。"
            ]
        ]
    },
    {
        "slug": "senegal-vs-iraq-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/senegal-vs-iraq-prediction-world-cup-2026-match-preview",
        "home_en": "Senegal",
        "away_en": "Iraq",
        "home_cn": "塞内加尔",
        "away_cn": "伊拉克",
        "home_pct": 77.2,
        "draw_pct": null,
        "away_pct": 8.6,
        "insights": [
            "Senegal are considered big favourites by the Opta supercomputer for this fixture, with a win probability of 77.2% to Iraq’s 8.6%.",
            "Senegal have only won one of their three Matchday 3 fixtures in the group stages of the World Cup.",
            "Iraq have lost each of their first five World Cup matches and could become just the second nation from the AFC confederation to fail to win their opening six games across the competition."
        ],
        "prediction": "",
        "summary_cn": "这场比赛的规模对任何一方来说都不会被忽视，但 Opta 超级计算机严重倾向于塞内加尔。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为塞内加尔是本场比赛的热门球队，获胜概率为 77.2%，而伊拉克则为 8.6%。\n· 塞内加尔在世界杯小组赛的三场第三轮比赛中只赢了一场。\n· 伊拉克队在世界杯前五场比赛中全部失利，可能成为亚足联第二个在世界杯前六场比赛中未能获胜的国家。"
            ],
            [
                "深度分析",
                "塞内加尔和伊拉克正处于最后机会，他们将于周五在多伦多体育场进行一场关键的第一组比赛。\n帕普·蒂奥率领的塞内加尔队以 3-1 负于法国队，随后在周一以 3-2 逆转挪威队。\n埃尔林·哈兰德两次射中球门，尽管伊斯梅拉·萨尔也梅开二度，但塞内加尔仍无法挽回局面。\n尽管他们进入前两名的希望已经破灭，但一切并没有失去，因为仍然有机会成为排名最好的八支球队之一，获得第三名。\n但塞内加尔需要扭转一些令人担忧的趋势，才能重振萎靡的赛事并进入 32 强。\n塞内加尔在世界杯首场比赛中两场失利，这是他们在单届世界杯上并列遭遇最多失利的球队，四年前在卡塔尔也曾两度失利。\n此外，塞内加尔队在遭遇连败后，首次面临小组赛三连败的局面。\n他们在这里的两场失利已经与他们在本届锦标赛这一阶段的前九场比赛中所遭受的损失一样多，其中四胜三平。\n塞内加尔此前在世界杯小组赛的三场MD3比赛中只赢了一场，一场平局一场失利。不过，这场胜利是在他们最近一次参加世界杯时取得的，即 2022 年以 2-1 战胜厄瓜多尔。\n萨尔的梅开二度不足以拯救塞内加尔对阵挪威的比赛，但他现在在九场世界杯比赛中打进了三个进球。塞内加尔球员在前 10 场比赛中的进球数是历史上最高的（与帕帕·布巴·迪奥普持平，他也进了 3 个球）。\n伊拉克的情况似乎比塞内加尔更糟糕，因为两场比赛后他们的净胜球为-6，所以即使是爆冷获胜也不能保证晋级。\n伊拉克队在首场比赛中以 1-4 输给挪威队（哈兰德在这场比赛中再次梅开二度），周一在费城以 3-0 不敌法国队。\n基利安·姆巴佩 (Kylian Mbappé) 在上下半场都有进球，随后奥斯曼·登贝莱 (Ousmane Dembélé) 在第 66 分钟取得了胜利，将比赛的比分超出了格雷厄姆·阿诺德 (Graham Arnold) 的球队。\n本届世界杯之前，只有两个国家在小组赛中以三球以上的比分输掉了三场比赛（1930 年的墨西哥和 1982 年的新西兰），而伊拉克在前两场比赛中就已经输掉了这个名单，因此将无法避免进入这个名单。\n这个海湾国家在世界杯前五场比赛中全部失利，并可能成为亚足联联盟中第二个未能赢得前六场比赛的国家，仅次于韩国在1954年至1998年期间输掉了前14场比赛。\n在伊拉克队输给法国队的比赛中，阿卡姆·哈希姆共 71 次传球，完成 86 次触球并完成 68 次。这两个总数都是伊拉克球员在世界杯单场比赛中进球最多的。"
            ],
            [
                "历史交锋",
                "这场第一组最后一轮的比赛是塞内加尔和伊拉克队的首次交锋。\n塞内加尔在世界杯上两场对阵亚足联球队的比赛中保持不败，2018年2-2战平日本，四年前3-1战胜东道主卡塔尔。\n对于伊拉克队来说，这场比赛是他们在世界杯上首次对阵非洲足联球队。\n亚足联最后三个国家在首场比赛中对阵非洲球队（朝鲜、卡塔尔和约旦）时遭遇失利，此前五支球队保持不败（3胜2平）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "这场比赛的规模对任何一方来说都不会被忽视，但 Opta 超级计算机严重倾向于塞内加尔。\n特兰加之狮队的获胜几率高达 77.2%，而伊拉克队的获胜几率仅为 8.6%，而平局的几率被认为是 14.2%。\n从比赛整体来看，塞内加尔显然无法再小组第一，但考虑到他们获胜的概率很高，根据Opta的实时排名，他们仍有56.9%的机会进入32强，但他们夺冠的可能性只有0.2%。\n伊拉克的前景要黯淡得多。他们同样无法小组第一，晋级淘汰赛的机会只有0.3%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer marginally favours a Paraguay victory, with Alfaro’s side having won 38.0% of the 25,000 pre-match simulations. Australia’s chances of claiming three points are rated at 23.4%, with a draw – which would also secure second place in Group D – at 38.6%.",
        "summary_cn": "Opta 超级计算机略微支持巴拉圭获胜，阿尔法罗的球队在 ​​25,000 次赛前模拟中获胜率为 38.0%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 巴拉圭队在之前的六场 FIFA 世界杯小组赛第三轮比赛中保持不败（W3 D3），并且是 Opta 最有希望延续这一连胜纪录的球队，他们的胜率高达 38.0%。\n· 澳大利亚在各项赛事中五次对阵巴拉圭均保持不败（2胜3平）。\n· 然而，澳大利亚队从未在世界杯上击败过南美洲球队（D1 L4）。"
            ],
            [
                "深度分析",
                "巴拉圭和澳大利亚正在争夺 D 组第二名，双方都希望与美国队一起进入世界杯淘汰赛阶段。\n两支球队在前两场比赛中各取一胜，在旧金山进行赢家通吃的比赛。\n对于凭借净胜球优势的澳大利亚队来说，一场平局就足以确保进入前两名。无论谁获得第三名，都不会失去一切，但他们必须等待其他地方的结果才能计划 32 强赛。\n巴拉圭队以 1-4 惨败美国队后，以 1-0 险胜土耳其队，随后在还剩一场比赛的情况下确认了土耳其队的出局。\n古斯塔沃·阿尔法罗的球队在决赛中米格尔·阿尔米龙因捂嘴而领到第一张红牌后，尽管比赛的一半以上有 10 名球员，但他的球队还是这么做了。\n马蒂亚斯·加拉尔萨 (Matías Galarza) 仅仅 64 秒后的进球——世界杯比赛中最早的制胜球——对 La Albirroja 来说已经足够了，他们是自 1966 年朝鲜队击败意大利队（同样是 32 次）以来，在决赛中单场比赛中面对射门次数最多的球队，同时保持不失球（32 次）。\n胡利奥·恩西索还为毛里西奥在对阵美国队的比赛中助攻，他成为继弗朗西斯科·阿尔塞（3次）和罗克·圣克鲁斯（2次）之后第三位在多场世界杯比赛中提供助攻的巴拉圭球员，也是最年轻的球员，年仅22岁零148天。\n这位前布莱顿和伊普斯维奇前锋现在可能成为自2002年德国队的迈克尔·巴拉克以来第一位在决赛中所有三场小组赛中都助攻进球的球员。\n恩西索的进攻创造力和威胁将至关重要，尤其是在阿尔米龙停赛一场的情况下，巴拉圭希望在世界杯上首次取得两场小组赛胜利。\n与此同时，澳大利亚队希望从0-2负于美国队的比赛中东山再起，力争在连续几届世界杯上首次进入淘汰赛阶段。\n在揭幕战中以同样的比分击败土耳其队后，澳大利亚队在西雅图的上半场晚些时候被卡梅伦·伯吉斯的乌龙球和亚历克斯·弗里曼的进球击败。\n伯吉斯的乌龙球是澳大利亚队在世界杯上丢的第三个球（追平了保加利亚、摩洛哥和瑞士的丢球数），仅次于墨西哥队（四个）。\n尽管如此，在球场的另一端，主教练托尼·波波维奇会有些担心。澳大利亚队在 2006 年至 2018 年四届世界杯上场均射门 13.2 次，而在过去两届世界杯上，澳大利亚队场均射门只有 6.7 次，其中上一次对阵共同主办国的比赛中只有 5 次射门。\n虽然一分足以让他们获得 D 组的亚军，但澳大利亚队知道，如果他们想在锦标赛中晋级，并且有机会历史上首次进入四分之一决赛，他们的进攻输出必须有显着的提高。"
            ],
            [
                "历史交锋",
                "这将是国家之间的第一次竞争性会议。\n澳大利亚从未输给巴拉圭，此前五次交锋均保持不败（2胜3平）。但最重要的是，这些都是在本土进行的国际友谊赛——现任主教练波波维奇参加了其中的三场比赛。\n历史还表明，对于澳大利亚队来说，在全球舞台上复制这一点将更加困难。事实上，他们在世界杯五次尝试中从未击败过南美足联国家队（平一平四），上一次此类比赛他们在卡塔尔举行的 16 强赛中以 2-1 输给了最终冠军阿根廷队。\n相比之下，巴拉圭在此前两届世界杯对阵亚足联球队的比赛中保持不败。 1986 年小组赛击败伊拉克后，24 年后，他们在 16 强交锋中互交白卷，并在点球大战中击败日本队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机略微支持巴拉圭获胜，阿尔法罗的球队在 ​​25,000 次赛前模拟中获胜率为 38.0%。\n澳大利亚队拿下三分的几率为 23.4%，平局则确保 D 组第二名的几率为 38.6%。\n这些百分比和最近的表格让这很难判断。\n澳大利亚在过去四场世界杯小组赛中赢了三场（L1）——比之前 16 场比赛的胜利总和还要多（W2 D4 L10）。\n与此同时，巴拉圭在前六场小组赛第三轮比赛中保持不败（3胜3平）。"
            ]
        ]
    },
    {
        "slug": "turkiye-vs-usa-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/turkiye-vs-usa-prediction-world-cup-2026-match-preview",
        "home_en": "Türkiye",
        "away_en": "USA",
        "home_cn": "土耳其",
        "away_cn": "美国",
        "home_pct": 29.3,
        "draw_pct": 23.0,
        "away_pct": 47.7,
        "insights": [
            "The Opta supercomputer expects the USA to finish their Group D campaign on the front foot, with Mauricio Pochettino’s side winning 47.7% of the pre-match simulations.",
            "USA have won back-to-back World Cup matches for the first time since the very first pair of games they played in the competition (against Belgium and Paraguay) in 1930. They have never won three in a row at the tournament.",
            "Türkiye have two losses from two at this World Cup, yet have never lost three games in a row in the competition. They were also kept goalless by both Australia and Paraguay, having only failed to score in one of their previous 10 World Cup matches."
        ],
        "prediction": "From 25,000 match simulations, Pochettino’s charges are given a healthy win probability of 47.7%. Despite their dismal showing so far, a Türkiye victory isn’t seen as too big of a stretch, with Montella’s side given a 29.3% win rating, just ahead of a draw at exactly 23.0% probability.",
        "summary_cn": "随着世界杯淘汰赛的到来，土耳其队将在这场比赛后退出舞台，Opta 超级计算机将美国队视为赢得这场 D 组决胜局的热门球队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计美国队将在 D 组比赛中取得领先，毛里西奥·波切蒂诺的球队在赛前模拟中获胜率为 47.7%。\n· 自 1930 年首次参加世界杯比赛（对阵比利时和巴拉圭）以来，美国队首次连续赢得世界杯比赛。他们从未在世界杯比赛中取得三连胜。\n· 土耳其队在本届世界杯上取得了两场两负的成绩，但从未在比赛中连续输过三场比赛。他们还被澳大利亚和巴拉圭两队保持无进球，在之前的 10 场世界杯比赛中只有一场没有进球。"
            ],
            [
                "深度分析",
                "毛里西奥·波切蒂诺 (Mauricio Pochettino) 率领的美国队正在备战 2026 年世界杯小组赛最后一场比赛，人们对他们抱有很高的期望，而共同主办方在进入 32 强之前已经确定为 D 组冠军。\n相反，美国队面对的是D组垫底的土耳其队，没有机会进入淘汰赛，他们在首场比赛中分别以2-0和1-0的比分输给了澳大利亚和巴拉圭。\n文森佐·蒙特拉的球队在输给澳大利亚队的比赛中每半场中段都有失球，但上次对阵巴拉圭队时几乎从一开始就落后。\n马蒂亚斯·加拉尔萨 (Matías Galarza) 在仅用时 1 分 4 秒为巴拉圭攻入制胜球，这不仅是本届世界杯最快的进球，也是自 2018 年丹麦队对阵克罗地亚队时马蒂亚斯·约根森 (Mathias Jørgensen) 在 55 秒内破门得分以来所有赛事中最快的进球。\n土耳其队在半场结束时米格尔·阿尔米龙的红牌帮助土耳其队重返比赛，但尽管他们总共尝试了 32 次射门，但他们追寻的扳平比分始终未能实现。\n这是本届世界杯上单场比赛中单支球队射门次数最多的球队，而土耳其队在最近 66 次射门组合中都没有进球（2026 年 62 次，2002 年 4 次），这是世界杯历史上第二长的连续射门次数（仅次于阿尔及利亚）。\n在本届世界杯上，凯南·耶尔迪兹在射门次数（12 次）、在对方禁区触球次数（20 次）和成功带球次数（5 次）方面领先土耳其队，但他的 12 次射门中只有 1 次射正，总预期进球数仅为 0.45（每次射门 0.04）。\n土耳其队在对阵巴拉圭队的比赛中毫无成果，控球率高达 78.6%，这是世界杯比赛历史上第六高的控球率，而阿卜杜勒克里姆·巴尔达克奇 (Abdülkerim Bardakci) 的 98 次传球是自 1966 年以来土耳其球员单场比赛中传球次数最多的。\n如果土耳其想要有机会对阵这支美国队，蒙特拉需要伊尔迪兹、巴达克奇、阿尔达·居勒和队长哈坎·恰尔汗奥卢等球员挺身而出，美国队在前两场比赛后势头不断增强。\n美国队是本届世界杯迄今为止表现最出色的球队之一，他们在首场比赛中以 4-1 击败巴拉圭队，随后经过一场艰苦的比赛以 2-0 战胜澳大利亚队，确定了 D 组冠军的位置。\n波切蒂诺的球队在两场比赛中打进了 6 个进球——继 1930 年和 2002 年两次打入 7 个进球之后，这已经是美国队在单届世界杯上的第三高进球数。在 2026 年世界杯的 6 个进球中，有 5 个是在上半场比赛中打进的。\n在福拉林·巴洛贡的梅开二度和乔瓦尼·雷纳的火箭将巴拉圭逼入绝境后，澳大利亚球员卡梅伦·伯吉斯早早将巴洛贡的传中带入自家球门，亚历克斯·弗里曼在半场结束前将东道主的优势扩大了一倍。\n弗里曼是本届世界杯上唯一一位同时进球和助攻的美国球员，成为自2014年约翰·布鲁克斯对阵加纳队以来第一位在世界杯上进球的后卫。\n这个最初被禁止的头球让美国队在比赛和 D 组中都占据了主导地位，从而锁定了 32 强对阵阿尔及利亚、奥地利或 B、E、F 或 I 组中其他第三名球队之一的道路。\n在对阵澳大利亚的比赛中，美国队展现出了深入晋级本届赛事所需的实力和勇气。如果像巴洛贡和康复的克里斯蒂安·普利西奇这样的球员在对阵土耳其的比赛中表现出色，人们对他们能够做到这一点的信心将会进一步增强。"
            ],
            [
                "历史交锋",
                "这将是土耳其队和美国队在世界杯上的首次交锋，但两国队之间并不陌生，此前五次交锋，双方取得了两胜一平、各进七个球的平衡战绩。\n他们的最后一场比赛是在 2025 年 6 月；在康涅狄格州举行的一场友谊赛中，杰克·麦克格林 (Jack McGlynn) 在 60 秒内为美国队进球，而古勒 (Güler) 和凯雷姆·阿克图科格鲁 (Kerem Aktürkoglu) 在第 24 分钟和第 27 分钟分别进球回应，最终土耳其队以 2-1 获胜。\n尽管本届世界杯开局强劲，美国队在过去 20 场对阵欧足联附属国家的世界杯比赛中只赢了一场，并在 2002 年小组赛中以 3-2 击败了葡萄牙队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "随着世界杯淘汰赛的到来，土耳其队将在这场比赛后退出舞台，Opta 超级计算机将美国队视为赢得这场 D 组决胜局的热门球队。\n根据 25,000 场比赛模拟，波切蒂诺的球队获胜概率为 47.7%。\n尽管土耳其队到目前为止表现不佳，但人们认为土耳其队的胜利并不算太大，蒙特拉队的获胜率为 29.3%，仅领先于平局的概率为 23.0%。"
            ]
        ]
    },
    {
        "slug": "japan-vs-sweden-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/japan-vs-sweden-prediction-world-cup-2026-match-preview",
        "home_en": "Japan",
        "away_en": "Sweden",
        "home_cn": "日本",
        "away_cn": "瑞典",
        "home_pct": 52.7,
        "draw_pct": null,
        "away_pct": 22.2,
        "insights": [
            "Japan go into this clash as favourites, according to the Opta supercomputer, winning 52.7% of simulations compared to Sweden ‘s 22.2%.",
            "Friday’s contest in Dallas will be Japan and Sweden’s first meeting at the World Cup.",
            "Following a draw with the Netherlands and a win over Tunisia, Japan have a chance to go through the group stage of a World Cup unbeaten for only the second time, after first doing so as co-hosts in 2002."
        ],
        "prediction": "The Opta supercomputer gives both Japan and the Netherlands a 100% chance of progressing to the round of 32, while Sweden are assigned a 91.5% probability as Group F’s top three sides look set to advance.",
        "summary_cn": "Opta 超级计算机支持日本队成为获胜并锁定下一轮席位的热门球队，在 25,000 次赛前模拟中，守康的球队以 52.7% 的胜率获胜。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，日本队在这场比赛中是夺冠热门，在模拟比赛中获胜率为 52.7%，而瑞典队的获胜率为 22.2%。\n· 周五在达拉斯举行的比赛将是日本和瑞典在世界杯上的首次交锋。"
            ],
            [
                "深度分析",
                "当日本队周五在达拉斯体育场迎战瑞典队时，F组前两名的名次就岌岌可危了，获胜者将在世界杯淘汰赛阶段之前获得巨大的提升。\n守安肇的球队在与瑞典的比赛之前目前在小组中排名第二，并且在本届赛事中保持不败，先是与领头羊荷兰队2-2战平，然后在上一场比赛中以4-0击败了已经被淘汰的突尼斯队。\n镰田大地在达拉斯比赛中第 89 分钟扳平比分，为对阵橙衣军团的比赛赢得了宝贵的一分，并在蒙特雷比赛仅四分钟后就进球，开始了日本队对突尼斯的比赛。\n上田绫濑梅开二度，而伊藤纯也也取得进球，让蓝武士在第一轮淘汰赛前处于领先地位。\n尽管他们的立场不同，但日本仍然面临着很多风险。避免输给瑞典意味着他们在2002年作为共同东道主首次在世界杯小组赛中保持不败（2胜1平）。\n守保知道这可以给淘汰赛带来信心，并渴望他的球队能够延续他们在所有比赛中九场不败的记录。\n在世界杯上，日本队在过去的四场比赛中保持不败（W2 D2），并且即将成为继韩国队（1998年至2002年连续六场比赛）之后第二个连续五场比赛不败的亚足联国家。\n阻碍他们的是一支命运多舛的瑞典队。\n格雷厄姆·波特的球队开局就取得了巨大的成功，以 5-1 击败了突尼斯队，随后在第二轮比赛中以 5-1 输给了荷兰队，他们也尝到了自食其果的滋味。\n由此，瑞典队成为世界杯历史上第二支在同一赛事中以至少四球优势获胜和输掉比赛的球队。\n顺便说一句，第一个案例也涉及瑞典，瑞典以 8-0 击败古巴，然后在 1938 年以 5-1 输给匈牙利。\n瑞典对阵荷兰的比赛实际上只面对了10次射门，但其中7次射正，5次射正；这是波特坚持改进的一个领域，尤其是面对日本的动态进攻。\n事实上，Samurai Blue 已经有 8 名不同的球员为进球做出贡献，追平了单届世界杯的最高进球数（2022 年也有 8 名球员）。\n他们中表现最出色的球员之一是上田，他的三粒进球（两粒进球，一次助攻）是日本球员在单届世界杯上并列最多的。他的两个进球也创下了该国联合锦标赛的纪录。\n对于瑞典队来说，亚历山大·伊萨克提供了最多的进攻灵感。这位前锋已经打进一球并送出 3 次助攻，已经超越了瑞典球员此前在世界杯上的进球数纪录（自 1966 年以来）。\nOpta 超级计算机给出日本和荷兰晋级 32 强的概率为 100%，而瑞典则有 91.5% 的概率，因为 F 组前三名球队有望晋级。"
            ],
            [
                "历史交锋",
                "这将是日本和瑞典在世界杯上的首次交手，尽管两国此前已经交锋过五次。\n他们的第一次交锋可以追溯到 1936 年奥运会上，当时日本队在 0-2 落后的情况下以 3-2 获胜，被称为“柏林奇迹”。自此之后，武士蓝队在所有四场比赛中均未尝胜绩，尽管最近一次是在 2002 年 5 月（以 1-1 结束）。\n自 2022 年世界杯开始以来，日本队在对阵欧洲球队的四场比赛中保持不败（W2 D2），其中包括在本届世界杯早些时候与荷兰队战平。他们在这段时间里的两场胜利相当于他们之前 10 次与欧洲国家交锋中取得的胜利。\n同样，瑞典在世界杯上从未输给过亚洲对手（2胜1平）。他们最近一次战胜亚足联国家队是2018年1-0击败韩国队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持日本队成为获胜并锁定下一轮席位的热门球队，在 25,000 次赛前模拟中，守康的球队以 52.7% 的胜率获胜。\n与此同时，瑞典获胜的概率仅为 22.2%，平局占模拟比赛的剩余 25.1%。"
            ]
        ]
    },
    {
        "slug": "tunisia-vs-netherlands-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/tunisia-vs-netherlands-prediction-world-cup-2026-match-preview",
        "home_en": "Tunisia",
        "away_en": "Netherlands",
        "home_cn": "突尼斯",
        "away_cn": "荷兰",
        "home_pct": 4.9,
        "draw_pct": 9.9,
        "away_pct": 85.3,
        "insights": [
            "After swatting aside Sweden, the Netherlands have an 85.3% chance of posting consecutive wins according to the Opta Supercomputer.",
            "Following 25,000 pre-match simulations, Tunisia emerged with just a 4.9% chance of success in Kansas City.",
            "Outside penalty shootouts, Oranje are unbeaten across 14 World Cup games since losing to Spain in the 2010 final (W9 D5) – that’s the longest streak in the tournament’s history."
        ],
        "prediction": "The Opta supercomputer’s 25,000 pre-match simulations calculated an 85.3% chance of success for the Netherlands. Tunisia have a mere 4.9% chance of leaving this World Cup with a win, while the draw is rated at 9.9%.",
        "summary_cn": "Opta 超级计算机进行了 25,000 次赛前模拟，计算出荷兰队的获胜几率为 85.3%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，在击败瑞典后，荷兰队连续获胜的几率为 85.3%。\n· 自 2010 年决赛输给西班牙（9 胜 5 平）以来，橙衣军团在世界杯的 14 场比赛中保持不败，这是世界杯历史上最长的不败纪录。"
            ],
            [
                "深度分析",
                "荷兰队几乎已经确定进入淘汰赛阶段，他们的目标是在周四对阵饱受危机蹂躏的突尼斯队时获得 F 组第一名。\n罗纳德·科曼的球队位居榜首，与日本队同积四分，而他们的对手已经无法晋级，只剩下骄傲了。\n在两度落后日本队的比赛中，荷兰队以 2-2 战平日本队，随后又在休斯敦与瑞典队交锋。\n令人惊讶的是，布赖恩·布罗比被选为前锋，事实证明他几乎无法上场，并成为第二位在世界杯首场比赛中梅开二度的荷兰球员。\n上半场开局火热，科曼的球队以 5-1 的比分战胜了刚刚以相同比分击败突尼斯队的瑞典队。\n即使没有历史最佳射手孟菲斯·德佩完全康复并火力全开，他们也取得了一些冷静的成绩：35%的射门转换率（7次射门/20次射门）是他们自60年前有此类记录以来历届世界杯上的最佳成绩。\n迄今为止，在 35 场小组赛中仅输过两次（22 胜 11 负）——最近一次是 1994 年对阵邻国比利时——很少有人预测周四晚上会发生令人震惊的失利。\n毫无疑问，历史将对他们有利。\n荷兰队三夺亚军，而突尼斯队在 20 场世界杯比赛中只取得了 3 场胜利。\n事实上，这个北非国家此前只在这个级别上击败过欧洲对手一次（D4 L8），最著名的是 2022 年卡塔尔世界杯上战胜法国队的比赛。\n即使是一场不可能的胜利在这种情况下也没有什么意义，因为他们在灾难性的开局后无法再从F组出线。\n在瑞典5-1大胜之后，足协立即解雇了萨布里·拉穆奇，并由另一位法国教练埃尔韦·雷纳德接替了他。\n然而，这位两届非洲国家杯冠军得主却无法适应他的新部队，因为突尼斯队0-4输给日本队的比赛中未能射正目标，预期进球数仅为0.05。\n这也让他们成为第四支在世界杯上连续输掉四场或以上进球的球队，加入了希腊（1994年）、韩国（1954年）和玻利维亚（1930年）的耻辱殿堂。\n雷纳德可能是公认的非洲杯王者，但他现在在世界杯决赛的七场比赛中输掉了五场。\n假设他在堪萨斯城开球前没有被解雇，雷纳德肯定会任命一名由队长埃利斯·斯基里和有影响力的组织者汉尼拔·梅杰布里组成的中场。\n梅杰布里在最后三区的传球次数最多，参加对阵日本队的对决最多（16 场比赛中赢了 8 场）；然而，总结一下这支缺乏进球的球队，他只为突尼斯队进球过一次。\n相比之下，科迪·加克波现在仅在世界杯小组赛阶段就有五个进球，与罗宾·范佩西并列荷兰球员之最。\n加克波（Gakpo）在左路忙碌，荷兰队的右路补给则由效力皇家马德里的丹泽尔·邓弗里斯（Denzel Dumfries）提供，他在对阵瑞典的比赛中梅开二度，将自己职业生涯的国际助攻总数达到了 20 次。\n如果他再为布罗比送出一系列诱人的传中——布罗比为科曼的球队提供了对阵日本时所缺少的焦点——那么突尼斯可能会面临一个漫长的夜晚。"
            ],
            [
                "历史交锋",
                "这两个国家将首次在世界杯上相遇，尽管荷兰队在三场友谊赛中保持不败。\n在第一场比赛中取得领先后，最后两场比赛均以平局收场。值得注意的是，1994年1月两队2-2战平时，科曼攻入了他的倒数第二粒国际比赛进球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机进行了 25,000 次赛前模拟，计算出荷兰队的获胜几率为 85.3%。\n突尼斯队在本届世界杯上获胜的概率仅为 4.9%，而平局概率为 9.9%。"
            ]
        ]
    },
    {
        "slug": "curacao-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/curacao-vs-ivory-coast-prediction-world-cup-2026-match-preview",
        "home_en": "Curaçao",
        "away_en": "Ivory Coast",
        "home_cn": "库拉索",
        "away_cn": "科特迪瓦",
        "home_pct": 7.9,
        "draw_pct": 10.1,
        "away_pct": 81.5,
        "insights": [
            "Ivory Coast overcame Curaçao in a huge 81.5% of 25,000 pre-match simulations by the Opta supercomputer.",
            "Curaçao could become the lowest-ranked side in history to reach the knockout stages at the World Cup.",
            "Ivory Coast are hoping to reach the World Cup knockout stages for the first time ever."
        ],
        "prediction": "The Opta supercomputer struggled to see anything other than a win for Ivory Coast, who came out on top in a massive 81.5% of 25,000 pre-match simulations. Curaçao were afforded just a 7.9% chance of victory, with the draw accounting for 10.1% of the data-led simulations.",
        "summary_cn": "Opta 超级计算机除了科特迪瓦队的胜利之外很难看到任何其他结果，科特迪瓦队在 25,000 次赛前模拟中以 81.5% 的准确率名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机在 25,000 次赛前模拟中以 81.5% 的准确率击败了科特迪瓦队。\n· 库拉索岛可能成为历史上进入世界杯淘汰赛阶段排名最低的球队。\n· 科特迪瓦希望有史以来第一次进入世界杯淘汰赛阶段。"
            ],
            [
                "深度分析",
                "当科特迪瓦周四在费城迎战库拉索岛时，他们只需要一分就能确保世界杯 E 组第二名。\n尽管埃默塞·法埃的球队在周六1-2负于德国的比赛中遭遇了心碎，但科特迪瓦在开局1-0战胜厄瓜多尔后，晋级希望仍然掌握在他们手中。\n即使厄瓜多尔在第三轮比赛中击败德国，科特迪瓦在交锋记录上优于南美球队，这意味着避免输给库拉索岛将锁定小组第二名。\n历史也可以等待。科特迪瓦从未在世界杯上进入过淘汰赛阶段，也从未在单届决赛中取得两场胜利。\n你也会期望在这里进球。科特迪瓦队在 91% 的世界杯比赛中都有进球（10/11），这是世界杯历史上至少参加过三场比赛的球队中进球率最高的球队。\nFaé 将再次向 Yan Diomande 寻求创意火花。他在前两场世界杯比赛中完成了 8 次带球，这是非洲球员在前两场世界杯比赛中并列最多带球记录（自 1966 年以来），另外还有 1994 年尼日利亚队的周日奥利塞（同样是 8 次）。\n事实上，科特迪瓦队在对阵德国队的比赛中总共完成了 20 次带球，这是他们在决赛中单场比赛中最多的带球过人次数。三名不同的球员完成了至少四次带球（迪奥曼德、威尔弗里德·辛戈、克里斯特·伊瑙·乌莱），这是自 1994 年尼日利亚对阵意大利（杰·杰·奥科查、菲尼迪·乔治和伊曼纽尔·阿穆尼克）以来，非洲球队在世界杯比赛中过人次数最多的一次。\nFaé预计他的球队会在这里更加主动。库拉索岛在本届世界杯的前两场比赛中射正 27 次，比 E 组其他所有球队的总和（19 次）还要多。\n然而，迪克·阿德沃卡特的球队在上一场与厄瓜多尔互交白卷的比赛中，尽管有 15 次射正，但还是设法保持不失球。\n库拉索岛在世界杯上的首个进球主要归功于埃洛伊·鲁姆（Eloy Room），他成为有记录以来（自 1966 年以来）第一位在世界杯比赛正常时间内（不包括加时赛）做出 15 次扑救的门将。根据射正目标的 xG，Room 阻止了两个进球（射中目标的 2.27 xG）。\n在这里一场不太可能的胜利将为阿德沃卡特的球队创造进一步的历史，因为即使厄瓜多尔战胜德国，库拉索岛也将有资格成为最好的第三名球队之一。\n自 1992 年推出 FIFA 世界排名以来，库拉索岛在 2026 年世界杯中排名第 83 位，可能成为世界杯小组赛中排名最低的球队。\n在球场的另一端，阿德沃卡特可能会向 Tahith Chong 寻求灵感。这位前曼联边锋是E组中完成过人次数最多的球员（9次），比迪奥曼德多1次。\n冲的总数是本次锦标赛上任何其他库拉索岛球员的两倍多（朱尼尼奥·巴库纳（Juninho Bacuna）位居第二，为 4 个），如果阿德沃卡特的球队想要在费城体育场创造历史，那么阿德沃卡特将需要这两个人都保持最佳状态。"
            ],
            [
                "历史交锋",
                "这将是两人的第一次会面。\n这也将是科特迪瓦在世界杯上首次对阵中北美洲及加勒比地区国家。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机除了科特迪瓦队的胜利之外很难看到任何其他结果，科特迪瓦队在 25,000 次赛前模拟中以 81.5% 的准确率名列前茅。\n库拉索岛获胜的几率仅为 7.9%，在以数据为主导的模拟中，平局占 10.1%。\n事实上，Opta 的现场锦标赛预测显示科特迪瓦进入淘汰赛阶段的可能性为 93.3%，远远高于库拉索岛 17.6% 的可能性。"
            ]
        ]
    },
    {
        "slug": "ecuador-vs-germany-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/ecuador-vs-germany-prediction-world-cup-2026-match-preview",
        "home_en": "Ecuador",
        "away_en": "Germany",
        "home_cn": "厄瓜多尔",
        "away_cn": "德国",
        "home_pct": 17.6,
        "draw_pct": null,
        "away_pct": 62.7,
        "insights": [
            "Germany are considered favourites by the Opta supercomputer for this fixture, with a win probability of 62.7% to Ecuador’s 17.6%.",
            "Deniz Undav is averaging a goal or assist every 11 minutes at this World Cup.",
            "Ecuador had 16 shots on target without scoring in their opening two games of the tournament."
        ],
        "prediction": "",
        "summary_cn": "Opta 超级计算机认为德国队是小组赛三胜三负的热门球队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为德国是本场比赛的热门球队，获胜概率为 62.7%，厄瓜多尔为 17.6%。\n· Deniz Undav 在本届世界杯上平均每 11 分钟就有一个进球或助攻。\n· 厄瓜多尔队在本届世界杯的前两场比赛中有 16 次射正但没有进球。"
            ],
            [
                "深度分析",
                "国家队在开局7-1大胜库拉索队后，又在最后时刻2-1战胜科特迪瓦队，已经锁定小组头名。\n朱利安·纳格尔斯曼的球队在对阵大象队的比赛中远没有令人信服，并且由于弗兰克·凯西在第 30 分钟的首开纪录，半场落后。\n但替补出场的德尼兹·昂达夫证明了自己是英雄，他在第 68 分钟将比分扳平，随后在第 94 分钟冷静地攻入制胜球，确保安全晋级淘汰赛。\n因此，纳格尔斯曼可能会考虑在完成小组任务时让一些主力休息，但他有机会帮助德国队在所有比赛中追平纪录的12连胜。\n他们之前在 1979 年 5 月至 1980 年 6 月期间取得了如此多的胜利，并且正在悄悄积蓄势头，希望赢得第五届世界杯。\n乌达夫在本届世界杯上打进了三个进球，全部是替补德国队出场的。在世界杯上，他平均每 11 分钟就有一个进球或助攻，其中他的 3 个进球和 2 个助攻来自仅仅 56 分钟的出场时间。\n没有球员在前三场世界杯比赛中以替补身份进球，而唯一在前三场比赛中进球的德国球员是 1970 年的盖德·穆勒和 2002 年的米罗斯拉夫·克洛泽。\n在赢得了前两场比赛后，德国队希望第四次赢得世界杯小组赛中的所有比赛，此前曾在 1970 年、1974 年（第二小组赛）和 2006 年实现过这一目标。\n厄瓜多尔晋级32强的希望悬而未决，塞巴斯蒂安·贝卡塞塞的球队在0-1负于科特迪瓦之后又与库拉索队0-0战平。\n这意味着他们需要首次战胜德国队才能进入淘汰赛阶段，但预兆看起来并不是特别好。\n三色旗队在本届世界杯的前两场比赛中有 16 次射门没有进球。从 1966 年到 2022 年的记录来看，单届赛事中单次射门次数最多的球队是 2002 年卫冕冠军法国队 18 次。\n老将前锋恩纳·瓦伦西亚可能会在这场比赛中为他的国家创造历史。如果他参加这场比赛，他将超越爱迪生·门德斯，成为厄瓜多尔世界杯出场纪录保持者。\n2014年他8次射门打进3球，2022年9次射门打进3球，但2026年他有8次射门没有进球。"
            ],
            [
                "历史交锋",
                "德国队此前两次对阵厄瓜多尔队均取得胜利，其中包括2006年主场世界杯小组赛中以3-0获胜。\n他们的另一场胜利是 2013 年 5 月以 4-2 的友谊赛获胜，这场比赛碰巧也是在美国佛罗里达州博卡拉顿举行。\n此外，德国队在世界杯小组赛对阵南美国家队的 10 场比赛中保持不败（7 胜 3 平），仅丢 5 个球。\n厄瓜多尔队自2013年2月3-2击败葡萄牙队以来，在最近9次与欧洲对手的交锋中未尝胜绩（5平4负）。然而，之前的四场比赛中有三场是平局，其中最近一次是在今年三月，他们1-1战平荷兰。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机认为德国队是小组赛三胜三负的热门球队。\n他们的胜率是62.7%，厄瓜多尔获胜的概率是17.6%，平局的概率是19.7%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer’s 25,000 pre-match simulations established Brazil as clear favourites, with a 69.6% chance of success. Scotland only have a modest 12.2% chance of claiming victory, with the draw rated at 18.2%.",
        "summary_cn": "Opta 超级计算机进行了 25,000 次赛前模拟，使巴西成为明显的热门球队，成功的几率为 69.6%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据Opta超级计算机的预测，巴西队将大步进入淘汰赛阶段——他们获胜的几率为69.6%。\n· 最终击败巴西队的几率只有 12.2%，苏格兰可以承担起他们喜欢的弱者角色。\n· 巴西是苏格兰遭遇次数最多但从未获胜的球队（P10 D2 L8）。"
            ],
            [
                "深度分析",
                "巴西队将在迈阿密第五次参加世界杯，他们将迎战一心改写历史的苏格兰队。\n虽然南美豪门五次获得世界冠军，但他们的苏格兰对手一直在尝试在重大赛事中小组出线，但未能成功。\n已经保证至少获得 C 组第三名，只要再拿一分，就肯定能首次进入世界杯淘汰赛阶段——即使是微弱的失利也足以证明。\n苏格兰在 1-0 战胜海地后又以 1-0 负于摩洛哥，现在他们将努力在重要决赛中赢得不止一次的胜利。\n为了完成这一任务，史蒂夫·克拉克的小队当然不缺乏经验；在对阵摩洛哥的比赛中，他的首发阵容中的球员总共代表国家队出场 609 次，这是苏格兰足球历史上出场次数最多的球员。\n然而，苏格兰从未在世界杯上击败过南美对手（D2 L6）。其中有四场对阵巴西队的比赛，双方第一次交锋是在 1974 年。\n尽管那场与当时的卫冕冠军的交锋以互交白卷告终，但巴西队此后已经三度获胜——82年的西班牙队、90年的意大利队和98年的法国队。\n今年，桑巴军团以净胜球优势位居C组榜首，在1-1战平摩洛哥后，球队以3-0击败海地。\n对阵后者时，马修斯·库尼亚的梅开二度和维尼修斯·儒尼奥尔的本届世界杯第二粒进球帮助巴西超越德国，成为世界杯历史上进球数最多的球队，达到 241 个。德国队随后在对阵科特迪瓦的比赛中梅开二度追平了这一纪录。\n和克拉克一样，安切洛蒂更喜欢经过验证的理智，而不是原始潜力：在对阵海地的比赛中首发出场的巴西十一人已经 30 岁零 190 天，是自 1962 年决赛以来在世界杯比赛中年龄最大的球员。\n然而，这一一般规则也有一些令人兴奋的例外。\n拉扬（19岁零320天）和恩德里克（19岁零333天）都是费城替补登场的球员，成为56年来代表巴西参加世界杯的最年轻球员。\n事实上，这是继 1958 年何塞·阿尔塔菲尼和 17 岁神童贝利之后，他们第二次在同一场世界杯比赛中派出两名 20 岁以下球员。\n在拉菲尼亚受伤后，巴西人的大部分希望都寄托在维尼修斯身上，他在过去五场国家队比赛中打进了六粒进球（三粒进球，三次助攻）。\n如果维尼修斯是现在的球员，也许内马尔就代表了过去，但由于拉菲尼亚缺席，而这位桑托斯球星据说现在已经康复，他可能会在周三发挥一些作用。\n值得注意的是，大约 15 年前，内马尔穿着著名的金丝雀黄色球衣首次梅开二度，当时本·甘农-多克还在婴儿学校上学。\n格子军团敦促克拉克释放他的快速边锋，他在约翰·麦克金对阵海地的进球中发挥了作用，但在输给摩洛哥的比赛中只能客串。\n虽然甘农-多克可能是苏格兰的外卡，但他们的无名英雄无疑是刘易斯·弗格森，迄今为止，他在铲断（8）、拦截（4）和决斗胜利（20）方面高居球队榜首。\n除了斯科特·麦肯纳和亚伦·希基的伤病疑虑外，弗格森还缺席了一些训练，但他希望为苏格兰足球最辉煌的时刻做好准备。"
            ],
            [
                "历史交锋",
                "巴西队和苏格兰队将恢复友好竞争，第五次在世界杯上相遇。自 1974 年以来，只有阿根廷对阵荷兰（六场）的比赛次数最多。\n自从当年0-0战平后，桑巴军团在接下来的三场比赛中都取得了胜利（1982年4-1，1990年1-0，1998年2-1）；他们在六场友谊赛中也保持不败。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机进行了 25,000 次赛前模拟，使巴西成为明显的热门球队，成功的几率为 69.6%。\n苏格兰获胜的几率只有 12.2%，平局率为 18.2%。"
            ]
        ]
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
        "prediction": "From 25,000 pre-match simulations, Morocco emerged victorious in 81.0% of the outcomes, suggesting they will be comfortable favourites in Atlanta. Haiti are given little margin for error with a mere 6.8% chance of victory, but with a draw standing at 12.3% likelihood, Les Grenadiers will do all they can to create history and avoid a sixth straight World Cup defeat.",
        "summary_cn": "摩洛哥可以说是迄今为止 C 组中最令人印象深刻的球队，并准备在 32 强赛中迎战荷兰、日本或德国，Opta 超级计算机预计摩洛哥将强势对阵海地。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机将摩洛哥视为赢得这场比赛的大热门，穆罕默德·瓦赫比的球队在 ​​25,000 次赛前模拟中以 81.0% 的胜率名列前茅。\n· 摩洛哥在过去四场世界杯小组赛中赢了三场，比他们在这一阶段的前 16 场比赛中取得的成绩（两场胜利）还要多。\n· 海地队在两届世界杯比赛中全部输掉了 5 场比赛，丢了 18 个进球，只进了 2 球。只有萨尔瓦多（6场）在本届赛事中出场次数更多，并且保持着100%的输球率。"
            ],
            [
                "深度分析",
                "2026 年世界杯 C 组头名位置岌岌可危，摩洛哥队将于周三在亚特兰大体育场与海地队进行决定性的比赛，阿特拉斯雄狮队仍有机会超越五届世界杯冠军巴西队。\n摩洛哥队保持不败，在小组中排名第二，领先于已经被淘汰的海地队，他们与巴西队1-1战平，并以1-0击败苏格兰队，距离晋级32强仅一步之遥。\n伊斯梅尔·萨巴里在对阵巴西的比赛中打入漂亮的首开纪录，并在上一场对阵苏格兰的比赛中更早进球，他在第二分钟凌空抽射破门，这被证明是世界杯历史上最早的致胜进球。\n塞巴里在仅仅 1 分 10 秒后的进球也是 2026 年世界杯上最早的进球，布拉希姆·迪亚兹为这位埃因霍温前锋提供了他在这么多场比赛中的第二次助攻。\n摩洛哥在两场比赛中从前到后都给人留下了深刻的印象，没有任何球员比阿什拉夫·哈基米赢得更多的对抗（15次）、更多的传球次数（11次）或更多的射门（5次），只有迪亚斯（5次）比巴黎圣日耳曼边后卫（4次）创造的机会更多。\n阿特拉斯雄狮攻防两端的高效体现在，苏格兰队在落后 88 分钟的情况下却未能取得一脚射门，而 18 岁的里尔中场球员阿尤布·布阿迪（Ayyoub Bouaddi）控制着引擎室，在对阵巴西队的比赛中也给人留下了深刻的印象。\n从目前情况来看，摩洛哥有望在 32 强赛中迎战荷兰（F 组榜首），而巴西队将在同组迎战日本队，巴西队仅以净胜球优势领先瓦赫比队。\n如果摩洛哥在 C 组决胜局中击败巴西，则跌至苏格兰之后排名第三，摩洛哥将对阵 E 组冠军德国，这意味着 2022 年半决赛选手没有“轻松”的道路。\n然而，摩洛哥希望击败海地队，为自己带来最好的平局，海地队在世界杯回归中两战两负，分别以 1-0 和 3-0 输给苏格兰和巴西。\n海地尚未在世界杯比赛中获得一分或零失球，并且在 1974 年和 2026 年两届世界杯的五场比赛中，有四场（总共 18 场）丢了 3 个或更多进球。\n卡伦斯·阿库斯领到了 2026 年世界杯最快的黄牌（3 分 21 秒），巴西队凭借马修斯·库尼亚 (Matheus Cunha) (2) 和维尼修斯·儒尼奥尔 (Vinícius Júnior) 的上半场进球迅速控制了局势。\n威尔逊·伊西多尔在中场休息时上场，海地队在上半场未能取得一脚射门，这是巴西队自 1990 年对阵苏格兰队以来在世界杯比赛中首次出现这样的情况。\n然而，海地队确实将桑巴军团在90分钟内的射门总数限制为8次，整个下半场也只有2次射门，这是世界杯上巴西队在半场后射门次数最少的球队（创纪录），仅次于2014年四分之一决赛对阵哥伦比亚的球队。\n由于没有机会进入淘汰赛阶段，海地将希望在一个高水平的比赛中结束他们的比赛，同时可能会令摩洛哥感到沮丧，而这个加勒比岛国仍在寻找他们的第一个世界杯积分。"
            ],
            [
                "历史交锋",
                "这将是摩洛哥和海地之间的首次交锋，塞巴斯蒂安·米涅的球队在时隔 52 年缺席世界杯之后，这是他们第六次参加世界杯比赛。\n摩洛哥在世界杯上唯一一次与中北美洲及加勒比海国家队交锋是在 2022 年小组赛期间，凭借哈基姆·齐耶赫和优素福·恩内西里上半场的进球，在卡塔尔以 2-1 击败加拿大队。\n与此同时，这是海地在本届世界杯上首次对阵非洲对手。他们之前与非洲足联国家仅有的两次交锋都是在友谊赛中对阵刚果（1992年）和突尼斯（2026年3月）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "摩洛哥可以说是迄今为止 C 组中最令人印象深刻的球队，并准备在 32 强赛中迎战荷兰、日本或德国，Opta 超级计算机预计摩洛哥将强势对阵海地。\n在 25,000 次赛前模拟中，摩洛哥以 81.0% 的胜率获胜，这表明他们将成为亚特兰大的热门球队。\n海地队的失误空间很小，获胜的可能性只有6.8%，但平局的可能性有12.3%，掷弹兵将竭尽全力创造历史，避免世界杯六连败。"
            ]
        ]
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
        "prediction": "The Opta supercomputer makes Bosnia heavy favourites for this match after they came out on top in 67.8% of the 25,000 pre-match simulations.",
        "summary_cn": "Opta 超级计算机使波斯尼亚队成为本场比赛的热门球队，他们在 25,000 次赛前模拟中以 67.8% 的成绩名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 卡塔尔的 FIFA 世界杯之旅似乎即将结束，Opta 超级计算机给他们带来的胜利机会只有 14.0%。\n· 波黑在过去 15 场国际比赛中，有 13 场比赛射正 3 次以上，同时在对方禁区场均触球 25 次。\n· 自 2025 年 10 月 2-1 战胜阿拉伯联合酋长国（D3 L5）以来，卡塔尔未能赢得八场国际比赛中的任何一场。"
            ],
            [
                "深度分析",
                "波斯尼亚和黑塞哥维那和卡塔尔将于周三在西雅图体育场进行 B 组最后一场比赛，以确保他们在世界杯上的活力。\n由于两支球队都只拿到一分，并且落后小组第一的加拿大队和第二名的瑞士队三分，因此至少其中一支球队肯定会被淘汰。\n在波斯尼亚之前的比赛中，塔里克·穆哈雷莫维奇在最后时刻的三个进球被红牌罚下，最终以 4-1 输给了瑞士。\n替补球员埃尔明·马赫米奇的雷鸣般的进球只是一个安慰，但这使他成为继2014年对阵阿根廷的维达·伊比舍维奇之后第二位替补攻入世界杯进球的波斯尼亚球员。\n谢尔盖·巴巴雷斯的球队现在进入这场比赛，知道失败将让他们回家。不过，他们需要在状态上进行大幅转变才能避免这种情况，因为他们在过去七场国际比赛中未尝一胜（D6，L1）。\n这场比赛的胜者有机会以小组亚军的身份晋级下一轮，但这需要获胜队扭转与加拿大队与瑞士队的负队之间的巨大净胜球差距。因此，作为最好的第三名球队之一晋级是胜利者最有可能的结果。\n“我们知道我们需要三分才能晋级。我们应该在前两场比赛中找到它们，我认为对阵卡塔尔我们有很好的机会拿下这三分，”阿米尔·哈齐亚梅托维奇说。\n“至于卡塔尔，我们会分析他们。好处是他们也必须争取胜利，所以这不会是一场谨慎的比赛。他们不是一支幼稚的球队，我们必须小心。”\n对于卡塔尔来说，除了胜利之外，别无他法，上周四在温哥华以 6-0 被加拿大队淘汰后，卡塔尔队很可能仍举步维艰。自2008年8月友谊赛1-6输给伊朗队以来，这是他们第一次丢这么多球。\n当霍曼·埃尔·阿明因对塔洪·布坎南犯规而被红牌罚下时，他们已经以 2-0 落后于加拿大队，而阿西姆·马迪博也在下半场早些时候因一次冲撞导致伊斯梅尔·科内腿部骨折而被罚下场。\n卡塔尔的控球率仅为 21%，是自 1966 年以来世界杯上第五低的控球率，并且面临 32 次射门，这是自 2014 年比利时对阵美国队 40 次射门以来单场比赛最多的一次。\n“我们很失望，但没有人放弃或举白旗。每个人都在谈论需要迅速反弹，”卡塔尔后卫佩德罗·米格尔说。\n“我们面前还有一场非常重要的比赛。我们会为胜利而战，让我们的球迷开心。我们不能让这场失利毁掉我们过去一段时间所做的一切。”\n波斯尼亚将缺席停赛的穆哈雷莫维奇，但希望埃丁·哲科能够保持足够的健康，让他在对阵加拿大的揭幕战中缺席并且在对阵瑞士的比赛中只踢了一个小时后感受到他的影响力。\n由于阿明和马迪博都被禁赛，洛佩特吉将不得不在这场关键的比赛中对防守和中场进行调整。"
            ],
            [
                "历史交锋",
                "这将是波斯尼亚和卡塔尔之间的第三次会议。\n卡塔尔队在2000年1月首次交锋中以2-0获胜，而他们唯一的另一场比赛是在2010年8月以1-1战平。\n不过，波斯尼亚之前的一场世界杯胜利是在对阵亚洲对手的情况下取得的——2014年以3-1战胜伊朗。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机使波斯尼亚队成为本场比赛的热门球队，他们在 25,000 次赛前模拟中以 67.8% 的成绩名列前茅。\n洛佩特吉的球队能否打破困境并以某种方式进入淘汰赛阶段？卡塔尔获胜的可能性只有 14.0%，这似乎不太可能。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours a Switzerland victory, with Yakin’s side winning 43.5% of the 25,000 pre-match simulations. Canada’s chances of claiming three points – and subsequently top spot in Group B – are rated at 28.1%, with a draw at 28.3%.",
        "summary_cn": "Opta 超级计算机支持瑞士队获胜，在 25,000 次赛前模拟中，雅金的球队获胜率为 43.5%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 瑞士在世界杯上对中北美洲及加勒比海地区的对手保持不败（W2 D3），并且是 Opta 超级计算机最有希望延续这一连胜纪录的球队，其胜率高达 43.5%。\n· 乔纳森·大卫在对阵卡塔尔的比赛中成为继 1930 年美国球员伯特·帕特诺德对阵巴拉圭之后第二位在决赛中上演帽子戏法的中北美洲及加勒比海国家队球员。\n· 瑞士在过去九场世界杯小组赛中仅输掉一场（5胜3平），2022年以0-1不敌巴西。"
            ],
            [
                "深度分析",
                "瑞士和加拿大将争夺 B 组第一名，周三，排名前两名的球队将在温哥华正面交锋。\n两队前两场比赛积4分，平局即可确保双双晋级淘汰赛。\n事实上，周三任何一方都无法确保晋级的唯一方法是，如果他们输掉比赛，并且波黑和卡塔尔之间的另一场 B 组比赛中的九个进球相差甚远。\n对于瑞士来说，这将是他们连续第四次在世界杯小组赛中晋级——这一壮举只有 2026 年的阿根廷、法国和巴西才能与之相媲美。\n穆拉特·亚金 (Murat Yakin) 的球队刚刚以 4-1 战胜波斯尼亚队，这也是世界杯历史上第一场在第 70 分钟后打入多达 5 个进球的比赛。\n鲁本·巴尔加斯和格兰尼特·扎卡为瑞士队进球，而约翰·曼赞比在 20 岁零 247 天的时候梅开二度，成为在世界杯比赛中作为替补球员打进两球或以上的最年轻球员，也是第一位为国家队打入两球或以上的球员。\n曼赞比随后希望有机会首发，瑞士队自 1994 年以来首次在决赛中在一场比赛中攻入 4 个或更多进球，他们希望在第二轮比赛中在加拿大对阵另一支得分能力强的球队时继续保持势头。\n共同主办方回到了同一个体育场，他们以 6-0 的比分击败了 9 人卡塔尔队，取得了世界杯上的首场胜利并以不失球的方式取得了胜利。\n加拿大队是中北美及加勒比地区足联决赛中单场比赛进球最多的国家（也是来自欧洲或南美洲以外的国家），同时追平了他们之前七场比赛的进球总数。他们在对方禁区内的 97 次触球也是世界杯比赛中球队记录最多的。\n乔纳森·大卫 (Jonathan David) 扮演了主角，他在世界杯上第二次上演了帽子戏法——继莱昂内尔·梅西 (Lionel Messi) 代表阿根廷对阵阿尔及利亚 (Algeria) 后，也是中北美洲及加勒比地区足球国家队球员在世界杯上的第二个帽子戏法，继 1930 年首届决赛中代表美国对阵巴拉圭的伯特·帕特诺德 (Bert Patenaude) 上演。\n大卫是自1982年意大利队保罗·罗西对阵巴西队以来第一位在决赛中上演帽子戏法的尤文图斯球员，也是世界杯历史上第三位在一场比赛中射正五次或以上并且在对方禁区触球超过15次的球员，仅次于尤西比奥（1966年对阵朝鲜）和乌韦·塞勒（1970年对阵意大利）。\n赛尔·拉林（Cyle Larin）在溃败期间也击中了目标。这位南安普顿前锋在对阵波黑的比赛中替补打入扳平比分的进球，成为第一位在决赛中连续比赛进球的加拿大球员。\n加拿大队历史性胜利中唯一令人不快的地方是萨索洛中场球员伊斯梅尔·科内的腿骨折，杰西·马什随后将不得不在剩下的比赛中缺席。"
            ],
            [
                "历史交锋",
                "这将是两国之间的第二次会议，也是第一次在正式比赛中举行。\n现任瑞士队主教练亚金实际上在两队2002年5月的一场友谊赛中担任防守核心。加拿大队在圣加仑以3-1获胜，托马斯·拉津斯基（Tomasz Radzinski）在每个半场都进球——保罗·斯塔尔特里（Paul Stalteri）的进球是双方的——而布莱斯·恩库福（Blaise Nkufo）在最后时刻为东道主攻入一粒安慰球。\n尽管如此，瑞士队在世界杯上从未输给过中北美洲及加勒比海地区的对手（2胜3平）。其中包括1994年他们最后一次在决赛中面对东道主，当时他们在底特律1-1战平美国队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持瑞士队获胜，在 25,000 次赛前模拟中，雅金的球队获胜率为 43.5%。\n加拿大队拿下三分并随后在 B 组中排名第一的机会为 28.1%，平局的机会为 28.3%。\n然而，最近的世界杯赛绩却让瑞士队倾斜，他们在过去的九场小组赛中赢了五场。\n他们在此期间唯一一次失败是2022年0-1逆转五届冠军巴西队。"
            ]
        ]
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
        "prediction": "The Opta supercomputer ran 25,000 pre-match simulations, with Croatia getting back on track and winning 63.0% of those. Panama are afforded just a 14.9% chance of a first World Cup victory, while the draw accounted for 22.2% of the data-led simulations.",
        "summary_cn": "Opta 超级计算机运行了 25,000 次赛前模拟，克罗地亚重回正轨并赢得了其中的 63.0%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta超级计算机预计克罗地亚获胜；他们在赛前模拟中以令人信服的 63.0% 战胜了巴拿马队。\n· 巴拿马队在世界杯四场比赛中全部输掉，只进了两个球。\n· 克罗地亚可能会第二次连续输掉世界杯比赛。"
            ],
            [
                "深度分析",
                "克罗地亚和巴拿马在世界杯揭幕战中令人失望的失利后，都希望周三在多伦多得到回应。\n兹拉科·达利奇的球队在上周三的 L 组比赛中以 4-2 输给了英格兰队。在两度落后的情况下，马丁·巴图里纳和佩塔尔·穆萨在半场结束前均扳平比分，但托马斯·图赫尔的球队在达拉斯的中场休息后占据了主导地位。\n考虑到克罗地亚在过去六场世界杯比赛中的四场比赛中输掉了首场比赛（W1 D1），达利奇可能不会太担心糟糕的开局。他们在过去两届比赛中至少仍然进入了半决赛。\n克罗地亚现在的任务是应对并避免继2002年输给厄瓜多尔和四年后输给巴西之后第二次连续输掉世界杯比赛。\n达利奇的队员们在对阵英格兰的比赛中出现了一些积极的迹象，他们的职业道德自始至终都无可挑剔。克罗地亚队在对手半场施加了 187 次高压，是本届世界杯首个比赛日中最多的球队。\n克罗地亚也有丰富的经验可供借鉴。卢卡·莫德里奇在揭幕战中首发，成为第二位参加过 10 场不同重大赛事的欧洲球员，另外一位是克里斯蒂亚诺·罗纳尔多（12 场）。\n然而，莫德里奇在比赛开始前就被换下场，他在世界杯或欧洲杯的 34 场首发中出场时间最少（58 分钟）。他希望在他为克罗地亚出场的第 200 场比赛中给人留下更多的印象，而达利奇可能会选择引进马特奥·科瓦契奇作为中场的支持者。\n巴拿马队也以失败告终，在伊伦基最后时刻的进球后，巴拿马队0-1不敌加纳队。比赛结束时，比赛时间为 94 分 04 秒。\n托马斯·克里斯蒂安森的球队在四场世界杯比赛中尚未取得一分（L4），同时他们已经丢了 12 个球，未能保持不失球，并且只进了两球。\n在 MD2 之前，只有萨尔瓦多拥有该赛事历史上最差的 100% 输球记录（六场比赛），但克里斯蒂安森可能会因他们的首场表现而受到鼓舞。\n巴拿马队在对阵加纳队的比赛中取得了 62% 的控球率和 502 次成功传球，此前在本届世界杯的一场比赛中巴拿马队的控球率从未超过 40% 或成功传球 350 次。\n何塞·科尔多巴是这些球上进步的核心人物，他尝试了 101 次传球——这是巴拿马队历史上单场比赛中传球次数最多的球员。他的 MD1 传球总数仅比 2018 年世界杯所有三场小组赛中巴拿马球员记录的传球总数少 15 次（加布里埃尔·戈麦斯传球 116 次）。\n安德烈斯·安德拉德（Andrés Andrade）也给人留下了深刻的印象，他在锦标赛首轮比赛中的断线传球次数在所有球员中排名第四（21 次）。他还与美国后卫蒂姆·雷姆并列从本方半场开始的断线传球次数最多的球员（15 次）。\n但巴拿马也投入了硬码。在 MD1 比赛中，没有哪支球队的铲断次数超过 29 次，而在 2022 年整场比赛中，只有法国队（对阵突尼斯队时有 37 次铲断）比这更多。\n再往前走，克里斯蒂安森可能会让伊斯梅尔·迪亚兹首发。他在去年的金杯赛上赢得了金靴奖，进球数是其他球员的两倍，可能会成为巴拿马队解决世界舞台上进球不足的问题的办法。"
            ],
            [
                "历史交锋",
                "这两支球队之前从未交手，但克罗地亚在过去 10 场世界杯对阵美洲球队的比赛中输掉了 7 场（2 胜 1 平）。\n达利奇的球队在此期间只保持过一场不失球，是在 2018 年世界杯上 3-0 战胜阿根廷队的比赛中实现的。\n在同一届比赛中，墨西哥在小组赛中以 1-0 战胜德国，但中北美洲及加勒比海地区国家在其他方面与欧洲球队的比赛却表现不佳。\n截至2026年世界杯首轮比赛结束，他们在过去24场对阵欧洲对手的比赛中只赢了一场（8平15负）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机运行了 25,000 次赛前模拟，克罗地亚重回正轨并赢得了其中的 63.0%。\n巴拿马队获得世界杯首胜的机会只有 14.9%，而在以数据为主导的模拟中，平局占 22.2%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer could not look past a Colombia win in Guadalajara, with Lorenzo’s side taking three points in 58% of the 25,000 pre-match simulations. Meanwhile, the chances of DR Congo pulling off another upset, and a draw are rated exactly the same at 21%.",
        "summary_cn": "Opta 超级计算机无法忽略哥伦比亚在瓜达拉哈拉的胜利，在 25,000 次赛前模拟中，洛伦佐的球队在 ​​58% 的情况下拿下了三分。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在瓜达拉哈拉开球之前，哥伦比亚在 Opta 超级计算机的模拟中以 58.0% 的胜率获胜。\n· 周三的比赛将标志着这两支球队在男子国际足球比赛中的首次交锋。\n· 刚果民主共和国在首场比赛1-1战平葡萄牙后，刚刚获得了他们在世界杯上的首个积分并攻入了他们在世界杯上的第一个进球。"
            ],
            [
                "深度分析",
                "在以3-1战胜乌兹别克斯坦开启世界杯征程后，哥伦比亚将在周三在瓜达拉哈拉迎战刚果民主共和国时寻求保持完美开局。\n这次K组比赛将是两国之间的第一次交锋，不过，就像对阵乌兹别克斯坦的情况一样，哥伦比亚不会被陌生的对手吓倒。\n洛杉矶咖啡队最近在世界杯小组赛中创造了令人印象深刻的战绩，过去七场比赛赢了六场，唯一的例外是 2018 年以 2-1 输给日本队。\n在那场比赛中，内斯托·洛伦索的球队表现出色，打进 17 个进球，仅丢 5 个球，这表明刚果民主共和国可能会度过一个艰难的夜晚。\n然而，美洲豹队在对阵葡萄牙队的比赛中表现出色，表明他们有能力给自己带来一些问题。\n塞巴斯蒂安·德萨布雷的球队结束了长达 52 年重返世界杯的等待，在休斯顿将克里斯蒂亚诺·罗纳尔多率领的葡萄牙队以 1-1 逼平，这是世界杯迄今为止最大的冷门之一。\n这一结果让他们在世界杯上获得了首个积分，事实上，这也是他们的处子进球，得益于尤阿内·维萨 (Yoane Wissa) 上半场的头球。\n1974年，他们唯一一次以扎伊尔队身份参加世界杯，他们以总比分14-0输掉了三场小组赛。\n不过，这个版本已经暗示这将是一个非常不同的故事。\n尽管对阵葡萄牙队的控球率仅为 24.6%（第一比赛日所有球队中控球率最低），但豹队将他们的射门次数限制在 7 次，只有 5 支球队的失球数更少。\n在球场的另一端，德萨布雷的球队采取了更加雄心勃勃的做法，八次射门中有六次是在禁区外射门（75%），这是首轮比赛中比例最高的球队。\n然而，这些努力中只有两次达到了目标，这是他们在对阵哥伦比亚时肯定希望改进的一个领域。\n然而，复制针对路易斯·迪亚斯和詹姆斯·罗德里格斯等人的防守努力可能会是一个更大的挑战，因为洛伦佐的球队在过去 10 场世界杯比赛中每场都有进球。\n事实上，这是本届世界杯上与卫冕冠军阿根廷队并列最长的连续进球纪录。\n周三的胜利也将确保哥伦比亚队连续第三次进入世界杯淘汰赛阶段，此前他们曾在 2014 年和 2018 年从小组赛阶段晋级。在此之前，他们四次闯入淘汰赛只有一次。\n如果洛斯卡夫特罗斯队想要延续这样的势头，很大程度上可能取决于迪亚兹，他在对阵乌兹别克斯坦队的比赛中凭借进球和助攻表现出色。\n这位边锋还在乌兹别克斯坦禁区内完成了六次触球，同时尝试了四次带球，赢得了八次对抗和五次犯规——比当晚任何其他哥伦比亚球员都多。\n与此同时，刚果民主共和国将再次向维萨寻求灵感。\n如果这位纽卡斯尔联前锋在瓜达拉哈拉进球，他将成为继 2018 年埃及球员穆罕默德·萨拉赫之后第二位在前两届世界杯比赛中均取得进球的非洲球员。"
            ],
            [
                "历史交锋",
                "周三的比赛将带来很多未知因素，因为这将是哥伦比亚和刚果民主共和国之间的首次交锋。\n这也将是刚果民主共和国第二次与南美足联球队交锋，此前刚果民主共和国在世界杯前几天的一场赛前友谊赛中以 2-1 不敌智利队。\n1990年，哥伦比亚在世界杯首场比赛中以1-2不敌喀麦隆，输给了非洲对手。但此后，他们以一球的优势赢得了所有三场此类比赛：1990年1-0战胜突尼斯，2014年2-1战胜科特迪瓦，2018年1-0战胜塞内加尔。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机无法忽略哥伦比亚在瓜达拉哈拉的胜利，在 25,000 次赛前模拟中，洛伦佐的球队在 ​​58% 的情况下拿下了三分。\n与此同时，刚果民主共和国再次爆冷和平局的几率完全相同，均为 21%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer predicts a close contest in New Jersey, with marginal favourites Norway winning 44.7% of its 25,000 pre-match simulations. Senegal triumphed 30.5% of the time, while a draw was shown a 24.9% chance.",
        "summary_cn": "Opta 超级计算机预测新泽西州将有一场势均力敌的比赛，在 25,000 次赛前模拟中，排名靠后的挪威队获胜率为 44.7%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在首场比赛以 4-1 战胜伊拉克后，挪威成为本次比赛的热门球队，Opta 超级计算机的获胜概率为 44.7%，而塞内加尔的获胜概率为 30.5%。\n· 周一的比赛将是挪威和塞内加尔在世界杯上的首次交锋。\n· 塞内加尔在前五场世界杯对阵欧洲对手的比赛中仅输掉一场（3胜1平）后，现在在过去的三场比赛中全部输掉了。"
            ],
            [
                "深度分析",
                "挪威队以4-1大胜伊拉克队，迎来了期待已久的重返世界杯决赛圈，他们希望周二在纽约新泽西体育场对阵塞内加尔队时保持完美开局。\n维京人队在波​​士顿的揭幕战无疑令人印象深刻，埃尔林·哈兰德在里奥·奥斯蒂加德也进球之前攻入了他在世界杯上的处子球，而艾门·侯赛因最后的乌龙球帮助球队取得了胜利。\n这一结果使挪威队跻身第一组榜首，与赛前热门法国队积分相同。\n这也延续了他们非凡的状态，索尔巴肯的球队现在在过去 11 场正式比赛中全部获胜，打进 50 个球，仅丢 7 个球。\n事实上，他们上一次失利要追溯到 2024 年 10 月的欧洲国家联赛中以 5-1 输给奥地利。\n周二可能还会有一段历史触手可及。挪威队从未在单届世界杯比赛中赢得过一场以上的比赛，今年只是他们第四次闯入决赛。\n与此同时，塞内加尔队在首场比赛中遭遇了近乎相反的开局，他们以 3-1 轻松击败法国队。\n基利安·姆巴佩和他的队友在纽约证明了自己太强大了，尽管易卜拉欣·姆巴耶在伤停补时阶段的安慰性进球至少给了塞内加尔一些可以继续前进的东西。\n这位巴黎圣日耳曼新星年仅18岁零143天，成为世界杯历史上进球最年轻的非洲球员。\n随着最艰难的小组赛比赛结束，帕普·蒂奥希望他的球队能够反弹，并与挪威队进行一场精彩的战斗，以保持他们的锦标赛活力。\n目前，Opta 超级计算机给特兰加雄狮队晋级的可能性为 56.5%，而挪威队由于开局强劲，晋级的可能性为 98.6%。\n如果塞内加尔想要扭转局面，蒂奥就必须寻找解决防守漏洞的办法，尤其是在与状态良好的哈兰德会面之前。\n在参加今年世界杯的 48 支球队中，只有沙特阿拉伯队（第 2 轮对阵西班牙队之前有 17 支球队）比塞内加尔队连续不失球的时间更长。\n事实上，他们在过去 12 场世界杯比赛中每场都有失球——这种情况可以追溯到 2002 年首次亮相，当时他们以 1-0 战胜法国队。\n这一数据肯定会给已经在世界杯上留下浓墨重彩的哈兰德带来鼓舞。\n这位挪威强队在过去11场代表挪威参加的比赛中每场都有进球，并且在过去5场比赛中每场都进球超过一个。自2023年初以来，他在20场国家队比赛中的17场进球。\n凭借 Martin Ødegaard 的优质服务，塞内加尔可能会度过另一个艰难的夜晚。\n挪威队对阵伊拉克队的 62 次突破中，有 8 次打破了对手的防线，队长厄德高负责其中的一半（4/8）——相当于整个伊拉克队的总和。他的 42 次传球中只有 1 次传球失误，并在最后三区完成了全部 16 次传球，这表明限制他的影响力可能是塞内加尔希望取得结果的关键。"
            ],
            [
                "历史交锋",
                "周二的比赛将是挪威和塞内加尔在男子世界杯上的首次交锋，也是他们 20 多年来的首次交锋。\n两队上次交锋是2006年3月在达喀尔举行的一场友谊赛，当时特兰加雄狮队以2-1获胜。\n挪威此前在世界杯上只遇到过一次非洲对手，1998年后来居上，2-2战平摩洛哥。\n与此同时，塞内加尔在大舞台上对阵欧洲球队的比赛中开局良好，前五次交锋中仅输掉一场（3胜1平）。但此后他们在过去三场比赛中全部失利，包括首场比赛输给法国队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机预测新泽西州将有一场势均力敌的比赛，在 25,000 次赛前模拟中，排名靠后的挪威队获胜率为 44.7%。\n塞内加尔获胜的概率为 30.5%，平局的概率为 24.9%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours an Algeria victory, with Petković’s side winning 60.7% of the 25,000 pre-match simulations. Jordan’s chances of claiming a first World Cup win are rated at 17.6%, with a draw at 21.7%.",
        "summary_cn": "Opta 超级计算机支持阿尔及利亚获胜，佩特科维奇的球队在 ​​25,000 次赛前模拟中获胜率为 60.7%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 阿尔及利亚在过去 11 场世界杯比赛中只赢了一场（D3 L7），但以 60.7% 的胜率成为 Opta 超级计算机的获胜热门。\n· 约旦在过去六场各项赛事中未尝一胜（平2平4负），与之前的13场比赛（平7胜2平）一样多。\n· 阿尔及利亚此前从未在世界杯决赛中输掉过前两场比赛。"
            ],
            [
                "深度分析",
                "约旦和阿尔及利亚周二将在旧金山湾体育场展开对决，他们的目标是从 J 组开局失利中恢复过来。\n首次参加世界杯的约旦队在首场对阵奥地利的比赛中保持了 75 分钟的领先优势，阿里·奥尔万在罗马诺·施密德的首开纪录后将球队扳平，但最终因亚赞·阿拉伯队的乌龙球和马尔科·阿诺托维奇的点球而以 3-1 落败。\n与此同时，阿尔及利亚队时隔12年后重返决赛，迎来了莱昂内尔·梅西(Lionel Messi)大师级的表演，阿根廷队长的帽子戏法让他们0-3落败。\n这是他们在世界杯上并列最惨重的失利，追平了40年前他们在墨西哥0-3输给西班牙的情况。\n阿尔及利亚队在 1982 年首次亮相时赢得了前三场比赛中的两场（排名第一），之后在过去 11 场世界杯比赛中只赢了一场（平三负七）。\n尽管如此，弗拉基米尔·佩特科维奇的球队还是会在一定程度上感到高兴，因为从纸面上看，他们J组最艰难的一场比赛已经过去了，而且他们对阵卫冕冠军的表现也有一些积极的一面。\n艾萨·曼迪 (Aïssa Mandi) 成为有记录以来第一位在世界杯比赛中完成 100 次或以上传球的非洲球员（自 1966 年以来），这位后卫在他尝试的 105 次传球中完成了 100 次（95.2%）。\n法雷斯·柴比构成的威胁也将鼓舞阿尔及利亚。这位边锋在今年早些时候的非洲国家杯期间为耳廓狐队射门次数最多，共打进 8 次，他参与了球队在第 1 比赛日的 7 次射门中的 4 次（3 次射门，1 次创造机会）。\n阿尔及利亚队将向查伊比这样的球员寻求灵感，因为他们希望继续保持世界杯决赛圈前两场比赛从未输过的记录。\n与此同时，乔丹希望奥尔万能够在国际舞台上延续他丰富的表现。在对阵奥地利的比赛中，他扳平比分的进球是他 10 场比赛中的第八个进球，比他同期的任何队友都多了 6 个进球。\n贾迈勒·塞拉米的球队在世界杯上表现出色，赢得了 52.7% 的对决，在最后三区的传球准确率高于奥地利（70.2% 比 68.6%），同时在射门（11 次）和射正次数（4 次）方面与对手不相上下。\n约旦还完成了 15 次带球过人，是自 2006 年科特迪瓦对阵阿根廷队 17 次带球以来首场世界杯比赛中过人次数最多的球队，而他们 62.5% 的成功率（24 次中的 15 次）是自 1986 年伊拉克对阵巴拉圭以来首场比赛中完成 15 次带球成功率最高的球队（65.2% - 23 次中 15 次）。\n到目前为止，乔丹无疑已经对自己做出了不错的评价，并且有积极的方面可以继续发展，但对于首次参加锦标赛的球员来说，积分现在至关重要。\n阿根廷队在J组最后一场比赛中等待的事实更加强调了在这里取得积极成果的重要性，因为他们试图将他们期待已久的决赛首秀延续到第一关之外。"
            ],
            [
                "历史交锋",
                "这将是约旦和阿尔及利亚之间的第四次交锋，也是自 2004 年 5 月友谊赛以来的首次交锋。双方在安纳巴以 1-1 战平，阿卜杜勒马利克·切拉德 (Abdelmalek Cherrad) 在比赛一小时内破门，抵消了马哈茂德·谢尔巴耶 (Mahmoud Shelbaieh) 上半场的射门。\n两国之间的前两次交锋都是在阿拉伯杯上。\n1974 年 10 月，阿尔及利亚在大马士革以 6-0 的比分大胜，但约旦最终在 14 年后在安曼以 2-1 的比分战胜了失利。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持阿尔及利亚获胜，佩特科维奇的球队在 ​​25,000 次赛前模拟中获胜率为 60.7%。\n约旦首次夺得世界杯冠军的几率为 17.6%，平局几率为 21.7%。\n然而，表格表明这对于塞拉米的球队来说将是一项艰巨的任务，因为他们在最不合时宜的时间里经历了状态的下滑。\n约旦目前在所有比赛的最后 6 场比赛中未尝一胜（平 2 平 4 场）——与之前 13 场比赛（平 7 平 2）的失利次数一样多。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "阿根廷队看起来将在两场比赛中取得两胜，Opta 超级计算机预测他们的获胜概率为 65.4%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 25,000 次赛前模拟，Opta 超级计算机给出的阿根廷获胜概率为 65.4%。\n· 阿根廷可能成为第七个在连续四场世界杯比赛中至少打入三球的国家，也是继 1998 年至 2002 年西班牙之后的第一个国家。\n· 奥地利最近 10 个世界杯进球中有 7 个是定位球进球（3 个角球、2 个点球、1 个任意球、1 个直接任意球）。"
            ],
            [
                "深度分析",
                "周一，阿根廷队在达拉斯体育场与奥地利队进行一场精彩的 J 组比赛，莱昂内尔·梅西 (Lionel Messi) 有望创造男子 FIFA 世界杯历史。\n梅西在 3-0 战胜阿尔及利亚的比赛中上演职业生涯第 61 次帽子戏法（俱乐部 50 次，阿根廷 11 次），距离超越米罗斯拉夫·克洛泽（16 球）成为赛事历史最佳射手仅差一球。\n如果他能在对阵奥地利的比赛中进球，这位八次金球奖得主也将成为世界杯历史上第三位连续六场比赛进球的球员。\n法国队贾斯特·方丹和巴西队雅伊尔津霍分别在 1958 年和 1970 年的单项赛事中取得了这一成绩，而梅西的成功可以追溯到四年前，阿尔比塞莱斯特队在卡塔尔世界杯上获得期待已久的胜利。\n尽管年事已高，这位 38 岁的球员对阿根廷的影响力丝毫没有动摇的迹象。在对阵阿尔及利亚的比赛中，他直接参与了球队 10 次射门中的 8 次（6 次射门，创造了 2 次机会），并且在对阵奥地利的比赛中也将发挥同样的影响力。\n虽然梅西的进攻表现理所当然地成为了头条新闻，但莱昂内尔·斯卡罗尼的球队成功地阻止了阿尔及利亚队的一脚射门也毫无价值。\n如果击败奥地利、约旦未能战胜阿尔及利亚，他们将确保以小组头名出线，与H组亚军进行较量。\n如果奥地利队赢了这场比赛，他们也有可能以小组第一的身份出线，但在首场3-1战胜约旦的比赛中经过长时间的努力后，他们需要提高水平。\n“我们知道阿根廷有多棒，”年轻的中场球员保罗·万纳说道。 “我们尊重他们，但我们对自己的优势充满信心。如果我们将我们的品质带到球场上，我们将为任何球队带来问题。”\n在看到罗马诺·施密德的首开纪录被阿里·奥尔万取消后，直到第76分钟，奥地利才重新取得领先——而这只有在亚赞·阿尔·阿拉伯攻入自家球门时才发生。\n马尔科·阿诺托维奇最后的点球只是让比分看起来比实际表现更有说服力。\n尽管如此，奥地利在各项赛事中仍取得了四连胜，并且在过去的12场比赛中取得了10场胜利，1平1负。\n如果他们能在对阵阿根廷队的比赛中再次取得胜利，这将是他们自1982年以来首次在世界杯上取得背靠背胜利。\n不过，奥地利对大卫·阿拉巴（David Alaba）、斯特凡·波什（Stefan Posch）和亚历山德罗·舍普夫（Alessandro Schöpf）的可用性表示担忧。波什在对阵约旦的比赛中下巴骨折后制作了一个特殊的面具。这三人一直在与球队其他成员分开训练，并面临一场比赛以恢复健康。\n马塞尔·萨比策有望保住自己在首发阵容中的位置，并第 100 次代表国家队出场，这使他与亚历山大·德拉戈维奇并列奥地利历史出场名单上的第四名。现在只有安德烈亚斯·赫尔佐格（103）、阿拉巴（本场比赛前114）和阿瑙托维奇（本场比赛前134）排在他前面。\n对于阿根廷队，斯卡罗尼预计将做出一些改变，其中可能会看到贡萨洛·蒙蒂尔（Gonzalo Montiel）让位给纳韦尔·莫利纳（Nahuel Molina），后者从轻微的肌肉拉伤中恢复过来。"
            ],
            [
                "历史交锋",
                "两支球队之间并没有太多历史交锋，之前的交锋都是友谊赛，最近一次交锋已经是 36 年前的事了。\n那是在维也纳 1-1 战平，他们 1980 年的交锋也在那里举行。最终阿根廷队以 5-1 获胜，迭戈·马拉多纳在这场比赛中上演了唯一的国际帽子戏法。\n阿根廷在过去八场世界杯小组赛对阵欧洲国家的比赛中只输掉了一场（4胜3平），克罗地亚在2018年以3-0击败了他们。\n与此同时，奥地利在历史上一直与南美对手作斗争。自1982年世界杯1-0战胜智利以来，他们在对阵此类对手的10场比赛中只赢了一场（平4负5），那场胜利是在2017年11月与乌拉圭的友谊赛中取得的。"
            ],
            [
                "赛前预测（Opta 超算）",
                "阿根廷队看起来将在两场比赛中取得两胜，Opta 超级计算机预测他们的获胜概率为 65.4%。\n分享战利品的可能性为 20.7%，而奥地利队爆冷全取三分的可能性为 13.9%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer understandably regards France as heavy favourites to win this match, and any other result would be a huge shock. Deschamps’ side were triumphant in 88.8% of the 25,000 pre-match simulations. The next most likely result is a draw, at 7.9%, while Iraq earned a famous victory in 3.4% of simulations.",
        "summary_cn": "可以理解的是，Opta 超级计算机认为法国队是赢得这场比赛的热门球队，任何其他结果都将是一个巨大的冲击。在 25,000 次赛前模拟中，德尚的球队获胜率为 88.8%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 法国队被认为是赢得这场比赛的热门球队，在 Opta 超级计算机的 25,000 次模拟中，法国队以 88.8% 的胜率名列前茅。\n· 伊拉克在之前的世界杯四场比赛中全部失利，并可能成为世界杯历史上第一个在前五场比赛中全部失利的亚洲国家。\n· 法国队正在寻求连续第四届世界杯在前两场比赛中都获胜——此前他们在世界杯上参加的 13 场比赛中只有一场（1998 年）做到了这一点。"
            ],
            [
                "深度分析",
                "法国队周一将在费城体育场迎战伊拉克队，这对基利安·姆巴佩来说可能是一个重要时刻。\n这位皇马前锋将代表法国队出场第 100 次，如果他出场的话，他在第一轮对阵塞内加尔的比赛中梅开二度，成为法国队历史上的总进球数和男足世界杯历史最佳射手，他的目标是打破世界杯历史进球纪录。\n如果莱昂内尔·梅西没有先到达那里的话。\n姆巴佩在对阵塞内加尔的比赛中梅开二度，将他的世界杯进球数增至 14 个，比米洛斯拉夫·克洛泽的纪录还少了两球，但几小时后，梅西在对阵阿尔及利亚的比赛中上演帽子戏法，超越了队伍，阿根廷人现在与克洛泽分享了冠军头衔。\nMD2比赛顺序的改变意味着梅西的阿根廷队将在法国对阵伊拉克之前直接对阵奥地利。\n因此，我们可以期待一个历史性的夜晚。如果梅西在对阵奥地利的比赛中扳平比分，姆巴佩就会知道，他可以通过帽子戏法，在 27 岁时成为这项赛事的历史最佳射手。\n法国队在对阵塞内加尔队的比赛中花了一些时间，可能在半场结束时就落后了，但主教练迪迪埃·德尚的改变让他们在下半场进入了最佳状态。\n最值得注意的是奥斯曼·登贝莱和迈克尔·奥利塞的角色转换；登贝莱在比赛中首发出场10号，奥利塞打右翼，但德尚将他们换换，效果非常好。\n许多人认为奥利塞是一名出色的组织核心，而随着这位拜仁慕尼黑球星在洞里打球并准备好接应姆巴佩的跑动，法国队的后场威胁也随之增加。事实上，正是奥利塞为姆巴佩的助攻帮助法国队在下半场中取得了领先。\n奥利塞的助攻是他在代表法国队出场的 18 场比赛中第 10 粒进球（7 粒进球，3 次助攻）；对于 21 世纪的蓝军来说，只有姆巴佩（17 岁）更快地达到了这一里程碑。与此同时，对阵伊拉克的进球或助攻将使他在连续三场比赛中直接为法国队进球做出贡献。\n如果法国队在这场比赛中获胜，他们将连续第四届世界杯在前两场比赛中均获胜，而此前他们在世界杯上的 13 场比赛（1998 年）只取得了一场胜利。\n不要让德尚对他的前锋线做出一些改变。他在对阵塞内加尔的比赛中只进行了两次换人，直到第80分钟登贝莱被布拉德利·巴科拉换下，两分钟后后者进球。\n拉扬·切尔基在正常比赛时间还剩三分钟时取代了德西雷·杜埃，尽管他客串得相当安静，但他会觉得他上赛季在曼城的俱乐部表现值得首发，而对手的防守可能比塞内加尔队的防守要低得多。\n无论谁为法国队效力，这对伊拉克来说都将是艰难的一天。他们最初在对阵挪威的比赛中坚守阵地，随后在 MD1 中以 4-1 失利。质量上的巨大差异很快就显现出来，埃尔林·哈兰德梅开二度。\n伊拉克在此前的世界杯四场比赛中全部失利，并可能成为世界杯历史上第一个在前五场比赛中全部失利的亚洲国家。\n艾门·侯赛因 (Aymen Hussein) 会觉得他有发言权；他在亚足联世界杯预选赛中打进了 12 个进球，是任何队友的两倍，并在伊拉克对阵挪威的比赛中攻入一球，这是他们在世界杯上的第二个进球。\n尽管如此，只要梅西没有击败他，所有的目光都会集中在姆巴佩身上，而他对进球和另一项纪录的追求就会继续下去。"
            ],
            [
                "历史交锋",
                "这将是法国与伊拉克的首次交锋。\n伊拉克在过去四场对阵欧洲对手的所有比赛中赢了两场，这是他们之前 16 场此类比赛中取得的胜利数量。\n法国队在各项赛事中与亚洲对手的前 13 次交锋中均未尝败绩，此后在最近的两场比赛中均以 1-0 的比分输给了中国队和日本队，且未取得进球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "可以理解的是，Opta 超级计算机认为法国队是赢得这场比赛的热门球队，任何其他结果都将是一个巨大的冲击。在 25,000 次赛前模拟中，德尚的球队获胜率为 88.8%。\n第二个最可能的结果是平局，为 7.9%，而伊拉克以 3.4% 的模拟赢得了一场著名的胜利。"
            ]
        ]
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
        "prediction": "The Opta Supercomputer’s 25,000 pre-match simulations established Egypt as clear favourites, with a 59.6% chance of success. New Zealand came out on top in just 17.7% of those simulations, with a draw rated at 22.7%.",
        "summary_cn": "Opta 超级计算机进行了 25,000 次赛前模拟，使埃及成为明显的热门球队，成功的几率为 59.6%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据国际足联的排名，新西兰队比下一个对手低 56 位，而获胜的机会只有 17.7%，新西兰队将承担起他们熟悉的弱者地位。\n· 虽然全白队在这个级别的七场比赛后尚未尝到成功的滋味，但只有洪都拉斯队（九场）比埃及队（八场）在世界杯上没有获胜的次数更多。"
            ],
            [
                "深度分析",
                "在美国以平局结束 G 组比赛后，新西兰和埃及将前往加拿大参加周日的潜在关键比赛。\n虽然法老队首场被比利时逼平，但他们的下一个对手却两次被伊朗追平，四支球队都锁定一分。\n马瑟韦尔边锋伊利亚·贾斯特延续了上赛季在俱乐部层面表现出的良好状态，成为第一个在世界杯比赛中进球超过一次的新西兰人。\n尽管他们未能取得胜利，但达伦·贝兹利的球队确实表现出了积极的意图：他们在前 30 分钟内的 3 次射正次数相当于新西兰队在 2010 年整场比赛中的射门次数。\n他们不仅两次取得领先（比前六场世界杯比赛的次数总和还要多），还在对方禁区内触球 21 次、控球率 51.5% 并完成 376 次传球。\n这些都是新西兰在一场世界杯比赛中的最高数据，表明这支被广泛赞誉为有史以来最有才华的球队可能已经准备好获得最高分。\n曾经的兼职游客，全白队现在是一个可靠的参与者，在世界杯的最后四场比赛中都取得了平局。顺便说一句，只有G组的对手比利时曾连续五次打平（1998年至2002年）。\n克里斯·伍德是美国历史上的最佳射手和鼓舞人心的队长，贾斯特在对阵伊朗的比赛中两次进球都是由克里斯·伍德助攻的。\n伍德在前场领先，还在伊朗半场内施加了 41 次高强度压力，如果新西兰队想要在本周末取得突破，可能也需要做出类似的贡献。\n虽然历史将沉重地压在贝兹利一边，但埃及却要承受更大的负担。尽管他们是 1934 年第一个参加世界杯的非洲国家，但他们也在等待一场难以捉摸的胜利。\n在埃玛姆·阿舒尔 (Emam Ashour) 在全球决赛中攻入比利时最快进球（时间为 19:00）后，法老队错失了最后一次机会，有望击败比利时。然而，他的惊人一击还不够。\n埃及队在世界杯上首次在半场领先，但穆罕默德·哈尼试图阻止罗梅卢·卢卡库进球时的乌龙球让他们失去了首场胜利。\n七届非洲冠军埃及尚未在最大的舞台上证明这一地位，但如果他们今年要这样做，那么穆罕默德·萨拉赫仍然是他们希望的核心。\n这位利物浦传奇人物在预选赛不败的比赛中贡献了 60% 的进球（9 粒进球，3 次助攻），之后在阿舒尔 34 岁生日那天对阵比利时的比赛中完成了爆炸性的射门。\n与今年决赛中其他几位年迈的球星一样，再加上同样 34 岁、相对低调的伍德，这可能是萨拉赫的最后一支舞。\n新秀前锋哈姆扎·阿卜杜勒卡里姆代表了新的一代；周一，他在第 76 分钟后取代了令人尊敬的队长，成为埃及最年轻的世界杯球员（18 岁 165 天）。\n这位巴塞罗那年轻球员的首发时机肯定会到来，但主教练霍萨姆·哈桑——在他自己的球员时代就是一位冷静的终结者——将再次让萨拉赫与奥马尔·马穆什搭档。"
            ],
            [
                "历史交锋",
                "这些国家不仅从未在世界杯上相遇过，而且这将是新西兰在世界杯上首次对阵非洲对手。\n埃及队此前3次与全白队交锋，取得2胜1平保持不败。最近一次是两年前在开罗1-0友谊赛的胜利。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机进行了 25,000 次赛前模拟，使埃及成为明显的热门球队，成功的几率为 59.6%。\n新西兰在这些模拟中仅 17.7% 名列前茅，平局率为 22.7%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer struggled to see past a win for Uruguay, who claimed all three points in a massive 67.2% of 25,000 pre-match simulations. Cape Verde are afforded just a 12.2% chance of victory in the same data-led sims, while the draw accounted for 20.6% of scenarios.",
        "summary_cn": "Opta 超级计算机艰难地见证了乌拉圭队的胜利，在 25,000 次赛前模拟中，乌拉圭队以 67.2% 的准确率全取三分。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计乌拉圭将赢得这场比赛，因为他们在赛前模拟中以 67.2% 的成绩名列前茅。\n· 佛得角从未对阵过乌拉圭，但在与南美足联对手的仅有的两次交锋中都遭遇失败。\n· 乌拉圭队在过去的九场世界杯小组赛中只输掉了一场。"
            ],
            [
                "深度分析",
                "尽管出于不同的原因，乌拉圭和佛得角在开局中取得了令人惊讶的成绩，但在周日的世界杯比赛中，H组的席位仍然悬而未决。\n尽管佛得角在近 100 分钟内面对欧洲冠军球队 27 次射门，但在国际足联顶级赛事的首场比赛中，佛得角还是令人震惊地以互交白卷逼平了西班牙队。巧合的是，乌拉圭队在揭幕战中也尝试了 27 次射门，但周一晚些时候以 1-1 战平沙特阿拉伯队，结果令人沮丧。\n佛得角很可能会在迈阿密对阵马塞洛·贝尔萨的球队时再次陷入困境，鉴于这一蓝图在对阵西班牙队时的效果，他们在第一场比赛中被马克西·阿劳霍第80分钟的扳平比分拯救。\n布比斯塔一定会对他的球队在无球时的纪律性感到高兴。尽管西班牙拥有超过 74% 的控球率，但佛得角只犯规一次，这是自 1966 年以来世界杯比赛中犯规最少的球队。\n四十岁的门将沃齐尼亚也为佛得角队带来了鼓舞人心的表现。他的 7 次扑救是自 2020 年 10 月以来在对阵西班牙的任何一场比赛中保持不失球的门将最多的一次，当时乌克兰的乔治·布什昌 (Georgiy Bushchan) 扑救了 8 次。\n沃齐尼亚在皮科·洛佩斯的带领下，得到了他面前坚韧后防线的帮助。他在 MD1 上解围 11 次，是自 2006 年突尼斯队的卡里姆·哈吉 (Karim Haggui) 对阵沙特阿拉伯队 (13 次) 以来，非洲球队在世界杯上首次亮相的最多解围次数。\n考虑到乌拉圭队在 MD1 的空战中尝试了 34 次传中，是 A 组到 H 组中最多的球队，洛佩斯应该会在这里再次忙碌。这也是他们在世界杯比赛中的最多记录（自 1966 年以来），但只有 9 次成功。\n阿劳霍将再次成为任何创造性探索的核心。除了扳平比分之外，他创造的五次机会——全部来自定位球——是自2010年迭戈·弗兰对阵墨西哥队以来乌拉圭球员在世界杯比赛中创造的最多机会。\n马蒂亚斯·奥利维拉（Matías Olivera）首次以中后卫而非边后卫身份参加本次比赛，他也给人留下了深刻的印象。在 MD1 比赛中，他为乌拉圭队完成了最多的断线传球（11 次）、前卫持球（31 次）以及赢得最多的对决（8 次）。\n然而，贝尔萨可能对费尔南多·穆斯莱拉感到失望，因为门将穆罕默德·坎诺的头球攻门，让阿卜杜拉·阿姆里为沙特阿拉伯首开纪录。\n如果穆斯莱拉在世界杯上再次获得信任而不是塞尔吉奥·罗切特，他将超越埃丁森·卡瓦尼（17 岁），并打破乌拉圭世界杯历史上出场次数最多的纪录。\n贝尔萨也可能不会因开局平局而惊慌失措。根据 Opta 超级计算机的数据，乌拉圭仍有 74.7% 的机会晋级 32 强，在该组中仅次于西班牙（96.3%）。\n最近的历史也表明没有理由担心。乌拉圭在过去 9 场国际足联全球舞台上的小组赛中仅输掉一场（6 胜 2 平），在 2022 年卡塔尔世界杯上以 2-0 输给了葡萄牙。\n这 9 场比赛总共只进了 15 个进球（11 个进球，4 个进球），平均每场 1.7 个进球，贝尔萨知道他的球队如果想要掌控自己的命运，这一次需要更加冷静的表现。\n但随着所有四支球队都取得一分，佛得角可能会感觉到另一个机会，可以更接近不太可能的进步。他们进入 32 强的机会从 Opta 超级计算机在北美踢球之前给出的 32.9% 跃升至 47.6%。"
            ],
            [
                "历史交锋",
                "周日将是这两对组合的首次交锋，虽然仍然有明显的热门，但佛得角与西班牙的历史性平局表明任何事情都有可能发生。\n鉴于乌拉圭在世界杯上对阵非洲球队的五场比赛中保持不败（W3 D2），他们有望突破这里的界限。\n佛得角已经对阵加纳（两次）、塞内加尔、南非和埃及，这将是乌拉圭在比赛中遇到的第五个非洲足联国家。\n布比斯塔的球队在对阵南美洲球队的比赛中仅输过两场——四年前他们0-1负于厄瓜多尔，今年3月2-4负于智利。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机艰难地见证了乌拉圭队的胜利，在 25,000 次赛前模拟中，乌拉圭队以 67.2% 的准确率全取三分。\n在同样以数据为主导的模拟游戏中，佛得角获胜的几率仅为 12.2%，而平局占了 20.6% 的情况。"
            ]
        ]
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
        "prediction": "The Red Devils triumphed in 67.5% of the 25,000 pre-match simulations, while Iran’s chances of victory are rated at just 13.2%. The probability of a draw, then, is left at 19.3%.",
        "summary_cn": "毫不奇怪，Opta 超级计算机无法忽视比利时在洛杉矶这场比赛中的胜利。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta超级计算机预测比利时是这场对阵伊朗的比赛中的热门球队，获胜概率高达67.5%。\n· 周日的比赛将是比利时和伊朗在男子国际足球比赛中的首次交锋。\n· 伊朗队在世界杯对阵欧洲对手的 10 场比赛中只赢了一场（D2 L7）。"
            ],
            [
                "深度分析",
                "比利时和伊朗在各自的世界杯首场比赛中都后来居上，经过一场艰苦的平局，使得周日在洛杉矶的比赛成为一场双方都输不起的比赛。\n这将是两国之间的首次交手，为竞争激烈的 G 组增添了另一层阴谋。\n虽然比利时肯定会认为自己是晋级热门，但鲁迪·加西亚知道他的球队在对阵埃及的揭幕战中表现低于标准杆。\n在埃玛姆·阿舒尔的精彩射门落后后，红魔在中场休息之前并没有什么紧迫感。\n然而，罗梅卢·卢卡库的引进提供了急需的催化剂，他的出现迫使穆罕默德·哈尼打进乌龙球，最终球队1-1战平。\n这一结果使比利时队在世界杯上的不胜纪录扩大到了三场（平2负1），而此前他们在世界杯上的13场比赛中只取得了两场胜利（11胜2平）。\n尽管如此，Opta 超级计算机仍然让加西亚的球队有 90.9% 的机会从 G 组晋级，而伊朗晋级下一轮的几率为 47.4%。\n阿米尔·加勒诺伊的球队也在揭幕战中奋力拼搏，以 2-2 战平新西兰，拉明·雷扎伊安和穆罕默德·莫赫比在破门两侧各入一球，抵消了伊利亚·贾斯特的梅开二度。\n继2014年0-0战平尼日利亚和2018年1-0战胜摩洛哥之后，伊朗队在世界杯首场比赛中第三次避免失利。\n不过，他们在世界杯的前两场比赛中从未获得过积分，这意味着如果他们在周日避免再次失利，那么一小段历史将会等待着他们。\n这将是伊朗第十次在世界杯上面对国际足联世界排名前十五的国家，此前九场此类比赛中有七场以失败告终。\n他们唯一的一场胜利是在1998年对阵美国队，而他们还在2018年英勇地1-1逼平了葡萄牙。\n虽然伊朗可能还有一座大山需要攀登，但他们将从比利时最近在大舞台上门前的干旱中得到一些鼓励。\n不包括乌龙球，自2022年米奇·巴舒亚伊在小组赛对阵加拿大队的比赛中进球以来，红魔还没有在世界杯上打进过进球。\n事实上，比利时队在本届世界杯上的最后 46 次射门均未进球，尽管这些尝试总计 5.66 个预期进球 (xG)。\n虽然射门仍然令人担忧，但加西亚仍然可以依靠杰里米·多库的混乱能量来创造机会。在第一轮对阵埃及的比赛中，这位曼城边锋在 10 次带球尝试中完成了 3 次，六次赢得控球权并赢得 5 次犯规。此前只有一名球员在单场世界杯比赛中创下如此高的数据，巴西队的维尼修斯·儒尼奥尔在 2022 年对阵瑞士队时做到了这一点。\n但如果加西亚要彻底解决比利时的进球问题，他需要卢卡库迅速重新找回他的进球手感。\n他在对阵埃及的比赛中替补出场，这是他为比利时出场的第 127 次，这使他与托比·阿尔德韦雷德 (Toby Alderweireld) 并列比利时历史出场名单第三位，仅次于扬·维尔通亨 (Jan Vertonghen)（157 场）和阿克塞尔·维特塞尔 (Axel Witsel)（138 场）。然而，自2018年对阵突尼斯队梅开二度以来，那不勒斯前锋还没有在世界杯上进球。"
            ],
            [
                "历史交锋",
                "周日的比赛意义不明，因为这将是比利时和伊朗在任何赛事中的首次交锋。\n比利时在过去 14 场比赛中保持不败，他们将满怀信心地到来，尽管加西亚知道他的球队如果想要晋级，就不能再犯一次失误。\n与此同时，伊朗队在世界杯对阵欧洲对手的 10 场比赛中只赢了一场（平 2 负 7），不过这场胜利是在他们最近一次此类交锋中取得的——2022 年世界杯小组赛 2-0 战胜威尔士。"
            ],
            [
                "赛前预测（Opta 超算）",
                "毫不奇怪，Opta 超级计算机无法忽视比利时在洛杉矶这场比赛中的胜利。\n在 25,000 次赛前模拟中，红魔的获胜率为 67.5%，而伊朗队的获胜机会仅为 13.2%。那么，平局的概率为 19.3%。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "西班牙队可能以不太令人印象深刻的方式开始了他们的比赛，但凭借 Opta 超级计算机，他们仍然是这场比赛中获胜的明显热门。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为西班牙是本场比赛的压倒性热门，获胜概率为 87.4%，而沙特阿拉伯的获胜概率为 3.8%。\n· 自上一次世界杯进球以来，西班牙队已经完成了 2,500 次传球并射门 49 次。\n· 在第一场比赛中，穆罕默德·阿尔·奥伊斯为沙特阿拉伯队对阵乌拉圭队做出了九次扑救。"
            ],
            [
                "深度分析",
                "西班牙队将在 2026 年世界杯 H 组第二场比赛中对阵沙特阿拉伯队，渴望证明自己的实力。\n许多人都期待路易斯·德拉富恩特的欧洲冠军队将于 7 月 19 日在纽约新泽西体育场举起奖杯。\n但他们的比赛以非常令人失望的方式开始，因为他们被首次参加比赛的佛得角队以0比0逼平，老门将沃齐尼亚和他面前坚忍的防守让西班牙的超级巨星感到沮丧。\n现在人们的注意力转移到周日在亚特兰大体育场举行的比赛，拉罗亚希望在那里打下一个标记，并重新强调他们在赛前热门球队中的地位。\n然而，西班牙队可能会有些担忧，他们在过去的四场世界杯比赛中都没有取得任何胜利（平局、平局）——这是他们在世界杯上最长的连续不胜纪录。\n此外，在过去三届比赛中，他们只赢了九场比赛中的两场，输掉一场，另外六场打平。\n他们最近两场世界杯比赛都以互交白卷告终；西班牙队从未在比赛中三场比赛没有进球。自从2022年小组赛第3轮对阵日本队第11分钟进球以来，他们已经完成了2500次传球和49次射门，但无济于事。\n西班牙队在对阵佛得角的平局中拥有 74.3% 的控球率，这是世界杯比赛中未能进球的球队有记录以来第四高的数字（自 1966 年以来）。另外三场控球率最高的比赛中有一场是在 2022 年对阵摩洛哥的比赛中（76.8%）。\n拉明·亚马尔在对阵佛得角的比赛中被任命为替补，他可能希望在伤后继续恢复健康的过程中扮演更重要的角色。在 MD1 中，尽管他只在第 71 分钟才上场（5 次），但他还是尝试带球次数最多的球员。相比之下，西班牙的首发边锋加维（0）和费兰·托雷斯（3）仅尝试了 3 次。\n队友罗德里在比赛中完成了六次突破防线传球，是 A-H 组中最多的球员。他还完成了五次突破线传球并射门，这是世界杯首轮比赛中与土耳其队的哈坎·恰尔汗奥卢并列最多的球员。\n沙特阿拉伯队在 H 组首场比赛中以 1-1 战平乌拉圭队，拿下重要一分，考虑到佛得角意外战平西班牙，这一分可能尤其重要。\n阿卜杜拉·阿姆里 (Abdulelah Al Amri) 在第 41 分钟为乔治·多尼斯 (Georgios Donis) 的球队取得领先，但马克西·阿劳霍 (Maxi Araújo) 在距离比赛结束仅 10 分钟时为南美球队扳平比分。\n在那场比赛中，沙特阿拉伯让乌拉圭队在禁区内触球41次，这是自1998年法国队触球46次以来，乌拉圭队在世界杯比赛中被触球次数最多的球队。\n他们还面临 47 次传中（包括角球），这是他们在单场比赛中并列最多的传中（1994 年对阵比利时时也有 47 次传中）。\n守门员穆罕默德·阿尔·奥瓦伊斯在球门之间忙碌，全场比赛做出了九次扑救。只有马布鲁克·扎耶德在 2006 年对阵西班牙的比赛中为沙特阿拉伯队在世界杯比赛中进球数最多（11 球）。\n阿尔·奥维斯在五场比赛中阻止了三个进球（10.0 xGOT，7 个失球），但尚未保持不失球。\n沙特阿拉伯希望在前两场比赛中首次保持不败，这是他们第七次参赛。"
            ],
            [
                "历史交锋",
                "西班牙此前曾与沙特阿拉伯交锋过3次，每次都取得胜利，打进9球，只丢2球。\n这些胜利包括他们之前唯一一次世界杯交锋，即2006年世界杯小组赛中以1-0获胜。\n沙特阿拉伯在世界杯上曾 11 次遭遇欧洲对手，其中 10 次失利。\n然而，巧合的是，他们的唯一一场胜利确实发生在美国，1994 年，沙特阿拉伯在华盛顿以 1-0 战胜了比利时。这场比赛因赛义德·阿尔-奥维兰 (Saeed Al-Owairan) 的一记轰动性个人进球而引人注目，他从本方半场带球射入制胜球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "西班牙队可能以不太令人印象深刻的方式开始了他们的比赛，但凭借 Opta 超级计算机，他们仍然是这场比赛中获胜的明显热门。\n事实上，他们的获胜概率为 87.4%，而沙特阿拉伯的获胜概率仅为 3.8%，平局的概率为 8.8%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer produced 25,000 pre-match simulations, and Türkiye came out as winners in 48.4% of the simulations. Paraguay only prevailed in 25.5%, with a draw rated at 26.0% – given the circumstances, the latter result would suit neither side.",
        "summary_cn": "Opta 超级计算机进行了 25,000 次赛前模拟，土耳其队在 48.4% 的模拟中获胜。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，尽管土耳其队在第一比赛日表现不佳，但他们有 48.4% 的机会赢得小组赛第二场对阵巴拉圭的比赛。\n· 巴拉圭队的获胜概率只有25.5%，预计不会结束世界杯四场不胜的局面。\n· 土耳其队在揭幕战中射门30次，是自2006年以来在世界杯比赛中没有进球最多的球队（葡萄牙对英格兰，31次），也是自1974年乌拉圭对瑞典（30次）以来在加时赛没有进球最多的球队。"
            ],
            [
                "深度分析",
                "土耳其和巴拉圭已经面临提前淘汰的前景，周五在旧金山相遇时，土耳其和巴拉圭都不能再犹豫了。\n巴拉圭队以 4-1 惨败美国队，而土耳其队则出人意料地以 2-0 输给澳大利亚队，这是他们在 11 场世界杯比赛中第二次没有进球。\n这并不是因为缺乏尝试。文森佐·蒙特拉的球队完成了 71 次中场突破线传球，是自 2010 年以来世界杯上最多的球队；他们还完成了 30 次射门，其中 8 次来自皇马球员阿尔达·居勒。\n阻止他们的是澳大利亚新秀帕特里克·比奇，他在比赛中做出了八次扑救。这是自 2002 年土耳其传奇人物鲁斯图·雷茨贝尔 (Rüstü Reçber) 在对阵巴西队的比赛中打进九球以来，在世界杯首秀中打进九球的门将。\n这是土耳其队自去年欧足联预选赛0比6输给西班牙队以来的首场失利，结束了各项赛事八场不败的记录（七胜一平）。\n然而，我们有理由相信他们能够直接反弹——自 2024 年 3 月以来，他们还没有连续输过比赛。\n上一次发生在五年前的竞技比赛中，当时他们以三连败退出 2020 年欧洲杯，这让人想起土耳其在大舞台上的麻烦历史。\n虽然土耳其球队在过去 13 场重大赛事中输掉了 9 场，但巴拉圭在 2026 年世界杯的主办国之一遭受重创后，在过去 4 场世界杯比赛中没有赢过任何一场。\n古斯塔沃·阿尔法罗的球队抵达北美时以稳健着称，他们在 18 场南美洲杯预选赛中没有失球超过两次，其中包括对阿根廷和巴西的里程碑式胜利。\n然而，在对阵美国队的比赛中，阿尔比罗哈队在半场结束时就已经0-3落后，这是他们之前16场世界杯比赛中上半场失球数的两倍。他们还遭遇了 16 次高失误——这是自 1966 年以来的最高失误纪录。\n简而言之，巴拉圭处于劣势。\n现在，他们必须避免第二次输掉前两场比赛；上一次发生这种情况是在2006年，当时他们在小组赛中被英格兰和瑞典击败。\n由于只有前两名可以保证晋级，南美球队理想情况下需要在对阵土耳其的比赛中获得最高分；然而，他们在过去 14 场对阵欧洲对手的世界杯比赛中只赢了两场（平 5 负 7）。\n如果巴拉圭想要获胜，胡里奥·恩西索可能是不可或缺的，他刚刚成为巴拉圭自 1966 年以来世界杯进球最年轻的贡献者，仅次于罗克·圣克鲁斯（2002 年 20 岁）。\n这位 22 岁的球员可能身材矮小——前锋米格尔·阿尔米龙和安东尼奥·萨纳布里亚也不是巨人——但他的球队并不害怕采取直接路线：门将奥兰多·吉尔在对阵美国队的比赛中进入最后三区的传球次数比其他任何人都多（8 次）。\n这应该是一场风格的冲突，因为土耳其队采取了更加耐心的方式，队长兼中场节拍器哈坎·恰尔汗奥卢（Hakan Çalhanoglu）设定了节奏。\n作为左翼的关键人物，费迪·卡迪奥格鲁在最后三区的传球次数最多（59 次），并在对阵澳大利亚的比赛中创造了 5 次机会。迄今为止，在 2024 年欧洲杯和本届世界杯上，他创造了 17 个进球，比其他土耳其球员多了 7 个进球。"
            ],
            [
                "历史交锋",
                "土耳其队 24 年来首次闯入全球决赛，而巴拉圭队（16 年来）将首次在世界杯上相遇。\n两队此前唯一一次交锋是 1995 年 6 月在智利进行的一场互交白卷的友谊赛。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机进行了 25,000 次赛前模拟，土耳其队在 48.4% 的模拟中获胜。\n巴拉圭仅以25.5%的胜率获胜，平局率为26.0%——考虑到这种情况，后者的结果对双方都不利。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "这场比赛是今年小组赛中两支球队在 FIFA 世界排名上差距最大的一场比赛，巴西（第 6 位）比海地（第 84 位）高出约 78 位。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为巴西是本场比赛的压倒性热门，获胜概率为 87.3%，海地为 4.3%。\n· 维尼修斯·儒尼奥尔在世界杯五场比赛中参与了四个进球。\n· 海地队在 MD1 上的射门次数比 C 组其他球队都多（15 次）。"
            ],
            [
                "深度分析",
                "安切洛蒂的球队在首场比赛中1-1战平摩洛哥，在第21分钟落后于伊斯梅尔·萨巴里的首开纪录，随后维尼修斯·儒尼奥尔打进一记精彩的扳平比分。\n不过，桑巴军团知道他们还有更多的工作要做，作为创纪录的五次冠军得主，他们仍然希望有机会深入锦标赛。\n虽然他们可能在第一轮比赛中与摩洛哥战平，但对这支南美豪门来说，好消息是，自从 1978 年阿根廷世界杯上两场比赛战平以来，他们在世界杯前两场比赛中都没有输过。\n当时，世界杯参赛资格只有16支球队，而巴西队在第二轮仅获得B组第二名，无缘决赛。\n然而，巴西最近两场世界杯小组赛均未能获胜，2022年0-1不敌喀麦隆，今年又1-1战平摩洛哥。此前他们只有一次在小组赛三场比赛中未尝一胜，那是在 1974 年和 1978 年（D2 L1）。\n2026 年首次参赛的球队有 48 支，巴西显然仍处于不错的位置，要相信他们不会进入最后 32 强，需要勇敢的赌注。\n尽管如此，人们还是担心在对阵摩洛哥的比赛中，他们面临的射门次数（14 次）比他们自己的射门次数（12 次）还要多。这是自2006年四分之一决赛对阵法国队以来，巴西队在世界杯比赛中首次出现这样的情况，结束了连续22场比赛以射门优势的局面。\n如果他们想要第六次赢得世界杯，维尼修斯可能至关重要，而这位皇马王牌现在已经在五场世界杯比赛中参与了四个进球（2个进球，2次助攻），这意味着他每98分钟就会进球或助攻——这是过去两届世界杯上所有巴西球员中进球或助攻最多的。\n与此同时，海地结束了长达 54 年的世界杯参赛资格等待，上一次晋级世界杯还要追溯到 1974 年，当时他们在西德小组赛中未能小组出线。\n你会觉得，他们这次进入淘汰赛的希望取决于在 C 组揭幕战中对阵苏格兰的结果。\n由于约翰·麦克金的制胜球偏出，导致塞巴斯蒂安·米涅的球队以 1-0 失利，这意味着塞巴斯蒂安·米涅的球队确实面临着提前淘汰的危险。\n鉴于海地目前已经输掉了所有世界杯比赛，在这些比赛中只进球两次、失球 15 次，所以预兆也不是特别好。\n此前只有三个国家输掉了前五场世界杯比赛——墨西哥（前九场）、萨尔瓦多（前六场）和加拿大（前六场）。\n海地在 MD1 上的射门次数确实比 C 组其他球队多（15 次），并且在对方禁区内的触球次数与巴西队并列榜首（22 次），但在这场比赛中他们必须付出一些努力才能复制这些数据。\n汉内斯·德尔克鲁瓦是海地队在输给苏格兰队的比赛中表现出色的球员之一，在对阵史蒂夫·克拉克的球队的比赛中，他的 66 次传球没有失误一次。\n他的控球数（6 次）和解围数（6 次）在队友中并列第一。这也是海地人在世界杯比赛中完成传球最多的一次。"
            ],
            [
                "历史交锋",
                "这场比赛标志着两国队首次在世界杯上相遇。\n不过，他们之前曾有过三次交手，巴西队在所有这些比赛中都取得了胜利。\n事实上，桑巴军团在这些比赛中已经打进了 17 个进球，并且仅向海地队丢过一次球。\n无独有偶，上一次交锋也是在美国，那就是2016年美洲杯，巴西队在佛罗里达州奥兰多以7-1大胜。\n目前球队成员阿利森·贝克尔和马奎尼奥斯在那场比赛中出场，菲利普·库蒂尼奥上演帽子戏法。"
            ],
            [
                "赛前预测（Opta 超算）",
                "这场比赛是今年小组赛中两支球队在 FIFA 世界排名上差距最大的一场比赛，巴西（第 6 位）比海地（第 84 位）高出约 78 位。\n因此，Seleção 被认为是凭借 Opta 超级计算机获胜的压倒性热门也就不足为奇了。\n目前他们获胜的几率为 87.3%，而海地队只有 4.3% 的几率成为世界杯上最著名的冷门之一。平局被认为是 8.4% 的命中率。\n巴西可能没有取得他们所期望的胜利开局，但他们仍有 55.3% 的可能性在 C 组中拔得头筹，并有 97% 的可能性进入 32 强。在撰写本文时，他们有 5.4% 的可能性赢得锦标赛。\n海地队对苏格兰队的惨败严重削弱了他们出线的机会。他们晋级淘汰赛的几率只有7.5%，小组第一的几率也只有0.5%。"
            ]
        ]
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
        "prediction": "Tunisia’s decision to replace Lamouchi with Renard after just one game offers an interesting dynamic to this match, but the Opta supercomputer is still confident Japan will come out on top, winning the World Cup’s 1,000 th match in 60.7% of its 25,000 simulations. The next most likely result is a draw, at 22.9%. Meanwhile, Tunisia have a 16.4% of earning a surprising win.",
        "summary_cn": "突尼斯队在一场比赛后就决定用雷纳德取代拉穆奇，这为这场比赛提供了一个有趣的动态，但 Opta 超级计算机仍然相信日本队将脱颖而出，在 25,000 次模拟中以 60.7% 的胜率赢得了世界杯的第 1,000 场比赛。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 日本被认为是这场比赛的明显夺冠热门，在 Opta 超级计算机的 25,000 次模拟中，日本队以 60.7% 的胜率名列前茅。\n· 突尼斯队在 MD1 比赛中以 5-1 负于瑞典队，这是他们世界杯历史上最惨重的失利。\n· 尽管自 2018 年以来，日本队在 FIFA 世界杯小组赛的七场比赛中每场都失球，但日本队只输掉了其中的两场比赛（W3 D2），而他们在之前的四场比赛中首先失球的比赛中只输了一场（W2 D1）。"
            ],
            [
                "深度分析",
                "突尼斯队在蒙特雷体育场迎战日本队将是 FIFA 世界杯历史上的第 1000 场比赛，距世界杯首场比赛 96 年后，蒙得维的亚主场迎战法国 4-1 墨西哥和美国 3-0 比利时。\n可以说，突尼斯队本届世界杯的开局相当坎坷。周日晚上在墨西哥举行的首场小组赛中，球队以 5-1 惨败给瑞典队，这并没有受到该国足球高层的欢迎，到了周二，主教练萨布里·拉穆奇 (Sabri Lamouchi) 被埃尔韦·雷纳德 (Hervé Renard) 取代。\n拉穆奇的离开意味着他成为世界杯历史上第一位在仅仅一场比赛后就被解雇的主教练。这位法国人在世界杯前只执教了突尼斯的四场比赛，其中两场在本月早些时候对阵奥地利和比利时的比赛中均以零分告负。\n这场对阵日本的比赛之后就是小组赛最后一场对阵荷兰的比赛，突尼斯足协显然已经没有时间可以浪费了。\n他们确实有提前解雇的历史。 1998年世界杯，突尼斯队在前两场比赛均未获胜后解雇了亨利克·卡斯佩尔恰克，但在第三场比赛战平后仍以小组垫底身份出线。\n雷纳德 (Renard) 上任时拥有丰富的经验。这将是他在国际管理中的第九个角色，包括多次在赞比亚和沙特阿拉伯任职，以及一段时间负责法国女队。\n在成功带领沙特阿拉伯队通过预选赛后，他原定在今年夏天随沙特阿拉伯队执教，但在四月份被乔治·多尼斯取代。不过，如果他希望从这支突尼斯队中取得任何成功，他手上的任务就很艰巨。\n他们在第一轮比赛中以 5-1 负于瑞典队，这是他们在世界杯上最惨重的失利；他们仅在 2018 年（8 个）和 2006 年（6 个）的单届赛事中总体失球数更多。\n拉穆奇可能会对守门员阿卜杜勒穆希布·查马克的表现感到不满，他两次失误直接导致进球，预期进球数为-2.88。\n继1982年智利对阵德国之后，突尼斯成为历史上第二支在世界杯比赛中在禁区外丢三球的球队（自1966年以来）。\n当然，这对日本来说都是好消息，在MD1对阵荷兰的比赛中两次落后并赢得一分后，日本将感觉自己处于有利地位，可以利用突尼斯的痛苦。\nHajime Moriyasu 的球队已经证明自己是一支非常难以击败的球队。尽管自 2018 年以来，日本队在世界杯小组赛的七场比赛中每场都失球，但日本队只输掉了其中的两场比赛（W3 D2），而他们在之前的四场比赛中首先失球的比赛中只输了一场（W2 D1）。\n守保对替补的大量使用无疑是这一记录的关键。自 2022 年世界杯开赛以来，日本队的 7 个进球中有 5 个是由替补球员打进 (3) 或助攻 (2)。事实上，上一场对阵荷兰队的比赛中，他们在第89分钟扳平比分的进球是由替补出场的小川功起助攻的，尽管他显然是在试图进球。球从镰田大知的头顶偏出。\n敬请关注谷口正吾在日本三后卫中路的出色控球能力。在世界杯比赛中传球次数超过 50 次的日本球员中，谷口对阵荷兰队的成功率最高（98% – 49/50），而在那场比赛中，只有维吉尔·范戴克（14 次）和扬·保罗·范赫克（11 次）的断线传球次数超过了他的 8 次。\n34岁的圣。特鲁伊登后卫是个大器晚成的球员，他大部分的国家队出场都是在三十多岁之后。"
            ],
            [
                "历史交锋",
                "突尼斯队和日本队在世界杯上第二次相遇。他们的首次交锋发生在 2002 年的小组赛中，当时日本队在主场以 2-0 获胜，其中值得注意的是中田秀寿在世界杯上的唯一进球。\n突尼斯在对阵日本的六场比赛中只赢了一场——2022 年 6 月在日本举行的麒麟杯友谊赛中以 3-0 获胜。其他五场比赛日本队全部获胜。\n日本队在世界杯前两场对阵非洲对手的比赛中获胜后，在过去两场比赛中都没有取得胜利，2014年以2-1输给科特迪瓦，然后在2018年以2-2战平塞内加尔。"
            ],
            [
                "赛前预测（Opta 超算）",
                "突尼斯队在一场比赛后就决定用雷纳德取代拉穆奇，这为这场比赛提供了一个有趣的动态，但 Opta 超级计算机仍然相信日本队将脱颖而出，在 25,000 次模拟中以 60.7% 的胜率赢得了世界杯的第 1,000 场比赛。\n接下来最有可能的结果是平局，为 22.9%。与此同时，突尼斯队以 16.4% 的比例取得了​​令人惊讶的胜利。"
            ]
        ]
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
        "prediction": "Across the 25,000 pre-match simulations, Ecuador came on top in a whopping 84.5% of them. The probability of a draw is 10.2%, with Curaçao taking all three points in just 5.3% of projections.",
        "summary_cn": "毫不奇怪，Opta 超级计算机使厄瓜多尔成为这场比赛的压倒性热门。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在首场比赛惨败之后，Opta 超级计算机给出的结果是库拉索岛对阵厄瓜多尔的获胜概率仅为 5.3%。\n· 自 2022 年 2-0 战胜卡塔尔以来，厄瓜多尔在世界杯上已经三场比赛未尝胜绩（平 1 平 2）。\n· 这是库拉索岛的第二场世界杯比赛——只有三个中北美洲及加勒比地区国家队在前两场比赛中取得过一场胜利（美国，1930年，古巴，1938年，哥斯达黎加，1990年）。"
            ],
            [
                "深度分析",
                "周六，库拉索岛将在堪萨斯城体育场举行的世界杯 E 组比赛中迎战厄瓜多尔队，希望能从首场惨败给德国队的失利中恢复过来。\n当利瓦诺·科梅南西亚 (Livano Comenencia) 攻入库拉索岛在世界杯上的第一个进球，以 1-1 战胜德国队时，在短暂的欢乐和兴奋之后，事情很快就变糟了，迪克·阿德沃卡特 (Dick Advocaat) 的球队以 7-1 惨败。\n这使得库拉索岛成为第二支在首场世界杯比赛中失球至少七个的球队。 1954年，韩国队以0比9输给匈牙利队，成为第一名。\n然而，阿德沃卡特仍然相信蓝波队能够取得成功，并避免与海地（1974年10个）、刚果民主共和国（1974年11个）和韩国（1954年16个）一起成为仅有的在前两场比赛中丢球超过10个的球队。\n“我们需要把这变成一场精彩的比赛，”阿德沃卡特在输给德国队后告诉记者。\n“我们可以在第二场和第三场比赛中带来惊喜。最终我们会很高兴我们成为世界上最大的足球锦标赛的一部分。”\n如果科梅南西亚再次进球帮助他们实现这一目标，他将成为第三位在中北美洲及加勒比地区足联国家队前两场世界杯比赛中都取得进球的球员。伯特·帕特诺德 (Bert Patenaude) 是 1930 年第一个为美国队实现这一壮举的人，但自 1938 年埃克托·索科罗 (Héctor Socorro) 为古巴队实现这一壮举以来，没有人做到过。\n如果库拉索岛再次失利，而科特迪瓦队在E组的另一场比赛中避免输给德国队，他们将被淘汰。\n在费城首场比赛中，科特迪瓦队首场比赛中阿马德·迪亚洛 (Amad Diallo) 的进球以 1-0 落后，厄瓜多尔不太可能对他们感到自满。\n这是厄瓜多尔在各项赛事 20 场比赛中首次失利，这种失利一直延续到 2024 年 9 月以 1-0 输给巴西。\n他们在世界杯上已经三场不胜，这是他们在世界杯历史上最长的连续不胜纪录（另外还有2006年至2014年期间的三连败）。\n塞巴斯蒂安·贝卡塞切的球队在进入比赛时也知道，如果他们惨败，他们的世界杯很可能就会结束——唯一能拯救他们的就是德国队战胜科特迪瓦队。\n厄瓜多尔很可能认为自己处于这样的境地很不幸，在阿马德补时制胜球之前，阿兰·明达、恩纳·瓦伦西亚和约翰·耶博阿在对阵科特迪瓦的比赛中击中了门框。\n但由于德国是他们E组的最后对手，他们不能错过这个机会。\n“当你没有按照自己想要的方式开始时，焦虑就会出现，”贝卡塞斯说。\n“但现在我们比以往任何时候都需要更多的信念、更多的信念、更多的信心。”\n威廉·帕乔和莫伊塞斯·凯塞多的出色分布应该使他们能够在对阵库拉索岛的比赛中控制控球权，库拉索岛很可能会打一场反击比赛。\n预计双方都不会面临任何伤病问题。"
            ],
            [
                "历史交锋",
                "这将是厄瓜多尔和库拉索岛的首次交锋，但贝卡塞斯的球队在对阵中北美洲及加勒比海对手的比赛中状态稳定。\n自2019年6月2-3输给墨西哥以来，厄瓜多尔在此前的13场此类比赛中保持不败，其中7胜6平。\n他们在过去两届世界杯对阵中北美洲及加勒比海国家队的比赛中也取得了胜利，2006年3-0击败哥斯达黎加，2014年2-1击败洪都拉斯。\n与此同时，库拉索岛在过去三场与南美洲球队的比赛中只输掉了一场（1胜1平）。然而，那是在 2023 年 3 月的一场友谊赛中以 7-0 击败阿根廷，其中包括莱昂内尔·梅西 (Lionel Messi) 的帽子戏法。"
            ],
            [
                "赛前预测（Opta 超算）",
                "毫不奇怪，Opta 超级计算机使厄瓜多尔成为这场比赛的压倒性热门。\n在 25,000 次赛前模拟中，厄瓜多尔以高达 84.5% 的成绩名列前茅。平局的概率为 10.2%，而库拉索岛全取三分的概率仅为 5.3%。\n库拉索岛知道，没有人指望他们能从这场比赛中得到任何东西，但通过分别从西班牙和葡萄牙身上拿分，刚果民主共和国和佛得角已经表明，在这场比赛中经验不足的球队也可以有自己的一天。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours an 11th straight Germany victory in all competitions, with Nagelsmann’s side winning 44.2% of the 25,000 pre-match simulations. Ivory Coast’s chances of claiming three points are rated at 30.1%, with a draw at 25.7%.",
        "summary_cn": "Opta 超级计算机支持德国队在所有比赛中取得 11 连胜，纳格尔斯曼的球队在 ​​25,000 次赛前模拟中获胜率为 44.2%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 德国在过去 10 场比赛中赢得了所有比赛，是 Opta 超级计算机最喜欢的球队，在 44.2% 的模拟中战胜科特迪瓦，延续了这一记录。\n· 科特迪瓦从未在单届世界杯上赢得多场比赛。\n· 德国队在过去七场世界杯比赛中没有一场保持零失球。"
            ],
            [
                "深度分析",
                "德国队和科特迪瓦队周六在多伦多体育场对阵时，都希望在世界杯E组中取得背靠背胜利。\n四届世界冠军在首轮比赛中表现出色，为首次参加锦标赛的库拉索岛队带来了火力洗礼，他们以 7-1 击败库拉索岛队，延续了丰富的状态。\n相比之下，科特迪瓦队则凭借阿马德·迪亚洛第 90 分钟的制胜球以 1-0 戏剧性地战胜厄瓜多尔队。\n德国队似乎恰逢其时，以 7-1 击败库拉索队，取得各项赛事的十连胜。这是自 1979 年 5 月至 1980 年 6 月约瑟夫·德沃尔 (Josef Derwall) 执教期间的 12 场连胜以来，他们最长的连胜纪录。\n第一比赛日，朱利安·纳格尔斯曼的球队菲利克斯·恩梅查、尼科·施洛特贝克、贾马尔·穆西亚拉、纳撒尼尔·布朗和德尼兹·昂达夫均取得进球，凯·哈弗茨梅开二度。\n这位阿森纳前锋是唯一一位在过去四场重大赛事（2020年欧洲杯、2022年世界杯、2024年欧洲杯和2026年世界杯）中为德国队进球的球员，他在这四场比赛中的八个进球是他的队友的两倍（穆夏拉和尼克拉斯·菲尔克鲁格各进四球）。\n然而，在球场的另一端，德国队已经连续七场世界杯比赛没有保持不失球。只有在 1934 年至 1954 年（九）之间，他们才经历了更长的未能在决赛中被淘汰的情况。\n与此同时，自 2006 年主办世界杯以来——当时他们以战胜哥斯达黎加和波兰的方式开场——Die Nationalelf 还没有赢得过前两场比赛。\n这将鼓励科特迪瓦申办球队首次在单届世界杯上取得多次胜利。\n此外，大象队还从未在决赛中连续不失球。事实上，尽管在对阵厄瓜多尔的比赛中遭遇了 12 次射门——这是他们在世界杯比赛中不失球最多的一场比赛，但埃默塞·法埃的球队顶住了压力，在最后时刻全取三分。\n阿马德是费城的英雄，他替补出场，出色地引导威尔弗里德·辛戈的方传球回家。他的致胜进球是在89分32秒时打进的，这是自20年前意大利16强对阵澳大利亚时托蒂在第94分26秒点球破门以来，世界杯上替补球员打入的最新进球（不包括加时赛和乌龙球）。\n阿马德刚刚在对阵厄瓜多尔的比赛中客串，他希望有机会在对阵德国的比赛中首发。如果他做到了，这位曼联边锋将有望成为继2014年热尔维尼奥之后第二位在连续世界杯比赛中进球的科特迪瓦人。"
            ],
            [
                "历史交锋",
                "这将是两国之间的第二次会面，也是第一次在竞争中交锋。\n他们之前唯一一次交锋发生在2009年11月，当时他们在友谊赛中2-2战平。\n卢卡斯·波多尔斯基在盖尔森基兴首开纪录，在埃马纽埃尔·埃布埃和塞杜·杜姆比亚的进球帮助科特迪瓦队扭转了比赛局面后，他还在伤停补时阶段扳平了比分。\n除此之外，德国在与非洲对手的八场世界杯比赛中只输掉了一场（五胜二平），1982 年以 2-1 不敌阿尔及利亚，尽管他们在那一年打进了决赛。\n至于科特迪瓦人，他们在世界杯对阵欧洲国家的四场比赛中只赢了一场（平一负二），在2006年小组赛中以2-0落后的情况下以3-2击败塞尔维亚和黑山——尽管他们已经确定出局。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持德国队在所有比赛中取得 11 连胜，纳格尔斯曼的球队在 ​​25,000 次赛前模拟中获胜率为 44.2%。\n科特迪瓦取三分的几率为30.1%，平局的几率为25.7%。\n然而，历史并不利于大象队，他们此前从未在单届世界杯上赢过两场比赛，也没有在连续几场比赛中保持不失球。"
            ]
        ]
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
        "prediction": "Over 25,000 pre-match simulations, the Oranje came out on top in 55.8% of the outcomes, suggesting that Koeman’s charges look likely to bounce back and claim their first win at the 2026 World Cup. A Swedish victory stands at just 21.9% probability, but a single point – with a 22.3% likelihood of a draw – should still be enough for Potter’s side to seal their place in the last 32.",
        "summary_cn": "尽管瑞典在 MD1 中凭借令人惊叹的进攻表现横扫突尼斯，但根据 Opta 超级计算机的数据，荷兰是这场 F 组比赛中最有希望获胜的球队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机使荷兰队成为本场对阵瑞典队的比赛的热门球队，在 25,000 次赛前模拟中获胜率为 55.8%。\n· 自 2010 年决赛以 1-0 输给西班牙以来，荷兰队在过去 13 场世界杯比赛中都避免了失利（正常时间）——这是世界杯历史上所有球队的最长不败纪录，与 1958 年至 1966 年间的巴西队并列。\n· 瑞典在揭幕战对阵突尼斯的比赛中打进的 5 个进球已经追平了他们在 2018 年世界杯上整个小组赛阶段的进球数，而且他们只是在前六届世界杯的其中一场（1994 年有 6 个进球）中小组赛进球数比他们多。"
            ],
            [
                "深度分析",
                "2026 年世界杯小组赛仅有四场全欧洲比赛中的第三场，荷兰队将在休斯敦体育场迎战瑞典队，两支球队都渴望从首轮比赛中积攒一些动力。\n作为曾闯入世界杯决赛但未获胜的五个国家中的两个（1974 年、1978 年和 2010 年的荷兰；1958 年的瑞典），罗纳德·科曼和格雷厄姆·波特的球队都希望在 2026 年世界杯上尽可能晋级。\n橙衣军团在达拉斯体育场对阵日本队的首场比赛中似乎已经拿下三分，但镰田大地在第 88 分钟扳平比分，让科曼的球队以 2-2 战平。\n维吉尔·范戴克和克雷森西奥·萨默维尔（中村圭人的第一个扳平球的双方）的进球让荷兰队有望取得胜利，但镰田在角球后的头球偏转意味着战利品被分享。\n结果，荷兰在最近两场世界杯比赛中都以 2-2 战平（2022 年四分之一决赛中也对阵阿根廷），此前在世界杯上只有 3 场比赛未尝胜绩——1978 年至 1990 年间连续 5 场比赛未尝胜绩。\n除了萨默维尔在荷兰队的处子秀中进球外，范迪克还打入了他在重大赛事中的首个进球，成为荷兰队第二年长的世界杯进球者（34岁零341天），仅次于2010年对阵乌拉圭的乔瓦尼·范布隆克霍斯特。\n莱恩·格拉文伯奇在他的世界杯首秀中为荷兰队攻入两粒进球，他的进球贡献数与他之前为荷兰队出场 27 场比赛中贡献的进球数一样多（1 粒进球，1 次助攻）。\n在达拉斯的那场平局是荷兰队第一次在世界杯比赛中两次领先但没有获胜，这可能会给瑞典带来更多信心，因为他们希望在 F 组两场比赛中取得两场胜利。\n波特的球队在蒙特雷球场几乎完美无缺，布莱顿的亚辛·阿亚里在七分钟内首开纪录，并在下半场补时阶段攻入第五个进球。\n瑞典队的另外三粒进球是亚历山大·伊萨克和维克多·吉克雷斯在半场结束时在两边各进一球，替补球员马蒂亚斯·斯文伯格在阿亚里结束比赛之前打进第四球。\n伊萨克在下半场助攻了吉克雷斯和斯文贝里，他的三粒进球已经成为自 2002 年亨利克·拉尔森（同样三粒进球）以来单届世界杯上瑞典球员中进球数最多的球员。\n斯文伯格替补上场后仅 18 秒就射入进球，这是自 1966 年以来世界杯比赛中替补球员第二快的进球，仅次于 2002 年乌拉圭队对阵塞内加尔队的理查德·莫拉莱斯（16 秒）。\n瑞典队对阵突尼斯队的比赛是他们在世界杯单场比赛中进球数第二高的表现，此前瑞典队在 1938 年四分之一决赛中以 8-0 战胜古巴队。\n然而，瑞典队此前在世界杯上对阵欧洲国家的七场小组赛中只赢了一场——不过这场胜利确实是在美国本土取得的，在 1994 年世界杯上以 3-1 击败了俄罗斯队。"
            ],
            [
                "历史交锋",
                "作为两个距离很近的欧洲国家，荷兰和瑞典已经举行过 20 次会面；最近一次是在 2017 年 10 月，当时罗本的梅开二度帮助荷兰队在 2018 年世界杯预选赛中以 2-0 获胜。\n橙衣军团 9 场胜利中，瑞典队取得了 7 场胜利，在过去 7 场对阵荷兰队的比赛中只取得了一场胜利，并在 2011 年 10 月以 3-2 获胜，获得了 2012 年欧洲杯的参赛资格。\n这将是荷兰队和瑞典队之间的第二次世界杯比赛——他们在 1974 年小组赛中的第一次比赛以互交白卷结束，但更为出名的是“克鲁伊夫转身”的到来，荷兰“全攻全守足球”风格开始占据主导地位。"
            ],
            [
                "赛前预测（Opta 超算）",
                "尽管瑞典在 MD1 中凭借令人惊叹的进攻表现横扫突尼斯，但根据 Opta 超级计算机的数据，荷兰是这场 F 组比赛中最有希望获胜的球队。\n在超过 25,000 次赛前模拟中，橙衣军团在 55.8% 的结果中名列前茅，这表明科曼的球队很可能会反弹并赢得 2026 年世界杯的首场胜利。\n瑞典获胜的概率仅为 21.9%，但单取一分（平局的可能性为 22.3%）仍足以让波特的球队锁定 32 强席位。"
            ]
        ]
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
        "prediction": "The Opta supercomputer gives Morocco a 91.6% chance of progressing to the knockout stage, while Scotland are assigned an 80.6% probability, making Friday’s result potentially decisive in the battle for qualification.",
        "summary_cn": "根据 Opta 超级计算机的数据，摩洛哥在波士顿开赛前占据上风，在 25,000 次赛前模拟中，阿特拉斯雄狮队的获胜率为 54.9%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在世界杯开局战平巴西后，Opta 超级计算机支持摩洛哥以 54.9% 的优势获胜。\n· 两队此前唯一一次交锋是在1998年世界杯小组赛中，摩洛哥队以3-0轻松获胜。"
            ],
            [
                "深度分析",
                "当两队周五在波士顿体育场相遇时，摩洛哥希望能够超越苏格兰，在世界杯 C 组中取得领先。\n阿特拉斯雄狮队 1-1 战平巴西队，为苏格兰夺取小组头名打开了大门，史蒂夫·克拉克的球队上周日以 1-0 险胜海地队，实现了这一目标。\n约翰·麦克金 (John McGinn) 证明了自己的与众不同，他在第 28 分钟射入制胜球，击败了约翰·普拉西德 (Johny Placide)，帮助苏格兰登上了顶峰。\n尽管有这样的记录，苏格兰队在周五的比赛中仍保持着良好的状态，在过去 11 场正式比赛中赢了 8 场（平 1 平 2），其中包括过去 6 场比赛中的 5 场（平 1）。\n在此轮比赛中唯一击败他们的球队是希腊，他们曾两次击败他们——第一次是在 2025 年 3 月的欧洲国家联赛交锋中（3-0），第二次是在 2025 年 11 月的世界杯预选赛中（3-2）。\n然而，阻碍他们前进的是一支众星云集的摩洛哥球队，他们很可能会因为在对阵巴西的首场比赛中只获得一分而感到失望。\n摩洛哥可以说是当晚表现更好的一方，甚至首开纪录，这得益于伊斯梅尔·萨巴里的精彩动作，据报道，他即将转会拜仁慕尼黑。\n维尼修斯·儒尼奥尔 (Vinícius Júnior) 的神奇一击将比分扳平，但阿特拉斯雄狮队从那里控制了比赛的大部分时间。\n事实上，穆罕默德·瓦赫比的球队在对阵巴西队的比赛中也许发现了比他们预想的更多的控制力，在最后三分之一的比赛中完成了 123 次传球——这是 C 组首轮比赛中最多的球队，也是他们在世界杯比赛中有记录的最高传球总数。\n这个结果肯定会向C组的其他球队以及整个赛事发出一份声明。\n事实上，凭​​借塞巴里、布拉希姆·迪亚斯、阿什拉夫·哈基米、努塞尔·马兹拉维和阿尤布·布阿迪等人才，摩洛哥已经摆脱了“失败者”的标签，成为国际舞台上真正的竞争者。\n此次平局也将他们在世界杯小组赛中的不败纪录延长至五场（W2 D3），追平了非洲国家最长的不败纪录，此前由喀麦隆（1982年至1990年）和塞内加尔（2002年至2018年）保持。\n所有这些都表明，苏格兰如果想要获得第二场胜利并接近淘汰赛阶段，将面临重大挑战。\n如果他们要这样做，他们将需要麦金再次发挥出最佳状态。\n到目前为止，这位苏格兰队长在克拉克的执教下已经打进了 21 粒进球，这是在单一教练执教下为苏格兰队打进的最多进球的球员，与丹尼斯·劳在伊恩·麦科尔麾下的 21 场比赛中打进的 21 粒进球并列。\n与此同时，摩洛哥队在对阵巴西队的比赛中也受到了队长哈基米的启发。\n这位边后卫在比赛中射门次数并列最多（3次），创造机会次数并列最多（3次），同时在铲断（6次）、赢得犯规（5次）和争抢获胜（11次）方面也领先摩洛哥。\n这使他成为有记录以来（自 1966 年以来）第一位在铲球、赢得犯规和赢得对抗方面领先全队的后卫，同时在世界杯比赛中的射门和创造机会并列第一。\nOpta 超级计算机给出摩洛哥晋级淘汰赛阶段的概率为 91.6%，而苏格兰晋级淘汰赛的概率为 80.6%，这使得周五的结果可能在资格争夺战中发挥决定性作用。"
            ],
            [
                "历史交锋",
                "两支球队历史上几乎没有什么交锋，他们之前唯一一次交手是在1998年圣艾蒂安世界杯小组赛中，摩洛哥队在圣艾蒂安以3-0获胜，这仍然是他们在世界杯上最大的一场胜利。\n不过，瓦赫比的球队在世界杯上经常遇到欧洲球队，过去 12 场比赛中有 9 场是对阵欧洲球队，比 2018 年以来的任何其他球队都要多。\n令人印象深刻的是，他们在过去六场世界杯对阵欧洲对手的比赛中只输了一场（2胜3平）——2018年0-1负于葡萄牙。"
            ],
            [
                "赛前预测（Opta 超算）",
                "根据 Opta 超级计算机的数据，摩洛哥在波士顿开赛前占据上风，在 25,000 次赛前模拟中，阿特拉斯雄狮队的获胜率为 54.9%。\n苏格兰获胜的可能性仅为 20.1%，而平局占模拟的剩余 25.1%。"
            ]
        ]
    },
    {
        "slug": "usa-vs-australia-prediction-world-cup-2026-match-preview",
        "url": "https://theanalyst.com/articles/usa-vs-australia-prediction-world-cup-2026-match-preview",
        "home_en": "USA",
        "away_en": "Australia",
        "home_cn": "美国",
        "away_cn": "澳大利亚",
        "home_pct": 58.5,
        "draw_pct": 20.9,
        "away_pct": 20.6,
        "insights": [
            "The Opta supercomputer has given the United States a sizeable chance of victory ahead of this game, with Mauricio Pochettino’s side winning 58.5% of pre-match simulations.",
            "USA have won each of their last seven matches in Seattle .",
            "Australia have won three of their last four games at the World Cup, having managed just two victories across their first 17 tournament matches."
        ],
        "prediction": "From 25,000 pre-match simulations, Pochettino’s team came out on top in 58.5% of the outcomes, suggesting there is a growing weight of expectation behind this USA side. Australia’s chances of victory stand at just 20.6% by comparison, and with a draw given a 20.9% probability, the Socceroos will be keen to upset those pre-match presumptions.",
        "summary_cn": "根据 Opta 超级计算机的数据，尽管两支球队在第一比赛日都取得了当之无愧的胜利，但共同主办的美国队被认为是压倒性最有希望在这里取得另一场胜利的球队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机在这场比赛前给了美国队很大的获胜机会，毛里西奥·波切蒂诺的球队在赛前模拟中获胜率为 58.5%。\n· 美国队过去七场在西雅图的比赛全部获胜。\n· 澳大利亚在过去的四场世界杯比赛中赢了三场，而在前 17 场比赛中只取得了两场胜利。"
            ],
            [
                "深度分析",
                "2026 年世界杯小组赛第二轮比赛中，两股巨大的势头汇聚在一起，东道主美国队在西雅图体育场迎战澳大利亚队，两国队都取得了胜利的开局。\n毛里西奥·波切蒂诺的球队是第一比赛日表现出色的球队之一，在达米安·博巴迪利亚早早打入乌龙球后，福拉林·巴洛贡和乔瓦尼·雷纳的进球在洛杉矶以 4-1 的比分横扫巴拉圭队。\n巴洛贡在世界杯首秀中梅开二度，成为继 1930 年伯特·帕特诺德 (Bert Pateaude) 在对阵巴拉圭的比赛中上演帽子戏法之后，第二位在单场比赛中攻入多个进球的美国男球员。\n队长蒂姆·雷姆 (Tim Ream) 以 38 岁零 250 天成为代表美国队参加男子世界杯的年龄最大的球员，这位中后卫完成了 23 次断线传球，这是自 2010 年加纳队的约翰·佩因西尔 (John Paintsil)（对阵美国队）以来在本届世界杯上后卫完成的最多的球员。\n在加利福尼亚州以 4-1 的压倒性胜利，成为美国队在历届男子世界杯上并列最大的胜利，也是他们第一次在足球最大舞台上的一场比赛中取得四粒进球。\n然而，自 1930 年首届世界杯的前两场比赛（其中包括以三球战胜巴拉圭）以来，这支 2026 年世界杯联合主办国还没有连续赢过世界杯比赛。\n波切蒂诺的计划可能已经在对阵巴拉圭的比赛中得到落实，但美国队面对的是澳大利亚队，澳大利亚队在 D 组揭幕战中以 2-0 击败了土耳其队。\n内斯托里·伊兰昆达 (Nestory Irankunda) 的突破性进球让他成为澳大利亚有史以来最年轻的世界杯进球者，当时他年仅 20 岁零 125 天。上一位在前两届世界杯比赛中进球的 21 岁以下球员是 2014 年荷兰队的孟菲斯·德佩。\n伊兰昆达的首开纪录以及下半场康纳·梅特卡夫的远射体现了澳大利亚队的比赛计划，尽管澳大利亚队的控球率只有 28.3%，这是他们在世界杯比赛中的最低控球率，但他们的反击却毫不留情。\n托尼·波波维奇的球队在 ​​2-0 获胜的比赛中遭遇了 30 次射门，只有 1974 年的西德队（3-0 获胜时有 31 次射门）在世界杯单场对阵澳大利亚的比赛中射门次数最多。\n哈里·苏塔尔在对阵土耳其的比赛中解围 14 次，在 2026 年世界杯所有球员中排名第三，仅次于彼得·威尔逊（1974 年对阵东德队 15 次）在代表澳大利亚参加的世界杯比赛中解围更多。\n此外，帕特里克·比奇的 8 次扑救是本届世界杯上澳大利亚队单场扑救最多的门将，也是自 2002 年土耳其队的鲁斯图·雷茨贝尔（9 次对阵巴西）以来，在世界杯首秀中扑救最多的门将。\n他们有机会通过一场胜利在 D 组榜首的位置上领先 3 分，但美国队可能会失去护身符边锋克里斯蒂安·普利西奇，因为他在半场对阵巴拉圭时被淘汰。\n为巴洛贡首开纪录后，普利西奇在世界杯出场次数中贡献了 1 粒进球和 3 次助攻，自 1966 年以来只有兰登·多诺万为美国队贡献了更多（5 次）。\n澳大利亚队在这场比赛中保持着良好的健康状况，并且在过去的五场世界杯比赛中都取得了进球——这是他们在世界杯上连续最长的进球纪录——澳大利亚队将支持自己再次取得重大胜利。"
            ],
            [
                "历史交锋",
                "美国队和澳大利亚队首次在世界杯上交锋，此前四次交锋均为友谊赛，分别于1992年、1998年、2010年和2025年进行。\n他们最近的交锋是美国队获胜：2010 年 6 月以 3-1 获胜，2025 年 10 月以 2-1 获胜，2026 年世界杯队员哈吉·赖特 (Haji Wright) 和克里斯蒂安·罗尔丹 (Cristian Roldan) 分别贡献了两个进球和助攻。左后卫乔丹·博斯为澳大利亚队攻入第一球。\n澳大利亚此前唯一一场对阵世界杯东道主的比赛是在 1974 年，当时他们在汉堡以 3-0 输给了最终的冠军西德队。"
            ],
            [
                "赛前预测（Opta 超算）",
                "根据 Opta 超级计算机的数据，尽管两支球队在第一比赛日都取得了当之无愧的胜利，但共同主办的美国队被认为是压倒性最有希望在这里取得另一场胜利的球队。\n在 25,000 次赛前模拟中，波切蒂诺的球队在 ​​58.5% 的结果中名列前茅，这表明人们对这支美国队的期望越来越高。\n相比之下，澳大利亚获胜的可能性仅为 20.6%，而平局的可能性为 20.9%，澳大利亚队将渴望打破这些赛前假设。"
            ]
        ]
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
        "prediction": "But the Opta supercomputer leant towards a Mexico victory in this encounter as Aguirre’s side came out on top in 48.8% of 25,000 pre-match simulations. South Korea were afforded a 24.8% chance of winning in the same data-led simulations, while the draw accounted for 26.4% of scenarios.",
        "summary_cn": "两支球队都有望在首场比赛获胜后从 A 组出线。 Opta 的锦标赛预测结果显示，墨西哥晋级的概率为 98.5%，而韩国进入 32 强的概率为 94.3%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计墨西哥将连续两场获胜，他们在赛前模拟中以 48.8% 的令人信服的胜率击败了韩国。\n· 韩国历史上首次在世界杯上赢得了前两场比赛。\n· 劳尔·希门尼斯在最近两场对阵韩国的比赛中都有进球。"
            ],
            [
                "深度分析",
                "墨西哥和韩国周五在瓜达拉哈拉体育场交锋时，都希望在世界杯 A 组中夺取控制权。\n凭借胡利安·奎尼奥内斯和劳尔·希门尼斯的进球，共同主办国墨西哥队在本届世界杯揭幕战中以 2-0 轻取九人南非队。亚亚·西托勒和特姆巴·兹瓦内因巴法纳·巴法纳双双被罚下场。\n凭借人数优势，墨西哥队在对阵南非队（467/520）的比赛中找到了传球成功率为 89.8% 的队友。这创下了他们在世界杯比赛中的最高传球成功率记录（自 1966 年以来）。\n不过，哈维尔·阿吉雷的球队的胜利确实付出了代价。队长兼关键中后卫塞萨尔·蒙特斯在下半场补时阶段因拒绝胡利索·穆达的进球机会而受到严厉的处罚，被罚下场。\n在球场的另一端，希门尼斯有望再次发挥作用。这位 35 岁的球员在过去两场对阵韩国的比赛中都取得了进球，尽管这两个进球都来自友谊赛（2020 年 11 月和 2025 年 9 月）。\n希门尼斯和奎尼奥内斯也可能成为第一位在前两届世界杯首发中均取得进球的墨西哥球员。\n更多的历史也等待着《El Tri》。墨西哥队在过去两届世界杯比赛中都取得了胜利（2022年MD3，2026年MD1），但他们从未在世界杯上取得过三连胜。\n然而，阿吉雷的球队此前在瓜达拉哈拉体育场举行的三场比赛中只赢了一场，那就是在 2024 年 10 月的一场友谊赛中以 2-0 战胜美国队。另外两场比赛均是在2010年9月对阵厄瓜多尔，最终以2-1负于厄瓜多尔，并在2025年10月以1-1战平。\n在周五以 2-1 逆转击败捷克队后，韩国队也将充满信心地进入比赛。黄仁范 (Hwang In-Beom) 取消了拉迪斯拉夫·克雷吉 (Ladislav Krejcí) 的首开纪录，随后吴贤奎 (Oh Hyeon-Gyu) 在返回瓜达拉哈拉的同一个体育场内攻入制胜球。\n在吴氏的决定性射门后，黄哲伦成为韩国第三位在世界杯比赛中进球和助攻的球员。他加入了崔顺浩（1986年对阵意大利）和现任韩国主帅洪明甫（1994年对阵西班牙）的行列。\n李康仁在对阵捷克队的比赛中也给人留下了深刻的印象。这位巴黎圣日耳曼前锋成为自1982年德国队对阵奥地利队的皮埃尔·利特巴尔斯基以来第一位在世界杯比赛中完成5次以上带球（5次）、传球成功率100%（38/38）和助攻进球的球员。\n洪的球队现在希望首次赢得世界杯前两场比赛的胜利。然而，自2002年击败葡萄牙和意大利获得第四名以来，他们在这项赛事中就再也没有取得过背靠背的胜利。\n阿吉雷知道他的球队必须留意孙兴慜，他在过去三场对阵墨西哥的比赛中攻入两球，其中包括 2018 年本届世界杯的一球。\n然而，在韩国队的揭幕战中，孙兴慜有六次射门，但没有得分，随后被周五的英雄吴宇森换下。这位前托特纳姆热刺前锋在他的 56 场国际比赛进球数上未能再增加，但距离追平国家队历史进球纪录还差两球。\n埃德森·阿尔瓦雷斯可能会负责应对孙兴慜和韩国队的进攻，蒙特斯在墨西哥首场比赛中因红牌停赛一场。"
            ],
            [
                "历史交锋",
                "如果重演之前的交锋，墨西哥队将完全控制A组。\n墨西哥队此前在世界杯上两场对阵韩国队的比赛中都取得了胜利，98年法国队3-1战胜韩国队，八年前俄罗斯队2-1战胜韩国队。\n韩国也从未在世界杯上遇到过东道主，尽管他们在过去与中北美及加勒比地区对手的三场比赛中都未能获胜（D1 L2）。\n墨西哥队在对阵亚洲对手的五场锦标赛比赛中全部获胜，并且在最近四场此类胜利中每场都进球两次或以上。"
            ],
            [
                "赛前预测（Opta 超算）",
                "两支球队都有望在首场比赛获胜后从 A 组出线。 Opta 的锦标赛预测结果显示，墨西哥晋级的概率为 98.5%，而韩国进入 32 强的概率为 94.3%。\n但 Opta 超级计算机倾向于墨西哥在这场比赛中获胜，因为阿吉雷的球队在 ​​25,000 次赛前模拟中以 48.8% 的胜率获胜。\n在相同的数据主导模拟中，韩国队获胜的几率为 24.8%，而平局占 26.4%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer is supremely confident that it will be Canada who pick up their first World Cup win in this match, with Marsch’s side earning all three points in 72.9% of its 25,000 simulations. The next most likely result is a draw, at 16.5%. Meanwhile, Qatar have just a 10.6% chance of upsetting the odds with an unlikely victory.",
        "summary_cn": "Opta 超级计算机非常有信心加拿大队将在这场比赛中首次夺得世界杯冠军，Marsch 的球队在 ​​25,000 次模拟中的 72.9% 中获得了全部三分。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 加拿大队显然是赢得这场比赛的热门球队，在 Opta 超级计算机的 25,000 次模拟中，加拿大队以 72.9% 的成绩名列前茅。\n· 加拿大队在温哥华举行的最近四场比赛中均取得胜利，打进 17 球，仅失 2 球。最后一支在不列颠哥伦比亚省击败他们的球队是 2016 年 3 月世界杯预选赛中的墨西哥队 (3-0)。\n· 卡塔尔队在 2026 年 FIFA 世界杯 B 组中的射门次数（6 次）、平均控球率（32%）、向前传球（118 次）、对方禁区触球（8 次）以及 MD1 中最后三区成功传球（24 次）方面排名垫底。"
            ],
            [
                "深度分析",
                "周四，加拿大队和卡塔尔队将在温哥华 BC 球场交锋，首次尝试赢得 FIFA 世界杯比赛。\n事实上，在 MD1 比赛中分别战平波黑队和瑞士队之前，两支球队在本届赛事中都拥有 100% 的输球记录。毫无疑问，他们的球迷会以不同的方式接受他们的抽签。\n加拿大队是对阵波斯尼亚队的侵略者，尽管丢掉了首个进球，但他们会觉得自己已经做了足够的努力来赢得比赛；他们拥有 61% 的控球率，在对方禁区内触球 37 次，而波黑则有 15 次触球，并且在空战中只丢了 0.02 个预期进球。\n对于卡塔尔来说，这是一个不同的故事，他们与经验丰富得多的瑞士队的平局就像一场胜利一样庆祝。他们拥有 32% 的控球率，在对方禁区内触球 8 次，而瑞士队则有 42 次触球，预计失球 3.2 个。然而，由于米罗·穆海姆在补时第4分钟的乌龙球，他们最终以平局逃脱。\n当然，加拿大要想在这里获胜，将会面临更大的压力。本届赛事的另外两个主办国墨西哥和美国在 MD1 赛上相对轻松地在主场获胜，而加拿大也迫切希望加入这一行列。他们在七次世界杯尝试中仍然没有取得胜利——只有洪都拉斯（9次）和埃及（8次）在没有尝过胜利的情况下踢了更多场比赛。\n温哥华市最近对他们很友善。加拿大队在过去的四场比赛中取得了胜利，打进 17 球，仅丢 2 球。最后一支击败他们的球队是 2016 年 3 月世界杯预选赛中的墨西哥队。\n加拿大队主教练杰西·马什可能认为他的球队在对阵波斯尼亚的比赛中的表现足以不需要在这场比赛中进行任何阵容调整，但两名推动首发的球员是普罗米斯·大卫和赛尔·拉林。\n大卫协助拉林打进了加拿大队在抽签中的唯一进球，这是世界杯比赛中第一次有两名替补球员为加拿大队进球。拉林进球时只在场上呆了 121 秒，并在第一次触球后就进球了。\n中场球员伊斯梅尔·科内（Ismaël Koné）是一位肯定能首发的球员。在对阵波斯尼亚队的比赛中，没有哪位加拿大球员比科内完成了更多的传球（50次），而他在最后三分之一的突破传球（9次）和高强度压力传球（49次）方面也领先于所有队友。\n卡塔尔没有输给瑞士多少有些幸运，而数据表明他们可能需要一定程度的运气才能不输掉这场比赛。他们在射门（6次）、控球（32%）、向前传球（118次）、在对方禁区触球（8次）和成功的最后三区传球（24次）方面在MD1中排名B组垫底。\n与此同时，他们面对的 26 次射门仅比 2022 年世界杯主场三场小组赛的总和（32 次）少了 6 次。\n两届亚洲足球先生阿克拉姆·阿菲夫经常被认为是卡塔尔有史以来最伟大的球员，而这位阿尔萨德边锋无疑将是他们在本届世界杯上取得成功的关键。\n阿菲夫是唯一一位在对阵瑞士的 MD1 比赛中创造多次机会的卡塔尔球员（2 次），而在 2022 年和 2026 年两次参加世界杯期间，阿菲夫创造的机会比任何其他队友多 5 次（7 次）。"
            ],
            [
                "历史交锋",
                "这将是加拿大和卡塔尔在世界杯上的首次交锋。他们之前唯一一次交锋是 2022 年 9 月在维也纳举行的一场友谊赛，加拿大凭借拉林和乔纳森·大卫的进球以 2-0 获胜。\n加拿大此前在世界杯上只遇到过一次非欧洲对手，2022 年世界杯小组赛中以 2-1 输给摩洛哥。\n这将是世界杯东道国第四次面对亚洲球队，前三届东道主均获胜——墨西哥1-0伊拉克（1986年）、法国4-0沙特阿拉伯（1998年）和俄罗斯5-0沙特阿拉伯（2018年）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机非常有信心加拿大队将在这场比赛中首次夺得世界杯冠军，Marsch 的球队在 ​​25,000 次模拟中的 72.9% 中获得了全部三分。\n下一个最可能的结果是平局，为 16.5%。与此同时，卡塔尔队只有 10.6% 的机会以不太可能的胜利打破赔率。"
            ]
        ]
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
        "prediction": "Of 25,000 pre-match simulations produced by the Opta supercomputer, Switzerland came out as strong favourites for victory: they have a 61.8% chance of success. Bosnia-Herzegovina only prevailed in 17.2% of those simulations, with a draw rated at 21.1%.",
        "summary_cn": "在 Opta 超级计算机生成的 25,000 次赛前模拟中，瑞士成为获胜的热门：他们的成功机会为 61.8%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，尽管开局不确定，瑞士队仍有 61.8% 的机会赢得小组赛第二场比赛。\n· 因此，波黑获胜的几率只有17.2%，预计不会创下10场不败的全国新纪录。\n· 瑞士在过去 17 场世界杯或欧洲杯小组赛中只输掉了两场（7 胜 8 平）。"
            ],
            [
                "深度分析",
                "瑞士和波斯尼亚和黑塞哥维那在 2026 年世界杯首场比赛中都在领先优势上失利，这使得他们周四在洛杉矶的交锋成为一场不容输掉的比赛。\n瑞士队无疑会感到最不幸，因为卡塔尔队的扳平比分（93:59）是自1966年有此纪录以来，世界杯小组赛第三晚扳平比分的进球。\n被迫以1-1战平，26次射门也是瑞士队在世界杯比赛中射门次数最多的。在出场的 16 名球员中，有 14 人尝试射门或创造机会。唯一没有做到这一点的两人是门将格雷戈尔·科贝尔和替补球员米罗·穆海姆——后者确实打进了一个代价高昂的乌龙球——但让卡塔尔队获得他们在世界杯上的首个积分却在国内引起了严厉的头条新闻。\n穆拉特·亚金（Murat Yakin）的球队在国际足联排名第 19 位，连续第六次出场，原本有望进入淘汰赛阶段，但这似乎已不再确定。\n作为一个实用主义者，亚金不太可能惊慌。 B组四支球队中，瑞士队完成传球次数最多（527次），传球准确率最高（91.5%）。相比之下，波斯尼亚和黑塞哥维那完成的传球最少（172 次），传球准确率最差（63.5%），这表明当两人在加州会面时，可能会出现风格冲突。\n波斯尼亚主帅谢尔盖·巴尔巴雷斯（Sergej Barbarez）毫不羞耻地采取更加垂直的方式，他因带领国家重返大舞台而被誉为英雄，自2014年首次亮相以来一直缺席。\n在约沃·卢基奇（Jovo Lukic）——代替因伤缺阵的历史最佳射手埃丁·哲科（Edin Dzeko）——在第四次出场中攻入他的第一个国际进球之后，他们几乎以战胜加拿大队开始。\n尽管共同东道主随后反击并取得平局，但波黑在过去 12 场比赛中只输掉了一场（5 胜 6 平），而在过去 15 场比赛中输掉了 12 场。\n奇怪的是，他们在所有比赛中的最后六场比赛都取得了平局——其中两场在附加赛中进入了点球大战——并且没有一个欧洲国家连续七场比赛打成平局。\n再次避免失败也将创造新的全国不败纪录；自获得独立以来，他们曾两次达到九（2013年6月和2018年11月）。\n因此，尽管排名落后 45 位，但波斯尼亚和黑塞哥维那在首次与另一个欧足联国家队进行世界杯比赛之前完全可以充满信心。\n历史表明，这可能是一场有趣的比赛：瑞士在过去五场世界杯对阵欧洲对手的比赛中打进了 23 个进球，平均每场 4.6 个进球。\n明星前锋布雷尔·恩博洛正在享受他最多产的时期。包括对阵卡塔尔时冷静射入的点球在内，他在过去 13 场比赛中打入的 25 个国家队进球中有 10 个来自。\n即使没有前主力沙奇里，瑞士队最后阵容的平均年龄（30岁86岁）也是所有世界杯比赛中年龄最大的；里卡多·罗德里格斯（Ricardo Rodríguez）和队长格拉尼特·扎卡（Granit Xhaka）这两位代表国家队出场超过 100 场的老将现在是参加七场重大赛事的三名瑞士人中的两人，另外两名是沙奇里。\n与此同时，波斯尼亚和黑塞哥维那的改组阵容将年轻与经验融为一体。四十岁的船长哲科提供了很多后者。克里姆·阿拉伊贝戈维奇 (Kerim Alajbegovic) 年仅 18 岁零 264 天，成为代表球队参加世界杯的最年轻球员，这位边锋现在将寻求升级为首发阵容。"
            ],
            [
                "历史交锋",
                "瑞士和波斯尼亚和黑塞哥维那迄今为止首次在世界杯上相遇。\n他们之前唯一的交锋是10年前在苏黎世的一场友谊赛，当时客队凭借哲科和米拉勒姆·普贾尼奇的进球以2-0获胜。"
            ],
            [
                "赛前预测（Opta 超算）",
                "在 Opta 超级计算机生成的 25,000 次赛前模拟中，瑞士成为获胜的热门：他们的成功机会为 61.8%。\n波斯尼亚和黑塞哥维那仅在 17.2% 的模拟比赛中获胜，平局率为 21.1%。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "在 Opta 超级计算机的 10,000 次赛前模拟中，捷克队的表现远远好于南非队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机使捷克队以 52.9% 的获胜概率成为夺冠热门，而南非的获胜概率为 23.3%。\n· 捷克队的米罗斯拉夫·库贝克（74岁零290天）和南非队的雨果·布罗斯（74岁69天），这将是世界杯历史上第一场两位主教练年龄都超过70岁的比赛。\n· 对阵墨西哥队的比赛中，特博霍·莫科纳的传球成功率为 92.9%（39/42），这是南非球员在世界杯比赛中传球超过 40 次的最高比例。"
            ],
            [
                "深度分析",
                "周四，捷克队和南非队将在亚特兰大体育场进行一场关键的世界杯 A 组比赛，届时他们都需要证明自己的实力。\n尽管捷克队在与韩国队的首场比赛中凭借拉迪斯拉夫·克雷西 (Ladislav Krejcí) 取得领先，但由于黄仁范 (Hwang In-beom) 和吴贤奎 (Oh Hyeon-gyu) 的进球，最终以 2-1 告负。\n世界杯感觉才刚刚开始，但捷克队已经知道，输给南非队以及避免输给韩国队的墨西哥队将提前结束他们的世界杯之旅。他们需要确保在这里得到结果。\n“我们面临着与韩国队完全不同的情况。我们肯定希望更多地控球并变得更加自信，”前锋托马斯·乔里说道。\n“我认为我们有能力进入好的位置。我们可以在训练中看到我们很擅长，我们只需要把它转移到比赛中。”\n捷克队希望在韩国队在上一场比赛中控球之后获得更多的控球权，将他们的射门次数限制在 7 次，累计预期进球 (xG) 值为 0.83。\n尽管他们还没有拿到一分，但 Opta 超级计算机仍然给他们提供了 49.8% 的机会进入最后 32 强，这表明他们有能力在这里获得结果。\n此前，捷克队只在世界杯上两次输掉了前两场比赛，而这些情况可以追溯到1954年和1970年。\n如果克雷西在对阵南非的比赛中再次进球，他将与奥尔德里奇·内杰德利（1934年、1938年）、拉迪斯拉夫·佩特拉斯（1970年）和米哈尔·比莱克（1990年）一起成为捷克队在世界杯前两场比赛中唯一进球的球员。\n捷克队的机会因南非队缺席亚亚·西托勒和特姆巴·兹瓦内而增加，他们在本届世界杯首场比赛中以 2-0 输给共同东道主墨西哥队时双双被出示红牌。\n在那场比赛中，南非队的射门总数（3次）、预期进球数（0.07次）、向对方禁区的传球次数（12次）和最后三区的成功传球次数（25次）都是世界杯比赛中最低的，而他们在对方禁区内的两次触球也是历史上并列最少的。\n巴法纳·巴法纳（Bafana Bafana）因墨西哥队的高压逼抢而未能打入两球，导致教练雨果·布罗斯（Hugo Broos）和守门员罗文·威廉姆斯（Ronwen Williams）受到批评。\n门将里卡多·戈斯（Ricardo Goss）为布罗斯辩护，他相信布罗斯能够帮助球队避免历史上第一次连续输掉世界杯比赛。\n“不幸的是，我们作为南非队不够现实。我并不是说我们不应该去尝试赢得比赛，但我认为这对教练不公平……我们仍然爱他，我们将为他效力，”戈斯说。\n南非也知道他们在比赛中的未来岌岌可危，因为输给捷克和韩国避免输给墨西哥就足以让他们出局。\n布罗斯可能会指望雷莱博希莱·莫福肯作为停赛的兹瓦内的替代者，而塔兰特·姆巴塔可能会在西索尔缺席的情况下被召唤。\n根据 Opta 超级计算机的数据，南非晋级淘汰赛的机会只有 24.9%，而对阵捷克队的积极结果将是保持这种可能性的关键。"
            ],
            [
                "历史交锋",
                "捷克和南非之前只交手过一次，那是在 1997 年的联合会杯上。那场比赛最终以 2-2 的比分结束，弗拉基米尔·斯米切尔梅开二度。\n南非队曾六次在世界杯上与欧洲球队交锋。他们最近一场此类比赛是令人难忘的 2-1 战胜法国队，并最终将法国队淘汰出 2010 年世界杯。\n巴法纳 巴法纳在过去四场世界杯对阵欧洲对手的比赛中只输了一场——2002 年以 3-2 输给了西班牙。\n与此同时，捷克队在 2006 年世界杯上唯一输给了非洲对手，以 2-0 输给了加纳。"
            ],
            [
                "赛前预测（Opta 超算）",
                "在 Opta 超级计算机的 10,000 次赛前模拟中，捷克队的表现远远好于南非队。\n库贝克的球队赢得了 52.9% 的预测，而南非则赢得了 23.3%。\n平局将使两支球队继续争夺晋级资格，概率为 23.8%——这比南非获胜的可能性更大。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours a Colombia victory, winning 67.7% of the 25,000 pre-match simulations. Uzbekistan’s chances of marking their World Cup bow with a win are rated at 11.7%, with a draw at 20.6%.",
        "summary_cn": "Opta 超级计算机支持哥伦比亚获胜，在 25,000 次赛前模拟中获胜率为 67.7%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 哥伦比亚在过去六场世界杯小组赛中赢了五场（L1），并且以 67.7% 的胜率成为 Opta 的夺冠热门。\n· 乌兹别克斯坦队的目标是成为继2010年斯洛伐克之后第一支进入世界杯淘汰赛阶段的球队。\n· 法比奥·卡纳瓦罗（2006 年）和内斯托尔·洛伦佐（1990 年）是参加 2026 年世界杯决赛的三名主教练中的两位，此外还有法国队主教练迪迪埃·德尚（1998 年）。"
            ],
            [
                "深度分析",
                "世界杯新晋国家乌兹别克斯坦队希望在墨西哥城战胜归来的哥伦比亚队，迎来他们期待已久的世界杯首秀。\n在经历了几次险些失利之后，白狼队终于在决赛中亮相，他们在亚冠预选赛中成功晋级，在16场比赛中只输了一场。\n埃尔多尔·肖穆罗多夫扮演了主角，这位前罗马前锋——现在正在与超级联赛球队伊斯坦布尔巴沙克谢希尔进行交易——直接参与了全队最高的九个进球（五个进球，四个助攻）。\n斯雷科·卡塔内克和蒂穆尔·卡帕泽都带领乌兹别克斯坦队在第二轮和第三轮小组赛中获得了第二名，落后于伊朗队，随后前意大利队队长法比奥·卡纳瓦罗在2006年带领蓝衣军团夺得世界杯经验，并获得了世界杯经验。\n卡纳瓦罗作为球员参加的四届世界杯是德国队出场次数最多的一次，与意大利人并列出场次数最多的世界杯。\n然而，他的世界杯生涯却以令人失望的结局告终，卫冕冠军意大利队在2010年决赛中以3-2击败斯洛伐克队，小组赛出局。\n巧合的是，斯洛伐克随后晋级淘汰赛是最后一次首次参加世界杯的球队实现这一壮举，卡纳瓦罗现在的目标是与乌兹别克斯坦效仿，而亚足联联盟中最后一支做到这一点的球队是1994年的沙特阿拉伯。\n另一个巧合是，卡纳瓦罗的对手也拥有世界杯决赛的经验，哥伦比亚主帅内斯托·洛伦佐曾是阿根廷队的一员，在1990年的世界杯决赛中被西德队击败。迪迪埃·德尚是 2026 年世界杯上唯一一位参加过世界杯决赛的主教练；这位即将卸任的法国主帅曾带领法国队于 1998 年在本土取得胜利。\n20 年前，当卡纳瓦罗举起世界杯奖杯时，洛伦佐是何塞·佩克曼手下的阿根廷助理教练，随后他跟随哥伦比亚队在 2014 年进入四分之一决赛，四年后在 16 强中点球大战输给了英格兰队。\nLos Cafeteros 缺席 2022 年卡塔尔世界杯后，洛伦佐带领他们在令人印象深刻的 CONMBEOL 预选赛中重返决赛，最终落后于卫冕世界冠军阿根廷和厄瓜多尔，获得第三名。\n哥伦比亚队的进攻质量突显了他们在本节中的预期进球数（28.8）、射正次数（96）和头球进球（7）。与此同时，他们的 28 个进球仅次于阿根廷队（31 个）——两年前，凭借劳塔罗·马丁内斯的加时赛制胜球，阿根廷队击败了他们夺得美洲杯冠军。\n洛伦佐的预选赛由头号射手路易斯·迪亚斯领衔，他的七个进球仅落后于莱昂内尔·梅西（八个）。与此同时，他们在 2014 年世界杯上的明星球员詹姆斯·罗德里格斯 (James Rodríguez) 贡献了 7 次助攻，比其他任何球员都多出 3 次，并以 6 个进球赢得了金靴奖。\n对于哥伦比亚能否效仿巴西进入八强的希望，这两个人都可能至关重要。 Los Cafeteros 在最近两次决赛中取得了相当快的进步，赢得了六场小组赛中的五场（L1），他们的目标是在北美取得同样的快速开局。"
            ],
            [
                "历史交锋",
                "这将是两国之间的首次会晤。\n乌兹别克斯坦此前唯一一次战胜南联盟球队是在 2023 年 3 月。\n白狼队在沙特阿拉伯进行的一场友谊赛中以1-0击败玻利维亚，埃尔多·肖穆罗多夫在第36分钟攻入制胜球。\n与此同时，哥伦比亚在最近一场世界杯比赛中输给了亚冠对手，并在 2018 年俄罗斯首场比赛中以 2-1 输给了日本。\n尽管如此，洛斯卡夫特罗斯队还是从早期的失利中恢复过来，在战胜波兰和塞内加尔后，以 H 组第一名的成绩名列前茅。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持哥伦比亚获胜，在 25,000 次赛前模拟中获胜率为 67.7%。\n乌兹别克斯坦在世界杯上获胜的几率为 11.7%，平局的几率为 20.6%。\n历史表明，我们不太可能在阿兹特克会议上看到僵局。\n哥伦比亚参加的 22 场世界杯比赛中没有一场是互交白卷，只有奥地利（29 场比赛）在世界杯上没有取得过 0-0 的战绩。"
            ]
        ]
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
        "prediction": "After sifting through 25,000 pre-match simulations, the Opta supercomputer predicts victory for Ghana, winning 45.1% of those sims. This game surely represents their best chance of claiming points in Group L, but Panama only won 28.1% of the supercomputer simulations, leaving a draw rated at 26.8%.",
        "summary_cn": "在筛选了 25,000 次赛前模拟后，Opta 超级计算机预测加纳获胜，其中获胜率为 45.1%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机是加纳队的最爱，在赛前模拟中获胜率为 45.1%。\n· 在超级计算机 25,000 次赛前模拟中，巴拿马队以 28.1% 的成绩首次赢得世界杯。\n· 73岁的黑星队主教练卡洛斯·奎罗斯将成为第三位执教五届世界杯的主教练。"
            ],
            [
                "深度分析",
                "巴拿马和加纳与两名欧洲重量级球队分在一组，他们都知道周三的首场比赛本质上是一场必须获胜的比赛。\n很少有人会看好任何一方对阵克罗地亚或英格兰的机会，因此未能获得最高分可能会付出高昂的代价——只有两支球队可以保证晋级。\n尽管加纳队甚至未能进入上届非洲国家杯，但他们在 10 场比赛中赢了 8 场（平 1 平 1），以小组第一的身份领先于马达加斯加和马里，获得了参加本届世界杯的资格。\n这标志着黑星队在 21 世纪第五次亮相，并激发了他们追随 2010 年四分之一决赛历史最佳战绩的梦想。\n那一年，他们在点球大战中输给了受反英雄路易斯·苏亚雷斯启发的乌拉圭队，但他们在随后的两次参赛（2014年和2022年）中都在第一阶段被淘汰。\n事实上，加纳在过去七场世界杯比赛中只赢了一场（D2 L4），并且在过去六场比赛中每场都至少失球两次。\n这支西非球队目前在 FIFA 世界排名中排名第 73 位，最近在过去七场比赛中输掉了 6 场，只是在上一场与威尔士 1-1 战平后才止住颓势。\n肩负着阻止球队颓势的重任，卡洛斯·奎罗斯于四月份被聘请接替奥托·阿多，成为继卡洛斯·阿尔贝托·佩雷拉（六次）和博拉·米卢蒂诺维奇（五次）之后第三位执教五届世界杯的人。\n现在，他执教了第九个不同的国家队，他还延续了自 2010 年随葡萄牙队开始的连续纪录，之后带领伊朗队连续三届参加世界杯。\n相比之下，巴拿马队主教练托马斯·克里斯蒂安森正在为他的世界杯首秀做准备，就在他上任六周年之前。\n克里斯蒂安森已经带领洛斯卡纳莱罗斯打进了 2023 年金杯决赛，然后是美洲杯淘汰赛，最后进入了 2025 年中北美洲及加勒比海国家联赛决胜局。\n现在，巴拿马队将第二次参加国际足联的顶级赛事。他们在2018年小组垫底，三场比赛全部输掉，丢了11个球。\n得益于世界杯共同主办国加拿大、墨西哥和美国的缺席，他们在预选赛中两轮保持不败（7胜3平）。他们还记录了最高数量的高失误（82）和紧逼序列（138）。\n尽管是巴塞罗那青训体系的产物，前西班牙前锋克里斯蒂安森却是一位实用主义者，他的球队仍然以老将防守型中场阿尼巴尔·戈多伊为核心。\n巴拿马队队长为他们提供了心跳，而边锋伊斯梅尔·迪亚兹则在进攻三区带来了威胁；后者在去年的金杯赛上赢得了金靴奖，进球数是其他球员的两倍。\n与此同时，在中北美洲及加勒比海地区预选赛中，只有三名球员的助攻数超过了贝西克塔斯队后卫阿米尔·穆里略（Amir Murillo）（3次），后者的预期助攻数也排名第二（2.6次）。\n相反，旗手仍然是 34 岁的队长乔丹·阿尤 (Jordan Ayew)，他在非洲足联预选赛中参与了 14 个进球（7 个进球、7 次助攻），与阿尔及利亚的穆罕默德·阿穆拉 (Mohammed Amoura) 并列最多。"
            ],
            [
                "历史交锋",
                "之前没有交手过，但加纳在此前三场世界杯对阵中北美洲和加勒比地区球队的比赛中赢了两场——全部都是对阵美国队。\n与此同时，巴拿马在世界杯上与非洲球队的唯一一场交锋是在 2018 年俄罗斯世界杯上以 2-1 输给突尼斯。"
            ],
            [
                "赛前预测（Opta 超算）",
                "在筛选了 25,000 次赛前模拟后，Opta 超级计算机预测加纳获胜，其中获胜率为 45.1%。\n这场比赛无疑是他们在L组拿分的最佳机会，但巴拿马队在超级计算机模拟中只赢了28.1%，平局率为26.8%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer gives Croatia a 77.2% chance of progressing from Group L, second only to England’s 95.6%.",
        "summary_cn": "根据 Opta 超级计算机的数据，英格兰队在这场 L 组揭幕战之前被视为夺冠热门，在 10,000 次赛前模拟中，三狮军团以 55.9% 的胜率获胜。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计英格兰将强势开启 2026 年世界杯征程，获胜概率为 55.9%，克罗地亚为 20.8%。\n· 这将是继2018年半决赛之后，英格兰和克罗地亚在世界杯上的第二次交锋，当时克罗地亚经过加时赛以2-1获胜。\n· 英格兰队在过去八场世界杯揭幕战中仅输掉一场（4胜3平）——2014年以2-1负于意大利。"
            ],
            [
                "深度分析",
                "周三，英格兰在达拉斯体育场举行的 L 组揭幕战中对阵克罗地亚，他们希望在世界杯上取得一个轰轰烈烈的开局。\n三狮军团是世界杯前状态最好的球队之一，也是进入半决赛的热门球队之一，Opta 超级计算机给了他们 29.1% 的机会。\n周三的比赛将标志着英格兰队第 17 次参加世界杯，也是他们连续第八次参加世界杯——这是他们自 1994 年缺席世界杯以来最长的连续参赛纪录（也是在美国）。\n托马斯·图赫尔的球队是欧洲足联仅有的两个赢得全部八场预选赛比赛的国家之一，另外两个国家是挪威。他们也是唯一一支在预选赛中不失球的球队。\n虽然令人印象深刻，但图赫尔现在面临着将这种状态转化为最大舞台的巨大挑战，而英格兰队经常发现这很困难。\n自1966年举起奖杯以来，三狮军团在赛事中的战绩就没有什么值得大书特书的。他们仅两次晋级四分之一决赛，并在 1990 年和 2018 年均获得第四名。\n然而，令英格兰队振奋的是他们在世界杯揭幕战中的强劲战绩。他们在过去八场揭幕战中仅输掉一场（3胜4平）——2014年1-2负于意大利。\n与此同时，克罗地亚队早已摆脱了“失败者”的标签，第七次参加世界杯，成为国际足坛表现最稳定的球队之一。\n瓦特雷尼队的记录可能表明他们往往忽冷忽热，但在不畏年龄的卢卡·莫德里奇的领导下，他们仍然是真正的威胁。\n在过去的六届世界杯中，他们曾三度在小组赛中被淘汰，但在另外三届世界杯上也都登上了领奖台。\n事实上，克罗地亚是过去两届世界杯上与法国并列的仅有的两个进入半决赛的国家之一。\n虽然他们这次进入四强的机会很小（8.9%），但他们仍然以良好的状态抵达美国。\n兹拉科·达利奇的球队在八场预选赛中赢了七场，并且整个赛季保持不败，只在布拉格0-0战平捷克队的比赛中失分。\n他们在过去两届世界杯小组赛中也保持不败（4胜2平），期间只丢了2个球。\n不过，揭幕战对克罗地亚来说并不总是那么有利。他们在过去五场世界杯揭幕战中只赢了一场（平一平三）——2018 年 2-0 战胜尼日利亚。\nOpta超级计算机让克罗地亚队从L组晋级的几率为77.2%，仅次于英格兰队的95.6%。\n虽然英格兰队在球场上的表现显然很强，但今年夏天英格兰队的成功程度可能取决于哈里·凯恩的表现。在过去两届世界杯上，只有基利安·姆巴佩（12 粒）的进球数超过凯恩的 8 粒进球。\n这位英格兰队长预计将在对阵克罗地亚的比赛中首发出场，这将是他在重大国际赛事中的第 30 场比赛，比任何其他英格兰球员都要多。\n与此同时，克罗地亚将再次向伊万·佩里西奇寻求灵感。\n这位经验丰富的边锋直接参与的进球比大型赛事历史上任何克罗地亚球员都多（10 粒进球，8 次助攻）。他也是过去三届世界杯上仅有的三名既进球又助攻的球员之一，另外两位是莱昂内尔·梅西和内马尔。"
            ],
            [
                "历史交锋",
                "上一次世界杯英格兰队和克罗地亚队的交锋是2018年的半决赛，达利奇的球队后来居上，通过加时赛以2-1获胜。\n基兰·特里皮尔帮助英格兰队早早取得领先，但佩里西奇和马里奥·曼朱基奇的进球最终帮助克罗地亚队首次进入世界杯决赛。\n周三的比赛将是英格兰队和克罗地亚队在21世纪重大赛事中的第四次交锋。迄今为止，他们在世界杯上交锋过一次（克罗地亚于 2018 年获胜），在欧洲杯上交锋过两次（英格兰均获胜）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "根据 Opta 超级计算机的数据，英格兰队在这场 L 组揭幕战之前被视为夺冠热门，在 10,000 次赛前模拟中，三狮军团以 55.9% 的胜率获胜。\n克罗地亚获胜的几率仅为 20.8%，而平局占模拟比赛的剩余 23.3%。"
            ]
        ]
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
        "prediction": "Across 25,000 pre-match simulations, Portugal dispatched DR Congo in a sizeable 54.5% of the outcomes, with a 22.3% likelihood that this Group K opener will finish level. The Leopards’ chances of victory stand at a reasonable 23.2%, but Sébastien Desabre’s side certainly couldn’t have asked for a much tougher test on their World Cup return.",
        "summary_cn": "刚果民主共和国获得本届世界杯资格后，FIFA 排名从第 56 位跃升至第 45 位，但 Opta 超级计算机仍然认为排名第五的葡萄牙更有可能赢得这场比赛。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机将葡萄牙视为 2026 年世界杯的大热门。他们在 54.5% 的赛前模拟中击败了刚果民主共和国。\n· 葡萄牙在过去四场世界杯揭幕战中只赢了一场，在 2022 年以 3-2 击败加纳。他们在世界杯的最后三场揭幕战中平均每场打进 5 个进球。\n· 这只是刚果民主共和国第二次参加世界杯，也是自 1974 年代表扎伊尔参加世界杯以来的第一次。只有威尔士（64 年）、埃及和挪威（均为 56 年）比豹队 52 年的比赛间隔更长。"
            ],
            [
                "深度分析",
                "克里斯蒂亚诺·罗纳尔多 (Cristiano Ronaldo) 和葡萄牙队终于踏上了 2026 年世界杯的赛场，在德克萨斯州休斯顿体育场举行的世界杯揭幕战对阵刚果民主共和国球队，刚果民主共和国队重返足球最大舞台的旅程已经进行了 52 年。\n葡萄牙是自 2002 年以来仅有的五个参加过每届世界杯的欧洲国家之一，与英格兰、法国、德国和西班牙一起，葡萄牙在过去五届世界杯中有四次进入了淘汰赛阶段。\n罗伯托·马丁内斯的球队在六场比赛中攻入 20 个进球，在爱尔兰共和国、匈牙利和亚美尼亚队的小组中名列前茅，布鲁诺·费尔南德斯和若昂·内维斯双双上演帽子戏法，最终以 9-1 战胜了后者。\nC罗以葡萄牙队最佳射手的身份结束了预选赛，他的五个进球在欧足联F组中并列最多；目前，这位41岁的球员是唯一一位在五届世界杯上进球的球员。\n这位阿尔纳斯尔前锋将成为继罗杰·米拉（42岁）之后参加世界杯的第二年长的外场球员，并且正在与莱昂内尔·梅西争夺成为有史以来第一位参加六届世界杯的球员。\n阿根廷队在前一天迎来揭幕战，罗纳尔多看起来很可能会输掉这场特别的战斗，但他将带领葡萄牙队在过去 11 场世界杯比赛中取得 10 场进球。\n唯一的例外是2022年四分之一决赛0-1输给摩洛哥，但葡萄牙队在马丁内斯身上有一位在这个级别上有着非凡战绩的教练。\n马丁内斯带领比利时和葡萄牙队，在他的 10 场世界杯比赛中赢得了 7 场——在世界杯上出场 10 场以上的主教练中，只有特莱·桑塔纳 (80%)、迪迪埃·德尚 (74%) 和约阿希姆·勒夫 (71%) 的胜率高于马丁内斯的 70%。\n然而，就进展而言，历史并不站在葡萄牙一边。他们在世界杯上的最好成绩是 60 年前的 1966 年英格兰世界杯上的第三名，此后他们只在 2006 年打进过一次半决赛。\n2026年至今，葡萄牙保持不败，在最近三场热身赛中击败了美国、智利和尼日利亚，在以2-1战胜后者的比赛中各入一球后，边锋佩德罗·内托和弗朗西斯科·康塞桑将有信心在马丁内斯的锋线上夹击罗纳尔多。\n虽然 21 世纪的老牌葡萄牙队希望取得他们有史以来最好的世界杯成绩，但他们的对手自 1974 年以来首次参加世界杯，并在 1997 年球队从扎伊尔更名后首次以刚果民主共和国的身份参加比赛。\n豹队在洲际附加赛中以 1-0 战胜牙买加，成为最后一批获得本届世界杯参赛资格的国家之一，阿克塞尔·图安泽贝在第 100 分钟的制胜球终结了球队 52 年缺席世界杯的局面。\n刚果民主共和国在非洲足球联盟预选赛第二轮中落后于加蓬，但先后击败喀麦隆和尼日利亚，进入在瓜达拉哈拉对阵牙买加的决定性附加赛决赛。\n在整个非洲足联预选赛中，刚果民主共和国有两名球员贡献了6个以上的进球，他们是塞德里克·巴坎布（Cédric Bakambu）（4个进球，2次助攻）和约阿尼·维萨（Yoane Wissa）（3个进球，3次助攻）；没有一个有资格的非洲国家管理得更多。\n这两名前锋将帮助刚果民主共和国在世界杯上打进首个进球，但他们的比赛可能会很谨慎，豹队 13 场预选赛中有 10 场都是以一球或更少的比分决定胜负（6 胜、2 平、2 负）。"
            ],
            [
                "历史交锋",
                "葡萄牙是赛事常客，而刚果民主共和国已有 52 年没有出现在这个舞台上，两国此前从未在任何正式比赛或友谊赛中相遇。\n葡萄牙将成为第四个面对刚果民主共和国的欧足联国家，刚果民主共和国在 1974 年世界杯上被苏格兰和南斯拉夫击败（以 9-0 输给后者），并在上个月的赛前友谊赛中与丹麦 0-0 战平。\n葡萄牙在世界杯上仅有的两次输给非洲国家的经历都是在 1986 年的小组赛和 2022 年的四分之一决赛中对阵摩洛哥。然而，他们对撒哈拉以南非洲球队保持不败，取得三胜一平。"
            ],
            [
                "赛前预测（Opta 超算）",
                "刚果民主共和国获得本届世界杯资格后，FIFA 排名从第 56 位跃升至第 45 位，但 Opta 超级计算机仍然认为排名第五的葡萄牙更有可能赢得这场比赛。\n在 25,000 场赛前模拟中，葡萄牙在 54.5% 的结果中击败了刚果民主共和国，这场 K 组揭幕战平局的可能性为 22.3%。\n豹队获胜的几率为 23.2%，但塞巴斯蒂安·德萨布雷的球队肯定不会要求他们在世界杯回归时面临更严峻的考验。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "奥地利目前在 FIFA 世界排名中排名第 25 位，比排名第 64 位的约旦高出约 39 位。这种排名上的差距肯定反映在 Opta 的超级计算机对旧金山的超级计算机的预期中。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为奥地利队是这场比赛中压倒性的热门球队，获胜概率为 69.6%，而约旦队的获胜概率为 13.5%。\n· 奥地利在过去的九场世界杯比赛中只赢了一场。\n· 约旦在 2026 年 FIFA 世界杯预选赛中攻入 32 粒进球，这是他在单届预选赛中的最高进球数。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "奥地利队将在旧金山湾区体育场迎战首次亮相世界杯的约旦队，这是他们 28 年来首次参加世界杯。\n自98年法国队以来，他们就再也没有出现在全球足坛的舞台上，当时他们在三场比赛中只得到两分，在小组赛中惨遭淘汰。\n但奥地利近三年的缺席已经结束，拉尔夫·朗尼克带领他们第八次参加世界杯。他们在欧足联预选赛中以小组头名的身份领先于波黑队。\n他们必须付出一些努力才能打破他们在世界杯上的最佳表现，那是在 1954 年，当时他们在半决赛中被邻国西德队以 6-1 击败。然而，他们最终逆转击败乌拉圭，获得第三名。\n在对阵西德队的恐怖表演之前，奥地利队以7比5战胜东道主瑞士队，这是世界杯历史上进球最多的一场比赛。\n在最近的比赛中，奥地利的表现并不是特别好。他们在之前的九场世界杯比赛中只赢了一场，1990年2-1战胜美国队，另外8场比赛中3平5负。\n不过，历史表明，这一目标应该是可以预期的。奥地利队已经参加了 29 场世界杯比赛，从未取得过 0-0 的成绩，这是世界杯历史上没有0-0 平局的比赛次数最多的。\n老将前锋马尔科·阿诺托维奇现年 37 岁，但他在预选赛中的进球数是其他奥地利球员的两倍（8 个），证明了自己持久的实力。\n阿瑙托维奇和马塞尔·萨比策是仅有的两位在过去三届主要赛事（2016 年、2020 年和 2024 年欧洲杯）中为奥地利队出场的球员，而在欧足联预选赛中，只有埃尔林·哈兰德（28 次）射正次数多于后者（16 次）。\n虽然奥地利已经缺席世界杯近三十年，但约旦在为首次亮相做准备时完全是新手。\n世界杯新秀所在的小组看起来很棘手，其中还包括 2022 年冠军阿根廷队和阿尔及利亚队。他们正试图成为自1994年沙特阿拉伯队以来第一个在首次征战中就进入淘汰赛阶段的亚足联球队。\n乔丹打进了 32 个进球，这是他们在单场预选赛中的最高进球数，超过了他们在 2014 年预选赛中的 30 个进球。\n尽管他们可能无法进入小组赛，但约旦在 2023 年亚洲杯上展现了自己的勇气，他们在决赛中以 3-1 输给了东道主卡塔尔。\n阿里·奥尔万 (Ali Olwan) 和马哈茂德·阿尔·马迪 (Mahmoud Al-Mardi) 将是两名值得关注的球员——前者是乔丹在预选赛中的最佳得分手，贡献了 9 次助攻，而后者则是球队的最高助攻贡献者 (6 次)。"
            ],
            [
                "历史交锋",
                "小组赛中还包括卫冕冠军和国际足联排名第一的阿根廷队，这场比赛对于两支希望进入淘汰赛阶段的球队来说都是一场至关重要的比赛。\n随着阿尔及利亚队完成J组四强，任何一方的胜利对于各自晋级32强的机会都是巨大的。\n这场 J 组比赛将是这些国家队首次正面交锋。这也是奥地利队首次在世界杯上与亚足联国家队交锋。"
            ],
            [
                "赛前预测（Opta 超算）",
                "奥地利目前在 FIFA 世界排名中排名第 25 位，比排名第 64 位的约旦高出约 39 位。这种排名上的差距肯定反映在 Opta 的超级计算机对旧金山的超级计算机的预期中。\n奥地利获胜的概率高达 69.6%。乔丹的机会只有13.5%，平局也算是16.9%的命中率。\n阿根廷队是小组出线热门，但奥地利队有17.6%的概率击败他们夺得小组头名，远高于约旦的3.4%。\n就进入淘汰赛阶段而言，奥地利队以 77.1% 的希望出线，而约旦队的希望率为 30.7%。"
            ]
        ]
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
        "prediction": "Regardless, Amoura’s prowess in front of goal has set Algeria up for their fifth appearance at the World Cup, and their first since 2014. That edition in Brazil was the only time they have progressed past the first round, but the Opta supercomputer gives them a 57.4% chance of making the knockout stages here.",
        "summary_cn": "Opta 超级计算机预测莱昂内尔·斯卡罗尼 (Lionel Scaloni) 的球队将以一场胜利开始，阿根廷队在 25,000 次赛前模拟中以 67.8% 的优势获胜。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机的赛前模拟结果显示，阿根廷队以 67.8% 的准确率击败了阿尔及利亚队。\n· 自1962年巴西队卫冕以来，还没有球队连续两次夺得世界杯冠军。\n· 莱昂内尔·梅西可能成为历史上第一位参加六次不同版本的这项比赛的球员。"
            ],
            [
                "深度分析",
                "阿根廷队将于周三在堪萨斯城开始对阿尔及利亚队的世界杯防守，莱昂内尔·梅西准备在国际足联的顶级赛事上创造进一步的历史。\n莱昂内尔·斯卡罗尼 (Lionel Scaloni) 的球队在 ​​2022 年世界杯决赛中击败了法国队，成为 2026 年世界杯夺冠热门的第四支球队。 Opta超级计算机仅让西班牙、法国和英格兰队夺冠的机会高于阿根廷队的10.2%。\n但他们首先必须通过J组，其中奥地利和约旦是他们的另外两个对手。不出所料，卫冕冠军在 Opta 的赛前预测中以 69.2% 的准确率高居榜首。\n梅西将带领阿根廷队进攻，总共打进13粒世界杯进球并送出8次助攻。在周三 3-0 战胜冰岛的友谊赛中，他替补出场仅三分钟就点球得分。\n这位38岁的球员在世界杯上出场26次，比其他任何球员都多。如果他在这里出场，梅西将成为历史上第一位参加六届世界杯的球员，尽管葡萄牙的克里斯蒂亚诺·罗纳尔多稍后可能实现这一壮举。\n不过，斯卡罗尼并不仅仅想依靠梅西。朱利安·阿尔瓦雷斯和劳塔罗·马丁内斯是另外两名处于巅峰期的备受瞩目的攻击手，他们将带领阿根廷队参加第 19 届世界杯。\n阿尔瓦雷斯和马丁内斯均攻入四球，为梅西的八个进球提供支持，斯卡罗尼的球队自 2014 年以来首次在南美洲足球锦标赛预选赛中名列前茅。他们在门前的努力帮助阿根廷连续 14 次参加本届赛事，这是继巴西（23 次）和德国（19 次）之后连续第三长的连续出场纪录。\n但对于 La Albiceleste 来说，资格赛还不够。他们希望成为继意大利（1934-1938）和巴西（1958-1962）之后第三支连续赢得世界杯冠军的男子球队。\n只有巴西（5 次冠军）、德国和意大利（各 4 次）赢得男子世界杯的次数多于阿根廷（3 次）。然而，自 1978 年首次夺冠以来，没有哪个国家曾多次捧起奖杯。\n阿根廷希望避免任何早期的冲击——他们在过去 14 场比赛中有 13 次闯入首轮，2002 年是个例外。上一次他们在揭幕战中未能进球要追溯到 1990 年，当时 0-1 输给了喀麦隆。\n但阿尔及利亚不会轻易屈服。在本届非洲足联预选赛中，只有冈比亚（27 球）和科特迪瓦（25 球）比弗拉基米尔·佩特科维奇的球队（10 场比赛中 24 球）进球多。\n他们功绩的核心人物是穆罕默德·阿穆拉，他在 10 场比赛中攻入 10 个进球，成为预选赛的最佳射手。然而，沃尔夫斯堡前锋和巴格达布内贾（3）是唯一在该赛季多次进球的阿尔及利亚人。\n不过，佩特科维奇可能会对过度依赖阿莫拉感到有些担忧。阿尔及利亚预选赛24粒进球中有58%是他直接参与的，还贡献了4次助攻。\n不管怎样，阿穆拉在门前的出色表现让阿尔及利亚队第五次参加世界杯，这也是他们自 2014 年以来的第一次。那届巴西世界杯是他们唯一一次晋级第一轮，但 Opta 超级计算机让他们有 57.4% 的机会进入淘汰赛阶段。\n然而，他们在全球舞台上的命运却不佳。阿尔及利亚在过去10场世界杯比赛中只赢了一场，12年前4-2战胜韩国，而另外两场胜利是在1982年。\n在球场的另一端，阿尔及利亚队在 13 场比赛中只取得了一场不失球（2010 年与英格兰队互交白卷）。"
            ],
            [
                "历史交锋",
                "这将是两人在世界杯上的首次交锋，但阿根廷队在 2007 年 6 月的唯一一次友谊赛中以微弱优势获胜。\n在那场比赛中，梅西为阿根廷队梅开二度，帮助球队在巴塞罗那诺坎普球场以4-3获胜。\n阿尔及利亚在世界杯上对阵南美洲球队的战绩相当平衡，取得一场胜利（1982年3-2对阵智利）和一场失败（1986年1-0对阵巴西）。\n相比之下，阿根廷在 1990 年首场交锋中以 1-0 输给喀麦隆后，过去六次与非洲对手的此类比赛都取得了胜利，其中五场对阵尼日利亚。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机预测莱昂内尔·斯卡罗尼 (Lionel Scaloni) 的球队将以一场胜利开始，阿根廷队在 25,000 次赛前模拟中以 67.8% 的优势获胜。\n在相同数据主导的情景中，阿尔及利亚仅获得第四次世界杯胜利，而平局则占 19.2%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer is confident of a Norway win here, with Solbakken’s side starting the tournament with a win in 75.9% of its 25,000 simulations. The next-most likely result is a draw at 14.2%. Meanwhile, Iraq are regarded as having a 9.9% chance of earning a shock win.",
        "summary_cn": "Opta 超级计算机对挪威队在这里获胜充满信心，索尔巴肯的球队在 ​​25,000 次模拟中以 75.9% 的胜利开始比赛。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 挪威被​​认为是这场比赛的明显夺冠热门，在 Opta 超级计算机的 25,000 次模拟中，挪威队以 75.9% 的胜率名列前茅。\n· 挪威是欧足联预选赛中 100% 获胜的两支球队之一（8/8），另外一支是英格兰。他们还每场打入 4.6 个进球（8 场比赛 37 个进球），这是欧洲国家队在单场 FIFA 世界杯预选赛 4 场以上比赛中的最佳平均进球数。\n· 伊拉克是第 48 支也是最后一支获得 2026 年 FIFA 世界杯参赛资格的球队，他们参加了 21 场预选赛，比任何其他球队都多。他们通过洲际附加赛在墨西哥2-1击败玻利维亚获得参赛资格。"
            ],
            [
                "深度分析",
                "伊拉克和挪威将于周二重返国际足联世界杯，这场比赛可能取决于一个关键问题：伊拉克能否阻止埃尔林·哈兰德？\n哈兰德感觉自己几乎可以在国际舞台上占据统治地位，他在 50 场比赛中为挪威队打进 55 粒进球的惊人表现也说明了这一点。然而，他以前从未有机会在大型比赛中展示自己的才华。挪威队最后一次亮相是在 2000 年欧洲杯上，比赛在哈兰德出生前 21 天结束。\n不过，在经历了几次失败的预选赛之后，挪威队似乎已经进入状态，一支才华横溢的球队终于意识到了自己的潜力。\n他们或许是整个世界杯预选赛中的统治者，赢得了全部八场比赛，同时打进了惊人的 37 个进球。英格兰是唯一一支每场比赛都获胜的欧洲球队。\n与此同时，挪威每场4.6个进球的进球率是欧洲国家在单场超过四场比赛的世界杯预选赛中平均进球数最高的。\n马丁·厄德高是其中的关键贡献者，他贡献了欧足联最高的七次助攻，他得到了亚历山大·索罗斯、安东尼奥·努萨和朱利安·瑞尔森等人的大力支持。但哈兰德毫无疑问是头条新闻，在预选赛中攻入 16 粒进球，是欧洲国家球员的两倍。\n他的功绩帮助挪威重返国际足坛榜首，而这已经是一个漫长的过程了。这是他们自1998年以来首次参加世界杯，当时他们在16强中被意大利淘汰，现任主教练索尔巴肯替补出场。\n他们还参加了 1994 年的锦标赛，这是之前唯一一次在美国举办的赛事，但以非同寻常的方式被淘汰。小组赛四支球队在积分和净胜球上均取得平局，这在世界杯历史上尚属绝无仅有。然而，挪威队由于进球最少而排名垫底。很难想象今年在哈兰德的带领下这对他们来说是一个问题。\n挪威队与法国队、塞内加尔队以及本场比赛的对手伊拉克队一起分在第一组，可以理解的是，伊拉克队在如此拥挤的小组中不太可能取得好成绩，根据 Opta 实力排名，伊拉克队是最难的小组。\nOpta超级计算机认为他们进入淘汰赛阶段的机会为21.9%，落后于法国（95.3%）、挪威（86.0%）和塞内加尔（60.4%）。\n伊拉克的秘密武器或许是主教练格雷厄姆·阿诺德的经验，他带领澳大利亚队进入了2022年卡塔尔世界杯的淘汰赛阶段。澳大利亚队在与突尼斯和丹麦队同组的小组中，凭借净胜球优势排名第二，落后于法国队。他们在 16 强赛中被最终冠军阿根廷队淘汰，并以 2-1 失利。\n他率领的澳大利亚队还在 2022 年世界杯预选赛中创下了连续 11 场比赛获胜的记录。\n对于阿诺德来说，2026 年版本的资格赛有点复杂。伊拉克是第 48 支也是最后一支获得 2026 年世界杯参赛资格的球队，他们参加了 21 场预选赛才晋级，比任何其他球队都要多。他们通过洲际附加赛在墨西哥2-1击败玻利维亚获得参赛资格。\n他们将迫切希望提高自己在 1986 年世界杯上的记录，当时他们三场小组赛全部失利。阻止哈兰德带领的挪威队的猛烈进攻将是他们面临的第一个挑战。"
            ],
            [
                "历史交锋",
                "这将是伊拉克和挪威之间的首次会议。这也将是挪威在世界杯上首次对阵亚足联成员。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机对挪威队在这里获胜充满信心，索尔巴肯的球队在 ​​25,000 次模拟中以 75.9% 的胜利开始比赛。\n第二个最可能的结果是 14.2% 的平局。与此同时，伊拉克被认为有 9.9% 的机会获得惊人胜利。"
            ]
        ]
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
        "prediction": "Still, though, the Opta supercomputer expects Les Bleus to emerge triumphant at New York New Jersey Stadium, with a win probability of 65.6%. By contrast, Senegal are rated as a mere 14.9% chance to get off to a winning start, while the draw is a 19.5% shot.",
        "summary_cn": "法国目前在国际足联的世界排名中排名第三，并且是本届世界杯的热门球队之一，尽管排名第 16 的塞内加尔将是一个棘手的首场对手。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 凭借 Opta 超级计算机，法国队显然是这场比赛中最热门的球队，其获胜概率为 65.6%，而塞内加尔的获胜概率为 14.9%。\n· 基利安·姆巴佩在过去两届世界杯上的进球数超过任何其他球员。\n· 塞内加尔在 12 场世界杯比赛中仅保持一场不失球。"
            ],
            [
                "深度分析",
                "法国队周二将在 2026 年世界杯揭幕战中对阵塞内加尔，开始寻求加入一家备受尊敬的球队。\n四年前，高卢雄鸡队在卡塔尔举行的一场经典决赛中负于阿根廷队获得亚军，此前他们曾于 2018 年在俄罗斯夺冠。\n他们现在的目标是成为继西德队（1982-1990年）和巴西队（1994-2002年）之后第三支连续三次进入世界杯决赛圈的球队。\n此外，法国在过去七届世界杯中有四届（1998年、2006年、2018年和2022年）进入决赛，是该时期其他国家的两倍。\n皇马巨星基利安·姆巴佩是法国队在 2018 年和 2022 年世界杯上表现强劲的主角，在这两届赛事中攻入了最多进球（12 个）。这一纪录使他与巴西伟大的贝利持平，距离米罗斯拉夫·克洛泽保持的历史纪录仅差四分。\n这 12 个进球包括 2022 年决赛中的帽子戏法，这使他成为继 1966 年代表英格兰队的杰夫·赫斯特之后第二位在这场表演赛中实现这一壮举的球员。\n法国队第 17 次参加世界杯，也是连续第八次参加世界杯，这是他们历史上最长的连续参赛纪录。高卢雄鸡队是两届冠军得主，也是最后一支以东道主身份夺得世界杯冠军的球队，那是 28 年前的 1998 年。\n迪迪埃·德尚当时担任法国队队长，他是作为球员和主教练赢得世界杯的三名球员之一，另外两个是马里奥·扎加洛和弗朗茨·贝肯鲍尔。\n这场比赛将是德尚作为法国队主帅的第 20 场世界杯比赛，只有赫尔穆特·舍恩在单支球队中执教次数最多（25 场比赛，西德队）。\n塞内加尔队在世界杯上爆冷战胜法国队并不陌生，在2002年世界杯揭幕战中，塞内加尔队以1-0击败法国队，当时这支欧洲豪门以卫冕冠军身份参赛。\n这是他们第一次参加足球界最盛大的国际赛事，但这个非洲国家继 2002 年（四分之一决赛）、2018 年（小组赛）和 2022 年（16 强）之后第四次晋级。\n这是他们连续第三次参加世界杯，这标志着非洲球队与摩洛哥和突尼斯并列连续参加世界杯最长纪录。\n然而，塞内加尔在世界杯上唯一一次不失球是在前面提到的1-0战胜法国队的比赛中；自那以后他们参加的11场比赛中每一场都丢球。\n塞内加尔在预选赛中表现强劲，保持不败，领先于刚果民主共和国以小组第一的身份晋级，同时他们还在今年早些时候首次赢得了非洲国家杯冠军。然而，非洲足球联合会（CAF）后来推翻了这一决定，将决赛判给了摩洛哥，因为决赛中对东道主的点球引发了争议，导致塞内加尔离开了球场。\n萨迪奥·马内是塞内加尔历史上的最佳射手，他是球队在预选赛中的最佳射手，攻入五球。这位34岁的球员此前只参加过一届世界杯，并在2018年参加了全部三场比赛。\n2002年塞内加尔战胜法国队的比赛中，主教练帕普·蒂奥（Pape Thiaw）作为未上场的替补球员，并且在那场比赛中只出场过一次。不过，他确实为亨利·卡马拉在 16 强对阵瑞典的比赛中攻入金球提供了助攻。这标志着他作为主教练第一次参加世界杯。"
            ],
            [
                "历史交锋",
                "法国队可能是这场比赛中获胜的热门球队，但他们在世界杯上的最低时刻之一是2002年对阵塞内加尔队。\n作为卫冕冠军参加日本和韩国的比赛，这支众星云集的球队在首尔以 1-0 惨败于当时首次参加比赛的塞内加尔队。\n帕帕·布巴·迪奥普在那场比赛中攻入制胜球，而现任主教练蒂奥是球队后来进入四分之一决赛的一员。\n对于法国队来说，这是一场极其糟糕的比赛的开始，他们只以一分的成绩被小组出局。\n他们在过去四场世界杯小组赛对阵非洲球队的比赛中输掉了三场，2010年0-1负于塞内加尔，2010年1-2负于南非，2022年0-1负于突尼斯。唯一的例外是2006年2-0战胜多哥。"
            ],
            [
                "赛前预测（Opta 超算）",
                "法国目前在国际足联的世界排名中排名第三，并且是本届世界杯的热门球队之一，尽管排名第 16 的塞内加尔将是一个棘手的首场对手。\n尽管如此，Opta 超级计算机仍然预计 Les Bleus 将在纽约新泽西体育场取得胜利，获胜概率为 65.6%。\n相比之下，塞内加尔队获胜的几率仅为 14.9%，而平局的几率为 19.5%。\n就本届赛事整体而言，法国队获得第一组冠军的概率为60.3%，进入淘汰赛的概率为95.3%。他们也被认为是继西班牙之后第二有可能赢得世界杯的球队，夺冠的可能性为 13.4%。\n与此同时，塞内加尔队以 10.1% 的概率获得小组冠军，并被认为有 60.4% 的机会进入淘汰赛阶段。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours an Iran victory, with Ghalenoei’s side winning 51.4% of the 25,000 pre-match simulations. New Zealand’s chances of claiming that first ever World Cup win are rated at 21.9%, with a draw at 26.7%.",
        "summary_cn": "Opta 超级计算机支持伊朗队获胜，加勒诺伊的球队在 ​​25,000 次赛前模拟中获胜率为 51.4%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 只有苏格兰（8 次）比伊朗（6 次）参加世界杯比赛的次数多于伊朗队（6 次），但他们是 Opta 获胜的热门球队，获胜的几率为 51.4%。\n· 只有洪都拉斯（9 场）和埃及（7 场）比新西兰（6 场）参加的世界杯比赛次数多，但从未取得过胜利。\n· 伊朗队在决赛中的最后8个进球全部是在下半场打进的，其中5个进球是在伤停补时阶段打进的。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "新西兰队将在洛杉矶体育场与伊朗队进行 G 组比赛，目标是在 FIFA 世界杯上首次取得胜利。\n16年前，全白队一直是南非决赛中唯一一支保持不败的球队。里基·赫伯特的球队在小组赛的所有三场比赛中都获得一分，其中包括1-1战平卫冕冠军意大利，但无法避免首轮出局。\n1982年首次参加世界杯的新西兰队在决赛中六场比赛均未尝胜绩（平3负3）；只有洪都拉斯（9）和埃及（7）在未取得胜利的情况下交手次数更多。\n打破那只鸭子将是达伦·贝兹利 (Darren Bazeley) 球队的主要目标，大洋洲足联保证了 2026 年锦标赛的席位，球队充分利用了优势，赢得了所有五场资格赛，一路上攻入 29 个进球，只丢了一次。\n巧合的是，早在 2025 年 3 月，新西兰就只比伊朗晚了一天获得参赛资格，只有日本比这两个国家更早预订了北美门票。然而，他们在进入决赛时并没有充满信心，在过去 11 场比赛中只赢了一场（L8）。\n全白队需要灵感，并希望他们的护身符克里斯·伍德（2010 年阵容中唯一一位同时参加 2026 年锦标赛的成员）能够摆脱伤病困扰的赛季，带领他们的进攻。作为该国历史上领先的射手和出场球员，他在 OFC 预选赛中以五场比赛中的 9 粒进球名列前茅。现年 34 岁的诺丁汉森林前锋将不顾一切地抓住机会，在最大的舞台上大放异彩。\n在伊朗队之前六次参加世界杯的比赛中，进球一直是一个问题。在决赛场次达到或超过15场的球队中，他们的场均得分最少（0.72），而胜率只有保加利亚（11.5%）低于他们（16.7%）。\n事实上，伊朗在世界杯的 18 场比赛中只赢了 3 场，尽管其中两场相当重要。他们在 1998 年决赛中以 2-1 击败美国队，四年前在卡塔尔，他们以 2-0 的胜利为加雷斯·贝尔 (Gareth Bale) 的威尔士队终结。\n如果伊朗队想要在第七次尝试中晋级小组赛，那么今年他们可能需要至少一场胜利。只有苏格兰队（8支球队）在决赛中出场次数最多但从未闯过第一轮。\n主教练阿米尔·加勒诺伊希望他的球队能够在持续的伊朗战争中为他们的国家提供一些值得欢呼的东西，这场战争威胁到了他们在北美的参赛资格。\n伊朗队在预选赛中的表现相当轻松，在 16 场比赛中只输掉了一场，而在第二轮和第三轮小组赛中都击败了乌兹别克斯坦队取得了头名。\n迈赫迪·塔雷米 (Mehdi Taremi) 在他们中扮演了主角。现在，这位经验丰富的前锋正在与奥林匹亚科斯队进行交易，他直接参与了球队 35 个进球中的 49%（10 粒进球，7 次助攻），同时他的上场时间也比任何队友都多（1,131 分钟）。和伍德一样，这位 33 岁的球员也决心对他的世界杯绝唱产生类似的影响。"
            ],
            [
                "历史交锋",
                "这将是两国之间的第三次会面，也是他们第一次在正式比赛中会面。\n1973年8月，两队在奥克兰首次交锋，双方互交白卷。\n时间快进到 2003 年，伊朗队在德黑兰交锋时以 3-0 获胜。阿里·卡里米上半场的梅开二度帮助球队控制了局势，下半场中段侯赛因·卡比的进球锁定了胜利。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持伊朗队获胜，加勒诺伊的球队在 ​​25,000 次赛前模拟中获胜率为 51.4%。\n新西兰首次夺得世界杯冠军的几率为 21.9%，平局的几率为 26.7%。\n然而，令全白队感到鼓舞的是，伊朗队在决赛中往往表现缓慢。\n他们在之前的六场比赛中只赢了一场首场比赛（平一平四）——2018 年击败了摩洛哥——而他们在决赛中的最后 8 个进球都是在下半场打进的。"
            ]
        ]
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
        "prediction": "After 25,000 pre-match simulations, the Opta supercomputer predicted success for Uruguay, with the South American side having a 63.2% chance of victory. Saudi Arabia start as long shots: only prevailing in 14.8% of those simulations, leaving a draw rated at 22.0%.",
        "summary_cn": "经过 25,000 次赛前模拟，Opta 超级计算机预测乌拉圭队获胜，南美球队获胜的几率为 63.2%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机以极大的优势赢得了乌拉圭队首场比赛的胜利，使乌拉圭队有 63.2% 的机会获胜。\n· 沙特阿拉伯的成功几率只有 14.8%，预计不会在 2022 年卡塔尔世界杯首轮比赛中重演对阵阿根廷的令人震惊的结果。\n· 只有三人在世界杯上执教的球队数量比乌拉圭主帅马塞洛·贝尔萨（3）多，但他的球队从未在一场比赛中进球超过一次。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "首届世界杯冠军和 2034 年东道主将于周一在迈阿密相遇，乌拉圭队将在 H 组揭幕战中与沙特阿拉伯队展开对决。\n沙特阿拉伯队在亚冠预选赛中表现不佳，在倒数第二阶段以遥远的成绩获得第三名，然后在第四轮击败伊拉克和印度尼西亚队获得榜首。\n在 12 场比赛中仅打进 10 粒进球，导致主教练埃尔维·雷纳德 (Hervé Renard) 离开（他于 2022 年带领球队前往卡塔尔），希腊教练乔治斯·多尼斯 (Georgios Donis) 接任。\n到目前为止，结果好坏参半，多尼斯在首场比赛中输给了厄瓜多尔，随后在赛前友谊赛中以 3-0 击败波多黎各并与塞内加尔 0-0 战平。\n尽管沙特阿拉伯在 2022 年世界杯的第一场比赛中令人震惊地击败了最终的冠军阿根廷队，但在此前的比赛中（13/19），沙特阿拉伯队输掉了 68%，这是所有参加 15 场以上比赛的国家中输掉率最差的。\n他们还只保持过一场不失球，那是1994年著名的1-0战胜比利时的比赛，当时萨伊德·阿尔·奥维兰的个人进球让他们迄今为止唯一一次小组赛阶段出局。\n现在，他们在返回北美时必须努力效仿这一壮举，而希望主要落在两个人的肩上。\n费拉斯·阿尔布里坎 (Feras Al Brikan) 是他们在预选赛中的最佳射手，攻入 5 个进球，其中包括在关键的 3-2 战胜印度尼西亚的比赛中梅开二度。与此同时，卫冕亚洲年度最佳球员塞勒姆·阿尔·道萨里（在对阵阿根廷队的比赛中打入进球）在 34 岁时仍然具有影响力。\n在沙特队对阵 H 组热门西班牙队和首次亮相的弱旅佛得角队之前，与乌拉圭队的第二场世界杯比赛正在等待着。\n第一次交锋是在 2018 年小组赛，乌拉圭凭借路易斯·苏亚雷斯的进球以 1-0 获胜，但这个南美国家的开局并不顺利。\n拉塞莱斯特队在过去的八场世界杯揭幕战中只赢了一场（平四平三），而他们在老教练马塞洛·贝尔萨的带领下经历了两年困难时期。\n一个真正的特立独行者，这将是他的第三次世界杯。他曾在不同的国家队执教过这些球队，2002 年在祖国阿根廷执教，八年后又在智利执教。\n贝尔萨的孩子们必须承担一段辉煌的——尽管遥远的——历史的重担：乌拉圭在 1930 年和 1950 年获得冠军，是仅有的六个多次赢得世界杯的国家之一。\n乌拉圭队将连续第五次参赛，现在他们希望能够打破自 1950 年夺冠以来的最佳表现——1954 年、1970 年和 2010 年再次获得第四名。\n乌拉圭还在南美洲预选赛中获得第四名，尤其是唯一一支客场击败阿根廷的球队，但在客场却表现不佳。\n在整个马拉松比赛中，达尔文·努涅斯直接参与的进球最多（5个进球，2个助攻），而只有哥伦比亚球星詹姆斯·罗德里格斯（7个）比马克西·阿劳霍（4个）进球多。\n努涅斯应该在周一带领乌拉圭队前线，但主创乔治安·德·阿拉斯卡埃塔、罗纳德·阿劳霍和队长何塞·玛丽亚·吉梅内斯的健康状况存疑。如果后者缺席，副队长费德里科·巴尔韦德将佩戴队长袖标。\n就沙特阿拉伯而言，他们仍然缺少首选门将纳瓦夫·阿尔·阿奇迪，因此经验丰富的副门将穆罕默德·阿尔·奥瓦伊斯可能会被要求介入。"
            ],
            [
                "历史交锋",
                "这将是两队在世界杯上的第二次交锋，八年前乌拉圭在罗斯托夫以 1-0 获胜；路易斯·苏亚雷斯在阿尔·奥维斯失误后攻入唯一进球。\n2014 年 10 月，他们还在利雅得法赫德国王体育场打了一场友谊赛，最终以 1-1 告终。"
            ],
            [
                "赛前预测（Opta 超算）",
                "经过 25,000 次赛前模拟，Opta 超级计算机预测乌拉圭队获胜，南美球队获胜的几率为 63.2%。\n沙特阿拉伯一开始的胜算不大：只有 14.8% 的模拟获胜，平局率为 22.0%。"
            ]
        ]
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
        "prediction": "Belgium came out on top in 60.2% of simulations, with Egypt winning in just 17.8%.",
        "summary_cn": "Opta 超级计算机进行了 25,000 次赛前模拟，使比利时成为获胜的热门球队。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机最喜欢比利时（60.2%）。\n· 比利时第 15 次参加世界杯；没有哪支欧洲球队有资格参加如此多的赛事但从未赢得过奖杯。\n· 只有洪都拉斯（9场）比埃及（7场）参加的世界杯比赛次数多，但从未取得过胜利。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "比利时希望在周一在西雅图体育场对阵埃及的国际足联世界杯 G 组揭幕战中继续他们近期令人印象深刻的状态。\n鲁迪·加西亚的球队在 ​​13 场比赛中保持不败，上一场在布鲁塞尔对阵突尼斯的比赛中以 5-0 获胜，其中有 5 名球员进球。\n这代表着加西亚令人印象深刻的转变的延续，加西亚于2025年1月接替多梅尼科·特德斯科，尽管输掉了他执教的第一场比赛，但帮助红魔避免了从欧洲国家联赛A级联赛降级。\n随后，这位法国人带领球队以不败战绩取得了世界杯预选赛的不败战绩，并打入 29 粒进球，小组第一，欧洲区进球数仅次于挪威（37 球）。\n曼城队边锋杰里米·多库参与了近四分之一的预选赛进球，其中五粒进球、两次助攻，并在战胜突尼斯的比赛中贡献了两次助攻。\n多库将被要求继续对进球构成威胁，而罗梅卢·卢卡库则被加西亚称为“身材走样”，因为他在 2025-26 赛季的大部分时间里都因肌肉反复受伤而缺席比赛。\n但卢卡库是比利时历史进球纪录保持者，他将渴望在本届世界杯上留下自己的印记，这可能会成为国家队黄金一代剩余球员的绝唱。\n穆罕默德·萨拉赫在参加世界杯时也可能感觉自己在利物浦令人失望的最后一个赛季中需要证明自己——他在联赛中的 14 粒进球是他自 2014-15 赛季效力切尔西和佛罗伦萨以来最差的表现。\n这位埃及前锋将在这场比赛当天庆祝他的 34 岁生日，毫无疑问，他很乐意带领他的国家队在世界杯上取得首场胜利来纪念这一点。\n法老队需要萨拉赫继续在国际比赛中令人印象深刻的表现，在预选赛不败的比赛中，他在球队 60% 的进球中发挥了作用（9 粒进球，3 次助攻）。\n萨拉赫下半场上场，埃及队在最后一场热身赛中1-0战胜俄罗斯队，1-2负于巴西队。\n尽管结果是后者，他们仍没有受伤的情况进入锦标赛。尽管如此，主教练霍萨姆·哈桑可能会采取保守的做法，让奥马尔·马穆什和萨拉赫在进攻上有足够的自由。\n据报道，多库已经摆脱了训练中的伤病，而蒂博·库尔图瓦将在没有意外情况下首发出场，这将是他第 16 次参加世界杯，追平扬·库勒曼斯 (Jan Ceulemans)，仅次于恩佐·西福 (Enzo Scifo) 的国家纪录 (17 次)。"
            ],
            [
                "历史交锋",
                "这将是比利时和埃及首次在世界杯上交手，但此前他们曾在友谊赛中交手过四次。\n埃及队对比利时队取得了三场胜利，法老队上次交锋是在 2022 年 11 月在科威特城，以 2-1 获胜。穆斯塔法·穆罕默德和特雷泽盖的进球是那次比赛的关键。\n但比利时在世界杯对阵非洲对手的五场比赛中只输了一场（3胜1平），那是2022年0-2负于摩洛哥的比赛。这一结果导致他们未能小组出线，你不会指望他们在北美重蹈覆辙。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机进行了 25,000 次赛前模拟，使比利时成为获胜的热门球队。\n比利时在 60.2% 的模拟中名列前茅，埃及仅以 17.8% 获胜。\n他们分享战利品的几率为22.3%"
            ]
        ]
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
        "prediction": "From 25,000 pre-match simulations, De la Fuente’s side came out on top in 87.2% of the outcomes, suggesting that Spain could make a significant statement right from the off. A draw stands at an 8.1% probability with a Cape Verde victory even lower at just 4.8%, but having already shocked the world just by reaching this tournament, Bubista’s Blue Sharks may have another upset in their arsenal.",
        "summary_cn": "由于欧洲冠军队将迎战世界排名第 67 位的世界杯新秀，Opta 超级计算机认为西班牙队在这场 H 组揭幕战中获胜的可能性极大。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机非常期待西班牙队在世界杯征程中取得领先，赛前模拟结果中有 87.2% 的结果是 2024 年欧洲杯冠军获胜。\n· 西班牙队第 17 次参加世界杯，也是连续第 13 次参加世界杯，这是欧洲国家目前连续参加世界杯时间第二长的球队，仅次于德国队连续参加 19 届世界杯。\n· 佛得角是第14支参加本届世界杯的非洲球队，他们的目标是成为自2006年加纳以来第一支在世界杯首秀就进入淘汰赛阶段的非洲球队。"
            ],
            [
                "深度分析",
                "整个国家都在期待欧洲卫冕冠军将在 2026 年 FIFA 世界杯上亮相，2024 年欧洲杯冠军西班牙将在佐治亚州亚特兰大体育场对阵佛得角的比赛中揭幕战。\n路易斯·德拉富恩特的球队将在 H 组（还包括沙特阿拉伯和乌拉圭）对阵本届世界杯的四支首次参赛球队之一，他们希望为余下的比赛早日奠定胜局。\n两年前，西班牙在上一场大型赛事的决胜局中以 2-1 击败英格兰队后，在本届世界杯上以六场比赛五胜的成绩位列预选赛小组第二，位列国际足联排名第二。\n作为欧洲冠军，今年夏天一路走来将成为继西德（1972年欧洲杯、1974年世界杯）、法国（1998年世界杯、2000年欧洲杯）和西班牙（2008年欧洲杯、2010年世界杯、2012年欧洲杯）之后第四支球队同时获得世界冠军和欧洲冠军。\n德拉富恩特带领西班牙重回辉煌，他的球队目前在过去 31 场正式比赛中保持不败，自 2023 年 3 月 0-2 输给苏格兰以来，取得了 25 场胜利，这是他们历史上最长的非友谊赛不败记录。\n西班牙队在本届世界杯预选赛中平均每 90 分钟射正 9.7 次，比任何其他球队都多，这体现了西班牙队的统治地位。\n米克尔·奥亚扎瓦尔是 2024 年欧洲杯决赛中西班牙队制胜球的进球者，他是欧足联预选赛中仅有的三名进球超过 10 的球员之一，他的 6 粒进球和 4 次助攻仅次于埃尔林·哈兰德（18 粒进球）和孟菲斯·德佩（12 粒进球）。\n自西班牙获得本届世界杯参赛资格以来，奥亚萨瓦尔继续进球，在 2026 年的四场友谊赛中攻入 3 球，维克多·穆尼奥斯、费兰·托雷斯和佩德里也有进球。\n然而，西班牙在最近几届世界杯上的战绩远非万无一失，他们在过去的六场比赛中只在 90 分钟内赢了一场——2022 年小组赛以 7-0 战胜哥斯达黎加。\n这场胜利可能为西班牙队树立标杆，西班牙队在击败非洲传统豪门喀麦隆队，在非洲足联预选赛小组中获得头名后，将在世界杯上首次对阵佛得角队。\n佛得角在预选赛中唯一的失利是客场负于喀麦隆（4-1），尽管蓝鲨确实是本届世界杯的非洲球队中净胜球最少的球队（+8）。\n佛得角是与库拉索岛、约旦和乌兹别克斯坦一起首次亮相非洲杯的四支球队之一，在主教练布比斯塔的带领下，曾两次晋级非洲国家杯淘汰赛阶段。\n事实上，佛得角在非洲杯的四场比赛中，有三场都进入了淘汰赛阶段，并在 2013 年和 2023 年（后者在布比斯塔的带领下）进入了四分之一决赛。\n佛得角以七战六胜的成绩结束预选赛，在本届世界杯上以 3-0 的比分横扫塞尔维亚和百慕大，在两场赛前友谊赛中以 3-0 的比分横扫塞尔维亚和百慕大。\n前锋戴隆·利夫拉门托 (Dailon Livramento) 在 2026 年世界杯的最后五场预选赛中攻入 4 粒进球；他在其中三场比赛中攻入首球，其中包括1-0战胜喀麦隆的关键比赛。\n在老将前里尔和诺丁汉森林边锋瑞安·门德斯的带领下，佛得角有几个名字为西班牙球员所熟知，尽管相比之下，这些名字有些不为人知，其中包括比利亚雷亚尔中后卫洛根·科斯塔。"
            ],
            [
                "历史交锋",
                "这将是西班牙和佛得角之间的首次交锋，这个非洲岛国将在最大的足球舞台上亮相。\n尼日利亚是唯一一支在世界杯上击败西班牙的非洲国家队，在 1998 年小组赛中以 3-2 获胜。\n西班牙队最近两场对阵非洲球队的比赛都是对阵摩洛哥，2018 年两队战成 2-2 平，2022 年四分之一决赛双方互交白卷（点球大战 0-3 失利）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "由于欧洲冠军队将迎战世界排名第 67 位的世界杯新秀，Opta 超级计算机认为西班牙队在这场 H 组揭幕战中获胜的可能性极大。\n在 25,000 次赛前模拟中，德拉富恩特的球队在 ​​87.2% 的结果中名列前茅，这表明西班牙可以从一开始就做出重要声明。\n平局的概率为 8.1%，佛得角获胜的概率更低，仅为 4.8%，但布比斯塔的蓝鲨队仅仅进入本届锦标赛就已经震惊了世界，他们的武器库中可能会再次爆出冷门。"
            ]
        ]
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
        "prediction": "Sweden enter this Group F opener as favourites according to the Opta supercomputer, with Potter’s side coming out on top in 51.1% of the 10,000 pre-match simulations. Tunisia managed victory in a slim 23.2% of the supercomputer’s simulations, while a draw is rated at a 25.7% shot.",
        "summary_cn": "根据 Opta 超级计算机的数据，瑞典队作为 F 组揭幕战的热门球队，波特的球队在 ​​10,000 次赛前模拟中以 51.1% 的胜率名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机在开球前将格雷厄姆·波特领导的瑞典视为夺冠热门，获胜概率为 51.1%，而突尼斯为 23.2%。\n· 周日的比赛是两支球队在世界杯上的首次交锋，之前的四次交锋都是友谊赛。\n· 瑞典在 12 场世界杯揭幕战中只输掉了 2 场（5 胜 5 场），并且在过去 4 场比赛中均保持不败（1 胜 3 场）。"
            ],
            [
                "深度分析",
                "周日在蒙特雷球场举行的 F 组揭幕战中，瑞典队将迎战突尼斯队，希望能顺利重返世界杯决赛圈。\n瑞典队第 13 次参加世界杯，这也是他们自 2018 年以来首次参加世界杯，当时他们进入四分之一决赛，但最终以 2-0 输给了最终进入半决赛的英格兰队。\n这次，瑞典队经历了巨大的变化，重返国际舞台，其中包括亚历山大·伊萨克、维克托·杰克雷斯、卢卡斯·伯格瓦尔和安东尼·埃兰加等领军人才。\n尽管预选赛经历了动荡，格雷厄姆·波特的球队将满怀信心地抵达瓜达卢佩，在过去四届世界杯中每一届都从小组赛阶段晋级。\n他们可能还希望在今年由美国、加拿大和墨西哥共同主办的世界杯上重演历史，瑞典上次进入半决赛是在 1994 年世界杯上，同样在美国举办。\n但正如他们的资格之旅所表明的那样，事情不会一帆风顺。瑞典在预选赛中垫底，落后于瑞士、科索沃和斯洛文尼亚，仅凭借欧洲国家联赛排名（第 34 位）进入附加赛。\n此后，波特的任命帮助瑞典队重振旗鼓，瑞典队分别以3-1和3-2战胜乌克兰队和波兰队，获得了决赛席位。\n这只会增强瑞典的信心，因为他们在世界杯首场 12 场比赛中只输了两场（5 胜 5 场），并且在过去 4 场比赛中都保持不败（1 胜 3 场），上一次这样的失利可以追溯到 1990 年 2-1 输给巴西。\n与此同时，突尼斯队已经跻身精英球队之列，他们正准备第七次参加世界杯，更确切地说，他们将连续第三次参加世界杯。\n这是非洲国家连续参加世界杯时间最长的纪录，另外还有摩洛哥和塞内加尔。然而，突尼斯队从未晋级过第一轮，只有苏格兰队（八支球队）在世界杯上出场次数更多，但没有晋级。\n然而，突尼斯队在 1978 年以 3-1 击败墨西哥队，成为第一支赢得世界杯比赛的非洲球队。\n尽管他们在周日和整个锦标赛中仍被视为弱者，但萨布里·拉穆奇的球队不应被低估。\n他们在预选赛中表现出色，在 30 场比赛中以 28 分（9 胜 1 平）的成绩位列小组第一，并且是除科特迪瓦之外仅有的两支在预选赛期间不失一球的非洲足联球队之一。\n这应该会让他们处于有利地位，因为他们面对的是艰难的 F 组，其中还包括瑞典、荷兰和日本，这些球队都拥有出色的进攻能力。\n因此，Opta 超级计算机将突尼斯列为最不可能取得进步的国家也就不足为奇了，他们的晋级机会为 43.4%。\n瑞典晋级下一轮的概率为 62.6%，落后于小组热门荷兰（88.2%）和日本（76.2%）。\n突尼斯此前在世界杯上的成绩也并不理想，他们在 18 场比赛中只赢了 3 场（胜率为 16.7%）。在参加过至少 15 场世界杯比赛的国家中，只有保加利亚（11.5%）的胜率较低。\n尽管期望不高，拉穆奇仍然希望穆罕默德·本·罗姆丹（四粒进球）和阿里·阿卜迪（一粒进球，三次助攻）能够将他们的资格赛状态带上大舞台。\n与此同时，波特将指望吉克雷斯来领导瑞典队的进攻。这位前锋在瑞典资格赛附加赛中攻入了六个进球中的四个，在对阵乌克兰的比赛中上演帽子戏法，然后在对阵波兰的决赛中第88分钟攻入制胜球。"
            ],
            [
                "历史交锋",
                "这场比赛将是瑞典和突尼斯之间的首次正式交锋，也是他们在世界杯上的首次交锋。\n此前四次交锋都是在国际友谊赛中，瑞典取得两胜，突尼斯取得一场平局。他们最近一次交锋是在 2003 年 2 月，当时突尼斯队在主场 1-0 获胜。\n不过，突尼斯队在世界杯对阵欧洲对手的 12 场比赛中只赢了一场（平 4 负 7），但这场胜利确实是在 2022 年对阵最终亚军法国队时取得的（小组赛 1-0）。"
            ],
            [
                "赛前预测（Opta 超算）",
                "根据 Opta 超级计算机的数据，瑞典队作为 F 组揭幕战的热门球队，波特的球队在 ​​10,000 次赛前模拟中以 51.1% 的胜率名列前茅。\n在超级计算机的模拟中，突尼斯队以 23.2% 的微弱优势获胜，而平局的概率为 25.7%。"
            ]
        ]
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
        "prediction": "Ivory Coast are slight favourites, winning this match in 37.5% of the supercomputer’s 25,000 pre-match simulations, while Ecuador came out on top in 35.2% of sims. The chance of a draw sits at 27.3%.",
        "summary_cn": "Opta 超级计算机的预测清楚地表明了这些团队的匹配程度。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 科特迪瓦被认为是这场对阵厄瓜多尔的比赛中获胜的热门球队，在 Opta 超级计算机的 25,000 次模拟中，科特迪瓦的胜率高达 37.5%。\n· 厄瓜多尔队是南美洲预选赛中防守最强的球队，18场比赛仅丢5球。他们还输掉了最少的比赛（2场）。\n· 科特迪瓦在 2026 年 FIFA 世界杯预选赛（D2）的 10 场比赛中赢得了 8 场，并且是非洲足联区仅有的两支不失一球的球队之一。"
            ],
            [
                "深度分析",
                "据推测，科特迪瓦和厄瓜多尔将在 E 组争夺第二名，而德国队预计将在小组中横扫出线，其中还包括首次亮相的库拉索岛。但如果这样假设，就会对两支球队都造成极大的伤害。每个人都在预选赛中表现出色，这是有充分理由的——他们的球队实力雄厚。\n科特迪瓦拥有大量令人兴奋的进攻天才，如扬·迪奥曼德、阿马德·迪亚洛和巴祖马纳·图雷，而厄瓜多尔则拥有强大的防守资产，如威廉·帕乔、皮耶罗·辛卡皮埃和莫伊塞斯·凯塞多。\n乍一看似乎不太可能，但当这两个国家于美国东部时间 6 月 14 日 19:00（或英国 6 月 15 日午夜）在费城对峙时，这将标志着他们之间的首次会面。部分原因是这两个国家之前都没有在国际足联世界杯上给人留下深刻的印象，此前总共只参加过七次世界杯。\n考虑到科特迪瓦多年来培养出的优秀球员——迪迪埃·德罗巴以及科洛·图雷和亚亚·图雷兄弟——这可能是他们第四次参加世界杯，也是他们自 2014 年以来的第一次。他们从未在地面舞台上取得过进步。\n他们毫无困难地晋级 2026 年世界杯，在 10 场比赛中保持不败，并且保持了同样多的零失球。突尼斯是非洲足联中唯一一个在每场预选赛中都保持不失球的国家。\n他们的 25 个进球也是 CAF 地区晋级的国家中进球最多的，他们的 15 名独特进球者也是如此。西蒙·阿丁格拉（Simon Adingra）也许发挥了最大的作用，他贡献了全队最多的 5 粒进球，其中包括 2 粒进球和 3 次助攻。\n厄瓜多尔在预选赛中的表现可以说更令人印象深刻，因为他们必须通过南美足联部分，其中包含了严格的深度质量。\n他们在 18 场比赛中只输了两次——客场对阵阿根廷和巴西——同时只丢了 5 个球。这两项数据都是南美洲球队中最好的，而他们在世界杯卫冕冠军阿根廷队中获得第二名的成绩是他们与2002年共同取得的最好成绩。\n帕乔现在随巴黎圣日耳曼队连续获得欧洲冠军联赛冠军，值得巨大的赞誉。他是唯一一位在预选赛、开始和结束全部 18 场比赛期间为南美足联国家队踢满每一分钟的外场球员。\n与此同时，根据 Opta 的预期进球数 (xGOT) 模型，厄瓜多尔门将埃尔南·加林德斯在预选赛期间阻止了 3.8 个进球，是所有进入决赛的国家门将中最多的。\n厄瓜多尔在预选赛中只打进了 14 个进球，但往往是一个熟悉的名字在最后三分之一的比赛中提供了必要的火花。国家队队长恩纳·瓦伦西亚打进了这 14 个进球中的 8 个，并助攻了 2 个进球。\n自2024年9月客场0-1负于巴西以来，厄瓜多尔已连续19场比赛保持不败，并在世界杯热身赛对阵沙特阿拉伯和危地马拉的比赛中获胜。\n与此同时，科特迪瓦队在世界杯前的最后三场比赛中都取得了胜利，他们在 3 月份以不失一球的方式击败了韩国队和苏格兰队，随后又在 6 月 4 日客场击败法国队。\n显而易见的是，如果任何一方能够在比赛开始时就以一场决定性的胜利战胜对方，那么他们都有足够的实力对E组的德国队施加巨大压力。"
            ],
            [
                "历史交锋",
                "这将是科特迪瓦和厄瓜多尔之间的首次会议。\n科特迪瓦此前在世界杯上对阵南美洲球队的三场比赛全部落败：2006 年的阿根廷（1-2）、2010 年的巴西（1-3）和 2014 年的哥伦比亚（1-2）。\n与此同时，厄瓜多尔此前在世界杯上唯一一次对阵非洲对手的比赛也以失败告终，2022年以1-2负于塞内加尔。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机的预测清楚地表明了这些团队的匹配程度。\n科特迪瓦队稍显热门，在超级计算机的 25,000 次赛前模拟中，他们以 37.5% 的胜率赢得了这场比赛，而厄瓜多尔则以 35.2% 的模拟胜率名列前茅。平局的几率为 27.3%。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "橙衣军团被 Opta 超级计算机视为夺冠热门，这让他们有 49.0% 的获胜机会。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 的超级计算机认为荷兰队是这场比赛的热门球队，获胜概率为 49.0%，而日本队的获胜概率为 26.0%。\n· 橙衣军团在过去 16 场世界杯小组赛中保持不败（12 胜 4 平），这是目前最长的不败记录。\n· 日本队在过去两届世界杯上都取得了首场胜利。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "荷兰队希望在 2026 年世界杯上迎战日本队，保持开场比赛的骄人战绩。\n两国将于周日在阿灵顿的达拉斯体育场展开各自的 F 组比赛，这些球队是出线的有力热门。\n事实上，历史表明罗纳德·科曼的球队可以取得一个良好的开局，因为荷兰队在过去九场世界杯首场比赛中保持不败，赢得了七场比赛，其中赢得了两场比赛。\n橙衣军团上一次在世界杯首场比赛中被击败，要追溯到 1938 年，当时他们以 3-0 输给了捷克斯洛伐克。\n此外，荷兰队在世界杯小组赛中连续16场不败，12胜4平，这是目前最长的不败纪录。\n巧合的是，他们在泳池阶段的上一次失利是在美国，1994年，比利时队在佛罗里达州奥兰多以1-0战胜比利时队。当天，将执教库拉索岛的迪克·阿德沃卡特是他们的主教练。\n荷兰队在 2018 年未能晋级后，四年前进入了四分之一决赛，并将在这里第 12 次参加世界杯。他们曾三次闯入决赛。 1974年、1978年和2010年，没有任何一支球队能在多次获得亚军的情况下获得冠军。\n总体而言，荷兰队在世界杯上的胜率为 54.5%（55 场比赛中的 30 场）。 2026年世界杯开赛前，赛事历史上只有巴西（66.7%）和德国（60.7%）胜率更高。此外，他们距离世界杯上的百场进球仅差四个进球。\n这是科曼首次率领球队参加全球赛事，也是继 2024 年欧洲杯之后的第二次重大赛事。他曾于 1990 年和 1994 年两次以球员身份代表荷兰队参加世界杯。\n孟菲斯·德佩将再次希望成为焦点。这位前锋在预选赛中是国家队的最佳射手（八次）和并列最佳助攻者（四次）。\n四年前在卡塔尔击败德国和西班牙后，日本队希望这次能够在小组赛中再次取得胜利。\n武士蓝队在过去两届世界杯比赛中都取得了首场比赛的胜利，其中包括 2018 年以 2-1 战胜哥伦比亚队，以及四年前以同样的比分战胜德国队。\n然而，日本队从未进入过16强，并且保持着世界杯最多场次未进入四分之一决赛的纪录（25场）。\n这将是他们连续第八次参加世界杯，这是亚洲国家队连续参加世界杯第二长的记录，仅次于韩国队目前连续 11 次参加世界杯。\nHajime Moriyasu 的球队在亚足联预选赛中进球最多，在“for”统计中登记为 51 个进球（扣除三个进球，因为他们以 3-0 战胜朝鲜队）。\n除主办国外，日本队是第一支获得参赛资格的球队。他们在预选赛期间打入 10 粒以上进球的球员比任何其他亚冠球队都多——久保建房（12 粒进球，4 粒进球，8 次助攻）、伊藤纯也（11 粒进球，1 粒进球，10 次助攻）和上田绫濑（10 粒进球，8 粒进球，2 次助攻）。\n39岁的长友佑都仍然保持着强劲的体力，他也有可能创造历史，成为第一个参加五届世界杯的亚洲人。"
            ],
            [
                "历史交锋",
                "这场F组的交锋标志着两国队在世界杯上第二次相遇。\n第一次交锋是在2010年的小组赛中，韦斯利·斯内德攻入唯一进球，帮助球队1-0获胜。荷兰队随后进入决赛，但被西班牙队击败。\n两队总共交锋过 3 次，日本队尚未取得胜利（D1、L2）。\n然而，日本在上届世界杯​​上确实在对阵欧洲国家的常规时间内保持不败，小组赛中击败了德国和西班牙，随后在16强加时赛中1-1战平克罗地亚后，在点球大战中被克罗地亚淘汰出局。"
            ],
            [
                "赛前预测（Opta 超算）",
                "橙衣军团被 Opta 超级计算机视为夺冠热门，这让他们有 49.0% 的获胜机会。\n与此同时，日本队的获胜概率为 25.8%，平局概率为 25.3%。\n就整个比赛而言，荷兰队以 49.7% 的概率获得小组第一，同时强烈认为他们至少能进入淘汰赛阶段 (89.4%)。就他们赢得比赛的梦想而言，截至撰写本文时，他们的机会为 3.9%，在所有 48 支球队中排名第八。\n日本队获得F组第一的概率为25.1%，进入淘汰赛的概率为75.4%。他们举起奖杯的几率为1.3%。"
            ]
        ]
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
        "prediction": "Owing to the expanded 48-team competition, the Opta supercomputer’s pre-tournament predictions gave Curaçao a 19% chance of reaching the round of 32. Germany topped Group E , in which they also face Ecuador and Ivory Coast , in 59.9% of 25,000 simulations.",
        "summary_cn": "Opta 超级计算机只能看到德国队的胜利——他们在 10,000 次赛前模拟中取得了 90.7% 的胜利。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 在 Opta 超级计算机的赛前模拟中，库拉索岛队输给了德国队，预测准确率为 90.7%。\n· 德国队第 21 次参加世界杯，比任何其他欧洲国家都多，仅次于巴西队（23 次）。\n· 库拉索岛的迪克·阿德沃卡特将成为这项赛事历史上最年长的主教练。"
            ],
            [
                "深度分析",
                "库拉索岛队周日在休斯敦体育场对阵四届冠军德国队，他们将在世界杯首秀中遭遇历史性的失利。\n由于墨西哥、加拿大和美国作为共同主办国都被排除在中北美洲及加勒比海地区足球锦标赛的参赛资格之外，库拉索岛充分利用了这一优势，创造了历史，并成为获得世界杯参赛资格的面积和人口最小的国家。\n他们是自 2018 年巴拿马以来第一批首次亮相中北美洲及加勒比海地区足联的球队。然而，自 1990 年哥斯达黎加闯入 16 强以来，该联盟的任何一支球队在首次亮相时都未能逃脱小组赛阶段。\n由于比赛规模扩大到了 48 支球队，Opta 超级计算机的赛前预测显示库拉索岛晋级 32 强的几率为 19%。在 25,000 次模拟中，德国队以 59.9% 的胜率夺得 E 组冠军，他们还将在该组中迎战厄瓜多尔和科特迪瓦。\n迪克·艾德沃卡特仍然会觉得他的球队完全配得上这里的位置。库拉索岛在中北美洲及加勒比海地区预选赛中的进球数（28 个）和预期进球数（22.9 个）均领先，而他们的 4 个高失误进球仅落后于哥斯达黎加的 6 个进球。\n这些功绩的核心人物是儒尼尼奥·巴库纳 (Juninho Bacuna)，他在比赛中创造了最多的机会（20 次），并且在预选赛中赢得的任意球数（25 次）比任何其他球员都多。他将与他的兄弟莱安德罗·巴库纳一起在中场取得成功。\n肯吉·戈雷也是联盟预选赛中仅有的四名进球数超过 3 次、助攻数超过 3 的球员之一，也是唯一一位做到这一点的库拉索代表。\n库拉索岛主教练阿德沃卡特在比赛当天已经78岁零260天，他也将创造历史，成为世界杯上最年长的主教练。阿德沃卡特和德国选手朱利安·纳格尔斯曼（38岁326天）之间39岁零299天的年龄差距将是世界杯上两位主教练交锋的最大年龄差距。\n然而，纳格尔斯曼的年轻并没有剥夺德国的重要经验。他们是第 21 次参加世界杯，是欧洲国家中出场次数最多的国家，仅次于巴西（23 次）。\nDie Nationalelf 的四项世界冠军头衔在欧洲国家中只能与意大利相媲美，总体上比巴西（五项）还要好。\n尽管德国队在这一舞台上战绩辉煌，但在2018年和2022年均未能进入淘汰赛阶段。不过，自1950年无缘世界杯以来，他们在其他18场比赛中16场均已晋级首轮。\n但德国队在过去两届比赛中都输掉了首场比赛，分别是 2018 年对阵墨西哥和四年后对阵日本。他们上一次不失球要追溯到2014年决赛，当时他们在加时赛后凭借马里奥·格策的制胜球以1-0战胜了阿根廷队。\n纳格尔斯曼的球队也输掉了欧洲预选赛揭幕战对阵斯洛伐克的比赛，但他们继续赢得了接下来的五场比赛，并在 A 组中名列前茅。尼克·沃尔特马德是他们成功的关键——他在预选赛期间的进球数比任何其他德国球员都多，进球四次（射正次数相同）并送出一次助攻。\n在球场的另一端，曼努埃尔·诺伊尔可能成为继洛塔尔·马特乌斯之后第二位参加五届世界杯的德国人。诺伊尔也将成为继墨西哥的安东尼奥·卡巴哈尔之后第二位出现在五届赛事中的门将。\n如果德国队想要提高 Opta 超级计算机在开球前为德国队赢得世界杯 5.8% 的机会，这位拜仁慕尼黑门将的经验以及约书亚·基米希的智慧将至关重要。"
            ],
            [
                "历史交锋",
                "这两支球队之间没有交锋历史，因为这将是德国和库拉索岛之间的首次交锋。\n然而，德国在过去 17 场世界杯对阵美洲球队的比赛中赢了 14 场（平 1 平 2）。\n库拉索岛与欧洲球队的最后一场比赛——5月底对阵苏格兰的友谊赛——最终以 4-1 落败，尤尔根·洛卡迪亚被罚下场。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机只能看到德国队的胜利——他们在 10,000 次赛前模拟中取得了 90.7% 的胜利。\n库拉索岛首次亮相就取得一场不太可能的胜利的可能性只有 3.6%。"
            ]
        ]
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
        "prediction": "Following 10,000 pre-match simulations, the Opta supercomputer predicts success for the United States, with a 39.6% chance of victory. Paraguay prevailed in 33.8% of those simulations, leaving a draw rated at 26.6%.",
        "summary_cn": "巴拉圭在模拟比赛中获胜率为 33.8%，平局率为 26.6%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预测联合主办方获胜，美国队获胜的几率为 39.6%。\n· 巴拉圭队的获胜概率为 33.8%，他们不希望逆转之前世界杯比赛的结果——美国队 3-0 获胜。\n· 那次遭遇发生在 1930 年首届决赛中，伯特·帕特诺德 (Bert Patenaude) 上演了世界杯首个帽子戏法，至今仍是美国队在本届世界杯上取得的最大胜利。"
            ],
            [
                "深度分析",
                "为了抓住早期的势头，D组的对手巴拉圭和美国队将于周六在洛杉矶相遇。\n这是三个国家首次共同主办世界杯，美国与邻国墨西哥和加拿大一起希望获得令人自豪的主场支持。\n根据 Opta 超级计算机的数据，星条旗队真正举起奖杯的机会只有 1.1%，但这并不意味着他们不能梦想。\n首先，毛里西奥·波切蒂诺的球队必须谈判一个棘手的小组，其中还有对阵澳大利亚（6月19日，西雅图）和土耳其（6月25日，洛杉矶）的比赛。\n这场盛大演出开始前的最后一场调整以美国队的失败告终，上周，尽管安东尼·罗宾逊凭借雷霆般的扳平比分，美国队还是在芝加哥以 2-1 的比分被德国队击败。\n至此，波切蒂诺领导下近两年的规划、调整和测试完成，他的26人阵容飞往加利福尼亚。这将是这位前托特纳姆热刺主帅首次作为教练参加世界杯，深入推进的压力是巨大的。\n美国队迄今为止最好的成绩是在 1930 年，当时他们击败巴拉圭获得铜牌——这仍然是中北美洲及加勒比地区足球协会国家队唯一一次进入前四名。在现代，他们最远的纪录是2002年打进四分之一决赛。\n现在，他们将第二次作为东道主，渴望超越 32 年前在主场闯入 16 强的表现。\n这或许并非异想天开：美国队在最近三场比赛（2010年、2014年、2022年）中都进入了淘汰赛阶段，而且他们在过去九场小组赛中只输了一场（3胜5平）。他们也在美国西海岸参加每场 D 组比赛，尽管他们之前在洛杉矶体育场输掉了两场比赛。\n虽然东道主不必晋级，但巴拉圭在南美洲获得第六名，获得了最后的自动席位。\n他们更倾向于谨慎行事，在晋级球队中净胜球（+4）和平均控球率（37.3%）最低；他们的定位球进球比例也最高（36%）。\n这为他们第九次参加世界杯做好了准备，但这也是自 2010 年以来的第一次，当时 La Albirroja 打进了四分之一决赛，这是他们有史以来最好的成绩。\n他们由古斯塔沃·阿尔法罗带领，他与波切蒂诺一起是今年世界杯的六名阿根廷教练之一，也是第三位带领巴拉圭队参加世界杯的教练之一。\n阿尔法罗的精彩表现是2-1战胜阿根廷队；然而，他的球队随后在去年11月的一场友谊赛中被美国队以2-1击败。\n在更严峻的情况下面对星条旗队之前，巴拉圭在主场4-0战胜尼加拉瓜进行了热身——这并不是赛前最考验对手的球队。\n巴拉圭可能只赢得了八场世界杯揭幕战中的一场（平四平三），但美国队的胜率在超过 30 场比赛的国家中排名第二低（24%）。\n改善这一纪录的希望主要寄托在克里斯蒂安·普利西奇身上，他在米兰度过了艰难的一年，但参与了2022年卡塔尔世界杯美国队的全部三个进球，并且在对阵德国队的比赛中表现出色。\n安东尼奥·萨纳布里亚 (Antonio Sanabria) 是巴拉圭进入决赛的最佳射手，打入 4 个进球，但作为南美区预选赛中最多产的替补球员（打入 3 个进球），他从替补席上首发可能会更好。"
            ],
            [
                "历史交锋",
                "这将是第二次世界杯相遇，1930 年美国队以 3-0 获胜。\n仅有的其他正式比赛是美洲杯：2007 年巴拉圭 3-1 获胜，九年后美国队 1-0 获胜。\n在本世纪的友谊赛中——包括去年 11 月美国队主场获胜——美国队以 3-1 领先。"
            ],
            [
                "赛前预测（Opta 超算）",
                "巴拉圭在模拟比赛中获胜率为 33.8%，平局率为 26.6%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer could not look past a victory for Canada, who came out on top in 52.7% of the 10,000 pre-match simulations. Bosnia-Herzegovina triumphed in just 22.0% of the supercomputer’s simulations, with a draw accounting for the remaining 25.3%.",
        "summary_cn": "Opta 超级计算机不容忽视加拿大队的胜利，在 10,000 次赛前模拟中，加拿大队以 52.7% 的胜率名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机在开球前支持加拿大队获胜，在赛前模拟中，联合主办方以 52.7% 的优势获胜。\n· 加拿大队在此前六场比赛全部失利后，仍在寻求在男子世界杯比赛中的首场胜利。\n· 周五的 B 组揭幕战将是加拿大和波斯尼亚和黑塞哥维那之间的首次交锋。\n· 国家 国家 美利坚合众国 大不列颠及北爱尔兰联合王国 阿富汗 奥兰群岛 阿尔巴尼亚 阿尔及利亚 美属萨摩亚 安道尔 安哥拉 安圭拉 安提瓜和巴布达 阿根廷 亚美尼亚 阿鲁巴 澳大利亚 奥地利 阿塞拜疆 巴哈马 巴林 孟加拉国 巴巴多斯 白俄罗斯 比利时 伯利兹 贝宁 百慕大 不丹 玻利维亚多民族国 波斯尼亚和黑塞哥维那 博茨瓦纳 布维岛 巴西 英属印度洋领地 美利坚合众国离岛 维尔京群岛（英国） 维尔京群岛（美国） 文莱达鲁萨兰国 保加利亚 布基纳法索 布隆迪 柬埔寨 喀麦隆 加拿大 佛得角 开曼群岛 中非共和国 乍得 智利 中国 圣诞岛 科科斯（基林）群岛 哥伦比亚 科摩罗 刚果 刚果（民主共和国） 库克群岛 哥斯达黎加 克罗地亚 古巴 库拉索岛 塞浦路斯 捷克共和国 丹麦 吉布提 多米尼克 多米尼加共和国 厄瓜多尔 埃及 萨尔瓦多赤道几内亚 厄立特里亚 爱沙尼亚 埃塞俄比亚 福克兰群岛（马尔维纳斯群岛） 斐济 芬兰 法国 法属圭亚那 法属波利尼西亚 法属南部领土 加蓬 冈比亚 格鲁吉亚 德国 加纳 直布罗陀 希腊 格陵兰岛 格林纳达 瓜德罗普岛 关岛 危地马拉 根西岛 几内亚比绍 圭亚那 海地 赫德岛和麦克唐纳群岛 罗马教廷 洪都拉斯 香港 匈牙利 冰岛 印度 印度尼西亚 伊朗伊斯兰共和国 伊拉克 爱尔兰 马恩岛 以色列 意大利象牙海岸 牙买加 日本 泽西岛 约旦 哈萨克斯坦 肯尼亚 基里巴斯 科威特 吉尔吉斯斯坦 老挝人民民主共和国 拉脱维亚 黎巴嫩 莱索托 利比里亚 利比亚 列支敦士登 立陶宛 卢森堡 澳门 马其顿(前南斯拉夫共和国) 马达加斯加 马拉维 马来西亚 马尔代夫 马里 马耳他 马绍尔群岛 马提尼克岛 毛里塔尼亚 毛里求斯 马约特岛 墨西哥 密克罗尼西亚联邦 摩尔多瓦共和国摩纳哥 蒙古 黑山 蒙特塞拉特 摩洛哥 莫桑比克 缅甸 纳米比亚 瑙鲁 尼泊尔 荷兰 新喀里多尼亚 新西兰 尼加拉瓜 尼日尔 尼日利亚 纽埃 诺福克岛 朝鲜民主主义人民共和国 北马里亚纳群岛 挪威 阿曼 巴基斯坦 帕劳 巴勒斯坦、巴拿马国 巴布亚新几内亚 巴拉圭 秘鲁 菲律宾 皮特凯恩 波兰 葡萄牙 波多黎各 卡塔尔 科索沃 留尼汪岛 罗马尼亚 俄罗斯 卢旺达 圣巴泰勒米 圣圣基茨和尼维斯 圣卢西亚 圣马丁岛（法属部分） 圣皮埃尔和密克隆群岛 圣文森特和格林纳丁斯 萨摩亚 圣马力诺 圣多美和普林西比 沙特阿拉伯 塞内加尔 塞尔维亚 塞舌尔 塞拉利昂 新加坡 圣马丁岛（荷属部分） 斯洛伐克 斯洛文尼亚 所罗门群岛 索马里 南非 南乔治亚岛和南桑威奇群岛 韩国 南苏丹西班牙 斯里兰卡 苏丹 斯瓦尔巴群岛和扬马延群岛 斯威士兰 瑞典 瑞士 阿拉伯叙利亚共和国 台湾 塔吉克斯坦 坦桑尼亚 泰国联合共和国 东帝汶 多哥 托克劳群岛 汤加 特立尼达和多巴哥 突尼斯 土耳其 土库曼斯坦 特克斯和凯科斯群岛 图瓦卢 乌干达 乌克兰 阿拉伯联合酋长国 大不列颠及北爱尔兰联合王国 美利坚合众国 乌拉圭 乌兹别克斯坦 瓦努阿图 梵蒂冈城 委内瑞拉玻利瓦尔共和国越南 瓦利斯和富图纳群岛 西撒哈拉 也门 赞比亚 津巴布韦"
            ],
            [
                "深度分析",
                "加拿大举行的第一场男子世界杯比赛将于周五在多伦多体育场主场迎战波斯尼亚和黑塞哥维那，这将是两队的首次交锋。\n共同主办国加拿大队与美国队和墨西哥队一起自动获得参加今年夏天世界杯的资格，这是他们继 1986 年和 2022 年之后第三次参加世界杯，也是他们第一次连续参加世界杯。\n杰西·马什 (Jesse Marsch) 的球队现在承担了共同主办方的职责，希望给人留下与他们之前在世界舞台上表现截然不同的印象。\n加拿大在之前的六场世界杯比赛中全部输掉，只进了两次球（其中一次是乌龙球），同时失球 12 次，只有萨尔瓦多追平这一纪录（六场失利）。\n然而，与之前的表现不同的是，人们对红红军团的期望要高得多，马什的球队在过去八场比赛中保持不败，并且在 2026 年尚未遭遇失败。\n事实上，在这八场比赛中，他们有六场不失球，突显出新发现的防守稳定性，考虑到世界杯足球的动态性质，这种防守可能是无价的。\n马什也可能对在多伦多的强势开局充满信心，加拿大在过去 28 场比赛中仅输掉了一场（18 胜 9 平）——2023 年 11 月以 3-2 输给牙买加。\n不过，这远非一帆风顺，因为他们面对的是一支坚韧的波斯尼亚和黑塞哥维那球队，他们在资格赛中经历了一场戏剧性但鼓舞人心的比赛，在附加赛中通过点球淘汰了威尔士和意大利。\n总的来说，谢尔盖·巴巴雷斯的球队在 ​​10 场预选赛中每场都有进球，并且只输过一场——主场 2-1 负于奥地利。\n今年的比赛是波黑队继 2014 年在巴西首次亮相后第二次参加世界杯。当时他们在小组赛中被淘汰（胜 1 负 2），尽管他们以 3-1 战胜伊朗队结束了本赛季的比赛。\nOpta 超级计算机将巴巴雷斯的球队列为 B 组第三有可能晋级的球队，仅次于瑞士队（91.0%）和周五的对手加拿大队（82.0%），他们的晋级机会为 60.3%。\n尽管如此，B组的其他球队最好不要低估波黑，他们在预选赛小组赛中以24分的成绩拿到了令人印象深刻的17分。\n他们在 40 岁的埃丁·哲科 (Edin Dzeko) 的带领下表现出色，他在 9 场比赛中攻入 6 个进球，为球队带来了宝贵的世界杯经验，他参加了 2014 年的全部三场比赛，在对阵伊朗的比赛中攻入一球。\n与此同时，加拿大队也有自己强大的进球威胁，也许没有比乔纳森·大卫（Jonathan David）更多产的了。这位尤文图斯前锋直接参与了加拿大队在过去两场大型赛事中超过三分之一的进球，在 2024 年美洲杯和 2025 年中北美洲及加勒比海金杯赛上打进 4 粒进球并送出 1 次助攻。\n这也将是马什作为加拿大主教练首次参加世界杯，也是他执教的第三场大型赛事，此前他在 2024 年美洲杯上获得第四名，并在 2025 年金杯赛上四分之一决赛负于危地马拉。\n红队在周五 B 组揭幕战之前热身得很好，在友谊赛中以 2-0 击败乌兹别克斯坦队并以 1-1 战平爱尔兰共和国。相反，波黑1-1战平巴拿马。"
            ],
            [
                "历史交锋",
                "这场比赛标志着这两个国家首次交锋，这对双方来说都是在最大舞台上的历史性时刻。\n然而，这将是加拿大队在世界杯上与欧洲足联球队的第六场比赛，这是加拿大队在世界杯上总共进行的七场比赛中的第六场。\n与此同时，波斯尼亚和黑塞哥维那将有望取得自 2014 年友谊赛 1-0 战胜墨西哥以来首次战胜中北美洲及加勒比海地区对手。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机不容忽视加拿大队的胜利，在 10,000 次赛前模拟中，加拿大队以 52.7% 的胜率名列前茅。\n波黑在超级计算机的模拟中仅获胜 22.0%，其余 25.3% 为平局。"
            ]
        ]
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
        "prediction": "The Opta supercomputer sees Scotland as the overwhelming favourites to win their opener, with 59.0% of the 25,000 pre-match simulations ending in victory for the Tartan Army. Haiti’s chances of winning stand at a not-insurmountable 19.2%, although that’s the least likely result of the pre-match predictions, with a 21.8% likelihood of the game ending level.",
        "summary_cn": "Opta 超级计算机认为苏格兰是赢得揭幕战的压倒性热门，在 25,000 次赛前模拟中，有 59.0% 的结果是格子呢军团获胜。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机预计苏格兰将在 1998 年以来的首场世界杯比赛中取得胜利，史蒂夫·克拉克 (Steve Clarke) 的球队在赛前模拟中击败海地的胜率高达 59.0%。\n· 海地在 1974 年 FIFA 世界杯的三场小组赛中丢了 14 个球，这是本届世界杯现阶段丢球第二多的球队，仅次于韩国在 1954 年世界杯上丢了 16 个球。\n· 苏格兰在世界杯的最后三场揭幕战中均告失利，上一次在世界杯揭幕战中取得胜利还要追溯到 1982 年，当时苏格兰在西班牙马拉加的罗萨德拉球场以 5-2 击败新西兰。"
            ],
            [
                "深度分析",
                "马萨诸塞州福克斯伯勒的波士顿体育场将举办一场本世纪国际足联世界杯上从未有过的两国队之间的比赛，海地和苏格兰将在 C 组揭幕战中对决。\n时隔 52 年，海地队在 1974 年唯一一次参加赛事，在中北美洲及加勒比海地区资格赛小组中名列前茅后，又回到了最大的舞台。\n海地缺席世界杯的 52 年时间是世界杯历史上并列第四长的，仅次于威尔士（1958 年至 2022 年 64 年）、埃及（1934 年至 1990 年 56 年）和挪威（1938 年至 1994 年 56 年）。\n海地在中北美洲及加勒比海地区预选赛C组中击败了尼古拉瓜、世界杯常客哥斯达黎加和洪都拉斯，尽管去年10月在特古西加尔巴以3-0失利，但仍领先后者两分。\n前锋杜肯斯·纳松 (Duckens Nazon) 为海地队打进 6 粒进球，为中北美洲及加勒比海地区预选赛进球数并列最多，其中包括在对阵哥斯达黎加的比赛中替补上场后上演帽子戏法。\n纳松在中北美洲及加勒比海地区预选赛中的射门次数（34次）和在对方禁区内的触球次数（59次）也比任何其他球员都多，而且海地队的前线自从获得参赛资格以来得到了进一步的加强。\n威尔逊·伊西多从法国转会成功，自三月份首次征召入伍以来，桑德兰前锋为掷弹兵队出场四次，打进两球。\n伊西多尔的两次进球分别发生在3月和6月1-1战平冰岛和2-1负于秘鲁的比赛中，以及海地在佛罗里达州劳德代尔堡4-0战胜新西兰的比赛中。\n尽管五天后以四球战胜新西兰队，但最终又被备受瞩目的英格兰队以 1-0 击败，但在海地最近的比赛中，攻防两端的进球总体上都是飞进的。\n在参加中北美洲及加勒比海地区预选赛的 10 场比赛中，只有百慕大（31 个）和尼加拉瓜（16 个）比海地的 13 个进球多，而塞巴斯蒂安·米涅的球队的预期失球数也位居第三（11.7 个）。\n然而，海地将受到苏格兰在过去九次世界杯与美洲球队（L7）交锋中未尝胜绩的事实的鼓舞。这其中包括他们之前唯一一次与中北美洲及加勒比海地区对手的交锋——1990年0-1负于哥斯达黎加。\n格子军团自 1998 年以来首次亮相世界杯，结束了自 1982 年以来首次在欧洲联盟世界杯预选赛小组第一名后阔别 28 年的局面。\n苏格兰希望能够比之前的重大国际赛事中表现更好。他们曾参加过 12 场不同的世界杯或欧洲锦标赛决赛，但在这 12 场比赛中，他们都未能小组赛阶段出线。\n这无疑是一项历史记录，只有伊朗和突尼斯（均为六支球队）参加过三次以上的小组赛，但没有与苏格兰队一起晋级。在欧洲国家中，只有阿尔巴尼亚曾多次参加过小组赛，但从未进入过淘汰赛（两次）。\n史蒂夫·克拉克 (Steve Clarke) 现在带领苏格兰队获得了过去四场主要赛事中三场的参赛资格（2020 年欧洲杯、2024 年欧洲杯和本届世界杯），比国家队 154 年历史上的任何其他主教练都多。\n苏格兰队在汉普顿公园球场的最后一场比赛中以 4-2 的比分击败丹麦队，在欧足联预选赛 C 组中获得头名，基兰·蒂尔尼和肯尼·麦克莱恩在补时阶段的进球锁定胜局。\n在参加本届世界杯的所有获得欧足联资格的球队中，苏格兰的净胜球确实是第二低（+6；进球 13 球，失球 7 球），仅次于瑞典，并且预期进球差第二低（+0.8）。\n然而，克拉克的球队在世界杯之前重新找回了他们的射门靴，在两场热身赛中分别以 4-1 和 4-0 击败了库拉索岛和玻利维亚队。\n劳伦斯·尚克兰和切·亚当斯在这些友谊赛中各进两球，那不勒斯中场球员斯科特·麦克托米奈也在新泽西对阵玻利维亚的上半场四球闪电战中取得进球。\n自 2023 年初以来，麦克托米奈已为苏格兰在正式比赛中攻入 13 个进球，比其他任何人至少多出 8 个进球。\n麦克托米奈在本届世界杯预选赛中参与的进球数比任何其他苏格兰球员都多（两粒进球，一次助攻），并且是在全部六场比赛中首发的三名球员之一，其他球员包括约翰·麦金和队长安迪·罗伯逊。"
            ],
            [
                "历史交锋",
                "扩大后的世界杯共有 48 支球队参加，其中包括四场首次预选赛以及多项国家间首次相遇的比赛，本次 C 组比赛将是后者之一。\n海地和苏格兰从未在正式比赛或友谊赛中相遇，这是加勒比球队首次对阵不列颠群岛球队。\n苏格兰此前唯一与中北美洲及加勒比海地区国家的交锋是对阵哥斯达黎加、特立尼达和多巴哥以及库拉索岛，上个月在汉普顿公园举行的赛前友谊赛中以 4-1 击败后者。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机认为苏格兰是赢得揭幕战的压倒性热门，在 25,000 次赛前模拟中，有 59.0% 的结果是格子呢军团获胜。\n海地队获胜的可能性为 19.2%，但这是赛前预测中可能性最小的结果，比赛结束的可能性为 21.8%。"
            ]
        ]
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
        "prediction": "The Opta supercomputer favours a Türkiye victory, with Montella’s side having won 55.3% of the 10,000 pre-match simulations. Australia’s chances of winning are rated at 20.5%, with a draw at 24.1%.",
        "summary_cn": "Opta 超级计算机支持土耳其获胜，蒙特拉的球队在 ​​10,000 次赛前模拟中获胜率为 55.3%。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 土耳其队在世界杯对阵亚足联球队的四场比赛中全部获胜，并且是 Opta 超级计算机最有希望获胜的球队（55.3%）。\n· 澳大利亚在过去五届世界杯上输掉的比赛比任何其他国家都多（17 场中有 10 场）。\n· 澳大利亚队在六场世界杯比赛中也有五场输掉了首场比赛。"
            ],
            [
                "深度分析",
                "土耳其队希望在温哥华举行的 D 组比赛中击败澳大利亚队，重返世界杯决赛圈。\n尽管土耳其人在过去八场欧洲锦标赛中获得了六场资格，但距土耳其上次登上全球舞台还不到四分之一世纪。\n那是在2002年，当时乌米特·达瓦拉、哈桑·萨斯和伊尔汗·曼西兹等人在日本和韩国的锦标赛上大放异彩，帮助他们的国家队进入了半决赛。\nŞenol Günes 的球队最终获得铜牌，哈坎·苏克 (Hakan Şükür) 的进球仅 11 秒就击败了韩国队，这仍然是世界杯历史上最快的进球。\n文森佐·蒙特拉是意大利队在 16 强赛中被东道主队击败的一员。24 年过去了，这位前前锋是继古内斯之后第二位带领土耳其队参加欧洲杯和世界杯的教练。\n在预选赛中，蒙特拉的球队落后于欧洲冠军西班牙队，获得第二名，随后在附加赛中以 1-0 击败罗马尼亚和科索沃，第三次晋级决赛。\n土耳其队主要由哈坎·恰尔汗奥卢和阿尔达·居勒领衔，他们各有四次助攻，在预选赛中总共贡献了国家队 42% 的进球（19 粒进球中的 8 粒）。\n凯南·耶尔迪兹也以并列领先的三个进球给人留下了深刻的印象，尽管这位尤文图斯边锋在意甲赛季最后阶段小腿受伤后正在努力恢复健康。\n尽管土耳其队并没有丰富的世界杯经验，但他们确实拥有丰富的血统。西德队和巴西队是仅有的在决赛中击败他们的球队，并在 1954 年和 2002 年分别赢得了各自的锦标赛冠军。\n同样，澳大利亚在之前的六次参赛中，有四次面对最终的获胜者——1974年的西德、2006年的意大利、2018年的法国，以及最近的2022年的阿根廷——每次都输了。\n澳大利亚队确实追平了他们上次在决赛中的最佳表现，进入了 16 强，同时还首次在单一赛事中取得了多项胜利（两次）。\n主教练托尼·波波维奇是2006年在古斯·希丁克的带领下进入第二轮的另一支澳大利亚队的一员，他们在小组中排名第二，落后于巴西，然后在对阵意大利的比赛中被弗朗西斯科·托蒂的点球击败。\n自当年世界杯开赛以来，澳大利亚队在 17 场世界杯比赛中遭遇 10 场失利，是所有国家中失利最多的国家，而且自 2014 年以来，长期排名第一的马修·瑞安 (Mathew Ryan) 在决赛中的失球次数比任何门将都多 (20 个)。\n然而，澳大利亚队这次不会那么容易翻身，波波维奇接替了在亚冠资格赛第三轮开局不佳后离开的格雷厄姆·阿诺德，这无疑稳定了球队的局势。\n这位前后卫在 C 组中连续 8 场不败，自 2014 年以来首次获得自动晋级资格。在亚冠赛区，只有日本（54 个）和韩国（40 个）的进球多于澳大利亚（38 个），尽管其中只有 16 个是在第三轮比赛中打进的，其中仅在击败印度尼西亚的比赛中就打进了 5 个进球。\n这是波波维奇希望他的球员在温哥华上场时能够解决的问题。\n他可能会向老将马修·莱基寻求灵感，他是澳大利亚过去 10 场世界杯比赛中的首发球员。这位35岁的墨尔本城前锋可能成为继蒂姆·卡希尔（Tim Cahill，2006年、2010年和2014年）和迈尔·耶迪纳克（Mile Jedinak，2014年和2018年）之后第三位在两次不同决赛中为澳大利亚队进球的球员。\n定位球很可能在这场比赛中发挥关键作用。在欧足联预选赛中，只有捷克队（7个）角球进球数多于土耳其队（5个），而澳大利亚队的角球和间接任意球进球数为8个，在亚冠赛区仅落后于卡塔尔队（11个）。"
            ],
            [
                "历史交锋",
                "这只是两国之间的第三次会议，土耳其在前两次会议中获胜。\n两人于 2004 年 5 月复出，当时新月星队在悉尼以 3-1 获胜，三天后在墨尔本以 1-0 险胜。\n土耳其队在此前四场世界杯对阵亚足联球队的比赛中全部获胜，打进 14 球，仅丢 2 球。其中包括 7-0 击败韩国队，这是他们在 1954 年决赛中的首场胜利。\n48 年后，在三四名附加赛中，同一支球队在 3-2 战胜他们的比赛中攻入两球。"
            ],
            [
                "赛前预测（Opta 超算）",
                "Opta 超级计算机支持土耳其获胜，蒙特拉的球队在 ​​10,000 次赛前模拟中获胜率为 55.3%。\n澳大利亚获胜的几率为20.5%，平局的几率为24.1%。\n然而，在决赛中，双方都没有取得令人鼓舞的战绩。\n土耳其在此前的世界杯首场比赛中均遭遇失利，分别是1954年1-4负于西德、2002年1-2负于巴西。\n与此同时，澳大利亚在此前的六场比赛中，有五场都输掉了首场比赛，除了2006年3-1战胜克罗地亚的比赛。"
            ]
        ]
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
        "prediction": "Across 25,000 pre-match simulations of this Group B clash, Switzerland came out on top 76.0% of the time, suggesting they are highly likely to pick up an early three points. Qatar’s chances of victory stand at just 9.1% by comparison, and with 14.9% of the simulations ending level, Julen Lopetegui’s side would likely be more than happy with a solitary point from this game.",
        "summary_cn": "尽管卡塔尔和瑞士在今年夏天的世界杯预选赛中都表现不佳，但根据 Opta 超级计算机的数据，他们有一个轻松的方式赢得世界杯揭幕战。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机认为瑞士是世界杯开局的热门球队，赛前模拟胜率高达 76.0%，而卡塔尔的胜率仅为 9.1%。\n· 这只是卡塔尔第二次参加 FIFA 世界杯，尽管这是他们自 2022 年主办世界杯后首次获得世界杯参赛资格。\n· 瑞士是仅有的两支在过去六场主要国际赛事（世界杯/欧洲杯）中都进入淘汰赛阶段的欧洲球队之一，另外两支球队是法国队。"
            ],
            [
                "深度分析",
                "2026 年世界杯，卡塔尔和瑞士与波斯尼亚和黑塞哥维那分在 B 组，东道主加拿大队将在加利福尼亚州圣克拉拉的旧金山湾区体育场展开比赛。\n卡塔尔首次作为预选赛参加世界杯，并主办了上一届世界杯，四年前在小组垫底后，卡塔尔希望这次能改变命运。\n卡塔尔队在 2022 年输掉了全部三场比赛，丢了 7 个球，只进了 1 个球，但朱伦·洛佩特吉的球队很快就进入了 2026 年世界杯预选赛的最后一个小组，击败了阿拉伯联合酋长国，夺得了榜首。\n在前两轮预选赛和总共 16 场比赛中，卡塔尔队由 Al-Duhail 前锋阿尔莫埃兹·阿里领衔，他的 12 个进球超过了 2026 年亚冠预选赛中任何其他球员的进球数。\n在各个大陆预选赛小组中，只有挪威的埃尔林·哈兰德（总共 16 个进球）比阿里的进球数多，而阿克拉姆·阿菲夫在卡塔尔队的助攻榜上位居榜首，他在 16 场比赛中贡献了 11 次助攻。\n阿尔萨德的组织核心有 6 个进球来自定位球，只有伊朗队的迈赫迪·塔雷米（Mehdi Taremi）（17 粒进球）比阿菲夫的 15 粒进球更多，共贡献 4 个进球和 11 次助攻。\n在参加今年夏天世界杯的亚足联国家中，卡塔尔输掉的比赛最多（5场），而在亚冠预选赛至少打了10场比赛的球队中，卡塔尔的场均进球数最多，平均为3.61个。\n然而，这些进球在 2026 年已经枯竭，卡塔尔在所有比赛的最后 373 分钟比赛中都未能取得进球，最后一次进球是在 2025 年 12 月阿拉伯杯对阵叙利亚的比赛中。\n这场比赛包括在世界杯前的两场友谊赛中以 1-0 输给爱尔兰共和国，以及与萨尔瓦多互交白卷，此前计划对阵塞尔维亚、阿根廷和苏丹的三场比赛均被取消。\n相比之下，卡塔尔队面对的是状态火热的瑞士队，穆拉特·亚金的球队在欧足联预选赛B组中名列前茅，在六场比赛中赢了四场，并且在此过程中保持不败。除了英格兰之外，瑞士队是欧足联预选赛中仅有的两支在任何一场比赛中从未落后的球队之一。\n瑞士队唯一失分是在客场战平斯洛文尼亚和科索沃的比赛中，并且还有B组的头号射手雷恩前锋布雷尔·恩博洛。\n恩博洛在最近的赛事中引起了轰动，他是仅有的五名在 2022 年世界杯和 2024 年欧洲杯上打进多个进球的球员之一，其他球员还有哈里·凯恩、凯·哈弗茨、尼克拉斯·菲尔克鲁格和科迪·加克波。\n自 1966 年以 5-0 输给西德队以来，瑞士队在最近六场世界杯揭幕战中保持不败。他们有信心在对阵目前国际足联世界排名第 56 位的卡塔尔队的比赛中连续七场不败，比自己（第 19 位）低 37 位。\n尽管瑞士队第 13 次获得世界杯参赛资格，并且在 2026 年连续第六次获得参赛资格，但瑞士队之前只在一次世界杯上以小组第一的身份夺冠，那就是 2006 年，当时他们在四场比赛中没有丢一球。\n瑞士在 2025 年的强势表现之后，2026 年的开局却步履蹒跚，然而，瑞士在 3 月份以 4-3 输给了德国，又与挪威和澳大利亚战平，上个月又以 4-1 战胜了约旦。\n丹·恩多耶在其中三场比赛中进球——包括在圣地亚哥对阵澳大利亚的揭幕战——诺丁汉森林边锋恩博洛以及年轻男孩队的二人组乔尔·蒙泰罗和克里斯蒂安·法斯纳赫特为雅金提供了大量的进攻选择。"
            ],
            [
                "历史交锋",
                "这两个国家在各自的历史上只曾交锋过一次，那次交锋是在 2018 年 11 月的一场友谊赛中，当时卡塔尔在瑞士卢加诺的科尔纳雷多球场以 1-0 击败东道主。\n阿克拉姆·阿菲夫在第 86 分钟的进球证明了比赛的不同，这位现年 29 岁的前锋是胜利的卡塔尔队入选洛佩特吉 2026 年世界杯阵容的 9 名球员之一。\n与此同时，瑞士队在参加今年世界杯的 26 名球员阵容中，有 7 名从 2018 年失利中幸存下来的球队，其中包括队长格拉尼特·扎卡 (Granit Xhaka) 和雷莫·弗洛伊勒 (Remo Freuler)。"
            ],
            [
                "赛前预测（Opta 超算）",
                "尽管卡塔尔和瑞士在今年夏天的世界杯预选赛中都表现不佳，但根据 Opta 超级计算机的数据，他们有一个轻松的方式赢得世界杯揭幕战。\n在这场 B 组比赛的 25,000 次赛前模拟中，瑞士队以 76.0% 的胜率名列前茅，这表明他们很有可能早早拿下三分。\n相比之下，卡塔尔队的获胜几率仅为 9.1%，而模拟结束水平为 14.9%，朱伦·洛佩特吉的球队可能会对这场比赛中的唯一一分感到非常高兴。"
            ]
        ]
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
        "prediction": "Brazil have the upper hand in this Group C curtain-raiser, having come out on top in 57.7% of the Opta supercomputer ‘s 25,000 pre-match simulations.",
        "summary_cn": "巴西队在这场 C 组揭幕战中占据上风，在 Opta 超级计算机的 25,000 次赛前模拟中，巴西队以 57.7% 的成绩名列前茅。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· 根据 Opta 超级计算机的数据，巴西队在世界杯对阵摩洛哥的比赛中有 58.6% 的机会取得胜利。\n· 这是小组赛阶段唯一一场有两支球队进入 FIFA 世界排名前 10 名的比赛（巴西第 6 位，摩洛哥第 8 位）。\n· 安切洛蒂力争成为继马塞洛·里皮和博斯克之后第三位赢得世界杯和欧洲冠军联赛/欧洲杯冠军的教练。"
            ],
            [
                "深度分析",
                "巴西队将于周六在纽约新泽西体育场举行的 C 组揭幕战中迎战摩洛哥，开始他们对第六个世界杯冠军的追求。\n没有哪个国家像巴西那样与世界杯有着如此密切的关系。他们是自 1930 年比赛创办以来唯一一个参加过每一届比赛的国家，并且他们的五次胜利是所有国家中获胜次数最多的。\n然而，他们上一次成功是在2002年，这是他们连续最长的一次未能捧起奖杯的记录。在北美的失败将使这个热爱足球的国家需要认真思考如何前进。\n四年前，他们在四分之一决赛中被克罗地亚队淘汰，拉菲尼亚以射门次数最多但未进球的球员（6次）结束了世界杯。\n不过，攻击者这次准备以更积极的方式留下自己的印记。他在 2026 年预选赛中参与的进球数比任何其他巴西球员都多（5 粒进球和 2 次助攻），并在 2025-26 赛季为西甲冠军巴塞罗那队出场 33 场比赛，贡献 21 粒进球和 7 次助攻。\n尽管热身赛中巴西队以6-2击败巴拿马队、2-1击败埃及队，但巴西队在预选赛上的表现还差得远。他们的第五名成绩是自该赛制 30 年前推出以来最差的成绩。\n现在，他们的教练席上拥有了赛事中获得最多荣誉的教练之一，那就是卡洛·安切洛蒂，他带领球队冲过终点线，并将在他的职业生涯中首次执教世界杯。\n安切洛蒂希望帮助巴西保持自1982年以来每届世界杯首轮小组第一的记录。如果他们在比赛开始时击败摩洛哥，那么他们的机会将大大增加，而苏格兰和海地在纸面上的威胁较小。\n然而，随着摩洛哥这个正在崛起的国家，这绝不是理所当然的。四年前，他们在卡塔尔打进了半决赛，并且是唯一一支赢得 2026 年世界杯预选赛全部八场比赛的非洲球队。当然，他们在与塞内加尔的一场有争议的决赛后也获得了2025年非洲国家杯冠军。\n因此，阿特拉斯雄狮队在某些方面被视为黑马也就不足为奇了，阿什拉夫·哈基米、布拉希姆·迪亚兹和阿尤布·埃尔·卡比肯定会发挥重要作用。迪亚兹和埃尔卡比贡献了摩洛哥在 2025 年非洲杯上的 9 个进球中的 8 个。\n伊斯梅尔·赛巴里（Ismael Saibari）是另一位值得关注的球员。这位中场球员在 2025-26 赛季为埃因霍温的所有比赛中打进了 19 粒进球和 9 次助攻，这就是为什么他与转会拜仁慕尼黑的联系如此紧密。\n塞巴里在摩洛哥首场热身赛中梅开二度，4-0战胜马达加斯加，随后在纽约1-1战平挪威。\n与挪威的比赛因阿卜迪·埃扎尔佐利和努塞尔·马兹拉维的受伤而受到影响。埃扎尔祖利因此被排除在世界杯之外，与纳耶夫·阿盖德一样因伤退出国家队。与此同时，马兹拉维因肩伤而无法出战巴西队。\n巴西队证实内马尔小腿伤势恢复情况良好，但预计他的健康状况不足以参加对阵摩洛哥的比赛。右后卫韦斯利在战胜埃及的比赛中受伤，也可能缺席比赛。"
            ],
            [
                "历史交锋",
                "这将是巴西和摩洛哥在世界杯上的第二次交锋，上一次交锋是在 1998 年的小组赛阶段，罗纳尔多和里瓦尔多在这场比赛中打入了首个进球。\n此后他们唯一的一场比赛是 2023 年 3 月在突尼斯举行的一场友谊赛，摩洛哥凭借索菲安·布法尔和阿卜杜勒哈米德·萨比里的进球以 2-1 获胜。\n不过，巴西队在世界杯对阵非洲对手的八场比赛中赢了七场。唯一的例外是 2022 年 0-1 输给喀麦隆，尽管阵容发生了很大变化，桑巴军团已经进入了 16 强。"
            ],
            [
                "赛前预测（Opta 超算）",
                "巴西队在这场 C 组揭幕战中占据上风，在 Opta 超级计算机的 25,000 次赛前模拟中，巴西队以 57.7% 的成绩名列前茅。\n23.5% 的预测中分享了战利品，而摩洛哥全取三分的比例仅为 18.8%。\n不过，无论谁脱颖而出，都可能会认为自己最有机会获得小组第一。"
            ]
        ]
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
        "prediction": "",
        "summary_cn": "两国在 FIFA 世界排名中仅相差 14 位，韩国目前排名第 25 位，捷克排名第 39 位。",
        "analysis_cn": [
            [
                "关键数据速览",
                "· Opta 超级计算机将韩国队列为本次 A 组比赛的热门球队，其获胜概率为 42.9%，而捷克队的获胜概率为 31.1%。\n· 这将是韩国第 12 届世界杯，是亚洲国家中参加世界杯次数最多的国家。\n· 捷克队在欧足联预选赛中定位球进球数超过任何其他球队（11 个）。"
            ],
            [
                "深度分析",
                "本届世界杯是韩国第 12 次参加世界杯，是亚洲国家中参加世界杯次数最多的国家。这也代表着他们自 1986 年以来连续 11 次参赛，目前只有巴西（23 次）、德国（19 次）、阿根廷（14 次）和西班牙（13 次）连续参赛次数更长。\n他们最好的表现是在 2002 年，当时他们作为共同东道主获得第四名，现任教练洪明甫 (Hong Myung-bo) 带领球队完成了那场令人难忘的比赛。然而，在本土之外，他们从未闯过16强。\n周四在瓜达拉哈拉体育场举行的比赛是取得开门红的好机会，但韩国队是参加世界杯 30 场以上比赛的球队中胜率最低的球队（18.4%）。不过，他们在过去两届世界杯对阵欧洲国家的比赛中都取得了胜利（2018年2-0战胜德国，2022年2-1战胜葡萄牙）。\n此外，继2014年之后第二次带领国家队征战世界杯的洪浩带领球队在亚冠预选赛中保持不败，在16场比赛中取得了11胜5平的成绩。\n他们在两场热身赛中也积攒了一些动力，先以5-0大胜特立尼达和多巴哥，然后以1-0击败萨尔瓦多。\n经验丰富的队长孙兴慜在 33 岁时仍然是国家队的危险人物，并且直接参与了韩国过去 10 个世界杯进球中的 4 个进球（3 粒进球，1 次助攻）。这位前托特纳姆热刺前锋，现在效力于美国职业足球大联盟的洛杉矶足球俱乐部，在预选赛中也贡献了最多的进球贡献（14 – 10 粒进球，4 次助攻）。\n捷克队肯定也会感受到机会，因为他们正在为第十次参加世界杯（捷克斯洛伐克第八次）做准备，这也是自 2006 年以来的第一次，当时他们尽管开局 3-0 战胜美国队，但未能小组赛出线。\n两届亚军（1934 年和 1962 年）通过附加赛晋级，两场比赛均以 2-2 战平，并在点球大战中击败了爱尔兰共和国和丹麦。\n在预选赛期间，他们的定位球进球数比欧足联分区中的任何其他球队都多（11/22），其中包括 7 个角球进球。此外，他们的 7 个头球进球数仅次于挪威队（8 个）。\n帕特里克·希克 (Patrik Schick) 在代表捷克队参加的 7 场重大赛事中攻入 6 个进球，其中包括在 2020 年欧洲杯上与克里斯蒂亚诺·罗纳尔多 (Cristiano Ronaldo) 并列最佳射手。他也是捷克队2026年预选赛的最佳射手，他的五个进球中有三个来自头球。\n主教练米罗斯拉夫·库贝克（Miroslav Koubeck）自 2025 年 12 月起就开始担任主教练，在捷克队在预选赛中落后于克罗地亚队获得第二名后接任主教练。他成功地带领球队在对阵爱尔兰和丹麦的附加赛中取得了成功。\n库贝克的球队也为本届世界杯做了很好的热身，在A组揭幕战之前的友谊赛中分别以2-1和3-1击败科索沃和危地马拉。"
            ],
            [
                "历史交锋",
                "这场比赛标志着这两个国家首次在世界杯上交锋。\n此前他们曾有过3次交锋，全都是友谊赛。这些比赛各胜一场平局。\n韩国队上次对阵捷克队是胜利者，那是在 2016 年 6 月在布拉格以 2-1 获胜。"
            ],
            [
                "赛前预测（Opta 超算）",
                "两国在 FIFA 世界排名中仅相差 14 位，韩国目前排名第 25 位，捷克排名第 39 位。\n因此，Opta 超级计算机预测一场势均力敌的比赛，韩国队以 42.9% 的获胜概率略胜一筹。\n与此同时，捷克队获胜的几率为 31.1%，而平局的几率为 26%。\n从整体比赛来看，韩国队获得A组第一的概率为21.5%，进入32强的概率为70.3%，但总体获胜的概率仅为0.40%。\n目前，捷克队以 17.4% 的概率获得 A 组冠军，但他们也有很高的机会出线，并有 64.0% 的概率进入淘汰赛阶段。\n这将是 2026 年世界杯 A 组的第二场比赛，当天早些时候将进行墨西哥对阵南非的比赛。"
            ]
        ]
    }
]
