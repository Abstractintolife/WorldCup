"""零碎控件：卡片、分隔线、加载圈、状态徽章、数字动画、金色数字。"""
from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.design.animation_manager import anim as _anim
from app.ui.design.frame_clock import FrameClock


# ─────────────── 卡片 ───────────────
class Card(QFrame):
    """带圆角和可选阴影的容器。

    设计修订（v2）
    --------------
    * **使用 ``WA_StyledBackground`` + QSS 渲染圆角玻璃底**，靠 QSS 的
      ``border-radius`` 即可裁剪显示区域。
    * 阴影改为可选 —— 当卡片要作为 ``QScrollArea`` 的内容宿主时，由
      调用方传 ``shadow=False`` 关闭，避免 ``QGraphicsDropShadowEffect``
      与 ``setWidget()`` 配合时出现「整张卡片被涂成单色」的渲染 bug。
    * 悬停辉光仍可用，但只在阴影开启时生效。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        shadow: bool = True,
        padding: int = 16,
        hover: bool = True,
        glow_color: str = "#00BFFF",
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(padding, padding, padding, padding)

        self._shadow: QGraphicsDropShadowEffect | None = None
        self._base_blur = 28
        self._peak_blur = 52
        self._glow = QColor(glow_color)
        self._hover_enabled = hover and shadow
        self._hover_anim: QPropertyAnimation | None = None
        self._offset_anim: QPropertyAnimation | None = None

        if shadow:
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(self._base_blur)
            eff.setOffset(0, 6)
            eff.setColor(QColor(0, 0, 0, 100))
            self.setGraphicsEffect(eff)
            self._shadow = eff

    def set_glow_color(self, color: str) -> None:
        self._glow = QColor(color)

    # ── 悬停辉光 ─────────────────────────────
    def _valid_shadow(self) -> "QGraphicsDropShadowEffect | None":
        if not self._hover_enabled:
            return None
        cur = self._shadow
        try:
            if cur is not None and self.graphicsEffect() is cur:
                cur.blurRadius()
                return cur
        except RuntimeError:
            pass
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(self._base_blur)
        eff.setOffset(0, 6)
        eff.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(eff)
        self._shadow = eff
        return eff

    def _animate_shadow(self, *, blur: int, alpha: int, tint: bool, offset_y: int = 6) -> None:
        shadow = self._valid_shadow()
        if shadow is None:
            return
        col = QColor(self._glow) if tint else QColor(0, 0, 0)
        col.setAlpha(alpha)
        shadow.setColor(col)
        # ★ 性能关键：不要动画 blurRadius —— 每帧改 blurRadius 会让 Qt 把整块
        #   投影重新高斯模糊（实测是「卡顿」主因之一）。改为「固定模糊半径 +
        #   一次性设定颜色 + 只动画廉价的 offset」来表达悬停「浮起」。
        #   blurRadius 只在悬停/离开各设一次（离散值），不再逐帧重栅格化。
        if shadow.blurRadius() != blur:
            shadow.setBlurRadius(blur)
        # 阴影下移动画（悬停时投影变长 → 卡片「浮起」错觉，且布局安全、开销极低）
        off = QPropertyAnimation(shadow, b"offset", self)
        off.setDuration(220)
        off.setStartValue(shadow.offset())
        off.setEndValue(QPointF(0, offset_y))
        off.setEasingCurve(QEasingCurve.Type.OutCubic)
        off.start()
        self._offset_anim = off

    def enterEvent(self, ev) -> None:
        if self._hover_enabled:
            self._animate_shadow(blur=self._peak_blur, alpha=170, tint=True, offset_y=14)
        super().enterEvent(ev)

    def leaveEvent(self, ev) -> None:
        if self._hover_enabled:
            self._animate_shadow(blur=self._base_blur, alpha=100, tint=False, offset_y=6)
        super().leaveEvent(ev)


# ─────────────── 分隔线 ───────────────
class HLine(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("hr", True)
        self.setFixedHeight(1)


# ─────────────── 状态徽章 ───────────────
class StatusChip(QLabel):
    """红/灰/蓝状态徽章。"""

    def __init__(self, status: str = "upcoming", text: str = "未开赛") -> None:
        super().__init__(text)
        self.set_state(status, text)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_state(self, status: str, text: str) -> None:
        self.setProperty("chip", status)
        self.setText(text)
        self.style().unpolish(self)
        self.style().polish(self)


# ─────────────── Spinner ───────────────
class Spinner(QWidget):
    """旋转加载圆环（由全局 FrameClock 驱动，支持 240FPS）。"""

    def __init__(self, parent: QWidget | None = None, *, diameter: int = 28) -> None:
        super().__init__(parent)
        self._diameter = diameter
        self._angle = 0.0
        self._color = QColor("#00BFFF")
        self.setFixedSize(diameter, diameter)
        self._clock = FrameClock.instance()
        self._subscribed = False

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        if not self._subscribed:
            self._clock.subscribe(self._on_frame)
            self._subscribed = True

    def hideEvent(self, ev) -> None:
        super().hideEvent(ev)
        if self._subscribed:
            self._clock.unsubscribe(self._on_frame)
            self._subscribed = False

    def _on_frame(self, _t: float, dt: float) -> None:
        # 480°/秒，与帧率无关
        self._angle = (self._angle + dt * 480.0) % 360.0
        self.update()

    def set_color(self, color: QColor) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(3, 3, -3, -3)
        ring = QColor(self._color)
        ring.setAlphaF(0.12)
        pen = QPen(ring); pen.setWidth(3)
        p.setPen(pen)
        p.drawEllipse(rect)
        pen2 = QPen(self._color); pen2.setWidth(3)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        p.drawArc(rect, int(-self._angle) * 16, 90 * 16)


# ─────────────── 数值动画 Label ───────────────
class CountUpLabel(QLabel):
    """普通版本：纯色数字 count-up。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0
        self._anim = QPropertyAnimation(self, b"intValue", self)
        self._anim.setDuration(900)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        _anim().track(self._anim)
        self.setText("0")

    def set_target(self, target: int) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(int(target))
        self._anim.start()

    def get_int_value(self) -> int:
        return self._value

    def set_int_value(self, v: int) -> None:
        self._value = int(v)
        self.setText(str(self._value))

    intValue = pyqtProperty(int, fget=get_int_value, fset=set_int_value)


