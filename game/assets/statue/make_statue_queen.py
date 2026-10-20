"""Weathered statue of a robed queen on a plinth, room 19 (3x3 ',-.' '|$|' "`-'"). python3 make_statue.py"""
import os, sys, math, random, json, shutil; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art import lerp
FW, FH = 48, 76; AX, AY = 24, 75                         # bottom 48x48 = footprint, 28px headroom
ST = [(70, 64, 60), (108, 100, 90), (146, 136, 120), (182, 172, 152), (222, 214, 194)]   # weathered limestone (warmer/lighter than the flag floor)
MOSS = [(48, 74, 36), (74, 104, 48), (104, 136, 62)]
GOLD = [(110, 70, 24), (176, 124, 40), (226, 176, 72), (255, 232, 150)]; RUBY = [(90, 14, 26), (150, 26, 40), (196, 36, 52), (240, 120, 130)]
SH = (10, 8, 16)
def shade(s, pts_fn, lx=-.5, ly=-.8):
    pass
def fillshade(s, mask_surf, ox=0, oy=0, cx=None):
    """shade every opaque pixel of mask by position (top-left lit) w/ Bayer dither into ST"""
    W, H = mask_surf.get_size(); b = mask_surf.get_bounding_rect()
    for y in range(H):
        for x in range(W):
            if mask_surf.get_at((x, y)).a:
                u = (x - 24) / 10.0; v = (y - b.y) / max(1, b.height)       # cylindrical: lit from the left, darker right edge and low
                l = .72 - u * .3 - abs(u) * .12 - v * .18 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
                s.set_at((x + ox, y + oy), ST[max(0, min(3, int(l * 4)))])
def statue(necklace):
    s = surf(FW, FH); r = random.Random(19)
    # contact shadow (baked)
    for y in range(FH - 8, FH):
        for x in range(FW):
            d = ((x - 25) / 23) ** 2 + ((y - (FH - 3)) / 4) ** 2
            if d <= 1 and (d < .6 or BAYER[y % 4][x % 4] / 16 > (d - .6) * 2.5): s.set_at((x, y), (*SH, 120))
    # plinth: top surface (y 46..54) + front face (54..72) spanning ~42px
    top = pygame.Rect(4, 44, 40, 11); face = pygame.Rect(4, 55, 40, 16)
    pygame.draw.rect(s, OUT, top.inflate(2, 2)); pygame.draw.rect(s, OUT, face.inflate(2, 2))
    for y in range(face.top, face.bottom):
        for x in range(face.left, face.right):
            l = .55 - (y - face.top) / face.height * .3 - (x - face.left) / face.width * .15 + (BAYER[y % 4][x % 4] / 16 - .5) * .25
            s.set_at((x, y), ST[max(0, min(3, int(l * 4)))])
    for y in range(top.top, top.bottom):
        for x in range(top.left, top.right):
            l = .8 - (x - top.left) / top.width * .25 + (BAYER[y % 4][x % 4] / 16 - .5) * .2
            s.set_at((x, y), ST[max(1, min(3, int(l * 4)))])
    line(s, ST[4], (top.left, top.top), (top.right - 1, top.top)); line(s, ST[3], (face.left, face.top), (face.right - 1, face.top))
    for yy in (60, 66): line(s, OUT, (face.left, yy), (face.right - 1, yy))                    # stone courses
    for xx in (14, 30, 22, 38): line(s, OUT, (xx, 60 if xx in (14, 30) else 66), (xx, 66 if xx in (14, 30) else 71))
    rect = pygame.draw.rect; rect(s, ST[0], (34, 55, 6, 3)); line(s, ST[4], (34, 58), (39, 58))   # chipped corner
    line(s, OUT, (9, 56), (11, 60)); line(s, OUT, (11, 60), (10, 64)); line(s, ST[3], (10, 56), (12, 60))  # crack
    # figure: robed queen, facing viewer. Build silhouette mask then shade
    m = surf(FW, FH)
    pygame.draw.polygon(m, (255, 255, 255), [(14, 50), (34, 50), (31, 30), (28, 22), (20, 22), (17, 30)])   # robe (flares to base)
    pygame.draw.ellipse(m, (255, 255, 255), (17, 20, 14, 8))                                             # shoulders
    pygame.draw.rect(m, (255, 255, 255), (22, 16, 4, 5))                                                 # neck
    pygame.draw.ellipse(m, (255, 255, 255), (19, 8, 10, 10))                                             # head
    pygame.draw.polygon(m, (255, 255, 255), [(20, 9), (20, 5), (22, 7), (24, 4), (26, 7), (28, 5), (28, 9)])  # crown
    pygame.draw.polygon(m, (255, 255, 255), [(31, 24), (36, 34), (34, 36), (29, 28)])                    # right arm out holding orb
    pygame.draw.circle(m, (255, 255, 255), (35, 35), 3)
    pygame.draw.polygon(m, (255, 255, 255), [(17, 24), (14, 36), (17, 37), (20, 28)])                    # left arm folded
    o = outline(m); s.blit(pygame.mask.from_surface(o).to_surface(setcolor=OUT, unsetcolor=(0, 0, 0, 0)), (0, 0))
    fillshade(s, m)
    for (a, b_) in (((21, 30), (19, 49)), ((25, 31), (25, 49)), ((29, 31), (31, 49))): line(s, ST[0], a, b_)   # robe folds
    for (a, b_) in (((22, 31), (20, 49)), ((26, 31), (26, 49))): line(s, ST[3], a, b_)
    line(s, ST[4], (18, 22), (22, 20)); line(s, ST[4], (20, 9), (20, 15)); line(s, ST[4], (19, 9), (21, 4))   # rim light top-left
    s.set_at((22, 12), ST[0]); s.set_at((26, 12), ST[0]); line(s, ST[1], (23, 15), (25, 15)); s.set_at((24, 13), ST[1])  # worn face
    line(s, OUT, (27, 10), (26, 14)); line(s, OUT, (26, 14), (28, 17))                                  # facial crack
    line(s, OUT, (30, 33), (28, 40)); line(s, OUT, (28, 40), (30, 45))                                  # robe crack
    s.set_at((36, 34), ST[0]); s.set_at((37, 35), (0, 0, 0, 0))                                         # chipped orb
    for k in range(26):                                                                                  # moss: clumps on plinth top, robe hem, shoulders
        x, y = r.choice([(r.randrange(6, 42), r.randrange(44, 48)), (r.randrange(15, 33), r.randrange(46, 50)), (r.randrange(5, 12), r.randrange(55, 70)), (r.randrange(18, 22), r.randrange(21, 24))])
        if s.get_at((x, y)).a and s.get_at((x, y))[:3] != OUT: s.set_at((x, y), MOSS[k % 3]); s.set_at((x, y + 1), MOSS[0]) if s.get_at((x, y + 1)).a else None
    if necklace:
        for i in range(11):                                                                              # draped chain over shoulders
            a = math.pi * i / 10; x, y = 24 - math.cos(a) * 5, 19 + math.sin(a) * 5
            s.set_at((round(x), round(y)), GOLD[2] if i % 2 else GOLD[3])
        pygame.draw.polygon(s, OUT, [(22, 23), (26, 23), (24, 27)]); pygame.draw.polygon(s, RUBY[2], [(23, 24), (25, 24), (24, 26)]); s.set_at((23, 24), RUBY[3])
    return s
