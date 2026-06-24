# Requirements Document

## Introduction

This document specifies the requirements for **WorldCup 3.0 — FIFA Ultimate Edition (Night Stadium HUD)**, a ground-up rebuild of the presentation, rendering, and motion layers of the existing PyQt6 desktop application (`世界杯赛事终端 / World Cup Console`). The existing data layer (`app/api`, `app/models`, `app/services`) is preserved and reused unchanged; everything visual above it is rearchitected around a single coherent theme — **"Night Stadium Futuristic HUD."**

These requirements are derived from the approved design document (`design.md`) and are organized into two complementary concerns:

1. **Concrete UI composition** — the exact layout, ordering, labels, and content of the Overview (概览) home page, pinned 1:1 to the supplied high-fidelity mockup (`想象中的效果图.png`). These requirements make the visual composition testable so the implementation can be verified against the mockup.
2. **Behavioral foundation** — the rendering, motion, particle, performance, and correctness behaviors that underpin the entire application, carried over from the design's component contracts and Correctness Properties.

Each requirement uses exactly one EARS pattern. All system names are defined in the Glossary. Acceptance criteria that correspond to design Correctness Properties are annotated with their property number to preserve traceability into the property-based test suite.

## Glossary

- **Overview Page**: The home/landing page of the application, titled "概览 / OVERVIEW", that composes the broadcast dashboard described by the mockup. (Implemented by `HomePage`.)
- **Navigation Rail**: The left-hand vertical chrome strip containing the logo, the ordered list of navigation items, and the footer status block. (Part of `MainWindow` shell.)
- **Top HUD Bar**: The top chrome strip containing the page title, search box, notification bell, region globe, and profile avatar.
- **Sub-Header**: The line beneath the page title showing the tournament tagline, data-source label, and the live-connection status pill.
- **Hero Match Card**: The large focal-match card on the Overview Page. (Implemented by `HeroMatchCard`.)
- **Standings Panel**: The group-standings card on the right of the Overview Page. (Implemented by `StandingsTable`.)
- **Stat Strip**: The horizontal row of six equal-width glass statistic cards on the Overview Page.
- **Today Matches Panel**: The "今日赛程 / TODAY'S MATCHES" bottom panel.
- **Live Match Center**: The "实时比赛 / LIVE MATCH" bottom panel and its event feed. (Implemented by `LiveMatchCenter`.)
- **Top Scorers Panel**: The "射手榜 / TOP SCORERS" bottom panel.
- **Host Cities Panel**: The "主办城市 / HOST CITIES" bottom panel with the North America map.
- **Stage Compositor**: The single full-window, multi-layer night-stadium backdrop renderer, with a GPU path (`StageCompositor`) and a CPU fallback (`StageCompositorCPU`) sharing one public API.
- **Particle Engine**: The unified particle subsystem composited inside the Stage Compositor.
- **Floodlight Sweep**: The two periodic radial light beams that sweep across the backdrop.
- **Motion System**: The single sanctioned source of all UI transitions (`motion_system.std_anim` / `hover_lift`).
- **Glass Card**: The unified glassmorphism card base used by every card in the application. (Implemented by `GlassCard`.)
- **Count-Up Number**: A numeric label that animates from 0 to its target value. (Implemented by `CountUpNumber`.)
- **Floating Flag**: A flag widget that bobs vertically in a continuous ambient loop. (Implemented by `FloatingFlag`.)
- **Mouse Trail**: The subtle trailing-dot overlay following the cursor. (Implemented by `MouseTrailOverlay`.)
- **Chart System**: The animated radar, line, and bar charts. (Implemented by `app/ui/widgets/charts/`.)
- **Frame Clock**: The single global animation heartbeat (`FrameClock`) that emits `tick(t, dt)`.
- **Data Service**: The existing asynchronous data layer (`DataService`, httpx + diskcache) that performs all network and caching work.
- **Win Probability**: The triple `(home, draw, away)` of integer percentages whose components each lie in `[0,100]` and sum to exactly 100.
- **Group Selector**: The set of group tabs labelled A through L on the Standings Panel.
- **Live Connection Pill**: The right-aligned status pill in the Sub-Header indicating live data connectivity.

## Requirements

### Requirement 1: Overview Page information hierarchy

**User Story:** As a fan opening the app, I want a broadcast-grade overview dashboard with a strict, predictable layout, so that the most important match and data are visually dominant.

#### Acceptance Criteria

