"""tower interiors (50 Bottom Of The East Tower, 61 Below The West Tower, 62 West Tower, 63 East Tower):
round-tower stone wall sheets (themed-wall hook), rounded pilaster posts, curved-joint tower flagstones, view-below
underlays (same landscape as #10/#11), tower stairs (1x2 up/down + 2x2 up, 'tower' variant -> art/tower_top/),
arrow slits with daylight + light patches on the floor (hand-placed lists for the game). python3 make_towers.py
The 2x2 spirals for rooms 50/61 are entries in art/spiral_stairs/make_spiral.py (PLACE) - run that too."""
import os, sys, math, random, json, copy
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from outdoor import stones, lichen, side_face, underlay, MORTAR, INK_
from art import lerp
import art3, setpiece
ROOMS = [50, 61, 62, 63]; TOP = 24; FACE = art3.FACE
TST = [(112, 102, 94), (98, 90, 88), (124, 114, 104), (90, 82, 84), (116, 106, 96)]     # older, warmer tower ashlar
SKY = [(150, 176, 200), (196, 214, 228), (236, 240, 236)]
files = {}
def save(name, sf, d=HERE): pygame.image.save(sf, os.path.join(d, name)); files[name] = sf; return sf
def sheet(tiles, w, h):
    s = surf(w * len(tiles), h); [s.blit(t, (i * w, 0)) for i, t in enumerate(tiles)]; return s
rnd = random.Random(2023)

def convex(s, rect, k=.35):
    """cylinder shading across a block: lit left-centre, dark right edge -> reads as a curved wall surface"""
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if not s.get_at((x, y)).a: continue
            u = (x - x0 + .5) / w; c = math.cos((u - .38) * math.pi)
            t = (1 - c) * k + (BAYER[y % 4][x % 4] / 16 - .5) * .08
            s.set_at((x, y), lerp(s.get_at((x, y))[:3], (24, 18, 30) if t > 0 else (232, 222, 210), abs(t)))

def wall_top(v):
    """thick round-tower wall top: big rubble-core blocks, a dressed curved coping course along the inner (south) edge"""
    s = surf(16, 16); stones(s, pygame.Rect(0, 0, 16, 16), rnd, [lerp(t, (64, 58, 66), .2) for t in TST], rowh=(6, 7, 8), dark=.38)
    for x in range(16):                                         # coping: bowed joint line (curvature cue)
        yy = 11 + round(1.2 * ((x - 7.5) / 8) ** 2 * 2)
        s.set_at((x, yy), MORTAR); s.set_at((x, yy - 1), lerp(s.get_at((x, yy - 1))[:3], (226, 214, 200), .35))
    for x in range(16): s.set_at((x, 0), (166, 156, 148))
    lichen(s, (0, 0, 16, 16), rnd, 1 + (v == 3) * 3)
    if v == 5:                                                  # loose rubble on the top
        for (x, y) in ((4, 5), (5, 5), (10, 3), (11, 7)): s.set_at((x, y), (138, 128, 118))
    return s

def wall_front(v):
    """inner face: large ashlar blocks with convex (cylindrical) shading per block - a curved tower wall; v4 iron ring,
    v5 putlog hole (scaffold socket)"""
    s = surf(16, FACE); r = random.Random(300 + v); y = 0; row = 0
    while y < FACE:
        h = 7 if y == 0 else FACE - y
        x = -(row % 2) * 6 - r.randrange(2)
        while x < 16:
            w = r.choice((8, 9, 10, 11, 12)); tone = lerp(r.choice(TST), (52, 46, 58), .32)
            pygame.draw.rect(s, tone, (x, y, w, h))
            rx = max(0, x); rw = min(16, x + w) - rx
            if rw > 0:
                sub = surf(w, h); sub.fill(tone); convex(sub, (0, 0, w, h), .42)
                s.blit(sub, (x, y))
            line(s, lerp(tone, (232, 222, 212), .35), (x + 1, y), (x + w - 2, y))
            pygame.draw.rect(s, MORTAR, (x, y, w, h), 1); x += w
        y += h; row += 1
    for x in range(16): s.set_at((x, 0), lerp(s.get_at((x, 0))[:3], (220, 210, 204), .45)); s.set_at((x, FACE - 1), MORTAR)
    for k in range(2):                                          # damp streaks
        x = r.randrange(2, 14)
        for yy in range(2, FACE - 1):
            if r.random() < .6: s.set_at((x, yy), lerp(s.get_at((x, yy))[:3], (36, 40, 40), .3))
    lichen(s, (0, FACE - 4, 16, 3), r, 1)
    if v == 4:
        pygame.draw.circle(s, (40, 34, 36), (8, 8), 2, 1); s.set_at((7, 6), (120, 110, 100)); s.set_at((8, 5), (30, 24, 28))
    if v == 5: pygame.draw.rect(s, (14, 10, 18), (5, 3, 3, 3)); s.set_at((5, 6), (150, 140, 130))
    return s

