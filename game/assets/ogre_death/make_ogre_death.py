"""Ogre death strip. python3 make_ogre_death.py  (1x RGBA, nearest-only transforms, no shadow/glow)
Uses art3.make_ogre() directly; reuses crumble/puff helpers style from ../snake_death."""
import os, sys, math, random, json
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../game"))
import pygame
pygame.init(); pygame.display.set_mode((1, 1))
import art, art3
FW, FH = 64, 48; AX, AY = 32, 44          # anchor: feet ground contact, bottom-centre
BASE = art3.make_ogre(); BW, BH = BASE.get_size()
def tint(src, fn):
    s = src.copy()
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            c = s.get_at((x, y))
            if c.a: s.set_at((x, y), (*fn(c[:3]), c.a))
    return s
def flash(t): return lambda c: tuple(int(v + (255 - v) * t) for v in c) if sum(c) > 130 else c
def gray(t): return lambda c: tuple(int(v + (sum(c) // 3 + 25 - v) * t) for v in c)
def place(spr, angle=0, dx=0, sy=1.0, sx=1.0):
    """rotate about feet (nearest), keep feet on anchor"""
    s = spr
    if sx != 1 or sy != 1: s = pygame.transform.scale(s, (round(BW * sx), round(BH * sy)))
    w, h = s.get_size()
    big = pygame.Surface((w * 3, h * 3), pygame.SRCALPHA); big.fill((0, 0, 0, 0)); big.blit(s, (w, h))  # pivot = feet centre
    pivot = (w + w // 2, h + h - 1)
    if angle:
        r = pygame.transform.rotate(big, angle)
        # pivot moves: compute its new position
        cx, cy = big.get_width() / 2, big.get_height() / 2; a = math.radians(angle)
        px, py = pivot[0] - cx, pivot[1] - cy
        nx, ny = px * math.cos(a) + py * math.sin(a), -px * math.sin(a) + py * math.cos(a)
        pivot = (r.get_width() / 2 + nx, r.get_height() / 2 + ny); big = r
    f = pygame.Surface((FW, FH), pygame.SRCALPHA); f.fill((0, 0, 0, 0))
    f.blit(big, (round(AX + dx - pivot[0]), round(AY - pivot[1])))
    return f
def crumble(src, t, rnd):
    s = pygame.Surface((FW, FH), pygame.SRCALPHA); s.fill((0, 0, 0, 0))
    for y in range(FH):
        for x in range(FW):
            c = src.get_at((x, y))
            if not c.a: continue
            thr = art.BAYER[y % 4][x % 4] / 16 * .7 + (1 - y / FH) * .3
            if thr < t:
                if rnd.random() < .08 * (1 - t): s.set_at((x, min(FH - 2, y + 1 + int(t * 8 * rnd.random()))), (128, 120, 104))
                continue
            s.set_at((x, y), c)
    return s
def puff(s, t, rnd, gx=FW // 2, gy=42, big=1.0):
    for i in range(20):
        a = i / 20 * math.tau; r = (6 + t * 20) * big
        x, y = gx + math.cos(a) * r, gy + math.sin(a) * r * .3 - t * 4
        rr = max(0, int(3 - t * 3 + (i % 2)))
        if rr: pygame.draw.circle(s, (150, 140, 120) if i % 3 else (110, 102, 92), (int(x), int(y)), rr)
def sparkles(s, t, rnd, gx=FW // 2, gy=40):
    for i in range(7):
        a = rnd.random() * math.tau; r = 4 + t * 18 * rnd.random()
        x, y = int(gx + math.cos(a) * r), int(gy - 6 - t * 16 - rnd.random() * 10)
        if 1 <= x < FW - 1 and 1 <= y < FH - 1:
            s.set_at((x, y), (255, 240, 170) if i % 2 else (190, 230, 140))
            if i % 3 == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): s.set_at((x + dx, y + dy), (200, 170, 90))
rnd = random.Random(5)
F = []
F.append(place(tint(BASE, flash(.9)), 0, 2))                  # 0 heavy hit flash, knocked back
F.append(place(tint(BASE, flash(.45)), 6, 3))                 # 1 flash fading, reels back
F.append(place(BASE, 10, 3))                                  # 2 stagger back
F.append(place(BASE, -4, 0))                                  # 3 stagger forward
F.append(place(BASE, 2, 1, sy=.88, sx=1.06))                  # 4 knees buckle
F.append(place(BASE, 30, 5, sy=.92))                          # 5 topple
F.append(place(BASE, 62, 10, sy=.95))                          # 6 topple
down = place(BASE, 90, 15)
d7 = down.copy(); puff(d7, .25, rnd, gy=43, big=1.2); F.append(d7)   # 7 THUD on back + impact dust
F.append(place(tint(BASE, gray(.5)), 90, 15))                  # 8 lying, greying
dead = place(tint(BASE, gray(.8)), 90, 15)
for i, t in enumerate((.3, .6, .9)):                          # 9-11 crumble
    f = crumble(dead, t, rnd); puff(f, (i + 2) / 5, rnd); sparkles(f, (i + 1) / 4, rnd); F.append(f)
f = pygame.Surface((FW, FH), pygame.SRCALPHA); f.fill((0, 0, 0, 0)); sparkles(f, 1.0, rnd); F.append(f)  # 12 sparkles only
DUR = [90, 70, 90, 90, 110, 70, 60, 160, 180, 90, 90, 100, 130]
def strip(fr):
    s = pygame.Surface((FW * len(fr), FH), pygame.SRCALPHA); s.fill((0, 0, 0, 0))
    for i, f in enumerate(fr): s.blit(f, (i * FW, 0))
    return s
pygame.image.save(strip(F), os.path.join(HERE, "ogre_death_right.png"))
pygame.image.save(strip([pygame.transform.flip(f, True, False) for f in F]), os.path.join(HERE, "ogre_death_left.png"))
json.dump({"sheets": [{"file": "ogre_death_right.png", "facing": "native art3.make_ogre orientation (club on right), game face>=0; topples to the left/back"},
                      {"file": "ogre_death_left.png", "facing": "mirror for face<0 (or flip right strip at runtime)"}],
  "frame_size": [FW, FH], "frames": len(F), "layout": "horizontal strip, 1x, RGBA, nearest only", "fps": 10, "frame_durations_ms": DUR, "total_ms": sum(DUR),
  "anchor": {"px": [AX, AY], "desc": f"bottom-centre at the ogre's feet (ground contact). Source sprite ({BW}x{BH}) sits with feet-centre on this point in frame 0 (shifted +2px by knockback)."},
  "frame_anchor_offsets": [[0, 0]] * len(F),
  "phases": {"0-1": "heavy white hit flash + knockback", "2-4": "stagger back/forward, knees buckle", "5-7": "topple onto back, impact dust", "8": "lying, greying", "9-11": "crumble to dust with puff + sparkles", "12": "sparkles only"},
  "final_frame": "play once; after frame 12 remove the monster (draw nothing). No loop.",
  "layering": "monster/sprite layer at ogre position, replaces squash+fade. No shadow/glow baked (flash is baked white tint). Body slides up to +15px right of anchor as it falls (baked into frames, offsets stay 0); fallen body spans roughly x 12-50 of the frame.",
  "source": "art3.make_ogre() pixels, transformed by make_ogre_death.py"}, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
P = pygame.Surface((7 * (FW * 4 + 10) + 10, 2 * (FH * 4 + 10) + 10)); P.fill((40, 36, 48))
for i, f in enumerate(F): P.blit(pygame.transform.scale(f, (FW * 4, FH * 4)), (10 + (i % 7) * (FW * 4 + 10), 10 + (i // 7) * (FH * 4 + 10)))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
from PIL import Image
imgs = []
for f in F:
    bg = pygame.Surface((FW, FH)); bg.fill((56, 54, 62)); bg.blit(f, (0, 0))
    imgs.append(Image.frombytes("RGB", (FW, FH), pygame.image.tobytes(bg, "RGB")).resize((FW * 4, FH * 4), Image.NEAREST))
imgs[0].save(os.path.join(HERE, "preview.gif"), save_all=True, append_images=imgs[1:], duration=DUR[:-1] + [600], loop=0)
print("ok", BW, BH)
