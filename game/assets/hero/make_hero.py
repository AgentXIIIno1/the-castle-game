"""Hero cleanup: better face, reshaped flowing cloak, 4-frame walk, separate sword/helmet layers. python3 make_hero.py
Game uses side view only (right native, flipped for left), hence right+left strips."""
import os, sys, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art3 import HERO, HERO_PAL, from_map
P = HERO_PAL
FW, FH = 36, 36; OX, OY = 1, 1                # body map placed at (1,1) like art.outline does
AX, AY = 12, 33                               # bottom-centre of feet
BASE = from_map(HERO, HERO_PAL); BW, BH = BASE.get_size()
CL = [(40, 26, 22), (62, 40, 30), (88, 60, 40), (118, 84, 56)]
def body(bob=0, lx=0, rx=0, ly=0, ry=0):
    s = surf(FW, FH)
    b = BASE.copy()
    for y in range(12, BH):                    # strip old cloak (left of torso)
        for x in range(0, 6 if y < 28 else 5):
            b.set_at((x, y), (0, 0, 0, 0))
    # face detail (facing right): eye whites + pupils, brows, nose shade, mouth
    for (x, y, c) in ((9, 7, P['w']), (10, 7, P['e']), (12, 7, P['w']), (13, 7, P['e']),
                      (9, 6, P['H']), (10, 6, P['H']), (12, 6, P['H']), (13, 6, P['H']),
                      (12, 8, P['S']), (13, 9, P['S']), (11, 10, (150, 70, 60)), (12, 10, (150, 70, 60)), (8, 8, (214, 130, 110))):
        b.set_at((x, y), c)
    top = b.subsurface((0, 0, BW, 27)); ll = b.subsurface((0, 27, 11, BH - 27)); rl = b.subsurface((11, 27, BW - 11, BH - 27))
    return b, top, ll, rl
def cloak(s, bob, sway):
    """flowing tapered cloak behind the body: shoulder at (6,12), hem flares back with sway"""
    x0, y0 = OX + 6, OY + 12 + bob
    pts = [(x0 + 1, y0), (x0 - 3, y0 + 4), (x0 - 5 - sway, y0 + 12), (x0 - 7 - sway * 2, y0 + 19), (x0 - 3 - sway, y0 + 18), (x0 - 1, y0 + 20), (x0 + 2, y0 + 16)]
    pygame.draw.polygon(s, CL[1], pts)
    line(s, CL[3], (x0, y0 + 1), (x0 - 4, y0 + 5)); line(s, CL[2], (x0 - 4, y0 + 5), (x0 - 6 - sway, y0 + 14))
    line(s, CL[0], (x0 - 1, y0 + 6), (x0 - 2 - sway, y0 + 17)); line(s, CL[0], (x0 - 7 - sway * 2, y0 + 19), (x0 - 1, y0 + 20))
    for i in range(3): s.set_at((x0 - 4 - sway - i, y0 + 15 + i), CL[2])
STEPS = {"idle": [(0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1)], "walk": [(0, 1, -1, 0, 0, 1), (1, 0, 0, -1, -1, 2), (0, -1, 1, 0, 0, 1), (1, 0, 0, -1, -1, 0)]}
def frame(bob, lx, rx, ly, ry, sway, breathe=0):
    s = surf(FW, FH); b, top, ll, rl = body()
    cloak(s, bob, sway)
    s.blit(ll, (OX + lx, OY + 27 + ly)); s.blit(rl, (OX + 11 + rx, OY + 27 + ry)); s.blit(top, (OX, OY + bob - breathe))
    return outline(s)
def sword_layer(bob):
    s = surf(FW, FH); hx, hy = OX + 19, OY + 17 + bob
    line(s, INK, (hx - 2, hy - 1), (hx + 3, hy + 2), 3); line(s, P['g'], (hx - 2, hy - 1), (hx + 3, hy + 2))
    for i in range(12):
        x, y = hx + 2 + i * .62, hy + 2 + i
        line(s, INK, (x - 1, y), (x + 2, y)); s.set_at((int(x), int(y)), (232, 236, 244)); s.set_at((int(x) + 1, int(y)), (138, 146, 160))
    s.set_at((hx + 10, hy + 14), INK); s.set_at((hx + 3, hy + 3), (255, 255, 255))
    return s
