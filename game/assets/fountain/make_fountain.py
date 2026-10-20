"""Fountain (3x3 footprint ',-.' '|?|' "`-'"): stone base + animated water/spout. python3 make_fountain.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art import lerp, STONE
FW, FH = 48, 60; AX, AY = 24, 59           # footprint = bottom 48x48 of the frame; anchor = bottom-centre of footprint
NF = 8
THEMES = {"garden": dict(st=[(58, 56, 66), (84, 80, 92), (110, 104, 114), (150, 144, 152)], moss=[(58, 88, 40), (86, 118, 52)]),
          "balcony": dict(st=[(66, 62, 70), (92, 88, 96), (120, 114, 122), (168, 162, 168)], moss=[])}
WATER = [(26, 60, 92), (38, 88, 124), (58, 122, 156), (110, 176, 206), (200, 236, 250)]
def ell(s, c, r): pygame.draw.ellipse(s, c, pygame.Rect(r))
def base(theme):
    p = THEMES[theme]; st = p["st"]; s = surf(FW, FH); rnd = random.Random(len(theme))
    # outer basin: front wall (lower ellipse band) + rim top
    ell(s, OUT, (0, 31, 48, 28)); ell(s, st[0], (1, 32, 46, 26))
    for y in range(40, 58):                                   # front wall with stone courses + Bayer shading
        for x in range(1, 47):
            if s.get_at((x, y))[:3] == st[0]:
                v = .55 - (y - 40) / 18 * .4 + (BAYER[y % 4][x % 4] / 16 - .5) * .25 - abs(x - 24) / 24 * .15
                c = st[max(0, min(2, int(v * 3)))]
                if (y - 41) % 6 == 0 or ((x + (y // 6) * 5) % 11 == 0): c = OUT if y > 42 else st[0]
                s.set_at((x, y), c)
    ell(s, OUT, (0, 25, 48, 24)); ell(s, st[2], (1, 26, 46, 22))          # rim top surface
    line(s, st[3], (8, 27), (38, 27)); line(s, st[3], (4, 29), (8, 27))   # rim highlight (top-left lit)
    ell(s, OUT, (5, 29, 38, 16)); ell(s, st[0], (6, 30, 36, 14))         # inner well (water layer drawn into it)
    # pedestal + upper bowl
    pygame.draw.rect(s, OUT, (20, 16, 9, 23)); pygame.draw.rect(s, st[1], (21, 17, 7, 22)); line(s, st[3], (21, 17), (21, 37)); line(s, st[0], (27, 17), (27, 38))
    ell(s, OUT, (12, 11, 25, 10)); ell(s, st[1], (13, 12, 23, 8)); ell(s, st[2], (13, 11, 23, 6)); line(s, st[3], (16, 12), (30, 12))
    ell(s, OUT, (17, 12, 15, 4)); pygame.draw.rect(s, OUT, (23, 4, 3, 9)); pygame.draw.rect(s, st[2], (24, 5, 1, 7))   # finial / spout pipe
    for m in range(14 if p["moss"] else 0):                                       # moss on the outer wall + rim
        x, y = rnd.randrange(4, 44), rnd.choice((rnd.randrange(44, 56), rnd.randrange(27, 31)))
        if s.get_at((x, y)).a and s.get_at((x, y))[:3] != OUT: s.set_at((x, y), p["moss"][m % 2])
    return s
def water(i):
    """water surface in the basin + upper bowl, ripples expand from the pedestal; spout arcs with moving droplets"""
    s = surf(FW, FH); t = i / NF
    ell(s, WATER[1], (6, 31, 36, 13)); ell(s, WATER[0], (6, 38, 36, 6))
    for k in range(2):                                         # expanding ripple rings
        r = ((t + k / 2) % 1); w, h = 10 + r * 26, 4 + r * 9
        rr = pygame.Rect(0, 0, w, h); rr.center = (24, 37)
        if rr.width < 36: pygame.draw.ellipse(s, WATER[3] if r < .6 else WATER[2], rr, 1)
    for k in range(3):                                         # soft glints drifting
        gx = 10 + (k * 11 + i * 2) % 28; gy = 33 + (k * 3) % 6
        if s.get_at((gx, gy)).a: s.set_at((gx, gy), WATER[4]); s.set_at((gx + 1, gy), WATER[3])
    ell(s, WATER[1], (15, 12, 19, 5)); line(s, WATER[3], (18, 13), (22 + i % 3, 13))                # upper bowl water
    for side in (-1, 1):                                       # spout: arcs from finial to upper bowl, overflow to basin
        for j in range(5):
            u = ((j / 5) + t) % 1; x = 24 + side * u * 7; y = 4 + (-6 * u + 14 * u * u)
            s.set_at((round(x), round(y)), WATER[4] if j % 2 else WATER[3])
        for j in range(4):
            u = ((j / 4) + t * 1.3) % 1; x = 24 + side * (11 + u * 5); y = 16 + u * u * 18
            c = WATER[3] if j % 2 else WATER[2]
            s.set_at((round(x), round(y)), c); s.set_at((round(x), round(y) + 1), WATER[2])
    s.set_at((24, 2 + (i % 2)), WATER[4])
    return s
out = {"sheets": [], "footprint_tiles": [3, 3], "glyphs": ",-. |?| `-'",
       "rooms": {"18": "GARDEN_SOUTH (rows 11-13, cols 11-13, 1-based) -> theme garden", "33": "BALCONY (rows 13-15, cols 15-17) -> theme balcony"},
       "anchor": {"px": [AX, AY], "desc": "bottom-centre of the 3x3 footprint: world (fx*16 + 24, (fy+3)*16) where (fx,fy) = 0-based cell of ','. Frame extends 12px above the footprint for the spout."},
       "layering": "object layer, depth-sort at y = (fy+3)*16 (same as now). Draw base, then water strip on top (same anchor). Or use the pre-composited *_full strip.",
       "blocking": "all 9 footprint cells block (unchanged: main.py FOUNTAIN glyphs). '?' is the centre.",
       "animation": {"frames": NF, "fps": 8, "frame_durations_ms": [125] * NF, "loop": True}, "no_glow_baked": True}
PRE = []
for th in THEMES:
    b = base(th); pygame.image.save(b, os.path.join(HERE, f"fountain_{th}_base.png"))
    W = surf(FW * NF, FH); F = surf(FW * NF, FH)
    for i in range(NF):
        w = water(i); W.blit(w, (i * FW, 0)); F.blit(b, (i * FW, 0)); F.blit(w, (i * FW, 0))
    pygame.image.save(W, os.path.join(HERE, f"fountain_{th}_water.png")); pygame.image.save(F, os.path.join(HERE, f"fountain_{th}_full.png"))
    out["sheets"] += [{"file": f"fountain_{th}_base.png", "frame_size": [FW, FH], "frames": 1, "layer": "base (static stone)"},
                      {"file": f"fountain_{th}_water.png", "frame_size": [FW, FH], "frames": NF, "layer": "water+spout overlay, loop"},
                      {"file": f"fountain_{th}_full.png", "frame_size": [FW, FH], "frames": NF, "layer": "base+water composited, loop"}]
    PRE.append((th, F))
json.dump(out, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# previews on real floors
import art3
rooms = {r["id"]: r for r in json.load(open(os.path.join(GAME, "../map/rooms.json")))["rooms"]}
fl18 = art3.bake_floor(18, rooms[18], True); fl33 = art3.bake_floor(33, rooms[33], False)
from PIL import Image
frames = []; Z = 3
for i in range(NF):
    P = pygame.Surface((2 * 112 * Z + 30, 112 * Z + 20)); P.fill((40, 36, 48))
    for k, (th, F) in enumerate(PRE):
        fl, (fx, fy) = ((fl18, (10, 10)) if th == "garden" else (fl33, (14, 12)))
        crop = fl.subsurface(((fx - 2) * 16 - 8, (fy - 2) * 16 - 8, 112, 112)).copy()
        crop.blit(F.subsurface((i * FW, 0, FW, FH)), (32 - 8 + 8, 32 + 8 + 48 - FH - 0 + 0))
        P.blit(pygame.transform.scale(crop, (112 * Z, 112 * Z)), (10 + k * (112 * Z + 10), 10))
    if i == 0: pygame.image.save(P, os.path.join(HERE, "preview.png"))
    frames.append(Image.frombytes("RGB", P.get_size(), pygame.image.tobytes(P, "RGB")))
frames[0].save(os.path.join(HERE, "preview.gif"), save_all=True, append_images=frames[1:], duration=125, loop=0)
print("ok")
