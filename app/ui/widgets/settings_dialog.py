"""设置对话框 —— 顶部栏「⚙ 设置」按钮打开。

旧版「设置」按钮没有任何点击回调（点了没反应），这里补上一个真正可用的
设置面板：

* **主题皮肤**：可视化色板预览卡，点击即实时切换全部动态皮肤
  （与顶栏 🎨 菜单同源）。每张卡用真实调色板绘制「背景 + 主色 + 辅色 +
  点缀色」缩略，所见即所得。
* **数据缓存**：一键清空本地 JSON 缓存并强制刷新当前页。
* **关于**：应用名 / 版本 / 数据来源。
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import __app_name__, __version__
from app.i18n import tr
from app.ui.design.app_cursor import pointing_hand_cursor
from app.ui.theme import THEME_META, THEME_ORDER, THEMES

_DIALOG_QSS = """
QDialog { background: #0B1020; }
QLabel { color: #FFFFFF; }
QPushButton {
    background: rgba(255,255,255,0.06); color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.16); border-radius: 12px;
    padding: 9px 18px; font-size: 12.5px; font-weight: 700;
}
QPushButton:hover { background: rgba(0,191,255,0.20); border: 1px solid #00BFFF; }
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00BFFF, stop:1 #6A5ACD);
    color: #ffffff; border: none;
}
QPushButton#primary:hover { background: #46D2FF; }
QPushButton[fpsBtn="true"] {
    font-size: 13px; font-weight: 800; padding: 4px;
}
QPushButton[fpsBtn="true"]:checked {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(0,191,255,0.34), stop:1 rgba(106,90,205,0.18));
    border: 1px solid #00BFFF; color: #ffffff;
}
"""


def _section_title(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setStyleSheet("font-size:13px; font-weight:900; color:#00BFFF;")
    return lab


def _hline() -> QFrame:
    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet("background: rgba(255,255,255,0.10);")
    return line


class _SkinSwatch(QFrame):
    """单个皮肤预览卡：真实调色板绘制的缩略图 + 名称 + 选中态高亮。"""

    clicked = pyqtSignal(str)

    def __init__(self, theme_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._key = theme_key
        self._selected = False
        self._hover = False
        self._palette = THEMES.get(theme_key, THEMES["dark"])
        zh, emoji, desc = THEME_META.get(theme_key, (theme_key, "🎨", ""))
        self._zh = zh
        self._emoji = emoji
        self._desc = desc
        self.setFixedSize(196, 96)
        self.setCursor(pointing_hand_cursor())
        self.setMouseTracking(True)

    def set_selected(self, on: bool) -> None:
        if on != self._selected:
            self._selected = on
            self.update()

    def enterEvent(self, ev) -> None:
        self._hover = True
        self.update()
        super().enterEvent(ev)

    def leaveEvent(self, ev) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(ev)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._key)
        super().mousePressEvent(ev)

    def paintEvent(self, _ev) -> None:
        t = self._palette
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)
        p.setClipPath(path)

        # 背景：调色板的主背景 → 卡片背景渐变
        bg = QLinearGradient(rect.topLeft(), rect.bottomRight())
        bg.setColorAt(0.0, QColor(t.bg))
        bg.setColorAt(1.0, QColor(t.bg_elevated))
        p.fillRect(rect, bg)

        # 主色斜带（模拟选中态高亮条）
        band = QLinearGradient(rect.topLeft(), rect.topRight())
        band.setColorAt(0.0, QColor(t.primary))
        band.setColorAt(1.0, QColor(t.primary_hover))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(band)
        p.drawRect(QRectF(rect.left(), rect.top(), rect.width(), 6))

        # 三个点缀色圆点（primary / secondary / accent）
        dot_y = rect.top() + 26
        for i, col in enumerate((t.primary, t.secondary, t.accent)):
            cx = rect.left() + 18 + i * 20
            p.setBrush(QColor(col))
            p.drawEllipse(QRectF(cx - 6, dot_y - 6, 12, 12))

        p.setClipping(False)

        # 文案
        p.setPen(QColor(t.text))
        f = p.font(); f.setBold(True); f.setPointSize(11)
        p.setFont(f)
        p.drawText(
            QRectF(rect.left() + 14, rect.top() + 44, rect.width() - 28, 22),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{self._emoji}  {self._zh}",
        )
        p.setPen(QColor(t.text_dim))
        f2 = p.font(); f2.setBold(False); f2.setPointSize(8)
        p.setFont(f2)
        p.drawText(
            QRectF(rect.left() + 14, rect.top() + 66, rect.width() - 28, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._desc,
        )

        # 边框：选中 = 主色粗描边；悬停 = 浅白；默认 = 暗描边
        if self._selected:
            pen = QPen(QColor(t.primary), 2.5)
        elif self._hover:
            pen = QPen(QColor(255, 255, 255, 90), 1.5)
        else:
            pen = QPen(QColor(255, 255, 255, 28), 1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 14, 14)

        # 选中态：右上角对勾徽章
        if self._selected:
            badge_r = 11.0
            bx = rect.right() - badge_r - 8
            by = rect.top() + badge_r + 12
            p.setBrush(QColor(t.primary))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(bx - badge_r, by - badge_r, badge_r * 2, badge_r * 2))
            p.setPen(QPen(QColor("#ffffff"), 2.0))
            p.drawLine(int(bx - 4), int(by), int(bx - 1), int(by + 4))
            p.drawLine(int(bx - 1), int(by + 4), int(bx + 5), int(by - 4))


class SettingsDialog(QDialog):
    """应用设置面板。"""

    theme_selected = pyqtSignal(str)   # 选中的皮肤 theme key
    fps_selected = pyqtSignal(int)     # 选中的动画帧率
    bg_anim_toggled = pyqtSignal(bool)  # 动态背景动画 开 / 关
    backend_selected = pyqtSignal(bool)  # 渲染后端：True=GPU(GLSL) / False=CPU
    cache_cleared = pyqtSignal()       # 用户点击「清空缓存」

    # 仅提供能「真实达成」的档位。240 已移除：CPU 渲染下无法稳定喂满，徒有
    # 高数字却卡顿；144 是单线程顺滑上限（详见 FrameClock.FPS_MAX 说明）。
    _FPS_CHOICES: tuple[tuple[int, str], ...] = (
        (60, "60\n标准"),
        (90, "90\n顺滑"),
        (120, "120\n流畅"),
        (144, "144\n电竞"),
    )

    def __init__(
        self,
        current_theme: str,
        current_fps: int = 60,
        parent: QWidget | None = None,
        current_bg_anim: bool = True,
        current_gpu_bg: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("设置"))
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(_DIALOG_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)

        title = QLabel("⚙  " + tr("设置"))
        title.setStyleSheet("font-size:20px; font-weight:900; color:#ffffff;")
        root.addWidget(title)

        # 注：「主题皮肤」三选一切换已移除 —— 应用统一使用单一夜间球场背景
        # （存在自定义背景图时以其为底图），无需多套皮肤。

        # ── 动画帧率 ──────────────────────────
        root.addWidget(_section_title(
            tr("动画帧率  ·  越高越顺滑（更耗 CPU）",
               "Animation FPS  ·  higher = smoother (more CPU)")))
        fps_row = QHBoxLayout()
        fps_row.setSpacing(10)
        self._fps_btns: dict[int, QPushButton] = {}
        for fps, label in self._FPS_CHOICES:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(pointing_hand_cursor())
            btn.setMinimumHeight(48)
            btn.setProperty("fpsBtn", True)
            btn.clicked.connect(lambda _c=False, f=fps: self._on_fps_clicked(f))
            self._fps_btns[fps] = btn
            fps_row.addWidget(btn, 1)
        root.addLayout(fps_row)
        self._select_fps_button(current_fps)

        root.addWidget(_hline())

        # ── 动态背景 ──────────────────────────
        root.addWidget(_section_title(
            tr("动态背景  ·  关闭可显著降低 CPU、提升流畅度",
               "Dynamic background  ·  turn off to cut CPU & boost smoothness")))
        bg_hint = QLabel(tr(
            "若界面卡顿，建议关闭动态背景（仅保留静态渐变，不影响功能）。",
            "If the UI stutters, turn off the dynamic background "
            "(static gradient only; no feature loss)."))
        bg_hint.setStyleSheet("color:#B0BEC5; font-size:11.5px;")
        bg_hint.setWordWrap(True)
        root.addWidget(bg_hint)
        bg_row = QHBoxLayout()
        bg_row.setSpacing(10)
        self._bg_btns: dict[bool, QPushButton] = {}
        for on, label in ((True, "开启\n炫彩"), (False, "关闭\n性能优先")):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(pointing_hand_cursor())
            btn.setMinimumHeight(48)
            btn.setProperty("fpsBtn", True)
            btn.clicked.connect(lambda _c=False, v=on: self._on_bg_clicked(v))
            self._bg_btns[on] = btn
            bg_row.addWidget(btn, 1)
        root.addLayout(bg_row)
        self._select_bg_button(bool(current_bg_anim))

        root.addWidget(_hline())

        # ── 渲染后端 ──────────────────────────
        root.addWidget(_section_title(
            tr("渲染后端  ·  GPU 把背景交给显卡，解放主线程",
               "Render backend  ·  GPU offloads the background, frees the main thread")))
        backend_hint = QLabel(tr(
            "CPU：QPainter 软件栅格化，跨平台最稳。\n"
            "GPU：GLSL 片元着色器渲染，主线程仅上传参数，可跑满高帧率并解锁真模糊/辉光"
            "（需 OpenGL 3.3；不可用时自动回退 CPU）。",
            "CPU: QPainter software rasterization, the most portable.\n"
            "GPU: GLSL fragment-shader rendering; the main thread only uploads "
            "uniforms, enabling high frame rates and real blur/glow "
            "(needs OpenGL 3.3; falls back to CPU automatically)."))
        backend_hint.setStyleSheet("color:#B0BEC5; font-size:11.5px;")
        backend_hint.setWordWrap(True)
        root.addWidget(backend_hint)
        backend_row = QHBoxLayout()
        backend_row.setSpacing(10)
        self._backend_btns: dict[bool, QPushButton] = {}
        for gpu, label in ((False, "CPU\n稳定"), (True, "GPU\n极致")):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(pointing_hand_cursor())
            btn.setMinimumHeight(48)
            btn.setProperty("fpsBtn", True)
            btn.clicked.connect(lambda _c=False, v=gpu: self._on_backend_clicked(v))
            self._backend_btns[gpu] = btn
            backend_row.addWidget(btn, 1)
        root.addLayout(backend_row)
        self._select_backend_button(bool(current_gpu_bg))

        root.addWidget(_hline())

        # ── 数据缓存 ──────────────────────────
        root.addWidget(_section_title(tr("数据缓存", "Data cache")))
        cache_hint = QLabel(tr("清空本地接口缓存后将重新拉取最新数据。",
                               "Clearing the local API cache re-fetches the latest data."))
        cache_hint.setStyleSheet("color:#B0BEC5; font-size:11.5px;")
        cache_hint.setWordWrap(True)
        root.addWidget(cache_hint)
        clear_btn = QPushButton(tr("🗑  清空缓存并刷新", "🗑  Clear cache & refresh"))
        clear_btn.setCursor(pointing_hand_cursor())
        clear_btn.clicked.connect(self._on_clear_cache)
        self._clear_btn = clear_btn
        root.addWidget(clear_btn)

        root.addWidget(_hline())

        # ── 关于 ──────────────────────────────
        root.addWidget(_section_title(tr("关于", "About")))
        about = QLabel(
            f"{__app_name__}  ·  v{__version__}\n"
            + tr("数据来源：懂球帝公开接口", "Data source: Dongqiudi public API") + "\n"
            + tr("国旗图源：本地内置位图（assets/flags）",
                 "Flags: bundled local bitmaps (assets/flags)")
        )
        about.setStyleSheet("color:#9AA3BE; font-size:11.5px;")
        root.addWidget(about)

        # ── 底部按钮 ──────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        close_btn = QPushButton(tr("完成", "Done"))
        close_btn.setObjectName("primary")
        close_btn.setCursor(pointing_hand_cursor())
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    # ── 事件 ─────────────────────────────────
    def _select_fps_button(self, fps: int) -> None:
        # 选最接近的档位高亮
        choices = [f for f, _ in self._FPS_CHOICES]
        nearest = min(choices, key=lambda f: abs(f - int(fps)))
        for f, btn in self._fps_btns.items():
            btn.setChecked(f == nearest)

    def _on_fps_clicked(self, fps: int) -> None:
        self._select_fps_button(fps)
        self.fps_selected.emit(fps)

    def _select_bg_button(self, on: bool) -> None:
        for v, btn in self._bg_btns.items():
            btn.setChecked(v == on)

    def _on_bg_clicked(self, on: bool) -> None:
        self._select_bg_button(on)
        self.bg_anim_toggled.emit(on)

    def _select_backend_button(self, gpu: bool) -> None:
        for v, btn in self._backend_btns.items():
            btn.setChecked(v == gpu)

    def _on_backend_clicked(self, gpu: bool) -> None:
        self._select_backend_button(gpu)
        self.backend_selected.emit(gpu)

    def _on_clear_cache(self) -> None:
        self.cache_cleared.emit()
        self._clear_btn.setText(tr("✅  已清空缓存", "✅  Cache cleared"))
        self._clear_btn.setEnabled(False)
