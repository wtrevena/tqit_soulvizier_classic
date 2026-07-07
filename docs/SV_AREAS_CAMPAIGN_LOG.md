# SV AREAS CAMPAIGN LOG - generalizing the blood-cave navmesh fix to every SV area

> Running checkpoint log for the Fable-time-boxed campaign that ports the proven
> blood-cave navmesh/entrance recipe to the remaining SV-only areas. Written
> continuously so nothing is lost. Companion docs: `SV_AREAS_CAMPAIGN_PLAN.md`
> (the per-area plan), `AREA_WIRING_RECIPE.md` (the blood-cave recipe), and
> `NAVMESH_OVERCOVERAGE_RCA.md` (obstacle carving).
>
> Baseline: build22 (commit `54e81a4`). `local/Levels_merged.arc` = 685,652,028 B,
> coupled `Quests.arc` 187,708 B. Python:
> `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`
> (`PYTHONIOENCODING=utf-8`).

---

## PART 0 - GENERALIZATION PROOF (blood-cave byte-identity) - DONE, PASS

**Goal (from the brief):** generalize `tools/gen_bc_navmeshes.py` (blood-cave-
hardcoded: `BC_TOKEN='xbloodcave'`, `R09_KEY`, `OWN_GUID_OVERRIDE`, `_root_rank`
pinned to `random09a.lvl`) into a per-area cluster config WITHOUT changing the
blood-cave output - then regenerate the blood-cave donors and prove them
byte-identical to the committed ones. That byte-identity is the no-regression
proof that must hold before any new area is generated.

### What changed in `tools/gen_bc_navmeshes.py`

Added a `ClusterConfig` dataclass + a `CLUSTERS` registry, and extracted the whole
former `main()` body into `run_cluster(cfg, dry_run)`. The four hardcoded
blood-cave values now come from `cfg`:

| Former hardcode | Now |
|-----------------|-----|
| `BC_TOKEN = 'xbloodcave'` | `cfg.tokens` (substring set matched against the SV level path) |
| `R09_KEY` appended + `sv_r09` | `cfg.extra_level_keys` (de-duped against the token match) |
| `OWN_GUID_OVERRIDE = {R09_KEY: AE_R09_GUID}` | `cfg.own_guid_override_keys` (each resolved to its SVAERA GUID at run time) |
| `_root_rank`: `bn == 'random09a.lvl'` | `cfg.anchor_key` (compared on the full path key) |
| hard anchor assert on `_r09_bn` | asserts on the anchor level derived from `cfg.anchor_key` |

`main()` is now a CLI dispatch: default `bloodcave`; `--cluster <name>` for one
area; `--cluster all` for every registered cluster; `--dry-run` unchanged.

The blood-cave config reproduces the prior behaviour exactly:
```python
R09_KEY = 'levels/world/orient/underground/random09a.lvl'
BLOODCAVE = ClusterConfig(
    name='bloodcave', tokens=('xbloodcave',),
    extra_level_keys=(R09_KEY,), own_guid_override_keys=(R09_KEY,),
    anchor_key=R09_KEY)
```

No code imports symbols from `gen_bc_navmeshes` (verified: all references in other
tools are comments/docstrings), so the refactor is internal to a CLI driver.

### Byte-identity proof (verbatim)

1. Snapshotted the 24 committed donors from `local/editor_normalized/` and computed
   their SHA256s (baseline).
2. Regenerated the blood cave with the CURRENT (pre-refactor) committed script into
   a temp dir -> **all 24 byte-identical to the on-disk donors** (proves the on-disk
   donors match HEAD and the pipeline is deterministic).
3. Applied the generalization refactor. Regenerated the blood cave again
   (`py tools/gen_bc_navmeshes.py`, default cluster) into a fresh temp dir.
4. Compared to the baseline:

```
=== BYTE-IDENTITY PROOF: refactored blood-cave donors vs pre-refactor baseline ===
compared: 24
RESULT: ALL 24 DONORS BYTE-IDENTICAL -- generalization is a proven no-op on blood-cave output
--- sha256 cross-check (aggregate of sorted per-donor sha256) ---
36a609bfe57e62423433c8958750dbe0666609ef54b3c5231472b0a53830d7c4   (refactored)
36a609bfe57e62423433c8958750dbe0666609ef54b3c5231472b0a53830d7c4   (baseline)
```

Generation summary (unchanged): 24 generated, 7 no-0x0a (ocean scenery), 31 total
xBloodCave levels; anchor Random09A shift=0; Y-ALIGN 25 constant seam offsets, 4
levels shifted (+3 each), max |shift|=3u.

### Blood-cave gate baseline (must stay green after every new area) - all PASS

