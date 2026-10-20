"""Magic smoke puff (#31, room 67: WAVE WAND on the mirror, and the arrival back from room 66). python3 make_smoke.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from monlib import *; from roomprev import *
from art import lerp
SM = [(58, 50, 74), (92, 84, 110), (128, 120, 146), (166, 160, 182), (206, 202, 218)]   # dusty violet-grey
OL = (34, 26, 46); TIP = [(255, 240, 170), (255, 250, 220)]; LIL = (200, 170, 240)       # wand-tip gold echo + lilac motes
def frame(W, H, cx, cy, sc, t, seed, nb):
    """t in [0,1]: 0-.2 burst out from the core, then rise and thin out. Billows = union of circles, chunky outline, top-left lit, Bayer-eroded as it dissipates"""
    r = random.Random(seed); s = surf(W, H)
    burst = min(1, t / .22); rise = max(0, t - .15)
    bl = []
    for i in range(nb):
        a = r.uniform(0, 6.283); d = r.uniform(.25, 1) * sc * 9; r0 = r.uniform(.55, 1) * sc * 6.5
        ox, oy = math.cos(a) * d * (.35 + .65 * burst) * .95, math.sin(a) * d * (.35 + .65 * burst) * 1.35
        up = rise * sc * r.uniform(20, 28) * (1.3 if oy < 0 else .8)
        rr = r0 * (.45 + .7 * burst + .25 * rise) * (1 - .6 * max(0, t - .55) / .45)
        bl.append((cx + ox + r.uniform(-1, 1) * rise * 6, cy + oy - up, rr))
    erode = max(0, (t - .4) / .6) ** 1.1                                   # 0 = solid, 1 = gone
    m = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            best = None
            for (bx, by, rr) in bl:
                if rr <= .6: continue
                d = math.hypot(x - bx, y - by) / rr
                if d <= 1 and (best is None or by > best[1]): best = (bx, by, rr, d)      # lower billows sit in front
            if best is None: continue
            band = best[3] - (1 - erode * .8)                              # crumble from the outside in; cores stay solid longer
            if band > 0 and BAYER[y % 4][x % 4] / 16 < band * 4: continue
            if erode > .7 and BAYER[(y + 1) % 4][(x + 2) % 4] / 16 < (erode - .7) * 2.6: continue
            m[y][x] = best
    for y in range(H):
        for x in range(W):
            b = m[y][x]
            if not b: continue
            bx, by, rr, d = b
            l = .78 - (x - bx) / rr * .28 - (y - by) / rr * .34 - d * .18 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            c = SM[max(0, min(4, int(l * 5)))]
            edge = any(not (0 <= x + dx < W and 0 <= y + dy < H) or not m[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            inner = not edge and any(m[y + dy][x + dx] and m[y + dy][x + dx][:2] != (bx, by) and m[y + dy][x + dx][1] < by for dx, dy in ((0, -1), (-1, 0), (1, 0)) if 0 <= x + dx < W and 0 <= y + dy < H)
            if edge: c = OL if erode < .5 else SM[0]                               # chunky outline, softens as it thins
            elif inner: c = SM[1]                                                  # seam where a front billow overlaps one behind
            if t < .35 and not edge and d < .5 and l > .62: c = lerp(c, TIP[0], .35 * (1 - t / .35))   # wand-tip colour echo in the core
            a = int(245 * (1 - .55 * erode))
            s.set_at((x, y), (*c, a))
    if t < .12:                                                                  # the "puff" pop: small gold star at the core, no glow
        k = int(sc * (3 + t * 30))
        for i in range(-k, k + 1):
            for (px, py) in ((cx + i, cy), (cx, cy + i)):
                if 0 <= px < W and 0 <= py < H: s.set_at((int(px), int(py)), (*(TIP[1] if abs(i) < 2 else TIP[0]), 255 - abs(i) * 20))
    for i in range(int(4 + sc * 3)):                                             # arcane motes: drift up and out, twinkle as 4-point stars
        a = r.uniform(0, 6.283); d = sc * r.uniform(8, 20) * (.4 + burst * .6 + rise * .4)
        x = int(cx + math.cos(a) * d); y = int(cy + math.sin(a) * d * .9 - rise * sc * r.uniform(26, 40))
        on = (int(t * 20) + i) % 3 != 0 and t < .92 - r.random() * .15
        if not on or not (1 <= x < W - 1 and 1 <= y < H - 1): continue
        c = TIP[0] if i % 3 == 0 else LIL
        s.set_at((x, y), (*TIP[1], 255))
        if (int(t * 20) + i) % 2: [s.set_at((x + dx, y + dy), (*c, 200)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    return s
def strip(W, H, cx, cy, sc, N, seed, nb):
    fr = [frame(W, H, cx, cy, sc, i / (N - 1) * .97, seed, nb) for i in range(N)]
    S = surf(W * N, H)
    for i, f in enumerate(fr): S.blit(f, (i * W, 0))
    return S, fr
DUR = [60, 80, 110, 140, 160, 170, 180, 200]                                   # 1100 ms
BIG, BF = strip(48, 72, 24, 46, 1.3, 8, 31, 14); pygame.image.save(BIG, os.path.join(HERE, "smoke_puff.png"))
DS = [60, 90, 120, 140, 160, 180]                                              # 750 ms
SMALL, SF = strip(32, 40, 16, 28, .8, 6, 66, 8); pygame.image.save(SMALL, os.path.join(HERE, "smoke_puff_small.png"))
json.dump({"issue": 31, "room": 67,
  "smoke_puff.png": {"frame_size": [48, 72], "frames": 8, "frame_durations_ms": DUR, "total_ms": sum(DUR), "fps_equivalent": round(8000 / sum(DUR), 2), "loop": False, "play": "once, then remove",
     "anchor": {"px": [24, 71], "desc": "bottom-centre. The burst core sits at frame (24,46), 25 px above the anchor: for puff(X, Y) put the anchor at room px (X, Y + 25). Mirror (open_mirror): X = 296, Y = 144, so the anchor goes at (296, 169)"},
     "use": "WAVE WAND on the mirror; keep the mirror sprite fading out underneath over ~0.45 s as now"},
  "smoke_puff_small.png": {"frame_size": [32, 40], "frames": 6, "frame_durations_ms": DS, "total_ms": sum(DS), "loop": False, "play": "once",
     "anchor": {"px": [16, 39], "desc": "bottom-centre = the hero's feet: (hx*16 + 8, (hy+1)*16), i.e. the core sits at (hx*16+8, hy*16+4), the current puff() centre"},
     "use": "arrival back from room 66 at MIRROR_ARRIVE; or use the big puff here too if you prefer one effect"},
  "layering": "draw after the sprite pass (above the hero and the mirror), before the additive light pass and the darkness overlay. That is the same spot as the current procedural puff. Real alpha (normal blend), no additive blend needed",
  "style": "chunky outlined violet-grey billows, gold core echoing the wand tip, lilac/gold arcane motes; burst, then rise, then Bayer-eroded dissipation; no baked glow",
  "optional": "screen shake 0.3 as now; a brief small warm light at the core for frames 0-1 if you like (colour [255,240,170], radius ~24)"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# previews: frame strips on dark + room 67 floor; gif; mock on the real shot (zoom 2)
from PIL import Image
b, TOP = baked(67)
mirror = pygame.image.load(os.path.join(GAME, "assets", "wall_mirror", "wall_mirror.png"))
def scene(i_big, i_small, u):
    f = b.copy(); m = mirror.copy(); m.set_alpha(int(255 * max(0, 1 - u / .45))); f.blit(m, (296 - 8, 192 - 108 + TOP))
    hero = pygame.image.load(os.path.join(GAME, "assets", "hero", os.listdir(os.path.join(GAME, "assets", "hero"))[0])) if False else None
    if i_big is not None: f.blit(BF[i_big], (296 - 24, 169 - 72 + TOP))
    if i_small is not None: f.blit(SF[i_small], (16 * 16 + 8 - 16, 10 * 16 - 40 + TOP))
    return f.subsurface((200, 40, 150, 180))
P = pygame.Surface((8 * 48 * 3 + 20, 72 * 3 + 40 * 3 + 30)); P.fill((96, 70, 52))
for i, f in enumerate(BF): P.blit(pygame.transform.scale(f, (144, 216)), (10 + i * 144, 10))
for i, f in enumerate(SF): P.blit(pygame.transform.scale(f, (96, 120)), (10 + i * 144, 236))
pygame.image.save(P, os.path.join(HERE, "preview.png"))
frames = []; t = 0; timeline = []
for i, d in enumerate(DUR): timeline.append((i, min(len(SF) - 1, i), t / 1000, d)); t += d
timeline.append((None, None, 1.2, 600))
for ib, is_, u, d in timeline:
    Z = pygame.transform.scale(scene(ib, is_, u), (450, 540)); frames.append((Image.frombytes("RGB", Z.get_size(), pygame.image.tobytes(Z, "RGB")), d))
frames[0][0].save(os.path.join(HERE, "preview.gif"), save_all=True, append_images=[f for f, _ in frames[1:]], duration=[d for _, d in frames], loop=0)
shot = pygame.image.load(os.path.join(GAME, "shots", "i31", "room67_before_wave_full.png")).convert() if pygame.display.get_init() and pygame.display.get_surface() else pygame.image.load(os.path.join(GAME, "shots", "i31", "room67_before_wave_full.png"))
OX, OY = 256, 17 - 2 * TOP + 2 * TOP                                          # room px -> shot px at zoom 2 (measured on the mirror)
M = pygame.Surface((shot.get_width() * 2 // 2 * 3 // 3, shot.get_height())); M.blit(shot, (0, 0))
for k, i in enumerate((1, 3, 5)):
    pass
mk = shot.copy(); mk.blit(pygame.transform.scale(BF[3], (96, 144)), (OX + (296 - 24) * 2, OY + (169 - 72) * 2))
mk.blit(pygame.transform.scale(SF[2], (64, 80)), (OX + (16 * 16 + 8 - 16) * 2, OY + (10 * 16 - 40) * 2))
pygame.image.save(mk, os.path.join(HERE, "preview_mock_room67.png")); copy_to_game(HERE, "smoke")
def touches(F):
    W, H = F.get_size(); return [k for k, ok in (("L", any(F.get_at((0, y)).a > 100 for y in range(H))), ("R", any(F.get_at((W - 1, y)).a > 100 for y in range(H))), ("T", any(F.get_at((x, 0)).a > 100 for x in range(W)))) if ok]
print("ok", sum(DUR), sum(DS), [touches(f) for f in BF], [touches(f) for f in SF])