1. THE Overview Page SHALL arrange its regions top-to-bottom as: Hero Match Card row, Stat Strip row, then a bottom multi-panel row.
2. THE Overview Page SHALL allocate layout stretch factors so the Hero:Overview:Standings:Schedule:Analysis:Other visual-weight ratio equals 40:20:15:10:10:5.
3. WHERE the application window is resized, THE Overview Page SHALL preserve the configured region stretch ratios.
4. THE Overview Page SHALL display the Hero Match Card and the Standings Panel side by side, with the Hero Match Card occupying the wider (left, ~65%) column and the Standings Panel the narrower (right, ~35%) column.

### Requirement 2: Navigation Rail composition

**User Story:** As a user, I want a consistent left navigation rail, so that I can reach every section of the app in a known order.

#### Acceptance Criteria

1. THE Navigation Rail SHALL display, at its top, a glowing "WORLD CUP / FIFA WORLD CUP" logo with a trophy mark.
2. THE Navigation Rail SHALL list navigation items in this exact order: 概览 (Overview), 赛程中心 (Schedule Center), 实时比赛 (Live Match), 球队 (Teams), 球员 (Players), 数据分析 (Data Analysis), 积分榜 (Standings), 射手榜 (Top Scorers), 场馆地图 (Venue Map), 新闻资讯 (News), 收藏夹 (Favorites), 设置 (Settings).
3. WHILE the Overview Page is the active page, THE Navigation Rail SHALL render the 概览 (Overview) item in the highlighted/active state and all other items in the inactive state.
4. THE Navigation Rail SHALL display a footer showing a "数据同步中… 98%" synchronization progress indicator and a "v3.0.0 / WORLD CUP 2026" version label.

### Requirement 3: Top HUD Bar composition

**User Story:** As a user, I want a top HUD bar with title, search, and account controls, so that I can identify the page and search globally.

#### Acceptance Criteria

1. THE Top HUD Bar SHALL display the page title "概览" with the subtitle "OVERVIEW".
2. THE Top HUD Bar SHALL display a centered search box with the placeholder text "搜索球队 / 球员 / 比赛…".
3. THE Top HUD Bar SHALL display a notification bell icon, a region globe showing "CN", and a circular profile avatar.

### Requirement 4: Sub-Header composition

**User Story:** As a user, I want a sub-header that frames the tournament context and live status, so that I know the data is current and where it comes from.

#### Acceptance Criteria

1. THE Sub-Header SHALL display the text "2026 美加墨世界杯 · 实时数据总览".
2. THE Sub-Header SHALL display the text "OVERVIEW · 数据来源：懂球帝公开接口".
3. THE Sub-Header SHALL display a right-aligned green Live Connection Pill labelled "实时数据已连接" with a status dot.

### Requirement 5: Hero Match Card layout and labels

**User Story:** As a fan, I want the featured match presented like a broadcast graphic, so that I can see the fixture, timing, and venue at a glance.

#### Acceptance Criteria

1. THE Hero Match Card SHALL display a stage/round label "小组赛 第3轮" in its top-left corner.
2. THE Hero Match Card SHALL display an "即将开始" status pill in its top-right corner.
3. THE Hero Match Card SHALL display the two competing teams centered as home flag — "VS" — away flag, with team names rendered as "瑞士 / SWITZERLAND" and "加拿大 / CANADA" for the sampled fixture.
4. THE Hero Match Card SHALL display a center column with a "距离开赛" caption above a flip-style countdown showing hours, minutes, and seconds labelled 时 / 分 / 秒.
5. THE Hero Match Card SHALL display the kickoff date-time "06月25日 03:00" and the venue "BC Place Stadium, Vancouver".
6. THE Hero Match Card SHALL display three pill action buttons in this order: 观看直播 (primary, with a play icon), 赛前分析, 历史交锋.
7. THE Hero Match Card SHALL display left and right carousel chevron arrows for paging between matches.

### Requirement 6: Hero countdown behavior

**User Story:** As a fan, I want a live countdown to kickoff, so that I know exactly how long until the match begins.

#### Acceptance Criteria

1. WHILE the kickoff time is in the future, THE Hero Match Card SHALL update the displayed countdown once per second.
2. WHEN two consecutive countdown ticks occur before kickoff, THE Hero Match Card SHALL render a remaining time that is non-increasing and never negative. _(Design Property 10)_
3. WHEN the current time reaches or passes the kickoff time, THE Hero Match Card SHALL stop the countdown timer and display a "LIVE" / "KICK-OFF" indicator.
4. THE Hero Match Card SHALL use exactly one per-second timer for the countdown and no other per-widget timers.

