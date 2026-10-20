"""spiral staircases: large central (rooms 7 up / 23 down, 2x2) and corner (rooms 4/5 up, 1x1). python3 make_spiral.py
Same palettes as art/stairs (art.py STONE indoor). 3/4 view, thick ink outline, rim light, baked contact shadow (flagged)."""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import STONE, lerp
INK = (16, 10, 16)
TOPC = [STONE["top2"], STONE["top"], (120, 114, 124), STONE["rim"]]
TREAD = [(86, 82, 96), (112, 106, 120), (138, 132, 146), (166, 160, 172), (196, 190, 200)]   # treads a notch lighter than the floor so the steps pop
RIS = [(40, 37, 48), STONE["face2"], STONE["face"]]
VOID = (14, 12, 20); MORT = STONE["mortar"]; MOSS = STONE["moss"]; SH = (8, 6, 12)
YS = .82                                                                  # 3/4 squash of the circle
def P(cx, cy, r, th, h): return (cx + r * math.cos(th), cy + r * math.sin(th) * YS - h)
def poly_fill(s, pts, col, clip=None):
    pygame.draw.polygon(s, col, [(round(x), round(y)) for x, y in pts])
def wedge(cx, cy, r0, R, a0, a1, h, n=6):
    outer = [P(cx, cy, R, a0 + (a1 - a0) * i / n, h) for i in range(n + 1)]
    inner = [P(cx, cy, r0, a1 - (a1 - a0) * i / n, h) for i in range(n + 1)]
    return outer + inner, outer
