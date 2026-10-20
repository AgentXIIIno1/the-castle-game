"""(Modern) backpack: floor pickup 16x16 + 12x12 small (art/items conventions) and hero overlay strips (back + front layers). python3 make_backpack.py"""
import os, sys, math, random, json; HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *; from roomprev import copy_to_game
from art import lerp
LE = [(46, 28, 18), (72, 46, 28), (100, 66, 40), (132, 92, 58), (164, 122, 80)]   # worn leather
ROLL = [(54, 58, 44), (78, 84, 62), (104, 110, 82)]                               # rolled bedroll (faded wool)
BUCK = [(120, 96, 50), (190, 160, 90)]; SH = (10, 8, 16)
def shade(s, r, pal, lit=.75):
    for y in range(r.top, r.bottom):
        for x in range(r.left, r.right):
            v = lit - (x - r.left) / max(1, r.width) * .3 - (y - r.top) / max(1, r.height) * .25 + (BAYER[y % 4][x % 4] / 16 - .5) * .22
            s.set_at((x, y), pal[max(0, min(len(pal) - 1, int(v * len(pal))))])
# ---------- floor item
def item_art(a):
    shade(a, pygame.Rect(3, 6, 10, 8), LE, .75)                                     # body
    pygame.draw.rect(a, LE[1], (12, 7, 2, 6)); line(a, LE[0], (13, 7), (13, 12))     # side pocket
    shade(a, pygame.Rect(3, 5, 10, 4), LE, .95); line(a, LE[4], (3, 5), (12, 5)); line(a, LE[0], (3, 9), (12, 9))   # flap
    for x in (5, 10): line(a, LE[0], (x, 8), (x, 12)); a.set_at((x, 10), BUCK[1]); a.set_at((x, 11), BUCK[0])       # straps + buckles
    shade(a, pygame.Rect(2, 2, 12, 3), ROLL, .8); line(a, ROLL[2], (3, 2), (12, 2)); a.set_at((2, 3), ROLL[0]); a.set_at((13, 3), ROLL[0])  # bedroll
    for x in (5, 10): a.set_at((x, 2), LE[1]); a.set_at((x, 3), LE[1]); a.set_at((x, 4), LE[1])                    # roll ties
    a.set_at((4, 12), LE[3]); a.set_at((8, 13), LE[0]); a.set_at((11, 7), LE[4])                                    # scuffs
