import os, sys; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from spider import build_spider
build_spider("small_spider", HERE, .8, 32, 24, 22, "Same design at half scale (2 eyes visible), ~1 tile wide.")
print("ok")
