# NAVMESH OVER-COVERAGE RCA (blood cave: walk-through-rocks)

> STATUS: COMPLETE (2026-07-06). All open items resolved; VERDICT + FIX SPEC at the
> bottom. Root cause = `load_tok_mesh` drops the `baseObstacles` polygons; fix =
> subtract obstacle polygons during rasterization (erode-then-carve), gated by a new
> zero-obstacle-overlap gate + the existing engine_corridor_full / seam / entrance
> suite staying green.
> Bug (Will, build18): in the blood cave the player can walk ANYWHERE inside the
> minimap footprint, including through solid rocks. Click-to-move blocking = the
> navmesh, so our offline-generated 0x0b meshes (gen_bc_navmeshes -> gen_rec02)
> are marking rock-occupied ground walkable.

## Measurement 1 - gold-standard reverse diff (OUR R09 donor vs AE Editor-baked R09)

Setup:
- AE-baked 0x0b extracted from `reference_mods/SVAERA_customquest/Resources/Levels.arc`
  Random09A blob: **58,226 bytes, byte-identical to the base-game Steam copy**
  (so it IS the vanilla Editor bake, untouched by SVAERA).
- AE mesh: center=(-883,-1,665) dims=(56,26,56) guids=1, 45,384 walkable cells.
- OUR donor `local/editor_normalized/Random09A.lvl.0b.bin`: center=(6016,24,3278)
  dims=(96,34,96) guids=2, 88,896 walkable cells (raw count, before XZ-column
  dedupe; includes the xPTS neighbour strip and 64u-snap padding).
- Frames differ: OUR is GRID_SHIFT-relocated into the merged blood-cave spot; the
  AE bake sits at the native Silk Road spot. Both grid origins are integer world
  coords, so both share one exact 0.2u lattice -> diff must be done with integer
  cell indices (cx = origin*5 + gx), NOT round(wx/CS) (Python banker's rounding
  on the *.5 cell centers collapses column pairs and fabricates fake stick-shaped
  blobs - first diff attempt was invalidated by exactly that).

FIRST (invalid) pass, kept for the record: naive round() quantization gave
forward coverage 54.3%, 29,708 "excess" cells in 7,912 uniform 15-cell sticks -
all artifacts of the rounding collapse. Redone below with exact lattice math.

RESULT (exact lattice, registration = index-corner-predicted offset, confirmed
sharp by hill-climb: refinement moved it 0 cells; overlap 45,148):

| metric | value |
|---|---|
| OUR walkable XZ columns | 88,896 (incl. xPTS strip + 64u-snap pad) |
| AE walkable XZ columns | 45,384 |
| common | 45,148 |
| forward coverage (OUR covers AE) | **99.5%** (missing only 236 = 0.5%) |
| EXCESS total (OUR walkable, AE not) | **43,748 = 49.2% of OUR** |
| EXCESS inside AE's own 80x80u footprint | **26,397 = 58.2% of AE's own walkable count** |
| EXCESS outside footprint (strip/pad) | 17,351 (legitimate-ish: neighbour strip + snap pad) |

Spatial structure of the inside-footprint excess: **12 contiguous blobs >= 1u^2
cover 100.0% of it** - top blobs are 39.0x31.8u (12,577 cells), 35.8x28.4u
(7,033), 16.2x39.8u (4,484). These are BIG SOLID REGIONS, not edge fringes
(fringe-vs-interior: 93% interior).

(RETRACTED early hypothesis: a first pass suggested excess sits "+17.8u above
the AE floor" = rock tops. WRONG - that offset is the Y FRAME DELTA between the
two maps (SV index corner y=18 vs AE y=0). The ground tok is in fact FLAT:
total height span 0.5u. The excess is at floor height.)

## Measurement 2 - the 0x0a container is SEVEN payloads; we parse only #0

SV R09's 0x0a section (235,263 B) decomposes exactly into:

