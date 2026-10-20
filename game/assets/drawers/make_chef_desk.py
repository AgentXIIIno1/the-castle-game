"""room 10 Chef's Quarters: the chef's small desk (scrubbed pine, recipe lectern, mortar & pestle, ladle, candle stub,
string of garlic), 3 drawer states like the other desks; the Wine Flask ('on desk', cell (7,10)) shows in the open drawer.
Adds pieces['chef_desk'] to manifest.json (other pieces untouched). python3 make_chef_desk.py"""
import os, sys, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import rooms, copy_to_game
from art import lerp
import art3, setpiece
W, H, AX, AY = 68, 50, 34, 47          # footprint 4x2 (x6-9, y10-11): bottom-centre world (6*16+32, 12*16) = (128, 192)
PINE = [(70, 50, 34), (112, 84, 54), (150, 118, 76), (186, 156, 106), (214, 190, 142)]
IRON = [(30, 28, 36), (64, 62, 72), (110, 108, 118)]
SH = (10, 8, 16)
def desk(state):
    s = surf(W, H); u = surf(W, H)
    for y in range(H - 6, H):                                         # baked contact shadow
        for x in range(W):
            d = ((x - AX) / 33) ** 2 + ((y - (H - 3)) / 3) ** 2
            if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.4): s.set_at((x, y), (*SH, 110))
    x0, x1, ty0, ty1 = 3, 64, 17, 33                                  # top plane (16 px deep), front face to the legs
    for y in range(ty0, ty1):
        for x in range(x0, x1):
            plank = (y - ty0) // 4; lit = .66 - (x - x0) / 61 * .2 + (BAYER[y % 4][x % 4] / 16 - .5) * .1 + (plank % 2) * .04
            u.set_at((x, y), PINE[max(0, min(4, int(lit * 5)))])
        if (y - ty0) % 4 == 3: line(u, PINE[1], (x0, y), (x1 - 1, y))  # board joints
    for x in range(x0, x1, 9): u.set_at((x + 4, ty0 + 6), PINE[1])    # knife scars (a chef's desk is also a board)
    line(u, PINE[4], (x0, ty0), (x1 - 1, ty0))
    pygame.draw.rect(u, PINE[1], (x0, ty1, x1 - x0, 7)); line(u, PINE[2], (x0, ty1), (x1 - 1, ty1))     # apron
    for lx in (x0, x1 - 3):                                           # legs
        pygame.draw.rect(u, PINE[1], (lx, ty1 + 7, 3, AY - ty1 - 7)); u.set_at((lx, ty1 + 7), PINE[3])
    dx0 = 30                                                          # drawer in the apron
    if state == "closed":
        pygame.draw.rect(u, PINE[2], (dx0, ty1 + 1, 16, 5)); pygame.draw.rect(u, PINE[0], (dx0, ty1 + 1, 16, 5), 1); u.set_at((dx0 + 8, ty1 + 3), IRON[2])
    else:                                                             # pulled out toward the viewer: box below the apron
        pygame.draw.rect(u, PINE[0], (dx0 - 1, ty1 + 2, 18, 4)); pygame.draw.rect(u, PINE[2], (dx0 - 1, ty1 + 6, 18, 6))
        pygame.draw.rect(u, (40, 28, 22), (dx0, ty1 + 2, 16, 4)); u.set_at((dx0 + 8, ty1 + 9), IRON[2])
        if state == "open_item":                                      # the Wine Flask lying in it
            pygame.draw.ellipse(u, (120, 60, 150), (dx0 + 3, ty1 + 2, 9, 4)); u.set_at((dx0 + 5, ty1 + 2), (200, 150, 230))
            line(u, (226, 214, 190), (dx0 + 12, ty1 + 3), (dx0 + 14, ty1 + 3))
    # --- the chef's things on top ---
    pygame.draw.polygon(u, PINE[1], [(8, 26), (24, 26), (22, 9), (10, 9)])                     # sloped recipe lectern
    pygame.draw.polygon(u, (226, 212, 176), [(10, 24), (16, 24), (16, 11), (11, 11)]); pygame.draw.polygon(u, (206, 192, 156), [(16, 24), (22, 24), (21, 11), (16, 11)])
    for yy in range(13, 23, 2): line(u, (120, 96, 70), (11, yy), (15, yy)); line(u, (120, 96, 70), (17, yy), (20, yy))
    line(u, (160, 40, 40), (16, 11), (16, 26))                                                  # ribbon bookmark
    pygame.draw.ellipse(u, (120, 116, 120), (36, 18, 10, 7)); pygame.draw.ellipse(u, (60, 56, 64), (38, 19, 6, 3))   # stone mortar
    line(u, (190, 186, 180), (41, 20), (45, 13)); u.set_at((45, 12), (220, 216, 210))          # pestle
    line(u, IRON[2], (50, 28), (58, 21)); pygame.draw.ellipse(u, IRON[1], (56, 18, 5, 4))      # ladle
    pygame.draw.rect(u, (220, 210, 180), (28, 18, 3, 5)); u.set_at((29, 17), (255, 210, 120)); u.set_at((29, 16), (255, 240, 180))   # candle stub
    pygame.draw.ellipse(u, IRON[1], (26, 22, 7, 3))
    for k, gx in enumerate((52, 56, 60)):                                                        # garlic string hanging off the corner
        pygame.draw.circle(u, (230, 224, 206), (gx + (k % 2), 34 + k * 2), 2); u.set_at((gx, 33 + k * 2), (180, 170, 140))
    line(u, (150, 130, 90), (51, 31), (61, 38))
    s.blit(outline(u), (-1, -1)); return s
