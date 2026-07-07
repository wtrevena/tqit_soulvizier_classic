# AREA WIRING RECIPE - exactly what it took to make the blood cave work

> The definitive, ordered checklist distilled from the 17-attempt invisible-wall campaign
> (2026-07-03 .. 2026-07-06, solved in build17). **This is the template for wiring EVERY
> remaining SV area** (uberdungeon, bossarena, secret_place, ...). Failure history and
> mechanism proofs live in WALL_ATTEMPT_LEDGER.md; engine internals in MODDING_PLAYBOOK.md.
> Per-area generalization plan: SV_AREAS_CAMPAIGN_PLAN.md.

## Phase A - get the levels into the merged world correctly

1. **Append the area's SV-only levels** to the merged map's LEVELS index with their own
   GUIDs (svaera_plus_portals does this). Shared levels keep SVAERA's copy - anything SV
   added to a shared level is DROPPED and must be restored in Phase D.
2. **Relocate the cluster** with a GRID_SHIFT entry (svaera_plus_portals.GRID_SHIFT is the
   single source of truth; gen_bc_navmeshes imports it - never hardcode a second copy).
3. **Normalize footprints**: index entry dims = box dims (base-game invariant). A 2u
   footprint gap at a seam blocks the walk-link even with perfect navmeshes (proven).
   Zero overlaps, flush edges (check_seam_all-style gate).
4. **Entrance = an engine-native mechanism interfacing FIXED data**:
   - Blood cave: HiddenValley01's native GridEntrance cave mouth (0x14 record) + the
     reciprocal 0x06 descriptor, with the SV Random09A blob SWAPPED IN at the AE GUID's
     index slot (AE GUID KEPT so the native mouth resolves; blob adds the west tunnel).
   - The mouth needs: destination level resident + its navmeshOK flag set + the landing
     coords within 2u of the destination mesh (Phase B.5 protects this).
   - Do NOT invent quest-portal teleports (failed twice: coord desync, fragile dialog).

## Phase B - navmeshes (the core; every step below was REQUIRED)

The stock engine only parses `0x0b` (REC\x02 / RLTD dtTileCache) pathing sections; SV's
`0x0a` (PathEngine) sections are silently skipped = invisible walls. Editor baking is
unusable on this hardware; generation is offline pure Python (tok_parse -> gen_rec02 ->
fastlz -> rec02_format, driven by gen_bc_navmeshes).

1. **Real 0x0b per walkable level** from the pristine upstream SV 0x0a tok geometry
   (decompiled trees lost most 0x0a; ALWAYS read upstream). CS=CH=0.2, ERODE=2, 64x64
   tiles, exactly 3 tilesets, FastLZ level-1, GUID list in the container.
2. **Neighbor-aware rasterization**: each level's heightfield unions EVERY abutting
   level's tok geometry (translated by 0x0a-corner world delta), extending ~16u (PAD)
   past the shared boundary. A seam walks only when BOTH meshes cross it and interlock.
3. **Cross-tagging (the stitch mechanism, disasm-proven)**: per-cell area id = 1 + index
   into the mesh's GUID list of the level whose footprint box owns that cell. GUID list =
   [own] + footprint-abutting neighbors. EVERY GUID must resolve in the merged world
   (ProcessRLTD rejects the whole section otherwise) - remap SV->AE for replaced shared
   levels, hard-fail on anything unresolvable.
4. **Y-ALIGNMENT (the final root cause)**: adjacent SV levels' toks are anchored a
   CONSTANT 0 or +-2.56u apart in Y (split-floor artifact; engine climb = 1u, place
   tolerance = 2u). Measure each abutting pair's constant offset from the toks (stdev
   < 1.0 = constant; leave variable/real terrain alone), BFS-propagate INTEGER per-level
   corrections, apply RIGIDLY: shift the int32 container center Y; neighbor strips carry
   (shift[nbr] - shift[own]) via their raster dy. NEVER bend or ramp floors per-mesh
   (owner-wins + relax_gradient_down created a NEW cliff - reverted). Drop cells with
   h<0 (stacked-below neighbor garbage; heights pack uint16).
