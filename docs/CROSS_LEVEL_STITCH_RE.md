# How TQAE stitches adjacent levels for seamless walking (no portals) - full RE + the exact fix

Track 1 deliverable, 2026-07-05 night. Disassembly of `backups/game_dll/Engine.dll.original`
(ImageBase 0x10000000; all addresses below are VAs in that image) + byte-level analysis of the
pristine SVAERA map (`reference_mods/SVAERA_customquest/Resources/Levels.arc`) and the deployed
build13 map/donors. Analysis scripts + raw disasm dumps live in the session scratchpad
(`t1_*.py` / `t1_*.txt` in `C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos\
fc31fa12-e2e4-44ef-998c-7fe110587b8c\scratchpad`); the decisive data experiment is
`t1_area_correlation.py` / `t1_overlap_depth.py`.

## 0. Executive verdict

**There is no cross-level "walk-link", no seam linker, and no level-adjacency table. The engine
has exactly TWO path mechanisms: (a) a path inside ONE level's navmesh, and (b) a portal hop.
Seamless overworld walking is mechanism (a): every Editor-baked level navmesh RASTERIZES ITS
NEIGHBORS' GEOMETRY out to ~16 world-units past its own footprint, and TAGS EVERY WALKABLE CELL
with the identity of the level that owns it - the tag is the cell's AREA ID, which is a 1-BASED
INDEX INTO THE NAVMESH'S GUID LIST.** A walk across a seam never leaves the current navmesh; the
polys under the player simply switch tag, the engine resolves the new tag to the neighbor Region,
and hands the entity over. The neighbor's own mesh mirrors the same strip from its side.

**Our generated cluster navmeshes have (build13) single-entry GUID lists, all cells tagged
area 1 (own), and rasterization that stops dead at the level boundary.** The engine therefore has
no data whatsoever connecting Random09A to xPassageTransitionStart: a click past the seam plane
has no navmesh covering both endpoints, no portal exists, so the path request fails at the plane =
the invisible wall. Ten of the eleven attempts (including the 64u lattice snap, which is provably
irrelevant - the per-level meshes are independent objects) never created the one thing the stitch
needs: **cross-boundary walkable cells tagged with the neighbor's GUID-list index, in both meshes
of the pair.**

The fix is entirely in the donor generator (`tools/gen_rec02.py` + `tools/gen_bc_navmeshes.py`):
rasterize each level's own tok PLUS its abutting neighbors' toks (clipped to the level's grid),
erode the union as one field, then tag each walkable cell by footprint containment (own box ->
area 1, neighbor K -> area K+1) with the GUID list `[own, neighbor1, neighbor2, ...]`. No engine
patch, no map-structure change, no portal needed. Section 6 has the exact spec.

## 1. The runtime object model (disasm-proven)

- **Each Level owns a PathFinder** (ctor `0x101f40a0`, called from Level ctor at `0x101b6e42`;
  vtable `0x102f8254`). PathFinder fields (established across ProcessRLTD + ctor + readers):
  - `+0x20 + set*0x4c`: 3 difficulty tilesets; per set: `-0x1c` dtNavMesh*, `-0x14` dtTileCache*,
    `+8` (set base) the live dtNavMeshQuery/mesh used by queries.
  - `+0xec..+0x100`: container center[3] + dims[3] (ints, world units; dims = half-extent + 16
    padding). Mesh-local origin = center - dims.
  - `+0x104/+0x108`: **the navmesh GUID list** (vector of 16-byte GUIDs) - stored, not just gated.
  - `+0x128/+0x12c`: vector<Portal*> - portals REGISTERED INTO this pathfinder by position.
  - `+0x13c/+0x140/+0x144`: dtTileCache callbacks: alloc (vtbl 0x102f8244), FastLZ compressor
    (vtbl 0x102f8234), **mesh-process (vtbl 0x102f59b0)**.
- **ProcessRLTD `0x101f4ba0`** (0x0b loader, `this` = the PathFinder): parses `REC\x02`, copies the
  GUID list into `+0x104` (per GUID it REQUIRES: GUID present in the world map `[mgr+0x70]` AND
  that level's Region RESIDENT in `[mgr+0x50][idx]`, at `0x101f4d0b..0x101f4d2a` - the known
  residency gate), copies center/dims to `+0xec`, then per tileset: **allocates a private
  dtNavMesh (0x48 bytes at `0x101f4fff`, init `0x101080c0`, maxTiles=1000)** + a dtTileCache
  (0x110c at `0x101f4e6b`, init `0x101004c0` with the alloc/compressor/meshproc from
  `+0x13c/140/144`), adds each compressed tile (`dtTileCache::addTile 0x101002b0`) and builds it
  (`buildNavMeshTile 0x100ff4d0` via `getTilesAt 0x10100440`).
  **=> Every level, every difficulty, is a SEPARATE dtNavMesh instance with a level-local origin.
  Detour never sees two levels in one mesh. Cross-level tile lattice alignment is meaningless.**

## 2. The per-poly region tag: area id == 1-based GUID-list index

- The engine's `dtTileCacheMeshProcess::process` impl (vtbl `0x102f59b0` slot 1 = `0x10105a90`,
  virtual-called from buildNavMeshTile at `0x100ff918`) is an identity copy:
  `for i < npolys: polyFlags[i] = (u16)polyAreas[i]`. **Poly flags = the rasterized cell AREA ID.**
