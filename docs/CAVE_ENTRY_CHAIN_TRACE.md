# Blood-cave entry chain: complete surface->cave trace (byte + Engine.dll disassembly)

Author: deepest-tier binary analysis pass, 2026-07-05. Read-only investigation
(no tool edits). Engine.dll analyzed = `backups/game_dll/Engine.dll.original`
(3,781,632 B, ImageBase 0x10000000). Maps analyzed: deployed
`CustomMaps/SoulvizierClassic/Resources/Levels.arc`, pristine
`reference_mods/SVAERA_customquest/Resources/Levels.arc`, upstream
`upstream/soulvizier_098i/Resources/Levels.arc`.

This trace supersedes the two prior Opus theories that failed in-game. Both prior
leading suspects (destination XZ-overlap; a broken/missing exit-portal binding in
the SV blob) are DISPROVEN here with bytes. The true break is a navmesh-load
**neighbor co-residency dependency** that the working base game does not have.

---

## 0. RANKED VERDICT (read this first)

**#1 (leading, mechanism-proven). R09's generated `0x0b` navmesh carries a second
GUID (`xPassageTransitionStart`) that the working base-game Random09A navmesh does
NOT. The engine will not finish loading R09's navmesh unless the `xPassageTransitionStart`
region is ALSO resident in memory at that moment. Because our relocated R09
edge-touches the SURFACE level `HighAltituedBorder01`, R09 gets pulled into surface
streaming (its blob loads, the caravan NPC renders) but its cave neighbor
`xPassageTransitionStart` (one grid-hop further, touching only R09) is not in the
surface stream. So `ProcessRLTD`'s GUID gate fails on `xPassageTransitionStart`,
R09's navmesh never loads (`Level+0x6a48` stays 0), the pathfinder's cross-region
linker skips the cave-mouth portal, click-to-move cannot path across, and the player
hits an invisible wall AT the mouth.** This is fully consistent with fix1 failing:
fix1 removed the R09/HiddenValley01 *area*-overlap but LEFT the R09/HighAltituedBorder01
*edge*-touch, so R09 still streams with the surface without its cave neighbor.

