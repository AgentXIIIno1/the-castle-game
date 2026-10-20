"""room 22 Guards Hall (Royal Guard honours) / #19 room 24 Knights Hall (knights' honours): wall trophies, knight
shields, honour banners, honour plaques, plate armour stands, an empty armour rack. python3 make_honours.py
manifest rooms_detail: wall_decals (file, fw, var, x, y[, mount]) as setpiece wall tuples, objects (file, fw, var, x, y, w, fps, light)
as setpiece object tuples (drawn bottom-centre at (x*16+w*8, y*16+16), depth-sorted), blocking cells listed per object."""
import os, sys, random, json, copy
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from art import lerp
import art3, setpiece
INK = (14, 10, 20); SH = (10, 8, 16)
GOLD = [(120, 84, 30), (178, 132, 48), (226, 182, 72), (250, 226, 140)]
SIL = [(70, 72, 84), (112, 116, 128), (160, 164, 176), (214, 218, 226)]
WD = [(40, 26, 20), (66, 44, 30), (94, 64, 42), (124, 88, 58), (156, 116, 78)]
TINCT = {"gules": [(92, 22, 28), (140, 34, 40), (178, 52, 52)], "azure": [(24, 40, 92), (36, 62, 140), (60, 92, 170)],
         "vert": [(22, 66, 42), (34, 98, 58), (56, 128, 76)], "sable": [(22, 20, 28), (38, 36, 46), (58, 56, 66)]}
files = {}
def save(n, sf): pygame.image.save(sf, os.path.join(HERE, n)); files[n] = sf; return sf
def sheet(t, w, h):
    s = surf(w * len(t), h); [s.blit(x, (i * w, 0)) for i, x in enumerate(t)]; return s
def shield_mask(w, h):
    """heater shield: flat top, straight sides to ~55%, curving to a point"""
    m = set()
    for y in range(h):
        for x in range(w):
            u = (x + .5) / w * 2 - 1; t = y / (h - 1)
            half = 1 if t < .55 else max(0, 1 - ((t - .55) / .45) ** 1.6)
            if abs(u) <= half: m.add((x, y))
    return m
