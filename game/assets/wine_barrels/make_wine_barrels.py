"""Room 68 wine barrel racks for the seven 4x2 '@' blocks (dungeon palette). python3 make_wine_barrels.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
WD = [(34, 22, 16), (56, 36, 24), (80, 54, 34), (108, 76, 48), (140, 104, 68)]   # damp cellar oak
IR = [(30, 30, 36), (54, 54, 62), (86, 86, 96), (130, 130, 140)]
WINE = (110, 20, 40); SH = (8, 6, 12)
FW, FH = 64, 52; AX, AY = 32, 50
def barrel_end(s, cx, cy, r, rnd, broken=False, tap=False):
    """barrel lying on its side, round end toward the viewer: staves, two iron hoops, bung, chalk mark"""
    pygame.draw.circle(s, OUT, (cx, cy), r + 1)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                v = .7 - (x - cx) / r * .2 - (y - cy) / r * .3 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
                c = WD[max(0, min(4, int(v * 5)))]
                if (x - cx + 40) % 4 == 0: c = WD[0]                                     # stave seams (vertical)
                s.set_at((x, y), c)
    pygame.draw.circle(s, IR[1], (cx, cy), r, 1); pygame.draw.arc(s, IR[3], (cx - r, cy - r, 2 * r + 1, 2 * r + 1), 1.8, 3.2, 1)
    pygame.draw.circle(s, IR[0], (cx, cy), r - 3, 1)
    if tap: pygame.draw.rect(s, OUT, (cx - 2, cy + r - 6, 4, 6)); pygame.draw.rect(s, IR[2], (cx - 1, cy + r - 5, 2, 4)); s.set_at((cx, cy + r - 1), WINE)
    else: pygame.draw.circle(s, WD[0], (cx + 1, cy - 1), 1)
    if rnd.random() < .5: line(s, (200, 196, 186), (cx - 3, cy + 2), (cx + 1, cy + 2)); s.set_at((cx - 1, cy + 3), (200, 196, 186))  # chalk tally
    if broken:
        pygame.draw.polygon(s, (14, 8, 10), [(cx - 2, cy - r + 2), (cx + 4, cy - r + 3), (cx + 2, cy - 2), (cx - 3, cy - 1)])
        line(s, WD[4], (cx - 2, cy - r + 2), (cx + 4, cy - r + 3))
def rack(v):
    s = surf(FW, FH); rnd = random.Random(v * 7 + 68)
    for y in range(FH - 8, FH):                                                          # baked contact shadow
        for x in range(FW):
            d = ((x - 32) / 31) ** 2 + ((y - (FH - 4)) / 4) ** 2
            if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, 130))
    u = surf(FW, FH)
    pygame.draw.rect(u, WD[1], (1, 42, 62, 6)); line(u, WD[3], (1, 42), (62, 42)); line(u, WD[0], (1, 47), (62, 47))    # cradle beam
    for x in (4, 30, 57): pygame.draw.rect(u, WD[2], (x, 36, 4, 12)); line(u, WD[4], (x, 36), (x, 47))                 # chocks
    s.blit(outline(u), (0, 0))
    r = 10
    for i, cx in enumerate((11, 32, 53)): barrel_end(s, cx, 32, r, rnd, broken=(v == 2 and i == 2), tap=(i == 1))
    tops = (21, 43) if v != 1 else (21,)
    for cx in tops: barrel_end(s, cx, 15, r, rnd)
    if v == 1:                                                                              # standing barrel instead of second top barrel
        pygame.draw.rect(s, OUT, (36, 2, 18, 22)); pygame.draw.rect(s, WD[2], (37, 6, 16, 17)); pygame.draw.ellipse(s, OUT, (36, 0, 18, 8)); pygame.draw.ellipse(s, WD[3], (37, 1, 16, 6))
        for yy in (9, 18): line(s, IR[1], (37, yy), (52, yy))
        line(s, WD[4], (38, 6), (38, 22))
    if v == 2:                                                                              # wine stain + cobweb
        for k in range(12): s.set_at((rnd.randrange(44, 62), rnd.randrange(43, 50)), (*lerp(WINE, (20, 10, 14), .4), 220))
        for k in range(6): line(s, (180, 176, 186, 150), (0, 0 + k * 0), (6 - k, k * 2))
    return s
R = [rack(v) for v in range(3)]
S = surf(FW * 3, FH)
for i, r_ in enumerate(R): S.blit(r_, (i * FW, 0))
pygame.image.save(S, os.path.join(HERE, "wine_barrels.png"))
BLOCKS = [(3, 2), (12, 2), (12, 5), (3, 8), (12, 8), (3, 11), (12, 11)]
json.dump({"room": 68, "room_name": "Royal Wine Cellar", "glyphs": "'@' 4x2 blocks (issue says 2x2/3x2; the layout has seven 4x2 blocks), top-left cells 0-based: " + str(BLOCKS),
  "sheet": {"file": "wine_barrels.png", "frame_size": [FW, FH], "variants": 3, "variant_notes": ["5 barrels (3 + 2 stacked)", "4 barrels + one standing cask on top", "broken barrel, wine stain, cobweb"]},
  "footprint_tiles": [4, 2], "anchor": {"px": [AX, AY], "desc": "bottom-centre of each 4x2 block: world (bx*16 + 32, (by+2)*16); the frame's bottom 32px covers the block, 20px headroom for the stacked barrels"},
  "placement": {f"{bx},{by}": i % 3 for i, (bx, by) in enumerate(BLOCKS)}, "blocking": "all block cells (as now)", "depth_sort_y": "(by+2)*16 per block", "shadow_baked": True,
  "notes": "draw instead of the procedural '@' table in room 68 only; dark damp oak + iron hoops (dungeon palette); FILL 'The Barrels are empty.' unchanged"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
b, TOP = baked(68)
for i, (bx, by) in enumerate(sorted(BLOCKS, key=lambda p: p[1])): b.blit(R[BLOCKS.index((bx, by)) % 3], (bx * 16 + 32 - AX, (by + 2) * 16 + TOP - AY))
dk = pygame.Surface(b.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 238))
for r_ in range(96, 0, -2): pygame.draw.circle(dk, (6, 4, 10, int(238 * min(1, (r_ / 96) ** 2.2))), (9 * 16, 7 * 16 + TOP), r_)
lit = b.copy(); lit.blit(dk, (0, 0))
P = pygame.Surface((2 * 2 * 304 + 30, 2 * 250 + 20)); P.fill((40, 36, 48))
P.blit(pygame.transform.scale(b.subsurface((0, 0, 304, 250)), (608, 500)), (10, 10)); P.blit(pygame.transform.scale(lit.subsurface((0, 0, 304, 250)), (608, 500)), (628, 10))
pygame.image.save(P, os.path.join(HERE, "preview.png")); copy_to_game(HERE, "wine_barrels"); print("ok")
