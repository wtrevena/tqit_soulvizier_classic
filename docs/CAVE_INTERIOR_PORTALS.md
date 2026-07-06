# Track 2: interior cave-mouth PORTALS between blood-cave rooms

Author: Track 2 (portal-doorways), 2026-07-05. Read-only investigation of the
DEPLOYED merged map + Engine.dll disassembly (capstone). New files only:
`tools/inject_interior_portals.py` (the injector, self-verifying) and this doc.
Nothing was written to any map. Companion docs: `docs/WALL_INVESTIGATION_STATE.md`
(the shared board), `docs/CAVE_ENTRY_CHAIN_TRACE.md` (the portal/navmesh disasm),
`docs/MODDING_PLAYBOOK.md` (mechanisms 2a/2b/2c).

Goal (Will's Track 2): replicate the WORKING surface cave-mouth
`GridEntrance`/portal mechanism BETWEEN interior cave rooms, so the player crosses
`Random09A -> xPassageTransitionStart` (the first broken seam) via an engine-native
PORTAL instead of the failing seamless grid-seam stitch. Design generalizes to the
rest of the chain.

---

## 0. TL;DR + honest verdict

- The working mouth `HiddenValley01 -> Random09A` is a **portal coordinate bridge**:
  a `GridEntrance` art entity in the surface `0x05`, a `0x14` binding
  (mouth/exit/dest-GUID), and a reciprocal exit descriptor in the destination's
  `0x06`. All three halves are byte-dumped below from the deployed map.
- I built `tools/inject_interior_portals.py`, data-driven by a
  `(fromLevel, toLevel, entrancePos, exitPos)` wiring list, which injects a
  `GridEntrance + 0x14` binding into `fromLevel` and a reciprocal `0x06` descriptor
  into `toLevel`, with fresh collision-free portal ids and navmesh-derived on-mesh
  landings. It runs against the deployed map IN MEMORY and byte-verifies every
  injected record (4-seam full-chain self-test PASSES). It does NOT run the build.
- **The one hard caveat (disasm-proven, section 7).** A cave-mouth portal is subject
  to the SAME navmesh-load / stream-residency gate that kills the seamless stitch:
  `GetConnectedRegion` (VA `0x102063e0`) resolves the destination as
  `[regionMgr+0x50][levelIndex]`, which is **NULL unless the destination level is
  already stream-resident**, and the PathFinder cross-region linker (`0x101f3680`)
  additionally requires `dstLevel+0x6a48 == 1` (dest navmesh loaded). A portal does
  NOT force the destination to load. So the portal only helps if, when the player is
  in `Random09A`, `xPassageTransitionStart` is resident and its navmesh has loaded.
  The CURRENT build (cluster relocated to an isolated island at world 7840, each
  navmesh own-GUID-only so it loads independently) is exactly the configuration the
  seamless stitch also depends on. **The portal's genuine advantage: it does NOT
  require the two navmeshes to geometrically overlap in an aligned band at the seam**
  (the fragile requirement that has failed 10+ ways); it needs only (a) the source
  `GridEntrance`+binding, (b) dest resident, (c) dest navmesh loaded. If (b)/(c) hold
  for the mouth `HiddenValley01 -> Random09A` (proven: that mouth works), the interior
  portal `Random09A -> xPassageTransitionStart` should build if `xPassageTransitionStart`
  co-streams with `Random09A`. Only an in-game launch confirms co-residency.

Recommendation: ship this alongside Track 1's stitch work as a second, independent
shot. If the seamless stitch still walls in-game, the portal is a mechanism-distinct
fallback that removes the seam-overlap dependency.

---

## 1. The working mouth, fully byte-dumped (deliverable 1)

Source: DEPLOYED map
`.../CustomMaps/SoulvizierClassic/Resources/Levels.arc` (684,860,698 B, 2282 levels).
Reproduce with `scratchpad/track2_probe.py`.

### 1.1 Level geometry (merged frame, GRID_SHIFT (7840,0,2030) applied)

| level | idx | corner (x,y,z) | content dims (tiles) | footprint (x0,z0,x1,z1) | GUID |
|-------|-----|----------------|----------------------|-------------------------|------|
| HiddenValley01 | 326 | (-134,-120,2174) | (64,76,64) | (-134,2174,-6,2302) | `ce93e328b14a5eba7ab5be8e623fa215` |
| Random09A | 703 | (5979,18,3243) | (40,10,40) | (5979,3243,6059,3323) | `d840e7ae4a42c504453f13a47940bc55` |
| xPassageTransitionStart | 2261 | (5819,18,3243) | (80,4,64) | (5819,3243,5979,3371) | `2d2acbf5c046947f494e1eb9b14a6d2d` |

`Random09A` west edge x=5979 == `xPassageTransitionStart` east edge x=5979 (the seam);
z-overlap band [3243,3323].

### 1.2 Surface side: `GridEntrance` in `HiddenValley01` `0x05`

- `HiddenValley01` blob is v0x11 (magic `4c564c11`). Sections:
  `0x05`(20255) `0x14`(5228) `0x06`(312552) `0x09`(4210) `0x0b`(238382) `0x17`(114919).
- `0x05` string[20] = `Records/Underground/NaturalCave/Orient/SilkRoad/SilkRdDngEntrance_C01_Ext.dbr`.
- Instance **#30** uses string[20] at LOCAL pos `(14.00, 18.00, 26.00)`. This is the
  visible cave mouth on the terrain. Its 72-byte record (v0x11):
  ```
  14000000                                  string_index = 20
  2ebd3bb3 00000000 000080bf                rotation row0
  00000000 ffff7f3f 00000000                rotation row1
  0000803f 00000000 2ebd3bb3                rotation row2
  00006041 00009041 0000d041                pos (14.0, 18.0, 26.0)
  00000000                                  flags
  00000000000000000000000000000000          v0x11 16-byte tail (zero)
  ```
  The entity carries NO ids of its own; the mouth/exit ids come from the `0x14`.

### 1.3 Surface side: the `0x14` binding record (v0x11, 60-byte payload)

`HiddenValley01`'s `0x14` record for **index 30** (same as the instance index):
```
payload (60 B):
  02000000 00000000 01000000                header (2,0,1)  [12 B]
  cfb4da3a694905fc2d76e29915737882          mouth Portal UniqueId   @12
  89328d35e24a56be552721831035ed62          exit  Portal UniqueId   @28
  d840e7ae4a42c504453f13a47940bc55          dest RegionId GUID (Random09A)  @44
```
- The 12-byte header `(2,0,1)` is IDENTICAL to the leading 12 bytes of a standard
  20-byte `0x14` payload `(2,0,1,1,0)`; the binding form drops the trailing `(1,0)`
  and appends the three 16-byte ids.
- Across the whole map, 60-byte binding headers are only ever `(2,0,1)` (x458) or
  `(2,0,0)` (x122). We use `(2,0,1)`.
- `GridEntrance::Read` (VA `0x10195240`) reads 12 consecutive dwords (48 bytes) from
  the entity stream into `[entity+0x2c8 .. +0x2f4]` = mouth(+0x2c8), exit(+0x2d8),
  dest GUID(+0x2e8). `CreatePortal` (`0x10194e60`, site `0x10194f1f`) then writes
  `portal+0xdc = dest GUID`, `portal+4 = mouth id`, `portal+0xec = exit id`, and the
  Portal ctor (`0x10205dcd`) sets `word[portal+0xfc] = 0x0101` so the portal is BORN
  OPEN (no quest needed).

### 1.4 Destination side: the reciprocal `0x06` descriptor (return + pairing)

`Random09A`'s `0x06` (809 B, v0x0e) ends with a portal-descriptor LIST at the tail:
```
... terrain grid ...
40000000                                    field = 64
01000000                                    count = 1
89328d35e24a56be552721831035ed62            exit  UniqueId  (== surface @28)
cfb4da3a694905fc2d76e29915737882            mouth UniqueId  (== surface @12)
ce93e328b14a5eba7ab5be8e623fa215            source GUID (HiddenValley01)
08000000 00000000 02000000                  per-descriptor 12-byte trailer (t0=8,0,t1=2)
```
- Structure decoded from the deployed map:
  `[u32 field=64][u32 count=N][ N x 60-byte descriptor ]` at the very END of `0x06`
  (after the head `[1][2][1][u32 dbrId][u32 strlen][dbr string]` and the terrain
  grid). Each descriptor = `[exit 16][mouth 16][srcGUID 16][12-byte trailer]`.
- **Reciprocity is exact and universal.** Verified on `Random09A` + 4 base-game
  mouths (`Connector02->StartingTownOptional02A`, `Connector01->SpartaOptCave02`,
  `Connector03->SpartaOptCata01`, `PineForestVillage02->ArachnosUnderground01_Floor0`):
  the descriptor's exit/mouth match the surface `0x14`'s exit/mouth byte-for-byte.
- A destination CAN hold several descriptors: `Greece/Athens/Underground/Entrance01`
  has `count=2` (two 60-byte descriptors). 54+ levels have 2+ dest-links.
- The per-descriptor trailer `(t0,0,t1)` varies by level (`Random09A` (8,0,2),
  `StartingTownOptional02A` (6,0,4)); it is a portal-type + index and is NOT read by
  the inbound crossing (section 4). We emit `(8,0,2)` (the working `Random09A` value).

### 1.5 v0x0e binding variant (what `Random09A` itself needs)

`Random09A` is v0x0e (magic `4c564c0e`) and ships with an EMPTY `0x14` (size 0). The
v0x0e binding form is proven by `xBloodCave/yet_another_fucking_connector` (v0x0e),
whose lone `0x14` record is a **48-byte** binding with **no 12-byte header**:
```
0x14 raw: 5d000000 30000000  <index=93><size=48>
  5db9d081594d5470b57827afcbd84606   mouth UniqueId   @0
  3dc661651243c6a25e16a6b76d3cc5d6   exit  UniqueId   @16
  aaedca39074882f5b4a72aabff97657e   dest GUID (drxBC3)  @32
```
So: **v0x11 -> 60-byte payload `[hdr(2,0,1)][mouth][exit][dest]`; v0x0e -> 48-byte
payload `[mouth][exit][dest]`.** (Note: `yac`/`drxBC3` are SV connectors whose
bindings are ONE-SIDED - neither 0x06 carries the other's reciprocal - so they are a
layout template only, NOT a reciprocity template. The base-game mouths are the
reciprocity template.)

---

## 2. Injection design (deliverable 3)

Tool: `tools/inject_interior_portals.py`. Self-contained, does NOT run the build.
The coordinator integrates it as a step in `tools/svaera_plus_portals.py` (section 6).

Per seam `fromLevel -> toLevel` it performs exactly the working-mouth pattern:

1. **Mint a fresh (mouth, exit) UniqueId pair.** Ids are `0xFEEDCAFE || u32 tag ||
   8 zero bytes`, drawn from a space scanned collision-free against all **641**
   existing portal ids in the deployed map (`scan_existing_portal_ids`). The scan
   pulls ids from every `0x14` 60/48-byte binding across all 2282 levels; the minted
   tags `0x5000+` do not collide.
2. **Inject a `GridEntrance` into `fromLevel`'s `0x05`** at `entrancePos` (local),
   handling v0x0e (56-byte records) and v0x11 (72-byte). Returns the injected
   instance index. Default art = `SilkRdDngEntrance_C01_Ext.dbr` (overridable per
   seam via `entranceDbr`).
3. **Add the `0x14` binding** for that instance: v0x11 -> 60-byte `[hdr(2,0,1)]
   [mouth][exit][destGUID]`; v0x0e -> 48-byte `[mouth][exit][destGUID]`. For v0x11
   it rebuilds a full ordered record set (default 20-byte `(2,0,1,1,0)` for every
   other instance, required for v0x11 interactivity). For v0x0e (empty `0x14`) it
   inserts a `0x14` section after `0x05` carrying just the binding (matching `yac`).
4. **Append the reciprocal descriptor to `toLevel`'s `0x06`**: if a
   `[64][count][descriptors]` list already ends the section, bump `count` and append
   our 60-byte descriptor; else append a fresh `[64][count=1][descriptor]`. The
   descriptor is `[exit][mouth][fromLevel GUID][trailer (8,0,2)]` - byte-identical in
   shape to the proven `Random09A` return descriptor.

The blob is rebuilt with `build_section_surgery.rebuild_blob` (section walk
preserved; verified round-trip). The magic byte and record stride are never changed
(v0x0e stays v0x0e), avoiding the v0e/v11 crash trap.

### 2.1 Self-verify (built in)

`py tools/inject_interior_portals.py [--chain]` runs the injection against the
deployed map in memory and re-parses every injected record:
- GridEntrance art string present in `fromLevel` `0x05`;
- `0x14` binding at the injected instance index byte-matches the expected payload;
- `toLevel` `0x06` ends with a valid `[64][count]` + our 60-byte descriptor, and the
  source GUID is findable (the engine scans for it);
- both blobs pass a section round-trip (no bytes swallowed).

Result (2026-07-05): single-seam and full 4-seam chain BOTH **PASS**, no map written.

---

## 3. Landing derivation (deliverable 2)

The failure mode that killed the old quest-teleport was an off-mesh / above-floor
target (0.28u off-mesh, +7u above floor). Landings here are derived from the
DESTINATION level's OWN `0x0b` navmesh, never the grid corner.

`derive_landing_local(dest_0x0b, dest_ints, near_world_x, near_world_z)`:
- parses the dest `0x0b` walkable cells (`area != 0`, `height != 0xff`) in world
  space: `origin = center - dims`; cell `(tx,ty,lx,lz)` ->
  `wx = origin_x + (tx*64+lx+0.5)*0.2`, `wz` likewise, `wy = (hmin+hval)*0.2`;
- keeps only INTERIOR cells (all 4 orthogonal neighbours walkable) so the landing is
  robustly ON the mesh, never an edge sliver;
- picks the interior cell nearest the seam midpoint (or the mesh centroid);
- returns it in LOCAL coords (world minus the dest grid corner), floor Y.

### 3.1 The critical Y fact (the two floors differ ~13.6u)

Parsed from the deployed navmeshes:

| level | walkable X range | walkable Z range | walkable Y range |
|-------|------------------|------------------|------------------|
| Random09A | [5920.5, 6050.7] | [3246.1, 3344.1] | **[26.4, 29.0]** |
| xPassageTransitionStart | [5792.5, 6047.5] | [3246.1, 3359.9] | **[15.4, 18.0]** |

The two rooms' floors are ~11-14u apart in Y at the shared seam. A landing MUST use
the destination's own floor Y. Derived landings near the seam midpoint
`(x=5979, z=3283)`:

| direction | landing LOCAL (x,y,z) | landing WORLD (x,y,z) | dest floor |
|-----------|----------------------|-----------------------|------------|
| arrive in xPassageTransitionStart (from R09) | (164.30, -2.60, 35.70) | (5983.30, **15.40**, 3278.70) | xPTS floor |
| return into Random09A (from xPTS) | (4.30, 11.00, 35.70) | (5983.30, **29.00**, 3278.70) | R09 floor |

Both are interior on-mesh cells (122401 / 86088 interior cells to choose from), at
the correct per-level floor Y. This is exactly why the landing is derived per-level
from the navmesh and not from a shared seam coordinate.

Note on placement semantics: the engine positions the player on crossing via
`Portal::GetFrontToBackCoords` (`0x102068b0`) = `inverse(surfaceXform) x destXform`
through the PAIRED (reciprocal) portal, not from an explicit landing coordinate in
the binding. The derived landings above are therefore the on-mesh points the mouth /
exit portal ENTITIES should sit at (and the doc's ground truth that a walkable cell
exists at the seam at the right Y). For production, pass explicit `entrancePos` /
`exitPos` per seam (below) rather than relying on centroid auto-derivation, so the
mouth entity sits exactly on the intended cell.

---

## 4. Why the inbound crossing needs only `GridEntrance + 0x14` (disasm)

`GridEntrance::Read` (`0x10195240`) populates the entity's id block
`[entity+0x2c8..+0x2f4]` from the entity stream (fed by the `0x14` binding), NOT from
the source level's `0x06`. `CreatePortal` (`0x10194e60`) builds the portal from that
block and adds it to the source region's portal array; the portal is born open. So
the **inbound** portal `Random09A -> xPassageTransitionStart` is fully defined by the
`GridEntrance` in `Random09A` + its `0x14` binding.

The destination `0x06` reciprocal descriptor supplies the PAIRED exit portal (matched
by the exit UniqueId), used for the RETURN crossing and for
`GetFrontToBackCoords`/`GetPortalOnOtherSide` (`0x1020dfd0`) to place the player. We
write it to match the working mouth so the return + placement resolve.

---

## 5. Per-seam wiring table (deliverable: generalization)

All interior chain levels exist in the deployed map, all v0x0e, all carry `0x0b` +
`0x06`, and every consecutive pair abuts (verified xgap=0, zgap=0):

| from | to | from idx | to idx | seam | notes |
|------|----|----------|--------|------|-------|
| Random09A | xPassageTransitionStart | 703 | 2261 | R09 west x=5979 | the #1 broken seam |
| xPassageTransitionStart | BC_initialpathway | 2261 | (SV-only) | x=5819 | |
| BC_initialpathway | drxFirstxistion_connection | | | x=5739 | |
| drxFirstxistion_connection | drxFirstRoom | | | x=5739/z | |
| drxFirstRoom | (next cave rooms) | | | | extend as needed |

Wiring is a Python list the coordinator passes to `inject_interior_portals`:
```python
wiring = [
  {'fromLevel': 'Levels/World/Orient/Underground/Random09A.lvl',
   'toLevel':   'Levels/World/xBloodCave/xPassageTransitionStart.lvl',
   'entrancePos': (4.3, 11.0, 35.7),      # LOCAL in Random09A (world (5983.3,29.0,3278.7))
   'exitPos':     (164.3, -2.6, 35.7)},   # LOCAL in xPTS       (world (5983.3,15.4,3278.7))
  {'fromLevel': 'Levels/World/xBloodCave/xPassageTransitionStart.lvl',
   'toLevel':   'Levels/World/xBloodCave/BC_initialpathway.lvl',
   'entrancePos': None, 'exitPos': None},  # None -> auto-derive from the dest navmesh
  # ... one row per seam ...
]
```
`entrancePos`/`exitPos = None` auto-derives near the seam. Auto-derivation is proven
for all 4 chain seams (self-test `--chain` PASSES) but can round a mouth a few units
past a narrow level corner (measured xPTS->BC entrance at local x=-4.3); prefer
explicit coords for the two load-bearing seams.

Fresh ids assigned across the chain in the self-test: `feedcafe0050`, `0150`,
`0250` ... `0750` (2 per seam), all collision-free.

For a BIDIRECTIONAL portal at a seam (mouth both ways) add a second wiring row with
from/to swapped; each direction is a self-contained `GridEntrance + 0x14` inbound
portal (section 4), so a two-row seam does not depend on the `0x06` reciprocal at all
- the most robust option if the `0x06` write proves fragile in-game (section 7).

---

## 6. Integration point for the coordinator (do not run the build here)

`inject_interior_portals(get_blob, set_blob, get_ints, level_index_by_key, wiring,
id_scan_pairs, base_tag=0x5000)` is callback-based so it plugs into
`svaera_plus_portals.py`'s in-memory level table without this module knowing the
merge internals:
- call it AFTER the R09 blob-swap + the `0x0b` injections, just before the DATA
  compaction loop writes each blob;
- `get_blob(key)`/`set_blob(key, blob)` read/write the CURRENT merged blob for a
  level key (lowercased fname, `/` separators); `get_ints(key)` returns the merged
  `ints_raw` (GUID + grid corner); `id_scan_pairs` = `[(blob,) for every merged
  blob]` so minted ids avoid the whole merged map;
- it mutates `fromLevel` and `toLevel` blobs in place via the callbacks and returns
  per-seam report dicts (ids + resolved coords) to log.

Because `Random09A` is the blob-swapped v0x0e level and `xPassageTransitionStart` is
an appended SV-only v0x0e level, both are edited by the same path; the injector reads
their post-swap/post-shift blobs and edits only `0x05`/`0x14` (fromLevel) and `0x06`
(toLevel). It touches neither the `0x0b` navmesh nor the LEVELS index, so it composes
cleanly with the existing pipeline and the navmesh verifier still passes.

Proposed edit (do NOT apply on the main branch - coordinator integrates): in
`svaera_plus_portals.main()`, after the R09 swap block (~line 628) and before the
per-blob write loop, build the in-memory blob map, call `inject_interior_portals`,
and write the returned blobs back into the merged-level blob source. Keep it behind a
flag (e.g. `SVC_INTERIOR_PORTALS=1`) so it can be toggled against Track 1's stitch.

---

## 7. Risks (deliverable 4) - honest, ranked

1. **RESIDENCY GATE (highest, disasm-proven, shared with the seamless stitch).**
   `GetConnectedRegion` (`0x102063e0`) returns `[regionMgr+0x50][destLevelIndex]`,
   NULL if the destination level is not stream-resident; the PathFinder linker
   (`0x101f3680`) also needs `dstLevel+0x6a48 == 1`. The portal does NOT force a
   load. If `xPassageTransitionStart` is not resident (with its navmesh loaded) when
   the player is in `Random09A`, the portal builds no walk-link and the wall persists
   - the SAME failure the seamless stitch hits. The current isolated-island cluster
   (world 7840, own-GUID-only navmeshes so each loads independently) is the best case
   for co-residency; the mouth `HiddenValley01 -> Random09A` proving it works means
   `Random09A` at least loads on demand. Whether its cave neighbour co-streams is a
   runtime-only fact. **Mitigation if it walls:** the portal removes the geometric
   seam-overlap requirement, so if Track 1's stitch fails purely on geometry, the
   portal is still worth trying; and a bidirectional two-`GridEntrance` seam (section
   5) avoids the `0x06` dependency.

2. **`0x06` descriptor-list write into a zero-tailed section (medium).** The base
   game frames the reciprocal list as `[64][count][N x 60B]` at the `0x06` tail.
   `xPassageTransitionStart`'s `0x06` tail is currently zero-padded with NO list, so
   the injector appends a fresh `[64][count=1][descriptor]`. This is structurally
   identical to `Random09A`'s working tail, but I could NOT prove from disassembly
   alone that the trailing zeros are free padding rather than part of the terrain
   grid the head length implies. If a launch shows the return broken (or worse, a
   terrain glitch), the safe alternative is the bidirectional two-`GridEntrance`
   design (each direction inbound-only, no `0x06` write). The inbound direction (the
   blocked one) does NOT use this write at all (section 4), so this risk is confined
   to the return trip.

3. **`GridEntrance` art looks like a dark cave mouth in an OPEN passage (low-medium,
   cosmetic).** `SilkRdDngEntrance_C01_Ext.dbr` is the visible Silk Road cave-opening
   mesh. Placed mid-tunnel at the `Random09A/xPTS` seam it will render as a cave
   opening, which may look odd where the passage is already open. Options: pick a
   subtler `GridEntrance`-class art per seam (the binding lives in `0x14`, the art is
   just the entity's mesh - any `GridEntrance` DBR works, or one with a tiny/invisible
   mesh), or accept the cave-mouth look (it reads as "the tunnel continues into a
   darker cave", which is thematically fine for a blood cave). Set via the wiring
   `entranceDbr` field.

4. **Transition feel: seamless walk-in vs a load/cursor (low).** A `GridEntrance`
   mouth is a WALK-IN with no load screen (the surface mouth `HiddenValley01 ->
   Random09A` is seamless, proven). The portal is born open (Portal ctor sets
   `word[+0xfc]=0x0101`), so no quest prompt appears. Expected behaviour: the player
   walks across the mouth plane and is placed at the paired exit with no load screen,
   same as the surface mouth. The one uncertainty is whether crossing a portal
   between two ALREADY-adjacent grid levels (rather than surface->distant-cave)
   produces any visible hitch; unobservable statically.

5. **Off-mesh / above-floor landing (mitigated).** Killed the old teleport. Mitigated
   by deriving landings from the destination navmesh interior cells at the dest's own
   floor Y (section 3). The two floors differ ~13.6u, so a naive shared coordinate
   would be ~13u off the floor on one side - the per-level derivation avoids exactly
   that.

6. **Mouth-plane orientation (low).** `CreatePortal` derives the crossing plane from
   the `GridEntrance` entity transform. The injector writes an identity rotation, so
   the plane faces the level axes. If the player can walk "around" the mouth without
   crossing its plane, the crossing won't fire; placing the mouth spanning the narrow
   seam corridor (the derived seam-midpoint cell) makes the crossing unavoidable. A
   per-seam rotation could be added to the wiring if a seam needs a specific facing.

---

## 8. Files

- `tools/inject_interior_portals.py` - the injector + self-verifier (NEW, this
  track). Entry point `inject_interior_portals(...)`; run `py
  tools/inject_interior_portals.py [--chain]` for the in-memory self-test.
- `scratchpad/track2_probe.py`, `track2_probe2.py`, `track2_probe3.py`,
  `track2_probe4.py` - read-only ground-truth dumps of the working mouth, the
  `0x14`/`0x06` layouts, and the v0x0e binding variant.
- `scratchpad/track2_disasm.py` - capstone disasm of `GetConnectedRegion`,
  `FindCrossedPortal`, `GetPortalOnOtherSide`, `GridEntrance::Read`, `CreatePortal`,
  Portal ctor (grounds the residency-gate + inbound-portal findings).

## 9. Engine VAs used (all in `backups/game_dll/Engine.dll.original`, ImageBase
`0x10000000`)

- `GridEntrance::Read` `0x10195240` - copies mouth/exit/dest ids (48 B) into
  `[entity+0x2c8..+0x2f4]`.
- `CreatePortal` `0x10194e60` (site `0x10194f1f`) - builds the portal; writes
  `portal+0xdc = dest GUID`.
- Portal ctor `0x10205d70` (`0x10205dcd  mov word [esi+0xfc], 0x0101`) - born open.
- `Region::FindCrossedPortal` `0x1020c110` - plane-crossing test, IsOpen gate at
  `portal+0xfc`.
- `Portal::GetFrontToBackCoords` `0x102068b0`; `Portal::GetConnectedRegion`
  `0x102063e0` (resolves dest = `[mgr+0x50][idx]`, NULL if not resident);
  `GetPortalOnOtherSide` `0x1020dfd0`.
- PathFinder cross-region linker `0x101f3680` (needs `dstLevel+0x6a48 == 1`);
  region-manager global `0x103743f0` (+0x34 manager, +0x50 live region-instance
  array, +0x70 GUID->index map).
