"""Reproducible stairs tiles for Castle Adventure remake. Run: python make_stairs.py
1x art on the 16px grid, RGBA, no smoothing, no baked glow/shadow. Palette from art.py STONE / art3.py floor pals."""
import os, sys, json, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
HERE = os.path.dirname(os.path.abspath(__file__)); GAME = os.path.join(HERE, "../../game"); sys.path.insert(0, GAME)
import pygame
pygame.init(); pygame.display.set_mode((1, 1))
from art import STONE, BAYER
T = 16
INK = (16, 10, 16)
PAL = {  # (outline, step tops dark->light, riser dark->light, rim, mortar)
 "indoor": dict(ink=INK, top=[STONE["top2"], STONE["top"], (120, 114, 124), STONE["rim"]],
                riser=[(40, 37, 48), STONE["face2"], STONE["face"]], mortar=STONE["mortar"], void=(14, 12, 20), accent=STONE["moss"]),
 "dungeon": dict(ink=INK, top=[(34, 31, 34), (50, 45, 46), (60, 54, 52), (96, 90, 84)],
                riser=[(22, 20, 24), (34, 31, 34), (42, 38, 40)], mortar=(22, 20, 26), void=(8, 7, 10), accent=(70, 84, 66)),
}
def surf(w, h): s = pygame.Surface((w * T, h * T), pygame.SRCALPHA); s.fill((0, 0, 0, 0)); return s
def cheeks(s, p, W, H):  # stone side walls (3/4 view) + thick outline
    pygame.draw.rect(s, p["ink"], (0, 0, W, H), 1)
    for y in range(1, H - 1):
        s.set_at((1, y), p["top"][2] if y % 4 else p["mortar"]); s.set_at((2, y), p["riser"][2])
        s.set_at((W - 3, y), p["riser"][1]); s.set_at((W - 2, y), p["riser"][0] if y % 4 else p["mortar"])
def up(v, w=1, h=1):
    p = PAL[v]; W, H = w * T, h * T; s = surf(w, h); cheeks(s, p, W, H)
    n = 4 * h; step = (H - 3) // n; rnd = random.Random(7 + w * 3 + h)
    for k in range(n):          # k=0 is the top (highest, brightest) step
        y0 = 1 + k * step; t = k / max(1, n - 1)
        b = 3 - round(t * 3); tc = p["top"][max(1, b)] if b > 0 else p["top"][0]
        for x in range(3, W - 3):
            s.set_at((x, y0), p["top"][min(3, b + 1)] if b < 3 else p["top"][3])     # lit nosing / rim
            for yy in range(y0 + 1, y0 + step - 1): s.set_at((x, yy), tc)
            s.set_at((x, y0 + step - 1), p["riser"][max(0, 2 - round(t * 2))] if (x - 3) % 8 else p["mortar"])
        for _ in range(w): s.set_at((3 + rnd.randrange(W - 6), y0 + 1 + rnd.randrange(max(1, step - 2))), p["riser"][1])
        s.set_at((W - 4, y0), p["riser"][2])
    for x in range(3, W - 3): s.set_at((x, H - 2), p["ink"])
    s.set_at((4, H - 4), p["accent"]); s.set_at((W - 5, 1 + step + 1), p["accent"])
    return s
def down(v, w=1, h=1):
    p = PAL[v]; W, H = w * T, h * T; s = surf(w, h); cheeks(s, p, W, H)
    for x in range(1, W - 1): s.set_at((x, 1), p["top"][3]); s.set_at((x, 2), p["top"][2]); s.set_at((x, 3), p["ink"])
    n = 3 * h + 1; step = (H - 5) // n
    for k in range(n):          # steps drop away into the dark
        y0 = 4 + k * step; t = (k + 1) / n
        cols = [lerp(p["top"][2], p["void"], t), lerp(p["riser"][1], p["void"], t)]
        for x in range(3, W - 3):
            s.set_at((x, y0), lerp(p["top"][3], p["void"], t * 1.1 if t < .9 else 1))
            for yy in range(y0 + 1, min(H - 1, y0 + step)):
                c = cols[1] if yy == y0 + step - 1 else cols[0]
                if t > .5 and (BAYER[yy % 4][x % 4] / 16) < (t - .5) * 1.4: c = p["void"]
                s.set_at((x, yy), c)
    for y in range(4 + n * step, H - 1):
        for x in range(3, W - 3): s.set_at((x, y), p["void"])
    for y in range(3, H): s.set_at((3, y), p["ink"]); s.set_at((W - 4, y), p["ink"])
    for x in range(W): s.set_at((x, H - 1), p["ink"])
    return s
def lerp(a, b, t): t = max(0, min(1, t)); return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def up_pieces(v):  # 4-frame strip: faint dust glint drifting across the lit top step
    base = up(v); out = pygame.Surface((T * 4, T), pygame.SRCALPHA); out.fill((0, 0, 0, 0))
    for i in range(4): out.blit(base, (i * T, 0)); out.set_at((i * T + 5 + i * 2, 2), (210, 200, 180, 150 if i % 2 else 100))
    return out