- **G2 entrance landing** (`entrance_landing_check.py --check-merged`):
  DONOR 508 cells in landing box, median Y=19.00, dY vs fixed landing +0.00u, all
  within 2u -> PASS; MERGED injected R09 0x0b identical -> PASS. `G2: PASS`.
- **G3 corridor** (`engine_corridor_full.py`): every walk-chain level reachable from
  deep Random09A: BC_initialpathway 100%, Random09A 99%, drxBC2 99%, drxBC_Connector1
  100%, drxFirstRoom 99%, drxFirstxistion_connection 100%, river_extension01 100%,
  riverextension02 100%, xPassageTransitionStart 100%, xTempleTransitionHallway 100%.
  Finale-behind-boss-door component + ocean scenery read 0% by design (frontier).
- **G4 seams** (`seam_delta_check.py`): worst median |dY| across chain seams = 0.00u
  (PASS <= 0.5u).

These three gates + `verify_merged_bc_navmeshes.py` (24/24) + byte-identical donors
constitute the "blood-cave suite still green" regression check re-run after each wave.

---

## WAVE 1 - single-level navmesh generation (Uber Dungeon, Boss Arena, Garden of Merchants, Sparta Crypt L2) - PASSED

**Scope:** generate real `0x0b` navmeshes for the 4 single-level, isolated-island,
no-internal-seam areas (the lowest-risk generation case) and inject them into the
merged map. NO entrance work (that is Wave 2/4/5) - these are walkable interiors
with no way in yet, a fine intermediate state. Cold Tombs deferred (Wave 6: no
`0x0a`, confirmed below).

### What changed (files)

- `tools/gen_bc_navmeshes.py` - added 4 single-level `ClusterConfig`s + registry
  entries (`uberdungeon`, `bossarena`, `gardenofmerchants`, `spartacryptl2`). Each:
  `tokens=('/<basename>.lvl',)`, no extras, no GUID override, `anchor_key` = the
  level's own SV path (asserted shift==0). No GRID_SHIFT (all sit at SV-original,
  already-disjoint positions - confirmed: merged footprint == SV footprint for all 4).
- `tools/debug/area_selfcheck.py` - NEW single-level gate (the G3/G4-degenerate +
  G-OVER check the plan calls for): round-trip validity, own-floor coverage,
  G-OVER (walk-on-rock), main-component fraction, GUID resolution. Parameterized by
  `--level`; `--check-merged` also gates the injected copy byte-exact.
- `tools/verify_merged_bc_navmeshes.py` - scope fix: the pass/fail count now counts
  only IN-SCOPE (blood-cave) donors, so other areas' donors in the shared donor dir
  no longer make the blood-cave gate miscount (was `24/28 FAIL`, now `24/24 PASS`).
- `local/editor_normalized/` - 4 new donors: `crypt_floor1.lvl.0b.bin` (320,324 B),
  `boss_arena.lvl.0b.bin` (474,110 B), `GardenofMerchants.lvl.0b.bin` (567,335 B),
  `SpartaCryptLevel2.lvl.0b.bin` (75,506 B).
- `local/Levels_merged.arc` - rebuilt with 28 donors injected (24 BC + 4 new):
  **686,012,299 B** (build22 was 685,652,028 B; +360,271 B). `Quests.arc` UNCHANGED
  (no quest/content change this wave). build22 map preserved at
  `local/Levels_merged_build22.arc` for rollback/diff.

### Ground-truth (upstream SV geometry, verified 2026-07-07)

All 4 have `0x0a` with exactly ONE GUID (their own, resolves in merged) = pure
isolated single-level, no neighbours, no cross-tags, no seams:

| Level | verts | tris | obstacles | merged fp == SV fp |
|-------|------:|-----:|----------:|:---:|
| crypt_floor1 | 8403 | 14890 | 36 | yes (no shift) |
| boss_arena | 360 | 591 | 13 | yes (no shift) |
| gardenofmerchants | 766 | 906 | 356 | yes (no shift) |
| spartacryptlevel2 | 1570 | 2746 | 39 | yes (no shift) |
| coldtombs | (no 0x0a) | - | - | Wave 6, correctly stubbed |

### Gate outputs (verbatim)

Donor generation (all: guids=1, nbrs=0, anchor shift=0, areas={1:...} only):
```
GEN crypt_floor1.lvl       320324 B tiles=203 guids=1 nbrs=0 carve=3318/454487(0.7% obs=36)  areas={1:451169}
GEN boss_arena.lvl         474110 B tiles=437 guids=1 nbrs=0 carve=157312/1630729(9.6% obs=13) areas={1:1473417}
GEN GardenofMerchants.lvl  567335 B tiles=440 guids=1 nbrs=0 carve=131110/1586195(8.3% obs=356) areas={1:1455085}
GEN SpartaCryptLevel2.lvl   75506 B tiles=42  guids=1 nbrs=0 carve=3399/78647(4.3% obs=39)   areas={1:75248}
```

