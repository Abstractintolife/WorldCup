#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""球员肖像处理脚本 —— 把普通实拍图，变成「世界杯赛事系统」球员详情页那种
深红电影风、球员靠右悬浮的 hero 大图。

脚本独立运行，不依赖项目里的任何代码。

==============================================================================
它做了什么
==============================================================================
对每一张原图：
  1. 抠图     —— 用 rembg 自动去掉背景（亮天空 / 看台），得到透明的球员剪影
  2. 自动裁剪 —— 去掉透明边缘，把球员裁到最紧
  3. 输出两份：
       players/<名字>.png        ← 透明 PNG（App 真正加载的素材）
       preview/<名字>_hero.png   ← 合成好的深红 hero 预览图（你本地验收用）

==============================================================================
准备工作（只需做一次）
==============================================================================
1. 装 Python 3.9 ~ 3.12（rembg 暂不支持 3.13+）

2. 安装依赖：
       pip install rembg pillow numpy onnxruntime

   （首次运行 rembg 会自动下载约 170MB 的抠图模型，需要联网，下载一次后离线可用）

==============================================================================
怎么用
==============================================================================
1. 把原图按"中文名"放进输入目录，例如：
       portraits_raw/哈弗茨.jpg
       portraits_raw/梅西.png
       portraits_raw/姆巴佩.jpg

2. 运行：
       python tools/process_portraits.py

   常用参数：
       --in  portraits_raw          输入目录（默认 portraits_raw）
       --out app/assets/players     透明 PNG 输出目录（默认 app/assets/players）
       --preview-dir portraits_preview   预览图输出目录
       --no-preview                 只抠图，不生成预览
       --model isnet-general-use    抠图模型（默认 isnet-general-use，质量最好；
                                    想快一点用 u2net）
       --overwrite                  覆盖已存在的结果（默认跳过已处理的）

   示例：只处理一张图看效果
       python tools/process_portraits.py --in portraits_raw --out app/assets/players

==============================================================================
拿到结果后
==============================================================================
- 打开 preview/<名字>_hero.png 看效果是否满意；
- 把 app/assets/players/<名字>.png 提交到仓库，App 端接好本地加载逻辑后即自动显示。
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# ────────────────────────────────────────────────────────────────────────────
# 依赖检查（给出友好的安装提示，而不是直接报 ImportError）
# ────────────────────────────────────────────────────────────────────────────
def _require(modname: str, pip_name: str | None = None):
    try:
        return __import__(modname)
    except ImportError:
        pip_name = pip_name or modname
        print(
            f"\n[缺少依赖] 需要 `{modname}`。请先安装：\n"
            f"    pip install rembg pillow numpy onnxruntime\n",
            file=sys.stderr,
        )
        sys.exit(1)


np = _require("numpy")
PIL = _require("PIL", "pillow")
from PIL import Image, ImageFilter  # noqa: E402

# rembg 体积大，单独导入并给提示
try:
    from rembg import new_session, remove
except ImportError:
    print(
        "\n[缺少依赖] 需要 `rembg`（自动抠图）。请安装：\n"
        "    pip install rembg onnxruntime\n"
        "如果你已经有抠好的透明 PNG，可加 --no-bg-removal 跳过抠图。\n",
        file=sys.stderr,
    )
    new_session = None  # type: ignore
    remove = None  # type: ignore


# 支持的输入图片后缀
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# 目标稿配色
RED = (255, 0, 80)          # 红色辉光主色
DARK = (10, 9, 15)          # 背景深色
DARK2 = (26, 10, 16)        # 背景深红


# ────────────────────────────────────────────────────────────────────────────
# 工具函数
# ────────────────────────────────────────────────────────────────────────────
def autocrop_alpha(img: Image.Image, pad_ratio: float = 0.02) -> Image.Image:
    """根据 alpha 通道把透明边缘裁掉，只留球员主体。"""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = np.array(img.split()[-1])
    ys, xs = np.where(alpha > 12)
    if len(xs) == 0 or len(ys) == 0:
        return img
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    pad_x = int((x1 - x0) * pad_ratio)
    pad_y = int((y1 - y0) * pad_ratio)
    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)
    x1 = min(img.width - 1, x1 + pad_x)
    y1 = min(img.height - 1, y1 + pad_y)
    return img.crop((x0, y0, x1 + 1, y1 + 1))


def cutout_player(src: Image.Image, session) -> Image.Image:
    """抠图 → 透明 PNG → 自动裁剪。"""
    if remove is None:
        # 没装 rembg：假设输入已是透明 PNG
        out = src.convert("RGBA")
    else:
        out = remove(src, session=session, post_process_mask=True)
        if not isinstance(out, Image.Image):
            out = Image.open(io.BytesIO(out))
        out = out.convert("RGBA")
    return autocrop_alpha(out)


def _vertical_dark_grad(w: int, h: int, top_a: int, bot_a: int) -> Image.Image:
    """上→下黑色渐变（用于上下暗角）。"""
    col = np.linspace(top_a, bot_a, h).astype(np.uint8)
    a = np.repeat(col[:, None], w, axis=1)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


def _horizontal_left_dark(w: int, h: int, left_a: int = 235, mid_stop: float = 0.62
                          ) -> Image.Image:
    """左→右黑色渐变：左边几乎全黑（放文字），到 mid_stop 处变透明。"""
    a = np.zeros(w, np.float32)
    cut = int(w * mid_stop)
    a[:cut] = np.linspace(left_a, 0, cut)
    arr = np.repeat(a[None, :], h, axis=0).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = arr
    return Image.fromarray(rgba, "RGBA")


