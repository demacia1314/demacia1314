#!/usr/bin/env python3
"""
Generate the demacia1314 GitHub profile dashboard SVG.

GitHub READMEs render single-column, so the only way to reproduce the
two-column dashboard from the reference design is to draw the whole thing as
one wide SVG. Every panel, border, corner accent, icon and pixel-art sprite is
generated below.

Run `python scripts/build_profile_svg.py` to regenerate assets/profile-dashboard.svg.
"""

import os

W, H = 1400, 1080

# ----------------------------------------------------------------------------
# palette
# ----------------------------------------------------------------------------
BG        = "#05070d"
PANEL     = "#0a0f1a"
PANEL_2   = "#0d1424"
CARD      = "#0b1424"
LINE      = "#1b2942"
LINE_LIT  = "#25405f"
CYAN      = "#00e5ff"
CYAN_DIM  = "#0b7f92"
CYAN_DEEP = "#12395c"
GREEN     = "#38ef7d"
WHITE     = "#e8f1ff"
MUTED     = "#6b7f9e"
SLATE     = "#94a3b8"
GOLD      = "#f5c542"
SILVER    = "#cbd5e1"
BRONZE    = "#cd8a52"
PINK      = "#ff6bb5"
VIOLET    = "#f59e0b"

MONO = ("ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
        "'Courier New', monospace")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class SVG:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    # -- primitives ---------------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1, rx=0,
             dash=None, opacity=None):
        a = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1, dash=None):
        a = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.add(a + "/>")

    def text(self, x, y, s, size=12, fill=WHITE, weight=500, anchor="start",
             spacing=None, opacity=None):
        a = f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{size}" fill="{fill}" font-weight="{weight}"'
        if anchor != "start":
            a += f' text-anchor="{anchor}"'
        if spacing:
            a += f' letter-spacing="{spacing}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + f">{esc(s)}</text>")

    def circle(self, cx, cy, r, fill, stroke=None, sw=1, opacity=None):
        a = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def path(self, d, fill="none", stroke=None, sw=1, opacity=None):
        a = f'<path d="{d}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(a + "/>")

    def poly(self, pts, fill, stroke=None, sw=1):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        self.add(a + "/>")

    # -- composite ----------------------------------------------------------
    def panel(self, x, y, w, h, title=None, right=None, fill=PANEL):
        self.rect(x, y, w, h, fill=fill, stroke=CYAN, sw=1.4, rx=3)
        self.rect(x + 5, y + 5, w - 10, h - 10, stroke=LINE, sw=1, rx=2,
                  dash="4,4")
        for cx, cy in ((x, y), (x + w - 5, y), (x, y + h - 5),
                       (x + w - 5, y + h - 5)):
            self.rect(cx, cy, 5, 5, fill=CYAN)
        if title is not None:
            self.rect(x + 6, y + 6, w - 12, 26, fill=PANEL_2, opacity="0.9")
            self.line(x + 6, y + 32, x + w - 6, y + 32, stroke=LINE)
            self.rect(x + 14, y + 14, 6, 10, fill=CYAN)
            self.text(x + 28, y + 24, title, size=12, fill=CYAN, weight=700,
                      spacing="1")
        if right:
            self.text(x + w - 18, y + 24, right, size=10.5, fill=GREEN,
                      weight=700, anchor="end", spacing="0.6")


