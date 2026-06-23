"""GLBackdrop —— GPU(GLSL) 版全局动态背景层。

为什么会有这个文件
-------------------
现有的 :class:`~app.ui.widgets.skin_backdrop.SkinBackdrop` 是 **CPU 软件栅格化**
（QPainter raster engine）：渐变、光晕、聚光灯、粒子全部在主线程逐像素绘制。
它已经被优化到该范式的极限（帧时钟 / 30fps 节流 / 离屏低分缓冲 / 精灵缓存 /
粒子裁剪），继续在 Python 层抠循环收益已经很小 —— 真正的天花板是 CPU raster，
而不是 Python。

本模块把同一套视觉搬到 **GPU**：用一个铺满整窗的全屏三角形 + 片元着色器
(``#version 330``)，渐变 / 光晕 / 聚光灯 / 粒子 / 辉光全部在 GPU 上逐像素并行计算。
Python 每帧只上传十几个浮点 uniform（时间、分辨率、当前皮肤配色），GIL 不再
参与逐像素工作 —— 主线程被彻底解放，滚动 / 点击因此更顺滑，且能轻松跑满高帧率。

* 粒子是 **程序化生成**（着色器内 hash 噪声 + 错峰闪烁），完全没有逐粒子的
  Python for 循环，也不需要 numpy —— 零新增依赖。
* 公共 API 与 ``SkinBackdrop`` 完全一致（``set_palette`` / ``set_enabled`` /
  ``set_paused``），因此可在主窗口里热插拔、与 CPU 版并排对比。
* 着色器编译 / 链接失败时自动降级为静态清屏底色（并打日志），不会崩溃。

如何启用
--------
``WC_GPU_BG=1`` 环境变量，或在「设置 → 渲染后端」里切到「GPU」。
"""
from __future__ import annotations

import logging
from array import array

from PyQt6.QtGui import QColor, QSurfaceFormat
from PyQt6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import Qt

from app.config import LOW_PERF
from app.ui.design.frame_clock import FrameClock
from app.ui.theme import DARK, ThemePalette

log = logging.getLogger(__name__)

# ── OpenGL 枚举常量（避免依赖 PyOpenGL；这些值是 GL 规范固定值）──
_GL_FLOAT = 0x1406
_GL_TRIANGLES = 0x0004
_GL_COLOR_BUFFER_BIT = 0x00004000

# 背景重绘上限：氛围运动 60fps 足矣，不必跟动效内核的 240Hz。
_BG_MIN_DT = 1.0 / 60.0


# ──────────────────────────────────────────────────────────────────
#  着色器源码
# ──────────────────────────────────────────────────────────────────
_VERT_SRC = """
#version 330 core
layout(location = 0) in vec2 a_pos;
out vec2 v_uv;
void main() {
    v_uv = a_pos * 0.5 + 0.5;          // 0..1
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""

_FRAG_SRC = """
#version 330 core
in  vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;
uniform vec3  u_top;        // 渐变上
uniform vec3  u_mid;        // 渐变中
uniform vec3  u_bot;        // 渐变下
uniform vec3  u_primary;    // 主色
uniform vec3  u_secondary;  // 辅色（光晕）
uniform vec3  u_accent;     // 点缀色

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}
vec2 hash22(vec2 p) {
    float n = hash21(p);
    return vec2(n, hash21(p + n));
}

// 柔和径向光晕（高斯衰减）
float glow(vec2 uv, vec2 c, float r) {
    float d = length(uv - c);
    return exp(-(d * d) / (2.0 * r * r));
}

