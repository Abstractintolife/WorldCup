"""自定义鼠标光标：把仓库里的 cursor.png / 光标.png 做成全局指针。

设计目标（与系统原生指针手感一致，但换成项目专属外观）：

* **自动裁掉透明留白** —— 源图是 64×64 画布，真正的箭头只占其中一小块
  （bbox 约 x[18..42] y[16..39]）。直接拿整张图当光标会显得「很小且偏移」，
  所以先按 alpha 求出不透明包围盒并裁剪，得到一枚饱满的指针。
* **按屏幕 DPI 缩放保持锐利** —— 在高分屏（devicePixelRatio>1）上，位图按
  物理像素渲染、再通过 ``setDevicePixelRatio`` 还原逻辑尺寸，避免发虚。
* **热点对准箭头尖** —— 点击的「真正生效点」是箭头最尖端（最上一行里最靠左
  的不透明像素），而非位图左上角，符合普通箭头光标的直觉。

缺图 / 解析失败时返回 ``None``，调用方据此回退到系统默认箭头（绝不崩溃）。
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QGuiApplication, QImage, QPixmap

from app.config import CURSOR_IMAGE_FALLBACK, CURSOR_IMAGE_PATH

log = logging.getLogger(__name__)

# 光标的目标「逻辑」高度（CSS 像素）。系统默认箭头约 20–24px；这里取 30 让
# 项目光标更醒目一点，但不至于夸张。宽度按原图纵横比自适应。
_TARGET_HEIGHT = 30

# 判定「不透明」的 alpha 阈值（0–255）。低于此值视为透明留白，参与裁剪。
_ALPHA_THRESHOLD = 40


def _source_path() -> Path | None:
    """优先用 assets/cursor.png，回退仓库根目录的「光标.png」。"""
    for p in (CURSOR_IMAGE_PATH, CURSOR_IMAGE_FALLBACK):
        try:
            if p.exists():
                return p
        except OSError:
            continue
    return None


def _opaque_bbox(img: QImage) -> tuple[int, int, int, int] | None:
    """返回不透明像素的包围盒 (minx, miny, maxx, maxy)；全透明时返回 None。"""
    w, h = img.width(), img.height()
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            if img.pixelColor(x, y).alpha() >= _ALPHA_THRESHOLD:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return None
    return minx, miny, maxx, maxy


def _tip_in_bbox(img: QImage, bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    """箭头尖端 = 包围盒内「最上一行里最靠左」的不透明像素（相对包围盒坐标）。"""
    minx, miny, maxx, maxy = bbox
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            if img.pixelColor(x, y).alpha() >= _ALPHA_THRESHOLD:
                return x - minx, y - miny
    return 0, 0


@lru_cache(maxsize=1)
def build_app_cursor() -> QCursor | None:
    """构建项目自定义指针光标。失败 / 缺图时返回 ``None``。

    结果带 ``lru_cache``：光标位图在整个进程生命周期内只构建一次。
    """
    path = _source_path()
    if path is None:
        log.info("未找到自定义光标图（cursor.png / 光标.png），使用系统默认箭头")
        return None

    img = QImage(str(path))
    if img.isNull():
        log.warning("自定义光标图无法解析：%s", path)
        return None
    img = img.convertToFormat(QImage.Format.Format_ARGB32)

    bbox = _opaque_bbox(img)
    if bbox is None:
        log.warning("自定义光标图全透明，忽略：%s", path)
        return None
    minx, miny, maxx, maxy = bbox
    tip_x, tip_y = _tip_in_bbox(img, bbox)

    # 裁剪到不透明包围盒（去掉四周透明留白）。
    cropped = img.copy(minx, miny, maxx - minx + 1, maxy - miny + 1)
    cw, ch = cropped.width(), cropped.height()
    if cw <= 0 or ch <= 0:
        return None

    # 高分屏：按 devicePixelRatio 渲染物理像素，再还原逻辑尺寸保持锐利。
    try:
        dpr = QGuiApplication.primaryScreen().devicePixelRatio() or 1.0
    except Exception:  # pragma: no cover
        dpr = 1.0
    dpr = max(1.0, float(dpr))

    scale = _TARGET_HEIGHT / ch  # 逻辑缩放系数
    dev_h = max(1, round(_TARGET_HEIGHT * dpr))
    dev_w = max(1, round(cw * scale * dpr))

    scaled = cropped.scaled(
        dev_w,
        dev_h,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    pm = QPixmap.fromImage(scaled)
    pm.setDevicePixelRatio(dpr)

    # 热点：箭头尖端按逻辑缩放后的坐标（QCursor 接受逻辑像素坐标）。
    hot_x = round(tip_x * scale)
    hot_y = round(tip_y * scale)
    log.info(
        "自定义光标已构建：源 %s，裁剪 %dx%d，逻辑高 %dpx，热点(%d,%d)，DPR %.2g",
        path.name, cw, ch, _TARGET_HEIGHT, hot_x, hot_y, dpr,
    )
    return QCursor(pm, hot_x, hot_y)


def apply_app_cursor(widget) -> bool:
    """把自定义光标设到 ``widget`` 上（其未单独设光标的子控件会自动继承）。

    返回是否成功应用。失败时静默保留系统默认箭头。
    """
    cursor = build_app_cursor()
    if cursor is None:
        return False
    widget.setCursor(cursor)
    return True