Area self-check (`area_selfcheck.py --level <lvl> --check-merged`), donor + merged
copy both, all PASS. Merged 0x0b bytes == donor for all 4 (byte-exact injection):

| Level | own-floor coverage | G-OVER walk-on-rock | main component | merged==donor |
|-------|-------------------:|--------------------:|---------------:|:---:|
| crypt_floor1 | 99.3% (451169/454487) | 0 (0.0000%) | 100.0% (1 comp) | 320324 B == |
| boss_arena | 90.4% (1473417/1630729) | 50 (0.0034%) | 93.8% (2 comps) | 474110 B == |
| gardenofmerchants | 91.7% (1455085/1586195) | 9 (0.0006%) | 91.8% (34 comps) | 567335 B == |
| spartacryptlevel2 | 95.7% (75248/78647) | 0 (0.0000%) | 100.0% (2 comps) | 75506 B == |

> The nonzero G-OVER on boss_arena (50) / gardenofmerchants (9) is EXPECTED and
> RCA-sanctioned: the carve itself leaves ZERO walk-on-rock (verified: `open&obs
> BEFORE repair = 0`), then the connectivity-repair restores exactly those cells to
> bridge a room piece the carve split off (boss_arena: a 99,945-cell fragment
> reconnected via a 50-cell = ~1.4u doorway through a cosmetic rock). Fraction
> 0.0034% << the 0.50% gate; a real carve failure would be ~9% (the pre-carve obs
> fraction). gardenofmerchants' 34 components are the rock-field garden nooks; the
> main hub is 91.8%.

Collateral (`collateral_diff.py build22 vs wave1`):
```
CHANGED BLOBS: 4
  boss_arena.lvl          811839 ->  1285801 B  (delta +473962)
  spartacryptlevel2.lvl    10613 ->    85971 B  (delta  +75358)
  gardenofmerchants.lvl  1940239 ->  2507426 B  (delta +567187)
  crypt_floor1.lvl         66683 ->   386859 B  (delta +320176)
```
EXACTLY the 4 intended level blobs changed (148-byte stub -> real navmesh); ZERO
other levels, no shared level, no blood-cave level touched.

verify_merged_bc_navmeshes (blood cave, new map): `24/24 in scope, PASS`.

Blood-cave suite still green (regression): G2 entrance `--check-merged` PASS (donor
+ merged both 508 cells, dY +0.00u); 24/24 blood-cave donors byte-identical to the
pre-campaign baseline (`36a609bf...` aggregate).

### What the main session should deploy for Wave 1

- `local/Levels_merged.arc` (686,012,299 B) - deploy to CustomMaps (map-data only,
  `-SyncLevels`). `Quests.arc` unchanged - no need to rebuild/redeploy it for Wave 1.
- Commit the 4 new donors + the 3 tool changes. Suggested tag: `build23-wave1-navmesh`.
- **In-game caveat:** these 4 interiors are now WALKABLE but still have NO ENTRANCE
  (Uber Dungeon + Boss Arena entrances arrive in Wave 2 via the maze03 patch;
  Garden in Wave 4; Sparta Crypt L2 in Wave 5 if it pans out). A walk test cannot
  reach them yet by normal play - this wave is bankable as "interiors ready" so the
  entrance waves land on already-meshed floors. (If Will wants to spot-check an
  interior now, a temporary devmap teleport / noclip into e.g. crypt_floor1 would
  confirm the floor is solid, but that is optional.)

---

## WAVE 2 - Uber Dungeon + Boss Arena entrances via maze03 - SKIPPED (ungateable offline; true mechanism documented)

**Verdict:** SKIP the entrance restoration. The Wave-1 interiors (crypt_floor1,
boss_arena navmeshes) are banked and their return/landing sides are proven on-mesh;
the ONE missing piece is the maze03 entrance portal, but restoring it is NOT the
plan's assumed "transfer the lost SV portal record" - it is an unrehearsed
quest-driven `GridEntranceDynamic` chain that (a) the plan's naive coordinate
transfer cannot satisfy and (b) no offline gate can certify. Documented in full for
a future attempt with an in-game test in the loop. No map change shipped this wave.

### The true entrance mechanism (fully reverse-engineered this wave)

The maze03 -> uber-dungeon -> boss-arena entrance is a **quest-opened dynamic grid
entrance**, not a static native cave mouth like the blood cave:

