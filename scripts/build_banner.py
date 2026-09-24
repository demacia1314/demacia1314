#!/usr/bin/env python3
"""
Compose the demacia1314 profile banner: assets/banner.png

The background is generated art (via the chatgpt2api image skill), but every
glyph of text is drawn here from a hand-built 5x7 pixel font.

That split is deliberate. Image models render plausible-looking text that is
frequently wrong -- one generated attempt invented "42 Repositories / 276
Commits / 18 Pull Requests / 7 Followers", none of which are true. Any number
that appears in this banner is drawn from the constants below.

Usage:
    py -3 scripts/build_banner.py [--bg path/to/background.png]
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFilter

W, H = 1600, 900

# ---------------------------------------------------------------------------
# verified figures (see README.md for provenance)
# ---------------------------------------------------------------------------
STATS = [
    ("6", "REPOS"),
    ("0", "FOLLOWERS"),
    ("1", "FOLLOWING"),
    ("48", "COMMITS"),
    ("6", "COMPS"),
]

TERMINAL = [
    ("demacia1314:~$", "whoami", "prompt"),
    ("", "demacia1314", "out"),
    ("demacia1314:~$", "cat kaggle.json", "prompt"),
    ("", '{ "tier": "EXPERT",', "ok"),
    ("", '  "silver": 1, "bronze": 1 }', "ok"),
]

MEDALS = [
    ("SILVER", "45 / 4,186", "AI Agent Security", (203, 213, 225), (124, 135, 152)),
    ("BRONZE", "402 / 6,807", "Pokemon TCG Battle", (205, 138, 82), (138, 82, 40)),
]

TIER = ("EXPERT", "1,617 / 217,552", "top 0.74%")

# Prompt separator. A hyphen collides with the following glyph at this scale
# because TRACK leaves only one column of gap, so a two-column dot is used.
PROMPT_SEP = "."

# ---------------------------------------------------------------------------
# palette
# ---------------------------------------------------------------------------
NAVY      = (8, 17, 31)
NAVY_2    = (6, 12, 22)
CYAN      = (0, 229, 255)
CYAN_DIM  = (11, 127, 146)
GREEN     = (62, 240, 138)
GOLD      = (245, 197, 66)
PINK      = (255, 107, 181)
WHITE     = (234, 243, 255)
SLATE     = (157, 176, 201)
MUTED     = (95, 115, 145)

# ---------------------------------------------------------------------------
# 5x7 pixel font
# ---------------------------------------------------------------------------
F = {
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "c": [".....", ".....", ".####", "#....", "#....", "#....", ".####"],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "f": ["..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."],
    "g": [".....", ".####", "#...#", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "j": ["...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#...#"],
    "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "p": [".....", "####.", "#...#", "#...#", "####.", "#....", "#...."],
    "q": [".....", ".####", "#...#", "#...#", ".####", "....#", "....#"],
    "r": [".....", ".....", "#.##.", "##...", "#....", "#....", "#...."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "y": [".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "%": ["#...#", "...#.", "..#..", "..#..", ".#...", "#...#", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "{": ["..##.", ".#...", ".#...", "##...", ".#...", ".#...", "..##."],
    "}": [".##..", "...#.", "...#.", "...##", "...#.", "...#.", ".##.."],
    ">": ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    "<": ["....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "~": [".....", ".....", ".##.#", "#..#.", ".....", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "·": [".....", ".....", ".....", "..##.", "..##.", ".....", "....."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}

GLYPH_W, GLYPH_H, TRACK = 5, 7, 6


def text_width(s, scale):
    return len(s) * TRACK * scale - scale


def draw_text(d, s, x, y, scale, color):
    cx = x
    for ch in s:
        g = F.get(ch) or F.get(ch.lower()) or F[" "]
        for ry, row in enumerate(g):
            rx = 0
            while rx < GLYPH_W:
                if row[rx] == "#":
                    run = 1
                    while rx + run < GLYPH_W and row[rx + run] == "#":
                        run += 1
                    d.rectangle(
                        [cx + rx * scale, y + ry * scale,
                         cx + (rx + run) * scale - 1, y + (ry + 1) * scale - 1],
                        fill=color)
                    rx += run
                else:
                    rx += 1
        cx += TRACK * scale
    return cx


def panel(d, x, y, w, h, title=None, accent=CYAN):
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=NAVY,
                        outline=accent, width=3)
    d.rounded_rectangle([x + 7, y + 7, x + w - 7, y + h - 7], radius=6,
                        outline=(27, 41, 66), width=2)
    for cx_, cy_ in ((x, y), (x + w - 12, y), (x, y + h - 12),
                     (x + w - 12, y + h - 12)):
        d.rectangle([cx_, cy_, cx_ + 12, cy_ + 12], fill=accent)
    if title:
        draw_text(d, title, x + 26, y + 24, 4, accent)


def draw_medal(d, cx, cy, r, light, dark, glyph):
    # ribbon: kept short so it cannot reach a panel title above the row
    rib = 14
    d.polygon([(cx - 20, cy - r - rib), (cx - 4, cy - r - rib),
               (cx - 12, cy - r + 6)], fill=dark)
    d.polygon([(cx + 4, cy - r - rib), (cx + 20, cy - r - rib),
               (cx + 12, cy - r + 6)], fill=light)
    # body
    import math
    pts = []
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=light, outline=dark)
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62],
              fill=NAVY_2, outline=dark, width=2)
    draw_text(d, glyph, cx - text_width(glyph, 3) / 2, cy - 10, 3, light)


def build(bg_path, out_path):
    bg = Image.open(bg_path).convert("RGB").resize((W, H), Image.LANCZOS)
    bg = bg.point(lambda v: int(v * 0.62))          # push it back into texture
    canvas = bg.convert("RGBA")

    # ---- glow pass for the title ------------------------------------------
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    draw_text(gd, "demacia1314", 80, 74, 14, CYAN)
    glow = glow.filter(ImageFilter.GaussianBlur(11))
    canvas = Image.alpha_composite(canvas, glow)

    d = ImageDraw.Draw(canvas)

    # ---- title + roles ----------------------------------------------------
    draw_text(d, "demacia1314", 80, 74, 14, WHITE)
    d.rectangle([80, 184, 80 + text_width("demacia1314", 14), 190], fill=CYAN)

    rx = 84
    for i, (label, col) in enumerate((("AI", CYAN), ("CV", GREEN),
                                      ("Agents", GOLD),
                                      ("Competitions", PINK))):
        if i:
            draw_text(d, "·", rx, 206, 5, CYAN_DIM)
            rx += 36
        draw_text(d, label, rx, 206, 5, col)
        rx += text_width(label, 5) + 30

    # ---- full-width stat strip -------------------------------------------
    sx, sy, sw_, sh_ = 76, 258, 1448, 118
    panel(d, sx, sy, sw_, sh_)
    seg = (sw_ - 40) / len(STATS)
    for i, (val, label) in enumerate(STATS):
        cx = sx + 20 + seg * i + seg / 2
        if i:
            d.rectangle([sx + 20 + seg * i, sy + 24, sx + 22 + seg * i,
                         sy + sh_ - 24], fill=(27, 41, 66))
        draw_text(d, val, cx - text_width(val, 7) / 2, sy + 28, 7, WHITE)
        draw_text(d, label, cx - text_width(label, 3) / 2, sy + 82, 3, MUTED)

    # ---- left column: terminal -------------------------------------------
    px, py, pw, ph = 76, 392, 1006, 368
    panel(d, px, py, pw, ph, title="TERMINAL")
    d.rounded_rectangle([px + 18, py + 62, px + pw - 18, py + ph - 18],
                        radius=6, fill=NAVY_2, outline=(27, 41, 66), width=2)
    ly = py + 86
    for prompt, cmd, kind in TERMINAL:
        col = CYAN if kind == "prompt" else (GREEN if kind == "ok" else SLATE)
        if prompt:
            draw_text(d, prompt, px + 40, ly, 4, CYAN)
        draw_text(d, cmd,
                  px + 40 + (text_width(prompt, 4) + 28 if prompt else 0),
                  ly, 4, col)
        ly += 50
    d.rectangle([px + 40, ly - 2, px + 46, ly + 20], fill=CYAN)

    # ---- right column: tier ----------------------------------------------
    tx, ty, tw, th = 1106, 392, 418, 136
    panel(d, tx, ty, tw, th)
    draw_text(d, "TIER", tx + 26, ty + 26, 3, SLATE)
    d.rectangle([tx + 26, ty + 46, tx + tw - 26, ty + 48], fill=(27, 41, 66))
    lvl, rank, pct = TIER
    draw_text(d, lvl, tx + tw / 2 - text_width(lvl, 7) / 2, ty + 54, 7, GREEN)
    # rank on its own line: at scale 3 the rank and percentile together are
    # wider than the panel interior, so they must not share a row
    draw_text(d, rank, tx + tw / 2 - text_width(rank, 3) / 2, ty + 108, 3,
              SLATE)

    # ---- right column: medals --------------------------------------------
    mx, my, mw, mh = 1106, 542, 418, 218
    panel(d, mx, my, mw, mh, title="MEDALS")
    for i, (name, rank, comp, light, dark) in enumerate(MEDALS):
        top = my + 46 + i * 82
        d.rectangle([mx + 20, top, mx + mw - 20, top + 74], fill=(11, 20, 34),
                    outline=(27, 41, 66))
        draw_medal(d, mx + 62, top + 40, 21, light, dark, "1" if i == 0 else "3")
        tx_ = mx + 100
        draw_text(d, name, tx_, top + 10, 3, light)
        draw_text(d, rank, tx_, top + 32, 3, WHITE)
        draw_text(d, comp, tx_, top + 58, 2.2, MUTED)

    # ---- footer -----------------------------------------------------------
    d.rectangle([76, 786, 1524, 788], fill=(27, 41, 66))
    draw_text(d, "Good Code · Brighter Tomorrows", 76, 812, 3, MUTED)
    draw_text(d, "github.com/demacia1314",
              1524 - text_width("github.com/demacia1314", 3), 812, 3, CYAN_DIM)

    canvas.convert("RGB").save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default=os.path.expandvars(
        r"%TEMP%\bg-gen\image_r001_i02_ultra-wide-16-9-empty-dark-tech-hud-frame-backgr.png"))
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(here), "assets", "banner.png"))
    a = ap.parse_args()
    out = build(a.bg, a.out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
