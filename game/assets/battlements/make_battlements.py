"""battlements / castle wall rooms (25, 26, 42-49, 51, 60): crenellated wall sheets in the room83 layout (per-room
wall-sheet hook), merlon posts, open-air flagstone walkway, dusk view-below underlays per room, battlement stairs.
python3 make_battlements.py"""
import os, sys, math, random, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from outdoor import *
import art3, setpiece
ROOMS = [25, 26, 42, 43, 44, 45, 46, 47, 48, 49, 51, 60]
files = {}
def save(name, sf): pygame.image.save(sf, os.path.join(HERE, name)); files[name] = sf; return sf
rnd = random.Random(1010)
TOPS = [merlon_top(rnd, BST, v) for v in range(6)]; FRONTS = [parapet_front(rnd, BST, v) for v in range(6)]
SIDES = [side_face(rnd, "left", BST) for _ in range(2)] + [side_face(rnd, "right", BST) for _ in range(2)]
def sheet(tiles, w, h):
    s = surf(w * len(tiles), h); [s.blit(t, (i * w, 0)) for i, t in enumerate(tiles)]; return s
save("batt_wall_tops.png", sheet(TOPS, 16, 16)); save("batt_wall_fronts.png", sheet(FRONTS, 16, FACE)); save("batt_side_walls.png", sheet(SIDES, 8, 16 + FACE))
POST = surf(36, 16 + 8 + FACE); POST.blit(merlon_post(rnd, BST, True), (0, 0)); POST.blit(merlon_post(rnd, BST, False), (18, 0)); save("batt_post.png", POST)
FLOOR = [floor_flag(random.Random(40 + v), v) for v in range(6)]; save("batt_floor.png", sheet(FLOOR, 16, 16))

# ---------- battlement stairs: art/stairs drawers with a weathered outdoor palette (same names/sizes as art/stairs) ----------
src = open(os.path.join(ART, "stairs", "make_stairs.py")).read()
ns = {"__file__": os.path.join(ART, "stairs", "make_stairs.py")}
exec(src[:src.index("def save(")], ns)
ns["PAL"]["battlement"] = dict(ink=(16, 10, 16), top=[(70, 68, 72), (92, 90, 92), (110, 106, 102), (150, 146, 140)],
                              riser=[(34, 32, 40), (52, 50, 58), (68, 66, 72)], mortar=(30, 28, 36), void=(12, 12, 20), accent=(150, 150, 70))
STAIRS = {}
for d, fn in (("up", ns["up"]), ("down", ns["down"])):
    for w, h in ((1, 1), (2, 1), (1, 2), (2, 2)):
        im = fn("battlement", w, h)
        lichen(im, (2, 2, im.get_width() - 4, im.get_height() - 4), random.Random(w * 3 + h), 3)
        STAIRS[(d, w, h)] = save(f"stairs_{d}_battlement_{w}x{h}.png", im)

# ---------- per-room underlays ----------
R = rooms(); TOP = 24
POSTS = {}; ULS = {}
for rid in ROOMS:
    room = R[rid]; g = room["grid"]
    POSTS[rid] = sorted((x, y) for y in range(18) for x in range(24) if art3.is_post(g, x, y))
    ULS[rid] = save(f"underlay_{rid}.png", underlay(rid, room, TOP, depth=1.0 if rid in (25, 26) else 1.15))
copy_to_game(HERE, "battlements")

# ---------- manifest ----------
B = "battlements/"
def stair_list(rid):
    return [{"glyph": ch, "cell": [x, y], "size": [w, h], "file": f"stairs_{'up' if ch == 'U' else 'down'}_battlement_{w}x{h}.png"} for ch, x, y, w, h in art3.stair_blocks(R[rid]["grid"])]