// 程序化粒子层：错峰闪烁 + 缓慢上浮，纯 GPU，无逐粒子 CPU 循环
float particles(vec2 uv, float t, float density, float speed, float size) {
    uv.y += t * speed;                       // 向上漂移
    uv.x += sin(uv.y * 3.0 + t) * 0.02;      // 轻微横向摆动
    vec2 gv = uv * density;
    vec2 id = floor(gv);
    vec2 fv = fract(gv);
    float acc = 0.0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 o = vec2(float(x), float(y));
            vec2 cid = id + o;
            float present = step(0.55, hash21(cid * 1.7 + 5.1));  // 稀疏化
            vec2 pp = o + hash22(cid) * 0.9 + 0.05;
            float d = length(fv - pp);
            float tw = 0.5 + 0.5 * sin(t * 2.4 + hash21(cid) * 6.2831);  // 闪烁
            acc += present * smoothstep(size, 0.0, d) * tw;
        }
    }
    return acc;
}

// 顶部摆动聚光灯光锥
float beam(vec2 uv, float baseX, float sway, float t) {
    float y = uv.y;                          // 0 顶 -> 1 底
    float cx = baseX + sway * sin(t) * (0.2 + y * 0.8);
    float halfw = mix(0.015, 0.16, y);       // 向下扩散
    float d = abs(uv.x - cx) / halfw;
    return smoothstep(1.0, 0.0, d) * (1.0 - y * 0.85);
}

