"""Shared helpers for monster strips (1x RGBA, nearest only, baked dark outline, no shadow/glow)."""
import os, sys, math, random, json
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../game"); sys.path.insert(0, GAME)
import pygame
pygame.init()
if not pygame.display.get_surface(): pygame.display.set_mode((1, 1))
import art, art3
BAYER = art.BAYER; INK = art3.INK; OUT = (14, 10, 20)
def surf(w, h): s = pygame.Surface((w, h), pygame.SRCALPHA); s.fill((0, 0, 0, 0)); return s
def blob(s, cx, cy, rx, ry, pal, light=(-.5, -.8)):
    """dithered shaded ellipse, lit from top-left (same formula as art3.make_ogre)"""
    W, H = s.get_size()
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if not (0 <= x < W and 0 <= y < H) or rx <= 0 or ry <= 0: continue
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                l = ((x - cx) / rx * light[0] + (y - cy) / ry * light[1]) * .5 + .55 - d * .2 + (BAYER[y % 4][x % 4] / 16 - .5) * .3
                s.set_at((x, y), pal[max(0, min(len(pal) - 1, int(l * len(pal))))])
def line(s, c, a, b, w=1): pygame.draw.line(s, c, (round(a[0]), round(a[1])), (round(b[0]), round(b[1])), w)
def outline(s):  # 1px dark outline inside same canvas
    m = pygame.mask.from_surface(s); o = surf(*s.get_size())
    ms = m.to_surface(setcolor=OUT, unsetcolor=(0, 0, 0, 0))
    for d in ((0, 1), (0, -1), (1, 0), (-1, 0)): o.blit(ms, d)
    o.blit(s, (0, 0)); return o
def tint(src, fn):
    s = src.copy()
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            c = s.get_at((x, y))
            if c.a and sum(c[:3]) > 130: s.set_at((x, y), (*fn(c[:3]), c.a))
    return s
