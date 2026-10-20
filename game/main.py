"""A tribute to Castle Adventure by Kevin Bales (1984). First playable slice.
Run: pip install pygame ; python main.py      (--shots to auto-save screenshots)"""
import itertools, os, sys, json, math, random, re
import pygame
import gfx
import decor
import setpiece
import art, art3, pixfont
try:
    import numpy as np
except Exception:      # numpy optional: pure-pygame fallbacks below
    np = None

HERE = os.path.dirname(os.path.abspath(__file__))
try: THEMES = json.load(open(os.path.join(HERE, "data", "room_themes.json")))
except Exception: THEMES = {}
DRAWER_ROOMS = (40, 56)   # desk drawers (remake visual): Yellow Room glasses, King's Study key
KEEP_ART = ("lamp", "sword", "helmet", "goblet")
DATA = os.path.join(HERE, "data")
T = 16                      # tile px (internal)
COLS, ROWS = 24, 18
W, H = 640, 360             # internal resolution (grows with the window, see set_frame)
BASE_W, BASE_H = 640, 360   # today's framing; windows smaller than BASE*SCALE keep it (scaled to fit)
SCALE = 2
ROOM_X, ROOM_Y = 128, 14
ZOOM = 2
VIEW = pygame.Rect(56, 6, 528, 292)     # room origin on internal surface
PANEL = pygame.Rect(40, 304, 560, 50)

def set_frame(sw, sh):
    """issue #29: keep the on-screen pixel size (SCALE screen px per internal px, ZOOM internal px per art px)
    and grow the internal frame to window/SCALE so bigger windows show more of the room. HUD and the text panel
    stay anchored to the screen edges. Below BASE*SCALE the old 640x360 frame is kept and scaled to fit."""
    global W, H, VIEW, PANEL
    if sw < BASE_W * SCALE or sh < BASE_H * SCALE: W, H = BASE_W, BASE_H
    else: W, H = sw // SCALE, sh // SCALE
    VIEW = pygame.Rect(56, 6, W - 112, H - 68)
    PANEL = pygame.Rect(40, H - 56, W - 80, 50)
    return W, H

# ---------------- window settings (fullscreen / size), stored in the user config dir ----------------
def settings_path():
    if sys.platform == "darwin": base = os.path.expanduser("~/Library/Application Support")
    elif os.name == "nt": base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else: base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "the-castle", "settings.json")

def load_settings():
    try: return json.load(open(settings_path()))
    except Exception: return {}

def save_settings(s):
    try:
        os.makedirs(os.path.dirname(settings_path()), exist_ok=True)
        json.dump(s, open(settings_path(), "w"), indent=1)
    except Exception as e: print("[castle diag] could not save settings:", e)
SLICE = set(range(1, 84))      # the whole castle (84 = escaped)
DARK = set(range(68, 84))      # cellar, maze, passages, dungeon: unlit
DARK_ENTRY = {68, 82}          # original: "It's too dark to go that way!" without the LAMP
# room 67 mirror cells (1-based original positions converted to 0-based cells)
MIRROR_ROOM, LAB_ROOM = 67, 66
MIRROR_OPEN = [((18, y), " ") for y in range(6, 12)] + [((19, 8), " "), ((19, 9), " ")] + \
              [((x, y), "#") for x in range(19, 24) for y in (7, 10)]     # mirror column cleared, east wall opened, corridor walls to the edge
MIRROR_ARRIVE = (16, 9)                                                     # original ROW=10:COL=17 when coming back from the lab
TRAPS = {78: (17, (8, 9)), 76: (14, (12, 13))}   # room: (col, rows) 0-based
KB_ROOM = 74   # maze room with the carved KB letters (assets/kb_letters)
FURN = {"R": "W", "N": "W", "Y": "W", "P": "W", "B": "W", "K": "%", "_": "%", "^": "%", ">": "%", "{": "%"}
# clear typos in the original room data (original text kept in rooms.json; fixed here at load)
TYPOS = [("Anex", "Annex"), ("Batlement", "Battlement"), ("Toture", "Torture"), ("Entrace", "Entrance"), ("entrace", "entrance"),
         ("Sorcerers", "Sorcerer's"), ("Kings Dressing", "King's Dressing"), ("Kings room .", "King's room."), ("Kings Room", "King's Room"),
         ("Kings Dressing room", "King's Dressing room"), ("the Kings", "the King's"), ("arch ways", "archways"), ("There 2 door ways", "There are 2 doorways"),
         ("door ways", "doorways"), ("at on end", "at one end"), ("stair case", "staircase"), ("middle,and", "middle, and"),
         ("with the King It", "with the King. It"), ("Tower .", "Tower."), ("Cooridor", "Corridor")]
