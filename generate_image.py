#!/usr/bin/env python3
"""Draw the front page of THE WORLD for Thursday 26 November 2026.

Everything on the page is painted in code with Pillow: the masthead, the
hero scene of the Strait of Hormuz at night, six story illustrations and
the briefs strip. No photo is used; no network is needed.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
PAPER = (247, 243, 232)
INK = (22, 22, 22)
NAVY = (18, 32, 58)
NAVY2 = (30, 52, 88)
RED = (163, 31, 31)
GOLD = (200, 162, 74)
GREY = (96, 96, 92)
LIGHT = (233, 227, 212)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit in width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    leading = leading or int(fnt.size * 1.22)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def gradient(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, y1 - y0)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=c)


def flame(draw, cx, base, w, h, seed=1):
    """A stylised flame: many thin overlapping ellipses, colour blending
    from deep orange at the base to pale yellow at the tip, with a slight
    sideways waver so it reads as fire, not a stack of discs."""
    rnd = random.Random(seed)
    steps = 14
    bot = (198, 66, 14)
    top = (255, 214, 96)
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(bot[c] + (top[c] - bot[c]) * t) for c in range(3))
        fw = w * (1 - t * 0.78) * rnd.uniform(0.94, 1.04)
        fh = h / steps * 2.1
        x = cx + math.sin(t * 5.0 + seed) * w * 0.06
        cy = base - t * h * 0.86
        draw.ellipse([x - fw / 2, cy - fh / 2, x + fw / 2, cy + fh / 2],
                     fill=col)


def smoke(draw, cx, cy, r, seed=2):
    rnd = random.Random(seed)
    for i in range(5):
        x = cx + rnd.uniform(-r, r) * 0.8
        y = cy - i * r * 0.42
        rr = r * (0.55 + i * 0.12)
        draw.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7],
                     fill=(58, 58, 66, 200))


def hero_scene(draw, box):
    """Night sea at Hormuz: burning tankers, missile streaks, smoke."""
    x0, y0, x1, y1 = box
    gradient(draw, box, (12, 20, 44), (66, 44, 34))
    # low sun glow on the horizon
    for r in range(150, 0, -6):
        a = int(70 * (1 - r / 150))
        draw.ellipse([x0 + 640 - r, y1 - 118 - r // 2, x0 + 640 + r,
                      y1 - 118 + r // 2], fill=(232, 130, 50, a))
    # stars
    rnd = random.Random(26)
    for _ in range(46):
        sx = rnd.uniform(x0 + 6, x1 - 6)
        sy = rnd.uniform(y0 + 6, y0 + 120)
        draw.point((sx, sy), fill=(220, 220, 200))
    horizon = y1 - 96
    # sea
    gradient(draw, (x0, horizon, x1, y1), (24, 38, 62), (10, 16, 32))
    for yy in range(horizon + 8, y1 - 6, 12):
        for xx in range(x0 + 12, x1 - 12, 46):
            draw.line([(xx, yy), (xx + 22, yy)], fill=(70, 96, 128), width=2)
    # moon
    draw.ellipse([x0 + 52, y0 + 26, x0 + 96, y0 + 70], fill=(232, 226, 196))
    draw.ellipse([x0 + 64, y0 + 34, x0 + 78, y0 + 48], fill=(206, 198, 166))
    # tanker 1 (left, burning)
    tx, ty = x0 + 120, horizon - 52
    draw.rectangle([tx, ty, tx + 240, ty + 52], fill=(14, 14, 18))
    draw.rectangle([tx + 150, ty - 26, tx + 196, ty], fill=(14, 14, 18))
    for wx in range(tx + 14, tx + 230, 26):
        draw.rectangle([wx, ty + 12, wx + 12, ty + 24], fill=(232, 160, 60))
    flame(draw, tx + 60, ty - 4, 74, 92, seed=3)
    flame(draw, tx + 190, ty - 4, 58, 70, seed=4)
    smoke(draw, tx + 120, ty - 44, 22, seed=5)
    # tanker 2 (right, burning)
    tx2, ty2 = x0 + 560, horizon - 44
    draw.rectangle([tx2, ty2, tx2 + 260, ty2 + 44], fill=(18, 18, 22))
    draw.rectangle([tx2 + 40, ty2 - 22, tx2 + 82, ty2], fill=(18, 18, 22))
    for wx in range(tx2 + 16, tx2 + 250, 26):
        draw.rectangle([wx, ty2 + 10, wx + 12, ty2 + 20], fill=(232, 160, 60))
    flame(draw, tx2 + 90, ty2 - 4, 66, 80, seed=6)
    flame(draw, tx2 + 210, ty2 - 4, 50, 62, seed=7)
    smoke(draw, tx2 + 150, ty2 - 40, 20, seed=8)
    # missile streaks arcing across the sky
    for (sx, sy, ex, ey) in [(x0 + 60, y0 + 150, x0 + 420, y0 + 60),
                             (x0 + 880, y0 + 170, x0 + 560, y0 + 70)]:
        steps = 24
        pts = []
        for i in range(steps + 1):
            t = i / steps
            px = sx + (ex - sx) * t
            py = sy + (ey - sy) * t - 46 * math.sin(math.pi * t)
            pts.append((px, py))
        draw.line(pts, fill=(255, 240, 200), width=3)
        draw.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 240, 200))
    # fire glow reflected on the water
    for cx in (tx + 120, tx2 + 150):
        for r in range(60, 0, -8):
            draw.ellipse([cx - r, horizon + 6, cx + r, horizon + 6 + r // 3],
                         outline=(232, 130, 50, 90), width=2)


def ill_ship(draw, box):
    """Container ship on a teal sea (tariffs)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(176, 208, 214))
    draw.rectangle([x0, y0 + 74, x1, y1], fill=(38, 84, 108))
    cols = [(163, 31, 31), (200, 162, 74), (30, 90, 60), (40, 70, 120)]
    for r, yy in enumerate((y0 + 30, y0 + 52)):
        for i in range(4):
            draw.rectangle([x0 + 8 + i * 27, yy, x0 + 32 + i * 27, yy + 20],
                           fill=cols[(i + r) % 4], outline=(20, 20, 20))
    draw.polygon([(x0 + 6, y0 + 74), (x0 + 112, y0 + 74), (x0 + 102, y0 + 92),
                  (x0 + 16, y0 + 92)], fill=(16, 16, 20))
    draw.rectangle([x0 + 88, y0 + 46, x0 + 104, y0 + 74], fill=(16, 16, 20))


