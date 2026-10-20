"""room 12 Castle Museum: empty plinths, an empty display case, dust outlines on the floor where pieces stood,
pale outlines of missing paintings / an empty weapon bracket on the north wall. python3 make_museum.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from setlib import *
from art import lerp
MAR = [(86, 82, 90), (120, 116, 122), (156, 152, 156), (196, 192, 194), (226, 222, 222)]
GOLD = [(120, 84, 30), (178, 132, 48), (226, 182, 72)]
VEL = [(70, 20, 30), (110, 30, 44)]
SH = (10, 8, 16); files = {}
def save(n, sf): pygame.image.save(sf, os.path.join(HERE, n)); files[n] = sf; return sf
def sheet(t, w, h):
    s = surf(w * len(t), h); [s.blit(x, (i * w, 0)) for i, x in enumerate(t)]; return s
def shadow(s, cx, cy, rx, ry):
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1 and (d < .55 or BAYER[y % 4][x % 4] / 16 > (d - .55) * 2.2): s.set_at((x, y), (*SH, 110))
def plinth(v):
    """16x28 sorted object: marble plinth, empty top with a clean square where the artifact stood; v1 velvet cushion, empty; v2 toppled/chipped"""
    s = surf(16, 28); u = surf(16, 28); shadow(s, 8, 25, 8, 2.5)
    for y in range(9, 25):
        for x in range(3, 13):
            lit = .7 - (x - 3) / 10 * .45 + (BAYER[y % 4][x % 4] / 16 - .5) * .12
            u.set_at((x, y), MAR[max(0, min(4, int(lit * 5)))])
    pygame.draw.rect(u, MAR[2], (2, 22, 12, 3)); pygame.draw.rect(u, MAR[2], (2, 8, 12, 3))     # base + cap mouldings
    line(u, MAR[4], (2, 8), (13, 8)); line(u, MAR[0], (2, 10), (13, 10)); line(u, MAR[0], (2, 24), (13, 24))
    pygame.draw.ellipse(u, MAR[3], (2, 5, 12, 6)); pygame.draw.ellipse(u, MAR[1], (2, 5, 12, 6), 1)    # top surface
    if v == 0: pygame.draw.rect(u, MAR[4], (6, 6, 4, 3)); [u.set_at((x, 6), (150, 140, 130)) for x in (5, 10)]   # clean square in the dust
    if v == 1: pygame.draw.ellipse(u, VEL[1], (4, 4, 8, 5)); pygame.draw.ellipse(u, VEL[0], (6, 5, 4, 2))           # empty cushion, dent
    if v == 2:
        for (x, y) in ((12, 5), (13, 6), (12, 6), (11, 5)): u.set_at((x, y), (0, 0, 0, 0))
        line(u, MAR[0], (6, 12), (8, 18)); line(u, MAR[0], (8, 18), (7, 21))
    for y in range(9, 22): u.set_at((3, y), lerp(u.get_at((3, y))[:3], (240, 236, 236), .35))          # rim light
    pygame.draw.rect(u, GOLD[1], (6, 15, 4, 2)); u.set_at((6, 15), GOLD[2])                           # brass label, name worn off
    s.blit(outline(u), (-1, -1)); return s
def case():
    """32x30 sorted object (2 cells): empty glass display case on an oak stand, one pane smashed, glass shards"""
    s = surf(32, 30); u = surf(32, 30); shadow(s, 16, 27, 15, 2.5)
    WD = [(66, 44, 30), (94, 64, 42), (124, 88, 58)]
    pygame.draw.rect(u, WD[1], (2, 16, 28, 7)); line(u, WD[2], (2, 16), (29, 16)); pygame.draw.rect(u, WD[0], (3, 23, 2, 4)); pygame.draw.rect(u, WD[0], (27, 23, 2, 4))
    pygame.draw.rect(u, VEL[0], (3, 9, 26, 7)); pygame.draw.rect(u, VEL[1], (4, 10, 24, 3))           # velvet bed, empty
    for (x, y) in ((8, 11), (9, 11), (18, 12), (19, 12)): u.set_at((x, y), (150, 90, 100))             # pale outlines of two pieces
    glass = (170, 200, 214, 110)
    for y in range(3, 16):
        for x in range(2, 30):
            if not (12 < x < 20 and y < 10): u.set_at((x, y), lerp(u.get_at((x, y))[:3], glass[:3], .35) if u.get_at((x, y)).a else glass)
    pygame.draw.rect(u, WD[2], (2, 2, 28, 14), 1); line(u, (230, 240, 246), (4, 4), (9, 4))
    for (x, y) in ((13, 9), (19, 7), (14, 3)): line(u, (200, 220, 230), (x, y), (x + 2, y + 1))         # broken pane edges
    s.blit(outline(u), (-1, -1))
    for (x, y) in ((10, 28), (20, 29), (23, 27)): s.set_at((x, y), (190, 214, 226))                      # shards on the floor
    return s
def dust(v):
    """16x16 floor decal: clean outline in the dust where an artifact stood. v0 square plinth, v1 round base, v2 long chest"""
    s = surf(16, 16)
    for y in range(16):
        for x in range(16):
            inside = (3 <= x <= 12 and 3 <= y <= 12) if v == 0 else (((x - 7.5) / 5.5) ** 2 + ((y - 7.5) / 4.5) ** 2 < 1) if v == 1 else (1 <= x <= 14 and 5 <= y <= 10)
            edge = BAYER[y % 4][x % 4] / 16
            if inside: s.set_at((x, y), (24, 20, 28, 110))                  # cleaner (darker, unfaded) stone
            elif edge < .35: s.set_at((x, y), (176, 166, 154, 90))         # dust film around it
    return s
def wall_ghost(v):
    """16x14 face decal: v0 paler rectangle + nail where a painting hung, v1 empty weapon bracket (two iron hooks), v2 small oval frame ghost"""
    s = surf(16, 14)
    if v == 0:
        for y in range(2, 12):
            for x in range(2, 14):
                if x in (2, 13) or y in (2, 11) or BAYER[y % 4][x % 4] < 3: s.set_at((x, y), (200, 190, 176, 70))
        s.set_at((8, 1), (40, 36, 40)); s.set_at((8, 0), (120, 116, 120))
    elif v == 1:
        for hx in (3, 11):
            pygame.draw.rect(s, (40, 38, 46), (hx, 4, 2, 2)); line(s, (110, 108, 118), (hx, 6), (hx + 1, 8)); s.set_at((hx + 2, 8), (110, 108, 118))
        for x in range(2, 14): s.set_at((x, 10), (200, 190, 176, 60))
    else:
        for y in range(1, 13):
            for x in range(3, 13):
                d = ((x - 7.5) / 4.5) ** 2 + ((y - 6.5) / 5.5) ** 2
                if .7 < d < 1: s.set_at((x, y), (200, 190, 176, 80))
    return s
save("museum_plinth.png", sheet([plinth(v) for v in range(3)], 16, 28)); save("museum_case.png", case())
save("museum_dust.png", sheet([dust(v) for v in range(3)], 16, 16)); save("museum_wall_ghost.png", sheet([wall_ghost(v) for v in range(3)], 16, 14))
M = "museum/"
PL = {12: {"wall": [(M + "museum_wall_ghost.png", 16, 0, 9, 1), (M + "museum_wall_ghost.png", 16, 1, 11, 1), (M + "museum_wall_ghost.png", 16, 2, 14, 1),
                    (M + "museum_wall_ghost.png", 16, 0, 16, 1), (M + "museum_wall_ghost.png", 16, 0, 19, 1)],
           "floor": [(M + "museum_dust.png", 16, 1, 12, 7), (M + "museum_dust.png", 16, 0, 18, 7), (M + "museum_dust.png", 16, 2, 13, 13),
                     (M + "museum_dust.png", 16, 0, 17, 12), (M + "museum_dust.png", 16, 1, 9, 5)],
           "obj": [(M + "museum_plinth.png", 16, 0, 13, 3, 1, 0, None), (M + "museum_plinth.png", 16, 1, 16, 3, 1, 0, None), (M + "museum_plinth.png", 16, 0, 19, 3, 1, 0, None),
                   (M + "museum_plinth.png", 16, 2, 9, 9, 1, 0, None), (M + "museum_plinth.png", 16, 1, 9, 13, 1, 0, None),
                   (M + "museum_case.png", 32, None, 14, 10, 2, 0, None)]}}
DET = {"12": check(12, PL[12])}
man = {"set": "museum", "issues": [16], "rooms": [12],
 "sheets": {"museum_plinth.png": {"frame_size": [16, 28], "variants": 3, "anchor": [8, 27], "layer": "sorted object, blocking", "shadow_baked": True, "content": "empty marble plinths: v0 clean square where a piece stood, v1 empty velvet cushion, v2 chipped + cracked; worn brass label"},
            "museum_case.png": {"frame_size": [32, 30], "anchor": [16, 29], "layer": "sorted object (w 2), blocking", "shadow_baked": True, "content": "empty glass display case, smashed pane, outlines on the velvet, shards on the floor"},
            "museum_dust.png": {"frame_size": [16, 16], "variants": 3, "layer": "floor decal (alpha)", "content": "dust outlines where artifacts stood: square, round, long chest"},
            "museum_wall_ghost.png": {"frame_size": [16, 14], "variants": 3, "mount": "face", "content": "v0 pale rectangle + nail of a missing painting, v1 empty weapon bracket, v2 oval frame ghost"}},
 "rooms_detail": DET, "room_themes_pending": {"12": {"name": "Castle Museum", "setpiece": True}},
 "integration_notes": ["wall_decals -> setpiece.wall_spots, floor_decals -> draw_floor, objects -> OBJ_ROOMS (depth-sorted), block rooms_detail.blocking_added",
                "then add room_themes_pending (setpiece: true)", "the Sword at (10,4) is untouched and reachable"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2); copy_to_game(HERE, "museum")
previews(HERE, PL, files, {12: "#16"}); print("ok", DET["12"]["bfs_all_walkable_connected_with_blocking"])