### Requirement 7: Win-probability split bar

**User Story:** As a fan, I want a win/draw/loss probability bar, so that I can gauge the predicted outcome of the featured match.

#### Acceptance Criteria

1. THE Hero Match Card SHALL display a win-probability bar split into three segments rendered left-to-right as home-win, draw, and away-win, with a red→neutral→blue gradient.
2. THE Hero Match Card SHALL label the segments for the sampled fixture as "47% 瑞士胜", "26% 平局", and "27% 加拿大胜".
3. THE Hero Match Card SHALL render the three segment widths proportional to the Win Probability triple, whose components sum to exactly 100. _(Design Property 12)_
4. IF the supplied Win Probability is invalid (components do not sum to 100), THEN THE Hero Match Card SHALL hide the win-probability bar.

### Requirement 8: Hero team rankings

**User Story:** As a fan, I want per-team rating and ranking context, so that I can compare the two sides.

#### Acceptance Criteria

1. THE Hero Match Card SHALL display, per team, an Elo rating, a FIFA ranking, and a world ranking.
2. IF rating or ranking data is missing for a team, THEN THE Hero Match Card SHALL render a placeholder "—" in place of the missing value.

### Requirement 9: Standings Panel layout and group selector

**User Story:** As a fan, I want a group standings table with a group selector, so that I can browse the table for any group.

#### Acceptance Criteria

1. THE Standings Panel SHALL display the header "小组积分榜 / GROUP STANDINGS".
2. THE Standings Panel SHALL display a Group Selector with tabs labelled A, B, C, D, E, F, G, H, I, J, K, L in that order.
3. WHILE no other group has been chosen, THE Standings Panel SHALL render group A as the active tab.
4. WHEN a user selects a Group Selector tab, THE Standings Panel SHALL display the standings for the selected group and mark that tab active.
5. THE Standings Panel SHALL display a footer button labelled "查看完整积分榜".

### Requirement 10: Standings table columns and content

**User Story:** As a fan, I want detailed standings columns, so that I can read points, goal difference, qualification odds, and recent form.

#### Acceptance Criteria

1. THE Standings Panel SHALL display columns in this order: # (rank), 球队 (team), 场次 (played), 胜平负 (W/D/L), 净胜球 (goal difference), 积分 (points), 出线概率 (qualification probability), 最近5场 (last 5).
2. THE Standings Panel SHALL render the 出线概率 column as a progress bar accompanied by a percentage value.
3. THE Standings Panel SHALL render the 最近5场 column as colored result pills where win=green, draw=amber, loss=red.
4. THE Standings Panel SHALL render at most 5 form pills per row, and each pill SHALL be one of {W, D, L}. _(Design Property 14)_
5. THE Standings Panel SHALL render the 出线概率 bar fill fraction equal to `clamp(p, 0, 1)` for qualification probability `p`. _(Design Property 16)_
6. THE Standings Panel SHALL display sample rows for the active group as 墨西哥 92%, 韩国 56%, 捷克 48%, 南非 4%.
7. WHERE a rank-change indicator is shown for a row, THE Standings Panel SHALL render "↑n" when the rank delta is positive, "↓n" when negative, and "—" when zero, where n is the absolute delta. _(Design Property 15)_

### Requirement 11: Stat Strip composition

**User Story:** As a fan, I want a row of tournament stat cards, so that I can absorb headline numbers quickly.

#### Acceptance Criteria

1. THE Stat Strip SHALL display exactly six equal-width Glass Cards in a single horizontal row for the 2026 tournament dataset.
2. THE Stat Strip SHALL display the cards left-to-right as: 总比赛场次, 总进球数, 进球球员, 平均进球, 参赛球队, 主办城市.
3. THE Stat Strip SHALL compute each card's headline value from current tournament data supplied by the Data Service, displaying the secondary text and icon shown for that card.
4. THE Stat Strip SHALL display the 总比赛场次 card with the sampled value 104, the secondary text "已结束 48 场", and a mini sparkline.
5. THE Stat Strip SHALL display the 总进球数 card with the sampled value 141, a "↑8%" delta, the secondary text "场均2.94球", and a soccer-ball icon.
6. THE Stat Strip SHALL display the 进球球员 card with the sampled value 89, a "↑15%" delta, the secondary text "来自32个国家", and a player icon.
7. THE Stat Strip SHALL display the 平均进球 card with the sampled value 2.94, a "↑6%" delta, the secondary text "每场比赛", and a goal icon.
8. THE Stat Strip SHALL display the 参赛球队 card with the sampled value 48, the secondary text "12个小组", and a shield icon.
9. THE Stat Strip SHALL display the 主办城市 card with the sampled value 16, the secondary text "美国/加拿大/墨西哥", and a pin icon.
10. WHEN the Overview Page is entered, THE Stat Strip SHALL render each headline number using the Count-Up Number animation.

