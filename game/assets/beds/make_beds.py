"""single beds in 3/4 view (decay style) + plain frames for the themed covers. python3 make_beds.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
WD = [(34, 22, 16), (58, 38, 26), (84, 56, 36), (112, 80, 52), (144, 108, 72)]
LIN = [(150, 140, 120), (186, 176, 152), (214, 206, 184), (234, 228, 210)]      # dusty linen
TICK = [(120, 112, 96), (156, 146, 124), (100, 92, 80)]                         # mattress ticking
BLANK = {"red": [(70, 24, 30), (104, 38, 44), (138, 58, 60), (170, 90, 86)], "violet": [(46, 34, 66), (72, 54, 98), (100, 80, 128), (134, 116, 160)],
         "ochre": [(80, 60, 30), (116, 88, 44), (150, 120, 62), (182, 156, 96)]}
DUST = (160, 152, 140); SH = (8, 6, 12)
def dith(u, r, pal, lit=.7, gx=.25, gy=.3):
    for y in range(r.top, r.bottom):
        for x in range(r.left, r.right):
            v = lit - (x - r.left) / max(1, r.width) * gx - (y - r.top) / max(1, r.height) * gy + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            u.set_at((x, y), pal[max(0, min(len(pal) - 1, int(v * len(pal))))])
def shadow(s, cx, cy, rx, ry):
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, 120))
def dust(s, n, box, seed):
    r = random.Random(seed)
    for k in range(n):
        x, y = r.randrange(box[0], box[2]), r.randrange(box[1], box[3]); c = s.get_at((x, y))
        if c.a == 255 and c[:3] != OUT: s.set_at((x, y), lerp(c[:3], DUST, .5))
def post(u, x, top, bot, knob=True):
    pygame.draw.rect(u, WD[2], (x, top, 4, bot - top)); line(u, WD[4], (x, top), (x, bot - 1)); line(u, WD[0], (x + 3, top), (x + 3, bot - 1))
    if knob: blob(u, x + 2, top - 1, 2.6, 2.4, WD[1:]); u.set_at((x + 1, top - 2), WD[4])
# ---------- horizontal bed: ']' head (west) + 4 body cells + '[' foot (east), 2 rows. frame 96x48, body cells at frame (16..80, 16..48)
def bed_h(blanket=None, seed=0):
    W, H = 96, 48; s = surf(W, H); u = surf(W, H); r = random.Random(seed)
    shadow(s, 50, 45, 46, 4)
    dith(u, pygame.Rect(10, 38, 78, 7), WD, .55); line(u, WD[3], (10, 38), (87, 38))                    # side rail (front face)
    for lx in (12, 82): pygame.draw.rect(u, WD[1], (lx, 44, 3, 3))                                      # feet
    dith(u, pygame.Rect(12, 16, 74, 23), TICK, .8, .1, .2)                                               # mattress top
    for x in range(14, 86, 6): line(u, TICK[2], (x, 17), (x, 37))                                         # ticking stripes (faded)
    line(u, TICK[1], (12, 16), (85, 16)); dith(u, pygame.Rect(12, 36, 74, 3), TICK, .4)                 # mattress edge
    # headboard: tall carved board at the west end, two posts
    pygame.draw.polygon(u, WD[2], [(4, 44), (4, 8), (8, 3), (12, 3), (16, 8), (16, 44)]); dith(u, pygame.Rect(5, 6, 10, 38), WD, .7)
    for y in (14, 26): line(u, WD[0], (6, y), (13, y)); line(u, WD[4], (6, y - 1), (13, y - 1))         # carved panels
    post(u, 2, 6, 46); post(u, 15, 12, 46)
    # footboard at the east end, lower
    dith(u, pygame.Rect(84, 18, 8, 26), WD, .55); line(u, WD[3], (84, 18), (91, 18)); post(u, 81, 16, 46); post(u, 91, 14, 46)
    if blanket is not None:
        B = BLANK[blanket]
        pygame.draw.rect(u, LIN[1], (17, 18, 15, 17), border_radius=4)                                  # pillow
        dith(u, pygame.Rect(18, 19, 13, 15), LIN, .8, .3, .3); line(u, LIN[3], (19, 19), (29, 19)); line(u, LIN[0], (24, 21), (25, 30))   # dent
        bl = pygame.Rect(32, 16, 50, 25)
        pts = [(32, 16), (82, 16), (82, 42), (70, 44), (58, 42), (46, 45), (34, 42)]                   # drapes over the front rail, rumpled hem
        pygame.draw.polygon(u, B[1], pts)
        for y in range(16, 46):
            for x in range(32, 83):
                if u.get_at((x, y))[:3] == B[1]:
                    w = (math.sin(x * .28 + y * .1 + seed) + .5 * math.sin(x * .11 - y * .2 + seed * 2)) * .14                      # folds
                    v = .72 + w - (y - 16) / 30 * .3 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
                    if y > 38: v -= .2                                                                # drape face is in shadow
                    u.set_at((x, y), B[max(0, min(3, int(v * 4)))])
        pygame.draw.rect(u, LIN[2], (32, 16, 6, 23)); line(u, LIN[3], (32, 16), (32, 38)); line(u, LIN[0], (37, 16), (37, 38))   # folded sheet hem
        if seed % 2: pygame.draw.polygon(u, B[0], [(66, 16), (82, 16), (82, 26)])                       # corner thrown back
        line(u, B[3], (40, 17), (80, 17))
    s.blit(outline(u), (0, 0)); dust(s, 40 if blanket else 24, (4, 8, 92, 46), seed + 3)
    for k in range(3): line(s, (196, 192, 200, 110), (2, 6), (8 - k * 2, 12 + k * 3))                     # cobweb on the headboard post
    return s
# ---------- vertical bed: '_' head (north) + 4 body rows + '^' foot (south), 2 cells wide. frame 32x112, body cells at frame (0..32, 32..96)
def bed_v(blanket=None, seed=0):
    W, H = 32, 112; s = surf(W, H); u = surf(W, H); r = random.Random(seed)
    shadow(s, 17, 108, 16, 4)
    dith(u, pygame.Rect(1, 24, 30, 74), TICK, .8, .15, .1)                                              # mattress
    for x in range(4, 30, 6): line(u, TICK[2], (x, 26), (x, 96))
    dith(u, pygame.Rect(1, 96, 30, 6), WD, .5); line(u, WD[3], (1, 96), (30, 96))                     # foot rail face
    # headboard (north) seen from the front-top: tall board 2 cells wide rising above the head cell
    pygame.draw.polygon(u, WD[2], [(0, 28), (0, 8), (6, 2), (26, 2), (32, 8), (32, 28)]); dith(u, pygame.Rect(1, 5, 30, 22), WD, .72)
    pygame.draw.rect(u, WD[1], (6, 9, 20, 12)); line(u, WD[4], (6, 9), (25, 9)); line(u, WD[0], (6, 20), (25, 20))   # carved panel
    post(u, 0, 4, 30); post(u, 28, 4, 30)
    dith(u, pygame.Rect(2, 98, 28, 10), WD, .55); line(u, WD[3], (2, 98), (29, 98)); post(u, 0, 94, 110); post(u, 28, 94, 110)   # footboard (south)
    if blanket is not None:
        B = BLANK[blanket]
        pygame.draw.rect(u, LIN[1], (4, 30, 24, 12), border_radius=4); dith(u, pygame.Rect(5, 31, 22, 10), LIN, .85, .3, .3); line(u, LIN[3], (6, 31), (25, 31))
        pygame.draw.polygon(u, B[1], [(1, 44), (31, 44), (31, 97), (20, 99), (10, 97), (1, 98)])
        for y in range(44, 100):
            for x in range(1, 32):
                if u.get_at((x, y))[:3] == B[1]:
                    w = (math.sin(y * .26 + x * .1 + seed) + .5 * math.sin(y * .1 - x * .22 + seed * 2)) * .14
                    v = .72 + w - (x - 1) / 30 * .25 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
                    u.set_at((x, y), B[max(0, min(3, int(v * 4)))])
        pygame.draw.rect(u, LIN[2], (1, 44, 30, 5)); line(u, LIN[3], (1, 44), (30, 44)); line(u, LIN[0], (1, 48), (30, 48))
        if seed % 2: pygame.draw.polygon(u, B[0], [(18, 90), (31, 80), (31, 97)])
    s.blit(outline(u), (0, 0)); dust(s, 40 if blanket else 24, (1, 4, 31, 108), seed + 5)
    return s
def strip(fr):
    w, h = fr[0].get_size(); S = surf(w * len(fr), h)
    for i, f in enumerate(fr): S.blit(f, (i * w, 0))
    return S
OUTF = {}
def save(n, S): pygame.image.save(S, os.path.join(HERE, n)); OUTF[n] = S; return S
BH = save("bed_single_h.png", strip([bed_h("red", 0), bed_h("violet", 1), bed_h("ochre", 2)]))
FH_ = save("bed_frame_h.png", bed_h(None, 4)); BV = save("bed_single_v.png", strip([bed_v("red", 0), bed_v("violet", 1)])); FV = save("bed_frame_v.png", bed_v(None, 4))
json.dump({"issue": 34,
  "bed_single_h.png": {"frame_size": [96, 48], "variants": {"0": "faded madder red", "1": "dusty violet", "2": "dusty ochre"}, "glyphs": "']' head (west) + 'W' x4 + '[' foot (east), 2 rows = 6x2 block",
     "anchor": {"px": [48, 47], "desc": "bottom-centre of the 6x2 block: world ((x0+3)*16, (y0+2)*16), x0 = column of ']', y0 = top row"}, "body_cells_in_frame": [16, 16, 64, 32],
     "footprint_tiles": [6, 2], "blocking": "all block cells (as now)", "depth_sort_y": "(y0+2)*16", "shadow_baked": True},
  "bed_frame_h.png": {"frame_size": [96, 48], "same_anchor_as": "bed_single_h.png", "desc": "plain frame with a bare ticking mattress; the themed covers (64x32, rooms 39/40) sit exactly on the body cells (frame px 16,16), drawn after the frame"},
  "bed_single_v.png": {"frame_size": [32, 112], "variants": {"0": "faded red", "1": "dusty violet"}, "glyphs": "'_' head (north) + 'W' x4 rows + '^' foot (south), 2 cells wide = 2x6 block",
     "anchor": {"px": [16, 111], "desc": "bottom-centre of the 2x6 block: world ((x0+1)*16, (y0+6)*16), x0 = left column, y0 = row of '_'"}, "body_cells_in_frame": [0, 32, 32, 64],
     "footprint_tiles": [2, 6], "blocking": "all block cells", "depth_sort_y": "(y0+6)*16", "shadow_baked": True, "note": "headboard rises 16 px above the '_' row"},
  "bed_frame_v.png": {"frame_size": [32, 112], "same_anchor_as": "bed_single_v.png", "desc": "plain frame for the 32x64 vertical covers (rooms 37/38) at frame px (0,32)"},
  "placements": {"room 10 (Chef's Quarters)": {"file": "bed_single_h.png", "variant": 2, "block": "x6-11, y1-2", "world_anchor": [144, 48]},
                 "room 67 (Sorcerer's Quarters)": [{"file": "bed_single_h.png", "variant": 1, "block": "x6-11, y5-6", "world_anchor": [144, 112]}, {"file": "bed_single_h.png", "variant": 1, "block": "x6-11, y11-12", "world_anchor": [144, 208]}],
                 "rooms 39/40": {"file": "bed_frame_h.png", "block": "x4-9, y5-6", "world_anchor": [112, 112], "then": "existing bed_cover at (5*16, 5*16)"},
                 "rooms 37/38": [{"file": "bed_frame_v.png", "block": "x6-7, y7-12", "world_anchor": [112, 208]}, {"file": "bed_frame_v.png", "block": "x16-17, y7-12", "world_anchor": [272, 208]}],
                 "anywhere else": "any ']W..W[' 6x2 block -> bed_single_h (pick variant by room colour); any '_ W W ^' 2x6 block -> bed_single_v"},
  "integration_notes": "replace the procedural W/[/] draw (art3 furniture pass) with these sprites, depth-sorted; keep blocking. In 37/38 the '_' and '^' cells are currently remapped to '%' tables: treat them as bed head/foot instead"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# preview: before/after on rooms 10, 67, 40, 37
def fr(S, i, w): return S.subsurface((i * w, 0, w, S.get_height()))
def room_after(rid, items):
    b, TOP = baked(rid); a = b.copy()
    for img, ax, ay in items: a.blit(img, (ax - img.get_width() // 2, ay - img.get_height() + TOP))
    return b, a
cov = lambda p: pygame.image.load(os.path.join(GAME, "assets", p))
fh_cov = FH_.copy(); fh_cov.blit(cov("yellow_room/bed_cover_yellow.png"), (16, 14))
fv_cov = FV.copy(); fv_cov.blit(cov("red_room/bed_cover_red.png"), (0, 30))
sets = [(10, [(fr(BH, 2, 96), 144, 48)], (40, 0, 200, 80)), (67, [(fr(BH, 1, 96), 144, 112), (fr(BH, 1, 96), 144, 208)], (72, 56, 160, 180)),
        (40, [(fh_cov, 112, 112)], (40, 64, 160, 80)), (37, [(fv_cov, 112, 208), (fv_cov, 272, 208)], (80, 120, 220, 120))]
rows = []
for rid, it, crop in sets:
    b, a = room_after(rid, it); c = pygame.Rect(crop); rows.append((pygame.transform.scale(b.subsurface(c), (c.w * 2, c.h * 2)), pygame.transform.scale(a.subsurface(c), (c.w * 2, c.h * 2))))
Wd = max(r[0].get_width() for r in rows) * 2 + 30; Ht = sum(r[0].get_height() for r in rows) + 10 * (len(rows) + 1)
P = pygame.Surface((Wd, Ht)); P.fill((40, 36, 48)); y = 10
for bb, aa in rows: P.blit(bb, (10, y)); P.blit(aa, (20 + bb.get_width(), y)); y += bb.get_height() + 10
pygame.image.save(P, os.path.join(HERE, "preview.png"))
S = pygame.Surface((96 * 3 + 36 * 4 + 40, 112 + 60 + 20)); S.fill((96, 70, 52))
for i in range(3): S.blit(fr(BH, i, 96), (10 + i * 100, 10))
S.blit(FH_, (10, 64)); S.blit(fh_cov, (110, 64))
for i, im in enumerate((fr(BV, 0, 32), fr(BV, 1, 32), FV, fv_cov)): S.blit(im, (320 + i * 36, 10))
pygame.image.save(pygame.transform.scale(S, (S.get_width() * 3, S.get_height() * 3)), os.path.join(HERE, "preview_sprites.png"))
copy_to_game(HERE, "beds"); print("ok")
