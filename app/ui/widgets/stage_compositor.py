"""stage_compositor —— 统一「夜间球场」舞台合成器（WorldCup 3.0 渲染核心）。

本模块用**一个**铺满整窗的最底层背景控件，取代旧的三套互相重叠的背景实现
(``particle_bg.py`` / ``gl_backdrop.py`` / ``skin_backdrop.py``)，渲染设计文档
约定的「夜间球场」五层氛围：

    L1 Base       —— 垂直球场之夜渐变（顶 #06111A → 中 #0A1B28 → 底 #0F2A1F）
    L2 Floodlights—— 顶部大面积径向泛光池（~8% 透明度）
    L3 Grass/noise—— 草皮纹理 / 场地噪声（3–5% 透明度）
    L4 Pitch      —— 极淡中圈 + 中线（~2% 透明度）
    L5 Trophy     —— 居中大力神杯剪影（~2% 透明度，**与时间无关**）

两个后端共享**完全一致**的公共 API（``set_palette`` / ``set_enabled`` /
``set_paused``）与 FrameClock「显示订阅 / 隐藏退订」行为：

* :class:`StageCompositor`     —— GPU 路径（``QOpenGLWidget`` + 全屏三角形 +
  ``#version 330 core`` 片元着色器，逐像素合成 L1→L5；每帧只上传
  ``u_time`` / ``u_res`` / ``u_ramp`` / ``u_accents`` 这几个 uniform）。
* :class:`StageCompositorCPU`  —— CPU 回退路径（``QPainter`` 把同样的层序画进
  ``BACKDROP_RENDER_SCALE`` 低分离屏缓冲再放大 blit）。

:func:`create_backdrop` 工厂：优先尝试 GPU（GL 3.3 core + 着色器编译/链接），
失败时打日志并回退到 CPU 版（公共 API 完全一致）。

纯函数 :func:`composite_ambient` / :func:`ambient_contributions` 把五层的合成
逻辑抽成**无 GUI 依赖**的纯计算，使各层透明度带（floodlights ~8% / grass 3–5%
/ pitch ~2% / trophy ~2%）与「奖杯层不随时间变化」可被无头属性测试直接检查。

「世界杯粒子引擎」与「聚光灯横扫」也并入本合成器，由**同一个** FrameClock 心跳
驱动（复用 :meth:`_CompositorMixin._on_frame`，**不**新增任何定时器；全应用唯一
允许的额外定时器是 Hero 倒计时）：

* :class:`ParticleSpec` —— 受校验的粒子视图模型（数量 80–120；kind ∈ {dust,
  grass,glint}；参考帧率下每帧位移 0.1–0.3 px；不透明度 0.05–0.15）。
* :class:`ParticleEngine` —— CPU 回退用的精灵缓存粒子场，``step_particles(dt)``
  以帧缩放 ``dt * REF_FPS`` 推进，因此 30–240Hz 下推进状态一致（帧率无关）。
  GPU 路径则在片元着色器内**程序化**生成粒子（无逐粒子 Python 循环）。
  明确**排除**花瓣 / 樱花 / 雪 / 流星 / 网页小游戏式特效。
* 纯函数 :func:`floodlight_sweep` / :func:`sweep_positions` —— 两束径向光带
  左右横扫，周期 8s、合计不透明度 ≤ ~5%，位置由 FrameClock ``t`` 推导（帧率无关）。

对应需求：16.1–16.5、17.1–17.5、18.1–18.3、25.1–25.3、27.1–27.4
（设计 Property 4 / 5 / 6 / 7 / 8 / 9 / 21 / 22）。
"""
from __future__ import annotations

import logging
import math
import random
from array import array
from dataclasses import dataclass
from typing import Literal

from app.config import BACKDROP_PARTICLE_SCALE, BACKDROP_RENDER_SCALE, BG_IMAGE_PATH, LOW_PERF
from app.ui.design.frame_clock import REF_FPS, FrameClock
from app.ui.design.hud_theme import NIGHT_STADIUM, HudPalette

log = logging.getLogger(__name__)

# 背景重绘上限：氛围运动 ~60fps 足矣，无需跟随动效内核可能高达 240Hz 的心跳。
_BG_MIN_DT = 1.0 / 60.0

# ── 自定义背景图（仓库根目录「背景图.png」）懒加载缓存 ──
#   None  = 尚未尝试加载
#   False = 已尝试但文件缺失 / 加载失败（不再重试）
#   QPixmap = 加载成功的原图
_BG_PIXMAP = None


def has_background_image() -> bool:
    """是否存在可用的自定义背景图（供 MainWindow 决定渲染后端）。"""
    try:
        return BG_IMAGE_PATH.is_file()
    except OSError:
        return False


def load_background_image():
    """懒加载并缓存自定义背景图 ``背景图.png``；缺失/失败返回 ``None``。"""
    global _BG_PIXMAP
    if _BG_PIXMAP is None:
        from PyQt6.QtGui import QPixmap
        try:
            if BG_IMAGE_PATH.is_file():
                pm = QPixmap(str(BG_IMAGE_PATH))
                _BG_PIXMAP = pm if (pm is not None and not pm.isNull()) else False
            else:
                _BG_PIXMAP = False
        except Exception as exc:  # pragma: no cover - 损坏文件等
            log.warning("背景图加载失败：%s", exc)
            _BG_PIXMAP = False
    return _BG_PIXMAP or None

# ── OpenGL 枚举常量（避免依赖 PyOpenGL；这些是 GL 规范固定值）──
_GL_FLOAT = 0x1406
_GL_TRIANGLES = 0x0004
_GL_COLOR_BUFFER_BIT = 0x00004000


# ════════════════════════════════════════════════════════════════════
#  纯计算层 —— 五层氛围合成（无 Qt 依赖，可无头测试）
# ════════════════════════════════════════════════════════════════════
#
# 透明度带（设计 Property 7）：每一层的「不透明度权重」必须落在其规定带内。
# 这些常量是各层贡献的**上限权重**——层函数本身返回 [0,1] 的强度，乘以权重得到
# 实际贡献，因此任意像素处每层贡献都落在 [0, 权重] 内。
FLOODLIGHT_OPACITY = 0.08          # L2 泛光 ~8%
GRASS_OPACITY = 0.04               # L3 草皮 3–5%（取中值 4%）
GRASS_OPACITY_BAND = (0.03, 0.05)
PITCH_OPACITY = 0.02               # L4 中圈/中线 ~2%
TROPHY_OPACITY = 0.02              # L5 奖杯剪影 ~2%

# 渐变分段位置（与 GPU 着色器一致）。
_RAMP_SPLIT = 0.55


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def _hex_rgb(hexstr: str) -> tuple[float, float, float]:
    """``"#RRGGBB"`` → 归一化 ``(r, g, b)`` ∈ [0,1]。"""
    s = hexstr.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return (r, g, b)