STATES = {"closed": "chef_desk_closed.png", "open_item": "chef_desk_open_item.png", "open_empty": "chef_desk_open_empty.png"}
IM = {}
for st, f in STATES.items(): IM[st] = desk(st); pygame.image.save(IM[st], os.path.join(HERE, f))
p = os.path.join(HERE, "manifest.json"); m = json.load(open(p))
m["pieces"]["chef_desk"] = {"room": 10, "glyph": "@", "footprint_tiles": [4, 2], "footprint_cells_0based": "x 6-9, y 10-11",
  "item": "WINE_FLASK (Wine Flask), row 11 col 8 1-based, 'on desk'", "states": STATES, "frame_size": [W, H],
  "anchor": {"px": [AX, AY], "desc": "bottom-centre of the footprint: world (6*16 + 32, (10+2)*16) = (128, 192) in room 10"},
  "depth_sort_y": "(10+2)*16", "blocking": "all footprint cells (unchanged: '@' is solid)", "shadow_baked": True,
  "state_rules": "closed until the player LOOKs/searches the desk; then open_item while the item is there; open_empty after GET",
  "issue": 15, "content": "chef's small desk: scrubbed pine with knife scars, sloped recipe lectern with an open recipe book, stone mortar and pestle, ladle, candle stub, a string of garlic; drawer in the apron"}
json.dump(m, open(p, "w"), indent=2 if open(p).read(2) != "{\"" else None)
copy_to_game(HERE, "drawers")
# preview room 10: before (procedural desk) / after (chef desk, each state)
R = rooms(); room = R[10]
def bk(art_state=None):
    r = copy.deepcopy(room)
    if art_state: setpiece.DESK[10] = "chef_desk"; setpiece._c.clear() if hasattr(setpiece, "_c") else None
    try: raw, top = art3.bake_room(10, r)
    finally: setpiece.DESK.pop(10, None)
    raw = raw.copy(); raw.set_colorkey((255, 0, 255)); b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0))
    if art_state: b.blit(IM[art_state], (128 - AX, 192 - AY + top))
    return b
font = pygame.font.Font(None, 18); crop = pygame.Rect(0, 0, 13 * 16, 15 * 16 + 24)
P = pygame.Surface((4 * (crop.w * 2 + 10) + 10, crop.h * 2 + 34)); P.fill((40, 36, 48))
for i, (lab, st) in enumerate((("before", None), ("AFTER closed", "closed"), ("open + Wine Flask", "open_item"), ("open, empty", "open_empty"))):
    x0 = 10 + i * (crop.w * 2 + 10); P.blit(font.render(f"#15 room 10 - {lab}", True, (230, 220, 200)), (x0, 6))
    P.blit(pygame.transform.scale(bk(st).subsurface(crop), (crop.w * 2, crop.h * 2)), (x0, 24))
pygame.image.save(P, os.path.join(HERE, "preview_chef_desk.png")); print("ok")
