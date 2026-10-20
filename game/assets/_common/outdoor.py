"""Shared outdoor pieces for #10 battlements and #11 tower tops: crenellated wall sheets (same layout as the room83 /
themed wall sheets), merlon posts, weathered floors, and the dusk 'view below' underlay (consistent with balcony_view)."""
import os, sys, math, random
import numpy as np
from monlib import *
from art import lerp
from art3 import FACE, vnoise, palettise
T = 16; SIDE = 8; MORTAR = (24, 20, 30); INK_ = (14, 10, 20)
HAZE = (46, 58, 76)                    # = balcony_view haze
DUSK = (112, 80, 104)                  # warm dusk glow toward the far (top) edge
GR = [(22, 40, 26), (32, 56, 32), (44, 74, 40), (60, 94, 50), (84, 118, 64)]
TREE = [(16, 32, 26), (28, 54, 36), (44, 78, 46), (70, 108, 60)]
FIELDS = [(44, 74, 40), (60, 94, 50), (118, 108, 58), (96, 84, 50), (84, 64, 44), (72, 98, 54), (104, 112, 62)]
WATER = [(30, 46, 66), (40, 62, 84), (70, 96, 120)]
# weathered outdoor stone: cooler, paler than the indoor walls, lichen accents
BST = [(108, 104, 104), (96, 94, 98), (120, 116, 112), (88, 86, 92), (112, 110, 104)]
LICHEN = [(150, 150, 70), (176, 160, 80), (120, 132, 64), (170, 110, 60)]

def stones(s, rect, rnd, tones, face=False, shade_to=(30, 26, 36), rowh=(5, 6, 6, 7), dark=.35):
    x0, y0, w, h = rect; clip = s.get_clip(); s.set_clip(rect); y, row = y0, 0
    while y < y0 + h:
        hh = rnd.choice(rowh if not face else (4, 5)); x = x0 - (row % 2) * 5 - rnd.randrange(3)
        while x < x0 + w:
            ww = rnd.choice((7, 8, 9, 10, 11)); r = pygame.Rect(x, y, ww, hh)
            tone = lerp(rnd.choice(tones), (40, 36, 48) if face else (54, 50, 64), .3 if face else dark)
            for yy in range(r.y, r.bottom):
                for xx in range(r.x, r.right):
                    if s.get_clip().collidepoint(xx, yy):
                        k = BAYER[yy % 4][xx % 4] / 16 * .5; sh = (xx - r.x) / ww * .2 + (yy - r.y) / hh * .35
                        s.set_at((xx, yy), lerp(tone, shade_to, sh * .9 + k * .25))
            line(s, lerp(tone, (230, 224, 230), .4), (r.x + 1, r.y + 1), (r.right - 3, r.y + 1))
            line(s, lerp(tone, (230, 224, 230), .2), (r.x + 1, r.y + 1), (r.x + 1, r.bottom - 3))
            pygame.draw.rect(s, MORTAR, r, 1); x += ww
        y += hh; row += 1
    s.set_clip(clip)

def lichen(s, rect, rnd, n, a=255):
    x0, y0, w, h = rect
    for _ in range(n):
        cx, cy = x0 + rnd.randrange(w), y0 + rnd.randrange(h); c = rnd.choice(LICHEN)
        for k in range(rnd.randrange(2, 6)):
            x, y = cx + rnd.randrange(-1, 2), cy + rnd.randrange(-1, 2)
            if x0 <= x < x0 + w and y0 <= y < y0 + h and s.get_at((x, y)).a: s.set_at((x, y), (*lerp(s.get_at((x, y))[:3], c, .7), a))