def ill_missile(draw, box):
    """Ballistic missile on a launcher under a dark sky (North Korea)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(24, 28, 44))
    for sx, sy in [(x0 + 18, y0 + 16), (x0 + 92, y0 + 30), (x0 + 52, y0 + 12)]:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(220, 220, 200))
    draw.polygon([(x0 + 56, y0 + 8), (x0 + 66, y0 + 30), (x0 + 46, y0 + 30)],
                 fill=(200, 200, 200))
    draw.rectangle([x0 + 46, y0 + 30, x0 + 66, y0 + 78], fill=(150, 40, 36))
    draw.rectangle([x0 + 40, y0 + 78, x0 + 72, y0 + 84], fill=(60, 60, 60))
    draw.line([(x0 + 30, y0 + 100), (x0 + 82, y0 + 100)], fill=(90, 90, 90),
              width=4)
    flame(draw, x0 + 56, y0 + 108, 26, 22, seed=9)
    draw.ellipse([x0 + 84, y0 + 60, x0 + 112, y0 + 88], fill=(232, 130, 50))


def ill_airfield(draw, box):
    """Airfield runway with a jet and a fireball (Ukraine strike)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(214, 208, 188))
    draw.polygon([(x0, y1), (x0 + 44, y0 + 52), (x1, y0 + 52), (x1, y1)],
                 fill=(70, 70, 74))
    for i in range(5):
        yy = y0 + 58 + i * 10
        wdt = 6 + i * 5
        draw.line([(x0 + 52 - i * 4, yy), (x0 + 52 - i * 4 + wdt, yy)],
                  fill=(240, 240, 220), width=2)
    # jet silhouette
    draw.polygon([(x0 + 22, y0 + 34), (x0 + 58, y0 + 26), (x0 + 96, y0 + 34),
                  (x0 + 58, y0 + 42)], fill=(30, 30, 34))
    draw.polygon([(x0 + 58, y0 + 26), (x0 + 66, y0 + 12), (x0 + 70, y0 + 26)],
                 fill=(30, 30, 34))
    flame(draw, x0 + 92, y0 + 44, 34, 40, seed=10)


