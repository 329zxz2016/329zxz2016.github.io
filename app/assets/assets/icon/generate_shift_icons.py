# -*- coding: utf-8 -*-
"""生成 5 套 Android 动态班次图标资源（供 activity-alias 切换）。

输出到 android/app/src/main/res：
- mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_shift_{key}.png   传统图标（完整方块）
- drawable-{密度}/ic_shift_{key}_fg.png                         自适应前景（透明）
- mipmap-anydpi-v26/ic_shift_{key}.xml                          自适应图标
- values/shift_icon_colors.xml                                  自适应背景色
键：default / day(白) / mid(中) / night(夜) / rest(休)
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT = r"D:\dev\daoban_app"
ICON_DIR = os.path.join(PROJECT, "assets", "icon")
RES = os.path.join(PROJECT, "android", "app", "src", "main", "res")
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

S = 1024
WHITE = (255, 255, 255)

VARIANTS = {
    # key: (背景渐变起, 背景渐变止, 大字符, 是否有班次)
    "default": ((52, 197, 102), (22, 126, 61), None, False),
    "day": ((93, 182, 0), (58, 130, 0), "白", True),
    "mid": ((252, 115, 141), (214, 62, 96), "中", True),
    "night": ((76, 111, 255), (40, 58, 190), "夜", True),
    "rest": ((118, 168, 129), (74, 122, 91), "休", True),
}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, c1, c2):
    img = Image.new("RGB", (size, size), c1)
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = 0.55 * (y / (size - 1)) + 0.45 * (x / (size - 1))
            px[x, y] = lerp(c1, c2, t)
    return img


def soft_glow(img):
    glow = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(glow)
    s = img.size[0]
    d.ellipse([-s * 0.35, -s * 0.55, s * 0.8, s * 0.35], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(s * 0.2))
    white = Image.new("RGB", img.size, WHITE)
    return Image.composite(white, img, glow.point(lambda v: int(v * 0.28)))


def rounded(img, radius_ratio=0.225):
    size = img.size
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0], size[1]], radius=int(size[0] * radius_ratio), fill=255
    )
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def draw_shift_foreground(size, char, color_hint):
    """自适应前景（透明）：居中白色粗体班次字（34%，留足安全边距，不会被 launcher 裁切）。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, int(size * 0.34))
    bbox = d.textbbox((0, 0), char, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(
        (size / 2 - tw / 2 - bbox[0], size / 2 - th / 2 - bbox[1]),
        char,
        font=font,
        fill=(255, 255, 255, 255),
    )
    return img


def draw_default_foreground(size):
    """默认图标前景：复用原 App 图标的自适应前景。"""
    src = Image.open(os.path.join(ICON_DIR, "app_icon_foreground.png")).convert("RGBA")
    return src.resize((size, size), Image.LANCZOS)


def build_legacy(size, key):
    c1, c2, char, is_shift = VARIANTS[key]
    bg = soft_glow(gradient(size, c1, c2)).convert("RGBA")
    if key == "default":
        src = Image.open(os.path.join(ICON_DIR, "app_icon.png")).convert("RGBA")
        return rounded(src.resize((size, size), Image.LANCZOS))
    fg = draw_shift_foreground(size, char, c1)
    out = Image.alpha_composite(bg, fg)
    return rounded(out)


def save_legacy(key):
    for density, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
        folder = os.path.join(RES, f"mipmap-{density}")
        os.makedirs(folder, exist_ok=True)
        img = build_legacy(1024, key).resize((px, px), Image.LANCZOS)
        img.save(os.path.join(folder, f"ic_shift_{key}.png"), "PNG")


def save_foreground(key):
    for density, px in (("mdpi", 108), ("hdpi", 162), ("xhdpi", 216), ("xxhdpi", 324), ("xxxhdpi", 432)):
        folder = os.path.join(RES, f"drawable-{density}")
        os.makedirs(folder, exist_ok=True)
        if key == "default":
            fg = draw_default_foreground(S)
        else:
            _, _, char, _ = VARIANTS[key]
            fg = draw_shift_foreground(S, char, VARIANTS[key][0])
        fg.resize((px, px), Image.LANCZOS).save(
            os.path.join(folder, f"ic_shift_{key}_fg.png"), "PNG"
        )


def save_adaptive_xml(key):
    folder = os.path.join(RES, "mipmap-anydpi-v26")
    os.makedirs(folder, exist_ok=True)
    # 自适应背景用渐变 drawable（比纯色更有质感）
    c1, c2, _char, is_shift = VARIANTS[key]
    bg_dir = os.path.join(RES, "drawable")
    os.makedirs(bg_dir, exist_ok=True)
    bg_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <gradient
        android:angle="270"
        android:startColor="#%02X%02X%02X"
        android:endColor="#%02X%02X%02X"
        android:type="linear" />
</shape>
""" % (c1[0], c1[1], c1[2], c2[0], c2[1], c2[2])
    with open(os.path.join(bg_dir, f"ic_shift_{key}_bg.xml"), "w", encoding="utf-8") as f:
        f.write(bg_xml)

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_shift_{key}_bg" />
    <foreground android:drawable="@drawable/ic_shift_{key}_fg" />
</adaptive-icon>
"""
    with open(os.path.join(folder, f"ic_shift_{key}.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_colors():
    folder = os.path.join(RES, "values")
    os.makedirs(folder, exist_ok=True)
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    for key, (c1, _c2, _ch, _sh) in VARIANTS.items():
        hexv = "#%02X%02X%02X" % c1
        lines.append(f'    <color name="ic_shift_{key}_bg">{hexv}</color>')
    lines.append("</resources>")
    lines.append("")
    with open(os.path.join(folder, "shift_icon_colors.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    for key in VARIANTS:
        save_legacy(key)
        save_foreground(key)
        save_adaptive_xml(key)
        print("generated", key)
    write_colors()
    print("done ->", RES)


if __name__ == "__main__":
    main()