def floor(fn):
    art_ = surf(16, 16); fn(art_); art_ = outline(art_)
    b = art_.get_bounding_rect(); s = surf(16, 16)
    for y in range(13, 16):
        for x in range(16):
            d = ((x - 8) / (b.width / 2 + 1)) ** 2 + ((y - 14.5) / 1.6) ** 2
            if d <= 1 and (d < .5 or BAYER[y % 4][x % 4] / 16 > (d - .5) * 2): s.set_at((x, y), (*SH, 110))
    s.blit(art_, (8 - (b.x + b.width // 2), 14 - b.bottom + 1)); return s
def small(fn):
    a = surf(16, 16); fn(a); b = a.get_bounding_rect(); a = a.subsurface(b).copy()
    k = 10 / max(b.width, b.height); a = pygame.transform.scale(a, (max(1, round(b.width * k)), max(1, round(b.height * k))))
    s = surf(12, 12); s.blit(a, (6 - a.get_width() // 2, 11 - a.get_height())); return outline(s)
FLOOR, SMALL = floor(item_art), small(item_art)
pygame.image.save(FLOOR, os.path.join(HERE, "backpack.png")); pygame.image.save(SMALL, os.path.join(HERE, "backpack_small.png"))
# ---------- hero overlays (hero frame 36x36, right native; body top bobs with the walk; see art/hero/make_hero.py)
FW, FH = 36, 36
BOBS = {"idle": [0, 0], "walk": [0, 1, 0, 1]}; DUR = {"idle": [400, 400], "walk": [140, 140, 140, 140]}
def back_layer(bob):
    """pack body + bedroll on the upper back, drawn BEHIND the hero body (and cloak). Visible: the bedroll between hair and cloak shoulder, and the pack's rear edge left of the cloak"""
    u = surf(FW, FH); o = bob
    shade(u, pygame.Rect(0, 15 + o, 7, 9), LE, .8); line(u, LE[4], (0, 15 + o), (6, 15 + o))       # pack body (rear edge shows at x0-3)
    line(u, LE[0], (0, 19 + o), (4, 19 + o)); u.set_at((1, 19 + o), BUCK[1]); u.set_at((1, 20 + o), BUCK[0])   # strap + buckle on the side
    line(u, LE[1], (0, 23 + o), (5, 23 + o))
    shade(u, pygame.Rect(0, 12 + o, 9, 4), ROLL, .9); line(u, ROLL[2], (1, 12 + o), (8, 12 + o)); line(u, ROLL[0], (0, 15 + o), (8, 15 + o))   # bedroll across the top
    pygame.draw.rect(u, ROLL[2], (0, 12 + o, 2, 4)); u.set_at((0, 13 + o), ROLL[1])                 # rolled end, lit
    for x in (3, 6): line(u, LE[1], (x, 12 + o), (x, 15 + o))                                       # roll ties
    u.set_at((2, 17 + o), LE[4]); u.set_at((4, 21 + o), LE[3])
    return outline(u)
def front_layer(bob):
    """shoulder straps over the jerkin, drawn IN FRONT of the body (below the necklace/sword/helmet)"""
    s = surf(FW, FH); o = bob; INK_ = (16, 10, 16)
    near = [(8, 14), (8, 15), (8, 16), (9, 17), (9, 18), (9, 19)]
    for (x, y) in near: s.set_at((x, y + o), LE[2]); s.set_at((x - 1, y + o), INK_); s.set_at((x + 1, y + o), LE[0])
    s.set_at((8, 14 + o), LE[4]); s.set_at((9, 18 + o), BUCK[1]); s.set_at((9, 19 + o), BUCK[0])   # lit top, buckle
    for (x, y) in ((16, 14), (16, 15), (16, 16), (15, 17), (15, 18)): s.set_at((x, y + o), LE[1]); s.set_at((x + 1, y + o), INK_)   # far strap, in shade
    s.set_at((16, 14 + o), LE[3])
    return s
def strip(frs):
    S = surf(FW * len(frs), FH)
    for i, f in enumerate(frs): S.blit(f, (i * FW, 0))
    return S
OUT_ = {}
for st, bobs in BOBS.items():
    for layer, fn in (("back", back_layer), ("front", front_layer)):
        R = strip([fn(b) for b in bobs]); Lf = strip([pygame.transform.flip(fn(b), True, False) for b in bobs])
        for side, S in (("right", R), ("left", Lf)):
            n = f"hero_backpack_{layer}_{st}_{side}.png"; pygame.image.save(S, os.path.join(HERE, n)); OUT_[n] = S
json.dump({"issue": 26, "mode": "Modern only",
  "item": {"floor": "backpack.png", "small": "backpack_small.png", "floor_frame": [16, 16], "floor_anchor": [8, 15], "shadow_baked": True, "small_frame": [12, 12], "small_anchor": [6, 11], "small_shadow_baked": False, "treasure": False},
  "hero_overlay": {"frame_size": [FW, FH], "anchor": {"px": [12, 33], "px_left": [24, 33]}, "same_as": "art/hero strips (right native, left = mirror)",
     "states": {st: {"frames": len(b), "frame_durations_ms": DUR[st], "files": {layer: [f"hero_backpack_{layer}_{st}_right.png", f"hero_backpack_{layer}_{st}_left.png"] for layer in ("back", "front")}} for st, b in BOBS.items()},
     "draw_order": "hero_backpack_back (pack body + bedroll)  ->  hero body/composited hero  ->  hero_backpack_front (straps)  ->  necklace  ->  sword  ->  helmet. With the pre-composited hero_{state}_swordX_helmetY strips: back BEHIND the composited strip, front ON TOP of it (the straps don't touch the sword hand or the helmet, so drawing them after is fine)",
     "frame_sync": "use the same frame index k as the hero strip (idle 2 frames / walk 4)"},
  "integration_notes": "main.with_overlays() only draws overlays on top. The backpack needs a 'behind' layer: blit hero_backpack_back_<state>_<side> before the hero frame and hero_backpack_front_<state>_<side> after it. If you'd rather keep the hero_overlays/<name>/ loader, copies are in game/assets/hero_overlays/backpack/ as back_<idle|walk>_<side>.png and <idle|walk>_<side>.png (front)"},
  open(os.path.join(HERE, "manifest.json"), "w"), indent=2)
# loader-friendly copies for main.overlay_strip ("<walk|idle>_<side>.png" = front) and the back layer
d = os.path.join(GAME, "assets", "hero_overlays", "backpack"); os.makedirs(d, exist_ok=True)
for st in BOBS:
    for side in ("right", "left"):
        OUT_[f"hero_backpack_front_{st}_{side}.png"] and pygame.image.save(OUT_[f"hero_backpack_front_{st}_{side}.png"], os.path.join(d, f"{st}_{side}.png"))
        pygame.image.save(OUT_[f"hero_backpack_back_{st}_{side}.png"], os.path.join(d, f"back_{st}_{side}.png"))
copy_to_game(HERE, "backpack"); print("ok")
