"""v2 art: 3/4 top-down pixel tiles baked in code at native res (16px tiles), nearest-neighbour upscaled by the presenter."""
import math, random
import pygame
import gfx

T, COLS, ROWS = 16, 24, 18
CAP = 6            # how far wall tops are raised (px) -> visible front face of this height
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def dither_fill(s, rect, c1, c2, rnd, amount=.5, noise=.35):
    """ordered-dither blend of two colours with per-pixel noise"""
    x0, y0, w, h = rect
    for y in range(y0, y0+h):
        for x in range(x0, x0+w):
            v = amount + (rnd.random()-.5)*noise
            s.set_at((x, y), c2 if v*16 > BAYER[y % 4][x % 4] else c1)

# ---------- palettes
STONE = dict(top=(98, 94, 106), top2=(70, 66, 80), face=(104, 98, 108), face2=(70, 66, 78), mortar=(30, 28, 38),
             rim=(156, 150, 160), moss=(72, 98, 52), moss2=(96, 126, 60))
GRASS = ((58, 90, 38), (76, 112, 44), (118, 150, 62), (36, 58, 28))
DIRT = ((92, 66, 44), (112, 82, 54))
FLAG = ((74, 64, 60), (86, 74, 66), (54, 46, 46), (110, 96, 84))

VOID = (255, 0, 255)   # colour-key: background swirl shows through outside the walls

