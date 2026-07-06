# Blood-cave invisible wall - investigation state (2026-07-05 night)

> Live shared context for the parallel fix effort. **Read this first.** Append what you
> learn; never delete a proven fact. Companion RE doc: `docs/CAVE_ENTRY_CHAIN_TRACE.md`.

## The symptom (stable, reproduced ~11 times)
Player walks in the HiddenValley01 cave mouth -> into Random09A (works) -> at the
Random09A -> xPassageTransitionStart ("Mysterious Passage") boundary hits an **invisible
wall**: the next room's terrain is visible, but click-to-move refuses to cross. Same spot
every build.

## What is DEFINITIVELY RULED OUT (engine-proven via Frida, do NOT re-attempt)
The `0x0b` (RLTD/Detour) navmesh is **NOT the cause**. A Frida probe hooking the navmesh
loader `ProcessRLTD` (Engine.dll base+0x1f4ba0) during a live walk showed EVERY blood-cave
level's navmesh loads successfully:
```
random09a OK(ret=1)   xpassagetransitionstart OK(ret=1)   bc_initialpathway OK(ret=1)
drxfirstroom OK(ret=1)   drxfirstxistion_connection OK(ret=1)
```
`navmeshOK` flag (`Level+0x6a48`) == 1 on all of them, `dead` (`region+0x74`) == 0.
Ten navmesh theories have now failed in-game and are DEAD: 0x0a-stub, gate-free/own-GUID,
mutual cross-list, neighbor-aware rasterization, footprint-flush, area-id 1, height-match,
GUID residency, and (2026-07-05) the 64u tile-lattice snap (`gen_rec02` lattice snap,
commit 92cad01: verified 24/24 seams 0.000 offset in the merged map, still walled).
**Stop rebuilding navmeshes.** The geometry is fine; the engine won't LINK the two levels.

## The decisive reframe (the key new fact)
From the same live region-manager sweep (global `Engine+0x3743f0` -> `[[G]+0x34]+0x50]` =
`vector<Region*>` indexed by level index; region fields: ownGUID@+0x14, Level*@+0x50,
dead@+0x74, portalArrayA@+0x8c/+0x90, portalArrayB@+0x128/+0x12c; portal: destGUID@+0xdc,
open@+0xfc, cachedDest@+0xd8):

- The mouth **portal** `hiddenvalley01 <-> random09a` exists and is `open=1` (that is why
  the mouth works - it is a GUID-bridged portal, position-independent).
- `random09a`'s readable portal array (+0x8c) holds **exactly ONE portal, pointing BACK to
  hiddenvalley01**. There is **no forward portal** to xPassageTransitionStart.
- **CRUCIAL:** the overworld levels (hiddenvalley01, valley01, valleydescent01, the
  borders - all SEPARATE levels at distinct indices) are simultaneously resident and
  **walk-connected with NO portals between them in +0x8c.** So the engine DOES support
  seamless walking across separate static level boundaries with no portal. The whole
  overworld runs on it. Our cave levels simply do not get that stitch.

## The leading hypothesis (unproven - Track 1's job to confirm)
Seamless inter-level walk-stitch is gated by an **adjacency/zone REGISTRATION** in the map,
not by geometry alone. Overworld levels sit at natural grid positions and are registered
(SD zones / GROUPS / a level-neighbor table / region adjacency). Our cluster is:
- **RELOCATED** by `GRID_SHIFT (7840,0,2030)` to empty world space, and
- **APPENDED** to the end of the LEVELS index (xPTS idx 2261, BC 2246; Random09A is a real
  slot 703 that we blob-swapped - and the MOUTH into it works because it is a portal).
Known: GROUPS (0x11) names none of the cluster levels; SD (0x18) is SV v6 wholesale;
footprints are byte-flush-adjacent (verified) so pure geometric adjacency is NOT the gate.

## Map format cheat-sheet (world01.map in Resources/Levels.arc)
Sections: QUESTS 0x1b, GROUPS 0x11, SD 0x18, LEVELS 0x01, BITMAPS 0x19, 0x10, DATA2 0x1a,
DATA 0x02. LEVELS entry `ints_raw` = 13x int32: [0..5] tile dims, [6,7,8] grid corner
(world x,y,z), [9..12] GUID. Per-level LVL blob sections: 0x05 entities, 0x06 terrain
(embeds cross-level link GUIDs), 0x09 env, 0x0a legacy PTH navmesh, 0x0b RLTD navmesh,
0x14 entity metadata (cave-mouth GUID bindings @12 mouth id / @28 exit id / @44 dest GUID).
Tools: `tools/merge_levels_binary.py` (parse_sections, parse_level_index, SEC_LEVELS),
`tools/build_section_surgery.py` (parse_blob_sections), `tools/arc_patcher.py` (ArcArchive),
`tools/svaera_plus_portals.py` (the merge; GRID_SHIFT, blob swap, 0x14 append).
Deployed map: `<TQ docs>/CustomMaps/SoulvizierClassic/Resources/Levels.arc`.
Engine.dll: `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll`
(x86 PE32, ImageBase 0x10000000, so disasm addr = base+RVA). Key RVAs (from
CAVE_ENTRY_CHAIN_TRACE.md): navmesh loader ProcessRLTD 0x1f4ba0; cross-region portal linker
0x1f3680 (iterates region portal array, checks dstLevel+0x6a48, builds link); GetConnectedRegion
0x2063e0 (portal method, resolves dest by GUID @portal+0xdc); FindCrossedPortal 0x20c110.

