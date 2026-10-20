"""helpers: bake a real room via the game and place sprites; copy deliverables to game/assets"""
import os, shutil, pygame, json
from monlib import GAME, art3
_R = None
def rooms():
    global _R
    if _R is None:
        cwd = os.getcwd(); os.chdir(GAME); import main; _R = main.load_rooms(); os.chdir(cwd)
    return _R
def baked(rid):
    raw, TOP = art3.bake_room(rid, rooms()[rid]); raw = raw.copy(); raw.set_colorkey((255, 0, 255))
    b = pygame.Surface(raw.get_size()); b.fill((20, 16, 26)); b.blit(raw, (0, 0)); return b, TOP
def copy_to_game(src, name):
    dst = os.path.join(GAME, "assets", name); os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if not f.startswith("preview"): shutil.copy(os.path.join(src, f), dst)
