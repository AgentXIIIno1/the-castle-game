"""tower tops (rooms 64 West, 65 East): parapet ring (battlement sheets + embrasure caps for the '-' / '|' cells),
silvered plank roof floor, open trapdoor for the 2x2 'D', dusk sky surround (underlay), harp plinth for room 65.
python3 make_tower_top.py   (run battlements/make_battlements.py first: the ring uses its wall sheets and posts)"""
import os, sys, math, random, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from outdoor import *
import art3, setpiece
ROOMS = [64, 65]; TOP = 24
files = {}
def save(name, sf): pygame.image.save(sf, os.path.join(HERE, name)); files[name] = sf; return sf
OAK = [(58, 52, 50), (80, 72, 66), (100, 92, 84), (122, 114, 104), (146, 138, 126)]      # sun-bleached, silvered oak
def plank(v):
    """two 8px boards per tile running E-W: grain streaks, butt joint with nail pairs, lichen"""
    r = random.Random(60 + v); s = surf(16, 16)
    for b_ in range(2):
        tone = .58 + ((b_ * 2 + v) % 3 - 1) * .07; jx = (3 + v * 5 + b_ * 8) % 16
        for y in range(b_ * 8, b_ * 8 + 8):
            for x in range(16):
                gr = .08 * math.sin((x + b_ * 5 + v * 3) * .35 + (y % 8) * 1.7) + (.06 if (x * 5 + y * 3 + v) % 13 == 0 else 0)
                g = tone + gr - (y - b_ * 8) * .015 + (BAYER[y % 4][x % 4] / 16 - .5) * .1
                s.set_at((x, y), OAK[max(0, min(4, int(g * 5)))])
        for x in range(16): s.set_at((x, b_ * 8), lerp(s.get_at((x, b_ * 8))[:3], (176, 168, 152), .35)); s.set_at((x, b_ * 8 + 7), (32, 28, 32))
        for y in range(b_ * 8, b_ * 8 + 7): s.set_at((jx, y), (32, 28, 32))
        for dx in (-2, 2):
            for yy in (b_ * 8 + 2, b_ * 8 + 5): s.set_at(((jx + dx) % 16, yy), (52, 50, 58)); s.set_at(((jx + dx) % 16, yy - 1), (150, 146, 150))
    lichen(s, (0, 0, 16, 16), r, (v == 3) * 3 + (v == 1))
    if v == 4:                                                              # rain puddle in a cupped board
        for x in range(4, 12):
            for y in (10, 11, 12): s.set_at((x, y), (62, 66, 86) if 5 <= x <= 10 and y == 11 else (58, 58, 70))
        s.set_at((6, 10), (122, 112, 142))
    if v == 5:                                                              # rotten, split board end
        for x in range(10, 15): s.set_at((x, 4), (24, 20, 26)); s.set_at((x, 3), (54, 46, 42))
    return s
FL = [plank(v) for v in range(6)]
F = surf(96, 16); [F.blit(t, (i * 16, 0)) for i, t in enumerate(FL)]; save("tower_floor.png", F)

def embrasure(vertical):
    """wide crenel cap for the ring's '-' (horizontal) and '|' (vertical) cells: no merlon, a lit sloping sill"""
    r = random.Random(7 + vertical); s = surf(16, 16)
    stones(s, pygame.Rect(0, 0, 16, 16), r, [lerp(t, (60, 58, 70), .25) for t in BST], dark=.4)
    if not vertical:
        stones(s, pygame.Rect(0, 4, 16, 6), r, BST); line(s, (210, 204, 198), (0, 4), (15, 4)); line(s, (36, 32, 42), (0, 10), (15, 10))
    else:
        stones(s, pygame.Rect(5, 0, 6, 16), r, BST); line(s, (210, 204, 198), (5, 0), (5, 15)); line(s, (36, 32, 42), (11, 0), (11, 15))
    pygame.draw.line(s, (150, 146, 156), (0, 0), (15, 0)); lichen(s, (0, 0, 16, 16), r, 2)
    return s