### Requirement 12: Today Matches Panel

**User Story:** As a fan, I want today's fixtures listed, so that I can see what is playing now and later today.

#### Acceptance Criteria

1. THE Today Matches Panel SHALL display the header "今日赛程 / TODAY'S MATCHES" with a match count that reflects the actual number of fixtures scheduled for the current day (e.g. "4场比赛" for the sampled day).
2. THE Today Matches Panel SHALL display time-stamped fixture rows, each with both teams' flags and a score or status.
3. THE Today Matches Panel SHALL display the sample rows: "01:00 葡萄牙 5-0 乌兹别克斯坦" with an odds tag, "04:00 英格兰 0-0 加纳" marked 已结束, "07:00 巴西 VS 塞尔维亚" marked 直播, and "10:00 法国 VS 沙特阿拉伯" marked 将开赛.
4. THE Today Matches Panel SHALL display a footer labelled "查看完整赛程".

### Requirement 13: Live Match Center panel and events

**User Story:** As a fan, I want a live match panel with a running event feed, so that I can follow goals and key moments in real time.

#### Acceptance Criteria

1. THE Live Match Center SHALL display the header "实时比赛 / LIVE MATCH".
2. WHILE a match is live, THE Live Match Center SHALL display a red "直播中" badge with the live clock (e.g. "75:24").
3. THE Live Match Center SHALL display the live scoreline with both teams' flags (e.g. "巴西 2 - 1 塞尔维亚").
4. THE Live Match Center SHALL display an event timeline over a mini pitch with sample events "23' 维尼修斯", "45' 内马尔", and "63' 米特罗维奇".
5. WHEN an event is pushed to the Live Match Center, THE Live Match Center SHALL create exactly one new event row for that event. _(Design Property 19)_
6. WHEN a goal event is pushed, THE Live Match Center SHALL slide the new event row in from the top using the Motion System.
7. WHILE the LIVE badge is breathing, THE Live Match Center SHALL keep the badge opacity within `[0.7, 1.0]`. _(Design Property 18)_
8. THE Live Match Center SHALL display a footer labelled "进入比赛中心".

### Requirement 14: Top Scorers Panel

**User Story:** As a fan, I want a top scorers list, so that I can see the tournament's leading goal scorers.

#### Acceptance Criteria

1. THE Top Scorers Panel SHALL display the header "射手榜 / TOP SCORERS".
2. THE Top Scorers Panel SHALL display ranked rows, each with a circular player avatar, rank, player and country, and goal count.
3. THE Top Scorers Panel SHALL display the sample rows: "1 梅西 (阿根廷) 5", "2 姆巴佩 (法国) 4", "2 哈兰德 (挪威) 4", "4 Á. Morata (西班牙) 3".
4. THE Top Scorers Panel SHALL display a footer labelled "查看完整射手榜".

### Requirement 15: Host Cities Panel

**User Story:** As a fan, I want a map of host cities, so that I can see where the tournament is being played.

#### Acceptance Criteria

1. THE Host Cities Panel SHALL display the header "主办城市 / HOST CITIES".
2. THE Host Cities Panel SHALL display a stylized North America map covering the USA, Canada, and Mexico, with glowing city dots.
3. THE Host Cities Panel SHALL label host-city dots including 温哥华, 多伦多, 西雅图, 旧金山, 洛杉矶, 达拉斯, 休斯顿, 堪萨斯城, 亚特兰大, 纽约·新泽西, 波士顿, 费城, 迈阿密, 墨西哥城, 瓜达拉哈拉, and 蒙特雷.
4. THE Host Cities Panel SHALL display a footer labelled "查看全部城市".

### Requirement 16: Night Stadium backdrop composition

**User Story:** As a user, I want a cinematic night-stadium backdrop, so that the app feels like a broadcast match center.

#### Acceptance Criteria

