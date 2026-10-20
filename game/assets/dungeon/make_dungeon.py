"""room 80 Dungeon / #25 room 81 Dungeon Annex: cell bars (barred cell windows on wall faces), wall shackles,
straw, a drain; reuses #7 wall_chains.png (east wall) and chain_bones.png (floor). python3 make_dungeon.py
Placements in manifest rooms_detail use the setpiece tuple format: wall (file, fw, var, x, y[, mount]), floor (file, fw, var, x, y[, flip])."""
import os, sys, random, json, copy
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from art import lerp
import art3, setpiece
FACE = art3.FACE; INK = (14, 10, 20)
IR = [(26, 24, 32), (44, 42, 52), (70, 68, 78), (104, 102, 110), (150, 148, 156)]
RUST = [(92, 50, 32), (128, 72, 40)]
STRAW = [(92, 74, 40), (128, 104, 56), (166, 136, 72), (198, 170, 98)]
files = {}
def save(n, sf): pygame.image.save(sf, os.path.join(HERE, n)); files[n] = sf; return sf
def sheet(t, w, h):
    s = surf(w * len(t), h); [s.blit(x, (i * w, 0)) for i, x in enumerate(t)]; return s

def bars(v):
    """16 x FACE face decal: dark cell window in the wall face with 3 iron bars + a riveted cross band; v1 one bar bent"""
    s = surf(16, FACE)
    pygame.draw.rect(s, (10, 8, 14), (2, 1, 12, FACE - 3))
    for y in range(1, FACE - 2):                                    # faint depth gradient inside the cell
        for x in range(3, 13):
            if BAYER[y % 4][x % 4] / 16 < .25 - y * .015: s.set_at((x, y), (26, 22, 32))
    for i, bx in enumerate((4, 8, 11)):
        for y in range(1, FACE - 2):
            x = bx + (1 if v == 1 and i == 1 and 4 <= y <= 7 else 0)
            s.set_at((x, y), IR[3]); s.set_at((x + 1, y), IR[1])
    for x in range(2, 14): s.set_at((x, 5), IR[2]); s.set_at((x, 6), IR[0])
    for x in (4, 8, 11): s.set_at((x, 5), IR[4])                   # rivets / rim light
    pygame.draw.rect(s, INK, (1, 0, 14, FACE - 1), 1)
    line(s, (150, 140, 130), (2, FACE - 2), (13, FACE - 2))        # stone sill
    s.set_at((5, FACE - 2), RUST[1]); s.set_at((9, FACE - 3), RUST[0])   # rust drips onto the sill
    return s

def shackles(v):
    """16x24 'hang' decal (top at the wall face top, hangs past the wall foot): wall plate + ring, chain(s), open manacles"""
    s = surf(16, 24); u = surf(16, 24)
    def chain(x0, y0, x1, y1):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(n + 1):
            x = round(x0 + (x1 - x0) * k / n); y = round(y0 + (y1 - y0) * k / n)
            u.set_at((x, y), IR[3] if k % 2 else IR[1])
    def cuff(cx, cy):
        pygame.draw.circle(u, IR[2], (cx, cy), 2, 1); u.set_at((cx - 1, cy - 2), IR[4]); u.set_at((cx + 2, cy), (0, 0, 0, 0))
    if v == 0:
        pygame.draw.rect(u, IR[1], (6, 2, 4, 3)); u.set_at((7, 2), IR[4])
        chain(7, 5, 4, 15); chain(8, 5, 11, 13); cuff(4, 17); cuff(11, 15)
    else:
        for px_ in (3, 11):
            pygame.draw.rect(u, IR[1], (px_ - 1, 2, 3, 3)); u.set_at((px_, 2), IR[4])
            chain(px_, 5, px_, 14); cuff(px_, 16)
        line(u, IR[2], (4, 9), (10, 9))                             # spreader bar
    u.set_at((6, 6), RUST[1]); u.set_at((10, 8), RUST[0])
    s.blit(outline(u), (-1, -1))
    for y in range(5, 14): s.set_at((7, y), lerp((20, 16, 24), (40, 30, 30), .5)) if not s.get_at((7, y)).a else None   # rust streak
    return s

