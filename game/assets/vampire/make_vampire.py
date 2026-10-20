"""Vampire strips. python3 make_vampire.py"""
import os, sys, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
FW, FH, AX, AY = 40, 48, 20, 46
CAPE = [(16, 12, 22), (30, 22, 40), (46, 34, 58)]; LINING = [(110, 20, 30), (150, 32, 40)]; SKIN = [(150, 150, 170), (190, 190, 206), (222, 222, 232)]
def vamp(sway=0, step=0, spread=0, lean=0, bob=0, fangs=False):
    s = surf(FW, FH); cx = 20 + lean; by = AY + bob
    w = 9 + spread * 8
    cape = [(cx - 4, by - 33), (cx - w, by - 18 + spread * 6), (cx - w + 1 + sway, by), (cx + w - 1 + sway, by), (cx + w, by - 18 + spread * 6), (cx + 4, by - 33)]
    pygame.draw.polygon(s, CAPE[1], cape)
    if spread > .2: pygame.draw.polygon(s, LINING[0], [(cx - 4, by - 31), (cx - w + 3, by - 18 + spread * 6), (cx - 4, by - 6), (cx + 4, by - 6), (cx + w - 3, by - 18 + spread * 6), (cx + 4, by - 31)])
    line(s, CAPE[2], cape[0], cape[1]); line(s, CAPE[0], cape[4], cape[3])
    pygame.draw.rect(s, (24, 20, 30), (cx - 4 + step, by - 8, 3, 8)); pygame.draw.rect(s, (24, 20, 30), (cx + 1 - step, by - 8, 3, 8))
    pygame.draw.rect(s, (36, 30, 44), (cx - 5, by - 28, 10, 20))   # suit
    pygame.draw.polygon(s, (230, 226, 230), [(cx - 2, by - 28), (cx + 2, by - 28), (cx, by - 22)]); s.set_at((cx, by - 24), LINING[1])
    pygame.draw.polygon(s, LINING[1], [(cx - 6, by - 30), (cx - 9, by - 37), (cx - 4, by - 31)]); pygame.draw.polygon(s, LINING[1], [(cx + 6, by - 30), (cx + 9, by - 37), (cx + 4, by - 31)])  # collar
    hx, hy = cx + 1, by - 34
    blob(s, hx, hy, 4.5, 5, SKIN)
    pygame.draw.polygon(s, (20, 16, 26), [(hx - 5, hy - 2), (hx - 4, hy - 6), (hx + 4, hy - 6), (hx + 5, hy - 2), (hx, hy - 3)])  # widow's peak
    s.set_at((hx - 1, hy), (230, 30, 40)); s.set_at((hx + 2, hy), (230, 30, 40)); line(s, INK, (hx - 2, hy - 1), (hx, hy)); line(s, INK, (hx + 1, hy), (hx + 3, hy - 1))
    line(s, (90, 30, 40), (hx - 1, hy + 3), (hx + 2, hy + 3))
    if fangs: s.set_at((hx - 1, hy + 4), (250, 250, 250)); s.set_at((hx + 2, hy + 4), (250, 250, 250))
    return outline(s)
idle = [vamp(sway=x) for x in (0, 1, 1, 0, -1, -1)]
walk = [vamp(step=st, sway=-st, bob=b) for st, b in ((-1, 0), (0, -1), (1, 0), (0, -1))]
attack = [vamp(spread=.3), vamp(spread=.8, bob=-1), vamp(spread=1, lean=2, fangs=True), vamp(spread=1, lean=3, fangs=True), vamp(spread=.4, lean=1)]
rnd = random.Random(6); MIST = ((150, 120, 170), (100, 80, 120))
def vanish(t):
    f = crumble(vamp(spread=1 - t), t, rnd, up=True); puff(f, t, 20, 30 - round(t * 10), 1.0, MIST)
    for k in range(int(1 + t * 4)):                         # little bats fleeing upward
        x, y = 8 + (k * 9 + int(t * 7)) % 26, max(3, 26 - int(t * 24) - k * 3)
        for dx, dy in ((-2, -1), (-1, 0), (0, 0), (1, 0), (2, -1)): f.set_at((x + dx, y + dy), INK)
    return f
death = [tint(vamp(), flash(.9)), tint(vamp(spread=.6, lean=-2), flash(.5)), vamp(spread=1, lean=-2, bob=-1), vanish(.25), vanish(.5), vanish(.75), vanish(1.0)]
build("vampire", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=170, loop=True, note="cape sway; vampire never moves in-game (can't be hurt)"),
    "walk": dict(frames=walk, dur=150, loop=True, note="provided for completeness"),
    "attack": dict(frames=attack, dur=[100, 110, 90, 140, 120], loop=False, note="cape flare (red lining), fanged lunge on frame 2"),
    "death": dict(frames=death, dur=[90, 90, 140, 100, 100, 110, 150], loop=False, note="'disappears' on the holy cross: flash, cape flare, dissolves upward into purple mist with fleeing bats; remove after last frame")},
    "Original: pale count with widow's peak, black suit, high red collar, black cape with red lining.")
print("ok")
