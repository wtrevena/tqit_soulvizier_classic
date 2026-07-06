# Blood-cave invisible wall - complete ATTEMPT LEDGER

> Every fix tried, whether it worked, how it was verified, and the lesson. Purpose:
> **never re-run a dead approach.** Companion docs: `WALL_INVESTIGATION_STATE.md` (current
> proven facts + open suspects), `CAVE_ENTRY_CHAIN_TRACE.md` (Engine.dll disassembly).
> Append new attempts here as they happen; never delete a recorded result.

## The two distinct problems (do not conflate)
1. **ENTRANCE / MOUTH** - getting the player from the surface (HiddenValley01) INTO the first
   cave room (Random09A). Mechanism = a cave-mouth **portal** (GUID-bridged). **SOLVED** (see
   Era 1). The mouth works today: Frida confirms `hiddenvalley01 <-> random09a` portal `open=1`.
2. **INTERIOR SEAM** - walking from Random09A onward through the chain
   (Random09A -> xPassageTransitionStart -> bc_initialpathway -> drxfirstroom -> ...). Mechanism =
   seamless cross-level walk-stitch (NO portal, like the overworld). **UNSOLVED** - this is the
   invisible wall at "Mysterious Passage". Everything in Era 2 below is about this.

Because both were "invisible walls", earlier attempts sometimes targeted the wrong one. The
mouth being fixed (player enters Random09A) is the proof the ENTRANCE problem is done and the
remaining wall is purely the INTERIOR SEAM.

---

## Era 0 - the format crack (the enabling win)
- **Approach 22 (pre-2026-07-04): inject a 148-byte empty `0x0b` stub** into each SV-only level,
  betting the engine's built-in runtime Recast generator would rebuild the navmesh at load.
  **DID NOT WORK.** Disassembly proved the runtime generator (`ProcessRLTD_flow` ~VA 0x101F6210)
  is gated by `cmp byte[0x10374441],0` and that gate byte is never set non-zero anywhere in
  Engine.dll -> it always early-returns. **Lesson:** the shipping engine only LOADS `0x0b`, it
  does not GENERATE it; we must supply real navmeshes.
- **Offline navmesh generation (Fable-max, WORKED):** fully reverse-engineered the `0x0b`
  RLTD/Detour `dtTileCache` + FastLZ container (`rec02_format.py`, `fastlz.py`, `gen_rec02.py`,
  `tok_parse.py`); generate real navmeshes in pure Python from the pristine `0x0a` geometry.
  Round-trip byte-identity proven on 670 real sections. **This unblocked everything** (Steam-clean,
  no Editor, no DLL patch). NOTE: this made the navmeshes LOAD - it did not by itself make the
  seams walkable (Era 2).

## Era 1 - the ENTRANCE / mouth (SOLVED)
- **Quest-portal boat-dialog teleport - DID NOT WORK (abandoned).** Teleport the player into the
  cave via a BoatDialog quest. Failed twice: first the target coord (-418,23,2227) was ~0.28u
  off-mesh / +7u above floor (derived from the LEVELS grid corner instead of the navmesh
  center-dims, which carries +16 pad) -> engine silently rejected; re-deriving to an on-mesh cell
  (-385,16,2236) STILL failed (dialog stopped appearing - fragile 200x-repeat OnLevelLoad idiom +
  saved quest state). **Lesson:** quest-teleport into a dungeon is fragile; a landing cell must be
  derived from the navmesh, not the grid corner; Will abandoned this for the engine-native doorway.
- **Random09A blob-swap (WORKED for the mouth).** SV's classic entry was a walk-in: SVAERA's
  `Random09A` level blob is replaced with SV's version (adds the west tunnel + blood-cave dressing),
  KEEPING the AE GUID in the LEVELS index so HiddenValley01's native `GridEntrance` cave mouth
  (whose `0x14` metadata references that GUID) streams the player in unchanged. Player now walks in
  the mouth into Random09A. **Confirmed in-game + by Frida (mouth portal open=1).**
- **Placement / GUID-residency-gate fixes (WORKED, several iterations).** The mouth initially
  walled because Random09A's navmesh failed the load GUID-residency gate: `ProcessRLTD` loads a
  navmesh only if EVERY listed neighbor GUID is stream-RESIDENT, and Random09A edge-touched a
  SURFACE level (HighAltituedBorder01) so it streamed in early, before its cave-neighbor was
  resident -> gate fail -> mouth wall. **Fix that worked:** relocate the WHOLE cluster (rigid,
  `GRID_SHIFT`, final (7840,0,2030)) into empty space with real clearance so it only loads as a
  unit via the mouth. Plus area-flag (id 2->1). After this, Will walked IN through the mouth and
  into Random09A. **Lesson:** the navmesh load gate is a residency check on the GUID list; isolate
  the cluster so it co-loads. (This is ALSO why later "own-GUID-only" navmesh lists were used.)

