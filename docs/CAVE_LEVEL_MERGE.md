# Track 3: Merge the blood-cave chain into one/few levels - FEASIBILITY VERDICT

> Author: Track-3 feasibility pass, 2026-07-05. Read-only investigation + a scratchpad
> prototype (no shared-file edits; no full build run). Companion docs:
> `docs/WALL_INVESTIGATION_STATE.md`, `docs/CAVE_ENTRY_CHAIN_TRACE.md`,
> `docs/MODDING_PLAYBOOK.md`. Every load-bearing claim below is byte-verified against
> `upstream/soulvizier_098i/Resources/Levels.arc` (SV) and
> `reference_mods/SVAERA_customquest/Resources/Levels.arc` (SVAERA), with the probe
> scripts named in the appendix.

---

## 0. VERDICT (read this first)

**Merging the FULL ~31-level cluster into one level: INFEASIBLE** (navmesh poly/tile
ceiling + multi-terrain-per-level is unprecedented + entity/terrain/lighting rebuild is
enormous). Do not attempt it.

**Merging JUST the reported seam - `Random09A` + `xPassageTransitionStart` into one
level: FEASIBLE FOR THE NAVMESH, BLOCKED ON TERRAIN.** The navmesh half is already
solved and I have a working prototype (Section 5): one continuous 62-tile navmesh over
the union, no cross-level seam, round-trip-valid. **But the two levels use two DIFFERENT
terrain systems** (R09 = base-game `SilkRoadCave.dbr` GridSystem; xPTS = `drxmap`
GridSystem), and a TQAE level blob's terrain (`0x06`) + legacy grid (`0x09`) + baked
detail (`0x17`) are each a SINGLE level-box-sized structure bound to ONE terrain origin.
Fusing two heterogeneous GridSystem terrains into one `0x06`/`0x17` at two local origins
has **no base-game precedent and no tooling in this repo**, and would require either
re-authoring the terrain in the TQAE Editor (the exact tool proven unusable on this
machine - the whole reason the offline pipeline exists) or reverse-engineering + writing
a `0x06`/`0x09`/`0x17` terrain-fusion generator from scratch (very high risk, effort in
the tens of hours with an uncertain outcome).

**Effort to a shippable merged pair: 25-45 h with SIGNIFICANT risk of a dead end** on the
terrain-fusion step (the one piece with no precedent and no in-game confirmation possible
without a launch). **Recommendation: do NOT pursue Track 3 as the primary fix.** It is
strictly heavier and riskier than Track 2 (interior portal doorways, a proven mechanism)
and Track 1 (RE the seamless stitch), and its single genuine advantage - "no cross-level
seam" - is ALSO delivered by the far cheaper **placement fix already implied by the
latest root-cause** (Fix B in `CAVE_ENTRY_CHAIN_TRACE.md`: park the whole cluster as a
disjoint island so all rooms co-stream and the residency gate passes, leaving the
existing per-level navmeshes and grid-seams to stitch as base-game connected-dungeon
batches do). Track 3 is worth keeping on the shelf ONLY as a last resort if BOTH Track 1
and Track 2 fail in-game AND the specific R09<->xPTS seam is the sole remaining wall.

The rest of this doc gives the evidence, the format-capability findings, the minimal
design (in case it is ever needed), the effort breakdown, and the blockers.

---

## 1. What "merge into one level" actually requires

A merged super-level must carry, in ONE `.lvl` blob at ONE grid corner, the combined
content of N source levels. Concretely (blob-section by blob-section, all byte-verified):

| Section | Per-level today | Merge requirement | Mechanical? |
|---|---|---|---|
| `0x05` entities | string table + 56B records, coords LEVEL-LOCAL | rebase every record's local xyz into the merged frame; concat string tables (dedup) | **YES - trivial** (Section 3) |
| `0x06` terrain | ONE terrain/GridSystem DBR + a level-box-sized walkable/height grid + a portal-link trailer | fuse N heterogeneous terrains into one box-sized grid at one origin | **NO - the blocker** (Section 4) |
| `0x09` grid (v0e) | 24B legacy grid stub (R09 has it; xPTS does not) | reconcile presence/absence; regenerate for merged box | UNCLEAR (Section 4) |
| `0x0a` PTH navmesh | legacy, engine ignores it | dropped anyway (we generate `0x0b`) | N/A |
| `0x0b` RLTD navmesh | generated offline per level | generate ONE over the union footprint | **YES - PROVEN** (Section 5) |
| `0x14` metadata | per-instance; empty (0 bytes) on these v0e cave levels | regen default for merged instance count | YES - trivial |
| `0x17` baked detail | 40KB-123KB level-box-sized baked layer (lighting/occlusion/detail grid) | regenerate for merged box, or the merged level renders wrong | **NO - no generator** (Section 4) |
| LEVELS `ints_raw` | tile dims + grid corner + GUID | set to union box + one corner + one GUID | YES - trivial |
| mouth `0x14` binding (in HiddenValley01) | points at R09's GUID | point at the merged level's GUID | YES - trivial (Section 6) |

