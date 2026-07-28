# THE MODDING PLAYBOOK - Soulvizier Classic (Titan Quest Anniversary Edition)

> For CONTENT (items, souls, pets, quests, quest rewards, loot drops, text/tags):
> see the companion **`docs/CONTENT_PLAYBOOK.md`**. This file is the WORLD layer
> (levels, navmesh, connections, entities); that one is the DB/records layer.

> How the TQAE game world actually works, and exactly what to do to add new caves,
> walkable areas, portals, teleports, quests, records, and entities into this mod.
> Written for a future session (or Will) starting from the repo with ZERO project
> memory. Every claim is byte-level, disassembly-verified, or points at a runnable
> tool. Cited `path:line` references are to files in this repo unless noted.
>
> Companion docs: `CLAUDE.md` (status board + map-bug history),
> `docs/blood_cave_walkin_entrance_plan.md` (the worked cave-mouth example),
> `tools/MAP_MERGE_EXPERIMENTS.md` (failure history), `docs/crash_analysis_report.md`
> (32-bit crash analysis). Where an older doc section conflicts with THIS playbook,
> this playbook wins (it encodes the 2026-07 disassembly + byte-level findings). A
> few stale sections in `CLAUDE.md` still describe the abandoned "Editor bake" plan
> as the path forward - that plan is dead; the offline pipeline (Section 3) shipped.

---

## 0. Orientation and conventions

- Python: use the `py` launcher (never `python`/`python3`). Set `PYTHONIOENCODING=utf-8`.
- Repo root: `C:/Users/willi/repos/tqit_soulvizier_classic`. Git remote `origin` =
  `github.com/wtrevena/tqit_soulvizier_classic`, branch `main`.
- The mod is a TQAE Custom Quest total conversion. It loads via TQAE main menu ->
  Play Custom Quest -> `SoulvizierClassic`. ALWAYS create a dedicated Custom Quest
  character to test; never load a mainline character into it (it corrupts them).
- Coordinate math constants used everywhere below (verified in `tools/gen_rec02.py:23`
  and the navmesh spec `tools/rec02_format.py`):
  - `SCALE = 2` world units per grid tile (map/LEVELS grid).
  - Navmesh cell `cs = ch = 0.2` world units.
  - Navmesh tile = 64x64 cells = `64 * 0.2 = 12.8` world units square.
  - A level's navmesh origin (local frame) = `center - dims`. Its walkable floor
    is found at `center - dims` corrected for the +16 padding on X/Z (see Section 11).

---

## 1. How the game world works (the mental model)

### 1.1 One world file, many streamed levels

The entire playable world is `world/world01.map`, stored inside
`Resources/Levels.arc` (a TQ `.arc` archive). The map is a flat container of typed
sections. Section codes (from `tools/merge_levels_binary.py:16-22` and confirmed by
disassembly):

| Section | Code   | What it holds |
|---------|--------|---------------|
| QUESTS  | `0x1b` | list of quest names registered in this world |
| GROUPS  | `0x11` | entity/spawn group records (REQUIRED to load; see graveyard) |
| SD      | `0x18` | scene/zone definitions (REQUIRED to load) |
| LEVELS  | `0x01` | the level index: one entry per level -> a `.lvl` blob in DATA |
| BITMAPS | `0x19` | minimap TGA index (cosmetic only) |
| (unk)   | `0x10` | passed through verbatim by the merge |
| DATA2   | `0x1a` | minimap TGA data + a level-count header (cosmetic; NOT pathfinding) |
| DATA    | `0x02` | the concatenated `.lvl` level blobs, referenced by absolute offset |

Parse a map with `tools/merge_levels_binary.py:parse_sections()` (line 25) and the
level index with `parse_level_index()` (line 38). `DATA2`/`BITMAPS` are minimap art
only - do NOT look there for walkability (a long-standing early misconception; see
`CLAUDE.md` "Key technical lessons" and `tools/MAP_MERGE_EXPERIMENTS.md`).

### 1.2 The LEVELS index entry (ints_raw)

Each LEVELS entry begins with a fixed 52-byte header called `ints_raw` = 13 x int32
(`tools/merge_levels_binary.py:45`), then a length-prefixed DBR string, a
length-prefixed filename, and the blob's `data_offset` + `data_length` into DATA.

`ints_raw` layout (13 x int32), verified in `tools/merge_levels_binary.py` and
`tools/build_section_surgery.py:transplant_rec02` (line 266) and `CLAUDE.md`:

| int index | byte offset | meaning |
|-----------|-------------|---------|
| `[0..5]`  | 0..23       | tile dimensions (per-axis half-extents in tiles; MapCompiler zeroes these) |
| `[6,7,8]` | 24..35      | grid corner world x, y, z |
| `[9..12]` | 36..51      | the level's 16-byte GUID |

So `ints_raw[36:52]` is the level GUID (used everywhere for cross-references), and
`struct.unpack_from('<iii', ints_raw, 24)` reads the grid corner. A level occupies
the world-grid footprint from its corner to `corner + tile_dims * SCALE` (SCALE=2).
`shifted_ints_raw()` in `tools/svaera_plus_portals.py:93` relocates a level cluster
by rewriting the grid corner at offset 24.

### 1.3 The level blob (.lvl) - internal sections

Each level blob starts with a 4-byte magic `LVL\x??` where the last byte is the
format generation, then typed internal sections `{uint32 type, uint32 size, bytes}`.
Parse with `tools/build_section_surgery.py:parse_blob_sections()` (line 28); rebuild
with `rebuild_blob()` (line 45).

Two blob format generations coexist in the merged world (see
`tools/MAP_MERGE_EXPERIMENTS.md` and `tools/build_section_surgery.py:239-242`):

- v0x0e (`LVL\x0e`, magic `0x0e4c564c`): 56-byte entity records in `0x05`, has a
  `0x09` grid section, NO `0x14` metadata section. All original Soulvizier (SV) levels.
- v0x11 (`LVL\x11`, magic `0x114c564c`): 72-byte entity records in `0x05` (the 56
  bytes + 16 zero bytes), NO `0x09`, has a `0x14` metadata section. Almost all SVAERA
  (the modern AE port) levels.
- A third generation v0x0f exists in raw MapCompiler output but is NOT used by the
  live pipeline; do not introduce it.

CRITICAL: never drop a raw v0x0e blob into a slot the engine treats as v0x11 (or
vice versa) without the repo's conversion machinery
(`convert_v0e_blob_to_v11()` in `tools/build_section_surgery.py:564`). Doing so
historically crashed the game on world streaming (git `f4fb176`). The magic byte and
the record stride must agree.

Internal `.lvl` section codes (byte-verified this project):