def flash(t): return lambda c: tuple(int(v + (255 - v) * t) for v in c)
def gray(t): return lambda c: tuple(int(v + (sum(c) // 3 + 25 - v) * t) for v in c)
def crumble(src, t, rnd, up=False):
    W, H = src.get_size(); s = surf(W, H)
    for y in range(H):
        for x in range(W):
            c = src.get_at((x, y))
            if not c.a: continue
            thr = BAYER[y % 4][x % 4] / 16 * .7 + ((y / H) if up else (1 - y / H)) * .3
            if thr < t:
                if rnd.random() < .08 * (1 - t):
                    yy = y - 1 - int(t * 8 * rnd.random()) if up else y + 1 + int(t * 8 * rnd.random())
                    if 0 <= yy < H: s.set_at((x, yy), (128, 120, 104) if not up else (200, 190, 220))
                continue
            s.set_at((x, y), c)
    return s
def puff(s, t, gx, gy, big=1.0, col=((150, 140, 120), (110, 102, 92))):
    for i in range(16):
        a = i / 16 * math.tau; r = (4 + t * 14) * big
        x, y = gx + math.cos(a) * r, gy + math.sin(a) * r * .3 - t * 3
        rr = max(0, int((3 - t * 3 + (i % 2)) * min(1, big)))
        if rr: pygame.draw.circle(s, col[0] if i % 3 else col[1], (int(x), int(y)), rr)
def sparkles(s, t, rnd, gx, gy, n=6, spread=14, cols=((255, 240, 170), (190, 230, 140))):
    W, H = s.get_size()
    for i in range(n):
        a = rnd.random() * math.tau; r = 3 + t * spread * rnd.random()
        x, y = int(gx + math.cos(a) * r), int(gy - 4 - t * spread - rnd.random() * 8)
        if 1 <= x < W - 1 and 1 <= y < H - 1:
            s.set_at((x, y), cols[i % len(cols)])
            if i % 3 == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): s.set_at((x + dx, y + dy), (200, 170, 90))
def death_tail(pose, rnd, gx, gy, big=1.0, n=3):
    """standard ending frames from a final dead pose: grey, crumble x n with puff/sparkle, sparkles only"""
    out = [tint(pose, gray(.5))]; dead = tint(pose, gray(.8))
    for i in range(n):
        t = (i + 1) / (n + .3); f = crumble(dead, t, rnd); puff(f, (i + 2) / (n + 2), gx, gy, big); sparkles(f, (i + 1) / (n + 1), rnd, gx, gy); out.append(f)
    f = surf(*pose.get_size()); sparkles(f, 1.0, rnd, gx, gy); out.append(f)
    return out
def build(name, here, fw, fh, anchor, states, notes, bg=(56, 54, 62)):
    """states: dict state -> dict(frames=[surf], dur=[ms], loop=bool, note=str). Writes strips, manifest, preview.png, preview.gif"""
    from PIL import Image
    man = {"monster": name, "frame_size": [fw, fh], "anchor": {"px": list(anchor), "px_left": [fw - anchor[0], anchor[1]], "desc": "bottom-centre ground contact; px for *_right strips, px_left for *_left (mirrored) strips; draw frame at (x - ax, y - ay)"},
           "layout": "one horizontal strip per state per facing, 1x RGBA, nearest only, dark outline baked, no shadow/glow baked",
           "facing": "*_right.png is the native facing (game face>=0); *_left.png is the mirror (face<0) - or flip right at runtime as main.py does",
           "notes": notes, "states": {}}
    rows = []
    for st, d in states.items():
        fr = d["frames"]; S = surf(fw * len(fr), fh)
        for i, f in enumerate(fr): S.blit(f, (i * fw, 0))
        L = surf(fw * len(fr), fh)
        for i, f in enumerate(fr): L.blit(pygame.transform.flip(f, True, False), (i * fw, 0))
        pygame.image.save(S, os.path.join(here, f"{name}_{st}_right.png")); pygame.image.save(L, os.path.join(here, f"{name}_{st}_left.png"))
        dur = d["dur"] if isinstance(d["dur"], list) else [d["dur"]] * len(fr)
        man["states"][st] = {"files": [f"{name}_{st}_right.png", f"{name}_{st}_left.png"], "frames": len(fr), "fps": round(1000 * len(fr) / sum(dur), 1),
                             "frame_durations_ms": dur, "loop": d["loop"], "frame_anchor_offsets": d.get("offsets", [[0, 0]] * len(fr)), "note": d.get("note", "")}
        rows.append((st, fr, dur))
    json.dump(man, open(os.path.join(here, "manifest.json"), "w"), indent=2)
    Z = 4; mx = max(len(r[1]) for r in rows); font = pygame.font.Font(None, 20)
    P = pygame.Surface((90 + mx * (fw * Z + 6), len(rows) * (fh * Z + 8) + 8)); P.fill((40, 36, 48))
    for j, (st, fr, _) in enumerate(rows):
        y = 8 + j * (fh * Z + 8); P.blit(font.render(st, True, (230, 220, 200)), (8, y + 4))
        for i, f in enumerate(fr):
            b = pygame.Surface((fw, fh)); b.fill(bg); b.blit(f, (0, 0)); P.blit(pygame.transform.scale(b, (fw * Z, fh * Z)), (90 + i * (fw * Z + 6), y))
    pygame.image.save(P, os.path.join(here, "preview.png"))
    imgs, ds = [], []
    for st, fr, dur in rows:
        reps = 3 if st in ("idle", "walk", "fly") else 1
        for _ in range(reps):
            for f, du in zip(fr, dur):
                b = pygame.Surface((fw, fh)); b.fill(bg); b.blit(f, (0, 0))
                imgs.append(Image.frombytes("RGB", (fw, fh), pygame.image.tobytes(b, "RGB")).resize((fw * Z, fh * Z), Image.NEAREST)); ds.append(du)
        ds[-1] += 300
    imgs[0].save(os.path.join(here, "preview.gif"), save_all=True, append_images=imgs[1:], duration=ds, loop=0)