Two of eight sections (`0x06`, `0x17`) are the blocker; `0x09` is a question mark. The
navmesh (the historic pain point) is the EASY part here.

---

## 2. Format-capability findings (byte evidence)

### 2.1 LEVELS-index header (`ints_raw`) has ample capacity
`ints_raw` = 13 x int32: `[0..5]` tile dims (content x/y/z, box x/y/z), `[6,7,8]` grid
corner (world x/y/z, int32), `[9..12]` 16-byte GUID. Center in the `0x0b` header is int32;
dims are uint32. The full-cluster union center (~-3098, well inside int32) and the pair
union (240x128) both fit trivially. **The index/header format does NOT limit merging.**

### 2.2 The navmesh (`0x0b`) tile/poly ceiling DOES limit the full merge
Surveyed all 2214 SVAERA baked `0x0b` sections (`probe_capacity.py`):
- **Largest single-level navmesh ever shipped = Maze03 at 778 tiles/set** (576x576 world
  units). The tile-count distribution falls off a cliff above ~550; only ONE level exceeds
  600.
- The `dtNavMesh::init` per-set alloc is `maxPolys=1000` (`rec02_format.py:53`), and Detour
  builds polys per tile-layer at load (`dtTileCache::buildNavMeshTile`). Maze03 loads fine
  at 778 tiles, so the practical ceiling is "a few hundred tiles, up to ~778 proven".
- **The full cluster's union footprint = 2633 x 916 world units** (X[-4414,-1781]
  Z[599,1515]), which is **~206 x 72 = ~14,832 tiles per set** for a dense fill, and even
  the SUM of the current per-level donor tile counts is **3,107 tiles** (`probe_capacity.py`
  Q2). That is **4x beyond the largest navmesh the engine has ever loaded**, and the union
  bbox is ~4.6x Maze03's largest dimension. A single monolithic cluster navmesh is
  over-ceiling. **INFEASIBLE.**
- **The pair (R09+xPTS) union = 240 x 128 world units = 62 tiles/set** in the prototype
  (Section 5). Comfortably under Maze03. **Pair navmesh: FEASIBLE.** (Any sub-merge that
  stays under ~400-500 tiles is safe; e.g. R09+xPTS+BC_initialpathway would still be small.
  But the big rooms - drxBC_Finale 548, drxBC3 383, drxFirstRoom 360 tiles EACH - cannot
  be merged with others without approaching/exceeding the ceiling.)

### 2.3 The full cluster also fails the "one terrain per level" reality harder
The cluster's 31 levels reference MANY distinct terrain/GridSystem DBRs (SilkRoadCave +
numerous `drxmap` GridSystems + ocean terrains), and span Y from -37 to +18 with rooms
physically STACKED and overlapping in XZ at different Y (drxBC* rooms at Y-27/-37,
R09/xPTS at Y+18). A single box-sized `0x06`/`0x17` cannot represent stacked multi-Y
terrain. **This alone kills the full merge independently of the navmesh ceiling.**

---

## 3. Coordinate rebasing is mechanical (PROVEN)

`0x05` entity records store position at record offset +40 as three float32 in the level's
LOCAL frame. Verified (`probe_capacity.py` Q3): every instance's local xyz fits inside its
level's box:
- Random09A: 107 instances, local x[0.8,69.1] y[-6.0,12.5] z[3.7,76.6], box 80x80. Inside.
- xPTS: 9 instances, local x[3.0,116.0] z[82.3,93.1], box 160x128. Inside.
- drxFirstRoom: 2352 instances, local x[2.4,234.9] z[0.7,234.2], box 240x240. Inside.

So rebasing is a pure translation: for a source level with grid corner `C_src` merged into
a super-level with corner `C_merged`,
```
new_local = old_local + (C_src - C_merged)          # per axis, world units
```
This is trivial to implement and there is a natural home for it (a new tool; do NOT touch
`build_section_surgery.inject_into_0x05*`, which only APPENDS at given local coords - the
merge would call a new `rebase_and_merge_0x05(levels, merged_corner)` helper). Entity count
is not a concern (drxFirstRoom alone has 2352; the engine handles thousands). **Entities:
mechanical, low-risk.**