| Code   | Contents | Notes |
|--------|----------|-------|
| `0x05` | entities: string table of DBR paths + per-instance records (record ref + 3x3 rotation + local x/y/z + flags) | `parse_0x05_strings()` line 54; record layout in `inject_into_0x05()` line 146 |
| `0x06` | terrain | embeds cross-level LINK GUIDs (incl. cave return-links) + portal UniqueId trailers |
| `0x09` | grid (v0x0e only) | legacy in-blob grid; absent in v0x11 |
| `0x0a` | LEGACY navmesh (TQIT PathEngine "tok" mesh) | STOCK TQAE ENGINE CANNOT PARSE IT - silently skipped. Source of the invisible-wall bug. |
| `0x0b` | MODERN navmesh (Recast/RLTD, `REC\x02` container) | THE ONLY navmesh the engine loads. See Section 3. |
| `0x14` | per-entity metadata records (v0x11) | cave-mouth GUID bindings live here (Section 2b) |
| `0x17` | misc | |

### 1.4 How levels connect at runtime (streaming + regions)

The engine streams levels as world-grid tiles. When you walk near a level's
footprint, it loads that `.lvl` blob and stitches it in. There is no monolithic
walkable surface; each level carries its own navmesh, and the engine hands the player
off between adjacent levels. Two levels become traversable to each other only through
one of the three deliberate mechanisms in Section 2. Destination resolution across
levels is done PURELY by 16-byte GUID (the `ints_raw[36:52]` GUID), never by
filename and never by world-XZ occupancy. This is why GUID hygiene is the single most
important discipline in this codebase.

---

## 2. The three ways areas connect (choose deliberately)

There are exactly three mechanisms. Pick by the experience you want.

### Decision table

| You want... | Use | Load screen? | Entities needed | Fragility |
|-------------|-----|--------------|-----------------|-----------|
| Seamless walking between two adjacent areas | (a) Grid-seam walk | No | None | Low - just navmesh alignment |
| Surface -> underground (cave/dungeon entry) | (b) Cave mouth / portal bridge | No (walk-in) | A `GridEntrance` art record + a `0x14` GUID binding | Medium - placement rules matter |
| Scripted warp (shrine, event, boss arena) | (c) Quest teleport | Depends | An NPC/proxy + a `.qst` action | HIGH - state bakes into saves |

Golden rule learned twice: for ENTRANCES prefer (a) or (b), engine-native mechanisms.
Reserve (c) for quest LOGIC, not for getting the player from A to B. Quest-driven
entrances broke twice in this project (Section 10).

### 2a. GRID-SEAM WALK (seamless walking)

Two levels whose footprints share a tile EDGE stream together, and the player walks
across the seam IF both sides' `0x0b` walkable cells reach the shared edge in an
aligned band. Requirements:

1. The two levels' grid footprints must ABUT (share an edge) or slightly overlap.
   Footprint = `corner .. corner + tile_dims * 2`. Compute abutment/overlap from
   `ints_raw` corner + dims.
2. Both `0x0b` navmeshes must have walkable cells (area id != 0) reaching the shared
   edge, and those walkable bands must OVERLAP across the seam (aim for >= 4 world
   units of aligned width; the shipped blood-cave seam overlaps ~31 units, see
   `CLAUDE.md` 2026-07-04 note).

This is how the blood-cave chain connects internally (no entities at all):
`Random09A -> xPassageTransitionStart -> BC_initialpathway -> drxFirstxistion_connection
-> drxFirstRoom -> cave` (grid-edge chain, byte-proven from the `0x0a` edge records;
see `docs/blood_cave_walkin_entrance_plan.md:29-31`).

Recipe in Section 5.

### 2b. CAVE MOUTH / PORTAL BRIDGE (surface <-> underground)

This is the mechanism for a cave entrance that the player walks into with NO load
screen. TQAE has NO surface->cave "portal entity". The visible cave mouth is a
`GridEntrance`-class DBR = PURE ART with ZERO destination fields (all 153 base-game
`GridEntrance` records carry only `mesh`/`scale`/render flags;
`docs/blood_cave_walkin_entrance_plan.md:14-18`).

The actual link is data in the SURFACE level:
- The `GridEntrance` art entity is placed in the surface level's `0x05` at a local
  position (the visible mouth on the terrain).
