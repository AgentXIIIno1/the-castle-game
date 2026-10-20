"""v3 art: bigger hand-authored sprites (pixel maps), painterly floors via value noise, pillared 3/4 walls."""
import math, random
try:
    import numpy as np
except Exception:
    np = None
import pygame
import os, json
import gfx
import decor
import setpiece
from art import BAYER, outline, lerp, stones, STONE, is_wall, T, COLS, ROWS

INK = (16, 10, 16)
HERO_PAL = {
 'k': INK, 'H': (64, 38, 22), 'h': (104, 64, 34), 'y': (150, 98, 52), 'Y': (186, 130, 74),
 'S': (158, 102, 74), 's': (212, 152, 112), 'q': (236, 186, 146), 't': (96, 62, 46), 'e': (30, 18, 18),
 'L': (78, 48, 28), 'l': (122, 80, 44), 'm': (166, 114, 64), 'C': (50, 34, 28), 'c': (84, 58, 40),
 'd': (118, 84, 56), 'w': (196, 186, 164), 'W': (140, 128, 116), 'b': (44, 28, 20), 'g': (226, 176, 72),
 'p': (72, 62, 66), 'P': (44, 38, 42), 'B': (60, 40, 28), 'n': (96, 66, 44),
}
HERO = """
.........kkkkk..........
.......kkyYyyhkk........
......kyYyyhhhhHk.......
.....khyyhhhyhhhHk......
....khhyhhHhhyhhHHk.....
....kHhhhsqqqshhhHk.....
...kHHhhHHqqHHshhHHk....
...kHhhsseqsessShHHk....
...kHhhSsssssssShhHk....
...kHHhStsssstSShHHk....
..kHHhhSttttttShhhHHk...
..kHHHhkStttSkhhHHHk....
..kCHHHkkSSSkkHHHCck....
.kcdcHHkwwWwwkHHcdck....
.kcddcklmmwWmmlkcdcCk...
kcdddcklmmlWlmmlkcSsk...
kcdddklmmllWllmlkSqsk...
kcddcklmllllllmlkssSk...
kcddckbbbgbbbbbbkkSk....
kcdcCklllmlllllk..k.....
kcdcCklllmllllLk........
kcddCkLllllllLLk........
kcdcCkkppppppppk........
kcdcCCkpppPpppPk........
.kcdcCkpppkpppPk........
.kcddCkppPkpPpPk........
.kcdcCkpPPkpPPPk........
..kcdCkpPPkpPPk.........
..kcCkkBnBkBnBk.........
..kcdkBBBBkBBBBk........
...kckBBBBkkBBBBk.......
...k.kkkkk..kkkkk.......
"""

def from_map(txt, pal):
    rows = [r for r in txt.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    s = pygame.Surface((w, len(rows)), pygame.SRCALPHA)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal: s.set_at((x, y), pal[ch])
    return s

def make_hero(frame, sword=True, helmet=False):
    base = from_map(HERO, HERO_PAL)
    w, h = base.get_size()
    s = pygame.Surface((w + 10, h + 2), pygame.SRCALPHA)
    if frame:  # walk: shift the legs
        top = base.subsurface((0, 0, w, 27)); legs = base.subsurface((0, 27, w, h - 27))
        s.blit(top, (0, 1)); s.blit(legs, (1, 28))
    else: s.blit(base, (0, 0))
    if helmet:   # steel cap with nasal guard and rivets
        pygame.draw.ellipse(s, INK, (4, -1, 15, 10)); pygame.draw.rect(s, INK, (4, 3, 15, 4))
        pygame.draw.ellipse(s, (150, 156, 170), (5, 0, 13, 9)); pygame.draw.rect(s, (110, 116, 130), (5, 4, 13, 2))
        pygame.draw.line(s, (220, 226, 236), (8, 1), (13, 1)); pygame.draw.line(s, (200, 206, 216), (7, 2), (7, 3))
        pygame.draw.line(s, (90, 96, 110), (11, 6), (11, 8)); s.set_at((7, 5), (230, 230, 240)); s.set_at((16, 5), (230, 230, 240))
    if not sword: return s
    # sword held low, blade angled down-right
    hx, hy = 19, 17 + (1 if frame else 0)
    pygame.draw.line(s, INK, (hx - 2, hy - 1), (hx + 3, hy + 2), 3)                   # crossguard outline
    pygame.draw.line(s, HERO_PAL['g'], (hx - 2, hy - 1), (hx + 3, hy + 2))
    for i in range(12):
        x, y = hx + 2 + i * .62, hy + 2 + i
        pygame.draw.line(s, INK, (x - 1, y), (x + 2, y))
        s.set_at((int(x), int(y)), (232, 236, 244)); s.set_at((int(x) + 1, int(y)), (138, 146, 160))
    s.set_at((hx + 10, hy + 14), INK)
    return s

def make_snake():
    """big coiled snake with scales: thick shaded tube along a squashed spiral + raised neck"""
    W, H = 48, 40
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    dark, mid, mid2, light, belly = (22, 52, 26), (48, 98, 44), (70, 124, 54), (140, 182, 84), (170, 170, 96)
    cx, cy = 22, 28
    pts = []
    for i in range(140):                     # spiral from outside in
        a = i / 140 * math.pi * 4.2
        r = 17 - i / 140 * 13
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * .5, 4.2 - i / 140 * 1.4, a))
    for i in range(22):                      # neck rising from outer end
        u = i / 21
        pts.insert(0, (cx + 17 + u * 2 - u * u * 4, cy - u * 18, 3.3 - u * .6, 0))
    order = sorted(range(len(pts)), key=lambda k: pts[k][1])
    for k in order:                          # outline pass
        x, y, th, a = pts[k]; pygame.draw.circle(s, INK, (x, y), th + 1)
    for k in order:
        x, y, th, a = pts[k]
        if k % 3 == 0: pygame.draw.circle(s, INK, (x, y + .6), th + .6)   # coil/scale band edges
        pygame.draw.circle(s, dark, (x, y), th)
        pygame.draw.circle(s, mid, (x - .6, y - .8), th * .78)
        pygame.draw.circle(s, mid2, (x - 1, y - 1.3), th * .45)
        if k % 4 == 0: s.set_at((int(x - 1), int(y - 2)), light)
    # scales: diamond flecks
    rnd = random.Random(3)
    for y in range(H):
        for x in range(W):
            c = s.get_at((x, y))
            if c[:3] in (mid, mid2) and (x + y * 2) % 4 == 0: s.set_at((x, y), dark if rnd.random() < .7 else mid2)
    # head
    hx, hy = cx + 15, cy - 20
    pygame.draw.ellipse(s, INK, (hx - 2, hy - 4, 13, 9))
    pygame.draw.ellipse(s, mid, (hx - 1, hy - 3, 11, 7))
    pygame.draw.ellipse(s, mid2, (hx, hy - 3, 8, 3)); pygame.draw.line(s, light, (hx + 1, hy - 3), (hx + 6, hy - 3))
    pygame.draw.line(s, dark, (hx + 1, hy + 2), (hx + 9, hy + 1))
    s.set_at((hx + 5, hy - 1), (255, 60, 50)); s.set_at((hx + 6, hy - 1), (255, 140, 110)); s.set_at((hx + 5, hy), (150, 20, 20))
    pygame.draw.line(s, (220, 40, 60), (hx + 10, hy + 1), (hx + 13, hy + 2))
    s.set_at((hx + 14, hy + 1), (220, 40, 60)); s.set_at((hx + 14, hy + 3), (220, 40, 60))
    return s

