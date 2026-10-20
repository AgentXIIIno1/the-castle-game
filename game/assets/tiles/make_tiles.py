"""Tile cleanup sheets: side-wall depth, cleaner dirt, room 83 many-coloured walls. python3 make_tiles.py
1x, 16px grid, RGBA. Stone drawing mirrors art3.vstones (bevel, mortar, Bayer shading) with tone sets as a parameter."""
import os, sys, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art import lerp
from art3 import STONE_TONES, FACE
T = 16; SIDE = 8                                     # side face width (was 6 in art3) for more depth
MORTAR = (24, 20, 30)
JEWEL = [(206, 70, 82), (84, 124, 224), (82, 184, 104), (172, 100, 214), (236, 192, 84), (80, 196, 206)]   # brightened for the unlit room
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
def side_face(rnd, side, tones):
    """side wall: cap strip on top (CAP 6) + inner face SIDE px wide, lit edge toward room, deep shadow toward wall"""
    s = surf(SIDE, T + FACE); stones(s, pygame.Rect(0, 0, SIDE, T + FACE), rnd, tones, face=True)
    for y in range(T + FACE):
        for x in range(SIDE):
            d = x / (SIDE - 1) if side == "left" else 1 - x / (SIDE - 1)       # 0 at wall, 1 at room edge
            c = s.get_at((x, y)); t = (1 - d) * .55
            if (BAYER[y % 4][x % 4] / 16) < (1 - d) * .4: t += .1
            s.set_at((x, y), (*lerp(c[:3], (14, 10, 22), t), 255))
    ex = SIDE - 1 if side == "left" else 0
    for y in range(T + FACE): s.set_at((ex, y), lerp(s.get_at((ex, y))[:3], (210, 204, 214), .3))   # rim highlight on room edge
    for x in range(SIDE): s.set_at((x, 0), (200, 194, 204)); s.set_at((x, T + FACE - 1), MORTAR)
    return s
def wall_top(rnd, tones): s = surf(T, T); stones(s, pygame.Rect(0, 0, T, T), rnd, tones); pygame.draw.line(s, (180, 174, 186), (0, 0), (T - 1, 0)); return s
def wall_front(rnd, tones):
    s = surf(T, FACE); stones(s, pygame.Rect(0, 0, T, FACE), rnd, tones, face=True)
    for x in range(T): s.set_at((x, 0), lerp(s.get_at((x, 0))[:3], (220, 214, 224), .5)); s.set_at((x, FACE - 1), MORTAR)
    return s
def dirt(rnd, seed):
    """3-tone dirt with wrap-around soft value noise (tileable), ordered dither, sparse pebbles + few grass sprigs. No big blotches."""
    import math
    pal = [(70, 60, 36), (96, 70, 44), (118, 88, 56), (138, 104, 66)]   # = art3 garden noise-dirt palette
    g = [[rnd.random() for _ in range(4)] for _ in range(4)]
    def n(x, y):
        fx, fy = x / 4, y / 4; ix, iy = int(fx), int(fy); tx, ty = fx - ix, fy - iy
        a = g[iy % 4][ix % 4]; b = g[iy % 4][(ix + 1) % 4]; c = g[(iy + 1) % 4][ix % 4]; d = g[(iy + 1) % 4][(ix + 1) % 4]
        sx, sy = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty); return (a * (1 - sx) + b * sx) * (1 - sy) + (c * (1 - sx) + d * sx) * sy
    s = surf(T, T)
    for y in range(T):
        for x in range(T):
            v = .35 + n(x, y) * .3 + (BAYER[y % 4][x % 4] / 16 - .5) * .25
            s.set_at((x, y), pal[max(0, min(2, int(v * 3)))])
    for _ in range(rnd.randrange(2, 4)):                                        # pebbles: 2px with highlight + dark underside
        x, y = rnd.randrange(1, T - 2), rnd.randrange(1, T - 2)
        s.set_at((x, y), pal[3]); s.set_at((x + 1, y), pal[2]); s.set_at((x, y + 1), (48, 34, 26)); s.set_at((x + 1, y + 1), (48, 34, 26))
    if seed % 3 == 0:
        x, y = rnd.randrange(2, T - 2), rnd.randrange(3, T - 1)
        s.set_at((x, y), (36, 58, 28)); s.set_at((x, y - 1), (96, 130, 52)); s.set_at((x - 1, y - 2), (118, 150, 62)); s.set_at((x + 1, y - 2), (132, 162, 70))
    return s