- **Resolution, position -> Region** (`0x101f0cf0`, 10 call sites incl. the FindPath wrappers
  `0x101f28b7/0x101f29e8` and the movement/entity updates `0x101fa641/0x101fa8f8/0x101fad81`):
  `dtNavMeshQuery::findNearestPoly(pos, ext=(2,2,2))` (`0x1010ba00`) -> decode polyRef -> read the
  poly's **flags word at poly+0x1c** (standard 32-byte dtPoly, flags at +28) -> `idx = flags - 1`
  -> **`0x101f0c90`: Region = liveRegionArray[ guidMap[ GUIDlist[idx] ] ]**
  (`[mgr+0x70]` map lookup + `[mgr+0x50]` live array, mgr global `0x103743f0`). Out-of-range idx
  returns NULL. The position is then re-based into the resolved region's frame using
  `region+0x2c/0x30/0x34` (the region's world origin ints).
- So the engine's answer to "which level is this spot in?" comes ENTIRELY from the poly tag of
  whatever navmesh serves the query - this is the handoff/bookkeeping backbone.
- Note `flags=0` would also be invisible to queries (default dtQueryFilter excludes flags==0), so
  walkable cells MUST carry area >= 1 regardless.

### The vanilla data proof (100% correlation)

`t1_area_correlation.py` decodes real Editor-baked `0x0b` sections from the pristine SVAERA map
and tests the prediction "cells with area K lie inside the footprint box of GUID[K-1]":

| level | GUID count | cells | area histogram | prediction hit-rate |
|---|---|---|---|---|
| HiddenValley01 | 7 | 119,178 | {1: 99442, 2: 13534, 5: 6202} | 100% / 100% / 100% |
| Valley01 | 8 | 331,236 | {1..8, bulk=area 4} | 98-100% every area |
| Valley01B | 7 | 124,431 | {1: 7842, 2: 113203, 7: 3386} | 100% x3 |
| ValleyDescent01 | 8 | 170,536 | {1..8, bulk=area 6} | 98-100% every area |
| HighAltituedBorder01 | 3 | 901 | {1: 901} | 100% |

- Area K maps onto GUID[K-1]'s box essentially perfectly (residue = cells straddling box edges).
- **GUID[0] is NOT necessarily the own level**: Valley01's own GUID sits at index 3 (its bulk
  cells are area 4); ValleyDescent01's own at index 5 (bulk = area 6). The old doctrine in
  `tools/rec02_format.py` ("own level GUID FIRST") and "areas 1..6 = walkable classes" is WRONG -
  the list order is arbitrary (Editor contributor order) and the area id is pure region ownership.
- **HighAltituedBorder01's entire mesh is one 901-cell strip tagged as HiddenValley01** (GUID[0]),
  zero own-tagged cells - a vanilla mesh that exists purely to mirror a neighbor's seam strip.
- Reciprocity at a working seam (`t1_overlap_depth.py`, HiddenValley01 | HiddenValleyborder01,
  boundary x=-6): HV01 carries 13,534 cells tagged border01 penetrating 0..15u EAST of the plane;
  border01 carries 6,373 cells tagged HV01 penetrating 0..15u WEST of it. **Both meshes cover the
  same seam band, each tagging every cell with its true owner.** Strip depth is bounded by the
  16u padding (`dims = half-extent + 16`).

