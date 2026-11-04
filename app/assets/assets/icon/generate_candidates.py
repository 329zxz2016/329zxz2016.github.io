# -*- coding: utf-8 -*-
"""生成 4 个 App 图标候选方案（原创设计，1024x1024）。

输出到 D:\dev\icon_candidates\，用于挑选后替换 assets/icon/app_icon.png。
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = r"D:\dev\icon_candidates"
os.makedirs(OUT, exist_ok=True)

S = 1024
BRAND = (52, 197, 102)      # #34C566
BRAND_DEEP = (30, 158, 74)  # #1E9E4A
BRAND_DARK = (21, 128, 61)  # #15803D
WHITE = (255, 255, 255)
INK = (23, 32, 42)
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
SHIFTS = [
    (93, 182, 0), (93, 182, 0),      # 白
    (252, 115, 141), (252, 115, 141),  # 中
    (76, 111, 255), (76, 111, 255),   # 夜
    (118, 168, 129), (118, 168, 129),  # 休
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, c1, c2, diagonal=0.45):
    img = Image.new("RGB", (size, size), c1)
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = diagonal * (y / (size - 1)) + (1 - diagonal) * (x / (size - 1))
            px[x, y] = lerp(c1, c2, t)
    return img


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def shadow_layers(img, blur=30, offset=(0, 18), alpha=90):
    alpha_mask = img.split()[-1]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    black = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    sh.paste(black, offset, alpha_mask)
    return sh.filter(ImageFilter.GaussianBlur(blur))


def soft_highlight(img):
    glow = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(glow)
    d.ellipse([-S * 0.35, -S * 0.55, S * 0.8, S * 0.4], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.2))
    white = Image.new("RGB", img.size, WHITE)
    return Image.composite(white, img, glow.point(lambda v: int(v * 0.35)))


# ---------------------------------------------------------------- 方案 A：满版日历
def variant_full_calendar():
    base = gradient(S, BRAND, BRAND_DARK, diagonal=0.6)
    base = soft_highlight(base).convert("RGBA")

    card = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    m = 62
    left, top, right, bottom = m, m + 18, S - m, S - m
    radius = 176
    d.rounded_rectangle([left, top, right, bottom], radius=radius, fill=WHITE)
    # 顶部品牌色条
    header_h = 210
    d.rounded_rectangle([left, top, right, top + header_h + radius], radius=radius, fill=BRAND)
    d.rectangle([left, top + header_h, right, top + header_h + radius + 6], fill=WHITE)
    # 装订环
    for rx in (left + 200, right - 300):
        d.rounded_rectangle([rx, top - 34, rx + 100, top + 96], radius=46, fill=BRAND_DEEP)
        d.rounded_rectangle([rx + 30, top - 2, rx + 70, top + 60], radius=20, fill=BRAND)
    # 8 个色块 2x4（大）
    grid_top = top + header_h + 96
    cols, rows = 4, 2
    gap = 34
    chip = (right - left - gap * (cols - 1) - 110) // cols
    total_w = chip * cols + gap * (cols - 1)
    gx = left + (right - left - total_w) // 2
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x = gx + c * (chip + gap)
            y = grid_top + r * (chip + gap)
            d.rounded_rectangle([x, y, x + chip, y + chip], radius=44, fill=SHIFTS[idx % 8])
            idx += 1
    img = Image.alpha_composite(base, shadow_layers(card))
    img = Image.alpha_composite(img, card)
    return rounded(img, 230)


# ---------------------------------------------------------------- 方案 B：班字徽章
def variant_character():
    base = gradient(S, (56, 205, 108), (16, 122, 66), diagonal=0.5)
    base = soft_highlight(base).convert("RGBA")
    d = ImageDraw.Draw(base)
    # 背景细纹理：8 段圆弧表示轮转
    cx, cy = S / 2, S / 2
    for i, color in enumerate(SHIFTS[:8]):
        start = -90 + i * 45
        d.arc([70, 70, S - 70, S - 70], start, start + 34, fill=(*color, 150), width=16)
    # 中央白色圆角徽章
    badge = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle([196, 196, S - 196, S - 196], radius=180, fill=(255, 255, 255, 255))
    img = Image.alpha_composite(base, shadow_layers(badge, blur=24, offset=(0, 14), alpha=80))
    img = Image.alpha_composite(img, badge)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 430)
    text = "班"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1] - 26), text, font=font, fill=BRAND_DARK)
    # 底部 4 个班次色点
    dot_r = 22
    total = len(SHIFTS[:4]) * (dot_r * 2 + 26) - 26
    x0 = cx - total / 2
    for i, color in enumerate([SHIFTS[0], SHIFTS[2], SHIFTS[4], SHIFTS[6]]):
        x = x0 + i * (dot_r * 2 + 26) + dot_r
        d.ellipse([x - dot_r, cy + 200, x + dot_r, cy + 200 + dot_r * 2], fill=color)
    return rounded(img, 230)


# ---------------------------------------------------------------- 方案 C：轮转色环
def variant_wheel():
    base = Image.new("RGBA", (S, S), (247, 247, 247, 255))
    d = ImageDraw.Draw(base)
    cx = cy = S / 2
    outer = 440
    n = 8
    colors = [
        (93, 182, 0), (118, 168, 129), (252, 115, 141), (255, 159, 67),
        (76, 111, 255), (108, 92, 231), (32, 201, 151), (255, 169, 77),
    ]
    for i, color in enumerate(colors):
        start = -90 + i * (360 / n)
        d.pieslice([cx - outer, cy - outer, cx + outer, cy + outer], start, start + (360 / n) + 1, fill=color)
    # 中心白色圆
    d.ellipse([cx - 250, cy - 250, cx + 250, cy + 250], fill=WHITE)
    img = Image.alpha_composite(rounded(gradient(S, (255, 255, 255), (240, 245, 242)).convert("RGBA"), 230), base)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 300)
    text = "班"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), text, font=font, fill=INK)
    return rounded(img, 230)


# ---------------------------------------------------------------- 方案 D：日历+循环箭头
def variant_cycle_arrow():
    base = gradient(S, (36, 178, 96), (13, 110, 60), diagonal=0.55).convert("RGBA")
    base = soft_highlight(base).convert("RGBA")
    d = ImageDraw.Draw(base)
    m = 108
    left, top, right, bottom = m, m + 40, S - m, S - m
    card = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    radius = 150
    cd.rounded_rectangle([left, top, right, bottom], radius=radius, fill=WHITE)
    cd.rounded_rectangle([left, top, right, top + 170 + radius], radius=radius, fill=BRAND_DEEP)
    img = Image.alpha_composite(base, shadow_layers(card, blur=28, offset=(0, 16)))
    img = Image.alpha_composite(img, card)
    d = ImageDraw.Draw(img)
    # 装订环
    for rx in (left + 160, right - 260):
        d.rounded_rectangle([rx, top - 30, rx + 100, top + 80], radius=44, fill=BRAND)
    # 8 色块
    grid_top = top + 230
    gap = 26
    chip = 132
    gx = left + (right - left - (chip * 4 + gap * 3)) // 2
    for i in range(8):
        r, c = divmod(i, 4)
        x = gx + c * (chip + gap)
        y = grid_top + r * (chip + gap)
        d.rounded_rectangle([x, y, x + chip, y + chip], radius=34, fill=SHIFTS[i])
    # 右下角循环箭头圆徽章
    bx, by, br = S - 250, S - 250, 128
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=BRAND_DEEP)
    d.arc([bx - 74, by - 74, bx + 74, by + 74], 40, 320, fill=WHITE, width=26)
    # 箭头三角
    ax, ay = bx + 74 * math.cos(math.radians(40)), by + 74 * math.sin(math.radians(40))
    tri = [(ax - 6, ay - 42), (ax - 6, ay + 42), (ax + 50, ay)]
    d.polygon(tri, fill=WHITE)
    return rounded(img, 230)


def save(img, name):
    path = os.path.join(OUT, name)
    img.convert("RGB").save(path, "PNG")
    print("saved", path)


save(variant_full_calendar(), "A_full_calendar.png")
save(variant_character(), "B_character.png")
save(variant_wheel(), "C_wheel.png")
save(variant_cycle_arrow(), "D_cycle_arrow.png")