void main() {
    // 顶部为原点的 uv；auv 做长宽比校正，让光晕是正圆
    vec2 uv = vec2(v_uv.x, 1.0 - v_uv.y);
    float aspect = u_res.x / max(u_res.y, 1.0);
    vec2 auv = vec2(uv.x * aspect, uv.y);

    // L1 三段竖向渐变
    vec3 col = mix(u_top, u_mid, smoothstep(0.0, 0.55, uv.y));
    col = mix(col, u_bot, smoothstep(0.55, 1.0, uv.y));

    float t = u_time;

    // L2 缓慢漂移的大面积径向光晕（辅色左上 + 主色右下）
    vec2 g1 = vec2((0.24 + 0.03 * sin(t * 0.18)) * aspect, 0.18 + 0.03 * cos(t * 0.15));
    vec2 g2 = vec2((0.82 - 0.03 * sin(t * 0.18)) * aspect, 0.30 + 0.03 * cos(t * 0.15));
    col += u_secondary * glow(auv, g1, 0.42) * 0.45;
    col += u_primary   * glow(auv, g2, 0.36) * 0.34;

    // L4 摆动聚光灯（冷白，略染主色）
    vec3 lightTint = mix(vec3(0.85, 0.94, 1.0), u_primary, 0.25);
    col += lightTint * beam(uv, 0.26, 0.10, t * 0.57) * 0.10;
    col += lightTint * beam(uv, 0.74, 0.10, t * 0.57 + 3.14159) * 0.10;

    // L5 程序化粒子（远处星点 + 近处柔光，两层）
    float pf = particles(uv,            t, 14.0, 0.012, 0.06);
    float pn = particles(uv * 1.3 + 11.3, t,  8.0, 0.020, 0.10);
    col += mix(u_primary, vec3(1.0), 0.6) * pf * 0.50;
    col += u_accent * pn * 0.25;

    // L6 底部辉光呼吸
    float breathe = 0.5 + 0.5 * sin(t * 0.9);
    col += u_primary * glow(auv, vec2(0.5 * aspect, 1.06), 0.5) * (0.18 + 0.10 * breathe);

    // 轻微暗角，增加纵深的高级感
    float vig = smoothstep(1.15, 0.35, length((uv - 0.5) * vec2(aspect, 1.0)));
    col *= mix(0.82, 1.0, vig);

    fragColor = vec4(col, 1.0);
}
"""


def _rgb(hexstr: str) -> tuple[float, float, float]:
    """'#RRGGBB' -> 归一化 (r, g, b)，供 GL uniform。"""
    c = QColor(hexstr)
    return (c.redF(), c.greenF(), c.blueF())


class GLBackdrop(QOpenGLWidget):
    """GPU 版整窗动态背景。API 与 :class:`SkinBackdrop` 对齐，可热插拔。"""

    def __init__(self, parent=None, palette: ThemePalette | None = None) -> None:
        # 请求 3.3 Core Profile 上下文，配合 #version 330 着色器
        fmt = QSurfaceFormat()
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setVersion(3, 3)
        fmt.setSwapInterval(0)  # 不让 swap 阻塞 GUI 线程（我们自己用帧时钟节流）
        super().__init__(parent)
        self.setFormat(fmt)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._palette: ThemePalette = palette or DARK

        # GL 资源（在 initializeGL 中创建）
        self._program: QOpenGLShaderProgram | None = None
        self._vao = QOpenGLVertexArrayObject()
        self._vbo = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        self._gl_ok = False
        self._res = (1.0, 1.0)

        # 动效内核（与 CPU 版共用同一个全局帧时钟）
        self._clock = FrameClock.instance()
        self._t = 0.0
        self._bg_accum = 0.0
        self._enabled = True     # 用户开关
        self._want_anim = True   # 页面级暂停
        self._subscribed = False

    # ─── 公共 API（与 SkinBackdrop 对齐）──────────────
    def set_palette(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.update()

    def set_paused(self, paused: bool) -> None:
        self._want_anim = not paused
        self._sync_subscription()

    def set_enabled(self, on: bool) -> None:
        """关闭后背景静止（仍显示当前帧的渐变/光晕），动画 CPU 占用归零。"""
        self._enabled = bool(on)
        self._sync_subscription()
        self.update()

    # ─── 订阅（自动启停）──────────────────────────────
    def _sync_subscription(self) -> None:
        run = (
            self._enabled and self._want_anim
            and self.isVisible() and not LOW_PERF
        )
        if run and not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True
        elif not run and self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        self._sync_subscription()

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    def _on_frame(self, t: float, dt: float) -> None:
        # 背景重绘节流到 ~60fps（运动是时间驱动，观感不受影响）
        self._bg_accum += dt
        if self._bg_accum < _BG_MIN_DT:
            return
        self._bg_accum = 0.0
        self._t = t
        self.update()

    # ─── OpenGL 生命周期 ──────────────────────────────
    def initializeGL(self) -> None:
        prog = QOpenGLShaderProgram(self)
        ok = prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, _VERT_SRC)
        ok = prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, _FRAG_SRC) and ok
        ok = prog.link() and ok
        if not ok:
            log.warning("GLBackdrop 着色器编译/链接失败，降级为静态底色：%s", prog.log())
            self._gl_ok = False
            self._program = None
            return

        self._program = prog

        # 全屏三角形（覆盖整个裁剪空间，超出部分被裁掉）
        verts = array("f", [-1.0, -1.0, 3.0, -1.0, -1.0, 3.0])
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
        f = self.context().functions()
        f.glViewport(0, 0, max(1, w), max(1, h))
        self._res = (float(max(1, w)), float(max(1, h)))

    def paintGL(self) -> None:
        f = self.context().functions()
        top = _rgb(self._palette.hero_grad_a)
        f.glClearColor(top[0], top[1], top[2], 1.0)
        f.glClear(_GL_COLOR_BUFFER_BIT)

        if not self._gl_ok or self._program is None:
            return

        p = self._palette
        prog = self._program
        prog.bind()
        self._vao.bind()

        prog.setUniformValue("u_time", float(self._t))
        prog.setUniformValue("u_res", float(self._res[0]), float(self._res[1]))
        prog.setUniformValue("u_top", *_rgb(p.hero_grad_a))
        prog.setUniformValue("u_mid", *_rgb(p.hero_grad_b))
        prog.setUniformValue("u_bot", *_rgb(p.hero_grad_c))
        prog.setUniformValue("u_primary", *_rgb(p.primary))
        prog.setUniformValue("u_secondary", *_rgb(p.secondary))
        prog.setUniformValue("u_accent", *_rgb(p.accent))

        f.glDrawArrays(_GL_TRIANGLES, 0, 3)

        self._vao.release()
        prog.release()