| # | type | size | content (verified by parsing) |
|---|---|---|---|
| 0 | 1 | 66,841 | guid table + center/dims + **ground tok** (`mesh/mesh3D` 1,435 verts / 2,302 tris + `mappingTo2D` 197 polys + **`baseObstacles` 108 obstacle polygons**) |
| 1 | 2 | 16,622 | `collisionPreprocess` tok, 4-byte shape-index prefix = 0 |
| 2 | 3 | 65,822 | `pathfindPreprocess` tok, shape 0 |
| 3 | 2 | 13,618 | `collisionPreprocess`, shape 1 |
| 4 | 3 | 40,472 | `pathfindPreprocess`, shape 1 |
| 5 | 2 | 9,398 | `collisionPreprocess`, shape 2 |
| 6 | 3 | 22,430 | `pathfindPreprocess`, shape 2 |

`tok_parse.extract_mesh()` reads ONLY payload 0 and `gen_rec02.load_tok_mesh()`
rasterizes ONLY its `mesh3D` - the PathEngine GROUND mesh (the full terrain
surface incl. rock masses), ignoring `baseObstacles` and all six preprocess
payloads. The stray repo-root `test_ground.tok` / `test_collision.tok` /
`test_pathfind.tok` are tiny synthetic samples of exactly these three content
types (element tables match).

AE R09 (SVAERA blob = byte-identical to base game) has NO 0x0a at all - the
Editor bake replaced it with the 0x0b (sections 0x5,0x14,0x6,0xb,0x17).

Obstacle-polygon overlay (108 baseObstacles, position format `face:x,z`
centi-units level-local, vertices = 4-point outline offsets):
- excess covered by obstacle polys: 29.9% (r=0), 38.0% (r=0.4 dilation)
- AE-walkable false-carve rate at r=0.4: 15.1%

## Measurement 3 - eliminating the other candidate carves (all NEGATIVE)

- **userData=1 tris**: only 35 tris / 1,445 cells; overlap with excess = 10
  cells (0.0%); overlap with AE-walkable = 0. Irrelevant either way.
- **Neighbour fill / join ramp / pad**: attribution shows **100.0% of the
  26,397 inside-footprint excess cells are already present in the OWN-tok
  raster** (erode 2, no neighbours). Neighbour-fill added ZERO inside-footprint
  excess on R09. Pipeline stages (2)/(3) exonerated for the interior;
  they only extend coverage outside the footprint (seam strips, by design).
- **Tri connectivity (edgeNConnection)**: every one of the 3,170 geometrically
  shared edges carries exactly one one-sided connection record; 0 shared edges
  are unconnected. The tri graph is FULLY connected - no walls encoded there.
- **mappingTo2D polys**: rasterize to 77,078 cells vs mesh3D's 77,074 - the
  identical region. It is just the 2D projection, no carve.
- **Ground mesh raised terrain**: mesh is flat (0.5u span) and covers only
  ~31% of the level box - the BIG rock masses are already holes in the tok.
  But it covers ~60% more area than the AE bake.

## Measurement 4 - the ASCII overlay map (the picture that resolved it)

Rendering common/excess/obstacles at 1 char = 1u shows:
- baseObstacle polys hug the CORRIDOR EDGES everywhere = they are the
  WALL-BASE / rock outlines lining the walkable channels (PathEngine models
  blocking as obstacle polygons ON TOP of a broader flat ground floor).
- The giant NE excess blob (39x32u) contains NO obstacles at all and connects
  to the corridor system -> under TQIT PathEngine runtime semantics (walkable =
  ground minus expanded obstacles) that region WAS walkable in TQIT.
  => The R09 gold diff carries a CONFOUND: the AE Editor bake reflects AE's
  RE-LAYOUT of this Orient level, while our merged map renders SV's (TQIT-era)
  R09 blob. Part of R09's "excess" is real drift, not over-coverage. R09 is
  therefore a soft gold standard; thresholds must come from the batch check
  below, not from R09 alone.

## Measurement 5 - the blood-cave rooms are FULL of baseObstacles (the smoking gun)

baseObstacles census across the SV cluster 0x0a payloads (all have the same
7-payload structure):