def merlon_top(rnd, tones, v):
    """crenellated wall top (16x16, drawn raised like every wall top): the parapet's crenel surface with ONE merlon block
    in the middle. Every tile carries the same merlon/crenel rhythm, so random tile choice keeps a regular 16px beat in
    both horizontal and vertical runs."""
    s = surf(T, T)
    stones(s, pygame.Rect(0, 0, T, T), rnd, [lerp(t, (60, 58, 70), .25) for t in tones], dark=.4)        # crenel (lower) surface
    pygame.draw.line(s, (150, 146, 156), (0, 0), (T - 1, 0))
    for y in range(11, 14):                                                                             # merlon's cast shadow on the crenel
        for x in range(3, 15):
            if BAYER[y % 4][x % 4] / 16 < (.85 if y < 13 else .4): s.set_at((x, y), lerp(s.get_at((x, y))[:3], (16, 12, 24), .55))
    m = surf(T, T)
    stones(m, pygame.Rect(3, 1, 10, 5), rnd, tones)                                                     # merlon cap (lit)
    for x in range(3, 13): m.set_at((x, 1), (206, 200, 196))
    for y in range(1, 6): m.set_at((3, y), lerp(m.get_at((3, y))[:3], (220, 214, 210), .35))
    stones(m, pygame.Rect(3, 6, 10, 6), rnd, tones, face=True)                                          # merlon south face
    for y in range(6, 12): m.set_at((12, y), lerp(m.get_at((12, y))[:3], (20, 16, 28), .45))
    for x in range(3, 13): m.set_at((x, 6), lerp(m.get_at((x, 6))[:3], (200, 194, 200), .45))
    if v == 2:                                                                                          # chipped merlon corner
        for (x, y) in ((12, 1), (11, 1), (12, 2)): m.set_at((x, y), (0, 0, 0, 0))
    if v == 4:                                                                                          # arrow loop slit in the merlon face
        for y in range(7, 11): m.set_at((8, y), (12, 8, 16))
        m.set_at((7, 8), (12, 8, 16)); m.set_at((9, 8), (12, 8, 16))
    pygame.draw.rect(m, INK_, (2, 0, 12, 12), 1)
    s.blit(m, (0, 0))
    lichen(s, (0, 0, T, T), rnd, 2 + (v == 3) * 4)
    if v == 5:                                                                                          # tuft of grass in a crenel joint
        for k in range(4): s.set_at((1 + k % 2, 9 - k), (80 + k * 10, 110 + k * 8, 50))
    return s

def parapet_front(rnd, tones, v):
    """inner face of the parapet (16 x FACE): dressed stone, water streaks, lichen at the foot; v5 has a drain hole"""
    s = surf(T, FACE); stones(s, pygame.Rect(0, 0, T, FACE), rnd, tones, face=True)
    for x in range(T): s.set_at((x, 0), lerp(s.get_at((x, 0))[:3], (220, 214, 224), .5)); s.set_at((x, FACE - 1), MORTAR)
    for k in range(2):                                                                                  # rain streaks
        x = rnd.randrange(2, 14)
        for y in range(1, FACE - 2):
            if rnd.random() < .7: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (30, 34, 40), .3))
    lichen(s, (0, FACE - 5, T, 4), rnd, 2)
    if v == 5:
        pygame.draw.rect(s, (12, 8, 16), (6, FACE - 5, 4, 3)); s.set_at((6, FACE - 6), (180, 176, 170))
    return s

def side_face(rnd, side, tones):
    s = surf(SIDE, T + FACE); stones(s, pygame.Rect(0, 0, SIDE, T + FACE), rnd, tones, face=True)
    for y in range(T + FACE):
        for x in range(SIDE):
            d = x / (SIDE - 1) if side == "left" else 1 - x / (SIDE - 1)
            c = s.get_at((x, y)); t = (1 - d) * .55
            if (BAYER[y % 4][x % 4] / 16) < (1 - d) * .4: t += .1
            s.set_at((x, y), (*lerp(c[:3], (14, 10, 22), t), 255))
    ex = SIDE - 1 if side == "left" else 0
    for y in range(T + FACE): s.set_at((ex, y), lerp(s.get_at((ex, y))[:3], (210, 204, 214), .3))
    for x in range(SIDE): s.set_at((x, 0), (200, 194, 204)); s.set_at((x, T + FACE - 1), MORTAR)
    lichen(s, (0, T, SIDE, FACE - 2), rnd, 1)
    return s

