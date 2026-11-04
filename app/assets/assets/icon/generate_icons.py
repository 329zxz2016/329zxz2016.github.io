# -*- coding: utf-8 -*-
"""生成「倒班日历」App 图标（品牌绿 + 日历 + 轮次色块 + 闹钟）。

输出：
- assets/icon/app_icon.png            1024x1024 不透明（Android/iOS 通用）
- assets/icon/app_icon_foreground.png 1024x1024 透明（Android 自适应图标前景）
- assets/icon/ic_stat_shift.png       96x96 白色透明（通知栏小图标）
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))

BRAND_START = (52, 197, 102)    # #34C566
BRAND_END = (37, 170, 73)       # #25AA49
SHIFT_COLORS = [
    (93, 182, 0),     # 白班 #5DB600
    (93, 182, 0),
    (252, 115, 141),  # 中班 #FC738D
    (252, 115, 141),
    (76, 111, 255),   # 夜班 #4C6FFF
    (76, 111, 255),
    (118, 168, 129),  # 休息 #76A881
    (118, 168, 129),
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_bg(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BRAND_START)
    px = img.load()
    for y in range(size):
        row_t = y / (size - 1)
        for x in range(size):
            tx = 0.55 * row_t + 0.45 * (x / (size - 1))
            px[x, y] = lerp(BRAND_START, BRAND_END, tx)
    glow = Image.new("L", (size, size), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-size * 0.25, -size * 0.45, size * 0.75, size * 0.45], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.18))
    white = Image.new("RGB", (size, size), (255, 255, 255))
    return Image.composite(white, img, glow.point(lambda v: int(v * 0.55)))


def draw_calendar(size: int, scale: float = 1.0) -> Image.Image:
    """画白色日历卡 + 8 个轮次色块 + 右下角闹钟徽章（RGBA）。"""
    S = size
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def sc(v):
        return v * scale

    cx, cy = S / 2, S / 2
    card_w, card_h = sc(620), sc(600)
    left = cx - card_w / 2
    top = cy - card_h / 2 + sc(18)
    right = left + card_w
    bottom = top + card_h
    radius = sc(78)

    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [left + sc(6), top + sc(18), right + sc(6), bottom + sc(20)],
        radius=radius,
        fill=(0, 0, 0, 80),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(sc(26)))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([left, top, right, bottom], radius=radius,
                        fill=(255, 255, 255, 255))

    header_h = sc(150)
    header = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(header)
    hd.rounded_rectangle(
        [left, top, right, top + header_h + radius],
        radius=radius,
        fill=(*BRAND_START, 255),
    )
    hd.rectangle(
        [left, top + header_h, right, top + header_h + radius + sc(4)],
        fill=(0, 0, 0, 0),
    )
    img = Image.alpha_composite(img, header)
    d = ImageDraw.Draw(img)

    ring_w, ring_h = sc(58), sc(150)
    for rx in (cx - sc(120), cx + sc(62)):
        d.rounded_rectangle(
            [rx, top - sc(52), rx + ring_w, top + sc(58)],
            radius=sc(28),
            fill=(255, 255, 255, 255),
        )
    for rx in (cx - sc(120), cx + sc(62)):
        d.rounded_rectangle(
            [rx + sc(18), top - sc(28), rx + ring_w - sc(18), top + sc(30)],
            radius=sc(14),
            fill=(*BRAND_START, 255),
        )

    grid_top = top + header_h + sc(52)
    cols, rows = 4, 2
    chip_w, chip_h = sc(116), sc(116)
    gap_x, gap_y = sc(32), sc(34)
    total_w = cols * chip_w + (cols - 1) * gap_x
    gx = cx - total_w / 2
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x = gx + c * (chip_w + gap_x)
            y = grid_top + r * (chip_h + gap_y)
            color = SHIFT_COLORS[idx % len(SHIFT_COLORS)]
            d.rounded_rectangle([x, y, x + chip_w, y + chip_h],
                                radius=sc(28), fill=(*color, 255))
            idx += 1

    badge_r = sc(122)
    bx, by = right - sc(96), bottom - sc(58)
    d.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
              fill=(255, 255, 255, 255))
    d.ellipse([bx - badge_r + sc(16), by - badge_r + sc(16),
               bx + badge_r - sc(16), by + badge_r - sc(16)],
              fill=(*BRAND_END, 255))
    lw = max(1, int(sc(15)))
    d.line([bx, by, bx, by - sc(58)], fill=(255, 255, 255, 255), width=lw)
    d.line([bx, by, bx + sc(46), by + sc(14)], fill=(255, 255, 255, 255), width=lw)
    d.ellipse([bx - sc(15), by - sc(15), bx + sc(15), by + sc(15)],
              fill=(255, 255, 255, 255))
    return img


def make_notification_icon(size: int = 96) -> Image.Image:
    """通知栏白色小图标：日历轮廓 + 3 个点（透明底）。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size * 0.14
    lw = max(2, int(size * 0.075))
    d.rounded_rectangle([m, m * 1.6, size - m, size - m],
                        radius=size * 0.14,
                        outline=(255, 255, 255, 255), width=lw)
    d.line([m, size * 0.36, size - m, size * 0.36],
           fill=(255, 255, 255, 255), width=max(2, int(size * 0.065)))
    for fx in (0.33, 0.5, 0.67):
        r = size * 0.045
        d.ellipse([size * fx - r, size * 0.58 - r,
                   size * fx + r, size * 0.58 + r],
                  fill=(255, 255, 255, 255))
    return img


def main() -> None:
    base = gradient_bg(1024)
    icon = draw_calendar(1024, scale=1.0)
    composed = Image.alpha_composite(base.convert("RGBA"), icon)
    flat = Image.new("RGB", (1024, 1024), (255, 255, 255))
    flat.paste(composed, (0, 0), composed)
    flat.save(os.path.join(OUT, "app_icon.png"), "PNG")

    fg = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    fg = Image.alpha_composite(fg, draw_calendar(1024, scale=0.60))
    fg.save(os.path.join(OUT, "app_icon_foreground.png"), "PNG")

    make_notification_icon(96).save(os.path.join(OUT, "ic_stat_shift.png"), "PNG")
    print("icons generated:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