def ill_parade(draw, box):
    """Thanksgiving parade balloon over a crowd (storm-grey sky)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(148, 164, 178))
    draw.ellipse([x0 + 22, y0 + 10, x0 + 92, y0 + 62], fill=(232, 120, 60))
    draw.ellipse([x0 + 34, y0 + 22, x0 + 46, y0 + 34], fill=(255, 255, 255))
    draw.line([(x0 + 40, y0 + 62), (x0 + 34, y0 + 96)], fill=(60, 60, 60),
              width=2)
    draw.line([(x0 + 74, y0 + 62), (x0 + 80, y0 + 96)], fill=(60, 60, 60),
              width=2)
    rnd = random.Random(12)
    for _ in range(14):
        cx = rnd.uniform(x0 + 4, x1 - 4)
        cy = rnd.uniform(y0 + 66, y1 - 6)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2],
                     fill=rnd.choice([(163, 31, 31), (200, 162, 74),
                                      (40, 70, 120), (30, 90, 60)]))
    draw.rectangle([x0, y1 - 10, x1, y1], fill=(40, 44, 52))


def ill_space(draw, box):
    """Satellite constellation over Earth (SpaceX approval)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(10, 14, 30))
    rnd = random.Random(13)
    for _ in range(22):
        sx = rnd.uniform(x0 + 4, x1 - 4)
        sy = rnd.uniform(y0 + 4, y0 + 70)
        draw.point((sx, sy), fill=(220, 220, 200))
    draw.ellipse([x0 + 4, y1 - 24, x0 + 88, y1 + 6], fill=(38, 84, 140))
    draw.arc([x0 + 4, y1 - 24, x0 + 88, y1 + 6], 200, 330,
             fill=(120, 180, 220), width=3)
    for (sx, sy) in [(x0 + 66, y0 + 26), (x0 + 92, y0 + 46), (x0 + 44, y0 + 52)]:
        draw.rectangle([sx - 9, sy - 3, sx - 2, sy + 3], fill=(180, 180, 190))
        draw.rectangle([sx + 2, sy - 3, sx + 9, sy + 3], fill=(180, 180, 190))
        draw.rectangle([sx - 2, sy - 5, sx + 2, sy + 5], fill=(220, 220, 230))
    draw.ellipse([x0 + 8, y0 + 8, x1 - 8, y0 + 78], outline=(120, 140, 180),
                 width=1)


