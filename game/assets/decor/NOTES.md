# Decor sprinkle: suggested algorithm (game-side)

Run this once per room when the room is baked, so the result is cached and stable.

1. `rnd = random.Random(rid * 104729)`. This is deterministic, so a room always looks the same.
2. **Theme:** `garden` if "GARDEN" is in `const`; `dungeon` if `art3.floor_kind(rid) == "cave"` (rooms 68–83); else `indoor`. Keep only props whose `themes` include that theme.
3. **Budget:** `n = rnd.choice([1, 2, 2, 3, 3, 4])`. Use 0–1 in tiny or puzzle-critical rooms, and never more than 4.
4. **Candidate cells per placement rule:**
   - **wall-face:** wall cells (`#`) whose cell below is walkable floor. The decal goes on that wall's front face.
   - **wall-top-corner:** floor cells with a wall above AND a wall to the left (use the sprite as is) or right (mirror it).
   - **wall-base:** walkable floor cells touching a wall on the N/E/W side.
   - **floor-open:** walkable cells with all 8 neighbours walkable.
   - **near-doorway:** floor within 2 cells of an exit gap, but never ON the path cells.
5. **Exclusions:** skip a cell if it is or touches any of:
   - doors, stairs (`U`/`D`), items, monster spawns, the fountain, or special glyphs (`$%@W[]G=`);
   - the room's exit gaps;
   - the main path: cells on a BFS shortest path between every pair of exits, and from each exit to each item.

   For **blocking** props, also skip any cell where placing it would disconnect `room["walk"]` (re-run the flood fill to check), and any cell on those paths.
6. **Choosing props:** weighted random pick using each prop's `weight`. Respect `max_per_room` and keep at least 3 cells between props of the same name. Pick the variant with `rnd.randrange(variants)`.
7. **Drawing:**
   - Floor and wall decals are drawn onto the baked room surface (floor decals after the floor, wall decals after the wall faces).
   - Objects go into the depth-sorted drawables at `y = cell_y*16 + 16`. Mark their cell non-walkable.
   - A lit sconce adds a warm point light at the sprite position + (7,4); animate it at 8 fps with a per-room phase offset.
8. **Subtlety:** for at most 2 decals per room, apply a random alpha of 70–100% and a random horizontal flip.
