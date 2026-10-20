"""Room 14 Large Throne ('%' block x10-13, y3-4 0-based) + dais + royal carpet runner. python3 make_throne.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp, club_shape
GOLD = [(96, 60, 20), (150, 104, 34), (204, 156, 58), (240, 204, 110), (255, 240, 190)]
VEL = [(60, 12, 26), (96, 22, 40), (132, 36, 54), (170, 64, 76)]
STN = [(60, 56, 66), (88, 84, 96), (118, 112, 124), (156, 150, 160)]
RUBY, SAPH, EMER = (210, 40, 60), (70, 120, 230), (50, 180, 110); SH = (10, 8, 16)
FW, FH = 72, 80; AX, AY = 36, 79          # footprint 64x32 at the bottom (+4px each side for dais lip); 48px headroom for the tall back
def shade_rect(s, r, pal, lit=.75):
    for y in range(r.top, r.bottom):
        for x in range(r.left, r.right):
            v = lit - (x - r.left) / max(1, r.width) * .3 - (y - r.top) / max(1, r.height) * .2 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            s.set_at((x, y), pal[max(0, min(len(pal) - 1, int(v * len(pal))))])
GEMS = []                                             # gem positions (for the glint strip)
def gem(u, x, y, c, big=False):
    hi = lerp(c, (255, 255, 255), .6); dk = lerp(c, (0, 0, 0), .45)
    if big:
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)): u.set_at((x + dx, y + dy), c)
        u.set_at((x, y), c); u.set_at((x - 1, y - 1), OUT); u.set_at((x + 1, y + 1), OUT); u.set_at((x + 1, y - 1), OUT); u.set_at((x - 1, y + 1), OUT)
        u.set_at((x, y - 1), hi); u.set_at((x + 1, y), dk); u.set_at((x, y + 1), dk)
    else: u.set_at((x, y), c); u.set_at((x - 1, y), hi) if x > 0 else None
    GEMS.append((x, y))
def throne():
    GEMS.clear(); s = surf(FW, FH)
    for y in range(FH - 9, FH):                                            # baked contact shadow
        for x in range(FW):
            d = ((x - 36) / 35) ** 2 + ((y - (FH - 4)) / 5) ** 2
            if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, 120))
    u = surf(FW, FH)
    # banners hanging from the outer posts (club-red with gold trim + fringe)
    for bx in (1, 63):
        r = pygame.Rect(bx, 12, 8, 26); shade_rect(u, r, VEL, .8)
        pygame.draw.polygon(u, (0, 0, 0, 0), [(bx, 38), (bx + 4, 33), (bx + 8, 38)])
        for y in range(33, 38):
            for x in range(bx, bx + 8):
                if y - 33 > 4 - abs(x - bx - 3.5) * 1.2: u.set_at((x, y), (0, 0, 0, 0))
        line(u, GOLD[3], (bx, 12), (bx + 7, 12)); line(u, GOLD[2], (bx, 13), (bx, 33)); line(u, GOLD[2], (bx + 7, 13), (bx + 7, 33))
        cl = surf(8, 8); club_shape(cl, 4, 3, 1.6, GOLD[3]); u.blit(cl, (bx, 16))
        line(u, GOLD[1], (bx - 1 if bx else 0, 11), (bx + 8, 11))                        # rod
    # dais: two gilt-trimmed stone steps
    for i, (top, h, inset) in enumerate(((63, 10, 0), (55, 8, 7))):
        r = pygame.Rect(1 + inset, top, FW - 2 - inset * 2, h); shade_rect(u, r, STN, .72 - i * .05)
        line(u, GOLD[4], (r.left, r.top), (r.right - 1, r.top)); line(u, GOLD[2], (r.left, r.top + 1), (r.right - 1, r.top + 1)); line(u, GOLD[0], (r.left, r.top + 2), (r.right - 1, r.top + 2))
        line(u, STN[0], (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1))
        for x in range(r.left + 3, r.right - 3, 6):                                   # carved rosettes on the riser
            u.set_at((x, r.top + 5), GOLD[2]); u.set_at((x, r.top + 4), GOLD[3]); u.set_at((x + 1, r.top + 5), GOLD[0])
        gem(u, r.left + 2, r.top + 5, SAPH); gem(u, r.right - 3, r.top + 5, SAPH)
    pygame.draw.rect(u, VEL[1], (28, 55, 16, 18)); line(u, VEL[3], (28, 55), (43, 55)); line(u, VEL[3], (28, 63), (43, 63))
    line(u, GOLD[3], (28, 55), (28, 72)); line(u, GOLD[3], (43, 55), (43, 72))
    # tall carved back with a pointed gothic crest
    pts = [(17, 46), (17, 14), (26, 8), (32, 5), (36, 1), (40, 5), (46, 8), (55, 14), (55, 46)]
    pygame.draw.polygon(u, GOLD[2], pts)
    for y in range(0, 47):
        for x in range(17, 56):
            if u.get_at((x, y))[:3] == GOLD[2]:
                v = .82 - (x - 17) / 38 * .3 - y / 46 * .15 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
                u.set_at((x, y), GOLD[max(0, min(4, int(v * 5)))])
    inner = [(22, 44), (22, 17), (29, 12), (36, 7), (43, 12), (50, 17), (50, 44)]
    pygame.draw.polygon(u, GOLD[0], [(p[0] - 1, p[1] - 1) if p[0] < 36 else (p[0] + 1, p[1] - 1) for p in inner])   # carved recess
    pygame.draw.polygon(u, VEL[1], inner)
    for y in range(6, 45):                                                            # velvet damask: diamond lattice + fleur dots
        for x in range(22, 51):
            if u.get_at((x, y))[:3] != VEL[1]: continue
            lx, ly = x - 36, y - 10
            c = VEL[1]
            if (lx + ly) % 8 == 0 or (lx - ly) % 8 == 0: c = VEL[0]
            if lx % 8 == 4 and ly % 8 == 0: c = VEL[3]
            if (lx % 8 == 4 and ly % 8 in (7, 1)) or (lx % 8 in (3, 5) and ly % 8 == 0): c = VEL[2]
            if x < 25: c = lerp(c, VEL[3], .25)                                       # rim light from the left
            u.set_at((x, y), c)
    for p, q in zip(pts[1:-2], pts[2:-1]): line(u, GOLD[4], p, q) if p[0] < 36 else None   # lit crest edge
    line(u, GOLD[4], (17, 14), (17, 45))
    for y in range(18, 44, 4): u.set_at((19, y), GOLD[4]); u.set_at((53, y), GOLD[1])   # bead moulding
    gem(u, 36, 10, RUBY, True); gem(u, 19, 16, EMER); gem(u, 53, 16, EMER); gem(u, 19, 42, RUBY); gem(u, 53, 42, RUBY)
    for (gx, gy) in ((27, 11), (45, 11)): gem(u, gx, gy, SAPH)
    cl = surf(16, 16); club_shape(cl, 8, 6, 3.2, GOLD[3]); u.blit(outline(cl), (28, 17))   # club crest
    gem(u, 36, 22, RUBY)
    # crown finial on the spire
    cr = surf(14, 9); pygame.draw.polygon(cr, GOLD[3], [(1, 8), (1, 3), (4, 5), (7, 1), (10, 5), (13, 3), (13, 8)]); line(cr, GOLD[4], (1, 7), (12, 7)); line(cr, GOLD[0], (1, 8), (13, 8))
    u.blit(outline(cr), (29, -2)); gem(u, 36, 4, RUBY); gem(u, 32, 5, SAPH); gem(u, 40, 5, SAPH)
    # side posts with orb finials
    for fx in (12, 56):
        pygame.draw.rect(u, GOLD[1], (fx, 12, 4, 40)); line(u, GOLD[4] if fx < 36 else GOLD[3], (fx, 12), (fx, 51))
        for y in range(16, 50, 5): line(u, GOLD[0], (fx, y), (fx + 3, y))           # carved rings
        blob(u, fx + 2, 9, 3.2, 3.2, GOLD[1:]); u.set_at((fx + 1, 7), GOLD[4]); gem(u, fx + 2, 4, RUBY); u.set_at((fx + 2, 5), GOLD[2])
    # seat
    seat = pygame.Rect(18, 42, 37, 7); shade_rect(u, seat, VEL, .95); line(u, VEL[3], (18, 42), (54, 42))
    for x in range(22, 52, 6): u.set_at((x, 45), GOLD[3])                            # tufting
    # scrolled apron
    ap = pygame.Rect(17, 49, 39, 7); shade_rect(u, ap, GOLD, .62); line(u, GOLD[4], (17, 49), (55, 49)); line(u, GOLD[0], (17, 55), (55, 55))
    for cx in (21, 51):
        pygame.draw.circle(u, GOLD[0], (cx, 52), 2, 1); u.set_at((cx - 1, 51), GOLD[4])   # volutes
    for i, x in enumerate(range(26, 48, 5)): gem(u, x, 52, (RUBY, SAPH, EMER, SAPH, RUBY)[i])
    # lion/griffin arms: paw base + roaring head with mane
    for ax, fl in ((7, 1), (57, -1)):
        arm = pygame.Rect(ax, 34, 9, 20); shade_rect(u, arm, GOLD, .8 if fl > 0 else .6); line(u, GOLD[4], (ax, 34), (ax + 8, 34))
        hd = surf(14, 14); cx = 7
        blob(hd, cx, 7, 6, 5.5, [GOLD[0], GOLD[1], GOLD[2]])                            # mane (darker ring)
        for k in range(8):
            t = k / 8 * 6.283; hd.set_at((int(cx + math.cos(t) * 5), int(7 + math.sin(t) * 5)), GOLD[0])
        blob(hd, cx + fl, 8, 3.4, 3.2, GOLD[2:])                                         # face
        hd.set_at((cx + fl - 1, 7), OUT); hd.set_at((cx + fl + 1, 7), OUT)                 # eyes
        hd.set_at((cx + fl, 9), GOLD[0]); line(hd, OUT, (cx + fl - 1, 11), (cx + fl + 1, 11))   # nose, mouth
        hd.set_at((cx + fl - 2, 6), GOLD[4])
        u.blit(outline(hd), (ax + 4 - 7, 31 - 8)); GEMS.append((ax + 4 + fl, 30))
        for y in range(38, 52, 3): u.set_at((ax + 1, y), GOLD[4] if fl > 0 else GOLD[2])
        for k in range(3): u.set_at((ax + 2 + k * 2, 53), GOLD[0]); u.set_at((ax + 2 + k * 2, 52), GOLD[3])  # paw toes
    s.blit(outline(u), (0, 0))
    r = random.Random(14)                                                            # dust, wear, a cobweb
    for k in range(26):
        x, y = r.randrange(6, 66), r.randrange(40, 74)
        c = s.get_at((x, y))
        if c.a == 255 and c[:3] != OUT: s.set_at((x, y), lerp(c[:3], (150, 142, 132), .55))
    for k in range(3): line(s, (200, 196, 206, 90), (55, 15), (55 - k * 2, 19 + k))
    for x in (30, 31, 33): s.set_at((x, 70), (60, 56, 64))                          # chipped step
    return s
def glints():
    """4-frame gem glint strip (same 72x80 frame), additive-friendly: transparent except small star sparkles on a rotating subset of gems"""
    S = surf(FW * 4, FH)
    for f in range(4):
        for i, (x, y) in enumerate(GEMS):
            if i % 4 != f: continue
            ox = f * FW
            for dx, dy, a in ((0, 0, 255), (-1, 0, 160), (1, 0, 160), (0, -1, 160), (0, 1, 160), (-2, 0, 70), (2, 0, 70), (0, -2, 70), (0, 2, 70)):
                if 0 <= x + dx < FW and 0 <= y + dy < FH: S.set_at((ox + x + dx, y + dy), (255, 250, 220, a))
    return S
def carpet(n):
    """royal runner 32 px wide x n tiles, not blocking; club motif + gold border, faded and frayed at the far end"""
    W, H = 32, n * 16; s = surf(W, H); r = random.Random(14)
    for y in range(H):
        for x in range(1, W - 1):
            c = VEL[1] if (x // 2 + y) % 4 else VEL[0]
            if x in (2, W - 3): c = GOLD[2]
            elif x in (3, W - 4): c = GOLD[0]
            c = lerp(c, (80, 74, 70), .15 + y / H * .2 + r.random() * .05)
            if y > H - 4 and r.random() < .4: continue                                                       # frayed end
            s.set_at((x, y), (*c, 255))
    for k in range(2, n, 3):
        cl = surf(16, 16); club_shape(cl, 8, 6, 2, lerp(GOLD[3], (90, 80, 70), .3)); s.blit(cl, (8, k * 16 - 6))
    return s
T_ = throne(); pygame.image.save(T_, os.path.join(HERE, "throne.png")); GL = glints(); pygame.image.save(GL, os.path.join(HERE, "throne_glint.png"))
CP = carpet(10); pygame.image.save(CP, os.path.join(HERE, "throne_carpet.png"))
json.dump({"room": 14, "room_name": "Throne Room", "glyphs": "'%' x10,x13 y3-4 and '-' x11-12 y4 (0-based) = 4x2 block",
  "pieces": {"throne.png": {"frame_size": [FW, FH], "footprint_tiles": [4, 2], "anchor": {"px": [AX, AY], "desc": "bottom-centre of the 4x2 block: world (10*16 + 32, (3+2)*16) = (192, 80); frame top-left (156, 1)"},
             "blocking": "all 8 block cells ('%' and the '-' between)", "depth_sort_y": "(3+2)*16 = 80", "shadow_baked": True, "replaces": "procedural '%' furniture in room 14",
             "design": "v2 (more ornate, issue #2 comment): pointed carved gilt back with crown finial, inset rubies/sapphires/emeralds catching left rim light, damask velvet back, club crest, orb-finial posts, roaring lion arms, scrolled jewelled apron, gold-trimmed dais steps with rosettes, hanging club banners, dust/cobweb/chipped step"},
             "throne_glint.png": {"frame_size": [FW, FH], "frames": 4, "anchor": {"px": [AX, AY]}, "optional": True, "layer": "drawn over throne.png at the same position, additive or alpha", "fps": 3, "desc": "small gem sparkles cycling over a quarter of the gems per frame; no bloom"},
             "throne_carpet.png": {"frame_size": [32, 160], "anchor": "top-left of cell (11, 5)", "footprint_tiles": [2, 10], "blocking": False, "layer": "floor decal",
             "placement": "runner from the dais to the south door: cells x11-12, y5-14", "optional": True}}},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
b, TOP = baked(14)
b.blit(CP, (11 * 16, 5 * 16 + TOP)); b.blit(T_, (10 * 16 + 32 - AX, 5 * 16 + TOP - AY))
P = pygame.transform.scale(b.subsurface((96, 0, 192, 200)), (576, 600)); pygame.image.save(P, os.path.join(HERE, "preview.png"))
old = pygame.image.load("/tmp/throne_old.png") if os.path.exists("/tmp/throne_old.png") else T_
C = pygame.Surface((FW * 2 * 4 + 30, FH * 4 + 20)); C.fill((40, 36, 48))
C.blit(pygame.transform.scale(old, (FW * 4, FH * 4)), (10, 10)); C.blit(pygame.transform.scale(T_, (FW * 4, FH * 4)), (FW * 4 + 20, 10))
pygame.image.save(C, os.path.join(HERE, "preview_compare.png")); copy_to_game(HERE, "throne"); print("ok")
