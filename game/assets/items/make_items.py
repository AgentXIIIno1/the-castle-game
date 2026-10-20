"""Item sprites replacing the orb placeholder (art.make_item). python3 make_items.py
Floor sprite 16x16 (anchor bottom-centre 8,15, contact shadow baked), small 'drawer/shelf' 12x12 (anchor 6,11, no shadow), 4-frame glint strip for treasures."""
import os, sys, math, json, shutil; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *
from art import lerp
GOLD = [(110, 70, 24), (176, 124, 40), (226, 176, 72), (255, 232, 150)]
SILV = [(70, 74, 88), (120, 126, 142), (176, 182, 196), (236, 240, 248)]
WOOD = [(60, 38, 22), (96, 62, 36), (132, 90, 52), (170, 124, 76)]
def P(c, k=4): return [lerp(c, (10, 6, 14), .55), lerp(c, (10, 6, 14), .25), c, lerp(c, (255, 250, 240), .45)]
RUBY = P((196, 36, 52)); JADE = P((70, 160, 100)); BLUE = P((80, 150, 230)); GLASS = P((150, 200, 220)); WINE = P((120, 30, 60)); LEATH = P((120, 50, 40))
def px(s, pts, c):
    for p in pts: s.set_at(p, c)
def rect(s, c, r): pygame.draw.rect(s, c, r)
def gem(s, cx, cy, r, pal):
    """faceted gem: crown triangles over pavilion"""
    pygame.draw.polygon(s, pal[1], [(cx - r, cy - r // 2), (cx + r, cy - r // 2), (cx, cy + r)])
    pygame.draw.polygon(s, pal[2], [(cx - r + 1, cy - r // 2), (cx - r // 2, cy - r), (cx + r // 2, cy - r), (cx + r - 1, cy - r // 2)])
    pygame.draw.polygon(s, pal[0], [(cx, cy + r), (cx + r, cy - r // 2), (cx + 1, cy - r // 2)])
    line(s, pal[3], (cx - r // 2, cy - r + 1), (cx, cy - r + 1)); s.set_at((cx - r // 2, cy - r // 2 + 1), pal[3])
def bar(s, x, y, pal, w=10):
    pygame.draw.polygon(s, pal[1], [(x, y + 5), (x + w, y + 5), (x + w - 2, y + 1), (x + 2, y + 1)])
    rect(s, pal[2], (x + 2, y + 1, w - 4, 2)); line(s, pal[3], (x + 2, y + 1), (x + w - 3, y + 1)); rect(s, pal[0], (x, y + 5, w + 1, 2)); line(s, pal[1], (x, y + 5), (x + w, y + 5))
def D_book(s):
    pygame.draw.polygon(s, LEATH[1], [(2, 9), (11, 7), (14, 10), (5, 12)]); pygame.draw.polygon(s, LEATH[2], [(2, 8), (11, 6), (14, 9), (5, 11)])
    line(s, (230, 222, 200), (5, 12), (14, 10)); line(s, (200, 190, 170), (5, 13), (14, 11)); line(s, LEATH[0], (2, 9), (5, 13))
    line(s, GOLD[2], (6, 9), (10, 8)); s.set_at((8, 8), GOLD[3]); line(s, LEATH[3], (3, 8), (10, 6))
def D_crown(s):
    rect(s, GOLD[1], (3, 8, 10, 5)); pygame.draw.polygon(s, GOLD[2], [(3, 8), (3, 3), (5, 6), (8, 2), (11, 6), (13, 3), (13, 8)])
    line(s, GOLD[3], (4, 8), (12, 8)); line(s, GOLD[0], (3, 12), (12, 12)); px(s, [(3, 3), (8, 2), (13, 3)], GOLD[3])
    s.set_at((8, 10), RUBY[2]); s.set_at((5, 10), BLUE[2]); s.set_at((11, 10), JADE[2]); s.set_at((8, 9), RUBY[3])
def D_crystal_ball(s):
    rect(s, WOOD[1], (4, 11, 8, 3)); line(s, WOOD[3], (4, 11), (11, 11)); line(s, WOOD[0], (4, 13), (11, 13))
    blob(s, 8, 7, 5, 5, [(70, 60, 140), (110, 100, 190), (160, 150, 230), (220, 214, 255)])
    px(s, [(6, 4), (5, 5), (6, 5)], (250, 248, 255)); s.set_at((10, 9), (90, 80, 160))
def D_diamond(s): gem(s, 8, 8, 5, GLASS)
def D_glasses(s):
    for cx in (4, 11):
        pygame.draw.circle(s, SILV[2], (cx, 9), 3, 1); pygame.draw.circle(s, (160, 200, 220), (cx, 9), 2); s.set_at((cx - 1, 8), (240, 250, 255))
    line(s, SILV[3], (6, 8), (9, 8)); line(s, SILV[1], (1, 8), (0, 6)); line(s, SILV[1], (14, 8), (15, 6))
def D_goldbar(s): bar(s, 3, 6, GOLD)
def D_harp(s):
    pygame.draw.polygon(s, GOLD[1], [(3, 13), (4, 2), (6, 2), (5, 13)])                        # pillar
    pygame.draw.arc(s, GOLD[2], (3, 1, 12, 10), 0, math.pi, 2); line(s, GOLD[2], (13, 6), (12, 13), 2); line(s, GOLD[1], (4, 13), (12, 13), 2)
    for x in range(6, 12, 2): line(s, (230, 226, 210), (x, 4 + (x - 6) // 3), (x, 12))
    line(s, GOLD[3], (4, 2), (4, 10)); s.set_at((9, 2), GOLD[3])
def D_holy_cross(s):
    rect(s, GOLD[1], (7, 2, 3, 12)); rect(s, GOLD[1], (3, 5, 11, 3)); line(s, GOLD[3], (7, 2), (7, 13)); line(s, GOLD[3], (3, 5), (13, 5))
    line(s, GOLD[0], (9, 8), (9, 13)); s.set_at((8, 6), RUBY[2])
def D_hourglass(s):
    rect(s, WOOD[2], (3, 2, 10, 2)); rect(s, WOOD[2], (3, 12, 10, 2)); line(s, WOOD[3], (3, 2), (12, 2)); line(s, WOOD[0], (3, 13), (12, 13))
    pygame.draw.polygon(s, (190, 220, 230), [(5, 4), (11, 4), (8, 8)]); pygame.draw.polygon(s, (190, 220, 230), [(8, 8), (11, 12), (5, 12)])
    pygame.draw.polygon(s, GOLD[2], [(6, 5), (10, 5), (8, 7)]); pygame.draw.polygon(s, GOLD[2], [(8, 10), (10, 12), (6, 12)]); s.set_at((8, 9), GOLD[3])
    line(s, WOOD[1], (4, 4), (4, 11)); line(s, WOOD[1], (12, 4), (12, 11)); s.set_at((6, 4), (250, 255, 255))
def D_jade_figurine(s):
    rect(s, JADE[0], (4, 12, 8, 2)); blob(s, 8, 9, 3.5, 3.5, JADE); blob(s, 8, 4, 2.6, 2.6, JADE)
    s.set_at((7, 4), JADE[0]); s.set_at((9, 4), JADE[0]); px(s, [(6, 7), (7, 2)], JADE[3])
def D_key(s):
    pygame.draw.circle(s, GOLD[2], (5, 6), 3, 2); line(s, GOLD[2], (7, 8), (13, 12), 2); line(s, GOLD[2], (11, 11), (10, 13)); line(s, GOLD[2], (13, 12), (12, 14))
    s.set_at((4, 4), GOLD[3]); line(s, GOLD[3], (8, 8), (12, 11))
def D_large_gem(s): gem(s, 8, 8, 6, BLUE)
def D_magic_wand(s):
    line(s, (40, 30, 50), (3, 13), (11, 5), 2); line(s, (90, 70, 110), (3, 12), (10, 5))
    for d in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): s.set_at((12 + d[0], 4 + d[1]), (255, 240, 170))
    px(s, [(14, 2), (10, 2)], (255, 250, 220)); s.set_at((3, 13), SILV[2])
def D_necklace(s):
    for i in range(14):
        a = math.pi * (i / 13); x, y = 8 - math.cos(a) * 6, 4 + math.sin(a) * 6
        s.set_at((round(x), round(y)), GOLD[2] if i % 2 else GOLD[3])
    gem(s, 8, 11, 2, RUBY)
def D_ruby(s): gem(s, 8, 8, 4, RUBY); gem(s, 12, 11, 2, RUBY)
def D_scepter(s):
    line(s, GOLD[1], (3, 14), (11, 5), 2); line(s, GOLD[3], (3, 13), (10, 5))
    blob(s, 12, 4, 2.6, 2.6, GOLD); s.set_at((12, 3), RUBY[2]); s.set_at((12, 4), RUBY[2]); s.set_at((11, 3), RUBY[3])
    line(s, GOLD[2], (6, 9), (8, 11))
def D_silver_bars(s):
    for (x, y, w) in ((0, 7, 8), (7, 7, 8), (3, 2, 8)):          # stacked ingots, each outlined so they read separately
        t = surf(16, 16); bar(t, x, y, SILV, w); s.blit(outline(t), (0, 0))
def D_wine_flask(s):
    blob(s, 8, 10, 4.5, 3.5, LEATH); rect(s, LEATH[1], (7, 3, 3, 4)); rect(s, WOOD[2], (7, 2, 3, 2)); line(s, LEATH[3], (6, 8), (9, 8))
    line(s, (210, 190, 150), (4, 7), (12, 11)); s.set_at((5, 9), LEATH[3])
ITEMS = [  # id, name, drawer, treasure, rooms
 ("BOOK", "Book", D_book, False), ("CROWN", "Crown", D_crown, True), ("CRYSTAL_BALL", "Crystal Ball", D_crystal_ball, False), ("DIAMOND", "Diamond", D_diamond, True),
 ("GLASSES", "Eye Glasses", D_glasses, False), ("GOLDBAR", "Goldbar", D_goldbar, True), ("HARP", "Harp", D_harp, True), ("HOLY_CROSS", "Holy Cross", D_holy_cross, True),
 ("HOURGLASS", "Hourglass", D_hourglass, True), ("JADE_FIGURINE", "Jade Figurine", D_jade_figurine, True), ("KEY", "Key", D_key, False), ("LARGE_GEM", "Large Gem", D_large_gem, True),
 ("MAGIC_WAND", "Magic Wand", D_magic_wand, False), ("NECKLACE", "Necklace", D_necklace, True), ("RUBYS", "Ruby", D_ruby, True), ("SCEPTER", "Scepter", D_scepter, True),
 ("SILVER_BARS", "Silver Bars", D_silver_bars, True), ("WINE_FLASK", "Wine Flask", D_wine_flask, False)]
SH = (10, 8, 16)
def floor(fn):
    art_ = surf(16, 16); fn(art_); art_ = outline(art_)
    b = art_.get_bounding_rect(); s = surf(16, 16)
    for y in range(13, 16):                          # contact shadow ellipse under the sprite
        for x in range(16):
            d = ((x - 8) / (b.width / 2 + 1)) ** 2 + ((y - 14.5) / 1.6) ** 2
            if d <= 1 and (d < .5 or BAYER[y % 4][x % 4] / 16 > (d - .5) * 2): s.set_at((x, y), (*SH, 110))
    s.blit(art_, (8 - (b.x + b.width // 2), 14 - b.bottom + 1)); return s
def small(fn):
    a = surf(16, 16); fn(a); b = a.get_bounding_rect(); a = a.subsurface(b).copy()
    k = 10 / max(b.width, b.height); a = pygame.transform.scale(a, (max(1, round(b.width * k)), max(1, round(b.height * k))))
    s = surf(12, 12); s.blit(a, (6 - a.get_width() // 2, 11 - a.get_height())); return outline(s)
def glint(base, i):
    f = base.copy(); b = base.get_bounding_rect(); pos = [(b.x + 2, b.y + 2), (b.centerx, b.y + 1), (b.right - 3, b.y + 3), None][i]
    if pos:
        x, y = pos
        for d, a in (((0, 0), 255), ((1, 0), 180), ((-1, 0), 180), ((0, 1), 180), ((0, -1), 180)):
            q = (x + d[0], y + d[1])
            if 0 <= q[0] < 16 and 0 <= q[1] < 16 and f.get_at(q).a > 200: f.set_at(q, (255, 255, 240, a))
    return f
man = {"replaces": "art.make_item() orb placeholder (main.Game.item_sprite fallback). Lamp, Sword, Helmet and Fancy Goblet already have dedicated art and are not included.",
       "floor": {"frame_size": [16, 16], "anchor": [8, 15], "shadow_baked": True, "note": "anchor bottom-centre at the item's floor contact; game's bob can stay"},
       "small": {"frame_size": [12, 12], "anchor": [6, 11], "shadow_baked": False, "use": "on desk/shelf/statue tops, in drawers, inventory/HUD"},
       "glint": {"frame_size": [16, 16], "frames": 4, "fps": 6, "loop": True, "frame_durations_ms": [160, 160, 160, 600], "anchor": [8, 15], "shadow_baked": True, "note": "treasures only; frame 3 = rest"},
       "items": {}}
for iid, name, fn, tr in ITEMS:
    key = iid.lower(); f = floor(fn); sm = small(fn)
    pygame.image.save(f, os.path.join(HERE, f"{key}.png")); pygame.image.save(sm, os.path.join(HERE, f"{key}_small.png"))
    ent = {"name": name, "treasure": tr, "floor": f"{key}.png", "small": f"{key}_small.png"}
    if tr:
        S = surf(64, 16)
        for i in range(4): S.blit(glint(f, i), (i * 16, 0))
        pygame.image.save(S, os.path.join(HERE, f"{key}_glint.png")); ent["glint"] = f"{key}_glint.png"
    man["items"][iid] = ent
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
font = pygame.font.Font(None, 16); Z = 4; cw = 16 * Z + 12 * Z + 30
P_ = pygame.Surface((6 * (cw + 10) + 10, 3 * (16 * Z + 40) + 10)); P_.fill((40, 36, 48))
for i, (iid, name, fn, tr) in enumerate(ITEMS):
    X, Y = 10 + (i % 6) * (cw + 10), 10 + (i // 6) * (16 * Z + 40)
    P_.blit(font.render(name + (" *" if tr else ""), True, (255, 220, 140) if tr else (230, 220, 200)), (X, Y))
    for k, (f, sz) in enumerate(((f"{iid.lower()}.png", 16), (f"{iid.lower()}_small.png", 12))):
        im = pygame.image.load(os.path.join(HERE, f)); b = pygame.Surface(im.get_size()); b.fill((70, 64, 56)); b.blit(im, (0, 0))
        P_.blit(pygame.transform.scale(b, (sz * Z, sz * Z)), (X + k * (16 * Z + 8), Y + 16))
        P_.blit(b, (X + 16 * Z + 8 + 12 * Z - 16 + (k * 18) - 0, Y + 16 + 12 * Z + 4)) if False else P_.blit(b, (X + k * 18, Y + 16 + 16 * Z + 2 - 18 + 18)) if False else None
    im = pygame.image.load(os.path.join(HERE, f"{iid.lower()}.png")); b = pygame.Surface((16, 16)); b.fill((70, 64, 56)); b.blit(im, (0, 0)); P_.blit(b, (X + 16 * Z + 8 + 12 * Z + 6, Y + 16))
pygame.image.save(P_, os.path.join(HERE, "preview.png"))
dst = os.path.join(GAME, "assets", "items"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(HERE):
    if not f.startswith("preview"): shutil.copy(os.path.join(HERE, f), dst)
print("ok")