1. `records\quests\portal_olympianarena1.dbr` = Class **`GridEntranceDynamic`**
   (template `GridEntranceDynamic.tpl`). In SV it is placed in maze03 (0x05 instance,
   flags=0, identity rotation, SV-local (101.84, 1.00, 144.52)) with a 48-byte
   `0x14` GridEntranceDynamic binding: `[mouth_uid 58941143..][exit_uid 6e513e90..]
   [dest_guid dbc245c358434e0b.. = crypt_floor1]`.
2. `records\quests\portal_olympianarena2.dbr` = Class **`GridExitOneWay`** = the
   landing/return side, placed in crypt_floor1 (0x14[192], mouth_uid 6e513e90.. -
   pairs maze03's exit_uid) and in boss_arena (0x14[28]/[29]).
3. The ported **`bossarena.qst`** (loads in-window since build22) drives it: a
   `Condition_OnLevelLoad` trigger fires `Action_ShowNpc` + **`Action_OpenDynGridEntrance`**
   (`dynGridEntranceName = portal_olympianarena1.dbr`) + `Action_UnlockFixedItem`.
   So the entrance is OPENED BY THE QUEST when maze03 loads - the portal object must
   exist in maze03's map data for the quest to find and open it.

### Why the plan's approach does not work (proven, not assumed)

- **AE maze03 lacks the portal entirely**: `0x14: 0 records`, no `portal_olympianarena1`
  string/instance (byte-confirmed). It is v0x0f (SV's is v0x0e), 447 instances vs SV's
  914 - a WHOLESALE RE-AUTHORED layout, not a patched copy.
- **SV's portal coordinates do not map to AE maze03's walkable floor.** SV and AE
  maze03 sit at DIFFERENT grid corners (delta AE-SV = (-1336,0,+258)) AND have
  different geometry. AE maze03's navmesh occupies only world X[-7870,-7526]
  Z[-3833,-3380]. SV's portal maps to:
  - same-LOCAL -> AE world (-7974,-3798): **169.5u off the nearest AE walkable cell**
    (and outside the walkable X range).
  - same-WORLD -> (-6638,-4056): **918u off**.
  Neither lands anywhere near AE maze03's mesh. There is no SV-faithful coordinate to
  restore; the portal would have to be HAND-PLACED on AE's re-authored geometry.
- **No AERA-native alternative exists**: SVAERA does not even contain crypt_floor1 or
  boss_arena (both are SV-only levels the merge appends), and NO level in the merged
  map binds their GUIDs via any 0x14/0x06 (scanned all 2282 levels). The only path in
  is the quest-DynGridEntrance above.

### What IS ready (verified on the merged map this wave)

- crypt_floor1 `portal_olympianarena2` landing (SV-local 139.9,10.0,231.9):
  **ON-MESH, nearest cell 0.00u, dY +0.00** (the Wave-1 crypt_floor1 navmesh lands the
  player perfectly). `portal_uberdungeon_return` NPC also ON-MESH (0.14u).
- boss_arena `portal_olympianarena2` + `volume_startolympianarena`: ON-MESH (0.10-0.14u).
- A portal placed at AE maze03's walkable CENTROID (local ~401,334) WOULD be on the AE
  navmesh - so hand-placement is geometrically feasible.

### Why this is a SKIP, not a fixable gate failure

The deliverable is **fundamentally ungateable offline**. Building the patch (append the
`portal_olympianarena1` instance + its 48-byte `0x14` GridEntranceDynamic binding to AE
maze03) is mechanically straightforward - I have the exact bytes and the INJECT_SPECS
machinery handles a flags=0 instance. But three things can only be settled by an in-game
test, and shipping a guess risks the exact "injected-but-untested = wasted deploy cycle"
the plan warns against:

1. **Placement is a blind level-design guess.** SV placed the portal at a meaningful spot
   in SV's maze; AE's maze is a different layout. The walkable centroid is an arbitrary
   corridor cell - the player may never walk there, and a portal floating mid-corridor is
   nonsensical. Choosing the RIGHT AE spot needs eyes in the level.
2. **The GridEntranceDynamic + Action_OpenDynGridEntrance + GridExitOneWay chain is
   unrehearsed** in this mod (the recipe itself flags the GridEntrance-binding append as
   "the only piece not yet built"). Appending a `0x14` GridEntranceDynamic binding to a
   v0x0f AE level, opened by a quest, transitioning to an SV-only appended level, is three
   untested mechanisms in series. None is offline-verifiable.
3. **Whether AE maze03 is even on the player's path** in AERA progression is unknown - if
   it is off-path, the OnLevelLoad quest trigger may rarely/never fire.

The campaign discipline (bank low-risk wins; do not let a hard wave produce an
uncertifiable deploy; skip with documentation after fix attempts are exhausted) makes
this a SKIP. The research above IS the deliverable: it converts a future attempt from
"guess and hope" into "hand-place the portal at a chosen AE maze03 walkable cell, append
the known 48-byte binding, deploy, and walk-test" - a single focused in-game validation.

### Exact recipe for a future attempt (when an in-game test is available)

1. Choose a walkable AE maze03 cell for the portal (ideally near where the player
   naturally traverses; the walkable region is world X[-7870,-7526] Z[-3833,-3380] =
   local ~[206,544]x[110,563]). Convert to maze03-local.
2. Append to AE maze03 `0x05`: a flags=0 instance of `records\quests\portal_olympianarena1.dbr`
   at that local coord, identity rotation (via `inject_into_0x05`, base_size=56).
3. Append to AE maze03 `0x14`: a 48-byte record at the new instance's index with payload
   `bytes.fromhex('58941143e04eb3c0d62dbd952143f05d' + '6e513e901549b1d558db968c61bda66a' +
   'dbc245c358434e0bb54760b234293cc5')` (mouth_uid + exit_uid + crypt_floor1 GUID) -
   the GridEntranceDynamic-binding append the recipe flags as not-yet-built.
4. Gate offline: the placement is on the AE maze03 navmesh (analogous to G2); crypt
   landing is already ON-MESH (verified). Collateral: only maze03's blob changes.
5. **Walk-test (unavoidable):** load a Custom Quest char, reach AE maze03, confirm the
   `bossarena.qst` OnLevelLoad opens the portal, walk into it, land on crypt_floor1,
   proceed to boss_arena. Boss Arena's own DynGridEntrance chain (crypt->arena) may
   need the same treatment - inspect during that attempt.

**Files changed this wave: NONE** (research only; `local/Levels_merged.arc` unchanged
from Wave 1). No deploy for Wave 2.

---

## WAVE 3 - Secret Place (11 levels, the only multi-seam area) - 3a PASSED (internal navmesh), 3b SKIPPED (entrance)

Split into 3a (internal navmesh chain - the campaign's proven competency, BANKED) and
3b (the scrabledeggs_floor06 entrance - same ungateable-offline class as Wave 2, SKIP).

### WAVE 3a - internal navmesh (BANKED)

**Scope:** the full blood-cave recipe applied to the 11 Secret Place levels
(idx 2235-2245): neighbour-aware raster + cross-tag + Y-align + obstacle carve. This is
the ONLY multi-seam SV area, so it exercises the entire generalized pipeline (unlike the
single-level Wave 1).

**Files changed:**
- `tools/gen_bc_navmeshes.py` - added `SECRET_PLACE` ClusterConfig (`tokens=('secret_place/',)`,
  `anchor_key = behindthesp`) + registry entry `secretplace`. No GRID_SHIFT, no GUID override.
- `tools/debug/cluster_seam_check.py` - NEW generalized multi-level G3/G4 gate (the
  blood-cave seam_delta_check/engine_corridor_full are chain-hardcoded). Auto-detects
  footprint-abutting donor pairs, checks median seam dY, and runs cross-mesh reachability
  BFS from a root. `--cluster <name>` resolves members via the generator config.
- `tools/debug/area_selfcheck.py` - coverage-denominator fix: measure own-floor coverage
  against the CARVED floor (eroded MINUS obstacles), not raw eroded. Rock-heavy levels
  (forest) were false-negatived at 81% when the donor covers 100% of the carved floor.
- `local/editor_normalized/` - 11 new donors (BehindtheSP, DarkForestEnter, WoodsCorner,
  SecretForest2, PillagedVillage, ForestObsidianTransition, RogueEncampment, Rogue
  Encampment Forest Entrance, RogueEncampmentForestFiller, tFinale, murderbossroom).
- `local/Levels_merged.arc` - rebuilt with 39 donors: **688,687,165 B** (+3,035,137 vs
  build22 cumulative; +2,675,137 vs Wave 1). Quests.arc UNCHANGED. Wave-1 map preserved
  at `local/Levels_merged_wave1.arc`.

**Cluster structure (confirmed 2026-07-07):** forest chain darkforestenter<->woodscorner
<->secretforest2<->pillagedvillage (mutually footprint-abutting, cross-tagged), rogue trio
rogueencampment<->rogue encampment forest entrance<->rogueencampmentforestfiller, and 4
single-GUID isolated islands (behindthesp, forestobsidiantransition, tfinale,
murderbossroom - quest-teleport-linked rooms, not grid seams). All 11 at SV-original
positions (merged fp == SV fp), all 0x0a GUIDs resolve in merged.

**Gate outputs (verbatim):**

Generation: `Y-ALIGN: 4 constant seam offsets; 0 levels shifted; max |shift|=0u; anchor
BehindtheSP.lvl shift=0`. Forest/rogue donors guids=3-4 nbrs=2-3 with neighbour-tagged
strips (build13 failure-mode assert passed - every donor listing neighbours has
cross-tagged cells). Obstacle carve 11-18% on the rock-heavy forest levels.

Cluster seam + reachability (`cluster_seam_check.py --cluster secretplace`):
```
G4 SEAMS (median dY over shared cells):
  darkforestenter | woodscorner                    300251  +0.00  1.60
  darkforestenter | secretforest2                  188718  +0.00  2.40
  woodscorner | secretforest2                       364073  +0.00  2.40
  woodscorner | pillagedvillage                     173886  +0.00  1.00
  secretforest2 | pillagedvillage                   291015  +0.00  2.20
  rogueencampment | rogue encampment forest entrance 331688 +0.00  0.80
  rogueencampment | rogueencampmentforestfiller     198911  +0.00  0.60
  rogue encampment forest entrance | ...forestfiller  93674 +0.00  0.60
  worst median |dY| = 0.00u over 8 abutting seams (PASS <= 0.5u)
```

Traversability (BFS both directions, main-component analysis): from EITHER end
(darkforestenter or pillagedvillage) the BFS reaches **100% of every forest level's MAIN
connected component** (darkforestenter 175051, woodscorner 63868, secretforest2 101755,
pillagedvillage 213126 - all 100% reached). The <100% total-floor numbers (73/31/57/75%)
are rock-separated pockets (correctly unwalkable - the carve). Bidirectional identity
proves the chain is fully connected both ways. The rogue trio behaves the same.

Per-donor self-check (`area_selfcheck.py`, coverage vs CARVED floor):
| Level | coverage | G-OVER | main comp |
|-------|---------:|-------:|----------:|
| behindthesp | 100.0% | 0 | 100.0% (1 comp) |
| darkforestenter | 100.0% (238571/238571) | 103 (0.022%) | 69.7% (rock-fragmented forest) |
| forestobsidiantransition | 100.0% | 0 | 99.9% |
| murderbossroom | 100.0% | 0 | 100.0% |
| rogueencampmentforestfiller | 100.0% | 0 | 100.0% |

> The forest levels' low OWN main-component % (69.7%) is legitimate rock fragmentation
> (the authoritative multi-level gate is `cluster_seam_check`, which proved the main
> components are 100% mutually reachable ACROSS seams). Coverage is 100% of the carved
> walkable floor for every level. G-OVER counts are the connectivity-repair bridges
> (<0.03%).

Merged injection: 11/11 byte-exact (merged 0x0b == donor) + 0x0a stripped.

Collateral (`collateral_diff.py wave1 vs wave3`): EXACTLY 11 changed blobs (the Secret
Place levels, 148-stub -> real navmesh); ZERO other levels, no shared level, no blood-cave
or Wave-1 area touched.

Blood-cave suite still green: verify_merged 24/24 PASS; G2 entrance PASS; 24 donors
byte-identical.

**What the main session should deploy for Wave 3a:** `local/Levels_merged.arc`
(688,687,165 B) to CustomMaps (map-data only). Quests.arc unchanged. Suggested tag
`build24-wave3a-secretplace`. In-game caveat: the Secret Place interiors are now walkable
and internally connected (forest chain + rogue trio walk; the 4 disjoint rooms are linked
by `urder.qst` teleports which already load in-window), BUT the ZONE ENTRANCE (from
Rhodes via scrabledeggs_floor06) is not restored (Wave 3b, skipped) - so the zone is not
reachable by normal play yet. Like Wave 1, this banks the interiors so a future entrance
patch lands on already-meshed floors. `widowletter.qst` (the in-zone content quest) is
self-contained and will fire once the zone is reachable.

### WAVE 3b - Secret Place entrance (scrabledeggs_floor06 -> behindthesp) - SKIPPED

Same ungateable-offline class as Wave 2, with the SAME structural blocker proven:

- **Mechanism:** SV scrabledeggs_floor06 links to behindthesp via a **static `0x06`
  GridSystem portal pair** (SV scrabledeggs 0x06 references BehindtheSP @891; behindthesp
  0x06 reciprocally references ScrabledEggs_Floor06 @761). This is the blood-cave CLASS
  (static native GridSystem, not quest-DynGridEntrance) - the proven-working kind, which
  is more promising than Wave 2.
- **But the merge keeps AE's scrabledeggs_floor06** (v0x11, GUID 63197cac.., corner
  (-1917,0,-6421)), whose `0x06` references ONLY ScrambledEggs_Floor05 - the behindthesp
  link is GONE, and its 144 `0x14` records are all scenery/collision (none for behindthesp).
- **SV and AE scrabledeggs_floor06 are different layouts** (SV v0x0e GUID 4b75d427..
  corner (-1956,0,-6193); different GUID, corner delta (39,0,-228), different 0x06 content).
  behindthesp is SV-only (AE has none), appended with its SV GUID.
- So restoring the entrance needs: (1) hand-place a door on AE scrabledeggs_floor06's
  re-authored layout (ungateable level-design guess, like Wave 2's portal), (2) splice a
  `0x06` GridSystem portal descriptor (the dungeon-grid door-cell format - an even more
  complex "not-yet-built" binding append than a `0x14`), (3) remap behindthesp's `0x06`
  reference from SV's scrabledeggs GUID to AE's. None offline-certifiable; the plan's naive
  "restore the SV 0x06 descriptor" is proven non-viable (different layout/GUID/corner).

**Why SKIP not fix:** identical reasoning to Wave 2 - the door placement is a blind
level-design decision on AE's geometry and the `0x06` GridSystem-portal-pair append is
unrehearsed; shipping a guess risks a wasted deploy cycle. The advantage vs Wave 2: this
is the STATIC blood-cave mechanism (the working class), so a future attempt has a proven
template - it needs (a) a chosen door cell on AE scrabledeggs_floor06's navmesh near the
SV door's rough area, (b) authoring the reciprocal `0x06` descriptors (mirror the
HV01<->Random09A pair the blood cave uses, retargeted to AE-scrabledeggs<->behindthesp
GUIDs), (c) a G2-style landing gate on behindthesp's side (behindthesp's navmesh is now
generated - its landing CAN be gated once a door cell is chosen), (d) a walk-test.
behindthesp's interior navmesh (Wave 3a) means the DESTINATION side is ready and gateable;
only the AE-scrabledeggs source side needs hand-placement + the walk-test.

**Files changed for 3b: NONE.**

---

## WAVE 4 - Garden of Merchants entrance - SKIPPED (same ungateable class; interior already banked in Wave 1)

The Garden of Merchants INTERIOR navmesh was generated + gated + banked in Wave 1 (it is
a single-level area). Wave 4 is specifically the ENTRANCE, and it is the same
ungateable-offline class as Wave 2/3b:

- **Mechanism (reverse-engineered this wave):** a **trigger->warp**, not a GridEntrance.
  SV startingfarmland06d places `records\drxmap\zgardenofmerchants\portmebiznitch\imhere.dbr`
  (the warp destination) at local (20.2,-2.5,188.5) + a `Starting_PortalMan` NPC; SV
  hiddenvalleyborder04 places `...\portmebiznitch\seen_ocv2_trigger.dbr` (the warp trigger
  volume). Walking into the trigger warps the player to the garden. This is DB-record +
  trigger-volume driven (NOT a static 0x14/0x06 GridSystem pair, NOT quest-gated).
- **Both shared levels are re-authored AE layouts that lost the SV records**: AE
  startingfarmland06d (v0x11, 994 inst, 980 `0x14` recs - all scenery, none to garden) has
  no `imhere`/portalman; AE hiddenvalleyborder04 (v0x11, 37 inst) has no `seen_ocv2_trigger`.
  SV vs AE differ wholesale (SV 918/51 inst vs AE 994/37).
- The garden's own interior has `teleportshrine_gom.dbr` (a teleport shrine, likely the
  EXIT) + `caravan_rhodes` (the Super-Caravan the plan noted) - the destination side is
  intact in the SV-preserved garden blob (and its navmesh is banked).
