import os, sys; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../_common"))
from spider import build_spider
build_spider("big_spider", HERE, 1.6, 64, 40, 37, "Original: hairy violet-black tarantula with red cross mark & 4 red eyes, faces right. Big = ~2 tiles wide.")
print("ok")