def fix_text(t):
    t = re.sub(r"'S\b", "'s", t)
    for a, b in TYPOS: t = t.replace(a, b)
    return re.sub(r"(\. )([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)
FOUNTAIN = ",-.|?`'"
  # rooms playable in this slice
DIRS = {"n": (0, -1, "north"), "s": (0, 1, "south"), "e": (1, 0, "east"), "w": (-1, 0, "west")}

# rich muted palette
C = dict(ink=(18, 14, 28), stone=(78, 74, 96), stone_hi=(120, 114, 140), stone_lo=(48, 44, 64),
         floor=(40, 46, 58), floor2=(46, 52, 66), gold=(232, 186, 82), red=(214, 78, 70), teal=(64, 178, 170),
         purple=(110, 74, 150), cream=(236, 226, 200), green=(120, 200, 120), brown=(112, 72, 46),
         hair=(96, 60, 34), skin=(214, 164, 124), leather=(130, 86, 52), cloak=(72, 58, 70), steel=(196, 204, 214))

# ---------------- data ----------------
def load_rooms():
    rooms = {r["id"]: r for r in json.load(open(os.path.join(DATA, "rooms.json")))["rooms"]}
    for rid, r in rooms.items():
        p = os.path.join(DATA, "rooms_layout", f"room_{rid:02d}.txt")
        grid = None
        if os.path.exists(p):
            lines = open(p).read().splitlines()
            i = next(k for k, l in enumerate(lines) if l.startswith("+"))
            grid = [l[1:1+COLS].ljust(COLS) for l in lines[i+1:i+1+ROWS]]
        r["name"] = fix_text(r["name"]); r["description"] = fix_text(r["description"])
        r["doors"] = [(m["col"]-1, m["row"]-1) for m in r.get("monsters", []) if m["name"] in ("Door", "")]
        r["monsters"] = [m for m in r.get("monsters", []) if m["name"] not in ("Door", "")]
        if grid:
            if rid == KB_ROOM:   # the maze's carved 'KB' (Kevin Bales): solid wall with letter decals, not a table and a bed
                r["kb_letters"] = [(x, y, c) for y, row in enumerate(grid) for x, c in enumerate(row) if c in "KB"]
                grid = ["".join("#" if c in "KB" else c for c in row) for row in grid]
            if rid == setpiece.TORTURE:   # the '{' chains are east-wall decals (setpiece.CHAIN_WALL): their cells are plain floor
                grid = [row.replace("{", " ") for row in grid]
            grid = ["".join("#" if c in "&;:" else FURN.get(c, " " if c == "M" else c) for c in row) for row in grid]
            for dx_, dy_ in r["doors"]: grid[dy_] = grid[dy_][:dx_] + "G" + grid[dy_][dx_+1:]
        r["grid"] = grid
        if grid: r["walk"] = flood(grid, r.get("exits", {}))
        r["items"] = [dict(it) for it in r.get("items", [])]
        for it in r["items"]:
            it["x"], it["y"] = it["col"]-1, it["row"]-1
        r["theme"] = THEMES.get(str(rid), {})                              # per-room tile/decor theme overrides (data/room_themes.json)
        r["hidden"] = [it for it in r["items"] if it.get("hidden")]      # revealed by LOOK/SEARCH <feature>
        r["items"] = [it for it in r["items"] if not it.get("hidden")]
        r["mons"] = [dict(m, x=m["col"]-1, y=m["row"]-1, alive=True, mt=0.0, flash=0.0) for m in r.get("monsters", [])]
    return rooms

def load_cfg(mode):
    """per-mode mechanics; each leaf is {"value": x, "src": ...}"""
    def flat(d):
        if isinstance(d, dict): return d["value"] if "value" in d else {k: flat(v) for k, v in d.items()}
        return d
    return flat(json.load(open(os.path.join(HERE, "config", f"{mode}.json"))))

MODES = ["classic", "modern"]

def flood(g, exits=None):
    """walkable = open tiles reachable from room centre; edge tiles are exits and end the fill"""
    walk = [[False]*COLS for _ in range(ROWS)]
    walls = [(x, y) for y in range(ROWS) for x in range(COLS) if g[y][x] == "#"] or [(11.5, 8.5)]
    cx = sum(w[0] for w in walls)/len(walls); cy = sum(w[1] for w in walls)/len(walls)   # centre of the walls, not the grid
    start = min(((abs(x-cx)+abs(y-cy), x, y) for y in range(ROWS) for x in range(COLS) if g[y][x] == " "))
    st = [start[1:]]; seeds = []
    # also seed from doorway gaps on exit edges (gap bounded by walls), so winding passages work
    sides = {"north": [(x, 0, 1, 0) for x in range(COLS)], "south": [(x, ROWS-1, 1, 0) for x in range(COLS)],
             "west": [(0, y, 0, 1) for y in range(ROWS)], "east": [(COLS-1, y, 0, 1) for y in range(ROWS)]}
    for side, cells in sides.items():
        if not (exits or {}).get(side): continue
        line = "".join(g[y][x] for x, y, _, _ in cells)
        for mm in re.finditer(r"(?<=[#=])( +)(?=[#=])", line):
            for k in range(mm.start(1), mm.end(1)): seeds.append(cells[k][:2])
    for y in range(ROWS):          # stairs are entry points too
        for x in range(COLS):
            if g[y][x] in "UD":
                seeds += [(x+dx, y+dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x+dx < COLS and 0 <= y+dy < ROWS]
    if seeds: st = seeds
    while st:
        x, y = st.pop()
        if walk[y][x] or g[y][x] != " ": continue
        walk[y][x] = True
        if x in (0, COLS-1) or y in (0, ROWS-1):     # edge (exit) tile: only step straight inward
            nx, ny = x + (x == 0) - (x == COLS-1), y + (y == 0) - (y == ROWS-1)
            if (nx, ny) != (x, y) and 0 <= nx < COLS and 0 <= ny < ROWS and not (nx in (0, COLS-1) and ny in (0, ROWS-1)): st.append((nx, ny))
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < COLS and 0 <= ny < ROWS: st.append((nx, ny))
    return walk

def solid(room, x, y):
    if not (0 <= x < COLS and 0 <= y < ROWS): return False
    ch = room["grid"][y][x]
    return ch in "#=*+UD$%@W[]G" + FOUNTAIN or not room["walk"][y][x]

# ---------------- procedural art ----------------
def px(surf, col, rects):
    for r in rects: pygame.draw.rect(surf, col, r)

def make_hero(frame):
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    bob = frame % 2
    # ragged cloak behind
    px(s, C["cloak"], [(3, 6, 9, 9), (2, 13, 2, 3), (6, 14, 2, 3), (10, 13, 2, 3)])
    px(s, C["ink"], [(4, 15, 1, 1), (9, 16, 1, 1)])
    # legs / boots
    px(s, (60, 44, 34), [(5, 13, 2, 3 - bob), (9, 13, 2, 2 + bob)])
    px(s, C["ink"], [(5, 16 - bob, 3, 1), (9, 15 + bob, 3, 1)])
    # leather jerkin + belt
    px(s, C["leather"], [(4, 7, 8, 6)])
    px(s, (160, 112, 70), [(5, 8, 1, 4)])
    px(s, C["ink"], [(4, 11, 8, 1)]); px(s, C["gold"], [(7, 11, 1, 1)])
    # head, stubble
    px(s, C["skin"], [(5, 2, 6, 5)])
    px(s, (150, 112, 90), [(5, 5, 6, 2)])
    px(s, C["ink"], [(6, 4, 1, 1), (9, 4, 1, 1)])
    # long messy hair
    px(s, C["hair"], [(4, 1, 8, 2), (3, 2, 2, 6), (11, 2, 2, 5), (4, 0, 3, 1), (8, 0, 3, 1), (12, 3, 1, 1), (2, 6, 1, 2)])
    px(s, (130, 86, 50), [(6, 1, 2, 1), (10, 2, 1, 1)])
    # arm + sword
    px(s, C["skin"], [(12, 8, 2, 2)])
    px(s, C["steel"], [(14, 1 + bob, 1, 8)]); px(s, (255, 255, 255), [(14, 1 + bob, 1, 2)])
    px(s, C["gold"], [(13, 9 + bob, 3, 1)]); px(s, C["brown"], [(14, 10 + bob, 1, 2)])
    return s

def make_backpack():
    """ placeholder until the art set's backpack sprite lands (assets/items: manifest entry or backpack.png wins)"""
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    px(s, (96, 64, 38), [(2, 3, 8, 8)]); px(s, (128, 88, 52), [(3, 4, 6, 3)]); px(s, (70, 46, 28), [(3, 1, 6, 2), (2, 8, 8, 1)])
    px(s, C["gold"], [(5, 6, 2, 1)])
    return outline(s)

def make_chainmail():
    """ placeholder until the art set's chain mail lands (assets/chain_mail/manifest.json "item" wins)"""
    s = pygame.Surface((14, 13), pygame.SRCALPHA)
    px(s, (112, 116, 124), [(3, 1, 8, 11), (1, 2, 2, 5), (11, 2, 2, 5)]); px(s, (150, 154, 162), [(4, 2, 6, 1), (4, 5, 6, 1), (4, 8, 6, 1)])
    px(s, (70, 72, 82), [(5, 1, 4, 2), (3, 11, 8, 1)])
    return outline(s)

def outline(s, col=C["ink"]):
    m = pygame.mask.from_surface(s)
    o = pygame.Surface((s.get_width()+2, s.get_height()+2), pygame.SRCALPHA)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        o.blit(m.to_surface(setcolor=col, unsetcolor=(0, 0, 0, 0)), (dx, dy))
    o.blit(s, (1, 1)); return o

def make_item(name):
    s = pygame.Surface((14, 14), pygame.SRCALPHA)
    n = name.lower()
    if "goblet" in n:
        px(s, C["gold"], [(3, 2, 8, 4), (4, 6, 6, 1), (6, 7, 2, 4), (3, 11, 8, 2)])
        px(s, (255, 236, 160), [(4, 3, 2, 2)]); px(s, C["red"], [(6, 4, 2, 1)])
    elif "flask" in n:
        px(s, C["purple"], [(3, 5, 8, 7)]); px(s, C["cream"], [(5, 1, 4, 4)]); px(s, (200, 140, 230), [(4, 6, 2, 2)])
    else:
        pygame.draw.circle(s, C["gold"], (7, 7), 5); px(s, (255, 240, 170), [(5, 4, 2, 2)])
    return outline(s)

def make_ogre():
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    px(s, (92, 120, 70), [(3, 2, 10, 8), (2, 9, 12, 7), (1, 10, 2, 4), (13, 10, 2, 4)])
    px(s, C["ink"], [(5, 5, 2, 2), (9, 5, 2, 2), (5, 8, 6, 1)])
    px(s, C["cream"], [(5, 8, 1, 2), (10, 8, 1, 2)]); px(s, C["red"], [(5, 5, 1, 1), (9, 5, 1, 1)])
    px(s, (70, 50, 40), [(3, 15, 4, 3), (9, 15, 4, 3)])
    return outline(s)

def make_rug():
    """the original ASCII club, reborn as a woven rug (4x2 tiles)"""
    w, h = 4*T, 2*T
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (120, 40, 52), (0, 0, w, h), border_radius=3)
    for y in range(2, h-2):
        for x in range(2, w-2):
            if (x + y) % 4 == 0: s.set_at((x, y), (150, 58, 66))
    pygame.draw.rect(s, C["gold"], (2, 2, w-4, h-4), 1)
    # woven club motif
    cx, cy = w//2, h//2
    px(s, C["cream"], [(cx-14, cy-1, 18, 3)])
    px(s, C["cream"], [(cx+2, cy-4, 10, 9)]); px(s, C["gold"], [(cx+4, cy-6, 2, 2), (cx+8, cy+5, 2, 2), (cx+12, cy-1, 2, 2)])
    px(s, (90, 60, 40), [(cx-16, cy-1, 3, 3)])
    for x in range(0, w, 3):          # fringe
        s.set_at((x, 0), C["cream"]); s.set_at((x, h-1), C["cream"])
    return s

def draw_room(rid, room, t):
    s = pygame.Surface((COLS*T, ROWS*T), pygame.SRCALPHA)
    g = room["grid"]
    rnd = random.Random(rid)
    for y in range(ROWS):
        for x in range(COLS):
            r = pygame.Rect(x*T, y*T, T, T)
            ch = g[y][x]
            if ch == "#":
                pygame.draw.rect(s, C["stone"], r)
                off = 0 if y % 2 else 8
                pygame.draw.line(s, C["stone_lo"], (r.x, r.y+7), (r.right, r.y+7))
                pygame.draw.line(s, C["stone_lo"], (r.x+off, r.y), (r.x+off, r.y+7))
                pygame.draw.line(s, C["stone_lo"], (r.x+(8-off), r.y+8), (r.x+(8-off), r.bottom))
                pygame.draw.line(s, C["stone_hi"], r.topleft, (r.right-1, r.y))
                pygame.draw.rect(s, C["stone_lo"], (r.x, r.bottom-1, T, 1))
            elif ch == "=":
                pygame.draw.rect(s, (70, 48, 34), r)
                for k in range(2, T, 5): pygame.draw.rect(s, (40, 40, 50), (r.x+k, r.y, 2, T))
                pygame.draw.rect(s, (40, 40, 50), (r.x, r.y+5, T, 2))
            elif room["walk"][y][x] or ch in "MU" or ch.islower():
                pygame.draw.rect(s, C["floor"] if (x+y) % 2 else C["floor2"], r)
                if rnd.random() < .06: s.set_at((r.x+rnd.randrange(T), r.y+rnd.randrange(T)), C["stone_lo"])
            if ch == "U":
                for k in range(4): pygame.draw.rect(s, C["stone_hi"] if k % 2 else C["stone"], (r.x, r.y+k*4, T, 3))
    return s

def inside(g, x, y):
    """floor if enclosed horizontally by walls or on an open corridor row/col"""
    row = g[y]; colm = [g[k][x] for k in range(ROWS)]
    l = "#" in row[:x] or x == 0; r_ = "#" in row[x+1:] or x == COLS-1
    u = "#" in "".join(colm[:y]) or y == 0; d = "#" in "".join(colm[y+1:]) or y == ROWS-1
    return l and r_ and u and d

# ---------------- background / CRT ----------------
_SW = {}
def swirl(t, small):
    try: return swirl_np(t, small)
    except Exception: return swirl_plain(t, small)

def swirl_plain(t, small):
    """pure-pygame fallback: drifting sine curves"""
    w, h = small.get_size(); small.fill((12, 9, 22))
    for k in range(9):
        pts = [(x, h/2 + math.sin(x*.03 + k*.7 + t*.3)*h*.4 + (k-4)*12) for x in range(0, w+8, 8)]
        pygame.draw.lines(small, (110, 64, 168) if k % 2 else (48, 132, 150), False, pts, 1)

def swirl_np(t, small):
    """thin curling purple/teal swirl lines on a deep background (numpy)"""
    w, h = small.get_size()
    if (w, h) not in _SW:
        X, Y = np.meshgrid(np.linspace(0, 6.4 * w / 320, w), np.linspace(0, 3.6 * h / 180, h), indexing="ij")
        if (w, h) != (BASE_W // 2, BASE_H // 2): X, Y = X.astype(np.float32), Y.astype(np.float32)   # big frames: float32 (~2x faster)
        B = np.tile(np.array(art.BAYER, np.float32) / 16 - .5, (w // 4 + 1, h // 4 + 1))[:w, :h].astype(X.dtype)
        _SW[(w, h)] = (X, Y, B)
    X, Y, B = _SW[(w, h)]
    t = X.dtype.type(t)
    wx = X + .9*np.sin(Y*1.4 + t*.22) + .4*np.sin(Y*3.1 - t*.15)
    wy = Y + .9*np.cos(X*1.2 - t*.18) + .4*np.cos(X*2.7 + t*.2)
    f = np.sin(wx*1.6 + np.sin(wy*1.8)*1.8) + np.cos(wy*1.9 - np.cos(wx*1.4)*1.7)
    line = np.abs(np.sin(f*2.6))
    teal = np.sin(X*.8 - Y*.9 + t*.1) + .3*np.sin(f) > .25
    out = np.empty((w, h, 3), np.uint8)
    bg = (np.clip((f + 2)/4, 0, 1) * 10)[..., None]
    out[:] = (np.array([12, 9, 22]) + bg * np.array([1.2, .6, 2.2])).astype(np.uint8)
    core = line < .10 + B*.06; edge = (line < .26 + B*.10) & ~core
    out[edge & ~teal] = (54, 30, 88); out[core & ~teal] = (110, 64, 168)
    out[edge & teal] = (20, 62, 78); out[core & teal] = (48, 132, 150)
    pygame.surfarray.blit_array(small, out)

def make_crt(size):
    w, h = size
    lines = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(0, h, 2): pygame.draw.line(lines, (0, 0, 0, 70), (0, y), (w, y))
    vig = pygame.Surface(size, pygame.SRCALPHA)
    for i in range(40):
        a = int(120 * (1 - i/40) ** 3)
        pygame.draw.rect(vig, (0, 0, 0, a), (i*3, i*2, w-i*6, h-i*4), 3, border_radius=60)
    return lines, vig

def blur5(src, d):
    """separable 5-tap gaussian (1 4 6 4 1)/16 along d, pure pygame"""
    out = gfx.rgb(src.get_size()); out.fill((0, 0, 0))
    for k, w in ((-2, 16), (-1, 64), (0, 96), (1, 64), (2, 16)):
        c = src.copy(); c.fill((w, w, w), special_flags=pygame.BLEND_RGB_MULT)
        out.blit(c, (k*d[0], k*d[1]), special_flags=pygame.BLEND_RGB_ADD)
    return out

_CURVE = {}
def curve(src, dst):
    """slight barrel curve: each row is scaled narrower toward top/bottom"""
    w, h = src.get_size()
    key = (w, h, PANEL.y)
    if key not in _CURVE:   # runs of rows sharing one shrink value; nearest scaling per run == per row
        runs, y = [], 0
        sh = lambda y: int(w * 0.014 * ((min(y, PANEL.y) + .5) / h * 2 - 1) ** 2)   # panel rows share one width so text doesn't shear
        while y < h:
            s0 = sh(y); y1 = y + 1
            while y1 < h and sh(y1) == s0: y1 += 1
            runs.append((y, y1 - y, s0)); y = y1
        _CURVE[key] = runs
    for y, n, shrink in _CURVE[key]:
        if shrink: dst.fill((0, 0, 0), (0, y, shrink, n)); dst.fill((0, 0, 0), (w - shrink, y, shrink, n))   # only the margins
        strip = src.subsurface((0, y, w, n))
        dst.blit(pygame.transform.scale(strip, (w - 2*shrink, n)), (shrink, y))

# ---------------- game ----------------
class Game:
    # restart = a fresh game state. Only these caches survive: sprite/animation caches keyed by asset kind
    # (not by object id) and the frame-sized UI surface. Room images survive only for rooms whose grid never changed.
    KEEP_ON_RESTART = ("_manim", "_death", "_fount", "_statue", "_hero_anim", "_door_spr", "_hero_ovl", "mode_cfgs", "ui")

    @staticmethod
    def clean_cache(cache):
        """room-image cache minus every room that was rebaked (gate, passage, bars, mirror) and the per-game flags"""
        dirty = cache.get("_dirty", set())
        return {k: v for k, v in cache.items()
                if k not in ("_dirty", "mirror67_open") and k not in dirty and not (isinstance(k, tuple) and k[-1] in dirty)}

    def restart(self, mode=None):
        """fresh Game state on the same object (main() keeps its reference): clears every attribute,
        so nothing set outside __init__ (smoke, cam, regen_acc, filled_once, held keys, stair state, ...) carries over"""
        keep = {k: self.__dict__[k] for k in self.KEEP_ON_RESTART if k in self.__dict__}
        cache = self.clean_cache(self.room_cache)
        self.__dict__.clear(); self.__dict__.update(keep)
        self.__init__(mode or "classic")
        for k, v in cache.items(): self.room_cache.setdefault(k, v)

    def __init__(self, mode="classic"):
        self.mode = mode; self.cfg = load_cfg(mode); self.mode_sel = MODES.index(mode)
        self.death = None; self.passage_open = False
        self.rooms = load_rooms(); self.place_chainmail()
        self.font = pygame.font.Font(None, 18); self.big = pygame.font.Font(None, 44); self.mid = pygame.font.Font(None, 22)
        self.heroes = {(sw, hm): [outline(art3.make_hero(f, sw, hm)) for f in (0, 1)] for sw in (False, True) for hm in (False, True)}
        self.hero = self.heroes[(True, False)]
        self.fountain = art3.make_fountain()
        self.ogre = art3.make_ogre(); self.rug = art.make_club_rug(); self.snake = art.outline(art3.make_snake()); self.torch = art.make_torch()
        self.bush = {"*": [art3.make_bush(True, k) for k in range(4)], "+": [art3.make_bush(False, k+9) for k in range(4)]}
        R = 50*T   # dark overlay covers the whole room layer wherever the hero stands (whole room can be on screen, #29)
        self.dark_full = pygame.Surface((R, R), pygame.SRCALPHA); self.dark_full.fill((4, 3, 10, 238))
        self.dark_lit = pygame.Surface((R, R), pygame.SRCALPHA); self.dark_lit.fill((4, 3, 10, 238))
        for r_ in range(96, 0, -2):   # lamp pool: alpha falls off toward the hero
            pygame.draw.circle(self.dark_lit, (6, 4, 10, int(238*min(1, (r_/96)**2.2))), (R//2, R//2), r_)
        self.lights = {"warm": art.light(30, (190, 120, 50)), "big": art.light(40, (150, 100, 40)), "candle": art.light(48, (200, 130, 60))}
        self.layer = gfx.rgb((COLS*T, ROWS*T + 24)); self.view_src = gfx.rgb((VIEW.w//ZOOM, VIEW.h//ZOOM)); self.view_vig = self.make_vig(VIEW.size)
        self.shadows = {w: art.shadow(w) for w in (12, 18, 24, 30, 40)}; self.rug_sh = art.shadow(4*T)
        self.chest = self.make_chest()
        self.item_spr = {}
        self.room_cache = {}
        self.state = "title"
        self.rid = 1; self.hx, self.hy = 11, 14; self.facing = 1
        self.draw_x, self.draw_y = self.hx*T, self.hy*T
        self.inv = []; self.typed = ""; self.log = []
        for r in self.rooms.values():      # monster stats from the mode config
            keep = []
            for m in r["mons"]:
                mc = self.cfg["monsters"].get(m["name"])
                if not mc: continue
                if not mc["can_be_hurt"]:      # vampire/fairies: never move, block the way, removed by puzzles
                    m.update(blocker=True, hp=1, strength=1, points=0, at=9e9); keep.append(m); continue
                m.update(hp=mc["strength"], strength=mc["strength"], dmg=(mc["dmg_min"], mc["dmg_max"]), points=mc["points"],
                         at=self.cfg["timing"]["monster_first_attack_delay"]); keep.append(m)
            r["mons"] = keep
        self.flask_full = False; self.heals_used = 0; self.gate_open = False; self.atk_cd = 0.0; self.since_combat = 99.0
        self.strength = self.cfg["player"]["start_strength"]; self.kills = 0; self.kill_pts = 0; self.shake = 0.0; self.hurt = 0.0; self.floats = []; self.lunge = None
        self.pops = []; self.t = 0; self.step = 0; self.confirm = None     # pending Y/N question: callable run on Y
        self.small = gfx.rgb((320, 180))
        self.enter_room(1, announce=True)

    # --- helpers
    @property
    def room(self): return self.rooms[self.rid]
    def say(self, *lines):
        for l in lines: self.log.append(re.sub(r'([.!?,])(?=[A-Za-z])', r'\1 ', l))
        self.log = self.log[-40:]
    def treasures(self):   # carried (+ dropped in treasure_room if configured; 0 = carried only)
        tr = self.cfg["points"]["treasure_room"]
        return sum(1 for i in self.inv if i.get("treasure")) + (sum(1 for i in self.rooms[tr]["items"] if i.get("treasure")) if tr else 0)
    def score(self): return self.kill_pts + self.cfg["points"]["treasure"]*self.treasures() + (self.cfg["points"]["escape"] if self.state == "escaped" else 0)
    def has(self, name): return any(self.is_item(i, name) for i in self.inv)    # carried or worn (#27: worn still counts)
    @staticmethod
    def is_item(i, name): return i["name"].lower() == name or i["name"].lower().split()[-1] == name
    # Modern: worn items stay in self.inv (treasure, necklace trap check, score all see them) but use no carry slot
    def worn(self, name=None): return [i for i in self.inv if i.get("worn") and (name is None or self.is_item(i, name))]
    def carried(self): return [i for i in self.inv if not (i.get("worn") or i.get("equipped"))]
    def slots_used(self): return sum(i.get("slots", 1) for i in self.carried())     # Chain Mail carried = 2
    def backpack(self): return next((i for i in self.inv if i.get("equipped")), None)
    def carry_limit(self): return self.cfg["inventory"]["limit"] + (self.cfg["backpack"]["bonus_slots"] if self.backpack() else 0)
    def helmet_on(self):
        """helmet protection / sprite: Classic = carried (original); Modern = only while worn"""
        return bool(self.worn("helmet")) if self.cfg["wear"]["helmet_needs_wearing"] else self.has("helmet")
    def mail_on(self): return bool(self.cfg["chainmail"]["enabled"] and self.worn("chain mail"))
    def mail_damage(self, dmg):
        """ worn Chain Mail: a landed hit does damage_mult of it, rounded half up, at least 1 (heals / 0 untouched)"""
        return max(1, int(dmg * self.cfg["chainmail"]["damage_mult"] + 0.5)) if dmg > 0 and self.mail_on() else dmg
    def place_chainmail(self):
        """ Modern: Chain Mail on its cell in the Knights Hall (the art set's manifest may move it onto the armour stand)"""
        cm = self.cfg["chainmail"]
        if not cm["enabled"]: return
        x, y = cm["cell"]
        try: x, y = json.load(open(os.path.join(HERE, "assets", "chain_mail", "manifest.json"))).get("item_cell", (x, y))
        except (OSError, ValueError): pass
        r = self.rooms[cm["room"]]
        r["_flags"] = {"CHAINMAIL"}      # setpiece.draw_objects: the armour stand prop, Modern only
        r["items"].append(dict(name="Chain Mail", x=x, y=y, treasure=False, slots=cm["carry_slots"], chainmail=True))
        if cm["stand_solid"] and setpiece.mail_stand() and r["walk"][y][x]:   # the stand blocks; set_objs = floor baked under it
            if setpiece.block_ok(r, [(x, y)]): r.setdefault("set_objs", []).append(["mail_stand", [(x, y)]])
            else: print("[castle diag] armour stand left walkable (would block):", (x, y))
    def wearable(self, it): return self.cfg["wear"]["worn_items_free_slots"] and any(self.is_item(it, w) for w in self.cfg["wear"]["wearable"])
    def inv_text(self):
        c = f"You carry ({self.slots_used()}/{self.carry_limit()}): " + (", ".join(i["name"] + (f" ({i['slots']} slots)" if i.get("slots", 1) > 1 else "")
                                                                                 for i in self.carried()) or "nothing.")
        w = [i["name"] for i in self.worn()] + (["Backpack (equipped)"] if self.backpack() else [])
        return [c] + ([f"Wearing: {', '.join(w)}."] if w else [])
    def hud_inv(self):
        c, w = self.carried(), self.worn() + ([self.backpack()] if self.backpack() else [])
        return ("INV " + ", ".join(i["name"] for i in c) if c else "") + (("   " if c else "") + "WEARING " + ", ".join(i["name"] for i in w) if w else "")
    def mon_at(self, x, y): return next((m for m in self.room["mons"] if m["alive"] and (m["x"], m["y"]) == (x, y)), None)
    def float_text(self, x, y, txt, col): self.floats.append([x*T + T/2, y*T, txt, col, 0.0])

    def enter_room(self, rid, announce=True):
        self.rid = rid; self.confirm = None       # a pending DROP TREASURE question doesn't follow you into another room
        if rid == MIRROR_ROOM: self.close_mirror()       # screen-only state in the original: every redraw of 67 shows the mirror again
        if rid not in self.room_cache: self.room_cache[rid] = art3.bake_room(rid, self.room)
        if announce: self.say("", self.room["name"].upper(), self.room["description"])

    def mirror_open(self): return bool(self.room_cache.get("mirror67_open"))

    def close_mirror(self):
        r = self.rooms[MIRROR_ROOM]
        if "grid0" in r: r["grid"] = list(r["grid0"])
        if self.mirror_open() or "grid0" in r:
            r.pop("_hook_blocks", None); r.pop("grid0", None); self.room_cache["mirror67_open"] = False
            rid, self.rid = self.rid, MIRROR_ROOM; self.rebake(); self.rid = rid

    def open_mirror(self):
        """WAVE WAND in 67: the mirror vanishes in a puff of smoke and the passage east to the lab opens"""
        r = self.room
        b = next(iter(setpiece.hook_blocks(MIRROR_ROOM, r)), None)
        if b:   # keep the old mirror sprite for the fade-out under the smoke
            sp, (ax, ay), _ = setpiece.hook_sprite(MIRROR_ROOM, b); X, Y = b[0]*T + b[2]*T//2, (b[1] + b[3])*T
            self.puff(X, Y - b[3]*T//2, sprite=(sp, X - ax, Y - 1 - ay))     # (296, 144): anchor at (296, 169)
        else: self.puff(18*T + 8, 9*T)
        r.setdefault("grid0", list(r["grid"]))
        g = r["grid"]
        for (x, y), ch in MIRROR_OPEN: g[y] = g[y][:x] + ch + g[y][x+1:]
        r.pop("_hook_blocks", None); self.room_cache["mirror67_open"] = True; self.rebake()

    # smoke (assets/smoke/manifest.json): (file, frame w, anchor, frame ms, anchor offset below the puff centre)
    PUFFS = {False: ("smoke/smoke_puff.png", 48, (24, 71), (60, 80, 110, 140, 160, 170, 180, 200), 25),
             True: ("smoke/smoke_puff_small.png", 32, (16, 39), (60, 90, 120, 140, 160, 180), 12)}   # small: anchor = hero's feet

    def puff(self, X, Y, sprite=None, small=False):
        """puff of smoke centred on room px (X, Y), played once; optional sprite fades out underneath (~0.45 s)"""
        f, fw, (ax, ay), ms, dy = self.PUFFS[small]
        self.smoke = dict(t0=self.t, sprite=sprite, file=f, fw=fw, pos=(X - ax, Y + dy - ay), ends=list(itertools.accumulate(m / 1000 for m in ms)), core=(X, Y))
        self.shake = max(self.shake, .3)

    def try_move(self, dx, dy):
        if self.state != "play": return
        self.facing = dx or self.facing
        nx, ny = self.hx+dx, self.hy+dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            m = self.mon_at(nx, ny)
            if m: return self.attack(m)
            ch = self.room["grid"][ny][nx]
            if ch in "UD":    # stairs: walking into them climbs (original moveDelta)
                dest = self.room["exits"].get("up" if ch == "U" else "down")
                if not dest: return
                if not self.stairs_armed(): return       # anti-bounce: fresh step needed after arriving
                if dest not in SLICE: self.say("The stairs fade into mist... (beyond this slice)"); return
                if dest in DARK_ENTRY and not self.has("lamp"): self.say("It's too dark to go that way!"); return
                self.enter_room(dest)
                if solid(self.room, self.hx, self.hy):
                    _, self.hx, self.hy = min((abs(x-self.hx)+abs(y-self.hy), x, y) for y in range(ROWS) for x in range(COLS) if not solid(self.room, x, y))
                self.draw_x, self.draw_y = self.hx*T, self.hy*T
                self.stair_arrive = (self.rid, self.hx, self.hy); self.stair_cd = self.cfg["stairs"]["cooldown_s"]
                self.stair_stale_key = self.held_key      # key held through the transition doesn't count
                return
            it = next((i for i in self.room["items"] if (i["x"], i["y"]) == (nx, ny)), None)
            if it and solid(self.room, nx, ny) and ch != "=":
                self.pick(it); return          # item on furniture (e.g. the flask on the desk): bump to take
            if ch == "=" and self.gate_open and self.rid == self.cfg["gate"]["room"]:
                self.hx, self.hy = nx, ny; self.step += 1; return
            if ch == "G":
                if self.has("key") and self.cfg["doors"]["bump_with_key_unlocks"]: self.unlock()
                else: self.say("The Door is locked.")
                return
            if not solid(self.room, nx, ny):
                self.hx, self.hy = nx, ny; self.step += 1
                tr = TRAPS.get(self.rid)
                if tr and nx == tr[0] and ny in tr[1] and not self.has("necklace"):
                    self.say("You have sprung a Trap!! The room has filled with water and you drowned!")
                    self.death = "drowned"; self.die(); return
                it = next((i for i in self.room["items"] if (i["x"], i["y"]) == (nx, ny)), None)
                if it: self.pick(it)     # original picks items up on contact
            elif ch == "=": self.say("The Gate is locked.")
            return
        d = {(0, -1): "n", (0, 1): "s", (1, 0): "e", (-1, 0): "w"}[(dx, dy)]
        self.leave(d)

    stair_cd = 0.0; stair_arrive = None; stair_stale_key = None
    def stairs_armed(self):
        if self.stair_arrive is None: return True
        if self.stair_stale_key is not None and self.held_key == self.stair_stale_key: return False
        if self.stair_cd <= 0 or (self.rid, self.hx, self.hy) != self.stair_arrive:
            self.stair_arrive = None; return True
        return False

    def pick(self, it):
        if it.get("backpack"): return self.equip_backpack(it)
        need = it.get("slots", 1)
        if self.slots_used() + need > self.carry_limit():
            self.say("It's too heavy to carry with all that." if need > 1 else f"Take {it['name']}: Can't carry any more!"); return False
        self.room["items"].remove(it); self.inv.append(it)
        self.say(f"Taken: {it['name']}." + ("  A TREASURE!" if it.get("treasure") else ""))
        self.pops.append([it, it["x"]*T, it["y"]*T, 0.0]); self.hud_bump = 1.0
        if self.room.get("drawer") == "open" and "desk" in it.get("hidden", ""): self.room["drawer"] = "empty"
        if "statue" in it.get("hidden", ""): self.room["statue_state"] = "plain"
        return True

    def attack(self, m):
        """needs SWORD; hit chance / damage / points from the mode config"""
        sw = self.cfg["sword"]; self.since_combat = 0
        if self.atk_cd > 0: return
        self.atk_cd = self.cfg["timing"]["player_attack_interval"]
        self.lunge = [m["x"] - self.hx, m["y"] - self.hy, 0.0]
        if m.get("blocker"):
            self.say(f"The {m['name']} is blocking your way." + (" He can't be hurt." if m["name"] == "Vampire" else "")); return
        if not self.has("sword"): self.say("You have no Weapon"); return
        if random.random() < sw["hit_chance"]:
            d = random.randint(sw["dmg_min"], sw["dmg_max"]); m["hp"] -= d; m["flash"] = .18; self.shake = max(self.shake, .15)
            self.float_text(m["x"], m["y"], str(d) if d >= 0 else f"+{-d}", (255, 230, 120) if d >= 0 else (120, 230, 140))
            if m["hp"] < self.cfg["timing"]["monster_dies_below"]:
                m["alive"] = False; m["dead_t"] = 0.0; self.kills += 1; self.kill_pts += m["points"]; self.shake = .35
                self.say(f"You killed the {m['name']}!"); self.float_text(m["x"], m["y"] - 1, f"+{m['points']}", (140, 230, 120))
                self.backpack_drop(m)
            else: self.say(f"You struck the {m['name']}!")
        else:
            if not sw["silent_miss"]: self.say(f"You missed the {m['name']}!")
            self.float_text(m["x"], m["y"], "MISS", (180, 180, 200))

    # Modern: the Ugly Ogre in room 21 drops a Backpack (+bonus_slots carry capacity, equips on pickup, no slot itself)
    def backpack_drop(self, m):
        bp = self.cfg["backpack"]
        if not bp["enabled"] or self.rid != bp["room"] or m["name"] != bp["monster"] or m.get("dropped"): return
        m["dropped"] = True
        self.room["items"].append(dict(name="Backpack", x=m["x"], y=m["y"], backpack=True, treasure=False))
        self.say(f"The {m['name']} dropped a Backpack!")

    def equip_backpack(self, it):
        if self.backpack(): self.say("You already have a Backpack."); return False
        if it in self.room["items"]: self.room["items"].remove(it)
        it["equipped"] = True; self.inv.append(it)
        self.say(f"Taken: Backpack. You put it on: you can carry {self.carry_limit()} items now.")
        self.pops.append([it, it["x"]*T, it["y"]*T, 0.0]); self.hud_bump = 1.0
        return True

    def free_cells_near(self, n):
        """n floor cells around the hero (nearest first): walkable, no item, no monster, not the hero's own cell"""
        seen = {(self.hx, self.hy)}; q = [(self.hx, self.hy)]; out = []
        while q and len(out) < n:
            x, y = q.pop(0)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                c = (x + dx, y + dy)
                if c in seen or not (0 < c[0] < COLS-1 and 0 < c[1] < ROWS-1) or solid(self.room, *c): continue
                seen.add(c); q.append(c)
                if not any((i["x"], i["y"]) == c for i in self.room["items"]) and not self.mon_at(*c) and len(out) < n: out.append(c)
        return out

    # ---- Modern: DROP TREASURE ----
    def needed_treasures(self):
        """treasures still needed to finish: the Necklace always (trap rooms 76/78); the Scepter while the gate is shut;
        the Holy Cross while a Vampire lives; the Harp while a Fairy remains"""
        alive = lambda nm: any(m.get("name") == nm and m["alive"] for r in self.rooms.values() for m in r["mons"])
        need = {"necklace"}
        if not self.gate_open: need.add("scepter")
        if alive("Vampire"): need.add("cross")
        if alive("Fairy"): need.add("harp")
        return need
    def spare_treasures(self):
        need = self.needed_treasures()
        return [i for i in self.inv if i.get("treasure") and not any(self.is_item(i, k) for k in need)]
    def drop_cells(self, k):
        """k cells for dropped items: the hero's cell, then the nearest free floor cells (no item, exit edge, trap,
        stair/door/set piece), nearest first; stacks on the hero's cell when the room runs out"""
        taken = {(i["x"], i["y"]) for i in self.room["items"]}
        tr = TRAPS.get(self.rid); traps = {(tr[0], y) for y in tr[1]} if tr else set()
        cand = sorted(((abs(x - self.hx) + abs(y - self.hy), y, x) for y in range(1, ROWS - 1) for x in range(1, COLS - 1)
                       if self.room["grid"][y][x] == " " and not solid(self.room, x, y) and (x, y) not in taken and (x, y) not in traps
                       and abs(x - self.hx) + abs(y - self.hy) <= 3))
        cells = [(x, y) for _, y, x in cand][:k]
        return cells + [(self.hx, self.hy)] * (k - len(cells))
    def drop_treasure(self, sure=False):
        tr = [i for i in self.inv if i.get("treasure")]
        if not tr: self.say("You aren't carrying any treasure."); return
        spare = self.spare_treasures()
        kept = [i["name"] for i in tr if i not in spare]
        if not spare: self.say("You have no treasures you can spare." + (f"  Kept: {', '.join(kept)} (still needed)." if kept else "")); return
        bank = self.cfg["points"]["treasure_room"]
        if self.rid != bank and not sure:
            pts = self.cfg["points"]["treasure"] * len(spare)
            self.say(f"Warning: treasures only score if carried or left in the Courtyard. Dropping {len(spare)} here loses {pts} points.",
                     "Are you sure? (Y/N)")
            self.confirm = lambda: self.drop_treasure(sure=True); return
        for it, (x, y) in zip(spare, self.drop_cells(len(spare))):
            self.inv.remove(it); it.pop("worn", None); it["x"], it["y"] = x, y; self.room["items"].append(it)
        self.hud_bump = 1.0
        self.say(f"Dropped: {', '.join(i['name'] for i in spare)}." + (f"  Kept: {', '.join(kept)} (still needed)." if kept else "")
                 + ("  They're safe here." if self.rid == bank else ""))

    def drop_backpack(self):
        """DROP BACKPACK: allowed; items over the base limit spill onto the floor around the hero (never over the limit)"""
        bp = self.backpack(); self.inv.remove(bp); bp.pop("equipped")
        bp["x"], bp["y"] = self.hx, self.hy; self.room["items"].append(bp)
        extra = []                                           # newest first until the rest fits (#28: Chain Mail counts 2)
        for it in self.carried()[::-1]:
            if self.slots_used() - sum(i.get("slots", 1) for i in extra) <= self.carry_limit(): break
            extra.append(it)
        cells = self.free_cells_near(len(extra))
        spilled = []
        for k, it in enumerate(extra):                       # no free floor nearby: they land on the hero's cell
            x, y = cells[k] if k < len(cells) else (self.hx, self.hy)
            self.inv.remove(it); it["x"], it["y"] = x, y; self.room["items"].append(it); spilled.append(it["name"])
        self.say("Dropped: Backpack." + (f"  It spills: {', '.join(spilled)}." if spilled else ""))

    def monsters_tick(self, dt):
        """original moveMonsters: each tick step toward the player (vertical, then horizontal),
        blocked by anything solid; when touching, 40% chance to hit for `attack`; helmet refunds half the time"""
        for m in self.room["mons"]:
            if not m["alive"]:
                m["dead_t"] = m.get("dead_t", 0) + dt; continue
            if m.get("blocker"): continue
            m["flash"] = max(0, m["flash"] - dt)
            dx, dy = self.hx - m["x"], self.hy - m["y"]
            ma = self.cfg["monster_attack"]; tm = self.cfg["timing"]
            touching = (max(abs(dx), abs(dy)) <= 1) if ma["touch_includes_diagonal"] else (abs(dx) + abs(dy) == 1)
            if touching:
                self.since_combat = 0
                m["at"] -= dt
                ak = self.anim_kind(m["name"]); an = ak and self.mon_anim(ak)
                if an and "attack" in an["states"]:   # start the attack strip so its hit frame lands when the bite resolves
                    s_ = an["states"]["attack"]; wind = sum(s_["durs"][:s_["hit"]]) / 1000
                    busy = m.get("atk_t0") is not None and self.anim_frame(s_, self.t - m["atk_t0"]) is not None
                    if not busy and m["at"] <= wind: m["atk_t0"] = self.t - (wind - max(0, m["at"]))
                if m["at"] <= 0:
                    m["at"] = tm["monster_attack_interval"]; m["bite"] = .2
                    helm = self.helmet_on()
                    if random.random() < (ma["hit_chance_helmet"] if helm else ma["hit_chance"]):
                        lo, hi = m["dmg"] if ma["use_monster_damage"] else (ma["dmg_min"], ma["dmg_max"])
                        dmg = random.randint(lo, hi)
                        if helm: dmg = int(round(dmg * ma["helmet_damage_factor"]))
                        dmg = self.mail_damage(dmg)
                        self.strength -= dmg
                        if self.strength < self.cfg["player"]["death_below"]:
                            self.strength = 0; self.say(f"The {m['name']} has killed you!"); self.die(); return
                        self.say(f"The {m['name']} struck you!" + ("  The Helmet helped." if helm and ma["helmet_message"] else ""))
                        self.float_text(self.hx, self.hy, f"-{dmg}" if dmg >= 0 else f"+{-dmg}", (255, 90, 80) if dmg >= 0 else (120, 230, 140))
                        if dmg > 0: self.hurt = .25; self.shake = max(self.shake, .25)
                    else:
                        if not ma["silent_miss"]: self.say(f"The {m['name']} missed you!")
                        self.float_text(self.hx, self.hy, "DODGE" if helm else "MISS", (200, 210, 230))
                continue
            m["mt"] -= dt
            if m["mt"] > 0: continue
            m["mt"] = self.cfg["timing"]["monster_move_interval"]
            sgx, sgy = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
            steps = ([(sgx, sgy)] if tm["monster_move_8way"] else []) + ([(0, sgy)] if sgy else []) + [(sgx, 0)]
            if tm["monster_move_8way"]: steps = steps[:1]     # original: one SGN step; blocked means no move
            for sx, sy in steps:
                nx, ny = m["x"] + sx, m["y"] + sy
                if (sx or sy) and 0 < nx < COLS-1 and 0 < ny < ROWS-1 and not solid(self.room, nx, ny) \
                        and (nx, ny) != (self.hx, self.hy) and not self.mon_at(nx, ny) \
                        and not any((i["x"], i["y"]) == (nx, ny) for i in self.room["items"]):
                    m["x"], m["y"] = nx, ny
                    if sx: m["face"] = sx
                    break

    def examine(self, n):
        r = self.room
        n = {"shelf": "shelves", "shelve": "shelves"}.get(n, n)
        hid = [h for h in r.get("hidden", []) if n in h.get("hidden", "") or n in h["name"].lower()]
        if hid:
            for h in hid:
                r["hidden"].remove(h); r["items"].append(h)
                hd = h.get("hidden", "")
                a_ = "some" if h["name"].endswith("s") else "an" if h["name"][0] in "AEIOU" else "a"
                if "desk" in hd and self.rid in DRAWER_ROOMS:
                    r["drawer"] = "open"
                    if self.mode != "classic": self.say(f"You open the desk drawer. There is {a_} {h['name']} inside."); continue
                self.say(f"There is {a_} {h['name']} on top." if "desk" in hd else f"There is {a_} {h['name']} on the shelf." if "shel" in hd
                         else f"The statue is wearing a {h['name']}." if "statue" in hd else f"You find a {h['name']}!")
            return
        if "flask" in n and (self.has("wine flask") or any("flask" in i["name"].lower() for i in r["items"])):
            self.say("It's filled with water." if self.flask_full else "It's empty."); return
        if "fountain" in n and self.rid == self.cfg["flask"]["fill_room"]:
            self.say("The fountain is filled with water."); return
        if n in ("chain", "mail", "chainmail", "armour", "armor") and any(i.get("chainmail") for i in self.inv + r["items"]):
            self.say("A knight's coat of chain mail: old and dark with age, but the rings are tight and sturdy. Heavy, though.")
            return
        if n in ("desk", "table", "bed"): self.say("Nothing special."); return
        self.say("I see nothing special.")

    def near_fountain(self):
        g = self.room["grid"]
        return any(   # original: a straight fountain edge (│ ─) in one of the 8 surrounding cells
            0 <= self.hy+dy < ROWS and 0 <= self.hx+dx < COLS and g[self.hy+dy][self.hx+dx] in self.cfg["flask"]["fill_edge_chars"]
            for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    def fill(self):
        """original FILL: only in the fountain room; needs the flask; must reach the fountain"""
        f = self.cfg["flask"]
        if self.rid == 68: self.say("The Barrels are empty."); return
        if self.rid != f["fill_room"]: self.say("There's nothing here to fill it with."); return
        if not self.has("wine flask"): self.say("You don't have a Container!"); return
        if self.flask_full: self.say("The flask is full!"); return
        if f["fill_needs_adjacent"] and not self.near_fountain(): self.say("I can't reach it!"); return
        if not f["refillable"] and getattr(self, "filled_once", False): self.say("The fountain has run dry."); return
        self.flask_full = True; self.filled_once = True; self.say("Done."); self.hud_bump = 1.0

    def drink(self):
        f = self.cfg["flask"]; pc = self.cfg["player"]
        if not (self.has("wine flask") and self.flask_full): self.say("You don't have any."); return
        uses = f["heal_uses_per_game"]
        if uses and self.heals_used >= uses:
            self.say("That was good.")
            if not f["drink_empties_after_used"]: return
        else:
            self.heals_used += 1
            before = self.strength
            self.strength = pc["max_strength"] if f["heal"] == "full" else min(pc["max_strength"], self.strength + f["heal_amount"])
            self.say("That was good! I feel much better now!"); self.float_text(self.hx, self.hy, f"+{self.strength - before}", (120, 230, 140))
        if f["drink_empties"]: self.flask_full = False

    def rebake(self):
        self.room["walk"] = flood(self.room["grid"], self.room["exits"]); decor.apply_blocking(self.room)
        for k in (self.rid, ("st", self.rid), ("stm", self.rid)): self.room_cache.pop(k, None)   # bake, stencil, outside mask
        self.room_cache.setdefault("_dirty", set()).add(self.rid)          # changed room: its image doesn't survive a restart
        self.room_cache[self.rid] = art3.bake_room(self.rid, self.room)

    def set_cells(self, cells, ch):
        g = self.room["grid"]
        for x, y in cells: g[y] = g[y][:x] + ch + g[y][x+1:]
        self.rebake()

    def unlock(self, lock=False):
        r = self.room
        if not r["doors"]: self.say("There's nothing here to unlock." if not lock else "There's nothing here to lock."); return
        if not self.has("key"): self.say("You don't have the Key."); return
        is_locked = r["grid"][r["doors"][0][1]][r["doors"][0][0]] == "G"
        if lock == is_locked: self.say("The Door is already locked!" if lock else "The Door is already unlocked!"); return
        if any((self.hx, self.hy) == d for d in r["doors"]): self.say("Step out of the doorway first."); return
        self.set_cells(r["doors"], "G" if lock else " "); self.say("Done."); self.shake = .15

    def die(self):
        self.death = getattr(self, "death", None) or "slain"
        self.state = "dead"; self.dead_t = 0.0; self.held = None; self.shake = .6

    def leave(self, d):
        dx, dy, name = DIRS[d]
        dest = self.room["exits"].get(name)
        if dest == 84:      # ESCAPED pseudo-room: only once the gate is open
            if not self.gate_open: self.say("The Gate is locked."); return False
            self.state = "escaped"; self.dead_t = 0.0; self.held = None
            self.say("You've Escaped the Castle!"); return True
        if not dest: self.say("You can't go that way."); return False
        if dest not in SLICE: self.say(f"The way {name} fades into mist... (beyond this slice)"); return False
        if dest in DARK_ENTRY and self.rid not in DARK and not self.has("lamp"): self.say("It's too dark to go that way!"); return False
        prev = self.rid
        self.enter_room(dest)
        g = self.room["grid"]
        # arrive at opposite edge, at an open tile nearest current coordinate
        if dx: x = 0 if dx > 0 else COLS-1; cand = [(abs(y-self.hy), x, y) for y in range(ROWS) if not solid(self.room, x, y)]
        else: y = 0 if dy > 0 else ROWS-1; cand = [(abs(x-self.hx), x, y) for x in range(COLS) if not solid(self.room, x, y)]
        if cand: _, self.hx, self.hy = min(cand)
        if dest == MIRROR_ROOM and prev == LAB_ROOM:   # original 0x3600: back through the mirror, which is closed again
            self.hx, self.hy = MIRROR_ARRIVE; self.puff(self.hx*T + 8, self.hy*T + 4, small=True)
            self.say("There is a puff of smoke & you appear in the Sorcerers room!")
        self.draw_x, self.draw_y = self.hx*T, self.hy*T
        return True

    def go(self, d):
        dx, dy, name = DIRS[d]
        if not self.room["exits"].get(name): self.say("You can't go that way."); return
        self.leave(d)

    def touching_prop(self, it):
        """remake guess: an item hidden in the middle of a desk/statue counts as in reach when you stand
        next to any tile of that piece of furniture (the original's 1-cell rule assumes a 1-cell prop)"""
        g = self.room["grid"]; seen = {(it["x"], it["y"])}; st = [(it["x"], it["y"])]
        while st:
            x, y = st.pop()
            if max(abs(x-self.hx), abs(y-self.hy)) <= 1: return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x+dx, y+dy)
                if n not in seen and 0 <= n[0] < COLS and 0 <= n[1] < ROWS and g[n[1]][n[0]] not in " #G": seen.add(n); st.append(n)
        return False

    def near(self, it, r=2): return abs(it["x"]-self.hx) <= r and abs(it["y"]-self.hy) <= r

    def take_off(self, n):
        """ REMOVE / TAKE OFF: back into a carry slot; refuses when every slot is full"""
        if self.backpack() and n in ("backpack", "pack"): self.drop_backpack(); return     # the backpack comes off = dropped
        its = [i for i in self.worn() if n and n in i["name"].lower()]
        if not its: self.say("You aren't wearing that." if n else "Remove what?"); return
        if self.slots_used() + its[0].get("slots", 1) > self.carry_limit():
            self.say("Your hands are full." if its[0].get("slots", 1) == 1 or self.slots_used() >= self.carry_limit()
                     else f"Your hands are too full to carry the {its[0]['name']}."); return
        its[0].pop("worn"); self.say(f"You take off the {its[0]['name']}."); self.hud_bump = 1.0

    def command(self, text):
        self.say("> " + text)
        w = text.lower().split()
        if getattr(self, "confirm", None):          # a Y/N question is open: Y runs it, anything else cancels
            fn, self.confirm = self.confirm, None
            if w and w[0] in ("y", "yes"): fn()
            else: self.say("Ok, nothing dropped.")
            return
        if not w: return
        v, n = w[0], (w[1] if len(w) > 1 else "")
        nn = " ".join(w[1:])       # whole noun phrase (original NOUN$ = everything after the first space)
        if v in ("n", "s", "e", "w", "north", "south", "east", "west"): v, n = "go", v
        if v in ("go", "walk", "move"):
            d = n[:1]
            if d in DIRS: self.go(d)
            elif n in ("up", "u", "down", "d"): self.say("Walk into the stairs to climb them.")
            else: self.say("Go where? (n/s/e/w)")
        elif v in ("look", "l") and (not n or n in ("room", "around", "rug", "carpet")):
            r = self.room; self.say(r["name"].upper(), r["description"])
            for it in r["items"]: self.say(f"There is a {it['name']} here.")
            for m in r["mons"]:
                if m["alive"]: self.say(f"A {m['name']} glares at you." if m["name"][0] not in "AEIOU" else f"An {m['name']} glares at you.")
                else: self.say(f"The dead {m['name']} lies here.")
            if self.rid == 1 and (n in ("", "rug", "carpet")):
                self.say("A woven rug with a great club suit. Woven words read: A TRIBUTE TO KEVIN BALES, WHO MADE CASTLE ADVENTURE IN 1984.")
        elif self.cfg["wear"]["worn_items_free_slots"] and (v == "remove" or (v == "take" and n == "off")):
            self.take_off(" ".join(w[2:]) if v == "take" else nn)
        elif v in ("get", "take"):
            its = [i for i in self.room["items"] if not n or n in i["name"].lower() or n == "all"]
            if not its: self.say("I don't see that here." if n != "rug" else "The rug is far too heavy to carry.")
            elif not self.cfg["inventory"]["get_visible_by_command"] and not its[0].get("hidden"): self.say("Get it Yourself!")
            elif not (self.near(its[0], self.cfg["inventory"]["get_hidden_reach"]) if its[0].get("hidden") else self.near(its[0], 2)) and not (its[0].get("hidden") and self.touching_prop(its[0])): self.say("I can't reach it!")
            else: self.pick(its[0])
        elif v == "drop" and n in ("treasure", "treasures") and self.cfg["drop_treasure"]["enabled"]:
            self.drop_treasure()
        elif v == "drop":
            its = [i for i in self.inv if n and n in i["name"].lower()]
            if not its: self.say("You aren't carrying that.")
            elif its[0].get("equipped"): self.drop_backpack()
            else:
                it = its[0]; self.inv.remove(it); it["x"], it["y"] = self.hx, self.hy
                if it.pop("worn", False): self.say(f"You take off the {it['name']}.")     # DROP on a worn item
                self.room["items"].append(it); self.say(f"Dropped: {it['name']}.")
        elif v in ("inventory", "inv", "i"):
            self.say(*self.inv_text())
        elif v in ("look", "search", "examine", "l", "x") and n:
            self.examine(n)
        elif v == "fill":
            self.fill()
        elif v == "drink":
            self.drink()
        elif v in ("pour", "empty"):
            if self.has("wine flask") and self.flask_full: self.flask_full = False; self.say("You pour the water & it spills on the ground.")
            elif self.has("wine flask"): self.say("It's empty.")
            else: self.say("You don't have any.")
        elif v in ("kill", "attack", "fight", "hit") and not self.cfg["parser"]["kill_alias"]:
            self.say(f"I can't kill {n or 'that'}. (Walk into it.)")
        elif v == "wear" and self.backpack() and n in ("backpack", "pack"): self.say("The Backpack is already on your back.")
        elif v == "wear" and self.cfg["wear"]["worn_items_free_slots"] and any(n and n in i["name"].lower() and self.wearable(i) for i in self.inv):
            it = next(i for i in self.inv if n in i["name"].lower() and self.wearable(i))
            if it.get("worn"): self.say(f"You're already wearing the {it['name']}.")
            else: it["worn"] = True; self.say(f"Ok. I'm wearing the {it['name']}."); self.hud_bump = 1.0
        elif v == "wear":
            if not any(n in i["name"].lower() for i in self.inv): self.say("You don't have it.")
            elif "crown" in n: self.say("The crown is too Heavy!")
            elif "glasses" in n: self.say("Ok. I'm wearing them.")
            elif any(k in n for k in ("helmet", "necklace")): self.say("Ok. I'm wearing it.")   # no effect: carrying is enough
            else: self.say("That could be Difficult!")
        elif v == "read":
            if not n: self.say("Read what?")
            elif "book" not in n: self.say("There's nothing to read on it." if any(n in i["name"].lower() for i in self.inv) else "You don't have it.")
            elif not self.has("book"): self.say("You don't have it.")
            elif not self.has("glasses"): self.say("You can't see well enough. It's all Blurry.")
            else: self.say("The book reads: Wave Scepter")
        elif v in ("unlock", "open", "lock", "close"):
            if n in ("gate",) and self.rid == 1: self.say("The Gate is locked Magically.")
            elif n and n != "door": self.say("You can't do that.")
            else: self.unlock(lock=v in ("lock", "close"))
        elif v in ("eat",): self.say("I'm not hungry!")
        elif v in ("climb",): self.say("I don't need to climb.")
        elif v in ("jump", "leap", "leep"): self.say("I don't think it's safe to Jump here!" if self.rid in range(25, 27) or self.rid in range(42, 52) or self.rid in range(60, 66) else "I Jumped.")
        elif v in ("rub", "clean"):
            if not any(n and n in i["name"].lower() for i in self.inv): self.say("You don't have it.")
            else: self.say("There's no Genie in this Lamp!" if "lamp" in n else f"The {n} is cleaner now.")
        elif v == "say": self.say(n.upper() if n else "Say what?")
        elif v == "wave" and nn in ("wand", "magic wand") and self.has("wand") and (
                (self.rid == 77 and not getattr(self, "passage_open", False)) or self.rid == MIRROR_ROOM):
            # original WAVE (0x76e3-0x7856): "As you wave the <NOUN>....", then lines 4-7 are overwritten with the puff text,
            # so the "Nothing Happens!" lines never show in 77/67
            self.say(f"As you wave the {nn.upper()}....", "There is a *Puff* of smoke Revealing a Secret passage!")
            if self.rid == 77: self.passage_open = True; self.set_cells([(11, 17), (12, 17)], " "); self.shake = .3
            else: self.open_mirror()       # no "already open" check in 67: waving again just redraws the opening
        elif v == "wave" and n and "cross" in n and self.has("holy cross") and any(m.get("name") == "Vampire" and m["alive"] for m in self.room["mons"]):
            for m_ in self.room["mons"]:
                if m_.get("name") == "Vampire": m_["alive"] = False; m_["dead_t"] = 0.0
            self.say("The vampire sees the holy cross and disappears!")
        elif v == "wave":
            if not any(n and n in i["name"].lower() for i in self.inv): self.say(f"You don't have a {nn.upper() or 'THAT'}!" if self.rid == MIRROR_ROOM else "You don't have it.")
            elif "scepter" in n and self.rid == self.cfg["gate"]["room"]:
                self.gate_open = True; self.say("The Gate opens by itself!"); self.shake = .3
                gate = [(x, y) for y in range(ROWS) for x in range(COLS) if self.room["grid"][y][x] == "="]
                self.set_cells(gate, " ")      # original: the gate glyph is erased from the screen
            elif any(k in n for k in ("scepter", "wand", "cross")): self.say("Nothing Happens!")
            else: self.say(f"You look awful Silly waving that {n}")
        elif v == "play":
            if "harp" in n and self.has("harp"):
                self.say("The Harp makes Beautiful Music!")
                if any(m.get("name") == "Fairy" and m["alive"] for m in self.room["mons"]):
                    for m_ in self.room["mons"]:
                        if m_.get("name") == "Fairy": m_["alive"] = False; m_["dead_t"] = 0.0
                    self.say("The fairy likes the music and leaves!")
            elif any(n and n in i["name"].lower() for i in self.inv): self.say(f"The {n} makes Horrible music!!")
            else: self.say("You don't have it.")
        elif v in ("kill", "attack", "fight", "hit"):   # convenience alias; the original attacks by walking into a monster
            ms = [m for m in self.room["mons"] if m["alive"] and max(abs(m["x"]-self.hx), abs(m["y"]-self.hy)) <= 1 and (not n or n in m["name"].lower())]
            if ms: self.attack(ms[0])
            else: self.say("There is nothing here to fight.")
        elif v in ("score",):
            self.say(f"Score: {self.score()}  Strength: {self.strength}")
        elif v in ("help", "?"):
            self.say("Arrows walk; walk into monsters to fight, into stairs to climb. LOOK [thing], GET, DROP, INV, READ, WAVE, UNLOCK DOOR, WEAR, "
                     + ("REMOVE, " if self.cfg["wear"]["worn_items_free_slots"] else "") + "PLAY, FILL, DRINK, POUR, SCORE.")
            if self.cfg["wear"]["worn_items_free_slots"]: self.say("Worn items (WEAR NECKLACE, WEAR HELMET) don't use a carry slot.")
            if self.cfg["drop_treasure"]["enabled"]: self.say("DROP TREASURE drops the treasures you don't need (only those left in the Courtyard still score).")
        elif self.rid == MIRROR_ROOM and "mirror" in (v, n): self.say("The wicked witch never lived here!!")   # original parser, after the other verbs
        else: self.say(self.cfg["parser"]["unknown_reply"])

    # --- loop
    held = None; held_key = None; rep = 0.0
    def event(self, e):
        if e.type == pygame.KEYUP and e.key == self.held_key: self.held = None; self.held_key = None
        if e.type != pygame.KEYDOWN: return
        if self.state == "title":
            if e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                self.mode_sel = 1 - self.mode_sel; self.hud_bump = 1.0
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.restart(MODES[self.mode_sel])
                self.state = "play"; self.say(f"{self.cfg['label']} MODE. Type HELP for commands.")
            return
        if self.state in ("dead", "escaped"):
            if e.key == pygame.K_RETURN and self.dead_t > 1.0:
                self.restart(self.mode); self.state = "play"
            return
        mv = {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}
        if e.key in mv:
            self.held = mv[e.key]; self.held_key = e.key; self.rep = 0.22; self.try_move(*mv[e.key])
        elif e.key == pygame.K_RETURN: self.command(self.typed.strip()); self.typed = ""
        elif e.key == pygame.K_BACKSPACE: self.typed = self.typed[:-1]
        elif e.unicode and e.unicode.isprintable() and len(self.typed) < 22: self.typed += e.unicode

    hud_bump = 0.0
    dt = 1/30
    def update(self, dt):
        self.dt = dt or self.dt; self.t += dt
        if self.state == "play":
            self.monsters_tick(dt); self.since_combat += dt
            pc = self.cfg["player"]
            if pc["regen_per_sec"] and self.since_combat > pc["regen_delay"] and self.strength < pc["max_strength"]*pc["regen_cap_frac"]:
                self.regen_acc = getattr(self, "regen_acc", 0) + pc["regen_per_sec"]*dt
                if self.regen_acc >= 1: self.strength += int(self.regen_acc); self.regen_acc -= int(self.regen_acc)
        if self.state in ("dead", "escaped"): self.dead_t += dt
        self.stair_cd = max(0.0, self.stair_cd - dt)
        if self.stair_stale_key is not None and self.held_key != self.stair_stale_key: self.stair_stale_key = None
        self.atk_cd = max(0, self.atk_cd - dt)
        self.shake = max(0, self.shake - dt); self.hurt = max(0, self.hurt - dt)
        for f in self.floats: f[4] += dt
        self.floats = [f for f in self.floats if f[4] < 1.0]
        if self.lunge:
            self.lunge[2] += dt
            if self.lunge[2] > .15: self.lunge = None
        for m in self.room["mons"]: m["bite"] = max(0, m.get("bite", 0) - dt)
        if self.held and self.state == "play":     # held arrow: keep stepping
            self.rep -= dt
            if self.rep <= 0:
                self.try_move(*self.held); self.rep += 0.12
        k = min(1, dt*14)
        self.draw_x += (self.hx*T - self.draw_x)*k; self.draw_y += (self.hy*T - self.draw_y)*k
        for p in self.pops: p[3] += dt
        self.pops = [p for p in self.pops if p[3] < .8]
        self.hud_bump = max(0, self.hud_bump - dt*2)

    def box(self, surf, rect, title=None, accent=C["red"]):
        """Balatro-ish info box: rounded, drop shadow, chunky accent border"""
        sh = rect.move(0, 4); pygame.draw.rect(surf, (8, 6, 14), sh, border_radius=8)
        pygame.draw.rect(surf, (30, 32, 44), rect, border_radius=8)
        pygame.draw.rect(surf, accent, rect, 2, border_radius=8)
        if title:
            tr = pygame.Rect(rect.x+8, rect.y-15, self.font.size(title)[0]+14, 16)
            pygame.draw.rect(surf, accent, tr, border_radius=5)
            surf.blit(self.font.render(title, False, C["cream"]), (tr.x+7, tr.y+3))

    def wrap(self, text, width):
        out, line = [], ""
        for w in text.split(" "):
            if pixfont.width(line + " " + w) > width and line: out.append(line); line = w
            else: line = (line + " " + w).strip()
        out.append(line); return out

    def hazed(self, sp, key=None):
        """room 33: multiply a sprite into the garden view's haze (cached)"""
        c = self.__dict__.setdefault("_haze", {}); k = key or id(sp)
        if k not in c: h = sp.copy(); h.fill(setpiece.HAZE, special_flags=pygame.BLEND_RGBA_MULT); c[k] = h
        return c[k]

    def door_sprite(self):
        """barred grating door, one cell plus a 6px top bar that rises into the wall above"""
        if not hasattr(self, "_door_spr"):
            s = pygame.Surface((T, T + 6), pygame.SRCALPHA)
            pygame.draw.rect(s, (30, 26, 34), (2, 0, T - 4, T + 6))
            for k in range(3, T - 3, 3): pygame.draw.line(s, (150, 150, 165), (k, 1), (k, T + 5))
            for k in (4, 6 + T//2): pygame.draw.line(s, (110, 110, 125), (2, k), (T - 3, k))
            self._door_spr = s
        return self._door_spr

    def stencil(self):
        k = ("st", self.rid)
        if k not in self.room_cache:
            base = self.room_cache[self.rid][0]
            m = pygame.mask.from_threshold(base, (255, 0, 255), (1, 1, 1, 255))
            self.room_cache[k] = gfx.to_rgb(m.to_surface(setcolor=(255, 0, 255), unsetcolor=(0, 255, 0)))
            self.room_cache[k].set_colorkey((0, 255, 0))
        return self.room_cache[k]

    def make_vig(self, size):
        try: return self.make_vig_np(size)
        except Exception:
            w, h = size; v = pygame.Surface(size, pygame.SRCALPHA)
            for i in range(30): pygame.draw.rect(v, (6, 4, 14, int(150*(1-i/30)**2)), (i*4, i*3, w-i*8, h-i*6), 4, border_radius=30)
            return v

    def make_vig_np(self, size):
        w, h = size
        X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h), indexing="ij")
        a = np.clip((X*X*.6 + Y*Y*.8) ** 1.4 * 200, 0, 190).astype(np.uint8)
        v = pygame.Surface(size, pygame.SRCALPHA); v.fill((6, 4, 14, 255))
        pygame.surfarray.pixels_alpha(v)[:] = a
        return v

    ANIM_KINDS = {"angry demon": "demon", "big spider": "big_spider", "small spider": "small_spider",
                  "bat": "bat", "vampire": "vampire", "fairy": "fairy", "snake": "snake", "ugly ogre": "ogre"}   # full state-driven sets in assets/<kind>/
    def fountain_anim(self, kind):
        cache = self.__dict__.setdefault("_fount", {})
        if kind not in cache:
            try:
                d = os.path.join(HERE, "assets", "fountain"); man = json.load(open(os.path.join(d, "manifest.json")))
                sh = next(x for x in man["sheets"] if x["file"] == f"fountain_{kind}_full.png")
                an = man.get("animation", {})
                cache[kind] = dict(strip=pygame.image.load(os.path.join(d, sh["file"])).convert_alpha(), size=tuple(sh["frame_size"]),
                                   n=sh["frames"], fps=an.get("fps", 8), anchor=tuple(man["anchor"]["px"]))
            except Exception as e:
                print(f"[castle diag] fountain art unavailable ({kind}):", e); cache[kind] = None
        return cache[kind]

    def hero_anim(self):
        """assets/hero: pre-combined walk/idle x sword x helmet strips (anchor px / px_left from the manifest)"""
        if not hasattr(self, "_hero_anim"):
            try:
                d = os.path.join(HERE, "assets", "hero"); man = json.load(open(os.path.join(d, "manifest.json"))); st = {}
                for name, sv in man["states"].items():
                    if not name.startswith(("walk_", "idle_", "body_", "sword_", "helmet_", "necklace_glint")): continue
                    f = sv["files"]
                    st[name] = dict(right=pygame.image.load(os.path.join(d, next(x for x in f if x.endswith("_right.png")))).convert_alpha(),
                                    left=pygame.image.load(os.path.join(d, next(x for x in f if x.endswith("_left.png")))).convert_alpha(),
                                    durs=sv["frame_durations_ms"], loop=True, offs=sv.get("frame_anchor_offsets"))
                A = man["anchor"]
                self._hero_anim = dict(states=st, size=tuple(man["frame_size"]), anchor=tuple(A["px"]), anchor_l=tuple(A.get("px_left", A["px"])))
            except Exception as e:
                print("[castle diag] hero art unavailable, using built-in sprite:", e); self._hero_anim = None
        return self._hero_anim

    def hero_overlays(self):
        """worn things drawn on the hero (#27 necklace, #26 backpack); art drops in at assets/hero_overlays/<name>/"""
        return ((["chainmail"] if self.mail_on() else []) + (["backpack"] if self.backpack() else [])   # draw order: mail, straps, necklace
                + [w for w in ("necklace",) if self.worn(w)])

    def overlay_strip(self, name, state, side, layer=""):
        """hero overlay strip: assets/hero_overlays/<name>/[back_]<state>_<side>.png, else [back_]<walk|idle>_<side>.png,
        else [back_]<name>_<side>.png; same frame size/anchor/timing as the hero strip it sits on. back_ = drawn behind
        the hero (e.g. the pack behind the cloak), plain = in front. Missing art = no overlay (None)."""
        cache = self.__dict__.setdefault("_hero_ovl", {}); key = (name, state, side, layer)
        if key not in cache:
            d = os.path.join(HERE, "assets", "hero_overlays", name); cache[key] = None
            for f in (f"{layer}{state}_{side}.png", f"{layer}{state.split('_')[0]}_{side}.png", f"{layer}{name}_{side}.png"):
                if os.path.exists(os.path.join(d, f)):
                    try: cache[key] = pygame.image.load(os.path.join(d, f)).convert_alpha()
                    except Exception as e: print(f"[castle diag] hero overlay {name} unavailable:", e)
                    break
        return cache[key]

    def compose_hero(self, kind, sword, helm, side, k):
        """hero frame with worn overlays. Order (layer_order): back layers (pack behind the cloak), body,
        front overlays (pack straps, necklace), sword, helmet. With the separate body/sword/helmet strips that order is
        exact; without them the pre-composited strip stands in for body+sword+helmet and the front overlays go on top."""
        ha = self.hero_anim(); S = ha["states"]; fw, fh = ha["size"]; state = f"{kind}_sword{int(sword)}_helmet{int(helm)}"
        fr = lambda st, i: (((i % max(1, st.get_width() // fw))*fw, 0, fw, fh))
        names = self.hero_overlays()
        back = [b for b in (self.overlay_strip(n, state, side, "back_") for n in names) if b is not None]
        front = []
        for n in names:
            st = self.overlay_strip(n, state, side)
            if st is None: continue
            gl = S.get("necklace_glint")
            if n == "necklace" and kind == "idle" and k == 0 and gl:        # optional ruby sparkle on the idle rest frame
                front.append((gl[side], self.anim_frame(gl, self.t))); continue
            front.append((st, k))
        comp = S[state]
        if not back and not front: return comp[side].subsurface(fr(comp[side], k))
        out = pygame.Surface((fw, fh), pygame.SRCALPHA)
        for b in back: out.blit(b, (0, 0), fr(b, k))
        layered = front and all(f"{l}_{kind}" in S for l in ("body", "sword", "helmet"))
        base = S[f"body_{kind}"] if layered else comp
        out.blit(base[side], (0, 0), fr(base[side], k))
        for st, i in front: out.blit(st, (0, 0), fr(st, i))
        if layered:
            for on, l in ((sword, "sword"), (helm, "helmet")):
                if on: out.blit(S[f"{l}_{kind}"][side], (0, 0), fr(S[f"{l}_{kind}"][side], k))
        return out

    def anim_kind(self, name): return self.ANIM_KINDS.get(name.lower())

    def mon_anim(self, kind):
        """manifest-driven monster animation set: states -> {right,left strips, durs, loop, offs}; None if unavailable"""
        cache = self.__dict__.setdefault("_manim", {})
        if kind not in cache:
            try:
                d = os.path.join(HERE, "assets", kind); man = json.load(open(os.path.join(d, "manifest.json")))
                fw, fh = man["frame_size"]; st = {}
                for name, sv in man["states"].items():
                    n = sv["frames"]; files = sv["files"]
                    r = pygame.image.load(os.path.join(d, next(f for f in files if f.endswith("_right.png")))).convert_alpha()
                    l = pygame.image.load(os.path.join(d, next(f for f in files if f.endswith("_left.png")))).convert_alpha()
                    durs = sv.get("frame_durations_ms") or [int(1000 / sv.get("fps", 8))] * n
                    hit = next((int(w) for w in re.findall(r"frame (\d+) = hit frame|on frame (\d+)", sv.get("note", "")) for w in w if w), 2)
                    st[name] = dict(right=r, left=l, durs=durs, loop=sv.get("loop", True), offs=sv.get("frame_anchor_offsets") or [[0, 0]] * n, hit=hit)
                st.setdefault("walk", st.get("move") or st.get("fly") or st["idle"])
                if "death" not in st:      # separate death folder (e.g. assets/snake_death)
                    da = self.death_anim(kind)
                    if da: st["death"] = dict(right=da["right"], left=da["left"], durs=da["durs"], loop=False, offs=da["offs"], hit=0, size=da["size"], anchor=da["anchor"], anchor_l=da["anchor_l"])
                A = man["anchor"]
                cache[kind] = dict(states=st, size=(fw, fh), anchor=tuple(A["px"]), anchor_l=tuple(A.get("px_left", A["px"])))
            except Exception as e:
                print(f"[castle diag] {kind} sprite art unavailable, using fallback:", e); cache[kind] = None
        return cache[kind]

    @staticmethod
    def anim_frame(state, t, loop=None):
        durs = state["durs"]; tot = sum(durs); t_ms = t * 1000
        if loop if loop is not None else state["loop"]: t_ms %= tot
        elif t_ms >= tot: return None
        k = 0
        while k < len(durs) - 1 and t_ms >= sum(durs[:k+1]): k += 1
        return k

    DEATH_KINDS = ("snake", "ogre")       # monsters with death strips in assets/<kind>_death/
    def death_kind(self, name):
        n = name.lower()
        return next((k for k in self.DEATH_KINDS if k in n), None)

    def death_anim(self, kind):
        """generic manifest-driven death strip loader: assets/<kind>_death/{manifest.json,<kind>_death_right/left.png}"""
        cache = self.__dict__.setdefault("_death", {})
        if kind not in cache:
            try:
                d = os.path.join(HERE, "assets", f"{kind}_death"); man = json.load(open(os.path.join(d, "manifest.json")))
                n = man.get("frames", 12); fw, fh = man.get("frame_size", [64, 48])
                fr = {k: pygame.image.load(os.path.join(d, f"{kind}_death_{k}.png")).convert_alpha() for k in ("right", "left")}
                durs = man.get("frame_durations_ms") or [1000 // man.get("fps", 10)] * n
                A = man.get("anchor", {}); apx = tuple(A.get("px", [fw//2, fh - 4]))
                cache[kind] = dict(fr, durs=durs, size=(fw, fh), anchor=apx, anchor_l=tuple(A.get("px_left", apx)),
                                   offs=man.get("frame_anchor_offsets") or [[0, 0]] * n)
            except Exception as e:
                print(f"[castle diag] {kind} death art unavailable:", e); cache[kind] = None
        return cache[kind]

    def mon_sprite(self, name):
        n = name.lower()
        if "snake" in n: return self.snake
        if "ogre" in n: return self.ogre
        key = ("mon", n)
        if key not in self.item_spr:
            tint = {"demon": (90, 0, 0), "vampire": (40, 0, 60), "fairy": (40, 90, 110), "spider": (0, 0, 0), "bat": (20, 0, 30)}
            t = next((v for k, v in tint.items() if k in n), (30, 30, 30))
            sp = self.ogre.copy()
            if "spider" in n or "bat" in n or "fairy" in n:
                f = .6 if "small" in n or "bat" in n or "fairy" in n else .85
                sp = pygame.transform.scale(sp, (int(sp.get_width()*f), int(sp.get_height()*f)))
                sp.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGBA_SUB)
            sp.fill(t + (0,), special_flags=pygame.BLEND_RGBA_ADD)
            self.item_spr[key] = sp
        return self.item_spr[key]

    def item_art(self, name):
        """item pack (assets/items/manifest.json): {floor, small, glint[frames]} or None"""
        key = ("art", name)
        if key not in self.item_spr:
            a = None; n = name.lower()
            if not any(k in n for k in KEEP_ART):
                d = os.path.join(HERE, "assets", "items")
                try:
                    man = json.load(open(os.path.join(d, "manifest.json")))
                    e = next((v for k, v in man["items"].items() if v["name"].lower() == n or k.lower().replace("_", " ") == n), None)
                    if e:
                        ld = lambda f: pygame.image.load(os.path.join(d, f)).convert_alpha()
                        a = dict(floor=ld(e["floor"]), small=ld(e["small"]) if e.get("small") else None, glint=None,
                                 dur=man["glint"]["frame_durations_ms"], anchor=tuple(man["floor"]["anchor"]),
                                 sanchor=tuple(man["small"]["anchor"]))
                        if e.get("glint"):
                            g = ld(e["glint"]); fw = man["glint"]["frame_size"][0]
                            a["glint"] = [g.subsurface((i*fw, 0, fw, g.get_height())) for i in range(g.get_width() // fw)]
                except Exception as ex: print("[castle diag] item art unavailable:", name, ex)
                if a is None:   # per-item folder: assets/<name>/manifest.json "item" (floor/small + anchors), e.g. #26 backpack
                    pd = os.path.join(HERE, "assets", n.replace(" ", "_"))
                    try:
                        if os.path.exists(os.path.join(pd, "manifest.json")):
                            e = json.load(open(os.path.join(pd, "manifest.json")))["item"]
                            ld = lambda f: pygame.image.load(os.path.join(pd, f)).convert_alpha()
                            a = dict(floor=ld(e["floor"]), small=ld(e["small"]) if e.get("small") else None, glint=None, dur=[],
                                     anchor=tuple(e["floor_anchor"]), sanchor=tuple(e["small_anchor"]) if e.get("small_anchor") else None)
                    except Exception as ex: print("[castle diag] item art unavailable:", name, ex); a = None
                if a is None:   # per-item file by name: assets/items/<name>.png
                    p = os.path.join(d, n.replace(" ", "_") + ".png")
                    if os.path.exists(p):
                        im = pygame.image.load(p).convert_alpha(); a = dict(floor=im, small=None, glint=None, dur=[], anchor=(im.get_width()//2, im.get_height()-1), sanchor=None)
            self.item_spr[key] = a
        return self.item_spr[key]

    def item_frame(self, name, small=False):
        """current sprite for an item: glint loop for treasures (frame durations from the manifest)"""
        a = self.item_art(name)
        if not a: return self.item_sprite(name)
        if small and a["small"]: return a["small"]
        if a["glint"] and not small:
            tot = sum(a["dur"]); ms = (self.t * 1000 + (hash(name) % 997)) % tot
            for i, dd in enumerate(a["dur"]):
                if ms < dd: return a["glint"][i]
                ms -= dd
        return a["floor"]

    def item_sprite(self, name):
        if name not in self.item_spr:
            n = name.lower(); a = None if any(k in n for k in KEEP_ART) else self.item_art(name)
            self.item_spr[name] = a["floor"] if a else (art3.make_lamp() if "lamp" in n else art3.make_sword_item() if "sword" in n
                                   else art3.make_helmet_item() if "helmet" in n else make_backpack() if n == "backpack" else make_chainmail() if n == "chain mail" else art.make_item(name))
        return self.item_spr[name]

    def statue_frame(self):
        """room 19 statue (batch 2): glint loop while the necklace is on it, plain after GET NECKLACE"""
        c = self.__dict__.setdefault("_statue", {})
        if not c:
            d = os.path.join(HERE, "assets", "statue")
            try:
                man = json.load(open(os.path.join(d, "manifest.json"))); fw, fh = man["frame_size"]
                g = pygame.image.load(os.path.join(d, "statue_necklace_glint.png")).convert_alpha()
                c.update(ok=True, glint=[g.subsurface((i*fw, 0, fw, fh)) for i in range(g.get_width() // fw)],
                         dur=man["states"]["with_necklace_glint"]["frame_durations_ms"],
                         plain=pygame.image.load(os.path.join(d, "statue_plain.png")).convert_alpha(),
                         necklace=pygame.image.load(os.path.join(d, "statue_necklace.png")).convert_alpha(), size=(fw, fh))
            except Exception as e: print("[castle diag] statue art unavailable:", e); c["ok"] = False
        if not c["ok"]: return None
        if self.room.get("statue_state") == "plain": return c["plain"]
        if not c["glint"]: return c["necklace"]
        ms = (self.t * 1000) % sum(c["dur"])
        for i, dd in enumerate(c["dur"]):
            if ms < dd: return c["glint"][i]
            ms -= dd
        return c["necklace"]

    def statue_glint_hook(self, frame_index):
        """hook for an extra sparkle/light on the necklace; currently adds nothing beyond the art's own glint"""
        return None

    def drawer_rect(self):
        """front of the desk ('@' block): returns (x, y, w, h) in room pixels for the drawer placeholder"""
        g = self.room["grid"]; cells = [(x, y) for y in range(ROWS) for x in range(COLS) if g[y][x] == "@"]
        if not cells: return None
        x0, x1 = min(c[0] for c in cells), max(c[0] for c in cells); y1 = max(c[1] for c in cells)
        cx = (x0 + x1 + 1) * T // 2
        return cx - 8, y1*T + T - 7, 16, 6

    def make_chest(self):
        c = pygame.Surface((11, 9), pygame.SRCALPHA)
        pygame.draw.rect(c, (120, 76, 40), (0, 3, 11, 6)); pygame.draw.rect(c, (150, 98, 52), (0, 0, 11, 4), border_radius=2)
        pygame.draw.line(c, (220, 170, 70), (0, 4), (10, 4)); pygame.draw.rect(c, (240, 200, 90), (4, 3, 3, 3))
        pygame.draw.line(c, (220, 170, 70), (2, 0), (2, 8)); pygame.draw.line(c, (220, 170, 70), (8, 0), (8, 8))
        return art.outline(c)

    def pill(self, surf, rect, border):
        pygame.draw.rect(surf, (8, 6, 14), rect.move(0, 3), border_radius=6)
        pygame.draw.rect(surf, (22, 18, 34), rect, border_radius=6)
        pygame.draw.rect(surf, border, rect, 2, border_radius=6)
        pygame.draw.line(surf, (70, 60, 100), (rect.x+6, rect.y+3), (rect.right-7, rect.y+3))

    def render(self, surf):
        if not hasattr(self, 'ui') or self.ui.get_size() != (W, H):   # frame size follows the window (set_frame)
            self.ui = pygame.Surface((W, H), pygame.SRCALPHA)
            self.small = gfx.rgb((W // 2, H // 2)); swirl(self.t, self.small)
        if self.view_src.get_size() != (VIEW.w // ZOOM, VIEW.h // ZOOM):
            self.view_src = gfx.rgb((VIEW.w // ZOOM, VIEW.h // ZOOM)); self.view_vig = self.make_vig(VIEW.size)
        if self.state == 'title': self.ui.fill((0, 0, 0, 0))
        self.frame_n = getattr(self, "frame_n", 0) + 1
        if self.frame_n % (3 if W <= BASE_W else 6) == 1 or getattr(self, "small_big", None) is None or self.small_big.get_size() != (W, H):
            swirl(self.t, self.small); self.small_big = pygame.transform.scale(self.small, (W, H))   # big frames: refresh less often
        surf.blit(self.small_big, (0, 0))
        if self.state == "title":   # title layout is 640x360: centre it in bigger frames
            if (W, H) == (BASE_W, BASE_H): return self.render_title(surf)
            ox, oy_ = (W - BASE_W) // 2, (H - BASE_H) // 2; full_ui = self.ui
            sub = surf.subsurface((ox, oy_, BASE_W, BASE_H)); self.ui = full_ui.subsurface((ox, oy_, BASE_W, BASE_H))
            gw, gh = W, H; globals().update(W=BASE_W, H=BASE_H)
            try: return self.render_title(sub)
            finally: globals().update(W=gw, H=gh); self.ui = full_ui
        L = self.layer
        base, TOP = self.room_cache[self.rid]
        L.fill((255, 0, 255)); L.blit(base, (0, 0))
        g = self.room["grid"]; oy = TOP
        for ch, sx, sy, sw_, sh_ in self.room.setdefault("stairs_", art3.stair_blocks(g)):   # optional dust on 1x1 up stairs
            if ch == "U" and sw_ == sh_ == 1 and not art3.spiral_block(self.rid, sx, sy):    # no dust on the spiral
                strip = art3.stair_img(f"stairs_up_{art3.stair_variant(self.rid, self.room)}_1x1_dust_strip.png")
                if strip: L.blit(strip, (sx*T, sy*T + oy), (16*(int(self.t*4) % 4), 0, 16, 16))
        dr = []   # depth-sorted drawables: (sort_y, sprite, x, y, shadow_w)
        sp = art3.spiral(self.rid)
        if sp and not sp["floor"]:      # rising spiral: the hero passes behind it on the row above the block
            dr.append((sp["sort"], sp["img"], sp["world"][0] - sp["anchor"][0], sp["world"][1] - sp["anchor"][1], 0, True))
        if self.rid == 1:
            rx, ry = COLS*T//2 - self.rug.get_width()//2, ROWS*T//2 - self.rug.get_height()//2
            L.blit(self.rug, (rx, ry + oy))
        for y in range(ROWS):
            for x in range(COLS):
                ch = g[y][x]
                if ch in "*+":
                    b = self.bush[ch][(x*3 + y) % 4]
                    if self.rid == setpiece.BALCONY and setpiece.underlay(self.rid): b = self.hazed(b)
                    dr.append((y*T + T, b, x*T + T//2 - b.get_width()//2, y*T + T - b.get_height() + 3, b.get_width() - 6))
        lights = []
        if self.rid == 1:   # torches flanking the gate and the north doorway
            for tx, ty in ((9, 16), (14, 16), (9, 1), (14, 1)):
                X = tx*T + (9 if tx == 9 else 3)
                dr.append((ty*T + T + 2, self.torch, X - 3, ty*T - 2, 0)); lights.append((X, ty*T + 1, "warm"))
        dro = self.room.get("drawer")
        dsk = setpiece.desk_sprite(self.rid, self.room)
        if dsk: dr.append((dsk[3], dsk[0], dsk[1], dsk[2], 0, True))   # desk: closed / open_item / open_empty
        setpiece.draw_objects(self.rid, self.room, self.t, dr, lights)
        setpiece.draw_hooks(self.rid, self.room, dr, self.t)
        setpiece.draw_beds(self.rid, self.room, dr)                              # beds, sorted by footprint bottom
        setpiece.draw_rail(self.rid, self.room, dr)                    # room 33 balcony railing
        if self.rid == setpiece.LAB:                                      # room 66 laboratory set pieces
            setpiece.draw_lab_glow(L, oy, self.t); setpiece.draw_lab(self.room, self.t, dr, lights)
        if self.rid in DRAWER_ROOMS and self.drawer_rect() and not dsk:   # desk drawer placeholder (closed / open with the item inside)
            dx_, dy_, dw_, dh_ = self.drawer_rect(); dsp = pygame.Surface((dw_, dh_ + 4), pygame.SRCALPHA)
            if dro == "open":
                pygame.draw.rect(dsp, (60, 36, 20), (0, 2, dw_, dh_ + 2)); pygame.draw.rect(dsp, (24, 14, 8), (2, 3, dw_ - 4, dh_ - 1))
                pygame.draw.rect(dsp, (120, 80, 44), (0, dh_ + 1, dw_, 3))
            else:
                pygame.draw.rect(dsp, (96, 62, 34), (0, 0, dw_, dh_)); pygame.draw.rect(dsp, (40, 24, 12), (0, 0, dw_, dh_), 1)
                pygame.draw.rect(dsp, (200, 170, 90), (dw_//2 - 1, dh_//2 - 1, 2, 2))
            dr.append((dy_ + dh_ + 1, dsp, dx_, dy_, 0))
        st_cell = next(((x, y) for y in range(ROWS) for x in range(COLS) if self.room["grid"][y][x] == "$"), None)
        for it in self.room["items"]:
            if st_cell and (it["x"], it["y"]) == st_cell and self.statue_frame(): continue   # the statue art shows the necklace
            if it.get("chainmail") and setpiece.mail_on_stand(self.rid, self.room): continue   # the full stand shows it
            in_drawer = dro == "open" and "desk" in it.get("hidden", "") and self.rid in DRAWER_ROOMS
            a = self.item_art(it["name"])
            if in_drawer and dsk: continue          # the open_item desk art shows it
            if in_drawer:
                spr = self.item_frame(it["name"], small=True); dx_, dy_, dw_, dh_ = self.drawer_rect()
                dr.append((dy_ + dh_ + 2, spr, dx_ + dw_//2 - spr.get_width()//2, dy_ + dh_ - spr.get_height(), 0, True))
                continue
            spr = self.item_frame(it["name"]) if a else self.item_sprite(it["name"])
            bob = math.sin(self.t*3 + it["x"]) * 1.0
            X, Y = it["x"]*T + T//2, it["y"]*T + T
            if a: dr.append((Y, spr, X - a["anchor"][0], Y - 1 - a["anchor"][1] - 2 + bob, 0, True))       # shadow_baked
            else: dr.append((Y, spr, X - spr.get_width()//2, Y - spr.get_height() - 2 + bob, 12, True))
            if it.get("treasure") or "lamp" in it["name"].lower(): lights.append((X, Y - 6, "big"))
        sfy = next((y for y in range(ROWS) if "," in g[y]), None)
        is_statue = sfy is not None and sfy + 1 < ROWS and "$" in g[sfy + 1]
        if sfy is not None and not is_statue and not (sfy + 1 < ROWS and "?" in g[sfy + 1]): sfy = None   # mirror (room 67) etc.: not a fountain
        if is_statue:   # room 19 statue: drawn like the fountain footprint, but its own art; FILL stays room-18-only
            fx = g[sfy].index(","); sp = self.statue_frame()
            if sp: dr.append(((sfy+3)*T, sp, fx*T, (sfy+3)*T - sp.get_height(), 0, True))
            else: dr.append(((sfy+3)*T, self.fountain, fx*T, sfy*T - 2, 44))
        elif sfy is not None:   # fountain (rooms 18, 33): animated strip, anchor (24,59)
            fy = sfy; fx = g[fy].index(",")
            fa = self.fountain_anim("balcony" if self.rid == 33 else "garden")
            if fa:
                k = int(self.t * fa["fps"]) % fa["n"]; fw, fh = fa["size"]; ax, ay = fa["anchor"]
                fs_ = fa["strip"].subsurface((k*fw, 0, fw, fh))
                if self.rid == setpiece.BALCONY and setpiece.underlay(self.rid): fs_ = self.hazed(fs_, ("fountain33", k))
                dr.append(((fy+3)*T, fs_, fx*T + 24 - ax, (fy+3)*T - 1 - ay, 44))
            else:
                dr.append(((fy+3)*T, self.fountain, fx*T, fy*T - 2, 44))
        dc = self.room.get("decor", {})
        for o in dc.get("objects", []):   # decor objects: bottom-centre at (x*16+8, y*16+16)
            sp = decor.surf_for(o)
            dr.append((o["y"]*T + T, sp, o["x"]*T + 8 - sp.get_width()//2, o["y"]*T + T - sp.get_height(),
                       0 if decor.prop(o["file"]).get("shadow_baked") else max(8, sp.get_width() - 4)))
        for a_ in dc.get("anim", []):     # lit sconces: 8 fps, per-room phase, warm point light at +(7,4)
            fx_, fy_ = decor.wall_pos(a_, oy, 8)
            sp = decor.surf_for(a_, int((self.t + dc["phase"]) * (a_["fps"] or 8)))
            L.blit(sp, (fx_, fy_))
            if a_["light"]: lights.append((fx_ + 7, fy_ - oy + 4, "warm"))
        for m in self.room["mons"]:
            spr = self.mon_sprite(m["name"])
            m.setdefault("dx_", m["x"]*T); m.setdefault("dy_", m["y"]*T)
            k = min(1, self.dt*10); m["dx_"] += (m["x"]*T - m["dx_"])*k; m["dy_"] += (m["y"]*T - m["dy_"])*k
            if m.get("face", 1) < 0: spr = pygame.transform.flip(spr, True, False)
            ak = self.anim_kind(m["name"]); an = ak and self.mon_anim(ak)
            if an:
                side = "left" if m.get("face", 1) < 0 else "right"; S = an["states"]
                if not m["alive"]:
                    st_, k = S["death"], self.anim_frame(S["death"], m.get("dead_t", 0), loop=False)
                    if k is None: continue           # played once: removed
                elif m.get("atk_t0") is not None and self.anim_frame(S["attack"], self.t - m["atk_t0"]) is not None:
                    st_ = S["attack"]; k = self.anim_frame(st_, self.t - m["atk_t0"])
                elif abs(m["dx_"] - m["x"]*T) + abs(m["dy_"] - m["y"]*T) > 1:
                    st_ = S["walk"]; k = self.anim_frame(st_, self.t)
                else:
                    st_ = S["idle"]; k = self.anim_frame(st_, self.t + (m["x"] * .37))
                fw, fh = st_.get("size", an["size"]); ax, ay = st_.get("anchor_l" if side == "left" else "anchor") or an["anchor_l" if side == "left" else "anchor"]; ox, oy_ = st_["offs"][k] if k < len(st_["offs"]) else (0, 0)
                fr = st_[side].subsurface((k*fw, 0, fw, fh))
                if m["alive"] and m["flash"] > 0:
                    fr = fr.copy(); fr.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
                X, Y = m["dx_"] + T//2, m["dy_"] + T     # ground anchor (hover is baked into bat/fairy frames)
                dr.append((Y, fr, X - ax + ox, Y + 3 - ay + oy_, max(10, fw // 2) if m["alive"] else 0, True)); continue
            kind = self.death_kind(m["name"])
            if not m["alive"] and kind and self.death_anim(kind):
                da = self.death_anim(kind); durs = da["durs"]
                t_ms = m.get("dead_t", 0) * 1000; k = 0
                while k < len(durs) and t_ms >= sum(durs[:k+1]): k += 1
                if k >= len(durs): continue          # played once: monster removed
                strip = da["left" if m.get("face", 1) < 0 else "right"]
                ax, ay = da["anchor_l" if m.get("face", 1) < 0 else "anchor"]; ox, oy_ = da["offs"][k] if k < len(da["offs"]) else (0, 0)
                X, Y = m["dx_"] + T//2, m["dy_"] + T + 3        # sprite bottom-centre (feet) in room coords
                fw, fh = da["size"]
                dr.append((Y - 3, strip.subsurface((k*fw, 0, fw, fh)), X - ax + ox, Y - ay + oy_, 0, True)); continue
            if not m["alive"]:     # death: squash flat and fade
                u = min(1, m.get("dead_t", 0) / .5)
                spr = pygame.transform.scale(spr, (int(spr.get_width()*(1+u*.4)), max(2, int(spr.get_height()*(1-u*.8)))))
                spr.set_alpha(int(255*(1-u*.6)))
            elif m["flash"] > 0:
                spr = spr.copy(); spr.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
            X, Y = m["dx_"] + T//2, m["dy_"] + T
            bx = by = 0
            if m.get("bite", 0) > 0:
                bx = (self.hx*T - m["x"]*T) * .25 * math.sin(m["bite"]/.2*math.pi); by = (self.hy*T - m["y"]*T) * .25 * math.sin(m["bite"]/.2*math.pi)
            dr.append((Y, spr, X - spr.get_width()//2 + bx, Y - spr.get_height() + 3 + by + (int(math.sin(self.t*2)) if m["alive"] else 0), 40 if m["alive"] else 0, True))
        ha = self.hero_anim()
        if ha:
            moving = abs(self.draw_x - self.hx*T) + abs(self.draw_y - self.hy*T) > .5 or self.held
            kind = "walk" if moving else "idle"; sw, hm = self.has("sword"), self.helmet_on()
            st_ = ha["states"][f"{kind}_sword{int(sw)}_helmet{int(hm)}"]; side = "left" if self.facing < 0 else "right"
            k = self.anim_frame(st_, self.t)
            hero = self.compose_hero(kind, sw, hm, side, k); hax, hay = ha["anchor_l" if side == "left" else "anchor"]
        else:
            hero = self.heroes[(self.has("sword"), self.helmet_on())][self.step % 2]
            if self.facing < 0: hero = pygame.transform.flip(hero, True, False)
        if self.hurt > 0:
            hero = hero.copy(); hero.fill((90, 0, 0, 0) if self.hurt > .12 else (40, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        hx, hy = self.draw_x + T//2, self.draw_y + T
        if self.lunge:
            u = math.sin(self.lunge[2]/.15*math.pi) * 6; hx += self.lunge[0]*u; hy += self.lunge[1]*u
        if ha: dr.append((hy, hero, hx - hax, hy + 3 - hay, 18, True))
        else: dr.append((hy, hero, hx - 11 if self.facing > 0 else hx - hero.get_width() + 11, hy - hero.get_height() + 2, 18, True))
        over = []   # sprites flagged True (hero, monsters, items, statue, desk, hooks, setpiece objects, doors) may cross the room
                    # outline (corridor joins, tall pieces); scenery such as bushes and fountains is still clipped to it
        for d_ in sorted(dr, key=lambda d: d[0]):
            sy, spr, x, y, sw = d_[:5]
            if len(d_) > 5 and d_[5]: over.append((spr, x, y))
            if sw:
                sh = self.shadows[min(self.shadows, key=lambda k: abs(k - sw))]
                L.blit(sh, (x + spr.get_width()//2 - sh.get_width()//2 + 2, sy - sh.get_height()//2 - 1 + oy))
            L.blit(spr, (x, y + oy))
        sm = getattr(self, "smoke", None)
        if sm and self.rid == MIRROR_ROOM:   # puff of smoke over the sprites, under light/darkness; old mirror fades underneath
            u = self.t - sm["t0"]
            if sm["sprite"] and u < .45:
                sp, sx, sy = sm["sprite"]; sp = sp.copy(); sp.set_alpha(int(255 * (1 - u / .45))); L.blit(sp, (sx, sy + oy))
            k = next((i for i, e in enumerate(sm["ends"]) if u < e), None)
            fr = setpiece.frame(sm["file"], sm["fw"], k) if k is not None else None
            if fr: L.blit(fr, (sm["pos"][0], sm["pos"][1] + oy))
            if k in (0, 1) : lights = list(lights) + [(*sm["core"], (24, (255, 240, 170)))]   # brief warm flash (manifest, optional)
            if k is None and u >= .45: self.smoke = None
        amb = self.room.get("theme", {}).get("ambient")       # outdoor dusk: dim the lit scene before the lights add up
        if amb and setpiece.underlay(self.rid, self.room): L.fill(tuple(amb), special_flags=pygame.BLEND_RGB_MULT)
        flick = 1 + .06*math.sin(self.t*9) + .04*math.sin(self.t*23)
        for X, Y, kind in lights:
            if kind not in self.lights: self.lights[kind] = art.light(*kind)    # (radius, colour) from a set-piece manifest
            lt = self.lights[kind]
            lt = pygame.transform.scale(lt, (int(lt.get_width()*flick), int(lt.get_height()*flick)))
            L.blit(lt, (X - lt.get_width()//2, Y - lt.get_height()//2 + oy), special_flags=pygame.BLEND_RGB_ADD)
        for dx_, dy_ in self.room.get("doors", []):
            if g[dy_][dx_] == "G":   # barred grating doors (rooms 68, 82): may cross the outline at corridor joins
                ds = self.door_sprite(); X, Y = dx_*T, dy_*T - 6
                L.blit(ds, (X, Y + oy)); over.append((ds, X, Y))
        if self.rid in DARK:
            lamp = self.has("lamp")
            dk = self.dark_lit if lamp else self.dark_full
            L.blit(dk, (hx - dk.get_width()//2, hy + oy - 8 - dk.get_height()//2))
        for fn, cell, r_, c_, pos, hsh in self.room.get("emissive", []):   # room 83 gem glints: never darkened
            sh_ = art3.tile_sheet(fn, cell)
            if sh_:
                g_ = sh_[r_][c_ % len(sh_[r_])]; a_ = int(255 * (0.6 + 0.4 * math.sin(self.t * 1.5 + hsh)))
                g_.set_alpha(a_); L.blit(g_, pos); g_.set_alpha(None)
        st = self.stencil()
        if over:   # doors, gates and set pieces (hooks, setpiece:true objects) may cross the outline: cut them out of the mask
            st = st.copy()   # (after the darkness pass, so a restored part stays as dark as the rest of the room)
            for sp, x, y in over: pygame.mask.from_surface(sp).to_surface(st, setcolor=(0, 255, 0), unsetcolor=None, dest=(int(x), int(y) + oy))
        L.blit(st, (0, 0))
        # camera: follow hero, clamp to room bounds, zoom x ZOOM
        vw, vh = VIEW.w // ZOOM, VIEW.h // ZOOM
        tx = hx - vw/2; ty = hy + oy - 16 - vh/2
        tx = max(-8, min(COLS*T + 8 - vw, tx)); ty = max(0, min(ROWS*T + oy + 2 - vh, ty))
        if self.rid in setpiece.TALL:   # keep the tall throne in frame (HUD covers ~16px at the top) while the hero stays visible
            ty = max(0, min(ty, max(6, hy + oy - vh + 30)))
        if vw >= COLS*T + 16: tx = -(vw - COLS*T) // 2              # whole room fits horizontally: centre, no scrolling
        if vh >= ROWS*T + oy + 2: ty = -(vh - (ROWS*T + oy)) // 2   # ... vertically
        if not hasattr(self, "cam") or self.cam_room != self.rid: self.cam = [tx, ty]; self.cam_room = self.rid
        self.cam[0] += (tx - self.cam[0]) * min(1, self.dt*6); self.cam[1] += (ty - self.cam[1]) * min(1, self.dt*6)
        sk = self.shake*14
        cx, cy = int(self.cam[0] + random.uniform(-sk, sk)), int(self.cam[1] + random.uniform(-sk, sk))
        V = self.view_src; V.fill((255, 0, 255)); V.blit(L, (-cx, -cy))
        big = pygame.transform.scale(V, VIEW.size); big.set_colorkey((255, 0, 255))
        surf.blit(big, VIEW.topleft); surf.blit(self.view_vig, VIEW.topleft)
        self.w2s = lambda wx, wy: (VIEW.x + (wx - cx)*ZOOM, VIEW.y + (wy + oy - cy)*ZOOM)
        for it, x, y, a in self.pops:   # pickup juice
            spr = self.item_sprite(it["name"])
            u = a / .8
            yy = y - math.sin(min(1, u*1.6) * math.pi) * 18 - u*6
            sc = (1 + .6*math.sin(u*math.pi*3) * (1-u)) * ZOOM
            s2 = pygame.transform.scale(spr, (int(spr.get_width()*sc), int(spr.get_height()*(2*ZOOM - sc))))
            s2.set_alpha(int(255*(1-u**3)))
            px_, py_ = self.w2s(x + T/2, yy)
            surf.blit(s2, (px_ - s2.get_width()/2, py_))
        # UI goes on its own layer, composited after the CRT warp so pixel text stays crisp
        surf = self.ui; surf.fill((0, 0, 0, 0))
        # HUD pill top-left with chest icon
        hb = self.hud_bump
        r = pygame.Rect(6, 6, 112, 20)
        self.pill(surf, r, (120, 84, 170))
        surf.blit(self.chest, (r.x + 7, r.y + 5 - int(hb*4)))
        surf.blit(pixfont.render("TREASURES", (226, 222, 236)), (r.x + 23, r.y + 7))
        surf.blit(pixfont.render(f"{self.treasures()}/13", (232, 176, 70)), (r.x + 82, r.y + 7 - int(hb*3)))
        # strength pill (red, pulses when hurt) + score pill
        r2 = pygame.Rect(124, 6, 128, 20)
        self.pill(surf, r2, (200, 70, 70) if self.hurt <= 0 else (255, 140, 120))
        heart = pixfont.render("<3", (240, 90, 90)) if False else None
        frac = self.strength / self.cfg["player"]["max_strength"]
        if self.cfg["player"]["hud_bar"]:
            pygame.draw.rect(surf, (40, 20, 30), (r2.x + 8, r2.y + 6, 70, 8), border_radius=3)
            pygame.draw.rect(surf, (220, 70, 70) if frac > .3 else (255, 120, 60), (r2.x + 8, r2.y + 6, int(70*frac), 8), border_radius=3)
            pygame.draw.line(surf, (255, 170, 160), (r2.x + 10, r2.y + 7), (r2.x + 6 + int(70*frac), r2.y + 7))
            surf.blit(pixfont.render(str(self.strength), (240, 220, 220)), (r2.x + 84, r2.y + 7))
        else:
            surf.blit(pixfont.render(f"STRENGTH {self.strength}", (240, 220, 220)), (r2.x + 10, r2.y + 7))
        if self.has("wine flask"):
            fl = pixfont.render("FLASK: " + ("WATER" if self.flask_full else "EMPTY"), (120, 190, 230) if self.flask_full else (170, 160, 180))
            surf.blit(fl, (356, 13))
        r3 = pygame.Rect(258, 6, 92, 20); self.pill(surf, r3, (90, 160, 110))
        surf.blit(pixfont.render(f"SCORE {self.score()}", (200, 240, 200)), (r3.x + 8, r3.y + 7))
        for fx, fy, txt, col, a in self.floats:      # damage numbers
            px_, py_ = self.w2s(fx, fy - a*14)
            t_ = pixfont.render(txt, col, 2 if a < .15 else 1)
            surf.blit(t_, (px_ - t_.get_width()/2, py_ - 18))
        # wide terminal panel
        P = PANEL
        self.pill(surf, P, (120, 84, 170))
        lines = []
        for l in self.log: lines += self.wrap(l.upper(), P.w - 40)
        y = P.y + 7
        for l in lines[-3:]:
            if l.startswith(">"):
                surf.blit(pixfont.render(">_", (110, 200, 90)), (P.x + 8, y)); l = l[1:].strip()
                surf.blit(pixfont.render(l, (110, 200, 90)), (P.x + 26, y))
            else:
                surf.blit(pixfont.render(l, (168, 128, 220)), (P.x + 26, y))
            y += 10
        cur = "_" if int(self.t*2) % 2 else " "
        surf.blit(pixfont.render(">_", (110, 200, 90)), (P.x + 8, P.bottom - 12))
        surf.blit(pixfont.render(self.typed + cur, (190, 240, 170)), (P.x + 26, P.bottom - 12))
        inv = "INV: " + (", ".join(i["name"] for i in self.inv) or "-")
        surf.blit(pixfont.render(inv, (200, 190, 220)), (6, H - 52 - 14)) if False else None
        rn = pixfont.render(self.room["name"], (120, 210, 200))
        surf.blit(rn, (W - rn.get_width() - 8, 10))
        if self.state in ("dead", "escaped"):
            won = self.state == "escaped"
            a = min(1, self.dead_t / .8)
            veil = pygame.Surface((W, H), pygame.SRCALPHA); veil.fill((0, 30, 20, int(170*a)) if won else (0, 20, 60, int(170*a)) if self.death == "drowned" else (40, 0, 10, int(170*a))); surf.blit(veil, (0, 0))
            box = pygame.Rect(W//2 - 150, H//2 - 80, 300, 110); self.pill(surf, box, (90, 200, 110) if won else (220, 70, 70))
            t1 = pixfont.render("YOU ESCAPED THE CASTLE!" if won else ("YOU DROWNED" if getattr(self, "death", "") == "drowned" else "YOU HAVE BEEN SLAIN"), (140, 240, 140) if won else (255, 110, 100), 2); surf.blit(t1, (W/2 - t1.get_width()/2, box.y + 16 + math.sin(self.t*3)*2))
            t2 = pixfont.render(f"SCORE {self.score()}   KILLS {self.kills}   TREASURES {self.treasures()}/13", (230, 220, 240)); surf.blit(t2, (W/2 - t2.get_width()/2, box.y + 52))
            if self.dead_t > 1: t3 = pixfont.render("PRESS ENTER TO PLAY AGAIN" if won else "PRESS ENTER TO TRY AGAIN", (110, 200, 90) if int(self.t*2) % 2 else (230, 200, 90)); surf.blit(t3, (W/2 - t3.get_width()/2, box.y + 80))
        if self.inv: surf.blit(pixfont.render(self.hud_inv(), (200, 190, 220)), (8, 30))

    def render_title(self, surf):
        u = self.ui
        wob = math.sin(self.t*2)*2
        t1 = pixfont.render("THE CASTLE", (236, 186, 82), 5, shadow=(60, 20, 40))
        u.blit(t1, (W/2 - t1.get_width()/2, 26 + wob))
        for i, (txt, col) in enumerate([("A FAN-MADE TRIBUTE TO CASTLE ADVENTURE", (226, 222, 236)),
                                        ("ORIGINAL 1984 FREEWARE GAME BY KEVIN BALES", (110, 200, 190))]):
            t = pixfont.render(txt, col); u.blit(t, (W/2 - t.get_width()/2, 74 + i*11))
        if not hasattr(self, "mode_cfgs"): self.mode_cfgs = [load_cfg(m) for m in MODES]
        cols = [(70, 150, 220), (220, 70, 80)]
        for i, mc in enumerate(self.mode_cfgs):       # Balatro-style picker cards
            sel = i == self.mode_sel
            cw, ch = 170, 150
            x = W/2 - 190 + i*210; y = 110 - (10 + math.sin(self.t*4)*3 if sel else 0)
            ang = (math.sin(self.t*2 + i)*2.5) if sel else (-3 if i == 0 else 3)
            card = pygame.Surface((cw, ch), pygame.SRCALPHA)
            pygame.draw.rect(card, (8, 6, 14), (0, 4, cw, ch-4), border_radius=10)
            pygame.draw.rect(card, (26, 22, 40), (0, 0, cw, ch-6), border_radius=10)
            pygame.draw.rect(card, cols[i] if sel else (80, 70, 100), (0, 0, cw, ch-6), 3, border_radius=10)
            hdr = pygame.Rect(10, 10, cw-20, 26); pygame.draw.rect(card, cols[i] if sel else (60, 54, 80), hdr, border_radius=6)
            lt = pixfont.render(mc["label"], (255, 255, 255), 2); card.blit(lt, (cw/2 - lt.get_width()/2, 16))
            for k, line in enumerate(mc["blurb"]):
                t = pixfont.render(line, (220, 214, 232)); card.blit(t, (cw/2 - t.get_width()/2, 46 + k*11))
            stats = [f"STRENGTH {mc['player']['start_strength']}", f"SWORD {int(mc['sword']['hit_chance']*100)}% {mc['sword']['dmg_min']}-{mc['sword']['dmg_max']}",
                     f"MONSTERS HIT {int(mc['monster_attack']['hit_chance']*100)}%",
                     "FLASK: " + ("FULL HEAL x1" if mc["flask"]["heal"] == "full" else f"+{mc['flask']['heal_amount']} REFILL")]
            for k, line in enumerate(stats):
                t = pixfont.render(line, (236, 186, 82) if sel else (150, 140, 160)); card.blit(t, (14, 80 + k*11))
            card = pygame.transform.rotate(card, ang)
            u.blit(card, (x + cw/2 - card.get_width()/2, y + ch/2 - card.get_height()/2))
        hint = pixfont.render("<  >  CHOOSE MODE     ENTER  START", (110, 200, 90) if int(self.t*2) % 2 else (230, 200, 90))
        u.blit(hint, (W/2 - hint.get_width()/2, 278))
        hero = pygame.transform.scale(self.heroes[(True, False)][int(self.t*2) % 2], (68, 68))
        surf.blit(hero, (W/2 - 34, 290))

class Presenter:
    """Composes the final frame in one opaque, display-format surface, then blits it once.
    Overlays are built after display init with convert_alpha(). Safe mode skips all effects."""
    def __init__(self, screen, crt_on):
        self.crt_on = crt_on
        self.resize(screen)
    def resize(self, screen):
        """frame = W*SCALE x H*SCALE, centred in the window (exact pixel size); small windows: scaled to fit"""
        self.screen = screen; ss = screen.get_size()
        fw, fh = W * SCALE, H * SCALE
        if fw > ss[0] or fh > ss[1]: fw, fh = ss                      # below BASE*SCALE: old behaviour, scale to the window
        self.size = (fw, fh); self.off = ((ss[0] - fw) // 2, (ss[1] - fh) // 2)
        self.frame = gfx.rgb(self.size)
        self.tmp = gfx.rgb((W, H))
        lines, vig = make_crt(self.size)
        self.lines, self.vig = lines.convert_alpha(), vig.convert_alpha()
        if (W, H) != (BASE_W, BASE_H):   # big frames: scanlines + vignette pre-composited into one overlay (one blit)
            self.lines.blit(self.vig, (0, 0)); self.vig = None
        if self.off != (0, 0): screen.fill((0, 0, 0))
    def present(self, game_surf, ui=None, target=None):
        if self.tmp.get_size() != game_surf.get_size(): self.resize(self.screen)
        f = self.frame
        if self.crt_on:
            curve(game_surf, self.tmp)
            # crisp bloom (art/tiles/NOTES.md): bright-pass, 1/2-res separable 5-tap blur x2, nearest up, add ~0.4, no black lift.
            # Bloom, grade and UI are composed at internal resolution and scaled once (same result as at screen size with
            # integer nearest scaling, a fraction of the fill cost at 2560x1440).
            k = 2 if W <= BASE_W else -(-W // 240)                                # big frames: bloom buffer capped at ~240 px wide
            self.n = getattr(self, "n", 0) + 1
            if k > 2 and self.n % 2 == 0 and getattr(self, "bloom_up", None) is not None and self.bloom_up.get_size() == (W, H):
                half = None                                                       # big frames: reuse last frame's bloom
            else:
                half = pygame.transform.scale(self.tmp, (W//k, H//k))
        if self.crt_on and half is not None:
            half.fill((190, 190, 190), special_flags=pygame.BLEND_RGB_SUB)        # luma > ~0.75 only
            for _ in range(2): half.blit(half, (0, 0), special_flags=pygame.BLEND_RGB_ADD)   # re-expand 65 -> ~255 range (x4)
            half = blur5(blur5(half, (1, 0)), (0, 1))
            if k == 2: half = blur5(blur5(half, (1, 0)), (0, 1))                   # one pass at k>2 gives a similar on-screen radius
            half.fill((102, 100, 108), special_flags=pygame.BLEND_RGB_MULT)        # ~0.4 strength, slightly cool
            self.bloom_up = pygame.transform.scale(half, (W, H)) if k > 2 else None
        if self.crt_on:
            if half is None: half = self.bloom_up
            if self.size == (W * SCALE, H * SCALE):
                c = self.tmp
                c.blit(half if half.get_size() == (W, H) else pygame.transform.scale(half, (W, H)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                c.fill((255, 240, 228), special_flags=pygame.BLEND_RGB_MULT)      # warm grade (blacks stay ink)
                if ui: c.blit(ui, (0, 0))                                         # unwarped UI
                pygame.transform.scale(c, self.size, f)
            else:
                pygame.transform.scale(self.tmp, self.size, f)
                f.blit(pygame.transform.scale(half, self.size), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                f.fill((255, 240, 228), special_flags=pygame.BLEND_RGB_MULT)
                if ui: f.blit(pygame.transform.scale(ui, self.size), (0, 0))
            f.blit(self.lines, (0, 0))
            if self.vig: f.blit(self.vig, (0, 0))
        else:
            pygame.transform.scale(game_surf, self.size, f)
            if ui: f.blit(pygame.transform.scale(ui, self.size), (0, 0))
        (target or self.screen).blit(f, self.off if target is None or target is self.screen else (0, 0))

def open_window(fullscreen=False, size=None):
    """F11 / settings: borderless fullscreen at the desktop resolution, else a resizable window.
    HiDPI/Retina (macOS): SDL reports the window in points and the OS scales it, so one art pixel stays
    ZOOM*SCALE points; the drawable is not rendered at physical resolution (documented in README)."""
    if fullscreen:
        try: dw, dh = pygame.display.get_desktop_sizes()[0]
        except Exception: dw, dh = 0, 0
        return pygame.display.set_mode((dw, dh), pygame.FULLSCREEN)   # (desktop size) = SDL desktop-fullscreen, no mode switch
    w, h = size or (BASE_W * SCALE, BASE_H * SCALE)
    want = (max(320, int(w)), max(180, int(h)))
    s = pygame.display.set_mode(want, pygame.RESIZABLE)
    if s.get_size() != want: s = pygame.display.set_mode(want, pygame.RESIZABLE)   # leaving fullscreen: SDL may keep the old size once
    return s

def self_test(g, pres, surf):
    """render known frames offscreen through the full pipeline; disable the warp if the world comes out black"""
    probe = gfx.rgb(pres.size); ok = True
    def centre_dark(img, rect=None):
        r = rect or pygame.Rect(0, 0, *img.get_size())
        pts = [(r.centerx + dx, r.centery + dy) for dx in (-20, 0, 20) for dy in (-20, 0, 20)]
        return max(sum(img.get_at(p)[:3]) for p in pts) < 40
    surf.fill((200, 120, 60)); pres.present(surf, None, probe)
    if centre_dark(probe): ok = False; print("[castle diag] WARNING: CRT pipeline produced a black frame")
    saved = (g.state, g.rid)
    g.state = "play"; g.render(surf); pres.present(surf, g.ui, probe)
    vr = pygame.Rect(VIEW.x*pres.size[0]//W, VIEW.y*pres.size[1]//H, VIEW.w*pres.size[0]//W, VIEW.h*pres.size[1]//H)   # probe is frame-sized
    if centre_dark(probe, vr): ok = False; print("[castle diag] WARNING: game world rendered black offscreen")
    g.state = saved[0]
    if not ok and pres.crt_on:
        pres.crt_on = False; print("[castle diag] CRT warp auto-disabled (press F1 to retry). Please report this line + the diag line.")
        surf.fill((200, 120, 60)); pres.present(surf, None, probe)
        print("[castle diag] self-test without CRT:", "ok" if not centre_dark(probe) else "STILL BLACK")
    else:
        print("[castle diag] self-test:", "ok" if ok else "failed")
    return ok

def post(game_surf, screen, pres, ui=None):
    pres.present(game_surf, ui)

def diag(screen):
    import platform
    try: npv = np.__version__
    except Exception: npv = "missing"
    info = dict(pygame=pygame.version.ver, ce=getattr(pygame, "IS_CE", False), sdl=".".join(map(str, pygame.get_sdl_version())),
                numpy=npv, png=pygame.image.get_extended(), driver=pygame.display.get_driver(), size=screen.get_size(), bits=screen.get_bitsize(),
                bytes=screen.get_bytesize(), masks=tuple(hex(m) for m in screen.get_masks()), flags=hex(screen.get_flags()),
                python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine())
    try: info["window"] = pygame.display.get_window_size()
    except Exception: pass
    print("[castle diag]", info); return info

def main():
    shots = "--shots" in sys.argv
    safe = os.environ.get("CASTLE_SAFE") == "1"
    crt_on = not ("--no-crt" in sys.argv or safe)
    pygame.init()
    scripted = shots
    settings = {} if scripted else load_settings()
    screen = open_window(settings.get("fullscreen", False), settings.get("window"))
    info = diag(screen)
    if not pygame.image.get_extended():
        print("[castle diag] WARNING: this pygame build cannot load PNG files - stairs/monster/hero art will use built-in fallbacks. Try: pip install -U pygame-ce")
    pygame.display.set_caption("A tribute to Castle Adventure by Kevin Bales")
    clock = pygame.time.Clock()
    set_frame(*screen.get_size())
    g = Game(); surf = gfx.rgb((W, H)); pres = Presenter(screen, crt_on)
    if "--no-selftest" not in sys.argv: self_test(g, pres, surf)
    script = []
    if shots:
        K = pygame.KEYDOWN
        def key(k, u=""): return pygame.event.Event(K, key=k, unicode=u)
        def typ(s): return [key(0, c) for c in s] + [key(pygame.K_RETURN)]
        script = [(1.0, [], "shots/01_title.png"), (0.2, [key(pygame.K_RETURN)], None),
                  (0.5, typ("look") + [key(pygame.K_LEFT)]*2, None), (0.8, [], "shots/02_courtyard.png"),
                  (0.2, typ("go n") + typ("go n") + typ("go w") + typ("go n"), None),
                  (0.6, [], "shots/03_dining_room.png"),
                  (0.0, ["walk"] + typ("get goblet"), None), (0.12, [], "shots/04_goblet_pickup.png"),
                  (0.8, typ("inv"), "shots/05_inventory.png")]
    timer = 0
    while True:
        dt = clock.tick(30)/1000 if not shots else 1/30
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
                pres.crt_on = not pres.crt_on; g.say("CRT effect " + ("ON" if pres.crt_on else "OFF") + " (F1)"); continue
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F2:
                pygame.image.save(screen, os.path.join(HERE, "shots", "readback.png")); g.say("Saved shots/readback.png"); continue
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11 and not scripted:   # borderless fullscreen at desktop res
                fs = not settings.get("fullscreen", False); settings["fullscreen"] = fs
                screen = open_window(fs, settings.get("window")); save_settings(settings)
                set_frame(*screen.get_size()); surf = gfx.rgb((W, H)); pres.resize(screen); continue
            if e.type in (getattr(pygame, "WINDOWSIZECHANGED", -1), pygame.VIDEORESIZE):
                screen = pygame.display.get_surface()
                if not settings.get("fullscreen") and not scripted:
                    settings["window"] = list(screen.get_size()); save_settings(settings)
                set_frame(*screen.get_size()); surf = gfx.rgb((W, H)); pres.resize(screen); continue
            g.event(e)
        if script:
            timer += dt
            if timer >= script[0][0]:
                wait, evs, shot = script.pop(0); timer = 0
                for e in evs:
                    if e == "walk":   # walk hero next to the goblet via real moves
                        it = g.room["items"][0]
                        for _ in range(40):
                            if g.near(it, 1): break
                            dx = (it["x"] > g.hx) - (it["x"] < g.hx); dy = (it["y"] > g.hy) - (it["y"] < g.hy)
                            ox, oy = g.hx, g.hy
                            if dy: g.try_move(0, dy)
                            if (g.hx, g.hy) == (ox, oy) and dx: g.try_move(dx, 0)
                    else: g.event(e)
                if shot:
                    g.update(0); g.render(surf); post(surf, screen, pres, getattr(g, 'ui', None))
                    pygame.image.save(screen, os.path.join(HERE, shot) if crt_on else os.path.join(HERE, shot).replace('.png', '_nocrt.png')); print("saved", shot, "room", g.rid, (g.hx, g.hy))
            if not script: return
        g.update(dt); g.render(surf); post(surf, screen, pres, getattr(g, 'ui', None))
        pygame.display.flip()

if __name__ == "__main__":
    main()