| level | obstacles | tris |
|---|---|---|
| **drxFirstRoom** | **5,318** | 15,465 |
| **drxBC2** | **3,161** | 7,221 |
| river_extension01 | 316 | 3,413 |
| riverextension02 | 240 | 1,468 |
| drxBC_Connector1 | 151 | 1,509 |
| drxBC3 | 116 | 3,719 |
| BC_initialpathway | 112 | 774 |
| Random09A | 108 | 2,302 |
| xPassageTransitionStart | 76 | 1,783 |
| (rest) | 0-68 | ... |

SV authored its rock fields as PathEngine obstacle polygons; the deep rooms
Will is walking through have THOUSANDS of them. `load_tok_mesh()` parses
payload 0 but reads only `mesh3D` - every obstacle is silently dropped, so
every rock footprint rasterizes as walkable floor. **This is the bug.**

No level in either arc ships 0x0a and 0x0b in the same blob, but 905 levels
have SV 0x0a + SVAERA(=AE Editor-baked) 0x0b under the same fname - a batch
validation corpus (small layout drift expected on a few, median tells truth).

## Leads on the source-data question (hypothesis b: sub-mesh selection)

- `tools/tok_parse.py extract_mesh()` parses the 0x0a PTH container as:
  `PTH\x04` + `{type,size,payload}*` but **asserts ptype==1 and reads ONLY the
  first payload**, ignoring anything after `12+psize`. If the container carries
  additional payloads (PathEngine ships ground / collision-carved / pathfind
  variants - note the stray `test_collision.tok`, `test_ground.tok`,
  `test_pathfind.tok` at repo root), we may be rasterizing the UNCARVED ground
  mesh instead of the obstacle-carved pathfind mesh. TO VERIFY: enumerate all
  payload records in R09 + BC-level 0x0a sections; parse each as tok; compare
  areas.
- `gen_rec02.load_tok_mesh` takes `root[0]` -> first `mesh3D` -> verts/tris.
  If one payload's tok stream contains multiple mesh/mesh3D children, same risk.

## Pipeline stages that ADD coverage (hypothesis c candidates)

From `gen_rec02.generate()` (read in full):
1. Own-tok rasterization (tri -> cell, max-y wins).
2. NEIGHBOUR fill: all cluster levels' toks rasterized into the padded grid
   (own-wins; adds floor only where own tok empty).
3. JOIN RAMP: fill cells within RAMP_MAX=15 height units of the own floor get
   blended toward it (BFS depth ~3 cells from the join).
4. erode(2 iterations) SHRINKS (cannot add).
5. Cross-tag area ids: labels only, no coverage change.
So pipeline-added coverage can come only from (2)/(3) - i.e. neighbour toks
painting INTO this level's interior where the own tok deliberately had a hole
(a rock footprint), because own-wins only protects cells the own tok COVERS;
holes get filled by any overlapping neighbour geometry.
NOTE: erode(2) at CS=0.2 removes only a 0.4u rim from every obstacle hole; the
Editor's bake erodes by walkableRadius too, so erode is not the suspect.

## Open items (in order) - ALL RESOLVED (2026-07-06)
1. [DONE] Exact-lattice reverse diff + blob map (redo). -> Measurement 1.
2. [DONE] RAW own-raster vs AE diff (isolates tok vs pipeline). -> Measurement 3
   (stage_decompose): 100.0% of the 26,397 inside-footprint excess is in the OWN
   raster; neighbour/pad add ZERO inside-footprint excess on R09. Pipeline
   exonerated; the excess is the own ground tok.
3. [DONE] 0x0a container payload enumeration (sub-mesh question). -> Measurement 6.
   VERDICT: NO carved sub-mesh exists. The 6 non-ground payloads are PathEngine
   pathfinding-accel structures, not alternate terrain. Fix hypothesis (a) is DEAD.
4. [DONE] Rock overlay vs excess. -> Measurement 2 (obstacle_overlay): the 108 R09
   baseObstacle polys register exactly inside the AE footprint and cover 29.9%
   (r=0) / 38.0% (r=0.4) of R09 excess. (0x05/0x14 decoration entities are the same
   rock fields authored as baseObstacle polys in the tok - the tok obstacles ARE
   the rock overlay; no separate 0x05 pass needed.)