def post(show_face):
    """round pilaster / buttress replacing art3.pillar() (18 x 16+8+FACE, same geometry): disc cap with a ring course,
    cylinder-shaded shaft"""
    w = 18; H = 16 + 8 + FACE; s = surf(w, H)
    stones(s, pygame.Rect(0, 0, w, 16), rnd, TST, rowh=(5, 6))
    pygame.draw.ellipse(s, lerp(TST[1], (40, 34, 46), .15), (2, 2, 14, 11)); pygame.draw.ellipse(s, (44, 38, 50), (2, 2, 14, 11), 1)
    for x in range(5, 11): s.set_at((x, 3), lerp(TST[2], (230, 220, 210), .3))
    pygame.draw.rect(s, INK_, (0, 0, w, 16), 1)
    fh = 8 + (FACE if show_face else 0)
    stones(s, pygame.Rect(0, 16, w, fh), rnd, TST, face=True); convex(s, (1, 16, w - 2, fh), .5)
    pygame.draw.line(s, (176, 166, 158), (1, 16), (w - 2, 16)); pygame.draw.rect(s, INK_, (0, 16, w, fh), 1)
    lichen(s, (1, 1, w - 2, 16 + fh - 2), rnd, 2)
    if not show_face: s.fill((0, 0, 0, 0), (0, 16 + 8, w, FACE))
    return s

def floor_tile(v):
    """tower flagstones: big slabs cut on curved joints (laid in rings around the tower's centre), worn, a little straw"""
    s = surf(16, 16); r = random.Random(500 + v); pal = [(62, 56, 58), (74, 68, 68), (86, 80, 78), (98, 92, 88), (112, 104, 98)]
    cx, cy, R = (r.choice((-10, 26)), r.choice((-12, 28)), r.choice((16, 20, 24)))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy); slab = d < R
            b = .55 + (.07 if slab else -.05) + (BAYER[y % 4][x % 4] / 16 - .5) * .2 + ((x * 5 + y * 11 + v) % 13 == 0) * .1
            s.set_at((x, y), pal[max(0, min(4, int(b * 5)))])
            if abs(d - R) < .6: s.set_at((x, y), (40, 36, 44))
    for k in range(16): s.set_at((k, 15), (44, 40, 48)); s.set_at((15, k), (44, 40, 48)); s.set_at((k, 0), pal[3])
    for _ in range((v in (1, 3)) * 2):                           # straw
        x, y = r.randrange(1, 14), r.randrange(1, 14); c = r.choice(((176, 150, 84), (150, 124, 66)))
        s.set_at((x, y), c); s.set_at((x + 1, y + r.choice((0, 1))), c)
    if v == 4:                                                  # worn hollow in the middle
        for y in range(5, 11):
            for x in range(4, 12):
                if ((x - 7.5) / 4) ** 2 + ((y - 8) / 3) ** 2 < 1: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (120, 112, 104), .3))
    if v == 5:                                                  # chipped slab corner
        for (x, y) in ((3, 3), (4, 3), (3, 4)): s.set_at((x, y), (48, 44, 50))
    return s

