"""Drawers (room 40 desk, room 56 ornate desk; closed/open_item/open_empty) + King's Study prop set. python3 make_study.py
Writes art/drawers and art/kings_study, copies both to game/assets. 1x RGBA, thick outline, rim light, baked contact shadows."""
import os, sys, math, random, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *
from art import lerp
DR = os.path.join(ART, "drawers"); KS = HERE; T = 16
W1 = [(46, 28, 18), (78, 50, 30), (110, 72, 42), (146, 100, 60), (186, 138, 88)]       # plain oak (matches game desk 96,62,36)
W2 = [(40, 18, 16), (70, 32, 26), (100, 50, 36), (134, 74, 50), (176, 112, 76)]        # rich mahogany for the king
GOLD = [(110, 70, 24), (176, 124, 40), (226, 176, 72), (255, 232, 150)]
PAPER = [(150, 132, 100), (196, 180, 140), (228, 216, 184), (246, 240, 220)]
SH = (10, 8, 16)
def shadow(s, cx, cy, rx, ry, a=120):
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, a))
def grain(s, r, pal, lit=.7):
    x0, y0, w, h = r
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            v = lit - (x - x0) / w * .2 - (y - y0) / max(1, h) * .15 + (BAYER[y % 4][x % 4] / 16 - .5) * .2 + (.08 if (y * 7 + x // 9) % 11 == 0 else 0)
            s.set_at((x, y), pal[max(0, min(len(pal) - 2, int(v * (len(pal) - 1))))])
def load(p): return pygame.image.load(p).convert_alpha()
ITEMS = os.path.join(ART, "items")
def desk(fw_t, fh_t, pal, state, item=None, ornate=False):
    """fw_t x fh_t footprint. Frame: footprint + 8px headroom + 6px below for the front face/legs. Anchor bottom-centre of footprint."""
    W, Hf = fw_t * T, fh_t * T; FH = Hf + 8 + 12; s = surf(W + 4, FH); ox = 2
    top = pygame.Rect(ox + 1, 6, W - 2, Hf - 10); face = pygame.Rect(ox + 1, top.bottom, W - 2, 14)
    shadow(s, ox + W / 2, Hf + 8 + 3, W / 2 + 1, 3)
    u = surf(W + 4, FH)
    grain(u, top, pal, .78); grain(u, face, pal, .5)
    line(u, pal[4], (top.left, top.top), (top.right - 1, top.top)); line(u, pal[3], (top.left, top.top + 1), (top.left, top.bottom - 1))
    line(u, pal[0], (top.left, top.bottom), (top.right - 1, top.bottom)); line(u, pal[3], (face.left, face.top + 1), (face.right - 1, face.top + 1))
    for lx in (face.left, face.right - 3):                                                       # legs / feet
        pygame.draw.rect(u, pal[1], (lx, face.bottom, 3, 4)); u.set_at((lx, face.bottom), pal[3])
    n = 3 if fw_t >= 6 else 2; dw = (face.width - 8) // n; drs = []
    for i in range(n):
        r = pygame.Rect(face.left + 4 + i * dw, face.top + 3, dw - 3, 9); drs.append(r)
        pygame.draw.rect(u, OUT, r, 1); line(u, pal[3], (r.left + 1, r.top + 1), (r.right - 2, r.top + 1))
        k = (r.centerx, r.centery); u.set_at(k, GOLD[2] if ornate else pal[4]); u.set_at((k[0] + 1, k[1]), GOLD[1] if ornate else pal[2])
    if ornate:
        line(u, GOLD[2], (top.left + 2, top.top + 2), (top.right - 3, top.top + 2)); line(u, GOLD[1], (face.left, face.top), (face.right - 1, face.top))
        for cx in (face.left + 1, face.right - 2): line(u, GOLD[2], (cx, face.top + 2), (cx, face.bottom - 2))
        for i in range(face.left + 6, face.right - 6, 6): u.set_at((i, face.bottom - 1), GOLD[1])
    s.blit(outline(u), (0, 0))
    od = drs[len(drs) // 2 if not ornate else 1]
    if state != "closed":                                                                       # drawer pulled out toward viewer
        d = pygame.Rect(od.left - 1, od.top + 1, od.width + 2, 13)
        pygame.draw.rect(s, OUT, d.inflate(2, 2)); grain(s, d, pal, .55)
        inner = d.inflate(-4, -6); inner.top = d.top + 2; pygame.draw.rect(s, (24, 14, 12), inner); line(s, pal[1], inner.topleft, inner.topright)
        line(s, pal[4], (d.left, d.top), (d.right - 1, d.top)); line(s, OUT, (d.left, d.bottom - 4), (d.right - 1, d.bottom - 4))
        s.set_at((d.centerx, d.bottom - 2), GOLD[2] if ornate else pal[4])
        if state == "open_item" and item:
            im = load(os.path.join(ITEMS, f"{item}_small.png")); s.blit(im, (d.centerx - 6, inner.bottom - 11))
    return s, (ox + W // 2, 8 + Hf - 2), FH
def scrolls(s, x, y, rnd):
    """pile of ancient scrolls and loose papers on a desk top"""
    for k in range(5):                                                    # loose sheets
        px, py = x + rnd.randrange(0, 22), y + rnd.randrange(0, 8); w, h = rnd.choice((7, 8, 9)), rnd.choice((5, 6))
        pygame.draw.rect(s, OUT, (px - 1, py - 1, w + 2, h + 2)); pygame.draw.rect(s, PAPER[1 + k % 2], (px, py, w, h)); line(s, PAPER[3], (px, py), (px + w - 1, py))
        for ly in range(py + 2, py + h - 1, 2): line(s, (110, 96, 76), (px + 1, ly), (px + w - 3, ly))
    for k in range(4):                                                    # rolled scrolls (horizontal cylinders with tied middle)
        px, py = x + 4 + rnd.randrange(0, 20), y - 2 + k * 3
        pygame.draw.rect(s, OUT, (px - 1, py - 1, 12, 5)); pygame.draw.rect(s, PAPER[2], (px, py, 10, 3)); line(s, PAPER[3], (px, py), (px + 9, py)); line(s, PAPER[0], (px, py + 2), (px + 9, py + 2))
        s.set_at((px + 5, py + 1), (150, 30, 40)); s.set_at((px + 5, py), (150, 30, 40)); s.set_at((px - 1, py + 1), PAPER[0])
    pygame.draw.rect(s, OUT, (x + 30, y + 3, 5, 6)); pygame.draw.rect(s, (30, 30, 50), (x + 31, y + 4, 3, 4)); line(s, (220, 220, 230), (x + 33, y - 1), (x + 31, y + 4))   # inkwell + quill
# ---------- (a) drawers
man_d = {"pieces": {}}
specs = [("yellow_room_desk", 40, (15, 11), 4, 2, W1, "glasses", False, "GLASSES (Eye Glasses), row 12 col 18 1-based"),
         ("kings_study_desk", 56, (9, 5), 6, 3, W2, "key", True, "KEY, row 7 col 12 1-based")]
PREV = {}
for nm, rid, (fx, fy), fw, fh, pal, item, orn, inote in specs:
    ent = {"room": rid, "glyph": "@", "footprint_tiles": [fw, fh], "footprint_cells_0based": f"x {fx}-{fx + fw - 1}, y {fy}-{fy + fh - 1}", "item": inote, "states": {}}
    for st in ("closed", "open_item", "open_empty"):
        s, anc, FH = desk(fw, fh, pal, st, item, orn)
        if orn:                                                           # the study desk carries the scroll pile (shared with kings_study)
            rnd = random.Random(56); scrolls(s, 10, 10, rnd); scrolls(s, 56, 12, rnd)
        f = f"{nm}_{st}.png"; pygame.image.save(s, os.path.join(DR, f)); ent["states"][st] = f; PREV[(nm, st)] = s
    ent.update({"frame_size": list(s.get_size()), "anchor": {"px": list(anc), "desc": f"bottom-centre of the footprint: world ({fx}*16 + {fw * 8}, ({fy}+{fh})*16) in room {rid}"},
                "depth_sort_y": f"({fy}+{fh})*16", "blocking": "all footprint cells (unchanged: '@' is solid)", "shadow_baked": True,
                "state_rules": "closed until the player LOOKs/searches the desk; then open_item while the item is there; open_empty after GET"})
    man_d["pieces"][nm] = ent
json.dump(man_d, open(os.path.join(DR, "manifest.json"), "w"), indent=2)
# ---------- (b) King's Study set
def bookshelf(v):
    W, H = 32, 40; s = surf(W, H); shadow(s, 16, 38, 15, 2.5); u = surf(W, H)
    pygame.draw.rect(u, W2[1], (1, 2, 30, 35)); line(u, W2[4], (1, 2), (30, 2)); pygame.draw.rect(u, W2[2], (0, 0, 32, 3)); line(u, GOLD[2], (2, 1), (29, 1))
    rnd = random.Random(v + 7); cols = [(150, 50, 46), (60, 90, 140), (70, 120, 70), (170, 140, 70), (110, 70, 130), (120, 90, 60)]
    for sy in (4, 15, 26):
        pygame.draw.rect(u, (26, 14, 12), (3, sy, 26, 9)); x = 3
        while x < 28:
            bw = rnd.choice((2, 2, 3)); bh = rnd.choice((6, 7, 8, 8)); c = rnd.choice(cols)
            if rnd.random() < .12: x += 2; continue                      # gap
            if rnd.random() < .1 and x < 25: pygame.draw.polygon(u, c, [(x, sy + 8), (x + 2, sy + 8), (x + 5, sy + 3), (x + 3, sy + 2)]); x += 5; continue   # leaning book
            pygame.draw.rect(u, c, (x, sy + 9 - bh, bw, bh)); u.set_at((x, sy + 9 - bh), lerp(c, (255, 240, 200), .5)); u.set_at((x, sy + 6), GOLD[1]) if bw > 2 else None
            x += bw
        pygame.draw.rect(u, W2[3], (2, sy + 9, 28, 2)); line(u, W2[4], (2, sy + 9), (29, sy + 9))
    for x in (1, 30): line(u, W2[0], (x, 3), (x, 36))
    pygame.draw.rect(u, W2[0], (1, 36, 30, 2))
    for k in range(4): u.set_at((rnd.randrange(4, 28), rnd.choice((4, 15, 26))), (190, 186, 196))   # cobweb/dust specks
    s.blit(outline(u), (0, 0)); return s
def candelabra(f):
    W, H = 16, 28; s = surf(W, H); shadow(s, 8, 26.5, 5, 1.5); u = surf(W, H)
    pygame.draw.rect(u, GOLD[1], (5, 24, 6, 2)); line(u, GOLD[3], (5, 24), (10, 24)); line(u, GOLD[1], (8, 12), (8, 24), 2); line(u, GOLD[3], (7, 13), (7, 23))
    pygame.draw.arc(u, GOLD[2], (2, 8, 12, 9), math.pi, 2 * math.pi, 2)
    for cx in (3, 8, 13):
        top = 6 if cx == 8 else 8
        pygame.draw.rect(u, (236, 228, 206), (cx - 1, top, 2, 5)); u.set_at((cx - 1, top), (255, 255, 240)); u.set_at((cx, top + 2), (200, 190, 170))
        pygame.draw.rect(u, GOLD[2], (cx - 2, top + 5, 4, 1))
    s.blit(outline(u), (0, 0))
    fl = [(255, 240, 170), (255, 186, 70), (226, 100, 34)]
    for i, cx in enumerate((3, 8, 13)):
        top = 6 if cx == 8 else 8; h = [3, 4, 3, 2][(f + i) % 4]; sw = [0, 1, 0, -1][(f + i * 2) % 4]
        for y in range(h): s.set_at((cx - (1 if y < 1 else 0) + (sw if y == h - 1 else 0), top - 1 - y), fl[min(2, y)])
    return s
def rug():
    W, H = 64, 48; s = surf(W, H); r = random.Random(3); red, red2, gold, cream = (110, 30, 42), (82, 22, 34), (190, 150, 70), (220, 206, 176)
    for y in range(3, H - 3):
        for x in range(2, W - 2):
            c = red2 if (x // 2 + y) % 4 == 0 else red
            if y in (5, H - 6) or x in (5, W - 6): c = gold
            elif y in (7, H - 8) or x in (7, W - 8): c = (40, 30, 60)
            c = lerp(c, (80, 74, 70), .12 + r.random() * .06)
            s.set_at((x, y), (*c, 255))
    for x in range(2, W - 2): s.set_at((x, H - 3), (*OUT, 220))                    # 3/4 thickness edge
    for y in range(4, H - 4, 2):
        for x, d in ((1, -1), (W - 2, 1)): s.set_at((x, y), (*gold, 255)); s.set_at((x + d, y), (*lerp(gold, (60, 50, 40), .4), 230))
    cl = surf(24, 24); import art; art.club_shape(cl, 12, 9, 4, cream); art.club_shape(cl, 12, 9, 3, cream)
    s.blit(outline(cl), (W // 2 - 12, H // 2 - 13))
    for (x, y) in ((10, 10), (W - 12, 10), (10, H - 12), (W - 12, H - 12)): pygame.draw.circle(s, gold, (x, y), 2); s.set_at((x, y), (40, 30, 60))
    return s
def banner(v):
    W, H = 16, 32; u = surf(W, H); r = random.Random(v + 9); body = [(70, 36, 96), (96, 52, 126), (130, 84, 160)] if v == 0 else [(110, 30, 42), (140, 44, 54), (172, 72, 76)]
    line(u, GOLD[3], (0, 0), (15, 0)); line(u, GOLD[1], (0, 1), (15, 1))
    tear = [26 + r.randrange(0, 5) for _ in range(12)]
    for x in range(2, 14):
        bot = min(tear[x - 2], 29 - abs(x - 8) // 2 * 0)
        for y in range(2, bot):
            c = body[1]
            if x in (2, 13): c = GOLD[1]
            elif x < 6: c = body[2] if (x + y) % 2 else body[1]
            c = lerp(c, (90, 86, 90), .25)                                       # faded
            if (x + y) % 2 == 0: c = lerp(c, (0, 0, 0), .08)
            if r.random() < .03: continue
            u.set_at((x, y), c)
    pygame.draw.polygon(u, GOLD[2], [(5, 10), (5, 7), (6, 8), (8, 6), (10, 8), (11, 7), (11, 10)]); line(u, GOLD[3], (5, 10), (11, 10))   # crown
    for y in range(13, 18): u.set_at((8, y), GOLD[1])
    return outline(u)
def parquet(v):
    s = surf(T, T); pal = [(70, 40, 26), (92, 56, 34), (112, 70, 42)]
    for y in range(T):
        for x in range(T):
            blk = ((x // 8) + (y // 8) + v) % 2; c = pal[1 + ((x if blk else y) // 2 + v) % 2]
            if (y % 8 == 0 and not blk) or (x % 8 == 0 and blk): c = pal[0]
            s.set_at((x, y), lerp(c, (0, 0, 0), BAYER[y % 4][x % 4] / 16 * .1))
    return s
files = {}
def save(nm, S): pygame.image.save(S, os.path.join(KS, nm)); files[nm] = S; return nm
save("bookshelf.png", sheet := surf(64, 40)); sheet.blit(bookshelf(0), (0, 0)); sheet.blit(bookshelf(1), (32, 0)); save("bookshelf.png", sheet)
C = surf(64, 28)
for i in range(4): C.blit(candelabra(i), (i * 16, 0))
save("candelabra.png", C); save("rug_royal.png", rug())
B = surf(32, 32); B.blit(banner(0), (0, 0)); B.blit(banner(1), (16, 0)); save("banner_royal.png", B)
PQ = surf(64, 16)
for i in range(4): PQ.blit(parquet(i), (i * 16, 0))
save("study_floor_parquet.png", PQ)
for st in ("closed", "open_item", "open_empty"): save(f"ornate_desk_scrolls_{st}.png", PREV[("kings_study_desk", st)])
man_k = {"room": 56, "room_name": "King's Study (interior x4-19, y4-13 0-based; desk '@' x9-14,y5-7; exits W y8-9, S x11-12)",
 "props": {
  "ornate_desk_scrolls_*.png": {"same_as": "drawers/kings_study_desk_* (desk piled with scrolls, quill, inkwell)", "anchor": [50, 54], "footprint_tiles": [6, 3], "blocking": True, "depth_sort_y": "(5+3)*16", "shadow_baked": True},
  "bookshelf.png": {"frame_size": [32, 40], "variants": 2, "anchor": "bottom-centre (16,39)", "footprint_tiles": [2, 1], "blocking": True, "layer": "object, depth-sorted at cell bottom", "shadow_baked": True,
                    "placement": "against the north wall, floor row y4: cells x5-6 and x16-17 (keep x11-12 clear)"},
  "candelabra.png": {"frame_size": [16, 28], "frames": 4, "fps": 6, "loop": True, "anchor": "bottom-centre (8,27)", "footprint_tiles": [1, 1], "blocking": True, "shadow_baked": True,
                     "light": "warm point light at (8,5) in the sprite (centre flame), radius ~48px; flicker intensity 0.85-1.0 synced to frame", "placement": "beside the desk: (15,6) and optionally (8,6)"},
  "rug_royal.png": {"frame_size": [64, 48], "anchor": "top-left of cell", "footprint_tiles": [4, 3], "blocking": False, "layer": "floor decal under everything",
                    "placement": "in front of the desk, cells x10-13, y9-11 (top-left (10,9)); club-suit motif echoes the courtyard rug"},
  "banner_royal.png": {"frame_size": [16, 32], "variants": 2, "anchor": "top-left of the north wall FACE at the cell", "blocking": False, "layer": "wall decal",
                       "placement": "north wall faces above x8 and x15 (purple, red); was x7 (wall post) and x16 (behind the right bookshelf), moved in #39",
                       "cells": {"purple": [8, 3], "red": [15, 3]}, "wall_post_cells_north_row3": [3, 7, 12, 17, 20], "keep_clear_x": "posts and shelf columns x5-6, x16-17"},
  "study_floor_parquet.png": {"frame_size": [16, 16], "variants": 4, "use": "optional floor for room 56 instead of plain planks: tile (x+y)%4 or thash"},
  "wall_tint": {"note": "optional: multiply room 56 wall stones by (1.05, 0.96, 0.9) for a warmer, royal feel; no extra sheet needed"}},
 "shadow_baked": True}
json.dump(man_k, open(os.path.join(KS, "manifest.json"), "w"), indent=2)
# ---------- previews: real baked rooms + props
cwd = os.getcwd(); os.chdir(GAME); import main; R = main.load_rooms(); os.chdir(cwd)
import fix39  # bake with the moved wall decals
def baked(rid):
    raw, TOP = art3.bake_room(rid, R[rid]); raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0)); return b, TOP
def put(b, TOP, spr, anchor, wx, wy): b.blit(spr, (wx - anchor[0], wy + TOP - anchor[1]))
font = pygame.font.Font(None, 18)
# room 56
b, TOP = baked(56)
for x in range(4, 20):
    for y in range(4, 14):
        if R[56]["walk"][y][x]: b.blit(PQ.subsurface((((x + y) % 4) * 16, 0, 16, 16)), (x * 16, y * 16 + TOP))
b.blit(files["rug_royal.png"], (10 * 16, 9 * 16 + TOP))
for i, x in enumerate((8, 15)): b.blit(B.subsurface((i * 16, 0, 16, 32)), (x * 16, 3 * 16 + TOP - 14 + 0))
for i, x in enumerate((5, 16)): put(b, TOP, sheet.subsurface((i * 32, 0, 32, 40)), (16, 39), x * 16 + 16, 5 * 16)
desk56 = PREV[("kings_study_desk", "open_item")]; put(b, TOP, desk56, man_d["pieces"]["kings_study_desk"]["anchor"]["px"], 9 * 16 + 48, 8 * 16)
put(b, TOP, C.subsurface((0, 0, 16, 28)), (8, 27), 15 * 16 + 8, 7 * 16)
# room 40
b40, T40 = baked(40)
put(b40, T40, PREV[("yellow_room_desk", "open_item")], man_d["pieces"]["yellow_room_desk"]["anchor"]["px"], 15 * 16 + 32, 13 * 16)
P = pygame.Surface((1180, 900)); P.fill((40, 36, 48))
P.blit(font.render("Room 56 King's Study: parquet, rug, banners, bookshelves, ornate desk (open, key), candelabra  (2x crop)", True, (230, 220, 200)), (10, 6))
P.blit(pygame.transform.scale(b.subsurface((48, 40, 288, 200)), (576, 400)), (10, 24))
P.blit(font.render("Room 40 Yellow Room: desk open with glasses (2x crop)", True, (230, 220, 200)), (600, 6))
P.blit(pygame.transform.scale(b40.subsurface((160, 120, 192, 140)), (384, 280)), (600, 24))
y = 440
for nm in ("yellow_room_desk", "kings_study_desk"):
    for k, st in enumerate(("closed", "open_item", "open_empty")):
        im = PREV[(nm, st)]; bb = pygame.Surface(im.get_size()); bb.fill((70, 44, 28)); bb.blit(im, (0, 0))
        P.blit(font.render(f"{nm} {st}", True, (230, 220, 200)), (10 + k * 390, y)); P.blit(pygame.transform.scale(bb, (im.get_width() * 3, im.get_height() * 3)), (10 + k * 390, y + 16))
    y += 200
pygame.image.save(P, os.path.join(KS, "preview.png"))
Q = pygame.Surface((420, 200)); Q.fill((40, 36, 48)); xx = 10
for nm in ("bookshelf.png", "candelabra.png", "banner_royal.png", "study_floor_parquet.png"):
    im = files[nm]; Q.blit(pygame.transform.scale(im, (im.get_width() * 2, im.get_height() * 2)), (xx if nm != "study_floor_parquet.png" else 10, 10 if nm != "study_floor_parquet.png" else 110)); xx += im.get_width() * 2 + 10
pygame.image.save(Q, os.path.join(KS, "preview_props.png"))
from PIL import Image
fr = []
for i in range(4):
    c = b.subsurface((176, 64, 120, 100)).copy(); put_ = c.blit(C.subsurface((i * 16, 0, 16, 28)), (15 * 16 + 8 - 176 - 8, 7 * 16 + TOP - 64 - 27))
    fr.append(Image.frombytes("RGB", (120, 100), pygame.image.tobytes(c, "RGB")).resize((360, 300), Image.NEAREST))
fr[0].save(os.path.join(KS, "preview_candelabra.gif"), save_all=True, append_images=fr[1:], duration=160, loop=0)
for src, dname in ((DR, "drawers"), (KS, "kings_study")):
    dst = os.path.join(GAME, "assets", dname); os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if not f.startswith("preview"): shutil.copy(os.path.join(src, f), dst)
print("ok")