5. **ANCHORING (the build17 lesson)**: each connected component's BFS root (shift=0)
   MUST be the level that interfaces FIXED, non-regenerated data - the entrance level
   (native mouth landing coords / native neighbor mesh). Root preference: entrance level
   > OWN_GUID_OVERRIDE levels > smallest basename (deterministic). HARD ASSERT the
   entrance level's shift == 0. An arbitrary root shifted Random09A -3u and walled the
   cave ENTRANCE while every interior gate passed.
6. **Injection**: svaera_plus_portals step 7b injects donors pre-positioned VERBATIM
   (no transplant) and strips the dead 0x0a.

## Phase C - gates (ALL must pass BEFORE any deploy; no exceptions)

| Gate | Tool | Pass condition |
|------|------|----------------|
| Donor fresh + GUIDs resolve | gen-time asserts | regen exits 0, anchor shift==0 |
| Byte-exact in map | tools/verify_merged_bc_navmeshes.py | N/N donors byte-identical, 0x0a stripped |
| G2 entrance | tools/debug/entrance_landing_check.py --check-merged | landing within 2.0u of mesh, ON THE MERGED MAP |
| G3 corridor | tools/debug/engine_corridor_full.py | whole walk chain 100% reachable from the entrance level |
| G4 seams | tools/debug/seam_delta_check.py | all chain seams median dY <= 0.5u |
| Frontier | frontier-seams check | every UNREACHED room shares ZERO floor cells with the chain (door-gated by design), else it is a wall |

**The G2 lesson: the oracle must test the AREA'S INTERFACE TO THE OUTSIDE, not start
inside it.** G3 starting inside Random09A was blind to the broken entrance. Every new
area needs its own G2-equivalent (its entrance mechanism checked against its mesh).

## Phase D - content and quests

1. Port the area's questlines into Quests.arc (tools/qst_format.py, 89/89 round-trip).
2. **Restore merge-dropped entities on shared levels** (NPCs, triggers, shrines,
   merchants, atmosphere emitters): extract records + local coords from the SV upstream
   blob, re-inject via INJECT_SPECS (build_quest_files.py) -> inject_into_0x05_v11 -
   the LIVE step-7 path ONLY (the old generate_default_0x14 path corrupted a blob).
3. Verify the quest chain STATICALLY end-to-end: every Condition/Action record resolves;
   every placement-dependent condition (ConversationStart, EnterVolume) has a live entity
   in a REACHABLE level; watch for circular gating (a drop conditioned on a step that
   needs a dropped entity). Tags resolve in Text.arc (tools/validate_tags.py).
4. DB records for placed entities must exist in the built .arz (Editor-records rule:
   loose-source resolution does not apply at runtime - the compiled DB is what counts).

## Phase E - process (non-negotiable, from Will)

- **Commit + tag `buildNN-<name>` BEFORE every build Will tests**; deploy keeps a rolling
  backup (local/Levels_deployed_prev.arc). Deploy touches Levels.arc ONLY - never map.dat.
- Independent implement agent -> independent max-effort vet (scope + strays + regressions
  + upstream/downstream wiring) -> re-implement -> re-vet until clean.
- Arm the frida debugger (scratchpad frida_seamless3.py pattern) before every walk test -
  one capture distinguishes navmesh-load vs portal vs placement failures instantly.
- Will must FULLY RESTART TQ to load a new map (running game holds it in RAM).

## Known generalization work (per new area)

gen_bc_navmeshes.py is blood-cave-hardcoded today: BC_TOKEN='xbloodcave', Random09A
entrance anchoring, R09-specific OWN_GUID_OVERRIDE/blob-swap. Per area you must supply:
(1) cluster token/level list, (2) GRID_SHIFT entry, (3) the entrance-anchor level + its
native interface (mouth record or walk-in neighbor), (4) an entrance G2 gate for that
interface, (5) the area's quest/entity restoration list. See SV_AREAS_CAMPAIGN_PLAN.md.