class GoldNumber(QWidget):
    """金色渐变 + 描边的 count-up 大号数字（FC25 风格）。

    自绘控件，确保字体「无遮挡」且能填充金色立体渐变 + 高光。
    可设置颜色（默认金）；使用 ``set_target`` 触发 count-up 动画。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        font_size: int = 38,
        primary: str = "#FFE680",
        secondary: str = "#FFB957",
        deep: str = "#A86A00",
    ) -> None:
        super().__init__(parent)
        self._value = 0
        self._target = 0
        self._font_size = font_size
        self._primary = QColor(primary)
        self._secondary = QColor(secondary)
        self._deep = QColor(deep)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # 关键：按真实字体度量设定最小尺寸，避免「大数字显示不全 / 顶部被裁」。
        self._apply_min_size()

        self._anim = QPropertyAnimation(self, b"intValue", self)
        self._anim.setDuration(1100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        _anim().track(self._anim)

    def _font(self) -> QFont:
        f = QFont(self.font())
        f.setPointSize(self._font_size)
        f.setBold(True)
        return f

    def _apply_min_size(self) -> None:
        """用 QFontMetrics 计算真实字形高度，设为控件最小高度（含余量）。

        旧版 ``sizeHint`` 用 ``font_size * 1.25`` 估高，对大号粗体字体偏小，
        导致 ``paintEvent`` 中 ``offset_y`` 变负、数字顶部被裁切。
        """
        from PyQt6.QtGui import QFontMetricsF
        fm = QFontMetricsF(self._font())
        h = int(fm.height() + 8)          # 上下各留 4px 余量
        w = int(fm.horizontalAdvance("88") + 12)
        self.setMinimumSize(w, h)

    def set_colors(self, primary: str, secondary: str, deep: str) -> None:
        self._primary = QColor(primary)
        self._secondary = QColor(secondary)
        self._deep = QColor(deep)
        self.update()
    def set_target(self, target: int) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(int(target))
        self._anim.start()
        self._target = int(target)

    def get_int_value(self) -> int:
        return self._value

    def set_int_value(self, v: int) -> None:
        self._value = int(v)
        self.update()

    intValue = pyqtProperty(int, fget=get_int_value, fset=set_int_value)

    def sizeHint(self):
        return self.minimumSize()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        f = self._font()
        p.setFont(f)
        text = str(self._value)
        rect = QRectF(self.rect())
        fm = p.fontMetrics()

        # 水平居中 + 垂直按基线居中（保证整字形完整显示、绝不裁顶/裁底）
        bw = fm.horizontalAdvance(text)
        offset_x = max(0.0, (rect.width() - bw) / 2)
        baseline = (rect.height() + fm.ascent() - fm.descent()) / 2

        path = QPainterPath()
        path.addText(rect.left() + offset_x, baseline, f, text)

        # 金色立体渐变填充
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, self._primary)
        grad.setColorAt(0.55, self._secondary)
        grad.setColorAt(1.0, self._deep)
        p.setBrush(grad)
        p.setPen(QPen(QColor(70, 35, 0, 180), 2.0))
        p.drawPath(path)


class AvatarRing(QWidget):
    """双层圆环 + 头像底盘（FC25 卡风）。

    用 QPainter 自绘双层圆环（外环渐变描边 + 内环细线），中间露出
    托管的真实头像（``set_avatar`` 传入 QPixmap 即可）。
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        diameter: int = 110,
        outer_color: str = "#00BFFF",
        inner_color: str = "#FFD700",
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(diameter, diameter)
        self._d = diameter
        self._outer = QColor(outer_color)
        self._inner = QColor(inner_color)
        self._pix = None  # QPixmap

    def set_avatar(self, pix) -> None:  # QPixmap | None
        self._pix = pix
        self.update()

    def set_colors(self, outer: str, inner: str) -> None:
        self._outer = QColor(outer)
        self._inner = QColor(inner)
        self.update()

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        cx, cy = rect.center().x(), rect.center().y()

        # 外环渐变（旋转一圈红->金->红）
        outer_pen_w = 4
        outer_rect = rect.adjusted(outer_pen_w / 2, outer_pen_w / 2,
                                    -outer_pen_w / 2, -outer_pen_w / 2)
        ring = QLinearGradient(outer_rect.topLeft(), outer_rect.bottomRight())
        ring.setColorAt(0.0, self._outer)
        ring.setColorAt(0.5, self._inner)
        ring.setColorAt(1.0, self._outer)
        pen = QPen(ring, outer_pen_w)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(outer_rect)

        # 内细线
        inner_rect = rect.adjusted(8, 8, -8, -8)
        p.setPen(QPen(QColor(255, 255, 255, 50), 1.0))
        p.drawEllipse(inner_rect)

        # 头像
        avatar_rect = rect.adjusted(11, 11, -11, -11)
        path = QPainterPath()
        path.addEllipse(avatar_rect)
        p.setClipPath(path)
        if self._pix is not None and not self._pix.isNull():
            scaled = self._pix.scaled(int(avatar_rect.width()),
                                      int(avatar_rect.height()),
                                      Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                      Qt.TransformationMode.SmoothTransformation)
            x = avatar_rect.left() + (avatar_rect.width() - scaled.width()) / 2
            y = avatar_rect.top() + (avatar_rect.height() - scaled.height()) / 2
            p.drawPixmap(int(x), int(y), scaled)
        else:
            p.fillPath(path, QColor(20, 24, 38))