## Era 2 - the INTERIOR SEAM wall (UNSOLVED; 10 navmesh theories, ALL failed in-game)
All of these targeted the `0x0b` navmesh or the LEVELS-index footprint. **Every one was
byte-verified as deployed, and every one still walled at the same spot in-game.** The pattern of
10/10 failures is itself the finding: **the navmesh content was never the variable.**

| # | Attempt | Hypothesis | Result | Lesson |
|---|---------|-----------|--------|--------|
| 1 | Gate-free / own-GUID-only navmesh list (with 2u footprint gap) | strip neighbor GUIDs so the mesh always loads | WALL | loads fine but no tile adjacency across a 2u gap |
| 2 | Footprint-flush (normalize content-dims -> box-dims so edges abut, gap 0) | engine needs index-footprint edge-abutment | WALL | flush (0/0 gap, byte-verified) still walls |
| 3 | Height-match investigation | floor-Y delta at the seam blocks the link | NOT IT | the WORKING R09<->xPTS seam has a BIGGER delta (2.6u) and walks; broken seam delta 0.0u |
| 4 | Area-id 2 -> 1 | cave interiors use walkable area-id 1 | WALL | area-id irrelevant to the link |
| 5 | Mutual cross-list via `0x0a` | both levels must list each other | WALL | `0x0a` lists are asymmetric; also `0x0a` is the legacy fmt the engine can't parse |
| 6 | Neighbor-aware rasterization (Fable-max; local oracle 18/18 seams cross) | each mesh must physically cross the boundary into the neighbor | WALL | walkable cells DO cross both sides (measured); still no link. Found+fixed 2 latent same-defect seams (good) but didn't fix the wall |
| 7 | Mutual grid-adjacency GUID lists | symmetric neighbor GUIDs = the stitch | WALL | GUID list is only the LOAD gate, not the stitch |
| 8 | Own-GUID-only + flush footprints (disasm-grounded combo) | the untested "loads + adjacent" combo | WALL | still walls with mesh loading + flush |
| 9 | 64u tile-lattice snap (build13, `gen_rec02` origin snap) | tiles stitch only if the two 12.8u lattices coincide; ours were 6.4u off, AE seams 0.000 | WALL | verified 24/24 seams 0.000 offset in merged map; STILL walls. The lattice geometry is not what gates the link |
| 10| (Era-1 residency fixes are separate - they fixed the MOUTH, not the seam) | | | |

## Era 4 - MECHANISM FOUND + THE FIX (2026-07-05 night, attempt #12)
Parallel Fable-max RE (docs/CROSS_LEVEL_STITCH_RE.md) cracked the actual mechanism, disasm-proven
with 100% correlation on ~750k vanilla cells: **there is no walk-link. Each level owns a PRIVATE
navmesh. The engine tags every poly with its cell's AREA ID and reads that at runtime as a 1-BASED
INDEX INTO THE MESH'S GUID LIST = the level that owns the cell. A seamless seam crossing is a
SINGLE-mesh path: a level's mesh rasterizes its neighbour's terrain ~16u PAST the shared boundary
and tags that strip with the neighbour's GUID index, so one mesh covers both sides of the click.**
Our meshes stopped at the boundary with only their own GUID -> no mesh covered both sides -> wall.

| # | Attempt | What it added over #1-11 | Static result |
|---|---------|--------------------------|---------------|
| 12 | **Cross-tag rasterization** (gen_rec02 per-cell area = 1+index of the GUID-list level whose footprint box contains the cell; gen_bc_navmeshes GUID list = [own]+abutting neighbours; each mesh rasterizes neighbour toks past the boundary) | the ONE thing all 11 missed: cross-boundary walkable cells tagged with the neighbour's GUID index, in BOTH meshes | **GATE PASS 20/20 walk seams**; R09\|xPTS = 3493/69473 cross-tagged cells past the plane (was 0/0). Built + verified 24/24 byte-exact + DEPLOYED (684,869,910 B). Walk test pending. |

