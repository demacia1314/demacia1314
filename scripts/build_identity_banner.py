#!/usr/bin/env python3
"""
Build the demacia1314 profile banner: assets/identity-banner.svg

Design notes
------------
Shares the dark-navy / neon-cyan pixel language of the reference aesthetic but
uses an original composition:

  * a single wide identity banner instead of a multi-panel dashboard
  * name rendered in a hand-built 5x7 pixel font, not a system typeface
  * avatar in a hexagonal pixel frame
  * circuit-trace motif for decoration
  * one terminal window running the full width

Run `py -3 scripts/build_identity_banner.py` to regenerate.
"""

import base64
import math
import os

W, H = 1400, 660

BG        = "#04070e"
FRAME     = "#0d1b2e"
FRAME_2   = "#101f36"
LINE      = "#1b2942"
CYAN      = "#00e5ff"
CYAN_DIM  = "#0b7f92"
CYAN_DEEP = "#123a5c"
GREEN     = "#3ef08a"
WHITE     = "#eaf3ff"
MUTED     = "#5f7391"
SLATE     = "#9db0c9"
GOLD      = "#f5c542"
SILVER    = "#cbd5e1"
BRONZE    = "#cd8a52"
PINK      = "#ff6bb5"

MONO = ("ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
        "'Courier New', monospace")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def data_uri(rel_path):
    """Inline a PNG as a data URI.

    GitHub renders README images through its camo proxy with a CSP that blocks
    SVG-embedded external loads, so the avatar has to travel inside the SVG
    itself.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(here), rel_path)
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


# ----------------------------------------------------------------------------
# 5x7 pixel font, for the large name
# ----------------------------------------------------------------------------
FONT = {
    "a": [".....", ".###.", "....#", ".####", "#...#", ".####", "....."],
    "c": [".....", ".####", "#....", "#....", "#....", ".####", "....."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", ".####", "....."],
    "e": [".....", ".###.", "#...#", "#####", "#....", ".###.", "....."],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", ".###.", "....."],
    "m": [".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "....."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", ".###.", "....."],
    "3": ["####.", "....#", "..##.", "....#", "#...#", ".###.", "....."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "....."],
}


def pixel_text(svg, text, x, y, scale, fill, glow=False):
    """Draw text using the 5x7 font. `scale` px per font pixel."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += scale * 4
            continue
        for ry, row in enumerate(glyph):
            run = 0
            for rx in range(len(row) + 1):
                bit = rx < len(row) and row[rx] == "#"
                if bit:
                    run += 1
                elif run:
                    svg.rect(cx + (rx - run) * scale, y + ry * scale,
                             run * scale, scale, fill=fill,
                             opacity="0.35" if glow else None)
                    run = 0
        cx += scale * 6


def pixel_width(text, scale):
    return sum(scale * (6 if c in FONT else 4) for c in text) - scale


class SVG:
    def __init__(self):
        self.p = []
        # measured text boxes: (x, y, x2, y2, label) for the overlap audit
        self.boxes = []

    def measure(self, x, y, s, size, anchor="start", label=""):
        """Record an approximate bounding box for a text run.

        MONO is a monospace stack, so advance width is ~0.6em for ASCII and
        ~1.0em for the wide punctuation used here.
        """
        adv = sum(0.6 if ord(c) < 0x2000 else 1.0 for c in s) * size
        if anchor == "middle":
            x -= adv / 2
        elif anchor == "end":
            x -= adv
        self.boxes.append((x, y - size * 0.78, x + adv, y + size * 0.24,
                           (label or s)[:48]))
        return adv

    def add(self, s):
        self.p.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1, rx=0,
             dash=None, opacity=None):
        a = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
             f'height="{h:.1f}" rx="{rx}" fill="{fill}"')
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1, dash=None, opacity=None):
        a = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
             f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def text(self, x, y, s, size=12, fill=WHITE, weight=500, anchor="start",
             spacing=None, opacity=None, track=False):
        if track:
            self.measure(x, y, s, size, anchor)
        a = (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" '
             f'font-size="{size}" fill="{fill}" font-weight="{weight}"')
        if anchor != "start":
            a += f' text-anchor="{anchor}"'
        if spacing:
            a += f' letter-spacing="{spacing}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.measure(x, y, s, size, anchor)
        self.add(a + f">{esc(s)}</text>")

    def circle(self, cx, cy, r, fill, stroke=None, sw=1, opacity=None):
        a = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def path(self, d, fill="none", stroke=None, sw=1, dash=None, opacity=None):
        a = f'<path d="{d}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def poly(self, pts, fill, stroke=None, sw=1, opacity=None):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")


