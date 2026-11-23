#!/usr/bin/env python3
"""Draw the zech entry: a flat world-map infographic of 23 Nov 2026 news.
Pure PIL, system fonts only, no network, no downloaded images."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# --- palette: dark ocean, teal continents, gold pins, red accents ---
OCEAN = (10, 38, 64)        # deep navy
OCEAN2 = (13, 48, 80)
LAND = (31, 138, 122)       # teal
LAND_EDGE = (64, 178, 160)
GOLD = (255, 196, 66)
RED = (226, 62, 52)
WHITE = (245, 247, 250)
MUTED = (168, 196, 214)
DARK = (8, 28, 48)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)

# --- equirectangular projection for the map band ---
MAP_X0, MAP_Y0, MAP_W, MAP_H = 20, 150, 984, 470
def proj(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y0 + (75.0 - lat) / 135.0 * MAP_H
    return (x, y)

# Simplified continent outlines as (lon, lat) polygons.
N_AMERICA = [(-168, 66), (-158, 71), (-140, 70), (-125, 71), (-110, 68),
             (-95, 69), (-82, 66), (-76, 62), (-65, 60), (-55, 52),
             (-60, 47), (-70, 44), (-75, 39), (-81, 32), (-84, 30),
             (-90, 21), (-97, 16), (-105, 20), (-115, 29), (-125, 40),
             (-125, 49), (-135, 58), (-152, 58), (-162, 60), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-32, 68), (-22, 70),
             (-25, 76), (-40, 80), (-58, 76), (-62, 70), (-58, 64)]
S_AMERICA = [(-78, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0),
             (-44, -3), (-35, -8), (-38, -15), (-41, -23), (-48, -28),
             (-58, -35), (-65, -41), (-68, -50), (-70, -54), (-73, -50),
             (-73, -40), (-73, -30), (-71, -20), (-77, -12), (-81, -5),
             (-80, 2), (-78, 9)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 51), (4, 53), (8, 57),
          (10, 59), (5, 60), (10, 62), (18, 69), (25, 71), (31, 70),
          (30, 66), (28, 61), (24, 58), (21, 55), (19, 54), (23, 54),
          (28, 46), (23, 40), (19, 42), (14, 45), (12, 44), (8, 44),
          (3, 43), (-1, 38), (-6, 36), (-10, 36)]
AFRICA = [(-17, 15), (-16, 21), (-10, 31), (-6, 35), (10, 37),
          (11, 34), (20, 32), (30, 31), (32, 31), (35, 28),
          (39, 21), (43, 12), (51, 11), (46, 2), (41, -2),
          (40, -10), (36, -18), (33, -26), (27, -33), (20, -35),
          (16, -29), (12, -18), (9, -1), (9, 4), (4, 6),
          (-8, 5), (-13, 8), (-17, 15)]
ASIA = [(31, 70), (40, 68), (50, 69), (60, 69), (68, 73),
        (75, 73), (85, 76), (100, 77), (110, 74), (125, 73),
        (140, 72), (155, 70), (170, 67), (178, 65), (170, 60),
        (162, 56), (158, 52), (150, 59), (142, 54), (142, 46),
        (135, 43), (130, 38), (127, 35), (122, 31), (120, 25),
        (110, 20), (108, 12), (105, 9), (100, 8), (98, 12),
        (92, 16), (88, 22), (80, 15), (77, 8), (75, 15),
        (72, 20), (66, 25), (61, 25), (57, 26), (52, 26),
        (50, 29), (48, 30), (44, 29), (40, 20), (39, 21),
        (35, 28), (33, 31), (36, 36), (30, 36), (27, 41),
        (23, 40), (28, 46), (24, 45), (30, 46), (33, 44),
        (39, 47), (41, 46), (40, 52), (38, 55), (35, 60),
        (33, 64), (31, 70)]
AUSTRALIA = [(114, -22), (114, -32), (118, -35), (124, -33), (129, -32),
             (132, -32), (136, -35), (140, -38), (146, -39), (150, -37),
             (153, -27), (153, -22), (150, -22), (146, -19), (142, -11),
             (136, -12), (132, -12), (126, -14), (122, -17), (118, -20),
             (114, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57),
      (0, 53), (1, 51), (-2, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38),
         (141, 41), (143, 42), (145, 44), (142, 44), (140, 40),
         (139, 37), (137, 36), (133, 35), (130, 33), (130, 31)]

CONTINENTS = [N_AMERICA, GREENLAND, S_AMERICA, EUROPE, AFRICA, ASIA,
              AUSTRALIA, UK, JAPAN]

# Pins: (number, lon, lat, label lines)
PINS = [
    (1, 36.0, 40.0, "ANTALYA", "COP31 talks collapse"),
    (2, 30.5, 50.4, "KYIV", "Drone hits flats — 14 missing"),
    (3, 16.0, 28.5, "BENGHAZI", "Sea drone hits Russian warship"),
    (4, 56.5, 26.5, "HORMUZ", "Houthis hit Saudi refinery"),
    (5, -0.1, 51.5, "LONDON", "Liverpool win; England to host"),
]

LEGEND = [
    ("1", "ANTALYA — COP31 climate talks collapse; EU rejects deal"),
    ("2", "KYIV — Russian drone hits homes, at least 14 missing"),
    ("3", "BENGHAZI — Ukrainian sea drone hits Russian warship"),
    ("4", "HORMUZ — Houthi strikes on Saudi refinery & radar"),
    ("5", "LONDON — Liverpool beat 10-man Man Utd"),
]

img = Image.new("RGB", (W, H), OCEAN)
d = ImageDraw.Draw(img, "RGBA")

# subtle latitude/longitude grid
for lon in range(-150, 181, 30):
    x = MAP_X0 + (lon + 180) / 360.0 * MAP_W
    d.line([(x, MAP_Y0), (x, MAP_Y0 + MAP_H)], fill=(255, 255, 255, 14), width=1)
for lat in range(-60, 76, 30):
    y = MAP_Y0 + (75 - lat) / 135.0 * MAP_H
    d.line([(MAP_X0, y), (MAP_X0 + MAP_W, y)], fill=(255, 255, 255, 14), width=1)

# map frame
d.rectangle([MAP_X0 - 6, MAP_Y0 - 6, MAP_X0 + MAP_W + 6, MAP_Y0 + MAP_H + 6],
            outline=(255, 255, 255, 60), width=2)

# continents
for poly in CONTINENTS:
    pts = [proj(lon, lat) for lon, lat in poly]
    d.polygon(pts, fill=LAND, outline=LAND_EDGE, width=2)

# --- header ---
d.text((512, 34), "THE WORLD", font=font(72), fill=WHITE, anchor="mt")
d.text((512, 112), "MONDAY 23 NOVEMBER 2026", font=font(36), fill=GOLD, anchor="mt")
d.line([(60, 158 - 14), (964, 158 - 14)], fill=GOLD, width=3)

# --- pins on the map ---
PIN_R = 21
for num, lon, lat, name, _short in PINS:
    x, y = proj(lon, lat)
    d.ellipse([x - PIN_R, y - PIN_R, x + PIN_R, y + PIN_R],
              fill=GOLD, outline=RED, width=4)
    d.text((x, y - 1), str(num), font=font(28), fill=DARK, anchor="mm")

# --- legend: numbered stories below the map ---
lx, ly = 44, 652
d.text((lx, ly), "THE DAY IN FIVE STORIES", font=font(30), fill=GOLD)
ly += 48
for num, line in LEGEND:
    # number chip
    d.ellipse([lx, ly + 2, lx + 34, ly + 36], fill=GOLD, outline=RED, width=3)
    d.text((lx + 17, ly + 18), num, font=font(22), fill=DARK, anchor="mm")
    d.text((lx + 48, ly + 18), line, font=font(27), fill=WHITE, anchor="lm")
    ly += 46

# --- footer: extra stories (two short centred lines, auto-fit to width) ---
def fit_font(text, max_w, start=24):
    for size in range(start, 15, -1):
        f = font(size)
        if f.getlength(text) <= max_w:
            return f
    return font(15)

d.line([(44, 936), (980, 936)], fill=(255, 255, 255, 60), width=2)
d.text((512, 950), "ALSO: England to host Women’s World Cup 2035  •  Alcaraz wins first ATP Finals",
       font=fit_font("ALSO: England to host Women’s World Cup 2035  •  Alcaraz wins first ATP Finals", 960),
       fill=MUTED, anchor="mt")
d.text((512, 982), "Gold $3,603/oz  •  Mexico arrests “El Chapo Isidro”",
       font=font(23), fill=MUTED, anchor="mt")

img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes", img.size)