1. THE Stage Compositor SHALL render a single composited backdrop with layers in bottom-to-top order: base vertical gradient (L1), floodlight pools (L2), grass/noise texture (L3), pitch markings (L4), and trophy silhouette (L5).
2. THE Stage Compositor SHALL render the base gradient from top "#06111A" through mid "#0A1B28" to bottom "#0F2A1F".
3. THE Stage Compositor SHALL keep each ambient layer's contribution within its specified opacity band: floodlights ~8%, grass 3–5%, pitch markings ~2%, trophy ~2%. _(Design Property 7)_
4. THE Stage Compositor SHALL render the trophy-silhouette layer (L5) as a function of pixel position only, independent of time. _(Design Property 9)_
5. THE Overview Page SHALL render its content over the backdrop using translucent chrome/hero regions and an opaque scroll body.

### Requirement 17: Particle Engine

**User Story:** As a user, I want subtle ambient particles, so that the backdrop feels alive without being distracting.

#### Acceptance Criteria

1. THE Particle Engine SHALL maintain an active particle count within `[80, 120]`. _(Design Property 4)_
2. THE Particle Engine SHALL keep each particle's per-frame speed within `[0.1, 0.3]` px/frame at the reference frame rate. _(Design Property 5)_
3. THE Particle Engine SHALL keep each particle's rendered opacity within `[0.05, 0.15]`. _(Design Property 6)_
4. THE Particle Engine SHALL render only particles of kind dust, grass, or glint.
5. THE Particle Engine SHALL exclude petals, sakura, snow, meteors, and browser-game style effects.

### Requirement 18: Floodlight Sweep

**User Story:** As a user, I want sweeping floodlights, so that the scene evokes a final-night broadcast atmosphere.

#### Acceptance Criteria

1. THE Floodlight Sweep SHALL move two radial beams horizontally with a periodic position of period 8 seconds. _(Design Property 8)_
2. THE Floodlight Sweep SHALL keep its combined opacity contribution at or below approximately 5%. _(Design Property 8)_
3. THE Floodlight Sweep SHALL derive beam position from Frame Clock time so motion is frame-rate independent.

### Requirement 19: Unified Motion System

**User Story:** As a user, I want uniform, snappy motion across the app, so that the experience feels coherent and never sluggish.

#### Acceptance Criteria

1. WHEN an animation is created through the Motion System, THE Motion System SHALL set its easing curve to OutCubic. _(Design Property 1)_
2. WHEN an animation is created through the Motion System, THE Motion System SHALL set its effective duration to at most 500 ms. _(Design Property 2)_
3. THE Motion System SHALL use 180 ms as the standard transition duration.
4. WHEN a user hovers a Glass Card, THE Glass Card SHALL move to `restY - 6px`, and WHEN the pointer leaves, THE Glass Card SHALL return exactly to `restY`. _(Design Property 3)_

### Requirement 20: Glass Card system

**User Story:** As a user, I want a consistent glass card aesthetic, so that every surface looks like part of one design language.

#### Acceptance Criteria

1. THE Glass Card SHALL render with corner radius 24px, fill `rgba(255,255,255,0.05)`, border `rgba(255,255,255,0.08)`, and shadow `0 10px 40px rgba(0,0,0,0.4)`.
2. WHEN a user hovers a Glass Card, THE Glass Card SHALL brighten its border to the high-contrast glass border color.
3. WHEN animating hover elevation, THE Glass Card SHALL animate the position property and SHALL NOT animate shadow blur radius.

### Requirement 21: Count-Up Number animation

**User Story:** As a fan, I want headline numbers to roll up on page entry, so that key stats feel dynamic and draw attention.

#### Acceptance Criteria

1. WHEN a Count-Up Number receives a target, THE Count-Up Number SHALL animate the displayed value from 0 toward the target over 800 ms.
2. WHEN the count-up animation completes, THE Count-Up Number SHALL render a value exactly equal to the target. _(Design Property 11)_
3. WHILE animating toward a non-negative target, THE Count-Up Number SHALL render non-decreasing intermediate values. _(Design Property 11)_

### Requirement 22: Floating Flag animation

**User Story:** As a fan, I want the hero flags to gently bob, so that the featured match feels lively.

#### Acceptance Criteria

1. THE Floating Flag SHALL oscillate its vertical offset within `[-3, +3]` px.
2. THE Floating Flag SHALL complete one oscillation cycle every 4 seconds.

### Requirement 23: Mouse Trail overlay

