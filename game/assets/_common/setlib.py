"""shared helpers for hand-placed set dressing (#14-#17): placement checks, BFS with new blocking, rooms_detail, before/after previews.
PL = {rid: {"wall": [(file, fw, var, x, y[, mount])], "floor": [(file, fw, var, x, y[, flip])], "obj": [(file, fw, var, x, y, w, fps, light)],
            "block": [(x, y)] extra blocking cells (default: each object's w cells on its row)}}"""
import os, copy, json
from collections import deque
from monlib import *
from roomprev import rooms, copy_to_game
import art3, setpiece
R = rooms()
def bfs(w, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and w[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
def blocking(p): return p.get("block") or [(t[3] + k, t[4]) for t in p.get("obj", []) for k in range(t[5])]
def check(rid, p, keep=()):
    g, w = R[rid]["grid"], R[rid]["walk"]
    for t in p.get("wall", []):
        x, y, m = t[3], t[4], (t[5:] or ("face",))[0]
        assert g[y][x] == "#" and not art3.is_post(g, x, y), (rid, t)
        if m == "east": assert w[y][x - 1], (rid, t)
        elif m == "west": assert w[y][x + 1], (rid, t)
        else: assert w[y + 1][x], (rid, t)
    for t in p.get("floor", []): assert w[t[4]][t[3]], (rid, t)
    blk = blocking(p)
    occupied = {(i["x"], i["y"]) for i in R[rid].get("items", [])} | {(m["x"], m["y"]) for m in R[rid].get("mons", [])} | set(keep)
    for c in blk: assert w[c[1]][c[0]] and c not in occupied, (rid, c)
    w2 = [r[:] for r in w]
    for x, y in blk: w2[y][x] = False
    cells = [(x, y) for y in range(18) for x in range(24) if w2[y][x]]
    ok = len(bfs(w2, cells[0])) == len(cells); assert ok, rid
    return {"name": R[rid]["name"], "wall_decals": [list(t) for t in p.get("wall", [])], "floor_decals": [list(t) for t in p.get("floor", [])],
            "objects": [list(t) for t in p.get("obj", [])], "blocking_added": [list(c) for c in blk],
            "post_cells": [[x, y] for y in range(18) for x in range(24) if art3.is_post(g, x, y)], "bfs_all_walkable_connected_with_blocking": ok}
def bake(rid, p, after, files, extra=None):
    room = copy.deepcopy(R[rid])
    if after: [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]; room["theme"] = dict(room.get("theme", {}), setpiece=True)
    raw, top = art3.bake_room(rid, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
    b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if not after: return b
    get = lambda t: files[os.path.basename(t[0])].subsurface(((t[2] or 0) * t[1], 0, t[1], files[os.path.basename(t[0])].get_height()))
    for t in p.get("floor", []):
        sp = get(t); sp = pygame.transform.flip(sp, True, False) if len(t) > 5 and t[5] else sp; b.blit(sp, (t[3] * 16, t[4] * 16 + top))
    for t in sorted(p.get("wall", []), key=lambda t: t[4]): sp = get(t); b.blit(sp, setpiece.wall_xy(t, sp, top))
    dr = [(t[4] * 16 + 16, get(t), t[3] * 16 + t[5] * 8 - t[1] // 2, None) for t in p.get("obj", [])] + (extra or [])
    for Y, sp, x, y in sorted(dr, key=lambda d: d[0]): b.blit(sp, (x, (Y - sp.get_height() if y is None else y) + top))
    return b
def previews(here, PL, files, label, extra={}):
    font = pygame.font.Font(None, 18)
    for rid, p in PL.items():
        P = pygame.Surface((2 * 768 + 30, 654)); P.fill((40, 36, 48))
        for j, af in enumerate((False, True)):
            x0 = 10 + j * 778
            P.blit(font.render(f"{label[rid]} room {rid} {R[rid]['name']} - {'AFTER' if af else 'before'}", True, (230, 220, 200)), (x0, 6))
            P.blit(pygame.transform.scale(bake(rid, p, af, files, extra.get(rid)), (768, 624)), (x0, 24))
        pygame.image.save(P, os.path.join(here, f"preview_{rid}.png"))
