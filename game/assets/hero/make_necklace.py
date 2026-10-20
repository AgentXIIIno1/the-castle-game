"""necklace overlay for the hero (worn): gold chain on the jerkin collar + ruby pendant, follows the walk bob, optional glint. python3 make_necklace.py
Also writes the combined layering preview (body/backpack/necklace/sword/helmet)."""
import os, sys, math, json, shutil; HERE = os.path.dirname(os.path.abspath(__file__)); ART = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ART, "_common"))
from monlib import *
GOLD = [(110, 70, 24), (176, 124, 40), (226, 176, 72), (255, 232, 150)]; RUBY = [(93, 19, 31), (149, 28, 42), (196, 36, 52), (222, 132, 136)]   # Necklace item colours
FW, FH = 36, 36
BOBS = {"idle": [0, 0], "walk": [0, 1, 0, 1]}; DUR = {"idle": [400, 400], "walk": [140, 140, 140, 140]}
CHAIN = [(9, 15), (10, 16), (11, 17), (13, 17), (14, 16), (15, 15)]          # drapes from the collar corners (frame coords, bob 0)
def necklace(bob, glint=False):
    s = surf(FW, FH); o = bob
    for i, (x, y) in enumerate(CHAIN): s.set_at((x, y + o), GOLD[3] if i in (0, 1) else GOLD[2] if i % 2 else GOLD[1])
    s.set_at((8, 14 + o), GOLD[1]); s.set_at((16, 14 + o), GOLD[0])          # chain going round the neck (behind the collar)
    # pendant: gold bezel + ruby, 3x3 below the chain's low point
    for (x, y, c) in ((12, 17, GOLD[2]), (11, 18, GOLD[1]), (13, 18, GOLD[0]), (12, 18, RUBY[2]), (12, 19, RUBY[1]), (11, 19, GOLD[0]), (13, 19, GOLD[0]), (12, 20, GOLD[1])):
        s.set_at((x, y + o), c)
    s.set_at((12, 18 + o), RUBY[3] if glint else RUBY[2])
    if glint:                                                                   # tiny 4-point sparkle on the ruby, no bloom
        for (x, y, a) in ((12, 17, 255), (11, 18, 170), (13, 18, 170), (12, 16, 110)): s.set_at((x, y + o), (255, 250, 230, a))
    return s
def strip(frs):
    S = surf(FW * len(frs), FH)
    for i, f in enumerate(frs): S.blit(f, (i * FW, 0))
    return S
files = {}
for st, bobs in BOBS.items():
    frs = [necklace(b) for b in bobs]
    for side, S in (("right", strip(frs)), ("left", strip([pygame.transform.flip(f, True, False) for f in frs]))):
        n = f"hero_necklace_{st}_{side}.png"; pygame.image.save(S, os.path.join(HERE, n)); files[n] = S
GL = [necklace(0, glint=(i == 1)) for i in range(4)]                         # optional glint loop, same anchor (overlay only while idle or every ~2 s)
for side, S in (("right", strip(GL)), ("left", strip([pygame.transform.flip(f, True, False) for f in GL]))):
    pygame.image.save(S, os.path.join(HERE, f"hero_necklace_glint_{side}.png"))
man = json.load(open(os.path.join(HERE, "manifest.json")))
for st in BOBS:
    man["states"][f"necklace_{st}"] = {"files": [f"hero_necklace_{st}_right.png", f"hero_necklace_{st}_left.png"], "frames": len(BOBS[st]), "fps": round(1000 / DUR[st][0], 2), "frame_durations_ms": DUR[st], "loop": True,
        "frame_anchor_offsets": [[0, 0]] * len(BOBS[st]), "note": "overlay (#27, worn necklace): Necklace item gold + ruby on the jerkin collar, follows the body bob. Draw after body + backpack straps, before sword and helmet; frame index = the hero strip's"}
