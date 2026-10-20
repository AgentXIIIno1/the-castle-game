"""(Modern) Chain Mail: floor item 16x16 + 12x12 small (backpack conventions), worn hero overlay (hauberk under the
cloak: collar coif, sleeves, hem below the jerkin), armour stand for room 24 (full + empty). python3 make_chainmail.py
Set folder is art/chain_mail/ because the game's loaders already read assets/chain_mail/ (main.place_chainmail,
main.item_art per-item folder, setpiece.mail_stand). Hero overlay strips are mastered in art/hero/ (hero_chainmail_*),
like the necklace, and copied to assets/hero_overlays/chainmail/ (tools/check_assets.py GENERATED rule)."""
import os, sys, math, random, json, shutil, copy
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import copy_to_game, rooms, baked
from art import lerp
import art3
ST = [(34, 36, 46), (58, 62, 74), (88, 92, 104), (122, 126, 138), (164, 168, 180), (210, 214, 222)]   # dithered steel
LEA = [(52, 34, 22), (84, 56, 34), (120, 84, 52)]                                                   # leather edging
WD = [(40, 26, 20), (66, 44, 30), (94, 64, 42), (124, 88, 58), (156, 116, 78)]
SH = (10, 8, 16)

def mail(x, y, lit):
    """one pixel of ring mesh: rows of interlocked rings = a shifted 2x2 pattern (bright ring top, dark hole), + lighting"""
    ph = (x + (y // 2) % 2) % 2; sub = y % 2
    v = lit + (.12 if (ph == 0 and sub == 0) else -.14 if (ph == 1 and sub == 1) else 0) + (BAYER[y % 4][x % 4] / 16 - .5) * .12
    return ST[max(0, min(5, int(v * 6)))]

# ---------- floor item: folded hauberk (sleeves folded across), leather-edged collar and hem ----------
def item_art(a):
    """hauberk laid out with the sleeves folded down along the body: T silhouette, ring mesh, leather collar + hem"""
    body = [(x, y) for y in range(3, 14) for x in range(4 + (1 if y > 11 else 0), 12 - (1 if y > 11 else 0))]
    slv = [(x, y) for y in range(4, 11) for x in (1, 2, 3) if x >= 1 + max(0, (y - 4) // 3) - 1 and not (x == 1 and y < 5)] + \
          [(15 - x, y) for y in range(4, 11) for x in (1, 2, 3) if not (x == 1 and y < 5)]
    for (x, y) in body: a.set_at((x, y), mail(x, y, .7 - (x - 4) / 8 * .22 - (y - 3) / 11 * .2))
    for (x, y) in slv: a.set_at((x, y), mail(x, y, .62 if x < 8 else .44))
    for y in range(4, 11): a.set_at((4, y), lerp(a.get_at((4, y))[:3], (20, 20, 30), .5)); a.set_at((11, y), lerp(a.get_at((11, y))[:3], (20, 20, 30), .5))  # sleeve seams
    for x in range(5, 11): a.set_at((x, 11), lerp(a.get_at((x, 11))[:3], (20, 20, 30), .4))     # fold of the skirt
    pygame.draw.rect(a, LEA[1], (6, 3, 4, 2)); a.set_at((7, 4), (20, 14, 18)); a.set_at((8, 4), (20, 14, 18)); a.set_at((6, 3), LEA[2])
    for x in range(5, 11): a.set_at((x, 13), LEA[0] if x % 2 else LEA[1])                      # hem binding
    for x in list(range(1, 4)) + list(range(4, 6)) + list(range(10, 15)): 
        if a.get_at((x, 4)).a: a.set_at((x, 4), lerp(a.get_at((x, 4))[:3], ST[5], .45))        # rim light: shoulders
    for y in range(5, 11): a.set_at((1, y), lerp(a.get_at((1, y))[:3], ST[5], .3)) if a.get_at((1, y)).a else None
    a.set_at((9, 9), (120, 70, 44)); a.set_at((13, 8), (110, 64, 40))                          # rust
def floor(fn):
    art_ = surf(16, 16); fn(art_); art_ = outline(art_)
    b = art_.get_bounding_rect(); s = surf(16, 16)
    for y in range(13, 16):
        for x in range(16):
            d = ((x - 8) / (b.width / 2 + 1)) ** 2 + ((y - 14.5) / 1.6) ** 2
            if d <= 1 and (d < .5 or BAYER[y % 4][x % 4] / 16 > (d - .5) * 2): s.set_at((x, y), (*SH, 110))
    s.blit(art_, (8 - (b.x + b.width // 2), 14 - b.bottom + 1)); return s
def small(fn):
    a = surf(16, 16); fn(a); b = a.get_bounding_rect(); a = a.subsurface(b).copy()
    k = 10 / max(b.width, b.height); a = pygame.transform.scale(a, (max(1, round(b.width * k)), max(1, round(b.height * k))))
    s = surf(12, 12); s.blit(a, (6 - a.get_width() // 2, 11 - a.get_height())); return outline(s)
files = {}
def save(n, sf, d=HERE): pygame.image.save(sf, os.path.join(d, n)); files[n] = sf; return sf
FLOOR, SMALL = save("chainmail.png", floor(item_art)), save("chainmail_small.png", small(item_art))

# ---------- hero overlay: derived per frame from the hero body strips, so it follows every bob and arm pose ----------
HERO = os.path.join(ART, "hero"); FW = FH = 36
SHIRT = {(196, 186, 164), (140, 128, 116)}                 # cream shirt collar -> mail coif
ARM = {(84, 58, 40), (118, 84, 56), (50, 34, 28)}          # sleeve colours on the near arm
JERK = {(122, 80, 44), (166, 114, 64), (78, 48, 28), (44, 28, 20), (64, 38, 22)}   # jerkin / belt
TROU = {(72, 62, 66), (44, 38, 42)}                        # trousers
def overlay_frame(body):
    px = lambda x, y: tuple(body.get_at((x, y)))[:3] if 0 <= x < FW and 0 <= y < FH and body.get_at((x, y)).a else None
    m = {}
    rows = [y for y in range(FH) if sum(px(x, y) in SHIRT for x in range(6, 17)) >= 3]   # the collar top row (eye whites have < 3)
    if not rows: return surf(FW, FH)
    c0 = rows[0]; c1 = max(y for y in range(c0, c0 + 6) for x in range(6, 17) if px(x, y) in SHIRT)
    TOR = {(122, 80, 44), (166, 114, 64)}
    for y in range(c0, c1 + 1):                             # coif: the shirt collar ...
        for x in range(6, 17):
            if px(x, y) in SHIRT: m[(x, y)] = "coif"
    for y in (c0 + 1, c0 + 2):                              # ... and a mail mantle band across both shoulders (jerkin top rows)
        for x in range(4, 18):
            if px(x, y) in TOR: m[(x, y)] = "coif"
    for y in range(c0 - 1, c0 + 7):                         # near sleeve: arm colours right of the torso (right-facing native)
        for x in range(16, FW):
            if px(x, y) in ARM: m[(x, y)] = "sleeve"
    for x in range(FW):                                     # hem: 2 rows of mail below the jerkin, over the top of the trousers
        for y in range(16, 30):
            if px(x, y) in JERK and px(x, y + 1) in TROU:
                for k in (1, 2):
                    if px(x, y + k) in TROU: m[(x, y + k)] = "hem"
                break
    s = surf(FW, FH)
    for (x, y), kind in m.items():
        lit = {"coif": .74, "sleeve": .66, "hem": .6}[kind] - (x - 8) * .012
        if kind == "hem" and y == max(yy for (xx, yy), kk in m.items() if kk == "hem" and xx == x): lit -= .14      # lower ring row in shadow
        c = mail(x, y, lit)
        if kind != "hem" and px(x, y - 1) is None or (kind == "coif" and y == c0 - 1): c = lerp(c, ST[5], .35)  # rim light on top edges
        s.set_at((x, y), c)
    return s
BOBS = {"idle": 2, "walk": 4}; DUR = {"idle": [400, 400], "walk": [140, 140, 140, 140]}
OV = {}
for st, n in BOBS.items():
    body = pygame.image.load(os.path.join(HERO, f"hero_body_{st}_right.png"))
    R_ = surf(FW * n, FH); L_ = surf(FW * n, FH)
    for k in range(n):
        f = overlay_frame(body.subsurface((k * FW, 0, FW, FH)))
        for part in ("sword", "helmet"):                      # never under a sword/helmet pixel (exact over pre-composited strips too)
            for side_ in ("right", "left"):
                P = pygame.image.load(os.path.join(HERO, f"hero_{part}_{st}_{side_}.png")).subsurface((k * FW, 0, FW, FH))
                if side_ == "left": P = pygame.transform.flip(P, True, False)
                for y in range(FH):
                    for x in range(FW):
                        if P.get_at((x, y)).a: f.set_at((x, y), (0, 0, 0, 0))
        R_.blit(f, (k * FW, 0)); L_.blit(pygame.transform.flip(f, True, False), (k * FW, 0))
    for side, S in (("right", R_), ("left", L_)):
        OV[(st, side)] = save(f"hero_chainmail_{st}_{side}.png", S, HERO)
# art/hero manifest (master of the hero set) + loader copies (hero_overlays/chainmail/<idle|walk>_<side>.png, byte-identical)
man = json.load(open(os.path.join(HERO, "manifest.json")))
for st, n in BOBS.items():
    man["states"][f"chainmail_{st}"] = {"files": [f"hero_chainmail_{st}_right.png", f"hero_chainmail_{st}_left.png"], "frames": n, "fps": round(1000 / DUR[st][0], 2), "frame_durations_ms": DUR[st], "loop": True,
        "frame_anchor_offsets": [[0, 0]] * n, "note": "overlay (#28, worn Chain Mail): mail coif at the collar, mail on the near sleeve, 2 rows of hauberk hem below the jerkin; derived per frame from hero_body so it follows the bob. Draw right after the body, before the backpack straps; frame index = the hero strip's"}
man["layer_order"] = ("backpack back (art/backpack) -> body (or a pre-composited hero_<state>_swordX_helmetY strip) -> chainmail -> backpack front straps -> necklace -> sword -> helmet. "
                      "Mail pixels only replace the shirt collar, the near sleeve and the trouser tops: none of them is under a sword or helmet pixel in any frame, so drawing it over a pre-composited strip is also exact")
json.dump(man, open(os.path.join(HERO, "manifest.json"), "w"), indent=1)
copy_to_game(HERO, "hero")
d = os.path.join(GAME, "assets", "hero_overlays", "chainmail"); os.makedirs(d, exist_ok=True)
for st in BOBS:
    for side in ("right", "left"): shutil.copy(os.path.join(HERO, f"hero_chainmail_{st}_{side}.png"), os.path.join(d, f"{st}_{side}.png"))

# overlap check: mail vs sword / helmet pixels in every frame
clash = []
for st, n in BOBS.items():
    for side in ("right", "left"):
        for part in ("sword", "helmet"):
            P = pygame.image.load(os.path.join(HERO, f"hero_{part}_{st}_{side}.png"))
            for k in range(n):
                for y in range(FH):
                    for x in range(FW):
                        if OV[(st, side)].get_at((k * FW + x, y)).a and P.get_at((k * FW + x, y)).a: clash.append((st, side, part, k, x, y))
print("mail/sword/helmet overlaps:", len(clash), clash[:6])

# ---------- armour stand (room 24): full (mail on it) and empty ----------
SW, SHH = 22, 34
def stand(full):
    s = surf(SW, SHH); u = surf(SW, SHH); r = random.Random(28)
    for y in range(SHH - 4, SHH):                                            # shadow
        for x in range(SW):
            d = ((x - 11) / 10) ** 2 + ((y - (SHH - 2)) / 2) ** 2
            if d <= 1 and (d < .55 or BAYER[y % 4][x % 4] / 16 > (d - .55) * 2.2): s.set_at((x, y), (*SH, 110))
    pygame.draw.rect(u, WD[2], (4, SHH - 5, 14, 2)); line(u, WD[4], (4, SHH - 5), (17, SHH - 5)); line(u, WD[1], (4, SHH - 4), (17, SHH - 4))   # cross feet
    pygame.draw.rect(u, WD[1], (8, SHH - 3, 6, 1))
    pygame.draw.rect(u, WD[2], (10, 7, 2, SHH - 11)); line(u, WD[3], (10, 7), (10, SHH - 5))             # post
    pygame.draw.rect(u, WD[2], (3, 8, 16, 2)); line(u, WD[4], (3, 8), (18, 8)); line(u, WD[0], (3, 9), (18, 9))   # shoulder bar
    pygame.draw.ellipse(u, WD[3], (8, 2, 6, 6)); u.set_at((9, 3), WD[4]); u.set_at((12, 6), WD[1])     # knob 'head'
    if full:
        for y in range(9, 26):                                               # hauberk body: broad shoulders, waist, flared skirt
            w = 6 if y < 11 else 5 if y < 18 else 6 + (y - 18) // 3
            for x in range(11 - w, 11 + w):
                if y == 25 and (x + 1) % 3 == 0: continue                    # ragged ring edge
                u.set_at((x, y), mail(x, y, .7 - (x - 4) / 14 * .3 - (y - 9) / 16 * .15))
        for x0 in (1, 18):                                                   # sleeves hanging down, split from the body
            for y in range(10, 21):
                for x in range(x0 + (1 if (x0 == 1 and y > 14) else 0), x0 + 3 - (1 if (x0 == 18 and y > 14) else 0)):
                    u.set_at((x, y), mail(x, y, .64 if x0 == 1 else .44))
        pygame.draw.ellipse(u, (20, 14, 18), (8, 9, 6, 3)); line(u, LEA[1], (8, 9), (13, 9))           # neck opening
        for x in range(6, 16): u.set_at((x, 24), LEA[0] if x % 3 else LEA[1])                          # leather hem
        for x in range(1, 21):
            if u.get_at((x, 10)).a and x not in range(8, 14): u.set_at((x, 10), lerp(u.get_at((x, 10))[:3], ST[5], .45))              # rim light
        for y in range(10, 21): u.set_at((1, y), lerp(u.get_at((1, y))[:3], ST[5], .35))
        u.set_at((14, 21), (120, 70, 44)); u.set_at((7, 16), (110, 64, 40))
    else:                                                                     # empty: dusty pale outline where the mail hung, a cobweb
        for x in range(5, 17): u.set_at((x, 11), (92, 70, 54))
        for k in range(5): u.set_at((15 + k // 2, 3 + k), (200, 200, 210, 150)); u.set_at((14 + k, 9 - k // 2), (200, 200, 210, 120))
    s.blit(outline(u), (0, 0)); return s
STAND = save("armour_stand.png", stand(True)); STAND0 = save("armour_stand_empty.png", stand(False))

# ---------- placement (room 24) + BFS ----------
R = rooms(); room = R[24]; g = room["grid"]
CELL = (15, 2)                                               # north wall between the x12 and x17 posts, clear of the red banner at x19; demon (5,9), Magic Wand (3,8)
assert room["walk"][CELL[1]][CELL[0]] and not art3.is_post(g, CELL[0], CELL[1] - 1) and g[CELL[1] - 1][CELL[0]] == "#"
X, Y = CELL[0] * 16 + 8, CELL[1] * 16 + 16; TL = (X - SW // 2, Y - SHH + 1)
def bfs(walk, st):
    seen = {st}; dq = deque([st])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 24 and 0 <= n[1] < 18 and n not in seen and walk[n[1]][n[0]]: seen.add(n); dq.append(n)
    return seen
w2 = [row[:] for row in room["walk"]]; w2[CELL[1]][CELL[0]] = False
start = (4, 0); before = bfs(room["walk"], start); after = bfs(w2, start)
assert before - after == {CELL}, before - after                # blocking it would cut nothing off
edge = [(x, y) for y in range(18) for x in range(24) if room["walk"][y][x] and (x in (0, 23) or y in (0, 17))]
assert all(e in after for e in edge if e in before) and (3, 8) in after and (5, 9) in after
mdist = abs(CELL[0] - 5) + abs(CELL[1] - 9)
M = {"issue": 28, "mode": "Modern only",
 "item": {"floor": "chainmail.png", "small": "chainmail_small.png", "floor_frame": [16, 16], "floor_anchor": [8, 15], "shadow_baked": True,
          "small_frame": [12, 12], "small_anchor": [6, 11], "small_shadow_baked": False, "treasure": False, "name": "Chain Mail",
          "content": "folded knight's hauberk: dithered steel ring mesh, sleeves folded across, leather-lined collar and hem binding, rim light, two rust spots"},
 "item_cell": list(CELL),
 "stand": {"file": "armour_stand_empty.png", "topleft": list(TL), "sort_y": Y, "blocking": False,
           "note": "setpiece.mail_stand() reads this. It is the EMPTY stand so it is right with today's code: the Chain Mail item (on item_cell, the same cell) is drawn in front of it while it lies there, and the stand stays empty after GET"},
 "stand_full": {"file": "armour_stand.png", "topleft": list(TL), "sort_y": Y,
                "state_switch": "draw stand_full INSTEAD of stand while a Chain Mail item is in room 24's items on item_cell, and skip that item's floor sprite (like the statue necklace); after GET (or if it is dropped elsewhere) draw the empty stand. Dropping it back on item_cell may restore the full stand"},
 "stand_frame": [SW, SHH], "stand_anchor": [SW // 2, SHH - 1], "stand_world_anchor": [X, Y],
 "placement_check": {"cell": list(CELL), "wall_above": [CELL[0], CELL[1] - 1], "post_cells_room24": [[x, y] for y in range(18) for x in range(24) if art3.is_post(g, x, y)],
                     "bfs": "blocking the cell would remove only that cell from the reachable set: every exit (N x4-5, S x10-13, E y7-10), the Magic Wand (3,8) and the demon (5,9) stay connected", "manhattan_to_demon": mdist,
                     "get_reach": "GET works from any adjacent cell (main.touching_prop / 1-cell rule), so the stand cell may be made blocking"},
 "hero_overlay": {"frame_size": [36, 36], "anchor": {"px": [12, 33], "px_left": [24, 33]}, "same_as": "art/hero strips (right native, left = mirror)",
                  "files_master": {st: [f"art/hero/hero_chainmail_{st}_right.png", f"art/hero/hero_chainmail_{st}_left.png"] for st in BOBS},
                  "loader_copies": "game/assets/hero_overlays/chainmail/<idle|walk>_<right|left>.png (byte-identical to the art/hero masters, see tools/check_assets.py GENERATED)",
                  "states": {st: {"frames": n, "frame_durations_ms": DUR[st]} for st, n in BOBS.items()},
                  "draw_order": "body -> chainmail -> backpack front straps -> necklace -> sword -> helmet (backpack back layer stays behind the body). main.hero_overlays() already returns ['chainmail', 'backpack', 'necklace'] in that order",
                  "sword_helmet_overlap_pixels": len(clash)}}
json.dump(M, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
copy_to_game(HERE, "chain_mail")

# ---------- previews ----------
BP = os.path.join(ART, "backpack")
def L(n, d=HERO): return pygame.image.load(os.path.join(d, n))
cols = []
for st, n in BOBS.items():
    for side in ("right", "left"):
        for sw in (0, 1):
            for hm in (0, 1):
                for mk, bp, nk in ((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 1, 1)):
                    fr = []
                    for k in range(n):
                        f = surf(FW, FH); c = (k * FW, 0, FW, FH)
                        if bp: f.blit(L(f"hero_backpack_back_{st}_{side}.png", BP), (0, 0), c)
                        f.blit(L(f"hero_body_{st}_{side}.png"), (0, 0), c)
                        if mk: f.blit(OV[(st, side)], (0, 0), c)
                        if bp: f.blit(L(f"hero_backpack_front_{st}_{side}.png", BP), (0, 0), c)
                        if nk: f.blit(L(f"hero_necklace_{st}_{side}.png"), (0, 0), c)
                        if sw: f.blit(L(f"hero_sword_{st}_{side}.png"), (0, 0), c)
                        if hm: f.blit(L(f"hero_helmet_{st}_{side}.png"), (0, 0), c)
                        fr.append(f)
                    cols.append(((st, side, sw, hm, mk, bp, nk), fr))
walk = [c for c in cols if c[0][0] == "walk"]; per = len(walk) // 2
Z = pygame.Surface((per * 38 + 4, 4 * 38 + 8)); Z.fill((96, 70, 52)); ci = {"right": 0, "left": 0}
for key, fr in walk:
    side = key[1]; c = ci[side]; ci[side] += 1; yo = 2 if side == "right" else 2 + 2 * 38 + 4
    Z.blit(fr[0], (2 + c * 38, yo)); Z.blit(fr[1], (2 + c * 38, yo + 38))
pygame.image.save(pygame.transform.scale(Z, (Z.get_width() * 3, Z.get_height() * 3)), os.path.join(HERE, "preview_overlays.png"))
from PIL import Image
gf = []
full = [c for c in cols if c[0][1] == "right" and c[0][2:] == (1, 1, 1, 1, 1)]
for key, fr in full:
    for f in fr * (2 if key[0] == "walk" else 1):
        Zs = pygame.Surface((36, 36)); Zs.fill((96, 70, 52)); Zs.blit(f, (0, 0)); Zs = pygame.transform.scale(Zs, (216, 216))
        gf.append(Image.frombytes("RGB", Zs.get_size(), pygame.image.tobytes(Zs, "RGB")))
gf[0].save(os.path.join(HERE, "preview_overlays.gif"), save_all=True, append_images=gf[1:], duration=160, loop=0)
# item + stand sheet, and the stand in baked room 24 (full / taken)
Q = pygame.Surface((120, 44)); Q.fill((96, 70, 52)); Q.blit(FLOOR, (4, 14)); Q.blit(SMALL, (24, 18)); Q.blit(STAND, (44, 4)); Q.blit(STAND0, (72, 4))
pygame.image.save(pygame.transform.scale(Q, (720, 264)), os.path.join(HERE, "preview.png"))
b, TOP = baked(24); full_ = b.copy(); emp = b.copy()
full_.blit(STAND, (TL[0], TL[1] + TOP)); emp.blit(STAND0, (TL[0], TL[1] + TOP))
crop = pygame.Rect(9 * 16, 0, 13 * 16, 8 * 16 + TOP)
P = pygame.Surface((crop.w * 3 * 2 + 30, crop.h * 3 + 30)); P.fill((40, 36, 48)); font = pygame.font.Font(None, 20)
for i, (nm, t) in enumerate((("room 24: armour stand with the mail (Chain Mail still there)", full_), ("after GET: empty stand", emp))):
    P.blit(font.render(nm, True, (230, 220, 200)), (10 + i * (crop.w * 3 + 10), 6)); P.blit(pygame.transform.scale(t.subsurface(crop), (crop.w * 3, crop.h * 3)), (10 + i * (crop.w * 3 + 10), 24))
pygame.image.save(P, os.path.join(HERE, "preview_room24.png"))
print("ok", CELL, TL, Y, mdist)
