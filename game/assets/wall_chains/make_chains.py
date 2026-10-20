"""room 79 Torture Room: wall-mounted chains and shackles on the EAST wall's inner side face (dungeon palette).
python3 make_chains.py  -> wall_chains.png (2 variants, 16x44), chain_bones.png (2 variants, 16x16), manifest, previews"""
import os, sys, math, random, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
T = 16; FW, FH = 16, 44
IRON = [(34, 32, 42), (60, 58, 70), (92, 90, 104), (132, 130, 144), (184, 180, 190)]   # dark -> rim
RUST = [(78, 40, 26), (112, 58, 32), (146, 84, 44), (176, 112, 60)]
BONE = [(112, 102, 86), (160, 150, 126), (204, 194, 166), (230, 222, 196)]
OUTC = (14, 10, 20)

def px(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height(): s.set_at((int(x), int(y)), c)

def plate(s, cx, cy, r):
    """iron wall plate (4x6) with 2 rivets on the side face, the ring staple pokes out at its lower-left"""
    for y in range(cy - 3, cy + 3):
        for x in range(cx - 1, cx + 3): px(s, x, y, IRON[1] if x == cx + 2 or y == cy + 2 else IRON[2])
    for x in range(cx - 1, cx + 2): px(s, x, cy - 3, IRON[3])
    px(s, cx, cy - 2, IRON[4]); px(s, cx, cy + 1, IRON[4]); px(s, cx + 1, cy + 1, IRON[0])
    if r.random() < .8: px(s, cx + 2, cy + 2, RUST[1]); px(s, cx + 1, cy + 2, RUST[2])
    px(s, cx - 2, cy, IRON[3]); px(s, cx - 2, cy + 1, IRON[2])          # staple

def ring(s, cx, cy):
    """iron ring 6x6, hollow, lit top-left"""
    pts = [(-1, -3), (0, -3), (1, -3), (2, -2), (2, -1), (2, 0), (2, 1), (1, 2), (0, 2), (-1, 2), (-2, 1), (-2, 0), (-2, -1), (-2, -2)]
    for dx, dy in pts:
        c = IRON[4] if dy <= -2 and dx <= 1 or dx == -2 and dy < 0 else IRON[3] if dy < 1 and dx < 2 else IRON[1]
        px(s, cx + dx, cy + dy, c)

def chain(s, a, b, sag, r, rusty=.25, pitch=3.0):
    """interlocking links along a sagging curve a->b: face-on links (3x5, open centre) alternating with edge-on bars"""
    pts = []
    for k in range(200):
        t = k / 199; pts.append(((a[0] + (b[0] - a[0]) * t) + sag * 4 * t * (1 - t) * -.6, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t) * .4))
    acc, last, out = 0, pts[0], [pts[0]]
    for p in pts[1:]:
        acc += math.hypot(p[0] - last[0], p[1] - last[1]); last = p
        if acc >= pitch: out.append(p); acc = 0
    for k, (x, y) in enumerate(out):
        xi, yi = round(x), round(y); rc = r.random() < rusty
        hi, mid, lo = (RUST[3], RUST[2], RUST[0]) if rc else (IRON[4], IRON[3], IRON[1])
        if k % 2 == 0:
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-1, 1):
                    if abs(dy) == 2 and dx == 1: continue
                    px(s, xi + dx, yi + dy, hi if dx < 0 and dy < 1 else mid if dy < 1 else lo)
            px(s, xi, yi - 2, hi); px(s, xi, yi + 2, lo)
            px(s, xi, yi - 1, OUTC); px(s, xi, yi, OUTC); px(s, xi, yi + 1, OUTC)    # the open centre reads as a dark hole
        else:
            for dy in (-2, -1, 0, 1): px(s, xi, yi + dy, hi if dy < 0 else mid)
            px(s, xi + 1, yi, lo)
    return out[-1]

