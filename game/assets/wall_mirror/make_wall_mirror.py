"""Room 67 large tarnished wall mirror on the east wall (glyph column ',' '|'x4 '`' at x18, y6-11 0-based). python3 make_wall_mirror.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
GOLD = [(92, 64, 26), (140, 104, 42), (186, 146, 64), (226, 192, 110), (250, 230, 170)]
GL = [(34, 40, 48), (52, 62, 72), (78, 92, 104), (120, 140, 150), (190, 208, 214)]
FW, FH = 16, 108; AX, AY = 8, 107                  # 1x6 column (96px) + 12px headroom (frame crest rises above)
def mirror():
    s = surf(FW, FH); u = surf(FW, FH); r = random.Random(67)
    # seen edge-on from the room (west): frame is a tall narrow parallelogram leaning on the east wall
    fr = [(3, 16), (12, 8), (12, 100), (3, 104)]
    pygame.draw.polygon(u, GOLD[1], fr)
    gl = [(5, 18), (11, 13), (11, 97), (5, 101)]
    pygame.draw.polygon(u, GL[1], gl)
    for y in range(12, 102):
        for x in range(5, 12):
            if u.get_at((x, y))[:3] == GL[1]:
                k = (y - x * 2) % 23; c = GL[3] if k < 2 else GL[2] if k < 5 else GL[1]                 # diagonal sheen bands
                if r.random() < .06 + (y > 80) * .12: c = (70, 64, 50)                                   # tarnish/silvering loss, worse at the bottom
                u.set_at((x, y), c)
    line(u, GL[4], (6, 20), (6, 40)); line(u, GL[4], (7, 22), (7, 28))                                    # highlight
    line(u, (20, 18, 24), (6, 52), (10, 62)); line(u, (20, 18, 24), (10, 62), (8, 70)); line(u, GL[3], (7, 52), (11, 61))  # crack
    line(u, GOLD[4], (3, 16), (12, 8)); line(u, GOLD[3], (3, 16), (3, 103)); line(u, GOLD[0], (12, 8), (12, 100))
    for y in range(20, 100, 10): u.set_at((3, y), GOLD[4]); u.set_at((4, y + 1), GOLD[0])                 # carved beads
    pygame.draw.polygon(u, GOLD[2], [(4, 10), (7, 2), (10, 1), (13, 5), (12, 9)]); u.set_at((8, 3), (170, 30, 50))   # crest
    pygame.draw.polygon(u, GOLD[1], [(3, 104), (12, 100), (13, 104), (5, 107)])                           # base foot
    s.blit(outline(u), (0, 0))
    for k in range(12): x, y = r.randrange(3, 13), r.randrange(8, 104); s.set_at((x, y), (176, 170, 160)) if s.get_at((x, y)).a and s.get_at((x, y))[:3] != OUT else None   # dust
    return s
M = mirror(); pygame.image.save(M, os.path.join(HERE, "wall_mirror.png"))
json.dump({"room": 67, "room_name": "Sorcerers Quarters", "glyphs": "',' (x18,y6), '|' (x18,y7-10), '`' (x18,y11) - a 1x6 column against the east wall (issue says 1x5; the layout has 6 cells)",
  "pieces": {"wall_mirror.png": {"frame_size": [FW, FH], "footprint_tiles": [1, 6], "anchor": {"px": [AX, AY], "desc": "bottom-centre of the column: world (18*16 + 8, (6+6)*16) = (296, 192); frame top-left (288, 85)"},
    "blocking": "all 6 column cells (as now)", "depth_sort_y": "(6+6)*16 = 192, or draw on the wall layer since it touches the east wall", "shadow_baked": False,
    "design": "tall gilt mirror seen edge-on, leaning on the east wall; tarnished glass with sheen bands, a crack, silvering loss toward the bottom, red-jewel crest"}}},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
b, TOP = baked(67)
pygame.draw.rect(b, (0, 0, 0), (0, 0, 0, 0)); b.blit(M, (18 * 16 + 8 - AX, 12 * 16 + TOP - AY))
pygame.image.save(pygame.transform.scale(b.subsurface((176, 40, 160, 190)), (480, 570)), os.path.join(HERE, "preview.png"))
copy_to_game(HERE, "wall_mirror"); print("ok")
