"""'Old & abandoned' decor set on the 16px grid. python3 make_decor.py
1x RGBA, baked dark outline on objects (decals use soft dark edges, no outline so they sit IN the surface), no shadow/glow."""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art import lerp
T = 16
TH = {  # theme palettes
 "indoor":  dict(st=[(46, 44, 52), (66, 62, 70), (88, 84, 88), (120, 114, 122)], wet=[(34, 40, 56), (60, 74, 96), (120, 140, 160)], moss=[(58, 80, 44), (80, 108, 54)], dust=(120, 112, 100)),
 "garden":  dict(st=[(54, 50, 44), (80, 74, 62), (104, 96, 80), (136, 126, 104)], wet=[(30, 46, 40), (52, 82, 76), (120, 160, 150)], moss=[(52, 92, 36), (84, 128, 50)], dust=(110, 92, 60)),
 "dungeon": dict(st=[(26, 24, 28), (42, 38, 40), (60, 54, 52), (86, 80, 74)], wet=[(18, 24, 26), (36, 50, 48), (90, 120, 110)], moss=[(50, 70, 50), (70, 96, 60)], dust=(80, 74, 66)),
}
WOOD = [(44, 28, 18), (72, 46, 28), (100, 66, 40), (130, 90, 56)]; BONE = [(150, 140, 120), (200, 192, 170), (232, 226, 206)]
CLOTH = {"red": [(70, 20, 26), (110, 34, 38), (150, 60, 56)], "blue": [(26, 34, 70), (40, 56, 106), (70, 90, 140)], "green": [(28, 50, 32), (44, 78, 46), (72, 110, 66)]}
def rr(seed): return random.Random(seed)
# ---------- drawers: each returns a Surface; v = variant index
SH = (10, 8, 16)
def shadow(s, cx, cy, rx, ry, a=110):
    """baked contact shadow: dithered dark ellipse (drawn first, under the object)"""
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d < .55 or BAYER[y % 4][x % 4] / 16 > (d - .55) * 2: s.set_at((x, y), (*SH, a))
def stone(s, x, y, w, h, p, rnd=None):
    """chunky rounded stone: outline, dithered 4-tone shading lit top-left, rim highlight, dark underside"""
    cx, cy, rx, ry = x + w / 2 - .5, y + h / 2 - .5, w / 2 + .3, h / 2 + .3
    pygame.draw.ellipse(s, OUT, (x - 1, y - 1, w + 2, h + 2))
    for yy in range(y - 1, y + h + 1):
        for xx in range(x - 1, x + w + 1):
            if not (0 <= xx < s.get_width() and 0 <= yy < s.get_height()): continue
            d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
            if d <= 1:
                v = .62 - (xx - cx) / rx * .22 - (yy - cy) / ry * .38 - d * .15 + (BAYER[yy % 4][xx % 4] / 16 - .5) * .22
                s.set_at((xx, yy), p[max(0, min(3, int(v * 4)))])
    s.set_at((round(cx - rx * .4), round(cy - ry * .6)), p[3])
    if w > 3: s.set_at((round(cx - rx * .4) + 1, round(cy - ry * .6)), p[3])