THEME = {str(rid): {"name": R[rid]["name"], "walls": B + "batt_", "floor_tiles": B + "batt_floor.png"} for rid in ROOMS}
NEW_KEYS = {str(rid): {"underlay": B + f"underlay_{rid}.png", "stairs": "battlement", "posts": B + "batt_post.png"} for rid in ROOMS}
man = {"set": "battlements", "rooms": ROOMS,
 "sheets": {
  "batt_wall_tops.png": {"cell": [16, 16], "cols": 6, "layout": "same as room83_wall_tops.png / red_wall_tops.png", "content": "crenellated parapet top: crenel surface + one merlon per tile (cap, south face, cast shadow), so any random tile keeps a 16px merlon beat in horizontal and vertical runs; v2 chipped, v3 lichen, v4 arrow loop, v5 grass tuft"},
  "batt_wall_fronts.png": {"cell": [16, FACE], "cols": 6, "layout": "same as room83_wall_fronts.png", "content": "inner parapet face, rain streaks, lichen at the foot; v5 drain hole"},
  "batt_side_walls.png": {"cell": [8, 16 + FACE], "cols": 4, "layout": "same as room83_side_walls.png: cols 0-1 left (west wall, lit), 2-3 right (east wall, shadowed)"},
  "batt_floor.png": {"cell": [16, 16], "variants": 6, "rule": "variant = thash(x,y) % 6 (existing floor_tiles hook)", "content": "weathered flagstone walkway, two slabs per tile, lichen, hairline cracks; v4 rain puddle reflecting the dusk sky, v5 grass in a crack"},
  "batt_post.png": {"frame_size": [18, 16 + 8 + FACE], "frames": 2, "frame_use": "0 = show_face (post above floor), 1 = no face (wall below; bottom 14px transparent)",
                    "anchor": "top-left at art3.pillar's (X, Y) = (x*16-1, y*16+TOP-RAISE-8): same 18px width, T top block and 8(+FACE) face as pillar()", "content": "squat turret merlon with a 3-merlon crenellated cap, arrow loop on the face, lichen"},
  "stairs_{up,down}_battlement_{1x1,2x1,1x2,2x2}.png": {"layout": "identical to art/stairs (same drawers, sizes and tiling; the 2x2 tiling rule of art3.draw_stairs applies)", "palette": "weathered outdoor stone + lichen"},
  "underlay_<rid>.png": {"size": [384, 18 * 16 + TOP], "blit_at": [0, 0], "covers_floor_from_col": None,
                         "content": "dusk view far below (fields, hedgerows, woods, a river, a road, hamlets; half resolution + depth haze toward the top like balcony_view), the curtain wall's outer face dropping into the haze under every wall cell that faces the void to the south (starts 6px under the cell below the wall, i.e. under the 14px front face), soft shadow along walls bordering the void",
                         "note": "drawn first in bake_room like balcony_view; walls, floors, posts, stairs go over it. With it, no bake pixel stays magenta, so the outline stencil hides nothing in these rooms (the view replaces the void)"}},
 "rooms_detail": {str(rid): {"name": R[rid]["name"], "text": R[rid]["description"], "stairs": stair_list(rid), "post_cells": [list(p) for p in POSTS[rid]],
                            "underlay": B + f"underlay_{rid}.png"} for rid in ROOMS},
 "room_themes_added": THEME, "room_themes_pending_new_keys": NEW_KEYS,
 "integration_notes": [
  "setpiece.underlay(rid): besides room 33, return (img(theme['underlay']), (0, 0), 99) when the room theme has an 'underlay' key (99 = no floor cells skipped); underlay_covers stays False for these rooms",
  "art3.bake_room skips corridor runners when an underlay exists (cor = ... if not (garden or ul)): fine for these rooms (room 25's x18-19 exit passage keeps the plain floor_tiles)",
  "art3.stair_variant: return theme['stairs'] ('battlement') when set, and load stairs_<d>_battlement_<w>x<h>.png from assets/battlements/ (stair_img_at)",
  "art3 pillar pass: when theme['posts'] is set, blit frame 0 (show_face) or 1 of batt_post.png at pillar's (X, Y) instead of pillar(); keep calling pillar() into a scratch surface if the rnd stream must stay unchanged",
  "decor: these rooms should not get indoor sconces/cobwebs; use decor 'garden' (moss/leaves) or setpiece true",
  "lighting: outdoor dusk; if they are dark rooms today, consider a dim ambient instead of full darkness"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
copy_to_game(HERE, "battlements")

# ---------- previews: real bakes, before vs after (hooks simulated in-process) ----------
_pillar = art3.pillar; _sv = art3.stair_variant; _simg = art3.stair_img; _ul = setpiece.underlay; _ulc = setpiece.underlay_covers
def patched(on):
    if not on:
        art3.pillar, art3.stair_variant, art3.stair_img, setpiece.underlay, setpiece.underlay_covers = _pillar, _sv, _simg, _ul, _ulc; return
    def pil(s, X, Y, r_, show_face):
        _pillar(pygame.Surface(s.get_size(), pygame.SRCALPHA), X, Y, r_, show_face)
        s.blit(POST.subsurface((0 if show_face else 18, 0, 18, POST.get_height())), (X, Y))
    art3.pillar = pil; art3.stair_variant = lambda rid, room: "battlement"
    art3.stair_img = lambda n: files.get(n) if "battlement" in n else _simg(n)
    setpiece.underlay = lambda rid: (ULS[rid], (0, 0), 99) if rid in ULS else _ul(rid)
    setpiece.underlay_covers = lambda rid, x, y: False if rid in ULS else _ulc(rid, x, y)
def bake(rid, after):
    room = copy.deepcopy(R[rid]); [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]
    if after: room["theme"] = dict(THEME[str(rid)], decor="garden")
    patched(after)
    try:
        raw, top = art3.bake_room(rid, room)
    finally: patched(False)
    raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0)); return b
font = pygame.font.Font(None, 18)
def board(rids, name, S=1):
    W, H = 384 * S, 312 * S
    P = pygame.Surface((2 * W + 30, len(rids) * (H + 22) + 10)); P.fill((40, 36, 48))
    for i, rid in enumerate(rids):
        for j, af in enumerate((False, True)):
            x0, y0 = 10 + j * (W + 10), 6 + i * (H + 22)
            P.blit(font.render(f"room {rid} {R[rid]['name']} - {'AFTER' if af else 'before'}", True, (230, 220, 200)), (x0, y0))
            P.blit(pygame.transform.scale(bake(rid, af), (W, H)), (x0, y0 + 16))
    pygame.image.save(P, os.path.join(HERE, name))
board([25, 42, 43], "preview.png"); board([46, 48, 60], "preview_2.png"); board([26, 44, 45, 47, 49, 51], "preview_rest.png")
b = bake(42, True); pygame.image.save(pygame.transform.scale(b.subsurface((176, 0, 208, 140)), (624, 420)), os.path.join(HERE, "preview_zoom42.png"))
print("ok")
