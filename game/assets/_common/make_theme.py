"""Red/Blue/Purple room themes (rooms 37/38/39), modelled on yellow_room/make_yellow.py. python3 make_theme.py red 37 | blue 38 | purple 39"""
import os, sys, math, random, json, shutil
ART = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME, RID = sys.argv[1], int(sys.argv[2]); HERE = os.path.join(ART, NAME + "_room"); os.makedirs(HERE, exist_ok=True); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *
from art import lerp
import numpy as np
src = open(os.path.join(ART, "tiles", "make_tiles.py")).read()                     # reuse the wall-sheet drawers verbatim (same layout as room83)
exec(src[src.index("T = 16; SIDE"):src.index("def dirt(")])
from art3 import FACE
CFG = {"red": dict(key=(176, 44, 50), amb=(255, 190, 180), beds=[(6, 8), (16, 8)], vert=True),
       "blue": dict(key=(56, 86, 176), amb=(180, 200, 255), beds=[(6, 8), (16, 8)], vert=True),
       "purple": dict(key=(120, 60, 160), amb=(220, 190, 255), beds=[(5, 5)], vert=False)}[NAME]
K = CFG["key"]; GR = (120, 114, 110)
def sh(t, fade=.22): return tuple(int(c) for c in lerp(lerp((0, 0, 0), K, t) if t <= 1 else lerp(K, (255, 245, 235), t - 1), GR, fade))
T = 16
OCHRE = [sh(1.0, .25), sh(1.12, .25), sh(.9, .25), sh(1.25, .25), sh(.95, .4)]          # faded yellow stone for walls
def floor_tile(v):
    """worn glazed ochre tiles (8x8 quarter tiles), grout, chips, dust bloom"""
    r = random.Random(v * 13 + 1); s = surf(T, T); pal = [sh(.5), sh(.62), sh(.74), sh(.86), sh(1.05)]
    for y in range(T):
        for x in range(T):
            q = v % 2; lx, ly = x, y
            l = .62 - lx / 16 * .15 - ly / 16 * .2 + q * .06 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
            c = pal[max(0, min(4, int(l * 5)))]
            if lx == 0 or ly == 0: c = sh(.42)                                       # grout
            elif lx == 1 and ly < 15 or ly == 1 and lx < 15: c = lerp(c, (240, 220, 160), .3)   # rim highlight
            s.set_at((x, y), lerp(c, (120, 112, 100), .18))                               # faded
    for k in range(v % 3 + 1):                                                            # chips + cracks
        x, y = r.randrange(2, 14), r.randrange(2, 14); s.set_at((x, y), sh(.25)); s.set_at((x + 1, y), pal[4]) if x < 15 else None
    if v in (2, 5):
        for i in range(5): s.set_at((3 + i, 5 + (i * 7) % 4), sh(.3))
    if v >= 4:                                                                             # dusty
        for y in range(T):
            for x in range(T):
                if BAYER[y % 4][x % 4] / 16 < .18 and r.random() < .6: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (180, 170, 150), .5))
    return s
