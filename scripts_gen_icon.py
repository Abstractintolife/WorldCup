"""生成应用图标文件（assets/icon/app.ico / app.png）。

用 Pillow 复刻 app/ui/design/app_icon.py 的「世界杯大力神杯」徽章设计，
导出多尺寸 .ico（Windows exe 图标）与 1024px .png（macOS/通用）。

运行：pip install pillow numpy && python scripts_gen_icon.py
"""
from __future__ import annotations

import math
import os

import numpy as np
from PIL import Image, ImageDraw

BASE = 256.0
SIZE = 1024
S = SIZE / BASE


def sc(v: float) -> float:
    return v * S


# ── 配色（与 app_icon.py 一致）──────────────────────────────
GOLD_HI = (255, 240, 168)
GOLD = (255, 210, 77)
GOLD_LO = (200, 150, 42)
OUTLINE = (90, 60, 0)


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def interp(stops, t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
            return tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
    return stops[-1][1]


def vertical_gradient(y0, y1, stops) -> np.ndarray:
    """返回 (SIZE,SIZE,3) 的竖向渐变（按行）。"""
    arr = np.zeros((SIZE, SIZE, 3), dtype=np.float64)
    for y in range(SIZE):
        t = (y - y0) / (y1 - y0) if y1 != y0 else 0.0
        arr[y, :, :] = interp(stops, t)
    return arr


def radial_add(scene, cx, cy, radius, color, peak):
    """线性衰减的径向光晕，叠加到 scene（RGB float）。"""
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    inten = np.clip(1.0 - dist / radius, 0.0, 1.0) * peak
    for k in range(3):
        scene[:, :, k] += color[k] * inten
    np.clip(scene, 0, 255, out=scene)


def bezier(p0, c1, c2, p3, n=26):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3 * p0[0] + 3 * mt**2 * t * c1[0]
             + 3 * mt * t**2 * c2[0] + t**3 * p3[0])
        y = (mt**3 * p0[1] + 3 * mt**2 * t * c1[1]
             + 3 * mt * t**2 * c2[1] + t**3 * p3[1])
        pts.append((sc(x), sc(y)))
    return pts


def star_points(cx, cy, r):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.4
        pts.append((sc(cx) + math.cos(ang) * sc(r) * (1 if i % 2 == 0 else 0.4) / 1,
                    sc(cy) + math.sin(ang) * sc(r) * (1 if i % 2 == 0 else 0.4) / 1))
    # 简化：直接按 rad 计算
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = sc(r) if i % 2 == 0 else sc(r) * 0.4
        pts.append((sc(cx) + math.cos(ang) * rad, sc(cy) + math.sin(ang) * rad))
    return pts


def build() -> Image.Image:
    # ── 1) 底色竖向渐变 ──
    scene = vertical_gradient(
        sc(6), sc(250),
        [(0.0, _hex("#15264A")), (0.55, _hex("#0E1A33")), (1.0, _hex("#080F1E"))],
    )
    # ── 2) 光晕（顶部紫 + 左下蓝）──
    radial_add(scene, sc(128), sc(0.16 * BASE), sc(0.7 * BASE), (106, 90, 205), 150 / 255)
    radial_add(scene, sc(0.2 * BASE), sc(0.92 * BASE), sc(0.6 * BASE), (0, 191, 255), 90 / 255)

    base_img = Image.fromarray(scene.astype(np.uint8), "RGB").convert("RGBA")
    draw = ImageDraw.Draw(base_img)

    # ── 3) 奖杯金色渐变（按竖向 y 70..210 映射）──
    gold = vertical_gradient(
        sc(70), sc(210),
        [(0.0, GOLD_HI), (0.45, GOLD), (1.0, GOLD_LO)],
    )
    gold_img = Image.fromarray(gold.astype(np.uint8), "RGB").convert("RGBA")

    # 奖杯轮廓 mask（所有金色部件并集）
    mask = Image.new("L", (SIZE, SIZE), 0)
    md = ImageDraw.Draw(mask)
    # 把手（左右半圆，粗线）
    hw = int(sc(11))
    md.arc([sc(58), sc(86), sc(104), sc(146)], 90, 270, fill=255, width=hw)
    md.arc([sc(152), sc(86), sc(198), sc(146)], 270, 90, fill=255, width=hw)
    # 杯身
    bowl = ([(sc(82), sc(82)), (sc(174), sc(82))]
            + bezier((174, 82), (172, 120), (152, 152), (128, 152))
            + bezier((128, 152), (104, 152), (84, 120), (82, 82)))
    md.polygon(bowl, fill=255)
    # 杯柄 / 底座 / 底板
    md.rounded_rectangle([sc(120), sc(150), sc(136), sc(172)], radius=sc(4), fill=255)
    md.polygon([(sc(104), sc(172)), (sc(152), sc(172)),
                (sc(160), sc(192)), (sc(96), sc(192))], fill=255)
    md.rounded_rectangle([sc(90), sc(190), sc(166), sc(206)], radius=sc(5), fill=255)

    # 用金色渐变填充奖杯
    base_img.paste(gold_img, (0, 0), mask)

    # 杯口椭圆（高光金）
    draw.ellipse([sc(80), sc(72), sc(176), sc(92)], fill=GOLD_HI,
                 outline=OUTLINE, width=max(1, int(sc(2.0))))

    # 奖杯描边（杯身 + 底座）
    ow = max(1, int(sc(2.4)))
    draw.line(bowl + [bowl[0]], fill=OUTLINE, width=ow, joint="curve")
    draw.polygon([(sc(104), sc(172)), (sc(152), sc(172)),
                  (sc(160), sc(192)), (sc(96), sc(192))], outline=OUTLINE, width=ow)

    # 杯身竖向高光
    shine = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shine)
    hl = ([(sc(108), sc(86)), (sc(120), sc(86))]
          + bezier((120, 86), (116, 120), (112, 138), (116, 148))
          + bezier((116, 148), (108, 138), (106, 110), (108, 86)))
    sdraw.polygon(hl, fill=(255, 255, 255, 120))
    base_img = Image.alpha_composite(base_img, shine)
    draw = ImageDraw.Draw(base_img)

    # 星芒点缀
    draw.polygon(star_points(196, 66, 12), fill=(255, 255, 255, 235))
    draw.polygon(star_points(210, 92, 7), fill=GOLD)
    draw.polygon(star_points(64, 70, 6), fill=(255, 255, 255, 190))

    # ── 4) 圆角徽章裁切 ──
    corner = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(corner).rounded_rectangle(
        [sc(6), sc(6), sc(250), sc(250)], radius=sc(0.235 * BASE), fill=255)
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(base_img, (0, 0), corner)
    return out


def main() -> None:
    os.makedirs("assets/icon", exist_ok=True)
    icon = build()
    icon.save("assets/icon/app.png")
    sizes = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
    icon.save("assets/icon/app.ico", sizes=sizes)
    # 校验
    with Image.open("assets/icon/app.ico") as im:
        print("app.ico sizes:", sorted(im.info.get("sizes", [])) if im.info.get("sizes") else "ok")
    print("written: assets/icon/app.png (1024) + assets/icon/app.ico")


if __name__ == "__main__":
    main()