## 3. How a path is actually found (and why seams need no portal)

`PathManager::FindPath` (`0x101ee910`) - the only dispatcher:
1. Collect the pathfinders COVERING the start (`0x101ec920`) and the end. "Covers" =
   `0x101f2490`: convert the location into pf-local coords and `findNearestPoly` with extents
   **(2,2,2)** - i.e. the pf's own dtNavMesh must have a walkable poly within 2u.
2. Double loop over (startPF, endPF) pairs (`0x101eea80`):
   - **startPF == endPF** (`0x101eea8c`) -> `PathFinder::FindPath 0x101f2a00` = a normal Detour
     path inside that ONE mesh. Start/end each arrive as (Region*, region-local pos) and are
     re-based via region origins into the pf frame (`0x101f2aa9..0x101f2b8x`).
   - **startPF != endPF** (`0x101eebc3`) -> `0x101f3680`: iterate the START pf's registered
     portal list (`pf+0x128`), per portal require open (`+0xfc`), dest region resident+alive,
     **dest `Level+0x6a48` navmesh-loaded (`0x101f37ff`)**, paired portal open (`0x1020dfd0` /
     `0x101f3854`) - then path to the portal and continue on the other side. Portals get into
     `pf+0x128` by POSITION: PathManager (`0x101ee610` on portal spawn, `0x101ee3e0` on pf
     registration) pushes every portal into every pathfinder whose mesh covers its coords.
3. Best-scoring candidate wins.

**A vanilla seam crossing is the startPF==endPF case.** Player in A near the seam, click a few
units into B: A's mesh has walkable polys up to ~15u past the plane (the strip), so A's pf covers
BOTH endpoints -> a single-mesh path crosses the plane. As the entity walks, the per-step position
resolution (Section 2 consumers) sees the poly tag flip to B's GUID index -> the entity's region
flips to B -> subsequent queries run on B's pf (whose mesh mirrors the band). Chains level to
level indefinitely. No portals, no links, no lattice constraint, no footprint-abutment check in
the WALK path. (Footprint adjacency matters ONLY for streaming co-residency - which the Frida
sweeps already proved works for our cluster - and for the ProcessRLTD residency gate.)

## 4. The exact gap in our cluster (byte-proven, deployed map)

Deployed build13 donors (`local/editor_normalized/*.0b.bin`, byte-identical in the deployed
`CustomMaps/.../Levels.arc` per `verify_merged_bc_navmeshes.py` + the build13 log):

| mesh | GUID list | area histogram | cells past the seam plane |
|---|---|---|---|
| Random09A | [own d840e7ae] | {1: 88,896} | 0 (raster stops at x=5979) |
| xPassageTransitionStart | [own 2d2acbf5] | {1: 126,727} | 0 |
| BC_initialpathway | [own e39fcb11] | {1: 114,953} | 0 |

vs the vanilla pattern (Section 2): multi-GUID list + own-tagged bulk + neighbor-tagged strips
0..15u past each shared plane, mirrored on both sides.

So at the R09 | xPTS seam (plane x=5979, ~80u shared z-band) the deployed build has:
- NO poly in either mesh on the far side of the plane (=> no pathfinder covers both endpoints of
  any click that crosses; the end snaps back to the plane within the 2u fuzz, or no pf qualifies),
- NO portal between the two regions (only the HV01<->R09 mouth pair exists - Frida-confirmed),
- NO neighbor entry in either GUID list (=> even standing ON the plane, no poly can ever resolve
  to the other region - the handoff has no data).
Result: click-to-move walks you to the plane and refuses to cross. Exactly the reported wall.

Historical donor states all miss the same thing (`deployed_0b/` snapshot + build logs):
- builds ~1-9 (multi-GUID, all cells area 2): with `[own, neighbor]` lists, EVERY poly tagged
  index 1 = the NEIGHBOR - the whole level claims to be the other level (bookkeeping garbage),
  and still zero cross-plane cells.
- "mutual cross-list" era (e.g. 15:45 snapshot): `[own, neighbor]` + all cells area 1 - correct
  own-tagging, still zero cross-plane cells, so nothing to cross onto.