- **Why SKIP:** restoring the entrance needs hand-placing the trigger volume + warp NPC on
  AE's re-authored farmland/border layouts (ungateable level-design guess) and validating a
  trigger->warp chain in-game (unrehearsed, DB+trigger driven). The plan's own steer was to
  patch only startingfarmland06d first and confirm in-game - i.e. it always required a
  walk-test. No offline gate can certify a trigger warp. The interior is banked; a future
  attempt hand-places the `imhere`/`seen_ocv2_trigger`/`Starting_PortalMan` records on AE
  startingfarmland06d's navmesh and walk-tests.

**Files changed for Wave 4: NONE** (interior was Wave 1; entrance skipped).

---

## WAVE 5 - Sparta Crypt L2 entrance - SKIPPED/DROPPED (no entrance exists, even in pristine SV)

The plan (Section 2.5) flagged this as ship-vs-drop pending entrance research. The research
is conclusive: **DROP the entrance.**

- SV spartacryptlevel2's `0x06` has a one-way link OUT to spartaoptcata01, but
  **spartaoptcata01 does NOT bind back to spartacryptlevel2 in EITHER SV or AE** - and
  SV spartaoptcata01 and AE spartaoptcata01 are BYTE-IDENTICAL (both v0x0e, 28 str, 88 inst,
  0x06 = 1102 B, same refs to Connector03). So this is NOT a merge-caused loss.