def shackle(s, cx, cy, open_=True, lying=False):
    """iron cuff: thick ring 7x6 with a dark hole, hinge knuckle at the left; open = the right jaw swung away"""
    ry = 2 if lying else 3
    for y in range(-ry, ry + 1):
        for x in range(-3, 4):
            d = (x / 3.4) ** 2 + (y / (ry + .4)) ** 2
            if d > 1: continue
            inner = (x / 1.6) ** 2 + (y / max(.8, ry - 1.4)) ** 2 < 1
            if inner: px(s, cx + x, cy + y, OUTC); continue
            if open_ and x >= 2 and y >= 0: continue
            px(s, cx + x, cy + y, IRON[4] if y < 0 and x < 1 else IRON[3] if y < 1 else IRON[2] if x < 2 else IRON[1])
    px(s, cx - 3, cy, IRON[4]); px(s, cx - 4, cy, IRON[2])               # hinge knuckle
    if open_:
        px(s, cx + 4, cy + 1, IRON[3]); px(s, cx + 4, cy + 2, IRON[2]); px(s, cx + 3, cy + 3, IRON[2])   # swung-open jaw
    px(s, cx + 1, cy - ry, RUST[2]); px(s, cx - 1, cy + ry, RUST[1])

def bones(s, r, kind):
    """small bone litter on the floor (alpha-ready, outlined later)"""
    if kind == 0:     # femur + knuckle bits
        line(s, BONE[2], (2, 12), (9, 10)); line(s, BONE[1], (2, 13), (9, 11))
        for (x, y) in ((1, 12), (2, 11), (9, 9), (10, 10), (10, 11), (1, 13)): px(s, x, y, BONE[3] if y < 12 else BONE[2])
        px(s, 12, 13, BONE[2]); px(s, 13, 13, BONE[1]); px(s, 6, 14, BONE[2]); px(s, 4, 6, BONE[1])
    else:             # cracked skull, jaw apart, rib
        blob(s, 6, 9, 3.4, 2.8, BONE)
        px(s, 5, 9, OUTC); px(s, 7, 9, OUTC); px(s, 6, 10, BONE[0]); px(s, 4, 8, BONE[3])
        line(s, BONE[0], (7, 7), (8, 9))                       # crack
        line(s, BONE[1], (5, 12), (8, 12)); px(s, 4, 11, BONE[1])   # jaw
        for k in range(4): px(s, 11 + k, 7 + k // 2 + (1 if k == 3 else 0), BONE[2 - (k > 1)])   # rib
    return s

def stain(s, cx, cy, rx, ry, a, r):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1 and (BAYER[y % 4][x % 4] / 16) < 1.1 - d * .8 and 0 <= x < s.get_width() and 0 <= y < s.get_height():
                c = s.get_at((x, y))
                if c.a == 0: s.set_at((x, y), (52, 22, 20, int(a * (1 - d * .5))))

def streak(s, x, y0, y1, r):
    for y in range(y0, y1):
        if r.random() < .85: px(s, x, y, (*RUST[0], 120 - (y - y0) * 8 if 120 - (y - y0) * 8 > 30 else 30))

# frame layout (16x44): sprite top = side-face top (wall cell row, raised 8); side face = x 8..15, y 0..29;
# the floor of the decal's cell is y 8..23, the next cell starts at y 24; the wall foot at the face is around x 7, y ~26
def variant(v):
    r = random.Random(79 + v); s = surf(FW, FH); fx = surf(FW, FH)
    if v == 0:    # high ring: long chain to an open shackle lying on the floor; low ring: short chain + dangling cuff
        plate(s, 12, 5, r); ring(s, 8, 8)
        plate(s, 12, 17, r); ring(s, 8, 20)
        chain(s, (7, 12), (6, 33), 2.0, r); shackle(s, 6, 37, True, True)
        chain(s, (8, 24), (9, 28), 0.3, r, .4); shackle(s, 9, 32, True)
        streak(fx, 13, 8, 18, r); streak(fx, 12, 20, 29, r)
        stain(fx, 6, 39, 5.5, 2.5, 120, r)
    else:         # high ring: long chain to a pair of manacles on a spreader bar; open neck collar on a low ring
        plate(s, 12, 4, r); ring(s, 8, 7)
        chain(s, (8, 11), (8, 27), 1.0, r)
        line(s, IRON[1], (3, 30), (13, 30)); line(s, IRON[4], (3, 29), (13, 29))       # spreader bar
        shackle(s, 4, 34, True); shackle(s, 12, 34, False)
        plate(s, 13, 18, r); ring(s, 9, 21)                                            # empty ring: its prisoner is gone
        streak(fx, 13, 7, 16, r); streak(fx, 14, 21, 28, r); streak(fx, 12, 9, 14, r)
        stain(fx, 8, 39, 6, 3, 130, r)
    o = outline(s)
    out = surf(FW, FH); out.blit(fx, (0, 0)); out.blit(o, (0, 0))
    return out

W = surf(FW * 2, FH); [W.blit(variant(v), (v * FW, 0)) for v in range(2)]
pygame.image.save(W, os.path.join(HERE, "wall_chains.png"))
BN = surf(32, 16)
for k in range(2):
    b_ = surf(16, 16); bones(b_, random.Random(k), k); b_ = outline(b_)
    sh = surf(16, 16); stain(sh, 7, 11, 6, 3, 70, random.Random(k)); sh.blit(b_, (0, 0)); BN.blit(sh, (k * 16, 0))
pygame.image.save(BN, os.path.join(HERE, "chain_bones.png"))

# ---------- placements (room 79, east wall x21; posts: corners y2,y15 and x%5/y%5==2 -> y7,y12) ----------
import art3 as A3
R = rooms(); room = R[79]; g = room["grid"]
POSTS_E = [y for y in range(18) if A3.is_post(g, 21, y)]
CHAIN_GLYPHS = [(20, 7), (20, 10)]
WALL = [("wall_chains/wall_chains.png", 16, 0, 21, 8, "east"), ("wall_chains/wall_chains.png", 16, 1, 21, 10, "east")]
FLOOR = [("wall_chains/chain_bones.png", 16, 0, 19, 9), ("wall_chains/chain_bones.png", 16, 1, 19, 11)]
for _, _, _, wx, wy, _ in WALL: assert not A3.is_post(g, wx, wy) and g[wy][wx] == "#"
def wall_topleft(wx, wy, top): return ((wx - 1) * T, wy * T + top - 8)      # east-wall side face: decal sits in floor cell x-1, from the raised face top
man_ = {"room": 79, "room_name": "Torture Room (interior x3-20, y3-14; table '@' x5-6 y5-7; chain glyphs '{' at (20,7) and (20,10), remapped to '%' today)",
 "sheets": {
  "wall_chains.png": {"frame_size": [FW, FH], "variants": 2, "layer": "east-wall side-face decal (baked into the room after the wall pass, in the wall-decal step of its row)",
      "anchor": "top-left px = ((wall_x-1)*16, wall_y*16 + TOP - 8): the frame's right 8 px cover the wall's 8px inner side face (X-8, raised top), the left half and the lower 16 px lie on the floor at the wall foot",
      "content": "v0: two bolted plates + rings, a long chain to an open shackle lying on the floor and a short chain with a dangling open cuff; v1: high ring, long chain to a pair of manacles on a spreader bar, an open neck collar on a second ring; rust streaks and a dark stain below",
      "blocking": False, "shadow_baked": False, "rows_drawn": "wall_y and the floor below it (to wall_y*16+TOP+36)"},
  "chain_bones.png": {"frame_size": [16, 16], "variants": 2, "layer": "floor decal (baked, under everything)", "anchor": "top-left of cell", "blocking": False,
      "content": "v0: femur and knuckle bits; v1: cracked skull with jaw and a rib; faint dark stain"}},
 "wall_post_cells_east_x21": POSTS_E,
 "placements_room79": {
  "WALL": [list(w) for w in WALL], "FLOOR": [list(f) for f in FLOOR],
  "setpiece_py": "CHAIN_WALL = [(\"wall_chains/wall_chains.png\", 16, 0, 21, 8, \"east\"), (\"wall_chains/wall_chains.png\", 16, 1, 21, 10, \"east\")]\nCHAIN_FLOOR = [(\"wall_chains/chain_bones.png\", 16, 0, 19, 9), (\"wall_chains/chain_bones.png\", 16, 1, 19, 11)]",
  "moved": "glyph (20,7) sits against the east-wall post (21,7) -> that chain set is mounted on wall cell (21,8) (decal over floor cell (20,8)); glyph (20,10) kept (wall cell (21,10), not a post)",
  "glyph_cells": "the '{' cells (20,7) and (20,10) should stop being tables/solid: drop the '{'->'%' FURN remap for room 79 and treat them as plain floor (walkable). The chains are wall decals, the hero walks in front of them"},
 "integration_notes": ["room 79: '{' -> ' ' (walkable floor) instead of '%'; keep the '@' Large Table as is",
                "draw CHAIN_WALL in art3.bake_room's wall-decal step for row wall_y (after that row's posts), blitting the frame at ((x-1)*16, y*16+TOP-8)",
                "draw CHAIN_FLOOR with the other floor decals (setpiece.draw_floor)", "room_themes.json: 79 setpiece true (optional: keeps random decor off the east wall cells x21 y8-11)"]}
json.dump(man_, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)

# ---------- previews: before/after on baked room 79, plain and under darkness (lamp near the chains) ----------
b, TOP = baked(79)
r2 = copy.deepcopy(room); g2 = [list(row) for row in r2["grid"]]
for x, y in CHAIN_GLYPHS: g2[y][x] = " "; r2["walk"][y][x] = True
r2["grid"] = ["".join(row) for row in g2]
for k in ("decor", "_set_done", "set_objs"): r2.pop(k, None)
raw, _ = art3.bake_room(79, r2); raw = raw.copy(); raw.set_colorkey((255, 0, 255)); a = pygame.Surface(raw.get_size()); a.fill((20, 16, 26)); a.blit(raw, (0, 0))
for f, fw, v, x, y in FLOOR: a.blit(BN.subsurface((v * 16, 0, 16, 16)), (x * T, y * T + TOP))
for f, fw, v, wx, wy, _ in WALL: a.blit(W.subsurface((v * FW, 0, FW, FH)), wall_topleft(wx, wy, TOP))
def dark(s, cx, cy, rr=80):
    o = s.copy(); dk = pygame.Surface(s.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 238))
    for r_ in range(rr, 0, -2): pygame.draw.circle(dk, (4, 3, 10, int(238 * (r_ / rr) ** 2.2)), (cx, cy), r_)
    o.blit(dk, (0, 0)); return o