- The surface level's `0x14` metadata record ADJACENT to that entity carries the
  binding. Byte offsets within that `0x14` payload (session-verified via
  `Engine.dll` disassembly + the Silk Road cave record):
  - `@12` = the mouth's Portal `UniqueId`
  - `@28` = the reciprocal exit Portal `UniqueId`
  - `@44` = the DESTINATION level's 16-byte RegionId GUID
  (`docs/blood_cave_walkin_entrance_plan.md:22-24` documents the Silk Road case: the
  `GridEntrance` at local (14,18,26) is instance #30, and `0x14` record #30's 60-byte
  payload holds Random09A's GUID at payload offset 44.)

The engine resolves the destination purely by that GUID. Relevant `Engine.dll`
routines (VAs, for cross-referencing during future RE):
- `GridEntrance::Read` VA `0x10195240`
- `Region::FindCrossedPortal` VA `0x1020c110` (ray-tests the movement segment vs the
  portal plane, gated by `IsOpen` at `portal+0xfc`)
- `Portal::GetFrontToBackCoords` VA `0x102068b0` (maps by `inverse(surfaceXform) x destXform`)
- `Portal::GetConnectedRegion` VA `0x102063e0`

The DESTINATION level's `0x06` section must carry the reciprocal portal UniqueIds AND
the SOURCE level's GUID (the return link), so the walk-out resolves. In the shipped
mod, SV-Random09A's `0x06` embeds HiddenValley01's GUID (kept intact by the blob swap;
only `0x0a` was stripped).

THE HARD PLACEMENT RULE (this is the lesson that cost the most time): a cave interior
MUST be XZ-AREA-DISJOINT from all surface/live regions. Every working base-game cave
interior parks ~1700 units away with ZERO overlap. Edge-TOUCH is fine; AREA-OVERLAP is
not. An interior that area-overlaps its surface region breaks the mouth transition
(invisible wall at the threshold). Overlap at a DIFFERENT Y is tolerated by the engine
(it streams by GUID/grid-edge, not world-XZ occupancy: the pristine SVAERA map has 117
XZ-overlapping level pairs, 12 at |dy|>40; `docs/blood_cave_walkin_entrance_plan.md:110-117`),
but do not rely on that as a crutch - keep interiors disjoint in XZ and only let the
INTENDED grid neighbor abut.

Recipe in Section 4.

### 2c. QUEST TELEPORTS (scripted)

Two scripted-warp primitives, both driven from a `.qst` file:
- `Action_BoatDialog` teleports the player to RAW world coords `(x,y,z)` (upstream
  proven). Fields: `npc, onOff, x, y, z, tag` (`tools/qst_format.py:162`; builder
  `make_boat_dialog_action` at line 666). The target MUST be an on-mesh walkable cell
  at floor Y - derive it from the destination level's `0x0b` donor
  (`origin = center - dims`; verify `area != 0` there), NOT from the LEVELS grid
  corner, and beware the +16 X/Z padding (Section 11). Off-mesh coords silently no-op.
- `StrategicMovementTeleportShrine` records for shrine-style warps (record-driven).

WARNING (learned twice): quest-driven entrances are FRAGILE. Quest step state bakes
into character saves, and the "200x-repeated `OnLevelLoad` step" idiom
(`REPEAT_STEPS = 200` in `tools/build_quest_files.py:33`) broke in-game twice. The
whole blood-cave boat-dialog entrance was removed in favor of mechanism (b). Use quest
teleports only for genuine scripted events (a shrine warp, a boss-arena entry), never
as the primary way into a persistent area.

---

## 3. Navmeshes: the non-negotiable

If a level has no valid `0x0b` navmesh, the click-to-move pathfinder refuses to enter
it -> invisible wall. This is THE root cause of the historic map bug. The stock TQAE
LVL parser has NO handler for the legacy `0x0a` PathEngine mesh - it silently skips it
(disassembly-verified 2026-07-03). So every walkable custom area needs a real `0x0b`.

There is no shortcut: the 148-byte "empty `0x0b` stub" does NOT work. It bets on the
engine's runtime Recast generator (`ProcessRLTD_flow`, VA `0x101F6210`) rebuilding the
mesh at load, but that generator is gated by `cmp byte[0x10374441],0 / je (skip)`, and
gate byte `0x10374441` lives in zero-initialized memory that NOTHING in the 3.78 MB
Engine.dll ever sets non-zero. It is Editor/tool-only dead code in the shipping build.

> **b89 (2026-07-27) - that stub was worse than useless, it was a CRASH.** It was also
> MALFORMED: written against a wrong format model, it emitted ONE truncated 44-byte
> parameter block (a real `dtTileCacheParams` is 52 B) instead of the THREE complete
> 56-byte tilesets the engine parses, plus a degenerate `[own, own, own]` GUID list.
> `ProcessRLTD` therefore ran off the end of the 148-byte section into the heap and
> killed the game whenever such a level streamed in (two Frida sessions, both at
> `ocean_extension05`). **A level with no walkable geometry must get a structurally
> VALID EMPTY container** (`build_minimal_rec02`, 224 B: own GUID once + 3 complete
> tilesets with `numTiles = 0`) - the shape stock TQAE ships for its own 60
> walkable-floor-less border/vista levels. And note "declared cut" does NOT mean "not
> streamed": the engine streams by grid proximity, so every level in the LEVELS index
> needs a well-formed section. See `docs/reports/b89_ocean_ext05_hotfix.md`.
The stub is kept ONLY for the 7 ocean-scenery levels that have no walkable geometry
(so the build stays green); see `build_minimal_rec02()` in
`tools/build_section_surgery.py:310`.

The TQAE Editor cannot bake navmeshes for custom GridSystem levels on this machine
(black viewport / "Error creating path mesh"). The way forward is the OFFLINE PYTHON
pipeline, which shipped.

### 3.1 The `0x0b` (`REC\x02` / RLTD) format

Full byte-accurate spec lives in the docstring of `tools/rec02_format.py:1-57`
(proven by round-trip identity over 370 Editor-baked + 300 SVAERA levels). Summary:

Container (all little-endian):
```
+0   b'REC\x02'
+4   uint32 version == 1        (engine skips the section otherwise)
+8   uint32 payload_size        == total - 12
+12  uint32 guid_count          (1..13 observed)
+16  guid_count x 16B GUIDs     own level GUID FIRST + geometry-contributing
                                neighbor level GUIDs
+..  int32  center[3]           world center = grid corner + half-extents
+..  uint32 dims[3]             half-extents (x/z: level half-extent + 16 padding)
+..  EXACTLY 3 tilesets         Normal / Epic / Legendary difficulty sets
```
Each tileset:
```
52B  dtTileCacheParams (orig=0,0,0; cs=ch=0.2; width=height=64;
     walkableHeight=2.0; walkableRadius; walkableClimb=1.0;
     maxSimplificationError=1.3; maxTiles; maxObstacles=128)
+52  int32 numTiles
     then numTiles x record:
       int32 dataSize
       dtTileCacheLayerHeader (56B; magic int32 == bytes b'RLTD'; version=1;
         tx,ty,tlayer; bmin[3],bmax[3] level-local; hmin,hmax; width=height=64;
         minx,maxx,miny,maxy usable sub-rect; pad[2])
       FastLZ-0.1.0-level-1 compressed heights + areas + cons (4096 cells each,
         64x64: heights = cell y - hmin, 0xff empty; areas 0=unwalkable, 1..6
         walkable classes [base game uses id 2 heavily]; cons = 4-dir connectivity
         low nibble + tile-border portals high nibble)
       int32 tx, ty (repeated trailer)
```

Key facts:
- The engine builds the actual navmesh polys AT LOAD from the rasterized layers
  (`dtTileCache::buildNavMeshTile`), so an offline generator only needs CORRECT
  RASTERIZATION - it does not need to prebuild polys.
- Base game uses `walkableRadius` 0.4/0.6/0.8 across the 3 sets; our generator emits 3
  identical sets at 0.4. This works; noted only for fidelity.

### 3.2 THE ENGINE GUID GATE (the second most important fact in this repo)

`ProcessRLTD` (VA `0x101f4ba0`) enforces: EVERY GUID in the section's GUID list must
resolve in the loaded world's level-GUID map, or the WHOLE section is REJECTED (silent
no-navmesh -> invisible wall). One unresolvable GUID kills the entire navmesh. This is
why merging (which changes which levels/GUIDs exist) forces GUID remapping on every
donor. See `tools/rec02_format.py:12-15,51-56` and `tools/gen_bc_navmeshes.py:22-27`.

### 3.3 The offline generation pipeline (pure Python, no Editor, no Recast lib)

Four stages, all committed and deterministic:

1. `tools/tok_parse.py` - tokenize the `0x0a` PathEngine "tok" walkable-surface mesh
   (verts/tris). `extract_mesh(path)` returns `(guids, center, dims, tok)`.
2. `tools/gen_rec02.py` - rasterize tris onto a `cs=0.2` cell grid, erode by
   `walkableRadius` (2 cells), compute per-cell height indices, slice into 64x64
   tiles, build heights/areas/cons planes, emit 3 difficulty sets. `generate(path)`
   returns `(doc, stats)`. Full docstring at `tools/gen_rec02.py:1-11`.
3. `tools/fastlz.py` - byte-exact Python port of FastLZ 0.1.0 level 1
   (`fastlz1_compress` line 75, `fastlz1_decompress` line 23), matching
   recastnavigation's bundled fastlz.
4. `tools/rec02_format.py` - byte-accurate `REC\x02` container serialize/parse
   (`serialize_rec02` line 119, `parse_rec02` line 69).

### 3.4 The donor driver + injection (this is the actual blood-cave fix)

`tools/gen_bc_navmeshes.py` is the driver. It:
- reads the PRISTINE upstream SV `0x0a` from
  `upstream/soulvizier_098i/Resources/Levels.arc` (the decompiled tree lost 28/30
  xBloodCave `0x0a` to failed Editor re-saves; upstream is untouched);