def sprite(s, ox, oy, rows, colors, scale):
    """Draw a pixel-art sprite; horizontal runs are merged into one rect."""
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
# sprites
# ----------------------------------------------------------------------------
HOOD = {
    "c": CYAN, "C": "#0891b2",
    "f": "#f2c9a0", "s": "#2b2233",
    "k": "#12101a", "w": "#8ef7ff",
    "n": "#d98b52", "y": "#ffd166",
}
HOOD_ROWS = [
    ".......ccc........",
    ".....ccccc........",
    "....ccccccc.......",
    "..ccccccccccc.....",
    ".ccccccCCCcccc....",
    "ccfff....fffcc....",
    "ccffsssssssffc....",
    "ccffsssssssffc....",
    ".cfswwsswwsffc....",
    "..cfsssssssfc.....",
    "..cffssssfffc.....",
    "...cfffffffcc.....",
    "....cfffffcc......",
    "...nnnccc.nn......",
    "..nnyy.ccc.yy.....",
    ".nnyy..ccc..yy....",
    "nnny...ccc...yn...",
    ".nn....ccc........",
    "..nn...ccc........",
    "..nnn..ccc........",
    "...nn..ccc........",
]

CAT_ORANGE = {"o": "#e8823c", "O": "#c9631f", "w": "#fff6e8", "k": "#1a1208",
              "p": "#ff8fa3"}
CAT_ROWS = [
    "..o.....o..",
    ".oOo...oOo.",
    ".oOooooooO.",
    "oOOoooooOOo",
    "oOwkOOkwOOo",
    "oOOopppOOOo",
    "oOOoooooOOo",
    ".oOwwwwwOo.",
    ".oOoooooOo.",
    "..oOOOOOo..",
]

DOG_BW = {"b": "#2b2b34", "w": "#f2f2f5", "k": "#111", "p": "#ff8fa3"}
DOG_ROWS = [
    "bb.......bb",
    "bwb.....bwb",
    "bwwwwwwwwww",
    "bwkwwwwkwww",
    "bwwwwwwwwww",
    ".bwwpppwwwb",
    ".bwwwwwwwwb",
    ".bwbbbbbwwb",
    "..bbbbbbb..",
    "...bb.bb...",
]

GHOST = {"g": "#7dd3fc", "d": "#38bdf8", "k": "#0c1a2b", "p": "#f9a8d4"}
GHOST_ROWS = [
    "....gggg....",
    "..gggggggg..",
    ".gggggggggg.",
    "gggkkggkkggg",
    "gggkkggkkggg",
    "gggggggggggg",
    "gggggggggggg",
    "gggpppppppgg",
    "gggggggggggg",
    "gggggggggggg",
    "g.ggg.ggg.gg",
]