def _hash21(x: float, y: float) -> float:
    """确定性 2D→1D 哈希噪声 ∈ [0,1)（与着色器同构，纯 Python 实现）。"""
    px = (x * 123.34) % 1.0
    py = (y * 345.45) % 1.0
    d = px * (px + 34.345) + py * (py + 34.345)
    px = (px + d) % 1.0
    py = (py + d) % 1.0
    return (px * py * 4096.0) % 1.0


def vertical_ramp(y: float, top: tuple, mid: tuple, bottom: tuple) -> tuple:
    """L1：三段竖向渐变。``y`` ∈ [0,1]（0=顶）。"""
    y = _clamp(y)
    if y <= _RAMP_SPLIT:
        t = y / _RAMP_SPLIT if _RAMP_SPLIT > 0 else 0.0
        a, b = top, mid
    else:
        t = (y - _RAMP_SPLIT) / (1.0 - _RAMP_SPLIT)
        a, b = mid, bottom
    t = _clamp(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def floodlight_pools(uv: tuple, t: float) -> float:
    """L2：顶部两片大面积径向泛光池的强度 ∈ [0,1]。

    随 ``t`` 极缓慢横向漂移（仅光斑位置变化，强度仍在 [0,1] 内）。
    """
    x, y = uv
    # 长宽无关的高斯光池；两片分居左右上方。
    c1x = 0.30 + 0.02 * math.sin(t * 0.18)
    c2x = 0.72 - 0.02 * math.sin(t * 0.18)
    cy = 0.16
    r = 0.42
    d1 = (x - c1x) ** 2 + (y - cy) ** 2
    d2 = (x - c2x) ** 2 + (y - cy) ** 2
    a = math.exp(-d1 / (2.0 * r * r)) + math.exp(-d2 / (2.0 * r * r))
    return _clamp(a)


def grass_noise(uv: tuple) -> float:
    """L3：草皮 / 场地噪声纹理强度 ∈ [0,1]（仅在画面下半部可见）。"""
    x, y = uv
    n = _hash21(x * 220.0, y * 220.0)
    # 仅在下半场显现草皮纹理，上半场（夜空）几乎为 0。
    field = _clamp((y - 0.45) / 0.55)
    return _clamp(n * field)


def pitch_markings(uv: tuple) -> float:
    """L4：透视中圈 + 中线强度 ∈ [0,1]。"""
    x, y = uv
    cx, cy = 0.5, 1.02
    # 透视半场中圈（被底边裁切的椭圆环）
    ex = (x - cx) / 0.22
    ey = (y - cy) / 0.16
    rr = math.sqrt(ex * ex + ey * ey)
    ring = max(0.0, 1.0 - abs(rr - 1.0) / 0.06)
    # 中线（水平细线，靠近场地中部）
    line = max(0.0, 1.0 - abs(y - 0.82) / 0.006) * _clamp((0.5 - abs(x - 0.5)) / 0.5)
    return _clamp(max(ring, line))


def trophy_silhouette(uv: tuple) -> float:
    """L5：居中大力神杯剪影强度 ∈ [0,1]。**纯位置函数，与时间无关。**"""
    x, y = uv
    dx = x - 0.5
    # 杯身（碗）：中部一个柔和椭圆斑。
    bowl_x = dx / 0.12
    bowl_y = (y - 0.46) / 0.14
    bowl = math.exp(-(bowl_x * bowl_x + bowl_y * bowl_y))
    # 底座：下方稍宽的柔和块。
    base_x = dx / 0.07
    base_y = (y - 0.66) / 0.05
    base = math.exp(-(base_x * base_x + base_y * base_y))
    return _clamp(max(bowl, base))


def ambient_contributions(uv: tuple, t: float, palette: HudPalette = NIGHT_STADIUM) -> dict:
    """返回各氛围层在 ``uv`` 处、时间 ``t`` 的**加权不透明度贡献**。

    每个值 = 层强度([0,1]) × 该层透明度带权重，因此恒落在 ``[0, 权重]`` 内：
    floodlight ∈ [0,0.08]，grass ∈ [0,0.04]，pitch ∈ [0,0.02]，trophy ∈ [0,0.02]。
    ``trophy`` 不依赖 ``t``（设计 Property 9）。供 Property 7 / 9 无头检查。
    """
    return {
        "floodlight": floodlight_pools(uv, t) * FLOODLIGHT_OPACITY,
        "grass": grass_noise(uv) * GRASS_OPACITY,
        "pitch": pitch_markings(uv) * PITCH_OPACITY,
        "trophy": trophy_silhouette(uv) * TROPHY_OPACITY,
    }


def composite_ambient(uv: tuple, t: float, palette: HudPalette = NIGHT_STADIUM) -> tuple:
    """逐像素合成 L1→L5，返回最终 ``(r, g, b)`` ∈ [0,1]。

    与 GPU 着色器、CPU 离屏缓冲使用**同一套**层序与权重，是「单一事实来源」。
    """
    top = _hex_rgb(palette.bg_top)
    mid = _hex_rgb(palette.bg_mid)
    bot = _hex_rgb(palette.bg_bottom)
    flood = _hex_rgb(palette.floodlight)
    grass_col = _hex_rgb(palette.bg_bottom)   # 草皮取底部墨绿提亮
    primary = _hex_rgb(palette.primary)
    accent = _hex_rgb(palette.accent)

    c = list(vertical_ramp(uv[1], top, mid, bot))                         # L1
    contrib = ambient_contributions(uv, t, palette)
    for i in range(3):
        c[i] += flood[i] * contrib["floodlight"]                         # L2
        c[i] += (0.6 * grass_col[i] + 0.4 * primary[i]) * contrib["grass"]  # L3
        c[i] += 1.0 * contrib["pitch"]                                   # L4 (白线)
        c[i] += accent[i] * contrib["trophy"]                            # L5
    return tuple(_clamp(v) for v in c)


# ════════════════════════════════════════════════════════════════════
#  世界杯粒子引擎 —— 类型化、受校验、帧率无关（设计 Property 4 / 5 / 6 / 21）
# ════════════════════════════════════════════════════════════════════
#
# 设计常量（与 GPU 着色器一致）。speed 单位为「参考帧率(60fps)下每帧位移像素」，
# 时间驱动改造后实际位移 = speed * dt * REF_FPS（帧缩放），故任意帧率观感一致。
PARTICLE_COUNT_MIN, PARTICLE_COUNT_MAX = 80, 120
PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX = 0.1, 0.3        # px/frame @ REF_FPS
PARTICLE_OPACITY_MIN, PARTICLE_OPACITY_MAX = 0.05, 0.15
PARTICLE_KINDS: tuple[str, str, str] = ("dust", "grass", "glint")

# 仅允许的三种粒子；下列「网页小游戏 / 浪漫风」特效被设计明确禁止（需求 17.5）。
BANNED_PARTICLE_KINDS: frozenset[str] = frozenset(
    {"petal", "petals", "sakura", "snow", "snowflake", "meteor", "meteors"}
)

# 粒子纵向位移以归一化高度推进；用一个固定参考高度把「px/frame」换算成归一化量，
# 使纯逻辑（与具体窗口尺寸无关）可被无头测试，并保持帧率无关的线性+取模推进。
PARTICLE_REF_HEIGHT = 1000.0


def default_particle_count() -> int:
    """按性能档位（``BACKDROP_PARTICLE_SCALE``）在 [80,120] 带内选一个数量。

    即便把粒子系数调到最低（0.1），数量仍恒落在设计带 [80,120] 内（需求 17.1）。
    """
    scale = _clamp(BACKDROP_PARTICLE_SCALE)
    span = PARTICLE_COUNT_MAX - PARTICLE_COUNT_MIN
    return int(round(PARTICLE_COUNT_MIN + span * scale))


@dataclass(frozen=True)
class ParticleSpec:
    """粒子视图模型（受校验）。

    描述粒子场的一类样本参数：数量、种类、参考帧率下每帧速度、不透明度。
    构造即校验，越界或非法 ``kind`` 抛 :class:`ValueError`（设计 Validation rules）。
    """

    count: int
    kind: Literal["dust", "grass", "glint"]
    speed_px_per_frame: float
    opacity: float

    def __post_init__(self) -> None:
        if not (PARTICLE_COUNT_MIN <= int(self.count) <= PARTICLE_COUNT_MAX):
            raise ValueError(
                f"ParticleSpec.count 必须落在 [{PARTICLE_COUNT_MIN},{PARTICLE_COUNT_MAX}]，得到 {self.count}"
            )
        # 先显式拒绝被设计排除的「网页小游戏 / 浪漫风」特效（需求 17.5），给出针对性报错。
        if isinstance(self.kind, str) and self.kind.strip().lower() in BANNED_PARTICLE_KINDS:
            raise ValueError(
                f"ParticleSpec.kind 禁止使用 {self.kind!r}：花瓣/樱花/雪/流星等"
                f"网页小游戏式特效被设计明确排除（需求 17.5），仅允许 {PARTICLE_KINDS}"
            )
        if self.kind not in PARTICLE_KINDS:
            raise ValueError(
                f"ParticleSpec.kind 必须 ∈ {PARTICLE_KINDS}（禁止花瓣/樱花/雪/流星），得到 {self.kind!r}"
            )
        if not (PARTICLE_SPEED_MIN <= float(self.speed_px_per_frame) <= PARTICLE_SPEED_MAX):
            raise ValueError(
                f"ParticleSpec.speed_px_per_frame 必须 ∈ [{PARTICLE_SPEED_MIN},{PARTICLE_SPEED_MAX}]，"
                f"得到 {self.speed_px_per_frame}"
            )
        if not (PARTICLE_OPACITY_MIN <= float(self.opacity) <= PARTICLE_OPACITY_MAX):
            raise ValueError(
                f"ParticleSpec.opacity 必须 ∈ [{PARTICLE_OPACITY_MIN},{PARTICLE_OPACITY_MAX}]，"
                f"得到 {self.opacity}"
            )


@dataclass
class _Particle:
    """单个粒子的运行时状态（归一化坐标，0=顶）。"""

    x: float          # 0..1
    y: float          # 0..1（0=顶，向上飘 → y 减小并环绕）
    speed: float      # px/frame @ REF_FPS ∈ [0.1,0.3]
    opacity: float    # ∈ [0.05,0.15]
    kind: str         # ∈ PARTICLE_KINDS
    phase: float      # 0..1，用于横向轻微漂移
    drift: float      # 横向漂移系数


class ParticleEngine:
    """CPU 回退用的「世界杯粒子引擎」：精灵缓存粒子场。

    * 数量恒落在 [80,120]（构造时把请求值夹到带内）。
    * 每个粒子的 ``speed`` ∈ [0.1,0.3]、``opacity`` ∈ [0.05,0.15]、
      ``kind`` ∈ {dust,grass,glint}（设计 Property 4 / 5 / 6）。
    * :meth:`step_particles` 用帧缩放 ``dt * REF_FPS`` 推进，纵向位移为
      **线性 + 取模环绕**，因此「等总时长、不同 dt 切分」推进到同一状态
      （帧率无关，设计 Property 21）。GPU 路径不用本类（着色器内程序化生成）。
    """

    def __init__(self, count: int | None = None, *, seed: int = 1,
                 ref_height: float = PARTICLE_REF_HEIGHT) -> None:
        requested = default_particle_count() if count is None else int(count)
        self._count = max(PARTICLE_COUNT_MIN, min(PARTICLE_COUNT_MAX, requested))
        self._ref_height = float(ref_height) if ref_height > 0 else PARTICLE_REF_HEIGHT
        rng = random.Random(seed)
        self._particles: list[_Particle] = []
        for i in range(self._count):
            self._particles.append(
                _Particle(
                    x=rng.random(),
                    y=rng.random(),
                    speed=PARTICLE_SPEED_MIN
                    + rng.random() * (PARTICLE_SPEED_MAX - PARTICLE_SPEED_MIN),
                    opacity=PARTICLE_OPACITY_MIN
                    + rng.random() * (PARTICLE_OPACITY_MAX - PARTICLE_OPACITY_MIN),
                    kind=PARTICLE_KINDS[i % len(PARTICLE_KINDS)],
                    phase=rng.random(),
                    drift=rng.uniform(-0.15, 0.15),
                )
            )

    # ── 可观察状态 ──────────────────────────────
    def active_count(self) -> int:
        return len(self._particles)

    @property
    def particles(self) -> list[_Particle]:
        return self._particles

    def spec_for(self, p: _Particle) -> ParticleSpec:
        """把某粒子的实例参数包装为受校验的 :class:`ParticleSpec`。"""
        return ParticleSpec(
            count=self._count, kind=p.kind,
            speed_px_per_frame=p.speed, opacity=p.opacity,
        )

    # ── 推进（帧率无关：线性 + 取模环绕）────────
    def step_particles(self, dt: float) -> None:
        """按真实经过时间 ``dt`` 推进所有粒子。

        帧缩放 ``fs = dt * REF_FPS``；纵向位移 ``speed * fs / ref_height``（归一化），
        以 ``% 1.0`` 环绕。取模在实数下满足结合律，故分多步小 dt 推进与一步大 dt
        推进结果一致（设计 Property 21）。``dt < 0`` 视为 0。
        """
        if dt <= 0.0:
            return
        fs = dt * REF_FPS
        h = self._ref_height
        for p in self._particles:
            p.y = (p.y - (p.speed * fs) / h) % 1.0
            p.phase = (p.phase + p.drift * fs / h) % 1.0


def default_particle_specs() -> tuple[ParticleSpec, ParticleSpec, ParticleSpec]:
    """三类粒子（dust/grass/glint）的代表性受校验 spec —— 供 UI / 测试取用。"""
    n = default_particle_count()
    return (
        ParticleSpec(count=n, kind="dust", speed_px_per_frame=0.15, opacity=0.10),
        ParticleSpec(count=n, kind="grass", speed_px_per_frame=0.10, opacity=0.07),
        ParticleSpec(count=n, kind="glint", speed_px_per_frame=0.25, opacity=0.13),
    )


# ════════════════════════════════════════════════════════════════════
#  聚光灯横扫 —— 两束径向光带左右横扫（设计 Property 8）
# ════════════════════════════════════════════════════════════════════
SWEEP_PERIOD = 8.0                  # 横扫周期 8s（需求 18.1）
SWEEP_OPACITY_CEIL = 0.05           # 合计不透明度 ≤ ~5%（需求 18.2）
SWEEP_LEFT, SWEEP_RIGHT = 0.15, 0.85   # 横扫左右端点（归一化 x）
SWEEP_RADIUS = 0.5                  # 光带横向高斯半径
# 单束峰值取 ceil/2，两束完全叠加时恰为 ceil；再统一 clamp 以确保 ≤ ceil。
SWEEP_BEAM_PEAK = SWEEP_OPACITY_CEIL / 2.0


def _ease_inout(p: float) -> float:
    """smoothstep 缓入缓出 ∈ [0,1]（与着色器 ``ease_inout`` 一致）。"""
    p = _clamp(p)
    return p * p * (3.0 - 2.0 * p)


def sweep_positions(t: float) -> tuple[float, float]:
    """返回两束光带在时间 ``t`` 的横向中心 ``(x1, x2)``（归一化 x）。

    位置仅取决于相位 ``(t mod 8)/8``，因此对任意 ``t`` 有
    ``sweep_positions(t) == sweep_positions(t + 8.0)``（周期 8s，需求 18.1）。
    """
    phase = (t % SWEEP_PERIOD) / SWEEP_PERIOD
    e = _ease_inout(phase)
    x1 = SWEEP_LEFT + (SWEEP_RIGHT - SWEEP_LEFT) * e         # 束 A：左→右
    x2 = SWEEP_RIGHT + (SWEEP_LEFT - SWEEP_RIGHT) * e        # 束 B：右→左
    return (x1, x2)


def _sweep_beam(uv: tuple, cx: float) -> float:
    """单束竖直径向光带在 ``uv`` 处的强度（横向高斯，峰值 ``SWEEP_BEAM_PEAK``）。"""
    dx = uv[0] - cx
    return SWEEP_BEAM_PEAK * math.exp(-(dx * dx) / (2.0 * SWEEP_RADIUS * SWEEP_RADIUS))


def floodlight_sweep(uv: tuple, t: float) -> float:
    """两束横扫光带在 ``uv``、时间 ``t`` 的**合计不透明度贡献** ∈ [0, 0.05]。

    位置由 FrameClock ``t`` 推导（帧率无关，需求 18.3）；合计经 clamp 后恒
    ≤ ``SWEEP_OPACITY_CEIL``（~5%，需求 18.2）。纯函数，供 Property 8 无头检查。
    """
    x1, x2 = sweep_positions(t)
    a = _sweep_beam(uv, x1) + _sweep_beam(uv, x2)
    return _clamp(a, 0.0, SWEEP_OPACITY_CEIL)


# ════════════════════════════════════════════════════════════════════
#  共享状态 / 行为混入 —— 保证两后端公共 API 与可观察状态完全一致
# ════════════════════════════════════════════════════════════════════
class _CompositorMixin:
    """两个后端共享的状态机：调色板 / 启停 / 暂停 / 帧时钟订阅 / 节流。

    不继承 ``QObject``，仅提供方法与状态字段，由各后端在 ``__init__`` 里调用
    :meth:`_init_state`。这样 GPU(QOpenGLWidget) 与 CPU(QWidget) 两条继承链都能
    复用同一套**可观察状态转移**（设计 Property 22）。
    """

    def _init_state(self, palette: HudPalette) -> None:
        self._palette: HudPalette = palette if _is_hud_palette(palette) else NIGHT_STADIUM
        self._clock = FrameClock.instance()
        self._t: float = 0.0
        self._bg_accum: float = 0.0
        self._enabled: bool = True     # 用户开关
        self._want_anim: bool = True   # 页面级暂停
        self._subscribed: bool = False
        # 世界杯粒子引擎：数量恒落在 [80,120]（设计 Property 4）。两后端都持有同一
        # 引擎以统一上报 active count；CPU 后端用它驱动精灵绘制并 step，GPU 后端
        # 在着色器内程序化生成粒子、不 step（见 _advance）。
        self._particles = ParticleEngine(seed=1)

    # ── 公共 API（两后端一致）────────────────────
    def set_palette(self, palette) -> None:
        """切换调色板。仅接受 :class:`HudPalette`；其它类型忽略（夜间球场单一主题）。"""
        if _is_hud_palette(palette):
            self._palette = palette
            self.update()

    def set_enabled(self, on: bool) -> None:
        """用户开关：关闭后背景静止（仍显示当前帧），动画 CPU/GPU 占用归零。"""
        self._enabled = bool(on)
        self._sync_subscription()
        self.update()

    def set_paused(self, paused: bool) -> None:
        """页面级暂停（如地球仪页持续自绘时临时停背景动画）。"""
        self._want_anim = not bool(paused)
        self._sync_subscription()

    # ── 可观察状态（供后端等价性测试 Property 22）──
    def is_enabled(self) -> bool:
        return self._enabled

    def is_paused(self) -> bool:
        return not self._want_anim

    def is_animating(self) -> bool:
        """当前是否已订阅帧时钟（即动画是否在推进）。"""
        return self._subscribed

    def palette_name(self) -> str:
        return self._palette.name

    def particle_count(self) -> int:
        """当前活动粒子数（恒 ∈ [80,120]，设计 Property 4）。"""
        return self._particles.active_count()

    def sweep_positions_now(self) -> tuple[float, float]:
        """当前帧两束横扫光带的横向中心（供调试 / 测试观察）。"""
        return sweep_positions(self._t)

    # ── 帧时钟订阅（引用计数自动启停）────────────
    def _should_run(self) -> bool:
        return (
            self._enabled and self._want_anim
            and self.isVisible() and not LOW_PERF
        )

    def _sync_subscription(self) -> None:
        run = self._should_run()
        if run and not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True
        elif not run and self._subscribed:
            self._safe_unsubscribe()

    def _safe_unsubscribe(self) -> None:
        """退订帧时钟；容忍解释器关停期 FrameClock C++ 对象已析构的竞态。"""
        try:
            self._clock.unsubscribe(self._on_frame)
        except RuntimeError:  # pragma: no cover - 仅发生在进程退出 teardown
            pass
        self._subscribed = False

    def _on_frame(self, t: float, dt: float) -> None:
        """帧时钟回调：累计 ``dt``，节流到 ~60fps 后推进时间/粒子并请求重绘。

        节流点上把**累计的真实 dt**（``self._bg_accum``）交给 :meth:`_advance`，
        既保证背景重绘 ~60fps，又让时间驱动的粒子推进按真实经过时间前进
        （帧率无关，需求 25.2 / 25.3）。运动仍只由这**唯一**的 FrameClock 驱动。
        """
        self._bg_accum += dt
        if self._bg_accum < _BG_MIN_DT:
            return
        step = self._bg_accum
        self._bg_accum = 0.0
        self._t = t
        self._advance(step)
        self.update()

    def _advance(self, step_dt: float) -> None:
        """按真实经过时间推进逐帧子系统。默认无操作（GPU 路径着色器内程序化）。"""
        # GPU 后端粒子在片元着色器内由 u_time 程序化生成，无需 Python 推进。

    # ── 生命周期（显示订阅 / 隐藏退订）────────────
    def _show_subscribe(self) -> None:
        self._sync_subscription()

    def _hide_unsubscribe(self) -> None:
        if self._subscribed:
            self._safe_unsubscribe()


def _is_hud_palette(palette) -> bool:
    """鸭子判定：是否为「夜间球场」HudPalette（具备渐变三色 + 强调色字段）。"""
    return all(
        hasattr(palette, attr)
        for attr in ("bg_top", "bg_mid", "bg_bottom", "primary", "floodlight", "accent")
    )


# ════════════════════════════════════════════════════════════════════
#  GPU 后端 —— QOpenGLWidget + 全屏三角形片元着色器
# ════════════════════════════════════════════════════════════════════
_VERT_SRC = """
#version 330 core
layout(location = 0) in vec2 a_pos;
out vec2 v_uv;
void main() {
    v_uv = a_pos * 0.5 + 0.5;          // 0..1
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""

# 片元着色器：逐像素合成 L1→L5。仅用 u_time / u_res / u_ramp / u_accents。
_FRAG_SRC = """
#version 330 core
in  vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;
uniform vec3  u_ramp[3];      // 0=top 1=mid 2=bottom
uniform vec3  u_accents[3];   // 0=primary 1=floodlight 2=accent

const float RAMP_SPLIT = 0.55;
const float FLOOD_OP = 0.08;
const float GRASS_OP = 0.04;
const float PITCH_OP = 0.02;
const float TROPHY_OP = 0.02;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

// L1 三段竖向渐变
vec3 vertical_ramp(float y) {
    vec3 c;
    if (y <= RAMP_SPLIT) c = mix(u_ramp[0], u_ramp[1], y / RAMP_SPLIT);
    else                 c = mix(u_ramp[1], u_ramp[2], (y - RAMP_SPLIT) / (1.0 - RAMP_SPLIT));
    return c;
}

// L2 顶部两片高斯泛光池
float floodlight_pools(vec2 uv, float t) {
    float c1x = 0.30 + 0.02 * sin(t * 0.18);
    float c2x = 0.72 - 0.02 * sin(t * 0.18);
    float cy = 0.16;
    float r = 0.42;
    float d1 = pow(uv.x - c1x, 2.0) + pow(uv.y - cy, 2.0);
    float d2 = pow(uv.x - c2x, 2.0) + pow(uv.y - cy, 2.0);
    float a = exp(-d1 / (2.0 * r * r)) + exp(-d2 / (2.0 * r * r));
    return clamp(a, 0.0, 1.0);
}

// L3 草皮噪声（仅下半场）
float grass_noise(vec2 uv) {
    float n = hash21(floor(uv * 220.0));
    float field = clamp((uv.y - 0.45) / 0.55, 0.0, 1.0);
    return clamp(n * field, 0.0, 1.0);
}

// L4 透视中圈 + 中线
float pitch_markings(vec2 uv) {
    vec2 c = vec2(0.5, 1.02);
    float ex = (uv.x - c.x) / 0.22;
    float ey = (uv.y - c.y) / 0.16;
    float rr = sqrt(ex * ex + ey * ey);
    float ring = max(0.0, 1.0 - abs(rr - 1.0) / 0.06);
    float line = max(0.0, 1.0 - abs(uv.y - 0.82) / 0.006)
                 * clamp((0.5 - abs(uv.x - 0.5)) / 0.5, 0.0, 1.0);
    return clamp(max(ring, line), 0.0, 1.0);
}

// L5 居中大力神杯剪影（与时间无关）
float trophy_silhouette(vec2 uv) {
    float dx = uv.x - 0.5;
    float bx = dx / 0.12;
    float by = (uv.y - 0.46) / 0.14;
    float bowl = exp(-(bx * bx + by * by));
    float sx = dx / 0.07;
    float sy = (uv.y - 0.66) / 0.05;
    float base = exp(-(sx * sx + sy * sy));
    return clamp(max(bowl, base), 0.0, 1.0);
}

// 聚光灯横扫：周期 8s、合计 ≤ ~5%，与 Python floodlight_sweep 同构
const float SWEEP_PERIOD = 8.0;
const float SWEEP_CEIL = 0.05;
const float SWEEP_LEFT = 0.15;
const float SWEEP_RIGHT = 0.85;
const float SWEEP_RADIUS = 0.5;
const float SWEEP_PEAK = 0.025;

float ease_inout(float p) { return p * p * (3.0 - 2.0 * p); }

float sweep_beam(vec2 uv, float cx) {
    float dx = uv.x - cx;
    return SWEEP_PEAK * exp(-(dx * dx) / (2.0 * SWEEP_RADIUS * SWEEP_RADIUS));
}

float floodlight_sweep(vec2 uv, float t) {
    float phase = mod(t, SWEEP_PERIOD) / SWEEP_PERIOD;
    float e = ease_inout(phase);
    float x1 = mix(SWEEP_LEFT, SWEEP_RIGHT, e);
    float x2 = mix(SWEEP_RIGHT, SWEEP_LEFT, e);
    return clamp(sweep_beam(uv, x1) + sweep_beam(uv, x2), 0.0, SWEEP_CEIL);
}

// 世界杯粒子引擎：程序化 dust/grass/glint（无逐粒子 CPU 循环）。
// 三层网格叠加 ~100 颗微粒，向上缓慢飘移；禁止花瓣/樱花/雪/流星。
// 每颗微粒不透明度落在 [0.05,0.15] 带内（与 ParticleSpec 同义）。
float particle_field(vec2 uv, float t) {
    float acc = 0.0;
    for (int gi = 0; gi < 3; gi++) {
        float fy = 9.0 + float(gi) * 4.0;            // 纵向网格密度
        vec2 g = vec2(uv.x * (fy * 0.6), uv.y * fy);
        vec2 cell = floor(g);
        vec2 f = fract(g);
        float h = hash21(cell + float(gi) * 31.7);
        float speed = 0.1 + h * 0.2;                 // 0.1..0.3 px/frame
        float px = 0.2 + 0.6 * hash21(cell + 4.3);
        float py = fract(hash21(cell + 9.1) - t * speed * 0.06);
        float d = distance(f, vec2(px, py));
        float op = 0.05 + 0.10 * hash21(cell + 7.7); // 0.05..0.15
        acc += op * smoothstep(0.07, 0.0, d);
    }
    return acc;
}

void main() {
    // 顶部为原点的 uv（与纯函数一致：y=0 顶）
    vec2 uv = vec2(v_uv.x, 1.0 - v_uv.y);
    float t = u_time;

    vec3 primary = u_accents[0];
    vec3 flood   = u_accents[1];
    vec3 accent  = u_accents[2];
    vec3 grassCol = mix(u_ramp[2], primary, 0.4);

    vec3 col = vertical_ramp(uv.y);                                  // L1
    col += flood   * floodlight_pools(uv, t) * FLOOD_OP;            // L2
    col += grassCol * grass_noise(uv) * GRASS_OP;                  // L3
    col += vec3(1.0) * pitch_markings(uv) * PITCH_OP;             // L4
    col += accent  * trophy_silhouette(uv) * TROPHY_OP;           // L5
    col += flood   * particle_field(uv, t);                       // 粒子引擎
    col += flood   * floodlight_sweep(uv, t);                     // 聚光灯横扫

    // 轻微暗角，增加纵深感（不属于五层，仅润色）
    float aspect = u_res.x / max(u_res.y, 1.0);
    float vig = smoothstep(1.2, 0.4, length((uv - 0.5) * vec2(aspect, 1.0)));
    col *= mix(0.86, 1.0, vig);

    fragColor = vec4(col, 1.0);
}
"""


def _make_gpu_class():
    """惰性构造 GPU 后端类（隔离 QtOpenGL 导入，便于无 GL 环境回退）。"""
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QOpenGLFunctions, QSurfaceFormat, QVector3D
    from PyQt6.QtOpenGL import (
        QOpenGLBuffer,
        QOpenGLShader,
        QOpenGLShaderProgram,
        QOpenGLVertexArrayObject,
    )
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    from PyQt6.QtWidgets import QSizePolicy

    class StageCompositor(QOpenGLWidget, _CompositorMixin):
        """GPU 版「夜间球场」舞台合成器（全屏三角形 + 片元着色器）。

        公共 API 与 :class:`StageCompositorCPU` 完全一致，可被 MainWindow 热插拔。
        着色器编译 / 链接失败时设置 ``_gl_ok=False``、发出 :data:`gpu_failed`
        并降级为静态清屏底色（不崩溃），MainWindow 可据此热切到 CPU 后端。
        """

        gpu_failed = pyqtSignal()

        def __init__(self, parent=None, palette: HudPalette = NIGHT_STADIUM) -> None:
            fmt = QSurfaceFormat()
            fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
            fmt.setVersion(3, 3)
            fmt.setSwapInterval(0)
            super().__init__(parent)
            self.setFormat(fmt)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            self._init_state(palette)

            self._program: QOpenGLShaderProgram | None = None
            self._vao = QOpenGLVertexArrayObject()
            self._vbo = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
            self._gl_ok = False
            self._glf: QOpenGLFunctions | None = None
            self._res = (1.0, 1.0)
            self._QVector3D = QVector3D

        # ── 生命周期 ────────────────────────────
        def showEvent(self, ev) -> None:
            super().showEvent(ev)
            self._show_subscribe()

        def hideEvent(self, ev) -> None:
            super().hideEvent(ev)
            self._hide_unsubscribe()

        # ── OpenGL ──────────────────────────────
        def _gl(self) -> "QOpenGLFunctions":
            """返回绑定到当前上下文的 QOpenGLFunctions（PyQt6 无 context().functions()）。"""
            f = self._glf
            if f is None:
                f = QOpenGLFunctions(self.context())
                f.initializeOpenGLFunctions()
                self._glf = f
            return f

        def initializeGL(self) -> None:
            # 上下文已就绪，初始化可复用的 GL 函数入口。
            self._glf = QOpenGLFunctions(self.context())
            self._glf.initializeOpenGLFunctions()

            prog = QOpenGLShaderProgram(self)
            ok = prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, _VERT_SRC)
            ok = prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, _FRAG_SRC) and ok
            ok = prog.link() and ok
            if not ok:
                log.warning("StageCompositor 着色器编译/链接失败，降级为静态底色：%s", prog.log())
                self._gl_ok = False
                self._program = None
                self.gpu_failed.emit()
                return

            self._program = prog
            verts = array("f", [-1.0, -1.0, 3.0, -1.0, -1.0, 3.0])  # 全屏三角形
            data = verts.tobytes()
            self._vao.create()
            self._vao.bind()
            self._vbo.create()
            self._vbo.bind()
            self._vbo.allocate(data, len(data))
            prog.bind()
            prog.enableAttributeArray(0)
            prog.setAttributeBuffer(0, _GL_FLOAT, 0, 2, 0)
            prog.release()
            self._vbo.release()
            self._vao.release()
            self._gl_ok = True

        def resizeGL(self, w: int, h: int) -> None:
            f = self._gl()
            f.glViewport(0, 0, max(1, w), max(1, h))
            self._res = (float(max(1, w)), float(max(1, h)))

        def paintGL(self) -> None:
            f = self._gl()
            top = _hex_rgb(self._palette.bg_top)
            f.glClearColor(top[0], top[1], top[2], 1.0)
            f.glClear(_GL_COLOR_BUFFER_BIT)
            if not self._gl_ok or self._program is None:
                return

            p = self._palette
            V = self._QVector3D
            prog = self._program
            prog.bind()
            self._vao.bind()

            prog.setUniformValue("u_time", float(self._t))
            prog.setUniformValue("u_res", float(self._res[0]), float(self._res[1]))
            # u_ramp[0..2]
            prog.setUniformValue("u_ramp[0]", V(*_hex_rgb(p.bg_top)))
            prog.setUniformValue("u_ramp[1]", V(*_hex_rgb(p.bg_mid)))
            prog.setUniformValue("u_ramp[2]", V(*_hex_rgb(p.bg_bottom)))
            # u_accents[0..2]
            prog.setUniformValue("u_accents[0]", V(*_hex_rgb(p.primary)))
            prog.setUniformValue("u_accents[1]", V(*_hex_rgb(p.floodlight)))
            prog.setUniformValue("u_accents[2]", V(*_hex_rgb(p.accent)))

            f.glDrawArrays(_GL_TRIANGLES, 0, 3)
            self._vao.release()
            prog.release()

    return StageCompositor


# ════════════════════════════════════════════════════════════════════
#  CPU 后端 —— QPainter 离屏低分缓冲 + 放大 blit
# ════════════════════════════════════════════════════════════════════
def _make_cpu_class():
    from PyQt6.QtCore import QRectF, QSize, Qt
    from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QRadialGradient
    from PyQt6.QtWidgets import QSizePolicy, QWidget

    def _qc(rgb: tuple, alpha: float = 1.0) -> QColor:
        c = QColor(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        c.setAlphaF(_clamp(alpha))
        return c

    class StageCompositorCPU(QWidget, _CompositorMixin):
        """CPU 回退版「夜间球场」舞台合成器。

        与 GPU 版**完全一致**的公共 API 与层序；用 ``QPainter`` 把 L1→L5 画进
        ``BACKDROP_RENDER_SCALE`` 低分离屏缓冲，再放大 blit 到整窗，显著降低
        全窗背景的栅格化开销。
        """

        def __init__(self, parent=None, palette: HudPalette = NIGHT_STADIUM) -> None:
            super().__init__(parent)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.lower()
            self._init_state(palette)
            self._buf = None  # QPixmap 离屏缓冲
            self._sprites: dict = {}  # kind → 缓存的粒子精灵 QPixmap
            self._bg_base = None       # 背景图「底图」缓存（等比铺满 + 可读性遮罩）
            self._bg_base_key = None   # 缓存键：(w, h, 调色板名)，变化时重建

        # ── 逐帧推进（粒子引擎；运动仍只由唯一 FrameClock 驱动）──
        def _advance(self, step_dt: float) -> None:
            self._particles.step_particles(step_dt)

        # ── 生命周期 ────────────────────────────
        def showEvent(self, ev) -> None:
            super().showEvent(ev)
            self._show_subscribe()

        def hideEvent(self, ev) -> None:
            super().hideEvent(ev)
            self._hide_unsubscribe()

        # ── 绘制 ────────────────────────────────
        def paintEvent(self, _ev) -> None:
            from PyQt6.QtGui import QPixmap

            w, h = self.width(), self.height()
            if w <= 1 or h <= 1:
                return
            scale = BACKDROP_RENDER_SCALE
            # 存在自定义背景图时，跳过低分离屏缓冲，直接全分辨率绘制，
            # 避免把照片先缩到 0.6 再放大造成的模糊（保持背景清晰）。
            if load_background_image() is not None:
                scale = 1.0
            if scale >= 0.99:
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                try:
                    self._paint_scene(p, w, h)
                finally:
                    p.end()
                return

            bw, bh = max(1, int(w * scale)), max(1, int(h * scale))
            if self._buf is None or self._buf.size() != QSize(bw, bh):
                self._buf = QPixmap(bw, bh)
            self._buf.fill(Qt.GlobalColor.transparent)
            bp = QPainter(self._buf)
            bp.setRenderHint(QPainter.RenderHint.Antialiasing)
            bp.scale(scale, scale)
            try:
                self._paint_scene(bp, w, h)
            finally:
                bp.end()
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            p.drawPixmap(self.rect(), self._buf)
            p.end()

        def _bg_base_pixmap(self, w: int, h: int, bg) -> "QPixmap":
            """返回缓存的背景「底图」（等比铺满的照片 + 烘焙好的可读性遮罩）。

            仅当窗口尺寸或调色板变化时重建；逐帧绘制只需对它做一次 blit，
            把「每帧平滑缩放 1.5MP 大图」的开销降为「每次 resize 一次」。
            """
            from PyQt6.QtGui import QPixmap
            key = (w, h, self._palette.name)
            if self._bg_base is not None and self._bg_base_key == key:
                return self._bg_base
            pal = self._palette
            base = QPixmap(w, h)
            base.fill(Qt.GlobalColor.black)
            bp = QPainter(base)
            bp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            iw, ih = bg.width(), bg.height()
            if iw > 0 and ih > 0:
                cover = max(w / iw, h / ih)
                dw, dh = iw * cover, ih * cover
                dx, dy = (w - dw) / 2.0, (h - dh) / 2.0
                bp.drawPixmap(QRectF(dx, dy, dw, dh), bg, QRectF(0, 0, iw, ih))
            ov = QLinearGradient(0.0, 0.0, 0.0, float(h))
            ov.setColorAt(0.0, _qc(_hex_rgb(pal.bg_top), 0.34))
            ov.setColorAt(0.5, _qc(_hex_rgb(pal.bg_mid), 0.42))
            ov.setColorAt(1.0, _qc(_hex_rgb(pal.bg_bottom), 0.58))
            bp.fillRect(QRectF(0, 0, w, h), ov)
            bp.end()
            self._bg_base = base
            self._bg_base_key = key
            return base

        def _paint_scene(self, p: "QPainter", w: int, h: int) -> None:
            pal = self._palette
            t = self._t
            rect = QRectF(0, 0, w, h)

            # ── 自定义背景图（背景图.png）优先 ──
            # 存在时作为底图铺满（等比覆盖、居中裁剪），叠加可读性遮罩，再点缀
            # 轻量氛围（粒子 + 聚光灯横扫），不渲染「夜间球场」程序化场景。
            #
            # 性能关键：把「缩放后的照片 + 可读性遮罩」**预合成并缓存**为底图，
            # 仅在尺寸/调色板变化时重建；逐帧只做一次廉价 blit + 轻量氛围层，
            # 避免每帧都对 1.5MP 大图做平滑缩放（那是卡顿的主因）。
            bg = load_background_image()
            if bg is not None and not bg.isNull():
                base = self._bg_base_pixmap(w, h, bg)
                if base is not None:
                    p.drawPixmap(0, 0, base)
                # 轻量氛围：仅保留上飘微粒（~0.2ms/帧）。原先的两束全窗径向「聚光灯
                # 横扫」在照片背景上几乎不可见，却占去 ~80% 的逐帧开销，故在背景图
                # 模式下省略，换取明显更顺滑的帧率。
                self._paint_particles(p, w, h)
                return

            # L1 三段竖向渐变
            g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            g.setColorAt(0.0, _qc(_hex_rgb(pal.bg_top)))
            g.setColorAt(_RAMP_SPLIT, _qc(_hex_rgb(pal.bg_mid)))
            g.setColorAt(1.0, _qc(_hex_rgb(pal.bg_bottom)))
            p.fillRect(rect, g)

            # L2 顶部两片泛光池（~8%）
            flood = _hex_rgb(pal.floodlight)
            cy = 0.16 * h
            r = 0.55 * max(w, h)
            for cxf in (0.30 + 0.02 * math.sin(t * 0.18), 0.72 - 0.02 * math.sin(t * 0.18)):
                cx = cxf * w
                rg = QRadialGradient(cx, cy, r)
                rg.setColorAt(0.0, _qc(flood, FLOODLIGHT_OPACITY))
                rg.setColorAt(1.0, _qc(flood, 0.0))
                p.fillRect(rect, rg)

            # L3 草皮纹理（下半场，~4%）—— 用底部墨绿提亮做柔和叠加
            grass = _hex_rgb(pal.bg_bottom)
            gg = QLinearGradient(rect.bottomLeft(), QRectF(0, h * 0.45, w, 1).topLeft())
            gg.setColorAt(0.0, _qc(grass, GRASS_OPACITY))
            gg.setColorAt(1.0, _qc(grass, 0.0))
            p.fillRect(rect, gg)

            # L4 中圈 + 中线（~2%，白）
            p.save()
            pen_col = _qc((1.0, 1.0, 1.0), PITCH_OPACITY)
            from PyQt6.QtGui import QPen
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(pen_col, 1.4))
            cx = w * 0.5
            base_y = h * 1.02
            from PyQt6.QtCore import QPointF
            p.drawEllipse(QPointF(cx, base_y), w * 0.22, h * 0.16)
            p.drawLine(QPointF(w * 0.3, h * 0.82), QPointF(w * 0.7, h * 0.82))
            p.restore()

            # L5 大力神杯剪影（~2%，金，静态）
            accent = _hex_rgb(pal.accent)
            from PyQt6.QtCore import QPointF
            bowl = QRadialGradient(QPointF(w * 0.5, h * 0.46), w * 0.12)
            bowl.setColorAt(0.0, _qc(accent, TROPHY_OPACITY))
            bowl.setColorAt(1.0, _qc(accent, 0.0))
            p.fillRect(rect, bowl)
            base = QRadialGradient(QPointF(w * 0.5, h * 0.66), w * 0.07)
            base.setColorAt(0.0, _qc(accent, TROPHY_OPACITY))
            base.setColorAt(1.0, _qc(accent, 0.0))
            p.fillRect(rect, base)

            # 粒子引擎（精灵缓存）—— dust/grass/glint，飘浮在场景之上
            self._paint_particles(p, w, h)

            # 聚光灯横扫（两束径向光带，合计 ≤ ~5%）
            flood_c = _hex_rgb(pal.floodlight)
            x1, x2 = sweep_positions(t)
            beam_r = 0.5 * max(w, h)
            for cxn in (x1, x2):
                rg = QRadialGradient(QPointF(cxn * w, h * 0.42), beam_r)
                rg.setColorAt(0.0, _qc(flood_c, SWEEP_BEAM_PEAK))
                rg.setColorAt(1.0, _qc(flood_c, 0.0))
                p.fillRect(rect, rg)

        def _particle_sprite(self, kind: str, color: tuple):
            """惰性构造并缓存某种粒子的精灵（小柔光点 / 短草叶 / 星芒）。"""
            from PyQt6.QtCore import QPointF, QRectF
            from PyQt6.QtGui import QPixmap, QRadialGradient

            cached = self._sprites.get(kind)
            if cached is not None:
                return cached
            size = 8
            spr = QPixmap(size, size)
            spr.fill(Qt.GlobalColor.transparent)
            sp = QPainter(spr)
            sp.setRenderHint(QPainter.RenderHint.Antialiasing)
            c = float(size) / 2.0
            if kind == "grass":
                # 短竖叶
                sp.setPen(_qc(color, 1.0))
                sp.drawLine(QPointF(c, 1.0), QPointF(c, size - 1.0))
            else:
                # dust / glint：柔光圆点（glint 更亮更集中）
                rg = QRadialGradient(QPointF(c, c), c)
                rg.setColorAt(0.0, _qc(color, 1.0))
                rg.setColorAt(1.0, _qc(color, 0.0))
                sp.setBrush(rg)
                sp.setPen(Qt.PenStyle.NoPen)
                sp.drawEllipse(QRectF(0, 0, size, size))
            sp.end()
            self._sprites[kind] = spr
            return spr

        def _paint_particles(self, p: "QPainter", w: int, h: int) -> None:
            flood_c = _hex_rgb(self._palette.floodlight)
            primary_c = _hex_rgb(self._palette.primary)
            accent_c = _hex_rgb(self._palette.accent)
            kind_color = {"dust": flood_c, "grass": primary_c, "glint": accent_c}
            p.save()
            for part in self._particles.particles:
                spr = self._particle_sprite(part.kind, kind_color.get(part.kind, flood_c))
                # 横向轻微漂移（用 phase），纵向由 step_particles 推进
                px = (part.x + 0.02 * math.sin(part.phase * 2.0 * math.pi)) * w
                py = part.y * h
                p.setOpacity(_clamp(part.opacity))
                p.drawPixmap(int(px), int(py), spr)
            p.setOpacity(1.0)
            p.restore()

    return StageCompositorCPU


# 惰性单例：首次访问时构造类（隔离 Qt 导入失败的环境）。
_GPU_CLS = None
_CPU_CLS = None


def _gpu_class():
    global _GPU_CLS
    if _GPU_CLS is None:
        _GPU_CLS = _make_gpu_class()
    return _GPU_CLS


def _cpu_class():
    global _CPU_CLS
    if _CPU_CLS is None:
        _CPU_CLS = _make_cpu_class()
    return _CPU_CLS


def _construct_gpu(palette: HudPalette, parent):
    """构造 GPU 后端实例（可能因缺少 QtOpenGL / 上下文而抛异常）。"""
    cls = _gpu_class()
    return cls(parent, palette=palette)


def _construct_cpu(palette: HudPalette, parent):
    cls = _cpu_class()
    return cls(parent, palette=palette)


# ════════════════════════════════════════════════════════════════════
#  工厂 —— 后端选择（GPU 优先，失败回退 CPU）
# ════════════════════════════════════════════════════════════════════
def create_backdrop(palette: HudPalette = NIGHT_STADIUM, *, parent=None, prefer_gpu: bool = True):
    """创建舞台合成器背景控件。

    ``prefer_gpu=True`` 时优先尝试 GPU（GL 3.3 core + 着色器）；构造失败
    （缺少 QtOpenGLWidgets / 无法创建上下文等）则打 warning 日志并回退到 CPU
    后端（公共 API 完全一致）。对应需求 27.1 / 27.2、设计 Property 22。
    """
    if prefer_gpu:
        try:
            bd = _construct_gpu(palette, parent)
            log.info("舞台合成器渲染后端：GPU (GLSL / QOpenGLWidget)")
            return bd
        except Exception as exc:  # 缺少 QtOpenGL / 构造失败 → 降级
            log.warning("GPU 舞台合成器初始化失败，降级为 CPU 后端：%s", exc)
    return _construct_cpu(palette, parent)
