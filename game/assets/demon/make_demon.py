"""Demon sprite strips. python3 make_demon.py"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
FW, FH, AX, AY = 64, 56, 32, 54
SK = [(70, 18, 22), (112, 30, 30), (150, 48, 40), (196, 84, 60)]
WG = [(36, 14, 24), (60, 22, 34), (88, 34, 44)]
HORN = (222, 206, 170); EYE = (255, 210, 80)
def demon(bob=0, step=0, wing=0, atk=0, lean=0):
    s = surf(FW, FH); cx = AX + lean; by = AY + bob
    # wings (behind), spread angle by wing
    for side in (-1, 1):
        sx, sy = cx + side * 6, by - 30
        tip = (sx + side * (14 + wing * 2), sy - 8 + wing * 4)
        pts = [(sx, sy), tip, (sx + side * (13 + wing), sy + 6 + wing), (sx + side * 8, sy + 3 + wing), (sx + side * 5, sy + 9)]
        pygame.draw.polygon(s, WG[1], pts); line(s, WG[2], (sx, sy), tip); line(s, WG[0], (sx + side * 5, sy + 9), (sx + side * 8, sy + 3 + wing))
    # tail
    for i in range(12):
        u = i / 11; line(s, SK[1], (cx - 4 - u * 10, by - 8 - math.sin(u * 3) * 4), (cx - 5 - u * 11, by - 8 - math.sin(u * 3 + .3) * 4), 2)
    pygame.draw.polygon(s, SK[2], [(cx - 16, by - 14), (cx - 19, by - 10), (cx - 14, by - 11)])
    # legs (goat-ish) with step
    for side, ph in ((-1, step), (1, -step)):
        lx = cx + side * 4
        blob(s, lx + ph, by - 7, 3, 5, SK); pygame.draw.rect(s, (40, 22, 22), (lx + ph - 2, by - 2, 5, 2))
    blob(s, cx, by - 19, 9, 10, SK)                     # torso
    line(s, SK[0], (cx - 3, by - 16), (cx + 3, by - 16)); line(s, SK[3], (cx - 5, by - 25), (cx - 1, by - 26))
    # arms; front (right) arm claws forward on attack
    blob(s, cx - 10, by - 20, 3, 6, SK)
    ax, ay = round(cx + 10 + atk * 7), round(by - 21 - atk * 3)
    blob(s, cx + 9 + atk * 3, by - 21 - atk, 3, 5, SK); blob(s, ax, ay, 2.5, 2.5, SK)
    for k in range(3): line(s, HORN, (ax + 1, ay - 1 + k), (ax + 3 + atk, ay - 2 + k * 2))
    # head
    hx, hy = round(cx + 1 + atk), round(by - 34)
    blob(s, hx, hy, 6, 6, SK)
    for side in (-1, 1):
        line(s, HORN, (hx + side * 3, hy - 4), (hx + side * 6, hy - 10), 2); s.set_at((hx + side * 7, hy - 11), HORN)
    s.set_at((hx + 1, hy - 1), EYE); s.set_at((hx + 4, hy - 1), EYE); line(s, INK, (hx, hy - 2), (hx + 2, hy - 1)); line(s, INK, (hx + 3, hy - 1), (hx + 5, hy - 2))
    line(s, INK, (hx + 1, hy + 2), (hx + 5, hy + 2)); s.set_at((hx + 2, hy + 3), HORN); s.set_at((hx + 4, hy + 3), HORN)
    if atk > .5: pygame.draw.rect(s, INK, (hx + 1, hy + 2, 5, 2)); s.set_at((hx + 2, hy + 2), HORN); s.set_at((hx + 4, hy + 2), HORN)
    return outline(s)
def rot(f, ang, dx=0):
    big = surf(FW * 2, FH * 2); big.blit(f, (FW // 2, FH // 2)); r = pygame.transform.rotate(big, ang)
    o = surf(FW, FH); o.blit(r, (r.get_width() // 2 - FW // 2 + 0 - (r.get_width() - FW * 2) // 2 * 0 - FW // 2 + dx, r.get_height() // 2 - FH // 2 - FH // 2 + (8 if abs(ang) > 45 else 3)))
    return o
idle = [demon(bob=b, wing=w) for b, w in ((0, 0), (-1, 1), (-1, 2), (0, 1))]
walk = [demon(bob=b, step=st, wing=1, lean=1) for b, st in ((0, -2), (-1, 0), (0, 2), (-1, 0))]
attack = [demon(atk=0, wing=0, lean=-1), demon(atk=.2, wing=3, lean=-2), demon(atk=1, wing=2, lean=2), demon(atk=1, wing=1, lean=2), demon(atk=.3, wing=0)]
rnd = random.Random(4)
def crop(f): return f.subsurface(f.get_bounding_rect()).copy()
base = demon()
dead = surf(FW, FH); fallen = pygame.transform.rotate(crop(demon(wing=-1)), 90); dead.blit(fallen, (FW // 2 - fallen.get_width() // 2 + 2, AY + 2 - fallen.get_height()))
death = [tint(base, flash(.9)), tint(demon(lean=-2, wing=3), flash(.4)), demon(lean=-3, bob=1, wing=3), demon(lean=2, bob=3, wing=-1)]
mid = surf(FW, FH); m = pygame.transform.rotate(crop(demon(wing=-1, bob=2)), 45); mid.blit(m, (FW // 2 - m.get_width() // 2 + 2, AY + 1 - m.get_height())); death.append(mid)
d2 = dead.copy(); puff(d2, .2, AX, AY - 2, 1.1); death.append(d2)
death += death_tail(dead, rnd, AX, AY - 4)
build("demon", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=180, loop=True, note="breathing + wing flex"),
    "walk": dict(frames=walk, dur=130, loop=True, note="hoof step, wings half-raised; move sprite in game"),
    "attack": dict(frames=attack, dur=[100, 110, 80, 120, 120], loop=False, note="wind-up (wings flare), claw lunge on frame 2 = hit frame"),
    "death": dict(frames=death, dur=[90, 70, 90, 100, 70, 160, 170, 90, 90, 100, 130], loop=False, note="play once; after last frame remove monster"),
}, "Original design: red horned demon with bat wings, tail, claws (replaces red-tinted ogre). ~hero scale (stands ~44px).")
print("ok")