- **spartacryptlevel2 has ZERO inbound binders in BOTH pristine SV AND the merged map**
  (scanned all levels' 0x14 dest-guids + 0x06 refs). It is a genuine dev-cut / unreachable
  level in classic SV - no entrance was ever authored.
- **Decision: DROP the entrance** (nothing to restore). The interior navmesh IS banked
  (Wave 1) - so if a future maintainer ever wants to expose it, they must AUTHOR a brand-new
  entrance (e.g. a 0x06 link from spartaoptcata01 to it), which is new content, not a
  restoration. Recommend leaving it as a walkable-but-unreachable level (harmless) unless
  Will explicitly wants a new entrance authored.

**Files changed for Wave 5: NONE.**

---

## WAVE 6 - Cold Tombs - NO WORK (correctly stubbed)

Confirmed in Wave 1's ground-truth probe: coldtombs has **no `0x0a` geometry** (0 tris
derivable) - it is the direct analogue of the blood cave's ocean-scenery stub levels. It
keeps its 148-byte `0x0b` stub. No entrance ever existed (2 placed records, no binder). No
work, as the plan directed. **Files changed: NONE.**

---

## CAMPAIGN SUMMARY

| Wave | Area | Result | Deliverable |
|------|------|--------|-------------|
| 0 | Generalization proof | PASS | `gen_bc_navmeshes.py` config-driven; 24 BC donors byte-identical |
| 1 | Uber/Boss/Garden/Sparta interiors | PASS | 4 navmeshes generated + injected + gated |
| 2 | Uber+Boss entrance (maze03) | SKIP | quest-DynGridEntrance; ungateable; recipe documented |
| 3a | Secret Place interior (11 lvl) | PASS | 11 navmeshes (cross-tag+Y-align) + injected + gated |
| 3b | Secret Place entrance | SKIP | static 0x06 pair on re-authored AE level; ungateable |
| 4 | Garden entrance | SKIP | trigger->warp on re-authored AE level; ungateable |
| 5 | Sparta Crypt L2 entrance | DROP | no entrance exists even in pristine SV |
| 6 | Cold Tombs | NONE | no geometry; correctly stubbed |