5. [DONE] SV deep-room tok carve check. -> Measurement 7. THE decisive test.
6. [DONE] Fix spec + offline gate. -> VERDICT + FIX SPEC below.

## Measurement 6 - the 6 non-ground payloads decoded (NO carved sub-mesh exists)

Ran `payload_analysis.py` + `stage_decompose.py` on R09's 0x0a. Each preprocess
payload is `<4-byte shape-index><tok stream>` (the analysis first failed because it
did not skip the 4-byte prefix; skipping it, all parse clean). Decoded:

| # | type | first bytes | tag | what it is |
|---|---|---|---|---|
| 0 | 1 | (guid preamble) | `mesh` | GROUND: mesh3D (1435 v / 2302 tris) + mappingTo2D (197 polys, = the 2D projection, 99.5% same cells) + **baseObstacles (108 obstacle polys)** |
| 1 | 2 | `\x00 collisionPreprocess` | shape 0 | agent-collision accel, shape index 0 |
| 2 | 3 | `\x00 pathfindPreprocess`  | shape 0 | A* preprocess, shape 0 |
| 3 | 2 | `\x01 collisionPreprocess` | shape 1 | collision accel, shape 1 |
| 4 | 3 | `\x01 pathfindPreprocess`  | shape 1 | A* preprocess, shape 1 |
| 5 | 2 | `\x02 collisionPreprocess` | shape 2 | collision accel, shape 2 |
| 6 | 3 | `\x02 pathfindPreprocess`  | shape 2 | A* preprocess, shape 2 |

pathfindPreprocess[0] parsed in full (65,818/65,818 bytes, clean):
`pathfindPreprocess{majorVersion=3, meshCheckSum=867394688} -> shape{vertices=8} +
attributes + preprocess{elementCorners(585 corner), graph(1174 source nodes),
silhouetteLookup(200 face -> 58 regionTarget)}`. The `shape` in every preprocess
payload is an 8-vertex agent SILHOUETTE spanning +/-40cm in x/y (the character's
collision cylinder for one of THREE agent sizes = small/medium/large monster) - it
is NOT terrain geometry. `collisionPreprocess` carries the same shape + edge
expansion / circuit / cut records = agent-vs-obstacle collision precompute.

CONCLUSION: there is exactly ONE terrain surface in the container - payload[0]'s
`mesh3D` (the flat ground floor). The 6 others are PathEngine's precomputed
navigation-graph and per-agent collision structures keyed to 3 agent radii. There
is NO obstacle-carved ground mesh to select instead. The ONLY encoding of the rock
walls is `baseObstacles` (obstacle polygons overlaid on the flat ground). This
kills fix hypothesis (a) "rasterize a different/carved payload".

## Measurement 7 - DEEP BLOOD-CAVE ROOM CARVE TEST (the real signal)

R09 is the drift-confounded soft-gold (only 108 obstacles; its AE bake is a
re-layout). The rooms Will walks through carry THOUSANDS of obstacles. Ran
`r09_bc2_carve.py` (carve = rasterize mesh3D, subtract baseObstacle polys via
point-in-poly, erode 2) with `parse_ground`/`stamp_obstacles` in `batch_validate.py`:

| room | obstacles | walkable before | after carve | carved | % of walkable | main-component after |
|---|---|---|---|---|---|---|
| **drxBC2** | 3,161 | 379,797 | 278,936 | 100,861 | **26.6%** | 95.6% (731 frags) |
| **drxFirstRoom** | 5,318 | 893,658 | 635,549 | 258,109 | **28.9%** | 97.5% (1,235 frags) |
| **BC_initialpathway** | 112 | 37,191 | 30,510 | 6,681 | **18.0%** | 99.1% (47 frags) |

DEEP-ROOM MATCH RATE: obstacle carve removes **27-29%** of the over-covered floor
in the deep rooms (drxBC2/drxFirstRoom - the ones full of rocks Will reported
walking through), vs only 18% in the thin corridor BC_initialpathway. That 27-29%
IS the walk-through-rocks excess: dense authored rock fields, each rock a
baseObstacle polygon, all currently rasterized as walkable floor.