def straw(v):
    """16x16 floor decal: a scatter of damp straw, alpha edges; v2 is a thin trail"""
    s = surf(16, 16); r = random.Random(80 + v)
    cx, cy, rx, ry = ((8, 9, 6, 4), (7, 8, 5, 5), (8, 9, 7, 2))[v]
    for _ in range((70, 60, 30)[v]):
        x = cx + r.gauss(0, rx / 1.6); y = cy + r.gauss(0, ry / 1.6); L = r.randrange(2, 5); dx = r.choice((-1, 1))
        for k in range(L):
            X, Y = int(x + k * dx), int(y - k * .4)
            if 0 <= X < 16 and 0 <= Y < 16: s.set_at((X, Y), STRAW[min(3, 1 + r.randrange(3) - (Y > cy + 1))])
    for y in range(16):                                            # under-shadow
        for x in range(16):
            if not s.get_at((x, y)).a and 0 < y and s.get_at((x, y - 1)).a and BAYER[y % 4][x % 4] < 9: s.set_at((x, y), (16, 12, 18, 120))
    return s

def drain():
    s = surf(16, 16)
    for y in range(16):                                            # wet dark stain
        for x in range(16):
            d = ((x - 8) / 7) ** 2 + ((y - 9) / 5.5) ** 2
            if d < 1 and BAYER[y % 4][x % 4] / 16 < (1 - d) * 1.4: s.set_at((x, y), (10, 14, 22, 110))
    pygame.draw.rect(s, (12, 10, 16), (5, 6, 6, 5)); pygame.draw.rect(s, INK, (4, 5, 8, 7), 1)
    for x in (6, 8, 10): line(s, IR[2], (x, 6), (x, 10))
    line(s, IR[4], (5, 5), (10, 5)); s.set_at((7, 11), RUST[1])
    return s

BARS = save("cell_bars.png", sheet([bars(0), bars(1)], 16, FACE)); SHK = save("shackles.png", sheet([shackles(0), shackles(1)], 16, 24))
STR = save("straw.png", sheet([straw(v) for v in range(3)], 16, 16)); DRN = save("drain.png", drain())

D = "dungeon/"; WC = "wall_chains/"
PL = {80: {"wall": [(D + "cell_bars.png", 16, 0, 13, 3), (D + "cell_bars.png", 16, 1, 15, 3),
                    (D + "shackles.png", 16, 0, 4, 0, "hang"), (D + "shackles.png", 16, 1, 13, 0, "hang"), (D + "shackles.png", 16, 0, 19, 0, "hang"),
                    (D + "shackles.png", 16, 1, 3, 9, "hang"), (D + "shackles.png", 16, 0, 20, 9, "hang"),
                    (WC + "wall_chains.png", 16, 0, 23, 11, "east")],
           "floor": [(D + "straw.png", 16, 0, 2, 2), (D + "straw.png", 16, 1, 11, 1), (D + "straw.png", 16, 2, 20, 2, True),
                     (D + "straw.png", 16, 1, 2, 7), (D + "straw.png", 16, 0, 20, 7, True), (D + "straw.png", 16, 0, 4, 12), (D + "straw.png", 16, 2, 19, 11),
                     (WC + "chain_bones.png", 16, 1, 2, 11), (WC + "chain_bones.png", 16, 0, 21, 12), (D + "drain.png", 16, 0, 11, 9)]},
      81: {"wall": [(D + "cell_bars.png", 16, 0, 6, 4), (D + "cell_bars.png", 16, 1, 8, 4),
                    (D + "shackles.png", 16, 1, 16, 4, "hang"), (D + "shackles.png", 16, 0, 19, 4, "hang"),
                    (WC + "wall_chains.png", 16, 1, 21, 6, "east"), (WC + "wall_chains.png", 16, 0, 21, 11, "east")],
           "floor": [(D + "straw.png", 16, 0, 7, 6), (D + "straw.png", 16, 2, 16, 5), (D + "straw.png", 16, 1, 7, 12), (D + "straw.png", 16, 0, 18, 12, True),
                     (WC + "chain_bones.png", 16, 1, 19, 7), (WC + "chain_bones.png", 16, 0, 8, 13), (D + "drain.png", 16, 0, 15, 9)]}}
R = rooms()
for rid, p in PL.items():
    g, w = R[rid]["grid"], R[rid]["walk"]
    for t in p["wall"]:
        x, y, m = t[3], t[4], (t[5:] or ("face",))[0]
        assert g[y][x] == "#" and not art3.is_post(g, x, y), (rid, t)
        if m == "east": assert w[y][x - 1], (rid, t)                      # floor at the wall foot
        else: assert y + 1 < 18 and w[y + 1][x], (rid, t)                 # visible face (floor below)
    for t in p["floor"]: assert w[t[4]][t[3]], (rid, t)