E = surf(32, 16); E.blit(embrasure(False), (0, 0)); E.blit(embrasure(True), (16, 0)); save("embrasure.png", E)

def trapdoor():
    """open roof hatch over the 2x2 'D' (32x32 at the cells): oak frame, iron corners, ladder into the dark, lid raised"""
    s = surf(32, 32); r = random.Random(5)
    pygame.draw.rect(s, OAK[1], (0, 6, 32, 26)); pygame.draw.rect(s, OAK[3], (0, 6, 32, 26), 2); pygame.draw.rect(s, INK_, (0, 6, 32, 26), 1)
    for y in range(10, 30):                                                 # the opening: ladder fading into darkness
        for x in range(4, 28):
            t = (y - 10) / 20; s.set_at((x, y), lerp((26, 22, 30), (4, 3, 8), t))
    for x in (8, 23):
        for y in range(10, 30): s.set_at((x, y), lerp(OAK[2], (8, 6, 12), (y - 10) / 22))
    for y in range(12, 30, 4): line(s, lerp(OAK[3], (8, 6, 12), (y - 10) / 20), (9, y), (22, y))
    for (x, y) in ((1, 7), (28, 7), (1, 28), (28, 28)): pygame.draw.rect(s, IR3, (x, y, 3, 3))
    lid = surf(32, 10)                                                      # lid raised against its hinges (seen edge-on, slightly open)
    pygame.draw.rect(lid, OAK[2], (2, 0, 28, 9)); [line(lid, OAK[0], (2 + k * 7, 0), (2 + k * 7, 8)) for k in range(1, 4)]
    line(lid, OAK[4], (2, 0), (29, 0)); pygame.draw.rect(lid, INK_, (2, 0, 28, 9), 1)
    for x in (6, 24): pygame.draw.rect(lid, IR3, (x, 6, 3, 3))
    s.blit(lid, (0, 0)); lichen(s, (0, 6, 32, 4), r, 2)
    return s
IR3 = (96, 96, 108)
save("stairs_down_tower_2x2.png", trapdoor())

def plinth():
    """low slate drum under the Harp (room 65, item cell (15,7)): 24x16, a dark cool disc for the gold harp to stand on"""
    s = surf(24, 16); sh = surf(24, 16)
    for y in range(11, 16):
        for x in range(0, 24):
            if ((x - 12.5) / 11.5) ** 2 + ((y - 13) / 2.6) ** 2 < 1: sh.set_at((x, y), (8, 6, 12, 120))
    s.blit(sh, (0, 0)); u = surf(24, 16)
    for y in range(6, 13):                                                  # drum face
        for x in range(2, 22): u.set_at((x, y), lerp((50, 52, 66), (22, 22, 32), (x - 2) / 20 + (BAYER[y % 4][x % 4] / 16 - .5) * .15))
    for y in range(1, 10):                                                  # top disc
        for x in range(1, 23):
            d = ((x - 11.5) / 10.6) ** 2 + ((y - 5) / 4.2) ** 2
            if d < 1: u.set_at((x, y), (76, 80, 98) if d > .72 else (56, 60, 76))
    for x in range(5, 17): u.set_at((x, 1), (156, 162, 180))
    for y in (2, 3, 4): u.set_at((2 if y > 2 else 3, y), (136, 142, 160))
    for x in range(3, 21, 4): u.set_at((x, 10), (88, 92, 110))              # carved band
    s.blit(outline(u), (0, 0)); return s
save("harp_plinth.png", plinth())

R = rooms(); ULS = {}; POSTS = {}
for rid in ROOMS:
    room = R[rid]; g = room["grid"]
    ULS[rid] = save(f"underlay_{rid}.png", underlay(rid, room, TOP, depth=1.35, extra="-|", drop=52))
    g2 = [row.replace("-", "#").replace("|", "#") for row in g]
    POSTS[rid] = sorted((x, y) for y in range(18) for x in range(24) if art3.is_post(g2, x, y))
