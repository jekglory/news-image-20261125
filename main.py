#!/usr/bin/env python3
"""The World in One Day - Wednesday 25 November 2026.

A pure-stdlib Python program that draws one 1024x1024 newspaper
front page summing up the day's real world news and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories researched from Wednesday 25 November 2026 reporting
(Reuters world summary, RFE/RL, Jagran Josh, Starlit Daily):
  lead   Ukraine - Zelenskyy confirms Kyiv's drone strike on a
         Russian cargo ship in the Gulf of Finland; days earlier
         Ukraine sank a Russian warship off Benghazi, Libya.
  1      Markets - Nvidia shares jump 31.5% in a day, regaining
         about $1 trillion in value as Jensen Huang returns
         as CEO after a spy scandal.
  2      Middle East - Houthis hit Riyadh's tallest tower,
         11 wounded; rebels push to 60 km from Aden; Britain
         sanctions Houthi leaders.
  3      France - Ex-president Sarkozy and Carla Bruni ordered
         to stand trial over alleged Libyan funding; pre-trial
         hearing set for 1 April 2027.
  4      Sport - Real Madrid beat PSV 5-1: a Bellingham stunner
         and a Mbappe brace.
  5      Sport - England beat Australia by 8 wickets in the
         second T20, chasing 185 to level the series.
  6      USA - Trump pardons Thanksgiving turkeys Freedom and
         Feathers and awards Rudy Giuliani the Medal of Freedom.
  7      Iran - Winter gas shortages and electricity rationing
         loom as war damage deepens the energy crisis.
  strip  GTA VI out worldwide; NATO sends early-warning jets to
         Poland; Indonesia's vice-president resigns; FBI crime
         database hit by a suspected breach; Nepal PM visits India.

No Pillow, no numpy, no network, no clock, no randomness.
Two runs write byte-identical output.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (22, 22, 28)
NAVY = (20, 33, 61)
NAVY2 = (28, 48, 88)
GOLD = (201, 162, 39)
GOLD_L = (232, 196, 90)
RED = (178, 34, 34)
RED_L = (214, 69, 65)
TEAL = (38, 120, 110)
TEAL_D = (24, 84, 78)
SKY = (70, 110, 150)
SKY_D = (44, 74, 110)
GREEN = (46, 125, 50)
GREY = (120, 124, 132)
GREY_L = (205, 203, 196)
WHITE = (255, 255, 255)
CREAM = (253, 250, 242)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def rect_outline(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        fill_rect(x - t // 2, y - t // 2, t, t, c)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)


def circle_outline(cx, cy, r, c, t=2):
    # True ring: only pixels whose distance lies within [r-t, r].
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d2 <= r * r:
                set_px(xx, yy, c)


def fill_poly(points, c):
    # Scanline fill for a simple polygon given as [(x, y), ...].
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                set_px(x, y, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits ('1' = on). Uppercase only; all copy
# is uppercased before drawing.
FONT = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01110', '10001', '10000', '10000', '10000', '10001', '01110'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01110', '10001', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('01110', '00100', '00100', '00100', '00100', '00100', '01110'),
    'J': ('00111', '00010', '00010', '00010', '00010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    '0': ('01110', '10001', '10011', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00110', '01000', '10000', '11111'),
    '3': ('11111', '00010', '00100', '00010', '00001', '10001', '01110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('00110', '01000', '10000', '11110', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00010', '01100'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
    '.': ('00000', '00000', '00000', '00000', '00000', '01100', '01100'),
    ',': ('00000', '00000', '00000', '00000', '01100', '00100', '01000'),
    '-': ('00000', '00000', '00000', '01110', '00000', '00000', '00000'),
    "'": ('00100', '00100', '01000', '00000', '00000', '00000', '00000'),
    '!': ('00100', '00100', '00100', '00100', '00100', '00000', '00100'),
    '?': ('01110', '10001', '00001', '00110', '00100', '00000', '00100'),
    ':': ('00000', '01100', '00000', '00000', '01100', '00000', '00000'),
    ';': ('00000', '01100', '00000', '01100', '01100', '00100', '01000'),
    '%': ('11001', '11010', '00010', '00100', '01000', '01011', '10011'),
    '+': ('00000', '00100', '00100', '11111', '00100', '00100', '00000'),
    '=': ('00000', '00000', '11111', '00000', '11111', '00000', '00000'),
    '/': ('00001', '00010', '00010', '00100', '01000', '01000', '10000'),
    '(': ('00010', '00100', '01000', '01000', '01000', '00100', '00010'),
    ')': ('01000', '00100', '00010', '00010', '00010', '00100', '01000'),
    '"': ('01010', '01010', '01010', '00000', '00000', '00000', '00000'),
    '&': ('01100', '10010', '10100', '01000', '10101', '10010', '01101'),
    '$': ('00100', '01111', '10100', '01110', '00101', '11110', '00100'),
    '\u2022': ('00000', '00000', '01100', '01100', '01100', '00000', '00000'),
}

_NORMALISE = {
    '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2014': '-', '\u00e9': 'E', '\u00e8': 'E',
    '\u00fc': 'U', '\u00f6': 'O',
}


def clean(text):
    out = []
    for ch in text.upper():
        out.append(_NORMALISE.get(ch, ch))
    return ''.join(out)


def text_w(text, scale):
    return len(clean(text)) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    text = clean(text)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centred(cx, y, text, scale, color):
    return draw_text(cx - text_w(text, scale) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = clean(text).split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- PNG out
def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    out += struct.pack('>I', binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * stride:(y + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
            + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + _chunk(b'IEND', b''))


def write_output():
    """Write /output/entry.png. The grader owns /output: clear only
    its contents, create it if missing, never delete the directory."""
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path):
            os.remove(path)
    target = os.path.join(out_dir, 'entry.png')
    with open(target, 'wb') as f:
        f.write(encode_png())
    return target


# ---------------------------------------------------------------- panels
def panel(x, y, w, h, accent, kicker, headlines, body, icon=None):
    """A news panel: white card, accent top bar, kicker, headline
    lines (scale 3), wrapped body (scale 2), optional icon fn."""
    fill_rect(x, y, w, h, WHITE)
    rect_outline(x, y, w, h, GREY_L, 1)
    fill_rect(x, y, w, 8, accent)
    draw_text(x + 14, y + 18, kicker, 2, accent)
    hy = y + 44
    for line in headlines:
        draw_text(x + 14, hy, line, 3, INK)
        hy += 26
    by = hy + 6
    if icon is not None:
        icon_w = 92
        body_w = w - 28 - icon_w - 12
        icon(x + w - 14 - icon_w, by, icon_w)
    else:
        body_w = w - 28
    for ln in wrap(body, 2, body_w):
        draw_text(x + 14, by, ln, 2, INK)
        by += 18


# ---------------------------------------------------------------- icons
def icon_ship(x, y, w):
    # Cargo ship on waves, inside a sky box.
    fill_rect(x, y, w, 92, (214, 232, 240))
    fill_rect(x, y + 78, w, 14, SKY)
    line(x, y + 82, x + w, y + 82, WHITE, 2)
    line(x, y + 87, x + w, y + 87, WHITE, 2)
    # hull
    fill_poly([(x + 8, y + 58), (x + w - 8, y + 58),
               (x + w - 20, y + 76), (x + 20, y + 76)], NAVY2)
    fill_rect(x + 14, y + 50, w - 28, 8, RED)
    # containers + bridge
    fill_rect(x + 16, y + 34, 18, 16, GOLD)
    fill_rect(x + 38, y + 34, 18, 16, TEAL)
    fill_rect(x + 60, y + 30, 16, 20, WHITE)
    fill_rect(x + 62, y + 32, 12, 4, NAVY2)
    # mast + smoke
    vline(x + w - 22, y + 12, 40, INK, 3)
    fill_circle(x + w - 30, y + 10, 4, GREY)
    fill_circle(x + w - 38, y + 6, 3, GREY)


def icon_chip(x, y, w):
    # Microchip: dark square, pins, inner die.
    fill_rect(x + 10, y, w - 20, 92, NAVY)
    fill_rect(x + 26, y + 22, w - 52, 48, NAVY2)
    rect_outline(x + 26, y + 22, w - 52, 48, GOLD_L, 2)
    for i in range(5):
        fill_rect(x + 10 + i * 14, y - 6, 6, 6, GOLD)
        fill_rect(x + 10 + i * 14, y + 92, 6, 6, GOLD)
    for i in range(4):
        fill_rect(x + 4, y + 12 + i * 18, 6, 6, GOLD)
        fill_rect(x + w - 10, y + 12 + i * 18, 6, 6, GOLD)


def icon_tower(x, y, w):
    # Skyscraper with a strike burst at its crown.
    fill_rect(x, y, w, 92, (232, 226, 214))
    fill_rect(x + 30, y + 26, 32, 66, SKY_D)
    fill_rect(x + 42, y + 8, 8, 18, SKY_D)
    for r in range(4):
        for c in range(2):
            fill_rect(x + 35 + c * 12, y + 34 + r * 14, 6, 8, GOLD_L)
    # burst
    for dx, dy in ((0, -12), (10, -8), (12, 0), (10, 8), (0, 12),
                   (-10, 8), (-12, 0), (-10, -8)):
        line(x + 46, y + 8, x + 46 + dx, y + 8 + dy, RED_L, 3)
    fill_circle(x + 46, y + 8, 5, RED)


def icon_court(x, y, w):
    # Courthouse: pediment, three columns, steps.
    fill_poly([(x + 6, y + 26), (x + w - 6, y + 26), (x + w // 2, y + 6)],
              NAVY2)
    fill_rect(x + 6, y + 26, w - 12, 6, NAVY2)
    for i in range(3):
        fill_rect(x + 14 + i * 26, y + 32, 10, 42, NAVY2)
    fill_rect(x + 6, y + 74, w - 12, 5, NAVY2)
    fill_rect(x, y + 79, w, 5, GREY)
    fill_rect(x + 4, y + 84, w - 8, 5, GREY_L)


def icon_ball(x, y, w):
    # Football on grass.
    fill_rect(x, y, w, 92, (214, 235, 205))
    fill_rect(x, y + 74, w, 18, GREEN)
    fill_circle(x + 46, y + 40, 26, WHITE)
    circle_outline(x + 46, y + 40, 26, INK, 2)
    fill_poly([(x + 40, y + 32), (x + 52, y + 32), (x + 56, y + 42),
               (x + 46, y + 50), (x + 36, y + 42)], INK)
    for dx, dy in ((-20, -14), (20, -14), (-22, 12), (22, 12)):
        line(x + 46, y + 40, x + 46 + dx, y + 40 + dy, INK, 2)


def icon_stumps(x, y, w):
    # Cricket stumps and ball on a pitch strip.
    fill_rect(x, y, w, 92, (232, 226, 205))
    fill_rect(x + 8, y + 78, w - 16, 14, (196, 164, 110))
    for i in range(3):
        fill_rect(x + 30 + i * 10, y + 34, 5, 44, GOLD)
    fill_rect(x + 30, y + 30, 25, 4, GOLD)
    fill_circle(x + 70, y + 58, 10, RED)
    fill_circle(x + 70, y + 58, 10, RED_L)
    line(x + 62, y + 52, x + 78, y + 64, RED, 2)
    line(x + 78, y + 52, x + 62, y + 64, RED, 2)


def icon_medal(x, y, w):
    # Medal with ribbon, for the Medal of Freedom.
    fill_rect(x, y, w, 92, (232, 226, 214))
    fill_poly([(x + 34, y + 4), (x + 46, y + 4), (x + 52, y + 40),
               (x + 40, y + 40)], RED)
    fill_poly([(x + 46, y + 4), (x + 58, y + 4), (x + 52, y + 40),
               (x + 40, y + 40)], (120, 20, 30))
    fill_circle(x + 46, y + 62, 22, GOLD)
    circle_outline(x + 46, y + 62, 22, (150, 110, 20), 2)
    fill_circle(x + 46, y + 62, 12, GOLD_L)


def icon_bolt(x, y, w):
    # Lightning bolt over a dark grid: power rationing.
    fill_rect(x, y, w, 92, NAVY)
    for i in range(1, 5):
        vline(x + i * 18, y + 6, 80, NAVY2, 1)
        hline(x + 6, y + i * 18, w - 12, NAVY2, 1)
    fill_poly([(x + 52, y + 6), (x + 30, y + 50), (x + 44, y + 50),
               (x + 36, y + 86), (x + 62, y + 40), (x + 48, y + 40)],
              GOLD_L)

# ---------------------------------------------------------------- page
def build_page():
    fill_rect(0, 0, W, H, PAPER)

    # --- masthead
    fill_rect(0, 0, W, 104, NAVY)
    draw_text_centred(W // 2, 16, 'THE WORLD IN ONE DAY', 5, WHITE)
    draw_text_centred(W // 2, 62, 'WEDNESDAY 25 NOVEMBER 2026', 2, GOLD_L)
    draw_text(24, 84, 'ONE DAY - ONE PAGE - ALL THE NEWS', 1, (160, 175, 200))
    draw_text(1024 - 24 - text_w('PRICE: ONE DAY OF HISTORY', 1), 84,
              'PRICE: ONE DAY OF HISTORY', 1, (160, 175, 200))
    hline(0, 104, W, GOLD, 4)

    # --- headline ticker
    fill_rect(0, 108, W, 28, GOLD)
    draw_text_centred(
        W // 2, 114,
        'UKRAINE CONFIRMS SEA STRIKES  \u2022  HOUTHIS HIT RIYADH  \u2022  NVIDIA +31.5%',
        2, NAVY)

    # --- lead story: Ukraine strikes at sea
    lx, ly, lw, lh = 16, 148, 620, 296
    fill_rect(lx, ly, lw, lh, WHITE)
    rect_outline(lx, ly, lw, lh, GREY_L, 1)
    fill_rect(lx, ly, lw, 8, RED)
    draw_text(lx + 14, ly + 18, 'LEAD STORY - WAR AT SEA', 2, RED)
    draw_text(lx + 14, ly + 44, 'UKRAINE STRIKES', 4, INK)
    draw_text(lx + 14, ly + 76, 'AT SEA', 4, INK)
    for i, ln in enumerate(wrap(
            "Zelenskyy confirms Kyiv's drone hit on a Russian cargo "
            "ship in the Gulf of Finland. Ukraine also sank "
            "a Russian warship off Benghazi, Libya.", 2, 350)):
        draw_text(lx + 14, ly + 122 + i * 18, ln, 2, INK)
    draw_text(lx + 14, ly + 236, 'KYIV - GULF OF FINLAND - BENGHAZI', 2, GREY)
    draw_text(lx + 14, ly + 258,
              'NORWAY URGES CAUTION AS STRIKES WIDEN', 2, GREY)
    icon_ship(lx + 398, ly + 122, 200)

    # --- markets: Nvidia
    rx, ry, rw, rh = 652, 148, 356, 296
    fill_rect(rx, ry, rw, rh, WHITE)
    rect_outline(rx, ry, rw, rh, GREY_L, 1)
    fill_rect(rx, ry, rw, 8, GREEN)
    draw_text(rx + 14, ry + 18, 'MARKETS', 2, GREEN)
    draw_text(rx + 14, ry + 44, 'NVIDIA SOARS', 4, INK)
    draw_text(rx + 14, ry + 84, '+31.5%', 7, GREEN)
    for i, ln in enumerate(wrap(
            'Shares jump in a day, regaining about $1 trillion '
            'as Huang returns as CEO.', 2, rw - 28)):
        draw_text(rx + 14, ry + 140 + i * 18, ln, 2, INK)
    icon_chip(rx + 14, ry + 196, 92)
    draw_text(rx + 122, ry + 210, 'CHIP GIANT', 2, GREY)
    draw_text(rx + 122, ry + 232, 'BACK ON TOP', 2, GREY)
    draw_text(rx + 122, ry + 254, 'AFTER SPY ROW', 2, GREY)

    # --- row two: three panels
    y2, h2, w2 = 460, 250, 322
    panel(16, y2, w2, h2, RED_L, 'MIDDLE EAST',
          ['HOUTHIS HIT', 'RIYADH TOWER'],
          'A strike on Riyadh\u2019s tallest tower wounds 11. '
          'Rebels near Aden; Britain sanctions Houthi leaders.',
          icon_tower)
    panel(354, y2, w2, h2, NAVY2, 'FRANCE',
          ['SARKOZY TO', 'STAND TRIAL'],
          'Sarkozy and Carla Bruni ordered to trial over '
          'alleged Libyan funding. Hearing: 1 April 2027.',
          icon_court)
    panel(692, y2, w2, h2, SKY_D, 'CHAMPIONS LEAGUE',
          ['REAL MADRID', '5-1 PSV'],
          'A Bellingham stunner and a Mbappe brace sink PSV '
          'as Madrid run riot at home.',
          icon_ball)

    # --- row three: three panels
    y3, h3 = 726, 210
    panel(16, y3, w2, h3, TEAL_D, 'CRICKET',
          ['ENGLAND LEVEL', 'T20 SERIES'],
          'England beat Australia by eight wickets in the '
          'second T20, chasing 185.',
          icon_stumps)
    panel(354, y3, w2, h3, GOLD, 'USA',
          ['TURKEYS SAVED,', 'GIULIANI HONOUR'],
          'Trump pardons turkeys Freedom and Feathers; '
          'Giuliani gets the Medal of Freedom.',
          icon_medal)
    panel(692, y3, w2, h3, NAVY2, 'IRAN',
          ['IRAN BRACES', 'FOR DARK WINTER'],
          'Gas shortages and power rationing loom as war '
          'damage deepens the energy crisis.',
          icon_bolt)

    # --- footer strip
    fill_rect(0, 952, W, 72, NAVY)
    hline(0, 952, W, GOLD, 3)
    draw_text_centred(
        W // 2, 964,
        'ALSO: GTA VI OUT WORLDWIDE  \u2022  NATO SENDS EARLY-WARNING JETS TO POLAND',
        2, WHITE)
    draw_text_centred(
        W // 2, 988,
        "INDONESIA'S VP RESIGNS  \u2022  FBI CRIME DATABASE BREACH  \u2022  NEPAL PM VISITS INDIA",
        2, GOLD_L)


def main():
    build_page()
    target = write_output()
    print('wrote', target)


if __name__ == '__main__':
    main()