def shield(w, h, field, charge):
    s = surf(w, h); M = shield_mask(w, h); F = TINCT[field]
    for (x, y) in M:
        lit = .6 - x / w * .35 - y / h * .15 + (BAYER[y % 4][x % 4] / 16 - .5) * .15
        s.set_at((x, y), F[max(0, min(2, int(lit * 3)))])
    cx = w // 2
    if charge == "crown":
        for x in range(cx - 3, cx + 3): s.set_at((x, h // 2), GOLD[2]); s.set_at((x, h // 2 - 1), GOLD[1])
        for x in (cx - 3, cx - 1, cx + 1): s.set_at((x + (x > cx - 2), h // 2 - 2), GOLD[3])
        s.set_at((cx - 3, h // 2 - 2), GOLD[3]); s.set_at((cx + 2, h // 2 - 2), GOLD[3])
    elif charge == "chevron":
        for k in range(cx):
            for d in (0, 1): s.set_at((cx - 1 - k, h // 3 + k + d), GOLD[2]); s.set_at((cx + k, h // 3 + k + d), GOLD[2])
    elif charge == "cross":
        for y in range(1, h - 3): s.set_at((cx - 1, y), SIL[3]); s.set_at((cx, y), SIL[2])
        for x in range(1, w - 1): s.set_at((x, h // 3), SIL[3]); s.set_at((x, h // 3 + 1), SIL[2])
    elif charge == "lion":                                   # rampant beast, very small: body, head, raised paw, tail
        for (x, y) in ((cx - 1, 4), (cx, 4), (cx, 5), (cx - 1, 5), (cx - 1, 6), (cx, 6), (cx + 1, 6), (cx - 1, 7), (cx, 7), (cx - 2, 8), (cx, 8),
                       (cx + 1, 3), (cx + 2, 4), (cx - 2, 5), (cx + 1, 8), (cx + 2, 7)): s.set_at((x, y), GOLD[2])
        s.set_at((cx, 4), GOLD[3])
    elif charge == "tower":
        pygame.draw.rect(s, GOLD[2], (cx - 2, h // 3, 4, h // 3)); [s.set_at((cx - 2 + k, h // 3 - 1), GOLD[3]) for k in (0, 2)] ; s.set_at((cx, h // 3 + 3), F[0])
    for (x, y) in M:                                         # rim light + border
        if (x - 1, y) not in M or (x, y - 1) not in M: s.set_at((x, y), lerp(s.get_at((x, y))[:3], (240, 230, 210), .35))
    return s

def trophy(v):
    """16x20 face decal: Royal Guard shield (gules, gold crown) over crossed halberds; v1 the shield is sable with a crown"""
    u = surf(16, 20)
    for d in (1, -1):                                        # crossed halberds
        x0 = 2 if d == 1 else 13
        for k in range(17): u.set_at((x0 + d * round(k * 11 / 16), 1 + k), WD[3] if k % 3 else WD[2])
        hx = x0; pygame.draw.rect(u, SIL[2], (hx - 1, 0, 3, 3)); u.set_at((hx, 0), SIL[3])
    sh = shield(10, 12, "gules" if v == 0 else "sable", "crown"); u.blit(sh, (3, 4))
    return outline(u).subsurface((1, 1, 16, 20)).copy() if False else _ol(u)
def _ol(u):
    o = outline(u); s = surf(u.get_width(), u.get_height()); s.blit(o, (-1, -1))
    # keep the outline inside the frame: blit once more to restore edge pixels clipped
    return s
def knight_shield(v):
    """16x16 face decal: a knight's heater shield on a bracket; v0 azure lion, v1 gules chevron, v2 sable cross, v3 vert tower"""
    u = surf(16, 16); f, c = (("azure", "lion"), ("gules", "chevron"), ("sable", "cross"), ("vert", "tower"))[v]
    u.blit(shield(11, 13, f, c), (2, 1)); pygame.draw.rect(u, SIL[1], (6, 0, 4, 1))
    s = _ol(u)
    return s
def banner(v):
    """16x28 'hang' decal: iron rod, cloth with gold fringe, swallowtail; v0 Royal Guard (gules, crown), v1 knights azure star,
    v2 knights vert sword"""
    u = surf(16, 28); F = TINCT[("gules", "azure", "vert")[v]]
    line(u, SIL[1], (1, 1), (14, 1)); u.set_at((1, 1), GOLD[2]); u.set_at((14, 1), GOLD[2])
    for y in range(2, 27):
        for x in range(3, 13):
            if y > 21 and abs(x - 7.5) < (y - 21) * .9: continue        # swallowtail notch
            wave = ((x + y // 3) % 4 == 0) * .1
            lit = .65 - (x - 3) / 10 * .3 - y / 28 * .2 + wave + (BAYER[y % 4][x % 4] / 16 - .5) * .12
            u.set_at((x, y), F[max(0, min(2, int(lit * 3)))])
    for x in range(3, 13): u.set_at((x, 2), GOLD[2])
    for y in range(3, 22): u.set_at((3, y), lerp(u.get_at((3, y))[:3], GOLD[1], .5)); u.set_at((12, y), lerp(u.get_at((12, y))[:3], GOLD[0], .5))
    cx, cy = 8, 11
    if v == 0:
        for x in range(5, 11): u.set_at((x, cy + 1), GOLD[2]); u.set_at((x, cy + 2), GOLD[1])
        for x in (5, 7, 8, 10): u.set_at((x, cy), GOLD[3])
        u.set_at((7, cy - 1), GOLD[3]); u.set_at((8, cy - 1), GOLD[3])
    elif v == 1:
        for (dx, dy) in ((0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (-3, 0), (-2, 0), (-1, 0), (1, 0), (2, 0), (3, 0), (-1, -1), (1, 1), (1, -1), (-1, 1)):
            u.set_at((cx - 1 + dx, cy + dy), SIL[3] if abs(dx) + abs(dy) < 2 else SIL[2])
    else:
        for y in range(6, 18): u.set_at((7, y), SIL[3]); u.set_at((8, y), SIL[2])
        for x in range(5, 11): u.set_at((x, 15), GOLD[2])
        u.set_at((7, 17), GOLD[2]); u.set_at((8, 17), GOLD[2])
    return _ol(u)
def plaque():
    """16x14 face decal: dark oak honour board with gilt name lines and a crown"""
    u = surf(16, 14); pygame.draw.rect(u, WD[1], (1, 1, 14, 11)); pygame.draw.rect(u, GOLD[1], (1, 1, 14, 11), 1)
    for x in range(2, 14): u.set_at((x, 2), WD[3])
    u.set_at((7, 3), GOLD[3]); u.set_at((8, 3), GOLD[3]); u.set_at((6, 4), GOLD[2]); u.set_at((9, 4), GOLD[2])
    for y in (6, 8, 10):
        for x in range(3, 13):
            if (x * 7 + y) % 5: u.set_at((x, y), GOLD[2] if y == 6 else GOLD[1])
    return _ol(u)
def plate_stand():
    """20x34 sorted object: plate armour (Royal Guard, crimson tabard) on a wooden stand, plumed helm; shadow baked"""
    s = surf(20, 34); u = surf(20, 34)
    for y in range(30, 34):
        for x in range(20):
            d = ((x - 10) / 9) ** 2 + ((y - 32) / 2) ** 2
            if d <= 1 and (d < .55 or BAYER[y % 4][x % 4] / 16 > (d - .55) * 2.2): s.set_at((x, y), (*SH, 110))
    line(u, WD[2], (4, 30), (15, 30)); line(u, WD[1], (4, 31), (15, 31)); pygame.draw.rect(u, WD[2], (9, 22, 2, 8))
    def steel(x, y, k=0): return SIL[max(0, min(3, int((.75 - (x - 4) / 12 * .35 - k + (BAYER[y % 4][x % 4] / 16 - .5) * .15) * 4)))]
    for y in range(9, 22):                                   # cuirass + tabard
        w = 5 if y < 18 else 4
        for x in range(10 - w, 10 + w): u.set_at((x, y), steel(x, y))
    for y in range(12, 24):
        for x in range(8, 12): u.set_at((x, y), TINCT["gules"][1 if x < 10 else 0])
    for x in range(8, 12): u.set_at((x, 15), GOLD[2])
    for (x0) in (3, 15):                                     # pauldrons + arms
        pygame.draw.rect(u, SIL[2], (x0, 9, 3, 3)); pygame.draw.rect(u, SIL[1], (x0 + (0 if x0 == 3 else 1), 12, 2, 7))
    pygame.draw.ellipse(u, SIL[2], (7, 2, 6, 7)); line(u, INK, (8, 5), (11, 5)); u.set_at((8, 3), SIL[3])   # helm + visor slit
    for k in range(4): u.set_at((10 + k // 2, 1 - k // 3 + (k == 0)), TINCT["gules"][2])                     # plume
    u.set_at((11, 0), TINCT["gules"][2]); u.set_at((12, 1), TINCT["gules"][1])
    for y in range(9, 18): u.set_at((5, y), lerp(u.get_at((5, y))[:3], SIL[3], .4))                          # rim light
    s.blit(_ol(u), (0, 0)); return s
def rack():
    """32x28 sorted object (2 cells): empty oak armour rack, pegs and a top rail with knight shields gone (pale outlines),
    one leftover gauntlet; shadow baked"""
    s = surf(32, 28); u = surf(32, 28)
    for y in range(24, 28):
        for x in range(32):
            d = ((x - 16) / 15) ** 2 + ((y - 26) / 2) ** 2
            if d <= 1 and (d < .55 or BAYER[y % 4][x % 4] / 16 > (d - .55) * 2.2): s.set_at((x, y), (*SH, 110))
    for x0 in (2, 28): pygame.draw.rect(u, WD[2], (x0, 2, 2, 23)); line(u, WD[4], (x0, 2), (x0, 24))
    for yy in (3, 12, 22):
        pygame.draw.rect(u, WD[2], (2, yy, 28, 2)); line(u, WD[4], (2, yy), (29, yy)); line(u, WD[0], (2, yy + 1), (29, yy + 1))
    for x in (8, 15, 22):
        u.set_at((x, 6), WD[3]); u.set_at((x, 7), WD[3]); u.set_at((x, 15), WD[3]); u.set_at((x, 16), WD[3])          # pegs
        for yy in range(5, 11): u.set_at((x + 3, yy), (88, 62, 44)) if yy in (5, 10) else None                      # pale dust outlines
    pygame.draw.rect(u, SIL[1], (21, 17, 3, 3)); u.set_at((21, 17), SIL[3]); u.set_at((22, 20), SIL[0])            # gauntlet on a peg
    s.blit(_ol(u), (0, 0)); return s

TRO = save("guard_trophy.png", sheet([trophy(v) for v in range(2)], 16, 20))
KSH = save("knight_shields.png", sheet([knight_shield(v) for v in range(4)], 16, 16))
BAN = save("honour_banner.png", sheet([banner(v) for v in range(3)], 16, 28))
PLQ = save("honour_plaque.png", plaque()); PST = save("guard_armour_stand.png", plate_stand()); RCK = save("armour_rack.png", rack())

H = "honours/"
PL = {22: {"wall": [(H + "honour_banner.png", 16, 0, 3, 1, "hang"), (H + "guard_trophy.png", 16, 0, 5, 1), (H + "guard_trophy.png", 16, 1, 9, 1),
                    (H + "honour_plaque.png", 16, 0, 11, 1), (H + "guard_trophy.png", 16, 1, 13, 1), (H + "guard_trophy.png", 16, 0, 15, 1),
                    (H + "honour_banner.png", 16, 0, 21, 1, "hang")],
           "obj": [(H + "guard_armour_stand.png", 20, None, 2, 3, 1, 0, None), (H + "guard_armour_stand.png", 20, None, 21, 3, 1, 0, None),
                   (H + "guard_armour_stand.png", 20, None, 2, 14, 1, 0, None), (H + "guard_armour_stand.png", 20, None, 21, 14, 1, 0, None)]},
      24: {"wall": [(H + "knight_shields.png", 16, 0, 8, 1), (H + "honour_banner.png", 16, 1, 10, 1, "hang"), (H + "knight_shields.png", 16, 1, 11, 1),
                    (H + "honour_plaque.png", 16, 0, 13, 1), (H + "knight_shields.png", 16, 2, 18, 1), (H + "honour_banner.png", 16, 2, 20, 1, "hang"),
                    (H + "knight_shields.png", 16, 3, 21, 1)],
           "obj": [(H + "armour_rack.png", 32, None, 18, 2, 2, 0, None)]}}
KEEP24 = {(15, 2), (14, 2), (16, 2), (15, 3), (14, 3), (16, 3)}   # #28 armour stand cell + approach
R = rooms()
def bfs(w, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and w[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
DET = {}
for rid, p in PL.items():
    g, w = R[rid]["grid"], R[rid]["walk"]
    for t in p["wall"]:
        assert g[t[4]][t[3]] == "#" and not art3.is_post(g, t[3], t[4]) and w[t[4] + 1][t[3]], (rid, t)
        if rid == 24: assert t[3] not in (14, 15, 16), t                     # the stand's sprite covers the face at x14-16
    blk = [(t[3] + k, t[4]) for t in p["obj"] for k in range(t[5])]
    for c in blk: assert w[c[1]][c[0]], (rid, c)
    if rid == 24: assert not (set(blk) & KEEP24)
    items = [(i["x"], i["y"]) for i in R[rid].get("items", [])] + [(m["x"], m["y"]) for m in R[rid].get("mons", [])] + ([(15, 2)] if rid == 24 else [])
    assert not (set(blk) & set(items))
    w2 = [r[:] for r in w]
    for x, y in blk: w2[y][x] = False
    cells = [(x, y) for y in range(18) for x in range(24) if w2[y][x]]
    ok = len(bfs(w2, cells[0])) == len(cells)
    edge = [(x, y) for (x, y) in cells if x in (0, 23) or y in (0, 17)]
    assert ok, rid
    DET[str(rid)] = {"name": R[rid]["name"], "wall_decals": [list(t) for t in p["wall"]], "objects": [list(t) for t in p["obj"]],
                     "blocking_added": [list(c) for c in blk], "post_cells": [[x, y] for y in range(18) for x in range(24) if art3.is_post(g, x, y)],
                     "bfs_all_walkable_connected_with_blocking": ok, "exits_reachable": len(edge)}
DET["24"]["kept_clear"] = sorted([list(c) for c in KEEP24])
copy_to_game(HERE, "honours")
man = {"set": "honours", "issues": [18, 19], "rooms": [22, 24],
 "sheets": {"guard_trophy.png": {"frame_size": [16, 20], "variants": 2, "mount": "face (bottom on the wall face, top 6px over the wall top)", "content": "Royal Guard shield (v0 gules / v1 sable, gold crown) over crossed halberds"},
            "knight_shields.png": {"frame_size": [16, 16], "variants": 4, "mount": "face", "content": "knights' heater shields: v0 azure lion, v1 gules chevron, v2 sable cross, v3 vert tower"},
            "honour_banner.png": {"frame_size": [16, 28], "variants": 3, "mount": "hang", "content": "v0 Royal Guard crimson + gold crown, v1 knights azure + silver star, v2 knights vert + sword; gold fringe, swallowtail"},
            "honour_plaque.png": {"frame_size": [16, 14], "mount": "face", "content": "oak honour board, gilt crown and name lines"},
            "guard_armour_stand.png": {"frame_size": [20, 34], "anchor": [10, 33], "layer": "sorted object (object tuple, w 1)", "shadow_baked": True, "blocking": True, "content": "Royal Guard plate armour on a stand, crimson tabard, plumed helm"},
            "armour_rack.png": {"frame_size": [32, 28], "anchor": [16, 27], "layer": "sorted object (object tuple, w 2)", "shadow_baked": True, "blocking": True, "content": "empty oak armour rack with pegs, dust outlines of the missing pieces, one gauntlet left"}},
 "rooms_detail": DET,
 "room_themes_pending": {"22": {"name": "Guards Hall", "setpiece": True}, "24": {"name": "Knights Hall", "setpiece": True}},
 "integration_notes": ["wall_decals like the towers/dungeon sets (setpiece.wall_spots); objects -> OBJ_ROOMS (draw_objects, depth-sorted) and block rooms_detail.blocking_added",
                "room 24 also keeps the #28 chain-mail stand (15,2) and its approach clear (kept_clear); the stand's sprite covers the wall face at x14-16, so no decals there",
                "then add room_themes_pending (setpiece: true) so the random banners/sconces don't double up (today's random red banner at (19,1) in room 24 would sit behind the rack)"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
copy_to_game(HERE, "honours")
def bake(rid, after):
    room = copy.deepcopy(R[rid])
    if after: [room.pop(k, None) for k in ("decor", "_set_done", "set_objs")]; room["theme"] = dict(room.get("theme", {}), setpiece=True)
    raw, top = art3.bake_room(rid, room); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
    b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if after:
        for t in sorted(PL[rid]["wall"], key=lambda t: t[4]):
            sp = setpiece.frame(t[0], t[1], t[2]); b.blit(sp, setpiece.wall_xy(t, sp, top))
        dr = [(t[4], files[t[0].split("/")[1]], t) for t in PL[rid]["obj"]]
        if rid == 24:
            st = json.load(open(os.path.join(GAME, "assets", "chain_mail", "manifest.json")))["stand_full"]
            dr.append((st["sort_y"] / 16 - 1, pygame.image.load(os.path.join(GAME, "assets", "chain_mail", st["file"])), ("stand", st["topleft"])))
        for _, sp, t in sorted(dr, key=lambda d: d[0]):
            if t[0] == "stand": b.blit(sp, (t[1][0], t[1][1] + top)); continue
            X, Y = t[3] * 16 + t[5] * 8, t[4] * 16 + 16
            b.blit(sp, (X - sp.get_width() // 2, Y - sp.get_height() + top))
    return b
font = pygame.font.Font(None, 18)
for rid in PL:
    P = pygame.Surface((2 * 768 + 30, 654)); P.fill((40, 36, 48))
    for j, af in enumerate((False, True)):
        x0 = 10 + j * 778
        P.blit(font.render(f"#{18 if rid == 22 else 19} room {rid} {R[rid]['name']} - {'AFTER' if af else 'before'}", True, (230, 220, 200)), (x0, 6))
        P.blit(pygame.transform.scale(bake(rid, af), (768, 624)), (x0, 24))
    pygame.image.save(P, os.path.join(HERE, f"preview_{rid}.png"))
Z = pygame.Surface((150, 40)); Z.fill((60, 54, 62)); Z.blit(TRO, (2, 2)); Z.blit(KSH, (36, 2)); Z.blit(BAN, (2, 10)) if False else Z.blit(BAN, (100, 2)); Z.blit(PLQ, (2, 24)); Z.blit(PST, (20, 4)) if False else None
Z.blit(RCK, (36, 18)); Z.blit(PST, (70, 4))
pygame.image.save(pygame.transform.scale(Z, (900, 240)), os.path.join(HERE, "preview_sheets.png"))
print("ok", {k: v["bfs_all_walkable_connected_with_blocking"] for k, v in DET.items()})
