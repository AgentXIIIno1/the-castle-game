"""Yellow Room (room 40): faded ochre floor, yellow wall sheets (room83 sheet layout), yellow decor + bed cover. python3 make_yellow.py"""
import os, sys, math, random, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *
from art import lerp
import numpy as np
src = open(os.path.join(ART, "tiles", "make_tiles.py")).read()                     # reuse the wall-sheet drawers verbatim (same layout as room83)
exec(src[src.index("T = 16; SIDE"):src.index("def dirt(")])
from art3 import FACE
T = 16
OCHRE = [(214, 162, 54), (232, 184, 70), (204, 150, 48), (240, 200, 96), (196, 160, 70)]          # faded yellow stone for walls
def floor_tile(v):
    """worn glazed ochre tiles (8x8 quarter tiles), grout, chips, dust bloom"""
    r = random.Random(v * 13 + 1); s = surf(T, T); pal = [(118, 90, 40), (146, 114, 52), (170, 136, 64), (192, 160, 84), (214, 186, 118)]
    for y in range(T):
        for x in range(T):
            q = v % 2; lx, ly = x, y
            l = .62 - lx / 16 * .15 - ly / 16 * .2 + q * .06 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
            c = pal[max(0, min(4, int(l * 5)))]
            if lx == 0 or ly == 0: c = (104, 80, 40)                                       # grout
            elif lx == 1 and ly < 15 or ly == 1 and lx < 15: c = lerp(c, (240, 220, 160), .3)   # rim highlight
            s.set_at((x, y), lerp(c, (120, 112, 100), .18))                               # faded
    for k in range(v % 3 + 1):                                                            # chips + cracks
        x, y = r.randrange(2, 14), r.randrange(2, 14); s.set_at((x, y), (60, 44, 26)); s.set_at((x + 1, y), pal[4]) if x < 15 else None
    if v in (2, 5):
        for i in range(5): s.set_at((3 + i, 5 + (i * 7) % 4), (70, 54, 30))
    if v >= 4:                                                                             # dusty
        for y in range(T):
            for x in range(T):
                if BAYER[y % 4][x % 4] / 16 < .18 and r.random() < .6: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (180, 170, 150), .5))
    return s