# ─────────────── 简单的横向 Pill 组 ───────────────
class PillRow(QWidget):
    """显示一行小胶囊（key: value）。"""

    def __init__(self, items: list[tuple[str, str]], parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for k, v in items:
            label = QLabel(f"<span style='opacity:.7'>{k}</span>  <b>{v}</b>")
            label.setStyleSheet(
                "background: rgba(255,255,255,0.04);"
                "border-radius: 9px; padding: 4px 10px;"
            )
            layout.addWidget(label)
        layout.addStretch(1)



# ─────────────── 分区标题 ───────────────
class SectionHeader(QWidget):
    """分区标题：彩色竖条 + 中文大标题 + 英文 overline + 右侧提示。

    统一所有页面分区的视觉节奏，是「商业级」排版层级的关键组件。
    """

    def __init__(
        self,
        title: str,
        subtitle_en: str = "",
        *,
        accent: str = "#00BFFF",
        hint: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 2, 2, 2)
        row.setSpacing(12)

        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setMinimumHeight(34)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f" stop:0 {accent}, stop:1 rgba(255,255,255,0.05));"
            f" border-radius: 2px;"
        )
        row.addWidget(bar)

        text = QVBoxLayout()
        text.setSpacing(0)
        t = QLabel(title)
        t.setStyleSheet("font-size:20px; font-weight:900; color:#FFFFFF;")
        text.addWidget(t)
        if subtitle_en:
            en = QLabel(subtitle_en)
            en.setStyleSheet(
                f"color:{accent}; font-size:10px; font-weight:800;"
                " letter-spacing:2px;"
            )
            text.addWidget(en)
        row.addLayout(text)
        row.addStretch(1)

        if hint:
            self._hint = QLabel(hint)
            self._hint.setStyleSheet("color:#6B7689; font-size:11.5px; font-weight:600;")
            row.addWidget(self._hint, alignment=Qt.AlignmentFlag.AlignVCenter)
        else:
            self._hint = None

    def set_hint(self, text: str) -> None:
        if self._hint is not None:
            self._hint.setText(text)
