"""Bat strips (flyer). python3 make_bat.py"""
import os, sys, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
FW, FH, AX, AY = 32, 32, 16, 30          # anchor = ground point under the bat; body hovers ~14px up
B = [(28, 18, 34), (52, 34, 62), (80, 56, 92), (112, 84, 124)]; MEM = [(44, 24, 52), (70, 40, 78)]
def bat(flap=0, hover=0, dive=0, mouth=False, dead=False):
    s = surf(FW, FH); cx, cy = 16 + round(dive * 4), AY - 14 + hover + round(dive * 5)
    if dead: cy = AY - 3
    span = [12, 9, 4, 9][flap % 4] if not dead else 11; tipy = [-6, 0, 4, -2][flap % 4] if not dead else 1
    for side in (-1, 1):
        tip = (cx + side * span, cy + tipy); mid = (cx + side * span * .55, cy + tipy * .4 + 4)
        pts = [(cx + side * 2, cy - 2), (cx + side * span * .5, cy + tipy * .5 - 2), tip, (cx + side * span * .8, cy + 4 + tipy * .3), mid, (cx + side * span * .3, cy + 5), (cx + side * 2, cy + 3)]
        pygame.draw.polygon(s, MEM[1], pts); line(s, B[3], pts[0], tip); line(s, MEM[0], tip, mid)
    blob(s, cx, cy, 3.5, 4, B)
    for side in (-1, 1): pygame.draw.polygon(s, B[2], [(cx + side * 1, cy - 3), (cx + side * 3, cy - 7), (cx + side * 3, cy - 2)])
    if not dead:
        s.set_at((cx - 1, cy - 1), (255, 70, 50)); s.set_at((cx + 1, cy - 1), (255, 70, 50))
        if mouth: pygame.draw.rect(s, INK, (cx - 1, cy + 1, 3, 2)); s.set_at((cx - 1, cy + 2), (240, 236, 220)); s.set_at((cx + 1, cy + 2), (240, 236, 220))
        else: s.set_at((cx - 1, cy + 2), (240, 236, 220)); s.set_at((cx + 1, cy + 2), (240, 236, 220))
    else:
        for d in (-1, 1): s.set_at((cx - 1 + d * 0, cy - 1), INK); s.set_at((cx + 1, cy - 1), INK)
    return outline(s)
fly = [bat(f, hover=h) for f, h in zip(range(4), (0, 1, 1, 0))]
idle = [bat(f, hover=h) for f, h in zip(range(4), (-1, 0, 1, 0))]
attack = [bat(0, hover=-2), bat(1, hover=-3, dive=-.5), bat(2, dive=1, mouth=True), bat(3, dive=1.3, mouth=True), bat(0, dive=.3)]
rnd = random.Random(2); dead = bat(dead=True)
death = [tint(bat(1), flash(.9)), tint(bat(2, hover=-1), flash(.4)), bat(2, hover=4), bat(3, hover=9), dead]
death += death_tail(dead, rnd, 16, AY - 1, big=.7)
build("bat", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=110, loop=True, note="hover in place (bats never land); body bob"),
    "fly": dict(frames=fly, dur=80, loop=True, note="flap cycle used while moving"),
    "attack": dict(frames=attack, dur=[80, 90, 70, 110, 100], loop=False, note="rise, dive-bite on frame 2 = hit frame"),
    "death": dict(frames=death, dur=[90, 70, 70, 70, 170, 170, 90, 90, 100, 130], loop=False, note="flash, drops to ground, crumbles; remove after last frame")},
    "Original: purple-black bat with red eyes and fangs. Flyer: anchor is the ground point (bottom-centre); body drawn ~14px above it, so the game should not add its own hover offset.")
print("ok")