def is_wall(g, x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and g[y][x] in "#="

def bake_floor(room, rnd, garden):
    s = gfx.rgb((COLS*T, ROWS*T))
    if garden:
        dither_fill(s, (0, 0, COLS*T, ROWS*T), GRASS[0], GRASS[1], rnd, .45, .9)
        for _ in range(60):   # darker clumps
            cx, cy = rnd.randrange(COLS*T), rnd.randrange(ROWS*T)
            for k in range(14): s.set_at(((cx+rnd.randrange(-4, 5)) % (COLS*T), (cy+rnd.randrange(-3, 4)) % (ROWS*T)), GRASS[3])
        for _ in range(9):   # dirt patches
            cx, cy, r = rnd.randrange(COLS*T), rnd.randrange(ROWS*T), rnd.randrange(6, 16)
            for y in range(cy-r, cy+r):
                for x in range(cx-r*2, cx+r*2):
                    d = ((x-cx)/(2*r))**2 + ((y-cy)/r)**2
                    if 0 <= x < COLS*T and 0 <= y < ROWS*T and d < 1 and (1-d)*16 > BAYER[y % 4][x % 4]*.9:
                        s.set_at((x, y), DIRT[d < .4])
        for _ in range(900):  # grass blades with highlight
            x, y = rnd.randrange(COLS*T), rnd.randrange(2, ROWS*T)
            s.set_at((x, y), GRASS[2]); s.set_at((x, y-1), GRASS[2] if rnd.random() < .5 else GRASS[1]); s.set_at((x, y+1), GRASS[3]); s.set_at((x+1 if x+1 < COLS*T else x, y+1), GRASS[3])
    else:   # open-air courtyard: packed earth with worn cobbles and weeds
        dither_fill(s, (0, 0, COLS*T, ROWS*T), (64, 52, 46), (76, 62, 52), rnd, .45, .8)
        for _ in range(260):
            cx, cy = rnd.randrange(COLS*T), rnd.randrange(ROWS*T)
            r = rnd.choice((2, 3, 3, 4))
            base = FLAG[rnd.randrange(2)]
            pygame.draw.ellipse(s, (34, 28, 30), (cx-r-1, cy-r+1, 2*r+2, 2*r))
            pygame.draw.ellipse(s, base, (cx-r, cy-r, 2*r, 2*r-1))
            s.set_at((cx-r+1, cy-r+1), FLAG[3]); s.set_at((cx-r+2, cy-r+1), FLAG[3])
        for _ in range(140):
            x, y = rnd.randrange(COLS*T), rnd.randrange(1, ROWS*T)
            s.set_at((x, y), (88, 110, 52)); s.set_at((x, y-1), (110, 136, 60))
    return s

def ao(s, g):
    """ambient occlusion / cast shadows from walls onto the floor"""
    sh = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    for y in range(ROWS):
        for x in range(COLS):
            if is_wall(g, x, y): continue
            X, Y = x*T, y*T
            if False:
                for k in range(10): pygame.draw.line(sh, (10, 8, 20, 150 - k*14), (X, Y+k), (X+T-1, Y+k))
            if is_wall(g, x-1, y):
                for k in range(7): pygame.draw.line(sh, (10, 8, 20, 160 - k*22), (X+k, Y), (X+k, Y+T-1))
            if is_wall(g, x+1, y):
                for k in range(4): pygame.draw.line(sh, (10, 8, 20, 70 - k*16), (X+T-1-k, Y), (X+T-1-k, Y+T-1))
    s.blit(sh, (0, 0))

FACE = 14   # front-face height projected onto the tile below

def stones(s, rect, base, dark, light, mortar, rnd, sw=8, sh=5):
    """irregular chunky stones with dark mortar outline and top-left rim highlight"""
    x0, y0, w, h = rect
    clip = s.get_clip(); s.set_clip(rect)
    y, row = y0, 0
    while y < y0 + h:
        hh = sh + rnd.choice((0, 0, 1))
        x = x0 - (row % 2) * (sw // 2) - rnd.randrange(0, 2)
        while x < x0 + w:
            ww = sw + rnd.choice((-1, 0, 1, 2))
            r = pygame.Rect(x, y, ww, hh)
            tone = lerp(base, dark, rnd.random()*.45) if rnd.random() < .7 else lerp(base, light, rnd.random()*.3)
            dither_fill(s, r.clip(rect), tone, dark, rnd, .25, .5)
            pygame.draw.line(s, lerp(tone, light, .55), (r.x+1, r.y+1), (r.right-2, r.y+1))
            pygame.draw.line(s, lerp(tone, light, .3), (r.x+1, r.y+1), (r.x+1, r.bottom-2))
            pygame.draw.rect(s, mortar, r, 1)
            x += ww
        y += hh; row += 1
    s.set_clip(clip)

def draw_wall(s, g, x, y, rnd, garden):
    X, Y = x*T, y*T
    ink = (14, 10, 20)
    stones(s, pygame.Rect(X, Y, T, T), STONE["top"], STONE["top2"], STONE["rim"], (34, 30, 42), rnd)
    if not is_wall(g, x, y-1): pygame.draw.line(s, STONE["rim"], (X, Y), (X+T-1, Y))
    if not is_wall(g, x-1, y): pygame.draw.line(s, ink, (X, Y), (X, Y+T-1))
    if not is_wall(g, x+1, y): pygame.draw.line(s, ink, (X+T-1, Y), (X+T-1, Y+T-1))
    if not is_wall(g, x, y-1): pygame.draw.line(s, ink, (X, Y-1), (X+T-1, Y-1)) if Y > 0 else None
    for _ in range(rnd.randrange(1, 5) if garden else rnd.randrange(0, 2)):   # moss on tops
        mx, my = X + rnd.randrange(1, T-2), Y + rnd.randrange(1, T-2)
        for d in ((0, 0), (1, 0), (0, 1), (1, 1), (2, 0)):
            if rnd.random() < .8: s.set_at((mx+d[0], my+d[1]), STONE["moss2"] if d[1] == 0 else STONE["moss"])

def draw_face(s, g, x, y, rnd, garden):
    """front face of a wall, projected down onto the open tile below"""
    if y+1 >= ROWS or is_wall(g, x, y+1): return
    X, Y = x*T, (y+1)*T
    r = pygame.Rect(X, Y, T, FACE)
    stones(s, r, STONE["face"], STONE["face2"], (110, 104, 120), (22, 20, 30), rnd, 8, 4)
    pygame.draw.line(s, STONE["rim"], (X, Y), (X+T-1, Y))                 # lit top edge
    pygame.draw.line(s, (14, 10, 20), (X, Y+FACE), (X+T-1, Y+FACE))       # base outline
    if not is_wall(g, x-1, y): pygame.draw.line(s, (14, 10, 20), (X, Y), (X, Y+FACE))
    if not is_wall(g, x+1, y): pygame.draw.line(s, (14, 10, 20), (X+T-1, Y), (X+T-1, Y+FACE))
    if garden or rnd.random() < .3:                                        # moss drips down the face
        for _ in range(rnd.randrange(1, 4)):
            mx = X + rnd.randrange(T); l = rnd.randrange(2, FACE)
            for k in range(l): s.set_at((mx, Y+1+k), STONE["moss"] if k else STONE["moss2"])
    sh = pygame.Surface((T, 6), pygame.SRCALPHA)                           # contact shadow
    for k in range(6): pygame.draw.line(sh, (8, 6, 16, 150 - k*25), (0, k), (T, k))
    s.blit(sh, (X, Y+FACE+1))

def draw_gate(s, g, x, y, rnd):
    _gate(s, g, x, y, rnd)
    if not is_gate(g, x-1, y) or not is_gate(g, x+1, y):     # stone gate posts either side
        px_ = x*T - 6 if not is_gate(g, x-1, y) else x*T + T - 2
        stones(s, pygame.Rect(px_, y*T - 10, 8, T + 10), (120, 114, 124), (80, 76, 90), (170, 164, 176), (20, 18, 28), rnd, 4, 4)
        pygame.draw.rect(s, (14, 10, 20), (px_, y*T - 10, 8, T + 10), 1)

def is_gate(g, x, y): return 0 <= x < COLS and g[y][x] == "="

def _gate(s, g, x, y, rnd):
    """portcullis set in the wall: dark opening, iron bars, timber lintel"""
    X, Y = x*T, y*T - 8
    pygame.draw.rect(s, (10, 8, 16), (X, Y, T, T+8))
    for bx in range(2, T, 4):
        pygame.draw.line(s, (130, 134, 146), (X+bx, Y+3), (X+bx, Y+T+7))
        pygame.draw.line(s, (36, 38, 48), (X+bx+1, Y+3), (X+bx+1, Y+T-1))
        s.set_at((X+bx, Y+3), (190, 196, 206))
    pygame.draw.line(s, (110, 114, 126), (X, Y+9), (X+T-1, Y+9))
    pygame.draw.rect(s, (104, 70, 40), (X, Y, T, 3)); pygame.draw.line(s, (150, 108, 64), (X, Y), (X+T-1, Y))
    pygame.draw.line(s, (14, 10, 20), (X, Y+3), (X+T-1, Y+3))

def bake_room(rid, room):
    rnd = random.Random(rid * 7919)
    g = room["grid"]; garden = "GARDEN" in (room.get("const") or "")
    s = bake_floor(room, rnd, garden)
    ao(s, g)
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] == " " and not room["walk"][y][x]:
                s.fill(VOID, (x*T, y*T, T, T))
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] == "#": draw_wall(s, g, x, y, rnd, garden)
            elif g[y][x] == "=": draw_gate(s, g, x, y, rnd)
    for y in range(ROWS):
        for x in range(COLS):
            if g[y][x] in "#=": draw_face(s, g, x, y, rnd, garden)
    return s