L = (18 * T + 8, 9 * T + TOP + 8)
crop = pygame.Rect(14 * T, 4 * T + TOP, 8 * T, 10 * T)
tiles = [("before", b), ("after", a), ("before, dark + lamp", dark(b, *L)), ("after, dark + lamp", dark(a, *L))]
font = pygame.font.Font(None, 18); S = 3
P = pygame.Surface((crop.w * S * 4 + 50, crop.h * S + 40)); P.fill((40, 36, 48))
for i, (nm, t) in enumerate(tiles):
    P.blit(font.render(nm, True, (230, 220, 200)), (10 + i * (crop.w * S + 10), 6))
    P.blit(pygame.transform.scale(t.subsurface(crop), (crop.w * S, crop.h * S)), (10 + i * (crop.w * S + 10), 24))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
Q = pygame.Surface((a.get_width() * 2 + 10, a.get_height())); Q.fill((40, 36, 48)); Q.blit(b, (0, 0)); Q.blit(a, (a.get_width() + 10, 0))
pygame.image.save(Q, os.path.join(HERE, "preview_room.png"))
Z = pygame.Surface((80, 48)); Z.fill((56, 54, 62)); Z.blit(W, (4, 4)); Z.blit(BN, (44, 4))
pygame.image.save(pygame.transform.scale(Z, (480, 288)), os.path.join(HERE, "preview_sheet.png"))
copy_to_game(HERE, "wall_chains"); print("ok", POSTS_E)
