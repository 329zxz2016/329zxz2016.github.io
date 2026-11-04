# -*- coding: utf-8 -*-
"""生成最终版「倒班日历」App 图标（v2：满版日历 + 轮次色块 + 时钟徽章）。

输出：
- assets/icon/app_icon.png            1024x1024 不透明（Android/iOS 通用）
- assets/icon/app_icon_foreground.png 1024x1024 透明（Android 自适应图标前景）
- assets/icon/ic_stat_shift.png       96x96 白色透明（通知栏小图标）
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
S = 1024

BRAND = (52, 197, 102)       # #34C566
BRAND_DEEP = (34, 168, 79)   # #22A84F
BRAND_DARK = (22, 126, 61)   # #167E3D
WHITE = (255, 255, 255)

SHIFTS = [
    (93, 182, 0), (93, 182, 0),        # 白
    (252, 115, 141), (252, 115, 141),  # 中
    (76, 111, 255), (76, 111, 255),    # 夜
    (118, 168, 129), (118, 168, 129),  # 休
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, c1, c2, diagonal=0.5):
    img = Image.new("RGB", (size, size), c1)
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = diagonal * (y / (size - 1)) + (1 - diagonal) * (x / (size - 1))
            px[x, y] = lerp(c1, c2, t)
    return img


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.size[0], img.size[1]], radius=radius, fill=255
    )
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def drop_shadow(img, blur=26, offset=(0, 18), alpha=85):
    alpha_mask = img.split()[-1]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    black = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    offset = (int(offset[0]), int(offset[1]))
    sh.paste(black, offset, alpha_mask)
    return sh.filter(ImageFilter.GaussianBlur(blur))


def soft_highlight(img):
    glow = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(glow)
    d.ellipse([-S * 0.4, -S * 0.6, S * 0.85, S * 0.35], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.22))
    white = Image.new("RGB", img.size, WHITE)
    return Image.composite(white, img, glow.point(lambda v: int(v * 0.30)))


def draw_clock_badge(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    # 白色描边外圈
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=WHITE)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRAND_DARK)
    # 表盘内圈
    d.ellipse(
        [cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18],
        outline=(255, 255, 255, 70), width=8,
    )
    # 指针：分针指 12，时针指 10 点方向（更清晰的时钟识别度）
    lw = max(10, int(r * 0.13))
    d.line([cx, cy, cx, cy - int(r * 0.52)], fill=WHITE, width=lw)
    ang = math.radians(-145)
    d.line(
        [cx, cy, cx + int(r * 0.36 * math.cos(ang)), cy + int(r * 0.36 * math.sin(ang))],
        fill=WHITE, width=lw,
    )
    dot = max(8, int(r * 0.10))
    d.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=WHITE)


def build_icon(size=1024, scale=1.0, transparent_bg=False, with_clock=True):
    """核心绘制：满版日历 + 8 个班次色块 + 右下角时钟徽章。"""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    def sc(v):
        return v / 1024.0 * size * scale

    if transparent_bg:
        layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        base = layer
    else:
        bg = gradient(size, BRAND, BRAND_DARK, diagonal=0.62)
        base = soft_highlight(bg).convert("RGBA")

    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    margin = sc(70)
    top_extra = sc(34)
    left = margin
    top = margin + top_extra
    right = size - margin
    bottom = size - margin
    radius = sc(200)

    # 卡片阴影 + 白卡
    cd.rounded_rectangle([left, top, right, bottom], radius=radius, fill=WHITE)

    # 顶部品牌色头
    header_h = sc(212)
    cd.rounded_rectangle(
        [left, top, right, top + header_h + radius], radius=radius, fill=BRAND
    )
    cd.rectangle(
        [left, top + header_h, right, top + header_h + radius + 8], fill=WHITE
    )

    composed = Image.alpha_composite(base, drop_shadow(card, blur=sc(26), offset=(0, sc(18))))
    composed = Image.alpha_composite(composed, card)
    d = ImageDraw.Draw(composed)

    # 装订环（白色圆环，压在顶部边缘）
    ring_w = sc(76)
    ring_h = sc(150)
    for cx in (left + (right - left) * 0.3, left + (right - left) * 0.7):
        rx = cx - ring_w / 2
        ry = top - ring_h * 0.52
        d.rounded_rectangle(
            [rx, ry, rx + ring_w, ry + ring_h], radius=ring_w / 2, fill=WHITE
        )
        # 内槽（用头部的绿色）
        d.rounded_rectangle(
            [rx + sc(20), ry + sc(26), rx + ring_w - sc(20), ry + ring_h - sc(26)],
            radius=(ring_w - sc(40)) / 2,
            fill=BRAND,
        )

    # 8 个班次色块（2 行 x 4 列，尽量大）
    body_top = top + header_h + sc(74)
    body_bottom = bottom - sc(96)
    cols, rows = 4, 2
    gap = sc(30)
    avail_w = (right - left) - sc(96)
    chip = (avail_w - gap * (cols - 1)) / cols
    total_w = chip * cols + gap * (cols - 1)
    gx = left + ((right - left) - total_w) / 2
    max_chip_h = ((body_bottom - body_top) - gap * (rows - 1)) / rows
    chip_h = min(chip, max_chip_h)
    gy = body_top + ((body_bottom - body_top) - (chip_h * rows + gap * (rows - 1))) / 2
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x = gx + c * (chip + gap)
            y = gy + r * (chip_h + gap)
            d.rounded_rectangle(
                [x, y, x + chip, y + chip_h], radius=sc(42), fill=SHIFTS[idx % 8]
            )
            idx += 1

    # 右下角时钟徽章（压住卡片角）
    if with_clock:
        r = sc(132)
        bx = right - sc(112)
        by = bottom - sc(112)
        draw_clock_badge(composed, bx, by, r)

    if transparent_bg:
        return composed
    return rounded(composed, int(sc(228)))


def make_notification_icon(size=96):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size * 0.13
    lw = max(2, int(size * 0.08))
    d.rounded_rectangle(
        [m, m * 1.5, size - m, size - m],
        radius=size * 0.16,
        outline=WHITE,
        width=lw,
    )
    d.line([m, size * 0.36, size - m, size * 0.36], fill=WHITE, width=lw)
    for i in range(3):
        x = size * (0.28 + i * 0.22)
        r = size * 0.055
        d.ellipse([x - r, size * 0.58 - r, x + r, size * 0.58 + r], fill=WHITE)
    return img


def main():
    icon = build_icon(S, scale=1.0, transparent_bg=False, with_clock=True)
    icon.convert("RGB").save(os.path.join(OUT, "app_icon.png"), "PNG")

    # 自适应前景：内容缩到中间 72%，透明底
    fg_size = int(S * 0.72)
    fg = build_icon(fg_size, scale=1.0, transparent_bg=True, with_clock=True)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    offset = (S - fg_size) // 2
    canvas.alpha_composite(fg, (offset, offset))
    canvas.save(os.path.join(OUT, "app_icon_foreground.png"), "PNG")

    make_notification_icon(96).save(os.path.join(OUT, "ic_stat_shift.png"), "PNG")
    print("icons v2 generated:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
