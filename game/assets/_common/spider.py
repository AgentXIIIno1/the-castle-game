import math, random
from monlib import *
BODY = [(20, 18, 26), (38, 32, 46), (58, 50, 66), (86, 76, 94)]
MARK = (170, 40, 40)
def spider(sc, FW, FH, AY, step=0, bob=0, atk=0, legs_up=0, belly=False):
    s = surf(FW, FH); cx = FW // 2 + round(atk * 3 * sc); by = AY + bob
    r = 8 * sc; cy = by - 6 * sc - (2 * sc if not belly else 0)
    for side in (-1, 1):                    # 4 legs per side, jointed
        for k in range(4):
            ph = math.sin(step * math.pi / 2 + k * 1.6 + (side > 0) * math.pi) * 2 * sc
            hip = (cx + side * (2 + k) * sc * .9, cy - 1 * sc + k * sc * .6)
            knee = (cx + side * (8 + k * 2.2) * sc, cy - (7 - k * 1.2) * sc - legs_up * 4 * sc + ph * .5)
            foot = (cx + side * (11 + k * 2.4) * sc + ph, by - (legs_up * 6 * sc if belly else 0) - (ph if side * ph > 0 else 0) * .3)
            if belly: knee, foot = (knee[0], cy - 9 * sc + k), (foot[0] - side * 4 * sc, cy - 12 * sc + k * 2)
            w = max(1, round(1.4 * sc))
            line(s, BODY[2], hip, knee, w); line(s, BODY[1], knee, foot, w); s.set_at((round(knee[0]), round(knee[1])), BODY[3])
    blob(s, cx - 4 * sc, cy, r * .95, r * .75, BODY)              # abdomen (back)
    m = round(cx - 4 * sc); n = round(cy - 2 * sc)
    for d in range(max(1, round(2 * sc))): s.set_at((m, n - d), MARK); s.set_at((m, n + d), MARK); s.set_at((m - d, n), MARK); s.set_at((m + d, n), MARK)
    blob(s, cx + 5 * sc, cy + 1 * sc, r * .55, r * .45, BODY)     # head/cephalothorax (front, facing right)
    ex, ey = round(cx + 7 * sc), round(cy)
    for e in range(2 if sc < 1 else 4):
        s.set_at((ex + e % 2 * 2 - (e // 2), ey - (e // 2)), (255, 70, 50) if not belly else BODY[3])
    fx = round(cx + 9 * sc + atk * 2 * sc)                           # fangs
    line(s, (230, 220, 200), (fx, round(cy + 2 * sc)), (fx + round(atk * sc), round(cy + 3 * sc + atk * 2 * sc)))
    return outline(s)
def build_spider(name, here, sc, FW, FH, AY, notes):
    rnd = random.Random(int(sc * 10))
    idle = [spider(sc, FW, FH, AY, step=0, bob=b) for b in (0, 0, -1, 0)]
    walk = [spider(sc, FW, FH, AY, step=i) for i in range(4)]
    atk = [spider(sc, FW, FH, AY, legs_up=.6, atk=-.5), spider(sc, FW, FH, AY, legs_up=1, atk=-1, bob=-1), spider(sc, FW, FH, AY, atk=1.5, legs_up=.3), spider(sc, FW, FH, AY, atk=1.2), spider(sc, FW, FH, AY, atk=0)]
    base = spider(sc, FW, FH, AY)
    dead = spider(sc, FW, FH, AY, belly=True, legs_up=1)
    death = [tint(base, flash(.9)), tint(spider(sc, FW, FH, AY, legs_up=1, bob=-2), flash(.4)), spider(sc, FW, FH, AY, legs_up=1, bob=-3, step=1), spider(sc, FW, FH, AY, legs_up=.5, bob=0, step=2), dead]
    death += death_tail(dead, rnd, FW // 2, AY - 2, big=sc)
    build(name, here, FW, FH, (FW // 2, AY), {
        "idle": dict(frames=idle, dur=200, loop=True), "walk": dict(frames=walk, dur=90, loop=True, note="8 legs alternate; skitter"),
        "attack": dict(frames=atk, dur=[90, 110, 70, 110, 110], loop=False, note="rear up, fang lunge on frame 2 = hit frame"),
        "death": dict(frames=death, dur=[90, 70, 80, 90, 180, 170, 90, 90, 100, 130], loop=False, note="flash, spasm, flips onto back legs curled, crumbles; remove after last frame")}, notes)
