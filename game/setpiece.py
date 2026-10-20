"""Hand-placed set pieces: room 19 statue lives in main; here the desks with drawers (rooms 40, 56),
the King's Study furnishings (56) and the Yellow Room dressing (40). Every piece degrades to nothing if its PNG is missing."""
import os, json, pygame
T, COLS, ROWS = 16, 24, 18
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_c = {}

def img(rel):
    if rel not in _c:
        try:
            im = pygame.image.load(os.path.join(A, rel))
            try: im = im.convert_alpha()
            except pygame.error: pass
            _c[rel] = im
        except Exception as e:
            print("[castle diag] set-piece art missing:", rel, e); _c[rel] = None
    return _c[rel]

def frame(rel, fw, i):
    im = img(rel)
    if not im: return None
    n = max(1, im.get_width() // fw); i %= n
    return im.subsurface((i * fw, 0, fw, im.get_height()))

def man(rel):
    k = "man:" + rel
    if k not in _c:
        try: _c[k] = json.load(open(os.path.join(A, rel)))
        except Exception: _c[k] = None
    return _c[k]

# ---------- desks with drawers ----------
DESK = {40: "yellow_room_desk", 56: "kings_study_desk", 10: "chef_desk"}   # chef's desk

def desk_block(room):
    g = room["grid"]; cells = [(x, y) for y in range(ROWS) for x in range(COLS) if g[y][x] == "@"]
    if not cells: return None
    x0, y0 = min(c[0] for c in cells), min(c[1] for c in cells)
    return x0, y0, max(c[0] for c in cells) - x0 + 1, max(c[1] for c in cells) - y0 + 1

def desk_state(room):
    return {"open": "open_item", "empty": "open_empty"}.get(room.get("drawer"), "closed")

def desk_sprite(rid, room):
    """-> (sprite, x, y, sort_y) in room pixels, or None (then main keeps the old placeholder)"""
    if rid not in DESK: return None
    m = man("drawers/manifest.json"); b = desk_block(room)
    if not m or not b: return None
    p = m["pieces"][DESK[rid]]; sp = img("drawers/" + p["states"][desk_state(room)])
    if not sp: return None
    fx, fy, w, h = b; ax, ay = p["anchor"]["px"]
    X, Y = fx * T + w * T // 2, (fy + h) * T
    return sp, X - ax, Y - ay, Y

def has_desk_art(rid, room): return desk_sprite(rid, room) is not None

# ---------- fixed props ----------
# objects: (file, frame_w, variant_or_None, cell_x, cell_y, width_cells, anim_fps, light)
STUDY_OBJ = [("kings_study/bookshelf.png", 32, 0, 5, 4, 2, 0, None), ("kings_study/bookshelf.png", 32, 1, 16, 4, 2, 0, None),
             ("kings_study/candelabra.png", 16, None, 15, 6, 1, 6, (8, 5))]
STUDY_FLOOR = [("kings_study/rug_royal.png", 64, 0, 10, 9)]
# placements (art/_common/fix39.py, kings_study / *_room manifests): all wall decals sit off wall-post cells
# wall decals: (file, frame_w, variant, wall_x, wall_y[, mount]); mount "face" (default: sits on the wall face, bottom-aligned),
# "hang" (top-aligned at the face top, may hang down over the wall foot: banners, pot rack, herbs), "east" (east wall's
# inner side face, see wall_xy)
STUDY_WALL = [("kings_study/banner_royal.png", 16, 0, 8, 3, "hang"), ("kings_study/banner_royal.png", 16, 1, 15, 3, "hang")]
YW = "yellow_room/"
YELLOW_WALL = [(YW + "wallpaper_peeling.png", 16, v, x, 3) for x, v in ((5, 0), (8, 1), (18, 2), (16, 0))] + \
              [(YW + "wallpaper_peeling.png", 16, v, x, 14) for x, v in ((6, 1), (15, 2))] + \
              [(YW + "mirror_tarnished.png", 16, 0, 14, 3), (YW + "frame_gilt.png", 16, 0, 10, 3)]
YELLOW_FLOOR = [(YW + "cobweb.png", 16, 0, 4, 4), (YW + "cobweb.png", 16, 0, 19, 4, True),
                (YW + "dust_indoor.png", 16, 0, 11, 8), (YW + "dust_indoor.png", 16, 1, 17, 13)]

COLOUR = {37: "red_room/", 38: "blue_room/", 39: "purple_room/"}
def colour_wall(rid):
    p = COLOUR[rid]
    return [(p + "wallpaper_peeling.png", 16, v, x, 3) for x, v in ((5, 0), (8, 1), (18, 2), (16, 0))] + \
           [(p + "mirror_tarnished.png", 16, 0, 14, 3), (p + "frame_gilt.png", 16, 0, 9 if rid in (37, 38) else 10, 3)]
def colour_floor(rid):
    p = COLOUR[rid]
    return [(p + "cobweb.png", 16, 0, 4, 4), (p + "cobweb.png", 16, 0, 19, 4, True),
            (p + "dust_indoor.png", 16, 0, 11, 9), (p + "dust_indoor.png", 16, 1, 17, 13)]

# ---------- room 79 torture room: assets/wall_chains/manifest.json ----------
TORTURE = 79
CHAIN_WALL = [("wall_chains/wall_chains.png", 16, 0, 21, 8, "east"), ("wall_chains/wall_chains.png", 16, 1, 21, 10, "east")]
def _towers(group="towers"):
    """(#20-#23) tower rooms 50, 61, 62, 63: arrow slits (wall) and their daylight patches (floor), exact tuples from
    assets/<group>/manifest.json rooms_detail; the dungeon set 80, 81 uses the same format"""
    try: d = json.load(open(os.path.join(A, group, "manifest.json")))["rooms_detail"]
    except (OSError, ValueError, KeyError): return {}, {}
    return ({int(r): [tuple(p) for p in v.get("wall_decals", [])] for r, v in d.items()},
            {int(r): [tuple(p) for p in v.get("floor_decals", [])] for r, v in d.items()})
TOWER_WALL, TOWER_FLOOR = _towers()
DUNGEON_WALL, DUNGEON_FLOOR = _towers("dungeon")
SET_BLOCK = {}    # rid -> manifest blocking_added cells (a tall piece may cover the cell above its foot: room 13's broken bench)
SET_GROUPS = ("honours", "museum", "ante_room", "patio")   # (#14-#19) sets in the same rooms_detail format
def _sets():
    """wall decals, floor decals, objects and warm light points of the later sets: {rid: [...]} each"""
    wall, floor, obj, light = {}, {}, {}, {}
    SET_BLOCK.clear()
    for grp in SET_GROUPS:
        try: d = json.load(open(os.path.join(A, grp, "manifest.json")))["rooms_detail"]
        except (OSError, ValueError, KeyError): continue
        for r, v in d.items():
            r = int(r)
            if v.get("wall_decals"): wall[r] = [tuple(p) for p in v["wall_decals"]]
            if v.get("floor_decals"): floor[r] = [tuple(p) for p in v["floor_decals"]]
            if v.get("objects"): obj[r] = [tuple(o) for o in v["objects"]]
            if v.get("blocking_added"): SET_BLOCK[r] = {tuple(c) for c in v["blocking_added"]}
            li = v.get("light_suggestion")
            if li: light[r] = [(c, (li["radius"], tuple(li["colour"]))) for c in li["cells"]]
    return wall, floor, obj, light
SET_WALL, SET_FLOOR, HONOUR_OBJ, SET_LIGHT = _sets()   # HONOUR_OBJ: stands/rack (22, 24), plinths/case (12), broken bench (13)
TOWER_LIGHT = (22, (34, 46, 66))      # dim cool daylight at each patch: (radius, colour) for main's light cache
CHAIN_FLOOR = [("wall_chains/chain_bones.png", 16, 0, 19, 9), ("wall_chains/chain_bones.png", 16, 1, 19, 11)]

# ---------- room 9 kitchen: assets/kitchen/manifest.json ----------
KITCHEN = 9
KITCHEN_OBJ = [("kitchen/hearth.png", 48, None, 14, 3, 3, 6, (24, 36)), ("kitchen/kitchen_barrel.png", 16, 0, 4, 3, 1, 0, None),
               ("kitchen/sack.png", 16, 0, 5, 3, 1, 0, None), ("kitchen/sack.png", 16, 1, 4, 4, 1, 0, None),
               ("kitchen/chopping_block.png", 16, 0, 19, 9, 1, 0, None)]
KITCHEN_WALL = [("kitchen/pot_rack.png", 32, 0, 8, 2, "hang"), ("kitchen/herbs_hanging.png", 16, 1, 6, 2, "hang"),
                ("kitchen/herbs_hanging.png", 16, 0, 18, 2, "hang"), ("kitchen/herbs_hanging.png", 16, 1, 19, 2, "hang")]
KITCHEN_FLOOR = [("kitchen/crockery_broken.png", 16, 0, 6, 11), ("kitchen/crockery_broken.png", 16, 1, 12, 11),
                 ("kitchen/cobweb.png", 16, 0, 20, 3, True), ("kitchen/cobweb.png", 16, 0, 4, 14)]

OBJ_ROOMS = {56: STUDY_OBJ, KITCHEN: KITCHEN_OBJ, **HONOUR_OBJ}
def objects(rid): return OBJ_ROOMS.get(rid, [])

def obj_light(f, k):
    """light kind for a set-piece object: the manifest's light (radius, colour, flicker synced to frame k), else 'candle'"""
    if f != "kitchen/hearth.png": return "candle"
    li = ((man("kitchen/manifest.json") or {}).get("sheets", {}).get("hearth.png") or {}).get("light")
    if not li: return "candle"
    fl = (0.8, 0.93, 1.0, 0.87)[k % 4]                          # 0.8-1.0, one step per flame frame (4 cached lights)
    return (li.get("radius_hint", 64), tuple(int(c * fl) for c in li.get("color", (255, 150, 70))))

# ---------- room 66 sorcerer's laboratory (issue #13): placements from assets/sorcerer_lab/manifest.json ----------
LAB = 66
def lab_man():
    return man("sorcerer_lab/manifest.json") if os.path.exists(os.path.join(A, "sorcerer_lab/manifest.json")) else None

def lab_sprites():
    m = lab_man()
    return [p for p in (m or {}).get("placements_room66", []) if p.get("layer") == "sprite"] if m else []

def blockers(rid):
    """[(index, cells)] of set pieces that block movement (BFS-checked in apply_blocking)"""
    if rid in OBJ_ROOMS:
        out = [(i, [(o[3] + k, o[4]) for k in range(o[5])]) for i, o in enumerate(OBJ_ROOMS[rid])]
        for i, cells in out:      # blocking_added cells straight above a piece's foot row belong to that piece
            o = OBJ_ROOMS[rid][i]
            cells[:0] = sorted((x, y) for x, y in SET_BLOCK.get(rid, ()) if o[3] <= x < o[3] + o[5] and o[4] - 2 <= y < o[4])
        return out
    if rid == LAB:
        return [(i, [(p["cell"][0] + kx, p["cell"][1] + ky) for kx in range(p["footprint"][0]) for ky in range(p["footprint"][1])])
                for i, p in enumerate(lab_sprites()) if p.get("blocking")]
    return []

def _lab_frame(p, t):
    sh = (lab_man() or {}).get("sheets", {}).get(p["file"], {}); fw = sh.get("frame_size", [16])[0]
    k = int(t * sh.get("fps", 6)) if p.get("frame") == "anim" else (p.get("frame") or 0)
    return frame("sorcerer_lab/" + p["file"], fw, k), sh

def draw_lab(room, t, dr, lights):
    """lab sprites (setpiece: drawn after the outline mask), cauldron and candle animation, their light points"""
    kept = {i for i, _ in room.get("set_objs", [])}
    sheets = (lab_man() or {}).get("sheets", {})
    for i, p in enumerate(lab_sprites()):
        if p.get("blocking") and i not in kept: continue           # skipped by the BFS check
        sp, sh = _lab_frame(p, t)
        if not sp: continue
        (wx, wy), (ax, ay) = p["world_anchor"], sh["anchor"]["px"]
        x, y = wx - ax, wy - ay
        dr.append((p.get("depth_sort_y", wy), sp, x, y, 0, True))
        if p["file"] == "cauldron.png":
            for key in ("light_point", "ember_light"):
                lp = sh.get(key)
                if lp: lights.append((x + lp["px"][0], y + lp["px"][1], (lp.get("radius_hint", 32), tuple(lp["color"]))))
        if p["file"] == "candles.png":                              # flame overlay at the same position, one light per flame tip
            fl = "candle_flame_cluster.png" if (p.get("frame") or 0) == 0 else "candle_flame_single.png"
            fs = sheets.get(fl, {}); f_ = frame("sorcerer_lab/" + fl, fs.get("frame_size", [16])[0], int((t + i * .37) * fs.get("fps", 8)))
            if f_:
                dr.append((p.get("depth_sort_y", wy) + 0.01, f_, x, y, 0, True))
                li = fs.get("light", {}); pts = fs.get("light_points_px", [])
                k_ = 1 / max(1, len(pts)) ** 0.8          # the cluster's 3 overlapping lights would add up to a white blob
                col = tuple(int(c * k_) for c in li.get("color", (255, 190, 110)))
                for px, py in pts: lights.append((x + px, y + py, (li.get("radius_hint", 24), col)))

def draw_lab_floor(s, top):
    m = lab_man()
    if not m: return
    for p in m.get("placements_room66", []):
        if p.get("layer") not in ("floor decal", "wall-top-corner"): continue
        sh = m["sheets"].get(p["file"], {}); fw = (sh.get("frame_size") or [16])[0]
        sp = frame("sorcerer_lab/" + p["file"], fw, 0 if p.get("frame") == "flip" else (p.get("frame") or 0))
        if not sp: continue
        if p.get("frame") == "flip": sp = pygame.transform.flip(sp, True, False)
        x, y = p["world_topleft"]; s.blit(sp, (x, y + top))

def draw_lab_glow(L, top, t):
    """optional rune circle pulse, above the floor and below the sprites"""
    m = lab_man(); p = next((q for q in (m or {}).get("placements_room66", []) if q["file"] == "rune_circle.png"), None)
    if not p or not os.path.exists(os.path.join(A, "sorcerer_lab/rune_circle_glow.png")): return
    sh = m["sheets"].get("rune_circle_glow.png", {}); k = int(t * sh.get("fps", 2)) % max(1, sh.get("frames", 4))
    f_ = frame("sorcerer_lab/rune_circle_glow.png", 64, k)     # faint (alpha <= 100) violet pulse: a plain alpha blit reads as a glow
    if f_: L.blit(f_, (p["world_topleft"][0], p["world_topleft"][1] + top))

def _bfs(walk, start):
    seen = {start}; st = [start]
    while st:
        x, y = st.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in seen and walk[n[1]][n[0]]: seen.add(n); st.append(n)
    return seen

def block_ok(room, cells):
    """True (and the cells blocked) if blocking them keeps every exit edge, item and monster that is reachable now
    reachable from the room edge (same rule as apply_blocking); else the walk grid is left unchanged"""
    walk = room["walk"]
    edge = [(x, y) for y in range(ROWS) for x in range(COLS) if walk[y][x] and (x in (0, COLS - 1) or y in (0, ROWS - 1))]
    if not edge: return False
    base = _bfs(walk, edge[0])
    goals = [c for c in edge + [(i["x"], i["y"]) for i in room.get("items", []) + room.get("hidden", [])]
             + [(m["x"], m["y"]) for m in room.get("mons", [])] if c in base and c not in cells]
    for x, y in cells: walk[y][x] = False
    reach = _bfs(walk, edge[0])
    if all(g in reach for g in goals): return True
    for x, y in cells: walk[y][x] = True
    return False

def apply_blocking(rid, room):
    """block set-piece cells, skipping any piece that would cut an exit, item or monster off (BFS)"""
    walk = room["walk"]; keep = room.setdefault("set_objs", [])
    if room.get("_set_done"):
        for _, cells in keep:
            for x, y in cells: walk[y][x] = False
        return
    room["_set_done"] = True
    edge = [(x, y) for y in range(ROWS) for x in range(COLS) if walk[y][x] and (x in (0, COLS - 1) or y in (0, ROWS - 1))]
    goals = edge + [(i["x"], i["y"]) for i in room.get("items", []) + room.get("hidden", []) if walk[i["y"]][i["x"]]]
    base = _bfs(walk, edge[0]) if edge else set()
    goals = [gl for gl in goals if gl in base]     # only what's reachable now must stay reachable (room 9: a walled-in pocket below the south wall)
    for i, cells in blockers(rid):
        o = objects(rid)[i] if rid in OBJ_ROOMS else (lab_sprites()[i]["file"],)
        if not all(walk[y][x] for x, y in cells): continue
        for x, y in cells: walk[y][x] = False
        reach = _bfs(walk, edge[0]) if edge else set()
        if not all(gl in reach for gl in goals if gl not in cells):
            for x, y in cells: walk[y][x] = True
            print("[castle diag] set piece skipped (would block):", rid, o[0], cells); continue
        keep.append([i, cells])

def placed_objects(rid, room):
    return [objects(rid)[i] for i, _ in room.get("set_objs", []) if isinstance(i, int)] if rid in OBJ_ROOMS else []   # room 66 draws via draw_lab

HARP_ROOM = 65
MAIL_ROOM = 24
_MAIL = {}
def mail_stand(full=False):
    """ armour stand for the Chain Mail (assets/chain_mail/manifest.json): "stand" = the empty stand, "stand_full" =
    the stand wearing the mail, drawn instead while the Chain Mail lies on "item_cell" (its floor sprite is then skipped).
    {"file", "topleft": [px, py] room px, "sort_y"}; not blocking. None without the art."""
    key = "stand_full" if full else "stand"
    if key not in _MAIL:
        _MAIL[key] = None
        try: st = json.load(open(os.path.join(A, "chain_mail", "manifest.json"))).get(key)
        except (OSError, ValueError): st = None
        if st and os.path.exists(os.path.join(A, "chain_mail", st["file"])):
            sp = img("chain_mail/" + st["file"])
            if sp: _MAIL[key] = (st["sort_y"], sp, st["topleft"][0], st["topleft"][1], 0)
    return _MAIL[key]
def mail_item_cell():
    if "cell" not in _MAIL:
        try: _MAIL["cell"] = tuple(json.load(open(os.path.join(A, "chain_mail", "manifest.json")))["item_cell"])
        except (OSError, ValueError, KeyError): _MAIL["cell"] = None
    return _MAIL["cell"]
def mail_on_stand(rid, room):
    """the Chain Mail item lies on its stand cell and the full-stand art exists"""
    c = mail_item_cell()
    return (rid == MAIL_ROOM and c is not None and mail_stand(True) is not None
            and any(i.get("chainmail") and (i["x"], i["y"]) == c for i in room["items"]))
def draw_objects(rid, room, t, dr, lights):
    for p in TOWER_FLOOR.get(rid, []):       # (#20-#23) daylight from the slits
        lights.append((p[3] * T + T // 2, p[4] * T + T // 2, TOWER_LIGHT))
    for (x, y), li in SET_LIGHT.get(rid, []):   # warm daylight from the patio
        lights.append((x * T + T // 2, y * T + T // 2, li))
    if rid == MAIL_ROOM and "CHAINMAIL" in room.get("_flags", ()):
        st = mail_stand(mail_on_stand(rid, room))
        if st: dr.append(st)
    if rid == HARP_ROOM and os.path.exists(os.path.join(A, "tower_top/harp_plinth.png")):   # slate disc under the Harp
        sp = img("tower_top/harp_plinth.png")                                                 # not blocking; sorts just before it
        if sp: dr.append((8 * T - 0.5, sp, 236, 114, 0))
    for f, fw, var, x, y, w, fps, light in placed_objects(rid, room):
        k = int(t * fps) if fps else (var or 0)
        sp = frame(f, fw, k)
        if not sp: continue
        X, Y = x * T + w * T // 2, y * T + T
        sx, sy = X - sp.get_width() // 2, Y - sp.get_height()
        dr.append((Y, sp, sx, sy, 0, True))   # shadow_baked; may cross the outline like the room 66 sprites (tops rise above the north wall)
        if light: lights.append((sx + light[0], sy + light[1], obj_light(f, k)))

def _face(x, y, top, raise_=8): return x * T, y * T + top - raise_ + T

def draw_floor(s, rid, room, top):
    if rid == LAB: draw_lab_floor(s, top)
    if rid == 14:   # optional throne carpet runner (throne batch): top-left cell (11,5)
        sp = img("throne/throne_carpet.png") if os.path.exists(os.path.join(A, "throne/throne_carpet.png")) else None
        if sp: s.blit(sp, (11 * T, 5 * T + top))
    for p in (STUDY_FLOOR if rid == 56 else YELLOW_FLOOR if rid == 40 else colour_floor(rid) if rid in COLOUR else
              CHAIN_FLOOR if rid == TORTURE else KITCHEN_FLOOR if rid == KITCHEN else TOWER_FLOOR.get(rid, DUNGEON_FLOOR.get(rid, SET_FLOOR.get(rid, [])))):
        f, fw, var, x, y = p[:5]; sp = frame(f, fw, var)
        if not sp: continue
        if len(p) > 5 and p[5]: sp = pygame.transform.flip(sp, True, False)
        s.blit(sp, (x * T, y * T + top))

def wall_spots(rid, room):
    """hand-placed wall decals actually drawn: [(file, frame_w, variant, x, y[, mount])], only on real wall cells (door gaps stay clear)"""
    g = room["grid"]
    return [p for p in (STUDY_WALL if rid == 56 else YELLOW_WALL if rid == 40 else colour_wall(rid) if rid in COLOUR else
                        CHAIN_WALL if rid == TORTURE else KITCHEN_WALL if rid == KITCHEN else TOWER_WALL.get(rid, DUNGEON_WALL.get(rid, SET_WALL.get(rid, [])))) if g[p[4]][p[3]] == "#"]

def wall_cells(p):
    """wall cells a hand-placed wall decal is mounted on (a 32px pot rack spans two)"""
    return [(p[3] + k, p[4]) for k in range(1 if (p[5:] or ("face",))[0] in ("east", "west") else max(1, p[1] // T))]

def wall_xy(p, sp, top):
    """top-left px of a hand-placed wall decal. face: bottom-aligned on the wall face; hang: top-aligned at the face top
    (hangs down past the wall foot); east: on the east wall's inner side face, frame left of the wall cell at ((x-1)*16, y*16+top-8)"""
    f, fw, var, x, y = p[:5]; mount = (p[5:] or ("face",))[0]
    if mount == "east": return (x - 1) * T, y * T + top - 8
    if mount == "west": return (x + 1) * T, y * T + top - 8      # (#20-#23) the west wall's lit inner side face
    X, Y = _face(x, y, top)
    return X, (Y if mount == "hang" else Y - max(0, sp.get_height() - 14))

def draw_wall(s, rid, room, top, row=None):
    for p in wall_spots(rid, room):
        if row is not None and p[4] != row: continue
        sp = frame(p[0], p[1], p[2]) if os.path.exists(os.path.join(A, p[0])) else None
        if sp: s.blit(sp, wall_xy(p, sp, top))

def draw_furniture_overlay(s, rid, room, top):
    draw_bed_covers(s, rid, room, top)
    if rid == 40 and (5, 5) not in bed_cells(rid, room):
        sp = img(YW + "bed_cover_yellow.png")
        if sp: s.blit(sp, (5 * T, 5 * T + top))

def floor_tile(rid, x, y, thash, room=None):
    """per-room floor tile override: Yellow Room / study parquet / room_themes 'floor_tiles'. None = keep the baked floor"""
    ft = (room or {}).get("theme", {}).get("floor_tiles")
    if ft and os.path.exists(os.path.join(A, ft)): return frame(ft, 16, thash(x, y) % 6)
    if rid == 40: return frame(YW + "yellow_floor.png", 16, thash(x, y) % 6)
    if rid == 56: return frame("kings_study/study_floor_parquet.png", 16, (x + y) % 4)
    return None

def wall_sheets(rid):
    """(tops, fronts, sides) prefixes in assets/ for per-room wall tiles; None = default"""
    if rid == 40: return YW + "yellow_wall_tops.png", YW + "yellow_wall_fronts.png", YW + "yellow_side_walls.png"
    return None

def wall_sheets_for(rid, room):
    w = room.get("theme", {}).get("walls")   # room_themes.json: "walls": "red_room/red_" -> red_wall_tops.png etc.
    if w and all(os.path.exists(os.path.join(A, w + n)) for n in ("wall_tops.png", "wall_fronts.png", "side_walls.png")):
        return w + "wall_tops.png", w + "wall_fronts.png", w + "side_walls.png"
    return wall_sheets(rid)

# ---------- room 33 balcony (issue #12): baked garden view + railing ----------
BALCONY = 33
def underlay(rid, room=None):
    """-> (surface, (px, py) on the bake surface, first covered cell column) or None.
    room_themes "underlay": a full 384x312 view under the whole bake (battlements, tower tops); 99 = no floor skipped"""
    ul = (room or {}).get("theme", {}).get("underlay")
    if ul and os.path.exists(os.path.join(A, ul)):
        sp = img(ul)
        if sp: return sp, (0, 0), 99
    if rid != BALCONY or not os.path.exists(os.path.join(A, "balcony/balcony_view.png")): return None
    sp = img("balcony/balcony_view.png")
    return (sp, (160, 0), 10) if sp else None

def underlay_covers(rid, x, y):
    u = underlay(rid) if rid == BALCONY else None
    return bool(u) and x >= u[2]

RAIL_FRAME = {"|": 0, "%": 1, ".": 2, "'": 3, "-": 4}   # '>' is remapped to '%' at load
def rail_cells(rid, room):
    """{(x, y): frame} for the balcony railing (column x9 plus the '-' end caps at (8,1) and (8,16))"""
    if rid != BALCONY or not os.path.exists(os.path.join(A, "balcony/balcony_rail.png")): return {}
    k = "_rail"
    if k not in room:
        g = room["grid"]; out = {}
        for y in range(ROWS):
            if g[y][9] in RAIL_FRAME: out[(9, y)] = RAIL_FRAME[g[y][9]]
        for y in (1, 16):
            if g[y][8] == "-": out[(8, y)] = 4
        room[k] = out
    return room[k]

def draw_rail(rid, room, dr):
    for (x, y), f in rail_cells(rid, room).items():
        sp = frame("balcony/balcony_rail.png", 16, f)
        if sp: dr.append(((y + 1) * T, sp, x * T, y * T - 8, 0, True))   # rises 8 px like the wall tops; may cross the outline

HAZE = (200, 206, 218, 255)   # room 33: fountain and bushes sit in the view's depth haze

# ---------- object hooks (issues #2 throne, #3 mirror, #4 barrels) ----------
# rid -> (glyph chars, asset path under assets/, kind). Each 4-connected block of those glyphs becomes one object,
# anchored bottom-centre of the block and depth-sorted at its bottom edge; placeholder art until delivers.
HOOKS = {9: ("%", "kitchen/stone_table.png", "table"),        # large stone table
         14: ("%-", "throne/throne.png", "throne"),
         67: (",|`", "wall_mirror/wall_mirror.png", "mirror"),
         68: ("@", "wine_barrels/wine_barrels.png", "barrels")}
# anchors (bottom-centre px) and variant sheets; placeholders use (w/2, h-1)
HOOK_ANCHOR = {9: (72, 45), 14: (36, 79), 67: (8, 107), 68: (32, 50)}

def blocks(g, chars):
    seen, out = set(), []
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] in chars and (x, y) not in seen:
                st, cells = [(x, y)], []; seen.add((x, y))
                while st:
                    cx, cy = st.pop(); cells.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (cx + dx, cy + dy)
                        if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in seen and g[n[1]][n[0]] in chars: seen.add(n); st.append(n)
                x0, y0 = min(c[0] for c in cells), min(c[1] for c in cells)
                out.append((x0, y0, max(c[0] for c in cells) - x0 + 1, max(c[1] for c in cells) - y0 + 1, set(cells)))
    return out

def hook_blocks(rid, room):
    if rid not in HOOKS: return []
    k = "_hook_blocks"
    if k not in room: room[k] = blocks(room["grid"], HOOKS[rid][0])
    return room[k]

def hooked_cell(rid, room, x, y):
    """art3 skips its procedural furniture for these cells; the hook draws them"""
    return any((x, y) in b[4] for b in hook_blocks(rid, room))

def _placeholder(kind, w, h):
    W, H = w * T, h * T
    if kind == "throne":
        s = pygame.Surface((W, H + 20), pygame.SRCALPHA)
        pygame.draw.rect(s, (110, 20, 30), (6, 2, W - 12, H + 6)); pygame.draw.rect(s, (200, 160, 60), (6, 2, W - 12, H + 6), 2)
        pygame.draw.rect(s, (140, 30, 40), (2, H - 4, W - 4, 20)); pygame.draw.rect(s, (220, 180, 70), (2, H - 4, W - 4, 20), 2)
        for k in range(3): pygame.draw.polygon(s, (230, 190, 70), [(W//2 - 8 + k*8, 2), (W//2 - 4 + k*8, -2 + 6), (W//2 + k*8, 2)])
        return s
    if kind == "mirror":
        s = pygame.Surface((W + 4, H + 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (150, 120, 60), (0, 0, W + 4, H + 6), border_radius=3)
        pygame.draw.rect(s, (120, 140, 160), (3, 3, W - 2, H), border_radius=2)
        pygame.draw.line(s, (200, 215, 230), (5, 6), (W - 2, H // 2), 1)
        return s
    s = pygame.Surface((W, H + 6), pygame.SRCALPHA)   # barrels: rows of round lids
    for by in range(h):
        for bx in range(w):
            cx, cy = bx * T + 8, by * T + 8
            pygame.draw.ellipse(s, (88, 54, 30), (cx - 7, cy - 6, 14, 16)); pygame.draw.ellipse(s, (130, 86, 48), (cx - 6, cy - 6, 12, 10))
            pygame.draw.ellipse(s, (50, 30, 18), (cx - 6, cy - 6, 12, 10), 1); pygame.draw.line(s, (60, 60, 66), (cx - 7, cy + 4), (cx + 6, cy + 4))
    return s

def hook_sprite(rid, b):
    """-> (sprite, anchor, is_art)"""
    x0, y0, w, h, _ = b; chars, path, kind = HOOKS[rid]
    key = ("hook", rid, x0, y0)
    if key not in _c:
        sp = img(path) if os.path.exists(os.path.join(A, path)) else None
        if sp and kind == "barrels":   # 64x52 variant sheet; per-block variant from the manifest placement map
            m = man("wine_barrels/manifest.json") or {}
            v = (m.get("placement") or {}).get(f"{x0},{y0}", (x0 + y0) % 3)
            fw = (m.get("sheet") or {}).get("frame_size", [64])[0]
            sp = sp.subsurface(((v % max(1, sp.get_width() // fw)) * fw, 0, fw, sp.get_height()))
        _c[key] = (sp, HOOK_ANCHOR[rid], True) if sp else None
        if not sp:
            ph = _placeholder(kind, w, h); _c[key] = (ph, (ph.get_width() // 2, ph.get_height() - 1), False)
    return _c[key]

TALL = {14}   # camera framing only: keep the tall throne in view (TJ: the throne may overlap the wall). Outline crossing is general

def draw_hooks(rid, room, dr, t=0.0):
    for b in hook_blocks(rid, room):
        x0, y0, w, h, _ = b; sp, (ax, ay), art = hook_sprite(rid, b)
        X, Y = x0 * T + w * T // 2, (y0 + h) * T
        dr.append((Y, sp, X - ax, Y - 1 - ay + (0 if art or HOOKS[rid][2] != "barrels" else 3), 0, True))   # True: may cross the outline
        if rid == 14 and art and os.path.exists(os.path.join(A, "throne/throne_glint.png")):   # optional glint overlay, 4x72x80 @ ~3 fps
            gl = frame("throne/throne_glint.png", 72, int(t * 3))
            if gl: dr.append((Y + 0.01, gl, X - ax, Y - 1 - ay, 0, True))

# ---------- coloured rooms (issue #5): bed covers from room_themes.json ----------
def furniture_overlay_row(rid, room):
    """ depth row for draw_furniture_overlay: the front (lowest) row of the room's beds"""
    th = room.get("theme", {}); bc = th.get("bed_cover")
    sp = img(bc) if bc and os.path.exists(os.path.join(A, bc)) else (img(YW + "bed_cover_yellow.png") if rid == 40 else None)
    rows = []
    for _, y0, _, h, _ in blocks(room["grid"], "W"):   # a cover may hang over the footboard row: use its own height
        rows.append(y0 + max(h, -(-sp.get_height() // T) if sp else h) - 1)
    return max(rows, default=ROWS - 1)

def draw_bed_covers(s, rid, room, top):
    """procedural beds only: a bed with carries its cover in its sprite"""
    art = bed_cells(rid, room)
    for x0, y0, w, h, _ in blocks(room["grid"], "W"):
        if (x0, y0) in art or (rid == 40 and not room.get("theme", {}).get("bed_cover")): continue
        cov = cover_surface(rid, room, w, h)
        if cov: s.blit(cov[0], (x0 * T + cov[1][0], y0 * T + top + cov[1][1]))

def cover_surface(rid, room, w, h):
    """the room's bed cover for a w x h body block: cover, else the room-colour placeholder; None = no cover"""
    th = room.get("theme", {}); bc = th.get("bed_cover")
    if rid == 40 and not bc: bc = YW + "bed_cover_yellow.png"
    if not bc: return None
    if os.path.exists(os.path.join(A, bc)): return img(bc), (0, 0)
    col = tuple(th.get("bed_color", (160, 40, 50)))
    ov = pygame.Surface((w * T, h * T - 5), pygame.SRCALPHA); ov.fill(col + (235,))
    for k in range(2, h * T - 5, 4): pygame.draw.line(ov, tuple(max(0, c - 40) for c in col) + (235,), (0, k), (w * T, k))
    return ov, (0, 5)

# ---------- beds (assets/beds/manifest.json) ----------
# horizontal: ']' head + 'W'x4 + '[' foot, 2 rows (6x2) -> bed_single_h (variant per room) or, under a themed cover, bed_frame_h
#             (cover at frame px 16,16). vertical: '_' head + 'W'x4 rows + '^' foot, 2 wide (2x6; '_'/'^' are '%' after the
#             FURN remap) -> bed_frame_v under the 37/38 covers (frame px 0,32), else bed_single_v.
# Anchor = bottom-centre pixel of the footprint (like the object hooks: anchor pixel at world (X, Y - 1)), sprite rises 16 px
# above it. Beds are depth-sorted sprites (sort y = footprint bottom); the bake keeps the floor and skips the bed cells;
# blocking stays on the grid cells.
BEDS = "beds/"
BED_VARIANT = {10: 2, 67: 1}       # bed_single_h: 0 madder red, 1 dusty violet, 2 dusty ochre (theme "bed_variant" overrides)
BED_H, BED_V = (96, 48, (48, 47)), (32, 112, (16, 111))

def bed_footprints(room):
    """[(x0, y0, w, h, body (bx, by, bw, bh), vertical)] for every bed: W body plus its post / head / foot cells"""
    g = room["grid"]; out = []
    for bx, by, bw, bh, _ in blocks(g, "W"):
        if bh > bw:   # vertical: '%' (from '_' / '^') full rows above and below the body
            top = by > 0 and all(g[by - 1][x] == "%" for x in range(bx, bx + bw))
            bot = by + bh < ROWS and all(g[by + bh][x] == "%" for x in range(bx, bx + bw))
            if top and bot: out.append((bx, by - 1, bw, bh + 2, (bx, by, bw, bh), True))
        else:
            l = bx > 0 and all(g[y][bx - 1] in "[]" for y in range(by, by + bh))
            r = bx + bw < COLS and all(g[y][bx + bw] in "[]" for y in range(by, by + bh))
            if l and r: out.append((bx - 1, by, bw + 2, bh, (bx, by, bw, bh), False))
    return out

def bed_sprites(rid, room):
    """cached [(cells, sprite, (left, top) room px, sort_y)] for the beds that have the art set; the bake skips `cells`"""
    if "_beds" in room: return room["_beds"]
    out = []
    for x0, y0, w, h, (bx, by, bw, bh), vert in bed_footprints(room):
        fw, fh, (ax, ay) = BED_V if vert else BED_H
        if (w * T, h * T + 16) != (fw, fh): continue          # only the sizes drew (6x2, 2x6)
        cov = cover_surface(rid, room, bw, bh)
        if cov: f, i = BEDS + ("bed_frame_v.png" if vert else "bed_frame_h.png"), 0
        else: f, i = BEDS + ("bed_single_v.png" if vert else "bed_single_h.png"), room.get("theme", {}).get("bed_variant", BED_VARIANT.get(rid, 0))
        if not os.path.exists(os.path.join(A, f)): continue
        sp = frame(f, fw, i).copy()
        if cov: sp.blit(cov[0], (cov[1][0] + (bx - x0) * T, cov[1][1] + (by - y0) * T + 16))   # cover on the body cells
        X, Y = x0 * T + w * T // 2, (y0 + h) * T
        out.append(({(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)}, sp, (X - ax, Y - 1 - ay), Y))
    room["_beds"] = out
    return out

def bed_cells(rid, room):
    return set().union(*(b[0] for b in bed_sprites(rid, room))) if bed_sprites(rid, room) else set()

def draw_beds(rid, room, dr):
    for _, sp, (x, y), sy in bed_sprites(rid, room): dr.append((sy, sp, x, y, 0, True))

def in_hook_bbox(rid, room, x, y):
    return any(b[0] <= x < b[0] + b[2] and b[1] <= y < b[1] + b[3] for b in hook_blocks(rid, room))

def theme_tiles_loaded(room):
    ft = room.get("theme", {}).get("floor_tiles")
    return bool(ft and os.path.exists(os.path.join(A, ft)))