def near_wall_above(g, x, y): return is_wall(g, x, y+1)  # keep space above a wall for the raised cap

# ---------- props & sprites (SRCALPHA, outlined)
def outline(s, col=(14, 10, 20)):
    m = pygame.mask.from_surface(s)
    o = pygame.Surface((s.get_width()+2, s.get_height()+2), pygame.SRCALPHA)
    ms = m.to_surface(setcolor=col, unsetcolor=(0, 0, 0, 0))
    for d in ((0, 1), (2, 1), (1, 0), (1, 2)): o.blit(ms, d)
    o.blit(s, (1, 1)); return o

def shade_blob(s, cx, cy, r, dark, mid, light, rnd, ry=None):
    """dithered sphere-ish shading lit from the top-left"""
    ry = ry or r
    for y in range(int(cy-ry), int(cy+ry)+1):
        for x in range(int(cx-r), int(cx+r)+1):
            dx, dy = (x-cx)/r, (y-cy)/ry
            d = dx*dx + dy*dy
            if d > 1 or not s.get_rect().collidepoint(x, y): continue
            l = (-dx*.6 - dy*.8) * .5 + .5 + (rnd.random()-.5)*.25
            th = BAYER[y % 4][x % 4]/16
            col = light if l > .78 + th*.1 else mid if l > .35 + th*.2 else dark
            s.set_at((x, y), col)