- generates the `0x0b` via `gen_rec02.generate()`;
- REPOSITIONS it to the merged grid by SHIFTING the container center by `GRID_SHIFT`
  (imported from `svaera_plus_portals.py` so the two can never drift -
  `tools/gen_bc_navmeshes.py:56`). The tile records are level-local, so shifting only
  the center repositions the whole mesh;
- REMAPS the GUID list to merged-world-resolvable GUIDs via
  `build_merged_guid_map()` (line 74) + `resolve_guids()` (line 107): keep each GUID
  that resolves, remap SV->AE for replaced shared levels, DROP any that still fails.
  Supports an own-GUID override (`OWN_GUID_OVERRIDE`, line 179) for the blob-swapped
  Random09A doorway cave;
- writes `local/editor_normalized/<basename>.0b.bin` (raw `0x0b` section bytes).

Run: `py tools/gen_bc_navmeshes.py` (about 3-4 minutes for the 23+1 levels,
deterministic; `--dry-run` to generate + self-verify without writing). The driver
self-verifies each donor: round-trip identity, exactly 3 sets, shifted center, every
GUID resolves.

Injection into the merged map is done by `svaera_plus_portals.py` (Section 9) via
`inject_rec02_into_blob(..., pre_positioned=True)` in
`tools/build_section_surgery.py:373`. Three donor modes:
- Tier 1 (`pre_positioned=True` + `donor_data`): insert the `.0b.bin` VERBATIM. The
  donor is already correctly positioned + GUID-correct, so `transplant_rec02` must NOT
  run (it would overwrite neighbor GUIDs and recompute the center, corrupting a
  correct section). This is the real fix path.
- Tier 2 (`donor_data` alone): `transplant_rec02` repositions an Editor-baked donor's
  header to this level's shifted grid (kept for any future Editor donor).
- Tier 3 (`use_stub=True`): `build_minimal_rec02`'s 224-byte structurally VALID EMPTY
  container (own GUID once, 3 complete tilesets, 0 tiles) for levels with no `0x0a`
  geometry to rasterize - the 7 ocean-scenery blood-cave levels + `coldtombs`. This
  section IS parsed by the engine when the level streams; it must never be partial
  (b89).
`inject_rec02_into_blob` ALWAYS strips `0x0a` so a `ProcessRLTD` reinit cannot clobber
the `0x0b` handler state.

### 3.5 Verify navmeshes

`py tools/verify_merged_bc_navmeshes.py` byte-verifies the FINAL merged map: for every
blood-cave level (+ the Random09A doorway), the `0x0b` size == the generated donor's
`.0b.bin` size and `0x0a` is stripped; ocean-scenery gets the 224-byte empty container.
Since b89 it also WALKS each container's structure (3 complete tilesets, clean end), not
just its size - size-only comparison is what let 8 malformed containers ship. Exits
non-zero on any miss (`tools/verify_merged_bc_navmeshes.py:1-9`). This is a hard gate
before deploy.

---

## 4. RECIPE: add a new cave (surface mouth -> interior)

Goal: a walk-in cave like the blood cave. Worked reference:
`docs/blood_cave_walkin_entrance_plan.md` (read it - it is the fully-verified example).

Choose your interior strategy first:
- Strategy A (blob-swap an existing base-game cave): hijack a base cave the surface
  already binds to (this is how the blood cave reuses the Silk Road cave). Best when a
  suitable base cave mouth already exists on the surface.
- Strategy B (brand-new interior level): append a new SV-only level and inject a new
  `GridEntrance` + `0x14` binding onto the surface level.

### Steps (Strategy A - blob swap; the proven path)

1. Find the surface cave mouth. Confirm the surface level's `0x05` places a
   `GridEntrance` DBR and its `0x14` record (same instance index) carries the base
   cave's GUID at payload `@44`. (For Silk Road: HiddenValley01, instance #30,
   `SilkRdDngEntrance_C01_Ext.dbr`, Random09A GUID at `@44`.) A helper scan pattern is
   in `docs/blood_cave_walkin_entrance_plan.md:22-24`.

2. Pick the interior blob (your custom cave, v0x0e) and decide its merged grid corner
   so that it is XZ-DISJOINT from all surface levels (mandatory) and its intended
   neighbor edge ABUTS. For the blood cave the shift is `GRID_SHIFT[...] = (1663,0,922)`
   putting Random09A at corner `(-198,18,2135)` so its WEST edge x=-198 meets shifted
   `xPassageTransitionStart`'s EAST edge (`tools/svaera_plus_portals.py:83-90`; the
   worked collision math is `docs/blood_cave_walkin_entrance_plan.md:99-123`). For a
   NEW cave, use the same abut-not-overlap arithmetic.

3. GUID strategy (decisive): KEEP the base cave's (AE) GUID in the merged LEVELS index
   for that slot. Then the surface mouth's `0x14` binding still resolves (no surface
   edit) and any neighbor navmesh listing that GUID still resolves (no regen of the
   neighbor). Achieve this by swapping only the blob + grid corner while writing AE's
   GUID into `ints_raw[36:52]` (`tools/svaera_plus_portals.py:541` onward, the
   `_r09_swap` machinery: `swapped_ints[36:52] = ae ... GUID`; line numbers may drift
   if that file is mid-edit - grep for `_r09_swap`).

4. Generate the interior's `0x0b` with `tools/gen_bc_navmeshes.py`. For a blob-swapped
   cave, add it to the batch with an `OWN_GUID_OVERRIDE` so its own GUID = the KEPT AE
   GUID, and set its neighbor GUID to the abutting level (Random09A -> neighbor
   xPassageTransitionStart; `tools/gen_bc_navmeshes.py:168-180`). Confirm `resolve_guids`
   drops 0 and the shifted center is right.
   Run: `py tools/gen_bc_navmeshes.py`.

5. Ensure the interior's `0x06` return-link resolves: it must embed the SURFACE level's
   GUID. If you blob-swapped an SV cave that already targeted the same surface level
   (shared GUID), this is free (blood cave: HiddenValley01's GUID is identical in SV
   and AE). Otherwise you must patch the `0x06` return GUID.

6. Wire the blob swap into the merge (`tools/svaera_plus_portals.py`, the Random09A
   swap block at ~line 541 + the DATA-compaction override at ~line 637; grep
   `_r09_swap` if it moved). Keep the
   base slot's GUID/fname/bitmap; take the SV blob + shifted corner + the generated
   `0x0b` (via `inject_rec02_into_blob(..., pre_positioned=True)`). Do NOT append the
   swapped level as an extra entry - it stays a single in-place swap so the level
   count + GUID set are unchanged. (If a concurrent edit is in flight, treat
   `docs/blood_cave_walkin_entrance_plan.md` Section 6.1 as the authoritative recipe
   for the exact edit.)

7. Build + verify + deploy (Section 9). Verify with
   `py tools/verify_merged_bc_navmeshes.py` (must be PASS, `0x0a` stripped).