Pinch / walk-chain safety (`pinch_analysis.py`, `seam_connect.py`):
- **Every disconnected fragment after carve is an ISOLATED ROCK ISLAND, not a
  corridor piece: touching-main(rim-split) = 0 in all three rooms.** The carve
  removes rock interiors; the walk chain (main component) survives at 95.6-99.1%.
  The 731/1,235 "components" are the insides of individual rocks, correctly newly
  unwalkable - exactly the intent.
- **DOORWAY RISK (must gate):** on BC_initialpathway the main component's corridor
  cross-section (1st-percentile) drops 2.0u -> 0.6u after carve; min = 1 cell both
  before and after. carve-then-erode(2) is more aggressive than erode(2)-then-carve
  (frag counts 47/731/1235 vs 10/62/121; main retention lower). A rock polygon that
  hugs a corridor edge, plus the erode(2) 0.4u rim, CAN pinch a ~1u doorway shut.
  This is why the fix needs the corridor gate below and prefers erode-then-carve.
- W-seam (Will's actual entry: BC_initialpathway <-> xPassageTransitionStart) stays
  in the main component in every carve variant. The extreme N/E/S corner edge cells
  fall off main after carve, but those are thin padded-grid scenery rims, not the
  real area-tagged handoff cells - the authoritative walk-chain gate is
  `engine_corridor_full.py` (which routes through real region-handoff cells), not a
  corner-edge proxy.

---

# VERDICT

**Root cause (confirmed, single):** `gen_rec02.load_tok_mesh()` returns only the
0x0a ground `mesh3D` and DROPS the `baseObstacles` polygons; `generate()` then
rasterizes the full flat ground floor as walkable. SV authored every rock/wall as a
PathEngine `baseObstacle` polygon ON TOP of a broad flat ground tok (PathEngine
runtime = ground MINUS expanded obstacles). Our offline pipeline never subtracts the
obstacles, so every rock footprint becomes walkable - the player walks through solid
rocks. The deep rooms Will hit have 3,161 (drxBC2) and 5,318 (drxFirstRoom)
obstacles; carving them removes 27-29% of the (over-covered) walkable floor. There
is NO carved alternate mesh to load instead (Measurement 6): the only fix is to
subtract the obstacle polygons during rasterization.

Not the cause (ruled out earlier, unchanged): neighbour-fill/join-ramp (0% of
inside-footprint excess), userData tris (10 cells), tri connectivity (fully
connected), mappingTo2D (identical region), raised terrain (mesh is flat, 0.5u),
the tile-lattice snap (a separate seam-stitch fix, orthogonal to over-coverage).

## FIX SPEC (hypothesis b: subtract obstacle polygons during rasterization)

Chosen fix = **(b) subtract baseObstacle polygons**; (a) is impossible (no carved
payload) and (c) reduces to (b). Precise changes, all in `tools/`:

### 1. `tok_parse.py` - return obstacles from the ground tok
Extend `load_tok_mesh()` (or add `load_tok_obstacles()`) to also parse
`mesh.children['baseObstacles']`. Each `<obstacle>` has cstring attrs
`position = 'FACE:x,z'` and `vertices = 'vx0,vz0,vx1,vz1,vx2,vz2,vx3,vz3'`, both in
centi-units level-local (relative to the 0x0a corner). Reference parse (verified in
`batch_validate.parse_ground`):
```
p = [int(n) for n in re.findall(r'-?\d+', ob['attrs']['position'])]   # [face, x, z]
v = [int(n) for n in re.findall(r'-?\d+', ob['attrs']['vertices'])]   # 8 offsets
px, pz = p[1]/100.0, p[2]/100.0
poly = [(px + v[i]/100.0, pz + v[i+1]/100.0) for i in range(0, len(v)-1, 2)]  # 4 pts
```
Return `obstacles` as a list of level-local (x,z) polygons alongside verts/tris.
(Registration proven: the 108 R09 polys land at world x[-922,-859] z[626,703],
exactly inside the AE footprint x[-923,-843] z[625,705].)

### 2. `gen_rec02.py` - carve obstacle cells out of the walkable grid
Signature: `generate(..., obstacles=(), obstacle_erode_r=0.0)`. After the own +
neighbour raster builds `hgrid`, before `erode()`:
```
obs_cells = stamp_obstacles(obstacles, gw, gh, off_x, off_z)   # point-in-poly, level-local
open_cells = erode(set(hgrid), gw, gh, ERODE_CELLS)            # erode FIRST
open_cells -= obs_cells                                         # THEN carve  (erode-then-carve)
```
Use the exact `stamp_obstacles` point-in-poly from `batch_validate.py` (even-odd
rule, per-poly bbox prefilter, r=0). ORDER = **erode-then-carve** (Measurement 7:
fewer fragments, higher main-component retention, less doorway pinch than
carve-then-erode). Do NOT dilate obstacles (r=0): dilation over-carved 15% of AE-
walkable on R09 and buys only +8pt excess removal; erode(2) already trims the 0.4u
walkableRadius rim, matching the Editor bake. Carve only own-level obstacles into
own-level cells (do not carve neighbour strips with this level's obstacles - a
neighbour cell is that neighbour's responsibility and carrying its own obstacles).
Neighbour strips: pass each neighbour's obstacles with its (dx,dz) and carve only
the neighbour-owned (area-tagged) cells, or simplest-safe: carve each donor's own
obstacles only, before the strips are tagged.

### 3. `gen_bc_navmeshes.py` - thread obstacles through
`load_tok_mesh()` at line ~230 is the single chokepoint that drops obstacles today.
Have it also return obstacles; store per entry; pass `obstacles=ent['obstacles']`
into the `generate(...)` call (~line 462). Regenerate all donors
(`py tools/gen_bc_navmeshes.py`), re-inject, re-verify, redeploy.

## OFFLINE GATES (must all pass before deploy)

Add to the donor-generation gate (block the build if any fails):

**G-OVER (new, the over-coverage gate):** for every donor, after generation,
`obstacle_overlap == 0`: NO walkable cell of the final (post-carve, post-erode)
open set may fall inside any of that donor's own baseObstacle polygons (r=0
point-in-poly). Directly asserts "no walkable-on-rock" per donor. Expected nonzero
carve counts per the Measurement-7 table (drxBC2 ~100k cells, drxFirstRoom ~258k)
double as a smoke test that carving actually ran.

**G3 must stay green (`tools/debug/engine_corridor_full.py`):** the walk-chain
levels (Random09A, xPassageTransitionStart, BC_initialpathway,
drxFirstxistion_connection, drxFirstRoom, drxBC2, drxBC_Connector1,
river_extension01, riverextension02, xTempleTransitionHallway) must all stay
~100% reachable from deep Random09A AFTER carve. This is the authoritative
walk-chain check (routes through real area-handoff cells) and the guard against
carve disconnecting a corridor. If any walk-chain level drops below ~99%, a rock
polygon pinched a corridor - loosen that donor (skip carving obstacles narrower
than ~1u, or exclude obstacles whose carve would split the main component).

**Seam-delta + entrance-landing (`seam_delta_check.py`, `entrance_landing_check.py`):**
must stay green - carving must not move the shared-seam floor heights or the
HiddenValley01 GridEntrance landing (BC_initialpathway's entry). Carving only
REMOVES walkable cells, never moves heights, so these should be unaffected; run them
to prove it.

**DOORWAY / NARROW-CORRIDOR RISK (explicit):** obstacle carve + erode(2) can pinch a
~1u doorway shut (BC_initialpathway corridor 1%ile 2.0u -> 0.6u after carve). G3
catches a fully-severed corridor; for a corridor merely NARROWED to sub-agent width
(walkableRadius 0.4u => needs >0.8u clear), add a per-donor corridor-width floor
check on the main component (min surviving corridor >= 4 cells / 0.8u along the walk
chain), or verify in-game at the two tightest necks (BC_initialpathway west tunnel;
drxBC_Connector1). Prefer erode-then-carve to minimize this; if a specific doorway
still pinches, exclude the offending edge-hugging obstacle from the carve for that
donor (the rock is cosmetic there; leaving its footprint walkable is harmless, the
alternative strands the player).