def sprite(s, ox, oy, rows, colors, scale):
    for ry, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == ch:
                run += 1
            s.rect(ox + x * scale, oy + ry * scale, run * scale, scale,
                   fill=colors[ch])
            x += run


# ----------------------------------------------------------------------------
# avatar: hooded coder in a hexagonal frame
# ----------------------------------------------------------------------------
AV = {
    "c": CYAN, "C": "#0a6d80",
    "f": "#f0c49b", "s": "#241b2e",
    "k": "#0e0c14", "w": "#8ef7ff",
    "v": "#16233b", "V": "#0d1524",
    "g": GREEN,
}
AV_ROWS = [
    "....cccccc........",
    "..cccccccccc......",
    "..cccccccccc......",
    ".cccccccccccc.....",
    ".cccccCCcccccc....",
    ".ccffffffffcc.....",
    ".ccffssssssfc.....",
    ".ccffssssssfc.....",
    ".ccfswwsswwfc.....",
    "..cfsssssssfc.....",
    "..cffssssfffc.....",
    "...cfffffffcc.....",
    "....cffffffc......",
    "...vvvcccc.vv.....",
    "..vvvvccccvvvv....",
    ".vvvvvccccvvvvv...",
    "vvvvvvccccvvvvvv..",
    "VvvvvvccccvvvvvV..",
    ".VvvvvccccvvvvV...",
    "..VVvvvcccvVV.....",
    "...VVVvvvVVV......",
    "....VVVVVVV.......",
]

CAT = {"o": "#e8823c", "O": "#b8571a", "w": "#fff6e8", "k": "#1a1208",
       "p": "#ff8fa3"}
CAT_ROWS = [
    ".o...o.",
    "oOo.oOo",
    "oOoooOo",
    "oOwkwwO",
    "oOopppO",
    ".oOwwwO",
    ".oOOOo.",
]


def audit(boxes):
    """Report overlapping text boxes.

    Text is drawn back-to-front, so any overlap between two measured runs is a
    real collision rather than intentional layering.
    """
    hits = []
    bx = sorted(boxes)
    for i in range(len(bx)):
        ax1, ay1, ax2, ay2, al = bx[i]
        for j in range(i + 1, len(bx)):
            cx1, cy1, cx2, cy2, cl = bx[j]
            if cx1 >= ax2:
                break
            ox = min(ax2, cx2) - max(ax1, cx1)
            oy = min(ay2, cy2) - max(ay1, cy1)
            if ox > 1 and oy > 1:
                hits.append((al, cl, ox, oy))
    return hits


