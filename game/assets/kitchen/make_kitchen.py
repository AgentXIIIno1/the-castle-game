"""room 9 Kitchen: stone table (replaces the wood '%' table) + kitchen dressing. python3 make_kitchen.py"""
import os, sys, math, random, json, shutil, copy
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from art import lerp
from collections import deque
T = 16
SL = [(40, 36, 42), (62, 57, 60), (86, 80, 80), (110, 103, 99), (136, 128, 120), (166, 158, 146), (196, 188, 172)]   # worn limestone
SB = [(22, 18, 24), (38, 34, 42), (56, 52, 60), (78, 74, 84), (100, 96, 106), (130, 124, 134)]                   # hearth fieldstone
WD = [(36, 24, 20), (60, 40, 30), (86, 60, 42), (114, 84, 58), (146, 112, 78)]
IR = [(26, 26, 32), (46, 46, 54), (74, 74, 86), (112, 112, 126), (160, 158, 170)]
CU = [(70, 34, 22), (120, 62, 34), (170, 98, 52), (214, 146, 86)]                                                  # copper
FL = [(160, 50, 24), (220, 110, 36), (252, 176, 64), (255, 236, 160)]
SOOT = (14, 10, 12); SH = (8, 6, 12)
def P(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height(): s.set_at((int(x), int(y)), c)
def shadow(s, cx, cy, rx, ry, a=120):
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, a))
def stonefill(u, rect, pal, lit, r, blocky=True, grad=.3):
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            v = lit - (y - y0) / max(1, h) * grad + (BAYER[y % 4][x % 4] / 16 - .5) * .14 + ((thash(x // 7, y // 5) % 5) - 2) * .02 * blocky
            P(u, x, y, pal[max(0, min(len(pal) - 1, int(v * len(pal))))])
def thash(x, y): return (x * 73856093 ^ y * 19349663) & 0xffff
def ellipse(u, cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: P(u, x, y, c)

# ---------- stone table: 9x2 cells (x8-16, y8-9), 144x46, anchor bottom-centre (72,45) ----------
def stone_table():
    W, H = 144, 46; s = surf(W, H); u = surf(W, H); r = random.Random(9)
    shadow(s, 72, 42, 72, 5, 110)
    for x0 in (12, 64, 116):                                  # three squat stone trestles
        stonefill(u, (x0, 30, 16, 14), SL, .55, r, grad=.35)
        for y in range(30, 44): P(u, x0, y, SL[3]); P(u, x0 + 15, y, SL[1])
        for x in range(x0, x0 + 16): P(u, x, 43, SL[1])
    stonefill(u, (1, 4, W - 2, 25), SL, .7, r, grad=.18)     # slab top
    for x in range(1, W - 1):                                 # slab front edge (8px) + lit nosing
        for y in range(29, 37): P(u, x, y, SL[2] if y < 33 else SL[1]) if (x + y) % 9 else P(u, x, y, SL[1])
        P(u, x, 29, SL[5]); P(u, x, 4, SL[5])
    for y in range(4, 37): P(u, 1, y, SL[4] if y < 29 else SL[2]); P(u, W - 2, y, SL[2] if y < 29 else SL[1])
    for k in range(6):                                        # slab joints (two blocks) & cracks
        pass
    for y in range(5, 29): P(u, 70 + (y // 6) % 2, y, SL[1])                     # joint between two slabs
    for y in range(29, 37): P(u, 71, y, SL[0])
    for cx, cy, n in ((24, 10, 9), (110, 20, 7), (92, 7, 5)):                   # hairline cracks
        x, y = cx, cy
        for k in range(n): P(u, x, y, SL[1]); x += r.choice((1, 1, 2)); y += r.choice((0, 1, -1)) if 5 < y < 27 else 0
    for x in (1, 2, 3, W - 2, W - 3, 40, 41, 120): P(u, x, 29, (0, 0, 0, 0)); P(u, x, 30, (0, 0, 0, 0)) if x < 4 or x > W - 4 else P(u, x, 30, SL[0])  # chipped edge
    for (x, y) in ((1, 4), (2, 4), (1, 5), (W - 2, 4), (W - 3, 4), (W - 2, 5)): P(u, x, y, (0, 0, 0, 0))            # rounded worn corners
    for x in range(50, 56): P(u, x, 36, (0, 0, 0, 0))                                                              # chunk out of the front lip
    for x in range(51, 55): P(u, x, 35, SL[0])
    for cx, cy, rx, ry, col in ((32, 18, 7, 3, (92, 40, 36)), (100, 12, 5, 2.5, (78, 54, 30)), (126, 22, 4, 2, (92, 40, 36)), (58, 24, 3, 1.5, (60, 50, 40))):   # wine / grease stains
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and BAYER[y % 4][x % 4] / 16 < 1 - d * .7: P(u, x, y, lerp(u.get_at((x, y))[:3], col, .55))
    for k in range(70):                                       # crumbs and flour dust
        x, y = r.randrange(6, W - 6), r.randrange(6, 27)
        P(u, x, y, r.choice([(214, 196, 150), (186, 150, 96), (232, 226, 210), (150, 112, 70)]))
    for y in range(8, 16):                                    # flour drift near the left end
        for x in range(8, 22):
            if r.random() < .35 - abs(x - 15) * .03: P(u, x, y, (220, 214, 200))
    # bread crust, cracked bowl, rusty knife
    ellipse(u, 46, 12, 6, 3, (150, 96, 50)); ellipse(u, 46, 11, 5, 2, (196, 140, 76)); P(u, 44, 10, (226, 186, 120)); P(u, 51, 13, (90, 56, 30))
    ellipse(u, 88, 17, 7, 3.5, WD[1]); ellipse(u, 88, 16, 6, 2.5, WD[3]); ellipse(u, 88, 16, 4, 1.5, WD[0])
    line(u, WD[0], (90, 13), (92, 19)); P(u, 84, 15, WD[4])
    line(u, (150, 146, 150), (112, 9), (124, 6)); line(u, (110, 76, 50), (124, 6), (129, 5)); P(u, 116, 8, (130, 70, 40)); P(u, 113, 9, (190, 186, 190))
    s.blit(outline(u), (0, 0)); return s

# ---------- hearth: 3 cells (x14-16, floor row y3), 48x64 frames x4, anchor bottom-centre (24,63) ----------
def hearth(f):
    W, H = 48, 64; s = surf(W, H); u = surf(W, H); r = random.Random(3)
    shadow(s, 24, 61, 24, 3, 100)
    stonefill(u, (6, 0, 36, 16), SB, .5, r, grad=.25)         # hood / chimney breast up the wall
    for y in range(0, 16): P(u, 6, y, SB[3]); P(u, 41, y, SB[1])
    for y in range(2, 15):                                    # soot streaks up the hood
        for x in range(16, 32):
            if (BAYER[y % 4][x % 4] / 16) < .55 - abs(x - 24) * .05 - (14 - y) * .015: P(u, x, y, lerp(u.get_at((x, y))[:3], SOOT, .6))
    stonefill(u, (0, 14, 48, 7), WD, .8, r, blocky=False, grad=.5)    # oak mantel beam
    for x in range(0, 48): P(u, x, 14, WD[4]); P(u, x, 20, WD[0])
    for x, h_, c in ((5, 5, (120, 140, 120)), (9, 4, (150, 90, 60)), (39, 6, (180, 170, 150)), (43, 3, (90, 110, 140))):   # jars on the mantel
        for y in range(14 - h_, 14):
            for dx in range(3): P(u, x + dx, y, lerp(c, (20, 16, 20), .1 + dx * .2))
        P(u, x, 14 - h_, lerp(c, (255, 255, 255), .4))
    stonefill(u, (0, 21, 10, 33), SB, .7, r, grad=.2); stonefill(u, (38, 21, 10, 33), SB, .55, r, grad=.2)   # jambs
    for y in range(21, 54): P(u, 0, y, SB[4]); P(u, 9, y, SB[2]); P(u, 38, y, SB[3]); P(u, 47, y, SB[1])
    for y in range(21, 54):                                   # opening: soot-black back with dim bricks, arched top
        for x in range(10, 38):
            ar = 21 + max(0, 6 - int(math.sqrt(max(0, 196 - (x - 23.5) ** 2)) / 14 * 6 + 0))
            if y < ar: stonefill(u, (x, y, 1, 1), SB, .55, r); continue
            back = SOOT if (y // 4 + (x + (y // 4) % 2 * 3) // 6) % 7 else (30, 22, 22)
            if y % 4 == 0 or (x + (y // 4) % 2 * 3) % 6 == 0: back = (6, 4, 6)
            P(u, x, y, back)
    for x in range(10, 38):                                   # arch voussoir line
        ar = 21 + max(0, 6 - int(math.sqrt(max(0, 196 - (x - 23.5) ** 2)) / 14 * 6))
        P(u, x, ar, SB[5]); P(u, x, ar - 1, SB[4]) if ar > 21 else None
    stonefill(u, (0, 54, 48, 5), SL, .8, r, grad=.2)          # hearth stone top + front edge
    for x in range(0, 48): P(u, x, 54, SL[5]); P(u, x, 59, SL[1]); P(u, x, 60, SL[1]); P(u, x, 61, SL[0])
    for x in range(0, 48): P(u, x, 58, SL[2])
    # logs + embers
    line(u, WD[1], (13, 52), (33, 50), 3); line(u, WD[0], (17, 53), (36, 53), 2); P(u, 34, 49, WD[3]); P(u, 13, 51, WD[3])
    for k in range(18):
        x, y = r.randrange(12, 36), r.randrange(51, 55); P(u, x, y, FL[(k + f) % 3])
    # flames (animated), behind the pot
    rf = random.Random(100 + f)
    for k in range(9):
        bx = 14 + k * 2.4 + rf.uniform(-1, 1); hgt = 6 + rf.random() * 9 * (1 - abs(k - 4) / 6)
        for j in range(int(hgt)):
            y = 51 - j; x = bx + math.sin((j + f * 2 + k) * .9) * 1.2
            c = FL[3] if j < hgt * .3 and 3 <= k <= 5 else FL[2] if j < hgt * .55 else FL[1] if j < hgt * .8 else FL[0]
            P(u, x, y, c); P(u, x + 1, y, FL[max(0, FL.index(c) - 1)]) if j < hgt * .6 else None
    # crane hook, chain and cauldron
    line(u, IR[2], (34, 24), (24, 24)); P(u, 35, 24, IR[3]); line(u, IR[1], (24, 24), (24, 30))
    for y in (25, 27, 29): P(u, 23, y, IR[3])
    line(u, IR[2], (17, 33), (24, 30)); line(u, IR[2], (31, 33), (24, 30))           # bail
    blob(u, 24, 41, 9, 7, IR[:4])
    ellipse(u, 24, 34, 9, 2.5, IR[0]); ellipse(u, 24, 34, 7.5, 1.6, (112, 70, 34))  # rim + stew
    for b in range(3):
        ph = (f + b * 3) % 4; bx = 20 + b * 4
        if ph < 3: P(u, bx, 34, (170, 116, 60)); P(u, bx, 33 + (ph == 1), (210, 160, 90))
    P(u, 17, 37, IR[4]); P(u, 18, 36, IR[4]); line(u, IR[3], (16, 38), (16, 42))    # rim light on the pot
    for x in range(16, 33):                                   # firelight catching the pot belly underside
        P(u, x, 47, lerp(IR[2], FL[1], .35))
    for y in range(28, 54): P(u, 10, y, lerp(u.get_at((10, y))[:3], FL[1], .25)); P(u, 37, y, lerp(u.get_at((37, y))[:3], FL[1], .25))
    for k in range(5):                                        # crumbled jamb corner, ash on the hearth stone
        P(u, r.randrange(2, 46), r.randrange(55, 58), (120, 116, 112))
    P(u, 0, 21, (0, 0, 0, 0)); P(u, 0, 22, (0, 0, 0, 0)); P(u, 47, 30, (0, 0, 0, 0))
    o = outline(u); s.blit(o, (0, 0))
    for k in range(4):                                        # steam from the stew up into the hood (thin, translucent)
        y = 31 - ((f * 3 + k * 5) % 16); x = 21 + k * 2 + int(math.sin(f * .8 + k) * 1.5)
        if y > 18: P(s, x, y, (190, 184, 176, 110)); P(s, x, y - 1, (170, 164, 160, 60))
    return s

# ---------- wall decals (north face, hang from the face top like the study banners) ----------
def pot_rack():
    W, H = 32, 30; u = surf(W, H); r = random.Random(4)
    for x in (2, 29): pygame.draw.rect(u, IR[1], (x - 1, 1, 3, 4)); P(u, x, 2, IR[4])                      # wall brackets
    line(u, IR[2], (1, 4), (30, 4)); line(u, IR[4], (1, 3), (30, 3))                                        # bar
    for x in (6, 16, 25):
        line(u, IR[2], (x, 5), (x, 7)); P(u, x + 1, 7, IR[3])                                                # S hooks
    # copper frying pan (handle up)
    line(u, CU[1], (6, 8), (6, 14), 2); P(u, 6, 8, CU[3])
    ellipse(u, 6, 20, 5, 6, CU[1]); ellipse(u, 6, 20, 4, 5, CU[2]); ellipse(u, 5, 19, 2, 3, CU[3]); P(u, 8, 23, (60, 90, 70)); P(u, 4, 23, CU[0])  # verdigris
    # iron pot by its bail
    line(u, IR[2], (12, 13), (16, 8)); line(u, IR[2], (20, 13), (16, 8))
    blob(u, 16, 18, 5, 5, IR[:4]); ellipse(u, 16, 13, 5, 1.5, IR[0]); P(u, 13, 16, IR[4])
    # ladle + copper saucepan
    line(u, WD[3], (25, 8), (25, 20)); ellipse(u, 25, 22, 3, 2, IR[2]); P(u, 24, 21, IR[4])
    line(u, CU[2], (28, 8), (28, 12)); pygame.draw.rect(u, CU[1], (26, 13, 5, 6)); line(u, CU[3], (26, 13), (30, 13)); P(u, 27, 15, CU[3])
    s = outline(u); return s

def herbs(v):
    W, H = 16, 26; u = surf(W, H); r = random.Random(20 + v)
    pygame.draw.rect(u, WD[2], (6, 1, 4, 3)); P(u, 7, 1, WD[4])                                            # wooden peg
    line(u, (160, 140, 100), (8, 4), (8, 8))                                                               # string
    if v == 0:      # dried herb bundle, heads down
        for k in range(9):
            x0 = 8 + (k - 4) * .5; x1 = 8 + (k - 4) * 1.4 + r.uniform(-.6, .6); y1 = 20 + r.randrange(-2, 4)
            line(u, r.choice([(90, 104, 56), (110, 120, 64), (130, 118, 70)]), (x0, 9), (x1, y1))
            P(u, x1, y1 + 1, r.choice([(150, 110, 150), (170, 150, 80), (120, 136, 70)])); P(u, x1 + 1, y1, (100, 112, 60))
        line(u, (200, 170, 110), (6, 9), (10, 9)); line(u, (150, 120, 80), (6, 10), (10, 10))             # twine wrap
    else:           # garlic braid + a sprig of bay
        for k in range(5):
            cx, cy = 8 + (1 if k % 2 else -1), 10 + k * 3
            ellipse(u, cx, cy, 2.6, 2.0, (196, 186, 164)); P(u, cx - 1, cy - 1, (236, 230, 212)); P(u, cx + 1, cy + 1, (150, 130, 120))
            P(u, cx, cy - 2, (170, 150, 110))
        for k in range(4): P(u, 11 + k // 2, 8 + k, (80, 104, 54)); P(u, 12 + k // 2, 8 + k, (60, 84, 44))
    return outline(u)

# ---------- floor props ----------
def barrel():
    W, H = 16, 24; s = surf(W, H); u = surf(W, H); r = random.Random(5)
    shadow(s, 8, 22, 8, 2.5)
    for y in range(6, 22):
        bul = 1 if 9 < y < 19 else 0
        for x in range(2 - bul, 14 + bul):
            v = .75 - abs(x - 6) / 10 + (BAYER[y % 4][x % 4] / 16 - .5) * .15 + (.08 if x % 3 == 0 else 0)
            P(u, x, y, WD[max(0, min(4, int(v * 5)))])
    for y in (8, 15, 20):
        for x in range(1, 15):
            if u.get_at((x, y)).a: P(u, x, y, IR[2] if x > 4 else IR[3])
    ellipse(u, 8, 6, 6, 2.5, WD[3]); ellipse(u, 8, 6, 5, 1.6, (40, 46, 56))                                # open top, dark water
    P(u, 6, 6, (110, 130, 150)); P(u, 7, 6, (80, 100, 120))
    line(u, WD[4], (9, 6), (13, 0)); ellipse(u, 13, 1, 1.5, 1, WD[3])                                      # dipper handle
    pygame.draw.polygon(u, WD[2], [(0, 21), (5, 18), (6, 20), (1, 23)])                                    # lid leaning against it
    s.blit(outline(u), (0, 0)); return s

def sack(v):
    W, H = 16, 20; s = surf(W, H); u = surf(W, H); r = random.Random(6 + v)
    shadow(s, 8, 18, 8, 2.5)
    SK = [(80, 66, 48), (112, 94, 68), (144, 124, 92), (176, 156, 120)]
    blob(u, 8, 13, 6.5, 5.5, SK); blob(u, 8, 8, 4.5, 3.5, SK)
    line(u, SK[0], (5, 7), (11, 7)); line(u, (160, 130, 90), (6, 6), (10, 6))                             # tied neck
    P(u, 8, 3, SK[2]); P(u, 7, 4, SK[3]); P(u, 9, 4, SK[1]); P(u, 6, 12, SK[0]); P(u, 10, 15, SK[0])     # ear + creases
    o = outline(u); s.blit(o, (0, 0))
    if v == 0:      # flour sack: torn corner, spilled flour
        P(s, 13, 15, (226, 220, 206)); P(s, 13, 16, (226, 220, 206))
        for k in range(26):
            x, y = 12 + r.randrange(0, 4), 15 + r.randrange(0, 5)
            if s.get_at((x, y)).a < 200: P(s, x, y, (226, 220, 206, 230))
        for x in range(4, 10): P(s, x, 10, (210, 204, 190))                                                # stencil band
    else:           # potato sack: a couple rolled out
        for cx, cy in ((13, 17), (2, 18)):
            ellipse(s, cx, cy, 1.8, 1.4, (150, 116, 70)); P(s, cx - 1, cy - 1, (190, 156, 100)); P(s, cx + 1, cy + 1, (90, 66, 40))
    return s

def chopping_block():
    W, H = 16, 24; s = surf(W, H); u = surf(W, H); r = random.Random(7)
    shadow(s, 8, 22, 8, 2.5)
    for y in range(12, 22):                                   # stump side
        for x in range(2, 14):
            v = .7 - abs(x - 6) / 9 + (BAYER[y % 4][x % 4] / 16 - .5) * .2 + (.1 if (x * 5) % 7 == 0 else 0)
            P(u, x, y, WD[max(0, min(4, int(v * 5)))])
    for x in (1, 14): P(u, x, 21, WD[1])                      # roots
    ellipse(u, 8, 12, 6, 3, (150, 114, 76)); ellipse(u, 8, 12, 4, 2, (176, 138, 92)); ellipse(u, 8, 12, 2, 1, (150, 114, 76))   # rings
    P(u, 8, 12, (110, 80, 50)); line(u, (110, 70, 50), (5, 12), (7, 14))
    for x, y in ((4, 11), (11, 13), (6, 14)): P(u, x, y, (110, 40, 36))                                    # old blood
    # cleaver bitten into the top
    pygame.draw.polygon(u, IR[3], [(7, 4), (13, 4), (13, 11), (8, 11)]); line(u, IR[4], (7, 4), (13, 4)); line(u, IR[1], (8, 11), (13, 11))
    P(u, 12, 5, IR[1]); P(u, 9, 9, (130, 70, 40)); P(u, 11, 10, (130, 70, 40))                              # rivet hole, rust
    line(u, WD[1], (7, 6), (2, 4), 2); P(u, 2, 3, WD[3])                                                   # handle
    for k in range(3): P(u, 3 + k * 4, 22, (220, 206, 180))                                                # bone chips
    s.blit(outline(u), (0, 0)); return s

def crockery(v):
    s = surf(16, 16); r = random.Random(8 + v); u = surf(16, 16)
    if v == 0:      # broken plate: cream glaze, blue rim band
        for k, (cx, cy, a0) in enumerate(((5, 8, 0), (10, 6, 1), (9, 11, 2), (13, 11, 3))):
            pts = [(cx + math.cos(a) * rr, cy + math.sin(a) * rr * .7) for a, rr in ((a0, 3), (a0 + 2.1, 2.4), (a0 + 4, 2.8))]
            pygame.draw.polygon(u, (214, 206, 186), pts); P(u, pts[0][0], pts[0][1], (70, 90, 150)); P(u, pts[1][0], pts[1][1], (90, 110, 170))
        for k in range(5): P(u, r.randrange(2, 14), r.randrange(4, 14), (200, 192, 172))
    else:           # broken terracotta jug: neck + belly shards + puddle stain
        pygame.draw.ellipse(u, (150, 74, 44), (3, 7, 7, 5)); pygame.draw.ellipse(u, (60, 30, 20), (4, 8, 4, 2))
        line(u, (190, 104, 64), (4, 8), (7, 7)); pygame.draw.rect(u, (130, 62, 38), (11, 5, 3, 4)); P(u, 11, 5, (190, 104, 64))
        pygame.draw.polygon(u, (150, 74, 44), [(9, 12), (13, 11), (12, 14)]); P(u, 10, 12, (190, 104, 64))
        for y in range(9, 15):
            for x in range(1, 15):
                if ((x - 8) / 7) ** 2 + ((y - 12) / 3) ** 2 < 1 and BAYER[y % 4][x % 4] < 8: P(s, x, y, (40, 26, 30, 110))
    s.blit(outline(u), (0, 0)); return s

# ---------- build files ----------
files = {}
def save(name, sf): pygame.image.save(sf, os.path.join(HERE, name)); files[name] = sf
TBL = stone_table(); save("stone_table.png", TBL)
HC = 10   # crop the hood: the hearth stands about one wall height tall
HF = surf(48 * 4, 64 - HC); [HF.blit(hearth(f), (f * 48, -HC)) for f in range(4)]; save("hearth.png", HF)
save("pot_rack.png", pot_rack())
HB = surf(32, 26); [HB.blit(herbs(v), (v * 16, 0)) for v in range(2)]; save("herbs_hanging.png", HB)
save("kitchen_barrel.png", barrel())
SK = surf(32, 20); [SK.blit(sack(v), (v * 16, 0)) for v in range(2)]; save("sack.png", SK)
save("chopping_block.png", chopping_block())
CR = surf(32, 16); [CR.blit(crockery(v), (v * 16, 0)) for v in range(2)]; save("crockery_broken.png", CR)
shutil.copy(os.path.join(ART, "decor", "cobweb.png"), os.path.join(HERE, "cobweb.png")); files["cobweb.png"] = pygame.image.load(os.path.join(HERE, "cobweb.png"))

# ---------- placements (setpiece.py style) ----------
K = "kitchen/"
KITCHEN_TABLE_HOOK = (9, ("%", K + "stone_table.png", "table"), (72, 45))         # HOOKS[9], HOOK_ANCHOR[9]
# objects: (file, frame_w, variant_or_None, cell_x, cell_y, width_cells, anim_fps, light)  -- bottom-centre of the cells, sorted at the cell bottom
KITCHEN_OBJ = [(K + "hearth.png", 48, None, 14, 3, 3, 6, (24, 36)),
               (K + "kitchen_barrel.png", 16, 0, 4, 3, 1, 0, None),
               (K + "sack.png", 16, 0, 5, 3, 1, 0, None),
               (K + "sack.png", 16, 1, 4, 4, 1, 0, None),
               (K + "chopping_block.png", 16, 0, 19, 9, 1, 0, None)]
# wall decals on the north face (row 2): (file, frame_w, variant, x, y); top-left = _face(x, y, top), hanging DOWN from the face top like the banners
KITCHEN_WALL = [(K + "pot_rack.png", 32, 0, 8, 2), (K + "herbs_hanging.png", 16, 1, 6, 2), (K + "herbs_hanging.png", 16, 0, 18, 2), (K + "herbs_hanging.png", 16, 1, 19, 2)]
# floor decals: (file, frame_w, variant, x, y[, flip])
KITCHEN_FLOOR = [(K + "crockery_broken.png", 16, 0, 6, 11), (K + "crockery_broken.png", 16, 1, 12, 11),
                 (K + "cobweb.png", 16, 0, 20, 3, True), (K + "cobweb.png", 16, 0, 4, 14)]
import art3 as A3
R = rooms(); room = R[9]; g = room["grid"]
POSTS = sorted((x, y) for y in range(18) for x in range(24) if A3.is_post(g, x, y))
for f, fw, v, x, y in KITCHEN_WALL:
    for k in range(fw // 16): assert g[y][x + k] == "#" and not A3.is_post(g, x + k, y), (f, x + k, y)
for o in KITCHEN_OBJ:
    for k in range(o[5]): assert room["walk"][o[4]][o[3] + k], o
    if o[0].endswith("hearth.png"):
        for k in range(o[5]): assert g[o[4] - 1][o[3] + k] == "#" and not A3.is_post(g, o[3] + k, o[4] - 1)
BLOCK = [(o[3] + k, o[4]) for o in KITCHEN_OBJ for k in range(o[5])]
# reachability: every exit cell and every item must stay connected, with a 1-cell margin in front of each doorway
walk = [row[:] for row in room["walk"]]
for x, y in BLOCK: walk[y][x] = False
edge = [(x, y) for y in range(18) for x in range(24) if room["walk"][y][x] and (x in (0, 23) or y in (0, 17))]
items = [(i["x"], i["y"]) for i in room.get("items", []) + room.get("hidden", [])]
def bfs(wk, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and wk[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
start = (11, 0); before_ = bfs(room["walk"], start); seen = bfs(walk, start)
edge = [e for e in edge if e in before_]          # the walkable strip x8-15 y16-17 south of the room is not connected to it (unchanged)
assert all(e in seen for e in edge) and all(i in seen for i in items)
assert before_ - seen == set(BLOCK), before_ - seen        # only the prop cells themselves are lost, nothing gets cut off
mouths = [(11, 3), (12, 3), (20, 4), (5, 14), (6, 14), (17, 14), (18, 14)]
assert not set(mouths) & set(BLOCK)
def pl(l): return [list(t) for t in l]
man = {"room": 9, "room_name": "Kitchen (interior x4-20, y3-14; table '%' x8-16 y8-9; exits N x11-12, E y4, S x5-6 and x17-18)",
 "sheets": {
  "stone_table.png": {"frame_size": [144, 46], "anchor": {"px": [72, 45], "note": "bottom-centre of the 9x2 '%' block -> world (8*16+72, 10*16)"}, "footprint_tiles": [9, 2], "blocking": True,
                      "depth_sort_y": "(8+2)*16 = 160", "shadow_baked": True, "content": "two worn limestone slabs on three squat trestles: chipped edges and corners, hairline cracks, wine/grease stains, crumbs, flour drift, bread crust, cracked wooden bowl, rusty knife"},
  "hearth.png": {"frame_size": [48, 54], "frames": 4, "fps": 6, "loop": True, "anchor": {"px": [24, 53]}, "footprint_tiles": [3, 1], "blocking": True, "shadow_baked": True,
                 "content": "fieldstone fireplace built against the north wall: soot-streaked hood rising over the wall face and top, oak mantel with jars, arched opening, logs, animated flames and embers, iron crane with a bubbling stew cauldron, wisps of steam (translucent)",
                 "light": {"px": [24, 36], "color": [255, 150, 70], "radius_hint": 64, "flicker": "0.8-1.0 synced to the frame"}, "outline_crossing": True},
  "pot_rack.png": {"frame_size": [32, 30], "layer": "wall decal, north face, hangs down from the face top (like banner_royal)", "blocking": False, "spans_cells": 2},
  "herbs_hanging.png": {"frame_size": [16, 26], "variants": 2, "layer": "wall decal, north face, hangs from the face top", "blocking": False, "content": "v0 dried herb bundle, v1 garlic braid with bay"},
  "kitchen_barrel.png": {"frame_size": [16, 24], "anchor": {"px": [8, 23]}, "footprint_tiles": [1, 1], "blocking": True, "shadow_baked": True},
  "sack.png": {"frame_size": [16, 20], "variants": 2, "anchor": {"px": [8, 19]}, "footprint_tiles": [1, 1], "blocking": True, "shadow_baked": True, "content": "v0 torn flour sack with a spill, v1 potato sack"},
  "chopping_block.png": {"frame_size": [16, 24], "anchor": {"px": [8, 23]}, "footprint_tiles": [1, 1], "blocking": True, "shadow_baked": True, "content": "stump block with a cleaver bitten in, old blood, bone chips"},
  "crockery_broken.png": {"frame_size": [16, 16], "variants": 2, "layer": "floor decal", "blocking": False, "content": "v0 smashed plate, v1 broken jug + dried stain"},
  "cobweb.png": {"same_as": "decor/cobweb.png", "layer": "wall-top-corner (floor decal at the inner corner cell)"}},
 "wall_post_cells_room9": [list(p) for p in POSTS],
 "placements_room9": {
  "HOOKS[9]": ["%", K + "stone_table.png", "table"], "HOOK_ANCHOR[9]": [72, 45],
  "KITCHEN_OBJ": pl(KITCHEN_OBJ), "KITCHEN_WALL": pl(KITCHEN_WALL), "KITCHEN_FLOOR": pl(KITCHEN_FLOOR),
  "blocking_cells": [list(c) for c in BLOCK], "reachability": "BFS from the north exit reaches every exit cell (N x11-12, E y4, S x5-6, x17-18); doorway mouths kept clear; room 9 has no items or monsters",
  "setpiece_py": ("HOOKS[9] = (\"%\", \"kitchen/stone_table.png\", \"table\"); HOOK_ANCHOR[9] = (72, 45)\n"
                  "KITCHEN_OBJ = " + repr(KITCHEN_OBJ) + "\nKITCHEN_WALL = " + repr(KITCHEN_WALL) + "\nKITCHEN_FLOOR = " + repr(KITCHEN_FLOOR))},
 "integration_notes": ["room_themes.json: \"9\": {\"name\": \"Kitchen\", \"setpiece\": true} (no random decor; keep the default flag floor and dungeon-grey walls)",
                "table: add 9 to HOOKS/HOOK_ANCHOR with the '%' glyph (art3 already skips hooked cells; blocking unchanged, the '%' cells stay solid)",
                "objects(9) -> KITCHEN_OBJ, blockers(9) -> its cells (apply_blocking BFS as for 56); hearth: animate frames at 6 fps, warm light at sprite px (24,36), radius ~64 (bigger than 'candle'), outline-crossing (its hood rises over the north wall top)",
                "draw KITCHEN_WALL in wall_spots/draw_wall for rid 9, top-aligned at _face(x, y, top) like the banners (both are 'hang' decals: pot_rack 32x30, herbs 16x26); pot_rack spans wall cells x8-9",
                "draw KITCHEN_FLOOR in setpiece.draw_floor (cobweb at (20,3) flipped)"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)

# ---------- previews: before/after baked room 9, lit and unlit (darkness + lamp + hearth light) ----------
b, TOP = baked(9)
r2 = copy.deepcopy(room); [r2.pop(k, None) for k in ("decor", "_set_done", "set_objs", "_hook_blocks")]
r2["grid"] = [row.replace("%", " ") for row in r2["grid"]]; r2["theme"] = dict(r2.get("theme") or {}, setpiece=True)   # preview: hooked table cells get floor, no random decor
for y in (8, 9):
    for x in range(8, 17): r2["walk"][y][x] = True
raw, _ = art3.bake_room(9, r2); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
a = pygame.Surface(raw.get_size()); a.fill((20, 16, 26)); a.blit(raw, (0, 0))
for f, fw, v, x, y, *fl in KITCHEN_FLOOR:
    sp = files[f.split("/")[1]].subsurface((v * fw, 0, fw, 16))
    if fl and fl[0]: sp = pygame.transform.flip(sp, True, False)
    a.blit(sp, (x * T, y * T + TOP))
for f, fw, v, x, y in KITCHEN_WALL:
    im = files[f.split("/")[1]]; a.blit(im.subsurface((v * fw, 0, fw, im.get_height())), (x * T, y * T + TOP - 8 + T))
def objs(frame_i):
    dr = []
    for f, fw, v, x, y, w, fps, light in KITCHEN_OBJ:
        im = files[f.split("/")[1]]; k = frame_i if fps else (v or 0); sp = im.subsurface(((k % (im.get_width() // fw)) * fw, 0, fw, im.get_height()))
        X, Y = x * T + w * T // 2, y * T + T; dr.append((Y, sp, X - sp.get_width() // 2, Y - sp.get_height()))
    dr.append((160, TBL, 8 * T + 72 - 72, 160 - 45))
    return sorted(dr, key=lambda d: d[0])
def compose(base, fi):
    o = base.copy()
    for _, sp, x, y in objs(fi): o.blit(sp, (x, y + TOP))
    return o
A = compose(a, 0)
def dark(s, lights):
    o = s.copy(); dk = pygame.Surface(s.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 232))
    for (cx, cy, rr) in lights:
        for r_ in range(rr, 0, -2):
            al = int(232 * (r_ / rr) ** 2.0)
            c = dk.get_at((cx + r_, cy)) if 0 <= cx + r_ < s.get_width() else None
            pygame.draw.circle(dk, (4, 3, 10, al), (cx, cy), r_, 2)
    o.blit(dk, (0, 0)); return o
def dark2(s, lights, warm=None):
    import numpy as np
    w, h = s.get_size(); X, Y = np.meshgrid(np.arange(w), np.arange(h), indexing="ij"); lit = np.zeros((w, h))
    for cx, cy, rr in lights: lit = np.maximum(lit, np.clip(1 - np.hypot(X - cx, Y - cy) / rr, 0, 1) ** 1.3)
    arr = pygame.surfarray.array3d(s).astype(float); amb = .1
    f_ = (amb + (1 - amb) * lit)[..., None]
    out = arr * f_
    if warm:
        cx, cy, rr = warm; wl = np.clip(1 - np.hypot(X - cx, Y - cy) / rr, 0, 1) ** 1.6
        out += wl[..., None] * np.array([60, 26, 0])
    o = pygame.Surface((w, h)); pygame.surfarray.blit_array(o, np.clip(out, 0, 255).astype(np.uint8)); return o
HL = (15 * T + 8, 3 * T + T - 54 + 36 + TOP)
LAMP = (11 * T + 8, 11 * T + TOP)
tiles = [("before (lit)", b), ("after (lit)", A), ("before, unlit: lamp only", dark2(b, [(LAMP[0], LAMP[1], 80)])),
         ("after, unlit: lamp + hearth light", dark2(A, [(LAMP[0], LAMP[1], 80), (HL[0], HL[1], 96)], (HL[0], HL[1], 80)))]
crop = pygame.Rect(2 * T, 0, 21 * T, 16 * T + TOP)
font = pygame.font.Font(None, 18); S = 2
Pv = pygame.Surface((crop.w * S * 2 + 30, (crop.h * S + 26) * 2 + 10)); Pv.fill((40, 36, 48))
for i, (nm, t) in enumerate(tiles):
    x0, y0 = 10 + (i % 2) * (crop.w * S + 10), 6 + (i // 2) * (crop.h * S + 26)
    Pv.blit(font.render(nm, True, (230, 220, 200)), (x0, y0)); Pv.blit(pygame.transform.scale(t.subsurface(crop), (crop.w * S, crop.h * S)), (x0, y0 + 18))
pygame.image.save(Pv, os.path.join(HERE, "preview.png"))
Z = pygame.Surface((300, 120)); Z.fill((56, 54, 62)); xx = 4
for nm in ("stone_table.png", "pot_rack.png", "herbs_hanging.png", "kitchen_barrel.png", "sack.png", "chopping_block.png", "crockery_broken.png"):
    im = files[nm]; Z.blit(im, (xx, 4 if nm == "stone_table.png" else 60)) if nm == "stone_table.png" else Z.blit(im, (xx - 148 if xx > 148 else xx, 60)); xx += (im.get_width() + 4) if nm != "stone_table.png" else 0
Z = pygame.Surface((420, 130)); Z.fill((56, 54, 62)); Z.blit(TBL, (4, 4)); Z.blit(HF, (156, 4)); xx = 4
for nm in ("pot_rack.png", "herbs_hanging.png", "kitchen_barrel.png", "sack.png", "chopping_block.png", "crockery_broken.png", "cobweb.png"):
    im = files[nm]; Z.blit(im, (xx, 72)); xx += im.get_width() + 6
pygame.image.save(pygame.transform.scale(Z, (1260, 390)), os.path.join(HERE, "preview_sheet.png"))
from PIL import Image
fr = []
for fi in range(4):
    c = compose(a, fi).subsurface(pygame.Rect(12 * T, 0, 7 * T, 6 * T + TOP)).copy()
    fr.append(Image.frombytes("RGB", c.get_size(), pygame.image.tostring(pygame.transform.scale(c, (c.get_width() * 4, c.get_height() * 4)), "RGB")))
fr[0].save(os.path.join(HERE, "preview_hearth.gif"), save_all=True, append_images=fr[1:], duration=166, loop=0)
copy_to_game(HERE, "kitchen"); print("ok", BLOCK)