def sheet(tiles, w, h, cols):
    rows = (len(tiles) + cols - 1) // cols; S = surf(w * cols, h * rows)
    for i, t in enumerate(tiles): S.blit(t, ((i % cols) * w, (i // cols) * h))
    return S
rnd = random.Random(40); out = {}
def save(n, S): pygame.image.save(S, os.path.join(HERE, n)); out[n] = S; return n
FL = [floor_tile(v) for v in range(6)]; save("yellow_floor.png", sheet(FL, T, T, 6))
tones = OCHRE
YT = [wall_top(rnd, tones) for _ in range(6)]; YF = [wall_front(rnd, tones) for _ in range(6)]
YS = [side_face(rnd, "left", tones) for _ in range(2)] + [side_face(rnd, "right", tones) for _ in range(2)]
save("yellow_wall_tops.png", sheet(YT, T, T, 6)); save("yellow_wall_fronts.png", sheet(YF, T, FACE, 6)); save("yellow_side_walls.png", sheet(YS, SIDE, T + FACE, 4))
# ---------- decor
def wallpaper(v):
    """peeling faded yellow damask wallpaper over the wall face (16x14), curled strip, bare plaster behind"""
    s = surf(T, FACE); r = random.Random(v + 3); base = (196, 170, 96); dark = (160, 132, 64); plaster = (150, 140, 120)
    peel = 6 + v * 3
    for y in range(FACE):
        for x in range(T):
            if x >= peel and y > 3 + (x - peel) // 2: c = plaster if (x + y) % 3 else (130, 120, 104)   # bare plaster
            else:
                c = base if ((x // 2 + y // 3) % 3) else dark                                          # damask stripe
                if (x % 6 == 3 and y % 5 == 2): c = (214, 190, 116)
                c = lerp(c, (130, 120, 100), .2 + (y / FACE) * .15)
            s.set_at((x, y), (*c, 230))
    for y in range(3, FACE):                                                                       # curled edge with shadow
        x = peel + (y - 3) // 2
        if x < T: s.set_at((x, y), (230, 210, 150, 255)); s.set_at((min(T - 1, x + 1), y), (60, 48, 30, 200))
    return s
def mirror(v):
    W, H = 16, 24; s = surf(W, H); u = surf(W, H); G = [(100, 76, 30), (150, 114, 44), (190, 150, 62), (226, 196, 110)]
    pygame.draw.ellipse(u, G[1], (1, 1, 14, 20)); pygame.draw.ellipse(u, (60, 66, 70), (4, 4, 8, 14))
    for y in range(4, 18):
        for x in range(4, 12):
            if u.get_at((x, y))[:3] == (60, 66, 70):
                c = (90, 100, 106) if (x - y) % 7 in (0, 1) else (56, 62, 66)
                if v == 1 and x + y > 17 and (x * y) % 3 == 0: c = (30, 30, 34)                   # cracked silvering
                u.set_at((x, y), c)
    line(u, (180, 196, 200), (5, 6), (7, 4)); pygame.draw.arc(u, G[3], (1, 1, 14, 20), 1.6, 3.4, 1)
    for (x, y) in ((8, 0), (8, 21), (0, 11), (15, 11)): u.set_at((x, y), G[2])
    for k in range(5): u.set_at((random.Random(v + k).randrange(2, 14), random.Random(k * 3 + v).randrange(2, 20)), (90, 80, 40)) # tarnish
    if v == 1: line(u, (24, 20, 26), (6, 9), (10, 15))
    s.blit(outline(u), (0, 0)); return s
def frame_portrait(v):
    W, H = 16, 20; u = surf(W, H); G = [(100, 76, 30), (150, 114, 44), (190, 150, 62), (226, 196, 110)]
    pygame.draw.rect(u, G[1], (0, 0, 16, 20)); line(u, G[3], (0, 0), (15, 0)); line(u, G[3], (0, 0), (0, 19)); pygame.draw.rect(u, (40, 30, 26), (3, 3, 10, 14))
    pygame.draw.ellipse(u, (120, 100, 80), (5, 5, 6, 6)); pygame.draw.rect(u, (90, 60, 60) if v == 0 else (60, 70, 90), (4, 11, 8, 6))   # faded sitter
    for k in range(6): u.set_at((3 + (k * 5) % 10, 3 + (k * 7) % 14), (70, 60, 50))
    if v == 1: line(u, (14, 10, 18), (3, 3), (12, 16))                                              # slashed canvas
    return outline(u)
def bedcover():
    """yellow quilt + pillow over the bed's YYYY cells (64x32: 4x2 tiles), faded and dusty"""
    W, H = 64, 32; s = surf(W, H); u = surf(W, H); Y = [(150, 116, 46), (190, 152, 66), (220, 186, 96), (240, 214, 140)]
    pygame.draw.rect(u, Y[1], (0, 4, 64, 27), border_radius=3)
    for y in range(4, 31):
        for x in range(64):
            if u.get_at((x, y)).a:
                c = Y[1] if ((x // 8 + y // 8) % 2) else Y[2]                                      # quilt squares
                if x % 8 == 0 or y % 8 == 4: c = Y[0]
                if (x % 8, y % 8) == (4, 0): c = Y[3]
                c = lerp(c, (150, 140, 120), .2 + (BAYER[y % 4][x % 4] / 16) * .1)
                u.set_at((x, y), c)
    pygame.draw.rect(u, (222, 214, 190), (4, 1, 22, 9), border_radius=3); line(u, (246, 240, 224), (6, 2), (23, 2)); line(u, (170, 160, 140), (5, 9), (24, 9))   # pillow
    pygame.draw.rect(u, (222, 214, 190), (30, 1, 22, 9), border_radius=3); line(u, (246, 240, 224), (32, 2), (49, 2))
    line(u, Y[3], (1, 12), (62, 12)); line(u, Y[0], (0, 29), (63, 29))                               # folded hem
    pygame.draw.polygon(u, Y[0], [(46, 30), (58, 30), (63, 24), (63, 31), (44, 31)])                 # rumpled corner
    s.blit(outline(u), (0, 0)); return s
D = os.path.join(ART, "decor"); dm = json.load(open(os.path.join(D, "manifest.json")))
WP = surf(48, FACE)
for v in range(3): WP.blit(wallpaper(v), (v * 16, 0))
save("wallpaper_peeling.png", WP)
MR = surf(32, 24); MR.blit(mirror(0), (0, 0)); MR.blit(mirror(1), (16, 0)); save("mirror_tarnished.png", MR)
PF = surf(32, 20); PF.blit(frame_portrait(0), (0, 0)); PF.blit(frame_portrait(1), (16, 0)); save("frame_gilt.png", PF)
save("bed_cover_yellow.png", bedcover())
for nm in ("cobweb.png", "dust_indoor.png"): shutil.copy(os.path.join(D, nm), os.path.join(HERE, nm)); out[nm] = pygame.image.load(os.path.join(HERE, nm))
# decals off wall-post cells: north wall x3-20 -> posts x3,7,12,17,20 ; south wall x3-10 | door x11-12 | x13-20 -> posts x3,7,10,13,17,20
WPN, WPS, POSTS_N, POSTS_S = (5, 8, 18, 16), (6, 15), [3, 7, 12, 17, 20], [3, 7, 10, 13, 17, 20]   # were north 5,8,12,16 and south 6,13
assert not set(WPN + (14, 10)) & set(POSTS_N) and not set(WPS) & set(POSTS_S)
man = {"room": 40, "room_name": "Yellow Room",
 "tiles": {"yellow_floor.png": {"cell": [16, 16], "variants": 6, "maps_to": "all walkable floor cells of room 40 (replaces 'wood' floor_kind)", "rule": "variant = thash(x,y) % 6 (4,5 are dusty: weight them lower near the walls is fine)"},
           "yellow_wall_tops.png": {"cell": [16, 16], "cols": 6, "maps_to": "room 40 '#' wall tops", "layout": "same as room83_wall_tops.png"},
           "yellow_wall_fronts.png": {"cell": [16, FACE], "cols": 6, "maps_to": "room 40 front faces", "layout": "same as room83_wall_fronts.png"},
           "yellow_side_walls.png": {"cell": [8, 30], "cols": 4, "maps_to": "room 40 side faces: cols 0-1 left, 2-3 right", "layout": "same as room83_side_walls.png"}},
 "props": [
  {"file": "wallpaper_peeling.png", "name": "wallpaper_peeling", "frame_size": [16, FACE], "variants": 3, "layer": "wall decal", "placement": "wall-face (overlays the front face exactly)", "blocking": False, "footprint_tiles": None, "shadow_baked": False, "themes": ["yellow"], "max_per_room": 6, "weight": 4, "anchor": "top-left of the wall FACE"},
  {"file": "mirror_tarnished.png", "name": "mirror_tarnished", "frame_size": [16, 24], "variants": 2, "layer": "wall decal", "placement": "wall-face", "blocking": False, "footprint_tiles": None, "shadow_baked": False, "themes": ["yellow", "indoor"], "max_per_room": 1, "weight": 1, "anchor": "top-left of the wall FACE, may rise 10px above it"},
  {"file": "frame_gilt.png", "name": "frame_gilt", "frame_size": [16, 20], "variants": 2, "layer": "wall decal", "placement": "wall-face", "blocking": False, "footprint_tiles": None, "shadow_baked": False, "themes": ["yellow", "indoor"], "max_per_room": 1, "weight": 1, "anchor": "top-left of the wall FACE, may rise 6px above it"},
  {"file": "bed_cover_yellow.png", "name": "bed_cover_yellow", "frame_size": [64, 32], "variants": 1, "layer": "furniture overlay", "placement": "over the bed 'Y' cells: top-left = (5*16, 5*16) (cells x5-8, y5-6), drawn after the baked bed, before posts", "blocking": True, "footprint_tiles": [4, 2], "shadow_baked": False, "themes": ["yellow"], "max_per_room": 1, "weight": 0, "anchor": "top-left of the first Y cell"},
  {"file": "cobweb.png", "name": "cobweb", "same_as": "decor/cobweb.png", "placement": "wall-top-corner"}, {"file": "dust_indoor.png", "name": "dust", "same_as": "decor/dust_indoor.png", "placement": "floor-open"}],
 "placements_room40": {"wallpaper_peeling": "north wall faces x5,x8,x18,x16 (variants 0,1,2,0); south faces x6, x15 (variants 1,2)", "mirror_tarnished": "north face x14", "frame_gilt": "north face x10",
                       "wall_decals": [{"name": "wallpaper_peeling", "variant": v, "cell": [x, 3]} for x, v in zip(WPN, (0, 1, 2, 0))] + [{"name": "wallpaper_peeling", "variant": v, "cell": [x, 14]} for x, v in zip(WPS, (1, 2))] +
                                      [{"name": "mirror_tarnished", "variant": 0, "cell": [14, 3]}, {"name": "frame_gilt", "variant": 0, "cell": [10, 3]}],
                       "wall_post_cells": {"north_row3": POSTS_N, "south_row14": POSTS_S}, "note_39": "issue #39: no hand-placed wall decal on a post cell (posts are drawn after wall decals and cover the cell's face + 1px each side)",
                       "cobweb": "(4,4) and mirrored (19,4)", "dust": "(11,8), (17,13)", "desk": "art/drawers/yellow_room_desk_* at its manifest anchor", "light": "warm amber ambient tint (255,230,170) at ~8% optional"}}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---------- preview: room 40 baked + retiled + props, and under lighting (vignette like main.make_vig_np)
cwd = os.getcwd(); os.chdir(GAME); import main; R = main.load_rooms(); os.chdir(cwd)
import fix39  # bake with the moved wall decals
room = R[40]; g = room["grid"]
raw, TOP = art3.bake_room(40, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
def isw(x, y): return 0 <= x < 24 and 0 <= y < 18 and g[y][x] in "#="
for y in range(18):
    for x in range(24):
        if room["walk"][y][x] and g[y][x] not in "@]Y[": b.blit(FL[(x * 7 + y * 13) % 6], (x * 16, y * 16 + TOP))
for y in range(18):                                  # recolour walls: tops (raised by 8 like the game), fronts below walls facing floor
    for x in range(24):
        if isw(x, y):
            b.blit(YT[(x * 5 + y) % 6], (x * 16, y * 16 + TOP - 8))
            if y + 1 < 18 and not isw(x, y + 1): b.blit(YF[(x + y) % 6], (x * 16, y * 16 + TOP + 8))
b.blit(out["bed_cover_yellow.png"], (5 * 16, 5 * 16 + TOP - 2))
for i, x in enumerate(WPN): b.blit(WP.subsurface(((i % 3) * 16, 0, 16, FACE)), (x * 16, 3 * 16 + TOP + 8))
b.blit(MR.subsurface((0, 0, 16, 24)), (14 * 16, 3 * 16 + TOP - 2)); b.blit(PF.subsurface((0, 0, 16, 20)), (10 * 16, 3 * 16 + TOP))
cw = out["cobweb.png"].subsurface((0, 0, 16, 16)); b.blit(cw, (4 * 16, 4 * 16 + TOP)); b.blit(pygame.transform.flip(cw, True, False), (19 * 16, 4 * 16 + TOP))
du = out["dust_indoor.png"]; b.blit(du.subsurface((0, 0, 16, 16)), (11 * 16, 8 * 16 + TOP)); b.blit(du.subsurface((16, 0, 16, 16)), (17 * 16, 12 * 16 + TOP))
dmf = json.load(open(os.path.join(ART, "drawers", "manifest.json")))["pieces"]["yellow_room_desk"]; dk = pygame.image.load(os.path.join(ART, "drawers", "yellow_room_desk_closed.png"))
b.blit(dk, (15 * 16 + 32 - dmf["anchor"]["px"][0], 13 * 16 + TOP - dmf["anchor"]["px"][1]))
crop = b.subsurface((40, 40, 312, 230)).copy()
lit = crop.copy(); w, h = lit.get_size()
X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h), indexing="ij"); a = np.clip((X * X * .6 + Y * Y * .8) ** 1.4 * 200, 0, 190).astype(np.uint8)
v = pygame.Surface((w, h), pygame.SRCALPHA); v.fill((6, 4, 14, 255)); pygame.surfarray.pixels_alpha(v)[:] = a; del a
amb = pygame.Surface((w, h), pygame.SRCALPHA); amb.fill((255, 230, 170, 20)); lit.blit(amb, (0, 0)); lit.blit(v, (0, 0))
font = pygame.font.Font(None, 18); P = pygame.Surface((2 * 624 + 30, 230 * 2 + 40 + 120)); P.fill((40, 36, 48))
P.blit(font.render("Room 40 retiled + props (2x)", True, (230, 220, 200)), (10, 6)); P.blit(pygame.transform.scale(crop, (624, 460)), (10, 24))
P.blit(font.render("same under game vignette + amber ambient (2x)", True, (230, 220, 200)), (644, 6)); P.blit(pygame.transform.scale(lit, (624, 460)), (644, 24))
xx = 10
for nm in ("yellow_floor.png", "yellow_wall_tops.png", "wallpaper_peeling.png", "mirror_tarnished.png", "frame_gilt.png", "bed_cover_yellow.png"):
    im = out[nm]; P.blit(pygame.transform.scale(im, (im.get_width() * 2, im.get_height() * 2)), (xx, 500)); xx += im.get_width() * 2 + 12
pygame.image.save(P, os.path.join(HERE, "preview.png"))
dst = os.path.join(GAME, "assets", "yellow_room"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(HERE):
    if not f.startswith("preview"): shutil.copy(os.path.join(HERE, f), dst)
print("ok")
