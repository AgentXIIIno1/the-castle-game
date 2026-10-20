"""Weathered statue of the KING on a plinth, room 19 (3x3 ',-.' '|$|' "`-'"). Queen original kept as make_statue_queen.py / statue_queen_*. python3 make_statue.py"""
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
    # figure: the King, facing viewer. broad shoulders, fur mantle, full beard, crown, sceptre. Build silhouette mask then shade
    m = surf(FW, FH); w = (255, 255, 255)
    pygame.draw.polygon(m, w, [(11, 50), (37, 50), (36, 30), (34, 22), (14, 22), (12, 30)])                  # heavy robe, boxy to the base
    pygame.draw.ellipse(m, w, (9, 18, 30, 11))                                                            # broad shoulders + mantle
    pygame.draw.ellipse(m, w, (18, 7, 12, 12))                                                            # head
    pygame.draw.polygon(m, w, [(19, 14), (29, 14), (28, 22), (24, 27), (20, 22)])                          # full beard to the chest
    pygame.draw.polygon(m, w, [(18, 9), (18, 3), (20, 5), (22, 1), (24, 4), (26, 1), (28, 5), (30, 3), (30, 9)])  # tall crown
    pygame.draw.rect(m, w, (37, 4, 3, 42)); pygame.draw.circle(m, w, (38, 4), 3)                         # sceptre (viewer's right)
    pygame.draw.polygon(m, w, [(33, 26), (38, 30), (39, 34), (35, 34), (31, 30)])                          # right arm holding the sceptre
    pygame.draw.polygon(m, w, [(14, 26), (11, 36), (19, 38), (21, 33)])                                   # left arm across the belly
    o = outline(m); s.blit(pygame.mask.from_surface(o).to_surface(setcolor=OUT, unsetcolor=(0, 0, 0, 0)), (0, 0))
    fillshade(s, m)
    for (a, b_) in (((17, 38), (14, 49)), ((22, 39), (21, 49)), ((27, 39), (28, 49)), ((32, 36), (34, 49))): line(s, ST[0], a, b_)  # robe folds
    for (a, b_) in (((18, 38), (15, 49)), ((23, 39), (22, 49)), ((28, 39), (29, 49))): line(s, ST[3], a, b_)
    line(s, ST[0], (24, 28), (24, 49)); line(s, ST[3], (23, 29), (23, 49))                                  # robe opening
    def part(poly_fn, shade_fn):
        p = surf(FW, FH); poly_fn(p)
        for y in range(FH):
            for x in range(FW):
                if p.get_at((x, y)).a: p.set_at((x, y), shade_fn(x, y))
        s.blit(outline(p), (0, 0))
    # fur mantle (ermine): pale band over the shoulders with dark tail-spots, scalloped hem
    def mant(p):
        pygame.draw.ellipse(p, (1, 1, 1), (9, 18, 30, 10)); pygame.draw.rect(p, (1, 1, 1), (10, 23, 28, 4))
        for x in range(10, 38, 4): pygame.draw.circle(p, (1, 1, 1), (x + 2, 27), 2)
    part(mant, lambda x, y: ST[0] if (x * 5 + y * 3) % 11 == 0 and y > 20 else (ST[4] if x < 18 and y < 22 else ST[3] if x < 26 else ST[2]) if BAYER[y % 4][x % 4] > 3 else ST[2] if x > 30 else ST[3])
    # hands: left fist across the robe, right fist on the sceptre
    part(lambda p: (pygame.draw.ellipse(p, (1, 1, 1), (12, 33, 9, 6)), pygame.draw.ellipse(p, (1, 1, 1), (34, 29, 6, 6))), lambda x, y: ST[3] if x < 24 else ST[2])
    line(s, ST[0], (15, 35), (15, 37)); line(s, ST[0], (17, 35), (17, 37)); line(s, ST[0], (36, 31), (38, 31))
    # head: face + full beard drawn as distinct outlined shapes
    part(lambda p: pygame.draw.ellipse(p, (1, 1, 1), (19, 8, 11, 10)), lambda x, y: ST[3] if x < 25 else ST[2])
    def beard(p): pygame.draw.polygon(p, (1, 1, 1), [(18, 13), (20, 17), (24, 16), (28, 17), (30, 13), (31, 19), (29, 25), (24, 31), (19, 25), (17, 19)])
    part(beard, lambda x, y: ST[0] if (y + (x // 2) * 2) % 4 == 0 else (ST[4] if x < 22 else ST[3] if x < 27 else ST[2]))
    line(s, ST[0], (21, 16), (23, 15)); line(s, ST[0], (25, 15), (27, 16)); line(s, ST[1], (23, 17), (25, 17))                                           # moustache
    s.set_at((22, 12), ST[0]); s.set_at((26, 12), ST[0]); line(s, ST[0], (21, 11), (23, 11)); line(s, ST[0], (25, 11), (27, 11))  # deep-set eyes + brow
    s.set_at((24, 13), ST[1]); s.set_at((24, 14), ST[0])                                                    # nose
    line(s, ST[0], (18, 8), (30, 8)); line(s, ST[4], (18, 7), (29, 7))                                      # crown band
    for x in (20, 24, 28): s.set_at((x, 6), ST[0])                                                           # carved crown jewels
    line(s, ST[4], (19, 4), (19, 8)); line(s, ST[4], (11, 22), (17, 19)); line(s, ST[4], (18, 10), (18, 14))  # rim light top-left
    line(s, ST[4], (37, 6), (37, 44)); line(s, ST[0], (39, 6), (39, 44)); s.set_at((37, 3), ST[4])           # sceptre shaft lit
    for y in (12, 24): line(s, ST[0], (37, y), (39, y))
    line(s, OUT, (28, 9), (27, 12))                                       # facial crack
    line(s, OUT, (32, 32), (30, 40)); line(s, OUT, (30, 40), (32, 46)); line(s, OUT, (14, 40), (15, 45))    # robe cracks
    s.set_at((40, 4), (0, 0, 0, 0)); s.set_at((40, 5), OUT); s.set_at((29, 3), (0, 0, 0, 0))                # chipped orb + crown point
    for k in range(30):                                                                                  # moss: plinth top, robe hem, shoulders, crown
        x, y = r.choice([(r.randrange(6, 42), r.randrange(44, 48)), (r.randrange(12, 36), r.randrange(46, 50)), (r.randrange(5, 12), r.randrange(55, 70)), (r.randrange(10, 16), r.randrange(21, 25)), (r.randrange(19, 23), r.randrange(4, 7))])
        if s.get_at((x, y)).a and s.get_at((x, y))[:3] != OUT: s.set_at((x, y), MOSS[k % 3]); s.set_at((x, y + 1), MOSS[0]) if s.get_at((x, y + 1)).a else None
    if necklace:
        for i in range(15):                                                                              # chain draped over the mantle, around the beard
            t = math.pi * i / 14; x, y = 24 - math.cos(t) * 11, 26 + math.sin(t) * 7
            s.set_at((round(x), round(y)), GOLD[2] if i % 2 else GOLD[3]); s.set_at((round(x), round(y) + 1), GOLD[0])
        pygame.draw.polygon(s, OUT, [(21, 32), (27, 32), (24, 37)]); pygame.draw.polygon(s, RUBY[2], [(22, 33), (26, 33), (24, 36)]); s.set_at((23, 33), RUBY[3]); s.set_at((25, 34), RUBY[1])
    return s
def glint(base, i):
    f = base.copy()
    if i in (1, 2):
        x, y = (23, 33) if i == 1 else (15, 30)
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
  "design": "the KING (issue #1): broad-shouldered, full curled beard, tall crown, heavy robe with an ermine fur mantle, sceptre in his right hand, left arm across the robe; weathered limestone with cracks, chips, moss; necklace draped over the mantle in the Necklace item gold + ruby", "backups": "queen original: statue_queen_necklace.png, statue_queen_plain.png, statue_queen_necklace_glint.png, make_statue_queen.py"},
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
Q = pygame.image.load(os.path.join(HERE, "statue_queen_necklace.png")); C = pygame.Surface((112 * Z * 2 + 30, 128 * Z + 20)); C.fill((40, 36, 48))
for k, img in enumerate((Q, A)):
    f = fl.copy(); f.blit(img, (fx * 16, (fy + 3) * 16 - FH)); C.blit(pygame.transform.scale(f.subsurface(crop), (112 * Z, 128 * Z)), (10 + k * (112 * Z + 10), 10))
pygame.image.save(C, os.path.join(HERE, "preview_compare.png"))
dst = os.path.join(GAME, "assets", "statue"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(HERE):
    if not f.startswith("preview"): shutil.copy(os.path.join(HERE, f), dst)
print("ok")