def save(s, n): pygame.image.save(s, os.path.join(HERE, n)); return n
manifest = {"tile_px": T, "scale_note": "authored 1x, game scales 2x nearest", "palette_source": "art.py STONE (indoor), art3.py 'cave' floor pal (dungeon)", "sheets": []}
mapping = {"up": {"glyph": "U", "rooms": "room_05 (to 21), room_68 (to 11), room_82 (to 43), any 'U'"},
           "down": {"glyph": "D", "rooms": "room_21 (to 5) and any 'D'"}}
FOOT = {(1, 1): "rooms 04,05,11,15,16,20,21,30,31,68", (2, 1): "rooms 25,26,32,34,41,48,49,53 (and mixed 42,45: one tile each -> use 1x1)",
        (1, 2): "rooms 43,82 (vertical pair at east wall)", (2, 2): "rooms 07,23,50,61,64,65 (62,63 mixed: use 1x2 per column)"}
for d, fn in (("up", up), ("down", down)):
    for v in ("indoor", "dungeon"):
        for (w, h), rms in FOOT.items():
            img = fn(v, w, h); n = save(img, f"stairs_{d}_{v}_{w}x{h}.png")
            manifest["sheets"].append(dict(file=n, frame_size=[16 * w, 16 * h], frames=1, fps=0, footprint_tiles=[w, h],
                anchor="top-left = top-left cell of the glyph block (draw at col*16,row*16, 0-based)",
                glyph="U" if d == "up" else "D", rooms=rms, variant=v,
                tile_pieces="slice into 16x16 cells row-major if per-cell drawing is needed",
                use_variant_when="dungeon if art3.floor_kind(rid)=='cave' (68-83) or dark cellar; else indoor",
                orientation="3/4 view, steps run across (horizontal); UP rises toward top of screen, DOWN descends toward bottom",
                layering="floor layer: blit over baked floor in place of the striped U, beneath items/monsters/hero. Fully opaque RGBA; no drop shadow baked; no glow baked."))
    if d == "up":
        for v in ("indoor", "dungeon"):
            n = save(up_pieces(v), f"stairs_up_{v}_1x1_dust_strip.png")
            manifest["sheets"].append(dict(file=n, frame_size=[16, 16], frames=4, fps=4, frame_offsets=[[0, 0]] * 4, footprint_tiles=[1, 1],
                anchor="top-left of tile cell", glyph="U", variant=v, optional=True, layering="optional animated replacement for 1x1 up tile"))
json.dump(manifest, open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# ---- preview contact sheet
import art3
rooms = {r["id"]: r for r in json.load(open(os.path.join(GAME, "../map/rooms.json")))["rooms"]}
def lay(rid): return [l[1:25] for l in open(os.path.join(GAME, f"../map/rooms_layout/room_{rid:02d}.txt")).read().splitlines()[4:22]]
def comp(rid, d, v, frid=None):
    frid = frid or rid; g = lay(rid); fl = art3.bake_floor(frid, rooms[frid], False).convert_alpha()
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch == "#": pygame.draw.rect(fl, (70, 66, 78), (x*T, y*T, T, T)); pygame.draw.rect(fl, INK, (x*T, y*T, T, T), 1)
    pos = [(x, y) for y, r in enumerate(g) for x, c in enumerate(r) if c in "UD"]
    xs = [p[0] for p in pos]; ys = [p[1] for p in pos]; w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    img = pygame.image.load(os.path.join(HERE, f"stairs_{d}_{v}_{w}x{h}.png")).convert_alpha()
    cx, cy = min(xs), min(ys); fl.blit(img, (cx * T, cy * T))
    crop = fl.subsurface(pygame.Rect(min(max(0, cx*T-48), fl.get_width()-112), min(max(0, cy*T-48), fl.get_height()-112), 112, 112)).copy()
    return pygame.transform.scale(crop, (224, 224))
font = pygame.font.Font(None, 18)
P = pygame.Surface((4 * 250, 2 * 270 + 40)); P.fill((24, 20, 30))
items = [("up", "indoor", 5), ("up", "dungeon", 82), ("down", "indoor", 23), ("down", "dungeon", 21)]
for i, (d, v, rid) in enumerate(items):
    img = pygame.image.load(os.path.join(HERE, f"stairs_{d}_{v}_1x1.png")).convert_alpha()
    X = i * 250 + 10
    P.blit(font.render(f"{d} / {v}", True, (230, 220, 200)), (X, 8))
    P.blit(pygame.transform.scale(img, (32, 32)), (X, 30)); P.blit(pygame.transform.scale(img, (64, 64)), (X + 40, 30))
    P.blit(pygame.transform.scale(img, (128, 128)), (X + 110, 30))
    P.blit(font.render(f"mock: room {rid} (2x)" + (" on cave floor" if v=="dungeon" and rid==21 else ""), True, (200, 190, 170)), (X, 280))
    P.blit(comp(rid, d, v, 82 if (v == "dungeon" and d == "down") else None), (X, 300))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
print("ok")