GM = [(30, 32, 40), (52, 54, 64), (76, 78, 88), (104, 106, 114), (146, 140, 132)]   # gunmetal dark..rim highlight
HAIRC = [P['H'], P['h'], P['y']]
def helmet_layer(bob):
    """worn iron nasal helm seated on the skull (frame rows 0-6 at bob 0), eyes/brows (rows 7-8) left clear."""
    s = surf(FW, FH); oy = OY - 1 + bob
    spans = {0: (10, 14), 1: (8, 16), 2: (7, 17), 3: (6, 18), 4: (5, 19), 5: (5, 19)}   # dome rows, follows skull
    for y, (x0, x1) in spans.items():
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, x1 - x0)                                   # lit from top-left
            v = .75 - u * .55 - y * .07 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            s.set_at((x, oy + y), GM[max(0, min(3, int(v * 4)))])
    for x in range(5, 20): s.set_at((x, oy + 5), GM[1] if x % 3 else GM[3])  # rim band w/ rivets
    for x in range(6, 19): s.set_at((x, oy + 4), GM[4] if 7 <= x <= 15 else GM[3])   # rim highlight
    line(s, GM[4], (9, oy + 1), (12, oy + 1)); s.set_at((8, oy + 2), GM[3])   # top glint
    line(s, GM[0], (14, oy + 2), (15, oy + 3)); s.set_at((14, oy + 3), GM[3])   # dent / scratch
    for x in (8, 12, 16): s.set_at((x, oy + 5), GM[4])                      # rivets
    for (x, y, c) in ((4, 6, 1), (4, 7, 0), (3, 8, 1), (4, 8, 0), (3, 9, 0), (5, 7, 2), (19, 6, 1), (20, 7, 0), (19, 7, 1), (20, 8, 0)):  # messy hair tufts below rim
        s.set_at((x, oy + y), HAIRC[c])
    o = outline(s)
    for x in range(7, 18): o.set_at((x, oy + 6), (0, 0, 0, 0)) if o.get_at((x, oy + 6))[:3] == OUT else None   # keep brow row clear
    for x in range(7, 18): o.set_at((x, oy + 6), GM[0])          # thin dark rim underside (1px) instead of thick ink over brows
    s2 = o; s2.set_at((12, oy + 7), GM[2]); s2.set_at((12, oy + 8), GM[1])   # thin nose guard, no outline (eyes at x10-11 / 13-14 stay clear)
    return s2
def comp(*layers):
    s = surf(FW, FH)
    for l in layers: s.blit(l, (0, 0))
    return s
states = {}
for st, seq in STEPS.items():
    dur = 400 if st == "idle" else 140
    bodies = [frame(*p) for p in seq]; bobs = [p[0] for p in seq]
    states[f"body_{st}"] = dict(frames=bodies, dur=dur, loop=True, note="base layer (no sword/helmet)")
    states[f"sword_{st}"] = dict(frames=[sword_layer(b) for b in bobs], dur=dur, loop=True, note="overlay layer: draw after body, same anchor")
    states[f"helmet_{st}"] = dict(frames=[helmet_layer(b) for b in bobs], dur=dur, loop=True, note="overlay layer: draw after body (and sword), same anchor")
    for sw in (0, 1):
        for hm in (0, 1):
            fr = [comp(bodies[i], *( [sword_layer(bobs[i])] if sw else []), *([helmet_layer(bobs[i])] if hm else [])) for i in range(len(seq))]
            states[f"{st}_sword{sw}_helmet{hm}"] = dict(frames=fr, dur=dur, loop=True, note="pre-composited variant = main.py heroes[(sword, helmet)]")
build("hero", HERE, FW, FH, (AX, AY), states,
      "Cleanup of art3.HERO: eye whites+pupils, brows, nose shading, mouth, cheek; old blocky left cloak replaced with a tapered flowing cloak that sways with the walk; 4-frame walk (legs alternate, body bobs) + 2-frame idle breathe. Sword and helmet are separate overlay layers or use the pre-composited *_swordX_helmetY strips. Side view only, matching main.py (right native; left = mirror). Tint/hurt flash stays game-side.")
print("ok")