8. In-game: enter the surface cave mouth, take the interior tunnel into the new area.
   The ONE thing static analysis cannot confirm is end-to-end tunnel walkability +
   the grid-seam hand-off (`docs/blood_cave_walkin_entrance_plan.md:113-121`). Fallback
   levers if a gap shows: flip the navmesh area flag / adjust erosion on that donor
   (Section 10 fallbacks); nudge the shift so the seam overlaps a full tile rather than
   merely abutting.

### Steps (Strategy B - new interior + injected mouth)

Same as A, but:
- Append the new interior as an SV-only level (new GUID; `svaera_plus_portals.py`
  append path). Its `0x0b` own-GUID = its OWN new GUID (no override needed).
- Inject a `GridEntrance` art entity into the surface level's `0x05` at the mouth's
  local position, and APPEND a matching `0x14` record whose 60-byte payload embeds the
  new interior's GUID at `@44` (and reciprocal UniqueIds at `@12`/`@28`). This needs a
  `0x14`-writer that appends a GUID-list payload rather than the default 20-byte
  payload (`generate_default_0x14()` in `tools/build_section_surgery.py:551` writes the
  default; the GUID-binding variant is sketched in
  `docs/blood_cave_walkin_entrance_plan.md:330-340`, Section 8 - it is the only piece
  not yet built, since Strategy A avoided it).
- Ensure the interior's `0x06` embeds the surface level's GUID for the return.

Placement rule is identical: interior XZ-disjoint from surface, mouth tile aligned so
the player walks onto it.

---

## 5. RECIPE: add a new walkable area / extension (grid-seam)

Goal: extend a walkable region with a new adjacent tile the player walks onto with no
mouth and no teleport (e.g. widen an outdoor area, add a side room reachable by
walking).

1. Author/obtain the new level blob (v0x0e is fine; the merge handles it) with its
   `0x05` entities and `0x06` terrain.
2. Choose its grid corner so its footprint ABUTS (shares an edge with) the existing
   level's footprint. Footprint = `corner .. corner + tile_dims*2`. If you are
   relocating an SV cluster, add a `GRID_SHIFT` key (substring-matched against the
   level path) in `tools/svaera_plus_portals.py:83` and regenerate donors AFTER
   editing it (import order matters - `gen_bc_navmeshes` imports `GRID_SHIFT`).
3. Generate its `0x0b` (Section 3.4). Its GUID list must include its OWN GUID first and
   the abutting level's GUID as a neighbor (so the seam resolves the GUID gate on both
   sides). If the neighbor is a level whose GUID changed in the merge, remap SV->AE via
   `resolve_guids`.
4. Alignment verification: the two navmeshes' walkable bands must overlap across the
   shared edge (>= 4 world units aligned). There is no dedicated seam-checker script;
   the practical check is (a) `verify_merged_bc_navmeshes` proves the donor landed, and
   (b) the in-game walk test proves the hand-off. If it fails, nudge the shift so the
   footprints overlap by a full tile (12.8u) rather than merely abut, or widen the
   walkable band at the edge (erosion fallback).
5. Build + verify + deploy (Section 9), then walk the seam in-game.

The blood-cave interior chain (Section 2a) is the reference: a string of levels each
abutting the next, each with a generated `0x0b` listing its neighbor(s), no entities.

---

## 6. RECIPE: add / port quests

`tools/qst_format.py` is a fully reverse-engineered `.qst` reader/writer/spec
(89/89 byte-identical round-trip; full format spec at `tools/qst_format.py:1-97`).
`parse(data)` returns a nested tree of tuples `('block', sub_items)` /
`('field', key, ('int'|'str', val))` (`tools/qst_format.py:300-307`). Note: `parse()`
renders int32 as UNSIGNED - normalize when comparing signed values (e.g. negative
teleport coords). Condition/action classes and their field lists are in
`CONDITION_FIELDS` / `ACTION_FIELDS` (`tools/qst_format.py:139,160`); ready-made
builders are the `make_*` helpers (line 596+).

### 6a. Port an existing upstream questline (the cheap path)

If the map's QUESTS section already registers the quest name **at an index the engine
LOADS** (see the load-window rule below) AND the level blobs already place the trigger
volumes/proxies/doors, then adding the questline is a Quests.arc-ONLY change (NO map
rebuild). This is how `urder`, `widowletter`, `bossarena`, `open_bloodcave_portal` were
integrated (`tools/build_quest_files.py:53-75`):

1. Copy the upstream `.qst` byte-for-byte from
   `upstream/soulvizier_098i/Resources/XPack/Quests.arc` into the mod's `Quests.arc`
   at the ARCHIVE ROOT (basename only - the engine strips the folder prefix and
   resolves at the root; `tools/build_quest_files.py:47-52`).
2. Confirm every record + text tag the quest references resolves in the built `.arz` /
   `Text.arc` (Section 8). If a referenced NPC/record was dropped by the merge, either
   restore the record or surgically neutralize just that trigger (6c).
3. Rebuild `Quests.arc` (the DB/text/quests build; Section 9). Byte-scan the built qst
   for expected coords/refs as a cheap verification.

> 🚨 THE QUESTS LOAD-WINDOW RULE (cost a repeat bug - "widow letter STILL missing").
> Merely having the quest NAME somewhere in the world's QUESTS(0x1b) list is NOT enough:
> **the engine only loads a QUESTS entry that sits within the first ~256 registered
> entries** (vanilla TQAE registers exactly 256 and all load; SVAERA registers 254). An
> entry APPENDED past that window NEVER loads for ANY character - the quest never tracks,
> its `OnLevelLoad` triggers never fire, no letter/chest/reward. This is empirically proven
> (docs/QUEST_STATE_INJECT.md sec 2: 53 appended entries produced zero state across 5
> custom-quest chars + vanilla saves). The prior build appended the 4 SV quests at idx
> 254-257 (widowletter at 256) and they were dead. THE FIX (build22): rebuild the QUESTS
> section so ported quests sit at a LOW index inside the window, via
> `tools/svaera_plus_portals.py build_ordered_quest_list` (a MAP rebuild). It: inserts the
> primary `Quests/<name>.qst` forms right after `Quests/sv_commonmechanics.qst` (idx 96),
> drops redundant native re-registrations (identity-duplicates like the 3x
> `x2quest_controlsdoors.qst`) to make room, and drops the appended `XPack/Quests/*`
> dup+dead tail (every identity is preserved by a native `Quests/` twin - the engine keys
> identity on the folder-stripped BASENAME: `md5(quests\<basename>.qst)`). Keep the final
> list <= 256 and keep the idx 254-255 tail == vanilla's (`x4_other_002_hcdungeon_control`
> + `x2_StartQuest`) so nothing a player needs shifts out of the window. Verify with the
> C5 gate (`tools/debug/gate_c5_regression.py`): 4 SV quests at idx < 254, no native lost
> from idx < 256, total <= 256. So porting an upstream questline whose name is ONLY in the
> appended tail DOES require a map rebuild to relocate it into the window.

### 6b. Author a new quest