def sheet(tiles, w, h, cols):
    rows = (len(tiles) + cols - 1) // cols; S = surf(w * cols, h * rows)
    for i, t in enumerate(tiles): S.blit(t, ((i % cols) * w, (i // cols) * h))
    return S
rnd = random.Random(83); out = {}
def save(name, S): pygame.image.save(S, os.path.join(HERE, name)); return name
# --- side walls (stone)
sl = [side_face(rnd, "left", STONE_TONES) for _ in range(4)]; sr = [side_face(rnd, "right", STONE_TONES) for _ in range(4)]
save("side_walls.png", sheet(sl + sr, SIDE, T + FACE, 4))
dt = [dirt(random.Random(i), i) for i in range(8)]
save("dirt_floor.png", sheet(dt, T, T, 8))
jt = [wall_top(rnd, [JEWEL[i % 6], lerp(JEWEL[(i + 2) % 6], (200, 190, 200), .1), JEWEL[(i + 4) % 6]]) for i in range(6)]
jf = [wall_front(rnd, [JEWEL[i % 6], JEWEL[(i + 1) % 6], JEWEL[(i + 3) % 6]]) for i in range(6)]
jl = [side_face(rnd, "left", JEWEL) for _ in range(2)] + [side_face(rnd, "right", JEWEL) for _ in range(2)]
save("room83_wall_tops.png", sheet(jt, T, T, 6)); save("room83_wall_fronts.png", sheet(jf, T, FACE, 6)); save("room83_side_walls.png", sheet(jl, SIDE, T + FACE, 4))

# ---------- dirt autotile (4-neighbour mask, alpha edges) ----------
DPAL = [(70, 60, 36), (96, 70, 44), (118, 88, 56), (138, 104, 66)]
def dirt_auto(mask, var):
    """mask bits: 1=N 2=E 4=S 8=W neighbour is dirt. Interior opaque; edges toward non-dirt fade with irregular, dithered alpha."""
    r = random.Random(mask * 31 + var * 7); base = dirt(random.Random(100 + var * 16 + mask), var + 1)
    edge = {k: [r.randrange(3, 7) for _ in range(T)] for k in "NESW"}
    for k in "NESW":                                       # smooth the depth profile so edges look organic, not noisy
        e = edge[k]; edge[k] = [round((e[i - 1] + e[i] * 2 + e[(i + 1) % T]) / 4) for i in range(T)]
    out = surf(T, T)
    for y in range(T):
        for x in range(T):
            a = 1.0
            for bit, k, d, i in ((1, "N", y, x), (2, "E", T - 1 - x, y), (4, "S", T - 1 - y, x), (8, "W", x, y)):
                if not mask & bit: a = min(a, (d - edge[k][i] + 3) / 4)
            # concave corners: neighbours both dirt but diagonal unknown -> keep opaque (game fills diagonals with its noise)
            a = max(0.0, min(1.0, a))
            if a <= 0: continue
            if a < 1 and BAYER[y % 4][x % 4] / 16 > a: continue   # dithered fade
            c = base.get_at((x, y))[:3]
            if a < 1: c = DPAL[1] if (x + y) % 3 else DPAL[0]      # darker damp rim like the noise dirt edge
            out.set_at((x, y), (*c, 255))
    return out
auto = [[dirt_auto(m, v) for m in range(16)] for v in range(2)]
save("dirt_autotile.png", sheet(auto[0] + auto[1], T, T, 16))
# ---------- room 83 emissive + bright fallback ----------
def emissive_of(tile, rate=3):
    """gem glints: brightest bevel pixels of each stone, saturated; drawn after lighting (unaffected by darkness)."""
    e = surf(*tile.get_size()); W, H = tile.get_size()
    for y in range(H):
        for x in range(W):
            c = tile.get_at((x, y))
            if c.a and max(c[:3]) > 150 and (x * 7 + y * 13) % rate == 0:
                m = max(c[:3]); e.set_at((x, y), (*[min(255, int(v / m * 255)) for v in c[:3]], 210))
                for dx, dy in ((1, 0), (0, 1)):
                    if 0 <= x + dx < W and 0 <= y + dy < H and tile.get_at((x + dx, y + dy)).a: e.set_at((x + dx, y + dy), (*[int(v / m * 200) for v in c[:3]], 90))
    return e
def bright(tile): return tint(tile, lambda c: lerp(c, (255, 250, 245), .28))
for nm, tl, w, h, cols in (("room83_wall_tops", jt, T, T, 6), ("room83_wall_fronts", jf, T, FACE, 6), ("room83_side_walls", jl, SIDE, T + FACE, 4)):
    save(nm + "_emissive.png", sheet([emissive_of(t) for t in tl], w, h, cols)); save(nm + "_bright.png", sheet([bright(t) for t in tl], w, h, cols))
man = {"tile_px": T, "notes": "1x RGBA, nearest, no baked shadow/glow (wall AO stays game-side). Pick variant per cell with a hash of (x, y) like art3 does.",
 "sheets": [
  {"file": "side_walls.png", "cell": [SIDE, T + FACE], "cols": 4, "rows": 2, "row0": "left-wall inner face (wall on left, room on right)", "row1": "right-wall inner face",
   "maps_to": "art3.bake_room side faces (currently 6px vstones face beside '#' cells)", "anchor": "top-left; left face at (X+T, Y) of the wall cell, right face at (X-SIDE, Y). Height covers cell + FACE so it meets the front-face run.",
   "change": "8px wide (was 6), lit rim on room edge, dithered falloff into the wall for depth"},
  {"file": "dirt_floor.png", "cell": [T, T], "cols": 8, "rows": 1, "maps_to": "garden dirt patches (art3.bake_floor_np garden dirt mask) - fill dirt-mask cells with these instead of palettised noise",
   "anchor": "top-left of cell", "change": "3-tone tileable ordered-dither dirt, sparse pebbles, occasional grass sprig; no large blotches"},
  {"file": "dirt_autotile.png", "cell": [T, T], "cols": 16, "rows": 2, "maps_to": "garden dirt cells (art3 dirt_cells) - REPLACES dirt_floor.png for gardens",
   "index_rule": "col = N*1 + E*2 + S*4 + W*8 where each bit = that 4-neighbour cell is also a dirt cell; row = variant (thash(cx,cy) % 2)",
   "blend": "RGBA: interior opaque, sides facing non-dirt fade out with irregular dithered alpha so the game's noise dirt/grass shows through. Blit with normal alpha over the baked noise floor. Isolated cells (col 0) become organic blobs, not squares.",
   "palette": "same 4 colours as art3 garden noise dirt"},
  {"file": "room83_wall_tops.png", "cell": [T, T], "cols": 6, "rows": 1, "maps_to": "room 83 (King's Secret Room, 'walls are many colours') '#' wall tops", "anchor": "top-left of cell (raised by CAP like stone tops)"},
  {"file": "room83_wall_fronts.png", "cell": [T, FACE], "cols": 6, "rows": 1, "maps_to": "room 83 front faces", "anchor": "top-left, directly below the wall top"},
  {"file": "room83_side_walls.png", "cell": [SIDE, T + FACE], "cols": 4, "rows": 1, "maps_to": "room 83 side faces: cols 0-1 left, 2-3 right", "anchor": "as side_walls.png"},
  {"file": "room83_*_emissive.png (tops, fronts, side_walls)", "cell": "same as the base sheet", "maps_to": "same cells/positions as each room83 base sheet",
   "use": "EMISSIVE: draw after the darkness/lighting overlay (dark_full / dark_lit) at the same positions as the base wall tiles, normal alpha blend (or BLEND_ADD). Never darkened. Optional twinkle: modulate alpha by 0.6-1.0 per tile with a slow sine."},
  {"file": "room83_*_bright.png (tops, fronts, side_walls)", "cell": "same as base", "use": "FALLBACK: drop-in replacement for the base sheets if no emissive pass is added (base lifted ~28% toward white). With the emissive pass, keep the normal base sheets."}]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# --- preview: sheets at 4x + mock rooms at 2x
import art3
rooms = {r["id"]: r for r in json.load(open(os.path.join(GAME, "../map/rooms.json")))["rooms"]}
def mock(tops, fronts, lefts, rights, floor, w=8, h=6):
    S = surf(w * T + 2 * SIDE, h * T + FACE + T); r = random.Random(1)
    for y in range(h):
        for x in range(w): S.blit(floor(x, y), (SIDE + x * T, T + FACE + y * T))
    for x in range(w): S.blit(tops[(x * 7) % len(tops)], (SIDE + x * T, 0)); S.blit(fronts[(x * 5) % len(fronts)], (SIDE + x * T, T))
    for y in range(h):
        S.blit(tops[(y * 3) % len(tops)], (SIDE - T + 0, T + FACE + y * T)) if False else None
        S.blit(lefts[y % len(lefts)], (0, T + y * T)); S.blit(rights[y % len(rights)], (SIDE + w * T, T + y * T))
    return S
fl = art3.bake_floor(5, rooms[5], False)
stone_t = [wall_top(rnd, STONE_TONES) for _ in range(4)]; stone_f = [wall_front(rnd, STONE_TONES) for _ in range(4)]
m1 = mock(stone_t, stone_f, sl, sr, lambda x, y: fl.subsurface((x * T, y * T, T, T)))
m2 = mock(stone_t, stone_f, sl, sr, lambda x, y: dt[(x * 3 + y * 5) % 8])
m3 = mock(jt, jf, jl[:2], jl[2:], lambda x, y: art3.bake_floor(83, rooms[83], False).subsurface((x * T, y * T, T, T)))
font = pygame.font.Font(None, 20); Z = 4
items = [("side_walls", "side_walls.png"), ("dirt_floor", "dirt_floor.png"), ("room83 tops", "room83_wall_tops.png"), ("room83 fronts", "room83_wall_fronts.png"), ("room83 sides", "room83_side_walls.png")]
P = pygame.Surface((1100, 1050)); P.fill((40, 36, 48)); y = 8
for lab, f in items:
    im = pygame.image.load(os.path.join(HERE, f)); P.blit(font.render(lab, True, (230, 220, 200)), (8, y)); P.blit(pygame.transform.scale(im, (im.get_width() * Z, im.get_height() * Z)), (130, y)); y += im.get_height() * Z + 10
x = 8
for lab, m in (("mock: stone sides (2x)", m1), ("mock: dirt floor (2x)", m2), ("mock: room 83 (2x)", m3)):
    P.blit(font.render(lab, True, (230, 220, 200)), (x, y)); P.blit(pygame.transform.scale(m, (m.get_width() * 2, m.get_height() * 2)), (x, y + 18)); x += m.get_width() * 2 + 20
pygame.image.save(P, os.path.join(HERE, "preview.png")); print("ok", y)
