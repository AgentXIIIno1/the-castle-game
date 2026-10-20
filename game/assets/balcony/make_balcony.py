"""Room 33 balcony: garden view below the railing (underlay) + stone balustrade pieces for the '|' '>' '.' "'" '-' rail glyphs. python3 make_balcony.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
T = 16; TOP = 24
VX0 = 10                                    # view covers cells x10..23 (everything east of the rail column x9), all rows, plus the TOP strip
VW, VH = (24 - VX0) * T, 18 * T + TOP       # 224 x 312, blit at bake px (160, 0)
HAZE = (46, 58, 76)
GR = [(22, 40, 26), (32, 56, 32), (44, 74, 40), (60, 94, 50), (84, 118, 64)]
GRAV = [(70, 64, 58), (96, 88, 76), (124, 114, 96)]
HEDGE = [(18, 36, 22), (34, 62, 34), (52, 88, 44), (80, 118, 60)]
TREE = [(16, 32, 26), (28, 54, 36), (44, 78, 46), (70, 108, 60)]
def view():
    """garden seen from above at a distance: drawn at half resolution (fewer details = further away), then 2x nearest; haze + darkening increase eastwards"""
    w, h = VW // 2, VH // 2; s = surf(w, h); r = random.Random(33)
    fcx, fcy = ((15 - VX0) * T + 8) // 2, (9 * T + 8 + TOP) // 2           # fountain centre (cell 15,9)
    for y in range(h):
        for x in range(w):
            n = (math.sin(x * .7 + y * .3) + math.sin(x * .23 - y * .51) * 1.3) * .08
            l = .5 + n + (BAYER[y % 4][x % 4] / 16 - .5) * .25
            c = GR[max(0, min(4, int(l * 5)))]
            d = math.hypot(x - fcx, (y - fcy) * 1.15)
            if d < 30: c = GRAV[max(0, min(2, int((l + .1) * 3)))]                  # gravel plaza round the fountain
            elif d < 32: c = GRAV[0]
            if (abs(y - fcy) < 3 or abs(x - fcx) < 3) and d >= 30: c = GRAV[1] if BAYER[y % 4][x % 4] > 4 else GRAV[0]   # cross paths
            s.set_at((x, y), (*c, 255))
    def hedge(rx, ry, rw, rh):
        pygame.draw.rect(s, OUT, (rx - 1, ry - 1, rw + 2, rh + 3))
        for y in range(ry, ry + rh + 1):
            for x in range(rx, rx + rw):
                l = .75 - (y - ry) / max(1, rh) * .5 + (BAYER[y % 4][x % 4] / 16 - .5) * .3
                s.set_at((x, y), (*HEDGE[max(0, min(3, int(l * 4)))], 255) if y < ry + rh else (*HEDGE[0], 255))
        line(s, HEDGE[3], (rx, ry), (rx + rw - 1, ry))
    for (rx, ry, rw, rh) in ((14, 20, 26, 5), (60, 20, 30, 5), (14, 130, 26, 5), (60, 130, 30, 5), (8, 40, 5, 30), (8, 92, 5, 30), (93, 40, 5, 30), (93, 92, 5, 30)):
        hedge(rx, ry, rw, rh)
    for (cx, cy) in ((14, 50), (80, 48), (20, 112), (82, 116)):                 # flower beds (faded)
        for k in range(16):
            x, y = cx + r.randrange(-5, 6), cy + r.randrange(-3, 4)
            if 0 <= x < w and 0 <= y < h: s.set_at((x, y), (*r.choice([(130, 70, 80), (150, 130, 70), (110, 90, 130)]), 255))
    def tree(cx, cy, rr):
        for y in range(cy - rr - 1, cy + rr + 3):                               # cast shadow then canopy
            for x in range(cx - rr, cx + rr + 4):
                if 0 <= x < w and 0 <= y < h and math.hypot(x - cx - 2, y - cy - 2) <= rr: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (6, 10, 10), .5))
        blob(s, cx, cy, rr, rr * .9, TREE)
        for k in range(rr * 2):
            a = r.random() * 6.28; x, y = int(cx + math.cos(a) * rr * .6) - 1, int(cy + math.sin(a) * rr * .6) - 1
            if 0 <= x < w and 0 <= y < h and x < cx: s.set_at((x, y), TREE[3])
    for (cx, cy, rr) in ((104, 8, 9), (88, 2, 7), (110, 30, 7), (108, 70, 8), (110, 100, 6), (104, 146, 9), (86, 154, 7), (60, 156, 6), (30, 154, 7), (40, 2, 6), (64, 4, 5)):
        tree(cx, cy, rr)
    S = pygame.transform.scale(s, (VW, VH))
    px = pygame.surfarray.pixels3d(S)
    import numpy as np
    X = np.arange(VW)[:, None] / VW; Y = np.arange(VH)[None, :] / VH
    f = np.clip(.18 + X * .32 + (np.abs(Y - .5) * 2) ** 3 * .18, 0, .6)          # depth haze: more to the east and toward the far top/bottom
    for i in range(3): px[:, :, i] = (px[:, :, i] * (1 - f) + HAZE[i] * f) * .82
    del px
    sh = surf(VW, VH)                                                            # shadow of the balcony on the garden + dark drop below the rail
    for x in range(22):
        a = int(200 * (1 - x / 22) ** 1.5)
        pygame.draw.line(sh, (6, 6, 12, a), (x, 0), (x, VH - 1))
    S.blit(sh, (0, 0))
    return S
def rail(kind):
    """16x24 cells (rise 8 px like walls): weathered stone balustrade, coping on top, balusters toward the void (east)"""
    ST = [(52, 48, 56), (78, 74, 84), (104, 100, 110), (132, 126, 138), (160, 154, 164)]
    s = surf(16, 24); u = surf(16, 24)
    if kind in ("|", "-"):
        if kind == "|":
            for y in range(2, 24, 4):                                            # balusters (east side, seen past the coping)
                pygame.draw.rect(u, ST[1], (9, y, 4, 3)); u.set_at((9, y), ST[3])
            pygame.draw.rect(u, ST[2], (3, 0, 7, 24)); line(u, ST[4], (3, 0), (3, 23)); line(u, ST[1], (9, 0), (9, 23))   # coping
            for y in (5, 13, 21): line(u, ST[1], (4, y), (8, y))
        else:
            for x in range(1, 16, 4): pygame.draw.rect(u, ST[1], (x, 14, 3, 8)); line(u, ST[3], (x, 14), (x, 21))
            pygame.draw.rect(u, ST[2], (0, 8, 16, 6)); line(u, ST[4], (0, 8), (15, 8)); line(u, ST[1], (0, 13), (15, 13))
            pygame.draw.rect(u, ST[1], (0, 22, 16, 2))
    else:                                                                        # pier: square post with a ball finial
        pygame.draw.rect(u, ST[1], (2, 12, 12, 12)); line(u, ST[3], (2, 12), (2, 23))
        pygame.draw.rect(u, ST[2], (1, 8, 14, 5)); line(u, ST[4], (1, 8), (14, 8)); line(u, ST[0], (1, 12), (14, 12))
        blob(u, 8, 5, 4, 4, ST[1:]); u.set_at((6, 3), ST[4])
        if kind == ">": pygame.draw.rect(u, ST[2], (4, 13, 4, 11)); line(u, ST[3], (4, 13), (4, 23))   # rail continues behind
    s.blit(outline(u), (0, 0))
    r = random.Random(ord(kind))
    for k in range(5):
        x, y = r.randrange(2, 14), r.randrange(4, 22)
        if s.get_at((x, y)).a and s.get_at((x, y))[:3] != OUT: s.set_at((x, y), r.choice([(50, 74, 40), (74, 100, 52)]))   # moss
    return s
V = view(); pygame.image.save(V, os.path.join(HERE, "balcony_view.png"))
KINDS = ["|", ">", ".", "'", "-"]
RS = surf(16 * len(KINDS), 24)
for i, k in enumerate(KINDS): RS.blit(rail(k), (i * 16, 0))
pygame.image.save(RS, os.path.join(HERE, "balcony_rail.png"))
json.dump({"room": 33, "room_name": "Balcony Looking Over The Castle Gardens",
  "balcony_view.png": {"size": [VW, VH], "layer": "underlay (baked, before anything else)", "placement": "blit at bake-surface px (160, 0) = cells x10-23, rows 0-17 plus the 24 px TOP strip; replaces the magenta void AND the floor patches currently baked under the fountain/bush cells there",
     "content": "garden seen from above: lawn, gravel plaza centred on the fountain cell (15,9), cross paths, clipped hedges, faded flower beds, treetops at the far edges; drawn at half resolution + depth haze toward the east, darker than the balcony; shadow band from the balcony along its west edge", "shadow_baked": True},
  "balcony_rail.png": {"frame_size": [16, 24], "frames": KINDS, "anchor": "frame top-left = (x*16, y*16 + TOP - 8): rises 8 px like the wall tops; bottom of the frame = bottom of the cell",
     "mapping": {"'|' (x9)": 0, "'>' (x9, currently remapped to the '%' table)": 1, "'.' (9,1) north end": 2, "\"'\" (9,16) south end": 3, "'-' (8,1) and (8,16)": 4},
     "blocking": "unchanged (rail cells stay solid)", "depth_sort_y": "(y+1)*16", "shadow_baked": False},
  "recommendations": {"fountain_and_bushes": "keep drawing them on top of the view; optionally multiply them by (200,206,218) so they sit in the haze", "lighting": "no extra light needed; the view is pre-darkened"}},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# preview: current bake vs. view underlay + rails + fountain/bushes
b0, TOP_ = baked(33); R = rooms()[33]; g = R["grid"]
raw, _ = art3.bake_room(33, R); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0)); b.blit(V, (160, 0))
for y in range(18):
    for x in range(24):
        ch = g[y][x]; orig = open(os.path.join(GAME, "../map/rooms_layout/room_33.txt")).read().split("\n")[4 + y][1 + x]
        if x <= 9 and orig in KINDS and (x == 9 or orig == "-"): b.blit(RS.subsurface((KINDS.index(orig) * 16, 0, 16, 24)), (x * 16, y * 16 + TOP_ - 8))
fd = os.path.join(GAME, "assets", "fountain"); fa = pygame.image.load(os.path.join(fd, "fountain_balcony_full.png")); fan = json.load(open(os.path.join(fd, "manifest.json")))["anchor"]["px"]
fr = fa.subsurface((0, 0, 48, 60)).copy(); fr.fill((200, 206, 218), special_flags=pygame.BLEND_RGB_MULT); b.blit(fr, (14 * 16 + 24 - fan[0], 11 * 16 + TOP_ - fan[1]))
for y in range(18):
    for x in range(24):
        if g[y][x] in '*+':
            bb = art3.make_bush(g[y][x] == '*', (k := (x * 3 + y) % 4) + (0 if g[y][x] == '*' else 9)).copy(); bb.fill((200, 206, 218), special_flags=pygame.BLEND_RGB_MULT); b.blit(bb, (x * 16 + 8 - bb.get_width() // 2, y * 16 + 16 - bb.get_height() + 3 + TOP_))
bush = pygame.image.load(os.path.join(GAME, "assets", "decor", "bush_big.png")) if os.path.exists(os.path.join(GAME, "assets", "decor", "bush_big.png")) else None
P = pygame.Surface((384 * 2 + 30, 312 * 2 // 1 + 20)); P.fill((40, 36, 48))
P.blit(pygame.transform.scale(b0, (384, 312)), (10, 10)); P.blit(pygame.transform.scale(b, (768, 624)).subsurface((0, 0, 384 + 384, 624)), (20 + 384, 10)) if False else None
P = pygame.Surface((384 * 2 * 2 + 30, 312 * 2 + 20)); P.fill((40, 36, 48))
P.blit(pygame.transform.scale(b0, (768, 624)), (10, 10)); P.blit(pygame.transform.scale(b, (768, 624)), (788, 10))
pygame.image.save(P, os.path.join(HERE, "preview.png")); copy_to_game(HERE, "balcony"); print("ok", bush is not None)