def merlon_post(rnd, tones, show_face):
    """replacement for art3.pillar() (same 18px width and geometry: top block T, face 8 (+FACE)): a squat turret merlon
    with a crenellated cap, so corners, run ends and every-5th posts read as part of the battlements"""
    w = T + 2; H = T + 8 + FACE; s = surf(w, H)
    stones(s, pygame.Rect(0, 0, w, T), rnd, tones)
    for x in range(1, w - 1): s.set_at((x, 1), (210, 204, 200))
    for x0 in (1, 7, 13):                                                                               # 3 little merlons on the cap
        pygame.draw.rect(s, lerp(tones[0], (230, 226, 220), .35), (x0, 2, 4, 3))
        pygame.draw.rect(s, (40, 36, 46), (x0, 5, 4, 2))
    pygame.draw.rect(s, INK_, (0, 0, w, T), 1)
    fh = 8 + (FACE if show_face else 0)
    stones(s, pygame.Rect(0, T, w, fh), rnd, tones, face=True)
    pygame.draw.rect(s, INK_, (0, T, w, fh), 1)
    pygame.draw.line(s, (150, 144, 156), (1, T), (w - 2, T))
    if show_face:
        for y in range(T + 3, T + 8): s.set_at((w // 2, y), (12, 8, 16))                               # arrow loop
    lichen(s, (1, 1, w - 2, T + fh - 2), rnd, 3)
    if not show_face: s.fill((0, 0, 0, 0), (0, T + 8, w, FACE))
    return s

# ---------- the view below (underlay) ----------
_land = {}
def landscape(seed=10):
    """big (1200x1200) dusk landscape far below, drawn at half resolution then 2x nearest, like balcony_view"""
    if seed in _land: return _land[seed]
    rnd = random.Random(seed); W = H = 600
    n = vnoise(W, H, 40, rnd) * .6 + vnoise(W, H, 12, rnd) * .3 + vnoise(W, H, 4, rnd) * .1
    wx = vnoise(W, H, 60, rnd) * 30; wy = vnoise(W, H, 60, rnd) * 30
    X, Y = np.meshgrid(np.arange(W), np.arange(H), indexing="ij")
    fx, fy = ((X + wx) // 26).astype(int), ((Y + wy) // 18).astype(int)
    fid = (fx * 92821 + fy * 68917 + seed * 31) % 9973
    px = np.array(FIELDS, np.uint8)[fid % len(FIELDS)].astype(np.float32)
    rows = (((Y + wy + fx * 3) % 3) < 1)                                                               # plough / crop rows
    px[rows] *= .95
    edge = np.zeros((W, H), bool); edge[1:, :] |= fid[1:, :] != fid[:-1, :]; edge[:, 1:] |= fid[:, 1:] != fid[:, :-1]
    px[edge] = np.array(TREE[1], np.float32)                                                            # hedgerows
    hedge_trees = edge & (vnoise(W, H, 3, rnd) > .62); px[hedge_trees] = np.array(TREE[2], np.float32)
    forest = n > .58
    canopy = palettise(np.clip((n - .58) * 2.2 + vnoise(W, H, 3, rnd) * .5 - .1 + np.gradient(n, axis=0) * -40 + np.gradient(n, axis=1) * -40, 0, .99), TREE, .3)
    px[forest] = canopy[forest]
    cy = H * .62 + np.sin(X / 70.0) * 40 + np.sin(X / 23.0) * 8                                        # river
    d = np.abs(Y - cy); river = d < 5
    px[river] = np.array(WATER[1], np.float32)
    px[(d < 2) & ((X + Y) % 7 == 0)] = np.array(WATER[2], np.float32)
    px[(d >= 5) & (d < 6.5)] = np.array((70, 74, 56), np.float32)                                       # banks
    ry = H * .3 + np.sin(X / 90.0 + 1) * 60                                                             # road
    road = np.abs(Y - ry) < 1.2; px[road] = np.array((120, 108, 86), np.float32)
    for k in range(5):                                                                                  # hamlets: tiny roofs
        hx, hy = rnd.randrange(40, W - 40), rnd.randrange(40, H - 40)
        for _ in range(7):
            x, y = hx + rnd.randrange(-14, 14), hy + rnd.randrange(-10, 10)
            px[x:x + 4, y:y + 3] = (124, 66, 50); px[x:x + 4, y + 2:y + 3] = (80, 44, 36); px[x:x + 1, y:y + 3] = (150, 90, 66)
    big = np.repeat(np.repeat(px, 2, axis=0), 2, axis=1)
    _land[seed] = big; return big

def view_below(rid, w, h, depth=1.0, seed=10):
    """crop of the landscape for one room + dusk depth haze (hazier toward the far/top edge, as the balcony fades east)"""
    L = landscape(seed); ox, oy = (rid * 137) % (L.shape[0] - w), (rid * 211) % (L.shape[1] - h)
    px = L[ox:ox + w, oy:oy + h].copy()
    X, Y = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h), indexing="ij")
    f = np.clip((.40 + (1 - Y) * .25) * depth, 0, .85)[..., None]
    warm = np.clip((1 - Y) ** 2 * .45, 0, 1)[..., None]
    hz = np.array(HAZE, np.float32) * (1 - warm) + np.array(DUSK, np.float32) * warm
    px = (px * (1 - f) + hz * f) * .72
    b = (np.tile(np.array(BAYER, np.float32), (w // 4 + 1, h // 4 + 1))[:w, :h] / 16 - .5)[..., None] * 6
    px = np.clip(px + b, 0, 255).astype(np.uint8)
    s = pygame.Surface((w, h)); pygame.surfarray.blit_array(s, px); return s

def drop_face(rnd, w, h, tones):
    """outer face of the curtain wall dropping away below a wall row, fading into the haze"""
    s = surf(w, h); stones(s, pygame.Rect(0, 0, w, h), rnd, tones, face=True, rowh=(6, 7, 7, 8))
    for y in range(h):
        t = (y / h) ** .8 * .9
        for x in range(w):
            c = s.get_at((x, y))
            if BAYER[y % 4][x % 4] / 16 < t * 1.1 - .05: s.set_at((x, y), (0, 0, 0, 0)); continue
            s.set_at((x, y), (*lerp(c[:3], lerp(HAZE, (20, 18, 30), .4), t), 255))
    return s

def is_wallish(g, x, y, extra=""):
    return 0 <= x < 24 and 0 <= y < 18 and g[y][x] in "#=" + extra

def underlay(rid, room, top, depth=1.0, extra="", seed=10, drop=44):
    """full bake-size underlay: view below + the outer wall drop under every wall cell that faces the void to the south,
    plus a soft contact shadow along walls that border the void. Walls, floors and posts are drawn over it by art3."""
    g, walk = room["grid"], room["walk"]; W, H = 24 * T, 18 * T + top
    s = view_below(rid, W, H, depth, seed); rnd = random.Random(rid * 17)
    voidc = lambda x, y: 0 <= x < 24 and 0 <= y < 18 and not walk[y][x] and g[y][x] == " "
    sh = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(18):
        for x in range(24):
            if not voidc(x, y): continue
            if is_wallish(g, x, y - 1, extra):                       # drop face starts under the wall's 14px front face
                y0 = y * T + top + 6; df = drop_face(rnd, T, drop, BST); s.blit(df, (x * T, y0))
                if not (is_wallish(g, x - 1, y - 1, extra) and voidc(x - 1, y)): pygame.draw.line(s, INK_, (x * T, y0), (x * T, y0 + drop // 2))
                if not (is_wallish(g, x + 1, y - 1, extra) and voidc(x + 1, y)): pygame.draw.line(s, INK_, (x * T + T - 1, y0), (x * T + T - 1, y0 + drop // 2))
            for dx, ex in ((-1, 0), (1, T - 4)):                     # a wall to the side: soft shadow on the view
                if is_wallish(g, x + dx, y, extra):
                    for k in range(4): pygame.draw.line(sh, (8, 6, 16, 90 - k * 22), (x * T + (k if dx < 0 else T - 1 - k), y * T + top), (x * T + (k if dx < 0 else T - 1 - k), y * T + top + T - 1))
    s.blit(sh, (0, 0)); return s

def floor_flag(rnd, v):
    """open-air walkway: weathered flagstone, two slabs per tile, lichen; v4 puddle, v5 grass in a crack"""
    s = surf(T, T); pal = [(64, 62, 66), (74, 72, 76), (84, 82, 84), (94, 92, 90), (106, 102, 98)]
    split = rnd.choice((6, 8, 10)); horiz = v % 2 == 0
    for y in range(T):
        for x in range(T):
            slab = (y < split) if horiz else (x < split)
            base = .55 + (.08 if slab else -.04) + (BAYER[y % 4][x % 4] / 16 - .5) * .22 + ((x * 7 + y * 13 + v * 5) % 11 == 0) * .1
            s.set_at((x, y), pal[max(0, min(4, int(base * 5)))])
    for k in range(T):
        if horiz: s.set_at((k, split), (40, 38, 46)); s.set_at((k, split + 1), pal[3])
        else: s.set_at((split, k), (40, 38, 46)); s.set_at((split + 1, k), pal[3])
    for k in range(T): s.set_at((k, T - 1), (44, 42, 50)); s.set_at((T - 1, k), (44, 42, 50)); s.set_at((k, 0), pal[3])
    lichen(s, (0, 0, T, T), rnd, (v % 3 == 0) + (v == 3) * 3)
    if rnd.random() < .6:                                                                               # hairline crack
        x, y = rnd.randrange(2, 13), rnd.randrange(2, 13)
        for k in range(5): s.set_at((x, y), (48, 46, 52)); x += rnd.choice((0, 1)); y += rnd.choice((0, 1))
    if v == 4:                                                                                          # small rain puddle reflecting the dusk sky
        for y in range(7, 12):
            for x in range(4, 12):
                d = ((x - 7.5) / 4) ** 2 + ((y - 9.5) / 2.2) ** 2
                if d < 1: s.set_at((x, y), (60, 64, 82) if d < .7 else (56, 56, 66))
        for x in (5, 6): s.set_at((x, 8), (118, 108, 136))
    if v == 5:
        for k in range(5): s.set_at((6 + k % 3, 12 - k // 2), (70 + k * 12, 110 + k * 6, 52))
    return s