Build a `Quest` object (`Quest`, `QuestStep`, `Trigger`, `build_quest` in
`tools/qst_format.py`) using the `make_*` helpers, serialize with `build_quest()`, and
write it into `Quests.arc` at the root. Register its name in the map's QUESTS section
(the merge does this for the names it knows; a genuinely new name must be added to the
merged QUESTS list in `svaera_plus_portals.py` and the trigger volumes/proxies placed
in the relevant level blobs -> that IS a map rebuild).

### 6c. Surgically neutralize a broken trigger

To drop a single trigger that references a lost record without disturbing the rest of a
ported quest, follow `_neutralize_bloodcave_entry_step()` in
`tools/build_quest_files.py:132`: parse the tree `[header_block, steps_container]`;
the steps container holds flat triples per step `(stepdef, trigger_container, sentinel)`;
a trigger container holds a `max` field then flat triples per trigger
`(trigger_header, conditions, actions)`; find the trigger whose actions block mentions
the dead record, DROP that triple, and DECREMENT the container's `max`. Re-serialize
through `qst_format`. This is exactly how the lost `starting_storyteller.dbr` trigger
was removed while keeping the rest of `open_bloodcave_portal.qst` byte-identical.

### 6d. Fragility warnings (read before using quests for movement)

- Quest step STATE bakes into character saves. A change to step structure can strand an
  existing save mid-quest.
- The `REPEAT_STEPS = 200` `OnLevelLoad` idiom (`tools/build_quest_files.py:33`) broke
  in-game twice. Avoid it for anything load-bearing.
- Do NOT use a quest to get the player into a persistent area; use mechanism (a)/(b).
  The whole blood-cave boat-dialog entrance was ripped out for this reason
  (`tools/build_quest_files.py:12-18,37-44`; the obsolete section in `CLAUDE.md`
  "Entrance bugs - OBSOLETE").

---

## 7. RECIPE: portals & teleports done right

- Interior portal PAIRS (cave <-> surface return): handled by mechanism (b) - the
  destination's `0x06` carries the reciprocal portal UniqueIds + the source GUID. You do
  not author a separate "portal record"; you author the `0x14` binding + the `0x06`
  return link. (Section 2b, Section 4.)
- Shrine / event warps: use a `StrategicMovementTeleportShrine` record, or an
  `Action_BoatDialog` from a quest, targeting an ON-MESH cell.
- `Action_BoatDialog` target coordinates - the rule that bit twice: the target MUST be
  a walkable navmesh cell at the correct floor Y. Derive it from the destination's
  `0x0b` donor: `origin = center - dims`, then find a cell with `area != 0`, and correct
  for the +16 X/Z padding baked into `dims` (the navmesh grid spans local `[0, 2*dims]`
  but the walkable content starts `pad=16` in on X/Z; `tools/gen_rec02.py:26,197-208`).
  Do NOT compute the target from the LEVELS grid corner - that is off by the padding and
  the half-extent, and off-mesh coords silently no-op. The old blood-cave teleport
  landed ~1900 units into void by using the unshifted SV coord against a shifted cluster
  (`CLAUDE.md` "Entrance bugs", `tools/build_quest_files.py:33` history).
- `Action_OpenDynGridEntrance` (`make_open_dyn_grid_entrance_action`,
  `tools/qst_format.py:655`) opens a dynamic grid entrance by name - relevant if you
  want a quest to reveal a cave mouth that starts closed.

---

## 8. RECIPE: new records / entities / items into the DB, and injecting entities

### 8.1 The database (`.arz`)

The mod DB is built by `tools/build_svc_database.py` from the upstream SV `.arz` files
plus the base game `database.arz`, producing
`work/SoulvizierClassic/Database/SoulvizierClassic.arz`. In Custom Quest mode the mod DB
is STACKED over the base `database.arz`, so ANY base-game record resolves for free even
if it is absent from the mod DB (e.g. `starting_storyteller.dbr` exists in base). This
is why you rarely need to author base-adjacent records - import them from `base_db`
instead.

Record-authoring patterns (all in `tools/build_svc_database.py` /
`tools/apply_svc_patches.py`):
- `_ensure_record(db, path, template)` - create a bare empty record with a template
  (`tools/apply_svc_patches.py:18`). Use this for souls (never `clone_record` a soul -
  it drags stat values that corrupt saved items; `CLAUDE.md` lessons).
- `db.clone_record(src, dst)` then `db.set_field(...)` - copy an existing record and
  tweak fields (used for portal NPCs cloned from the Egypt boat captain;
  `tools/build_svc_database.py:1283-1290`).
- Import a base-game record into the mod DB by copying its fields from `base_db`
  (`_import_boat_captain` line 1201, `_import_dialog_needed` line 1229).
- CRITICAL dtype lesson: never pass an explicit dtype to `set_field()` on a CLONED
  record - INT/FLOAT corruption silently zeroes values (pet spawn failure). See
  `CLAUDE.md` "Key technical lessons".

Records are authored on disk as ArtManager-format `.dbr` when they must be loose (CRLF
line endings, `key,value,` lines). `tools/populate_svbake_records.py` extracts placed
records to loose `.dbr` (that tool exists for the abandoned Editor-bake path; you rarely
need it now that navmeshes are generated offline).

### 8.2 Level classes for custom dungeons

A custom dungeon interior is typically a `GridSystem`-class level
(`records\drxmap\bloodcave\bloodcave.dbr`, Class `GridSystem`, template
`Engine\GridSystem.tpl`): a grid-tile system whose `feature` + `wallPieceBase*` fields
list the floor/wall `.msh` pieces (`CLAUDE.md` blood-cave subsection). Placed dungeon
pieces are `Decoration` records with `mesh` + `baseTexture`.

### 8.3 Art resolution

Meshes/textures come from `.arc` archives (the first path component of an asset path is
the archive name, e.g. `SVItems\jewelry\soul_n_icon.tex` -> archive `SVItems`). Records
must resolve in the built `.arz` OR the base game. Text/name/desc tags must resolve in
`Text.arc` (built by `build_text_arc`; every soul name uses a `{^F}` prefix for
pink/magenta and its `tag...` must exist in `Text.arc`). Do NOT run `-LiteMode`: it
strips `drx.arc` + `DRXtextures.arc`, which hold the blood cave's own terrain meshes +
wall textures (`CLAUDE.md` release plan).

### 8.4 Inject entities into an EXISTING level

Use `INJECT_SPECS` in `tools/build_section_surgery.py:121` - a map of
`level path key -> [(dbr_bytes, x, y, z), ...]` that appends DB-backed entities into
that level's `0x05` at LOCAL coords (with a 0x14 metadata entry generated for v0x11
levels). `inject_into_0x05` (line 146) handles v0x0e (56-byte records),
`inject_into_0x05_v11` (line 479) handles v0x11 (72-byte). Note the history in
`INJECT_SPECS`: injecting into a v0x11 Delphi level corrupted the blob and crashed
world streaming, and the blood-cave surface NPC injects were REMOVED once the walk-in
mechanism replaced them (`tools/build_section_surgery.py:121-139`). Keep injections to
levels + formats proven safe, and always regenerate `0x14` to match the new instance
count.