LAMP = """
.......kk.......
......kgYk......
.....kkGgkk.....
....kGgYYgGk..k.
.kk.kgYYggGkkkgk
kg.kGgYgggGgGgk.
kg.kGgggggggGk..
.kkkGGgggGGGk...
...kkGGGGGGkk...
....kOgYggOk....
...kOOOOOOOOk...
....kkkkkkkk....
"""
def make_lamp():
    return from_map(LAMP, {'k': INK, 'g': (222, 164, 58), 'G': (150, 96, 34), 'Y': (255, 236, 150), 'O': (110, 70, 28)})

def make_bush(big, seed):
    rnd = random.Random(seed)
    w, h = (34, 28) if big else (24, 20)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = [(24, 50, 28), (38, 76, 36), (58, 104, 44), (92, 140, 58), (140, 184, 80)]
    blobs = [(rnd.uniform(.2, .8) * w, rnd.uniform(.3, .75) * h, rnd.uniform(.14, .24) * w) for _ in range(11 if big else 7)]
    for y in range(h):
        for x in range(w):
            best = None
            for bx, by, r in blobs:
                d = ((x - bx) / r) ** 2 + ((y - by) / (r * .85)) ** 2
                if d < 1 and (best is None or d < best[0]): best = (d, bx, by, r)
            if not best: continue
            d, bx, by, r = best
            l = (-(x - bx) * .5 - (y - by) * .9) / r * .5 + .5 - d * .25 + (y / h) * -.25 + .1
            l += (BAYER[y % 4][x % 4] / 16 - .5) * .35 + rnd.uniform(-.12, .12)
            s.set_at((x, y), cols[max(0, min(4, int(l * 5)))])
    for _ in range(26 if big else 14):        # leaf flecks
        x, y = rnd.randrange(2, w - 3), rnd.randrange(2, h - 3)
        if s.get_at((x, y)).a and s.get_at((x, y + 2)).a:
            s.set_at((x, y), cols[4]); s.set_at((x + 1, y), cols[3]); s.set_at((x, y + 1), cols[1])
    return outline(s)