---

## 4. The terrain blocker (`0x06` / `0x09` / `0x17`) - byte evidence

### 4.1 `0x06` is ONE terrain description + a box-sized grid + a portal trailer
`probe_terrain.py` / `probe_terrain2.py`. The `0x06` layout (Random09A, 809 bytes):
```
+0   uint32 = 1
+4   uint32 = 2
+8   uint32 = 1
+12  uint32 outer_len = 721
+16  uint32 inner_len = 64
+20  "Records/Underground/NaturalCave/Orient/SilkRoad/SilkRoadCave.dbr"   <- THE terrain
+..  a walkable/height grid of ~653 bytes sized to the level BOX (40x40 tiles)
+..  portal trailer: exit UniqueId(89328d35..), mouth UniqueId(cfb4da3a..),
     source GUID(ce93e328.. = HiddenValley01)   <- the cave-mouth RETURN link
```
The grid after the terrain DBR is exactly one level-box worth of cells. It cannot describe
two boxes at two origins.

### 4.2 Multi-material IS allowed, but multi-TERRAIN-SYSTEM is not what these are
A first read of "1363/2235 levels have >=2 Records-refs in 0x06" looks like multi-terrain
is normal. It is NOT the same thing (`probe_terrain2.py`): those multi-ref levels are
OUTDOOR levels painting several `Records\TerrainType\...` MATERIALS (grass/rock/gravel
textures) onto ONE heightfield grid (Valley01 carries 4 TerrainType paints). The cave
levels instead each reference a whole `Records\Underground\...` or `records\drxmap\...`
**GridSystem** (a dungeon tile-piece system). R09 = `SilkRoadCave` GridSystem; xPTS =
`drxmap` GridSystem. **No base-game level fuses two GridSystem dungeon terrains into one
`0x06`.** The merged pair would be the first, with no reference implementation to copy and
no way to confirm it renders without an Editor bake or an in-game launch.

### 4.3 `0x09` presence is inconsistent across the pair
R09 has a 24-byte `0x09` legacy grid; xPTS has NONE (`probe_terrain.py`). A merged level
must pick one representation; the interaction of `0x09` with a fused GridSystem terrain is
unknown, and the failure graveyard already records that v0e/v11 + `0x09` mishandling
crashes world streaming (`MODDING_PLAYBOOK.md` Section 10). Extra risk surface.

### 4.4 `0x17` is a large baked level-sized layer that would be wrong post-merge
Every cluster level carries a `0x17` section of 40KB-123KB (`probe_capacity.py`/
`probe_terrain2.py`): a baked, level-box-sized detail/lighting/occlusion layer. Merged
into a bigger box at a shifted origin, the source `0x17`s no longer align; the merged level
would render with broken lighting/detail unless `0x17` is regenerated - and there is NO
`0x17` generator in this repo (it is Editor-baked). This is a second no-tooling blocker on
top of `0x06`.

**Net: the terrain/detail sections are the reason Track 3 is not a mechanical merge.** The
navmesh was the hard problem everyone feared; it turns out to be the SOLVED part, and the
terrain - normally trivial when you keep levels separate - is what a merge forces you to
fuse, with no precedent and no offline tool.

---

## 5. The navmesh half IS solved - working prototype (evidence)

`scratchpad/proto_merge_navmesh.py` (writes only to scratchpad) generates ONE navmesh over
the R09+xPTS union using the EXISTING `gen_rec02.generate()` neighbor-union machinery
(the same code path `gen_bc_navmeshes.py` already runs per level), by treating the union
footprint as one level and offering xPTS's tok as neighbor geometry to R09's:
```
MERGED footprint (SV coords): X[-2021,-1781] Z[1213,1341] = 240 x 128 world u
=== MERGED-PAIR single navmesh generated ===
  tiles/set = 62   maxTiles field = 1000   size = 122,289 B
  center = (-1888,24,1280)  dims(half) = (160,34,128)
  round-trip OK: True, sets = 3
  walkable cells WEST of the old R09|xPTS seam (xPTS side): 44,883
  walkable cells EAST of the old seam (R09 side):           71,545
  => single mesh covers BOTH sides continuously = NO cross-level seam
```
This is the entire point of Track 3 for the navmesh dimension: because the two rooms live
in ONE navmesh with ONE GUID list (own GUID only), there is **no cross-level walk-link to
build, no residency gate to satisfy, no seam to stitch** - the exact failure modes that
have walled every prior fix simply do not exist inside a single level's mesh. The generator
already unions the two toks (OWN-WINS + JOIN-RAMP handle the 2.6u floor disagreement), and
the tile count (62) is far under the proven 778-tile ceiling. **Navmesh: feasible, proven,
low-risk.** (It is the terrain, not the navmesh, that blocks shipping this.)

