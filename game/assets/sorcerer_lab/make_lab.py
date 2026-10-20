"""Room 66 Sorcerer's Secret Laboratory props (abandoned). python3 make_lab.py"""
import os, sys, math, random, json, shutil; HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from art import lerp
from collections import deque
WD = [(36, 24, 20), (60, 40, 30), (86, 60, 42), (114, 84, 58), (146, 112, 78)]
IR = [(28, 28, 34), (50, 50, 58), (80, 80, 92), (120, 120, 134)]
GL = [(70, 90, 100), (120, 150, 160), (190, 220, 226)]                    # glass
POT = {"green": [(30, 70, 40), (60, 130, 60), (130, 200, 100)], "violet": [(56, 30, 80), (110, 60, 150), (180, 130, 220)], "amber": [(90, 50, 20), (170, 110, 40), (240, 190, 90)], "red": [(80, 20, 30), (150, 40, 50), (220, 110, 110)]}
WAX = [(150, 136, 110), (200, 186, 156), (236, 226, 200)]; FL = [(200, 80, 30), (250, 170, 60), (255, 240, 170)]
SH = (8, 6, 12)
def shadow(s, cx, cy, rx, ry, a=120):
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, a))
def wood(u, r, lit=.7):
    for y in range(r.top, r.bottom):
        for x in range(r.left, r.right):
            v = lit - (y - r.top) / max(1, r.height) * .25 + (BAYER[y % 4][x % 4] / 16 - .5) * .2 + (.06 if (x * 3 + y // 3) % 7 == 0 else 0)
            u.set_at((x, y), WD[max(0, min(4, int(v * 5)))])
def flask(u, cx, by, w, h, col, neck=3, fill=.6, round_=True):
    """glass vessel: round or tall body, liquid level, neck, rim highlight"""
    P = POT[col]
    if round_: pygame.draw.ellipse(u, GL[0], (cx - w // 2, by - h, w, h))
    else: pygame.draw.rect(u, GL[0], (cx - w // 2, by - h, w, h))
    lv = by - int(h * fill)
    for y in range(by - h, by):
        for x in range(cx - w // 2, cx + w // 2 + 1):
            if u.get_at((x, y))[:3] == GL[0] and y >= lv: u.set_at((x, y), P[1] if x > cx - w // 4 else P[2])
    if fill > 0: line(u, P[2], (cx - w // 2 + 1, lv), (cx + w // 2 - 2, lv))
    pygame.draw.rect(u, GL[0], (cx - 1, by - h - neck, 2 + (w > 8), neck + 1)); u.set_at((cx - 1, by - h - neck), GL[2])
    u.set_at((cx - w // 2 + 1, by - h + h // 3), GL[2]); u.set_at((cx - w // 2 + 2, by - h + h // 3 - 1), GL[2])
# ---------- shelves of jars (2x1, against the north wall)
def shelf(v):
    W, H = 32, 44; s = surf(W, H); u = surf(W, H); r = random.Random(v + 66)
    shadow(s, 16, H - 3, 15, 3)
    wood(u, pygame.Rect(1, 2, 30, 40), .55); pygame.draw.rect(u, WD[0], (3, 4, 26, 36))
    for sy in (14, 27, 40):
        wood(u, pygame.Rect(1, sy, 30, 3), .9); line(u, WD[4], (1, sy), (30, sy))
    for sy in (14, 27, 40):                                                   # jars on each shelf
        x = 4
        while x < 27:
            w = r.choice((4, 5, 6)); h = r.choice((5, 7, 8)); col = r.choice(list(POT))
            if v == 1 and sy == 27 and x > 12: break                            # gap where jars fell
            if r.random() < .2: pygame.draw.rect(u, WD[2], (x, sy - 4, w, 4)); line(u, WD[4], (x, sy - 4), (x + w - 1, sy - 4))  # old book
            else: flask(u, x + w // 2, sy, w, h - 2, col, neck=2, fill=r.choice((.2, .5, .8)), round_=r.random() < .5)
            x += w + 1
    s.blit(outline(u), (0, 0))
    for k in range(5): line(s, (190, 186, 196, 110), (1 + (29 if v else 0), 2), ((8 - k * 2) if not v else (24 + k * 2), 2 + k * 2))  # cobweb corner
    if v == 1:
        for k in range(8): s.set_at((r.randrange(10, 30), r.randrange(41, 44)), (*GL[r.randrange(1, 3)], 255))   # glass shards at the foot
    return s
# ---------- alchemy bench with alembics (4x1)
def bench():
    W, H = 64, 48; s = surf(W, H); u = surf(W, H)
    shadow(s, 32, H - 3, 31, 3)
    for lx in (3, 57): pygame.draw.rect(u, WD[1], (lx, 30, 4, 17)); line(u, WD[3], (lx, 30), (lx, 46))
    wood(u, pygame.Rect(1, 24, 62, 7), .85); line(u, WD[4], (1, 24), (62, 24)); line(u, WD[0], (1, 30), (62, 30))
    pygame.draw.rect(u, WD[1], (7, 38, 50, 3))                                # stretcher
    flask(u, 10, 24, 10, 10, "green", neck=4, fill=.5)                         # alembic: round flask, burner, swan neck into a receiver
    pygame.draw.rect(u, IR[2], (6, 22, 9, 2))
    line(u, GL[1], (11, 9), (22, 6)); line(u, GL[1], (22, 6), (27, 14)); line(u, GL[2], (11, 8), (21, 5))
    flask(u, 28, 24, 8, 9, "green", neck=2, fill=.3)
    flask(u, 40, 24, 5, 12, "violet", neck=3, fill=.7, round_=False); flask(u, 46, 24, 6, 7, "amber", neck=2, fill=.4)
    pygame.draw.rect(u, IR[1], (51, 18, 9, 6)); line(u, IR[3], (51, 18), (59, 18)); line(u, IR[0], (55, 12), (58, 18), 2)   # mortar + pestle
    pygame.draw.rect(u, WD[2], (33, 20, 5, 4)); line(u, WD[4], (33, 20), (37, 20))                                         # tinder box
    s.blit(outline(u), (0, 0))
    for p in ((18, 26), (19, 27), (35, 26), (44, 25)): s.set_at(p, (*POT["green"][1], 255))                                # drips/stains
    for k in range(4): line(s, (190, 186, 196, 100), (63, 24), (58 + k, 31 - k))
    return s
# ---------- cauldron (2x1), 6-frame bubble loop
def cauldron(f):
    W, H = 32, 40; s = surf(W, H); u = surf(W, H); r = random.Random(f)
    shadow(s, 16, H - 3, 15, 3)
    for k, (x0, x1) in enumerate(((5, 9), (23, 27))): line(u, IR[1], (x0 + 2, 26), (x0, 38), 2); line(u, IR[1], (x1 - 2, 26), (x1, 38), 2)  # tripod legs
    for y in range(32, 38):                                                    # embers under the pot
        for x in range(10, 23):
            if r.random() < .5: u.set_at((x, y), FL[0] if r.random() < .7 else FL[1])
    blob(u, 16, 24, 13, 10, IR)                                                # pot body
    pygame.draw.ellipse(u, IR[0], (3, 12, 26, 8)); pygame.draw.ellipse(u, POT["green"][1], (5, 13, 22, 6))   # rim + brew
    line(u, IR[3], (4, 15), (10, 13))
    for y in range(13, 19):
        for x in range(5, 27):
            if u.get_at((x, y))[:3] == POT["green"][1] and (x + y + f) % 5 == 0: u.set_at((x, y), POT["green"][2])
    for b in range(3):                                                         # bubbles rise/pop on a 6-frame cycle
        ph = (f + b * 2) % 6; bx = 9 + b * 6; by = 16 - (ph // 2)
        if ph < 4: pygame.draw.circle(u, POT["green"][2], (bx, by), 1 + ph // 2); u.set_at((bx - 1, by - 1), (220, 255, 200))
        elif ph == 4: u.set_at((bx - 1, by), (220, 255, 200)); u.set_at((bx + 1, by - 1), (220, 255, 200))
    s.blit(outline(u), (0, 0))
    for k in range(3):                                                         # thin steam wisps
        y = 10 - ((f * 2 + k * 4) % 10); x = 12 + k * 4 + int(math.sin(f + k) * 1.5)
        if y >= 0: s.set_at((x, y), (170, 200, 170, 120)); s.set_at((x, y + 1), (150, 180, 150, 70))
    return s
# ---------- rune circle decal (64x64, 4x4 cells) + faint glow strip
def rune(glow=None):
    W = 64; s = surf(W, W); c = (32, 32)
    base = (140, 110, 176, 190) if glow is None else (190, 150, 255, int(60 + 40 * math.sin(glow * math.pi / 2)))
    dim = (96, 76, 124, 160)
    for rr in (29, 25):
        for a in range(360):
            t = math.radians(a); x, y = c[0] + math.cos(t) * rr, c[1] + math.sin(t) * rr * .8
            if glow is not None or random.Random(a).random() > .12: s.set_at((int(x), int(y)), base)    # worn gaps
    for k in range(5):                                                         # pentagram
        a = math.radians(-90 + k * 144); b = math.radians(-90 + (k + 1) * 144)
        line(s, dim if glow is None else base, (c[0] + math.cos(a) * 24, c[1] + math.sin(a) * 19), (c[0] + math.cos(b) * 24, c[1] + math.sin(b) * 19))
    rnd = random.Random(7)
    for k in range(12):                                                        # glyphs between the rings
        t = math.radians(k * 30 + 15); x, y = int(c[0] + math.cos(t) * 27), int(c[1] + math.sin(t) * 21.6)
        g = rnd.randrange(4)
        pts = [((0, -1), (0, 1)), ((-1, 0), (1, 0)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))][g]
        for p in pts: s.set_at((x + p[0], y + p[1]), base)
        s.set_at((x, y), base)
    if glow is None:
        for k in range(40):                                                    # scuffed by feet / dust
            x, y = rnd.randrange(4, 60), rnd.randrange(8, 56)
            if s.get_at((x, y)).a: s.set_at((x, y), (0, 0, 0, 0))
    return s
# ---------- lectern with an open grimoire (1x1), open grimoires on the floor
def lectern():
    W, H = 16, 32; s = surf(W, H); u = surf(W, H)
    shadow(s, 8, H - 3, 7, 2)
    pygame.draw.rect(u, WD[1], (6, 14, 4, 16)); line(u, WD[3], (6, 14), (6, 29)); pygame.draw.rect(u, WD[2], (3, 28, 10, 3))
    pygame.draw.polygon(u, WD[2], [(1, 14), (15, 14), (13, 8), (3, 8)])
    pygame.draw.polygon(u, (200, 186, 150), [(2, 12), (8, 13), (8, 6), (3, 6)]); pygame.draw.polygon(u, (176, 160, 126), [(8, 13), (14, 12), (13, 6), (8, 6)])
    for y in (8, 10): line(u, (90, 70, 60), (4, y), (7, y)); line(u, (90, 70, 60), (9, y), (12, y))
    u.set_at((5, 11), POT["red"][1]); line(u, (120, 30, 30), (8, 13), (8, 17))                              # sigil + bookmark ribbon
    s.blit(outline(u), (0, 0)); return s
def grimoire(v):
    s = surf(16, 16); u = surf(16, 16)
    shadow(s, 8, 13, 7, 2, 90)
    cov = (70, 30, 40) if v == 0 else (40, 40, 70)
    pygame.draw.rect(u, cov, (1, 5, 14, 8))
    pygame.draw.polygon(u, (196, 182, 146), [(2, 6), (8, 7), (8, 12), (2, 11)]); pygame.draw.polygon(u, (172, 156, 122), [(8, 7), (14, 6), (14, 11), (8, 12)])
    for y in (8, 10): line(u, (90, 70, 60), (3, y), (6, y)); line(u, (90, 70, 60), (10, y), (13, y))
    if v == 1: pygame.draw.polygon(u, (210, 196, 160), [(9, 7), (14, 3), (14, 6)])                           # loose page
    s.blit(outline(u), (0, 0)); return s
# ---------- candles + flame strip
def candles(v):
    s = surf(16, 16); u = surf(16, 16)
    shadow(s, 8, 14, 6, 2, 90)
    hs = ((5, 8), (9, 5), (12, 3)) if v == 0 else ((8, 10),)
    for x, h in hs:
        pygame.draw.rect(u, WAX[1], (x - 1, 14 - h, 3, h)); u.set_at((x - 1, 14 - h), WAX[2]); u.set_at((x + 1, 14 - h + 1), WAX[0])
        u.set_at((x + 2, 14 - h + 2), WAX[1])                                                                   # drip
    pygame.draw.ellipse(u, WAX[0], (2, 12, 13, 3))                                                              # melted pool
    s.blit(outline(u), (0, 0)); return s, [(x, 14 - h - 2) for x, h in hs]
def flame(f, tips):
    s = surf(16, 16)
    for i, (x, y) in enumerate(tips):
        dx = (0, 1, 0, -1)[(f + i) % 4]; hh = (3, 2, 3, 4)[(f + i * 3) % 4]
        for k in range(hh):
            c = FL[2] if k == 0 else FL[1] if k < hh - 1 else FL[0]
            s.set_at((x + (dx if k == hh - 1 else 0), y - k + 1), (*c, 255))
    return s
# ---------- decay
def spill(v):
    s = surf(32, 16); col = POT["green" if v == 0 else "violet"]; r = random.Random(v * 5)
    for k in range(6): pygame.draw.ellipse(s, (*col[0], 200), (r.randrange(0, 18), r.randrange(4, 10), r.randrange(6, 14), r.randrange(3, 6)))
    for k in range(5): s.set_at((r.randrange(4, 28), r.randrange(5, 12)), (*col[2], 220))
    u = surf(32, 16); flask(u, 26, 12, 6, 5, "green" if v == 0 else "violet", neck=2, fill=0)
    u = pygame.transform.rotate(u, 90 if v else -90).subsurface((0, 0, 16, 32)) if False else u
    s.blit(outline(u), (0, 0)); return s
def glass(v):
    s = surf(16, 16); r = random.Random(v + 40)
    for k in range(9):
        x, y = r.randrange(2, 14), r.randrange(6, 14); c = GL[r.randrange(0, 3)]
        s.set_at((x, y), (*OUT, 255)); s.set_at((x + 1, y), (*c, 255)); s.set_at((x + 1, y - 1), (*GL[2], 255)) if k % 3 == 0 else None
    return s
def strip(frames):
    w, h = frames[0].get_size(); S = surf(w * len(frames), h)
    for i, f in enumerate(frames): S.blit(f, (i * w, 0))
    return S
OUTF = {}
def save(n, S): pygame.image.save(S, os.path.join(HERE, n)); OUTF[n] = S; return S
SHF = save("lab_shelf_jars.png", strip([shelf(0), shelf(1)])); BN = save("alchemy_bench.png", bench())
CA = save("cauldron.png", strip([cauldron(f) for f in range(6)])); RU = save("rune_circle.png", rune()); RG = save("rune_circle_glow.png", strip([rune(g) for g in range(4)]))
LE = save("lectern_grimoire.png", lectern()); GR = save("grimoire_open.png", strip([grimoire(0), grimoire(1)]))
c0, t0 = candles(0); c1, t1 = candles(1); CD = save("candles.png", strip([c0, c1]))
CF0 = save("candle_flame_cluster.png", strip([flame(f, t0) for f in range(4)])); CF1 = save("candle_flame_single.png", strip([flame(f, t1) for f in range(4)]))
SP = save("spill_potion.png", strip([spill(0), spill(1)])); BG = save("broken_glass.png", strip([glass(0), glass(1)]))
shutil.copy(os.path.join(ART, "decor", "cobweb.png"), HERE)
# ---------- placements (0-based cells, room 66 interior x5-22, y3-14; door west at rows 8-9; Crystal Ball item at (9,12) kept clear)
PL = [  # name, file, frame, cell x, cell y, footprint w, h, blocking, layer
 ("shelf_jars", "lab_shelf_jars.png", 0, 6, 3, 2, 1, True, "sprite"), ("shelf_jars", "lab_shelf_jars.png", 1, 20, 3, 2, 1, True, "sprite"),
 ("alchemy_bench", "alchemy_bench.png", 0, 10, 3, 4, 1, True, "sprite"),
 ("cauldron", "cauldron.png", "anim", 18, 12, 2, 1, True, "sprite"),
 ("lectern_grimoire", "lectern_grimoire.png", 0, 16, 3, 1, 1, True, "sprite"),
 ("rune_circle", "rune_circle.png", 0, 13, 7, 4, 4, False, "floor decal"),
 ("grimoire_open", "grimoire_open.png", 0, 21, 8, 1, 1, False, "floor decal"), ("grimoire_open", "grimoire_open.png", 1, 7, 13, 1, 1, False, "floor decal"),
 ("candles", "candles.png", 0, 12, 6, 1, 1, False, "sprite"), ("candles", "candles.png", 1, 17, 6, 1, 1, False, "sprite"),
 ("candles", "candles.png", 1, 12, 11, 1, 1, False, "sprite"), ("candles", "candles.png", 0, 17, 11, 1, 1, False, "sprite"),
 ("spill_potion", "spill_potion.png", 0, 14, 4, 2, 1, False, "floor decal"), ("spill_potion", "spill_potion.png", 1, 19, 9, 2, 1, False, "floor decal"),
 ("broken_glass", "broken_glass.png", 0, 21, 4, 1, 1, False, "floor decal"), ("broken_glass", "broken_glass.png", 1, 8, 5, 1, 1, False, "floor decal"),
 ("cobweb", "cobweb.png", 0, 5, 3, 1, 1, False, "wall-top-corner"), ("cobweb", "cobweb.png", "flip", 22, 3, 1, 1, False, "wall-top-corner")]
R = rooms()[66]; walk = [row[:] for row in R["walk"]]
for n, f, fr, x, y, w, h, blk, lay in PL:
    if blk:
        for yy in range(y, y + h):
            for xx in range(x, x + w): walk[yy][xx] = False
def bfs(start):
    seen = {start}; q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 24 and 0 <= ny < 18 and walk[ny][nx] and (nx, ny) not in seen: seen.add((nx, ny)); q.append((nx, ny))
    return seen
reach = bfs((0, 8)); orig = sum(1 for yy in range(18) for xx in range(24) if R["walk"][yy][xx]); allw = sum(1 for yy in range(18) for xx in range(24) if walk[yy][xx])
assert (9, 12) in reach and len(reach) == allw, ("blocked!", len(reach), allw)
CANDLE_LIGHTS = {0: t0, 1: t1}
def anchor(f, fr):
    S = OUTF.get(f); return None
SIZES = {"lab_shelf_jars.png": (32, 44), "alchemy_bench.png": (64, 48), "cauldron.png": (32, 40), "lectern_grimoire.png": (16, 32), "candles.png": (16, 16), "rune_circle.png": (64, 64),
         "grimoire_open.png": (16, 16), "spill_potion.png": (32, 16), "broken_glass.png": (16, 16), "cobweb.png": (16, 16)}
man = {"room": 66, "room_name": "Sorcerers Secret Laboratory", "style": "abandoned: cobwebs, dust, spills, broken glass; muted potion colours, no baked glow",
 "sheets": {
  "lab_shelf_jars.png": {"frame_size": [32, 44], "variants": 2, "footprint_tiles": [2, 1], "anchor": {"px": [16, 43]}, "blocking": True, "shadow_baked": True, "note": "against the north wall; v1 has fallen jars + shards"},
  "alchemy_bench.png": {"frame_size": [64, 48], "variants": 1, "footprint_tiles": [4, 1], "anchor": {"px": [32, 47]}, "blocking": True, "shadow_baked": True, "note": "alembic (flask, swan neck, receiver), tall/round flasks, mortar and pestle"},
  "cauldron.png": {"frame_size": [32, 40], "frames": 6, "fps": 6, "loop": True, "footprint_tiles": [2, 1], "anchor": {"px": [16, 39]}, "blocking": True, "shadow_baked": True,
                   "light_point": {"px": [16, 16], "color": [120, 220, 110], "radius_hint": 40, "flicker": "slow"}, "ember_light": {"px": [16, 35], "color": [255, 130, 50], "radius_hint": 24}},
  "rune_circle.png": {"frame_size": [64, 64], "variants": 1, "footprint_tiles": [4, 4], "anchor": "top-left of the top-left cell", "layer": "floor decal (baked)", "blocking": False},
  "rune_circle_glow.png": {"frame_size": [64, 64], "frames": 4, "fps": 2, "loop": True, "optional": True, "anchor": "same as rune_circle.png", "layer": "additive overlay above the floor, below sprites", "note": "faint violet pulse; no bloom"},
  "lectern_grimoire.png": {"frame_size": [16, 32], "variants": 1, "footprint_tiles": [1, 1], "anchor": {"px": [8, 31]}, "blocking": True, "shadow_baked": True},
  "grimoire_open.png": {"frame_size": [16, 16], "variants": 2, "anchor": "top-left of the cell", "layer": "floor decal", "blocking": False},
  "candles.png": {"frame_size": [16, 16], "variants": 2, "anchor": {"px": [8, 15]}, "blocking": False, "shadow_baked": True, "note": "v0 cluster of 3, v1 single"},
  "candle_flame_cluster.png": {"frame_size": [16, 16], "frames": 4, "fps": 8, "overlay_for": "candles v0, same position", "light_points_px": t0, "light": {"color": [255, 190, 110], "radius_hint": 28}},
  "candle_flame_single.png": {"frame_size": [16, 16], "frames": 4, "fps": 8, "overlay_for": "candles v1, same position", "light_points_px": t1, "light": {"color": [255, 190, 110], "radius_hint": 22}},
  "spill_potion.png": {"frame_size": [32, 16], "variants": 2, "anchor": "top-left of the first cell", "layer": "floor decal", "blocking": False, "note": "v0 green, v1 violet, with an empty toppled flask"},
  "broken_glass.png": {"frame_size": [16, 16], "variants": 2, "anchor": "top-left of the cell", "layer": "floor decal", "blocking": False},
  "cobweb.png": {"same_as": "decor/cobweb.png", "placement": "wall-top-corner"}},
 "placements_room66": [{"name": n, "file": f, "frame": fr, "cell": [x, y], "footprint": [w, h], "blocking": blk, "layer": lay,
                        **({"world_anchor": [x * 16 + w * 8, (y + h) * 16], "depth_sort_y": (y + h) * 16} if lay == "sprite" else {"world_topleft": [x * 16, y * 16]})} for n, f, fr, x, y, w, h, blk, lay in PL],
 "bfs_check": f"all {allw} walkable cells stay reachable from the west door (0,8); Crystal Ball cell (9,12) clear and reachable",
 "lights_room66": "cauldron light_point + embers, one light per candle flame tip (cell origin + light_points_px), all from the manifest"}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---------- mock preview on baked room 66, unlit + dark/lit
b, TOP = baked(66)
fl = surf(*b.get_size())
def fr_of(S, i, w): return S.subsurface((i * w, 0, w, S.get_height()))
for n, f, fr, x, y, w, h, blk, lay in PL:
    if lay == "floor decal":
        S = OUTF[f]; fw = SIZES[f][0]; b.blit(fr_of(S, fr, fw) if S.get_width() > fw else S, (x * 16, y * 16 + TOP))
b.blit(fr_of(RG, 1, 64), (13 * 16, 7 * 16 + TOP), special_flags=pygame.BLEND_RGBA_ADD) if False else None
gl = fr_of(RG, 1, 64).copy(); b.blit(gl, (13 * 16, 7 * 16 + TOP))
cw = pygame.image.load(os.path.join(HERE, "cobweb.png")).subsurface((0, 0, 16, 16))
sprites = []
for n, f, fr, x, y, w, h, blk, lay in PL:
    if lay == "sprite":
        S = OUTF[f]; fw, fh = SIZES[f]; img = fr_of(S, 0 if fr == "anim" else fr, fw) if S.get_width() > fw else S
        sprites.append(((y + h) * 16, img, x * 16 + w * 8 - fw // 2, (y + h) * 16 + TOP - fh, f, fr))
    elif lay == "wall-top-corner": b.blit(cw if fr != "flip" else pygame.transform.flip(cw, True, False), (x * 16, y * 16 + TOP))
lights = []
for Y, img, X, Yp, f, fr in sorted(sprites, key=lambda t: t[0]):
    b.blit(img, (X, Yp))
    if f == "candles.png":
        b.blit(fr_of(CF0 if fr == 0 else CF1, 1, 16), (X, Yp)); lights += [(X + px, Yp + py, (255, 190, 110), 28) for px, py in (t0 if fr == 0 else t1)]
    if f == "cauldron.png": lights += [(X + 16, Yp + 16, (120, 220, 110), 40), (X + 16, Yp + 35, (255, 130, 50), 24)]
# crystal ball stand-in so the item spot is visible
it = os.path.join(GAME, "assets", "items", "crystal_ball.png")
if os.path.exists(it): b.blit(pygame.image.load(it), (9 * 16, 12 * 16 + TOP))
lit = b.copy(); dk = pygame.Surface(b.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 225))
for (lx, ly, col, rr) in lights:
    for r_ in range(rr, 0, -2): pygame.draw.circle(dk, (4, 3, 10, int(225 * (r_ / rr) ** 1.6)), (lx, ly), r_)
lit.blit(dk, (0, 0))
glow = surf(*b.get_size())
for (lx, ly, col, rr) in lights: pygame.draw.circle(glow, (*col, 26), (lx, ly), rr // 2)
lit.blit(glow, (0, 0))
crop = pygame.Rect(56, 24, 328, 240)
P = pygame.Surface((crop.w * 4 + 30, crop.h * 2 + 20)); P.fill((40, 36, 48))
P.blit(pygame.transform.scale(b.subsurface(crop), (crop.w * 2, crop.h * 2)), (10, 10)); P.blit(pygame.transform.scale(lit.subsurface(crop), (crop.w * 2, crop.h * 2)), (crop.w * 2 + 20, 10))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
from PIL import Image
fr_ = []
for f in range(6):
    Z = pygame.Surface((96, 72)); Z.fill((30, 26, 34)); Z.blit(fr_of(CA, f, 32), (4, 20)); Z.blit(fr_of(CF0, f % 4, 16), (44, 40)); Z.blit(fr_of(CD, 0, 16), (44, 40)); Z.blit(fr_of(CF0, f % 4, 16), (44, 40)); Z.blit(fr_of(RG, f % 4, 64), (60, 8))
    Z = pygame.transform.scale(Z, (384, 288)); fr_.append(Image.frombytes("RGB", Z.get_size(), pygame.image.tobytes(Z, "RGB")))
fr_[0].save(os.path.join(HERE, "preview_anim.gif"), save_all=True, append_images=fr_[1:], duration=160, loop=0)
copy_to_game(HERE, "sorcerer_lab"); print("ok", allw, len(reach))