### 8.5 Validate tags (build gate)

`py tools/validate_tags.py <final.arz> <final_text.arc>` fails loud if any MOD-OWNED
name/desc tag referenced by the `.arz` is missing from `Text.arc`
(`tools/validate_tags.py:1-53`). It is a build gate - a missing tag shows the raw
`tag...` string in-game. The build passes today (every referenced authoritative tag
resolves).

---

## 9. The build -> verify -> deploy loop

The disciplined path (commands assume repo root, `py` launcher,
`PYTHONIOENCODING=utf-8`):

1. EDIT tools/records/quests as needed.

2. If placement (grid corner / `GRID_SHIFT`) changed, REGENERATE donors:
   ```
   py tools/gen_bc_navmeshes.py            # ~3-4 min; writes local/editor_normalized/*.0b.bin
   py tools/gen_bc_navmeshes.py --dry-run  # generate + self-verify, write nothing
   ```
   Edit `GRID_SHIFT` in `svaera_plus_portals.py` FIRST, then regenerate - the driver
   imports `GRID_SHIFT`, so donors must be produced AFTER the shift is set.

3. BUILD the merged map (heavy, ~2 min, writes `local/Levels_merged.arc`):
   ```
   py tools/svaera_plus_portals.py
   ```
   Sanity in its output: levels count, `Bad offsets: 0`, `Bad magic: 0`, size < 2GB.
   (The append-clone at idx 2281 is a harmless diagnostic.)

4. BUILD the DB + Text + Quests (produces the `.arz`, `Text.arc`, `Quests.arc`):
   ```
   scripts/bootstrap_working_mod.ps1        # DB + text + resources (NO -LiteMode)
   ```
   or the direct DB build in `CLAUDE.md` "Build & deploy commands". `validate_tags` runs
   as a gate; `Quests.arc` arc-verify should report all-OK / 0-FAIL.

5. VERIFY navmeshes landed:
   ```
   py tools/verify_merged_bc_navmeshes.py   # must PASS: every donor present, 0x0a stripped
   ```
   (`tools/verify_editor_output.py` is only for the abandoned Editor-bake path.)

6. DEPLOY to CustomMaps (backs up ALL character saves + the prior deploy first):
   ```
   powershell -ExecutionPolicy Bypass -File scripts/deploy_to_custommaps.ps1 -SyncLevels
   ```
   `-SyncLevels` is OPT-IN on purpose: it copies `local/Levels_merged.arc` into `work/`.
   Only pass it after you have verified the local build is correct - a stale local
   rebuild once nearly clobbered the good deployed map
   (`scripts/deploy_to_custommaps.ps1:11-16,89-110`). Without it, the deploy uses the
   existing `work/.../Levels.arc`.

7. TEST in-game: TQAE -> Play Custom Quest -> `SoulvizierClassic`, using a DEDICATED
   Custom Quest character (never a mainline character). Testing aids: soul drops are
   forced to 100% by default for testing (`SVC_RELEASE_DROPS=1` gives tuned rates).

8. SHIP (Steam Workshop, when ready):
   ```
   scripts/package_workshop.ps1             # stages dist/workshop/SoulvizierClassic/
   scripts/upload_workshop.ps1              # steamcmd, appid 475150
   ```

What each verifier proves:
- `svaera_plus_portals.py` self-verify: offsets/magic valid, under 2GB, drxmap present.
- `verify_merged_bc_navmeshes.py`: every generated donor is present at its exact size in
  the final map and `0x0a` is stripped (the anti-invisible-wall gate).
- `validate_tags.py`: no referenced mod tag is missing from `Text.arc`.
- `gen_bc_navmeshes.py` per-donor asserts: round-trip identity, 3 sets, shifted center,
  all GUIDs resolve.

Engine reality (do not fight it): the engine is 32-bit with a ~4GB LAA ceiling; the
merged map decompresses to ~2GB. Crashes under load are a memory-exhaustion engine bug,
not a mod bug (`docs/crash_analysis_report.md`). Mitigation shipped as INSTRUCTIONS: the
community 4GB LAA patch on `TQ.exe`. You cannot redistribute a patched `TQ.exe` (Steam
verify reverts it, and a content mod cannot ship the exe) - ship it as README guidance
only.

---

## 10. Failure graveyard (do NOT repeat)

| What was tried | Why it failed | The rule |
|----------------|---------------|----------|
| Ship levels with `0x0a` only | Stock engine has no `0x0a` handler; silently skipped -> invisible wall | Every walkable level needs a real `0x0b` (Section 3) |
| 148-byte empty `0x0b` stub (Approach 22) | Runtime Recast generator is gated by byte `0x10374441`, never set non-zero in the shipping DLL -> dead; AND the stub was malformed (1 truncated tileset, not 3) so `ProcessRLTD` read past the section = **crash on stream-in** (b89) | No-geometry levels get the 224-byte VALID empty container; real areas need real navmeshes |
| Assuming a "cut"/unreachable level is never loaded | The engine streams by grid proximity, not by design intent - `ocean_extension05` sits inside the walkable `drxBC3` block and streamed every time (b89) | Every level in the LEVELS index needs a well-formed `0x0b`; `MAP-NAV-5`/`-6` deliberately ignore cut-ness |
| Quest-portal (boat-dialog) entrance | State bakes into saves; the 200x `OnLevelLoad` idiom broke in-game TWICE | Use engine-native entrances (a)/(b); quests for logic only |
| Off-mesh teleport target coords | Silently no-op; also the unshifted coord landed ~1900u into void on a shifted cluster | Derive target from `0x0b` origin `center-dims`, verify `area!=0`, mind +16 padding |
| Cave interior XZ-overlapping its surface region | Breaks the cave-mouth transition (invisible wall at threshold) | Interiors XZ-DISJOINT; only the intended neighbor edge abuts; edge-touch OK |
| Raw v0x0e blob into a v0x11 slot pattern | Crash on world streaming (git `f4fb176`) | Convert with `convert_v0e_blob_to_v11()`; magic + record stride must agree |
| `transplant_rec02` on a pre-positioned donor | Overwrites neighbor GUIDs with the own GUID + recomputes center -> corrupts a correct section | Inject pre-positioned donors VERBATIM (`pre_positioned=True`) |
| One unresolvable GUID in a `0x0b` GUID list | `ProcessRLTD` rejects the WHOLE section -> no navmesh -> invisible wall | Remap SV->AE, drop unresolvable, keep own GUID first (`resolve_guids`) |
| `transplant_rec02` capping diff_count at 4 | Wrote center/dims into the GUID region for donors with >4 GUID blocks -> mesh not repositioned | Read the real diff_count; only fall back if implausible for the section length (`tools/build_section_surgery.py:279-288`) |
| Running `-LiteMode` | Strips `drx.arc`/`DRXtextures.arc` which the blood cave's own meshes/textures need | Keep DRX; crash mitigation is the 4GB LAA patch, not stripping art |
| Deploy auto-syncing a stale `local` map | Nearly clobbered the good deployed map | `-SyncLevels` is opt-in; verify the local build first |
| Raw MapCompiler output with no GROUPS/SD/QUESTS patch (Exp 6) | Crashes immediately on Custom Quest start | GROUPS/SD/QUESTS/ints_raw patching is mandatory for load |
| SVAERA baseline deployed unmodified (Exp 7) | Worked perfectly - proved the wall came from SV merging, not the base map | Baseline-compare when a whole-map regression appears |
| Cap a DLC controller quest by storing a capped copy at the Quests.arc ROOT (basename) | Quest identity = `md5(FULL registry path)`, not `quests\<basename>`. The map registers `xquest_controlsbossdoors.qst` under `XPack/quests/...`, which resolves to the base game's UNCAPPED `xpack/Quests.arc`; the root copy is never consulted -> the IT-cap was 100% INERT and the post-Hades "Portal to the North" leaked to vanilla Act 5 (A5, 2026-07-11). Sibling of the build22 widow-letter inert fix | A "port a vanilla DLC controller with one action removed" fix MUST land in the matching mod `Resources/xpack/`/`XPack4/` Quests.arc, re-point the map QUESTS registry, or be done at the DB-record level (A5 = `RequireNoDLC` suppression + Victory-Portal un-gate). NEVER assume the engine strips a registry path to its basename |