---

## 6. The mouth, quests, and GUIDs on a merged pair (handled/known)

- **Mouth rebind (easy):** HiddenValley01's `0x14` record #30 carries the destination GUID
  at payload `@44` (currently AE-Random09A's `d840e7ae...`). If R09 is absorbed into a
  merged level, either (a) give the merged level AE-Random09A's GUID (keep the mouth
  binding untouched, exactly the trick the current R09 blob-swap already uses), or (b)
  rewrite `@44` to the merged GUID. Option (a) is free and preferred. The merged level's
  `0x06` must still carry the reciprocal return trailer (exit/mouth UniqueIds + HiddenValley01
  GUID) so the walk-out resolves - it is present in R09's `0x06` today and must be preserved
  into the fused `0x06`.
- **Landing point:** the player materializes at R09's GridEntrance tile geometry, which is
  in R09's local frame; after rebasing R09's entities/terrain into the merged frame the
  landing tile moves with them, so the arrival stays consistent (no spawn proxy exists to
  fix up; `blood_cave_walkin_entrance_plan.md` Section 2.4).
- **Quests/scripts referencing individual GUIDs:** the cluster's questlines
  (`open_bloodcave_portal`, `urder`, `widowletter`, `bossarena`) resolve targets by level
  GUID and by placed trigger volumes/proxies inside the level blobs. Absorbing
  `xPassageTransitionStart` (which currently has its OWN GUID) into a merged level DROPS the
  xPTS GUID from the world. Any navmesh/quest/`0x06`-return reference to the xPTS GUID
  elsewhere would then fail the ProcessRLTD GUID gate or the quest target lookup. Audited
  scope: xPTS's GUID is referenced by its grid neighbors' `0x0a` lists (which we regenerate
  anyway) and potentially by cluster quest triggers. **This must be swept before a merge**
  (grep the merged world for the absorbed GUIDs; remap or drop). For the minimal R09+xPTS
  pair the exposure is small (xPTS has no known quest trigger of its own; it is a pure
  transition corridor), but it is real and is part of the effort.
- **GUID-gate upside:** the merged level lists only its OWN GUID (Section 5), so it is
  self-contained like base-game AE-Random09A and always loads once instantiated - it does
  not depend on any neighbor being resident. That is the clean property Track 3 buys.

---

## 7. The minimal-proof design (R09 + xPTS -> one level) - IF ever pursued

Smallest version that would kill the specific reported seam. Prerequisite that has no
current solution: a terrain-fusion step (7.3). Sketch, NEW files only:

1. **New tool `tools/merge_two_levels.py`** (do not edit shared build scripts): given two
   source `.lvl` blobs + their `ints_raw`, produce ONE merged blob + one `ints_raw`.
   - `merged_corner` = min corner of the two boxes; `merged_box` = union tile dims.
   - `0x05`: concat string tables (dedup by DBR), rebase every instance local xyz by
     `(C_src - C_merged)` (Section 3). Regenerate `0x14` default for the new count.
   - `ints_raw`: union box + `merged_corner` + AE-Random09A's GUID (keep the mouth binding).
2. **Navmesh:** generate ONE `0x0b` over the union with `gen_rec02.generate(footprint=union,
   neighbors=[the other tok])` and own-GUID = AE-Random09A's GUID (prototype in Section 5;
   promote `proto_merge_navmesh.py` into the tool). Inject `pre_positioned=True`, strip `0x0a`.