def make_bush(big, seed):
    rnd = random.Random(seed)
    w = 28 if big else 20
    s = pygame.Surface((w, w), pygame.SRCALPHA)
    dark, mid, light = (30, 58, 30), (52, 96, 44), (104, 150, 66)
    for _ in range(8 if big else 5):
        r = rnd.randrange(5, 9 if big else 7)
        shade_blob(s, rnd.randrange(r, w-r), rnd.randrange(r+1, w-r), r, dark, mid, light, rnd)
    for _ in range(10):
        x, y = rnd.randrange(w), rnd.randrange(w)
        if s.get_at((x, y)).a: s.set_at((x, y), (150, 190, 90))
    return outline(s)

def make_snake():
    rnd = random.Random(5)
    s = pygame.Surface((22, 20), pygame.SRCALPHA)
    dark, mid, light = (28, 64, 34), (58, 112, 50), (128, 170, 80)
    # coils (back to front)
    for cy, r in ((14, 8), (11, 6)):
        pygame.draw.ellipse(s, dark, (11-r-2, cy-r//2-1, 2*r+4, r+3))
        shade_blob(s, 11, cy, r+1, dark, mid, light, rnd, ry=r//2+1)
        pygame.draw.ellipse(s, dark, (11-r//2, cy-2, r, 3))
    # raised neck and head
    for i, (x, y) in enumerate(((14, 9), (15, 7), (16, 5), (16, 3))):
        pygame.draw.circle(s, mid, (x, y), 2); s.set_at((x-1, y-1), light)
    pygame.draw.ellipse(s, mid, (14, 0, 7, 5)); pygame.draw.line(s, light, (15, 0), (19, 0))
    s.set_at((18, 1), (230, 40, 40)); s.set_at((19, 1), (255, 120, 90))
    pygame.draw.line(s, (220, 50, 60), (21, 3), (21, 5)); s.set_at((20, 3), (220, 50, 60))
    for _ in range(12):  # scales
        x, y = rnd.randrange(4, 18), rnd.randrange(8, 19)
        if s.get_at((x, y))[:3] == mid: s.set_at((x, y), dark)
    return outline(s)

def make_lamp():
    s = pygame.Surface((14, 10), pygame.SRCALPHA)
    gd, gm, gl = (130, 86, 30), (214, 160, 60), (255, 230, 150)
    pygame.draw.ellipse(s, gm, (2, 3, 9, 6)); pygame.draw.line(s, gl, (4, 4), (7, 4))
    pygame.draw.line(s, gm, (10, 5), (13, 3)); s.set_at((13, 2), gl)   # spout
    pygame.draw.arc(s, gd, (0, 3, 4, 5), 1.5, 4.7)                        # handle
    pygame.draw.rect(s, gd, (4, 8, 5, 2)); pygame.draw.rect(s, gm, (5, 1, 3, 2)); s.set_at((6, 0), gl)
    pygame.draw.line(s, gd, (3, 7), (10, 7))
    return outline(s)

def make_goblet():
    s = pygame.Surface((10, 13), pygame.SRCALPHA)
    gd, gm, gl = (130, 86, 30), (214, 160, 60), (255, 230, 150)
    pygame.draw.rect(s, gm, (1, 0, 8, 5)); pygame.draw.line(s, gl, (2, 1), (2, 4)); pygame.draw.line(s, gd, (8, 0), (8, 4))
    pygame.draw.rect(s, gd, (2, 5, 6, 1)); pygame.draw.rect(s, gm, (4, 6, 2, 4)); pygame.draw.rect(s, gm, (1, 10, 8, 2))
    s.set_at((4, 2), (200, 40, 50)); s.set_at((5, 2), (240, 80, 90)); pygame.draw.line(s, gd, (1, 12), (8, 12))
    return outline(s)

def make_item(name):
    n = name.lower()
    if "lamp" in n: return make_lamp()
    if "goblet" in n: return make_goblet()
    s = pygame.Surface((10, 10), pygame.SRCALPHA); shade_blob(s, 5, 5, 4, (130, 86, 30), (214, 160, 60), (255, 230, 150), random.Random(1))
    return outline(s)

def club_shape(surf, cx, cy, r, col):
    """the playing-card club suit: three lobes + flared stem"""
    pygame.draw.circle(surf, col, (cx, cy - r), r)
    pygame.draw.circle(surf, col, (cx - r - r//3, cy + r//3), r)
    pygame.draw.circle(surf, col, (cx + r + r//3, cy + r//3), r)
    pygame.draw.rect(surf, col, (cx - r//2, cy - r//2, r, r))
    pygame.draw.polygon(surf, col, [(cx - 1, cy), (cx + 1, cy), (cx + r, cy + 2*r + 2), (cx - r, cy + 2*r + 2)])

def make_club_rug():
    """woven rug with a large playing-card club (the original game's player glyph)"""
    w, h = 4*T, 3*T
    rnd = random.Random(42)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    red, red2, cream, gold, ink = (124, 34, 44), (98, 24, 36), (232, 220, 190), (210, 164, 70), (24, 16, 22)
    pygame.draw.rect(s, red, (0, 2, w, h-4), border_radius=2)
    for y in range(2, h-2):            # weave texture
        for x in range(w):
            if (x // 2 + y) % 4 == 0 or rnd.random() < .08: s.set_at((x, y), red2)
    pygame.draw.rect(s, gold, (2, 4, w-4, h-8), 1)
    pygame.draw.rect(s, cream, (5, 7, w-10, h-14), 1, border_radius=3)   # card border
    for x in range(8, w-8, 4):                                           # border zigzag
        s.set_at((x, 5), cream); s.set_at((x+2, h-6), cream)
    club_shape(s, w//2+1, h//2 - 3, 5, ink)                                # shadowed big club
    club_shape(s, w//2 - 1, h//2 - 5, 5, cream)
    pip = ["01110", "01110", "11011", "11111", "11011", "00100", "01110"]
    for (cx, cy) in ((9, 9), (w-14, h-16)):                              # corner pips
        for yy, row in enumerate(pip):
            for xx, b in enumerate(row):
                if b == "1": s.set_at((cx+xx, cy+yy), cream)
    for x in range(0, w, 2):                                             # fringe
        s.set_at((x, 0), cream); s.set_at((x, 1), cream); s.set_at((x, h-1), cream); s.set_at((x, h-2), cream)
    return s

def shadow(w):
    s = pygame.Surface((w, max(4, w//3)), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (8, 6, 16, 120), s.get_rect())
    pygame.draw.ellipse(s, (8, 6, 16, 80), s.get_rect().inflate(4, 2)) if False else None
    return s

def light(radius, col):
    """additive warm light, dithered falloff"""
    s = gfx.rgb((radius*2, radius*2))
    s.fill((0, 0, 0))
    for y in range(radius*2):
        for x in range(radius*2):
            d = math.hypot(x-radius, y-radius) / radius
            if d < 1:
                k = (1-d)**2 + (BAYER[y % 4][x % 4]/16 - .5)*.06
                s.set_at((x, y), tuple(max(0, min(255, int(c*k))) for c in col))
    return s

def vignette(size):
    w, h = size
    s = gfx.rgb(size)
    for y in range(h):
        for x in range(0, w, 2):
            dx, dy = (x - w/2)/(w/2), (y - h/2)/(h/2)
            v = max(0, 1 - (dx*dx*.55 + dy*dy*.7))**.6
            v = 0.35 + 0.65*v + (BAYER[y % 4][x % 4]/16 - .5)*.03
            c = int(255*min(1, v)); pygame.draw.line(s, (c, c, min(255, c+8)), (x, y), (x+1, y))
    return s

def make_torch():
    s = pygame.Surface((6, 12), pygame.SRCALPHA)
    pygame.draw.rect(s, (90, 60, 36), (2, 5, 2, 7)); pygame.draw.rect(s, (60, 60, 70), (1, 5, 4, 2))
    pygame.draw.ellipse(s, (240, 140, 40), (0, 0, 6, 7)); pygame.draw.ellipse(s, (255, 230, 140), (2, 2, 2, 4))
    return outline(s)
