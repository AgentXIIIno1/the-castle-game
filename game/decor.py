"""Seeded per-room decor sprinkle (art/decor, see assets/decor/NOTES.md).
plan(rid, room) is deterministic and cached in room["decor"]; art3.bake_room draws decals,
main.py depth-sorts objects and lights lit sconces. Blocking objects mark room["walk"] False
only if every exit, stair and item stays reachable (BFS check)."""
import json, os, random
from collections import deque
import pygame

T, COLS, ROWS = 16, 24, 18
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "decor")
SPECIAL = set("$%@W[]G=UD,-.|?`'*+")
CRITICAL = {1, 77, 78, 83}          # puzzle rooms: at most one non-blocking decal
_man = None; _img = {}

def manifest():
    global _man
    if _man is None:
        try: _man = json.load(open(os.path.join(DIR, "manifest.json")))["props"]
        except Exception as e: print("[castle diag] decor manifest unavailable:", e); _man = []
    return _man

def frames(p):
    """list of frame surfaces (variants or animation frames) for a prop; [] if missing"""
    f = p["file"]
    if f not in _img:
        try:
            im = pygame.image.load(os.path.join(DIR, f))
            try: im = im.convert_alpha()
            except pygame.error: pass
            fw, fh = p["frame_size"]
            _img[f] = [im.subsurface((i * fw, 0, fw, fh)) for i in range(im.get_width() // fw)]
        except Exception as e:
            print("[castle diag] decor art missing:", f, e); _img[f] = []
    return _img[f]

def theme(rid, room, floor_kind):
    if room.get("theme", {}).get("decor"): return room["theme"]["decor"]
    if "GARDEN" in (room.get("const") or ""): return "garden"
    return "dungeon" if floor_kind(rid, room) == "cave" else "indoor"

def _bfs(walk, start, blocked=frozenset()):
    prev = {start: None}; q = deque([start])
    while q:
        c = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in prev and walk[n[1]][n[0]] and n not in blocked:
                prev[n] = c; q.append(n)
    return prev

def plan(rid, room, floor_kind):
    if "decor" in room: return room["decor"]
    g, walk = room["grid"], room["walk"]
    rnd = random.Random(rid * 104729)
    th = theme(rid, room, floor_kind)
    props = [p for p in manifest() if th in p["themes"] and frames(p)] if not room.get("theme", {}).get("setpiece") else []
    W = lambda x, y: 0 <= x < COLS and 0 <= y < ROWS and walk[y][x]
    wall = lambda x, y: 0 <= x < COLS and 0 <= y < ROWS and g[y][x] == "#"
    from art3 import is_post
    post = lambda x, y: is_post(g, x, y)          # wall posts are drawn over the wall faces: keep wall decals off them
    # anchors that must stay connected: exit gaps (walkable edge cells), cells beside stairs/doors, items, monsters
    edge = [(x, y) for y in range(ROWS) for x in range(COLS) if walk[y][x] and (x in (0, COLS - 1) or y in (0, ROWS - 1))]
    near = lambda pts: [(x + dx, y + dy) for x, y in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if W(x + dx, y + dy)]
    stairs = [(x, y) for y in range(ROWS) for x in range(COLS) if g[y][x] in "UDG"]
    things = [(i["x"], i["y"]) for i in room.get("items", []) + room.get("hidden", [])] + [(m["col"] - 1, m["row"] - 1) for m in room.get("monsters", [])]
    keys = list(dict.fromkeys(edge + near(stairs) + [t for t in things if W(*t)] + near([t for t in things if not W(*t)])))
    # exclusion zone: specials, things, exits, and every BFS shortest path between key cells
    excl = set(keys) | set(things)
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] in SPECIAL: excl.update((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    for t in things: excl.update((t[0] + dx, t[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    for i, a in enumerate(keys[:40]):
        prev = _bfs(walk, a)
        for b in keys[i + 1:40]:
            c = b if b in prev else None
            while c is not None: excl.add(c); c = prev[c]
    free = lambda x, y: W(x, y) and (x, y) not in excl
    def cands(rule, p):
        out = []
        for y in range(ROWS):
            for x in range(COLS):
                if "wall-top-corner" in rule:
                    if free(x, y) and wall(x, y - 1) and (wall(x - 1, y) or wall(x + 1, y)): out.append((x, y, wall(x + 1, y) and not wall(x - 1, y)))
                elif "wall-face" in rule:
                    w2 = p["frame_size"][0] // T
                    if all(wall(x + k, y) and not wall(x + k, y + 1) and W(x + k, y + 1) for k in range(w2)): out.append((x, y, False))
                else:
                    ok8 = free(x, y) and all(W(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                    base = free(x, y) and (wall(x, y - 1) or wall(x - 1, y) or wall(x + 1, y))
                    door = free(x, y) and any(abs(x - ex) + abs(y - ey) <= 2 for ex, ey in edge)
                    w2 = p["frame_size"][0] // T
                    if w2 > 1 and not all(free(x + k, y) for k in range(w2)): continue
                    if ("floor-open" in rule and ok8) or ("wall-base" in rule and base) or ("near-doorway" in rule and door): out.append((x, y, False))
        return out
    n = rnd.choice([1, 2, 2, 3, 3, 4]) if rid not in CRITICAL else 1
    decals, objects, anim, used, placed = [], [], [], set(), {}
    tries = 0; subtle = 0; wallfp = set()
    import setpiece
    if rid in setpiece.TOWER_WALL:      # (#20-#23) random decor stays off the arrow slits and their daylight patches
        for p in setpiece.TOWER_WALL[rid]: wallfp |= set(setpiece.wall_cells(p)); excl.update(setpiece.wall_cells(p))
        for p in setpiece.TOWER_FLOOR.get(rid, []): excl.update((p[3] + dx, p[4] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    while len(decals) + len(objects) + len(anim) < n and props and tries < 30:
        tries += 1
        p = rnd.choices(props, weights=[q["weight"] for q in props])[0]
        nm = p["name"]
        if placed.get(nm, 0) >= p["max_per_room"] or (p["blocking"] and rid in CRITICAL): continue
        cs = [c for c in cands(p["placement"], p) if (c[0], c[1]) not in used
              and all(abs(c[0] - a) + abs(c[1] - b) >= 3 for a, b in placed.get(nm + "@", []))]
        if not cs: continue
        x, y, mirror = rnd.choice(cs)
        if "wall-face" in p["placement"]:   # never on a post or over another wall decal (either covered it);
            w2 = p["frame_size"][0] // T     # same rnd draws, so the rest of the room is unchanged
            onp = lambda c: any(post(c[0] + k, c[1]) or (c[0] + k, c[1]) in wallfp for k in range(w2))
            if onp((x, y)):
                ok = [c for c in cs if not onp(c)]
                if not ok: continue
                x, y, mirror = min(ok, key=lambda c: (abs(c[0] - x) + abs(c[1] - y), c[1], c[0]))
            wallfp |= {(x + k, y) for k in range(w2)}
        fr = frames(p); var = rnd.randrange(len(fr)) if p.get("variants") else 0
        if p["blocking"]:
            blocked = {(x, y)}
            reach = _bfs(walk, keys[0], blocked) if keys else {}
            if not all(k in reach for k in keys if k not in blocked) or (x, y) in keys: continue
        alpha, flip = 255, mirror
        if p["layer"] != "object" and not p.get("frames") and subtle < 2 and rnd.random() < .5:
            subtle += 1; alpha = rnd.randint(178, 255); flip = flip or rnd.random() < .5
        rec = dict(file=p["file"], name=nm, layer=p["layer"], rule=p["placement"], x=x, y=y, var=var, flip=flip, alpha=alpha, fps=p.get("fps", 0),
                   light=bool(p.get("light", "") and "lit" in str(p.get("light")) and "none" not in str(p.get("light"))))
        if p["layer"] == "object": objects.append(rec)
        elif p.get("frames", 1) and p.get("fps"): anim.append(rec)
        else: decals.append(rec)
        used.add((x, y)); placed[nm] = placed.get(nm, 0) + 1; placed.setdefault(nm + "@", []).append((x, y))
    room["decor"] = dict(decals=decals, objects=objects, anim=anim, phase=rnd.random())
    apply_blocking(room)
    return room["decor"]

def apply_blocking(room):
    import setpiece
    if room.get("id") is not None: setpiece.apply_blocking(room["id"], room)
    for o in room.get("decor", {}).get("objects", []): room["walk"][o["y"]][o["x"]] = False

def prop(file): return next(p for p in manifest() if p["file"] == file)

def surf_for(rec, k=None):
    fr = frames(prop(rec["file"]))
    s = fr[rec["var"] if k is None else k % len(fr)]
    if rec["flip"]: s = pygame.transform.flip(s, True, False)
    if rec["alpha"] < 255: s = s.copy(); s.set_alpha(rec["alpha"])
    return s

def wall_pos(rec, top, raise_):
    """wall-face decal: top-left of the wall FACE (just below the wall top); corner/floor: top-left of the floor cell"""
    if "wall-face" in rec["rule"]: return rec["x"] * T, rec["y"] * T + top - raise_ + T
    return rec["x"] * T, rec["y"] * T + top

def draw_floor(s, room, top):
    for r in room["decor"]["decals"]:
        if r["layer"] == "floor decal": s.blit(surf_for(r), (r["x"] * T, r["y"] * T + top))

def draw_wall(s, room, top, raise_, row=None):
    for r in room["decor"]["decals"]:
        if r["layer"] == "wall decal" and (row is None or r["y"] == row): s.blit(surf_for(r), wall_pos(r, top, raise_))