def build():
    s = SVG()
    s.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
          f'viewBox="0 0 {W} {H}">')
    s.add(f'''<defs>
  <linearGradient id="bgG" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#060c18"/>
    <stop offset="50%" stop-color="#04070e"/>
    <stop offset="100%" stop-color="#070f1e"/>
  </linearGradient>
  <linearGradient id="hexG" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0d2138"/>
    <stop offset="100%" stop-color="#071120"/>
  </linearGradient>
  <linearGradient id="accG" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.9"/>
    <stop offset="55%" stop-color="#00e5ff" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="silverG" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="38%" stop-color="#e2e8f0"/>
    <stop offset="72%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#7c8798"/>
  </linearGradient>
</defs>''')

    s.rect(0, 0, W, H, fill="url(#bgG)")

    # ------------------------------------------------------------------
    # outer frame with asymmetric corner marks (L-brackets, not full sets)
    # ------------------------------------------------------------------
    m = 22
    s.rect(m, m, W - 2 * m, H - 2 * m, fill="#070d19", stroke=LINE, sw=1.3, rx=5)
    br = 26  # bracket arm
    for (bx, by, dx, dy) in ((m, m, 1, 1), (W - m, m, -1, 1),
                             (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        s.line(bx, by, bx + dx * br, by, stroke=CYAN, sw=2.4)
        s.line(bx, by, bx, by + dy * br, stroke=CYAN, sw=2.4)

    # ------------------------------------------------------------------
    # circuit-trace decoration (right side)
    # ------------------------------------------------------------------
    for k, (ty, col, op) in enumerate(((120, CYAN, "0.5"), (170, CYAN_DEEP, "0.75"),
                                       (215, GREEN, "0.35"))):
        y = ty
        s.path(f"M{W-m-14} {y} H{W-m-120} l-26 26 H{W-m-300}", fill="none",
               stroke=col, sw=1.1, opacity=op, dash="6,5")
        s.circle(W - m - 300, y + 26, 2.6, fill=col, opacity=op)
    for k in range(5):
        s.rect(W - m - 60 - k * 22, 300, 10, 10, fill=CYAN_DEEP,
               opacity=f"{0.7 - k*0.11:.2f}", rx=1)

    # ------------------------------------------------------------------
    # avatar: hexagon + pixel portrait
    # ------------------------------------------------------------------
    ax, ay, arad = 150, 250, 104
    import math
    hexp = [(ax + arad * math.cos(math.radians(a - 90)),
             ay + arad * math.sin(math.radians(a - 90)))
            for a in range(0, 360, 60)]
    s.poly(hexp, fill="url(#hexG)", stroke=CYAN, sw=2)
    hexp2 = [(ax + (arad - 11) * math.cos(math.radians(a - 90)),
              ay + (arad - 11) * math.sin(math.radians(a - 90)))
             for a in range(0, 360, 60)]
    s.poly(hexp2, fill="none", stroke=CYAN_DEEP, sw=1, opacity="0.8")
    s.add(f'<clipPath id="hexc"><polygon points="'
          + " ".join(f"{x:.1f},{y:.1f}" for x, y in hexp2) + '"/></clipPath>')
    s.add('<g clip-path="url(#hexc)">')
    s.rect(ax - arad, ay - arad, arad * 2, arad * 2, fill="#071120")
    s.add(f'<image x="{ax - arad + 4:.1f}" y="{ay - arad + 4:.1f}" '
          f'width="{arad * 2 - 8:.1f}" height="{arad * 2 - 8:.1f}" '
          f'preserveAspectRatio="xMidYMid meet" '
          f'href="{data_uri("assets/avatar-pixel.png")}"/>')
    s.add('</g>')

    # ------------------------------------------------------------------
    # name + roles
    # ------------------------------------------------------------------
    nx = 300
    s.text(nx, 118, "> IDENTITY // demacia1314", size=11.5, fill=CYAN_DIM,
           weight=700, spacing="1.6")
    s.rect(nx, 128, 128, 1.4, fill="url(#accG)")

    name = "demacia1314"
    nsc = 11
    pixel_text(s, name, nx + 2, 150, nsc, CYAN, glow=True)
    pixel_text(s, name, nx + 2, 150, nsc, WHITE)

    # caret
    s.rect(nx + pixel_width(name, nsc) + 22, 150, nsc + 2, 7 * nsc, fill=CYAN,
           opacity="0.9")

    # roles as a dot-separated line, not chips
    ry = 258
    roles = [("AI", CYAN), ("CV", GREEN), ("Agents", GOLD), ("Competitions", PINK)]
    rx = nx + 2
    for i, (label, col) in enumerate(roles):
        if i:
            s.text(rx, ry, "·", size=15, fill=CYAN_DEEP, weight=800)
            rx += 14
        s.text(rx, ry, label, size=14.5, fill=col, weight=700, spacing="0.4")
        rx += 7.2 * len(label) + 12

    s.text(nx + 2, ry + 30,
           "Building intelligent systems for a better tomorrow.",
           size=13, fill=SLATE, weight=500)
    s.text(nx + 2, ry + 52,
           "Kaggle Expert · 1 silver, 1 bronze", size=12, fill=MUTED,
           weight=600)

    # ------------------------------------------------------------------
    # stat strip (horizontal, replaces the sidebar column)
    # ------------------------------------------------------------------
    sy = 350
    stats = [("REPOS", "6"), ("FOLLOWERS", "0"), ("FOLLOWING", "1"),
             ("COMMITS / YR", "48"), ("COMPETITIONS", "6")]
    seg = (W - 2 * m - 60) / len(stats)
    s.rect(m + 30, sy, W - 2 * m - 60, 74, fill="#08111f", stroke=LINE, rx=4)
    for i, (label, val) in enumerate(stats):
        cx = m + 30 + seg * i + seg / 2
        if i:
            s.line(m + 30 + seg * i, sy + 14, m + 30 + seg * i, sy + 60,
                   stroke=LINE)
        s.text(cx, sy + 34, val, size=21, fill=WHITE, weight=900, anchor="middle")
        s.text(cx, sy + 54, label, size=9, fill=MUTED, weight=700,
               anchor="middle", spacing="1.2")

    # ------------------------------------------------------------------
    # terminal window (left) + medal card (right), side by side
    # ------------------------------------------------------------------
    ty = 442
    th = 158
    gap = 16
    card_w = 280
    term_w = W - 2 * m - 60 - gap - card_w

    s.rect(m + 30, ty, term_w, th, fill="#060c16", stroke=LINE, sw=1.2, rx=5)
    s.rect(m + 30, ty, term_w, 26, fill="#0b1524", rx=5)
    s.rect(m + 30, ty + 16, term_w, 10, fill="#0b1524")
    s.line(m + 30, ty + 26, m + 30 + term_w, ty + 26, stroke=LINE)
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        s.circle(m + 48 + i * 16, ty + 13, 4.6, fill=col)
    s.text(m + 30 + term_w / 2, ty + 17, "demacia1314 — zsh",
           size=10, fill=MUTED, weight=600, anchor="middle")

    lines = [
        ("demacia1314:~$", "whoami", CYAN, WHITE),
        ("", "AI researcher · computer vision · agents", None, SLATE),
        ("", "", None, None),
        ("demacia1314:~$", "cat kaggle.json", CYAN, WHITE),
        ("", '{ "tier": "EXPERT", "gold": 0,', None, GREEN),
        ("", '  "silver": 1, "bronze": 1, "competitions": 6 }', None, GREEN),
    ]
    ly = ty + 50
    caret_at = None
    for prompt, cmd, pcol, ccol in lines:
        if prompt:
            s.text(m + 52, ly, prompt, size=12, fill=pcol, weight=700)
        if cmd:
            off = 14.5 * len(prompt) if prompt else 0
            s.text(m + 52 + off, ly, cmd, size=12, fill=ccol, weight=600)
            caret_at = (m + 52 + off + 7.2 * len(cmd) + 8, ly)
        ly += 21

    if caret_at:
        s.rect(caret_at[0], caret_at[1] - 10, 7, 13, fill=CYAN, opacity="0.85")

    # ------------------------------------------------------------------
    # medal card, right of the terminal
    # ------------------------------------------------------------------
    bx = m + 30 + term_w + gap
    s.rect(bx, ty, card_w, th, fill="#08101d", stroke=LINE, sw=1.2, rx=5)
    s.text(bx + 16, ty + 24, "MEDALS", size=10, fill=CYAN, weight=800,
           spacing="1.2")
    s.line(bx + 16, ty + 32, bx + card_w - 16, ty + 32, stroke=LINE)

    for k, (cx_, fill, stroke, glyph, gcol) in enumerate((
            (bx + 52, "url(#silverG)", "#f8fafc", "Ag", SILVER),
            (bx + 124, BRONZE, "#f3d0a8", "Bz", "#f3d0a8"))):
        cy_ = ty + 66
        s.poly([(cx_, cy_ - 22), (cx_ + 17, cy_ - 22), (cx_ + 26, cy_ - 13),
                (cx_ + 26, cy_ + 3), (cx_ + 17, cy_ + 12), (cx_, cy_ + 12),
                (cx_ - 9, cy_ + 3), (cx_ - 9, cy_ - 13)],
               fill=fill, stroke=stroke, sw=1.1)
        s.circle(cx_ + 8.5, cy_ - 5, 7.4, fill="#0b1220",
                 stroke=stroke if k else SLATE)
        s.text(cx_ + 8.5, cy_ - 2, glyph, size=7, fill=gcol, weight=900,
               anchor="middle")
        s.text(cx_ + 8.5, cy_ + 26, ("SILVER", "BRONZE")[k], size=8.5,
               fill=stroke if k else SLATE, weight=800, anchor="middle",
               spacing="1")

    s.text(bx + card_w / 2, ty + 120, "1 silver · 1 bronze", size=10.5,
           fill=MUTED, weight=600, anchor="middle")
    s.text(bx + card_w / 2, ty + 138, "EXPERT · 6 competitions", size=10,
           fill=GREEN, weight=700, anchor="middle")

    # ------------------------------------------------------------------
    # footer
    # ------------------------------------------------------------------
    s.line(m + 30, H - 54, W - m - 30, H - 54, stroke=LINE)
    s.text(m + 30, H - 32, "Good Code  ·  Brighter Tomorrows", size=10.5,
           fill=MUTED, weight=600)
    s.text(W - m - 30, H - 32, "github.com/demacia1314", size=10.5,
           fill=CYAN_DIM, weight=700, anchor="end")

    s.add("</svg>")
    return "\n".join(s.p), s.boxes


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here), "assets", "identity-banner.svg")
    svg, svg_obj = build()
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print(f"wrote {out}  ({len(svg):,} bytes)")

    hits = audit(svg_obj)
    if hits:
        print(f"\n!! {len(hits)} overlapping text run(s):")
        for a, b, ox, oy in sorted(hits, key=lambda h: -h[3])[:12]:
            print(f"   {oy:5.1f}px vertical overlap: {a!r}  <->  {b!r}")
        return 1
    print("layout audit: no text overlaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