**#2 (secondary, would surface after #1 is fixed). Navmesh placement drift.** Our
generated R09 navmesh is centered at `(-230,24,2229)` but the LEVELS-index says the
level is centered at `corner+halfext = (-238,17,2221)` (an `(8,7,8)` mismatch,
because the SV geometry is wider than the AE index's half-extent of 40). The real
AE-R09 navmesh center exactly equals `corner+halfext`. If the mouth is fixed and the
player still cannot stand at the drop point or cross the R09->xPTS seam, this offset
is the next thing to correct.

**Everything else is RULED OUT with evidence** (Section 4): the surface side is
byte-identical to the working base game; the reciprocal portal binding is byte-identical
across AE/SV/deployed; the destination placement is now disjoint from HiddenValley01;
the navmesh area id (2) is a legitimate base-game walkable class; the navmesh is
structurally valid and does parse/load; the GUID list resolving in the whole-map
registry is necessary but NOT sufficient (residency is the missing half).

**THE ONE FIX TO TRY NEXT (cheapest, decisive):** regenerate R09's donor navmesh with
a **single-GUID** list (own `d840e7ae...` only, dropping the `xPassageTransitionStart`
neighbor GUID), exactly matching the working base-game AE-Random09A. This removes the
co-residency dependency so R09's navmesh loads the instant R09 is instantiated, the
mouth link builds, and the player walks in. See Section 7 for the exact change and the
follow-on if the seam then walls.

---

## 1. The transition mechanism (Engine.dll, VA-proven)

A TQAE seamless cave mouth is a PORTAL COORDINATE BRIDGE plus a PATHFINDER
CROSS-REGION LINK. Walk-in works only if the pathfinder can build a nav link across
the mouth portal into the destination region's navmesh.

### 1.1 Reading the surface binding
`GridEntrance::Read` @ `0x10195240` copies 12 dwords from the surface level's `0x14`
record into the entity at `[edi+0x2c8 .. edi+0x2f4]` = three 16-byte ids:
mouth Portal UniqueId, reciprocal exit Portal UniqueId, destination RegionId GUID.

### 1.2 Creating the surface portal
`CreatePortal` @ `0x10194e60` (call site `0x10194f1f`) allocates a Portal and writes:
- `portal+4 .. +0x10` = mouth UniqueId (`0x10194f4e`),
- `portal+0xdc .. +0xe8` = destination RegionId GUID (`0x10194fe0`, from `[esi+0x2e8..]`),
- `portal+0xec .. +0xf8` = reciprocal exit UniqueId (`0x10194fda`, from `[esi+0x2d8..]`).

### 1.3 The portal is BORN OPEN (no quest-open needed)
Portal constructor @ `0x10205d70`: `0x10205dcd  mov word ptr [esi+0xfc], 0x101`.
So `[portal+0xfc]` (IsOpen) AND `[portal+0xfd]` are both initialized to 1. A plain
`GridEntrance` mouth is open from construction; nothing has to "open" it. (This kills
the "does IsOpen need a quest to open it" branch, deliverable 5a.)

### 1.4 Crossing test
`Region::FindCrossedPortal` @ `0x1020c110` iterates the region's portal array
(`[region+0x8c .. +0x90]`), and per portal: `0x1020c15d cmp byte [eax+0xfc],0 / je skip`
(IsOpen gate), then `0x1020c16e call 0x10205840` (plane distance vs the movement
segment), keeping the nearest crossed portal. Destination region is resolved purely by
GUID via `GetConnectedRegion` @ `0x102063e0` (map lookup by `portal+0xdc`, no adjacency
test).

---

## 2. THE WALL (the exact gate, disasm-proven)

Click-to-move refuses to cross because the PATHFINDER never builds a nav link across
the mouth portal. `PathFinder` cross-region linker @ `0x101f3680` iterates portals
(`[ebx+0x128 .. +0x12c]`) and, per portal, requires ALL of:

```
0x101f36f4  mov  al,[portal+0xfc]      ; portal open?
0x101f36fc  je   0x101f3d20            ;   no  -> skip (no link)
0x101f37d5  call 0x102063e0            ; GetConnectedRegion (dest by GUID)
0x101f37dc  je   0x101f3d20            ;   null -> skip
0x101f37e8  cmp  [dstRegion+0x50],0    ; dest Level ptr present?
0x101f37ec  je   0x101f3d20
0x101f37f2  cmp  byte [dstRegion+0x74],0
0x101f37f6  jne  0x101f3d20
0x101f37ff  mov  al,[dstLevel+0x6a48]  ; *** dest navmesh LOADED-OK flag ***
0x101f3807  je   0x101f3d20            ;   0 -> SKIP: build no link across this portal
...                                    ; (0x101f3854 also requires the paired portal open)
```

`0x101f3d20` merely advances the loop (`inc esi; jb 0x101f36e0`) with NO link built
for the skipped portal. A mouth portal whose destination `Level+0x6a48 == 0` therefore
produces exactly the reported symptom: the region renders, but click-to-move cannot
path across the threshold = invisible wall.

`Level+0x6a48` is born 0 (Level ctor @ `0x101b6e01 mov byte [esi+0x6a48],0`) and is set
to 1 (`0x101b3d33 / 0x101b3ed2 / 0x101b651d / 0x101b69bc`) ONLY on a successful navmesh
load. So the whole bug reduces to: does R09's navmesh load successfully?

---

## 3. THE NAVMESH LOAD GATE and the co-residency requirement

`ProcessRLTD` @ `0x101f4ba0` (sole caller `0x101b4158`; on failure returns 0 and the
caller logs an error and does NOT set `+0x6a48`) parses the `REC\x02` container and,
for EACH GUID in the navmesh's GUID list, does:

```
0x101f4d0b  call 0x10061470            ; find GUID in the world level-GUID map ([reg+0x70])
0x101f4d16  je   0x101f51f8            ;   not in map -> FAIL
0x101f4d1c  mov  ecx,[node+0x20]       ; value = level index
0x101f4d23  mov  eax,[reg+0x50]        ; region-instance array base
0x101f4d26  cmp  [eax+ecx*4],0         ; *** instance pointer for that level ***
0x101f4d2a  je   0x101f51f8            ;   NULL (level not resident) -> FAIL
```

`0x101f51f8` -> `0x101f5247 xor eax,eax` -> returns 0 (navmesh load fails).

**`[reg+0x50]` is a LIVE `vector<Region*>` indexed by level index, null until that
level is streamed in** (not a static registry). Proof: the same array is read and
explicitly null-checked at `0x10194aa3` and at `0x101b65b8`:
```
0x101b65a9  mov  ecx,[reg+0x50]
0x101b65b8  mov  edi,[ecx+edi*4]       ; region = array[idx]
0x101b65bb  test edi,edi / je skip     ; NULL when the level is not resident
```
and `GetConnectedRegion` @ `0x102063e0` returns `[reg+0x50][idx]` after a GUID-map
lookup, caching it lazily at `portal+0xd8` and permitting a null (region not yet loaded)
result. If `[reg+0x50]` were statically full, none of these null-checks or the lazy
cache would exist. (This is the precise point the prior investigations got wrong: they
asserted "the GUID gate resolves against a whole-map registry, not live-stream." The map
at `[reg+0x70]` is whole-map and static; the instance array at `[reg+0x50]` is live. The
gate checks the LIVE array. GUID-in-map is necessary but not sufficient; the neighbor
level must be RESIDENT.)

Multi-GUID navmeshes are normal (1963 / 2235 SVAERA levels carry 2..13 GUIDs) and the
game works because grid-streaming keeps a spatial neighborhood resident: when you stand
in a level, its grid neighbors (its navmesh's neighbor GUIDs) are loaded, so its navmesh
loads. At the streaming frontier a level's navmesh simply loads just-in-time as you
approach and its neighbors stream in. That "neighbors are resident" invariant is exactly
what breaks for our R09.

---

## 4. What is RULED OUT (with the evidence that kills each)

1. **Surface side / the door frame.** Deployed `HiddenValley01` blob == pristine SVAERA
   blob, byte-for-byte (695,598 B). Its `0x05` places `SilkRdDngEntrance_C01_Ext.dbr`
   as instance #30 at local (14,18,26); its `0x14` record #30 (60-byte payload) carries
   mouth UniqueId @12 (`cfb4da3a...`), reciprocal exit UniqueId @28 (`89328d35...`),
   destination GUID @44 (`d840e7ae...` = Random09A). Intact and identical to base game.

2. **Reciprocal exit-portal binding in the destination (the prior "leading suspect").**
   R09's `0x06` section (809 B) carries the return trailer at section offsets 749 / 765
   / 781: exit UniqueId, mouth UniqueId, and `HiddenValley01`'s GUID. This trailer is
   **byte-identical across AE-Random09A, SV-Random09A, and the deployed swapped R09.**
   The 56 byte differences between AE and SV `0x06` are ALL in the walkable-cell grid
   (offsets 96..535), none in the portal trailer. The blob swap did NOT drop or mismatch
   the exit portal. (Prior hypothesis 3 disproven.)

3. **Destination placement / XZ-overlap (the other prior suspect, and fix1's target).**
   Deployed R09 footprint is X[-278,-198] Z[2181,2261]; HiddenValley01 is X[-134,-6]
   Z[2174,2302]. They are DISJOINT in X (64u gap). Fix1 achieved the disjointness, and
   the wall persisted, so raw co-residency/overlap with HiddenValley01 is not the cause.
   Every one of the 580 base-game cave-mouth destinations is likewise XZ-disjoint from
   its source surface, so distance is normal.

4. **Navmesh area id.** Our mesh uses walkable area id 2. Base game uses area 2 for
   50.2M cells (more than area 1's 48.3M) across a 400-navmesh sample; caves such as
   Random01A and EgyptHCDungeon use area 2 as walkable. Legit. (Fallback #1 in the
   status board is unnecessary.)

5. **Navmesh structural validity / does it parse and load.** The generated R09 mesh
   parses cleanly (3 sets, valid `dtTileCacheParams`, every tile header magic `DTLR`,
   version 1, `tx/ty` matching the trailer, `bmin.x == tx*12.8`, consistent
   `hmin<=hmax`, valid usable sub-rects, FastLZ decompresses to exactly `w*h*3`). Field
   for field it is indistinguishable from real editor bakes (AE-Random09A,
   AE-Random03A). So the mesh itself does not fail `dtTileCache::addTile` /
   `buildNavMeshTile`; `+0x6a48` would be set 1 IF the GUID gate passed.

6. **GUID list resolving in the whole-map registry.** Both R09 navmesh GUIDs resolve to
   real levels in the deployed LEVELS index (`d840e7ae` -> Random09A, `2d2acbf5` ->
   xPassageTransitionStart). Static resolution is fine. This is the half the prior
   agents checked; the live-residency half (Section 3) is the half they missed.

---

## 5. The working reference pair, fully dumped (deliverable 2)

`HiddenValley01 -> AE-Random09A` in pristine SVAERA is the working exemplar:

- Surface `0x14` #30: mouth `cfb4da3a...`, exit `89328d35...`, dest `d840e7ae...`.
- Destination `0x06` trailer (section offsets 749/765/781): exit `89328d35...`, mouth
  `cfb4da3a...`, source `ce93e328...` (HiddenValley01). The exit portal's UniqueId
  matches the surface `@28`. Reciprocal binding complete on both sides.
- **AE-Random09A navmesh GUID list = `[d840e7ae]` (ONE guid, own only).** center
  `(-883,-1,665)` = corner `(-923,0,625)` + halfext `(40,-1,40)` exactly; 3 genuine
  erosion sets (walkableRadius 0.4/0.6/0.8); parked at (-923,625), fully XZ-disjoint
  from every other level (0 neighbors). Because it has NO neighbor GUID, its navmesh
  loads as soon as AE-Random09A itself is instantiated. That is why the base-game mouth
  works: a single, self-contained, neighbor-free cave destination.

Control pair `NeanderThugValley02 -> Random03A` shows the same shape (1-GUID isolated
destination, reciprocal trailer present).

Note: cave destinations CAN be multi-GUID in base game (e.g. Random01A carries 4), but
those are random-dungeon levels whose whole chain is co-loaded by the random-dungeon
batch system. Our R09 is a static merge level, so that batch co-load does not apply to it.

---

## 6. Our deployed door, diffed against the working shape (deliverable 3)

| Element | Working AE | Deployed (SV swap) | Same? |
|--------|-----------|--------------------|-------|
| Surface `HiddenValley01` blob | pristine | pristine (byte-exact) | yes |
| Surface `0x14` #30 (mouth/exit/dest ids) | present | identical | yes |
| Destination `0x06` reciprocal trailer | present | byte-identical | yes |
| Destination navmesh GUID list | `[own]` (1) | `[own, xPassageTransitionStart]` (2) | **NO** |
| Destination placement | disjoint island, 0 neighbors | edge-touches SURFACE `HighAltituedBorder01` AND cave `xPassageTransitionStart` | **NO** |
| Navmesh center vs level center | equal | off by (8,7,8) | no (secondary) |

Deployed R09 grid contacts (edge-touch, 0 area overlap):
- EAST edge x=-198 touches `HighAltituedBorder01` (a Silk Road SURFACE border, Ycorner -98).
- WEST edge x=-278 touches `xPassageTransitionStart` (cave, Ycorner 18).
- `xPassageTransitionStart` in turn touches ONLY R09.

So the load-time story is: player on the HiddenValley01 surface -> `HighAltituedBorder01`
streams -> R09 streams as its west grid-neighbor (R09's blob loads; the caravan/SV cave
content renders on the surface, explaining the NPC) -> R09's navmesh tries to load ->
its GUID gate needs `xPassageTransitionStart` resident -> `xPassageTransitionStart` is
one hop further out, touching only R09, at/beyond the surface streaming frontier -> gate
fails -> `+0x6a48` stays 0 -> mouth link never built -> invisible wall. The two prior
fixes could never move this: fix1 changed placement (irrelevant to a residency gate);
neither prior fix touched R09's navmesh GUID list.

---

## 7. THE EXACT FIX (ranked)

### Fix A (do this first: cheapest and decisive)
Regenerate R09's donor navmesh with a **single-GUID** list (own `d840e7ae...` only),
identical in shape to the proven-working AE-Random09A. In `tools/gen_bc_navmeshes.py`
this is a targeted change in the per-level GUID resolution: for the Random09A key, force
the resolved list to `[own_guid]` instead of `own + resolved neighbors` (the
`OWN_GUID_OVERRIDE` mechanism for R09 already exists at lines ~169-210; add an analogous
"neighbors = none for R09" rule so `resolve_guids` returns only the own GUID). Then
regenerate R09's `.0b.bin`, re-run the R09 swap in `tools/svaera_plus_portals.py`, and
redeploy. Effort: one donor + the R09 blob, no full-cluster re-bake.

Why it should clear the mouth: R09's navmesh no longer depends on `xPassageTransitionStart`
residency, so it loads the instant R09 is instantiated (however R09 gets loaded),
`+0x6a48 -> 1`, `0x101f3680` builds the mouth link, click-to-move crosses.

Diagnostic value: if the mouth opens (player enters R09), the neighbor-co-residency
mechanism is confirmed. If the player then walls at the R09->xPassageTransitionStart
seam, that isolates the SECOND requirement (the seam stitch needs xPTS resident and
likely the neighbor GUID) and you proceed to Fix B. If the mouth STILL walls with a
1-GUID R09, the navmesh-neighbor theory is wrong and the next suspect is the paired
portal / `dstRegion+0x74` branch at `0x101f37f2` / `0x101f3854`.

### Fix B (fuller, base-game-consistent; needed if the seam walls after A)
Move the ENTIRE blood-cave cluster (all 30 levels incl. R09 + xPassageTransitionStart,
preserving their relative grid offsets so the R09<->xPTS seam is unchanged) into empty
world space that is XZ-DISJOINT from every surface/live level with NO edge-touch either
(today R09 edge-touches the surface `HighAltituedBorder01`). Every base-game cave cluster
is parked this way (~1000-1700u from any surface). With no surface contact, R09 is loaded
ONLY through the cave-mouth connected-region path, which instantiates R09 and streams its
spatial neighborhood (xPassageTransitionStart), so the GUID gate is satisfied and BOTH the
mouth and the R09->xPTS seam resolve. Change point: the xBloodCave `GRID_SHIFT` in
`tools/svaera_plus_portals.py`; pick a shift whose cluster bounding box shares no edge and
no area with any surface level, then regenerate the cluster donors (their centers follow
the shift) and rebuild. Effort: heavy (full 2GB rebuild).

### Design note (honest)
"Cave mouth -> a STATIC grid-seam CHAIN of levels" has no base-game precedent. Base-game
seamless multi-level caves are random-dungeon batches (co-loaded by the random-dungeon
system); base-game mouth destinations are single self-contained levels. Our design makes
Random09A both a mouth destination AND a static grid-seam chain head, which is why it sits
on this residency knife-edge. Fix A makes R09 behave like the proven single-level mouth
destination (correct for the mouth); Fix B makes the whole cave a disjoint cluster the
mouth streams as a unit (closest analog to how the engine actually streams a walk-in
cave). If both prove fragile in-game, the robust alternative is to stop chaining R09 to
xPTS by grid-seam and instead give R09 its OWN complete interior (a self-contained cave
whose navmesh needs no neighbor), reaching the blood cave via a second mouth/GridEntrance
inside R09 rather than a grid seam.

---

## 8. Confidence and what only an in-game test can confirm

- Mechanism of the wall (pathfinder link gated by `dstLevel+0x6a48`; `+0x6a48` set only
  on a successful navmesh load; the load gated by live residency of every navmesh-GUID
  level): HIGH, disassembly-proven at the VAs cited.
- That deployed R09 differs from working AE-R09 exactly by the extra `xPassageTransitionStart`
  GUID and the surface edge-touch: CERTAIN, byte-proven.
- That `xPassageTransitionStart` is in fact NOT resident at the moment R09's navmesh
  loads (vs merely one hop out): the ONE link static analysis cannot prove, because the
  engine's exact streaming radius and the cave-mouth connected-region pre-load order are
  runtime behavior. Fix A sidesteps this by removing the dependency entirely, which is
  why it is the recommended first move and also the cleanest experiment: its in-game
  result (mouth opens / mouth still walls / wall moves to the seam) will confirm or refute
  the residency mechanism in a single launch.
- Secondary navmesh center drift `(8,7,8)` and the seam-walkability of the generated mesh:
  only an in-game walk can confirm once the mouth is open.

## Appendix: key VAs and byte offsets
- `GridEntrance::Read` 0x10195240; `CreatePortal` 0x10194e60 (site 0x10194f1f);
  Portal ctor open-flag 0x10205dcd (`word[+0xfc]=0x0101`).
- `Region::FindCrossedPortal` 0x1020c110 (IsOpen test 0x1020c15d); plane test 0x10205840;
  `GetFrontToBackCoords` 0x102068b0; `GetConnectedRegion` 0x102063e0;
  `GetPortalOnOtherSide` 0x1020dfd0.
- PathFinder cross-region linker 0x101f3680; navmesh-loaded gate 0x101f37ff (`Level+0x6a48`);
  skip target 0x101f3d20.
- `ProcessRLTD` 0x101f4ba0 (GUID map lookup 0x101f4d0b, live-residency check 0x101f4d26,
  fail 0x101f51f8, success `mov eax,1` 0x101f51ea); caller/gate 0x101b4158/0x101b415d;
  `Level+0x6a48` writers 0x101b3d33/0x101b3ed2/0x101b651d/0x101b69bc, ctor-zero 0x101b6e01.
- Region-manager live array `[mgr+0x50]` (`vector<Region*>` by level index), null-checked
  0x10194ab2 / 0x101b65b8; manager global 0x103743f0 (+0x34 = manager, +0x50 = instance
  array, +0x70 = GUID->index map).
- Surface `0x14` #30 payload (60 B): mouth id @12, exit id @28, dest GUID @44.
- Destination `0x06` reciprocal trailer: exit id @749, mouth id @765, source GUID @781.
- Deployed R09 navmesh GUIDs: `[d840e7ae... (own), 2d2acbf5... (xPassageTransitionStart)]`;
  AE-R09: `[d840e7ae...]` only.
