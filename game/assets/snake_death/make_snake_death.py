"""Snake death strip generator. python3 make_snake_death.py
Re-implements art3.make_snake geometry with pose params; 1x, RGBA, no smoothing, no shadow/glow."""
import os, sys, math, random, json
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../game"))
import pygame
pygame.init(); pygame.display.set_mode((1, 1))
import art, art3
sys.path.insert(0, os.path.join(HERE, '../_common'))
from snakelib import *
INK = art3.INK
def crumble(src, t, rnd):
    """dissolve: pixels drop out in Bayer order, loose ones fall as dust; top crumbles first"""
    s = pygame.Surface((FW, FH), pygame.SRCALPHA); s.fill((0, 0, 0, 0))
    for y in range(FH):
        for x in range(FW):
            c = src.get_at((x, y))
            if c.a == 0: continue
            thr = art.BAYER[y % 4][x % 4] / 16 * .7 + (1 - y / FH) * .3
            if thr < t:
                if rnd.random() < .08 * (1 - t):        # falling dust grain
                    dy = int(t * 10 * rnd.random()) + 1; yy = min(FH - 2, y + dy)
                    s.set_at((x, yy), gray((120, 112, 96), .3))
                continue
            s.set_at((x, y), c)
    return s
def puff(s, t, rnd):
    """dust puff ring + sparkles near ground (bottom ~y 38-44)"""
    gx, gy = FW // 2, 40
    for i in range(18):
        a = i / 18 * math.tau; r = 6 + t * 18
        x, y = gx + math.cos(a) * r, gy + math.sin(a) * r * .35 - t * 4
        rr = max(0, int(3 - t * 3 + (i % 2)))
        if rr: pygame.draw.circle(s, (150, 140, 120) if i % 3 else (110, 102, 92), (int(x), int(y)), rr)
    for i in range(6):
        a = rnd.random() * math.tau; r = 4 + t * 16 * rnd.random()
        x, y = int(gx + math.cos(a) * r), int(gy - 6 - t * 14 - rnd.random() * 10)
        if 1 <= x < FW - 1 and 1 <= y < FH - 1:
            col = (255, 240, 170) if i % 2 else (190, 230, 140)
            s.set_at((x, y), col)
            if (i + int(t * 10)) % 3 == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): s.set_at((x + dx, y + dy), (200, 170, 90))
def fl(c): return flash(c, .75)
def gr(t): f = lambda c: gray(c, t); f.__name__ = "gr"; return f
frames = []
frames.append(snake(tint=fl, neck_rise=1.05, neck_bend=-.6))                    # 0 hit flash, recoil back
frames.append(snake(neck_rise=1.1, neck_bend=-1.0, coil_jit=.6, phase=0))       # 1 rear up
frames.append(snake(neck_rise=.9, neck_bend=1.0, coil_jit=1.0, phase=2))        # 2 writhe
frames.append(snake(neck_rise=.75, neck_bend=-.8, coil_jit=1.0, phase=4))       # 3 writhe
frames.append(snake(neck_rise=.45, neck_bend=.4, coil_jit=.5, phase=5, eye=False))   # 4 neck falls
frames.append(snake(neck_rise=.12, neck_bend=0, flat=.9, eye=False, head_drop=2))   # 5 limp on ground
frames.append(snake(neck_rise=.1, flat=.85, eye=False, head_drop=2, tint=gr(.5), tongue=True))  # 6 still, greying
dead = snake(neck_rise=.1, flat=.85, eye=False, head_drop=2, tint=gr(.8))
rnd = random.Random(9)
for i, t in enumerate((.25, .5, .75, 1.0)):                                       # 7-10 crumble + puff
    f = crumble(dead, t, rnd); puff(f, (i + 1) / 5, rnd); frames.append(f)
f = pygame.Surface((FW, FH), pygame.SRCALPHA); f.fill((0, 0, 0, 0)); puff(f, 1.0, rnd)  # 11 last sparkles
# keep only sparkles for final frame
g = pygame.Surface((FW, FH), pygame.SRCALPHA); g.fill((0, 0, 0, 0))
for y in range(FH):
    for x in range(FW):
        c = f.get_at((x, y))
        if c.a and c[0] > 180: g.set_at((x, y), c)
frames.append(g)
DUR = [80, 70, 70, 70, 90, 140, 160, 90, 90, 90, 100, 120]
def strip(fr):
    s = pygame.Surface((FW * len(fr), FH), pygame.SRCALPHA); s.fill((0, 0, 0, 0))
    for i, f in enumerate(fr): s.blit(f, (i * FW, 0))
    return s
R = strip(frames); L = strip([pygame.transform.flip(f, True, False) for f in frames])
pygame.image.save(R, os.path.join(HERE, "snake_death_right.png")); pygame.image.save(L, os.path.join(HERE, "snake_death_left.png"))
json.dump({"sheets": [
  {"file": "snake_death_right.png", "facing": "right (native art3.make_snake orientation, game face>=0)"},
  {"file": "snake_death_left.png", "facing": "left (mirror; game face<0). Or flip the right strip at runtime like main.py does."}],
  "frame_size": [FW, FH], "frames": len(frames), "layout": "horizontal strip, 1x, RGBA, no smoothing",
  "fps": 11, "frame_durations_ms": DUR, "total_ms": sum(DUR),
  "anchor": {"px": [32, 42], "desc": "bottom-centre at body ground contact (lowest coil row). Equivalent: frame top-left = original snake sprite top-left - (8,6)."},
  "frame_anchor_offsets": [[0, 0]] * len(frames),
  "phases": {"0": "hit flash + recoil", "1-3": "rear up / writhe", "4-5": "neck collapses, X eye, limp", "6": "still, greying", "7-10": "crumble to dust with puff + sparkles", "11": "sparkles only"},
  "final_frame": "play once; after frame 11 remove the monster (draw nothing). Do not loop.",
  "layering": "draw on the monster/sprite layer at the snake's position, replacing the squash+fade. No shadow or glow baked; frame 0 is a baked white hit flash. Puff/sparkles extend to frame edges, may overlap neighbouring tiles.",
  "source": "art3.make_snake geometry/palette, regenerated by make_snake_death.py"}, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# previews
P = pygame.Surface((FW * 4 * 6 + 70, FH * 4 * 2 + 30)); P.fill((40, 36, 48))
for i, f in enumerate(frames):
    P.blit(pygame.transform.scale(f, (FW * 4, FH * 4)), (10 + (i % 6) * (FW * 4 + 10), 10 + (i // 6) * (FH * 4 + 10)))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
from PIL import Image
imgs = []
for f in frames:
    bg = pygame.Surface((FW, FH)); bg.fill((56, 54, 62)); bg.blit(f, (0, 0))
    imgs.append(Image.frombytes("RGB", (FW, FH), pygame.image.tobytes(bg, "RGB")).resize((FW * 4, FH * 4), Image.NEAREST))
imgs[0].save(os.path.join(HERE, "preview.gif"), save_all=True, append_images=imgs[1:], duration=DUR[:-1] + [600], loop=0)
print("ok")