def crack(v, th):
    """chunky crack: 2px dark gash, lit lower lip, chipped stone flecks"""
    s = surf(T, T); r = rr(v); p = TH[th]["st"]; x, y = r.randrange(5, 11), 1; pts = []
    while y < 15:
        pts.append((x, y)); x = max(2, min(13, x + r.choice((-2, -1, 0, 1, 2)))); y += r.choice((2, 3))
    pts.append((x, 15))
    for a_, b_ in zip(pts, pts[1:]):
        line(s, OUT, a_, b_, 2); line(s, p[3], (a_[0] + 1, a_[1] + 1), (b_[0] + 1, b_[1] + 1))
    bx, by = pts[len(pts) // 2]                                   # branch
    line(s, OUT, (bx, by), (bx + (3 if v % 2 else -3), by + 3)); s.set_at((bx + (4 if v % 2 else -4), by + 4), p[3])
    for k in range(2): q = pts[r.randrange(len(pts))]; s.set_at((q[0] + 2, q[1]), p[0])
    return s
def missing_stone(v, th):
    """recessed hole: shadowed top edge, visible stone behind, lit bottom lip"""
    s = surf(T, T); p = TH[th]["st"]; r = rr(v + 10); w, h = (9, 6) if v == 0 else (11, 7); x0, y0 = r.randrange(1, T - w), r.randrange(2, T - h - 2)
    pygame.draw.rect(s, OUT, (x0 - 1, y0 - 1, w + 2, h + 2))
    pygame.draw.rect(s, lerp(p[0], (8, 6, 12), .5), (x0, y0, w, h))                       # deep recess
    pygame.draw.rect(s, lerp(p[1], (8, 6, 12), .45), (x0 + 1, y0 + 3, w - 3, h - 3))      # back stone
    line(s, lerp(p[2], (8, 6, 12), .4), (x0 + 1, y0 + 3), (x0 + w - 3, y0 + 3))
    line(s, (6, 4, 10), (x0, y0), (x0 + w - 1, y0)); line(s, (6, 4, 10), (x0, y0 + 1), (x0 + w - 1, y0 + 1))  # top shadow
    line(s, p[3], (x0 - 1, y0 + h), (x0 + w, y0 + h)); line(s, p[2], (x0, y0 + h + 1), (x0 + w - 1, y0 + h + 1))  # lit bottom lip
    s.set_at((x0 + w, y0 + h + 1), OUT); stone(s, x0 + w - 2, y0 + h + 2, 2, 1, p) if y0 + h + 3 < T else None
    return s
def moss(v, th):
    """chunky moss clumps along the top of the face with a few drooping vines"""
    s = surf(T, T + 8); r = rr(v + 20); m = TH[th]["moss"]; P4 = [lerp(m[0], (14, 20, 12), .5), m[0], m[1], lerp(m[1], (200, 220, 140), .35)]
    for k in range(2 + v % 2):
        cx = 3 + k * 5 + r.randrange(-1, 2); L = r.randrange(7, 16)
        for y in range(2, L):                                      # vine (2px with highlight)
            x = cx + round(math.sin(y * .45 + k) * 1.2)
            s.set_at((x, y), P4[1]); s.set_at((x + 1, y), P4[0])
            if y % 4 == 1: s.set_at((x - 1, y), P4[2]); s.set_at((x - 2, y + 1), P4[1])   # leaf
        blob(s, cx + .5, L, 1.6, 1.4, P4)
    for k in range(4):                                             # clumps on top edge
        blob(s, 2 + k * 4 + r.randrange(-1, 2), 2 + r.randrange(0, 2), 2.6, 2.0, P4)
    return outline(s)
def cobweb(v, th):
    s = surf(T, T); c, c2 = (176, 172, 184, 170), (232, 228, 236, 230); L = 13 + (v % 2) * 2
    angs = (0, 22, 45, 68, 90)
    for a in angs:
        e = (math.cos(math.radians(a)) * L, math.sin(math.radians(a)) * L); line(s, c2, (0, 0), e)
    for rad in (3, 6, 9, 12):
        if rad > L: continue
        pts = [(math.cos(math.radians(a)) * rad, math.sin(math.radians(a)) * rad + (1 if 0 < a < 90 else 0)) for a in angs]   # sagging threads
        for i in range(len(pts) - 1): line(s, c2 if rad in (6, 12) else c, pts[i], pts[i + 1])
    for (x, y) in ((1, 1), (2, 1), (1, 2)): s.set_at((x, y), (250, 248, 252, 240))    # dense anchor
    if v == 2: pygame.draw.circle(s, OUT, (9, 8), 2); s.set_at((9, 8), (120, 30, 30)); s.set_at((8, 7), (200, 196, 204))  # dead spider husk
    return s
def rubble(v, th):
    s = surf(T, T); p = TH[th]["st"]; r = rr(v + 60)
    spots = [(3, 8, 5, 4), (9, 10, 4, 3), (6, 4, 3, 3), (11, 5, 3, 2), (2, 12, 3, 2)][: 3 + v]
    for (x, y, w, h) in spots: shadow(s, x + w / 2 + 1, y + h + .5, w / 2 + 1, 1.2, 120)
    for (x, y, w, h) in spots: stone(s, x, y, w, h, p)
    return s
def debris(v, th):
    s = surf(T, T); p = TH[th]["st"]; r = rr(v + 70)
    shadow(s, 8, 11, 6, 1.6, 100)
    a, b = (3, 10 - v), (12, 7 + v)                                  # broken plank with splintered end
    line(s, OUT, (a[0], a[1] + 1), (b[0], b[1] + 1), 4); line(s, WOOD[1], a, b, 2); line(s, WOOD[3], (a[0], a[1] - 1), (b[0], b[1] - 1))
    for k in range(3): s.set_at((b[0] + 1, b[1] - 1 + k), WOOD[2]); s.set_at((b[0] + 2, b[1] + k - 1), OUT)
    stone(s, 10, 11, 3, 2, p); stone(s, 2, 12, 2, 2, p)
    s.set_at((6, 6), WOOD[2]); s.set_at((7, 6), OUT)
    return s
def puddle(v, th):
    s = surf(T, T); w = TH[th]["wet"]; cx, cy = 8, 9; rx, ry = 6 + (v == 1), 3.4 + (v == 2) * .6
    for y in range(T):
        for x in range(T):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + math.sin(x * 1.1 + v * 2) * .12
            if d < 1.25:
                if d >= 1: c = (*lerp(w[0], (8, 6, 12), .5), 200)             # dark damp edge
                elif d > .7: c = (*w[0], 230)
                else: c = (*(w[1] if (x + y) % 5 else w[0]), 235)
                s.set_at((x, y), c)
    line(s, (*w[2], 255), (cx - 4, cy - 2), (cx - 1, cy - 2)); s.set_at((cx + 1, cy - 2), (*w[2], 255))   # reflection highlight
    line(s, (*lerp(w[2], w[1], .5), 230), (cx + 1, cy + 1), (cx + 3, cy + 1))
    line(s, (*lerp(w[1], (200, 210, 220), .3), 220), (cx - 4, cy + 3), (cx + 3, cy + 3))                   # lit near rim
    return s
def bones(v, th):
    s = surf(T, T)
    def bone(a, b):
        line(s, OUT, a, b, 4)
        for q in (a, b): pygame.draw.circle(s, OUT, q, 2)
        line(s, BONE[1], a, b, 2); line(s, BONE[2], (a[0], a[1] - 1), (b[0], b[1] - 1))
        for q in (a, b): pygame.draw.circle(s, BONE[1], q, 1); s.set_at((q[0] - 1, q[1] - 1), BONE[2]); s.set_at((q[0] + 1, q[1] + 1), BONE[0])
    shadow(s, 8, 12, 6, 1.8, 100)
    if v == 0: bone((3, 11), (12, 9))
    elif v == 1: bone((3, 9), (11, 12)); bone((5, 13), (12, 6))
    else:
        bone((8, 12), (13, 10))
        pygame.draw.ellipse(s, OUT, (1, 3, 9, 9)); pygame.draw.ellipse(s, BONE[1], (2, 4, 7, 7)); line(s, BONE[2], (3, 4), (6, 4))
        pygame.draw.rect(s, BONE[0], (3, 9, 5, 2)); s.set_at((3, 7), OUT); s.set_at((4, 7), OUT); s.set_at((6, 7), OUT); s.set_at((7, 7), OUT); s.set_at((5, 9), OUT)
        for x in (4, 6): s.set_at((x, 10), OUT)
    return s
def broken_furn(v, th):
    s = surf(T, T); shadow(s, 8, 12, 6, 1.6, 100); u = surf(T, T)
    if v == 0: line(u, WOOD[1], (2, 11), (12, 7), 3); line(u, WOOD[3], (2, 10), (12, 6)); pygame.draw.circle(u, WOOD[2], (12, 7), 2)   # turned chair leg
    elif v == 1: pygame.draw.rect(u, WOOD[1], (2, 7, 11, 4)); line(u, WOOD[3], (2, 7), (12, 7)); line(u, WOOD[0], (7, 7), (6, 10)); s.set_at((12, 9), (150, 150, 160))
    else: pygame.draw.polygon(u, WOOD[1], [(4, 12), (10, 5), (13, 7), (7, 13)]); line(u, WOOD[3], (4, 12), (10, 5)); u.set_at((11, 7), (160, 160, 170))
    s.blit(outline(u), (0, 0)); return s
CLUB = ["..##..", ".####.", "######", "##.###", "..##..", ".####."]
def club(s, x, y, c):
    for j, row in enumerate([".##.", "####", ".##.", "####", "####", ".##."][:0] or ["..#..", ".###.", "#####", "#.#.#", "..#..", ".###."]):
        for i, ch in enumerate(row):
            if ch == "#": s.set_at((x + i, y + j), c)
def weave(c, x, y, k): return lerp(c, (0, 0, 0), .12) if (x + y) % 2 == 0 and k else c
def rug(v, th):
    cl = CLOTH[["red", "blue"][v % 2]]; s = surf(32, T); r = rr(v + 100); gold = (176, 140, 72)
    shadow(s, 16, 9, 15, 6, 60)
    for y in range(2, 14):
        for x in range(3, 29):
            c = cl[1]
            if y in (3, 12) or x in (4, 27): c = gold
            elif y in (2, 13) or x in (3, 28): c = cl[0]
            c = weave(c, x, y, True); c = lerp(c, (90, 84, 78), .3 + r.random() * .12)     # faded weave
            s.set_at((x, y), (*c, 255))
    for y in range(3, 13, 1):                                         # fringe
        for x, d in ((2, -1), (29, 1)):
            if y % 2: s.set_at((x, y), (*lerp(gold, (90, 84, 78), .3), 255)); s.set_at((x + d, y), (*lerp(gold, (60, 56, 50), .4), 230))
    if v == 0: club(s, 14, 5, lerp((24, 18, 26), cl[1], .25))        # club suit motif (echoes the courtyard rug)
    else:
        for k in range(3): club(s, 7 + k * 7, 5, lerp(cl[2], (90, 84, 78), .3))
    for x in range(3, 29): s.set_at((x, 14), (*OUT, 200))             # front edge (3/4 thickness)
    return s
def banner(v, th):
    cl = CLOTH[["red", "blue", "green"][v % 3]]; s = surf(T, 24); r = rr(v + 40); gold = (176, 140, 72)
    line(s, WOOD[3], (1, 0), (14, 0)); line(s, WOOD[1], (1, 1), (14, 1)); s.set_at((0, 1), WOOD[2]); s.set_at((15, 1), WOOD[2])
    tear = [r.randrange(15, 22) for _ in range(12)]; tear = [round((tear[i - 1] + 2 * tear[i] + tear[(i + 1) % 12]) / 4) for i in range(12)]
    for x in range(2, 14):
        for y in range(2, tear[x - 2]):
            c = cl[1]
            if x in (3, 12): c = gold
            elif x == 2 or x == 13: c = cl[0]
            elif x < 6: c = cl[2] if (x + y) % 2 else cl[1]                 # lit fold
            c = weave(c, x, y, True)
            if r.random() < .04: continue                                  # moth holes
            s.set_at((x, y), c)
    club(s, 5, 7, lerp(gold, cl[1], .15))
    return outline(s)
def tapestry(v, th):
    cl = CLOTH[["blue", "red"][v % 2]]; s = surf(32, 24); r = rr(v + 50); gold = (176, 140, 72)
    line(s, WOOD[1], (0, 1), (31, 1)); line(s, WOOD[3], (0, 0), (31, 0))
    for x in range(1, 31):
        bot = 20 - (r.randrange(1, 7) if x > 19 + v * 3 else 0)
        for y in range(2, bot):
            c = cl[1]
            if y in (3, bot - 2) or x in (2, 29): c = gold
            elif 6 < y < bot - 4 and 6 < x < 26 and ((x - 6) // 3 + (y - 6) // 3) % 2 == 0: c = cl[2]
            c = weave(c, x, y, True)
            if x > 22 and r.random() < .12: c = lerp(c, (60, 56, 60), .6)    # scorched/faded corner
            s.set_at((x, y), lerp(c, (90, 86, 90), .2))
        for k in range(2): s.set_at((x, bot + k), lerp(gold, (60, 56, 50), .3 + k * .3)) if x % 2 else None   # fringe
    club(s, 13, 8, lerp(gold, cl[1], .2))
    for y in range(2, 21): s.set_at((1, y), lerp(cl[0], (0, 0, 0), .3))              # fold shadow
    return outline(s)
def sconce(lit, f=0):
    s = surf(T, T); I = [(40, 38, 46), (70, 68, 78), (110, 108, 118), (150, 148, 156)]
    pygame.draw.rect(s, I[1], (6, 9, 4, 5)); line(s, I[3], (6, 9), (6, 13)); line(s, I[0], (9, 10), (9, 13)); line(s, I[0], (7, 14), (8, 15))
    pygame.draw.polygon(s, I[2], [(3, 7), (12, 7), (10, 10), (5, 10)]); line(s, I[3], (4, 7), (11, 7))
    if lit:
        fl = [(255, 236, 160), (255, 180, 70), (220, 96, 34)]; h = [6, 7, 5, 6][f]; sw = [0, 1, 0, -1][f]
        for y in range(h):
            w = max(0, 2 - y // 2)
            for x in range(-w, w + 1): s.set_at((7 + x + (sw if y > 2 else 0), 6 - y), fl[min(2, abs(x) + (y > h - 2))])
        s.set_at((7 + sw, 6 - h), fl[2])
    else:
        pygame.draw.rect(s, (200, 190, 170), (6, 3, 3, 4)); line(s, (230, 222, 206), (6, 3), (6, 6)); s.set_at((7, 2), OUT); line(s, (200, 190, 170), (8, 7), (8, 8))  # cold candle stub w/ drip
    return outline(s)
def dust(v, th):
    s = surf(T, T); d = TH[th]["dust"]; r = rr(v + 110)
    cs = [(8 + r.uniform(-2, 2), 8 + r.uniform(-1, 1), r.uniform(4, 7), r.uniform(2.5, 4)) for _ in range(3)]
    for y in range(T):
        for x in range(T):
            f = max(1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2 for cx, cy, rx, ry in cs) + (r.random() - .5) * .35
            if f > 0 and BAYER[y % 4][x % 4] / 16 < f * .9: s.set_at((x, y), (*d, 80 + int(min(1, f) * 70)))
    for k in range(3): x, y = r.randrange(3, 13), r.randrange(4, 12); s.set_at((x, y), (*lerp(d, (255, 250, 240), .3), 200))   # footprints of grit
    return s
def leaves(v, th):
    s = surf(T, T); r = rr(v + 120); cols = [[(110, 66, 30), (160, 104, 44), (204, 150, 70)], [(90, 90, 36), (130, 128, 52), (176, 170, 80)], [(120, 50, 30), (170, 80, 40), (210, 120, 60)]]
    for k in range(3):
        x, y = r.randrange(2, 12), r.randrange(3, 12); c = cols[(k + v) % 3]; flip = r.random() < .5
        shadow(s, x + 1.5, y + 2.5, 2.5, 1, 90)
        u = surf(6, 5)
        for (i, j, t) in ((1, 1, 2), (2, 1, 1), (3, 2, 1), (2, 2, 1), (1, 2, 0), (4, 2, 1), (3, 3, 0), (2, 3, 0)): u.set_at((i, j), c[t])
        u.set_at((0, 1), c[0]); u = outline(u)
        if flip: u = pygame.transform.flip(u, True, False)
        s.blit(u, (x - 1, y - 1))
    return s
def chair_toppled(v, th):
    s = surf(20, 16); shadow(s, 10, 13, 9, 2.5); u = surf(20, 16)
    pygame.draw.polygon(u, WOOD[1], [(1, 6), (8, 4), (9, 12), (2, 13)])                 # chair back lying flat (slats)
    for k in range(3): line(u, WOOD[0], (2 + k * 2, 6 - k // 2), (3 + k * 2, 12 - k // 2))
    line(u, WOOD[3], (1, 6), (8, 4))
    pygame.draw.polygon(u, WOOD[2], [(8, 7), (14, 6), (14, 10), (8, 12)]); line(u, WOOD[3], (8, 7), (14, 6))   # seat, edge-on
    for (a_, b_) in (((14, 6), (19, 3 + v)), ((14, 10), (19, 8)), ((12, 7), (16, 2))):                  # legs sticking up/out
        line(u, WOOD[1], a_, b_, 2); u.set_at(b_, WOOD[3])
    if v: line(u, (14, 10, 18), (4, 7), (6, 11))                                                         # split slat
    s.blit(outline(u), (0, 0)); return s
def crate_broken(v, th):
    s = surf(T, 20)
    pygame.draw.rect(s, WOOD[1], (2, 7, 12, 11)); pygame.draw.rect(s, WOOD[2], (2, 4, 12, 4)); line(s, WOOD[3], (2, 4), (13, 4))
    for x in (2, 13): line(s, WOOD[0], (x, 7), (x, 17))
    line(s, WOOD[0], (3, 12), (12, 12))
    pygame.draw.polygon(s, (14, 10, 18), [(6, 8), (11, 9), (9, 15), (5, 13)] if v == 0 else [(8, 4), (13, 4), (13, 10)])
    line(s, WOOD[2], (10, 2), (15, 6))                       # sprung plank
    o = surf(16, 20); shadow(o, 8, 18, 7.5, 2); o.blit(outline(s), (0, -1)); return o
def rubble_heap(v, th):
    s = surf(T, 18); p = TH[th]["st"]; r = rr(v + 130); shadow(s, 8, 15.5, 7.5, 2.2)
    u = surf(T, 18)
    for (x, y, w, h) in ([(1, 11, 5, 4), (9, 11, 5, 4), (5, 9, 6, 4), (3, 6, 4, 3), (8, 5, 5, 4), (6, 2, 4, 3)] if v == 0 else
                         [(2, 11, 6, 4), (9, 10, 5, 5), (4, 7, 5, 4), (9, 6, 4, 3), (6, 3, 4, 3)]):
        stone(u, x, y, w, h, p)
    s.blit(u, (0, 0)); return s
# ---------- registry: name, fn, (w,h), layer, rule, blocking, themes, variants, max/room, weight
P = [
 ("crack", crack, (16, 16), "wall decal", "wall-face", False, ["indoor", "dungeon"], 3, 2, 3),
 ("missing_stone", missing_stone, (16, 16), "wall decal", "wall-face", False, ["indoor", "dungeon", "garden"], 2, 1, 2),
 ("moss_vines", moss, (16, 24), "wall decal", "wall-face (top of face, hangs down)", False, ["garden", "dungeon", "indoor"], 3, 2, 2),
 ("cobweb", cobweb, (16, 16), "wall decal", "wall-top-corner (top-left inner corner; mirror for top-right)", False, ["indoor", "dungeon"], 3, 2, 3),
 ("banner_torn", banner, (16, 24), "wall decal", "wall-face", False, ["indoor"], 3, 1, 1),
 ("tapestry_torn", tapestry, (32, 24), "wall decal", "wall-face (2 cells wide)", False, ["indoor"], 2, 1, 1),
 ("rubble", rubble, (16, 16), "floor decal", "wall-base or floor-open", False, ["indoor", "dungeon", "garden"], 3, 2, 3),
 ("debris", debris, (16, 16), "floor decal", "floor-open or near-doorway", False, ["indoor", "dungeon"], 3, 2, 2),
 ("puddle", puddle, (16, 16), "floor decal", "floor-open or wall-base", False, ["dungeon", "indoor", "garden"], 3, 1, 2),
 ("bones", bones, (16, 16), "floor decal", "floor-open or wall-base", False, ["dungeon"], 3, 2, 2),
 ("broken_furniture", broken_furn, (16, 16), "floor decal", "floor-open or wall-base", False, ["indoor"], 3, 2, 2),
 ("rug_faded", rug, (32, 16), "floor decal", "floor-open (2x1 cells, centre of room)", False, ["indoor"], 2, 1, 1),
 ("dust", dust, (16, 16), "floor decal", "floor-open or wall-base", False, ["indoor", "dungeon"], 3, 3, 3),
 ("leaves", leaves, (16, 16), "floor decal", "floor-open", False, ["garden"], 3, 3, 3),
 ("chair_toppled", chair_toppled, (20, 16), "object", "floor-open or wall-base", True, ["indoor"], 2, 1, 1),
 ("crate_broken", crate_broken, (16, 20), "object", "wall-base", True, ["indoor", "dungeon"], 2, 1, 1),
 ("rubble_heap", rubble_heap, (16, 18), "object", "wall-base or floor-open", True, ["indoor", "dungeon", "garden"], 2, 1, 1),
]
man = {"tile_px": T, "notes": "Blocking objects have a small contact shadow BAKED IN (shadow_baked: true) - do not add a game shadow for them. Each file is a horizontal strip of variants (or animation frames for sconces). Decals: no outline/shadow, draw on the floor/wall layer after the baked room. Objects: dark outline baked, depth-sorted like other sprites. No glow baked; the game adds sconce light.",
       "anchors": {"floor decal": "top-left of the cell", "wall decal": "top-left of the wall FACE (just below the wall top) for wall-face; top-left of the inner corner floor cell for wall-top-corner", "object": "bottom-centre at the bottom edge of the footprint cell (x*16+8, y*16+16)"},
       "props": []}
SHEETS = {}
for name, fn, (w, h), layer, rule, block, themes, nv, mx, wt in P:
    pal_dep = name in ("crack", "missing_stone", "moss_vines", "rubble", "debris", "puddle", "dust", "rubble_heap")
    for th in (themes if pal_dep else [themes[0]]):
        S = surf(w * nv, h)
        for v in range(nv): S.blit(fn(v, th), (v * w, 0))
        f = f"{name}_{th}.png" if pal_dep else f"{name}.png"; pygame.image.save(S, os.path.join(HERE, f)); SHEETS[(name, th)] = S
        man["props"].append({"file": f, "name": name, "frame_size": [w, h], "variants": nv, "layer": layer, "placement": rule, "blocking": block,
                             "footprint_tiles": [1, 1] if block else None, "shadow_baked": block or name in ("rubble", "debris", "bones", "broken_furniture", "leaves", "rug_faded"), "themes": [th] if pal_dep else themes, "max_per_room": mx, "weight": wt,
                             "anchor": man["anchors"][layer]})
# sconces
for nm, frames in (("sconce_lit", [sconce(True, f) for f in range(4)]), ("sconce_unlit", [sconce(False)])):
    S = surf(T * len(frames), T)
    for i, f in enumerate(frames): S.blit(f, (i * T, 0))
    pygame.image.save(S, os.path.join(HERE, nm + ".png")); SHEETS[(nm, "indoor")] = S
    man["props"].append({"file": nm + ".png", "name": nm, "frame_size": [T, T], "frames": len(frames), "fps": 8 if len(frames) > 1 else 0, "loop": len(frames) > 1,
                         "layer": "wall decal", "placement": "wall-face (front face, centred)", "blocking": False, "themes": ["indoor", "dungeon"],
                         "max_per_room": 2, "weight": 2, "anchor": man["anchors"]["wall decal"], "light": "lit: game adds a warm point light ~(x+7, y+4)" if len(frames) > 1 else "none"})
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---------- contact sheet
font = pygame.font.Font(None, 18); Z = 4; rows = list(SHEETS.items())
P2 = pygame.Surface((1400, 30 + ((len(rows) + 1) // 2) * (24 * Z + 26))); P2.fill((40, 36, 48))
for i, ((nm, th), S) in enumerate(rows):
    X = 10 + (i % 2) * 700; Y = 10 + (i // 2) * (24 * Z + 26)
    b = pygame.Surface(S.get_size()); b.fill({"garden": (60, 92, 38), "dungeon": (34, 31, 34)}.get(th, (66, 62, 70))); b.blit(S, (0, 0))
    P2.blit(font.render(f"{nm} [{th}]", True, (230, 220, 200)), (X, Y)); P2.blit(pygame.transform.scale(b, (S.get_width() * Z, S.get_height() * Z)), (X, Y + 16))
pygame.image.save(P2, os.path.join(HERE, "preview_contact.png"))
# ---------- mock rooms: real baked rooms + a light sprinkle
cwd = os.getcwd(); os.chdir(GAME); import main; R = main.load_rooms(); os.chdir(cwd)
def mock(rid, places):
    room = R[rid]; raw, TOP = art3.bake_room(rid, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255)); base = pygame.Surface(raw.get_size()); base.fill((20, 16, 26)); base.blit(raw, (0, 0))
    for nm, th, v, cx, cy, kind in places:
        S = SHEETS[(nm, th)]; w, h = S.get_width() // (4 if nm == "sconce_lit" else 1) if False else None, None
        ent = next(p for p in man["props"] if p["file"] in (f"{nm}_{th}.png", f"{nm}.png"))
        fw, fh = ent["frame_size"]; spr = S.subsurface((v * fw, 0, fw, fh))
        X, Y = cx * T, cy * T + TOP
        if kind == "wallface": Y = cy * T + TOP - 14 + 0
        if kind == "obj": X, Y = cx * T + 8 - fw // 2, cy * T + TOP + 16 - fh
        if kind == "mirror": spr = pygame.transform.flip(spr, True, False)
        base.blit(spr, (X, Y))
    return base
M = [("indoor (room 5)", mock(5, [("cobweb", "indoor", 1, 2, 2, "floor"), ("crack", "indoor", 0, 6, 2, "wallface"), ("sconce_lit", "indoor", 0, 12, 2, "wallface"),
                                 ("dust", "indoor", 0, 9, 9, "floor"), ("rug_faded", "indoor", 0, 10, 8, "floor"), ("chair_toppled", "indoor", 0, 19, 13, "obj"), ("rubble", "indoor", 1, 20, 3, "floor")])),
     ("garden (room 18)", mock(18, [("leaves", "garden", 0, 6, 4, "floor"), ("leaves", "garden", 2, 16, 14, "floor"), ("rubble", "garden", 0, 20, 9, "floor"), ("puddle", "garden", 1, 8, 9, "floor")])),
     ("dungeon (room 82)", mock(82, [("bones", "dungeon", 2, 16, 8, "floor"), ("puddle", "dungeon", 0, 19, 9, "floor"), ("cobweb", "indoor", 0, 14, 7, "floor"), ("crate_broken", "indoor", 0, 14, 9, "obj"), ("moss_vines", "dungeon", 1, 18, 7, "wallface"), ("dust", "dungeon", 1, 8, 8, "floor")]))]
CROPS = [pygame.Rect(0, 0, 192, 150), pygame.Rect(32, 40, 192, 150), pygame.Rect(176, 100, 192, 150)]
P3 = pygame.Surface((10 + 192 + 20 + 384 + 10, 3 * (300 + 30) + 10)); P3.fill((40, 36, 48)); y = 6
for i, (lab, m) in enumerate(M):
    P3.blit(font.render(lab + "  (whole room scaled down | detail 2x)", True, (230, 220, 200)), (10, y))
    P3.blit(pygame.transform.scale(m, (192, round(192 * m.get_height() / m.get_width()))), (10, y + 18))
    P3.blit(pygame.transform.scale(m.subsurface(CROPS[i]), (384, 300)), (222, y + 18)); y += 330
pygame.image.save(P3, os.path.join(HERE, "preview_rooms.png"))
print("ok", len(man["props"]))