def shadow(s, cx, cy, rx, ry, a=120):
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, a))
def newel(u, cx, ytop, ybot, w):
    pygame.draw.rect(u, RIS[1], (cx - w // 2, ytop, w, ybot - ytop)); line(u, TOPC[3], (cx - w // 2, ytop), (cx - w // 2, ybot - 1))
    line(u, RIS[0], (cx + w // 2 - (0 if w % 2 else 1), ytop), (cx + w // 2 - (0 if w % 2 else 1), ybot - 1))
    for y in range(ytop + 4, ybot, 5): line(u, MORT, (cx - w // 2 + 1, y), (cx + w // 2 - 1, y))
    blob(u, cx, ytop, w / 2 + 1, w / 3 + 1, [RIS[1], TOPC[1], TOPC[2], TOPC[3]])                         # cap
C_ = 1.0                                                                    # nearness = Z + h*YS (oblique projection)
class ZB:
    """tiny z-buffer: each primitive is a polygon (or rect) with a per-pixel 'nearness' function; the nearest wins. ids give ink seams"""
    def __init__(s, W, H): s.W, s.H = W, H; s.z = [[-1e9] * W for _ in range(H)]; s.c = [[None] * W for _ in range(H)]; s.id = [[-1] * W for _ in range(H)]; s.n = 0
    def prim(s, pts, colfn, keyfn):
        m = pygame.Surface((s.W, s.H), pygame.SRCALPHA); m.fill((0, 0, 0, 0))
        if len(pts) >= 3: pygame.draw.polygon(m, (255, 255, 255), [(round(x), round(y)) for x, y in pts])
        s.n += 1; b = m.get_bounding_rect()
        for y in range(b.top, b.bottom):
            for x in range(b.left, b.right):
                if m.get_at((x, y)).a:
                    k = keyfn(x, y)
                    if k > s.z[y][x]: s.z[y][x] = k; s.c[y][x] = colfn(x, y); s.id[y][x] = s.n
    def out(s, ink=True):
        o = surf(s.W, s.H)
        for y in range(s.H):
            for x in range(s.W):
                if s.c[y][x] is None: continue
                c = s.c[y][x]
                if ink:
                    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < s.W and 0 <= ny < s.H and s.id[ny][nx] not in (-1, s.id[y][x]) and s.z[ny][nx] < s.z[y][x] - 1.5: c = INK; break
                o.set_at((x, y), (*c[:3], 255))
        return o
def dith_pick(pal, v, x, y): return pal[max(0, min(len(pal) - 1, int((v + (BAYER[y % 4][x % 4] / 16 - .5) * .25) * len(pal))))]
def helix(zb, cx, cy, R, r0, N, dA, rise, a_start, sgn, h0=0, th=None, dark=None, rail=True):
    th = th or 2                                                                # thin cantilevered treads: the gaps read as a spiral
    dk = dark or (lambda h: 0)
    for k in range(N):
        a0 = a_start + sgn * k * dA; a1 = a0 + sgn * dA; h = h0 + k * rise * (1 if h0 >= 0 else -1) if False else h0 + k * rise
        pts, outer = wedge(cx, cy, r0, R, a0, a1, h)
        am = (a0 + a1) / 2; lam = .5 - .5 * math.cos(am + .6); t = k / max(1, N - 1)
        def topcol(x, y, h=h, lam=lam, t=t, k=k, a0=a0, a1=a1):
            v = .45 + t * .45 - lam * .2 + (.06 if k % 2 else 0)
            c = dith_pick(TREAD, v, x, y)
            px, py = P(cx, cy, R - 1, (a0 + a1) / 2, h)
            return lerp(c, VOID, dk(h))
        zb.prim(pts, topcol, lambda x, y, h=h: ((y - cy + h) / YS) * C_ + h * YS)
        if h > 0 and math.sin(am) > -.2:                                                        # solid curved wall under the front treads, down to the floor
            under = outer + [(x, y + h) for x, y in reversed(outer)]
            zb.prim(under, lambda x, y, lam=lam, h=h: (MORT if (int(y + h) % 5 == 0) else dith_pick([RIS[0], RIS[1], RIS[2], STONE["face"]], .85 - lam * .75, x, y)),
                    lambda x, y, h=h: math.sqrt(max(0, R * R - (x - cx) ** 2)) + (h / 2) * YS - .6)
        face = outer + [(x, y + th) for x, y in reversed(outer)]                                  # outer stringer face (thickness)
        zb.prim(face, lambda x, y, h=h, lam=lam: lerp(dith_pick(RIS, .8 - lam * .7, x, y), VOID, dk(h)),
                lambda x, y, h=h: math.sqrt(max(0, R * R - (x - cx) ** 2)) * C_ + (h - th / 2) * YS - .2)
        lead = [P(cx, cy, r0, a1, h), P(cx, cy, R, a1, h), P(cx, cy, R, a1, h + rise), P(cx, cy, r0, a1, h + rise)]   # riser up to the next step
        zm = (r0 + R) / 2 * math.sin(a1)
        if k < N - 1: zb.prim(lead, lambda x, y, h=h: lerp(dith_pick(RIS, .55, x, y), VOID, dk(h)), lambda x, y, h=h, zm=zm: zm * C_ + (h + rise / 2) * YS - .4)
        if rail:
            px, py = P(cx, cy, R - .7, am, h); L = max(4, R * .45); zp = (R - .7) * math.sin(am)
            zb.prim([(px - .5, py), (px + .5, py), (px + .5, py - L), (px - .5, py - L)], lambda x, y: (98, 70, 46) if y > py - L + 1 else (140, 100, 62),
                    lambda x, y, zp=zp, h=h: zp * C_ + (h + 2) * YS + .5)
    if rail:
        pts = [P(cx, cy, R - .7, a_start + sgn * (k + .5) * dA, h0 + k * rise) for k in range(N)]
        for k, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
            L = max(4, R * .45); am = a_start + sgn * (k + 1) * dA; zp = (R - .7) * math.sin(am)
            zb.prim([(x0, y0 - L), (x1, y1 - L), (x1, y1 - L + 1.2), (x0, y0 - L + 1.2)], lambda x, y: (120, 84, 52),
                    lambda x, y, zp=zp, k=k: zp * C_ + (h0 + k * rise + L) * YS + 1)
def newel_z(zb, cx, cy, r0, htop, hbot, dk=lambda h: 0):
    yt, yb = cy - htop - 2, cy - hbot + r0 * YS
    zb.prim([(cx - r0, yt), (cx + r0, yt), (cx + r0, yb), (cx - r0, yb)],
            lambda x, y: lerp(TOPC[3] if x <= cx - r0 + .5 else RIS[0] if x >= cx + r0 - 1 else dith_pick(RIS, .75, x, y), VOID, dk(cy + r0 * YS - y)),
            lambda x, y: r0 * C_ + (cy + r0 * YS - y) * YS * .99)
def spiral_up(W, H, cx, cy, R, r0, N, dA, rise, a_start, flip=False, rail=True, seed=0):
    zb = ZB(W, H); sg = -1 if flip else 1
    helix(zb, cx, cy, R, r0, N, dA, rise, a_start, sg, rail=rail)
    top = (N - 1) * rise + 4
    newel_z(zb, cx, cy, r0, top, 0)
    capy = cy - top - 2
    zb.prim([(cx + r0 * 1.6 * math.cos(t), capy + r0 * .9 * math.sin(t)) for t in [i * math.pi / 6 for i in range(12)]], lambda x, y: TOPC[3] if x < cx else TOPC[2], lambda x, y: 999)
    s = surf(W, H); shadow(s, cx + 1, cy + 2, R + 1, R * YS + 2)
    s.blit(outline(zb.out()), (0, 0))
    r = random.Random(seed)
    for k in range(int(W * H / 60)):
        x, y = r.randrange(W), r.randrange(H); c = s.get_at((x, y))
        if c.a == 255 and c[:3] in (TOPC[1], TOPC[2]): s.set_at((x, y), lerp(c[:3], (150, 144, 136), .4) if k % 5 else MOSS)
    return s
def spiral_down(W, H, cx, cy, R, r0, N, dA, rise, a_start, seed=0):
    s = surf(W, H); u = surf(W, H); shadow(s, cx + 1, cy + 2, R + 2, R * YS + 3, 90)
    zb = ZB(W, H)
    depth = N * rise
    dk = lambda h: min(.92, max(0, (-h - 2) / depth) * .95)
    helix(zb, cx, cy, R - 2, r0, N, dA, -rise, a_start, 1, h0=-rise, rail=False, dark=dk)
    newel_z(zb, cx, cy, r0, -2, -depth - 6, dk)
    well = zb.out(ink=True)
    pygame.draw.ellipse(u, TOPC[1], (cx - R - 1, cy - R * YS - 1, 2 * R + 2, 2 * R * YS + 2))             # curb ring
    hole = surf(W, H); pygame.draw.ellipse(hole, (255, 255, 255), (cx - R + 2, cy - (R - 2) * YS, 2 * R - 4, 2 * (R - 2) * YS))
    for y in range(H):
        for x in range(W):
            if hole.get_at((x, y)).a:
                c = well.get_at((x, y)); u.set_at((x, y), c[:3] if c.a else VOID)
    pygame.draw.arc(u, INK, (cx - R + 2, cy - (R - 2) * YS, 2 * R - 4, 2 * (R - 2) * YS), 0, math.pi, 1)          # lip shadow (back inner edge)
    pygame.draw.arc(u, TOPC[3], (cx - R - 1, cy - R * YS - 1, 2 * R + 2, 2 * R * YS + 2), math.pi * .5, math.pi * 1.1, 1)
    pygame.draw.arc(u, TOPC[0], (cx - R - 1, cy - R * YS - 1, 2 * R + 2, 2 * R * YS + 2), math.pi * 1.5, math.pi * 2.05, 1)
    blob(u, cx, int(cy - 2), r0 + 1.5, r0 + .5, [RIS[1], TOPC[1], TOPC[2], TOPC[3]])                          # newel cap at floor level
    posts = []
    for i in range(7):
        a = math.pi + i * math.pi / 6; px, py = P(cx, cy, R, a, 0); posts.append((round(px), round(py - 6)))
        line(u, (98, 70, 46), (px, py), (px, py - 6))
    pygame.draw.lines(u, (120, 84, 52), False, posts); [u.set_at(p, (150, 108, 66)) for p in posts[:3]]
    s.blit(outline(u), (0, 0))
    r = random.Random(seed)
    for k in range(int(W * H / 70)):
        x, y = r.randrange(W), r.randrange(H); c = s.get_at((x, y))
        if c.a == 255 and c[:3] == TOPC[1]: s.set_at((x, y), lerp(c[:3], (150, 144, 136), .4) if k % 4 else MOSS)
    return s
OUTF = {}
def save(n, S): pygame.image.save(S, os.path.join(HERE, n)); OUTF[n] = S; return S
# large 2x2: footprint 32x32 at the frame bottom
L_UP = save("spiral_up_large.png", spiral_up(32, 60, 16, 45, 15.5, 2.4, 11, math.radians(28), 2.5, math.radians(0), seed=7))
L_DN = save("spiral_down_large.png", spiral_down(32, 40, 16, 24, 15.5, 2.2, 10, math.radians(36), 3, math.radians(-80), seed=23))
# corner 1x1 (room 4 = NE corner climbs clockwise toward the walls; room 5 mirrored)
C4 = save("spiral_up_corner.png", spiral_up(16, 30, 8, 23, 7.5, 1.3, 7, math.radians(44), 2.4, math.radians(0), rail=False, seed=4))
C5 = save("spiral_up_corner_mirror.png", pygame.transform.flip(C4, True, False))
PLACE = {4: ("spiral_up_corner.png", (20, 3), (1, 1), (8, 29)), 5: ("spiral_up_corner_mirror.png", (3, 3), (1, 1), (8, 29)),
         7: ("spiral_up_large.png", (11, 8), (2, 2), (16, 59)), 23: ("spiral_down_large.png", (11, 8), (2, 2), (16, 39)),
         50: ("spiral_up_large.png", (18, 8), (2, 2), (16, 59)), 61: ("spiral_up_large.png", (4, 8), (2, 2), (16, 59))}   # tower bases
man = {"issue": 9, "palette": "same as art/stairs indoor (art.py STONE)", "shadow_baked": True,
  "files": {"spiral_up_large.png": {"frame_size": [32, 60], "anchor": {"px": [16, 59]}, "glyph": "U 2x2", "desc": "helix of 13 wedge steps rising from the front around a central newel, with a handrail; rises 28 px above the block"},
            "spiral_down_large.png": {"frame_size": [32, 40], "anchor": {"px": [16, 39]}, "glyph": "D 2x2", "desc": "stairwell: curb ring, back balustrade, wedge steps winding down into darkness, newel cap"},
            "spiral_up_corner.png": {"frame_size": [16, 30], "anchor": {"px": [8, 29]}, "glyph": "U 1x1", "desc": "small spiral, 8 steps; curls up toward the NE corner"},
            "spiral_up_corner_mirror.png": {"frame_size": [16, 30], "anchor": {"px": [8, 29]}, "glyph": "U 1x1", "desc": "horizontal flip for the NW corner"}},
  "rooms": {str(rid): {"file": f, "block_topleft_cell": list(c), "footprint_tiles": list(fp), "anchor_px": list(a),
                       "world_anchor": [c[0] * 16 + fp[0] * 8, (c[1] + fp[1]) * 16], "blocking_trigger_cells": [[c[0] + i, c[1] + j] for j in range(fp[1]) for i in range(fp[0])],
                       "depth_sort_y": (c[1] + fp[1]) * 16, "layer": "depth-sorted sprite (it rises above the block; the hero must pass behind it on the row above)" if "up" in f else "floor layer (draw in place of the straight D tiles); the balustrade only rises 6 px, so depth-sort it at the block bottom if you prefer"}
            for rid, (f, c, fp, a) in PLACE.items()},
  "integration_notes": "for rooms 4, 5, 7, 23 (and 50, 61 for #20/#21 tower bases), skip the straight stair tiles (draw_stairs) and draw these at world_anchor; trigger, blocking and cooldown unchanged (the stair cells stay non-walkable triggers). The 1x1 dust strip is not used for these rooms"}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# previews on the real baked rooms: before (straight tiles) vs after
rows = []
for rid, (f, c, fp, a) in PLACE.items():
    b, TOP = baked(rid); af = b.copy()
    af.fill((0, 0, 0), (c[0] * 16, c[1] * 16 + TOP, fp[0] * 16, fp[1] * 16)); bk, _ = baked(rid)
    # restore floor under the block from a neighbouring floor cell, then the sprite
    flr = art3.bake_floor(rid, rooms()[rid], False)
    af.blit(flr, (c[0] * 16, c[1] * 16 + TOP), (c[0] * 16, c[1] * 16, fp[0] * 16, fp[1] * 16))
    S = OUTF[f]; af.blit(S, (c[0] * 16 + fp[0] * 8 - a[0], (c[1] + fp[1]) * 16 + TOP - a[1]))
    cw = pygame.Rect(c[0] * 16 - 40, c[1] * 16 + TOP - 56, fp[0] * 16 + 80, fp[1] * 16 + 90).clip(b.get_rect())
    rows.append((rid, pygame.transform.scale(b.subsurface(cw), (cw.w * 3, cw.h * 3)), pygame.transform.scale(af.subsurface(cw), (cw.w * 3, cw.h * 3))))
Wd = max(r[1].get_width() for r in rows) * 2 + 30; Ht = sum(r[1].get_height() + 10 for r in rows) + 10
Pv = pygame.Surface((Wd, Ht)); Pv.fill((40, 36, 48)); y = 10
for rid, bb, aa in rows: Pv.blit(bb, (10, y)); Pv.blit(aa, (20 + bb.get_width(), y)); y += bb.get_height() + 10
pygame.image.save(Pv, os.path.join(HERE, "preview.png"))
Z = pygame.Surface((32 * 2 + 16 * 2 + 50, 64)); Z.fill((66, 62, 70)); x = 6
for n in ("spiral_up_large.png", "spiral_down_large.png", "spiral_up_corner.png", "spiral_up_corner_mirror.png"): im = OUTF[n]; Z.blit(im, (x, 62 - im.get_height())); x += im.get_width() + 10
pygame.image.save(pygame.transform.scale(Z, (Z.get_width() * 6, Z.get_height() * 6)), os.path.join(HERE, "preview_sprites.png"))
copy_to_game(HERE, "spiral_stairs"); print("ok")