# ---------- painterly floors via value noise
def vnoise(w, h, cell, rnd):
    small = pygame.Surface((max(2, w // cell + 2), max(2, h // cell + 2)))
    for y in range(small.get_height()):
        for x in range(small.get_width()):
            v = rnd.randrange(256); small.set_at((x, y), (v, v, v))
    big = pygame.transform.smoothscale(small, (w + cell * 2, h + cell * 2))
    return pygame.surfarray.array3d(big)[cell:cell + w, cell:cell + h, 0].astype(np.float32) / 255.0

def palettise(field, pal, bayer_amt=.18):
    w, h = field.shape
    b = np.array(BAYER, np.float32) / 16 - .5
    bt = np.tile(b, (w // 4 + 1, h // 4 + 1))[:w, :h]
    idx = np.clip(((field + bt * bayer_amt) * len(pal)).astype(int), 0, len(pal) - 1)
    out = np.array(pal, np.uint8)[idx]
    return out

def bake_floor(rid, room, garden):
    try: return bake_floor_np(rid, room, garden)
    except Exception as e:
        print("[castle diag] numpy floor failed, using plain floor:", e)
        rnd = random.Random(rid); s = gfx.rgb((COLS * T, ROWS * T))
        base = [(46, 74, 32), (60, 92, 38), (78, 110, 44)] if garden else [(50, 42, 40), (60, 50, 46), (72, 60, 52)]
        s.fill(base[1])
        for _ in range(4000): s.set_at((rnd.randrange(COLS * T), rnd.randrange(ROWS * T)), rnd.choice(base))
        return s

# ---------- stair art (the art set: assets/stairs, see manifest.json)
STAIR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "stairs")
_stair_cache = {}

TILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tiles")
_tile_cache = {}
def tile_sheet(name, cell):
    """slice a tile sheet into cells (row-major list of rows); None if missing"""
    if name not in _tile_cache:
        try:
            img = pygame.image.load(os.path.join(TILE_DIR, name) if "/" not in name else os.path.join(os.path.dirname(TILE_DIR), name))
            try: img = img.convert_alpha()
            except pygame.error: pass
            cw, ch = cell
            _tile_cache[name] = [[img.subsurface((c*cw, r*ch, cw, ch)) for c in range(img.get_width()//cw)] for r in range(img.get_height()//ch)]
        except Exception as e:
            print("[castle diag] tile art missing:", name, e); _tile_cache[name] = None
    return _tile_cache[name]

def thash(x, y): return (x * 73856093 ^ y * 19349663) & 0xffff

def stair_img(name):
    if name not in _stair_cache:
        img = None
        try:
            v = next((d for k, d in STAIR_VARIANT_DIR.items() if f"_{k}_" in name), None)
            img = pygame.image.load(os.path.join(os.path.dirname(STAIR_DIR), v, name) if v else os.path.join(STAIR_DIR, name))
            try: img = img.convert_alpha()
            except pygame.error: pass       # no display yet: keep the loaded RGBA surface
        except Exception as e:
            if "dust_strip" not in name: print("[castle diag] stair art missing:", name, e)
        _stair_cache[name] = img
    return _stair_cache[name]

def fallback_stairs(s, X, Y, w, h, up):
    """procedural steps if the PNG can't be loaded (e.g. pygame built without PNG support)"""
    pygame.draw.rect(s, (24, 20, 30), (X, Y, w, h))
    n = max(3, h // 4)
    for i in range(n):
        k = i if up else n - 1 - i
        c = lerp((70, 66, 80), (170, 164, 176), k / max(1, n - 1))
        pygame.draw.rect(s, c, (X + 1, Y + i * h // n, w - 2, h // n - 1))
    pygame.draw.rect(s, (12, 10, 18), (X, Y, w, h), 1)

def stair_blocks(g):
    """connected blocks of the same stair glyph -> (glyph, col, row, w, h)"""
    seen, out = set(), []
    for y in range(ROWS):
        for x in range(COLS):
            ch = g[y][x]
            if ch not in "UD" or (x, y) in seen: continue
            st, cells = [(x, y)], []
            seen.add((x, y))
            while st:
                cx, cy = st.pop(); cells.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (cx + dx, cy + dy)
                    if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in seen and g[n[1]][n[0]] == ch: seen.add(n); st.append(n)
            x0, y0 = min(c[0] for c in cells), min(c[1] for c in cells)
            out.append((ch, x0, y0, max(c[0] for c in cells) - x0 + 1, max(c[1] for c in cells) - y0 + 1))
    return out

def stair_variant(rid, room):
    st = room.get("theme", {}).get("stairs")              # 'battlement' / 'tower' (assets/battlements, assets/tower_top)
    if st: return st
    return "dungeon" if floor_kind(rid, room) == "cave" else "indoor"

STAIR_VARIANT_DIR = {"battlement": "battlements", "tower": "tower_top"}

SPIRAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "spiral_stairs")
_spiral = {}
def spiral(rid):
    """ spiral staircase for rooms 4/5/7/23 (assets/spiral_stairs/manifest.json "rooms"):
    dict(img, cell, anchor, world, sort, floor) or None. Replaces the straight stair tiles of that block; triggers,
    blocking and the stair cooldown are untouched (the U/D cells stay as they are)."""
    if not _spiral:
        try:
            man = json.load(open(os.path.join(SPIRAL_DIR, "manifest.json")))
            for k, e in man["rooms"].items():
                img = pygame.image.load(os.path.join(SPIRAL_DIR, e["file"]))
                try: img = img.convert_alpha()
                except pygame.error: pass
                _spiral[int(k)] = dict(img=img, cell=tuple(e["block_topleft_cell"]), anchor=tuple(e["anchor_px"]), world=tuple(e["world_anchor"]),
                                       sort=e["depth_sort_y"], floor=e.get("layer", "").startswith("floor"))
        except Exception as ex:
            print("[castle diag] spiral stair art unavailable:", ex); _spiral[None] = None
    return _spiral.get(rid)

def spiral_block(rid, x0, y0):
    sp = spiral(rid)
    return sp if sp and sp["cell"] == (x0, y0) else None

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "kb_letters")
def draw_kb_letters(s, room, top, raise_):
    """ carved letters on the raised wall top of their cell: top-left at (x*16, y*16 + TOP - RAISE), normal alpha"""
    for x, y, c in room.get("kb_letters", []):
        img = stair_img_at(KB_DIR, f"kb_letter_{c}.png")
        if img: s.blit(img, (x * T, y * T + top - raise_))

def stair_img_at(d, name):
    key = (d, name)
    if key not in _stair_cache:
        img = None
        try:
            img = pygame.image.load(os.path.join(d, name))
            try: img = img.convert_alpha()
            except pygame.error: pass
        except Exception as e: print("[castle diag] art missing:", name, e)
        _stair_cache[key] = img
    return _stair_cache[key]

def draw_stairs(s, rid, room, top):
    var = stair_variant(rid, room)
    for ch, x0, y0, w, h in stair_blocks(room["grid"]):
        d = "up" if ch == "U" else "down"
        sp = spiral_block(rid, x0, y0)
        if sp:                                    # spiral: floor-layer art is baked here, rising ones are depth-sorted in main
            if sp["floor"]: s.blit(sp["img"], (sp["world"][0] - sp["anchor"][0], sp["world"][1] - sp["anchor"][1] + top))
            continue
        for by in range(y0, y0 + h, 2):           # tile 2x2 pieces over bigger blocks
            for bx in range(x0, x0 + w, 2):
                fw, fh = min(2, x0 + w - bx), min(2, y0 + h - by)
                img = stair_img(f"stairs_{d}_{var}_{fw}x{fh}.png")
                if img: s.blit(img, (bx * T, by * T + top))
                else: fallback_stairs(s, bx * T, by * T + top, fw * T, fh * T, d == "up")

def floor_kind(rid, room):
    if room.get("theme", {}).get("floor"): return room["theme"]["floor"]
    c = (room.get("const") or "").upper(); nm = room.get("name", "").upper()
    if rid == 1: return "cobble"
    if 68 <= rid <= 83: return "cave"
    if any(k in c or k in nm for k in ("BATTLE", "WALL", "TOWER", "BALCONY", "KITCHEN", "STORAGE")): return "flag"
    if any(k in c or k in nm for k in ("ROOM", "QUARTERS", "STUDY", "LIBRARY", "DRESS", "BALLROOM", "DINING", "GUEST", "LAB")): return "wood"
    return "flag"

def bake_floor_np(rid, room, garden):
    rnd = random.Random(rid * 31)
    w, h = COLS * T, ROWS * T
    n = vnoise(w, h, 24, rnd) * .55 + vnoise(w, h, 9, rnd) * .3 + vnoise(w, h, 3, rnd) * .15
    dirtn = vnoise(w, h, 20, rnd) * .7 + vnoise(w, h, 5, rnd) * .3
    if garden:
        pal = [(34, 56, 28), (46, 74, 32), (60, 92, 38), (78, 110, 44), (98, 130, 52), (124, 152, 62)]
        arr = palettise((n - .2) * 1.4, pal)
        dirt = palettise((dirtn - .62) * 4.0, [(70, 60, 36), (96, 70, 44), (118, 88, 56), (138, 104, 66)])
        mask = (dirtn + (np.tile(np.array(BAYER) / 16, (w // 4, h // 4))[:w, :h] - .5) * .05) > .7
        arr[mask] = dirt[mask]
        dirt_cells = mask.reshape(w // T, T, h // T, T).mean(axis=(1, 3)) > .45
    else:
        kind = floor_kind(rid, room)
        pal = {"cobble": [(40, 33, 34), (50, 42, 40), (60, 50, 46), (72, 60, 52), (84, 70, 60)],
               "wood": [(58, 36, 24), (70, 44, 28), (82, 52, 32), (96, 62, 38), (110, 72, 44)],
               "flag": [(46, 44, 52), (56, 54, 62), (66, 62, 70), (76, 72, 78), (88, 84, 88)],
               "cave": [(26, 24, 28), (34, 31, 34), (42, 38, 40), (50, 45, 46), (60, 54, 52)]}[kind]
        arr = palettise((n - .2) * 1.4, pal)
    s = gfx.rgb((w, h))
    pygame.surfarray.blit_array(s, arr)
    if garden:
        dt = tile_sheet("dirt_autotile.png", (16, 16))
        if dt:
            cw, chh = dirt_cells.shape
            isd = lambda x, y: 0 <= x < cw and 0 <= y < chh and dirt_cells[x, y]
            for cx in range(cw):
                for cy in range(chh):
                    if dirt_cells[cx, cy]:
                        mk = isd(cx, cy - 1) * 1 + isd(cx + 1, cy) * 2 + isd(cx, cy + 1) * 4 + isd(cx - 1, cy) * 8
                        s.blit(dt[thash(cx, cy) % len(dt)][mk], (cx * T, cy * T))
    if garden:
        for _ in range(700):                  # grass tufts: little V strokes
            x, y = rnd.randrange(1, w - 2), rnd.randrange(3, h)
            c = s.get_at((x, y))
            if c[1] > c[0] + 20:
                s.set_at((x, y - 1), (132, 162, 70)); s.set_at((x - 1, y - 2), (110, 144, 60)); s.set_at((x + 1, y - 2), (150, 178, 80))
                s.set_at((x, y), (30, 50, 26))
    elif kind == "wood":                      # plank floor: boards with staggered joints and grain
        for y in range(0, h, 6):
            pygame.draw.line(s, (36, 22, 16), (0, y), (w, y)); pygame.draw.line(s, (122, 82, 50), (0, y + 1), (w, y + 1))
            off = rnd.randrange(24)
            for x in range(off, w, rnd.choice((22, 26, 30))): pygame.draw.line(s, (36, 22, 16), (x, y), (x, y + 5))
        for _ in range(500):
            x, y = rnd.randrange(w - 4), rnd.randrange(h)
            pygame.draw.line(s, (62, 40, 26), (x, y), (x + rnd.randrange(2, 6), y))
    elif kind in ("flag", "cave"):            # large worn flagstones / rough cave slabs
        y = 0
        while y < h:
            hh = rnd.choice((10, 12, 14)) if kind == "flag" else rnd.choice((7, 9, 12)); x = -rnd.randrange(10)
            while x < w:
                ww = rnd.choice((12, 16, 18, 20)) if kind == "flag" else rnd.choice((8, 11, 15))
                pygame.draw.rect(s, (22, 20, 26), (x, y, ww, hh), 1)
                pygame.draw.line(s, lerp(pal[3], (200, 196, 200), .25), (x + 1, y + 1), (x + ww - 3, y + 1))
                if rnd.random() < .25: pygame.draw.line(s, (30, 28, 34), (x + 3, y + 3), (x + 3 + rnd.randrange(5), y + 3 + rnd.randrange(5)))
                x += ww
            y += hh
        if kind == "cave":
            for _ in range(160): s.set_at((rnd.randrange(w), rnd.randrange(h)), (70, 84, 66))
    else:                                     # worn cobbles
        for _ in range(420):
            cx, cy, r = rnd.randrange(w), rnd.randrange(h), rnd.choice((2, 3, 3, 4))
            tone = rnd.choice([(78, 70, 68), (90, 82, 78), (68, 62, 62)])
            pygame.draw.ellipse(s, (34, 28, 28), (cx - r, cy - r // 2 + 1, 2 * r + 1, r + 2))
            pygame.draw.ellipse(s, tone, (cx - r, cy - r // 2, 2 * r, r + 1))
            pygame.draw.line(s, lerp(tone, (200, 190, 180), .4), (cx - r + 2, cy - r // 2), (cx + r - 3, cy - r // 2))
        for _ in range(220):
            x, y = rnd.randrange(1, w - 1), rnd.randrange(2, h)
            s.set_at((x, y), (92, 116, 56)); s.set_at((x, y - 1), (120, 146, 64))
    return s

# ---------- walls with faces, pillars, corner posts
FACE = 14
STONE_TONES = [(104, 98, 108), (92, 88, 98), (116, 110, 116), (84, 80, 92), (98, 96, 92)]

def vstones(s, rect, rnd, face=False):
    x0, y0, w, h = rect
    clip = s.get_clip(); s.set_clip(rect)
    y, row = y0, 0
    while y < y0 + h:
        hh = rnd.choice((5, 6, 6, 7)) if not face else rnd.choice((4, 5))
        x = x0 - (row % 2) * 5 - rnd.randrange(3)
        while x < x0 + w:
            ww = rnd.choice((7, 8, 9, 10, 11))
            r = pygame.Rect(x, y, ww, hh)
            tone = rnd.choice(STONE_TONES)
            if face: tone = lerp(tone, (40, 36, 48), .3)
            else: tone = lerp(tone, (54, 50, 64), .35)
            for yy in range(r.y, r.bottom):
                for xx in range(r.x, r.right):
                    if s.get_clip().collidepoint(xx, yy):
                        k = (BAYER[yy % 4][xx % 4] / 16) * .5 + rnd.random() * .15
                        sh = ((xx - r.x) / ww * .2 + (yy - r.y) / hh * .35)
                        s.set_at((xx, yy), lerp(tone, (30, 26, 36), sh * .9 + k * .25))
            pygame.draw.line(s, lerp(tone, (220, 214, 220), .35), (r.x + 1, r.y + 1), (r.right - 3, r.y + 1))
            pygame.draw.line(s, lerp(tone, (220, 214, 220), .18), (r.x + 1, r.y + 1), (r.x + 1, r.bottom - 3))
            pygame.draw.rect(s, (24, 20, 30), r, 1)
            if rnd.random() < (.35 if face else .2):     # moss on stone
                mx, my = r.x + rnd.randrange(1, max(2, ww - 2)), r.y + (0 if face else rnd.randrange(1, hh))
                for k in range(rnd.randrange(3, 8)):
                    s.set_at((mx + rnd.randrange(-2, 3), my + rnd.randrange(0, 3 if not face else hh)), rnd.choice([(70, 102, 46), (96, 132, 58), (52, 80, 38)]))
            x += ww
        y += hh; row += 1
    s.set_clip(clip)

# ---------- corridors: runner floor + slim wall edges (assets/corridor/manifest.json) ----------
COR = "corridor/"

def corridor_cells(room):
    """{(x, y): {"h"|"v"}} narrow passages: walkable cells with walls on both sides, 1-2 cells wide (a grid edge is an
    exit, not a wall), each run extended one cell into the room at its mouth. Stairs/doors/props cells are left out."""
    g, walk = room["grid"], room["walk"]
    props = {(o["x"], o["y"]) for o in room.get("decor", {}).get("objects", [])}
    W = lambda x, y: 0 <= x < COLS and 0 <= y < ROWS and g[y][x] in "#="
    F = lambda x, y: 0 <= x < COLS and 0 <= y < ROWS and (walk[y][x] or (x, y) in props) and (g[y][x] == " " or g[y][x].islower())
    out = {}
    for y in range(ROWS):
        for x in range(COLS):
            if not F(x, y): continue
            if W(x, y - 1) and W(x, y + 1): out.setdefault((x, y), set()).add("h")
            if W(x, y - 1) and F(x, y + 1) and W(x, y + 2): out.setdefault((x, y), set()).add("h"); out.setdefault((x, y + 1), set()).add("h")
            if W(x - 1, y) and W(x + 1, y): out.setdefault((x, y), set()).add("v")
            if W(x - 1, y) and F(x + 1, y) and W(x + 2, y): out.setdefault((x, y), set()).add("v"); out.setdefault((x + 1, y), set()).add("v")
    mouths = {}
    for (x, y), ks in out.items():   # doorway mouth: one cell past each end of a run, into the room
        for k in ks:
            for d in ((-1, 0), (1, 0)) if k == "h" else ((0, -1), (0, 1)):
                n = (x + d[0], y + d[1])
                if n not in out and F(*n): mouths.setdefault(n, set()).add(k)
    for n, ks in mouths.items(): out[n] = ks
    return {c: ks for c, ks in out.items() if c not in props}

def corridor_art():
    import setpiece
    return all(os.path.exists(os.path.join(setpiece.A, COR + f)) for f in ("corridor_floor_h.png", "corridor_floor_v.png",
               "corridor_lip_n.png", "corridor_rim_s.png", "corridor_rim_w.png", "corridor_rim_e.png"))

def bake_room(rid, room):
    rnd = random.Random(rid * 7919)
    g = room["grid"]; garden = "GARDEN" in (room.get("const") or "")
    ring = room.get("theme", {}).get("ring_glyphs")            # tower-top parapet ring: '-'/'|' cells bake as wall (no floor)
    if ring: g = ["".join("#" if c in ring else c for c in row) for row in g]
    TOP = 24   # extra space above row 0 for raised pillars/faces
    s = gfx.rgb((COLS * T, ROWS * T + TOP)); s.fill((255, 0, 255))
    fl = bake_floor(rid, room, garden)
    tint = room.get("theme", {}).get("tint")                                  # per-room theme override (room_themes.json)
    if tint and not garden and not setpiece.theme_tiles_loaded(room): fl = fl.copy(); fl.fill(tuple(tint), special_flags=pygame.BLEND_MULT)
    ul = setpiece.underlay(rid, room)                                         # room 33 garden view; battlement/tower views
    if ul: s.blit(ul[0], ul[1])
    decor.plan(rid, room, floor_kind)                                        # (planned earlier now: corridor detection skips props)
    cor = corridor_cells(room) if not (garden or ul) and corridor_art() else {}   #
    _rs = pygame.Surface(s.get_size()) if cor else None                       # scratch: skipped faces/posts still draw here, at the
                                                                              # same coords/clip, so the rnd stream (all other stone textures) is unchanged
    corh = {c for c, ks in cor.items() if "h" in ks}
    wall_n = {(x, y - 1) for x, y in corh}                                     # wall cell directly north of a horizontal corridor
    wall_s = {(x, y + 1) for x, y in corh}                                     # ... directly south: drawn without the raise
    W_ = lambda x, y: 0 <= x < COLS and 0 <= y < ROWS and g[y][x] in "#="
    props = {(o["x"], o["y"]) for o in room.get("decor", {}).get("objects", [])}   # decor props block walk but stand on floor
    props |= {tuple(c) for _, cells in room.get("set_objs", []) for c in cells}   # so do set pieces (study shelves, lab sprites)
    for y in range(ROWS):
        for x in range(COLS):
            if ul and setpiece.underlay_covers(rid, x, y): continue
            if room["walk"][y][x] or (x, y) in props or g[y][x] in "*+MUDG,-.|?`'$%@W[]" or g[y][x].islower() or setpiece.in_hook_bbox(rid, room, x, y):
                ft = setpiece.floor_tile(rid, x, y, thash, room)                    # per-room floor art (Yellow Room, study parquet)
                if (x, y) in cor: ft = setpiece.frame(COR + ("corridor_floor_h.png" if cor[(x, y)] == {"h"} else "corridor_floor_v.png"), 16, thash(x, y) % 6)
                if ft: s.blit(ft, (x * T, y * T + TOP))
                else: s.blit(fl, (x * T, y * T + TOP), (x * T, y * T, T, T))
    # contact AO next to walls
    sh = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    for y in range(ROWS):
        for x in range(COLS):
            if not room["walk"][y][x] and (x, y) not in props: continue
            X, Y = x * T, y * T + TOP
            if (x, y) in cor and os.path.exists(os.path.join(setpiece.A, COR + "corridor_ao.png")):   # corridor contact shadow
                for i_, (dx, dy) in enumerate(((0, -1), (0, 1), (-1, 0), (1, 0))):
                    if W_(x + dx, y + dy): sh.blit(setpiece.frame(COR + "corridor_ao.png", 16, i_), (X, Y))
                continue
            if is_wall(g, x - 1, y):
                for k in range(8): pygame.draw.line(sh, (8, 6, 18, 150 - k * 18), (X + k, Y), (X + k, Y + T - 1))
            if is_wall(g, x + 1, y):
                for k in range(6): pygame.draw.line(sh, (8, 6, 18, 110 - k * 18), (X + T - 1 - k, Y), (X + T - 1 - k, Y + T - 1))
            if is_wall(g, x, y - 1):
                for k in range(10): pygame.draw.line(sh, (8, 6, 18, 160 - k * 15), (X, Y + FACE - 4 + k), (X + T - 1, Y + FACE - 4 + k))
    s.blit(sh, (0, 0))
    decor.plan(rid, room, floor_kind); decor.draw_floor(s, room, TOP); setpiece.draw_floor(s, rid, room, TOP)      # floor decals on the baked floor
    j83 = None; emis = room["emissive"] = []
    ws = setpiece.wall_sheets_for(rid, room)
    if rid == 83 or ws:
        tn, fn, sn = ws or ("room83_wall_tops.png", "room83_wall_fronts.png", "room83_side_walls.png")
        a, b = tile_sheet(tn, (16, 16)), tile_sheet(fn, (16, 14))
        if a and b: j83 = (a, b)
    side_t = tile_sheet("side_walls.png", (8, 30))
    if rid == 83 or ws:
        r83 = tile_sheet(sn, (8, 30))
        if r83: side_t = [r83[0][:2], r83[0][2:]]
    # wall tops (raised by RAISE), then front faces in depth order
    RAISE = 8
    for y in range(ROWS):
        for x in range(COLS):
            ch = g[y][x]
            if ch not in "#=": continue
            X, Y = x * T, y * T + TOP - RAISE
            if (x, y) in wall_s and ch == "#": Y += RAISE                       # south wall of a corridor: no raise
            if ch == "=":
                draw_gate(s, X, Y + RAISE, rnd, g, x, y); continue
            if j83:
                i_ = thash(x, y) % len(j83[0][0]); s.blit(j83[0][0][i_], (X, Y)); (rid == 83) and emis.append(("room83_wall_tops_emissive.png", (16, 16), 0, i_, (X, Y), thash(x, y)))
            else: vstones(s, pygame.Rect(X, Y, T, T), rnd)
            if not is_wall(g, x - 1, y): pygame.draw.line(s, INK, (X, Y), (X, Y + T - 1))
            if not is_wall(g, x + 1, y): pygame.draw.line(s, INK, (X + T - 1, Y), (X + T - 1, Y + T - 1))
            if not is_wall(g, x, y - 1): pygame.draw.line(s, (176, 170, 180), (X, Y), (X + T - 1, Y)); pygame.draw.line(s, INK, (X, Y - 1), (X + T - 1, Y - 1))
            # side faces: visible inner edge of side walls (thin lit/dark bevel)
            if (x, y) in wall_s: s.blit(setpiece.img(COR + "corridor_rim_s.png"), (X, y * T + TOP))
            for dx_ in (1, -1):
                if not side_t and 0 <= x + dx_ < COLS and not is_wall(g, x + dx_, y) and room["walk"][y][x + dx_] and "v" in cor.get((x + dx_, y), ()):
                    vstones(_rs, pygame.Rect(X + T, Y + 4, 6, T) if dx_ == 1 else pygame.Rect(X - 6, Y + 4, 6, T), rnd, face=True)      # skipped 8px side face, keep the rnd stream
            if x + 1 < COLS and not is_wall(g, x + 1, y) and room["walk"][y][x + 1] and "v" not in cor.get((x + 1, y), ()):    # west wall: lit inner face
                if side_t:
                    i_ = thash(x, y) % len(side_t[0]); s.blit(side_t[0][i_], (X + T, Y))
                    if j83 and rid == 83: emis.append(("room83_side_walls_emissive.png", (8, 30), 0, i_, (X + T, Y), thash(x, y)))
                else:
                    fr = pygame.Rect(X + T, Y + 4, 6, T); vstones(s, fr, rnd, face=True)
                    s.fill((30, 24, 20), fr, special_flags=pygame.BLEND_RGB_ADD)
                    pygame.draw.line(s, INK, (fr.right, fr.y), (fr.right, fr.bottom))
            if x - 1 >= 0 and not is_wall(g, x - 1, y) and room["walk"][y][x - 1] and "v" not in cor.get((x - 1, y), ()):      # east wall: shadowed inner face
                if side_t:
                    i_ = thash(x, y) % len(side_t[1]); s.blit(side_t[1][i_], (X - 8, Y))
                    if j83 and rid == 83: emis.append(("room83_side_walls_emissive.png", (8, 30), 0, 2 + i_, (X - 8, Y), thash(x, y)))
                else:
                    fr = pygame.Rect(X - 6, Y + 4, 6, T); vstones(s, fr, rnd, face=True)
                    s.fill((30, 30, 30), fr, special_flags=pygame.BLEND_RGB_SUB)
                    pygame.draw.line(s, INK, (fr.x - 1, fr.y), (fr.x - 1, fr.bottom))
            # front face
            if (x, y) in wall_n and ch == "#" and not is_wall(g, x, y + 1):    # lip instead of the 14px face
                if not j83: vstones(_rs, pygame.Rect(X, Y + T, T, FACE), rnd, face=True)
                s.blit(setpiece.img(COR + "corridor_lip_n.png"), (X, Y + T)); continue
            if not is_wall(g, x, y + 1):
                fr = pygame.Rect(X, Y + T, T, FACE)
                if j83:
                    i_ = thash(x, y) % len(j83[1][0]); s.blit(j83[1][0][i_], (X, Y + T)); (rid == 83) and emis.append(("room83_wall_fronts_emissive.png", (16, 14), 0, i_, (X, Y + T), thash(x, y)))
                else: vstones(s, fr, rnd, face=True)
                pygame.draw.line(s, (150, 144, 156), (X, Y + T), (X + T - 1, Y + T))
                pygame.draw.line(s, INK, (X, fr.bottom), (X + T - 1, fr.bottom))
                if not is_wall(g, x - 1, y): pygame.draw.line(s, INK, (X, Y + T), (X, fr.bottom))
                if not is_wall(g, x + 1, y): pygame.draw.line(s, INK, (X + T - 1, Y + T), (X + T - 1, fr.bottom))
    for (x, y), ks in cor.items():                                             # 3px rims instead of the 8px side faces
        if "v" in ks and W_(x - 1, y): s.blit(setpiece.img(COR + "corridor_rim_w.png"), (x * T, y * T + TOP))
        if "v" in ks and W_(x + 1, y): s.blit(setpiece.img(COR + "corridor_rim_e.png"), (x * T + 13, y * T + TOP))
    # stairs go AFTER the wall pass: side faces (8px) and front faces of neighbouring walls used to overdraw them
    draw_stairs(s, rid, room, TOP)
    if ring and os.path.exists(os.path.join(setpiece.A, "tower_top/embrasure.png")):   # wide crenels over the ring's wall tops
        for y, row in enumerate(room["grid"]):
            for x, c in enumerate(row):
                if c in "-|": s.blit(setpiece.frame("tower_top/embrasure.png", 16, 0 if c == "-" else 1), (x * T, y * T + TOP - 8))
    # depth order: wall pillars, furniture and bed covers are drawn into per-row layers, then composited
    # row by row (north to south). A north-wall pillar's raised face reaches ~6px into the row below and used to be drawn
    # after all furniture, so it covered beds/desks against the wall (room 10). A pillar of row y still covers furniture
    # in row y-1 (south walls stand in front). Drawing order of the rnd calls is unchanged, so textures stay identical.
    base, layers, pillars = s, {}, {}
    def layer(row):
        if row not in layers: layers[row] = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        return layers[row]
    beds = setpiece.bed_cells(rid, room)                                    #
    hidden = enclosed_furniture(g, room["walk"])                           # furniture sealed inside a wall block (74 'KB', 85)
    # furniture: tables/desks (% @), beds (W with [ ] posts)
    for y in range(ROWS):
        s = layer(y) if any(c in "%@W[]" for c in g[y]) else base
        for x in range(COLS):
            ch = g[y][x]; X, Y = x * T, y * T + TOP
            if (x, y) in hidden: continue                       # used to be hidden behind pillars; with the #32 order it would show
            if (x, y) in beds: continue                         # bed: depth-sorted sprite drawn by main
            if ch == "@" and setpiece.has_desk_art(rid, room): continue
            if setpiece.hooked_cell(rid, room, x, y) or (x, y) in setpiece.rail_cells(rid, room): continue   # rail drawn by main                  # throne / mirror / barrels drawn by the object hooks          # desk drawn by main (state-driven)
            if ch in "%@":
                pygame.draw.rect(s, (96, 62, 36), (X, Y - 2, T, T)); pygame.draw.line(s, (140, 96, 56), (X, Y - 2), (X + T - 1, Y - 2))
                if ch == "@" and "LIBRARY" in (room.get("const") or ""):     # bookshelves: rows of coloured spines
                    pygame.draw.rect(s, (44, 28, 20), (X, Y, T, T - 2))
                    for row_y in (Y + 1, Y + 8):
                        xx = X
                        while xx < X + T:
                            bw = rnd.choice((2, 2, 3)); bh = rnd.choice((5, 6, 6))
                            pygame.draw.rect(s, rnd.choice([(150, 50, 46), (60, 90, 140), (70, 120, 70), (170, 140, 70), (110, 70, 130)]), (xx, row_y + 6 - bh, bw, bh))
                            xx += bw
                        pygame.draw.line(s, (120, 80, 48), (X, row_y + 6), (X + T - 1, row_y + 6))
                else:
                    for k in range(3, T, 5): pygame.draw.line(s, (78, 50, 30), (X, Y + k), (X + T - 1, Y + k))
                if not (y + 1 < ROWS and g[y + 1][x] == ch):
                    pygame.draw.rect(s, (60, 38, 24), (X, Y + T - 2, T, 5)); pygame.draw.line(s, INK, (X, Y + T + 3), (X + T - 1, Y + T + 3))
                if not (y > 0 and g[y - 1][x] == ch): pygame.draw.line(s, INK, (X, Y - 3), (X + T - 1, Y - 3))
                if not (x > 0 and g[y][x - 1] == ch): pygame.draw.line(s, INK, (X, Y - 3), (X, Y + T + 3))
                if not (x + 1 < COLS and g[y][x + 1] == ch): pygame.draw.line(s, INK, (X + T - 1, Y - 3), (X + T - 1, Y + T + 3))
            elif ch == "W":
                pygame.draw.rect(s, (120, 40, 52), (X, Y, T, T)); pygame.draw.rect(s, (220, 210, 190), (X, Y, T, 5))
                for k in range(7, T, 4): pygame.draw.line(s, (96, 30, 42), (X, Y + k), (X + T - 1, Y + k))
            elif ch in "[]":
                pygame.draw.rect(s, (80, 52, 30), (X + 4, Y - 4, 8, T + 4)); pygame.draw.rect(s, INK, (X + 4, Y - 4, 8, T + 4), 1)
    s = base
    ov = layer(setpiece.furniture_overlay_row(rid, room))                  # themed bed covers sit with the bed's front row
    setpiece.draw_furniture_overlay(ov, rid, room, TOP)
    # pillars & corner posts: raised blocks at corners/ends and every 5 tiles
    kb = {(x, y) for x, y, _ in room.get("kb_letters", [])}
    bp = room.get("theme", {}).get("posts")                                   # post sprite instead of pillar()
    bp = bp if bp and os.path.exists(os.path.join(setpiece.A, bp)) else None
    _ps = pygame.Surface(s.get_size()) if bp else None                        # scratch pillar() keeps the rnd stream
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] != "#": continue
            post = is_post(g, x, y)
            if post and (x, y) in kb:                   # letter cells: plain wall top (post drawn off-screen, keeps rnd)
                pillar(pygame.Surface(base.get_size()), x * T - 1, y * T + TOP - RAISE - 8, rnd, not is_wall(g, x, y + 1)); continue
            if post and (x, y) in wall_s:               # a raised post would cover the corridor
                pillar(_rs, x * T - 1, y * T + TOP - RAISE - 8, rnd, not is_wall(g, x, y + 1)); continue
            if post:
                pl = pillars.setdefault(y, pygame.Surface(base.get_size(), pygame.SRCALPHA))
                if (x, y) in wall_n:   # north wall of a corridor: same post, cut at the wall cell's bottom (no face over the runner)
                    ps = pygame.Surface(base.get_size(), pygame.SRCALPHA); py_ = y * T + TOP - RAISE - 8
                    pillar(ps, x * T - 1, py_, rnd, not is_wall(g, x, y + 1))
                    pl.blit(ps, (x * T - 2, py_), (x * T - 2, py_, T + 4, 2 * T)); continue
                if bp:
                    pillar(_ps, x * T - 1, y * T + TOP - RAISE - 8, rnd, not is_wall(g, x, y + 1))
                    pl.blit(setpiece.frame(bp, 18, 0 if not is_wall(g, x, y + 1) else 1), (x * T - 1, y * T + TOP - RAISE - 8)); continue
                pillar(pl, x * T - 1, y * T + TOP - RAISE - 8, rnd, not is_wall(g, x, y + 1))
    # wall decals (random and hand-placed) are kept off post cells and drawn after their row's posts (RAISE=8):
    # the post's 1px outline used to cut a decal next to it, and a decal on a post was hidden outright
    deco = {p[4] for p in setpiece.wall_spots(rid, room)} | {d["y"] for d in room["decor"]["decals"] if d["layer"] == "wall decal"}
    for row in sorted(set(layers) | set(pillars) | deco):                   # pillars of a row first, then its wall decals, then that row's furniture
        if row in pillars: s.blit(pillars[row], (0, 0))
        if row in deco: decor.draw_wall(s, room, TOP, 8, row); setpiece.draw_wall(s, rid, room, TOP, row)
        if row in layers: s.blit(layers[row], (0, 0))
    draw_kb_letters(s, room, TOP, RAISE)                                       # carved KB: wall-top decals over the finished wall tops
    try:
        arr = pygame.surfarray.array3d(s)    # snap blended near-magenta pixels back to the exact colour key (format-independent RGB)
        mask = (arr[..., 0] > 150) & (arr[..., 1] < 70) & (arr[..., 2] > 150)
        arr[mask] = (255, 0, 255); pygame.surfarray.blit_array(s, arr)
    except Exception as e: print("[castle diag] magenta snap skipped:", e)
    return s, TOP

def is_post(g, x, y):
    """raised wall post/pillar cell: corners, wall ends and every 5th cell of a straight run. A post covers its cell's
    wall top and face (plus 1px each side), so wall decals must not be placed on one"""
    if not (0 <= x < COLS and 0 <= y < ROWS) or g[y][x] != "#": return False
    nb = [is_wall(g, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    return ((nb[0] or nb[1]) and (nb[2] or nb[3])) or sum(nb) == 1 or (nb[0] and nb[1] and x % 5 == 2) or (nb[2] and nb[3] and y % 5 == 2)

def enclosed_furniture(g, walk):
    """cells of furniture groups (4-connected %@W[]) with no walkable cell around them: not visible in a room"""
    seen, out = set(), set()
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in seen or g[y][x] not in "%@W[]": continue
            comp, st = [], [(x, y)]; seen.add((x, y))
            while st:
                cx, cy = st.pop(); comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and (nx, ny) not in seen and g[ny][nx] in "%@W[]": seen.add((nx, ny)); st.append((nx, ny))
            if not any(0 <= cx + dx < COLS and 0 <= cy + dy < ROWS and walk[cy + dy][cx + dx]
                       for cx, cy in comp for dx in (-1, 0, 1) for dy in (-1, 0, 1)): out.update(comp)
    return out

def pillar(s, X, Y, rnd, show_face):
    w = T + 2
    vstones(s, pygame.Rect(X, Y, w, T), rnd)
    pygame.draw.rect(s, INK, (X, Y, w, T), 1)
    pygame.draw.line(s, (190, 184, 192), (X + 1, Y + 1), (X + w - 2, Y + 1))
    fr = pygame.Rect(X, Y + T, w, 8 + (FACE if show_face else 0))
    vstones(s, fr, rnd, face=True)
    pygame.draw.rect(s, INK, fr, 1)
    pygame.draw.line(s, (150, 144, 156), (X + 1, Y + T), (X + w - 2, Y + T))
    sh = pygame.Surface((w, 4), pygame.SRCALPHA); sh.fill((8, 6, 18, 90)); s.blit(sh, (X, fr.bottom))

def draw_gate(s, X, Y, rnd, g, x, y):
    pygame.draw.rect(s, (8, 6, 12), (X, Y - 8, T, T + 8))
    for bx in range(2, T, 4):
        pygame.draw.line(s, INK, (X + bx + 1, Y - 6), (X + bx + 1, Y + T - 1))
        pygame.draw.line(s, (128, 132, 146), (X + bx, Y - 6), (X + bx, Y + T - 1))
        s.set_at((X + bx, Y - 6), (210, 214, 224))
    for by in (Y - 1, Y + 8):
        pygame.draw.line(s, (112, 116, 128), (X, by), (X + T - 1, by)); pygame.draw.line(s, INK, (X, by + 1), (X + T - 1, by + 1))
    pygame.draw.rect(s, (110, 74, 42), (X, Y - 10, T, 4)); pygame.draw.line(s, (160, 116, 70), (X, Y - 10), (X + T - 1, Y - 10))
    pygame.draw.line(s, INK, (X, Y - 6), (X + T - 1, Y - 6))


def make_ogre():
    """hulking shaded ogre, ~2 tiles tall"""
    rnd = random.Random(8)
    w, h = 30, 34
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    sk = [(52, 72, 40), (76, 104, 54), (104, 134, 70), (140, 166, 94)]
    def blob(cx, cy, rx, ry):
        for y in range(int(cy-ry), int(cy+ry)+1):
            for x in range(int(cx-rx), int(cx+rx)+1):
                d = ((x-cx)/rx)**2 + ((y-cy)/ry)**2
                if d <= 1 and 0 <= x < w and 0 <= y < h:
                    l = (-(x-cx)/rx*.5 - (y-cy)/ry*.8)*.5 + .55 - d*.2 + (BAYER[y % 4][x % 4]/16-.5)*.3
                    s.set_at((x, y), sk[max(0, min(3, int(l*4)))])
    blob(15, 19, 11, 10)                 # torso
    blob(5, 20, 4, 7); blob(25, 20, 4, 7)   # arms
    blob(15, 8, 7, 7)                    # head
    pygame.draw.rect(s, (90, 62, 40), (6, 24, 18, 5)); pygame.draw.line(s, (130, 92, 56), (6, 24), (23, 24))  # loincloth
    pygame.draw.rect(s, (60, 44, 32), (8, 29, 5, 5)); pygame.draw.rect(s, (60, 44, 32), (17, 29, 5, 5))      # legs
    s.set_at((12, 7), (255, 70, 40)); s.set_at((17, 7), (255, 70, 40)); pygame.draw.line(s, INK, (11, 6), (13, 6)); pygame.draw.line(s, INK, (16, 6), (18, 6))
    pygame.draw.line(s, INK, (12, 11), (17, 11)); s.set_at((12, 10), (236, 230, 200)); s.set_at((17, 10), (236, 230, 200))
    pygame.draw.line(s, (100, 70, 40), (27, 10), (29, 28), 3); pygame.draw.circle(s, (120, 84, 50), (27, 9), 3)    # club weapon
    return outline(s)

def make_sword_item():
    s = pygame.Surface((18, 8), pygame.SRCALPHA)
    pygame.draw.line(s, INK, (1, 4), (16, 4), 3)
    pygame.draw.line(s, (230, 234, 244), (5, 3), (16, 3)); pygame.draw.line(s, (140, 148, 162), (5, 4), (16, 4))
    pygame.draw.line(s, (226, 176, 72), (4, 1), (4, 6)); pygame.draw.line(s, (110, 70, 40), (1, 4), (3, 4))
    return outline(s)

def make_helmet_item():
    s = pygame.Surface((14, 11), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (150, 156, 170), (0, 0, 14, 12)); pygame.draw.rect(s, (110, 116, 130), (0, 7, 14, 4))
    pygame.draw.line(s, (230, 234, 244), (3, 2), (8, 2)); pygame.draw.line(s, (80, 86, 100), (7, 6), (7, 10))
    return outline(s)

def make_fountain():
    s = pygame.Surface((3*T, 3*T), pygame.SRCALPHA)
    pygame.draw.ellipse(s, INK, (0, 6, 48, 40)); pygame.draw.ellipse(s, (120, 114, 124), (1, 7, 46, 37))
    pygame.draw.ellipse(s, (70, 66, 80), (5, 11, 38, 29)); pygame.draw.ellipse(s, (40, 90, 120), (7, 13, 34, 25))
    pygame.draw.ellipse(s, (70, 140, 170), (11, 16, 18, 8)); pygame.draw.line(s, (180, 220, 240), (14, 18), (22, 18))
    pygame.draw.rect(s, INK, (20, 4, 8, 22)); pygame.draw.rect(s, (140, 134, 144), (21, 5, 6, 20))
    pygame.draw.ellipse(s, (160, 210, 240), (18, 0, 12, 6))
    return s
