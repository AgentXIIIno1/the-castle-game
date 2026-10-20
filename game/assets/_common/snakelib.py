"""Shared snake drawer (cleaner rings, bigger head) used by snake/ and snake_death/."""
import math, random
from monlib import *
FW, FH = 64, 48; OX, OY = 8, 6
INK = art3.INK
PAL = [(22, 52, 26), (48, 98, 44), (70, 124, 54), (140, 182, 84)]
FW, FH = 64, 48            # frame; snake (48x40 + 1px outline) placed with ground contact at bottom-centre
OX, OY = 8, 6              # offset of the 48x40 snake box within the frame (matches original sprite at frame (8,6))
def gray(c, t): g = sum(c) // 3; return tuple(int(c[i] + ((g + 30) - c[i]) * t) for i in range(3))
def flash(c, t): return tuple(int(c[i] + (255 - c[i]) * t) for i in range(3))
def snake(neck_rise=1.0, neck_bend=0.0, coil_jit=0.0, flat=1.0, tint=None, phase=0.0, head_drop=0.0, eye=True, tongue=True):
    s = pygame.Surface((FW, FH), pygame.SRCALPHA); s.fill((0, 0, 0, 0))
    cx, cy = 22 + OX, 28 + OY
    pal = [tint(c) for c in PAL] if tint else PAL; ink = INK
    dark, mid, mid2, light = pal
    pts = []
    for i in range(140):
        a = i / 140 * math.pi * 4.2; r = 17 - i / 140 * 13
        r *= 1 + coil_jit * math.sin(a * 3 + phase) * .12
        pts.append((cx + math.cos(a) * r * (1 + (1 - flat) * .25), cy + math.sin(a) * r * .5 * flat + (1 - flat) * 3, 4.2 - i / 140 * 1.4))
    neck = []
    for i in range(22):
        u = i / 21
        x = cx + 17 + u * 2 - u * u * 4 + neck_bend * math.sin(u * math.pi) * 6 + (1 - neck_rise) * u * 14
        y = cy - u * 18 * neck_rise
        neck.append((x, y, 3.3 - u * .6))
    pts = neck[::-1] + pts
    order = sorted(range(len(pts)), key=lambda k: pts[k][1])
    for k in order:
        x, y, th = pts[k]; pygame.draw.circle(s, ink, (x, y), th + 1)
    for k in order:
        x, y, th = pts[k]
        pygame.draw.circle(s, ink, (x, y + 1), th); pygame.draw.circle(s, dark, (x, y), th); pygame.draw.circle(s, mid, (x - .6, y - .8), th * .78)
        pygame.draw.circle(s, mid2, (x - 1, y - 1.3), th * .45)
        if k % 7 == 0 and k > 22:   # clean ring band: dark seam + pale ring
            line(s, (14, 34, 18), (x - th * .8, y + th * .3), (x + th * .3, y - th * .8)); line(s, mid2, (x - th * .8 + 1, y + th * .3), (x + th * .3 + 1, y - th * .8)); s.set_at((int(x - 1), int(y - 2)), light)
    for y in range(FH):
        for x in range(FW):
            if s.get_at((x, y))[:3] == mid and (x + y * 3) % 7 == 0: s.set_at((x, y), dark)
    hx, hy = int(neck[-1][0]) - 3, int(neck[-1][1]) - 3 + int(head_drop)
    pygame.draw.ellipse(s, ink, (hx - 3, hy - 6, 17, 12)); pygame.draw.ellipse(s, mid, (hx - 2, hy - 5, 15, 10))
    pygame.draw.ellipse(s, mid2, (hx, hy - 5, 10, 4)); line(s, light, (hx + 1, hy - 5), (hx + 8, hy - 5))
    line(s, dark, (hx + 2, hy + 3), (hx + 12, hy + 1)); pygame.draw.ellipse(s, (120, 150, 80), (hx + 1, hy + 1, 10, 3))
    s.set_at((hx + 12, hy - 2), dark)                                   # nostril
    ex, ey = hx + 7, hy - 2
    if eye:
        pygame.draw.rect(s, INK, (ex - 1, ey - 1, 4, 3)); s.set_at((ex, ey), (255, 200, 60)); s.set_at((ex + 1, ey), (255, 120, 40)); s.set_at((ex + 1, ey - 1), (255, 240, 180))
    else:
        for d in (-1, 1): s.set_at((ex + d, ey + d), INK); s.set_at((ex + d, ey - d), INK)
        s.set_at((ex, ey), INK)
    if tongue: line(s, (220, 40, 60), (hx + 14, hy + 1), (hx + 17, hy + 2 + (0 if eye else 2))); s.set_at((hx + 18, hy + 1), (220, 40, 60)); s.set_at((hx + 18, hy + 3), (220, 40, 60))
    return art.outline(s) if s.get_size() == (FW, FH) and False else s