# ----------------------------------------------------------------------------
# small vector icons (emoji render inconsistently, so these are drawn)
# ----------------------------------------------------------------------------
def icon_chip(s, x, y, kind, col=CYAN, size=26):
    """Icon inside a rounded chip."""
    s.rect(x, y, size, size, fill="#0c1526", stroke=LINE, rx=3)
    cx, cy, sz = x + size / 2, y + size / 2, size
    if kind == "brain":
        s.circle(cx, cy, 5.5, "none", stroke=col, sw=1.4)
        s.rect(cx - 1, cy - 8.5, 2, 3, fill=col)
        s.rect(cx - 1, cy + 5.5, 2, 3, fill=col)
        s.rect(cx - 8.5, cy - 1, 3, 2, fill=col)
        s.rect(cx + 5.5, cy - 1, 3, 2, fill=col)
    elif kind == "book":
        s.rect(cx - 7, cy - 6, 14, 12, fill="none", stroke=col, sw=1.4, rx=1)
        s.line(cx, cy - 6, cx, cy + 6, stroke=col, sw=1.2)
        s.line(cx - 4.5, cy - 2.5, cx - 1.5, cy - 2.5, stroke=col, sw=1)
        s.line(cx + 1.5, cy - 2.5, cx + 4.5, cy - 2.5, stroke=col, sw=1)
    elif kind == "bolt":
        s.poly([(cx + 1, cy - 7), (cx - 5, cy + 1), (cx - 0.5, cy + 1),
                (cx - 1.5, cy + 7), (cx + 5, cy - 1.5), (cx + 0.5, cy - 1.5)],
               fill=col)
    elif kind == "wrench":
        s.rect(cx - 6, cy - 5, 12, 10, fill="none", stroke=col, sw=1.3, rx=2)
        s.circle(cx - 3, cy, 2, "none", stroke=col, sw=1.2)
        s.circle(cx + 3, cy, 2, "none", stroke=col, sw=1.2)
    elif kind == "folder":
        s.path(f"M{cx-7} {cy+5.5} V{cy-4} h5 l2 2.5 h7 V{cy+5.5} Z",
               fill="none", stroke=col, sw=1.3)
    elif kind == "people":
        s.circle(cx - 3.5, cy - 2.5, 3, "none", stroke=col, sw=1.2)
        s.path(f"M{cx-9} {cy+6} a5.5 5.5 0 0 1 11 0", fill="none",
               stroke=col, sw=1.2)
        s.circle(cx + 5, cy - 3.5, 2.3, "none", stroke=col, sw=1.1)
        s.path(f"M{cx+1} {cy+6} a4.5 4.5 0 0 1 9 0", fill="none",
               stroke=col, sw=1.1)
    elif kind == "link":
        s.rect(cx - 7, cy - 6.5, 9, 9, fill="none", stroke=col, sw=1.3, rx=2)
        s.rect(cx - 2, cy - 2.5, 9, 9, fill="none", stroke=col, sw=1.3, rx=2)
    elif kind == "rocket":
        s.path(f"M{cx} {cy-7} c3 3 3.5 6.5 3.5 9 h-7 c0-2.5 .5-6 3.5-9 Z",
               fill=col)
        s.poly([(cx - 3.5, cy + 2), (cx - 6, cy + 6), (cx - 3, cy + 5)],
               fill=col)
        s.poly([(cx + 3.5, cy + 2), (cx + 6, cy + 6), (cx + 3, cy + 5)],
               fill=col)
        s.circle(cx, cy - 2.5, 1.6, fill="#0c1526")
    elif kind == "kaggle":
        s.rect(cx - 5.5, cy - 7, 2.6, 14, fill=col)
        s.poly([(cx + 1, cy), (cx + 6.5, cy - 6.5), (cx + 2.5, cy - 6.5),
                (cx - 1.5, cy - 1.5)], fill=col)
        s.poly([(cx - 1.5, cy + 1.5), (cx + 2.5, cy + 6.5), (cx + 6.5, cy + 6.5),
                (cx + 1, cy)], fill=col)
    return size


def dot_icon(s, x, y, col, size=26, glyph=None):
    s.rect(x, y, size, size, fill="#0c1526", stroke=LINE, rx=3)
    s.circle(x + size / 2, y + size / 2, size * 0.24, fill=col, opacity="0.85")


