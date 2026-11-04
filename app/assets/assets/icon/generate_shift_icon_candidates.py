# -*- coding: utf-8 -*-
"""动态班次图标重做候选（去掉顶部横条、缩小文字、加美化）。"""
from __future__ import annotations
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = r"D:\dev\icon_shift_candidates"
os.makedirs(OUT, exist_ok=True)
S = 1024
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
WHITE = (255, 255, 255)

VARIANTS = {
    "day": ((93, 182, 0), (44, 120, 0), "白"),
    "night": ((76, 111, 255), (32, 46, 170), "夜"),
    "mid": ((252, 115, 141), (200, 50, 84), "中"),
    "rest": ((118, 168, 129), (66, 116, 84), "休"),
}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, c1, c2):
    img = Image.new("RGB", (size, size), c1)
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = 0.6 * (y / (size - 1)) + 0.4 * (x / (size - 1))
            px[x, y] = lerp(c1, c2, t)
    return img


def soft_glow(img):
    glow = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(glow)
    s = img.size[0]
    d.ellipse([-s * 0.45, -s * 0.55, s * 0.9, s * 0.3], fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(s * 0.18))
    return Image.composite(Image.new("RGB", img.size, WHITE), img, glow.point(lambda v: int(v * 0.25)))


def rounded(img, radius_ratio=0.225):
    size = img.size
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0], size[1]], radius=int(size[0] * radius_ratio), fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def draw_char(d, size, char, ratio, color, dy=0.0):
    font = ImageFont.truetype(FONT_BOLD, int(size * ratio))
    bbox = d.textbbox((0, 0), char, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((size / 2 - tw / 2 - bbox[0], size / 2 - th / 2 - bbox[1] + size * dy), char, font=font, fill=color)


# 方案 A：渐变底 + 大留白 + 白色字（36%）+ 右下小光点
def variant_a(key, char, c1, c2, size=S):
    img = soft_glow(gradient(size, c1, c2)).convert("RGBA")
    d = ImageDraw.Draw(img)
    draw_char(d, size, char, 0.36, WHITE, dy=-0.02)
    # 底部三个小圆点（班次指示，低调装饰）
    r = size * 0.018
    cy = size * 0.80
    for i, off in enumerate((-0.05, 0.0, 0.05)):
        cx = size / 2 + size * off
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*WHITE, 190))
    return rounded(img)


# 方案 B：渐变底 + 白色圆形徽章（52%）+ 班次色字（25%）
def variant_b(key, char, c1, c2, size=S):
    img = soft_glow(gradient(size, c1, c2)).convert("RGBA")
    d = ImageDraw.Draw(img)
    r = size * 0.27
    cx = cy = size / 2
    # 徽章阴影
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - r, cy - r + size * 0.02, cx + r, cy + r + size * 0.02], fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(size * 0.02)))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
    draw_char(d, size, char, 0.25, (*c1, 255), dy=0.005)
    return rounded(img)


# 方案 C：渐变底 + 白色字（34%）+ 底部细圆弧装饰
def variant_c(key, char, c1, c2, size=S):
    img = soft_glow(gradient(size, c1, c2)).convert("RGBA")
    d = ImageDraw.Draw(img)
    draw_char(d, size, char, 0.34, WHITE, dy=-0.05)
    # 底部白色细弧线（轮转暗示）
    r = size * 0.30
    cx = cy = size * 0.82
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(*WHITE, 130), width=int(size * 0.018))
    return rounded(img)


def preview(img, key, name):
    img.convert("RGB").resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, f"{name}-{key}.png"), "PNG")


for key, (c1, c2, char) in VARIANTS.items():
    for name, fn in (("A", variant_a), ("B", variant_b), ("C", variant_c)):
        img = fn(key, char, c1, c2)
        img.convert("RGB").save(os.path.join(OUT, f"{name}-{key}-1024.png"), "PNG")
        preview(img, key, name)
print("done", OUT)
