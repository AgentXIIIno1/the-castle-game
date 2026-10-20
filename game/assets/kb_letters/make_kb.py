"""room 74: 'KB' carved into the top of the sealed wall block (cells (8,10) K and (9,10) B). Dungeon palette. python3 make_kb.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
K = ["................",
     "................",
     "...##.....##....",
     "...##....##.....",
     "...##...##......",
     "...##..##.......",
     "...##.##........",
     "...####.........",
     "...####.........",
     "...##.##........",
     "...##..##.......",
     "...##...##......",
     "...##....##.....",
     "...##.....##....",
     "................",
     "................"]
B = ["................",
     "................",
     "...######.......",
     "...##...##......",
     "...##....##.....",
     "...##....##.....",
     "...##...##......",
     "...#######......",
     "...##....##.....",
     "...##.....##....",
     "...##.....##....",
     "...##....##.....",
     "...########.....",
     "................",
     "................",
     "................"]
B = B[1:] + B[:1]                                                           # same baseline as K (rows 2-13)
SHADOW = (12, 9, 16); DEEP = (26, 22, 32); FLOOR_G = (44, 40, 48); LIP = (176, 170, 184); MOSS = [(52, 66, 46), (70, 84, 66)]; DUST = (104, 98, 92)
def carve(bm, seed):
    r = random.Random(seed); s = surf(16, 16)
    G = lambda x, y: 0 <= x < 16 and 0 <= y < 16 and bm[y][x] == "#"
    for y in range(16):
        for x in range(16):
            if G(x, y):
                if not G(x, y - 1) or not G(x - 1, y): c = SHADOW                 # upper/left inner wall: in shadow
                elif not G(x, y + 1) or not G(x + 1, y): c = FLOOR_G              # groove floor catching a little light
                else: c = DEEP
                s.set_at((x, y), (*c, 255))
            else:
                if G(x, y - 1) or G(x - 1, y): s.set_at((x, y), (*LIP, 120 if G(x, y - 1) else 80))    # lit lower/right lip
                elif G(x, y + 1) and BAYER[y % 4][x % 4] < 8: s.set_at((x, y), (*SHADOW, 70))         # soft upper rim shade
    groove = [(x, y) for y in range(16) for x in range(16) if G(x, y)]
    for k in range(3):                                                          # chips: notches broken out of the lip
        x, y = r.choice(groove)
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            if not G(x + dx, y + dy) and 0 <= x + dx < 16 and 0 <= y + dy < 16: s.set_at((x + dx, y + dy), (*DEEP, 230)); break
    for k in range(5):                                                          # moss / dust settled in the grooves
        x, y = r.choice(groove)
        if not G(x, y + 1) or k % 2: s.set_at((x, y), (*(MOSS[k % 2] if k < 3 else DUST), 255))
    for k in range(4):                                                          # stray scratches
        x, y = r.randrange(1, 15), r.randrange(1, 15)
        if not G(x, y) and s.get_at((x, y)).a == 0: s.set_at((x, y), (*SHADOW, 90))
    return s
def panel():
    """dressed-stone face (32x16) chiselled smooth across both cells so the letters read on the busy brick tops; bevelled, cracked, worn"""
    P = surf(32, 16); r = random.Random(74); PAL = [(70, 66, 78), (86, 82, 94), (100, 96, 108), (116, 112, 122)]
    for y in range(1, 16):
        for x in range(1, 31):
            v = .62 - x / 32 * .15 - y / 16 * .2 + (BAYER[y % 4][x % 4] / 16 - .5) * .25
            P.set_at((x, y), (*PAL[max(0, min(3, int(v * 4)))], 255))
    line(P, (150, 146, 158), (1, 1), (30, 1)); line(P, (136, 132, 144), (1, 1), (1, 15))                 # lit bevel (top/left)
    line(P, (40, 36, 46), (31, 1), (31, 15)); line(P, (40, 36, 46), (1, 15), (31, 15) if False else (30, 15))   # shadow bevel
    for (x0, y0, x1, y1) in ((26, 1, 29, 5), (2, 12, 4, 15)): line(P, (36, 32, 42), (x0, y0), (x1, y1))     # cracks
    for k in range(10): x, y = r.randrange(2, 30), r.randrange(2, 15); P.set_at((x, y), (*DUST, 255))
    for (x, y) in ((1, 1), (30, 1), (1, 15), (31, 14)): P.set_at((x, y), (0, 0, 0, 0))                        # chipped corners
    for k in range(4): P.set_at((r.randrange(1, 31), 15), (*MOSS[k % 2], 255))
    return P
PN = panel()
KS, BS = carve(K, 1), carve(B, 2)
_k = PN.subsurface((0, 0, 16, 16)).copy(); _k.blit(KS, (0, 0)); KS = _k
_b = PN.subsurface((16, 0, 16, 16)).copy(); _b.blit(BS, (0, 0)); BS = _b
pygame.image.save(KS, os.path.join(HERE, "kb_letter_K.png")); pygame.image.save(BS, os.path.join(HERE, "kb_letter_B.png"))
W = surf(32, 16); W.blit(KS, (0, 0)); W.blit(BS, (16, 0)); pygame.image.save(W, os.path.join(HERE, "kb_word.png"))
json.dump({"issue": 6, "room": 74,
  "glyph_cells_0based": {"K": [8, 10], "B": [9, 10]},
  "where": "both cells sit inside the sealed wall block x7-10, y9-11 (the '&' cells become '#'), so only the TOP of the block shows: the letters are carved into the wall-top surface, read from above",
  "files": {"kb_letter_K.png": {"size": [16, 16], "cell": [8, 10]}, "kb_letter_B.png": {"size": [16, 16], "cell": [9, 10]},
            "kb_word.png": {"size": [32, 16], "cells": "x8-9, y10", "note": "K + B in one image; same as drawing the two letters separately"}},
  "anchor": "top-left of the cell's raised wall top: (x*16, y*16 + TOP - 8), the same RAISE=8 as the wall-top pass. Whole word: (8*16, 10*16 + TOP - 8) = (128, 152 + TOP)",
  "layer": "wall-top decal (each letter carries its half of a smoothed, bevelled stone panel so it reads on the brick pattern): blit onto the baked wall top after the wall-top pass and before the front faces of the row below (row 11 is also wall, so nothing overlaps). Alpha overlay: opaque groove pixels, translucent lit lip",
  "blocking": "not blocking itself; the cells stay solid as wall (unchanged)",
  "integration_notes": "draw the K/B cells as normal wall tops (as they are now via enclosed_furniture + the '#' wall pass) and blit these decals on top; no FURN remap needed for 74",
  "lighting": "no glow; it shows under the lamp like the rest of the wall"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# preview: before/after on baked room 74, plain and under dungeon darkness with the lamp at (12,10)
b, TOP = baked(74); a = b.copy(); a.blit(W, (8 * 16, 10 * 16 + TOP - 8))
def dark(s, cx, cy, rr=72):
    o = s.copy(); dk = pygame.Surface(s.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 238))
    for r_ in range(rr, 0, -2): pygame.draw.circle(dk, (4, 3, 10, int(238 * (r_ / rr) ** 2.2)), (cx, cy), r_)
    o.blit(dk, (0, 0)); return o
L = (12 * 16 + 8, 10 * 16 + TOP + 8)
crop = pygame.Rect(72, 9 * 16 + TOP - 40, 136, 88)
tiles = [b, a, dark(b, *L), dark(a, *L)]
P = pygame.Surface((crop.w * 3 * 2 + 30, crop.h * 3 * 2 + 30)); P.fill((40, 36, 48))
for i, t in enumerate(tiles): P.blit(pygame.transform.scale(t.subsurface(crop), (crop.w * 3, crop.h * 3)), (10 + (i % 2) * (crop.w * 3 + 10), 10 + (i // 2) * (crop.h * 3 + 10)))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
Z = pygame.Surface((32, 16)); Z.blit(b, (0, 0), (8 * 16, 10 * 16 + TOP - 8, 32, 16)); Z.blit(W, (0, 0))
pygame.image.save(pygame.transform.scale(Z, (320, 160)), os.path.join(HERE, "preview_zoom.png"))
copy_to_game(HERE, "kb_letters"); print("ok")