def _radial_glow(w: int, h: int, cx: float, cy: float, radius: float,
                 color=RED, max_a: int = 150) -> Image.Image:
    """以 (cx,cy) 为中心的红色径向辉光。"""
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    a = np.clip(1.0 - dist, 0, 1) ** 1.6 * max_a
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0] = color[0]
    rgba[..., 1] = color[1]
    rgba[..., 2] = color[2]
    rgba[..., 3] = a.astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def make_hero(cutout: Image.Image, w: int = 1500, h: int = 540) -> Image.Image:
    """把透明球员图合成成目标稿那种深红 hero 预览图。"""
    # 1) 深色斜向渐变底
    base = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        base[..., c] = np.linspace(DARK[c], DARK2[c], w)[None, :]
    canvas = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")

    # 2) 右侧红色辉光（球员所在位置）
    glow = _radial_glow(w, h, cx=w * 0.68, cy=h * 0.55,
                        radius=h * 1.15, max_a=150)
    canvas = Image.alpha_composite(canvas, glow)

    # 3) 贴球员 —— 靠右、顶部出血
    target_h = int(h * 1.12)                       # 比画布高，头部超出顶部
    scale = target_h / cutout.height
    pw = int(cutout.width * scale)
    player = cutout.resize((pw, target_h), Image.LANCZOS)

    # 球员身体中心放在画布约 66% 处
    px = int(w * 0.66 - pw / 2)
    py = int(h - target_h + h * 0.06)              # 略微下沉，脚出血
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.alpha_composite(player, (px, py))

    # 球员红色边缘光（rim light）：放大 alpha 做发光描边
    rim = player.split()[-1].filter(ImageFilter.GaussianBlur(6))
    rim_rgba = Image.new("RGBA", player.size, RED + (0,))
    rim_rgba.putalpha(rim.point(lambda v: int(v * 0.5)))
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_layer.alpha_composite(rim_rgba, (px, py))
    canvas = Image.alpha_composite(canvas, glow_layer)
    canvas = Image.alpha_composite(canvas, layer)

    # 4) 左→右深色渐变（保证左边文字可读）
    canvas = Image.alpha_composite(canvas, _horizontal_left_dark(w, h))

    # 5) 上下暗角
    canvas = Image.alpha_composite(canvas, _vertical_dark_grad(w, h, 90, 0))
    bottom = _vertical_dark_grad(w, h, 0, 150)
    canvas = Image.alpha_composite(canvas, bottom)

    return canvas.convert("RGB")


# ────────────────────────────────────────────────────────────────────────────
# 主流程
# ────────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="把球员实拍图处理成透明 PNG + 深红 hero 预览图。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--in", dest="in_dir", default="portraits_raw",
                    help="输入目录（放原图，按中文名命名）。默认 portraits_raw")
    ap.add_argument("--out", dest="out_dir", default="assets/players",
                    help="透明 PNG 输出目录。默认 app/assets/players")
    ap.add_argument("--preview-dir", dest="preview_dir", default="portraits_preview",
                    help="hero 预览图输出目录。默认 portraits_preview")
    ap.add_argument("--no-preview", action="store_true", help="不生成预览图")
    ap.add_argument("--no-bg-removal", action="store_true",
                    help="跳过抠图（输入已是透明 PNG 时用）")
    ap.add_argument("--model", default="isnet-general-use",
                    help="rembg 抠图模型（isnet-general-use 质量最好 / u2net 更快）")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在的结果")
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    preview_dir = Path(args.preview_dir)

    if not in_dir.exists():
        in_dir.mkdir(parents=True, exist_ok=True)
        print(f"[提示] 输入目录不存在，已创建：{in_dir.resolve()}")
        print("       请把原图（按中文名命名，如 哈弗茨.jpg）放进去再运行。")
        return 0

    files = sorted(p for p in in_dir.iterdir()
                   if p.is_file() and p.suffix.lower() in EXTS)
    if not files:
        print(f"[提示] {in_dir} 里没有找到图片（支持 {', '.join(sorted(EXTS))}）。")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    if not args.no_preview:
        preview_dir.mkdir(parents=True, exist_ok=True)

    # 初始化抠图模型
    session = None
    if not args.no_bg_removal:
        if new_session is None:
            print("[错误] 未安装 rembg，无法抠图。装好后重试，或加 --no-bg-removal。")
            return 1
        print(f"[模型] 加载抠图模型 {args.model}（首次会下载，请稍候）...")
        session = new_session(args.model)

    ok = skip = fail = 0
    for f in files:
        name = f.stem  # 中文名
        out_png = out_dir / f"{name}.png"
        if out_png.exists() and not args.overwrite:
            print(f"[跳过] {name}（已存在，加 --overwrite 可覆盖）")
            skip += 1
            continue
        try:
            print(f"[处理] {f.name} ...", end=" ", flush=True)
            src = Image.open(f).convert("RGBA")
            cutout = cutout_player(src, session)
            cutout.save(out_png)
            msg = f"→ {out_png}"
            if not args.no_preview:
                hero = make_hero(cutout)
                hero_path = preview_dir / f"{name}_hero.png"
                hero.save(hero_path, quality=92)
                msg += f"  |  预览 {hero_path}"
            print("OK  " + msg)
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"失败：{e}")
            fail += 1

    print(f"\n完成：成功 {ok}，跳过 {skip}，失败 {fail}")
    print(f"透明 PNG → {out_dir.resolve()}")
    if not args.no_preview:
        print(f"预览图   → {preview_dir.resolve()}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
