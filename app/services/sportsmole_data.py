"""自动生成：Sports Mole 各场赛前预览的结构化数据。

请勿手工编辑。由 scripts_gen_sportsmole.py 抓取 sportsmole.co.uk 预览页
解析生成。仅含事实型字段：比分预测（We say）、双方预测首发、近期战绩，
不含原文逐字转载。
数据来源：sportsmole.co.uk。
"""

null = None  # 兼容 JSON 字面量中的 null（缺失值）

SPORTSMOLE_RAW = [
    {
        "article_id": 599751,
        "home_en": "Switzerland",
        "away_en": "Canada",
        "home_cn": "瑞士",
        "away_cn": "加拿大",
        "url": "https://www.sportsmole.co.uk/football/switzerland/world-cup-2026/preview/switzerland-vs-canada-prediction-team-news-lineups_599751.html",
        "date": "2026-06-21T17:45:00Z",
        "score_home": 1,
        "score_away": 1,
        "lineup_home": "Kobel; Widemer, Jaquez, Akanji, Rodriguez; Aebischer, Xhaka, Freuler; Ndoye, Embolo, Vargas",
        "lineup_away": "Crepeau; Johnston, Bombito, Sigur, Laryea; Buchanan, Eustaquio, Saliba, Ahmed; David, Larin",
        "form_home": [
            "L",
            "D",
            "W",
            "D",
            "D",
            "W"
        ],
        "form_away": [
            "D",
            "D",
            "W",
            "D",
            "D",
            "W"
        ]
    },
    {
        "article_id": 599770,
        "home_en": "Scotland",
        "away_en": "Brazil",
        "home_cn": "苏格兰",
        "away_cn": "巴西",
        "url": "https://www.sportsmole.co.uk/football/scotland/world-cup-2026/preview/scotland-vs-brazil-prediction-team-news-lineups_599770.html",
        "date": "2026-06-22T20:00:00Z",
        "score_home": 1,
        "score_away": 3,
        "lineup_home": "Gunn; Patterson, Hendry, Hanley, Robertson, Tierney; Christie, Ferguson; McTominay, McGinn; Adams",
        "lineup_away": "Alisson; Danilo, Marquinhos, Gabriel, Douglas Santos; Guimaraes, Casemiro; Rayan, Paqueta, Vinicius Jr; Cunha",
        "form_home": [
            "L",
            "L",
            "W",
            "W",
            "W",
            "L"
        ],
        "form_away": [
            "L",
            "W",
            "W",
            "W",
            "D",
            "W"
        ]
    },
    {
        "article_id": 599775,
        "home_en": "Morocco",
        "away_en": "Haiti",
        "home_cn": "摩洛哥",
        "away_cn": "海地",
        "url": "https://www.sportsmole.co.uk/football/morocco/world-cup-2026/preview/morocco-vs-haiti-prediction-team-news-lineups_599775.html",
        "date": "2026-06-22T22:00:00Z",
        "score_home": 3,
        "score_away": 0,
        "lineup_home": "Bono; Hakimi, Diop, Riad, Mazraoui; El Aynaoui, Bouaddi; Diaz, Ounahi, El Khannouss; Saibari",
        "lineup_away": "Placide; Arcus, Delcroix, Ade, Experience; Deedson, Bellegarde, Jean Jacques, Providence; Isidor, Pierrot",
        "form_home": [
            "W",
            "W",
            "W",
            "D",
            "D",
            "W"
        ],
        "form_away": [
            "L",
            "D",
            "W",
            "L",
            "L",
            "L"
        ]
    },
    {
        "article_id": 599786,
        "home_en": "Czech Republic",
        "away_en": "Mexico",
        "home_cn": "捷克",
        "away_cn": "墨西哥",
        "url": "https://www.sportsmole.co.uk/football/czech-republic/world-cup-2026/preview/czech-republic-vs-mexico-prediction-team-news-lineups_599786.html",
        "date": "2026-06-21T23:20:00Z",
        "score_home": 1,
        "score_away": 2,
        "lineup_home": "Kovar; Holes, Hranac, Krejci; Coufal, Darida, Cerv, Sadilek, Sojka; Schick, Hlozek",
        "lineup_away": "Rangel; Sanchez, Reyes, Vasquez, Gallardo; Gutierrez, Lira, Romo; Alvarado, Gimenez, Quinones",
        "form_home": [
            "D",
            "L",
            "W",
            "W",
            "W",
            "W"
        ],
        "form_away": [
            "W",
            "W",
            "W",
            "W",
            "W",
            "D"
        ]
    },
    {
        "article_id": 599815,
        "home_en": "South Africa",
        "away_en": "South Korea",
        "home_cn": "南非",
        "away_cn": "韩国",
        "url": "https://www.sportsmole.co.uk/football/south-africa/world-cup-2026/preview/south-africa-vs-south-korea-prediction-team-news-lineups_599815.html",
        "date": "2026-06-22T12:25:00Z",
        "score_home": 0,
        "score_away": 1,
        "lineup_home": "Williams; Mudau, Okon, Mbokazi, Modiba; Mbatha, Sithole, Adams; Maseko, Appollis, Rayners",
        "lineup_away": "S Kim; H Lee, M J Kim, G Lee; M H Kim, Hwang, Paik, Seol; K Lee, J Lee; Son",
        "form_home": [],
        "form_away": []
    },
    {
        "article_id": 599838,
        "home_en": "Bosnia-Herzegovina",
        "away_en": "Qatar",
        "home_cn": "波黑",
        "away_cn": "卡塔尔",
        "url": "https://www.sportsmole.co.uk/football/bosnia-herzegovina/world-cup-2026/preview/bosnia-hvina-vs-qatar-prediction-team-news-lineups_599838.html",
        "date": "2026-06-22T18:54:00Z",
        "score_home": 2,
        "score_away": 1,
        "lineup_home": "Vasilj; Dedic, Katic, Hadzikadunic, Kolasinac; Alajbegovic, Sunjic, Tahirovic, Memic; Dzeko, Demirovic",
        "lineup_away": "Abunada; Al Oui, Khoukhi, Miguel, Al Brake; Laye, Gaber, Boudiaf; Edmilson, Abdurisag, Afif",
        "form_home": [],
        "form_away": []
    },
    {
        "article_id": 599846,
        "home_en": "Turkey",
        "away_en": "USA",
        "home_cn": "土耳其",
        "away_cn": "美国",
        "url": "https://www.sportsmole.co.uk/football/turkey/world-cup-2026/preview/turkey-vs-usa-prediction-team-news-lineups_599846.html",
        "date": "2026-06-22T20:01:54Z",
        "score_home": 1,
        "score_away": 2,
        "lineup_home": "Cakir; Muldur, Demiral, Kabak, Kadioglu; Ozcan, Calhanoglu; Akgun, Guler, Yildiz; Gul",
        "lineup_away": "Freese; Scally, McKenzie, Trusty, Arfsten; Roldan, Berhalter; Weah, Reyna, Zendejas; Pepi",
        "form_home": [
            "W",
            "W",
            "W",
            "W",
            "L",
            "L"
        ],
        "form_away": [
            "L",
            "L",
            "W",
            "L",
            "W",
            "W"
        ]
    },
    {
        "article_id": 599879,
        "home_en": "Japan",
        "away_en": "Sweden",
        "home_cn": "日本",
        "away_cn": "瑞典",
        "url": "https://www.sportsmole.co.uk/football/japan/world-cup-2026/preview/japan-vs-sweden-prediction-team-news-lineups_599879.html",
        "date": "2026-06-23T10:40:00Z",
        "score_home": 2,
        "score_away": 1,
        "lineup_home": "Suzuki; Tomiyasu, Itakura, Ito; Doan, Sano, Tanaka, Nakamura; Ito, Kamada, Ueda",
        "lineup_away": "Nordfeldt; Lagerbielke, Hien, Lindelof; Elanga, Bergvall, Karlstrom, Ayari, Gudmundsson; Gyokeres, Isak",
        "form_home": [],
        "form_away": []
    },
    {
        "article_id": 599880,
        "home_en": "Ecuador",
        "away_en": "Germany",
        "home_cn": "厄瓜多尔",
        "away_cn": "德国",
        "url": "https://www.sportsmole.co.uk/football/germany/world-cup-2026/preview/ecuador-vs-germany-prediction-team-news-lineups_599880.html",
        "date": "2026-06-23T18:00:00Z",
        "score_home": 0,
        "score_away": 2,
        "lineup_home": "Galindez; Ordonez, Pacho, Hincapie; Yeboah, Franco, Caicedo, Vite, Estupinan; Plata, Valencia",
        "lineup_away": "Baumann; Anton, Tah, Rudiger, Raum; Goretzka, Stiller; Leweling, Amiri, Beier; Undav",
        "form_home": [
            "D",
            "D",
            "W",
            "W",
            "L",
            "D"
        ],
        "form_away": [
            "W",
            "W",
            "W",
            "W",
            "W",
            "W"
        ]
    },
    {
        "article_id": 599885,
        "home_en": "Curacao",
        "away_en": "Ivory Coast",
        "home_cn": "库拉索",
        "away_cn": "科特迪瓦",
        "url": "https://www.sportsmole.co.uk/football/curacao/world-cup-2026/preview/curacao-vs-ivory-coast-prediction-team-news-lineups_599885.html",
        "date": "2026-06-23T20:00:00Z",
        "score_home": 0,
        "score_away": 2,
        "lineup_home": "Room; Brenet, Gaari, Obispo, Floranus, Fonville; Chong, Comenencia, L. Bacuna, J. Bacuna; Locadia",
        "lineup_away": "Y. Fofana; Doue, Kossounou, Agbadou, Konan; Sangare, Kessie, Inao Oulai; Diallo, Bonny, Diomande",
        "form_home": [
            "D",
            "W",
            "W",
            "W",
            "W",
            "W"
        ],
        "form_away": [
            "W",
            "W",
            "L",
            "W",
            "D",
            "L"
        ]
    },
    {
        "article_id": 599899,
        "home_en": "Paraguay",
        "away_en": "Australia",
        "home_cn": "巴拉圭",
        "away_cn": "澳大利亚",
        "url": "https://www.sportsmole.co.uk/football/paraguay/world-cup-2026/preview/paraguay-vs-australia-prediction-team-news-lineups_599899.html",
        "date": "2026-06-23T22:21:00Z",
        "score_home": 0,
        "score_away": 1,
        "lineup_home": "Gill; Caceres, G Gomez, Alderete, Alonso; Velazquez, Cubas, D Gomez, Galarza; Pitta, Enciso",
        "lineup_away": "Beach; Circati, Souttar, Burgess; Italiano, O'Neill, Okon-Engstler, Bos; Volpato, Toure, Irankunda",
        "form_home": [
            "W",
            "W",
            "L",
            "W",
            "L",
            "W"
        ],
        "form_away": [
            "W",
            "W",
            "L",
            "D",
            "W",
            "L"
        ]
    },
    {
        "article_id": 599913,
        "home_en": "Tunisia",
        "away_en": "Netherlands",
        "home_cn": "突尼斯",
        "away_cn": "荷兰",
        "url": "https://www.sportsmole.co.uk/football/tunisia/world-cup-2026/preview/tunisia-vs-netherlands-prediction-team-news-lineups_599913.html",
        "date": "2026-06-23T17:13:00Z",
        "score_home": 0,
        "score_away": 3,
        "lineup_home": "Dahmen; Valery, Rekik, Talbi, Ali Abdi; Skhiri; Slimane, Hannibal; Chaouat, Saad, Mastouri",
        "lineup_away": "Verbruggen; Dumfries, Van Dijk, Van Hecke, Van de Ven; De Jong, Reijnders, Gravenberch; Malen, Brobbey, Gakpo",
        "form_home": [],
        "form_away": [
            "W",
            "D",
            "L",
            "W",
            "D",
            "W"
        ]
    }
]