man["states"]["necklace_glint"] = {"files": ["hero_necklace_glint_right.png", "hero_necklace_glint_left.png"], "frames": 4, "frame_durations_ms": [1600, 90, 110, 200], "loop": True, "optional": True,
    "note": "optional idle replacement for necklace_idle (bob 0): frame 1 sparkles on the ruby, same timing as the statue necklace glint"}
man["layer_order"] = "backpack back (art/backpack) -> body (or a pre-composited hero_<state>_swordX_helmetY strip) -> backpack front straps -> necklace -> sword -> helmet. Over a pre-composited strip, drawing the straps and the necklace after it is fine: neither touches the sword hand or the helmet"
json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
# loader-friendly copies for main.overlay_strip(): assets/hero_overlays/necklace/<idle|walk>_<side>.png
d = os.path.join(GAME, "assets", "hero_overlays", "necklace"); os.makedirs(d, exist_ok=True)
for st in BOBS:
    for side in ("right", "left"): shutil.copy(os.path.join(HERE, f"hero_necklace_{st}_{side}.png"), os.path.join(d, f"{st}_{side}.png"))
# ---------- combined layering preview: every sword/helmet combo x backpack x necklace, walk frames, right + left
BP = os.path.join(ART, "backpack")
def L(n): return pygame.image.load(os.path.join(HERE, n))
def B(n): return pygame.image.load(os.path.join(BP, n))
rows = []
for st in ("idle", "walk"):
    n = len(BOBS[st])
    for side in ("right", "left"):
        for sw in (0, 1):
            for hm in (0, 1):
                for bp, nk in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    row = []
                    for k in range(n):
                        f = surf(FW, FH)
                        if bp: f.blit(B(f"hero_backpack_back_{st}_{side}.png"), (0, 0), (k * FW, 0, FW, FH))
                        f.blit(L(f"hero_{st}_sword{sw}_helmet{hm}_{side}.png"), (0, 0), (k * FW, 0, FW, FH))
                        if bp: f.blit(B(f"hero_backpack_front_{st}_{side}.png"), (0, 0), (k * FW, 0, FW, FH))
                        if nk: f.blit(L(f"hero_necklace_{st}_{side}.png"), (0, 0), (k * FW, 0, FW, FH))
                        row.append(f)
                    rows.append(((st, side, sw, hm, bp, nk), row))
# compact sheet: walk right/left, each column = one combo (frame 1 and 2)
combos = [r for r in rows if r[0][0] == "walk"]
Z = pygame.Surface((len(combos) // 2 * 38 + 4, 2 * 38 * 2 + 4)); Z.fill((96, 70, 52))
ci = {"right": 0, "left": 0}
for (st, side, sw, hm, bp, nk), row in combos:
    c = ci[side]; ci[side] += 1; yo = 2 if side == "right" else 2 + 76
    Z.blit(row[0], (2 + c * 38, yo)); Z.blit(row[1], (2 + c * 38, yo + 38))
pygame.image.save(pygame.transform.scale(Z, (Z.get_width() * 3, Z.get_height() * 3)), os.path.join(HERE, "preview_overlays.png"))
# animated gif: full kit, walk then idle with glint
from PIL import Image
fr = []
full = [r for r in rows if r[0][1] == "right" and r[0][2:] == (1, 1, 1, 1)]
for (key, row) in full:
    for f in row * (2 if key[0] == "walk" else 1):
        Zs = pygame.Surface((36, 36)); Zs.fill((96, 70, 52)); Zs.blit(f, (0, 0)); Zs = pygame.transform.scale(Zs, (216, 216))
        fr.append(Image.frombytes("RGB", Zs.get_size(), pygame.image.tobytes(Zs, "RGB")))
fr[0].save(os.path.join(HERE, "preview_overlays.gif"), save_all=True, append_images=fr[1:], duration=160, loop=0)
dst = os.path.join(GAME, "assets", "hero")
for f in os.listdir(HERE):
    if f.startswith("hero_necklace") or f in ("manifest.json", "make_necklace.py"): shutil.copy(os.path.join(HERE, f), dst)
print("ok", len(rows))
