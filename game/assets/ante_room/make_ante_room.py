"""room 13 Ante Room: traces of the benches that lined the walls - pale clean strips and leg scuffs on the floor,
back-rail rub marks on the side walls, one broken bench left behind. python3 make_ante_room.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from setlib import *
from art import lerp
FACE = art3.FACE; WD = [(40, 26, 20), (66, 44, 30), (94, 64, 42), (124, 88, 58), (156, 116, 78)]; SH = (10, 8, 16); files = {}
def save(n, sf): pygame.image.save(sf, os.path.join(HERE, n)); files[n] = sf; return sf
def sheet(t, w, h):
    s = surf(w * len(t), h); [s.blit(x, (i * w, 0)) for i, x in enumerate(t)]; return s
def mark(v):
    """16x16 floor decal for a vertical bench run against the WEST wall (flip for the east wall): a less-worn strip in x8-15 (x0-7 lie under the wall's 8px side face)
    with leg scuffs; v0 run top end, v1 middle, v2 bottom end"""
    s = surf(16, 16)
    y0, y1 = (3 if v == 0 else 0), (12 if v == 2 else 16)
    for y in range(y0, y1):
        for x in range(8, 16):
            if BAYER[y % 4][x % 4] < 9: s.set_at((x, y), (20, 14, 16, 120))        # stone the bench kept from wear
    for y in range(y0, y1):                                                        # bench front edge (the floor beyond is worn paler)
        s.set_at((15, y), (12, 8, 12, 150)) if y % 3 else None
    for (lx, ly) in ([(9, 4), (13, 4)] if v == 0 else [(9, 12), (13, 12)] if v == 2 else [(9, 8), (13, 8)]):
        pygame.draw.rect(s, (12, 8, 12, 200), (lx, ly, 2, 2)); s.set_at((min(15, lx + 2), ly + 1), (214, 190, 150, 120))     # leg marks
    for k in range(4): s.set_at((8 + k * 2, (y0 + y1) // 2 + (k % 2)), (180, 170, 156, 70))                         # scratches
    return s
def rub(east):
    """16 x 16+FACE side-face decal: darker polished band where bench backs rubbed the wall (east mount: face x8-15; west: x0-7)"""
    s = surf(16, 16 + FACE); x0 = 8 if east else 0
    for y in range(16 + 2, 16 + 7):
        for x in range(x0, x0 + 8):
            if BAYER[y % 4][x % 4] < 10: s.set_at((x, y), (12, 8, 14, 140))
    for x in range(x0, x0 + 8): s.set_at((x, 16 + 2), (220, 206, 190, 120))
    return s
def bench():
    """16x40 sorted object, vertical bench along the east wall covering 2 cells: oak seat, one end's legs gone so it slumps
    to the floor, a split board; shadow baked"""
    s = surf(16, 40); u = surf(16, 40)
    for y in range(34, 40):
        for x in range(16):
            d = ((x - 8) / 7) ** 2 + ((y - 37) / 3) ** 2
            if d < 1 and BAYER[y % 4][x % 4] / 16 < 1 - d: s.set_at((x, y), (*SH, 100))
    for y in range(6, 36):
        sl = 0 if y > 20 else (20 - y) // 5                                        # top end slumped lower (closer to the floor)
        for x in range(3, 13):
            lit = .65 - (x - 3) / 10 * .3 + (BAYER[y % 4][x % 4] / 16 - .5) * .1
            u.set_at((x, y + (3 - sl if y < 20 else 0)), WD[max(0, min(4, int(lit * 5)))])
    for y in range(9, 36, 6): line(u, WD[1], (3, y), (12, y))
    line(u, WD[0], (8, 12), (7, 30))                                               # the split board
    pygame.draw.rect(u, WD[1], (3, 36, 10, 3)); pygame.draw.rect(u, WD[1], (4, 26, 2, 10)); pygame.draw.rect(u, WD[1], (10, 26, 2, 10))   # front legs
    for (x, y) in ((1, 4), (14, 7), (13, 2)): u.set_at((x, y), WD[3])               # splinters
    s.blit(outline(u), (-1, -1)); return s
save("bench_marks.png", sheet([mark(v) for v in range(3)], 16, 16)); save("bench_rub.png", sheet([rub(True), rub(False)], 16, 16 + FACE)); save("bench_broken.png", bench())
A_ = "ante_room/"
PL = {13: {"floor": [(A_ + "bench_marks.png", 16, 0, 7, 6), (A_ + "bench_marks.png", 16, 1, 7, 7), (A_ + "bench_marks.png", 16, 1, 7, 8),
                     (A_ + "bench_marks.png", 16, 1, 7, 9), (A_ + "bench_marks.png", 16, 1, 7, 10), (A_ + "bench_marks.png", 16, 2, 7, 11),
                     (A_ + "bench_marks.png", 16, 0, 16, 6, True), (A_ + "bench_marks.png", 16, 2, 16, 7, True)],
           "wall": [(A_ + "bench_rub.png", 16, 1, 6, 8, "west"), (A_ + "bench_rub.png", 16, 1, 6, 9, "west"), (A_ + "bench_rub.png", 16, 1, 6, 10, "west"),
                    (A_ + "bench_rub.png", 16, 0, 17, 8, "east"), (A_ + "bench_rub.png", 16, 0, 17, 9, "east")],
           "obj": [(A_ + "bench_broken.png", 16, None, 16, 10, 1, 0, None)], "block": [(16, 9), (16, 10)]}}
DET = {"13": check(13, PL[13])}
DET["13"]["note"] = "bench_broken is drawn bottom-centre at (16*16+8, 11*16) and covers cells (16,9)-(16,10): block both. The east bench's marks continue under it (16,6)-(16,7)"
man = {"set": "ante_room", "issues": [17], "rooms": [13],
 "sheets": {"bench_marks.png": {"frame_size": [16, 16], "variants": 3, "layer": "floor decal (alpha); 6th tuple field = flip for the east wall", "content": "where the benches stood: unworn strip, leg marks, scratches; v0 top end, v1 middle, v2 bottom end"},
            "bench_rub.png": {"frame_size": [16, 16 + FACE], "frames": 2, "frame_use": "0 east mount ((x-1)*16, y*16+TOP-8); 1 west mount ((x+1)*16, ...)", "content": "dark polished band where bench backs rubbed the side walls"},
            "bench_broken.png": {"frame_size": [16, 40], "anchor": [8, 39], "layer": "sorted object (w 1, 2 cells tall), blocking (16,9)+(16,10)", "shadow_baked": True, "content": "one broken oak bench left against the east wall, slumped at one end, split seat"}},
 "rooms_detail": DET, "room_themes_pending": {"13": {"name": "Ante Room", "setpiece": True}},
 "integration_notes": ["wall_decals -> setpiece.wall_spots (east/west mounts), floor_decals -> draw_floor, objects -> OBJ_ROOMS, block rooms_detail.blocking_added", "then add room_themes_pending (setpiece: true)"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2); copy_to_game(HERE, "ante_room")
previews(HERE, PL, files, {13: "#17"}); print("ok", DET["13"]["bfs_all_walkable_connected_with_blocking"])