## The three tracks (Will: pursue in parallel, disciplined, document everything)
1. **RE the seamless stitch** - find how the overworld links adjacent levels WITHOUT portals
   (a distinct mechanism from the portal linker), then find the map-structure registration
   the relocated/appended cluster lacks, and specify the minimal fix. Cleanest, fixes all
   seams at once. Doc: `docs/CROSS_LEVEL_STITCH_RE.md`.
2. **Portal doorways** - replicate the WORKING cave-mouth GridEntrance between each interior
   seam (start random09a<->xPTS). Proven mechanism, seamless walk-in. Doc:
   `docs/CAVE_INTERIOR_PORTALS.md`.
3. **Merge cave chain into fewer levels** - one continuous navmesh, no cross-level seams.
   Cleanest result, heaviest work. Feasibility + plan. Doc: `docs/CAVE_LEVEL_MERGE.md`.

## Structures CLEARED (do not re-investigate as the stitch registration)
- **GROUPS (0x11) - CLEARED (coordinator, groups_probe.py, 2026-07-05).** 893 records, all
  gameplay-entity categories: Unified Proxies (165), Unique Proxies (259), Wander Points (129),
  Npc Wanderers (129), Any Entity (116), RespawnShrine (26), TeleportShrine (10), Patrol/Proxy
  Patrollers, Bandari/Terracotta. Members are ENTITY proxies (spawns/shrines/wander points)
  located in various levels - NOT level-adjacency. Level GUIDs appear in a group's raw_data only
  because that level contains such an entity (bc_initialpathway/drxfirstroom appear via a
  RespawnShrine group; random09a/xPTS/valleydescent01 simply have no such proxy). GROUPS is NOT
  the walk-stitch registration. Remaining structural suspects: **SD (0x18) zones, the 0x10
  section, the LEVELS-index per-entry fields, and the RELOCATION/spatial-bounds angle** (cluster
  parked 3000u from any other level at corner ~7840 - possibly outside the engine's spatial level
  index, which would break geometric neighbor-finding while leaving the GUID-based mouth portal
  working). Also note: hiddenvalley01 has NO 0x06 cross-level GUID ref to its overworld
  walk-neighbors (only the 0x14->random09a mouth), so 0x06 cross-refs are likely NOT the overworld
  stitch registration either (per scan_mouths.py).

## Reusable Frida kit (needs the game RUNNING; Will must relaunch to use)
`scratchpad/frida_test13.py` = combined ProcessRLTD hook + region sweep. `frida_disasm.py`
= live `Instruction.parse` disassembler (grounds struct offsets). `frida_portals.py` =
FindCrossedPortal hook. `seam_lattice_check.py <map> [--gate]` = static AE-vs-ours lattice +
boundary-crossing diff. `scan_mouths.py` = 0x14/0x06 door-record scan. All read-only.

## TRACK 1 RESULT (2026-07-05 late night): STITCH MECHANISM FOUND - read docs/CROSS_LEVEL_STITCH_RE.md
Disassembly-proven end to end + 100% data correlation on vanilla meshes. **The stitch is NOT in
any map section (SD/0x10/LEVELS-fields/GROUPS all moot): there is no walk-link, no seam linker,
no adjacency table. Seamless walking = a path inside ONE level's navmesh.** Every Editor-baked
mesh rasterizes its NEIGHBORS' geometry ~16u past its own footprint, and every walkable cell's
AREA ID is a **1-based index into that mesh's GUID list** naming the level that owns the cell
(poly flags = area id, identity-copied by the engine meshproc at 0x10105a90; position->Region
resolution at 0x101f0cf0/0x101f0c90 reads poly flags-1 -> GUIDlist -> live region array).
PathManager::FindPath (0x101ee910) only ever does same-pathfinder mesh paths (0x101f2a00) or
portal hops (0x101f3680); a pathfinder "covers" a point iff its OWN mesh has a walkable poly
within (2,2,2) of it (0x101f2490). Vanilla seams work because BOTH meshes carry each other's
tagged strip (measured HV01|HVborder01: 13,534/6,373 reciprocal cross-tagged cells, 0-15u past
the plane; area K == GUID[K-1] footprint at 98-100% over ~750k cells / 5 levels; own GUID is NOT
always first - the "areas are walkable classes" doctrine is DEAD). Build13 donors: guids=[own],
all cells area 1, raster stops at the seam plane -> the engine has ZERO data linking R09<->xPTS
-> path end snaps to the plane -> the wall. The 64u lattice snap chased a ghost (per-level meshes
are SEPARATE dtNavMesh instances; no cross-mesh tile math exists). The RELOCATION/spatial-bounds
angle is also moot (pathfinder lookup is a live spatial index of resident pathfinders, position-
based, no world-bounds table). FIX (generator-only; no engine, no map-structure change):
union-rasterize own + abutting-neighbor toks per level, erode as ONE field, tag each walkable
cell by footprint containment (own=area 1, neighbor K=area K+1), GUID list [own+neighbors],
symmetric on both sides of all 39 seams; add a merged-map gate "both meshes of each seam pair
carry >=50 cells tagged as the other level past the plane". Exact code spec + self-verify gates +
risk ladder in docs/CROSS_LEVEL_STITCH_RE.md Section 6 (one watch-item: R09 multi-GUID load-order
residency at the mouth preload - build11/12 Frida logs show it held fine in practice).