copy_to_game(HERE, "tower_top")
TT = "tower_top/"
THEME = {str(rid): {"name": R[rid]["name"], "walls": "battlements/batt_", "floor_tiles": TT + "tower_floor.png"} for rid in ROOMS}
NEW_KEYS = {str(rid): {"underlay": TT + f"underlay_{rid}.png", "stairs": "tower", "posts": "battlements/batt_post.png", "ring_glyphs": "-|"} for rid in ROOMS}
emb = {str(rid): [{"cell": [x, y], "frame": 0 if R[rid]["grid"][y][x] == "-" else 1} for y in range(18) for x in range(24) if R[rid]["grid"][y][x] in "-|"] for rid in ROOMS}
man = {"set": "tower_top", "rooms": ROOMS, "uses": "battlements/batt_wall_tops.png, batt_wall_fronts.png, batt_side_walls.png, batt_post.png (same parapet as the battlements)",
 "sheets": {
  "tower_floor.png": {"cell": [16, 16], "variants": 6, "rule": "thash(x,y) % 6 (floor_tiles hook)", "content": "sun-bleached silvered oak roof planks, butt joints and nails, lichen; v4 rain puddle, v5 rotten board end"},
  "embrasure.png": {"frame_size": [16, 16], "frames": 2, "frame_use": "0 = '-' cells (sill runs E-W), 1 = '|' cells (sill runs N-S)", "anchor": "top-left at (x*16, y*16+TOP-8): over the raised wall top of that cell",
                    "content": "wide crenel: no merlon, lit stone sill, lichen", "placements": emb},
  "stairs_down_tower_2x2.png": {"size": [32, 32], "anchor": "top-left of the 2x2 'D' block", "cells": {"64": [4, 8], "65": [18, 8]}, "content": "open roof hatch: oak frame with iron corners, ladder fading into the dark, lid raised on its hinges",
                                "trigger": "unchanged (the D cells stay the way down)"},
  "harp_plinth.png": {"size": [24, 16], "layer": "depth-sorted sprite drawn just before the item (sort y = 8*16 - 0.5), NOT a floor decal: the west wall's 8px side face covers the left half of cell (15,7) in the bake", "room": 65, "cell": [15, 7],
                      "anchor": {"px": [12, 13], "world": [15 * 16 + 8, 8 * 16 - 1], "note": "top-left = (236, 114) room px; the harp (anchored at its cell bottom, raised ~3px, bobbing 1px) stands on the disc"}, "blocking": False, "shadow_baked": True,
                      "why": "the Harp item is gold (#d8a030-ish) and the roof planks are pale silver-brown: the dark slate disc gives it a cool, dark backdrop; the harp keeps its cell and stays pickable"},
  "underlay_<rid>.png": {"size": [384, 18 * 16 + TOP], "blit_at": [0, 0], "content": "the same dusk view below as the battlements, hazier (higher up), with the tower's outer wall dropping away under the south half of the ring (the '-' cells count as wall)"}},
 "post_cells_if_ring_glyphs_count_as_wall": {str(k): [list(p) for p in v] for k, v in POSTS.items()},
 "room_themes_added": THEME, "room_themes_pending_new_keys": NEW_KEYS,
 "integration_notes": [
  "rooms 64/65: draw the '-' and '|' cells as wall ('#') in the wall/post pass (they are already not walkable) so the ring is one continuous crenellated parapet, then blit embrasure.png frame 0/1 over their wall tops at (x*16, y*16+TOP-8); skip the floor under them",
  "setpiece.underlay: theme 'underlay' key as for the battlements",
  "art3.stair_variant: theme 'stairs' = 'tower' -> stairs_down_tower_2x2.png from assets/tower_top/ (the only stair block in these rooms is the 2x2 'D')",
  "posts: theme 'posts' -> battlements/batt_post.png as for the battlements",
  "room 65: draw harp_plinth.png as a sprite at top-left (236, 114) room px, depth-sorted just before the Harp (sort y 127.5); not blocking, no change to the item"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
copy_to_game(HERE, "tower_top")

# ---------- previews ----------
BA = os.path.join(ART, "battlements"); POST = pygame.image.load(os.path.join(BA, "batt_post.png"))
_pillar = art3.pillar; _sv = art3.stair_variant; _simg = art3.stair_img; _ul = setpiece.underlay; _ulc = setpiece.underlay_covers
def patched(on):
    if not on:
        art3.pillar, art3.stair_variant, art3.stair_img, setpiece.underlay, setpiece.underlay_covers = _pillar, _sv, _simg, _ul, _ulc; return
    def pil(s, X, Y, r_, show_face):
        _pillar(pygame.Surface(s.get_size(), pygame.SRCALPHA), X, Y, r_, show_face)
        s.blit(POST.subsurface((0 if show_face else 18, 0, 18, POST.get_height())), (X, Y))
    art3.pillar = pil; art3.stair_variant = lambda rid, room: "tower"
    art3.stair_img = lambda n: files["stairs_down_tower_2x2.png"] if n.startswith("stairs_down_tower_2x2") else _simg(n)
    setpiece.underlay = lambda rid: (ULS[rid], (0, 0), 99) if rid in ULS else _ul(rid)
    setpiece.underlay_covers = lambda rid, x, y: False if rid in ULS else _ulc(rid, x, y)
item_harp = pygame.image.load(os.path.join(ART, "items", "harp.png"))
def bake(rid, after):
    room = copy.deepcopy(R[rid]); [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]
    if after:
        room["theme"] = dict(THEME[str(rid)], decor="garden"); room["grid"] = [row.replace("-", "#").replace("|", "#") for row in room["grid"]]
    patched(after)
    try: raw, top = art3.bake_room(rid, room)
    finally: patched(False)
    raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if after:
        for e in emb[str(rid)]: b.blit(E.subsurface((e["frame"] * 16, 0, 16, 16)), (e["cell"][0] * 16, e["cell"][1] * 16 + top - 8))
        if rid == 65: b.blit(files["harp_plinth.png"], (236, 114 + top))
    for it in R[rid]["items"]:
        if it["name"] == "Harp": b.blit(item_harp, (it["x"] * 16, it["y"] * 16 + top - 3))
    return b
def dark(s, cx, cy, rr=80):
    import numpy as np
    w, h = s.get_size(); X, Y = np.meshgrid(np.arange(w), np.arange(h), indexing="ij")
    lit = np.clip(1 - np.hypot(X - cx, Y - cy) / rr, 0, 1) ** 1.3; arr = pygame.surfarray.array3d(s).astype(float) * (.18 + .82 * lit)[..., None]
    o = pygame.Surface((w, h)); pygame.surfarray.blit_array(o, arr.astype(np.uint8)); return o
font = pygame.font.Font(None, 18); crop = {64: pygame.Rect(0, 40, 192, 200), 65: pygame.Rect(192, 40, 192, 200)}; S = 2
P = pygame.Surface((3 * 192 * S + 40, 2 * (200 * S + 22) + 10)); P.fill((40, 36, 48))
for i, rid in enumerate(ROOMS):
    bb, aa = bake(rid, False), bake(rid, True)
    for j, (nm, t) in enumerate((("before", bb), ("AFTER", aa), ("after, dim (lamp near the harp/hatch)", dark(aa, (16 * 16 if rid == 65 else 5 * 16), 9 * 16 + TOP, 110)))):
        x0, y0 = 10 + j * (192 * S + 10), 6 + i * (200 * S + 22)
        P.blit(font.render(f"room {rid} {nm}", True, (230, 220, 200)), (x0, y0)); P.blit(pygame.transform.scale(t.subsurface(crop[rid]), (192 * S, 200 * S)), (x0, y0 + 16))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
Z = bake(65, True).subsurface((13 * 16, 5 * 16 + TOP - 8, 80, 64)); pygame.image.save(pygame.transform.scale(Z, (384, 336)), os.path.join(HERE, "preview_harp.png"))
print("ok", POSTS)