# ---- arrow slits (wall decals) + daylight patches (floor decals) ----
def slit_face():
    """north-wall face decal (16 x FACE): splayed embrasure, a 2px slit of daylight, lit sill"""
    s = surf(16, FACE)
    for y in range(1, FACE - 1):
        hw = 2 + (FACE - y) // 4
        for x in range(8 - hw, 8 + hw): s.set_at((x, y), lerp((44, 38, 46), (88, 80, 80), abs(x - 7.5) / hw))
    for y in range(2, FACE - 3):
        for x in (7, 8): s.set_at((x, y), SKY[1] if y > 3 else SKY[0])
    s.set_at((7, 2), SKY[2]); s.set_at((8, FACE - 4), SKY[2])
    line(s, (180, 170, 160), (4, FACE - 2), (11, FACE - 2)); line(s, MORTAR, (4, FACE - 1), (11, FACE - 1))
    for y in range(1, FACE - 1): s.set_at((8 - (2 + (FACE - y) // 4) - 1, y), INK_); s.set_at((8 + (2 + (FACE - y) // 4), y), INK_)
    return s
def slit_side(east):
    """side-face decal (16 x 16+FACE): the slit seen on an east (or west) wall's inner side face. Frame 0 = east mount
    (face in frame x 8..15, at ((x-1)*16, y*16+TOP-8) like CHAIN_WALL), frame 1 = west mount (face in x 0..7, at ((x+1)*16, ...))"""
    s = surf(16, 16 + FACE); x0 = 8 if east else 0
    for y in range(6, 16 + FACE - 4):
        for x in range(x0 + 1, x0 + 7): s.set_at((x, y), (50, 44, 52) if (x - x0) in (1, 6) else (70, 64, 66))
        for x in (x0 + 3, x0 + 4): s.set_at((x, y), SKY[1] if y > 8 else SKY[2])
    line(s, INK_, (x0 + 1, 5), (x0 + 6, 5)); line(s, (176, 166, 156), (x0 + 1, 16 + FACE - 4), (x0 + 6, 16 + FACE - 4))
    return s
def light_patch(direction):
    """floor decal 16x16: soft dithered daylight from a slit (alpha). 0 = from the north wall, 1 = from an east wall, 2 = from a west wall"""
    s = surf(16, 16)
    for y in range(16):
        for x in range(16):
            u, w = {0: (y / 15, abs(x - 7.5)), 1: (1 - x / 15, abs(y - 7.5)), 2: (x / 15, abs(y - 7.5))}[direction]
            half = 1.5 + u * 4.5
            if w < half and BAYER[y % 4][x % 4] / 16 < (1 - u * .8) * (1 - w / half) * 1.3:
                s.set_at((x, y), (240, 234, 210, int(150 * (1 - u * .5))))
    return s

TOPS = [wall_top(v) for v in range(6)]; FRONTS = [wall_front(v) for v in range(6)]
SIDES = [side_face(rnd, "left", TST) for _ in range(2)] + [side_face(rnd, "right", TST) for _ in range(2)]
for sd in SIDES: convex(sd, (0, 0, 8, 16 + FACE), .18)
save("tower_wall_tops.png", sheet(TOPS, 16, 16)); save("tower_wall_fronts.png", sheet(FRONTS, 16, FACE)); save("tower_side_walls.png", sheet(SIDES, 8, 16 + FACE))
POST = surf(36, 16 + 8 + FACE); POST.blit(post(True), (0, 0)); POST.blit(post(False), (18, 0)); save("tower_post.png", POST)
save("tower_floor_in.png", sheet([floor_tile(v) for v in range(6)], 16, 16))
SLIT = save("tower_slit.png", slit_face()); SLITS = save("tower_slit_side.png", sheet([slit_side(True), slit_side(False)], 16, 16 + FACE))
LIGHT = save("tower_slit_light.png", sheet([light_patch(k) for k in range(3)], 16, 16))

# ---- tower stairs: art/stairs drawers, tower palette, written into art/tower_top/ ('tower' variant loads from there) ----
TT = os.path.join(ART, "tower_top")
src = open(os.path.join(ART, "stairs", "make_stairs.py")).read(); ns = {"__file__": os.path.join(ART, "stairs", "make_stairs.py")}
exec(src[:src.index("def save(")], ns)
ns["PAL"]["tower"] = dict(ink=(16, 10, 16), top=[(78, 70, 70), (98, 90, 86), (118, 108, 100), (156, 146, 134)],
                          riser=[(36, 30, 38), (54, 48, 56), (72, 64, 68)], mortar=(30, 26, 34), void=(12, 10, 18), accent=(150, 124, 70))
NEW_STAIRS = {}
for d, w, h in (("up", 1, 2), ("down", 1, 2), ("up", 2, 2)):
    n = f"stairs_{d}_tower_{w}x{h}.png"; NEW_STAIRS[n] = save(n, (ns["up"] if d == "up" else ns["down"])("tower", w, h), TT)
copy_to_game(TT, "tower_top")

# ---- per-room data ----
R = rooms(); D = "towers/"
ULS = {rid: save(f"underlay_{rid}.png", underlay(rid, R[rid], TOP, depth=1.3 if rid in (50, 61) else 1.5, seed=10)) for rid in ROOMS}
copy_to_game(HERE, "towers")
THEME = {str(rid): {"name": R[rid]["name"], "walls": D + "tower_", "floor_tiles": D + "tower_floor_in.png", "underlay": D + f"underlay_{rid}.png",
                    "posts": D + "tower_post.png", **({"stairs": "tower"} if rid in (62, 63) else {})} for rid in ROOMS}
# arrow slits: setpiece wall-decal tuples (file, fw, var, x, y[, mount]) + floor light (file, fw, var, x, y)
SL = {50: [("east", 23, 9), ("west", 14, 8)], 61: [("east", 9, 9), ("west", 0, 8)],
      62: [("face", 3, 5), ("face", 6, 5), ("west", 0, 9)], 63: [("face", 18, 5), ("face", 21, 5), ("east", 23, 8)]}
WALL, FLOOR = {}, {}
_MAN = os.path.join(HERE, "manifest.json")   # the game may tune placements in the manifest (d03397d): those win over SL
_KEEP = json.load(open(_MAN))["rooms_detail"] if os.path.exists(_MAN) else {}
for rid, lst in SL.items():
    if str(rid) in _KEEP:
        WALL[rid] = [tuple(p) for p in _KEEP[str(rid)]["wall_decals"]]; FLOOR[rid] = [tuple(p) for p in _KEEP[str(rid)]["floor_decals"]]; continue
    g = R[rid]["grid"]; W_, F_ = [], []
    for m, x, y in lst:
        assert g[y][x] == "#" and not art3.is_post(g, x, y), (rid, x, y)
        if m == "face": W_.append((D + "tower_slit.png", 16, 0, x, y)); F_.append((D + "tower_slit_light.png", 16, 0, x, y + 1))
        elif m == "east": W_.append((D + "tower_slit_side.png", 16, 0, x, y, "east")); F_.append((D + "tower_slit_light.png", 16, 1, x - 1, y))
        else: W_.append((D + "tower_slit_side.png", 16, 1, x, y, "west")); F_.append((D + "tower_slit_light.png", 16, 2, x + 1, y))
        assert R[rid]["walk"][F_[-1][4]][F_[-1][3]], (rid, F_[-1])
    WALL[rid], FLOOR[rid] = W_, F_
def bfs(walk, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and walk[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
REACH = {}
for rid in ROOMS:
    w = R[rid]["walk"]; cells = [(x, y) for y in range(18) for x in range(24) if w[y][x]]
    comp = bfs(w, cells[0]); REACH[rid] = len(comp) == len(cells)
POSTS = {rid: [[x, y] for y in range(18) for x in range(24) if art3.is_post(R[rid]["grid"], x, y)] for rid in ROOMS}
STAIRS = {rid: [{"glyph": ch, "cell": [x, y], "size": [w, h]} for ch, x, y, w, h in art3.stair_blocks(R[rid]["grid"])] for rid in ROOMS}

man = {"set": "towers", "issues": [20, 21, 22, 23], "rooms": ROOMS,
 "sheets": {
  "tower_wall_tops.png": {"cell": [16, 16], "cols": 6, "layout": "same as batt_wall_tops / room83_wall_tops", "content": "thick round-tower wall top, rubble core, bowed coping joint along the inner edge; v3 lichen, v5 loose rubble"},
  "tower_wall_fronts.png": {"cell": [16, FACE], "cols": 6, "layout": "same as room83_wall_fronts", "content": "big ashlar blocks with cylindrical shading per block (curved tower wall), damp streaks; v4 iron ring, v5 putlog hole"},
  "tower_side_walls.png": {"cell": [8, 16 + FACE], "cols": 4, "layout": "cols 0-1 west wall (lit), 2-3 east wall (shadowed)"},
  "tower_post.png": {"frame_size": [18, 16 + 8 + FACE], "frames": 2, "frame_use": "0 show_face, 1 no face (as batt_post)", "anchor": "art3.pillar (X, Y)", "content": "round pilaster: disc cap with ring course, cylinder-shaded shaft"},
  "tower_floor_in.png": {"cell": [16, 16], "variants": 6, "rule": "thash(x,y) % 6 (floor_tiles hook)", "content": "tower flagstones on curved (ring) joints, straw; v4 worn hollow, v5 iron drain grate"},
  "tower_slit.png": {"frame_size": [16, FACE], "mount": "face (setpiece.wall_xy, bottom-aligned on the north wall face)", "content": "splayed arrow slit with daylight"},
  "tower_slit_side.png": {"frame_size": [16, 16 + FACE], "frames": 2, "frame_use": "0 = east mount at ((x-1)*16, y*16+TOP-8) (existing 'east'); 1 = west mount at ((x+1)*16, y*16+TOP-8) (NEW mount, needs code)"},
  "tower_slit_light.png": {"frame_size": [16, 16], "frames": 3, "frame_use": "0 below a north slit, 1 west of an east slit, 2 east of a west slit", "layer": "floor decal, alpha (draw after the floor tiles, before stairs/objects)"},
  "underlay_<rid>.png": {"size": [384, 18 * 16 + TOP], "blit_at": [0, 0], "content": "the #10/#11 dusk view far below (same landscape) with the tower's outer wall dropping into the haze; 62/63 hazier (higher up)"},
  "../tower_top/stairs_{up,down}_tower_1x2.png, stairs_up_tower_2x2.png": {"layout": "art/stairs drawers, tower palette", "note": "theme stairs 'tower' loads from assets/tower_top/; the existing stairs_down_tower_2x2 (roof trapdoor) is untouched"},
  "../spiral_stairs (rooms 50, 61)": {"file": "spiral_up_large.png", "note": "entries added to make_spiral.py PLACE: block (18,8) room 50, (4,8) room 61, world_anchor (304,160)/(80,160), depth-sorted; the existing data-driven spiral hook draws them"}},
 "rooms_detail": {str(rid): {"name": R[rid]["name"], "text": R[rid]["description"], "stairs": STAIRS[rid], "post_cells": POSTS[rid],
                             "wall_decals": [list(p) for p in WALL[rid]], "floor_decals": [list(p) for p in FLOOR[rid]], "blocking_added": [],
                             "bfs_all_walkable_connected": REACH[rid]} for rid in ROOMS},
 "room_themes_added": THEME,
 "integration_notes": [
  "wall decals: add TOWER_WALL = {rid: [...]} (rooms_detail.wall_decals) to setpiece.wall_spots and TOWER_FLOOR (floor_decals) to draw_floor, like CHAIN_WALL/CHAIN_FLOOR",
  "new 'west' mount in setpiece.wall_xy: return ((x+1)*T, y*T+top-8) (the west wall's lit inner side face; frame 1 of tower_slit_side.png); wall_cells() should treat it like 'east' (one cell)",
  "optional: a dim cool light point at each floor light patch (daylight), and/or exclude these rooms from sconce decor so random decals don't sit next to the slits",
  "no blocking changes: slits/light patches are decals; stair cells unchanged"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
copy_to_game(HERE, "towers")

# ---- previews: real bakes (theme hooks are live in art3/setpiece), slits + light simulated on top ----
def bake(rid, after):
    room = copy.deepcopy(R[rid]); [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]
    room["theme"] = THEME[str(rid)] if after else {}
    raw, top = art3.bake_room(rid, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
    b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if after:
        for f, fw, var, x, y in FLOOR[rid]: b.blit(LIGHT.subsurface((var * 16, 0, 16, 16)), (x * 16, y * 16 + top))
        for p in WALL[rid]:
            f, fw, var, x, y = p[:5]; m = (p[5:] or ("face",))[0]
            if m == "face": X, Y = setpiece._face(x, y, top); b.blit(SLIT, (X, Y))
            else: b.blit(SLITS.subsurface((var * 16, 0, 16, 16 + FACE)), (((x - 1) if m == "east" else (x + 1)) * 16 - (0 if m == "east" else 0), y * 16 + top - 8))
        sp = art3.spiral(rid)
        if sp: b.blit(sp["img"], (sp["world"][0] - sp["anchor"][0], sp["world"][1] - sp["anchor"][1] + top))
    return b
font = pygame.font.Font(None, 18)
for rid in ROOMS:
    P = pygame.Surface((2 * 384 * 2 + 30, 312 * 2 + 30)); P.fill((40, 36, 48))
    for j, af in enumerate((False, True)):
        x0 = 10 + j * (384 * 2 + 10)
        P.blit(font.render(f"#{ {50: 20, 61: 21, 62: 22, 63: 23}[rid]} room {rid} {R[rid]['name']} - {'AFTER' if af else 'before'}", True, (230, 220, 200)), (x0, 6))
        P.blit(pygame.transform.scale(bake(rid, af), (768, 624)), (x0, 24))
    pygame.image.save(P, os.path.join(HERE, f"preview_{rid}.png"))
Z = pygame.Surface((240, 60)); Z.fill((40, 36, 48))
Z.blit(files["tower_wall_tops.png"], (2, 2)); Z.blit(files["tower_wall_fronts.png"], (2, 20)); Z.blit(files["tower_floor_in.png"], (2, 38))
Z.blit(POST, (100, 2)); Z.blit(SLIT, (140, 2)); Z.blit(SLITS, (160, 2)); Z.blit(LIGHT, (100, 42))
for i, n in enumerate(NEW_STAIRS.values()): Z.blit(n, (196 + i * 0, 2) if i == 2 else (150 + i * 18, 26))
pygame.image.save(pygame.transform.scale(Z, (960, 240)), os.path.join(HERE, "preview_sheets.png"))
print("ok", REACH)