def build():
    s = SVG()
    s.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
          f'viewBox="0 0 {W} {H}">')

    s.add(f'''<defs>
  <linearGradient id="night" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#0a1633"/><stop offset="55%" stop-color="#081026"/>
    <stop offset="100%" stop-color="#050a16"/>
  </linearGradient>
  <linearGradient id="silverG" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="35%" stop-color="#e2e8f0"/>
    <stop offset="70%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#7c8798"/>
  </linearGradient>
  <radialGradient id="moonG" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#fff8d6"/><stop offset="72%" stop-color="#f5e08a"/>
    <stop offset="100%" stop-color="#e8c65a" stop-opacity="0"/>
  </radialGradient>
</defs>''')

    s.rect(0, 0, W, H, fill=BG)

    # ========================================================================
    # SIDEBAR
    # ========================================================================
    sx, sw_ = 24, 300
    s.panel(sx, 24, sw_, H - 48)

    # --- avatar rings ---
    ax, ay = sx + sw_ / 2, 148
    for r, col, op in ((80, CYAN_DEEP, "1"), (72, CYAN, "0.22"), (64, CYAN, "0.12")):
        s.circle(ax, ay, r, "none", stroke=col, sw=1.2, opacity=op)
    for k in range(28):
        import math
        th = k * (2 * math.pi / 28)
        px_, py_ = ax + 72 * math.cos(th), ay + 72 * math.sin(th)
        if k % 4 == 0:
            s.rect(px_ - 1.5, py_ - 1.5, 3, 3, fill=CYAN, opacity="0.55")
    s.circle(ax, ay, 56, fill="#0b1220", stroke=CYAN, sw=1.6)
    sc = 5.4
    sprite(s, ax - 9.5 * sc, ay - 11 * sc, HOOD_ROWS, HOOD, sc)
    sprite(s, ax - 1.5 * sc, ay - 12.6 * sc, CAT_ROWS, CAT_ORANGE, 2.0)

    # --- name ---
    s.text(ax, 276, "demacia1314", size=26, fill=WHITE, weight=800,
           anchor="middle", spacing="1.5")
    s.text(ax, 305, "@demacia1314", size=12, fill=MUTED, weight=600,
           anchor="middle")

    # --- quote box ---
    s.rect(sx + 24, 328, sw_ - 48, 56, fill="#08101f", stroke=LINE, rx=3)
    s.text(sx + 34, 344, "“", size=20, fill=CYAN_DIM, weight=800)
    s.text(ax, 356, "Small Steps", size=13, fill=CYAN, weight=700,
           anchor="middle")
    s.text(ax, 374, "to Brighter AI.", size=12, fill=SLATE, weight=500,
           anchor="middle")
    s.text(sx + sw_ - 34, 372, "”", size=20, fill=CYAN_DIM, weight=800,
           anchor="end")

    # --- roles ---
    roles = [("brain", "AI Enthusiast", CYAN),
             ("book", "Lifelong Learner", GREEN),
             ("bolt", "Kaggle Competitor", GOLD),
             ("wrench", "Building Cool Stuff", VIOLET)]
    ry = 420
    for kind, label, col in roles:
        icon_chip(s, sx + 24, ry - 15, kind, col)
        s.text(sx + 60, ry + 4, label, size=12, fill=SLATE, weight=600)
        ry += 40

    s.line(sx + 24, ry - 8, sx + sw_ - 24, ry - 8, stroke=LINE)
    ry += 24

    # --- stats ---
    stats = [("folder", "Public repositories", "6", GOLD),
             ("people", "Followers", "0", PINK),
             ("link", "Following", "1", CYAN)]
    for kind, label, val, col in stats:
        icon_chip(s, sx + 24, ry - 15, kind, col)
        s.text(sx + 60, ry + 4, label, size=12, fill=SLATE, weight=600)
        s.text(sx + sw_ - 24, ry + 4, val, size=13, fill=WHITE, weight=800,
               anchor="end")
        ry += 38

    ry += 12

    # --- kaggle button ---
    s.rect(sx + 24, ry, sw_ - 48, 42, fill="#0a2033", stroke=CYAN, sw=1.4, rx=3)
    icon_chip(s, sx + 36, ry + 9, "rocket", CYAN, 24)
    s.text(sx + 70, ry + 26, "OPEN KAGGLE PROFILE", size=11, fill=CYAN,
           weight=800, spacing="0.6")
    ry += 130

    # --- ghost mascot ---
    sprite(s, ax - 5.5 * 6, ry, GHOST_ROWS, GHOST, 6)
    ry += len(GHOST_ROWS) * 6 + 26

    s.text(ax, ry + 4, "Good Code", size=11, fill=MUTED, weight=600,
           anchor="middle")
    s.text(ax, ry + 20, "Brighter Tomorrow", size=11, fill=MUTED, weight=600,
           anchor="middle")

    # ========================================================================
    # MAIN COLUMN
    # ========================================================================
    mx = sx + sw_ + 20
    mw = W - mx - 24

    # ---- header banner ----------------------------------------------------
    by, bh = 24, 250
    s.panel(mx, by, mw, bh)
    ix, iy, iw, ih = mx + 6, by + 6, mw - 12, bh - 12
    s.add(f'<clipPath id="hdr"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="2"/></clipPath>')
    s.add('<g clip-path="url(#hdr)">')
    s.rect(ix, iy, iw, ih, fill="url(#night)")
    import math
    for k in range(64):
        x = (k * 137) % iw
        y = (k * 53) % 170 + 12
        if x > iw - 250 and y < 110:
            continue
        col = CYAN if k % 3 == 0 else (WHITE if k % 3 == 1 else GOLD)
        s.rect(ix + x, iy + y, 2, 2, fill=col, opacity="0.8")
    s.circle(ix + iw - 196, iy + 66, 46, fill="url(#moonG)")
    s.circle(ix + iw - 196, iy + 66, 24, fill="#f7e9a8")
    s.circle(ix + iw - 208, iy + 58, 5, fill="#e6d18e")
    s.circle(ix + iw - 186, iy + 78, 3.5, fill="#e6d18e")
    s.path(f"M{ix} {iy+ih} L{ix} {iy+ih-72} L{ix+96} {iy+ih-122} "
           f"L{ix+178} {iy+ih-66} L{ix+290} {iy+ih-146} L{ix+412} {iy+ih-60} "
           f"L{ix+534} {iy+ih-124} L{ix+672} {iy+ih-52} "
           f"L{ix+iw} {iy+ih-100} L{ix+iw} {iy+ih} Z", fill="#0c1830")
    s.path(f"M{ix} {iy+ih} L{ix} {iy+ih-40} L{ix+146} {iy+ih-88} "
           f"L{ix+306} {iy+ih-32} L{ix+478} {iy+ih-80} L{ix+648} {iy+ih-28} "
           f"L{ix+iw} {iy+ih-66} L{ix+iw} {iy+ih} Z", fill="#0a1226")
    for k in range(9):
        wdt = 92 - k * 9
        s.rect(ix + iw - 196 - wdt / 2, iy + 120 + k * 9, wdt, 2,
               fill="#f7e9a8", opacity=f"{0.48 - k*0.048:.2f}")
    sprite(s, ix + iw - 400, iy + ih - 104, CAT_ROWS, CAT_ORANGE, 3)
    sprite(s, ix + iw - 322, iy + ih - 100, DOG_ROWS, DOG_BW, 3)
    s.add('</g>')

    # signpost
    spx = ix + iw - 100
    s.rect(spx + 30, iy + 42, 5, 100, fill="#6b4a2a")
    for k, (label, col) in enumerate((("BETTER AI", CYAN), ("BRIGHTER", GOLD),
                                      ("TOMORROWS", SLATE),
                                      ("TOGETHER <3", GREEN))):
        yy = iy + 42 + k * 23
        s.rect(spx, yy, 64, 18, fill="#0e1b30", stroke=col, sw=0.8)
        s.text(spx + 32, yy + 13, label, size=6.4, fill=col, weight=800,
               anchor="middle", spacing="0.3")

    for k, line in enumerate(("Game", "Curiosity", "Brighter", "Tomorrow")):
        s.text(ix + iw - 196 + (0 if k % 2 == 0 else -10), iy + 152 + k * 21,
               line, size=15, fill="#8fb4d9", weight=500, opacity="0.9")

    s.text(ix + 34, iy + 56, "> hello, i'm", size=13, fill=CYAN, weight=700,
           spacing="0.6")
    s.text(ix + 34, iy + 112, "demacia1314", size=44, fill=WHITE, weight=900,
           spacing="2")
    s.rect(ix + 404, iy + 80, 13, 34, fill=CYAN, opacity="0.85")
    s.text(ix + 34, iy + 146, "AI / CV / Agents / Competitions", size=15,
           fill=GREEN, weight=700, spacing="1.4")
    s.line(ix + 34, iy + 162, ix + 440, iy + 162, stroke=CYAN_DIM)
    s.text(ix + 34, iy + 188, "Building intelligent systems for a better tomorrow.",
           size=13, fill=SLATE, weight=500)
    s.text(ix + 34, iy + 214, "Kaggle  x  Open Source  x  Real-World Impact",
           size=12, fill=SLATE, weight=600)

    s.rect(ix + iw - 180, iy + ih - 46, 154, 34, fill="#08111f", stroke=LINE,
           rx=2)
    s.text(ix + iw - 166, iy + ih - 31, "< Keep Learning", size=8.5,
           fill=CYAN, weight=700)
    s.text(ix + iw - 166, iy + ih - 19, "Keep Building >", size=8.5,
           fill=GREEN, weight=700)

    # ---- About Me ---------------------------------------------------------
    ay2, ah = 292, 168
    s.panel(mx, ay2, mw, ah, title="ABOUT ME")
    sprite(s, mx + 36, ay2 + 62, CAT_ROWS, CAT_ORANGE, 5.4)

    tx = mx + 132
    s.text(tx, ay2 + 58,
           "Building AI agents, computer vision projects, and competition solutions.",
           size=12.5, fill=CYAN, weight=600)
    for k, line in enumerate((
            "I'm passionate about turning ideas into real-world impact through AI.",
            "Currently exploring multimodal agents, computer vision, and",
            "participating in Kaggle competitions to learn, compete, and grow.")):
        s.text(tx, ay2 + 80 + k * 20, line, size=12.5, fill=SLATE, weight=500)

    chips = [("Curious", CYAN), ("Open to collaboration", GREEN),
             ("Always learning", SLATE)]
    cx = tx
    for label, col in chips:
        cw = 7.6 * len(label) + 24
        s.rect(cx, ay2 + 138, cw, 22, fill="#0b1728", stroke=col, sw=0.9, rx=3)
        s.text(cx + cw / 2, ay2 + 152, label, size=10, fill=col, weight=700,
               anchor="middle")
        cx += cw + 10

    qx, qw = mx + mw - 244, 226
    s.rect(qx, ay2 + 46, qw, 78, fill="#08101f", stroke=LINE, rx=3)
    s.text(qx + 16, ay2 + 70, "“", size=20, fill=CYAN_DIM, weight=800)
    s.text(qx + qw / 2 + 6, ay2 + 86, "Better AI.", size=13, fill=CYAN,
           weight=700, anchor="middle")
    s.text(qx + qw / 2 + 6, ay2 + 106, "Brighter Tomorrows.", size=12,
           fill=SLATE, weight=600, anchor="middle")
    s.text(qx + qw - 16, ay2 + 118, "”", size=20, fill=CYAN_DIM,
           weight=800, anchor="end")

    # ---- Featured Projects ------------------------------------------------
    py, ph = 476, 158
    s.panel(mx, py, mw, ph, title="FEATURED PROJECTS",
            right="View all repositories →")
    projs = [("kaggle", "dsh-airdrop", "Drag & drop uploads", "TypeScript", "9"),
             ("book", "WordAgent", "AI sidebar for Word", "TypeScript", "0"),
             ("link", "dsh-remote-deliver", "Remote file delivery", "JavaScript", "0")]
    pw = (mw - 36 - 2 * 14) / 3
    for i, (kind, name, desc, lang, stars) in enumerate(projs):
        px_ = mx + 18 + i * (pw + 14)
        s.rect(px_, py + 42, pw, 100, fill=CARD, stroke=LINE, rx=3)
        icon_chip(s, px_ + 14, py + 56, kind, CYAN, 28)
        s.text(px_ + 50, py + 69, name, size=11.5, fill=WHITE, weight=800)
        s.text(px_ + 50, py + 83, desc, size=9, fill=MUTED, weight=500)
        s.rect(px_ + 14, py + 108, 7.4 * len(lang) + 18, 20, fill="#0a1a2c",
               stroke=CYAN_DIM, sw=0.8, rx=3)
        s.text(px_ + 14 + (7.4 * len(lang) + 18) / 2, py + 122, lang, size=9,
               fill=CYAN, weight=700, anchor="middle")
        s.text(px_ + pw - 14, py + 122, f"★ {stars}", size=10, fill=GOLD,
               weight=700, anchor="end")

    # ---- Kaggle Awards ----------------------------------------------------
    ky, kh = 652, 178
    s.panel(mx, ky, mw, kh, title="KAGGLE AWARDS // DEMACIA1314",
            right="● VERIFIED VIA KAGGLE API")

    lw = 212
    s.rect(mx + 18, ky + 42, lw, 120, fill="#0a101d", stroke=LINE, rx=3)
    mxm = mx + 66
    s.poly([(mxm, ky + 56), (mxm + 24, ky + 56), (mxm + 37, ky + 69),
            (mxm + 37, ky + 89), (mxm + 24, ky + 102), (mxm, ky + 102),
            (mxm - 13, ky + 89), (mxm - 13, ky + 69)],
           fill="url(#silverG)", stroke="#f8fafc", sw=1.2)
    s.circle(mxm + 12, ky + 79, 11, fill="#0b1220", stroke=SLATE)
    s.text(mxm + 12, ky + 83, "Ag", size=10, fill=SILVER, weight=900,
           anchor="middle")
    bxm = mx + 146
    s.poly([(bxm, ky + 62), (bxm + 21, ky + 62), (bxm + 32, ky + 73),
            (bxm + 32, ky + 91), (bxm + 21, ky + 102), (bxm, ky + 102),
            (bxm - 11, ky + 91), (bxm - 11, ky + 73)],
           fill=BRONZE, stroke="#f3d0a8", sw=1.1)
    s.circle(bxm + 10.5, ky + 82, 9, fill="#1a0f06", stroke=BRONZE)
    s.text(bxm + 10.5, ky + 85.5, "Bz", size=8.5, fill="#f3d0a8", weight=900,
           anchor="middle")
    s.text(mx + 18 + lw / 2, ky + 120, "COMPETITIONS TIER", size=9.5,
           fill=SLATE, weight=700, anchor="middle", spacing="1")
    s.line(mx + 36, ky + 128, mx + 18 + lw - 18, ky + 128, stroke=LINE)
    s.text(mx + 18 + lw / 2, ky + 150, "EXPERT", size=21, fill=GREEN,
           weight=900, anchor="middle", spacing="2")

    six = mx + 18 + lw + 14
    siw = mw - 18 * 2 - lw - 14 - 152
    s.rect(six, ky + 42, siw, 72, fill="#0c192c", stroke=CYAN_DEEP, sw=1.2, rx=3)
    s.rect(six + 14, ky + 57, 36, 36, fill="#132441", stroke=SILVER, rx=3)
    s.text(six + 32, ky + 81, "\U0001f948", size=17, anchor="middle")
    s.text(six + 62, ky + 71, "AI Agent Security - Multi-Step Tool Attacks",
           size=12.5, fill=WHITE, weight=800)
    s.text(six + 62, ky + 89, "Featured · Code Competition · 4,186 Teams Worldwide",
           size=10.5, fill=SLATE)
    s.text(six + 62, ky + 106, "OFFICIAL AWARD: SILVER MEDAL (TOP 1.07%)",
           size=10, fill=CYAN, weight=700)

    rx_ = six + siw + 12
    s.rect(rx_, ky + 42, 140, 72, fill="#0a1120", stroke=LINE, rx=3)
    s.text(rx_ + 70, ky + 70, "RANK #45", size=14, fill=WHITE, weight=900,
           anchor="middle")
    s.line(rx_ + 22, ky + 80, rx_ + 118, ky + 80, stroke=LINE)
    s.text(rx_ + 70, ky + 97, "LEADERBOARD", size=9.5, fill=CYAN, weight=800,
           anchor="middle", spacing="1")

    s.rect(six, ky + 124, siw + 152, 42, fill="#170f07", stroke=BRONZE, sw=1,
           rx=3)
    s.rect(six + 12, ky + 132, 26, 26, fill="#241407", stroke=BRONZE, rx=3)
    s.text(six + 25, ky + 151, "\U0001f949", size=13, anchor="middle")
    s.text(six + 48, ky + 145, "BRONZE MEDAL · second competition medal",
           size=10.5, fill="#f3d0a8", weight=700)
    s.text(six + 48, ky + 160,
           "Kaggle API confirms the medal; competition not yet attributed",
           size=9.5, fill=MUTED)
    s.text(six + siw + 140, ky + 152, "OPEN →", size=10.5, fill=CYAN,
           weight=800, anchor="end")

    # ---- bottom strip -----------------------------------------------------
    sy = 858
    sh = 170
    cw3 = (mw - 2 * 14) / 3

    s.panel(mx, sy, cw3, sh, title="SKILLS & TECH STACK")
    skills = [("Python", "#3776ab"), ("TypeScript", "#3178c6"),
              ("PyTorch", "#ee4c2c"), ("OpenCV", "#5c3ee8")]
    kx = mx + 36
    step = (cw3 - 62) / 3
    for label, col in skills:
        s.circle(kx, sy + 80, 16, fill=col, opacity="0.92")
        s.circle(kx, sy + 80, 16, "none", stroke=col, sw=1, opacity="0.5")
        s.text(kx, sy + 112, label, size=9, fill=SLATE, weight=600,
               anchor="middle")
        kx += step
    s.text(mx + cw3 / 2, sy + 136, "· · ·  and more", size=10,
           fill=MUTED, weight=600, anchor="middle")

    gx = mx + cw3 + 14
    s.panel(gx, sy, cw3, sh, title="GITHUB ACTIVITY")
    s.rect(gx + 18, sy + 46, cw3 - 36, 62, fill="#08101f", stroke=LINE, rx=3)
    cols, rows_ = 30, 5
    gw = (cw3 - 36 - 32) / cols
    for c in range(cols):
        for r_ in range(rows_):
            on = (c * 7 + r_ * 5) % 13 < 2
            s.rect(gx + 30 + c * gw, sy + 54 + r_ * 10, gw - 1.5, 8,
                   fill=GREEN if on else CYAN_DEEP, opacity="0.9" if on else "0.45")
    s.text(gx + cw3 / 2, sy + 128, "48 contributions in the last year",
           size=9.5, fill=MUTED, weight=600, anchor="middle")

    nx = mx + 2 * (cw3 + 14)
    s.panel(nx, sy, cw3, sh, title="CONNECT")
    items = [("kaggle", "GitHub", "@demacia1314", CYAN),
             ("kaggle", "Kaggle", "demacia1314", GREEN)]
    iy_ = sy + 62
    for kind, label, handle, col in items:
        icon_chip(s, nx + 22, iy_ - 15, kind, col, 28)
        s.text(nx + 58, iy_ - 3, label, size=10.5, fill=WHITE, weight=800)
        s.text(nx + 58, iy_ + 12, handle, size=9.5, fill=col, weight=600)
        iy_ += 44

    # ---- footer -----------------------------------------------------------
    s.line(mx + 18, H - 52, mx + mw - 18, H - 52, stroke=LINE)
    s.text(mx + mw / 2 - 130, H - 30,
           "⭐ Thanks for visiting! If you like my work, consider following.",
           size=10.5, fill=SLATE, weight=600, anchor="middle")
    s.text(mx + mw - 18, H - 30, "Good Code  Brighter Tomorrows", size=10,
           fill=MUTED, weight=600, anchor="end")

    s.add("</svg>")
    return "\n".join(s.parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here), "assets", "profile-dashboard.svg")
    svg = build()
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print(f"wrote {out}  ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