3. **Terrain fusion (`0x06`/`0x09`/`0x17`) - THE UNSOLVED STEP.** Options, all costly:
   - (3a) Author the merged terrain in the TQAE Editor and bake `0x06`/`0x17`/pathing. This
     is the "just use the Editor" path that is **already proven unusable on this hardware**
     (black viewport, "Error creating path mesh"); it is why the offline pipeline exists. If
     the Editor worked, the whole invisible-wall saga would have ended long ago. NOT viable
     here.
   - (3b) RE the `0x06` GridSystem-grid + `0x17` baked-layer formats and write an offline
     fuser that stitches two box-sized grids into one union-box grid at the correct sub-
     origins, choosing per-cell which source terrain owns each cell. High RE effort, and the
     result cannot be validated without an in-game launch (unlike the navmesh, there is no
     round-trip corpus of "merged" terrains to check against). This is the genuine risk.
   - (3c) Give the merged level a SINGLE uniform terrain (e.g. keep only R09's SilkRoadCave
     GridSystem, discard xPTS's drxmap terrain) and let the fused navmesh cover the corridor.
     Cheapest, but the xPTS corridor would render with the wrong (or missing) terrain art -
     visually broken, likely unacceptable for a ship.
4. **Wire the swap** the same way the current R09 blob-swap is wired in
   `svaera_plus_portals.py` (`_r09_swap` block), but the swapped blob is now the MERGED blob
   and the xPTS LEVELS entry is REMOVED (or emptied) so the world has one level where there
   were two. Sweep the merged world for the dropped xPTS GUID (Section 6).
5. **Build/verify/deploy/walk-test** per `MODDING_PLAYBOOK.md` Section 9.

Even this minimal version needs step 3, which is the blocker. Steps 1, 2, 4 are ~1-2 days;
step 3 is the open-ended risk.

---

## 8. Effort estimate + top blockers

**Effort (minimal R09+xPTS pair, to a shippable state):**
- `merge_two_levels.py` (entities rebase + `ints_raw` + wiring): ~6-8 h.
- Navmesh over union (promote the prototype): ~2-3 h (mostly done).
- Mouth rebind + GUID-drop sweep + quest audit: ~3-5 h.
- **Terrain fusion (`0x06`/`0x09`/`0x17`): 12-30+ h with a real chance of no viable
  outcome** (Editor path dead; offline fuser is fresh RE with no validation corpus; uniform-
  terrain shortcut is visually broken).
- Build/deploy/iterate on the walk test: several launches (Will-gated).
- **Total: ~25-45 h, dominated by an uncertain terrain-fusion step.**

**Full-cluster merge: not estimated - it is infeasible** (Section 2.2/2.3).

**Top blockers, ranked:**
1. **Terrain fusion has no tool and no precedent** (`0x06`/`0x17` are Editor-baked, box-
   sized, single-origin; two GridSystem dungeons cannot be expressed in one). This is the
   showstopper. (Section 4)
2. **Navmesh poly/tile ceiling** forbids merging the big rooms or the whole cluster
   (3,107 tiles vs 778 proven max). Caps any merge to a couple of small adjacent rooms.
   (Section 2.2)
3. **Dropped-GUID sweep** (absorbing xPTS removes its GUID; every residual reference must be
   remapped or it fails the GUID gate / quest lookup). (Section 6)
4. **No in-game validation of a fused terrain** without a launch - unlike the navmesh, there
   is no static round-trip check that the merged `0x06`/`0x17` is correct.

**Why not to do this:** Track 3's only unique benefit (no cross-level seam) is delivered far
more cheaply by the placement-island fix (Fix B, `CAVE_ENTRY_CHAIN_TRACE.md`) or by Track 2
(interior portal doorways, proven mechanism). Track 3 trades a solved-navmesh problem for an
unsolved-terrain problem. **Shelve it unless Tracks 1+2 both fail and only the R09<->xPTS
seam remains.**

---

## Appendix: probe scripts (session scratchpad, re-runnable, read-only)
- `probe_merge.py` - cluster dims/footprints/entity counts/GUIDs + union bbox + pair union.
- `probe_capacity.py` - SVAERA baked navmesh tile-count distribution (Maze03=778 max),
  cluster donor tile counts (sum 3107), `0x05` local-coord frame, `0x06` head scan.
- `probe_terrain.py` - `0x06`/`0x09` structure for the pair; AE-R09 vs SV-R09 sections;
  poly-load reality (Maze03 loads at 778 tiles); `0x06` portal trailer (return-link GUIDs).
- `probe_terrain2.py` - multi-Records-ref survey (TerrainType paints vs GridSystem terrains);
  `0x06` box-sized grid proof; `0x17` probe; biggest base-game single-level cave footprints.
- `proto_merge_navmesh.py` - **working prototype**: one 62-tile navmesh over the R09+xPTS
  union, round-trip-valid, walkable on both sides of the old seam (44,883 / 71,545 cells).

All run with `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`,
`PYTHONIOENCODING=utf-8`, from the repo root.
