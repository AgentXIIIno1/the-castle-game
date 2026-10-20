"""Ogre idle/move/attack strips matching ogre_death (64x48, anchor 32,44). python3 make_ogre.py"""
import os, sys, math; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
FW, FH, AX, AY = 64, 48, 32, 44
BASE = art3.make_ogre(); BW, BH = BASE.get_size()
def place(spr, angle=0, dx=0, dy=0, sy=1.0, sx=1.0):
    """rotate about the feet (nearest), keep feet on anchor (same as ogre_death)"""
    s = spr if (sx, sy) == (1, 1) else pygame.transform.scale(spr, (round(BW * sx), round(BH * sy)))
    w, h = s.get_size(); big = surf(w * 3, h * 3); big.blit(s, (w, h)); pivot = (w + w // 2, h + h - 1)
    if angle:
        r = pygame.transform.rotate(big, angle); cx, cy = big.get_width() / 2, big.get_height() / 2; a = math.radians(angle)
        px, py = pivot[0] - cx, pivot[1] - cy
        pivot = (r.get_width() / 2 + px * math.cos(a) + py * math.sin(a), r.get_height() / 2 - px * math.sin(a) + py * math.cos(a)); big = r
    f = surf(FW, FH); f.blit(big, (round(AX + dx - pivot[0]), round(AY + dy - pivot[1]))); return f
idle = [place(BASE), place(BASE, sy=.97, sx=1.03), place(BASE, sy=.95, sx=1.05), place(BASE, sy=.97, sx=1.03)]
move = [place(BASE, 3, dy=0), place(BASE, 0, dy=-1), place(BASE, -3, dy=0), place(BASE, 0, dy=-1)]
attack = [place(BASE, 6, -1), place(BASE, 12, -2, sy=.96), place(BASE, -14, 3), place(BASE, -10, 2), place(BASE, -3, 1)]
build("ogre", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=[260, 180, 260, 180], loop=True, note="heavy breathing (squash/stretch)"),
    "move": dict(frames=move, dur=150, loop=True, note="lumbering side-to-side sway with bob; translate in game"),
    "attack": dict(frames=attack, dur=[110, 160, 70, 140, 140], loop=False, hit_frame=2, note="lean back with club raised, slam forward; frame 2 = hit frame"),
}, "Built from art3.make_ogre() pixels, nearest-only transforms about the feet; same frame/anchor as ogre_death so states swap without jumping.")
import json; m = json.load(open(os.path.join(HERE, "manifest.json"))); m["states"]["attack"]["hit_frame"] = 2; json.dump(m, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
print("ok")
