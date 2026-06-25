"""自定义鼠标光标：把仓库里的位图做成全局指针。

本模块提供两枚项目专属光标：

* **默认箭头**（``cursor.png`` / ``光标.png``）—— 替代系统默认箭头，平时悬浮用。
* **点击手型**（``click_cursor.png`` / ``点击光标.png``）—— 替代系统 PointingHand
  「白手」，悬浮在按钮 / 可点卡片等可交互目标上时显示。

两枚光标共享同一套构建逻辑，因此外观「手感」一致：

* **自动裁掉透明留白** —— 源图是大画布，真正的图形只占其中一块。直接拿整张图
  当光标会显得「很小且偏移」，所以先按 alpha 求出不透明包围盒并裁剪。
* **统一目标尺寸** —— 两枚光标都按同一个逻辑高度 :data:`_TARGET_HEIGHT` 缩放，
  这样箭头与手型在屏幕上大小一致、互相切换时不会「忽大忽小」。
* **按屏幕 DPI 缩放保持锐利** —— 在高分屏（devicePixelRatio>1）上，位图按
  物理像素渲染、再通过 ``setDevicePixelRatio`` 还原逻辑尺寸，避免发虚。
* **热点对准生效点** —— 箭头取「最上一行里最靠左」的不透明像素（箭头尖）；
  手型取「最上一行的中点」（食指尖），符合各自直觉。

缺图 / 解析失败时返回 ``None``，调用方据此回退到系统默认光标（绝不崩溃）。
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QGuiApplication, QImage, QPixmap

from app.config import (
    CLICK_CURSOR_IMAGE_FALLBACK,
    CLICK_CURSOR_IMAGE_PATH,
    CURSOR_IMAGE_FALLBACK,
    CURSOR_IMAGE_PATH,
)

log = logging.getLogger(__name__)

# 两枚光标共用的目标「逻辑」高度（CSS 像素）。系统默认箭头约 20–24px；这里取
# 24 让项目光标醒目但不夸张。宽度按各自原图纵横比自适应——因此箭头与手型在屏幕
# 上「高度一致」，视觉大小统一。改这一个值即可整体放大 / 缩小所有自定义光标。
_TARGET_HEIGHT = 24

# 判定「不透明」的 alpha 阈值（0–255）。低于此值视为透明留白，参与裁剪。
_ALPHA_THRESHOLD = 40


def _first_existing(*paths: Path) -> Path | None:
    """返回首个存在的路径；都不存在时返回 ``None``。"""
    for p in paths:
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


def _tip_top_left(img: QImage, bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    """箭头尖端 = 包围盒内「最上一行里最靠左」的不透明像素（相对包围盒坐标）。"""
    minx, miny, maxx, maxy = bbox
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            if img.pixelColor(x, y).alpha() >= _ALPHA_THRESHOLD:
                return x - minx, y - miny
    return 0, 0


def _tip_top_center(img: QImage, bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    """食指尖 = 包围盒内「最上一行不透明像素跨度的中点」（相对包围盒坐标）。"""
    minx, miny, maxx, maxy = bbox
    for y in range(miny, maxy + 1):
        xs = [x for x in range(minx, maxx + 1)
              if img.pixelColor(x, y).alpha() >= _ALPHA_THRESHOLD]
        if xs:
            return (xs[0] + xs[-1]) // 2 - minx, y - miny
    return 0, 0


def _build_cursor(path: Path, *, hotspot: str) -> QCursor | None:
    """从位图构建一枚自定义光标。

    :param path: 源图路径。
    :param hotspot: ``"tip_left"`` 取箭头尖（左上），``"tip_center"`` 取食指尖（上中）。
    """
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

    if hotspot == "tip_center":
        tip_x, tip_y = _tip_top_center(img, bbox)
    else:
        tip_x, tip_y = _tip_top_left(img, bbox)

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

    scale = _TARGET_HEIGHT / ch  # 逻辑缩放系数（两枚光标统一高度）
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

    # 热点：生效点按逻辑缩放后的坐标（QCursor 接受逻辑像素坐标）。
    hot_x = round(tip_x * scale)
    hot_y = round(tip_y * scale)
    log.info(
        "自定义光标已构建：源 %s，裁剪 %dx%d，逻辑高 %dpx，热点(%d,%d)，DPR %.2g",
        path.name, cw, ch, _TARGET_HEIGHT, hot_x, hot_y, dpr,
    )
    return QCursor(pm, hot_x, hot_y)


@lru_cache(maxsize=1)
def build_app_cursor() -> QCursor | None:
    """构建项目默认箭头光标。失败 / 缺图时返回 ``None``。"""
    path = _first_existing(CURSOR_IMAGE_PATH, CURSOR_IMAGE_FALLBACK)
    if path is None:
        log.info("未找到自定义箭头光标图（cursor.png / 光标.png），使用系统默认箭头")
        return None
    return _build_cursor(path, hotspot="tip_left")


@lru_cache(maxsize=1)
def build_click_cursor() -> QCursor | None:
    """构建项目「点击 / 可交互」手型光标。失败 / 缺图时返回 ``None``。"""
    path = _first_existing(CLICK_CURSOR_IMAGE_PATH, CLICK_CURSOR_IMAGE_FALLBACK)
    if path is None:
        log.info("未找到自定义手型光标图（click_cursor.png / 点击光标.png），"
                 "可交互目标沿用系统 PointingHand")
        return None
    return _build_cursor(path, hotspot="tip_center")


@lru_cache(maxsize=1)
def pointing_hand_cursor() -> QCursor:
    """可交互目标使用的手型光标：优先自定义位图，缺图时回退系统 PointingHand。

    供各可点控件 ``setCursor(pointing_hand_cursor())`` 调用，统一替换原先散落的
    ``Qt.CursorShape.PointingHandCursor``。
    """
    cursor = build_click_cursor()
    if cursor is not None:
        return cursor
    return QCursor(Qt.CursorShape.PointingHandCursor)


def apply_app_cursor(widget) -> bool:
    """把默认箭头光标设到 ``widget`` 上（其未单独设光标的子控件会自动继承）。

    返回是否成功应用。失败时静默保留系统默认箭头。
    """
    cursor = build_app_cursor()
    if cursor is None:
        return False
    widget.setCursor(cursor)
    return True
