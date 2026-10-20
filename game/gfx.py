"""Format-safe surfaces. Never use display-format convert() for offscreen/numpy work:
on some platforms (macOS/Metal, pygame-ce) the display is 32-bit ARGB, so convert() gives
surfaces with a per-pixel alpha channel that numpy writes / colour keys leave at 0 -> black world."""
import pygame
XRGB = (0x00FF0000, 0x0000FF00, 0x000000FF, 0)

import os
_FORCE = {"argb": (0xFF0000, 0xFF00, 0xFF, 0xFF000000), "bgra": (0xFF00, 0xFF0000, 0xFF000000, 0xFF),
          "rgba": (0xFF000000, 0xFF0000, 0xFF00, 0xFF), "xbgr": (0xFF, 0xFF00, 0xFF0000, 0)}.get(os.environ.get("CASTLE_TEST_FMT", ""))

def rgb(size):
    """opaque 32-bit XRGB surface with known masks (no alpha channel).
    CASTLE_TEST_FMT=argb|bgra|rgba|xbgr forces another layout (testing only)."""
    if _FORCE:
        return pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA if _FORCE[3] else 0, 32, _FORCE)
    return pygame.Surface((int(size[0]), int(size[1])), 0, 32, XRGB)

def to_rgb(src):
    s = rgb(src.get_size()); s.blit(src, (0, 0)); return s
