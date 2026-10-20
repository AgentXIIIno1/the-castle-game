"""room 6 East Dining Room: a glimpse of the garden patio through the large east opening (x22-23, y5-12): sunlit patio
flags with moss and grass in the joints, a flower-bed edge and a box hedge corner at each side, daylight falling inward
(floor decals, nothing blocks the exit). python3 make_patio.py"""
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from setlib import *
from art import lerp
GR = [(30, 52, 30), (44, 74, 40), (62, 98, 52), (90, 128, 66), (128, 160, 84)]
FL = [(200, 70, 80), (230, 200, 90), (190, 150, 220), (240, 240, 230)]
SAND = [(92, 84, 72), (114, 104, 86), (136, 124, 102), (160, 148, 120)]
files = {}
def save(n, sf): pygame.image.save(sf, os.path.join(HERE, n)); files[n] = sf; return sf
def sheet(t, w, h):
    s = surf(w * len(t), h); [s.blit(x, (i * w, 0)) for i, x in enumerate(t)]; return s
def flag(v, sun):
    """opaque 16x16 patio tile: pale sandstone flags, grass in the joints; sun = 0 (threshold, x22) .. 1 (outside, x23)"""
    r = random.Random(60 + v * 7 + int(sun * 3)); s = surf(16, 16); split = r.choice((6, 8, 10))
    for y in range(16):
        for x in range(16):
            b = .35 + sun * .2 + (x / 15) * .12 * (1 - sun) + (BAYER[y % 4][x % 4] / 16 - .5) * .2 + ((x * 5 + y * 3 + v) % 11 == 0) * .1
            s.set_at((x, y), SAND[max(0, min(3, int(b * 4)))])
    for k in range(16):
        for (x, y) in ((k, split), (15, k), (k, 15)):
            s.set_at((x, y), GR[1 + (k + v) % 3] if r.random() < .6 else (70, 64, 56))
    for _ in range(3 + v):                                                       # moss/grass tufts
        x, y = r.randrange(16), r.choice((split, 15)); s.set_at((x, max(0, y - 1)), GR[3]); s.set_at((x, y), GR[2])
    if v == 3:                                                                   # a daisy in a crack
        s.set_at((5, split - 1), FL[3]); s.set_at((4, split - 1), FL[3]); s.set_at((5, split - 2), FL[1])
    return s
def bed(edge):
    """opaque 16x16: flower-bed + box hedge corner seen past the opening (edge 0 = north side y5, 1 = south side y12):
    hedge along the wall side, flowers, then flags"""
    r = random.Random(7 + edge); s = flag(0, 1)
    rows = range(0, 9) if edge == 0 else range(7, 16)
    for y in rows:
        for x in range(16):
            dy = y if edge == 0 else 15 - y
            if dy < 5:                                                           # box hedge, lit top
                c = GR[max(0, min(4, 1 + (4 - dy) // 2 + (BAYER[y % 4][x % 4] < 5)))]; s.set_at((x, y), c)
            elif dy < 9:                                                         # bed soil + flowers
                s.set_at((x, y), (70, 52, 40) if BAYER[y % 4][x % 4] < 8 else (88, 66, 48))
                if r.random() < .25: s.set_at((x, y), r.choice(FL))
                elif r.random() < .3: s.set_at((x, y), GR[3])
    for x in range(16): s.set_at((x, (4 if edge == 0 else 11)), (24, 40, 24))
    return s
def light():
    """16x16 alpha floor decal: warm daylight spilling onto the dining-room floor at the threshold (x21), fading west"""
    s = surf(16, 16)
    for y in range(16):
        for x in range(16):
            u = 1 - x / 15
            if BAYER[y % 4][x % 4] / 16 < (1 - u) * .9: s.set_at((x, y), (250, 236, 190, int(90 * (1 - u * .7))))
    return s
FLAGS = [flag(v, 0) for v in range(4)] + [flag(v, 1) for v in range(4)]
save("patio_flags.png", sheet(FLAGS, 16, 16)); save("patio_bed.png", sheet([bed(0), bed(1)], 16, 16)); save("patio_light.png", light())
P_ = "patio/"
fl = []
for y in range(5, 13):
    fl.append((P_ + "patio_light.png", 16, 0, 21, y))
    if y == 5: fl += [(P_ + "patio_bed.png", 16, 0, 22, y), (P_ + "patio_bed.png", 16, 0, 23, y)]
    elif y == 12: fl += [(P_ + "patio_bed.png", 16, 1, 22, y), (P_ + "patio_bed.png", 16, 1, 23, y)]
    else: fl += [(P_ + "patio_flags.png", 16, (y * 3) % 4, 22, y), (P_ + "patio_flags.png", 16, 4 + (y * 5 + 1) % 4, 23, y)]
PL = {6: {"floor": fl}}
DET = {"6": check(6, PL[6])}
DET["6"]["note"] = "the patio flags/beds are opaque and replace the floor in x22-23 (draw them in draw_floor); all cells stay walkable (the east exit to room 18 is untouched)"
DET["6"]["light_suggestion"] = {"cells": [[22, y] for y in range(5, 13, 2)], "radius": 28, "colour": [70, 64, 44], "note": "warm daylight, like TOWER_LIGHT"}
man = {"set": "patio", "issues": [14], "rooms": [6],
 "sheets": {"patio_flags.png": {"frame_size": [16, 16], "variants": 8, "frame_use": "0-3 threshold column x22 (a little shaded), 4-7 outside x23 (full sun)", "layer": "opaque floor decal", "content": "pale sandstone patio flags, grass and moss in the joints, a daisy (v3)"},
            "patio_bed.png": {"frame_size": [16, 16], "variants": 2, "frame_use": "0 north edge (y5), 1 south edge (y12)", "layer": "opaque floor decal", "content": "box hedge + flower bed along the opening's side walls, then flags"},
            "patio_light.png": {"frame_size": [16, 16], "layer": "floor decal (alpha) at x21", "content": "warm daylight spilling in, fading west"}},
 "rooms_detail": DET,
 "integration_notes": ["floor_decals -> draw_floor for room 6 (no setpiece flag needed: nothing replaces the random decor)", "optional: warm light points (light_suggestion)", "no blocking"]}
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2); copy_to_game(HERE, "patio")
previews(HERE, PL, files, {6: "#14"}); print("ok", DET["6"]["bfs_all_walkable_connected_with_blocking"])