The Exp 1-7 sequence (`tools/MAP_MERGE_EXPERIMENTS.md`) chased "terrain edge mismatch"
theories for the invisible wall before the TRUE root cause (`0x0a` never parsed) was
found by disassembly. Do not re-run those terrain-boundary experiments; the answer is
navmesh format, not tile geometry.

---

## 11. Appendix: engine internals cheat-sheet

Coordinate math:
- `SCALE = 2` world units per grid tile (LEVELS grid). Proof: HiddenValley01 corner
  (-134,2174) 64 tiles wide; east neighbor corner (-6,2174) -> dX = 128 = 64*2
  (`docs/blood_cave_walkin_entrance_plan.md:66-67`).
- Navmesh cell `cs = ch = 0.2`; tile = 64 cells = 12.8 world units.
- Navmesh grid origin (local) = `center - dims`; walkable content is inset by the
  `pad = 16` on X/Z (`tools/gen_rec02.py:26,197-208`). The container spans local
  `[0, 2*dims]`.
- `0x0b` container `center = grid_corner + half_extents`; `dims` = half-extents with
  X/Z `+16` padding and Y adjusted (`transplant_rec02`,
  `tools/build_section_surgery.py:296-305`).

`ints_raw` (LEVELS entry, 13 x int32): `[0..5]` tile dims, `[6,7,8]` grid corner
(world x/y/z, byte offset 24), `[9..12]` GUID (byte offset 36..52).

Blob magics: v0x0e = `0x0e4c564c` (`LVL\x0e`); v0x11 = `0x114c564c` (`LVL\x11`)
(`tools/build_section_surgery.py:241-242`). Map magic = `0x0650414d`
(`tools/merge_levels_binary.py:14`). Navmesh container magic = `b'REC\x02'`; tile
header magic = int32 `0x44544c52` == bytes `b'RLTD'` (`tools/rec02_format.py:38,101`).

Engine.dll VAs (session disassembly; for future RE cross-reference):
- `ProcessRLTD` `0x101f4ba0` - loads a `0x0b` section; enforces the GUID gate.
- `ProcessRLTD_flow` (runtime Recast generator) `0x101F6210` - DEAD in shipping build
  (gated by byte `0x10374441`, never set).
- `dtTileCache::addTile` `0x101002b0`; polys built at load via
  `dtTileCache::buildNavMeshTile`.
- `GridEntrance::Read` `0x10195240`.
- `Region::FindCrossedPortal` `0x1020c110` (portal open flag at `portal+0xfc`).
- `Portal::GetFrontToBackCoords` `0x102068b0`; `Portal::GetConnectedRegion` `0x102063e0`.

Format spec pointers (read these docstrings before editing the corresponding tool):
- `0x0b` / RLTD navmesh: `tools/rec02_format.py:1-57`.
- Offline navmesh generation: `tools/gen_rec02.py:1-11`, driver
  `tools/gen_bc_navmeshes.py:1-38`.
- FastLZ: `tools/fastlz.py:1-3`.
- `.qst` quest format: `tools/qst_format.py:1-97`.
- Map sections + LEVELS index + `ints_raw`: `tools/merge_levels_binary.py`.
- Level-blob surgery (sections, `0x05`/`0x14`, v0e/v11, rec02 inject):
  `tools/build_section_surgery.py`.
- The full merge (GRID_SHIFT, donor tiers, blob swap, append-clone, DATA/DATA2):
  `tools/svaera_plus_portals.py`.

Cave-mouth `0x14` payload offsets (60-byte GridEntrance binding, session-verified):
`@12` mouth Portal UniqueId, `@28` reciprocal exit Portal UniqueId, `@44` destination
level GUID (16B). Default (non-binding) `0x14` payload = 20 bytes `flags=2,0,1,1,0`
(`tools/build_section_surgery.py:108`).

Donor pipeline timings + outputs: `gen_bc_navmeshes.py` ~3-4 min, deterministic,
writes `local/editor_normalized/<basename>.0b.bin`; `svaera_plus_portals.py` ~2 min,
writes `local/Levels_merged.arc`. The current merged map is ~652MB compressed
(~2.04GB decompressed), 24/24 blood-cave navmeshes byte-exact.

---

## 12. Quick reference: "I want to add X"

- A new cave you walk into -> Section 4 (Strategy A if reusing a base cave mouth,
  Strategy B for a brand-new interior). Placement: interior XZ-disjoint, mouth tile
  aligned, `0x14` GUID binding on the surface, `0x0b` generated with the right own +
  neighbor GUIDs, `0x06` return link to the surface GUID.
- A walkable extension you walk onto -> Section 5 (grid-seam: abut footprints, generate
  `0x0b` listing the neighbor GUID, verify the walkable bands overlap).
- A quest (new or ported) -> Section 6 (port byte-exact into `Quests.arc` root if the
  name is registered + triggers placed = no map rebuild; author with `make_*` +
  `build_quest`; neutralize a broken trigger with the `_neutralize` pattern).
- A shrine/event warp -> Section 7 (`Action_BoatDialog`/`StrategicMovementTeleportShrine`
  to an ON-MESH cell derived from the `0x0b` origin).
- A new item/soul/pet/record -> Section 8 (`_ensure_record`/`clone_record`/import from
  base; validate tags; keep DRX).
- An entity into an existing level -> Section 8.4 (`INJECT_SPECS`, regenerate `0x14`).

Then always: build (Section 9 steps 2-4) -> verify (step 5) -> deploy `-SyncLevels`
(step 6) -> walk it in-game on a dedicated Custom Quest character (step 7).