**Net map deliverable:** `local/Levels_merged.arc` = **688,687,165 B** (build22 baseline
685,652,028 B; +3,035,137 B). 15 new real navmeshes injected (4 Wave-1 + 11 Wave-3a),
each byte-exact, 0x0a stripped. `Quests.arc` UNCHANGED throughout. Blood-cave suite green
at every step (24/24 donors byte-identical, all gates PASS). Zero collateral (only the 15
intended level blobs differ from build22).

**Deploy guidance for the main session:** deploy `local/Levels_merged.arc` to CustomMaps
(map-data only, `-SyncLevels`; Quests.arc needs no rebuild). Commit the 15 donors + the
tool changes (`gen_bc_navmeshes.py` config, `area_selfcheck.py`, `cluster_seam_check.py`,
`verify_merged_bc_navmeshes.py` scope fix). Suggested single tag covering both banked
navmesh waves, e.g. `build24-sv-area-navmeshes`. Rollback snapshots kept:
`local/Levels_merged_build22.arc`, `_wave1.arc`.

**The entrance gap (Waves 2/3b/4/5):** 3 of 4 remaining areas need an entrance restored,
and all 3 hit the SAME structural wall - the shared level that carried the SV entrance is a
WHOLESALE RE-AUTHORED AE layout (different GUID/corner/geometry), so the SV entrance
record's coordinates are meaningless in AE, and restoring it requires HAND-PLACING the
entrance on AE's geometry + validating an unrehearsed cross-level transition (DynGridEntrance
/ static 0x06 pair / trigger-warp) that no offline gate can certify. Each area's DESTINATION
side is now ready and on-mesh (Wave 1/3a interiors), so a future entrance push is a focused
"place the entrance on the AE shared level's navmesh, author the known binding, walk-test"
task per area - documented per wave above. This is genuine level-design-plus-in-game-test
work, correctly out of scope for an offline-gated navmesh campaign.

---