def sheet(tiles, w, h, cols):
    rows = (len(tiles) + cols - 1) // cols; S = surf(w * cols, h * rows)
    for i, t in enumerate(tiles): S.blit(t, ((i % cols) * w, (i // cols) * h))
    return S
rnd = random.Random(RID); out = {}
def save(n, S): pygame.image.save(S, os.path.join(HERE, n)); out[n] = S; return n
FL = [floor_tile(v) for v in range(6)]; save(NAME + "_floor.png", sheet(FL, T, T, 6))
tones = OCHRE
YT = [wall_top(rnd, tones) for _ in range(6)]; YF = [wall_front(rnd, tones) for _ in range(6)]
YS = [side_face(rnd, "left", tones) for _ in range(2)] + [side_face(rnd, "right", tones) for _ in range(2)]
save(NAME + "_wall_tops.png", sheet(YT, T, T, 6)); save(NAME + "_wall_fronts.png", sheet(YF, T, FACE, 6)); save(NAME + "_side_walls.png", sheet(YS, SIDE, T + FACE, 4))
# ---------- decor
def wallpaper(v):
    """peeling faded yellow damask wallpaper over the wall face (16x14), curled strip, bare plaster behind"""
    s = surf(T, FACE); r = random.Random(v + 3); base = sh(.95, .3); dark = sh(.72, .3); plaster = (150, 140, 120)
    peel = 6 + v * 3
    for y in range(FACE):
        for x in range(T):
            if x >= peel and y > 3 + (x - peel) // 2: c = plaster if (x + y) % 3 else (130, 120, 104)   # bare plaster
            else:
                c = base if ((x // 2 + y // 3) % 3) else dark                                          # damask stripe
                if (x % 6 == 3 and y % 5 == 2): c = sh(1.2, .3)
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
def bedcover_v():
    """vertical quilt + one pillow at the head (32x64: 2x4 tiles), faded and dusty"""
    return pygame.transform.rotate(bedcover_h_raw(True), 0)
def bedcover():
    """yellow quilt + pillow over the bed's YYYY cells (64x32: 4x2 tiles), faded and dusty"""
    W, H = 64, 32; s = surf(W, H); u = surf(W, H); Y = [sh(.6, .15), sh(.85, .15), sh(1.0, .15), sh(1.3, .15)]
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
def bedcover_h_raw(vert):
    W, H = (32, 64) if vert else (64, 32); s = surf(W, H); u = surf(W, H); Y = [sh(.6, .15), sh(.85, .15), sh(1.0, .15), sh(1.3, .15)]
    pygame.draw.rect(u, Y[1], (0, 10, W, H - 11), border_radius=3)
    for y in range(10, H - 1):
        for x in range(W):
            if u.get_at((x, y)).a:
                c = Y[1] if ((x // 8 + y // 8) % 2) else Y[2]
                if x % 8 == 0 or y % 8 == 4: c = Y[0]
                if (x % 8, y % 8) == (4, 0): c = Y[3]
                u.set_at((x, y), lerp(c, (150, 140, 120), .2 + (BAYER[y % 4][x % 4] / 16) * .1))
    pygame.draw.rect(u, (222, 214, 190), (4, 1, 24, 10), border_radius=3); line(u, (246, 240, 224), (6, 2), (25, 2)); line(u, (170, 160, 140), (5, 10), (26, 10))
    line(u, Y[3], (1, 18), (W - 2, 18)); line(u, Y[0], (0, H - 3), (W - 1, H - 3))
    pygame.draw.polygon(u, Y[0], [(18, H - 2), (W - 1, H - 12), (W - 1, H - 1), (16, H - 1)])
    s.blit(outline(u), (0, 0)); return s
D = os.path.join(ART, "decor"); dm = json.load(open(os.path.join(D, "manifest.json")))
WP = surf(48, FACE)
for v in range(3): WP.blit(wallpaper(v), (v * 16, 0))
save("wallpaper_peeling.png", WP)
MR = surf(32, 24); MR.blit(mirror(0), (0, 0)); MR.blit(mirror(1), (16, 0)); save("mirror_tarnished.png", MR)
PF = surf(32, 20); PF.blit(frame_portrait(0), (0, 0)); PF.blit(frame_portrait(1), (16, 0)); save("frame_gilt.png", PF)
BC = bedcover_h_raw(True) if CFG["vert"] else bedcover(); save(f"bed_cover_{NAME}.png", BC)
for nm in ("cobweb.png", "dust_indoor.png"): shutil.copy(os.path.join(D, nm), os.path.join(HERE, nm)); out[nm] = pygame.image.load(os.path.join(HERE, nm))
BEDS = CFG["beds"]; BW, BH = BC.get_size()
TH = NAME.capitalize() + " Room"
# hand-placed north-face decals kept off wall-post cells (art3 pillar pass: corners/ends + x%5==2 on straight runs).
# 37/38 north wall x3-10 | door x11-12 | x13-20 -> posts x3,7,10,13,17,20 ; 39 north wall x3-20 -> posts x3,7,12,17,20
POSTS = {37: [3, 7, 10, 13, 17, 20], 38: [3, 7, 10, 13, 17, 20], 39: [3, 7, 12, 17, 20]}[RID]
WPX = (5, 8, 18, 16)            # was 5,8,12,16: x12 is the door gap in 37/38 and a post in 39 -> x18
FRX = 9 if RID in (37, 38) else 10   # was 10: x10 is the door-end post in 37/38 -> x9
MRX = 14
assert not set(WPX + (FRX, MRX)) & set(POSTS)
man = {"room": RID, "room_name": TH,
 "tiles": {NAME + "_floor.png": {"cell": [16, 16], "variants": 6, "maps_to": f"all walkable floor cells of room {RID} (replaces 'wood' floor_kind; drop the theme 'tint' once used)", "rule": "variant = thash(x,y) % 6 (4,5 dusty)"},
           NAME + "_wall_tops.png": {"cell": [16, 16], "cols": 6, "maps_to": f"room {RID} '#' wall tops", "layout": "same as room83_wall_tops.png"},
           NAME + "_wall_fronts.png": {"cell": [16, FACE], "cols": 6, "maps_to": f"room {RID} front faces", "layout": "same as room83_wall_fronts.png"},
           NAME + "_side_walls.png": {"cell": [8, 30], "cols": 4, "maps_to": f"room {RID} side faces: cols 0-1 left, 2-3 right", "layout": "same as room83_side_walls.png"}},
 "props": [
  {"file": "wallpaper_peeling.png", "name": "wallpaper_peeling", "frame_size": [16, FACE], "variants": 3, "layer": "wall decal", "placement": "wall-face (overlays the front face exactly)", "blocking": False, "shadow_baked": False, "themes": [NAME], "anchor": "top-left of the wall FACE"},
  {"file": "mirror_tarnished.png", "name": "mirror_tarnished", "frame_size": [16, 24], "variants": 2, "layer": "wall decal", "placement": "wall-face", "blocking": False, "shadow_baked": False, "themes": [NAME], "anchor": "top-left of the wall FACE, may rise 10px above it"},
  {"file": "frame_gilt.png", "name": "frame_gilt", "frame_size": [16, 20], "variants": 2, "layer": "wall decal", "placement": "wall-face", "blocking": False, "shadow_baked": False, "themes": [NAME], "anchor": "top-left of the wall FACE, may rise 6px above it"},
  {"file": f"bed_cover_{NAME}.png", "name": f"bed_cover_{NAME}", "frame_size": [BW, BH], "variants": 1, "layer": "furniture overlay",
   "placement": "over each bed's body cells, top-left px = " + ", ".join(f"({bx*16},{by*16}) (cells x{bx}-{bx+BW//16-1}, y{by}-{by+BH//16-1})" for bx, by in BEDS) + "; drawn after the baked bed, before posts; pillow end = head ('_' / ']' side)",
   "blocking": True, "footprint_tiles": [BW // 16, BH // 16], "shadow_baked": False, "anchor": "top-left of the bed's first body cell"},
  {"file": "cobweb.png", "name": "cobweb", "same_as": "decor/cobweb.png", "placement": "wall-top-corner"}, {"file": "dust_indoor.png", "name": "dust", "same_as": "decor/dust_indoor.png", "placement": "floor-open"}],
 f"placements_room{RID}": {"wallpaper_peeling": f"north wall faces x{WPX[0]},x{WPX[1]},x{WPX[2]},x{WPX[3]} (variants 0,1,2,0)", "mirror_tarnished": f"north face x{MRX}", "frame_gilt": f"north face x{FRX}",
   "wall_decals": [{"name": "wallpaper_peeling", "variant": v, "cell": [x, 3]} for x, v in zip(WPX, (0, 1, 2, 0))] + [{"name": "mirror_tarnished", "variant": 0, "cell": [MRX, 3]}, {"name": "frame_gilt", "variant": 0, "cell": [FRX, 3]}],
   "wall_post_cells_north_row3": POSTS, "note_39": "issue #39: no hand-placed wall decal on a post cell (posts are drawn after wall decals and cover the cell's face + 1px each side)",
   "cobweb": "(4,4) and mirrored (19,4)", "dust": "(11,9), (17,13)", "light": f"optional ambient tint {list(CFG['amb'])} at ~8%"}}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---------- preview: room 40 baked + retiled + props, and under lighting (vignette like main.make_vig_np)
cwd = os.getcwd(); os.chdir(GAME); import main; R = main.load_rooms(); os.chdir(cwd)
import fix39  # bake with the moved wall decals
room = R[RID]; g = room["grid"]
raw, TOP = art3.bake_room(RID, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
def isw(x, y): return 0 <= x < 24 and 0 <= y < 18 and g[y][x] in "#="
for y in range(18):
    for x in range(24):
        if room["walk"][y][x] and g[y][x] not in "@]Y[_^RNPW": b.blit(FL[(x * 7 + y * 13) % 6], (x * 16, y * 16 + TOP))
for y in range(18):                                  # recolour walls: tops (raised by 8 like the game), fronts below walls facing floor
    for x in range(24):
        if isw(x, y):
            b.blit(YT[(x * 5 + y) % 6], (x * 16, y * 16 + TOP - 8))
            if y + 1 < 18 and not isw(x, y + 1): b.blit(YF[(x + y) % 6], (x * 16, y * 16 + TOP + 8))
[b.blit(BC, (bx * 16, by * 16 + TOP - 2)) for bx, by in BEDS]
for i, x in enumerate(WPX): b.blit(WP.subsurface(((i % 3) * 16, 0, 16, FACE)), (x * 16, 3 * 16 + TOP + 8))
b.blit(MR.subsurface((0, 0, 16, 24)), (MRX * 16, 3 * 16 + TOP - 2)); b.blit(PF.subsurface((0, 0, 16, 20)), (FRX * 16, 3 * 16 + TOP))
cw = out["cobweb.png"].subsurface((0, 0, 16, 16)); b.blit(cw, (4 * 16, 4 * 16 + TOP)); b.blit(pygame.transform.flip(cw, True, False), (19 * 16, 4 * 16 + TOP))
du = out["dust_indoor.png"]; b.blit(du.subsurface((0, 0, 16, 16)), (11 * 16, 9 * 16 + TOP)); b.blit(du.subsurface((16, 0, 16, 16)), (17 * 16, 12 * 16 + TOP))
crop = b.subsurface((40, 40, 312, 230)).copy()
lit = crop.copy(); w, h = lit.get_size()
X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h), indexing="ij"); a = np.clip((X * X * .6 + Y * Y * .8) ** 1.4 * 200, 0, 190).astype(np.uint8)
v = pygame.Surface((w, h), pygame.SRCALPHA); v.fill((6, 4, 14, 255)); pygame.surfarray.pixels_alpha(v)[:] = a; del a
amb = pygame.Surface((w, h), pygame.SRCALPHA); amb.fill((*CFG["amb"], 20)); lit.blit(amb, (0, 0)); lit.blit(v, (0, 0))
font = pygame.font.Font(None, 18); P = pygame.Surface((2 * 624 + 30, 230 * 2 + 40 + 120)); P.fill((40, 36, 48))
P.blit(font.render(f"Room {RID} retiled + props (2x)", True, (230, 220, 200)), (10, 6)); P.blit(pygame.transform.scale(crop, (624, 460)), (10, 24))
P.blit(font.render("same under game vignette + tinted ambient (2x)", True, (230, 220, 200)), (644, 6)); P.blit(pygame.transform.scale(lit, (624, 460)), (644, 24))
xx = 10
for nm in (NAME + "_floor.png", NAME + "_wall_tops.png", "wallpaper_peeling.png", "mirror_tarnished.png", "frame_gilt.png", f"bed_cover_{NAME}.png"):
    im = out[nm]; P.blit(pygame.transform.scale(im, (im.get_width() * 2, im.get_height() * 2)), (xx, 500)); xx += im.get_width() * 2 + 12
pygame.image.save(P, os.path.join(HERE, "preview.png"))
dst = os.path.join(GAME, "assets", NAME + "_room"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(HERE):
    if not f.startswith("preview"): shutil.copy(os.path.join(HERE, f), dst)
print("ok")