- "area-id 1" and "gate-free/own-GUID" and build13 lattice-snap: single-GUID + area 1 - self-
  consistent, still zero cross-registration.
- The 64u lattice snap chased tile-grid alignment BETWEEN meshes; Section 1 proves the meshes are
  separate dtNavMesh instances - there is no cross-mesh tile math anywhere. 24/24 aligned seams
  and still walled is exactly what the mechanism predicts.
- NAVMESH_COVERAGE_FIX.md's "the linker keys on INDEX-footprint adjacency; a 2u gap blocks the
  link" is likewise corrected: there is no such linker; index footprints gate streaming, not
  walking. (The 2u-gap fix was still harmless/correct as metadata hygiene.)

## 5. Why every other observed behavior fits

- The cave MOUTH works: it is a portal (GridEntrance binding), handled by `0x101f3680`; it needs
  only portal-open + dest resident + dest navmeshOK=1 (all Frida-verified true).
- Walking INSIDE each cluster level works in every build: same-pf single-mesh paths; the region
  resolution is not needed to move within one region (and NULL/garbage resolution does not block
  it).
- Overworld levels walk seamlessly with `portals A(+0x8c)=cave-mouths-only, B empty`: Section 3.
- 1963/2235 SVAERA levels carry 2..13 GUIDs; "base game uses area 2 heavily": those are the
  neighbor strips (first neighbor = index 2) - not a "walkable class".
- The ProcessRLTD residency gate passed for 2-GUID cluster donors in live play (build12 Frida log:
  `random09a navmeshOK=1` in every sweep with xPTS co-resident) - the cluster co-streams, so
  multi-GUID lists are safe here.

## 6. THE FIX (concrete, minimal, generator-only)

Goal per abutting cluster pair (A, B), e.g. Random09A | xPassageTransitionStart,
xPTS | BC_initialpathway, and every other seam in the chain (39 listed pairs):

