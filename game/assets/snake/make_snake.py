"""Snake idle/move strips (cleaner rings, bigger head). python3 make_snake.py"""
import os, sys, math; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from snakelib import *
import monlib
AX, AY = 32, 42
idle = [snake(neck_rise=1 + .04 * math.sin(i / 6 * math.tau), neck_bend=.25 * math.sin(i / 6 * math.tau), tongue=i in (2, 3)) for i in range(6)]
move = [snake(neck_rise=.95, neck_bend=.5 * math.sin(i / 4 * math.tau), coil_jit=.5, phase=i / 4 * math.tau, tongue=i % 2 == 0) for i in range(4)]
atk = [snake(neck_rise=.85, neck_bend=-.6), snake(neck_rise=.8, neck_bend=-1), snake(neck_rise=1.05, neck_bend=1.2), snake(neck_rise=1.0, neck_bend=1.0), snake(neck_rise=1, neck_bend=.2)]
monlib.build("snake", HERE, FW, FH, (AX, AY), {
    "idle": dict(frames=idle, dur=160, loop=True, note="neck sway + tongue flick on frames 2-3"),
    "move": dict(frames=move, dur=120, loop=True, note="coils ripple, neck undulates; translate in game"),
    "attack": dict(frames=atk, dur=[110, 120, 70, 120, 120], loop=False, note="coil back, strike on frame 2 = hit frame")},
    "Cleanup of art3.make_snake: clean ring bands (no noisy ink bands / flecks), bigger head with slit eye, pale jaw, nostril. Same 64x48 frame + anchor as snake_death (death strip regenerated with this drawer).")
print("ok")