**User Story:** As a user, I want a subtle cursor trail, so that pointer motion feels premium without being gimmicky.

#### Acceptance Criteria

1. THE Mouse Trail SHALL render at most 5 trail dots at any time. _(Design Property 17)_
2. THE Mouse Trail SHALL render dot opacities that are strictly decreasing from head to tail. _(Design Property 17)_
3. THE Mouse Trail SHALL ignore pointer events (it SHALL be transparent for mouse input).
4. WHILE the pointer is stationary and no trail dots are visible, THE Mouse Trail SHALL reset its stored dot opacity values.

### Requirement 24: Chart System

**User Story:** As a fan, I want animated charts, so that analytics feel like a broadcast graphics package.

#### Acceptance Criteria

1. WHEN a chart receives a dataset, THE Chart System SHALL animate its reveal progress monotonically from 0 to 1. _(Design Property 20)_
2. WHEN a chart reveal completes, THE Chart System SHALL render geometry that matches the input data values. _(Design Property 20)_
3. THE Chart System SHALL target a 300 ms eased (OutCubic) refresh for chart updates, within a tolerance of ±10 ms.

### Requirement 25: Single Frame Clock heartbeat and frame-rate independence

**User Story:** As a user, I want smooth, consistent motion at any refresh rate, so that the app looks correct on any machine.

#### Acceptance Criteria

1. THE Stage Compositor SHALL subscribe to the Frame Clock on show and unsubscribe on hide.
2. THE Stage Compositor SHALL throttle ambient redraws to approximately 60 FPS even when the Frame Clock runs faster.
3. WHERE the Frame Clock runs at any supported rate between 30 Hz and 240 Hz, THE Stage Compositor and Particle Engine SHALL advance time-driven motion at the same real-time speed. _(Design Property 21)_
4. THE application SHALL use no live per-widget timers other than the Frame Clock and the single Hero Match Card countdown timer.

### Requirement 26: Off-thread data loading

**User Story:** As a user, I want the interface to stay responsive while data loads, so that the app never freezes.

#### Acceptance Criteria

1. WHEN data is loaded, THE Data Service SHALL execute the network request off the GUI/main thread. _(Design Property 13)_
2. THE Overview Page SHALL request all data through the Data Service rather than issuing network calls directly.

### Requirement 27: Rendering backend selection and equivalence

**User Story:** As a user on any hardware, I want the app to render correctly whether or not the GPU path is available, so that it works everywhere.

#### Acceptance Criteria

1. WHEN the application starts, THE Stage Compositor SHALL attempt to initialize the GPU (OpenGL 3.3) backend.
2. IF the GPU context is unavailable or shader compilation/link fails, THEN THE Stage Compositor SHALL construct the CPU fallback backend with the identical public API and log a warning.
3. THE Stage Compositor SHALL accept identical `set_palette`, `set_enabled`, and `set_paused` calls on both the GPU and CPU backends and SHALL produce the same observable state transitions. _(Design Property 22)_
4. IF a runtime verification detects a divergence between the GPU and CPU backends' observable state for an identical call, THEN THE Stage Compositor SHALL log the mismatch and fall back to the CPU backend.

### Requirement 28: Data and rendering error handling

**User Story:** As a user, I want graceful degradation when data or rendering fails, so that the app stays usable.

#### Acceptance Criteria

1. IF the Data Service raises a network or timeout error, THEN THE Overview Page SHALL retain the last good data and show the existing empty/error state for affected widgets.
2. WHEN the next scheduled refresh tick occurs after a fetch failure, THE Data Service SHALL retry the failed load.
3. WHERE low-performance mode is enabled (`WC_LITE=1` / `LOW_PERF`), THE Stage Compositor SHALL render a static gradient backdrop and THE Motion System SHALL make transitions instant while keeping the UI fully functional.

### Requirement 29: First-open broadcast scene

**User Story:** As a first-time user, I want the home screen to immediately present the full broadcast scene, so that the app makes a strong first impression.

#### Acceptance Criteria

1. WHEN the Overview Page is first painted, THE Overview Page SHALL compose the night-stadium gradient, Floodlight Sweep, Particle Engine, Floating Flags, Hero countdown, Count-Up Numbers, populated Standings Panel, grass texture, and trophy silhouette together in one scene.
2. WHEN the Overview Page becomes active via navigation, THE Motion System SHALL target a 180 ms fade-and-slide page transition, permitting minor overruns provided the requested duration is 180 ms.