New tooling: `tools/verify_cross_tags.py` (the anti-regression gate: both sides of every walk seam
must carry >=50 cross-tagged cells past the plane - all 11 prior builds fail it, #12 passes),
`tools/debug/navlib.py` (decode donor -> tagged cells). The gate is the static success-predictor;
only Will's walk test gives final confirmation (project discipline), but the mechanism is HIGH
confidence + the gate objectively distinguishes #12 from every failure.

## Era 3 - the DEBUGGER (Frida) turning point - what is now PROVEN
Will authorized attaching a debugger. Frida (scriptable, no GUI) attached to the running 32-bit
TQ.exe and hooked Engine.dll. Probes: `scratchpad/frida_probe.py` (ProcessRLTD load hook),
`frida_portals.py` (FindCrossedPortal), `frida_sweep.py` / `frida_test13.py` (region-manager
memory sweep), `frida_disasm.py` (live `Instruction.parse` to ground struct offsets).

**PROVEN (do not re-litigate):**
- Every blood-cave navmesh **LOADS OK** (`ProcessRLTD` ret=1; `Level+0x6a48` flag=1):
  random09a, xpassagetransitionstart, bc_initialpathway, drxfirstroom, drxfirstxistion_connection.
  => **the navmesh is not the cause. Stop rebuilding it.**
- The mouth **portal** `hiddenvalley01 <-> random09a` exists and is `open=1` (why the mouth works).
- `random09a`'s portal array holds exactly ONE portal, pointing BACK to the surface. No forward
  portal to the passage.
- **The overworld levels (all SEPARATE levels) are walk-connected with NO portals between them.**
  Seamless inter-level walk-stitch is a real engine feature that needs no portal; our cave levels
  don't get it.

**Meta-lesson (Will's, and the hard-won one):** after 2-3 same-result failures, STOP guessing and
MEASURE the working-vs-broken difference directly. Nine navmesh rebuilds cost far more than one
debugger session. The debugger session ended the entire navmesh line of inquiry in one run.

## Structures CLEARED as the stitch registration (with evidence)
- **GROUPS (0x11)** - `scratchpad/groups_probe.py`: 893 records, all gameplay-entity categories
  (Unified/Unique Proxies, Wander Points, Npc Wanderers, RespawnShrine, TeleportShrine, ...). Level
  GUIDs appear only because a level holds such an entity. NOT walk-adjacency.
- **`0x06` cross-level GUID refs** - `scan_mouths.py`: hiddenvalley01 has NO `0x06` cross-ref to its
  overworld walk-neighbors (only the `0x14`->random09a mouth), yet it stitches to them. So `0x06`
  cross-refs are not the overworld stitch registration.

## Open suspects (the current 3 parallel tracks - 2026-07-05 night)
Navmesh ruled out -> the wall is the **cross-level walk-stitch registration** the relocated+appended
cluster lacks. Three tracks running in parallel (Workflow wf_4d232512-454):
- **T1 (Fable-max) RE the stitch** -> `CROSS_LEVEL_STITCH_RE.md`. Suspects: SD (0x18) zones, the
  0x10 section, LEVELS-index per-entry fields, and the RELOCATION/spatial-bounds angle (cluster
  parked ~3000u out at corner 7840 - maybe outside the engine's spatial level index, which would
  break geometric neighbor-finding while the GUID-based mouth still works).
- **T2 (Opus) portal doorways** -> `CAVE_INTERIOR_PORTALS.md` + `tools/inject_interior_portals.py`.
  Replicate the working mouth GridEntrance between interior rooms.
- **T3 (Opus) merge levels** -> `CAVE_LEVEL_MERGE.md`. Merge the chain into one level = one
  continuous navmesh, no seams.

## Meta-lessons (apply to all future map work)
1. **Two invisible-wall problems, two mechanisms:** mouth = GUID portal (position-independent);
   interior seam = seamless stitch (position/registration-dependent). Diagnose which one you're at.
2. **The navmesh is fully exonerated** by the debugger. Any future "fix the navmesh" idea for THIS
   wall is a dead end unless the debugger first shows a navmesh load FAILURE.
3. **Measure the working exemplar first.** The overworld (works) vs the cave (walls) diff is the
   whole game. We wasted 9 builds not doing this.
4. **Verify deployed bytes, but that's necessary-not-sufficient.** Every failed attempt was
   correctly deployed; "it's in the map" never meant "it works".
5. **Frida > static guessing** for behavior questions. Ground every struct offset with live
   `Instruction.parse` before trusting a sweep.
