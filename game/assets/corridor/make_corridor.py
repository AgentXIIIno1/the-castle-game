"""corridor floor runner + wall-edge lips/rims so narrow passages read as walkable. python3 make_corridor.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import *
from art import lerp
T = 16
FLAG = [(92, 74, 58), (118, 96, 74), (140, 116, 88), (162, 136, 104), (184, 158, 122)]   # warm sandstone, lighter than the grey wall faces
GROUT = (52, 40, 34)
def floor_tile(v, horiz):
    """worn flagstone runner: 2-3 flags per tile, dark grout, lighter wear band along the walking direction, chips"""
    r = random.Random(v * 17 + (0 if horiz else 9)); s = surf(T, T)
    cuts = (r.randrange(4, 12), r.randrange(4, 12))                               # flag joints across the walking direction, staggered per half
    for y in range(T):
        for x in range(T):
            a, b = (x, y) if horiz else (y, x)                                 # a = along, b = across
            cut = cuts[0] if b < 8 else cuts[1]; flag = (0 if a < cut else 1) + (2 if b >= 8 else 0)
            l = .5 + ((flag * 37) % 5 - 2) * .03 - (b / 16) * .12 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            l += .16 * max(0, 1 - abs(b - 7.5) / 5)                           # worn path down the middle
            c = FLAG[max(0, min(4, int(l * 5)))]
            if a == 0 or a == cut or b == 0 or b == 8: c = GROUT                         # joints (b==0 = seam between rows of flags)
            elif a == 1 or a == cut + 1 or b == 1 or b == 9: c = lerp(c, FLAG[4], .35)   # rim light on each flag
            s.set_at((x, y), (*c, 255))
    for k in range(v % 3 + 1):                                                 # chips + cracks
        a, b = r.randrange(3, 14), r.randrange(3, 14); x, y = (a, b) if horiz else (b, a)
        s.set_at((x, y), (*GROUT, 255)); s.set_at((min(15, x + 1), y), (*FLAG[1], 255))
    if v == 4:                                                                 # moss in a joint
        for k in range(4): x, y = (cuts[0], 1 + k * 2) if horiz else (1 + k * 2, cuts[0]); s.set_at((x, y), (60, 84, 44, 255))
    if v == 5:                                                                 # dust drift
        for y in range(T):
            for x in range(T):
                b = y if horiz else x
                if b > 11 and BAYER[y % 4][x % 4] < 8: s.set_at((x, y), (*lerp(s.get_at((x, y))[:3], (150, 142, 128), .45), 255))
    return s
WALL = [(76, 72, 84), (100, 96, 108), (126, 120, 132)]
def lip_n():
    """16x8 short front face for a wall directly NORTH of a corridor cell: replaces the 14 px face so the corridor floor shows; lit top edge, ink bottom"""
    s = surf(16, 8); r = random.Random(3)
    for y in range(8):
        for x in range(16):
            c = WALL[1] if (x + (y // 4) * 5) % 8 else (28, 24, 34)
            if y % 4 == 3: c = (28, 24, 34)
            s.set_at((x, y), (*lerp(c, (20, 16, 28), y / 10), 255))
    line(s, (176, 170, 180), (0, 0), (15, 0)); line(s, (14, 10, 20), (0, 7), (15, 7))
    return s
def rim_s():
    """16x3 lit lip along the top edge of a wall directly SOUTH of a corridor (draw that wall top un-raised, then this on its top edge)"""
    s = surf(16, 3); line(s, (14, 10, 20), (0, 0), (15, 0)); line(s, (196, 188, 196), (0, 1), (15, 1)); line(s, (120, 114, 126), (0, 2), (15, 2)); return s
def rim_side(side):
    """3x16 thin lit wall edge replacing the 8 px side face next to a vertical corridor: ink on the corridor side, lit stone, dark toward the wall"""
    s = surf(3, 16)
    cols = [(60, 56, 66), (184, 176, 186), (14, 10, 20)] if side == "w" else [(14, 10, 20), (150, 144, 156), (48, 44, 54)]
    for y in range(16):
        for i, c in enumerate(cols): s.set_at((i, y), (*c, 255))
        if y % 6 == 5: s.set_at((1, y), (40, 36, 46, 255))
    return s
def ao():
    """16x16 x4 soft contact shadow at the wall base inside a corridor cell (N, S, W, E edge), alpha"""
    S = surf(64, 16)
    for i, side in enumerate("NSWE"):
        for y in range(16):
            for x in range(16):
                d = {"N": y, "S": 15 - y, "W": x, "E": 15 - x}[side]
                if d < 5 and BAYER[y % 4][x % 4] / 16 < 1 - d / 5: S.set_at((i * 16 + x, y), (10, 8, 18, 120 - d * 20))
    return S
def sheet(t):
    S = surf(16 * len(t), 16)
    for i, x in enumerate(t): S.blit(x, (i * 16, 0))
    return S
FH = [floor_tile(v, True) for v in range(6)]; FV = [floor_tile(v, False) for v in range(6)]
pygame.image.save(sheet(FH), os.path.join(HERE, "corridor_floor_h.png")); pygame.image.save(sheet(FV), os.path.join(HERE, "corridor_floor_v.png"))
LN, RS, RW, RE, AO = lip_n(), rim_s(), rim_side("w"), rim_side("e"), ao()
for n, im in (("corridor_lip_n.png", LN), ("corridor_rim_s.png", RS), ("corridor_rim_w.png", RW), ("corridor_rim_e.png", RE), ("corridor_ao.png", AO)): pygame.image.save(im, os.path.join(HERE, n))
RULES = """corridor cells (computed once per room, after FURN remaps):
  W(x,y) = grid cell is a wall ('#' or '='); outside the grid counts as NOT wall (it is an exit), so the void between corridor walls at the grid edge is not picked up; F(x,y) = room['walk'][y][x]
  horizontal corridor cell: F(x,y) and W(x,y-1) and W(x,y+1)                                  (1 wide)
                         or F(x,y) and W(x,y-1) and F(x,y+1) and W(x,y+2)   (+ the cell below)  (2 wide)
  vertical corridor cell:   F(x,y) and W(x-1,y) and W(x+1,y)                                  (1 wide)
                         or F(x,y) and W(x-1,y) and F(x+1,y) and W(x+2,y)   (+ the cell right)  (2 wide)
  plus: extend each run by one cell into the room (the doorway mouth) so the runner meets the room floor; skip cells holding stairs/doors/props.
  a cell that is both (corner/junction): use the _v sheet."""
json.dump({"issue": 33,
  "tiles": {"corridor_floor_h.png": {"cell": [16, 16], "variants": 6, "use": "horizontal corridor cells (walls N and S)", "rule": "variant = thash(x,y) % 6 (4 = moss in a joint, 5 = dust drift: use sparingly)"},
            "corridor_floor_v.png": {"cell": [16, 16], "variants": 6, "use": "vertical corridor cells (walls W and E) and junctions", "rule": "variant = thash(x,y) % 6"}},
  "edge_pieces": {
    "corridor_lip_n.png": {"size": [16, 8], "use": "wall cell directly NORTH of a horizontal corridor cell: draw this INSTEAD of the 14 px front face, at the face position (X, Y_raised + 16). With the raised top it fills down to the wall cell's bottom edge, so the corridor's full 16 px stays visible"},
    "corridor_rim_s.png": {"size": [16, 3], "use": "wall cell directly SOUTH of a horizontal corridor cell: draw that wall top WITHOUT the 8 px raise (it otherwise covers half the corridor), then this rim at its top edge (X, y*16 + TOP)"},
    "corridor_rim_w.png": {"size": [3, 16], "use": "west wall of a vertical corridor: replaces the 8 px side face; draw at the corridor cell's left edge (x*16, y*16 + TOP)"},
    "corridor_rim_e.png": {"size": [3, 16], "use": "east wall of a vertical corridor: replaces the 8 px side face; draw at the corridor cell's right edge (x*16 + 13, y*16 + TOP)"},
    "corridor_ao.png": {"frame_size": [16, 16], "frames": ["N", "S", "W", "E"], "use": "optional contact shadow inside the corridor cell on each side that touches a wall (replaces the bake's generic AO there)"}},
  "why": "a 1-wide corridor is currently covered by the north wall's 14 px face (6 px into the cell) plus the south wall's 8 px raised top, leaving about 2 px of floor. In vertical corridors the 8 px side faces from both walls cover the cell. The pieces above shrink those overlaps to a 3 px rim",
  "detection": RULES,
  "lighting": "no emissive or baked light; darkness/lamp rules apply unchanged (the runner is only a lighter and warmer albedo)"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---------- preview: room 10 before/after (simulated on the bake), plus room 9
def corridor_cells(R):
    g, wk = R["grid"], R["walk"]
    Wl = lambda x, y: (0 <= x < 24 and 0 <= y < 18) and g[y][x] in "#="          # the grid edge is an exit, not a wall
    F = lambda x, y: 0 <= x < 24 and 0 <= y < 18 and wk[y][x]
    H, V = set(), set()
    for y in range(18):
        for x in range(24):
            if not F(x, y): continue
            if Wl(x, y - 1) and Wl(x, y + 1): H.add((x, y))
            if Wl(x, y - 1) and F(x, y + 1) and Wl(x, y + 2): H |= {(x, y), (x, y + 1)}
            if Wl(x - 1, y) and Wl(x + 1, y): V.add((x, y))
            if Wl(x - 1, y) and F(x + 1, y) and Wl(x + 2, y): V |= {(x, y), (x + 1, y)}
    return H, V, Wl
def after(rid):
    R = rooms()[rid]; b, TOP = baked(rid); a = b.copy(); H, V, Wl = corridor_cells(R)
    for (x, y) in H - V:
        X, Y = x * 16, y * 16 + TOP
        if Wl(x, y + 1) and Wl(x, y - 1):                                      # 1-wide: unraised south wall top + rim, short north lip
            a.blit(b, (X, Y + 16), (X, Y + 16 - 8, 16, 16))                  # simulate un-raised south wall top
        a.blit(FH[(x * 7 + y * 13) % 6], (X, Y))
        if Wl(x, y - 1): a.blit(LN, (X, Y - 8)); a.blit(AO.subsurface((0, 0, 16, 16)), (X, Y))
        if Wl(x, y + 1): a.blit(RS, (X, Y + 16))
    for (x, y) in V:
        X, Y = x * 16, y * 16 + TOP
        a.blit(FV[(x * 7 + y * 13) % 6], (X, Y))
        if Wl(x - 1, y): a.blit(RW, (X, Y)); a.blit(AO.subsurface((32, 0, 16, 16)), (X + 3, Y))
        if Wl(x + 1, y): a.blit(RE, (X + 13, Y)); a.blit(AO.subsurface((48, 0, 16, 16)), (X - 3, Y))
    return b, a, H, V
out = []
for rid, crop in ((10, (0, 0, 220, 260)), (9, (120, 0, 260, 312))):
    b, a, H, V = after(rid); c = pygame.Rect(crop)
    dk = pygame.Surface(b.get_size(), pygame.SRCALPHA); dk.fill((4, 3, 10, 150))
    out.append([pygame.transform.scale(x.subsurface(c), (c.w * 2, c.h * 2)) for x in (b, a)]); print(rid, "H", sorted(H), "V", sorted(V))
Wd = sum(o[0].get_width() * 2 + 20 for o in out) + 10; Ht = max(o[0].get_height() for o in out) + 20
P = pygame.Surface((Wd, Ht)); P.fill((40, 36, 48)); x = 10
for bb, aa in out: P.blit(bb, (x, 10)); P.blit(aa, (x + bb.get_width() + 6, 10)); x += bb.get_width() * 2 + 20
pygame.image.save(P, os.path.join(HERE, "preview.png"))
Z = surf(16 * 6 + 10, 40 + 20); [Z.blit(FH[i], (i * 16, 0)) for i in range(6)]; [Z.blit(FV[i], (i * 16, 18)) for i in range(6)]
Z.blit(LN, (0, 38)); Z.blit(RS, (20, 38)); Z.blit(RW, (40, 38)); Z.blit(RE, (46, 38)); Z.blit(AO, (52, 38)) if False else None
pygame.image.save(pygame.transform.scale(Z, (Z.get_width() * 4, Z.get_height() * 4)), os.path.join(HERE, "preview_tiles.png"))
copy_to_game(HERE, "corridor"); print("ok")