1. **GUID lists**: A's donor lists `[ownA, B(, other abutting contributors)]`; B's lists
   `[ownB, A(, ...)]`. (Order arbitrary per vanilla; keep own first so area 1 = own. For the
   blob-swapped Random09A keep the existing `OWN_GUID_OVERRIDE` AE GUID `d840e7ae...` - both as
   its own entry and as the neighbor entry inside xPTS's list.)
2. **Union rasterization**: rasterize A's own tok PLUS each listed neighbor's tok (all toks are in
   one shared SV world frame; the uniform GRID_SHIFT applies to all, so they can be rasterized
   into A's grid directly), clipped to A's mesh grid (origin = snapped `center - dims`, span
   `2*dims` - the padded box; the build13 snap-expanded grids already cover 16..63u past each
   edge, so capacity exists). **Erode the union as ONE field** (2 cells, as now) - never erode
   each level separately or the seam line itself gets notched from both sides.
3. **Tagging**: after erosion, every walkable cell's area id = 1 + index-in-A's-GUID-list of the
   level whose (merged-frame, half-open `[x0,x1) x [z0,z1)`) footprint box contains the cell
   center. Own box -> 1, first neighbor -> 2, etc. If any cell lands in a level NOT yet listed
   (diagonal corner spill), ADD that level to the GUID list and tag accordingly (vanilla lists
   include diagonals); a cell inside no cluster/own box (shouldn't happen inside the padded box)
   -> drop it (area 0).
4. **cons planes**: compute from the merged walkable field exactly as today (area boundaries do
   NOT affect cons; different-area cells become separate polys that share edges, which is the
   vanilla shape).
5. Everything else unchanged: 3 identical difficulty sets, FastLZ, lattice snap (harmless),
   verbatim `pre_positioned=True` injection in `svaera_plus_portals.py`, freshness gate (reads
   only the corner).

### Code changes

- `tools/gen_rec02.py` - `generate()` currently rasterizes ONE tok and stamps a constant area.
  Change signature to accept contributions: `generate(main_tok_path, neighbors=[(tok_path,
  world_shift, guid_index), ...])` (or a prebuilt list of (tris, tag)); rasterize all into the one
  grid; erode the union; assign per-cell area by the containment rule (pass in the level-box
  table + guid order); slice tiles as now. The constant `AREA = 1`/`2` stamp is deleted.
- `tools/gen_bc_navmeshes.py` - per level:
  - compute abutting neighbors from the SHIFTED LEVELS footprints (corner + box-dims*2 edge-share
    with >0 shared span; the merged-frame table already exists in the merge script);
  - build the GUID list `[own] + neighbors` AFTER `resolve_guids` remapping (R09 keeps
    `OWN_GUID_OVERRIDE`; xPTS's neighbor entry for R09 must be the AE GUID). HARD-FAIL (do not
    silently drop) if a contributing neighbor's GUID cannot resolve;
  - pass each neighbor's pristine upstream tok (same source as its own donor) into `generate()`;
  - self-verify per donor: (i) parse-back round-trip as now; (ii) `max(area) <= guid_count`;
    (iii) for every listed seam neighbor, the donor has >= 50 cells tagged with that neighbor's
    index AND those cells sit beyond the shared plane; (iv) all GUIDs resolve in the merged world.
- Add a merged-map gate (extend `verify_merged_bc_navmeshes.py` or the seam checker): for each of
  the 39 seam pairs, BOTH deployed meshes contain >= 50 walkable cells tagged as the other level
  within the shared band mod nothing (plain world-box test) - this is the anti-regression check
  that all 11 prior builds would have failed.
- `tools/svaera_plus_portals.py`: **no change required** for the stitch itself.

### Risks / watch-items (ranked)

1. **Load-order residency**: with `[own, xPTS]` in R09's list, R09's navmesh load (mouth-portal
   preload) requires xPTS resident at that instant. Empirically fine (build11/12 logs: R09
   navmeshOK=1 in every sweep; grid streaming brings the cluster in together), but if the mouth
   ever walls again with multi-GUID donors, THIS is the suspect: check `Level+0x6a48` on R09 via
   the frida kit. Mitigations if it ever bites: retry-friendly ordering (list xPTS in R09 only,
   generate R09's strip inside xPTS's mesh deeper), or a tiny always-resident anchor. Do not
   pre-optimize; test first.
2. **Height agreement at the seam**: both toks are cuts of one continuous SV mesh, so heights
   agree; the self-verify (iii) should also assert |dy| <= 1 cell across the plane band.
3. **Erosion at the strip's far edge** is expected and harmless (the neighbor's own mesh owns that
   interior); what matters is continuity ACROSS the plane, which the union erosion guarantees.
4. GUID-count bound: vanilla max observed 13; our worst level has < 8 abutting contributors. Poly
   flags are u16; area ids up to 14 are fine.

## 7. Corrections to prior docs (do not re-learn the old way)

- `tools/rec02_format.py` docstring: "GUIDs = own level FIRST + neighbors" -> own is NOT
  necessarily first; "areas 1..6 walkable classes" -> **areas = 1-based GUID-list index of the
  cell's owning level; 0 = unwalkable**.
- `docs/MODDING_PLAYBOOK.md` Section 2a (grid-seam recipe): "abutting footprints + walkable bands
  overlapping across the seam" is INSUFFICIENT - both meshes must RASTERIZE PAST the seam and TAG
  the strip with the neighbor's GUID index (this doc, Section 6).
- `docs/NAVMESH_COVERAGE_FIX.md` Section 1: the "cross-region walk-link keyed on index-footprint
  adjacency" mechanism claim is wrong (no such linker exists); the 2u index-gap fix stays as
  harmless metadata hygiene.
- `docs/CAVE_ENTRY_CHAIN_TRACE.md` remains correct about the portal path + residency gate; its
  Fix A/B analysis is superseded by this doc for the seam question.

## 8. Confidence

- Mechanism (per-level meshes; area=GUID-index tagging; same-pf vs portal dispatch; coverage =
  findNearestPoly(2,2,2)): **HIGH** - complete disassembly chain (Sections 1-3, all VAs cited)
  plus a 100%-hit-rate prediction test on ~750k vanilla cells across 5 levels and reciprocal
  strip measurements at a working seam, and it post-dicts all 11 failures and every runtime
  observation without exceptions.
- That the deployed cluster lacks exactly the cross-tagged strips + neighbor GUID entries:
  **CERTAIN** (byte-verified donors == deployed sections).
- That the Section 6 generator fix opens the seam in-game: **HIGH but only a walk test proves it**
  (project discipline). The one identified residual risk is the load-order residency note
  (watch-item 1), with a ready diagnostic.