def glint(base, i):
    f = base.copy()
    if i in (1, 2):
        x, y = (23, 24) if i == 1 else (21, 22)
        for d, c in (((0, 0), (255, 255, 240)), ((1, 0), (255, 240, 180)), ((-1, 0), (255, 240, 180)), ((0, 1), (255, 240, 180)), ((0, -1), (255, 240, 180))): f.set_at((x + d[0], y + d[1]), c)
        if i == 1: f.set_at((x + 2, y), (255, 220, 140)); f.set_at((x - 2, y), (255, 220, 140))
    return f
A = statue(True); B = statue(False)
pygame.image.save(A, os.path.join(HERE, "statue_necklace.png")); pygame.image.save(B, os.path.join(HERE, "statue_plain.png"))
DUR = [1600, 90, 110, 200]
G = surf(FW * 4, FH)
for i in range(4): G.blit(glint(A, i), (i * FW, 0))
pygame.image.save(G, os.path.join(HERE, "statue_necklace_glint.png"))
json.dump({"room": 19, "room_name": "Center Of The Upper Hall", "glyphs": ",-. |$| `-'", "footprint_tiles": [3, 3], "footprint_cells_0based": "cols 10-12, rows 6-8 ('$' at col 11,row 7)",
  "frame_size": [FW, FH], "anchor": {"px": [AX, AY], "desc": "bottom-centre of the 3x3 footprint: world (fx*16 + 24, (fy+3)*16), (fx,fy) = 0-based cell of ','; frame top-left = (fx*16, (fy+3)*16 - 76)"},
  "depth_sort_y": "(fy+3)*16 (same as the fountain draw it replaces)", "blocking": "all 9 footprint cells (main.py solid glyphs ',-.|$`'')", "shadow_baked": True,
  "states": {"with_necklace": {"file": "statue_necklace.png", "when": "necklace still hidden on the statue ('$' item not taken)"},
             "with_necklace_glint": {"file": "statue_necklace_glint.png", "frames": 4, "frame_durations_ms": DUR, "loop": True, "note": "sparkle ~every 2 s; use instead of the static with_necklace"},
             "without_necklace": {"file": "statue_plain.png", "when": "after GET NECKLACE"}},
  "design": "original: weathered robed queen with crown, holding a chipped orb, on a coursed plinth; cracks, chips, moss; necklace in the Necklace item's gold + ruby"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# previews on the real room 19 floor
import art3
rooms = {r["id"]: r for r in json.load(open(os.path.join(GAME, "../map/rooms.json")))["rooms"]}
fl = art3.bake_floor(19, rooms[19], False); fx, fy = 10, 6
from PIL import Image
frames = []; Z = 3
crop = pygame.Rect(fx * 16 - 32, fy * 16 - 48, 112, 128)
for i in range(4):
    P = pygame.Surface((112 * Z * 2 + 30, 128 * Z + 20)); P.fill((40, 36, 48))
    for k, img in enumerate((G.subsurface((i * FW, 0, FW, FH)), B)):
        f = fl.copy(); f.blit(img, (fx * 16, (fy + 3) * 16 - FH)); P.blit(pygame.transform.scale(f.subsurface(crop), (112 * Z, 128 * Z)), (10 + k * (112 * Z + 10), 10))
    if i == 0: pygame.image.save(P, os.path.join(HERE, "preview.png"))
    frames.append(Image.frombytes("RGB", P.get_size(), pygame.image.tobytes(P, "RGB")))
frames[0].save(os.path.join(HERE, "preview.gif"), save_all=True, append_images=frames[1:], duration=DUR, loop=0)
dst = os.path.join(GAME, "assets", "statue"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(HERE):
    if not f.startswith("preview"): shutil.copy(os.path.join(HERE, f), dst)
print("ok")