def ill_candles(draw, box):
    """Memorial candles (Hong Kong tower fire)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(32, 28, 34))
    for i, cx in enumerate((x0 + 28, x0 + 58, x0 + 88)):
        draw.rectangle([cx - 7, y0 + 56, cx + 7, y1 - 8], fill=(232, 226, 200))
        flame(draw, cx, y0 + 54, 14, 26, seed=14 + i)
    draw.rectangle([x0, y1 - 8, x1, y1], fill=(70, 60, 66))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- masthead ----
    d.rectangle([MARGIN, 22, W - MARGIN, 118], fill=NAVY)
    d.rectangle([MARGIN, 22, W - MARGIN, 118], outline=GOLD, width=2)
    title = font(SERIF_B, 62)
    tw = d.textlength("THE WORLD", font=title)
    d.text(((W - tw) / 2, 26), "THE WORLD", font=title, fill=(247, 243, 232))
    sub = font(SANS, 17)
    line = "THURSDAY, 26 NOVEMBER 2026  •  THE DAY IN ONE PAGE  •  No. 331"
    sw = d.textlength(line, font=sub)
    d.text(((W - sw) / 2, 92), line, font=sub, fill=(200, 162, 74))
    d.line([(MARGIN, 126), (W - MARGIN, 126)], fill=INK, width=2)

    # ---- hero scene (rendered on its own layer so nothing escapes) ----
    hw, hh = W - 2 * MARGIN, 236
    layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer, "RGBA")
    hero_scene(ld, (0, 0, hw, hh))
    img.paste(layer, (MARGIN, 136), layer)
    d.rectangle([MARGIN, 136, W - MARGIN, 136 + hh], outline=INK, width=2)
    d.rectangle([MARGIN, 136 + hh, W - MARGIN, 136 + hh + 4], fill=GOLD)

    # ---- lead headline ----
    y = 382
    y = para(d, MARGIN, y,
             "U.S. STRIKES THREE IRANIAN TANKERS AS TEHRAN FIRES MISSILES AT A CARRIER",
             font(SERIF_B, 33), W - 2 * MARGIN, leading=40)
    y = para(d, MARGIN, y + 4,
             "Tanker war escalates in the Strait of Hormuz: Washington says its warships "
             "dodged the missiles; Iran says it hit three more tankers on an "
             "\u201cunauthorised route\u201d. Oil flows on as the strait stays open.",
             font(SERIF, 19), W - 2 * MARGIN, fill=(52, 52, 48), leading=24)
    d.line([(MARGIN, y + 8), (W - MARGIN, y + 8)], fill=INK, width=2)

    # ---- story cards ----
    cards = [
        (ill_ship, "TARIFFS, ACT TWO",
         "Trump unveils new duties on 14 trading partners \u2014 China, India and Europe in the firing line.",
         "WASHINGTON"),
        (ill_missile, "PYONGYANG",
         "Kim Jong Un orders tactical nuclear weapons deployed more widely, calling for a diversified nuclear force.",
         "SEOUL"),
        (ill_airfield, "UKRAINE",
         "Kyiv says it struck a major Russian air base, damaging five planes, as the war grinds into another winter.",
         "KYIV"),
        (ill_parade, "THANKSGIVING",
         "The 100th Macy\u2019s parade is postponed two days as a major storm hits; king tides batter the California coast.",
         "NEW YORK"),
        (ill_space, "ORBIT",
         "SpaceX wins U.S. approval to launch a million satellites to power orbital data centres.",
         "WASHINGTON"),
        (ill_candles, "HONG KONG",
         "The city remembers the 168 people killed in the housing-complex fire, one week on.",
         "HONG KONG"),
    ]
    cw, ch, gap = 472, 120, 12
    x0, y0 = MARGIN, 536
    for i, (ill, kicker, text, dateline) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * (ch + 14)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=(255, 255, 255),
                    outline=(180, 174, 158), width=1)
        ill(d, (cx + 8, cy + 8, cx + 124, cy + ch - 8))
        tx = cx + 134
        d.text((tx, cy + 8), kicker, font=font(SANS_B, 14), fill=RED)
        d.text((tx, cy + 27), dateline, font=font(SANS, 12), fill=GREY)
        para(d, tx, cy + 46, text, font(SERIF, 16), cw - 144, leading=20)

    # ---- briefs strip ----
    by = 536 + 3 * ch + 2 * gap + 14
    d.rectangle([MARGIN, by, W - MARGIN, by + 76], fill=NAVY)
    d.text((MARGIN + 14, by + 8), "IN BRIEF", font=font(SANS_B, 15),
           fill=GOLD)
    briefs = ("Cairo fuel-tanker crash fire kills 31  •  U.S. jobless claims fall "
              "to 189,000  •  Second judge blocks Trump\u2019s birthright order  •  "
              "Houthis strike Riyadh again  •  Duran Duran guitarist Andy Taylor "
              "dies at 65  •  Six dead in plane crash off the U.S. coast")
    para(d, MARGIN + 14, by + 30, briefs, font(SANS, 15),
         W - 2 * MARGIN - 28, fill=(232, 228, 214), leading=19)

    out = os.environ.get("OUT", "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
