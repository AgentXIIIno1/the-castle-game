"""Fairy strips (flyer). python3 make_fairy.py"""
import os, sys, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
FW, FH, AX, AY = 32, 36, 16, 34
SKIN = [(200, 150, 120), (232, 186, 150), (250, 214, 180)]; DRESS = [(40, 96, 110), (60, 140, 150), (110, 190, 190)]; HAIR = (240, 200, 90)
WING = (190, 230, 240, 150); WING2 = (230, 250, 255, 200)
def fairy(flap=0, hover=0, zap=0, lean=0):
    s = surf(FW, FH); cx, by = 16 + lean, AY - 10 + hover
    up = [(-5, -8), (-6, -3), (-4, 2), (-6, -3)][flap % 4]
    for side in (-1, 1):
        a = (cx + side * 2, by - 14)
        pygame.draw.polygon(s, WING, [a, (cx + side * (8 + up[1] // 2), by - 14 + up[0]), (cx + side * 7, by - 10)])
        pygame.draw.polygon(s, WING, [a, (cx + side * 6, by - 7 - up[1] // 3), (cx + side * 3, by - 7)])
        line(s, WING2, a, (cx + side * (8 + up[1] // 2), by - 14 + up[0]))
    pygame.draw.polygon(s, DRESS[1], [(cx - 2, by - 13), (cx + 2, by - 13), (cx + 4, by - 4), (cx - 4, by - 4)]); line(s, DRESS[2], (cx - 1, by - 12), (cx - 3, by - 5)); line(s, DRESS[0], (cx + 4, by - 4), (cx - 4, by - 4))
    line(s, SKIN[1], (cx - 1, by - 3), (cx - 2, by)); line(s, SKIN[1], (cx + 1, by - 3), (cx + 2, by - 1))
    blob(s, cx, by - 17, 3, 3.2, SKIN)
    line(s, HAIR, (cx - 3, by - 20), (cx + 3, by - 20)); line(s, HAIR, (cx - 3, by - 19), (cx - 4, by - 15)); line(s, HAIR, (cx + 3, by - 19), (cx + 2, by - 17))
    s.set_at((cx + 1, by - 17), (30, 60, 90)); s.set_at((cx - 1, by - 17), (30, 60, 90))
    wx, wy = cx + 5 + round(zap * 2), by - 12 - round(zap * 3)                   # wand
    line(s, (230, 220, 200), (cx + 2, by - 10), (wx, wy)); s.set_at((wx, wy - 1), (255, 240, 170))
    if zap > .5:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (0, -2)): s.set_at((wx + dx, wy - 1 + dy), (255, 240, 170))
    o = outline(s)
    for y in range(FH):                                                          # keep wings translucent: remove outline around wing-only pixels? keep simple
        pass
    return o
idle = [fairy(f, hover=h) for f, h in zip(range(4), (0, -1, -1, 0))]
fly = [fairy(f, hover=h, lean=1) for f, h in zip(range(4), (0, -1, 0, 1))]
attack = [fairy(0, zap=0), fairy(1, zap=.4, hover=-1), fairy(2, zap=1, lean=1), fairy(3, zap=1, lean=1), fairy(0, zap=.2)]
rnd = random.Random(11)
def leave(t):
    f = surf(FW, FH); src = fairy(int(t * 8), hover=-round(t * 5))
    f.blit(crumble(src, max(0, t - .3) * 1.4, rnd, up=True), (0, 0)); sparkles(f, t, rnd, 16, AY - 6 - round(t * 4), n=8, cols=((255, 240, 170), (190, 230, 240), (240, 180, 220)))
    return f
death = [tint(fairy(0), flash(.6)), fairy(1, hover=-2), leave(.2), leave(.4), leave(.6), leave(.8), leave(1.0)]
build("fairy", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=90, loop=True, note="hover with fast wing flutter; fairy never moves in-game (can't be hurt)"),
    "fly": dict(frames=fly, dur=70, loop=True),
    "attack": dict(frames=attack, dur=[90, 90, 80, 120, 110], loop=False, note="wand zap sparkle on frame 2"),
    "death": dict(frames=death, dur=[100, 100, 100, 100, 110, 120, 160], loop=False, note="'leaves' when music is played: flash, rises and dissolves into sparkles; remove after last frame")},
    "Original: tiny blonde fairy, teal dress, translucent pale-blue wings (semi-alpha pixels), wand. Flyer: anchor is the ground point; body hovers ~10px above it.")
print("ok")