def bfs(w, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and w[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
REACH = {}
for rid in PL:
    w = R[rid]["walk"]; cells = [(x, y) for y in range(18) for x in range(24) if w[y][x]]; REACH[rid] = len(bfs(w, cells[0])) == len(cells)
copy_to_game(HERE, "dungeon")
man = {"set": "dungeon", "issues": [24, 25], "rooms": [80, 81],
 "sheets": {"cell_bars.png": {"frame_size": [16, FACE], "variants": 2, "mount": "face (setpiece.wall_xy, on the wall's 14px front face)", "content": "barred cell window: dark cell behind 3 iron bars + riveted band, stone sill, rust; v1 one bar bent", "blocking": False},
            "shackles.png": {"frame_size": [16, 24], "variants": 2, "mount": "hang (top at the face top, hangs past the wall foot like kitchen herbs)", "content": "v0 wall plate, two chains, open cuffs; v1 two rings + spreader bar manacles; rust streak", "blocking": False},
            "straw.png": {"frame_size": [16, 16], "variants": 3, "layer": "floor decal (alpha)", "content": "damp straw bedding; v2 a thin trail"},
            "drain.png": {"frame_size": [16, 16], "layer": "floor decal", "content": "iron drain grate in a wet stain"},
            "reused": {"wall_chains/wall_chains.png": "#7, east mount", "wall_chains/chain_bones.png": "#7, floor decal"}},
 "rooms_detail": {str(rid): {"name": R[rid]["name"], "wall_decals": [list(t) for t in p["wall"]], "floor_decals": [list(t) for t in p["floor"]],
                             "post_cells": [[x, y] for y in range(18) for x in range(24) if art3.is_post(R[rid]["grid"], x, y)],
                             "blocking_added": [], "bfs_all_walkable_connected": REACH[rid]} for rid, p in PL.items()},
 "room_themes_pending": {"80": {"name": "Dungeon", "setpiece": True}, "81": {"name": "Dungeon Annex", "setpiece": True}},
 "integration_notes": ["read rooms_detail like the towers set: wall_decals -> setpiece.wall_spots, floor_decals -> draw_floor (6th field = horizontal flip)",
                "then add room_themes_pending (setpiece: true) to map/room_themes.json so the random decor does not double up; not added yet because without the lists it would only strip the rooms bare",
                "no blocking changes"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
copy_to_game(HERE, "dungeon")
# previews: before = today's bake (random decor), after = no random decor + these decals
def bake(rid, after):
    room = copy.deepcopy(R[rid])
    if after: [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]; room["theme"] = dict(room.get("theme", {}), setpiece=True)
    raw, top = art3.bake_room(rid, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
    b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if after:
        for t in PL[rid]["floor"]:
            sp = setpiece.frame(t[0], t[1], t[2])
            if len(t) > 5 and t[5]: sp = pygame.transform.flip(sp, True, False)
            b.blit(sp, (t[3] * 16, t[4] * 16 + top))
        for t in sorted(PL[rid]["wall"], key=lambda t: t[4]):
            sp = setpiece.frame(t[0], t[1], t[2]); b.blit(sp, setpiece.wall_xy(t, sp, top))
    return b
font = pygame.font.Font(None, 18)
for rid in PL:
    P = pygame.Surface((2 * 768 + 30, 654)); P.fill((40, 36, 48))
    for j, af in enumerate((False, True)):
        x0 = 10 + j * 778
        P.blit(font.render(f"#{24 if rid == 80 else 25} room {rid} {R[rid]['name']} - {'AFTER' if af else 'before'}", True, (230, 220, 200)), (x0, 6))
        P.blit(pygame.transform.scale(bake(rid, af), (768, 624)), (x0, 24))
    pygame.image.save(P, os.path.join(HERE, f"preview_{rid}.png"))
Z = pygame.Surface((120, 30)); Z.fill((60, 54, 62)); Z.blit(BARS, (2, 2)); Z.blit(SHK, (36, 2)); Z.blit(STR, (2, 14)); Z.blit(DRN, (70, 2))
pygame.image.save(pygame.transform.scale(Z, (720, 180)), os.path.join(HERE, "preview_sheets.png"))
print("ok", REACH)
